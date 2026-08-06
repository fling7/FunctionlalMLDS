# Anonymous-review hygiene

The review bundle is designed to disclose implementation and evidence without
disclosing reviewer-service credentials, workstation identity, or author
identity.

## Included scan scope

`verify.py` scans the text files intended to support anonymous review:

- this artifact directory;
- paper sources and structural evaluation artifacts;
- each case's `input`, `functionalmlds`, and `intermediate` data;
- the Unity manifest/version record and the binding, evidence, and smoke
  sources named by the verifier.

The scanner fails on email addresses, Windows or POSIX user-home paths, private
key headers, common high-confidence API-token formats, and quoted secret
assignments. Its findings contain repository-relative paths only.

## Excluded private and machine-local material

Do not place the following in an anonymous review archive:

- Git metadata or branch/remotes;
- reviewer-service tokens, raw reviews, upload receipts, or contact addresses;
- environment files, shell history, IDE settings, Unity license material, or
  package caches;
- generated logs under runtime, test, temporary, or paper-build directories;
- screenshots with desktop chrome, account names, or local paths;
- acknowledgements, deanonymizing project URLs, author lists, or affiliations.

The committed `.gitignore` keeps reviewer tokens/private responses, paper build
products, and temporary PDF renders out of version control. That is a useful
guard, but it is not a substitute for running the verifier immediately before
packaging the review artifact.

## Deliberate non-claims

Fixture identifiers, scene objects, synthetic agent roles, and cited authors
are research content, not the submission's author identity. The scan is a
high-confidence hygiene check, not a legal determination that arbitrary prose
contains no identifying inference. A human should still inspect the final PDF,
supplementary files, archive file list, and PDF metadata before upload.

