from __future__ import annotations

import importlib
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


BACKEND_RELATIVE_ROOT = Path("InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents")
DEFAULT_OUTPUT_RELATIVE_ROOT = Path("output/wizard_functionalmlds")

STAGE_RUNNERS: Dict[str, Tuple[str, str]] = {
    "mlds_ingestion": ("mlds_ingestion", "run_ingestion_for_case"),
    "scene_semantics": ("scene_semantics", "run_scene_semantics_for_case"),
    "agent_roles": ("agent_roles", "run_agent_roles_for_case"),
    "knowledge_synthesis": ("knowledge_synthesis", "run_knowledge_synthesis_for_case"),
    "agent_placement": ("agent_placement", "run_agent_placement_for_case"),
    "functionalmlds_assembly": ("functionalmlds_assembler", "run_functionalmlds_assembly_for_case"),
    "handoff_derivation": ("handoff_derivation", "run_handoff_derivation_for_case"),
    "project_materialization": ("project_materializer", "run_project_materializer_for_case"),
    "schema_validation": ("validators.schema_validator", "run_schema_validation_for_case"),
    "functionalmlds_invariants": (
        "validators.functionalmlds_invariants",
        "run_functionalmlds_invariant_validation_for_case",
    ),
    "traceability_metrics": ("validators.traceability_metrics", "run_traceability_metrics_for_case"),
    "handoff_metrics": ("validators.handoff_metrics", "run_handoff_metrics_for_case"),
    "stage_completion": ("stage_completion", "run_stage_completion_for_case"),
}

ANALYZE_STAGE_IDS = (
    "mlds_ingestion",
    "scene_semantics",
    "agent_roles",
    "knowledge_synthesis",
    "agent_placement",
    "functionalmlds_assembly",
    "handoff_derivation",
    "functionalmlds_invariants",
)

ANALYZE_PREVIEW_ARTIFACTS = {
    "normalized_scene": "intermediate/scene_graph.normalized.json",
    "object_group_summary": "intermediate/object_group_summary.json",
    "scene_semantics": "intermediate/scene_semantics.json",
    "agent_roles": "intermediate/agent_roles.generated.json",
    "handoff_matrix": "intermediate/handoff_matrix.json",
    "knowledge": "intermediate/knowledge.generated.json",
    "agent_placements": "intermediate/agent_placements.json",
    "functionalmlds": "functionalmlds/functionalmlds.instance.generated.json",
    "functionalmlds_validation": "validation/functionalmlds_invariant_validation.json",
    "handoff_derivation_validation": "validation/handoff_derivation_validation.json",
    "functionalmlds_explicit_invariants": "validation/functionalmlds_invariants_validation.json",
}

ANALYZE_VALIDATION_ARTIFACTS = {
    "mlds_ingestion": "validation/mlds_ingestion_validation.json",
    "scene_semantics": "validation/scene_semantics_validation.json",
    "agent_roles": "validation/agent_roles_validation.json",
    "knowledge_synthesis": "validation/knowledge_synthesis_validation.json",
    "agent_placement": "validation/agent_placement_validation.json",
    "functionalmlds_assembly": "validation/functionalmlds_invariant_validation.json",
    "handoff_derivation": "validation/handoff_derivation_validation.json",
    "functionalmlds_invariants": "validation/functionalmlds_invariants_validation.json",
}

COMMIT_STAGE_IDS = (
    *ANALYZE_STAGE_IDS,
    "project_materialization",
    "schema_validation",
    "traceability_metrics",
    "handoff_metrics",
)

COMMIT_REQUIRED_ARTIFACTS = {
    **ANALYZE_PREVIEW_ARTIFACTS,
    "project_materialization_validation": "validation/project_materialization_validation.json",
    "schema_validation": "validation/schema_validation.json",
    "traceability_metrics": "validation/traceability_metrics.json",
    "handoff_metrics": "validation/handoff_metrics.json",
    "backend_project": "projects/{case_id}/project.json",
    "backend_room_plan": "projects/{case_id}/room_plan.json",
    "backend_agents": "projects/{case_id}/agents.json",
    "backend_trace_map": "projects/{case_id}/trace_map.json",
    "backend_kb_root": "projects/{case_id}/kb",
}

