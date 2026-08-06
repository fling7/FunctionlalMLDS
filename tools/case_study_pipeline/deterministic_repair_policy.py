from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from .common import read_json, write_json


SCHEMA = "functionalmlds_deterministic_repair_policy_report"
SCHEMA_VERSION = "1.0"
POLICY_PATH = Path(__file__).resolve().parent / "config" / "deterministic_repair_policy.json"


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    entries: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            entries.append(json.loads(line))
    return entries


def _count(entries: List[Mapping[str, Any]], repair_type: str) -> int:
    return sum(1 for entry in entries if entry.get("repair_type") == repair_type)


def compute_policy_report(case_root: Path) -> Dict[str, Any]:
    case_root = Path(case_root).resolve()
    policy = read_json(POLICY_PATH)
    repair_entries = _read_jsonl(case_root / "repair_log.jsonl")
    deterministic_types = {"deterministic_recovery", "accepted_warning"}
    llm_repair_count = _count(repair_entries, "llm_repair_attempt")
    deterministic_repair_count = sum(1 for entry in repair_entries if entry.get("repair_type") in deterministic_types)
    llm_generation_count = _count(repair_entries, "llm_generation_attempt")
    rule_count = len(policy.get("rules") or [])
    deterministic_rule_count = sum(1 for rule in policy.get("rules") or [] if not rule.get("llm_allowed"))
    llm_rule_count = sum(1 for rule in policy.get("rules") or [] if rule.get("llm_allowed"))
    errors: List[str] = []
    if not rule_count:
        errors.append("No deterministic repair policy rules defined.")
    if not deterministic_rule_count:
        errors.append("No deterministic repair rules defined before LLM escalation.")
    if not llm_rule_count:
        errors.append("No LLM escalation rule defined.")
    if llm_repair_count > 0 and deterministic_repair_count == 0:
        errors.append("LLM repair attempts occurred without any deterministic repair evidence.")
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": [],
        "metrics": {
            "rule_count": rule_count,
            "deterministic_rule_count": deterministic_rule_count,
            "llm_escalation_rule_count": llm_rule_count,
            "repair_log_entry_count": len(repair_entries),
            "llm_generation_attempt_count": llm_generation_count,
            "llm_repair_attempt_count": llm_repair_count,
            "deterministic_repair_evidence_count": deterministic_repair_count,
            "deterministic_first_policy_satisfied": deterministic_rule_count > 0 and llm_rule_count > 0,
        },
        "policy_path": str(POLICY_PATH),
        "repair_log_path": str(case_root / "repair_log.jsonl"),
        "rules": policy.get("rules") or [],
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    metrics = report.get("metrics") or {}
    lines = [
        "# Deterministic Repair Policy Report",
        "",
        f"- Status: {report.get('status')}",
        f"- Rules: {metrics.get('rule_count')}",
        f"- Deterministic rules: {metrics.get('deterministic_rule_count')}",
        f"- LLM escalation rules: {metrics.get('llm_escalation_rule_count')}",
        f"- Repair log entries: {metrics.get('repair_log_entry_count')}",
        f"- LLM first-generation attempts: {metrics.get('llm_generation_attempt_count')}",
        f"- LLM repair attempts: {metrics.get('llm_repair_attempt_count')}",
        f"- Deterministic repair evidence: {metrics.get('deterministic_repair_evidence_count')}",
        "",
        "## Rules",
        "",
        "| Priority | Rule ID | Repair type | LLM allowed | Name |",
        "|---:|---|---|---:|---|",
    ]
    for rule in sorted(report.get("rules") or [], key=lambda item: int(item.get("priority") or 0)):
        lines.append(
            "| {priority} | {rule_id} | {repair_type} | {llm_allowed} | {name} |".format(
                priority=rule.get("priority"),
                rule_id=rule.get("rule_id"),
                repair_type=rule.get("repair_type"),
                llm_allowed=rule.get("llm_allowed"),
                name=rule.get("name"),
            )
        )
    lines.append("")
    return "\n".join(lines)


def run_policy_report(case_root: Path) -> Dict[str, Any]:
    case_root = Path(case_root).resolve()
    report = compute_policy_report(case_root)
    output_path = case_root / "deterministic_repair_policy_report.json"
    markdown_path = case_root / "paper_artifacts" / "deterministic_repair_policy_report.md"
    write_json(output_path, report)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    aggregate_path = case_root / "aggregate_report.json"
    if aggregate_path.exists():
        aggregate = read_json(aggregate_path)
        aggregate["deterministic_repair_policy"] = report
        write_json(aggregate_path, aggregate)
    return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate deterministic-first repair policy against repair logs.")
    parser.add_argument("--case-root", type=Path, default=Path("output/case_studies"))
    args = parser.parse_args(argv)
    report = run_policy_report(args.case_root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
