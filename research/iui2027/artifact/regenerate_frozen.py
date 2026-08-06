#!/usr/bin/env python3
"""Regenerate the three IUI case-study projects without an API or network.

The checked-in scene semantics, normalized agent roles and knowledge documents
are treated as immutable inputs.  Every generated artifact is first produced
and validated in a temporary workspace.  ``--check`` discards that workspace;
``--write`` publishes the validated files with rollback support.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
import socket
import sys
import tempfile
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from unittest.mock import patch


sys.dont_write_bytecode = True

ARTIFACT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = ARTIFACT_DIR.parents[2]
CASE_IDS = (
    "bestfit_career_fair",
    "classroom_dinosaur",
    "steinpilz_brand_room",
)
BACKEND_RELATIVE = Path(
    "InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents"
)
SUMMARY_PATH = ARTIFACT_DIR / "regeneration-summary.json"
SUMMARY_SCHEMA = "iui2027_frozen_regeneration"
SUMMARY_SCHEMA_VERSION = "1.0"

FROZEN_CASE_FILES = (
    "input/source_mlds.json",
    "input/source_mlds.sha256",
    "intermediate/scene_graph.normalized.json",
    "intermediate/scene_semantics.json",
    "intermediate/agent_roles.generated.json",
    "intermediate/knowledge.generated.json",
)
OPTIONAL_SEED_FILES = (
    "intermediate/object_group_summary.json",
    "intermediate/agent_placements.json",
    "stage_manifest.json",
)
PUBLISHED_CASE_FILES = (
    "stage_manifest.json",
    "intermediate/agent_placements.json",
    "intermediate/handoff_matrix.json",
    "functionalmlds/functionalmlds.instance.generated.json",
    "functionalmlds/functionalmlds.v2.instance.json",
    "functionalmlds/functionalmlds.v2.assembly_report.json",
    "validation/agent_placement_validation.json",
    "validation/functionalmlds_invariant_validation.json",
    "validation/handoff_derivation_validation.json",
    "validation/project_materialization_validation.json",
    "validation/schema_validation.json",
    "validation/functionalmlds_invariants_validation.json",
)
PUBLISHED_CASE_DIRECTORIES = ("interactive_agents_project/kb",)
REGENERATED_STAGE_IDS = {
    "agent_placement",
    "functionalmlds_assembly",
    "handoff_derivation",
    "functionalmlds_v2_assembly",
    "project_materialization",
    "schema_validation",
    "functionalmlds_invariants",
}


class RegenerationError(RuntimeError):
    """Expected fail-closed regeneration error."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(
        (candidate for candidate in root.rglob("*") if candidate.is_file()),
        key=lambda candidate: candidate.relative_to(root).as_posix(),
    ):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(bytes.fromhex(_sha256_file(path)))
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise RegenerationError(f"{path.name} must contain a JSON object.")
    return payload


def _atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _safe_error(value: object, *private_roots: Path) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ")
    roots = [REPOSITORY_ROOT, Path.home(), *private_roots]
    candidates: set[str] = set()
    for root in roots:
        try:
            resolved = str(root.resolve())
        except Exception:
            resolved = str(root)
        candidates.update((resolved, resolved.replace("\\", "/")))
    for candidate in sorted(candidates, key=len, reverse=True):
        if candidate:
            text = text.replace(candidate, "<workspace>")
    text = re.sub(
        r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "<email>",
        text,
    )
    text = " ".join(text.split())
    return text[:800]


def _blocked_network(*_args: Any, **_kwargs: Any) -> None:
    raise RegenerationError("Network access is disabled for frozen regeneration.")


@contextlib.contextmanager
def network_disabled() -> Iterable[None]:
    """Fail immediately if a dependency unexpectedly attempts network I/O."""

    with contextlib.ExitStack() as stack:
        stack.enter_context(
            patch.object(socket.socket, "connect", side_effect=_blocked_network)
        )
        stack.enter_context(
            patch.object(socket.socket, "connect_ex", side_effect=_blocked_network)
        )
        stack.enter_context(
            patch("socket.create_connection", side_effect=_blocked_network)
        )
        stack.enter_context(
            patch.object(urllib.request, "urlopen", side_effect=_blocked_network)
        )
        yield


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise RegenerationError(f"Missing {label}: {path.name}")


