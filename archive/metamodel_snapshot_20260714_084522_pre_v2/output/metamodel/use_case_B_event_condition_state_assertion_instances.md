# Anwendungsfall B: Event-, Condition- und StateAssertion-Instanzen

Stand: 2026-07-07

Task: 8.7 `Events, Conditions und StateAssertions fuer B anlegen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Modellierungsregel

Dieser Task konsolidiert die Ablaufbedingungen und erwarteten Zustaende fuer alle drei B-Scenarios:

- `SC-B-01-MAIN`
- `SC-B-01-ALT01`
- `SC-B-01-EX01`

Die drei Modellklassen werden strikt getrennt:

- `Event` beschreibt einen fachlich beobachtbaren Ausloeser.
- `Condition` beschreibt Preconditions, Guards oder Postconditions.
- `StateAssertion` beschreibt erwartete oder beobachtete Zustaende eines identifizierbaren Subjekts.

Technische Aufrufe, Controller, APIs, Topics, Tools und RuntimeActions werden in diesem Task nicht angelegt. Technische Ausfuehrung folgt erst spaeter ueber:

`ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

## Identifizierbare Subjekte fuer StateAssertions

| Subject-ID | Metamodell-Einordnung | `Entity.kind` | Status | Verwendung |
| --- | --- | --- | --- | --- |
| `ENT-B-01 VivianAssistant` | `Agent` und damit `Entity` | `agent` | angelegt in Task 8.3 | Vivian-Modus, Vivian-Hinweise, Rueckfragen, Fehlererklaerung und Abschlussmeldung |
| `ENT-B-02 CoffeeMachine` | `Entity` | `asset` | angelegt in Task 8.4 | Kaffeemaschinenzustand, Bereitschaft, Startfreigabe, Feedback und sicherer Zustand |
| `ENT-B-03 Cup` | `Entity` | `asset` | minimale Kontext-Entity fuer StateAssertions | Tassenplatzierung als fachlich pruefbarer Kontextzustand |
| `ENT-B-04 BrewingRequest` | `Entity` | `stateObject` | minimale Kontext-Entity fuer StateAssertions | Startwunsch, Bestaetigung und fachlicher Startausloesungszustand |

`ENT-B-03` und `ENT-B-04` werden hier nur so weit formalisiert, wie es fuer gueltige `StateAssertion.subjectRef`-Referenzen noetig ist. Sie sind keine Actoren und keine RuntimeActions.

## Event-Instanzen

### Main Scenario Events

| Event-ID | Metamodellklasse | `uuid` | `shortName` | `Event.kind` | `Event.expression` | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `B-E01` | `Event` | `B-E01` | `AssistenzAngefordert` | `user` | `requestedAssistance(Visitor, CoffeeMachine)` | genutzt |
| `B-E02` | `Event` | `B-E02` | `VivianFuehrungsmodusAktiv` | `signal` | `modeChanged(VivianAssistant, guiding)` | genutzt |
| `B-E03` | `Event` | `B-E03` | `TassePlatziert` | `user` | `placed(Visitor, Cup, CoffeeMachine.cupArea)` | genutzt |
| `B-E04` | `Event` | `B-E04` | `TasseErkannt` | `environment` | `stateChanged(CoffeeMachine.cupPresent, true)` | genutzt in Main und Alternative |
| `B-E05` | `Event` | `B-E05` | `ProgrammGewaehlt` | `user` | `selectedProgram(Visitor, CoffeeMachine, coffee)` | genutzt |
| `B-E06` | `Event` | `B-E06` | `ProgrammauswahlBestaetigt` | `environment` | `stateChanged(CoffeeMachine.selectedProgram, coffee)` | genutzt |
| `B-E07` | `Event` | `B-E07` | `StarttasteBetaetigt` | `user` | `pressed(Visitor, CoffeeMachine.startButton)` | genutzt |
| `B-E08` | `Event` | `B-E08` | `BruehanforderungErkannt` | `signal` | `recognized(BrewingRequest.state, requested)` | genutzt |
| `B-E09` | `Event` | `B-E09` | `StartbereitschaftGemeldet` | `environment` | `stateChanged(CoffeeMachine.lifecycleState, ready) and shown(CoffeeMachine.readyFeedback)` | genutzt |
| `B-E10` | `Event` | `B-E10` | `StartbestaetigungAngefordert` | `signal` | `confirmationRequested(VivianAssistant, BrewingRequest)` | genutzt |
| `B-E11` | `Event` | `B-E11` | `AssistierterStartBestaetigt` | `user` | `confirmed(Visitor, BrewingRequest)` | genutzt |
| `B-E12` | `Event` | `B-E12` | `FachlichesStartsignalAusgegeben` | `signal` | `startSignalEmitted(System, CoffeeMachine)` | genutzt |
| `B-E13` | `Event` | `B-E13` | `BruehvorgangLaeuft` | `environment` | `stateChanged(CoffeeMachine.lifecycleState, brewing)` | genutzt |
| `B-E14` | `Event` | `B-E14` | `BruehfortschrittSichtbar` | `environment` | `shown(CoffeeMachine.progressIndicator)` | genutzt |
| `B-E15` | `Event` | `B-E15` | `BruehvorgangAbgeschlossen` | `environment` | `stateChanged(CoffeeMachine.lifecycleState, finished)` | genutzt |
| `B-E16` | `Event` | `B-E16` | `AbschlussrueckmeldungSichtbar` | `environment` | `shown(CoffeeMachine.completionFeedback)` | genutzt |
| `B-E17` | `Event` | `B-E17` | `VivianAbschlussGemeldet` | `signal` | `reported(VivianAssistant, completion)` | genutzt |

