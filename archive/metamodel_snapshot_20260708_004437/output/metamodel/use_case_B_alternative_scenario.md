# Anwendungsfall B: Alternatives Szenario

Stand: 2026-07-07

Task: 7.9 `Alternatives Szenario B formulieren`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Entscheidung

| Feld | Wert |
| --- | --- |
| Scenario-ID | `SC-B-01-ALT01` |
| `Scenario.kind` | `alternative` |
| Sprechender Name | `Fehlende Tasse korrigieren` |
| Zugehoeriger Main Use Case | `UC-B-01 Assistierte Kaffeemaschinenbedienung mit Vivian` |
| Branch-Anker aus 7.7 | `B-BRANCH-A02` |
| Eintrittspunkt im Hauptpfad | nach `B-MAIN-S05` |
| Rueckkehrpunkt in den Hauptpfad | vor `B-MAIN-S06` |
| Abgedeckter Fall aus 6.8 | `B-ALT-003` |

## Warum dies eine Alternative und keine Exception ist

Dieses Szenario beschreibt keinen fatalen Fehler. Es beschreibt einen gueltigen anderen Ablauf, in dem eine fachliche Voraussetzung zunaechst fehlt, aber durch Benutzerhandlung hergestellt werden kann.

Der Hauptpfad nimmt an, dass nach der Tassenplatzierung die Kaffeemaschine `CoffeeMachine.cupPresent = true` meldet. Das alternative Szenario behandelt den Fall, dass die Tasse noch nicht erkannt wurde. Vivian fuehrt den Visitor zur Korrektur, der Visitor platziert oder richtet die Tasse neu aus, die Kaffeemaschine erkennt die Tasse, und der Ablauf kehrt danach zum Hauptpfad zurueck.

Damit gilt:

- kein Bruehstart wird ausgefuehrt, solange `cupPresent = false` gilt,
- der Benutzer kann die Situation fachlich korrigieren,
- der Use Case bleibt erfolgreich abschliessbar,
- die Alternative ist kein `Extend`, weil sie kein optionales Zusatzverhalten ist, sondern ein korrigierbarer Ablaufzweig.

## Scenario-Bedingungen

| Condition-ID | `Condition.kind` | Ausdruck | Verwendung | Begruendung |
| --- | --- | --- | --- | --- |
| `B-ALT-PRE-01` | `pre` | `CoffeeMachine.availabilityState = available and CoffeeMachine.powerState = on` | `Scenario.precondition` | Die Alternative setzt dieselbe verfuegbare virtuelle Kaffeemaschine wie der Hauptpfad voraus. |
| `B-ALT-G01` | `guard` | `CoffeeMachine.cupPresent = false` | Eintritt in `SC-B-01-ALT01` | Der alternative Pfad wird nur betreten, wenn die Tasse nicht erkannt wurde. |
| `B-ALT-G02` | `guard` | `CoffeeMachine.cupPresent = true` | Rueckkehr in den Hauptpfad | Nach erfolgreicher Korrektur darf der Ablauf vor `B-MAIN-S06` fortgesetzt werden. |
| `B-ALT-POST-01` | `post` | `CoffeeMachine.cupPresent = true` | `Scenario.postcondition` | Das alternative Szenario endet mit der hergestellten Tassenbedingung. |
| `B-ALT-POST-02` | `post` | `CoffeeMachine.lifecycleState != error` | `Scenario.postcondition` | Die Alternative endet nicht in einem Maschinenfehler. |

## Events

| Event-ID | `Event.kind` | `Event.expression` | Verwendung | Begruendung |
| --- | --- | --- | --- | --- |
| `B-ALT-E01` | `environment` | `stateChanged(CoffeeMachine.cupPresent, false)` | `B-ALT-S01` | Die Kaffeemaschine meldet, dass keine Tasse erkannt wurde. |
| `B-ALT-E02` | `signal` | `guidanceIssued(VivianAssistant, placeCupAgain)` | `B-ALT-S02` | Vivian gibt einen korrigierenden Hinweis. |
| `B-ALT-E03` | `user` | `placedOrAdjusted(Visitor, Cup, CoffeeMachine.cupArea)` | `B-ALT-S03` | Der Visitor korrigiert die Tassenplatzierung. |
| `B-E04` | `environment` | `stateChanged(CoffeeMachine.cupPresent, true)` | `B-ALT-S04` | Das bereits definierte Hauptpfad-Event wird wiederverwendet, wenn die Tasse erkannt ist. |

## StateAssertions

| StateAssertion-ID | subjectRef | `expectedState` | Neu oder wiederverwendet | Verwendung |
| --- | --- | --- | --- | --- |
| `SA-B-CM-CUP-MISSING` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.cupPresent = false` | neu fuer Alternative | `B-ALT-S01` |
| `SA-B-VIVIAN-CUP-CORRECTION-GUIDANCE` | `ENT-B-01 VivianAssistant` | `VivianAssistant.guidanceTopic = placeCupAgain` | neu fuer Alternative | `B-ALT-S02` |
| `SA-B-CUP-PLACED` | `ENT-B-03 Cup` | `Cup.state = placed` | wiederverwendet aus 7.6 | `B-ALT-S03` |
| `SA-B-CM-CUP-PRESENT` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.cupPresent = true` | wiederverwendet aus 7.6 | `B-ALT-S04` |

