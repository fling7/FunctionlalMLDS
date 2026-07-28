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
- [ ] R1.10 Rebuild, rerun all gates, push, and resubmit.

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
