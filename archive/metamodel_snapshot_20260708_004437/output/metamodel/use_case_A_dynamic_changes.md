# Anwendungsfall A: Dynamische Aenderungen der Szene

Stand: 2026-07-07

Task: 2.6 `Dynamische Aenderungen der Szene erfassen`

Zweckbezug: Der Anwendungsfall beschreibt, wie ein Agent innerhalb einer virtuellen Szene zur Laufzeit auf Ereignisse und Bedingungen reagiert, seine Rolle, Position oder Handlung dynamisch aendert und dadurch einen explizit pruefbaren Zielzustand der Szene erreicht.

## Modellierungsregel

Eine dynamische Aenderung wird hier nicht als technischer Ablauf, Engine-Update oder Pathfinding-Schritt verstanden. Modelliert wird nur das fachlich Beobachtbare:

- ein `Event`, wenn etwas geschieht und einen Schritt ausloesen kann,
- eine `Condition`, wenn eine pruefbare Aussage eine Ausfuehrung erlaubt, verhindert, verzweigt oder abschliesst,
- eine `StateAssertion`, wenn ein beobachtbarer Zustand eines identifizierbaren Subjekts erwartet oder festgestellt wird.

Ein Zustandswechsel wird deshalb als Kombination aus Vorzustand, Ausloeser, optionaler Bedingung und Zielzustand beschrieben. Der Zielzustand ist spaeter als `StateAssertion.subjectRef + expectedState` modellierbar. Die technische Umsetzung bleibt ausserhalb von `ScenarioStep` und darf erst spaeter ueber `CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction` angebunden werden.

## Ereignisse

| ID | Ereignis | Quelle / betroffene Elemente | Vorlaeufige Metamodell-Zuordnung | Ausdruck fuer `Event.expression` | Begruendung |
| --- | --- | --- | --- | --- | --- |
| `A-E1` | Ein Szenenteilnehmer betritt die Ausloesezone. | `SceneParticipant`, `TriggerZone` | `Event.kind = spatial` | `entered(SceneParticipant, TriggerZone)` | Das Betreten einer Zone ist ein raeumliches Ereignis, das Agentenverhalten starten oder verzweigen kann. |
| `A-E2` | Eine externe Signalquelle sendet ein Start- oder Aenderungssignal. | `ExternalSignalSource`, `SceneStateFlag` | `Event.kind = signal` | `signalEmitted(ExternalSignalSource)` | Das Signal ist ein fachlicher Ausloeser, aber noch kein technischer Topic- oder API-Aufruf. |
| `A-E3` | Ein relevantes Interaktionsobjekt wechselt in einen gesperrten oder nicht verfuegbaren Zustand. | `InteractionAsset` | `Event.kind = environment` | `stateChanged(InteractionAsset, locked|unavailable)` | Der Objektzustand beeinflusst, ob der Agent direkt handeln kann oder einen Alternativschritt benoetigt. |
| `A-E4` | Eine Hindernisregion blockiert den geplanten Zielbereich. | `ObstacleRegion`, `TargetZone` | `Event.kind = environment` | `stateChanged(ObstacleRegion, blocked|temporarilyBlocked)` | Der konkrete Pfadalgorithmus bleibt out of scope; relevant ist die fachliche Blockadebedingung. |
| `A-E5` | Ein Instruktionsmarker wird sichtbar oder bestaetigt. | `InstructionMarker`, `AgentBody` | `Event.kind = signal` | `markerVisible(InstructionMarker)` | Der Marker liefert beobachtbare Handlungsinformation fuer Agent oder Teilnehmer. |
| `A-E6` | Der Agent erreicht oder verlaesst einen gueltigen Szenenbereich. | `AgentBody`, `SceneBoundary` | `Event.kind = spatial` | `boundaryStateChanged(AgentBody, SceneBoundary)` | Die Grenze ist relevant fuer Guards, Exceptions und pruefbare Aufenthaltszustaende. |
| `A-E7` | Ein Beobachtungspunkt wird geprueft oder verifiziert. | `ObservationPoint`, `SceneObserver` | `Event.kind = user` oder `Event.kind = signal` | `verified(ObservationPoint)` | Ob die Pruefung von einem Beobachter oder Systemsignal kommt, kann im konkreten Szenario entschieden werden. |
| `A-E8` | Das System gibt eine sichtbare Rueckmeldung aus. | `FeedbackSignal`, `SceneStateFlag` | `Event.kind = signal` | `shown(FeedbackSignal)` | Rueckmeldung ist ein beobachtbares Signal und kann Folge- oder Abschlussbedingungen ausloesen. |

