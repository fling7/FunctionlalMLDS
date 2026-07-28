from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .common import read_json, update_manifest, write_json


SCHEMA = "functionalmlds_chat_test_results"
SCHEMA_VERSION = "1.0"
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = (
    REPOSITORY_ROOT
    / "InteractivAgents"
    / "openai_unity_expert_npcs_pycharm"
    / "InteractiveAgents"
)
BACKEND_IMPLEMENTATION_PATHS = [
    BACKEND_ROOT / "backend" / "app.py",
    BACKEND_ROOT / "backend" / "state.py",
    BACKEND_ROOT / "backend" / "functionalmlds_v2_runtime.py",
]


def backend_url_from_config(config_path: Path) -> str:
    raw = json.loads(Path(config_path).read_text(encoding="utf-8-sig"))
    host = str(raw.get("server_host") or "127.0.0.1").strip()
    port = int(raw.get("server_port") or 8787)
    return f"http://{host}:{port}"


def _post_json(url: str, payload: Mapping[str, Any], *, timeout_seconds: int) -> Tuple[int, Dict[str, Any]]:
    data = json.dumps(dict(payload), ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8", errors="replace")
            return int(response.status), json.loads(body) if body.strip() else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body) if body.strip() else {}
        except json.JSONDecodeError:
            payload = {"error": body}
        return int(exc.code), payload


def _get_json(url: str, *, timeout_seconds: int) -> Tuple[int, Dict[str, Any]]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8", errors="replace")
            return int(response.status), json.loads(body) if body.strip() else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body) if body.strip() else {}
        except json.JSONDecodeError:
            payload = {"error": body}
        return int(exc.code), payload


def _health_ok(backend_url: str, timeout_seconds: int) -> bool:
    try:
        status, payload = _get_json(f"{backend_url.rstrip('/')}/health", timeout_seconds=timeout_seconds)
    except Exception:
        return False
    return status == 200 and payload.get("status") == "ok"


def _setup_session(
    *,
    backend_url: str,
    case_id: str,
    memory_mode: str,
    timeout_seconds: int,
) -> Tuple[int, Dict[str, Any]]:
    return _post_json(
        f"{backend_url.rstrip('/')}/setup",
        {"project_id": case_id, "memory_mode": memory_mode},
        timeout_seconds=timeout_seconds,
    )


def _chat(
    *,
    backend_url: str,
    session_id: str,
    active_agent_id: str,
    user_text: str,
    timeout_seconds: int,
) -> Tuple[int, Dict[str, Any], float]:
    started = time.perf_counter()
    status, payload = _post_json(
        f"{backend_url.rstrip('/')}/chat",
        {
            "session_id": session_id,
            "active_agent_id": active_agent_id,
            "user_text": user_text,
        },
        timeout_seconds=timeout_seconds,
    )
    return status, payload, round((time.perf_counter() - started) * 1000, 3)


def _agent_ids_from_setup(setup_response: Mapping[str, Any]) -> List[str]:
    return [
        str(agent.get("id") or "").strip()
        for agent in setup_response.get("agents") or []
        if isinstance(agent, Mapping) and str(agent.get("id") or "").strip()
    ]


