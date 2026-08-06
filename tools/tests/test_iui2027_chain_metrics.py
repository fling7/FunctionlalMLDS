from __future__ import annotations

import copy
import unittest

from research.iui2027.evaluation.run_benchmark import (
    _aggregate_asset_interaction_chain_metrics,
    _asset_interaction_chain_metrics,
    _timing_summary,
)


def _complete_instance() -> dict:
    return {
        "objects": [
            {
                "id": "ASSET-1",
                "type": "Entity",
                "entityRole": "sceneObject",
                "sourceId": "asset_1",
            },
            {
                "id": "AGENT-1",
                "type": "Agent",
                "sourceId": "agent_1",
            },
            {
                "id": "CAP-1",
                "type": "Capability",
            },
            {
                "id": "CU-1",
                "type": "CapabilityUse",
                "typeRef": ["CAP-1"],
                "provider": ["AGENT-1"],
                "target": ["ASSET-1"],
            },
            {
                "id": "ASSERT-1",
                "type": "StateAssertion",
            },
            {
                "id": "STEP-1",
                "type": "ScenarioStep",
                "performedBy": ["AGENT-1"],
                "capabilityUse": ["CU-1"],
                "resultingAssertion": ["ASSERT-1"],
            },
            {
                "id": "SCENARIO-1",
                "type": "Scenario",
                "step": ["STEP-1"],
            },
            {
                "id": "USE-CASE-1",
                "type": "UseCase",
            },
            {
                "id": "SPEC-1",
                "type": "UseCaseScenarioSpecification",
                "useCase": ["USE-CASE-1"],
                "scenario": ["SCENARIO-1"],
            },
            {
                "id": "ACTION-1",
                "type": "RuntimeAction",
            },
            {
                "id": "BINDING-1",
                "type": "RuntimeBinding",
                "capability": ["CAP-1"],
                "runtimeAction": ["ACTION-1"],
            },
            {
                "id": "VALIDATION-TARGET-1",
                "type": "RuntimeValidationTarget",
                "runtimeBinding": ["BINDING-1"],
                "element": ["BINDING-1"],
            },
            {
                "id": "OUTCOME-1",
                "type": "StateAssertionOutcome",
                "assertion": ["ASSERT-1"],
            },
            {
                "id": "PROCEDURE-1",
                "type": "RuntimeValidationProcedure",
                "vvIntendedOutcome": ["OUTCOME-1"],
            },
            {
                "id": "VALIDATION-CASE-1",
                "type": "ValidationCase",
                "vvSubject": ["BINDING-1"],
                "vvTarget": ["VALIDATION-TARGET-1"],
                "vvProcedure": ["PROCEDURE-1"],
            },
            {
                "id": "VALIDATION-BINDING-1",
                "type": "ValidationCaseUseCaseBinding",
                "validationCase": ["VALIDATION-CASE-1"],
                "useCase": ["USE-CASE-1"],
            },
        ]
    }


def _object(instance: dict, object_id: str) -> dict:
    return next(
        item
        for item in instance["objects"]
        if item.get("id") == object_id
    )


