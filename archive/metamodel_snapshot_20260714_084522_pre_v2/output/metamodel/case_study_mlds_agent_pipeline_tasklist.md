# Taskliste: Case Study Pipeline fuer FunctionalMLDS + Interactive Agents

Stand: 2026-07-08

Ziel: Aufbau einer wissenschaftlich auswertbaren Case-Study-Pipeline, die beliebige MLDS-Dateien in ein raumkundiges Multi-Agenten-Projekt ueberfuehrt, dabei eine FunctionalMLDS-Instanz erzeugt, Runtime-Verhalten in Unity/Backend ausfuehrt und die Traceability sowie Korrektheit automatisch validiert.

Wichtig: Der OpenAI API Key ist lokal in der ignorierten Backend-Datei `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/config.json` gespeichert. Der Key darf nicht in Berichte, Logs, Git-Commits, Tasklisten oder Validierungsartefakte geschrieben werden.

## Grundprinzip

Die Pipeline wird modular aufgebaut. Jede Stufe liest klar definierte Artefakte, schreibt klar definierte Artefakte und besitzt eine Zwischenpruefung. Bei Fehlern wird nicht global neu gestartet, sondern nur die betroffene Stufe repariert und erneut ausgefuehrt.

Arbeitsverzeichnis fuer Case Studies:

```text
output/case_studies/<case_id>/
  input/
  intermediate/
  functionalmlds/
  interactive_agents_project/
  runtime_logs/
  validation/
  paper_artifacts/
```

Jede Stufe schreibt einen Manifest-Eintrag:

```text
output/case_studies/<case_id>/stage_manifest.json
```

Das Manifest enthaelt pro Stufe: Stage-ID, Input-Dateien, Input-Hashes, Output-Dateien, Output-Hashes, Modellname bei LLM-Aufrufen, Prompt-Version, Zeitstempel, Status, Fehlerliste und Reparaturversuche.

## Pipeline-Module

| Modul | Aufgabe | LLM-Aufruf |
| --- | --- | --- |
| `MldsIngestion` | MLDS-Datei lesen, Schema erkennen, Szene normalisieren | nein |
| `SceneSemantics` | Raumfunktion, Zonen, Objektgruppen, Besucherintentionen ableiten | ja |
| `AgentRoleSynthesis` | Agentenrollen, Personas, Expertise, Wissenstags erzeugen | ja |
| `KnowledgeSynthesis` | lokale Wissenseintraege aus MLDS-Kontext erzeugen | ja |
| `SpatialPlacement` | Agentenpositionen und Blickrichtungen bestimmen | optional, primaer deterministisch |
| `FunctionalMldsAssembler` | Requirements, UseCases, Scenarios, Capabilities, Bindings erzeugen | ja |
| `ProjectMaterializer` | `project.json`, `room_plan.json`, `agents.json`, `kb/` schreiben | nein |
| `RuntimeExecutor` | Backend-Setup, Chat-Tests, Handoff-Tests ausfuehren | optional fuer Testfragen |
| `Validator` | Invarianten, Traceability, Placement, Runtime-Logs pruefen | optional fuer qualitative Antwortbewertung |
| `PaperArtifactBuilder` | Tabellen, Trace-Beispiele, Metriken, Figuren erzeugen | nein |

## 0. Vorbereitungs- und Sicherheitschecks

- [x] `config.json` im Backend auf Git-Ignorierung pruefen.
  - Zwischenpruefung: `git check-ignore config.json` muss erfolgreich sein.
  - Zwischenpruefung: `git ls-files config.json` darf die Datei nicht als getrackt melden.
  - Reparatur: Falls getrackt, Key nicht speichern; stattdessen `.env` oder User-Secret verwenden und Git-Index bereinigen.

- [x] API-Key lokal speichern.
  - Output: Backend-`config.json` enthaelt einen nicht-leeren `openai_api_key`.
  - Zwischenpruefung: Nur redaktierten Status ausgeben, niemals Key.

- [x] Python-Backend syntaktisch pruefen.
  - Befehl: `python -m py_compile main.py backend/*.py`
  - Erfolgskriterium: keine Compile-Fehler.
  - Reparatur: Syntaxfehler isoliert im betroffenen Modul beheben.

- [x] Unity-Projektstruktur pruefen.
  - Input: `InteractivAgents/InteractiveAgents2`
  - Erfolgskriterien:
    - `ProjectSettings/ProjectVersion.txt` vorhanden.
    - `Assets/Scripting/QuickAgentManager.cs` vorhanden.
    - `Assets/Scripting/ArrowProjectWizard.cs` vorhanden.
    - `Assets/Scripting/ProjectManagerUI.cs` vorhanden.
  - Reparatur: fehlende Pfade dokumentieren und Import-/Copy-Schritt definieren.

## 1. Case-Study-Korpus definieren

- [x] Initiale MLDS-Dateien fuer die Validierung auswaehlen.
  - Mindestkorpus:
    - `Assets/Scripting/MLDSSteinpilz.json` fuer Food/Brand Experience.
    - `Assets/Scripting/KlassenraumMLDS.json` fuer Education.
    - `Assets/Scripting/BestfitMLDS.json` fuer Career Fair/Corporate Booth.
  - Erweiterbarkeit: zusaetzlich `--input-glob "*.json"` fuer beliebige MLDS-Dateien.

- [x] Fuer jede MLDS-Datei eine `case_id` erzeugen.
  - Regel: Dateiname normalisieren, z. B. `steinpilz_brand_room`, `classroom_dinosaur`, `bestfit_career_fair`.
  - Output: `output/case_studies/<case_id>/input/source_mlds.json`
  - Zwischenpruefung: Jede `case_id` ist eindeutig.
  - Reparatur: Bei Kollision Suffix anhaengen.

- [x] Input-Hash berechnen.
  - Output: `input/source_mlds.sha256`
  - Zwischenpruefung: Hash im Stage-Manifest vorhanden.
  - Reparatur: Manifest neu schreiben.

## 2. MLDS-Ingestion und Normalisierung

- [x] `MldsIngestion` implementieren.
  - Empfohlener Pfad: `tools/case_study_pipeline/mlds_ingestion.py`
  - Input: `source_mlds.json`
  - Output: `intermediate/scene_graph.normalized.json`

- [x] Schemaerkennung implementieren.
  - Erkenne mindestens:
    - MLDS-Schema mit `scene.objects`
    - einfaches RoomPlan-Schema mit `zones` und `spawn_points`
  - Zwischenpruefung: `schema_kind` muss gesetzt sein.
  - Reparatur: Falls unbekannt, Fehlerbericht mit ersten Top-Level-Keys ausgeben.

- [x] Objektliste extrahieren.
  - Felder:
    - `object_id`
    - `object_type`
    - `group`
    - `position`
    - `rotation`
    - `dimensions`
    - `specification`
  - Zwischenpruefung:
    - mindestens ein Objekt vorhanden.
    - alle IDs eindeutig oder automatisch stabil nachgeneriert.
  - Reparatur: fehlende IDs deterministisch erzeugen.

- [x] Raumdimensionen extrahieren.
  - Output:
    - `room_bounds`
    - `environment_type`
    - `scene_name`
  - Zwischenpruefung: Wenn Dimensionen fehlen, Fallback-Bounds aus Objektpositionen berechnen.

- [x] Objektgruppen zusammenfassen.
  - Output: `intermediate/object_group_summary.json`
  - Inhalt: Gruppe, Anzahl, Objektarten, typische Positionen, Beispiel-Spezifikationen.
  - Zwischenpruefung: Jede nicht-strukturelle Objektgruppe muss mindestens ein Objekt referenzieren.

## 3. Semantische Raumanalyse mit LLM

- [x] Prompt-Version `scene_semantics_v1` definieren.
  - Pfad: `tools/case_study_pipeline/prompts/scene_semantics_v1.md`
  - Input: normalisierte Objektgruppen, Raumdimensionen, Szenenname.
  - Output-Schema:
    - `domain`
    - `room_purpose`
    - `visitor_goals`
    - `semantic_zones`
    - `important_objects`
    - `interaction_topics`
    - `agent_role_candidates`

- [x] LLM-Aufruf als Structured Output implementieren.
  - Pfad: `tools/case_study_pipeline/llm_client.py`
  - Modellname aus Backend-Konfiguration lesen.
  - Kein API-Key in Logs schreiben.

- [x] Semantische Analyse ausfuehren.
  - Output: `intermediate/scene_semantics.json`
  - Zwischenpruefung:
    - `domain` nicht leer.
    - mindestens 2 `visitor_goals`.
    - mindestens 2 `semantic_zones`.
    - alle referenzierten Objekt-IDs existieren im normalisierten Scene Graph.
  - Reparaturschleife:
    - Wenn Objekt-IDs halluziniert wurden, LLM mit Fehlermeldung und erlaubter ID-Liste erneut aufrufen.
    - Maximal 3 Reparaturversuche.
    - Danach Stage als `needs_manual_review` markieren.

## 4. Agentenrollen ableiten

- [x] Prompt-Version `agent_roles_v1` definieren.
  - Input:
    - `scene_semantics.json`
    - `object_group_summary.json`
    - optional vorhandene Agentenvorlagen.
  - Output-Schema:
    - `agents[]`
      - `id`
      - `display_name`
      - `persona`
      - `expertise[]`
      - `knowledge_tags[]`
      - `responsible_zone_ids[]`
      - `grounded_object_ids[]`
      - `handoff_targets[]`
      - `voice`
      - `voice_style`
      - `tts_model`

- [x] AgentRoleSynthesis ausfuehren.
  - Output: `intermediate/agent_roles.generated.json`
  - Zwischenpruefung:
    - 2 bis 8 Agenten pro Case Study.
    - Jede Agent-ID ist eindeutig.
    - Jede `knowledge_tag` ist slug-kompatibel.
    - Jeder Agent hat mindestens eine Expertise.
    - Jeder Agent referenziert mindestens eine Zone oder mindestens ein Objekt.
  - Reparaturschleife:
    - Ungueltige IDs normalisieren.
    - Fehlende Grounding-Objekte automatisch aus Expertise/Zone ergaenzen.
    - Bei Rollen ohne klare Zuständigkeit LLM mit Kritik erneut aufrufen.

- [x] Handoff-Matrix erzeugen.
  - Output: `intermediate/handoff_matrix.json`
  - Inhalt: Quelle, Ziel, Bedingung, fachlicher Grund.
  - Zwischenpruefung:
    - Kein Agent darf sich selbst als Handoff-Ziel haben.
    - Jedes Ziel muss existieren.
  - Reparatur: ungueltige Handoff-Ziele entfernen oder auf passende vorhandene Agenten mappen.

