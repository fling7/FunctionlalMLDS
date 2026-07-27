from __future__ import annotations

"""Deterministic end-to-end acceptance for the Unity/Backend V2 alignment.

The runner is deliberately read-mostly: it reads the seven checked-in case
artifacts and performs project materialization only in a temporary directory.
Its only persistent writes are the requested JSON and German Markdown reports.
Every check returns structured evidence, so a failed run still produces a
complete diagnostic and exits with status 1.
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


# Acceptance must not leave import caches next to production sources.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = ROOT / "tools"
for _import_root in (ROOT, TOOLS_ROOT):
    if str(_import_root) not in sys.path:
        sys.path.insert(0, str(_import_root))

OUTPUT_DIR = ROOT / "output" / "unity_v2_alignment"
DEFAULT_JSON_REPORT = OUTPUT_DIR / "unity_v2_alignment_acceptance.json"
DEFAULT_MARKDOWN_REPORT = OUTPUT_DIR / "unity_v2_alignment_acceptance.md"
DEFAULT_ARCHIVE = ROOT / "archive" / "functionalmlds_implementation_v05_20260714_pre_v2_runtime"
DEFAULT_TASKLIST = OUTPUT_DIR / "unity_v2_implementation_tasklist.md"

BACKEND_ROOT = (
    ROOT
    / "InteractivAgents"
    / "openai_unity_expert_npcs_pycharm"
    / "InteractiveAgents"
)
UNITY_SCRIPT_ROOT = ROOT / "InteractivAgents" / "InteractiveAgents2" / "Assets" / "Scripting"
UNITY_SOURCE_COPY_ROOT = BACKEND_ROOT / "unity_scripts"
V2_SCHEMA = (
    ROOT
    / "tools"
    / "case_study_pipeline"
    / "schemas"
    / "dynamic_functional_mlds_v2_instance.schema.json"
)

V2_INSTANCE_NAME = "functionalmlds.v2.instance.json"
V2_ASSEMBLY_REPORT_NAME = "functionalmlds.v2.assembly_report.json"
V05_INSTANCE_NAME = "functionalmlds.instance.generated.json"
ASSERTION_TYPES = (
    "EventAssertion",
    "GroundingAssertion",
    "OutputAssertion",
    "RelationAssertion",
    "StateAssertion",
)
ACTION_KINDS = ("setup", "chat", "handoff")

# Fixed order is intentional. Discovery would silently accept an eighth or a
# replacement fixture and would make the Golden-v0.5 check weaker.
FIXTURE_RELATIVES = (
    "output/case_studies/bestfit_career_fair",
    "output/case_studies/classroom_dinosaur",
    "output/case_studies/steinpilz_brand_room",
    "output/wizard_functionalmlds/cheese_factory_tradefair_booth_36f00adc",
    "output/wizard_functionalmlds/mldssteinpilz_e2e_1783611970",
    "output/wizard_functionalmlds/mldssteinpilz_probe",
    "output/wizard_functionalmlds/mldssteinpilz_uidiag_abs_repair_1783611709",
)

UNITY_SOURCE_RELATIVES = (
    "QuickAgentManager.cs",
    "FunctionalMldsV2QuickAgentBridge.cs",
    "FunctionalMldsV2/FunctionalMldsV2Assertions.cs",
    "FunctionalMldsV2/FunctionalMldsV2CapabilityDispatcher.cs",
    "FunctionalMldsV2/FunctionalMldsV2Loader.cs",
    "FunctionalMldsV2/FunctionalMldsV2Model.cs",
    "FunctionalMldsV2/FunctionalMldsV2RuntimeContext.cs",
    "FunctionalMldsV2/FunctionalMldsV2RuntimeLogger.cs",
    "FunctionalMldsV2/FunctionalMldsV2ScenarioRunner.cs",
    "FunctionalMldsV2/FunctionalMldsV2ValidationRecorder.cs",
)

UNITY_LOG_DEFAULTS = {
    "compile": OUTPUT_DIR / "unity_final_v2_compile.log",
    "quickbridge": OUTPUT_DIR / "unity_final_v2_smoke.log",
    "native": OUTPUT_DIR / "unity_final_native_v2_smoke.log",
    "real_instance": OUTPUT_DIR / "unity_final_real_instance_smoke.log",
}
UNITY_LOG_MARKERS = {
    "compile": "Batchmode quit successfully invoked - shutting down!",
    "quickbridge": "[FunctionalMldsV2QuickAgentBridgeSmoke] OK",
    "native": "[FunctionalMLDSV2NativeSmoke] OK",
    "real_instance": "[FunctionalMLDSUnitySmoke] OK",
}
UNITY_COMPLETION_MARKER = "Exiting batchmode successfully now!"
UNITY_FATAL_PATTERNS = (
    re.compile(r"error CS\d+", re.IGNORECASE),
    re.compile(r"scripts have compiler errors", re.IGNORECASE),
    re.compile(r"compilation failed", re.IGNORECASE),
    re.compile(r"executeMethod class .* could not be found", re.IGNORECASE),
    re.compile(r"executeMethod method .* could not be found", re.IGNORECASE),
    re.compile(r"Aborting batchmode due to failure", re.IGNORECASE),
)

PYTEST_LOG_DEFAULTS = {
    "tools": OUTPUT_DIR / "pytest_tools_full_final.log",
    "backend": OUTPUT_DIR / "pytest_backend_full_final.log",
}
PYTEST_LOG_MARKERS = {
    "tools": ("85 passed", "58 subtests passed"),
    "backend": ("5 passed", "23 subtests passed"),
}
PYTEST_FATAL_PATTERNS = (
    re.compile(r"\bfailed\b", re.IGNORECASE),
    re.compile(r"\berror(?:s)?\b", re.IGNORECASE),
    re.compile(r"\binterrupted\b", re.IGNORECASE),
)


def _read_log_text(path: Path) -> str:
    payload = path.read_bytes()
    if payload.startswith((b"\xff\xfe", b"\xfe\xff")):
        return payload.decode("utf-16", errors="replace")
    return payload.decode("utf-8-sig", errors="replace")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def workspace_path(path: Path) -> str:
    path = Path(path).resolve()
    try:
        return path.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def _clean_error(error: BaseException | str, temporary_root: Path | None = None) -> str:
    text = str(error).replace(str(ROOT), "<WORKSPACE>")
    if temporary_root is not None:
        text = text.replace(str(temporary_root), "<TEMP>")
    return text


def _result(passed: bool, **details: Any) -> dict[str, Any]:
    return {"status": "pass" if passed else "fail", **details}


def verify_archive(archive_dir: Path = DEFAULT_ARCHIVE) -> dict[str, Any]:
    """Verify manifest contents and the deterministic ZIP plus sidecar."""

    try:
        from archive_functionalmlds_v05 import verify_archive as archive_verifier

        evidence = archive_verifier(Path(archive_dir).resolve(), check_sources=False)
        return _result(
            evidence.get("status") == "pass",
            archive=workspace_path(archive_dir),
            manifest_entries=evidence.get("manifestEntries"),
            manifested_bytes=evidence.get("manifestedBytes"),
            fixture_count=evidence.get("fixtureCount"),
            zip=evidence.get("zip"),
            zip_sha256=evidence.get("zipSHA256"),
            secret_findings=evidence.get("secretFindings"),
        )
    except Exception as exc:
        return _result(False, archive=workspace_path(archive_dir), errors=[_clean_error(exc)])


def verify_golden_v05_fixtures(archive_dir: Path = DEFAULT_ARCHIVE) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for case_relative in FIXTURE_RELATIVES:
        current = ROOT / case_relative / "functionalmlds" / V05_INSTANCE_NAME
        archived = Path(archive_dir) / "fixtures" / case_relative / "functionalmlds" / V05_INSTANCE_NAME
        current_hash = sha256(current) if current.is_file() else None
        archive_hash = sha256(archived) if archived.is_file() else None
        byte_equal = (
            current.is_file()
            and archived.is_file()
            and current.stat().st_size == archived.stat().st_size
            and current.read_bytes() == archived.read_bytes()
        )
        cases.append(
            {
                "case_id": Path(case_relative).name,
                "current": workspace_path(current),
                "archived": workspace_path(archived),
                "current_sha256": current_hash,
                "archive_sha256": archive_hash,
                "byte_equal": byte_equal,
            }
        )
    passed = len(cases) == 7 and all(item["byte_equal"] for item in cases)
    return _result(passed, expected_case_count=7, case_count=len(cases), cases=cases)


def verify_existing_v2_artifacts(schema_path: Path = V2_SCHEMA) -> dict[str, Any]:
    try:
        from jsonschema import Draft202012Validator
        from dynamic_functional_mlds_v2_compat import import_v05, structural_sha256
    except Exception as exc:
        return _result(False, schema=workspace_path(schema_path), errors=[_clean_error(exc)])

    try:
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8-sig"))
        validator = Draft202012Validator(schema)
    except Exception as exc:
        return _result(False, schema=workspace_path(schema_path), errors=[_clean_error(exc)])

    cases: list[dict[str, Any]] = []
    for case_relative in FIXTURE_RELATIVES:
        case_dir = ROOT / case_relative
        model_path = case_dir / "functionalmlds" / V2_INSTANCE_NAME
        report_path = case_dir / "functionalmlds" / V2_ASSEMBLY_REPORT_NAME
        v05_path = case_dir / "functionalmlds" / V05_INSTANCE_NAME
        errors: list[str] = []
        assertion_counts: dict[str, int] = {name: 0 for name in ASSERTION_TYPES}
        object_count = 0
        model_sha: str | None = None
        report_status: str | None = None
        if not model_path.is_file():
            errors.append(f"Fehlende V2-Instanz: {workspace_path(model_path)}")
        if not report_path.is_file():
            errors.append(f"Fehlender Assembly-Report: {workspace_path(report_path)}")
        if errors:
            cases.append(
                {
                    "case_id": case_dir.name,
                    "model": workspace_path(model_path),
                    "assembly_report": workspace_path(report_path),
                    "status": "fail",
                    "errors": errors,
                }
            )
            continue

        try:
            instance = json.loads(model_path.read_text(encoding="utf-8-sig"))
            report = json.loads(report_path.read_text(encoding="utf-8-sig"))
            model_sha = sha256(model_path)
            schema_errors = sorted(
                validator.iter_errors(instance),
                key=lambda item: (list(item.absolute_path), item.message),
            )
            errors.extend(
                f"JSON-Schema {list(error.absolute_path)}: {error.message}"
                for error in schema_errors
            )
            expected_root = {
                "schema": "dynamic_functional_mlds_v2_instance",
                "metamodelVersion": "2.0.0-model",
                "serializationVersion": "1.0",
                "profile": "executable",
                "fixture_profile": "executable",
                "caseId": case_dir.name,
            }
            for field, expected in expected_root.items():
                if instance.get(field) != expected:
                    errors.append(
                        f"{field} erwartet {expected!r}, gefunden {instance.get(field)!r}."
                    )
            objects = instance.get("objects") if isinstance(instance.get("objects"), list) else []
            object_count = len(objects)
            counts = Counter(
                str(item.get("type"))
                for item in objects
                if isinstance(item, Mapping)
            )
            assertion_counts = {name: counts[name] for name in ASSERTION_TYPES}
            missing_types = [name for name, count in assertion_counts.items() if count < 1]
            if missing_types:
                errors.append("Fehlende Assertion-Typen: " + ", ".join(missing_types))

            report_status = str(report.get("status") or "")
            if (
                report_status != "valid"
                or report.get("ok") is not True
                or report.get("errors")
                or report.get("issues")
            ):
                errors.append("Assembly-Report ist nicht fehlerfrei/valid.")

            v05 = json.loads(v05_path.read_text(encoding="utf-8-sig"))
            semantic = import_v05(v05).get("dynamicFunctionalModel")
            expected_projection_hash = structural_sha256(semantic)
            actual_projection_hash = str(
                (instance.get("sourceContract") or {}).get("semanticProjectionSha256") or ""
            )
            if actual_projection_hash != expected_projection_hash:
                errors.append("sourceContract verweist nicht auf den aktuellen v0.5-Semantikstand.")
        except Exception as exc:
            errors.append(_clean_error(exc))

        cases.append(
            {
                "case_id": case_dir.name,
                "model": workspace_path(model_path),
                "assembly_report": workspace_path(report_path),
                "model_sha256": model_sha,
                "object_count": object_count,
                "profile": "executable",
                "assertion_type_counts": assertion_counts,
                "assembly_report_status": report_status,
                "status": "pass" if not errors else "fail",
                "errors": errors,
            }
        )

    passed = len(cases) == 7 and all(item["status"] == "pass" for item in cases)
    return _result(
        passed,
        schema=workspace_path(schema_path),
        expected_case_count=7,
        case_count=len(cases),
        required_assertion_types=list(ASSERTION_TYPES),
        cases=cases,
    )


def _copy_case_for_acceptance(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("input", "intermediate", "functionalmlds", "interactive_agents_project"):
        source_child = source / name
        if source_child.is_dir():
            shutil.copytree(source_child, destination / name)
    manifest = source / "stage_manifest.json"
    if manifest.is_file():
        shutil.copyfile(manifest, destination / manifest.name)


def verify_temporary_dual_materialization() -> dict[str, Any]:
    """Materialize all cases outside the workspace and load the backend contract."""

    cases: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="functionalmlds-v2-acceptance-") as temp_text:
        temporary_root = Path(temp_text)
        temp_backend = temporary_root / "InteractiveAgents"
        shutil.copytree(BACKEND_ROOT / "backend", temp_backend / "backend")

        try:
            from case_study_pipeline.project_materializer import (
                materialize_project,
                validate_materialized_project,
            )
        except Exception as exc:
            return _result(False, expected_case_count=7, case_count=0, cases=[], errors=[_clean_error(exc)])

        backend_path = str(temp_backend.resolve())
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        for case_relative in FIXTURE_RELATIVES:
            source_case = ROOT / case_relative
            temp_case = temporary_root / "cases" / source_case.name
            errors: list[str] = []
            validation_status: str | None = None
            contract_kind: str | None = None
            action_counts = {kind: 0 for kind in ACTION_KINDS}
            dual_files: dict[str, bool] = {}
            model_sha: str | None = None
            try:
                _copy_case_for_acceptance(source_case, temp_case)
                project_paths = materialize_project(case_dir=temp_case, backend_root=temp_backend)
                validation = validate_materialized_project(
                    project_paths,
                    case_dir=temp_case,
                    backend_root=temp_backend,
                )
                validation_status = str(validation.get("status") or "")
                if validation_status != "valid" or validation.get("errors"):
                    errors.extend(str(item) for item in validation.get("errors") or [])
                    if validation_status != "valid" and not validation.get("errors"):
                        errors.append(f"validate_materialized_project={validation_status!r}")

                from backend.functionalmlds_v2_runtime import load_project_contract  # type: ignore

                contract = load_project_contract(Path(project_paths["project_dir"]))
                contract_kind = str(contract.get("kind") or "")
                if contract_kind != "v2":
                    errors.append(f"load_project_contract lieferte {contract_kind!r} statt 'v2'.")
                actions = (contract.get("runtime_context") or {}).get("runtime_actions") or []
                action_counts = {
                    kind: len(
                        [
                            item
                            for item in actions
                            if isinstance(item, Mapping) and item.get("action_kind") == kind
                        ]
                    )
                    for kind in ACTION_KINDS
                }
                for kind, count in action_counts.items():
                    if count != 1:
                        errors.append(f"Erwartet genau eine {kind}-Action, gefunden {count}.")

                dual_files = {
                    "functionalmlds.v2.instance.json": Path(project_paths["functionalmlds_v2"]).is_file(),
                    "functionalmlds.v05.instance.json": Path(project_paths["functionalmlds_v05"]).is_file(),
                    "trace_map.v2.json": Path(project_paths["trace_map_v2"]).is_file(),
                    "trace_map.v05.json": Path(project_paths["trace_map_v05"]).is_file(),
                }
                if not all(dual_files.values()):
                    errors.append("Die temporäre Projektmaterialisierung ist nicht vollständig dual.")
                model_sha = str(contract.get("model_sha256") or "")
            except Exception as exc:
                errors.append(_clean_error(exc, temporary_root))

            cases.append(
                {
                    "case_id": source_case.name,
                    "status": "pass" if not errors else "fail",
                    "validation_status": validation_status,
                    "contract_kind": contract_kind,
                    "action_kind_counts": action_counts,
                    "dual_files": dual_files,
                    "model_sha256": model_sha,
                    "errors": [_clean_error(item, temporary_root) for item in errors],
                }
            )

    passed = len(cases) == 7 and all(item["status"] == "pass" for item in cases)
    return _result(
        passed,
        execution_scope="isoliertes temporäres Verzeichnis",
        expected_case_count=7,
        case_count=len(cases),
        cases=cases,
    )


def verify_unity_source_copies(
    unity_root: Path = UNITY_SCRIPT_ROOT,
    copy_root: Path = UNITY_SOURCE_COPY_ROOT,
) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for relative in UNITY_SOURCE_RELATIVES:
        unity_path = Path(unity_root) / Path(relative)
        copy_path = Path(copy_root) / Path(relative)
        unity_hash = sha256(unity_path) if unity_path.is_file() else None
        copy_hash = sha256(copy_path) if copy_path.is_file() else None
        files.append(
            {
                "relative_path": relative,
                "unity_sha256": unity_hash,
                "source_copy_sha256": copy_hash,
                "sha_identical": unity_hash is not None and unity_hash == copy_hash,
            }
        )

    expected_v2 = {
        Path(item).as_posix()
        for item in UNITY_SOURCE_RELATIVES
        if item.startswith("FunctionalMldsV2/")
    }
    unity_v2 = {
        path.relative_to(unity_root).as_posix()
        for path in (Path(unity_root) / "FunctionalMldsV2").glob("*.cs")
    } if (Path(unity_root) / "FunctionalMldsV2").is_dir() else set()
    copy_v2 = {
        path.relative_to(copy_root).as_posix()
        for path in (Path(copy_root) / "FunctionalMldsV2").glob("*.cs")
    } if (Path(copy_root) / "FunctionalMldsV2").is_dir() else set()
    set_match = unity_v2 == expected_v2 == copy_v2
    passed = len(files) == len(UNITY_SOURCE_RELATIVES) and set_match and all(
        item["sha_identical"] for item in files
    )
    return _result(
        passed,
        file_count=len(files),
        expected_file_count=len(UNITY_SOURCE_RELATIVES),
        v2_directory_set_identical=set_match,
        missing_or_extra_unity_v2=sorted(expected_v2.symmetric_difference(unity_v2)),
        missing_or_extra_source_copy_v2=sorted(expected_v2.symmetric_difference(copy_v2)),
        files=files,
    )


def _unity_log_ready(path: Path, marker: str) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return marker in text and UNITY_COMPLETION_MARKER in text


def wait_for_unity_logs(
    log_paths: Mapping[str, Path],
    *,
    timeout_seconds: float,
    poll_seconds: float = 1.0,
) -> None:
    """Wait before report generation while any required Unity log is incomplete."""

    deadline = time.monotonic() + max(0.0, timeout_seconds)
    while True:
        incomplete = [
            name
            for name, path in log_paths.items()
            if not _unity_log_ready(Path(path), UNITY_LOG_MARKERS[name])
        ]
        if not incomplete or time.monotonic() >= deadline:
            return
        time.sleep(min(max(poll_seconds, 0.05), max(0.05, deadline - time.monotonic())))


def verify_unity_logs(log_paths: Mapping[str, Path]) -> dict[str, Any]:
    logs: list[dict[str, Any]] = []
    expected_names = tuple(UNITY_LOG_DEFAULTS)
    for name in expected_names:
        path = Path(log_paths[name])
        marker = UNITY_LOG_MARKERS[name]
        errors: list[str] = []
        text = ""
        if not path.is_file():
            errors.append("Logdatei fehlt.")
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
            if marker not in text:
                errors.append(f"Erfolgsmarker fehlt: {marker}")
            if UNITY_COMPLETION_MARKER not in text:
                errors.append("Unity-Batchlauf ist nicht nachweislich vollständig beendet.")
            fatal_hits = sorted(
                {match.group(0) for pattern in UNITY_FATAL_PATTERNS for match in pattern.finditer(text)}
            )
            if fatal_hits:
                errors.append("Fatale Unity-/C#-Muster: " + ", ".join(fatal_hits))
        logs.append(
            {
                "kind": name,
                "path": workspace_path(path),
                "sha256": sha256(path) if path.is_file() else None,
                "success_marker": marker,
                "marker_found": marker in text,
                "completed": UNITY_COMPLETION_MARKER in text,
                "status": "pass" if not errors else "fail",
                "errors": errors,
            }
        )
    passed = len(logs) == 4 and all(item["status"] == "pass" for item in logs)
    return _result(passed, log_count=len(logs), logs=logs)


def verify_python_test_logs(log_paths: Mapping[str, Path]) -> dict[str, Any]:
    logs: list[dict[str, Any]] = []
    for name, markers in PYTEST_LOG_MARKERS.items():
        path = Path(log_paths.get(name, Path()))
        errors: list[str] = []
        text = ""
        if not path.is_file():
            errors.append("Volltest-Log fehlt.")
        else:
            text = _read_log_text(path)
            missing_markers = [marker for marker in markers if marker not in text]
            if missing_markers:
                errors.append("Erwartete Erfolgsmarker fehlen: " + ", ".join(missing_markers))
            fatal_matches = sorted(
                {
                    match.group(0)
                    for pattern in PYTEST_FATAL_PATTERNS
                    for match in pattern.finditer(text)
                }
            )
            if fatal_matches:
                errors.append("Fehlermarker im Volltest-Log: " + ", ".join(fatal_matches))
        logs.append(
            {
                "kind": name,
                "path": workspace_path(path),
                "sha256": sha256(path) if path.is_file() else None,
                "success_markers": list(markers),
                "markers_found": all(marker in text for marker in markers),
                "status": "pass" if not errors else "fail",
                "errors": errors,
            }
        )
    passed = len(logs) == len(PYTEST_LOG_MARKERS) and all(item["status"] == "pass" for item in logs)
    return _result(passed, log_count=len(logs), logs=logs)


def verify_tasklist(tasklist: Path = DEFAULT_TASKLIST, *, require_closed: bool = False) -> dict[str, Any]:
    tasklist = Path(tasklist)
    if not tasklist.is_file():
        return _result(False, tasklist=workspace_path(tasklist), errors=["Taskliste fehlt."])
    text = tasklist.read_text(encoding="utf-8-sig")
    expected = [f"{number:02d}" for number in range(1, 45)]
    checkbox_entries = re.findall(r"- \[([ xX])\]\s+\*\*UV2-(\d{2})\b", text)
    checkbox_counts = Counter(number for _, number in checkbox_entries)
    # Prose may legitimately refer back to an ID (for example the Definition of
    # Done). The normative task identity is therefore the checkbox entry, not
    # every textual occurrence of the token.
    missing = [f"UV2-{number}" for number in expected if checkbox_counts[number] == 0]
    duplicates = [f"UV2-{number}" for number in expected if checkbox_counts[number] > 1]
    unexpected = [f"UV2-{number}" for number in sorted(checkbox_counts) if number not in expected]
    checkbox_by_id: dict[str, str] = {}
    duplicate_checkboxes: list[str] = []
    for state, number in checkbox_entries:
        identifier = f"UV2-{number}"
        if identifier in checkbox_by_id:
            duplicate_checkboxes.append(identifier)
        checkbox_by_id[identifier] = state
    missing_checkboxes = [f"UV2-{number}" for number in expected if f"UV2-{number}" not in checkbox_by_id]
    open_ids = [
        identifier
        for identifier in (f"UV2-{number}" for number in expected)
        if checkbox_by_id.get(identifier, " ").lower() != "x"
    ]
    identifier_complete = not missing and not duplicates and not unexpected
    checkbox_complete = not missing_checkboxes and not duplicate_checkboxes
    passed = identifier_complete and checkbox_complete and (not require_closed or not open_ids)
    return _result(
        passed,
        tasklist=workspace_path(tasklist),
        expected_id_count=44,
        unique_id_count=len(checkbox_counts),
        checkbox_count=len(checkbox_entries),
        identifiers_complete=identifier_complete,
        checkboxes_complete=checkbox_complete,
        require_closed=require_closed,
        closed_count=44 - len(open_ids),
        missing_ids=missing,
        duplicate_ids=duplicates,
        unexpected_ids=unexpected,
        missing_checkboxes=missing_checkboxes,
        duplicate_checkboxes=sorted(set(duplicate_checkboxes)),
        open_ids=open_ids,
    )


def _run_check(check_id: str, title: str, callback: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        evidence = callback()
    except Exception as exc:  # Last-resort isolation: later checks must still run.
        evidence = _result(False, errors=[_clean_error(exc)])
    return {"check_id": check_id, "title": title, **evidence}


def build_report(
    *,
    archive_dir: Path,
    tasklist: Path,
    log_paths: Mapping[str, Path],
    pytest_log_paths: Mapping[str, Path],
    require_closed_tasklist: bool,
) -> dict[str, Any]:
    checks = [
        _run_check("UV2-A01", "v0.5-Archiv: Manifest und deterministisches ZIP", lambda: verify_archive(archive_dir)),
        _run_check("UV2-A02", "Sieben Golden-v0.5-Fixtures bytegleich zum Archiv", lambda: verify_golden_v05_fixtures(archive_dir)),
        _run_check("UV2-A03", "Vorhandene V2-Instanzen, Reports, Schema und Assertions", verify_existing_v2_artifacts),
        _run_check("UV2-A04", "Temporäre duale Materialisierung und Backend-Vertrag", verify_temporary_dual_materialization),
        _run_check("UV2-A05", "Unity-Projektquellen und Backend-Quellkopien SHA-identisch", verify_unity_source_copies),
        _run_check("UV2-A06", "Finale Unity-Compile-/Smoke-Logs", lambda: verify_unity_logs(log_paths)),
        _run_check("UV2-A07", "Vollständige Tools- und Backend-Python-Testläufe", lambda: verify_python_test_logs(pytest_log_paths)),
        _run_check(
            "UV2-A08",
            "Tasklisten-ID- und Checkbox-Vollständigkeit",
            lambda: verify_tasklist(tasklist, require_closed=require_closed_tasklist),
        ),
    ]
    passed = all(check.get("status") == "pass" for check in checks)
    return {
        "schema": "functionalmlds_unity_v2_alignment_acceptance",
        "schema_version": "1.0",
        "status": "pass" if passed else "fail",
        "summary": {
            "check_count": len(checks),
            "passed": sum(check.get("status") == "pass" for check in checks),
            "failed": sum(check.get("status") != "pass" for check in checks),
            "fixture_count": 7,
        },
        "checks": checks,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    passed = report.get("status") == "pass"
    lines = [
        "# Gesamtabnahme Unity/Backend – Dynamic Functional MLDS V2",
        "",
        f"Gesamtstatus: **{'BESTANDEN' if passed else 'NICHT BESTANDEN'}**",
        "",
        "Die Abnahme verändert keine Produktionsartefakte. Alle sieben dualen",
        "Projektmaterialisierungen wurden in einem isolierten temporären Verzeichnis ausgeführt.",
        "",
        "## Prüfergebnisse",
        "",
        "| ID | Prüfung | Status |",
        "|---|---|---|",
    ]
    for check in report.get("checks") or []:
        status = "BESTANDEN" if check.get("status") == "pass" else "FEHLER"
        lines.append(f"| {check.get('check_id')} | {check.get('title')} | **{status}** |")

    failures = [check for check in report.get("checks") or [] if check.get("status") != "pass"]
    if failures:
        lines.extend(["", "## Fehlerdetails", ""])
        for check in failures:
            lines.append(f"### {check.get('check_id')} – {check.get('title')}")
            lines.append("")
            direct_errors = list(check.get("errors") or [])
            nested_errors: list[str] = []
            for key in ("cases", "logs", "files"):
                for item in check.get(key) or []:
                    if isinstance(item, Mapping) and item.get("status") == "fail":
                        label = item.get("case_id") or item.get("kind") or item.get("relative_path") or key
                        for error in item.get("errors") or []:
                            nested_errors.append(f"{label}: {error}")
            for error in direct_errors + nested_errors:
                lines.append(f"- {error}")
            if not direct_errors and not nested_errors:
                lines.append("- Siehe strukturierten JSON-Nachweis für die abweichenden Felder.")
            lines.append("")

    lines.extend(
        [
            "## Abnahmekriterien",
            "",
            "- Archiv-Manifest und deterministisches ZIP sind unverändert verifizierbar.",
            "- Alle sieben v0.5-Golden-Fixtures sind bytegleich zur Archivfassung.",
            "- Alle sieben V2-Instanzen sind schema- und profilkonform und enthalten fünf Assertion-Arten.",
            "- Alle sieben Projekte sind dual materialisierbar und als V2-Backendvertrag ladbar.",
            "- Setup, Chat und Handoff sind je Projekt jeweils genau einmal modelliert.",
            "- Die Unity-Produktionsquellen und ihre Backend-Quellkopien sind SHA-identisch.",
            "- Compile-, QuickBridge-, Native- und Real-Instance-Smoke sind vollständig erfolgreich.",
            "- Die vollständigen Tools- und Backend-Python-Testläufe sind erfolgreich.",
            "- Die Taskliste enthält UV2-01 bis UV2-44 vollständig und eindeutig.",
            "",
        ]
    )
    return "\n".join(lines)


def write_reports(report: Mapping[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path = Path(json_path)
    markdown_path = Path(markdown_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gesamtabnahme der FunctionalMLDS-V2-Unity-Ausrichtung")
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--tasklist", type=Path, default=DEFAULT_TASKLIST)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--markdown-report", type=Path, default=DEFAULT_MARKDOWN_REPORT)
    parser.add_argument("--unity-compile-log", type=Path, default=UNITY_LOG_DEFAULTS["compile"])
    parser.add_argument("--unity-quickbridge-log", type=Path, default=UNITY_LOG_DEFAULTS["quickbridge"])
    parser.add_argument("--unity-native-log", type=Path, default=UNITY_LOG_DEFAULTS["native"])
    parser.add_argument("--unity-real-instance-log", type=Path, default=UNITY_LOG_DEFAULTS["real_instance"])
    parser.add_argument("--pytest-tools-log", type=Path, default=PYTEST_LOG_DEFAULTS["tools"])
    parser.add_argument("--pytest-backend-log", type=Path, default=PYTEST_LOG_DEFAULTS["backend"])
    parser.add_argument(
        "--log-wait-seconds",
        type=float,
        default=0.0,
        help="Vor der Report-Erzeugung auf noch laufende Unity-Logs warten.",
    )
    parser.add_argument(
        "--require-closed-tasklist",
        action="store_true",
        help="Zusätzlich zu vollständigen IDs müssen alle 44 Checkboxen geschlossen sein.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    log_paths = {
        "compile": args.unity_compile_log,
        "quickbridge": args.unity_quickbridge_log,
        "native": args.unity_native_log,
        "real_instance": args.unity_real_instance_log,
    }
    pytest_log_paths = {
        "tools": args.pytest_tools_log,
        "backend": args.pytest_backend_log,
    }
    wait_for_unity_logs(log_paths, timeout_seconds=args.log_wait_seconds)
    report = build_report(
        archive_dir=args.archive,
        tasklist=args.tasklist,
        log_paths=log_paths,
        pytest_log_paths=pytest_log_paths,
        require_closed_tasklist=args.require_closed_tasklist,
    )
    write_reports(report, args.json_report, args.markdown_report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "json_report": str(Path(args.json_report).resolve()),
                "markdown_report": str(Path(args.markdown_report).resolve()),
                **report["summary"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
