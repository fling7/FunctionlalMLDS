# Wissenschaftliche Einordnung: MLDS Project Wizard als FunctionalMLDS-Case-Study-Instrument

Stand: 2026-07-09

## Ziel Der Einordnung

Der umgebaute `MLDSI Project Wizard` ist nicht nur ein Editor-Werkzeug fuer Unity. Er dient als kontrollierter Einstiegspunkt fuer eine Case Study, in der dieselbe MLDS/MLDSI-Raumbeschreibung auf zwei Arten verarbeitet werden kann:

- Baseline: direkte Generierung eines Interactive-Agents-Projekts.
- Treatment: metamodel-vermittelte Generierung ueber FunctionalMLDS mit expliziter Validierung und Runtime-Evidenz.

Damit wird der wissenschaftliche Beitrag nicht als "bessere Dialogqualitaet" oder "schoenere Unity-Szene" formuliert, sondern als nachweisbare Zunahme an Traceability, Pruefbarkeit, Reparierbarkeit und Reproduzierbarkeit.

## Baseline A: Legacy Wizard

Der Legacy-Modus bildet den bisherigen Ablauf ab:

```text
MLDS/MLDSI -> Interactive-Agents-Projekt
```

Der Wizard sendet die MLDS/MLDSI-Datei an `POST /projects/arrow/analyze`. Das Backend erzeugt daraus einen Draft mit Projektbeschreibung, Agenten, Wissenseintraegen und Platzierungsvorschau. Beim Commit schreibt das Backend ein direkt nutzbares Projekt:

- `projects/<project_id>/project.json`
- `projects/<project_id>/room_plan.json`
- `projects/<project_id>/agents.json`
- `projects/<project_id>/kb/...`

Dieser Ablauf ist praktisch nuetzlich und bleibt als Vergleichsbasis erhalten. Wissenschaftlich ist er aber nur begrenzt inspizierbar, weil Use Cases, Szenarioschritte, Capabilities, RuntimeBindings, ValidationCases und Traceability-Beziehungen nicht als eigene Modellartefakte existieren.

Wichtig: Das ist kein Fehler des Legacy-Modus. Es definiert nur die Grenze der Baseline. Legacy erzeugt ein lauffaehiges Agentenprojekt, aber keine explizite FunctionalMLDS-Modellinstanz.

## Treatment B: FunctionalMLDS Wizard

Der FunctionalMLDS-Modus erweitert denselben Wizard-Ablauf:

```text
MLDS/MLDSI -> FunctionalMLDS -> validiertes Interactive-Agents-Projekt
```

Die Eingabe bleibt dieselbe MLDS/MLDSI-Datei. Das Backend fuehrt aber eine stufenweise Pipeline aus:

1. MLDS-Ingestion und Normalisierung.
2. Semantische Analyse der Szene.
3. Agentenrollen, Zustaendigkeiten und Handoff-Beziehungen.
4. Wissenssynthese fuer Agenten und Raumobjekte.
5. Platzierung der Agenten.
6. FunctionalMLDS-Instanzbildung.
7. Projektmaterialisierung in das Interactive-Agents-Format.
8. Schema-, Invarianten-, Traceability- und Handoff-Validierung.
9. Runtime-Setup, Chat- und Handoff-Pruefung.

Das Ziel ist nicht, das Runtime-Projekt zu ersetzen. FunctionalMLDS strukturiert den Generierungsprozess so, dass das Ergebnis als Modellinstanz, als materialisiertes Agentenprojekt und als Runtime-Verhalten geprueft werden kann.

## Was Die Metamodell-Abbildung Belegt

Die Metamodell-Abbildung ist belegt, wenn aus der MLDS/MLDSI-Datei eine FunctionalMLDS-Instanz entsteht und diese Instanz die relevanten Modellklassen mit gueltigen Beziehungen enthaelt.

Zentrale Evidenzartefakte:

| Evidenz | Datei oder Ort | Aussage |
| --- | --- | --- |
| FunctionalMLDS-Instanz | `output/wizard_functionalmlds/<case_id>/functionalmlds/functionalmlds.instance.generated.json` | Explizite Modellinstanz mit Requirements, UseCase, Scenario, ScenarioSteps, Actors, Entities, Agents, Capabilities, RuntimeBindings und ValidationCases. |
| Schema-Validierung | `output/wizard_functionalmlds/<case_id>/validation/schema_validation.json` | Die Instanz folgt dem erwarteten JSON-Schema. |
| Invarianten-Validierung | `output/wizard_functionalmlds/<case_id>/validation/functionalmlds_invariants_validation.json` | Kardinalitaeten, Referenzen und Kerninvarianten sind gueltig. |
| Stage Manifest | `output/wizard_functionalmlds/<case_id>/stage_manifest.json` | Jede Pipeline-Stufe ist mit Status, Inputs, Outputs und Reparatur-/Reuse-Informationen nachvollziehbar. |
| Traceability-Metriken | `output/wizard_functionalmlds/<case_id>/validation/traceability_metrics.json` | Abdeckung zwischen Modell, MLDS-Objektgruppen, RuntimeBindings und Validierungsfaellen wird messbar. |
| Handoff-Metriken | `output/wizard_functionalmlds/<case_id>/validation/handoff_metrics.json` | Agenten-Spezialwissen und Handoff-Ziele verweisen auf gueltige Runtime-Agenten und Entscheidungsfaelle. |

Fuer den vorhandenen Drei-Domaenen-Korpus zeigen die Paper-Artefakte:

- alle drei Cases besitzen eine FunctionalMLDS-Instanz,
- alle drei Cases haben `invariant_status = valid`,
- jedes Case besitzt 1 UseCase, 12 ScenarioSteps, 9 Capabilities, 9 RuntimeBindings und 6 ValidationCases,
- Requirement-to-validation coverage ist `1.0`,
- durchschnittliche Trace Coverage ist `0.847222`.

Diese Werte stehen in:

- `output/case_studies/paper_artifacts/tables/metamodel_coverage.md`
- `output/case_studies/paper_artifacts/comparison_metrics.md`

## Was Die Runtime-Funktion Belegt

Die Runtime-Funktion ist belegt, wenn die FunctionalMLDS-Instanz nicht nur als Datei existiert, sondern ein Interactive-Agents-Projekt erzeugt, das in Backend und Unity ausgefuehrt werden kann.

Zentrale Runtime-Evidenzartefakte:

| Evidenz | Datei oder Ort | Aussage |
| --- | --- | --- |
| Materialisiertes Projekt | `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/<case_id>/project.json` | Projekt ist im Backend-Projektstore sichtbar. |
| Raumplan | `.../projects/<case_id>/room_plan.json` | MLDS-/Raumwissen bleibt fuer Runtime-Setup verfuegbar. |
| Agenten | `.../projects/<case_id>/agents.json` | Agenten besitzen Rollen, Spezialwissen, Knowledge-Tags, Positionen und Forward-Vektoren. |
| Wissensbasis | `.../projects/<case_id>/kb/...` | Raum-, Objekt- und Fachwissen ist als projektlokale KB materialisiert. |
| Trace Map | `.../projects/<case_id>/trace_map.json` | Verknuepft Runtime-Aktionen mit FunctionalMLDS-Elementen. |
| Setup-Response | `output/wizard_functionalmlds/<case_id>/runtime_logs/setup_response.json` oder Case-Study-Runtime-Logs | Belegt, dass `/setup` eine Session und platzierte Agenten liefert. |
| Chat-/Handoff-Logs | `runtime_logs/*.jsonl` und Validierungsreports | Belegen, dass Agenten antworten und Handoffs beobachtbar sind. |

Fuer das aktuell gepruefte Wizard-Zielprojekt `classroom_dinosaur` wurde gezeigt:

- `POST /setup` liefert 4 Agenten mit Position und Forward-Vektor.
- Unity-Batchmode-Smoke spawnt dieselben 4 Agenten.
- Raumwissen kann aus der Projekt-KB beantwortet werden.
- Eine Dinosaurierfrage an den falschen Agenten fuehrt zu einem Handoff auf `exhibit_interpreter`.
- Die Handoff-Runtime ist ueber `trace_map.json` mit einer FunctionalMLDS RuntimeAction verbunden.

Damit ist die Runtime-Funktion nicht nur manuell plausibel, sondern durch Backend-Smoke, Unity-Smoke und Trace-Artefakte belegbar.

## Forschungsfragen, Die Der Wizard-Umbau Stuetzt

Der Wizard-Umbau stuetzt insbesondere drei Forschungsfragen:

### RQ1: Kann eine MLDS-zu-Agenten-Transformation explizit tracebar modelliert werden?

