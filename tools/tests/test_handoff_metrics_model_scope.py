from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.case_study_pipeline.validators.handoff_metrics import (
    compute_handoff_metrics,
    run_handoff_metrics_for_case,
)


def _event(*, source: str, target: str, schema_version: str, model_sha256: str = "") -> dict:
    event = {
        "event_id": f"EVT-{schema_version}-{source}-{target}",
        "event_type": "backend_handoff_completed",
        "schema_version": schema_version,
        "runtime_action_id": "RA-CASE-BACKEND-CHAT-HANDOFF",
        "runtime_binding_id": "RB-CASE-HANDOFF-TO-RESPONSIBLE-AGENT",
        "session_id": "session-1",
        "metadata": {"from": source, "to": target},
    }
    if model_sha256:
        event["model_sha256"] = model_sha256
    return event


class HandoffMetricsModelScopeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.agent_roles = {
            "agents": [
                {"id": "agent_a", "handoff_targets": ["agent_b"]},
                {"id": "agent_b", "handoff_targets": []},
                {"id": "agent_c", "handoff_targets": []},
            ]
        }
        self.handoff_matrix = {
            "handoffs": [
                {
                    "source_agent_id": "agent_a",
                    "target_agent_id": "agent_b",
                    "condition": "B is responsible.",
                    "reason": "Delegate to B.",
                }
            ]
        }

    def test_v2_scope_ignores_legacy_and_other_model_events_but_checks_current_model(self) -> None:
        active_sha = "A" * 64
        result = compute_handoff_metrics(
            agent_roles=self.agent_roles,
            handoff_matrix=self.handoff_matrix,
            runtime_events=[
                _event(source="agent_a", target="agent_c", schema_version="1.0"),
                _event(
                    source="agent_a",
                    target="agent_c",
                    schema_version="2.0",
                    model_sha256="B" * 64,
                ),
                _event(
                    source="agent_a",
                    target="agent_b",
                    schema_version="2.0",
                    model_sha256=active_sha.lower(),
                ),
            ],
            test_results=[],
            active_model_sha256=active_sha,
        )

        self.assertEqual("valid", result["status"])
        self.assertEqual(3, result["metrics"]["runtime_event_count"])
        self.assertEqual(1, result["metrics"]["current_model_runtime_event_count"])
        self.assertEqual(2, result["metrics"]["historical_runtime_event_count"])
        self.assertEqual(1, result["metrics"]["observed_valid_handoff_event_count"])

        invalid_current = compute_handoff_metrics(
            agent_roles=self.agent_roles,
            handoff_matrix=self.handoff_matrix,
            runtime_events=[
                _event(
                    source="agent_a",
                    target="agent_c",
                    schema_version="2.0",
                    model_sha256=active_sha,
                )
            ],
            test_results=[],
            active_model_sha256=active_sha,
        )
        self.assertEqual("invalid", invalid_current["status"])
        self.assertEqual(
            [{"source": "agent_a", "target": "agent_c"}],
            invalid_current["observed_invalid_handoff_pairs"],
        )

    def test_legacy_case_keeps_unscoped_validation(self) -> None:
        result = compute_handoff_metrics(
            agent_roles=self.agent_roles,
            handoff_matrix=self.handoff_matrix,
            runtime_events=[_event(source="agent_a", target="agent_c", schema_version="1.0")],
            test_results=[],
        )
        self.assertEqual("invalid", result["status"])
        self.assertEqual(1, result["metrics"]["current_model_runtime_event_count"])
        self.assertEqual(0, result["metrics"]["historical_runtime_event_count"])

    def test_case_runner_hashes_v2_model_and_reports_historical_events(self) -> None:
        with tempfile.TemporaryDirectory(prefix="handoff_model_scope_") as tmp:
            case_dir = Path(tmp) / "case"
            (case_dir / "intermediate").mkdir(parents=True)
            (case_dir / "runtime_logs").mkdir()
            (case_dir / "functionalmlds").mkdir()
            (case_dir / "validation").mkdir()
            (case_dir / "intermediate" / "agent_roles.generated.json").write_text(
                json.dumps(self.agent_roles), encoding="utf-8"
            )
            (case_dir / "intermediate" / "handoff_matrix.json").write_text(
                json.dumps(self.handoff_matrix), encoding="utf-8"
            )
            model_path = case_dir / "functionalmlds" / "functionalmlds.v2.instance.json"
            model_path.write_bytes(b'{"schema":"dynamic_functional_mlds_v2_instance"}\n')
            active_sha = hashlib.sha256(model_path.read_bytes()).hexdigest().upper()
            events = [
                _event(source="agent_a", target="agent_c", schema_version="1.0"),
                _event(
                    source="agent_a",
                    target="agent_b",
                    schema_version="2.0",
                    model_sha256=active_sha,
                ),
            ]
            (case_dir / "runtime_logs" / "events.jsonl").write_text(
                "".join(json.dumps(event) + "\n" for event in events), encoding="utf-8"
            )

            result = run_handoff_metrics_for_case(case_dir)

            self.assertEqual("success", result["status"])
            metrics = result["validation"]["metrics"]
            self.assertEqual(active_sha, metrics["active_model_sha256"])
            self.assertEqual(1, metrics["historical_runtime_event_count"])
            self.assertEqual(1, metrics["observed_valid_handoff_event_count"])


if __name__ == "__main__":
    unittest.main()
