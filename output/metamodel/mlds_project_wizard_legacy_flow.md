# Bestehender Legacy-Datenfluss des MLDSI Project Wizard

Stand: 2026-07-09

## Kurzfazit

Der aktuelle `MLDSI Project Wizard` erzeugt ein normales Interactive-Agents-Projekt. Er erzeugt keine FunctionalMLDS-Instanz und keine TraceMap. Die Analyse erzeugt einen fluechtigen Draft im Backend; erst der Commit schreibt Projektdateien.

## Unity-Seite

Datei:

- `InteractivAgents/InteractiveAgents2/Assets/Scripting/ArrowProjectWizard.cs`

### 1. MLDSI laden

`LoadArrowFile` liest die ausgewaehlte `.json`- oder `.mldsi`-Datei als UTF-8-Text in `arrowJson`.

### 2. Analyze

`StartAnalyze` sendet:

```json
{
  "arrow_json": "<MLDSI JSON als String>"
}
```

an:

```text
POST /projects/arrow/analyze
```

Die Response enthaelt:

- `session_id`
- `draft`

Der Draft wird in Unity angezeigt und enthaelt:

- `assistant_message`
- `analysis`
- `project`
- `agents`
- `knowledge`
- `placement_preview`

### 3. Chat-Refinement

`SendChat` sendet:

```json
{
  "session_id": "<session_id>",
  "user_text": "<Nutzerwunsch>"
}
```

an:

```text
POST /projects/arrow/chat
```

Die Response ersetzt den aktuellen Draft.

### 4. Commit

`CommitProject` sendet:

```json
{
  "session_id": "<session_id>",
  "display_name": "<Projektname>",
  "project_id": "<optionale Projekt-ID>",
  "description": "<Beschreibung>"
}
```

an:

```text
POST /projects/arrow/commit
```

Die Response enthaelt:

- `status`
- `project`
- `placements`
- `room_objects`
- `room_bounds`

## Backend-Seite

Dateien:

- `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/server.py`
- `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/state.py`
- `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/projects.py`
- `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/schemas.py`

### 1. Analyze-Endpunkt

`server.py` routet `POST /projects/arrow/analyze` auf:

```python
store.analyze_arrow(payload)
```

`analyze_arrow`:

- parst `arrow_json`.
- ruft `_generate_arrow_draft` auf.
- legt eine `ArrowProjectDraft`-Session im Speicher ab.
- gibt `session_id` und Draft zurueck.

### 2. Draft-Erzeugung

`_generate_arrow_draft` verwendet `arrow_project_schema()` und erzeugt per LLM ein strukturiertes JSON mit:

- `assistant_message`
- `analysis`
- `project`
- `agents`
- `knowledge`
- `placement_preview`

Die Normalisierung erfolgt in `_normalize_arrow_draft`.

### 3. Chat-Endpunkt

`server.py` routet `POST /projects/arrow/chat` auf:

```python
store.arrow_chat(payload)
```

`arrow_chat`:

- laedt die `ArrowProjectDraft`-Session.
- ergaenzt die History um den Nutzerwunsch.
- ruft `_generate_arrow_draft` erneut auf.
- ersetzt Draft-Felder in der Session.
- gibt den aktualisierten Draft zurueck.

### 4. Commit-Endpunkt

`server.py` routet `POST /projects/arrow/commit` auf:

```python
store.commit_arrow_project(payload)
```

`commit_arrow_project`:

- laedt die `ArrowProjectDraft`-Session.
- erzeugt ein Projekt ueber `ProjectManager.create_project`.
- berechnet/normalisiert Agentenplatzierungen.
- schreibt Agenten ueber `ProjectManager.save_agents`.
- schreibt den originalen MLDSI-Payload als `room_plan.json` ueber `ProjectManager.save_room_plan`.
- schreibt Knowledge-Eintraege ueber `ProjectManager.upsert_knowledge`.
- aktualisiert die projektbezogene Knowledge Base.

## Persistierte Legacy-Artefakte

Bei erfolgreichem Commit entstehen unter:

```text
InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/<project_id>/
```

die folgenden Artefakte:

- `project.json`
- `room_plan.json`
- `agents.json`
- `kb/<tag>/<name>.txt`

## Was im Legacy-Ablauf nicht entsteht

Der Legacy-Ablauf erzeugt derzeit nicht:

- `functionalmlds/functionalmlds.instance.generated.json`
- `trace_map.json`
- `validation/functionalmlds_invariants_validation.json`
- `validation/schema_validation.json`
- `validation/traceability_metrics.json`
- `validation/handoff_metrics.json`
- FunctionalMLDS-`ValidationCase`-Artefakte
- FunctionalMLDS-`RuntimeBinding`-/`RuntimeAction`-Traceability ausserhalb der optionalen Runtime-Log-Unterstuetzung

## Statische Zwischenpruefung

Die relevanten Schreibaufrufe im Legacy-Commit sind:

- `ProjectManager.create_project`
- `ProjectManager.save_agents`
- `ProjectManager.save_room_plan`
- `ProjectManager.upsert_knowledge`

Eine Suche in den Legacy-Commit-Pfaden nach `functionalmlds`, `trace_map` und `functionalmlds_trace_path` zeigt:

- keine Erzeugung einer FunctionalMLDS-Instanz.
- keine Erzeugung einer TraceMap.
- keine FunctionalMLDS-Referenz in `project.json`.

## Konsequenz fuer den Umbau

Der FunctionalMLDS-Modus muss additiv eingefuehrt werden. Legacy darf weiter genau diesen Ablauf ausfuehren. Der neue Modus muss dagegen nach dem Commit mindestens erzeugen:

- Runtime-Projektdateien wie Legacy.
- zusaetzlich `trace_map.json` im Runtime-Projekt.
- zusaetzlich `functionalmlds.instance.generated.json` im Forschungs-/Case-Verzeichnis.
- zusaetzlich Validierungsreports gegen Schema, Invarianten und Traceability.
