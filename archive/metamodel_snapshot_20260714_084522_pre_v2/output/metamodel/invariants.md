# Invarianten und Modellregeln des aktuellen Metamodells

Stand: 2026-07-07

Task: 1.4 `Bestehende Invarianten extrahieren`

Quellen:

- Spezifikation: `output/metamodel/dynamic_functional_mlds_specification.md`
- Kardinalitaetstabelle: `output/metamodel/cardinality_table.md`
- Elementnotizen: `output/metamodel/metamodel_element_notes.md`

## Ergebnis

Die bestehenden Modellregeln sind extrahiert und jeweils kurz begruendet. Die Regeln sind in zwei Gruppen getrennt:

1. explizite Invarianten aus der Spezifikation,
2. abgeleitete Konsistenzregeln aus Kardinalitaeten, Besitzsemantik und Diagrammstruktur.

Diese Trennung ist wichtig: Explizite Invarianten sind normative Regeln des Modells. Abgeleitete Konsistenzregeln sind keine neuen Klassen oder neuen Beziehungen, sondern Konsequenzen aus dem aktuellen Modellstand.

## A. Explizite Invarianten aus der Spezifikation

| Nr. | Regel | Begruendung | Relevanz fuer spaetere Beispiele |
| ---: | --- | --- | --- |
| E1 | Pro `UseCase` muss genau ein `Scenario.kind = main` existieren. Alternative und Exception-Szenarien duerfen zusaetzlich existieren. | Ein UseCase braucht einen eindeutigen Normalablauf, damit alternative und fehlerhafte Ablaeufe eindeutig relativ dazu eingeordnet werden koennen. | Bei Agentenszenen und Vivian/Kaffeemaschine darf es nicht mehrere konkurrierende Hauptablaeufe fuer denselben UseCase geben. |
| E2 | `Include` beschreibt verpflichtende Wiederverwendung. Optionales oder bedingtes Zusatzverhalten ist kein Include, sondern ein `Extend` oder eine `StepRelation.kind = alternative|exception`. | EAST-ADL unterscheidet verpflichtend eingefuegtes Verhalten von optionaler Erweiterung. Eine Vermischung wuerde UseCase-Semantik und Validierung verfaelschen. | Bereitschaftspruefung einer Kaffeemaschine kann Include sein; optionale Vivian-Erklaerung waere eher Extend oder Alternative. |
| E3 | Ein `Extend.extensionLocation` muss auf `ExtensionPoint`-Elemente zeigen, die zum `extendedCase` gehoeren. | Eine Erweiterung darf nur an definierten Stellen des erweiterten Basis-UseCase einsetzen. Sonst waere unklar, wo Verhalten eingefuegt wird. | Bei optionaler Hilfestellung muss der Einstiegspunkt, z. B. nach Startkommando, explizit zum erweiterten UseCase gehoeren. |
| E4 | Eine `Satisfy`-Instanz referenziert entweder `Requirement` oder `UseCase`, nicht beides gleichzeitig. | Die XOR-Regel verhindert mehrdeutige Traceability. Eine Beziehung soll klar sagen, welche Spezifikation erfuellt wird. | Fuer spaetere Trace-Ketten muss eindeutig sein, ob eine Capability ein Requirement oder einen UseCase erfuellt. |
| E5 | `ScenarioStep` darf keine direkte Referenz auf `RuntimeAction`, API-Endpunkte, Tools oder Message Topics besitzen. | Szenarioschritte bleiben fachlich. Technische Bindung erfolgt erst ueber `CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`. | Verhindert, dass Vivian- oder VR-Schritte direkt mit Controller-Aufrufen vermischt werden. |
| E6 | `Capability` enthaelt keine technischen Endpoint- oder Tool-Daten. Technische Details liegen ausschliesslich in `RuntimeBinding` und `RuntimeAction`. | Capabilities beschreiben fachliche Faehigkeiten; technische Plattformdetails muessen austauschbar bleiben. | Eine Capability wie `StartBrewing` darf keine Unity-Methode oder API-Adresse enthalten. |
| E7 | Alle `ScenarioStep`-Elemente einer `ParallelGroup` muessen zum selben `Scenario` gehoeren. | Parallelitaet gruppiert Schritte innerhalb eines konkreten Ablaufs. Schritte aus verschiedenen Scenarios zu mischen wuerde Ablaufsemantik zerstoeren. | Bei parallelen Agentenhandlungen muessen alle parallelisierten Schritte im selben Szenario liegen. |
| E8 | Wenn `ScenarioStep.kind = actorIntent`, dann sollte `performedBy` auf einen `Actor` zeigen. Bei Systemantworten wird die ausfuehrende Logik ueber `CapabilityUse` und `Capability` modelliert. | ActorIntent beschreibt eine Absicht einer externen Rolle. Systemreaktionen sind dagegen fachliche Faehigkeitsnutzungen und nicht Actor-Handlungen. | Vivian muss sauber als Rolle oder Agent eingeordnet werden; Benutzerhandlungen duerfen nicht mit Systemantworten vermischt werden. |

