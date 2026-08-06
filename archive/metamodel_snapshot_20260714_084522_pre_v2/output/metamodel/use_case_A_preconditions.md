# Anwendungsfall A: Startzustand und Vorbedingungen

Stand: 2026-07-07

Task: 2.8 `Startzustand und Vorbedingungen sammeln`

Zweckbezug: Der Anwendungsfall beschreibt, wie ein Agent innerhalb einer virtuellen Szene zur Laufzeit auf Ereignisse und Bedingungen reagiert, seine Rolle, Position oder Handlung dynamisch aendert und dadurch einen explizit pruefbaren Zielzustand der Szene erreicht.

## Modellierungsregel

Der Startzustand beschreibt beobachtbare Ausgangswerte vor dem ersten fachlichen Szenarioschritt. Er ist primaer als `StateAssertion` formulierbar.

Eine Vorbedingung beschreibt eine pruefbare Aussage, die vor dem Hauptszenario oder vor einem konkreten Schritt wahr sein muss. Sie ist primaer als `Condition.kind = pre`, `Condition.kind = guard`, `Condition.kind = spatial` oder `Condition.kind = timing` formulierbar.

Nicht aufgenommen werden technische Initialisierungen wie Engine-Start, Controller-Setup, API-Verbindung, Topic-Subscription oder Pathfinding-Konfiguration. Solche Details duerfen spaeter nur ueber `RuntimeBinding` und `RuntimeAction` referenziert werden.

## Ausgangszustand des Hauptszenarios

| ID | Ausgangszustand | Betroffenes Subjekt | Vorlaeufige Metamodell-Abbildung | Pruefbarer Ausdruck |
| --- | --- | --- | --- | --- |
| `A-I1` | Der Agent ist vorhanden und fachlich adressierbar. | `AgentBody` | `StateAssertion.subjectRef = AgentBody` | `exists(AgentBody) = true` |
| `A-I2` | Der Agent befindet sich im gueltigen Szenenbereich. | `AgentBody`, `SceneBoundary` | `StateAssertion` plus raeumliche `Condition` | `inside(AgentBody, SceneBoundary) = true` |
| `A-I3` | Der Agent ist noch nicht in der Zielzone. | `AgentBody`, `TargetZone` | `StateAssertion.subjectRef = TargetZone` oder `AgentBody` | `at(AgentBody, TargetZone) = false` |
| `A-I4` | Der Agent ist zu Beginn nicht blockiert. | `AgentBody`, `AgentBody.roleState` | `StateAssertion.subjectRef = AgentBody` | `AgentBody.roleState != blocked` |
| `A-I5` | Die Zielzone ist fachlich erreichbar. | `TargetZone`, `ObstacleRegion` | `StateAssertion.subjectRef = TargetZone` | `TargetZone.state = reachable` |
| `A-I6` | Kein Hindernis blockiert den Zielbereich dauerhaft. | `ObstacleRegion` | `StateAssertion.subjectRef = ObstacleRegion` | `ObstacleRegion.state in {clear, cleared}` |
| `A-I7` | Eine Ausloesequelle ist fachlich aktivierbar. | `TriggerZone` oder `ExternalSignalSource` | `StateAssertion` ueber die gewaehlte Quelle | `TriggerZone.state = active or ExternalSignalSource.state in {silent, signalPending}` |
| `A-I8` | Ein optionales Interaktionsobjekt ist verfuegbar, falls der Ablauf es benoetigt. | `InteractionAsset` | `StateAssertion.subjectRef = InteractionAsset` | `InteractionAsset.state in {available, active}` |
| `A-I9` | Der Beobachtungspunkt ist noch nicht verifiziert. | `ObservationPoint` | `StateAssertion.subjectRef = ObservationPoint` | `ObservationPoint.state = notObserved` |
| `A-I10` | Es wurde noch keine Ergebnisrueckmeldung gezeigt. | `FeedbackSignal` | `StateAssertion.subjectRef = FeedbackSignal` | `FeedbackSignal.state = notShown` |

## Vorbedingungen

