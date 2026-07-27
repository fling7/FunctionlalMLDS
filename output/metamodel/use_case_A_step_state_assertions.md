# Anwendungsfall A: Erwartete StateAssertions je Hauptpfad-Schritt

Stand: 2026-07-07

Task: 3.6 `Fuer jeden Schritt A erwartete Zustandsaussagen bestimmen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

Main Scenario: `Agent reagiert auf gueltiges Ereignis und erreicht Zielzone`

## Modellierungsregel

`ScenarioStep.resultingState -> StateAssertion [0..*]` erlaubt mehrere erwartete Zustandsaussagen pro Schritt. Jede `StateAssertion` braucht genau ein identifizierbares Subjekt und einen erwarteten Zustand.

Deshalb werden zusammengesetzte fachliche Aussagen in einzelne StateAssertions zerlegt. Eine StateAssertion enthaelt keine technische Ausfuehrung, keine API-Antwort und keinen Runtime-Log, sondern nur eine beobachtbare oder erwartete fachliche Zustandsaussage.

## StateAssertions pro ScenarioStep

| Step-ID | StateAssertion-ID | `subjectRef` | `expectedState` | Zweck der Zustandsaussage |
| --- | --- | --- | --- | --- |
| `A-MAIN-S01` | `A-SA-S01-01` | `TriggerZone` | `entered` | Das gueltige Ausloeseereignis ist als betretener Ausloesebereich beobachtbar. |
| `A-MAIN-S01` | `A-SA-S01-02` | `SceneStateFlag` | `requiresReaction` | Der Szenenzustand verlangt nach dem Start-Event eine Agentenreaktion. |
| `A-MAIN-S02` | `A-SA-S02-01` | `AgentBody` | `inside(SceneBoundary)` | Der Agent befindet sich im gueltigen Szenenbereich. |
| `A-MAIN-S02` | `A-SA-S02-02` | `SceneBoundary` | `notViolated` | Die Szenengrenze ist im Hauptpfad nicht verletzt. |
| `A-MAIN-S03` | `A-SA-S03-01` | `AgentBody` | `idleOrWaiting` | Der Agent ist in einem handlungsbereiten Ausgangszustand. |
| `A-MAIN-S03` | `A-SA-S03-02` | `AgentBody` | `roleState=notBlocked` | Die Agentenrolle blockiert den Hauptpfad nicht. |
| `A-MAIN-S04` | `A-SA-S04-01` | `TargetZone` | `reachable` | Die Zielzone ist fachlich erreichbar. |
| `A-MAIN-S04` | `A-SA-S04-02` | `ObstacleRegion` | `clear` | Keine Blockade verhindert den erfolgreichen Hauptpfad. |
| `A-MAIN-S05` | `A-SA-S05-01` | `AgentBody` | `roleState=executor` | Der Agent hat die Ausfuehrungsrolle angenommen. |
| `A-MAIN-S05` | `A-SA-S05-02` | `AgentBody` | `acting` | Der Agent ist fachlich in einen aktiven Reaktionszustand gewechselt. |
| `A-MAIN-S06` | `A-SA-S06-01` | `AgentBody` | `movingTo(TargetZone)` | Der Agent fuehrt die zielgerichtete Bewegung oder Handlung aus. |
| `A-MAIN-S06` | `A-SA-S06-02` | `TargetZone` | `occupied` | Die Zielzone wird im Hauptpfad durch die Agentenhandlung erreicht oder belegt. |
| `A-MAIN-S07` | `A-SA-S07-01` | `AgentBody` | `at(TargetZone)` | Der Agent befindet sich an der Zielzone. |
| `A-MAIN-S07` | `A-SA-S07-02` | `TargetZone` | `reached` | Die Zielzone ist als erreicht markiert. |
| `A-MAIN-S08` | `A-SA-S08-01` | `ObservationPoint` | `verified` | Der erreichte Zielzustand wurde beobachtbar verifiziert. |
| `A-MAIN-S08` | `A-SA-S08-02` | `SceneStateFlag` | `resolved` | Die Szene fordert nach erfolgreicher Verifikation keine unmittelbare Reaktion mehr. |
| `A-MAIN-S09` | `A-SA-S09-01` | `FeedbackSignal` | `confirmed` | Die Ergebnisrueckmeldung wurde bestaetigt. |
| `A-MAIN-S09` | `A-SA-S09-02` | `AgentBody` | `roleState=completed` | Der Agentenablauf ist fachlich abgeschlossen. |

## Kompakte Sicht pro Schritt

| Step-ID | Anzahl StateAssertions | Fachlicher Schwerpunkt |
| --- | --- | --- |
| `A-MAIN-S01` | 2 | Start-Ereignis und Reaktionsbedarf |
| `A-MAIN-S02` | 2 | gueltiger Szenenbereich |
| `A-MAIN-S03` | 2 | Handlungsbereitschaft |
| `A-MAIN-S04` | 2 | Zielerreichbarkeit |
| `A-MAIN-S05` | 2 | Rollenwechsel |
| `A-MAIN-S06` | 2 | zielgerichtete Handlung |
| `A-MAIN-S07` | 2 | Zielerreichung |
| `A-MAIN-S08` | 2 | Verifikation |
| `A-MAIN-S09` | 2 | Rueckmeldung und Abschluss |

## Rueckbindung an Ziel- und Nachbedingungen

| StateAssertion-ID | Bezug | Bemerkung |
| --- | --- | --- |
| `A-SA-S02-01` | `A-G2`, `A-Q2` | Agent bleibt im gueltigen Szenenbereich. |
| `A-SA-S05-01` | `A-G3`, `A-O4` | Agent nimmt die passende Rolle an. |
| `A-SA-S07-01` | `A-G5`, `A-O2`, `A-Q1` | Agent erreicht die Zielzone. |
| `A-SA-S07-02` | `A-G5`, `A-O3`, `A-Q1` | Zielzone ist als erreicht markiert. |
| `A-SA-S08-01` | `A-G6`, `A-O6`, `A-Q4` | Zielzustand ist verifiziert. |
| `A-SA-S09-01` | `A-G7`, `A-O7`, `A-Q5` | Rueckmeldung ist bestaetigt. |
| `A-SA-S09-02` | `A-O4`, `A-Q3` | Agentenablauf ist abgeschlossen und nicht blockiert. |

## Hinweise zur spaeteren Modellierung

Die Ausdruecke `inside(SceneBoundary)`, `movingTo(TargetZone)` und `at(TargetZone)` stehen bewusst als fachliche Zustandsstrings in `StateAssertion.expectedState`. Sie sind keine Implementierungsbefehle. Falls spaeter ein raeumliches Ergaenzungsmodell eingefuehrt wird, koennen diese Strings durch strukturiertere Location- oder Relationselemente ersetzt werden, ohne die fachliche Bedeutung der ScenarioSteps zu aendern.

## Abnahmekontrolle

| Kriterium aus Task 3.6 | Erfuellung |
| --- | --- |
| StateAssertions pro Schritt vorhanden | `A-MAIN-S01` bis `A-MAIN-S09` haben jeweils zwei StateAssertions. |
| Jede StateAssertion hat ein Subjekt | Jede Zeile enthaelt genau ein `subjectRef`. |
| Jede StateAssertion hat einen erwarteten Zustand | Jede Zeile enthaelt genau einen `expectedState`-Wert. |
| Kardinalitaet `0..*` eingehalten | Mehrere StateAssertions pro Schritt sind zulaessig; kein Schritt benoetigt eine kuenstliche Zusammenfassung. |
| Konsistenz zu Ziel und Postconditions vorhanden | Zentrale Zielaussagen werden auf `A-G2` bis `A-G7` und `A-O2` bis `A-O7` rueckgebunden. |
| Keine technische Kurzschaltung | Keine StateAssertion referenziert API, Topic, Engine-Befehl, Controlleraufruf oder RuntimeAction. |

## Konsequenz fuer Task 3.7

Task 3.7 kann nun die `StepRelation`-Sequenz des Hauptszenarios definieren. Die StateAssertions helfen dabei, die Reihenfolge zu begruenden:

- Verifikation folgt erst nach Zielerreichung.
- Rueckmeldung folgt erst nach Verifikation.
- Rollenwechsel und Zielhandlung folgen erst nach Start, Bereichspruefung, Bereitschaft und Zielerreichbarkeit.