## B. Abgeleitete Konsistenzregeln aus Kardinalitaeten und Diagrammstruktur

| Nr. | Regel | Herleitung | Begruendung | Relevanz fuer spaetere Beispiele |
| ---: | --- | --- | --- | --- |
| A1 | Ein `RequirementsModel` kann null bis beliebig viele `Requirement` und `UseCase` enthalten. | `RequirementsModel -> Requirement [0..*]`, `RequirementsModel -> UseCase [0..*]` | Der Kontext ist ein Container, erzwingt aber keine Mindestanzahl in jedem Zwischenstand. | Fruehe Beispielentwuerfe koennen erst UseCases oder erst Requirements erfassen. |
| A2 | Ein `UseCase` kann null bis beliebig viele `ExtensionPoint`, `Include` und `Extend` besitzen. | `UseCase -> ExtensionPoint [0..*]`, `UseCase -> Include [0..*]`, `UseCase -> Extend [0..*]` | Nicht jeder UseCase braucht Wiederverwendung oder Erweiterung. | Ein einfacher Agenten-UseCase muss keine ExtensionPoints haben; Kaffeemaschine kann sie haben. |
| A3 | Ein dynamisch ausfuehrbarer `UseCase` besitzt mindestens ein `Scenario`. | `UseCase -> Scenario [1..*]` | Ohne Szenario waere der UseCase nicht dynamisch operationalisiert. | Beide Anwendungsfaelle muessen mindestens ein Main-Scenario bekommen. |
| A4 | Ein `Scenario` besitzt mindestens einen geordneten `ScenarioStep`. | `Scenario -> ScenarioStep [1..*] ordered composition` | Ein Szenario ohne Schritte hat keine auswertbare Ablaufsemantik. | Jeder Beispielablauf muss in mindestens einen Schritt zerlegt werden. |
| A5 | `ScenarioStep` gehoert genau zu seinem `Scenario`; `ParallelGroup` besitzt Schritte nicht. | Komposition `Scenario -> ScenarioStep`, Referenz `ParallelGroup -> ScenarioStep` | Besitz und Referenz werden getrennt, damit ein Schritt nicht durch Parallelgruppen doppelt besessen wird. | Parallelitaet in Agentenszenen referenziert Schritte, statt sie aus dem Scenario herauszuloesen. |
| A6 | Eine `StepRelation` hat genau einen Quellschritt und genau einen Zielschritt. | `source step [1]`, `target step [1]` | Ablaufkanten muessen eindeutig gerichtet sein, sonst sind Sequenzen, Alternativen und Exceptions nicht pruefbar. | Haupt-, Alternativ- und Fehlerpfade brauchen klare Start- und Zielschritte. |
| A7 | Eine `ParallelGroup` referenziert mindestens zwei `ScenarioStep`-Elemente. | `member steps [2..*]` | Parallelitaet mit nur einem Schritt waere semantisch leer. | Parallele Agentenhandlungen duerfen erst modelliert werden, wenn mindestens zwei Schritte beteiligt sind. |
| A8 | Ein `ScenarioStep` kann null bis beliebig viele `Event`-Ausloeser haben. | `ScenarioStep -> Event [0..*]` | Nicht jeder Schritt muss explizit eventgetrieben sein; mehrere Ausloeser koennen moeglich sein. | Vivian- und Objektinteraktionen koennen User-, Signal- oder Environment-Events kombinieren. |
| A9 | Ein `ScenarioStep` kann hoechstens eine direkte Guard-Condition besitzen. | `ScenarioStep -> Condition [0..1]` | Die sichtbare Guard-Rolle bleibt eindeutig. Weitere Vor-/Nachbedingungen liegen auf Scenario- oder Capability-Ebene. | Bei Kaffeemaschine sollte z. B. `machine.ready = true` nicht doppelt als mehrere konkurrierende Guards modelliert werden. |
| A10 | Ein `ScenarioStep` kann beliebig viele resultierende `StateAssertion`-Elemente besitzen. | `ScenarioStep -> StateAssertion [0..*]` | Ein Schritt kann mehrere beobachtbare Zustandsfolgen haben. | Ein Schritt kann zugleich Maschinenzustand, Vivian-Feedback und UI-Anzeige setzen. |
| A11 | Ein `ScenarioStep` kann null bis beliebig viele `CapabilityUse`-Elemente enthalten. | `ScenarioStep -> CapabilityUse [0..*]` | Nicht jeder Schritt loest Systemfaehigkeiten aus; systemische Schritte koennen mehrere fachliche Faehigkeiten brauchen. | Beobachtungsschritte koennen ohne CapabilityUse auskommen, Systemreaktionen brauchen meist eine. |
| A12 | Jede `CapabilityUse` referenziert genau eine `Capability`. | `CapabilityUse -> Capability [1]` | Eine Nutzung muss eindeutig auf eine fachliche Faehigkeit zeigen. | Ein Schritt wie "Vivian startet Bruehvorgang" darf die benoetigte Capability nicht offenlassen. |
| A13 | Jede `Capability` besitzt mindestens einen `Effect`. | `Capability -> Effect [1..*]` | Eine fachliche Faehigkeit muss beobachtbar machen, was sie verspricht. | Capabilities fuer Agentenbewegung oder Kaffeemaschine muessen einen pruefbaren Effekt haben. |
| A14 | Eine `Capability` kann null bis beliebig viele `RuntimeBinding`-Elemente besitzen. | `Capability -> RuntimeBinding [0..*]` | Fachliche Faehigkeiten duerfen modelliert werden, bevor eine technische Plattformbindung existiert. | In fruehen Beispielen kann fachliche Funktion schon beschrieben werden, auch wenn WebXR/Unity-Binding spaeter folgt. |
| A15 | Jede `RuntimeBinding` gehoert genau zu einer `Capability` und enthaelt mindestens eine `RuntimeAction`. | `RuntimeBinding.capability [1]`, `RuntimeBinding -> RuntimeAction [1..*]` | Eine technische Bindung ohne fachliche Capability oder ohne technische Aktion waere nicht ausfuehrbar. | Vivian- oder Kaffeemaschinen-Bindings muessen konkret ausfuehrbar gemacht werden. |
| A16 | Eine `RuntimeAction` ist der Ort fuer technische Endpoints, Tools, Topics sowie Input- und Output-Schemas. | Attribute `endpoint | tool | topic`, `inputSchema [0..1]`, `outputSchema [0..1]` | Technische Details bleiben aus UseCase, ScenarioStep und Capability herausgezogen. | Controller-Aufrufe fuer Kaffeemaschine gehoeren hierhin, nicht in den ScenarioStep. |
| A17 | Ein `Agent` ist eine spezialisierte `Entity`, aber nicht automatisch ein `Actor`. | `Agent -> Entity` specialization; `Agent.playsActor [0..*]`; Actor/Agent-Trennung | Rolle und ausfuehrende Entitaet sind verschiedene Modellierungsebenen. | Vivian kann als Agent eine oder mehrere Actor-Rollen spielen; das muss explizit entschieden werden. |
| A18 | `Entity -> Capability [0..*]` beschreibt Bereitstellung, nicht zwingend Ausfuehrung in einem Schritt. | sichtbare Kante `provides capability [0..*]` | Eine Entity kann Faehigkeiten anbieten, die erst ueber CapabilityUse und RuntimeBinding verwendet werden. | Kaffeemaschine oder Vivian koennen Capabilities bereitstellen, ohne dass jeder Schritt sie nutzt. |
| A19 | `ValidationCase` muss mindestens ein erwartetes Ergebnis besitzen. | `ValidationCase.expectedOutcome [1..*]` | Ein Test ohne erwartetes Outcome ist nicht validierend. | Jeder Beispieltest muss mindestens eine StateAssertion oder erwartete Wirkung pruefen. |
| A20 | `ValidationCase -> RuntimeBinding [0..*]` ist pruefend/abhaengig, nicht besitzend. | sichtbare Dependency `checks runtime binding [0..*]` | Validierung darf technische Bindings pruefen, besitzt sie aber nicht. | Tests fuer Vivian oder Kaffeemaschine koennen mehrere Bindings pruefen, ohne diese zu definieren. |

