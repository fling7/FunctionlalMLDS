# Ziel-Datenmodell: FunctionalMLDS-Drafts im MLDS Project Wizard

Stand: 2026-07-09

## Grundsatz

Der bestehende Wizard-Draft bleibt kompatibel. Die bisherigen Felder bleiben im Legacy- und FunctionalMLDS-Modus erhalten:

- `assistant_message`
- `analysis`
- `project`
- `agents`
- `knowledge`
- `placement_preview`

FunctionalMLDS erweitert diesen Draft nur um optionale Felder. Dadurch koennen alte Unity-Versionen alte Backend-Antworten weiterhin lesen, und der Legacy-Modus muss keine FunctionalMLDS-Artefakte erzeugen.

## Request-Erweiterungen

### Analyze

```json
{
  "arrow_json": "{...}",
  "generation_mode": "legacy"
}
```

`generation_mode` ist optional. Fehlt das Feld, gilt `legacy`.

Erlaubte Werte:

- `legacy`
- `functionalmlds`

### Chat

```json
{
  "session_id": "...",
  "user_text": "..."
}
```

Der Chat-Modus wird aus der gespeicherten Wizard-Session gelesen. Ein optional mitgesendetes `generation_mode` darf nur als Plausibilitaetscheck verwendet werden und darf den Session-Modus nicht stillschweigend ueberschreiben.

### Commit

```json
{
  "session_id": "...",
  "display_name": "...",
  "project_id": "...",
  "description": "...",
  "generation_mode": "functionalmlds"
}
```

`generation_mode` bleibt optional. Wenn es gesetzt ist, muss es zum gespeicherten Session-Modus passen. Bei Abweichung soll der Commit abbrechen, damit kein Legacy-Projekt versehentlich als FunctionalMLDS-Projekt behandelt wird.

## Draft-Erweiterungen

Neue optionale Felder im `draft`:

```json
{
  "generation_mode": "functionalmlds",
  "functionalmlds_summary": {},
  "functionalmlds_path": "...",
  "trace_map_path": "...",
  "validation_summary": {},
  "scenario_summary": {},
  "capability_summary": {},
  "handoff_summary": {},
  "room_knowledge_summary": {}
}
```

Diese Felder sind im Legacy-Modus nicht erforderlich und sollen dort leer bleiben oder fehlen.

## FunctionalMLDS-Summary

`functionalmlds_summary` fasst die erzeugte FunctionalMLDS-Instanz zusammen. Es transportiert nicht die komplette Metamodell-Datei in die Unity-UI.

Empfohlene Felder:

```json
{
  "case_id": "bestfit_career_fair",
  "schema": "functionalmlds_case_study",
  "metamodel_version": "v0.5",
  "use_case_id": "UC-BESTFIT_CAREER_FAIR-01",
  "main_scenario_id": "SC-BESTFIT_CAREER_FAIR-MAIN",
  "actor_count": 3,
  "entity_count": 39,
  "agent_count": 5,
  "capability_count": 9,
  "runtime_binding_count": 9,
  "validation_case_count": 6,
  "satisfy_relationship_count": 6
}
```

## Validation-Summary

`validation_summary` zeigt, ob die erzeugten Dateien wirklich am Metamodell validiert wurden.

Empfohlene Felder:

```json
{
  "status": "valid",
  "schema_status": "valid",
  "invariant_status": "valid",
  "materialization_status": "valid",
  "traceability_status": "valid",
  "handoff_status": "valid",
  "error_count": 0,
  "warning_count": 2,
  "traceability_average_coverage": 0.847222,
  "handoff_decision_accuracy": 1.0
}
```

Commit-Regel: Im FunctionalMLDS-Modus darf `status` nur `valid` sein, wenn Schema-, Invariant- und Materialisierungsvalidierung erfolgreich sind. Traceability- und Handoff-Metriken duerfen Warnungen enthalten, muessen aber vorhanden und auswertbar sein.

## Scenario-Summary

`scenario_summary` macht fuer die UI sichtbar, welcher Ablauf im FunctionalMLDS-Modell abgebildet wurde.

Empfohlene Felder:

```json
{
  "use_case_id": "...",
  "main_scenario_id": "...",
  "goal": "...",
  "step_count": 12,
  "validation_case_count": 6
}
```

Eine spaetere UI kann zusaetzlich gekuerzte Steps anzeigen. Fuer die erste Implementierung reicht eine kompakte Summary, damit Unity nicht die gesamte Szenariostruktur parsen muss.

