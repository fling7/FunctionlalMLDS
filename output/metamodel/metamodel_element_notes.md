# Arbeitsnotizen zu Metamodell-Elementen

Stand: 2026-07-07

Quelle: `output/metamodel/dynamic_functional_mlds_specification.md`

Zweck dieses Dokuments: Task 1.1 der ausfuehrbaren Taskliste erfuellen. Jedes in der aktuellen Spezifikation vorkommende Metamodell-Element wird kurz beschrieben, damit die spaetere Beispielausarbeitung nicht aus dem Bauch heraus erfolgt.

## Lesestand

Die aktuelle Spezifikation wurde vollstaendig gelesen:

- Problemstellung
- EAST-ADL-Abgleich
- Verdichtungen gegenueber der groesseren Fassung
- Modellidee
- zentrale Kardinalitaeten
- Invarianten
- Kaffeemaschinenbeispiel
- Interpretation
- Quellen

## Abstrakte und uebergeordnete Elemente

| Element | Kurzbeschreibung | Relevanz fuer die Beispiele |
| --- | --- | --- |
| `Identifiable` | Abstrakter Bezugspunkt fuer eindeutig identifizierbare Modellelemente. In der Spezifikation wichtig, weil `Satisfy.satisfiedBy` und `StateAssertion.subject` auf identifizierbare Elemente zeigen koennen. | Agenten, Vivian, Kaffeemaschine, Szenenobjekte und Zielzustaende muessen referenzierbar sein. |
| `TraceableSpecification` | Abstrakte Spezifikationseinheit, von der u. a. Requirements, Actors, UseCases, Scenarios, ScenarioSteps, Entities, Capabilities und ValidationCases profitieren. | Ermoeglicht Traceability vom fachlichen Text bis zur technischen Bindung. |
| `RedefinableElement` | Abstraktes EAST-ADL-nahes Element, in der aktuellen Verdichtung nur noch fuer `ExtensionPoint` relevant. | Wichtig, um nicht faelschlich jeden `ScenarioStep` als redefinierbares Element zu modellieren. |

## EAST-ADL-naher Use-Case-Kern

| Element | Kurzbeschreibung | Wichtige Beziehungen und Regeln | Relevanz fuer die Beispiele |
| --- | --- | --- | --- |
| `RequirementsModel` | Kontextcontainer fuer Requirements und UseCases. | Enthaelt `Requirement [0..*]` und `UseCase [0..*]`. | Dient als oberer Container fuer beide Beispielraeume. |
| `Requirement` | Textuelle Anforderung, die fachlich nachvollziehbar erfuellt werden muss. | Kann ueber `Satisfy` mit erfuellenden Elementen verbunden werden. | Beispiele brauchen pruefbare Anforderungen, z. B. Agentenverhalten oder Kaffeemaschinenbedienung. |
| `Actor` | Externe Rolle, die mit dem System interagiert; keine zwingend physische Instanz. | Interagiert mit `UseCase`; bei `ScenarioStep.kind = actorIntent` sollte `performedBy` auf Actor zeigen. | Vivian, Benutzer, Trainer oder Besucher muessen als Rollen sauber von Agent/Entity getrennt werden. |
| `UseCase` | Beschreibt eine Nutzung des Systems und was das System leisten soll. | Enthaelt ExtensionPoints, Include-/Extend-Beziehungen und mindestens ein Scenario. | Jeder Beispielraum braucht mindestens einen fachlichen UseCase. |
| `Include` | Verpflichtende Wiederverwendung eines UseCase-Verhaltens. Der inkludierende UseCase ist ohne dieses Verhalten nicht vollstaendig korrekt. | `UseCase -> Include [0..*]`, `Include.addition -> UseCase [1]`. | Nur fuer Pflichtablaeufe verwenden, z. B. zwingende Bereitschaftspruefung. |
| `Extend` | Optionale oder bedingte Ergaenzung eines eigenstaendig sinnvollen Basis-UseCase. | `UseCase -> Extend [0..*]`, `Extend.extendedCase -> UseCase [1]`, `Extend.extensionLocation -> ExtensionPoint [1..*]`. | Nuetzlich fuer optionale Erklaerungen, Hilfestellungen oder Trainingsmodus. |
| `ExtensionPoint` | Stelle innerhalb des erweiterten UseCase, an der ergaenzendes Verhalten eingefuegt werden darf. | Gehoert zum erweiterten UseCase; ein `Extend.extensionLocation` muss auf ExtensionPoints dieses Basis-UseCase zeigen. | Bei Vivian/Kaffeemaschine wichtig, wenn optionale Hilfestellung an einer konkreten Stelle einfuegt. |
| `Satisfy` | RequirementsRelationship, das Anforderungen oder UseCases mit erfuellenden Elementen verbindet. | XOR-Regel: Eine Satisfy-Instanz referenziert entweder Requirements oder UseCases, nicht beides gleichzeitig. `satisfiedBy` zeigt auf `Identifiable [1..*]`. | Wichtig fuer wissenschaftliche Nachvollziehbarkeit von Requirement zu Modell- oder Runtime-Element. |

