# Anwendungsfall B: Direkt modellierbare Elemente

Stand: 2026-07-07

Task: 9.1 `Direkt modellierbare B-Elemente markieren`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Abgrenzung

Ein Element gilt hier als direkt modellierbar, wenn es ohne neue Metamodellklasse und ohne semantischen Umweg einer vorhandenen Klasse, einem vorhandenen Attribut oder einer vorhandenen Beziehung des aktuellen kompakten Metamodells zugeordnet werden kann.

Diese Datei bewertet noch keine unscharf oder nicht modellierbaren Elemente. Solche Faelle folgen bewusst erst in Task 9.2 und 9.3.

## Ergebnis

Die zentralen Elemente des Anwendungsfalls B sind direkt modellierbar. Die direkte Abbildung deckt Requirements, UseCase, externe Actor-Rolle, Vivian als Agent/Entity, Kaffeemaschine als Entity, Scenarios, Steps, Events, Conditions, StateAssertions, fachliche Capabilities, RuntimeBindings, RuntimeActions und ValidationCases ab.

| Bereich | Direkt modellierbar? | Begruendung |
| --- | --- | --- |
| Requirements und UseCase | ja | Der Kern enthaelt `Requirement`, `UseCase`, `Actor` und optional `Satisfy`. |
| Rollen- und Instanztrennung | ja | `Actor`, `Agent` und `Entity` reichen fuer Visitor, Vivian und Kaffeemaschine aus. |
| Szenarioablauf | ja | `Scenario`, `ScenarioStep`, `StepRelation`, `Event`, `Condition` und `StateAssertion` decken Hauptpfad, Alternative und Exception ab. |
| Fachliche Assistenz- und Objektfaehigkeiten | ja | `CapabilityUse`, `Capability` und `Effect` bilden Vivian- und Kaffeemaschinenreaktionen ab. |
| Runtime-Anbindung | ja | `RuntimeBinding` und `RuntimeAction` trennen technische Bindung und technische Einzelaktion. |
| Validierung | ja | `ValidationCase` kann Requirements, den UseCase und RuntimeBindings pruefen; konkrete Scenario-Bezuege stehen im Stimulus und ExpectedOutcome. |

## Direkte Abbildung: Use-Case-Kern

| B-Element | Metamodellklasse | Konkrete Beziehung oder Attribut | Direkt modellierbare Instanzen |
| --- | --- | --- | --- |
| B-Requirements-Kontext | `RequirementsModel` | `RequirementsModel -> Requirement [0..*]`; `RequirementsModel -> UseCase [0..*]` | Kontext fuer `B-REQ-001` bis `B-REQ-018` und `UC-B-01` |
| Anforderungen an assistierte Kaffeemaschinenbedienung | `Requirement` | `RequirementsModel -> Requirement`; `Requirement.text` | `B-REQ-001` bis `B-REQ-018` |
| Fachlicher Anwendungsfall | `UseCase` | `RequirementsModel -> UseCase`; `UseCase -> Scenario [1..*]` | `UC-B-01` |
| Externe Benutzerrolle | `Actor` | `Actor -- UseCase : interactsWith` | `ACT-B-01 Visitor` |
| Requirement-Erfuellung | `Satisfy` | `Satisfy.satisfiedRequirement [0..*]`; `Satisfy.satisfiedBy [1..*]`; XOR-Regel | direkt modellierbar, aber fuer B noch nicht formal instanziiert |
| UseCase-Erfuellung | `Satisfy` | `Satisfy.satisfiedUseCase [0..*]`; `Satisfy.satisfiedBy [1..*]`; XOR-Regel | direkt modellierbar, aber fuer B noch nicht formal instanziiert |

## Direkte Abbildung: Rollen, Agenten und Entitaeten