### Alternative und Exception Events

| Event-ID | Metamodellklasse | `uuid` | `shortName` | `Event.kind` | `Event.expression` | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `B-ALT-E01` | `Event` | `B-ALT-E01` | `TasseNichtErkannt` | `environment` | `stateChanged(CoffeeMachine.cupPresent, false)` | genutzt |
| `B-ALT-E02` | `Event` | `B-ALT-E02` | `TassenkorrekturHinweis` | `signal` | `guidanceIssued(VivianAssistant, placeCupAgain)` | genutzt |
| `B-ALT-E03` | `Event` | `B-ALT-E03` | `TasseNeuPlatziertOderAusgerichtet` | `user` | `placedOrAdjusted(Visitor, Cup, CoffeeMachine.cupArea)` | genutzt |
| `B-EX-E01` | `Event` | `B-EX-E01` | `BereitschaftFehlgeschlagen` | `environment` | `readinessFailed(CoffeeMachine, waterLevelLow)` | genutzt |
| `B-EX-E02` | `Event` | `B-EX-E02` | `FehlererklaerungAusgegeben` | `signal` | `errorExplanationIssued(VivianAssistant, waterLevelLow)` | genutzt |
| `B-EX-E03` | `Event` | `B-EX-E03` | `StartfreigabeBlockiert` | `environment` | `stateChanged(CoffeeMachine.startPermission, blocked)` | genutzt |
| `B-EX-E04` | `Event` | `B-EX-E04` | `ExceptionAbgeschlossen` | `signal` | `exceptionClosed(VivianAssistant, brewingNotStarted)` | genutzt |

## Condition-Instanzen

### Main Scenario Preconditions, Guards und Postconditions

