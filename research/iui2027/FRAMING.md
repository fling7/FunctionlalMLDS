# IUI 2027 framing

## Working title

**From Spatial Scene Descriptions to Verifiable Embodied-Agent Interactions:
A Model-Grounded Authoring Interface for Unity**

Short alternative:

**Model-Grounded Authoring for Spatially Situated Agents in Unity**

## One-sentence contribution

We present and evaluate an intelligent authoring interface and runtime layer
that turns structured spatial scene descriptions into embodied Unity agents
while keeping object references, responsibilities, capabilities, handoffs, and
observed outcomes connected through an executable interaction model.

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
description, lets an author inspect and revise them, and materializes the result
in Unity and the agent backend. At runtime, a ray-selected object becomes a
validated spatial context. The model determines the responsible agent and
allowed capability path; observable events close the trace back to the
user-facing scenario.

## Concrete running example

A visitor points at a dinosaur skeleton and asks, “What is this?”

1. Unity maps the selected collider to the modeled `DinosaurSkeleton` entity.
2. The backend validates the entity and model hash before invoking an LLM.
3. The model links the asset to `ExhibitInterpreter`, its
   `DescribeRoomObject` capability, and the `/chat` runtime action.
4. Only modeled handoffs are available.
5. The response returns the grounded entity and evidence references.
6. Runtime probes verify selection, routing, capability use, and response
   grounding and attach the verdicts to the scenario trace.

This example is the target end-to-end behavior. The existing codebase already
contains the model, generation pipeline, backend, Unity agents, and validation
infrastructure; live deictic selection and the complete runtime evidence chain
are implementation work, not pre-existing results.

## Research questions

**RQ1 — Interaction correctness.**  
How accurately does model-grounded execution resolve spatial targets and route
requests to appropriate embodied agents across heterogeneous scenes, including
ambiguous, negative, and changed-scene cases?

**RQ2 — Robust authoring and evolution.**  
Compared with direct artifact wiring, how does the model-grounded workflow
affect consistency, detected configuration faults, and the artifacts that must
be edited when an interaction changes?

**RQ3 — Runtime accountability.**  
To what extent can a user-facing interaction be traced from intent and selected
target through agent capability and runtime action to a validated outcome, and
which failure classes remain observable?

The paper does not claim improved subjective user experience unless a valid
human-participant study is completed. Without such a study, human-centric value
is addressed through concrete user tasks, inspectable explanations, correction
mechanisms, and observable system behavior.

## Intended contributions

1. A model-grounded authoring architecture for spatial embodied-agent
   interfaces, implemented as a Unity desktop prototype with a WebXR deployment
   path and a multi-agent backend.
2. An executable interaction chain from scenario and selected spatial target to
   responsible agent, capability, runtime action, assertion, and evidence.
3. An author-facing inspection and repair loop for generated object, agent,
   placement, responsibility, and handoff relationships.
4. A reproducible benchmark over multiple spatial environments covering target
   resolution, routing, change tasks, trace completeness, and injected faults.
5. Empirical comparison with direct artifact wiring, bounded to measured
   engineering and interaction outcomes.

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
4. The proposed authoring interface makes those decisions visible and editable.
5. FunctionalMLDS stores them as an executable interaction contract.
6. Unity and the backend execute only contract-valid actions and handoffs.
7. Runtime evidence explains whether the intended interaction succeeded.
8. A controlled benchmark tests grounding, routing, evolution, and failures.