## Capability-Summary

`capability_summary` zeigt, welche Faehigkeiten und Runtime-Bindings vom Metamodell abgedeckt werden.

Empfohlene Felder:

```json
{
  "capability_count": 9,
  "runtime_binding_count": 9,
  "runtime_action_count": 12,
  "capabilities": [
    {
      "id": "CAP-...-ANSWER-ROOM-GROUNDED-QUESTION",
      "runtime_binding_count": 1
    }
  ]
}
```

## Handoff-Summary

`handoff_summary` sichert die bisherige Agenten-Grundfunktionalitaet ab: Agenten wissen, welches Spezialwissen andere Agenten besitzen und an wen sie uebergeben koennen.

Empfohlene Felder:

```json
{
  "agent_count": 5,
  "declared_handoff_pair_count": 12,
  "valid_handoff_target_ratio": 1.0,
  "handoff_decision_accuracy": 1.0,
  "self_handoff_count": 0
}
```

## Room-Knowledge-Summary

`room_knowledge_summary` zeigt, dass Raumwissen aus der MLDS weiterhin eingebettet ist.

Empfohlene Felder:

```json
{
  "room_object_count": 27,
  "semantic_zone_count": 6,
  "knowledge_file_count": 15,
  "agent_to_knowledge_tag_coverage": 1.0,
  "object_group_to_agent_role_grounding": 1.0
}
```

Damit kann der Wizard anzeigen, dass Agenten nicht nur abstrakte Rollen besitzen, sondern auf konkrete Objekte, Zonen und Knowledge-Tags aus der MLDS bezogen sind.

## Commit-Response-Erweiterungen

Die bestehende Commit-Antwort bleibt erhalten:

- `status`
- `project`
- `placements`
- `room_objects`
- `room_bounds`

Neue optionale FunctionalMLDS-Felder:

- `generation_mode`
- `functionalmlds_path`
- `trace_map_path`
- `validation_summary`
- `functionalmlds_summary`

Im materialisierten `project.json` soll zusaetzlich mindestens ein Verweis auf die FunctionalMLDS-Instanz stehen. Der bestehende Case-Study-Materializer nutzt bereits `functionalmlds_trace_path`; fuer den Wizard sollte der Name spaeter eindeutig festgelegt werden, z. B. `functionalmlds_path` plus `trace_map_path`.

## Backend-Session-Erweiterung

`ArrowProjectDraft` soll optional erweitert werden um:

- `generation_mode: str = "legacy"`
- `case_id: Optional[str] = None`
- `case_dir: Optional[str] = None`
- `functionalmlds_path: Optional[str] = None`
- `trace_map_path: Optional[str] = None`
- `validation_summary: Dict[str, Any] = field(default_factory=dict)`
- `functionalmlds_summary: Dict[str, Any] = field(default_factory=dict)`
- `scenario_summary: Dict[str, Any] = field(default_factory=dict)`
- `capability_summary: Dict[str, Any] = field(default_factory=dict)`
- `handoff_summary: Dict[str, Any] = field(default_factory=dict)`
- `room_knowledge_summary: Dict[str, Any] = field(default_factory=dict)`

Legacy-Code darf diese Felder nicht benoetigen.

## Unity-Parse-Regeln

Unitys `JsonUtility` kann alte Drafts weiterhin lesen, solange neue Felder optional sind. Fuer die Wizard-UI sollen neue serialisierbare Klassen ergaenzt werden:

- `FunctionalMldsSummary`
- `ValidationSummary`
- `ScenarioSummary`
- `CapabilitySummary`
- `HandoffSummary`
- `RoomKnowledgeSummary`

Die Anzeige dieser Klassen erfolgt nur, wenn `generation_mode == "functionalmlds"` oder mindestens eines der FunctionalMLDS-Felder gesetzt ist.

## Nicht-Ziele

Der Draft transportiert nicht die komplette FunctionalMLDS-Instanz. Die vollstaendige Instanz bleibt Datei-Artefakt:

`functionalmlds/functionalmlds.instance.generated.json`

Die UI zeigt nur Zusammenfassungen, Pfade und Validierungsstatus. Das reduziert Parse-Komplexitaet in Unity und verhindert, dass grosse Metamodell-Instanzen im Editor-Fenster unuebersichtlich werden.
