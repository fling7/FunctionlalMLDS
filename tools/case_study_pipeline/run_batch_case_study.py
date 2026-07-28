from __future__ import annotations

import argparse
import glob
from pathlib import Path
from typing import Any, Dict, List

from .agent_placement import run_agent_placement_for_case, validate_agent_placements
from .agent_roles import (
    PROMPT_PATH as AGENT_ROLES_PROMPT_PATH,
    REPAIR_PROMPT_PATH as AGENT_ROLES_REPAIR_PROMPT_PATH,
    run_agent_roles_for_case,
    validate_agent_roles,
)
from .answer_grounding import run_answer_grounding_for_case
from .chat_tests import backend_url_from_config, run_chat_tests_for_case
from .common import (
    manifest_stage_inputs_match,
    manifest_stage_metadata_matches,
    read_json,
    update_manifest,
    write_json,
)
from .cross_case_metrics import run_cross_case_metrics
from .deterministic_repair_policy import run_policy_report
from .evaluation_questions import run_evaluation_questions_for_case
from .functionalmlds_assembler import (
    PROMPT_PATH as FUNCTIONALMLDS_PROMPT_PATH,
    run_functionalmlds_assembly_for_case,
    validate_functionalmlds_instance,
)
from .functionalmlds_v2_assembler import run_functionalmlds_v2_assembly_for_case
from .generalizability_assessment import run_generalizability_assessment
from .handoff_derivation import run_handoff_derivation_for_case
from .handoff_tests import run_handoff_tests_for_case
from .knowledge_synthesis import (
    PROMPT_PATH as KNOWLEDGE_PROMPT_PATH,
    REPAIR_PROMPT_PATH as KNOWLEDGE_REPAIR_PROMPT_PATH,
    materialize_knowledge_files,
    run_knowledge_synthesis_for_case,
    validate_knowledge,
)
from .mlds_ingestion import run_pipeline
from .paper_artifacts import generate_paper_artifacts
from .project_materializer import DEFAULT_BACKEND_ROOT, run_project_materializer_for_case, validate_materialized_project
from .repair_log import run_repair_log
from .scene_semantics import (
    PROMPT_PATH as SCENE_SEMANTICS_PROMPT_PATH,
    REPAIR_PROMPT_PATH as SCENE_SEMANTICS_REPAIR_PROMPT_PATH,
    run_scene_semantics_for_case,
    validate_scene_semantics,
)
from .stage_completion import run_stage_completion_for_case
from .validators.schema_validator import run_schema_validation_for_case
from .validators.functionalmlds_invariants import run_functionalmlds_invariant_validation_for_case
from .validators.handoff_metrics import run_handoff_metrics_for_case
from .validators.placement_metrics import run_placement_metrics_for_case
from .validators.traceability_metrics import run_traceability_metrics_for_case


CONFIG_DIR = Path(__file__).resolve().parent / "config"
FUNCTIONALMLDS_IMPLEMENTATION_PATH = (
    Path(__file__).resolve().parent / "functionalmlds_assembler.py"
)
PROJECT_MATERIALIZER_IMPLEMENTATION_PATH = (
    Path(__file__).resolve().parent / "project_materializer.py"
)


def _load_default_inputs() -> List[Path]:
    path = CONFIG_DIR / "default_inputs.json"
    if not path.exists():
        return []
    payload = read_json(path)
    if not isinstance(payload, list):
        return []
    return [Path(str(item)) for item in payload if str(item).strip()]


DEFAULT_INPUTS = _load_default_inputs()


