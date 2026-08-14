from __future__ import annotations

import unittest

from tools.case_study_pipeline.handoff_derivation import (
    derive_handoff_artifacts,
    validate_handoff_derivation,
)


class HandoffDerivationCompleteGraphTests(unittest.TestCase):
    @staticmethod
    def _roles() -> dict:
        return {
            "agents": [
                {
                    "id": agent_id,
                    "display_name": agent_id.title(),
                    "persona": f"Persona {agent_id}",
                    "expertise": [f"topic_{agent_id}"],
                    "responsible_zone_ids": [f"zone_{agent_id}"],
                    "grounded_object_ids": [f"asset_{agent_id}"],
                    "knowledge_tags": [f"knowledge_{agent_id}"],
                    "handoff_targets": [],
                }
                for agent_id in ("alpha", "beta", "gamma")
            ]
        }

    @staticmethod
    def _functional_agents() -> dict:
        return {
            "agents": [
                {
                    "id": f"AG-{agent_id.upper()}",
                    "source_agent_id": agent_id,
                    "handoff_targets": [],
                }
                for agent_id in ("alpha", "beta", "gamma")
            ]
        }

    def test_derivation_models_every_directed_non_self_pair(self) -> None:
        derived = derive_handoff_artifacts(
            agent_roles=self._roles(),
            functionalmlds_instance=self._functional_agents(),
            existing_handoff_matrix={"handoffs": []},
        )
        report = validate_handoff_derivation(
            derived["agent_roles"],
            derived["handoff_matrix"],
        )

        self.assertEqual("valid", report["status"], report["errors"])
        self.assertEqual(6, report["metrics"]["expected_direct_handoff_count"])
        self.assertEqual(0, report["metrics"]["missing_direct_handoff_count"])

    def test_validator_rejects_a_missing_direct_pair(self) -> None:
        roles = self._roles()
        roles["agents"][0]["handoff_targets"] = ["beta"]
        matrix = {
            "handoffs": [
                {
                    "source_agent_id": "alpha",
                    "target_agent_id": "beta",
                    "condition": "topic beta",
                    "reason": "beta owns the topic",
                }
            ]
        }

        report = validate_handoff_derivation(roles, matrix)

        self.assertEqual("invalid", report["status"])
        self.assertGreater(report["metrics"]["missing_direct_handoff_count"], 0)
        self.assertTrue(
            any("Direct agent handoff is missing" in item for item in report["errors"])
        )


if __name__ == "__main__":
    unittest.main()
