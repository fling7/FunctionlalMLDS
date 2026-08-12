from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from backend.functionalmlds_v2_runtime import (  # noqa: E402
    load_project_contract,
    runtime_actions_for_kind,
    select_runtime_action,
)
from backend.kb import KnowledgeBase  # noqa: E402
from backend.projects import ProjectManager  # noqa: E402
from backend.state import SessionStore  # noqa: E402


PROJECT_ID = (
    "kaesestand_steinpilz_haptisch_chill_milcherlebnisraum_"
    "welcome_gruen_029e9a89"
)
SOURCE_PROJECT = BACKEND_ROOT / "projects" / PROJECT_ID


class _ModelProducedHandoffOpenAI:
    api_key = "offline"
    timeout_seconds = 1

    def __init__(self) -> None:
        self.calls = []
        self.responses = [
            {
                "say": "Dazu leite ich an den Käseexperten weiter.",
                "handoff_to": "cheese_expert",
                "handoff_reason": "Fachwissen zur Käseherstellung",
                "handoff_brief": "Der Gast fragt nach Käseherstellung.",
                "confidence": 0.9,
            },
            {
                "say": "Gerne erkläre ich die Käseherstellung.",
                "handoff_to": None,
                "handoff_reason": None,
                "handoff_brief": None,
                "confidence": 1.0,
            },
        ]

    def create_structured_json(self, **kwargs: object):
        self.calls.append(kwargs)
        parsed = copy.deepcopy(self.responses[len(self.calls) - 1])
        return parsed, {"id": f"offline-{len(self.calls)}"}, json.dumps(parsed)


class KaesesteinpilzCommunicationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = load_project_contract(BACKEND_ROOT / "projects" / PROJECT_ID)
        cls.runtime = cls.contract["runtime_context"]

    def test_setup_transport_is_uniquely_mapped(self) -> None:
        selected = select_runtime_action(self.runtime, "setup")
        self.assertEqual("setup", selected["action_kind"])

    def test_generic_text_and_voice_work_for_every_active_agent(self) -> None:
        chats = runtime_actions_for_kind(self.runtime, "chat")
        providers = {item["provider_entity_id"] for item in chats}
        targetless = [item for item in chats if not item["target_ids"]]
        self.assertEqual(1, len(targetless))

        for communication_kind in ("text", "voice"):
            for provider in providers:
                with self.subTest(kind=communication_kind, provider=provider):
                    selected = select_runtime_action(
                        self.runtime,
                        "chat",
                        provider_entity_id=provider,
                        require_targetless=True,
                    )
                    self.assertEqual(
                        targetless[0]["capability_use_id"],
                        selected["capability_use_id"],
                    )
                    handoff = select_runtime_action(
                        self.runtime,
                        "handoff",
                        provider_entity_id=provider,
                        require_targetless=True,
                    )
                    self.assertEqual([], handoff["target_ids"])

    def test_every_deictic_object_chat_is_uniquely_mapped(self) -> None:
        chats = runtime_actions_for_kind(self.runtime, "chat")
        object_chats = [item for item in chats if item["target_ids"]]
        self.assertGreater(len(object_chats), 0)

        for expected in object_chats:
            asset_id = next(
                item for item in expected["target_ids"] if item.startswith("ENT-ASSET-")
            )
            with self.subTest(target=asset_id):
                selected = select_runtime_action(
                    self.runtime,
                    "chat",
                    provider_entity_id=expected["provider_entity_id"],
                    target_id=asset_id,
                )
                self.assertEqual(
                    expected["capability_use_id"],
                    selected["capability_use_id"],
                )

    def test_every_deictic_handoff_is_uniquely_mapped(self) -> None:
        handoffs = runtime_actions_for_kind(self.runtime, "handoff")
        self.assertGreater(len(handoffs), 0)
        targetless = [item for item in handoffs if not item["target_ids"]]
        self.assertEqual(1, len(targetless))

        for expected in handoffs:
            if not expected["target_ids"]:
                continue
            asset_id = next(
                item for item in expected["target_ids"] if item.startswith("ENT-ASSET-")
            )
            with self.subTest(target=asset_id):
                selected = select_runtime_action(
                    self.runtime,
                    "handoff",
                    provider_entity_id=expected["provider_entity_id"],
                    target_id=asset_id,
                )
                self.assertEqual(
                    expected["capability_use_id"],
                    selected["capability_use_id"],
                )

    def test_loaded_contract_hashes_are_pinned(self) -> None:
        self.assertEqual("v2", self.contract["kind"])
        self.assertEqual(
            self.contract["model_sha256"],
            self.runtime["model_sha256"],
        )


