# Rueckwaertskompatibilitaetspruefung 11.6

Stand: 2026-07-07

Task: 11.6 `Rueckwaertskompatibilitaet pruefen`

Zweck: Diese Pruefung stellt sicher, dass die in 11.4 spezifizierten minimalen Kernanpassungen und die in 11.5 spezifizierten optionalen Ergaenzungsmodule keine bestehende Instanz aus Anwendungsfall A oder B ungueltig machen.

Bezugsdateien:

- `minimal_core_adaptations.md`
- `extension_models_specification.md`
- `use_case_A_usecase_instance.md`
- `use_case_A_scenario_instances.md`
- `use_case_A_scenario_step_instances.md`
- `use_case_A_cardinality_check.md`
- `use_case_B_usecase_instance.md`
- `use_case_B_scenario_instances.md`
- `use_case_B_scenario_step_instances.md`
- `use_case_B_cardinality_invariant_check.md`

## Gesamtergebnis

Die Rueckwaertskompatibilitaet ist gegeben.

| Pruefbereich | Urteil | Begruendung |
| --- | --- | --- |
| Bestehende UseCases | gueltig | `UC-A-01` und `UC-B-01` behalten Text, Ziel, Actor-/Agent-Trennung und Scenario-Komposition. |
| Bestehende Scenarios | gueltig | Die sechs Scenarios behalten `Scenario.kind`, Owner-UseCase, geordnete Step-Membership und genau ein Main-Scenario je UseCase. |
| Bestehende ScenarioSteps | gueltig | Alle 42 Steps behalten `stepNumber`, `kind`, `performedBy`-Regel und fachlichen Text. Es wird keine neue Pflichtkante eingefuehrt. |
| Bestehende Entities und Agents | gueltig | `Entity.kind [0..1]` ist optional. Fehlende Typisierung macht keine Entity ungueltig. |
| Bestehende Effects | gueltig | `Effect.evidencedBy -> StateAssertion [0..*]` ist optional. Effects ohne Evidence-Link bleiben gueltig. |
| Bestehende StateAssertions | gueltig | StateAssertions werden nicht umbesessen und nicht exklusiv an Effects gebunden. |
| Bestehende RuntimeBindings und RuntimeActions | gueltig | Keine technische Beziehung wird verschoben oder neu verpflichtend. |
| Bestehende ValidationCases | gueltig | Formale Assertion-Logik bleibt optionales Modul und wird nicht fuer vorhandene ValidationCases verlangt. |
| Ergaenzungsmodule | gueltig optional | Kein Modul ist Pflicht fuer bestehende Kerninstanzen. |

## Gepruefter Bestand

| Bestand | A | B | Bewertung |
| --- | ---: | ---: | --- |
| UseCases | 1 | 1 | unveraendert gueltig |
| Scenarios | 3 | 3 | unveraendert gueltig |
| Main Scenarios je UseCase | 1 | 1 | unveraendert gueltig |
| ScenarioSteps | 14 | 28 | unveraendert gueltig |
| StepRelations | 14 | 28 formal | unveraendert gueltig |
| ParallelGroups | 0 | 0 | unveraendert gueltig, optional |
| StateAssertions | 28 | 30 | unveraendert gueltig |
| Capabilities | 3 | 11 | unveraendert gueltig |
| Effects | 6 | 11 | unveraendert gueltig |
| RuntimeBindings | 3 | 11 | unveraendert gueltig |
| RuntimeActions | 6 | 25 | unveraendert gueltig |
| ValidationCases | 8 | 10 | unveraendert gueltig |

## Wirkung der Kernanpassungen

### KERN-01: `Entity.kind [0..1]`

| Bestehendes Element | Wirkung | Kompatibilitaetsurteil |
| --- | --- | --- |
| Entity ohne `kind` | Keine Pflichtmigration. Das Attribut ist optional. | gueltig |
| Agent als Entity-Spezialisierung | Bleibt unveraendert. Optional kann `kind = agent` gesetzt werden. | gueltig |
| Objekt- oder Szenen-Entity | Bleibt unveraendert. Optional koennen grobe Werte wie `asset`, `zone`, `signal` oder `stateObject` gesetzt werden. | gueltig |
| Actor | Nicht betroffen. `Actor` bleibt externe Use-Case-Rolle und wird nicht durch `Entity.kind` ersetzt. | gueltig |

Moegliche optionale Nachpflege:

| Use Case | Kandidaten fuer optionale Typisierung |
| --- | --- |
| A | Agent-Entity als `agent`, Zielzone oder Szenenbereich als `zone`, Feedbacksignal als `signal`, beobachtbare Szenenzustaende als `stateObject`. |
| B | Vivian als `agent`, Kaffeemaschine und Tasse als `asset`, BrewingRequest als `stateObject`, Bedienzone als `zone`. |

Diese Nachpflege ist optional. Ohne Nachpflege bleiben alle Instanzen gueltig.

### KERN-02: `Effect.evidencedBy -> StateAssertion [0..*]`

