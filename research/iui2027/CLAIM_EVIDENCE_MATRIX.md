# Claim-to-evidence matrix

Last updated: 2026-07-28

No claim may move into the abstract, results, or conclusion until its evidence
row is `ready`. A passing implementation test establishes behavior under the
tested inputs; it is not automatically evidence of usability or generality.

| ID | Candidate claim | Required evidence | Current evidence | Status |
|---|---|---|---|---|
| C1 | FunctionalMLDS links a user scenario through capability use and provider to a concrete runtime action and assertion. | Valid native V2 instances; schema and cross-reference invariants; positive and negative tests. | Fresh models contain complete chains for 93/93 assets and 186/186 asset-targeting answer/handoff steps, with zero structural errors. | ready |
| C2 | A desktop Unity interaction can resolve a selected scene object to a stable model entity and preserve that target through chat. | Binding-registry tests; deterministic ray-selection cases; live or batch Unity smoke; target ID in request/response evidence. | Binding, QuickAgent-bridge, and spatial-grounding Unity batch smokes pass; backend contract tests preserve the server-resolved, model-authorized target in response evidence. | ready |
| C3 | The backend rejects stale or forged spatial context before chat state or LLM execution. | Positive, unknown-entity, stale-hash, ambiguous, and no-mutation backend tests. | The spatial-contract suite passes all 12 tests, including 16 enumerated invalid variants; precondition failures leave both model-call count and history unchanged. | ready |
| C4 | Agent routing and handoffs are constrained by modeled asset, group, zone, and handoff relationships. | Deterministic routing tests; forbidden-handoff tests; runtime evidence with routing reasons. | All 93 natural-corpus assets resolve uniquely at the asset tier. Across 459 source-target pairs, 441 are graph-reachable and 18 are explicitly unreachable; online choices use only the exact selected chain. | ready |
| C5 | Direct wiring and the model-grounded representation preserve the same routing behavior under one fixed decision rule, while differing in explicit structure, edit footprint, validator scope, and local execution cost. | Executed paired baseline/treatment mutations with immutable inputs, raw outputs, denominators, and descriptive timing ranges. | Under the shared deterministic resolver, the adapters agree on 93 ownership and 459 routing decisions and after all 9 shared mutations. Both detect/localize 9/9 shared faults with 0/3 baseline false positives. Edit footprints and timings are reported separately. | ready |
| C6 | Evaluated interactions have complete scenario-to-outcome trace evidence rather than transport-only success. | Live event chain and assertion verdicts; complete runtime-action-to-log coverage; deliberately broken traces. | Eight observation-based probes and structured verdicts are implemented; native-scenario, QuickAgent-bridge, and spatial-grounding Unity batch smokes all pass, including deliberately invalid states. | ready |
| C7 | The pipeline materializes valid model-grounded configurations for three different spatial cases without case-specific pipeline code. | Fresh atomic regeneration, content hashes, per-case validity, and non-duplicated scene-specific interactions. | API-free, network-blocked regeneration validates and publishes all 3/3 cases. Each case has asset-specific use cases and distinct stable hashes. | ready |
| C8 | The evaluation reports structural contract conformance without presenting it as semantic answer quality. | Trusted target/agent/capability checks; explicit scope flags and limitations; no response-quality metric or semantic judge. | The benchmark and manuscript explicitly exclude semantic answer quality and human outcomes. | ready |
| C9 | The artifact is reproducible without private credentials for deterministic checks. | Clean-checkout command, dependency/version record, immutable inputs, machine-readable results, anonymity scan. | Frozen regeneration, one-command verification, immutable hashes, environment metadata, a data dictionary, and anonymity scanning are present. The final full verifier passed every mandatory gate, including three Unity smokes, with no network or model-API use. | ready |

## Claims intentionally excluded

- improved usability, preference, trust, workload, or perceived control;
- broad generalization beyond the evaluated cases;
- full EAST-ADL conformance;
- the first Unity, XR, LLM-agent, embodied-agent, or model-based UI system;
- evaluated WebXR use before controller and physical-headset evidence exists;
- autonomous repair effectiveness or a human maintenance-time advantage.

## Evidence gates for the paper

- The abstract may contain only `ready` claims and their principal measured values.
- Each Results subsection cites machine-readable output paths and states
  numerator, denominator, condition, and exclusions.
- Discussion may interpret measured behavior but may not promote a `partial`
  engineering mechanism into an empirical result.
- Limitations retain every failed, excluded, stale, or untested condition.
