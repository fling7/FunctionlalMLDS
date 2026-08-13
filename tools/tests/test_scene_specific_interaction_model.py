"""Focused coverage for scene-specific FunctionalMLDS interaction chains."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
for import_root in (ROOT, TOOLS):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from dynamic_functional_mlds_v2_compat import import_v05  # noqa: E402
from case_study_pipeline.functionalmlds_assembler import (  # noqa: E402
    assemble_functionalmlds_instance,
    validate_functionalmlds_instance,
)
from case_study_pipeline.functionalmlds_v2_assembler import (  # noqa: E402
    _build_native_instance,
    validate_functionalmlds_v2_instance,
)


CASE_IDS = (
    "bestfit_career_fair",
    "classroom_dinosaur",
    "steinpilz_brand_room",
)
EXPECTED_GROUNDED_ASSET_COUNTS = {
    "bestfit_career_fair": 27,
    "classroom_dinosaur": 36,
    "steinpilz_brand_room": 30,
}


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _assemble(case_id: str) -> tuple[dict, dict, dict, dict]:
    intermediate = ROOT / "output" / "case_studies" / case_id / "intermediate"
    normalized_scene = _read(intermediate / "scene_graph.normalized.json")
    scene_semantics = _read(intermediate / "scene_semantics.json")
    agent_roles = _read(intermediate / "agent_roles.generated.json")
    instance = assemble_functionalmlds_instance(
        case_id=case_id,
        normalized_scene=normalized_scene,
        scene_semantics=scene_semantics,
        agent_roles=agent_roles,
    )
    return instance, normalized_scene, scene_semantics, agent_roles


def _objects_by_type(instance: dict, type_name: str) -> list[dict]:
    return [
        item
        for item in instance.get("objects") or []
        if item.get("type") == type_name
    ]


class SceneSpecificInteractionModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v05_by_case = {
            case_id: _assemble(case_id)[0]
            for case_id in CASE_IDS
        }
        cls.classroom_v2 = _build_native_instance(
            import_v05(cls.v05_by_case["classroom_dinosaur"])
        )

    def test_each_grounded_asset_has_one_explicit_provider_target_chain(self) -> None:
        observed_shapes: set[tuple[int, int, int]] = set()
        for case_id, instance in self.v05_by_case.items():
            with self.subTest(case_id=case_id):
                report = validate_functionalmlds_instance(instance)
                self.assertEqual("valid", report["status"], report["errors"])

                interactions = [
                    use_case
                    for use_case in instance["requirementsModel"]["useCases"]
                    if "-INTERACT-" in use_case["id"]
                ]
                expected_count = EXPECTED_GROUNDED_ASSET_COUNTS[case_id]
                self.assertEqual(expected_count, len(interactions))

                uses = {
                    item["id"]: item
                    for item in instance["capabilityUses"]
                    if item.get("preferred_provider_entity_id")
                    and item.get("target_entity_ids")
                }
                self.assertEqual(expected_count * 2, len(uses))
                generic_uses = [
                    item
                    for item in instance["capabilityUses"]
                    if not item.get("target_entity_ids")
                    and item["id"].endswith(
                        (
                            "S11-ANSWER-ROOM-GROUNDED-QUESTION",
                            "S12-HANDOFF-TO-RESPONSIBLE-AGENT",
                        )
                    )
                ]
                self.assertEqual(2, len(generic_uses))
                self.assertEqual(
                    expected_count,
                    len(
                        {
                            next(
                                target_id
                                for target_id in use["target_entity_ids"]
                                if target_id.startswith("ENT-ASSET-")
                            )
                            for use in uses.values()
                        }
                    ),
                )
                for use_case in interactions:
                    scenario = use_case["scenarios"][0]
                    self.assertEqual("main", scenario["kind"])
                    self.assertEqual(3, len(scenario["steps"]))
                    for step in scenario["steps"][1:]:
                        self.assertEqual(1, len(step["capabilityUseIds"]))
                        use = uses[step["capabilityUseIds"][0]]
                        self.assertTrue(use["preferred_provider_entity_id"].startswith("ENT-AGENT-"))
                        self.assertTrue(
                            any(
                                target_id.startswith("ENT-ASSET-")
                                for target_id in use["target_entity_ids"]
                            )
                        )
                first_object_id = next(
                    obj["object_id"]
                    for obj in _assemble(case_id)[1]["objects"]
                    if any(
                        obj["object_id"] in (agent.get("grounded_object_ids") or [])
                        for agent in _assemble(case_id)[3]["agents"]
                    )
                )
                first_token = first_object_id.upper().replace("-", "_")
                self.assertIn(
                    f"CU-{case_id.upper()}-INTERACT-{first_token}-ANSWER-ROOM-GROUNDED-QUESTION",
                    uses,
                )

                observed_shapes.add(
                    (
                        len(instance["requirementsModel"]["useCases"]),
                        len(instance["capabilityUses"]),
                        len(instance["validationCases"]),
                    )
                )
        self.assertEqual(3, len(observed_shapes))

    def test_dinosaur_chain_projects_exact_provider_asset_group_and_zone(self) -> None:
        use_id = (
            "CU-CLASSROOM_DINOSAUR-INTERACT-DINOSAUR_SKELETON-"
            "ANSWER-ROOM-GROUNDED-QUESTION"
        )
        v05_use = next(
            item
            for item in self.v05_by_case["classroom_dinosaur"]["capabilityUses"]
            if item["id"] == use_id
        )
        expected_provider = "ENT-AGENT-EXHIBIT_INTERPRETER"
        expected_targets = [
            "ENT-ASSET-DINOSAUR_SKELETON",
            "ENT-GROUP-DECOR",
            "ENT-ZONE-DINOSAUR_DISPLAY_ZONE",
        ]
        self.assertEqual(expected_provider, v05_use["preferred_provider_entity_id"])
        self.assertEqual(expected_targets, v05_use["target_entity_ids"])

        by_id = {
            item["id"]: item
            for item in self.classroom_v2["objects"]
        }
        native_use = by_id[use_id]
        self.assertEqual([expected_provider], native_use["provider"])
        self.assertEqual(expected_targets, native_use["target"])
        native_step = next(
            step
            for step in _objects_by_type(self.classroom_v2, "ScenarioStep")
            if use_id in step["capabilityUse"]
        )
        self.assertEqual(
            "STEP-CLASSROOM_DINOSAUR-INTERACT-DINOSAUR_SKELETON-ANSWER",
            native_step["id"],
        )
        self.assertEqual([expected_provider], native_step["performedBy"])

        native_by_id = {
            item["id"]: item for item in self.classroom_v2["objects"]
        }
        self.assertEqual(
            [],
            native_by_id[
                "CU-CLASSROOM_DINOSAUR-S11-ANSWER-ROOM-GROUNDED-QUESTION"
            ]["target"],
        )
        self.assertEqual(
            [],
            native_by_id[
                "CU-CLASSROOM_DINOSAUR-S12-HANDOFF-TO-RESPONSIBLE-AGENT"
            ]["target"],
        )

    def test_native_validator_rejects_dinosaur_provider_target_mismatch(self) -> None:
        mutated = copy.deepcopy(self.classroom_v2)
        use_id = (
            "CU-CLASSROOM_DINOSAUR-INTERACT-DINOSAUR_SKELETON-"
            "ANSWER-ROOM-GROUNDED-QUESTION"
        )
        native_use = next(
            item for item in mutated["objects"] if item.get("id") == use_id
        )
        native_use["target"] = [
            target_id
            for target_id in native_use["target"]
            if target_id != "ENT-ASSET-DINOSAUR_SKELETON"
        ]

        report = validate_functionalmlds_v2_instance(mutated)

        self.assertEqual("invalid", report["status"])
        self.assertIn(
            "IUI-DOMAIN-TARGET",
            {issue.get("code") for issue in report["errors"]},
        )

    def test_native_agents_preserve_modeled_handoff_targets(self) -> None:
        source_agents = {
            item["source_agent_id"]: item
            for item in self.v05_by_case["classroom_dinosaur"]["agents"]
        }
        native_agents = {
            item.get("sourceAgentId"): item
            for item in self.classroom_v2["objects"]
            if item.get("type") == "Agent"
        }
        native_agents_by_id = {
            item["id"]: item
            for item in self.classroom_v2["objects"]
            if item.get("type") == "Agent"
        }
        for source_id, source in source_agents.items():
            with self.subTest(source_id=source_id):
                expected = source.get("handoff_targets") or []
                actual = native_agents[source_id].get("handoffTarget") or []
                self.assertEqual(len(expected), len(actual))
                self.assertEqual(
                    expected,
                    [
                        native_agents_by_id[next_id]["sourceAgentId"]
                        for next_id in actual
                    ],
                )

    def test_competing_asset_owner_fails_closed_without_group_or_zone_fallback(self) -> None:
        _, normalized_scene, scene_semantics, agent_roles = _assemble(
            "classroom_dinosaur"
        )
        mutated_roles = copy.deepcopy(agent_roles)
        mutated_roles["agents"][0]["grounded_object_ids"].append(
            "dinosaur_skeleton"
        )

        with self.assertRaisesRegex(
            ValueError,
            "dinosaur_skeleton has ambiguous asset owners",
        ):
            assemble_functionalmlds_instance(
                case_id="classroom_dinosaur",
                normalized_scene=normalized_scene,
                scene_semantics=scene_semantics,
                agent_roles=mutated_roles,
            )

    def test_unowned_scene_group_is_not_promoted_to_runtime_contract(self) -> None:
        _, normalized_scene, scene_semantics, agent_roles = _assemble(
            "classroom_dinosaur"
        )
        mutated_scene = copy.deepcopy(normalized_scene)
        exemplar = copy.deepcopy(mutated_scene["objects"][0])
        exemplar.update(
            {
                "object_id": "unowned_prop",
                "object_type": "unowned_prop",
                "group": "unowned_group",
            }
        )
        mutated_scene["objects"].append(exemplar)

        instance = assemble_functionalmlds_instance(
            case_id="classroom_dinosaur",
            normalized_scene=mutated_scene,
            scene_semantics=scene_semantics,
            agent_roles=agent_roles,
        )

        entity_ids = {entity["id"] for entity in instance["entities"]}
        self.assertNotIn("ENT-GROUP-UNOWNED_GROUP", entity_ids)
        report = validate_functionalmlds_instance(instance)
        self.assertEqual("valid", report["status"], report["errors"])


if __name__ == "__main__":
    unittest.main()