def _say_events(response: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [
        dict(event)
        for event in response.get("events") or []
        if isinstance(event, Mapping) and event.get("type") == "say"
    ]


def _answer_text(response: Mapping[str, Any]) -> str:
    return "\n".join(str(event.get("text") or "").strip() for event in _say_events(response)).strip()


def _looks_like_openai_error(response: Mapping[str, Any], answer_text: str) -> bool:
    if response.get("error"):
        return True
    return "[Backend] OpenAI Fehler" in answer_text or "OpenAI HTTP" in answer_text


def _question_filter(questions: Sequence[Dict[str, Any]], question_kind: Optional[str], max_questions: Optional[int]) -> List[Dict[str, Any]]:
    filtered = [
        question
        for question in questions
        if isinstance(question, dict) and (not question_kind or question.get("kind") == question_kind)
    ]
    if max_questions is not None:
        return filtered[: max(0, int(max_questions))]
    return filtered


def _reuse_setup_session(case_dir: Path) -> Dict[str, Any]:
    setup_response_path = case_dir / "runtime_logs" / "setup_response.json"
    if setup_response_path.exists():
        return read_json(setup_response_path)
    return {}


def run_chat_tests_for_case(
    case_dir: Path,
    *,
    backend_url: str,
    memory_mode: str = "agent_private_history",
    isolate_questions: bool = True,
    timeout_seconds: int = 90,
    max_questions: Optional[int] = None,
    question_kind: Optional[str] = None,
) -> Dict[str, Any]:
    case_dir = Path(case_dir).resolve()
    case_id = case_dir.name
    questions_path = case_dir / "validation" / "evaluation_questions.json"
    raw_output_path = case_dir / "runtime_logs" / "chat_responses.json"
    validation_path = case_dir / "validation" / "chat_test_results.json"

    errors: List[str] = []
    warnings: List[str] = []
    raw_responses: List[Dict[str, Any]] = []
    chat_tests: List[Dict[str, Any]] = []

    if not _health_ok(backend_url, timeout_seconds=min(timeout_seconds, 10)):
        errors.append(f"Backend health check failed: {backend_url}/health.")

    questions_payload = read_json(questions_path)
    questions = _question_filter(questions_payload.get("questions") or [], question_kind, max_questions)
    if not questions:
        errors.append("No evaluation questions selected.")

    reused_setup = _reuse_setup_session(case_dir)
    reused_agent_ids = set(_agent_ids_from_setup(reused_setup))
    if not isolate_questions and not reused_setup.get("session_id"):
        errors.append("Cannot reuse setup session because runtime_logs/setup_response.json has no session_id.")

    if not errors:
        for question in questions:
            question_id = str(question.get("question_id") or "").strip()
            setup_status = None
            setup_response: Dict[str, Any] = reused_setup
            if isolate_questions:
                setup_status, setup_response = _setup_session(
                    backend_url=backend_url,
                    case_id=case_id,
                    memory_mode=memory_mode,
                    timeout_seconds=timeout_seconds,
                )
            session_id = str(setup_response.get("session_id") or "").strip()
            agent_ids = set(_agent_ids_from_setup(setup_response)) or reused_agent_ids
            active_agent_id = str(question.get("active_agent_id") or "").strip()
            expected = (
                dict(question.get("expected"))
                if isinstance(question.get("expected"), Mapping)
                else {}
            )
            request_payload = {
                "session_id": session_id,
                "active_agent_id": active_agent_id,
                "user_text": str(
                    question.get("utterance") or question.get("text") or ""
                ).strip(),
            }
            if not session_id:
                response_status = 0
                response_payload = {"error": "No session_id available."}
                duration_ms = 0.0
            else:
                response_status, response_payload, duration_ms = _chat(
                    backend_url=backend_url,
                    session_id=session_id,
                    active_agent_id=active_agent_id,
                    user_text=request_payload["user_text"],
                    timeout_seconds=timeout_seconds,
                )

            answer = _answer_text(response_payload)
            say_events = _say_events(response_payload)
            observed_handoff = response_payload.get("handoff") if isinstance(response_payload.get("handoff"), Mapping) else None
            observed_handoff_to = str(observed_handoff.get("to") or "").strip() if observed_handoff else None
            response_active_agent = str(response_payload.get("active_agent_id") or "").strip()

            test_errors: List[str] = []
            if setup_status is not None and setup_status != 200:
                test_errors.append(f"setup returned HTTP {setup_status}.")
            if response_status != 200:
                test_errors.append(f"chat returned HTTP {response_status}.")
            if not say_events:
                test_errors.append("chat response has no say event.")
            if not answer:
                test_errors.append("chat answer text is empty.")
            if response_active_agent not in agent_ids:
                test_errors.append(f"response active_agent_id is unknown: {response_active_agent}.")
            if active_agent_id not in agent_ids:
                test_errors.append(f"requested active_agent_id is unknown: {active_agent_id}.")
            if _looks_like_openai_error(response_payload, answer):
                test_errors.append("chat response contains an OpenAI/backend error.")

            raw_responses.append(
                {
                    "question_id": question_id,
                    "request": request_payload,
                    "setup_status": setup_status,
                    "response_status": response_status,
                    "duration_ms": duration_ms,
                    "response": response_payload,
                }
            )
            chat_tests.append(
                {
                    "question_id": question_id,
                    "case_id": case_id,
                    "kind": question.get("kind"),
                    "benchmark_class": question.get("benchmark_class"),
                    "success": not test_errors,
                    "errors": test_errors,
                    "http_status": response_status,
                    "duration_ms": duration_ms,
                    "session_id": session_id,
                    "active_agent_id": active_agent_id,
                    "response_active_agent_id": response_active_agent,
                    "event_count": len(response_payload.get("events") or []),
                    "say_event_count": len(say_events),
                    "answer_char_count": len(answer),
                    "answer_preview": answer[:500],
                    "expected_handoff": bool(question.get("expected_handoff")),
                    "expected_handoff_to": question.get("expected_handoff_to"),
                    "observed_handoff": bool(observed_handoff),
                    "observed_handoff_to": observed_handoff_to,
                    "expected_agent_id": question.get("expected_agent_id"),
                    "expected_resolution": (
                        question.get("expected_resolution")
                        or expected.get("resolution")
                    ),
                    "expected_rationale": expected.get("rationale"),
                    "candidate_agent_ids": (
                        question.get("candidate_agent_ids")
                        or expected.get("candidate_agent_ids")
                        or []
                    ),
                    "expected_zone_ids": question.get("expected_zone_ids") or [],
                    "expected_object_ids": question.get("expected_object_ids") or [],
                }
            )

    failed_tests = [test for test in chat_tests if not test["success"]]
    errors.extend(f"{test['question_id']}: {'; '.join(test['errors'])}" for test in failed_tests[:20])
    if len(failed_tests) > 20:
        errors.append(f"{len(failed_tests) - 20} additional chat tests failed.")

    metrics = {
        "selected_question_count": len(questions),
        "executed_chat_count": len(chat_tests),
        "successful_chat_count": len(chat_tests) - len(failed_tests),
        "failed_chat_count": len(failed_tests),
        "http_200_count": sum(1 for test in chat_tests if test["http_status"] == 200),
        "say_event_coverage": round(
            sum(1 for test in chat_tests if test["say_event_count"] > 0) / len(chat_tests),
            6,
        )
        if chat_tests
        else 0.0,
        "nonempty_answer_coverage": round(
            sum(1 for test in chat_tests if test["answer_char_count"] > 0) / len(chat_tests),
            6,
        )
        if chat_tests
        else 0.0,
        "handoff_question_count": sum(1 for test in chat_tests if test["kind"] == "handoff_decision"),
        "handoff_negative_question_count": sum(
            1 for test in chat_tests if test["kind"] == "handoff_negative"
        ),
        "handoff_ambiguous_question_count": sum(
            1 for test in chat_tests if test["kind"] == "handoff_ambiguous"
        ),
        "handoff_unknown_question_count": sum(
            1 for test in chat_tests if test["kind"] == "handoff_unknown"
        ),
        "observed_handoff_count": sum(1 for test in chat_tests if test["observed_handoff"]),
        "isolated_session_per_question": bool(isolate_questions),
    }
    payload = {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "backend_url": backend_url,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
        "chat_tests": chat_tests,
    }
    raw_payload = {
        "schema": f"{SCHEMA}_raw",
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "backend_url": backend_url,
        "responses": raw_responses,
    }
    write_json(validation_path, payload)
    write_json(raw_output_path, raw_payload)
    update_manifest(
        case_dir,
        stage_id="chat_tests",
        status="success" if payload["status"] == "valid" else "failed",
        input_paths=[
            questions_path,
            Path(__file__).resolve(),
            BACKEND_ROOT / "projects" / case_id / "project.json",
            BACKEND_ROOT / "projects" / case_id / "agents.json",
            BACKEND_ROOT / "projects" / case_id / "trace_map.v2.json",
            BACKEND_ROOT / "projects" / case_id / "functionalmlds.v2.instance.json",
            *BACKEND_IMPLEMENTATION_PATHS,
        ],
        output_paths=[validation_path, raw_output_path],
        errors=payload["errors"],
        warnings=payload["warnings"],
        metadata=payload["metrics"],
    )
    return {
        "case_id": case_id,
        "status": "success" if payload["status"] == "valid" else "failed",
        "validation": {
            "status": payload["status"],
            "errors": payload["errors"],
            "warnings": payload["warnings"],
            "metrics": payload["metrics"],
        },
        "validation_path": str(validation_path),
        "raw_output_path": str(raw_output_path),
    }


def run_chat_tests_for_cases(
    case_dirs: Iterable[Path],
    *,
    backend_url: str,
    memory_mode: str = "agent_private_history",
    isolate_questions: bool = True,
    timeout_seconds: int = 90,
    max_questions: Optional[int] = None,
    question_kind: Optional[str] = None,
) -> List[Dict[str, Any]]:
    return [
        run_chat_tests_for_case(
            case_dir,
            backend_url=backend_url,
            memory_mode=memory_mode,
            isolate_questions=isolate_questions,
            timeout_seconds=timeout_seconds,
            max_questions=max_questions,
            question_kind=question_kind,
        )
        for case_dir in case_dirs
    ]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run backend /chat evaluation tests.")
    parser.add_argument("--case-dir", type=Path, action="append")
    parser.add_argument("--case-root", type=Path)
    parser.add_argument("--backend-url", default=None)
    parser.add_argument(
        "--backend-config",
        type=Path,
        default=Path("InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/config.json"),
    )
    parser.add_argument("--memory-mode", default="agent_private_history")
    parser.add_argument("--reuse-setup-session", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--max-questions-per-case", type=int, default=None)
    parser.add_argument("--question-kind", default=None)
    args = parser.parse_args(argv)
    case_dirs = args.case_dir or []
    if args.case_root:
        case_dirs.extend(sorted(path for path in args.case_root.iterdir() if path.is_dir()))
    if not case_dirs:
        parser.error("Pass --case-dir or --case-root.")
    backend_url = args.backend_url or backend_url_from_config(args.backend_config)
    results = run_chat_tests_for_cases(
        case_dirs,
        backend_url=backend_url,
        memory_mode=args.memory_mode,
        isolate_questions=not args.reuse_setup_session,
        timeout_seconds=args.timeout_seconds,
        max_questions=args.max_questions_per_case,
        question_kind=args.question_kind,
    )
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 0 if all(result["status"] == "success" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
