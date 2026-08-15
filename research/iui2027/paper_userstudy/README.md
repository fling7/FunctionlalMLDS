# IUI 2027 user-study paper version

This directory contains a new, independent manuscript version based on
`research/iui2027/paper_reframed/` from branch `paper/iui2027-reframed`.
The existing `paper/` and `paper_reframed/` directories remain unchanged.

## Purpose

This version introduces the user-study perspective in the Introduction while
retaining the reframed manuscript as its technical baseline. Study findings are
currently described qualitatively; participant counts and numerical outcomes
will be added after data collection and analysis are frozen.

## Main files

- `main.tex`
- `sections/01_introduction.tex`
- `iui2027-userstudy.pdf`

The manuscript reuses the existing bibliography and Unity figure from the
unchanged sibling directory `../paper/`.

## Build

```bash
latexmk -pdf main.tex
```

The branch workflow rebuilds and commits `iui2027-userstudy.pdf` whenever the
new manuscript sources change.
