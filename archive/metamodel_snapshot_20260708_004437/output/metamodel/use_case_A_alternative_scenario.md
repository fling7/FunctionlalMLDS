# Anwendungsfall A: Alternatives Szenario

Stand: 2026-07-07

Task: 3.8 `Alternatives Szenario A formulieren`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

Alternative Scenario: `Temporaere Blockade der Zielzone aufloesen`

## Szenario-Festlegung

| Feld | Wert |
| --- | --- |
| Scenario-ID | `A-ALT-SC01` |
| `Scenario.kind` | `alternative` |
| Name | `Temporaere Blockade der Zielzone aufloesen` |
| Einstiegspunkt im Hauptpfad | nach `A-MAIN-S04` |
| Rueckfuehrung in den Hauptpfad | vor `A-MAIN-S05` |
| Bezug zu vorbereitetem Alternativfall | `A-ALT2` |
| Ziel des Alternativszenarios | Die temporaere Blockade wird fachlich aufgeloest, sodass der Agent danach die Ausfuehrungsrolle annehmen und den Hauptpfad fortsetzen kann. |

## Einstieg und Bedingung

| Aspekt | Modellierung |
| --- | --- |
| Ausloeser | `A-E4`: `stateChanged(ObstacleRegion, blocked|temporarilyBlocked)` |
| Einstiegskante | `A-MAIN-S04 -> A-ALT-S01` |
| `StepRelation.kind` fuer Einstieg | `alternative` |
| Guard der Einstiegskante | `ObstacleRegion.state = temporarilyBlocked and TargetZone.state = reachable` |
| Warum Alternative und keine Exception? | Die Blockade ist temporaer und kann fachlich aufgehoben werden; der Hauptzielzustand bleibt erreichbar. |

## Alternative ScenarioSteps

| Step-Nr. | Step-ID | ScenarioStep-Kandidat | `ScenarioStep.kind` | Event | Guard | Erwartete StateAssertions |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `A-ALT-S01` | Die temporaere Blockade der Zielzone wird festgestellt. | `environmentObservation` | `A-E4` | `ObstacleRegion.state = temporarilyBlocked` | `ObstacleRegion = temporarilyBlocked`; `SceneStateFlag = requiresReaction` |
| 2 | `A-ALT-S02` | Die Blockade wird fachlich als aufgehoben festgestellt. | `environmentObservation` | kein eigenes Event | `ObstacleRegion.state in {temporarilyBlocked, cleared}` | `ObstacleRegion = cleared`; `TargetZone = reachable` |

## StepRelations des Alternativszenarios

| Relation-ID | Source-Step | Target-Step | `StepRelation.kind` | Guard | Zweck |
| --- | --- | --- | --- | --- | --- |
| `A-ALT-R01` | `A-MAIN-S04` | `A-ALT-S01` | `alternative` | `ObstacleRegion.state = temporarilyBlocked and TargetZone.state = reachable` | Einstieg aus der Zielerreichbarkeitspruefung in den Alternativpfad. |
| `A-ALT-R02` | `A-ALT-S01` | `A-ALT-S02` | `sequence` | keine | Nach Feststellung der temporaeren Blockade wird deren fachliche Aufloesung beobachtet. |
| `A-ALT-R03` | `A-ALT-S02` | `A-MAIN-S05` | `sequence` | `ObstacleRegion.state = cleared and TargetZone.state = reachable` | Rueckfuehrung in den Hauptpfad vor Rollenannahme. |

## Warum dieser Einstiegspunkt?

`A-MAIN-S04` prueft im Hauptpfad, ob die Zielzone fachlich erreichbar ist. Genau dort entscheidet sich, ob die normale Sequenz zu `A-MAIN-S05` fortgesetzt werden darf oder ob eine temporaere Blockade erst fachlich aufgeloest werden muss.

Die Rueckfuehrung vor `A-MAIN-S05` ist korrekt, weil der Agent die Ausfuehrungsrolle erst annehmen soll, wenn die Zielzone wieder erreichbar ist. Damit bleibt die in Task 3.5 definierte Guard Condition `A-GUARD-S05` gueltig.

## Abgrenzung zur Exception

| Fall | Einordnung | Begruendung |
| --- | --- | --- |
| `ObstacleRegion.state = temporarilyBlocked` und Freigabe moeglich | Alternative | Ziel bleibt erreichbar; Rueckfuehrung in den Hauptpfad ist definiert. |
| `ObstacleRegion.state = blocked` und keine Freigabebedingung wahr | Exception | Ziel ist im normalen Ablauf nicht erreichbar; dieser Fall gehoert zu Task 3.9. |

## Abnahmekontrolle

| Kriterium aus Task 3.8 | Erfuellung |
| --- | --- |
| `Scenario.kind = alternative` | `A-ALT-SC01` ist explizit als `alternative` festgelegt. |
| Klarer Einstiegspunkt vorhanden | Einstieg nach `A-MAIN-S04` ueber `A-ALT-R01`. |
| Bedingung vorhanden | Einstiegsguard `ObstacleRegion.state = temporarilyBlocked and TargetZone.state = reachable`. |
| Rueckfuehrung vorhanden | Rueckfuehrung ueber `A-ALT-R03` zu `A-MAIN-S05`. |
| Eigener Abschluss nicht noetig | Das Alternativszenario endet nicht separat, sondern fuehrt in den Hauptpfad zurueck. |
| Metamodellnahe Elemente vorhanden | ScenarioSteps, StepRelations, Event, Guard Conditions und StateAssertions sind ausgewiesen. |
| Keine technische Kurzschaltung | Keine API, kein Topic, kein Engine-Befehl, kein Controlleraufruf und keine RuntimeAction. |

## Konsequenz fuer Task 3.9

Task 3.9 kann den zugehoerigen Exception-Fall formulieren: Die Zielzone ist dauerhaft blockiert oder die temporaere Blockade kann nicht fachlich aufgeloest werden. Dieser Fall sollte nicht in den Hauptpfad zurueckfuehren, sondern einen sicheren Fehlerabschluss besitzen.
