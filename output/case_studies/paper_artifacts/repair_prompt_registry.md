# Repair Prompt Registry

The case-study pipeline separates primary generation prompts from LLM repair prompts. Repair prompts are only injected after a previous generated artefact exists and validation errors are available.

| Prompt version | File | Used by stage | Purpose |
|---|---|---|---|
| `repair_invalid_object_refs_v1` | `tools/case_study_pipeline/prompts/repair_invalid_object_refs_v1.md` | `scene_semantics` | Repair invalid scene-semantics object references while preserving valid semantic structure. |
| `repair_invalid_handoff_targets_v1` | `tools/case_study_pipeline/prompts/repair_invalid_handoff_targets_v1.md` | `agent_roles` | Repair invalid agent role or handoff references using only allowed IDs. |
| `repair_missing_knowledge_entries_v1` | `tools/case_study_pipeline/prompts/repair_missing_knowledge_entries_v1.md` | `knowledge_synthesis` | Repair missing or invalid knowledge entries for required agent knowledge tags. |
| `repair_missing_capabilities_v1` | `tools/case_study_pipeline/prompts/repair_missing_capabilities_v1.md` | future FunctionalMLDS repair | Prepared prompt for missing Capability, CapabilityUse or RuntimeBinding coverage. |

Implementation note:
The active LLM stages pass the selected repair prompt through `repair_instruction` only when `previous_invalid_output` and `validation_errors` are present. First-pass generation therefore still uses the primary stage prompt only.