| Condition-ID | Metamodellklasse | `uuid` | `Condition.kind` | Scope | `Condition.expression` |
| --- | --- | --- | --- | --- | --- |
| `B-MAIN-PRE-01` | `Condition` | `B-MAIN-PRE-01` | `pre` | `SC-B-01-MAIN` | `Visitor is present and able to interact` |
| `B-MAIN-PRE-02` | `Condition` | `B-MAIN-PRE-02` | `pre` | `SC-B-01-MAIN` | `CoffeeMachine.availabilityState = available` |
| `B-MAIN-PRE-03` | `Condition` | `B-MAIN-PRE-03` | `pre` | `SC-B-01-MAIN` | `CoffeeMachine.powerState = on` |
| `B-MAIN-PRE-04` | `Condition` | `B-MAIN-PRE-04` | `pre` | `SC-B-01-MAIN` | `CoffeeMachine.lifecycleState in {idle, ready, notReady}` |
| `B-MAIN-PRE-05` | `Condition` | `B-MAIN-PRE-05` | `pre` | `SC-B-01-MAIN` | `VivianAssistant.mode can become guiding` |
| `B-MAIN-G01` | `Condition` | `B-MAIN-G01` | `guard` | `B-MAIN-S01` | `helpRequested = true` |
| `B-MAIN-G02` | `Condition` | `B-MAIN-G02` | `guard` | `B-MAIN-S03`, `B-MAIN-R02` | `VivianAssistant.mode = guiding` |
| `B-MAIN-G03` | `Condition` | `B-MAIN-G03` | `guard` | `B-MAIN-S06`, `B-MAIN-R05` | `CoffeeMachine.cupPresent = true` |
| `B-MAIN-G04` | `Condition` | `B-MAIN-G04` | `guard` | `B-MAIN-S09`, `B-MAIN-R08` | `CoffeeMachine.selectedProgram != none` |
| `B-MAIN-G05` | `Condition` | `B-MAIN-G05` | `guard` | `B-MAIN-S11`, `B-MAIN-R10` | `BrewingRequest.state = requested and BrewingRequest.state != cancelled` |
| `B-MAIN-G06` | `Condition` | `B-MAIN-G06` | `guard` | `B-MAIN-S12`, `B-MAIN-R11` | `ReadinessCheck.result = passed and CoffeeMachine.cupPresent = true and CoffeeMachine.waterLevel = sufficient and CoffeeMachine.selectedProgram != none and CoffeeMachine.lifecycleState != brewing and CoffeeMachine.lifecycleState != error` |
| `B-MAIN-G07` | `Condition` | `B-MAIN-G07` | `guard` | `B-MAIN-S14`, `B-MAIN-R13` | `confirmationRequested(VivianAssistant, BrewingRequest) and BrewingRequest.state != cancelled` |
| `B-MAIN-G08` | `Condition` | `B-MAIN-G08` | `guard` | `B-MAIN-S15`, `B-MAIN-R14` | `BrewingRequest.confirmed = true and CoffeeMachine.startPermission = allowed and ReadinessCheck.result = passed and BrewingRequest.state != cancelled` |
| `B-MAIN-G09` | `Condition` | `B-MAIN-G09` | `guard` | `B-MAIN-S17`, `B-MAIN-R16` | `CoffeeMachine.lifecycleState = brewing` |
| `B-MAIN-G10` | `Condition` | `B-MAIN-G10` | `guard` | `B-MAIN-S19`, `B-MAIN-R18` | `CoffeeMachine.lifecycleState = finished` |
| `B-MAIN-G11` | `Condition` | `B-MAIN-G11` | `guard` | `B-MAIN-S20`, `B-MAIN-R19` | `CoffeeMachine.completionFeedback = visible` |
| `B-MAIN-POST-01` | `Condition` | `B-MAIN-POST-01` | `post` | `SC-B-01-MAIN` | `CoffeeMachine.lifecycleState = finished` |
| `B-MAIN-POST-02` | `Condition` | `B-MAIN-POST-02` | `post` | `SC-B-01-MAIN` | `CoffeeMachine.completionFeedback = visible` |
| `B-MAIN-POST-03` | `Condition` | `B-MAIN-POST-03` | `post` | `SC-B-01-MAIN` | `VivianAssistant.feedbackState = completionReported` |
| `B-MAIN-POST-04` | `Condition` | `B-MAIN-POST-04` | `post` | `SC-B-01-MAIN` | `BrewingRequest.state != cancelled` |
| `B-MAIN-POST-05` | `Condition` | `B-MAIN-POST-05` | `post` | `SC-B-01-MAIN` | `CoffeeMachine.lifecycleState != error` |

### Alternative und Exception Conditions

