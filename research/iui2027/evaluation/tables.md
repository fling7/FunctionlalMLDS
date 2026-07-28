# IUI 2027 Structural System Benchmark

All values below are computed without API calls. Routing is structural; answer semantics and human outcomes are not scored.

## Corpus

| Case | V2 SHA-256 | Objects | Agents | Scene objects | Groups | Zones |
|---|---|---:|---:|---:|---:|---:|
| bestfit_career_fair | `861e3569b4c82c4e7d5e486dfce24343b237f3a1ef0056d512ca0795811e077e` | 293 | 5 | 27 | 12 | 6 |
| classroom_dinosaur | `5fe7e33d91933a87dcb25539f68ec34b6751950216bb121dfbe83ee61066451c` | 292 | 4 | 36 | 5 | 4 |
| steinpilz_brand_room | `56658f5e72532753d6163a5f93bd8517e4f9e8e963c79ed74965f71c9c096431` | 296 | 6 | 30 | 9 | 8 |

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

| Case | Repetitions | Direct median (ns) | Fresh V2 median (ns) | V2/direct ratio | Deterministic outputs |
|---|---:|---:|---:|---:|---|
| bestfit_career_fair | 40 | 1279400 | 3529650 | 2.758832 | true |
| classroom_dinosaur | 40 | 1510800 | 5265200 | 3.485041 | true |
| steinpilz_brand_room | 40 | 1954350 | 5235700 | 2.678998 | true |

## V2-only validator behavior

These mutations exercise V2-only constructs and are not included in the Direct-Wiring common denominator.

| Validator | Expected-valid denominator | False positives | V2-only mutation denominator | Detected | Detection rate | Localized among detected |
|---|---:|---:|---:|---:|---:|---:|
| canonical_v2 | 3 | 0 | 9 | 3 | 33.3% | 100.0% |
| pipeline_agent_provider_contract | 3 | 0 | 9 | 9 | 100.0% | 100.0% |

## Checked-in V2 staleness audit

Checked-in provider-contract rejections: 3/3; fresh in-memory regeneration accepted: 3/3.
