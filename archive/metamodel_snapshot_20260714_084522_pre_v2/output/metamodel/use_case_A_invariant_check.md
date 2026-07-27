# Anwendungsfall A: Invariantenpruefung

Stand: 2026-07-07

Task: 4.17 `Invarianten fuer A pruefen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Ergebnis

Die Invarianten und abgeleiteten Konsistenzregeln des aktuellen Metamodells sind fuer Anwendungsfall A erfuellt.

| Pruefbereich | Ergebnis |
| --- | --- |
| Explizite Invarianten `E1` bis `E8` | bestanden |
| Abgeleitete Konsistenzregeln `A1` bis `A20` | bestanden oder nicht anwendbar |
| Korrigierte Konsistenzhinweise waehrend der Pruefung | 1 Gruppe: Rollenzustand des Agenten normalisiert |
| Offene Invariantenverletzungen | 0 |

## Korrigierter Befund waehrend der Pruefung

Beim Invarianten-Scan gab es in fruehen Entwurfsartefakten noch die alte Kurzschreibweise `AgentRoleState` als scheinbar eigenstaendiges Subjekt. Die formale StateAssertion-Datei hatte diese Schreibweise in Task 4.9 bereits korrekt normalisiert: Rollenzustaende werden als Zustand des identifizierbaren Subjekts `AgentBody` modelliert, z. B. `subjectRef = AgentBody`, `expectedState = roleState=executor`.

Diese fruehen Artefakte wurden an die formale Modellierung angeglichen:

| Angepasstes Artefakt | Korrektur |
| --- | --- |
| `use_case_A_step_state_assertions.md` | `subjectRef = AgentRoleState` wurde zu `subjectRef = AgentBody`, `expectedState = roleState=...`. |
| `use_case_A_exception_scenario.md` | Exception-Zustand nutzt `AgentBody.roleState = blocked`. |
| `use_case_A_scene_objects.md` | Rollenstatus wird als `AgentBody.roleState` beschrieben. |
| `use_case_A_alternatives_exceptions.md` | Blockierter Rollenstatus wird als `AgentBody.roleState = blocked` beschrieben. |
| `use_case_A_condition_instances.md` | Conditions verwenden `AgentBody.roleState` statt freistehendem `AgentRoleState`. |
| `use_case_A_step_guards.md` | Guard-Ausdruecke verwenden `AgentBody.roleState`. |
| `use_case_A_dynamic_changes.md` | Rollenwechsel wird als `AgentBody.roleState: observer -> executor` beschrieben. |
| `use_case_A_goal.md` | Zielbezug fuer Rolle nutzt `AgentBody.roleState`. |
| `use_case_A_postconditions.md` | Nachbedingungen nutzen `AgentBody.roleState`. |
| `use_case_A_preconditions.md` | Vorbedingungen nutzen `AgentBody.roleState`. |
| `use_case_A_requirements.md` | Verifikationsideen nutzen `AgentBody.roleState`. |
| `use_case_A_scenario_instances.md` | Exception-Postcondition nutzt `AgentBody.roleState = blocked`. |

`use_case_A_state_assertion_instances.md` enthaelt die alte Schreibweise nur noch bewusst als Normalisierungshinweis. Das ist keine Verletzung, sondern dokumentiert die Korrekturregel.

## Explizite Invarianten

| Nr. | Regel | Bewertung fuer A | Ergebnis |
| ---: | --- | --- | --- |
| E1 | Genau ein `Scenario.kind = main` pro UseCase. | `UC-A-01` besitzt genau `A-MAIN-SC01` als Main Scenario; `A-ALT-SC01` und `A-EX-SC01` sind zusaetzlich erlaubt. | bestanden |
| E2 | `Include` nur fuer verpflichtende Wiederverwendung. | Anwendungsfall A nutzt kein Include; Alternative und Exception sind als Scenario/StepRelation modelliert. | bestanden |
| E3 | `Extend.extensionLocation` muss auf ExtensionPoints des extendedCase zeigen. | Kein Extend in A instanziiert; daher keine fehlerhafte ExtensionLocation moeglich. | nicht anwendbar, bestanden |
| E4 | `Satisfy` referenziert Requirement oder UseCase, nicht beides. | `SAT-A-REQ-*` belegt nur Requirements; `SAT-A-UC-001` belegt nur den UseCase. | bestanden |
| E5 | `ScenarioStep` darf nicht direkt auf RuntimeAction, API, Tool oder Topic zeigen. | ScenarioSteps zeigen auf Events, Conditions, StateAssertions und CapabilityUses; RuntimeActions liegen nur unter RuntimeBindings. | bestanden |
| E6 | `Capability` enthaelt keine technischen Endpoint- oder Tool-Daten. | Capabilities enthalten Intent, Preconditions und Effects; technische Endpoints stehen ausschliesslich in RuntimeActions. | bestanden |
| E7 | ParallelGroup-Schritte muessen zum selben Scenario gehoeren. | A nutzt keine ParallelGroup; `0` ParallelGroups ist fachlich begruendet. | nicht anwendbar, bestanden |
| E8 | `actorIntent`-Steps sollten `performedBy` auf Actor setzen; Systemantworten laufen ueber CapabilityUse. | A besitzt keine `actorIntent`-Steps; alle `systemResponse`-Steps nutzen CapabilityUse. | bestanden |

## Abgeleitete Konsistenzregeln

| Nr. | Regel | Bewertung fuer A | Ergebnis |
| ---: | --- | --- | --- |
| A1 | RequirementsModel kann beliebig viele Requirements und UseCases enthalten. | 15 Requirements und 1 UseCase sind im A-Kontext angelegt. | bestanden |
| A2 | UseCase kann beliebig viele ExtensionPoints, Includes und Extends besitzen. | A nutzt jeweils 0; das ist zulaessig. | bestanden |
| A3 | Dynamischer UseCase besitzt mindestens ein Scenario. | `UC-A-01` besitzt 3 Scenarios. | bestanden |
| A4 | Jedes Scenario besitzt mindestens einen ScenarioStep. | Main 9, Alternative 2, Exception 3 Steps. | bestanden |
| A5 | ScenarioStep gehoert genau zu seinem Scenario; ParallelGroup besitzt Schritte nicht. | Jeder Step hat genau ein Owner-Scenario; keine ParallelGroup. | bestanden |
| A6 | StepRelation hat genau Source und Target. | Alle 14 StepRelations besitzen genau einen Source- und einen Target-Step. | bestanden |
| A7 | ParallelGroup braucht mindestens zwei Steps. | Keine ParallelGroup instanziiert. | nicht anwendbar, bestanden |
| A8 | ScenarioStep kann 0..* Events haben. | Einige Steps haben Events, andere begruendet keine. | bestanden |
| A9 | ScenarioStep hat hoechstens eine direkte Guard Condition. | Jeder Step hat 0 oder 1 Guard. | bestanden |
| A10 | ScenarioStep kann 0..* StateAssertions haben. | Jeder A-Step besitzt zwei resultingState-Referenzen. | bestanden |
| A11 | ScenarioStep kann 0..* CapabilityUses haben. | Drei systemResponse-Steps besitzen je eine CapabilityUse; Beobachtungssteps keine. | bestanden |
| A12 | Jede CapabilityUse referenziert genau eine Capability. | `A-CU-001` bis `A-CU-003` referenzieren je genau eine Capability. | bestanden |
| A13 | Jede Capability besitzt mindestens einen Effect. | Jede der 3 Capabilities besitzt 2 Effects. | bestanden |
| A14 | Capability kann 0..* RuntimeBindings besitzen. | Jede A-Capability besitzt eine RuntimeBinding. | bestanden |
| A15 | RuntimeBinding gehoert zu genau einer Capability und enthaelt mindestens eine RuntimeAction. | Jede der 3 RuntimeBindings referenziert eine Capability und besitzt 2 RuntimeActions. | bestanden |
| A16 | RuntimeAction ist Ort fuer Endpoints, Tools, Topics und Schemas. | Endpoints und Schemas stehen nur in `use_case_A_runtime_action_instances.md`. | bestanden |
| A17 | Agent ist Entity, aber nicht automatisch Actor. | `AgentBody` ist Agent/Entity; `ACT-A-*` bleiben externe Rollen. | bestanden |
| A18 | Entity provides Capability beschreibt Bereitstellung, nicht jeden Schritt. | `AgentBody` stellt fachliche Capabilities bereit; Nutzung erfolgt ueber CapabilityUse. | bestanden |
| A19 | ValidationCase braucht mindestens ein erwartetes Ergebnis. | Alle 8 ValidationCases besitzen ExpectedOutcome. | bestanden |
| A20 | ValidationCase prueft RuntimeBinding, besitzt sie aber nicht. | RuntimeBindings bleiben eigene Instanzen; ValidationCases referenzieren sie pruefend. | bestanden |

## Zentrale semantische Trennlinien

| Trennlinie | Pruefbefund |
| --- | --- |
| Actor vs. Agent | Actoren sind `ScenarioDesigner`, `SceneParticipant`, `SceneObserver`; der handelnde modellierte Agent ist `AgentBody`. Keine Vermischung gefunden. |
| Fachlicher Schritt vs. technische Aktion | ScenarioSteps bleiben fachlich; technische Endpoints stehen nur in RuntimeActions. |
| Capability vs. RuntimeBinding | Capabilities beschreiben fachliche Faehigkeiten; RuntimeBindings ordnen diese an `GenericVRSceneRuntime` an. |
| RuntimeBinding vs. RuntimeAction | RuntimeBinding ist Container/Zuordnung; RuntimeActions sind die konkreten technischen Einzelaktionen. |
| Effect vs. RuntimeAction | Effects beschreiben beobachtbare fachliche Wirkungen; RuntimeActions realisieren technische Aufrufe. |
| ValidationCase vs. RuntimeBinding | ValidationCases pruefen RuntimeBindings, besitzen sie aber nicht. |

## Direkte RuntimeAction-Abkuerzung

Die wichtigste Invariante aus Task 4.17 ist ausdruecklich bestanden:

| Frage | Ergebnis |
| --- | --- |
| Gibt es eine direkte `ScenarioStep -> RuntimeAction`-Abbildung? | nein |
| Gibt es eine direkte `CapabilityUse -> RuntimeAction`-Abbildung? | nein |
| Gibt es technische Endpoints in ScenarioSteps? | nein |
| Gibt es technische Endpoints in Capabilities? | nein |
| Liegen technische Endpoints in RuntimeActions? | ja, dort gehoeren sie hin. |

## Befund

Anwendungsfall A ist nach dem aktuellen Stand invariantentreu modelliert. Die einzige gefundene Inkonsistenz war eine alte Schreibweise fuer den Rollenzustand des Agenten in fruehen Entwurfsdateien; sie wurde auf `AgentBody.roleState` normalisiert. Es bleiben keine offenen Invariantenverletzungen.

## Konsequenz fuer Task 5.1

Task 5.1 kann nun die direkt modellierbaren Elemente von Anwendungsfall A markieren. Die Invariantenpruefung liefert dafuer die gesicherte Grundlage: Die bestehende Abbildung ist kardinalitaetskonform, invariantentreu und trennt fachliche Modellierung von technischer Runtime-Ausfuehrung.