| Bestehendes Element | Wirkung | Kompatibilitaetsurteil |
| --- | --- | --- |
| Effect ohne `evidencedBy` | Keine Pflichtmigration. Die neue Referenz ist `0..*`. | gueltig |
| StateAssertion ohne referenzierenden Effect | Bleibt eigenstaendig gueltig. Die inverse Sicht ist optional ableitbar. | gueltig |
| Capability mit bestehenden Effects | Bleibt unveraendert. `Capability -> Effect [1..*]` wird nicht geaendert. | gueltig |
| ValidationCase | Wird nicht ersetzt. `Effect.evidencedBy` ist Traceability, kein Testorakel. | gueltig |

Moegliche optionale Nachpflege:

| Use Case | Kandidaten fuer optionale Evidence-Links |
| --- | --- |
| A | Effects der Agentenreaktion koennen auf StateAssertions wie Zielzone erreicht, Rolle angenommen oder Rueckmeldung bestaetigt zeigen. |
| B | Effects der Vivian- und Kaffeemaschinen-Capabilities koennen auf StateAssertions wie `CoffeeMachineReady`, `BrewingStarted`, `BrewingFinished` oder `UserConsentAvailable` zeigen. |

Diese Links sind fachlich nuetzlich, aber nicht erforderlich.

## Wirkung der Ergaenzungsmodule

Alle Ergaenzungsmodule sind zuschaltbar. Kein bestehendes Kernartefakt muss Modulinstanzen besitzen.

| Modul | Bestehender Bestand betroffen? | Kompatibilitaetsurteil |
| --- | --- | --- |
| `InteractionObjectModule` | Nein. B kann Kaffeemaschine, Starttaste und Tassenbereich spaeter verfeinern. | gueltig optional |
| `AssistantInteractionModule` | Nein. B kann Vivian-Dialogakte spaeter verfeinern. | gueltig optional |
| `DecisionRuleModule` | Nein. B kann Bereitschaftspruefung spaeter als RuleSet ausdruecken. | gueltig optional |
| `StateTransitionModule` | Nein. A und B koennen lifecycleartige Zustaende spaeter formalisieren. | gueltig optional |
| `SpatialSemanticsModule` | Nein. A kann Raumbeziehungen spaeter strukturieren. | gueltig optional |
| `EventDetailModule` | Nein. A/B-Events bleiben mit `Event.expression` gueltig. | gueltig optional |
| `RuntimeExecutionModule` | Nein. Bestehende RuntimeBindings bleiben gueltig; technische Reihenfolge kann spaeter ergaenzt werden. | gueltig optional |
| `ValidationAssertionModule` | Nein. Bestehende ValidationCases bleiben gueltig; formale Orakel koennen spaeter ergaenzt werden. | gueltig optional |
| `RuntimeProfileModule` | Nein. RuntimeBinding und RuntimeAction bleiben gueltig; Profile koennen spaeter ergaenzt werden. | gueltig optional |

## Pruefung Anwendungsfall A

| Element | Bestand | Rueckwaertskompatibilitaet |
| --- | --- | --- |
| UseCase | `UC-A-01` | bleibt gueltig; keine neue UseCase-Pflichtbeziehung. |
| Scenarios | `A-MAIN-SC01`, `A-ALT-SC01`, `A-EX-SC01` | bleiben gueltig; genau ein Main-Scenario bleibt erhalten. |
| ScenarioSteps | 14 Steps | bleiben gueltig; keine neue Step-Pflichtkante, keine Runtime-Direktkopplung. |
| ScenarioStep.kind | `environmentObservation`, `systemResponse`, kein `actorIntent` | bleibt gueltig; `performedBy` bleibt leer, weil kein externer Actor handelt. |
| Capabilities und Effects | 3 Capabilities, 6 Effects | bleiben gueltig; Evidence-Links optional. |
| Runtime | 3 RuntimeBindings, 6 RuntimeActions | bleibt gueltig; RuntimeExecutionModule optional. |
| Validation | 8 ValidationCases | bleiben gueltig; ValidationAssertionModule optional. |

Keine A-Instanz wird ungueltig. A kann optional von `Entity.kind`, `Effect.evidencedBy`, `SpatialSemanticsModule` und `StateTransitionModule` profitieren.

## Pruefung Anwendungsfall B

