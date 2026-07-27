# Abschlusspruefung 14.4: Professoren-taugliche Argumentation

Stand: 2026-07-08

Task: 14.4 `Professoren-taugliche Argumentation pruefen`

## Ergebnis

Die kritischen Begriffe `Include`, `Extend`, `ExtensionPoint`, `Satisfy`, `ScenarioStep`, `CapabilityUse` und `RuntimeBinding` koennen konsistent erklaert werden. Die zentrale Verteidigungslinie lautet:

Das Metamodell trennt drei Ebenen strikt:

1. Use-Case-Ebene: Anforderungen, Use Cases, Actors, Include, Extend, ExtensionPoint und Satisfy.
2. Scenario-Ebene: konkrete dynamische Ablaeufe mit Steps, Events, Conditions, StateAssertions, StepRelations und Varianten.
3. Functional/Runtime Bridge: fachliche Faehigkeitsnutzung ueber `CapabilityUse` und `Capability`, technische Realisierung erst ueber `RuntimeBinding` und `RuntimeAction`.

Dadurch wird verhindert, dass Varianten faelschlich als Use-Case-Erweiterungen, Requirements faelschlich als Szenarioschritte oder technische RuntimeActions faelschlich als fachliche ScenarioSteps modelliert werden.

## Normative Bezugspunkte

| Begriff | Belastbare Modellregel |
| --- | --- |
| `UseCase` | Beschreibt eine Nutzung des Systems und was das System leisten soll. |
| `Include` | Verpflichtende Wiederverwendung: Das Verhalten des inkludierten Use Case wird in den inkludierenden Use Case eingefuegt. |
| `Extend` | Bedingte oder optionale Ergaenzung eines eigenstaendig sinnvollen Basis-Use-Case. |
| `ExtensionPoint` | Gehoert zum erweiterten Use Case und markiert die Stelle, an der ein `Extend` andocken darf. |
| `Satisfy` | Trace-Beziehung von erfuellenden Elementen zu Requirement oder UseCase; im Modell gilt die XOR-Regel: eine Satisfy-Instanz referenziert nicht beides gleichzeitig. |
| `ScenarioStep` | Fachlicher Schritt innerhalb eines konkreten Scenario, keine technische Aktion und kein eigener Use Case. |
| `CapabilityUse` | Kontextuelle Nutzung einer fachlichen Capability durch einen ScenarioStep. |
| `RuntimeBinding` | Technische Bindung einer fachlichen Capability an konkrete RuntimeActions; technische Details beginnen hier, nicht im ScenarioStep. |

Quelle fuer die EAST-ADL-nahe Semantik ist die EAST-ADL Domain Model Specification V2.1.12, insbesondere Requirements, UseCases und VerificationValidation:

- https://east-adl.info/Specification/V2.1.12/EAST-ADL-Specification_V2.1.12.pdf

## Kernargument in einem Satz

Ein `ScenarioStep` beschreibt, was im fachlichen Ablauf passiert; eine `Capability` beschreibt, welche fachliche Faehigkeit dafuer benoetigt wird; eine `RuntimeBinding` beschreibt erst danach, wie diese Faehigkeit technisch ausgefuehrt wird.

## Erwartbare Rueckfragen und belastbare Antworten

