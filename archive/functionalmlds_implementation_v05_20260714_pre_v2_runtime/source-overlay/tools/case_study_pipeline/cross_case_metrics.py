from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .common import read_json, write_json


SCHEMA = "functionalmlds_cross_case_metrics"
SCHEMA_VERSION = "1.0"


def _read_if_exists(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


def _round(value: Optional[float]) -> Optional[float]:
    return None if value is None else round(value, 6)


def _mean(values: Iterable[Optional[float]]) -> Optional[float]:
    cleaned = [float(value) for value in values if value is not None]
    if not cleaned:
        return None
    return sum(cleaned) / len(cleaned)


def _trace_metric(traceability_report: Mapping[str, Any], metric_id: str) -> Optional[Dict[str, Any]]:
    for item in traceability_report.get("traceability_metrics") or []:
        if isinstance(item, Mapping) and item.get("metric_id") == metric_id:
            return dict(item)
    return None


def _stage_error_summary(manifest: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}
    for entry in manifest.get("stages") or []:
        if not isinstance(entry, Mapping):
            continue
        stage_id = str(entry.get("stage_id") or "").strip()
        if not stage_id:
            continue
        errors = entry.get("errors") or []
        warnings = entry.get("warnings") or []
        metadata = entry.get("metadata") or {}
        attempts = metadata.get("attempts_used", 0) if isinstance(metadata, Mapping) else 0
        try:
            attempts = int(attempts or 0)
        except Exception:
            attempts = 0
        result[stage_id] = {
            "status": entry.get("status"),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "attempts_used": attempts,
        }
    return result


def _load_case_summary(case_dir: Path) -> Dict[str, Any]:
    semantics = _read_if_exists(case_dir / "intermediate" / "scene_semantics.json")
    manifest = _read_if_exists(case_dir / "stage_manifest.json")
    ingestion = _read_if_exists(case_dir / "validation" / "mlds_ingestion_validation.json")
    traceability = _read_if_exists(case_dir / "validation" / "traceability_metrics.json")
    handoff_metrics = _read_if_exists(case_dir / "validation" / "handoff_metrics.json")
    placement_metrics = _read_if_exists(case_dir / "validation" / "placement_metrics.json")
    answer_grounding = _read_if_exists(case_dir / "validation" / "answer_grounding_results.json")
    stage_completion = _read_if_exists(case_dir / "validation" / "stage_completion_report.json")
    evaluation_questions = _read_if_exists(case_dir / "validation" / "evaluation_questions.json")
    chat_tests = _read_if_exists(case_dir / "validation" / "chat_test_results.json")

    trace_avg = (traceability.get("metrics") or {}).get("average_coverage")
    object_group_metric = _trace_metric(traceability, "object_group_to_agent_role_grounding") or {}
    requirement_metric = _trace_metric(traceability, "requirement_to_validation_coverage") or {}
    runtime_action_metric = _trace_metric(traceability, "runtime_action_to_log_coverage") or {}

    return {
        "case_id": case_dir.name,
        "domain": semantics.get("domain") or "unknown",
        "room_purpose": semantics.get("room_purpose") or "",
        "object_count": (ingestion.get("metrics") or {}).get("object_count"),
        "semantic_zone_count": (semantics.get("metrics") or {}).get("semantic_zone_count")
        or len(semantics.get("semantic_zones") or []),
        "agent_count": (handoff_metrics.get("metrics") or {}).get("agent_count"),
        "question_count": (evaluation_questions.get("metrics") or {}).get("question_count"),
        "chat_success_count": (chat_tests.get("metrics") or {}).get("successful_chat_count"),
        "chat_count": (chat_tests.get("metrics") or {}).get("executed_chat_count"),
        "trace_average_coverage": trace_avg,
        "requirement_to_validation_coverage": requirement_metric.get("coverage"),
        "runtime_action_to_log_coverage": runtime_action_metric.get("coverage"),
        "object_group_coverage": object_group_metric.get("coverage"),
        "object_group_covered": object_group_metric.get("numerator"),
        "object_group_total": object_group_metric.get("denominator"),
        "handoff_accuracy": (handoff_metrics.get("metrics") or {}).get("handoff_decision_accuracy"),
        "handoff_decision_test_count": (handoff_metrics.get("metrics") or {}).get("decision_test_count"),
        "answer_grounding_ratio": (answer_grounding.get("metrics") or {}).get("grounded_answer_ratio"),
        "stage_completion_ratio": (stage_completion.get("metrics") or {}).get("completion_ratio"),
        "stage_errors": _stage_error_summary(manifest),
    }


def _aggregate_stage_errors(case_summaries: List[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    aggregate: Dict[str, Dict[str, Any]] = {}
    for summary in case_summaries:
        for stage_id, values in (summary.get("stage_errors") or {}).items():
            entry = aggregate.setdefault(
                stage_id,
                {
                    "case_count": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "warning_count": 0,
                    "repair_attempt_count": 0,
                },
            )
            entry["case_count"] += 1
            if values.get("status") == "success":
                entry["success_count"] += 1
            entry["error_count"] += int(values.get("error_count") or 0)
            entry["warning_count"] += int(values.get("warning_count") or 0)
            entry["repair_attempt_count"] += int(values.get("attempts_used") or 0)
    return dict(sorted(aggregate.items()))


def compute_cross_case_metrics(out_root: Path) -> Dict[str, Any]:
    out_root = Path(out_root).resolve()
    case_dirs = sorted(path for path in out_root.iterdir() if path.is_dir() and (path / "stage_manifest.json").exists())
    case_summaries = [_load_case_summary(case_dir) for case_dir in case_dirs]

    handoff_accuracy_by_domain = {
        str(summary["domain"]): summary.get("handoff_accuracy") for summary in case_summaries
    }
    object_group_coverage_by_domain = {
        str(summary["domain"]): {
            "coverage": summary.get("object_group_coverage"),
            "covered": summary.get("object_group_covered"),
            "total": summary.get("object_group_total"),
        }
        for summary in case_summaries
    }
    metrics = {
        "case_count": len(case_summaries),
        "average_trace_coverage": _round(_mean(summary.get("trace_average_coverage") for summary in case_summaries)),
        "average_requirement_to_validation_coverage": _round(
            _mean(summary.get("requirement_to_validation_coverage") for summary in case_summaries)
        ),
        "average_runtime_action_to_log_coverage": _round(
            _mean(summary.get("runtime_action_to_log_coverage") for summary in case_summaries)
        ),
        "average_handoff_accuracy": _round(_mean(summary.get("handoff_accuracy") for summary in case_summaries)),
        "average_object_group_coverage": _round(_mean(summary.get("object_group_coverage") for summary in case_summaries)),
        "average_answer_grounding_ratio": _round(_mean(summary.get("answer_grounding_ratio") for summary in case_summaries)),
        "average_stage_completion_ratio": _round(_mean(summary.get("stage_completion_ratio") for summary in case_summaries)),
        "total_chat_tests": sum(int(summary.get("chat_count") or 0) for summary in case_summaries),
        "successful_chat_tests": sum(int(summary.get("chat_success_count") or 0) for summary in case_summaries),
        "total_handoff_decision_tests": sum(int(summary.get("handoff_decision_test_count") or 0) for summary in case_summaries),
    }
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "valid",
        "errors": [],
        "warnings": [],
        "metrics": metrics,
        "case_summaries": case_summaries,
        "stage_error_summary": _aggregate_stage_errors(case_summaries),
        "handoff_accuracy_by_domain": handoff_accuracy_by_domain,
        "object_group_coverage_by_domain": object_group_coverage_by_domain,
    }


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def render_cross_case_markdown(report: Mapping[str, Any]) -> str:
    metrics = report.get("metrics") or {}
    lines = [
        "# FunctionalMLDS Case Study Aggregate Report",
        "",
        "## Overview",
        "",
        f"- Cases: {_fmt(metrics.get('case_count'))}",
        f"- Average trace coverage: {_fmt(metrics.get('average_trace_coverage'))}",
        f"- Average handoff accuracy: {_fmt(metrics.get('average_handoff_accuracy'))}",
        f"- Average object-group coverage: {_fmt(metrics.get('average_object_group_coverage'))}",
        f"- Average answer-grounding ratio: {_fmt(metrics.get('average_answer_grounding_ratio'))}",
        f"- Stage-completion ratio: {_fmt(metrics.get('average_stage_completion_ratio'))}",
        f"- Chat tests: {_fmt(metrics.get('successful_chat_tests'))}/{_fmt(metrics.get('total_chat_tests'))}",
        f"- Handoff decision tests: {_fmt(metrics.get('total_handoff_decision_tests'))}",
        "",
        "## Per-Case Metrics",
        "",
        "| Case | Domain | Trace avg. | Runtime log cov. | Handoff acc. | Object-group cov. | Grounding | Completion |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in report.get("case_summaries") or []:
        lines.append(
            "| {case_id} | {domain} | {trace} | {runtime} | {handoff} | {object_group} | {grounding} | {completion} |".format(
                case_id=summary.get("case_id"),
                domain=summary.get("domain"),
                trace=_fmt(summary.get("trace_average_coverage")),
                runtime=_fmt(summary.get("runtime_action_to_log_coverage")),
                handoff=_fmt(summary.get("handoff_accuracy")),
                object_group=_fmt(summary.get("object_group_coverage")),
                grounding=_fmt(summary.get("answer_grounding_ratio")),
                completion=_fmt(summary.get("stage_completion_ratio")),
            )
        )
    lines.extend(
        [
            "",
            "## Stage Errors And Repair Attempts",
            "",
            "| Stage | Cases | Success | Errors | Warnings | Repair attempts |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for stage_id, summary in (report.get("stage_error_summary") or {}).items():
        lines.append(
            "| {stage} | {cases} | {success} | {errors} | {warnings} | {attempts} |".format(
                stage=stage_id,
                cases=_fmt(summary.get("case_count")),
                success=_fmt(summary.get("success_count")),
                errors=_fmt(summary.get("error_count")),
                warnings=_fmt(summary.get("warning_count")),
                attempts=_fmt(summary.get("repair_attempt_count")),
            )
        )
    lines.extend(
        [
            "",
            "## Domain Metrics",
            "",
            "| Domain | Handoff accuracy | Object-group coverage |",
            "|---|---:|---:|",
        ]
    )
    object_groups = report.get("object_group_coverage_by_domain") or {}
    for domain, handoff_accuracy in (report.get("handoff_accuracy_by_domain") or {}).items():
        object_group = object_groups.get(domain) or {}
        lines.append(
            f"| {domain} | {_fmt(handoff_accuracy)} | {_fmt(object_group.get('coverage'))} ({_fmt(object_group.get('covered'))}/{_fmt(object_group.get('total'))}) |"
        )
    lines.append("")
    return "\n".join(lines)


def run_cross_case_metrics(out_root: Path) -> Dict[str, Any]:
    out_root = Path(out_root).resolve()
    report = compute_cross_case_metrics(out_root)
    aggregate_path = out_root / "aggregate_report.json"
    aggregate = _read_if_exists(aggregate_path)
    aggregate["stage"] = "cross_case_metrics"
    aggregate["success_count"] = report["metrics"]["case_count"] if report["status"] == "valid" else 0
    aggregate["failure_count"] = 0 if report["status"] == "valid" else report["metrics"]["case_count"]
    aggregate["case_count"] = report["metrics"]["case_count"]
    aggregate["cross_case_metrics"] = report
    write_json(aggregate_path, aggregate)
    markdown_path = out_root / "aggregate_report.md"
    markdown_path.write_text(render_cross_case_markdown(report), encoding="utf-8")
    return {
        "status": "success" if report["status"] == "valid" else "failed",
        "validation": {
            "status": report["status"],
            "errors": report["errors"],
            "warnings": report["warnings"],
            "metrics": report["metrics"],
        },
        "aggregate_json_path": str(aggregate_path),
        "aggregate_markdown_path": str(markdown_path),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compute cross-case metrics for FunctionalMLDS case studies.")
    parser.add_argument("--out-root", type=Path, default=Path("output/case_studies"))
    args = parser.parse_args(argv)
    result = run_cross_case_metrics(args.out_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
