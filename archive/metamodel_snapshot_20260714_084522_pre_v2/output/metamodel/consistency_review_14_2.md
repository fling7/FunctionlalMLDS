# Fachliche Konsistenzpruefung 14.2

Stand: 2026-07-08

Task: 14.2 `Fachliche Konsistenz pruefen`

Ziel: Pruefen, ob die A/B-Artefakte und die finale v0.5-Spezifikation die zentralen Trennlinien des Metamodells einhalten.

## Pruefumfang

Geprueft wurden insbesondere:

- `dynamic_functional_mlds_specification.md`
- `dynamic_functional_mlds_metamodel.mmd`
- `written_elaboration_de.md`
- A-Artefakte zu Actor, Entity/Agent, Capability, RuntimeAction und ValidationCase
- B-Artefakte zu Visitor/Vivian, Kaffeemaschine, Capability, RuntimeAction und ValidationCase
- kritischer Subagent-Review durch `Aristotle`

## Prueffragen

| Nr. | Frage | Ergebnis |
| --- | --- | --- |
| 1 | Wird `Actor` als externe Use-Case-Rolle und `Agent` als ausfuehrende/beobachtete Entity getrennt? | bestanden |
| 2 | Wird Vivian in der B-Baseline nicht als primaerer Actor modelliert? | bestanden |
| 3 | Wird `ScenarioStep.performedBy` nur fuer `actorIntent`-Schritte genutzt? | bestanden |
| 4 | Bleiben Capabilities fachlich und frei von Endpoints, Topics, Tools und Schemas? | bestanden |
| 5 | Liegen technische Aktionen nur unter `RuntimeBinding -> RuntimeAction`? | bestanden |
| 6 | Gibt es keine direkte `ScenarioStep -> RuntimeAction`-Kante? | bestanden |
| 7 | Werden ValidationCases als pruefende Artefakte modelliert, ohne RuntimeActions oder Scenarios zu besitzen? | bestanden nach Korrektur |
| 8 | Nutzen gesetzte `Entity.kind`-Werte nur die v0.5-Enumeration `agent`, `asset`, `zone`, `signal`, `stateObject`? | bestanden nach Korrektur |

## Befund 1: Actor und Agent

Die Trennung ist fachlich konsistent.

| Bereich | Bewertung |
| --- | --- |
| A | `ScenarioDesigner`, `SceneParticipant` und `SceneObserver` bleiben Actor-Rollen. Agenten und Szenenobjekte liegen auf Entity-/Agent-Ebene. |
| B | `ACT-B-01 Visitor` ist die externe Rolle. `ENT-B-01 VivianAssistant` ist Agent/Entity mit `Entity.kind = agent`. `ENT-B-02 CoffeeMachine` ist Entity/Asset. |
| performedBy | Vivian-, System- und Objektreaktionen erhalten kein `performedBy`; nur Visitor-`actorIntent`-Schritte nutzen `performedBy = ACT-B-01 Visitor`. |

Keine Vermischung gefunden.

## Befund 2: Capability und RuntimeAction

Die fachliche/technische Trennung ist konsistent.

| Ebene | Zulaessiger Inhalt | Ergebnis |
| --- | --- | --- |
| `ScenarioStep` | fachliche Handlung, Beobachtung oder Systemreaktion | keine direkte RuntimeAction-Kante |
| `CapabilityUse` | Nutzung genau einer fachlichen Capability | keine RuntimeAction-Referenz |
| `Capability` | Intent, Preconditions, Effects | keine Endpoints, Topics, Tools oder Schemas |
| `RuntimeBinding` | technische Bindung genau einer Capability | besitzt RuntimeActions |
| `RuntimeAction` | Endpoints, Topics, Tools, Input-/Output-Schemas | technische Details liegen hier |

Der erlaubte Pfad bleibt:

`ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

## Befund 3: Scenario und ValidationCase

Der kritische Review fand ein echtes Konsistenzrisiko: In `use_case_B_validation_case_instances.md` standen in der Spalte `validates` teils Scenario-IDs wie `SC-B-01-MAIN`, obwohl die Metamodellkante `ValidationCase -> UseCase : validates` zeigt.

Korrektur:

- `ValidationCase.validates` referenziert nun durchgaengig `UC-B-01`.
- Der konkrete Scenario-Kontext bleibt im Stimulus und ExpectedOutcome erhalten.
- Eine direkte `ValidationCase -> Scenario`-Kante wird nicht eingefuehrt.

Damit bleibt `Scenario` der Ablaufcontainer und `ValidationCase` ein pruefendes Artefakt.

## Befund 4: Entity.kind

Der kritische Review fand alte Begleittexte mit frueheren EntityKind-Werten wie `user`, `system` und `environment`. Diese Werte sind fuer `Event.kind` weiterhin zulaessig, aber nicht fuer `Entity.kind` in v0.5.

Korrektur:

| Datei | Korrektur |
| --- | --- |
| `use_case_A_entities_agents.md` | EntityKind-Werte auf `agent`, `asset`, `zone`, `signal`, `stateObject` harmonisiert; unpassender Fall bleibt untypisiert. |
| `use_case_A_state_assertion_instances.md` | StateAssertion-Subjekte auf v0.5-EntityKinds harmonisiert. |
| `use_case_A_scene_objects.md` | Szenenobjekt-EntityKinds auf v0.5 harmonisiert. |
| `use_case_B_actor_agent_mapping.md` | Vivian von `system` auf `agent` gesetzt. |
| `use_case_B_event_condition_state_assertion_instances.md` | Vivian auf `agent`, BrewingRequest auf `stateObject` gesetzt. |
| `metamodel_element_notes.md` | Entity-Definition an v0.5 angepasst. |
| `example_scenarios_tasklist.md` | alte Abnahmeregel fuer Task 2.4 an v0.5 angepasst. |

`Event.kind = user|environment|signal` wurde bewusst nicht geaendert, weil das eine andere Typisierungsebene ist.

## Verifikation

| Check | Ergebnis |
| --- | --- |
| Suche nach alten EntityKind-Altwerten | keine problematischen Treffer |
| Suche nach gemischter Validates-Formulierung fuer UseCase und Scenario | korrigiert |
| Suche nach B-ValidationCases mit Scenario-ID in der `validates`-Spalte | keine problematischen Treffer |
| Suche nach direkter `ScenarioStep -> RuntimeAction`-Kopplung | keine problematischen Treffer; verbleibende Treffer sind Negativregeln oder Stimulusbeschreibungen |
| ASCII-Pruefung der geaenderten Dateien | bestanden |

## Ergebnis

Task 14.2 ist erfuellt. Nach Korrektur der beiden Reviewfunde gibt es keine fachliche Vermischung von:

- Actor und Agent,
- fachlicher Capability und technischer RuntimeAction,
- Scenario und ValidationCase.

Offenes Restrisiko: Einige aeltere Arbeitsnotizen enthalten noch historische Kontextformulierungen. Sie sind nicht normativ, solange die finale Spezifikation, die Mapping-Artefakte und die Taskliste v0.5 als gueltige Linie fuehren.
