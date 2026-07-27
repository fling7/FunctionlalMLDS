# Anwendungsfall A: Effect-Instanzen

Stand: 2026-07-07

Task: 4.12 `Effect-Instanzen fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

Ein `Effect` beschreibt die fachlich versprochene, beobachtbare Wirkung einer `Capability`. Der Effect ist damit weder ein Szenarioschritt noch eine technische Aktion. Er beschreibt, welcher fachliche Zustand nach erfolgreicher Nutzung der Capability beobachtbar sein soll.

Fuer Anwendungsfall A gelten diese Regeln:

- `Capability -> Effect` wird als `promisedEffect` gelesen.
- Jede angelegte `Capability` besitzt mindestens einen `Effect`.
- Jeder hier angelegte `Effect` gehoert genau zu einer fachlichen `Capability`.
- `observableBy` referenziert eine externe Beobachterrolle, hier `ACT-A-03` (`SceneObserver`).
- Der Bezug zu `StateAssertion` ist eine fachliche Rueckfuehrung auf bereits modellierte erwartete Zustaende. Er fuegt keine neue Metamodellkante hinzu.
- Kein `Effect` beschreibt Plattformaufrufe, Endpunkte, Topics, Tools, Controller oder RuntimeActions.

Damit bleibt die Schichtung erhalten:

`ScenarioStep -> CapabilityUse -> Capability -> Effect`

und die technische Ausfuehrung folgt erst spaeter ueber:

`Capability -> RuntimeBinding -> RuntimeAction`

## Angelegte Effect-Instanzen

| Effect-ID | Owner-Capability | `observableBy` | Fachlich beobachtbare Wirkung | StateAssertion-Bezug | Fachliche Pruefung |
| --- | --- | --- | --- | --- | --- |
| `A-EFF-ROLE-EXECUTOR` | `A-CAP-ADOPT-EXECUTOR-ROLE` | `ACT-A-03` | Der Agent besitzt den Rollenzustand `executor`. | `A-SA-S05-01` | `AgentBody.expectedState` enthaelt `roleState=executor`. |
| `A-EFF-AGENT-ACTING` | `A-CAP-ADOPT-EXECUTOR-ROLE` | `ACT-A-03` | Der Agent ist in einem aktiven Reaktionszustand. | `A-SA-S05-02` | `AgentBody.expectedState = acting`. |
| `A-EFF-AGENT-MOVING-TO-TARGET` | `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `ACT-A-03` | Der Agent fuehrt die zielgerichtete Szenenhandlung in Richtung Zielzone aus. | `A-SA-S06-01` | `AgentBody.expectedState = movingTo(TargetZone)`. |
| `A-EFF-TARGET-OCCUPIED` | `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `ACT-A-03` | Die Zielzone ist durch die Agentenhandlung erreicht oder belegt. | `A-SA-S06-02` | `TargetZone.expectedState = occupied`. |
| `A-EFF-AGENT-WAITING` | `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `ACT-A-03` | Der Agent setzt die Zielhandlung nicht fort und bleibt in einem sicheren Wartezustand. | `A-EX-SA03` | `AgentBody.expectedState = waiting`. |
| `A-EFF-ROLE-BLOCKED` | `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `ACT-A-03` | Der Rollenzustand des Agenten ist fuer den blockierten Zielpfad gesperrt. | `A-EX-SA04` | `AgentBody.expectedState` enthaelt `roleState=blocked`. |

## Kardinalitaetspruefung je Capability

| Capability-ID | Zugeordnete Effects | Anzahl | Bewertung |
| --- | --- | ---: | --- |
| `A-CAP-ADOPT-EXECUTOR-ROLE` | `A-EFF-ROLE-EXECUTOR`, `A-EFF-AGENT-ACTING` | 2 | gueltig: mindestens ein promised Effect vorhanden. |
| `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `A-EFF-AGENT-MOVING-TO-TARGET`, `A-EFF-TARGET-OCCUPIED` | 2 | gueltig: mindestens ein promised Effect vorhanden. |
| `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `A-EFF-AGENT-WAITING`, `A-EFF-ROLE-BLOCKED` | 2 | gueltig: mindestens ein promised Effect vorhanden. |

## Rueckbindung auf StateAssertions

Die StateAssertion-IDs in der Effect-Tabelle dienen als fachlicher Trace. Sie zeigen, welcher erwartete Zustand den Effect beobachtbar macht. Der Trace ist bewusst nicht als technische Messvorschrift formuliert.

| Effect-ID | Beobachtetes Subjekt | Erwarteter Zustand | Entsprechende StateAssertion |
| --- | --- | --- | --- |
| `A-EFF-ROLE-EXECUTOR` | `AgentBody` | `roleState=executor` | `A-SA-S05-01` |
| `A-EFF-AGENT-ACTING` | `AgentBody` | `acting` | `A-SA-S05-02` |
| `A-EFF-AGENT-MOVING-TO-TARGET` | `AgentBody` | `movingTo(TargetZone)` | `A-SA-S06-01` |
| `A-EFF-TARGET-OCCUPIED` | `TargetZone` | `occupied` | `A-SA-S06-02` |
| `A-EFF-AGENT-WAITING` | `AgentBody` | `waiting` | `A-EX-SA03` |
| `A-EFF-ROLE-BLOCKED` | `AgentBody` | `roleState=blocked` | `A-EX-SA04` |

## Warum der SceneObserver als `observableBy` reicht

Die Effects sind aus Sicht des Use Case beobachtbare fachliche Ergebnisse. Fuer diesen kompakten A-Durchlauf reicht deshalb `ACT-A-03` (`SceneObserver`) als Beobachterrolle aus. `ACT-A-01` (`ScenarioDesigner`) definiert die Modellierungsabsicht, ist aber nicht zwingend der Beobachter jedes Effects. `ACT-A-02` (`SceneParticipant`) kann Ereignisse ausloesen, ist aber nicht die Validierungs- oder Beobachterrolle der hier versprochenen Capability-Wirkungen.

## Keine technische Kurzschaltung

| Verbotene Kurzschaltung | Bewertung |
| --- | --- |
| `ScenarioStep -> RuntimeAction` | nicht vorhanden; Steps zeigen nur auf `CapabilityUse`. |
| `CapabilityUse -> RuntimeAction` | nicht vorhanden; CapabilityUse referenziert nur `Capability`. |
| `Effect` als technische Aktion | nicht vorhanden; jeder Effect beschreibt einen fachlichen Zustand. |
| `Effect` mit Plattform-, Endpunkt-, Topic-, Tool- oder Controllerdaten | nicht vorhanden. |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 4.12 | Folgetask |
| --- | --- | --- |
| `RuntimeBinding` | nicht angelegt | 4.13 |
| `RuntimeAction` | nicht angelegt | 4.14 |
| `ValidationCase` | nicht angelegt | 4.15 |

## Abnahmekontrolle

| Kriterium aus Task 4.12 | Erfuellung |
| --- | --- |
| Versprochene beobachtbare Effekte angelegt | Sechs `Effect`-Instanzen sind angelegt. |
| Jede Capability hat mindestens einen Effect | Jede der drei Capabilities besitzt zwei Effects. |
| Effects sind fachlich beobachtbar | Jeder Effect ist ueber eine StateAssertion fachlich rueckgebunden. |
| `observableBy` ist gesetzt | Alle sechs Effects referenzieren `ACT-A-03`. |
| Keine technische Ausfuehrung vorweggenommen | Es werden keine RuntimeBindings oder RuntimeActions angelegt. |

## Konsequenz fuer Task 4.13

Task 4.13 kann nun fuer jede fachliche `Capability` technische `RuntimeBinding`-Instanzen anlegen. Dabei muss jede RuntimeBinding genau eine Capability referenzieren und darf erst dort technische Bindungsinformationen enthalten.
