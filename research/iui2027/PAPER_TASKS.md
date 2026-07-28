# IUI 2027 scientific paper task list

The paper source lives in `paper/`. Tasks are completed in order unless a later
task can be advanced without inventing unavailable results.

## A — Submission scaffold

- [x] **A1** Obtain the latest official `acmart` template and record its version.
- [x] **A2** Create the anonymous one-column review manuscript using
      `\documentclass[manuscript,review,anonymous]{acmart}`.
- [x] **A3** Add ACM CCS concepts and author keywords relevant to IUI.
- [x] **A4** Establish a reproducible local PDF build.
- [x] **A5** Add word-count, anonymity, broken-reference, and PDF-metadata checks.

## B — Evidence-first outline

- [x] **B1** Create a claim-to-evidence matrix.
- [ ] **B2** Freeze the title and abstract before abstract registration.
- [ ] **B3** Map each research question to method, metric, result, and limitation.
- [ ] **B4** Remove claims that cannot be supported by the submission deadline.

## C — Related work

- [x] **C1** Review primary literature on intelligent and multimodal interfaces.
- [x] **C2** Review embodied and situated conversational agents.
- [x] **C3** Review spatial reference resolution and scene grounding.
- [x] **C4** Review model-based UI and interactive-system authoring.
- [x] **C5** Review agent orchestration, tracing, and human control.
- [x] **C6** Verify every BibTeX record against a publisher or DOI source.
- [x] **C7** State the precise gap without claiming that no prior system exists.

## D — Manuscript sections

- [ ] **D1 Abstract:** problem, gap, approach, evaluation, measured results, boundary.
- [x] **D2 Introduction:** motivating user interaction, challenge, contributions.
- [x] **D3 Related Work:** synthesis and gap, not a catalogue.
- [ ] **D4 System:** interaction model, generation, Unity/WebXR, agents, traces.
- [ ] **D5 Method:** cases, tasks, baselines, mutations, metrics, statistics.
- [ ] **D6 Results:** answer each RQ using generated evidence only.
- [x] **D7 Discussion:** human-centric implications, control, failure recovery,
      practical use, societal impact.
- [ ] **D8 Limitations and threats:** no hidden limitations or overgeneralization.
- [ ] **D9 Conclusion:** concise contribution and bounded findings.
- [ ] **D10 AI methods:** describe every LLM role, prompt, model, and judge affecting results.
- [x] **D11 Ethics statement:** accurately state that the present software-only
      evaluation contains no human participants or personal data.

## E — Visual material

- [ ] **E1** Interaction walkthrough figure from user reference to validated response.
- [ ] **E2** Architecture/model-to-runtime figure.
- [ ] **E3** Experimental design figure or compact condition table.
- [ ] **E4** Per-RQ results tables with denominators and uncertainty.
- [ ] **E5** Failure taxonomy with representative examples.
- [ ] **E6** Accessible descriptions, legible labels, and non-color-only encoding.

## F — Quality and compliance

- [x] **F1** Keep main text at or below 8,000 words.
- [x] **F2** Use direct, human-readable prose and define unavoidable terminology.
- [ ] **F3** Audit citations, quotations, numbers, cross-references, and captions.
- [ ] **F4** Audit anonymity in source, PDF, metadata, figures, links, and supplements.
- [ ] **F5** Run accessibility checks and inspect every rendered PDF page.
- [ ] **F6** Add practical/societal impact, privacy, bias, control, and failure discussion.
- [ ] **F7** Ensure concurrent-submission disclosure is accurate.

## G — Review loop and submission

- [ ] **G1** Run an internal claims/evidence review.
- [ ] **G2** Build the ≤10 MB, ≤15-page anonymous PDF used by the Stanford reviewer.
- [ ] **G3** Submit to `Other / ACM IUI 2027` using the authorized email address.
- [ ] **G4** Track every major comment and its resolution.
- [ ] **G5** Repeat build and review until the master exit criteria pass.
- [ ] **G6** Register the abstract in PCS by 2026-08-13 AoE.
- [ ] **G7** Submit the final manuscript by 2026-08-20 AoE.