| B-Element | Metamodellklasse | Konkrete Beziehung oder Attribut | Direkt modellierbare Instanzen |
| --- | --- | --- | --- |
| Visitor als externe Rolle | `Actor` | `Actor -- UseCase : interactsWith`; `ScenarioStep.performedBy [0..1]` | `ACT-B-01 Visitor` |
| Vivian als Assistenzinstanz | `Agent` und `Entity` | `Agent --|> Entity`; `StateAssertion.subjectRef -> Identifiable [1]`; `Entity -> Capability : provides [0..*]` | `ENT-B-01 VivianAssistant` |
| Kaffeemaschine als Interaktionsobjekt | `Entity` | `Entity.kind = asset`; `StateAssertion.subjectRef [1]`; `Entity -> Capability [0..*]` | `ENT-B-02 CoffeeMachine` |
| Tasse als Kontextobjekt | `Entity` | `StateAssertion.subjectRef [1]`; Nutzung in `Condition.expression` und `CapabilityUse.parameters` | `ENT-B-03 Cup` |
| Bruehanforderung als fachlicher Request | `Entity` | `StateAssertion.subjectRef [1]`; Nutzung in `Condition.expression` und Runtime-Schemas | `ENT-B-04 BrewingRequest` |
| Visitor-Handlungen | `ScenarioStep` | `ScenarioStep.kind = actorIntent`; `performedBy = ACT-B-01 Visitor` | `B-MAIN-S01`, `B-MAIN-S04`, `B-MAIN-S07`, `B-MAIN-S09`, `B-MAIN-S14`, `B-ALT-S03` |
| Vivian- und Systemreaktionen | `ScenarioStep` und `CapabilityUse` | `ScenarioStep.kind = systemResponse`; `ScenarioStep -> CapabilityUse [0..*]` | elf systemische Schritte mit `B-CU-001` bis `B-CU-011` |
| Objekt- und Umweltbeobachtungen | `ScenarioStep`, `Event`, `StateAssertion` | `ScenarioStep.kind = environmentObservation`; `triggeredBy [0..*]`; `resultingState [0..*]` | elf Beobachtungssteps im Haupt-, Alternativ- und Exception-Pfad |

## Direkte Abbildung: Szenarien und Ablaufstruktur

| B-Element | Metamodellklasse | Konkrete Beziehung oder Attribut | Direkt modellierbare Instanzen |
| --- | --- | --- | --- |
| Erfolgreicher Hauptablauf | `Scenario` | `UseCase -> Scenario [1..*]`; `Scenario.kind = main`; `Scenario.goal` | `SC-B-01-MAIN` |
| Fehlende Tasse mit Rueckfuehrung | `Scenario` | `UseCase -> Scenario [1..*]`; `Scenario.kind = alternative`; `Scenario.goal` | `SC-B-01-ALT01` |
| Fehlgeschlagene Bereitschaftspruefung | `Scenario` | `UseCase -> Scenario [1..*]`; `Scenario.kind = exception`; `Scenario.goal` | `SC-B-01-EX01` |
| Nummerierte Hauptpfadschritte | `ScenarioStep` | `Scenario -> ScenarioStep [1..*]`; `stepNumber`; `kind`; `text` | `B-MAIN-S01` bis `B-MAIN-S20` |
| Nummerierte Alternativschritte | `ScenarioStep` | `Scenario -> ScenarioStep [1..*]`; `ScenarioStep.kind` | `B-ALT-S01` bis `B-ALT-S04` |
| Nummerierte Exception-Schritte | `ScenarioStep` | `Scenario -> ScenarioStep [1..*]`; `ScenarioStep.kind` | `B-EX-S01` bis `B-EX-S04` |
| Lineare Hauptpfadsequenz | `StepRelation` | `Scenario -> StepRelation [0..*]`; `source [1]`; `target [1]`; `kind = sequence` | `B-MAIN-R01` bis `B-MAIN-R19` |
| Einstieg und Rueckfuehrung der Alternative | `StepRelation` | `source [1]`; `target [1]`; `kind = alternative|sequence`; optional `guard [0..1]` | `B-ALT-R-IN01`, `B-ALT-R01`, `B-ALT-R02`, `B-ALT-R03`, `B-ALT-R-OUT01` |
| Einstieg und Sequenz der Exception | `StepRelation` | `source [1]`; `target [1]`; `kind = exception|sequence`; optional `guard [0..1]` | `B-EX-R-IN01`, `B-EX-R01`, `B-EX-R02`, `B-EX-R03` |
| Nicht benoetigte Parallelitaet | `ParallelGroup` | `Scenario -> ParallelGroup [0..*]` erlaubt 0 | Fuer B keine Instanz; direkt modellierbar waere sie erst bei mindestens zwei parallelen Steps |
| Vorbereitete Branch-Anker | keine formale Klasse im Instanzenstand | dokumentierte Analyseinformation, keine `StepRelation` ohne Target | `B-BRANCH-*` als Vorbereitung, nicht als formale Instanz |

