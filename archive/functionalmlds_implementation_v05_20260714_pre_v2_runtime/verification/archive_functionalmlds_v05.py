from __future__ import annotations

"""Create and verify the immutable FunctionalMLDS v0.5 runtime source archive.

The archive is intentionally a small source overlay.  The large, unchanged Unity
assets are reconstructed from the recorded Git/LFS base revision; generated Unity
caches, runtime logs and local credentials are never copied.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.parse
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "archive" / "functionalmlds_implementation_v05_20260714_pre_v2_runtime"
MANIFEST_NAME = "manifest.sha256.csv"
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

UNITY_REPO = ROOT / "InteractivAgents" / "InteractiveAgents2"
BACKEND_REPO = (
    ROOT
    / "InteractivAgents"
    / "openai_unity_expert_npcs_pycharm"
    / "InteractiveAgents"
)

DENIED_DIRECTORY_NAMES = {
    ".git",
    ".idea",
    ".pytest_cache",
    ".vs",
    ".vscode",
    "build",
    "builds",
    "library",
    "logs",
    "memorycaptures",
    "obj",
    "recordings",
    "runtime_logs",
    "temp",
    "usersettings",
    "__pycache__",
}
DENIED_EXACT_FILENAMES = {
    ".env",
    "config.json",
}
DENIED_FILENAME_FRAGMENTS = {
    "api_key",
    "apikey",
    "credential",
    "private_key",
    "secret",
}
DENIED_SUFFIXES = {".pyc", ".pyo"}

# Strong credential signatures only.  Source identifiers such as ``api_key`` are
# allowed; concrete long credential values are not.
SECRET_CONTENT_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\b(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{20,})\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(
        r"(?im)^\s*(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)"
        r"\s*[:=]\s*[\"'](?!<|your[_-]|example|changeme|none|null|\$\{)"
        r"[A-Za-z0-9_./+=:-]{16,}[\"']"
    ),
)


@dataclass(frozen=True)
class Payload:
    source: Path
    archive_path: PurePosixPath
    category: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def workspace_relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def normalized_relative(path: str | PurePosixPath) -> PurePosixPath:
    value = PurePosixPath(str(path).replace("\\", "/"))
    if value.is_absolute() or ".." in value.parts or not value.parts:
        raise ValueError(f"Unsafe relative path: {path}")
    return value


def forbidden_source_path(path: Path | PurePosixPath | str) -> bool:
    value = PurePosixPath(str(path).replace("\\", "/"))
    lowered_parts = [part.lower() for part in value.parts]
    if any(part in DENIED_DIRECTORY_NAMES for part in lowered_parts[:-1]):
        return True
    if not lowered_parts:
        return True
    name = lowered_parts[-1]
    if name in DENIED_EXACT_FILENAMES or name.startswith(".env."):
        return True
    if any(fragment in name for fragment in DENIED_FILENAME_FRAGMENTS):
        return True
    return any(name.endswith(suffix) for suffix in DENIED_SUFFIXES)


def decoded_text(data: bytes) -> str | None:
    if b"\x00" in data[:8192]:
        return None
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    return None


def assert_no_secret_content(data: bytes, label: str) -> None:
    text = decoded_text(data)
    if text is None:
        return
    for pattern in SECRET_CONTENT_PATTERNS:
        if pattern.search(text):
            raise RuntimeError(f"Potential credential content rejected: {label}")


def assert_safe_payload(payload: Payload) -> None:
    source_rel = normalized_relative(workspace_relative(payload.source))
    if forbidden_source_path(source_rel):
        raise RuntimeError(f"Forbidden source path selected: {source_rel}")
    archive_rel = normalized_relative(payload.archive_path)
    if forbidden_source_path(archive_rel):
        raise RuntimeError(f"Forbidden archive path selected: {archive_rel}")
    assert_no_secret_content(payload.source.read_bytes(), source_rel.as_posix())


def add_file(
    payloads: list[Payload],
    source_relative: str,
    archive_relative: str,
    category: str,
) -> None:
    source = ROOT / normalized_relative(source_relative)
    if not source.is_file():
        raise FileNotFoundError(source)
    payloads.append(Payload(source, normalized_relative(archive_relative), category))


def add_tree(
    payloads: list[Payload],
    source_relative: str,
    archive_prefix: str,
    category: str,
) -> None:
    root = ROOT / normalized_relative(source_relative)
    if not root.is_dir():
        raise FileNotFoundError(root)
    for source in sorted(root.rglob("*"), key=lambda item: item.as_posix().casefold()):
        if not source.is_file():
            continue
        rel = normalized_relative(workspace_relative(source))
        if forbidden_source_path(rel):
            continue
        archive_rel = normalized_relative(PurePosixPath(archive_prefix) / rel)
        payloads.append(Payload(source, archive_rel, category))


def selected_payloads() -> list[Payload]:
    payloads: list[Payload] = []

    add_file(
        payloads,
        "tools/generate_dynamic_functional_mlds.py",
        "source-overlay/tools/generate_dynamic_functional_mlds.py",
        "pipeline",
    )
    add_tree(payloads, "tools/case_study_pipeline", "source-overlay", "pipeline")

    backend_base = "InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents"
    add_tree(payloads, f"{backend_base}/backend", "source-overlay", "backend")
    add_tree(payloads, f"{backend_base}/tests", "source-overlay", "backend-tests")
    add_tree(payloads, f"{backend_base}/unity_scripts", "source-overlay", "unity-source-copy")
    add_tree(payloads, f"{backend_base}/examples", "source-overlay", "backend-examples")
    add_tree(payloads, f"{backend_base}/projects", "source-overlay", "backend-projects")
    add_tree(payloads, f"{backend_base}/kb", "source-overlay", "backend-kb")
    backend_readme = ROOT / backend_base / "README.md"
    if backend_readme.is_file():
        add_file(
            payloads,
            f"{backend_base}/README.md",
            f"source-overlay/{backend_base}/README.md",
            "backend",
        )

    unity_base = "InteractivAgents/InteractiveAgents2"
    add_tree(payloads, f"{unity_base}/Assets/Scripting", "source-overlay", "unity")
    add_tree(payloads, f"{unity_base}/Assets/InteractiveAgents", "source-overlay", "unity")
    for relative in (
        f"{unity_base}/Packages/manifest.json",
        f"{unity_base}/Packages/packages-lock.json",
        f"{unity_base}/ProjectSettings/ProjectVersion.txt",
    ):
        add_file(payloads, relative, f"source-overlay/{relative}", "unity-environment")
    for character in ("Ch01", "Ch08", "Ch21", "Ch22", "Ch23"):
        material = f"{unity_base}/Assets/Resources/Characters/Textures/{character}_hair.mat"
        add_file(payloads, material, f"source-overlay/{material}", "unity-dirty-material")
        meta = f"{material}.meta"
        if (ROOT / meta).is_file():
            add_file(payloads, meta, f"source-overlay/{meta}", "unity-dirty-material")

    fixtures = (
        "output/case_studies/bestfit_career_fair/functionalmlds/functionalmlds.instance.generated.json",
        "output/case_studies/classroom_dinosaur/functionalmlds/functionalmlds.instance.generated.json",
        "output/case_studies/steinpilz_brand_room/functionalmlds/functionalmlds.instance.generated.json",
        "output/wizard_functionalmlds/cheese_factory_tradefair_booth_36f00adc/functionalmlds/functionalmlds.instance.generated.json",
        "output/wizard_functionalmlds/mldssteinpilz_e2e_1783611970/functionalmlds/functionalmlds.instance.generated.json",
        "output/wizard_functionalmlds/mldssteinpilz_probe/functionalmlds/functionalmlds.instance.generated.json",
        "output/wizard_functionalmlds/mldssteinpilz_uidiag_abs_repair_1783611709/functionalmlds/functionalmlds.instance.generated.json",
    )
    for fixture in fixtures:
        add_file(payloads, fixture, f"fixtures/{fixture}", "v05-fixture")

    evidence_files = (
        "output/metamodel_v2/evidence/v05_compatibility_mapping.json",
        "output/metamodel_v2/evidence/v05_compatibility_mapping.md",
        "output/metamodel_v2/evidence/v05_field_coverage.json",
        "output/metamodel_v2/evidence/v05_roundtrip_report.json",
        "output/metamodel_v2/evidence/v05_roundtrip_report.md",
        "output/metamodel_v2/evidence/v05_validator_nonregression.json",
        "output/metamodel_v2/evidence/implementation_hash_verification.json",
        "output/metamodel_v2/evidence/snapshot_verification.json",
        "output/metamodel_v2/evidence/acceptance_report.json",
        "output/metamodel_v2/evidence/acceptance_report.md",
    )
    for evidence in evidence_files:
        add_file(payloads, evidence, f"evidence/{Path(evidence).name}", "evidence")
    add_tree(
        payloads,
        "output/metamodel_v2/evidence/v05_projections",
        "evidence",
        "evidence-projections",
    )

    add_file(
        payloads,
        "archive/metamodel_snapshot_20260714_084522_pre_v2.zip",
        "model/metamodel_snapshot_20260714_084522_pre_v2.zip",
        "model",
    )
    add_file(
        payloads,
        "archive/metamodel_snapshot_20260714_084522_pre_v2/manifest.sha256.csv",
        "model/metamodel_snapshot_20260714_084522_pre_v2.manifest.sha256.csv",
        "model",
    )
    add_file(
        payloads,
        "tools/archive_functionalmlds_v05.py",
        "verification/archive_functionalmlds_v05.py",
        "verification",
    )

    archive_paths: set[PurePosixPath] = set()
    source_paths: set[Path] = set()
    for payload in payloads:
        assert_safe_payload(payload)
        if payload.archive_path in archive_paths:
            raise RuntimeError(f"Duplicate archive path: {payload.archive_path}")
        resolved = payload.source.resolve()
        if resolved in source_paths:
            raise RuntimeError(f"Duplicate selected source: {payload.source}")
        archive_paths.add(payload.archive_path)
        source_paths.add(resolved)
    return sorted(payloads, key=lambda item: item.archive_path.as_posix().casefold())


def run_git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    # Preserve the two-column porcelain status prefix.  A generic ``strip``
    # would remove the leading space from the first " worktree modified" row.
    return result.stdout.rstrip("\r\n")


def sanitized_remote_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if not parsed.scheme or not parsed.netloc:
        return url
    hostname = parsed.hostname or ""
    if parsed.port:
        hostname = f"{hostname}:{parsed.port}"
    return urllib.parse.urlunsplit((parsed.scheme, hostname, parsed.path, parsed.query, parsed.fragment))


def git_state(repo: Path) -> tuple[dict[str, object], str]:
    status = run_git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    remote_lines = run_git(repo, "remote", "-v").splitlines()
    remotes: list[dict[str, str]] = []
    for line in remote_lines:
        fields = line.split()
        if len(fields) >= 3:
            remotes.append(
                {
                    "name": fields[0],
                    "url": sanitized_remote_url(fields[1]),
                    "direction": fields[2].strip("()"),
                }
            )
    lines = status.splitlines() if status else []
    counts = Counter("untracked" if line.startswith("??") else "changed" for line in lines)
    state: dict[str, object] = {
        "workspacePath": workspace_relative(repo),
        "head": run_git(repo, "rev-parse", "HEAD"),
        "branch": run_git(repo, "branch", "--show-current"),
        "trackedFileCount": int(run_git(repo, "ls-files").count("\n") + 1),
        "statusEntryCount": len(lines),
        "changedEntryCount": counts["changed"],
        "untrackedEntryCount": counts["untracked"],
        "remotes": sorted(remotes, key=lambda item: (item["name"], item["direction"], item["url"])),
    }
    rendered_status = "\n".join(lines) + ("\n" if lines else "")
    assert_no_secret_content(rendered_status.encode("utf-8"), f"git status for {repo}")
    return state, rendered_status


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_text(path: Path, text: str) -> None:
    write_bytes(path, text.replace("\r\n", "\n").encode("utf-8"))


def json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def sanitized_implementation_baseline() -> tuple[bytes, dict[str, object]]:
    baseline = ROOT / "output" / "metamodel_v2" / "implementation_baseline.sha256.csv"
    with baseline.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    kept: list[dict[str, str]] = []
    excluded: list[str] = []
    for row in rows:
        relative = row["RelativePath"].replace("\\", "/")
        if forbidden_source_path(relative):
            excluded.append(relative)
        else:
            kept.append(row)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=("RelativePath", "SHA256", "Bytes"),
        quoting=csv.QUOTE_ALL,
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(kept)
    metadata: dict[str, object] = {
        "originalWorkspacePath": workspace_relative(baseline),
        "originalSHA256": sha256_file(baseline),
        "originalRows": len(rows),
        "sanitizedRows": len(kept),
        "excludedRows": len(excluded),
        "exclusionPolicy": "Credential-, cache-, log-, IDE- and generated-user-state paths are omitted.",
    }
    return buffer.getvalue().encode("utf-8"), metadata


def source_origins_csv(payloads: Sequence[Payload]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=("ArchivePath", "WorkspacePath", "Category", "SHA256", "Bytes"),
        quoting=csv.QUOTE_ALL,
        lineterminator="\n",
    )
    writer.writeheader()
    for payload in payloads:
        writer.writerow(
            {
                "ArchivePath": payload.archive_path.as_posix(),
                "WorkspacePath": workspace_relative(payload.source),
                "Category": payload.category,
                "SHA256": sha256_file(payload.source),
                "Bytes": payload.source.stat().st_size,
            }
        )
    return buffer.getvalue().encode("utf-8")


def restore_readme(unity_state: dict[str, object], backend_state: dict[str, object]) -> str:
    unity_origin = next(
        item["url"]
        for item in unity_state["remotes"]  # type: ignore[index]
        if item["name"] == "origin" and item["direction"] == "fetch"
    )
    backend_origin = next(
        item["url"]
        for item in backend_state["remotes"]  # type: ignore[index]
        if item["name"] == "origin" and item["direction"] == "fetch"
    )
    return f"""# FunctionalMLDS v0.5 Runtime-Archiv

