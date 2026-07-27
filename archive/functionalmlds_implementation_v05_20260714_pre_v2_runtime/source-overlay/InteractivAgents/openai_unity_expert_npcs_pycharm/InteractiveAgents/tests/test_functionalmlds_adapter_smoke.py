from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from backend.functionalmlds_adapter import FunctionalMldsAdapter


class FunctionalMldsAdapterSmokeTest(unittest.TestCase):
    def test_existing_case_recovers_without_llm_and_validates_commit(self) -> None:
        backend_root = Path(__file__).resolve().parents[1]
        workspace_root = self._find_workspace_root(backend_root)
        fixture_case = workspace_root / "output" / "case_studies" / "classroom_dinosaur"
        source_payload = self._read_json(fixture_case / "input" / "source_mlds.json")

        with tempfile.TemporaryDirectory(prefix="functionalmlds_adapter_smoke_") as tmp:
            output_root = Path(tmp) / "wizard_functionalmlds"
            adapter = FunctionalMldsAdapter.discover(
                workspace_root=workspace_root,
                backend_root=backend_root,
                output_root=output_root,
            )
            adapter.validate_environment()

            initialized = adapter.initialize_case_from_payload(
                source_payload,
                case_id="classroom_dinosaur",
            )
            case_dir = Path(initialized["case_dir"])
            self.assertTrue((case_dir / "input" / "source_mlds.json").exists())
            self._copy_fixture_outputs(fixture_case, case_dir)

            recovered_stage_ids = (
                "scene_semantics",
                "agent_roles",
                "knowledge_synthesis",
                "functionalmlds_invariants",
                "project_materialization",
                "schema_validation",
                "traceability_metrics",
                "handoff_metrics",
            )
            for stage_id in recovered_stage_ids:
                with self.subTest(stage_id=stage_id):
                    result = adapter.run_stage_deterministic_first(case_dir, stage_id)
                    self.assertEqual("success", result.get("status"))
                    self.assertTrue(result.get("deterministic_recovery"))
                    self.assertFalse(result.get("llm_used"))

            analyze_report = adapter.validate_analyze_case(case_dir)
            self.assertEqual("valid", analyze_report.get("status"), analyze_report.get("errors"))
            analyze_summary = adapter.summarize_analyze_validation(analyze_report)
            self.assertEqual("valid", analyze_summary.get("schema_status"))
            self.assertEqual("valid", analyze_summary.get("invariant_status"))
            self.assertEqual("valid", analyze_summary.get("handoff_status"))

            commit_report = adapter.validate_commit_case(case_dir)
            self.assertEqual("valid", commit_report.get("status"), commit_report.get("errors"))
            commit_summary = adapter.summarize_commit_validation(commit_report)
            self.assertEqual("valid", commit_summary.get("schema_status"))
            self.assertEqual("valid", commit_summary.get("invariant_status"))
            self.assertEqual("valid", commit_summary.get("materialization_status"))
            self.assertEqual("valid", commit_summary.get("traceability_status"))
            self.assertEqual("valid", commit_summary.get("handoff_status"))
            self.assertGreaterEqual(commit_summary.get("traceability_average_coverage", 0.0), 0.8)
            self.assertEqual(1.0, commit_summary.get("handoff_decision_accuracy"))

            instance = self._read_json(case_dir / "functionalmlds" / "functionalmlds.instance.generated.json")
            self.assertEqual("functionalmlds_case_study", instance.get("schema"))
            self.assertEqual("classroom_dinosaur", instance.get("caseId"))
            self.assertTrue(instance.get("requirementsModel", {}).get("useCases"))
            self.assertTrue(instance.get("runtimeBindings"))
            self.assertTrue(instance.get("validationCases"))

            backend_project_dir = backend_root / "projects" / "classroom_dinosaur"
            self.assertTrue((backend_project_dir / "project.json").exists())
            self.assertTrue((backend_project_dir / "room_plan.json").exists())
            self.assertTrue((backend_project_dir / "agents.json").exists())
            self.assertTrue((backend_project_dir / "trace_map.json").exists())
            self.assertTrue(any((backend_project_dir / "kb").rglob("*.txt")))

            manifest = self._read_json(case_dir / "stage_manifest.json")
            stage_entries = {entry.get("stage_id"): entry for entry in manifest.get("stages", [])}
            for stage_id in recovered_stage_ids:
                metadata = stage_entries[stage_id].get("metadata", {})
                self.assertTrue(metadata.get("recovered_without_rerun"))
                self.assertFalse(metadata.get("llm_used"))
                self.assertEqual(0, metadata.get("attempts_used"))

    @staticmethod
    def _find_workspace_root(start: Path) -> Path:
        for candidate in [start, *start.parents]:
            if (candidate / "tools" / "case_study_pipeline").exists():
                return candidate
        raise AssertionError("Workspace root with tools/case_study_pipeline not found.")

    @staticmethod
    def _read_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8-sig"))

    @staticmethod
    def _copy_fixture_outputs(source_case: Path, target_case: Path) -> None:
        ignore = shutil.ignore_patterns("__pycache__")
        for source in source_case.iterdir():
            if source.name == "input":
                continue
            target = target_case / source.name
            if source.is_dir():
                shutil.copytree(source, target, dirs_exist_ok=True, ignore=ignore)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)


if __name__ == "__main__":
    unittest.main()