| ID | Vorbedingung | Art | Betroffene Elemente | Vorlaeufige Metamodell-Abbildung | Pruefbare Aussage |
| --- | --- | --- | --- | --- | --- |
| `A-P1` | Der modellierte Agent ist als `Agent` und zugleich als spezialisierte `Entity` referenzierbar. | strukturell | `AgentBody` | `Condition.kind = pre` | `exists(AgentBody) and AgentBody is Agent` |
| `A-P2` | Der Agent ist handlungsbereit. | fachlich | `AgentBody`, `AgentBody.roleState` | `Condition.kind = pre` | `AgentBody.state in {idle, waiting} and AgentBody.roleState != blocked` |
| `A-P3` | Der Agent befindet sich im erlaubten Szenenbereich. | raeumlich | `AgentBody`, `SceneBoundary` | `Condition.kind = spatial` | `inside(AgentBody, SceneBoundary) = true` |
| `A-P4` | Die Zielzone ist erreichbar und nicht bereits als erreicht markiert. | fachlich/raeumlich | `TargetZone`, `ObstacleRegion` | `Condition.kind = pre` oder `spatial` | `TargetZone.state = reachable and ObstacleRegion.state != blocked` |
| `A-P5` | Mindestens ein gueltiger Ausloeser ist modelliert und kann eintreten. | ausloeserbezogen | `TriggerZone`, `ExternalSignalSource` | `Condition.kind = pre` | `TriggerZone.state = active or ExternalSignalSource.state in {silent, signalPending}` |
| `A-P6` | Ein eintretendes Ausloeseereignis passt zu den erlaubten Ereignisarten des Szenarios. | ausloeserbezogen | `Event` | `Condition.kind = guard` | `Event.kind in {spatial, signal, user, environment}` |
| `A-P7` | Das Szenario beginnt nicht in einem bereits abgeschlossenen Zielzustand. | fachlich | `AgentBody`, `TargetZone`, `FeedbackSignal` | `Condition.kind = pre` | `at(AgentBody, TargetZone) = false and FeedbackSignal.state = notShown` |
| `A-P8` | Falls ein Interaktionsobjekt benoetigt wird, ist es nicht gesperrt. | fachlich | `InteractionAsset` | `Condition.kind = guard` | `InteractionAsset.state != locked and InteractionAsset.state != unavailable` |
| `A-P9` | Falls ein Instruktionsmarker verwendet wird, ist sein Zustand eindeutig. | fachlich | `InstructionMarker` | `Condition.kind = pre` | `InstructionMarker.state in {hidden, visible}` |
| `A-P10` | Das Szenario kann den Zielzustand beobachten oder spaeter verifizieren. | validierungsbezogen | `ObservationPoint`, `SceneObserver` | `Condition.kind = pre` | `exists(ObservationPoint) = true` |
| `A-P11` | Die Reaktion erfolgt innerhalb eines fachlich erlaubten Zeitfensters, falls Timing modelliert wird. | zeitlich | `SceneStateFlag`, optional `RandomVariable` | `Condition.kind = timing` | `reactionTime <= allowedReactionWindow` |
| `A-P12` | Keine fachliche Exception liegt bereits zu Beginn vor. | fachlich | `SceneBoundary`, `ObstacleRegion`, `AgentBody.roleState` | `Condition.kind = pre` | `SceneBoundary.state != violated and ObstacleRegion.state != blocked and AgentBody.roleState != blocked` |

## Pflicht- und optionale Vorbedingungen

| Kategorie | Vorbedingungen | Begruendung |
| --- | --- | --- |
| Pflicht fuer das Hauptszenario | `A-P1`, `A-P2`, `A-P3`, `A-P4`, `A-P5`, `A-P6`, `A-P7`, `A-P10`, `A-P12` | Ohne diese Aussagen ist der Erfolg aus `A-G1` bis `A-G7` nicht sinnvoll pruefbar. |
| Optional je nach Szenariovariante | `A-P8`, `A-P9`, `A-P11` | Diese Bedingungen werden nur benoetigt, wenn ein Interaktionsobjekt, Instruktionsmarker oder Timing explizit Teil des konkreten Szenarios ist. |

## Rueckbindung an Zielaussagen

| Zielaussage aus 2.7 | Relevante Vorbedingungen |
| --- | --- |
| `A-G1` gueltiges Ereignis hat ausgeloest | `A-P5`, `A-P6` |
| `A-G2` Agent ist im gueltigen Szenenbereich | `A-P3`, `A-P12` |
| `A-G3` Agent ist handlungsbereit oder in passender Rolle | `A-P1`, `A-P2` |
| `A-G4` Zielzone ist erreichbar oder Alternative geloest | `A-P4`, optional `A-P8`, `A-P11` |
| `A-G5` Agent erreicht Zielzone | `A-P2`, `A-P3`, `A-P4`, `A-P7` |
| `A-G6` Beobachtungspunkt wurde verifiziert | `A-P10` |
| `A-G7` Rueckmeldung wurde bestaetigt | `A-P7`, `A-P10` |

## Abnahmekontrolle

| Kriterium aus Task 2.8 | Erfuellung |
| --- | --- |
| Liste von Preconditions vorhanden | `A-P1` bis `A-P12` bilden die Vorbedingungsliste. |
| Jede Vorbedingung ist pruefbar | Jede Zeile enthaelt eine konkrete pruefbare Aussage. |
| Startzustand erfasst | `A-I1` bis `A-I10` beschreiben beobachtbare Ausgangszustaende. |
| Metamodellnahe Zuordnung vorhanden | Jede Vorbedingung verweist auf `Condition.kind`; jeder Ausgangszustand auf `StateAssertion` oder eine raeumliche `Condition`. |
| Pflicht und Option getrennt | Pflichtbedingungen und optionale Variantenbedingungen sind separat ausgewiesen. |
| Keine technische Kurzschaltung | Technische Initialisierung, APIs, Topics, Engine-Start und Pathfinding sind ausgeschlossen. |

## Konsequenz fuer Task 2.9

Task 2.9 kann aus den Zielaussagen `A-G5` bis `A-G7` die Endzustaende und Nachbedingungen ableiten. Besonders relevant sind:

- `TargetZone.state = reached`,
- `ObservationPoint.state = verified`,
- `FeedbackSignal.state = confirmed`,
- keine Verletzung von `SceneBoundary`,
- keine offen gebliebene Blockade im erfolgreichen Hauptpfad.
