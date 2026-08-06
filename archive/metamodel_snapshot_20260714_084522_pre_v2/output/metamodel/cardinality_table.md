# Kardinalitaetstabelle des aktuellen Metamodells

Stand: 2026-07-07

Task: 1.3 `Alle Kardinalitaeten aus Diagramm und Spezifikation extrahieren`

Quellen:

- Diagramm/Generator: `tools/generate_dynamic_functional_mlds.py`
- Spezifikation: `output/metamodel/dynamic_functional_mlds_specification.md`
- Diagramm-Spezifikationsabgleich: `output/metamodel/diagram_spec_alignment.md`

## Ergebnis

Alle 30 sichtbaren Diagramm-/Mermaid-Beziehungen und gezeichneten Attributbeziehungen sind in der Kardinalitaetstabelle enthalten. Die zwei v0.5-Ergaenzungen sind als `21a` und `24a` eingefuegt, damit fruehere Pruefverweise stabil bleiben. Zusaetzlich sind die spezifikations- und attributbasierten Kardinalitaeten erfasst, die nicht als eigene sichtbare Kante im SVG-Diagramm vorkommen.

## A. Sichtbare Diagramm- und Mermaid-Beziehungen

| Nr. | Quelle | Ziel | Label / Rollenname | Diagrammtyp | Kardinalitaet am Ziel/Rollenende | Besitzsemantik | Spezifikationsstatus |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `RequirementsModel` | `Requirement` | contains requirements | composition | `0..*` | Requirements gehoeren zum RequirementsModel. | explizit in zentraler Kardinalitaetentabelle |
| 2 | `RequirementsModel` | `UseCase` | contains use cases | composition | `0..*` | UseCases gehoeren zum RequirementsModel. | explizit in zentraler Kardinalitaetentabelle |
| 3 | `Actor` | `UseCase` | interacts with | association | `0..*` | keine Besitzsemantik | in Diagramm und Beziehungsabdeckung explizit; zentrale Kardinalitaetentabelle enthaelt diese Kante nicht |
| 4 | `UseCase` | `ExtensionPoint` | defines extension points | composition | `0..*` | ExtensionPoints gehoeren zum UseCase. | explizit in zentraler Kardinalitaetentabelle |
| 5 | `UseCase` | `Include` | contains Include relationships | composition | `0..*` | Include-Beziehungen gehoeren zum UseCase. | explizit in zentraler Kardinalitaetentabelle |
| 6 | `UseCase` | `Extend` | contains Extend relationships | composition | `0..*` | Extend-Beziehungen gehoeren zum UseCase. | explizit in zentraler Kardinalitaetentabelle |
| 7 | `Extend` | `ExtensionPoint` | extension location | association | `1..*` | keine Besitzsemantik | explizit in zentraler Kardinalitaetentabelle und Invarianten |
| 8 | `Satisfy` | `Requirement` | satisfies requirement | association | `0..*` | keine Besitzsemantik | in Diagramm und Beziehungsabdeckung explizit; XOR-Regel in Invarianten |
| 9 | `Satisfy` | `UseCase` | satisfies use case | association | `0..*` | keine Besitzsemantik | in Diagramm und Beziehungsabdeckung explizit; XOR-Regel in Invarianten |
| 10 | `UseCase` | `Scenario` | contains executable scenarios | composition | `1..*` | Scenarios gehoeren zum UseCase. | explizit in zentraler Kardinalitaetentabelle und Invarianten |
| 11 | `Scenario` | `ScenarioStep` | contains ordered steps | ordered composition | `1..*` | ScenarioSteps gehoeren zum Scenario. | explizit in zentraler Kardinalitaetentabelle |
| 12 | `Scenario` | `StepRelation` | contains step relations | composition | `0..*` | StepRelations gehoeren zum Scenario. | explizit in zentraler Kardinalitaetentabelle |
| 13 | `Scenario` | `ParallelGroup` | contains parallel groups | composition | `0..*` | ParallelGroups gehoeren zum Scenario. | in Diagramm und Beziehungsabdeckung explizit; zentrale Kardinalitaetentabelle enthaelt diese Kante nicht |
| 14 | `ScenarioStep` | `Event` | triggered by event | association | `0..*` | keine Besitzsemantik | in Diagramm, Beispiel und Beziehungsabdeckung explizit |
| 15 | `ScenarioStep` | `Condition` | guard condition | association | `0..1` | keine Besitzsemantik | in Diagramm, Verdichtungsbeschreibung und Beziehungsabdeckung explizit |
| 16 | `ScenarioStep` | `StateAssertion` | resulting state | association | `0..*` | keine Besitzsemantik | in Diagramm, Beispiel und Beziehungsabdeckung explizit |
| 17 | `StepRelation` | `ScenarioStep` | source step | association | `1` | keine Besitzsemantik | in Beziehungsabdeckung explizit; Kardinalitaet ergibt sich aus Diagrammrolle |
| 18 | `StepRelation` | `ScenarioStep` | target step | association | `1` | keine Besitzsemantik | in Beziehungsabdeckung explizit; Kardinalitaet ergibt sich aus Diagrammrolle |
| 19 | `ParallelGroup` | `ScenarioStep` | member steps | reference | `2..*` | referenziert Schritte, besitzt sie aber nicht | explizit in zentraler Kardinalitaetentabelle und Invarianten |
| 20 | `Agent` | `Entity` | specialization | inheritance | nicht anwendbar | Agent ist spezialisierte Entity. | explizit in Verdichtungsbeschreibung und Beziehungsabdeckung |
| 21 | `Entity` | `Capability` | provides capability | association | `0..*` | keine Besitzsemantik | in Diagramm und Beziehungsabdeckung explizit |
| 21a | `Entity` | `EntityKind` | kind | typed attribute / Mermaid reference | `0..1` | keine Besitzsemantik; EntityKind typisiert nur grob | explizit in v0.5-Spezifikation, Mermaid und Kernanpassungen |
| 22 | `ScenarioStep` | `CapabilityUse` | requires capability use | composition | `0..*` | CapabilityUses gehoeren zum ScenarioStep. | explizit in zentraler Kardinalitaetentabelle |
| 23 | `CapabilityUse` | `Capability` | uses capability | association | `1` | keine Besitzsemantik | explizit in zentraler Kardinalitaetentabelle |
| 24 | `Capability` | `Effect` | promised effect | composition | `1..*` | Effects gehoeren zur Capability. | explizit in zentraler Kardinalitaetentabelle |
| 24a | `Effect` | `StateAssertion` | evidenced by state assertion | reference | `0..*` | keine Besitzsemantik; StateAssertions werden nicht vom Effect besessen | explizit in v0.5-Spezifikation, Diagramm, Mermaid und Kernanpassungen |
| 25 | `Capability` | `FunctionBehavior` | refines function behavior | optional bridge | `0..*` | keine Besitzsemantik | in Beziehungsabdeckung explizit |
| 26 | `Capability` | `RuntimeBinding` | runtime binding | association | `0..*` | keine Besitzsemantik | explizit in zentraler Kardinalitaetentabelle |
| 27 | `RuntimeBinding` | `RuntimeAction` | maps to runtime action | composition | `1..*` | RuntimeActions gehoeren zur RuntimeBinding. | explizit in zentraler Kardinalitaetentabelle |
| 28 | `ValidationCase` | `RuntimeBinding` | checks runtime binding | dependency | `0..*` | keine Besitzsemantik | in Beziehungsabdeckung, Beispiel und Interpretation explizit |