## Scenario Layer

| Element | Kurzbeschreibung | Wichtige Beziehungen und Regeln | Relevanz fuer die Beispiele |
| --- | --- | --- | --- |
| `Scenario` | Konkreter dynamischer Ablauf innerhalb eines UseCase. | Pro UseCase genau ein `Scenario.kind = main`; Alternativen und Exceptions optional. Enthaelt `ScenarioStep [1..*]`, `StepRelation [0..*]`, optional Parallelgruppen. | Hauptcontainer fuer beide Beispielszenarien. |
| `ScenarioStep` | Einzelner fachlicher Schritt in einem Szenario. | Darf keine direkte Referenz auf `RuntimeAction`, API-Endpunkte, Tools oder Topics besitzen. Kann `CapabilityUse [0..*]` enthalten. | Zentral fuer Agentendynamik und Vivian-Interaktionen. |
| `StepRelation` | Explizite Ablaufbeziehung zwischen Schritten. | Modelliert Sequenz, Alternative, Exception, Fork, Join oder Loop; aktuelle Darstellung trennt sinnvoll `source step [1]` und `target step [1]`. | Benoetigt fuer nichtlineare Ablaeufe, Alternativen, Fehlerfaelle und parallele Agentenhandlungen. |
| `ParallelGroup` | Gruppiert mindestens zwei Schritte, die parallel oder nebenlaeufig betrachtet werden. | Referenziert `ScenarioStep [2..*]`; besitzt diese Schritte nicht. Alle referenzierten Schritte muessen zum selben Scenario gehoeren. | Relevant, wenn mehrere Agenten gleichzeitig handeln oder Beobachtung und Systemreaktion parallel laufen. |
| `Event` | Ausloesendes Ereignis, in der Verdichtung ueber `Event.kind` statt eigener Subklassen modelliert. | Typen koennen z. B. temporal, spatial, signal, user oder environment sein. | Erfasst Benutzeraktionen, Vivian-Signale, Sensor-/Szenenereignisse und Objektzustaende als Ausloeser. |
| `Condition` | Bedingung oder Ausdruck fuer Guards, Timing, Vor-/Nachbedingungen oder raeumliche Bedingungen. | Verdichtet Guard-, Timing- und Spatial-Constraints ueber `Condition.kind`. | Braucht man fuer Startbedingungen, Entscheidungslogik, Bereitschaftspruefungen und Fehlerfaelle. |
| `StateAssertion` | Erwartete oder beobachtete Zustandsaussage ueber ein identifizierbares Subjekt. | Hat ein Subjekt und einen erwarteten Zustand. | Zentral fuer Kaffeemaschinenzustand, Agentenposition, Vivian-Feedback und Szenenzustand. |

## Functional/Runtime Bridge

