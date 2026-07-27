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
    target_name = _agent_name(target_agent, target)
    text = (
        f"I am asking you, but my topic is this: {condition}. "
        f"Please connect me to the right expert if {target_name} should handle it."
    )
    return {
        "question_id": _question_id(case_id, "HANDOFF", f"{source}_TO_{target}"),
        "case_id": case_id,
        "kind": "handoff_decision",
        "text": text,
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
        "provenance": {
            "source": "handoff_matrix.handoffs",
            "source_agent_id": source,
            "target_agent_id": target,
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
        if not _clean_text(question.get("text")):
            errors.append(f"{question_id or index} has empty text.")

        kind = str(question.get("kind") or "").strip()
        kinds[kind] = kinds.get(kind, 0) + 1
        active_agent_id = str(question.get("active_agent_id") or "").strip()
        if active_agent_id not in agent_ids:
            errors.append(f"{question_id or index} references unknown active_agent_id: {active_agent_id}.")

        expected_handoff = question.get("expected_handoff")
        if not isinstance(expected_handoff, bool):
            errors.append(f"{question_id or index}.expected_handoff must be boolean.")
        expected_target = question.get("expected_handoff_to")
        if expected_target is not None and str(expected_target) not in agent_ids:
            errors.append(f"{question_id or index} references unknown expected_handoff_to: {expected_target}.")

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
        "declared_handoff_pair_count": len(handoff_pairs),
        "zone_question_coverage": round(len(zone_question_zones) / len(zone_ids), 6) if zone_ids else 1.0,
        "agent_question_coverage": round(len(agent_question_agents) / len(agent_ids), 6) if agent_ids else 1.0,
        "handoff_pair_question_coverage": round(len(handoff_question_pairs) / len(handoff_pairs), 6) if handoff_pairs else 1.0,
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
        input_paths=[semantics_path, agent_roles_path, handoff_path],
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