| Kritische Frage | Kurze Antwort | Begruendung / Verteidigung |
| --- | --- | --- |
| Warum sind Alternative und Exception nicht als `Extend` modelliert? | Weil sie in A und B Ablaufvarianten innerhalb desselben Use Case sind, keine eigenstaendigen Erweiterungs-Use-Cases. | `Scenario.kind = alternative|exception` und `StepRelation.kind` reichen fuer lokale Varianten. Ein `Extend` waere erst korrekt, wenn ein separater erweiternder Use Case existiert und am Basis-Use-Case ein passender ExtensionPoint definiert ist. |
| Wann waere `Include` korrekt? | Nur bei verpflichtendem, wiederverwendbarem Use-Case-Verhalten. | Beispiel B: Eine eigenstaendige `UC-B-02 Kaffeemaschinenbereitschaft pruefen` waere ein gueltiger Include-Kandidat, wenn sie als eigener Use Case mit Main Scenario ausgearbeitet wird. Solange die Readiness-Pruefung nur ein Schritt plus Capability in `UC-B-01` ist, wird kein unfertiger Include erzeugt. |
| Wann waere `Extend` korrekt? | Bei optionalem oder bedingtem Zusatzverhalten, das den Basis-Use-Case nicht erst vollstaendig macht. | Beispiel B: Eine optionale Trainings-Erklaerung durch Vivian waere ein Extend-Kandidat, wenn `UC-B-01` auch ohne diese Erklaerung sinnvoll bleibt und ein `ExtensionPoint` wie `AfterStartCommand` existiert. |
| Warum braucht `Extend` einen `ExtensionPoint`? | Weil der erweiternde Use Case nicht beliebig irgendwo in den Basisablauf eingreifen darf. | Der `ExtensionPoint` gehoert zum erweiterten Use Case und macht die Andockstelle explizit. Ohne ihn waere unklar, welche Stelle im Basisverhalten erweitert wird. |
| Wo liegen die ExtensionPoints, wenn A und B kein formales `Extend` instanziieren? | Formal duerfen dann 0 ExtensionPoints existieren. | Die in B genannten ExtensionPoints sind Kandidaten fuer eine spaetere Extend-Schicht, keine bereits instanziierten Pflichtelemente. Ein ExtensionPoint gehoert zum erweiterten Use Case, nicht zum ScenarioStep. |
| Warum erbt `ScenarioStep` nicht von `RedefinableElement`? | Weil Erweiterbarkeit auf Use-Case-Ebene ueber `ExtensionPoint` modelliert wird, nicht durch beliebige Erweiterbarkeit jedes Steps. | Das Modell bleibt kompakt und EAST-ADL-nah. ScenarioSteps koennen ueber `StepRelation`, Events, Conditions und Scenarios variiert werden; Use-Case-Erweiterung bleibt `Extend + ExtensionPoint`. |
| Warum darf eine `Satisfy`-Instanz nicht Requirement und UseCase zugleich referenzieren? | Damit die Bedeutung der Trace-Beziehung eindeutig bleibt. | Wenn dasselbe Element sowohl ein Requirement als auch einen UseCase erfuellt, werden zwei Satisfy-Instanzen angelegt. So bleibt die EAST-ADL-nahe XOR-Regel pruefbar. |
| Ist es ein Problem, dass B noch keine formalen Satisfy-Instanzen hat? | Nein fuer Kardinalitaet und Modellkorrektheit; ja als moeglicher spaeterer Traceability-Ausbau. | `Satisfy` ist optional. B weist Requirements derzeit ueber ValidationCases und Artefakt-Trace nach. Fuer eine finale Requirements-Traceability-Tabelle koennen formale B-Satisfy-Instanzen ergaenzt werden, ohne das Metamodell zu aendern. |
| Bedeutet eine Kette wie `B-REQ-011 -> UC-B-01`, dass eine formale B-Satisfy-Kante existiert? | Nein, solange keine B-Satisfy-Instanz angelegt ist. | In der B-Ausarbeitung ist diese Kette argumentativer Trace. Eine formale Umsetzung waere moeglich, muesste aber als eigene `Satisfy`-Instanz mit Requirement-Zweig modelliert werden und duerfte nicht gleichzeitig den UseCase-Zweig belegen. |
| Warum ist Vivian kein Actor? | Weil Vivian in der aktuellen Systemgrenze Teil der assistierten VR-Interaktion ist. | Der `Visitor` ist externe Rolle und damit Actor. Vivian ist ein `Agent`/`Entity` innerhalb des Systems; Vivian-Reaktionen sind `systemResponse`-Steps und laufen ueber CapabilityUse. |
| Warum wird die Kaffeemaschine nicht als Actor modelliert? | Weil sie keine externe Rolle mit eigener Use-Case-Absicht ist. | Die Kaffeemaschine ist eine fachliche Entity mit `Entity.kind = asset`; ihr Zustand wird ueber Conditions und StateAssertions beschrieben, ihr Verhalten ueber Capabilities und RuntimeBindings. |
| Warum ist `B-MAIN-G08` ein Guard vor dem Startschritt und nicht nur Capability-Precondition? | Weil der Guard entscheidet, ob der ScenarioStep fachlich betreten werden darf. | Capability-Preconditions beschreiben Voraussetzungen der Faehigkeit. Der Guard an der Ablaufkante beziehungsweise am Step ist die Freigabebedingung des konkreten Scenarios: Ohne Bestaetigung und Startfreigabe wird `B-MAIN-S15` nicht erreicht. |
| Warum gibt es `CapabilityUse`, wenn es schon `Capability` gibt? | Weil Nutzung und Faehigkeit verschiedene Ebenen sind. | `Capability` ist wiederverwendbare fachliche Faehigkeit. `CapabilityUse` ist die konkrete Nutzung dieser Faehigkeit in einem ScenarioStep, mit Kontext und Parametern. |
| Warum darf `ScenarioStep` nicht direkt auf `RuntimeAction` zeigen? | Weil dann fachliche Absicht und technische Ausfuehrung vermischt werden. | Der erlaubte Pfad ist `ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`. Dadurch bleibt die technische Bindung austauschbar und validierbar. |
| Warum enthaelt `Capability` keine Endpoints, Topics oder Toolnamen? | Weil eine Capability fachlich beschreibt, was geleistet wird, nicht wie es technisch umgesetzt wird. | Endpoints, Topics, Tools und Schemas gehoeren in `RuntimeAction` unter einer `RuntimeBinding`. Das verhindert Plattformkopplung auf Scenario-Ebene. |
| Warum hat `RuntimeBinding` eine eigene Klasse? | Weil eine fachliche Capability auf keiner, einer oder mehreren technischen Plattformen gebunden sein kann. | Eine RuntimeBinding referenziert genau eine Capability und besitzt mindestens eine RuntimeAction. Sie ordnet fachliche Faehigkeit und technische Aktionen kontrolliert zu, behauptet aber noch keine vollstaendige Orchestrierungslogik wie Reihenfolge, Retry oder Rollback. |
| Warum prueft ein `ValidationCase` RuntimeBindings, besitzt sie aber nicht? | Weil Validation ein pruefender Bezug ist, keine Komposition. | RuntimeBindings gehoeren zur technischen Realisierung einer Capability. ValidationCases formulieren Stimulus und ExpectedOutcome und duerfen Bindings ausfuehren oder pruefen, aber nicht strukturell besitzen. |
| Warum ist `Effect.evidencedBy` kein ValidationOutcome? | Weil es nur Traceability zwischen fachlicher Wirkung und beobachtbarer StateAssertion ausdrueckt. | `Effect.evidencedBy` ist optional und nicht-kompositiv. Testorakel, logische Operatoren oder formale Auswertung gehoeren in ein optionales Validation-Modul. |

