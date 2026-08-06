from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from research.iui2027.evaluation.run_benchmark import (
    CASE_IDS,
    REPOSITORY_ROOT,
    build_benchmark,
    build_environment,
    write_artifacts,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Iui2027SystemBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.case_dirs = {
            case_id: REPOSITORY_ROOT
            / "output"
            / "case_studies"
            / case_id
            for case_id in CASE_IDS
        }
        cls.v2_paths = {
            case_id: case_dir
            / "functionalmlds"
            / "functionalmlds.v2.instance.json"
            for case_id, case_dir in cls.case_dirs.items()
        }
        cls.input_paths = [
            path
            for case_dir in cls.case_dirs.values()
            for path in (
                case_dir
                / "functionalmlds"
                / "functionalmlds.v2.instance.json",
                case_dir
                / "functionalmlds"
                / "functionalmlds.v2.assembly_report.json",
                case_dir
                / "functionalmlds"
                / "functionalmlds.instance.generated.json",
                case_dir / "intermediate" / "scene_semantics.json",
                case_dir
                / "intermediate"
                / "agent_roles.generated.json",
                case_dir / "intermediate" / "handoff_matrix.json",
            )
        ]
        cls.before_hashes = {
            str(path): _sha256(path) for path in cls.input_paths
        }
        cls.results = build_benchmark(REPOSITORY_ROOT)
        cls.environment = build_environment(REPOSITORY_ROOT)

    @classmethod
    def tearDownClass(cls) -> None:
        after = {str(path): _sha256(path) for path in cls.input_paths}
        if after != cls.before_hashes:
            raise AssertionError("The benchmark modified a source artifact.")

    def test_corpus_hashes_and_denominators_are_real(self) -> None:
        cases = self.results["corpus"]["cases"]
        self.assertEqual(list(CASE_IDS), [case["case_id"] for case in cases])
        self.assertEqual(3, len(cases))
        for case in cases:
            path = self.v2_paths[case["case_id"]]
            self.assertEqual(_sha256(path), case["v2_sha256"])
            self.assertEqual(path.stat().st_size, case["v2_bytes"])
            self.assertTrue(case["reference_label"]["expected_valid"])
            self.assertEqual(
                64,
                len(case["fresh_v2_semantic_projection_sha256"]),
            )

        aggregate = self.results["corpus"]["aggregate_counts"]
        self.assertEqual(93, aggregate["scene_objects"])
        self.assertEqual(15, aggregate["agents"])

    def test_every_scene_object_has_unique_asset_priority_owner(self) -> None:
        aggregate = self.results["ownership"]["aggregate"]
        self.assertEqual(93, aggregate["scene_object_denominator"])
        self.assertEqual(
            {
                "asset": 93,
                "group": 0,
                "zone": 0,
                "unassigned": 0,
            },
            aggregate["selected_tier_counts"],
        )
        self.assertEqual(
            {"unique": 93, "ambiguous": 0, "unassigned": 0},
            aggregate["resolution_counts"],
        )

    def test_every_scene_object_has_complete_interaction_chains(self) -> None:
        suite = self.results["asset_interaction_chains"]
        aggregate = suite["aggregate"]
        scene_object_count = self.results["corpus"]["aggregate_counts"][
            "scene_objects"
        ]
        self.assertEqual(scene_object_count, aggregate["asset_denominator"])
        self.assertEqual(
            scene_object_count,
            aggregate["asset_with_chain_candidate_count"],
        )
        self.assertEqual(
            scene_object_count,
            aggregate["complete_asset_count"],
        )
        self.assertEqual(1.0, aggregate["asset_chain_coverage_rate"])
        self.assertEqual(1.0, aggregate["complete_asset_rate"])
        self.assertGreaterEqual(
            aggregate["chain_candidate_denominator"],
            aggregate["asset_denominator"],
        )
        self.assertEqual(
            aggregate["chain_candidate_denominator"],
            aggregate["complete_chain_count"],
        )
        self.assertEqual(1.0, aggregate["chain_completeness_rate"])
        self.assertEqual(0, aggregate["error_count"])
        self.assertEqual([], aggregate["errors"])

        corpus_by_case = {
            case["case_id"]: case
            for case in self.results["corpus"]["cases"]
        }
        for case in suite["case_results"]:
            metrics = case["metrics"]
            with self.subTest(case=case["case_id"]):
                self.assertEqual(
                    corpus_by_case[case["case_id"]]["counts"][
                        "scene_objects"
                    ],
                    metrics["asset_denominator"],
                )
                self.assertEqual(
                    metrics["asset_denominator"],
                    metrics["complete_asset_count"],
                )
                self.assertEqual(
                    metrics["chain_candidate_denominator"],
                    metrics["complete_chain_count"],
                )
                self.assertEqual(0, metrics["error_count"])

    def test_routing_has_explicit_all_start_agent_denominator(self) -> None:
        aggregate = self.results["routing"]["aggregate"]
        expected = sum(
            case["counts"]["scene_objects"] * case["counts"]["agents"]
            for case in self.results["corpus"]["cases"]
        )
        self.assertEqual(459, expected)
        self.assertEqual(expected, aggregate["routing_probe_denominator"])
        self.assertEqual(expected, sum(aggregate["status_counts"].values()))
        self.assertFalse(aggregate["answer_semantics_evaluated"])

    def test_full_runtime_corpus_matches_direct_one_hop_expectations(self) -> None:
        suite = self.results["runtime_corpus"]
        self.assertEqual("pass", suite["status"])
        self.assertEqual(3, suite["case_denominator"])
        self.assertEqual(459, suite["probe_denominator"])
        self.assertEqual(
            {
                "local_owner": 93,
                "direct_allowed": 205,
                "transitive_allowed": 143,
                "rejected_unreachable": 18,
                "ambiguous_target": 0,
                "unassigned_target": 0,
            },
            suite["expected_status_counts"],
        )
        self.assertEqual(298, suite["accepted_probe_denominator"])
        self.assertEqual(298, suite["accepted_with_evidence_count"])
        self.assertEqual(161, suite["rejected_probe_denominator"])
        self.assertEqual(161, suite["fail_closed_before_stub_count"])
        self.assertEqual(161, suite["rejection_zero_stub_call_count"])
        self.assertEqual(
            161,
            suite["rejection_without_state_mutation_count"],
        )
        self.assertEqual(298, suite["structured_stub_calls"])
        self.assertEqual(459, suite["state_restoration_count"])
        self.assertEqual(459, suite["passed_probe_count"])
        self.assertEqual(0, suite["failed_probe_count"])
        self.assertTrue(suite["network_blocked"])
        self.assertEqual(0, suite["api_calls"])
        self.assertTrue(
            suite["fresh_v2_materialized_equality_verified"]
        )
        cache = suite["contract_snapshot_cache"]
        self.assertEqual(3, cache["materialized_contract_disk_load_count"])
        self.assertEqual(
            599,
            cache["session_store_contract_load_call_count"],
        )
        self.assertEqual(596, cache["immutable_snapshot_reuse_count"])

        records = [
            record
            for case in suite["case_results"]
            for record in case["records"]
        ]
        self.assertEqual(
            459,
            len(
                {
                    (
                        item["case_id"],
                        item["start"],
                        item["target"],
                    )
                    for item in records
                }
            ),
        )
        required = {
            "case_id",
            "start",
            "target",
            "expected",
            "actual",
            "stub_calls",
            "state_mutated",
        }
        for record in records:
            with self.subTest(
                case=record["case_id"],
                start=record["start"],
                target=record["target"],
            ):
                self.assertTrue(required.issubset(record))
                self.assertTrue(record["passed"])
                self.assertTrue(record["state_restored"])
                if record["expected_structural_status"] in {
                    "local_owner",
                    "direct_allowed",
                }:
                    self.assertEqual(
                        "accepted_with_evidence",
                        record["actual"],
                    )
                    self.assertEqual(1, record["stub_calls"])
                    self.assertTrue(record["state_mutated"])
                    self.assertTrue(record["evidence_preserved"])
                    self.assertTrue(record["trusted_target_preserved"])
                    self.assertTrue(record["trusted_provider_preserved"])
                    self.assertTrue(record["model_binding_preserved"])
                else:
                    self.assertEqual(
                        "fail_closed_before_stub",
                        record["actual"],
                    )
                    self.assertEqual(0, record["stub_calls"])
                    self.assertFalse(record["state_mutated"])

    def test_direct_wiring_and_fresh_v2_have_full_semantic_parity(self) -> None:
        comparison = self.results["direct_wiring_comparison"]
        aggregate = comparison["aggregate"]
        self.assertEqual("comparable", aggregate["status"])
        self.assertEqual(0, aggregate["parity_failure_count"])
        self.assertEqual(93, aggregate["baseline_responsibility_denominator"])
        self.assertEqual(459, aggregate["baseline_routing_probe_denominator"])

        excluded_zone_only_ids = []
        for case in comparison["case_results"]:
            with self.subTest(case=case["case_id"]):
                self.assertEqual("pass", case["baseline_parity"]["status"])
                self.assertEqual(0, case["baseline_parity"]["mismatch_count"])
                self.assertEqual(
                    case["baseline_semantic_projection_sha256"][
                        "direct_wiring"
                    ],
                    case["baseline_semantic_projection_sha256"]["fresh_v2"],
                )
                excluded_zone_only_ids.extend(
                    case["direct_wiring_object_universe"][
                        "zone_only_reference_ids_excluded"
                    ]
                )
                for mutation in case["mutation_runs"]:
                    self.assertEqual("pass", mutation["parity"]["status"])
                    self.assertEqual(0, mutation["parity"]["mismatch_count"])
        self.assertEqual(["floor_marking_path1"], excluded_zone_only_ids)

    def test_common_mutations_use_independent_delta_validators(self) -> None:
        comparison = self.results["direct_wiring_comparison"]
        for adapter_id, metrics in comparison["aggregate"][
            "adapter_metrics"
        ].items():
            with self.subTest(adapter=adapter_id):
                self.assertEqual(3, metrics["expected_valid_case_denominator"])
                self.assertEqual(0, metrics["baseline_false_positive_count"])
                self.assertEqual(9, metrics["common_mutation_denominator"])
                self.assertEqual(9, metrics["detected_mutation_count"])
                self.assertEqual(1.0, metrics["mutation_detection_rate"])
                self.assertEqual(9, metrics["localized_detection_count"])
                self.assertEqual(1.0, metrics["localization_rate"])
                self.assertGreater(metrics["artifact_edit_count"], 0)
                self.assertGreater(metrics["reference_edit_count"], 0)

        expected_validator_ids = {
            "direct_wiring": "direct_wiring_validator",
            "fresh_v2": "fresh_v2_adapter_validator",
        }
        for case in comparison["case_results"]:
            for adapter_id, validator_id in expected_validator_ids.items():
                baseline = case["baseline_validation"][adapter_id]
                self.assertEqual(validator_id, baseline["validator_id"])
                self.assertTrue(baseline["accepted"])
            for mutation in case["mutation_runs"]:
                for adapter_id in expected_validator_ids:
                    validation = mutation[adapter_id]["validation"]
                    self.assertTrue(validation["detected_by_new_error"])
                    self.assertTrue(validation["localized"])
                    self.assertGreater(
                        mutation[adapter_id]["artifact_edit_count"],
                        0,
                    )
                    self.assertGreater(
                        mutation[adapter_id]["reference_edit_count"],
                        0,
                    )

    def test_synthetic_priority_probes_cover_all_tiers_fail_closed(self) -> None:
        suite = self.results["direct_wiring_comparison"][
            "synthetic_priority_probe_suite"
        ]
        self.assertEqual("pass", suite["status"])
        self.assertFalse(suite["included_in_natural_corpus_metrics"])
        self.assertEqual(3, suite["case_denominator"])
        self.assertEqual(3, suite["probe_types_per_case"])
        self.assertEqual(18, suite["total_adapter_observation_denominator"])
        self.assertEqual(0, suite["semantic_parity_mismatch_count"])
        for adapter_id, metrics in suite["adapter_metrics"].items():
            with self.subTest(adapter=adapter_id):
                self.assertEqual(9, metrics["synthetic_probe_denominator"])
                self.assertEqual(9, metrics["passed_probe_count"])
                self.assertEqual(3, metrics["group_fallback_count"])
                self.assertEqual(3, metrics["zone_fallback_count"])
                self.assertEqual(3, metrics["ambiguity_fail_closed_count"])

        expected = {
            "asset_removed_group_fallback": ("group", "unique", True),
            "asset_and_group_removed_zone_fallback": (
                "zone",
                "unique",
                True,
            ),
            "competing_owner_at_highest_active_tier": (
                "asset",
                "ambiguous",
                False,
            ),
        }
        for case in suite["case_results"]:
            self.assertEqual("pass", case["status"])
            self.assertEqual(3, len(case["probe_results"]))
            for probe in case["probe_results"]:
                tier, resolution, accepted = expected[probe["probe_id"]]
                self.assertEqual("pass", probe["semantic_parity"])
                for adapter_id, observation in probe["adapters"].items():
                    with self.subTest(
                        case=case["case_id"],
                        probe=probe["probe_id"],
                        adapter=adapter_id,
                    ):
                        self.assertEqual(
                            tier,
                            observation["observed_selected_tier"],
                        )
                        self.assertEqual(
                            resolution,
                            observation["observed_resolution"],
                        )
                        self.assertEqual(
                            accepted,
                            observation[
                                "accepted_by_unique_owner_policy"
                            ],
                        )
                        self.assertTrue(observation["passed"])
                        if resolution == "ambiguous":
                            self.assertTrue(
                                observation["ambiguity_fail_closed"]
                            )
                            self.assertEqual(
                                observation["routing_probe_denominator"],
                                observation["routing_status_counts"][
                                    "ambiguous_target"
                                ],
                            )

    def test_v2_only_mutations_are_separate_from_common_denominator(self) -> None:
        suite = self.results["v2_only_validation"]
        self.assertIn("V2-only", suite["suite_scope"])
        for validator_id, metrics in suite["validator_metrics"].items():
            with self.subTest(validator=validator_id):
                self.assertEqual(3, metrics["expected_valid_case_denominator"])
                self.assertEqual(0, metrics["baseline_false_positive_count"])
                self.assertEqual(9, metrics["applicable_mutation_denominator"])
                self.assertGreater(metrics["detected_mutation_count"], 0)
                self.assertIsNotNone(metrics["mutation_detection_rate"])

    def test_runtime_workload_is_repeated_and_output_deterministic(self) -> None:
        cases = self.results["direct_wiring_comparison"]["case_results"]
        for case in cases:
            runtime = case["runtime"]
            with self.subTest(case=case["case_id"]):
                self.assertEqual(4, runtime["warmups"])
                self.assertEqual(40, runtime["repetitions"])
                self.assertTrue(runtime["alternating_execution_order"])
                self.assertTrue(runtime["deterministic_workload_outputs"])
                self.assertEqual(
                    runtime["projection_sha256"]["direct_wiring"],
                    runtime["projection_sha256"]["fresh_v2"],
                )
                self.assertGreater(
                    runtime["direct_wiring"]["median_ns"],
                    0,
                )
                self.assertGreater(runtime["fresh_v2"]["median_ns"], 0)
                for adapter_id in ("direct_wiring", "fresh_v2"):
                    summary = runtime[adapter_id]
                    self.assertLessEqual(
                        summary["min_ns"],
                        summary["q1_ns"],
                    )
                    self.assertLessEqual(
                        summary["q1_ns"],
                        summary["median_ns"],
                    )
                    self.assertLessEqual(
                        summary["median_ns"],
                        summary["q3_ns"],
                    )
                    self.assertLessEqual(
                        summary["q3_ns"],
                        summary["max_ns"],
                    )
                    self.assertGreaterEqual(summary["iqr_ns"], 0)

    def test_stale_checked_in_v2_is_audit_only(self) -> None:
        audit = self.results["checked_in_v2_staleness_audit"]
        self.assertEqual(3, audit["case_denominator"])
        self.assertEqual(3, audit["fresh_regeneration_acceptance_count"])
        comparison = self.results["direct_wiring_comparison"]
        self.assertFalse(
            comparison["fairness_contract"][
                "treatment_uses_checked_in_stale_v2"
            ]
        )

    def test_environment_hashes_every_input_and_uses_no_api(self) -> None:
        inputs = self.environment["input_files"]
        self.assertEqual(18, len(inputs))
        self.assertEqual(
            {
                "v2",
                "assembly_report",
                "v05",
                "scene_semantics",
                "agent_roles",
                "handoff_matrix",
            },
            {item["role"] for item in inputs},
        )
        for item in inputs:
            path = REPOSITORY_ROOT / item["path"]
            self.assertEqual(_sha256(path), item["sha256"])
        self.assertFalse(self.environment["network_required"])
        self.assertFalse(self.environment["api_key_required"])

    def test_no_answer_semantics_or_unexecuted_baseline_is_invented(self) -> None:
        comparison = self.results["legacy_direct_wiring_comparison"]
        self.assertEqual("comparable", comparison["status"])
        self.assertTrue(comparison["numeric_results"])
        self.assertFalse(self.results["scope"]["answer_semantics_evaluated"])
        self.assertEqual(0, self.results["scope"]["api_calls"])

    def test_artifact_serialization_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="iui2027-benchmark-a-"
        ) as first_dir, tempfile.TemporaryDirectory(
            prefix="iui2027-benchmark-b-"
        ) as second_dir:
            first = write_artifacts(
                Path(first_dir),
                self.results,
                self.environment,
            )
            second = write_artifacts(
                Path(second_dir),
                self.results,
                self.environment,
            )
            for key in first:
                with self.subTest(artifact=key):
                    self.assertEqual(
                        first[key].read_bytes(),
                        second[key].read_bytes(),
                    )


if __name__ == "__main__":
    unittest.main()
