from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

RUNTIME_LOG_SCHEMA = "functionalmlds_runtime_event"
RUNTIME_LOG_SCHEMA_VERSION = "1.0"
RUNTIME_LOG_SCHEMA_VERSION_V2 = "2.0"

RUNTIME_EVENT_TYPES = {
    "pipeline_stage_started",
    "pipeline_stage_completed",
    "backend_setup_started",
    "backend_setup_completed",
    "backend_chat_started",
    "backend_chat_completed",
    "backend_handoff_completed",
    "unity_setup_completed",
    "unity_agent_selected",
    "unity_chat_sent",
    "unity_chat_received",
    "unity_handoff_received",
    "unity_handoff_arrived",
    "validation_observation",
    "error",
}

REQUIRED_EVENT_FIELDS = (
    "timestamp",
    "case_id",
    "session_id",
    "event_type",
    "agent_id",
    "scenario_step_id",
    "capability_id",
    "runtime_binding_id",
    "runtime_action_id",
    "input_summary",
    "output_summary",
)

_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)(api[_-]?key|authorization|bearer)\s*[:=]\s*[^,\s}]+"),
)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def redact_summary(value: Any, *, max_chars: int = 2000) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_chars:
        return text[: max_chars - 15].rstrip() + " [TRUNCATED]"
    return text


def build_runtime_event(
    *,
    case_id: str,
    event_type: str,
    input_summary: Any,
    output_summary: Any = "",
    session_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    scenario_step_id: Optional[str] = None,
    capability_id: Optional[str] = None,
    runtime_binding_id: Optional[str] = None,
    runtime_action_id: Optional[str] = None,
    timestamp: Optional[str] = None,
    duration_ms: Optional[float] = None,
    status: Optional[str] = None,
    error_summary: Optional[Any] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    event_id: Optional[str] = None,
) -> Dict[str, Any]:
    event = {
        "schema": RUNTIME_LOG_SCHEMA,
        "schema_version": RUNTIME_LOG_SCHEMA_VERSION,
        "event_id": event_id or f"EVT-{uuid.uuid4().hex}",
        "timestamp": timestamp or utc_timestamp(),
        "case_id": case_id,
        "session_id": session_id,
        "event_type": event_type,
        "agent_id": agent_id,
        "scenario_step_id": scenario_step_id,
        "capability_id": capability_id,
        "runtime_binding_id": runtime_binding_id,
        "runtime_action_id": runtime_action_id,
        "input_summary": redact_summary(input_summary),
        "output_summary": redact_summary(output_summary),
        "duration_ms": duration_ms,
        "status": status,
        "error_summary": redact_summary(error_summary) if error_summary is not None else None,
        "metadata": _clean_metadata(metadata or {}),
    }
    errors = validate_runtime_event(event)
    if errors:
        raise ValueError("; ".join(errors))
    return event


