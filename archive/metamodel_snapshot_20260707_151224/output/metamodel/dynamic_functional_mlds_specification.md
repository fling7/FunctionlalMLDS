# Kompaktes Metamodell für Dynamic Functional MLDS

Version: v0.4, EAST-ADL-abgeglichen und bewusst verdichtet.

Quellenbasis: EAST-ADL Domain Model Specification V2.1.12, insbesondere Requirements, UseCases und VerificationValidation. Die EAST-ADL-Definitionen wurden nicht kopiert, sondern auf die für Dynamic Functional MLDS relevanten Beziehungen reduziert.

## Problem

Bestehende Text-zu-VR- oder MLDS-Pipelines können Räume, Objekte und teilweise Interaktionen erzeugen. Für eine wissenschaftlich belastbare Modellierung reicht das aber nicht aus: Es muss nachvollziehbar sein, welche Anforderung oder welcher Use Case eine dynamische Funktion motiviert, in welchem Szenarioschritt sie ausgelöst wird, welche fachliche Fähigkeit dadurch benötigt wird, wie diese Fähigkeit technisch gebunden wird und wie das Verhalten validiert werden kann.

Das Kernproblem ist also nicht: "Wie rufe ich in Unity oder WebXR eine Funktion auf?", sondern: "Wie bleibt eine dynamische Funktion von der Anforderung bis zur ausführbaren technischen Bindung traceable, prüfbar und austauschbar?"

## EAST-ADL-Abgleich

Die Use-Case-Semantik folgt EAST-ADL:

- `RequirementsModel` ist der Kontextcontainer für `Requirement` und `UseCase`.
- `Requirement`, `Actor` und `UseCase` sind `TraceableSpecification`.
- `Actor` beschreibt eine externe Rolle, nicht zwingend eine physische Instanz. Ein realer Benutzer, Sensor oder Agent kann mehrere Rollen spielen.
- `UseCase` beschreibt eine Nutzung des Systems und erfasst, was das System leisten soll.
- `Include` ist verpflichtend: Die Behavior des inkludierten Use Cases wird in den inkludierenden Use Case eingefügt; der inkludierende Use Case ist ohne diese Behavior nicht korrekt ausführbar.
- `Extend` ist ergänzend: Ein erweiternder Use Case ergänzt einen eigenständig sinnvollen Basis-Use-Case an einem oder mehreren `ExtensionPoint`.
- `ExtensionPoint` gehört zum erweiterten Use Case und bezeichnet die Stelle, an der Verhalten ergänzt werden darf.
- `Satisfy` verbindet Anforderungen oder Use Cases mit erfüllenden Elementen. Gemäß EAST-ADL darf eine einzelne `Satisfy`-Beziehung entweder Requirements oder UseCases referenzieren, aber nicht beides gleichzeitig.

## Was gegenüber der größeren Fassung geändert wurde

Das Modell wurde bewusst verkleinert:

- `SpatialEvent`, `TemporalEvent`, `EnvironmentEvent` usw. wurden zu `Event.kind` zusammengefasst.
- `SpatialConstraint`, Timing- und Guard-Ausdrücke wurden zu `Condition.kind` zusammengefasst.
- `ScenarioStep` erbt nicht mehr von `RedefinableElement`. In EAST-ADL ist `RedefinableElement` hier für `ExtensionPoint` relevant, nicht für jeden Schritt.
- `Actor` und `Agent` sind getrennt. `Actor` ist eine Rolle im Use Case; `Agent` ist eine ausführende oder beobachtete Entität, die diese Rolle spielen kann.
- `ParallelGroup` besitzt keine Schritte. Schritte gehören genau zum `Scenario`; eine Parallelgruppe referenziert nur mindestens zwei dieser Schritte.
- `ScenarioStep` zeigt nicht direkt auf technische APIs, Tools, Topics oder RuntimeActions. Der fachliche Pfad ist: `ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`.

## Modellidee

Das Metamodell besteht aus drei kompakten Teilen:

1. Der EAST-ADL-nahe Use-Case-Kern beschreibt Anforderungen, Use Cases, Actors, Include, Extend, ExtensionPoint und Satisfy.
2. Die Scenario-Erweiterung beschreibt konkrete dynamische Abläufe innerhalb eines Use Cases: Schritte, Ereignisse, Bedingungen, Zustandsaussagen, Alternativen und Parallelität.
3. Die Functional/Runtime Bridge trennt fachliche Fähigkeiten von technischer Ausführung: Ein Szenarioschritt benötigt eine `CapabilityUse`; diese referenziert eine fachliche `Capability`; erst `RuntimeBinding` ordnet diese Fähigkeit einer konkreten `RuntimeAction` zu.

## Zentrale Kardinalitäten

| Beziehung | Kardinalität | Bedeutung |
| --- | ---: | --- |
| `RequirementsModel -> Requirement` | `0..*` | Ein Requirements-Kontext kann beliebig viele Anforderungen enthalten. |
| `RequirementsModel -> UseCase` | `0..*` | Ein Requirements-Kontext kann beliebig viele Use Cases enthalten. |
| `UseCase -> ExtensionPoint` | `0..*` composite | ExtensionPoints gehören zum Use Case, dessen Verhalten erweitert werden darf. |
| `UseCase -> Include` | `0..*` composite | Ein Use Case kann verpflichtende Teilverhalten inkludieren. |
| `Include -> UseCase` | `addition [1]` | Genau ein Use Case liefert das eingefügte Verhalten. |
| `UseCase -> Extend` | `0..*` composite | Ein Use Case kann andere Use Cases erweitern. |
| `Extend -> UseCase` | `extendedCase [1]` | Genau ein Basis-Use-Case wird erweitert. |
| `Extend -> ExtensionPoint` | `1..*` | Die Erweiterung muss mindestens einen ExtensionPoint des Basis-Use-Cases adressieren. |
| `UseCase -> Scenario` | `1..*` composite | Jeder dynamisch ausführbare Use Case hat mindestens ein Szenario. |
| `Scenario -> ScenarioStep` | `1..*` ordered composite | Ein Szenario besteht aus geordneten Schritten. |
| `Scenario -> StepRelation` | `0..*` composite | Nichtlineare Flüsse werden explizit modelliert. |
| `ParallelGroup -> ScenarioStep` | `2..*` reference | Parallelität referenziert Schritte, besitzt sie aber nicht. |
| `ScenarioStep -> CapabilityUse` | `0..*` composite | Ein Schritt kann fachliche Fähigkeiten benötigen. |
| `CapabilityUse -> Capability` | `1` | Jede Nutzung referenziert genau eine fachliche Fähigkeit. |
| `Capability -> RuntimeBinding` | `0..*` | Eine fachliche Fähigkeit kann auf keiner, einer oder mehreren Plattformen technisch gebunden werden. |
| `RuntimeBinding.capability` | `1` | Jede technische Bindung referenziert genau eine fachliche Fähigkeit. |
| `RuntimeBinding -> RuntimeAction` | `1..*` composite | Eine Fähigkeit kann durch eine oder mehrere technische Aktionen realisiert werden. |
| `Capability -> Effect` | `1..*` composite | Eine Fähigkeit muss mindestens einen beobachtbaren versprochenen Effekt haben. |

## Invarianten

1. Pro `UseCase` muss genau ein `Scenario.kind = main` existieren. Alternative und Exception-Szenarien dürfen zusätzlich existieren.
2. `Include` beschreibt verpflichtende Wiederverwendung. Optionales oder bedingtes Zusatzverhalten ist kein Include, sondern ein `Extend` oder eine `StepRelation.kind = alternative|exception`.
3. Ein `Extend.extensionLocation` muss auf `ExtensionPoint`-Elemente zeigen, die zum `extendedCase` gehören.
4. Eine `Satisfy`-Instanz referenziert entweder `Requirement` oder `UseCase`, nicht beides gleichzeitig.
5. `ScenarioStep` darf keine direkte Referenz auf `RuntimeAction`, API-Endpunkte, Tools oder Message Topics besitzen.
6. `Capability` enthält keine technischen Endpoint- oder Tool-Daten. Technische Details liegen ausschließlich in `RuntimeBinding` und `RuntimeAction`.
7. Alle `ScenarioStep`-Elemente einer `ParallelGroup` müssen zum selben `Scenario` gehören.
8. Wenn `ScenarioStep.kind = actorIntent`, dann sollte `performedBy` auf einen `Actor` zeigen. Bei Systemantworten wird die ausführende Logik über `CapabilityUse` und `Capability` modelliert.

