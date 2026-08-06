# Anwendungsfall A: Direkt modellierbare Elemente

Stand: 2026-07-07

Task: 5.1 `Alle Elemente markieren, die direkt modellierbar sind`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Abgrenzung

Ein Element gilt hier als direkt modellierbar, wenn es ohne neue Metamodellklasse und ohne semantischen Umweg einer vorhandenen Klasse, einem vorhandenen Attribut oder einer vorhandenen Beziehung des aktuellen kompakten Metamodells zugeordnet werden kann.

Diese Datei bewertet noch keine unscharfen oder nicht modellierbaren Elemente. Solche Faelle folgen bewusst erst in Task 5.2 und 5.3.

## Ergebnis

Die zentralen Elemente des Anwendungsfalls A sind direkt modellierbar. Die direkte Abbildung deckt Requirements, UseCase, Actor-Rollen, Scenarios, Steps, Events, Conditions, StateAssertions, fachliche Capabilities, Runtime-Bindungen, technische RuntimeActions und ValidationCases ab.

| Bereich | Direkt modellierbar? | Begruendung |
| --- | --- | --- |
| Requirements und UseCase | ja | EAST-ADL-naher Kern enthaelt `Requirement`, `UseCase`, `Actor` und `Satisfy`. |
| Szenarioablauf | ja | `Scenario`, `ScenarioStep`, `StepRelation`, `Event`, `Condition` und `StateAssertion` decken den Ablauf ab. |
| Agent als modelliertes Subjekt | ja | `Agent` ist Spezialisierung von `Entity`; `AgentBody` kann als identifizierbares Subjekt verwendet werden. |
| Fachliche Agentenfaehigkeiten | ja | `CapabilityUse`, `Capability` und `Effect` bilden fachliche Reaktionen ab. |
| Runtime-Anbindung | ja | `RuntimeBinding` und `RuntimeAction` trennen technische Bindung und technische Einzelaktion. |
| Validierung | ja | `ValidationCase` kann Requirements, UseCase und RuntimeBindings pruefen. |

## Direkte Abbildung: Use-Case-Kern

| A-Element | Metamodellklasse | Konkrete Beziehung oder Attribut | Direkt modellierbare Instanzen |
| --- | --- | --- | --- |
| A-Requirements-Kontext | `RequirementsModel` | `RequirementsModel -> Requirement [0..*]`; `RequirementsModel -> UseCase [0..*]` | Kontext fuer `A-REQ-001` bis `A-REQ-015` und `UC-A-01` |
| Anforderungen an dynamisches Agentenmodellieren | `Requirement` | `RequirementsModel -> Requirement`; `Requirement.text` | `A-REQ-001` bis `A-REQ-015` |
| Fachlicher Anwendungsfall | `UseCase` | `RequirementsModel -> UseCase`; `UseCase -> Scenario [1..*]` | `UC-A-01` |
| Externe Modellierungsrolle | `Actor` | `Actor -- UseCase : interactsWith` | `ACT-A-01` / `ScenarioDesigner` |
| Externe Szenenteilnehmerrolle | `Actor` | `Actor -- UseCase : interactsWith` | `ACT-A-02` / `SceneParticipant` |
| Externe Beobachterrolle | `Actor` | `Actor -- UseCase : interactsWith`; `Effect.observableBy [0..*]` | `ACT-A-03` / `SceneObserver` |
| Requirement-Erfuellung | `Satisfy` | `Satisfy.satisfiedRequirement [0..*]`; `Satisfy.satisfiedBy [1..*]`; XOR-Regel | `SAT-A-REQ-001` bis `SAT-A-REQ-015` |
| UseCase-Erfuellung | `Satisfy` | `Satisfy.satisfiedUseCase [0..*]`; `Satisfy.satisfiedBy [1..*]`; XOR-Regel | `SAT-A-UC-001` |

## Direkte Abbildung: Szenarien und Ablaufstruktur

