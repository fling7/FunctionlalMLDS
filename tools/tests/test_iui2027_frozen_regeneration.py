from __future__ import annotations

import hashlib
import io
import json
import socket
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from research.iui2027.artifact import regenerate_frozen


class FrozenRegenerationTests(unittest.TestCase):
    def test_parser_requires_explicit_nonmutating_or_write_mode(self) -> None:
        self.assertTrue(regenerate_frozen.parse_args(["--check"]).check)
        self.assertTrue(regenerate_frozen.parse_args(["--write"]).write)
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                regenerate_frozen.parse_args([])

    def test_network_guard_blocks_direct_socket_connections(self) -> None:
        candidate = socket.socket()
        try:
            with regenerate_frozen.network_disabled():
                with self.assertRaises(regenerate_frozen.RegenerationError):
                    candidate.connect(("127.0.0.1", 9))
        finally:
            candidate.close()

    def test_case_staging_copies_only_frozen_inputs_and_optional_seeds(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="iui-frozen-staging-test-"
        ) as temporary_name:
            temporary = Path(temporary_name)
            source = temporary / "source" / "case"
            target = temporary / "staged" / "case"
            for relative in regenerate_frozen.FROZEN_CASE_FILES:
                path = source / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}\n", encoding="utf-8")
            source_payload = source / "input" / "source_mlds.json"
            digest = hashlib.sha256(source_payload.read_bytes()).hexdigest()
            (source / "input" / "source_mlds.sha256").write_text(
                digest + "\n",
                encoding="ascii",
            )
            placement = (
                source / "intermediate" / "agent_placements.json"
            )
            placement.write_text('{"placements":[]}\n', encoding="utf-8")
            generated = (
                source
                / "functionalmlds"
                / "functionalmlds.v2.instance.json"
            )
            generated.parent.mkdir(parents=True, exist_ok=True)
            generated.write_text('{"stale":true}\n', encoding="utf-8")

            regenerate_frozen._copy_case_inputs(source, target)

            for relative in regenerate_frozen.FROZEN_CASE_FILES:
                self.assertTrue((target / relative).is_file())
            self.assertTrue(
                (
                    target / "intermediate" / "agent_placements.json"
                ).is_file()
            )
            self.assertFalse(
                (
                    target
                    / "functionalmlds"
                    / "functionalmlds.v2.instance.json"
                ).exists()
            )

    def test_publication_can_roll_back_files_and_directories(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="iui-frozen-publication-test-"
        ) as temporary_name:
            root = Path(temporary_name)
            source_file = root / "stage" / "model.json"
            source_file.parent.mkdir(parents=True)
            source_file.write_text('{"version":2}\n', encoding="utf-8")
            target_file = root / "final" / "model.json"
            target_file.parent.mkdir(parents=True)
            target_file.write_text('{"version":1}\n', encoding="utf-8")

            source_directory = root / "stage" / "kb"
            source_directory.mkdir()
            (source_directory / "new.txt").write_text("new\n", encoding="utf-8")
            target_directory = root / "final" / "kb"
            target_directory.mkdir()
            (target_directory / "old.txt").write_text("old\n", encoding="utf-8")

            publication = regenerate_frozen._Publication()
            publication.prepare(source_file, target_file)
            publication.prepare(source_directory, target_directory)
            publication.apply()
            self.assertEqual(
                {"version": 2},
                json.loads(target_file.read_text(encoding="utf-8")),
            )
            self.assertTrue((target_directory / "new.txt").is_file())

            publication.rollback()
            self.assertEqual(
                {"version": 1},
                json.loads(target_file.read_text(encoding="utf-8")),
            )
            self.assertTrue((target_directory / "old.txt").is_file())
            self.assertFalse((target_directory / "new.txt").exists())

    def test_comparison_reports_bytes_semantics_and_path_normalization(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="iui-frozen-comparison-test-"
        ) as temporary_name:
            root = Path(temporary_name)
            staged_root = root / "stage"
            target_root = root / "target"
            staged = staged_root / "trace.json"
            target = target_root / "trace.json"
            staged.parent.mkdir(parents=True)
            target.parent.mkdir(parents=True)
            staged.write_text(
                json.dumps(
                    {"path": str(staged_root), "values": [1, 2]},
                    separators=(",", ":"),
                ),
                encoding="utf-8",
            )
            target.write_text(
                json.dumps(
                    {"values": [1, 2], "path": str(target_root)},
                    indent=2,
                ),
                encoding="utf-8",
            )

            comparison = regenerate_frozen._comparison_entry(
                logical_path="trace.json",
                staged=staged,
                target=target,
                replacements=[(str(staged_root), str(target_root))],
            )

            self.assertFalse(comparison["byte_equal"])
            self.assertFalse(comparison["semantic_equal"])
            self.assertTrue(comparison["path_normalized_semantic_equal"])


if __name__ == "__main__":
    unittest.main()
