from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from backend.functionalmlds_adapter import FunctionalMldsAdapter


class FunctionalMldsRecoveryProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.backend_root = Path(__file__).resolve().parents[1]
        cls.workspace_root = cls._find_workspace_root(cls.backend_root)
        tools_root = cls.workspace_root / "tools"
        for import_root in (cls.workspace_root, tools_root):
            if str(import_root) not in sys.path:
                sys.path.insert(0, str(import_root))
        from case_study_pipeline.common import update_manifest
        from case_study_pipeline.agent_placement import PLACEMENT_ALGORITHM_VERSION

        cls.update_manifest = staticmethod(update_manifest)
        cls.placement_algorithm_version = PLACEMENT_ALGORITHM_VERSION

    def test_agent_placement_recovery_rejects_old_algorithm_contract(self) -> None:
        with self._case() as (adapter, case_dir, _backend_root):
            inputs = [
                self._write(case_dir / relative, {"input": relative})
                for relative in (
                    "intermediate/scene_graph.normalized.json",
                    "intermediate/scene_semantics.json",
                    "intermediate/agent_roles.generated.json",
                )
            ]
            placements = self._write(case_dir / "intermediate/agent_placements.json", {"agent_placements": []})
            validation_path = case_dir / "validation/agent_placement_validation.json"
            validation = self._write(
                validation_path,
                {
                    "status": "valid",
                    "placement_algorithm_version": self.placement_algorithm_version,
                    "errors": [],
                    "warnings": [],
                    "metrics": {},
                },
            )
            self.update_manifest(
                case_dir,
                stage_id="agent_placement",
                status="success",
                input_paths=inputs,
                output_paths=[placements, validation],
            )
            self.assertIsNotNone(adapter.try_deterministic_recovery(case_dir, "agent_placement"))

            self._write(
                validation_path,
                {
                    "status": "valid",
                    "placement_algorithm_version": "1.0.0",
                    "errors": [],
                    "warnings": [],
                    "metrics": {},
                },
            )
            self.assertIsNone(adapter.try_deterministic_recovery(case_dir, "agent_placement"))

    def test_agent_placement_recovery_rejects_mutated_recorded_output(self) -> None:
        with self._case() as (adapter, case_dir, _backend_root):
            inputs = [
                self._write(case_dir / relative, {"input": relative})
                for relative in (
                    "intermediate/scene_graph.normalized.json",
                    "intermediate/scene_semantics.json",
                    "intermediate/agent_roles.generated.json",
                )
            ]
            placements = self._write(
                case_dir / "intermediate/agent_placements.json",
                {"agent_placements": [{"agent_id": "AG-1"}]},
            )
            validation = self._write(
                case_dir / "validation/agent_placement_validation.json",
                {
                    "status": "valid",
                    "placement_algorithm_version": self.placement_algorithm_version,
                    "errors": [],
                    "warnings": [],
                    "metrics": {},
                },
            )
            self.update_manifest(
                case_dir,
                stage_id="agent_placement",
                status="success",
                input_paths=inputs,
                output_paths=[placements, validation],
            )

            self.assertIsNotNone(adapter.try_deterministic_recovery(case_dir, "agent_placement"))
            self._write(placements, {"agent_placements": [{"agent_id": "MUTATED"}]})
            self.assertIsNone(adapter.try_deterministic_recovery(case_dir, "agent_placement"))

    def test_knowledge_recovery_repairs_missing_but_rejects_mutated_existing_file(self) -> None:
        with self._case() as (adapter, case_dir, _backend_root):
            inputs = [
                self._write(case_dir / relative, {"input": relative})
                for relative in (
                    "intermediate/scene_graph.normalized.json",
                    "intermediate/scene_semantics.json",
                    "intermediate/agent_roles.generated.json",
                )
            ]
            knowledge = self._write(
                case_dir / "intermediate/knowledge.generated.json",
                {
                    "knowledge_entries": [
                        {"tag": "room", "name": "facts", "text": "Original facts"},
                    ]
                },
            )
            validation = self._write_valid(
                case_dir / "validation/knowledge_synthesis_validation.json"
            )
            kb_file = self._write(
                case_dir / "interactive_agents_project/kb/room/facts.txt",
                "Original facts\n",
            )
            self.update_manifest(
                case_dir,
                stage_id="knowledge_synthesis",
                status="success",
                input_paths=inputs,
                output_paths=[knowledge, validation, kb_file],
            )

            unrecorded = self._write(
                case_dir / "interactive_agents_project/kb/unrecorded.txt",
                "not in the historical manifest",
            )
            self.assertIsNone(adapter.try_deterministic_recovery(case_dir, "knowledge_synthesis"))
            unrecorded.unlink()

            kb_file.unlink()
            recovered = adapter.try_deterministic_recovery(case_dir, "knowledge_synthesis")
            self.assertIsNotNone(recovered)
            self.assertEqual(kb_file.read_text(encoding="utf-8"), "Original facts\n")

            kb_file.write_text("Tampered facts\n", encoding="utf-8")
            self.assertIsNone(adapter.try_deterministic_recovery(case_dir, "knowledge_synthesis"))
            self.assertEqual(kb_file.read_text(encoding="utf-8"), "Tampered facts\n")

    def test_directory_tree_hash_detects_added_file_and_unhashed_directory_is_not_trusted(self) -> None:
        with self._case() as (adapter, case_dir, _backend_root):
            inputs = [
                self._write(case_dir / relative, {"input": relative})
                for relative in (
                    "intermediate/scene_graph.normalized.json",
                    "intermediate/scene_semantics.json",
                    "intermediate/agent_roles.generated.json",
                )
            ]
            knowledge = self._write(
                case_dir / "intermediate/knowledge.generated.json",
                {
                    "knowledge_entries": [
                        {"tag": "room", "name": "facts", "text": "Original facts"},
                    ]
                },
            )
            validation = self._write_valid(
                case_dir / "validation/knowledge_synthesis_validation.json"
            )
            kb_root = case_dir / "interactive_agents_project/kb"
            self._write(kb_root / "room/facts.txt", "Original facts\n")
            self.update_manifest(
                case_dir,
                stage_id="knowledge_synthesis",
                status="success",
                input_paths=inputs,
                output_paths=[knowledge, validation, kb_root],
            )
            manifest_path = case_dir / "stage_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            directory_record = next(
                record
                for record in manifest["stages"][0]["outputs"]
                if record["path"] == str(kb_root)
            )
            self.assertEqual(directory_record["tree_sha256"], adapter._tree_sha256(kb_root))
            self.assertIsNotNone(adapter.try_deterministic_recovery(case_dir, "knowledge_synthesis"))

            self._write(kb_root / "unexpected.txt", "unexpected")
            self.assertIsNone(adapter.try_deterministic_recovery(case_dir, "knowledge_synthesis"))

            # A legacy directory entry without either a tree hash or complete
            # per-file records is not a trustworthy cache proof.
            (kb_root / "unexpected.txt").unlink()
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            directory_record = next(
                record
                for record in manifest["stages"][0]["outputs"]
                if record["path"] == str(kb_root)
            )
            directory_record.pop("tree_sha256", None)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertIsNone(adapter.try_deterministic_recovery(case_dir, "knowledge_synthesis"))

    def test_v2_recovery_rejects_changed_v05_input(self) -> None:
        with self._case() as (adapter, case_dir, _backend_root):
            source = self._write(case_dir / "functionalmlds/functionalmlds.instance.generated.json", {"source": 1})
            v2 = self._write(case_dir / "functionalmlds/functionalmlds.v2.instance.json", {"v2": 1})
            report = self._write_valid(case_dir / "functionalmlds/functionalmlds.v2.assembly_report.json")
            self.update_manifest(
                case_dir,
                stage_id="functionalmlds_v2_assembly",
                status="success",
                input_paths=[source],
                output_paths=[v2, report],
            )

            recovered = adapter.try_deterministic_recovery(case_dir, "functionalmlds_v2_assembly")
            self.assertIsNotNone(recovered)
            self._write(source, {"source": 2})
            self.assertIsNone(adapter.try_deterministic_recovery(case_dir, "functionalmlds_v2_assembly"))

    def test_project_materialization_recovery_rejects_changed_source(self) -> None:
        with self._case() as (adapter, case_dir, backend_root):
            inputs = [
                self._write(case_dir / relative, {"input": relative})
                for relative in (
                    "input/source_mlds.json",
                    "intermediate/agent_roles.generated.json",
                    "intermediate/agent_placements.json",
                    "intermediate/knowledge.generated.json",
                    "functionalmlds/functionalmlds.instance.generated.json",
                    "functionalmlds/functionalmlds.v2.instance.json",
                )
            ]
            validation = self._write_valid(case_dir / "validation/project_materialization_validation.json")
            project_dir = backend_root / "projects" / case_dir.name
            outputs = [
                self._write(project_dir / name, {"output": name})
                for name in (
                    "project.json",
                    "room_plan.json",
                    "agents.json",
                    "trace_map.json",
                    "trace_map.v2.json",
                    "trace_map.v05.json",
                    "functionalmlds.v2.instance.json",
                    "functionalmlds.v05.instance.json",
                )
            ]
            kb_root = project_dir / "kb"
            kb_file = self._write(kb_root / "knowledge.txt", "knowledge")
            self.update_manifest(
                case_dir,
                stage_id="project_materialization",
                status="success",
                input_paths=inputs,
                output_paths=[*outputs, validation, kb_file],
            )

            recovered = adapter.try_deterministic_recovery(case_dir, "project_materialization")
            self.assertIsNotNone(recovered)
            self._write(inputs[0], {"input": "changed"})
            self.assertIsNone(adapter.try_deterministic_recovery(case_dir, "project_materialization"))

    def test_schema_recovery_rejects_changed_additional_manifest_input(self) -> None:
        with self._case() as (adapter, case_dir, backend_root):
            v05 = self._write(case_dir / "functionalmlds/functionalmlds.instance.generated.json", {"v05": 1})
            v2 = self._write(case_dir / "functionalmlds/functionalmlds.v2.instance.json", {"v2": 1})
            project = self._write(backend_root / "projects" / case_dir.name / "project.json", {"project": 1})
            validation = self._write_valid(case_dir / "validation/schema_validation.json")
            self.update_manifest(
                case_dir,
                stage_id="schema_validation",
                status="success",
                input_paths=[v05, v2, project],
                output_paths=[validation],
            )

            recovered = adapter.try_deterministic_recovery(case_dir, "schema_validation")
            self.assertIsNotNone(recovered)
            self._write(project, {"project": 2})
            self.assertIsNone(adapter.try_deterministic_recovery(case_dir, "schema_validation"))

    def _case(self):
        return _TemporaryCase(self.workspace_root)

    @staticmethod
    def _write(path: Path, payload):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    @classmethod
    def _write_valid(cls, path: Path) -> Path:
        return cls._write(path, {"status": "valid", "errors": [], "warnings": [], "metrics": {}})

    @staticmethod
    def _find_workspace_root(start: Path) -> Path:
        for candidate in [start, *start.parents]:
            if (candidate / "tools" / "case_study_pipeline").exists():
                return candidate
        raise AssertionError("Workspace root with tools/case_study_pipeline not found.")


class _TemporaryCase:
    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.temp = tempfile.TemporaryDirectory(prefix="functionalmlds_recovery_provenance_")

    def __enter__(self):
        root = Path(self.temp.name)
        case_dir = root / "case"
        backend_root = root / "backend"
        case_dir.mkdir(parents=True)
        backend_root.mkdir(parents=True)
        adapter = FunctionalMldsAdapter.discover(
            workspace_root=self.workspace_root,
            backend_root=backend_root,
            output_root=root / "output",
        )
        return adapter, case_dir, backend_root

    def __exit__(self, exc_type, exc, traceback):
        self.temp.cleanup()


if __name__ == "__main__":
    unittest.main()