| A-Element | Metamodellklasse | Konkrete Beziehung oder Attribut | Direkt modellierbare Instanzen |
| --- | --- | --- | --- |
| Erfolgreicher Hauptablauf | `Scenario` | `UseCase -> Scenario [1..*]`; `Scenario.kind = main`; `Scenario.goal` | `A-MAIN-SC01` |
| Temporaere Blockade mit Rueckfuehrung | `Scenario` | `UseCase -> Scenario [1..*]`; `Scenario.kind = alternative`; `Scenario.goal` | `A-ALT-SC01` |
| Dauerhafte Blockade mit Fehlerabschluss | `Scenario` | `UseCase -> Scenario [1..*]`; `Scenario.kind = exception`; `Scenario.goal` | `A-EX-SC01` |
| Nummerierte Hauptpfadschritte | `ScenarioStep` | `Scenario -> ScenarioStep [1..*]`; `ScenarioStep.stepNumber`; `ScenarioStep.kind`; `ScenarioStep.text` | `A-MAIN-S01` bis `A-MAIN-S09` |
| Nummerierte Alternativschritte | `ScenarioStep` | `Scenario -> ScenarioStep [1..*]`; `ScenarioStep.kind = environmentObservation` | `A-ALT-S01`, `A-ALT-S02` |
| Nummerierte Exception-Schritte | `ScenarioStep` | `Scenario -> ScenarioStep [1..*]`; `ScenarioStep.kind` | `A-EX-S01`, `A-EX-S02`, `A-EX-S03` |
| Lineare Hauptpfadsequenz | `StepRelation` | `Scenario -> StepRelation [0..*]`; `source [1]`; `target [1]`; `kind = sequence` | `A-MAIN-R01` bis `A-MAIN-R08` |
| Einstieg und Rueckfuehrung der Alternative | `StepRelation` | `source [1]`; `target [1]`; `kind = alternative|sequence`; optional `guard [0..1]` | `A-ALT-R01`, `A-ALT-R02`, `A-ALT-R03` |
| Einstieg und Sequenz der Exception | `StepRelation` | `source [1]`; `target [1]`; `kind = exception|sequence`; optional `guard [0..1]` | `A-EX-R01`, `A-EX-R02`, `A-EX-R03` |
| Nicht benoetigte Parallelitaet | `ParallelGroup` | `Scenario -> ParallelGroup [0..*]` erlaubt 0 | Fuer A keine Instanz; direkt modellierbar waere sie erst bei mindestens zwei parallelen Steps |

## Direkte Abbildung: Ereignisse und Bedingungen

| A-Element | Metamodellklasse | Konkrete Beziehung oder Attribut | Direkt modellierbare Instanzen |
| --- | --- | --- | --- |
| Raeumliches Startereignis | `Event` | `ScenarioStep -> Event : triggeredBy [0..*]`; `Event.kind = spatial`; `Event.expression` | `A-E1` |
| Externes Signal als vorbereiteter Ausloeser | `Event` | `Event.kind = signal`; optionaler `triggeredBy`-Bezug | `A-E2` |
| Objektstoerung als vorbereiteter Ausloeser | `Event` | `Event.kind = environment`; optionaler `triggeredBy`-Bezug | `A-E3` |
| Blockadezustandsaenderung | `Event` | `ScenarioStep -> Event : triggeredBy [0..*]`; `Event.kind = environment` | `A-E4` |
| Optionaler Instruktionsmarker | `Event` | `Event.kind = signal`; optionaler `triggeredBy`-Bezug | `A-E5` |
| Szenengrenzenaenderung | `Event` | `Event.kind = spatial`; optionaler `triggeredBy`-Bezug | `A-E6` |
| Beobachtungspunkt-Verifikation | `Event` | `ScenarioStep -> Event : triggeredBy [0..*]`; `Event.kind = signal` | `A-E7` |
| Sichtbare Rueckmeldung | `Event` | `ScenarioStep -> Event : triggeredBy [0..*]`; `Event.kind = signal` | `A-E8` |
| Scenario-Preconditions | `Condition` | `Scenario.precondition [0..*]`; `Condition.kind = pre|spatial|guard|timing`; `Condition.expression` | `A-P1` bis `A-P12` |
| Scenario-Postconditions | `Condition` | `Scenario.postcondition [0..*]`; `Condition.kind = post`; `Condition.expression` | `A-Q1` bis `A-Q11` |
| Step-Guards | `Condition` | `ScenarioStep -> Condition : guard [0..1]`; `Condition.expression` | `A-GUARD-S01` bis `A-GUARD-S09`, soweit belegt |
| Alternative- und Exception-Guards | `Condition` | `ScenarioStep.guard [0..1]`; `StepRelation.guard [0..1]` | `A-GUARD-ALT-*`, `A-GUARD-EX-*` |

