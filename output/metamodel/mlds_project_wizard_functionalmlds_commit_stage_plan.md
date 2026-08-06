# FunctionalMLDS Commit-Stage-Plan fuer den MLDS Project Wizard

Stand: 2026-07-09

## Entscheidung

Der FunctionalMLDS-Commit-Modus stellt sicher, dass alle Analyze-Artefakte vorhanden sind, materialisiert danach das Interactive-Agents-Projekt und fuehrt die finalen Validierungen aus. Erst danach darf der Wizard einen Commit als erfolgreich anzeigen.

Commit-Stages:

1. `mlds_ingestion`
2. `scene_semantics`
3. `agent_roles`
4. `knowledge_synthesis`
5. `agent_placement`
6. `functionalmlds_assembly`
7. `functionalmlds_invariants`
8. `project_materialization`
9. `schema_validation`
10. `traceability_metrics`
11. `handoff_metrics`
12. `stage_completion`

## Blockierende Validierungen

Diese Stages muessen fuer einen erfolgreichen FunctionalMLDS-Commit `success` liefern:

- `functionalmlds_invariants`
- `project_materialization`
- `schema_validation`

Wenn eine davon fehlschlaegt, darf der Wizard kein erfolgreich gespeichertes FunctionalMLDS-Projekt melden.

## Evidenz-Reports

Diese Reports muessen vorhanden sein und an die Wizard-UI zusammengefasst werden:

- `validation/functionalmlds_invariants_validation.json`
- `validation/project_materialization_validation.json`
- `validation/schema_validation.json`
- `validation/traceability_metrics.json`
- `validation/handoff_metrics.json`
- `validation/stage_completion_report.json`

Traceability- und Handoff-Metriken duerfen Warnungen enthalten, muessen aber erzeugt und auswertbar sein. Sie dienen als wissenschaftliche Evidenz dafuer, dass die erzeugten Projektdateien auf das Metamodell zurueckfuehrbar sind.

## Finale Artefakte

Der Commit muss mindestens diese Dateien erzeugen oder bestaetigen:

| Artefakt | Pfad |
| --- | --- |
| FunctionalMLDS-Instanz | `functionalmlds/functionalmlds.instance.generated.json` |
| Assembly-Invariant-Check | `validation/functionalmlds_invariant_validation.json` |
| Expliziter Invariant-Check | `validation/functionalmlds_invariants_validation.json` |
| Materialisierungsvalidierung | `validation/project_materialization_validation.json` |
| Schema-Validierung | `validation/schema_validation.json` |
| Traceability-Metriken | `validation/traceability_metrics.json` |
| Handoff-Metriken | `validation/handoff_metrics.json` |
| Stage-Completion-Report | `validation/stage_completion_report.json` |
| Backend-Projekt | `InteractiveAgents/projects/<case_id>/project.json` |
| Backend-Raumplan | `InteractiveAgents/projects/<case_id>/room_plan.json` |
| Backend-Agenten | `InteractiveAgents/projects/<case_id>/agents.json` |
| Backend-Trace-Map | `InteractiveAgents/projects/<case_id>/trace_map.json` |
| Backend-Knowledge-Base | `InteractiveAgents/projects/<case_id>/kb/...` |

## Unterschied zu Analyze

Analyze erzeugt eine FunctionalMLDS-Vorschau und prueft die Modellinvarianten. Commit erzeugt zusaetzlich die finalen Runtime-Dateien fuer Interactive Agents und validiert die gesamte Kette aus MLDS, FunctionalMLDS, Runtime-Bindings, Trace Map und Backend-Projekt.

## Adapter-Konstante

Der Commit-Plan ist im Backend-Adapter als `COMMIT_STAGE_IDS` hinterlegt und ueber `FunctionalMldsAdapter.commit_stage_plan(case_id=...)` abrufbar.
