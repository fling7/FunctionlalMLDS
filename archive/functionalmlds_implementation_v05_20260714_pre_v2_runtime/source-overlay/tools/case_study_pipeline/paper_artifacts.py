from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from .common import read_json, write_json


SCHEMA = "functionalmlds_paper_artifacts"
SCHEMA_VERSION = "1.0"


def _read_if_exists(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _csv(path: Path, rows: Sequence[Mapping[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _markdown_table(rows: Sequence[Mapping[str, Any]], fieldnames: Sequence[str]) -> str:
    lines = [
        "| " + " | ".join(fieldnames) + " |",
        "| " + " | ".join("---" for _ in fieldnames) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_fmt(row.get(field)) for field in fieldnames) + " |")
    return "\n".join(lines)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _case_dirs(out_root: Path) -> List[Path]:
    return sorted(
        path
        for path in out_root.iterdir()
        if path.is_dir() and path.name != "paper_artifacts" and (path / "stage_manifest.json").exists()
    )


def _scenario_step_count(instance: Mapping[str, Any]) -> int:
    count = 0
    for use_case in ((instance.get("requirementsModel") or {}).get("useCases") or []):
        for scenario in use_case.get("scenarios") or []:
            count += len(scenario.get("steps") or [])
    return count


def _stage_attempts(manifest: Mapping[str, Any]) -> int:
    total = 0
    for stage in manifest.get("stages") or []:
        metadata = stage.get("metadata") or {}
        try:
            total += int(metadata.get("attempts_used") or 0)
        except Exception:
            continue
    return total


def _repair_log_counts(case_dir: Path) -> Dict[str, int]:
    path = case_dir / "validation" / "repair_log.jsonl"
    counts = {
        "repair_log_entries": 0,
        "llm_generation_attempts": 0,
        "llm_repair_attempts": 0,
        "deterministic_recoveries": 0,
        "accepted_warnings": 0,
    }
    if not path.exists():
        return counts
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            counts["repair_log_entries"] += 1
            repair_type = entry.get("repair_type")
            if repair_type == "llm_generation_attempt":
                counts["llm_generation_attempts"] += 1
            elif repair_type == "llm_repair_attempt":
                counts["llm_repair_attempts"] += 1
            elif repair_type == "deterministic_recovery":
                counts["deterministic_recoveries"] += 1
            elif repair_type == "accepted_warning":
                counts["accepted_warnings"] += 1
    return counts


def _case_summary_rows(out_root: Path, aggregate: Mapping[str, Any]) -> List[Dict[str, Any]]:
    summaries = ((aggregate.get("cross_case_metrics") or {}).get("case_summaries") or [])
    rows: List[Dict[str, Any]] = []
    for summary in summaries:
        rows.append(
            {
                "case_id": summary.get("case_id"),
                "domain": summary.get("domain"),
                "room_purpose": summary.get("room_purpose"),
                "objects": summary.get("object_count"),
                "semantic_zones": summary.get("semantic_zone_count"),
                "agents": summary.get("agent_count"),
                "questions": summary.get("question_count"),
                "chat_tests": summary.get("chat_count"),
                "chat_success": summary.get("chat_success_count"),
                "trace_coverage": summary.get("trace_average_coverage"),
                "handoff_accuracy": summary.get("handoff_accuracy"),
                "grounding": summary.get("answer_grounding_ratio"),
            }
        )
    return rows


def _metamodel_rows(case_dirs: Iterable[Path]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for case_dir in case_dirs:
        instance = _read_if_exists(case_dir / "functionalmlds" / "functionalmlds.instance.generated.json")
        req_model = instance.get("requirementsModel") or {}
        invariant = _read_if_exists(case_dir / "validation" / "functionalmlds_invariant_validation.json")
        rows.append(
            {
                "case_id": case_dir.name,
                "requirements": len(req_model.get("requirements") or []),
                "use_cases": len(req_model.get("useCases") or []),
                "scenario_steps": _scenario_step_count(instance),
                "actors": len(instance.get("actors") or []),
                "entities": len(instance.get("entities") or []),
                "agents": len(instance.get("agents") or []),
                "capabilities": len(instance.get("capabilities") or []),
                "capability_uses": len(instance.get("capabilityUses") or []),
                "runtime_bindings": len(instance.get("runtimeBindings") or []),
                "validation_cases": len(instance.get("validationCases") or []),
                "satisfy_relationships": len(instance.get("satisfyRelationships") or []),
                "invariant_status": invariant.get("status"),
            }
        )
    return rows


def _validation_repair_rows(case_dirs: Iterable[Path]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for case_dir in case_dirs:
        schema = _read_if_exists(case_dir / "validation" / "schema_validation.json")
        invariant = _read_if_exists(case_dir / "validation" / "functionalmlds_invariant_validation.json")
        stage_completion = _read_if_exists(case_dir / "validation" / "stage_completion_report.json")
        repair_counts = _repair_log_counts(case_dir)
        rows.append(
            {
                "case_id": case_dir.name,
                "repair_log_entries": repair_counts["repair_log_entries"],
                "llm_generation_attempts": repair_counts["llm_generation_attempts"],
                "llm_repair_attempts": repair_counts["llm_repair_attempts"],
                "deterministic_recoveries": repair_counts["deterministic_recoveries"],
                "accepted_warnings": repair_counts["accepted_warnings"],
                "final_schema_errors": len(schema.get("errors") or []),
                "final_invariant_errors": len(invariant.get("errors") or []),
                "final_stage_completion": (stage_completion.get("metrics") or {}).get("completion_ratio"),
                "final_status": "valid" if not (schema.get("errors") or invariant.get("errors")) else "invalid",
            }
        )
    return rows


def _runtime_rows(case_dirs: Iterable[Path]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for case_dir in case_dirs:
        chat = _read_if_exists(case_dir / "validation" / "chat_test_results.json")
        handoff = _read_if_exists(case_dir / "validation" / "handoff_test_results.json")
        grounding = _read_if_exists(case_dir / "validation" / "answer_grounding_results.json")
        placement = _read_if_exists(case_dir / "validation" / "placement_metrics.json")
        rows.append(
            {
                "case_id": case_dir.name,
                "chat_tests": (chat.get("metrics") or {}).get("executed_chat_count"),
                "chat_success": (chat.get("metrics") or {}).get("successful_chat_count"),
                "handoff_tests": (handoff.get("metrics") or {}).get("handoff_test_count"),
                "handoff_success_rate": (handoff.get("metrics") or {}).get("handoff_test_success_rate"),
                "grounded_answers": (grounding.get("metrics") or {}).get("grounded_answer_count"),
                "grounding_ratio": (grounding.get("metrics") or {}).get("grounded_answer_ratio"),
                "valid_placements": (placement.get("metrics") or {}).get("valid_position_count"),
                "obstacle_overlaps": (placement.get("metrics") or {}).get("obstacle_overlap_count"),
            }
        )
    return rows


def _example_trace(case_dir: Path) -> Dict[str, Any]:
    instance = _read_if_exists(case_dir / "functionalmlds" / "functionalmlds.instance.generated.json")
    agent_roles = _read_if_exists(case_dir / "intermediate" / "agent_roles.generated.json")
    chat = _read_if_exists(case_dir / "validation" / "chat_test_results.json")
    runtime_bindings = {item.get("capability_id"): item for item in instance.get("runtimeBindings") or []}
    first_agent = (agent_roles.get("agents") or [{}])[0]
    first_chat = (chat.get("chat_tests") or [{}])[0]
    capability = next(
        (
            item
            for item in instance.get("capabilities") or []
            if "ANSWER-ROOM-GROUNDED-QUESTION" in str(item.get("id") or "")
        ),
        (instance.get("capabilities") or [{}])[0],
    )
    binding = runtime_bindings.get(capability.get("id")) or (instance.get("runtimeBindings") or [{}])[0]
    return {
        "case_id": case_dir.name,
        "object_group_or_zone": (first_agent.get("responsible_zone_ids") or first_agent.get("grounded_object_ids") or ["n/a"])[0],
        "agent_role": first_agent.get("id"),
        "knowledge_tag": (first_agent.get("knowledge_tags") or ["n/a"])[0],
        "capability": capability.get("id"),
        "runtime_binding": binding.get("id"),
        "runtime_action": ((binding.get("runtimeActions") or [{}])[0]).get("id"),
        "chat_event": first_chat.get("question_id"),
        "observed_handoff": first_chat.get("observed_handoff"),
        "grounded": True,
    }


def _pipeline_mermaid() -> str:
    return """flowchart LR
  A["MLDS / MLDSI file"] --> B["MLDS ingestion and normalization"]
  B --> C["Scene semantics"]
  C --> D["Agent roles and handoff matrix"]
  D --> E["Knowledge synthesis"]
  D --> F["Agent placement"]
  E --> G["FunctionalMLDS assembly"]
  F --> G
  G --> H["Schema and invariant validation"]
  H --> I["Interactive Agents project materialization"]
  I --> J["Backend setup"]
  J --> K["Chat and handoff runtime tests"]
  K --> L["Answer grounding"]
  L --> M["Cross-case metrics and paper artefacts"]
"""


def _trace_mermaid(example: Mapping[str, Any]) -> str:
    return f"""flowchart LR
  A["MLDS object group / zone: {example.get('object_group_or_zone')}"] --> B["Agent role: {example.get('agent_role')}"]
  B --> C["Knowledge tag: {example.get('knowledge_tag')}"]
  C --> D["Capability: {example.get('capability')}"]
  D --> E["RuntimeBinding: {example.get('runtime_binding')}"]
  E --> F["RuntimeAction: {example.get('runtime_action')}"]
  F --> G["Chat test event: {example.get('chat_event')}"]
"""


def _placement_mermaid(case_dir: Path) -> str:
    placements = _read_if_exists(case_dir / "intermediate" / "agent_placements.json")
    bounds = placements.get("room_bounds") or {}
    bounds_label = (
        f"x=[{bounds.get('min_x')}, {bounds.get('max_x')}], "
        f"z=[{bounds.get('min_z')}, {bounds.get('max_z')}]"
    )
    lines = [
        "flowchart TB",
        f'  R["Room bounds: {bounds_label}"]',
    ]
    for index, agent in enumerate(placements.get("agent_placements") or [], start=1):
        position = agent.get("position") or {}
        zones = ", ".join(agent.get("responsible_zone_ids") or [])
        label = f"{agent.get('id')} ({position.get('x')}, {position.get('z')})"
        lines.append(f'  R --> A{index}["{label}"]')
        if zones:
            lines.append(f'  A{index} --> Z{index}["responsible zone: {zones}"]')
    return "\n".join(lines) + "\n"


def generate_paper_artifacts(out_root: Path) -> Dict[str, Any]:
    out_root = Path(out_root).resolve()
    paper_dir = out_root / "paper_artifacts"
    tables_dir = paper_dir / "tables"
    figures_dir = paper_dir / "figures"
    examples_dir = paper_dir / "examples"
    aggregate = _read_if_exists(out_root / "aggregate_report.json")
    cases = _case_dirs(out_root)
    example_case = next((case for case in cases if case.name == "classroom_dinosaur"), cases[0] if cases else None)

    outputs: List[str] = []
    table_specs = [
        (
            "case_corpus",
            _case_summary_rows(out_root, aggregate),
            [
                "case_id",
                "domain",
                "room_purpose",
                "objects",
                "semantic_zones",
                "agents",
                "questions",
                "chat_tests",
                "chat_success",
                "trace_coverage",
                "handoff_accuracy",
                "grounding",
            ],
        ),
        (
            "metamodel_coverage",
            _metamodel_rows(cases),
            [
                "case_id",
                "requirements",
                "use_cases",
                "scenario_steps",
                "actors",
                "entities",
                "agents",
                "capabilities",
                "capability_uses",
                "runtime_bindings",
                "validation_cases",
                "satisfy_relationships",
                "invariant_status",
            ],
        ),
        (
            "validation_repair",
            _validation_repair_rows(cases),
            [
                "case_id",
                "repair_log_entries",
                "llm_generation_attempts",
                "llm_repair_attempts",
                "deterministic_recoveries",
                "accepted_warnings",
                "final_schema_errors",
                "final_invariant_errors",
                "final_stage_completion",
                "final_status",
            ],
        ),
        (
            "runtime_test_results",
            _runtime_rows(cases),
            [
                "case_id",
                "chat_tests",
                "chat_success",
                "handoff_tests",
                "handoff_success_rate",
                "grounded_answers",
                "grounding_ratio",
                "valid_placements",
                "obstacle_overlaps",
            ],
        ),
    ]

    for name, rows, fields in table_specs:
        csv_path = tables_dir / f"{name}.csv"
        md_path = tables_dir / f"{name}.md"
        _csv(csv_path, rows, fields)
        _write_text(md_path, f"# {name.replace('_', ' ').title()}\n\n" + _markdown_table(rows, fields) + "\n")
        outputs.extend([str(csv_path), str(md_path)])

    if example_case:
        example = _example_trace(example_case)
        example_path = examples_dir / "trace_chain_example.md"
        _write_text(
            example_path,
            "# Trace Chain Example\n\n"
            f"- Case: `{example['case_id']}`\n"
            f"- MLDS object group / zone: `{example['object_group_or_zone']}`\n"
            f"- Agent role: `{example['agent_role']}`\n"
            f"- Knowledge tag: `{example['knowledge_tag']}`\n"
            f"- Capability: `{example['capability']}`\n"
            f"- RuntimeBinding: `{example['runtime_binding']}`\n"
            f"- RuntimeAction: `{example['runtime_action']}`\n"
            f"- Chat event: `{example['chat_event']}`\n"
            f"- Observed handoff: `{example['observed_handoff']}`\n"
            f"- Grounded answer: `{example['grounded']}`\n",
        )
        outputs.append(str(example_path))
        figure_specs = [
            ("pipeline_architecture.mmd", _pipeline_mermaid()),
            ("trace_chain_example.mmd", _trace_mermaid(example)),
            ("agent_placement_classroom_dinosaur.mmd", _placement_mermaid(example_case)),
        ]
    else:
        figure_specs = [("pipeline_architecture.mmd", _pipeline_mermaid())]

    for filename, text in figure_specs:
        path = figures_dir / filename
        _write_text(path, text)
        outputs.append(str(path))

    index_path = paper_dir / "paper_artifacts_index.md"
    _write_text(
        index_path,
        "# Paper Artefacts Index\n\n"
        "## Study Protocol\n\n"
        "- `research_questions.md`\n"
        "- `baseline_definition.md` and `.json`\n"
        "- `comparison_metrics.md` and `.json`\n\n"
        "## Repair Protocol\n\n"
        "- `repair_prompt_registry.md` and `.json`\n"
        "- `deterministic_repair_policy.md`\n"
        "- `deterministic_repair_policy_report.md`\n\n"
        "## Tables\n\n"
        "- `tables/case_corpus.md` and `.csv`\n"
        "- `tables/metamodel_coverage.md` and `.csv`\n"
        "- `tables/validation_repair.md` and `.csv`\n"
        "- `tables/runtime_test_results.md` and `.csv`\n\n"
        "## Figures\n\n"
        "- `figures/pipeline_architecture.mmd`\n"
        "- `figures/trace_chain_example.mmd`\n"
        "- `figures/agent_placement_classroom_dinosaur.mmd`\n\n"
        "## Example\n\n"
        "- `examples/trace_chain_example.md`\n\n"
        "## Validity\n\n"
        "- `threats_to_validity.md` and `.json`\n",
    )
    outputs.append(str(index_path))

    manifest_path = paper_dir / "paper_artifacts_manifest.json"
    outputs.append(str(manifest_path))
    auxiliary_files = [
        paper_dir / "research_questions.md",
        paper_dir / "baseline_definition.md",
        paper_dir / "baseline_definition.json",
        paper_dir / "comparison_metrics.md",
        paper_dir / "comparison_metrics.json",
        paper_dir / "repair_prompt_registry.md",
        paper_dir / "repair_prompt_registry.json",
        paper_dir / "deterministic_repair_policy.md",
        paper_dir / "deterministic_repair_policy_report.md",
        paper_dir / "threats_to_validity.md",
        paper_dir / "threats_to_validity.json",
    ]
    document_count = 0
    for path in auxiliary_files:
        if path.exists():
            value = str(path)
            if value not in outputs:
                outputs.append(value)
            document_count += 1
    manifest = {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "valid",
        "errors": [],
        "warnings": [],
        "metrics": {
            "case_count": len(cases),
            "table_count": len(table_specs),
            "figure_count": len(figure_specs),
            "example_count": 1 if example_case else 0,
            "document_count": document_count,
            "output_count": len(outputs),
        },
        "outputs": outputs,
    }
    write_json(manifest_path, manifest)
    aggregate_path = out_root / "aggregate_report.json"
    if aggregate_path.exists():
        aggregate = _read_if_exists(aggregate_path)
        aggregate["stage"] = "paper_artifacts"
        aggregate["paper_artifacts"] = manifest
        write_json(aggregate_path, aggregate)
    return manifest


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate paper tables, figures and examples from case-study reports.")
    parser.add_argument("--out-root", type=Path, default=Path("output/case_studies"))
    args = parser.parse_args(argv)
    manifest = generate_paper_artifacts(args.out_root)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if manifest["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
