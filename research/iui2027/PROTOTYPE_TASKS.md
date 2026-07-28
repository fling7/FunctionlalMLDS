# Prototype and evaluation task list

Last updated: 2026-07-29

This list follows the paper's actual claim boundary: a Unity desktop
prototype, a model-constrained agent backend, a limited placement-authoring
loop, and a deterministic structural system evaluation. A checked task has
implementation, an automated check, and inspectable evidence. Features listed
as out of scope are not silently treated as missing evidence; the paper does
not claim them.

## P0 — Reproducible demonstrator

- [x] Select `steinpilz_brand_room` as the canonical walkthrough and explain why
      the scene exercises assets, groups, zones, several agents, and handoffs.
- [x] Provide one artifact command that validates frozen inputs, fresh V2
      models, benchmark evidence, backend contracts, Unity integration, paper
      hygiene, and anonymity.
- [x] Record Python, Unity, package, OS, LLM, prompt, sampling, repair, and
      benchmark settings.
- [x] Make deterministic regeneration work without an API key or network
      access.
- [x] Hash immutable inputs and reject stale checked-in V2 instances.
- [x] Publish validated regenerated artifacts for all three cases.
- [x] Provide a scripted, review-anonymous Unity capture command pinned to
      the walkthrough's exact project, entity, source ID, and collider.

Evidence: `artifact/README.md`, `artifact/regenerate_frozen.py`,
`artifact/regeneration-summary.json`, `evaluation/environment.json`.

## P1 — Stable Unity-to-model bindings

- [x] Add `FunctionalMldsSceneObjectBinding` with stable model/source IDs,
      group, zone, display name, collider, and synonyms.
- [x] Add a registry that resolves bindings by stable IDs rather than
      GameObject-name heuristics.
- [x] Validate missing, duplicate, stale, unknown, and ambiguous bindings
      fail-closed.
- [x] Expose the loaded entity, group, zone, agent, and responsibility
      relations to the QuickAgent bridge.
- [x] Add static, edit-mode, and batch-mode Unity checks.

Acceptance met: a relevant collider resolves to exactly one V2 entity, while an
invalid or ambiguous binding is blocked with an explicit state.

## P2 — Deictic spatial selection

- [x] Implement a shared desktop ray-selection abstraction.
- [x] Preserve the selected target while a request is composed and sent.
- [x] Highlight the selected object and show a human-readable selection state.
- [x] Distinguish resolved, no-target, and ambiguous states.
- [x] Block a deictic request without exactly one target before an LLM call.
- [x] Exercise serialization and fail-closed selection in a real Unity
      batch-mode smoke.

Acceptance met for the desktop path. WebXR controller and gaze input are
explicitly outside the evaluated prototype.

## P3 — Validated spatial chat contract

- [x] Send structured spatial context containing the pinned model hash, stable
      entity/source ID, hit coordinates, distance, modality, and ambiguity.
- [x] Validate model hash, entity, interaction mode, and request size before
      history or session state changes.
- [x] Derive group and zone on the server from the trusted model.
- [x] Reject malformed, forged, stale, unknown, and ambiguous contexts before
      an LLM call.
- [x] Return trusted entity IDs, model-binding IDs, evidence references, and a
      routing explanation.
- [x] Keep a non-deictic request fail-closed when the model contains no unique
      targetless action chain.
- [x] Cover valid, tampered, drifted, ambiguous, and no-mutation paths in
      backend tests.

Acceptance met: invalid spatial context cannot invoke the model or mutate chat
history; a valid path retains the selected entity in response evidence.

## P4 — Model-constrained providers and handoffs

- [x] Attribute each asset-facing capability and scenario step to its
      responsible domain agent, not a generic orchestrator.
- [x] Generate one scene-specific use case with a three-step interaction chain
      for every grounded asset.
