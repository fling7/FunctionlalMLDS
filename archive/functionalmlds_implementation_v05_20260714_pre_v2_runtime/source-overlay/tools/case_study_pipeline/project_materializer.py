from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from .common import copy_file, read_json, update_manifest, write_json
from .agent_roles import voice_gender_for_voice


DEFAULT_BACKEND_ROOT = Path("InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents")


def _now_ms() -> int:
    return int(time.time() * 1000)


def _copy_kb(src_root: Path, dst_root: Path) -> List[Path]:
    written: List[Path] = []
    if dst_root.exists():
        shutil.rmtree(dst_root)
    for src in src_root.rglob("*.txt"):
        relative = src.relative_to(src_root)
        dst = dst_root / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        written.append(dst)
    return written


def _load_backend_agent_spec(backend_root: Path):
    root = str(backend_root.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    from backend.state import AgentSpec  # type: ignore

    return AgentSpec


def build_trace_map(
    *,
    case_dir: Path,
    project_dir: Path,
    functionalmlds_instance: Dict[str, Any],
    agent_roles: Dict[str, Any],
) -> Dict[str, Any]:
    use_cases = (functionalmlds_instance.get("requirementsModel") or {}).get("useCases") or []
    main_use_case = use_cases[0] if use_cases else {}
    main_scenario = (main_use_case.get("scenarios") or [{}])[0]
    scenario_steps = main_scenario.get("steps") or []
    runtime_bindings = functionalmlds_instance.get("runtimeBindings") or []
    validation_cases = functionalmlds_instance.get("validationCases") or []
    capabilities = functionalmlds_instance.get("capabilities") or []

    agent_refs = []
    generated_agents = functionalmlds_instance.get("agents") or []
    generated_by_source = {agent.get("source_agent_id"): agent for agent in generated_agents if isinstance(agent, dict)}
    for agent in agent_roles.get("agents") or []:
        source_agent_id = str(agent.get("id") or "")
        functional_agent = generated_by_source.get(source_agent_id, {})
        agent_refs.append(
            {
                "agent_id": source_agent_id,
                "functionalmlds_agent_id": functional_agent.get("id"),
                "entity_id": functional_agent.get("entity_id"),
                "plays_actor": functional_agent.get("playsActor") or [],
                "knowledge_tags": agent.get("knowledge_tags") or [],
            }
        )

    runtime_action_refs = []
    for binding in runtime_bindings:
        for action in binding.get("runtimeActions") or []:
            runtime_action_refs.append(
                {
                    "runtime_binding_id": binding.get("id"),
                    "capability_id": binding.get("capability_id"),
                    "runtime_action_id": action.get("id"),
                    "endpoint": action.get("endpoint"),
                    "tool": action.get("tool"),
                    "topic": action.get("topic"),
                }
            )

    return {
        "schema": "functionalmlds_trace_map",
        "case_id": case_dir.name,
        "functionalmlds_path": str(case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"),
        "project_files": {
            "project": str(project_dir / "project.json"),
            "room_plan": str(project_dir / "room_plan.json"),
            "agents": str(project_dir / "agents.json"),
            "kb_root": str(project_dir / "kb"),
        },
        "use_case_id": main_use_case.get("id"),
        "main_scenario_id": main_scenario.get("id"),
        "scenario_steps": [
            {
                "scenario_step_id": step.get("id"),
                "step_number": step.get("stepNumber"),
                "capability_use_ids": step.get("capabilityUseIds") or [],
                "resulting_state_ids": step.get("resultingState") or [],
            }
            for step in scenario_steps
        ],
        "capabilities": [
            {
                "capability_id": capability.get("id"),
                "effect_ids": [effect.get("id") for effect in capability.get("effects") or []],
            }
            for capability in capabilities
        ],
        "runtime_actions": runtime_action_refs,
        "validation_cases": [
            {
                "validation_case_id": validation_case.get("id"),
                "runtime_binding_ids": validation_case.get("runtime_binding_ids") or [],
                "expected_outcome_ids": validation_case.get("expectedOutcome") or [],
            }
            for validation_case in validation_cases
        ],
        "agents": agent_refs,
    }


def materialize_project(
    *,
    case_dir: Path,
    backend_root: Path = DEFAULT_BACKEND_ROOT,
) -> Dict[str, Path]:
    case_dir = case_dir.resolve()
    backend_root = backend_root.resolve()
    project_dir = backend_root / "projects" / case_dir.name
    project_dir.mkdir(parents=True, exist_ok=True)

    source_mlds = case_dir / "input" / "source_mlds.json"
    agent_roles = read_json(case_dir / "intermediate" / "agent_roles.generated.json")
    placements = read_json(case_dir / "intermediate" / "agent_placements.json")
    functionalmlds_path = case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"
    functionalmlds_instance = read_json(functionalmlds_path)
    kb_source = case_dir / "interactive_agents_project" / "kb"

    existing_project = project_dir / "project.json"
    created_ms = _now_ms()
    if existing_project.exists():
        try:
            created_ms = int(read_json(existing_project).get("created_ms") or created_ms)
        except Exception:
            pass

    project_json = {
        "id": case_dir.name,
        "display_name": case_dir.name.replace("_", " ").title(),
        "description": "Generated FunctionalMLDS case-study project for Interactive Agents.",
        "created_ms": created_ms,
        "updated_ms": _now_ms(),
        "generation_mode": "functionalmlds",
        "functionalmlds_trace_path": str(functionalmlds_path),
        "functionalmlds_case_dir": str(case_dir),
        "source_mlds_path": str(source_mlds),
        "metamodelVersion": functionalmlds_instance.get("metamodelVersion") or "",
    }
    placement_by_id = {
        str(placement.get("id")): placement
        for placement in placements.get("agent_placements") or []
        if isinstance(placement, dict)
    }
    agents_out = []
    for agent in agent_roles.get("agents") or []:
        agent_id = str(agent.get("id") or "")
        placement = placement_by_id.get(agent_id, {})
        voice = agent.get("voice") or "alloy"
        voice_gender = agent.get("voice_gender") or voice_gender_for_voice(str(voice))
        agents_out.append(
            {
                "id": agent_id,
                "display_name": agent.get("display_name") or agent_id,
                "persona": agent.get("persona") or "",
                "voice": voice,
                "voice_gender": voice_gender,
                "voice_style": agent.get("voice_style") or "neutral",
                "tts_model": "gpt-4o-mini-tts" if str(agent.get("tts_model") or "").lower() == "standard" else (agent.get("tts_model") or "gpt-4o-mini-tts"),
                "expertise": agent.get("expertise") or [],
                "knowledge_tags": agent.get("knowledge_tags") or [],
                "responsible_zone_ids": agent.get("responsible_zone_ids") or [],
                "grounded_object_ids": agent.get("grounded_object_ids") or [],
                "handoff_targets": agent.get("handoff_targets") or [],
                "preferred_zone_ids": agent.get("responsible_zone_ids") or [],
                "position": (placement.get("position") or {"x": 0.0, "y": 0.0, "z": 0.0}),
                "forward": (placement.get("forward") or {"x": 0.0, "y": 0.0, "z": 1.0}),
                "functionalmlds_agent_ref": agent_id,
            }
        )

    project_path = project_dir / "project.json"
    room_plan_path = project_dir / "room_plan.json"
    agents_path = project_dir / "agents.json"
    trace_map_path = project_dir / "trace_map.json"
    write_json(project_path, project_json)
    copy_file(source_mlds, room_plan_path)
    write_json(agents_path, {"agents": agents_out})
    write_json(
        trace_map_path,
        build_trace_map(
            case_dir=case_dir,
            project_dir=project_dir,
            functionalmlds_instance=functionalmlds_instance,
            agent_roles=agent_roles,
        ),
    )
    written_kb = _copy_kb(kb_source, project_dir / "kb")
    return {
        "project_dir": project_dir,
        "project_json": project_path,
        "room_plan": room_plan_path,
        "agents": agents_path,
        "trace_map": trace_map_path,
        "kb_root": project_dir / "kb",
        "written_kb_count": len(written_kb),
    }


def validate_materialized_project(project_paths: Dict[str, Path], *, case_dir: Path, backend_root: Path = DEFAULT_BACKEND_ROOT) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    project_json_path = project_paths["project_json"]
    room_plan_path = project_paths["room_plan"]
    agents_path = project_paths["agents"]
    trace_map_path = project_paths.get("trace_map")
    kb_root = project_paths["kb_root"]

    for path in (project_json_path, room_plan_path, agents_path, trace_map_path):
        if path is None:
            errors.append("Missing trace_map path in project_paths.")
            continue
        if not path.exists():
            errors.append(f"Missing project file: {path}")
        else:
            try:
                json.loads(path.read_text(encoding="utf-8-sig"))
            except Exception as exc:
                errors.append(f"Invalid JSON in {path}: {exc}")

    project_json = read_json(project_json_path) if project_json_path.exists() else {}
    for field in (
        "id",
        "display_name",
        "description",
        "created_ms",
        "updated_ms",
        "generation_mode",
        "functionalmlds_trace_path",
        "functionalmlds_case_dir",
        "source_mlds_path",
        "metamodelVersion",
    ):
        if field not in project_json:
            errors.append(f"project.json missing field: {field}")
    if project_json.get("generation_mode") != "functionalmlds":
        errors.append("project.json generation_mode must be 'functionalmlds'.")
    for field in ("functionalmlds_trace_path", "functionalmlds_case_dir", "source_mlds_path", "metamodelVersion"):
        if not str(project_json.get(field) or "").strip():
            errors.append(f"project.json field is empty: {field}")

    agents_payload = read_json(agents_path) if agents_path.exists() else {"agents": []}
    agents = agents_payload.get("agents") or []
    if not agents:
        errors.append("agents.json contains no agents.")

    trace_map = read_json(trace_map_path) if trace_map_path is not None and trace_map_path.exists() else {}
    for field in ("schema", "case_id", "functionalmlds_path", "use_case_id", "main_scenario_id", "scenario_steps", "runtime_actions", "validation_cases", "agents"):
        if field not in trace_map:
            errors.append(f"trace_map.json missing field: {field}")
    if trace_map.get("case_id") != case_dir.name:
        errors.append("trace_map.json case_id does not match project/case directory.")
    if not trace_map.get("scenario_steps"):
        errors.append("trace_map.json has no scenario_steps.")
    if not trace_map.get("runtime_actions"):
        errors.append("trace_map.json has no runtime_actions.")
    if not trace_map.get("validation_cases"):
        errors.append("trace_map.json has no validation_cases.")

    try:
        AgentSpec = _load_backend_agent_spec(backend_root)
        for index, agent in enumerate(agents):
            AgentSpec.from_dict(agent, index)
    except Exception as exc:
        errors.append(f"Backend AgentSpec could not load generated agents: {exc}")

    for index, agent in enumerate(agents):
        if str(agent.get("tts_model") or "").lower() == "standard":
            errors.append(f"agents[{index}].tts_model is still 'standard'.")
        for field in (
            "id",
            "display_name",
            "persona",
            "expertise",
            "knowledge_tags",
            "responsible_zone_ids",
            "grounded_object_ids",
            "handoff_targets",
            "preferred_zone_ids",
            "voice",
            "voice_gender",
            "voice_style",
            "tts_model",
        ):
            value = agent.get(field)
            if field in {"expertise", "knowledge_tags", "responsible_zone_ids", "grounded_object_ids", "handoff_targets", "preferred_zone_ids"}:
                if not isinstance(value, list):
                    errors.append(f"agents[{index}].{field} must be a list.")
            elif not str(value or "").strip():
                errors.append(f"agents[{index}].{field} is empty.")
        if not isinstance(agent.get("position"), dict):
            errors.append(f"agents[{index}] has no position object.")
        if not isinstance(agent.get("forward"), dict):
            errors.append(f"agents[{index}] has no forward object.")
        for tag in agent.get("knowledge_tags") or []:
            tag_dir = kb_root / str(tag)
            if not tag_dir.exists():
                errors.append(f"Missing KB folder for tag: {tag}")
            elif not list(tag_dir.glob("*.txt")):
                errors.append(f"KB folder for tag has no text files: {tag}")

    empty_kb_files = [str(path) for path in kb_root.rglob("*.txt") if not path.read_text(encoding="utf-8").strip()]
    if empty_kb_files:
        errors.append("Empty KB files: " + ", ".join(empty_kb_files[:5]))

    return {
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "agent_count": len(agents),
            "kb_file_count": len(list(kb_root.rglob("*.txt"))) if kb_root.exists() else 0,
            "trace_step_count": len(trace_map.get("scenario_steps") or []),
            "trace_runtime_action_count": len(trace_map.get("runtime_actions") or []),
            "trace_validation_case_count": len(trace_map.get("validation_cases") or []),
        },
    }


def run_project_materializer_for_case(case_dir: Path, *, backend_root: Path = DEFAULT_BACKEND_ROOT) -> Dict[str, Any]:
    case_dir = case_dir.resolve()
    backend_root = backend_root.resolve()
    source_mlds = case_dir / "input" / "source_mlds.json"
    agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    placements_path = case_dir / "intermediate" / "agent_placements.json"
    knowledge_path = case_dir / "intermediate" / "knowledge.generated.json"
    functionalmlds_path = case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"
    validation_path = case_dir / "validation" / "project_materialization_validation.json"

    project_paths = materialize_project(case_dir=case_dir, backend_root=backend_root)
    validation = validate_materialized_project(project_paths, case_dir=case_dir, backend_root=backend_root)
    write_json(validation_path, validation)
    status = "success" if validation["status"] == "valid" else "needs_manual_review"
    output_paths = [
        project_paths["project_json"],
        project_paths["room_plan"],
        project_paths["agents"],
        project_paths["trace_map"],
        validation_path,
        *list(project_paths["kb_root"].rglob("*.txt")),
    ]
    update_manifest(
        case_dir,
        stage_id="project_materialization",
        status=status,
        input_paths=[source_mlds, agent_roles_path, placements_path, knowledge_path, functionalmlds_path],
        output_paths=output_paths,
        errors=validation.get("errors"),
        warnings=validation.get("warnings"),
        metadata=validation.get("metrics"),
    )
    return {
        "case_id": case_dir.name,
        "status": status,
        "validation": validation,
        "project_dir": str(project_paths["project_dir"]),
        "validation_path": str(validation_path),
    }
