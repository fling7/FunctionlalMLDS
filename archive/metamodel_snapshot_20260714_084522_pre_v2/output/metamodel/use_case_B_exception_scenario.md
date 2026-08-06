# Anwendungsfall B: Exception-Szenario

Stand: 2026-07-07

Task: 7.10 `Exception-Szenario B formulieren`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Entscheidung

| Feld | Wert |
| --- | --- |
| Scenario-ID | `SC-B-01-EX01` |
| `Scenario.kind` | `exception` |
| Sprechender Name | `Bereitschaftspruefung schlaegt fehl` |
| Zugehoeriger Main Use Case | `UC-B-01 Assistierte Kaffeemaschinenbedienung mit Vivian` |
| Branch-Anker aus 7.7 | `B-BRANCH-E02` |
| Eintrittspunkt im Hauptpfad | nach `B-MAIN-S11` |
| Rueckkehrpunkt in den Hauptpfad | keiner |
| Abgedeckte Faelle aus 6.8 | `B-EXC-003`, `B-EXC-004`, `B-EXC-005` |

## Warum dies eine Exception und keine Alternative ist

Dieses Szenario beschreibt keinen korrigierbaren Nebenpfad. Die Bereitschaftspruefung schlaegt fehl und die Ursache kann innerhalb des aktuellen Ablaufs nicht behoben werden. Der Bruehstart wird deshalb nicht ausgefuehrt.

Der Ablauf endet sicher und erklaerbar:

- `ReadinessCheck.result = failed` ist sichtbar.
- `CoffeeMachine.lifecycleState = notReady` bleibt oder wird gesetzt.
- `CoffeeMachine.startPermission = blocked` verhindert den assistierten Bruehstart.
- `CoffeeMachine.safeState = true` stellt sicher, dass kein unkontrollierter Bruehvorgang laeuft.
- Vivian erklaert die Ursache, statt den Start technisch zu erzwingen.

Damit ist der Pfad eine echte `exception`: Er verhindert den Hauptpfad und kehrt nicht zu `B-MAIN-S12` oder spaeteren Hauptpfadschritten zurueck.

## Scenario-Bedingungen

| Condition-ID | `Condition.kind` | Ausdruck | Verwendung | Begruendung |
| --- | --- | --- | --- | --- |
| `B-EX-PRE-01` | `pre` | `BrewingRequest.state = requested and BrewingRequest.state != cancelled` | `Scenario.precondition` | Die Exception tritt erst nach einer aktiven Startanforderung und der Bereitschaftspruefung auf. |
| `B-EX-G01` | `guard` | `ReadinessCheck.result = failed and CoffeeMachine.waterLevel = low and correctionInCurrentScenario = false` | Eintritt in `SC-B-01-EX01` | Die Ursache ist bekannt und im aktuellen Ablauf nicht korrigierbar. |
| `B-EX-G02` | `guard` | `CoffeeMachine.startPermission = blocked` | Kein Bruehstart | Das System darf keinen Bruehstart ausloesen. |
| `B-EX-POST-01` | `post` | `CoffeeMachine.lifecycleState = notReady` | `Scenario.postcondition` | Die Maschine bleibt in einem nicht startbereiten Zustand. |
| `B-EX-POST-02` | `post` | `CoffeeMachine.startPermission = blocked` | `Scenario.postcondition` | Der Start ist fachlich blockiert. |
| `B-EX-POST-03` | `post` | `CoffeeMachine.safeState = true` | `Scenario.postcondition` | Die Exception endet sicher. |
| `B-EX-POST-04` | `post` | `VivianAssistant.feedbackState = errorExplained` | `Scenario.postcondition` | Die Exception endet erklaerbar fuer den Visitor. |
| `B-EX-POST-05` | `post` | `CoffeeMachine.lifecycleState != brewing` | `Scenario.postcondition` | Es wurde kein Bruehvorgang gestartet. |

## Events

| Event-ID | `Event.kind` | `Event.expression` | Verwendung | Begruendung |
| --- | --- | --- | --- | --- |
| `B-EX-E01` | `environment` | `readinessFailed(CoffeeMachine, waterLevelLow)` | `B-EX-S01` | Die fehlgeschlagene Bereitschaft wird als beobachtbares Objekt-/Pruefergebnis modelliert. |
| `B-EX-E02` | `signal` | `errorExplanationIssued(VivianAssistant, waterLevelLow)` | `B-EX-S02` | Vivian erklaert die Ursache fachlich. |
| `B-EX-E03` | `environment` | `stateChanged(CoffeeMachine.startPermission, blocked)` | `B-EX-S03` | Die Startfreigabe wird blockiert. |
| `B-EX-E04` | `signal` | `exceptionClosed(VivianAssistant, brewingNotStarted)` | `B-EX-S04` | Vivian schliesst den Ausnahmefall erklaerbar ab. |

## StateAssertions

