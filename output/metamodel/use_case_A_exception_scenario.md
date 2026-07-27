# Anwendungsfall A: Exception-Szenario

Stand: 2026-07-07

Task: 3.9 `Exception-Szenario A formulieren`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

Exception Scenario: `Dauerhafte Blockade verhindert Zielerreichung`

## Szenario-Festlegung

| Feld | Wert |
| --- | --- |
| Scenario-ID | `A-EX-SC01` |
| `Scenario.kind` | `exception` |
| Name | `Dauerhafte Blockade verhindert Zielerreichung` |
| Einstiegspunkt im Hauptpfad | nach `A-MAIN-S04` |
| Rueckfuehrung in den Hauptpfad | keine |
| Bezug zu vorbereitetem Exception-Fall | `A-EX3` |
| Ziel des Exception-Szenarios | Der normale Zielpfad wird sicher beendet, weil die Zielzone dauerhaft nicht erreichbar ist. |

## Fehlerausloeser und Bedingung

| Aspekt | Modellierung |
| --- | --- |
| Fehlerausloeser | `A-E4`: `stateChanged(ObstacleRegion, blocked|temporarilyBlocked)` |
| Exception-Einstiegskante | `A-MAIN-S04 -> A-EX-S01` |
| `StepRelation.kind` fuer Einstieg | `exception` |
| Guard der Einstiegskante | `ObstacleRegion.state = blocked` |
| Verletzte Hauptpfadbedingung | `A-GUARD-S04`: `TargetZone.state = reachable and ObstacleRegion.state != blocked` |
| Verletzte Nachbedingung | `A-Q1` und `A-Q7` koennen im normalen Ablauf nicht erfuellt werden. |

## Exception ScenarioSteps

| Step-Nr. | Step-ID | ScenarioStep-Kandidat | `ScenarioStep.kind` | Event | Guard | Erwartete StateAssertions |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `A-EX-S01` | Die dauerhafte Blockade der Zielzone wird festgestellt. | `environmentObservation` | `A-E4` | `ObstacleRegion.state = blocked` | `ObstacleRegion = blocked`; `TargetZone = unreached` |
| 2 | `A-EX-S02` | Der Agent wird am Fortsetzen des Zielpfads gehindert. | `systemResponse` | kein eigenes Event | `ObstacleRegion.state = blocked` | `AgentBody = waiting`; `AgentBody.roleState = blocked` |
| 3 | `A-EX-S03` | Der nicht erreichbare Zielzustand wird als Fehlerabschluss rueckgemeldet. | `environmentObservation` | kein eigenes Event | `AgentBody.roleState = blocked` | `FeedbackSignal = failed`; `SceneStateFlag = requiresReaction` |

## StepRelations des Exception-Szenarios

| Relation-ID | Source-Step | Target-Step | `StepRelation.kind` | Guard | Zweck |
| --- | --- | --- | --- | --- | --- |
| `A-EX-R01` | `A-MAIN-S04` | `A-EX-S01` | `exception` | `ObstacleRegion.state = blocked` | Einstieg aus der Zielerreichbarkeitspruefung in den Exception-Pfad. |
| `A-EX-R02` | `A-EX-S01` | `A-EX-S02` | `sequence` | keine | Nach Feststellung der Blockade wird der Agent sicher am Zielpfad-Fortschritt gehindert. |
| `A-EX-R03` | `A-EX-S02` | `A-EX-S03` | `sequence` | keine | Nach dem sicheren Haltezustand wird der Fehlerabschluss beobachtbar rueckgemeldet. |

## Sicherer Endzustand

| StateAssertion-ID | `subjectRef` | `expectedState` | Bedeutung |
| --- | --- | --- | --- |
| `A-EX-SA01` | `ObstacleRegion` | `blocked` | Die Ursache der Exception bleibt beobachtbar. |
| `A-EX-SA02` | `TargetZone` | `unreached` | Das Erfolgsziel wurde nicht erreicht und wird nicht faelschlich als erreicht markiert. |
| `A-EX-SA03` | `AgentBody` | `waiting` | Der Agent setzt die Zielhandlung nicht unzulaessig fort. |
| `A-EX-SA04` | `AgentBody` | `roleState=blocked` | Die Agentenrolle ist fuer den Hauptpfad gesperrt. |
| `A-EX-SA05` | `FeedbackSignal` | `failed` | Der Fehlerabschluss ist beobachtbar rueckgemeldet. |
| `A-EX-SA06` | `SceneStateFlag` | `requiresReaction` | Die Szene verlangt Korrektur, Aufloesung oder manuelle Entscheidung. |

## Warum keine Rueckfuehrung?

Eine Rueckfuehrung in den Hauptpfad waere nur zulaessig, wenn die Blockade fachlich aufgeloest ist und `TargetZone.state = reachable` wieder gilt. Dieser Fall wurde in Task 3.8 als Alternative modelliert.

Im Exception-Szenario bleibt `ObstacleRegion.state = blocked`. Dadurch waere eine Rueckfuehrung zu `A-MAIN-S05` inkonsistent, weil `A-GUARD-S05` weiterhin voraussetzt, dass die Zielzone erreichbar ist.

## Abgrenzung zur Alternative

| Fall | Einordnung | Begruendung |
| --- | --- | --- |
| `ObstacleRegion.state = temporarilyBlocked` und spaetere Freigabe | Alternative | Ziel bleibt erreichbar; Rueckfuehrung zu `A-MAIN-S05` ist definiert. |
| `ObstacleRegion.state = blocked` ohne Freigabe | Exception | Ziel ist im normalen Ablauf nicht erreichbar; sicherer Fehlerabschluss erforderlich. |

## Abnahmekontrolle

| Kriterium aus Task 3.9 | Erfuellung |
| --- | --- |
| `Scenario.kind = exception` | `A-EX-SC01` ist explizit als `exception` festgelegt. |
| Fehlerausloeser vorhanden | `A-E4` ist als Fehlerausloeser angegeben. |
| Systemreaktion vorhanden | `A-EX-S02` beschreibt die fachliche Reaktion: Agent wird sicher am Fortsetzen gehindert. |
| Sicherer Endzustand vorhanden | `A-EX-SA01` bis `A-EX-SA06` beschreiben beobachtbare Abschlusszustaende. |
| Keine Rueckfuehrung in den Hauptpfad | Der Pfad endet mit Fehlerabschluss, weil `ObstacleRegion.state = blocked` bestehen bleibt. |
| Metamodellnahe Elemente vorhanden | ScenarioSteps, StepRelations, Event, Guard Conditions und StateAssertions sind ausgewiesen. |
| Keine technische Kurzschaltung | Keine API, kein Topic, kein Engine-Befehl, kein Controlleraufruf und keine RuntimeAction. |

## Konsequenz fuer Task 3.10

Task 3.10 kann pruefen, ob fuer Anwendungsfall A parallele oder nebenlaeufige Agentenablaeufe benoetigt werden. Das bisherige Haupt-, Alternativ- und Exception-Szenario ist sequenziell modellierbar; eine `ParallelGroup` ist daher nur noetig, wenn eine gleichzeitige Beobachtung oder mehragentige Handlung fachlich gefordert wird.
