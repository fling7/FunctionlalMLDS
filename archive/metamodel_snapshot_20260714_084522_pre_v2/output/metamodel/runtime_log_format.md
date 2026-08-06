# Runtime-Logformat fuer die FunctionalMLDS Case Study

Die Runtime-Logs liegen pro Case Study unter `runtime_logs/events.jsonl`. Jede Zeile ist ein eigenstaendiges JSON-Objekt und beschreibt genau ein beobachtbares Ereignis der Pipeline, des Interactive-Agents-Backends oder optional des Unity-Clients.

## Pflichtfelder pro Event

- `timestamp`: ISO-8601-Zeitpunkt in UTC.
- `case_id`: stabile Case-ID, identisch mit dem Case-Ordner und `trace_map.case_id`.
- `session_id`: Backend-Session-ID oder `null`, wenn vor `/setup` noch keine Session existiert.
- `event_type`: kontrollierter Ereignistyp, zum Beispiel `backend_setup_completed`, `backend_chat_completed`, `backend_handoff_completed`, `unity_setup_completed`, `unity_agent_selected`, `unity_chat_sent`, `unity_chat_received`, `unity_handoff_arrived` oder `validation_observation`.
- `agent_id`: beteiligter Agent oder `null`.
- `scenario_step_id`: referenzierter FunctionalMLDS-ScenarioStep oder `null`.
- `capability_id`: referenzierte FunctionalMLDS-Capability oder `null`.
- `runtime_binding_id`: referenziertes RuntimeBinding oder `null`.
- `runtime_action_id`: referenzierte RuntimeAction oder `null`.
- `input_summary`: kurze, redigierte Zusammenfassung des Inputs.
- `output_summary`: kurze, redigierte Zusammenfassung des Outputs.

## Optionale Felder

- `schema`: `functionalmlds_runtime_event`
- `schema_version`: `1.0`
- `event_id`: eindeutige Event-ID.
- `duration_ms`: Laufzeit des beobachteten Schritts.
- `status`: `success`, `failure`, `skipped` oder `needs_manual_review`.
- `error_summary`: kurze, redigierte Fehlermeldung.
- `metadata`: flache skalare Zusatzdaten, zum Beispiel Anzahl geladener Agenten.

## Traceability-Regel

Wenn `runtime_action_id` gesetzt ist, muessen `runtime_binding_id` und `capability_id` zu genau dieser RuntimeAction in `trace_map.json` passen. `scenario_step_id`, `agent_id`, `capability_id`, `runtime_binding_id` und `runtime_action_id` duerfen nur auf IDs verweisen, die in `trace_map.json` vorkommen.

## Beispiel

```json
{"schema":"functionalmlds_runtime_event","schema_version":"1.0","event_id":"EVT-example","timestamp":"2026-07-08T08:37:00Z","case_id":"steinpilz_brand_room","session_id":"session-123","event_type":"backend_setup_completed","agent_id":null,"scenario_step_id":"STEP-STEINPILZ_BRAND_ROOM-07","capability_id":"CAP-STEINPILZ_BRAND_ROOM-SETUP-INTERACTIVE-SESSION","runtime_binding_id":"RB-STEINPILZ_BRAND_ROOM-SETUP-INTERACTIVE-SESSION","runtime_action_id":"RA-STEINPILZ_BRAND_ROOM-BACKEND-SETUP","input_summary":"project_id=steinpilz_brand_room; memory_mode=agent_private_history","output_summary":"setup ok; agents=6","duration_ms":850,"status":"success","error_summary":null,"metadata":{"agent_count":6}}
```

Die formale Spezifikation liegt in `tools/case_study_pipeline/schemas/runtime_event.schema.json`. Das Hilfsmodul `tools.case_study_pipeline.runtime_logging` erzeugt und prueft Events ohne LLM-Aufrufe.