| StateAssertion-ID | subjectRef | `expectedState` | Verwendung | Begruendung |
| --- | --- | --- | --- | --- |
| `SA-B-READINESS-FAILED` | `ENT-B-04 BrewingRequest` | `ReadinessCheck.result = failed` | `B-EX-S01` | Die Bereitschaftspruefung ist negativ abgeschlossen. |
| `SA-B-CM-WATER-LOW` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.waterLevel = low` | `B-EX-S01` | Die Ursache der fehlgeschlagenen Bereitschaft ist fachlich sichtbar. |
| `SA-B-CM-NOT-READY` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.lifecycleState = notReady` | `B-EX-S01`, `B-EX-S03` | Die Maschine ist nicht startbereit. |
| `SA-B-VIVIAN-ERROR-EXPLAINED` | `ENT-B-01 VivianAssistant` | `VivianAssistant.feedbackState = errorExplained` | `B-EX-S02` | Vivian hat die Ursache erklaert. |
| `SA-B-CM-START-BLOCKED` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.startPermission = blocked` | `B-EX-S03` | Der Start bleibt fachlich verhindert. |
| `SA-B-CM-SAFE` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.safeState = true` | `B-EX-S03` | Die Maschine befindet sich in einem sicheren Zustand. |
| `SA-B-CM-NOT-BREWING` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.lifecycleState != brewing` | `B-EX-S03` | Es laeuft kein Bruehvorgang. |
| `SA-B-VIVIAN-EXCEPTION-CLOSED` | `ENT-B-01 VivianAssistant` | `VivianAssistant.feedbackState = exceptionClosed` | `B-EX-S04` | Der Ausnahmefall ist fuer den Visitor abgeschlossen. |

## ScenarioSteps

| Nr. | ScenarioStep-ID | `ScenarioStep.kind` | Text | performedBy | triggeredBy | guard | resultingState |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `B-EX-S01` | `environmentObservation` | Die Bereitschaftspruefung meldet, dass die Kaffeemaschine wegen zu niedrigem Wasserstand nicht startbereit ist. | - | `B-EX-E01` | `B-EX-G01` | `SA-B-READINESS-FAILED`, `SA-B-CM-WATER-LOW`, `SA-B-CM-NOT-READY` |
| 2 | `B-EX-S02` | `systemResponse` | Vivian erklaert dem Visitor, dass der Bruehstart wegen fehlender Startbereitschaft nicht ausgefuehrt wird. | - | `B-EX-E02` | - | `SA-B-VIVIAN-ERROR-EXPLAINED` |
| 3 | `B-EX-S03` | `environmentObservation` | Die Kaffeemaschine bleibt startblockiert und in einem sicheren nicht bruehenden Zustand. | - | `B-EX-E03` | `B-EX-G02` | `SA-B-CM-START-BLOCKED`, `SA-B-CM-SAFE`, `SA-B-CM-NOT-BREWING` |
| 4 | `B-EX-S04` | `systemResponse` | Vivian schliesst den Ausnahmefall ab und laesst den Hauptpfad nicht weiterlaufen. | - | `B-EX-E04` | - | `SA-B-VIVIAN-EXCEPTION-CLOSED` |

## StepRelations

| Relation-ID | source step | target step | relation kind | guardRef | Begruendung |
| --- | --- | --- | --- | --- | --- |
| `B-EX-R-IN01` | `B-MAIN-S11` | `B-EX-S01` | `exception` | `B-EX-G01` | Die negative Bereitschaftspruefung verlaesst den Hauptpfad. |
| `B-EX-R01` | `B-EX-S01` | `B-EX-S02` | `sequence` | - | Nach der negativen Pruefung erklaert Vivian die Ursache. |
| `B-EX-R02` | `B-EX-S02` | `B-EX-S03` | `sequence` | `B-EX-G02` | Nach der Erklaerung bleibt der Start fachlich blockiert. |
| `B-EX-R03` | `B-EX-S03` | `B-EX-S04` | `sequence` | - | Der sichere Zustand erlaubt einen erklaerbaren Abschluss der Exception. |

## Graphsicht

Der Exception-Pfad haengt nach der Bereitschaftspruefung aus und kehrt nicht in den Hauptpfad zurueck:

`B-MAIN-S11 -> B-EX-S01 -> B-EX-S02 -> B-EX-S03 -> B-EX-S04`

Nicht erlaubt ist in diesem Pfad:

`B-EX-S04 -> B-MAIN-S12`

Der Hauptpfad ab `B-MAIN-S12` setzt `ReadinessCheck.result = passed` voraus. Diese Voraussetzung ist in der Exception explizit falsch.

## Modellierungsgrenzen

| Thema | Entscheidung |
| --- | --- |
| Keine technische Direktkopplung | Die Exception nennt keinen Controller, keine API, kein Topic, kein Tool und keine RuntimeAction. |
| Keine Alternative | Der Pfad ist nicht innerhalb des aktuellen Ablaufs korrigierbar und kehrt nicht in den Hauptpfad zurueck. |
| Kein Bruehstart | `CoffeeMachine.lifecycleState != brewing` bleibt erwarteter Zustand. |
| Sicheres Ende | `CoffeeMachine.safeState = true` und `CoffeeMachine.startPermission = blocked` beschreiben den sicheren Abschluss. |
| Erklaerbares Ende | Vivians Fehlererklaerung ist als StateAssertion modelliert. |

## Abnahmekontrolle

| Kriterium aus Task 7.10 | Erfuellung |
| --- | --- |
| `Scenario.kind = exception` vorhanden | Ja: `SC-B-01-EX01` ist als `exception` festgelegt. |
| Exception endet sicher | Ja: `SA-B-CM-SAFE` und `SA-B-CM-START-BLOCKED` sichern den Endzustand ab. |
| Exception endet erklaerbar | Ja: Vivian erklaert die Ursache und schliesst den Ausnahmefall. |
| Kein Ruecksprung in Hauptpfad | Ja. Der Pfad endet bei `B-EX-S04` und kehrt nicht zu `B-MAIN-S12` zurueck. |
| Ursache ist modelliert | Ja: `ReadinessCheck.result = failed` und `CoffeeMachine.waterLevel = low`. |
| Keine technische Direktkopplung | Erfuellt. |

## Konsequenz fuer Task 8.1

Task 8.1 kann nun aus Hauptpfad, Alternative und Exception pruefbare Requirements fuer B ableiten. Wichtig sind Anforderungen an assistierte Bedienung, Startfreigabe, sichere Blockierung bei fehlender Bereitschaft und erklaerbare Vivian-Rueckmeldung.
