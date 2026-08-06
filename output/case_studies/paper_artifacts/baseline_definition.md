# Baseline and Treatment Definition

## Purpose

This document defines the empirical comparison used by the FunctionalMLDS case study. The goal is not to show that the existing Interactive Agents pipeline is unusable. The goal is to isolate what the FunctionalMLDS metamodel adds: explicit traceability, staged validation, repairable intermediate artefacts and runtime-checkable behaviour.

## Baseline A: Direct MLDSI-to-Interactive-Agents Generation

Baseline A is the existing Interactive Agents project generation workflow implemented by the Unity `ArrowProjectWizard` and the Python backend.

### Entry Point

- Unity editor tool: `InteractivAgents/InteractiveAgents2/Assets/Scripting/ArrowProjectWizard.cs`
- Backend endpoints:
  - `POST /projects/arrow/analyze`
  - `POST /projects/arrow/chat`
  - `POST /projects/arrow/commit`
- Backend implementation:
  - `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/state.py`
  - `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/schemas.py`
  - `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/projects.py`

### Input

- One MLDSI/MLDS JSON file describing a room or scene.
- Optional user feedback through the Wizard chat loop.

### Transformation

The backend sends the MLDSI/MLDS JSON plus conversational history to an LLM and requests a structured `arrow_project` draft. The draft contains:

- project metadata,
- agent specifications,
- knowledge entries,
- placement preview.

The commit step writes the generated project to the backend project store.

### Output Artefacts

Baseline A creates or updates:

- `project.json`
- `room_plan.json`
- `agents.json`
- project-local `kb/<tag>/<entry>.txt`
- optional placement preview returned to Unity

### Validation Already Present

Baseline A has useful implementation-level safeguards:

- structured LLM output schema for the generated project draft,
- normalized agent IDs, voice settings and knowledge tags,
- placement normalization against the provided room plan,
- backend checks for existing project IDs and basic request validity.

### Explicitly Missing In Baseline A

Baseline A does not create an explicit FunctionalMLDS instance. Therefore the following constructs are missing as first-class, inspectable artefacts:

- UseCase and Scenario decomposition,
- ScenarioStep sequence with guards and effects,
- Requirement-to-validation links,
- Capability and CapabilityUse elements,
- RuntimeBinding and RuntimeAction elements,
- explicit trace from MLDS object groups to agent roles, knowledge, capabilities and runtime events,
- stage manifest with per-stage hashes, validation status and repair attempts.

These missing items are not implementation bugs. They define the comparison boundary: Baseline A is direct artefact generation, while Treatment B is metamodel-mediated artefact generation.

## Treatment B: FunctionalMLDS-Mediated Generation

Treatment B is the pipeline implemented under `tools/case_study_pipeline`.

### Entry Point

- Batch runner: `tools/case_study_pipeline/run_batch_case_study.py`
- Inputs can be passed through `--inputs` or `--input-glob`.

### Input

- The same MLDS/MLDSI scene files used by Baseline A.

### Transformation

Treatment B introduces explicit intermediate stages:

1. MLDS ingestion and normalization.
2. Scene semantics extraction.
3. Agent role and handoff modelling.
4. Knowledge synthesis.
5. Agent placement.
6. FunctionalMLDS instance assembly.
7. Project materialization into the Interactive Agents backend format.
8. Schema, invariant and traceability validation.
9. Runtime setup, chat tests, handoff tests and answer-grounding checks.
10. Cross-case and generalizability assessment.

### Output Artefacts

Treatment B creates the same deployable target class as Baseline A, but additionally creates:

- `functionalmlds/functionalmlds.instance.generated.json`
- per-stage `stage_manifest.json`
- `validation/*.json` reports,
- generated evaluation questions,
- runtime chat and handoff logs,
- aggregate reports and paper artefacts.

## Controlled Variables

The comparison should keep these factors constant where possible:

- same input MLDS/MLDSI files,
- same Interactive Agents backend target format,
- same runtime endpoints for setup and chat,
- same domain corpus,
- same LLM model family when LLM calls are required,
- same maximum repair budget for Treatment B where repair loops are evaluated.

## Comparison Scope

Baseline A and Treatment B should be compared on the generated evidence, not only on visual plausibility.

Included:
- traceability,
- consistency,
- runtime-checkability,
- generalizability,
- repairability,
- reproducibility of intermediate artefacts.

Excluded from the primary comparison:
- photorealistic quality of Unity visuals,
- subjective conversational pleasantness,
- performance benchmarking of Unity rendering,
- end-user usability of the editor UI.

## Expected Result Pattern

Baseline A is expected to be competitive for quick project creation because it directly produces usable Interactive Agents artefacts. Treatment B is expected to be stronger for scientific evaluation because it produces explicit, inspectable and checkable intermediate representations.

The central claim is therefore:

FunctionalMLDS does not replace the Interactive Agents generator. It wraps and structures the generation process so that the resulting agent system can be traced, validated, repaired and compared across domains.
