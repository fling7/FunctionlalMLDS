# Reframed ACM IUI 2027 paper

This directory contains a **new, parallel paper version**. The prior manuscript
in `research/iui2027/paper/` is intentionally unchanged.

## Working title

**Preventing Wrong-Target Agent Actions in Spatial Interfaces with Executable
Interaction Contracts**

The title and opening now lead with the user-visible failure mode rather than
the metamodel. FunctionalMLDS is presented as the concrete realization of the
contract, not as the sole subject of the paper.

## Main changes

1. **IUI-centered problem statement.** The central problem is a fluent answer
   produced for the wrong spatial target, provider, or backend action.
2. **New research questions.**
   - coverage and migration non-regression;
   - fail-closed runtime enforcement;
   - added cross-layer assurance and cost.
3. **Placement removed from the core claim.** The placement workbench remains
   in the repository and old paper, but no longer competes with the interaction
   contract for the paper's main story.
4. **V2-only invariants moved into the main result.** The strict
   agent–provider contract's 9/9 detection/localization result is now the
   positive expressiveness evidence, while direct-wiring parity is described
   honestly as non-regression.
5. **Shared-resolver limitation made explicit.** The adapter comparison is not
   presented as an independent routing oracle or architectural superiority.
6. **Current benchmark values used.** The timing table follows
   `research/iui2027/evaluation/tables.md` on the branch baseline
   (`5.89–7.61x` V2/direct median ratio). This differs from the older PDF
   snapshot and should be regenerated once more immediately before submission.
7. **Interaction contract figure.** The main diagram follows the actual
   admission order: Unity selection, identity gate, responsibility gate,
   operation gate, response model, response/evidence gate, commit or rollback.
8. **Human claims remain bounded.** The text explains user-facing consequences
   but does not claim improved trust, usability, workload, preference, or
   dialogue quality.

## Build

From this directory:

```bash
latexmk -pdf main.tex
```

The manuscript intentionally reuses the existing bibliography and Unity image:

- `../paper/references.bib`
- `../paper/figures/unity-model-grounded-selection.png`

This avoids duplicating or modifying the original paper assets.

## Compiled review PDF

The branch build publishes the current review manuscript as
`iui2027-reframed.pdf` in this directory. The PDF is generated from `main.tex`
and the checked-in section, bibliography, and figure sources; the prior paper
PDF remains unchanged.

## Evidence sources

Claims in the draft are constrained to the checked-in evidence:

- `research/iui2027/CLAIM_EVIDENCE_MATRIX.md`
- `research/iui2027/evaluation/results.json`
- `research/iui2027/evaluation/tables.md`
- `research/iui2027/artifact/verification-summary.json`
- `InteractivAgents/.../tests/test_spatial_chat_contract.py`
- `InteractivAgents/.../unity_scripts/FunctionalMldsV2/`
- `tools/dynamic_functional_mlds_v2_model.py`
- `tools/validate_dynamic_functional_mlds_v2.py`

No new empirical result has been invented for this rewrite.

## Submission-critical open evidence

The most valuable additional evaluation is an independently authored fourth
scene with natural group- and zone-level ownership, an unassigned asset, and a
genuine ambiguity, evaluated after freezing the resolver. The second priority
is an independent route oracle or separately implemented resolver. A controlled
developer diagnosis study would be valuable, but only with ethics clearance,
adequate participants, and a fair task design; a rushed convenience study is
not recommended.

See `EVALUATION_BACKLOG.md` for an executable plan.
