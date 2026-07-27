# Definition-of-Done-Audit: MLDS Project Wizard FunctionalMLDS

Stand: 2026-07-09

Dieses Audit sammelt die finalen Nachweise fuer die Definition-of-Done-Punkte aus `mlds_project_wizard_functionalmlds_tasklist.md`.

## 1. Wizard Bietet Sichtbar Beide Modi An

Status: bestanden.

Nachweise:

- `InteractivAgents/InteractiveAgents2/Assets/Scripting/ArrowProjectWizard.cs` definiert `GenerationModeLabels` mit:
  - `Legacy Interactive Agents`
  - `FunctionalMLDS`
- `ArrowProjectWizard.cs` rendert diese Labels im Abschnitt `Projektmodus` ueber `GUILayout.Toolbar(...)`.
- Unity-Menueintrag ist vorhanden: `Tools/MLDSI Project Wizard`.
- `ShowWindow()` ruft `GetWindow<ArrowProjectWizard>("MLDSI Project Wizard")`.
- Unity-Batchmode-Compile auf `InteractivAgents/InteractiveAgents2` lief mit Exitcode `0`.
- Unity-Batchmode-ExecuteMethod `ArrowProjectWizard.ShowWindow` lief mit Exitcode `0`.
- Relevante Logs:
  - `%TEMP%/functionalmlds_unity_compile_20260709_152657.log`
  - `%TEMP%/functionalmlds_unity_wizard_open_20260709_152836.log`

Bewertung:

Der Wizard ist im Unity-Editor oeffenbar, kompiliert und bietet die beiden Projektmodi sichtbar an.

## 2. Legacy-Modus Funktioniert Unveraendert

Status: bestanden.

Nachweise:

- Automatisierter Test: `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py`.
- Ausgefuehrter Befehl:
  - `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_backend_endpoints_smoke -v`
- Ergebnis:
  - `Ran 1 test ... OK`
- Der Legacy-Analyze-Aufruf verwendet dieselbe MLDS wie der FunctionalMLDS-Pfad, aber ohne FunctionalMLDS-spezifische Optionen:
  - kein `generation_mode=functionalmlds`
  - kein `run_validation`
  - kein `max_repair_attempts`
  - kein `project_id_hint`
- Legacy-Draft liefert `generation_mode=legacy`.
- Legacy-Draft enthaelt keine FunctionalMLDS-Felder:
  - keine `functionalmlds_summary`
  - keinen `functionalmlds_path`
  - keinen `trace_map_path`
- Legacy-Commit erzeugt die normalen Projektartefakte:
  - `project.json`
  - `room_plan.json`
  - `agents.json`
  - `kb/...`
- Legacy-Commit erzeugt keine FunctionalMLDS-Pflichtartefakte:
  - keine `trace_map.json`
  - kein `functionalmlds/`-Verzeichnis
- Der FunctionalMLDS-Adapter wird im Legacy-Pfad bis nach Legacy-Commit nicht aufgerufen.

Bewertung:

Der Legacy-Modus bleibt rueckwaertskompatibel. Fehlende oder nicht gesetzte FunctionalMLDS-Optionen fuehren weiterhin zum bisherigen Projektformat.

## 3. FunctionalMLDS-Analyze Zeigt Agenten, Knowledge, Handoff- Und FunctionalMLDS-Summary

Status: bestanden.

Nachweise:

- Automatisierter Test: `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py`.
- Ausgefuehrter Befehl:
  - `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_backend_endpoints_smoke -v`
- Ergebnis:
  - `Ran 1 test ... OK`
- FunctionalMLDS-Analyze-Request verwendet:
  - `generation_mode=functionalmlds`
  - `project_id_hint=classroom_dinosaur`
  - `run_validation=true`
  - `max_repair_attempts=0`
- Gepruefte Draft-Inhalte:
  - `generation_mode=functionalmlds`
  - `validation_summary.status=valid`
  - `functionalmlds_summary.case_id=classroom_dinosaur`
  - `functionalmlds_path` vorhanden
  - 4 Agenten im Draft
  - mindestens 8 Knowledge-Eintraege im Draft
  - FunctionalMLDS-Summary enthaelt RuntimeBindings und ValidationCases
  - Scenario-Summary enthaelt ScenarioSteps
  - Capability-Summary enthaelt RuntimeActions
  - Handoff-Summary enthaelt deklarierte Handoff-Paare und gueltige Zielquote
  - Room-Knowledge-Summary enthaelt Raumobjekte und Knowledge-Dateien