| Element | Bestand | Rueckwaertskompatibilitaet |
| --- | --- | --- |
| UseCase | `UC-B-01` | bleibt gueltig; Visitor bleibt Actor, Vivian bleibt Agent/Entity. |
| Scenarios | `SC-B-01-MAIN`, `SC-B-01-ALT01`, `SC-B-01-EX01` | bleiben gueltig; genau ein Main-Scenario bleibt erhalten. |
| ScenarioSteps | 28 Steps | bleiben gueltig; keine neue Step-Pflichtkante, keine Runtime-Direktkopplung. |
| ActorIntent-Steps | 6 Steps mit `performedBy = ACT-B-01 Visitor` | bleiben gueltig; `Actor` wird nicht mit `Entity` oder `Agent` vermischt. |
| SystemResponse-Steps | 11 Steps mit CapabilityUse | bleiben gueltig; Vivian/Systemreaktionen bleiben ueber CapabilityUse modelliert. |
| InteractionObject-Bedarf | Kaffeemaschine, Starttaste, Tasse, Programmwahl | bisher fachlich modellierbar; optional spaeter mit `InteractionObjectModule` praezisierbar. |
| Vivian-Dialogbedarf | Guidance, Rueckfragen, Erklaerung | bisher fachlich modellierbar; optional spaeter mit `AssistantInteractionModule` praezisierbar. |
| Bereitschaftspruefung | Conditions, StateAssertions und Capability | bisher gueltig; optional spaeter mit `DecisionRuleModule` formalisierbar. |
| Runtime | 11 RuntimeBindings, 25 RuntimeActions | bleibt gueltig; RuntimeExecution/Profile optional. |
| Validation | 10 ValidationCases | bleiben gueltig; ValidationAssertionModule optional. |

Keine B-Instanz wird ungueltig. B kann optional von fast allen Ergaenzungsmodulen profitieren, aber kein Modul ist Pflicht fuer die vorhandene Baseline.

## Ausschluss von Inkompatibilitaeten

| Risiko | Pruefung | Ergebnis |
| --- | --- | --- |
| Neues Pflichtattribut | `Entity.kind` ist `0..1`. | ausgeschlossen |
| Neue Pflichtbeziehung | `Effect.evidencedBy` ist `0..*`. | ausgeschlossen |
| Veraenderte bestehende Kardinalitaet | Bestehende Kernkardinalitaeten bleiben unveraendert. | ausgeschlossen |
| Ersetzung von ScenarioStep | Kein Modul ersetzt `ScenarioStep`. | ausgeschlossen |
| Technische Kurzschaltung | Keine neue direkte `ScenarioStep -> RuntimeAction`-Kante. | ausgeschlossen |
| Actor/Agent-Vermischung | `Actor` bleibt Use-Case-Rolle; `Agent` bleibt Entity-Spezialisierung. | ausgeschlossen |
| Pflichtnutzung von Ergaenzungsmodulen | Alle Module sind optional. | ausgeschlossen |
| Komposition von Kerninstanzen durch Module | Anschlussstellen an den Kern sind nicht-kompositiv. | ausgeschlossen |

## Gueltigkeitsbedingungen bei optionaler Nachpflege

Wenn spaeter optionale Nachpflege vorgenommen wird, gelten folgende Regeln:

| ID | Bedingung |
| --- | --- |
| BC-01 | Eine gesetzte `Entity.kind`-Typisierung muss zur bestehenden Spezialisierung passen. Besonders `kind = agent` darf nur fuer Agenten oder explizite Agent-Spezialisierungen genutzt werden. |
| BC-02 | `Entity.kind` darf keine Actor-Rolle ausdruecken. |
| BC-03 | Ein `Effect.evidencedBy`-Link darf nur auf StateAssertions zeigen, die den Effect fachlich stuetzen oder konkretisieren. |
| BC-04 | Modulinstanzen duerfen nur bestehende Kerninstanzen referenzieren und diese nicht besitzen. |
| BC-05 | Modulinstanzen duerfen keine direkte technische Kurzschaltung einfuehren. |
| BC-06 | Ein bestehender UseCase oder ScenarioStep darf nur dann umbenannt, geloescht oder in der Kardinalitaet geaendert werden, wenn eine separate Modellentscheidung dies explizit begruendet. |

## Abnahmekontrolle

| Kriterium aus Task 11.6 | Erfuellung |
| --- | --- |
| Liste betroffener bestehender Elemente vorhanden | UseCases, Scenarios, ScenarioSteps, Entities, Effects, StateAssertions, RuntimeBindings, RuntimeActions und ValidationCases sind geprueft. |
| Kein bestehender UseCase wird ungueltig | `UC-A-01` und `UC-B-01` bleiben gueltig. |
| Kein bestehender ScenarioStep wird ungueltig | Alle 42 ScenarioSteps bleiben gueltig. |
| Ausnahmen explizit begruendet | Keine Ausnahme erforderlich, weil keine bestehende Instanz ungueltig wird. |
| Optionale Nachpflege getrennt | Optionale Typisierung, Evidence-Links und Module sind als Nachpflege markiert, nicht als Migration. |
| Kerninvarianten bleiben erhalten | Actor/Agent-Trennung, fachlich/technisch-Trennung und Scenario/Runtime-Trennung bleiben erhalten. |

## Konsequenz fuer Task 12.1

Die Beschreibung kann nun auf einer stabilen Grundlage formuliert werden: Das Metamodell ist rueckwaertskompatibel, weil es den Kern nur minimal optional erweitert und groessere Praezisierung bewusst in zuschaltbare Module auslagert. Die Beispiele A und B bleiben im Kern gueltig und koennen bei Bedarf graduell praezisiert werden.