| Condition-ID | Metamodellklasse | `uuid` | `Condition.kind` | Scope | `Condition.expression` |
| --- | --- | --- | --- | --- | --- |
| `B-ALT-PRE-01` | `Condition` | `B-ALT-PRE-01` | `pre` | `SC-B-01-ALT01` | `CoffeeMachine.availabilityState = available and CoffeeMachine.powerState = on` |
| `B-ALT-G01` | `Condition` | `B-ALT-G01` | `guard` | `B-ALT-S01`, `B-ALT-S02`, `B-ALT-R-IN01`, `B-ALT-R01` | `CoffeeMachine.cupPresent = false` |
| `B-ALT-G02` | `Condition` | `B-ALT-G02` | `guard` | `B-ALT-S04`, `B-ALT-R-OUT01` | `CoffeeMachine.cupPresent = true` |
| `B-ALT-POST-01` | `Condition` | `B-ALT-POST-01` | `post` | `SC-B-01-ALT01` | `CoffeeMachine.cupPresent = true` |
| `B-ALT-POST-02` | `Condition` | `B-ALT-POST-02` | `post` | `SC-B-01-ALT01` | `CoffeeMachine.lifecycleState != error` |
| `B-EX-PRE-01` | `Condition` | `B-EX-PRE-01` | `pre` | `SC-B-01-EX01` | `BrewingRequest.state = requested and BrewingRequest.state != cancelled` |
| `B-EX-G01` | `Condition` | `B-EX-G01` | `guard` | `B-EX-S01`, `B-EX-R-IN01` | `ReadinessCheck.result = failed and CoffeeMachine.waterLevel = low and correctionInCurrentScenario = false` |
| `B-EX-G02` | `Condition` | `B-EX-G02` | `guard` | `B-EX-S03`, `B-EX-R02` | `CoffeeMachine.startPermission = blocked` |
| `B-EX-POST-01` | `Condition` | `B-EX-POST-01` | `post` | `SC-B-01-EX01` | `CoffeeMachine.lifecycleState = notReady` |
| `B-EX-POST-02` | `Condition` | `B-EX-POST-02` | `post` | `SC-B-01-EX01` | `CoffeeMachine.startPermission = blocked` |
| `B-EX-POST-03` | `Condition` | `B-EX-POST-03` | `post` | `SC-B-01-EX01` | `CoffeeMachine.safeState = true` |
| `B-EX-POST-04` | `Condition` | `B-EX-POST-04` | `post` | `SC-B-01-EX01` | `VivianAssistant.feedbackState = errorExplained` |
| `B-EX-POST-05` | `Condition` | `B-EX-POST-05` | `post` | `SC-B-01-EX01` | `CoffeeMachine.lifecycleState != brewing` |

## StateAssertion-Instanzen

### Main Scenario StateAssertions

