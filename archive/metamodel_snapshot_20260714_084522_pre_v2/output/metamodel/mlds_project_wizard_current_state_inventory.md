# MLDS Project Wizard Current State Inventory

Stand: 2026-07-09

## Scope

Dieses Inventar sichert den Ist-Zustand vor dem Umbau des MLDSI Project Wizard auf einen zusaetzlichen FunctionalMLDS-Modus.

## Erfasste Dateien

| Datei | Rolle | Status |
|---|---|---|
| `InteractivAgents/InteractiveAgents2/Assets/Scripting/ArrowProjectWizard.cs` | Unity-Editor-Wizard fuer MLDSI-Analyse, Chat-Refinement und Commit | vorhanden |
| `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/server.py` | HTTP-Endpunkte fuer Setup, Chat, Project Manager und Arrow/Wizard | vorhanden, `py_compile` erfolgreich |
| `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/state.py` | Backend-Sessionlogik, Arrow-Draft-Erzeugung, Commit in Interactive-Agents-Projekt | vorhanden, `py_compile` erfolgreich |
| `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/schemas.py` | Structured-Output-Schema fuer Wizard-Drafts | vorhanden, `py_compile` erfolgreich |

## Aktuelle Wizard-Endpunkte

Der Wizard nutzt aktuell ausschliesslich den bestehenden Arrow/MLDSI-Ablauf:

- `POST /projects/arrow/analyze`
- `POST /projects/arrow/chat`
- `POST /projects/arrow/commit`

Im aktuellen Wizard-Code gibt es noch keine Modusunterscheidung wie `generation_mode = legacy | functionalmlds`.

## Aktuelle Persistenz beim Commit

`commit_arrow_project` speichert aktuell ein normales Interactive-Agents-Projekt:

- `projects/<project_id>/project.json`
- `projects/<project_id>/room_plan.json`
- `projects/<project_id>/agents.json`
- `projects/<project_id>/kb/...`

Der bestehende Wizard-Commit erzeugt aktuell nicht automatisch:

- `functionalmlds/functionalmlds.instance.generated.json`
- `trace_map.json`
- FunctionalMLDS-Schema- oder Invariantenreports
- Traceability-Metriken
- FunctionalMLDS-ValidationCases

## Bereits vorhandene FunctionalMLDS-Integration ausserhalb des Wizards

Die FunctionalMLDS-Case-Study-Pipeline existiert separat unter:

- `tools/case_study_pipeline/`

Sie erzeugt fuer Case-Study-Projekte bereits:

- FunctionalMLDS-Instanzen
- TraceMaps
- validierte Interactive-Agents-Projekte
- Schema-/Invarianten-/Traceability-Reports
- Runtime-Testreports

Diese Pipeline ist aber noch nicht direkt in den Unity-Wizard eingebunden.

## Zwischenpruefungen

| Check | Ergebnis | Kommentar |
|---|---|---|
| Backend Python `py_compile` fuer `server.py`, `state.py`, `schemas.py` | erfolgreich | keine Syntaxfehler in den relevanten Backend-Dateien |
| Unity-Version passend zum Projekt | ermittelt | Projekt verlangt Unity `6000.4.5f1`, lokal vorhanden |
| Unity Batchmode Compile/Import | blockiert | Unity meldet, dass das Projekt bereits in einer anderen Unity-Instanz geoeffnet ist |
| `dotnet build` als Ersatzcheck | nicht moeglich | lokal ist nur .NET Runtime, kein .NET SDK installiert |

## Konsequenz fuer die Umsetzung

- Legacy-Code darf erst geaendert werden, nachdem die bestehenden Pfade sauber erhalten bleiben.
- Der neue FunctionalMLDS-Modus sollte zunaechst additiv implementiert werden.
- Vor dem finalen Abschluss muss der Unity-Batchmode-Compile erneut ausgefuehrt werden, sobald keine zweite Unity-Instanz das Projekt blockiert.
- FunctionalMLDS darf im neuen Modus nicht optional-validierungsfrei sein: ein FunctionalMLDS-Commit muss Modellartefakte erzeugen und gegen Schema, Invarianten und Traceability pruefen.
