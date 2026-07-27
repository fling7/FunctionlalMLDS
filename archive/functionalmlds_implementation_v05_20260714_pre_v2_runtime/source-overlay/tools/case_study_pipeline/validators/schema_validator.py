from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from jsonschema import Draft202012Validator

from ..common import read_json, update_manifest, write_json
from ..project_materializer import DEFAULT_BACKEND_ROOT


SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"


@dataclass(frozen=True)
class ArtifactTarget:
    artifact_id: str
    schema_name: str
    path: Path


def _schema_path(schema_name: str) -> Path:
    return SCHEMA_DIR / schema_name


def _json_path(path: Path) -> Path:
    return Path(path).resolve()


def _format_json_path(error_path: Iterable[Any]) -> str:
    parts = [str(part) for part in error_path]
    return "$" if not parts else "$." + ".".join(parts)


def _load_schema(schema_name: str) -> Dict[str, Any]:
    return read_json(_schema_path(schema_name))


def _validate_payload(*, artifact_id: str, schema_name: str, payload: Any) -> List[str]:
    schema = _load_schema(schema_name)
    validator = Draft202012Validator(schema)
    return [
        f"{artifact_id} {_format_json_path(error.absolute_path)}: {error.message}"
        for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path))
    ]


def _target_report(
    *,
    artifact_id: str,
    schema_name: str,
    path: Optional[Path],
    errors: List[str],
) -> Dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "schema": schema_name,
        "path": str(path) if path is not None else None,
        "status": "valid" if not errors else "invalid",
        "error_count": len(errors),
        "errors": errors,
    }


def _read_artifact(target: ArtifactTarget) -> Any:
    if not target.path.exists():
        raise FileNotFoundError(f"{target.artifact_id} fehlt: {target.path}")
    return read_json(target.path)


def _project_payload(*, case_dir: Path, backend_root: Path) -> tuple[Dict[str, Any], List[Path]]:
    project_dir = backend_root.resolve() / "projects" / case_dir.name
    paths = {
        "project": project_dir / "project.json",
        "agents": project_dir / "agents.json",
        "room_plan": project_dir / "room_plan.json",
        "trace_map": project_dir / "trace_map.json",
    }
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Projektdateien fehlen: {', '.join(missing)}")
    return {name: read_json(path) for name, path in paths.items()}, list(paths.values())


def validate_case_schemas(*, case_dir: Path, backend_root: Path = DEFAULT_BACKEND_ROOT) -> Dict[str, Any]:
    case_dir = case_dir.resolve()
    backend_root = backend_root.resolve()
    targets = [
        ArtifactTarget(
            "normalized_scene",
            "normalized_scene.schema.json",
            case_dir / "intermediate" / "scene_graph.normalized.json",
        ),
        ArtifactTarget(
            "scene_semantics",
            "scene_semantics.schema.json",
            case_dir / "intermediate" / "scene_semantics.json",
        ),
        ArtifactTarget(
            "knowledge",
            "knowledge.schema.json",
            case_dir / "intermediate" / "knowledge.generated.json",
        ),
        ArtifactTarget(
            "functionalmlds_instance",
            "functionalmlds_case_study.schema.json",
            case_dir / "functionalmlds" / "functionalmlds.instance.generated.json",
        ),
    ]

    reports: List[Dict[str, Any]] = []
    errors: List[str] = []
    warning_messages: List[str] = []
    input_paths: List[Path] = []

    for target in targets:
        input_paths.append(target.path)
        try:
            payload = _read_artifact(target)
            target_errors = _validate_payload(
                artifact_id=target.artifact_id,
                schema_name=target.schema_name,
                payload=payload,
            )
        except Exception as exc:
            target_errors = [f"{target.artifact_id}: {exc}"]
        reports.append(
            _target_report(
                artifact_id=target.artifact_id,
                schema_name=target.schema_name,
                path=target.path,
                errors=target_errors,
            )
        )
        errors.extend(target_errors)

    agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    handoff_matrix_path = case_dir / "intermediate" / "handoff_matrix.json"
    input_paths.extend([agent_roles_path, handoff_matrix_path])
    try:
        agent_roles = read_json(agent_roles_path)
        handoff_matrix = read_json(handoff_matrix_path)
        agent_roles_payload = {
            "agents": agent_roles.get("agents") or [],
            "handoffs": handoff_matrix.get("handoffs") or [],
        }
        agent_role_errors = _validate_payload(
            artifact_id="agent_roles",
            schema_name="agent_roles.schema.json",
            payload=agent_roles_payload,
        )
    except Exception as exc:
        agent_role_errors = [f"agent_roles: {exc}"]
    reports.append(
        _target_report(
            artifact_id="agent_roles",
            schema_name="agent_roles.schema.json",
            path=case_dir / "intermediate",
            errors=agent_role_errors,
        )
    )
    errors.extend(agent_role_errors)

    project_paths: List[Path] = []
    try:
        project_payload, project_paths = _project_payload(case_dir=case_dir, backend_root=backend_root)
        project_errors = _validate_payload(
            artifact_id="interactive_agents_project",
            schema_name="interactive_agents_project.schema.json",
            payload=project_payload,
        )
    except Exception as exc:
        project_errors = [f"interactive_agents_project: {exc}"]
    input_paths.extend(project_paths)
    reports.append(
        _target_report(
            artifact_id="interactive_agents_project",
            schema_name="interactive_agents_project.schema.json",
            path=backend_root / "projects" / case_dir.name,
            errors=project_errors,
        )
    )
    errors.extend(project_errors)

    runtime_log_path = case_dir / "runtime_logs" / "events.jsonl"
    runtime_event_count = 0
    if runtime_log_path.exists():
        runtime_schema = "runtime_event.schema.json"
        input_paths.append(runtime_log_path)
        runtime_errors: List[str] = []
        with runtime_log_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                runtime_event_count += 1
                try:
                    event = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    runtime_errors.append(f"runtime_events line {line_number}: invalid JSON: {exc}")
                    continue
                runtime_errors.extend(
                    f"runtime_events line {line_number}: {error}"
                    for error in _validate_payload(
                        artifact_id="runtime_events",
                        schema_name=runtime_schema,
                        payload=event,
                    )
                )
        reports.append(
            _target_report(
                artifact_id="runtime_events",
                schema_name=runtime_schema,
                path=runtime_log_path,
                errors=runtime_errors,
            )
        )
        errors.extend(runtime_errors)
    else:
        warning_messages.append(f"Runtime-Log fehlt: {runtime_log_path}")

    schema_names = sorted({report["schema"] for report in reports})
    output = {
        "case_id": case_dir.name,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warning_messages,
        "metrics": {
            "artifact_count": len(reports),
            "valid_artifact_count": sum(1 for report in reports if report["status"] == "valid"),
            "invalid_artifact_count": sum(1 for report in reports if report["status"] != "valid"),
            "schema_count": len(schema_names),
            "runtime_event_count": runtime_event_count,
        },
        "artifacts": reports,
        "schemas": schema_names,
    }
    return output


