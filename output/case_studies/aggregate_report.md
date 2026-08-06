# FunctionalMLDS Case Study Aggregate Report

## Overview

- Cases: 3
- Average trace coverage: 0.847
- Average handoff accuracy: 1.000
- Average object-group coverage: 1.000
- Average answer-grounding ratio: 1.000
- Stage-completion ratio: 1.000
- Chat tests: 66/66
- Handoff decision tests: 66

## Per-Case Metrics

| Case | Domain | Trace avg. | Runtime log cov. | Handoff acc. | Object-group cov. | Grounding | Completion |
|---|---|---:|---:|---:|---:|---:|---:|
| bestfit_career_fair | Career Fair / Recruiting Event | 0.847 | 0.250 | 1.000 | 1.000 | 1.000 | 1.000 |
| classroom_dinosaur | education | 0.847 | 0.250 | 1.000 | 1.000 | 1.000 | 1.000 |
| steinpilz_brand_room | Food Industry Trade Fair | 0.847 | 0.250 | 1.000 | 1.000 | 1.000 | 1.000 |

## Stage Errors And Repair Attempts

| Stage | Cases | Success | Errors | Warnings | Repair attempts |
|---|---:|---:|---:|---:|---:|
| agent_placement | 3 | 3 | 0 | 0 | 0 |
| agent_roles | 3 | 3 | 0 | 0 | 3 |
| answer_grounding | 3 | 3 | 0 | 0 | 0 |
| case_initialization | 3 | 3 | 0 | 0 | 0 |
| chat_tests | 3 | 3 | 0 | 0 | 0 |
| evaluation_questions | 3 | 3 | 0 | 0 | 0 |
| functionalmlds_assembly | 3 | 3 | 0 | 0 | 0 |
| functionalmlds_invariants | 3 | 3 | 0 | 0 | 0 |
| handoff_metrics | 3 | 3 | 0 | 0 | 0 |
| handoff_tests | 3 | 3 | 0 | 0 | 0 |
| knowledge_synthesis | 3 | 3 | 0 | 0 | 3 |
| mlds_ingestion | 3 | 3 | 0 | 0 | 0 |
| placement_metrics | 3 | 3 | 0 | 0 | 0 |
| project_materialization | 3 | 3 | 0 | 0 | 0 |
| runtime_setup | 3 | 3 | 0 | 0 | 0 |
| scene_semantics | 3 | 3 | 0 | 0 | 2 |
| schema_validation | 3 | 3 | 0 | 0 | 0 |
| stage_completion | 3 | 3 | 0 | 0 | 0 |
| traceability_metrics | 3 | 3 | 0 | 6 | 0 |

## Domain Metrics

| Domain | Handoff accuracy | Object-group coverage |
|---|---:|---:|
| Career Fair / Recruiting Event | 1.000 | 1.000 (12/12) |
| education | 1.000 | 1.000 (5/5) |
| Food Industry Trade Fair | 1.000 | 1.000 (9/9) |
