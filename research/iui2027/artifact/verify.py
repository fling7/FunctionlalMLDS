#!/usr/bin/env python3
"""Verify the anonymous, API-free ACM IUI 2027 review artifact.

The default path is deliberately fail-closed.  It does not call a model API,
access the network, or start Unity.  A Unity editor is only launched when an
explicit ``--unity-editor`` path is supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


ARTIFACT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = ARTIFACT_DIR.parents[2]
SUMMARY_PATH = ARTIFACT_DIR / "verification-summary.json"

CASE_IDS = (
    "bestfit_career_fair",
    "classroom_dinosaur",
    "steinpilz_brand_room",
)
CANONICAL_DEMONSTRATOR = "steinpilz_brand_room"
EXPECTED_UNITY_VERSION = "6000.4.5f1"
EXPECTED_UNITY_PACKAGES = {
    "com.de-panther.webxr": "0.23.0",
    "com.de-panther.webxr-interactions": "0.23.0",
    "com.unity.inputsystem": "1.19.0",
    "com.unity.nuget.newtonsoft-json": "3.2.2",
    "com.unity.test-framework": "1.6.0",
    "com.unity.xr.interaction.toolkit": "3.5.0",
}
EXPECTED_UNITY_CLASSES = {
    (
        "InteractivAgents/InteractiveAgents2/Assets/Scripting/"
        "FunctionalMldsSceneObjectBinding.cs"
    ): ("FunctionalMldsSceneObjectBinding",),
    (
        "InteractivAgents/InteractiveAgents2/Assets/Scripting/"
        "FunctionalMldsSceneBindingBootstrapper.cs"
    ): ("FunctionalMldsSceneBindingBootstrapper",),
    (
        "InteractivAgents/InteractiveAgents2/Assets/Scripting/"
        "FunctionalMldsV2/FunctionalMldsV2InteractionEvidence.cs"
    ): ("FunctionalMldsV2InteractionEvidence",),
    (
        "InteractivAgents/InteractiveAgents2/Assets/InteractiveAgents/Editor/"
        "FunctionalMldsSpatialGroundingSmoke.cs"
    ): (
        "FunctionalMldsSpatialGroundingSmoke",
        "RunFromCommandLine",
        "[FunctionalMldsSpatialGroundingSmoke] OK",
    ),
    (
        "InteractivAgents/InteractiveAgents2/Assets/InteractiveAgents/Editor/"
        "FunctionalMldsV2NativeSmoke.cs"
    ): ("FunctionalMldsV2NativeSmoke", "[FunctionalMLDSV2NativeSmoke] OK"),
    (
        "InteractivAgents/InteractiveAgents2/Assets/InteractiveAgents/Editor/"
        "FunctionalMldsV2QuickAgentBridgeSmoke.cs"
    ): (
        "FunctionalMldsV2QuickAgentBridgeSmoke",
        "RunFromCommandLine",
        "[FunctionalMldsV2QuickAgentBridgeSmoke] OK",
    ),
}
UNITY_SMOKES = (
    (
        "FunctionalMldsV2NativeSmoke.Run",
        "[FunctionalMLDSV2NativeSmoke] OK",
    ),
    (
        "FunctionalMldsV2QuickAgentBridgeSmoke.RunFromCommandLine",
        "[FunctionalMldsV2QuickAgentBridgeSmoke] OK",
    ),
    (
        "FunctionalMldsSpatialGroundingSmoke.RunFromCommandLine",
        "[FunctionalMldsSpatialGroundingSmoke] OK",
    ),
)

TEXT_SUFFIXES = {
    ".bib",
    ".cs",
    ".json",
    ".md",
    ".py",
    ".tex",
    ".txt",
}


class VerificationError(RuntimeError):
    """Expected, human-readable verification failure."""


@dataclass
class Check:
    identifier: str
    label: str
    mandatory: bool = True
    status: str = "not_run"
    facts: dict[str, Any] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "label": self.label,
            "mandatory": self.mandatory,
            "status": self.status,
            "facts": self.facts,
            "issues": self.issues,
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def relative_path(path: Path, root: Path = REPOSITORY_ROOT) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise VerificationError("A checked path escapes the repository.") from exc


def safe_text(value: object, root: Path = REPOSITORY_ROOT) -> str:
    """Remove local paths, email addresses and long output from diagnostics."""

    text = str(value).replace("\r", " ").replace("\n", " ")
    candidates = {
        str(root.resolve()),
        str(root.resolve()).replace("\\", "/"),
        str(Path.home()),
        str(Path.home()).replace("\\", "/"),
    }
    for candidate in sorted(candidates, key=len, reverse=True):
        if candidate:
            text = text.replace(candidate, "<repository>")
    text = re.sub(
        r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "<email>",
        text,
    )
    text = re.sub(
        r"(?i)\b[A-Z]:[\\/](?:[^\\/\s]+[\\/])*[^\\/\s]*",
        "<absolute-path>",
        text,
    )
    text = re.sub(
        r"(?<![A-Za-z0-9_.-])/(?:Users|home)/[^\s]+",
        "<absolute-path>",
        text,
    )
    text = " ".join(text.split())
    return text[:600]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def execute_check(check: Check, operation: Callable[[], Mapping[str, Any]]) -> None:
    try:
        check.facts = dict(operation())
        check.status = "pass"
    except Exception as exc:  # Each failed check must still reach the summary.
        check.status = "fail"
        check.issues.append(safe_text(exc))


def check_case_inputs() -> Mapping[str, Any]:
    cases: list[dict[str, Any]] = []
    required_relative_paths = (
        "functionalmlds/functionalmlds.instance.generated.json",
        "functionalmlds/functionalmlds.v2.instance.json",
        "functionalmlds/functionalmlds.v2.assembly_report.json",
        "intermediate/scene_semantics.json",
        "intermediate/agent_roles.generated.json",
        "intermediate/handoff_matrix.json",
    )
    for case_id in CASE_IDS:
        case_dir = REPOSITORY_ROOT / "output" / "case_studies" / case_id
        source = case_dir / "input" / "source_mlds.json"
        manifest = case_dir / "input" / "source_mlds.sha256"
        required = [source, manifest]
        required.extend(case_dir / item for item in required_relative_paths)
        missing = [
            relative_path(path) for path in required if not path.is_file()
        ]
        if missing:
            raise VerificationError(
                f"{case_id} is missing required inputs: {', '.join(missing)}"
            )
        expected = manifest.read_text(encoding="ascii").strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise VerificationError(
                f"{relative_path(manifest)} is not a single SHA-256 digest."
            )
        actual = sha256_file(source)
        if actual != expected:
            raise VerificationError(
                f"{case_id} source hash is stale: expected {expected}, got {actual}."
            )
        cases.append(
            {
                "case_id": case_id,
                "source_sha256": actual,
                "required_input_count": len(required),
            }
        )
    return {
        "case_count": len(cases),
        "canonical_demonstrator": CANONICAL_DEMONSTRATOR,
        "cases": cases,
    }


def check_fresh_v2() -> Mapping[str, Any]:
    if str(REPOSITORY_ROOT) not in sys.path:
        sys.path.insert(0, str(REPOSITORY_ROOT))
    from tools.case_study_pipeline.functionalmlds_v2_assembler import (
        assemble_v2_instance,
        validate_functionalmlds_v2_instance,
    )

    cases: list[dict[str, Any]] = []
    for case_id in CASE_IDS:
        v05_path = (
            REPOSITORY_ROOT
            / "output"
            / "case_studies"
            / case_id
            / "functionalmlds"
            / "functionalmlds.instance.generated.json"
        )
        source = read_json(v05_path)
        first = assemble_v2_instance(source)
        second = assemble_v2_instance(source)
        first_hash = canonical_sha256(first)
        if canonical_sha256(second) != first_hash:
            raise VerificationError(
                f"In-memory V2 assembly is not deterministic for {case_id}."
            )
        report = validate_functionalmlds_v2_instance(first)
        if not report.get("ok") or report.get("status") != "valid":
            codes = sorted(
                {
                    str(issue.get("code") or "unknown")
                    for issue in report.get("errors") or []
                }
            )
            raise VerificationError(
                f"Fresh V2 validation failed for {case_id}: {', '.join(codes)}"
            )
        if first.get("caseId") != case_id:
            raise VerificationError(
                f"Fresh V2 case identity changed for {case_id}."
            )
        cases.append(
            {
                "case_id": case_id,
                "fresh_v2_sha256": first_hash,
                "object_count": len(first.get("objects") or []),
                "validation_status": report["status"],
                "validation_error_count": len(report.get("errors") or []),
            }
        )
    return {"case_count": len(cases), "cases": cases}


def _checked_repository_file(relative: str) -> Path:
    path = (REPOSITORY_ROOT / relative).resolve()
    relative_path(path)
    if not path.is_file():
        raise VerificationError(f"Benchmark input is missing: {relative}")
    return path


def _validate_environment_hashes(environment: Mapping[str, Any]) -> int:
    records: list[Mapping[str, Any]] = []
    records.extend(environment.get("input_files") or [])
    records.extend(environment.get("validator_and_benchmark_sources") or [])
    if not records:
        raise VerificationError("Benchmark environment contains no input hashes.")
    for record in records:
        relative = str(record.get("path") or "")
        expected = str(record.get("sha256") or "").lower()
        if not relative or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise VerificationError("Benchmark environment has an invalid hash record.")
        actual = sha256_file(_checked_repository_file(relative))
        if actual != expected:
            raise VerificationError(
                f"Benchmark input hash is stale for {relative}."
            )
    return len(records)


def _validate_benchmark_payload(
    results: Mapping[str, Any],
    environment: Mapping[str, Any],
) -> Mapping[str, Any]:
    expected_cases = list(CASE_IDS)
    scope = results.get("scope") or {}
    corpus_cases = (results.get("corpus") or {}).get("cases") or []
    actual_cases = [str(item.get("case_id") or "") for item in corpus_cases]
    if results.get("schema") != "iui2027_structural_system_benchmark":
        raise VerificationError("Unexpected IUI benchmark schema.")
    if actual_cases != expected_cases:
        raise VerificationError("IUI benchmark case order or membership is stale.")
    if scope.get("api_calls") != 0 or scope.get("answer_semantics_evaluated"):
        raise VerificationError("Benchmark scope no longer matches the API-free claim.")
    if scope.get("unity_runtime_started"):
        raise VerificationError("Structural benchmark unexpectedly reports starting Unity.")
    comparison = (results.get("direct_wiring_comparison") or {}).get(
        "aggregate"
    ) or {}
    if comparison.get("status") != "comparable":
        raise VerificationError("Direct-Wiring and fresh V2 are not comparable.")
    stale = results.get("checked_in_v2_staleness_audit") or {}
    rejected = int(stale.get("checked_in_rejection_count") or 0)
    if rejected:
        raise VerificationError(
            "Checked-in V2 inputs are stale for "
            f"{rejected}/{len(CASE_IDS)} cases; regenerate them before release."
        )
    if int(stale.get("fresh_regeneration_acceptance_count") or 0) != len(
        CASE_IDS
    ):
        raise VerificationError("Not every fresh V2 regeneration is accepted.")
    runtime_corpus = results.get("runtime_corpus") or {}
    if runtime_corpus.get("status") != "pass":
        raise VerificationError("The fresh-V2 SessionStore runtime corpus failed.")
    if int(runtime_corpus.get("probe_denominator") or 0) != 459:
        raise VerificationError(
            "The fresh-V2 SessionStore runtime corpus is not the full "
            "asset-by-start-Agent matrix."
        )
    if (
        int(runtime_corpus.get("failed_probe_count") or 0) != 0
        or int(runtime_corpus.get("passed_probe_count") or 0) != 459
    ):
        raise VerificationError(
            "The fresh-V2 SessionStore runtime corpus has failed probes."
        )
    if (
        int(runtime_corpus.get("accepted_with_evidence_count") or 0)
        != int(runtime_corpus.get("accepted_probe_denominator") or 0)
    ):
        raise VerificationError(
            "An accepted runtime-corpus probe lacks model evidence."
        )
    if (
        int(runtime_corpus.get("fail_closed_before_stub_count") or 0)
        != int(runtime_corpus.get("rejected_probe_denominator") or 0)
    ):
        raise VerificationError(
            "A rejected runtime-corpus probe was not fail-closed before the stub."
        )
    if (
        runtime_corpus.get("api_calls") != 0
        or not runtime_corpus.get("network_blocked")
        or not runtime_corpus.get(
            "fresh_v2_materialized_equality_verified"
        )
    ):
        raise VerificationError(
            "The runtime-corpus API/network/fresh-materialization contract failed."
        )
    hash_count = _validate_environment_hashes(environment)
    return {
        "schema_version": results.get("schema_version"),
        "case_count": len(corpus_cases),
        "environment_hash_count": hash_count,
        "direct_wiring_comparison_status": comparison["status"],
        "checked_in_v2_rejection_count": rejected,
        "fresh_v2_acceptance_count": stale[
            "fresh_regeneration_acceptance_count"
        ],
        "answer_semantics_evaluated": False,
        "api_calls": 0,
        "runtime_corpus_status": runtime_corpus["status"],
        "runtime_corpus_probe_denominator": runtime_corpus[
            "probe_denominator"
        ],
    }


def check_benchmark(mode: str) -> Mapping[str, Any]:
    evaluation_dir = REPOSITORY_ROOT / "research" / "iui2027" / "evaluation"
    if mode == "run":
        if str(REPOSITORY_ROOT) not in sys.path:
            sys.path.insert(0, str(REPOSITORY_ROOT))
        from research.iui2027.evaluation.run_benchmark import run

        with tempfile.TemporaryDirectory(prefix="iui2027-benchmark-") as name:
            results, environment, _ = run(
                repo_root=REPOSITORY_ROOT,
                output_dir=Path(name),
            )
    else:
        results = read_json(evaluation_dir / "results.json")
        environment = read_json(evaluation_dir / "environment.json")
    facts = dict(_validate_benchmark_payload(results, environment))
    facts["mode"] = mode
    return facts


def run_test_modules(
    modules: Sequence[str],
    *,
    timeout_seconds: int,
) -> Mapping[str, Any]:
    command = [sys.executable, "-m", "unittest", "-q", *modules]
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    if completed.returncode != 0:
        output = (completed.stderr or completed.stdout or "no diagnostic").strip()
        tail = " ".join(output.splitlines()[-8:])
        raise VerificationError(
            f"Test suite failed with exit code {completed.returncode}: {tail}"
        )
    return {
        "module_count": len(modules),
        "modules": list(modules),
        "exit_code": completed.returncode,
    }


def check_materialization_contract(timeout_seconds: int) -> Mapping[str, Any]:
    return run_test_modules(
        ("tools.tests.test_v2_materializer_backend_contract",),
        timeout_seconds=timeout_seconds,
    )


def check_submission_tests(timeout_seconds: int) -> Mapping[str, Any]:
    return run_test_modules(
        (
            "tools.tests.test_iui2027_artifact",
            "tools.tests.test_iui2027_frozen_regeneration",
            "tools.tests.test_iui2027_paper_checker",
            "tools.tests.test_iui2027_reviewer_client",
            "tools.tests.test_iui2027_system_benchmark",
            (
                "InteractivAgents.openai_unity_expert_npcs_pycharm."
                "InteractiveAgents.tests.test_spatial_chat_contract"
            ),
        ),
        timeout_seconds=timeout_seconds,
    )


def check_paper() -> Mapping[str, Any]:
    paper_dir = REPOSITORY_ROOT / "research" / "iui2027" / "paper"
    pdf = paper_dir / "build" / "main.pdf"
    if not pdf.is_file():
        return {
            "pdf_present": False,
            "checker_status": "not_run",
            "reason": "No built PDF is present.",
        }
    completed = subprocess.run(
        [sys.executable, str(paper_dir / "check_submission.py")],
        cwd=paper_dir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        output = (completed.stderr or completed.stdout or "no diagnostic").strip()
        tail = " ".join(output.splitlines()[-8:])
        raise VerificationError(f"Strict paper checker failed: {tail}")
    return {
        "pdf_present": True,
        "pdf_sha256": sha256_file(pdf),
        "pdf_bytes": pdf.stat().st_size,
        "checker_status": "pass",
    }


def check_unity_static() -> Mapping[str, Any]:
    project = REPOSITORY_ROOT / "InteractivAgents" / "InteractiveAgents2"
    version_text = (
        project / "ProjectSettings" / "ProjectVersion.txt"
    ).read_text(encoding="utf-8-sig")
    match = re.search(r"(?m)^m_EditorVersion:\s*(\S+)\s*$", version_text)
    actual_version = match.group(1) if match else ""
    if actual_version != EXPECTED_UNITY_VERSION:
        raise VerificationError(
            f"Expected Unity {EXPECTED_UNITY_VERSION}, found {actual_version or 'none'}."
        )
    manifest = read_json(project / "Packages" / "manifest.json")
    dependencies = manifest.get("dependencies") or {}
    for package, expected_version in EXPECTED_UNITY_PACKAGES.items():
        actual = dependencies.get(package)
        if actual != expected_version:
            raise VerificationError(
                f"Unity package {package} must be {expected_version}, found {actual}."
            )
    for relative, markers in EXPECTED_UNITY_CLASSES.items():
        path = REPOSITORY_ROOT / relative
        if not path.is_file():
            raise VerificationError(f"Expected Unity source is missing: {relative}")
        source = path.read_text(encoding="utf-8-sig")
        missing = [marker for marker in markers if marker not in source]
        if missing:
            raise VerificationError(
                f"Unity source {relative} lacks markers: {', '.join(missing)}"
            )
    return {
        "unity_version": actual_version,
        "required_packages": EXPECTED_UNITY_PACKAGES,
        "class_file_count": len(EXPECTED_UNITY_CLASSES),
        "batch_smoke_count_available": len(UNITY_SMOKES),
    }


def run_unity_smokes(
    editor: Path,
    *,
    timeout_seconds: int,
) -> Mapping[str, Any]:
    editor = editor.expanduser().resolve()
    if not editor.is_file():
        raise VerificationError("The supplied Unity editor does not exist.")
    project = (
        REPOSITORY_ROOT / "InteractivAgents" / "InteractiveAgents2"
    ).resolve()
    runs: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="iui2027-unity-smoke-") as name:
        output_dir = Path(name)
        for index, (method, marker) in enumerate(UNITY_SMOKES, start=1):
            log = output_dir / f"unity-{index}.log"
            environment = os.environ.copy()
            environment["FUNCTIONALMLDS_V2_SMOKE_OUTPUT_DIR"] = str(
                output_dir / "native-output"
            )
            command = [
                str(editor),
                "-batchmode",
                "-nographics",
                "-quit",
                "-projectPath",
                str(project),
                "-executeMethod",
                method,
                "-logFile",
                str(log),
            ]
            completed = subprocess.run(
                command,
                cwd=REPOSITORY_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            log_text = (
                log.read_text(encoding="utf-8", errors="replace")
                if log.is_file()
                else ""
            )
            if completed.returncode != 0 or marker not in log_text:
                raise VerificationError(
                    f"Unity smoke {method} failed or did not emit its OK marker."
                )
            runs.append(
                {
                    "execute_method": method,
                    "exit_code": completed.returncode,
                    "ok_marker_observed": True,
                }
            )
    return {"editor_started": True, "runs": runs}


def iter_release_files() -> Iterable[Path]:
    selected: set[Path] = set()
    roots = (
        REPOSITORY_ROOT / "research" / "iui2027" / "artifact",
        REPOSITORY_ROOT / "research" / "iui2027" / "evaluation",
        REPOSITORY_ROOT / "research" / "iui2027" / "paper",
        REPOSITORY_ROOT / "research" / "iui2027" / "reviewer",
    )
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower() in TEXT_SUFFIXES
                and "build" not in path.parts
                and ".latex-toolchain" not in path.parts
                and "private" not in path.parts
                and path.name != SUMMARY_PATH.name
            ):
                selected.add(path)
    for case_id in CASE_IDS:
        case_dir = (
            REPOSITORY_ROOT / "output" / "case_studies" / case_id
        )
        for child in ("input", "functionalmlds", "intermediate"):
            root = case_dir / child
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                    selected.add(path)
    for relative in EXPECTED_UNITY_CLASSES:
        selected.add(REPOSITORY_ROOT / relative)
    selected.add(
        REPOSITORY_ROOT
        / "InteractivAgents"
        / "InteractiveAgents2"
        / "Packages"
        / "manifest.json"
    )
    selected.add(
        REPOSITORY_ROOT
        / "InteractivAgents"
        / "InteractiveAgents2"
        / "ProjectSettings"
        / "ProjectVersion.txt"
    )
    return sorted(selected, key=lambda item: relative_path(item))


def scan_text(text: str) -> list[str]:
    findings: set[str] = set()
    patterns = {
        "email_address": (
            r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
        ),
        "windows_user_path": r"(?i)\b[A-Z]:[\\/]Users[\\/][^\\/\s]+",
        "posix_user_path": r"(?<![A-Za-z0-9_.-])/(?:Users|home)/[^/\s]+",
        "private_key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "openai_secret": r"\bsk-[A-Za-z0-9_-]{20,}\b",
        "github_secret": r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b",
        "assigned_secret": (
            r"(?i)\b(?:api[_-]?key|password|secret|access[_-]?token)"
            r"\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']"
        ),
    }
    for label, pattern in patterns.items():
        if re.search(pattern, text):
            findings.add(label)
    return sorted(findings)


def check_anonymity() -> Mapping[str, Any]:
    findings: list[dict[str, Any]] = []
    files = list(iter_release_files())
    for path in files:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        labels = scan_text(text)
        if labels:
            findings.append(
                {"path": relative_path(path), "finding_types": labels}
            )
    if findings:
        compact = "; ".join(
            f"{item['path']} ({','.join(item['finding_types'])})"
            for item in findings[:12]
        )
        raise VerificationError(
            f"Anonymous release scan found sensitive material: {compact}"
        )
    return {
        "file_count": len(files),
        "finding_count": 0,
        "scan_scope": "documented anonymous review bundle",
        "patterns": [
            "email_address",
            "local_user_path",
            "private_key",
            "high_confidence_api_or_access_secret",
        ],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify the anonymous API-free IUI 2027 artifact and write an "
            "atomic machine-readable summary."
        )
    )
    parser.add_argument(
        "--benchmark-mode",
        choices=("check", "run"),
        default="check",
        help=(
            "Check the committed benchmark and all recorded hashes (default), "
            "or rerun it in a temporary directory."
        ),
    )
    parser.add_argument(
        "--unity-editor",
        type=Path,
        default=None,
        help="Optional Unity executable; supplying it runs real batch smokes.",
    )
    parser.add_argument(
        "--test-timeout-seconds",
        type=int,
        default=1200,
    )
    parser.add_argument(
        "--unity-timeout-seconds",
        type=int,
        default=900,
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Diagnostic only; skipped mandatory tests make verification fail.",
    )
    parser.add_argument(
        "--skip-paper-check",
        action="store_true",
        help="Skip the optional PDF check even when a PDF is present.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=SUMMARY_PATH,
        help="Summary destination; it must remain inside the repository.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.test_timeout_seconds <= 0 or args.unity_timeout_seconds <= 0:
        raise SystemExit("Timeouts must be positive.")
    summary_path = args.summary.resolve()
    relative_path(summary_path)

    checks: list[Check] = []

    def add(
        identifier: str,
        label: str,
        operation: Callable[[], Mapping[str, Any]],
        *,
        mandatory: bool = True,
    ) -> None:
        check = Check(identifier, label, mandatory=mandatory)
        execute_check(check, operation)
        checks.append(check)

    add("case_inputs", "Case inputs and source hashes", check_case_inputs)
    add("fresh_v2", "Fresh deterministic V2 assembly", check_fresh_v2)
    add(
        "benchmark",
        "IUI structural benchmark",
        lambda: check_benchmark(args.benchmark_mode),
    )

    if args.skip_tests:
        checks.append(
            Check(
                "materialization_contract",
                "Materialization/backend contract tests",
                mandatory=True,
                status="not_run",
                issues=["Mandatory tests were skipped explicitly."],
            )
        )
        checks.append(
            Check(
                "submission_tests",
                "Targeted IUI submission tests",
                mandatory=True,
                status="not_run",
                issues=["Mandatory tests were skipped explicitly."],
            )
        )
    else:
        add(
            "materialization_contract",
            "Materialization/backend contract tests",
            lambda: check_materialization_contract(
                args.test_timeout_seconds
            ),
        )
        add(
            "submission_tests",
            "Targeted IUI submission tests",
            lambda: check_submission_tests(args.test_timeout_seconds),
        )

    add("unity_static", "Unity version, packages and smoke sources", check_unity_static)
    if args.unity_editor is None:
        checks.append(
            Check(
                "unity_batch_smokes",
                "Optional real Unity batch smokes",
                mandatory=False,
                status="not_run",
                facts={"editor_started": False},
                issues=[
                    "No Unity editor was supplied; static Unity checks still ran."
                ],
            )
        )
    else:
        add(
            "unity_batch_smokes",
            "Optional real Unity batch smokes",
            lambda: run_unity_smokes(
                args.unity_editor,
                timeout_seconds=args.unity_timeout_seconds,
            ),
        )

    if args.skip_paper_check:
        checks.append(
            Check(
                "paper",
                "Strict anonymous paper checker",
                mandatory=False,
                status="not_run",
                issues=["Paper check was skipped explicitly."],
            )
        )
    else:
        paper_check = Check(
            "paper",
            "Strict anonymous paper checker",
            mandatory=True,
        )
        execute_check(paper_check, check_paper)
        if (
            paper_check.status == "pass"
            and not paper_check.facts.get("pdf_present")
        ):
            paper_check.mandatory = False
            paper_check.status = "not_run"
        checks.append(paper_check)

    add("anonymity", "Secret, identity and local-path scan", check_anonymity)

    failed = [
        check
        for check in checks
        if check.mandatory and check.status != "pass"
    ]
    summary = {
        "schema": "iui2027_artifact_verification",
        "schema_version": "1.0.0",
        "overall_status": "fail" if failed else "pass",
        "canonical_demonstrator": CANONICAL_DEMONSTRATOR,
        "network_used": False,
        "model_api_used": False,
        "unity_started": args.unity_editor is not None,
        "benchmark_mode": args.benchmark_mode,
        "checks": [check.to_dict() for check in checks],
        "failed_mandatory_check_ids": [
            check.identifier for check in failed
        ],
        "interpretation": (
            "A pass establishes artifact integrity and executable structural "
            "contracts only; it is not evidence of answer quality, usability, "
            "trust, or population-level effects."
        ),
    }
    atomic_write_json(summary_path, summary)

    print(
        json.dumps(
            {
                "overall_status": summary["overall_status"],
                "summary": relative_path(summary_path),
                "failed_mandatory_check_ids": summary[
                    "failed_mandatory_check_ids"
                ],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
