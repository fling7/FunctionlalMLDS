# Redacted reviewer iterations

This file contains only non-secret editorial summaries. Access tokens,
authorized contact data, and raw service responses remain in ignored private
paths.

## Iteration 1 — 2026-07-29

Paper commit: `1a50dec`

Overall assessment: the external reviewer recommends acceptance, but makes the
recommendation contingent on a clearer concrete walkthrough, stronger
authorization/governance positioning, and—if feasible—additional external or
human evidence. Because the recommendation is conditional, this iteration does
not yet satisfy the project exit criterion.

### Strengths retained

- technically solid, fail-closed Unity/backend interaction contract;
- unusually precise claim boundaries and limitations;
- deterministic, API-free evaluation and complete reproduction harness;
- exhaustive enforcement probes with clean rollback;
- strong fit to traceable spatial-agent interaction at IUI.

### Revision tasks

- [x] R1.1 Add a concrete main-text walkthrough from Unity selection through
      provider, capability, action, returned evidence, and assertion outcome;
      show both admitted and fail-closed paths. The revision reports the
      structural contract verdict and explicitly distinguishes it from the
      declared but not semantically judged assertion.
- [x] R1.2 Add an actual Unity prototype view and replace or relocate the dense
      metamodel overview so the interaction path is easier to read.
- [x] R1.3 Compare the contract with current delegation/authorization,
      event-sourced orchestration, capability-governance, XR routing, and
      scenario-control work using verified primary sources.
- [x] R1.4 Explain pinned-model behavior for runtime scene change, transactional
      refresh, session isolation, and unsupported multi-user concurrency.
- [x] R1.5 Clarify stable-ID behavior for prefab duplication, instantiation,
      and scene merges, including which cases fail validation.
- [x] R1.6 Clarify that online handoff is one hop per turn and how a later turn
      is re-admitted under the pinned contract.
- [x] R1.7 State the artifact-release boundary and the path to public-sample
      replication without claiming an unavailable redistribution license.
- [x] R1.8 Explain the authoring roadmap beyond placement without presenting
      responsibility/capability/handoff editing as implemented.
- [x] R1.9 Retain the explicit limits: shared resolver, internal binding
      consistency, author-authored corpus, synthetic fallback, desktop-only
      Unity paths, no human study, and no full-stack latency claim.
- [x] R1.10 Rebuild, rerun all gates, push, and resubmit.

### Evidence that cannot be manufactured

A developer study, physical-headset evaluation, or genuinely third-party scene
would strengthen external validity, but none may be claimed without new data,
appropriate provenance/licensing, and—where people participate—the applicable
ethics process. These remain future-study items rather than invented
revisions.

### Revision-2 safeguards

- The walkthrough capture is pinned to the exact project, entity, source ID,
  and collider used in the text; locale-independent coordinates support the
  paper annotation.
- A compact main-text table keeps every principal measured result within the
  reviewer's 15-page analysis window.
- Request-decidable preconditions are now separated from response-dependent
  postconditions so the unmodeled-handoff rollback is not overstated.
- The abstract's Unity count is corrected to 31 scenario contexts and 73
  actions.

### Revision-2 local verification

- The strict paper checker passes at 7,052 approximate main-text words and
  verifies that the complete Conclusion ends within the first 15 pages.
- The 21-page anonymous PDF passes veraPDF's PDF/UA-2 profile.
- The exact walkthrough capture resolves `brand_panel3` to
  `ENT-ASSET-BRAND_PANEL3`, logs invariant-culture viewport coordinates, and
  completes with 30 valid scene bindings.
- The full artifact verifier reports `overall_status: pass`, all mandatory
  checks pass, all three real Unity batch smokes observe their OK marker, and
  neither network nor model API is used.

## Iteration 2 — 2026-07-29

Reviewed paper commit: `75c3189`

Reviewer service timestamp: `2026-07-28T23:25:40.557218`

Venue supplied to the reviewer: `ACM IUI 2027`

Overall assessment: the fresh external review recommends acceptance after
minor revisions. It describes the contribution as technically solid,
implemented end to end, useful to the IUI community, and supported by an
evaluation that is convincing for the paper's deliberately bounded claims.
Neither the assessment nor the weakness section identifies a major or critical
issue, and neither recommends rejection. This satisfies the project's
operational review exit criterion.

### Strengths retained

- a coherent and auditable Unity-to-backend interaction contract;
- fail-closed behavior with staged validation and runtime evidence;
- exhaustive probes, deterministic stubs, fault injection, and reproducible
  artifacts that match the bounded claims;
- clear writing, appropriate prior-work context, and practical value for
  spatial and embodied-agent systems.

### Residual minor comments

- A compact main-text presentation of further metamodel cardinalities and
  invariants could help readers; the current detailed material remains in the
  appendix to preserve the IUI review window.
- The comparison with runtime-verification and W3C PROV-style approaches could
  be expanded beyond the current positioning.
- A full-stack latency profile or more upstream deictic-resolver integration
  guidance would be useful, but cannot be claimed from the present local,
  model-API-free measurements.
- External validity remains intentionally limited to three purposively authored
  scenes, a shared resolver, static pinned scenes, and one-hop delegation.

These points do not invalidate a result or require a correction to a central
claim. The manuscript already states the corresponding evidence boundaries;
the measurement- and corpus-expansion items are recorded as future work rather
than being manufactured after review.

### Exit decision

- [x] The textual assessment recommends acceptance.
- [x] No critical or major weakness remains.
- [x] All verdict-changing comments from the prior round were addressed.
- [x] The reviewed PDF is the verified snapshot with SHA-256
      `ade3bcde931e59bc861e3b423cc72c8208c6557dee82eb547f0128415dd59066`.