def _verify_source_hash(case_dir: Path) -> str:
    source = case_dir / "input" / "source_mlds.json"
    manifest = case_dir / "input" / "source_mlds.sha256"
    _require_file(source, "source MLDS")
    _require_file(manifest, "source hash manifest")
    expected = manifest.read_text(encoding="ascii").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise RegenerationError(
            f"{case_dir.name} has an invalid source hash manifest."
        )
    actual = _sha256_file(source)
    if actual != expected:
        raise RegenerationError(
            f"{case_dir.name} source hash does not match its manifest."
        )
    return actual


def _copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _copy_case_inputs(source: Path, target: Path) -> None:
    for relative in FROZEN_CASE_FILES:
        input_path = source / relative
        _require_file(input_path, f"frozen case input {relative}")
        _copy_file(input_path, target / relative)
    for relative in OPTIONAL_SEED_FILES:
        input_path = source / relative
        if input_path.is_file():
            _copy_file(input_path, target / relative)


def _copy_backend_code(source: Path, target: Path) -> None:
    backend_source = source / "backend"
    _require_file(backend_source / "__init__.py", "backend Python package")
    shutil.copytree(
        backend_source,
        target / "backend",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )
    for case_id in CASE_IDS:
        current_project = source / "projects" / case_id / "project.json"
        if current_project.is_file():
            _copy_file(
                current_project,
                target / "projects" / case_id / "project.json",
            )