def append_runtime_event(path: Path, event: Mapping[str, Any]) -> None:
    errors = validate_runtime_event(event)
    if errors:
        raise ValueError("; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(event), ensure_ascii=False, sort_keys=True))
        handle.write("\n")


def read_runtime_events(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    events: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                event = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL event: {exc}") from exc
            errors = validate_runtime_event(event)
            if errors:
                raise ValueError(f"{path}:{line_number}: {'; '.join(errors)}")
            events.append(event)
    return events


def validate_runtime_event(event: Mapping[str, Any], trace_map: Optional[Mapping[str, Any]] = None) -> List[str]:
    errors: List[str] = []
    is_v2 = str(event.get("schema_version") or RUNTIME_LOG_SCHEMA_VERSION) == RUNTIME_LOG_SCHEMA_VERSION_V2
    for field in REQUIRED_EVENT_FIELDS:
        if field not in event:
            errors.append(f"missing required field: {field}")

    if event.get("schema", RUNTIME_LOG_SCHEMA) != RUNTIME_LOG_SCHEMA:
        errors.append("schema must be functionalmlds_runtime_event")
    if event.get("schema_version", RUNTIME_LOG_SCHEMA_VERSION) not in {
        RUNTIME_LOG_SCHEMA_VERSION,
        RUNTIME_LOG_SCHEMA_VERSION_V2,
    }:
        errors.append("schema_version must be 1.0 or 2.0")
    if not _is_non_empty_string(event.get("case_id")):
        errors.append("case_id must be a non-empty string")
    if event.get("event_type") not in RUNTIME_EVENT_TYPES:
        errors.append(f"event_type must be one of: {', '.join(sorted(RUNTIME_EVENT_TYPES))}")
    if not _is_iso_timestamp(event.get("timestamp")):
        errors.append("timestamp must be an ISO-8601 date-time string")

    for field in ("session_id", "agent_id", "scenario_step_id", "capability_id", "runtime_binding_id", "runtime_action_id"):
        value = event.get(field)
        if value is not None and not _is_non_empty_string(value):
            errors.append(f"{field} must be null or a non-empty string")

    for field in ("input_summary", "output_summary"):
        value = event.get(field)
        if not isinstance(value, str):
            errors.append(f"{field} must be a string")
        elif len(value) > 2000:
            errors.append(f"{field} must be at most 2000 characters")
        elif _looks_like_secret(value):
            errors.append(f"{field} appears to contain a secret")

    error_summary = event.get("error_summary")
    if error_summary is not None:
        if not isinstance(error_summary, str):
            errors.append("error_summary must be null or a string")
        elif len(error_summary) > 2000:
            errors.append("error_summary must be at most 2000 characters")
        elif _looks_like_secret(error_summary):
            errors.append("error_summary appears to contain a secret")

    duration_ms = event.get("duration_ms")
    if duration_ms is not None and not isinstance(duration_ms, (int, float)):
        errors.append("duration_ms must be null or numeric")
    elif isinstance(duration_ms, (int, float)) and duration_ms < 0:
        errors.append("duration_ms must not be negative")

    valid_statuses = (
        {"success", "failed", "error", "inconclusive"}
        if is_v2
        else {"success", "failure", "skipped", "needs_manual_review", None}
    )
    if event.get("status") not in valid_statuses:
        errors.append("status is not valid")

    if is_v2:
        for field in (
            "model_version",
            "model_sha256",
            "capability_use_id",
            "provider_entity_id",
            "target_ids",
            "assertion_ids",
            "validation_case_ids",
            "runtime_validation_target_ids",
        ):
            if field not in event:
                errors.append(f"missing required V2 field: {field}")
        if event.get("model_version") != "2.0.0-model":
            errors.append("model_version must be 2.0.0-model")
        model_hash = event.get("model_sha256")
        if not isinstance(model_hash, str) or not re.fullmatch(r"[A-F0-9]{64}", model_hash):
            errors.append("model_sha256 must be an uppercase SHA-256")
        for field in ("capability_use_id", "provider_entity_id"):
            if not _is_non_empty_string(event.get(field)):
                errors.append(f"{field} must be a non-empty string")
        for field in (
            "target_ids",
            "assertion_ids",
            "validation_case_ids",
            "runtime_validation_target_ids",
        ):
            value = event.get(field)
            if not isinstance(value, list) or any(not _is_non_empty_string(item) for item in value):
                errors.append(f"{field} must be an array of non-empty strings")
        if isinstance(event.get("assertion_ids"), list) and not event.get("assertion_ids"):
            errors.append("assertion_ids must not be empty for V2")

    metadata = event.get("metadata", {})
    if not isinstance(metadata, Mapping):
        errors.append("metadata must be an object")
    else:
        for key, value in metadata.items():
            if not isinstance(key, str):
                errors.append("metadata keys must be strings")
            if value is not None and not isinstance(value, (str, int, float, bool)):
                errors.append(f"metadata[{key}] must be scalar or null")

    if trace_map is not None:
        errors.extend(validate_runtime_event_trace(event, trace_map))

    return errors


def validate_runtime_event_trace(event: Mapping[str, Any], trace_map: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if event.get("case_id") != trace_map.get("case_id"):
        errors.append("event case_id does not match trace_map case_id")

    step_ids = {step.get("scenario_step_id") for step in trace_map.get("scenario_steps", []) if isinstance(step, Mapping)}
    capability_ids = {item.get("capability_id") for item in trace_map.get("capabilities", []) if isinstance(item, Mapping)}
    action_items = [item for item in trace_map.get("runtime_actions", []) if isinstance(item, Mapping)]
    binding_ids = {item.get("runtime_binding_id") for item in action_items}
    action_ids = {item.get("runtime_action_id") for item in action_items}
    capability_use_ids = {item.get("capability_use_id") for item in action_items}
    provider_ids = {item.get("provider_entity_id") for item in action_items}
    assertion_ids = {
        item.get("assertion_id") for item in trace_map.get("assertions", []) if isinstance(item, Mapping)
    }
    validation_case_ids = {
        item.get("validation_case_id") for item in trace_map.get("validation_cases", []) if isinstance(item, Mapping)
    }
    runtime_validation_target_ids = {
        item.get("runtime_validation_target_id")
        for item in trace_map.get("runtime_validation_targets", [])
        if isinstance(item, Mapping)
    }
    agent_ids = {item.get("agent_id") for item in trace_map.get("agents", []) if isinstance(item, Mapping)}

    _check_optional_ref(errors, event, "scenario_step_id", step_ids)
    _check_optional_ref(errors, event, "capability_id", capability_ids)
    _check_optional_ref(errors, event, "runtime_binding_id", binding_ids)
    _check_optional_ref(errors, event, "runtime_action_id", action_ids)
    _check_optional_ref(errors, event, "agent_id", agent_ids)
    _check_optional_ref(errors, event, "capability_use_id", capability_use_ids)
    _check_optional_ref(errors, event, "provider_entity_id", provider_ids)
    for field, allowed in (
        ("assertion_ids", assertion_ids),
        ("validation_case_ids", validation_case_ids),
        ("runtime_validation_target_ids", runtime_validation_target_ids),
    ):
        for value in event.get(field) or []:
            if value not in {item for item in allowed if item is not None}:
                errors.append(f"{field} contains a reference not present in trace_map: {value}")

    action_id = event.get("runtime_action_id")
    if action_id is not None:
        matches = [item for item in action_items if item.get("runtime_action_id") == action_id]
        if matches:
            action = matches[0]
            if event.get("runtime_binding_id") != action.get("runtime_binding_id"):
                errors.append("runtime_action_id does not belong to runtime_binding_id")
            if event.get("capability_id") != action.get("capability_id"):
                errors.append("runtime_action_id does not belong to capability_id")
            for field in (
                "scenario_step_id",
                "capability_use_id",
                "provider_entity_id",
            ):
                if event.get(field) != action.get(field):
                    errors.append(f"runtime_action_id does not belong to {field}")
            if list(event.get("target_ids") or []) != list(action.get("target_ids") or []):
                errors.append("runtime_action_id target_ids do not match the exact trace mapping")
    return errors


def _clean_metadata(metadata: Mapping[str, Any]) -> Dict[str, Any]:
    clean: Dict[str, Any] = {}
    for key, value in metadata.items():
        if value is None or isinstance(value, (int, float, bool)):
            clean[str(key)] = value
        elif isinstance(value, str):
            clean[str(key)] = redact_summary(value, max_chars=500)
        else:
            clean[str(key)] = redact_summary(value, max_chars=500)
    return clean


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_iso_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(normalized)
        return True
    except ValueError:
        return False


def _looks_like_secret(value: str) -> bool:
    return any(pattern.search(value) for pattern in _SECRET_PATTERNS)


def _check_optional_ref(errors: List[str], event: Mapping[str, Any], field: str, allowed: Iterable[Any]) -> None:
    value = event.get(field)
    if value is None:
        return
    allowed_values = {item for item in allowed if item is not None}
    if value not in allowed_values:
        errors.append(f"{field} is not present in trace_map: {value}")
