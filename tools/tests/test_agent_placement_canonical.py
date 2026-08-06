from __future__ import annotations

import copy
import math
import unittest

from tools.case_study_pipeline.agent_placement import (
    MIN_AGENT_DISTANCE,
    PLACEMENT_ALGORITHM_VERSION,
    PLACEMENT_ARTIFACT_SCHEMA,
    PLACEMENT_ARTIFACT_SCHEMA_VERSION,
    PLACEMENT_FLOOR_TOLERANCE,
    AgentPlacementError,
    generate_agent_placements,
    placement_artifact_sha256,
    validate_agent_placements,
)


def _object(
    object_id: str,
    *,
    x: float,
    y: float = 0.5,
    z: float,
    width: float = 0.2,
    height: float = 1.0,
    depth: float = 0.2,
    yaw: float = 0.0,
) -> dict:
    return {
        "object_id": object_id,
        "object_type": "fixture",
        "group": "content",
        "position": {"x": x, "y": y, "z": z},
        "rotation": {"x": 0.0, "y": yaw, "z": 0.0},
        "dimensions": {"width": width, "height": height, "depth": depth},
    }


def _scene(*objects: dict, bounds: dict | None = None) -> dict:
    return {
        "room_bounds": bounds
        or {"min_x": -10.0, "max_x": 10.0, "min_z": -6.0, "max_z": 6.0},
        "objects": list(objects),
    }


def _roles(*agent_ids: str) -> dict:
    return {
        "agents": [
            {
                "id": agent_id,
                "display_name": agent_id,
                "responsible_zone_ids": [],
                "grounded_object_ids": [],
            }
            for agent_id in agent_ids
        ]
    }


def _placement(agent_id: str, *, x: float, z: float, forward: dict | None = None) -> dict:
    return {
        "id": agent_id,
        "position": {"x": x, "y": 0.0, "z": z},
        "forward": forward or {"x": 0.0, "y": 0.0, "z": 1.0},
    }


def _artifact(bounds: dict, placements: list[dict], *, origin: str = "deterministic") -> dict:
    return {
        "schema": PLACEMENT_ARTIFACT_SCHEMA,
        "schema_version": PLACEMENT_ARTIFACT_SCHEMA_VERSION,
        "placement_algorithm_version": PLACEMENT_ALGORITHM_VERSION,
        "origin": origin,
        "room_bounds": bounds,
        "agent_placements": placements,
    }


