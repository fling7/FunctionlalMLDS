from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.case_study_pipeline.common import (
    load_manifest,
    manifest_stage_inputs_match,
    manifest_stage_metadata_matches,
    update_manifest,
    verify_manifest_stage_integrity,
)


class StageFingerprintInvalidationTests(unittest.TestCase):
    def test_input_content_dependency_set_and_model_metadata_invalidate_stage(self) -> None:
        with tempfile.TemporaryDirectory(prefix="stage-fingerprint-") as temporary:
            root = Path(temporary)
            case_dir = root / "case"
            case_dir.mkdir()
            model = root / "model.json"
            prompt = root / "prompt.md"
            implementation = root / "stage.py"
            output = root / "result.json"
            model.write_text('{"version": 1}', encoding="utf-8")
            prompt.write_text("prompt-v1", encoding="utf-8")
            implementation.write_text("VERSION = 1\n", encoding="utf-8")
            output.write_text('{"status": "valid"}', encoding="utf-8")
            dependencies = [model, prompt, implementation]

            update_manifest(
                case_dir,
                stage_id="example",
                status="success",
                input_paths=dependencies,
                output_paths=[output],
                metadata={"llm": {"model": "model-a"}},
            )

            self.assertTrue(
                manifest_stage_inputs_match(
                    case_dir,
                    "example",
                    dependencies,
                )
            )
            self.assertTrue(
                manifest_stage_metadata_matches(
                    case_dir,
                    "example",
                    {"llm.model": "model-a"},
                )
            )
            self.assertFalse(
                manifest_stage_metadata_matches(
                    case_dir,
                    "example",
                    {"llm.model": "model-b"},
                )
            )
            self.assertFalse(
                manifest_stage_inputs_match(
                    case_dir,
                    "example",
                    [model, prompt],
                ),
                "A dependency subset must not authorize stale stage reuse.",
            )

            implementation.write_text("VERSION = 2\n", encoding="utf-8")
            self.assertFalse(
                manifest_stage_inputs_match(
                    case_dir,
                    "example",
                    dependencies,
                )
            )

    def test_integrity_reports_question_or_project_output_drift(self) -> None:
        with tempfile.TemporaryDirectory(prefix="stage-integrity-") as temporary:
            root = Path(temporary)
            case_dir = root / "case"
            case_dir.mkdir()
            questions = root / "evaluation_questions.json"
            project = root / "project.json"
            result = root / "chat_results.json"
            questions.write_text('{"questions": []}', encoding="utf-8")
            project.write_text('{"id": "case"}', encoding="utf-8")
            result.write_text('{"status": "valid"}', encoding="utf-8")

            update_manifest(
                case_dir,
                stage_id="chat_tests",
                status="success",
                input_paths=[questions, project],
                output_paths=[result],
            )
            entry = next(
                item
                for item in load_manifest(case_dir)["stages"]
                if item["stage_id"] == "chat_tests"
            )
            self.assertTrue(verify_manifest_stage_integrity(entry)["valid"])

            questions.write_text('{"questions": [{"id": "new"}]}', encoding="utf-8")
            integrity = verify_manifest_stage_integrity(entry)

            self.assertFalse(integrity["valid"])
            self.assertEqual(1, integrity["drift_count"])
            self.assertEqual("sha256_mismatch", integrity["drift"][0]["reason"])
            self.assertEqual(str(questions), integrity["drift"][0]["path"])


if __name__ == "__main__":
    unittest.main()