class KaesesteinpilzRuntimeHandoffTests(unittest.TestCase):
    def _build_store(self, root: Path) -> tuple[SessionStore, _ModelProducedHandoffOpenAI]:
        projects_root = root / "projects"
        project_dir = projects_root / PROJECT_ID
        shutil.copytree(SOURCE_PROJECT, project_dir)
        manager = ProjectManager(
            root=projects_root,
            template_room_plan=project_dir / "room_plan.json",
            template_agents=project_dir / "agents.json",
        )
        openai = _ModelProducedHandoffOpenAI()
        return (
            SessionStore(
                max_history_turns=4,
                max_handoffs=1,
                kb=KnowledgeBase(root / "fallback-kb"),
                kb_max_snippets=2,
                model="offline",
                temperature=0.0,
                stt_model="offline",
                stt_language="de",
                stt_max_audio_bytes=1024,
                openai=openai,
                project_manager=manager,
            ),
            openai,
        )

    def test_non_deictic_model_handoff_uses_targetless_mapping_in_both_memory_modes(self) -> None:
        for memory_mode in ("shared_history", "agent_private_history"):
            with self.subTest(memory_mode=memory_mode):
                with tempfile.TemporaryDirectory(
                    prefix=f"functionalmlds-kaesesteinpilz-{memory_mode}-"
                ) as temp_dir:
                    store, openai = self._build_store(Path(temp_dir))
                    setup = store.setup_from_request(
                        {
                            "project_id": PROJECT_ID,
                            "session_id": f"SESSION-{memory_mode}",
                            "memory_mode": memory_mode,
                        }
                    )

                    response = store.chat(
                        {
                            "session_id": setup["session_id"],
                            "active_agent_id": "welcome_host",
                            "interaction_mode": "non_deictic",
                            "user_text": "Wie wird der Käse hergestellt?",
                        },
                        include_runtime_actions=True,
                    )

                    self.assertEqual("cheese_expert", response["active_agent_id"])
                    self.assertEqual(
                        {"from": "welcome_host", "to": "cheese_expert"},
                        {
                            "from": response["handoff"]["from"],
                            "to": response["handoff"]["to"],
                        },
                    )
                    self.assertEqual(2, len(response["events"]))
                    self.assertEqual(2, len(openai.calls))
                    self.assertIs(response["handoff"]["modeled_handoff"], True)
                    self.assertIn(
                        "cheese_expert",
                        openai.calls[0]["schema"]["properties"]["handoff_to"]
                        ["oneOf"][0]["enum"],
                    )
                    self.assertEqual(
                        [],
                        openai.calls[1]["schema"]["properties"]["handoff_to"]
                        ["oneOf"][0]["enum"],
                    )

                    runtime_handoff = response["_functionalmlds_runtime_actions"][
                        "handoff"
                    ]
                    runtime_chat = response["_functionalmlds_runtime_actions"][
                        "chat"
                    ]
                    self.assertEqual([], runtime_handoff["target_ids"])
                    self.assertEqual(
                        runtime_chat["capability_use_id"],
                        response["model_binding"]["capability_use_id"],
                    )
                    self.assertEqual(
                        runtime_handoff["capability_use_id"],
                        response["handoff_model_binding"]["capability_use_id"],
                    )
                    self.assertNotEqual(
                        response["model_binding"]["capability_use_id"],
                        response["handoff_model_binding"]["capability_use_id"],
                    )
                    expected = select_runtime_action(
                        store.sessions[setup["session_id"]].functionalmlds_runtime_context,
                        "handoff",
                        provider_entity_id="ENT-AGENT-WELCOME_HOST",
                        require_targetless=True,
                    )
                    self.assertEqual(
                        expected["capability_use_id"],
                        runtime_handoff["capability_use_id"],
                    )

    def test_direct_answer_omits_handoff_evidence(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="functionalmlds-kaesesteinpilz-no-handoff-"
        ) as temp_dir:
            store, openai = self._build_store(Path(temp_dir))
            openai.responses = [
                {
                    "say": "Das kann ich direkt beantworten.",
                    "handoff_to": None,
                    "handoff_reason": None,
                    "handoff_brief": None,
                    "confidence": 1.0,
                }
            ]
            setup = store.setup_from_request(
                {
                    "project_id": PROJECT_ID,
                    "session_id": "SESSION-NO-HANDOFF",
                    "memory_mode": "shared_history",
                }
            )

            response = store.chat(
                {
                    "session_id": setup["session_id"],
                    "active_agent_id": "welcome_host",
                    "interaction_mode": "non_deictic",
                    "user_text": "Wo bin ich hier?",
                },
                include_runtime_actions=True,
            )

            self.assertIsNone(response["handoff"])
            self.assertNotIn("handoff_model_binding", response)
            self.assertIn("model_binding", response)


if __name__ == "__main__":
    unittest.main()