## Beispiel A: dynamisches Agentenverhalten

Die Modellierung bleibt fachlich, obwohl spaeter RuntimeActions existieren.

| Ebene | Beispiel |
| --- | --- |
| Requirement | `A-REQ-006`: Der Agent soll eine ausfuehrende Rolle annehmen koennen. |
| UseCase | `UC-A-01`: Dynamisches Agentenverhalten in virtueller Szene modellieren. |
| ScenarioStep | `A-MAIN-S05`: System nimmt die ausfuehrende Rolle an. |
| CapabilityUse | `A-CU-001`: nutzt die fachliche Faehigkeit Rollenwechsel. |
| Capability | `A-CAP-ADOPT-EXECUTOR-ROLE`: beschreibt den fachlichen Rollenwechsel. |
| Effect | `A-EFF-ROLE-EXECUTOR`: Agent besitzt den Rollenzustand `executor`. |
| RuntimeBinding | `A-RB-ROLE-EXECUTOR-VR`: bindet die Capability an VR-RuntimeActions. |
| ValidationCase | `A-VC-002-ROLE-BINDING`: prueft Rollenwechsel und Binding. |

Verteidigung: Der Step ist keine technische Aktion. Die Runtime wird erst nach der Capability angebunden. Dadurch kann die fachliche Spezifikation bestehen bleiben, wenn die technische Plattform wechselt.

## Beispiel B: Vivian bedient mit dem Visitor eine Kaffeemaschine

Der kritische Pfad fuer den Bruehstart:

`B-MAIN-S15 -> B-CU-007 -> CAP-B-START-BREWING -> B-EFF-BREWING-START-ISSUED -> B-RB-COFFEE-START-BREWING -> RuntimeActions -> StateAssertions -> B-VC-005`

| Ebene | Warum korrekt? |
| --- | --- |
| `B-MAIN-S15` | beschreibt die fachliche Systemreaktion: Bruehstart wird nach Freigabe ausgeloest. |
| `B-MAIN-G08` | wirkt als Guard/Freigabebedingung vor dem Startschritt; ohne bestaetigte Freigabe darf der Step nicht betreten werden. |
| `B-CU-007` | verbindet diesen Step mit genau einer fachlichen Capability. |
| `CAP-B-START-BREWING` | beschreibt die erlaubte fachliche Leistung, nicht den Controlleraufruf. |
| `B-RB-COFFEE-START-BREWING` | ordnet die Capability dem Kaffeemaschinenadapter, der VR-Synchronisation und dem Trace zu. |
| RuntimeActions | enthalten erst hier technische Ausfuehrungsdetails. |
| ValidationCase | prueft, ob Start nur mit Freigabe erfolgt und die erwarteten StateAssertions eintreten. |

Verteidigung: Das Modell kann erklaeren, warum der Start erlaubt ist, bevor es beschreibt, wie der Start technisch ausgefuehrt wird.

