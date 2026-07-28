# Prototype and evaluation task list

Last updated: 2026-07-28

Priority meanings:

- `MUST`: required for defensible IUI main-paper claims.
- `SHOULD`: materially strengthens the submission.
- `COULD`: useful only after every `MUST` item is complete.

A task is complete only when its implementation, automated check, and generated
evidence are present. Tasks are ordered by dependency and are worked through in
this order.

## P0 — Reproducible demonstrator

- [ ] **MUST P0.1** Select `steinpilz_brand_room` as the canonical live
      demonstrator and document why its Unity scene and model belong together.
- [ ] **MUST P0.2** Add a single command that starts or validates the pinned
      backend, Unity project configuration, and selected FunctionalMLDS V2 model.
- [ ] **MUST P0.3** Record Python, Unity, package, OS, LLM, prompt, temperature,
      and seed or stored-response versions.
- [ ] **MUST P0.4** Make the complete non-Unity test suite terminate reliably.
- [ ] **MUST P0.5** Run all tests and archive a machine-readable test summary.
- [ ] **MUST P0.6** Include model, project, backend, prompt, and question hashes
      in stage invalidation so stale runtime evidence cannot be reused.

Acceptance: a fresh checkout deterministically selects the same scene, V2
contract, configuration, and benchmark inputs without manual file selection.

## P1 — Stable Unity-to-model object bindings

- [ ] **MUST P1.1** Add a scene-object binding component containing `entityId`,
      `sourceObjectId`, object group, zone, display name, collider, and optional
      synonyms.
- [ ] **MUST P1.2** Add an editor/runtime registry that resolves bindings by
      stable IDs rather than GameObject-name heuristics.
- [ ] **MUST P1.3** Validate missing, duplicate, stale, and ambiguous bindings
      before interaction starts.
- [ ] **MUST P1.4** Give the QuickAgent bridge read-only access to loaded entity,
      group, zone, agent, and responsibility relationships.
- [ ] **MUST P1.5** Add edit-mode tests for valid and invalid registries.

Acceptance: every semantically relevant demonstrator object maps to exactly one
V2 entity; duplicate or missing IDs fail closed with an actionable diagnostic.

## P2 — Deictic spatial target selection

- [ ] **MUST P2.1** Implement a shared spatial-selection abstraction.
- [ ] **MUST P2.2** Resolve desktop camera raycasts against the binding registry.
- [ ] **MUST P2.3** Keep the selected target stable while a text or voice query
      is composed and sent.
- [ ] **MUST P2.4** Highlight the selected object and show its human-readable name.
- [ ] **MUST P2.5** Represent no target, a resolved target, and ambiguity
      explicitly; ask for clarification instead of guessing.
- [ ] **SHOULD P2.6** Connect a WebXR controller ray to the same abstraction.
- [ ] **COULD P2.7** Add gaze selection after controller selection is stable.

Acceptance: “What is this?” deterministically resolves the correct entity ID for
at least twelve defined desktop targets, and ambiguous cases do not invoke the
LLM.

## P3 — Validated spatial chat contract

- [ ] **MUST P3.1** Extend the Unity request with a structured
      `spatial_context`: model hash, entity/source ID, hit position, distance,
      modality, and ambiguity state.
- [ ] **MUST P3.2** Validate the model hash and entity against the model pinned to
      the backend session before history or session state is mutated.
- [ ] **MUST P3.3** Derive group and zone server-side from trusted model
      relationships; never trust client-supplied responsibility data.
- [ ] **MUST P3.4** Reject unknown, stale, malformed, and ambiguous targets before
      any LLM request.
- [ ] **MUST P3.5** Restrict retrieval to knowledge connected to the resolved
      entity where such knowledge is modeled.
- [ ] **MUST P3.6** Return `grounded_entity_ids`, evidence references, and routing
      reason in the response.
- [ ] **MUST P3.7** Add positive, tampering, model-drift, and no-mutation tests.

Acceptance: a forged entity, wrong model hash, or ambiguous selection is rejected
without changing chat history; a valid request returns the same trusted entity
ID and supporting evidence.

## P4 — Model-constrained providers, routing, and handoffs

- [ ] **MUST P4.1** Make the responsible domain agent, rather than the generic
      runtime orchestrator, provide each user-facing capability.
- [ ] **MUST P4.2** Make `ScenarioStep.performedBy`,
      `CapabilityUse.provider`, responsible zone, grounded asset, and capability
      provider form one valid chain.
- [ ] **MUST P4.3** Resolve object-to-agent responsibility deterministically in
      the order asset, group, then zone.
- [ ] **MUST P4.4** Restrict online structured-output handoff choices to the
      modeled `handoffTarget` set.
- [ ] **MUST P4.5** Validate a handoff before state mutation and expose a concise
      routing explanation to the interface.
- [ ] **MUST P4.6** Add positive and negative provider, routing, and handoff tests.
- [ ] **MUST P4.7** Regenerate every evaluated native V2 instance and verify that
      no user-facing step is attributed to the orchestrator.

Acceptance: no online handoff outside the V2 contract is possible, and each
benchmark target produces a deterministic, explainable responsible agent.

## P5 — Executable interaction scenario and assertions

- [ ] **MUST P5.1** Add or bind a runtime action for spatial target resolution.
- [ ] **MUST P5.2** Connect the existing `ScenarioRunner` to live
      QuickAgentManager selection, routing, chat, response, and handoff events.
- [ ] **MUST P5.3** Prevent an answer-display transition until target resolution
      and agent routing have succeeded.
- [ ] **MUST P5.4** Implement probes for object binding, target resolution,
      entity/capability agreement, agent responsibility, response entity, and
      handoff permission.