def _handoff_pairs_from_agents(roles: Mapping[str, Any]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for agent in roles.get("agents") or []:
        if not isinstance(agent, Mapping):
            continue
        source = str(agent.get("id") or "").strip()
        for raw_target in agent.get("handoff_targets") or []:
            target = str(raw_target or "").strip()
            if source and target:
                pairs.add((source, target))
    return pairs


def _handoff_pairs_from_declarations(
    roles: Mapping[str, Any],
) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    declarations = roles.get("handoffs")
    if not isinstance(declarations, list):
        raise RegenerationError(
            "Frozen agent roles must retain the normalized handoffs array."
        )
    for declaration in declarations:
        if not isinstance(declaration, Mapping):
            continue
        source = str(declaration.get("source_agent_id") or "").strip()
        target = str(declaration.get("target_agent_id") or "").strip()
        if source and target:
            pairs.add((source, target))
    return pairs


def _validate_frozen_inputs(case_dir: Path) -> dict[str, Any]:
    from tools.case_study_pipeline.agent_roles import validate_agent_roles
    from tools.case_study_pipeline.knowledge_synthesis import (
        materialize_knowledge_files,
        validate_knowledge,
    )

    normalized = _read_json(
        case_dir / "intermediate" / "scene_graph.normalized.json"
    )
    semantics = _read_json(case_dir / "intermediate" / "scene_semantics.json")
    roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    knowledge_path = case_dir / "intermediate" / "knowledge.generated.json"
    roles = _read_json(roles_path)
    knowledge = _read_json(knowledge_path)

    role_validation = validate_agent_roles(
        roles,
        scene_semantics=semantics,
        normalized_scene=normalized,
    )
    if role_validation.get("status") != "valid":
        raise RegenerationError(
            "Frozen agent roles are invalid: "
            + "; ".join(str(item) for item in role_validation.get("errors") or [])
        )
    target_pairs = _handoff_pairs_from_agents(roles)
    declaration_pairs = _handoff_pairs_from_declarations(roles)
    if target_pairs != declaration_pairs:
        raise RegenerationError(
            "Frozen role handoffs do not exactly match the agents' handoff targets."
        )

    knowledge_validation = validate_knowledge(
        knowledge,
        normalized_scene=normalized,
        agent_roles=roles,
    )
    if knowledge_validation.get("status") != "valid":
        raise RegenerationError(
            "Frozen knowledge is invalid: "
            + "; ".join(
                str(item) for item in knowledge_validation.get("errors") or []
            )
        )

    kb_root = case_dir / "interactive_agents_project" / "kb"
    if kb_root.exists():
        shutil.rmtree(kb_root)
    written = materialize_knowledge_files(case_dir, knowledge)
    if len(written) != len(knowledge.get("knowledge_entries") or []):
        raise RegenerationError("Not every frozen knowledge entry was materialized.")

    return {
        "status": "valid",
        "source_sha256": _verify_source_hash(case_dir),
        "scene_semantics_sha256": _sha256_file(
            case_dir / "intermediate" / "scene_semantics.json"
        ),
        "agent_roles_sha256": _sha256_file(roles_path),
        "knowledge_sha256": _sha256_file(knowledge_path),
        "agent_count": len(roles.get("agents") or []),
        "handoff_count": len(declaration_pairs),
        "knowledge_entry_count": len(knowledge.get("knowledge_entries") or []),
    }


def _stage_record(
    stage_id: str,
    result: Mapping[str, Any],
    *,
    action: str | None = None,
) -> dict[str, Any]:
    validation = result.get("validation")
    if not isinstance(validation, Mapping):
        validation = {}
    record: dict[str, Any] = {
        "id": stage_id,
        "status": str(result.get("status") or ""),
        "validation_status": str(validation.get("status") or ""),
        "metrics": dict(validation.get("metrics") or {}),
    }
    if action:
        record["action"] = action
    return record


def _require_success(stage_id: str, result: Mapping[str, Any]) -> None:
    status = str(result.get("status") or "").lower()
    validation = result.get("validation")
    validation_status = (
        str(validation.get("status") or "").lower()
        if isinstance(validation, Mapping)
        else ""
    )
    if status not in {"success", "reused"} or validation_status != "valid":
        errors = (
            list(validation.get("errors") or [])
            if isinstance(validation, Mapping)
            else []
        )
        detail = "; ".join(str(item) for item in errors[:8]) or status
        raise RegenerationError(f"{stage_id} failed: {detail}")


def _placement_stage(case_dir: Path) -> tuple[dict[str, Any], str]:
    from tools.case_study_pipeline.agent_placement import (
        run_agent_placement_for_case,
        validate_agent_placements,
    )
    from tools.case_study_pipeline.common import (
        read_json,
        update_manifest,
        write_json,
    )

    normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
    semantics_path = case_dir / "intermediate" / "scene_semantics.json"
    roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    placements_path = case_dir / "intermediate" / "agent_placements.json"
    validation_path = case_dir / "validation" / "agent_placement_validation.json"
    if placements_path.is_file():
        validation = validate_agent_placements(
            read_json(placements_path),
            normalized_scene=read_json(normalized_path),
            agent_roles=read_json(roles_path),
        )
        if validation.get("status") == "valid":
            write_json(validation_path, validation)
            update_manifest(
                case_dir,
                stage_id="agent_placement",
                status="success",
                input_paths=[normalized_path, semantics_path, roles_path],
                output_paths=[placements_path, validation_path],
                errors=validation.get("errors"),
                warnings=validation.get("warnings"),
                metadata={
                    **dict(validation.get("metrics") or {}),
                    "frozen_regeneration_action": "reused",
                },
            )
            return {
                "case_id": case_dir.name,
                "status": "reused",
                "validation": validation,
            }, "reused"
    result = run_agent_placement_for_case(case_dir)
    return result, "generated"


def _handoff_stage(case_dir: Path) -> dict[str, Any]:
    """Derive handoffs without changing the frozen role document."""

    from tools.case_study_pipeline.agent_roles import validate_agent_roles
    from tools.case_study_pipeline.common import (
        read_json,
        update_manifest,
        write_json,
    )
    from tools.case_study_pipeline.handoff_derivation import (
        derive_handoff_artifacts,
        validate_handoff_derivation,
    )

    normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
    semantics_path = case_dir / "intermediate" / "scene_semantics.json"
    roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    instance_path = (
        case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"
    )
    handoff_path = case_dir / "intermediate" / "handoff_matrix.json"
    validation_path = case_dir / "validation" / "handoff_derivation_validation.json"

    frozen_roles = read_json(roles_path)
    frozen_roles_hash = _sha256_file(roles_path)
    seed = {"handoffs": list(frozen_roles.get("handoffs") or [])}
    derived = derive_handoff_artifacts(
        agent_roles=frozen_roles,
        functionalmlds_instance=read_json(instance_path),
        existing_handoff_matrix=seed,
    )
    if derived["agent_roles"] != frozen_roles:
        raise RegenerationError(
            "Handoff derivation would mutate the frozen agent-role artifact."
        )
    role_validation = validate_agent_roles(
        frozen_roles,
        scene_semantics=read_json(semantics_path),
        normalized_scene=read_json(normalized_path),
    )
    handoff_validation = validate_handoff_derivation(
        frozen_roles,
        derived["handoff_matrix"],
    )
    errors = [
        *list(role_validation.get("errors") or []),
        *list(handoff_validation.get("errors") or []),
    ]
    warnings = [
        *list(role_validation.get("warnings") or []),
        *list(handoff_validation.get("warnings") or []),
    ]
    validation = {
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            **dict(derived.get("metrics") or {}),
            "role_validation_status": role_validation.get("status"),
            "derivation_validation_status": handoff_validation.get("status"),
            "frozen_role_unchanged": True,
        },
        "role_validation": role_validation,
        "derivation_validation": handoff_validation,
    }
    if errors:
        raise RegenerationError(
            "Handoff derivation is invalid: "
            + "; ".join(str(item) for item in errors[:8])
        )
    write_json(instance_path, derived["functionalmlds_instance"])
    write_json(handoff_path, derived["handoff_matrix"])
    write_json(validation_path, validation)
    if _sha256_file(roles_path) != frozen_roles_hash:
        raise RegenerationError("Frozen agent-role bytes changed unexpectedly.")
    update_manifest(
        case_dir,
        stage_id="handoff_derivation",
        status="success",
        input_paths=[roles_path, instance_path],
        output_paths=[roles_path, instance_path, handoff_path, validation_path],
        errors=errors,
        warnings=warnings,
        metadata=validation["metrics"],
    )
    return {
        "case_id": case_dir.name,
        "status": "success",
        "validation": validation,
    }