## 5. Wissensbasis generieren

- [x] Prompt-Version `knowledge_synthesis_v1` definieren.
  - Input:
    - MLDS-Objekt-Spezifikationen
    - Raumsemantik
    - Agentenrollen
  - Output-Schema:
    - `knowledge_entries[]`
      - `tag`
      - `name`
      - `source_object_ids[]`
      - `text`
      - `intended_agents[]`

- [x] Wissenseintraege generieren.
  - Output: `intermediate/knowledge.generated.json`
  - Zwischenpruefung:
    - Jeder `knowledge_tag` aus Agenten hat mindestens einen Wissenseintrag oder ist bewusst als `common` markiert.
    - Jeder Wissenseintrag referenziert vorhandene Objekte oder eine globale Raumsemantik.
    - Keine API-Keys oder Systempfade im Text.
  - Reparaturschleife:
    - Fehlende Tags mit kurzem Eintrag auffuellen.
    - Halluzinierte Objekt-IDs entfernen und LLM zur Korrektur erneut aufrufen.

- [x] Wissenseintraege als Dateien materialisieren.
  - Output:
    - `interactive_agents_project/kb/<tag>/<name>.txt`
  - Zwischenpruefung:
    - jede Datei lesbar.
    - keine leeren Wissensdateien.

## 6. Agentenplatzierung

- [x] Deterministische Platzierung wiederverwenden.
  - Modul: bestehende Logik aus `backend/placement.py`
  - Input:
    - normalisierte Szene
    - Agentenrollen
  - Output: `intermediate/agent_placements.json`

- [x] Platzierungsregeln definieren.
  - Agenten stehen innerhalb der Raumgrenzen.
  - Agenten stehen nicht in strukturellen Objekten.
  - Mindestabstand zwischen Agenten.
  - Agenten stehen semantisch nahe an ihren Zonen/Objekten, soweit moeglich.

- [x] Platzierung pruefen.
  - Zwischenpruefung:
    - alle Agenten haben `position`.
    - alle Agenten haben `forward`.
    - keine Position liegt ausserhalb der Bounds.
    - kein Agent liegt innerhalb eines Hindernis-Footprints.
  - Reparaturschleife:
    - automatische Neupositionierung per Spiral-/Grid-Suche.
    - falls weiterhin ungueltig: Placement-Stage als `needs_manual_review`.

## 7. FunctionalMLDS-Instanz erzeugen

- [x] FunctionalMLDS-JSON-Schema definieren.
  - Pfad: `tools/case_study_pipeline/schemas/functionalmlds_case_study.schema.json`
  - Muss die Kernklassen abbilden:
    - `Requirement`
    - `UseCase`
    - `Actor`
    - `Scenario`
    - `ScenarioStep`
    - `Event`
    - `Condition`
    - `StateAssertion`
    - `Entity`
    - `Agent`
    - `CapabilityUse`
    - `Capability`
    - `Effect`
    - `RuntimeBinding`
    - `RuntimeAction`
    - `ValidationCase`

- [x] Prompt-Version `functionalmlds_assembly_v1` definieren.
  - Input:
    - Raumsemantik
    - Agentenrollen
    - Wissen
    - Handoff-Matrix
    - Runtime-Endpunkte
  - Output:
    - `functionalmlds/functionalmlds.instance.generated.json`

- [x] Requirements erzeugen.
  - Mindestanforderungen:
    - MLDS-basierte Projektgenerierung
    - raumbezogene Agentenantwort
    - agentenspezifisches Wissen
    - Handoff an zuständigen Agenten
    - Runtime-Traceability
  - Zwischenpruefung:
    - mindestens 5 Requirements.
    - jedes Requirement hat stabile ID und Text.

- [x] UseCases erzeugen.
  - Haupt-UseCase:
    - `UC-<case_id>-01`: `Generate and use spatially grounded multi-agent guide`
  - Optionale UseCases:
    - Projektgenerierung aus MLDS
    - Besucherfrage beantworten
    - Handoff ausfuehren
  - Zwischenpruefung:
    - mindestens ein Main UseCase.
    - Include/Extend nur verwenden, wenn semantisch begruendet.

- [x] Main Scenario erzeugen.
  - Muss mindestens enthalten:
    - MLDS laden
    - Szene analysieren
    - Agentenrollen ableiten
    - Wissen erzeugen
    - Agenten platzieren
    - Projekt materialisieren
    - Unity Setup ausfuehren
    - Besucherfrage beantworten
    - optional Handoff
  - Zwischenpruefung:
    - genau ein `Scenario.kind = main` pro UseCase.
    - Schritte geordnet.

- [x] Capabilities und RuntimeBindings erzeugen.
  - Mindest-Capabilities:
    - `AnalyzeMLDSScene`
    - `DeriveSpatialAgentRoles`
    - `GenerateRoomKnowledge`
    - `PlaceAgentsInScene`
    - `AnswerRoomGroundedQuestion`
    - `HandoffToResponsibleAgent`
  - Mindest-RuntimeBindings:
    - `POST /projects/arrow/analyze`
    - `POST /projects/arrow/commit`
    - `POST /setup`
    - `POST /chat`
  - Zwischenpruefung:
    - Jede `CapabilityUse` referenziert genau eine `Capability`.
    - Jede `Capability` hat mindestens einen `Effect`.
    - Keine `ScenarioStep`-Instanz referenziert direkt eine `RuntimeAction`.

- [x] ValidationCases erzeugen.
  - Mindestens:
    - Modellvalidierung
    - Projektmaterialisierung
    - Setup-Validierung
    - Chat-Antwortvalidierung
    - Handoff-Validierung
  - Zwischenpruefung:
    - Jeder ValidationCase referenziert pruefbare StateAssertions oder RuntimeBinding.

## 8. Interactive-Agents-Projekt materialisieren

- [x] Projektordner erzeugen.
  - Ziel:
    - `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/<case_id>/`
  - Output:
    - `project.json`
    - `room_plan.json`
    - `agents.json`
    - `kb/`

- [x] `project.json` schreiben.
  - Felder:
    - `id`
    - `display_name`
    - `description`
    - `created_ms`
    - `updated_ms`
    - optional `functionalmlds_trace_path`
  - Zwischenpruefung: JSON valide.

- [x] `room_plan.json` schreiben.
  - Bei MLDS-Input: Original oder normalisierte MLDS-Struktur beibehalten.
  - Zwischenpruefung: Backend kann Datei laden.

- [x] `agents.json` schreiben.
  - Muss kompatibel mit `AgentSpec.from_dict` sein.
  - Felder:
    - `id`
    - `display_name`
    - `persona`
    - `expertise`
    - `knowledge_tags`
    - `position`
    - `forward`
    - `voice`
    - `voice_style`
    - `tts_model`
  - Zwischenpruefung:
    - Backend kann Agenten laden.
    - `tts_model` darf nicht `standard` bleiben; normalisieren auf gueltiges TTS-Modell.

- [x] KB-Dateien kopieren/schreiben.
  - Zwischenpruefung:
    - alle Agent-`knowledge_tags` haben vorhandene Ordner.
    - mindestens ein `common`-Wissen, wenn sinnvoll.

## 9. Backend- und Runtime-Instrumentierung

- [x] Trace-ID-Felder einfuehren, ohne bestehende API zu brechen.
  - Optionen:
    - Zusatzdatei `trace_map.json` im Projektordner.
    - optionale Felder in `agents.json`, die Backend ignorieren darf.
  - Zwischenpruefung: bestehendes `/setup` bleibt kompatibel.
  - Ergebnis 2026-07-08:
    - `trace_map.json` wird pro materialisiertem Projekt erzeugt und durch den Materializer validiert.
    - `GET /health` erfolgreich.
    - `POST /setup` mit `project_id=steinpilz_brand_room` erfolgreich; 6 Agenten mit Positionsdaten geladen.
    - Backend-Start fuer nicht-interaktive Validierung robust gemacht (`config.json` mit BOM, EOF-Fallback auf Beispielpfade).

- [x] Runtime-Logformat definieren.
  - Output:
    - `runtime_logs/events.jsonl`
  - Pro Event:
    - `timestamp`
    - `case_id`
    - `session_id`
    - `event_type`
    - `agent_id`
    - `scenario_step_id`
    - `capability_id`
    - `runtime_binding_id`
    - `runtime_action_id`
    - `input_summary`
    - `output_summary`
  - Ergebnis 2026-07-08:
    - JSON-Schema angelegt: `tools/case_study_pipeline/schemas/runtime_event.schema.json`.
    - Hilfsmodul angelegt: `tools/case_study_pipeline/runtime_logging.py`.
    - Deutsche Formatspezifikation angelegt: `output/metamodel/runtime_log_format.md`.
    - Leere Ziel-Logs pro Case angelegt: `runtime_logs/events.jsonl`.
    - Zwischenpruefung erfolgreich: synthetisches `/setup`-Event gegen `trace_map.json` validiert, JSONL-Roundtrip erfolgreich, Secret-Redaction erfolgreich.

- [x] Backend-Logging minimal erweitern.
  - Falls Codeaenderung:
    - nur additive Felder.
    - keine API-Keys loggen.
  - Zwischenpruefung:
    - `/setup` und `/chat` funktionieren weiterhin mit alten Clients.
  - Ergebnis 2026-07-08:
    - Backend-Modul `backend/runtime_trace.py` angelegt.
    - `POST /setup` schreibt `backend_setup_completed` nach `runtime_logs/events.jsonl`.
    - `POST /chat` schreibt `backend_chat_completed`; bei Handoff zusaetzlich `backend_handoff_completed`.
    - API-Antworten bleiben unveraendert; Logging ist nur additiver Side Effect.
    - Zwischenpruefung erfolgreich: `/setup` mit echtem Backend gestartet; `/chat` mit Fake-OpenAI-Testserver ohne API-Token ausgefuehrt; Events gegen `trace_map.json` validiert; Secret-Check erfolgreich.

- [x] Unity-Logging optional ergaenzen.
  - Ziel:
    - Chat-Events, Handoff-Ankunft, Agentenauswahl und Setup-Ergebnis protokollieren.
  - Zwischenpruefung:
    - Unity-Kompatibilitaet nicht brechen.
  - Ergebnis 2026-07-08:
    - Unity-Komponente `unity_scripts/FunctionalMLDSUnityRuntimeLogger.cs` angelegt.
    - `QuickAgentManager` protokolliert optional `unity_setup_completed`, `unity_chat_sent`, `unity_chat_received`, `unity_handoff_arrived` und `unity_agent_selected`.
    - Logging ist per Default deaktiviert (`enableUnityRuntimeLogging = false`) und damit additiv.
    - Runtime-Event-Schema und Validator um `unity_agent_selected` und `unity_handoff_arrived` erweitert.
    - Zwischenpruefung erfolgreich: neue Unity-Eventtypen gegen `trace_map.json` validiert, C#-Klammerpruefung erfolgreich, `git diff --check` erfolgreich.
    - Hinweis: Unity-Editor/Batchmode war in dieser Umgebung nicht verfuegbar; vollstaendiger Unity-Import bleibt als spaetere manuelle Pruefung sinnvoll.

