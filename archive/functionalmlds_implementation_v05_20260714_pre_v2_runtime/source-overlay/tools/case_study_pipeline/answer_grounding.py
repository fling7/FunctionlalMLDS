from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from .common import read_json, update_manifest, write_json


SCHEMA = "functionalmlds_answer_grounding_results"
SCHEMA_VERSION = "1.0"
PROMPT_VERSION = "answer_grounding_judge_v1"
CONFIG_DIR = Path(__file__).resolve().parent / "config"


STOPWORDS = {
    "about",
    "after",
    "alle",
    "all",
    "also",
    "and",
    "area",
    "auch",
    "auf",
    "aus",
    "bei",
    "can",
    "das",
    "dass",
    "dem",
    "den",
    "der",
    "des",
    "die",
    "dies",
    "diese",
    "dieser",
    "dir",
    "do",
    "dort",
    "du",
    "ein",
    "eine",
    "einem",
    "einen",
    "einer",
    "er",
    "for",
    "from",
    "gerne",
    "haben",
    "has",
    "hier",
    "ich",
    "im",
    "in",
    "ist",
    "it",
    "mit",
    "of",
    "oder",
    "on",
    "please",
    "relevant",
    "sie",
    "sind",
    "the",
    "there",
    "this",
    "und",
    "was",
    "what",
    "which",
    "you",
    "zur",
    "zum",
}


def _load_aliases() -> Dict[str, Set[str]]:
    path = CONFIG_DIR / "answer_grounding_aliases.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        return {}
    aliases: Dict[str, Set[str]] = {}
    for key, values in payload.items():
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
            continue
        aliases[str(key)] = {str(value) for value in values if str(value).strip()}
    return aliases


ALIASES = _load_aliases()


NEGATIVE_MARKERS = {
    "openai fehler",
    "backend fehler",
    "i do not know",
    "ich weiss nicht",
    "ich weiß nicht",
    "keine informationen",
}


def _normalize_text(text: Any) -> str:
    value = str(text or "").lower()
    value = value.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return value


def _tokens(text: Any) -> Set[str]:
    normalized = _normalize_text(text)
    raw_tokens = re.findall(r"[a-z0-9]+", normalized)
    result: Set[str] = set()
    for token in raw_tokens:
        if len(token) < 3 or token in STOPWORDS or token.isdigit():
            continue
        result.add(token)
        if token in ALIASES:
            result.update(_normalize_text(alias) for alias in ALIASES[token])
        for key, aliases in ALIASES.items():
            normalized_aliases = {_normalize_text(alias) for alias in aliases}
            if key in token or any(alias in token for alias in normalized_aliases):
                result.add(key)
                result.update(normalized_aliases)
    return result


def _tokens_from_values(values: Iterable[Any]) -> Set[str]:
    result: Set[str] = set()
    for value in values:
        if isinstance(value, Mapping):
            result.update(_tokens(json.dumps(value, ensure_ascii=False, sort_keys=True)))
        elif isinstance(value, (list, tuple, set)):
            result.update(_tokens_from_values(value))
        else:
            result.update(_tokens(value))
    return result


def _agent_by_id(agent_roles: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        str(agent.get("id") or "").strip(): dict(agent)
        for agent in agent_roles.get("agents") or []
        if isinstance(agent, Mapping) and str(agent.get("id") or "").strip()
    }


def _object_by_id(normalized_scene: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        str(obj.get("object_id") or "").strip(): dict(obj)
        for obj in normalized_scene.get("objects") or []
        if isinstance(obj, Mapping) and str(obj.get("object_id") or "").strip()
    }


def _zone_by_id(scene_semantics: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        str(zone.get("zone_id") or "").strip(): dict(zone)
        for zone in scene_semantics.get("semantic_zones") or []
        if isinstance(zone, Mapping) and str(zone.get("zone_id") or "").strip()
    }