Dieses Archiv bewahrt den unmittelbar vor der V2-Runtime-Anpassung verwendeten
v0.5-Implementierungsstand. Es ist ein Source-Overlay; grosse unveraenderte
Unity-Assets werden aus dem festgehaltenen Git/LFS-Commit rekonstruiert.

## Integritaet pruefen

```powershell
python verification/archive_functionalmlds_v05.py verify --output .
```

Neben dem Archiv liegt eine `.zip.sha256`-Datei fuer die Pruefung des ZIPs.

## Wiederherstellung

1. Unity-Basis auschecken und LFS-Inhalte laden:

```powershell
git clone {unity_origin} InteractivAgents/InteractiveAgents2
git -C InteractivAgents/InteractiveAgents2 checkout {unity_state['head']}
git -C InteractivAgents/InteractiveAgents2 lfs pull
```

2. Backend-Basis auschecken:

```powershell
git clone {backend_origin} InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents
git -C InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents checkout {backend_state['head']}
```

3. Den Inhalt von `source-overlay/` ueber den Workspace kopieren. Relative
   Pfade und Unity-`.meta`-Dateien muessen erhalten bleiben.
4. Das Modell-ZIP aus `model/` entpacken.
5. Eine lokale `config.json` neu anlegen. Zugangsdaten sind bewusst nicht im
   Archiv enthalten.
