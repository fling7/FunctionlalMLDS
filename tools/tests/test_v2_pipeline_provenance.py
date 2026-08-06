"""Regression tests for V2 pipeline ordering and provenance invalidation."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
for import_root in (ROOT, TOOLS):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from dynamic_functional_mlds_v2_compat import (  # noqa: E402
    discover_v05_instances,
    import_v05,
    structural_sha256,
)
from case_study_pipeline.functionalmlds_v2_assembler import (  # noqa: E402
    run_functionalmlds_v2_assembly_for_case,
)
from case_study_pipeline.project_materializer import _ensure_v2_instance  # noqa: E402
from case_study_pipeline.stage_completion import (  # noqa: E402
    REQUIRED_STAGES,
    REQUIRED_VALIDATION_REPORTS,
)


class V2PipelineProvenanceTests(unittest.TestCase):
    def test_existing_v2_is_regenerated_when_v05_semantic_projection_drifts(self) -> None:
        source_fixture = discover_v05_instances(ROOT)[0]
        with tempfile.TemporaryDirectory(prefix="functionalmlds_v2_provenance_") as tmp:
            case_dir = Path(tmp) / "case"
            source_path = case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"
            source_path.parent.mkdir(parents=True)
            shutil.copyfile(source_fixture, source_path)

            run_functionalmlds_v2_assembly_for_case(case_dir)
            v2_path = case_dir / "functionalmlds" / "functionalmlds.v2.instance.json"
            before = json.loads(v2_path.read_text(encoding="utf-8"))
            before_hash = before["sourceContract"]["semanticProjectionSha256"]

            source = json.loads(source_path.read_text(encoding="utf-8-sig"))
            source["requirementsModel"]["requirements"][0]["text"] += " Provenance mutation."
            source_path.write_text(json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8")

            ensured = _ensure_v2_instance(case_dir)
            self.assertEqual(v2_path, ensured)
            after = json.loads(v2_path.read_text(encoding="utf-8"))
            expected_projection = import_v05(source)["dynamicFunctionalModel"]
            expected_hash = structural_sha256(expected_projection)
            self.assertNotEqual(before_hash, expected_hash)
            self.assertEqual(expected_hash, after["sourceContract"]["semanticProjectionSha256"])

    def test_stage_completion_requires_handoff_before_v2_and_its_report(self) -> None:
        assembly_index = REQUIRED_STAGES.index("functionalmlds_assembly")
        handoff_index = REQUIRED_STAGES.index("handoff_derivation")
        v2_index = REQUIRED_STAGES.index("functionalmlds_v2_assembly")
        self.assertLess(assembly_index, handoff_index)
        self.assertLess(handoff_index, v2_index)
        self.assertIn(
            Path("validation/handoff_derivation_validation.json"),
            REQUIRED_VALIDATION_REPORTS,
        )


if __name__ == "__main__":
    unittest.main()
