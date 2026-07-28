# IUI 2027 scientific paper task list

Last updated: 2026-07-29

The paper source is in `paper/`. A checked item is present in the current
anonymous manuscript and backed by the cited artifact. PCS actions remain
author actions because they require account access and final author metadata.

## A — Venue-compliant scaffold

- [x] Verify the official 2027 call, dates, scope, and evidence policy.
- [x] Use the latest installed `acmart` review format:
      `\documentclass[manuscript,review,anonymous]{acmart}`.
- [x] Add relevant ACM CCS concepts and keywords.
- [x] Keep the main-text estimate below the recommended 8,000 words.
- [x] Add strict checks for format, pending values, citations, anonymity,
      metadata, log errors, size, and tagging.
- [x] Document the optional supplement and concurrent-submission rule.

## B — Claim and narrative freeze

- [x] Frame the contribution around the Unity interaction and authoring
      implementation, with the model as its interaction-assurance contract.
- [x] Freeze the working title and complete a measured abstract.
- [x] Map all three research questions to method, result, and limitation.
- [x] Remove unsupported claims about user experience, semantic answer quality,
      WebXR evaluation, broad generality, and representation superiority.
- [x] Keep every abstract/result/conclusion claim in the evidence matrix.

## C — Related work and novelty

- [x] Cover human–AI interaction and intelligible control.
- [x] Cover embodied/situated agents and spatial reference.
- [x] Cover conversational authoring and agents in XR.
- [x] Cover model-based interface engineering and traceability.
- [x] Position the contribution as an explicit lifecycle connection, not as
      the first Unity, XR, LLM-agent, embodied-agent, or model-based UI system.
- [x] Verify bibliography identifiers against primary publisher, DOI, or arXiv
      records.

## D — Manuscript sections

- [x] Abstract: problem, approach, corpus, principal measured results, boundary.
- [x] Introduction: user interaction, gap, RQs, and four contributions.
- [x] Related Work: synthesis and precise novelty boundary.
- [x] System: interaction goals, model contract, placement workbench, Unity,
      backend, runtime evidence, and AI roles.
- [x] Method: cases, adapters, immutable inputs, routing probes, mutations,
      timing, runtime tests, placement transactions, and analysis boundary.
- [x] Results: exact answers to RQ1–RQ3 with generated denominators.
- [x] Discussion: author/visitor implications, visible failure, mixed tradeoff,
      privacy, bias, and control.
- [x] Limitations: corpus, shared sources/validators, synthetic mutations,
      absent human/semantic/WebXR evidence, client trust, and timing scope.
- [x] Conclusion: concise, measured, and non-causal.
- [x] GenAI account: all research-affecting model calls, sampling, repair,
      frozen outputs, coding assistance, and editorial reviewer role.
- [x] Human-subject boundary: no participants or personal data in the reported
      software-system evaluation.

## E — Visual and quantitative material

- [x] Add an accessible model-to-runtime contract diagram.
- [x] Add an accessible placement/visitor workflow diagram.
- [x] Add an accessible compact authoring/runtime architecture diagram.
- [x] Add per-case chain and routing tables.
- [x] Add fault/edit and timing tables with explicit denominators.
- [x] Describe representative invalid requests, trace failures, and rollback
      behavior in the RQ3 text.
- [x] Use labels and line styles that do not depend on color.
- [x] Give every table and figure a detailed `\Description` or tagged alt text.

## F — Reproducible and accessible PDF

- [x] Pin the LaTeX tagging stack to
      `latex-lab-2025-11-01a` /
      `c5afb829ef326a0469435da85636c973cc258b3f`.
- [x] Build with LuaLaTeX and `\DocumentMetadata{pdfstandard=UA-2}`.
- [x] Add an optional hard veraPDF PDF/UA-2 gate.
- [x] Complete the final four-pass build after the last source edit.
- [x] Pass veraPDF PDF/UA-2 and the strict local submission checker.
- [x] Render and visually inspect every final PDF page.
- [x] Complete a final number/citation/cross-reference/anonymity audit.

## G — Review loop

- [x] Complete an independent internal IUI-style review and address every
      critical or major point.
- [x] Upload the anonymous PDF to paperreview.ai as `ACM IUI 2027` using the
      authorized email.
- [x] Store the access token and raw reviews only in ignored private paths.
- [x] Convert every substantial comment into a redacted task and resolution.
- [ ] Rebuild and resubmit until the textual assessment is positive and no
      critical or major issue remains.
- [ ] Record the passing review timestamp and paper commit without the email,
      token, or private raw response.

## H — Author actions before PCS deadlines

- [ ] Confirm final author order, affiliations, corresponding author, and
      concurrent-submission disclosure.
- [ ] Register the abstract in PCS by 2026-08-13 AoE.
- [ ] Submit the full paper by 2026-08-20 AoE.
- [ ] Decide which review-only files may receive a redistribution license and
      whether to attach an anonymous supplement/video.
