# FunctionalMLDS Generalizability Assessment

## Ergebnis

- Status: valid
- Checks: 5/5
- Score: 1.0
- Cases: 3
- Domaenen: 3

## Checks

| Check | Result | Evidence |
|---|---:|---|
| multi_domain_corpus | True | 3 cases, 3 domains |
| same_pipeline_stages | True | same stages=True |
| no_failed_cases | True | success=3, failure=0 |
| domain_terms_externalized | True | 25 Python files scanned, 0 findings |
| runtime_behavior_cross_domain | True | handoff=1.0, grounding=1.0, chat=66/66 |

## Interpretation

Die Pipeline kann als domaenenuebergreifend anwendbar bewertet werden, wenn dieselben Stufen fuer alle Cases erfolgreich laufen, die Domaenenbegriffe ausserhalb des Python-Codes liegen und die Runtime-Checks ueber alle Domaenen hinweg erfolgreich bleiben.
