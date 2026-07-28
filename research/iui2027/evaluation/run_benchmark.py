from __future__ import annotations

"""Run the deterministic IUI 2027 structural system benchmark.

The benchmark deliberately evaluates model structure, routing reachability and
validator behavior.  It does not call an LLM, start Unity, or assign scores to
answer meaning or user experience.
"""

import argparse
import copy
import hashlib
import importlib.metadata
import json
import platform
import statistics
import subprocess
import sys
import time
from collections import Counter, deque
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.case_study_pipeline.project_materializer import (  # noqa: E402
    _validate_v2_agent_provider_contract,
)
from tools.case_study_pipeline.functionalmlds_v2_assembler import (  # noqa: E402
    assemble_v2_instance,
)
from tools.dynamic_functional_mlds_v2_model import MODEL  # noqa: E402
from tools.validate_dynamic_functional_mlds_v2 import validate_instance  # noqa: E402


BENCHMARK_SCHEMA = "iui2027_structural_system_benchmark"
BENCHMARK_VERSION = "1.1.0"
CASE_IDS = (
    "bestfit_career_fair",
    "classroom_dinosaur",
    "steinpilz_brand_room",
)
VALIDATOR_SOURCE_PATHS = (
    Path("tools/dynamic_functional_mlds_v2_model.py"),
    Path("tools/validate_dynamic_functional_mlds_v2.py"),
    Path("tools/case_study_pipeline/project_materializer.py"),
    Path("tools/case_study_pipeline/functionalmlds_v2_assembler.py"),
    Path("research/iui2027/evaluation/run_benchmark.py"),
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_text(payload: Any) -> str:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _refs(value: Any) -> list[str]:
    if value is None:
        return []
    raw = value if isinstance(value, list) else [value]
    return [str(item).strip() for item in raw if str(item).strip()]


def _typed(instance: Mapping[str, Any], type_name: str) -> list[dict[str, Any]]:
    return [
        dict(item)
        for item in instance.get("objects") or []
        if isinstance(item, Mapping) and item.get("type") == type_name
    ]


def _entities_with_role(
    instance: Mapping[str, Any],
    role: str,
) -> list[dict[str, Any]]:
    return sorted(
        (
            dict(item)
            for item in instance.get("objects") or []
            if isinstance(item, Mapping)
            and item.get("type") == "Entity"
            and item.get("entityRole") == role
        ),
        key=lambda item: str(item.get("id") or ""),
    )


def _case_paths(repo_root: Path, case_id: str) -> dict[str, Path]:
    case_dir = repo_root / "output" / "case_studies" / case_id
    return {
        "case_dir": case_dir,
        "v2": case_dir
        / "functionalmlds"
        / "functionalmlds.v2.instance.json",
        "assembly_report": case_dir
        / "functionalmlds"
        / "functionalmlds.v2.assembly_report.json",
        "agent_roles": case_dir
        / "intermediate"
        / "agent_roles.generated.json",
        "scene_semantics": case_dir
        / "intermediate"
        / "scene_semantics.json",
        "handoff_matrix": case_dir
        / "intermediate"
        / "handoff_matrix.json",
        "v05": case_dir
        / "functionalmlds"
        / "functionalmlds.instance.generated.json",
    }


def _relative(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _corpus_record(
    repo_root: Path,
    case_id: str,
    paths: Mapping[str, Path],
    instance: Mapping[str, Any],
) -> dict[str, Any]:
    object_counts = Counter(
        str(item.get("type") or "")
        for item in instance.get("objects") or []
        if isinstance(item, Mapping)
    )
    assembly_report = _read_json(paths["assembly_report"])
    return {
        "case_id": case_id,
        "v2_path": _relative(repo_root, paths["v2"]),
        "v2_sha256": _sha256(paths["v2"]),
        "v2_bytes": paths["v2"].stat().st_size,
        "agent_roles_path": _relative(repo_root, paths["agent_roles"]),
        "agent_roles_sha256": _sha256(paths["agent_roles"]),
        "scene_semantics_path": _relative(
            repo_root,
            paths["scene_semantics"],
        ),
        "scene_semantics_sha256": _sha256(paths["scene_semantics"]),
        "handoff_matrix_path": _relative(
            repo_root,
            paths["handoff_matrix"],
        ),
        "handoff_matrix_sha256": _sha256(paths["handoff_matrix"]),
        "v05_path": _relative(repo_root, paths["v05"]),
        "v05_sha256": _sha256(paths["v05"]),
        "reference_label": {
            "expected_valid": (
                assembly_report.get("status") == "valid"
                and bool(assembly_report.get("ok"))
            ),
            "source": _relative(repo_root, paths["assembly_report"]),
            "source_sha256": _sha256(paths["assembly_report"]),
        },
        "counts": {
            "objects": len(instance.get("objects") or []),
            "agents": object_counts["Agent"],
            "scene_objects": len(_entities_with_role(instance, "sceneObject")),
            "object_groups": len(_entities_with_role(instance, "objectGroup")),
            "semantic_zones": len(_entities_with_role(instance, "semanticZone")),
            "capabilities": object_counts["Capability"],
            "capability_uses": object_counts["CapabilityUse"],
            "scenario_steps": object_counts["ScenarioStep"],
            "runtime_actions": object_counts["RuntimeAction"],
            "validation_cases": object_counts["ValidationCase"],
        },
        "object_type_counts": dict(sorted(object_counts.items())),
    }


def _owners_for_refs(
    agents: Sequence[Mapping[str, Any]],
    field: str,
    target_ids: Iterable[str],
) -> list[str]:
    targets = set(target_ids)
    return sorted(
        str(agent.get("id") or "")
        for agent in agents
        if targets.intersection(_refs(agent.get(field)))
    )


def _responsibility_records(
    instance: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    agents = sorted(_typed(instance, "Agent"), key=lambda item: item["id"])
    assets = _entities_with_role(instance, "sceneObject")
    groups = _entities_with_role(instance, "objectGroup")
    zones = _entities_with_role(instance, "semanticZone")

    records: list[dict[str, Any]] = []
    tier_counts: Counter[str] = Counter()
    resolution_counts: Counter[str] = Counter()
    for asset in assets:
        asset_id = str(asset["id"])
        source_id = str(asset.get("sourceId") or "")
        explicit_group_ids = _refs(asset.get("objectGroup"))
        inferred_group_ids = [
            str(group["id"])
            for group in groups
            if source_id in _refs(group.get("sourceObjectId"))
        ]
        group_ids = sorted(set(explicit_group_ids) | set(inferred_group_ids))
        zone_ids = sorted(
            str(zone["id"])
            for zone in zones
            if source_id in _refs(zone.get("sourceObjectId"))
        )
        candidates = {
            "asset": _owners_for_refs(agents, "groundedAsset", [asset_id]),
            "group": _owners_for_refs(
                agents,
                "groundedObjectGroup",
                group_ids,
            ),
            "zone": _owners_for_refs(agents, "responsibleZone", zone_ids),
        }
        selected_tier = next(
            (
                tier
                for tier in ("asset", "group", "zone")
                if candidates[tier]
            ),
            "unassigned",
        )
        owners = (
            candidates[selected_tier]
            if selected_tier != "unassigned"
            else []
        )
        resolution = (
            "unique"
            if len(owners) == 1
            else "ambiguous"
            if len(owners) > 1
            else "unassigned"
        )
        tier_counts[selected_tier] += 1
        resolution_counts[resolution] += 1
        records.append(
            {
                "asset_id": asset_id,
                "source_object_id": source_id,
                "object_group_ids": group_ids,
                "zone_ids": zone_ids,
                "candidate_owner_agent_ids": candidates,
                "selected_tier": selected_tier,
                "owner_agent_ids": owners,
                "resolution": resolution,
            }
        )

    denominator = len(records)
    metrics = {
        "scene_object_denominator": denominator,
        "selected_tier_counts": {
            tier: tier_counts[tier]
            for tier in ("asset", "group", "zone", "unassigned")
        },
        "resolution_counts": {
            state: resolution_counts[state]
            for state in ("unique", "ambiguous", "unassigned")
        },
        "unique_responsibility_rate": (
            round(resolution_counts["unique"] / denominator, 6)
            if denominator
            else None
        ),
    }
    return records, metrics


def _shortest_path(
    graph: Mapping[str, Sequence[str]],
    start: str,
    target: str,
) -> list[str] | None:
    if start == target:
        return [start]
    queue: deque[list[str]] = deque([[start]])
    visited = {start}
    while queue:
        path = queue.popleft()
        for neighbor in sorted(graph.get(path[-1], [])):
            if neighbor in visited:
                continue
            candidate = [*path, neighbor]
            if neighbor == target:
                return candidate
            visited.add(neighbor)
            queue.append(candidate)
    return None


def _routing_records(
    instance: Mapping[str, Any],
    responsibilities: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    agents = sorted(_typed(instance, "Agent"), key=lambda item: item["id"])
    agent_ids = [str(agent["id"]) for agent in agents]
    graph = {
        str(agent["id"]): sorted(_refs(agent.get("handoffTarget")))
        for agent in agents
    }
    probes: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    unique_target_probe_count = 0

    for responsibility in responsibilities:
        owners = list(responsibility["owner_agent_ids"])
        for start_agent_id in agent_ids:
            target_paths = [
                {
                    "target_agent_id": target,
                    "path": _shortest_path(graph, start_agent_id, target),
                }
                for target in owners
            ]
            if len(owners) == 0:
                status = "unassigned_target"
            elif len(owners) > 1:
                status = "ambiguous_target"
            else:
                unique_target_probe_count += 1
                path = target_paths[0]["path"]
                if path is None:
                    status = "rejected_unreachable"
                elif len(path) == 1:
                    status = "local_owner"
                elif len(path) == 2:
                    status = "direct_allowed"
                else:
                    status = "transitive_allowed"
            status_counts[status] += 1
            probes.append(
                {
                    "asset_id": responsibility["asset_id"],
                    "start_agent_id": start_agent_id,
                    "owner_agent_ids": owners,
                    "responsibility_resolution": responsibility["resolution"],
                    "status": status,
                    "target_paths": target_paths,
                }
            )

    binary_statuses = (
        "local_owner",
        "direct_allowed",
        "transitive_allowed",
        "rejected_unreachable",
    )
    one_hop_count = (
        status_counts["local_owner"] + status_counts["direct_allowed"]
    )
    graph_reachable_count = one_hop_count + status_counts["transitive_allowed"]
    metrics = {
        "routing_probe_denominator": len(probes),
        "definition": "one probe per sceneObject and modeled start Agent",
        "unique_target_probe_denominator": unique_target_probe_count,
        "status_counts": {
            status: status_counts[status]
            for status in (
                *binary_statuses,
                "ambiguous_target",
                "unassigned_target",
            )
        },
        "one_hop_structural_coverage": (
            round(one_hop_count / unique_target_probe_count, 6)
            if unique_target_probe_count
            else None
        ),
        "graph_reachability_coverage": (
            round(graph_reachable_count / unique_target_probe_count, 6)
            if unique_target_probe_count
            else None
        ),
        "answer_semantics_evaluated": False,
    }

    pair_denominator = len(agent_ids) * max(0, len(agent_ids) - 1)
    declared_edges = {
        (source, target)
        for source, targets in graph.items()
        for target in targets
        if source != target
    }
    reachable_pairs = {
        (source, target)
        for source in agent_ids
        for target in agent_ids
        if source != target and _shortest_path(graph, source, target) is not None
    }
    graph_metrics = {
        "ordered_agent_pair_denominator_excluding_self": pair_denominator,
        "declared_direct_handoff_count": len(declared_edges),
        "rejected_direct_pair_count": pair_denominator - len(declared_edges),
        "graph_reachable_pair_count": len(reachable_pairs),
        "graph_unreachable_pair_count": pair_denominator - len(reachable_pairs),
    }
    return probes, metrics, graph_metrics


def _priority_record(
    *,
    asset_id: str,
    asset_candidates: Iterable[str],
    group_candidates: Iterable[str],
    zone_candidates: Iterable[str],
) -> dict[str, Any]:
    candidates = {
        "asset": sorted(set(asset_candidates)),
        "group": sorted(set(group_candidates)),
        "zone": sorted(set(zone_candidates)),
    }
    selected_tier = next(
        (tier for tier in ("asset", "group", "zone") if candidates[tier]),
        "unassigned",
    )
    owners = (
        candidates[selected_tier] if selected_tier != "unassigned" else []
    )
    return {
        "asset_id": asset_id,
        "candidate_owner_agent_ids": candidates,
        "selected_tier": selected_tier,
        "owner_agent_ids": owners,
        "resolution": (
            "unique"
            if len(owners) == 1
            else "ambiguous"
            if len(owners) > 1
            else "unassigned"
        ),
    }


def _routing_from_adapter(
    *,
    agent_ids: Sequence[str],
    graph: Mapping[str, Sequence[str]],
    responsibilities: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []
    for responsibility in sorted(
        responsibilities,
        key=lambda item: str(item["asset_id"]),
    ):
        owners = list(responsibility["owner_agent_ids"])
        for start in sorted(agent_ids):
            paths = [
                {
                    "target_agent_id": target,
                    "path": _shortest_path(graph, start, target),
                }
                for target in owners
            ]
            if not owners:
                status = "unassigned_target"
            elif len(owners) > 1:
                status = "ambiguous_target"
            elif paths[0]["path"] is None:
                status = "rejected_unreachable"
            elif len(paths[0]["path"]) == 1:
                status = "local_owner"
            elif len(paths[0]["path"]) == 2:
                status = "direct_allowed"
            else:
                status = "transitive_allowed"
            probes.append(
                {
                    "asset_id": responsibility["asset_id"],
                    "start_agent_id": start,
                    "owner_agent_ids": owners,
                    "status": status,
                    "target_paths": paths,
                }
            )
    return probes


def _direct_wiring_adapter(
    *,
    scene_semantics: Mapping[str, Any],
    agent_roles: Mapping[str, Any],
    handoff_matrix: Mapping[str, Any],
    expected_asset_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    agents = [
        dict(item)
        for item in agent_roles.get("agents") or []
        if isinstance(item, Mapping)
    ]
    agent_ids = sorted(str(agent.get("id") or "") for agent in agents)
    zones = [
        dict(item)
        for item in scene_semantics.get("semantic_zones") or []
        if isinstance(item, Mapping)
    ]
    zone_referenced_assets = {
        str(object_id)
        for zone in zones
        for object_id in zone.get("object_ids") or []
        if str(object_id)
    }
    grounded_assets = {
        str(object_id)
        for agent in agents
        for object_id in agent.get("grounded_object_ids") or []
        if str(object_id)
    }
    observed_assets = zone_referenced_assets | grounded_assets
    asset_ids = sorted(
        set(expected_asset_ids)
        if expected_asset_ids is not None
        # The executable direct-wiring surface is the set of objects assigned
        # to at least one Agent. Scene-semantics may additionally contain
        # zone-only navigation/decorative references that are not routeable
        # objects and have no V2 sceneObject counterpart.
        else grounded_assets
    )
    responsibilities = []
    for asset_id in asset_ids:
        asset_owners = [
            str(agent.get("id") or "")
            for agent in agents
            if asset_id
            in {
                str(value)
                for value in agent.get("grounded_object_ids") or []
            }
        ]
        zone_ids = {
            str(zone.get("zone_id") or "")
            for zone in zones
            if asset_id
            in {str(value) for value in zone.get("object_ids") or []}
        }
        zone_owners = [
            str(agent.get("id") or "")
            for agent in agents
            if zone_ids.intersection(
                {
                    str(value)
                    for value in agent.get("responsible_zone_ids") or []
                }
            )
        ]
        responsibilities.append(
            _priority_record(
                asset_id=asset_id,
                asset_candidates=asset_owners,
                # The three direct-wiring artifacts contain no object-group
                # relationship. The tier remains explicit but has no candidates.
                group_candidates=[],
                zone_candidates=zone_owners,
            )
        )
    graph = {agent_id: [] for agent_id in agent_ids}
    for handoff in handoff_matrix.get("handoffs") or []:
        if not isinstance(handoff, Mapping):
            continue
        source = str(handoff.get("source_agent_id") or "")
        target = str(handoff.get("target_agent_id") or "")
        if source:
            graph.setdefault(source, []).append(target)
    graph = {
        source: sorted(set(targets)) for source, targets in graph.items()
    }
    return {
        "adapter_id": "direct_wiring",
        "agent_ids": agent_ids,
        "asset_ids": asset_ids,
        "observed_asset_ids": sorted(observed_assets),
        "grounded_asset_ids": sorted(grounded_assets),
        "zone_only_reference_ids": sorted(
            zone_referenced_assets - grounded_assets
        ),
        "responsibilities": responsibilities,
        "handoff_graph": graph,
        "routing_probes": _routing_from_adapter(
            agent_ids=agent_ids,
            graph=graph,
            responsibilities=responsibilities,
        ),
        "group_tier_representation": "not_present_in_source_artifacts",
        "object_universe_rule": (
            "unique agent_roles.agents[].grounded_object_ids"
        ),
    }


def _fresh_v2_adapter(
    instance: Mapping[str, Any],
) -> dict[str, Any]:
    agents = sorted(_typed(instance, "Agent"), key=lambda item: item["id"])
    source_by_native = {
        str(agent["id"]): str(agent.get("sourceAgentId") or "")
        for agent in agents
    }
    assets = _entities_with_role(instance, "sceneObject")
    groups = _entities_with_role(instance, "objectGroup")
    zones = _entities_with_role(instance, "semanticZone")
    responsibilities = []
    for asset in assets:
        native_asset_id = str(asset["id"])
        asset_id = str(asset.get("sourceId") or "")
        group_ids = sorted(
            set(_refs(asset.get("objectGroup")))
            | {
                str(group["id"])
                for group in groups
                if asset_id in _refs(group.get("sourceObjectId"))
            }
        )
        zone_ids = sorted(
            str(zone["id"])
            for zone in zones
            if asset_id in _refs(zone.get("sourceObjectId"))
        )
        responsibilities.append(
            _priority_record(
                asset_id=asset_id,
                asset_candidates=(
                    source_by_native[str(agent["id"])]
                    for agent in agents
                    if native_asset_id in _refs(agent.get("groundedAsset"))
                ),
                group_candidates=(
                    source_by_native[str(agent["id"])]
                    for agent in agents
                    if set(group_ids).intersection(
                        _refs(agent.get("groundedObjectGroup"))
                    )
                ),
                zone_candidates=(
                    source_by_native[str(agent["id"])]
                    for agent in agents
                    if set(zone_ids).intersection(
                        _refs(agent.get("responsibleZone"))
                    )
                ),
            )
        )
    graph = {
        source_by_native[str(agent["id"])]: sorted(
            source_by_native.get(target, target)
            for target in _refs(agent.get("handoffTarget"))
        )
        for agent in agents
    }
    agent_ids = sorted(source_by_native.values())
    return {
        "adapter_id": "fresh_v2",
        "agent_ids": agent_ids,
        "asset_ids": sorted(
            str(asset.get("sourceId") or "") for asset in assets
        ),
        "responsibilities": sorted(
            responsibilities,
            key=lambda item: item["asset_id"],
        ),
        "handoff_graph": graph,
        "routing_probes": _routing_from_adapter(
            agent_ids=agent_ids,
            graph=graph,
            responsibilities=responsibilities,
        ),
        "group_tier_representation": "explicit_v2_object_group_entities",
    }


def _semantic_projection(adapter: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "agent_ids": list(adapter["agent_ids"]),
        "asset_ids": list(adapter["asset_ids"]),
        "responsibilities": [
            {
                "asset_id": item["asset_id"],
                "selected_tier": item["selected_tier"],
                "owner_agent_ids": item["owner_agent_ids"],
                "resolution": item["resolution"],
            }
            for item in adapter["responsibilities"]
        ],
        "handoff_graph": adapter["handoff_graph"],
        "routing_probes": adapter["routing_probes"],
    }


def _projection_sha256(adapter: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            _semantic_projection(adapter),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _compare_adapters(
    direct: Mapping[str, Any],
    treatment: Mapping[str, Any],
) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    for field in ("agent_ids", "asset_ids", "handoff_graph"):
        if direct[field] != treatment[field]:
            mismatches.append(
                {
                    "scope": field,
                    "direct": direct[field],
                    "treatment": treatment[field],
                }
            )
    direct_responsibility = {
        item["asset_id"]: item for item in direct["responsibilities"]
    }
    treatment_responsibility = {
        item["asset_id"]: item for item in treatment["responsibilities"]
    }
    for asset_id in sorted(
        set(direct_responsibility) | set(treatment_responsibility)
    ):
        left = direct_responsibility.get(asset_id)
        right = treatment_responsibility.get(asset_id)
        fields = ("selected_tier", "owner_agent_ids", "resolution")
        if left is None or right is None or any(
            left[field] != right[field] for field in fields
        ):
            mismatches.append(
                {
                    "scope": "responsibility",
                    "asset_id": asset_id,
                    "direct": left,
                    "treatment": right,
                }
            )
    direct_probes = {
        (item["asset_id"], item["start_agent_id"]): item
        for item in direct["routing_probes"]
    }
    treatment_probes = {
        (item["asset_id"], item["start_agent_id"]): item
        for item in treatment["routing_probes"]
    }
    for key in sorted(set(direct_probes) | set(treatment_probes)):
        left = direct_probes.get(key)
        right = treatment_probes.get(key)
        fields = ("owner_agent_ids", "status", "target_paths")
        if left is None or right is None or any(
            left[field] != right[field] for field in fields
        ):
            mismatches.append(
                {
                    "scope": "routing_probe",
                    "asset_id": key[0],
                    "start_agent_id": key[1],
                    "direct": left,
                    "treatment": right,
                }
            )
    return {
        "status": "pass" if not mismatches else "fail",
        "responsibility_denominator": len(direct["responsibilities"]),
        "routing_probe_denominator": len(direct["routing_probes"]),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }


def _direct_validator(
    *,
    scene_semantics: Mapping[str, Any],
    agent_roles: Mapping[str, Any],
    handoff_matrix: Mapping[str, Any],
    expected_asset_ids: Sequence[str],
    expected_agent_ids: Sequence[str],
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    agents = [
        item
        for item in agent_roles.get("agents") or []
        if isinstance(item, Mapping)
    ]
    agent_ids = [str(item.get("id") or "") for item in agents]
    if sorted(agent_ids) != sorted(expected_agent_ids):
        errors.append(
            {
                "code": "DIRECT-AGENT-SET",
                "path": "agent_roles.agents",
                "message": "Agent ids differ from the reference corpus.",
            }
        )
    if len(agent_ids) != len(set(agent_ids)):
        errors.append(
            {
                "code": "DIRECT-DUPLICATE-AGENT",
                "path": "agent_roles.agents[].id",
                "message": "Agent ids must be unique.",
            }
        )
    zones = [
        item
        for item in scene_semantics.get("semantic_zones") or []
        if isinstance(item, Mapping)
    ]
    zone_ids = {str(item.get("zone_id") or "") for item in zones}
    for agent in agents:
        agent_id = str(agent.get("id") or "")
        for zone_id in agent.get("responsible_zone_ids") or []:
            if str(zone_id) not in zone_ids:
                errors.append(
                    {
                        "code": "DIRECT-DANGLING-ZONE",
                        "path": f"agent_roles.agents.{agent_id}.responsible_zone_ids",
                        "message": f"Unknown zone {zone_id}.",
                    }
                )
        for target in agent.get("handoff_targets") or []:
            if str(target) not in set(agent_ids):
                errors.append(
                    {
                        "code": "DIRECT-DANGLING-HANDOFF",
                        "path": f"agent_roles.agents.{agent_id}.handoff_targets",
                        "message": f"Unknown handoff target {target}.",
                    }
                )
    role_pairs = {
        (str(agent.get("id") or ""), str(target))
        for agent in agents
        for target in agent.get("handoff_targets") or []
    }
    matrix_pairs = {
        (
            str(item.get("source_agent_id") or ""),
            str(item.get("target_agent_id") or ""),
        )
        for item in handoff_matrix.get("handoffs") or []
        if isinstance(item, Mapping)
    }
    for source, target in sorted(matrix_pairs):
        if source not in set(agent_ids) or target not in set(agent_ids):
            errors.append(
                {
                    "code": "DIRECT-DANGLING-MATRIX-HANDOFF",
                    "path": "handoff_matrix.handoffs",
                    "message": f"Unknown handoff pair {source}->{target}.",
                }
            )
    if role_pairs != matrix_pairs:
        errors.append(
            {
                "code": "DIRECT-HANDOFF-DIVERGENCE",
                "path": "agent_roles.handoff_targets|handoff_matrix.handoffs",
                "message": "Redundant handoff references disagree.",
            }
        )
    adapter = _direct_wiring_adapter(
        scene_semantics=scene_semantics,
        agent_roles=agent_roles,
        handoff_matrix=handoff_matrix,
        expected_asset_ids=expected_asset_ids,
    )
    missing_observed = sorted(
        set(expected_asset_ids) - set(adapter["observed_asset_ids"])
    )
    for asset_id in missing_observed:
        errors.append(
            {
                "code": "DIRECT-MISSING-ASSET-REFERENCE",
                "path": f"scene_semantics|agent_roles.{asset_id}",
                "message": f"Reference asset {asset_id} is absent.",
            }
        )
    for responsibility in adapter["responsibilities"]:
        if responsibility["resolution"] != "unique":
            errors.append(
                {
                    "code": "DIRECT-OWNERSHIP",
                    "path": f"responsibility.{responsibility['asset_id']}",
                    "message": (
                        f"Asset {responsibility['asset_id']} has "
                        f"{len(responsibility['owner_agent_ids'])} selected owners."
                    ),
                }
            )
    return {
        "validator_id": "direct_wiring_validator",
        "accepted": not errors,
        "errors": errors,
    }


def _fresh_v2_adapter_validator(
    *,
    instance: Mapping[str, Any],
    expected_asset_ids: Sequence[str],
    expected_agent_ids: Sequence[str],
) -> dict[str, Any]:
    # Independent adapter validator: it intentionally does not reuse the
    # direct-wiring validator or its result. Canonical V2 validation is
    # exercised separately by the V2-only mutation suite.
    errors: list[dict[str, str]] = []
    adapter = _fresh_v2_adapter(instance)
    if adapter["agent_ids"] != sorted(expected_agent_ids):
        errors.append(
            {
                "code": "V2-AGENT-SET",
                "path": "Agent.sourceAgentId",
                "message": "Agent source ids differ from the reference corpus.",
            }
        )
    if adapter["asset_ids"] != sorted(expected_asset_ids):
        missing = sorted(set(expected_asset_ids) - set(adapter["asset_ids"]))
        extra = sorted(set(adapter["asset_ids"]) - set(expected_asset_ids))
        errors.append(
            {
                "code": "V2-ASSET-SET",
                "path": "Entity[sceneObject].sourceId",
                "message": f"Asset set mismatch; missing={missing}, extra={extra}.",
            }
        )
    known_agents = set(adapter["agent_ids"])
    for source, targets in adapter["handoff_graph"].items():
        for target in targets:
            if target not in known_agents:
                errors.append(
                    {
                        "code": "V2-DANGLING-HANDOFF",
                        "path": f"Agent.{source}.handoffTarget",
                        "message": f"Unknown handoff target {target}.",
                    }
                )
    for responsibility in adapter["responsibilities"]:
        if responsibility["resolution"] != "unique":
            errors.append(
                {
                    "code": "V2-OWNERSHIP",
                    "path": f"responsibility.{responsibility['asset_id']}",
                    "message": (
                        f"Asset {responsibility['asset_id']} has "
                        f"{len(responsibility['owner_agent_ids'])} selected owners."
                    ),
                }
            )
    return {
        "validator_id": "fresh_v2_adapter_validator",
        "accepted": not errors,
        "errors": errors,
    }


def _common_mutation_spec(adapter: Mapping[str, Any]) -> dict[str, Any]:
    responsibilities = {
        item["asset_id"]: item for item in adapter["responsibilities"]
    }
    assets = sorted(responsibilities)
    missing_asset = assets[0]
    duplicate_asset = assets[1] if len(assets) > 1 else assets[0]
    current_owner = responsibilities[duplicate_asset]["owner_agent_ids"][0]
    additional_owner = next(
        agent_id
        for agent_id in sorted(adapter["agent_ids"])
        if agent_id != current_owner
    )
    source = next(
        source
        for source, targets in sorted(adapter["handoff_graph"].items())
        if targets
    )
    target = sorted(adapter["handoff_graph"][source])[0]
    return {
        "missing_ownership": {"asset_id": missing_asset},
        "duplicate_owner": {
            "asset_id": duplicate_asset,
            "additional_owner_agent_id": additional_owner,
        },
        "dangling_handoff": {
            "source_agent_id": source,
            "old_target_agent_id": target,
            "invalid_target_agent_id": "iui2027_missing_agent",
        },
    }


def _mutate_direct_common(
    *,
    mutation_id: str,
    spec: Mapping[str, Any],
    scene_semantics: Mapping[str, Any],
    agent_roles: Mapping[str, Any],
    handoff_matrix: Mapping[str, Any],
) -> dict[str, Any]:
    scene = copy.deepcopy(dict(scene_semantics))
    roles = copy.deepcopy(dict(agent_roles))
    matrix = copy.deepcopy(dict(handoff_matrix))
    edited_artifacts: set[str] = set()
    reference_edits = 0
    tokens: list[str] = []
    if mutation_id == "missing_ownership":
        asset_id = str(spec["asset_id"])
        tokens = [asset_id, "ownership", "absent"]
        for agent in roles.get("agents") or []:
            before = list(agent.get("grounded_object_ids") or [])
            after = [value for value in before if str(value) != asset_id]
            reference_edits += len(before) - len(after)
            if after != before:
                agent["grounded_object_ids"] = after
                edited_artifacts.add("agent_roles")
        for zone in scene.get("semantic_zones") or []:
            before = list(zone.get("object_ids") or [])
            after = [value for value in before if str(value) != asset_id]
            reference_edits += len(before) - len(after)
            if after != before:
                zone["object_ids"] = after
                edited_artifacts.add("scene_semantics")
    elif mutation_id == "duplicate_owner":
        asset_id = str(spec["asset_id"])
        additional = str(spec["additional_owner_agent_id"])
        tokens = [asset_id, "owners"]
        agent = next(
            item for item in roles["agents"] if item.get("id") == additional
        )
        if asset_id not in agent.get("grounded_object_ids", []):
            agent.setdefault("grounded_object_ids", []).append(asset_id)
            reference_edits += 1
            edited_artifacts.add("agent_roles")
    elif mutation_id == "dangling_handoff":
        source = str(spec["source_agent_id"])
        old = str(spec["old_target_agent_id"])
        invalid = str(spec["invalid_target_agent_id"])
        tokens = [source, invalid, "handoff"]
        agent = next(
            item for item in roles["agents"] if item.get("id") == source
        )
        agent["handoff_targets"] = [
            invalid if str(value) == old else value
            for value in agent.get("handoff_targets") or []
        ]
        reference_edits += 1
        edited_artifacts.add("agent_roles")
        entry = next(
            item
            for item in matrix["handoffs"]
            if item.get("source_agent_id") == source
            and item.get("target_agent_id") == old
        )
        entry["target_agent_id"] = invalid
        reference_edits += 1
        edited_artifacts.add("handoff_matrix")
    else:
        raise ValueError(f"Unknown common mutation: {mutation_id}")
    return {
        "scene_semantics": scene,
        "agent_roles": roles,
        "handoff_matrix": matrix,
        "artifact_edit_count": len(edited_artifacts),
        "edited_artifacts": sorted(edited_artifacts),
        "reference_edit_count": reference_edits,
        "localization_tokens": tokens,
    }


def _mutate_v2_common(
    *,
    mutation_id: str,
    spec: Mapping[str, Any],
    instance: Mapping[str, Any],
) -> dict[str, Any]:
    mutated = copy.deepcopy(dict(instance))
    objects = mutated["objects"]
    agents = [item for item in objects if item.get("type") == "Agent"]
    source_to_agent = {
        str(item.get("sourceAgentId") or ""): item for item in agents
    }
    assets = {
        str(item.get("sourceId") or ""): item
        for item in objects
        if item.get("type") == "Entity"
        and item.get("entityRole") == "sceneObject"
    }
    reference_edits = 0
    tokens: list[str] = []
    if mutation_id == "missing_ownership":
        asset_id = str(spec["asset_id"])
        asset = assets[asset_id]
        native_asset_id = str(asset["id"])
        tokens = [asset_id, "ownership"]
        for agent in agents:
            before = _refs(agent.get("groundedAsset"))
            after = [value for value in before if value != native_asset_id]
            reference_edits += len(before) - len(after)
            agent["groundedAsset"] = after
        group_ids = _refs(asset.get("objectGroup"))
        reference_edits += len(group_ids)
        asset["objectGroup"] = []
        for item in objects:
            if item.get("type") != "Entity":
                continue
            if item.get("entityRole") not in {"objectGroup", "semanticZone"}:
                continue
            before = _refs(item.get("sourceObjectId"))
            after = [value for value in before if value != asset_id]
            reference_edits += len(before) - len(after)
            item["sourceObjectId"] = after
    elif mutation_id == "duplicate_owner":
        asset_id = str(spec["asset_id"])
        additional = str(spec["additional_owner_agent_id"])
        tokens = [asset_id, "owners"]
        native_asset_id = str(assets[asset_id]["id"])
        agent = source_to_agent[additional]
        if native_asset_id not in _refs(agent.get("groundedAsset")):
            agent.setdefault("groundedAsset", []).append(native_asset_id)
            reference_edits += 1
    elif mutation_id == "dangling_handoff":
        source = str(spec["source_agent_id"])
        old = str(spec["old_target_agent_id"])
        invalid = str(spec["invalid_target_agent_id"])
        tokens = [source, invalid, "handoff"]
        old_native = str(source_to_agent[old]["id"])
        invalid_native = invalid
        agent = source_to_agent[source]
        agent["handoffTarget"] = [
            invalid_native if value == old_native else value
            for value in _refs(agent.get("handoffTarget"))
        ]
        reference_edits += 1
    else:
        raise ValueError(f"Unknown common mutation: {mutation_id}")
    return {
        "instance": mutated,
        "artifact_edit_count": 1,
        "edited_artifacts": ["fresh_v2_instance"],
        "reference_edit_count": reference_edits,
        "localization_tokens": tokens,
    }


def _new_issue_evaluation(
    baseline: Mapping[str, Any],
    mutated: Mapping[str, Any],
    tokens: Sequence[str],
) -> dict[str, Any]:
    baseline_signatures = {
        _issue_signature(issue) for issue in baseline["errors"]
    }
    new_errors = [
        issue
        for issue in mutated["errors"]
        if _issue_signature(issue) not in baseline_signatures
    ]
    searchable = " ".join(
        " ".join(_issue_signature(issue)) for issue in new_errors
    ).casefold()
    return {
        "accepted": mutated["accepted"],
        "new_error_count": len(new_errors),
        "detected_by_new_error": bool(new_errors),
        "localized": bool(new_errors)
        and any(token.casefold() in searchable for token in tokens),
        "new_errors": new_errors,
    }


def _timing_summary(values: Sequence[int]) -> dict[str, Any]:
    ordered = sorted(values)
    p95_index = max(0, min(len(ordered) - 1, int(0.95 * len(ordered)) - 1))
    return {
        "repetitions": len(values),
        "min_ns": min(values),
        "median_ns": int(statistics.median(values)),
        "p95_ns": ordered[p95_index],
        "max_ns": max(values),
    }


def _measure_adapter_pair(
    *,
    direct_factory: Callable[[], dict[str, Any]],
    treatment_factory: Callable[[], dict[str, Any]],
    repetitions: int = 40,
    warmups: int = 4,
) -> dict[str, Any]:
    for _ in range(warmups):
        direct_factory()
        treatment_factory()
    durations = {"direct_wiring": [], "fresh_v2": []}
    hashes = {"direct_wiring": set(), "fresh_v2": set()}
    for index in range(repetitions):
        order = (
            ("direct_wiring", direct_factory),
            ("fresh_v2", treatment_factory),
        )
        if index % 2:
            order = tuple(reversed(order))
        for adapter_id, factory in order:
            started = time.perf_counter_ns()
            adapter = factory()
            durations[adapter_id].append(time.perf_counter_ns() - started)
            hashes[adapter_id].add(_projection_sha256(adapter))
    direct_summary = _timing_summary(durations["direct_wiring"])
    treatment_summary = _timing_summary(durations["fresh_v2"])
    return {
        "workload": (
            "Construct normalized responsibility adapter and enumerate all "
            "object-by-start-agent structural routes from already parsed "
            "artifacts; excludes JSON I/O and v0.5-to-V2 generation."
        ),
        "warmups": warmups,
        "repetitions": repetitions,
        "alternating_execution_order": True,
        "deterministic_workload_outputs": (
            len(hashes["direct_wiring"]) == 1
            and len(hashes["fresh_v2"]) == 1
        ),
        "projection_sha256": {
            key: sorted(value)[0] if len(value) == 1 else sorted(value)
            for key, value in hashes.items()
        },
        "direct_wiring": direct_summary,
        "fresh_v2": treatment_summary,
        "median_runtime_ratio_fresh_v2_over_direct": round(
            treatment_summary["median_ns"] / direct_summary["median_ns"],
            6,
        ),
        "interpretation": (
            "Descriptive local timing only; no inferential performance "
            "advantage is claimed."
        ),
    }


def _priority_probe_observation(
    *,
    adapter: Mapping[str, Any],
    asset_id: str,
    candidate_owner_agent_ids: Mapping[str, Sequence[str]],
    expected_selected_tier: str,
    expected_resolution: str,
) -> dict[str, Any]:
    candidates = copy.deepcopy(dict(candidate_owner_agent_ids))
    responsibility = _priority_record(
        asset_id=asset_id,
        asset_candidates=candidates["asset"],
        group_candidates=candidates["group"],
        zone_candidates=candidates["zone"],
    )
    routes = _routing_from_adapter(
        agent_ids=adapter["agent_ids"],
        graph=adapter["handoff_graph"],
        responsibilities=[responsibility],
    )
    statuses = Counter(route["status"] for route in routes)
    ambiguity_fail_closed = (
        responsibility["resolution"] == "ambiguous"
        and statuses["ambiguous_target"] == len(routes)
    )
    accepted_by_unique_owner_policy = (
        responsibility["resolution"] == "unique"
    )
    expected_accepted = expected_resolution == "unique"
    passed = (
        responsibility["selected_tier"] == expected_selected_tier
        and responsibility["resolution"] == expected_resolution
        and accepted_by_unique_owner_policy == expected_accepted
    )
    if expected_resolution == "ambiguous":
        passed = passed and ambiguity_fail_closed
    return {
        "candidate_owner_agent_ids": candidates,
        "expected_selected_tier": expected_selected_tier,
        "expected_resolution": expected_resolution,
        "observed_selected_tier": responsibility["selected_tier"],
        "observed_owner_agent_ids": responsibility["owner_agent_ids"],
        "observed_resolution": responsibility["resolution"],
        "accepted_by_unique_owner_policy": accepted_by_unique_owner_policy,
        "routing_probe_denominator": len(routes),
        "routing_status_counts": {
            status: statuses[status]
            for status in (
                "local_owner",
                "direct_allowed",
                "transitive_allowed",
                "rejected_unreachable",
                "ambiguous_target",
                "unassigned_target",
            )
        },
        "ambiguity_fail_closed": ambiguity_fail_closed,
        "passed": passed,
    }


def _synthetic_priority_probe_case(
    *,
    case_id: str,
    direct: Mapping[str, Any],
    treatment: Mapping[str, Any],
) -> dict[str, Any]:
    direct_by_asset = {
        item["asset_id"]: item for item in direct["responsibilities"]
    }
    treatment_by_asset = {
        item["asset_id"]: item for item in treatment["responsibilities"]
    }
    selected_asset_id = next(
        (
            asset_id
            for asset_id in sorted(
                set(direct_by_asset) & set(treatment_by_asset)
            )
            if direct_by_asset[asset_id]["resolution"] == "unique"
            and treatment_by_asset[asset_id]["resolution"] == "unique"
            and direct_by_asset[asset_id]["owner_agent_ids"]
            == treatment_by_asset[asset_id]["owner_agent_ids"]
            and direct_by_asset[asset_id][
                "candidate_owner_agent_ids"
            ]["zone"]
            == treatment_by_asset[asset_id][
                "candidate_owner_agent_ids"
            ]["zone"]
            == direct_by_asset[asset_id]["owner_agent_ids"]
        ),
        None,
    )
    if selected_asset_id is None:
        return {
            "case_id": case_id,
            "status": "not_comparable",
            "reason": (
                "No common object has the same unique Asset and Zone owner "
                "in both adapters."
            ),
            "probe_results": [],
            "semantic_parity_mismatch_count": 0,
            "semantic_parity_mismatches": [],
        }

    owner = direct_by_asset[selected_asset_id]["owner_agent_ids"][0]
    competitor = next(
        agent_id
        for agent_id in direct["agent_ids"]
        if agent_id != owner
    )
    # The natural Direct-Wiring artifacts have no object-group relation.
    # These isolated micro-probes therefore add the same derived Group
    # candidate to copies of both normalized adapters. They test the priority
    # decision rule, not native Direct-Wiring group expressiveness.
    base_candidates = {
        "asset": [owner],
        "group": [owner],
        "zone": [owner],
    }
    specifications = (
        {
            "probe_id": "asset_removed_group_fallback",
            "candidates": {
                **base_candidates,
                "asset": [],
            },
            "expected_selected_tier": "group",
            "expected_resolution": "unique",
        },
        {
            "probe_id": "asset_and_group_removed_zone_fallback",
            "candidates": {
                **base_candidates,
                "asset": [],
                "group": [],
            },
            "expected_selected_tier": "zone",
            "expected_resolution": "unique",
        },
        {
            "probe_id": "competing_owner_at_highest_active_tier",
            "candidates": {
                **base_candidates,
                "asset": [owner, competitor],
            },
            "expected_selected_tier": "asset",
            "expected_resolution": "ambiguous",
        },
    )
    probe_results: list[dict[str, Any]] = []
    parity_mismatches: list[dict[str, Any]] = []
    for specification in specifications:
        adapters = {
            "direct_wiring": _priority_probe_observation(
                adapter=direct,
                asset_id=selected_asset_id,
                candidate_owner_agent_ids=specification["candidates"],
                expected_selected_tier=specification[
                    "expected_selected_tier"
                ],
                expected_resolution=specification["expected_resolution"],
            ),
            "fresh_v2": _priority_probe_observation(
                adapter=treatment,
                asset_id=selected_asset_id,
                candidate_owner_agent_ids=specification["candidates"],
                expected_selected_tier=specification[
                    "expected_selected_tier"
                ],
                expected_resolution=specification["expected_resolution"],
            ),
        }
        comparable_fields = (
            "observed_selected_tier",
            "observed_owner_agent_ids",
            "observed_resolution",
            "accepted_by_unique_owner_policy",
            "routing_probe_denominator",
            "routing_status_counts",
            "ambiguity_fail_closed",
        )
        mismatch_fields = [
            field
            for field in comparable_fields
            if adapters["direct_wiring"][field]
            != adapters["fresh_v2"][field]
        ]
        if mismatch_fields:
            parity_mismatches.append(
                {
                    "probe_id": specification["probe_id"],
                    "fields": mismatch_fields,
                    "direct_wiring": adapters["direct_wiring"],
                    "fresh_v2": adapters["fresh_v2"],
                }
            )
        probe_results.append(
            {
                "probe_id": specification["probe_id"],
                "asset_id": selected_asset_id,
                "synthetic_change": (
                    "Derived candidate-set copy; natural corpus unchanged."
                ),
                "adapters": adapters,
                "semantic_parity": "pass"
                if not mismatch_fields
                else "fail",
            }
        )
    passed = (
        not parity_mismatches
        and all(
            observation["passed"]
            for probe in probe_results
            for observation in probe["adapters"].values()
        )
    )
    return {
        "case_id": case_id,
        "status": "pass" if passed else "fail",
        "asset_id": selected_asset_id,
        "derived_group_candidate_owner_agent_id": owner,
        "competing_owner_agent_id": competitor,
        "probe_results": probe_results,
        "semantic_parity_mismatch_count": len(parity_mismatches),
        "semantic_parity_mismatches": parity_mismatches,
    }


def _aggregate_synthetic_priority_probes(
    cases: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    case_results = [
        case["synthetic_priority_probe_result"] for case in cases
    ]
    comparable = all(case["status"] != "not_comparable" for case in case_results)
    passed = comparable and all(
        case["status"] == "pass" for case in case_results
    )
    adapter_metrics: dict[str, Any] = {}
    for adapter_id in ("direct_wiring", "fresh_v2"):
        observations = [
            probe["adapters"][adapter_id]
            for case in case_results
            for probe in case["probe_results"]
        ]
        adapter_metrics[adapter_id] = {
            "synthetic_probe_denominator": len(observations),
            "passed_probe_count": sum(
                observation["passed"] for observation in observations
            ),
            "group_fallback_count": sum(
                observation["observed_selected_tier"] == "group"
                and observation["observed_resolution"] == "unique"
                for observation in observations
            ),
            "zone_fallback_count": sum(
                observation["observed_selected_tier"] == "zone"
                and observation["observed_resolution"] == "unique"
                for observation in observations
            ),
            "ambiguity_fail_closed_count": sum(
                observation["ambiguity_fail_closed"]
                for observation in observations
            ),
        }
    return {
        "status": (
            "pass"
            if passed
            else "not_comparable"
            if not comparable
            else "fail"
        ),
        "included_in_natural_corpus_metrics": False,
        "case_denominator": len(case_results),
        "probe_types_per_case": 3,
        "total_adapter_observation_denominator": sum(
            metrics["synthetic_probe_denominator"]
            for metrics in adapter_metrics.values()
        ),
        "semantic_parity_mismatch_count": sum(
            case["semantic_parity_mismatch_count"]
            for case in case_results
        ),
        "adapter_metrics": adapter_metrics,
        "case_results": case_results,
        "interpretation": (
            "Synthetic normalized-candidate probes exercise the priority "
            "decision rule only. They do not demonstrate natural-corpus "
            "Group/Zone usage or native Direct-Wiring group expressiveness."
        ),
    }


def _common_comparison_for_case(
    *,
    case_id: str,
    scene_semantics: Mapping[str, Any],
    agent_roles: Mapping[str, Any],
    handoff_matrix: Mapping[str, Any],
    fresh_v2: Mapping[str, Any],
) -> dict[str, Any]:
    direct = _direct_wiring_adapter(
        scene_semantics=scene_semantics,
        agent_roles=agent_roles,
        handoff_matrix=handoff_matrix,
    )
    treatment = _fresh_v2_adapter(fresh_v2)
    parity = _compare_adapters(direct, treatment)
    expected_assets = list(direct["asset_ids"])
    expected_agents = list(direct["agent_ids"])
    direct_baseline_validation = _direct_validator(
        scene_semantics=scene_semantics,
        agent_roles=agent_roles,
        handoff_matrix=handoff_matrix,
        expected_asset_ids=expected_assets,
        expected_agent_ids=expected_agents,
    )
    treatment_baseline_validation = _fresh_v2_adapter_validator(
        instance=fresh_v2,
        expected_asset_ids=expected_assets,
        expected_agent_ids=expected_agents,
    )
    mutation_spec = _common_mutation_spec(direct)
    mutation_records = []
    for mutation_id in (
        "missing_ownership",
        "duplicate_owner",
        "dangling_handoff",
    ):
        direct_mutation = _mutate_direct_common(
            mutation_id=mutation_id,
            spec=mutation_spec[mutation_id],
            scene_semantics=scene_semantics,
            agent_roles=agent_roles,
            handoff_matrix=handoff_matrix,
        )
        treatment_mutation = _mutate_v2_common(
            mutation_id=mutation_id,
            spec=mutation_spec[mutation_id],
            instance=fresh_v2,
        )
        direct_adapter = _direct_wiring_adapter(
            scene_semantics=direct_mutation["scene_semantics"],
            agent_roles=direct_mutation["agent_roles"],
            handoff_matrix=direct_mutation["handoff_matrix"],
            expected_asset_ids=expected_assets,
        )
        treatment_adapter = _fresh_v2_adapter(
            treatment_mutation["instance"]
        )
        mutated_parity = _compare_adapters(
            direct_adapter,
            treatment_adapter,
        )
        direct_report = _direct_validator(
            scene_semantics=direct_mutation["scene_semantics"],
            agent_roles=direct_mutation["agent_roles"],
            handoff_matrix=direct_mutation["handoff_matrix"],
            expected_asset_ids=expected_assets,
            expected_agent_ids=expected_agents,
        )
        treatment_report = _fresh_v2_adapter_validator(
            instance=treatment_mutation["instance"],
            expected_asset_ids=expected_assets,
            expected_agent_ids=expected_agents,
        )
        mutation_records.append(
            {
                "case_id": case_id,
                "mutation_id": mutation_id,
                "semantic_specification": mutation_spec[mutation_id],
                "parity": mutated_parity,
                "direct_wiring": {
                    "artifact_edit_count": direct_mutation[
                        "artifact_edit_count"
                    ],
                    "edited_artifacts": direct_mutation[
                        "edited_artifacts"
                    ],
                    "reference_edit_count": direct_mutation[
                        "reference_edit_count"
                    ],
                    "validation": _new_issue_evaluation(
                        direct_baseline_validation,
                        direct_report,
                        direct_mutation["localization_tokens"],
                    ),
                },
                "fresh_v2": {
                    "artifact_edit_count": treatment_mutation[
                        "artifact_edit_count"
                    ],
                    "edited_artifacts": treatment_mutation[
                        "edited_artifacts"
                    ],
                    "reference_edit_count": treatment_mutation[
                        "reference_edit_count"
                    ],
                    "validation": _new_issue_evaluation(
                        treatment_baseline_validation,
                        treatment_report,
                        treatment_mutation["localization_tokens"],
                    ),
                },
            }
        )
    timing = _measure_adapter_pair(
        direct_factory=lambda: _direct_wiring_adapter(
            scene_semantics=scene_semantics,
            agent_roles=agent_roles,
            handoff_matrix=handoff_matrix,
        ),
        treatment_factory=lambda: _fresh_v2_adapter(fresh_v2),
    )
    return {
        "case_id": case_id,
        "baseline_parity": parity,
        "baseline_semantic_projection_sha256": {
            "direct_wiring": _projection_sha256(direct),
            "fresh_v2": _projection_sha256(treatment),
        },
        "baseline_validation": {
            "direct_wiring": direct_baseline_validation,
            "fresh_v2": treatment_baseline_validation,
        },
        "direct_wiring_object_universe": {
            "rule": direct["object_universe_rule"],
            "routeable_object_count": len(direct["asset_ids"]),
            "zone_only_reference_ids_excluded": direct[
                "zone_only_reference_ids"
            ],
        },
        "direct_wiring_source_artifacts": [
            "scene_semantics",
            "agent_roles",
            "handoff_matrix",
        ],
        "treatment_source": "fresh in-memory V2 regenerated from v0.5",
        "mutation_runs": mutation_records,
        "synthetic_priority_probe_result": _synthetic_priority_probe_case(
            case_id=case_id,
            direct=direct,
            treatment=treatment,
        ),
        "runtime": timing,
    }


def _aggregate_common_comparison(
    cases: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    parity_failures = [
        {
            "case_id": case["case_id"],
            "scope": "baseline",
            "mismatches": case["baseline_parity"]["mismatches"],
        }
        for case in cases
        if case["baseline_parity"]["status"] != "pass"
    ]
    for case in cases:
        parity_failures.extend(
            {
                "case_id": case["case_id"],
                "scope": mutation["mutation_id"],
                "mismatches": mutation["parity"]["mismatches"],
            }
            for mutation in case["mutation_runs"]
            if mutation["parity"]["status"] != "pass"
        )
    comparable = not parity_failures
    adapter_metrics: dict[str, Any] = {}
    for adapter_id in ("direct_wiring", "fresh_v2"):
        baseline_false_positives = sum(
            not case["baseline_validation"][adapter_id]["accepted"]
            for case in cases
        )
        mutation_runs = [
            mutation[adapter_id]
            for case in cases
            for mutation in case["mutation_runs"]
        ]
        detected = sum(
            item["validation"]["detected_by_new_error"]
            for item in mutation_runs
        )
        localized = sum(
            item["validation"]["localized"] for item in mutation_runs
        )
        adapter_metrics[adapter_id] = {
            "expected_valid_case_denominator": len(cases),
            "baseline_false_positive_count": baseline_false_positives,
            "baseline_false_positive_rate": (
                round(baseline_false_positives / len(cases), 6)
                if cases
                else None
            ),
            "common_mutation_denominator": (
                len(mutation_runs) if comparable else 0
            ),
            "detected_mutation_count": detected if comparable else None,
            "mutation_detection_rate": (
                round(detected / len(mutation_runs), 6)
                if comparable and mutation_runs
                else None
            ),
            "localized_detection_count": (
                localized if comparable else None
            ),
            "localization_rate": (
                round(localized / len(mutation_runs), 6)
                if comparable and mutation_runs
                else None
            ),
            "artifact_edit_count": (
                sum(item["artifact_edit_count"] for item in mutation_runs)
                if comparable
                else None
            ),
            "reference_edit_count": (
                sum(item["reference_edit_count"] for item in mutation_runs)
                if comparable
                else None
            ),
        }
    return {
        "status": "comparable" if comparable else "not_comparable",
        "parity_failure_count": len(parity_failures),
        "parity_failures": parity_failures,
        "baseline_case_denominator": len(cases),
        "baseline_responsibility_denominator": sum(
            case["baseline_parity"]["responsibility_denominator"]
            for case in cases
        ),
        "baseline_routing_probe_denominator": sum(
            case["baseline_parity"]["routing_probe_denominator"]
            for case in cases
        ),
        "common_mutation_types": [
            "missing_ownership",
            "duplicate_owner",
            "dangling_handoff",
        ],
        "adapter_metrics": adapter_metrics,
        "runtime_method": {
            "repetitions_per_case": 40,
            "warmups_per_case": 4,
            "alternating_execution_order": True,
            "timings_are_descriptive": True,
        },
    }


def _canonical_validation(instance: Mapping[str, Any]) -> dict[str, Any]:
    report = validate_instance(
        MODEL,
        instance,
        subject=str(instance.get("caseId") or instance.get("id") or "case"),
    ).to_dict()
    issues = [
        {
            "code": str(issue.get("code") or "CANONICAL"),
            "path": str(issue.get("path") or ""),
            "message": str(issue.get("message") or ""),
        }
        for issue in report.get("issues") or []
        if str(issue.get("severity") or "error") == "error"
    ]
    return {
        "validator_id": "canonical_v2",
        "accepted": bool(report.get("ok")) and not issues,
        "errors": issues,
    }


def _pipeline_validation(
    instance: Mapping[str, Any],
    agent_roles: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        _validate_v2_agent_provider_contract(
            functionalmlds_instance=dict(instance),
            agent_roles=dict(agent_roles),
        )
    except Exception as exc:
        return {
            "validator_id": "pipeline_agent_provider_contract",
            "accepted": False,
            "errors": [
                {
                    "code": "PIPELINE-CONTRACT",
                    "path": "",
                    "message": str(exc),
                }
            ],
        }
    return {
        "validator_id": "pipeline_agent_provider_contract",
        "accepted": True,
        "errors": [],
    }


def _run_validators(
    instance: Mapping[str, Any],
    agent_roles: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    reports = (
        _canonical_validation(instance),
        _pipeline_validation(instance, agent_roles),
    )
    return {report["validator_id"]: report for report in reports}


def _issue_signature(issue: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        str(issue.get("code") or ""),
        str(issue.get("path") or ""),
        str(issue.get("message") or ""),
    )


def _mutate_dangling_handoff(
    instance: dict[str, Any],
) -> tuple[dict[str, Any], list[str]] | None:
    agent = next(
        (
            item
            for item in _typed(instance, "Agent")
            if _refs(item.get("handoffTarget"))
        ),
        None,
    )
    if agent is None:
        return None
    stored = next(
        item
        for item in instance["objects"]
        if item.get("id") == agent["id"]
    )
    invalid_id = "ENT-IUI2027-MISSING-HANDOFF-TARGET"
    stored["handoffTarget"] = [
        invalid_id,
        *_refs(stored.get("handoffTarget"))[1:],
    ]
    return instance, [str(stored["id"]), "handoffTarget", invalid_id]


def _mutate_missing_provider(
    instance: dict[str, Any],
) -> tuple[dict[str, Any], list[str]] | None:
    uses = _typed(instance, "CapabilityUse")
    if not uses:
        return None
    use_id = str(uses[0]["id"])
    stored = next(
        item for item in instance["objects"] if item.get("id") == use_id
    )
    stored["provider"] = []
    return instance, [use_id, "provider"]


def _mutate_duplicate_source_agent(
    instance: dict[str, Any],
) -> tuple[dict[str, Any], list[str]] | None:
    agents = _typed(instance, "Agent")
    if len(agents) < 2:
        return None
    first_source = str(agents[0].get("sourceAgentId") or "")
    second_id = str(agents[1]["id"])
    if not first_source:
        return None
    stored = next(
        item for item in instance["objects"] if item.get("id") == second_id
    )
    stored["sourceAgentId"] = first_source
    return instance, [second_id, "sourceAgentId", "ambiguous"]


def _mutate_domain_provider(
    instance: dict[str, Any],
) -> tuple[dict[str, Any], list[str]] | None:
    by_id = {
        str(item.get("id") or ""): item
        for item in instance.get("objects") or []
        if isinstance(item, Mapping)
    }
    agent_capabilities = {
        capability_id
        for item in _typed(instance, "Agent")
        for capability_id in _refs(item.get("providedCapability"))
    }
    use = next(
        (
            item
            for item in _typed(instance, "CapabilityUse")
            if len(_refs(item.get("typeRef"))) == 1
            and _refs(item.get("typeRef"))[0] in agent_capabilities
            and len(_refs(item.get("provider"))) == 1
            and by_id.get(_refs(item.get("provider"))[0], {}).get("type")
            == "Agent"
        ),
        None,
    )
    if use is None:
        return None
    orchestrator = next(
        (
            item
            for item in _typed(instance, "Entity")
            if item.get("entityRole") == "runtimeOrchestrator"
        ),
        None,
    )
    if orchestrator is None:
        return None
    capability_id = _refs(use.get("typeRef"))[0]
    use_id = str(use["id"])
    orchestrator_id = str(orchestrator["id"])
    by_id[orchestrator_id]["providedCapability"] = sorted(
        set(_refs(by_id[orchestrator_id].get("providedCapability")))
        | {capability_id}
    )
    by_id[use_id]["provider"] = [orchestrator_id]
    for step in _typed(instance, "ScenarioStep"):
        if use_id in _refs(step.get("capabilityUse")):
            by_id[str(step["id"])]["performedBy"] = [orchestrator_id]
    return instance, [use_id, "domain Capability", "Domain Agent"]


Mutation = tuple[
    str,
    Callable[[dict[str, Any]], tuple[dict[str, Any], list[str]] | None],
]
MUTATIONS: tuple[Mutation, ...] = (
    ("missing_capability_provider", _mutate_missing_provider),
    ("duplicate_source_agent", _mutate_duplicate_source_agent),
    ("domain_capability_reassigned_to_orchestrator", _mutate_domain_provider),
)


def _validation_evaluation(
    cases: Sequence[
        tuple[
            str,
            Mapping[str, Any],
            Mapping[str, Any],
            Mapping[str, Any],
        ]
    ],
) -> dict[str, Any]:
    baseline_records: list[dict[str, Any]] = []
    mutation_records: list[dict[str, Any]] = []
    validator_ids = (
        "canonical_v2",
        "pipeline_agent_provider_contract",
    )

    for case_id, instance, agent_roles, corpus_record in cases:
        baseline = _run_validators(instance, agent_roles)
        baseline_records.append(
            {
                "case_id": case_id,
                "expected_valid": corpus_record["reference_label"][
                    "expected_valid"
                ],
                "validators": {
                    validator_id: {
                        "accepted": baseline[validator_id]["accepted"],
                        "error_count": len(
                            baseline[validator_id]["errors"]
                        ),
                        "errors": baseline[validator_id]["errors"],
                    }
                    for validator_id in validator_ids
                },
            }
        )

        for mutation_id, mutate in MUTATIONS:
            mutation_input = copy.deepcopy(dict(instance))
            mutated = mutate(mutation_input)
            if mutated is None:
                mutation_records.append(
                    {
                        "case_id": case_id,
                        "mutation_id": mutation_id,
                        "applicable": False,
                        "reason": (
                            "The freshly regenerated baseline does not satisfy "
                            "the "
                            "mutation precondition."
                        ),
                    }
                )
                continue
            mutated_instance, localization_tokens = mutated
            reports = _run_validators(mutated_instance, agent_roles)
            validator_results: dict[str, Any] = {}
            for validator_id in validator_ids:
                baseline_signatures = {
                    _issue_signature(issue)
                    for issue in baseline[validator_id]["errors"]
                }
                new_issues = [
                    issue
                    for issue in reports[validator_id]["errors"]
                    if _issue_signature(issue) not in baseline_signatures
                ]
                searchable = " ".join(
                    " ".join(_issue_signature(issue)) for issue in new_issues
                ).casefold()
                localized = bool(new_issues) and any(
                    token.casefold() in searchable
                    for token in localization_tokens
                )
                validator_results[validator_id] = {
                    "accepted": reports[validator_id]["accepted"],
                    "error_count": len(reports[validator_id]["errors"]),
                    "new_error_count": len(new_issues),
                    "detected_by_new_error": bool(new_issues),
                    "localized": localized,
                    "new_errors": new_issues,
                }
            mutation_records.append(
                {
                    "case_id": case_id,
                    "mutation_id": mutation_id,
                    "applicable": True,
                    "localization_tokens": localization_tokens,
                    "validators": validator_results,
                }
            )

    expected_valid_denominator = sum(
        1 for item in baseline_records if item["expected_valid"]
    )
    validator_metrics: dict[str, Any] = {}
    for validator_id in validator_ids:
        false_positives = sum(
            1
            for item in baseline_records
            if item["expected_valid"]
            and not item["validators"][validator_id]["accepted"]
        )
        applicable = [
            item
            for item in mutation_records
            if item["applicable"]
        ]
        detected = [
            item
            for item in applicable
            if item["validators"][validator_id]["detected_by_new_error"]
        ]
        localized = [
            item
            for item in detected
            if item["validators"][validator_id]["localized"]
        ]
        validator_metrics[validator_id] = {
            "expected_valid_case_denominator": expected_valid_denominator,
            "baseline_false_positive_count": false_positives,
            "baseline_false_positive_rate": (
                round(false_positives / expected_valid_denominator, 6)
                if expected_valid_denominator
                else None
            ),
            "applicable_mutation_denominator": len(applicable),
            "detected_mutation_count": len(detected),
            "mutation_detection_rate": (
                round(len(detected) / len(applicable), 6)
                if applicable
                else None
            ),
            "localized_detection_count": len(localized),
            "localization_rate_among_detected": (
                round(len(localized) / len(detected), 6)
                if detected
                else None
            ),
        }

    return {
        "reference_label_definition": (
            "The source case is labeled expected-valid only when its "
            "independently persisted assembly report has status=valid and "
            "ok=true. Validators are evaluated on a newly assembled in-memory "
            "V2 instance from that case's v0.5 input, never on the checked-in "
            "V2 instance."
        ),
        "suite_scope": (
            "These mutation types rely on V2-only constructs and are reported "
            "separately from the common Direct-Wiring comparison denominator."
        ),
        "detection_definition": (
            "A mutation is detected only when the mutated copy produces at "
            "least one error signature absent from that validator's baseline "
            "report; a pre-existing baseline rejection cannot count as a "
            "mutation detection."
        ),
        "localization_definition": (
            "A detected mutation is localized when a new issue mentions at "
            "least one deterministic mutation-specific id or field token."
        ),
        "baseline_cases": baseline_records,
        "mutation_runs": mutation_records,
        "validator_metrics": validator_metrics,
    }


def _aggregate_counts(
    records: Sequence[Mapping[str, Any]],
    path: Sequence[str],
    keys: Sequence[str],
) -> dict[str, int]:
    result = {key: 0 for key in keys}
    for record in records:
        value: Any = record
        for part in path:
            value = value[part]
        for key in keys:
            result[key] += int(value.get(key) or 0)
    return result


def _adapter_metrics(adapter: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    tier_counts = Counter(
        item["selected_tier"] for item in adapter["responsibilities"]
    )
    resolution_counts = Counter(
        item["resolution"] for item in adapter["responsibilities"]
    )
    ownership_denominator = len(adapter["responsibilities"])
    ownership = {
        "scene_object_denominator": ownership_denominator,
        "selected_tier_counts": {
            tier: tier_counts[tier]
            for tier in ("asset", "group", "zone", "unassigned")
        },
        "resolution_counts": {
            state: resolution_counts[state]
            for state in ("unique", "ambiguous", "unassigned")
        },
        "unique_responsibility_rate": (
            round(resolution_counts["unique"] / ownership_denominator, 6)
            if ownership_denominator
            else None
        ),
    }
    status_counts = Counter(
        item["status"] for item in adapter["routing_probes"]
    )
    unique_denominator = sum(
        status_counts[state]
        for state in (
            "local_owner",
            "direct_allowed",
            "transitive_allowed",
            "rejected_unreachable",
        )
    )
    one_hop = status_counts["local_owner"] + status_counts["direct_allowed"]
    reachable = one_hop + status_counts["transitive_allowed"]
    routing = {
        "routing_probe_denominator": len(adapter["routing_probes"]),
        "definition": "one probe per sceneObject and modeled start Agent",
        "unique_target_probe_denominator": unique_denominator,
        "status_counts": {
            state: status_counts[state]
            for state in (
                "local_owner",
                "direct_allowed",
                "transitive_allowed",
                "rejected_unreachable",
                "ambiguous_target",
                "unassigned_target",
            )
        },
        "one_hop_structural_coverage": (
            round(one_hop / unique_denominator, 6)
            if unique_denominator
            else None
        ),
        "graph_reachability_coverage": (
            round(reachable / unique_denominator, 6)
            if unique_denominator
            else None
        ),
        "answer_semantics_evaluated": False,
    }
    agent_ids = list(adapter["agent_ids"])
    pair_denominator = len(agent_ids) * max(0, len(agent_ids) - 1)
    declared = {
        (source, target)
        for source, targets in adapter["handoff_graph"].items()
        for target in targets
        if source != target
    }
    reachable_pairs = {
        (source, target)
        for source in agent_ids
        for target in agent_ids
        if source != target
        and _shortest_path(
            adapter["handoff_graph"],
            source,
            target,
        )
        is not None
    }
    graph = {
        "ordered_agent_pair_denominator_excluding_self": pair_denominator,
        "declared_direct_handoff_count": len(declared),
        "rejected_direct_pair_count": pair_denominator - len(declared),
        "graph_reachable_pair_count": len(reachable_pairs),
        "graph_unreachable_pair_count": pair_denominator - len(reachable_pairs),
    }
    return ownership, routing, graph


def build_benchmark(repo_root: Path = REPOSITORY_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    case_payloads: list[
        tuple[str, dict[str, Any], dict[str, Any], dict[str, Any]]
    ] = []
    corpus: list[dict[str, Any]] = []
    ownership_cases: list[dict[str, Any]] = []
    routing_cases: list[dict[str, Any]] = []
    comparison_cases: list[dict[str, Any]] = []
    checked_in_staleness: list[dict[str, Any]] = []

    for case_id in CASE_IDS:
        paths = _case_paths(repo_root, case_id)
        missing = [
            str(path)
            for key, path in paths.items()
            if key != "case_dir" and not path.is_file()
        ]
        if missing:
            raise FileNotFoundError(
                f"Case {case_id} is incomplete: {', '.join(missing)}"
            )
        checked_in_instance = _read_json(paths["v2"])
        v05 = _read_json(paths["v05"])
        fresh_instance = assemble_v2_instance(v05)
        agent_roles = _read_json(paths["agent_roles"])
        scene_semantics = _read_json(paths["scene_semantics"])
        handoff_matrix = _read_json(paths["handoff_matrix"])
        corpus_record = _corpus_record(
            repo_root,
            case_id,
            paths,
            checked_in_instance,
        )
        fresh_adapter = _fresh_v2_adapter(fresh_instance)
        ownership_metrics, routing_metrics, graph_metrics = _adapter_metrics(
            fresh_adapter
        )
        corpus_record["fresh_v2_semantic_projection_sha256"] = (
            _projection_sha256(fresh_adapter)
        )
        corpus.append(corpus_record)
        ownership_cases.append(
            {
                "case_id": case_id,
                "metrics": ownership_metrics,
                "asset_responsibilities": fresh_adapter[
                    "responsibilities"
                ],
                "treatment_source": (
                    "fresh in-memory V2 regenerated from v0.5"
                ),
            }
        )
        routing_cases.append(
            {
                "case_id": case_id,
                "metrics": routing_metrics,
                "handoff_graph_metrics": graph_metrics,
                "routing_probes": fresh_adapter["routing_probes"],
                "treatment_source": (
                    "fresh in-memory V2 regenerated from v0.5"
                ),
            }
        )
        stale_pipeline = _pipeline_validation(
            checked_in_instance,
            agent_roles,
        )
        fresh_pipeline = _pipeline_validation(
            fresh_instance,
            agent_roles,
        )
        checked_in_staleness.append(
            {
                "case_id": case_id,
                "checked_in_v2_sha256": corpus_record["v2_sha256"],
                "checked_in_pipeline_accepted": stale_pipeline[
                    "accepted"
                ],
                "checked_in_pipeline_errors": stale_pipeline["errors"],
                "fresh_pipeline_accepted": fresh_pipeline["accepted"],
                "fresh_pipeline_errors": fresh_pipeline["errors"],
                "stale_rejection_resolved_by_fresh_regeneration": (
                    not stale_pipeline["accepted"]
                    and fresh_pipeline["accepted"]
                ),
            }
        )
        comparison_cases.append(
            _common_comparison_for_case(
                case_id=case_id,
                scene_semantics=scene_semantics,
                agent_roles=agent_roles,
                handoff_matrix=handoff_matrix,
                fresh_v2=fresh_instance,
            )
        )
        case_payloads.append(
            (case_id, fresh_instance, agent_roles, corpus_record)
        )

    corpus_totals = {
        key: sum(int(case["counts"][key]) for case in corpus)
        for key in (
            "objects",
            "agents",
            "scene_objects",
            "object_groups",
            "semantic_zones",
            "capabilities",
            "capability_uses",
            "scenario_steps",
            "runtime_actions",
            "validation_cases",
        )
    }
    ownership_tiers = _aggregate_counts(
        ownership_cases,
        ("metrics", "selected_tier_counts"),
        ("asset", "group", "zone", "unassigned"),
    )
    ownership_resolutions = _aggregate_counts(
        ownership_cases,
        ("metrics", "resolution_counts"),
        ("unique", "ambiguous", "unassigned"),
    )
    ownership_denominator = sum(
        item["metrics"]["scene_object_denominator"]
        for item in ownership_cases
    )
    routing_statuses = _aggregate_counts(
        routing_cases,
        ("metrics", "status_counts"),
        (
            "local_owner",
            "direct_allowed",
            "transitive_allowed",
            "rejected_unreachable",
            "ambiguous_target",
            "unassigned_target",
        ),
    )
    routing_denominator = sum(
        item["metrics"]["routing_probe_denominator"]
        for item in routing_cases
    )
    unique_routing_denominator = sum(
        item["metrics"]["unique_target_probe_denominator"]
        for item in routing_cases
    )
    one_hop = (
        routing_statuses["local_owner"]
        + routing_statuses["direct_allowed"]
    )
    reachable = one_hop + routing_statuses["transitive_allowed"]
    comparison_aggregate = _aggregate_common_comparison(comparison_cases)
    priority_probe_suite = _aggregate_synthetic_priority_probes(
        comparison_cases
    )

    return {
        "schema": BENCHMARK_SCHEMA,
        "schema_version": BENCHMARK_VERSION,
        "scope": {
            "case_ids": list(CASE_IDS),
            "api_calls": 0,
            "unity_runtime_started": False,
            "structural_routing_evaluated": True,
            "answer_semantics_evaluated": False,
            "human_outcomes_evaluated": False,
        },
        "corpus": {
            "cases": corpus,
            "aggregate_counts": corpus_totals,
        },
        "ownership": {
            "priority_rule": "Asset > Group > Zone",
            "case_results": ownership_cases,
            "aggregate": {
                "scene_object_denominator": ownership_denominator,
                "selected_tier_counts": ownership_tiers,
                "resolution_counts": ownership_resolutions,
                "unique_responsibility_rate": (
                    round(
                        ownership_resolutions["unique"]
                        / ownership_denominator,
                        6,
                    )
                    if ownership_denominator
                    else None
                ),
            },
        },
        "routing": {
            "case_results": routing_cases,
            "aggregate": {
                "routing_probe_denominator": routing_denominator,
                "unique_target_probe_denominator": (
                    unique_routing_denominator
                ),
                "status_counts": routing_statuses,
                "one_hop_structural_coverage": (
                    round(one_hop / unique_routing_denominator, 6)
                    if unique_routing_denominator
                    else None
                ),
                "graph_reachability_coverage": (
                    round(reachable / unique_routing_denominator, 6)
                    if unique_routing_denominator
                    else None
                ),
                "answer_semantics_evaluated": False,
            },
        },
        "direct_wiring_comparison": {
            "aggregate": comparison_aggregate,
            "case_results": comparison_cases,
            "synthetic_priority_probe_suite": priority_probe_suite,
            "fairness_contract": {
                "same_scene_object_ids": True,
                "same_agent_source_ids": True,
                "same_responsibility_priority": "Asset > Group > Zone",
                "same_object_by_start_agent_probe_definition": True,
                "direct_wiring_object_universe": (
                    "unique grounded_object_ids in agent_roles; zone-only "
                    "semantic references are disclosed but excluded because "
                    "they are not executable Agent-grounding targets"
                ),
                "treatment_uses_checked_in_stale_v2": False,
                "treatment_source": (
                    "fresh in-memory V2 regenerated from each v0.5 instance"
                ),
                "direct_wiring_sources": [
                    "scene_semantics.json",
                    "agent_roles.generated.json",
                    "handoff_matrix.json",
                ],
                "answer_semantics_evaluated": False,
                "synthetic_priority_probes_mixed_with_natural_corpus": False,
            },
        },
        "v2_only_validation": _validation_evaluation(case_payloads),
        "checked_in_v2_staleness_audit": {
            "case_denominator": len(checked_in_staleness),
            "checked_in_rejection_count": sum(
                not item["checked_in_pipeline_accepted"]
                for item in checked_in_staleness
            ),
            "fresh_regeneration_acceptance_count": sum(
                item["fresh_pipeline_accepted"]
                for item in checked_in_staleness
            ),
            "resolved_stale_rejection_count": sum(
                item[
                    "stale_rejection_resolved_by_fresh_regeneration"
                ]
                for item in checked_in_staleness
            ),
            "cases": checked_in_staleness,
        },
        "legacy_direct_wiring_comparison": {
            "status": comparison_aggregate["status"],
            "superseded_by": "direct_wiring_comparison",
            "numeric_results": comparison_aggregate["adapter_metrics"],
        },
        "limitations": [
            (
                "Routing metrics measure references and graph reachability, "
                "not whether a generated answer is correct, useful or trusted."
            ),
            (
                "Transitive paths show graph reachability; they do not claim "
                "that a deployed runtime permits multiple handoffs per turn."
            ),
            (
                "The corpus contains three authored rooms and does not support "
                "population-level or subjective usability claims."
            ),
            (
                "Runtime measurements cover normalized adapter construction "
                "and structural route enumeration from parsed artifacts; "
                "they exclude JSON I/O, Unity and V2 generation."
            ),
            (
                "The direct-wiring artifacts contain no object-group "
                "relationship. Their Group tier is explicit but empty; "
                "baseline comparability is therefore established only because "
                "all 93 baseline objects resolve at the higher Asset tier. "
                "Separate synthetic candidate-set probes exercise Group and "
                "Zone fallback without being mixed into natural-corpus counts."
            ),
        ],
    }


def _git_commit(repo_root: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
    except Exception:
        return None


def build_environment(repo_root: Path = REPOSITORY_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    sources = []
    for relative in VALIDATOR_SOURCE_PATHS:
        path = repo_root / relative
        sources.append(
            {
                "path": relative.as_posix(),
                "sha256": _sha256(path),
            }
        )
    inputs = []
    for case_id in CASE_IDS:
        paths = _case_paths(repo_root, case_id)
        for role in (
            "v2",
            "assembly_report",
            "v05",
            "scene_semantics",
            "agent_roles",
            "handoff_matrix",
        ):
            path = paths[role]
            inputs.append(
                {
                    "case_id": case_id,
                    "role": role,
                    "path": _relative(repo_root, path),
                    "sha256": _sha256(path),
                }
            )
    try:
        jsonschema_version = importlib.metadata.version("jsonschema")
    except importlib.metadata.PackageNotFoundError:
        jsonschema_version = None
    clock = time.get_clock_info("perf_counter")
    return {
        "schema": "iui2027_benchmark_environment",
        "schema_version": BENCHMARK_VERSION,
        "command": (
            "python research/iui2027/evaluation/run_benchmark.py"
        ),
        "git_commit": _git_commit(repo_root),
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "dependencies": {"jsonschema": jsonschema_version},
        "runtime_measurement": {
            "clock": "time.perf_counter_ns",
            "clock_implementation": clock.implementation,
            "clock_resolution_seconds": clock.resolution,
            "monotonic": clock.monotonic,
            "adjustable": clock.adjustable,
            "warmups_per_case": 4,
            "repetitions_per_case": 40,
            "alternating_execution_order": True,
            "json_io_included": False,
            "v05_to_v2_generation_included": False,
        },
        "validator_and_benchmark_sources": sources,
        "input_files": inputs,
        "network_required": False,
        "api_key_required": False,
    }


def _format_rate(value: Any) -> str:
    return "n/a" if value is None else f"{100 * float(value):.1f}%"


def _format_value(value: Any) -> str:
    return "n/a" if value is None else str(value)


def render_tables(results: Mapping[str, Any]) -> str:
    lines = [
        "# IUI 2027 Structural System Benchmark",
        "",
        (
            "All values below are computed without API calls. Routing is "
            "structural; answer semantics and human outcomes are not scored."
        ),
        "",
        "## Corpus",
        "",
        "| Case | V2 SHA-256 | Objects | Agents | Scene objects | Groups | Zones |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for case in results["corpus"]["cases"]:
        counts = case["counts"]
        lines.append(
            "| {case} | `{sha}` | {objects} | {agents} | {assets} | "
            "{groups} | {zones} |".format(
                case=case["case_id"],
                sha=case["v2_sha256"],
                objects=counts["objects"],
                agents=counts["agents"],
                assets=counts["scene_objects"],
                groups=counts["object_groups"],
                zones=counts["semantic_zones"],
            )
        )

    lines.extend(
        [
            "",
            "## Responsibility resolution",
            "",
            "| Case | Denominator | Asset tier | Group tier | Zone tier | Unique | Ambiguous | Unassigned |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for case in results["ownership"]["case_results"]:
        metrics = case["metrics"]
        tiers = metrics["selected_tier_counts"]
        resolution = metrics["resolution_counts"]
        lines.append(
            "| {case} | {denom} | {asset} | {group} | {zone} | "
            "{unique} | {ambiguous} | {unassigned} |".format(
                case=case["case_id"],
                denom=metrics["scene_object_denominator"],
                asset=tiers["asset"],
                group=tiers["group"],
                zone=tiers["zone"],
                unique=resolution["unique"],
                ambiguous=resolution["ambiguous"],
                unassigned=resolution["unassigned"],
            )
        )

    lines.extend(
        [
            "",
            "## Structural routing from every start agent",
            "",
            "| Case | Probe denominator | Local owner | Direct allowed | Transitive allowed | Rejected unreachable | One-hop coverage | Graph reachability |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for case in results["routing"]["case_results"]:
        metrics = case["metrics"]
        statuses = metrics["status_counts"]
        lines.append(
            "| {case} | {denom} | {local} | {direct} | {transitive} | "
            "{rejected} | {one_hop} | {reachable} |".format(
                case=case["case_id"],
                denom=metrics["routing_probe_denominator"],
                local=statuses["local_owner"],
                direct=statuses["direct_allowed"],
                transitive=statuses["transitive_allowed"],
                rejected=statuses["rejected_unreachable"],
                one_hop=_format_rate(
                    metrics["one_hop_structural_coverage"]
                ),
                reachable=_format_rate(
                    metrics["graph_reachability_coverage"]
                ),
            )
        )

    comparison = results["direct_wiring_comparison"]
    lines.extend(
        [
            "",
            "## Executable Direct-Wiring comparison",
            "",
            f"**Comparability:** `{comparison['aggregate']['status']}`",
            "",
            (
                "The Direct-Wiring adapter reads the existing scene "
                "semantics, Agent roles and handoff matrix. The treatment is "
                "freshly regenerated in memory from v0.5."
            ),
            "",
            "### Semantic parity",
            "",
            "| Case | Objects | Object x start-Agent probes | Baseline mismatches | Common mutations | Mutated mismatches | Excluded zone-only references |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for case in comparison["case_results"]:
        parity = case["baseline_parity"]
        mutation_mismatches = sum(
            mutation["parity"]["mismatch_count"]
            for mutation in case["mutation_runs"]
        )
        excluded = case["direct_wiring_object_universe"][
            "zone_only_reference_ids_excluded"
        ]
        lines.append(
            "| {case} | {objects} | {probes} | {baseline_mismatches} | "
            "{mutations} | {mutation_mismatches} | {excluded} |".format(
                case=case["case_id"],
                objects=parity["responsibility_denominator"],
                probes=parity["routing_probe_denominator"],
                baseline_mismatches=parity["mismatch_count"],
                mutations=len(case["mutation_runs"]),
                mutation_mismatches=mutation_mismatches,
                excluded=", ".join(f"`{item}`" for item in excluded)
                if excluded
                else "none",
            )
        )
    lines.extend(
        [
            "",
            (
                "The routeable Direct-Wiring object universe is the union of "
                "`grounded_object_ids`. Zone-only references are disclosed "
                "above and excluded because they are not Agent-grounding "
                "targets."
            ),
            "",
            "### Synthetic priority-rule probes",
            "",
        ]
    )
    priority_suite = comparison["synthetic_priority_probe_suite"]
    lines.extend(
        [
            (
                f"**Status:** `{priority_suite['status']}`. These probes are "
                "derived copies and are not included in natural-corpus "
                "ownership or routing metrics."
            ),
            "",
            "| Case | Derived object | Direct passed | Fresh V2 passed | Group fallbacks | Zone fallbacks | Ambiguity fail-closed | Parity mismatches |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for case in priority_suite["case_results"]:
        adapter_counts = {}
        for adapter_id in ("direct_wiring", "fresh_v2"):
            observations = [
                probe["adapters"][adapter_id]
                for probe in case["probe_results"]
            ]
            adapter_counts[adapter_id] = {
                "passed": sum(item["passed"] for item in observations),
                "group": sum(
                    item["observed_selected_tier"] == "group"
                    and item["observed_resolution"] == "unique"
                    for item in observations
                ),
                "zone": sum(
                    item["observed_selected_tier"] == "zone"
                    and item["observed_resolution"] == "unique"
                    for item in observations
                ),
                "fail_closed": sum(
                    item["ambiguity_fail_closed"]
                    for item in observations
                ),
            }
        lines.append(
            "| {case} | `{asset}` | {direct_passed}/3 | {v2_passed}/3 | "
            "{group}/2 | {zone}/2 | {fail_closed}/2 | {mismatches} |".format(
                case=case["case_id"],
                asset=case.get("asset_id", "n/a"),
                direct_passed=adapter_counts["direct_wiring"]["passed"],
                v2_passed=adapter_counts["fresh_v2"]["passed"],
                group=sum(
                    item["group"] for item in adapter_counts.values()
                ),
                zone=sum(
                    item["zone"] for item in adapter_counts.values()
                ),
                fail_closed=sum(
                    item["fail_closed"]
                    for item in adapter_counts.values()
                ),
                mismatches=case["semantic_parity_mismatch_count"],
            )
        )
    lines.extend(
        [
            "",
            (
                "The Group candidate is added identically to normalized "
                "copies because the natural Direct-Wiring artifacts contain "
                "no group relation. These probes test priority behavior, not "
                "native Direct-Wiring Group expressiveness."
            ),
            "",
            "### Validation and edit effort on the common denominator",
            "",
            "| Adapter | Expected-valid denominator | False positives | Common mutation denominator | Detected | Detection rate | Localized | Localization rate | Artifact edits | Reference edits |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for adapter_id, metrics in sorted(
        comparison["aggregate"]["adapter_metrics"].items()
    ):
        lines.append(
            "| {adapter} | {valid_denom} | {fp} | {mutation_denom} | "
            "{detected} | {detection_rate} | {localized} | "
            "{localization_rate} | {artifact_edits} | "
            "{reference_edits} |".format(
                adapter=adapter_id,
                valid_denom=metrics["expected_valid_case_denominator"],
                fp=metrics["baseline_false_positive_count"],
                mutation_denom=metrics["common_mutation_denominator"],
                detected=_format_value(
                    metrics["detected_mutation_count"]
                ),
                detection_rate=_format_rate(
                    metrics["mutation_detection_rate"]
                ),
                localized=_format_value(
                    metrics["localized_detection_count"]
                ),
                localization_rate=_format_rate(
                    metrics["localization_rate"]
                ),
                artifact_edits=_format_value(
                    metrics["artifact_edit_count"]
                ),
                reference_edits=_format_value(
                    metrics["reference_edit_count"]
                ),
            )
        )
    lines.extend(
        [
            "",
            (
                "Common denominators contain only the three semantically "
                "equivalent mutations: missing ownership, duplicate owner and "
                "dangling handoff. V2-only mutations are excluded."
            ),
            "",
            "### Repeated local structural runtime",
            "",
            "| Case | Repetitions | Direct median (ns) | Fresh V2 median (ns) | V2/direct ratio | Deterministic outputs |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for case in comparison["case_results"]:
        runtime = case["runtime"]
        lines.append(
            "| {case} | {repetitions} | {direct} | {treatment} | "
            "{ratio} | {deterministic} |".format(
                case=case["case_id"],
                repetitions=runtime["repetitions"],
                direct=runtime["direct_wiring"]["median_ns"],
                treatment=runtime["fresh_v2"]["median_ns"],
                ratio=_format_value(
                    runtime[
                        "median_runtime_ratio_fresh_v2_over_direct"
                    ]
                ),
                deterministic=str(
                    runtime["deterministic_workload_outputs"]
                ).lower(),
            )
        )

    lines.extend(
        [
            "",
            "## V2-only validator behavior",
            "",
            (
                "These mutations exercise V2-only constructs and are not "
                "included in the Direct-Wiring common denominator."
            ),
            "",
            "| Validator | Expected-valid denominator | False positives | V2-only mutation denominator | Detected | Detection rate | Localized among detected |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for validator_id, metrics in sorted(
        results["v2_only_validation"]["validator_metrics"].items()
    ):
        lines.append(
            "| {validator} | {valid_denom} | {fp} | {mutation_denom} | "
            "{detected} | {detection_rate} | {localization_rate} |".format(
                validator=validator_id,
                valid_denom=metrics["expected_valid_case_denominator"],
                fp=metrics["baseline_false_positive_count"],
                mutation_denom=metrics[
                    "applicable_mutation_denominator"
                ],
                detected=metrics["detected_mutation_count"],
                detection_rate=_format_rate(
                    metrics["mutation_detection_rate"]
                ),
                localization_rate=_format_rate(
                    metrics["localization_rate_among_detected"]
                ),
            )
        )
    stale = results["checked_in_v2_staleness_audit"]
    lines.extend(
        [
            "",
            "## Checked-in V2 staleness audit",
            "",
            (
                f"Checked-in provider-contract rejections: "
                f"{stale['checked_in_rejection_count']}/"
                f"{stale['case_denominator']}; fresh in-memory regeneration "
                f"accepted: {stale['fresh_regeneration_acceptance_count']}/"
                f"{stale['case_denominator']}."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_artifacts(
    output_dir: Path,
    results: Mapping[str, Any],
    environment: Mapping[str, Any],
) -> dict[str, Path]:
    output_dir = Path(output_dir).resolve()
    paths = {
        "results": output_dir / "results.json",
        "tables": output_dir / "tables.md",
        "environment": output_dir / "environment.json",
    }
    _write_text(paths["results"], _json_text(results))
    _write_text(paths["tables"], render_tables(results))
    _write_text(paths["environment"], _json_text(environment))
    return paths


def run(
    *,
    repo_root: Path = REPOSITORY_ROOT,
    output_dir: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path]]:
    repo_root = Path(repo_root).resolve()
    output_dir = (
        Path(output_dir).resolve()
        if output_dir is not None
        else repo_root / "research" / "iui2027" / "evaluation"
    )
    results = build_benchmark(repo_root)
    environment = build_environment(repo_root)
    paths = write_artifacts(output_dir, results, environment)
    return results, environment, paths


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the API-free IUI 2027 structural system benchmark."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPOSITORY_ROOT,
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    results, _, paths = run(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
    )
    summary = {
        "schema": results["schema"],
        "case_count": len(results["corpus"]["cases"]),
        "scene_object_denominator": results["ownership"]["aggregate"][
            "scene_object_denominator"
        ],
        "routing_probe_denominator": results["routing"]["aggregate"][
            "routing_probe_denominator"
        ],
        "direct_wiring_comparison_status": results[
            "direct_wiring_comparison"
        ]["aggregate"]["status"],
        "common_mutation_denominator_per_adapter": results[
            "direct_wiring_comparison"
        ]["aggregate"]["adapter_metrics"]["direct_wiring"][
            "common_mutation_denominator"
        ],
        "synthetic_priority_probe_status": results[
            "direct_wiring_comparison"
        ]["synthetic_priority_probe_suite"]["status"],
        "answer_semantics_evaluated": False,
        "artifacts": {
            key: str(path) for key, path in paths.items()
        },
    }
    print(_json_text(summary), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