def _output_facts(case_dir: Path, backend_root: Path) -> list[dict[str, Any]]:
    paths = [
        (
            "functionalmlds/functionalmlds.instance.generated.json",
            case_dir
            / "functionalmlds"
            / "functionalmlds.instance.generated.json",
        ),
        (
            "functionalmlds/functionalmlds.v2.instance.json",
            case_dir / "functionalmlds" / "functionalmlds.v2.instance.json",
        ),
        (
            "intermediate/agent_placements.json",
            case_dir / "intermediate" / "agent_placements.json",
        ),
        (
            "intermediate/handoff_matrix.json",
            case_dir / "intermediate" / "handoff_matrix.json",
        ),
        (
            "interactive_agents_project/kb",
            case_dir / "interactive_agents_project" / "kb",
        ),
    ]
    facts: list[dict[str, Any]] = []
    for logical_path, path in paths:
        if path.is_file():
            facts.append(
                {"path": logical_path, "kind": "file", "sha256": _sha256_file(path)}
            )
        elif path.is_dir():
            facts.append(
                {"path": logical_path, "kind": "tree", "sha256": _sha256_tree(path)}
            )
        else:
            raise RegenerationError(f"Expected output is missing: {logical_path}")
    project_dir = backend_root / "projects" / case_dir.name
    model_path = project_dir / "functionalmlds.v2.instance.json"
    if not project_dir.is_dir() or not model_path.is_file():
        raise RegenerationError("The materialized backend project is incomplete.")
    facts.append(
        {
            "path": f"backend/projects/{case_dir.name}",
            "kind": "materialized_project",
            "file_count": sum(
                1 for candidate in project_dir.rglob("*") if candidate.is_file()
            ),
            "model_sha256": _sha256_file(model_path),
        }
    )
    return facts


def _semantic_comparison(
    staged: Path,
    target: Path,
    replacements: Sequence[tuple[str, str]],
) -> tuple[bool, bool]:
    """Return exact and path-normalized semantic equality."""

    if staged.suffix.lower() == ".json" and target.suffix.lower() == ".json":
        staged_value = json.loads(staged.read_text(encoding="utf-8-sig"))
        target_value = json.loads(target.read_text(encoding="utf-8-sig"))
        return (
            staged_value == target_value,
            _replace_strings(staged_value, replacements) == target_value,
        )
    staged_text = staged.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    target_text = target.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    return staged_text == target_text, staged_text == target_text


