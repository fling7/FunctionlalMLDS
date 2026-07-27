# Anwendungsfall A: Kardinalitaetspruefung

Stand: 2026-07-07

Task: 4.16 `Kardinalitaeten fuer A pruefen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Ergebnis

Die bisher angelegten Instanzen fuer Anwendungsfall A verletzen keine Kardinalitaet des aktuellen kompakten Metamodells.

| Pruefbereich | Ergebnis |
| --- | --- |
| Sichtbare Diagrammkanten | bestanden |
| Attributbasierte Kardinalitaeten | bestanden |
| Pflichtbeziehungen | bestanden |
| Optional nicht instanziierte Beziehungen | zulaessig |
| Offene Kardinalitaetsverletzungen | 0 |

Wichtig: Eine Beziehung mit Kardinalitaet `0..*` oder `0..1` muss nicht belegt werden. Nicht instanziierte optionale Beziehungen werden deshalb nur dann als Problem gewertet, wenn ein konkretes A-Artefakt sie trotzdem benutzt oder wenn eine Folgeregel verletzt waere.

## Gepruefte Artefakte

| Artefakt | Zweck fuer die Pruefung |
| --- | --- |
| `cardinality_table.md` | Soll-Kardinalitaeten des Metamodells |
| `use_case_A_requirements.md` | Requirement-Instanzen |
| `use_case_A_usecase_instance.md` | UseCase-Instanz |
| `use_case_A_actor_instances.md` | Actor-UseCase-Beziehungen |
| `use_case_A_satisfy_relationships.md` | Satisfy-Instanzen und XOR-Regel |
| `use_case_A_scenario_instances.md` | UseCase-Scenario-Komposition |
| `use_case_A_scenario_step_instances.md` | ScenarioStep-Komposition |
| `use_case_A_event_instances.md` | triggeredBy-Zuordnungen |
| `use_case_A_condition_instances.md` | Guard-, Pre- und Postcondition-Zuordnungen |
| `use_case_A_state_assertion_instances.md` | resultingState- und subjectRef-Zuordnungen |
| `use_case_A_capability_use_instances.md` | ScenarioStep-CapabilityUse-Komposition |
| `use_case_A_capability_instances.md` | Capability-Instanzen |
| `use_case_A_effect_instances.md` | Capability-Effect-Komposition |
| `use_case_A_runtime_binding_instances.md` | Capability-RuntimeBinding-Zuordnung |
| `use_case_A_runtime_action_instances.md` | RuntimeBinding-RuntimeAction-Komposition |
| `use_case_A_validation_case_instances.md` | ValidationCase-Zuordnungen |

## Zentrale Zaehler fuer A

| Elementgruppe | Anzahl fuer A | Bewertung |
| --- | ---: | --- |
| Requirements | 15 | gueltig |
| UseCases | 1 | gueltig |
| Actors | 3 | gueltig |
| Satisfy-Instanzen | 16 | gueltig |
| Scenarios | 3 | gueltig |
| Main Scenarios pro UseCase | 1 | gueltig |
| ScenarioSteps | 14 | gueltig |
| StepRelations | 14 | gueltig |
| ParallelGroups | 0 | gueltig, optional |
| Events | 8 | gueltig |
| triggeredBy-Zuordnungen | 5 | gueltig |
| Conditions | 41 | gueltig |
| StateAssertions | 28 | gueltig |
| CapabilityUses | 3 | gueltig |
| Capabilities | 3 | gueltig |
| Effects | 6 | gueltig |
| RuntimeBindings | 3 | gueltig |
| RuntimeActions | 6 | gueltig |
| ValidationCases | 8 | gueltig |

## Checkliste sichtbarer Diagrammkanten

| Nr. | Beziehung | Soll | Ist fuer A | Bewertung |
| ---: | --- | --- | --- | --- |
| 1 | `RequirementsModel -> Requirement` | `0..*` | 15 A-Requirements im A-Artefaktkontext | gueltig |
| 2 | `RequirementsModel -> UseCase` | `0..*` | 1 UseCase `UC-A-01` im A-Artefaktkontext | gueltig |
| 3 | `Actor -> UseCase` | `0..*` beidseitig | `ACT-A-01`, `ACT-A-02`, `ACT-A-03` interagieren mit `UC-A-01` | gueltig |
| 4 | `UseCase -> ExtensionPoint` | `0..*` | 0 ExtensionPoints fuer `UC-A-01` | gueltig, optional |
| 5 | `UseCase -> Include` | `0..*` | 0 Include-Instanzen fuer `UC-A-01` | gueltig, optional |
| 6 | `UseCase -> Extend` | `0..*` | 0 Extend-Instanzen fuer `UC-A-01` | gueltig, optional |
| 7 | `Extend -> ExtensionPoint` | `1..*` falls Extend existiert | keine Extend-Instanz | gueltig, nicht anwendbar |
| 8 | `Satisfy -> Requirement` | `0..*` plus XOR | 15 Requirement-Satisfy-Instanzen belegen je Requirement-Zweig | gueltig |
| 9 | `Satisfy -> UseCase` | `0..*` plus XOR | 1 UseCase-Satisfy-Instanz belegt UseCase-Zweig | gueltig |
| 10 | `UseCase -> Scenario` | `1..*` | 3 Scenarios fuer `UC-A-01` | gueltig |
| 11 | `Scenario -> ScenarioStep` | `1..*` | Main: 9, Alternative: 2, Exception: 3 | gueltig |
| 12 | `Scenario -> StepRelation` | `0..*` | Main: 8, Alternative: 3, Exception: 3 | gueltig |
| 13 | `Scenario -> ParallelGroup` | `0..*` | 0 ParallelGroups | gueltig, optional |
| 14 | `ScenarioStep -> Event` | `0..*` | 5 triggeredBy-Zuordnungen; andere Steps begruendet leer | gueltig |
| 15 | `ScenarioStep -> Condition` | `0..1` Guard | jeder Step hoechstens 1 Guard; `A-MAIN-S07` ohne Guard | gueltig |
| 16 | `ScenarioStep -> StateAssertion` | `0..*` | jeder der 14 Steps besitzt 2 resultingState-Referenzen | gueltig |
| 17 | `StepRelation -> ScenarioStep` source | `1` | jede der 14 StepRelations besitzt genau einen Source-Step | gueltig |
| 18 | `StepRelation -> ScenarioStep` target | `1` | jede der 14 StepRelations besitzt genau einen Target-Step | gueltig |
| 19 | `ParallelGroup -> ScenarioStep` memberSteps | `2..*` falls ParallelGroup existiert | keine ParallelGroup | gueltig, nicht anwendbar |
| 20 | `Agent -> Entity` | Spezialisierung | `AgentBody` wird als Agent und damit als Entity-Subjekt verwendet | gueltig |
| 21 | `Entity -> Capability` provides | `0..*` | `AgentBody` stellt die drei A-Capabilities fachlich bereit | gueltig |
| 21a | `Entity -> EntityKind` kind | `0..1` | gesetzte Werte nutzen `agent`, `asset`, `zone`, `signal` oder `stateObject`; `SceneStateController` bleibt zulaessig untypisiert | gueltig |
| 22 | `ScenarioStep -> CapabilityUse` | `0..*` | 3 CapabilityUses an systemResponse-Steps; andere Steps 0 | gueltig |
| 23 | `CapabilityUse -> Capability` | `1` | jede der 3 CapabilityUses referenziert genau 1 Capability | gueltig |
| 24 | `Capability -> Effect` | `1..*` | jede der 3 Capabilities besitzt 2 Effects | gueltig |
| 24a | `Effect -> StateAssertion` evidencedBy | `0..*` | alle 6 Effects besitzen fachliche StateAssertion-Traces; die Referenz bleibt nicht-kompositiv | gueltig |
| 25 | `Capability -> FunctionBehavior` | `0..*` | 0 FunctionBehavior-Bruecken fuer A | gueltig, optional |
| 26 | `Capability -> RuntimeBinding` | `0..*` | jede der 3 Capabilities besitzt 1 RuntimeBinding | gueltig |
| 27 | `RuntimeBinding -> RuntimeAction` | `1..*` | jede der 3 RuntimeBindings besitzt 2 RuntimeActions | gueltig |
| 28 | `ValidationCase -> RuntimeBinding` | `0..*` | strukturelle Cases 0; runtime-nahe Cases 1..2 oder Referenzmenge | gueltig |

## Checkliste attributbasierter Kardinalitaeten

| Element oder Attribut | Soll | Ist fuer A | Bewertung |
| --- | --- | --- | --- |
| `Satisfy.satisfiedBy` | `1..*` | jede der 16 Satisfy-Instanzen hat mindestens ein erfuellendes Element | gueltig |
| `Satisfy.satisfiedRequirement` vs. `satisfiedUseCase` | XOR | keine Instanz belegt beide Zweige zugleich | gueltig |
| `Include.addition` | `1` falls Include existiert | keine Include-Instanz | gueltig, nicht anwendbar |
| `Extend.extendedCase` | `1` falls Extend existiert | keine Extend-Instanz | gueltig, nicht anwendbar |
| `Extend.extensionLocation` | `1..*` falls Extend existiert | keine Extend-Instanz | gueltig, nicht anwendbar |
| `Extend.condition` | `0..1` | keine Extend-Instanz | gueltig, nicht anwendbar |
| `Scenario.precondition` | `0..*` | Main besitzt 12 Preconditions; Alternative/Exception sind fachlich beschrieben | gueltig |
| `Scenario.postcondition` | `0..*` | Main besitzt 11 Postconditions; Alternative/Exception sind fachlich beschrieben | gueltig |
| `ScenarioStep.performedBy` | `0..1` | alle Steps leer, weil kein Step `actorIntent` ist | gueltig |
| `ScenarioStep.occurrenceProbability` | `0..1` | nicht genutzt | gueltig, optional |
| `StepRelation.guard` | `0..1` | jede Relation hoechstens 1 Guard; reine Sequenzen ohne Guard | gueltig |
| `StepRelation.probability` | `0..1` | nicht genutzt | gueltig, optional |
| `ParallelGroup.memberStep` | `2..*` falls ParallelGroup existiert | keine ParallelGroup | gueltig, nicht anwendbar |
| `Condition.randomVariable` | `0..*` | keine RandomVariable-Instanzen | gueltig, optional |
| `StateAssertion.subjectRef` | `1` | jede der 28 StateAssertions besitzt genau ein identifizierbares Subjekt | gueltig |
| `StateAssertion.expectedState` | `1` | jede der 28 StateAssertions besitzt genau einen erwarteten Zustand | gueltig |
| `Agent.playsActor` | `0..*` | nicht belegt | gueltig, optional |
| `Entity.kind` | `0..1` | jede typisierte Entity hat hoechstens einen zulaessigen v0.5-Wert; fehlende Typisierung ist erlaubt | gueltig |
| `CapabilityUse.capability` | `1` | jede der 3 CapabilityUses referenziert genau eine Capability | gueltig |
| `CapabilityUse.parameters` | `0..*` | jede CapabilityUse hat fachliche Parameter; beliebige Anzahl zulaessig | gueltig |
| `Capability.precondition` | `0..*` | jede der 3 Capabilities referenziert mehrere fachliche Conditions | gueltig |
| `Capability.promisedEffect` | `1..*` | jede Capability besitzt 2 Effects | gueltig |
| `Effect.observableBy` | `0..*` | alle 6 Effects referenzieren `ACT-A-03` | gueltig |
| `Effect.evidencedBy` | `0..*` | alle 6 Effects sind auf je eine fachlich passende StateAssertion rueckgebunden; Pflicht ist die Beziehung nicht | gueltig |
| `FunctionBehavior.behaviorKind` | `0..1` | nicht genutzt | gueltig, optional |
| `RuntimeBinding.capability` | `1` | jede der 3 RuntimeBindings referenziert genau eine Capability | gueltig |
| `RuntimeBinding.runtimeAction` | `1..*` | jede der 3 RuntimeBindings besitzt 2 RuntimeActions | gueltig |
| `RuntimeAction.inputSchema` | `0..1` | jede der 6 RuntimeActions besitzt genau 1 Input-Schema | gueltig |
| `RuntimeAction.outputSchema` | `0..1` | jede der 6 RuntimeActions besitzt genau 1 Output-Schema | gueltig |
| `ValidationCase.stimulus` | `0..*` | jeder der 8 ValidationCases hat mindestens einen Stimulus | gueltig |
| `ValidationCase.expectedOutcome` | `1..*` | jeder der 8 ValidationCases hat mindestens ein erwartetes Outcome | gueltig |

## Pruefung pro Szenario

| Scenario | Steps | StepRelations | ParallelGroups | Bewertung |
| --- | ---: | ---: | ---: | --- |
| `A-MAIN-SC01` | 9 | 8 | 0 | gueltig: mindestens ein Step, lineare Sequenz, keine unnoetige ParallelGroup |
| `A-ALT-SC01` | 2 | 3 | 0 | gueltig: Einstieg, interne Sequenz und Rueckfuehrung haben je Source und Target |
| `A-EX-SC01` | 3 | 3 | 0 | gueltig: Einstieg und Fehlersequenz haben je Source und Target |

## Pruefung der fachlich-technischen Bruecke

| Kette | Soll | Ist fuer A | Bewertung |
| --- | --- | --- | --- |
| `ScenarioStep -> CapabilityUse` | `0..*` | `A-MAIN-S05`, `A-MAIN-S06`, `A-EX-S02` haben je eine CapabilityUse | gueltig |
| `CapabilityUse -> Capability` | `1` | `A-CU-001`, `A-CU-002`, `A-CU-003` referenzieren je genau eine Capability | gueltig |
| `Capability -> Effect` | `1..*` | jede Capability hat zwei Effects | gueltig |
| `Capability -> RuntimeBinding` | `0..*` | jede Capability hat eine RuntimeBinding | gueltig |
| `RuntimeBinding -> RuntimeAction` | `1..*` | jede RuntimeBinding hat zwei RuntimeActions | gueltig |
| `ValidationCase -> RuntimeBinding` | `0..*` | alle RuntimeBindings werden durch ValidationCases geprueft; strukturelle Cases duerfen 0 Bindings haben | gueltig |

## Optional nicht instanziierte Beziehungen

| Beziehung | Warum keine Verletzung? |
| --- | --- |
| `UseCase -> ExtensionPoint` | `UC-A-01` nutzt aktuell kein `Extend`; `0..*` erlaubt 0. |
| `UseCase -> Include` | Kein verpflichtend wiederverwendeter Sub-UseCase erforderlich; `0..*` erlaubt 0. |
| `UseCase -> Extend` | Alternative und Exception sind als Scenarios modelliert, nicht als UseCase-Erweiterung; `0..*` erlaubt 0. |
| `ParallelGroup -> ScenarioStep` | Es existiert keine ParallelGroup; die `2..*`-Regel wird erst relevant, wenn eine ParallelGroup instanziiert wird. |
| `Capability -> FunctionBehavior` | Keine EAST-ADL-FunctionBehavior-Bruecke fuer A erforderlich; `0..*` erlaubt 0. |
| `Condition -> RandomVariable` | Keine probabilistische Condition in A formal instanziiert; `0..*` erlaubt 0. |
| `Agent -> Actor` playsRole | Actor/Agent-Trennung bleibt bewusst ohne Rollenbindung; `0..*` erlaubt 0. |
| `Entity.kind` | `SceneStateController` bleibt bewusst untypisiert; `0..1` erlaubt fehlende Typisierung. |

## Befund

Alle fuer Anwendungsfall A relevanten Pflichtkardinalitaeten sind erfuellt. Optionale Beziehungen sind entweder begruendet leer oder korrekt instanziiert. Es bleibt keine offene Kardinalitaetsverletzung.

## Konsequenz fuer Task 4.17

Task 4.17 kann nun die Invarianten fuer Anwendungsfall A pruefen. Die Kardinalitaeten sind bereits bestanden; der naechste Schritt muss vor allem die semantischen Regeln pruefen, insbesondere:

- keine direkte `ScenarioStep -> RuntimeAction`-Abbildung,
- keine Vermischung von Actor und Agent,
- keine technischen Details in Capabilities,
- Satisfy-XOR-Regel,
- genau ein Main Scenario pro UseCase.