## B. Nicht separat gezeichnete Spezifikations- und Attributkardinalitaeten

Diese Kardinalitaeten sind fuer die Beispielmodellierung relevant, erscheinen aber nicht alle als eigene sichtbare Diagrammkante. Einige sind als Attribute in Klassenboxen oder in der Spezifikation formuliert.

| Element / Beziehung | Kardinalitaet | Quelle | Bedeutung fuer die spaetere Beispielarbeit |
| --- | ---: | --- | --- |
| `RequirementsModel.requirement` | `0..*` | Klassenattribut und zentrale Kardinalitaet | Ein Kontext kann beliebig viele Anforderungen enthalten. |
| `RequirementsModel.useCase` | `0..*` | Klassenattribut und zentrale Kardinalitaet | Ein Kontext kann beliebig viele UseCases enthalten. |
| `Satisfy.satisfiedRequirement` | `0..*` | Klassenattribut, EAST-ADL-Abgleich, Invariante | Satisfy darf Requirements referenzieren, aber XOR-Regel beachten. |
| `Satisfy.satisfiedUseCase` | `0..*` | Klassenattribut, EAST-ADL-Abgleich, Invariante | Satisfy darf UseCases referenzieren, aber XOR-Regel beachten. |
| `Satisfy.satisfiedBy` | `1..*` | Klassenattribut | Mindestens ein identifizierbares Element erfuellt die referenzierte Spezifikation. |
| `Include.addition` | `1` | Klassenattribut und zentrale Kardinalitaet | Ein Include fuegt genau einen UseCase verpflichtend ein. |
| `Extend.extendedCase` | `1` | Klassenattribut und zentrale Kardinalitaet | Ein Extend erweitert genau einen Basis-UseCase. |
| `Extend.extensionLocation` | `1..*` | Klassenattribut, zentrale Kardinalitaet, Invariante | Eine Erweiterung muss mindestens eine gueltige Erweiterungsstelle adressieren. |
| `Extend.condition` | `0..1` | Klassenattribut | Eine Erweiterung kann bedingt sein, muss es aber nicht. |
| `Scenario.pre/postcondition` | `0..*` | Klassenattribut | Ein Scenario kann mehrere Vor- oder Nachbedingungen besitzen. |
| `ScenarioStep.performedBy` | `0..1` | Klassenattribut und Invariante | Ein actorIntent-Schritt sollte auf hoechstens einen Actor zeigen. |
| `ScenarioStep.occurrenceProbability` | `0..1` | Klassenattribut | Ein Schritt kann probabilistisch annotiert werden. |
| `StepRelation.guard` | `0..1` | Klassenattribut | Eine Ablaufbeziehung kann genau eine Guard Condition besitzen. |
| `StepRelation.probability` | `0..1` | Klassenattribut | Eine Alternative oder Verzweigung kann eine Wahrscheinlichkeit besitzen. |
| `ParallelGroup.memberStep` | `2..*` | Klassenattribut und sichtbare Kante | Parallelitaet braucht mindestens zwei Mitgliedsschritte. |
| `Condition.randomVariable` | `0..*` | Klassenattribut | Bedingungen koennen probabilistische Variablen referenzieren. |
| `StateAssertion.subject` | `1` | Klassenattribut | Jede Zustandsaussage braucht genau ein identifizierbares Subjekt. |
| `Agent.playsActor` | `0..*` | Klassenattribut | Eine Agent-Entitaet kann mehrere externe Rollen spielen. |
| `Entity.kind` | `0..1` | Klassenattribut, Mermaid, v0.5-Spezifikation | Eine Entity kann optional genau eine grobe Art besitzen: `agent`, `asset`, `zone`, `signal` oder `stateObject`. |
| `CapabilityUse.capability` | `1` | Klassenattribut und zentrale Kardinalitaet | Jede Faehigkeitsnutzung referenziert genau eine Capability. |
| `CapabilityUse.parameters` | `0..*` | Klassenattribut | Eine Faehigkeitsnutzung kann beliebig viele Parameter besitzen. |
| `Capability.precondition` | `0..*` | Klassenattribut | Eine Capability kann fachliche Vorbedingungen haben. |
| `Capability.promisedEffect` | `1..*` | Klassenattribut und zentrale Kardinalitaet | Jede Capability muss mindestens einen beobachtbaren Effekt versprechen. |
| `Effect.observableBy` | `0..*` | Klassenattribut | Ein Effekt kann von beliebig vielen Actor-Rollen beobachtbar sein. |
| `Effect.evidencedBy` | `0..*` | v0.5-Spezifikation und sichtbare Diagrammbeziehung | Ein Effect kann durch beliebig viele StateAssertions fachlich beobachtbar gemacht werden; die Beziehung ist optional und nicht-kompositiv. |
| `FunctionBehavior.behaviorKind` | `0..1` | Klassenattribut | Die optionale EAST-ADL-Bruecke kann typisiert werden. |
| `FunctionBehavior.formal reference` | `0..1` | Klassenattribut | Optionaler Verweis auf formale Verhaltensbeschreibung. |
| `RuntimeBinding.capability` | `1` | Klassenattribut und zentrale Kardinalitaet | Jede technische Bindung gehoert genau zu einer fachlichen Capability. |
| `RuntimeBinding.runtimeAction` | `1..*` | Klassenattribut und zentrale Kardinalitaet | Jede RuntimeBinding muss mindestens eine technische Aktion enthalten. |
| `RuntimeAction.inputSchema` | `0..1` | Klassenattribut | Eine technische Aktion kann ein Eingabeschema besitzen. |
| `RuntimeAction.outputSchema` | `0..1` | Klassenattribut | Eine technische Aktion kann ein Ausgabeschema besitzen. |
| `ValidationCase.stimulus` | `0..*` | Klassenattribut | Ein ValidationCase kann mehrere Stimuli referenzieren. |
| `ValidationCase.expectedOutcome` | `1..*` | Klassenattribut | Ein ValidationCase muss mindestens ein erwartetes Ergebnis besitzen. |