def _comparison_entry(
    *,
    logical_path: str,
    staged: Path,
    target: Path,
    replacements: Sequence[tuple[str, str]],
) -> dict[str, Any]:
    target_exists = target.is_file()
    staged_exists = staged.is_file()
    if not staged_exists or not target_exists:
        return {
            "path": logical_path,
            "staged_exists": staged_exists,
            "target_exists": target_exists,
            "byte_equal": False,
            "semantic_equal": False,
            "path_normalized_semantic_equal": False,
        }
    try:
        semantic_equal, normalized_equal = _semantic_comparison(
            staged,
            target,
            replacements,
        )
        semantic_error = None
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        semantic_equal = False
        normalized_equal = False
        semantic_error = type(exc).__name__
    entry: dict[str, Any] = {
        "path": logical_path,
        "staged_exists": True,
        "target_exists": True,
        "byte_equal": staged.read_bytes() == target.read_bytes(),
        "semantic_equal": semantic_equal,
        "path_normalized_semantic_equal": normalized_equal,
    }
    if semantic_error:
        entry["semantic_comparison_error"] = semantic_error
    return entry


def _target_comparison(
    *,
    staged_case: Path,
    target_case: Path,
    staged_backend_root: Path,
    target_backend_root: Path,
) -> dict[str, Any]:
    staged_project = staged_backend_root / "projects" / staged_case.name
    target_project = target_backend_root / "projects" / target_case.name
    replacements = _publication_replacements(
        staged_case,
        target_case,
        staged_project,
        target_project,
    )
    entries: list[dict[str, Any]] = []
    for relative in PUBLISHED_CASE_FILES:
        entries.append(
            _comparison_entry(
                logical_path=relative,
                staged=staged_case / relative,
                target=target_case / relative,
                replacements=replacements,
            )
        )
    directory_pairs = (
        (
            "interactive_agents_project/kb",
            staged_case / "interactive_agents_project" / "kb",
            target_case / "interactive_agents_project" / "kb",
        ),
        (
            f"backend/projects/{staged_case.name}",
            staged_project,
            target_project,
        ),
    )
    for logical_root, staged_root, target_root in directory_pairs:
        staged_files = {
            path.relative_to(staged_root).as_posix(): path
            for path in staged_root.rglob("*")
            if path.is_file()
        }
        target_files = {
            path.relative_to(target_root).as_posix(): path
            for path in target_root.rglob("*")
            if path.is_file()
        } if target_root.is_dir() else {}
        for relative in sorted(set(staged_files) | set(target_files)):
            entries.append(
                _comparison_entry(
                    logical_path=f"{logical_root}/{relative}",
                    staged=staged_files.get(relative, staged_root / relative),
                    target=target_files.get(relative, target_root / relative),
                    replacements=replacements,
                )
            )
    byte_equal_count = sum(bool(item["byte_equal"]) for item in entries)
    semantic_equal_count = sum(bool(item["semantic_equal"]) for item in entries)
    normalized_equal_count = sum(
        bool(item["path_normalized_semantic_equal"]) for item in entries
    )
    return {
        "artifact_count": len(entries),
        "byte_equal_count": byte_equal_count,
        "semantic_equal_count": semantic_equal_count,
        "path_normalized_semantic_equal_count": normalized_equal_count,
        "all_bytes_equal": byte_equal_count == len(entries),
        "all_semantically_equal": semantic_equal_count == len(entries),
        "all_path_normalized_semantically_equal": (
            normalized_equal_count == len(entries)
        ),
        "artifacts": entries,
    }


