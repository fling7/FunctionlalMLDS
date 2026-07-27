# FunctionalMLDS Analyze-Stage-Plan fuer den MLDS Project Wizard

Stand: 2026-07-09

## Entscheidung

Der FunctionalMLDS-Analyze-Modus fuehrt die Pipeline bis zu einer validierbaren FunctionalMLDS-Vorschau aus, schreibt aber noch kein finales Interactive-Agents-Projekt in den Backend-Projektordner.

Analyze-Stages:

1. `mlds_ingestion`
2. `scene_semantics`
3. `agent_roles`
4. `knowledge_synthesis`
5. `agent_placement`
6. `functionalmlds_assembly`
7. `functionalmlds_invariants`

Nicht im Analyze-Modus:

- `project_materialization`
- `schema_validation` gegen materialisierte Backend-Projektdateien
- `traceability_metrics`, soweit diese die finale Trace Map aus der Materialisierung erwarten
- Runtime-, Chat-, Handoff- und Answer-Grounding-Tests

## Begruendung

Der Wizard soll im Analyze-Schritt bereits zeigen koennen, dass die MLDS nicht nur in Legacy-Agenten umgewandelt wird, sondern in eine FunctionalMLDS-Struktur passt. Dafuer muessen Agenten, Wissen, Platzierungen, Handoff-Struktur und FunctionalMLDS-Instanz vorhanden sein.

Gleichzeitig darf Analyze noch keine finalen Projektdateien schreiben. Das finale Schreiben nach `InteractiveAgents/projects/<project_id>/` ist eine Commit-Entscheidung und muss dort mit vollstaendiger Validierung abgesichert werden.

## Erwartete Analyze-Artefakte

| Artefakt | Pfad im Case-Ordner | Zweck im Wizard |
| --- | --- | --- |
| Normalisierte Szene | `intermediate/scene_graph.normalized.json` | Raumobjekte, Zonen, Bounds |
| Objektgruppen | `intermediate/object_group_summary.json` | Raumwissen und Grounding-Vorschau |
| Szenensemantik | `intermediate/scene_semantics.json` | fachliche Zonen, Ziele, Interaktionsthemen |
| Agentenrollen | `intermediate/agent_roles.generated.json` | Agenten, Spezialwissen, Verantwortlichkeiten |
| Handoff-Matrix | `intermediate/handoff_matrix.json` | wer an wen weiterleiten darf |
| Wissen | `intermediate/knowledge.generated.json` | Knowledge-Tags und Inhalte |
| Platzierung | `intermediate/agent_placements.json` | Placement Preview |
| FunctionalMLDS-Instanz | `functionalmlds/functionalmlds.instance.generated.json` | metamodel-nahe Vorschau |
| Invariant-Validierung | `validation/functionalmlds_invariant_validation.json` | Nachweis, dass die Instanz in sich konsistent ist |

## Fehlerverhalten

Jede Stage muss einen Status liefern. Fuer den Wizard gilt:

- `success`: naechste Stage darf laufen.
- `needs_manual_review`: Analyze bricht kontrolliert ab und zeigt Validierungsfehler/Warnungen.
- `failed` oder `skipped`: Analyze bricht kontrolliert ab und zeigt die Ursache.

Der Wizard soll keine Commit-Aktion erlauben, wenn die Analyze-Stage `functionalmlds_assembly` oder die Invariant-Validierung nicht erfolgreich abgeschlossen wurde.

## Zeit- und Token-Einschaetzung

LLM-Aufrufe sind im Analyze-Modus fuer diese Stages zu erwarten:

- `scene_semantics`
- `agent_roles`
- `knowledge_synthesis`

Deterministische Stages:

- `mlds_ingestion`
- `agent_placement`
- `functionalmlds_assembly`
- `functionalmlds_invariants`

Damit ist Analyze fachlich aussagekraeftig, aber immer noch kleiner als ein vollstaendiger Case-Study-Lauf mit Materialisierung, Runtime-Setup und Chat-/Handoff-Tests.

## Adapter-Konstante

Der Stage-Plan ist im Backend-Adapter als `ANALYZE_STAGE_IDS` hinterlegt und ueber `FunctionalMldsAdapter.analyze_stage_plan()` abrufbar.
