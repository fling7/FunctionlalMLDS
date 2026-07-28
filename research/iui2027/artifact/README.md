# Anonymous ACM IUI 2027 artifact

This directory is the entry point for reproducing the paper's structural
system evidence. The default verification is deterministic, fail-closed and
API-free: it does not contact an LLM, the paper-review service, or any other
network service. It also does not start Unity unless an editor executable is
provided explicitly.

## Canonical demonstrator

`steinpilz_brand_room` is the canonical demonstrator. It is the richest of the
three authored fixtures: the room contains several semantic zones, object
groups and individual assets as well as multiple agents whose responsibilities
and handoff relations can be inspected. That makes one compact walkthrough
sufficient to show:

1. stable identity from a spatial scene description to FunctionalMLDS V2;
2. `Asset > Group > Zone` responsibility resolution;
3. routing from a selected object and current agent to a modeled provider;
4. runtime evidence that binds the selected entity, model hash, provider and
   action.

The demonstrator is an explanatory example, not a user study and not evidence
that the system generalizes to arbitrary rooms. The two other fixtures
(`classroom_dinosaur` and `bestfit_career_fair`) remain part of the structural
benchmark so that the reported denominators do not depend on one room.

## One-command verification

Run from the repository root with Python 3.11 or newer:

```text
python -m pip install -r research/iui2027/artifact/requirements.txt
python research/iui2027/artifact/verify.py
```

The command checks:

- all expected case inputs and their source hash manifests;
- deterministic in-memory regeneration and canonical validation of V2;
- the committed IUI benchmark, including every recorded input/source hash;
- the temporary materialization-to-backend contract;
- targeted benchmark, artifact and spatial-chat regression tests;
- the Unity version, relevant packages, binding/evidence classes and smoke
  entry points;
- the strict paper checker when a built review PDF is present;
- the documented review bundle for email addresses, local user paths, private
  keys and high-confidence embedded secrets.

It atomically writes `verification-summary.json`. The summary contains only
repository-relative identifiers and hashes; it never records a local absolute
path, reviewer email, review token, API key, or subprocess log.

The verifier is intentionally stricter than the benchmark's methodological
comparison. The benchmark can regenerate its V2 treatment in memory and audit
old checked-in V2 instances without using them. The release verifier fails if
such checked-in V2 instances are rejected, because a review artifact should
not ship a known-stale representation.

To rerun the structural benchmark in a temporary directory instead of only
checking its committed evidence and hashes:

```text
python research/iui2027/artifact/verify.py --benchmark-mode run
```

## Optional real Unity smokes

Supplying an editor executable starts three sequential Unity batch-mode smokes:
the native V2 scenario/assertion/evidence smoke, the QuickAgent bridge smoke,
and the spatial grounding/serialization smoke.

```text
python research/iui2027/artifact/verify.py --unity-editor /path/to/Unity
```

The Unity logs and runtime-validation output are created in a temporary
directory and removed afterwards. The committed summary records only the
execute-method name, exit status and presence of the expected `OK` marker.
Because Unity editor licensing is machine-specific, static verification
remains the default and a skipped Unity run is reported explicitly rather than
presented as a successful runtime execution.

## Interpretation boundary

A passing artifact establishes that the checked files agree, that fresh model
generation and validators execute, and that the tested structural contracts
hold for the three fixtures. It does not measure generated-answer correctness,
human usefulness, usability, trust, end-to-end network latency, or
population-level effects. See [DATA_DICTIONARY.md](DATA_DICTIONARY.md) for the
reported fields, [ANONYMITY.md](ANONYMITY.md) for review-bundle hygiene, and
[LICENSE_STATUS.md](LICENSE_STATUS.md) before redistributing any file.

