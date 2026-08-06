from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from .common import read_json, update_manifest, write_json


SCHEMA = "functionalmlds_evaluation_questions"
SCHEMA_VERSION = "1.0"
PROMPT_VERSION = "evaluation_questions_v1"
PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / f"{PROMPT_VERSION}.md"


def _case_prefix(case_id: str) -> str:
    return case_id.upper().replace("-", "_")


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _agent_by_id(agent_roles: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        str(agent.get("id") or "").strip(): dict(agent)
        for agent in agent_roles.get("agents") or []
        if isinstance(agent, Mapping) and str(agent.get("id") or "").strip()
    }


def _agent_name(agent: Mapping[str, Any], fallback: str) -> str:
    return _clean_text(agent.get("display_name")) or fallback


def _expected_block(
    *,
    agent_id: Optional[str],
    handoff: bool,
    handoff_to: Optional[str],
    resolution: str,
    rationale: str,
    candidate_agent_ids: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Keep evaluation-only labels separate from the user utterance."""

    return {
        "agent_id": agent_id,
        "handoff": handoff,
        "handoff_to": handoff_to,
        "resolution": resolution,
        "rationale": _clean_text(rationale),
        "candidate_agent_ids": list(candidate_agent_ids or []),
    }


def _topic_terms(
    agent: Mapping[str, Any],
    *,
    agent_id: str,
    limit: int = 4,
) -> List[str]:
    forbidden = {
        _clean_text(agent_id).casefold(),
        _agent_name(agent, agent_id).casefold(),
    }
    terms: List[str] = []
    for value in [
        *(agent.get("expertise") or []),
        *(agent.get("knowledge_tags") or []),
        *(agent.get("responsible_zone_ids") or []),
        *(agent.get("grounded_object_ids") or []),
    ]:
        term = _clean_text(value).replace("_", " ").replace("-", " ")
        if (
            term
            and term.casefold() not in forbidden
            and term.casefold() not in {item.casefold() for item in terms}
        ):
            terms.append(term)
        if len(terms) >= limit:
            break
    return terms


def _agent_reference_forms(agent_id: str, agent: Mapping[str, Any]) -> Set[str]:
    forms = {
        _clean_text(agent_id),
        _clean_text(agent_id).replace("_", " ").replace("-", " "),
        _agent_name(agent, agent_id),
    }
    return {" ".join(form.casefold().split()) for form in forms if len(form.strip()) >= 4}


def _contains_agent_reference(
    utterance: str,
    *,
    agent_id: str,
    agent: Mapping[str, Any],
) -> bool:
    normalized = " ".join(_clean_text(utterance).casefold().split())
    normalized_spaced = normalized.replace("_", " ").replace("-", " ")
    return any(
        form in normalized or form in normalized_spaced
        for form in _agent_reference_forms(agent_id, agent)
    )


def _first_agent_id(agent_by_id: Mapping[str, Any]) -> Optional[str]:
    return next(iter(agent_by_id), None)


def _zone_to_agents(agent_by_id: Mapping[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {}
    for agent_id, agent in agent_by_id.items():
        for zone_id in agent.get("responsible_zone_ids") or []:
            zone_id = str(zone_id or "").strip()
            if zone_id:
                result.setdefault(zone_id, []).append(agent_id)
    return result


def _handoff_pairs(handoff_matrix: Mapping[str, Any]) -> Set[Tuple[str, str]]:
    pairs: Set[Tuple[str, str]] = set()
    for handoff in handoff_matrix.get("handoffs") or []:
        if not isinstance(handoff, Mapping):
            continue
        source = str(handoff.get("source_agent_id") or "").strip()
        target = str(handoff.get("target_agent_id") or "").strip()
        if source and target:
            pairs.add((source, target))
    return pairs


def _question_id(case_id: str, kind: str, raw_id: str) -> str:
    safe = _clean_text(raw_id).upper().replace(" ", "_").replace("-", "_")
    return f"EQ-{_case_prefix(case_id)}-{kind}-{safe}"


def _zone_question(
    *,
    case_id: str,
    zone: Mapping[str, Any],
    active_agent_id: str,
    expected_agent_id: Optional[str],
) -> Dict[str, Any]:
    zone_id = str(zone.get("zone_id") or "").strip()
    zone_name = _clean_text(zone.get("name")) or zone_id
    purpose = _clean_text(zone.get("purpose"))
    object_ids = [str(obj_id) for obj_id in (zone.get("object_ids") or []) if str(obj_id).strip()]
    if purpose:
        text = f"What can I do in the {zone_name} area, and which objects there are relevant for {purpose.lower()}?"
    else:
        text = f"What can I do in the {zone_name} area, and which objects there are relevant?"
    return {
        "question_id": _question_id(case_id, "ZONE", zone_id),
        "case_id": case_id,
        "kind": "zone_grounding",
        "text": text,
        "utterance": text,
        "benchmark_class": "positive",
        "active_agent_id": active_agent_id,
        "expected_agent_id": expected_agent_id,
        "expected_handoff": False,
        "expected_handoff_to": None,
        "expected_zone_ids": [zone_id],
        "expected_object_ids": object_ids[:6],
        "source_agent_id": None,
        "target_agent_id": None,
        "handoff_condition": None,
        "handoff_reason": None,
        "expected": _expected_block(
            agent_id=expected_agent_id,
            handoff=False,
            handoff_to=None,
            resolution="answer",
            rationale=f"The active agent is responsible for zone {zone_id}.",
        ),
        "provenance": {
            "source": "scene_semantics.semantic_zones",
            "zone_id": zone_id,
            "object_ids": object_ids,
        },
    }


def _agent_question(*, case_id: str, agent_id: str, agent: Mapping[str, Any]) -> Dict[str, Any]:
    name = _agent_name(agent, agent_id)
    expertise = [_clean_text(item) for item in (agent.get("expertise") or []) if _clean_text(item)]
    zones = [str(zone_id) for zone_id in (agent.get("responsible_zone_ids") or []) if str(zone_id).strip()]
    objects = [str(obj_id) for obj_id in (agent.get("grounded_object_ids") or []) if str(obj_id).strip()]
    expertise_text = ", ".join(expertise[:3]) or "your assigned responsibilities"
    text = f"{name}, what are you responsible for in this room, especially regarding {expertise_text}?"
    return {
        "question_id": _question_id(case_id, "AGENT", agent_id),
        "case_id": case_id,
        "kind": "agent_responsibility",
        "text": text,
        "utterance": text,
        "benchmark_class": "positive",
        "active_agent_id": agent_id,
        "expected_agent_id": agent_id,
        "expected_handoff": False,
        "expected_handoff_to": None,
        "expected_zone_ids": zones,
        "expected_object_ids": objects[:8],
        "source_agent_id": None,
        "target_agent_id": None,
        "handoff_condition": None,
        "handoff_reason": None,
        "expected": _expected_block(
            agent_id=agent_id,
            handoff=False,
            handoff_to=None,
            resolution="answer",
            rationale="The question concerns the active agent's own modeled responsibility.",
        ),
        "provenance": {
            "source": "agent_roles.agents",
            "agent_id": agent_id,
            "knowledge_tags": agent.get("knowledge_tags") or [],
        },
    }


def _handoff_question(
    *,
    case_id: str,
    handoff: Mapping[str, Any],
    source_agent: Mapping[str, Any],
    target_agent: Mapping[str, Any],
) -> Dict[str, Any]:
    source = str(handoff.get("source_agent_id") or "").strip()
    target = str(handoff.get("target_agent_id") or "").strip()
    condition = _clean_text(handoff.get("condition"))
    reason = _clean_text(handoff.get("reason"))
    target_terms = _topic_terms(target_agent, agent_id=target, limit=4)
    topic = ", ".join(target_terms) or "a responsibility outside your assigned room area"
    text = (
        f"I have a question about {topic}. "
        "Please help directly or connect me to the appropriate room expert."
    )
    return {
        "question_id": _question_id(case_id, "HANDOFF", f"{source}_TO_{target}"),
        "case_id": case_id,
        "kind": "handoff_decision",
        "text": text,
        "utterance": text,
        "benchmark_class": "positive",
        "active_agent_id": source,
        "expected_agent_id": target,
        "expected_handoff": True,
        "expected_handoff_to": target,
        "expected_zone_ids": [str(zone_id) for zone_id in (target_agent.get("responsible_zone_ids") or []) if str(zone_id).strip()],
        "expected_object_ids": [str(obj_id) for obj_id in (target_agent.get("grounded_object_ids") or []) if str(obj_id).strip()][:8],
        "source_agent_id": source,
        "target_agent_id": target,
        "handoff_condition": condition,
        "handoff_reason": reason,
        "expected": _expected_block(
            agent_id=target,
            handoff=True,
            handoff_to=target,
            resolution="route",
            rationale=reason or condition,
            candidate_agent_ids=[target],
        ),
        "provenance": {
            "source": "handoff_matrix.handoffs",
            "source_agent_id": source,
            "target_agent_id": target,
        },
    }


def _handoff_negative_question(
    *,
    case_id: str,
    source_agent_id: str,
    source_agent: Mapping[str, Any],
) -> Dict[str, Any]:
    terms = _topic_terms(source_agent, agent_id=source_agent_id, limit=3)
    topic = ", ".join(terms) or "your own responsibilities in this room"
    text = f"What should a visitor know about {topic}?"
    return {
        "question_id": _question_id(case_id, "HANDOFF_NEGATIVE", source_agent_id),
        "case_id": case_id,
        "kind": "handoff_negative",
        "text": text,
        "utterance": text,
        "benchmark_class": "negative",
        "active_agent_id": source_agent_id,
        "expected_agent_id": source_agent_id,
        "expected_handoff": False,
        "expected_handoff_to": None,
        "expected_zone_ids": [
            str(zone_id)
            for zone_id in source_agent.get("responsible_zone_ids") or []
            if str(zone_id).strip()
        ],
        "expected_object_ids": [
            str(object_id)
            for object_id in source_agent.get("grounded_object_ids") or []
            if str(object_id).strip()
        ][:8],
        "source_agent_id": source_agent_id,
        "target_agent_id": None,
        "candidate_agent_ids": [],
        "handoff_condition": None,
        "handoff_reason": "The topic belongs to the active agent's modeled responsibility.",
        "expected_resolution": "answer",
        "expected": _expected_block(
            agent_id=source_agent_id,
            handoff=False,
            handoff_to=None,
            resolution="answer",
            rationale="The topic belongs to the active agent's modeled responsibility.",
        ),
        "provenance": {
            "source": "agent_roles.agents",
            "source_agent_id": source_agent_id,
            "benchmark_case": "negative_handoff",
        },
    }


def _handoff_ambiguous_question(
    *,
    case_id: str,
    source_agent_id: str,
    candidates: Sequence[Tuple[str, Mapping[str, Any]]],
) -> Dict[str, Any]:
    selected = list(candidates[:2])
    candidate_ids = [agent_id for agent_id, _ in selected]
    topics = [
        (_topic_terms(agent, agent_id=agent_id, limit=1) or ["that room area"])[0]
        for agent_id, agent in selected
    ]
    text = (
        f"My question combines {topics[0]} and {topics[1]}. "
        "Which aspect should I clarify before you decide who can help?"
    )
    return {
        "question_id": _question_id(
            case_id,
            "HANDOFF_AMBIGUOUS",
            f"{source_agent_id}_{'_'.join(candidate_ids)}",
        ),
        "case_id": case_id,
        "kind": "handoff_ambiguous",
        "text": text,
        "utterance": text,
        "benchmark_class": "ambiguous",
        "active_agent_id": source_agent_id,
        "expected_agent_id": source_agent_id,
        "expected_handoff": False,
        "expected_handoff_to": None,
        "expected_zone_ids": [],
        "expected_object_ids": [],
        "source_agent_id": source_agent_id,
        "target_agent_id": None,
        "candidate_agent_ids": candidate_ids,
        "handoff_condition": None,
        "handoff_reason": "Two declared targets are plausible; the system should clarify before routing.",
        "expected_resolution": "clarify",
        "expected": _expected_block(
            agent_id=source_agent_id,
            handoff=False,
            handoff_to=None,
            resolution="clarify",
            rationale="Two declared targets are plausible; the system should clarify before routing.",
            candidate_agent_ids=candidate_ids,
        ),
        "provenance": {
            "source": "handoff_matrix.handoffs",
            "source_agent_id": source_agent_id,
            "candidate_agent_ids": candidate_ids,
            "benchmark_case": "ambiguous_handoff",
        },
    }


def _handoff_unknown_question(*, case_id: str, active_agent_id: str) -> Dict[str, Any]:
    text = "What will tomorrow's exact closing price of the S&P 500 be?"
    return {
        "question_id": _question_id(case_id, "HANDOFF_UNKNOWN", active_agent_id),
        "case_id": case_id,
        "kind": "handoff_unknown",
        "text": text,
        "utterance": text,
        "benchmark_class": "unknown",
        "active_agent_id": active_agent_id,
        "expected_agent_id": active_agent_id,
        "expected_handoff": False,
        "expected_handoff_to": None,
        "expected_zone_ids": [],
        "expected_object_ids": [],
        "source_agent_id": active_agent_id,
        "target_agent_id": None,
        "candidate_agent_ids": [],
        "handoff_condition": None,
        "handoff_reason": "No modeled room agent can ground a future market-price prediction.",
        "expected_resolution": "abstain",
        "expected": _expected_block(
            agent_id=active_agent_id,
            handoff=False,
            handoff_to=None,
            resolution="abstain",
            rationale="No modeled room agent can ground a future market-price prediction.",
        ),
        "provenance": {
            "source": "deterministic_out_of_scope_probe",
            "source_agent_id": active_agent_id,
            "benchmark_case": "unknown_handoff",
        },
    }


def generate_deterministic_questions(
    *,
    case_id: str,
    scene_semantics: Dict[str, Any],
    agent_roles: Dict[str, Any],
    handoff_matrix: Dict[str, Any],
) -> Dict[str, Any]:
    agent_by_id = _agent_by_id(agent_roles)
    zone_to_agents = _zone_to_agents(agent_by_id)
    fallback_agent = _first_agent_id(agent_by_id)
    questions: List[Dict[str, Any]] = []

    for zone in scene_semantics.get("semantic_zones") or []:
        if not isinstance(zone, Mapping) or not str(zone.get("zone_id") or "").strip():
            continue
        zone_id = str(zone.get("zone_id") or "").strip()
        responsible_agents = zone_to_agents.get(zone_id) or []
        expected_agent_id = responsible_agents[0] if responsible_agents else fallback_agent
        if expected_agent_id:
            questions.append(
                _zone_question(
                    case_id=case_id,
                    zone=zone,
                    active_agent_id=expected_agent_id,
                    expected_agent_id=expected_agent_id,
                )
            )

    for agent_id, agent in agent_by_id.items():
        questions.append(_agent_question(case_id=case_id, agent_id=agent_id, agent=agent))

    for handoff in handoff_matrix.get("handoffs") or []:
        if not isinstance(handoff, Mapping):
            continue
        source = str(handoff.get("source_agent_id") or "").strip()
        target = str(handoff.get("target_agent_id") or "").strip()
        if source in agent_by_id and target in agent_by_id and source != target:
            questions.append(
                _handoff_question(
                    case_id=case_id,
                    handoff=handoff,
                    source_agent=agent_by_id[source],
                    target_agent=agent_by_id[target],
                )
            )

    for agent_id, agent in agent_by_id.items():
        questions.append(
            _handoff_negative_question(
                case_id=case_id,
                source_agent_id=agent_id,
                source_agent=agent,
            )
        )

    targets_by_source: Dict[str, List[str]] = {}
    for source, target in sorted(_handoff_pairs(handoff_matrix)):
        if source in agent_by_id and target in agent_by_id:
            targets_by_source.setdefault(source, []).append(target)
    for source, target_ids in targets_by_source.items():
        if len(target_ids) < 2:
            continue
        questions.append(
            _handoff_ambiguous_question(
                case_id=case_id,
                source_agent_id=source,
                candidates=[
                    (target_id, agent_by_id[target_id])
                    for target_id in target_ids[:2]
                ],
            )
        )

    if fallback_agent:
        questions.append(
            _handoff_unknown_question(
                case_id=case_id,
                active_agent_id=fallback_agent,
            )
        )

    validation = validate_evaluation_questions(
        {
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "case_id": case_id,
            "generation_mode": "deterministic",
            "prompt_version": None,
            "questions": questions,
        },
        scene_semantics=scene_semantics,
        agent_roles=agent_roles,
        handoff_matrix=handoff_matrix,
    )
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "generation_mode": "deterministic",
        "prompt_version": None,
        "status": validation["status"],
        "errors": validation["errors"],
        "warnings": validation["warnings"],
        "metrics": validation["metrics"],
        "questions": questions,
    }


def validate_evaluation_questions(
    payload: Mapping[str, Any],
    *,
    scene_semantics: Mapping[str, Any],
    agent_roles: Mapping[str, Any],
    handoff_matrix: Mapping[str, Any],
) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    questions = payload.get("questions") or []
    if not isinstance(questions, list):
        errors.append("questions must be a list.")
        questions = []

    case_id = str(payload.get("case_id") or "").strip()
    agent_ids = set(_agent_by_id(agent_roles))
    zone_ids = {
        str(zone.get("zone_id") or "").strip()
        for zone in scene_semantics.get("semantic_zones") or []
        if isinstance(zone, Mapping) and str(zone.get("zone_id") or "").strip()
    }
    handoff_pairs = _handoff_pairs(handoff_matrix)
    question_ids: Set[str] = set()
    kinds: Dict[str, int] = {}
    zone_question_zones: Set[str] = set()
    agent_question_agents: Set[str] = set()
    handoff_question_pairs: Set[Tuple[str, str]] = set()
    ambiguous_question_sources: Set[str] = set()

    for index, question in enumerate(questions):
        if not isinstance(question, Mapping):
            errors.append(f"questions[{index}] is not an object.")
            continue
        question_id = str(question.get("question_id") or "").strip()
        if not question_id:
            errors.append(f"questions[{index}].question_id is empty.")
        elif question_id in question_ids:
            errors.append(f"Duplicate question_id: {question_id}.")
        question_ids.add(question_id)

        if str(question.get("case_id") or "").strip() != case_id:
            errors.append(f"{question_id or index} has a case_id mismatch.")
        text = _clean_text(question.get("text"))
        utterance = _clean_text(question.get("utterance") or text)
        if not text:
            errors.append(f"{question_id or index} has empty text.")
        if not utterance:
            errors.append(f"{question_id or index} has empty utterance.")
        if question.get("utterance") is not None and utterance != text:
            errors.append(f"{question_id or index}.utterance must match legacy text.")

        kind = str(question.get("kind") or "").strip()
        kinds[kind] = kinds.get(kind, 0) + 1
        active_agent_id = str(question.get("active_agent_id") or "").strip()
        if active_agent_id not in agent_ids:
            errors.append(f"{question_id or index} references unknown active_agent_id: {active_agent_id}.")

        expected_handoff = question.get("expected_handoff")
        if not isinstance(expected_handoff, bool):
            errors.append(f"{question_id or index}.expected_handoff must be boolean.")
        expected_target = (
            str(question.get("expected_handoff_to")).strip()
            if question.get("expected_handoff_to") is not None
            else None
        )
        if expected_target is not None and expected_target not in agent_ids:
            errors.append(f"{question_id or index} references unknown expected_handoff_to: {expected_target}.")
        expected = question.get("expected")
        if expected is not None:
            if not isinstance(expected, Mapping):
                errors.append(f"{question_id or index}.expected must be an object.")
            else:
                if bool(expected.get("handoff")) != bool(expected_handoff):
                    errors.append(f"{question_id or index}.expected.handoff disagrees with legacy field.")
                if expected.get("handoff_to") != expected_target:
                    errors.append(f"{question_id or index}.expected.handoff_to disagrees with legacy field.")
                if expected.get("agent_id") != question.get("expected_agent_id"):
                    errors.append(f"{question_id or index}.expected.agent_id disagrees with legacy field.")
                if not _clean_text(expected.get("rationale")):
                    errors.append(f"{question_id or index}.expected.rationale is empty.")

        if kind == "zone_grounding":
            for zone_id in question.get("expected_zone_ids") or []:
                zone_id = str(zone_id)
                if zone_id not in zone_ids:
                    errors.append(f"{question_id} references unknown zone_id: {zone_id}.")
                zone_question_zones.add(zone_id)
            if expected_handoff:
                errors.append(f"{question_id} is a zone question but expects a handoff.")
        elif kind == "agent_responsibility":
            agent_question_agents.add(active_agent_id)
            if expected_handoff:
                errors.append(f"{question_id} is an agent-responsibility question but expects a handoff.")
        elif kind == "handoff_decision":
            source = str(question.get("source_agent_id") or "").strip()
            target = str(question.get("target_agent_id") or "").strip()
            pair = (source, target)
            handoff_question_pairs.add(pair)
            if pair not in handoff_pairs:
                errors.append(f"{question_id} references undeclared handoff pair: {source}->{target}.")
            if not expected_handoff:
                errors.append(f"{question_id} is a handoff question but expected_handoff is false.")
            if expected_target != target:
                errors.append(f"{question_id} expected_handoff_to does not match target_agent_id.")
            target_agent = _agent_by_id(agent_roles).get(target, {})
            if target_agent and _contains_agent_reference(
                utterance,
                agent_id=target,
                agent=target_agent,
            ):
                errors.append(
                    f"{question_id}.utterance leaks the expected target agent label or id."
                )
        elif kind == "handoff_negative":
            source = str(question.get("source_agent_id") or "").strip()
            if source != active_agent_id:
                errors.append(f"{question_id} source_agent_id must equal active_agent_id.")
            if expected_handoff or expected_target is not None:
                errors.append(f"{question_id} negative case must not expect a handoff.")
            if question.get("expected_agent_id") != active_agent_id:
                errors.append(f"{question_id} negative case must remain with the active agent.")
        elif kind == "handoff_ambiguous":
            source = str(question.get("source_agent_id") or "").strip()
            candidates = [
                str(item).strip()
                for item in question.get("candidate_agent_ids") or []
                if str(item).strip()
            ]
            ambiguous_question_sources.add(source)
            if source != active_agent_id:
                errors.append(f"{question_id} source_agent_id must equal active_agent_id.")
            if len(candidates) < 2 or len(candidates) != len(set(candidates)):
                errors.append(f"{question_id} requires at least two unique candidate_agent_ids.")
            for candidate in candidates:
                if (source, candidate) not in handoff_pairs:
                    errors.append(
                        f"{question_id} candidate is not a declared target: {source}->{candidate}."
                    )
                candidate_agent = _agent_by_id(agent_roles).get(candidate, {})
                if candidate_agent and _contains_agent_reference(
                    utterance,
                    agent_id=candidate,
                    agent=candidate_agent,
                ):
                    errors.append(
                        f"{question_id}.utterance leaks candidate agent label or id: {candidate}."
                    )
            if expected_handoff or expected_target is not None:
                errors.append(f"{question_id} ambiguous case must clarify before handoff.")
            if question.get("expected_resolution") != "clarify":
                errors.append(f"{question_id} ambiguous case must expect clarification.")
        elif kind == "handoff_unknown":
            if expected_handoff or expected_target is not None:
                errors.append(f"{question_id} unknown case must not expect a handoff.")
            if question.get("expected_resolution") != "abstain":
                errors.append(f"{question_id} unknown case must expect abstention.")
        else:
            errors.append(f"{question_id or index} has unknown kind: {kind}.")

    missing_zone_questions = sorted(zone_ids - zone_question_zones)
    missing_agent_questions = sorted(agent_ids - agent_question_agents)
    if missing_zone_questions:
        errors.append("Missing zone questions for: " + ", ".join(missing_zone_questions))
    if missing_agent_questions:
        errors.append("Missing agent responsibility questions for: " + ", ".join(missing_agent_questions))
    if handoff_pairs and not handoff_question_pairs:
        errors.append("At least one handoff_decision question is required.")
    if handoff_pairs and len(handoff_question_pairs) < len(handoff_pairs):
        warnings.append(
            f"Only {len(handoff_question_pairs)} of {len(handoff_pairs)} declared handoff pairs have direct test questions."
        )

    metrics = {
        "question_count": len(questions),
        "zone_question_count": kinds.get("zone_grounding", 0),
        "semantic_zone_count": len(zone_ids),
        "agent_responsibility_question_count": kinds.get("agent_responsibility", 0),
        "agent_count": len(agent_ids),
        "handoff_question_count": kinds.get("handoff_decision", 0),
        "handoff_negative_question_count": kinds.get("handoff_negative", 0),
        "handoff_ambiguous_question_count": kinds.get("handoff_ambiguous", 0),
        "handoff_unknown_question_count": kinds.get("handoff_unknown", 0),
        "declared_handoff_pair_count": len(handoff_pairs),
        "zone_question_coverage": round(len(zone_question_zones) / len(zone_ids), 6) if zone_ids else 1.0,
        "agent_question_coverage": round(len(agent_question_agents) / len(agent_ids), 6) if agent_ids else 1.0,
        "handoff_pair_question_coverage": round(len(handoff_question_pairs) / len(handoff_pairs), 6) if handoff_pairs else 1.0,
        "ambiguous_source_question_count": len(ambiguous_question_sources),
    }
    return {
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
    }


def run_evaluation_questions_for_case(case_dir: Path) -> Dict[str, Any]:
    case_dir = Path(case_dir).resolve()
    semantics_path = case_dir / "intermediate" / "scene_semantics.json"
    agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    handoff_path = case_dir / "intermediate" / "handoff_matrix.json"
    output_path = case_dir / "validation" / "evaluation_questions.json"

    scene_semantics = read_json(semantics_path)
    agent_roles = read_json(agent_roles_path)
    handoff_matrix = read_json(handoff_path)
    payload = generate_deterministic_questions(
        case_id=case_dir.name,
        scene_semantics=scene_semantics,
        agent_roles=agent_roles,
        handoff_matrix=handoff_matrix,
    )
    write_json(output_path, payload)
    update_manifest(
        case_dir,
        stage_id="evaluation_questions",
        status="success" if payload["status"] == "valid" else "failed",
        input_paths=[
            semantics_path,
            agent_roles_path,
            handoff_path,
            PROMPT_PATH,
            Path(__file__).resolve(),
        ],
        output_paths=[output_path],
        errors=payload["errors"],
        warnings=payload["warnings"],
        metadata=payload["metrics"],
    )
    return {
        "case_id": case_dir.name,
        "status": "success" if payload["status"] == "valid" else "failed",
        "validation": {
            "status": payload["status"],
            "errors": payload["errors"],
            "warnings": payload["warnings"],
            "metrics": payload["metrics"],
        },
        "questions_path": str(output_path),
    }


def run_evaluation_questions_for_cases(case_dirs: Iterable[Path]) -> List[Dict[str, Any]]:
    return [run_evaluation_questions_for_case(case_dir) for case_dir in case_dirs]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic evaluation questions.")
    parser.add_argument("--case-dir", type=Path, action="append")
    parser.add_argument("--case-root", type=Path)
    args = parser.parse_args(argv)
    case_dirs = args.case_dir or []
    if args.case_root:
        case_dirs.extend(sorted(path for path in args.case_root.iterdir() if path.is_dir()))
    if not case_dirs:
        parser.error("Pass --case-dir or --case-root.")
    results = run_evaluation_questions_for_cases(case_dirs)
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 0 if all(result["status"] == "success" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