def _run_case(case_dir: Path, backend_root: Path) -> dict[str, Any]:
    from tools.case_study_pipeline.functionalmlds_assembler import (
        run_functionalmlds_assembly_for_case,
    )
    from tools.case_study_pipeline.functionalmlds_v2_assembler import (
        run_functionalmlds_v2_assembly_for_case,
    )
    from tools.case_study_pipeline.project_materializer import (
        run_project_materializer_for_case,
    )
    from tools.case_study_pipeline.validators.functionalmlds_invariants import (
        run_functionalmlds_invariant_validation_for_case,
    )
    from tools.case_study_pipeline.validators.schema_validator import (
        run_schema_validation_for_case,
    )

    frozen = _validate_frozen_inputs(case_dir)
    stages: list[dict[str, Any]] = []

    placement, placement_action = _placement_stage(case_dir)
    _require_success("agent_placement", placement)
    stages.append(
        _stage_record(
            "agent_placement",
            placement,
            action=placement_action,
        )
    )

    ordered_operations = (
        ("functionalmlds_assembly", run_functionalmlds_assembly_for_case),
        ("handoff_derivation", _handoff_stage),
        ("functionalmlds_v2_assembly", run_functionalmlds_v2_assembly_for_case),
        (
            "project_materialization",
            lambda path: run_project_materializer_for_case(
                path,
                backend_root=backend_root,
            ),
        ),
        (
            "schema_validation",
            lambda path: run_schema_validation_for_case(
                path,
                backend_root=backend_root,
            ),
        ),
        (
            "functionalmlds_invariants",
            run_functionalmlds_invariant_validation_for_case,
        ),
    )
    for stage_id, operation in ordered_operations:
        result = operation(case_dir)
        _require_success(stage_id, result)
        stages.append(_stage_record(stage_id, result))

    return {
        "case_id": case_dir.name,
        "status": "pass",
        "frozen_inputs": frozen,
        "stages": stages,
        "outputs": _output_facts(case_dir, backend_root),
    }


def _replace_strings(value: Any, replacements: Sequence[tuple[str, str]]) -> Any:
    if isinstance(value, str):
        for old, new in replacements:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [_replace_strings(item, replacements) for item in value]
    if isinstance(value, dict):
        return {
            key: _replace_strings(item, replacements)
            for key, item in value.items()
        }
    return value


def _publication_replacements(
    staged_case: Path,
    final_case: Path,
    staged_project: Path,
    final_project: Path,
) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for old_path, new_path in (
        (staged_case, final_case),
        (staged_project, final_project),
    ):
        old = str(old_path.resolve())
        new = str(new_path.resolve())
        pairs.extend(
            (
                (old, new),
                (old.replace("\\", "/"), new.replace("\\", "/")),
            )
        )
    return sorted(set(pairs), key=lambda item: len(item[0]), reverse=True)


