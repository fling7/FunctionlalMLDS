# Anwendungsfall A: Condition-Instanzen

Stand: 2026-07-07

Task: 4.8 `Condition-Instanzen fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

`Condition` besitzt im kompakten Metamodell die Attribute `kind` und `expression`. Die hier verwendeten IDs wie `A-P1`, `A-GUARD-S01` oder `A-Q1` sind lokale Modellgriffe fuer die Beispielausarbeitung; sie sind nicht als zusaetzliches Metamodellattribut zu verstehen.

Zulaessige Werte fuer `Condition.kind` sind:

- `pre`
- `guard`
- `post`
- `spatial`
- `timing`

`Scenario.pre/postcondition [0..*]` erlaubt mehrere Vor- und Nachbedingungen auf Scenario-Ebene. `ScenarioStep.guard [0..1]` und `StepRelation.guard [0..1]` erlauben dagegen hoechstens eine direkte Guard Condition pro Schritt beziehungsweise Ablaufkante. Zusammengesetzte fachliche Voraussetzungen werden deshalb in einer einzigen pruefbaren `Condition.expression` gebuendelt.

## Scenario-Preconditions

| Condition-ID | `Condition.kind` | Scope | Pflichtstatus | `Condition.expression` | Begruendung |
| --- | --- | --- | --- | --- | --- |
| `A-P1` | `pre` | `A-MAIN-SC01` | Pflicht | `exists(AgentBody) and AgentBody is Agent` | Der modellierte Agent muss fachlich referenzierbar sein. |
| `A-P2` | `pre` | `A-MAIN-SC01` | Pflicht | `AgentBody.state in {idle, waiting} and AgentBody.roleState != blocked` | Der Agent muss handlungsbereit sein. |
| `A-P3` | `spatial` | `A-MAIN-SC01` | Pflicht | `inside(AgentBody, SceneBoundary) = true` | Der Agent muss sich im erlaubten Szenenbereich befinden. |
| `A-P4` | `pre` | `A-MAIN-SC01` | Pflicht | `TargetZone.state = reachable and ObstacleRegion.state != blocked` | Die Zielzone muss fuer den Erfolgspfad erreichbar sein. |
| `A-P5` | `pre` | `A-MAIN-SC01` | Pflicht | `TriggerZone.state = active or ExternalSignalSource.state in {silent, signalPending}` | Mindestens ein gueltiger Ausloeser muss modelliert sein. |
| `A-P6` | `guard` | `A-MAIN-SC01` | Pflicht | `Event.kind in {spatial, signal, user, environment}` | Ein eintretendes Ereignis muss zu den erlaubten Ereignisarten passen. |
| `A-P7` | `pre` | `A-MAIN-SC01` | Pflicht | `at(AgentBody, TargetZone) = false and FeedbackSignal.state = notShown` | Das Scenario darf nicht schon im Zielzustand starten. |
| `A-P8` | `guard` | `A-MAIN-SC01` | optional | `InteractionAsset.state != locked and InteractionAsset.state != unavailable` | Nur relevant, falls ein Interaktionsobjekt Teil der Szenariovariante wird. |
| `A-P9` | `pre` | `A-MAIN-SC01` | optional | `InstructionMarker.state in {hidden, visible}` | Nur relevant, falls ein Instruktionsmarker verwendet wird. |
| `A-P10` | `pre` | `A-MAIN-SC01` | Pflicht | `exists(ObservationPoint) = true` | Der Zielzustand muss beobachtbar oder spaeter verifizierbar sein. |
| `A-P11` | `timing` | `A-MAIN-SC01` | optional | `reactionTime <= allowedReactionWindow` | Nur relevant, falls Timing explizit modelliert wird. |
| `A-P12` | `pre` | `A-MAIN-SC01` | Pflicht | `SceneBoundary.state != violated and ObstacleRegion.state != blocked and AgentBody.roleState != blocked` | Zu Beginn darf keine fachliche Exception vorliegen. |

## Main-Scenario-Step-Guards

| Condition-ID | `Condition.kind` | Zugeordneter Step | `Condition.expression` | Bewertung |
| --- | --- | --- | --- | --- |
| `A-GUARD-S01` | `guard` | `A-MAIN-S01` | `Event.kind = spatial and Event.expression = entered(SceneParticipant, TriggerZone)` | Trennt den Hauptpfadstart ueber Zoneneintritt von alternativen Startformen. |
| `A-GUARD-S02` | `spatial` | `A-MAIN-S02` | `inside(AgentBody, SceneBoundary) = true` | Verhindert Fortsetzung ausserhalb der Szenengrenze. |
| `A-GUARD-S03` | `pre` | `A-MAIN-S03` | `AgentBody.state in {idle, waiting} and AgentBody.roleState != blocked` | Schuetzt Rollenwechsel und Reaktion vor blockiertem Agenten. |
| `A-GUARD-S04` | `guard` | `A-MAIN-S04` | `TargetZone.state = reachable and ObstacleRegion.state != blocked` | Entscheidet Hauptpfad gegen Blockade-Alternative oder Blockade-Exception. |
| `A-GUARD-S05` | `guard` | `A-MAIN-S05` | `inside(AgentBody, SceneBoundary) = true and AgentBody.roleState != blocked and TargetZone.state = reachable` | Rollenannahme ist nur bei weiterhin gueltigen Voraussetzungen erlaubt. |
| `A-GUARD-S06` | `guard` | `A-MAIN-S06` | `AgentBody.roleState = executor and TargetZone.state = reachable and ObstacleRegion.state != blocked` | Zielhandlung ist nur nach Rollenannahme und bei erreichbarer Zielzone erlaubt. |
| `A-GUARD-S08` | `post` | `A-MAIN-S08` | `at(AgentBody, TargetZone) = true and TargetZone.state in {occupied, reached}` | Verifikation darf erst nach beobachtbarer Zielerreichung erfolgen. |
| `A-GUARD-S09` | `post` | `A-MAIN-S09` | `ObservationPoint.state = verified and FeedbackSignal.state = shown` | Rueckmeldungsbestaetigung setzt Verifikation und angezeigte Rueckmeldung voraus. |

`A-MAIN-S07` besitzt bewusst keine direkte Guard Condition. Die Zulaessigkeit der Zielerreichung wurde bereits durch `A-GUARD-S06` abgesichert; `A-MAIN-S07` beschreibt den resultierenden beobachteten Zustand.

## Alternative- und Exception-Guards

| Condition-ID | `Condition.kind` | Zugeordnetes Element | `Condition.expression` | Bewertung |
| --- | --- | --- | --- | --- |
| `A-GUARD-ALT-S01` | `guard` | `A-ALT-S01` | `ObstacleRegion.state = temporarilyBlocked` | Der Alternativpfad startet nur bei temporaerer Blockade. |
| `A-GUARD-ALT-S02` | `guard` | `A-ALT-S02` | `ObstacleRegion.state in {temporarilyBlocked, cleared}` | Die Aufloesungsbeobachtung ist nur in einem aufloesbaren Blockadekontext sinnvoll. |
| `A-GUARD-ALT-R01` | `guard` | `A-ALT-R01` | `ObstacleRegion.state = temporarilyBlocked and TargetZone.state = reachable` | Einstiegskante aus `A-MAIN-S04` in die Alternative. |
| `A-GUARD-ALT-R03` | `guard` | `A-ALT-R03` | `ObstacleRegion.state = cleared and TargetZone.state = reachable` | Rueckfuehrung in den Hauptpfad vor `A-MAIN-S05`. |
| `A-GUARD-EX-S01` | `guard` | `A-EX-S01` | `ObstacleRegion.state = blocked` | Exception-Pfad startet nur bei dauerhafter Blockade. |
| `A-GUARD-EX-S02` | `guard` | `A-EX-S02` | `ObstacleRegion.state = blocked` | Der Agent darf nur bei bestehender Blockade am Fortsetzen gehindert werden. |
| `A-GUARD-EX-S03` | `guard` | `A-EX-S03` | `AgentBody.roleState = blocked` | Fehlerabschluss wird nur nach blockierendem Agentenzustand rueckgemeldet. |
| `A-GUARD-EX-R01` | `guard` | `A-EX-R01` | `ObstacleRegion.state = blocked` | Einstiegskante aus `A-MAIN-S04` in die Exception. |

Die Relationen `A-ALT-R02`, `A-EX-R02` und `A-EX-R03` besitzen keine eigene Guard Condition, weil sie reine Sequenzfortschritte innerhalb des bereits gewaehlten Pfads sind.

## Scenario-Postconditions

| Condition-ID | `Condition.kind` | Scope | Pflichtstatus | `Condition.expression` | Begruendung |
| --- | --- | --- | --- | --- | --- |
| `A-Q1` | `post` | `A-MAIN-SC01` | Pflicht | `at(AgentBody, TargetZone) = true and TargetZone.state = reached` | Der Hauptzielzustand ist erreicht. |
| `A-Q2` | `post` | `A-MAIN-SC01` | Pflicht | `inside(AgentBody, SceneBoundary) = true` | Der erfolgreiche Ablauf bleibt innerhalb der Szenengrenze. |
| `A-Q3` | `post` | `A-MAIN-SC01` | Pflicht | `AgentBody.state != blocked and AgentBody.roleState in {executor, completed}` | Der Agent endet nicht in einem Fehlerzustand. |
| `A-Q4` | `post` | `A-MAIN-SC01` | Pflicht | `ObservationPoint.state = verified` | Der Zielzustand wurde beobachtbar verifiziert. |
| `A-Q5` | `post` | `A-MAIN-SC01` | Pflicht | `FeedbackSignal.state = confirmed` | Der Abschluss wurde rueckgemeldet. |
| `A-Q6` | `post` | `A-MAIN-SC01` | kontextabhaengig | `ExternalSignalSource.state = signalConsumed or TriggerZone.state in {entered, left}` | Kein fuer den Erfolg relevanter Ausloeser bleibt unverarbeitet. |
| `A-Q7` | `post` | `A-MAIN-SC01` | kontextabhaengig | `ObstacleRegion.state in {clear, cleared}` | Keine relevante Blockade bleibt offen. |
| `A-Q8` | `post` | `A-MAIN-SC01` | kontextabhaengig | `InteractionAsset.state not in {locked, unavailable}` | Optional genutzte Interaktionsobjekte stehen konsistent. |
| `A-Q9` | `post` | `A-MAIN-SC01` | kontextabhaengig | `InstructionMarker.state in {acknowledged, expired, hidden}` | Optional verwendete Instruktionsmarker sind verarbeitet. |
| `A-Q10` | `post` | `A-MAIN-SC01` | kontextabhaengig | `SceneStateFlag.state in {normal, resolved}` | Die Szene fordert keine unmittelbare weitere Reaktion. |
| `A-Q11` | `post` | `A-MAIN-SC01` | Pflicht | `inside(AgentBody, SceneBoundary) = true and AgentBody.roleState != blocked` | Erhaltene Pflichtbedingungen bleiben nach Abschluss gueltig. |

## Referenzierung durch Scenario, ScenarioStep und StepRelation

| Zieltyp | Ziel | Referenzierte Conditions | Kardinalitaetsbewertung |
| --- | --- | --- | --- |
| `Scenario.precondition` | `A-MAIN-SC01` | `A-P1`, `A-P2`, `A-P3`, `A-P4`, `A-P5`, `A-P6`, `A-P7`, `A-P8`, `A-P9`, `A-P10`, `A-P11`, `A-P12` | gueltig: `0..*` |
| `Scenario.postcondition` | `A-MAIN-SC01` | `A-Q1`, `A-Q2`, `A-Q3`, `A-Q4`, `A-Q5`, `A-Q6`, `A-Q7`, `A-Q8`, `A-Q9`, `A-Q10`, `A-Q11` | gueltig: `0..*` |
| `ScenarioStep.guard` | `A-MAIN-S01` | `A-GUARD-S01` | gueltig: `0..1` |
| `ScenarioStep.guard` | `A-MAIN-S02` | `A-GUARD-S02` | gueltig: `0..1` |
| `ScenarioStep.guard` | `A-MAIN-S03` | `A-GUARD-S03` | gueltig: `0..1` |
| `ScenarioStep.guard` | `A-MAIN-S04` | `A-GUARD-S04` | gueltig: `0..1` |
| `ScenarioStep.guard` | `A-MAIN-S05` | `A-GUARD-S05` | gueltig: `0..1` |
| `ScenarioStep.guard` | `A-MAIN-S06` | `A-GUARD-S06` | gueltig: `0..1` |
| `ScenarioStep.guard` | `A-MAIN-S07` | leer | gueltig: Guard ist optional |
| `ScenarioStep.guard` | `A-MAIN-S08` | `A-GUARD-S08` | gueltig: `0..1` |
| `ScenarioStep.guard` | `A-MAIN-S09` | `A-GUARD-S09` | gueltig: `0..1` |
| `ScenarioStep.guard` | `A-ALT-S01` | `A-GUARD-ALT-S01` | gueltig: `0..1` |
| `ScenarioStep.guard` | `A-ALT-S02` | `A-GUARD-ALT-S02` | gueltig: `0..1` |
| `ScenarioStep.guard` | `A-EX-S01` | `A-GUARD-EX-S01` | gueltig: `0..1` |
| `ScenarioStep.guard` | `A-EX-S02` | `A-GUARD-EX-S02` | gueltig: `0..1` |
| `ScenarioStep.guard` | `A-EX-S03` | `A-GUARD-EX-S03` | gueltig: `0..1` |
| `StepRelation.guard` | `A-ALT-R01` | `A-GUARD-ALT-R01` | gueltig: `0..1` |
| `StepRelation.guard` | `A-ALT-R02` | leer | gueltig: Guard ist optional |
| `StepRelation.guard` | `A-ALT-R03` | `A-GUARD-ALT-R03` | gueltig: `0..1` |
| `StepRelation.guard` | `A-EX-R01` | `A-GUARD-EX-R01` | gueltig: `0..1` |
| `StepRelation.guard` | `A-EX-R02` | leer | gueltig: Guard ist optional |
| `StepRelation.guard` | `A-EX-R03` | leer | gueltig: Guard ist optional |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 4.8 | Folgetask |
| --- | --- | --- |
| `StateAssertion`-Instanzen | nicht formal angelegt | 4.9 |
| `RandomVariable`-Instanzen fuer Timing | nicht angelegt; `A-P11` bleibt deterministische Timing-Condition | bei Bedarf spaeteres Ergaenzungsmodell |
| `CapabilityUse`- und `Capability`-Preconditions | nicht angelegt | 4.10 und 4.11 |
| Runtime- oder API-Bedingungen | bewusst nicht modelliert | 4.13 und 4.14 |

## Abnahmekontrolle

| Kriterium aus Task 4.8 | Erfuellung |
| --- | --- |
| Preconditions vorhanden | `A-P1` bis `A-P12` sind als Conditions angelegt. |
| Guards vorhanden | Main-, Alternativ- und Exception-Guards sind als Conditions angelegt. |
| Postconditions vorhanden | `A-Q1` bis `A-Q11` sind als Conditions angelegt. |
| Jede Condition hat Typ | Jede Condition besitzt einen Wert fuer `Condition.kind`. |
| Jede Condition hat Ausdruck | Jede Condition besitzt eine nichtleere `Condition.expression`. |
| `ScenarioStep.guard [0..1]` eingehalten | Jeder Step referenziert hoechstens eine Guard Condition. |
| `StepRelation.guard [0..1]` eingehalten | Jede Ablaufkante referenziert hoechstens eine Guard Condition. |
| Keine technische Kurzschaltung | Keine Condition referenziert API, Topic, RuntimeAction, Tool oder Controlleraktion. |

## Konsequenz fuer Task 4.9

Task 4.9 kann nun die `StateAssertion`-Instanzen fuer A anlegen. Dabei muessen die in den Conditions verwendeten Subjekte wie `AgentBody`, `TargetZone`, `ObstacleRegion`, `ObservationPoint`, `FeedbackSignal` und `SceneStateFlag` als identifizierbare Subjekte konsistent referenziert werden.