## ScenarioSteps

| Nr. | ScenarioStep-ID | `ScenarioStep.kind` | Text | performedBy | triggeredBy | guard | resultingState |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `B-ALT-S01` | `environmentObservation` | Die Kaffeemaschine meldet, dass keine Tasse erkannt wurde. | - | `B-ALT-E01` | `B-ALT-G01` | `SA-B-CM-CUP-MISSING` |
| 2 | `B-ALT-S02` | `systemResponse` | Vivian weist den Visitor darauf hin, die Tasse korrekt zu platzieren oder neu auszurichten. | - | `B-ALT-E02` | `B-ALT-G01` | `SA-B-VIVIAN-CUP-CORRECTION-GUIDANCE` |
| 3 | `B-ALT-S03` | `actorIntent` | Der Visitor platziert oder richtet die Tasse an der Kaffeemaschine neu aus. | `ACT-B-01 Visitor` | `B-ALT-E03` | - | `SA-B-CUP-PLACED` |
| 4 | `B-ALT-S04` | `environmentObservation` | Die Kaffeemaschine meldet, dass die Tasse nun vorhanden ist. | - | `B-E04` | `B-ALT-G02` | `SA-B-CM-CUP-PRESENT` |

## StepRelations

| Relation-ID | source step | target step | relation kind | guardRef | Begruendung |
| --- | --- | --- | --- | --- | --- |
| `B-ALT-R-IN01` | `B-MAIN-S05` | `B-ALT-S01` | `alternative` | `B-ALT-G01` | Wenn nach der Tassenplatzierung keine Tasse erkannt wird, verlaesst der Ablauf den Hauptpfad. |
| `B-ALT-R01` | `B-ALT-S01` | `B-ALT-S02` | `sequence` | `B-ALT-G01` | Vivian reagiert auf die fehlende Tassenerkennung mit einem Korrekturhinweis. |
| `B-ALT-R02` | `B-ALT-S02` | `B-ALT-S03` | `sequence` | - | Der Visitor kann auf Vivians Hinweis hin die Tasse korrigieren. |
| `B-ALT-R03` | `B-ALT-S03` | `B-ALT-S04` | `sequence` | - | Nach der Korrektur wird die Tassenerkennung erneut beobachtet. |
| `B-ALT-R-OUT01` | `B-ALT-S04` | `B-MAIN-S06` | `sequence` | `B-ALT-G02` | Sobald `cupPresent = true` gilt, kehrt der Ablauf zur Programmauswahl-Fuehrung des Hauptpfads zurueck. |

## Graphsicht

Der alternative Pfad haengt an `B-MAIN-S05` aus und kehrt vor `B-MAIN-S06` zurueck:

`B-MAIN-S05 -> B-ALT-S01 -> B-ALT-S02 -> B-ALT-S03 -> B-ALT-S04 -> B-MAIN-S06`

Damit bleibt der erfolgreiche Hauptpfad nach der Korrektur unveraendert:

`B-MAIN-S06 -> ... -> B-MAIN-S20`

## Modellierungsgrenzen

| Thema | Entscheidung |
| --- | --- |
| Keine technische Direktkopplung | Die Alternative nennt keinen Controller, keine API, kein Topic, kein Tool und keine RuntimeAction. |
| Keine Exception | Die Alternative endet mit `CoffeeMachine.cupPresent = true` und kehrt in den Hauptpfad zurueck. |
| Kein Extend | Der Ablauf ist keine optionale Zusatzfunktion, sondern ein korrigierbarer anderer Pfad innerhalb desselben Use Case. |
| Actor/Agent-Trennung | Nur `B-ALT-S03` ist `actorIntent` mit `ACT-B-01 Visitor`; Vivian bleibt `systemResponse`. |
| Objektzustand getrennt | Die Kaffeemaschine bleibt `Entity`; Tassenerkennung wird als `StateAssertion` modelliert. |

## Abnahmekontrolle

| Kriterium aus Task 7.9 | Erfuellung |
| --- | --- |
| `Scenario.kind = alternative` vorhanden | Ja: `SC-B-01-ALT01` ist als `alternative` festgelegt. |
| Alternative ist nicht bloss Fehlerfall | Ja. Die fehlende Tasse ist korrigierbar und fuehrt zur Rueckkehr in den Hauptpfad. |
| Steps sind fachlich eindeutig | Vier Schritte trennen Objektbeobachtung, Vivian-Hinweis, Benutzerkorrektur und erneute Objektbeobachtung. |
| Branch und Rejoin sind nachvollziehbar | Einstieg von `B-MAIN-S05`, Rueckkehr zu `B-MAIN-S06`. |
| Conditions sind minimal | Eintritt nutzt `cupPresent = false`, Rueckkehr nutzt `cupPresent = true`. |
| Keine technische Direktkopplung | Erfuellt. |

## Konsequenz fuer Task 7.10

Task 7.10 kann nun ein echtes Exception-Szenario formulieren. Geeignet ist ein nicht korrigierbarer Maschinen- oder Bereitschaftsfehler, der nicht in den Hauptpfad zurueckkehrt, sondern in einem sicheren oder erklaerbaren Zustand endet.
