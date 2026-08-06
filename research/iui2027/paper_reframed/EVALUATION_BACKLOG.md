# Evaluation backlog for the IUI submission

This backlog is ordered by expected value for the paper rather than by
implementation convenience.

## P0 — strongly recommended before submission

### 1. Independently authored held-out scene

**Goal:** reduce the current self-authored/corpus-construction threat and
exercise responsibility tiers naturally rather than through derived copies.

**Protocol**

1. Freeze and tag the current resolver, validators, metric code, and paper
   claims before the new case is inspected.
2. Give a fourth room description and authoring instructions to a person who
   did not implement the resolver.
3. Require the case to contain:
   - at least 20 routeable assets;
   - at least four agents;
   - natural asset-, group-, and zone-level ownership;
   - at least one intentionally unassigned asset;
   - at least one genuine highest-tier ambiguity;
   - one direct handoff, one transitive-only path, and one unreachable pair.
4. Do not patch the resolver after seeing the result. Record failures as
   results; any later repair becomes a separate follow-up run.
5. Freeze the expected owner and route table before running the implementation.

**Report**

- complete-chain numerator/denominator;
- ownership outcomes by natural tier;
- expected vs. observed owner and route confusion matrix;
- admission/rejection results;
- stage and relation for every failure;
- any case-generation or validation failure;
- provenance showing that the case was authored independently.

**Best paper use:** a separate held-out subsection, not merged silently into the
development corpus.

### 2. Independent route oracle

The current direct and V2 adapters parse separately but share one routing
classifier. Add an oracle that does not call the production resolver.

Practical options, in preferred order:

1. A declarative CSV/JSON table of `(case, object, start_agent,
   expected_owner, expected_route)` reviewed and frozen before execution.
2. A second minimal resolver implemented by another person from the written
   policy.
3. A property-based reference implementation using a different graph library
   and independent code path.

For the held-out case, manually review all rows. For the current 459 probes,
review a stratified subset covering each route class and each scene. The paper
can then distinguish migration parity from independent conformance.

### 3. Actual diagnostic-surface evidence

The current paper has a real Unity selection image, but detailed contract
evidence is mostly in logs/runtime payloads. Add one implemented developer
surface or inspector that shows:

- selected entity and source ID;
- pinned model hash/version;
- resolved owner and responsibility tier;
- route reason;
- capability use, capability, binding, and action;
- verdict and rejection stage;
- violated relation for a negative case.

Capture at least four deterministic scenarios:

1. valid local answer;
2. valid direct handoff;
3. ambiguous selection;
4. stale model or unreachable provider.

A short anonymous video and a static screenshot would materially improve IUI
fit. Do not present a mock-up as an implemented interface.

## P1 — high value if time, ethics, and participants are available

### 4. Developer diagnosis and repair study

**Research question:** Does the explicit contract help developers diagnose and
repair cross-layer spatial-agent faults compared with direct artifacts?

**Design:** within-subject or counterbalanced mixed design, using equivalent
but non-identical cases. Conditions are direct wiring and contract-grounded
artifacts. Tasks should include one common fault and one cross-layer fault per
condition; do not assign a fault that the baseline cannot represent unless the
task is explicitly framed as a capability difference.

**Primary measures**

- correct diagnosis rate;
- correct repair rate;
- time to diagnosis and repair;
- number of artifacts opened;
- number of incorrect edits or regressions;
- accuracy of the participant's explanation of target, provider, and action.

**Secondary measures**

- perceived mental effort;
- confidence calibrated against correctness;
- qualitative breakdowns and requested evidence.

Complete the applicable ethics process before recruitment. Pre-register
exclusion criteria, counterbalancing, tasks, and primary outcomes. A very small
convenience sample with only Likert ratings would not resolve the current
reviewer concern.

### 5. Independent semantic-answer evaluation

Keep this separate from contract conformance. Use questions with curated
ground-truth answers for a subset of objects and compare:

- correct target but wrong/unconstrained provider;
- contract-grounded provider and knowledge scope;
- abstention or rejection on invalid context.

Score factuality and relevance with human raters or a documented rubric; do not
use the response model as its own judge. This study can show whether the
structural boundary interacts with answer quality, but it is not needed to
validate the current deterministic guarantee.

## P2 — useful extensions, not submission blockers

### 6. Headset/WebXR path

Run the same contract through a physical controller ray or gaze input and
record target identity, ambiguity state, request, and returned evidence. This
would support an XR claim rather than only a Unity desktop claim.

### 7. Concurrent sessions and project evolution

Test:

- several sessions pinned to different model hashes;
- simultaneous writes to one session;
- object creation/deletion and model regeneration;
- explicit migration or rejection of a stale session.

### 8. Broader fault catalogue

Add mutations for duplicate runtime bindings, wrong target in a capability use,
missing assertion coverage, action schema mismatch, contradictory group/zone
membership, duplicate Unity collider binding, and response evidence with a
correct target but wrong provider/action.

## Recommended order

For acceptance probability, the strongest achievable sequence is:

1. held-out independently authored scene;
2. independent route oracle;
3. real diagnostic UI evidence;
4. developer study only if it can be done rigorously.

The first two directly address the current evaluation's circularity and
generality limitations without relying on a rushed human study.
