# Abschlusspruefung 14.3: Kardinalitaeten final

Stand: 2026-07-08

Task: 14.3 `Kardinalitaeten final pruefen`

## Ergebnis

Die final geprueften Artefakte verletzen keine Kardinalitaet des aktuellen v0.5-Kernmetamodells. Die beiden spaeter eingefuehrten Kernpraezisierungen sind rueckwaertskompatibel und korrekt beruecksichtigt:

- `Entity.kind [0..1]` ist optional und nutzt nur die Werte `agent`, `asset`, `zone`, `signal` oder `stateObject`.
- `Effect.evidencedBy -> StateAssertion [0..*]` ist optional, nicht-kompositiv und ersetzt keinen `ValidationCase`.

Die zentrale Kardinalitaetstabelle und der Diagramm-Spezifikationsabgleich wurden von 28 auf 30 Beziehungen nachgezogen. Die neuen Beziehungen sind als `21a` und `24a` eingefuegt, damit bestehende Pruefverweise stabil bleiben.

## Gepruefte Artefakte

| Artefakt | Pruefzweck | Ergebnis |
| --- | --- | --- |
| `dynamic_functional_mlds_specification.md` | Normative v0.5-Kardinalitaeten und Invarianten | bestanden |
| `dynamic_functional_mlds_metamodel.mmd` | Mermaid-Beziehungen, insbesondere `EntityKind` und `evidencedBy` | bestanden |
| `cardinality_table.md` | Vollstaendige Beziehungstabelle | nachgezogen, bestanden |
| `diagram_spec_alignment.md` | Abgleich Diagramm gegen Spezifikation | nachgezogen, bestanden |
| `use_case_A_cardinality_check.md` | A-Instanzen gegen Kardinalitaeten | nachgezogen, bestanden |
| `use_case_B_cardinality_invariant_check.md` | B-Instanzen gegen Kardinalitaeten und Invarianten | nachgezogen, bestanden |
| `use_case_A_effect_instances.md` | A-Effects und Evidence-Bezuege | nachgezogen, bestanden |
| `use_case_B_validation_case_instances.md` | ValidationCase-Validierungsziel fuer B | bestanden nach 14.2-Korrektur |

## Normative Beziehungsmatrix

