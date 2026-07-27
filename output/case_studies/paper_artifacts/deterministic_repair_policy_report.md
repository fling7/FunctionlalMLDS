# Deterministic Repair Policy Report

- Status: valid
- Rules: 7
- Deterministic rules: 6
- LLM escalation rules: 1
- Repair log entries: 12
- LLM first-generation attempts: 8
- LLM repair attempts: 0
- Deterministic repair evidence: 4

## Rules

| Priority | Rule ID | Repair type | LLM allowed | Name |
|---:|---|---|---:|---|
| 1 | DR-001 | deterministic_normalization | False | Normalize identifiers |
| 2 | DR-002 | deterministic_manifest_rebuild | False | Recompute manifest hashes |
| 3 | DR-003 | deterministic_value_mapping | False | Normalize TTS model aliases |
| 4 | DR-004 | deterministic_geometry_recompute | False | Regenerate agent placements |
| 5 | DR-005 | deterministic_recovery | False | Recover existing valid artefacts without rerun |
| 6 | DR-006 | deterministic_regeneration | False | Regenerate deterministic derived artefacts |
| 99 | LR-001 | llm_repair | True | Escalate semantic repairs to LLM |