## Zustandswechsel

| ID | Zustandswechsel | Ausloeser | Relevante Bedingung | Vorlaeufige Metamodell-Zuordnung | Zielzustand als `StateAssertion.expectedState` |
| --- | --- | --- | --- | --- | --- |
| `A-S1` | `AgentBody: idle -> moving` | `A-E1` oder `A-E2` | `A-C1`, `A-C2`, optional `A-C3` | `StateAssertion` fuer `AgentBody`; Event triggert spaeter einen `ScenarioStep`. | `moving` |
| `A-S2` | `AgentBody.roleState: observer -> executor` | `A-E1`, `A-E2` oder ein vorheriger `ScenarioStep` | `A-C1`, `A-C5` | `StateAssertion` ueber `AgentBody.roleState`; kein eigener Actor. | `executor` |
| `A-S3` | `TriggerZone: active -> entered` | `A-E1` | `A-C2` | `Event` plus `StateAssertion` ueber `TriggerZone`. | `entered` |
| `A-S4` | `TargetZone: reachable -> occupied` | Agentenbewegung abgeschlossen | `A-C1`, `A-C3`, `A-C4` | `StateAssertion` ueber `TargetZone` und optional ueber `AgentBody`. | `occupied` |
| `A-S5` | `TargetZone: occupied -> reached` | Beobachtung oder Abschluss des Agentenschritts | `A-C7` | `StateAssertion` als pruefbarer Zielzustand. | `reached` |
| `A-S6` | `InteractionAsset: available -> active -> used` | Agent oder Teilnehmer interagiert mit Objekt | `A-C4` | `StateAssertion` ueber `InteractionAsset`; Interaktion selbst spaeter als `ScenarioStep`. | `active` oder `used` |
| `A-S7` | `SceneStateFlag: normal -> requiresReaction` | `A-E2`, `A-E3` oder `A-E4` | `A-C5` | Kombination aus `Event`, `Condition` und `StateAssertion` ueber Szenenzustand. | `requiresReaction` |
| `A-S8` | `ObstacleRegion: clear -> blocked` | `A-E4` | keine oder `A-C3` als Folgeguard | `Event.kind = environment`; Zielzustand als `StateAssertion`. | `blocked` |
| `A-S9` | `ObstacleRegion: blocked -> cleared` | Umgebungsaenderung oder Korrekturschritt | `A-C6` | `StateAssertion`; kann spaeter eine alternative `StepRelation` wieder in den Hauptablauf fuehren. | `cleared` |
| `A-S10` | `FeedbackSignal: notShown -> shown -> confirmed` | `A-E8` oder Abschluss eines Schritts | `A-C7`, `A-C8` | Rueckmeldung wird als beobachtbarer Effekt und spaeter als Validierungsgrundlage nutzbar. | `shown` oder `confirmed` |
| `A-S11` | `ExternalSignalSource: signalPending -> signalEmitted -> signalConsumed` | Externes Signal | `A-C5` | `Event` fuer Emission; `StateAssertion` fuer verbrauchten Signalzustand. | `signalConsumed` |
| `A-S12` | `SceneBoundary: inside -> nearBoundary -> violated` | `A-E6` | `A-C2` verletzt | `StateAssertion` und moegliche `StepRelation.kind = exception`. | `violated` |

## Bedingungen

