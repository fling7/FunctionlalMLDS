from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

from tools.case_study_pipeline.functionalmlds_v2_assembler import (  # noqa: E402
    assemble_functionalmlds_v2_instance,
    validate_functionalmlds_v2_instance,
)
from tools.case_study_pipeline.project_materializer import build_trace_map_v2  # noqa: E402
from tools.case_study_pipeline.validators.schema_validator import (  # noqa: E402
    V05_GENERATED_INSTANCE_FILENAME,
    V05_PROJECT_INSTANCE_FILENAME,
    V05_TRACE_SCHEMA,
    V05_VERSIONED_TRACE_FILENAME,
    V2_GENERATED_INSTANCE_FILENAME,
    V2_ASSEMBLY_REPORT_FILENAME,
    V2_MODEL_VERSION,
    V2_PROJECT_INSTANCE_FILENAME,
    V2_TRACE_SCHEMA,
    V2_TRACE_VERSION,
    V2_VERSIONED_TRACE_FILENAME,
    validate_case_schemas,
)


CASE_ID = "classroom_dinosaur"
REFERENCE_CASE = ROOT / "output" / "case_studies" / CASE_ID


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _legacy_trace(case_dir: Path, project_dir: Path) -> dict:
    return {
        "schema": V05_TRACE_SCHEMA,
        "case_id": CASE_ID,
        "functionalmlds_path": str(case_dir / "functionalmlds" / V05_GENERATED_INSTANCE_FILENAME),
        "project_files": {
            "project": str(project_dir / "project.json"),
            "agents": str(project_dir / "agents.json"),
            "room_plan": str(project_dir / "room_plan.json"),
        },
        "scenario_steps": [{"scenario_step_id": "STEP"}],
        "capabilities": [{"capability_id": "CAP"}],
        "runtime_actions": [{"runtime_action_id": "RA"}],
        "validation_cases": [{"validation_case_id": "VC"}],
        "agents": [{"agent_id": "agent"}],
    }


def _v2_trace(case_dir: Path, project_dir: Path, model_sha256: str) -> dict:
    return {
        "schema": V2_TRACE_SCHEMA,
        "schema_version": V2_TRACE_VERSION,
        "model_version": V2_MODEL_VERSION,
        "model_sha256": model_sha256,
        "profile": "executable",
        "case_id": CASE_ID,
        "functionalmlds_path": str(case_dir / "functionalmlds" / V05_GENERATED_INSTANCE_FILENAME),
        "functionalmlds_v2_path": str(case_dir / "functionalmlds" / V2_GENERATED_INSTANCE_FILENAME),
        "project_files": {
            "project": str(project_dir / "project.json"),
            "agents": str(project_dir / "agents.json"),
            "room_plan": str(project_dir / "room_plan.json"),
        },
        "use_case_id": "UC-CLASSROOM",
        "main_scenario_id": "SCN-CLASSROOM-MAIN",
        "scenario_steps": [{"scenario_step_id": "STEP"}],
        "step_relations": [{"step_relation_id": "REL"}],
        "parallel_groups": [],
        "guards": [],
        "capabilities": [{"capability_id": "CAP"}],
        "assertions": [{"assertion_id": "ASSERT"}],
        "runtime_actions": [{"runtime_action_id": "RA"}],
        "validation_cases": [{"validation_case_id": "VC"}],
        "runtime_validation_targets": [{"runtime_validation_target_id": "VT"}],
        "agents": [{"agent_id": "agent"}],
    }


class DualSchemaValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v05 = _read_json(
            REFERENCE_CASE / "functionalmlds" / V05_GENERATED_INSTANCE_FILENAME
        )
        cls.v2 = assemble_functionalmlds_v2_instance(cls.v05)

    def _materialize_test_case(self, root: Path, *, dual: bool) -> tuple[Path, Path]:
        case_dir = root / "cases" / CASE_ID
        backend_root = root / "backend"
        project_dir = backend_root / "projects" / CASE_ID
        intermediate = case_dir / "intermediate"
        intermediate.mkdir(parents=True, exist_ok=True)
        for filename in (
            "scene_graph.normalized.json",
            "scene_semantics.json",
            "knowledge.generated.json",
            "agent_roles.generated.json",
            "handoff_matrix.json",
        ):
            shutil.copyfile(REFERENCE_CASE / "intermediate" / filename, intermediate / filename)

        v05_source = case_dir / "functionalmlds" / V05_GENERATED_INSTANCE_FILENAME
        _write_json(v05_source, self.v05)
        _write_json(
            project_dir / "agents.json",
            {
                "agents": [
                    {
                        "id": "agent",
                        "display_name": "Agent",
                        "persona": "",
                        "expertise": [],
                        "knowledge_tags": [],
                        "position": {"x": 0.0, "y": 0.0, "z": 0.0},
                        "forward": {"x": 0.0, "y": 0.0, "z": 1.0},
                    }
                ]
            },
        )
        _write_json(project_dir / "room_plan.json", {"scene": {}})

        if not dual:
            _write_json(
                project_dir / "project.json",
                {
                    "id": CASE_ID,
                    "display_name": "Classroom Dinosaur",
                    "description": "Legacy test project",
                    "created_ms": 1,
                    "updated_ms": 2,
                    "generation_mode": "functionalmlds",
                    "metamodelVersion": "v0.5",
                },
            )
            _write_json(project_dir / "trace_map.json", _legacy_trace(case_dir, project_dir))
            return case_dir, backend_root

        v2_source = case_dir / "functionalmlds" / V2_GENERATED_INSTANCE_FILENAME
        v2_project = project_dir / V2_PROJECT_INSTANCE_FILENAME
        _write_json(v2_source, self.v2)
        _write_json(
            case_dir / "functionalmlds" / V2_ASSEMBLY_REPORT_FILENAME,
            validate_functionalmlds_v2_instance(self.v2),
        )
        _write_json(v2_project, self.v2)
        _write_json(project_dir / V05_PROJECT_INSTANCE_FILENAME, self.v05)
        model_sha256 = _sha256(v2_project)
        agent_roles = _read_json(intermediate / "agent_roles.generated.json")
        trace_v2 = build_trace_map_v2(
            case_dir=case_dir,
            project_dir=project_dir,
            functionalmlds_instance=self.v2,
            agent_roles=agent_roles,
            model_sha256=model_sha256,
        )
        trace_agent_by_source = {
            item["agent_id"]: item for item in trace_v2["agents"]
        }
        _write_json(
            project_dir / "agents.json",
            {
                "agents": [
                    {
                        "id": item["id"],
                        "display_name": item.get("display_name") or item["id"],
                        "persona": item.get("persona") or "test persona",
                        "expertise": item.get("expertise") or [],
                        "knowledge_tags": item.get("knowledge_tags") or [],
                        "position": {"x": 0.0, "y": 0.0, "z": 0.0},
                        "forward": {"x": 0.0, "y": 0.0, "z": 1.0},
                        "functionalmlds_agent_ref": trace_agent_by_source[item["id"]][
                            "functionalmlds_agent_id"
                        ],
                        "functionalmlds_entity_ref": trace_agent_by_source[item["id"]][
                            "entity_id"
                        ],
                        "provided_capability_ids": trace_agent_by_source[item["id"]][
                            "provided_capability_ids"
                        ],
                        "plays_actor_ids": trace_agent_by_source[item["id"]]["plays_actor"],
                    }
                    for item in agent_roles["agents"]
                ]
            },
        )
        _write_json(project_dir / "trace_map.json", trace_v2)
        _write_json(project_dir / V2_VERSIONED_TRACE_FILENAME, trace_v2)
        _write_json(project_dir / V05_VERSIONED_TRACE_FILENAME, _legacy_trace(case_dir, project_dir))
        _write_json(
            project_dir / "project.json",
            {
                "id": CASE_ID,
                "display_name": "Classroom Dinosaur",
                "description": "Dual V2 test project",
                "created_ms": 1,
                "updated_ms": 2,
                "generation_mode": "functionalmlds",
                "metamodelVersion": V2_MODEL_VERSION,
                "functionalmlds_model_path": str(v2_project),
                "functionalmlds_legacy_path": str(project_dir / V05_PROJECT_INSTANCE_FILENAME),
                "functionalmlds_trace_map_path": str(project_dir / V2_VERSIONED_TRACE_FILENAME),
                "functionalmlds_legacy_trace_map_path": str(project_dir / V05_VERSIONED_TRACE_FILENAME),
                "functionalmlds_model_sha256": model_sha256,
                "functionalmlds_model_version": V2_MODEL_VERSION,
                "functionalmlds_model_schema": "dynamic_functional_mlds_v2_instance",
                "functionalmlds_profile": "executable",
                "functionalmlds_trace_schema_version": V2_TRACE_VERSION,
            },
        )
        return case_dir, backend_root

    def test_legacy_project_remains_valid_without_versioned_v2_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="schema-validator-v05-") as temp:
            case_dir, backend_root = self._materialize_test_case(Path(temp), dual=False)
            report = validate_case_schemas(case_dir=case_dir, backend_root=backend_root)
        self.assertEqual("valid", report["status"], report["errors"])
        self.assertEqual("v0.5", report["contract_mode"])
        artifact_ids = {item["artifact_id"] for item in report["artifacts"]}
        self.assertIn("functionalmlds_instance", artifact_ids)
        self.assertNotIn("functionalmlds_v2_instance", artifact_ids)

    def test_complete_dual_v2_project_passes_schema_and_canonical_validator(self) -> None:
        with tempfile.TemporaryDirectory(prefix="schema-validator-v2-") as temp:
            case_dir, backend_root = self._materialize_test_case(Path(temp), dual=True)
            report = validate_case_schemas(case_dir=case_dir, backend_root=backend_root)
        self.assertEqual("valid", report["status"], report["errors"])
        self.assertEqual("v2-dual", report["contract_mode"])
        by_id = {item["artifact_id"]: item for item in report["artifacts"]}
        self.assertEqual("valid", by_id["functionalmlds_v2_instance"]["status"])
        self.assertEqual("valid", by_id["functionalmlds_v05_instance"]["status"])

    def test_dual_project_requires_explicit_legacy_instance(self) -> None:
        with tempfile.TemporaryDirectory(prefix="schema-validator-missing-v05-") as temp:
            case_dir, backend_root = self._materialize_test_case(Path(temp), dual=True)
            (backend_root / "projects" / CASE_ID / V05_PROJECT_INSTANCE_FILENAME).unlink()
            report = validate_case_schemas(case_dir=case_dir, backend_root=backend_root)
        self.assertEqual("invalid", report["status"])
        self.assertTrue(
            any(V05_PROJECT_INSTANCE_FILENAME in error for error in report["errors"]),
            report["errors"],
        )

    def test_dual_project_requires_valid_v2_assembly_report(self) -> None:
        with tempfile.TemporaryDirectory(prefix="schema-validator-report-") as temp:
            case_dir, backend_root = self._materialize_test_case(Path(temp), dual=True)
            report_path = case_dir / "functionalmlds" / V2_ASSEMBLY_REPORT_FILENAME
            assembly_report = _read_json(report_path)
            assembly_report["status"] = "invalid"
            assembly_report["ok"] = False
            _write_json(report_path, assembly_report)
            report = validate_case_schemas(case_dir=case_dir, backend_root=backend_root)
        self.assertEqual("invalid", report["status"])
        self.assertTrue(
            any(V2_ASSEMBLY_REPORT_FILENAME in error for error in report["errors"]),
            report["errors"],
        )

    def test_v2_project_rejects_legacy_active_trace_and_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory(prefix="schema-validator-drift-") as temp:
            case_dir, backend_root = self._materialize_test_case(Path(temp), dual=True)
            project_dir = backend_root / "projects" / CASE_ID
            _write_json(project_dir / "trace_map.json", _legacy_trace(case_dir, project_dir))
            project = _read_json(project_dir / "project.json")
            project["functionalmlds_model_sha256"] = "0" * 64
            _write_json(project_dir / "project.json", project)
            report = validate_case_schemas(case_dir=case_dir, backend_root=backend_root)
        self.assertEqual("invalid", report["status"])
        joined = "\n".join(report["errors"])
        self.assertIn("requires active trace_map.json schema", joined)
        self.assertIn("does not match functionalmlds.v2.instance.json SHA-256", joined)

    def test_v2_project_requires_exact_runtime_metadata(self) -> None:
        mutations = {
            "metamodelVersion": "v0.5",
            "functionalmlds_model_version": "2.0",
            "functionalmlds_model_schema": "functionalmlds_case_study",
            "functionalmlds_profile": "full-surface",
            "functionalmlds_trace_schema_version": "1.0",
        }
        for field, bad_value in mutations.items():
            with self.subTest(field=field), tempfile.TemporaryDirectory(
                prefix=f"schema-validator-meta-{field}-"
            ) as temp:
                case_dir, backend_root = self._materialize_test_case(Path(temp), dual=True)
                project_path = backend_root / "projects" / CASE_ID / "project.json"
                project = _read_json(project_path)
                project[field] = bad_value
                _write_json(project_path, project)
                report = validate_case_schemas(case_dir=case_dir, backend_root=backend_root)
            self.assertEqual("invalid", report["status"], report["errors"])
            self.assertTrue(
                any(field in error for error in report["errors"]),
                report["errors"],
            )

    def test_v2_agents_require_native_mapping_fields(self) -> None:
        with tempfile.TemporaryDirectory(prefix="schema-validator-agent-map-") as temp:
            case_dir, backend_root = self._materialize_test_case(Path(temp), dual=True)
            agents_path = backend_root / "projects" / CASE_ID / "agents.json"
            agents = _read_json(agents_path)
            del agents["agents"][0]["functionalmlds_agent_ref"]
            _write_json(agents_path, agents)
            report = validate_case_schemas(case_dir=case_dir, backend_root=backend_root)
        self.assertEqual("invalid", report["status"])
        self.assertTrue(
            any("functionalmlds_agent_ref" in error for error in report["errors"]),
            report["errors"],
        )

    def test_schema_valid_but_semantically_forged_chain_is_rejected_by_runtime_loader(self) -> None:
        with tempfile.TemporaryDirectory(prefix="schema-validator-runtime-chain-") as temp:
            case_dir, backend_root = self._materialize_test_case(Path(temp), dual=True)
            project_dir = backend_root / "projects" / CASE_ID
            trace = _read_json(project_dir / V2_VERSIONED_TRACE_FILENAME)
            trace["runtime_actions"][0]["provider_entity_id"] = next(
                item["id"]
                for item in self.v2["objects"]
                if item.get("type") == "Entity"
                and item["id"] != trace["runtime_actions"][0]["provider_entity_id"]
            )
            _write_json(project_dir / V2_VERSIONED_TRACE_FILENAME, trace)
            _write_json(project_dir / "trace_map.json", trace)
            report = validate_case_schemas(case_dir=case_dir, backend_root=backend_root)
        self.assertEqual("invalid", report["status"])
        self.assertTrue(
            any("shared runtime contract validation failed" in error for error in report["errors"]),
            report["errors"],
        )

    def test_canonical_v2_mutation_is_not_accepted_by_schema_only(self) -> None:
        with tempfile.TemporaryDirectory(prefix="schema-validator-canonical-") as temp:
            case_dir, backend_root = self._materialize_test_case(Path(temp), dual=True)
            project_dir = backend_root / "projects" / CASE_ID
            mutated = copy.deepcopy(self.v2)
            root = next(item for item in mutated["objects"] if item.get("type") == "DynamicFunctionalModel")
            root["requirementsModel"] = []
            v2_project = project_dir / V2_PROJECT_INSTANCE_FILENAME
            v2_source = case_dir / "functionalmlds" / V2_GENERATED_INSTANCE_FILENAME
            _write_json(v2_project, mutated)
            _write_json(v2_source, mutated)
            model_sha256 = _sha256(v2_project)
            trace = _read_json(project_dir / V2_VERSIONED_TRACE_FILENAME)
            trace["model_sha256"] = model_sha256
            _write_json(project_dir / V2_VERSIONED_TRACE_FILENAME, trace)
            _write_json(project_dir / "trace_map.json", trace)
            project = _read_json(project_dir / "project.json")
            project["functionalmlds_model_sha256"] = model_sha256
            _write_json(project_dir / "project.json", project)
            report = validate_case_schemas(case_dir=case_dir, backend_root=backend_root)
        self.assertEqual("invalid", report["status"])
        self.assertTrue(
            any("canonical IROOT" in error for error in report["errors"]),
            report["errors"],
        )


if __name__ == "__main__":
    unittest.main()
