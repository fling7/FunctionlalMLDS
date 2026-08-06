from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple

from .common import read_json, update_manifest, write_json


SCHEMA = "functionalmlds_handoff_test_results"
SCHEMA_VERSION = "1.0"
Pair = Tuple[str, str]
POSITIVE_KIND = "handoff_decision"
SAFEGUARD_KINDS = {
    "handoff_negative",
    "handoff_ambiguous",
    "handoff_unknown",
}
HANDOFF_BENCHMARK_KINDS = {POSITIVE_KIND, *SAFEGUARD_KINDS}


def _handoff_pairs(handoff_matrix: Mapping[str, Any]) -> Set[Pair]:
    pairs: Set[Pair] = set()
    for handoff in handoff_matrix.get("handoffs") or []:
        if not isinstance(handoff, Mapping):
            continue
        source = str(handoff.get("source_agent_id") or "").strip()
        target = str(handoff.get("target_agent_id") or "").strip()
        if source and target:
            pairs.add((source, target))
    return pairs


def _round(value: Optional[float]) -> Optional[float]:
    return None if value is None else round(value, 6)


def _handoff_chat_tests(chat_results: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [
        dict(item)
        for item in chat_results.get("chat_tests") or []
        if isinstance(item, Mapping) and item.get("kind") in HANDOFF_BENCHMARK_KINDS
    ]


def compute_handoff_test_results(
    *,
    case_id: str,
    chat_results: Dict[str, Any],
    handoff_matrix: Dict[str, Any],
) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    declared_pairs = _handoff_pairs(handoff_matrix)
    handoff_tests = _handoff_chat_tests(chat_results)
    observed_pairs: Set[Pair] = set()
    passed = 0
    evaluated_tests: List[Dict[str, Any]] = []

    if not any(test.get("kind") == POSITIVE_KIND for test in handoff_tests):
        errors.append("No handoff_decision chat tests found.")

    for test in handoff_tests:
        question_id = str(test.get("question_id") or "").strip()
        source = str(test.get("active_agent_id") or "").strip()
        expected_target = str(test.get("expected_handoff_to") or "").strip()
        observed_target = str(test.get("observed_handoff_to") or "").strip()
        expected_pair = (source, expected_target)
        observed_pair = (source, observed_target)
        test_errors: List[str] = []
        kind = str(test.get("kind") or "")

        if not test.get("success"):
            test_errors.append("Underlying chat test did not succeed.")
        if kind == POSITIVE_KIND:
            if expected_pair not in declared_pairs:
                test_errors.append(
                    "Expected handoff pair is not declared in handoff_matrix: "
                    f"{source}->{expected_target}."
                )
            if not test.get("expected_handoff"):
                test_errors.append(
                    "Test is marked as handoff_decision but expected_handoff is false."
                )
            if not test.get("observed_handoff"):
                test_errors.append("Expected a handoff, but none was observed.")
            if observed_target != expected_target:
                test_errors.append(
                    "Observed handoff target mismatch: "
                    f"expected {expected_target}, got {observed_target}."
                )
            if observed_pair not in declared_pairs:
                test_errors.append(
                    "Observed handoff pair is not declared in handoff_matrix: "
                    f"{source}->{observed_target}."
                )
            if str(test.get("response_active_agent_id") or "").strip() != expected_target:
                test_errors.append(
                    "response_active_agent_id does not match expected handoff target: "
                    f"{test.get('response_active_agent_id')} != {expected_target}."
                )
            if int(test.get("say_event_count") or 0) < 2:
                test_errors.append(
                    "Handoff response should contain at least two say events: "
                    "source handoff plus target answer."
                )
        else:
            if test.get("expected_handoff") or expected_target:
                test_errors.append(
                    f"{kind} safety probe must not declare an expected handoff."
                )
            if test.get("observed_handoff") or observed_target:
                test_errors.append(
                    f"{kind} safety probe triggered an unintended handoff to "
                    f"{observed_target or '<unspecified>'}."
                )
            if str(test.get("response_active_agent_id") or "").strip() != source:
                test_errors.append(
                    f"{kind} safety probe changed active agent instead of retaining {source}."
                )
            if int(test.get("say_event_count") or 0) < 1:
                test_errors.append(f"{kind} safety probe produced no answer event.")
            required_resolution = {
                "handoff_negative": "answer",
                "handoff_ambiguous": "clarify",
                "handoff_unknown": "abstain",
            }.get(kind)
            if test.get("expected_resolution") != required_resolution:
                test_errors.append(
                    f"{kind} must declare expected_resolution={required_resolution!r}."
                )

        if not test_errors:
            passed += 1
            if kind == POSITIVE_KIND:
                observed_pairs.add(observed_pair)
        evaluated_tests.append(
            {
                "question_id": question_id,
                "case_id": case_id,
                "source_agent_id": source,
                "kind": kind,
                "benchmark_class": test.get("benchmark_class"),
                "target_agent_id": expected_target or None,
                "expected_handoff": bool(test.get("expected_handoff")),
                "expected_handoff_to": expected_target,
                "observed_handoff": bool(test.get("observed_handoff")),
                "observed_handoff_to": observed_target or None,
                "response_active_agent_id": test.get("response_active_agent_id"),
                "say_event_count": test.get("say_event_count"),
                "answer_char_count": test.get("answer_char_count"),
                "expected_resolution": test.get("expected_resolution"),
                "candidate_agent_ids": test.get("candidate_agent_ids") or [],
                "semantic_resolution_assessed": False,
                "correct": not test_errors,
                "errors": test_errors,
            }
        )
        errors.extend(f"{question_id}: {error}" for error in test_errors)

    positive_tests = [
        item for item in evaluated_tests if item["kind"] == POSITIVE_KIND
    ]
    safeguard_tests = [
        item for item in evaluated_tests if item["kind"] in SAFEGUARD_KINDS
    ]
    missing_declared_pairs = sorted(
        declared_pairs
        - {
            (item["source_agent_id"], item["target_agent_id"])
            for item in positive_tests
        }
    )
    if missing_declared_pairs:
        errors.append(
            "Declared handoff pairs without direct handoff test: "
            + ", ".join(f"{source}->{target}" for source, target in missing_declared_pairs)
        )

    total = len(handoff_tests)
    positive_passed = sum(1 for item in positive_tests if item["correct"])
    safeguard_passed = sum(1 for item in safeguard_tests if item["correct"])
    if safeguard_tests:
        warnings.append(
            "Ambiguous/unknown answer semantics are not judged automatically; "
            "safety probes verify transport success, no unintended handoff, and "
            "active-agent retention only."
        )
    metrics = {
        "declared_handoff_pair_count": len(declared_pairs),
        "handoff_test_count": total,
        "passed_handoff_test_count": passed,
        "failed_handoff_test_count": total - passed,
        "handoff_test_success_rate": _round(passed / total) if total else 0.0,
        "positive_handoff_test_count": len(positive_tests),
        "positive_handoff_success_rate": _round(
            positive_passed / len(positive_tests)
        )
        if positive_tests
        else 0.0,
        "handoff_safeguard_test_count": len(safeguard_tests),
        "handoff_safeguard_routing_success_rate": _round(
            safeguard_passed / len(safeguard_tests)
        )
        if safeguard_tests
        else None,
        "semantic_resolution_assessed": False,
        "declared_pair_test_coverage": _round((len(declared_pairs) - len(missing_declared_pairs)) / len(declared_pairs))
        if declared_pairs
        else 1.0,
        "observed_declared_pair_count": len(observed_pairs),
        "observed_pair_coverage": _round(len(observed_pairs) / len(declared_pairs)) if declared_pairs else 1.0,
    }
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
        "handoff_tests": evaluated_tests,
    }