## Direkte Abbildung: Ereignisse und Bedingungen

| B-Element | Metamodellklasse | Konkrete Beziehung oder Attribut | Direkt modellierbare Instanzen |
| --- | --- | --- | --- |
| Benutzerereignisse | `Event` | `ScenarioStep -> Event : triggeredBy [0..*]`; `Event.kind = user`; `Event.expression` | `B-E01`, `B-E03`, `B-E05`, `B-E07`, `B-E11`, `B-ALT-E03` |
| Vivian-/Systemsignale | `Event` | `Event.kind = signal`; `triggeredBy [0..*]` | `B-E02`, `B-E08`, `B-E10`, `B-E12`, `B-E17`, `B-ALT-E02`, `B-EX-E02`, `B-EX-E04` |
| Kaffeemaschinen- und Umweltereignisse | `Event` | `Event.kind = environment`; `Event.expression` | `B-E04`, `B-E06`, `B-E09`, `B-E13`, `B-E14`, `B-E15`, `B-E16`, `B-ALT-E01`, `B-EX-E01`, `B-EX-E03` |
| Scenario-Preconditions | `Condition` | `Scenario.precondition [0..*]`; `Condition.kind = pre`; `Condition.expression` | `B-MAIN-PRE-*`, `B-ALT-PRE-01`, `B-EX-PRE-01` |
| Scenario-Postconditions | `Condition` | `Scenario.postcondition [0..*]`; `Condition.kind = post`; `Condition.expression` | `B-MAIN-POST-*`, `B-ALT-POST-*`, `B-EX-POST-*` |
| Step- und Relation-Guards | `Condition` | `ScenarioStep.guard [0..1]`; `StepRelation.guard [0..1]`; `Condition.kind = guard` | `B-MAIN-G01` bis `B-MAIN-G11`, `B-ALT-G01`, `B-ALT-G02`, `B-EX-G01`, `B-EX-G02` |
| Erwartete Vivian-Zustaende | `StateAssertion` | `subjectRef = ENT-B-01`; `expectedState` | `SA-B-VIVIAN-*` |
| Erwartete Kaffeemaschinenzustaende | `StateAssertion` | `subjectRef = ENT-B-02`; `expectedState` | `SA-B-CM-*` |
| Erwartete Kontextzustaende | `StateAssertion` | `subjectRef = ENT-B-03` oder `ENT-B-04`; `expectedState` | `SA-B-CUP-PLACED`, `SA-B-BREWING-*`, `SA-B-READINESS-FAILED` |

## Direkte Abbildung: Functional/Runtime Bridge

