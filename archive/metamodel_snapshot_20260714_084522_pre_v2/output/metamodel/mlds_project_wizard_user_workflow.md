# Nutzerablauf: MLDS Project Wizard mit Legacy- und FunctionalMLDS-Modus

Stand: 2026-07-09

## Zweck

Der `MLDSI Project Wizard` erzeugt aus einer MLDS/MLDSI-Datei ein Interactive-Agents-Projekt. Der Wizard besitzt zwei Modi:

- `Legacy Interactive Agents`: erzeugt das bisherige Projektformat.
- `FunctionalMLDS`: erzeugt ein validiertes Interactive-Agents-Projekt, dessen Agenten, Wissen, Handoffs, Raumbezug und Runtime-Bindings zusaetzlich auf das FunctionalMLDS-Metamodell abgebildet werden.

Der Legacy-Modus bleibt fuer bestehende Ablaufe unveraendert. Der FunctionalMLDS-Modus ist der Forschungs-/Validierungsmodus fuer die Metamodell-Case-Study.

## Voraussetzungen

- Backend laeuft lokal, standardmaessig unter `http://127.0.0.1:8787`.
- Unity-Projekt ist `InteractivAgents/InteractiveAgents2`.
- Backend-Projektroot ist `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents`.
- Eingabe ist eine JSON- oder `.mldsi`-Datei mit MLDS/MLDSI-Raumbeschreibung.

## Wizard Oeffnen

1. Unity-Projekt `InteractivAgents/InteractiveAgents2` oeffnen.
2. Im Unity-Menue `Tools/MLDSI Project Wizard` auswaehlen.
3. Im Feld `Backend Base Url` die Backend-Adresse pruefen.

Der Wizard ist ein Unity-`EditorWindow`. Der Einstieg wird ueber `ArrowProjectWizard.ShowWindow()` geoeffnet.

## Modus Waehlen

Im Abschnitt `Projektmodus` einen der beiden Toolbar-Eintraege auswaehlen:

- `Legacy Interactive Agents`
- `FunctionalMLDS`

Beim Umschalten des Modus wird der aktuelle Draft geloescht. Die MLDSI-Datei und Backend-URL bleiben erhalten, danach muss erneut analysiert werden.

## MLDS Laden

Die MLDS/MLDSI-Datei wird im Wizard per Drag-and-drop geladen:

1. JSON- oder `.mldsi`-Asset in den Bereich `MLDSI-JSON hierhin ziehen` ziehen.
2. Der Wizard liest die Datei und zeigt den Dateipfad an.
3. Optional im Feld `Projekt-ID (optional)` bereits eine stabile ID eintragen.

Im FunctionalMLDS-Modus ist eine stabile Projekt-ID besonders sinnvoll, weil sie als `project_id_hint` an das Backend geht und dadurch Case-ID, FunctionalMLDS-Artefakte und Runtime-Projekt eindeutig zusammenhaelt.

## Analyse Ausfuehren

Button `MLDSI analysieren` startet `POST /projects/arrow/analyze`.

Im Legacy-Modus sendet der Wizard:

- `arrow_json`
- `generation_mode = "legacy"`

Erwartetes Analyseergebnis:

- Projektvorschlag
- vorgeschlagene Agenten
- Wissenseintraege
- Platzierungsvorschau

Im FunctionalMLDS-Modus sendet der Wizard:

- `arrow_json`
- `generation_mode = "functionalmlds"`
- `project_id_hint`
- `run_validation = true`
- `max_repair_attempts = 3`

Erwartetes Analyseergebnis:

- alle Legacy-Preview-Daten
- Metamodell-Artefaktpfad zu `functionalmlds.instance.generated.json`
- Validierungsstatus
- Use-Case-/Szenario-Zusammenfassung
- Capability-/Runtime-Zusammenfassung
- Handoff-/Spezialwissen-Zusammenfassung
- Raumwissen-/Grounding-Zusammenfassung

Eine FunctionalMLDS-Analyse ist nur eine Preview. Runtime-Projektdateien gelten erst nach erfolgreichem Commit als final.

## Optionaler Chat Im Wizard

Der Wizard besitzt einen Chatbereich fuer Aenderungswuensche am Draft.

Im Legacy-Modus kann der Chat den Draft direkt weiterentwickeln.

