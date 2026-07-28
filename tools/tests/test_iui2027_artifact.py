from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research.iui2027.artifact import verify


class Iui2027ArtifactTests(unittest.TestCase):
    def test_case_hash_manifests_are_current(self) -> None:
        facts = verify.check_case_inputs()
        self.assertEqual(3, facts["case_count"])
        self.assertEqual(
            "steinpilz_brand_room",
            facts["canonical_demonstrator"],
        )
        for case in facts["cases"]:
            self.assertRegex(case["source_sha256"], r"^[0-9a-f]{64}$")

    def test_static_unity_contract_requires_pinned_sources(self) -> None:
        facts = verify.check_unity_static()
        self.assertEqual("6000.4.5f1", facts["unity_version"])
        self.assertGreaterEqual(facts["class_file_count"], 6)
        self.assertEqual(3, facts["batch_smoke_count_available"])

    def test_scan_detects_synthetic_identity_and_secrets(self) -> None:
        address = "reviewer" + "@" + "example.invalid"
        local_path = "C:" + "\\Users\\" + "reviewer\\paper.pdf"
        api_secret = "sk-" + ("A" * 24)
        self.assertIn("email_address", verify.scan_text(address))
        self.assertIn("windows_user_path", verify.scan_text(local_path))
        self.assertIn("openai_secret", verify.scan_text(api_secret))
        self.assertEqual([], verify.scan_text("PAPERREVIEW_EMAIL is read from env"))

    def test_summary_write_is_atomic_and_contains_no_local_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iui-artifact-test-") as name:
            path = Path(name) / "summary.json"
            value = {
                "schema": "test",
                "status": "pass",
                "path": "research/iui2027/artifact",
            }
            verify.atomic_write_json(path, value)
            self.assertEqual(value, json.loads(path.read_text(encoding="utf-8")))
            leftovers = list(path.parent.glob(".summary.json.*.tmp"))
            self.assertEqual([], leftovers)

    def test_default_parser_never_starts_network_or_unity(self) -> None:
        args = verify.parse_args([])
        self.assertEqual("check", args.benchmark_mode)
        self.assertIsNone(args.unity_editor)
        self.assertFalse(args.skip_tests)
        self.assertFalse(args.skip_paper_check)

    def test_diagnostics_redact_repository_home_and_identity(self) -> None:
        address = "person" + "@" + "example.invalid"
        diagnostic = f"{verify.REPOSITORY_ROOT} {Path.home()} {address}"
        sanitized = verify.safe_text(diagnostic)
        self.assertNotIn(str(verify.REPOSITORY_ROOT), sanitized)
        self.assertNotIn(str(Path.home()), sanitized)
        self.assertNotIn(address, sanitized)


if __name__ == "__main__":
    unittest.main()
