from __future__ import annotations

import copy
import json
import math
import re
import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import Any, Dict
from unittest import mock

import backend
from backend.functionalmlds_adapter import FunctionalMldsAdapter
from backend.kb import KnowledgeBase
from backend.projects import ProjectManager
from backend.state import (
    ArrowProjectDraft,
    GENERATION_MODE_FUNCTIONALMLDS,
    GENERATION_MODE_LEGACY,
    SessionStore,
)
from backend.version import API_VERSION, BACKEND_VERSION, backend_version_payload


class BackendVersionAndPlacementTest(unittest.TestCase):
    def test_backend_version_has_one_semver_source(self) -> None:
        self.assertEqual("1.0.0", BACKEND_VERSION)
        self.assertEqual("1.0", API_VERSION)
        self.assertEqual(BACKEND_VERSION, backend.__version__)
        self.assertRegex(BACKEND_VERSION, re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"))
        self.assertEqual(
            {
                "status": "ok",
                "backend_version": BACKEND_VERSION,
                "api_version": API_VERSION,
            },
            backend_version_payload(),
        )

    def test_legacy_placement_validation_is_exact_and_non_mutating_on_error(self) -> None:
        with tempfile.TemporaryDirectory(prefix="backend_placement_validation_") as tmp:
            store = self._store(Path(tmp))
            session = self._legacy_session()
            store.arrow_sessions[session.session_id] = session

            valid = self._valid_request(session)
            invalid_requests = (
                valid[:-1],
                [*valid, {**copy.deepcopy(valid[0]), "id": "unexpected_agent"}],
                [
                    {**copy.deepcopy(valid[0]), "position": {"x": math.nan, "y": 0.0, "z": 0.0}},
                    copy.deepcopy(valid[0]),
                ],
                [
                    {**copy.deepcopy(valid[0]), "forward": {"x": 1.0, "y": 0.1, "z": 0.0}},
                    copy.deepcopy(valid[1]),
                ],
                [
                    {**copy.deepcopy(valid[0]), "position": {"x": -1.0, "y": 0.1, "z": 0.0}},
                    copy.deepcopy(valid[1]),
                ],
                [
                    {**copy.deepcopy(valid[0]), "forward": {"x": 2.0, "y": 0.0, "z": 0.0}},
                    copy.deepcopy(valid[1]),
                ],
                [
                    {**copy.deepcopy(valid[0]), "position": {"x": math.inf, "y": 0.0, "z": 0.0}},
                    copy.deepcopy(valid[1]),
                ],
            )

            for index, placements in enumerate(invalid_requests):
                before = copy.deepcopy(session)
                with self.subTest(invalid_request=index):
                    result = store.update_arrow_placement(
                        {
                            "session_id": session.session_id,
                            "generation_mode": GENERATION_MODE_LEGACY,
                            "agent_placements": placements,
                        }
                    )
                    self.assertEqual("invalid", result["status"])
                    self.assertEqual("invalid", result["validation"]["status"])
                    self.assertFalse(result["mutation_applied"])
                    self.assertTrue(result["validation"]["errors"])
                    self.assertEqual(before, session)

    def test_valid_legacy_update_preserves_exact_vectors(self) -> None:
        with tempfile.TemporaryDirectory(prefix="backend_legacy_placement_") as tmp:
            root = Path(tmp)
            store = self._store(root)
            session = self._legacy_session()
            session.arrow_payload = {
                "objects": [
                    {
                        "id": "manual_position_obstacle",
                        "position": {"x": -2.25, "y": 0.0, "z": 1.125},
                        "dimensions": {"x": 1.0, "y": 1.0, "z": 1.0},
                    }
                ]
            }
            store.arrow_sessions[session.session_id] = session
            requested = self._valid_request(session)
            requested[0]["position"] = {"x": -2.25, "y": 0.0, "z": 1.125}
            requested[0]["forward"] = {"x": 0.6, "y": 0.0, "z": 0.8}

            result = store.update_arrow_placement(
                {
                    "session_id": session.session_id,
                    "agent_placements": requested,
                }
            )

            self.assertEqual("ok", result["status"])
            self.assertEqual("valid", result["validation"]["status"])
            self.assertTrue(result["mutation_applied"])
            actual = self._compact_placements(session.placement_preview)
            self.assertEqual(requested, actual)

            committed = store.commit_arrow_project(
                {
                    "session_id": session.session_id,
                    "project_id": "manual_legacy_placement",
                    "display_name": "Manual Legacy Placement",
                }
            )
            self.assertEqual("ok", committed["status"])
            saved_agents = self._read_json(
                root / "projects" / "manual_legacy_placement" / "agents.json"
            )["agents"]
            saved_by_id = {item["id"]: item for item in saved_agents}
            for placement in requested:
                saved = saved_by_id[placement["id"]]
                self.assertEqual(placement["position"], saved["position"])
                self.assertEqual(placement["forward"], saved["forward"])

    def test_parallel_session_and_case_mutations_are_serialized(self) -> None:
        with tempfile.TemporaryDirectory(prefix="backend_placement_locking_") as tmp:
            store = self._store(Path(tmp))
            session = self._legacy_session()
            store.arrow_sessions[session.session_id] = session
            requested = self._valid_request(session)

            session_probe = self._install_concurrency_probe(
                store,
                "_update_arrow_placement_unlocked",
            )
            session_results, session_errors = self._run_parallel_barrier(
                lambda: store.update_arrow_placement(
                    {
                        "session_id": session.session_id,
                        "agent_placements": copy.deepcopy(requested),
                    }
                )
            )
            self.assertEqual([], session_errors)
            self.assertEqual(2, len(session_results))
            self.assertTrue(all(item.get("status") == "ok" for item in session_results))
            self.assertEqual(1, session_probe["max_active"])

            case_probe = self._install_concurrency_probe(
                store,
                "_analyze_arrow_unlocked",
                result_factory=lambda: {"session_id": "probe", "draft": {}},
            )
            case_results, case_errors = self._run_parallel_barrier(
                lambda: store.analyze_arrow(
                    {
                        "generation_mode": "legacy",
                        "project_id_hint": "shared_lock_case",
                        "arrow_json": {"scene": {"objects": []}},
                    }
                )
            )
            self.assertEqual([], case_errors)
            self.assertEqual(2, len(case_results))
            self.assertEqual(1, case_probe["max_active"])

    def test_functionalmlds_geometry_rejection_does_not_mutate_files_or_session(self) -> None:
        with tempfile.TemporaryDirectory(prefix="backend_functionalmlds_geometry_") as tmp:
            fixture = self._functional_fixture(Path(tmp))
            store = fixture["store"]
            session = fixture["session"]
            adapter = fixture["adapter"]
            case_dir = fixture["case_dir"]
            requested = self._valid_request(session)
            requested[0]["position"] = {"x": 100000.0, "y": 0.0, "z": 100000.0}
            session_before = copy.deepcopy(session)
            files_before = self._file_snapshot(
                SessionStore._functionalmlds_placement_transaction_paths(case_dir)
            )

            with mock.patch(
                "backend.state.FunctionalMldsAdapter.discover",
                return_value=adapter,
            ):
                result = store.update_arrow_placement(
                    {
                        "session_id": session.session_id,
                        "generation_mode": GENERATION_MODE_FUNCTIONALMLDS,
                        "agent_placements": requested,
                    }
                )

            self.assertEqual("invalid", result["status"])
            self.assertEqual("invalid", result["validation"]["status"])
            self.assertFalse(result["mutation_applied"])
            self.assertTrue(result["validation"]["errors"])
            self.assertEqual(session_before, session)
            self.assertEqual(
                files_before,
                self._file_snapshot(SessionStore._functionalmlds_placement_transaction_paths(case_dir)),
            )

    def test_functionalmlds_downstream_failure_rolls_back_every_file_and_session(self) -> None:
        with tempfile.TemporaryDirectory(prefix="backend_functionalmlds_rollback_") as tmp:
            fixture = self._functional_fixture(Path(tmp))
            store = fixture["store"]
            session = fixture["session"]
            adapter = fixture["adapter"]
            case_dir = fixture["case_dir"]
            requested = self._valid_request(session)
            requested[0]["forward"] = {"x": 1.0, "y": 0.0, "z": 0.0}
            requested[1]["forward"] = {"x": -1.0, "y": 0.0, "z": 0.0}

            transaction_paths = SessionStore._functionalmlds_placement_transaction_paths(case_dir)
            files_before = self._file_snapshot(transaction_paths)
            session_before = copy.deepcopy(session)
            regenerated = case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"

            def fail_after_partial_regeneration(*_: Any, **__: Any) -> Dict[str, Any]:
                regenerated.write_text('{"partially_regenerated":true}\n', encoding="utf-8")
                raise RuntimeError("forced downstream failure")

            with (
                mock.patch(
                    "backend.state.FunctionalMldsAdapter.discover",
                    return_value=adapter,
                ),
                mock.patch.object(adapter, "run_stage", side_effect=fail_after_partial_regeneration) as run_stage,
            ):
                result = store.update_arrow_placement(
                    {
                        "session_id": session.session_id,
                        "generation_mode": GENERATION_MODE_FUNCTIONALMLDS,
                        "agent_placements": requested,
                    }
                )

            self.assertEqual(1, run_stage.call_count, result)
            self.assertEqual("invalid", result["status"])
            self.assertEqual("invalid", result["validation"]["status"])
            self.assertFalse(result["mutation_applied"])
            self.assertIn("zur", result["validation"]["errors"][0].lower())
            self.assertIn("forced downstream failure", result["validation"]["errors"][0])
            self.assertEqual(session_before, session)
            self.assertEqual(files_before, self._file_snapshot(transaction_paths))
            self.assertEqual([], list(case_dir.rglob(".*.tmp")))
            self.assertEqual([], list(case_dir.rglob(".*.restore")))

    def test_functionalmlds_failure_after_metrics_regeneration_restores_metrics(self) -> None:
        with tempfile.TemporaryDirectory(prefix="backend_functionalmlds_metrics_rollback_") as tmp:
            fixture = self._functional_fixture(Path(tmp))
            store = fixture["store"]
            session = fixture["session"]
            adapter = fixture["adapter"]
            case_dir = fixture["case_dir"]
            requested = self._valid_request(session)
            reversed_positions = [
                copy.deepcopy(item["position"])
                for item in reversed(requested)
            ]
            for index, placement in enumerate(requested):
                placement["position"] = reversed_positions[index]

            transaction_paths = SessionStore._functionalmlds_placement_transaction_paths(case_dir)
            metrics_path = case_dir / "validation" / "placement_metrics.json"
            self.assertIn(metrics_path, transaction_paths)
            files_before = self._file_snapshot(transaction_paths)
            session_before = copy.deepcopy(session)
            original_run_stage = adapter.run_stage
            observed: Dict[str, bytes] = {}

            def run_with_real_metrics(
                stage_case_dir: Path,
                stage_id: str,
                **kwargs: Any,
            ) -> Dict[str, Any]:
                if stage_id == "placement_metrics":
                    return original_run_stage(stage_case_dir, stage_id, **kwargs)
                return {"status": "success"}

            def fail_after_metrics(_: Path) -> Dict[str, Any]:
                observed["metrics"] = metrics_path.read_bytes()
                raise RuntimeError("forced failure after placement metrics")

            with (
                mock.patch(
                    "backend.state.FunctionalMldsAdapter.discover",
                    return_value=adapter,
                ),
                mock.patch.object(
                    adapter,
                    "run_stage",
                    side_effect=run_with_real_metrics,
                ),
                mock.patch.object(
                    adapter,
                    "validate_analyze_case",
                    side_effect=fail_after_metrics,
                ),
            ):
                result = store.update_arrow_placement(
                    {
                        "session_id": session.session_id,
                        "generation_mode": GENERATION_MODE_FUNCTIONALMLDS,
                        "agent_placements": requested,
                    }
                )

            self.assertEqual("invalid", result["status"])
            self.assertIn("forced failure after placement metrics", result["validation"]["errors"][0])
            self.assertNotEqual(files_before[str(metrics_path)], observed.get("metrics"))
            self.assertEqual(session_before, session)
            self.assertEqual(files_before, self._file_snapshot(transaction_paths))

    def test_functionalmlds_commit_rejects_post_analyze_placement_tampering(self) -> None:
        with tempfile.TemporaryDirectory(prefix="backend_functionalmlds_commit_guard_") as tmp:
            fixture = self._functional_fixture(Path(tmp))
            store = fixture["store"]
            session = fixture["session"]
            adapter = fixture["adapter"]
            case_dir = fixture["case_dir"]
            placements_path = case_dir / "intermediate" / "agent_placements.json"
            placements = self._read_json(placements_path)
            placements["agent_placements"][0]["position"]["x"] = 100000.0
            placements_path.write_text(
                json.dumps(placements, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            executed_stages: list[str] = []

            def record_stage(_: Path, stage_id: str, **__: Any) -> Dict[str, Any]:
                executed_stages.append(stage_id)
                return {"status": "success"}

            with (
                mock.patch(
                    "backend.state.FunctionalMldsAdapter.discover",
                    return_value=adapter,
                ),
                mock.patch.object(
                    adapter,
                    "run_stage_deterministic_first",
                    side_effect=record_stage,
                ),
            ):
                result = store.commit_arrow_project(
                    {
                        "session_id": session.session_id,
                        "generation_mode": GENERATION_MODE_FUNCTIONALMLDS,
                        "project_id": session.case_id,
                        "display_name": "Tampered Placement Must Fail",
                    }
                )

            self.assertEqual("needs_repair", result["status"])
            errors = result["validation_summary"]["errors"]
            self.assertTrue(any("agent_placement_commit_guard" in error for error in errors), errors)
            self.assertTrue(
                any("outside room bounds" in error or "Manifest-Hash" in error for error in errors),
                errors,
            )
            self.assertEqual(["functionalmlds_invariants"], executed_stages)
            self.assertNotIn("project_materialization", executed_stages)

    def test_functionalmlds_authoring_preview_is_non_mutating_and_chat_is_honest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="backend_authoring_preview_") as tmp:
            fixture = self._functional_fixture(Path(tmp))
            store = fixture["store"]
            session = fixture["session"]
            adapter = fixture["adapter"]
            case_dir = fixture["case_dir"]
            paths = SessionStore._functionalmlds_placement_transaction_paths(case_dir)
            files_before = self._file_snapshot(paths)
            placement_before = copy.deepcopy(session.placement_preview)

            chat = store.arrow_chat(
                {
                    "session_id": session.session_id,
                    "user_text": "Stelle den Ausstellungsagenten näher an das Exponat.",
                }
            )
            self.assertEqual("not_applied", chat["chat_status"]["status"])
            self.assertFalse(chat["chat_status"]["model_mutated"])
            self.assertFalse(session.validation_stale)
            self.assertEqual([], session.refinement_requests)
            self.assertEqual(files_before, self._file_snapshot(paths))

            inspected = store.inspect_arrow_authoring(
                {
                    "session_id": session.session_id,
                    "generation_mode": GENERATION_MODE_FUNCTIONALMLDS,
                }
            )
            self.assertEqual("placement_only", inspected["authoring_state"]["scope"])
            revision = inspected["authoring_state"]["revision"]
            requested = self._changed_forward_request(session)

            with mock.patch(
                "backend.state.FunctionalMldsAdapter.discover",
                return_value=adapter,
            ):
                previewed = store.preview_arrow_authoring(
                    {
                        "session_id": session.session_id,
                        "generation_mode": GENERATION_MODE_FUNCTIONALMLDS,
                        "expected_revision": revision,
                        "change": {
                            "kind": "agent_placement",
                            "rationale": "Blickrichtung zum Exponat korrigieren.",
                            "agent_placements": requested,
                        },
                    }
                )

            self.assertEqual("preview_ready", previewed["status"])
            self.assertFalse(previewed["mutation_applied"])
            self.assertEqual("previewed", previewed["change"]["lifecycle"])
            self.assertEqual(1, len(previewed["change"]["diffs"]))
            self.assertEqual(files_before, self._file_snapshot(paths))
            self.assertEqual(placement_before, session.placement_preview)
            self.assertTrue(previewed["change"]["affected_artifacts"])
            for path in previewed["change"]["affected_artifacts"]:
                self.assertFalse(Path(path).is_absolute(), path)
                self.assertNotIn("\\", path)
            serialized = json.dumps(previewed, ensure_ascii=False)
            self.assertNotIn(str(case_dir), serialized)
            self.assertNotIn(str(Path(tmp)), serialized)

            blocked = store.commit_arrow_project(
                {
                    "session_id": session.session_id,
                    "project_id": session.case_id,
                    "display_name": "Open Preview Must Block",
                }
            )
            self.assertEqual("needs_authoring_decision", blocked["status"])

    def test_functionalmlds_authoring_apply_accept_and_undo_is_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="backend_authoring_undo_") as tmp:
            fixture = self._functional_fixture(Path(tmp))
            store = fixture["store"]
            session = fixture["session"]
            adapter = fixture["adapter"]
            case_dir = fixture["case_dir"]
            paths = SessionStore._functionalmlds_placement_transaction_paths(case_dir)
            files_before = self._file_snapshot(paths)
            placement_before = copy.deepcopy(session.placement_preview)

            inspected = store.inspect_arrow_authoring({"session_id": session.session_id})
            requested = self._changed_forward_request(session)
            with mock.patch(
                "backend.state.FunctionalMldsAdapter.discover",
                return_value=adapter,
            ):
                previewed = store.preview_arrow_authoring(
                    {
                        "session_id": session.session_id,
                        "expected_revision": inspected["authoring_state"]["revision"],
                        "change": {
                            "kind": "agent_placement",
                            "agent_placements": requested,
                        },
                    }
                )
                applied = store.apply_arrow_authoring(
                    {
                        "session_id": session.session_id,
                        "change_id": previewed["change"]["change_id"],
                        "expected_revision": previewed["authoring_state"]["revision"],
                    }
                )

            self.assertEqual("applied_pending_accept", applied["status"])
            self.assertTrue(applied["mutation_applied"])
            self.assertEqual(
                "valid",
                applied["change"]["analysis_validation_summary"]["status"],
            )
            self.assertNotEqual(files_before, self._file_snapshot(paths))
            self.assertNotEqual(placement_before, session.placement_preview)

            accepted = store.accept_arrow_authoring(
                {
                    "session_id": session.session_id,
                    "change_id": applied["change"]["change_id"],
                    "expected_revision": applied["authoring_state"]["revision"],
                }
            )
            self.assertEqual("accepted", accepted["status"])
            self.assertTrue(accepted["authoring_state"]["can_undo"])
            files_accepted = self._file_snapshot(paths)

            with mock.patch(
                "backend.state.FunctionalMldsAdapter.discover",
                return_value=adapter,
            ):
                undone = store.undo_arrow_authoring(
                    {
                        "session_id": session.session_id,
                        "change_id": accepted["change"]["change_id"],
                        "expected_revision": accepted["authoring_state"]["revision"],
                    }
                )
            self.assertEqual("undone", undone["status"])
            self.assertFalse(undone["mutation_applied"])
            self.assertFalse(undone["authoring_state"]["can_undo"])
            self.assertEqual(files_before, self._file_snapshot(paths))
            self.assertEqual(placement_before, session.placement_preview)
            self.assertNotEqual(files_accepted, self._file_snapshot(paths))

    def test_functionalmlds_authoring_discard_and_revision_conflict_are_non_destructive(self) -> None:
        with tempfile.TemporaryDirectory(prefix="backend_authoring_discard_") as tmp:
            fixture = self._functional_fixture(Path(tmp))
            store = fixture["store"]
            session = fixture["session"]
            adapter = fixture["adapter"]
            case_dir = fixture["case_dir"]
            paths = SessionStore._functionalmlds_placement_transaction_paths(case_dir)
            files_before = self._file_snapshot(paths)

            inspected = store.inspect_arrow_authoring({"session_id": session.session_id})
            requested = self._changed_forward_request(session)
            with mock.patch(
                "backend.state.FunctionalMldsAdapter.discover",
                return_value=adapter,
            ):
                conflict = store.preview_arrow_authoring(
                    {
                        "session_id": session.session_id,
                        "expected_revision": "sha256:" + ("0" * 64),
                        "change": {
                            "kind": "agent_placement",
                            "agent_placements": requested,
                        },
                    }
                )
                self.assertEqual("conflict", conflict["status"])
                self.assertEqual(files_before, self._file_snapshot(paths))

                previewed = store.preview_arrow_authoring(
                    {
                        "session_id": session.session_id,
                        "expected_revision": inspected["authoring_state"]["revision"],
                        "change": {
                            "kind": "agent_placement",
                            "agent_placements": requested,
                        },
                    }
                )
                applied = store.apply_arrow_authoring(
                    {
                        "session_id": session.session_id,
                        "change_id": previewed["change"]["change_id"],
                        "expected_revision": previewed["authoring_state"]["revision"],
                    }
                )
                discarded = store.discard_arrow_authoring(
                    {
                        "session_id": session.session_id,
                        "change_id": applied["change"]["change_id"],
                        "expected_revision": applied["authoring_state"]["revision"],
                    }
                )

            self.assertEqual("discarded", discarded["status"])
            self.assertFalse(discarded["mutation_applied"])
            self.assertEqual("idle", discarded["authoring_state"]["lifecycle"])
            self.assertEqual(files_before, self._file_snapshot(paths))

    def test_functionalmlds_authoring_apply_failure_rolls_back_and_keeps_preview(self) -> None:
        with tempfile.TemporaryDirectory(prefix="backend_authoring_failure_") as tmp:
            fixture = self._functional_fixture(Path(tmp))
            store = fixture["store"]
            session = fixture["session"]
            adapter = fixture["adapter"]
            case_dir = fixture["case_dir"]
            paths = SessionStore._functionalmlds_placement_transaction_paths(case_dir)
            files_before = self._file_snapshot(paths)
            placement_before = copy.deepcopy(session.placement_preview)

            inspected = store.inspect_arrow_authoring({"session_id": session.session_id})
            requested = self._changed_forward_request(session)
            with mock.patch(
                "backend.state.FunctionalMldsAdapter.discover",
                return_value=adapter,
            ):
                previewed = store.preview_arrow_authoring(
                    {
                        "session_id": session.session_id,
                        "expected_revision": inspected["authoring_state"]["revision"],
                        "change": {
                            "kind": "agent_placement",
                            "agent_placements": requested,
                        },
                    }
                )
                with mock.patch.object(
                    adapter,
                    "run_stage",
                    side_effect=RuntimeError("forced authoring regeneration failure"),
                ):
                    failed = store.apply_arrow_authoring(
                        {
                            "session_id": session.session_id,
                            "change_id": previewed["change"]["change_id"],
                            "expected_revision": previewed["authoring_state"]["revision"],
                        }
                    )

            self.assertEqual("invalid", failed["status"])
            self.assertEqual("previewed", failed["authoring_state"]["lifecycle"])
            self.assertEqual(files_before, self._file_snapshot(paths))
            self.assertEqual(placement_before, session.placement_preview)
            self.assertTrue(
                any(
                    "forced authoring regeneration failure" in error
                    for error in failed["errors"]
                ),
                failed["errors"],
            )

    @staticmethod
    def _store(root: Path) -> SessionStore:
        backend_root = Path(__file__).resolve().parents[1]
        return SessionStore(
            max_history_turns=4,
            max_handoffs=1,
            kb=KnowledgeBase(root / "kb"),
            kb_max_snippets=2,
            model="test-model",
            temperature=0.0,
            stt_model="whisper-1",
            stt_language="",
            stt_max_audio_bytes=1024,
            openai=object(),  # Placement updates never call the OpenAI client.
            project_manager=ProjectManager(
                root / "projects",
                template_room_plan=backend_root / "examples" / "room_plan.example.json",
                template_agents=backend_root / "examples" / "agents.example.json",
            ),
        )

    @staticmethod
    def _legacy_session() -> ArrowProjectDraft:
        agents = [
            {"id": "agent_a", "display_name": "Agent A"},
            {"id": "agent_b", "display_name": "Agent B"},
        ]
        preview = {
            "room_objects": [],
            "agent_placements": [
                {
                    "id": "agent_a",
                    "display_name": "Agent A",
                    "position": {"x": -1.0, "y": 0.0, "z": 0.0},
                    "forward": {"x": 0.0, "y": 0.0, "z": 1.0},
                },
                {
                    "id": "agent_b",
                    "display_name": "Agent B",
                    "position": {"x": 1.0, "y": 0.0, "z": 0.0},
                    "forward": {"x": 0.0, "y": 0.0, "z": 1.0},
                },
            ],
        }
        return ArrowProjectDraft(
            session_id="legacy-placement-session",
            arrow_payload={},
            analysis="",
            assistant_message="",
            project={"display_name": "Legacy Placement"},
            agents=agents,
            knowledge=[],
            placement_preview=preview,
            generation_mode=GENERATION_MODE_LEGACY,
        )

    def _functional_fixture(self, root: Path) -> Dict[str, Any]:
        backend_root = Path(__file__).resolve().parents[1]
        workspace_root = self._find_workspace_root(backend_root)
        source_case = workspace_root / "output" / "case_studies" / "classroom_dinosaur"
        output_root = root / "output"
        case_dir = output_root / "classroom_dinosaur"
        shutil.copytree(source_case, case_dir)
        temp_backend_root = root / "InteractiveAgents"
        temp_backend_root.mkdir(parents=True)
        store = self._store(temp_backend_root)
        adapter = FunctionalMldsAdapter.discover(
            workspace_root=workspace_root,
            backend_root=temp_backend_root,
            output_root=output_root,
        )
        # Recompute with the current placement implementation.  The checked-in
        # fixture may have been produced by an older obstacle-footprint rule.
        adapter.run_stage(case_dir, "agent_placement")
        adapter.run_stage(case_dir, "placement_metrics")
        roles = self._read_json(case_dir / "intermediate" / "agent_roles.generated.json")
        placements = self._read_json(case_dir / "intermediate" / "agent_placements.json")
        session = ArrowProjectDraft(
            session_id="functionalmlds-placement-session",
            arrow_payload={},
            analysis="",
            assistant_message="",
            project={"display_name": "FunctionalMLDS Placement"},
            agents=copy.deepcopy(roles["agents"]),
            knowledge=[],
            placement_preview={
                "room_bounds": copy.deepcopy(placements.get("room_bounds") or {}),
                "room_objects": [],
                "agent_placements": copy.deepcopy(placements["agent_placements"]),
            },
            generation_mode=GENERATION_MODE_FUNCTIONALMLDS,
            case_id=case_dir.name,
            case_dir=str(case_dir),
            agent_roles=copy.deepcopy(roles),
            functionalmlds_path=str(
                case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"
            ),
            validation_summary={"status": "valid"},
        )
        store.arrow_sessions[session.session_id] = session
        return {
            "store": store,
            "session": session,
            "adapter": adapter,
            "case_dir": case_dir,
        }

    @staticmethod
    def _valid_request(session: ArrowProjectDraft) -> list[Dict[str, Any]]:
        placements = {
            str(item.get("id")): item
            for item in session.placement_preview.get("agent_placements") or []
            if isinstance(item, dict)
        }
        return [
            {
                "id": str(agent["id"]),
                "position": copy.deepcopy(placements[str(agent["id"])]["position"]),
                "forward": copy.deepcopy(placements[str(agent["id"])]["forward"]),
            }
            for agent in session.agents
        ]

    @classmethod
    def _changed_forward_request(
        cls,
        session: ArrowProjectDraft,
    ) -> list[Dict[str, Any]]:
        requested = cls._valid_request(session)
        current = requested[0]["forward"]
        candidates = (
            {"x": 1.0, "y": 0.0, "z": 0.0},
            {"x": -1.0, "y": 0.0, "z": 0.0},
            {"x": 0.0, "y": 0.0, "z": 1.0},
            {"x": 0.0, "y": 0.0, "z": -1.0},
        )
        requested[0]["forward"] = next(
            copy.deepcopy(candidate)
            for candidate in candidates
            if candidate != current
        )
        return requested

    @staticmethod
    def _compact_placements(preview: Dict[str, Any]) -> list[Dict[str, Any]]:
        return [
            {
                "id": item["id"],
                "position": item["position"],
                "forward": item["forward"],
            }
            for item in preview.get("agent_placements") or []
        ]

    @staticmethod
    def _file_snapshot(paths: list[Path]) -> Dict[str, bytes | None]:
        return {
            str(path): path.read_bytes() if path.exists() else None
            for path in paths
        }

    @staticmethod
    def _install_concurrency_probe(
        store: SessionStore,
        method_name: str,
        *,
        result_factory: Any = None,
    ) -> Dict[str, Any]:
        original = getattr(store, method_name)
        probe: Dict[str, Any] = {"active": 0, "max_active": 0, "lock": threading.Lock()}

        def wrapped(payload: Dict[str, Any]) -> Dict[str, Any]:
            with probe["lock"]:
                probe["active"] += 1
                probe["max_active"] = max(probe["max_active"], probe["active"])
            try:
                time.sleep(0.075)
                return result_factory() if result_factory is not None else original(payload)
            finally:
                with probe["lock"]:
                    probe["active"] -= 1

        setattr(store, method_name, wrapped)
        return probe

    @staticmethod
    def _run_parallel_barrier(call: Any) -> tuple[list[Dict[str, Any]], list[BaseException]]:
        barrier = threading.Barrier(3)
        results: list[Dict[str, Any]] = []
        errors: list[BaseException] = []

        def worker() -> None:
            try:
                barrier.wait(timeout=3)
                results.append(call())
            except BaseException as exc:  # captured for an explicit assertion in the main test thread
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for thread in threads:
            thread.start()
        barrier.wait(timeout=3)
        for thread in threads:
            thread.join(timeout=5)
        if any(thread.is_alive() for thread in threads):
            errors.append(AssertionError("Parallel mutation worker did not terminate."))
        return results, errors

    @staticmethod
    def _read_json(path: Path) -> Dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8-sig"))

    @staticmethod
    def _find_workspace_root(start: Path) -> Path:
        for candidate in [start, *start.parents]:
            if (candidate / "tools" / "case_study_pipeline").exists():
                return candidate
        raise AssertionError("Workspace root with tools/case_study_pipeline not found.")


if __name__ == "__main__":
    unittest.main()
