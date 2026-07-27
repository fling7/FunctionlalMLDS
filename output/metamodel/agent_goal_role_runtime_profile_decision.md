# Entscheidung 10.8: Brauchen Agenten eigene Ziele, Rollenwechsel oder Laufzeitprofile?

Stand: 2026-07-07

Task: 10.8 `Pruefen, ob Agenten eigene Ziele, Rollenwechsel oder Laufzeitprofile brauchen`

Verglichene Use Cases:

- `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`
- `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Bezugsdateien:

- `entity_agent_scene_object_decision.md`
- `state_assertion_object_state_decision.md`
- `capability_runtime_vivian_action_decision.md`
- `spatial_relationship_decision.md`
- `interaction_object_affordance_decision.md`
- `use_case_A_goal.md`
- `use_case_A_dynamic_changes.md`
- `use_case_A_indirect_modelability.md`
- `use_case_A_capability_instances.md`
- `use_case_A_effect_instances.md`
- `use_case_B_vivian_classification.md`
- `use_case_B_capability_instances.md`

## Entscheidung

Agenten brauchen fuer den aktuellen kompakten Kern keine eigenen Kernklassen `AgentGoal`, `AgentRole`, `RoleTransition` oder `RuntimeProfile`.

Fuer die beiden Baseline-Beispiele reichen:

- `Agent --|> Entity` fuer die Identitaet aktiver Systemsubjekte,
- `UseCase.goal` und `Scenario.goal` fuer fachliche Zielaussagen,
- `Capability` und `CapabilityUse` fuer fachliche Faehigkeiten und ihre Nutzung,
- `Condition` fuer Vorbedingungen und Guards,
- `StateAssertion` fuer Rollen-, Modus-, Aktivitaets- und Ergebniszustaende,
- `RuntimeBinding` und `RuntimeAction` fuer technische Anbindung.

Ein optionales `AgentBehaviorModule` wird erst benoetigt, wenn Agenten eigene interne Ziele, Prioritaeten, Policies, Rollenmodelle, erlaubte Rollentransitionen, Planungsentscheidungen oder konkurrierende Absichten maschinenlesbar ausdruecken sollen.

Ein optionales `RuntimeProfileModule` wird erst benoetigt, wenn Laufzeitvarianten, Plattformprofile, Adapterversionen, Ressourcen, Latenz, Modellversionen oder Ausfuehrungsparameter nicht nur dokumentiert, sondern formal auswaehlbar und validierbar sein muessen.

Damit lautet die Entscheidung:

| Frage | Entscheidung |
| --- | --- |
| Muss der Kern um `AgentGoal` erweitert werden? | nein |
| Muss der Kern um `AgentRole` oder `RoleTransition` erweitert werden? | nein |
| Muss der Kern um `RuntimeProfile` erweitert werden? | nein |
| Reicht `Agent` plus `Capability` fuer die Baseline? | ja, zusammen mit `Condition`, `StateAssertion`, `Effect` und `RuntimeBinding` |
| Reicht `Agent` plus `Capability` fuer autonome Planung oder formale Rollenautomaten? | nein |
| Reicht `Agent` plus `Capability` fuer technische Laufzeitprofile? | nein; diese gehoeren nicht in `Agent`, sondern unter Runtime-Ergaenzung |
| Empfohlene Behandlung | Kern unveraendert; optional `AgentBehaviorModule` und optional `RuntimeProfileModule` |

## Begriffsabgrenzung

| Konzept | Aufgabe | Beispiel | Nicht verwechseln mit |
| --- | --- | --- | --- |
| `Agent` | Identifizierbare aktive Systeminstanz. | `AgentBody`, `VivianAssistant` | Kein externer `Actor` und kein technisches Profil. |
| `UseCase.goal` | Fachlicher Zweck des gesamten Use Case. | Dynamisches Agentenverhalten pruefbar modellieren. | Kein internes Agentenziel. |
| `Scenario.goal` | Beobachtbarer Erfolg eines konkreten Szenarios. | Agent erreicht Zielzone und Rueckmeldung ist bestaetigt. | Kein Planner-Ziel. |
| `Capability` | Fachliche Faehigkeit einer Entity oder eines Agenten. | Rolle annehmen, Zielhandlung ausfuehren, Vivian fuehrt an. | Keine Motivation, keine Prioritaet, kein Runtime-Profil. |
| `StateAssertion` | Erwarteter Zustand eines Subjekts. | `AgentBody.roleState = executor`, `VivianAssistant.mode = guiding` | Kein formaler Zustandsautomat. |
| `Condition` | Vorbedingung, Guard oder Nachbedingung. | `AgentBody.roleState != blocked` | Keine Policy oder Planner-Entscheidung. |
| `RuntimeBinding` | Technische Bindung einer fachlichen Capability. | VR-Rollenwechsel-Binding, Vivian-Guidance-Binding | Kein fachliches Agentenziel. |
| `RuntimeProfile` | Optionale technische Ausfuehrungsvariante. | Avatar/TTS/LLM-Profil, VR-Agentencontroller-Version | Kein Kernkonzept und keine Agentenrolle. |

## Warum `Agent` plus `Capability` nicht immer ausreicht

`Agent` plus `Capability` reicht, wenn modelliert werden soll, welches aktive Subjekt welche fachliche Faehigkeit bereitstellt oder nutzt.

Es reicht nicht, wenn das Modell beantworten muss, warum ein Agent eine Faehigkeit auswaehlt, wie er zwischen konkurrierenden Zielen priorisiert, welche Rollenwechsel erlaubt sind oder welches technische Profil zur Laufzeit benutzt werden soll.

| Fehlender Aspekt | Warum nicht in `Agent`/`Capability` | Beispiel |
| --- | --- | --- |
| Internes Ziel | `Capability` beschreibt Koennen, nicht Wollen oder Zweckauswahl. | Agent soll `TargetZone` erreichen, aber zugleich Grenzverletzung vermeiden. |
| Zielprioritaet | Der Kern kennt keine Prioritaets-, Utility- oder Konfliktregel. | Sicherheit vor Zielerreichung. |
| Rollenmodell | `roleState=executor` ist ein Zustand, aber keine Rollendefinition. | erlaubte Rollen `observer`, `executor`, `blocked`, `completed` |
| Erlaubte Rollentransition | Vor- und Zielzustand sind verteilt ueber `Condition` und `StateAssertion`. | `observer -> executor` erlaubt, `blocked -> executor` verboten |
| Entscheidungs-Policy | Guards beschreiben Zulaessigkeit, aber keine Auswahlstrategie. | Bei temporaerer Blockade warten oder Alternativroute waehlen |
| Laufzeitprofil | `Capability` darf keine Endpoint-, Modell-, TTS-, Avatar- oder Controllerdetails enthalten. | Vivian nutzt LLM-Profil A oder lokales Regelprofil |
| Ressourcen und QoS | Der Kern beschreibt keine Latenz, Kosten, Rate Limits oder Zuverlaessigkeit. | Assistant antwortet unter 2 s; Agentencontroller mit bestimmter Tickrate |
| Mehrere technische Realisierungen | `RuntimeBinding` erlaubt mehrere Bindings, aber keine formale Auswahlregel. | VR-Agent kann Unity- oder WebXR-Controller nutzen |
| Personalisierung | Agent/Capability tragen keine Benutzer- oder Lernprofile. | Vivian erklaert anders fuer Anfaenger als fuer Experten |

Diese Aspekte sollen nicht in den Kern gezwungen werden. Sonst wuerde `Agent` zu einem Mischcontainer fuer Identitaet, Autonomie, Rollenautomat, Dialogstrategie und Runtime-Konfiguration.

## Bewertung fuer Anwendungsfall A

Anwendungsfall A ist der staerkste Treiber fuer Agentenrollen und Zielzustand.

| A-Aspekt | Aktuelle Kernabbildung | Reicht fuer Baseline? | Wann ein Agent-Modul noetig wird |
| --- | --- | --- | --- |
| Use-Case-Ziel | `UseCase.goal` aus `use_case_A_goal.md` | ja | Wenn Zielhierarchien oder konkurrierende Agentenziele modelliert werden. |
| Szenarioerfolg | `Scenario.goal`, Conditions und StateAssertions `A-G1` bis `A-G7` | ja | Wenn Erfolg intern geplant statt nur pruefbar beschrieben wird. |
| Rollenwechsel | `A-CU-001 -> A-CAP-ADOPT-EXECUTOR-ROLE -> A-EFF-ROLE-EXECUTOR -> StateAssertion roleState=executor` | ja | Wenn Rollen als eigene Elemente mit erlaubten Transitionen, Rechten und Policies benoetigt werden. |
| Aktivitaet | `StateAssertion expectedState = moving`, `waiting`, `acting` | ja | Wenn Aktivitaeten als formaler Lifecycle oder Zustandsautomat gelten sollen. |
| Blockadebehandlung | `Condition`, `StepRelation.kind = alternative|exception`, `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | ja | Wenn der Agent selbst zwischen Strategien waehlt. |
| Bewegung zur Zielzone | `Capability`, `Effect`, `StateAssertion`, optional RuntimeBinding | ja | Wenn Pfadplanung, Bewegungsmodus oder Navigation Policies modelliert werden. |
| Runtime-Ausfuehrung | `Capability -> RuntimeBinding -> RuntimeAction` | ja | Wenn Controllerprofile, Plattformversionen oder Auswahlregeln formal werden. |

