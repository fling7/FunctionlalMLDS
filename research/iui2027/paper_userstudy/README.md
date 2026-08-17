# IUI 2027 user-study paper version

This directory contains the independent user-study manuscript derived from
`research/iui2027/paper_reframed/`. The existing `paper/` and
`paper_reframed/` directories remain unchanged.

## Evaluation structure

The manuscript combines two complementary studies:

- **Study T:** deterministic contract coverage, migration, runtime enforcement,
  mutation, Unity-smoke, and structural-cost evaluation.
- **Study U:** remote, unmoderated browser study of target, handoff, and
  responsibility intelligibility.

The current Study U results use the dated questionnaire export of
17 August 2026 with 65 completed sessions. Later responses must be analyzed as
a new dated cut rather than silently appended.

## Main files

- `main.tex`
- `sections/05_evaluation.tex`
- `sections/06_user_results.tex`
- `analysis/analyze_questionnaire.py`
- `iui2027-userstudy.pdf`

The manuscript reuses the existing bibliography and Unity figure from the
unchanged sibling directory `../paper/`.

## Reproducing the questionnaire summaries

```bash
python analysis/analyze_questionnaire.py path/to/questionnaire-export.json
```

The script deliberately restricts handoff-understanding and final-agent
summaries to sessions with `q5_handoff_observed == "yes"`.

## Build

```bash
latexmk -pdf main.tex
```

The branch workflow rebuilds and commits `iui2027-userstudy.pdf` whenever the
manuscript sources change.