## Direkte Abbildung: Modellierte Subjekte und Zustandsaussagen

| A-Element | Metamodellklasse | Konkrete Beziehung oder Attribut | Direkt modellierbare Instanzen |
| --- | --- | --- | --- |
| Dynamischer Szenenagent | `Agent` und `Entity` | `Agent --|> Entity`; `StateAssertion.subjectRef -> Identifiable [1]`; `Entity -> Capability : provides [0..*]` | `AgentBody` |
| Ausloesezone | `Entity` | `StateAssertion.subjectRef -> Identifiable [1]`; Nutzung in `Event.expression` und `Condition.expression` | `TriggerZone` |
| Szenengrenze | `Entity` | `StateAssertion.subjectRef -> Identifiable [1]`; Nutzung in raeumlichen Conditions | `SceneBoundary` |
| Zielbereich | `Entity` | `StateAssertion.subjectRef -> Identifiable [1]`; Nutzung in Conditions, Effects und Runtime-Schemas | `TargetZone` |
| Hindernisbereich | `Entity` | `StateAssertion.subjectRef -> Identifiable [1]`; Nutzung in Guards und Runtime-Schemas | `ObstacleRegion` |
| Szenenzustandsmarker | `Entity` | `StateAssertion.subjectRef -> Identifiable [1]` | `SceneStateFlag` |
| Beobachtungspunkt | `Entity` | `StateAssertion.subjectRef -> Identifiable [1]`; `Effect.observableBy` bleibt Actor-Rolle, nicht Entity | `ObservationPoint` |
| Rueckmeldung | `Entity` | `StateAssertion.subjectRef -> Identifiable [1]` | `FeedbackSignal` |
| Agentenrolle als Zustand | `StateAssertion.expectedState` und `Condition.expression` | `subjectRef = AgentBody`; `expectedState = roleState=...` | `roleState=notBlocked`, `roleState=executor`, `roleState=completed`, `roleState=blocked` |
| Erwartete Hauptpfad-Zustaende | `StateAssertion` | `ScenarioStep -> StateAssertion : resultingState [0..*]`; `subjectRef [1]`; `expectedState` | `A-SA-S01-01` bis `A-SA-S09-02` |
| Erwartete Alternativ-Zustaende | `StateAssertion` | `ScenarioStep -> StateAssertion : resultingState [0..*]` | `A-ALT-SA01` bis `A-ALT-SA04` |
| Erwartete Exception-Zustaende | `StateAssertion` | `ScenarioStep -> StateAssertion : resultingState [0..*]` | `A-EX-SA01` bis `A-EX-SA06` |

## Direkte Abbildung: Functional/Runtime Bridge

