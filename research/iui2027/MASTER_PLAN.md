# ACM IUI 2027 submission master plan

Last updated: 2026-07-29

Target: ACM IUI 2027 main paper  
Abstract registration: 2026-08-13 AoE  
Paper submission: 2026-08-20 AoE

This file is the authoritative progress overview. Detailed, checkable work is
kept in the linked subplans. A task is complete only when its stated evidence
exists in the repository or, for an external review, in the private reviewer
record.

## Exit criteria

The project is complete only when all of the following hold:

- [x] The prototype and evaluation tasks marked `MUST` are complete.
- [x] Every claim in the paper maps to generated evidence.
- [x] The anonymous PDF builds with the official ACM review class.
- [x] The PDF satisfies the IUI format, anonymity, accessibility, and word-count checks.
- [x] A fresh Stanford Agentic Reviewer run contains no major or critical weakness.
- [x] Its overall assessment is positive and recommends acceptance or describes
      the work as submission-ready.
- [x] All repository changes and non-secret review evidence are committed and pushed.
- [x] The five-minute heartbeat is paused only after the preceding criteria hold.

The Stanford service does not expose an IUI-calibrated accept/reject score.
Consequently, “accepted” is operationalized by the two reviewer criteria above;
an ICLR score will not be used as a misleading substitute.

## Phase 0 — safe checkpoint

- [x] Verify the pre-work tree is clean and synchronized with `origin/main`.
- [x] Create `codex/iui-2027-submission`.
- [x] Push the checkpoint branch.
- [x] Configure a five-minute thread heartbeat.
- [x] Exclude reviewer tokens and private responses from Git.

## Phase 1 — venue and contribution

- [x] Verify the official IUI 2027 dates and paper format.
- [x] Verify anonymity, evidence, human-subject, GenAI, supplement, and OA rules.
- [x] Define a conference-specific contribution and conservative claim boundary.
- [ ] Freeze the paper title, abstract metadata, and author list before 2026-08-13.

References:

- [Conference requirements](CONFERENCE_REQUIREMENTS.md)
- [Framing and research questions](FRAMING.md)
- [Claim-to-evidence matrix](CLAIM_EVIDENCE_MATRIX.md)

## Phase 2 — prototype and evaluation

- [x] Complete all `MUST` items in [PROTOTYPE_TASKS.md](PROTOTYPE_TASKS.md).
- [x] Run the clean, end-to-end evaluation from immutable inputs.
- [x] Generate tables, figures, raw result files, environment metadata, and hashes.
- [x] Audit every generated number against its raw evidence.

## Phase 3 — paper

- [x] Complete all manuscript, verification, and review-loop items (sections
      A–G) in [PAPER_TASKS.md](PAPER_TASKS.md).
- [x] Build the anonymous PDF and inspect every page.
- [x] Package anonymized supplementary material; a system video is deferred
      because it is not required for the present claim boundary.

The PCS/account actions in section H intentionally remain with the authors.

## Phase 4 — external review loop

- [x] Follow [REVIEW_PROTOCOL.md](REVIEW_PROTOCOL.md).
- [x] Submit only the anonymous PDF to the Stanford Agentic Reviewer.
- [x] Save the returned token only in an ignored local file.
- [x] Convert each substantial review comment into a tracked paper or prototype task.
- [x] Rebuild and resubmit only after the prior review has been fully addressed.
- [x] Stop only when the exit criteria are met.

## Phase 5 — release

- [x] Run all Python, backend, model, evaluation, Unity, and paper checks.
- [x] Ensure no token, email address, author identity, local path, or secret is in review artifacts.
- [x] Commit the final source, generated evidence, and submission PDF.
- [x] Push `codex/iui-2027-submission`.
- [x] Record the reviewed paper commit (`75c3189`) and reviewer service
      timestamp (`2026-07-28T23:25:40.557218`).
- [x] Pause the heartbeat.

## Completion record

The second fresh external review recommends acceptance after minor revisions
and reports no major, critical, or rejection-level issue. The reviewed
anonymous PDF is the snapshot from commit `75c3189`, with SHA-256
`ade3bcde931e59bc861e3b423cc72c8208c6557dee82eb547f0128415dd59066`.
Residual minor suggestions and the reason they do not change the bounded
claims are recorded in
[reviewer/REVIEW_ITERATIONS.md](reviewer/REVIEW_ITERATIONS.md).

This research-preparation plan is complete. Abstract registration, author
metadata, and the actual PCS submission remain human account actions due by
the dates above.
