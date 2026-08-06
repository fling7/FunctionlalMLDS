# Entscheidung 10.3: Reichen `Entity` und `Agent` fuer Szenenobjekte aus?

Stand: 2026-07-07

Task: 10.3 `Pruefen, ob Entity/Agent fuer Szenenobjekte ausreicht`

Verglichene Use Cases:

- `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`
- `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Bezugsdateien:

- `dynamic_functional_mlds_specification.md`
- `metamodel_element_notes.md`
- `cardinality_table.md`
- `invariants.md`
- `common_concepts_A_B.md`
- `differences_A_B.md`
- `use_case_A_direct_modelability.md`
- `use_case_B_direct_modelability.md`

## Entscheidung

`Entity` und `Agent` reichen fuer die aktuellen Szenenobjekte im kompakten Kern aus.

Die Entscheidung gilt unter drei Bedingungen:

1. Ein Szenenobjekt wird im Kern primaer als eindeutig identifizierbares, beobachtbares oder faehigkeitsbereitstellendes Modellsubjekt verstanden.
2. Aktive systemische Subjekte werden als `Agent` modelliert, weil `Agent` eine spezialisierte `Entity` ist.
3. Spezialisierte Details wie Geometrie, Affordances, Bedienpunkte, formale Zustandsautomaten, RuntimeProfile oder Dialoginhalte werden nicht in `Entity` hineingezogen, sondern bei Bedarf in optionale Ergaenzungsmodule ausgelagert.

Damit lautet die knappe Modellentscheidung:

| Frage | Entscheidung |
| --- | --- |
| Braucht der Kern eine neue Klasse `SceneObject`? | nein |
| Braucht der Kern eine neue Klasse `InteractionObject`? | nein, nicht im Kern; bei Bedarf optionales Modul |
| Reicht `Entity` fuer passive, beobachtete und interaktive Objekte? | ja, fuer Identitaet, Zustandsaussagen, Bedingungen und Capability-Bereitstellung |
| Reicht `Agent` fuer aktive systemische Subjekte? | ja, fuer `AgentBody` und `VivianAssistant` |
| Sollte `Entity.kind [0..1]` als minimale Praezisierung erhalten bzw. vorbereitet werden? | ja, als optionaler Kernkandidat |

## Begriffsentscheidung

| Modellierungsfall | Zu verwenden | Begruendung |
| --- | --- | --- |
| Externe Rolle im Use Case | `Actor` | `Actor` beschreibt eine Rolle, z. B. Visitor, ScenarioDesigner oder SceneObserver. |
| Aktive ausfuehrende oder beobachtete Systeminstanz | `Agent` | `Agent` ist spezialisierte `Entity`; passend fuer `AgentBody` und `VivianAssistant`. |
| Passives oder interaktives Szenenobjekt | `Entity` | `Entity` ist identifizierbar, kann Zustandssubjekt sein und optional Capabilities bereitstellen. |
| Raum- oder Szenenmarker | `Entity` | Zonen, Grenzen, Zielbereiche und Feedbacksignale brauchen Identitaet, aber nicht zwingend eigene Kernklassen. |
| Bedienpunkt, Affordance oder Control Surface | optionales `InteractionObjectModule` | Im Kern kann es in Expressions und Runtime-Schemas stehen; bei maschineller Auswertung braucht es ein Modul. |

Diese Trennung verhindert zwei haeufige Fehler:

- Ein `Actor` wird nicht als konkrete Laufzeitinstanz missverstanden.
- Ein technisches oder interaktives Objekt wird nicht automatisch zu einem `Agent`.

## Abbildung der Szenenobjekte

| Szenenobjekt-Kategorie | A-Beispiele | B-Beispiele | Kernabbildung | Reicht fuer Baseline? |
| --- | --- | --- | --- | --- |
| Aktiver Agent | `AgentBody` | `VivianAssistant` | `Agent --|> Entity`; `Entity -> Capability [0..*]`; `StateAssertion.subject [1]` | ja |
| Interaktionsobjekt | vorbereitetes `InteractionAsset` | `CoffeeMachine` | `Entity`; optional `Entity.kind = asset`; `Entity -> Capability [0..*]` | ja, solange Affordances nicht eigenstaendig ausgewertet werden |
| Kontextobjekt | `TargetZone`, `ObstacleRegion`, `SceneBoundary` | `Cup`, `BrewingRequest` | `Entity`; Nutzung in `Condition`, `Event`, `StateAssertion`, `CapabilityUse.parameters` | ja |
| Beobachtungs- oder Feedbackobjekt | `ObservationPoint`, `FeedbackSignal`, `SceneStateFlag` | Maschinenfeedback, Fortschrittsanzeige, CompletionFeedback | `Entity` plus `StateAssertion` und `Effect.observableBy` | ja |
| Bedienpunkt oder Objektteil | nicht zentral instanziiert | Starttaste, Tassenbereich, Programmauswahl | aktuell Ausdruck in `Event.expression`, `Condition.expression` oder Runtime-Schema | nur fuer Baseline; optionales Modul bei Praezisionsbedarf |

## Begruendung 1: Objektzustand

Fuer Objektzustaende reicht `Entity` als Zustandssubjekt im Kern aus.

| Zustandsart | Aktuelle Kernabbildung | A-Beispiel | B-Beispiel | Bewertung |
| --- | --- | --- | --- | --- |
| Einzelner beobachteter Zustand | `StateAssertion.subject [1]`; `StateAssertion.expectedState` | `AgentBody.roleState = executor` | `CoffeeMachine.lifecycleState = brewing` | ausreichend |
| Vorbedingung oder Guard | `Condition.expression`; optional Bezug auf Entity | `inside(AgentBody, SceneBoundary)` | `CoffeeMachine.cupPresent = true` | ausreichend fuer Baseline |
| Mehrere parallele Merkmale | mehrere `StateAssertion`-Instanzen oder zusammengesetzte Expressions | Position, Rolle, Blockadezustand | Wasserstand, Tasse, Programm, Startfreigabe | ausreichend, aber semantisch grob |
| Erlaubte Uebergaenge | verteilt auf `Condition`, `Event`, `ScenarioStep`, `StateAssertion` | `notBlocked -> executor -> completed` | `ready -> brewing -> finished` | nicht als formaler Automat; optionales `StateTransitionModule` |

Die Kernfrage fuer 10.3 lautet nicht, ob `Entity` alle Zustandssemantik ausdrueckt. Sie lautet, ob `Entity` als Traeger der Zustandsaussage reicht. Das tut sie: Die konkrete Zustandsaussage liegt bewusst in `StateAssertion` und `Condition`, nicht in einer spezialisierten Objektklasse.

Konsequenz fuer 10.4: Wenn Zustandsautomaten mit Source-State, Target-State, Trigger, Guard und Effect maschinenlesbar benoetigt werden, muss das als `StateTransitionModule` entschieden werden. Diese Entscheidung darf nicht durch eine neue Kernklasse `SceneObject` vorweggenommen werden.

## Begruendung 2: Interaktion

Fuer die aktuelle Interaktion reicht `Entity` zusammen mit `Event`, `Condition`, `ScenarioStep`, `CapabilityUse`, `Capability` und `Effect` aus.

| Interaktionsaspekt | Aktuelle Kernabbildung | Beispiel | Bewertung |
| --- | --- | --- | --- |
| Externe Benutzerabsicht | `ScenarioStep.kind = actorIntent`; `performedBy -> Actor [0..1]` | Visitor drueckt Starttaste; SceneParticipant betritt TriggerZone | ausreichend |
| Ausloesendes Ereignis | `ScenarioStep -> Event [0..*]`; `Event.expression` | `pressed(Visitor, CoffeeMachine.startButton)` | ausreichend fuer Baseline |
| Interaktionsbedingung | `Condition.expression` | `CoffeeMachine.cupPresent = true` | ausreichend fuer Baseline |
| Fachliche Systemreaktion | `ScenarioStep -> CapabilityUse -> Capability` | Vivian fuehrt; Kaffeemaschine prueft Bereitschaft; Agent wechselt Rolle | ausreichend |
| Beobachtbare Wirkung | `Capability -> Effect [1..*]`; `ScenarioStep -> StateAssertion [0..*]` | Startbestaetigung sichtbar; Agent ist Executor | ausreichend |
| Strukturierte Affordance | nicht eigenstaendig im Kern | Starttaste mit Bedienart, Aktivierungsbedingung, Position, Feedback | optionales `InteractionObjectModule` |

Damit ist `Entity` fuer interaktive Szenenobjekte ausreichend, solange die Interaktion als fachlicher Ablauf beschrieben wird. Nicht ausreichend ist `Entity`, wenn Bedienpunkte selbst zu first-class Modellelementen werden sollen.

Eine Kaffeemaschine kann deshalb im Kern als `Entity` modelliert werden. Ihre Faehigkeiten wie `CAP-B-CHECK-MACHINE-READY` und `CAP-B-START-BREWING` werden ueber `Capability` beschrieben. Die konkrete Starttaste bleibt in der Baseline ein Ausdruck oder Runtime-Schema. Erst wenn Starttaste, Tassenbereich, Display, erlaubte Manipulation und Aktivierungsbedingungen automatisch generiert oder validiert werden sollen, braucht es ein optionales Affordance-Modul.

## Begruendung 3: Runtime-Anbindung

`Entity` und `Agent` reichen auch fuer die Runtime-Anbindung, weil die technische Bindung nicht direkt am Objekt haengt, sondern ueber die fachliche Capability laeuft.

Der korrekte Pfad ist:

`Entity/Agent -> Capability -> RuntimeBinding -> RuntimeAction`

oder im Szenario-Kontext:

`ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