- Unity-Wizard-Code zeigt die Draft-Daten in separaten Abschnitten:
  - `Metamodell-Artefakte`
  - `Validierung`
  - `Use Case / Szenario`
  - `Capabilities / Runtime`
  - `Handoff / Spezialwissen`
  - `Raumwissen / Grounding`

Bewertung:

Der FunctionalMLDS-Analyze-Pfad erzeugt einen validen, sichtbaren Draft mit Agenten, Wissen, Handoff-Informationen und FunctionalMLDS-Summaries. Der Wizard besitzt die UI-Abschnitte, um diese Daten anzuzeigen.

## 4. FunctionalMLDS-Commit Erzeugt Vollstaendige Projekt- Und Modellartefakte

Status: bestanden.

Nachweise:

- Automatisierter Test: `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py`.
- Ausgefuehrter Befehl:
  - `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_backend_endpoints_smoke -v`
- Ergebnis:
  - `Ran 1 test ... OK`
- FunctionalMLDS-Commit-Request verwendet:
  - `generation_mode=functionalmlds`
  - `project_id=classroom_dinosaur`
- Gepruefte Commit-Response:
  - `status=ok`
  - `generation_mode=functionalmlds`
  - `validation_summary.status=valid`
  - `schema_status=valid`
  - `invariant_status=valid`
  - `materialization_status=valid`
  - `traceability_status=valid`
  - `handoff_status=valid`
- Gepruefte Backend-Projektartefakte:
  - `project.json`
  - `room_plan.json`
  - `agents.json`
  - `kb/...` mit mindestens einer Textdatei
  - `trace_map.json`
- Gepruefte Trace-Map:
  - existiert im Backend-Projekt
  - Commit-Response `trace_map_path` zeigt auf diese Datei
  - `trace_map.json` hat `schema=functionalmlds_trace_map`
- Gepruefte FunctionalMLDS-Artefakte:
  - `functionalmlds/functionalmlds.instance.generated.json`
  - Commit-Response `functionalmlds_path` zeigt auf diese Datei
  - Instanz hat `schema=functionalmlds_case_study`
- Gepruefte Validierungsreports:
  - `schema_validation.json` mit `status=valid`
  - `functionalmlds_invariants_validation.json` mit `status=valid`
  - `project_materialization_validation.json` mit `status=valid`
  - `traceability_metrics.json` mit `status=valid`
  - `handoff_metrics.json` mit `status=valid`

Bewertung:

Der FunctionalMLDS-Commit materialisiert ein nutzbares Interactive-Agents-Projekt und legt parallel die benoetigten Metamodell-, Trace- und Validierungsartefakte ab.

## 5. Agenten Beantworten Raum- Und MLDS-Objektfragen

Status: bestanden.

Nachweise:

- Automatisierter Test: `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py`.
- Ausgefuehrter Befehl:
  - `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_backend_endpoints_smoke -v`
- Ergebnis:
  - `Ran 1 test ... OK`
- Testaufbau:
  - FunctionalMLDS-Analyze erzeugt einen validen Draft fuer `classroom_dinosaur`.
  - FunctionalMLDS-Commit materialisiert das Backend-Projekt und die Metamodell-Artefakte.
  - `POST /setup` startet eine Runtime-Session fuer das frisch erzeugte Projekt.
  - Der Chat wird mit `active_agent_id=teacher_agent` ueber `POST /chat` aufgerufen.
- Testfrage:
  - `Welche Ausstattung gibt es im Unterrichtsbereich?`
- Token-Schonung:
  - Der Fake-OpenAI-Client erzwingt fuer `schema_name=npc_action` einen `OpenAIHTTPError`.
  - Dadurch wird der deterministische Chat-Fallback getestet, ohne echte API-Tokens zu verbrauchen.
- Gepruefte Runtime-Antwort:
  - bleibt beim Agenten `teacher_agent`;
  - erzeugt kein Handoff;
  - enthaelt die Markierung `functionalmlds-raumwissen`;
  - nennt das MLDS-Objekt `chalkboard`;
  - nennt die MLDS-Objektgruppe `student desks`.

Bewertung:

Ein frisch per FunctionalMLDS-Wizard-Pfad erzeugtes Projekt kann zur Laufzeit eine konkrete Frage zum Raum und zu MLDS-Objekten aus dem materialisierten FunctionalMLDS-/Projektwissen beantworten. Dieser Punkt ist damit fuer den exemplarischen Case `classroom_dinosaur` automatisiert nachgewiesen.