| Element | Kurzbeschreibung | Wichtige Beziehungen und Regeln | Relevanz fuer die Beispiele |
| --- | --- | --- | --- |
| `Entity` | Fachlich relevante ausfuehrende oder beobachtete Entitaet mit optionaler grober `Entity.kind`-Typisierung. | Kann Capabilities bereitstellen; `Agent` ist spezialisierte Entity. Zulaessige EntityKind-Werte sind `agent`, `asset`, `zone`, `signal` und `stateObject`. | Kandidat fuer Vivian, Agenten, Kaffeemaschine, Werkzeuge und Szenenobjekte. |
| `Agent` | Ausfuehrende oder beobachtete Entitaet, die Rollen spielen kann. | Getrennt von `Actor`: Actor ist Rolle, Agent ist Instanz/Entitaet. | Wichtig fuer dynamisches Agentenmodellieren und fuer Vivian, falls Vivian als ausfuehrende Instanz modelliert wird. |
| `CapabilityUse` | Nutzung einer fachlichen Faehigkeit durch einen Szenarioschritt. | `ScenarioStep -> CapabilityUse [0..*]`; jede CapabilityUse referenziert genau eine `Capability [1]`. | Bruecke vom Szenarioschritt zur fachlichen Funktion, ohne direkt technisch zu werden. |
| `Capability` | Fachliche Faehigkeit mit Intent, Preconditions und versprochenem beobachtbarem Effekt. | Hat keine Endpoint-, Tool- oder Topic-Daten. Muss mindestens einen `Effect [1..*]` haben. Kann RuntimeBindings besitzen. | Beschreibt z. B. "Kaffee bruehen starten" oder "Agent bewegt sich zu Ziel". |
| `Effect` | Versprochener beobachtbarer Effekt einer Capability. | `Capability -> Effect [1..*]` composite. | Macht fachliche Funktionen pruefbar, z. B. Maschine ist brewing oder Agent ist an Zielposition. |
| `RuntimeBinding` | Technische Bindung einer fachlichen Capability an eine konkrete Plattform oder Laufzeitumgebung. | Referenziert genau eine Capability und besitzt `RuntimeAction [1..*]`. | Trennt fachliche Modellierung von Unity/WebXR/API/Tool-Aufrufen. |
| `RuntimeAction` | Konkrete technische Aktion, z. B. Endpoint, Tool oder Topic. | Liegt ausschliesslich unter RuntimeBinding; ScenarioStep darf nicht direkt darauf zeigen. | Hier landen konkrete Vivian-/VR-/Kaffeemaschinen-Controller-Aufrufe. |
| `FunctionBehavior` | Optionale EAST-ADL-nahe Bruecke zu formalem oder funktionalem Verhalten. | Im Diagramm als optionale Bruecke von Capability zu EAST-ADL::FunctionBehavior gefuehrt. | Nur verwenden, wenn eine Capability an bestehende EAST-ADL-Funktionsverhaltensmodelle angeschlossen werden soll. |
| `ValidationCase` | Validierungs- oder Testfall fuer erwartetes Verhalten. | Hat Stimulus und erwartetes Outcome; kann RuntimeBinding pruefen. | Dient dazu, Haupt-, Alternativ- und Fehlerablaeufe pruefbar zu machen. |

## Hilfs- und Attributkonzepte

| Konzept | Kurzbeschreibung | Relevanz |
| --- | --- | --- |
| `RandomVariable` | Attribut-/Hilfskonzept fuer probabilistische Bedingungen oder Unschaerfen. | Kann fuer Auftretenswahrscheinlichkeiten und dynamische Szenenvariabilitaet relevant werden. |
| `KeyValue` | Parameterstruktur fuer `CapabilityUse.parameters`. | Nuetzlich fuer konkrete Parameter wie Zielposition, Maschinen-ID oder Auswahloption. |
| `Schema` | Struktur fuer technische Ein- und Ausgabedaten einer RuntimeAction. | Relevant fuer RuntimeActions, aber nicht fuer fachliche Capabilities. |
| `Identifier` | Typ fuer eindeutige Identifikation. | Wichtig fuer Traceability und Referenzen. |

## Regeln, die fuer die Beispiele besonders wichtig sind

1. `Actor` und `Agent` nicht vermischen: Actor ist eine Rolle; Agent ist eine ausfuehrende oder beobachtete Entitaet.
2. `ScenarioStep` nicht technisch kurzschliessen: technische Ausfuehrung laeuft nur ueber `CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`.
3. `Capability` bleibt fachlich: keine Unity-Methode, kein MQTT-Topic, kein Toolname in Capability.
4. `RuntimeAction` bleibt technisch: konkrete Endpoints, Tools, Topics oder Controller-Aufrufe gehoeren dorthin.
5. `Include` nur fuer verpflichtendes Verhalten verwenden.
6. `Extend` nur fuer optionale oder bedingte Ergaenzung an einem gueltigen `ExtensionPoint` verwenden.
7. `ParallelGroup` besitzt keine Schritte, sondern referenziert mindestens zwei Schritte desselben Scenarios.
8. `Satisfy` muss die XOR-Regel beachten: Requirement oder UseCase, nicht beides in derselben Satisfy-Instanz.

## Offene Beobachtungen fuer spaetere Tasks

- Die Spezifikation enthaelt bereits ein Kaffeemaschinenbeispiel, aber noch nicht Vivian-spezifisch.
- Fuer dynamische Agenten koennte spaeter geprueft werden, ob `Agent`, `Entity`, `StateAssertion`, `Condition` und `Capability` ausreichen oder ob ein zusaetzliches Scene-/Agent-Extension-Modell noetig ist.
- Fuer Interaktionsobjekte koennte spaeter geprueft werden, ob Affordances, Objektzustandsautomaten oder Manipulationspunkte ein eigenes Ergaenzungsmodell benoetigen.
- Die aktuelle Spezifikation ist fachlich stark auf Traceability und Runtime-Trennung ausgelegt; raeumliche Struktur ist nur indirekt ueber `Condition`, `Event` und `StateAssertion` modellierbar.
