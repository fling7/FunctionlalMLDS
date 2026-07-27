from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Set

from .common import read_json, write_json


SCHEMA = "functionalmlds_generalizability_assessment"
SCHEMA_VERSION = "1.0"
PACKAGE_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = PACKAGE_ROOT / "config"
DOMAIN_SCAN_STOPWORDS = {
    "area",
    "agents",
    "assets",
    "case",
    "event",
    "fair",
    "floor",
    "input",
    "interactive",
    "interactivagents",
    "json",
    "mlds",
    "room",
    "scripting",
    "stand",
    "trade",
    "visitor",
    "with",
}


def _round(value: float) -> float:
    return round(float(value), 6)


def _split_terms(value: Any) -> Set[str]:
    terms: Set[str] = set()
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", str(value or ""))
    text = re.sub(r"[_/\\.-]+", " ", text)
    for token in re.findall(r"[A-Za-z][A-Za-z0-9]{3,}", text):
        normalized = token.lower().strip("_-")
        if normalized and normalized not in DOMAIN_SCAN_STOPWORDS:
            terms.add(normalized)
    return terms


def _load_configured_domain_terms() -> Set[str]:
    terms: Set[str] = set()
    for path in (
        CONFIG_DIR / "case_aliases.json",
        CONFIG_DIR / "default_inputs.json",
    ):
        if not path.exists():
            continue
        payload = read_json(path)
        terms.update(_split_terms(payload))
    return terms


def _terms_from_cases(case_summaries: Sequence[Mapping[str, Any]]) -> Set[str]:
    terms: Set[str] = set()
    for summary in case_summaries:
        terms.update(_split_terms(summary.get("case_id")))
        terms.update(_split_terms(summary.get("domain")))
        terms.update(_split_terms(summary.get("room_purpose")))
    return terms


