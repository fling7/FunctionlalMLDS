# Anwendungsfall A: Guard Conditions je Hauptpfad-Schritt

Stand: 2026-07-07

Task: 3.5 `Fuer jeden Schritt A die Guard Conditions bestimmen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

Main Scenario: `Agent reagiert auf gueltiges Ereignis und erreicht Zielzone`

## Modellierungsregel

`ScenarioStep.guard -> Condition [0..1]` erlaubt pro Schritt hoechstens eine Guard Condition. Deshalb werden mehrere fachliche Voraussetzungen, wenn noetig, in einem einzigen pruefbaren `Condition.expression` zusammengefasst.

Ein Guard wird nur gesetzt, wenn er den Ablauf beeinflusst:

- Der Schritt darf nur bei erfuellter Bedingung im Hauptpfad fortgesetzt werden.
- Bei Nichterfuellung entsteht ein Alternativ- oder Exception-Pfad.
- Reine Ergebnisbeobachtungen erhalten keinen Guard, wenn sie nur einen Zustand feststellen und nicht selbst verzweigen.

## Guard Conditions pro ScenarioStep

| Step-ID | ScenarioStep-Kandidat | Guard-ID | `Condition.kind` | `Condition.expression` | Warum hier ein Guard oder kein Guard? |
| --- | --- | --- | --- | --- | --- |
| `A-MAIN-S01` | Ein gueltiges Ausloeseereignis wird fachlich festgestellt. | `A-GUARD-S01` | `guard` | `Event.kind = spatial and Event.expression = entered(SceneParticipant, TriggerZone)` | Der Guard trennt den Hauptpfadstart ueber Zoneneintritt von alternativen Startformen wie `A-E2`. |
| `A-MAIN-S02` | Der Agent wird im gueltigen Szenenbereich festgestellt. | `A-GUARD-S02` | `spatial` | `inside(AgentBody, SceneBoundary) = true` | Bei Nichterfuellung entsteht ein Exception-Pfad wegen verletzter Szenengrenze. |
| `A-MAIN-S03` | Der Agent wird als handlungsbereit festgestellt. | `A-GUARD-S03` | `pre` | `AgentBody.state in {idle, waiting} and AgentBody.roleState != blocked` | Nur ein handlungsbereiter, nicht blockierter Agent darf in die Reaktion uebergehen. |
| `A-MAIN-S04` | Die Zielzone wird als fachlich erreichbar festgestellt. | `A-GUARD-S04` | `guard` | `TargetZone.state = reachable and ObstacleRegion.state != blocked` | Der Guard entscheidet zwischen Hauptpfad, temporaerer Blockade-Alternative und dauerhafter Blockade-Exception. |
| `A-MAIN-S05` | Der Agent nimmt die Ausfuehrungsrolle an. | `A-GUARD-S05` | `guard` | `inside(AgentBody, SceneBoundary) = true and AgentBody.roleState != blocked and TargetZone.state = reachable` | Der Rollenwechsel ist nur sinnvoll, wenn die zuvor geprueften Hauptpfadbedingungen noch gelten. |
| `A-MAIN-S06` | Der Agent fuehrt die zielgerichtete Szenenhandlung aus. | `A-GUARD-S06` | `guard` | `AgentBody.roleState = executor and TargetZone.state = reachable and ObstacleRegion.state != blocked` | Die Zielhandlung darf erst nach Rollenannahme und bei weiterhin erreichbarer Zielzone erfolgen. |
| `A-MAIN-S07` | Der Agent erreicht die Zielzone. | keine Guard Condition | - | - | Der Schritt ist eine resultierende Beobachtung der vorherigen Handlung; die erwarteten Zustaende werden in Task 3.6 modelliert. |
| `A-MAIN-S08` | Der Zielzustand wird beobachtbar verifiziert. | `A-GUARD-S08` | `post` | `at(AgentBody, TargetZone) = true and TargetZone.state in {occupied, reached}` | Die Verifikation darf nur erfolgen, wenn der Zielzustand fachlich beobachtbar erreicht wurde. |
| `A-MAIN-S09` | Die Ergebnisrueckmeldung wird bestaetigt. | `A-GUARD-S09` | `post` | `ObservationPoint.state = verified and FeedbackSignal.state = shown` | Die Bestaetigung ist nur zulaessig, nachdem der Zielzustand verifiziert und eine Rueckmeldung angezeigt wurde. |

## Rueckbindung an bestehende Bedingungen

| Guard-ID | Bezug aus frueheren Tasks | Bemerkung |
| --- | --- | --- |
| `A-GUARD-S01` | `A-P6`, `A-E1` | Erlaubt den raeumlichen Hauptpfadstart. |
| `A-GUARD-S02` | `A-P3`, `A-C2`, `A-Q2` | Verhindert, dass der Erfolgspfad ausserhalb der Szenengrenze weiterlaeuft. |
| `A-GUARD-S03` | `A-P2`, `A-C1`, `A-Q3` | Verhindert Rollenwechsel bei blockiertem Agenten. |
| `A-GUARD-S04` | `A-P4`, `A-C3`, `A-Q7` | Entscheidender Guard fuer Hauptpfad versus Blockade. |
| `A-GUARD-S05` | `A-P2`, `A-P3`, `A-P4` | Fasst die fuer Rollenannahme weiter geltenden Voraussetzungen zusammen. |
| `A-GUARD-S06` | `A-S2`, `A-C3`, `A-Q1` | Schuetzt die zielgerichtete Handlung vor Ausfuehrung ohne passende Rolle oder erreichbares Ziel. |
| `A-GUARD-S08` | `A-C7`, `A-G5`, `A-Q4` | Verifikation ist nur nach erreichter Zielposition sinnvoll. |
| `A-GUARD-S09` | `A-C8`, `A-G7`, `A-Q5` | Bestaetigung setzt Verifikation und sichtbare Rueckmeldung voraus. |

## Keine Guard Condition bei `A-MAIN-S07`

`A-MAIN-S07` erhaelt bewusst keinen Guard. Der Schritt beschreibt, dass der Agent die Zielzone erreicht. Die Zulassigkeit dieser Zielerreichung wurde bereits in `A-GUARD-S06` geprueft. Der erreichte Zustand selbst wird in Task 3.6 als `StateAssertion` modelliert.

## Abnahmekontrolle

| Kriterium aus Task 3.5 | Erfuellung |
| --- | --- |
| Conditionliste pro Schritt vorhanden | `A-MAIN-S01` bis `A-MAIN-S09` haben je eine Zeile mit Guard oder begruendet leerem Guard. |
| Kardinalitaet `0..1` eingehalten | Jeder Schritt besitzt hoechstens eine Guard Condition. |
| Guards sind optional | `A-MAIN-S07` bleibt ohne Guard, weil keine Ablaufentscheidung an diesem Schritt liegt. |
| Guards nur bei Ablaufrelevanz gesetzt | Jeder gesetzte Guard verhindert unzulaessige Fortsetzung oder trennt Hauptpfad von Alternative/Exception. |
| Jede Condition ist pruefbar | Jede gesetzte Guard Condition besitzt einen konkreten Ausdruck. |
| Keine technische Kurzschaltung | Keine Guard Condition referenziert API, Topic, Engine-Befehl, Controlleraufruf oder RuntimeAction. |

## Konsequenz fuer Task 3.6

Task 3.6 kann nun die erwarteten StateAssertions pro Schritt bestimmen. Besonders relevant sind:

- `A-MAIN-S05`: `AgentBody.roleState = executor`,
- `A-MAIN-S07`: `at(AgentBody, TargetZone) = true` und `TargetZone.state = reached`,
- `A-MAIN-S08`: `ObservationPoint.state = verified`,
- `A-MAIN-S09`: `FeedbackSignal.state = confirmed`.