| ID | Bedingung | Betroffene Elemente | Vorlaeufige Metamodell-Zuordnung | Ausdruck fuer `Condition.expression` | Rolle im Szenario |
| --- | --- | --- | --- | --- | --- |
| `A-C1` | Der Agent ist handlungsbereit. | `AgentBody`, `AgentBody.roleState` | `Condition.kind = pre` oder `guard` | `AgentBody.state in {idle, waiting} and AgentBody.roleState != blocked` | Vorbedingung fuer Agentenreaktion. |
| `A-C2` | Der Agent befindet sich innerhalb des gueltigen Szenenbereichs. | `AgentBody`, `SceneBoundary` | `Condition.kind = spatial` | `inside(AgentBody, SceneBoundary) = true` | Raumbezogener Guard; Verletzung fuehrt zu Exception. |
| `A-C3` | Der Zielbereich ist fachlich erreichbar. | `TargetZone`, `ObstacleRegion` | `Condition.kind = spatial` oder `guard` | `TargetZone.state = reachable and ObstacleRegion.state != blocked` | Entscheidet zwischen Hauptablauf und Alternativpfad. |
| `A-C4` | Das Interaktionsobjekt ist verfuegbar. | `InteractionAsset` | `Condition.kind = pre` oder `guard` | `InteractionAsset.state in {available, active}` | Vorbedingung fuer objektbezogene Handlung. |
| `A-C5` | Die Szene verlangt eine Reaktion. | `SceneStateFlag`, `ExternalSignalSource` | `Condition.kind = guard` | `SceneStateFlag.state = requiresReaction or signalEmitted(ExternalSignalSource)` | Guard fuer reaktive Agentenschritte. |
| `A-C6` | Eine Blockade wurde aufgehoben oder darf umgangen werden. | `ObstacleRegion`, `TargetZone` | `Condition.kind = guard` | `ObstacleRegion.state in {cleared, temporarilyBlocked}` | Ermoeglicht Rueckkehr in den Hauptablauf oder Alternative. |
| `A-C7` | Der Zielzustand ist beobachtbar erreicht. | `AgentBody`, `TargetZone`, `ObservationPoint` | `Condition.kind = post` | `at(AgentBody, TargetZone) and ObservationPoint.state = verified` | Nachbedingung fuer erfolgreiche Zielerreichung. |
| `A-C8` | Die Rueckmeldung wurde bestaetigt. | `FeedbackSignal`, `SceneObserver` | `Condition.kind = post` | `FeedbackSignal.state = confirmed` | Abschlussbedingung fuer spaetere Validierung. |
| `A-C9` | Das Zeitfenster fuer die Reaktion ist nicht abgelaufen. | `SceneStateFlag`, optional `RandomVariable` | `Condition.kind = timing` | `reactionTime <= allowedReactionWindow` | Nur fachliche Timing-Bedingung; keine Scheduler-Implementierung. |

## Minimale Abbildungsregel fuer das spaetere Szenario

| Dynamische Beobachtung | Abbildung im Metamodell |
| --- | --- |
| "Etwas passiert." | `Event.kind + Event.expression` |
| "Ein Schritt darf nur unter einer Voraussetzung laufen." | `Condition.kind = pre|guard|spatial|timing` |
| "Ein Schritt fuehrt zu einem beobachtbaren Zustand." | `ScenarioStep.resultingState -> StateAssertion` |
| "Ein Zustand aendert sich von X nach Y." | Vorzustand als `Condition`, Zielzustand als `StateAssertion`; der Ausloeser bleibt `Event`. |
| "Es gibt eine Alternative oder Exception." | `StepRelation.kind = alternative|exception` mit optionaler Guard-`Condition`. |
| "Eine technische Aktion fuehrt die Aenderung aus." | Noch nicht in `ScenarioStep`; spaeter nur ueber `CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`. |

## Abnahmekontrolle

| Kriterium aus Task 2.6 | Erfuellung |
| --- | --- |
| Ereignisse erfasst | `A-E1` bis `A-E8` listen raeumliche, signalbasierte, nutzerbezogene und umgebungsbezogene Ereignisse. |
| Zustandswechsel erfasst | `A-S1` bis `A-S12` beschreiben beobachtbare Vorher/Nachher-Aenderungen der relevanten Szenenobjekte. |
| Bedingungen erfasst | `A-C1` bis `A-C9` erfassen Vorbedingungen, Guards, raeumliche Bedingungen, Timing und Nachbedingungen. |
| Jede Aenderung vorlaeufig zuordenbar | Jede Zeile verweist explizit auf `Event`, `Condition` oder `StateAssertion`; Zustandswechsel werden als Kombination dieser Elemente verstanden. |
| Keine technische Kurzschaltung | Keine Zeile enthaelt RuntimeAction, API, Topic, Engine-Befehl oder Pathfinding-Algorithmus. |

## Konsequenz fuer Task 2.7

Task 2.7 kann daraus ein Hauptziel ableiten. Ein naheliegender Zielkandidat ist:

`Der dynamische Agent reagiert auf ein gueltiges Ereignis, wechselt in die passende Rolle, erreicht die Zielzone unter Einhaltung der relevanten Bedingungen und erzeugt eine bestaetigte, beobachtbare Rueckmeldung.`

Dieser Zielkandidat ist pruefbar, weil er auf `A-C7`, `A-C8`, `A-S5` und `A-S10` zurueckgefuehrt werden kann.
