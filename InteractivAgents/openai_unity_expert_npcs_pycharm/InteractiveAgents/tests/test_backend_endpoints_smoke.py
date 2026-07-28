from __future__ import annotations

import hashlib
import http.client
import io
import json
import re
import shutil
import socket
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict
from unittest import mock

from backend.functionalmlds_adapter import FunctionalMldsAdapter
from backend.functionalmlds_v2_runtime import FunctionalMldsContractError, load_project_contract
from backend.kb import KnowledgeBase
from backend.openai_client import OpenAIHTTPError
from backend.placement import normalize_placement_preview
from backend.projects import ProjectManager
from backend.server import (
    MAX_JSON_BODY_BYTES,
    MAX_MULTIPART_BODY_BYTES,
    _read_json,
    _read_multipart,
    start_http_server,
)
from backend.state import SessionStore
from backend.version import BACKEND_VERSION, backend_version_payload


class FakeOpenAIClient:
    api_key = "test-key"
    timeout_seconds = 1

    def __init__(self) -> None:
        self.structured_calls = 0
        self.json_calls = 0

    def create_structured_json(self, **kwargs: Any) -> tuple[Dict[str, Any], Dict[str, Any], str]:
        self.structured_calls += 1
        if kwargs.get("schema_name") == "npc_action":
            raise OpenAIHTTPError(0, "forced offline chat fallback")
        draft = self._legacy_draft()
        return draft, {"id": "fake-structured-response"}, json.dumps(draft)

    def create_json_object(self, **_: Any) -> tuple[Dict[str, Any], Dict[str, Any], str]:
        self.json_calls += 1
        draft = self._legacy_draft()
        return draft, {"id": "fake-json-response"}, json.dumps(draft)

    @staticmethod
    def _legacy_draft() -> Dict[str, Any]:
        return {
            "assistant_message": "Legacy-Smoke-Analyse abgeschlossen.",
            "analysis": "Deterministischer Legacy-Draft fuer Endpoint-Smoke.",
            "project": {
                "display_name": "Endpoint Legacy Smoke",
                "description": "Legacy endpoint smoke project.",
            },
            "agents": [
                {
                    "id": "legacy_teacher",
                    "display_name": "Legacy Teacher",
                    "persona": "Erklaert den Raum und moderiert Fragen.",
                    "voice": "alloy",
                    "voice_gender": "maennlich",
                    "voice_style": "klar",
                    "tts_model": "gpt-4o-mini-tts",
                    "expertise": ["Raumueberblick"],
                    "knowledge_tags": ["scene"],
                },
                {
                    "id": "legacy_expert",
                    "display_name": "Legacy Expert",
                    "persona": "Ergaenzt fachliche Details.",
                    "voice": "coral",
                    "voice_gender": "weiblich",
                    "voice_style": "praezise",
                    "tts_model": "gpt-4o-mini-tts",
                    "expertise": ["Objektdetails"],
                    "knowledge_tags": ["objects"],
                },
            ],
            "knowledge": [
                {
                    "tag": "scene",
                    "name": "overview",
                    "text": "Der Legacy-Smoke nutzt dieselbe MLDS-Quelle, erzeugt aber keine FunctionalMLDS-Artefakte.",
                }
            ],
            "placement_preview": {
                "room_objects": [],
                "agent_placements": [
                    {
                        "id": "legacy_teacher",
                        "position": {"x": -0.5, "y": 0.0, "z": 0.0},
                        "forward": {"x": 0.0, "y": 0.0, "z": 1.0},
                        "spawn_point_id": "legacy_spawn_1",
                        "zone_id": "legacy_zone",
                        "tags": ["legacy"],
                    },
                    {
                        "id": "legacy_expert",
                        "position": {"x": 0.5, "y": 0.0, "z": 0.0},
                        "forward": {"x": 0.0, "y": 0.0, "z": 1.0},
                        "spawn_point_id": "legacy_spawn_2",
                        "zone_id": "legacy_zone",
                        "tags": ["legacy"],
                    },
                ],
                "room_bounds": {"min_x": -2.0, "max_x": 2.0, "min_z": -2.0, "max_z": 2.0},
            },
        }


class EndpointSmokeSessionStore(SessionStore):
    test_backend_root: Path

    def _project_root(self) -> Path:
        return self.test_backend_root


