"""Focused multi-UseCase runtime-trace and action-selection regression tests."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = (
    ROOT
    / "InteractivAgents"
    / "openai_unity_expert_npcs_pycharm"
    / "InteractiveAgents"
)
for import_root in (ROOT, BACKEND_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from backend.functionalmlds_v2_runtime import (  # noqa: E402
    FunctionalMldsContractError,
    _build_v2_runtime_context,
    _validate_v2_instance,
    _validate_v2_trace,
    runtime_actions_for_kind,
    select_runtime_action,
)
from backend.runtime_trace import log_backend_event  # noqa: E402
from tools.case_study_pipeline.functionalmlds_assembler import (  # noqa: E402
    assemble_functionalmlds_instance,
)
from tools.case_study_pipeline.functionalmlds_v2_assembler import (  # noqa: E402
    assemble_v2_instance,
)
from tools.case_study_pipeline.project_materializer import (  # noqa: E402
    build_trace_map_v2,
)


CASE_ID = "classroom_dinosaur"
CASE_DIR = ROOT / "output" / "case_studies" / CASE_ID


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class MultiScenarioV2RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        intermediate = CASE_DIR / "intermediate"
        cls.agent_roles = _read(
            intermediate / "agent_roles.generated.json"
        )
        v05 = assemble_functionalmlds_instance(
            case_id=CASE_ID,
            normalized_scene=_read(
                intermediate / "scene_graph.normalized.json"
            ),
            scene_semantics=_read(
                intermediate / "scene_semantics.json"
            ),
            agent_roles=cls.agent_roles,
        )
        cls.instance = assemble_v2_instance(v05)
        cls.model_sha256 = "A" * 64
        cls.trace = build_trace_map_v2(
            case_dir=CASE_DIR,
            project_dir=ROOT / "unused-multi-scenario-test-project",
            functionalmlds_instance=cls.instance,
            agent_roles=cls.agent_roles,
            model_sha256=cls.model_sha256,
        )
        cls.by_id = _validate_v2_instance(cls.instance)
        _validate_v2_trace(
            cls.trace,
            cls.by_id,
            cls.model_sha256,
            cls.instance,
        )
        cls.context = _build_v2_runtime_context(
            cls.instance,
            cls.trace,
            cls.model_sha256,
        )

    def test_each_use_case_has_one_main_scenario_and_each_chain_has_owner(self) -> None:
        use_cases = [
            item
            for item in self.instance["objects"]
            if item.get("type") == "UseCase"
        ]
        main_scenarios = [
            item
            for item in self.instance["objects"]
            if item.get("type") == "Scenario"
            and item.get("kind") == "main"
        ]
        self.assertGreater(len(use_cases), 1)
        self.assertEqual(len(use_cases), len(main_scenarios))
        self.assertEqual(
            {item["id"] for item in use_cases},
            set(self.trace["use_case_ids"]),
        )
        self.assertEqual(
            {item["id"] for item in main_scenarios},
            set(self.trace["main_scenario_ids"]),
        )
        for action in self.trace["runtime_actions"]:
            with self.subTest(action=action["capability_use_id"]):
                self.assertEqual(
                    "Scenario",
                    self.by_id[action["scenario_id"]]["type"],
                )
                self.assertEqual(
                    "UseCase",
                    self.by_id[action["use_case_id"]]["type"],
                )
                self.assertIn(
                    action["scenario_step_id"],
                    self.by_id[action["scenario_id"]]["step"],
                )

    def test_setup_is_unique_but_chat_and_handoff_are_asset_specific(self) -> None:
        setup = runtime_actions_for_kind(self.context, "setup")
        chats = runtime_actions_for_kind(self.context, "chat")
        handoffs = runtime_actions_for_kind(self.context, "handoff")
        self.assertEqual(1, len(setup))
        self.assertGreater(len(chats), 1)
        self.assertEqual(len(chats), len(handoffs))
        self.assertTrue(all(item["target_ids"] for item in chats))
        self.assertTrue(all(item["target_ids"] for item in handoffs))

    def test_deictic_selection_requires_both_trusted_target_and_provider(self) -> None:
        dinosaur_target = "ENT-ASSET-DINOSAUR_SKELETON"
        expected = next(
            item
            for item in runtime_actions_for_kind(self.context, "chat")
            if dinosaur_target in item["target_ids"]
        )
        selected = select_runtime_action(
            self.context,
            "chat",
            target_id=dinosaur_target,
            provider_entity_id=expected["provider_entity_id"],
        )
        self.assertEqual(expected, selected)
        with self.assertRaisesRegex(
            FunctionalMldsContractError,
            "no exact action mapping",
        ):
            select_runtime_action(
                self.context,
                "chat",
                target_id=dinosaur_target,
                provider_entity_id="ENT-AGENT-NOT-THE-ROUTED-PROVIDER",
            )

    def test_multi_chain_non_deictic_request_cannot_claim_an_asset_chain(self) -> None:
        provider = runtime_actions_for_kind(
            self.context,
            "chat",
        )[0]["provider_entity_id"]
        with self.assertRaisesRegex(
            FunctionalMldsContractError,
            "ambiguous action mappings",
        ):
            select_runtime_action(self.context, "chat")
        with self.assertRaisesRegex(
            FunctionalMldsContractError,
            "no exact action mapping",
        ):
            select_runtime_action(
                self.context,
                "chat",
                provider_entity_id=provider,
                require_targetless=True,
            )

    def test_single_chain_v2_context_remains_selectable(self) -> None:
        legacy_action = copy.deepcopy(
            runtime_actions_for_kind(self.context, "chat")[0]
        )
        legacy_action.pop("scenario_id", None)
        legacy_action.pop("use_case_id", None)
        legacy_context = {"runtime_actions": [legacy_action]}
        self.assertEqual(
            legacy_action,
            select_runtime_action(legacy_context, "chat"),
        )

    def test_trace_rejects_chain_claiming_the_wrong_scenario(self) -> None:
        mutated = copy.deepcopy(self.trace)
        chat = next(
            item
            for item in mutated["runtime_actions"]
            if item["action_kind"] == "chat"
        )
        chat["scenario_id"] = next(
            scenario_id
            for scenario_id in mutated["main_scenario_ids"]
            if scenario_id != chat["scenario_id"]
        )
        with self.assertRaisesRegex(
            FunctionalMldsContractError,
            "scenario_id does not own",
        ):
            _validate_v2_trace(
                mutated,
                self.by_id,
                self.model_sha256,
                self.instance,
            )

    def test_runtime_logger_commits_the_preselected_chain_not_an_arbitrary_kind(self) -> None:
        expected = runtime_actions_for_kind(self.context, "chat")[1]
        contract = {
            "kind": "v2",
            "model_version": "2.0.0-model",
            "profile": "executable",
            "model_sha256": self.model_sha256,
            "trace": {"case_id": CASE_ID},
            "runtime_context": self.context,
            "project": {},
        }

        class _Manager:
            def __init__(self, project_dir: Path) -> None:
                self.project_dir = project_dir

            def _project_dir(self, _project_id: str) -> Path:
                return self.project_dir

        with tempfile.TemporaryDirectory(
            prefix="multi-scenario-runtime-log-"
        ) as temporary:
            project_dir = Path(temporary) / "project"
            project_dir.mkdir()
            (project_dir / "project.json").write_text(
                json.dumps(
                    {"functionalmlds_model_version": "2.0.0-model"}
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "backend.runtime_trace.load_project_contract",
                return_value=contract,
            ):
                event = log_backend_event(
                    project_manager=_Manager(project_dir),
                    project_id=CASE_ID,
                    action_kind="chat",
                    event_type="multi_scenario_chat",
                    session_id="SESSION-MULTI",
                    agent_id=None,
                    input_summary={"mode": "deictic"},
                    output_summary={"accepted": True},
                    expected_action=expected,
                )
        assert event is not None
        for field_name in (
            "scenario_step_id",
            "capability_use_id",
            "capability_id",
            "provider_entity_id",
            "target_ids",
            "runtime_binding_id",
            "runtime_action_id",
        ):
            self.assertEqual(expected[field_name], event[field_name])


if __name__ == "__main__":
    unittest.main()