| A-Element | Metamodellklasse | Konkrete Beziehung oder Attribut | Direkt modellierbare Instanzen |
| --- | --- | --- | --- |
| Nutzung einer fachlichen Rollenwechsel-Faehigkeit | `CapabilityUse` | `ScenarioStep -> CapabilityUse [0..*]`; `CapabilityUse -> Capability [1]` | `A-CU-001` |
| Nutzung einer zielgerichteten Szenenhandlungs-Faehigkeit | `CapabilityUse` | `ScenarioStep -> CapabilityUse [0..*]`; `CapabilityUse.parameters [0..*]` | `A-CU-002` |
| Nutzung einer Blockade-Sicherungs-Faehigkeit | `CapabilityUse` | `ScenarioStep -> CapabilityUse [0..*]`; `CapabilityUse -> Capability [1]` | `A-CU-003` |
| Fachlicher Rollenwechsel des Agenten | `Capability` | `Entity -> Capability : provides [0..*]`; `Capability -> Effect [1..*]`; `Capability -> RuntimeBinding [0..*]` | `A-CAP-ADOPT-EXECUTOR-ROLE` |
| Fachliche zielgerichtete Agentenhandlung | `Capability` | `Capability.precondition [0..*]`; `Capability.promisedEffect [1..*]` | `A-CAP-PERFORM-TARGETED-SCENE-ACTION` |
| Fachliches Stoppen blockierten Fortschritts | `Capability` | `Capability.precondition [0..*]`; `Capability.promisedEffect [1..*]` | `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` |
| Beobachtbare Rollenwechsel-Effects | `Effect` | `Capability -> Effect : promisedEffect [1..*]`; `Effect.observableBy [0..*]` | `A-EFF-ROLE-EXECUTOR`, `A-EFF-AGENT-ACTING` |
| Beobachtbare Zielhandlungs-Effects | `Effect` | `Capability -> Effect : promisedEffect [1..*]`; StateAssertion-Trace | `A-EFF-AGENT-MOVING-TO-TARGET`, `A-EFF-TARGET-OCCUPIED` |
| Beobachtbare Blockade-Effects | `Effect` | `Capability -> Effect : promisedEffect [1..*]`; StateAssertion-Trace | `A-EFF-AGENT-WAITING`, `A-EFF-ROLE-BLOCKED` |
| Rollenwechsel-Binding | `RuntimeBinding` | `Capability -> RuntimeBinding [0..*]`; `RuntimeBinding.capability [1]`; `RuntimeBinding -> RuntimeAction [1..*]` | `A-RB-ROLE-EXECUTOR-VR` |
| Zielhandlungs-Binding | `RuntimeBinding` | `Capability -> RuntimeBinding [0..*]`; `RuntimeBinding.capability [1]` | `A-RB-TARGET-ACTION-VR` |
| Blockade-Binding | `RuntimeBinding` | `Capability -> RuntimeBinding [0..*]`; `RuntimeBinding.capability [1]` | `A-RB-BLOCKED-PROGRESS-VR` |
| Technische Rollenwechsel-Aktionen | `RuntimeAction` | `RuntimeBinding -> RuntimeAction [1..*]`; `RuntimeAction.inputSchema [0..1]`; `RuntimeAction.outputSchema [0..1]` | `A-RA-ROLE-SET`, `A-RA-ROLE-SYNC` |
| Technische Zielhandlungs-Aktionen | `RuntimeAction` | `RuntimeBinding -> RuntimeAction [1..*]`; Endpoint/Schemas als RuntimeAction-Daten | `A-RA-TARGET-ACTION-REQUEST`, `A-RA-TARGET-OCCUPANCY-SYNC` |
| Technische Blockade-Aktionen | `RuntimeAction` | `RuntimeBinding -> RuntimeAction [1..*]`; Endpoint/Schemas als RuntimeAction-Daten | `A-RA-BLOCK-PROGRESS-HOLD`, `A-RA-BLOCK-STATE-SYNC` |

## Direkte Abbildung: Validierung und Nachweis

