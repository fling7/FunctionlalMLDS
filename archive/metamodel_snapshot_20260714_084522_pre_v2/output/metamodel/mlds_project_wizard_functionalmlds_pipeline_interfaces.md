# FunctionalMLDS-Pipeline-Schnittstellen fuer den MLDS Project Wizard

Stand: 2026-07-09

## Zweck

Dieses Dokument beschreibt die vorhandenen Pipeline-Schnittstellen, die der MLDS Project Wizard im neuen FunctionalMLDS-Modus wiederverwenden kann. Ziel ist nicht, den Legacy-Ablauf zu ersetzen, sondern aus derselben MLDS-Eingabe zusaetzlich eine FunctionalMLDS-Instanz, eine Traceability-Struktur und ein in Unity nutzbares Interactive-Agents-Projekt zu erzeugen.

Der Wizard darf im FunctionalMLDS-Modus einen Commit erst als erfolgreich melden, wenn die erzeugten Artefakte gegen die vorhandenen Schema-, Invariant- und Materialisierungspruefungen validiert wurden.

## Hauptpipeline

| Stufe | Python-Schnittstelle | Eingabe | Zentrale Ausgabe |
| --- | --- | --- | --- |
| MLDS-Ingestion | `mlds_ingestion.run_pipeline(inputs, out_root)` | Liste von MLDS/MLDSI-Dateien, Zielordner | Case-Ordner mit normalisiertem Scene Graph und Ingestion-Report |
| Scene Semantics | `scene_semantics.run_scene_semantics_for_case(case_dir, model_override=None, max_repair_attempts=3, config_path=None)` | Case-Ordner | `intermediate/scene_semantics.json`, Semantik-Validierung |
| Agent Roles | `agent_roles.run_agent_roles_for_case(case_dir, model_override=None, max_repair_attempts=3, config_path=None)` | Case-Ordner mit Scene Semantics | `intermediate/agent_roles.generated.json`, `intermediate/handoff_matrix.json` |
| Knowledge Synthesis | `knowledge_synthesis.run_knowledge_synthesis_for_case(case_dir, model_override=None, max_repair_attempts=2, config_path=None)` | Case-Ordner mit Rollen und Szene | Knowledge-JSON und materialisierte Wissensdateien fuer Agenten |
| Agent Placement | `agent_placement.run_agent_placement_for_case(case_dir)` | Case-Ordner mit Szene und Rollen | `intermediate/agent_placements.json` |
| FunctionalMLDS Assembly | `functionalmlds_assembler.run_functionalmlds_assembly_for_case(case_dir)` | Case-Ordner mit Szene, Rollen, Wissen, Placement | `functionalmlds/functionalmlds.instance.generated.json` |
| Projekt-Materialisierung | `project_materializer.run_project_materializer_for_case(case_dir, backend_root=DEFAULT_BACKEND_ROOT)` | Case-Ordner mit FunctionalMLDS-Instanz | Backend-Projekt unter `InteractiveAgents/projects/<case_id>/` |

Der aktuell voreingestellte Backend-Zielordner ist:

`InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents`

## Validierungsstufen

| Pruefung | Python-Schnittstelle | Zweck |
| --- | --- | --- |
| Schema | `schema_validator.run_schema_validation_for_case(case_dir, backend_root=DEFAULT_BACKEND_ROOT)` | prueft Case-Artefakte und materialisiertes Backend-Projekt gegen die JSON-Schemata |
| FunctionalMLDS-Invarianten | `functionalmlds_invariants.run_functionalmlds_invariant_validation_for_case(case_dir)` | prueft Metamodell-Invarianten, z. B. Referenzen, Pflichtfelder, Traceability-Anforderungen |
| Traceability | `traceability_metrics.run_traceability_metrics_for_case(case_dir)` | misst Abdeckung von MLDS-Objekten, FunctionalMLDS-Elementen, RuntimeBindings und ValidationCases |
| Handoff | `handoff_metrics.run_handoff_metrics_for_case(case_dir, config_path=None)` | prueft, ob Spezialwissen und Weiterleitungen zwischen Agenten konsistent abgebildet sind |
| Stage Completion | `stage_completion.run_stage_completion_for_case(case_dir)` | prueft, ob alle erwarteten Pipeline-Stufen erfolgreich abgeschlossen wurden |

## Erwartete Wizard-Verwendung

Der Analyze-Schritt sollte im FunctionalMLDS-Modus mindestens bis zu diesen Artefakten laufen:

- normalisierte MLDS-Szene
- Scene Semantics
- Agent Roles
- Handoff Matrix
- Knowledge Draft
- Placement Preview
- FunctionalMLDS-Summary fuer die Wizard-UI

Der Commit-Schritt muss danach mindestens diese Artefakte erzeugen:

- `functionalmlds/functionalmlds.instance.generated.json`
- `validation/schema_validation.json`
- `validation/functionalmlds_invariant_validation.json`
- `validation/project_materialization_validation.json`
- `validation/traceability_metrics.json`
- `InteractiveAgents/projects/<case_id>/project.json`
- `InteractiveAgents/projects/<case_id>/room_plan.json`
- `InteractiveAgents/projects/<case_id>/agents.json`
- `InteractiveAgents/projects/<case_id>/trace_map.json`
- `InteractiveAgents/projects/<case_id>/kb/...`

## Bestandsnachweis

Die vorhandene Pipeline wurde bereits fuer drei Case-Study-Cases materialisiert. Alle drei Cases besitzen eine FunctionalMLDS-Instanz, eine Invariant-Validierung, ein materialisiertes Backend-Projekt und eine `trace_map.json`.

| Case | FunctionalMLDS | Backend-Projekt | Agenten | KB-Dateien | Trace-Steps | Runtime-Actions | Validation-Cases | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `bestfit_career_fair` | vorhanden | vorhanden | 5 | 15 | 12 | 12 | 6 | valid |
| `classroom_dinosaur` | vorhanden | vorhanden | 4 | 8 | 12 | 12 | 6 | valid |
| `steinpilz_brand_room` | vorhanden | vorhanden | 6 | 18 | 12 | 12 | 6 | valid |

Die Stage-Manifeste enthalten fuer alle drei Cases den Status `success` fuer die fuer den Wizard relevanten Stufen:

- `mlds_ingestion`
- `scene_semantics`
- `agent_roles`
- `knowledge_synthesis`
- `agent_placement`
- `functionalmlds_assembly`
- `project_materialization`
- `schema_validation`
- `functionalmlds_invariants`
- `traceability_metrics`
- `handoff_metrics`
- `stage_completion`

## Konsequenz fuer den Umbau

Der FunctionalMLDS-Modus sollte nicht die alte `_generate_arrow_draft`-Logik erweitern, bis sie selbst zu einer zweiten Pipeline wird. Sinnvoller ist ein Backend-Adapter, der den bestehenden Wizard-Datenfluss kapselt und intern die Pipeline-Stufen aus `tools/case_study_pipeline/` ausfuehrt.

Damit bleibt der Legacy-Modus unveraendert, waehrend der FunctionalMLDS-Modus dieselben fachlichen Ergebnisse wie bisher liefert, aber zusaetzlich metamodel-konforme Artefakte und Validierungsnachweise erzeugt.
