# Anwendungsfall A: Ausloesende Events je Hauptpfad-Schritt

Stand: 2026-07-07

Task: 3.4 `Fuer jeden Schritt A die ausloesenden Events bestimmen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

Main Scenario: `Agent reagiert auf gueltiges Ereignis und erreicht Zielzone`

## Modellierungsregel

`ScenarioStep.triggeredBy -> Event [0..*]` erlaubt, dass ein Schritt keine direkte Event-Referenz besitzt. Ein Event wird deshalb nur dann zugeordnet, wenn der Schritt durch ein fachlich benennbares Ereignis ausgeloest wird.

Reine Sequenzfortschritte bekommen kein kuenstliches Event. Sie werden spaeter ueber `StepRelation.kind = sequence` verbunden und erhalten ihre fachliche Begrenzung ueber Guard-Conditions oder StateAssertions.

Fuer den Hauptpfad wird `A-E1` als Start-Event gewaehlt: Ein Szenenteilnehmer betritt die Ausloesezone. Der alternative Start ueber ein externes Signal (`A-E2`) bleibt dem Alternativfall `A-ALT1` vorbehalten.

## Eventzuordnung pro ScenarioStep

| Step-ID | ScenarioStep-Kandidat | Direkte Events fuer `triggeredBy` | Event-Art | Event-Ausdruck | Begruendung |
| --- | --- | --- | --- | --- | --- |
| `A-MAIN-S01` | Ein gueltiges Ausloeseereignis wird fachlich festgestellt. | `A-E1` | `spatial` | `entered(SceneParticipant, TriggerZone)` | Der Hauptpfad startet durch ein raeumliches Betreten der Ausloesezone. |
| `A-MAIN-S02` | Der Agent wird im gueltigen Szenenbereich festgestellt. | keine direkte Event-Referenz | - | - | Der Schritt prueft einen Zustand nach dem Start-Event; kein neues Ereignis ist erforderlich. |
| `A-MAIN-S03` | Der Agent wird als handlungsbereit festgestellt. | keine direkte Event-Referenz | - | - | Der Schritt beobachtet die Bereitschaft des Agenten als Voraussetzung; kein neues Ereignis ist erforderlich. |
| `A-MAIN-S04` | Die Zielzone wird als fachlich erreichbar festgestellt. | keine direkte Event-Referenz | - | - | Der Schritt prueft Erreichbarkeit; Blockade-Events gehoeren zu Alternative oder Exception, nicht zum normalen Hauptpfad. |
| `A-MAIN-S05` | Der Agent nimmt die Ausfuehrungsrolle an. | keine direkte Event-Referenz | - | - | Die Rollenannahme ist die systemische Reaktion auf den bereits festgestellten Start und die erfuellten Bedingungen. |
| `A-MAIN-S06` | Der Agent fuehrt die zielgerichtete Szenenhandlung aus. | keine direkte Event-Referenz | - | - | Die Handlung folgt aus der Sequenz und den Guards; ein zusaetzliches Event wuerde dieselbe Ursache doppelt modellieren. |
| `A-MAIN-S07` | Der Agent erreicht die Zielzone. | keine direkte Event-Referenz | - | - | Die Zielerreichung ist ein resultierender Zustand der vorherigen Handlung, kein eigenstaendiger Ausloeser. |
| `A-MAIN-S08` | Der Zielzustand wird beobachtbar verifiziert. | `A-E7` | `signal` | `verified(ObservationPoint)` | Die Verifikation wird im Hauptpfad als fachliches Beobachtungssignal modelliert. |
| `A-MAIN-S09` | Die Ergebnisrueckmeldung wird bestaetigt. | `A-E8` | `signal` | `shown(FeedbackSignal)` | Die sichtbare Rueckmeldung ist das Signal, das den beobachtbaren Abschluss des Hauptpfads traegt. |

## Nicht dem Hauptpfad direkt zugeordnete Events

| Event-ID | Event-Art | Event-Ausdruck | Warum nicht direkt im Hauptpfad? | Spaetere Verwendung |
| --- | --- | --- | --- | --- |
| `A-E2` | `signal` | `signalEmitted(ExternalSignalSource)` | Dieser Start ist als Alternative zu `A-E1` vorbereitet. | `A-ALT1` |
| `A-E3` | `environment` | `stateChanged(InteractionAsset, locked|unavailable)` | Dieses Ereignis beschreibt eine Objektstoerung, nicht den erfolgreichen Normalpfad. | `A-EX4` oder objektbezogene Alternative |
| `A-E4` | `environment` | `stateChanged(ObstacleRegion, blocked|temporarilyBlocked)` | Dieses Ereignis beschreibt Blockade oder temporaere Blockade. | `A-ALT2`, `A-EX3` |
| `A-E5` | `signal` | `markerVisible(InstructionMarker)` | Der Instruktionsmarker ist optional und nicht Teil des schlanken Hauptpfads. | `A-ALT4` |
| `A-E6` | `spatial` | `boundaryStateChanged(AgentBody, SceneBoundary)` | Grenzverletzungen gehoeren nicht zum erfolgreichen Hauptpfad. | `A-EX1` |

## Konsistenz zu `ScenarioStep.kind`

| Step-ID | Schrittart aus Task 3.3 | Evententscheidung |
| --- | --- | --- |
| `A-MAIN-S01` | `environmentObservation` | Hat ein direktes Event, weil der Schritt ein ausloesendes Ereignis feststellt. |
| `A-MAIN-S02` | `environmentObservation` | Kein direktes Event, weil ein Zustand beobachtet wird. |
| `A-MAIN-S03` | `environmentObservation` | Kein direktes Event, weil ein Zustand beobachtet wird. |
| `A-MAIN-S04` | `environmentObservation` | Kein direktes Event, weil ein Zustand beobachtet wird. |
| `A-MAIN-S05` | `systemResponse` | Kein direktes Event, weil die Reaktion sequenziell aus Start-Event und Guards folgt. |
| `A-MAIN-S06` | `systemResponse` | Kein direktes Event, weil die Handlung sequenziell aus der Rollenannahme folgt. |
| `A-MAIN-S07` | `environmentObservation` | Kein direktes Event, weil ein resultierender Zustand beobachtet wird. |
| `A-MAIN-S08` | `environmentObservation` | Hat ein direktes Event, weil die Verifikation selbst als Beobachtungssignal modelliert wird. |
| `A-MAIN-S09` | `environmentObservation` | Hat ein direktes Event, weil die Rueckmeldung als beobachtbares Signal modelliert wird. |

## Abnahmekontrolle

| Kriterium aus Task 3.4 | Erfuellung |
| --- | --- |
| Eventliste pro Schritt vorhanden | `A-MAIN-S01` bis `A-MAIN-S09` haben je eine Zeile mit direkter Eventliste oder begruendet leerer Eventliste. |
| Jeder zugeordnete Event hat Art | `A-E1`, `A-E7` und `A-E8` besitzen jeweils eine Event-Art. |
| Jeder zugeordnete Event hat Ausdruck | `A-E1`, `A-E7` und `A-E8` besitzen jeweils einen Event-Ausdruck. |
| Keine kuenstlichen Events erzeugt | Sequenz- und Zustandspruefschritte ohne eigenes Ereignis bleiben ohne direkte Event-Referenz. |
| Alternative und Exception getrennt | `A-E2` bis `A-E6` werden fuer spaetere Alternativen oder Exceptions reserviert. |
| Anschluss an Task 3.5 vorhanden | Die Evententscheidungen machen sichtbar, wo Guards noetig werden: insbesondere nach `A-MAIN-S01` bis `A-MAIN-S04`. |

## Konsequenz fuer Task 3.5

Task 3.5 kann die Guard Conditions bestimmen. Besonders relevant sind:

- `A-MAIN-S02`: Agent muss innerhalb des gueltigen Szenenbereichs sein.
- `A-MAIN-S03`: Agent muss handlungsbereit sein.
- `A-MAIN-S04`: Zielzone muss erreichbar sein.
- `A-MAIN-S05` und `A-MAIN-S06`: Reaktion und Handlung duerfen erst nach gueltigem Start und erfuellten Bedingungen erfolgen.