| B-Element | Metamodellklasse | Konkrete Beziehung oder Attribut | Direkt modellierbare Instanzen |
| --- | --- | --- | --- |
| Nutzung fachlicher Vivian-Fuehrung | `CapabilityUse` | `ScenarioStep -> CapabilityUse [0..*]`; `CapabilityUse -> Capability [1]` | `B-CU-001`, `B-CU-002`, `B-CU-003` |
| Nutzung fachlicher Request- und Rueckfragefaehigkeiten | `CapabilityUse` | `CapabilityUse.parameters [0..*]`; `CapabilityUse -> Capability [1]` | `B-CU-004`, `B-CU-006` |
| Nutzung fachlicher Maschinenfaehigkeiten | `CapabilityUse` | `ScenarioStep -> CapabilityUse`; `CapabilityUse -> Capability [1]` | `B-CU-005`, `B-CU-007` |
| Nutzung fachlicher Abschluss-, Alternativ- und Exception-Faehigkeiten | `CapabilityUse` | `ScenarioStep -> CapabilityUse`; `CapabilityUse -> Capability [1]` | `B-CU-008`, `B-CU-009`, `B-CU-010`, `B-CU-011` |
| Vivian-Faehigkeiten | `Capability` | `Entity -> Capability : provides [0..*]`; `Capability.precondition [0..*]`; `Capability.promisedEffect [1..*]` | neun `CAP-B-VIVIAN-*` Capabilities |
| Kaffeemaschinen-Faehigkeiten | `Capability` | `Entity -> Capability : provides [0..*]`; `Capability.promisedEffect [1..*]` | `CAP-B-CHECK-MACHINE-READY`, `CAP-B-START-BREWING` |
| Beobachtbare fachliche Wirkungen | `Effect` | `Capability -> Effect : promisedEffect [1..*]`; StateAssertion-Trace | `B-EFF-*` |
| Vivian- und VR-Bindungen | `RuntimeBinding` | `Capability -> RuntimeBinding [0..*]`; `RuntimeBinding.capability [1]`; `RuntimeBinding -> RuntimeAction [1..*]` | `B-RB-VIVIAN-*` |
| Kaffeemaschinenadapter-Bindungen | `RuntimeBinding` | `RuntimeBinding.capability [1]`; Runtime-Kontext `CoffeeMachineAdapterRuntime` | `B-RB-COFFEE-READINESS-CHECK`, `B-RB-COFFEE-START-BREWING` |
| Trace-Synchronisationsanteile | `RuntimeBinding` und `RuntimeAction` | Runtime-Kontext `FunctionalMLDSTraceRuntime`; keine direkte Step-Kante | in mehreren `B-RB-*` Bindings und `B-RA-TRACE-*` Actions |
| Technische Vivian-Aktionen | `RuntimeAction` | `RuntimeBinding -> RuntimeAction [1..*]`; Endpoint/Schemas als RuntimeAction-Daten | `B-RA-VIVIAN-*` |
| Technische VR-Praesentationsaktionen | `RuntimeAction` | `RuntimeAction.inputSchema [0..1]`; `RuntimeAction.outputSchema [0..1]` | `B-RA-VR-*` |
| Technische Kaffeemaschinenaktionen | `RuntimeAction` | Endpoint/Schemas als RuntimeAction-Daten | `B-RA-CM-*` |
| Technische Trace-Aktionen | `RuntimeAction` | Topic/Schemas als RuntimeAction-Daten | `B-RA-TRACE-*` |

## Direkte Abbildung: Validierung und Nachweis

| B-Element | Metamodellklasse | Konkrete Beziehung oder Attribut | Direkt modellierbare Instanzen |
| --- | --- | --- | --- |
| Struktur des Use Case pruefen | `ValidationCase` | `ValidationCase.verifies -> Requirement [0..*]`; `ValidationCase.validates -> UseCase [0..*]`; `expectedOutcome [1..*]` | `B-VC-001-USECASE-STRUCTURE` |
| Vivian-Fuehrungsstart pruefen | `ValidationCase` | `ValidationCase -> RuntimeBinding [0..*] : executes/checks`; `stimulus [0..*]` | `B-VC-002-MAIN-GUIDANCE-START` |
| Tassen- und Programmpfad pruefen | `ValidationCase` | `ValidationCase.verifies`; `ValidationCase.validates`; `expectedOutcome` | `B-VC-003-CUP-AND-PROGRAM-GUIDANCE` |
| Request und positive Bereitschaft pruefen | `ValidationCase` | `ValidationCase -> RuntimeBinding [0..*]`; RuntimeActions nur im Stimulus | `B-VC-004-REQUEST-READINESS-PASSED` |
| Startbestaetigung und Bruehstart pruefen | `ValidationCase` | `ValidationCase -> RuntimeBinding [0..*]`; `expectedOutcome [1..*]` | `B-VC-005-CONFIRMATION-AND-START` |
| Hauptpfadabschluss pruefen | `ValidationCase` | `ValidationCase.validates -> UseCase [0..*]`; Scenario-Scope im Stimulus; `expectedOutcome [1..*]` | `B-VC-006-MAIN-COMPLETION` |
| Alternative fehlende Tasse pruefen | `ValidationCase` | struktureller und runtime-naher ValidationCase | `B-VC-007-ALTERNATIVE-MISSING-CUP` |
| Exception fehlgeschlagene Bereitschaft pruefen | `ValidationCase` | RuntimeBinding-Pruefung plus erwarteter sicherer Outcome | `B-VC-008-EXCEPTION-READINESS-FAILED` |
| Keine Runtime-Kurzschaltung pruefen | `ValidationCase` | struktureller ExpectedOutcome ohne RuntimeBinding-Besitz | `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT` |
| Runtime-Abdeckung pruefen | `ValidationCase` | prueft `RuntimeBinding -> RuntimeAction [1..*]` | `B-VC-010-RUNTIME-COVERAGE` |

