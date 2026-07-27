"""Regression tests for the lossless v0.5 ↔ V2 compatibility projection."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import dynamic_functional_mlds_v2_compat as compat  # noqa: E402


def recursive_key_order(value):
    if isinstance(value, dict):
        return [(key, recursive_key_order(child)) for key, child in value.items()]
    if isinstance(value, list):
        return [recursive_key_order(child) for child in value]
    return type(value).__name__


class V05CompatibilityProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = compat.discover_v05_instances(ROOT)
        cls.documents = [compat.load_json(path) for path in cls.paths]

    def test_discovers_exactly_the_eight_live_instances(self):
        self.assertEqual(8, len(self.paths))
        self.assertSetEqual(
            compat.EXPECTED_CASE_IDS,
            {document["caseId"] for document in self.documents},
        )
        self.assertTrue(all("archive" not in path.parts for path in self.paths))

    def test_all_eight_round_trip_with_structure_presence_and_order_unchanged(self):
        for document in self.documents:
            with self.subTest(caseId=document["caseId"]):
                envelope = compat.import_v05(document)
                exported = compat.export_v05(envelope)
                self.assertEqual(document, exported)
                self.assertEqual(
                    recursive_key_order(document),
                    recursive_key_order(exported),
                )
                self.assertEqual(
                    compat.structural_sha256(document),
                    compat.structural_sha256(exported),
                )
                # Returned exports are defensive copies.
                exported["caseId"] = "mutated-copy"
                self.assertEqual(document["caseId"], envelope["v05Projection"]["caseId"])

    def test_main_use_case_and_main_scenario_remain_first(self):
        for document in self.documents:
            envelope = compat.import_v05(document)
            exported = compat.export_v05(envelope)
            self.assertEqual(
                document["requirementsModel"]["useCases"][0]["id"],
                exported["requirementsModel"]["useCases"][0]["id"],
            )
            self.assertEqual(
                "main",
                exported["requirementsModel"]["useCases"][0]["scenarios"][0]["kind"],
            )

    def test_projection_ledger_preserves_runtime_locator_slots(self):
        for document in self.documents:
            envelope = compat.import_v05(document)
            slots_by_id = {
                item["runtimeActionId"]: item
                for item in envelope["v05ProjectionLedger"]["runtimeActionLocatorSlots"]
            }
            for binding in document["runtimeBindings"]:
                for action in binding["runtimeActions"]:
                    ledger_entry = slots_by_id[action["id"]]
                    active = []
                    for slot in ("endpoint", "tool", "topic"):
                        self.assertEqual(slot in action, ledger_entry["slots"][slot]["present"])
                        self.assertEqual(action.get(slot), ledger_entry["slots"][slot]["value"])
                        if slot in action and action[slot] is not None:
                            active.append(slot)
                    self.assertEqual([ledger_entry["activeSlot"]], active)

    def test_projection_ledger_preserves_legacy_validation_levels_without_derivation(self):
        for document in self.documents:
            envelope = compat.import_v05(document)
            observed = [item["level"] for item in document["validationCases"]]
            preserved = [
                value
                for pointer, value in envelope["v05ProjectionLedger"]["enumLexemes"].items()
                if pointer.endswith("/level")
            ]
            self.assertEqual(observed, preserved)
            semantic = envelope["dynamicFunctionalModel"]["verificationValidation"]["vvCases"]
            self.assertTrue(all("legacyLevel" not in item for item in semantic))

    def test_projection_ledger_preserves_all_agent_identity_namespaces(self):
        for document in self.documents:
            envelope = compat.import_v05(document)
            expected = [
                (agent["id"], agent["source_agent_id"], agent["entity_id"])
                for agent in document["agents"]
            ]
            actual = [
                (item["agentId"], item["sourceAgentId"], item["entityId"])
                for item in envelope["v05ProjectionLedger"]["agentAliases"]
            ]
            self.assertEqual(expected, actual)
            self.assertTrue(all(agent_id.startswith("AG-") for agent_id, _, _ in actual))
            self.assertTrue(all(entity_id.startswith("ENT-AGENT-") for _, _, entity_id in actual))

    def test_normalized_field_mapping_covers_173_paths_and_101_leaves(self):
        mapping = compat.build_semantic_mapping(self.documents)
        self.assertEqual(173, mapping["entryCount"])
        self.assertEqual(72, mapping["structurePathCount"])
        self.assertEqual(101, mapping["leafPathCount"])
        self.assertTrue(mapping["coverage"]["covered"])
        self.assertEqual(173, mapping["coverage"]["coveredPathCount"])
        self.assertEqual(173, mapping["coverage"]["resolvedTargetCount"])
        self.assertEqual([], mapping["coverage"]["unresolvedTargets"])
        self.assertEqual([], mapping["coverage"]["missingStructurePaths"])
        self.assertEqual([], mapping["coverage"]["missingLeafPaths"])
        self.assertTrue(all(entry["v2Target"] != "UNMAPPED" for entry in mapping["entries"]))
        self.assertTrue(all(entry["rule"] for entry in mapping["entries"]))

    def test_cli_audit_and_evidence_pass(self):
        audit = compat.run_compatibility_audit(ROOT)
        self.assertTrue(audit["passed"])
        self.assertEqual(8, audit["fixtureCount"])
        with tempfile.TemporaryDirectory() as temporary_directory:
            written = compat.write_evidence(audit, Path(temporary_directory))
            self.assertEqual(5, len(written))
            self.assertTrue(all(path.is_file() for path in written))
            report = json.loads((Path(temporary_directory) / "v05_roundtrip_report.json").read_text(encoding="utf-8"))
            self.assertTrue(report["passed"])

    def test_v2_only_extensions_fail_instead_of_being_dropped(self):
        envelope = compat.import_v05(self.documents[0])
        envelope["v2Extensions"] = {"functionBehavior": {"path": "Assets/Behavior"}}
        with self.assertRaisesRegex(compat.RepresentabilityError, "v2Extensions"):
            compat.export_v05(envelope)

        envelope = compat.import_v05(self.documents[0])
        envelope["newV2Association"] = []
        with self.assertRaisesRegex(compat.RepresentabilityError, "V2-only envelope"):
            compat.export_v05(envelope)

    def test_semantic_or_exact_projection_manipulation_is_detected(self):
        envelope = compat.import_v05(self.documents[0])
        envelope["dynamicFunctionalModel"]["shortName"] = "changed"
        with self.assertRaisesRegex(compat.RepresentabilityError, "dynamicFunctionalModel"):
            compat.export_v05(envelope)

        envelope = compat.import_v05(self.documents[0])
        envelope["v05Projection"]["requirementsModel"]["requirements"][0]["text"] += " changed"
        with self.assertRaisesRegex(compat.RepresentabilityError, "dynamicFunctionalModel"):
            compat.export_v05(envelope)

    def test_ledger_manipulation_of_legacy_level_or_agent_alias_is_detected(self):
        envelope = compat.import_v05(self.documents[0])
        level_pointer = next(
            pointer
            for pointer in envelope["v05ProjectionLedger"]["enumLexemes"]
            if pointer.endswith("/level")
        )
        envelope["v05ProjectionLedger"]["enumLexemes"][level_pointer] = "derived"
        with self.assertRaisesRegex(compat.RepresentabilityError, "Ledger"):
            compat.export_v05(envelope)

        envelope = compat.import_v05(self.documents[0])
        envelope["v05ProjectionLedger"]["agentAliases"][0]["entityId"] = "ENT-AGENT-WRONG"
        with self.assertRaisesRegex(compat.RepresentabilityError, "Ledger"):
            compat.export_v05(envelope)

    def test_invalid_runtime_locator_multiplicity_is_rejected(self):
        document = copy.deepcopy(self.documents[0])
        action = document["runtimeBindings"][0]["runtimeActions"][0]
        action["endpoint"] = "POST /also-active"
        action["tool"] = "module.call"
        action["topic"] = None
        with self.assertRaisesRegex(compat.RepresentabilityError, "exactly one active locator"):
            compat.import_v05(document)

        document = copy.deepcopy(self.documents[0])
        action = document["runtimeBindings"][0]["runtimeActions"][0]
        action["endpoint"] = None
        action["tool"] = None
        action["topic"] = None
        with self.assertRaisesRegex(compat.RepresentabilityError, "exactly one active locator"):
            compat.import_v05(document)

    def test_missing_legacy_level_is_rejected_not_inferred(self):
        document = copy.deepcopy(self.documents[0])
        del document["validationCases"][0]["level"]
        with self.assertRaisesRegex(compat.RepresentabilityError, "compatibility discriminator"):
            compat.import_v05(document)

    def test_agent_alias_must_reference_existing_agent_entity(self):
        document = copy.deepcopy(self.documents[0])
        document["agents"][0]["entity_id"] = "ENT-AGENT-DOES-NOT-EXIST"
        with self.assertRaisesRegex(compat.RepresentabilityError, "references missing entity_id"):
            compat.import_v05(document)

    def test_non_main_first_scenario_is_rejected(self):
        document = copy.deepcopy(self.documents[0])
        document["requirementsModel"]["useCases"][0]["scenarios"][0]["kind"] = "alternative"
        with self.assertRaisesRegex(compat.RepresentabilityError, "must remain the main scenario"):
            compat.import_v05(document)


if __name__ == "__main__":
    unittest.main()