## Typische Fallen und sichere Antwort

| Falle | Sichere Antwort |
| --- | --- |
| "Alternative = Extend" | Nein. Alternative ist nur dann Extend, wenn sie als separater erweiternder Use Case an einem ExtensionPoint modelliert ist. |
| "Pflichtschritt = Include" | Nein. Ein Pflichtschritt ist nicht automatisch ein Include. Include braucht einen eigenen inkludierten Use Case. |
| "Vivian handelt, also Actor" | Nein. Actor ist externe Rolle. Vivian ist bei der aktuellen Systemgrenze Agent/Entity im System. |
| "Kaffeemaschine startet, also RuntimeAction im Step" | Nein. Der Step bleibt fachlich; RuntimeAction liegt erst unter RuntimeBinding. |
| "Satisfy kann alles gleichzeitig traceen" | Nein. Eine Satisfy-Instanz bleibt semantisch eindeutig: Requirement-Zweig oder UseCase-Zweig. |
| "Effect beweist den Test" | Nein. Effect beschreibt versprochene Wirkung; ValidationCase prueft. `evidencedBy` ist nur Trace zu StateAssertions. |
| "RuntimeBinding ist nur technisches Beiwerk" | Nein. RuntimeBinding ist die kontrollierte Uebersetzungsstelle zwischen fachlicher Capability und technischer Aktion. |

## Ehrliche Grenzen

| Grenze | Warum akzeptabel? | Falls der Professor nachfragt |
| --- | --- | --- |
| B hat noch keine formalen Satisfy-Instanzen. | Kardinalitaetskonform, weil Satisfy optional ist; Requirements sind ueber ValidationCases und Artefakte nachvollziehbar. | Fuer finale Traceability koennen B-Satisfy-Instanzen nachgetragen werden, ohne Modellanpassung. |
| B-Traces in Fliesstexten koennen wie formale Satisfy-Kanten wirken. | Sie sind derzeit argumentativer Trace, solange keine konkrete `Satisfy`-Instanz angelegt ist. | In der Verteidigung klar sagen: formal nachtragbar, aber dann mit XOR-konformen getrennten Satisfy-Instanzen. |
| Readiness-Pruefung ist kein formales Include. | Aktuell als ScenarioStep plus Capability modelliert; ein Include waere erst mit eigenem Use Case sauber. | `UC-B-02 Kaffeemaschinenbereitschaft pruefen` ist ein gueltiger spaeterer Include-Kandidat. |
| Interaktionsobjekt-Details der Kaffeemaschine sind nicht im Kern. | Kern bleibt kompakt; `Entity.kind = asset` reicht fuer die Baseline. | Bedienpunkte und Affordances gehoeren in ein optionales InteractionObject-Modul. |
| RuntimeAction-Reihenfolge ist nicht formalisiert. | Fuer Traceability reicht RuntimeBinding mit mehreren RuntimeActions; Reihenfolge ist derzeit dokumentarisch. | Ausfuehrbare Orchestrierung gehoert in ein RuntimeExecution-Modul. |
| ValidationOutcome ist nicht als eigene Logik modelliert. | ValidationCase hat Stimulus und ExpectedOutcome; komplexe Testlogik ist bewusst kein Kern. | Formale Testorakel gehoeren in ein optionales Validation-Modul. |

## Abnahmebefund

| Begriff | Kann sauber erklaert werden? | Befund |
| --- | --- | --- |
| `Include` | ja | Pflicht-Reuse auf Use-Case-Ebene; in A/B bewusst nicht formal instanziiert. |
| `Extend` | ja | Optionales Zusatzverhalten mit ExtensionPoint; A/B nutzen stattdessen Scenarios fuer lokale Varianten. |
| `ExtensionPoint` | ja | Gehoert zum erweiterten Use Case; nicht jeder ScenarioStep ist ein ExtensionPoint. |
| `Satisfy` | ja | Eindeutiger Requirement- oder UseCase-Trace; XOR-Regel bleibt pruefbar. |
| `ScenarioStep` | ja | Fachlicher Ablaufbaustein, keine technische Aktion. |
| `CapabilityUse` | ja | Kontextuelle Nutzung einer fachlichen Capability durch einen Step. |
| `RuntimeBinding` | ja | Technische Bindung einer Capability an RuntimeActions; keine direkte Step-Kopplung. |

Der kritische Subagent-Review zu 14.4 wurde integriert. Er hat besonders die B-Satisfy-Traceability, die ExtensionPoint-Kandidaten und die Guard-vs-Precondition-Abgrenzung geprueft.

Task 14.5 kann auf dieser Argumentation aufbauen und die finale Artefaktliste erzeugen.
