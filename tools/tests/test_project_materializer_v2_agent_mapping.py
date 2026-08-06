from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

from tools.case_study_pipeline.project_materializer import (  # noqa: E402
    _validate_and_index_agent_placements,
    _validate_v2_agent_provider_contract,
    build_trace_map_v2,
)
from tools.case_study_pipeline.functionalmlds_v2_assembler import (  # noqa: E402
    assemble_v2_instance,
)
from tools.case_study_pipeline.agent_placement import (  # noqa: E402
    PLACEMENT_FLOOR_TOLERANCE,
    generate_agent_placements,
)


CASE_DIR = ROOT / "output" / "case_studies" / "classroom_dinosaur"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ProjectMaterializerV2AgentMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.instance = assemble_v2_instance(
            _read_json(
                CASE_DIR
                / "functionalmlds"
                / "functionalmlds.instance.generated.json"
            )
        )
        cls.agent_roles = _read_json(
            CASE_DIR / "intermediate" / "agent_roles.generated.json"
        )
        # The checked-in case remains an immutable pre-contract cache. Build a
        # current versioned placement artifact in memory for materializer tests.
        cls.placements = generate_agent_placements(
            normalized_scene=_read_json(CASE_DIR / "intermediate" / "scene_graph.normalized.json"),
            scene_semantics=_read_json(CASE_DIR / "intermediate" / "scene_semantics.json"),
            agent_roles=cls.agent_roles,
        )

    def _validate(self, instance: dict, agent_roles: dict | None = None) -> dict:
        return _validate_v2_agent_provider_contract(
            functionalmlds_instance=instance,
            agent_roles=agent_roles or self.agent_roles,
        )

    def test_complete_bijection_is_projected_in_source_agent_order(self) -> None:
        mapping = self._validate(self.instance)
        source_ids = [item["id"] for item in self.agent_roles["agents"]]
        self.assertEqual(set(source_ids), set(mapping))

        trace = build_trace_map_v2(
            case_dir=CASE_DIR,
            project_dir=ROOT / "unused-test-project",
            functionalmlds_instance=self.instance,
            agent_roles=self.agent_roles,
            model_sha256="A" * 64,
        )
        self.assertEqual(source_ids, [item["agent_id"] for item in trace["agents"]])
        self.assertTrue(
            all(item["functionalmlds_agent_id"] == item["entity_id"] for item in trace["agents"])
        )

    def test_unknown_native_source_agent_is_not_silently_filtered(self) -> None:
        instance = copy.deepcopy(self.instance)
        agent = next(item for item in instance["objects"] if item.get("type") == "Agent")
        agent["sourceAgentId"] = "unknown-source-agent"
        with self.assertRaisesRegex(ValueError, "unknown sourceAgentId"):
            self._validate(instance)

    def test_duplicate_native_source_agent_is_rejected_as_ambiguous(self) -> None:
        instance = copy.deepcopy(self.instance)
        agents = [item for item in instance["objects"] if item.get("type") == "Agent"]
        agents[1]["sourceAgentId"] = agents[0]["sourceAgentId"]
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self._validate(instance)

    def test_source_agent_without_native_agent_is_rejected(self) -> None:
        roles = copy.deepcopy(self.agent_roles)
        roles["agents"].append({"id": "unmapped-agent"})
        with self.assertRaisesRegex(ValueError, "without exactly one native Agent/Entity"):
            self._validate(self.instance, roles)

    def test_unresolved_outgoing_agent_reference_is_rejected(self) -> None:
        instance = copy.deepcopy(self.instance)
        agent = next(item for item in instance["objects"] if item.get("type") == "Agent")
        agent["playsActor"] = ["ACTOR-DOES-NOT-EXIST"]
        with self.assertRaisesRegex(ValueError, "unresolved reference"):
            self._validate(instance)

    def test_capability_use_provider_must_provide_its_capability(self) -> None:
        instance = copy.deepcopy(self.instance)
        by_id = {item["id"]: item for item in instance["objects"]}
        use = next(item for item in instance["objects"] if item.get("type") == "CapabilityUse")
        capability_id = (use.get("typeRef") or use.get("capability"))[0]
        provider = by_id[use["provider"][0]]
        provider["providedCapability"] = [
            item for item in provider.get("providedCapability") or [] if item != capability_id
        ]
        with self.assertRaisesRegex(ValueError, "does not provide Capability"):
            self._validate(instance)

    def test_agent_owned_capability_cannot_be_reassigned_to_orchestrator(self) -> None:
        instance = copy.deepcopy(self.instance)
        by_id = {item["id"]: item for item in instance["objects"]}
        use = next(
            item
            for item in instance["objects"]
            if item.get("type") == "CapabilityUse"
            and by_id[item["provider"][0]].get("type") == "Agent"
        )
        capability_id = use["typeRef"][0]
        orchestrator = next(
            item
            for item in instance["objects"]
            if item.get("entityRole") == "runtimeOrchestrator"
        )
        orchestrator.setdefault("providedCapability", []).append(capability_id)
        use["provider"] = [orchestrator["id"]]

        with self.assertRaisesRegex(
            ValueError,
            "must not advertise Agent-owned domain Capabilities|not a modeled Domain Agent",
        ):
            self._validate(instance)

    def test_materializer_requires_complete_exact_placement_projection(self) -> None:
        indexed = _validate_and_index_agent_placements(self.agent_roles, self.placements)
        self.assertEqual(
            {agent["id"] for agent in self.agent_roles["agents"]},
            set(indexed),
        )

        missing = copy.deepcopy(self.placements)
        missing["agent_placements"].pop()
        with self.assertRaisesRegex(ValueError, "missing="):
            _validate_and_index_agent_placements(self.agent_roles, missing)

        duplicate = copy.deepcopy(self.placements)
        duplicate["agent_placements"].append(copy.deepcopy(duplicate["agent_placements"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate agent id"):
            _validate_and_index_agent_placements(self.agent_roles, duplicate)

    def test_materializer_rejects_non_executable_forward_instead_of_defaulting(self) -> None:
        invalid = copy.deepcopy(self.placements)
        invalid["agent_placements"][0]["forward"] = {"x": 0.0, "y": 0.0, "z": 0.0}
        with self.assertRaisesRegex(ValueError, "forward must be normalized"):
            _validate_and_index_agent_placements(self.agent_roles, invalid)

    def test_materializer_rejects_old_contract_unknown_origin_and_non_json_numbers(self) -> None:
        for field, value in (
            ("schema", "wrong"),
            ("schema_version", "1.0"),
            ("placement_algorithm_version", "1.0.0"),
            ("origin", "legacy"),
        ):
            with self.subTest(field=field):
                invalid = copy.deepcopy(self.placements)
                invalid[field] = value
                with self.assertRaises(ValueError):
                    _validate_and_index_agent_placements(self.agent_roles, invalid)

        for vector, value in (("position", True), ("position", "1.0"), ("forward", True), ("forward", "1.0")):
            with self.subTest(vector=vector, value=value):
                invalid = copy.deepcopy(self.placements)
                invalid["agent_placements"][0][vector]["x"] = value
                with self.assertRaisesRegex(ValueError, "finite JSON-number"):
                    _validate_and_index_agent_placements(self.agent_roles, invalid)

    def test_materializer_uses_shared_floor_tolerance(self) -> None:
        at_limit = copy.deepcopy(self.placements)
        at_limit["agent_placements"][0]["position"]["y"] = PLACEMENT_FLOOR_TOLERANCE
        _validate_and_index_agent_placements(self.agent_roles, at_limit)

        outside = copy.deepcopy(at_limit)
        outside["agent_placements"][0]["position"]["y"] = PLACEMENT_FLOOR_TOLERANCE * 1.01
        with self.assertRaisesRegex(ValueError, "planar"):
            _validate_and_index_agent_placements(self.agent_roles, outside)


if __name__ == "__main__":
    unittest.main()