def _validation_is_valid(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        return read_json(path).get("status") == "valid"
    except Exception:
        return False


def _manifest_inputs_match(case_dir: Path, stage_id: str, input_paths: List[Path]) -> bool:
    return manifest_stage_inputs_match(
        case_dir,
        stage_id,
        input_paths,
        exact=True,
    )


def _can_reuse_stage(
    case_dir: Path,
    *,
    stage_id: str,
    validation_path: Path,
    output_paths: List[Path],
    input_paths: List[Path],
    expected_metadata: Dict[str, Any] | None = None,
) -> bool:
    return (
        _validation_is_valid(validation_path)
        and all(path.exists() for path in output_paths)
        and _manifest_inputs_match(case_dir, stage_id, input_paths)
        and (
            not expected_metadata
            or manifest_stage_metadata_matches(
                case_dir,
                stage_id,
                expected_metadata,
            )
        )
    )


def _recover_scene_semantics_if_possible(case_dir: Path) -> None:
    normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
    group_summary_path = case_dir / "intermediate" / "object_group_summary.json"
    semantics_path = case_dir / "intermediate" / "scene_semantics.json"
    validation_path = case_dir / "validation" / "scene_semantics_validation.json"
    if not semantics_path.exists() or _validation_is_valid(validation_path):
        return
    normalized = read_json(normalized_path)
    validation = validate_scene_semantics(read_json(semantics_path), normalized)
    write_json(validation_path, validation)
    if validation["status"] == "valid":
        update_manifest(
            case_dir,
            stage_id="scene_semantics",
            status="success",
            input_paths=[normalized_path, group_summary_path, SCENE_SEMANTICS_PROMPT_PATH, SCENE_SEMANTICS_REPAIR_PROMPT_PATH],
            output_paths=[semantics_path, validation_path],
            metadata={"recovered_without_llm": True, "metrics": validation.get("metrics", {})},
        )


def _recover_agent_roles_if_possible(case_dir: Path) -> None:
    normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
    group_summary_path = case_dir / "intermediate" / "object_group_summary.json"
    semantics_path = case_dir / "intermediate" / "scene_semantics.json"
    agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    handoff_path = case_dir / "intermediate" / "handoff_matrix.json"
    validation_path = case_dir / "validation" / "agent_roles_validation.json"
    if not agent_roles_path.exists() or not handoff_path.exists() or _validation_is_valid(validation_path):
        return
    combined = {}
    combined.update(read_json(agent_roles_path))
    combined.update(read_json(handoff_path))
    validation = validate_agent_roles(
        combined,
        scene_semantics=read_json(semantics_path),
        normalized_scene=read_json(normalized_path),
    )
    write_json(validation_path, validation)
    if validation["status"] == "valid":
        update_manifest(
            case_dir,
            stage_id="agent_roles",
            status="success",
            input_paths=[normalized_path, group_summary_path, semantics_path, AGENT_ROLES_PROMPT_PATH, AGENT_ROLES_REPAIR_PROMPT_PATH],
            output_paths=[agent_roles_path, handoff_path, validation_path],
            metadata={"recovered_without_llm": True, "metrics": validation.get("metrics", {})},
        )


def _recover_knowledge_if_possible(case_dir: Path) -> None:
    normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
    semantics_path = case_dir / "intermediate" / "scene_semantics.json"
    agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    knowledge_path = case_dir / "intermediate" / "knowledge.generated.json"
    validation_path = case_dir / "validation" / "knowledge_synthesis_validation.json"
    if not knowledge_path.exists() or _validation_is_valid(validation_path):
        return
    knowledge = read_json(knowledge_path)
    validation = validate_knowledge(
        knowledge,
        normalized_scene=read_json(normalized_path),
        agent_roles=read_json(agent_roles_path),
    )
    written_files = materialize_knowledge_files(case_dir, knowledge) if validation["status"] == "valid" else []
    write_json(validation_path, validation)
    if validation["status"] == "valid":
        update_manifest(
            case_dir,
            stage_id="knowledge_synthesis",
            status="success",
            input_paths=[normalized_path, semantics_path, agent_roles_path, KNOWLEDGE_PROMPT_PATH, KNOWLEDGE_REPAIR_PROMPT_PATH],
            output_paths=[knowledge_path, validation_path, *written_files],
            metadata={"recovered_without_llm": True, "metrics": validation.get("metrics", {})},
        )


def _recover_agent_placement_if_possible(case_dir: Path) -> None:
    normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
    semantics_path = case_dir / "intermediate" / "scene_semantics.json"
    agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    placements_path = case_dir / "intermediate" / "agent_placements.json"
    validation_path = case_dir / "validation" / "agent_placement_validation.json"
    if not placements_path.exists() or _validation_is_valid(validation_path):
        return
    validation = validate_agent_placements(
        read_json(placements_path),
        normalized_scene=read_json(normalized_path),
        agent_roles=read_json(agent_roles_path),
    )
    write_json(validation_path, validation)
    if validation["status"] == "valid":
        update_manifest(
            case_dir,
            stage_id="agent_placement",
            status="success",
            input_paths=[normalized_path, semantics_path, agent_roles_path],
            output_paths=[placements_path, validation_path],
            metadata={"recovered_without_rerun": True, "metrics": validation.get("metrics", {})},
        )


def _recover_functionalmlds_if_possible(case_dir: Path) -> None:
    normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
    semantics_path = case_dir / "intermediate" / "scene_semantics.json"
    agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    placements_path = case_dir / "intermediate" / "agent_placements.json"
    instance_path = case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"
    validation_path = case_dir / "validation" / "functionalmlds_invariant_validation.json"
    if not instance_path.exists() or _validation_is_valid(validation_path):
        return
    validation = validate_functionalmlds_instance(read_json(instance_path))
    write_json(validation_path, validation)
    if validation["status"] == "valid":
        update_manifest(
            case_dir,
            stage_id="functionalmlds_assembly",
            status="success",
            input_paths=[
                normalized_path,
                semantics_path,
                agent_roles_path,
                placements_path,
                FUNCTIONALMLDS_PROMPT_PATH,
                FUNCTIONALMLDS_IMPLEMENTATION_PATH,
            ],
            output_paths=[instance_path, validation_path],
            metadata={"recovered_without_rerun": True, "metrics": validation.get("metrics", {})},
        )


def _recover_project_materialization_if_possible(case_dir: Path, backend_root: Path = DEFAULT_BACKEND_ROOT) -> None:
    source_mlds = case_dir / "input" / "source_mlds.json"
    agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    placements_path = case_dir / "intermediate" / "agent_placements.json"
    knowledge_path = case_dir / "intermediate" / "knowledge.generated.json"
    functionalmlds_path = case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"
    functionalmlds_v2_path = case_dir / "functionalmlds" / "functionalmlds.v2.instance.json"
    project_dir = backend_root.resolve() / "projects" / case_dir.name
    validation_path = case_dir / "validation" / "project_materialization_validation.json"
    project_paths = {
        "project_dir": project_dir,
        "project_json": project_dir / "project.json",
        "room_plan": project_dir / "room_plan.json",
        "agents": project_dir / "agents.json",
        "trace_map": project_dir / "trace_map.json",
        "trace_map_v2": project_dir / "trace_map.v2.json",
        "trace_map_v05": project_dir / "trace_map.v05.json",
        "functionalmlds_v2": project_dir / "functionalmlds.v2.instance.json",
        "functionalmlds_v05": project_dir / "functionalmlds.v05.instance.json",
        "kb_root": project_dir / "kb",
    }
    if not project_paths["project_json"].exists() or _validation_is_valid(validation_path):
        return
    validation = validate_materialized_project(project_paths, case_dir=case_dir, backend_root=backend_root)
    write_json(validation_path, validation)
    if validation["status"] == "valid":
        update_manifest(
            case_dir,
            stage_id="project_materialization",
            status="success",
            input_paths=[
                source_mlds,
                agent_roles_path,
                placements_path,
                knowledge_path,
                functionalmlds_path,
                functionalmlds_v2_path,
                PROJECT_MATERIALIZER_IMPLEMENTATION_PATH,
            ],
            output_paths=[
                project_paths["project_json"],
                project_paths["room_plan"],
                project_paths["agents"],
                project_paths["trace_map"],
                project_paths["trace_map_v2"],
                project_paths["trace_map_v05"],
                project_paths["functionalmlds_v2"],
                project_paths["functionalmlds_v05"],
                validation_path,
            ],
            metadata={"recovered_without_rerun": True, "metrics": validation.get("metrics", {})},
        )


def _existing_scene_semantics_result(case_dir: Path) -> Dict[str, Any]:
    validation = read_json(case_dir / "validation" / "scene_semantics_validation.json")
    return {
        "case_id": case_dir.name,
        "status": "success",
        "validation": validation,
        "semantics_path": str(case_dir / "intermediate" / "scene_semantics.json"),
        "validation_path": str(case_dir / "validation" / "scene_semantics_validation.json"),
        "model": "reused",
        "attempts_used": 0,
    }


def _existing_agent_roles_result(case_dir: Path) -> Dict[str, Any]:
    validation = read_json(case_dir / "validation" / "agent_roles_validation.json")
    return {
        "case_id": case_dir.name,
        "status": "success",
        "validation": validation,
        "agent_roles_path": str(case_dir / "intermediate" / "agent_roles.generated.json"),
        "handoff_matrix_path": str(case_dir / "intermediate" / "handoff_matrix.json"),
        "validation_path": str(case_dir / "validation" / "agent_roles_validation.json"),
        "model": "reused",
        "attempts_used": 0,
    }


def _existing_knowledge_result(case_dir: Path) -> Dict[str, Any]:
    validation = read_json(case_dir / "validation" / "knowledge_synthesis_validation.json")
    return {
        "case_id": case_dir.name,
        "status": "success",
        "validation": validation,
        "knowledge_path": str(case_dir / "intermediate" / "knowledge.generated.json"),
        "kb_root": str(case_dir / "interactive_agents_project" / "kb"),
        "validation_path": str(case_dir / "validation" / "knowledge_synthesis_validation.json"),
        "model": "reused",
        "attempts_used": 0,
    }


def _existing_agent_placement_result(case_dir: Path) -> Dict[str, Any]:
    validation = read_json(case_dir / "validation" / "agent_placement_validation.json")
    return {
        "case_id": case_dir.name,
        "status": "success",
        "validation": validation,
        "placements_path": str(case_dir / "intermediate" / "agent_placements.json"),
        "validation_path": str(case_dir / "validation" / "agent_placement_validation.json"),
    }


def _existing_functionalmlds_result(case_dir: Path) -> Dict[str, Any]:
    validation = read_json(case_dir / "validation" / "functionalmlds_invariant_validation.json")
    return {
        "case_id": case_dir.name,
        "status": "success",
        "validation": validation,
        "functionalmlds_path": str(case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"),
        "validation_path": str(case_dir / "validation" / "functionalmlds_invariant_validation.json"),
    }


def _existing_project_materialization_result(case_dir: Path, backend_root: Path = DEFAULT_BACKEND_ROOT) -> Dict[str, Any]:
    validation = read_json(case_dir / "validation" / "project_materialization_validation.json")
    return {
        "case_id": case_dir.name,
        "status": "success",
        "validation": validation,
        "project_dir": str(backend_root.resolve() / "projects" / case_dir.name),
        "validation_path": str(case_dir / "validation" / "project_materialization_validation.json"),
    }


def resolve_inputs(explicit_inputs: List[str], input_glob: str | None) -> List[Path]:
    paths: List[Path] = []
    if explicit_inputs:
        paths.extend(Path(p) for p in explicit_inputs)
    if input_glob:
        paths.extend(Path(p) for p in glob.glob(input_glob, recursive=True))
    if not paths:
        paths.extend(DEFAULT_INPUTS)
    unique: List[Path] = []
    seen = set()
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the modular FunctionalMLDS case-study pipeline.")
    parser.add_argument("--inputs", nargs="*", default=[], help="Explicit MLDS/RoomPlan JSON files.")
    parser.add_argument("--input-glob", default=None, help="Glob for additional MLDS/RoomPlan JSON files.")
    parser.add_argument("--out-root", type=Path, default=Path("output/case_studies"))
    parser.add_argument("--run-llm", action="store_true", help="Run LLM-based stages after offline ingestion.")
    parser.add_argument("--run-runtime", action="store_true", help="Run backend chat, handoff and answer-grounding runtime checks.")
    parser.add_argument("--max-repair-attempts", type=int, default=3)
    parser.add_argument("--model", default=None, help="Optional OpenAI model override for LLM stages.")
    parser.add_argument("--force-llm", action="store_true", help="Re-run LLM stages even when valid cached outputs exist.")
    parser.add_argument(
        "--backend-config",
        type=Path,
        default=Path("InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/config.json"),
        help="Backend config containing the local OpenAI settings.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inputs = resolve_inputs(args.inputs, args.input_glob)
    missing = [str(path) for path in inputs if not path.exists()]
    if missing:
        for path in missing:
            print(f"Missing input: {path}")
        return 2

    out_root = args.out_root.resolve()
    results = run_pipeline(inputs, out_root)
    semantics_results = []
    agent_role_results = []
    knowledge_results = []
    placement_results = []
    functionalmlds_results = []
    handoff_derivation_results = []
    functionalmlds_v2_results = []
    materialization_results = []
    schema_validation_results = []
    functionalmlds_invariant_results = []
    traceability_metric_results = []
    placement_metric_results = []
    handoff_metric_results = []
    evaluation_question_results = []
    chat_test_results = []
    handoff_test_results = []
    answer_grounding_results = []
    stage_completion_results = []
    cross_case_metric_result = None
    generalizability_result = None
    repair_log_result = None
    deterministic_repair_policy_result = None
    paper_artifacts_result = None
    if args.run_llm:
        for result in results:
            case_dir = out_root / result["case_id"]
            normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
            group_summary_path = case_dir / "intermediate" / "object_group_summary.json"
            semantics_path = case_dir / "intermediate" / "scene_semantics.json"
            semantics_validation_path = case_dir / "validation" / "scene_semantics_validation.json"
            if not args.force_llm:
                _recover_scene_semantics_if_possible(case_dir)
            if not args.force_llm and _can_reuse_stage(
                case_dir,
                stage_id="scene_semantics",
                validation_path=semantics_validation_path,
                output_paths=[semantics_path, semantics_validation_path],
                input_paths=[
                    normalized_path,
                    group_summary_path,
                    SCENE_SEMANTICS_PROMPT_PATH,
                    SCENE_SEMANTICS_REPAIR_PROMPT_PATH,
                ],
                expected_metadata=(
                    {"llm.model": args.model} if args.model else None
                ),
            ):
                semantics_results.append(_existing_scene_semantics_result(case_dir))
            else:
                semantics_results.append(
                    run_scene_semantics_for_case(
                        case_dir,
                        model_override=args.model,
                        max_repair_attempts=args.max_repair_attempts,
                        config_path=args.backend_config,
                    )
                )
        for result in semantics_results:
            if result["status"] != "success":
                agent_role_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because scene_semantics did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            case_dir = out_root / result["case_id"]
            normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
            group_summary_path = case_dir / "intermediate" / "object_group_summary.json"
            semantics_path = case_dir / "intermediate" / "scene_semantics.json"
            agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
            handoff_path = case_dir / "intermediate" / "handoff_matrix.json"
            agent_roles_validation_path = case_dir / "validation" / "agent_roles_validation.json"
            if not args.force_llm:
                _recover_agent_roles_if_possible(case_dir)
            if not args.force_llm and _can_reuse_stage(
                case_dir,
                stage_id="agent_roles",
                validation_path=agent_roles_validation_path,
                output_paths=[agent_roles_path, handoff_path, agent_roles_validation_path],
                input_paths=[
                    normalized_path,
                    group_summary_path,
                    semantics_path,
                    AGENT_ROLES_PROMPT_PATH,
                    AGENT_ROLES_REPAIR_PROMPT_PATH,
                ],
                expected_metadata=(
                    {"llm.model": args.model} if args.model else None
                ),
            ):
                agent_role_results.append(_existing_agent_roles_result(case_dir))
            else:
                agent_role_results.append(
                    run_agent_roles_for_case(
                        case_dir,
                        model_override=args.model,
                        max_repair_attempts=args.max_repair_attempts,
                        config_path=args.backend_config,
                    )
                )
        for result in agent_role_results:
            if result["status"] != "success":
                knowledge_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because agent_roles did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            case_dir = out_root / result["case_id"]
            normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
            semantics_path = case_dir / "intermediate" / "scene_semantics.json"
            agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
            knowledge_path = case_dir / "intermediate" / "knowledge.generated.json"
            knowledge_validation_path = case_dir / "validation" / "knowledge_synthesis_validation.json"
            kb_root = case_dir / "interactive_agents_project" / "kb"
            if not args.force_llm:
                _recover_knowledge_if_possible(case_dir)
            if not args.force_llm and _can_reuse_stage(
                case_dir,
                stage_id="knowledge_synthesis",
                validation_path=knowledge_validation_path,
                output_paths=[knowledge_path, knowledge_validation_path, kb_root],
                input_paths=[
                    normalized_path,
                    semantics_path,
                    agent_roles_path,
                    KNOWLEDGE_PROMPT_PATH,
                    KNOWLEDGE_REPAIR_PROMPT_PATH,
                ],
                expected_metadata=(
                    {"llm.model": args.model} if args.model else None
                ),
            ):
                knowledge_results.append(_existing_knowledge_result(case_dir))
            else:
                knowledge_results.append(
                    run_knowledge_synthesis_for_case(
                        case_dir,
                        model_override=args.model,
                        max_repair_attempts=args.max_repair_attempts,
                        config_path=args.backend_config,
                )
            )
        for result in knowledge_results:
            if result["status"] != "success":
                placement_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because knowledge_synthesis did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            case_dir = out_root / result["case_id"]
            normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
            semantics_path = case_dir / "intermediate" / "scene_semantics.json"
            agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
            placements_path = case_dir / "intermediate" / "agent_placements.json"
            placement_validation_path = case_dir / "validation" / "agent_placement_validation.json"
            _recover_agent_placement_if_possible(case_dir)
            if _can_reuse_stage(
                case_dir,
                stage_id="agent_placement",
                validation_path=placement_validation_path,
                output_paths=[placements_path, placement_validation_path],
                input_paths=[normalized_path, semantics_path, agent_roles_path],
            ):
                placement_results.append(_existing_agent_placement_result(case_dir))
            else:
                placement_results.append(run_agent_placement_for_case(case_dir))
        for result in placement_results:
            if result["status"] != "success":
                functionalmlds_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because agent_placement did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            case_dir = out_root / result["case_id"]
            normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
            semantics_path = case_dir / "intermediate" / "scene_semantics.json"
            agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
            placements_path = case_dir / "intermediate" / "agent_placements.json"
            instance_path = case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"
            validation_path = case_dir / "validation" / "functionalmlds_invariant_validation.json"
            _recover_functionalmlds_if_possible(case_dir)
            if _can_reuse_stage(
                case_dir,
                stage_id="functionalmlds_assembly",
                validation_path=validation_path,
                output_paths=[instance_path, validation_path],
                input_paths=[
                    normalized_path,
                    semantics_path,
                    agent_roles_path,
                    placements_path,
                    FUNCTIONALMLDS_PROMPT_PATH,
                    FUNCTIONALMLDS_IMPLEMENTATION_PATH,
                ],
            ):
                functionalmlds_results.append(_existing_functionalmlds_result(case_dir))
            else:
                functionalmlds_results.append(run_functionalmlds_assembly_for_case(case_dir))
        for result in functionalmlds_results:
            if result["status"] != "success":
                handoff_derivation_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because functionalmlds_assembly did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            handoff_derivation_results.append(
                run_handoff_derivation_for_case(out_root / result["case_id"])
            )
        for result in handoff_derivation_results:
            if result["status"] != "success":
                functionalmlds_v2_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because handoff_derivation did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            functionalmlds_v2_results.append(
                run_functionalmlds_v2_assembly_for_case(out_root / result["case_id"])
            )
        for result in functionalmlds_v2_results:
            if result["status"] != "success":
                materialization_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because functionalmlds_v2_assembly did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            case_dir = out_root / result["case_id"]
            source_mlds = case_dir / "input" / "source_mlds.json"
            agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
            placements_path = case_dir / "intermediate" / "agent_placements.json"
            knowledge_path = case_dir / "intermediate" / "knowledge.generated.json"
            functionalmlds_path = case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"
            functionalmlds_v2_path = case_dir / "functionalmlds" / "functionalmlds.v2.instance.json"
            project_dir = DEFAULT_BACKEND_ROOT.resolve() / "projects" / result["case_id"]
            project_json = project_dir / "project.json"
            room_plan = project_dir / "room_plan.json"
            agents = project_dir / "agents.json"
            trace_map = project_dir / "trace_map.json"
            trace_map_v2 = project_dir / "trace_map.v2.json"
            trace_map_v05 = project_dir / "trace_map.v05.json"
            project_v2 = project_dir / "functionalmlds.v2.instance.json"
            project_v05 = project_dir / "functionalmlds.v05.instance.json"
            validation_path = case_dir / "validation" / "project_materialization_validation.json"
            _recover_project_materialization_if_possible(case_dir, DEFAULT_BACKEND_ROOT)
            if _can_reuse_stage(
                case_dir,
                stage_id="project_materialization",
                validation_path=validation_path,
                output_paths=[
                    project_json,
                    room_plan,
                    agents,
                    trace_map,
                    trace_map_v2,
                    trace_map_v05,
                    project_v2,
                    project_v05,
                    validation_path,
                ],
                input_paths=[
                    source_mlds,
                    agent_roles_path,
                    placements_path,
                    knowledge_path,
                    functionalmlds_path,
                    functionalmlds_v2_path,
                    PROJECT_MATERIALIZER_IMPLEMENTATION_PATH,
                ],
            ):
                materialization_results.append(_existing_project_materialization_result(case_dir, DEFAULT_BACKEND_ROOT))
            else:
                materialization_results.append(run_project_materializer_for_case(case_dir, backend_root=DEFAULT_BACKEND_ROOT))

    if materialization_results:
        for result in materialization_results:
            if result["status"] != "success":
                schema_validation_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because project_materialization did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            schema_validation_results.append(
                run_schema_validation_for_case(out_root / result["case_id"], backend_root=DEFAULT_BACKEND_ROOT)
            )

    if schema_validation_results:
        for result in schema_validation_results:
            if result["status"] != "success":
                functionalmlds_invariant_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because schema_validation did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            functionalmlds_invariant_results.append(
                run_functionalmlds_invariant_validation_for_case(out_root / result["case_id"])
            )

    if functionalmlds_invariant_results:
        for result in functionalmlds_invariant_results:
            if result["status"] != "success":
                traceability_metric_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because functionalmlds_invariants did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            traceability_metric_results.append(run_traceability_metrics_for_case(out_root / result["case_id"]))

    if traceability_metric_results:
        for result in traceability_metric_results:
            if result["status"] != "success":
                placement_metric_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because traceability_metrics did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            placement_metric_results.append(run_placement_metrics_for_case(out_root / result["case_id"]))

    if placement_metric_results:
        for result in placement_metric_results:
            if result["status"] != "success":
                handoff_metric_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because placement_metrics did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            handoff_metric_results.append(
                run_handoff_metrics_for_case(out_root / result["case_id"], config_path=args.backend_config)
            )

    if handoff_metric_results:
        for result in handoff_metric_results:
            if result["status"] != "success":
                evaluation_question_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because handoff_metrics did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            evaluation_question_results.append(run_evaluation_questions_for_case(out_root / result["case_id"]))

    if args.run_runtime and evaluation_question_results:
        backend_url = backend_url_from_config(args.backend_config)
        for result in evaluation_question_results:
            if result["status"] != "success":
                chat_test_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because evaluation_questions did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            chat_test_results.append(
                run_chat_tests_for_case(
                    out_root / result["case_id"],
                    backend_url=backend_url,
                    memory_mode="agent_private_history",
                    isolate_questions=True,
                )
            )

    if chat_test_results:
        for result in chat_test_results:
            if result["status"] != "success":
                handoff_test_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because chat_tests did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            handoff_test_results.append(run_handoff_tests_for_case(out_root / result["case_id"]))

    if handoff_test_results:
        for result in handoff_test_results:
            if result["status"] != "success":
                answer_grounding_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because handoff_tests did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            answer_grounding_results.append(run_answer_grounding_for_case(out_root / result["case_id"]))

    if answer_grounding_results:
        for result in answer_grounding_results:
            if result["status"] != "success":
                stage_completion_results.append(
                    {
                        "case_id": result["case_id"],
                        "status": "skipped",
                        "validation": {
                            "status": "invalid",
                            "errors": ["Skipped because answer_grounding did not succeed."],
                            "warnings": [],
                            "metrics": {},
                        },
                    }
                )
                continue
            stage_completion_results.append(run_stage_completion_for_case(out_root / result["case_id"]))

    if stage_completion_results and all(result["status"] == "success" for result in stage_completion_results):
        cross_case_metric_result = run_cross_case_metrics(out_root)

    final_results = stage_completion_results or answer_grounding_results or handoff_test_results or chat_test_results or evaluation_question_results or handoff_metric_results or placement_metric_results or traceability_metric_results or functionalmlds_invariant_results or schema_validation_results or materialization_results or functionalmlds_v2_results or handoff_derivation_results or functionalmlds_results or placement_results or knowledge_results or agent_role_results or semantics_results or results
    aggregate = {
        "stage": (
            "cross_case_metrics"
            if cross_case_metric_result
            else "stage_completion"
            if stage_completion_results
            else "answer_grounding"
            if answer_grounding_results
            else "handoff_tests"
            if handoff_test_results
            else "chat_tests"
            if chat_test_results
            else "evaluation_questions"
            if evaluation_question_results
            else "handoff_metrics"
            if handoff_metric_results
            else "placement_metrics"
            if placement_metric_results
            else "traceability_metrics"
            if traceability_metric_results
            else "functionalmlds_invariants"
            if functionalmlds_invariant_results
            else "schema_validation"
            if schema_validation_results
            else "project_materialization"
            if materialization_results
            else "functionalmlds_v2_assembly"
            if functionalmlds_v2_results
            else "handoff_derivation"
            if handoff_derivation_results
            else "functionalmlds_assembly"
            if functionalmlds_results
            else "agent_placement"
            if placement_results
            else "knowledge_synthesis"
            if knowledge_results
            else ("agent_roles" if agent_role_results else ("scene_semantics" if args.run_llm else "mlds_ingestion"))
        ),
        "case_count": len(results),
        "success_count": sum(1 for r in final_results if r["status"] == "success"),
        "failure_count": sum(1 for r in final_results if r["status"] != "success"),
        "llm_enabled": bool(args.run_llm),
        "runtime_enabled": bool(args.run_runtime),
        "max_repair_attempts": args.max_repair_attempts,
        "cases": results,
        "scene_semantics": semantics_results,
        "agent_roles": agent_role_results,
        "knowledge_synthesis": knowledge_results,
        "agent_placement": placement_results,
        "functionalmlds_assembly": functionalmlds_results,
        "handoff_derivation": handoff_derivation_results,
        "functionalmlds_v2_assembly": functionalmlds_v2_results,
        "project_materialization": materialization_results,
        "schema_validation": schema_validation_results,
        "functionalmlds_invariants": functionalmlds_invariant_results,
        "traceability_metrics": traceability_metric_results,
        "placement_metrics": placement_metric_results,
        "handoff_metrics": handoff_metric_results,
        "evaluation_questions": evaluation_question_results,
        "chat_tests": chat_test_results,
        "handoff_tests": handoff_test_results,
        "answer_grounding": answer_grounding_results,
        "stage_completion": stage_completion_results,
        "cross_case_metrics": cross_case_metric_result,
    }
    write_json(out_root / "aggregate_report.json", aggregate)
    if cross_case_metric_result:
        # Re-apply the cross-case writer because it augments the aggregate JSON and writes aggregate_report.md.
        cross_case_metric_result = run_cross_case_metrics(out_root)
    if cross_case_metric_result and cross_case_metric_result["status"] == "success":
        generalizability_result = run_generalizability_assessment(out_root)
        aggregate = read_json(out_root / "aggregate_report.json")
    if generalizability_result and generalizability_result["status"] == "success":
        repair_log_summary = run_repair_log(out_root)
        repair_log_result = {
            "status": "success" if repair_log_summary["status"] == "valid" else "failure",
            "validation": repair_log_summary,
        }
        deterministic_repair_policy_report = run_policy_report(out_root)
        deterministic_repair_policy_result = {
            "status": "success" if deterministic_repair_policy_report["status"] == "valid" else "failure",
            "validation": deterministic_repair_policy_report,
        }
        paper_artifacts_manifest = generate_paper_artifacts(out_root)
        paper_artifacts_result = {
            "status": "success" if paper_artifacts_manifest["status"] == "valid" else "failure",
            "validation": paper_artifacts_manifest,
        }
        aggregate = read_json(out_root / "aggregate_report.json")
    for result in results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']}: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in semantics_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} scene_semantics: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in agent_role_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} agent_roles: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in knowledge_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} knowledge_synthesis: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in placement_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} agent_placement: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in functionalmlds_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} functionalmlds_assembly: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in handoff_derivation_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} handoff_derivation: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in functionalmlds_v2_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} functionalmlds_v2_assembly: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in materialization_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} project_materialization: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in schema_validation_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} schema_validation: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in functionalmlds_invariant_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} functionalmlds_invariants: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in traceability_metric_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} traceability_metrics: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in placement_metric_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} placement_metrics: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in handoff_metric_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} handoff_metrics: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in evaluation_question_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} evaluation_questions: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in chat_test_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} chat_tests: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in handoff_test_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} handoff_tests: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in answer_grounding_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} answer_grounding: {result['status']} ({errors} errors, {warnings} warnings)")
    for result in stage_completion_results:
        errors = len(result["validation"].get("errors") or [])
        warnings = len(result["validation"].get("warnings") or [])
        print(f"{result['case_id']} stage_completion: {result['status']} ({errors} errors, {warnings} warnings)")
    if cross_case_metric_result:
        errors = len(cross_case_metric_result["validation"].get("errors") or [])
        warnings = len(cross_case_metric_result["validation"].get("warnings") or [])
        print(f"cross_case_metrics: {cross_case_metric_result['status']} ({errors} errors, {warnings} warnings)")
    if generalizability_result:
        errors = len(generalizability_result["validation"].get("errors") or [])
        warnings = len(generalizability_result["validation"].get("warnings") or [])
        print(
            f"generalizability_assessment: {generalizability_result['status']} "
            f"({errors} errors, {warnings} warnings)"
        )
    if paper_artifacts_result:
        errors = len(repair_log_result["validation"].get("errors") or []) if repair_log_result else 0
        warnings = len(repair_log_result["validation"].get("warnings") or []) if repair_log_result else 0
        print(f"repair_log: {repair_log_result['status']} ({errors} errors, {warnings} warnings)")
        errors = len(deterministic_repair_policy_result["validation"].get("errors") or []) if deterministic_repair_policy_result else 0
        warnings = len(deterministic_repair_policy_result["validation"].get("warnings") or []) if deterministic_repair_policy_result else 0
        print(
            f"deterministic_repair_policy: {deterministic_repair_policy_result['status']} "
            f"({errors} errors, {warnings} warnings)"
        )
        errors = len(paper_artifacts_result["validation"].get("errors") or [])
        warnings = len(paper_artifacts_result["validation"].get("warnings") or [])
        print(f"paper_artifacts: {paper_artifacts_result['status']} ({errors} errors, {warnings} warnings)")
    print(f"Aggregate: {aggregate['success_count']}/{aggregate['case_count']} succeeded")
    generalizability_failed = bool(generalizability_result and generalizability_result["status"] != "success")
    repair_log_failed = bool(repair_log_result and repair_log_result["status"] != "success")
    deterministic_repair_policy_failed = bool(
        deterministic_repair_policy_result and deterministic_repair_policy_result["status"] != "success"
    )
    paper_artifacts_failed = bool(paper_artifacts_result and paper_artifacts_result["status"] != "success")
    return (
        0
        if aggregate["failure_count"] == 0
        and not generalizability_failed
        and not repair_log_failed
        and not deterministic_repair_policy_failed
        and not paper_artifacts_failed
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