def _rewrite_json_tree(root: Path, replacements: Sequence[tuple[str, str]]) -> None:
    for path in sorted(root.rglob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        rewritten = _replace_strings(payload, replacements)
        if rewritten != payload:
            path.write_text(
                json.dumps(rewritten, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


def _mapped_staged_path(
    final_path: Path,
    *,
    staged_case: Path,
    final_case: Path,
    staged_project: Path,
    final_project: Path,
) -> Path:
    resolved = final_path.resolve()
    for final_root, staged_root in (
        (final_case.resolve(), staged_case.resolve()),
        (final_project.resolve(), staged_project.resolve()),
    ):
        try:
            return staged_root / resolved.relative_to(final_root)
        except ValueError:
            continue
    return resolved


def _refresh_regenerated_manifest_entries(
    manifest_path: Path,
    *,
    staged_case: Path,
    final_case: Path,
    staged_project: Path,
    final_project: Path,
) -> None:
    manifest = _read_json(manifest_path)
    for stage in manifest.get("stages") or []:
        if (
            not isinstance(stage, dict)
            or stage.get("stage_id") not in REGENERATED_STAGE_IDS
        ):
            continue
        for field in ("inputs", "outputs"):
            for entry in stage.get(field) or []:
                if not isinstance(entry, dict) or not entry.get("path"):
                    continue
                staged_path = _mapped_staged_path(
                    Path(str(entry["path"])),
                    staged_case=staged_case,
                    final_case=final_case,
                    staged_project=staged_project,
                    final_project=final_project,
                )
                entry.pop("sha256", None)
                entry.pop("tree_sha256", None)
                if staged_path.is_file():
                    entry["sha256"] = _sha256_file(staged_path)
                elif staged_path.is_dir():
                    entry["tree_sha256"] = _sha256_tree(staged_path)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


class _Publication:
    """Prepare same-parent replacements and roll all of them back on failure."""

    def __init__(self) -> None:
        self._records: list[tuple[Path, Path | None]] = []
        self._prepared: list[tuple[Path, Path]] = []

    def prepare(self, source: Path, target: Path) -> None:
        if not source.exists():
            raise RegenerationError(f"Publication source is missing: {source.name}")
        target.parent.mkdir(parents=True, exist_ok=True)
        incoming = target.parent / f".{target.name}.incoming-{uuid.uuid4().hex}"
        if source.is_dir():
            shutil.copytree(source, incoming)
        else:
            shutil.copy2(source, incoming)
        self._prepared.append((incoming, target))

    def apply(self) -> None:
        for incoming, target in self._prepared:
            backup: Path | None = None
            if target.exists():
                backup = target.parent / f".{target.name}.backup-{uuid.uuid4().hex}"
                os.replace(target, backup)
            try:
                os.replace(incoming, target)
            except Exception:
                if backup is not None and backup.exists():
                    os.replace(backup, target)
                raise
            self._records.append((target, backup))

    def rollback(self) -> None:
        for target, backup in reversed(self._records):
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
            if backup is not None and backup.exists():
                os.replace(backup, target)
        for incoming, _target in self._prepared:
            if incoming.is_dir():
                shutil.rmtree(incoming, ignore_errors=True)
            elif incoming.exists():
                incoming.unlink()
        self._records.clear()

    def commit(self) -> None:
        for _target, backup in self._records:
            if backup is None:
                continue
            if backup.is_dir():
                shutil.rmtree(backup)
            elif backup.exists():
                backup.unlink()
        for incoming, _target in self._prepared:
            if incoming.is_dir():
                shutil.rmtree(incoming, ignore_errors=True)
            elif incoming.exists():
                incoming.unlink()
        self._records.clear()


def _post_publish_validation(
    repository_root: Path,
    backend_root: Path,
) -> None:
    from tools.case_study_pipeline.agent_placement import (
        validate_agent_placements,
    )
    from tools.case_study_pipeline.agent_roles import validate_agent_roles
    from tools.case_study_pipeline.functionalmlds_v2_assembler import (
        validate_functionalmlds_v2_instance,
    )
    from tools.case_study_pipeline.knowledge_synthesis import validate_knowledge
    from tools.case_study_pipeline.validators.functionalmlds_invariants import (
        validate_functionalmlds_invariants,
    )
    from tools.case_study_pipeline.validators.schema_validator import (
        validate_case_schemas,
    )

    for case_id in CASE_IDS:
        case_dir = repository_root / "output" / "case_studies" / case_id
        normalized = _read_json(
            case_dir / "intermediate" / "scene_graph.normalized.json"
        )
        semantics = _read_json(
            case_dir / "intermediate" / "scene_semantics.json"
        )
        roles = _read_json(
            case_dir / "intermediate" / "agent_roles.generated.json"
        )
        checks = (
            validate_agent_roles(
                roles,
                scene_semantics=semantics,
                normalized_scene=normalized,
            ),
            validate_knowledge(
                _read_json(
                    case_dir / "intermediate" / "knowledge.generated.json"
                ),
                normalized_scene=normalized,
                agent_roles=roles,
            ),
            validate_agent_placements(
                _read_json(
                    case_dir / "intermediate" / "agent_placements.json"
                ),
                normalized_scene=normalized,
                agent_roles=roles,
            ),
            validate_functionalmlds_invariants(
                _read_json(
                    case_dir
                    / "functionalmlds"
                    / "functionalmlds.instance.generated.json"
                )
            ),
            validate_functionalmlds_v2_instance(
                _read_json(
                    case_dir
                    / "functionalmlds"
                    / "functionalmlds.v2.instance.json"
                )
            ),
            validate_case_schemas(
                case_dir=case_dir,
                backend_root=backend_root,
            ),
        )
        invalid = [
            check
            for check in checks
            if check.get("status") != "valid"
        ]
        if invalid:
            errors = [
                str(error)
                for check in invalid
                for error in check.get("errors") or []
            ]
            raise RegenerationError(
                f"Post-publication validation failed for {case_id}: "
                + "; ".join(errors[:8])
            )


def _publish(
    repository_root: Path,
    staged_cases_root: Path,
    staged_backend_root: Path,
) -> None:
    final_cases_root = repository_root / "output" / "case_studies"
    final_backend_root = repository_root / BACKEND_RELATIVE

    for case_id in CASE_IDS:
        staged_case = staged_cases_root / case_id
        final_case = final_cases_root / case_id
        staged_project = staged_backend_root / "projects" / case_id
        final_project = final_backend_root / "projects" / case_id
        replacements = _publication_replacements(
            staged_case,
            final_case,
            staged_project,
            final_project,
        )
        _rewrite_json_tree(staged_case, replacements)
        _rewrite_json_tree(staged_project, replacements)
        _refresh_regenerated_manifest_entries(
            staged_case / "stage_manifest.json",
            staged_case=staged_case,
            final_case=final_case,
            staged_project=staged_project,
            final_project=final_project,
        )

    transaction = _Publication()
    try:
        for case_id in CASE_IDS:
            staged_case = staged_cases_root / case_id
            final_case = final_cases_root / case_id
            for relative in PUBLISHED_CASE_FILES:
                transaction.prepare(staged_case / relative, final_case / relative)
            for relative in PUBLISHED_CASE_DIRECTORIES:
                transaction.prepare(staged_case / relative, final_case / relative)
            transaction.prepare(
                staged_backend_root / "projects" / case_id,
                final_backend_root / "projects" / case_id,
            )
        transaction.apply()
        _post_publish_validation(repository_root, final_backend_root)
    except Exception:
        transaction.rollback()
        raise
    transaction.commit()


def regenerate(
    *,
    repository_root: Path = REPOSITORY_ROOT,
    mode: str,
) -> dict[str, Any]:
    """Run a complete temporary regeneration and optionally publish it."""

    if mode not in {"check", "write"}:
        raise ValueError("mode must be 'check' or 'write'")
    repository_root = repository_root.resolve()
    if str(repository_root) not in sys.path:
        sys.path.insert(0, str(repository_root))

    summary: dict[str, Any] = {
        "schema": SUMMARY_SCHEMA,
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "mode": mode,
        "status": "fail",
        "api_calls": 0,
        "network_access": "blocked",
        "frozen_inputs_mutated": False,
        "case_order": list(CASE_IDS),
        "cases": [],
        "published": False,
    }
    with tempfile.TemporaryDirectory(
        prefix="iui2027-frozen-regeneration-"
    ) as temporary_name:
        temporary_root = Path(temporary_name)
        staged_cases_root = temporary_root / "output" / "case_studies"
        staged_backend_root = temporary_root / "backend-root"
        private_roots = (temporary_root,)
        try:
            source_cases_root = repository_root / "output" / "case_studies"
            source_backend_root = repository_root / BACKEND_RELATIVE
            for case_id in CASE_IDS:
                _copy_case_inputs(
                    source_cases_root / case_id,
                    staged_cases_root / case_id,
                )
            _copy_backend_code(source_backend_root, staged_backend_root)

            with network_disabled():
                for case_id in CASE_IDS:
                    staged_case = staged_cases_root / case_id
                    case_summary = _run_case(
                        staged_case,
                        staged_backend_root,
                    )
                    case_summary["target_comparison"] = _target_comparison(
                        staged_case=staged_case,
                        target_case=source_cases_root / case_id,
                        staged_backend_root=staged_backend_root,
                        target_backend_root=source_backend_root,
                    )
                    summary["cases"].append(case_summary)
                if mode == "write":
                    _publish(
                        repository_root,
                        staged_cases_root,
                        staged_backend_root,
                    )
                    summary["published"] = True
            summary["status"] = "pass"
        except Exception as exc:
            summary["error"] = _safe_error(exc, *private_roots)
            summary["status"] = "fail"
    return summary


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate all three IUI fixtures from frozen semantic, role and "
            "knowledge artifacts without an API or network."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--check",
        action="store_true",
        help="Regenerate and validate only in a temporary workspace.",
    )
    mode.add_argument(
        "--write",
        action="store_true",
        help=(
            "Regenerate in a temporary workspace, then transactionally publish "
            "the validated generated artifacts."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    selected_mode = "write" if args.write else "check"
    summary = regenerate(mode=selected_mode)
    if selected_mode == "write":
        _atomic_write_json(SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
