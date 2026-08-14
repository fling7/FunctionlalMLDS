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
from backend.openai_client import OpenAIHTTPError  # noqa: E402
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


class _JsonFallbackHandoffOpenAI:
    api_key = "offline"
    timeout_seconds = 1

    def __init__(self, responses: list[dict]) -> None:
        self.structured_calls = []
        self.json_calls = []
        self.responses = copy.deepcopy(responses)

    def create_structured_json(self, **kwargs: object):
        self.structured_calls.append(kwargs)
        raise OpenAIHTTPError(400, "structured output unsupported")

    def create_json_object(self, **kwargs: object):
        self.json_calls.append(kwargs)
        parsed = copy.deepcopy(self.responses[len(self.json_calls) - 1])
        return parsed, {"id": f"json-{len(self.json_calls)}"}, json.dumps(parsed)


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
        targetless_by_provider = {
            item["provider_entity_id"]: item for item in targetless
        }
        self.assertEqual(len(providers), len(targetless))
        self.assertEqual(providers, set(targetless_by_provider))

        handoffs = runtime_actions_for_kind(self.runtime, "handoff")
        targetless_handoffs = [item for item in handoffs if not item["target_ids"]]
        targetless_handoffs_by_provider = {
            item["provider_entity_id"]: item for item in targetless_handoffs
        }
        self.assertEqual(len(providers), len(targetless_handoffs))
        self.assertEqual(providers, set(targetless_handoffs_by_provider))

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
                        targetless_by_provider[provider]["capability_use_id"],
                        selected["capability_use_id"],
                    )
                    self.assertEqual(provider, selected["provider_entity_id"])
                    handoff = select_runtime_action(
                        self.runtime,
                        "handoff",
                        provider_entity_id=provider,
                        require_targetless=True,
                    )
                    self.assertEqual([], handoff["target_ids"])
                    self.assertEqual(
                        targetless_handoffs_by_provider[provider]["capability_use_id"],
                        handoff["capability_use_id"],
                    )
                    self.assertEqual(provider, handoff["provider_entity_id"])

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
        expected_providers = {
            item["entity_id"] for item in self.runtime["agents"]
        }
        self.assertEqual(len(expected_providers), len(targetless))
        self.assertEqual(
            expected_providers,
            {item["provider_entity_id"] for item in targetless},
        )

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

    def test_every_agent_can_directly_handoff_to_every_other_specialist(self) -> None:
        agents = {
            item["source_agent_id"]: item
            for item in self.runtime["agents"]
        }
        all_ids = set(agents)
        for source_id, agent in agents.items():
            with self.subTest(source=source_id):
                self.assertEqual(
                    all_ids - {source_id},
                    set(agent["handoff_target_source_agent_ids"]),
                )

        tactile = agents["tactile_guide"]
        self.assertIn("heritage_educator", tactile["handoff_target_source_agent_ids"])

    def test_loaded_contract_hashes_are_pinned(self) -> None:
        self.assertEqual("v2", self.contract["kind"])
        self.assertEqual(
            self.contract["model_sha256"],
            self.runtime["model_sha256"],
        )


