from __future__ import annotations

import copy
import json
import shutil
import socket
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = (
    ROOT
    / "InteractivAgents"
    / "openai_unity_expert_npcs_pycharm"
    / "InteractiveAgents"
)
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from backend.functionalmlds_v2_runtime import (  # noqa: E402
    FunctionalMldsContractError,
    load_project_contract,
    select_runtime_action,
)
from backend.kb import KnowledgeBase  # noqa: E402
from backend.projects import ProjectManager  # noqa: E402
from backend.runtime_trace import (  # noqa: E402
    _append_jsonl_transaction,
    contract_runtime_fingerprint,
    log_backend_event,
)
from backend.server import start_http_server  # noqa: E402
from backend.state import SessionStore  # noqa: E402


CASE_ID = "classroom_dinosaur"
SOURCE_PROJECT = BACKEND_ROOT / "projects" / CASE_ID


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


class _OfflineOpenAI:
    api_key = "offline"
    timeout_seconds = 1

    def create_structured_json(self, **_: object):
        parsed = {
            "say": "Lokale Testantwort",
            "handoff_to": None,
            "handoff_reason": None,
            "handoff_brief": None,
            "confidence": 1.0,
        }
        return parsed, {"id": "offline-response"}, json.dumps(parsed)


class FunctionalMldsV2SessionHardeningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="functionalmlds-v2-session-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.projects_root = self.root / "projects"
        self.project_dir = self.projects_root / CASE_ID
        shutil.copytree(SOURCE_PROJECT, self.project_dir)

        # Keep every runtime write inside the disposable project copy.
        project = _read_json(self.project_dir / "project.json")
        project["functionalmlds_trace_path"] = str(
            self.project_dir / "functionalmlds" / "source-v05.json"
        )
        _write_json(self.project_dir / "project.json", project)

        manager = ProjectManager(
            root=self.projects_root,
            template_room_plan=self.project_dir / "room_plan.json",
            template_agents=self.project_dir / "agents.json",
        )
        self.store = SessionStore(
            max_history_turns=4,
            max_handoffs=1,
            kb=KnowledgeBase(self.root / "fallback-kb"),
            kb_max_snippets=2,
            model="offline",
            temperature=0.0,
            stt_model="offline",
            stt_language="de",
            stt_max_audio_bytes=1024,
            openai=_OfflineOpenAI(),
            project_manager=manager,
        )

    def _setup(self, session_id: str = "SESSION-HARDENING") -> dict:
        return self.store.setup_from_request(
            {"project_id": CASE_ID, "session_id": session_id}
        )

    def test_setup_pins_complete_contract_and_exact_setup_action(self) -> None:
        response = self._setup()
        state = self.store.sessions[response["session_id"]]
        contract = load_project_contract(self.project_dir)
        preflight = self.store.preflight_runtime_action(response["session_id"], "setup")

        self.assertEqual("v2", state.functionalmlds_contract_kind)
        self.assertEqual(contract["model_sha256"], state.functionalmlds_model_sha256)
        self.assertEqual(
            contract_runtime_fingerprint(contract),
            state.functionalmlds_contract_fingerprint,
        )
        self.assertEqual(
            select_runtime_action(contract["runtime_context"], "setup"),
            preflight["action"],
        )

    def test_project_drift_is_rejected_before_chat_state_mutation(self) -> None:
        response = self._setup()
        session_id = response["session_id"]
        state = self.store.sessions[session_id]
        before_history = copy.deepcopy(state.history)
        before_updated = state.updated_ms

        trace_path = self.project_dir / "trace_map.v2.json"
        trace = _read_json(trace_path)
        chat = next(
            item for item in trace["runtime_actions"] if item["action_kind"] == "chat"
        )
        chat["locator"]["value"] = "POST /chat-drifted"
        _write_json(trace_path, trace)

        with self.assertRaises(FunctionalMldsContractError):
            self.store.chat(
                {
                    "session_id": session_id,
                    "active_agent_id": next(iter(state.agents)),
                    "interaction_mode": "non_deictic",
                    "user_text": "Diese Anfrage darf keinen Zustand verändern.",
                }
            )
        self.assertEqual(before_history, state.history)
        self.assertEqual(before_updated, state.updated_ms)

    def test_logger_rejects_action_drift_without_writing_success_evidence(self) -> None:
        contract = load_project_contract(self.project_dir)
        expected = copy.deepcopy(
            select_runtime_action(contract["runtime_context"], "chat")
        )
        expected["runtime_action_id"] = "RA-TAMPERED"

        with self.assertRaisesRegex(FunctionalMldsContractError, "action drift"):
            log_backend_event(
                project_manager=self.store.project_manager,
                project_id=CASE_ID,
                action_kind="chat",
                event_type="must_not_be_written",
                session_id="SESSION-HARDENING",
                agent_id=None,
                input_summary={},
                output_summary={"accepted": True},
                expected_contract_fingerprint=contract_runtime_fingerprint(contract),
                expected_action=expected,
            )
        self.assertFalse((self.project_dir / "runtime_logs" / "events.jsonl").exists())
        self.assertFalse(
            (self.project_dir / "runtime_logs" / "runtime_validation.v2.jsonl").exists()
        )

    def test_two_file_append_rolls_back_both_files_on_local_failure(self) -> None:
        event_path = self.root / "logs" / "events.jsonl"
        validation_path = self.root / "logs" / "runtime_validation.v2.jsonl"
        event_path.parent.mkdir(parents=True)
        event_path.write_text('{"old":"event"}\n', encoding="utf-8")
        validation_path.write_text('{"old":"validation"}\n', encoding="utf-8")
        old_event = event_path.read_bytes()
        old_validation = validation_path.read_bytes()
        calls = 0

        def fail_second_fsync(_: int) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated validation fsync failure")

        with mock.patch("backend.runtime_trace.os.fsync", side_effect=fail_second_fsync):
            with self.assertRaisesRegex(OSError, "simulated"):
                _append_jsonl_transaction(
                    event_path,
                    [{"new": "event"}],
                    validation_path,
                    [{"new": "validation"}],
                )

        self.assertEqual(old_event, event_path.read_bytes())
        self.assertEqual(old_validation, validation_path.read_bytes())

    def test_http_chat_rolls_back_session_if_v2_evidence_commit_fails(self) -> None:
        response = self._setup("SESSION-HTTP-ROLLBACK")
        session_id = response["session_id"]
        state = self.store.sessions[session_id]
        before = self.store.snapshot_session_mutation(session_id)

        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        thread = threading.Thread(
            target=start_http_server,
            args=("127.0.0.1", port, self.store),
            daemon=True,
        )
        thread.start()
        health_url = f"http://127.0.0.1:{port}/health"
        for _ in range(50):
            try:
                with urllib.request.urlopen(health_url, timeout=0.2):
                    break
            except Exception:
                time.sleep(0.02)
        else:
            self.fail("test HTTP server did not start")

        body = json.dumps(
            {
                "session_id": session_id,
                "active_agent_id": next(iter(state.agents)),
                "interaction_mode": "non_deictic",
                "user_text": "Rollback-Test",
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/chat",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with mock.patch(
            "backend.server.log_backend_events",
            side_effect=OSError("simulated evidence failure"),
        ):
            with self.assertRaises(urllib.error.HTTPError) as raised:
                urllib.request.urlopen(request, timeout=3)
        self.assertEqual(500, raised.exception.code)
        self.assertEqual(before, self.store.snapshot_session_mutation(session_id))


if __name__ == "__main__":
    unittest.main()