6. Das Laufzeitprofil explizit auf `v0.5` setzen.

Nicht wiederherzustellen sind `Library`, `Temp`, Logs, IDE-Caches,
`UserSettings`, Runtime-Logs oder das alte exportierte Unity-Paket. Unity baut
die Cache-Verzeichnisse neu auf; das Exportpaket ist kein Runtime-Eingang.

## Nichtregression

```powershell
python tools/dynamic_functional_mlds_v2_compat.py
python -m pytest -q tools/tests/test_dynamic_functional_mlds_v2_compat.py tools/tests/test_dynamic_functional_mlds_v2_validation.py
python -m pytest -q InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_functionalmlds_adapter_smoke.py InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py
```

Erwartet werden sieben verlustfreie v0.5-Roundtrips, 173 abgedeckte Pfade und
gueltige Schema-/Invariantenpruefungen aller sieben Golden-Fixtures.

Unity-Version: 6000.4.5f1. Der bekannte Editor-Smoke wird ueber
`QuickAgentManagerFunctionalMldsSmoke.Run` gestartet.
"""


def manifest_rows(directory: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix().casefold()):
        if not path.is_file() or path.name == MANIFEST_NAME:
            continue
        relative = path.relative_to(directory).as_posix()
        rows.append({"RelativePath": relative, "SHA256": sha256_file(path), "Bytes": path.stat().st_size})
    return rows


def write_manifest(directory: Path) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=("RelativePath", "SHA256", "Bytes"),
        quoting=csv.QUOTE_ALL,
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(manifest_rows(directory))
    write_text(directory / MANIFEST_NAME, buffer.getvalue())


def deterministic_zip_bytes(directory: Path) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix().casefold()):
            if not path.is_file():
                continue
            relative = path.relative_to(directory).as_posix()
            info = zipfile.ZipInfo(relative, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits |= 0x800
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return buffer.getvalue()


def assert_nested_zip_safe(path: Path) -> None:
    with zipfile.ZipFile(path, "r") as archive:
        seen: set[str] = set()
        for info in archive.infolist():
            relative = normalized_relative(info.filename)
            if info.filename in seen:
                raise RuntimeError(f"Duplicate nested ZIP entry: {path}: {info.filename}")
            seen.add(info.filename)
            if forbidden_source_path(relative):
                raise RuntimeError(f"Forbidden path in nested ZIP: {path}: {relative}")
            if not info.is_dir():
                assert_no_secret_content(archive.read(info), f"{path}!{relative}")


def load_manifest(directory: Path) -> list[dict[str, str]]:
    with (directory / MANIFEST_NAME).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_archive(directory: Path, check_sources: bool) -> dict[str, object]:
    if not directory.is_dir():
        raise FileNotFoundError(directory)
    manifest = directory / MANIFEST_NAME
    if not manifest.is_file():
        raise FileNotFoundError(manifest)
    rows = load_manifest(directory)
    expected_paths = {row["RelativePath"] for row in rows}
    actual_paths = {
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file() and path.name != MANIFEST_NAME
    }
    if expected_paths != actual_paths:
        raise RuntimeError(
            f"Manifest/file set mismatch; missing={sorted(expected_paths - actual_paths)}, "
            f"unexpected={sorted(actual_paths - expected_paths)}"
        )
    total_bytes = 0
    for row in rows:
        relative = normalized_relative(row["RelativePath"])
        if forbidden_source_path(relative):
            raise RuntimeError(f"Forbidden archived path: {relative}")
        path = directory / relative
        expected_size = int(row["Bytes"])
        actual_size = path.stat().st_size
        if actual_size != expected_size:
            raise RuntimeError(f"Size mismatch for {relative}: {actual_size} != {expected_size}")
        actual_hash = sha256_file(path)
        if actual_hash != row["SHA256"].upper():
            raise RuntimeError(f"SHA-256 mismatch for {relative}")
        total_bytes += actual_size
        assert_no_secret_content(path.read_bytes(), relative.as_posix())
        if path.suffix.lower() == ".zip":
            assert_nested_zip_safe(path)

    zip_path = directory.with_suffix(".zip")
    zip_sha_path = Path(str(zip_path) + ".sha256")
    if not zip_path.is_file() or not zip_sha_path.is_file():
        raise FileNotFoundError("ZIP or ZIP SHA-256 sidecar missing")
    sidecar_parts = zip_sha_path.read_text(encoding="utf-8").strip().split()
    if len(sidecar_parts) != 2 or sidecar_parts[1] != zip_path.name:
        raise RuntimeError("Invalid ZIP SHA-256 sidecar")
    actual_zip_hash = sha256_file(zip_path)
    if sidecar_parts[0].upper() != actual_zip_hash:
        raise RuntimeError("ZIP SHA-256 sidecar mismatch")
    expected_zip_bytes = deterministic_zip_bytes(directory)
    if sha256_bytes(expected_zip_bytes) != actual_zip_hash or expected_zip_bytes != zip_path.read_bytes():
        raise RuntimeError("ZIP is not the deterministic rendering of the archive directory")
    with zipfile.ZipFile(zip_path, "r") as archive:
        names = archive.namelist()
        expected_zip_names = sorted(
            (path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file()),
            key=str.casefold,
        )
        if names != expected_zip_names or len(names) != len(set(names)):
            raise RuntimeError("ZIP entry set/order mismatch")
        for name in names:
            normalized_relative(name)
            archive.read(name)

    source_checks = 0
    if check_sources:
        origins_path = directory / "source_origins.csv"
        with origins_path.open("r", encoding="utf-8-sig", newline="") as handle:
            origins = list(csv.DictReader(handle))
        for row in origins:
            origin = ROOT / normalized_relative(row["WorkspacePath"])
            archived = directory / normalized_relative(row["ArchivePath"])
            if not origin.is_file():
                raise FileNotFoundError(origin)
            if sha256_file(origin) != row["SHA256"].upper() or sha256_file(archived) != row["SHA256"].upper():
                raise RuntimeError(f"Source/archive drift: {row['WorkspacePath']}")
            source_checks += 1

    fixture_count = len(list((directory / "fixtures").rglob("functionalmlds.instance.generated.json")))
    if fixture_count != 7:
        raise RuntimeError(f"Expected seven Golden fixtures, found {fixture_count}")
    metadata = json.loads((directory / "archive_metadata.json").read_text(encoding="utf-8"))
    if metadata.get("contract") != "v0.5" or metadata.get("archiveFormat") != "functionalmlds-source-overlay/1":
        raise RuntimeError("Archive metadata contract/format mismatch")
    return {
        "status": "pass",
        "archive": workspace_relative(directory) if directory.resolve().is_relative_to(ROOT.resolve()) else str(directory),
        "manifestEntries": len(rows),
        "manifestedBytes": total_bytes,
        "fixtureCount": fixture_count,
        "sourceComparisons": source_checks,
        "zip": zip_path.name,
        "zipSHA256": actual_zip_hash,
        "secretFindings": 0,
    }


def create_archive(directory: Path) -> dict[str, object]:
    if directory.exists() or directory.with_suffix(".zip").exists() or Path(str(directory.with_suffix(".zip")) + ".sha256").exists():
        raise FileExistsError(f"Archive target already exists: {directory}")
    directory.parent.mkdir(parents=True, exist_ok=True)
    payloads = selected_payloads()
    try:
        for payload in payloads:
            destination = directory / payload.archive_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(payload.source, destination)
            if sha256_file(destination) != sha256_file(payload.source):
                raise RuntimeError(f"Copy verification failed: {payload.source}")

        write_bytes(directory / "source_origins.csv", source_origins_csv(payloads))
        baseline_bytes, baseline_metadata = sanitized_implementation_baseline()
        write_bytes(directory / "external_implementation_baseline.sanitized.sha256.csv", baseline_bytes)

        unity_state, unity_status = git_state(UNITY_REPO)
        backend_state, backend_status = git_state(BACKEND_REPO)
        write_text(directory / "git-state" / "unity-status.txt", unity_status)
        write_text(directory / "git-state" / "backend-status.txt", backend_status)
        write_text(directory / "git-state" / "unity.json", json_text(unity_state))
        write_text(directory / "git-state" / "backend.json", json_text(backend_state))

        counts = Counter(payload.category for payload in payloads)
        metadata = {
            "archiveFormat": "functionalmlds-source-overlay/1",
            "archiveId": directory.name,
            "contract": "v0.5",
            "snapshotLabel": "2026-07-14-pre-v2-runtime",
            "purpose": "Immutable restore source for the FunctionalMLDS v0.5 Unity/backend/pipeline implementation.",
            "deterministicZipTimestamp": "1980-01-01T00:00:00",
            "pythonVersionAtCreation": platform.python_version(),
            "payloadSourceFileCount": len(payloads),
            "payloadCategoryCounts": dict(sorted(counts.items())),
            "goldenFixtureCount": counts["v05-fixture"],
            "unity": unity_state,
            "backend": backend_state,
            "externalImplementationBaseline": baseline_metadata,
            "secretPolicy": {
                "status": "enforced",
                "excludedNames": sorted(DENIED_EXACT_FILENAMES),
                "excludedDirectoryNames": sorted(DENIED_DIRECTORY_NAMES),
                "concreteCredentialSignatureFindings": 0,
            },
            "largeAssetRestore": {
                "unityGitLfsRequired": True,
                "unityLibraryArchived": False,
                "exportedUnityPackageArchived": False,
            },
        }
        write_text(directory / "archive_metadata.json", json_text(metadata))
        write_text(directory / "README_RESTORE.md", restore_readme(unity_state, backend_state))

        for path in directory.rglob("*"):
            if path.is_file():
                if forbidden_source_path(path.relative_to(directory).as_posix()):
                    raise RuntimeError(f"Forbidden output path: {path}")
                assert_no_secret_content(path.read_bytes(), path.relative_to(directory).as_posix())
                if path.suffix.lower() == ".zip":
                    assert_nested_zip_safe(path)

        write_manifest(directory)
        zip_bytes = deterministic_zip_bytes(directory)
        zip_path = directory.with_suffix(".zip")
        write_bytes(zip_path, zip_bytes)
        write_text(Path(str(zip_path) + ".sha256"), f"{sha256_bytes(zip_bytes)}  {zip_path.name}\n")
        return verify_archive(directory, check_sources=True)
    except Exception:
        # A failed creation must not leave an apparently usable partial archive.
        if directory.exists():
            shutil.rmtree(directory)
        zip_path = directory.with_suffix(".zip")
        if zip_path.exists():
            zip_path.unlink()
        zip_sha = Path(str(zip_path) + ".sha256")
        if zip_sha.exists():
            zip_sha.unlink()
        raise


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("create", "verify"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
        if command == "verify":
            subparser.add_argument("--check-sources", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    output = args.output
    if not output.is_absolute():
        output = ROOT / output
    if args.command == "create":
        report = create_archive(output)
    else:
        report = verify_archive(output, check_sources=bool(args.check_sources))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
