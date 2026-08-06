# Anwendungsfall A: Relevante Szenenobjekte

Stand: 2026-07-07

Task: 2.5 `Relevante Szenenobjekte als fachliche Gegenstaende erfassen`

Zweckbezug: Der Anwendungsfall beschreibt, wie ein Agent innerhalb einer virtuellen Szene zur Laufzeit auf Ereignisse und Bedingungen reagiert, seine Rolle, Position oder Handlung dynamisch aendert und dadurch einen explizit pruefbaren Zielzustand der Szene erreicht.

## Auswahlregel

Ein Gegenstand wird nur aufgenommen, wenn er fuer Agentenverhalten, Szenenzustand, Ereignisse, Bedingungen oder Zielzustand relevant ist. Jedes Objekt besitzt daher mindestens:

- einen beobachtbaren Zustand,
- oder eine relevante Interaktion,
- oder beides.

Nicht aufgenommen werden reine Render-, Asset-, Material-, Licht-, Physik- oder Engine-Details ohne direkte fachliche Relevanz fuer das dynamische Agentenmodell.

## Objektliste

| Objektname | Naheliegende Metamodell-Einordnung | Beobachtbarer Zustand | Relevante Interaktion | Relevanz fuer Anwendungsfall A |
| --- | --- | --- | --- | --- |
| `AgentBody` | `Agent` / spezialisierte `Entity` | `idle`, `moving`, `waiting`, `acting`, `arrived`, `blocked` | Reagiert auf Events, fuehrt fachliche Handlungen aus, aendert Position oder Zustand. | Zentrales Subjekt des dynamischen Agentenverhaltens. |
| `AgentBody.roleState` | Zustand des `Agent` | `observer`, `assistant`, `executor`, `blocked`, `completed` | Rollenwechsel kann durch Event, Condition oder ScenarioStep ausgeloest werden. | Erfasst, dass der Agent nicht nur Position, sondern auch Rolle oder Handlung dynamisch aendern kann. |
| `TargetZone` | `Entity` mit `kind = zone` | `unreached`, `reachable`, `occupied`, `reached` | Agent kann die Zone ansteuern, betreten oder als Zielzustand erreichen. | Typisches Ziel fuer StateAssertions wie `agent.location = targetZone`. |
| `TriggerZone` | `Entity` mit `kind = zone` | `inactive`, `active`, `entered`, `left` | Betreten oder Verlassen loest Events und ggf. StepRelations aus. | Liefert raeumliche Ausloeser fuer dynamisches Agentenverhalten. |
| `InteractionAsset` | `Entity` mit `kind = asset` | `available`, `unavailable`, `active`, `used`, `locked` | Agent oder SceneParticipant kann Zustand beobachten, aktivieren oder darauf reagieren. | Generischer Platzhalter fuer ein interaktionsrelevantes Szenenobjekt, das Verhalten beeinflusst. |
| `InstructionMarker` | `Entity` mit `kind = asset` | `hidden`, `visible`, `acknowledged`, `expired` | Kann dem Agenten oder Teilnehmer anzeigen, wohin oder wie gehandelt werden soll. | Macht Ziel- oder Handlungsinformation beobachtbar, ohne technische UI-Details vorwegzunehmen. |
| `SceneStateFlag` | `Entity` mit `kind = stateObject` | `normal`, `changed`, `requiresReaction`, `resolved` | Zustandsaenderung der Szene kann Agentenreaktion ausloesen. | Verdichtet szenische Bedingungen, die nicht als einzelnes physisches Objekt auftreten muessen. |
| `ObstacleRegion` | `Entity` mit `kind = zone` | `clear`, `blocked`, `temporarilyBlocked`, `cleared` | Beeinflusst, ob ein Ziel erreichbar ist oder ein Alternativpfad fachlich noetig wird. | Wichtig fuer Conditions wie `pathToTarget.blocked = true`, ohne Pathfinding-Algorithmus zu modellieren. |
| `ObservationPoint` | `Entity` mit `kind = stateObject` | `notObserved`, `observed`, `verified` | Agent oder Beobachter kann diesen Punkt erreichen oder pruefen. | Ermoeglicht pruefbare Zwischen- oder Zielzustaende fuer Validierung. |
| `FeedbackSignal` | `Entity` mit `kind = signal` | `notShown`, `shown`, `confirmed`, `failed` | System zeigt Rueckmeldung ueber Agentenhandlung oder Zielerreichung. | Verbindet Agentenverhalten mit beobachtbarem Szenenfeedback und spaeteren ValidationCases. |
| `ExternalSignalSource` | `Entity` mit `kind = signal` | `silent`, `signalPending`, `signalEmitted`, `signalConsumed` | Sendet fachliches Signal, das Agentenverhalten ausloest oder verzweigt. | Praezisiert externe Ereignisquellen, wenn `ExternalEventSource` als Actor-Rolle nicht ausreicht. |
| `SceneBoundary` | `Entity` mit `kind = zone` | `inside`, `outside`, `nearBoundary`, `violated` | Agent oder Teilnehmer kann Bereichsgrenzen betreten, verlassen oder verletzen. | Erlaubt Conditions und StateAssertions zu gueltigem Aufenthaltsbereich. |

## Kontextobjekte, aber noch keine finalen Szenenobjekte

| Kontextgegenstand | Warum noch nicht als Objektliste-Kern aufgenommen? | Moegliche spaetere Rolle |
| --- | --- | --- |
| `VirtualSceneContext` | Zu abstrakt fuer ein einzelnes beobachtbares Objekt; dient eher als Kontext fuer mehrere Conditions und StateAssertions. | Kann spaeter als Entity-Kontext bestehen bleiben. |
| `SceneStateController` | Fachliche Systementitaet fuer Orchestrierung, aber kein Szenenobjekt im engeren Sinn. | Kann spaeter Capabilities bereitstellen. |
| `ObservationChannel` | Beobachtungs-/Monitoring-Funktion, nicht zwingend ein Szenengegenstand. | Kann spaeter ValidationCases oder Effects stuetzen. |

## Abnahmekontrolle

| Kriterium aus Task 2.5 | Erfuellung |
| --- | --- |
| Objektliste mit Name | Jede Zeile in der Objektliste hat einen stabilen Objekt-/Gegenstandsnamen. |
| Zustand erfasst | Jede Zeile enthaelt mindestens einen beobachtbaren Zustand. |
| Relevanz erfasst | Jede Zeile enthaelt eine Begruendung fuer die Relevanz im Anwendungsfall A. |
| Interaktion oder beobachtbarer Zustand vorhanden | Jede Zeile hat beobachtbare Zustaende; die meisten Zeilen haben zusaetzlich eine relevante Interaktion. |
| Keine reine Asset-/Renderliste | Rendering, Materialien, Meshes und Engine-Details sind bewusst ausgeschlossen. |

## Konsequenz fuer Task 2.6

Task 2.6 kann aus dieser Objektliste dynamische Aenderungen ableiten, insbesondere:

- Events aus `TriggerZone`, `ExternalSignalSource` oder `SceneBoundary`,
- Zustandswechsel von `AgentBody`, `InteractionAsset`, `ObstacleRegion` oder `FeedbackSignal`,
- Conditions ueber `TargetZone`, `ObstacleRegion`, `SceneStateFlag` oder `SceneBoundary`,
- StateAssertions ueber `AgentBody` einschliesslich `roleState`, `TargetZone`, `ObservationPoint` und `FeedbackSignal`.