## C. Prueffragen fuer spaetere Instanziierungen

Diese Fragen koennen bei den Beispielszenarien als schnelle Konsistenzkontrolle verwendet werden:

1. Hat jeder dynamisch relevante UseCase genau ein Main-Scenario?
2. Sind optionale Erklaerungen, Hilfen oder Trainingsablaeufe wirklich `Extend` oder Alternativen und nicht faelschlich `Include`?
3. Zeigt jedes `Extend` auf gueltige ExtensionPoints des erweiterten UseCase?
4. Erfuellt jede `Satisfy`-Instanz nur Requirement oder UseCase, nicht beides?
5. Gibt es irgendwo eine verbotene Direktkante von `ScenarioStep` zu `RuntimeAction` oder zu einem technischen Endpoint?
6. Enthalten Capabilities ausschliesslich fachliche Intents, Preconditions und Effects?
7. Liegen alle technischen Aktionen ausschliesslich in `RuntimeAction` unter `RuntimeBinding`?
8. Sind Actor und Agent sauber getrennt?
9. Referenziert jede ParallelGroup mindestens zwei Schritte desselben Scenario?
10. Hat jede Capability mindestens einen beobachtbaren Effect?
11. Hat jede RuntimeBinding genau eine fachliche Capability und mindestens eine technische RuntimeAction?
12. Hat jeder ValidationCase mindestens ein erwartetes Outcome?

## D. Konsequenz fuer den naechsten Task

Task 1.5 kann auf dieser Invariantenliste aufbauen und ein Glossar erstellen. Besonders wichtig sind dort die Begriffe `Actor`, `Agent`, `Entity`, `ScenarioStep`, `CapabilityUse`, `Capability`, `RuntimeBinding`, `RuntimeAction` und `ValidationCase`, weil sie in den Invarianten die zentralen Trennlinien des Modells bilden.