## 10. Validierungslogik implementieren

- [x] JSON-Schema-Validator implementieren.
  - Pfad: `tools/case_study_pipeline/validators/schema_validator.py`
  - Prueft:
    - normalisierte Szene
    - Agentenrollen
    - Wissen
    - FunctionalMLDS-Instanz
    - Projektdateien
  - Ergebnis 2026-07-08:
    - Validator implementiert: `tools/case_study_pipeline/validators/schema_validator.py`.
    - Fehlende Schemas ergaenzt:
      - `tools/case_study_pipeline/schemas/normalized_scene.schema.json`
      - `tools/case_study_pipeline/schemas/knowledge.schema.json`
      - `tools/case_study_pipeline/schemas/interactive_agents_project.schema.json`
    - Agentenrollen werden als zusammengesetztes Artefakt aus `agent_roles.generated.json` und `handoff_matrix.json` validiert.
    - Runtime-Events werden, falls vorhanden, zeilenweise gegen `runtime_event.schema.json` validiert.
    - Batch-Runner integriert `schema_validation` nach `project_materialization`.
    - Zwischenpruefung erfolgreich:
      - `python -m py_compile` fuer Validator und Batch-Runner erfolgreich.
      - alle Schema-JSONs parsebar.
      - alle drei Case Studies validiert; je Case 7/7 Artefakte gueltig.
      - Aggregate Report steht auf `stage=schema_validation`, `success_count=3`, `failure_count=0`.

- [x] FunctionalMLDS-Invarianten pruefen.
  - Invarianten:
    - pro UseCase genau ein Main Scenario.
    - Scenario hat mindestens einen Step.
    - ScenarioStep besitzt keine direkte RuntimeAction.
    - CapabilityUse referenziert genau eine Capability.
    - Capability hat mindestens einen Effect.
    - RuntimeBinding hat mindestens eine RuntimeAction.
    - ValidationCase referenziert pruefbare Elemente.
  - Ergebnis 2026-07-08:
    - Eigenstaendiger Validator implementiert: `tools/case_study_pipeline/validators/functionalmlds_invariants.py`.
    - Report pro Case: `validation/functionalmlds_invariants_validation.json`.
    - Jede der sieben Invarianten wird separat mit `status`, `checked_count`, `error_count` und Fehlerliste ausgewiesen.
    - Batch-Runner integriert `functionalmlds_invariants` nach `schema_validation`.
    - Zwischenpruefung erfolgreich:
      - `python -m py_compile` fuer Validator und Batch-Runner erfolgreich.
      - `git diff --check` erfolgreich.
      - alle drei Case Studies validiert; je Case 7/7 Invarianten bestanden.
      - je Case 47 Modellelemente gegen die Invarianten geprueft.
      - Aggregate Report steht auf `stage=functionalmlds_invariants`, `success_count=3`, `failure_count=0`.

- [x] Traceability-Metriken berechnen.
  - Metriken:
    - Requirement-to-Validation-Coverage
    - ScenarioStep-to-Capability-Coverage
    - Capability-to-RuntimeBinding-Coverage
    - RuntimeAction-to-Log-Coverage
    - Agent-to-KnowledgeTag-Coverage
    - ObjectGroup-to-AgentRole-Grounding
  - Ergebnis 2026-07-08:
    - Metrikmodul implementiert: `tools/case_study_pipeline/validators/traceability_metrics.py`.
    - Report pro Case: `validation/traceability_metrics.json`.
    - Batch-Runner integriert `traceability_metrics` nach `functionalmlds_invariants`.
    - Reparatur ausgefuehrt: FunctionalMLDS-Assembly ergaenzt `VC-<case>-MLDS-INGESTION`, sodass `REQ-<case>-001` explizit validiert wird.
    - Zwischenpruefung erfolgreich:
      - `python -m py_compile` fuer Metrikmodul, Assembler und Batch-Runner erfolgreich.
      - `git diff --check` erfolgreich.
      - alle drei Case Studies mit `traceability_metrics: success`.
      - Aggregate Report steht auf `stage=traceability_metrics`, `success_count=3`, `failure_count=0`.
    - Coverage-Ergebnisse:
      - Requirement-to-Validation: 1.0 fuer alle drei Cases.
      - Capability-to-RuntimeBinding: 1.0 fuer alle drei Cases.
      - Agent-to-KnowledgeTag: 1.0 fuer alle drei Cases.
      - ObjectGroup-to-AgentRole-Grounding: 1.0 fuer alle drei Cases, strukturelle Gruppen wie `floor`/`walls` separat ausgeschlossen und dokumentiert.
      - ScenarioStep-to-Capability: 0.833333 fuer alle drei Cases; offene Steps sind ActorIntent-Schritte ohne technische Capability.
      - RuntimeAction-to-Log: 0.166667 fuer `steinpilz_brand_room`, 0.0 fuer die beiden anderen Cases; erwartbar bis die Runtime-Tests pro Case ausgefuehrt wurden.

- [x] Placement-Metriken berechnen.
  - Metriken:
    - Anteil gueltiger Agentenpositionen.
    - minimale Distanz zwischen Agenten.
    - Anzahl Hindernisueberlappungen.
    - Distanz zu verantwortlichen Objektgruppen/Zonen.
  - Ergebnis 2026-07-08:
    - Metrikmodul implementiert: `tools/case_study_pipeline/validators/placement_metrics.py`.
    - Report pro Case: `validation/placement_metrics.json`.
    - Batch-Runner integriert `placement_metrics` nach `traceability_metrics`.
    - Zwischenpruefung erfolgreich:
      - `python -m py_compile` fuer Metrikmodul und Batch-Runner erfolgreich.
      - `git diff --check` erfolgreich.
      - alle drei Case Studies mit `placement_metrics: success`.
      - Aggregate Report steht auf `stage=placement_metrics`, `success_count=3`, `failure_count=0`.
    - Messergebnisse:
      - `steinpilz_brand_room`: gueltige Positionsquote 1.0, Mindestabstand 0.985146, Hindernisueberlappungen 0.
      - `classroom_dinosaur`: gueltige Positionsquote 1.0, Mindestabstand 1.288, Hindernisueberlappungen 0.
      - `bestfit_career_fair`: gueltige Positionsquote 1.0, Mindestabstand 0.753558, Hindernisueberlappungen 0.

- [x] Handoff-Metriken berechnen.
  - Metriken:
    - Anteil gueltiger Handoff-Ziele.
    - Handoff-Entscheidung korrekt fuer Testfragen.
    - keine Selbst-Handoffs.
    - keine Kettenweiterleitung ueber Limit.
  - Ergebnis 2026-07-08:
    - Metrikmodul implementiert: `tools/case_study_pipeline/validators/handoff_metrics.py`.
    - Report pro Case: `validation/handoff_metrics.json`.
    - Batch-Runner integriert `handoff_metrics` nach `placement_metrics`.
    - Zwischenpruefung erfolgreich:
      - `python -m py_compile` fuer Metrikmodul und Batch-Runner erfolgreich.
      - `git diff --check` erfolgreich.
      - alle drei Case Studies mit `handoff_metrics: success`.
      - Aggregate Report steht auf `stage=handoff_metrics`, `success_count=3`, `failure_count=0`.
    - Messergebnisse:
      - `steinpilz_brand_room`: 15 Handoff-Paare, gueltige Handoff-Ziele 1.0, Selbst-Handoffs 0, fehlende Matrix-Paare 0, Extra-Matrix-Paare 0.
      - `classroom_dinosaur`: 6 Handoff-Paare, gueltige Handoff-Ziele 1.0, Selbst-Handoffs 0, fehlende Matrix-Paare 0, Extra-Matrix-Paare 0.
      - `bestfit_career_fair`: 12 Handoff-Paare, gueltige Handoff-Ziele 1.0, Selbst-Handoffs 0, fehlende Matrix-Paare 0, Extra-Matrix-Paare 0.
    - Hinweis:
      - `handoff_decision_accuracy` ist vorbereitet, aber noch nicht bewertet (`decision_test_count=0`), weil die Testfragen und Runtime-Handoff-Tests erst in Abschnitt 11 erzeugt und ausgefuehrt werden.

## 11. Runtime-Tests ausfuehren

- [x] Backend starten.
  - Arbeitsverzeichnis:
    - `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents`
  - Befehl:
    - `python main.py`
  - Zwischenpruefung:
    - `GET /health` gibt `status=ok`.
  - Reparatur:
    - Port-Konflikt erkennen.
    - alternativen Port konfigurieren oder alten Prozess beenden.
  - Ergebnis 2026-07-08:
    - Backend gestartet auf `http://127.0.0.1:8787`.
    - Prozess: `python main.py`, PID `74816`.
    - Health-Check erfolgreich: `GET /health` -> `{"status":"ok"}`.
    - Logs:
      - `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/runtime_logs/backend_stdout.log`
      - `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/runtime_logs/backend_stderr.log`

- [x] `/setup` pro Case Study ausfuehren.
  - Request:
    - `{ "project_id": "<case_id>", "memory_mode": "agent_private_history" }`
  - Output:
    - `runtime_logs/setup_response.json`
  - Zwischenpruefung:
    - Session-ID vorhanden.
    - Agentenanzahl entspricht `agents.json`.
    - alle Agenten haben Position und Forward.
  - Ergebnis 2026-07-08:
    - `/setup` erfolgreich fuer alle drei Case Studies ausgefuehrt.
    - Setup-Antworten gespeichert:
      - `output/case_studies/steinpilz_brand_room/runtime_logs/setup_response.json`
      - `output/case_studies/classroom_dinosaur/runtime_logs/setup_response.json`
      - `output/case_studies/bestfit_career_fair/runtime_logs/setup_response.json`
    - Runtime-Setup-Reports gespeichert:
      - `output/case_studies/steinpilz_brand_room/validation/runtime_setup_validation.json`
      - `output/case_studies/classroom_dinosaur/validation/runtime_setup_validation.json`
      - `output/case_studies/bestfit_career_fair/validation/runtime_setup_validation.json`
    - Zwischenpruefung erfolgreich:
      - `steinpilz_brand_room`: Session-ID vorhanden, 6/6 Agenten, 6/6 mit Position und Forward.
      - `classroom_dinosaur`: Session-ID vorhanden, 4/4 Agenten, 4/4 mit Position und Forward.
      - `bestfit_career_fair`: Session-ID vorhanden, 5/5 Agenten, 5/5 mit Position und Forward.
      - Runtime-Logevents schema- und trace-gueltig; je Case mindestens ein `backend_setup_completed` Event mit `status=success`.
      - Abhaengige Batch-Metriken erneut ausgefuehrt; Aggregate Report weiterhin `success_count=3`, `failure_count=0`.

