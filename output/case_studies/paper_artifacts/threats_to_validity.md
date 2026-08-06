# Threats to Validity

## Scope

The current case study contains three MLDS domains, 66 executed chat tests, 66 handoff decision tests, a generalizability score of `1.0` and an average trace coverage of `0.847222`. These results support the feasibility of the FunctionalMLDS-mediated pipeline, but they do not remove all validity risks.

## Internal Validity

| ID | Threat | Impact | Mitigation | Residual risk |
|---|---|---|---|---|
| INT-01 | LLM-generated intermediate artefacts can vary between runs. | Different scene semantics, agent roles or knowledge entries may change downstream validation results. | Prompt versions, stage manifests, input/output hashes and bounded repair attempts are recorded. Deterministic validators are used after each LLM stage. | A full replication study should rerun the pipeline multiple times per case and report variance. |
| INT-02 | Repair loops may hide initial generation errors if only final artefacts are reported. | The final success rate may overstate one-shot generation reliability. | Repair attempts are aggregated in the stage manifest and paper tables report pre-final repair attempts separately from final errors. | The next repair-log task should add per-error JSONL records for exact before/after failure analysis. |
| INT-03 | The backend runtime state can influence chat and handoff tests. | Session history, cached project data or backend configuration could bias test outcomes. | Chat tests use isolated sessions per question and record runtime setup and response logs. | Unity-side interaction timing and visual navigation are not fully exercised by backend-only runtime tests. |

## External Validity

| ID | Threat | Impact | Mitigation | Residual risk |
|---|---|---|---|---|
| EXT-01 | The corpus currently contains three MLDS domains. | Results may not generalize to safety-critical automotive scenarios, industrial production cells or complex multi-room environments. | The pipeline accepts arbitrary MLDS inputs through CLI arguments and the generalizability check verifies absence of hard-coded domain terms in Python code. | Additional domains are required before claiming broad industrial generality. |
| EXT-02 | The Interactive Agents system is a prototype with Unity and Python backend components. | Findings may depend on prototype-specific project formats, endpoints or runtime assumptions. | The comparison separates deployable target artefacts from metamodel-added evidence and documents the exact backend endpoints and files. | A production AUTOSAR/EAST-ADL toolchain integration remains future work. |
| EXT-03 | The case study focuses on room-based agent interaction, not all possible FunctionalMLDS use cases. | Interaction-object scenarios, stateful object manipulation and non-dialogue behaviours may require additional extension models. | The metamodel keeps RuntimeBinding and Capability separate from Scenario, enabling extension without changing the core use-case structure. | A separate object-interaction case study should validate stateful devices such as a coffee machine. |

## Construct Validity

| ID | Threat | Impact | Mitigation | Residual risk |
|---|---|---|---|---|
| CON-01 | Trace coverage may not fully capture semantic correctness. | A trace link can exist even if the generated role or knowledge is semantically weak. | Traceability metrics are combined with runtime chat tests, handoff tests and deterministic answer-grounding checks. | Expert review of selected trace chains is still needed for qualitative semantic adequacy. |
| CON-02 | Answer grounding uses deterministic token overlap and no LLM judge in the current run. | Lexical overlap may miss paraphrases or falsely accept shallow mentions. | The grounding report explicitly records `llm_judge_used=false` and combines agent/context grounding with negative-marker checks. | For publication, a small expert-labelled sample should calibrate deterministic grounding thresholds. |
| CON-03 | RuntimeAction-to-log coverage is intentionally lower than other trace metrics. | Readers may misinterpret the 0.25 coverage as a failure of the metamodel rather than a boundary of observable runtime logging. | Reports state that only runtime-observable actions are expected to have backend log evidence. | The runtime logging schema should be extended if more pipeline actions need direct runtime observation. |

## Conclusion Validity

| ID | Threat | Impact | Mitigation | Residual risk |
|---|---|---|---|---|
| CONC-01 | The study has no completed Baseline A run over the same corpus yet. | Current comparison can support metamodel-added evidence, but direct superiority claims over the baseline remain limited. | The metric catalogue distinguishes direct comparison metrics from metamodel-added evidence metrics. | A future baseline execution is required for statistical or quantitative baseline-vs-treatment claims. |
| CONC-02 | The number of cases and tests is sufficient for a case study but not for statistical generalization. | Perfect scores such as 66/66 chat tests should be interpreted as case-study evidence, not population-level proof. | The paper should report exact corpus size, number of questions and domains alongside all averages. | Confidence intervals or repeated-run statistics require more cases and repeated runs. |

## Reporting Rule

The paper should avoid broad claims such as "FunctionalMLDS is generally correct for industrial toolchains." A defensible claim is narrower:

FunctionalMLDS made the MLDS-to-Interactive-Agents pipeline traceable, checkable and reproducible for the evaluated three-domain case-study corpus, while exposing clear remaining work for repeated runs, broader domains, baseline execution and expert semantic review.
