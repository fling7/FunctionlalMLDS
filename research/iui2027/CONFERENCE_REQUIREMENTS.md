# ACM IUI 2027 requirements

Source of truth: <https://iui.acm.org/2027/call-for-papers/>

Verified on 2026-07-28. Conference-specific instructions override general ACM
guidance if the two differ.

## Dates

All deadlines are end of day Anywhere on Earth.

| Milestone | Date |
| --- | --- |
| Abstract registration | 2026-08-13 |
| Full paper | 2026-08-20 |
| Initial notification | 2026-10-29 |
| Invited rebuttal | 2026-11-05 |
| Final decision | 2026-11-23 |
| Camera-ready | 2026-12-03 |
| Conference, Helsinki | 2027-02-08 to 2027-02-11 |

The abstract date is treated as mandatory. The public call does not state which
metadata become immutable at abstract registration.

## Review manuscript

- Latest ACM Master Article Template.
- LaTeX class:

  ```latex
  \documentclass[manuscript,review,anonymous]{acmart}
  ```

- Single-column review layout through the ACM TAPS workflow.
- Variable paper length, proportional to the contribution.
- Target at most 8,000 words.
- A manuscript above 10,000 words requires an explicit length justification.
- References, figure/table captions, GenAI disclosure, and appendices are excluded
  from that word count.
- Submission in PCS under `SIGCHI / IUI 2027 / IUI 2027 Papers`.

## Scope and evidence

An IUI paper must address a practical HCI problem with machine intelligence and
must discuss both computational and human-centric aspects. Evidence must be
appropriate to the claims; the call lists user studies, system evaluations, and
computational analyses as examples. A user study is not formally mandatory.

Directly relevant topics are:

- intelligent AR/VR interfaces;
- embodied agents;
- intelligent multimodal interfaces and assistants;
- knowledge-based interface design and generation;
- end-user interaction with LLMs and agents;
- human-agent interaction and multi-agent systems;
- user control and steering of agents;
- human-in-the-loop testing and debugging;
- reproducibility and mixed-methods evaluation.

## Double-blind rules

- No author names or affiliations in the PDF.
- No identifying names, logos, faces, credits, metadata, or URLs in supplements.
- Remove or anonymize acknowledgements.
- Cite related work, including the authors' work, normally and in the third person.
- Do not write “our previous work” or otherwise reveal ownership.
- Anonymize repository links and video content.

Violations can lead to desk rejection.

## Human participants

If people participate in the research, the applicable institutional ethics
process must be completed before data collection. The submission must include
an anonymized note explaining the relevant approval or exemption context. No
human-subject results may be invented, backfilled, or collected without that
determination.

## Generative AI

IUI 2027 does not require disclosure when AI only assists with wording. AI used
in the research itself must be described in detail in the methods. This paper
therefore has to document LLM-based generation, agent responses, prompts,
repair, evaluation, and any AI-based judge that affects reported results.

The Stanford Agentic Reviewer is used only as editorial feedback and is not a
scientific evaluator in the paper.

## Supplements and publication

- Supplements are optional but encouraged and must be anonymous.
- Suggested supplements include data sheets, questionnaires, and application videos.
- Videos must be captioned and follow the SIGCHI technical guidance.
- Closely related concurrent submissions based on the same artifact, study, or
  data must be disclosed in anonymized form in PCS.
- Accepted papers appear in the ACM Digital Library and require an in-person
  presentation by a registered author.
- ACM publications are Open Access. APC eligibility must be checked against the
  corresponding author's institution; the 2026 temporary prices are not assumed
  to apply to a conference held in 2027.

## Submission gates

- [ ] Abstract registered by 2026-08-13 AoE.
- [ ] Main text at or below 8,000 words, unless a justified exception is necessary.
- [ ] Correct `acmart` options and one-column review PDF.
- [ ] Complete double-blind audit, including PDF metadata and supplements.
- [ ] Claims-to-evidence table has no unsupported claim.
- [ ] Human-subject note is accurate, or the paper clearly states that no human
      participants were involved.
- [ ] Machine intelligence used in the research is reproducibly documented.
- [ ] Practical and societal impact, limitations, privacy, bias, and user control
      are discussed.
- [ ] Accessibility check passes; all figures have descriptions and videos have captions.