| StateAssertion-ID | Metamodellklasse | `uuid` | Owner-Scenario | ScenarioStep | `subjectRef` | `expectedState` |
| --- | --- | --- | --- | --- | --- | --- |
| `SA-B-VIVIAN-GUIDING` | `StateAssertion` | `SA-B-VIVIAN-GUIDING` | `SC-B-01-MAIN` | `B-MAIN-S02` | `ENT-B-01 VivianAssistant` | `VivianAssistant.mode = guiding` |
| `SA-B-VIVIAN-GUIDANCE-CUP` | `StateAssertion` | `SA-B-VIVIAN-GUIDANCE-CUP` | `SC-B-01-MAIN` | `B-MAIN-S03` | `ENT-B-01 VivianAssistant` | `VivianAssistant.guidanceTopic = placeCup` |
| `SA-B-CUP-PLACED` | `StateAssertion` | `SA-B-CUP-PLACED` | `SC-B-01-MAIN` | `B-MAIN-S04` | `ENT-B-03 Cup` | `Cup.state = placed` |
| `SA-B-CM-CUP-PRESENT` | `StateAssertion` | `SA-B-CM-CUP-PRESENT` | `SC-B-01-MAIN` | `B-MAIN-S05` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.cupPresent = true` |
| `SA-B-VIVIAN-GUIDANCE-PROGRAM` | `StateAssertion` | `SA-B-VIVIAN-GUIDANCE-PROGRAM` | `SC-B-01-MAIN` | `B-MAIN-S06` | `ENT-B-01 VivianAssistant` | `VivianAssistant.guidanceTopic = selectProgram` |
| `SA-B-CM-PROGRAM-COFFEE` | `StateAssertion` | `SA-B-CM-PROGRAM-COFFEE` | `SC-B-01-MAIN` | `B-MAIN-S08` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.selectedProgram = coffee` |
| `SA-B-CM-SELECTION-FEEDBACK` | `StateAssertion` | `SA-B-CM-SELECTION-FEEDBACK` | `SC-B-01-MAIN` | `B-MAIN-S08` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.selectionFeedback = visible` |
| `SA-B-BREWING-REQUESTED` | `StateAssertion` | `SA-B-BREWING-REQUESTED` | `SC-B-01-MAIN` | `B-MAIN-S09` | `ENT-B-04 BrewingRequest` | `BrewingRequest.state = requested` |
| `SA-B-VIVIAN-INTENT-CONFIRMED` | `StateAssertion` | `SA-B-VIVIAN-INTENT-CONFIRMED` | `SC-B-01-MAIN` | `B-MAIN-S10` | `ENT-B-01 VivianAssistant` | `VivianAssistant.feedbackState = intentConfirmed` |
| `SA-B-CM-READY` | `StateAssertion` | `SA-B-CM-READY` | `SC-B-01-MAIN` | `B-MAIN-S12` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.lifecycleState = ready` |
| `SA-B-CM-READY-FEEDBACK` | `StateAssertion` | `SA-B-CM-READY-FEEDBACK` | `SC-B-01-MAIN` | `B-MAIN-S12` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.readyFeedback = visible` |
| `SA-B-CM-START-PERMISSION` | `StateAssertion` | `SA-B-CM-START-PERMISSION` | `SC-B-01-MAIN` | `B-MAIN-S12` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.startPermission = allowed` |
| `SA-B-VIVIAN-AWAITING-CONFIRMATION` | `StateAssertion` | `SA-B-VIVIAN-AWAITING-CONFIRMATION` | `SC-B-01-MAIN` | `B-MAIN-S13` | `ENT-B-01 VivianAssistant` | `VivianAssistant.feedbackState = awaitingConfirmation` |
| `SA-B-BREWING-CONFIRMED` | `StateAssertion` | `SA-B-BREWING-CONFIRMED` | `SC-B-01-MAIN` | `B-MAIN-S14` | `ENT-B-04 BrewingRequest` | `BrewingRequest.confirmed = true` |
| `SA-B-BREWING-START-ISSUED` | `StateAssertion` | `SA-B-BREWING-START-ISSUED` | `SC-B-01-MAIN` | `B-MAIN-S15` | `ENT-B-04 BrewingRequest` | `BrewingRequest.executionState = startIssued` |
| `SA-B-CM-BREWING` | `StateAssertion` | `SA-B-CM-BREWING` | `SC-B-01-MAIN` | `B-MAIN-S16` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.lifecycleState = brewing` |
| `SA-B-CM-PROGRESS-VISIBLE` | `StateAssertion` | `SA-B-CM-PROGRESS-VISIBLE` | `SC-B-01-MAIN` | `B-MAIN-S17` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.progressIndicator = visible` |
| `SA-B-CM-FINISHED` | `StateAssertion` | `SA-B-CM-FINISHED` | `SC-B-01-MAIN` | `B-MAIN-S18` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.lifecycleState = finished` |
| `SA-B-CM-COMPLETION-FEEDBACK` | `StateAssertion` | `SA-B-CM-COMPLETION-FEEDBACK` | `SC-B-01-MAIN` | `B-MAIN-S19` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.completionFeedback = visible` |
| `SA-B-VIVIAN-COMPLETION-REPORTED` | `StateAssertion` | `SA-B-VIVIAN-COMPLETION-REPORTED` | `SC-B-01-MAIN` | `B-MAIN-S20` | `ENT-B-01 VivianAssistant` | `VivianAssistant.feedbackState = completionReported` |

### Alternative und Exception StateAssertions