- [x] Testfragen generieren.
  - Deterministisch:
    - pro semantischer Zone eine Frage.
    - pro Agent eine Zuständigkeitsfrage.
    - mindestens eine Handoff-Frage.
  - Optional LLM:
    - `evaluation_questions_v1` erzeugt natuerliche Besucherfragen.
  - Output:
    - `validation/evaluation_questions.json`
  - Ergebnis 2026-07-08:
    - Deterministischer Generator implementiert: `tools/case_study_pipeline/evaluation_questions.py`.
    - Optionale LLM-Promptvorlage vorbereitet, aber nicht aufgerufen: `tools/case_study_pipeline/prompts/evaluation_questions_v1.md`.
    - Batch-Runner integriert `evaluation_questions` nach `handoff_metrics`.
    - Zwischenpruefung erfolgreich:
      - `python -m py_compile` fuer Generator und Batch-Runner erfolgreich.
      - `git diff --check` erfolgreich.
      - alle drei Case Studies mit `evaluation_questions: success`.
      - Aggregate Report steht auf `stage=evaluation_questions`, `success_count=3`, `failure_count=0`.
    - Messergebnisse:
      - `steinpilz_brand_room`: 29 Fragen = 8 Zonenfragen, 6 Agentenfragen, 15 Handoff-Fragen; Coverage jeweils 1.0.
      - `classroom_dinosaur`: 14 Fragen = 4 Zonenfragen, 4 Agentenfragen, 6 Handoff-Fragen; Coverage jeweils 1.0.
      - `bestfit_career_fair`: 23 Fragen = 6 Zonenfragen, 5 Agentenfragen, 12 Handoff-Fragen; Coverage jeweils 1.0.
    - Hinweis:
      - Keine API-Token verbraucht; die LLM-Umschreibung bleibt optional fuer spaetere natuerlichere Besucherformulierungen.

- [x] Chat-Tests ausfuehren.
  - Fuer jede Frage:
    - aktiven Startagenten setzen.
    - `POST /chat` ausfuehren.
    - Antwort und Events loggen.
  - Zwischenpruefung:
    - HTTP 200.
    - mindestens ein `say`-Event.
    - Antwort nicht leer.
    - `active_agent_id` existiert.
  - Ergebnis 2026-07-08:
    - Chat-Test-Runner implementiert: `tools/case_study_pipeline/chat_tests.py`.
    - Batch-Runner integriert Runtime-Chat-Tests hinter explizitem `--run-runtime`, damit normale Batchlaeufe keine API-Tokens verbrauchen.
    - Output pro Case:
      - kompakter Report: `validation/chat_test_results.json`
      - rohe Backend-Antworten: `runtime_logs/chat_responses.json`
    - Ausfuehrung:
      - Fragen wurden pro Test in isolierten Sessions ausgefuehrt, damit keine vorherige Antwort die naechste Frage beeinflusst.
      - `classroom_dinosaur`: 14/14 erfolgreich, HTTP-200-Coverage 1.0, `say`-Coverage 1.0, nichtleere Antworten 1.0, beobachtete Handoffs 6/6.
      - `bestfit_career_fair`: 23/23 erfolgreich, HTTP-200-Coverage 1.0, `say`-Coverage 1.0, nichtleere Antworten 1.0, beobachtete Handoffs 12/12.
      - `steinpilz_brand_room`: 29/29 erfolgreich, HTTP-200-Coverage 1.0, `say`-Coverage 1.0, nichtleere Antworten 1.0, beobachtete Handoffs 15/15.
    - Folgepruefung:
      - Handoff-Metriken nach den Chat-Tests erneut berechnet.
      - `handoff_decision_accuracy` ist fuer alle drei Cases 1.0.
      - Aggregate Report steht auf `stage=chat_tests`, `success_count=3`, `failure_count=0`.
    - Hinweis:
      - Dieser Schritt hat echte `/chat`-LLM-Aufrufe ausgefuehrt; die deterministic/offline Stages wurden vorher abgeschlossen.

- [x] Handoff-Test ausfuehren.
  - Beispiel:
    - Start bei Markenbotschafterin.
    - Frage zur Herstellung -> erwarteter Zielagent: Kaesemeister.
  - Zwischenpruefung:
    - Handoff vorhanden, wenn fachlich erwartet.
    - Zielagent passt zur Handoff-Matrix.
  - Reparaturschleife:
    - Agentenpersona/Handoff-Regel schaerfen.
    - Wissenstags korrigieren.
    - Test erneut ausfuehren.
  - Ergebnis 2026-07-08:
    - Handoff-Test-Validator implementiert: `tools/case_study_pipeline/handoff_tests.py`.
    - Batch-Runner integriert `handoff_tests` nach `chat_tests` innerhalb der expliziten Runtime-Stufe.
    - Output pro Case:
      - `validation/handoff_test_results.json`
    - Auswertung:
      - Keine neuen `/chat`-Aufrufe; der Schritt wertet die bereits ausgefuehrten Runtime-Chat-Tests aus.
      - `steinpilz_brand_room`: 15/15 Handoff-Tests bestanden, deklarierte Pair-Coverage 1.0, beobachtete Pair-Coverage 1.0.
      - `classroom_dinosaur`: 6/6 Handoff-Tests bestanden, deklarierte Pair-Coverage 1.0, beobachtete Pair-Coverage 1.0.
      - `bestfit_career_fair`: 12/12 Handoff-Tests bestanden, deklarierte Pair-Coverage 1.0, beobachtete Pair-Coverage 1.0.
    - Folgepruefung:
      - Handoff-Metriken deduplizieren jetzt `handoff_test_results.json` und `chat_test_results.json` nach `question_id`.
      - `handoff_decision_accuracy` bleibt fuer alle drei Cases 1.0.
      - Aggregate Report steht auf `stage=handoff_tests`, `success_count=3`, `failure_count=0`.

- [x] Antwort-Grounding pruefen.
  - Deterministisch:
    - Antwort muss mindestens auf Agent-KnowledgeTags und Projektkontext zurueckfuehrbar sein.
  - Optional LLM-Judge:
    - Bewertet auf Skala 0..2:
      - raumbezogen
      - korrekt gegen MLDS-Kontext
      - keine offensichtliche Halluzination
      - Handoff fachlich plausibel
  - Zwischenpruefung:
    - LLM-Judge nur als sekundäre Evidenz, nicht als einzige Wahrheit.
  - Ergebnis 2026-07-08:
    - Deterministischer Grounding-Validator implementiert: `tools/case_study_pipeline/answer_grounding.py`.
    - Optionale LLM-Judge-Promptvorlage vorbereitet, aber nicht aufgerufen: `tools/case_study_pipeline/prompts/answer_grounding_judge_v1.md`.
    - Batch-Runner integriert `answer_grounding` nach `handoff_tests` innerhalb der expliziten Runtime-Stufe.
    - Output pro Case:
      - `validation/answer_grounding_results.json`
    - Methode:
      - Abgleich der Antworttexte gegen response-agent-spezifische Knowledge-Tags, Expertise, KB-Eintraege, erwartete Zonen, erwartete Objekte und Projektkontext.
      - Deutsche Antworten werden ueber normalisierte Tokens und eine kleine domaenenspezifische Aliasliste auf englische MLDS-Begriffe gemappt.
      - LLM-Judge wurde nicht verwendet; `llm_judge_used=false`.
    - Messergebnisse:
      - `steinpilz_brand_room`: 29/29 Antworten grounded, Agent-Grounding-Coverage 1.0, Kontext-Grounding-Coverage 1.0.
      - `classroom_dinosaur`: 14/14 Antworten grounded, Agent-Grounding-Coverage 1.0, Kontext-Grounding-Coverage 1.0.
      - `bestfit_career_fair`: 23/23 Antworten grounded, Agent-Grounding-Coverage 1.0, Kontext-Grounding-Coverage 1.0.
    - Zwischenpruefung erfolgreich:
      - `python -m py_compile` fuer Validator und Batch-Runner erfolgreich.
      - `git diff --check` erfolgreich.
      - Aggregate Report steht auf `stage=answer_grounding`, `success_count=3`, `failure_count=0`.

## 12. Batch-Validierung ueber mehrere MLDS-Domaenen

- [x] Batch-Runner implementieren.
  - Pfad:
    - `tools/case_study_pipeline/run_batch_case_study.py`
  - CLI:
    - `--inputs <glob-or-list>`
    - `--out-root output/case_studies`
    - `--run-llm`
    - `--run-runtime`
    - `--max-repair-attempts 3`
  - Ergebnis 2026-07-08:
    - Batch-Runner ist implementiert und fuehrt die modularen Stages ueber eine oder mehrere MLDS-Dateien aus.
    - CLI verfuegbar:
      - `--inputs [INPUTS ...]`
      - `--input-glob INPUT_GLOB`
      - `--out-root OUT_ROOT`
      - `--run-llm`
      - `--run-runtime`
      - `--max-repair-attempts MAX_REPAIR_ATTEMPTS`
      - `--model MODEL`
      - `--force-llm`
      - `--backend-config BACKEND_CONFIG`
    - `--run-runtime` fuehrt explizit Backend-Chat-, Handoff- und Answer-Grounding-Checks aus; ohne diesen Schalter werden keine Runtime-Chat-Aufrufe gestartet.
    - Zwischenpruefung erfolgreich:
      - `python -m py_compile tools/case_study_pipeline/run_batch_case_study.py`
      - `python -m tools.case_study_pipeline.run_batch_case_study --help`
      - tokenfreier Smoke-Test mit separatem Output: `python -m tools.case_study_pipeline.run_batch_case_study --inputs InteractivAgents/InteractiveAgents2/Assets/Scripting/KlassenraumMLDS.json --out-root output/case_study_batch_runner_smoke`
      - Smoke-Aggregate: `stage=mlds_ingestion`, `success_count=1`, `failure_count=0`.
      - Haupt-Aggregate bleibt unveraendert auf `stage=answer_grounding`, `success_count=3`, `failure_count=0`.

