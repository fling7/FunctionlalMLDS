# Anwendungsfall A: Event-Instanzen

Stand: 2026-07-07

Task: 4.7 `Event-Instanzen fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

`ScenarioStep -> Event` ist eine Assoziation mit `triggeredBy [0..*]`. Ein Schritt darf also kein, ein oder mehrere ausloesende Ereignisse referenzieren. Umgekehrt darf ein fachlich gleiches Event von mehreren Schritten oder Pfaden verwendet werden, wenn es denselben beobachtbaren Ausloeser beschreibt.

Events werden nur dort einem Schritt zugeordnet, wo der Schritt tatsaechlich durch ein benennbares Ereignis ausgeloest wird. Reine Sequenz-, Zustandspruefungs- oder Ergebnisbeobachtungsschritte erhalten kein kuenstliches Event.

## Angelegte Event-Instanzen

| Event-ID | Metamodellklasse | `uuid` | `shortName` | `Event.kind` | `Event.expression` | Status | Begruendung |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `A-E1` | `Event` | `A-E1` | `SceneParticipantBetrittTriggerZone` | `spatial` | `entered(SceneParticipant, TriggerZone)` | genutzt | Startet den Hauptpfad als raeumliches Ausloeseereignis. |
| `A-E2` | `Event` | `A-E2` | `ExternesSignalEmittiert` | `signal` | `signalEmitted(ExternalSignalSource)` | ungenutzt vorbereitet | Alternativer Start ist vorbereitet, aber im aktuellen Scenario-Set noch nicht formalisiert. |
| `A-E3` | `Event` | `A-E3` | `InteraktionsobjektStoerung` | `environment` | `stateChanged(InteractionAsset, locked|unavailable)` | ungenutzt vorbereitet | Objektstoerung gehoert zu einer spaeteren objektbezogenen Alternative oder Exception. |
| `A-E4` | `Event` | `A-E4` | `BlockadezustandGeaendert` | `environment` | `stateChanged(ObstacleRegion, blocked|temporarilyBlocked)` | genutzt | Startet die temporaere Blockade-Alternative und die dauerhafte Blockade-Exception. |
| `A-E5` | `Event` | `A-E5` | `InstruktionsmarkerSichtbar` | `signal` | `markerVisible(InstructionMarker)` | ungenutzt vorbereitet | Optionaler Instruktionsmarker ist nicht Teil des aktuellen schlanken Scenario-Sets. |
| `A-E6` | `Event` | `A-E6` | `SzenengrenzeGeaendert` | `spatial` | `boundaryStateChanged(AgentBody, SceneBoundary)` | ungenutzt vorbereitet | Grenzverletzung ist als Exception-Fall vorbereitet, aber aktuell nicht formalisiert. |
| `A-E7` | `Event` | `A-E7` | `BeobachtungspunktVerifiziert` | `signal` | `verified(ObservationPoint)` | genutzt | Loest die beobachtbare Zielzustandsverifikation im Hauptpfad aus. |
| `A-E8` | `Event` | `A-E8` | `RueckmeldungAngezeigt` | `signal` | `shown(FeedbackSignal)` | genutzt | Traegt den beobachtbaren Abschluss durch sichtbare Rueckmeldung. |

## `triggeredBy`-Zuordnung zu ScenarioSteps

| Beziehung-ID | ScenarioStep | Event | Beziehung | Bewertung |
| --- | --- | --- | --- | --- |
| `A-TE-01` | `A-MAIN-S01` | `A-E1` | `triggeredBy` | gueltig: Hauptpfad startet durch raeumliches Ereignis. |
| `A-TE-02` | `A-MAIN-S08` | `A-E7` | `triggeredBy` | gueltig: Verifikation wird als Beobachtungssignal modelliert. |
| `A-TE-03` | `A-MAIN-S09` | `A-E8` | `triggeredBy` | gueltig: Rueckmeldung wird als Signal des Abschlusses modelliert. |
| `A-TE-04` | `A-ALT-S01` | `A-E4` | `triggeredBy` | gueltig: temporaere Blockade wird durch Blockadezustandsaenderung erkannt. |
| `A-TE-05` | `A-EX-S01` | `A-E4` | `triggeredBy` | gueltig: dauerhafte Blockade nutzt denselben fachlichen Ereignistyp mit anderer Guard-Bedingung. |

## Schritte ohne direkte Event-Referenz

| ScenarioStep | Grund fuer leeres `triggeredBy` |
| --- | --- |
| `A-MAIN-S02` | Zustand nach Start-Event; kein neues Ereignis erforderlich. |
| `A-MAIN-S03` | Bereitschaftszustand wird beobachtet; kein neues Ereignis erforderlich. |
| `A-MAIN-S04` | Zielerreichbarkeit wird geprueft; Blockadeereignisse verzweigen in Alternative oder Exception. |
| `A-MAIN-S05` | Rollenannahme folgt aus Sequenz und Guards, nicht aus neuem Event. |
| `A-MAIN-S06` | Zielhandlung folgt aus Rollenannahme und Guards. |
| `A-MAIN-S07` | Zielerreichung ist resultierender Zustand der Handlung. |
| `A-ALT-S02` | Aufhebung wird als Folge der Alternative beobachtet; kein eigenes Event im aktuellen Modell. |
| `A-EX-S02` | Systemische Reaktion auf bereits festgestellte Blockade. |
| `A-EX-S03` | Fehlerabschluss folgt aus Exception-Sequenz. |

## Ungenutzte, aber bewusst erhaltene Events

| Event-ID | Status | Warum behalten? | Spaetere Einhaengung |
| --- | --- | --- | --- |
| `A-E2` | ungenutzt vorbereitet | Ermoeglicht einen alternativen Start ueber externe Signale, ohne den aktuellen Hauptpfad aufzublasen. | Optionales alternatives Scenario `A-ALT1` oder Erweiterungsmodell fuer externe Ereignisquellen. |
| `A-E3` | ungenutzt vorbereitet | Interaktionsobjektstoerungen werden fuer Beispiel B und objektbezogene Agentenszenen relevant. | Objekt-/Interaktionsmodell oder spaetere Exception `A-EX4`. |
| `A-E5` | ungenutzt vorbereitet | Instruktionsmarker sind optional und aktuell keine Pflicht fuer Zielerreichung. | Optionales Hilfs- oder Erklaerszenario. |
| `A-E6` | ungenutzt vorbereitet | Grenzverletzungen sind fachlich relevant, aber nicht Teil des aktuellen Blockade-Exception-Pfads. | Spaetere Exception `A-EX1`. |

## Kardinalitaetscheck

| Regel | Bewertung fuer A |
| --- | --- |
| `ScenarioStep.triggeredBy [0..*]` | Erfuellt: einige Steps haben ein Event, andere begruendet keines. |
| Event mit mehreren Step-Zuordnungen | Erfuellt: `A-E4` wird bei `A-ALT-S01` und `A-EX-S01` verwendet; die Unterscheidung erfolgt spaeter ueber Guards. |
| Event ohne Step-Zuordnung | Erfuellt durch Markierung: `A-E2`, `A-E3`, `A-E5`, `A-E6` sind explizit ungenutzt vorbereitet. |
| Keine kuenstlichen Events | Erfuellt: Sequenzfortschritte ohne eigenstaendigen Ausloeser bleiben ohne Event. |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 4.7 | Folgetask |
| --- | --- | --- |
| Guard Conditions fuer Event-Auswahl | nicht formal angelegt | 4.8 |
| StateAssertions als Event-Folgen | nicht formal angelegt | 4.9 |
| CapabilityUse fuer systemische Reaktionen | nicht angelegt | 4.10 |
| RuntimeAction oder technische Endpoints | bewusst nicht referenziert | 4.14 |

## Abnahmekontrolle

| Kriterium aus Task 4.7 | Erfuellung |
| --- | --- |
| Eventliste vorhanden | `A-E1` bis `A-E8` sind als Event-Instanzen angelegt. |
| Jeder Event hat Art | Jedes Event besitzt genau einen Wert fuer `Event.kind`. |
| Jeder Event hat Ausdruck | Jedes Event besitzt eine pruefbare `Event.expression`. |
| Jeder genutzte Event ist mindestens einem Schritt zugeordnet | `A-E1`, `A-E4`, `A-E7`, `A-E8` besitzen `triggeredBy`-Zuordnungen. |
| Jeder nicht zugeordnete Event ist als ungenutzt markiert | `A-E2`, `A-E3`, `A-E5`, `A-E6` sind explizit `ungenutzt vorbereitet`. |
| Keine technische Kurzschaltung | Kein Event referenziert API, Topic, RuntimeAction, Tool oder Controlleraktion. |

## Konsequenz fuer Task 4.8

Task 4.8 kann nun die Condition-Instanzen fuer A anlegen. Besonders wichtig ist `A-E4`: Dasselbe Event fuehrt je nach Guard in die Alternative (`temporarilyBlocked`) oder in die Exception (`blocked`).