| A-Element | Metamodellklasse | Konkrete Beziehung oder Attribut | Direkt modellierbare Instanzen |
| --- | --- | --- | --- |
| Preconditions des Hauptpfads pruefen | `ValidationCase` | `ValidationCase.verifies -> Requirement [0..*]`; `ValidationCase.validates -> UseCase [0..*]`; `expectedOutcome [1..*]` | `A-VC-001-MAIN-PRECONDITION-CHAIN` |
| Rollenwechsel-Binding pruefen | `ValidationCase` | `ValidationCase -> RuntimeBinding [0..*] : executes/checks` | `A-VC-002-ROLE-BINDING` |
| Zielhandlungs-Binding pruefen | `ValidationCase` | `ValidationCase -> RuntimeBinding [0..*]`; `stimulus [0..*]`; `expectedOutcome [1..*]` | `A-VC-003-TARGET-ACTION-BINDING` |
| Hauptpfad-Ende pruefen | `ValidationCase` | `ValidationCase.validates -> UseCase [0..*]`; `expectedOutcome [1..*]` | `A-VC-004-MAIN-COMPLETION` |
| Alternative pruefen | `ValidationCase` | `ValidationCase.verifies -> Requirement [0..*]`; ohne RuntimeBinding zulaessig | `A-VC-005-ALTERNATIVE-TEMPORARY-BLOCK` |
| Exception pruefen | `ValidationCase` | `ValidationCase -> RuntimeBinding [0..*]`; `expectedOutcome [1..*]` | `A-VC-006-EXCEPTION-BLOCKED-PROGRESS` |
| Keine Runtime-Kurzschaltung pruefen | `ValidationCase` | `ValidationCase.verifies -> Requirement`; struktureller ExpectedOutcome | `A-VC-007-NO-DIRECT-RUNTIME-SHORTCUT` |
| Keine kuenstliche Parallelitaet pruefen | `ValidationCase` | `ValidationCase.verifies -> Requirement`; keine RuntimeBinding notwendig | `A-VC-008-NO-ARTIFICIAL-PARALLELGROUP` |

## Direkter Trace-Beispielpfad

Ein vollstaendig direkt modellierbarer Trace fuer den Rollenwechsel lautet:

`A-REQ-006 -> SAT-A-REQ-006 -> UC-A-01 -> A-MAIN-SC01 -> A-MAIN-S05 -> A-CU-001 -> A-CAP-ADOPT-EXECUTOR-ROLE -> A-EFF-ROLE-EXECUTOR -> A-RB-ROLE-EXECUTOR-VR -> A-RA-ROLE-SET -> A-VC-002-ROLE-BINDING`

Dieser Trace nutzt nur vorhandene Metamodellklassen und vorhandene Beziehungen. Es gibt keine direkte Abkuerzung von `ScenarioStep` zu `RuntimeAction`.

## Noch nicht bewertet in 5.1

Folgende Aspekte werden absichtlich nicht in dieser Datei als Problem oder Luecke bewertet, weil sie zu Task 5.2 und 5.3 gehoeren:

- ob raeumliche Beziehungen wie `inside`, `at` oder `movingTo` als Strings ausreichend praezise sind,
- ob Agenten-Lebenszyklus oder Rollenwechsel langfristig eine eigene Struktur brauchen,
- ob Interaktionsobjekte eigene Affordances oder Zustandsautomaten benoetigen,
- ob externe Signale, Beobachtungskanaele oder Laufzeitprofile eigene Ergaenzungsmodelle brauchen.

## Abnahmekontrolle

| Kriterium aus Task 5.1 | Erfuellung |
| --- | --- |
| Tabelle `Element -> Metamodellklasse` vorhanden | Mehrere Tabellen ordnen A-Elemente konkreten Metamodellklassen zu. |
| Jede direkte Abbildung nennt konkrete Klasse | Jede Zeile nennt eine Klasse wie `UseCase`, `ScenarioStep`, `Capability` oder `RuntimeAction`. |
| Jede direkte Abbildung nennt konkrete Beziehung | Jede Zeile nennt eine Beziehung oder ein Attribut, z. B. `UseCase -> Scenario`, `ScenarioStep -> CapabilityUse`, `RuntimeBinding -> RuntimeAction`. |
| Keine Problem- oder Lueckenbewertung vorweggenommen | 5.2 und 5.3 bleiben fuer unscharfe oder nicht modellierbare Elemente reserviert. |

## Konsequenz fuer Task 5.2

Task 5.2 kann nun alle Elemente markieren, die nur indirekt oder unsauber modellierbar sind. Die direkte Basis ist hiermit abgegrenzt: Alles, was nicht ohne Zusatzannahme in die Tabellen oben passt, muss in 5.2 als unscharf oder in 5.3 als nicht modellierbar bewertet werden.