- [x] Alle Stages pro MLDS-Datei ausfuehren.
  - Zwischenpruefung:
    - jeder Case hat Stage-Manifest.
    - jeder Case hat FunctionalMLDS-Instanz.
    - jeder Case hat Validierungsreport.
  - Ergebnis 2026-07-08:
    - Stage-Completion-Validator implementiert: `tools/case_study_pipeline/stage_completion.py`.
    - Batch-Runner integriert `stage_completion` nach `answer_grounding`.
    - Output:
      - pro Case: `validation/stage_completion_report.json`
      - uebergreifend: `output/case_studies/stage_completion_report.json`
    - Zwischenpruefung erfolgreich:
      - `python -m py_compile` fuer Validator und Batch-Runner erfolgreich.
      - `git diff --check` erfolgreich.
      - jeder Case hat `stage_manifest.json`.
      - jeder Case hat `functionalmlds/functionalmlds.instance.generated.json`.
      - jeder Case hat alle 16 geforderten Validierungsreports mit `status=valid`.
    - Messergebnisse:
      - `steinpilz_brand_room`: 18/18 Stages erfolgreich, 16/16 Validierungsreports gueltig, Completion-Ratio 1.0.
      - `classroom_dinosaur`: 18/18 Stages erfolgreich, 16/16 Validierungsreports gueltig, Completion-Ratio 1.0.
      - `bestfit_career_fair`: 18/18 Stages erfolgreich, 16/16 Validierungsreports gueltig, Completion-Ratio 1.0.
      - Aggregate Report steht auf `stage=stage_completion`, `success_count=3`, `failure_count=0`.

- [x] Cross-Case-Metriken berechnen.
  - Output:
    - `output/case_studies/aggregate_report.json`
    - `output/case_studies/aggregate_report.md`
  - Metriken:
    - Durchschnittliche Trace-Coverage.
    - Fehler je Stage.
    - Reparaturversuche je Stage.
    - Handoff-Genauigkeit je Domaene.
    - Objektgruppen-Abdeckung je Domaene.
  - Ergebnis 2026-07-08:
    - Cross-Case-Metrikmodul implementiert: `tools/case_study_pipeline/cross_case_metrics.py`.
    - Batch-Runner integriert `cross_case_metrics` nach `stage_completion`.
    - Outputs erzeugt:
      - `output/case_studies/aggregate_report.json`
      - `output/case_studies/aggregate_report.md`
    - Metriken:
      - Case Count: 3.
      - Durchschnittliche Trace-Coverage: 0.847222.
      - Durchschnittliche Requirement-to-Validation-Coverage: 1.0.
      - Durchschnittliche RuntimeAction-to-Log-Coverage: 0.25.
      - Durchschnittliche Handoff-Genauigkeit: 1.0.
      - Durchschnittliche Objektgruppen-Abdeckung: 1.0.
      - Durchschnittliches Antwort-Grounding: 1.0.
      - Durchschnittliche Stage-Completion-Ratio: 1.0.
      - Chat-Tests: 66/66 erfolgreich.
      - Handoff-Decision-Tests: 66.
    - Domaenenmetriken:
      - `Food Industry Trade Fair`: Handoff-Genauigkeit 1.0, Objektgruppen-Abdeckung 9/9.
      - `education`: Handoff-Genauigkeit 1.0, Objektgruppen-Abdeckung 5/5.
      - `Career Fair / Recruiting Event`: Handoff-Genauigkeit 1.0, Objektgruppen-Abdeckung 12/12.
    - Stage-Fehler und Reparaturversuche:
      - Alle ausgewerteten Stages in allen drei Cases mit `success`.
      - Fehler je Stage: 0.
      - Traceability-Metriken enthalten 6 Warnungen insgesamt, weil ActorIntent-Schritte absichtlich keine technische Capability haben und RuntimeAction-to-Log nur runtime-beobachtbare Aktionen abdeckt.
      - Reparatur-/LLM-Versuche aus Manifesten aggregiert: `scene_semantics` 2, `agent_roles` 3, `knowledge_synthesis` 3; deterministische Stages 0.
    - Zwischenpruefung erfolgreich:
      - `python -m py_compile` fuer Cross-Case-Modul und Batch-Runner erfolgreich.
      - `git diff --check` erfolgreich.
      - Aggregate Report steht auf `stage=cross_case_metrics`, `success_count=3`, `failure_count=0`.

- [x] Generalisierbarkeit beurteilen.
  - Frage:
    - Funktioniert dieselbe Pipeline fuer Food/Brand, Education und Career Fair ohne Spezialcode?
  - Zwischenpruefung:
    - Domaenenspezifische Begriffe duerfen in Daten/Prompts liegen, nicht in Pipeline-Code.
  - Umsetzung:
    - Domaenen- und Case-spezifische Begriffe aus Python-Code ausgelagert:
      - `tools/case_study_pipeline/config/case_aliases.json`
      - `tools/case_study_pipeline/config/default_inputs.json`
      - `tools/case_study_pipeline/config/answer_grounding_aliases.json`
    - Automatischer Generalisierbarkeitscheck implementiert:
      - Modul: `tools/case_study_pipeline/generalizability_assessment.py`
      - JSON-Report: `output/case_studies/generalizability_assessment.json`
      - Markdown-Report: `output/case_studies/generalizability_assessment.md`
    - Batch-Runner integriert `generalizability_assessment` nach `cross_case_metrics`.
  - Ergebnis:
    - `multi_domain_corpus`: bestanden, 3 Cases / 3 Domaenen.
    - `same_pipeline_stages`: bestanden, alle Cases nutzen dasselbe Stage-Set.
    - `no_failed_cases`: bestanden, `success_count=3`, `failure_count=0`.
    - `domain_terms_externalized`: bestanden, 25 Python-Dateien gescannt, 0 Treffer fuer konfigurierte Case-/Domaenenterme.
    - `runtime_behavior_cross_domain`: bestanden, Handoff-Genauigkeit 1.0, Answer-Grounding 1.0, Chat-Tests 66/66.
    - Generalizability Score: 1.0.
  - Reparaturschleife:
    - Erster Checklauf war ungueltig, weil die Wortliste zu breit war und generische Pipelinebegriffe wie `event`, `floor`, `agents` als Domaenenterme zaehlte.
    - Scanner auf echte Case-/Domaenenterme beschraenkt und Stopliste fuer technische Pipelinebegriffe ergaenzt.
  - Zwischenpruefung erfolgreich:
    - `python -m py_compile` fuer Generalisierbarkeitsmodul, Batch-Runner, Answer-Grounding und MLDS-Ingestion erfolgreich.
    - Einzel-MLDS-Smoke-Test nach Auslagerung der Konfiguration erfolgreich:
      - `classroom_dinosaur: success (0 errors, 0 warnings)`.
    - Generalisierbarkeitsreport steht auf `status=valid`, `passed_check_count=5/5`.

## 13. Wissenschaftliche Auswertung

- [x] Forschungsfragen formulieren.
  - RQ1: Kann FunctionalMLDS eine MLDS-zu-Agenten-Transformation vollstaendig tracebar modellieren?
  - RQ2: Erhoeht FunctionalMLDS die Pruefbarkeit gegenueber direkter MLDS-zu-Agenten-Generierung?
  - RQ3: Bleibt die Pipeline ueber unterschiedliche MLDS-Domaenen hinweg anwendbar?
  - Umsetzung:
    - Paper-Baustein erzeugt:
      - `output/case_studies/paper_artifacts/research_questions.md`
    - Jede Forschungsfrage wurde operationalisiert:
      - Motivation.
      - messbare Pruefkriterien.
      - Primaere Evidenz aus vorhandenen Reports.
      - Interpretation fuer die spaetere Results-Section.
  - Ergebnis:
    - RQ1 fokussiert die tracebare Modellierbarkeit von MLDS-Rauminformationen zu interaktiven Agenten.
    - RQ2 fokussiert die gesteigerte Pruefbarkeit gegenueber direkter Artefaktgenerierung.
    - RQ3 fokussiert die domaenenuebergreifende Anwendbarkeit ohne Spezialcode.
  - Evidenzanker:
    - RQ1: `average_trace_coverage=0.847222`, `average_requirement_to_validation_coverage=1.0`, `average_object_group_coverage=1.0`, Schema-/Invariantenvalidierung 3/3.
    - RQ2: `average_stage_completion_ratio=1.0`, Chat-Tests 66/66, Handoff-Genauigkeit 1.0, Answer-Grounding 1.0, Stage-Fehler 0.
    - RQ3: Generalizability Score 1.0, 3 Cases / 3 Domaenen, 25 Python-Dateien mit 0 Domaenenterm-Treffern.
  - Zwischenpruefung:
    - Alle RQs sind empirisch pruefbar und verweisen auf bereits erzeugte Pipeline-Artefakte.
    - Keine RQ setzt eine noch nicht implementierte Metrik zwingend voraus; die Baseline wird im naechsten Task separat definiert.

- [x] Baseline definieren.
  - Baseline A:
    - bestehender `ArrowProjectWizard` erzeugt Agentenprojekt ohne FunctionalMLDS-Instanz.
  - Treatment B:
    - MLDS -> FunctionalMLDS -> Agentenprojekt -> Runtime-Validierung.
  - Umsetzung:
    - Paper-Baustein erzeugt:
      - `output/case_studies/paper_artifacts/baseline_definition.md`
    - Maschinenlesbare Definition erzeugt:
      - `output/case_studies/paper_artifacts/baseline_definition.json`
  - Baseline A konkretisiert:
    - Reales Entry Point Artefakt: `InteractivAgents/InteractiveAgents2/Assets/Scripting/ArrowProjectWizard.cs`.
    - Reale Backend-Endpunkte: `/projects/arrow/analyze`, `/projects/arrow/chat`, `/projects/arrow/commit`.
    - Reale Ausgaben: `project.json`, `room_plan.json`, `agents.json`, projektlokale `kb/`-Eintraege und Placement Preview.
    - Vorhandene Checks: Structured Output Schema, Agent-/Voice-Normalisierung, Placement-Normalisierung, Backend-Requestvalidierung.
  - Treatment B konkretisiert:
    - Entry Point: `tools/case_study_pipeline/run_batch_case_study.py`.
    - Zusatzausgaben: FunctionalMLDS-Instanz, Stage Manifest, Validierungsreports, Runtime Logs, Aggregate Reports, Paper-Artefakte.
  - Vergleichsgrenze:
    - Baseline A ist keine fehlerhafte Pipeline, sondern direkte Artefaktgenerierung.
    - Treatment B ist metamodel-vermittelte Artefaktgenerierung mit expliziter Trace-, Validierungs- und Reparaturstruktur.
  - Zwischenpruefung:
    - Baseline ist aus realem Code abgeleitet, nicht hypothetisch.
    - Baseline und Treatment nutzen dieselbe Zielklasse: Interactive-Agents-Projekt.
    - Vergleich vermeidet eine Strohpuppe: vorhandene Wizard-Safeguards werden explizit anerkannt.