COMMIT_VALIDATION_ARTIFACTS = {
    **ANALYZE_VALIDATION_ARTIFACTS,
    "project_materialization": "validation/project_materialization_validation.json",
    "schema_validation": "validation/schema_validation.json",
    "traceability_metrics": "validation/traceability_metrics.json",
    "handoff_metrics": "validation/handoff_metrics.json",
}

DETERMINISTIC_FIRST_STAGE_SPECS = {
    "mlds_ingestion": {
        "inputs": ["input/source_mlds.json"],
        "outputs": [
            "intermediate/scene_graph.normalized.json",
            "intermediate/object_group_summary.json",
            "validation/mlds_ingestion_validation.json",
        ],
        "validation": "validation/mlds_ingestion_validation.json",
        "repair_type": "deterministic_normalization",
    },
    "scene_semantics": {
        "inputs": ["intermediate/scene_graph.normalized.json", "intermediate/object_group_summary.json"],
        "outputs": ["intermediate/scene_semantics.json", "validation/scene_semantics_validation.json"],
        "validation": "validation/scene_semantics_validation.json",
        "repair_type": "deterministic_recovery",
        "llm_stage": True,
    },
    "agent_roles": {
        "inputs": [
            "intermediate/scene_graph.normalized.json",
            "intermediate/object_group_summary.json",
            "intermediate/scene_semantics.json",
        ],
        "outputs": [
            "intermediate/agent_roles.generated.json",
            "intermediate/handoff_matrix.json",
            "validation/agent_roles_validation.json",
        ],
        "validation": "validation/agent_roles_validation.json",
        "repair_type": "deterministic_recovery",
        "llm_stage": True,
    },
    "knowledge_synthesis": {
        "inputs": [
            "intermediate/scene_graph.normalized.json",
            "intermediate/scene_semantics.json",
            "intermediate/agent_roles.generated.json",
        ],
        "outputs": [
            "intermediate/knowledge.generated.json",
            "validation/knowledge_synthesis_validation.json",
        ],
        "validation": "validation/knowledge_synthesis_validation.json",
        "repair_type": "deterministic_recovery",
        "llm_stage": True,
    },
    "agent_placement": {
        "inputs": [
            "intermediate/scene_graph.normalized.json",
            "intermediate/scene_semantics.json",
            "intermediate/agent_roles.generated.json",
        ],
        "outputs": ["intermediate/agent_placements.json", "validation/agent_placement_validation.json"],
        "validation": "validation/agent_placement_validation.json",
        "repair_type": "deterministic_geometry_recompute",
    },
    "functionalmlds_assembly": {
        "inputs": [
            "intermediate/scene_graph.normalized.json",
            "intermediate/scene_semantics.json",
            "intermediate/agent_roles.generated.json",
            "intermediate/agent_placements.json",
        ],
        "outputs": [
            "functionalmlds/functionalmlds.instance.generated.json",
            "validation/functionalmlds_invariant_validation.json",
        ],
        "validation": "validation/functionalmlds_invariant_validation.json",
        "repair_type": "deterministic_regeneration",
    },
    "handoff_derivation": {
        "inputs": [
            "intermediate/agent_roles.generated.json",
            "intermediate/handoff_matrix.json",
            "functionalmlds/functionalmlds.instance.generated.json",
        ],
        "outputs": [
            "intermediate/agent_roles.generated.json",
            "intermediate/handoff_matrix.json",
            "functionalmlds/functionalmlds.instance.generated.json",
            "validation/handoff_derivation_validation.json",
        ],
        "validation": "validation/handoff_derivation_validation.json",
        "repair_type": "deterministic_regeneration",
    },
    "functionalmlds_invariants": {
        "inputs": ["functionalmlds/functionalmlds.instance.generated.json"],
        "outputs": ["validation/functionalmlds_invariants_validation.json"],
        "validation": "validation/functionalmlds_invariants_validation.json",
        "repair_type": "deterministic_regeneration",
    },
    "project_materialization": {
        "inputs": [
            "input/source_mlds.json",
            "intermediate/agent_roles.generated.json",
            "intermediate/agent_placements.json",
            "intermediate/knowledge.generated.json",
            "functionalmlds/functionalmlds.instance.generated.json",
        ],
        "outputs": ["validation/project_materialization_validation.json"],
        "validation": "validation/project_materialization_validation.json",
        "repair_type": "deterministic_regeneration",
    },
    "schema_validation": {
        "inputs": ["functionalmlds/functionalmlds.instance.generated.json"],
        "outputs": ["validation/schema_validation.json"],
        "validation": "validation/schema_validation.json",
        "repair_type": "deterministic_regeneration",
    },
    "traceability_metrics": {
        "inputs": ["functionalmlds/functionalmlds.instance.generated.json"],
        "outputs": ["validation/traceability_metrics.json"],
        "validation": "validation/traceability_metrics.json",
        "repair_type": "deterministic_regeneration",
    },
    "handoff_metrics": {
        "inputs": [
            "intermediate/agent_roles.generated.json",
            "intermediate/handoff_matrix.json",
            "functionalmlds/functionalmlds.instance.generated.json",
        ],
        "outputs": ["validation/handoff_metrics.json"],
        "validation": "validation/handoff_metrics.json",
        "repair_type": "deterministic_regeneration",
    },
}