- [ ] **MUST P5.5** Replace transport-success `inconclusive` records with real
      `pass` or `fail` verdicts where the required observation exists.
- [ ] **MUST P5.6** Reserve `inconclusive` for genuinely missing observations.
- [ ] **MUST P5.7** Add smoke tests showing valid traces pass and intentionally
      broken traces fail closed.

Acceptance: the live interaction executes the modeled chain
`target → agent → capability → runtime action → response assertion`; it cannot
jump directly from a question to displaying an answer.

## P6 — Scene-specific models and authoring loop

- [ ] **MUST P6.1** Replace the identical hard-coded scenario template with
      interaction elements derived from each evaluated scene and agent set.
- [ ] **MUST P6.2** Generate distinct scenario steps and targets for classroom,
      career-fair, and food/trade-fair cases.
- [ ] **MUST P6.3** Add an explicit “apply changes and regenerate preview” action
      to the FunctionalMLDS authoring UI.
- [ ] **MUST P6.4** Show a before/after diff with affected agents, entities,
      model IDs, explanations, and validation status.
- [ ] **MUST P6.5** Support accept, discard, and undo without restarting.
- [ ] **MUST P6.6** Prove schema and invariant validity and report non-duplicated
      per-case coverage.

Acceptance: an author can inspect, apply, validate, and undo a responsibility or
placement change, and the resulting scene-specific model remains valid.

## P7 — Non-leaking interaction benchmark

- [ ] **MUST P7.1** Remove the correct target agent’s name from handoff questions.
- [ ] **MUST P7.2** Create held-out paraphrases independently of the handoff matrix.
- [ ] **MUST P7.3** Add negative requests, ambiguous references, unknown targets,
      neighboring objects, and partially occluded targets.
- [ ] **MUST P7.4** Store expected target, expected agent, acceptable outcome,
      and rationale separately from the user utterance.
- [ ] **MUST P7.5** Report target-resolution accuracy, routing accuracy, task
      success, false-handoff rate, abstention, interaction steps, and latency
      with confidence intervals where meaningful.
- [ ] **SHOULD P7.6** Have qualified humans inspect a blinded response sample,
      subject to the applicable ethics determination.

Acceptance: no benchmark utterance leaks its expected target or agent, and both
positive and fail-closed behavior are measured.

## P8 — Fair baseline, mutations, and observability

- [ ] **MUST P8.1** Implement a direct-wiring baseline with the same
      Unity/backend behavior but without the FunctionalMLDS control layer.
- [ ] **MUST P8.2** Hold scenes, agents, prompts, questions, model, and runtime
      constant between baseline and treatment.
- [ ] **MUST P8.3** Execute change tasks: rename/move/delete object, reassign
      agent, change zone, change capability, and change endpoint.
- [ ] **MUST P8.4** Deterministically inject missing bindings/providers,
      duplicate IDs, stale hashes, invalid zones, wrong endpoints, unmodeled
      handoffs, and broken traces.
- [ ] **MUST P8.5** Measure edited artifacts, inconsistent references, detection
      and false-positive rates, localization, repair, regeneration, execution
      success, and runtime overhead.
- [ ] **MUST P8.6** Instrument `target_selection_started`, `target_resolved`,
      `target_ambiguous`, `agent_routed`, `grounded_chat_sent`,
      `grounded_response_received`, `grounding_assertion_evaluated`, and
      `task_completed`.
- [ ] **MUST P8.7** Carry model and interaction IDs on every evaluated runtime
      action and obtain complete runtime-action-to-log coverage.

Acceptance: immutable inputs reproduce both conditions and all mutations, with
every reported value traceable to raw events and hashes.

## P9 — Response grounding and human-centric evidence

- [ ] **MUST P9.1** Separate structural grounding from semantic answer quality.
- [ ] **MUST P9.2** Replace single-token overlap as a success criterion with
      case-specific expected facts and disallowed claims.
- [ ] **MUST P9.3** Report lexical, structural, and semantic measures separately.
- [ ] **SHOULD P9.4** Add blinded human or independent-model labels and agreement;
      disclose model judging in Methods.
- [ ] **MUST P9.5** Define end-user tasks and interaction breakdowns before
      interpreting system measurements.
- [ ] **MUST P9.6** State the institution-specific ethics determination accurately.
- [ ] **SHOULD P9.7** Run a preregistered comparative study only if approval,
      recruitment, and the deadline permit it.
- [ ] **MUST P9.8** Without an approved study, remove subjective claims and
      present a system/computational evaluation.

Acceptance: every quality claim names its evidence source; no usability, trust,
workload, preference, or participant claim appears without valid human evidence.

## P10 — XR path and anonymous artifact

- [ ] **MUST P10.1** Describe the implementation as a Unity desktop prototype
      with a WebXR deployment path until controller input and a real-headset test
      are complete.
- [ ] **SHOULD P10.2** Connect controller selection, push-to-talk, subtitles, and
      an XR-readable world-space HUD.
- [ ] **SHOULD P10.3** Test WebGL/WebXR, microphone permission, CORS, local HTTPS,
      and at least one physical headset.
- [ ] **MUST P10.4** Provide a one-command deterministic benchmark requiring no
      private API key.
- [ ] **MUST P10.5** Create an anonymous artifact snapshot with README, license,
      dependency lock, data dictionary, and immutable result inputs.
- [ ] **SHOULD P10.6** Record a captioned anonymous system video.
- [ ] **MUST P10.7** Scan artifact, PDF, video, logs, and metadata for identities,
      local paths, tokens, and secrets.

Acceptance: reviewers can reproduce deterministic checks without credentials;
all XR claims match the interaction path that was actually tested.