def run_schema_validation_for_case(
    case_dir: Path,
    *,
    backend_root: Path = DEFAULT_BACKEND_ROOT,
) -> Dict[str, Any]:
    case_dir = Path(case_dir).resolve()
    backend_root = Path(backend_root).resolve()
    validation = validate_case_schemas(case_dir=case_dir, backend_root=backend_root)
    validation_path = case_dir / "validation" / "schema_validation.json"
    write_json(validation_path, validation)

    input_paths = [
        case_dir / "intermediate" / "scene_graph.normalized.json",
        case_dir / "intermediate" / "scene_semantics.json",
        case_dir / "intermediate" / "agent_roles.generated.json",
        case_dir / "intermediate" / "handoff_matrix.json",
        case_dir / "intermediate" / "knowledge.generated.json",
        case_dir / "functionalmlds" / "functionalmlds.instance.generated.json",
        backend_root / "projects" / case_dir.name / "project.json",
        backend_root / "projects" / case_dir.name / "agents.json",
        backend_root / "projects" / case_dir.name / "room_plan.json",
        backend_root / "projects" / case_dir.name / "trace_map.json",
        case_dir / "runtime_logs" / "events.jsonl",
    ]
    schema_paths = [_schema_path(name) for name in validation["schemas"]]
    update_manifest(
        case_dir,
        stage_id="schema_validation",
        status="success" if validation["status"] == "valid" else "failed",
        input_paths=input_paths + schema_paths,
        output_paths=[validation_path],
        errors=validation["errors"],
        warnings=validation["warnings"],
        metadata=validation["metrics"],
    )
    return {
        "case_id": case_dir.name,
        "status": "success" if validation["status"] == "valid" else "failed",
        "validation": validation,
        "validation_path": str(validation_path),
    }


def run_schema_validation_for_cases(
    case_dirs: Iterable[Path],
    *,
    backend_root: Path = DEFAULT_BACKEND_ROOT,
) -> List[Dict[str, Any]]:
    return [run_schema_validation_for_case(Path(case_dir), backend_root=backend_root) for case_dir in case_dirs]


def _case_dirs_from_root(root: Path) -> List[Path]:
    return sorted([path for path in root.iterdir() if path.is_dir()])


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate FunctionalMLDS case-study artifacts against JSON Schemas.")
    parser.add_argument("--case-dir", type=Path, action="append", help="Case-study directory to validate.")
    parser.add_argument("--case-root", type=Path, help="Root containing multiple case-study directories.")
    parser.add_argument("--backend-root", type=Path, default=DEFAULT_BACKEND_ROOT)
    args = parser.parse_args(argv)

    case_dirs = args.case_dir or []
    if args.case_root:
        case_dirs.extend(_case_dirs_from_root(args.case_root))
    if not case_dirs:
        parser.error("Pass --case-dir or --case-root.")

    results = run_schema_validation_for_cases(case_dirs, backend_root=args.backend_root)
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 0 if all(result["status"] == "success" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