## 6. Agenten Nutzen Spezialwissen

Status: bestanden.

Nachweise:

- Automatisierter Test: `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py`.
- Ausgefuehrter Befehl:
  - `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_backend_endpoints_smoke -v`
- Ergebnis:
  - `Ran 1 test ... OK`
- Testaufbau:
  - Derselbe Endpoint-Smoke erzeugt zuerst ein frisches FunctionalMLDS-Projekt `classroom_dinosaur`.
  - `POST /setup` startet eine Runtime-Session fuer dieses Projekt.
  - Der Chat wird mit `active_agent_id=exhibit_interpreter` ueber `POST /chat` aufgerufen.
- Testfrage:
  - `What is special about the dinosaur skeleton exhibit for paleontology?`
- Relevant gemappte Agentenfelder:
  - `exhibit_interpreter.expertise` enthaelt fachliche Rollenanteile wie Museum Education und Paleontology Basics.
  - `exhibit_interpreter.knowledge_tags` enthaelt `dinosaur_display_zone` und `dinosaur_education`.
  - `exhibit_interpreter.grounded_object_ids` enthaelt `dinosaur_skeleton`.
- Token-Schonung:
  - Der Fake-OpenAI-Client erzwingt fuer `schema_name=npc_action` einen `OpenAIHTTPError`.
  - Dadurch wird der deterministische Chat-Fallback getestet, ohne echte API-Tokens zu verbrauchen.
- Gepruefte Runtime-Antwort:
  - bleibt beim Agenten `exhibit_interpreter`;
  - erzeugt kein Handoff;
  - enthaelt die Markierung `functionalmlds-raumwissen`;
  - nennt `dinosaur skeleton`;
  - nennt `paleontology`.

Bewertung:

Das frisch erzeugte FunctionalMLDS-Projekt nutzt agentenspezifische Knowledge-Tags, Expertise und geerdete Objektbeziehungen zur Laufzeit. Damit ist nachgewiesen, dass Spezialwissen nicht nur in den Artefakten gespeichert wird, sondern fuer agentenspezifische Antworten nutzbar ist.

## 7. Agenten Loesen Handoffs An Geeignetere Agenten Aus

Status: bestanden.

Nachweise:

- Automatisierter Test: `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py`.
- Ausgefuehrter Befehl:
  - `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_backend_endpoints_smoke -v`
- Ergebnis:
  - `Ran 1 test ... OK`
- Testaufbau:
  - Derselbe Endpoint-Smoke erzeugt zuerst ein frisches FunctionalMLDS-Projekt `classroom_dinosaur`.
  - `POST /setup` startet eine Runtime-Session fuer dieses Projekt.
  - Der Chat wird bewusst mit `active_agent_id=teacher_agent` gestartet, obwohl die Frage zur Dinosaurierausstellung gehoert.
- Testfrage:
  - `I need details about the dinosaur skeleton exhibit and paleontology.`
- Erwartete Modellgrundlage:
  - Die Handoff-Matrix enthaelt die Kante `teacher_agent -> exhibit_interpreter`.
  - `teacher_agent.handoff_targets` enthaelt `exhibit_interpreter`.
  - `exhibit_interpreter` besitzt passende Expertise, Knowledge-Tags und das geerdete Objekt `dinosaur_skeleton`.
- Token-Schonung:
  - Der Fake-OpenAI-Client erzwingt fuer `schema_name=npc_action` einen `OpenAIHTTPError`.
  - Dadurch wird der deterministische Handoff-Fallback getestet, ohne echte API-Tokens zu verbrauchen.
- Gepruefte Runtime-Reaktion:
  - `active_agent_id` wechselt zu `exhibit_interpreter`;
  - `handoff.from=teacher_agent`;
  - `handoff.to=exhibit_interpreter`;
  - es entstehen mindestens zwei Chat-Events;
  - die Handoff-Antwort nennt `exhibit interpreter`;
  - die Zielantwort enthaelt `dinosaur skeleton` und `paleontology`.

Bewertung:

Das frisch erzeugte FunctionalMLDS-Projekt nutzt die aus dem Metamodell abgeleitete Handoff-Struktur zur Laufzeit. Eine fachlich falsch adressierte Frage wird vom Ausgangsagenten an den besser geeigneten Zielagenten weitergeleitet und dort beantwortet.