class CanonicalAgentPlacementTests(unittest.TestCase):
    def test_floor_slice_ignores_hanging_objects_but_blocks_floor_objects(self) -> None:
        roles = _roles("guide")
        bounds = {"min_x": -4.0, "max_x": 4.0, "min_z": -4.0, "max_z": 4.0}
        payload = _artifact(bounds, [_placement("guide", x=0.0, z=0.0)])

        hanging_scene = _scene(
            _object("picture", x=0.0, y=2.0, z=0.0, width=3.0, height=0.5, depth=1.0),
            bounds=bounds,
        )
        self.assertEqual(
            "valid",
            validate_agent_placements(payload, normalized_scene=hanging_scene, agent_roles=roles)["status"],
        )

        floor_scene = _scene(
            _object("cabinet", x=0.0, y=0.5, z=0.0, width=3.0, height=1.0, depth=1.0),
            bounds=bounds,
        )
        result = validate_agent_placements(payload, normalized_scene=floor_scene, agent_roles=roles)
        self.assertEqual("invalid", result["status"])
        self.assertEqual(1, result["metrics"]["obstacle_overlap_count"])

        unknown_height_scene = _scene(
            _object("room_plan_fixture", x=0.0, y=0.0, z=0.0, width=3.0, height=0.0, depth=1.0),
            bounds=bounds,
        )
        unknown_height = validate_agent_placements(
            payload,
            normalized_scene=unknown_height_scene,
            agent_roles=roles,
        )
        self.assertEqual("invalid", unknown_height["status"])
        self.assertEqual(1, unknown_height["metrics"]["obstacle_overlap_count"])

    def test_yaw_rotated_obstacle_uses_exact_oriented_footprint(self) -> None:
        roles = _roles("guide")
        scene = _scene(_object("diagonal", x=0.0, z=0.0, width=4.0, depth=0.2, yaw=45.0))

        # Unity/MLDS +45 degree yaw places the long axis along x=-z.
        overlap_payload = _artifact(
            scene["room_bounds"],
            [_placement("guide", x=1.0, z=-1.0)],
        )
        overlap = validate_agent_placements(overlap_payload, normalized_scene=scene, agent_roles=roles)
        self.assertEqual("invalid", overlap["status"])
        self.assertEqual(1, overlap["metrics"]["obstacle_overlap_count"])

        # This point lies inside the rotated AABB envelope, but outside the
        # actual thin oriented rectangle (including avatar padding).
        clear_payload = _artifact(
            scene["room_bounds"],
            [_placement("guide", x=1.0, z=1.0)],
        )
        clear = validate_agent_placements(clear_payload, normalized_scene=scene, agent_roles=roles)
        self.assertEqual("valid", clear["status"], clear["errors"])

    def test_primary_zone_uses_geometry_medoid_instead_of_remote_mean(self) -> None:
        scene = _scene(
            _object("left_outer", x=-8.0, z=0.0),
            _object("left_medoid", x=-7.0, z=0.0),
            _object("left_outlier", x=2.0, z=0.0),
            _object("remote", x=9.0, z=0.0),
            bounds={"min_x": -12.0, "max_x": 12.0, "min_z": -5.0, "max_z": 5.0},
        )
        semantics = {
            "semantic_zones": [
                {
                    "zone_id": "primary",
                    "object_ids": ["left_outer", "left_medoid", "left_outlier"],
                    "centroid_xz": {"x": 99.0, "z": 99.0},
                },
                {
                    "zone_id": "remote",
                    "object_ids": ["remote"],
                    "centroid_xz": {"x": 9.0, "z": 0.0},
                },
            ]
        }
        roles = {
            "agents": [
                {
                    "id": "guide",
                    "responsible_zone_ids": ["primary", "remote"],
                    "grounded_object_ids": ["left_outer", "left_medoid", "left_outlier", "remote"],
                }
            ]
        }

        generated = generate_agent_placements(
            normalized_scene=scene,
            scene_semantics=semantics,
            agent_roles=roles,
        )
        self.assertEqual(PLACEMENT_ALGORITHM_VERSION, generated["placement_algorithm_version"])
        self.assertEqual(PLACEMENT_ARTIFACT_SCHEMA_VERSION, generated["schema_version"])
        self.assertEqual("deterministic", generated["origin"])
        target = generated["agent_placements"][0]["target_xz"]
        self.assertEqual({"x": -7.0, "z": 0.0}, target)

    def test_generation_is_order_independent_and_keeps_one_meter_distance(self) -> None:
        scene = _scene(bounds={"min_x": -4.0, "max_x": 4.0, "min_z": -4.0, "max_z": 4.0})
        roles = _roles("charlie", "alpha", "bravo")
        generated = generate_agent_placements(
            normalized_scene=scene,
            scene_semantics={"semantic_zones": []},
            agent_roles=roles,
        )

        reversed_roles = copy.deepcopy(roles)
        reversed_roles["agents"].reverse()
        reversed_generated = generate_agent_placements(
            normalized_scene=scene,
            scene_semantics={"semantic_zones": []},
            agent_roles=reversed_roles,
        )
        by_id = {item["id"]: item for item in generated["agent_placements"]}
        reversed_by_id = {item["id"]: item for item in reversed_generated["agent_placements"]}
        self.assertEqual(
            {agent_id: item["position"] for agent_id, item in by_id.items()},
            {agent_id: item["position"] for agent_id, item in reversed_by_id.items()},
        )

        positions = [(item["position"]["x"], item["position"]["z"]) for item in by_id.values()]
        distances = [
            math.dist(left, right)
            for index, left in enumerate(positions)
            for right in positions[index + 1 :]
        ]
        self.assertGreaterEqual(min(distances), MIN_AGENT_DISTANCE)
        for item in by_id.values():
            forward = item["forward"]
            self.assertTrue(all(math.isfinite(forward[key]) for key in ("x", "y", "z")))
            self.assertAlmostEqual(
                1.0,
                math.sqrt(forward["x"] ** 2 + forward["y"] ** 2 + forward["z"] ** 2),
                places=12,
            )

        validation = validate_agent_placements(generated, normalized_scene=scene, agent_roles=roles)
        self.assertEqual("valid", validation["status"], validation["errors"])
        self.assertEqual(PLACEMENT_ALGORITHM_VERSION, validation["placement_algorithm_version"])
        self.assertEqual(placement_artifact_sha256(generated), validation["placement_artifact_sha256"])
        self.assertGreaterEqual(validation["metrics"]["minimum_agent_distance"], MIN_AGENT_DISTANCE)

    def test_non_finite_or_non_normalized_forward_is_rejected(self) -> None:
        scene = _scene()
        roles = _roles("guide")
        for forward in (
            {"x": math.nan, "y": 0.0, "z": 1.0},
            {"x": 2.0, "y": 0.0, "z": 0.0},
            {"x": 0.0, "y": 0.5, "z": math.sqrt(0.75)},
        ):
            with self.subTest(forward=forward):
                payload = _artifact(
                    scene["room_bounds"],
                    [_placement("guide", x=0.0, z=0.0, forward=forward)],
                )
                result = validate_agent_placements(payload, normalized_scene=scene, agent_roles=roles)
                self.assertEqual("invalid", result["status"])
                self.assertTrue(any("forward vector" in error for error in result["errors"]))

    def test_contract_origin_and_json_number_types_are_strict(self) -> None:
        scene = _scene()
        roles = _roles("guide")
        valid = _artifact(scene["room_bounds"], [_placement("guide", x=0.0, z=0.0)])
        manual = copy.deepcopy(valid)
        manual["origin"] = "wizard_manual"
        self.assertEqual(
            "valid",
            validate_agent_placements(manual, normalized_scene=scene, agent_roles=roles)["status"],
        )

        mutations = (
            ("schema", "wrong"),
            ("schema_version", "1.0"),
            ("placement_algorithm_version", "1.0.0"),
            ("origin", None),
            ("origin", "legacy"),
        )
        for field, value in mutations:
            with self.subTest(field=field, value=value):
                invalid = copy.deepcopy(valid)
                if value is None:
                    invalid.pop(field)
                else:
                    invalid[field] = value
                report = validate_agent_placements(invalid, normalized_scene=scene, agent_roles=roles)
                self.assertEqual("invalid", report["status"])
                self.assertIsNone(report["placement_artifact_sha256"])

        for field, value in (("position", True), ("position", "0.0"), ("forward", True), ("forward", "0.0")):
            with self.subTest(vector=field, value=value):
                invalid = copy.deepcopy(valid)
                invalid["agent_placements"][0][field]["x"] = value
                report = validate_agent_placements(invalid, normalized_scene=scene, agent_roles=roles)
                self.assertEqual("invalid", report["status"])
                self.assertIsNone(report["placement_artifact_sha256"])

    def test_floor_tolerance_and_artifact_hash_are_stable(self) -> None:
        scene = _scene()
        roles = _roles("guide")
        payload = _artifact(scene["room_bounds"], [_placement("guide", x=0.0, z=0.0)])
        payload["agent_placements"][0]["position"]["y"] = PLACEMENT_FLOOR_TOLERANCE
        report = validate_agent_placements(payload, normalized_scene=scene, agent_roles=roles)
        self.assertEqual("valid", report["status"], report["errors"])
        self.assertEqual(placement_artifact_sha256(payload), report["placement_artifact_sha256"])

        reordered = {key: payload[key] for key in reversed(list(payload))}
        self.assertEqual(placement_artifact_sha256(payload), placement_artifact_sha256(reordered))

        outside = copy.deepcopy(payload)
        outside["agent_placements"][0]["position"]["y"] = PLACEMENT_FLOOR_TOLERANCE * 1.01
        outside_report = validate_agent_placements(outside, normalized_scene=scene, agent_roles=roles)
        self.assertEqual("invalid", outside_report["status"])

    def test_infeasible_room_raises_explicit_agent_error(self) -> None:
        bounds = {"min_x": -1.0, "max_x": 1.0, "min_z": -1.0, "max_z": 1.0}
        scene = _scene(
            _object("blocking_box", x=0.0, z=0.0, width=2.0, height=1.0, depth=2.0),
            bounds=bounds,
        )
        with self.assertRaisesRegex(AgentPlacementError, "Unable to place agent 'trapped'.*No valid floor position"):
            generate_agent_placements(
                normalized_scene=scene,
                scene_semantics={"semantic_zones": []},
                agent_roles=_roles("trapped"),
            )


if __name__ == "__main__":
    unittest.main()
