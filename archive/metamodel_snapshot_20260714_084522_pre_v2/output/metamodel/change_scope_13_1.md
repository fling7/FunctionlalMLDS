# Aenderungsumfang 13.1

Datum: 2026-07-08
Task: 13.1 `Aenderungsumfang bestaetigen`

## Zweck

Diese Datei legt den Aenderungsumfang fuer die naechsten Arbeitsschritte 13.2 bis 13.8 fest. Sie verhindert, dass der kompakte Kern durch die Beispielanalyse unkontrolliert vergroessert wird.

Grundlage sind die Abschnitte `Modellentscheidung` und `Finaler Beispieltrace` in `written_elaboration_de.md`.

## Ergebnis

Diagramm, Generator und generierte Spezifikation sollen angepasst werden. Der Aenderungsumfang ist aber eng begrenzt:

1. Zwei minimale Kernanpassungen werden in Generator, Diagramm, Mermaid und Spezifikation uebernommen.
2. Optionale Ergaenzungsmodule werden nur textlich als nicht zum Kern gehoerende Andockpunkte beschrieben.
3. Bestehende A/B-Beispielinstanzen bleiben strukturell gueltig und muessen fuer diesen Schritt nicht neu modelliert werden.
4. Das bestehende Archiv bleibt unveraendert; ein neuer Snapshot wird erst in Task 13.8 erzeugt.

## Freigegebene Kernanpassungen

| Nr. | Aenderung | Zielartefakte | Modellwirkung |
| --- | --- | --- | --- |
| `KERN-01` | `Entity.kind: EntityKind [0..1]` | Generator, SVG, PNG, Mermaid, Spezifikation | Optionale grobe Typisierung identifizierbarer Entities. Fehlende Werte bleiben gueltig. |
| `KERN-01a` | Enumeration `EntityKind = agent, asset, zone, signal, stateObject` | Generator, SVG, PNG, Mermaid, Spezifikation | Definiert eine kleine stabile Wertemenge ohne domaenenspezifische Spezialtypen. |
| `KERN-02` | `Effect.evidencedBy -> StateAssertion [0..*]` | Generator, SVG, PNG, Mermaid, Spezifikation | Optionale nicht-kompositive Trace-Referenz von fachlicher Wirkung zu beobachtbarer Zustandsaussage. |

## Nicht freigegebene Kernvergroesserungen

Die folgenden Konzepte werden nicht als Kernklassen oder Kernbeziehungen in das Diagramm aufgenommen:

| Konzept | Entscheidung | Grund |
| --- | --- | --- |
| `InteractionObject`, `ControlSurface`, `Affordance`, `InteractionZone` | nicht in den Kern | Gehoert in ein optionales `InteractionObjectModule`. |
| `GuidanceContent`, `DialogueAct`, Antwortoptionen, Turn-Taking | nicht in den Kern | Gehoert in ein optionales `AssistantInteractionModule`. |
| formale Zustandsautomaten, StateDimensions, Transitionen | nicht in den Kern | Gehoert in ein optionales `StateTransitionModule`. |
| Runtime-Reihenfolge, Dependency-Kanten, Retry- oder Fehlerpolitik | nicht in den Kern | Gehoert in ein optionales `RuntimeExecutionModule`. |
| SafetyCase oder SafetyArgument | nicht in den Kern | Aktuell reichen Condition, StateAssertion und ValidationCase. |
| direkte `ScenarioStep -> RuntimeAction`-Kante | ausdruecklich verboten | Fachliche Absicht und technische Ausfuehrung muessen getrennt bleiben. |

## Zielartefakte pro Folgeaufgabe

| Folgeaufgabe | Ziel | Umfang |
| --- | --- | --- |
| 13.2 Generator aktualisieren | `tools/generate_dynamic_functional_mlds.py` | Nur KERN-01, KERN-01a und KERN-02 einbauen; keine neuen Modulklassen. |
| 13.3 Diagramm neu erzeugen | `dynamic_functional_mlds_metamodel.svg`, `.png`, `.mmd` | Diagramm muss neue Typisierung und Evidence-Kante sichtbar zeigen. |
| 13.4 Kantenkreuzungen pruefen | Kreuzungsreport | Neue Evidence-Kante darf bestehende Lesbarkeit nicht verschlechtern. |
| 13.5 Label-Overlaps pruefen | Overlap-Report | Labels der neuen Kante und Enumeration muessen lesbar bleiben. |
| 13.6 Diagramm visuell pruefen | Sichtpruefung | Keine abgeschnittenen Labels, keine unklare Zuordnung. |
| 13.7 Spezifikation aktualisieren | `dynamic_functional_mlds_specification.md` plus ggf. Begleittext | Kardinalitaeten, Invarianten und Kompatibilitaet der beiden Kernanpassungen beschreiben. |
| 13.8 Neuen Stand archivieren | neuer timestamped Snapshot | Alter Snapshot bleibt unveraendert. |

## Kardinalitaeten und Semantik

| Element | Kardinalitaet | Semantik |
| --- | --- | --- |
| `Entity.kind` | `[0..1]` | Eine Entity kann genau eine grobe Art besitzen, muss aber keine besitzen. |
| `EntityKind` | Enumeration | Werte sind stabil und bewusst grob. Keine Werte wie `coffeeMachine`, `startButton`, `ttsVoice` oder `unityController`. |
| `Effect.evidencedBy` | `[0..*]` | Ein Effect kann durch beliebig viele StateAssertions beobachtbar gemacht werden. |
| inverse Sicht `StateAssertion` zu `Effect` | nicht exklusiv | Eine StateAssertion darf von mehreren Effects oder ValidationCases genutzt werden. |
| Besitzsemantik | keine Komposition | Ein Effect besitzt die StateAssertion nicht. |

## Beizubehaltende Invarianten

| Invariante | Status nach Aenderung |
| --- | --- |
| Genau ein Main Scenario pro UseCase | unveraendert. |
| Include bleibt verpflichtend, Extend bleibt optional/bedingt | unveraendert. |
| `Satisfy` referenziert Requirement oder UseCase, nicht beides | unveraendert. |
| Keine direkte `ScenarioStep -> RuntimeAction`-Kante | unveraendert und weiter ausdruecklich verboten. |
| Actor/Agent-Trennung | unveraendert; `Entity.kind` ersetzt keinen Actor. |
| Capability bleibt fachlich | unveraendert; technische Details bleiben in `RuntimeBinding` und `RuntimeAction`. |

## Abnahme 13.1

| Kriterium | Erfuellung |
| --- | --- |
| Liste der freigegebenen Modellaenderungen vorhanden | KERN-01, KERN-01a und KERN-02 sind explizit genannt. |
| Klar, ob nur Text oder auch Diagramm/Generator betroffen ist | Diagramm, Generator, Mermaid und generierte Spezifikation sind betroffen. |
| Nicht freigegebene Erweiterungen abgegrenzt | Optionale Module sind als Nicht-Kernumfang aufgefuehrt. |
| Keine Scope-Ausweitung auf direkte Runtime-Kopplung | Direkte `ScenarioStep -> RuntimeAction`-Kante bleibt verboten. |
| Archivverhalten geklaert | Bestehender Snapshot bleibt unveraendert; neuer Snapshot erst in 13.8. |