def run_handoff_tests_for_case(case_dir: Path) -> Dict[str, Any]:
    case_dir = Path(case_dir).resolve()
    chat_results_path = case_dir / "validation" / "chat_test_results.json"
    handoff_matrix_path = case_dir / "intermediate" / "handoff_matrix.json"
    output_path = case_dir / "validation" / "handoff_test_results.json"

    payload = compute_handoff_test_results(
        case_id=case_dir.name,
        chat_results=read_json(chat_results_path),
        handoff_matrix=read_json(handoff_matrix_path),
    )
    write_json(output_path, payload)
    update_manifest(
        case_dir,
        stage_id="handoff_tests",
        status="success" if payload["status"] == "valid" else "failed",
        input_paths=[chat_results_path, handoff_matrix_path],
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


def run_handoff_tests_for_cases(case_dirs: Iterable[Path]) -> List[Dict[str, Any]]:
    return [run_handoff_tests_for_case(case_dir) for case_dir in case_dirs]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate observed handoffs against the handoff matrix.")
    parser.add_argument("--case-dir", type=Path, action="append")
    parser.add_argument("--case-root", type=Path)
    args = parser.parse_args(argv)
    case_dirs = args.case_dir or []
    if args.case_root:
        case_dirs.extend(sorted(path for path in args.case_root.iterdir() if path.is_dir()))
    if not case_dirs:
        parser.error("Pass --case-dir or --case-root.")
    results = run_handoff_tests_for_cases(case_dirs)
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 0 if all(result["status"] == "success" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