Im FunctionalMLDS-Modus werden Chat-Aenderungswuensche als Refinement Requests vorgemerkt. Der Draft wird dadurch als nicht final validiert markiert. Ein finaler Commit darf erst nach erneuter Regeneration/Validierung erfolgen, damit die Aenderung im Metamodell sichtbar und pruefbar bleibt.

## Projekt Committen

Im Abschnitt `Projekt erstellen` Felder setzen:

- `Name`
- `Projekt-ID (optional)`
- `Beschreibung`

Button `Abschliessen` startet `POST /projects/arrow/commit`.

Legacy-Commit erzeugt:

- `projects/<project_id>/project.json`
- `projects/<project_id>/room_plan.json`
- `projects/<project_id>/agents.json`
- `projects/<project_id>/kb/...`

Legacy-Commit erzeugt keine FunctionalMLDS-Pflichtartefakte, also insbesondere keine `trace_map.json` und kein `functionalmlds/`-Verzeichnis.

FunctionalMLDS-Commit erzeugt bzw. validiert:

- `projects/<project_id>/project.json`
- `projects/<project_id>/room_plan.json`
- `projects/<project_id>/agents.json`
- `projects/<project_id>/kb/...`
- `projects/<project_id>/trace_map.json`
- `output/wizard_functionalmlds/<project_id>/functionalmlds/functionalmlds.instance.generated.json`
- Validierungsreports unter `output/wizard_functionalmlds/<project_id>/validation/...`

Der Commit gilt nur als final, wenn die Backend-Antwort `status = "ok"` und `validation_summary.status = "valid"` liefert.

## FunctionalMLDS-Evidenz Im Wizard

Nach erfolgreichem FunctionalMLDS-Commit zeigt der Wizard die Commit-Evidenz an:

- Commit-Status
- FunctionalMLDS-Pfad
- Trace-Map-Pfad
- Metamodell-Kurzfassung
- Schema-/Invariant-/Materialisierungs-/Traceability-/Handoff-Status
- Fehler- und Warnungslisten

Diese Anzeige ist wichtig, weil sie zeigt, dass nicht nur ein Runtime-Projekt entstanden ist, sondern dass dieses Projekt durch eine Metamodell-Instanz und Validierungsartefakte belegt ist.

## Projekt In QuickAgentManager Starten

Nach dem Commit wird das Projekt in der Runtime ueber `QuickAgentManager` gestartet:

1. Szene mit `QuickAgentManager` starten.
2. Im On-Screen-UI `Projekt` statt `Pfade` waehlen.
3. `Projektliste laden` klicken.
4. Das committete Projekt auswaehlen.
5. `Setup erneut vom Server` klicken.

QuickAgentManager sendet dann `POST /setup` mit:

- `project_id = <ausgewaehltes Projekt>`
- `memory_mode = shared_history` oder `agent_private_history`

Erwartetes Ergebnis:

- Backend liefert eine `session_id`.
- Alle Agenten werden mit Position und Forward-Vektor geladen.
- Agenten spawnen in Unity.
- Chatfragen koennen gestellt werden.
- Handoff-Ereignisse werden im Chatlog sichtbar, wenn ein anderer Agent fachlich besser passt.

## Woran Man Sieht, Dass FunctionalMLDS Getestet Wird

FunctionalMLDS ist nicht schon dadurch getestet, dass Agenten spawnen. Es ist getestet, wenn alle folgenden Punkte gleichzeitig erfuellt sind:

- Wizard wurde im Modus `FunctionalMLDS` genutzt.
- Analyze-Draft zeigt `validation_summary.status = valid`.
- Commit liefert `status = ok`.
- Commit liefert `validation_summary.status = valid`.
- `functionalmlds.instance.generated.json` existiert.
- `trace_map.json` existiert.
- `trace_map.json` referenziert Runtime-Aktionen des Interactive-Agents-Projekts.
- `QuickAgentManager` kann dasselbe Projekt per `project_id` starten.
- Agenten koennen Raum- und Objektfragen aus MLDS-/KB-Wissen beantworten.
- Handoffs folgen den im FunctionalMLDS-/Agentenmodell abgeleiteten Spezialwissen- und Zustaendigkeitsbeziehungen.

Damit ist der Ablauf fuer eine Case Study nachvollziehbar: dieselbe MLDS wird analysiert, in FunctionalMLDS ueberfuehrt, validiert, als Runtime-Projekt materialisiert und anschliessend in Unity ausgefuehrt.