### Beispiel A: Rollenwechsel

Die Baseline bildet den Rollenwechsel ohne eigene `AgentRole`-Klasse ab:

| Ebene | Instanz |
| --- | --- |
| Agent | `AgentBody` |
| Vorbedingung | `AgentBody.roleState != blocked`, Zielzone erreichbar |
| ScenarioStep | `A-MAIN-S05` |
| CapabilityUse | `A-CU-001` |
| Capability | `A-CAP-ADOPT-EXECUTOR-ROLE` |
| Effect | `A-EFF-ROLE-EXECUTOR`, `A-EFF-AGENT-ACTING` |
| StateAssertion | `AgentBody.roleState = executor`, `AgentBody.expectedState = acting` |
| RuntimeBinding | `A-RB-ROLE-EXECUTOR-VR` |
| RuntimeAction | `A-RA-ROLE-SET`, `A-RA-ROLE-SYNC` |

Das ist fuer die Baseline ausreichend, weil der Ablauf vorgibt, wann der Rollenwechsel stattfindet, und der Zielzustand beobachtbar ist.

Ein Agent-Modul waere noetig, wenn z. B. folgende Aussage formal werden soll:

`AgentBody darf nur von observer nach executor wechseln, wenn rolePolicy.allows(observer, executor) gilt; ein Wechsel aus blocked nach executor ist verboten; safetyGoal hat hoehere Prioritaet als reachTargetGoal.`