## Direkter Trace-Beispielpfad

Ein vollstaendig direkt modellierbarer Trace fuer den assistierten Bruehstart lautet:

`B-REQ-011 -> UC-B-01 -> SC-B-01-MAIN -> B-MAIN-S15 -> B-CU-007 -> CAP-B-START-BREWING -> B-EFF-BREWING-START-ISSUED -> B-RB-COFFEE-START-BREWING -> B-RA-CM-REQUEST-BREWING-START -> B-VC-005-CONFIRMATION-AND-START`

Dieser Trace nutzt nur vorhandene Metamodellklassen und vorhandene Beziehungen. Es gibt keine direkte Abkuerzung von `ScenarioStep` zu `RuntimeAction`.

## Noch nicht bewertet in 9.1

Folgende Aspekte werden absichtlich nicht in dieser Datei als Problem oder Luecke bewertet, weil sie zu Task 9.2 und 9.3 gehoeren:

- ob Vivians Dialogverhalten als einfache `Capability` ausreicht oder ein eigenes Dialog-/Interaction-Modell braucht,
- ob Kaffeemaschinen-Affordances wie Taste, Display, Tassenbereich und Feedbackkanal eigene Strukturen brauchen,
- ob Objektzustaende langfristig als StateAssertions genuegen oder ein Objektzustandsautomat noetig wird,
- ob Runtime-Kontexte wie `VivianAssistantRuntime` und `CoffeeMachineAdapterRuntime` als Strings ausreichend praezise sind,
- ob korrigierbare Preconditions wie Wasserstand, Tasse oder Programmauswahl als Variantenfamilie modelliert werden sollten,
- ob formale `Satisfy`-Instanzen fuer B vor der finalen Traceability-Konsolidierung angelegt werden muessen.

## Abnahmekontrolle

| Kriterium aus Task 9.1 | Erfuellung |
| --- | --- |
| Mappingtabelle vorhanden | Mehrere Tabellen ordnen B-Elemente konkreten Metamodellklassen zu. |
| Jede direkte Abbildung nennt konkrete Klasse | Jede Mapping-Zeile nennt eine Klasse wie `UseCase`, `ScenarioStep`, `Capability`, `RuntimeBinding` oder `RuntimeAction`. |
| Jede direkte Abbildung nennt konkrete Beziehung | Jede Mapping-Zeile nennt eine Beziehung oder ein Attribut, z. B. `UseCase -> Scenario`, `ScenarioStep -> CapabilityUse`, `RuntimeBinding -> RuntimeAction`. |
| Haupt-, Alternativ- und Exception-Pfad sind abgedeckt | Alle drei B-Scenarios erscheinen in der direkten Abbildung. |
| Keine Problem- oder Lueckenbewertung vorweggenommen | 9.2 und 9.3 bleiben fuer unscharfe oder nicht modellierbare Elemente reserviert. |

## Konsequenz fuer Task 9.2

Task 9.2 kann nun alle B-Elemente markieren, die nur indirekt, unscharf oder mit Zusatzannahmen modellierbar sind. Die direkte Basis ist hiermit abgegrenzt: Alles, was nicht ohne Zusatzannahme in die Tabellen oben passt, muss in 9.2 als unscharf oder in 9.3 als nicht modellierbar bewertet werden.
