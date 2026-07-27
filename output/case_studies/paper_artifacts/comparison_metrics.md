# Comparison Metrics

## Goal

The comparison metrics evaluate what FunctionalMLDS adds to the existing Interactive Agents generation workflow. The metrics do not treat Baseline A as defective. Baseline A is direct artefact generation. Treatment B is metamodel-mediated generation with explicit traceability, validation and repair artefacts.

## Value Types

| Value kind | Meaning |
|---|---|
| `measured` | The value is already available in generated reports. |
| `explicit_absence` | The compared construct is not a first-class artefact in Baseline A. |
| `requires_baseline_run` | The metric can be computed after running Baseline A on the same corpus. |
| `protocol_defined` | The metric is defined, but needs a targeted follow-up experiment. |

## Metric Catalogue

| ID | RQ | Dimension | Metric | Baseline A | Treatment B |
|---|---|---|---|---|---|
| M1 | RQ1 | Traceability | Explicit FunctionalMLDS instance presence | explicit absence, expected 0.0 | measured 1.0 |
| M2 | RQ1 | Traceability | Average explicit trace coverage | explicit absence, expected 0.0 | measured 0.847222 |
| M3 | RQ1 | Traceability | Requirement-to-validation coverage | explicit absence, expected 0.0 | measured 1.0 |
| M4 | RQ1 | Traceability | Object-group-to-agent grounding | requires baseline run | measured 1.0 |
| M5 | RQ2 | Consistency | Schema and invariant success | explicit absence, expected 0.0 | measured 1.0 |
| M6 | RQ2 | Consistency | Invalid handoff target count | requires baseline run | measured 0 |
| M7 | RQ2 | Consistency | Missing knowledge tag count | requires baseline run | measured 0 |
| M8 | RQ2 | Consistency | Unbound capability count | explicit absence | measured 0 |
| M9 | RQ2 | Runtime-checkability | Handoff decision accuracy | requires baseline run | measured 1.0 |
| M10 | RQ2 | Runtime-checkability | Answer grounding ratio | requires baseline run | measured 1.0 |
| M11 | RQ2 | Repairability | Stage completion ratio | explicit absence, expected 0.0 | measured 1.0 |
| M12 | RQ2 | Repairability | Bounded LLM repair attempt count | explicit absence | measured 0 |
| M13 | RQ3 | Generalizability | Generalizability score | protocol defined | measured 1.0 |
| M14 | RQ3 | Generalizability | Domain term externalization | protocol defined | measured 1.0 |
| M15 | RQ2 | Maintainability | RuntimeBinding substitution locality | explicit absence | protocol defined |

## Metric Families

### Traceability

Traceability metrics test whether the generation process produces explicit links between MLDS scene content, FunctionalMLDS model elements and runtime artefacts. Baseline A can create useful agents and knowledge entries, but it does not expose UseCases, ScenarioSteps, Capabilities, RuntimeBindings or Requirement-to-validation links as first-class artefacts.

Primary metrics:
- M1 explicit model artefact presence.
- M2 average trace coverage.
- M3 requirement-to-validation coverage.
- M4 object-group-to-agent grounding.

### Consistency

Consistency metrics test whether generated artefacts refer to valid targets and satisfy declared invariants. For Treatment B this is measured through schema validation, FunctionalMLDS invariants, handoff metrics and knowledge validation. For Baseline A, agent and knowledge consistency can be measured only after running the Wizard output through an adapter.

Primary metrics:
- M5 schema and invariant success.
- M6 invalid handoff target count.
- M7 missing knowledge tag count.
- M8 unbound capability count.

### Runtime-Checkability

Runtime-checkability metrics test whether the generated system behaves as expected through backend setup, chat, handoff and answer grounding. These metrics are fair to both pipelines if both generate Interactive Agents projects for the same input corpus.

Primary metrics:
- M9 handoff decision accuracy.
- M10 answer grounding ratio.

### Repairability

Repairability metrics test whether failed intermediate outputs can be localized and repaired without restarting the entire generation process. Treatment B records stage status, hashes and bounded repair attempts. Baseline A offers conversational refinement in the Wizard, but not a stage-local repair manifest.

Primary metrics:
- M11 stage completion ratio.
- M12 bounded repair attempt count.

### Generalizability

Generalizability metrics test whether the same implementation works across different MLDS domains without hard-coded domain assumptions. Treatment B already measures this through the generalizability assessment. Baseline A can be assessed with the same domain corpus after direct Wizard generation.

Primary metrics:
- M13 generalizability score.
- M14 domain term externalization.

### Maintainability

Maintainability is kept as a protocol-defined metric because it needs a targeted change experiment. The planned test exchanges a RuntimeBinding and counts whether Scenario or ScenarioStep elements must change. Treatment B is designed for this locality; Baseline A has no explicit RuntimeBinding construct.

Primary metric:
- M15 RuntimeBinding substitution locality.

## Current Treatment Evidence

Current values from the generated reports:

- Average trace coverage: `0.847222`
- Requirement-to-validation coverage: `1.0`
- Object-group coverage: `1.0`
- Schema and invariant success: `3/3`
- Handoff decision accuracy: `1.0`
- Answer grounding ratio: `1.0`
- Stage completion ratio: `1.0`
- Chat tests: `66/66`
- Handoff decision tests: `66`
- LLM generation attempts: `8`
- LLM repair attempts after invalid generated artefacts: `0`
- Deterministic recoveries: `1`
- Accepted traceability warnings: `3`
- Generalizability score: `1.0`
- Domain term externalization: `25` Python files scanned, `0` findings

## Interpretation Rule

For the paper, use two result categories:

1. **Direct comparison metrics**: metrics computable for both Baseline A and Treatment B after running both on the same MLDS corpus, such as handoff accuracy, answer grounding, invalid handoff targets and missing knowledge tags.
2. **Metamodel-added evidence metrics**: metrics that Baseline A cannot express without adding a metamodel layer, such as Requirement-to-validation coverage, Capability binding coverage and stage-local repair tracking.

This distinction prevents the comparison from unfairly penalizing Baseline A for not being designed as a metamodel pipeline, while still making the scientific contribution of FunctionalMLDS measurable.