## C. Konsistenzbefund

- Keine sichtbare Diagramm-/Mermaid-Beziehung fehlt in Abschnitt A.
- Die sichtbaren Kardinalitaeten sind mit der aktuellen Diagrammdefinition konsistent.
- Einige Beziehungen sind im Diagramm sichtbar, aber nicht in der zentralen Kardinalitaetentabelle der Spezifikation enthalten. Sie sind nun in `diagram_spec_alignment.md` und in Abschnitt A dieser Tabelle explizit erfasst.
- Die v0.5-Ergaenzungen `Entity.kind [0..1]` und `Effect.evidencedBy -> StateAssertion [0..*]` sind sowohl als sichtbare bzw. gezeichnete Beziehungen als auch in Abschnitt B als Attribut-/Referenzkardinalitaeten erfasst.
- Die nicht separat gezeichneten Kardinalitaeten in Abschnitt B sind wichtig fuer die spaetere Instanziierung der Beispielszenarien, besonders fuer Vivian, Agenten, Kaffeemaschine, Capabilities, RuntimeBindings und ValidationCases.

## D. Konsequenz fuer die naechsten Schritte

Task 1.4 kann auf dieser Tabelle aufbauen und die Invarianten extrahieren. Besonders relevant sind:

- genau ein Main-Scenario pro UseCase,
- keine direkte `ScenarioStep -> RuntimeAction`-Kante,
- Trennung von Actor und Agent,
- XOR-Regel bei `Satisfy`,
- `ParallelGroup` referenziert mindestens zwei Schritte desselben Scenario,
- `Capability` enthaelt keine technischen Runtime-Daten.
