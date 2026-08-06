from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .common import read_json, update_manifest, write_json
from .mlds_ingestion import is_structural_object


MIN_AGENT_DISTANCE = 0.75
OBJECT_PADDING = 0.45
WALL_MARGIN = 0.45


def _distance_xz(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def _normalize_vec_xz(dx: float, dz: float) -> Dict[str, float]:
    length = math.sqrt(dx * dx + dz * dz)
    if length < 1e-6:
        return {"x": 0.0, "y": 0.0, "z": 1.0}
    return {"x": round(dx / length, 4), "y": 0.0, "z": round(dz / length, 4)}


def _room_center(bounds: Dict[str, float]) -> Tuple[float, float]:
    return ((bounds["min_x"] + bounds["max_x"]) / 2.0, (bounds["min_z"] + bounds["max_z"]) / 2.0)


def _object_bounds(obj: Dict[str, Any]) -> Tuple[float, float, float, float]:
    pos = obj.get("position") or {}
    dims = obj.get("dimensions") or {}
    x = float(pos.get("x", 0.0))
    z = float(pos.get("z", 0.0))
    width = max(float(dims.get("width", 0.0) or 0.0), 0.2)
    depth = max(float(dims.get("depth", 0.0) or 0.0), 0.2)
    return (x - width / 2.0, x + width / 2.0, z - depth / 2.0, z + depth / 2.0)


def _inside_bounds(x: float, z: float, bounds: Dict[str, float]) -> bool:
    return (
        bounds["min_x"] + WALL_MARGIN <= x <= bounds["max_x"] - WALL_MARGIN
        and bounds["min_z"] + WALL_MARGIN <= z <= bounds["max_z"] - WALL_MARGIN
    )


def _inside_obstacle(x: float, z: float, obstacles: Sequence[Tuple[float, float, float, float]]) -> bool:
    for min_x, max_x, min_z, max_z in obstacles:
        if min_x - OBJECT_PADDING <= x <= max_x + OBJECT_PADDING and min_z - OBJECT_PADDING <= z <= max_z + OBJECT_PADDING:
            return True
    return False


def _too_close_to_agents(x: float, z: float, placed: Sequence[Dict[str, Any]]) -> bool:
    for placement in placed:
        pos = placement.get("position") or {}
        if _distance_xz((x, z), (float(pos.get("x", 0.0)), float(pos.get("z", 0.0)))) < MIN_AGENT_DISTANCE:
            return True
    return False


def _is_valid_position(
    x: float,
    z: float,
    *,
    bounds: Dict[str, float],
    obstacles: Sequence[Tuple[float, float, float, float]],
    placed: Sequence[Dict[str, Any]],
) -> bool:
    return _inside_bounds(x, z, bounds) and not _inside_obstacle(x, z, obstacles) and not _too_close_to_agents(x, z, placed)


def _clamp_to_room(x: float, z: float, bounds: Dict[str, float]) -> Tuple[float, float]:
    return (
        max(bounds["min_x"] + WALL_MARGIN, min(bounds["max_x"] - WALL_MARGIN, x)),
        max(bounds["min_z"] + WALL_MARGIN, min(bounds["max_z"] - WALL_MARGIN, z)),
    )


def _spiral_search(
    target: Tuple[float, float],
    *,
    bounds: Dict[str, float],
    obstacles: Sequence[Tuple[float, float, float, float]],
    placed: Sequence[Dict[str, Any]],
) -> Tuple[float, float]:
    start_x, start_z = _clamp_to_room(target[0], target[1], bounds)
    if _is_valid_position(start_x, start_z, bounds=bounds, obstacles=obstacles, placed=placed):
        return start_x, start_z

    radius = 0.45
    while radius <= 6.5:
        for index in range(24):
            angle = (2.0 * math.pi * index) / 24.0
            x, z = _clamp_to_room(start_x + math.cos(angle) * radius, start_z + math.sin(angle) * radius, bounds)
            if _is_valid_position(x, z, bounds=bounds, obstacles=obstacles, placed=placed):
                return x, z
        radius += 0.35
    return start_x, start_z


def _object_lookup(normalized_scene: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    result = {}
    for obj in normalized_scene.get("objects") or []:
        if isinstance(obj, dict) and obj.get("object_id"):
            result[str(obj["object_id"])] = obj
    return result


def _zone_centroids(scene_semantics: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
    result = {}
    for zone in scene_semantics.get("semantic_zones") or []:
        if not isinstance(zone, dict):
            continue
        centroid = zone.get("centroid_xz") or {}
        zone_id = str(zone.get("zone_id") or "")
        if zone_id:
            result[zone_id] = (float(centroid.get("x", 0.0)), float(centroid.get("z", 0.0)))
    return result


def _agent_target(
    agent: Dict[str, Any],
    *,
    object_lookup: Dict[str, Dict[str, Any]],
    zone_centroids: Dict[str, Tuple[float, float]],
    room_center: Tuple[float, float],
) -> Tuple[float, float]:
    points: List[Tuple[float, float]] = []
    for zone_id in agent.get("responsible_zone_ids") or []:
        if zone_id in zone_centroids:
            points.append(zone_centroids[zone_id])
    for object_id in agent.get("grounded_object_ids") or []:
        obj = object_lookup.get(str(object_id))
        if not obj:
            continue
        pos = obj.get("position") or {}
        points.append((float(pos.get("x", 0.0)), float(pos.get("z", 0.0))))
    if not points:
        return room_center
    return (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))


def generate_agent_placements(
    *,
    normalized_scene: Dict[str, Any],
    scene_semantics: Dict[str, Any],
    agent_roles: Dict[str, Any],
) -> Dict[str, Any]:
    bounds = normalized_scene.get("room_bounds") or {"min_x": -5.0, "max_x": 5.0, "min_z": -5.0, "max_z": 5.0}
    center = _room_center(bounds)
    object_lookup = _object_lookup(normalized_scene)
    zone_centroids = _zone_centroids(scene_semantics)
    obstacles = [
        _object_bounds(obj)
        for obj in normalized_scene.get("objects") or []
        if isinstance(obj, dict) and not is_structural_object(obj)
    ]
    placed: List[Dict[str, Any]] = []
    for agent in agent_roles.get("agents") or []:
        if not isinstance(agent, dict):
            continue
        target = _agent_target(agent, object_lookup=object_lookup, zone_centroids=zone_centroids, room_center=center)
        # Stand slightly toward the room center from the target to avoid sitting on the represented object.
        direction_to_center = _normalize_vec_xz(center[0] - target[0], center[1] - target[1])
        preferred = (target[0] + direction_to_center["x"] * 1.25, target[1] + direction_to_center["z"] * 1.25)
        x, z = _spiral_search(preferred, bounds=bounds, obstacles=obstacles, placed=placed)
        forward = _normalize_vec_xz(target[0] - x, target[1] - z)
        placed.append(
            {
                "id": agent.get("id"),
                "display_name": agent.get("display_name") or agent.get("id"),
                "position": {"x": round(x, 3), "y": 0.0, "z": round(z, 3)},
                "forward": forward,
                "target_xz": {"x": round(target[0], 3), "z": round(target[1], 3)},
                "responsible_zone_ids": agent.get("responsible_zone_ids") or [],
                "grounded_object_ids": agent.get("grounded_object_ids") or [],
            }
        )
    return {"room_bounds": bounds, "agent_placements": placed}


def _minimum_agent_distance(placements: List[Dict[str, Any]]) -> Optional[float]:
    if len(placements) < 2:
        return None
    distances = []
    for i, left in enumerate(placements):
        left_pos = left.get("position") or {}
        for right in placements[i + 1 :]:
            right_pos = right.get("position") or {}
            distances.append(
                _distance_xz(
                    (float(left_pos.get("x", 0.0)), float(left_pos.get("z", 0.0))),
                    (float(right_pos.get("x", 0.0)), float(right_pos.get("z", 0.0))),
                )
            )
    return min(distances) if distances else None


def validate_agent_placements(
    placements_payload: Dict[str, Any],
    *,
    normalized_scene: Dict[str, Any],
    agent_roles: Dict[str, Any],
) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    bounds = placements_payload.get("room_bounds") or normalized_scene.get("room_bounds")
    if not bounds:
        errors.append("room_bounds are missing.")
        bounds = {"min_x": -5.0, "max_x": 5.0, "min_z": -5.0, "max_z": 5.0}
    obstacles = [
        _object_bounds(obj)
        for obj in normalized_scene.get("objects") or []
        if isinstance(obj, dict) and not is_structural_object(obj)
    ]
    placements = placements_payload.get("agent_placements") or []
    expected_agent_ids = {str(agent.get("id")) for agent in agent_roles.get("agents") or [] if isinstance(agent, dict)}
    actual_agent_ids: Set[str] = set()
    obstacle_overlaps = 0
    out_of_bounds = 0

    if len(placements) != len(expected_agent_ids):
        errors.append(f"Expected {len(expected_agent_ids)} placements, got {len(placements)}.")

    for index, placement in enumerate(placements):
        agent_id = str(placement.get("id") or "")
        actual_agent_ids.add(agent_id)
        if agent_id not in expected_agent_ids:
            errors.append(f"agent_placements[{index}] references unknown agent id: {agent_id}.")
        pos = placement.get("position") or {}
        forward = placement.get("forward") or {}
        x = float(pos.get("x", 0.0))
        z = float(pos.get("z", 0.0))
        if not _inside_bounds(x, z, bounds):
            out_of_bounds += 1
            errors.append(f"agent_placements[{index}] is outside room bounds.")
        if _inside_obstacle(x, z, obstacles):
            obstacle_overlaps += 1
            errors.append(f"agent_placements[{index}] overlaps an obstacle footprint.")
        if abs(float(forward.get("x", 0.0))) + abs(float(forward.get("z", 0.0))) < 0.1:
            errors.append(f"agent_placements[{index}] has an invalid forward vector.")

    missing_agents = sorted(expected_agent_ids - actual_agent_ids)
    if missing_agents:
        errors.append("Missing placements for agents: " + ", ".join(missing_agents))

    min_distance = _minimum_agent_distance(placements)
    if min_distance is not None and min_distance < MIN_AGENT_DISTANCE:
        errors.append(f"Minimum agent distance is too small: {min_distance:.3f}.")

    return {
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "agent_count": len(expected_agent_ids),
            "placement_count": len(placements),
            "out_of_bounds_count": out_of_bounds,
            "obstacle_overlap_count": obstacle_overlaps,
            "minimum_agent_distance": round(min_distance, 4) if min_distance is not None else None,
        },
    }


def run_agent_placement_for_case(case_dir: Path) -> Dict[str, Any]:
    case_dir = case_dir.resolve()
    normalized_path = case_dir / "intermediate" / "scene_graph.normalized.json"
    semantics_path = case_dir / "intermediate" / "scene_semantics.json"
    agent_roles_path = case_dir / "intermediate" / "agent_roles.generated.json"
    placements_path = case_dir / "intermediate" / "agent_placements.json"
    validation_path = case_dir / "validation" / "agent_placement_validation.json"

    normalized_scene = read_json(normalized_path)
    scene_semantics = read_json(semantics_path)
    agent_roles = read_json(agent_roles_path)
    placements = generate_agent_placements(
        normalized_scene=normalized_scene,
        scene_semantics=scene_semantics,
        agent_roles=agent_roles,
    )
    validation = validate_agent_placements(
        placements,
        normalized_scene=normalized_scene,
        agent_roles=agent_roles,
    )
    write_json(placements_path, placements)
    write_json(validation_path, validation)
    status = "success" if validation["status"] == "valid" else "needs_manual_review"
    update_manifest(
        case_dir,
        stage_id="agent_placement",
        status=status,
        input_paths=[normalized_path, semantics_path, agent_roles_path],
        output_paths=[placements_path, validation_path],
        errors=validation.get("errors"),
        warnings=validation.get("warnings"),
        metadata=validation.get("metrics"),
    )
    return {
        "case_id": case_dir.name,
        "status": status,
        "validation": validation,
        "placements_path": str(placements_path),
        "validation_path": str(validation_path),
    }