## 8. FunctionalMLDS-Invarianten Sind Valide

Status: bestanden.

Nachweise:

- Automatisierter Test: `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py`.
- Ausgefuehrter Befehl:
  - `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_backend_endpoints_smoke -v`
- Ergebnis:
  - `Ran 1 test ... OK`
- Testaufbau:
  - Derselbe Endpoint-Smoke erzeugt zuerst ein frisches FunctionalMLDS-Projekt `classroom_dinosaur`.
  - FunctionalMLDS-Commit fuehrt die Validierungen aus.
  - Der Test liest anschliessend den erzeugten Report `validation/functionalmlds_invariants_validation.json`.
- Gepruefte Commit-Response:
  - `validation_summary.invariant_status=valid`
- Gepruefte Report-Metriken:
  - `invariant_count >= 8`;
  - `passed_invariant_count == invariant_count`;
  - `failed_invariant_count == 0`;
  - `errors == []`.
- Gepruefte Einzelinvarianten:
  - jede Invariante im Report hat `status=valid`;
  - jede Invariante im Report hat `error_count=0`.

Bewertung:

Der FunctionalMLDS-Wizard-Pfad erzeugt nicht nur eine Instanzdatei, sondern eine Instanz, die die definierten FunctionalMLDS-Invarianten erfuellt. Der Nachweis erfolgt auf dem frisch erzeugten Artefakt und nicht nur auf einem statischen Referenzbestand.

## 9. Traceability-Metriken Sind Vorhanden

Status: bestanden.

Nachweise:

- Automatisierter Test: `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py`.
- Ausgefuehrter Befehl:
  - `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_backend_endpoints_smoke -v`
- Ergebnis:
  - `Ran 1 test ... OK`
- Testaufbau:
  - Derselbe Endpoint-Smoke erzeugt zuerst ein frisches FunctionalMLDS-Projekt `classroom_dinosaur`.
  - FunctionalMLDS-Commit fuehrt die Validierungen aus.
  - Der Test liest anschliessend den erzeugten Report `validation/traceability_metrics.json`.
- Gepruefte Commit-Response:
  - `validation_summary.traceability_status=valid`
- Gepruefte Report-Metriken:
  - `metric_count >= 6`;
  - `metric_count == len(traceability_metrics)`;
  - `full_coverage_metric_count >= 4`;
  - `average_coverage > 0.75`;
  - `errors == []`.
- Gepruefte Metrikarten:
  - `requirement_to_validation_coverage`;
  - `scenario_step_to_capability_coverage`;
  - `capability_to_runtime_binding_coverage`;
  - `runtime_action_to_log_coverage`;
  - `agent_to_knowledge_tag_coverage`;
  - `object_group_to_agent_role_grounding`.
- Konsistenzbedingungen pro Metrik:
  - `denominator > 0`;
  - `numerator >= 0`;
  - `0.0 <= coverage <= 1.0`.
- Vollstaendig abgedeckte zentrale Metamodell-Bezuege:
  - Requirements zu ValidationCases;
  - Capabilities zu RuntimeBindings;
  - Agenten zu Knowledge-Tags;
  - Objektgruppen zu Agent-Role-Grounding.
- Runtime-Nachweis:
  - `runtime_action_to_log_coverage.coverage > 0.0`.

Bewertung:

Der FunctionalMLDS-Wizard-Pfad erzeugt Traceability-Metriken fuer Requirements, Szenarioschritte, Capabilities, RuntimeActions, Agentenwissen und Objekt-Grounding. Die Metriken werden aus dem frisch erzeugten Artefakt gelesen und automatisiert auf Struktur, Wertebereiche und zentrale Vollabdeckungen geprueft.

## 10. Runtime-Setup Funktioniert Aus Unity

Status: bestanden.

Nachweise:

- Unity-Editor-Smoke: `InteractivAgents/InteractiveAgents2/Assets/InteractiveAgents/Editor/QuickAgentManagerFunctionalMldsSmoke.cs`.
- Unity-Version:
  - `6000.4.5f1`
- ExecuteMethod:
  - `QuickAgentManagerFunctionalMldsSmoke.Run`
