# Abgleich Diagrammbeziehungen gegen Spezifikation

Stand: 2026-07-07

Task: 1.2 `Aktuelles Diagramm gegen die Spezifikation abgleichen`

Quellen:

- Diagrammdefinition: `tools/generate_dynamic_functional_mlds.py`
- Spezifikation: `output/metamodel/dynamic_functional_mlds_specification.md`

## Ergebnis

Alle 30 sichtbaren Diagramm-/Mermaid-Beziehungen und gezeichneten Attributbeziehungen aus dem aktuellen Stand sind in der Spezifikation auffindbar. Die zwei v0.5-Ergaenzungen sind als `21a` und `24a` eingefuegt, damit fruehere Pruefverweise stabil bleiben. Fuer die Beziehungen, die vorher nur implizit ueber Text, Attribute oder Beispiel erklaert waren, wurde in der generierten Spezifikation der Abschnitt `Diagramm-Beziehungsabdeckung` ergaenzt.

## Abgleichliste

| Nr. | Diagrammbeziehung | Diagrammlabel | Typ im Diagramm | Spezifikationsstelle | Status |
| ---: | --- | --- | --- | --- | --- |
| 1 | `RequirementsModel -> Requirement` | contains requirements `[0..*]` | composition | `Zentrale Kardinalitaeten`; `Diagramm-Beziehungsabdeckung` | OK |
| 2 | `RequirementsModel -> UseCase` | contains use cases `[0..*]` | composition | `Zentrale Kardinalitaeten`; `Diagramm-Beziehungsabdeckung` | OK |
| 3 | `Actor -> UseCase` | interacts with `[0..*]` | association | `EAST-ADL-Abgleich`; `Diagramm-Beziehungsabdeckung` | OK |
| 4 | `UseCase -> ExtensionPoint` | defines extension points `[0..*]` | composition | `Zentrale Kardinalitaeten`; `Diagramm-Beziehungsabdeckung` | OK |
| 5 | `UseCase -> Include` | contains Include relationships `[0..*]` | composition | `Zentrale Kardinalitaeten`; `Diagramm-Beziehungsabdeckung` | OK |
| 6 | `UseCase -> Extend` | contains Extend relationships `[0..*]` | composition | `Zentrale Kardinalitaeten`; `Diagramm-Beziehungsabdeckung` | OK |
| 7 | `Extend -> ExtensionPoint` | extension location `[1..*]` | association | `Zentrale Kardinalitaeten`; `Invarianten`; `Diagramm-Beziehungsabdeckung` | OK |
| 8 | `Satisfy -> Requirement` | satisfies requirement `[0..*]` | association | `EAST-ADL-Abgleich`; `Invarianten`; `Diagramm-Beziehungsabdeckung` | OK |
| 9 | `Satisfy -> UseCase` | satisfies use case `[0..*]` | association | `EAST-ADL-Abgleich`; `Invarianten`; `Diagramm-Beziehungsabdeckung` | OK |
| 10 | `UseCase -> Scenario` | contains executable scenarios `[1..*]` | composition | `Zentrale Kardinalitaeten`; `Invarianten`; `Diagramm-Beziehungsabdeckung` | OK |
| 11 | `Scenario -> ScenarioStep` | contains ordered steps `[1..*]` | ordered composition | `Zentrale Kardinalitaeten`; `Diagramm-Beziehungsabdeckung` | OK |
| 12 | `Scenario -> StepRelation` | contains step relations `[0..*]` | composition | `Zentrale Kardinalitaeten`; `Invarianten`; `Diagramm-Beziehungsabdeckung` | OK |
| 13 | `Scenario -> ParallelGroup` | contains parallel groups `[0..*]` | composition | `Modellidee`; `Diagramm-Beziehungsabdeckung` | OK |
| 14 | `ScenarioStep -> Event` | triggered by event `[0..*]` | association | `Modellidee`; `Beispiel`; `Diagramm-Beziehungsabdeckung` | OK |
| 15 | `ScenarioStep -> Condition` | guard condition `[0..1]` | association | `Modellidee`; `Was geaendert wurde`; `Diagramm-Beziehungsabdeckung` | OK |
| 16 | `ScenarioStep -> StateAssertion` | resulting state `[0..*]` | association | `Modellidee`; `Beispiel`; `Diagramm-Beziehungsabdeckung` | OK |
| 17 | `StepRelation -> ScenarioStep` | source step `[1]` | association | `Zentrale Kardinalitaeten`; `Diagramm-Beziehungsabdeckung` | OK |
| 18 | `StepRelation -> ScenarioStep` | target step `[1]` | association | `Zentrale Kardinalitaeten`; `Diagramm-Beziehungsabdeckung` | OK |
| 19 | `ParallelGroup -> ScenarioStep` | member steps `[2..*]` | reference | `Zentrale Kardinalitaeten`; `Invarianten`; `Diagramm-Beziehungsabdeckung` | OK |
| 20 | `Agent -> Entity` | specialization | inheritance | `Was geaendert wurde`; `Diagramm-Beziehungsabdeckung` | OK |
| 21 | `Entity -> Capability` | provides capability `[0..*]` | association | `Diagramm-Beziehungsabdeckung`; `Functional/Runtime Bridge`-Modellidee | OK |
| 21a | `Entity -> EntityKind` | kind `[0..1]` | typed attribute / Mermaid reference | `Zentrale Kardinalitaeten`; `Diagramm-Beziehungsabdeckung`; `Kernanpassungen v0.5` | OK |
| 22 | `ScenarioStep -> CapabilityUse` | requires capability use `[0..*]` | composition | `Zentrale Kardinalitaeten`; `Modellidee`; `Invarianten`; `Diagramm-Beziehungsabdeckung` | OK |
| 23 | `CapabilityUse -> Capability` | uses capability `[1]` | association | `Zentrale Kardinalitaeten`; `Modellidee`; `Diagramm-Beziehungsabdeckung` | OK |
| 24 | `Capability -> Effect` | promised effect `[1..*]` | composition | `Zentrale Kardinalitaeten`; `Diagramm-Beziehungsabdeckung` | OK |
| 24a | `Effect -> StateAssertion` | evidenced by state assertion `[0..*]` | reference | `Zentrale Kardinalitaeten`; `Invarianten`; `Diagramm-Beziehungsabdeckung`; `Kernanpassungen v0.5` | OK |
| 25 | `Capability -> FunctionBehavior` | refines function behavior `[0..*]` | optional association | `Diagramm-Beziehungsabdeckung` | OK |
| 26 | `Capability -> RuntimeBinding` | runtime binding `[0..*]` | association | `Zentrale Kardinalitaeten`; `Modellidee`; `Diagramm-Beziehungsabdeckung` | OK |
| 27 | `RuntimeBinding -> RuntimeAction` | maps to runtime action `[1..*]` | composition | `Zentrale Kardinalitaeten`; `Invarianten`; `Diagramm-Beziehungsabdeckung` | OK |
| 28 | `ValidationCase -> RuntimeBinding` | checks runtime binding `[0..*]` | dependency | `Diagramm-Beziehungsabdeckung`; `Beispiel`; `Interpretation` | OK |

## Beobachtung fuer spaetere Tasks

Der Abgleich zeigt, dass die Spezifikation vor Task 1.2 die Kernkardinalitaeten gut abgedeckt hat, aber einige sichtbare Kanten nur implizit enthielt. Das ist jetzt fuer den aktuellen v0.5-Stand bereinigt, einschliesslich `Entity.kind [0..1]` und `Effect.evidencedBy -> StateAssertion [0..*]`. Task 14.3 kann daher die Kardinalitaeten aus Diagramm und Spezifikation final pruefen, ohne verdeckte Beziehungen nachtragen zu muessen.