| Runtime-Frage | Kernabbildung | Warum ausreichend? |
| --- | --- | --- |
| Welche Entity kann etwas fachlich leisten? | `Entity -> Capability [0..*]` | Vivian, CoffeeMachine und AgentBody koennen Capabilities bereitstellen. |
| Welche fachliche Faehigkeit wird in einem Schritt benoetigt? | `ScenarioStep -> CapabilityUse [0..*]`; `CapabilityUse -> Capability [1]` | Der Schritt bleibt fachlich und referenziert keine technische Aktion. |
| Wie wird die Faehigkeit technisch gebunden? | `Capability -> RuntimeBinding [0..*]` | Eine Capability kann ohne, mit einer oder mit mehreren Plattformbindungen existieren. |
| Wo stehen Endpoints, Tools, Topics und Schemas? | `RuntimeBinding -> RuntimeAction [1..*]` | Technische Details bleiben in `RuntimeAction`; `Capability` bleibt fachlich. |
| Darf ein Szenenobjekt direkt eine RuntimeAction besitzen? | nein | Das wuerde die Invariante gegen direkte technische Kurzschluesse unterlaufen. |

Fuer A bedeutet das: `AgentBody` stellt fachliche Agentenfaehigkeiten bereit, z. B. Rollenwechsel oder Zielhandlung. Diese werden ueber VR-RuntimeBindings technisch gebunden.

