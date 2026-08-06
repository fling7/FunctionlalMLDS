# Anwendungsfall B: Conditions des Hauptszenarios

Stand: 2026-07-07

Task: 7.5 `Conditions fuer B bestimmen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Quelle:

- `use_case_B_preconditions.md`
- `use_case_B_events.md`
- `use_case_B_step_kinds.md`
- `use_case_B_coffee_machine_states.md`

## Zweck

Diese Datei legt die Conditions fuer den erfolgreichen Hauptpfad von `UC-B-01` fest. Sie operationalisiert den breiteren Condition-Katalog aus Task 6.7 fuer das konkrete Main Scenario.

Die Conditions werden bewusst nicht als technische Aufrufe formuliert. Sie bleiben fachlich und pruefbar:

- Scenario-Preconditions beschreiben, was vor dem erfolgreichen Hauptpfad gelten muss.
- Guard-Conditions entscheiden, ob ein Schritt oder spaeter eine `StepRelation` im Hauptpfad zulaessig ist.
- Scenario-Postconditions beschreiben, was nach erfolgreichem Abschluss gelten muss.

## Modellierungsregel

Im aktuellen Metamodell gilt:

- `Scenario.pre/postcondition [0..*]`: Ein Scenario darf mehrere Vor- und Nachbedingungen besitzen.
- `ScenarioStep -> Condition : guard [0..1]`: Ein ScenarioStep darf hoechstens eine direkte Guard-Condition referenzieren.
- `StepRelation.guard [0..1]`: Eine Ablaufbeziehung darf hoechstens eine Guard-Condition besitzen.

Wenn ein Ablaufgate mehrere fachliche Fakten benoetigt, wird deshalb genau eine zusammengesetzte Guard-Expression gebildet. Dadurch bleiben Kardinalitaeten und Lesbarkeit erhalten.

Events aus Task 7.4 werden nicht noch einmal als Conditions dupliziert, ausser wenn sie wirklich eine Ablaufentscheidung ausdruecken, zum Beispiel `helpRequested = true` oder `BrewingRequest.confirmed = true`.

## Scenario-Preconditions

Diese Preconditions gehoeren auf das Main Scenario `SC-B-01-MAIN`. Sie beschreiben Voraussetzungen des erfolgreichen Hauptpfads, nicht alle denkbaren Fehler- oder Korrekturfaelle.

| Condition-ID | `Condition.kind` | Ausdruck | Herkunft | Belegung im Modell | Begruendung |
| --- | --- | --- | --- | --- | --- |
| `B-MAIN-PRE-01` | `pre` | `Visitor is present and able to interact` | `B-COND-019` | `Scenario.precondition` | Ohne interaktionsfaehigen Visitor ist der Use Case nicht ausfuehrbar. |
| `B-MAIN-PRE-02` | `pre` | `CoffeeMachine.availabilityState = available` | `B-COND-001` | `Scenario.precondition` | Die Kaffeemaschine muss fachlich verfuegbar sein. |
| `B-MAIN-PRE-03` | `pre` | `CoffeeMachine.powerState = on` | `B-COND-002` | `Scenario.precondition` | Eine ausgeschaltete Maschine gehoert in einen Fehler- oder Korrekturpfad. |
| `B-MAIN-PRE-04` | `pre` | `CoffeeMachine.lifecycleState in {idle, ready, notReady}` | `B-COND-003` | `Scenario.precondition` | Der Ablauf darf nicht mitten in `brewing`, `finished`, `error` oder `cancelled` starten. |
| `B-MAIN-PRE-05` | `pre` | `VivianAssistant.mode can become guiding` | `B-COND-004` | `Scenario.precondition` | Das Beispiel beschreibt assistierte Bedienung mit Vivian; der Assistenzmodus muss fachlich erreichbar sein. |

Nicht als Scenario-Precondition modelliert werden `cupPresent`, `selectedProgram`, `waterLevel`, `BrewingRequest` und `startPermission`, weil sie im Ablauf hergestellt oder geprueft werden. Sie gehoeren in Guards.

## Guard-Conditions des Hauptpfads

| Condition-ID | `Condition.kind` | Ausdruck | Primaerer Einsatz | Herkunft | Ablaufentscheidung |
| --- | --- | --- | --- | --- | --- |
| `B-MAIN-G01` | `guard` | `helpRequested = true` | Start von `B-MAIN-S01` beziehungsweise Relation in den Main Path | `B-COND-005`, `B-E01` | Trennt assistierte Bedienung von einem unassistierten Bedienpfad. |
| `B-MAIN-G02` | `guard` | `VivianAssistant.mode = guiding` | `B-MAIN-S03` | `B-E02`, `B-MAIN-PRE-05` | Vivian darf Bedienhinweise erst geben, wenn der Fuehrungsmodus aktiv ist. |
| `B-MAIN-G03` | `guard` | `CoffeeMachine.cupPresent = true` | `B-MAIN-S06` | `B-COND-006`, `B-E04`, `B-CM-ST-016` | Programmauswahl wird im Hauptpfad erst gefuehrt, nachdem eine Tasse erkannt wurde. |
| `B-MAIN-G04` | `guard` | `CoffeeMachine.selectedProgram != none` | `B-MAIN-S09` | `B-COND-008`, `B-E06`, `B-CM-ST-018` | Ein Startwunsch ist im Hauptpfad erst sinnvoll, wenn ein Programm gewaehlt ist. |
| `B-MAIN-G05` | `guard` | `BrewingRequest.state = requested and BrewingRequest.state != cancelled` | `B-MAIN-S11` | `B-COND-010`, `B-COND-012`, `B-E08` | Die Bereitschaftspruefung wird nur fuer eine aktive Startanforderung ausgefuehrt. |
| `B-MAIN-G06` | `guard` | `ReadinessCheck.result = passed and CoffeeMachine.cupPresent = true and CoffeeMachine.waterLevel = sufficient and CoffeeMachine.selectedProgram != none and CoffeeMachine.lifecycleState != brewing and CoffeeMachine.lifecycleState != error` | Positive Verzweigung nach `B-MAIN-S11`, insbesondere `B-MAIN-S12` | `B-COND-006`, `B-COND-007`, `B-COND-008`, `B-COND-013`, `B-COND-014`, `B-COND-017`, `B-E09` | Trennt den erfolgreichen Hauptpfad von Korrektur- und Exception-Pfaden. |
| `B-MAIN-G07` | `guard` | `confirmationRequested(VivianAssistant, BrewingRequest) and BrewingRequest.state != cancelled` | `B-MAIN-S14` | `B-COND-012`, `B-E10` | Eine Benutzerbestaetigung ist nur nach Vivians ausdruecklicher Rueckfrage gueltig. |
| `B-MAIN-G08` | `guard` | `BrewingRequest.confirmed = true and CoffeeMachine.startPermission = allowed and ReadinessCheck.result = passed and BrewingRequest.state != cancelled` | `B-MAIN-S15` | `B-COND-009`, `B-COND-011`, `B-COND-012`, `B-COND-017`, `B-E11`, `B-E12` | Das System darf den Bruehstart nur nach bestaetigter Freigabe und positiver Bereitschaft ausloesen. |
| `B-MAIN-G09` | `guard` | `CoffeeMachine.lifecycleState = brewing` | `B-MAIN-S17` | `B-E13`, `B-CM-ST-008` | Fortschrittsfeedback ist nur im laufenden Bruehvorgang Teil des Hauptpfads. |
| `B-MAIN-G10` | `guard` | `CoffeeMachine.lifecycleState = finished` | `B-MAIN-S19` | `B-E15`, `B-CM-ST-009` | Abschlussfeedback wird erst nach erreichtem Abschlusszustand erwartet. |
| `B-MAIN-G11` | `guard` | `CoffeeMachine.completionFeedback = visible` | `B-MAIN-S20` | `B-E16`, `B-CM-ST-025` | Vivians Abschlussmeldung folgt im Hauptpfad auf die sichtbare Abschlussrueckmeldung. |

## Scenario-Postconditions

Diese Postconditions beschreiben den erfolgreichen Abschluss von `SC-B-01-MAIN`. Konkrete `StateAssertion`-Instanzen werden in Task 7.6 angelegt.

| Condition-ID | `Condition.kind` | Ausdruck | Herkunft | Belegung im Modell | Begruendung |
| --- | --- | --- | --- | --- | --- |
| `B-MAIN-POST-01` | `post` | `CoffeeMachine.lifecycleState = finished` | `B-CM-ST-009`, `B-E15` | `Scenario.postcondition` | Der erfolgreiche Hauptpfad endet nach abgeschlossenem Bruehvorgang. |
| `B-MAIN-POST-02` | `post` | `CoffeeMachine.completionFeedback = visible` | `B-CM-ST-025`, `B-E16` | `Scenario.postcondition` | Der Abschluss muss fuer Benutzer und ValidationCase beobachtbar sein. |
| `B-MAIN-POST-03` | `post` | `VivianAssistant.feedbackState = completionReported` | `B-ACT-016`, `B-E17` | `Scenario.postcondition` | Vivian hat den Abschluss fachlich gemeldet. |
| `B-MAIN-POST-04` | `post` | `BrewingRequest.state != cancelled` | `B-COND-012` | `Scenario.postcondition` | Der erfolgreiche Hauptpfad darf nicht als Abbruch enden. |
| `B-MAIN-POST-05` | `post` | `CoffeeMachine.lifecycleState != error` | `B-COND-014` | `Scenario.postcondition` | Der erfolgreiche Hauptpfad endet nicht im Fehlerzustand. |

## Guard-Zuordnung zu ScenarioSteps

Die Tabelle legt fest, welche direkte Guard-Condition ein Schritt im Hauptpfad erhalten soll. Schritte ohne echte Ablaufentscheidung bleiben ohne direkte Guard, damit keine kuenstlichen Bedingungen entstehen.

| Nr. | ScenarioStep | Schrittart | Direkte Guard-Condition | Begruendung |
| ---: | --- | --- | --- | --- |
| 1 | `B-MAIN-S01` | `actorIntent` | `B-MAIN-G01` | Der assistierte Pfad startet nur bei Hilfewunsch. |
| 2 | `B-MAIN-S02` | `systemResponse` | - | Vivian reagiert direkt auf `B-E01`; die Szenario-Preconditions reichen. |
| 3 | `B-MAIN-S03` | `systemResponse` | `B-MAIN-G02` | Bedienhinweise setzen aktiven Fuehrungsmodus voraus. |
| 4 | `B-MAIN-S04` | `actorIntent` | - | Das Platzieren der Tasse ist die Benutzerhandlung selbst. |
| 5 | `B-MAIN-S05` | `environmentObservation` | - | Die Tassenerkennung ist eine Beobachtung, keine weitere Entscheidung. |
| 6 | `B-MAIN-S06` | `systemResponse` | `B-MAIN-G03` | Vivian fuehrt erst nach erkannter Tasse zur Programmauswahl. |
| 7 | `B-MAIN-S07` | `actorIntent` | - | Programmauswahl ist Benutzerhandlung. |
| 8 | `B-MAIN-S08` | `environmentObservation` | - | Auswahlbestaetigung ist eine Beobachtung der Maschine. |
| 9 | `B-MAIN-S09` | `actorIntent` | `B-MAIN-G04` | Starttaste im Hauptpfad erst nach vorhandener Programmauswahl. |
| 10 | `B-MAIN-S10` | `systemResponse` | - | Vivian bestaetigt das Start-Event `B-E07`. |
| 11 | `B-MAIN-S11` | `systemResponse` | `B-MAIN-G05` | Bereitschaftspruefung setzt aktive, nicht abgebrochene Startanforderung voraus. |
| 12 | `B-MAIN-S12` | `environmentObservation` | `B-MAIN-G06` | Nur positive Bereitschaft fuehrt in den erfolgreichen Hauptpfad. |
| 13 | `B-MAIN-S13` | `systemResponse` | - | Die Rueckfrage folgt aus der positiven Bereitschaft. |
| 14 | `B-MAIN-S14` | `actorIntent` | `B-MAIN-G07` | Die Bestaetigung ist nur nach Vivians Rueckfrage gueltig. |
| 15 | `B-MAIN-S15` | `systemResponse` | `B-MAIN-G08` | Der assistierte Start verlangt Freigabe, Startpermission und bestandene Pruefung. |
| 16 | `B-MAIN-S16` | `environmentObservation` | - | Der Wechsel nach `brewing` ist ein resultierender Objektzustand. |
| 17 | `B-MAIN-S17` | `environmentObservation` | `B-MAIN-G09` | Fortschritt wird nur im Bruehzustand erwartet. |
| 18 | `B-MAIN-S18` | `environmentObservation` | - | Der Wechsel nach `finished` ist resultierender Objektzustand. |
| 19 | `B-MAIN-S19` | `environmentObservation` | `B-MAIN-G10` | Abschlussfeedback setzt den fertigen Maschinenzustand voraus. |
| 20 | `B-MAIN-S20` | `systemResponse` | `B-MAIN-G11` | Vivian meldet Abschluss erst nach sichtbarer Abschlussrueckmeldung. |

## Entscheidungsabdeckung

| Ablaufentscheidung | Noetige Condition(s) | Warum nicht mehr? |
| --- | --- | --- |
| Einstieg in assistierte Bedienung | `B-MAIN-G01` | Systemverfuegbarkeit und Vivian-Faehigkeit liegen bereits als Scenario-Preconditions vor. |
| Fuehrung zur Programmauswahl | `B-MAIN-G03` | Wasserstand und Startpermission sind an dieser Stelle noch nicht entscheidungsrelevant. |
| Startanforderung nach Programmauswahl | `B-MAIN-G04` | Die Programmauswahl ist noetig; Bereitschaft wird erst danach geprueft. |
| Bereitschaftspruefung ausfuehren | `B-MAIN-G05` | Ohne aktive Startanforderung waere die Pruefung fachlich verfrueht. |
| Positive Bereitschaft gegen Korrektur/Exception abgrenzen | `B-MAIN-G06` | Alle Startbedingungen werden in genau einer zusammengesetzten Guard gebuendelt. |
| Benutzerfreigabe einholen | `B-MAIN-G07` | Eine Bestaetigung ohne vorherige Rueckfrage waere mehrdeutig. |
| Assistierten Start ausloesen | `B-MAIN-G08` | Startfreigabe, bestaetigte Anfrage und positive Bereitschaft sind gemeinsam noetig. |
| Fortschritt anzeigen | `B-MAIN-G09` | Fortschritt ist nur im Bruehzustand sinnvoll. |
| Abschlussfeedback anzeigen | `B-MAIN-G10` | Abschlussfeedback ist erst nach `finished` zulaessig. |
| Vivian-Abschlussmeldung ausgeben | `B-MAIN-G11` | Vivian meldet den Abschluss, wenn der Maschinenabschluss beobachtbar ist. |

## Nicht als Conditions modelliert

| Kandidat | Entscheidung | Begruendung |
| --- | --- | --- |
| `B-E03`, `B-E05`, `B-E07`, `B-E11` als reine User-Events | Nicht separat als Condition, ausser wo sie eine Entscheidung tragen. | Events sind bereits `triggeredBy`; doppelte Conditions wuerden den Ablauf aufblaehen. |
| Controller-, API-, Tool- oder Topic-Aufrufe | Nicht modelliert. | Technische Details gehoeren spaeter unter `RuntimeBinding -> RuntimeAction`. |
| Kaffeemaschinenzustand `brewing` oder `finished` als volle StateAssertion | Noch nicht formalisiert. | Task 7.6 legt die `StateAssertion`-Instanzen an. |
| Fehlerfaelle bei fehlender Tasse, fehlendem Wasser oder Maschinenfehler | Nur ueber negierte Guards vorbereitet. | Alternative und Exception-Szenarien folgen spaeter in 7.9 und 7.10. |

## Abnahmekontrolle

| Kriterium aus Task 7.5 | Erfuellung |
| --- | --- |
| Guard-, Pre- und Postconditions vorhanden | Scenario-Preconditions, Guard-Conditions und Scenario-Postconditions sind getrennt angelegt. |
| Jede Ablaufentscheidung hat genau die noetigen Conditions | Die Entscheidungsabdeckung listet jedes Gate mit der minimal noetigen Condition. |
| `ScenarioStep.guard [0..1]` eingehalten | Kein Schritt besitzt mehr als eine direkte Guard-Condition; zusammengesetzte Pruefungen sind eine Condition. |
| Anschluss an Events vorhanden | Guards referenzieren die fachlich relevanten Events aus Task 7.4 nur dort, wo sie entscheidungsrelevant sind. |
| Anschluss an StateAssertions vorbereitet | Postconditions und objektbezogene Guards zeigen auf die Zustandskandidaten fuer Task 7.6. |
| Keine technische Direktkopplung | Keine Condition nennt API, Topic, Tool, Controller oder RuntimeAction. |

## Konsequenz fuer Task 7.6

Task 7.6 kann nun aus den objekt- und systembezogenen Conditions konkrete `StateAssertion`-Instanzen ableiten. Besonders relevant sind:

- `CoffeeMachine.cupPresent = true`
- `CoffeeMachine.selectedProgram = coffee`
- `CoffeeMachine.lifecycleState = ready`
- `CoffeeMachine.lifecycleState = brewing`
- `CoffeeMachine.progressIndicator = visible`
- `CoffeeMachine.lifecycleState = finished`
- `CoffeeMachine.completionFeedback = visible`
- `VivianAssistant.feedbackState = completionReported`
