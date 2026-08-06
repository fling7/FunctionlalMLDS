# IUI 2027 Structural System Benchmark

All values below are computed without API calls. Routing is structural; answer semantics and human outcomes are not scored.

## Corpus

| Case | V2 SHA-256 | Objects | Agents | Scene objects | Groups | Zones |
|---|---|---:|---:|---:|---:|---:|
| bestfit_career_fair | `6231d576becf69ae3e593e75e5075329c530285fb4aebd36d5182c16f2697c17` | 1208 | 5 | 27 | 12 | 6 |
| classroom_dinosaur | `36ad81efdc00b09e50b1433b75e74688bfdc0579a5deb86585efca056f6b4428` | 1522 | 4 | 36 | 5 | 4 |
| steinpilz_brand_room | `5615722da2d20f2cd850f69dd27a8501f7939f581514aa79d75b2ee2526216bf` | 1316 | 6 | 30 | 9 | 8 |

## Complete asset-specific interaction chains (RQ1)

The asset denominator contains every `sceneObject`, even when no chain exists. The chain denominator contains every `ScenarioStep`/`CapabilityUse` pair that explicitly targets a scene object. A complete chain resolves Capability, provider, target, RuntimeBinding/RuntimeAction and a UseCase-linked ValidationCase covering the step's resulting assertions.

| Case | Asset denominator | Assets with chain | Complete assets | Asset completeness | Chain denominator | Complete chains | Chain completeness | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bestfit_career_fair | 27 | 27 | 27 | 100.0% | 54 | 54 | 100.0% | 0 |
| classroom_dinosaur | 36 | 36 | 36 | 100.0% | 72 | 72 | 100.0% | 0 |
| steinpilz_brand_room | 30 | 30 | 30 | 100.0% | 60 | 60 | 100.0% | 0 |
| **Aggregate** | 93 | 93 | 93 | 100.0% | 186 | 186 | 100.0% | 0 |

No asset-chain errors were observed.

## Responsibility resolution

| Case | Denominator | Asset tier | Group tier | Zone tier | Unique | Ambiguous | Unassigned |
|---|---:|---:|---:|---:|---:|---:|---:|
| bestfit_career_fair | 27 | 27 | 0 | 0 | 27 | 0 | 0 |
| classroom_dinosaur | 36 | 36 | 0 | 0 | 36 | 0 | 0 |
| steinpilz_brand_room | 30 | 30 | 0 | 0 | 30 | 0 | 0 |

## Structural routing from every start agent

| Case | Probe denominator | Local owner | Direct allowed | Transitive allowed | Rejected unreachable | One-hop coverage | Graph reachability |
|---|---:|---:|---:|---:|---:|---:|---:|
| bestfit_career_fair | 135 | 27 | 53 | 55 | 0 | 59.3% | 100.0% |
| classroom_dinosaur | 144 | 36 | 81 | 9 | 18 | 81.2% | 87.5% |
| steinpilz_brand_room | 180 | 30 | 71 | 79 | 0 | 56.1% | 100.0% |

## API-free fresh-V2 SessionStore runtime corpus (RQ3)

The expectation for each row comes from the independent Direct-Wiring artifacts. Each observed result executes a materialized project, verified equal to fresh V2 regenerated in the same run, through `SessionStore.chat` with a deterministic structured-response stub and an active network guard. The complete per-probe records are stored in `results.json`.

| Case | Probes | Local | Direct | Transitive | Unreachable | Accepted with target/provider/binding evidence | Rejected before stub and mutation | Stub calls | Passed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bestfit_career_fair | 135 | 27 | 53 | 55 | 0 | 80/80 | 55/55 | 80 | 135/135 |
| classroom_dinosaur | 144 | 36 | 81 | 9 | 18 | 117/117 | 27/27 | 117 | 144/144 |
| steinpilz_brand_room | 180 | 30 | 71 | 79 | 0 | 101/101 | 79/79 | 101 | 180/180 |
| **Aggregate** | 459 | 93 | 205 | 143 | 18 | 298/298 | 161/161 | 298 | 459/459 |