- [x] Vergleichsmetriken definieren.
  - Traceability:
    - Baseline hat keine explizite Requirement-to-Runtime-Kette.
    - Treatment hat pruefbare Kette.
  - Consistency:
    - Anzahl ungueltiger Handoff-Ziele.
    - Anzahl fehlender Wissenstags.
    - Anzahl ungebundener Capabilities.
  - Maintainability:
    - Austausch einer RuntimeBinding ohne Scenario-Aenderung.
  - Umsetzung:
    - Paper-Baustein erzeugt:
      - `output/case_studies/paper_artifacts/comparison_metrics.md`
    - Maschinenlesbarer Metrikkatalog erzeugt:
      - `output/case_studies/paper_artifacts/comparison_metrics.json`
  - Definierte Metrikfamilien:
    - Traceability: M1 bis M4.
    - Consistency: M5 bis M8.
    - Runtime-Checkability: M9 bis M10.
    - Repairability: M11 bis M12.
    - Generalizability: M13 bis M14.
    - Maintainability: M15.
  - Aktuell gemessene Treatment-Werte:
    - M1 FunctionalMLDS-Instanz vorhanden: 1.0.
    - M2 Average Trace Coverage: 0.847222.
    - M3 Requirement-to-Validation Coverage: 1.0.
    - M4 Object-Group-to-Agent Grounding: 1.0.
    - M5 Schema-/Invariantenerfolg: 1.0.
    - M6 Invalid Handoff Target Count: 0.
    - M7 Missing Knowledge Tag Count: 0.
    - M8 Unbound Capability Count: 0.
    - M9 Handoff Decision Accuracy: 1.0.
    - M10 Answer Grounding Ratio: 1.0.
    - M11 Stage Completion Ratio: 1.0.
    - M12 Repair Attempt Count: 8.
    - M13 Generalizability Score: 1.0.
    - M14 Domain Term Externalization: 1.0.
    - M15 RuntimeBinding Substitution Locality: als gezieltes Folgeexperiment definiert.
  - Fairnessregel:
    - Direkt vergleichbare Metriken werden nach einem Baseline-Lauf fuer beide Pipelines berechnet.
    - Metamodell-Zusatzevidenz wird separat berichtet, wenn Baseline A den gemessenen Modellbegriff nicht als First-Class-Artefakt besitzt.
  - Zwischenpruefung:
    - Der Metrikkatalog erkennt vorhandene Baseline-Safeguards an und markiert fehlende Metamodellbegriffe als `explicit_absence`, nicht als Implementierungsfehler.
    - Keine Metrik vermischt visuelle Qualitaet, Editor-Usability oder subjektive Dialogqualitaet mit der wissenschaftlichen Modellvalidierung.

- [x] Paper-Artefakte erzeugen.
  - Tabellen:
    - Case-Korpus.
    - Metamodell-Coverage.
    - Invariantenverletzungen vor/nach Reparatur.
    - Runtime-Testresultate.
  - Figuren:
    - Pipeline-Architektur.
    - Trace-Kette fuer einen Beispielschritt.
    - Agentenplatzierung im Raum.
  - Beispiele:
    - MLDS-Objektgruppe -> Agentenrolle -> Wissenstag -> Capability -> RuntimeBinding -> Chat-Event.
  - Umsetzung:
    - Reproduzierbarer Generator implementiert:
      - `tools/case_study_pipeline/paper_artifacts.py`
    - Batch-Runner integriert Paper-Artefakte nach erfolgreichem Generalisierbarkeitscheck.
    - Manifest erzeugt und in `aggregate_report.json` referenziert:
      - `output/case_studies/paper_artifacts/paper_artifacts_manifest.json`
  - Tabellen erzeugt:
    - Case-Korpus:
      - `output/case_studies/paper_artifacts/tables/case_corpus.md`
      - `output/case_studies/paper_artifacts/tables/case_corpus.csv`
    - Metamodell-Coverage:
      - `output/case_studies/paper_artifacts/tables/metamodel_coverage.md`
      - `output/case_studies/paper_artifacts/tables/metamodel_coverage.csv`
    - Validierung/Reparatur:
      - `output/case_studies/paper_artifacts/tables/validation_repair.md`
      - `output/case_studies/paper_artifacts/tables/validation_repair.csv`
    - Runtime-Testresultate:
      - `output/case_studies/paper_artifacts/tables/runtime_test_results.md`
      - `output/case_studies/paper_artifacts/tables/runtime_test_results.csv`
  - Figuren erzeugt:
    - Pipeline-Architektur:
      - `output/case_studies/paper_artifacts/figures/pipeline_architecture.mmd`
    - Trace-Kette fuer einen Beispielschritt:
      - `output/case_studies/paper_artifacts/figures/trace_chain_example.mmd`
    - Agentenplatzierung im Raum:
      - `output/case_studies/paper_artifacts/figures/agent_placement_classroom_dinosaur.mmd`
  - Beispiel erzeugt:
    - `output/case_studies/paper_artifacts/examples/trace_chain_example.md`
  - Index erzeugt:
    - `output/case_studies/paper_artifacts/paper_artifacts_index.md`
  - Ergebnis:
    - 4 Tabellenfamilien, 3 Mermaid-Figuren, 1 Trace-Beispiel, 14 Output-Artefakte.
    - Manifeststatus `valid`, fehlende Outputs 0.
  - Hinweis zur Reparaturtabelle:
    - Exakte Vor-Reparatur-Fehlerzahlen liegen erst nach dem spaeteren Reparaturprotokoll-Task als JSONL vor.
    - Die Paper-Tabelle berichtet deshalb wissenschaftlich vorsichtig `pre_final_repair_attempts` und finale Schema-/Invariant-Fehler.
  - Zwischenpruefung:
    - `python -m py_compile` fuer Generator und Batch-Runner erfolgreich.
    - Manifest `output_count=14`, gelistete Dateien 14, fehlende Dateien 0.
    - `aggregate_report.json` steht auf `stage=paper_artifacts` und enthaelt den Paper-Artefakt-Manifestblock.

- [x] Threats to Validity dokumentieren.
  - Interne Validitaet:
    - LLM-Ausgaben variieren.
    - Prompt-Versionierung notwendig.
  - Externe Validitaet:
    - nur drei bis n MLDS-Domaenen.
    - Unity- und Backend-Prototypstatus.
  - Konstruktvaliditaet:
    - LLM-Judge nicht als alleinige Korrektheitsquelle.
    - Grounding-Metriken muessen mit deterministischen Checks kombiniert werden.
  - Umsetzung:
    - Paper-Baustein erzeugt:
      - `output/case_studies/paper_artifacts/threats_to_validity.md`
    - Maschinenlesbare Threat-Liste erzeugt:
      - `output/case_studies/paper_artifacts/threats_to_validity.json`
    - Paper-Artefakt-Index und Manifest ergaenzt.
    - `aggregate_report.json` enthaelt einen `threats_to_validity`-Block.
  - Dokumentierte Kategorien:
    - Internal Validity:
      - LLM-Varianz.
      - Reparaturschleifen als moegliche Verdeckung von Einzelschrittfehlern.
      - Backend-Runtime-State als Einflussfaktor.
    - External Validity:
      - aktueller Korpus mit 3 Domaenen.
      - Unity-/Python-Prototypstatus.
      - Fokus auf room-based agent interaction.
    - Construct Validity:
      - Trace-Coverage misst nicht automatisch semantische Qualitaet.
      - Answer-Grounding aktuell deterministisch, `llm_judge_used=false`.
      - RuntimeAction-to-Log-Coverage bewusst begrenzt.
    - Conclusion Validity:
      - Baseline A wurde noch nicht voll ueber denselben Korpus ausgefuehrt.
      - 66/66 Runtime-Tests sind Case-Study-Evidenz, keine statistische Populationsaussage.
  - Reporting-Regel:
    - Keine breite Aussage wie "FunctionalMLDS ist allgemein fuer industrielle Toolchains korrekt".
    - Verteidigbare Aussage: FunctionalMLDS macht die evaluierte MLDS-zu-Interactive-Agents-Pipeline fuer den drei-Domaenen-Korpus tracebar, pruefbar und reproduzierbar.
  - Zwischenpruefung:
    - Threats JSON parsebar und `status=valid`.
    - 11 Threat-Eintraege dokumentiert.
    - Paper-Artefakt-Manifest enthaelt jetzt `output_count=16` und `validity_artifact_count=2`.

## 14. Reparaturschleifen als Standardprozess

Jede Stage folgt diesem Muster:

```text
Run Stage
  -> Validate Output
    -> if valid: freeze output hash and continue
    -> if invalid and attempts < max:
         create repair prompt or deterministic repair
         rerun only this stage
       else:
         mark needs_manual_review
         continue only if downstream can tolerate missing output
```

- [x] Reparaturprotokoll schreiben.
  - Output:
    - `validation/repair_log.jsonl`
  - Pro Eintrag:
    - Stage
    - Fehler
    - Reparaturtyp
    - Versuch
    - Ergebnis
  - Umsetzung:
    - Generator implementiert:
      - `tools/case_study_pipeline/repair_log.py`
    - Pro Case erzeugt:
      - `output/case_studies/bestfit_career_fair/validation/repair_log.jsonl`
      - `output/case_studies/classroom_dinosaur/validation/repair_log.jsonl`
      - `output/case_studies/steinpilz_brand_room/validation/repair_log.jsonl`
    - Aggregierte Logs erzeugt:
      - `output/case_studies/repair_log.jsonl`
      - `output/case_studies/repair_log_summary.json`
    - Batch-Runner integriert Repair-Log-Erzeugung vor Paper-Artefakt-Generierung.
    - `aggregate_report.json` enthaelt einen `repair_log`-Block.
  - Ergebnis:
    - 12 Reparatur-/Generierungsprotokolleintraege.
    - 8 erfolgreiche LLM-Erstgenerierungen.
    - 0 echte LLM-Reparaturversuche nach invalidem Artefakt.
    - 1 deterministische Recovery (`steinpilz_brand_room`, `scene_semantics`).
    - 3 akzeptierte Traceability-Warnungen.
  - Korrektur vorheriger Interpretation:
    - `attempts_used=1` ist ein erfolgreicher Erstgenerierungsversuch, kein Reparaturversuch.
    - Vergleichsmetriken, Research-Questions-Evidenz und Paper-Tabelle `validation_repair` wurden entsprechend korrigiert.
  - Zwischenpruefung:
    - Repair-Log-Summary `status=valid`.
    - Alle drei per-Case `validation/repair_log.jsonl` vorhanden.
    - Paper-Reparaturtabelle trennt jetzt `llm_generation_attempts`, `llm_repair_attempts`, `deterministic_recoveries` und `accepted_warnings`.