class Iui2027AssetInteractionChainMetricTests(unittest.TestCase):
    def test_complete_chain_has_explicit_asset_and_chain_denominators(
        self,
    ) -> None:
        metrics = _asset_interaction_chain_metrics(_complete_instance())

        self.assertEqual(1, metrics["asset_denominator"])
        self.assertEqual(1, metrics["asset_with_chain_candidate_count"])
        self.assertEqual(1.0, metrics["asset_chain_coverage_rate"])
        self.assertEqual(1, metrics["complete_asset_count"])
        self.assertEqual(1.0, metrics["complete_asset_rate"])
        self.assertEqual(1, metrics["chain_candidate_denominator"])
        self.assertEqual(1, metrics["complete_chain_count"])
        self.assertEqual(1.0, metrics["chain_completeness_rate"])
        self.assertEqual([], metrics["errors"])

        chain = metrics["asset_results"][0]["chains"][0]
        self.assertEqual(["CAP-1"], chain["capability_ids"])
        self.assertEqual(["AGENT-1"], chain["provider_ids"])
        self.assertEqual(["ASSET-1"], chain["target_ids"])
        self.assertEqual(["BINDING-1"], chain["runtime_binding_ids"])
        self.assertEqual(["ACTION-1"], chain["runtime_action_ids"])
        self.assertEqual(["ASSERT-1"], chain["resulting_assertion_ids"])
        self.assertEqual(
            ["VALIDATION-CASE-1"],
            chain["validation_case_ids"],
        )

    def test_asset_without_chain_stays_in_asset_denominator(self) -> None:
        instance = _complete_instance()
        _object(instance, "STEP-1")["capabilityUse"] = []

        metrics = _asset_interaction_chain_metrics(instance)

        self.assertEqual(1, metrics["asset_denominator"])
        self.assertEqual(0, metrics["asset_with_chain_candidate_count"])
        self.assertEqual(0.0, metrics["asset_chain_coverage_rate"])
        self.assertEqual(0, metrics["chain_candidate_denominator"])
        self.assertIsNone(metrics["chain_completeness_rate"])
        self.assertEqual(
            {"ASSET_CHAIN_MISSING": 1},
            metrics["error_code_counts"],
        )

    def test_missing_runtime_action_is_localized_to_chain(self) -> None:
        instance = _complete_instance()
        instance["objects"] = [
            item
            for item in instance["objects"]
            if item.get("id") != "ACTION-1"
        ]

        metrics = _asset_interaction_chain_metrics(instance)

        self.assertEqual(1, metrics["chain_candidate_denominator"])
        self.assertEqual(0, metrics["complete_chain_count"])
        self.assertEqual(
            {"RUNTIME_ACTION_REFERENCE_INVALID": 1},
            metrics["error_code_counts"],
        )
        error = metrics["errors"][0]
        self.assertEqual("ASSET-1", error["asset_id"])
        self.assertEqual("STEP-1", error["step_id"])
        self.assertEqual("CU-1", error["capability_use_id"])
        self.assertIn(
            "BINDING-1",
            error["details"]["binding_actions"],
        )

    def test_provider_must_equal_step_performer(self) -> None:
        instance = _complete_instance()
        instance["objects"].append(
            {
                "id": "AGENT-2",
                "type": "Agent",
                "sourceId": "agent_2",
            }
        )
        _object(instance, "STEP-1")["performedBy"] = ["AGENT-2"]

        metrics = _asset_interaction_chain_metrics(instance)

        self.assertEqual(0, metrics["complete_chain_count"])
        self.assertEqual(
            {"PROVIDER_PERFORMER_MISMATCH": 1},
            metrics["error_code_counts"],
        )
        self.assertEqual(
            ["AGENT-1"],
            metrics["errors"][0]["details"]["provider_refs"],
        )
        self.assertEqual(
            ["AGENT-2"],
            metrics["errors"][0]["details"]["performed_by_refs"],
        )

    def test_validation_case_must_cover_resulting_assertion(self) -> None:
        instance = _complete_instance()
        instance["objects"].append(
            {
                "id": "ASSERT-OTHER",
                "type": "StateAssertion",
            }
        )
        _object(instance, "OUTCOME-1")["assertion"] = ["ASSERT-OTHER"]

        metrics = _asset_interaction_chain_metrics(instance)

        self.assertEqual(0, metrics["complete_chain_count"])
        self.assertEqual(
            {"VALIDATION_CASE_ASSERTION_NOT_COVERED": 1},
            metrics["error_code_counts"],
        )
        self.assertEqual(
            ["ASSERT-1"],
            metrics["errors"][0]["details"][
                "resulting_assertion_ids"
            ],
        )

    def test_aggregate_preserves_case_qualified_error_details(self) -> None:
        passing = _asset_interaction_chain_metrics(_complete_instance())
        failing_instance = copy.deepcopy(_complete_instance())
        _object(failing_instance, "STEP-1")["capabilityUse"] = []
        failing = _asset_interaction_chain_metrics(failing_instance)

        aggregate = _aggregate_asset_interaction_chain_metrics(
            [
                {"case_id": "passing", "metrics": passing},
                {"case_id": "failing", "metrics": failing},
            ]
        )

        self.assertEqual(2, aggregate["asset_denominator"])
        self.assertEqual(1, aggregate["complete_asset_count"])
        self.assertEqual(0.5, aggregate["complete_asset_rate"])
        self.assertEqual(1, aggregate["chain_candidate_denominator"])
        self.assertEqual(1, aggregate["complete_chain_count"])
        self.assertEqual("failing", aggregate["errors"][0]["case_id"])


class Iui2027TimingDispersionTests(unittest.TestCase):
    def test_timing_summary_reports_quartiles_iqr_and_range(self) -> None:
        summary = _timing_summary([50, 10, 40, 20, 30])

        self.assertEqual(10, summary["min_ns"])
        self.assertEqual(30, summary["median_ns"])
        self.assertEqual(20.0, summary["q1_ns"])
        self.assertEqual(40.0, summary["q3_ns"])
        self.assertEqual(20.0, summary["iqr_ns"])
        self.assertEqual(50, summary["max_ns"])
        self.assertEqual(
            "inclusive linear interpolation",
            summary["quartile_method"],
        )

    def test_timing_summary_rejects_empty_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one"):
            _timing_summary([])


if __name__ == "__main__":
    unittest.main()