| Nr. | Beziehung / Eigenschaft | Soll | A-Befund | B-Befund | Ergebnis |
| ---: | --- | --- | --- | --- | --- |
| 1 | `RequirementsModel -> Requirement` | `0..*` | 15 Requirements | 18 Requirements | bestanden |
| 2 | `RequirementsModel -> UseCase` | `0..*` | 1 UseCase | 1 UseCase | bestanden |
| 3 | `Actor -> UseCase` | `0..*` | 3 Actors interagieren mit `UC-A-01` | `Visitor` interagiert mit `UC-B-01` | bestanden |
| 4 | `UseCase -> ExtensionPoint` | `0..*` | 0, erlaubt | 0, erlaubt | bestanden |
| 5 | `UseCase -> Include` | `0..*` | 0, erlaubt | 0, erlaubt | bestanden |
| 6 | `UseCase -> Extend` | `0..*` | 0, erlaubt | 0, erlaubt | bestanden |
| 7 | `Extend -> ExtensionPoint` | `1..*`, falls Extend existiert | nicht anwendbar | nicht anwendbar | bestanden |
| 8 | `Satisfy -> Requirement` | `0..*`, XOR mit UseCase-Zweig | 15 Requirement-Satisfy | keine formalen B-Satisfy | bestanden |
| 9 | `Satisfy -> UseCase` | `0..*`, XOR mit Requirement-Zweig | 1 UseCase-Satisfy | keine formalen B-Satisfy | bestanden |
| 10 | `Satisfy.satisfiedBy` | `1..*`, falls Satisfy existiert | jede A-Satisfy-Instanz belegt | nicht anwendbar | bestanden |
| 11 | `UseCase -> Scenario` | `1..*` | 3 Scenarios | 3 Scenarios | bestanden |
| 12 | genau ein `Scenario.kind = main` pro UseCase | `1` | genau 1 Main | genau 1 Main | bestanden |
| 13 | `Scenario -> ScenarioStep` | `1..*` | 14 Steps verteilt auf 3 Scenarios | 28 Steps verteilt auf 3 Scenarios | bestanden |
| 14 | `Scenario -> StepRelation` | `0..*` | 14 Relations | 28 formale Relations | bestanden |
| 15 | `StepRelation.sourceStep` | `1` | jede Relation genau 1 Source | jede Relation genau 1 Source | bestanden |
| 16 | `StepRelation.targetStep` | `1` | jede Relation genau 1 Target | jede Relation genau 1 Target | bestanden |
| 17 | `Scenario -> ParallelGroup` | `0..*` | 0, erlaubt | 0, erlaubt | bestanden |
| 18 | `ParallelGroup -> ScenarioStep` | `2..*`, falls ParallelGroup existiert | nicht anwendbar | nicht anwendbar | bestanden |
| 19 | `ScenarioStep -> Event` | `0..*` | 5 Zuordnungen, leere Steps erlaubt | alle 28 Steps fachlich getriggert | bestanden |
| 20 | `ScenarioStep -> Condition` | `0..1` Guard je Step | hoechstens 1 Guard | hoechstens 1 Guard | bestanden |
| 21 | `ScenarioStep -> StateAssertion` | `0..*` | 28 StateAssertions | 30 StateAssertions | bestanden |
| 22 | `ScenarioStep.performedBy` | `0..1` | leer, weil keine actorIntent-Steps | nur Visitor bei actorIntent-Steps | bestanden |
| 23 | `Agent -> Entity` | Spezialisierung | AgentBody als Agent/Entity | Vivian als Agent/Entity | bestanden |
| 24 | `Agent.playsActor` | `0..*` | leer, erlaubt | leer, erlaubt | bestanden |
| 25 | `Entity -> Capability` | `0..*` | AgentBody stellt 3 Capabilities bereit | Vivian 9, CoffeeMachine 2 | bestanden |
| 26 | `Entity.kind` | `0..1` | gesetzte Werte zulaessig; ein Entity bewusst untypisiert | gesetzte Werte zulaessig | bestanden |
| 27 | `ScenarioStep -> CapabilityUse` | `0..*` | 3 CapabilityUses | 11 CapabilityUses | bestanden |
| 28 | `CapabilityUse -> Capability` | `1` | jede CapabilityUse genau 1 Capability | jede CapabilityUse genau 1 Capability | bestanden |
| 29 | `Capability -> Effect` | `1..*` | jede Capability 2 Effects | jede Capability 1 Effect | bestanden |
| 30 | `Effect -> StateAssertion` | `0..*`, nicht-kompositiv | alle 6 Effects haben StateAssertion-Trace | alle 11 Effects haben StateAssertion-Trace | bestanden |
| 31 | `Effect.observableBy` | `0..*` | alle 6 Effects durch `SceneObserver` beobachtbar | leer oder dokumentarisch, erlaubt | bestanden |
| 32 | `Capability -> FunctionBehavior` | `0..*` | 0, erlaubt | 0, erlaubt | bestanden |
| 33 | `Capability -> RuntimeBinding` | `0..*` | 3 Bindings | 11 Bindings | bestanden |
| 34 | `RuntimeBinding.capability` | `1` | jede Binding genau 1 Capability | jede Binding genau 1 Capability | bestanden |
| 35 | `RuntimeBinding -> RuntimeAction` | `1..*` | jede Binding 2 Actions | jede Binding 2 oder 3 Actions | bestanden |
| 36 | `RuntimeAction.inputSchema` | `0..1` | jede Action hoechstens 1 Schema | jede Action hoechstens 1 Schema | bestanden |
| 37 | `RuntimeAction.outputSchema` | `0..1` | jede Action hoechstens 1 Schema | jede Action hoechstens 1 Schema | bestanden |
| 38 | `ValidationCase.validates` | UseCase-Referenz, kein Scenario-Ziel | `UC-A-01` | `UC-B-01` nach 14.2-Korrektur | bestanden |
| 39 | `ValidationCase -> RuntimeBinding` | `0..*` | strukturelle Cases duerfen 0 haben; Runtime-Cases pruefen Bindings | strukturelle Cases duerfen 0 haben; Runtime-Cases pruefen Bindings | bestanden |
| 40 | `ValidationCase.expectedOutcome` | `1..*` | alle 8 Cases belegt | alle 10 Cases belegt | bestanden |

