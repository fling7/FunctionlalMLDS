# Artifact data dictionary

## Cases and source records

| Field or file | Meaning |
|---|---|
| `case_id` | Stable fixture identifier. The set is `bestfit_career_fair`, `classroom_dinosaur`, and `steinpilz_brand_room`. |
| `input/source_mlds.json` | Authored spatial scene description used as the original case input. |
| `input/source_mlds.sha256` | SHA-256 of the exact source JSON bytes. A mismatch is a stale-input failure. |
| `functionalmlds.instance.generated.json` | Version 0.5 FunctionalMLDS pipeline input from which V2 is regenerated in memory. |
| `functionalmlds.v2.instance.json` | Checked-in V2 snapshot. It is hashed and audited; the fair benchmark treatment is freshly regenerated instead. |
| `functionalmlds.v2.assembly_report.json` | Canonical and pipeline validation evidence associated with the checked-in V2 snapshot. |
| `scene_semantics.json` | Direct-Wiring baseline's normalized scene objects, groups and zones. |
| `agent_roles.generated.json` | Direct-Wiring baseline's modeled agents and spatial responsibilities. |
| `handoff_matrix.json` | Direct-Wiring baseline's allowed source-to-target handoffs. |

`steinpilz_brand_room` is the canonical walkthrough, while all three cases
form the benchmark corpus.

## Structural benchmark

| Field | Denominator and interpretation |
|---|---|
| `scene_object_denominator` | Every routeable scene object across the three cases. |
| `selected_tier_counts` | Number resolved at Asset, Group, Zone, or unassigned priority. |
| `resolution_counts` | Number with unique, ambiguous, or missing responsibility. |
| `routing_probe_denominator` | Cartesian product of every routeable object and every modeled start agent within each case. |
| `status_counts` | Local, direct-handoff, transitively reachable, or unreachable structural route. |
| `common_mutation_denominator` | Controlled mutations expressible in both Direct-Wiring and fresh-V2 representations. |
| `detected_mutation_count` | Mutations for which an independent validator adds the expected new issue. |
| `localization_rate` | Detected mutations whose new issue names the changed object, agent, or field token. |
| `fresh_v2_acceptance_count` | Fresh in-memory V2 instances accepted by canonical and provider-contract validation. |
| `checked_in_v2_rejection_count` | Checked-in snapshots rejected by the current pipeline contract. Nonzero is a release-verification failure. |

Timing values are descriptive local microbenchmarks. They include adapter
construction and route enumeration after JSON parsing; they exclude file I/O,
V2 generation, Unity and network activity. They are not a claim of user-facing
latency improvement.

## `verification-summary.json`

| Field | Meaning |
|---|---|
| `overall_status` | `pass` only when every mandatory check passed. |
| `network_used` / `model_api_used` | Fixed `false`; no default verification step has a network implementation. |
| `unity_started` | Whether a Unity executable was supplied explicitly. |
| `benchmark_mode` | `check` for committed hash/evidence validation or `run` for temporary regeneration. |
| `checks[].status` | `pass`, `fail`, or `not_run`. An optional Unity check may be `not_run` without failing the artifact. |
| `checks[].facts` | Non-sensitive counts, versions, hashes, test-module names and bounded outcomes. |
| `checks[].issues` | Sanitized diagnostic text with local paths and addresses removed. |
| `failed_mandatory_check_ids` | Stable identifiers for every unresolved release blocker. |

The summary deliberately contains no timestamp, hostname, absolute path,
reviewer address, token, API key, raw model response, Unity log, or full
subprocess output.

## Out-of-scope outcomes

The artifact does not contain labels for answer correctness, usefulness,
usability, trust, workload, preference, or other human outcomes. A structural
route only means that the model specifies a responsibility/handoff path; it
does not establish that a generated answer is semantically good.

