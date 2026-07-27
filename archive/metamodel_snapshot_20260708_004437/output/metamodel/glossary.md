# Glossar fuer die weitere Beispielausarbeitung

Stand: 2026-07-07

Task: 1.5 `Begriffsliste fuer die Ausarbeitung anlegen`

Zweck: Dieses Glossar fixiert die Begriffe, die in den spaeteren Beispielen zu dynamischen Agenten und Vivian/Kaffeemaschine konsistent verwendet werden muessen. Jeder Begriff hat eine Ein-Satz-Definition und Beispielplatzhalter fuer die beiden Anwendungsfaelle.

## Pflichtbegriffe aus Task 1.5

| Begriff | Ein-Satz-Definition | Wichtige Abgrenzung | Beispielplatzhalter A: dynamische Agenten | Beispielplatzhalter B: Vivian/Kaffeemaschine |
| --- | --- | --- | --- | --- |
| `Actor` | Ein Actor ist eine externe Rolle, die mit dem System interagiert oder im UseCase eine Absicht aus Sicht der Umgebung ausdrueckt. | Actor ist keine physische Instanz und nicht automatisch ein Agent; eine reale Entitaet kann mehrere Actor-Rollen spielen. | `[A-Actor-Platzhalter: Rolle, die Agentenverhalten anstoesst oder beobachtet]` | `[B-Actor-Platzhalter: Benutzerrolle, Vivian-Rolle oder Besucherrolle bei der Kaffeemaschinenbedienung]` |
| `Agent` | Ein Agent ist eine spezialisierte Entity, die als ausfuehrende oder beobachtete Entitaet in der Szene auftreten und Actor-Rollen spielen kann. | Agent ist eine Entitaet/Instanzebene, waehrend Actor die UseCase-Rollenebene beschreibt. | `[A-Agent-Platzhalter: dynamischer Szenenagent mit Rolle, Zustand und Faehigkeiten]` | `[B-Agent-Platzhalter: Vivian als ausfuehrende oder assistierende Entitaet, falls fachlich passend]` |
| `Entity` | Eine Entity ist ein fachlich relevantes Objekt, System, Asset, Benutzer- oder Umgebungselement, das beobachtet werden oder Capabilities bereitstellen kann. | Entity ist allgemeiner als Agent; nicht jede Entity handelt aktiv oder spielt eine Actor-Rolle. | `[A-Entity-Platzhalter: Szenenobjekt, Zielpunkt, Umgebungselement oder Agentenbasis]` | `[B-Entity-Platzhalter: Kaffeemaschine, Tasse, Bedienpanel, Vivian oder VR-System]` |
| `ScenarioStep` | Ein ScenarioStep ist ein einzelner fachlicher Schritt innerhalb eines Scenario, der eine Benutzerabsicht, Systemreaktion oder Umgebungsbeobachtung beschreibt. | ScenarioStep bleibt fachlich und darf nicht direkt auf RuntimeAction, API, Tool oder Topic zeigen. | `[A-ScenarioStep-Platzhalter: Agent bewegt sich, beobachtet, reagiert oder aendert Szenenzustand]` | `[B-ScenarioStep-Platzhalter: Benutzer drueckt Taste, Vivian erklaert, System prueft Zustand oder Maschine startet]` |
| `CapabilityUse` | Eine CapabilityUse ist die konkrete Nutzung einer fachlichen Capability durch einen ScenarioStep. | CapabilityUse ist die Bruecke vom Ablauf zur fachlichen Faehigkeit, aber noch keine technische Ausfuehrung. | `[A-CapabilityUse-Platzhalter: Schritt fordert z. B. AgentMoveToTarget oder ObserveObject an]` | `[B-CapabilityUse-Platzhalter: Schritt fordert z. B. CheckMachineReady oder StartBrewing an]` |
| `Capability` | Eine Capability ist eine fachliche Faehigkeit mit Intent, Vorbedingungen und mindestens einem beobachtbaren versprochenen Effekt. | Capability enthaelt keine technischen Endpoint-, Tool-, Topic-, Unity- oder API-Daten. | `[A-Capability-Platzhalter: fachliche Faehigkeit eines Agenten oder Szenensystems]` | `[B-Capability-Platzhalter: fachliche Faehigkeit zur Bedienung oder Pruefung der Kaffeemaschine]` |
| `RuntimeBinding` | Eine RuntimeBinding ordnet genau eine fachliche Capability einer konkreten technischen Plattform- oder Laufzeitbindung zu. | RuntimeBinding ist techniknah, aber noch der Container fuer RuntimeActions und nicht selbst der einzelne Endpoint. | `[A-RuntimeBinding-Platzhalter: Binding einer Agentenfaehigkeit an Unity, WebXR, Simulationslogik oder Toolchain]` | `[B-RuntimeBinding-Platzhalter: Binding einer Kaffeemaschinen- oder Vivian-Faehigkeit an Controller/API/Tool]` |
| `RuntimeAction` | Eine RuntimeAction ist die konkrete technische Aktion, etwa ein Endpoint, Toolaufruf, Topic oder Controllerbefehl mit optionalen Ein- und Ausgabeschemas. | RuntimeAction darf nicht direkt an ScenarioStep haengen, sondern nur ueber RuntimeBinding erreicht werden. | `[A-RuntimeAction-Platzhalter: konkreter technischer Befehl fuer Agentenbewegung, Animation oder Szenenupdate]` | `[B-RuntimeAction-Platzhalter: konkreter Controller-Aufruf fuer Starttaste, Bruehvorgang, Anzeige oder Vivian-Ausgabe]` |
| `ValidationCase` | Ein ValidationCase beschreibt einen pruefbaren Fall mit Stimulus und mindestens einem erwarteten Outcome. | ValidationCase prueft Verhalten und technische Bindungen, besitzt diese Bindungen aber nicht. | `[A-ValidationCase-Platzhalter: Test, ob Agentenzustand oder Szenenzustand nach Stimulus korrekt ist]` | `[B-ValidationCase-Platzhalter: Test, ob Kaffeemaschine und Vivian nach Bedienhandlung den erwarteten Zustand erreichen]` |

