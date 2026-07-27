# Anwendungsfall B: Kardinalitaets- und Invariantenpruefung

Stand: 2026-07-07

Task: 8.13 `Kardinalitaeten und Invarianten fuer B pruefen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Ergebnis

Die bisher angelegten Instanzen fuer Anwendungsfall B verletzen keine Pflichtkardinalitaet und keine zentrale Invariante des kompakten Metamodells.

| Pruefbereich | Ergebnis |
| --- | --- |
| Sichtbare Diagrammkanten | bestanden |
| Attributbasierte Kardinalitaeten | bestanden |
| Pflichtbeziehungen | bestanden |
| Optional nicht instanziierte Beziehungen | zulaessig |
| Explizite Invarianten | bestanden |
| Abgeleitete Konsistenzregeln | bestanden oder nicht anwendbar |
| Offene Kardinalitaetsverletzungen | 0 |
| Offene Invariantenverletzungen | 0 |

Wichtig: Beziehungen mit Kardinalitaet `0..*` oder `0..1` muessen nicht belegt werden. Nicht instanziierte optionale Beziehungen werden deshalb nur dann als Problem gewertet, wenn ein konkretes B-Artefakt sie trotzdem benutzt oder wenn eine Folgeregel verletzt waere.

## Gepruefte Artefakte

| Artefakt | Zweck fuer die Pruefung |
| --- | --- |
| `use_case_B_requirements.md` | Requirement-Instanzen |
| `use_case_B_usecase_instance.md` | UseCase-Instanz |
| `use_case_B_actor_agent_mapping.md` | Actor-, Agent- und Actor-UseCase-Zuordnung |
| `use_case_B_coffee_machine_entity.md` | Kaffeemaschine als fachliche Entity |
| `use_case_B_scenario_instances.md` | UseCase-Scenario-Komposition |
| `use_case_B_scenario_step_instances.md` | ScenarioStep-Komposition und Schrittarten |
| `use_case_B_step_relations.md` | StepRelation-Instanzen und Branch-Anker |
| `use_case_B_event_condition_state_assertion_instances.md` | Events, Conditions, StateAssertions |
| `use_case_B_capability_use_instances.md` | ScenarioStep-CapabilityUse-Komposition |
| `use_case_B_capability_instances.md` | Capability- und Effect-Instanzen |
| `use_case_B_runtime_binding_instances.md` | Capability-RuntimeBinding-Zuordnung |
| `use_case_B_runtime_action_instances.md` | RuntimeBinding-RuntimeAction-Komposition |
| `use_case_B_validation_case_instances.md` | ValidationCase-Zuordnungen |

## Zentrale Zaehler fuer B

| Elementgruppe | Anzahl fuer B | Bewertung |
| --- | ---: | --- |
| Requirements | 18 | gueltig |
| UseCases | 1 | gueltig |
| Actors | 1 | gueltig |
| Agents | 1 | gueltig |
| Zentrale Objekt-Entities | 1 Kaffeemaschine, plus Kontext-Entities `Cup` und `BrewingRequest` | gueltig |
| Scenarios | 3 | gueltig |
| Main Scenarios pro UseCase | 1 | gueltig |
| ScenarioSteps | 28 | gueltig |
| StepRelations | 28 formal: 19 Main, 5 Alternative, 4 Exception | gueltig |
| Branch-Anker | 13 vorbereitete, nicht formale Anker | gueltig, keine StepRelations |
| ParallelGroups | 0 | gueltig, optional |
| Events | 24 | gueltig |
| Conditions | 34 | gueltig |
| StateAssertions | 30 | gueltig |
| CapabilityUses | 11 | gueltig |
| Capabilities | 11 | gueltig |
| Effects | 11 | gueltig |
| RuntimeBindings | 11 | gueltig |
| RuntimeActions | 25 | gueltig |
| ValidationCases | 10 | gueltig |
| Satisfy-Instanzen | 0 formal fuer B | gueltig, spaetere Konsolidierung |

## Checkliste sichtbarer Diagrammkanten

| Nr. | Beziehung | Soll | Ist fuer B | Bewertung |
| ---: | --- | --- | --- | --- |
| 1 | `RequirementsModel -> Requirement` | `0..*` | 18 B-Requirements im B-Artefaktkontext | gueltig |
| 2 | `RequirementsModel -> UseCase` | `0..*` | 1 UseCase `UC-B-01` | gueltig |
| 3 | `Actor -> UseCase` | `0..*` beidseitig | `ACT-B-01 Visitor` interagiert mit `UC-B-01` | gueltig |
| 4 | `UseCase -> ExtensionPoint` | `0..*` | 0 ExtensionPoints fuer `UC-B-01` | gueltig, optional |
| 5 | `UseCase -> Include` | `0..*` | 0 Include-Instanzen fuer `UC-B-01` | gueltig, optional |
| 6 | `UseCase -> Extend` | `0..*` | 0 Extend-Instanzen fuer `UC-B-01` | gueltig, optional |
| 7 | `Extend -> ExtensionPoint` | `1..*` falls Extend existiert | keine Extend-Instanz | gueltig, nicht anwendbar |
| 8 | `Satisfy -> Requirement/UseCase` | `0..*` plus XOR | noch keine formalen B-Satisfy-Instanzen | gueltig, nicht anwendbar |
| 9 | `UseCase -> Scenario` | `1..*` | 3 Scenarios fuer `UC-B-01` | gueltig |
| 10 | `Scenario -> ScenarioStep` | `1..*` | Main: 20, Alternative: 4, Exception: 4 | gueltig |
| 11 | `Scenario -> StepRelation` | `0..*` | Main: 19, Alternative: 5, Exception: 4 | gueltig |
| 12 | `Scenario -> ParallelGroup` | `0..*` | 0 ParallelGroups | gueltig, optional |
| 13 | `ScenarioStep -> Event` | `0..*` | alle 28 Steps haben mindestens ein fachliches Event | gueltig |
| 14 | `ScenarioStep -> Condition` | `0..1` Guard | jeder Step hat hoechstens eine direkte Guard Condition | gueltig |
| 15 | `ScenarioStep -> StateAssertion` | `0..*` | Steps haben 0, 1 oder mehrere resultingState-Referenzen | gueltig |
| 16 | `StepRelation -> ScenarioStep` source | `1` | jede der 28 formalen Relations besitzt genau einen Source-Step | gueltig |
| 17 | `StepRelation -> ScenarioStep` target | `1` | jede der 28 formalen Relations besitzt genau einen Target-Step | gueltig |
| 18 | `ParallelGroup -> ScenarioStep` memberSteps | `2..*` falls ParallelGroup existiert | keine ParallelGroup | gueltig, nicht anwendbar |
| 19 | `Agent -> Entity` | Spezialisierung | `ENT-B-01 VivianAssistant` wird als Agent und Entity verwendet | gueltig |
| 20 | `Entity -> Capability` provides | `0..*` | Vivian stellt 9 Capabilities bereit; CoffeeMachine stellt 2 Capabilities bereit | gueltig |
| 20a | `Entity -> EntityKind` kind | `0..1` | Vivian nutzt `agent`; CoffeeMachine und Cup nutzen `asset`; BrewingRequest nutzt `stateObject` | gueltig |
| 21 | `ScenarioStep -> CapabilityUse` | `0..*` | 11 CapabilityUses an 11 systemResponse-Steps | gueltig |
| 22 | `CapabilityUse -> Capability` | `1` | jede der 11 CapabilityUses referenziert genau 1 Capability | gueltig |
| 23 | `Capability -> Effect` | `1..*` | jede der 11 Capabilities besitzt 1 Effect | gueltig |
| 23a | `Effect -> StateAssertion` evidencedBy | `0..*` | alle 11 Effects besitzen mindestens einen passenden StateAssertion-Bezug; Conditions bleiben nur fachlicher Kontext, nicht Ziel der Evidence-Kante | gueltig |
| 24 | `Capability -> FunctionBehavior` | `0..*` | 0 FunctionBehavior-Bruecken fuer B | gueltig, optional |
| 25 | `Capability -> RuntimeBinding` | `0..*` | jede der 11 Capabilities besitzt 1 RuntimeBinding | gueltig |
| 26 | `RuntimeBinding -> RuntimeAction` | `1..*` | jede der 11 RuntimeBindings besitzt 2 oder 3 RuntimeActions | gueltig |
| 27 | `ValidationCase -> RuntimeBinding` | `0..*` | strukturelle Cases 0; runtime-nahe Cases 1..3 oder Referenzmenge | gueltig |

## Checkliste attributbasierter Kardinalitaeten

| Element oder Attribut | Soll | Ist fuer B | Bewertung |
| --- | --- | --- | --- |
| Genau ein `Scenario.kind = main` pro UseCase | `1` | `SC-B-01-MAIN` ist das einzige Main Scenario | gueltig |
| `Scenario.kind` | `main`, `alternative`, `exception` | je ein Main-, Alternative- und Exception-Scenario | gueltig |
| `Scenario.precondition` | `0..*` | Main 5, Alternative 1, Exception 1 | gueltig |
| `Scenario.postcondition` | `0..*` | Main 5, Alternative 2, Exception 5 | gueltig |
| `ScenarioStep.performedBy` | `0..1` | 6 ActorIntent-Steps mit `ACT-B-01 Visitor`; alle System- und Observation-Steps leer | gueltig |
| `ScenarioStep.occurrenceProbability` | `0..1` | nicht genutzt | gueltig, optional |
| `StepRelation.guard` | `0..1` | jede Relation hoechstens 1 Guard; reine Sequenzen ohne Guard | gueltig |
| `StepRelation.probability` | `0..1` | Hauptpfadrelationen mit `1.0`; andere ohne oder fachlich beschrieben | gueltig |
| `StateAssertion.subjectRef` | `1` | jede der 30 StateAssertions besitzt genau ein identifizierbares Subjekt | gueltig |
| `StateAssertion.expectedState` | `1` | jede der 30 StateAssertions besitzt genau einen pruefbaren Zustand | gueltig |
| `Agent.playsActor` | `0..*` | Vivian spielt keine Actor-Rolle in der Baseline | gueltig, optional |
| `Entity.kind` | `0..1` | jede typisierte B-Entity nutzt hoechstens einen zulaessigen v0.5-Wert; untypisierte Entities waeren ebenfalls erlaubt | gueltig |
| `CapabilityUse.capability` | `1` | jede der 11 CapabilityUses referenziert genau eine Capability | gueltig |
| `CapabilityUse.parameters` | `0..*` | fachliche Parameter sind gesetzt, Anzahl frei | gueltig |
| `Capability.precondition` | `0..*` | jede der 11 Capabilities referenziert Conditions oder StateAssertions | gueltig |
| `Capability.promisedEffect` | `1..*` | jede der 11 Capabilities besitzt genau einen Effect | gueltig |
| `Effect.observableBy` | `0..*` | nicht formal belegt; StateAssertion-Bezug dokumentiert Beobachtbarkeit | gueltig, optional |
| `Effect.evidencedBy` | `0..*` | StateAssertion-Bezuege sind vorhanden, aber nicht als Pflichtbeziehung erzwungen; Conditions werden nicht als Evidence-Ziel gezaehlt | gueltig |
| `RuntimeBinding.capability` | `1` | jede der 11 RuntimeBindings referenziert genau eine Capability | gueltig |
| `RuntimeBinding.runtimeAction` | `1..*` | jede Binding besitzt mindestens zwei RuntimeActions | gueltig |
| `RuntimeAction.inputSchema` | `0..1` | jede der 25 RuntimeActions besitzt genau 1 Input-Schema | gueltig |
| `RuntimeAction.outputSchema` | `0..1` | jede der 25 RuntimeActions besitzt genau 1 Output-Schema | gueltig |
| `ValidationCase.stimulus` | `0..*` | jeder der 10 ValidationCases hat mindestens einen Stimulus | gueltig |
| `ValidationCase.expectedOutcome` | `1..*` | jeder der 10 ValidationCases hat mindestens ein erwartetes Outcome | gueltig |

## Pruefung pro Szenario

| Scenario | Steps | StepRelations | ParallelGroups | Bewertung |
| --- | ---: | ---: | ---: | --- |
| `SC-B-01-MAIN` | 20 | 19 | 0 | gueltig: mindestens ein Step, lineare Hauptsequenz, keine unnoetige ParallelGroup |
| `SC-B-01-ALT01` | 4 | 5 | 0 | gueltig: Einstieg, interne Sequenz und Rueckfuehrung haben je Source und Target |
| `SC-B-01-EX01` | 4 | 4 | 0 | gueltig: Einstieg und Fehlersequenz haben je Source und Target, keine Rueckfuehrung |

## Pruefung der Schrittarten

| ScenarioStep.kind | Anzahl | Kardinalitaets- und Invariantenbewertung |
| --- | ---: | --- |
| `actorIntent` | 6 | alle sechs Schritte besitzen `performedBy = ACT-B-01 Visitor` |
| `systemResponse` | 11 | alle elf Schritte besitzen keine `performedBy`-Actor-Referenz und sind ueber `CapabilityUse` angebunden |
| `environmentObservation` | 11 | alle elf Schritte besitzen keine `performedBy`-Actor-Referenz und werden ueber Events, Conditions und StateAssertions beschrieben |

Damit ist die Actor/Agent/Entity-Trennung konsistent:

- `Visitor` ist externe Actor-Rolle.
- `VivianAssistant` ist Agent/Entity innerhalb des betrachteten Systems.
- `CoffeeMachine` ist fachliche Entity und Interaktionsobjekt, aber kein Actor.

## Pruefung der fachlich-technischen Bruecke

| Kette | Soll | Ist fuer B | Bewertung |
| --- | --- | --- | --- |
| `ScenarioStep -> CapabilityUse` | `0..*` | 11 systemResponse-Steps haben je eine CapabilityUse | gueltig |
| `CapabilityUse -> Capability` | `1` | `B-CU-001` bis `B-CU-011` referenzieren je genau eine Capability | gueltig |
| `Capability -> Effect` | `1..*` | jede Capability hat genau einen Effect | gueltig |
| `Capability -> RuntimeBinding` | `0..*` | jede Capability hat eine RuntimeBinding | gueltig |
| `RuntimeBinding -> RuntimeAction` | `1..*` | jede RuntimeBinding hat 2 oder 3 RuntimeActions | gueltig |
| `ValidationCase -> RuntimeBinding` | `0..*` | alle RuntimeBindings werden durch ValidationCases geprueft; strukturelle Cases duerfen 0 Bindings haben | gueltig |

## Explizite Invarianten

| Nr. | Regel | Bewertung fuer B | Ergebnis |
| ---: | --- | --- | --- |
| E1 | Genau ein `Scenario.kind = main` pro UseCase. | `UC-B-01` besitzt genau `SC-B-01-MAIN` als Main Scenario. | bestanden |
| E2 | `Include` nur fuer verpflichtende Wiederverwendung. | B nutzt kein Include; Hauptpfad, Alternative und Exception sind Scenarios desselben Use Case. | bestanden |
| E3 | `Extend.extensionLocation` muss auf ExtensionPoints des extendedCase zeigen. | Kein Extend in B instanziiert; daher keine fehlerhafte ExtensionLocation moeglich. | nicht anwendbar, bestanden |
| E4 | `Satisfy` referenziert Requirement oder UseCase, nicht beides. | Keine formalen B-Satisfy-Instanzen; keine XOR-Verletzung moeglich. | nicht anwendbar, bestanden |
| E5 | `ScenarioStep` darf nicht direkt auf RuntimeAction, API, Tool oder Topic zeigen. | Keine `B-RA-*`-Referenz in ScenarioSteps, CapabilityUses oder Capabilities gefunden. | bestanden |
| E6 | `Capability` enthaelt keine technischen Endpoint- oder Tool-Daten. | Capabilities enthalten Intent, Preconditions und Effects; technische Endpoints stehen ausschliesslich in RuntimeActions. | bestanden |
| E7 | ParallelGroup-Schritte muessen zum selben Scenario gehoeren. | B nutzt keine ParallelGroup; `0` ParallelGroups ist fachlich begruendet. | nicht anwendbar, bestanden |
| E8 | `actorIntent`-Steps sollten `performedBy` auf Actor setzen; Systemantworten laufen ueber CapabilityUse. | Sechs ActorIntent-Steps zeigen auf `ACT-B-01`; elf Systemantworten laufen ueber CapabilityUse. | bestanden |

## Abgeleitete Konsistenzregeln

| Nr. | Regel | Bewertung fuer B | Ergebnis |
| ---: | --- | --- | --- |
| B1 | Dynamischer UseCase besitzt mindestens ein Scenario. | `UC-B-01` besitzt 3 Scenarios. | bestanden |
| B2 | Jedes Scenario besitzt mindestens einen ScenarioStep. | Main 20, Alternative 4, Exception 4 Steps. | bestanden |
| B3 | Jede formale StepRelation besitzt Source und Target. | 28 formale Relations besitzen je Source und Target. | bestanden |
| B4 | Branch-Anker duerfen nicht als formale StepRelations mit fehlendem Target gezaehlt werden. | 13 Branch-Anker sind als nicht formale Vorbereitungen dokumentiert. | bestanden |
| B5 | Jeder Step hat hoechstens eine direkte Guard Condition. | In Task 8.7 fuer alle 28 Steps bestaetigt. | bestanden |
| B6 | Jede StateAssertion referenziert genau ein identifizierbares Subjekt. | Vivian, CoffeeMachine, Cup und BrewingRequest sind als Subjekte verwendet. | bestanden |
| B7 | Actor, Agent und Entity werden nicht vermischt. | Visitor, Vivian und CoffeeMachine sind getrennt modelliert. | bestanden |
| B8 | SystemResponses erhalten CapabilityUse, ActorIntent und EnvironmentObservation nicht kuenstlich. | 11 von 11 SystemResponses haben CapabilityUse; Actor- und Umweltsteps haben keine. | bestanden |
| B9 | Jede CapabilityUse referenziert eine existierende Capability. | 11 Referenzen, 11 definierte Capabilities, keine fehlenden Referenzen. | bestanden |
| B10 | Jede Capability besitzt mindestens einen Effect. | 11 Capabilities, 11 Effects, keine fehlenden Effects. | bestanden |
| B11 | Jede RuntimeBinding referenziert eine existierende Capability. | 11 Binding-Referenzen, 11 definierte Capabilities. | bestanden |
| B12 | Jede RuntimeBinding besitzt mindestens eine RuntimeAction. | alle 11 Bindings besitzen 2 oder 3 RuntimeActions. | bestanden |
| B13 | Jede RuntimeAction besitzt genau einen Owner. | 25 RuntimeActions liegen unter genau einer Binding-ID. | bestanden |
| B14 | ValidationCases besitzen Stimulus und erwartetes Outcome. | alle 10 ValidationCases erfuellen beide Felder. | bestanden |
| B15 | RuntimeActions sind technische Details, aber keine fachlichen Steps. | RuntimeAction-IDs erscheinen nur im RuntimeAction-Artefakt und als pruefende Stimuli in ValidationCases. | bestanden |

## Optional nicht instanziierte Beziehungen

| Beziehung | Warum keine Verletzung? |
| --- | --- |
| `UseCase -> ExtensionPoint` | `UC-B-01` nutzt aktuell kein `Extend`; `0..*` erlaubt 0. |
| `UseCase -> Include` | Kein verpflichtend wiederverwendeter Sub-UseCase erforderlich; `0..*` erlaubt 0. |
| `UseCase -> Extend` | Alternative und Exception sind als Scenarios modelliert, nicht als UseCase-Erweiterung; `0..*` erlaubt 0. |
| `Satisfy` | Formale B-Satisfy-Instanzen werden spaeter konsolidiert; bis dahin existiert keine fehlerhafte Instanz. |
| `ParallelGroup -> ScenarioStep` | Es existiert keine ParallelGroup; die `2..*`-Regel wird erst relevant, wenn eine ParallelGroup instanziiert wird. |
| `Capability -> FunctionBehavior` | Keine EAST-ADL-FunctionBehavior-Bruecke fuer B erforderlich; `0..*` erlaubt 0. |
| `Condition -> RandomVariable` | Keine probabilistische Condition in B formal instanziiert; `0..*` erlaubt 0. |
| `Agent -> Actor` playsRole | Vivian bleibt in der Baseline Agent/Entity und spielt keine Actor-Rolle; `0..*` erlaubt 0. |

## Direkte RuntimeAction-Abkuerzung

Die wichtigste Invariante fuer B ist ausdruecklich bestanden:

| Frage | Ergebnis |
| --- | --- |
| Gibt es eine direkte `ScenarioStep -> RuntimeAction`-Abbildung? | nein |
| Gibt es eine direkte `CapabilityUse -> RuntimeAction`-Abbildung? | nein |
| Gibt es eine direkte `Capability -> RuntimeAction`-Abbildung? | nein |
| Gibt es technische Endpoints in ScenarioSteps? | nein |
| Gibt es technische Endpoints in Capabilities? | nein |
| Liegen technische Endpoints, Topics und Schemas in RuntimeActions? | ja, dort gehoeren sie hin. |

## Befund

Anwendungsfall B ist nach dem aktuellen Stand kardinalitaetskonform und invariantentreu modelliert. Die fachliche Ebene bleibt von der technischen Runtime-Ebene getrennt. Die zentrale Kette

`ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

ist fuer alle systemischen Schritte vollstaendig abbildbar, ohne dass Actor-Intent-Schritte oder Beobachtungssteps kuenstlich technisiert werden.

Es bleiben keine offenen Kardinalitaets- oder Invariantenverletzungen.

## Konsequenz fuer Task 9.1

Task 9.1 kann nun die direkt modellierbaren Elemente von Anwendungsfall B markieren. Die Pruefung liefert dafuer die gesicherte Grundlage: UseCase, Actor, Agent, Entity, Scenarios, Steps, Events, Conditions, StateAssertions, Capabilities, RuntimeBindings, RuntimeActions und ValidationCases sind im aktuellen Modell konsistent instanziierbar.
