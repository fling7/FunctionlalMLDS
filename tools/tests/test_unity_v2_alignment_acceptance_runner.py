from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.run_unity_v2_alignment_acceptance import (
    PYTEST_LOG_MARKERS,
    UNITY_COMPLETION_MARKER,
    UNITY_LOG_MARKERS,
    UNITY_SOURCE_RELATIVES,
    verify_python_test_logs,
    verify_tasklist,
    verify_unity_logs,
    verify_unity_source_copies,
)


class UnityV2AlignmentAcceptanceRunnerTests(unittest.TestCase):
    def test_tasklist_requires_every_identifier_and_checkbox_once(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            path = Path(temp_text) / "tasks.md"
            path.write_text(
                "\n".join(
                    f"- [{'x' if number < 44 else ' '}] **UV2-{number:02d} – Task.**"
                    for number in range(1, 45)
                ),
                encoding="utf-8",
            )
            relaxed = verify_tasklist(path)
            strict = verify_tasklist(path, require_closed=True)
            self.assertEqual("pass", relaxed["status"])
            self.assertEqual(43, relaxed["closed_count"])
            self.assertEqual(["UV2-44"], relaxed["open_ids"])
            self.assertEqual("fail", strict["status"])

            path.write_text(path.read_text(encoding="utf-8").replace("UV2-44", "UV2-43"), encoding="utf-8")
            invalid = verify_tasklist(path)
            self.assertEqual("fail", invalid["status"])
            self.assertEqual(["UV2-44"], invalid["missing_ids"])
            self.assertEqual(["UV2-43"], invalid["duplicate_ids"])

    def test_unity_logs_need_success_and_completion_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            root = Path(temp_text)
            paths = {}
            for kind, marker in UNITY_LOG_MARKERS.items():
                path = root / f"{kind}.log"
                path.write_text(f"{marker}\n{UNITY_COMPLETION_MARKER}\n", encoding="utf-8")
                paths[kind] = path
            self.assertEqual("pass", verify_unity_logs(paths)["status"])

            paths["native"].write_text(UNITY_COMPLETION_MARKER, encoding="utf-8")
            result = verify_unity_logs(paths)
            self.assertEqual("fail", result["status"])
            native = next(item for item in result["logs"] if item["kind"] == "native")
            self.assertFalse(native["marker_found"])

    def test_unity_source_copy_check_is_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            root = Path(temp_text)
            unity = root / "unity"
            copied = root / "copy"
            for relative in UNITY_SOURCE_RELATIVES:
                payload = (relative + "\n").encode("utf-8")
                for base in (unity, copied):
                    path = base / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(payload)
            self.assertEqual("pass", verify_unity_source_copies(unity, copied)["status"])

            (copied / UNITY_SOURCE_RELATIVES[0]).write_text("drift", encoding="utf-8")
            self.assertEqual("fail", verify_unity_source_copies(unity, copied)["status"])

    def test_python_test_logs_need_every_success_marker_and_no_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_text:
            root = Path(temp_text)
            paths = {}
            for kind, markers in PYTEST_LOG_MARKERS.items():
                path = root / f"{kind}.log"
                path.write_text("\n".join(markers) + "\n", encoding="utf-8")
                paths[kind] = path
            self.assertEqual("pass", verify_python_test_logs(paths)["status"])

            paths["backend"].write_text("5 passed\n1 failed\n", encoding="utf-8")
            result = verify_python_test_logs(paths)
            self.assertEqual("fail", result["status"])
            backend = next(item for item in result["logs"] if item["kind"] == "backend")
            self.assertFalse(backend["markers_found"])


if __name__ == "__main__":
    unittest.main()
