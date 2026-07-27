# Anwendungsfall A: StateAssertion-Instanzen

Stand: 2026-07-07

Task: 4.9 `StateAssertion-Instanzen fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

`StateAssertion` beschreibt eine erwartete oder beobachtbare fachliche Zustandsaussage. Jede StateAssertion besitzt:

- genau ein identifizierbares Subjekt als `subjectRef`,
- genau einen erwarteten Zustand als `expectedState`.

Die Beziehung `ScenarioStep.resultingState -> StateAssertion [0..*]` erlaubt mehrere Zustandsaussagen pro Schritt. Deshalb werden zusammengesetzte Aussagen in einzelne StateAssertions zerlegt.

Wichtig fuer die Korrektheit: `AgentRoleState` wird nicht als eigenes nicht-identifizierbares Subjekt verwendet. Rollenzustaende werden als Zustand des identifizierbaren Subjekts `AgentBody` formuliert, z. B. `roleState=executor`.

## Identifizierbare Subjekte

| Subject-ID | Identifizierbarer Modellgegenstand | Einordnung | Verwendung in StateAssertions |
| --- | --- | --- | --- |
| `AgentBody` | Agent / spezialisierte Entity | `Agent`, `Entity.kind = agent` | Position, Aktivitaet und Rollenzustand des dynamischen Agenten |
| `TriggerZone` | Szenenbereich | `Entity.kind = zone` | raeumliches Startereignis |
| `SceneBoundary` | Szenengrenze | `Entity.kind = zone` | Gueltigkeit des Szenenbereichs |
| `TargetZone` | Zielbereich | `Entity.kind = zone` | Erreichbarkeit, Belegung und Zielerreichung |
| `ObstacleRegion` | Hindernisbereich | `Entity.kind = zone` | freie, temporaer blockierte oder dauerhaft blockierte Zielregion |
| `SceneStateFlag` | Szenenzustandsmarker | `Entity.kind = stateObject` | Reaktionsbedarf oder geloester Szenenzustand |
| `ObservationPoint` | Beobachtungspunkt | `Entity.kind = stateObject` | beobachtbare Verifikation |
| `FeedbackSignal` | Rueckmeldung | `Entity.kind = signal` | bestaetigte oder fehlgeschlagene Rueckmeldung |

## Main-Scenario-StateAssertions

| StateAssertion-ID | Owner-Scenario | ScenarioStep | `subjectRef` | `expectedState` | Zweck |
| --- | --- | --- | --- | --- | --- |
| `A-SA-S01-01` | `A-MAIN-SC01` | `A-MAIN-S01` | `TriggerZone` | `entered` | Das gueltige Ausloeseereignis ist als betretener Ausloesebereich beobachtbar. |
| `A-SA-S01-02` | `A-MAIN-SC01` | `A-MAIN-S01` | `SceneStateFlag` | `requiresReaction` | Die Szene verlangt nach dem Start-Event eine Agentenreaktion. |
| `A-SA-S02-01` | `A-MAIN-SC01` | `A-MAIN-S02` | `AgentBody` | `inside(SceneBoundary)` | Der Agent befindet sich im gueltigen Szenenbereich. |
| `A-SA-S02-02` | `A-MAIN-SC01` | `A-MAIN-S02` | `SceneBoundary` | `notViolated` | Die Szenengrenze ist im Hauptpfad nicht verletzt. |
| `A-SA-S03-01` | `A-MAIN-SC01` | `A-MAIN-S03` | `AgentBody` | `idleOrWaiting` | Der Agent ist in einem handlungsbereiten Ausgangszustand. |
| `A-SA-S03-02` | `A-MAIN-SC01` | `A-MAIN-S03` | `AgentBody` | `roleState=notBlocked` | Der Rollenzustand des Agenten blockiert den Hauptpfad nicht. |
| `A-SA-S04-01` | `A-MAIN-SC01` | `A-MAIN-S04` | `TargetZone` | `reachable` | Die Zielzone ist fachlich erreichbar. |
| `A-SA-S04-02` | `A-MAIN-SC01` | `A-MAIN-S04` | `ObstacleRegion` | `clear` | Keine Blockade verhindert den erfolgreichen Hauptpfad. |
| `A-SA-S05-01` | `A-MAIN-SC01` | `A-MAIN-S05` | `AgentBody` | `roleState=executor` | Der Agent hat die Ausfuehrungsrolle angenommen. |
| `A-SA-S05-02` | `A-MAIN-SC01` | `A-MAIN-S05` | `AgentBody` | `acting` | Der Agent ist fachlich in einen aktiven Reaktionszustand gewechselt. |
| `A-SA-S06-01` | `A-MAIN-SC01` | `A-MAIN-S06` | `AgentBody` | `movingTo(TargetZone)` | Der Agent fuehrt die zielgerichtete Bewegung oder Handlung aus. |
| `A-SA-S06-02` | `A-MAIN-SC01` | `A-MAIN-S06` | `TargetZone` | `occupied` | Die Zielzone wird durch die Agentenhandlung erreicht oder belegt. |
| `A-SA-S07-01` | `A-MAIN-SC01` | `A-MAIN-S07` | `AgentBody` | `at(TargetZone)` | Der Agent befindet sich an der Zielzone. |
| `A-SA-S07-02` | `A-MAIN-SC01` | `A-MAIN-S07` | `TargetZone` | `reached` | Die Zielzone ist als erreicht markiert. |
| `A-SA-S08-01` | `A-MAIN-SC01` | `A-MAIN-S08` | `ObservationPoint` | `verified` | Der erreichte Zielzustand wurde beobachtbar verifiziert. |
| `A-SA-S08-02` | `A-MAIN-SC01` | `A-MAIN-S08` | `SceneStateFlag` | `resolved` | Die Szene fordert nach erfolgreicher Verifikation keine unmittelbare Reaktion mehr. |
| `A-SA-S09-01` | `A-MAIN-SC01` | `A-MAIN-S09` | `FeedbackSignal` | `confirmed` | Die Ergebnisrueckmeldung wurde bestaetigt. |
| `A-SA-S09-02` | `A-MAIN-SC01` | `A-MAIN-S09` | `AgentBody` | `roleState=completed` | Der Agentenablauf ist fachlich abgeschlossen. |

## Alternative-Scenario-StateAssertions

| StateAssertion-ID | Owner-Scenario | ScenarioStep | `subjectRef` | `expectedState` | Zweck |
| --- | --- | --- | --- | --- | --- |
| `A-ALT-SA01` | `A-ALT-SC01` | `A-ALT-S01` | `ObstacleRegion` | `temporarilyBlocked` | Die temporaere Ursache der Alternative ist beobachtbar. |
| `A-ALT-SA02` | `A-ALT-SC01` | `A-ALT-S01` | `SceneStateFlag` | `requiresReaction` | Die Szene verlangt Reaktion auf die temporaere Blockade. |
| `A-ALT-SA03` | `A-ALT-SC01` | `A-ALT-S02` | `ObstacleRegion` | `cleared` | Die temporaere Blockade ist fachlich aufgehoben. |
| `A-ALT-SA04` | `A-ALT-SC01` | `A-ALT-S02` | `TargetZone` | `reachable` | Die Zielzone ist wieder fuer den Hauptpfad erreichbar. |

## Exception-Scenario-StateAssertions

| StateAssertion-ID | Owner-Scenario | ScenarioStep | `subjectRef` | `expectedState` | Zweck |
| --- | --- | --- | --- | --- | --- |
| `A-EX-SA01` | `A-EX-SC01` | `A-EX-S01` | `ObstacleRegion` | `blocked` | Die Ursache der Exception bleibt beobachtbar. |
| `A-EX-SA02` | `A-EX-SC01` | `A-EX-S01` | `TargetZone` | `unreached` | Das Erfolgsziel wurde nicht erreicht. |
| `A-EX-SA03` | `A-EX-SC01` | `A-EX-S02` | `AgentBody` | `waiting` | Der Agent setzt die Zielhandlung nicht unzulaessig fort. |
| `A-EX-SA04` | `A-EX-SC01` | `A-EX-S02` | `AgentBody` | `roleState=blocked` | Der Rollenzustand des Agenten ist fuer den Hauptpfad gesperrt. |
| `A-EX-SA05` | `A-EX-SC01` | `A-EX-S03` | `FeedbackSignal` | `failed` | Der Fehlerabschluss ist beobachtbar rueckgemeldet. |
| `A-EX-SA06` | `A-EX-SC01` | `A-EX-S03` | `SceneStateFlag` | `requiresReaction` | Die Szene verlangt Korrektur, Aufloesung oder manuelle Entscheidung. |

## ResultingState-Zuordnung je Step

| ScenarioStep | `resultingState`-Referenzen | Anzahl | Bewertung |
| --- | --- | ---: | --- |
| `A-MAIN-S01` | `A-SA-S01-01`, `A-SA-S01-02` | 2 | gueltig: `0..*` |
| `A-MAIN-S02` | `A-SA-S02-01`, `A-SA-S02-02` | 2 | gueltig: `0..*` |
| `A-MAIN-S03` | `A-SA-S03-01`, `A-SA-S03-02` | 2 | gueltig: `0..*` |
| `A-MAIN-S04` | `A-SA-S04-01`, `A-SA-S04-02` | 2 | gueltig: `0..*` |
| `A-MAIN-S05` | `A-SA-S05-01`, `A-SA-S05-02` | 2 | gueltig: `0..*` |
| `A-MAIN-S06` | `A-SA-S06-01`, `A-SA-S06-02` | 2 | gueltig: `0..*` |
| `A-MAIN-S07` | `A-SA-S07-01`, `A-SA-S07-02` | 2 | gueltig: `0..*` |
| `A-MAIN-S08` | `A-SA-S08-01`, `A-SA-S08-02` | 2 | gueltig: `0..*` |
| `A-MAIN-S09` | `A-SA-S09-01`, `A-SA-S09-02` | 2 | gueltig: `0..*` |
| `A-ALT-S01` | `A-ALT-SA01`, `A-ALT-SA02` | 2 | gueltig: `0..*` |
| `A-ALT-S02` | `A-ALT-SA03`, `A-ALT-SA04` | 2 | gueltig: `0..*` |
| `A-EX-S01` | `A-EX-SA01`, `A-EX-SA02` | 2 | gueltig: `0..*` |
| `A-EX-S02` | `A-EX-SA03`, `A-EX-SA04` | 2 | gueltig: `0..*` |
| `A-EX-S03` | `A-EX-SA05`, `A-EX-SA06` | 2 | gueltig: `0..*` |

## Normalisierung gegenueber frueheren Notizen

| Fruehere Schreibweise | Normierte StateAssertion-Schreibweise | Grund |
| --- | --- | --- |
| `AgentRoleState = notBlocked` | `subjectRef = AgentBody`, `expectedState = roleState=notBlocked` | `AgentBody` ist das identifizierbare Subjekt. |
| `AgentRoleState = executor` | `subjectRef = AgentBody`, `expectedState = roleState=executor` | Rollenzustand gehoert fachlich zum Agenten. |
| `AgentRoleState = completed` | `subjectRef = AgentBody`, `expectedState = roleState=completed` | Abschlusszustand wird am Agenten beobachtet. |
| `AgentRoleState = blocked` | `subjectRef = AgentBody`, `expectedState = roleState=blocked` | Exception-Zustand wird am Agenten beobachtet. |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 4.9 | Folgetask |
| --- | --- | --- |
| `CapabilityUse`-Instanzen | nicht angelegt | 4.10 |
| `Capability`- und `Effect`-Instanzen | nicht angelegt | 4.11 und 4.12 |
| Runtime- oder API-Zustaende | bewusst nicht modelliert | 4.13 und 4.14 |
| `ValidationCase`-Outcomes | nicht angelegt | 4.15 |

## Abnahmekontrolle

| Kriterium aus Task 4.9 | Erfuellung |
| --- | --- |
| Erwartete Zustandsaussagen vorhanden | 28 `StateAssertion`-Instanzen sind angelegt. |
| Jede Aussage referenziert ein identifizierbares Subjekt | Jede Zeile verwendet ein Subjekt aus dem Subject-Katalog. |
| Jede Aussage hat genau einen erwarteten Zustand | Jede Zeile besitzt genau einen `expectedState`. |
| Main, Alternative und Exception abgedeckt | 18 Main-, 4 Alternative- und 6 Exception-StateAssertions sind vorhanden. |
| `ScenarioStep.resultingState [0..*]` eingehalten | Jeder relevante Step referenziert zwei StateAssertions; mehrere Referenzen sind zulaessig. |
| Keine technische Kurzschaltung | Keine StateAssertion referenziert API, Topic, RuntimeAction, Tool oder Controlleraktion. |

## Konsequenz fuer Task 4.10

Task 4.10 kann nun die `CapabilityUse`-Instanzen fuer A anlegen. Besonders relevant sind die systemischen Schritte `A-MAIN-S05`, `A-MAIN-S06` und `A-EX-S02`, weil sie fachliche Reaktionen beschreiben und nicht direkt auf RuntimeActions zeigen duerfen.
