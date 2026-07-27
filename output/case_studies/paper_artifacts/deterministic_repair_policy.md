# Deterministic Repair Policy

## Principle

The case-study pipeline prefers deterministic repair whenever an invalid artefact can be corrected without changing domain semantics. LLM repair is an escalation path, not the default.

## Rule Order

| Priority | Rule | Repair type | Typical issue | LLM allowed |
|---:|---|---|---|---:|
| 1 | Normalize identifiers | deterministic normalization | missing, duplicate or unstable IDs | false |
| 2 | Recompute manifest hashes | deterministic manifest rebuild | missing or stale `sha256` entries | false |
| 3 | Normalize TTS model aliases | deterministic value mapping | `tts_model=standard` | false |
| 4 | Regenerate agent placements | deterministic geometry recompute | out-of-bounds or obstacle-overlapping placement | false |
| 5 | Recover existing valid artefacts | deterministic recovery | valid artefact exists, stale manifest | false |
| 6 | Regenerate deterministic derived artefacts | deterministic regeneration | stale validation/report artefacts | false |
| 99 | Escalate semantic repairs to LLM | LLM repair | ambiguous semantics, roles, knowledge or capability coverage | true |

## Escalation Rule

Use an LLM repair prompt only when a validator requires semantic judgement that cannot be derived from existing IDs, schemas, geometry, manifests or runtime logs.

## Current Evidence

The current repair log contains:

- `8` successful LLM first-generation attempts.
- `0` LLM repair attempts after invalid generated artefacts.
- `1` deterministic recovery.
- `3` accepted traceability warnings.

This supports the intended policy: deterministic validation and recovery are used before any LLM repair escalation.
