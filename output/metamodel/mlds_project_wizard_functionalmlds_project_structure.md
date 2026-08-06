# FunctionalMLDS Wizard Project Structure

## Zweck

Der MLDS Project Wizard erzeugt im FunctionalMLDS-Modus zwei klar getrennte Artefaktbereiche:

1. Einen Forschungs- und Validierungsbereich unter `output/wizard_functionalmlds/<case_id>/`.
2. Ein kleines Interactive-Agents-Runtime-Projekt unter `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/<case_id>/`.

Diese Trennung ist verbindlich. Die Runtime muss nur die Dateien enthalten, die Unity und das Python-Backend zum Laden, Fragenbeantworten, Agentenwissen und Handoff brauchen. Vollstaendige FunctionalMLDS-Instanzen, Validierungsberichte, Zwischenartefakte und Stage-Manifeste bleiben im Output-Bereich, damit sie fuer Paper, Debugging und Reproduzierbarkeit erhalten bleiben, ohne das Unity-Projekt aufzublaehen.

## Case-ID

`<case_id>` ist der gemeinsame Primaerschluessel zwischen Output-Bereich und Runtime-Projekt. Er muss vom Backend mit `require_safe_case_id` validiert werden und darf keine Pfadnavigation enthalten. Alle Artefakte einer Wizard-Erzeugung muessen denselben `case_id` verwenden.

## Output-Bereich

Root:

```text
output/wizard_functionalmlds/<case_id>/
```

Verbindliche Struktur:

```text
input/
  source_mlds.json
  source_mlds.sha256
intermediate/
  scene_graph.normalized.json
  object_group_summary.json
  scene_semantics.json
  agent_roles.generated.json
  handoff_matrix.json
  knowledge.generated.json
  agent_placements.json
functionalmlds/
  functionalmlds.instance.generated.json
validation/
  mlds_ingestion_validation.json
  functionalmlds_invariant_validation.json
  handoff_derivation_validation.json
  functionalmlds_invariants_validation.json
  project_materialization_validation.json
  schema_validation.json
  traceability_metrics.json
  handoff_metrics.json
  stage_completion_report.json
interactive_agents_project/
  kb/
stage_manifest.json
```

Pflicht in der Analyze-Phase:

- `input/source_mlds.json`
- `intermediate/scene_graph.normalized.json`
- `intermediate/object_group_summary.json`
- `intermediate/scene_semantics.json`
- `intermediate/agent_roles.generated.json`
- `intermediate/handoff_matrix.json`
- `intermediate/knowledge.generated.json`
- `intermediate/agent_placements.json`
- `functionalmlds/functionalmlds.instance.generated.json`
- `validation/functionalmlds_invariant_validation.json`
- `validation/handoff_derivation_validation.json`
- `stage_manifest.json`

Pflicht in der Commit-Phase:

- alle Analyze-Artefakte
- `validation/functionalmlds_invariants_validation.json`
- `validation/project_materialization_validation.json`
- `validation/schema_validation.json`
- `validation/traceability_metrics.json`
- `validation/handoff_metrics.json`
- `validation/stage_completion_report.json`
- ein materialisiertes Backend-Projekt unter `InteractiveAgents/projects/<case_id>/`

## Runtime-Projekt

Root:

```text
InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/<case_id>/
```

Verbindliche Struktur:

```text
project.json
room_plan.json
agents.json
trace_map.json
kb/
  <knowledge_tag>/
    <entry>.txt
```

Diese Dateien sind bewusst kompakt:

- `project.json` enthaelt Projektmetadaten und Referenzen auf FunctionalMLDS-Artefakte im Output-Bereich.
- `room_plan.json` ist die vom Wizard analysierte MLDS-Raumdatei bzw. deren normalisierte Runtime-Kopie.
- `agents.json` enthaelt die agentenspezifischen Runtime-Daten: Persona, Stimme, Expertise, Knowledge Tags, Handoff-Ziele, Positionen und FunctionalMLDS-Agentenreferenzen.
- `trace_map.json` verbindet Runtime-Aktionen, Agenten, Use Cases, Szenarioschritte, Capabilities und Validation Cases mit der FunctionalMLDS-Instanz.
- `kb/` enthaelt nur die fuer den Chat zur Laufzeit benoetigten Wissensdateien.

Nicht in das Runtime-Projekt gehoeren:

- vollstaendige Stage-Manifeste
- Validierungsberichte
- Metrikberichte
- Zwischenmodelle
- grosse Paper-/Case-Study-Artefakte

## Referenzrichtung

Die Runtime verweist auf den Output-Bereich, nicht umgekehrt. `project.json` und `trace_map.json` duerfen FunctionalMLDS-Pfade enthalten, damit Runtime-Logging und Validierung Ereignisse auf das Metamodell zurueckfuehren koennen. Die Runtime darf aber nicht darauf angewiesen sein, alle Forschungsartefakte vollstaendig in den Speicher zu laden.

Minimal erforderliche Referenzen:

- `project.json.functionalmlds_trace_path` zeigt auf `output/wizard_functionalmlds/<case_id>/functionalmlds/functionalmlds.instance.generated.json`.
- `project.json.generation_mode` ist im FunctionalMLDS-Modus exakt `functionalmlds`.
- `project.json.functionalmlds_case_dir` zeigt auf `output/wizard_functionalmlds/<case_id>/`.
- `project.json.source_mlds_path` zeigt auf `output/wizard_functionalmlds/<case_id>/input/source_mlds.json`.
- `project.json.metamodelVersion` entspricht `functionalmlds.instance.generated.json.metamodelVersion`.
- `trace_map.json.functionalmlds_path` zeigt auf dieselbe FunctionalMLDS-Instanz.
- `trace_map.json.project_files` zeigt auf `project.json`, `room_plan.json`, `agents.json` und `kb/`.

## Validierungsregel

Ein FunctionalMLDS-Projekt gilt erst dann als commit-faehig, wenn mindestens diese Checks erfolgreich sind:

- FunctionalMLDS-Invarianten bestehen.
- Projektmaterialisierung erzeugt alle Runtime-Dateien.
- Runtime-Projekt besteht die Schema-Validierung.
- Traceability-Metriken und Handoff-Metriken wurden erzeugt.
- Stage-Completion-Report bestaetigt die erwarteten Artefakte.

Wenn ein Chat-Refinement vorgemerkt wurde, ist der Draft `validation_stale=true`. In diesem Zustand darf kein Runtime-Projekt als final gelten, bevor Analyze- und Commit-Stages erneut durchlaufen wurden.

## Kompaktheitsentscheidung

Die Zielstruktur ist kompakt genug fuer Unity, weil nur `project.json`, `room_plan.json`, `agents.json`, `trace_map.json` und `kb/` im Runtime-Projekt landen. Die wissenschaftlich relevanten Nachweise bleiben reproduzierbar im Output-Bereich. Dadurch kann derselbe Wizard sowohl praktisch nutzbare Interactive-Agents-Projekte erzeugen als auch zeigen, dass diese Projekte aus einem validierten FunctionalMLDS-Modell abgeleitet wurden.