## Beispiel: Interaktive Kaffeemaschine im virtuellen Raum

Angenommen, ein Besucher in einem VR-Schulungsraum soll eine Kaffeemaschine bedienen können.

Requirement:
`REQ-001`: "Der Benutzer muss den Brühvorgang durch Drücken der Starttaste auslösen können."

Use Case:
`UC_StartBrewing`: "Kaffee brühen starten"

Actor:
`Visitor`: externe Rolle, die mit dem System interagiert.

Include:
`UC_StartBrewing` inkludiert `UC_CheckMachineReady`. Das ist verpflichtend, weil der Brühvorgang ohne verfügbare Maschine, Wasser und Tasse nicht korrekt ausführbar ist.

ExtensionPoint:
`EP_AfterStartCommand`: Stelle nach dem Startkommando.

Extend:
`UC_ExplainBrewing` erweitert `UC_StartBrewing` an `EP_AfterStartCommand`, falls der Trainingsmodus aktiv ist. Das ist kein Include, weil die Erklärung optional ist und der Basis-Use-Case auch ohne Erklärung sinnvoll bleibt.

Scenario:
`SC_MainStartBrewing` ist das Main-Szenario von `UC_StartBrewing`.

ScenarioSteps:
- `S1`: Visitor drückt die Starttaste. `triggeredBy = Event(kind=user, expression="press(startButton)")`
- `S2`: Das System prüft die Bereitschaft. `requires = CapabilityUse(CheckMachineReady)`
- `S3`: Das System startet den Brühvorgang. `requires = CapabilityUse(StartBrewing)` und `resultingState = StateAssertion(coffeeMachine.state = brewing)`

Capability:
`StartBrewing` beschreibt fachlich: "Setzt die Kaffeemaschine in den Zustand brewing und macht den Brühfortschritt sichtbar." Die Capability kennt keine Unity-Methode, keinen MQTT-Topic und keinen API-Endpunkt.

RuntimeBinding:
`RB_StartBrewing_WebXR` bindet `StartBrewing` an technische Aktionen, z. B. `RuntimeAction(endpoint="CoffeeMachineController.startBrewing()", inputSchema="machineId")`.

ValidationCase:
`VC_StartBrewing`: Bei Stimulus `press(startButton)` und Vorbedingung `machine.ready = true` muss der erwartete Zustand `coffeeMachine.state = brewing` eintreten und eine Fortschrittsanzeige sichtbar sein.

Damit ist die Funktion von der Anforderung bis zur ausführbaren VR-Interaktion nachvollziehbar:

`REQ-001 -> UC_StartBrewing -> SC_MainStartBrewing -> S3 -> CapabilityUse(StartBrewing) -> Capability(StartBrewing) -> RuntimeBinding -> RuntimeAction -> ValidationCase`

## Interpretation

Das Modell trennt bewusst drei Fragen:

- Was soll das System aus Sicht von Anforderungen und Use Cases leisten?
- Wann tritt dieses Verhalten in einem Szenario auf?
- Wie wird die fachliche Fähigkeit auf einer konkreten Plattform ausgeführt und validiert?

Diese Trennung ist entscheidend, weil ein MLDS- oder LLM-basierter Generator dadurch nicht sofort technische Aktionen halluzinieren muss. Er kann zuerst Use Case, Szenario, Bedingung und Capability erzeugen. Erst danach wird eine gültige RuntimeBinding ausgewählt oder erzeugt. Das macht die Pipeline erklärbarer, austauschbarer und prüfbarer.

## Quellen

- EAST-ADL Association: EAST-ADL Domain Model Specification V2.1.12, Requirements, UseCases und VerificationValidation: https://east-adl.info/Specification/V2.1.12/EAST-ADL-Specification_V2.1.12.pdf
- EAST-ADL Specification Portal: https://east-adl.info/Specification.html
