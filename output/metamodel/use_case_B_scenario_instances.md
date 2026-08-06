# Anwendungsfall B: Scenario-Instanzen

Stand: 2026-07-07

Task: 8.5 `Scenarios fuer B anlegen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Modellierungsregel

Ein dynamisch ausfuehrbarer `UseCase` besitzt mindestens ein `Scenario`. Fuer `UC-B-01` werden genau drei Scenario-Instanzen angelegt:

- ein `main` Scenario fuer den erfolgreichen assistierten Bedienablauf,
- ein `alternative` Scenario fuer eine korrigierbare fehlende Tasse mit Rueckfuehrung,
- ein `exception` Scenario fuer eine fehlgeschlagene Bereitschaftspruefung ohne Rueckfuehrung.

Die zentrale Invariante lautet: Pro `UseCase` muss genau ein `Scenario.kind = main` existieren. Weitere `alternative`- und `exception`-Scenarios sind erlaubt.

`Scenario -> ScenarioStep [1..*]` wird in diesem Task ueber stabile geordnete Step-IDs deklariert. Die detaillierten `ScenarioStep`-Instanzen mit Nummer, Text, Art, `performedBy`, Events, Guards und resultierenden StateAssertions folgen in Task 8.6 und 8.7. Damit entstehen keine leeren Scenarios, aber die Step-Instanziierung wird nicht vorweggenommen.

## UseCase-Scenario-Komposition

| Beziehung-ID | Owner | Owned Scenario | Komposition | Kardinalitaetsbewertung |
| --- | --- | --- | --- | --- |
| `B-USC-01` | `UC-B-01` | `SC-B-01-MAIN` | `UseCase -> Scenario` | gueltig: `UC-B-01` besitzt mindestens ein Scenario. |
| `B-USC-02` | `UC-B-01` | `SC-B-01-ALT01` | `UseCase -> Scenario` | gueltig: alternatives Scenario ist zusaetzlich erlaubt. |
| `B-USC-03` | `UC-B-01` | `SC-B-01-EX01` | `UseCase -> Scenario` | gueltig: exception Scenario ist zusaetzlich erlaubt. |

## Angelegte Scenario-Instanzen

| Instanz-ID | Metamodellklasse | `uuid` | `shortName` | `Scenario.kind` | Name | Owner-UseCase |
| --- | --- | --- | --- | --- | --- | --- |
| `SC-B-01-MAIN` | `Scenario` | `SC-B-01-MAIN` | `AssistierteKaffeemaschinenbedienungErfolgreich` | `main` | `Assistierte Kaffeemaschinenbedienung erfolgreich ausfuehren` | `UC-B-01` |
| `SC-B-01-ALT01` | `Scenario` | `SC-B-01-ALT01` | `FehlendeTasseKorrigieren` | `alternative` | `Fehlende Tasse korrigieren` | `UC-B-01` |
| `SC-B-01-EX01` | `Scenario` | `SC-B-01-EX01` | `BereitschaftspruefungSchlaegtFehl` | `exception` | `Bereitschaftspruefung schlaegt fehl` | `UC-B-01` |

## Scenario-Details

### `SC-B-01-MAIN`

| Feld | Wert |
| --- | --- |
| `Scenario.kind` | `main` |
| `goal` | Der Visitor bedient mit Vivian als Assistenzagent eine virtuelle Kaffeemaschine so, dass Tasse, Programmauswahl, Bereitschaft, Startbestaetigung, Bruehzustand, Fortschritt, Abschlusszustand und Rueckmeldung fachlich nachvollziehbar und pruefbar sind. |
| Einstieg | Start des assistierten Use-Case-Ablaufs durch `B-MAIN-S01` mit Hilfewunsch des Visitors, vorbereitet durch `B-E01` und `B-MAIN-G01`. |
| Abschluss | `B-MAIN-S20` meldet den erfolgreichen Abschluss durch Vivian, nachdem die Kaffeemaschine Abschlussfeedback liefert. |
| Geordnete `ScenarioStep`-IDs | `B-MAIN-S01`, `B-MAIN-S02`, `B-MAIN-S03`, `B-MAIN-S04`, `B-MAIN-S05`, `B-MAIN-S06`, `B-MAIN-S07`, `B-MAIN-S08`, `B-MAIN-S09`, `B-MAIN-S10`, `B-MAIN-S11`, `B-MAIN-S12`, `B-MAIN-S13`, `B-MAIN-S14`, `B-MAIN-S15`, `B-MAIN-S16`, `B-MAIN-S17`, `B-MAIN-S18`, `B-MAIN-S19`, `B-MAIN-S20` |
| Scenario-Preconditions | `B-MAIN-PRE-01`, `B-MAIN-PRE-02`, `B-MAIN-PRE-03`, `B-MAIN-PRE-04`, `B-MAIN-PRE-05` |
| Scenario-Postconditions | `B-MAIN-POST-01`, `B-MAIN-POST-02`, `B-MAIN-POST-03`, `B-MAIN-POST-04`, `B-MAIN-POST-05` |
| Relevante StepRelations im Kontext | `B-MAIN-R01` bis `B-MAIN-R19` |
| ParallelGroups | keine |

### `SC-B-01-ALT01`

| Feld | Wert |
| --- | --- |
| `Scenario.kind` | `alternative` |
| `goal` | Eine zunaechst fehlende oder nicht erkannte Tasse wird durch Benutzerhandlung korrigiert, sodass die assistierte Bedienung vor der Programmauswahl in den Hauptpfad zurueckkehren kann. |
| Einstieg | Nach `B-MAIN-S05`, wenn `B-ALT-G01` gilt: `CoffeeMachine.cupPresent = false`. |
| Rueckfuehrung | Vor `B-MAIN-S06`, wenn `B-ALT-G02` gilt: `CoffeeMachine.cupPresent = true`. |
| Geordnete `ScenarioStep`-IDs | `B-ALT-S01`, `B-ALT-S02`, `B-ALT-S03`, `B-ALT-S04` |
| Scenario-Preconditions | `B-ALT-PRE-01` |
| Scenario-Postconditions | `B-ALT-POST-01`, `B-ALT-POST-02` |
| Relevante StepRelations im Kontext | `B-ALT-R-IN01`, `B-ALT-R01`, `B-ALT-R02`, `B-ALT-R03`, `B-ALT-R-OUT01` |
| ParallelGroups | keine |

Dieses Scenario ist kein `Extend`: Es ist kein optionales Zusatzverhalten an einem ExtensionPoint, sondern ein korrigierbarer Ablaufzweig innerhalb desselben Use Case.

### `SC-B-01-EX01`

| Feld | Wert |
| --- | --- |
| `Scenario.kind` | `exception` |
| `goal` | Eine fehlgeschlagene Bereitschaftspruefung verhindert den Bruehstart, blockiert die Startfreigabe, haelt die Kaffeemaschine in einem sicheren nicht bruehenden Zustand und laesst Vivian die Ursache erklaeren. |
| Einstieg | Nach `B-MAIN-S11`, wenn `B-EX-G01` gilt: `ReadinessCheck.result = failed and CoffeeMachine.waterLevel = low and correctionInCurrentScenario = false`. |
| Rueckfuehrung | keine Rueckfuehrung in den Hauptpfad |
| Geordnete `ScenarioStep`-IDs | `B-EX-S01`, `B-EX-S02`, `B-EX-S03`, `B-EX-S04` |
| Scenario-Preconditions | `B-EX-PRE-01` |
| Scenario-Postconditions | `B-EX-POST-01`, `B-EX-POST-02`, `B-EX-POST-03`, `B-EX-POST-04`, `B-EX-POST-05` |
| Relevante StepRelations im Kontext | `B-EX-R-IN01`, `B-EX-R01`, `B-EX-R02`, `B-EX-R03` |
| ParallelGroups | keine |

Dieses Scenario ist keine Alternative: Der Pfad ist innerhalb des aktuellen Ablaufs nicht korrigierbar, startet keinen Bruehvorgang und kehrt nicht zu `B-MAIN-S12` oder spaeteren Hauptpfadschritten zurueck.

## Main-Scenario-Eindeutigkeit

| UseCase | Zugeordnete Scenarios | Anzahl `main` | Bewertung |
| --- | --- | ---: | --- |
| `UC-B-01` | `SC-B-01-MAIN`, `SC-B-01-ALT01`, `SC-B-01-EX01` | 1 | gueltig: genau ein Main Scenario. |

## Kardinalitaetscheck auf Scenario-Ebene

| Beziehung oder Attribut | Soll | Ist fuer B | Bewertung |
| --- | --- | --- | --- |
| `UseCase -> Scenario` | `1..*` | `3` Scenarios fuer `UC-B-01` | erfuellt |
| Genau ein `Scenario.kind = main` pro UseCase | `1` | `SC-B-01-MAIN` | erfuellt |
| Alternative Scenarios | optional | `SC-B-01-ALT01` | zulaessig |
| Exception Scenarios | optional | `SC-B-01-EX01` | zulaessig |
| `Scenario -> ScenarioStep` | `1..*` ordered composition | Main: 20 Step-IDs; Alternative: 4 Step-IDs; Exception: 4 Step-IDs | als geordnete Membership deklariert, Detailinstanzen folgen in 8.6 |
| `Scenario -> ParallelGroup` | `0..*` | `0` fuer alle drei Scenarios | erfuellt |
| `Scenario.pre/postcondition` | `0..*` | pro Scenario fachlich referenziert | erfuellt |

## Abgleich mit Requirements

| Requirement | Erwartete Scenario-Abdeckung | In Task 8.5 angelegt? |
| --- | --- | --- |
| `B-REQ-001` | UseCase mit main, alternative und exception Scenarios | ja |
| `B-REQ-003` bis `B-REQ-013` | erfolgreicher Hauptpfad `SC-B-01-MAIN` | ja |
| `B-REQ-006` | korrigierbare fehlende Tasse in `SC-B-01-ALT01` | ja |
| `B-REQ-014` | fehlgeschlagene Bereitschaftspruefung in `SC-B-01-EX01` | ja |
| `B-REQ-015` | sicherer und erklaerter Exception-Abschluss in `SC-B-01-EX01` | ja |
| `B-REQ-016` | Alternative/Exception nicht als Include/Extend missbraucht | ja |
| `B-REQ-017` | keine technische Kurzschaltung in Scenarios | ja |
| `B-REQ-018` | Scenario-Ebene fuer Traceability vorbereitet | ja |

Diese Tabelle ist noch keine formale `Satisfy`-Instanziierung. Sie dient nur als Konsistenzabgleich fuer die spaetere Trace-Kette.

## Nicht vorweggenommen

| Elementgruppe | Status | Folgetask |
| --- | --- | --- |
| Detaillierte `ScenarioStep`-Instanzen | nur Step-ID-Membership deklariert | 8.6 |
| `Event`, `Condition`, `StateAssertion`-Instanzen als konsolidierte Mapping-Instanzen | fachlich vorbereitet, aber hier nicht neu instanziiert | 8.7 |
| `CapabilityUse` | nicht angelegt | 8.8 |
| `Capability`, `Effect` | nicht angelegt | 8.9 |
| `RuntimeBinding`, `RuntimeAction` | nicht angelegt | 8.10 und 8.11 |
| `ValidationCase` | nicht angelegt | 8.12 |
| `Satisfy` | nicht angelegt | spaetere Konsolidierung nach B-Mapping |

## Abnahmekontrolle

| Kriterium aus Task 8.5 | Erfuellung |
| --- | --- |
| Main Scenario angelegt | `SC-B-01-MAIN` mit `Scenario.kind = main` |
| Alternative Scenario angelegt | `SC-B-01-ALT01` mit `Scenario.kind = alternative` |
| Exception Scenario angelegt | `SC-B-01-EX01` mit `Scenario.kind = exception` |
| Genau ein Main Scenario | `UC-B-01` besitzt genau ein `main` Scenario. |
| Scenarios besitzen Step-Membership | Alle drei Scenarios deklarieren mindestens eine geordnete Step-ID. |
| Alternative und Exception semantisch getrennt | `SC-B-01-ALT01` kehrt in den Hauptpfad zurueck; `SC-B-01-EX01` nicht. |
| Keine technische Kurzschaltung | Kein Scenario referenziert RuntimeAction, API, Topic, Tool oder Controlleraktion. |
| Folge-Tasks nicht vorweggenommen | Detailsteps, Events, Conditions, StateAssertions, Capabilities, Runtime und Validation bleiben fuer die vorgesehenen Tasks offen. |

## Konsequenz fuer Task 8.6

Task 8.6 kann nun die `ScenarioStep`-Instanzen fuer `SC-B-01-MAIN`, `SC-B-01-ALT01` und `SC-B-01-EX01` formal anlegen. Dabei muessen die hier deklarierten geordneten Step-ID-Memberships exakt uebernommen werden.
