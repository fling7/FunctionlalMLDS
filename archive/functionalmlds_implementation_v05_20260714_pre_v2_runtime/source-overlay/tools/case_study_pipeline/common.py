from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def slugify(value: str, fallback: str = "case") -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or fallback


def relative_to_or_absolute(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path.resolve())


def ensure_dirs(case_dir: Path) -> None:
    for name in (
        "input",
        "intermediate",
        "functionalmlds",
        "interactive_agents_project",
        "runtime_logs",
        "validation",
        "paper_artifacts",
    ):
        (case_dir / name).mkdir(parents=True, exist_ok=True)


def load_manifest(case_dir: Path) -> Dict[str, Any]:
    path = case_dir / "stage_manifest.json"
    if not path.exists():
        return {"case_id": case_dir.name, "created_at": utc_now_iso(), "stages": []}
    return read_json(path)


def update_manifest(
    case_dir: Path,
    *,
    stage_id: str,
    status: str,
    input_paths: Iterable[Path],
    output_paths: Iterable[Path],
    errors: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    manifest = load_manifest(case_dir)
    manifest["case_id"] = case_dir.name
    manifest["updated_at"] = utc_now_iso()

    inputs = []
    for path in input_paths:
        path = Path(path)
        entry = {"path": str(path)}
        if path.exists() and path.is_file():
            entry["sha256"] = sha256_file(path)
        inputs.append(entry)

    outputs = []
    for path in output_paths:
        path = Path(path)
        entry = {"path": str(path)}
        if path.exists() and path.is_file():
            entry["sha256"] = sha256_file(path)
        outputs.append(entry)

    stage_entry = {
        "stage_id": stage_id,
        "status": status,
        "updated_at": utc_now_iso(),
        "inputs": inputs,
        "outputs": outputs,
        "errors": errors or [],
        "warnings": warnings or [],
        "metadata": metadata or {},
    }

    stages = [s for s in manifest.get("stages", []) if s.get("stage_id") != stage_id]
    stages.append(stage_entry)
    manifest["stages"] = stages
    write_json(case_dir / "stage_manifest.json", manifest)