## Executable Direct-Wiring comparison

**Comparability:** `comparable`

The Direct-Wiring adapter reads the existing scene semantics, Agent roles and handoff matrix. The treatment is freshly regenerated in memory from v0.5.

### Semantic parity

| Case | Objects | Object x start-Agent probes | Baseline mismatches | Common mutations | Mutated mismatches | Excluded zone-only references |
|---|---:|---:|---:|---:|---:|---|
| bestfit_career_fair | 27 | 135 | 0 | 3 | 0 | none |
| classroom_dinosaur | 36 | 144 | 0 | 3 | 0 | none |
| steinpilz_brand_room | 30 | 180 | 0 | 3 | 0 | `floor_marking_path1` |

The routeable Direct-Wiring object universe is the union of `grounded_object_ids`. Zone-only references are disclosed above and excluded because they are not Agent-grounding targets.

### Synthetic priority-rule probes

**Status:** `pass`. These probes are derived copies and are not included in natural-corpus ownership or routing metrics.

| Case | Derived object | Direct passed | Fresh V2 passed | Group fallbacks | Zone fallbacks | Ambiguity fail-closed | Parity mismatches |
|---|---|---:|---:|---:|---:|---:|---:|
| bestfit_career_fair | `bar_stool_refreshment1` | 3/3 | 3/3 | 2/2 | 2/2 | 2/2 | 0 |
| classroom_dinosaur | `beanbag1` | 3/3 | 3/3 | 2/2 | 2/2 | 2/2 | 0 |
| steinpilz_brand_room | `brand_panel1` | 3/3 | 3/3 | 2/2 | 2/2 | 2/2 | 0 |

The Group candidate is added identically to normalized copies because the natural Direct-Wiring artifacts contain no group relation. These probes test priority behavior, not native Direct-Wiring Group expressiveness.

### Validation and edit effort on the common denominator

| Adapter | Expected-valid denominator | False positives | Common mutation denominator | Detected | Detection rate | Localized | Localization rate | Artifact edits | Reference edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| direct_wiring | 3 | 0 | 9 | 9 | 100.0% | 9 | 100.0% | 15 | 15 |
| fresh_v2 | 3 | 0 | 9 | 9 | 100.0% | 9 | 100.0% | 9 | 18 |

Common denominators contain only the three semantically equivalent mutations: missing ownership, duplicate owner and dangling handoff. V2-only mutations are excluded.

### Repeated local structural runtime

| Case | Repetitions | Direct median [Q1, Q3] ns | Direct min-max ns | Fresh V2 median [Q1, Q3] ns | Fresh V2 min-max ns | V2/direct median ratio | Deterministic outputs |
|---|---:|---:|---:|---:|---:|---:|---|
| bestfit_career_fair | 40 | 1322300 [1166550.0, 1516050.0] | 704300-16690400 | 10057300 [7783575.0, 11572800.0] | 5853300-85286700 | 7.605914 | true |
| classroom_dinosaur | 40 | 1245750 [772225.0, 1608575.0] | 708500-155640200 | 9438950 [5681400.0, 13336025.0] | 4717200-282907700 | 7.576922 | true |
| steinpilz_brand_room | 40 | 1044050 [991775.0, 1694000.0] | 941800-3108200 | 6151450 [4951225.0, 7308525.0] | 4444100-9323400 | 5.891911 | true |

## V2-only validator behavior

These mutations exercise V2-only constructs and are not included in the Direct-Wiring common denominator.

| Validator | Expected-valid denominator | False positives | V2-only mutation denominator | Detected | Detection rate | Localized among detected |
|---|---:|---:|---:|---:|---:|---:|
| canonical_v2 | 3 | 0 | 9 | 3 | 33.3% | 100.0% |
| pipeline_agent_provider_contract | 3 | 0 | 9 | 9 | 100.0% | 100.0% |

## Checked-in V2 staleness audit

Checked-in provider-contract rejections: 0/3; fresh in-memory regeneration accepted: 3/3.
