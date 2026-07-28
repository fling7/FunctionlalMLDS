# IUI 2027 framing

## Working title

**Model-Grounded Interaction Contracts for Traceable Spatial Agent Interfaces
in Unity**

Short alternative:

**Model-Grounded Authoring for Spatially Situated Agents in Unity**

## One-sentence contribution

We present and evaluate a model-grounded interaction-assurance layer for
LLM-enabled spatial agents in Unity. It validates stable object references,
responsibilities, capabilities, handoffs, and observed outcomes through an
executable interaction contract, while a limited authoring workbench supports
reversible placement changes.

## HCI problem

Building a room with conversational agents is not only a scene-generation
problem. A person expects pointing to an object and asking “What is this?” to
reach the responsible agent, use the intended knowledge, and fail visibly when
the reference is ambiguous. An author expects these relationships to remain
understandable when an object, zone, capability, or responsible agent changes.
In conventional Unity prototypes, the relevant decisions are distributed across
scene objects, configuration files, prompts, and backend code. This makes
interaction failures hard to explain and authoring changes error-prone.

## Proposed approach

FunctionalMLDS is the interaction contract underneath the authoring interface,
not the paper’s sole subject. It explicitly connects:

1. a user-facing scenario and spatial target;
2. Unity entities, groups, zones, and stable scene-object bindings;
3. embodied agents and their modeled responsibilities;
4. capability use, provider selection, and permitted handoffs;
5. validated Unity/backend runtime actions; and
6. assertions and runtime evidence.

The authoring system derives and previews these links from a structured room
description and materializes the result in Unity and the agent backend. Authors
can inspect every link; the implemented workbench revises placement only, while
typed responsibility, capability, and handoff edits remain a roadmap. At
runtime, a ray-selected object becomes a validated spatial context. The model
determines the responsible agent and allowed capability path; observable events
close the trace back to the user-facing scenario.

## Concrete running example

A visitor selects the Unity object `brand_panel3` in the Steinpilz exhibition
room and asks a grounded question.

1. Unity maps the collider to `ENT-ASSET-BRAND_PANEL3`.
2. The backend validates the entity and pinned model hash before the response
   stub.
3. The capability use names the asset, branding group, entrance zone, and
   responsible Reception Agent.
4. From the Lounge Host, one declared handoff reaches that provider; from the
   Career Advisor, the required two-hop route is rejected before the stub.
5. The runtime binding maps the grounded-answer capability to
   `RA-STEINPILZ_BRAND_ROOM-BACKEND-CHAT` (`POST /chat`).
6. The admitted path returns the structural verdict `accepted_with_evidence`
   and preserves target, provider, capability-use, capability, binding, and
   action IDs. The grounded-answer assertion remains declared rather than
   independently judged for semantic correctness.

This is the implemented end-to-end contract exercised by the Unity batch
smokes and backend tests. The evaluation does not ask an online model to judge
its own answer: it measures stable target preservation, provider selection,
permitted execution, and observation-backed contract verdicts. Semantic or
biological correctness of a dinosaur description remains outside the reported
claims.

## Research questions

**RQ1 — Interaction representation and execution.**

Can assets in heterogeneous scenes be represented as provider-coherent
interaction chains and resolved to responsible agents under explicit asset,
group, and zone rules?

**RQ2 — Comparative structural robustness.**

Under semantically matched executable adapters, how do direct wiring and the
model-grounded representation compare in routing parity, detection and
localization of common faults, representation edits, and local execution time?

**RQ3 — Runtime accountability and author control.**

Which invalid selections, routes, and traces are rejected before state
mutation, and can an author preview, validate, discard, or undo a placement
change without breaking the model-to-runtime chain?

The paper does not claim improved subjective user experience unless a valid
human-participant study is completed. Without such a study, human-centric value
is addressed through concrete user tasks, inspectable explanations, correction
mechanisms, and observable system behavior.

## Intended contributions

1. A model-grounded authoring and runtime-contract architecture for spatial
   embodied-agent interfaces, implemented as a Unity desktop prototype and a
   multi-agent backend.
2. An executable interaction chain from scenario and selected spatial target to
   responsible agent, capability, runtime action, assertion, and evidence.
3. An author-facing inspect, preview, validate, discard, and undo loop for
   generated agent placements. Responsibility editing remains outside the
   current prototype.
4. A reproducible, API-free structural benchmark over multiple spatial
   environments, plus positive and deliberately broken Unity/backend traces.
5. An executable comparison with direct artifact wiring, bounded to measured
   routing parity, synthetic faults, representation edits, and descriptive
   local runtime.

## Defensible novelty

Prior work separately covers model-based interface development, conversational
XR authoring, spatially grounded agents, and LLM multi-agent orchestration. The
novelty claim is their explicit engineering connection: a single executable
model links interaction requirements, spatial Unity entities, agent
capabilities, backend actions, and runtime validation evidence.

The paper must not claim to be the first Unity, XR, LLM, embodied-agent,
model-based UI, or multi-agent system.

## Claim boundary

We may claim technical feasibility, measured interaction correctness, explicit
traceability, and observed effects in executed benchmark changes.

We must not claim:

- superior conversational quality without independent semantic evaluation;
- improved usability, trust, workload, or preference without a valid study;
- broad generalization beyond the evaluated scenes;
- full EAST-ADL compliance without independent conformance evidence;
- automatic repair effectiveness without systematic fault injection;
- causal superiority over manual authoring without a fair executed baseline;
- evaluated WebXR interaction until a real controller and headset path is tested.

## Paper narrative

1. An author turns a spatial scene description into a multi-agent interface.
2. A visitor points to an object and asks an underspecified question.
3. Direct wiring hides reference resolution and routing across assets and code.
4. The proposed interface makes those decisions visible and makes placement
   reversibly editable.
5. FunctionalMLDS stores them as an executable interaction contract.
6. Unity and the backend execute only contract-valid actions and handoffs.
7. Runtime evidence explains whether the intended interaction succeeded.
8. A controlled benchmark tests grounding, routing, evolution, and failures.