@dataclass(frozen=True)
class FunctionalMldsAdapterPaths:
    workspace_root: Path
    backend_root: Path
    pipeline_root: Path
    output_root: Path


@dataclass
class FunctionalMldsAdapter:
    paths: FunctionalMldsAdapterPaths

    @classmethod
    def discover(
        cls,
        *,
        workspace_root: Optional[Path] = None,
        backend_root: Optional[Path] = None,
        output_root: Optional[Path] = None,
    ) -> "FunctionalMldsAdapter":
        workspace = workspace_root.resolve() if workspace_root else find_workspace_root()
        backend = backend_root.resolve() if backend_root else (workspace / BACKEND_RELATIVE_ROOT).resolve()
        pipeline = (workspace / "tools" / "case_study_pipeline").resolve()
        output = output_root.resolve() if output_root else (workspace / DEFAULT_OUTPUT_RELATIVE_ROOT).resolve()

        if not backend.exists():
            raise FileNotFoundError(f"Backend root nicht gefunden: {backend}")
        if not pipeline.exists():
            raise FileNotFoundError(f"FunctionalMLDS-Pipeline nicht gefunden: {pipeline}")

        return cls(
            FunctionalMldsAdapterPaths(
                workspace_root=workspace,
                backend_root=backend,
                pipeline_root=pipeline,
                output_root=output,
            )
        )

    def ensure_pipeline_importable(self) -> None:
        workspace = str(self.paths.workspace_root)
        if workspace not in sys.path:
            sys.path.insert(0, workspace)

    def import_pipeline_module(self, module_name: str):
        self.ensure_pipeline_importable()
        return importlib.import_module(f"tools.case_study_pipeline.{module_name}")

    def validate_environment(self) -> Dict[str, str]:
        self.ensure_pipeline_importable()
        ingestion = self.import_pipeline_module("mlds_ingestion")
        if not hasattr(ingestion, "initialize_case") or not hasattr(ingestion, "run_ingestion_for_case"):
            raise RuntimeError("mlds_ingestion stellt die erwarteten Funktionen nicht bereit.")
        return {
            "workspace_root": str(self.paths.workspace_root),
            "backend_root": str(self.paths.backend_root),
            "pipeline_root": str(self.paths.pipeline_root),
            "output_root": str(self.paths.output_root),
        }

    def analyze_stage_plan(self) -> Dict[str, Any]:
        return {
            "stages": list(ANALYZE_STAGE_IDS),
            "artifacts": dict(ANALYZE_PREVIEW_ARTIFACTS),
            "validations": dict(ANALYZE_VALIDATION_ARTIFACTS),
            "materializes_backend_project": False,
            "requires_llm": True,
            "stops_before_commit": True,
            "requires_valid_analyze_gate": True,
        }

    def commit_stage_plan(self, *, case_id: str = "{case_id}") -> Dict[str, Any]:
        safe_case_id = require_safe_case_id(case_id) if case_id != "{case_id}" else case_id
        artifacts = {
            key: value.format(case_id=safe_case_id)
            for key, value in COMMIT_REQUIRED_ARTIFACTS.items()
        }
        return {
            "stages": list(COMMIT_STAGE_IDS),
            "artifacts": artifacts,
            "validations": dict(COMMIT_VALIDATION_ARTIFACTS),
            "materializes_backend_project": True,
            "requires_llm": True,
            "requires_valid_materialization": True,
            "minimum_blocking_validations": [
                "functionalmlds_invariants",
                "project_materialization",
                "schema_validation",
            ],
            "required_metric_reports": [
                "traceability_metrics",
                "handoff_metrics",
            ],
        }

    def initialize_case_from_payload(self, payload: Dict[str, Any], *, case_id: str) -> Dict[str, str]:
        if not isinstance(payload, dict):
            raise ValueError("MLDS-Payload muss ein Objekt sein.")
        safe_case_id = require_safe_case_id(case_id)
        self.ensure_case_can_be_written(payload, safe_case_id)
        source_path = self.write_source_payload(payload, safe_case_id)
        ingestion = self.import_pipeline_module("mlds_ingestion")
        initialized = ingestion.initialize_case(source_path, self.paths.output_root, safe_case_id)
        return {
            "case_id": safe_case_id,
            "source_path": str(source_path),
            "case_dir": str(initialized["case_dir"]),
            "source_copy": str(initialized["source_copy"]),
            "hash_path": str(initialized["hash_path"]),
        }

    def write_source_payload(self, payload: Dict[str, Any], case_id: str) -> Path:
        safe_case_id = require_safe_case_id(case_id)
        source_path = self.paths.output_root / "_wizard_inputs" / f"{safe_case_id}.source_mlds.json"
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return source_path

    def derive_case_id(
        self,
        payload: Dict[str, Any],
        *,
        project_id_hint: str = "",
        display_name: str = "",
        include_hash: bool = True,
    ) -> str:
        return derive_case_id(
            payload,
            project_id_hint=project_id_hint,
            display_name=display_name,
            include_hash=include_hash,
        )

    def ensure_case_can_be_written(self, payload: Dict[str, Any], case_id: str, *, allow_overwrite: bool = False) -> None:
        safe_case_id = require_safe_case_id(case_id)
        case_dir = self.paths.output_root / safe_case_id
        if allow_overwrite or not case_dir.exists():
            return

        new_hash = payload_hash(payload)
        existing_source_path = case_dir / "input" / "source_mlds.json"
        if existing_source_path.exists():
            existing_payload = json.loads(existing_source_path.read_text(encoding="utf-8"))
            if payload_hash(existing_payload) == new_hash:
                return
            raise FileExistsError(
                f"Case-Verzeichnis existiert bereits mit anderem MLDS-Payload: {case_dir}. "
                "Bitte andere Projekt-ID waehlen oder bewusstes Ueberschreiben implementieren."
            )

        existing_hash_path = case_dir / "input" / "source_mlds.sha256"
        if existing_hash_path.exists():
            raise FileExistsError(
                f"Case-Verzeichnis existiert bereits, aber source_mlds.json fehlt: {case_dir}. "
                "Bitte andere Projekt-ID waehlen oder bewusstes Ueberschreiben implementieren."
            )

        if any(case_dir.iterdir()):
            raise FileExistsError(
                f"Case-Verzeichnis existiert bereits und besitzt keinen vergleichbaren Source-Hash: {case_dir}."
            )

    def run_stage(self, case_dir: Path, stage_id: str, **kwargs: Any) -> Dict[str, Any]:
        if stage_id not in STAGE_RUNNERS:
            allowed = ", ".join(sorted(STAGE_RUNNERS))
            raise ValueError(f"Unbekannte FunctionalMLDS-Stage: {stage_id}. Erlaubt: {allowed}.")

        module_name, function_name = STAGE_RUNNERS[stage_id]
        module = self.import_pipeline_module(module_name)
        runner = getattr(module, function_name)
        case_path = Path(case_dir).resolve()

        if stage_id in {"project_materialization", "schema_validation"}:
            kwargs.setdefault("backend_root", self.paths.backend_root)
        return runner(case_path, **kwargs)

    def run_stage_deterministic_first(self, case_dir: Path, stage_id: str, **kwargs: Any) -> Dict[str, Any]:
        case_path = Path(case_dir).resolve()
        recovered = self.try_deterministic_recovery(case_path, stage_id)
        if recovered is not None:
            self.write_repair_log(case_path)
            return recovered
        result = self.run_stage(case_path, stage_id, **kwargs)
        self.write_repair_log(case_path)
        return result

    def try_deterministic_recovery(self, case_dir: Path, stage_id: str) -> Optional[Dict[str, Any]]:
        spec = DETERMINISTIC_FIRST_STAGE_SPECS.get(stage_id)
        if not spec:
            return None
        case_path = Path(case_dir).resolve()
        validation_path = case_path / str(spec["validation"])
        if not self._validation_is_valid(validation_path):
            return None

        self._repair_deterministic_derived_outputs(case_path, stage_id)
        output_paths = self._stage_output_paths(case_path, stage_id, spec)
        if not output_paths or not all(path.exists() for path in output_paths):
            return None

        validation = self._read_json_if_exists(validation_path)
        common = self.import_pipeline_module("common")
        common.update_manifest(
            case_path,
            stage_id=stage_id,
            status="success",
            input_paths=[case_path / str(path) for path in spec.get("inputs", [])],
            output_paths=output_paths,
            errors=validation.get("errors"),
            warnings=validation.get("warnings"),
            metadata={
                "recovered_without_rerun": True,
                "recovered_without_llm": bool(spec.get("llm_stage")),
                "repair_type": spec.get("repair_type"),
                "llm_used": False,
                "attempts_used": 0,
                "metrics": validation.get("metrics", {}),
            },
        )
        return {
            "case_id": case_path.name,
            "status": "success",
            "validation": validation,
            "validation_path": str(validation_path),
            "deterministic_recovery": True,
            "llm_used": False,
        }

    def write_repair_log(self, case_dir: Path) -> Dict[str, Any]:
        repair_log = self.import_pipeline_module("repair_log")
        return repair_log.write_repair_log_for_case(Path(case_dir).resolve())

    def _repair_deterministic_derived_outputs(self, case_dir: Path, stage_id: str) -> None:
        if stage_id != "knowledge_synthesis":
            return
        knowledge_path = case_dir / "intermediate" / "knowledge.generated.json"
        if not knowledge_path.exists():
            return
        knowledge_module = self.import_pipeline_module("knowledge_synthesis")
        knowledge = self._read_json_if_exists(knowledge_path)
        knowledge_module.materialize_knowledge_files(case_dir, knowledge)

    def _stage_output_paths(self, case_dir: Path, stage_id: str, spec: Dict[str, Any]) -> List[Path]:
        paths = [case_dir / str(path) for path in spec.get("outputs", [])]
        if stage_id == "knowledge_synthesis":
            kb_root = case_dir / "interactive_agents_project" / "kb"
            if not kb_root.exists() or not list(kb_root.rglob("*.txt")):
                return []
            paths.append(kb_root)
        if stage_id == "project_materialization":
            project_dir = self.paths.backend_root / "projects" / case_dir.name
            paths.extend(
                [
                    project_dir / "project.json",
                    project_dir / "room_plan.json",
                    project_dir / "agents.json",
                    project_dir / "trace_map.json",
                    project_dir / "kb",
                ]
            )
        return paths

    @staticmethod
    def _validation_is_valid(path: Path) -> bool:
        try:
            return json.loads(path.read_text(encoding="utf-8-sig")).get("status") == "valid"
        except Exception:
            return False

    @staticmethod
    def _read_json_if_exists(path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return {}

    def validate_analyze_case(self, case_dir: Path) -> Dict[str, Any]:
        case_path = Path(case_dir).resolve()
        errors = []
        warnings = []
        artifacts: Dict[str, Dict[str, Any]] = {}
        validations: Dict[str, Dict[str, Any]] = {}

        for artifact_id, relative_path in ANALYZE_PREVIEW_ARTIFACTS.items():
            path = case_path / relative_path
            artifact_report = {
                "path": str(path),
                "exists": path.exists(),
                "json_status": "missing",
            }
            if not path.exists():
                errors.append(f"Analyze-Artefakt fehlt: {artifact_id} ({relative_path})")
            else:
                try:
                    json.loads(path.read_text(encoding="utf-8-sig"))
                    artifact_report["json_status"] = "valid"
                except Exception as exc:
                    artifact_report["json_status"] = "invalid"
                    errors.append(f"Analyze-Artefakt ist kein gueltiges JSON: {artifact_id} ({exc})")
            artifacts[artifact_id] = artifact_report

        for validation_id, relative_path in ANALYZE_VALIDATION_ARTIFACTS.items():
            path = case_path / relative_path
            validation_report = {
                "path": str(path),
                "exists": path.exists(),
                "status": "missing",
                "error_count": 0,
                "warning_count": 0,
                "errors": [],
                "warnings": [],
            }
            if not path.exists():
                errors.append(f"Analyze-Validierung fehlt: {validation_id} ({relative_path})")
                validations[validation_id] = validation_report
                continue

            try:
                payload = json.loads(path.read_text(encoding="utf-8-sig"))
            except Exception as exc:
                validation_report["status"] = "invalid_json"
                validation_report["errors"] = [str(exc)]
                validation_report["error_count"] = 1
                errors.append(f"Analyze-Validierung ist kein gueltiges JSON: {validation_id} ({exc})")
                validations[validation_id] = validation_report
                continue

            report_errors = list(payload.get("errors") or [])
            report_warnings = list(payload.get("warnings") or [])
            status = str(payload.get("status") or "").strip().lower()
            validation_report.update(
                {
                    "status": status or "missing_status",
                    "error_count": len(report_errors),
                    "warning_count": len(report_warnings),
                    "errors": report_errors,
                    "warnings": report_warnings,
                    "metrics": payload.get("metrics") or {},
                }
            )
            warnings.extend(f"{validation_id}: {warning}" for warning in report_warnings)
            if status != "valid":
                errors.append(
                    f"Analyze-Validierung ist nicht valid: {validation_id} "
                    f"(status={status or 'missing'}, errors={len(report_errors)})"
                )
                errors.extend(f"{validation_id}: {error}" for error in report_errors)
            validations[validation_id] = validation_report

        return {
            "status": "valid" if not errors else "invalid",
            "case_id": case_path.name,
            "case_dir": str(case_path),
            "errors": errors,
            "warnings": warnings,
            "artifacts": artifacts,
            "validations": validations,
            "metrics": {
                "artifact_count": len(artifacts),
                "valid_artifact_count": len(
                    [item for item in artifacts.values() if item.get("json_status") == "valid"]
                ),
                "validation_count": len(validations),
                "valid_validation_count": len(
                    [item for item in validations.values() if item.get("status") == "valid"]
                ),
            },
        }

    def summarize_analyze_validation(self, report: Dict[str, Any]) -> Dict[str, Any]:
        validations = report.get("validations") or {}
        pre_model_status = combined_validation_status(
            validations,
            (
                "mlds_ingestion",
                "scene_semantics",
                "agent_roles",
                "knowledge_synthesis",
                "agent_placement",
            ),
        )
        invariant_status = combined_validation_status(
            validations,
            ("functionalmlds_assembly", "functionalmlds_invariants"),
        )
        handoff_status = combined_validation_status(validations, ("handoff_derivation",))
        errors = list(report.get("errors") or [])
        warnings = list(report.get("warnings") or [])
        return {
            "status": report.get("status") or "invalid",
            "schema_status": pre_model_status,
            "invariant_status": invariant_status,
            "materialization_status": "not_run",
            "traceability_status": "not_run",
            "handoff_status": handoff_status,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "traceability_average_coverage": 0.0,
            "handoff_decision_accuracy": 0.0,
            "errors": errors,
            "warnings": warnings,
        }

    def validate_commit_case(self, case_dir: Path) -> Dict[str, Any]:
        case_path = Path(case_dir).resolve()
        errors = []
        warnings = []
        artifacts: Dict[str, Dict[str, Any]] = {}
        validations: Dict[str, Dict[str, Any]] = {}

        for artifact_id, relative_path in self.commit_stage_plan(case_id=case_path.name)["artifacts"].items():
            path = self._resolve_commit_artifact_path(case_path, relative_path)
            artifact_report = {
                "path": str(path),
                "exists": path.exists(),
                "kind": "directory" if path.exists() and path.is_dir() else "file",
                "json_status": "not_json",
            }
            if not path.exists():
                errors.append(f"Commit-Artefakt fehlt: {artifact_id} ({relative_path})")
            elif path.is_file() and path.suffix.lower() == ".json":
                try:
                    json.loads(path.read_text(encoding="utf-8-sig"))
                    artifact_report["json_status"] = "valid"
                except Exception as exc:
                    artifact_report["json_status"] = "invalid"
                    errors.append(f"Commit-Artefakt ist kein gueltiges JSON: {artifact_id} ({exc})")
            artifacts[artifact_id] = artifact_report

        for validation_id, relative_path in COMMIT_VALIDATION_ARTIFACTS.items():
            path = case_path / relative_path
            validation_report = self._read_validation_report(path)
            if not validation_report["exists"]:
                errors.append(f"Commit-Validierung fehlt: {validation_id} ({relative_path})")
            elif validation_report["status"] != "valid":
                errors.append(
                    f"Commit-Validierung ist nicht valid: {validation_id} "
                    f"(status={validation_report['status']}, errors={validation_report['error_count']})"
                )
                errors.extend(f"{validation_id}: {error}" for error in validation_report["errors"])
            warnings.extend(f"{validation_id}: {warning}" for warning in validation_report["warnings"])
            validations[validation_id] = validation_report

        return {
            "status": "valid" if not errors else "invalid",
            "case_id": case_path.name,
            "case_dir": str(case_path),
            "errors": errors,
            "warnings": warnings,
            "artifacts": artifacts,
            "validations": validations,
            "metrics": {
                "artifact_count": len(artifacts),
                "present_artifact_count": len(
                    [item for item in artifacts.values() if item.get("exists")]
                ),
                "validation_count": len(validations),
                "valid_validation_count": len(
                    [item for item in validations.values() if item.get("status") == "valid"]
                ),
            },
        }

    def summarize_commit_validation(self, report: Dict[str, Any]) -> Dict[str, Any]:
        validations = report.get("validations") or {}
        schema_status = combined_validation_status(
            validations,
            (
                "mlds_ingestion",
                "scene_semantics",
                "agent_roles",
                "knowledge_synthesis",
                "agent_placement",
                "schema_validation",
            ),
        )
        invariant_status = combined_validation_status(
            validations,
            ("functionalmlds_assembly", "functionalmlds_invariants"),
        )
        materialization_status = combined_validation_status(validations, ("project_materialization",))
        traceability_status = combined_validation_status(validations, ("traceability_metrics",))
        handoff_status = combined_validation_status(validations, ("handoff_derivation", "handoff_metrics"))
        errors = list(report.get("errors") or [])
        warnings = list(report.get("warnings") or [])
        trace_metrics = (validations.get("traceability_metrics") or {}).get("metrics") or {}
        handoff_metrics = (validations.get("handoff_metrics") or {}).get("metrics") or {}
        return {
            "status": report.get("status") or "invalid",
            "schema_status": schema_status,
            "invariant_status": invariant_status,
            "materialization_status": materialization_status,
            "traceability_status": traceability_status,
            "handoff_status": handoff_status,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "traceability_average_coverage": float(trace_metrics.get("average_coverage") or 0.0),
            "handoff_decision_accuracy": float(handoff_metrics.get("handoff_decision_accuracy") or 0.0),
            "errors": errors,
            "warnings": warnings,
        }

    def _resolve_commit_artifact_path(self, case_dir: Path, relative_path: str) -> Path:
        if relative_path.startswith("projects/"):
            return self.paths.backend_root / relative_path
        return case_dir / relative_path

    @staticmethod
    def _read_validation_report(path: Path) -> Dict[str, Any]:
        report = {
            "path": str(path),
            "exists": path.exists(),
            "status": "missing",
            "error_count": 0,
            "warning_count": 0,
            "errors": [],
            "warnings": [],
            "metrics": {},
        }
        if not path.exists():
            return report
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            report.update(
                {
                    "status": "invalid_json",
                    "error_count": 1,
                    "errors": [str(exc)],
                }
            )
            return report
        errors = list(payload.get("errors") or [])
        warnings = list(payload.get("warnings") or [])
        report.update(
            {
                "status": str(payload.get("status") or "missing_status").strip().lower(),
                "error_count": len(errors),
                "warning_count": len(warnings),
                "errors": errors,
                "warnings": warnings,
                "metrics": payload.get("metrics") or {},
            }
        )
        return report

    def run_ingestion_from_payload(self, payload: Dict[str, Any], *, case_id: str) -> Dict[str, Any]:
        initialized = self.initialize_case_from_payload(payload, case_id=case_id)
        result = self.run_stage(Path(initialized["case_dir"]), "mlds_ingestion")
        return {
            "case_id": initialized["case_id"],
            "case_dir": initialized["case_dir"],
            "source_path": initialized["source_path"],
            "ingestion": result,
        }


def find_workspace_root(start: Optional[Path] = None) -> Path:
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if (candidate / "tools" / "case_study_pipeline").is_dir() and (candidate / BACKEND_RELATIVE_ROOT).is_dir():
            return candidate
    raise FileNotFoundError("Workspace-Root mit tools/case_study_pipeline und InteractiveAgents-Backend nicht gefunden.")


def require_safe_case_id(case_id: str) -> str:
    value = str(case_id or "").strip()
    if not value:
        raise ValueError("case_id fehlt.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
        raise ValueError("case_id darf nur Buchstaben, Zahlen, Punkt, Unterstrich und Bindestrich enthalten.")
    if ".." in value:
        raise ValueError("case_id darf keine '..'-Sequenz enthalten.")
    return value


def derive_case_id(
    payload: Dict[str, Any],
    *,
    project_id_hint: str = "",
    display_name: str = "",
    include_hash: bool = True,
) -> str:
    if not isinstance(payload, dict):
        raise ValueError("MLDS-Payload muss ein Objekt sein.")

    explicit = ascii_slug(project_id_hint, fallback="")
    if explicit:
        return require_safe_case_id(explicit)

    source_name = first_non_empty(
        display_name,
        nested_string(payload, "project", "display_name"),
        nested_string(payload, "project", "name"),
        nested_string(payload, "metadata", "display_name"),
        nested_string(payload, "metadata", "name"),
        nested_string(payload, "scene", "sceneName"),
        nested_string(payload, "scene", "name"),
        nested_string(payload, "scene", "displayName"),
        nested_string(payload, "sceneName"),
        nested_string(payload, "name"),
        nested_string(payload, "id"),
        "functional_mlds_case",
    )
    base = ascii_slug(source_name, fallback="functional_mlds_case")
    if include_hash:
        base = f"{base}_{payload_hash(payload)[:8]}"
    return require_safe_case_id(base)


def payload_hash(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(canonical_payload_text(payload).encode("utf-8")).hexdigest()


def canonical_payload_text(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def first_non_empty(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def nested_string(payload: Dict[str, Any], *path: str) -> str:
    value: Any = payload
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return ""
        value = value[key]
    if isinstance(value, (dict, list)):
        return ""
    return str(value or "").strip()


def ascii_slug(value: str, fallback: str = "case") -> str:
    text = str(value or "")
    for source, replacement in {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "Ä": "Ae",
        "Ö": "Oe",
        "Ü": "Ue",
        "ß": "ss",
        "ẞ": "SS",
    }.items():
        text = text.replace(source, replacement)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9_-]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or fallback


def combined_validation_status(validations: Dict[str, Any], validation_ids: Tuple[str, ...]) -> str:
    statuses = []
    for validation_id in validation_ids:
        validation = validations.get(validation_id)
        if not isinstance(validation, dict):
            statuses.append("missing")
            continue
        statuses.append(str(validation.get("status") or "missing").strip().lower())
    if not statuses:
        return "not_run"
    if all(status == "valid" for status in statuses):
        return "valid"
    if any(status in {"invalid", "invalid_json", "missing", "missing_status"} for status in statuses):
        return "invalid"
    return statuses[0]