- Testaufbau:
  - Fuer den Test wurde ein temporaerer Backend-Prozess auf einem freien lokalen Port gestartet.
  - Unity erhielt den Backend-Port ueber `FUNCTIONALMLDS_BACKEND_URL`.
  - Unity erhielt das Projekt ueber `FUNCTIONALMLDS_PROJECT_ID=classroom_dinosaur`.
  - `FUNCTIONALMLDS_CHAT_SMOKE=0`, damit dieser DoD-Punkt nur Runtime-Setup ohne API-Verbrauch prueft.
- Ergebnis:
  - Unity-Batchmode-Exitcode `0`.
- Relevante Logs:
  - `%TEMP%/functionalmlds_unity_setup_smoke_20260709_164100.log`
  - `%TEMP%/functionalmlds_unity_setup_backend_20260709_164100.out.log`
  - `%TEMP%/functionalmlds_unity_setup_backend_20260709_164100.err.log`
- Gepruefte Unity-Smoke-Ausgabe:
  - `project_id=classroom_dinosaur`;
  - `session_id_present=True`;
  - `spawned_agents=4`;
  - `expected_agents=4`;
  - `[FunctionalMLDSUnitySmoke] OK`.
- Gepruefte Unity-seitige Runtime-Schritte:
  - `GET /projects` enthaelt `classroom_dinosaur`;
  - `POST /setup` liefert eine `QuickAgentManager.SetupResponse`;
  - `session_id` ist vorhanden;
  - Agentenliste ist nicht leer;
  - `QuickAgentManager` wird als GameObject-Komponente erzeugt;
  - Projektselektion, `sessionId`, `memoryMode`, `lastAgents` und aktiver Agent werden gesetzt;
  - `SpawnAgents` erzeugt fuer jeden Backend-Agenten ein Unity-GameObject;
  - Anzahl gespawnter GameObjects entspricht der Agentenzahl aus dem Backend.

Bewertung:

Das frisch erzeugte FunctionalMLDS-Projekt ist nicht nur im Backend verwendbar, sondern kann aus Unity heraus ueber den bestehenden `QuickAgentManager` eingerichtet werden. Unity kann das Projekt finden, `/setup` aufrufen, die Antwort des Backends parsen und die Agenten in der Szene instanziieren.

## 11. Mindestens Fuenf Chat-Fragen Funktionieren

Status: bestanden.

Nachweise:

- Automatisierter Test: `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py`.
- Ausgefuehrter Befehl:
  - `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_backend_endpoints_smoke -v`
- Ergebnis:
  - `Ran 1 test ... OK`
- Testaufbau:
  - Der Endpoint-Smoke erzeugt zuerst per FunctionalMLDS-Analyze und FunctionalMLDS-Commit ein frisches Projekt `classroom_dinosaur`.
  - Danach startet der Test ueber `POST /setup` eine Runtime-Session fuer dieses Projekt.
  - Der Test zaehlt verifizierte Chatfragen in `verified_chat_questions` und prueft `len(verified_chat_questions) >= 5`.
- Token-Schonung:
  - Der Fake-OpenAI-Client erzwingt fuer `schema_name=npc_action` einen `OpenAIHTTPError`.
  - Dadurch wird der deterministische Chat-Fallback getestet, ohne echte API-Tokens zu verbrauchen.
- Gepruefte Chatfragen:
  - `teacher_agent`: `Welche Ausstattung gibt es im Unterrichtsbereich?`
    - Antwort enthaelt `functionalmlds-raumwissen`, `chalkboard` und `student desks`.
  - `exhibit_interpreter`: `What is special about the dinosaur skeleton exhibit for paleontology?`
    - Antwort enthaelt `functionalmlds-raumwissen`, `dinosaur skeleton` und `paleontology`.
  - `reading_area_guide`: `What can visitors use in the reading area for study and relaxation?`
    - Antwort enthaelt `functionalmlds-raumwissen`, `reading table`, `beanbags` und `bookcase`.
  - `decorative_zone_ambassador`: `Which art and plants shape the decorative zone ambiance?`
    - Antwort enthaelt `functionalmlds-raumwissen`, `abstract artworks` und `potted indoor plants`.
  - `teacher_agent`: `I need details about the dinosaur skeleton exhibit and paleontology.`
    - Runtime loest ein Handoff zu `exhibit_interpreter` aus.
    - Zielantwort enthaelt `dinosaur skeleton` und `paleontology`.

Bewertung:

Das frisch erzeugte FunctionalMLDS-Projekt beantwortet mindestens fuenf unterschiedliche Chatfragen ueber mehrere Agenten, Wissensbereiche und ein Handoff hinweg. Damit ist der praktische Runtime-Zugriff auf Raumwissen, Spezialwissen, Zonenwissen und Handoff-Wissen automatisiert nachgewiesen.