## Ergaenzende Begriffe fuer die naechsten Tasks

Diese Begriffe waren nicht explizit in Task 1.5 gefordert, werden aber in den naechsten Schritten sehr wahrscheinlich benoetigt.

| Begriff | Ein-Satz-Definition | Beispielplatzhalter |
| --- | --- | --- |
| `Requirement` | Ein Requirement ist eine pruefbare textuelle Anforderung, die fachlich motiviert, warum ein Verhalten existieren muss. | `[Requirement-Platzhalter: Der Benutzer muss ... koennen]` |
| `UseCase` | Ein UseCase beschreibt eine fachliche Nutzung des Systems und nicht die technische Implementierung dieser Nutzung. | `[UseCase-Platzhalter: Dynamisches Agentenverhalten ausloesen oder Kaffeemaschine mit Vivian bedienen]` |
| `Scenario` | Ein Scenario beschreibt einen konkreten Ablauf eines UseCase als main, alternative oder exception. | `[Scenario-Platzhalter: Main-, Alternativ- oder Fehlerablauf]` |
| `Event` | Ein Event ist ein ausloesendes Ereignis wie Benutzerhandlung, Signal, Zeitereignis, Raumereignis oder Umgebungsaenderung. | `[Event-Platzhalter: press(button), agentEnteredZone, waterLevelLow]` |
| `Condition` | Eine Condition ist eine pruefbare Bedingung fuer Guard, Timing, Raumbezug, Vorbedingung oder Nachbedingung. | `[Condition-Platzhalter: machine.ready = true oder distance(agent,target) < threshold]` |
| `StateAssertion` | Eine StateAssertion ist eine erwartete oder beobachtete Zustandsaussage ueber genau ein identifizierbares Subjekt. | `[StateAssertion-Platzhalter: coffeeMachine.state = brewing oder agent.location = targetZone]` |
| `Effect` | Ein Effect ist der beobachtbare versprochene Effekt einer Capability. | `[Effect-Platzhalter: Fortschritt sichtbar, Agent am Ziel, Objekt aktiviert]` |
| `StepRelation` | Eine StepRelation verbindet genau einen Quellschritt mit genau einem Zielschritt und typisiert den Ablauf als sequence, alternative, exception, fork, join oder loop. | `[StepRelation-Platzhalter: S1 -> S2 als sequence oder S2 -> S_error als exception]` |
| `ParallelGroup` | Eine ParallelGroup referenziert mindestens zwei Schritte desselben Scenario, die parallel oder nebenlaeufig betrachtet werden. | `[ParallelGroup-Platzhalter: Agent beobachtet Objekt parallel zu Systemfeedback]` |
| `Satisfy` | Satisfy verbindet entweder Requirements oder UseCases mit erfuellenden identifizierbaren Elementen, aber nicht beides in derselben Instanz. | `[Satisfy-Platzhalter: Capability oder ValidationCase erfuellt REQ-x]` |
| `Include` | Include modelliert verpflichtend eingefuegtes UseCase-Verhalten, ohne das der inkludierende UseCase nicht korrekt vollstaendig ist. | `[Include-Platzhalter: Bereitschaftspruefung vor Kaffeemaschinenstart]` |
| `Extend` | Extend modelliert optionales oder bedingtes Zusatzverhalten an einem definierten ExtensionPoint eines eigenstaendig sinnvollen Basis-UseCase. | `[Extend-Platzhalter: Vivian erklaert optional nach Startkommando]` |
| `ExtensionPoint` | Ein ExtensionPoint bezeichnet die Stelle im erweiterten UseCase, an der Extend-Verhalten einsetzen darf. | `[ExtensionPoint-Platzhalter: Nach Startkommando, vor Fehlerbehandlung, nach Agentenankunft]` |

## Leitplanken fuer die Verwendung der Begriffe

1. `Actor` bezeichnet Rollen, `Agent` und `Entity` bezeichnen fachliche Entitaeten.
2. `ScenarioStep` beschreibt fachliche Ablaufschritte und bleibt frei von technischen Endpoints.
3. `CapabilityUse` verbindet den Schritt mit einer fachlichen `Capability`.
4. `Capability` beschreibt das fachliche Koennen und mindestens einen beobachtbaren `Effect`.
5. `RuntimeBinding` und `RuntimeAction` sind die einzigen Orte fuer konkrete technische Ausfuehrung.
6. `ValidationCase` prueft den Ablauf und seine erwarteten Outcomes, ohne RuntimeBindings zu besitzen.
7. `Include` ist verpflichtend, `Extend` ist optional oder bedingt.
8. `StateAssertion` macht Ziel- und Zwischenzustaende pruefbar.

## Abnahmestatus

- Alle in Task 1.5 geforderten Begriffe sind enthalten.
- Jeder geforderte Begriff hat eine Ein-Satz-Definition.
- Jeder geforderte Begriff hat Beispielplatzhalter fuer Anwendungsfall A und Anwendungsfall B.
- Die Begriffe sind an die Invarianten aus `output/metamodel/invariants.md` anschlussfaehig.