- [x] LLM-Reparaturprompts trennen.
  - Beispiele:
    - `repair_invalid_object_refs_v1.md`
    - `repair_missing_capabilities_v1.md`
    - `repair_invalid_handoff_targets_v1.md`
  - Umsetzung:
    - Aktive Repair-Prompts ausgelagert:
      - `tools/case_study_pipeline/prompts/repair_invalid_object_refs_v1.md`
      - `tools/case_study_pipeline/prompts/repair_invalid_handoff_targets_v1.md`
      - `tools/case_study_pipeline/prompts/repair_missing_knowledge_entries_v1.md`
    - Vorbereiteter Capability-Repair-Prompt:
      - `tools/case_study_pipeline/prompts/repair_missing_capabilities_v1.md`
    - Aktive Stages nutzen Repair-Prompts nur noch ueber `repair_instruction = repair_prompt_text`:
      - `scene_semantics` -> `repair_invalid_object_refs_v1`
      - `agent_roles` -> `repair_invalid_handoff_targets_v1`
      - `knowledge_synthesis` -> `repair_missing_knowledge_entries_v1`
    - Stage-Manifeste neuer Laeufe protokollieren `repair_prompt_version`.
    - Repair-Log-Eintraege enthalten jetzt optional `repair_prompt_version`.
  - Paper-Artefakt:
    - Repair-Prompt-Register erzeugt:
      - `output/case_studies/paper_artifacts/repair_prompt_registry.md`
      - `output/case_studies/paper_artifacts/repair_prompt_registry.json`
    - Paper-Artefakt-Index und Manifest enthalten das Register.
  - Zwischenpruefung:
    - `python -m py_compile` fuer betroffene LLM-Stages, Batch-Runner, Repair-Log und Paper-Artefakt-Generator erfolgreich.
    - Suche bestaetigt: Reparaturtexte liegen in `tools/case_study_pipeline/prompts/repair_*_v1.md`; Code uebergibt nur noch den geladenen Prompttext.
    - Paper-Artefakt-Manifest steht auf `output_count=23`, `document_count=9`.

- [x] Deterministische Reparaturen priorisieren.
  - Beispiele:
    - IDs normalisieren.
    - fehlende Hashes nachtragen.
    - `tts_model=standard` normalisieren.
    - Agentenpositionen neu suchen.
  - LLM nur verwenden, wenn fachliche Semantik betroffen ist.
  - Umsetzung:
    - Deterministic-first Policy erstellt:
      - `tools/case_study_pipeline/config/deterministic_repair_policy.json`
    - Policy-Report-Generator implementiert:
      - `tools/case_study_pipeline/deterministic_repair_policy.py`
    - Report erzeugt:
      - `output/case_studies/deterministic_repair_policy_report.json`
      - `output/case_studies/paper_artifacts/deterministic_repair_policy_report.md`
    - Paper-Policy-Dokument erzeugt:
      - `output/case_studies/paper_artifacts/deterministic_repair_policy.md`
    - Batch-Runner integriert Policy-Report nach Repair-Log und vor Paper-Artefakten.
  - Priorisierte deterministische Regeln:
    - DR-001: IDs normalisieren.
    - DR-002: Manifest-Hashes neu berechnen.
    - DR-003: `tts_model=standard` deterministisch auf `gpt-4o-mini-tts` abbilden.
    - DR-004: Agentenpositionen geometrisch neu berechnen.
    - DR-005: vorhandene valide Artefakte ohne LLM wiederherstellen.
    - DR-006: deterministische Derived Artefacts/Reports regenerieren.
    - LR-001: LLM-Reparatur nur als semantische Eskalation.
  - Ergebnis:
    - 7 Policy-Regeln insgesamt.
    - 6 deterministische Regeln.
    - 1 LLM-Eskalationsregel.
    - Repair-Log-Evidence: 12 Eintraege, 8 LLM-Erstgenerierungen, 0 LLM-Reparaturversuche, 4 deterministische/akzeptierte Repair-Evidenzen.
    - `deterministic_first_policy_satisfied=true`.
  - Zwischenpruefung:
    - `python -m py_compile` fuer Policy-Generator, Paper-Artefakt-Generator und Batch-Runner erfolgreich.
    - Policy-Report `status=valid`.
    - Paper-Artefakt-Manifest enthaelt jetzt `output_count=25`, `document_count=11`.

## 15. Definition of Done fuer die Case Study

Die Case Study gilt als abgeschlossen, wenn fuer mindestens drei unterschiedliche MLDS-Dateien gilt:

- [x] FunctionalMLDS-Instanz vorhanden.
  - Gepruefte Cases:
    - `bestfit_career_fair`
    - `classroom_dinosaur`
    - `steinpilz_brand_room`
  - Evidenz:
    - Alle drei Dateien `functionalmlds/functionalmlds.instance.generated.json` vorhanden.
    - Alle drei Dateien parsebar.
    - Alle drei Instanzen mit `schema=functionalmlds_case_study`.
    - Alle drei Instanzen mit `metamodelVersion=v0.5`.
  - Mindeststruktur pro Case:
    - 6 Requirements.
    - 1 Use Case.
    - 9 Capabilities.
    - 9 RuntimeBindings.
    - 6 ValidationCases.
  - Zusaetzliche Paper-Evidenz:
    - `output/case_studies/paper_artifacts/tables/metamodel_coverage.md`
- [x] Interactive-Agents-Projekt materialisiert.
  - Gepruefte Cases:
    - `bestfit_career_fair`
    - `classroom_dinosaur`
    - `steinpilz_brand_room`
  - Zielstruktur:
    - Backend-Projekte liegen unter `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/<case_id>/`.
    - Pro Case vorhanden: `project.json`, `room_plan.json`, `agents.json`, `trace_map.json`.
    - Pro Case vorhandene Knowledge-Base-Dateien im materialisierten Backend-Projekt und als Ausgangsartefakt unter `output/case_studies/<case_id>/interactive_agents_project/kb/`.
  - Validierung:
    - `validation/project_materialization_validation.json` meldet fuer alle drei Cases `status=valid`.
    - Fehler: 0 fuer alle drei Cases.
    - Warnungen: 0 fuer alle drei Cases.
  - Materialisierte Agenten:
    - `bestfit_career_fair`: 5 Agenten, 15 Knowledge-Base-Dateien.
    - `classroom_dinosaur`: 4 Agenten, 8 Knowledge-Base-Dateien.
    - `steinpilz_brand_room`: 6 Agenten, 18 Knowledge-Base-Dateien.
  - Trace-Map-Evidenz pro Case:
    - 12 ScenarioSteps.
    - 12 RuntimeActions.
    - 6 ValidationCases.
- [x] Backend-`/setup` erfolgreich.
  - Gepruefte Cases:
    - `bestfit_career_fair`
    - `classroom_dinosaur`
    - `steinpilz_brand_room`
  - Endpoint:
    - `POST /setup` wird mit `project_id=<case_id>` und `memory_mode` aufgerufen.
    - Das Backend laedt dadurch `room_plan.json`, `agents.json` und die projektbezogene Knowledge Base aus `InteractiveAgents/projects/<case_id>/`.
  - Gespeicherte Runtime-Evidenz:
    - `runtime_logs/setup_response.json` pro Case vorhanden.
    - Setup-Antwort enthaelt pro Case eine `session_id`.
    - Setup-Antwort enthaelt pro Case die erwartete Agentenzahl.
  - Validierung:
    - `validation/runtime_setup_validation.json` meldet fuer alle drei Cases `status=valid`.
    - Fehler: 0 fuer alle drei Cases.
    - Warnungen: 0 fuer alle drei Cases.
    - Runtime-Event-Validierungsfehler: 0 fuer alle drei Cases.
  - Agenten aus Setup-Antwort:
    - `bestfit_career_fair`: 5/5 Agenten mit Position und Blickrichtung.
    - `classroom_dinosaur`: 4/4 Agenten mit Position und Blickrichtung.
    - `steinpilz_brand_room`: 6/6 Agenten mit Position und Blickrichtung.
  - Runtime-Log-Evidenz:
    - `runtime_logs/events.jsonl` enthaelt `backend_setup_completed`-Events fuer alle drei Cases.
- [x] mindestens fuenf Chat-Testfragen erfolgreich.
  - Gepruefte Cases:
    - `bestfit_career_fair`
    - `classroom_dinosaur`
    - `steinpilz_brand_room`
  - Validierungsartefakte:
    - `validation/chat_test_results.json` pro Case vorhanden.
    - `runtime_logs/chat_responses.json` pro Case vorhanden.
    - Rohantwortanzahl entspricht pro Case der Anzahl ausgefuehrter Chat-Tests.
  - Ergebnis pro Case:
    - `bestfit_career_fair`: 23/23 Chat-Tests erfolgreich, 23 HTTP-200-Antworten, 0 Fehler, 0 Warnungen.
    - `classroom_dinosaur`: 14/14 Chat-Tests erfolgreich, 14 HTTP-200-Antworten, 0 Fehler, 0 Warnungen.
    - `steinpilz_brand_room`: 29/29 Chat-Tests erfolgreich, 29 HTTP-200-Antworten, 0 Fehler, 0 Warnungen.
  - Gesamt:
    - 66/66 Chat-Tests erfolgreich.
    - Say-Event-Coverage: 1.0 fuer alle drei Cases.
    - Nonempty-Answer-Coverage: 1.0 fuer alle drei Cases.
    - Tests wurden mit isolierter Session pro Frage ausgefuehrt.
