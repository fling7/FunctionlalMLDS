from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional


RUNTIME_LOG_SCHEMA = "functionalmlds_runtime_event"
RUNTIME_LOG_SCHEMA_VERSION = "1.0"

_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)(api[_-]?key|authorization|bearer)\s*[:=]\s*[^,\s}]+"),
)


def log_backend_event(
    *,
    project_manager: Any,
    project_id: Optional[str],
    action_kind: str,
    event_type: str,
    session_id: Optional[str],
    agent_id: Optional[str],
    input_summary: Any,
    output_summary: Any,
    duration_ms: Optional[float] = None,
    status: str = "success",
    metadata: Optional[Mapping[str, Any]] = None,
) -> None:
    if not project_id:
        return
    try:
        project_dir = _project_dir(project_manager, project_id)
        if project_dir is None:
            return
        trace_map = _read_json_if_exists(project_dir / "trace_map.json")
        trace_ref = _trace_ref(trace_map, action_kind)
        log_path = _runtime_log_path(project_dir)
        event = _build_event(
            case_id=str(trace_map.get("case_id") or project_id),
            event_type=event_type,
            session_id=session_id,
            agent_id=agent_id,
            input_summary=input_summary,
            output_summary=output_summary,
            duration_ms=duration_ms,
            status=status,
            metadata=metadata or {},
            scenario_step_id=_scenario_step_id(trace_map, trace_ref.get("capability_id")),
            capability_id=trace_ref.get("capability_id"),
            runtime_binding_id=trace_ref.get("runtime_binding_id"),
            runtime_action_id=trace_ref.get("runtime_action_id"),
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
    except Exception as exc:
        print(f"[RuntimeTrace] Warnung: Event konnte nicht geschrieben werden: {exc}", flush=True)


def _project_dir(project_manager: Any, project_id: str) -> Optional[Path]:
    resolver = getattr(project_manager, "_project_dir", None)
    if callable(resolver):
        return Path(resolver(project_id))
    root = getattr(project_manager, "root", None)
    if root is None:
        return None
    return Path(root) / project_id


def _runtime_log_path(project_dir: Path) -> Path:
    meta = _read_json_if_exists(project_dir / "project.json")
    trace_path_raw = str(meta.get("functionalmlds_trace_path") or "").strip()
    if trace_path_raw:
        trace_path = Path(trace_path_raw)
        if trace_path.parent.name == "functionalmlds":
            return trace_path.parent.parent / "runtime_logs" / "events.jsonl"
    return project_dir / "runtime_logs" / "events.jsonl"


def _read_json_if_exists(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _trace_ref(trace_map: Mapping[str, Any], action_kind: str) -> Dict[str, Optional[str]]:
    actions = [item for item in trace_map.get("runtime_actions", []) if isinstance(item, Mapping)]
    action_kind = action_kind.strip().lower()

    def matches(item: Mapping[str, Any]) -> bool:
        action_id = str(item.get("runtime_action_id") or "")
        capability_id = str(item.get("capability_id") or "")
        endpoint = str(item.get("endpoint") or "")
        if action_kind == "setup":
            return endpoint == "POST /setup"
        if action_kind == "handoff":
            return endpoint == "POST /chat" and ("HANDOFF" in action_id or "HANDOFF" in capability_id)
        if action_kind == "chat":
            return (
                endpoint == "POST /chat"
                and "HANDOFF" not in action_id
                and "HANDOFF" not in capability_id
            )
        return False

    for item in actions:
        if matches(item):
            return {
                "capability_id": _optional_str(item.get("capability_id")),
                "runtime_binding_id": _optional_str(item.get("runtime_binding_id")),
                "runtime_action_id": _optional_str(item.get("runtime_action_id")),
            }
    return {"capability_id": None, "runtime_binding_id": None, "runtime_action_id": None}


def _scenario_step_id(trace_map: Mapping[str, Any], capability_id: Optional[str]) -> Optional[str]:
    if not capability_id:
        return None
    case_id = str(trace_map.get("case_id") or "").upper()
    prefix = f"CAP-{case_id}-"
    suffix = capability_id[len(prefix) :] if capability_id.startswith(prefix) else capability_id
    for step in trace_map.get("scenario_steps", []):
        if not isinstance(step, Mapping):
            continue
        for capability_use_id in step.get("capability_use_ids") or []:
            if str(capability_use_id).endswith(suffix):
                return _optional_str(step.get("scenario_step_id"))
    return None


def _build_event(
    *,
    case_id: str,
    event_type: str,
    session_id: Optional[str],
    agent_id: Optional[str],
    scenario_step_id: Optional[str],
    capability_id: Optional[str],
    runtime_binding_id: Optional[str],
    runtime_action_id: Optional[str],
    input_summary: Any,
    output_summary: Any,
    duration_ms: Optional[float],
    status: str,
    metadata: Mapping[str, Any],
) -> Dict[str, Any]:
    return {
        "schema": RUNTIME_LOG_SCHEMA,
        "schema_version": RUNTIME_LOG_SCHEMA_VERSION,
        "event_id": f"EVT-{uuid.uuid4().hex}",
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "case_id": case_id,
        "session_id": session_id,
        "event_type": event_type,
        "agent_id": agent_id,
        "scenario_step_id": scenario_step_id,
        "capability_id": capability_id,
        "runtime_binding_id": runtime_binding_id,
        "runtime_action_id": runtime_action_id,
        "input_summary": _summary(input_summary),
        "output_summary": _summary(output_summary),
        "duration_ms": duration_ms,
        "status": status,
        "error_summary": None,
        "metadata": _metadata(metadata),
    }


def _summary(value: Any, max_chars: int = 2000) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_chars:
        return text[: max_chars - 15].rstrip() + " [TRUNCATED]"
    return text


def _metadata(values: Mapping[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in values.items():
        if value is None or isinstance(value, (str, int, float, bool)):
            out[str(key)] = value
        else:
            out[str(key)] = _summary(value, max_chars=500)
    return out


def _optional_str(value: Any) -> Optional[str]:
    text = str(value or "").strip()
    return text or None