def _scan_python_code(terms: Iterable[str]) -> Dict[str, Any]:
    term_set = {term.lower() for term in terms if len(term) >= 4}
    findings: List[Dict[str, Any]] = []
    for path in sorted(PACKAGE_ROOT.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        matched = sorted(term for term in term_set if re.search(rf"\b{re.escape(term)}\b", lowered))
        if matched:
            findings.append(
                {
                    "path": str(path),
                    "matched_terms": matched,
                }
            )
    return {
        "status": "clean" if not findings else "contains_configured_domain_terms",
        "scanned_file_count": len([path for path in PACKAGE_ROOT.rglob("*.py") if "__pycache__" not in path.parts]),
        "finding_count": len(findings),
        "findings": findings,
    }


def _stage_sets(case_summaries: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    per_case = {
        str(summary.get("case_id")): sorted((summary.get("stage_errors") or {}).keys()) for summary in case_summaries
    }
    unique_stage_sets = {tuple(stages) for stages in per_case.values()}
    return {
        "same_stage_set_for_all_cases": len(unique_stage_sets) <= 1,
        "per_case_stage_count": {case_id: len(stages) for case_id, stages in per_case.items()},
        "stage_ids": next(iter(unique_stage_sets), ()),
    }


def assess_generalizability(out_root: Path) -> Dict[str, Any]:
    out_root = Path(out_root).resolve()
    aggregate_path = out_root / "aggregate_report.json"
    aggregate = read_json(aggregate_path)
    cross_case_metrics = aggregate.get("cross_case_metrics") or {}
    metrics = cross_case_metrics.get("metrics") or {}
    case_summaries = cross_case_metrics.get("case_summaries") or []
    domains = sorted({str(summary.get("domain") or "unknown") for summary in case_summaries})
    stage_assessment = _stage_sets(case_summaries)
    domain_terms = _load_configured_domain_terms() | _terms_from_cases(case_summaries)
    code_scan = _scan_python_code(domain_terms)

    checks = [
        {
            "check_id": "multi_domain_corpus",
            "passed": len(case_summaries) >= 3 and len(domains) >= 3,
            "evidence": {
                "case_count": len(case_summaries),
                "domain_count": len(domains),
                "domains": domains,
            },
        },
        {
            "check_id": "same_pipeline_stages",
            "passed": bool(stage_assessment["same_stage_set_for_all_cases"]),
            "evidence": stage_assessment,
        },
        {
            "check_id": "no_failed_cases",
            "passed": int(aggregate.get("failure_count") or 0) == 0,
            "evidence": {
                "success_count": aggregate.get("success_count"),
                "failure_count": aggregate.get("failure_count"),
            },
        },
        {
            "check_id": "domain_terms_externalized",
            "passed": code_scan["finding_count"] == 0,
            "evidence": code_scan,
        },
        {
            "check_id": "runtime_behavior_cross_domain",
            "passed": metrics.get("average_handoff_accuracy") == 1.0
            and metrics.get("average_answer_grounding_ratio") == 1.0,
            "evidence": {
                "average_handoff_accuracy": metrics.get("average_handoff_accuracy"),
                "average_answer_grounding_ratio": metrics.get("average_answer_grounding_ratio"),
                "successful_chat_tests": metrics.get("successful_chat_tests"),
                "total_chat_tests": metrics.get("total_chat_tests"),
            },
        },
    ]
    passed_count = sum(1 for check in checks if check["passed"])
    errors = [
        f"{check['check_id']} failed."
        for check in checks
        if not check["passed"]
    ]
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": [],
        "metrics": {
            "check_count": len(checks),
            "passed_check_count": passed_count,
            "generalizability_score": _round(passed_count / len(checks)) if checks else 0.0,
            "case_count": len(case_summaries),
            "domain_count": len(domains),
        },
        "checks": checks,
    }


def render_generalizability_markdown(report: Mapping[str, Any]) -> str:
    metrics = report.get("metrics") or {}
    lines = [
        "# FunctionalMLDS Generalizability Assessment",
        "",
        "## Ergebnis",
        "",
        f"- Status: {report.get('status')}",
        f"- Checks: {metrics.get('passed_check_count')}/{metrics.get('check_count')}",
        f"- Score: {metrics.get('generalizability_score')}",
        f"- Cases: {metrics.get('case_count')}",
        f"- Domaenen: {metrics.get('domain_count')}",
        "",
        "## Checks",
        "",
        "| Check | Result | Evidence |",
        "|---|---:|---|",
    ]
    for check in report.get("checks") or []:
        evidence = check.get("evidence") or {}
        if check.get("check_id") == "domain_terms_externalized":
            code_scan = evidence
            evidence_text = (
                f"{code_scan.get('scanned_file_count')} Python files scanned, "
                f"{code_scan.get('finding_count')} findings"
            )
        elif check.get("check_id") == "multi_domain_corpus":
            evidence_text = f"{evidence.get('case_count')} cases, {evidence.get('domain_count')} domains"
        elif check.get("check_id") == "runtime_behavior_cross_domain":
            evidence_text = (
                f"handoff={evidence.get('average_handoff_accuracy')}, "
                f"grounding={evidence.get('average_answer_grounding_ratio')}, "
                f"chat={evidence.get('successful_chat_tests')}/{evidence.get('total_chat_tests')}"
            )
        elif check.get("check_id") == "same_pipeline_stages":
            evidence_text = f"same stages={evidence.get('same_stage_set_for_all_cases')}"
        else:
            evidence_text = f"success={evidence.get('success_count')}, failure={evidence.get('failure_count')}"
        lines.append(f"| {check.get('check_id')} | {check.get('passed')} | {evidence_text} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Die Pipeline kann als domaenenuebergreifend anwendbar bewertet werden, wenn dieselben Stufen fuer alle "
            "Cases erfolgreich laufen, die Domaenenbegriffe ausserhalb des Python-Codes liegen und die Runtime-Checks "
            "ueber alle Domaenen hinweg erfolgreich bleiben.",
            "",
        ]
    )
    return "\n".join(lines)


def run_generalizability_assessment(out_root: Path) -> Dict[str, Any]:
    report = assess_generalizability(out_root)
    out_root = Path(out_root).resolve()
    write_json(out_root / "generalizability_assessment.json", report)
    (out_root / "generalizability_assessment.md").write_text(
        render_generalizability_markdown(report),
        encoding="utf-8",
    )
    aggregate_path = out_root / "aggregate_report.json"
    if aggregate_path.exists():
        aggregate = read_json(aggregate_path)
        aggregate["generalizability_assessment"] = report
        aggregate["stage"] = "generalizability_assessment"
        write_json(aggregate_path, aggregate)
    return {
        "status": "success" if report["status"] == "valid" else "failure",
        "validation": report,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess whether the FunctionalMLDS case-study pipeline generalizes.")
    parser.add_argument("--out-root", type=Path, default=Path("output/case_studies"))
    args = parser.parse_args()
    result = run_generalizability_assessment(args.out_root)
    validation = result["validation"]
    print(
        "generalizability_assessment: {status} ({errors} errors, {checks} checks)".format(
            status=result["status"],
            errors=len(validation.get("errors") or []),
            checks=(validation.get("metrics") or {}).get("check_count"),
        )
    )
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