Diese Aussage laesst sich mit `Agent` plus `Capability` nicht sauber modellieren, weil dort Rollenregeln und Zielprioritaeten fehlen.

## Bewertung fuer Anwendungsfall B

Anwendungsfall B ist weniger durch autonome Agentenplanung getrieben, aber Vivian zeigt klar die Grenze zwischen Agent, Assistenzverhalten und Runtime-Profil.

| B-Aspekt | Aktuelle Kernabbildung | Reicht fuer Baseline? | Wann ein Zusatzmodul noetig wird |
| --- | --- | --- | --- |
| Vivian als Agent | `VivianAssistant` ist `Agent` und `Entity` | ja | Kein Zusatzmodul noetig. |
| Vivian-Modus | `StateAssertion`: `mode = guiding`, `awaitingConfirmation`, `errorExplained` | ja | Wenn Modi als formaler Dialog-/Agentenautomat gelten sollen. |
| Vivian-Faehigkeiten | `CAP-B-VIVIAN-*` und `CapabilityUse` | ja | Wenn Vivian selbst plant, priorisiert oder persoenlich adaptiert. |
| Dialogstrategie | indirekt ueber Capability, Effect, StateAssertion und RuntimeAction | begrenzt | Optionales `AssistantInteractionModule`. |
| Startbestaetigung | `CAP-B-VIVIAN-REQUEST-CONFIRMATION` plus Events/StateAssertions | ja | Wenn Antwortpolitik, Timeout oder Widerruf formal werden. |
| Runtime-Profil | `RuntimeBinding -> RuntimeAction` | ja fuer technische Baseline | Optionales `RuntimeProfileModule`, wenn Profile auswaehlbar oder validierbar werden. |

### Beispiel B: Vivian fuehrt zur Tassenplatzierung

Kompakte Kernabbildung:

| Ebene | Instanz |
| --- | --- |
| Agent | `ENT-B-01 VivianAssistant` |
| Mode State | `VivianAssistant.mode = guiding` |
| ScenarioStep | `B-MAIN-S03` |
| CapabilityUse | `B-CU-002` |
| Capability | `CAP-B-VIVIAN-GUIDE-CUP` |
| Effect | `B-EFF-CUP-GUIDANCE-ISSUED` |
| StateAssertion | `SA-B-VIVIAN-GUIDANCE-CUP` |
| RuntimeBinding | `B-RB-VIVIAN-CUP-GUIDANCE` |
| RuntimeAction | `B-RA-VIVIAN-COMPOSE-CUP-GUIDANCE`; `B-RA-VR-PRESENT-CUP-GUIDANCE` |

