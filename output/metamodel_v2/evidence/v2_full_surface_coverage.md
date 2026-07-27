# Dynamic Functional MLDS V2 – executable validation evidence

Generated: 2026-07-14T11:14:42.264861+00:00
Overall result: **PASS**

| Subject | Result | Errors | Warnings | Checks |
| --- | --- | ---: | ---: | ---: |
| Dynamic Functional MLDS V2 | PASS | 0 | 0 | 18 |
| DFMLDS-V2-positive-full-surface | PASS | 0 | 0 | 18 |
| positive-full-surface | PASS | 0 | 0 | 13 |

## Dynamic Functional MLDS V2

All executable checks passed.

## DFMLDS-V2-positive-full-surface

All executable checks passed.

## positive-full-surface

All executable checks passed.

Full-surface coverage: **17/17**

| Requirement | Covered | Structural evidence |
| --- | --- | --- |
| `COV-USECASE-REL` | yes | ep, include, extend |
| `COV-SCENARIO-KINDS` | yes | alternative, exception, main |
| `COV-RELATION-KINDS` | yes | alternative, exception, fork, join, loop, sequence |
| `COV-SIGNAL` | yes | ent-signal |
| `COV-LOCATORS` | yes | endpoint, tool, topic |
| `COV-PARAMETER-SCHEMA` | yes | parameter-binding, schema-in, schema-out, cap-param, runtime-param |
| `COV-ABSTRACT-VV` | yes | vc-abstract, procedure-abstract |
| `COV-SATISFY-BRANCHES` | yes | satisfy-requirement, satisfy-usecase |
| `COV-STATE-EVIDENCE` | yes | state |
| `COV-ASSERTION-KINDS` | yes | EventAssertion, GroundingAssertion, OutputAssertion, RelationAssertion, StateAssertion |
| `COV-ASSERTION-RESULT` | yes | assertion-result, actual |
| `COV-CAPABILITY-PERFORMER` | yes | cap-use |
| `COV-RUNTIME-TARGET` | yes | vt |
| `COV-BRANCH-PROBABILITY` | yes | r45-alt, r46-exc |
| `COV-ROOT-CONTAINERS` | yes | root |
| `COV-VV-ROLE-SEPARATION` | yes | rb |
| `COV-VERIFY-CASE` | yes | verify |