Fuer B bedeutet das: `VivianAssistant` und `CoffeeMachine` stellen fachliche Capabilities bereit, die ueber Vivian-, VR-, Kaffeemaschinenadapter- oder Trace-RuntimeBindings ausgefuehrt werden.

## Grenzfaelle und Modulbedarf

| Grenzfall | Reicht `Entity`/`Agent` im Kern? | Empfohlene Behandlung |
| --- | --- | --- |
| Objekt hat nur Identitaet und beobachtbaren Zustand | ja | `Entity` plus `StateAssertion` |
| Objekt stellt fachliche Faehigkeiten bereit | ja | `Entity -> Capability` |
| Aktives Systemsubjekt handelt oder spielt Rollen | ja | `Agent --|> Entity`; optional `Agent.playsActor` |
| Objekt hat interne StateMachine mit erlaubten Transitionen | nein, nicht formal | optionales `StateTransitionModule` |
| Objekt hat Bedienpunkte, Manipulationsarten und Affordances | nein, nicht formal | optionales `InteractionObjectModule` |
| Objekt braucht Koordinaten, Volumen, Distanz, Sichtbarkeit oder Erreichbarkeit | nein, nicht formal | optionales `SpatialSemanticsModule` |
| Objekt braucht Adapterversionen, Schemamodelle oder RuntimeProfile | nein, nicht formal | optionales `RuntimeExecutionModule` oder RuntimeProfile-Modul |