class BackendEndpointSmokeTest(unittest.TestCase):
    def test_request_body_readers_accept_payloads_within_limits(self) -> None:
        json_body = b'{"status":"ok"}'
        json_handler = mock.Mock()
        json_handler.headers = {"Content-Length": str(len(json_body))}
        json_handler.rfile = io.BytesIO(json_body)
        self.assertEqual({"status": "ok"}, _read_json(json_handler))

        boundary = "request-limit-smoke"
        multipart_body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="session_id"\r\n'
            "\r\n"
            "session-1\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="audio"; filename="sample.wav"\r\n'
            "Content-Type: audio/wav\r\n"
            "\r\n"
            "audio-bytes\r\n"
            f"--{boundary}--\r\n"
        ).encode("utf-8")
        multipart_handler = mock.Mock()
        multipart_handler.headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(multipart_body)),
        }
        multipart_handler.rfile = io.BytesIO(multipart_body)

        fields, files = _read_multipart(multipart_handler)

        self.assertEqual("session-1", fields["session_id"])
        self.assertEqual("sample.wav", files["audio"]["filename"])
        self.assertEqual(b"audio-bytes", files["audio"]["content"])

    def test_request_body_readers_reject_oversized_bodies_before_reading(self) -> None:
        cases = [
            (
                "json",
                _read_json,
                {"Content-Length": str(MAX_JSON_BODY_BYTES + 1)},
                "JSON-Body ist zu groß",
            ),
            (
                "multipart",
                _read_multipart,
                {
                    "Content-Type": "multipart/form-data; boundary=boundary",
                    "Content-Length": str(MAX_MULTIPART_BODY_BYTES + 1),
                },
                "Multipart-Body ist zu groß",
            ),
        ]

        for name, reader, headers, expected_error in cases:
            with self.subTest(body_kind=name):
                handler = mock.Mock()
                handler.headers = headers
                handler.rfile.read.side_effect = AssertionError(
                    "Oversized request body must not be read."
                )

                with self.assertRaisesRegex(ValueError, expected_error):
                    reader(handler)

                handler.rfile.read.assert_not_called()

    def test_http_rejects_oversized_json_and_multipart_requests(self) -> None:
        store = mock.Mock()
        base_url = self._start_server(store)
        cases = [
            (
                "/setup",
                "application/json",
                MAX_JSON_BODY_BYTES + 1,
                "JSON-Body ist zu groß",
            ),
            (
                "/stt",
                "multipart/form-data; boundary=boundary",
                MAX_MULTIPART_BODY_BYTES + 1,
                "Multipart-Body ist zu groß",
            ),
        ]

        for path, content_type, declared_length, expected_error in cases:
            with self.subTest(path=path):
                status, response = self._post_headers_only(
                    base_url,
                    path,
                    content_type=content_type,
                    content_length=declared_length,
                )
                self.assertEqual(400, status)
                self.assertIn(expected_error, response["error"])

        store.setup_from_request.assert_not_called()
        store.stt.assert_not_called()

    def test_placement_authoring_http_routes_forward_exact_payloads(self) -> None:
        route_store = mock.Mock()
        route_methods = {
            "inspect": "inspect_arrow_authoring",
            "preview": "preview_arrow_authoring",
            "apply": "apply_arrow_authoring",
            "accept": "accept_arrow_authoring",
            "discard": "discard_arrow_authoring",
            "undo": "undo_arrow_authoring",
        }
        for action, method_name in route_methods.items():
            setattr(
                route_store,
                method_name,
                mock.Mock(return_value={"status": action, "route": method_name}),
            )

        base_url = self._start_server(route_store)
        advertised = self._get_json(base_url, "/")["endpoints"]
        payload = {
            "session_id": "authoring-http-smoke",
            "expected_revision": "sha256:" + ("1" * 64),
        }
        for action, method_name in route_methods.items():
            with self.subTest(action=action):
                response = self._post_json(
                    base_url,
                    f"/projects/arrow/authoring/{action}",
                    payload,
                )
                self.assertEqual(action, response["status"])
                self.assertEqual(method_name, response["route"])
                getattr(route_store, method_name).assert_called_once_with(payload)
                self.assertIn(
                    f"POST /projects/arrow/authoring/{action}",
                    advertised,
                )

    def test_legacy_and_functionalmlds_endpoints(self) -> None:
        backend_root = Path(__file__).resolve().parents[1]
        workspace_root = self._find_workspace_root(backend_root)
        fixture_case = workspace_root / "output" / "case_studies" / "classroom_dinosaur"
        source_payload = self._read_json(fixture_case / "input" / "source_mlds.json")

        with tempfile.TemporaryDirectory(prefix="functionalmlds_endpoint_smoke_") as tmp:
            tmp_root = Path(tmp)
            temp_backend_root = tmp_root / "InteractiveAgents"
            temp_output_root = tmp_root / "wizard_functionalmlds"
            self._prepare_temp_backend(backend_root, temp_backend_root)
            self._copy_tree(fixture_case, temp_output_root / "classroom_dinosaur")

            project_manager = ProjectManager(
                temp_backend_root / "projects",
                template_room_plan=backend_root / "examples" / "room_plan.example.json",
                template_agents=backend_root / "examples" / "agents.example.json",
            )
            store = EndpointSmokeSessionStore(
                max_history_turns=8,
                max_handoffs=2,
                kb=KnowledgeBase(temp_backend_root / "kb"),
                kb_max_snippets=4,
                model="fake-model",
                temperature=0.0,
                stt_model="whisper-1",
                stt_language="",
                stt_max_audio_bytes=1024,
                openai=FakeOpenAIClient(),
                project_manager=project_manager,
                default_room_plan_path="examples/room_plan.example.json",
                default_agents_path="examples/agents.example.json",
            )
            store.test_backend_root = temp_backend_root

            base_url = self._start_server(store)
            health = self._get_json(base_url, "/health")
            version = self._get_json(base_url, "/version")
            self.assertEqual(backend_version_payload(), health)
            self.assertEqual(health, version)
            self.assertEqual("1.0.0", BACKEND_VERSION)
            original_discover = FunctionalMldsAdapter.discover
            original_manifest_inputs_match = FunctionalMldsAdapter._manifest_inputs_match
            original_manifest_outputs_match = FunctionalMldsAdapter._manifest_outputs_match

            def discover_for_test(**_: Any) -> FunctionalMldsAdapter:
                return original_discover(
                    workspace_root=workspace_root,
                    backend_root=temp_backend_root,
                    output_root=temp_output_root,
                )

            def recover_supplied_llm_fixture(
                adapter_self: FunctionalMldsAdapter,
                case_dir: Path,
                stage_id: str,
                expected_paths: list[Path],
            ) -> bool:
                # This is an endpoint/contract smoke, not a live-LLM test.  The
                # copied fixture contains already validated LLM-stage outputs;
                # prompt edits must not turn the smoke into a network-dependent
                # and non-deterministic generation run.  All deterministic
                # downstream stages still use the production cache checks.
                if stage_id in {"scene_semantics", "agent_roles", "knowledge_synthesis"}:
                    return True
                return original_manifest_inputs_match(adapter_self, case_dir, stage_id, expected_paths)

            def recover_supplied_llm_fixture_outputs(
                adapter_self: FunctionalMldsAdapter,
                case_dir: Path,
                stage_id: str,
                expected_paths: list[Path],
                *,
                allow_missing_derived: bool = False,
            ) -> bool:
                if stage_id in {"scene_semantics", "agent_roles", "knowledge_synthesis"}:
                    return all(path.exists() for path in expected_paths)
                return original_manifest_outputs_match(
                    adapter_self,
                    case_dir,
                    stage_id,
                    expected_paths,
                    allow_missing_derived=allow_missing_derived,
                )

            with (
                mock.patch("backend.state.FunctionalMldsAdapter.discover", side_effect=discover_for_test) as discover_mock,
                mock.patch.object(
                    FunctionalMldsAdapter,
                    "_manifest_inputs_match",
                    new=recover_supplied_llm_fixture,
                ),
                mock.patch.object(
                    FunctionalMldsAdapter,
                    "_manifest_outputs_match",
                    new=recover_supplied_llm_fixture_outputs,
                ),
            ):
                legacy_analyze = self._post_json(
                    base_url,
                    "/projects/arrow/analyze",
                    {"arrow_json": source_payload},
                )
                legacy_draft = legacy_analyze["draft"]
                self.assertEqual("legacy", legacy_draft.get("generation_mode"))
                self.assertEqual("Endpoint Legacy Smoke", legacy_draft["project"]["display_name"])
                self.assertGreaterEqual(len(legacy_draft.get("agents") or []), 2)
                self.assertNotIn("functionalmlds_summary", legacy_draft)
                self.assertNotIn("functionalmlds_path", legacy_draft)
                self.assertNotIn("trace_map_path", legacy_draft)

                legacy_session = store.arrow_sessions[legacy_analyze["session_id"]]
                normalized_legacy_preview = normalize_placement_preview(
                    source_payload,
                    legacy_session.agents,
                    legacy_session.placement_preview,
                )
                legacy_forwards = (
                    {"x": 1.0, "y": 0.0, "z": 0.0},
                    {"x": -1.0, "y": 0.0, "z": 0.0},
                )
                legacy_manual_placements = [
                    {
                        "id": placement["id"],
                        "position": placement["position"],
                        "forward": legacy_forwards[index],
                    }
                    for index, placement in enumerate(
                        normalized_legacy_preview["agent_placements"]
                    )
                ]
                legacy_placement_update = self._post_json(
                    base_url,
                    "/projects/arrow/placement",
                    {
                        "session_id": legacy_analyze["session_id"],
                        "generation_mode": "legacy",
                        "agent_placements": legacy_manual_placements,
                    },
                )
                self.assertEqual("ok", legacy_placement_update.get("status"))
                self.assertEqual("valid", legacy_placement_update["validation"]["status"])
                self.assertTrue(legacy_placement_update.get("mutation_applied"))
                self.assertEqual(
                    legacy_manual_placements,
                    [
                        {
                            "id": item["id"],
                            "position": item["position"],
                            "forward": item["forward"],
                        }
                        for item in legacy_placement_update["placement_preview"]["agent_placements"]
                    ],
                )

                legacy_commit = self._post_json(
                    base_url,
                    "/projects/arrow/commit",
                    {
                        "session_id": legacy_analyze["session_id"],
                        "project_id": "endpoint_legacy_smoke",
                        "display_name": "Endpoint Legacy Smoke",
                        "description": "Endpoint smoke legacy project.",
                    },
                )
                self.assertEqual("ok", legacy_commit.get("status"))
                self.assertEqual("legacy", legacy_commit.get("generation_mode"))
                self.assertEqual("endpoint_legacy_smoke", legacy_commit["project"]["id"])
                legacy_project_dir = temp_backend_root / "projects" / "endpoint_legacy_smoke"
                self.assertTrue((legacy_project_dir / "project.json").exists())
                self.assertTrue((legacy_project_dir / "room_plan.json").exists())
                self.assertTrue((legacy_project_dir / "agents.json").exists())
                self.assertTrue(any((legacy_project_dir / "kb").rglob("*.txt")))
                self.assertFalse((legacy_project_dir / "trace_map.json").exists())
                self.assertFalse((legacy_project_dir / "functionalmlds").exists())
                self.assertNotIn("functionalmlds_path", legacy_commit)
                self.assertNotIn("trace_map_path", legacy_commit)
                self.assertNotIn("validation_summary", legacy_commit)
                legacy_agents_by_id = {
                    item["id"]: item
                    for item in self._read_json(legacy_project_dir / "agents.json")["agents"]
                }
                for requested in legacy_manual_placements:
                    with self.subTest(legacy_manual_placement=requested["id"]):
                        saved = legacy_agents_by_id[requested["id"]]
                        self.assertEqual(requested["position"], saved["position"])
                        self.assertEqual(requested["forward"], saved["forward"])
                self.assertEqual(0, discover_mock.call_count)

                functional_analyze = self._post_json(
                    base_url,
                    "/projects/arrow/analyze",
                    {
                        "generation_mode": "functionalmlds",
                        "project_id_hint": "classroom_dinosaur",
                        "run_validation": True,
                        "max_repair_attempts": 0,
                        "arrow_json": source_payload,
                    },
                )
                functional_draft = functional_analyze["draft"]
                self.assertEqual("functionalmlds", functional_draft.get("generation_mode"))
                self.assertEqual("valid", functional_draft["validation_summary"]["status"])
                self.assertEqual("classroom_dinosaur", functional_draft["functionalmlds_summary"]["case_id"])
                self.assertTrue(functional_draft.get("functionalmlds_path"))
                self.assertEqual(4, len(functional_draft.get("agents") or []))
                self.assertGreaterEqual(len(functional_draft.get("knowledge") or []), 8)
                self.assertGreater(functional_draft["functionalmlds_summary"].get("runtime_binding_count", 0), 0)
                self.assertGreater(functional_draft["functionalmlds_summary"].get("validation_case_count", 0), 0)
                self.assertGreater(functional_draft["scenario_summary"].get("step_count", 0), 0)
                self.assertGreater(functional_draft["capability_summary"].get("runtime_action_count", 0), 0)
                self.assertGreater(functional_draft["handoff_summary"].get("declared_handoff_pair_count", 0), 0)
                self.assertGreaterEqual(functional_draft["handoff_summary"].get("valid_handoff_target_ratio", 0.0), 1.0)
                self.assertGreater(functional_draft["room_knowledge_summary"].get("room_object_count", 0), 0)
                self.assertGreater(functional_draft["room_knowledge_summary"].get("knowledge_file_count", 0), 0)

                functional_case_dir = temp_output_root / "classroom_dinosaur"
                placement_module = discover_for_test().import_pipeline_module("agent_placement")
                current_generated_placements = placement_module.generate_agent_placements(
                    normalized_scene=self._read_json(
                        functional_case_dir / "intermediate" / "scene_graph.normalized.json"
                    ),
                    scene_semantics=self._read_json(
                        functional_case_dir / "intermediate" / "scene_semantics.json"
                    ),
                    agent_roles=self._read_json(
                        functional_case_dir / "intermediate" / "agent_roles.generated.json"
                    ),
                )["agent_placements"]
                generated_by_id = {
                    item["id"]: item
                    for item in current_generated_placements
                }
                analyzed_placements = [
                    generated_by_id[item["id"]]
                    for item in functional_draft["placement_preview"]["agent_placements"]
                ]
                reversed_positions = [
                    dict(item["position"])
                    for item in reversed(analyzed_placements)
                ]
                functional_forwards = (
                    {"x": 1.0, "y": 0.0, "z": 0.0},
                    {"x": -1.0, "y": 0.0, "z": 0.0},
                    {"x": 0.0, "y": 0.0, "z": 1.0},
                    {"x": 0.0, "y": 0.0, "z": -1.0},
                )
                functional_manual_placements = [
                    {
                        "id": item["id"],
                        "position": reversed_positions[index],
                        "forward": functional_forwards[index],
                    }
                    for index, item in enumerate(analyzed_placements)
                ]
                functional_placement_update = self._post_json(
                    base_url,
                    "/projects/arrow/placement",
                    {
                        "session_id": functional_analyze["session_id"],
                        "generation_mode": "functionalmlds",
                        "agent_placements": functional_manual_placements,
                    },
                )
                self.assertEqual("ok", functional_placement_update.get("status"))
                self.assertEqual("valid", functional_placement_update["validation"]["status"])
                self.assertTrue(functional_placement_update.get("mutation_applied"))
                self.assertEqual(
                    functional_manual_placements,
                    [
                        {
                            "id": item["id"],
                            "position": item["position"],
                            "forward": item["forward"],
                        }
                        for item in functional_placement_update["placement_preview"]["agent_placements"]
                    ],
                )
                placement_artifact = self._read_json(
                    temp_output_root
                    / "classroom_dinosaur"
                    / "intermediate"
                    / "agent_placements.json"
                )
                self.assertEqual("functionalmlds_agent_placements", placement_artifact.get("schema"))
                self.assertEqual("2.0", placement_artifact.get("schema_version"))
                self.assertEqual("2.0.0", placement_artifact.get("placement_algorithm_version"))
                self.assertEqual("wizard_manual", placement_artifact.get("origin"))
                canonical_placement_hash = placement_module.placement_artifact_sha256(
                    placement_artifact
                )
                placement_validation = self._read_json(
                    temp_output_root
                    / "classroom_dinosaur"
                    / "validation"
                    / "agent_placement_validation.json"
                )
                self.assertEqual(
                    canonical_placement_hash,
                    placement_validation.get("placement_artifact_sha256"),
                )
                placement_metrics_path = (
                    temp_output_root
                    / "classroom_dinosaur"
                    / "validation"
                    / "placement_metrics.json"
                )
                placement_metrics = self._read_json(placement_metrics_path)
                self.assertEqual("valid", placement_metrics.get("status"))
                metric_positions = {
                    item["agent_id"]: item["position"]
                    for item in placement_metrics.get("per_agent") or []
                }
                for requested in functional_manual_placements:
                    self.assertEqual(
                        {
                            "x": requested["position"]["x"],
                            "z": requested["position"]["z"],
                        },
                        metric_positions[requested["id"]],
                    )
                manifest = self._read_json(
                    temp_output_root / "classroom_dinosaur" / "stage_manifest.json"
                )
                placement_metrics_stage = next(
                    item
                    for item in manifest["stages"]
                    if item.get("stage_id") == "placement_metrics"
                )
                placement_file_path = (
                    temp_output_root
                    / "classroom_dinosaur"
                    / "intermediate"
                    / "agent_placements.json"
                )
                metrics_input = next(
                    item
                    for item in placement_metrics_stage["inputs"]
                    if Path(str(item.get("path") or "")).name == "agent_placements.json"
                )
                self.assertEqual(
                    hashlib.sha256(placement_file_path.read_bytes()).hexdigest(),
                    metrics_input.get("sha256"),
                )
                placement_artifact_by_id = {
                    item["id"]: item
                    for item in placement_artifact["agent_placements"]
                }
                for requested in functional_manual_placements:
                    with self.subTest(functionalmlds_analyze_placement=requested["id"]):
                        saved = placement_artifact_by_id[requested["id"]]
                        self.assertEqual(requested["position"], saved["position"])
                        self.assertEqual(requested["forward"], saved["forward"])

                functional_commit = self._post_json(
                    base_url,
                    "/projects/arrow/commit",
                    {
                        "session_id": functional_analyze["session_id"],
                        "generation_mode": "functionalmlds",
                        "project_id": "classroom_dinosaur",
                        "display_name": "Classroom Dinosaur Endpoint Smoke",
                        "description": "FunctionalMLDS endpoint smoke project.",
                    },
                )
                self.assertEqual("ok", functional_commit.get("status"), functional_commit.get("validation_summary"))
                self.assertEqual("functionalmlds", functional_commit.get("generation_mode"))
                self.assertEqual("valid", functional_commit["validation_summary"]["status"])
                self.assertEqual("classroom_dinosaur", functional_commit["project"]["id"])
                functional_project_dir = temp_backend_root / "projects" / "classroom_dinosaur"
                trace_map = functional_project_dir / "trace_map.json"
                self.assertTrue((functional_project_dir / "project.json").exists())
                self.assertTrue((functional_project_dir / "room_plan.json").exists())
                self.assertTrue((functional_project_dir / "agents.json").exists())
                self.assertTrue(any((functional_project_dir / "kb").rglob("*.txt")))
                self.assertTrue(trace_map.exists())
                self.assertEqual(str(trace_map), functional_commit.get("trace_map_path"))
                self.assertEqual("functionalmlds_trace_map_v2", self._read_json(trace_map).get("schema"))
                self.assertEqual(
                    "functionalmlds_trace_map_v2",
                    self._read_json(functional_project_dir / "trace_map.v2.json").get("schema"),
                )
                self.assertEqual(
                    "functionalmlds_trace_map",
                    self._read_json(functional_project_dir / "trace_map.v05.json").get("schema"),
                )
                self.assertEqual(
                    "dynamic_functional_mlds_v2_instance",
                    self._read_json(functional_project_dir / "functionalmlds.v2.instance.json").get("schema"),
                )
                self.assertEqual(
                    "functionalmlds_case_study",
                    self._read_json(functional_project_dir / "functionalmlds.v05.instance.json").get("schema"),
                )
                self.assertEqual("valid", functional_commit["validation_summary"]["schema_status"])
                self.assertEqual("valid", functional_commit["validation_summary"]["invariant_status"])
                self.assertEqual("valid", functional_commit["validation_summary"]["materialization_status"])
                self.assertEqual("valid", functional_commit["validation_summary"]["traceability_status"])
                self.assertEqual("valid", functional_commit["validation_summary"]["handoff_status"])
                functional_agents_by_id = {
                    item["id"]: item
                    for item in self._read_json(functional_project_dir / "agents.json")["agents"]
                }
                for requested in functional_manual_placements:
                    with self.subTest(functionalmlds_committed_placement=requested["id"]):
                        saved = functional_agents_by_id[requested["id"]]
                        self.assertEqual(requested["position"], saved["position"])
                        self.assertEqual(requested["forward"], saved["forward"])
                deployment_documents = {
                    "project": self._read_json(functional_project_dir / "project.json"),
                    "agents": self._read_json(functional_project_dir / "agents.json"),
                    "trace": self._read_json(functional_project_dir / "trace_map.json"),
                    "trace_v2": self._read_json(functional_project_dir / "trace_map.v2.json"),
                    "trace_v05": self._read_json(functional_project_dir / "trace_map.v05.json"),
                }
                deployment_fields = (
                    "placement_schema",
                    "placement_schema_version",
                    "placement_algorithm_version",
                    "placement_origin",
                    "placement_artifact_sha256",
                    "placement_projection_sha256",
                )
                for field_name in deployment_fields:
                    declared = {
                        document_name: document.get(field_name)
                        for document_name, document in deployment_documents.items()
                    }
                    with self.subTest(placement_deployment_field=field_name):
                        self.assertEqual(1, len(set(declared.values())), declared)
                        self.assertTrue(next(iter(declared.values())))
                self.assertEqual(
                    canonical_placement_hash,
                    deployment_documents["project"]["placement_artifact_sha256"],
                )
                self.assertEqual(
                    "wizard_manual",
                    deployment_documents["project"]["placement_origin"],
                )
                self.assertRegex(
                    deployment_documents["project"]["placement_projection_sha256"],
                    r"^[0-9a-f]{64}$",
                )

                functional_instance = functional_case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"
                self.assertTrue(functional_instance.exists())
                self.assertEqual(str(functional_instance), functional_commit.get("functionalmlds_path"))
                self.assertEqual("functionalmlds_case_study", self._read_json(functional_instance).get("schema"))
                for report_name in (
                    "schema_validation.json",
                    "functionalmlds_invariants_validation.json",
                    "project_materialization_validation.json",
                    "traceability_metrics.json",
                    "handoff_metrics.json",
                ):
                    report_path = functional_case_dir / "validation" / report_name
                    with self.subTest(report_name=report_name):
                        self.assertTrue(report_path.exists())
                        self.assertEqual("valid", self._read_json(report_path).get("status"))
                handoff_report = self._read_json(functional_case_dir / "validation" / "handoff_metrics.json")
                handoff_metrics = handoff_report.get("metrics") or {}
                self.assertRegex(str(handoff_metrics.get("active_model_sha256") or ""), r"^[A-F0-9]{64}$")
                self.assertGreater(handoff_metrics.get("historical_runtime_event_count", 0), 0)
                self.assertEqual(0, handoff_metrics.get("observed_invalid_handoff_event_count"))
                invariant_report = self._read_json(functional_case_dir / "validation" / "functionalmlds_invariants_validation.json")
                invariant_metrics = invariant_report.get("metrics") or {}
                self.assertGreaterEqual(invariant_metrics.get("invariant_count", 0), 8)
                self.assertEqual(
                    invariant_metrics.get("invariant_count"),
                    invariant_metrics.get("passed_invariant_count"),
                )
                self.assertEqual(0, invariant_metrics.get("failed_invariant_count"))
                self.assertEqual([], invariant_report.get("errors"))
                for invariant in invariant_report.get("invariants") or []:
                    with self.subTest(invariant_id=invariant.get("invariant_id")):
                        self.assertEqual("valid", invariant.get("status"))
                        self.assertEqual(0, invariant.get("error_count"))
                traceability_report = self._read_json(functional_case_dir / "validation" / "traceability_metrics.json")
                traceability_metrics_summary = traceability_report.get("metrics") or {}
                traceability_metrics = traceability_report.get("traceability_metrics") or []
                self.assertEqual([], traceability_report.get("errors"))
                self.assertGreaterEqual(traceability_metrics_summary.get("metric_count", 0), 6)
                self.assertEqual(traceability_metrics_summary.get("metric_count"), len(traceability_metrics))
                self.assertGreaterEqual(traceability_metrics_summary.get("full_coverage_metric_count", 0), 4)
                self.assertGreater(traceability_metrics_summary.get("average_coverage", 0.0), 0.75)
                metrics_by_id = {
                    str(metric.get("metric_id")): metric
                    for metric in traceability_metrics
                }
                for metric_id in (
                    "requirement_to_validation_coverage",
                    "scenario_step_to_capability_coverage",
                    "capability_to_runtime_binding_coverage",
                    "runtime_action_to_log_coverage",
                    "agent_to_knowledge_tag_coverage",
                    "object_group_to_agent_role_grounding",
                ):
                    self.assertIn(metric_id, metrics_by_id)
                    metric = metrics_by_id[metric_id]
                    with self.subTest(traceability_metric_id=metric_id):
                        self.assertGreater(metric.get("denominator", 0), 0)
                        self.assertGreaterEqual(metric.get("numerator", -1), 0)
                        self.assertGreaterEqual(metric.get("coverage", -1.0), 0.0)
                        self.assertLessEqual(metric.get("coverage", 2.0), 1.0)
                for full_metric_id in (
                    "requirement_to_validation_coverage",
                    "capability_to_runtime_binding_coverage",
                    "agent_to_knowledge_tag_coverage",
                    "object_group_to_agent_role_grounding",
                ):
                    with self.subTest(full_traceability_metric_id=full_metric_id):
                        self.assertEqual(1.0, metrics_by_id[full_metric_id].get("coverage"))
                        self.assertEqual([], metrics_by_id[full_metric_id].get("uncovered_ids"))
                self.assertGreater(metrics_by_id["runtime_action_to_log_coverage"].get("coverage", 0.0), 0.0)

                projects = self._get_json(base_url, "/projects")["projects"]
                project_ids = {item.get("id") for item in projects}
                self.assertIn("endpoint_legacy_smoke", project_ids)
                self.assertIn("classroom_dinosaur", project_ids)

                setup = self._post_json(
                    base_url,
                    "/setup",
                    {"project_id": "classroom_dinosaur", "memory_mode": "shared_history"},
                )
                self.assertTrue(setup.get("session_id"))
                self.assertEqual("shared_history", setup.get("memory_mode"))
                agents = setup.get("agents") or []
                self.assertEqual(4, len(agents))
                self.assertTrue(all(agent.get("position") for agent in agents))
                self.assertTrue(all(agent.get("forward") for agent in agents))
                verified_chat_questions = []
                verified_handoffs = []

                room_chat = self._post_json(
                    base_url,
                    "/chat",
                    {
                        "session_id": setup["session_id"],
                        "active_agent_id": "teacher_agent",
                        "interaction_mode": "non_deictic",
                        "user_text": "Welche Ausstattung gibt es im Unterrichtsbereich?",
                    },
                )
                self.assertEqual("teacher_agent", room_chat.get("active_agent_id"))
                self.assertIsNone(room_chat.get("handoff"))
                events = room_chat.get("events") or []
                self.assertGreaterEqual(len(events), 1)
                answer_text = "\n".join(str(event.get("text") or "") for event in events).lower()
                self.assertIn("functionalmlds-raumwissen", answer_text)
                self.assertIn("chalkboard", answer_text)
                self.assertIn("student desks", answer_text)
                verified_chat_questions.append("room_equipment")

                specialty_chat = self._post_json(
                    base_url,
                    "/chat",
                    {
                        "session_id": setup["session_id"],
                        "active_agent_id": "exhibit_interpreter",
                        "interaction_mode": "non_deictic",
                        "user_text": "What is special about the dinosaur skeleton exhibit for paleontology?",
                    },
                )
                self.assertEqual("exhibit_interpreter", specialty_chat.get("active_agent_id"))
                self.assertIsNone(specialty_chat.get("handoff"))
                specialty_events = specialty_chat.get("events") or []
                self.assertGreaterEqual(len(specialty_events), 1)
                specialty_answer = "\n".join(str(event.get("text") or "") for event in specialty_events).lower()
                self.assertIn("functionalmlds-raumwissen", specialty_answer)
                self.assertIn("dinosaur skeleton", specialty_answer)
                self.assertIn("paleontology", specialty_answer)
                verified_chat_questions.append("dinosaur_specialty")

                reading_chat = self._post_json(
                    base_url,
                    "/chat",
                    {
                        "session_id": setup["session_id"],
                        "active_agent_id": "reading_area_guide",
                        "interaction_mode": "non_deictic",
                        "user_text": "What can visitors use in the reading area for study and relaxation?",
                    },
                )
                self.assertEqual("reading_area_guide", reading_chat.get("active_agent_id"))
                self.assertIsNone(reading_chat.get("handoff"))
                reading_events = reading_chat.get("events") or []
                self.assertGreaterEqual(len(reading_events), 1)
                reading_answer = "\n".join(str(event.get("text") or "") for event in reading_events).lower()
                self.assertIn("functionalmlds-raumwissen", reading_answer)
                self.assertIn("reading table", reading_answer)
                self.assertIn("beanbags", reading_answer)
                self.assertIn("bookcase", reading_answer)
                verified_chat_questions.append("reading_area")

                decorative_chat = self._post_json(
                    base_url,
                    "/chat",
                    {
                        "session_id": setup["session_id"],
                        "active_agent_id": "decorative_zone_ambassador",
                        "interaction_mode": "non_deictic",
                        "user_text": "Which art and plants shape the decorative zone ambiance?",
                    },
                )
                self.assertEqual("decorative_zone_ambassador", decorative_chat.get("active_agent_id"))
                self.assertIsNone(decorative_chat.get("handoff"))
                decorative_events = decorative_chat.get("events") or []
                self.assertGreaterEqual(len(decorative_events), 1)
                decorative_answer = "\n".join(str(event.get("text") or "") for event in decorative_events).lower()
                self.assertIn("functionalmlds-raumwissen", decorative_answer)
                self.assertIn("abstract artworks", decorative_answer)
                self.assertIn("potted indoor plants", decorative_answer)
                verified_chat_questions.append("decorative_zone")

                handoff_chat = self._post_json(
                    base_url,
                    "/chat",
                    {
                        "session_id": setup["session_id"],
                        "active_agent_id": "teacher_agent",
                        "interaction_mode": "non_deictic",
                        "user_text": "I need details about the dinosaur skeleton exhibit and paleontology.",
                    },
                )
                self.assertEqual("exhibit_interpreter", handoff_chat.get("active_agent_id"))
                self.assertEqual(
                    {"from": "teacher_agent", "to": "exhibit_interpreter"},
                    {
                        "from": (handoff_chat.get("handoff") or {}).get("from"),
                        "to": (handoff_chat.get("handoff") or {}).get("to"),
                    },
                )
                handoff_events = handoff_chat.get("events") or []
                self.assertGreaterEqual(len(handoff_events), 2)
                handoff_answer = "\n".join(str(event.get("text") or "") for event in handoff_events).lower()
                self.assertIn("exhibit interpreter", handoff_answer)
                self.assertIn("dinosaur skeleton", handoff_answer)
                self.assertIn("paleontology", handoff_answer)
                verified_chat_questions.append("handoff_to_exhibit_interpreter")
                verified_handoffs.append("teacher_agent_to_exhibit_interpreter")
                self.assertGreaterEqual(len(verified_chat_questions), 5)
                self.assertGreaterEqual(len(verified_handoffs), 1)
                tampered_agents = self._read_json(functional_project_dir / "agents.json")
                tampered_agents["agents"][0]["position"]["x"] += 0.125
                (functional_project_dir / "agents.json").write_text(
                    json.dumps(tampered_agents, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    FunctionalMldsContractError,
                    "projection does not match",
                ):
                    load_project_contract(functional_project_dir)
                self._assert_no_secret_markers(temp_backend_root / "projects", temp_output_root)

    @staticmethod
    def _prepare_temp_backend(source_backend: Path, temp_backend: Path) -> None:
        temp_backend.mkdir(parents=True, exist_ok=True)
        BackendEndpointSmokeTest._copy_tree(source_backend / "examples", temp_backend / "examples")
        projects_root = temp_backend / "projects"
        projects_root.mkdir(parents=True, exist_ok=True)
        BackendEndpointSmokeTest._copy_tree(
            source_backend / "projects" / "classroom_dinosaur",
            projects_root / "classroom_dinosaur",
        )
        (temp_backend / "kb").mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _start_server(store: SessionStore) -> str:
        port = BackendEndpointSmokeTest._free_port()
        thread = threading.Thread(target=start_http_server, args=("127.0.0.1", port, store), daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{port}"
        deadline = time.time() + 8.0
        while time.time() < deadline:
            try:
                if BackendEndpointSmokeTest._get_json(base_url, "/health").get("status") == "ok":
                    return base_url
            except Exception:
                time.sleep(0.05)
        raise AssertionError("Backend smoke server did not become healthy.")

    @staticmethod
    def _free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    @staticmethod
    def _get_json(base_url: str, path: str) -> Dict[str, Any]:
        with urllib.request.urlopen(base_url + path, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @staticmethod
    def _post_json(base_url: str, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            base_url + path,
            data=data,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise AssertionError(f"HTTP {exc.code} for {path}: {body}") from exc

    @staticmethod
    def _post_headers_only(
        base_url: str,
        path: str,
        *,
        content_type: str,
        content_length: int,
    ) -> tuple[int, Dict[str, Any]]:
        port = int(base_url.rsplit(":", 1)[1])
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
        try:
            connection.putrequest("POST", path)
            connection.putheader("Content-Type", content_type)
            connection.putheader("Content-Length", str(content_length))
            connection.endheaders()
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload
        finally:
            connection.close()

    @staticmethod
    def _find_workspace_root(start: Path) -> Path:
        for candidate in [start, *start.parents]:
            if (candidate / "tools" / "case_study_pipeline").exists():
                return candidate
        raise AssertionError("Workspace root with tools/case_study_pipeline not found.")

    @staticmethod
    def _read_json(path: Path) -> Dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8-sig"))

    @staticmethod
    def _copy_tree(source: Path, target: Path) -> None:
        shutil.copytree(source, target, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))

    @staticmethod
    def _assert_no_secret_markers(*roots: Path) -> None:
        patterns = (
            re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
            re.compile(r"\bOPENAI_API_KEY\b", re.IGNORECASE),
            re.compile(r"\bopenai_api_key\b", re.IGNORECASE),
            re.compile(re.escape(FakeOpenAIClient.api_key)),
        )
        suffixes = {".json", ".jsonl", ".log", ".md", ".txt", ".xml", ".yaml", ".yml"}
        matches = []
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in suffixes:
                    continue
                try:
                    text = path.read_text(encoding="utf-8-sig")
                except UnicodeDecodeError:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                if any(pattern.search(text) for pattern in patterns):
                    matches.append(str(path))
        if matches:
            raise AssertionError("Secret marker found in generated artifacts/logs: " + ", ".join(matches[:10]))


if __name__ == "__main__":
    unittest.main()
