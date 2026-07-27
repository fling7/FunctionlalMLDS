# Anwendungsfall B: StateAssertions des Hauptszenarios

Stand: 2026-07-07

Task: 7.6 `StateAssertions fuer B bestimmen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Quelle:

- `use_case_B_main_scenario_steps.md`
- `use_case_B_step_kinds.md`
- `use_case_B_events.md`
- `use_case_B_conditions.md`
- `use_case_B_coffee_machine_states.md`
- `use_case_B_vivian_classification.md`
- `use_case_B_coffee_machine_classification.md`

## Zweck

Diese Datei legt die `StateAssertion`-Kandidaten fuer den erfolgreichen Hauptpfad von `UC-B-01` fest. Eine `StateAssertion` beschreibt einen erwarteten oder beobachtbaren Zustand eines eindeutig referenzierbaren Subjekts.

Die zentrale Trennung lautet:

- Kaffeemaschinenzustand: `subjectRef = ENT-B-02 CoffeeMachine`
- Vivian-Zustand oder Vivian-Rueckmeldung: `subjectRef = ENT-B-01 VivianAssistant`
- Kontextobjekt Tasse: `subjectRef = ENT-B-03 Cup`
- Fachlicher Startwunsch: `subjectRef = ENT-B-04 BrewingRequest`

Benutzerfeedback wird nicht als innerer Zustand des Actors `ACT-B-01 Visitor` modelliert. Stattdessen wird modelliert, dass eine Rueckmeldung fuer den Benutzer sichtbar, hoerbar oder fachlich gemeldet ist. Das Subjekt der Zustandsaussage bleibt also die rueckmeldende Entity, z. B. `CoffeeMachine` oder `VivianAssistant`.

## Modellierungsregel

Im Metamodell besitzt `StateAssertion` genau:

- `subjectRef: Identifiable [1]`
- `expectedState: String`

`ScenarioStep -> StateAssertion : resultingState [0..*]` erlaubt, dass ein Schritt keine, eine oder mehrere resultierende Zustandsaussagen referenziert.

Eine StateAssertion wird nur angelegt, wenn der Zustand fachlich relevant, beobachtbar oder fuer spaetere Validierung verwendbar ist. Reine Events und reine Guards werden nicht noch einmal als StateAssertion dupliziert.

## Subjektkatalog

| subjectRef | Metamodell-Einordnung | Verwendung in 7.6 | Begruendung |
| --- | --- | --- | --- |
| `ENT-B-01 VivianAssistant` | `Agent` und damit `Entity` | Assistenzmodus, Anleitung, Rueckfrage, Abschlussmeldung | Vivian ist im Basismodell eine modellierte Assistenzinstanz im System. |
| `ENT-B-02 CoffeeMachine` | `Entity` | Objektzustand, Bereitschaftsmerkmale, Maschinenfeedback | Die Kaffeemaschine ist das zentrale Interaktionsobjekt. |
| `ENT-B-03 Cup` | `Entity`-Kandidat | Tassenplatzierung | Die Tasse ist ein relevantes Kontextobjekt fuer `cupPresent`. |
| `ENT-B-04 BrewingRequest` | fachliches `Entity`-/Identifiable-Kandidat | Startwunsch, Bestaetigung, Startausloesung | Der Startwunsch wird in Events und Conditions bereits als eigener fachlicher Zustand verwendet. |

`ENT-B-03` und `ENT-B-04` erzwingen keine Kernmetamodell-Erweiterung. Sie sind fachliche Instanzkandidaten, damit StateAssertions nicht auf unidentifizierbare Freitextobjekte zeigen.

## StateAssertion-Katalog

| StateAssertion-ID | subjectRef | `expectedState` | Kategorie | Herkunft | Hauptpfad-Schritt |
| --- | --- | --- | --- | --- | --- |
| `SA-B-VIVIAN-GUIDING` | `ENT-B-01 VivianAssistant` | `VivianAssistant.mode = guiding` | Vivian-Rueckmeldung/Systemzustand | `B-ACT-001`, `B-ACT-010`, `B-E02` | `B-MAIN-S02` |
| `SA-B-VIVIAN-GUIDANCE-CUP` | `ENT-B-01 VivianAssistant` | `VivianAssistant.guidanceTopic = placeCup` | Benutzerfeedback durch Vivian | `B-ACT-010` | `B-MAIN-S03` |
| `SA-B-CUP-PLACED` | `ENT-B-03 Cup` | `Cup.state = placed` | Kontextobjektzustand | `B-ACT-002`, `B-E03` | `B-MAIN-S04` |
| `SA-B-CM-CUP-PRESENT` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.cupPresent = true` | Kaffeemaschinenzustand | `B-CM-ST-016`, `B-E04` | `B-MAIN-S05` |
| `SA-B-VIVIAN-GUIDANCE-PROGRAM` | `ENT-B-01 VivianAssistant` | `VivianAssistant.guidanceTopic = selectProgram` | Benutzerfeedback durch Vivian | `B-ACT-010` | `B-MAIN-S06` |
| `SA-B-CM-PROGRAM-COFFEE` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.selectedProgram = coffee` | Kaffeemaschinenzustand | `B-CM-ST-018`, `B-E06` | `B-MAIN-S08` |
| `SA-B-CM-SELECTION-FEEDBACK` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.selectionFeedback = visible` | Benutzerfeedback durch Kaffeemaschine | `B-CM-ST-022`, `B-E06` | `B-MAIN-S08` |
| `SA-B-BREWING-REQUESTED` | `ENT-B-04 BrewingRequest` | `BrewingRequest.state = requested` | fachlicher Request-Zustand | `B-ACT-004`, `B-E07`, `B-E08` | `B-MAIN-S09` |
| `SA-B-VIVIAN-INTENT-CONFIRMED` | `ENT-B-01 VivianAssistant` | `VivianAssistant.feedbackState = intentConfirmed` | Vivian-Rueckmeldung/Systemzustand | `B-ACT-009`, `B-E08` | `B-MAIN-S10` |
| `SA-B-CM-READY` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.lifecycleState = ready` | Kaffeemaschinenzustand | `B-CM-ST-006`, `B-E09` | `B-MAIN-S12` |
| `SA-B-CM-READY-FEEDBACK` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.readyFeedback = visible` | Benutzerfeedback durch Kaffeemaschine | `B-CM-ST-021`, `B-E09` | `B-MAIN-S12` |
| `SA-B-CM-START-PERMISSION` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.startPermission = allowed` | Kaffeemaschinenzustand | `B-CM-ST-019`, `B-MAIN-G08` | `B-MAIN-S12` |
| `SA-B-VIVIAN-AWAITING-CONFIRMATION` | `ENT-B-01 VivianAssistant` | `VivianAssistant.feedbackState = awaitingConfirmation` | Benutzerfeedback durch Vivian | `B-ACT-013`, `B-E10` | `B-MAIN-S13` |
| `SA-B-BREWING-CONFIRMED` | `ENT-B-04 BrewingRequest` | `BrewingRequest.confirmed = true` | fachlicher Request-Zustand | `B-ACT-005`, `B-E11` | `B-MAIN-S14` |
| `SA-B-BREWING-START-ISSUED` | `ENT-B-04 BrewingRequest` | `BrewingRequest.executionState = startIssued` | fachlicher Request-Zustand | `B-ACT-014`, `B-E12` | `B-MAIN-S15` |
| `SA-B-CM-BREWING` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.lifecycleState = brewing` | Kaffeemaschinenzustand | `B-CM-ST-008`, `B-E13` | `B-MAIN-S16` |
| `SA-B-CM-PROGRESS-VISIBLE` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.progressIndicator = visible` | Benutzerfeedback durch Kaffeemaschine | `B-CM-ST-023`, `B-E14` | `B-MAIN-S17` |
| `SA-B-CM-FINISHED` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.lifecycleState = finished` | Kaffeemaschinenzustand | `B-CM-ST-009`, `B-E15` | `B-MAIN-S18` |
| `SA-B-CM-COMPLETION-FEEDBACK` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.completionFeedback = visible` | Benutzerfeedback durch Kaffeemaschine | `B-CM-ST-025`, `B-E16` | `B-MAIN-S19` |
| `SA-B-VIVIAN-COMPLETION-REPORTED` | `ENT-B-01 VivianAssistant` | `VivianAssistant.feedbackState = completionReported` | Benutzerfeedback durch Vivian | `B-ACT-016`, `B-E17` | `B-MAIN-S20` |

## `resultingState`-Zuordnung zu ScenarioSteps

| Nr. | ScenarioStep | Schrittart | `resultingState` | Begruendung |
| ---: | --- | --- | --- | --- |
| 1 | `B-MAIN-S01` | `actorIntent` | - | Der Hilfewunsch ist bereits als Event `B-E01` und Guard `B-MAIN-G01` modelliert; keine zusaetzliche Zustandsaussage noetig. |
| 2 | `B-MAIN-S02` | `systemResponse` | `SA-B-VIVIAN-GUIDING` | Vivian befindet sich danach im Fuehrungsmodus. |
| 3 | `B-MAIN-S03` | `systemResponse` | `SA-B-VIVIAN-GUIDANCE-CUP` | Der Benutzerhinweis zur Tasse ist als Vivian-Rueckmeldung beobachtbar. |
| 4 | `B-MAIN-S04` | `actorIntent` | `SA-B-CUP-PLACED` | Die Benutzerhandlung erzeugt einen pruefbaren Kontextobjektzustand. |
| 5 | `B-MAIN-S05` | `environmentObservation` | `SA-B-CM-CUP-PRESENT` | Die Maschine meldet die Tassenerkennung. |
| 6 | `B-MAIN-S06` | `systemResponse` | `SA-B-VIVIAN-GUIDANCE-PROGRAM` | Vivian fuehrt zum naechsten Bedienpunkt. |
| 7 | `B-MAIN-S07` | `actorIntent` | - | Die Auswahlhandlung wird erst durch die Maschinenbestaetigung in `B-MAIN-S08` als Objektzustand festgelegt. |
| 8 | `B-MAIN-S08` | `environmentObservation` | `SA-B-CM-PROGRAM-COFFEE`, `SA-B-CM-SELECTION-FEEDBACK` | Auswahl und sichtbare Bestaetigung sind getrennte, parallele Zustandsaussagen. |
| 9 | `B-MAIN-S09` | `actorIntent` | `SA-B-BREWING-REQUESTED` | Das Druecken der Starttaste erzeugt den fachlichen Startwunsch. |
| 10 | `B-MAIN-S10` | `systemResponse` | `SA-B-VIVIAN-INTENT-CONFIRMED` | Vivian bestaetigt die erkannte Bruehanforderung. |
| 11 | `B-MAIN-S11` | `systemResponse` | - | Die Bereitschaftspruefung ist eine fachliche Capability-Nutzung; ihr positives Ergebnis wird in `B-MAIN-S12` objektseitig sichtbar. |
| 12 | `B-MAIN-S12` | `environmentObservation` | `SA-B-CM-READY`, `SA-B-CM-READY-FEEDBACK`, `SA-B-CM-START-PERMISSION` | Bereitschaft, Startfreigabe und sichtbares Feedback bleiben getrennte Maschinenzustaende. |
| 13 | `B-MAIN-S13` | `systemResponse` | `SA-B-VIVIAN-AWAITING-CONFIRMATION` | Vivian wartet fachlich auf die explizite Freigabe. |
| 14 | `B-MAIN-S14` | `actorIntent` | `SA-B-BREWING-CONFIRMED` | Die Benutzerfreigabe macht den Startwunsch bestaetigt. |
| 15 | `B-MAIN-S15` | `systemResponse` | `SA-B-BREWING-START-ISSUED` | Der Bruehstart wurde fachlich ausgeloest; technische Ausfuehrung bleibt spaeter RuntimeBinding. |
| 16 | `B-MAIN-S16` | `environmentObservation` | `SA-B-CM-BREWING` | Die Maschine befindet sich im Bruehzustand. |
| 17 | `B-MAIN-S17` | `environmentObservation` | `SA-B-CM-PROGRESS-VISIBLE` | Der Fortschritt ist sichtbar und damit validierbar. |
| 18 | `B-MAIN-S18` | `environmentObservation` | `SA-B-CM-FINISHED` | Die Maschine erreicht den fachlichen Abschlusszustand. |
| 19 | `B-MAIN-S19` | `environmentObservation` | `SA-B-CM-COMPLETION-FEEDBACK` | Die Abschlussrueckmeldung ist sichtbar. |
| 20 | `B-MAIN-S20` | `systemResponse` | `SA-B-VIVIAN-COMPLETION-REPORTED` | Vivian meldet den erfolgreichen Abschluss. |

## Trennung der Zustandsarten

| Zustandsart | StateAssertions | Zweck |
| --- | --- | --- |
| Kaffeemaschinenzustand | `SA-B-CM-CUP-PRESENT`, `SA-B-CM-PROGRAM-COFFEE`, `SA-B-CM-READY`, `SA-B-CM-START-PERMISSION`, `SA-B-CM-BREWING`, `SA-B-CM-FINISHED` | Objekt- und Bereitschaftszustaende des Interaktionsobjekts. |
| Vivian-Rueckmeldung/Systemzustand | `SA-B-VIVIAN-GUIDING`, `SA-B-VIVIAN-INTENT-CONFIRMED` | Interner oder fachlicher Assistenzzustand von Vivian. |
| Benutzerfeedback durch Vivian | `SA-B-VIVIAN-GUIDANCE-CUP`, `SA-B-VIVIAN-GUIDANCE-PROGRAM`, `SA-B-VIVIAN-AWAITING-CONFIRMATION`, `SA-B-VIVIAN-COMPLETION-REPORTED` | Fuer den Benutzer wahrnehmbare Vivian-Kommunikation. |
| Benutzerfeedback durch Kaffeemaschine | `SA-B-CM-SELECTION-FEEDBACK`, `SA-B-CM-READY-FEEDBACK`, `SA-B-CM-PROGRESS-VISIBLE`, `SA-B-CM-COMPLETION-FEEDBACK` | Fuer den Benutzer sichtbare Objekt- oder Bedienrueckmeldung. |
| Kontext- und Request-Zustaende | `SA-B-CUP-PLACED`, `SA-B-BREWING-REQUESTED`, `SA-B-BREWING-CONFIRMED`, `SA-B-BREWING-START-ISSUED` | Zustandsaussagen, die nicht der Kaffeemaschine selbst gehoeren, aber den Ablauf pruefbar machen. |

## Beziehung zu Conditions

| Condition | Relevante StateAssertion | Bemerkung |
| --- | --- | --- |
| `B-MAIN-G02` | `SA-B-VIVIAN-GUIDING` | Der aktive Fuehrungsmodus wird als Vivian-Zustand pruefbar. |
| `B-MAIN-G03` | `SA-B-CM-CUP-PRESENT` | Tassenerkennung wird als Maschinenzustand geprueft. |
| `B-MAIN-G04` | `SA-B-CM-PROGRAM-COFFEE` | Programmauswahl wird als Maschinenzustand geprueft. |
| `B-MAIN-G05` | `SA-B-BREWING-REQUESTED` | Die aktive Startanforderung wird als Request-Zustand geprueft. |
| `B-MAIN-G06` | `SA-B-CM-CUP-PRESENT`, `SA-B-CM-PROGRAM-COFFEE`, `SA-B-CM-READY` | Die positive Bereitschaft verbindet Bereitschaftsmerkmale und Lebenszykluszustand. |
| `B-MAIN-G08` | `SA-B-BREWING-CONFIRMED`, `SA-B-CM-START-PERMISSION`, `SA-B-CM-READY` | Der Bruehstart setzt Freigabe, Startpermission und positive Bereitschaft voraus. |
| `B-MAIN-G09` | `SA-B-CM-BREWING` | Fortschritt ist nur im Bruehzustand sinnvoll. |
| `B-MAIN-G10` | `SA-B-CM-FINISHED` | Abschlussfeedback setzt den Abschlusszustand voraus. |
| `B-MAIN-G11` | `SA-B-CM-COMPLETION-FEEDBACK` | Vivians Abschlussmeldung folgt auf sichtbares Abschlussfeedback. |

## Abnahmekontrolle

| Kriterium aus Task 7.6 | Erfuellung |
| --- | --- |
| Objekt- und Systemzustandsaussagen vorhanden | 20 StateAssertions sind angelegt. |
| Kaffeemaschinenzustand trennbar | Objektzustaende der Kaffeemaschine nutzen `ENT-B-02 CoffeeMachine` als subjectRef. |
| Vivian-Rueckmeldung trennbar | Vivian-Zustaende und Vivian-Kommunikation nutzen `ENT-B-01 VivianAssistant` als subjectRef. |
| Benutzerfeedback trennbar | Benutzerfeedback wird als sichtbare oder gemeldete Rueckmeldung der ausgebenden Entity modelliert. |
| `ScenarioStep.resultingState [0..*]` eingehalten | Alle 20 Schritte haben eine Zuordnung oder eine begruendete leere Zuordnung. |
| Keine technische Direktkopplung | Keine StateAssertion referenziert API, Topic, Tool, Controller oder RuntimeAction. |
| Anschluss an Conditions vorhanden | Die relevanten Guards aus 7.5 sind auf StateAssertions abbildbar. |

## Konsequenz fuer Task 7.7

Task 7.7 kann nun die `StepRelation`-Kanten fuer B definieren. Die resultierenden Zustandsaussagen helfen dabei, saubere Sequenz-, Alternativ- und Exception-Kanten zu begruenden, ohne Conditions und StateAssertions zu vermischen.