Die Grenze ist wichtig: Eine neue Kernklasse `SceneObject` wuerde kaum mehr leisten als `Entity`, aber zusaetzliche Begriffe einfuehren. Eine Kernklasse `InteractionObject` waere fuer B attraktiv, wuerde aber A und einfache Szenarien unnoetig belasten.

## Kardinalitaets- und Invariantencheck

| Regel | Auswirkung auf die Entscheidung |
| --- | --- |
| `Agent --|> Entity` | Aktive Subjekte koennen ohne neue Klasse als spezialisierte Entities modelliert werden. |
| `Entity -> Capability [0..*]` | Ein Szenenobjekt kann keine, eine oder mehrere fachliche Faehigkeiten bereitstellen. |
| `StateAssertion.subject [1]` | Jedes Zustandsstatement braucht genau ein identifizierbares Subjekt; `Entity` erfuellt diese Rolle. |
| `ScenarioStep -> StateAssertion [0..*]` | Ein Schritt kann beliebig viele Objekt- oder Agentenzustaende erwarten. |
| `Capability -> RuntimeBinding [0..*]` | Runtime-Anbindung bleibt optional und austauschbar. |
| `RuntimeBinding -> RuntimeAction [1..*]` | Technische Ausfuehrung ist nur unter RuntimeBinding konkret. |
| Keine direkte `ScenarioStep -> RuntimeAction`-Kante | `Entity`/`Agent` duerfen nicht als Umweg fuer technische Kurzschluesse verwendet werden. |
| `Capability` enthaelt keine technischen Endpoint- oder Tool-Daten | Objektfaehigkeiten bleiben fachlich; RuntimeDetails bleiben ausgelagert. |

Keine dieser Regeln erzwingt eine zusaetzliche Kernklasse fuer Szenenobjekte.

## Empfehlung fuer das Metamodell

| Empfehlung | Status |
| --- | --- |
| `Entity` als allgemeines identifizierbares Szenenobjekt beibehalten | bestaetigt |
| `Agent` als aktive Spezialisierung von `Entity` beibehalten | bestaetigt |
| `Actor` und `Agent` strikt getrennt halten | bestaetigt |
| optionale `Entity.kind [0..1]`-Typisierung als minimalen Kernkandidaten vorbereiten | empfohlen |
| keine neue Kernklasse `SceneObject` einfuehren | empfohlen |
| keine neue Kernklasse `InteractionObject` einfuehren | empfohlen |
| Affordances, StateMachines, Spatial Semantics und RuntimeProfile als optionale Module behandeln | empfohlen |

## Abnahmekontrolle

| Kriterium aus Task 10.3 | Erfuellung |
| --- | --- |
| Entscheidung vorhanden | `Entity` und `Agent` reichen fuer den kompakten Kern und die aktuellen Beispiele aus. |
| Objektzustand begruendet | Abschnitt `Begruendung 1: Objektzustand` trennt Zustandssubjekt, StateAssertion und optionale StateTransition. |
| Interaktion begruendet | Abschnitt `Begruendung 2: Interaktion` trennt fachliche Interaktion von strukturierten Affordances. |
| Runtime-Anbindung begruendet | Abschnitt `Begruendung 3: Runtime-Anbindung` zeigt den Pfad `Entity/Agent -> Capability -> RuntimeBinding -> RuntimeAction`. |
| A und B getrennt beruecksichtigt | Die Abbildungstabelle nennt AgentBody, raeumliche Entities, Vivian, CoffeeMachine, Cup und BrewingRequest. |
| Keine Kernaufblaehung | Neue Klassen werden nur als optionale Module empfohlen, nicht als Kernbestandteile. |

## Konsequenz fuer Task 10.4

Task 10.4 soll als naechstes pruefen, ob `StateAssertion` fuer Objektzustaende ausreicht. Die Entscheidung aus 10.3 nimmt diese Frage nicht vorweg: `Entity` reicht als Subjekt der Zustandsaussage, aber ob `StateAssertion` auch fuer Zustandsautomaten und Uebergaenge ausreicht, muss separat entschieden werden.
