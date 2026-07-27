# Anwendungsfall A: Hauptszenario als ScenarioStep-Kandidaten

Stand: 2026-07-07

Task: 3.2 `Hauptszenario A in nummerierte Schritte zerlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

Main Scenario: `Agent reagiert auf gueltiges Ereignis und erreicht Zielzone`

## Modellierungsregel

Dieser Task zerlegt nur den erfolgreichen Hauptpfad in nummerierte `ScenarioStep`-Kandidaten. Jeder Schritt enthaelt genau eine fachliche Aussage.

Noch nicht festgelegt werden:

- Schrittart (`actorIntent`, `systemResponse`, `environmentObservation`),
- ausloesende Events,
- Guard Conditions,
- resultierende StateAssertions,
- CapabilityUses,
- RuntimeBindings oder RuntimeActions.

Diese Punkte folgen in den Tasks 3.3 bis 3.8.

## Hauptpfad

| Step-Nr. | Step-ID | ScenarioStep-Kandidat | Einzelaussage | Warum genau ein fachlicher Schritt? |
| --- | --- | --- | --- | --- |
| 1 | `A-MAIN-S01` | Ein gueltiges Ausloeseereignis wird fachlich festgestellt. | Ausloeseereignis festgestellt | Der Schritt beschreibt nur das Vorliegen eines gueltigen Ausloesers. |
| 2 | `A-MAIN-S02` | Der Agent wird im gueltigen Szenenbereich festgestellt. | Agent im Szenenbereich | Der Schritt beschreibt nur die raeumliche Zulaessigkeit des Agenten. |
| 3 | `A-MAIN-S03` | Der Agent wird als handlungsbereit festgestellt. | Agent handlungsbereit | Der Schritt beschreibt nur die fachliche Bereitschaft des Agenten. |
| 4 | `A-MAIN-S04` | Die Zielzone wird als fachlich erreichbar festgestellt. | Zielzone erreichbar | Der Schritt beschreibt nur die Erreichbarkeit des Zielbereichs. |
| 5 | `A-MAIN-S05` | Der Agent nimmt die Ausfuehrungsrolle an. | Rolle angenommen | Der Schritt beschreibt nur den Rollenwechsel des Agenten. |
| 6 | `A-MAIN-S06` | Der Agent fuehrt die zielgerichtete Szenenhandlung aus. | Zielhandlung ausgefuehrt | Der Schritt beschreibt nur die fachliche Handlung auf dem Weg zum Ziel. |
| 7 | `A-MAIN-S07` | Der Agent erreicht die Zielzone. | Zielzone erreicht | Der Schritt beschreibt nur die Zielerreichung durch den Agenten. |
| 8 | `A-MAIN-S08` | Der Zielzustand wird beobachtbar verifiziert. | Zielzustand verifiziert | Der Schritt beschreibt nur die fachliche Verifikation des erreichten Zustands. |
| 9 | `A-MAIN-S09` | Die Ergebnisrueckmeldung wird bestaetigt. | Rueckmeldung bestaetigt | Der Schritt beschreibt nur die Bestaetigung der beobachtbaren Rueckmeldung. |

## Vorlaeufige Sequenz

| Von | Nach | Vorlaeufige Beziehung |
| --- | --- | --- |
| `A-MAIN-S01` | `A-MAIN-S02` | normaler Hauptpfad |
| `A-MAIN-S02` | `A-MAIN-S03` | normaler Hauptpfad |
| `A-MAIN-S03` | `A-MAIN-S04` | normaler Hauptpfad |
| `A-MAIN-S04` | `A-MAIN-S05` | normaler Hauptpfad |
| `A-MAIN-S05` | `A-MAIN-S06` | normaler Hauptpfad |
| `A-MAIN-S06` | `A-MAIN-S07` | normaler Hauptpfad |
| `A-MAIN-S07` | `A-MAIN-S08` | normaler Hauptpfad |
| `A-MAIN-S08` | `A-MAIN-S09` | normaler Hauptpfad |

Die eigentlichen `StepRelation.kind`-Werte werden erst in Task 3.7 festgelegt.

## Abgrenzung zu Alternativen und Exceptions

Der Hauptpfad enthaelt noch keine Alternativen und keine Exceptions. Die in Task 2.10 vorbereiteten Faelle werden spaeter als Verzweigungen ergaenzt, ohne den linearen Erfolgspfad aus diesem Task zu vermischen.

## Abnahmekontrolle

| Kriterium aus Task 3.2 | Erfuellung |
| --- | --- |
| Sequenz von `ScenarioStep`-Kandidaten vorhanden | `A-MAIN-S01` bis `A-MAIN-S09` bilden die Hauptpfadsequenz. |
| Jeder Schritt hat genau eine fachliche Aussage | Jede Zeile besitzt eine einzelne Schrittaussage und eine kurze Einzelaussage. |
| Hauptpfad ohne Alternative und Exception | Der Abschnitt `Hauptpfad` enthaelt nur den erfolgreichen linearen Ablauf. |
| Technische Umsetzung nicht vorweggenommen | Keine Zeile enthaelt API, Topic, Engine-Befehl, Controlleraufruf oder RuntimeAction. |
| Anschluss an Folge-Tasks vorhanden | Schrittart, Events, Guards, StateAssertions und Relations sind explizit fuer 3.3 bis 3.7 offen gehalten. |

## Konsequenz fuer Task 3.3

Task 3.3 kann fuer jeden Schritt bestimmen, ob er als `actorIntent`, `systemResponse` oder `environmentObservation` einzuordnen ist.