Das reicht fuer die Baseline, weil Vivian nicht selbst zwischen Zielen plant. Vivian reagiert auf den Szenarioschritt und nutzt eine fachliche Capability.

Ein Zusatzmodul waere noetig, wenn Vivian eigene Agentenziele haette, z. B.:

- `assistUserGoal`: Bedienung erfolgreich abschliessen,
- `avoidUnsafeStartGoal`: Bruehstart ohne Tasse oder Freigabe verhindern,
- `minimizeUserConfusionGoal`: Erklaerstrategie anpassen,
- `recoverFromErrorGoal`: Korrekturpfad auswaehlen.

Diese Ziele sind mehr als Capabilities. Sie beschreiben Absichten, Prioritaeten und Auswahlregeln. Das gehoert in ein Agent-/Assistant-Modul, nicht in den Kern.

## Laufzeitprofile getrennt halten

Laufzeitprofile sind wichtig, aber sie sind keine Agentenrollen und keine fachlichen Capabilities.

| Profilart | Geeigneter Ort | Beispiel | Warum nicht in `Agent`? |
| --- | --- | --- | --- |
| VR-Agentencontroller-Profil | optionales `RuntimeProfileModule` unter `RuntimeBinding` | Controller-Version, Tickrate, Bewegungsmodus | Technische Ausfuehrungsdetails wuerden `Agent` verschmutzen. |
| Vivian-LLM-Profil | optionales `RuntimeProfileModule` unter Vivian-RuntimeBinding | Modellversion, Promptprofil, Temperatur, Safety-Policy | Fachlicher Agent bleibt unabhaengig von Implementierung. |
| Avatar/TTS-Profil | optional unter RuntimeBinding oder AssistantInteraction | Stimme, Sprache, Avatar-Geste | Praesentation ist nicht identisch mit Agentenidentitaet. |
| Kaffeemaschinenadapter-Profil | RuntimeBinding/RuntimeAction | Adapterversion, Endpoint, Schema | CoffeeMachine ist `Entity`, Adapter ist Technik. |
| Trace-/Validation-Profil | optionales Test-/Runtime-Modul | Trace-Level, Assertion-Modus | Validierung ist nicht Agentenverhalten. |

Der korrekte Pfad bleibt:

`Agent/Entity -> Capability -> RuntimeBinding -> RuntimeAction`

Falls Profile formal werden:

`RuntimeBinding -> RuntimeProfile -> RuntimeAction`

oder, wenn das Profil eine ganze Ausfuehrungsumgebung beschreibt:

`RuntimeEnvironment -> RuntimeProfile -> RuntimeBinding`

## Vorgeschlagener Andockpunkt fuer optionale Module

### Optionales `AgentBehaviorModule`

| Modulkonzept | Kardinalitaet/Andockpunkt | Zweck |
| --- | --- | --- |
| `AgentGoal` | `Agent -> AgentGoal [0..*]` | Beschreibt interne Ziele eines Agenten. |
| `GoalPriority` | `AgentGoal [1]` | Beschreibt Prioritaet, Gewicht oder Safety-Rang. |
| `AgentRole` | `Agent -> AgentRole [0..*]` oder `AgentProfile -> AgentRole [1..*]` | Typisiert erlaubte Rollen statt nur Zustandsstrings zu verwenden. |
| `RoleTransition` | `AgentRole -> AgentRole`, mit `Condition [0..*]` | Beschreibt erlaubte Rollenwechsel. |
| `AgentPolicy` | `Agent -> AgentPolicy [0..*]` | Beschreibt Auswahl-, Recovery- oder Konfliktregeln. |
| `PlanStep` | optional an `ScenarioStep` oder `CapabilityUse` | Beschreibt interne Planungsstruktur, wenn der Agent selbst plant. |
| `GoalSatisfaction` | `AgentGoal -> StateAssertion [1..*]` | Bindet interne Ziele an beobachtbare Erfuellung. |

### Optionales `RuntimeProfileModule`

| Modulkonzept | Kardinalitaet/Andockpunkt | Zweck |
| --- | --- | --- |
| `RuntimeProfile` | `RuntimeBinding -> RuntimeProfile [0..*]` | Beschreibt technische Ausfuehrungsvariante. |
| `RuntimeEnvironment` | `RuntimeProfile -> RuntimeEnvironment [1]` | Beschreibt Plattform oder Laufzeitumgebung. |
| `AdapterProfile` | `RuntimeProfile -> AdapterProfile [0..*]` | Beschreibt Adapter, Protokoll, Version oder Schemafamilie. |
| `ExecutionConstraint` | `RuntimeProfile -> ExecutionConstraint [0..*]` | Beschreibt Latenz, Ressourcen, Rate Limits oder Safety-Vorgaben. |
| `ProfileSelectionRule` | `RuntimeBinding -> RuntimeProfile [0..*]` mit `Condition` | Beschreibt, wann welches Profil gewaehlt wird. |