def _knowledge_by_agent(knowledge: Mapping[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    result: Dict[str, List[Dict[str, Any]]] = {}
    for entry in knowledge.get("knowledge_entries") or []:
        if not isinstance(entry, Mapping):
            continue
        for agent_id in entry.get("intended_agents") or []:
            result.setdefault(str(agent_id), []).append(dict(entry))
    return result


def _full_answer(raw_responses: Mapping[str, Any], question_id: str, fallback: str) -> str:
    for response in raw_responses.get("responses") or []:
        if not isinstance(response, Mapping) or response.get("question_id") != question_id:
            continue
        events = ((response.get("response") or {}).get("events") or []) if isinstance(response.get("response"), Mapping) else []
        answer_parts = [
            str(event.get("text") or "").strip()
            for event in events
            if isinstance(event, Mapping) and event.get("type") == "say" and str(event.get("text") or "").strip()
        ]
        if answer_parts:
            return "\n".join(answer_parts)
    return fallback


def _agent_terms(agent_id: str, agent: Mapping[str, Any], knowledge_entries: Sequence[Mapping[str, Any]]) -> Set[str]:
    return _tokens_from_values(
        [
            agent_id,
            agent.get("display_name"),
            agent.get("persona"),
            agent.get("expertise") or [],
            agent.get("knowledge_tags") or [],
            agent.get("responsible_zone_ids") or [],
            agent.get("grounded_object_ids") or [],
            [entry.get("tag") for entry in knowledge_entries],
            [entry.get("name") for entry in knowledge_entries],
            [entry.get("text") for entry in knowledge_entries],
        ]
    )


def _context_terms(
    *,
    test: Mapping[str, Any],
    scene_semantics: Mapping[str, Any],
    normalized_scene: Mapping[str, Any],
) -> Set[str]:
    object_by_id = _object_by_id(normalized_scene)
    zone_by_id = _zone_by_id(scene_semantics)
    expected_zone_ids = [str(zone_id) for zone_id in test.get("expected_zone_ids") or []]
    expected_object_ids = [str(object_id) for object_id in test.get("expected_object_ids") or []]

    values: List[Any] = [
        scene_semantics.get("domain"),
        scene_semantics.get("room_purpose"),
        test.get("expected_zone_ids") or [],
        test.get("expected_object_ids") or [],
    ]
    values.extend(zone_by_id[zone_id] for zone_id in expected_zone_ids if zone_id in zone_by_id)
    values.extend(object_by_id[object_id] for object_id in expected_object_ids if object_id in object_by_id)
    return _tokens_from_values(values)


def _negative_markers(answer_text: str) -> List[str]:
    normalized = _normalize_text(answer_text)
    return [marker for marker in NEGATIVE_MARKERS if _normalize_text(marker) in normalized]


def _token_overlap(answer_tokens: Set[str], expected_tokens: Set[str]) -> List[str]:
    return sorted(answer_tokens & expected_tokens)


def compute_answer_grounding(
    *,
    case_id: str,
    chat_results: Dict[str, Any],
    raw_responses: Dict[str, Any],
    agent_roles: Dict[str, Any],
    scene_semantics: Dict[str, Any],
    normalized_scene: Dict[str, Any],
    knowledge: Dict[str, Any],
) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    agent_by_id = _agent_by_id(agent_roles)
    knowledge_by_agent = _knowledge_by_agent(knowledge)
    grounded_answers: List[Dict[str, Any]] = []

    for test in chat_results.get("chat_tests") or []:
        if not isinstance(test, Mapping):
            continue
        question_id = str(test.get("question_id") or "").strip()
        response_agent_id = str(test.get("observed_handoff_to") or test.get("response_active_agent_id") or test.get("active_agent_id") or "").strip()
        agent = agent_by_id.get(response_agent_id) or agent_by_id.get(str(test.get("active_agent_id") or "").strip()) or {}
        answer_text = _full_answer(raw_responses, question_id, str(test.get("answer_preview") or ""))
        answer_tokens = _tokens(answer_text)
        agent_tokens = _agent_terms(response_agent_id, agent, knowledge_by_agent.get(response_agent_id, []))
        context_tokens = _context_terms(test=test, scene_semantics=scene_semantics, normalized_scene=normalized_scene)
        agent_overlap = _token_overlap(answer_tokens, agent_tokens)
        context_overlap = _token_overlap(answer_tokens, context_tokens)
        negative = _negative_markers(answer_text)

        test_errors: List[str] = []
        if not test.get("success"):
            test_errors.append("Underlying chat test did not succeed.")
        if not answer_text.strip():
            test_errors.append("Answer text is empty.")
        if not response_agent_id or response_agent_id not in agent_by_id:
            test_errors.append(f"Response agent is unknown: {response_agent_id}.")
        if negative:
            test_errors.append("Answer contains negative/error markers: " + ", ".join(negative))
        if not agent_overlap:
            test_errors.append("Answer has no deterministic overlap with response agent knowledge tags, expertise or KB entries.")
        if not context_overlap:
            test_errors.append("Answer has no deterministic overlap with expected zone, object or project-context terms.")

        grounded_answers.append(
            {
                "question_id": question_id,
                "case_id": case_id,
                "kind": test.get("kind"),
                "active_agent_id": test.get("active_agent_id"),
                "response_agent_id": response_agent_id,
                "expected_handoff": bool(test.get("expected_handoff")),
                "observed_handoff": bool(test.get("observed_handoff")),
                "answer_char_count": len(answer_text),
                "agent_grounding_overlap_count": len(agent_overlap),
                "context_grounding_overlap_count": len(context_overlap),
                "agent_grounding_terms": agent_overlap[:20],
                "context_grounding_terms": context_overlap[:20],
                "negative_markers": negative,
                "grounded": not test_errors,
                "errors": test_errors,
            }
        )
        errors.extend(f"{question_id}: {error}" for error in test_errors)

    total = len(grounded_answers)
    grounded_count = sum(1 for item in grounded_answers if item["grounded"])
    metrics = {
        "answer_count": total,
        "grounded_answer_count": grounded_count,
        "ungrounded_answer_count": total - grounded_count,
        "grounded_answer_ratio": round(grounded_count / total, 6) if total else 0.0,
        "agent_grounding_coverage": round(
            sum(1 for item in grounded_answers if item["agent_grounding_overlap_count"] > 0) / total,
            6,
        )
        if total
        else 0.0,
        "context_grounding_coverage": round(
            sum(1 for item in grounded_answers if item["context_grounding_overlap_count"] > 0) / total,
            6,
        )
        if total
        else 0.0,
        "negative_marker_count": sum(1 for item in grounded_answers if item["negative_markers"]),
        "llm_judge_used": False,
    }
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
        "grounded_answers": grounded_answers,
    }


def run_answer_grounding_for_case(case_dir: Path) -> Dict[str, Any]:
    case_dir = Path(case_dir).resolve()
    chat_results_path = case_dir / "validation" / "chat_test_results.json"
    raw_responses_path = case_dir / "runtime_logs" / "chat_responses.json"
    agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    semantics_path = case_dir / "intermediate" / "scene_semantics.json"
    normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
    knowledge_path = case_dir / "intermediate" / "knowledge.generated.json"
    output_path = case_dir / "validation" / "answer_grounding_results.json"

    payload = compute_answer_grounding(
        case_id=case_dir.name,
        chat_results=read_json(chat_results_path),
        raw_responses=read_json(raw_responses_path),
        agent_roles=read_json(agent_roles_path),
        scene_semantics=read_json(semantics_path),
        normalized_scene=read_json(normalized_path),
        knowledge=read_json(knowledge_path),
    )
    write_json(output_path, payload)
    update_manifest(
        case_dir,
        stage_id="answer_grounding",
        status="success" if payload["status"] == "valid" else "failed",
        input_paths=[chat_results_path, raw_responses_path, agent_roles_path, semantics_path, normalized_path, knowledge_path],
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
        "validation_path": str(output_path),
    }


def run_answer_grounding_for_cases(case_dirs: Iterable[Path]) -> List[Dict[str, Any]]:
    return [run_answer_grounding_for_case(case_dir) for case_dir in case_dirs]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate deterministic grounding of chat answers.")
    parser.add_argument("--case-dir", type=Path, action="append")
    parser.add_argument("--case-root", type=Path)
    args = parser.parse_args(argv)
    case_dirs = args.case_dir or []
    if args.case_root:
        case_dirs.extend(sorted(path for path in args.case_root.iterdir() if path.is_dir()))
    if not case_dirs:
        parser.error("Pass --case-dir or --case-root.")
    results = run_answer_grounding_for_cases(case_dirs)
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 0 if all(result["status"] == "success" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