## 12. Mindestens Ein Handoff-Test Funktioniert

Status: bestanden.

Nachweise:

- Automatisierter Test: `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py`.
- Ausgefuehrter Befehl:
  - `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_backend_endpoints_smoke -v`
- Ergebnis:
  - `Ran 1 test ... OK`
- Testaufbau:
  - Der Endpoint-Smoke erzeugt zuerst per FunctionalMLDS-Analyze und FunctionalMLDS-Commit ein frisches Projekt `classroom_dinosaur`.
  - Danach startet der Test ueber `POST /setup` eine Runtime-Session fuer dieses Projekt.
  - Der Test zaehlt verifizierte Handoffs in `verified_handoffs` und prueft `len(verified_handoffs) >= 1`.
- Token-Schonung:
  - Der Fake-OpenAI-Client erzwingt fuer `schema_name=npc_action` einen `OpenAIHTTPError`.
  - Dadurch wird der deterministische Handoff-Fallback getestet, ohne echte API-Tokens zu verbrauchen.
- Gepruefter Handoff:
  - Ausgangsagent: `teacher_agent`;
  - Frage: `I need details about the dinosaur skeleton exhibit and paleontology.`;
  - erwarteter Zielagent: `exhibit_interpreter`;
  - `active_agent_id=exhibit_interpreter`;
  - `handoff.from=teacher_agent`;
  - `handoff.to=exhibit_interpreter`;
  - mindestens zwei Chat-Events;
  - Zielantwort enthaelt `dinosaur skeleton` und `paleontology`.

Bewertung:

Das frisch erzeugte FunctionalMLDS-Projekt fuehrt mindestens einen reproduzierbaren Runtime-Handoff aus. Der Test zeigt, dass eine fachlich falsch adressierte Frage nicht nur beantwortet, sondern an den gemaess FunctionalMLDS/Handoff-Matrix besser geeigneten Agenten weitergeleitet wird.

## 13. Kein API-Key In Projektartefakten Oder Logs

Status: bestanden.

Nachweise:

- Automatisierter Test: `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py`.
- Ausgefuehrter Befehl:
  - `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_backend_endpoints_smoke -v`
- Ergebnis:
  - `Ran 1 test ... OK`
- Testschutz fuer frisch erzeugte Artefakte:
  - Der Endpoint-Smoke erzeugt Legacy- und FunctionalMLDS-Projektartefakte in temporaeren Verzeichnissen.
  - Nach Analyze, Commit, Setup, Chat und Handoff scannt der Test:
    - temporaere Backend-Projektartefakte;
    - temporaeren FunctionalMLDS-Output;
    - erzeugte JSON-, JSONL-, Log-, Markdown-, Text-, XML- und YAML-Dateien.
  - Gepruefte Muster:
    - OpenAI-Secret-Key-Signatur `sk-...`;
    - `OPENAI_API_KEY`;
    - `openai_api_key`;
    - Fake-Key des Tests.
  - Treffer fuehren zum Testfehler.
  - Der Test meldet im Fehlerfall nur Pfade, nicht den Secret-Inhalt.
- Redaktierter Bestandsscan ueber vorhandene Artefakt-/Logbereiche:
  - `output/case_studies`;
  - `output/wizard_functionalmlds`;
  - `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects`;
  - `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/runtime_logs`;
  - relevante temporaere `functionalmlds_*` Logs unter `%TEMP%`.
- Bestandsscan-Ergebnis:
  - `370` Dateien gescannt;
  - `0` Treffer fuer echte OpenAI-Secret-Key-Signatur `sk-...`;
  - `0` Treffer fuer den lokal konfigurierten OpenAI-Key-Wert.
- Einordnung:
  - Der Bestandsscan meldete vier harmlose Referenzen auf Variablen-/Konfigurationsnamen in bestehenden KB-Dokumenten.
  - Diese Treffer enthalten keinen Schluesselwert.

Bewertung:

Der Wizard-/Runtime-Pfad schreibt keinen OpenAI-Key in die erzeugten Projektartefakte oder Logs. Der Schutz ist sowohl fuer neu erzeugte Smoke-Test-Artefakte automatisiert als auch fuer den vorhandenen Artefakt-/Logbestand redaktiert nachgewiesen.
