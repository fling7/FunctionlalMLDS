# Claim-to-evidence matrix

Last updated: 2026-07-28

No claim may move into the abstract, results, or conclusion until its evidence
row is `ready`. A passing implementation test establishes behavior under the
tested inputs; it is not automatically evidence of usability or generality.

| ID | Candidate claim | Required evidence | Current evidence | Status |
|---|---|---|---|---|
| C1 | FunctionalMLDS links a user scenario through capability use and provider to a concrete runtime action and assertion. | Valid native V2 instances; schema and cross-reference invariants; positive and negative tests. | Native assembler, validator, generated instances, and existing contract tests. Provider semantics are being corrected. | partial |
| C2 | A desktop Unity interaction can resolve a selected scene object to a stable model entity and preserve that target through chat. | Binding-registry tests; deterministic ray-selection cases; live or batch Unity smoke; target ID in request/response evidence. | Existing raycast only selects agents. New implementation and tests are in progress. | pending |
| C3 | The backend rejects stale or forged spatial context before chat state or LLM execution. | Positive, unknown-entity, stale-hash, ambiguous, and no-mutation backend tests. | Existing session/model validation is a base; spatial-context contract is in progress. | pending |
| C4 | Agent routing and handoffs are constrained by modeled asset, group, zone, and handoff relationships. | Deterministic routing tests; forbidden-handoff tests; runtime evidence with routing reasons. | Offline fallback uses modeled targets, but the prior online path allowed every agent. Correction is in progress. | pending |
| C5 | The model-grounded condition detects more injected cross-artifact inconsistencies than direct wiring under the same behavior and inputs. | Executed paired baseline/treatment mutations with immutable inputs, raw outputs, denominators, and uncertainty. | Protocol exists; no fair executed baseline result yet. | pending |
| C6 | Evaluated interactions have complete scenario-to-outcome trace evidence rather than transport-only success. | Live event chain and assertion verdicts; complete runtime-action-to-log coverage; deliberately broken traces. | Current Unity bridge records transport success as inconclusive; live scenario wiring is pending. | pending |
| C7 | The pipeline materializes valid model-grounded configurations for three different spatial cases without case-specific pipeline code. | Fresh atomic regeneration, content hashes, per-case validity, and non-duplicated scene-specific interactions. | Three cases exist, but stored evidence is stale or template-identical in parts. | partial |
| C8 | Structural grounding and semantic response quality are evaluated separately. | Trusted target/agent/capability checks plus expected facts and disallowed claims; judge details if used. | Existing token-overlap metric is insufficient; replacement benchmark is pending. | pending |
| C9 | The artifact is reproducible without private credentials for deterministic checks. | Clean-checkout command, dependency/version record, immutable inputs, machine-readable results, anonymity scan. | Paper build/check and many deterministic tests exist; unified artifact command is pending. | partial |

## Claims intentionally excluded

- improved usability, preference, trust, workload, or perceived control;
- broad generalization beyond the evaluated cases;
- full EAST-ADL conformance;
- the first Unity, XR, LLM-agent, embodied-agent, or model-based UI system;
- evaluated WebXR use before controller and physical-headset evidence exists;
- repair effectiveness before deterministic fault injection is executed.

## Evidence gates for the paper

- The abstract may contain only `ready` claims and their principal measured values.
- Each Results subsection cites machine-readable output paths and states
  numerator, denominator, condition, and exclusions.
- Discussion may interpret measured behavior but may not promote a `partial`
  engineering mechanism into an empirical result.
- Limitations retain every failed, excluded, stale, or untested condition.
