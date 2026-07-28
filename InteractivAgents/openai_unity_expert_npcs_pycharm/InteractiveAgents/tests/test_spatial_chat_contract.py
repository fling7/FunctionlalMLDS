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

from backend.functionalmlds_v2_runtime import FunctionalMldsContractError  # noqa: E402
from backend.kb import KnowledgeBase  # noqa: E402
from backend.projects import ProjectManager  # noqa: E402
from backend.state import SessionStore  # noqa: E402


CASE_ID = "classroom_dinosaur"
SOURCE_PROJECT = BACKEND_ROOT / "projects" / CASE_ID
DINO_ENTITY_ID = "ENT-ASSET-DINOSAUR_SKELETON"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


class _ScriptedOpenAI:
    api_key = "offline"
    timeout_seconds = 1

    def __init__(self) -> None:
        self.calls = []
        self.response = {
            "say": "Das ist das Dinosaurierskelett.",
            "handoff_to": None,
            "handoff_reason": None,
            "handoff_brief": None,
            "confidence": 1.0,
        }

    def create_structured_json(self, **kwargs: object):
        self.calls.append(kwargs)
        parsed = copy.deepcopy(self.response)
        return parsed, {"id": "offline-response"}, json.dumps(parsed)


class SpatialChatContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="functionalmlds-spatial-chat-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.projects_root = self.root / "projects"
        self.project_dir = self.projects_root / CASE_ID
        shutil.copytree(SOURCE_PROJECT, self.project_dir)

        manager = ProjectManager(
            root=self.projects_root,
            template_room_plan=self.project_dir / "room_plan.json",
            template_agents=self.project_dir / "agents.json",
        )
        self.openai = _ScriptedOpenAI()
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
            openai=self.openai,
            project_manager=manager,
        )

    def _setup(self, session_id: str = "SESSION-SPATIAL") -> dict:
        return self.store.setup_from_request(
            {"project_id": CASE_ID, "session_id": session_id}
        )

    @staticmethod
    def _context(pinned_hash: str, **overrides: object) -> dict:
        context = {
            "model_sha256": pinned_hash,
            "state": "resolved",
            "entity_id": DINO_ENTITY_ID,
            "source_object_id": "dinosaur_skeleton",
            "object_group_id": "decor",
            "zone_id": "dinosaur_display_zone",
            "hit_position": {"x": 2.1, "y": 1.4, "z": 4.2},
            "distance_m": 3.25,
            "selection_modality": "desktop_ray",
            "ambiguity_reason": "",
            "candidate_entity_ids": [DINO_ENTITY_ID],
        }
        context.update(overrides)
        return context

    def test_resolved_context_routes_by_asset_and_returns_model_evidence(self) -> None:
        # agents.json is only a projection.  Even if its handoff list is widened,
        # setup must replace it with the handoffTarget relation from the V2 model.
        agents_path = self.project_dir / "agents.json"
        agents = _read_json(agents_path)
        agents["agents"][0]["handoff_targets"] = [
            "reading_area_guide",
            "exhibit_interpreter",
            "decorative_zone_ambassador",
        ]
        _write_json(agents_path, agents)

        setup = self._setup()
        state = self.store.sessions[setup["session_id"]]
        self.assertEqual(
            ["reading_area_guide", "exhibit_interpreter"],
            state.agents["teacher_agent"].handoff_targets,
        )

        response = self.store.chat(
            {
                "session_id": setup["session_id"],
                "active_agent_id": "teacher_agent",
                "user_text": "Was ist das?",
                "interaction_mode": "deictic",
                "spatial_context": self._context(setup["model_sha256"]),
            }
        )

        self.assertEqual("exhibit_interpreter", response["active_agent_id"])
        self.assertEqual("spatial_route", response["handoff"]["kind"])
        self.assertEqual("teacher_agent", response["handoff"]["from"])
        self.assertEqual("exhibit_interpreter", response["handoff"]["to"])
        self.assertEqual("asset", response["routing"]["priority"])
        self.assertEqual(
            DINO_ENTITY_ID,
            response["grounding"]["selected_entity_id"],
        )
        self.assertEqual(
            "dinosaur_skeleton",
            response["grounding"]["selected_source_object_id"],
        )
        self.assertIn(DINO_ENTITY_ID, response["grounded_entity_ids"])
        self.assertIn("ENT-GROUP-DECOR", response["grounded_entity_ids"])
        self.assertIn(
            "ENT-ZONE-DINOSAUR_DISPLAY_ZONE",
            response["grounded_entity_ids"],
        )
        relations = {
            item["relation"] for item in response["grounding_evidence"]
        }
        self.assertEqual(
            {
                "selected_scene_object",
                "objectGroup",
                "zone_contains_source_object",
            },
            relations,
        )
        self.assertIn("asset priority", response["routing_reason"])
        self.assertEqual(
            "exhibit_interpreter",
            response["events"][0]["agent_id"],
        )
        developer_text = "\n".join(
            str(item.get("content") or "")
            for item in self.openai.calls[0]["input_messages"]
            if item.get("role") == "developer"
        )
        self.assertIn("dinosaur_skeleton", developer_text)
        self.assertIn("ENT-ASSET-DINOSAUR_SKELETON", developer_text)

    def test_priority_falls_back_from_asset_to_group_then_zone(self) -> None:
        setup = self._setup()
        state = self.store.sessions[setup["session_id"]]
        grounding = self.store._validate_spatial_context(
            state,
            self._context(setup["model_sha256"]),
        )
        self.assertIsNotNone(grounding)
        original_agents = copy.deepcopy(
            state.functionalmlds_runtime_context["agents"]
        )

        route = self.store._resolve_spatial_route(
            state,
            "teacher_agent",
            grounding,
        )
        self.assertEqual("asset", route["priority"])

        for item in state.functionalmlds_runtime_context["agents"]:
            item["grounded_asset_ids"] = []
        route = self.store._resolve_spatial_route(
            state,
            "teacher_agent",
            grounding,
        )
        self.assertEqual("group", route["priority"])

        for item in state.functionalmlds_runtime_context["agents"]:
            item["grounded_object_group_ids"] = []
        route = self.store._resolve_spatial_route(
            state,
            "teacher_agent",
            grounding,
        )
        self.assertEqual("zone", route["priority"])
        state.functionalmlds_runtime_context["agents"] = original_agents

    def test_stale_unknown_ambiguous_and_contradictory_contexts_do_not_mutate(self) -> None:
        setup = self._setup()
        state = self.store.sessions[setup["session_id"]]
        before = self.store.snapshot_session_mutation(setup["session_id"])
        bad_contexts = (
            self._context(setup["model_sha256"], model_sha256="0" * 64),
            self._context(
                setup["model_sha256"],
                state="ambiguous",
                ambiguity_reason="two colliders overlap",
                candidate_entity_ids=[
                    DINO_ENTITY_ID,
                    "ENT-ASSET-PICTURE1",
                ],
            ),
            self._context(
                setup["model_sha256"],
                entity_id="ENT-ASSET-DOES-NOT-EXIST",
            ),
            self._context(
                setup["model_sha256"],
                source_object_id="picture1",
            ),
            self._context(
                setup["model_sha256"],
                object_group_id="furniture",
            ),
        )

        for index, spatial_context in enumerate(bad_contexts):
            with self.subTest(index=index):
                with self.assertRaises((ValueError, FunctionalMldsContractError)):
                    self.store.chat(
                        {
                            "session_id": setup["session_id"],
                            "active_agent_id": "teacher_agent",
                            "user_text": "Was ist das?",
                            "interaction_mode": "deictic",
                            "spatial_context": spatial_context,
                        }
                    )
                self.assertEqual(
                    before,
                    self.store.snapshot_session_mutation(setup["session_id"]),
                )
        self.assertEqual([], self.openai.calls)
        self.assertEqual([], state.history)

    def test_unmodeled_online_handoff_is_rejected_without_history_mutation(self) -> None:
        setup = self._setup()
        state = self.store.sessions[setup["session_id"]]
        before = self.store.snapshot_session_mutation(setup["session_id"])
        self.openai.response = {
            "say": "Ich versuche eine unzulässige Weiterleitung.",
            "handoff_to": "decorative_zone_ambassador",
            "handoff_reason": "not modeled",
            "handoff_brief": "must be rejected",
            "confidence": 0.1,
        }

        with self.assertRaisesRegex(ValueError, "nicht modellierten Handoff"):
            self.store.chat(
                {
                    "session_id": setup["session_id"],
                    "active_agent_id": "exhibit_interpreter",
                    "user_text": "Bitte leite mich falsch weiter.",
                    "interaction_mode": "non_deictic",
                }
            )

        self.assertEqual(
            before,
            self.store.snapshot_session_mutation(setup["session_id"]),
        )
        allowed_enum = self.openai.calls[0]["schema"]["properties"]["handoff_to"][
            "oneOf"
        ][0]["enum"]
        self.assertEqual(["teacher_agent"], allowed_enum)

    def test_non_deictic_chat_has_no_grounding_evidence(self) -> None:
        setup = self._setup()
        response = self.store.chat(
            {
                "session_id": setup["session_id"],
                "active_agent_id": "exhibit_interpreter",
                "interaction_mode": "non_deictic",
                "user_text": "Erzähle mir etwas über das Exponat.",
            }
        )

        self.assertEqual("exhibit_interpreter", response["active_agent_id"])
        self.assertEqual("non_deictic", response["interaction_mode"])
        self.assertEqual(
            {
                "runtime_binding_id",
                "runtime_action_id",
                "capability_id",
                "capability_use_id",
            },
            set(response["model_binding"]),
        )
        for field_name in (
            "grounded_entity_ids",
            "grounding_evidence",
            "routing_reason",
            "grounding",
            "routing",
        ):
            self.assertNotIn(field_name, response)
        self.assertEqual(2, len(self.store.sessions[setup["session_id"]].history))

    def test_v2_requires_explicit_mode_and_deictic_context_without_mutation(self) -> None:
        setup = self._setup()
        before = self.store.snapshot_session_mutation(setup["session_id"])
        payloads = (
            {
                "session_id": setup["session_id"],
                "active_agent_id": "teacher_agent",
                "user_text": "Was ist das?",
            },
            {
                "session_id": setup["session_id"],
                "active_agent_id": "teacher_agent",
                "user_text": "Was ist das?",
                "interaction_mode": "deictic",
            },
            {
                "session_id": setup["session_id"],
                "active_agent_id": "teacher_agent",
                "user_text": "Allgemeine Frage.",
                "interaction_mode": "invalid",
            },
        )
        for index, payload in enumerate(payloads):
            with self.subTest(index=index):
                with self.assertRaises(ValueError):
                    self.store.chat(payload)
                self.assertEqual(
                    before,
                    self.store.snapshot_session_mutation(setup["session_id"]),
                )
        self.assertEqual([], self.openai.calls)

    def test_non_deictic_rejects_spatial_context_without_mutation(self) -> None:
        setup = self._setup()
        before = self.store.snapshot_session_mutation(setup["session_id"])
        with self.assertRaisesRegex(ValueError, "non_deictic"):
            self.store.chat(
                {
                    "session_id": setup["session_id"],
                    "active_agent_id": "teacher_agent",
                    "user_text": "Allgemeine Frage.",
                    "interaction_mode": "non_deictic",
                    "spatial_context": self._context(setup["model_sha256"]),
                }
            )
        self.assertEqual(
            before,
            self.store.snapshot_session_mutation(setup["session_id"]),
        )
        self.assertEqual([], self.openai.calls)

    def test_invalid_v2_active_agent_fails_closed(self) -> None:
        setup = self._setup()
        before = self.store.snapshot_session_mutation(setup["session_id"])
        with self.assertRaisesRegex(ValueError, "active_agent_id"):
            self.store.chat(
                {
                    "session_id": setup["session_id"],
                    "active_agent_id": "not-in-model",
                    "user_text": "Allgemeine Frage.",
                    "interaction_mode": "non_deictic",
                }
            )
        self.assertEqual(
            before,
            self.store.snapshot_session_mutation(setup["session_id"]),
        )
        self.assertEqual([], self.openai.calls)

    def test_spatial_size_limits_fail_closed(self) -> None:
        setup = self._setup()
        before = self.store.snapshot_session_mutation(setup["session_id"])
        oversized_contexts = (
            self._context(
                setup["model_sha256"],
                ambiguity_reason="x" * 513,
            ),
            self._context(
                setup["model_sha256"],
                candidate_entity_ids=[DINO_ENTITY_ID] * 17,
            ),
            self._context(
                setup["model_sha256"],
                entity_id="x" * 257,
            ),
            self._context(
                setup["model_sha256"],
                distance_m=1_000_001,
            ),
        )
        for index, spatial_context in enumerate(oversized_contexts):
            with self.subTest(index=index):
                with self.assertRaises(ValueError):
                    self.store.chat(
                        {
                            "session_id": setup["session_id"],
                            "active_agent_id": "teacher_agent",
                            "user_text": "Was ist das?",
                            "interaction_mode": "deictic",
                            "spatial_context": spatial_context,
                        }
                    )
                self.assertEqual(
                    before,
                    self.store.snapshot_session_mutation(setup["session_id"]),
                )
        self.assertEqual([], self.openai.calls)

    def test_whitespace_handoff_is_normalized_to_none(self) -> None:
        setup = self._setup()
        self.openai.response = {
            "say": "Direkte Antwort.",
            "handoff_to": "   ",
            "handoff_reason": "   ",
            "handoff_brief": "   ",
            "confidence": 1.0,
        }
        response = self.store.chat(
            {
                "session_id": setup["session_id"],
                "active_agent_id": "exhibit_interpreter",
                "user_text": "Allgemeine Frage.",
                "interaction_mode": "non_deictic",
            }
        )
        self.assertIsNone(response["handoff"])
        self.assertEqual("exhibit_interpreter", response["active_agent_id"])

    def test_legacy_agents_without_allow_list_keep_all_other_handoff_targets(self) -> None:
        room_plan = _read_json(self.project_dir / "room_plan.json")
        legacy = self.store.create_session(
            room_plan=room_plan,
            agent_dicts=[
                {
                    "id": "legacy_a",
                    "display_name": "Legacy A",
                    "persona": "Entry agent.",
                },
                {
                    "id": "legacy_b",
                    "display_name": "Legacy B",
                    "persona": "Specialist.",
                },
            ],
            session_id="SESSION-LEGACY-HANDOFF",
        )
        self.assertEqual(
            ["legacy_b"],
            self.store._allowed_handoff_ids(legacy, legacy.agents["legacy_a"]),
        )
        self.openai.response = {
            "say": "Ich leite weiter.",
            "handoff_to": "legacy_b",
            "handoff_reason": "specialist",
            "handoff_brief": "question",
            "confidence": 1.0,
        }
        result = self.store._call_agent(
            legacy,
            legacy.agents["legacy_a"],
            [{"role": "user", "content": "Frage"}],
            allow_handoff=True,
        )
        self.assertEqual("legacy_b", result["handoff_to"])
        allowed_enum = self.openai.calls[-1]["schema"]["properties"]["handoff_to"][
            "oneOf"
        ][0]["enum"]
        self.assertEqual(["legacy_b"], allowed_enum)
        self.openai.response = {
            "say": "Legacy fallback.",
            "handoff_to": None,
            "handoff_reason": None,
            "handoff_brief": None,
            "confidence": 1.0,
        }
        response = self.store.chat(
            {
                "session_id": legacy.session_id,
                "active_agent_id": "missing-legacy-agent",
                "user_text": "Legacy request without interaction marker.",
            }
        )
        self.assertEqual("legacy_a", response["active_agent_id"])
        self.assertNotIn("interaction_mode", response)


if __name__ == "__main__":
    unittest.main()
