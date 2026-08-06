# Anwendungsfall A: Scenario-Instanzen

Stand: 2026-07-07

Task: 4.5 `Scenario-Instanzen fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

Ein dynamisch ausfuehrbarer `UseCase` besitzt mindestens ein `Scenario`. Fuer `UC-A-01` werden genau drei Scenario-Instanzen angelegt:

- ein `main` Scenario fuer den erfolgreichen Normalablauf,
- ein `alternative` Scenario fuer eine temporaere Blockade mit Rueckfuehrung,
- ein `exception` Scenario fuer eine dauerhafte Blockade mit sicherem Fehlerabschluss.

Die zentrale Invariante lautet: Pro `UseCase` muss genau ein `Scenario.kind = main` existieren. Weitere `alternative`- und `exception`-Scenarios sind erlaubt.

`Scenario -> ScenarioStep [1..*]` wird in diesem Task ueber stabile geordnete Step-IDs deklariert. Die detaillierten `ScenarioStep`-Instanzen mit Nummer, Text, Art und optionalem `performedBy` folgen in Task 4.6. Damit bleibt die Modellierung schrittweise, ohne leere Scenarios zu erzeugen.

## UseCase-Scenario-Komposition

| Beziehung-ID | Owner | Owned Scenario | Komposition | Kardinalitaetsbewertung |
| --- | --- | --- | --- | --- |
| `A-USC-01` | `UC-A-01` | `A-MAIN-SC01` | `UseCase -> Scenario` | gueltig: `UC-A-01` besitzt mindestens ein Scenario. |
| `A-USC-02` | `UC-A-01` | `A-ALT-SC01` | `UseCase -> Scenario` | gueltig: alternatives Scenario ist zusaetzlich erlaubt. |
| `A-USC-03` | `UC-A-01` | `A-EX-SC01` | `UseCase -> Scenario` | gueltig: exception Scenario ist zusaetzlich erlaubt. |

## Angelegte Scenario-Instanzen

| Instanz-ID | Metamodellklasse | `uuid` | `shortName` | `Scenario.kind` | Name | Owner-UseCase |
| --- | --- | --- | --- | --- | --- | --- |
| `A-MAIN-SC01` | `Scenario` | `A-MAIN-SC01` | `AgentReagiertUndErreichtZielzone` | `main` | `Agent reagiert auf gueltiges Ereignis und erreicht Zielzone` | `UC-A-01` |
| `A-ALT-SC01` | `Scenario` | `A-ALT-SC01` | `TemporaereBlockadeAufloesen` | `alternative` | `Temporaere Blockade der Zielzone aufloesen` | `UC-A-01` |
| `A-EX-SC01` | `Scenario` | `A-EX-SC01` | `DauerhafteBlockadeFehlerabschluss` | `exception` | `Dauerhafte Blockade verhindert Zielerreichung` | `UC-A-01` |

## Scenario-Details

### `A-MAIN-SC01`

| Feld | Wert |
| --- | --- |
| `Scenario.kind` | `main` |
| `goal` | Nach einem gueltigen Ausloeseereignis befindet sich der dynamische Agent innerhalb des gueltigen Szenenbereichs in der passenden Rolle, erreicht die fachlich erreichbare Zielzone und erzeugt eine bestaetigte beobachtbare Rueckmeldung. |
| Einstieg | Start des UseCase-Ablaufs ueber gueltiges Ausloeseereignis, konkret vorbereitet durch `A-E1`. |
| Abschluss | `A-MAIN-S09` bestaetigt die beobachtbare Ergebnisrueckmeldung. |
| Geordnete `ScenarioStep`-IDs | `A-MAIN-S01`, `A-MAIN-S02`, `A-MAIN-S03`, `A-MAIN-S04`, `A-MAIN-S05`, `A-MAIN-S06`, `A-MAIN-S07`, `A-MAIN-S08`, `A-MAIN-S09` |
| Scenario-Preconditions | `A-P1`, `A-P2`, `A-P3`, `A-P4`, `A-P5`, `A-P6`, `A-P7`, `A-P10`, `A-P12` |
| Scenario-Postconditions | `A-Q1`, `A-Q2`, `A-Q3`, `A-Q4`, `A-Q5`, `A-Q11`; optional kontextabhaengig `A-Q6`, `A-Q7`, `A-Q8`, `A-Q9`, `A-Q10` |
| ParallelGroups | keine |

### `A-ALT-SC01`

| Feld | Wert |
| --- | --- |
| `Scenario.kind` | `alternative` |
| `goal` | Die temporaere Blockade wird fachlich aufgeloest, sodass der Agent danach die Ausfuehrungsrolle annehmen und den Hauptpfad fortsetzen kann. |
| Einstieg | Nach `A-MAIN-S04`, wenn `ObstacleRegion.state = temporarilyBlocked and TargetZone.state = reachable` gilt. |
| Rueckfuehrung | Vor `A-MAIN-S05`, wenn `ObstacleRegion.state = cleared and TargetZone.state = reachable` gilt. |
| Geordnete `ScenarioStep`-IDs | `A-ALT-S01`, `A-ALT-S02` |
| Scenario-Preconditions | Hauptpfad hat `A-MAIN-S04` erreicht; `ObstacleRegion.state = temporarilyBlocked`; `TargetZone.state = reachable` |
| Scenario-Postconditions | `ObstacleRegion.state = cleared`; `TargetZone.state = reachable`; Hauptpfad kann vor `A-MAIN-S05` fortgesetzt werden |
| ParallelGroups | keine |

### `A-EX-SC01`

| Feld | Wert |
| --- | --- |
| `Scenario.kind` | `exception` |
| `goal` | Der normale Zielpfad wird sicher beendet, weil die Zielzone dauerhaft nicht erreichbar ist. |
| Einstieg | Nach `A-MAIN-S04`, wenn `ObstacleRegion.state = blocked` gilt. |
| Rueckfuehrung | keine Rueckfuehrung in den Hauptpfad |
| Geordnete `ScenarioStep`-IDs | `A-EX-S01`, `A-EX-S02`, `A-EX-S03` |
| Scenario-Preconditions | Hauptpfad hat `A-MAIN-S04` erreicht; `ObstacleRegion.state = blocked`; `A-GUARD-S04` ist fuer den Erfolgspfad verletzt |
| Scenario-Postconditions | `TargetZone = unreached`; `AgentBody.roleState = blocked`; `FeedbackSignal = failed`; `SceneStateFlag = requiresReaction` |
| ParallelGroups | keine |

## Main-Scenario-Eindeutigkeit

| UseCase | Zugeordnete Scenarios | Anzahl `main` | Bewertung |
| --- | --- | ---: | --- |
| `UC-A-01` | `A-MAIN-SC01`, `A-ALT-SC01`, `A-EX-SC01` | 1 | gueltig: genau ein Main-Scenario. |

## Kardinalitaetscheck auf Scenario-Ebene

| Beziehung oder Attribut | Soll | Ist fuer A | Bewertung |
| --- | --- | --- | --- |
| `UseCase -> Scenario` | `1..*` | `3` Scenarios fuer `UC-A-01` | erfuellt |
| Genau ein `Scenario.kind = main` pro UseCase | `1` | `A-MAIN-SC01` | erfuellt |
| Alternative Scenarios | optional | `A-ALT-SC01` | zulaessig |
| Exception Scenarios | optional | `A-EX-SC01` | zulaessig |
| `Scenario -> ScenarioStep` | `1..*` ordered | Main: 9 Step-IDs; Alternative: 2 Step-IDs; Exception: 3 Step-IDs | als geordnete Membership deklariert, Detailinstanzen folgen in 4.6 |
| `Scenario -> ParallelGroup` | `0..*` | `0` fuer alle drei Scenarios | erfuellt |
| `Scenario.pre/postcondition` | `0..*` | pro Scenario vorhanden oder fachlich angegeben | erfuellt |

## Abgleich mit Satisfy-Referenzen

| Satisfy-Referenz | Erwartete Scenario-ID | In Task 4.5 angelegt? |
| --- | --- | --- |
| `SAT-A-REQ-001` | `A-MAIN-SC01`, `A-ALT-SC01`, `A-EX-SC01` | ja |
| `SAT-A-REQ-005` | `A-ALT-SC01`, `A-EX-SC01` | ja |
| `SAT-A-REQ-011` | `A-ALT-SC01` | ja |
| `SAT-A-REQ-012` | `A-EX-SC01` | ja |
| `SAT-A-REQ-013` | `A-MAIN-SC01`, `A-ALT-SC01`, `A-EX-SC01` | ja |
| `SAT-A-REQ-014` | `A-MAIN-SC01`, `A-ALT-SC01`, `A-EX-SC01` | ja |
| `SAT-A-REQ-015` | `A-MAIN-SC01`, `A-ALT-SC01`, `A-EX-SC01` | ja |
| `SAT-A-UC-001` | `A-MAIN-SC01`, `A-ALT-SC01`, `A-EX-SC01` | ja |

## Nicht vorweggenommen

| Elementgruppe | Status | Folgetask |
| --- | --- | --- |
| Detaillierte `ScenarioStep`-Instanzen | nur Step-ID-Membership deklariert | 4.6 |
| `Event`-Instanzen | nicht formal angelegt | 4.7 |
| `Condition`-Instanzen | nicht formal angelegt | 4.8 |
| `StateAssertion`-Instanzen | nicht formal angelegt | 4.9 |
| `StepRelation`-Instanzen | bereits fachlich vorbereitet, formale Konsolidierung erfolgt mit den Steps | 4.6 bis 4.9 |
| `CapabilityUse`, `Capability`, `Effect`, `RuntimeBinding`, `RuntimeAction` | nicht angelegt | 4.10 bis 4.14 |
| `ValidationCase` | nicht angelegt | 4.15 |

## Abnahmekontrolle

| Kriterium aus Task 4.5 | Erfuellung |
| --- | --- |
| Main Scenario angelegt | `A-MAIN-SC01` mit `Scenario.kind = main` |
| Alternative Scenario angelegt | `A-ALT-SC01` mit `Scenario.kind = alternative` |
| Exception Scenario angelegt | `A-EX-SC01` mit `Scenario.kind = exception` |
| Genau ein Main Scenario pro UseCase | `UC-A-01` besitzt genau ein `main` Scenario. |
| Scenario-IDs stimmen mit Satisfy-Referenzen ueberein | Alle in Task 4.4 referenzierten Scenario-IDs sind angelegt. |
| Keine technische Kurzschaltung | Kein Scenario referenziert RuntimeAction, API, Topic oder Controlleraktion. |

## Konsequenz fuer Task 4.6

Task 4.6 kann nun die `ScenarioStep`-Instanzen fuer `A-MAIN-SC01`, `A-ALT-SC01` und `A-EX-SC01` formal anlegen. Dabei muessen die hier deklarierten geordneten Step-ID-Memberships exakt uebernommen werden.
