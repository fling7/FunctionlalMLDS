"""Regression coverage for the native executable Dynamic Functional MLDS V2 assembly."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
for import_root in (ROOT, TOOLS):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from dynamic_functional_mlds_v2_compat import discover_v05_instances, load_json  # noqa: E402
from dynamic_functional_mlds_v2_model import MODEL  # noqa: E402
from validate_dynamic_functional_mlds_v2 import validate_instance  # noqa: E402
from case_study_pipeline.functionalmlds_v2_assembler import (  # noqa: E402
    V2AssemblyError,
    V2_FILENAME,
    V2_SCHEMA_PATH,
    V2_VALIDATION_FILENAME,
    assemble_v2_instance,
    run_v2_assembly,
    validate_functionalmlds_v2_instance,
)


ASSERTION_TYPES = {
    "StateAssertion",
    "EventAssertion",
    "OutputAssertion",
    "GroundingAssertion",
    "RelationAssertion",
}


def objects_by_type(instance: dict, type_name: str) -> list[dict]:
    return [item for item in instance["objects"] if item.get("type") == type_name]


def object_index(instance: dict) -> dict[str, dict]:
    return {item["id"]: item for item in instance["objects"]}


def canonical_codes(instance: dict) -> set[str]:
    report = validate_instance(MODEL, instance, subject="mutated native V2 instance")
    return {issue.code for issue in report.issues}


class FunctionalMldsV2RuntimeAssemblerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.paths = discover_v05_instances(ROOT)
        cls.v05_documents = [load_json(path) for path in cls.paths]
        cls.instances = [assemble_v2_instance(document) for document in cls.v05_documents]
        cls.schema = json.loads(V2_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.schema_validator = Draft202012Validator(cls.schema)

    def test_all_eight_real_fixtures_are_native_schema_and_canonical_valid(self) -> None:
        self.assertEqual(8, len(self.paths))
        for path, instance in zip(self.paths, self.instances):
            with self.subTest(case_dir=path.parent.parent.name):
                self.schema_validator.validate(instance)
                report = validate_functionalmlds_v2_instance(instance)
                self.assertEqual("valid", report["status"])
                self.assertTrue(report["ok"])
                self.assertEqual("dynamic_functional_mlds_v2_instance", instance["schema"])
                self.assertEqual("2.0.0-model", instance["metamodelVersion"])
                self.assertEqual("executable", instance["profile"])
                self.assertEqual("executable", instance["fixture_profile"])
                self.assertNotIn("dynamicFunctionalModel", instance)
                self.assertNotIn("v05Projection", instance)
                self.assertNotIn("v05ProjectionLedger", instance)

                ids = [item["id"] for item in instance["objects"]]
                self.assertEqual(len(ids), len(set(ids)))
                roots = objects_by_type(instance, "DynamicFunctionalModel")
                self.assertEqual(1, len(roots))
                self.assertEqual(instance["id"], roots[0]["id"])

    def test_complete_executable_capability_and_assertion_semantics(self) -> None:
        for document, instance in zip(self.v05_documents, self.instances):
            with self.subTest(caseId=instance["caseId"]):
                by_id = object_index(instance)
                preferred_provider_by_use = {
                    item["id"]: item.get("preferred_provider_entity_id")
                    for item in document.get("capabilityUses") or []
                    if item.get("preferred_provider_entity_id")
                }
                agent_provider_ids = {}
                for agent in objects_by_type(instance, "Agent"):
                    for capability_id in agent.get("providedCapability") or []:
                        agent_provider_ids.setdefault(capability_id, []).append(agent["id"])
                observed_assertion_types = {
                    item["type"] for item in instance["objects"] if item["type"] in ASSERTION_TYPES
                }
                self.assertSetEqual(ASSERTION_TYPES, observed_assertion_types)

                step_for_use = {}
                for step in objects_by_type(instance, "ScenarioStep"):
                    for use_id in step["capabilityUse"]:
                        step_for_use[use_id] = step
                for capability_use in objects_by_type(instance, "CapabilityUse"):
                    self.assertEqual(1, len(capability_use["typeRef"]))
                    self.assertEqual(1, len(capability_use["provider"]))
                    provider_id = capability_use["provider"][0]
                    provider = by_id[provider_id]
                    self.assertIn(provider["type"], {"Entity", "Agent"})
                    self.assertIn(capability_use["typeRef"][0], provider["providedCapability"])
                    self.assertIn(provider_id, step_for_use[capability_use["id"]]["performedBy"])
                    domain_providers = agent_provider_ids.get(capability_use["typeRef"][0], [])
                    if domain_providers:
                        self.assertEqual("Agent", provider["type"])
                        self.assertEqual(
                            preferred_provider_by_use.get(
                                capability_use["id"],
                                domain_providers[0],
                            ),
                            provider_id,
                        )
                    else:
                        self.assertEqual("runtimeOrchestrator", provider.get("entityRole"))

                self.assertTrue(objects_by_type(instance, "RuntimeValidationTarget"))
                self.assertTrue(objects_by_type(instance, "RuntimeValidationLog"))
                self.assertTrue(objects_by_type(instance, "RuntimeActualOutcome"))
                self.assertTrue(objects_by_type(instance, "AssertionResult"))

    def test_application_action_mapping_is_explicit_and_exact(self) -> None:
        for instance in self.instances:
            with self.subTest(caseId=instance["caseId"]):
                by_id = object_index(instance)
                counts = {"setup": 0, "chat": 0, "handoff": 0, "runtime": 0}
                for action in objects_by_type(instance, "RuntimeAction"):
                    self.assertEqual(1, len(action["locator"]))
                    self.assertEqual(1, len(action["inputSchema"]))
                    schema_reference = by_id[action["inputSchema"][0]]
                    mapping = json.loads(schema_reference["text"])
                    self.assertEqual(
                        "https://json-schema.org/draft/2020-12/schema",
                        mapping["$schema"],
                    )
                    self.assertEqual("2.0", mapping["wireContractVersion"])
                    self.assertEqual(
                        action["id"],
                        mapping["modelBinding"]["runtimeActionId"],
                    )
                    counts[mapping["applicationActionKind"]] += 1
                    if mapping["applicationActionKind"] in {"chat", "handoff"}:
                        self.assertIn("interaction_mode", mapping["required"])
                        self.assertEqual(
                            ["deictic", "non_deictic"],
                            mapping["properties"]["interaction_mode"]["enum"],
                        )
                        deictic_condition = next(
                            condition
                            for condition in mapping["allOf"]
                            if condition["if"]["properties"]["interaction_mode"].get(
                                "const"
                            )
                            == "deictic"
                        )
                        self.assertIn(
                            "spatial_context",
                            deictic_condition["then"]["required"],
                        )
                        self.assertEqual(1, len(action["outputSchema"]))
                        response_mapping = json.loads(
                            by_id[action["outputSchema"][0]]["text"]
                        )
                        self.assertEqual(
                            mapping["modelBinding"],
                            response_mapping["modelBinding"],
                        )
                        self.assertIn(
                            "grounding_evidence",
                            response_mapping["properties"],
                        )
                self.assertEqual(1, counts["setup"])
                self.assertEqual(1, counts["chat"])
                self.assertEqual(1, counts["handoff"])
                self.assertGreater(counts["runtime"], 0)

    def test_assembly_is_deterministic(self) -> None:
        repeated = assemble_v2_instance(copy.deepcopy(self.v05_documents[0]))
        self.assertEqual(self.instances[0], repeated)

    def test_writer_preserves_v05_and_emits_stable_files_and_report(self) -> None:
        source_path = self.paths[0]
        original = source_path.read_bytes()
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = run_v2_assembly(source_path, Path(temporary_directory))
            instance_path = Path(result["functionalmlds_v2_path"])
            report_path = Path(result["validation_path"])
            self.assertEqual(V2_FILENAME, instance_path.name)
            self.assertEqual(V2_VALIDATION_FILENAME, report_path.name)
            self.assertEqual("success", result["status"])
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual("valid", report["status"])
            self.assertIn("metrics", report)
            self.schema_validator.validate(json.loads(instance_path.read_text(encoding="utf-8")))
        self.assertEqual(original, source_path.read_bytes())

    def test_schema_rejects_v05_unknown_fields_and_missing_profile(self) -> None:
        with self.assertRaises(Exception):
            self.schema_validator.validate(self.v05_documents[0])

        extra_root = copy.deepcopy(self.instances[0])
        extra_root["projectionEnvelope"] = {}
        with self.assertRaises(Exception):
            self.schema_validator.validate(extra_root)

        extra_object_field = copy.deepcopy(self.instances[0])
        extra_object_field["objects"][0]["legacyRuntime"] = True
        with self.assertRaises(Exception):
            self.schema_validator.validate(extra_object_field)

        missing_profile = copy.deepcopy(self.instances[0])
        del missing_profile["profile"]
        with self.assertRaises(Exception):
            self.schema_validator.validate(missing_profile)

    def test_duplicate_application_mapping_fails_closed_at_import_boundary(self) -> None:
        v05 = copy.deepcopy(self.v05_documents[0])
        first_action = v05["runtimeBindings"][0]["runtimeActions"][0]
        first_action["endpoint"] = "POST /setup"
        first_action["tool"] = None
        first_action["topic"] = None
        with self.assertRaisesRegex(V2AssemblyError, "exactly one setup, chat and handoff"):
            assemble_v2_instance(v05)

    def test_negative_missing_capability_provider(self) -> None:
        mutated = copy.deepcopy(self.instances[0])
        objects_by_type(mutated, "CapabilityUse")[0]["provider"] = []
        self.assertIn("ICAP002", canonical_codes(mutated))

    def test_pipeline_validation_rejects_orchestrator_for_agent_owned_capability(self) -> None:
        mutated = copy.deepcopy(self.instances[0])
        by_id = object_index(mutated)
        domain_use = next(
            item
            for item in objects_by_type(mutated, "CapabilityUse")
            if by_id[item["provider"][0]].get("type") == "Agent"
        )
        capability_id = domain_use["typeRef"][0]
        orchestrator = next(
            item
            for item in objects_by_type(mutated, "Entity")
            if item.get("entityRole") == "runtimeOrchestrator"
        )
        orchestrator.setdefault("providedCapability", []).append(capability_id)
        domain_use["provider"] = [orchestrator["id"]]
        owner = next(
            step
            for step in objects_by_type(mutated, "ScenarioStep")
            if domain_use["id"] in step["capabilityUse"]
        )
        owner["performedBy"] = [orchestrator["id"]]

        report = validate_functionalmlds_v2_instance(mutated)

        self.assertEqual("invalid", report["status"])
        self.assertIn(
            "IUI-DOMAIN-PROVIDER",
            {issue.get("code") for issue in report["errors"]},
        )

    def test_negative_assertion_without_subject(self) -> None:
        mutated = copy.deepcopy(self.instances[0])
        assertion = next(item for item in mutated["objects"] if item["type"] in ASSERTION_TYPES)
        assertion["subject"] = []
        self.assertIn("IAST002", canonical_codes(mutated))

    def test_negative_sequence_probability(self) -> None:
        mutated = copy.deepcopy(self.instances[0])
        relation = next(
            item for item in objects_by_type(mutated, "StepRelation") if item["kind"] == "sequence"
        )
        relation["probability"] = 0.5
        self.assertIn("ISCN010", canonical_codes(mutated))
        with self.assertRaises(Exception):
            self.schema_validator.validate(mutated)

    def test_negative_runtime_validation_target_without_element(self) -> None:
        mutated = copy.deepcopy(self.instances[0])
        objects_by_type(mutated, "RuntimeValidationTarget")[0]["element"] = []
        self.assertIn("IVV013", canonical_codes(mutated))

    def test_negative_assertion_result_without_assertion(self) -> None:
        mutated = copy.deepcopy(self.instances[0])
        objects_by_type(mutated, "AssertionResult")[0]["assertion"] = []
        self.assertIn("IAST011", canonical_codes(mutated))

    def test_negative_cross_scenario_step_relation_target(self) -> None:
        mutated = copy.deepcopy(self.instances[0])
        orchestrator_id = next(
            item["id"]
            for item in objects_by_type(mutated, "Entity")
            if item.get("entityRole") == "runtimeOrchestrator"
        )
        relation = objects_by_type(mutated, "StepRelation")[0]
        relation["targetStep"] = [orchestrator_id]
        relation["target"] = [orchestrator_id]
        self.assertIn("ISCN005", canonical_codes(mutated))


if __name__ == "__main__":
    unittest.main()