| StateAssertion-ID | Metamodellklasse | `uuid` | Owner-Scenario | ScenarioStep | `subjectRef` | `expectedState` |
| --- | --- | --- | --- | --- | --- | --- |
| `SA-B-CM-CUP-MISSING` | `StateAssertion` | `SA-B-CM-CUP-MISSING` | `SC-B-01-ALT01` | `B-ALT-S01` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.cupPresent = false` |
| `SA-B-VIVIAN-CUP-CORRECTION-GUIDANCE` | `StateAssertion` | `SA-B-VIVIAN-CUP-CORRECTION-GUIDANCE` | `SC-B-01-ALT01` | `B-ALT-S02` | `ENT-B-01 VivianAssistant` | `VivianAssistant.guidanceTopic = placeCupAgain` |
| `SA-B-READINESS-FAILED` | `StateAssertion` | `SA-B-READINESS-FAILED` | `SC-B-01-EX01` | `B-EX-S01` | `ENT-B-04 BrewingRequest` | `ReadinessCheck.result = failed` |
| `SA-B-CM-WATER-LOW` | `StateAssertion` | `SA-B-CM-WATER-LOW` | `SC-B-01-EX01` | `B-EX-S01` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.waterLevel = low` |
| `SA-B-CM-NOT-READY` | `StateAssertion` | `SA-B-CM-NOT-READY` | `SC-B-01-EX01` | `B-EX-S01`, `B-EX-S03` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.lifecycleState = notReady` |
| `SA-B-VIVIAN-ERROR-EXPLAINED` | `StateAssertion` | `SA-B-VIVIAN-ERROR-EXPLAINED` | `SC-B-01-EX01` | `B-EX-S02` | `ENT-B-01 VivianAssistant` | `VivianAssistant.feedbackState = errorExplained` |
| `SA-B-CM-START-BLOCKED` | `StateAssertion` | `SA-B-CM-START-BLOCKED` | `SC-B-01-EX01` | `B-EX-S03` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.startPermission = blocked` |
| `SA-B-CM-SAFE` | `StateAssertion` | `SA-B-CM-SAFE` | `SC-B-01-EX01` | `B-EX-S03` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.safeState = true` |
| `SA-B-CM-NOT-BREWING` | `StateAssertion` | `SA-B-CM-NOT-BREWING` | `SC-B-01-EX01` | `B-EX-S03` | `ENT-B-02 CoffeeMachine` | `CoffeeMachine.lifecycleState != brewing` |
| `SA-B-VIVIAN-EXCEPTION-CLOSED` | `StateAssertion` | `SA-B-VIVIAN-EXCEPTION-CLOSED` | `SC-B-01-EX01` | `B-EX-S04` | `ENT-B-01 VivianAssistant` | `VivianAssistant.feedbackState = exceptionClosed` |

Hinweis: `SA-B-CUP-PLACED` und `SA-B-CM-CUP-PRESENT` werden in `SC-B-01-ALT01` wiederverwendet, weil die Alternative nach erfolgreicher Korrektur dieselben fachlichen Zielzustaende wie der Hauptpfad herstellt.

## Zuordnung zu ScenarioSteps

| ScenarioStep | `triggeredBy` | `guard` | `resultingState` |
| --- | --- | --- | --- |
| `B-MAIN-S01` | `B-E01` | `B-MAIN-G01` | leer |
| `B-MAIN-S02` | `B-E01` | leer | `SA-B-VIVIAN-GUIDING` |
| `B-MAIN-S03` | `B-E02` | `B-MAIN-G02` | `SA-B-VIVIAN-GUIDANCE-CUP` |
| `B-MAIN-S04` | `B-E03` | leer | `SA-B-CUP-PLACED` |
| `B-MAIN-S05` | `B-E04` | leer | `SA-B-CM-CUP-PRESENT` |
| `B-MAIN-S06` | `B-E04` | `B-MAIN-G03` | `SA-B-VIVIAN-GUIDANCE-PROGRAM` |
| `B-MAIN-S07` | `B-E05` | leer | leer |
| `B-MAIN-S08` | `B-E06` | leer | `SA-B-CM-PROGRAM-COFFEE`, `SA-B-CM-SELECTION-FEEDBACK` |
| `B-MAIN-S09` | `B-E07` | `B-MAIN-G04` | `SA-B-BREWING-REQUESTED` |
| `B-MAIN-S10` | `B-E07` | leer | `SA-B-VIVIAN-INTENT-CONFIRMED` |
| `B-MAIN-S11` | `B-E08` | `B-MAIN-G05` | leer |
| `B-MAIN-S12` | `B-E09` | `B-MAIN-G06` | `SA-B-CM-READY`, `SA-B-CM-READY-FEEDBACK`, `SA-B-CM-START-PERMISSION` |
| `B-MAIN-S13` | `B-E09` | leer | `SA-B-VIVIAN-AWAITING-CONFIRMATION` |
| `B-MAIN-S14` | `B-E10`, `B-E11` | `B-MAIN-G07` | `SA-B-BREWING-CONFIRMED` |
| `B-MAIN-S15` | `B-E11`, `B-E12` | `B-MAIN-G08` | `SA-B-BREWING-START-ISSUED` |
| `B-MAIN-S16` | `B-E13` | leer | `SA-B-CM-BREWING` |
| `B-MAIN-S17` | `B-E14` | `B-MAIN-G09` | `SA-B-CM-PROGRESS-VISIBLE` |
| `B-MAIN-S18` | `B-E15` | leer | `SA-B-CM-FINISHED` |
| `B-MAIN-S19` | `B-E16` | `B-MAIN-G10` | `SA-B-CM-COMPLETION-FEEDBACK` |
| `B-MAIN-S20` | `B-E16`, `B-E17` | `B-MAIN-G11` | `SA-B-VIVIAN-COMPLETION-REPORTED` |
| `B-ALT-S01` | `B-ALT-E01` | `B-ALT-G01` | `SA-B-CM-CUP-MISSING` |
| `B-ALT-S02` | `B-ALT-E02` | `B-ALT-G01` | `SA-B-VIVIAN-CUP-CORRECTION-GUIDANCE` |
| `B-ALT-S03` | `B-ALT-E03` | leer | `SA-B-CUP-PLACED` |
| `B-ALT-S04` | `B-E04` | `B-ALT-G02` | `SA-B-CM-CUP-PRESENT` |
| `B-EX-S01` | `B-EX-E01` | `B-EX-G01` | `SA-B-READINESS-FAILED`, `SA-B-CM-WATER-LOW`, `SA-B-CM-NOT-READY` |
| `B-EX-S02` | `B-EX-E02` | leer | `SA-B-VIVIAN-ERROR-EXPLAINED` |
| `B-EX-S03` | `B-EX-E03` | `B-EX-G02` | `SA-B-CM-START-BLOCKED`, `SA-B-CM-SAFE`, `SA-B-CM-NOT-BREWING`, `SA-B-CM-NOT-READY` |
| `B-EX-S04` | `B-EX-E04` | leer | `SA-B-VIVIAN-EXCEPTION-CLOSED` |

## Zuordnung zu Scenarios und StepRelations

| Zieltyp | Ziel | Referenzen | Bewertung |
| --- | --- | --- | --- |
| `Scenario.precondition` | `SC-B-01-MAIN` | `B-MAIN-PRE-01`, `B-MAIN-PRE-02`, `B-MAIN-PRE-03`, `B-MAIN-PRE-04`, `B-MAIN-PRE-05` | gueltig: `0..*` |
| `Scenario.postcondition` | `SC-B-01-MAIN` | `B-MAIN-POST-01`, `B-MAIN-POST-02`, `B-MAIN-POST-03`, `B-MAIN-POST-04`, `B-MAIN-POST-05` | gueltig: `0..*` |
| `Scenario.precondition` | `SC-B-01-ALT01` | `B-ALT-PRE-01` | gueltig: `0..*` |
| `Scenario.postcondition` | `SC-B-01-ALT01` | `B-ALT-POST-01`, `B-ALT-POST-02` | gueltig: `0..*` |
| `Scenario.precondition` | `SC-B-01-EX01` | `B-EX-PRE-01` | gueltig: `0..*` |
| `Scenario.postcondition` | `SC-B-01-EX01` | `B-EX-POST-01`, `B-EX-POST-02`, `B-EX-POST-03`, `B-EX-POST-04`, `B-EX-POST-05` | gueltig: `0..*` |
| `StepRelation.guard` | `B-ALT-R-IN01` | `B-ALT-G01` | Eintritt in Alternative bei fehlender Tasse |
| `StepRelation.guard` | `B-ALT-R-OUT01` | `B-ALT-G02` | Rueckkehr in den Hauptpfad bei erkannter Tasse |
| `StepRelation.guard` | `B-EX-R-IN01` | `B-EX-G01` | Eintritt in Exception bei fehlgeschlagener Bereitschaftspruefung |
| `StepRelation.guard` | `B-EX-R02` | `B-EX-G02` | Blockierter Start nach Fehlererklaerung |

## Kardinalitaets- und Konsistenzcheck

| Regel | Bewertung fuer B |
| --- | --- |
| `ScenarioStep.triggeredBy [0..*]` | Erfuellt. Alle 28 Steps haben mindestens ein fachlich begruendetes Event; einige Steps nutzen mehrere Events. |
| `ScenarioStep.guard [0..1]` | Erfuellt. Jeder Step hat hoechstens eine direkte Guard Condition. |
| `StepRelation.guard [0..1]` | Erfuellt. Jede aufgefuehrte Relation hat hoechstens eine Guard Condition. |
| `ScenarioStep.resultingState [0..*]` | Erfuellt. Steps haben keine, eine oder mehrere resultierende StateAssertions. |
| `StateAssertion.subjectRef [1]` | Erfuellt. Jede StateAssertion referenziert genau ein identifizierbares Subjekt. |
| `StateAssertion.expectedState` | Erfuellt. Jede StateAssertion besitzt genau einen pruefbaren erwarteten Zustand. |
| Jede Entscheidung modelliert | Erfuellt. Einstieg, positive Bereitschaft, Rueckkehr aus Alternative, Exception-Einstieg und Startblockierung besitzen Conditions. |
| Jeder Zielzustand modelliert | Erfuellt. Erfolgszustand, Korrekturzustand und sicherer Exception-Zustand sind als StateAssertions formuliert. |
| Keine technische Kurzschaltung | Erfuellt. Keine Event-, Condition- oder StateAssertion-Instanz referenziert Controller, API, Topic, Tool oder RuntimeAction. |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 8.7 | Folgetask |
| --- | --- | --- |
| `CapabilityUse`-Instanzen | nicht angelegt | 8.8 |
| `Capability`- und `Effect`-Instanzen | nicht angelegt | 8.9 |
| `RuntimeBinding` und `RuntimeAction` | nicht angelegt | 8.10 und 8.11 |
| `ValidationCase` | nicht angelegt | 8.12 |
| Formale `Satisfy`-Instanzen | nicht angelegt | spaetere Konsolidierung nach B-Mapping |

## Abnahmekontrolle

| Kriterium aus Task 8.7 | Erfuellung |
| --- | --- |
| Ablaufbedingungen vorhanden | Main-, Alternative- und Exception-Preconditions, Guards und Postconditions sind angelegt. |
| Erwartete Zustaende vorhanden | Main-, Alternative- und Exception-StateAssertions sind angelegt und Step-bezogen zugeordnet. |
| Jede Entscheidung modelliert | Guards fuer Assistenzstart, Fuehrungsmodus, Tasse, Programmauswahl, Bereitschaft, Bestaetigung, Startfreigabe, Alternative und Exception sind vorhanden. |
| Jeder Zielzustand modelliert | `brewing`, `finished`, sichtbares Feedback, korrigierte Tasse, blockierter Start und sicherer Nicht-Bruehzustand sind StateAssertions. |
| Actor/Agent/Entity-Trennung eingehalten | User-Events kommen vom Visitor; Vivian-Zustaende referenzieren `ENT-B-01`; Kaffeemaschinenzustaende referenzieren `ENT-B-02`. |
| Keine Runtime-Direktkopplung | Technische Ausfuehrung bleibt aus Events, Conditions und StateAssertions herausgezogen. |

## Konsequenz fuer Task 8.8

Task 8.8 kann nun fuer die systemischen Schritte die benoetigten `CapabilityUse`-Instanzen anlegen. Besonders relevant sind Vivian-Fuehrung, Vivian-Rueckfrage, Bereitschaftspruefung, fachlicher Bruehstart, Fehlererklaerung und Exception-Abschluss.