class KaesesteinpilzRuntimeHandoffTests(unittest.TestCase):
    def _build_store(self, root: Path, openai=None):
        projects_root = root / "projects"
        project_dir = projects_root / PROJECT_ID
        shutil.copytree(SOURCE_PROJECT, project_dir)
        manager = ProjectManager(
            root=projects_root,
            template_room_plan=project_dir / "room_plan.json",
            template_agents=project_dir / "agents.json",
        )
        openai = openai or _ModelProducedHandoffOpenAI()
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
                        ["anyOf"][0]["enum"],
                    )
                    self.assertEqual(
                        {"type": "null"},
                        openai.calls[1]["schema"]["properties"]["handoff_to"],
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

    def test_all_modeled_directed_handoffs_execute_in_both_memory_modes(self) -> None:
        runtime = load_project_contract(SOURCE_PROJECT)["runtime_context"]
        agent_ids = [item["source_agent_id"] for item in runtime["agents"]]
        expected_agent_ids = {
            "welcome_host",
            "cheese_expert",
            "tactile_guide",
            "heritage_educator",
            "lounge_host",
        }
        self.assertEqual(expected_agent_ids, set(agent_ids))
        self.assertEqual(5, len(agent_ids))
        executed_pairs = 0
        with tempfile.TemporaryDirectory(
            prefix="functionalmlds-kaesesteinpilz-all-handoffs-"
        ) as temp_dir:
            store, openai = self._build_store(Path(temp_dir))
            for memory_mode in ("shared_history", "agent_private_history"):
                for source_id in agent_ids:
                    for target_id in agent_ids:
                        if source_id == target_id:
                            continue
                        with self.subTest(
                            memory_mode=memory_mode,
                            source=source_id,
                            target=target_id,
                        ):
                            executed_pairs += 1
                            openai.calls.clear()
                            openai.responses = [
                                {
                                    "say": f"Ich leite an {target_id} weiter.",
                                    "handoff_to": target_id,
                                    "handoff_reason": "modellierter Spezialist",
                                    "handoff_brief": "Weiterleitungstest",
                                    "confidence": 1.0,
                                },
                                {
                                    "say": "Ich habe die Frage uebernommen.",
                                    "handoff_to": None,
                                    "handoff_reason": None,
                                    "handoff_brief": None,
                                    "confidence": 1.0,
                                },
                            ]
                            session_id = (
                                f"SESSION-{memory_mode}-{source_id}-{target_id}"
                            )
                            setup = store.setup_from_request(
                                {
                                    "project_id": PROJECT_ID,
                                    "session_id": session_id,
                                    "memory_mode": memory_mode,
                                }
                            )
                            response = store.chat(
                                {
                                    "session_id": setup["session_id"],
                                    "active_agent_id": source_id,
                                    "interaction_mode": "non_deictic",
                                    "user_text": f"Bitte leite mich an {target_id}.",
                                },
                                include_runtime_actions=True,
                            )

                            self.assertEqual(target_id, response["active_agent_id"])
                            self.assertEqual(source_id, response["handoff"]["from"])
                            self.assertEqual(target_id, response["handoff"]["to"])
                            self.assertIs(response["handoff"]["modeled_handoff"], True)
                            self.assertIn("handoff_model_binding", response)
                            self.assertEqual(2, len(response["events"]))
                            self.assertEqual(2, len(openai.calls))
                            allowed_schema = openai.calls[0]["schema"]["properties"][
                                "handoff_to"
                            ]
                            self.assertIn("anyOf", allowed_schema)
                            self.assertNotIn("oneOf", allowed_schema)
                            self.assertEqual(
                                set(agent_ids) - {source_id},
                                set(allowed_schema["anyOf"][0]["enum"]),
                            )
        self.assertEqual(40, executed_pairs)

    def test_json_fallback_canonicalizes_cow_role_to_heritage_educator(self) -> None:
        for memory_mode in ("shared_history", "agent_private_history"):
            with self.subTest(memory_mode=memory_mode):
                fallback_openai = _JsonFallbackHandoffOpenAI(
                    [
                        {
                            "say": "Ich leite dich an den Kuhbetreuer weiter.",
                            "handoff_to": "dairy_cow_caretaker",
                            "handoff_reason": "Kuh",
                            "handoff_brief": "Frage zur Kuh",
                            "confidence": 0.9,
                        },
                        {
                            "say": "Ich erklaere dir gern die Milchkuh.",
                            "handoff_to": None,
                            "handoff_reason": None,
                            "handoff_brief": None,
                            "confidence": 1.0,
                        },
                    ]
                )
                with tempfile.TemporaryDirectory(
                    prefix="functionalmlds-kaesesteinpilz-cow-alias-"
                ) as temp_dir:
                    store, _ = self._build_store(
                        Path(temp_dir),
                        openai=fallback_openai,
                    )
                    setup = store.setup_from_request(
                        {
                            "project_id": PROJECT_ID,
                            "session_id": f"SESSION-COW-ALIAS-{memory_mode}",
                            "memory_mode": memory_mode,
                        }
                    )
                    response = store.chat(
                        {
                            "session_id": setup["session_id"],
                            "active_agent_id": "welcome_host",
                            "interaction_mode": "non_deictic",
                            "user_text": "Leite mich zu dem, der die Kuh betreut.",
                        },
                        include_runtime_actions=True,
                    )

                    self.assertEqual("heritage_educator", response["active_agent_id"])
                    self.assertEqual("welcome_host", response["handoff"]["from"])
                    self.assertEqual("heritage_educator", response["handoff"]["to"])
                    self.assertIs(response["handoff"]["modeled_handoff"], True)
                    self.assertIn("handoff_model_binding", response)
                    self.assertNotIn(
                        "dairy_cow_caretaker",
                        json.dumps(response),
                    )
                    self.assertEqual(2, len(fallback_openai.structured_calls))
                    self.assertEqual(2, len(fallback_openai.json_calls))

    def test_json_fallback_suppresses_invented_self_handoff(self) -> None:
        fallback_openai = _JsonFallbackHandoffOpenAI(
            [
                {
                    "say": "Ich leite dich an den Kuhbetreuer weiter.",
                    "handoff_to": "dairy_cow_caretaker",
                    "handoff_reason": "Kuh",
                    "handoff_brief": "Frage zur Kuh",
                    "confidence": 0.9,
                }
            ]
        )
        with tempfile.TemporaryDirectory(
            prefix="functionalmlds-kaesesteinpilz-cow-self-alias-"
        ) as temp_dir:
            store, _ = self._build_store(Path(temp_dir), openai=fallback_openai)
            setup = store.setup_from_request(
                {
                    "project_id": PROJECT_ID,
                    "session_id": "SESSION-COW-SELF-ALIAS",
                    "memory_mode": "shared_history",
                }
            )
            response = store.chat(
                {
                    "session_id": setup["session_id"],
                    "active_agent_id": "heritage_educator",
                    "interaction_mode": "non_deictic",
                    "user_text": "Leite mich zu dem, der die Kuh betreut.",
                },
                include_runtime_actions=True,
            )

            self.assertEqual("heritage_educator", response["active_agent_id"])
            self.assertIsNone(response["handoff"])
            self.assertNotIn("handoff_model_binding", response)
            self.assertIn("bereits zustaendig", response["events"][0]["text"])
            self.assertNotIn("dairy_cow_caretaker", json.dumps(response))
            self.assertEqual(1, len(fallback_openai.structured_calls))
            self.assertEqual(1, len(fallback_openai.json_calls))

    def test_json_fallback_keeps_existing_spatial_cow_route(self) -> None:
        fallback_openai = _JsonFallbackHandoffOpenAI(
            [
                {
                    "say": "Ich leite dich an den Kuhbetreuer weiter.",
                    "handoff_to": "dairy_cow_caretaker",
                    "handoff_reason": "Kuh",
                    "handoff_brief": "Frage zur Kuh",
                    "confidence": 0.9,
                }
            ]
        )
        with tempfile.TemporaryDirectory(
            prefix="functionalmlds-kaesesteinpilz-cow-spatial-alias-"
        ) as temp_dir:
            store, _ = self._build_store(Path(temp_dir), openai=fallback_openai)
            setup = store.setup_from_request(
                {
                    "project_id": PROJECT_ID,
                    "session_id": "SESSION-COW-SPATIAL-ALIAS",
                    "memory_mode": "shared_history",
                }
            )
            response = store.chat(
                {
                    "session_id": setup["session_id"],
                    "active_agent_id": "welcome_host",
                    "interaction_mode": "deictic",
                    "user_text": "Wer betreut das hier?",
                    "spatial_context": {
                        "model_sha256": setup["model_sha256"],
                        "state": "resolved",
                        "entity_id": "ENT-ASSET-STEINPILZ_DAIRY_COW",
                        "source_object_id": "steinpilz_dairy_cow",
                        "hit_position": {"x": -1.75, "y": 0.8, "z": -3.45},
                        "distance_m": 2.0,
                        "selection_modality": "desktop_ray",
                        "candidate_entity_ids": [
                            "ENT-ASSET-STEINPILZ_DAIRY_COW"
                        ],
                    },
                },
                include_runtime_actions=True,
            )

            self.assertEqual("heritage_educator", response["active_agent_id"])
            self.assertEqual("welcome_host", response["handoff"]["from"])
            self.assertEqual("heritage_educator", response["handoff"]["to"])
            self.assertEqual("spatial_route", response["handoff"]["kind"])
            self.assertIs(response["handoff"]["modeled_handoff"], True)
            self.assertIn("handoff_model_binding", response)
            self.assertNotIn("dairy_cow_caretaker", json.dumps(response))
            self.assertEqual(1, len(fallback_openai.structured_calls))
            self.assertEqual(1, len(fallback_openai.json_calls))

    def test_json_fallback_unknown_role_never_becomes_a_handoff(self) -> None:
        fallback_openai = _JsonFallbackHandoffOpenAI(
            [
                {
                    "say": "Ich leite dich an einen erfundenen Agenten weiter.",
                    "handoff_to": "astronomy_oracle",
                    "handoff_reason": "unbekannt",
                    "handoff_brief": "unbekannt",
                    "confidence": 0.2,
                }
            ]
        )
        with tempfile.TemporaryDirectory(
            prefix="functionalmlds-kaesesteinpilz-unknown-alias-"
        ) as temp_dir:
            store, _ = self._build_store(Path(temp_dir), openai=fallback_openai)
            setup = store.setup_from_request(
                {
                    "project_id": PROJECT_ID,
                    "session_id": "SESSION-UNKNOWN-ALIAS",
                    "memory_mode": "shared_history",
                }
            )
            response = store.chat(
                {
                    "session_id": setup["session_id"],
                    "active_agent_id": "welcome_host",
                    "interaction_mode": "non_deictic",
                    "user_text": "Leite mich an die Dekorationsperson weiter.",
                },
                include_runtime_actions=True,
            )

            self.assertEqual("welcome_host", response["active_agent_id"])
            self.assertIsNone(response["handoff"])
            self.assertNotIn("handoff_model_binding", response)
            self.assertNotIn("astronomy_oracle", json.dumps(response))
            self.assertIn("keinem eindeutigen", response["events"][0]["text"])
            self.assertEqual(1, len(fallback_openai.structured_calls))
            self.assertEqual(1, len(fallback_openai.json_calls))

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

    def test_narrated_route_is_normalized_to_real_handoff(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="functionalmlds-kaesesteinpilz-narrated-handoff-"
        ) as temp_dir:
            store, openai = self._build_store(Path(temp_dir))
            openai.responses = [
                {
                    "say": (
                        "Natürlich! Für detaillierte Fragen rund um Käse leite ich "
                        "dich an unseren Käse-Experten weiter. Möchtest du etwas "
                        "Bestimmtes über Sorten, Herstellung oder Verkostung wissen?"
                    ),
                    "handoff_to": None,
                    "handoff_reason": None,
                    "handoff_brief": None,
                    "confidence": 0.8,
                },
                {
                    "say": "Gerne erkläre ich dir die Käseherstellung.",
                    "handoff_to": None,
                    "handoff_reason": None,
                    "handoff_brief": None,
                    "confidence": 1.0,
                },
            ]
            setup = store.setup_from_request(
                {
                    "project_id": PROJECT_ID,
                    "session_id": "SESSION-NARRATED-HANDOFF",
                    "memory_mode": "shared_history",
                }
            )

            response = store.chat(
                {
                    "session_id": setup["session_id"],
                    "active_agent_id": "welcome_host",
                    "interaction_mode": "non_deictic",
                    "user_text": "Leite mich an den Käse-Experten.",
                },
                include_runtime_actions=True,
            )

            self.assertEqual("cheese_expert", response["active_agent_id"])
            self.assertEqual("welcome_host", response["handoff"]["from"])
            self.assertEqual("cheese_expert", response["handoff"]["to"])
            self.assertIs(response["handoff"]["modeled_handoff"], True)
            self.assertIn("handoff_model_binding", response)
            self.assertEqual(2, len(response["events"]))
            self.assertEqual(2, len(openai.calls))
            self.assertIn("Ich leite deine Frage", response["events"][0]["text"])
            self.assertNotIn("?", response["events"][0]["text"])
            self.assertIn("ausdruecklich", response["handoff"]["reason"])
            developer_prompt = openai.calls[0]["input_messages"][0]["content"]
            self.assertIn("KEIN Ersatz fuer den Handoff", developer_prompt)
            self.assertIn("stelle vorher keine Rueckfrage", developer_prompt)

    def test_negated_or_rejected_referral_never_forces_handoff(self) -> None:
        rejected_requests = (
            "Bitte leite mich nicht an den Kaese-Experten weiter.",
            "Ich moechte nicht zum Kaese-Experten gehen.",
            "Muss ich nicht mit dem Kaese-Experten sprechen?",
            "Ich lehne eine Weiterleitung zum Kaese-Experten ab.",
        )
        for index, user_text in enumerate(rejected_requests):
            with self.subTest(user_text=user_text), tempfile.TemporaryDirectory(
                prefix="functionalmlds-kaesesteinpilz-negated-handoff-"
            ) as temp_dir:
                store, openai = self._build_store(Path(temp_dir))
                openai.responses = [
                    {
                        "say": "Das beantworte ich direkt, ohne weiterzuleiten.",
                        "handoff_to": None,
                        "handoff_reason": None,
                        "handoff_brief": None,
                        "confidence": 1.0,
                    }
                ]
                setup = store.setup_from_request(
                    {
                        "project_id": PROJECT_ID,
                        "session_id": f"SESSION-NEGATED-HANDOFF-{index}",
                        "memory_mode": "shared_history",
                    }
                )

                response = store.chat(
                    {
                        "session_id": setup["session_id"],
                        "active_agent_id": "welcome_host",
                        "interaction_mode": "non_deictic",
                        "user_text": user_text,
                    },
                    include_runtime_actions=True,
                )

                self.assertEqual("welcome_host", response["active_agent_id"])
                self.assertIsNone(response["handoff"])
                self.assertNotIn("handoff_model_binding", response)
                self.assertEqual(1, len(response["events"]))
                self.assertEqual(1, len(openai.calls))


if __name__ == "__main__":
    unittest.main()
