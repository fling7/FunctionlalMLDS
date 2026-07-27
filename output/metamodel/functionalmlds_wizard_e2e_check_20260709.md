# FunctionalMLDS Wizard E2E Check 2026-07-09

## Fragestellung

Eine bestehende MLDS-Datei soll im MLDS Project Wizard im Modus `FunctionalMLDS` nicht nur als Legacy-Interaktionsprojekt analysiert werden, sondern in eine FunctionalMLDS-Instanz ueberfuehrt werden. Die erzeugten Dateien muessen sich am FunctionalMLDS-Metamodell orientieren, validierbar sein und weiterhin ein nutzbares Interactive-Agents-Projekt erzeugen.

## Gepruefter Ablauf

1. Quelle: `InteractivAgents/InteractiveAgents2/Assets/Scripting/MLDSSteinpilz.json`
2. Backend: `http://127.0.0.1:8787`
3. Analyze-Payload:
   - `generation_mode=functionalmlds`
   - `run_validation=true`
   - `max_repair_attempts=3`
4. Commit-Payload:
   - `generation_mode=functionalmlds`
   - gleiche `session_id` wie Analyze
   - feste `project_id` als FunctionalMLDS-Case-ID

## Ergebnis

| Pruefpunkt | Ergebnis |
| --- | --- |
| Backend-Health | ok |
| Analyze-Modus | `functionalmlds` |
| Analyze-Validierung | `valid` |
| Commit-Status | `ok` |
| Commit-Modus | `functionalmlds` |
| Commit-Validierung | `valid` |
| Unity-Batchcompile | erfolgreich, keine C#-Compilerfehler |
| Legacy-Endpoint-Smoke | erfolgreich |

## Erzeugte Kernartefakte

Case-ID: `mldssteinpilz_e2e_1783611970`

| Artefakt | Pfad | Status |
| --- | --- | --- |
| Quell-MLDS | `output/wizard_functionalmlds/mldssteinpilz_e2e_1783611970/input/source_mlds.json` | vorhanden |
| FunctionalMLDS-Instanz | `output/wizard_functionalmlds/mldssteinpilz_e2e_1783611970/functionalmlds/functionalmlds.instance.generated.json` | vorhanden |
| E2E-Report | `output/wizard_functionalmlds/mldssteinpilz_e2e_1783611970/e2e_wizard_report.json` | vorhanden |
| Projekt | `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/mldssteinpilz_e2e_1783611970/project.json` | vorhanden |
| Agenten | `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/mldssteinpilz_e2e_1783611970/agents.json` | vorhanden |
| Raumplan | `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/mldssteinpilz_e2e_1783611970/room_plan.json` | vorhanden |
| Trace-Map | `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/mldssteinpilz_e2e_1783611970/trace_map.json` | vorhanden |

## Metamodell-Abdeckung der Instanz

| Element | Anzahl |
| --- | ---: |
| UseCases | 1 |
| Main Scenarios | 1 |
| ScenarioSteps | 12 |
| Actors | 3 |
| Entities | 53 |
| Agents | 6 |
| Capabilities | 9 |
| RuntimeBindings | 9 |
| ValidationCases | 6 |
| SatisfyRelationships | 6 |

Schema: `functionalmlds_case_study`

Metamodell-Version: `v0.5`

## Hinweise

Die Commit-Validierung ist `valid`, enthaelt aber erwartbare Warnungen fuer noch nicht vorhandene Runtime-Evidenz, z. B. fehlende echte Laufzeit-Events und noch nicht evaluierte Handoff-Entscheidungsgenauigkeit. Das ist fuer die statische Metamodell-Konformitaet korrekt: Die Struktur ist gueltig, Runtime-Evidenz entsteht erst nach echter Interaktion in Unity.

## Relevante Reparaturen

- Backend-Prozess wurde sauber neu gestartet; vorher antwortete ein alter Listener im Legacy-Pfad.
- `tools/case_study_pipeline/llm_client.py` loest Backend-Konfigurationspfade robuster auf.
- `backend/state.py` verhindert, dass ein fehlgeschlagener FunctionalMLDS-Lauf still wie Legacy aussieht.
- `ArrowProjectWizard.cs` zeigt eine Warnung, wenn im FunctionalMLDS-Modus keine FunctionalMLDS-Daten in der Backend-Antwort sind.
- `ArrowProjectWizard.cs` sendet beim Commit nun ebenfalls `generation_mode`.