## V0.5-Zusatzpruefung

### Entity.kind

`Entity.kind` ist keine neue Pflichtklassifikation. Dadurch bleiben bestehende Entities ohne Typisierung gueltig. Wenn ein Wert gesetzt wird, muss er aus der kleinen v0.5-Enumeration stammen.

| Use Case | Befund | Ergebnis |
| --- | --- | --- |
| A | `DynamicSceneAgent`, `UserEmbodiedAgent`, `SupervisorAgent` und `EnvironmentReactiveAgent` nutzen `agent`; Zonen nutzen `zone`; Signale nutzen `signal`; `VirtualSceneContext` nutzt `stateObject`; `SceneStateController` bleibt untypisiert. | bestanden |
| B | `VivianAssistant` nutzt `agent`; `CoffeeMachine` und `Cup` nutzen `asset`; `BrewingRequest` nutzt `stateObject`. | bestanden |

### Effect.evidencedBy

`Effect.evidencedBy` ist eine Trace-Referenz auf `StateAssertion`, keine Komposition und kein Testorakel. Conditions duerfen fachlicher Kontext eines Effects sein, sind aber nicht Ziel der Evidence-Kante.

| Use Case | Befund | Ergebnis |
| --- | --- | --- |
| A | Alle 6 Effects sind auf konkrete StateAssertions wie `A-SA-S05-01`, `A-SA-S06-02` oder `A-EX-SA04` rueckgebunden. | bestanden |
| B | Alle 11 Effects besitzen mindestens einen StateAssertion-Bezug; zusaetzliche Conditions bleiben nur Kontext. | bestanden |

## Korrekturen in diesem Schritt

| Datei | Korrektur |
| --- | --- |
| `cardinality_table.md` | Ergebnis von 28 auf 30 Beziehungen aktualisiert; `Entity.kind` und `Effect.evidencedBy` ergaenzt. |
| `diagram_spec_alignment.md` | Abgleich von 28 auf 30 Beziehungen aktualisiert; v0.5-Beziehungen als `21a` und `24a` aufgenommen. |
| `use_case_A_cardinality_check.md` | A-Kardinalitaetscheck um `Entity.kind` und `Effect.evidencedBy` erweitert. |
| `use_case_B_cardinality_invariant_check.md` | B-Kardinalitaetscheck um `Entity.kind` und `Effect.evidencedBy` erweitert. |
| `use_case_A_effect_instances.md` | Alter Satz entfernt, der die nun vorhandene Evidence-Kante verneinte. |
| Historische Gap- und Klassifikationsdateien | Vor-v0.5-Formulierungen zu fehlendem `Entity.kind` oder fehlender `Effect -> StateAssertion`-Kante als historisch markiert beziehungsweise auf den aktuellen v0.5-Stand gebracht. |

## Schlussbefund

Es bleibt keine offene Kardinalitaetsverletzung. Optionale Beziehungen sind nur dort leer, wo `0..*` oder `0..1` dies ausdruecklich erlaubt. Pflichtbeziehungen wie `UseCase -> Scenario [1..*]`, `Scenario -> ScenarioStep [1..*]`, `CapabilityUse -> Capability [1]`, `Capability -> Effect [1..*]`, `RuntimeBinding -> RuntimeAction [1..*]` und `ValidationCase.expectedOutcome [1..*]` sind in beiden Anwendungsfaellen erfuellt.

Task 14.4 kann auf diesem Befund aufbauen und die professoren-taugliche Argumentation pruefen, insbesondere die Begruendung von `Include`, `Extend`, `ExtensionPoint`, `Satisfy`, `ScenarioStep`, `CapabilityUse` und `RuntimeBinding`.