Bewusste Nicht-Kanten:

- `ScenarioStep -> RuntimeProfile`
- `AgentGoal -> RuntimeAction`
- `AgentRole -> RuntimeAction`

Diese Kanten wuerden fachliche Agentenlogik direkt mit Technik verbinden und die bestehende Kerninvariante unterlaufen.

## Kern- und Modulentscheidung

| Modellierungsbedarf | Entscheidung |
| --- | --- |
| Agent als aktive modellierte Instanz | Kern: `Agent --|> Entity` |
| Agent besitzt fachliche Faehigkeiten | Kern: `Entity -> Capability [0..*]` |
| Agent nutzt Faehigkeit in einem Schritt | Kern: `ScenarioStep -> CapabilityUse -> Capability` |
| Agentenrolle als beobachtbarer Zustand | Kern: `StateAssertion.expectedState`, z. B. `roleState=executor` |
| Rollenwechsel als fachlicher Schritt | Kern: `Condition + CapabilityUse + Effect + StateAssertion` |
| Interne Zielhierarchie oder Zielkonflikt | optionales `AgentBehaviorModule` |
| Formale Rollenmenge und erlaubte Transitionen | optionales `AgentBehaviorModule` oder `StateTransitionModule` |
| Autonome Planung und Policy-Auswahl | optionales `AgentBehaviorModule` |
| Dialogstrategie von Vivian | optionales `AssistantInteractionModule` |
| Technische Plattform-, Modell- oder Adapterprofile | optionales `RuntimeProfileModule` |

## Invariantencheck

| Regel | Ergebnis |
| --- | --- |
| `Agent --|> Entity` bleibt die einzige Kern-Spezialisierung fuer aktive Subjekte | eingehalten |
| Keine Vermischung von `Actor` und `Agent` | eingehalten; Visitor bleibt Actor, Vivian und AgentBody bleiben Agenten |
| Keine direkte `ScenarioStep -> RuntimeAction`-Kante | eingehalten |
| Keine direkte `AgentGoal -> RuntimeAction`-Kante | als Modulregel empfohlen |
| `Capability` bleibt fachlich und enthaelt keine technischen Profile | eingehalten |
| Rollen- und Moduszustaende bleiben ueber `StateAssertion` pruefbar | eingehalten |
| Runtimeprofile haengen unter RuntimeBinding, nicht unter fachlichem Step | empfohlen |

## Abnahmekontrolle

| Kriterium aus Task 10.8 | Erfuellung |
| --- | --- |
| Entscheidung vorhanden | Keine neuen Kernklassen; optionale AgentBehavior- und RuntimeProfile-Module bei erweitertem Scope. |
| `Agent` plus `Capability` bewertet | Fuer die Baseline ausreichend, aber nicht fuer interne Ziele, Rollenautomaten, Policies oder Runtimeprofile. |
| Begruendung fuer Nicht-Ausreichen vorhanden | Abschnitt `Warum Agent plus Capability nicht immer ausreicht` listet die fehlenden Semantiken. |
| A-Beispiel verwendet | Rollenwechsel `A-MAIN-S05`, `A-CU-001`, `A-CAP-ADOPT-EXECUTOR-ROLE`, `roleState=executor`. |
| B-Beispiel verwendet | Vivian-Fuehrung `B-MAIN-S03`, `B-CU-002`, `CAP-B-VIVIAN-GUIDE-CUP`, Modus `guiding`. |
| Runtimeprofile getrennt | Eigener Abschnitt ordnet Profile unter RuntimeBinding/RuntimeProfile, nicht unter Agent. |
| Keine Kernaufblaehung abgeleitet | Kern bleibt kompakt; Erweiterungen bleiben modular. |

## Konsequenz fuer Abschnitt 11

Abschnitt 11 kann nun entscheiden, welche optionalen Module tatsaechlich in das finale Gesamtmodell eingehaengt werden. Aus 10.8 folgt: Der Kern sollte nicht um Agentenziele, Rollenautomaten oder Runtimeprofile erweitert werden. Wenn die Dissertation autonome Agentenplanung oder formal auswaehlbare Laufzeitprofile betonen soll, sollten diese als klar abgegrenzte Zusatzmodule modelliert werden.