Ja, fuer die evaluierten Cases. Die FunctionalMLDS-Instanz und `trace_map.json` machen sichtbar, wie MLDS-Objekte, Agentenrollen, Capabilities, RuntimeBindings und ValidationCases zusammenhaengen. Die Metriken belegen eine durchschnittliche Trace Coverage von `0.847222` und Requirement-to-validation coverage von `1.0`.

### RQ2: Erhoeht FunctionalMLDS die Pruefbarkeit gegenueber direkter Artefaktgenerierung?

Ja, in Bezug auf metamodel-added evidence. Der Legacy-Wizard erzeugt nutzbare Projektdateien, aber keine pruefbaren UseCase-, Scenario-, Capability-, RuntimeBinding- oder ValidationCase-Artefakte. FunctionalMLDS erzeugt diese Artefakte explizit und validiert sie ueber Schema-, Invarianten-, Traceability- und Handoff-Reports.

### RQ3: Ist der Ansatz ueber mehrere MLDS-Domaenen hinweg wiederverwendbar?

Die bestehende Case Study liefert positive Evidenz fuer drei Domaenen:

- `bestfit_career_fair`
- `classroom_dinosaur`
- `steinpilz_brand_room`

Die bisherigen Reports zeigen `schema and invariant success = 3/3`, `stage completion ratio = 1.0` und `generalizability score = 1.0`. Das ist Case-Study-Evidenz fuer Wiederverwendbarkeit im untersuchten Korpus, aber keine statistische Allgemeingueltigkeit.

## Warum Der Wizard Fuer Das Paper Wichtig Ist

Vor dem Umbau existierten Case-Study-Pipeline und Unity-Wizard als getrennte Perspektiven:

- Die Pipeline konnte FunctionalMLDS-Artefakte erzeugen.
- Der Wizard konnte Interactive-Agents-Projekte erzeugen.

Durch den Umbau kann der Wizard selbst zwischen Baseline und Treatment umschalten. Dadurch entsteht ein wissenschaftlich sauberer Vergleichspunkt:

- gleiche Eingabe,
- gleicher Benutzerablauf,
- gleicher Ziel-Runtime-Typ,
- unterschiedliche Evidenzschicht.

Der FunctionalMLDS-Modus ist damit kein Nebenartefakt mehr, sondern Teil des praktischen Authoring-Flows. Das ist wichtig, weil die Case Study zeigen soll, dass das Metamodell nicht nur offline modellierbar ist, sondern in eine bestehende Toolchain eingebettet werden kann.

## Verteidigbare Kernaussage

Eine vorsichtige, wissenschaftlich belastbare Aussage lautet:

FunctionalMLDS macht die evaluierte MLDS-zu-Interactive-Agents-Pipeline fuer den untersuchten Drei-Domaenen-Korpus tracebar, validierbar, reparierbar und runtime-pruefbar. Der Wizard-Umbau zeigt, dass diese Evidenzschicht in den bestehenden Authoring-Workflow integrierbar ist, ohne den Legacy-Modus zu brechen.

Eine zu starke Aussage waere:

FunctionalMLDS ist allgemein fuer alle industriellen Toolchains korrekt.

Diese staerkere Aussage ist durch die aktuelle Case Study nicht gedeckt. Sie wuerde weitere Domaenen, wiederholte Laeufe, Expert Reviews und eine produktionsnahe Toolchain-Integration erfordern.

## Paper-Relevante Artefaktliste

Fuer ein Paper sollten mindestens diese Artefakte referenziert werden:

- `output/metamodel/mlds_project_wizard_user_workflow.md`
- `output/case_studies/paper_artifacts/baseline_definition.md`
- `output/case_studies/paper_artifacts/comparison_metrics.md`
- `output/case_studies/paper_artifacts/tables/metamodel_coverage.md`
- `output/case_studies/paper_artifacts/tables/validation_repair.md`
- `output/case_studies/<case_id>/functionalmlds/functionalmlds.instance.generated.json`
- `output/case_studies/<case_id>/validation/schema_validation.json`
- `output/case_studies/<case_id>/validation/functionalmlds_invariants_validation.json`
- `output/case_studies/<case_id>/validation/traceability_metrics.json`
- `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/<case_id>/trace_map.json`
- `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py`
- `InteractivAgents/InteractiveAgents2/Assets/InteractiveAgents/Editor/QuickAgentManagerFunctionalMldsSmoke.cs`