- [x] Carry `use_case_id` and `scenario_id` on each runtime action chain.
- [x] Resolve responsibility deterministically in the order asset, group, zone.
- [x] Evaluate only the highest matching tier and reject a tie at that tier.
- [x] Restrict online handoff choices to the selected chain's modeled targets.
- [x] Select deictic chat/handoff mappings by trusted target and provider before
      LLM execution.
- [x] Regenerate and validate every evaluated V2 case and backend project.

Acceptance met: 93 authored assets have a unique natural-corpus owner and an
explicit provider-specific execution chain.

## P5 — Executable scenario and runtime evidence

- [x] Connect target resolution, routing, chat, response, and handoff events to
      the scenario runner.
- [x] Prevent an answer transition until target and provider checks succeed.
- [x] Implement eight runtime probes for binding, target, scenario,
      capability, provider, response, route, and observed assertion state.
- [x] Produce `pass`, `fail`, `inconclusive`, and `error` from observations
      rather than equating transport success with correctness.
- [x] Retain model, scenario, capability-use, binding, action, provider, and
      target IDs in runtime evidence.
- [x] Exercise the native scenario, QuickAgent bridge, and spatial grounding in
      three real Unity batch-mode smokes.

Acceptance met for the tested Unity desktop and deterministic backend paths.
The smokes establish contract execution, not conversational answer quality.

## P6 — Placement-authoring transaction

- [x] Inspect stable agent IDs, current coordinates, revision, and content hash.
- [x] Preview structured before/after coordinates without writing files.
- [x] Apply only against the inspected revision, then regenerate and validate.
- [x] Keep a successful change pending until explicit acceptance or discard.
- [x] Roll back byte-exactly after a generation/validation failure.
- [x] Support discard and one-level undo of the last accepted placement.
- [x] Disable commit while a decision is pending and reject revision conflicts.
- [x] Expose the six authoring operations through backend routes and Unity UI.
- [x] Report free-text edit attempts as not applied rather than inventing a
      model mutation.

Acceptance met by 12 placement tests, including four paper-level transactional
workflows. Responsibility editing is not claimed.

## P7 — Fair structural comparison

- [x] Implement a normalized direct-artifact adapter and a freshly regenerated
      V2 adapter over the same cases.
- [x] Compare all natural-corpus ownership and routing decisions.
- [x] Inject the same provider, asset, group, zone, and ambiguity conditions
      into both adapters.
- [x] Inject three shared mutation classes per case and distinguish detection
      from localization.
- [x] Add V2-only mutations to describe validator expressiveness without
      mislabeling them as baseline failures.
- [x] Count edited artifacts and references separately.
- [x] Measure local deterministic execution time with median, quartiles, IQR,
      and range; exclude network and LLM latency.
- [x] Report every numerator, denominator, error, and input hash in JSON and
      generated tables.

Acceptance met: both adapters preserve all measured natural and common-mutation
decisions; the paper reports representation tradeoffs rather than superiority.

## P8 — Anonymous verification artifact

- [x] Provide frozen, API-free regeneration for all three cases.
- [x] Provide a one-command verifier and machine-readable atomic summary.
- [x] Add a data dictionary, environment record, anonymity policy, and explicit
      license-status file.
- [x] Exclude tokens, reviewer responses, build products, and local toolchains
      from Git.
- [x] Scan source, supplement, PDF metadata, logs, and generated summaries for
      identities, local paths, and secrets.
- [x] Pass the final post-paper artifact run with all tests, all three real
      Unity smokes, the strict paper check, and no skips in claimed components.

Final evidence: `artifact/verification-summary.json` reports `overall_status:
pass`, no failed mandatory checks, real Unity execution, and no network or
model-API use.

## Deliberately outside the current claims

- WebXR controller, gaze, microphone, or physical-headset evaluation;
- free-form responsibility/capability editing in Unity;
- subjective usability, trust, workload, preference, or participant outcomes;
- semantic or factual quality of generated answers;
- autonomous repair effectiveness or a human maintenance-time advantage;
- broad generalization beyond the three purposively selected development cases.

These are future-study tasks, not prerequisites hidden behind the current
system/computational claims.
