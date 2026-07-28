# IUI 2027 structural system benchmark

Run from the repository root:

```powershell
python research/iui2027/evaluation/run_benchmark.py
```

The command regenerates:

- `results.json`: machine-readable corpus, responsibility, routing, parity,
  mutation, validation, edit-effort and timing results;
- `tables.md`: paper-ready summaries with explicit denominators;
- `environment.json`: hashes of every input and implementation source plus
  the local timing environment.

It performs no network or model API calls and does not start Unity.

## Fair executable comparison

The benchmark evaluates two normalized adapters over the same cases:

1. **Direct-Wiring baseline.** It reads the existing
   `scene_semantics.json`, `agent_roles.generated.json` and
   `handoff_matrix.json` artifacts.
2. **FunctionalMLDS V2 treatment.** It regenerates a new V2 instance in
   memory from each checked-in v0.5 instance. The checked-in V2 files are
   hashed and audited for staleness but are never used as treatment input.

Both adapters expose the same source Agent IDs, apply the same
`Asset > Group > Zone` rule and enumerate one routing probe for every
routeable object and every modeled start Agent. In the Direct-Wiring
artifacts, the routeable object universe is the union of Agent
`grounded_object_ids`. Zone-only references are disclosed separately because
they are not executable Agent-grounding targets. The current corpus therefore
contains 93 routeable objects and 15 Agents.

Comparability is fail-closed. Baseline and treatment must agree on Agent IDs,
object IDs, handoff graph, selected responsibility and every object-by-start-
Agent route. The same parity check is repeated after every common mutation.
All mismatches are retained in `results.json`; metrics on the common
denominator become `n/a` when parity fails.

The natural corpus resolves all 93 objects at the Asset tier. A separate
synthetic micro-benchmark therefore exercises the complete priority rule on
three derived copies per case:

- remove Asset candidates and require a unique Group fallback;
- remove Asset and Group candidates and require a unique Zone fallback;
- add a competing owner at the highest active tier and require an ambiguous,
  fail-closed result for every start Agent.

These 18 adapter observations (three probes × three cases × two adapters) are
reported separately and never added to natural-corpus ownership or routing
denominators. The same Group candidate is added to normalized copies of both
adapters because the Direct-Wiring sources have no native group relationship.
Consequently, these probes test priority behavior but do not establish native
Direct-Wiring Group expressiveness.

## Mutations and validators

The common comparison applies three deterministic mutations that both
representations can express:

- remove all ownership paths for one object;
- assign a second Asset-level owner;
- replace one handoff target with the same dangling source ID.

Each representation has its own validator and is evaluated by error delta:
only an issue absent from its unmodified baseline counts as detection.
Localization requires the new issue to mention a mutation-specific object,
Agent or field token. Results include false positives and both artifact- and
reference-edit counts.

V2-only mutations are reported in a separate suite and never added to the
common denominator. This prevents V2-only expressiveness from being counted
as a Direct-Wiring failure.

Runtime is a descriptive local microbenchmark. It alternates adapter order,
uses four warm-ups and 40 measured repetitions per case, and checks that every
run produces the same semantic projection hash. It includes normalized
adapter construction and route enumeration from already parsed artifacts; it
excludes JSON I/O, v0.5-to-V2 generation, Unity and all network activity. No
inferential performance advantage is claimed.

## Interpretation boundary

The benchmark answers structural questions only:

- Does a routeable object resolve to exactly one modeled responsible Agent?
- Is that Agent local, directly reachable, transitively reachable or
  unreachable from each modeled start Agent?
- Do independent validators add a localized issue after a controlled
  mutation?
- How many stored artifacts and references must be changed to express that
  mutation?

It does **not** measure answer correctness, usefulness, user experience,
trust, end-to-end latency or whether a deployed runtime permits a multi-hop
handoff in one turn. The three authored rooms do not support population-level
or subjective usability claims.
