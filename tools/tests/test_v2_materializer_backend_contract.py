"""End-to-end regression tests for the materialized FunctionalMLDS V2 runtime contract.

The suite intentionally starts from the real v0.5 classroom fixture but performs every
assembly, materialization and runtime write inside temporary directories.  It therefore
tests the production bridge without modifying case-study artifacts or their runtime logs.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
BACKEND_APP_ROOT = (
    ROOT
    / "InteractivAgents"
    / "openai_unity_expert_npcs_pycharm"
    / "InteractiveAgents"
)
for import_root in (ROOT, BACKEND_APP_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from backend.functionalmlds_v2_runtime import (  # noqa: E402
    PLACEMENT_DEPLOYMENT_FIELDS,
    RUNTIME_CONTEXT_SCHEMA,
    V05_MODEL_VERSION,
    V2_MODEL_VERSION,
    FunctionalMldsContractError,
    load_project_contract,
    load_v2_document,
    select_runtime_action,
)
from backend.kb import KnowledgeBase  # noqa: E402
from backend.projects import ProjectManager  # noqa: E402
from backend.runtime_trace import log_backend_event  # noqa: E402
from backend.state import SessionStore  # noqa: E402
from tools.case_study_pipeline.agent_placement import (  # noqa: E402
    run_agent_placement_for_case,
)
from tools.case_study_pipeline.functionalmlds_v2_assembler import (  # noqa: E402
    run_v2_assembly,
)
from tools.case_study_pipeline.project_materializer import (  # noqa: E402
    V05_PROJECT_INSTANCE_FILENAME,
    V2_PROJECT_INSTANCE_FILENAME,
    V2_TRACE_SCHEMA,
    V2_TRACE_VERSION,
    materialize_project,
)


CASE_ID = "classroom_dinosaur"
REFERENCE_CASE = ROOT / "output" / "case_studies" / CASE_ID
V05_SOURCE_FILENAME = "functionalmlds.instance.generated.json"

RUNTIME_EVENT_SCHEMA_PATH = (
    ROOT / "tools" / "case_study_pipeline" / "schemas" / "runtime_event_v2.schema.json"
)
RUNTIME_VALIDATION_SCHEMA_PATH = (
    ROOT
    / "tools"
    / "case_study_pipeline"
    / "schemas"
    / "runtime_validation_v2.schema.json"
)

ACTION_ID_FIELDS = (
    "scenario_step_id",
    "capability_use_id",
    "capability_id",
    "provider_entity_id",
    "runtime_binding_id",
    "runtime_action_id",
)

EXPECTED_APPLICATION_ACTIONS = {
    "setup": {
        "scenario_step_id": "STEP-CLASSROOM_DINOSAUR-S09",
        "capability_use_id": "CU-CLASSROOM_DINOSAUR-S09-SETUP-INTERACTIVE-SESSION",
        "capability_id": "CAP-CLASSROOM_DINOSAUR-SETUP-INTERACTIVE-SESSION",
        "provider_entity_id": "ENT-CLASSROOM_DINOSAUR-RUNTIME-ORCHESTRATOR",
        "runtime_binding_id": "RB-CLASSROOM_DINOSAUR-SETUP-INTERACTIVE-SESSION",
        "runtime_action_id": "RA-CLASSROOM_DINOSAUR-BACKEND-SETUP",
    },
    "chat": {
        "scenario_step_id": "STEP-CLASSROOM_DINOSAUR-S11",
        "capability_use_id": "CU-CLASSROOM_DINOSAUR-S11-ANSWER-ROOM-GROUNDED-QUESTION",
        "capability_id": "CAP-CLASSROOM_DINOSAUR-ANSWER-ROOM-GROUNDED-QUESTION",
        "provider_entity_id": "ENT-CLASSROOM_DINOSAUR-RUNTIME-ORCHESTRATOR",
        "runtime_binding_id": "RB-CLASSROOM_DINOSAUR-ANSWER-ROOM-GROUNDED-QUESTION",
        "runtime_action_id": "RA-CLASSROOM_DINOSAUR-BACKEND-CHAT",
    },
    "handoff": {
        "scenario_step_id": "STEP-CLASSROOM_DINOSAUR-S12",
        "capability_use_id": "CU-CLASSROOM_DINOSAUR-S12-HANDOFF-TO-RESPONSIBLE-AGENT",
        "capability_id": "CAP-CLASSROOM_DINOSAUR-HANDOFF-TO-RESPONSIBLE-AGENT",
        "provider_entity_id": "ENT-CLASSROOM_DINOSAUR-RUNTIME-ORCHESTRATOR",
        "runtime_binding_id": "RB-CLASSROOM_DINOSAUR-HANDOFF-TO-RESPONSIBLE-AGENT",
        "runtime_action_id": "RA-CLASSROOM_DINOSAUR-BACKEND-CHAT-HANDOFF",
    },
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _json_lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


class FunctionalMldsV2MaterializerBackendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.event_validator = Draft202012Validator(
            _read_json(RUNTIME_EVENT_SCHEMA_PATH),
            format_checker=FormatChecker(),
        )
        cls.validation_validator = Draft202012Validator(
            _read_json(RUNTIME_VALIDATION_SCHEMA_PATH),
            format_checker=FormatChecker(),
        )

        cls.reference_v05_path = (
            REFERENCE_CASE / "functionalmlds" / V05_SOURCE_FILENAME
        )
        cls.reference_v05_sha256 = _sha256(cls.reference_v05_path)

        cls._base_temp = tempfile.TemporaryDirectory(prefix="functionalmlds-v2-e2e-base-")
        cls.addClassCleanup(cls._base_temp.cleanup)
        cls.base_root = Path(cls._base_temp.name)
        cls.base_case_dir = cls.base_root / "cases" / CASE_ID

        for relative_dir in ("input", "intermediate", "interactive_agents_project/kb"):
            source = REFERENCE_CASE / relative_dir
            destination = cls.base_case_dir / relative_dir
            shutil.copytree(source, destination)

        # The checked-in case remains an immutable v0.5 fixture.  Regenerate the
        # strict V2 placement artifact only inside this suite's temporary copy.
        placement_result = run_agent_placement_for_case(cls.base_case_dir)
        if placement_result["status"] != "success":
            raise AssertionError(placement_result)

        copied_v05_path = (
            cls.base_case_dir / "functionalmlds" / V05_SOURCE_FILENAME
        )
        copied_v05_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cls.reference_v05_path, copied_v05_path)
        assembly = run_v2_assembly(copied_v05_path, copied_v05_path.parent)
        if assembly["status"] != "success":
            raise AssertionError(assembly)

        cls.base_backend_root = cls.base_root / "backend"
        cls.base_project_paths = materialize_project(
            case_dir=cls.base_case_dir,
            backend_root=cls.base_backend_root,
        )
        cls.base_project_dir = cls.base_project_paths["project_dir"]

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="functionalmlds-v2-e2e-test-")
        self.addCleanup(self._temp.cleanup)
        self.test_root = Path(self._temp.name)
        self.case_dir = self.test_root / "cases" / CASE_ID
        self.backend_root = self.test_root / "backend"
        self.project_dir = self.backend_root / "projects" / CASE_ID
        shutil.copytree(self.base_case_dir, self.case_dir)
        shutil.copytree(self.base_project_dir, self.project_dir)

        # Runtime logging derives its target from this source-model path.  Repoint it
        # to the per-test case so even successful log tests cannot touch the fixture.
        project = _read_json(self.project_dir / "project.json")
        project["functionalmlds_trace_path"] = str(
            self.case_dir / "functionalmlds" / V05_SOURCE_FILENAME
        )
        project["functionalmlds_case_dir"] = str(self.case_dir)
        project["source_mlds_path"] = str(self.case_dir / "input" / "source_mlds.json")
        _write_json(self.project_dir / "project.json", project)

    def _contract(self) -> dict[str, Any]:
        return load_project_contract(self.project_dir)

    def _restore_project(self) -> None:
        if self.project_dir.exists():
            shutil.rmtree(self.project_dir)
        shutil.copytree(self.base_project_dir, self.project_dir)
        project = _read_json(self.project_dir / "project.json")
        project["functionalmlds_trace_path"] = str(
            self.case_dir / "functionalmlds" / V05_SOURCE_FILENAME
        )
        project["functionalmlds_case_dir"] = str(self.case_dir)
        project["source_mlds_path"] = str(self.case_dir / "input" / "source_mlds.json")
        _write_json(self.project_dir / "project.json", project)

    def _synchronize_model_hash(self) -> str:
        model_path = self.project_dir / V2_PROJECT_INSTANCE_FILENAME
        model_sha256 = _sha256(model_path)
        project = _read_json(self.project_dir / "project.json")
        project["functionalmlds_model_sha256"] = model_sha256
        _write_json(self.project_dir / "project.json", project)
        for filename in ("trace_map.v2.json", "trace_map.json"):
            trace_path = self.project_dir / filename
            trace = _read_json(trace_path)
            trace["model_sha256"] = model_sha256
            _write_json(trace_path, trace)
        return model_sha256

    def test_materializer_emits_dual_files_hash_and_exact_backend_v2_contract(self) -> None:
        project = _read_json(self.project_dir / "project.json")
        v2_path = self.project_dir / V2_PROJECT_INSTANCE_FILENAME
        v05_path = self.project_dir / V05_PROJECT_INSTANCE_FILENAME
        active_trace = _read_json(self.project_dir / "trace_map.json")
        trace_v2 = _read_json(self.project_dir / "trace_map.v2.json")
        trace_v05 = _read_json(self.project_dir / "trace_map.v05.json")

        self.assertTrue(v2_path.is_file())
        self.assertTrue(v05_path.is_file())
        self.assertEqual(
            _read_json(self.case_dir / "functionalmlds" / V05_SOURCE_FILENAME),
            _read_json(v05_path),
        )
        self.assertEqual(
            _read_json(self.case_dir / "functionalmlds" / V2_PROJECT_INSTANCE_FILENAME),
            _read_json(v2_path),
        )
        self.assertEqual(_sha256(v2_path), project["functionalmlds_model_sha256"])
        self.assertEqual(V2_PROJECT_INSTANCE_FILENAME, project["functionalmlds_model_path"])
        self.assertEqual(V05_PROJECT_INSTANCE_FILENAME, project["functionalmlds_legacy_path"])
        self.assertEqual("trace_map.v2.json", project["functionalmlds_trace_map_path"])
        self.assertEqual("trace_map.v05.json", project["functionalmlds_legacy_trace_map_path"])
        self.assertEqual(trace_v2, active_trace)
        self.assertEqual(V2_TRACE_SCHEMA, trace_v2["schema"])
        self.assertEqual(V2_TRACE_VERSION, trace_v2["schema_version"])
        self.assertEqual("functionalmlds_trace_map", trace_v05["schema"])

        contract = self._contract()
        self.assertEqual("v2", contract["kind"])
        self.assertEqual(V2_MODEL_VERSION, contract["model_version"])
        self.assertEqual("executable", contract["profile"])
        self.assertEqual(_sha256(v2_path), contract["model_sha256"])
        self.assertEqual(_read_json(v2_path), load_v2_document(self.project_dir))

        context = contract["runtime_context"]
        self.assertEqual(RUNTIME_CONTEXT_SCHEMA, context["schema"])
        self.assertEqual(V2_MODEL_VERSION, context["model_version"])
        self.assertEqual(contract["model_sha256"], context["model_sha256"])
        self.assertEqual("executable", context["profile"])
        self.assertEqual(V2_TRACE_VERSION, context["trace_schema_version"])

        native_by_id = {item["id"]: item for item in contract["instance"]["objects"]}
        self.assertEqual(
            {"setup", "chat", "handoff"},
            {
                item["action_kind"]
                for item in context["runtime_actions"]
                if item["action_kind"] in {"setup", "chat", "handoff"}
            },
        )
        for action_kind, expected_ids in EXPECTED_APPLICATION_ACTIONS.items():
            with self.subTest(action_kind=action_kind):
                action = select_runtime_action(context, action_kind)
                self.assertEqual(
                    expected_ids,
                    {field: action[field] for field in ACTION_ID_FIELDS},
                )
                step = native_by_id[action["scenario_step_id"]]
                use = native_by_id[action["capability_use_id"]]
                provider = native_by_id[action["provider_entity_id"]]
                binding = native_by_id[action["runtime_binding_id"]]
                self.assertIn(action["capability_use_id"], step["capabilityUse"])
                self.assertIn(action["provider_entity_id"], step["performedBy"])
                self.assertEqual([action["capability_id"]], use["typeRef"])
                self.assertEqual([action["provider_entity_id"]], use["provider"])
                self.assertIn(action["capability_id"], provider["providedCapability"])
                self.assertEqual([action["capability_id"]], binding["capability"])
                self.assertIn(action["runtime_action_id"], binding["runtimeAction"])

        # Reading/copying the fixture and assembling its temp copy must never rewrite it.
        self.assertEqual(self.reference_v05_sha256, _sha256(self.reference_v05_path))

    def test_setup_response_exposes_the_complete_runtime_context_to_unity(self) -> None:
        project_manager = ProjectManager(
            root=self.backend_root / "projects",
            template_room_plan=self.project_dir / "room_plan.json",
            template_agents=self.project_dir / "agents.json",
        )
        store = SessionStore(
            max_history_turns=4,
            max_handoffs=1,
            kb=KnowledgeBase(self.project_dir / "kb"),
            kb_max_snippets=2,
            model="offline-contract-test",
            temperature=0.0,
            stt_model="offline-contract-test",
            stt_language="de",
            stt_max_audio_bytes=1024,
            openai=object(),  # Network access is not used by setup_from_request.
            project_manager=project_manager,
        )

        response = store.setup_from_request(
            {"project_id": CASE_ID, "session_id": "SESSION-V2-CONTRACT-TEST"}
        )
        contract = self._contract()
        context = response["functionalmlds"]

        self.assertEqual("SESSION-V2-CONTRACT-TEST", response["session_id"])
        self.assertEqual(V2_MODEL_VERSION, response["metamodel_version"])
        self.assertEqual(V2_TRACE_VERSION, response["trace_schema_version"])
        self.assertEqual(contract["model_sha256"], response["model_sha256"])
        self.assertEqual("executable", response["functionalmlds_profile"])
        self.assertEqual(
            f"/projects/{CASE_ID}/functionalmlds-v2",
            response["functionalmlds_model_endpoint"],
        )
        self.assertEqual(contract["runtime_context"], context)
        self.assertEqual(
            EXPECTED_APPLICATION_ACTIONS["setup"],
            {
                field: select_runtime_action(context, "setup")[field]
                for field in ACTION_ID_FIELDS
            },
        )
        self.assertEqual(
            context["runtime_validation_target_id"],
            response["runtime_validation_target_id"],
        )
        self.assertTrue(response["agents"])
        self.assertTrue(
            all(agent["functionalmlds_entity_id"] for agent in response["agents"])
        )

    def test_runtime_events_and_validation_records_conform_to_v2_schemas(self) -> None:
        project_manager = ProjectManager(
            root=self.backend_root / "projects",
            template_room_plan=self.project_dir / "room_plan.json",
            template_agents=self.project_dir / "agents.json",
        )
        contract = self._contract()
        expected_by_kind = {
            kind: select_runtime_action(contract["runtime_context"], kind)
            for kind in ("setup", "chat", "handoff")
        }

        returned_events = []
        for action_kind in ("setup", "chat", "handoff"):
            event = log_backend_event(
                project_manager=project_manager,
                project_id=CASE_ID,
                action_kind=action_kind,
                event_type=f"contract_test_{action_kind}",
                session_id="SESSION-V2-CONTRACT-TEST",
                agent_id=None,
                input_summary={"action": action_kind},
                output_summary={"accepted": True},
                duration_ms=1.0,
                status="success",
                metadata={"test": "temporary-e2e"},
            )
            self.assertIsNotNone(event)
            assert event is not None
            self.event_validator.validate(event)
            expected_action = expected_by_kind[action_kind]
            for field in ACTION_ID_FIELDS + (
                "target_ids",
                "assertion_ids",
                "validation_case_ids",
                "runtime_validation_target_ids",
            ):
                self.assertEqual(expected_action[field], event[field])
            returned_events.append(event)

        runtime_log_dir = self.case_dir / "runtime_logs"
        self.assertTrue(runtime_log_dir.is_relative_to(self.test_root))
        event_rows = _json_lines(runtime_log_dir / "events.jsonl")
        validation_rows = _json_lines(runtime_log_dir / "runtime_validation.v2.jsonl")
        self.assertEqual(returned_events, event_rows)
        self.assertEqual(3, len(validation_rows))

        for action_kind, event, validation in zip(
            ("setup", "chat", "handoff"),
            event_rows,
            validation_rows,
        ):
            with self.subTest(action_kind=action_kind):
                self.event_validator.validate(event)
                self.validation_validator.validate(validation)
                expected_action = expected_by_kind[action_kind]
                self.assertEqual(
                    expected_action["validation_case_ids"],
                    validation["validation_case_ids"],
                )
                self.assertEqual(
                    expected_action["runtime_validation_target_ids"],
                    validation["runtime_validation_target_ids"],
                )
                self.assertEqual(
                    expected_action["assertion_ids"],
                    [
                        result["assertion"][0]
                        for result in validation["runtimeActualOutcome"]["result"]
                    ],
                )
                self.assertTrue(
                    all(
                        result["evidenceRef"] == f"runtime-event://{event['event_id']}"
                        for result in validation["runtimeActualOutcome"]["result"]
                    )
                )

    def test_backend_fails_closed_on_hash_provider_and_trace_manipulation(self) -> None:
        with self.subTest(manipulation="declared model hash"):
            project = _read_json(self.project_dir / "project.json")
            project["functionalmlds_model_sha256"] = "0" * 64
            _write_json(self.project_dir / "project.json", project)
            with self.assertRaisesRegex(FunctionalMldsContractError, "hash mismatch"):
                self._contract()

    def test_backend_fails_closed_on_every_derived_trace_fact_and_downgrade(self) -> None:
        for field in (
            "target_ids",
            "assertion_ids",
            "validation_case_ids",
            "runtime_validation_target_ids",
        ):
            with self.subTest(manipulation=field):
                self._restore_project()
                trace_path = self.project_dir / "trace_map.v2.json"
                trace = _read_json(trace_path)
                trace["runtime_actions"][0][field] = [trace["main_scenario_id"]]
                _write_json(trace_path, trace)
                with self.assertRaisesRegex(
                    FunctionalMldsContractError,
                    rf"{field} does not exactly match",
                ):
                    self._contract()

        with self.subTest(manipulation="locator"):
            self._restore_project()
            trace_path = self.project_dir / "trace_map.v2.json"
            trace = _read_json(trace_path)
            trace["runtime_actions"][0]["locator"] = {
                "kind": "endpoint",
                "value": "POST /wrong-but-well-formed",
            }
            _write_json(trace_path, trace)
            with self.assertRaisesRegex(FunctionalMldsContractError, "locator does not exactly match"):
                self._contract()

        with self.subTest(manipulation="swapped action kinds"):
            self._restore_project()
            trace_path = self.project_dir / "trace_map.v2.json"
            trace = _read_json(trace_path)
            chat = next(item for item in trace["runtime_actions"] if item["action_kind"] == "chat")
            handoff = next(item for item in trace["runtime_actions"] if item["action_kind"] == "handoff")
            chat["action_kind"], handoff["action_kind"] = handoff["action_kind"], chat["action_kind"]
            _write_json(trace_path, trace)
            with self.assertRaisesRegex(FunctionalMldsContractError, "action_kind does not match"):
                self._contract()

        with self.subTest(manipulation="missing runtime chain"):
            self._restore_project()
            trace_path = self.project_dir / "trace_map.v2.json"
            trace = _read_json(trace_path)
            trace["runtime_actions"] = trace["runtime_actions"][1:]
            _write_json(trace_path, trace)
            with self.assertRaisesRegex(
                FunctionalMldsContractError,
                "not a complete, exact projection|requires exactly one",
            ):
                self._contract()

        for version_change in ("v0.5", None):
            with self.subTest(manipulation=f"V2 downgrade to {version_change!r}"):
                self._restore_project()
                project_path = self.project_dir / "project.json"
                project = _read_json(project_path)
                if version_change is None:
                    project.pop("functionalmlds_model_version", None)
                    project.pop("metamodelVersion", None)
                else:
                    project["functionalmlds_model_version"] = version_change
                    project["metamodelVersion"] = version_change
                _write_json(project_path, project)
                with self.assertRaisesRegex(
                    FunctionalMldsContractError,
                    "Mixed or downgraded FunctionalMLDS contract",
                ):
                    self._contract()

        # Restore the pristine per-test project before testing a semantic model attack.
        shutil.rmtree(self.project_dir)
        shutil.copytree(self.base_project_dir, self.project_dir)
        project = _read_json(self.project_dir / "project.json")
        project["functionalmlds_trace_path"] = str(
            self.case_dir / "functionalmlds" / V05_SOURCE_FILENAME
        )
        _write_json(self.project_dir / "project.json", project)

        with self.subTest(manipulation="CapabilityUse provider"):
            model_path = self.project_dir / V2_PROJECT_INSTANCE_FILENAME
            instance = _read_json(model_path)
            by_id = {item["id"]: item for item in instance["objects"]}
            setup_ids = EXPECTED_APPLICATION_ACTIONS["setup"]
            capability_id = setup_ids["capability_id"]
            invalid_provider = next(
                item
                for item in instance["objects"]
                if item.get("type") in {"Entity", "Agent"}
                and item["id"] != setup_ids["provider_entity_id"]
                and capability_id not in item.get("providedCapability", [])
            )
            capability_use = by_id[setup_ids["capability_use_id"]]
            capability_use["provider"] = [invalid_provider["id"]]
            step = by_id[setup_ids["scenario_step_id"]]
            step["performedBy"] = [
                invalid_provider["id"]
                if ref == setup_ids["provider_entity_id"]
                else ref
                for ref in step["performedBy"]
            ]
            _write_json(model_path, instance)
            self._synchronize_model_hash()
            with self.assertRaisesRegex(
                FunctionalMldsContractError,
                "provider does not provide its Capability",
            ):
                self._contract()

        # Restore once more so the trace attack is not masked by the invalid model.
        shutil.rmtree(self.project_dir)
        shutil.copytree(self.base_project_dir, self.project_dir)
        project = _read_json(self.project_dir / "project.json")
        project["functionalmlds_trace_path"] = str(
            self.case_dir / "functionalmlds" / V05_SOURCE_FILENAME
        )
        _write_json(self.project_dir / "project.json", project)

        with self.subTest(manipulation="runtime trace action chain"):
            for filename in ("trace_map.v2.json", "trace_map.json"):
                trace_path = self.project_dir / filename
                trace = _read_json(trace_path)
                setup = next(
                    item for item in trace["runtime_actions"] if item["action_kind"] == "setup"
                )
                setup["runtime_action_id"] = EXPECTED_APPLICATION_ACTIONS["chat"][
                    "runtime_action_id"
                ]
                _write_json(trace_path, trace)
            with self.assertRaisesRegex(
                FunctionalMldsContractError,
                "RuntimeAction is not owned by the binding",
            ):
                self._contract()

    def test_v05_legacy_contract_loads_in_isolation_without_implicit_migration(self) -> None:
        legacy_dir = self.test_root / "legacy_backend" / "projects" / CASE_ID
        legacy_dir.mkdir(parents=True)
        shutil.copy2(
            self.project_dir / V05_PROJECT_INSTANCE_FILENAME,
            legacy_dir / V05_PROJECT_INSTANCE_FILENAME,
        )
        legacy_trace_path = legacy_dir / "trace_map.json"
        shutil.copy2(self.project_dir / "trace_map.v05.json", legacy_trace_path)
        legacy_trace = _read_json(legacy_trace_path)
        for field_name in PLACEMENT_DEPLOYMENT_FIELDS:
            legacy_trace.pop(field_name, None)
        _write_json(legacy_trace_path, legacy_trace)
        _write_json(
            legacy_dir / "project.json",
            {
                "id": CASE_ID,
                "display_name": "Classroom Dinosaur legacy contract test",
                "description": "Native v0.5 runtime contract; no migration requested.",
                "created_ms": 1,
                "updated_ms": 1,
                "generation_mode": "functionalmlds",
                "metamodelVersion": V05_MODEL_VERSION,
            },
        )
        v2_path = legacy_dir / V2_PROJECT_INSTANCE_FILENAME
        self.assertFalse(v2_path.exists())

        contract = load_project_contract(legacy_dir)

        self.assertEqual("v05", contract["kind"])
        self.assertEqual(V05_MODEL_VERSION, contract["model_version"])
        self.assertEqual("legacy", contract["profile"])
        self.assertNotIn("instance", contract)
        self.assertEqual(RUNTIME_CONTEXT_SCHEMA, contract["runtime_context"]["schema"])
        self.assertEqual("legacy", contract["runtime_context"]["profile"])
        self.assertEqual(
            {"setup", "chat", "handoff"},
            {
                item["action_kind"]
                for item in contract["runtime_context"]["runtime_actions"]
            },
        )
        for action_kind in ("setup", "chat", "handoff"):
            self.assertEqual(
                EXPECTED_APPLICATION_ACTIONS[action_kind]["runtime_action_id"],
                select_runtime_action(contract["runtime_context"], action_kind)[
                    "runtime_action_id"
                ],
            )
        self.assertFalse(v2_path.exists(), "Legacy loading must not perform a hidden V2 migration.")


if __name__ == "__main__":
    unittest.main()
