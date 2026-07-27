# Anwendungsfall B: ScenarioStep-Instanzen

Stand: 2026-07-07

Task: 8.6 `ScenarioSteps fuer B anlegen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Modellierungsregel

`ScenarioStep` ist ein geordneter fachlicher Schritt innerhalb genau eines `Scenario`. Die Komposition `Scenario -> ScenarioStep [1..*]` bedeutet: Jeder hier angelegte Schritt gehoert genau zu seinem Owner-Scenario.

In diesem Task werden nur die Step-Instanzen mit `uuid`, `shortName`, `stepNumber`, `ScenarioStep.kind`, `text` und optionalem `performedBy` angelegt. Events, Guard Conditions, StateAssertions, CapabilityUses und Runtime-Beziehungen bleiben fuer Task 8.7 bis 8.11 offen.

`performedBy` wird nur gesetzt, wenn `ScenarioStep.kind = actorIntent` ist. In Anwendungsfall B betrifft das die fachlichen Benutzerhandlungen des Visitors. Vivian-, System- und Objektreaktionen erhalten kein `performedBy`, weil Vivian als `Agent`/`Entity` modelliert ist und Systemantworten spaeter ueber `CapabilityUse -> Capability` beschrieben werden.

## ScenarioStep-Instanzen fuer `SC-B-01-MAIN`

| Owner-Scenario | Step-ID | Metamodellklasse | `uuid` | `shortName` | `stepNumber` | `ScenarioStep.kind` | `performedBy` | `text` |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `SC-B-01-MAIN` | `B-MAIN-S01` | `ScenarioStep` | `B-MAIN-S01` | `AssistenzAnfordern` | 1 | `actorIntent` | `ACT-B-01 Visitor` | Der Visitor fordert die assistierte Kaffeemaschinenbedienung an. |
| `SC-B-01-MAIN` | `B-MAIN-S02` | `ScenarioStep` | `B-MAIN-S02` | `VivianFuehrungsmodusAktivieren` | 2 | `systemResponse` | leer | Vivian wechselt in den Fuehrungsmodus fuer die Kaffeemaschinenbedienung. |
| `SC-B-01-MAIN` | `B-MAIN-S03` | `ScenarioStep` | `B-MAIN-S03` | `TassenplatzierungAnleiten` | 3 | `systemResponse` | leer | Vivian weist den Visitor auf die notwendige Tassenplatzierung hin. |
| `SC-B-01-MAIN` | `B-MAIN-S04` | `ScenarioStep` | `B-MAIN-S04` | `TassePlatzieren` | 4 | `actorIntent` | `ACT-B-01 Visitor` | Der Visitor platziert die Tasse an der Kaffeemaschine. |
| `SC-B-01-MAIN` | `B-MAIN-S05` | `ScenarioStep` | `B-MAIN-S05` | `TasseErkanntMelden` | 5 | `environmentObservation` | leer | Die Kaffeemaschine meldet, dass eine Tasse vorhanden ist. |
| `SC-B-01-MAIN` | `B-MAIN-S06` | `ScenarioStep` | `B-MAIN-S06` | `ProgrammauswahlAnleiten` | 6 | `systemResponse` | leer | Vivian weist den Visitor auf die Programmauswahl hin. |
| `SC-B-01-MAIN` | `B-MAIN-S07` | `ScenarioStep` | `B-MAIN-S07` | `KaffeeprogrammWaehlen` | 7 | `actorIntent` | `ACT-B-01 Visitor` | Der Visitor waehlt das Kaffeeprogramm. |
| `SC-B-01-MAIN` | `B-MAIN-S08` | `ScenarioStep` | `B-MAIN-S08` | `ProgrammauswahlBestaetigen` | 8 | `environmentObservation` | leer | Die Kaffeemaschine bestaetigt die Programmauswahl. |
| `SC-B-01-MAIN` | `B-MAIN-S09` | `ScenarioStep` | `B-MAIN-S09` | `StarttasteBetaetigen` | 9 | `actorIntent` | `ACT-B-01 Visitor` | Der Visitor betaetigt die Starttaste. |
| `SC-B-01-MAIN` | `B-MAIN-S10` | `ScenarioStep` | `B-MAIN-S10` | `BruehanforderungBestaetigen` | 10 | `systemResponse` | leer | Vivian bestaetigt die erkannte Bruehanforderung. |
| `SC-B-01-MAIN` | `B-MAIN-S11` | `ScenarioStep` | `B-MAIN-S11` | `BedienbereitschaftPruefen` | 11 | `systemResponse` | leer | Das System prueft die Bedienbereitschaft der Kaffeemaschine. |
| `SC-B-01-MAIN` | `B-MAIN-S12` | `ScenarioStep` | `B-MAIN-S12` | `StartbereitschaftMelden` | 12 | `environmentObservation` | leer | Die Kaffeemaschine meldet ihre Startbereitschaft. |
| `SC-B-01-MAIN` | `B-MAIN-S13` | `ScenarioStep` | `B-MAIN-S13` | `StartbestaetigungAnfordern` | 13 | `systemResponse` | leer | Vivian fordert die explizite Startbestaetigung an. |
| `SC-B-01-MAIN` | `B-MAIN-S14` | `ScenarioStep` | `B-MAIN-S14` | `AssistiertenStartBestaetigen` | 14 | `actorIntent` | `ACT-B-01 Visitor` | Der Visitor bestaetigt den assistierten Start. |
| `SC-B-01-MAIN` | `B-MAIN-S15` | `ScenarioStep` | `B-MAIN-S15` | `BruehvorgangFachlichStarten` | 15 | `systemResponse` | leer | Das System startet den Bruehvorgang fachlich. |
| `SC-B-01-MAIN` | `B-MAIN-S16` | `ScenarioStep` | `B-MAIN-S16` | `BruehzustandMelden` | 16 | `environmentObservation` | leer | Die Kaffeemaschine wechselt in den Zustand `brewing`. |
| `SC-B-01-MAIN` | `B-MAIN-S17` | `ScenarioStep` | `B-MAIN-S17` | `BruehfortschrittAnzeigen` | 17 | `environmentObservation` | leer | Die Kaffeemaschine zeigt den Bruehfortschritt an. |
| `SC-B-01-MAIN` | `B-MAIN-S18` | `ScenarioStep` | `B-MAIN-S18` | `AbschlusszustandMelden` | 18 | `environmentObservation` | leer | Die Kaffeemaschine wechselt in den Zustand `finished`. |
| `SC-B-01-MAIN` | `B-MAIN-S19` | `ScenarioStep` | `B-MAIN-S19` | `AbschlussrueckmeldungAnzeigen` | 19 | `environmentObservation` | leer | Die Kaffeemaschine zeigt die Abschlussrueckmeldung an. |
| `SC-B-01-MAIN` | `B-MAIN-S20` | `ScenarioStep` | `B-MAIN-S20` | `VivianAbschlussMelden` | 20 | `systemResponse` | leer | Vivian meldet dem Visitor den erfolgreichen Abschluss. |

## ScenarioStep-Instanzen fuer `SC-B-01-ALT01`

| Owner-Scenario | Step-ID | Metamodellklasse | `uuid` | `shortName` | `stepNumber` | `ScenarioStep.kind` | `performedBy` | `text` |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `SC-B-01-ALT01` | `B-ALT-S01` | `ScenarioStep` | `B-ALT-S01` | `TasseFehltMelden` | 1 | `environmentObservation` | leer | Die Kaffeemaschine meldet, dass keine Tasse erkannt wurde. |
| `SC-B-01-ALT01` | `B-ALT-S02` | `ScenarioStep` | `B-ALT-S02` | `TassenkorrekturAnleiten` | 2 | `systemResponse` | leer | Vivian weist den Visitor darauf hin, die Tasse korrekt zu platzieren oder neu auszurichten. |
| `SC-B-01-ALT01` | `B-ALT-S03` | `ScenarioStep` | `B-ALT-S03` | `TasseNeuAusrichten` | 3 | `actorIntent` | `ACT-B-01 Visitor` | Der Visitor platziert oder richtet die Tasse an der Kaffeemaschine neu aus. |
| `SC-B-01-ALT01` | `B-ALT-S04` | `ScenarioStep` | `B-ALT-S04` | `TasseNunVorhandenMelden` | 4 | `environmentObservation` | leer | Die Kaffeemaschine meldet, dass die Tasse nun vorhanden ist. |

## ScenarioStep-Instanzen fuer `SC-B-01-EX01`

| Owner-Scenario | Step-ID | Metamodellklasse | `uuid` | `shortName` | `stepNumber` | `ScenarioStep.kind` | `performedBy` | `text` |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `SC-B-01-EX01` | `B-EX-S01` | `ScenarioStep` | `B-EX-S01` | `BereitschaftFehlgeschlagenMelden` | 1 | `environmentObservation` | leer | Die Bereitschaftspruefung meldet, dass die Kaffeemaschine wegen zu niedrigem Wasserstand nicht startbereit ist. |
| `SC-B-01-EX01` | `B-EX-S02` | `ScenarioStep` | `B-EX-S02` | `FehlerUrsacheErklaeren` | 2 | `systemResponse` | leer | Vivian erklaert dem Visitor, dass der Bruehstart wegen fehlender Startbereitschaft nicht ausgefuehrt wird. |
| `SC-B-01-EX01` | `B-EX-S03` | `ScenarioStep` | `B-EX-S03` | `SicherenNichtBruehendenZustandMelden` | 3 | `environmentObservation` | leer | Die Kaffeemaschine bleibt startblockiert und in einem sicheren nicht bruehenden Zustand. |
| `SC-B-01-EX01` | `B-EX-S04` | `ScenarioStep` | `B-EX-S04` | `AusnahmefallAbschliessen` | 4 | `systemResponse` | leer | Vivian schliesst den Ausnahmefall ab und laesst den Hauptpfad nicht weiterlaufen. |

## Sortier- und Besitzcheck

| Scenario | Erwartete Step-Folge | Anzahl Steps | Bewertung |
| --- | --- | ---: | --- |
| `SC-B-01-MAIN` | `B-MAIN-S01 -> B-MAIN-S02 -> B-MAIN-S03 -> B-MAIN-S04 -> B-MAIN-S05 -> B-MAIN-S06 -> B-MAIN-S07 -> B-MAIN-S08 -> B-MAIN-S09 -> B-MAIN-S10 -> B-MAIN-S11 -> B-MAIN-S12 -> B-MAIN-S13 -> B-MAIN-S14 -> B-MAIN-S15 -> B-MAIN-S16 -> B-MAIN-S17 -> B-MAIN-S18 -> B-MAIN-S19 -> B-MAIN-S20` | 20 | eindeutig sortiert von `stepNumber = 1` bis `20` |
| `SC-B-01-ALT01` | `B-ALT-S01 -> B-ALT-S02 -> B-ALT-S03 -> B-ALT-S04` | 4 | eindeutig sortiert von `stepNumber = 1` bis `4` |
| `SC-B-01-EX01` | `B-EX-S01 -> B-EX-S02 -> B-EX-S03 -> B-EX-S04` | 4 | eindeutig sortiert von `stepNumber = 1` bis `4` |

## `performedBy`-Entscheidung

| Step-Kategorie | Betroffene Steps | `performedBy` | Begruendung |
| --- | --- | --- | --- |
| `actorIntent` | `B-MAIN-S01`, `B-MAIN-S04`, `B-MAIN-S07`, `B-MAIN-S09`, `B-MAIN-S14`, `B-ALT-S03` | `ACT-B-01 Visitor` | Diese Schritte beschreiben eine externe Benutzerabsicht oder Bedienhandlung. |
| `systemResponse` | `B-MAIN-S02`, `B-MAIN-S03`, `B-MAIN-S06`, `B-MAIN-S10`, `B-MAIN-S11`, `B-MAIN-S13`, `B-MAIN-S15`, `B-MAIN-S20`, `B-ALT-S02`, `B-EX-S02`, `B-EX-S04` | leer | Vivian- und Systemreaktionen werden nicht als Actor-Handlung modelliert, sondern spaeter ueber `CapabilityUse` und `Capability`. |
| `environmentObservation` | `B-MAIN-S05`, `B-MAIN-S08`, `B-MAIN-S12`, `B-MAIN-S16`, `B-MAIN-S17`, `B-MAIN-S18`, `B-MAIN-S19`, `B-ALT-S01`, `B-ALT-S04`, `B-EX-S01`, `B-EX-S03` | leer | Objekt- und Zustandsbeobachtungen werden nicht von einem Actor ausgefuehrt. |

## Zuordnungsanker fuer Folge-Tasks

Diese Tabelle erfuellt das Abnahmekriterium, dass jeder Schritt einer Rolle, einem Event oder einer Faehigkeit zuordenbar ist. Sie legt noch keine formalen `Event`, `Condition`, `StateAssertion` oder `CapabilityUse`-Instanzen an.

| Step-ID | Primaerer Zuordnungsanker | Typ | Folgetask |
| --- | --- | --- | --- |
| `B-MAIN-S01` | `ACT-B-01 Visitor`, `B-E01` | Rolle und User-Event | 8.7 |
| `B-MAIN-S02` | `B-E01`, Kandidat `CAP-B-VIVIAN-ENTER-GUIDANCE` | Event und Capability-Kandidat | 8.7, 8.8 |
| `B-MAIN-S03` | `B-E02`, Kandidat `CAP-B-VIVIAN-GUIDE-CUP` | Event und Capability-Kandidat | 8.7, 8.8 |
| `B-MAIN-S04` | `ACT-B-01 Visitor`, `B-E03` | Rolle und User-Event | 8.7 |
| `B-MAIN-S05` | `B-E04`, `ENT-B-02 CoffeeMachine` | Environment-Event und Entity | 8.7 |
| `B-MAIN-S06` | `B-E04`, Kandidat `CAP-B-VIVIAN-GUIDE-PROGRAM` | Event und Capability-Kandidat | 8.7, 8.8 |
| `B-MAIN-S07` | `ACT-B-01 Visitor`, `B-E05` | Rolle und User-Event | 8.7 |
| `B-MAIN-S08` | `B-E06`, `ENT-B-02 CoffeeMachine` | Environment-Event und Entity | 8.7 |
| `B-MAIN-S09` | `ACT-B-01 Visitor`, `B-E07` | Rolle und User-Event | 8.7 |
| `B-MAIN-S10` | `B-E07`, Kandidat `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST` | Event und Capability-Kandidat | 8.7, 8.8 |
| `B-MAIN-S11` | `B-E08`, Kandidat `CAP-B-CHECK-MACHINE-READY` | Event und Capability-Kandidat | 8.7, 8.8 |
| `B-MAIN-S12` | `B-E09`, `ENT-B-02 CoffeeMachine` | Environment-Event und Entity | 8.7 |
| `B-MAIN-S13` | `B-E09`, Kandidat `CAP-B-VIVIAN-REQUEST-CONFIRMATION` | Event und Capability-Kandidat | 8.7, 8.8 |
| `B-MAIN-S14` | `ACT-B-01 Visitor`, `B-E10`, `B-E11` | Rolle, Signal-Event und User-Event | 8.7 |
| `B-MAIN-S15` | `B-E11`, `B-E12`, Kandidat `CAP-B-START-BREWING` | Events und Capability-Kandidat | 8.7, 8.8 |
| `B-MAIN-S16` | `B-E13`, `ENT-B-02 CoffeeMachine` | Environment-Event und Entity | 8.7 |
| `B-MAIN-S17` | `B-E14`, `ENT-B-02 CoffeeMachine` | Environment-Event und Entity | 8.7 |
| `B-MAIN-S18` | `B-E15`, `ENT-B-02 CoffeeMachine` | Environment-Event und Entity | 8.7 |
| `B-MAIN-S19` | `B-E16`, `ENT-B-02 CoffeeMachine` | Environment-Event und Entity | 8.7 |
| `B-MAIN-S20` | `B-E16`, `B-E17`, Kandidat `CAP-B-VIVIAN-REPORT-COMPLETION` | Events und Capability-Kandidat | 8.7, 8.8 |
| `B-ALT-S01` | `B-ALT-E01`, `ENT-B-02 CoffeeMachine` | Environment-Event und Entity | 8.7 |
| `B-ALT-S02` | `B-ALT-E02`, Kandidat `CAP-B-VIVIAN-GUIDE-CUP-CORRECTION` | Event und Capability-Kandidat | 8.7, 8.8 |
| `B-ALT-S03` | `ACT-B-01 Visitor`, `B-ALT-E03` | Rolle und User-Event | 8.7 |
| `B-ALT-S04` | `B-E04`, `ENT-B-02 CoffeeMachine` | Environment-Event und Entity | 8.7 |
| `B-EX-S01` | `B-EX-E01`, `ENT-B-02 CoffeeMachine` | Environment-Event und Entity | 8.7 |
| `B-EX-S02` | `B-EX-E02`, Kandidat `CAP-B-VIVIAN-EXPLAIN-ERROR` | Event und Capability-Kandidat | 8.7, 8.8 |
| `B-EX-S03` | `B-EX-E03`, `ENT-B-02 CoffeeMachine` | Environment-Event und Entity | 8.7 |
| `B-EX-S04` | `B-EX-E04`, Kandidat `CAP-B-VIVIAN-CLOSE-EXCEPTION` | Event und Capability-Kandidat | 8.7, 8.8 |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 8.6 | Folgetask |
| --- | --- | --- |
| `Event`-Instanzen und `triggeredBy` | nicht formal angelegt | 8.7 |
| `Condition`-Instanzen und `guard` | nicht formal angelegt | 8.7 |
| `StateAssertion`-Instanzen und `resultingState` | nicht formal angelegt | 8.7 |
| `CapabilityUse`-Instanzen | nicht angelegt | 8.8 |
| `Capability`-Instanzen und `Effect`-Instanzen | nicht angelegt | 8.9 |
| `RuntimeAction`-Referenzen | bewusst keine direkte Referenz | 8.10 und 8.11 ueber `RuntimeBinding` |
| `ValidationCase` | nicht angelegt | 8.12 |

## Abnahmekontrolle

| Kriterium aus Task 8.6 | Erfuellung |
| --- | --- |
| Nummerierte Schrittliste vorhanden | 28 `ScenarioStep`-Instanzen besitzen `stepNumber`. |
| Schrittliste mit Text vorhanden | Jede Step-Instanz besitzt ein fachliches `text`-Attribut. |
| Schrittliste mit Art vorhanden | Jeder Step hat genau einen Wert aus `actorIntent`, `systemResponse`, `environmentObservation`. |
| Optionales `performedBy` korrekt behandelt | Nur sechs `actorIntent`-Steps haben `performedBy = ACT-B-01 Visitor`; alle anderen Steps bleiben leer. |
| Schrittfolge eindeutig sortiert | Jede Scenario-Tabelle beginnt bei `1` und steigt ohne Luecke an. |
| Jeder Step gehoert genau zu einem Scenario | Jede Zeile besitzt genau ein `Owner-Scenario`. |
| Jeder Schritt ist zuordenbar | Jeder Step besitzt einen Zuordnungsanker zu Rolle, Event, Entity oder Capability-Kandidat. |
| Keine technische Kurzschaltung | Kein Step referenziert RuntimeAction, API, Topic, Tool oder Controlleraktion direkt. |

## Konsequenz fuer Task 8.7

Task 8.7 kann nun die Event-, Condition- und StateAssertion-Instanzen fuer B konsolidiert anlegen und sie den hier formalisierten Step-IDs zuordnen.