- [x] mindestens ein erwarteter Handoff-Test erfolgreich oder begruendet nicht anwendbar.
  - Gepruefte Cases:
    - `bestfit_career_fair`
    - `classroom_dinosaur`
    - `steinpilz_brand_room`
  - Validierungsartefakte:
    - `validation/handoff_test_results.json` pro Case vorhanden.
    - `validation/handoff_metrics.json` pro Case vorhanden.
    - `intermediate/handoff_matrix.json` pro Case vorhanden.
  - Ergebnis pro Case:
    - `bestfit_career_fair`: 12/12 Handoff-Tests bestanden, deklarierte Paarabdeckung 1.0, beobachtete Paarabdeckung 1.0.
    - `classroom_dinosaur`: 6/6 Handoff-Tests bestanden, deklarierte Paarabdeckung 1.0, beobachtete Paarabdeckung 1.0.
    - `steinpilz_brand_room`: 15/15 Handoff-Tests bestanden, deklarierte Paarabdeckung 1.0, beobachtete Paarabdeckung 1.0.
  - Gesamt:
    - 33/33 Handoff-Tests bestanden.
    - 33/33 beobachtete Handoffs sind deklarierte Handoff-Paare.
    - Handoff-Test-Success-Rate: 1.0 fuer alle drei Cases.
    - Handoff-Decision-Accuracy: 1.0 fuer alle drei Cases.
  - Strukturpruefung:
    - keine Selbst-Handoffs.
    - keine duplizierten Handoff-Paare.
    - keine fehlenden Matrix-Paare.
    - keine zusaetzlichen Matrix-Paare.
    - keine ungueltigen beobachteten Handoff-Ziele.
  - Beispiel-Evidenz:
    - `reception_agent -> benefits_expert` in `bestfit_career_fair`: Ziel beobachtet, `response_active_agent_id=benefits_expert`, zwei Say-Events.
    - `teacher_agent -> reading_area_guide` in `classroom_dinosaur`: Ziel beobachtet, `response_active_agent_id=reading_area_guide`, zwei Say-Events.
    - `reception_agent -> product_specialist_agent` in `steinpilz_brand_room`: Ziel beobachtet, `response_active_agent_id=product_specialist_agent`, zwei Say-Events.
- [x] alle FunctionalMLDS-Kerninvarianten erfuellt.
  - Gepruefte Cases:
    - `bestfit_career_fair`
    - `classroom_dinosaur`
    - `steinpilz_brand_room`
  - Validierungsartefakt:
    - `validation/functionalmlds_invariants_validation.json` pro Case vorhanden.
  - Ergebnis pro Case:
    - `bestfit_career_fair`: 7/7 Invarianten bestanden, 48 gepruefte Elemente, 0 Fehler, 0 Warnungen.
    - `classroom_dinosaur`: 7/7 Invarianten bestanden, 48 gepruefte Elemente, 0 Fehler, 0 Warnungen.
    - `steinpilz_brand_room`: 7/7 Invarianten bestanden, 48 gepruefte Elemente, 0 Fehler, 0 Warnungen.
  - Gepruefte Kerninvarianten:
    - jeder UseCase besitzt genau ein Main Scenario.
    - jedes Scenario besitzt mindestens einen ScenarioStep.
    - ScenarioSteps referenzieren keine RuntimeActions direkt.
    - jeder CapabilityUse referenziert genau eine existierende Capability.
    - jede Capability besitzt mindestens einen Effect.
    - jedes RuntimeBinding besitzt mindestens eine RuntimeAction.
    - jeder ValidationCase referenziert mindestens ein pruefbares StateAssertion- oder RuntimeBinding-Element.
  - Strukturumfang pro Case:
    - 1 UseCase.
    - 1 Scenario.
    - 12 ScenarioSteps.
    - 9 Capabilities.
    - 10 CapabilityUses.
    - 9 RuntimeBindings.
    - 6 ValidationCases.
- [x] Trace-Coverage-Report vorhanden.
  - Gepruefte Cases:
    - `bestfit_career_fair`
    - `classroom_dinosaur`
    - `steinpilz_brand_room`
  - Validierungsartefakt:
    - `validation/traceability_metrics.json` pro Case vorhanden.
    - `stage_manifest.json` enthaelt fuer alle drei Cases `traceability_metrics: success`.
  - Reportstatus:
    - alle drei Reports mit `status=valid`.
    - Fehler: 0 fuer alle drei Cases.
    - Warnungen: 2 pro Case; beide Warnungen sind als Teilabdeckung dokumentiert und fachlich begruendet.
  - Voll abgedeckte Trace-Ketten pro Case:
    - Requirement-to-Validation-Coverage: 6/6 = 1.0.
    - Capability-to-RuntimeBinding-Coverage: 9/9 = 1.0.
    - Agent-to-KnowledgeTag-Coverage: 1.0.
    - ObjectGroup-to-AgentRole-Grounding: 1.0.
  - Dokumentierte Teilabdeckung pro Case:
    - ScenarioStep-to-Capability-Coverage: 10/12 = 0.833333.
    - Die zwei offenen ScenarioSteps sind `actorIntent`-Schritte und daher bewusst nicht direkt als technische Capability operationalisiert.
    - RuntimeAction-to-Log-Coverage: 3/12 = 0.25.
    - Im Backend-Runtime-Log beobachtet sind die drei live ausgefuehrten Backend-Aktionen `BACKEND-SETUP`, `BACKEND-CHAT` und `BACKEND-CHAT-HANDOFF`; die uebrigen RuntimeActions beschreiben Offline-Pipeline-Schritte.
  - Durchschnittliche Trace-Coverage:
    - `bestfit_career_fair`: 0.847222.
    - `classroom_dinosaur`: 0.847222.
    - `steinpilz_brand_room`: 0.847222.
- [x] Aggregate-Report ueber alle Cases vorhanden.
  - Artefakte:
    - `output/case_studies/aggregate_report.json` vorhanden.
    - `output/case_studies/aggregate_report.md` vorhanden.
  - Cross-Case-Report:
    - `cross_case_metrics.status=valid`.
    - Fehler: 0.
    - Warnungen: 0.
    - Case Count: 3.
    - Cases: `bestfit_career_fair`, `classroom_dinosaur`, `steinpilz_brand_room`.
  - Aggregierte Kernmetriken:
    - Average Trace Coverage: 0.847222.
    - Average Requirement-to-Validation-Coverage: 1.0.
    - Average RuntimeAction-to-Log-Coverage: 0.25.
    - Average Handoff Accuracy: 1.0.
    - Average Object-Group Coverage: 1.0.
    - Average Answer-Grounding Ratio: 1.0.
    - Average Stage-Completion Ratio: 1.0.
    - Chat Tests: 66/66 erfolgreich.
    - Handoff Decision Tests: 66.
  - Per-Case-Metriken im Markdown-Report:
    - `bestfit_career_fair`: Trace 0.847222, Runtime 0.25, Handoff 1.0, Object-Group 1.0, Grounding 1.0, Completion 1.0.
    - `classroom_dinosaur`: Trace 0.847222, Runtime 0.25, Handoff 1.0, Object-Group 1.0, Grounding 1.0, Completion 1.0.
    - `steinpilz_brand_room`: Trace 0.847222, Runtime 0.25, Handoff 1.0, Object-Group 1.0, Grounding 1.0, Completion 1.0.
  - Stage-Summary:
    - `runtime_setup`: 3/3 success, 0 Fehler, 0 Warnungen.
    - `chat_tests`: 3/3 success, 0 Fehler, 0 Warnungen.
    - `handoff_tests`: 3/3 success, 0 Fehler, 0 Warnungen.
    - `functionalmlds_invariants`: 3/3 success, 0 Fehler, 0 Warnungen.
    - `traceability_metrics`: 3/3 success, 0 Fehler, 6 dokumentierte Warnungen zur fachlich begruendeten Teilabdeckung.
    - `stage_completion`: 3/3 success, 0 Fehler, 0 Warnungen.
- [x] Paper-Tabellen und ein Beispiel-Trace vorhanden.
  - Manifest:
    - `output/case_studies/paper_artifacts/paper_artifacts_manifest.json` vorhanden.
    - `schema=functionalmlds_paper_artifacts`.
    - `status=valid`.
    - Fehler: 0.
    - Warnungen: 0.
    - Outputs: 25/25 vorhanden.
  - Tabellen:
    - `tables/case_corpus.md` und `.csv` vorhanden.
    - `tables/metamodel_coverage.md` und `.csv` vorhanden.
    - `tables/validation_repair.md` und `.csv` vorhanden.
    - `tables/runtime_test_results.md` und `.csv` vorhanden.
    - Manifest-Metrik: `table_count=4`.
  - Figuren:
    - `figures/pipeline_architecture.mmd` vorhanden.
    - `figures/trace_chain_example.mmd` vorhanden.
    - `figures/agent_placement_classroom_dinosaur.mmd` vorhanden.
    - Manifest-Metrik: `figure_count=3`.
  - Beispiel-Trace:
    - `examples/trace_chain_example.md` vorhanden.
    - Manifest-Metrik: `example_count=1`.
    - Beispiel verbindet `classroom_dinosaur` von `instruction_zone` ueber `teacher_agent`, Knowledge-Tag, Capability, RuntimeBinding und RuntimeAction bis zum Chat-Ereignis `EQ-CLASSROOM_DINOSAUR-ZONE-INSTRUCTION_ZONE`.
  - Weitere Paper-Unterlagen:
    - `paper_artifacts_index.md` vorhanden.
    - `research_questions.md` vorhanden.
    - `baseline_definition.md`/`.json` vorhanden.
    - `comparison_metrics.md`/`.json` vorhanden.
    - `repair_prompt_registry.md`/`.json` vorhanden.
    - `deterministic_repair_policy.md` und `deterministic_repair_policy_report.md` vorhanden.
    - `threats_to_validity.md`/`.json` vorhanden.
    - Manifest-Metrik: `document_count=11`.
- [x] kein API-Key in Artefakten, Logs oder Git-Status.
  - Artefakt-/Log-Suche:
    - Suchmuster fuer OpenAI-Key-Formate in `output`, `tools` und `archive` ausgefuehrt.
    - Trefferanzahl: 0.
    - Damit kein Key in Case-Study-Artefakten, Runtime-Logs, Paper-Artefakten, Metamodell-Artefakten, Pipeline-Tools oder textuellen Archivartefakten gefunden.
  - Git-Status-Suche:
    - normale `git status --short --untracked-files=all`-Ausgabe gegen dasselbe Secret-Muster geprueft.
    - `git_status_secret_pattern_present=False`.
    - `git_status_mentions_config_json=False`.
  - Lokale Runtime-Config:
    - lokale `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/config.json` enthaelt den Key erwartungsgemaess als lokale Runtime-Konfiguration.
    - Datei ist nicht getrackt.
    - Datei wird durch `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/.gitignore` mit Regel `config.json` ignoriert.
    - Die lokale Config ist damit bewusst nicht Teil der erzeugten Forschungsartefakte und nicht Teil des normalen Git-Status.

## 16. Naechster konkreter Umsetzungsschritt

Als erster Implementierungsschritt sollte nicht direkt Unity geaendert werden. Zuerst wird der batchfaehige Offline-Teil gebaut:

1. `tools/case_study_pipeline/` anlegen.
2. `mlds_ingestion.py` implementieren.
3. `scene_graph.normalized.json` fuer die drei vorhandenen MLDS-Dateien erzeugen.
4. Validator fuer Input und Normalisierung schreiben.
5. Erst danach LLM-basierte Semantikanalyse anschliessen.

Damit ist die Basis reproduzierbar, bevor Modellgenerierung und Runtime-Tests dazukommen.
