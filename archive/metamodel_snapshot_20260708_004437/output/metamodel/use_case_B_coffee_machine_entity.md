# Anwendungsfall B: Kaffeemaschine als fachliche Entitaet

Stand: 2026-07-07

Task: 8.4 `Kaffeemaschine als fachliche Entitaet modellieren`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Modellierungsregel

Die Kaffeemaschine wird in der aktuellen Baseline als `Entity` modelliert. Ihre primaere `Entity.kind` ist `asset`, weil sie ein identifizierbares virtuelles Szenenobjekt und Interaktionsobjekt ist.

Die Kaffeemaschine ist:

- eine fachliche Entitaet mit beobachtbaren Zustaenden,
- ein bedienbares virtuelles Asset,
- ein moeglicher Traeger fachlicher Capabilities,
- ein Subjekt von Conditions, Events und StateAssertions.

Die Kaffeemaschine ist nicht:

- ein `Actor`, weil sie keine externe Rolle mit eigener UseCase-Absicht ist,
- ein `Agent`, weil sie keine eigenstaendige Assistenz-, Dialog- oder Planungsinstanz wie Vivian ist,
- eine `RuntimeAction`, weil technische Ansteuerung erst unter `RuntimeBinding -> RuntimeAction` liegt,
- ein Controller, Topic, Tool, Endpoint, GameObject oder Prefab.

## Angelegte Entity-Instanz

| Attribut / Beziehung | Wert |
| --- | --- |
| Instanz-ID | `ENT-B-02` |
| Metamodellklasse | `Entity` |
| `uuid` | `ENT-B-02` |
| `shortName` | `CoffeeMachine` |
| Anzeigename | `Virtuelle Kaffeemaschine` |
| `Entity.kind` | `asset` |
| Semantische Rolle | `interactionObject` |
| UseCase-Kontext | `UC-B-01 Assistierte Kaffeemaschinenbedienung mit Vivian` |
| Primaerer Actor im Kontext | `ACT-B-01 Visitor` |
| Assistenzagent im Kontext | `ENT-B-01 VivianAssistant` |
| Fachliche Beschreibung | Bedienbares virtuelles Objekt mit Bereitschaftsmerkmalen, Betriebszustaenden, sichtbarem Feedback und einem fachlich startbaren Bruehvorgang. |
| Capabilities | noch nicht instanziiert; Kandidaten werden in Task 8.9 angelegt |
| RuntimeBinding / RuntimeAction | keine direkte Beziehung; technische Bindung folgt erst in Task 8.10 und 8.11 |

## Begruendung fuer `Entity.kind = asset`

| Option | Entscheidung | Begruendung |
| --- | --- | --- |
| `asset` | gewaehlt | Die Kaffeemaschine ist ein virtuelles Szenenobjekt, das bedient und beobachtet wird. Ihre Zustaende sind fachlich relevant. |
| `system` | nicht gewaehlt fuer die Entity selbst | Systemische Logik wie Bereitschaftspruefung oder Startausloesung wird spaeter als Capability modelliert. Die Kaffeemaschine selbst bleibt das bediente Objekt. |
| `user` | nicht gewaehlt | Die Kaffeemaschine repraesentiert keinen Benutzer und keine externe Benutzerrolle. |
| `environment` | nicht gewaehlt | Die Kaffeemaschine ist kein diffuser Umgebungskontext, sondern ein konkretes Interaktionsobjekt. |

`asset` schliesst nicht aus, dass die Kaffeemaschine technisch durch Systemsoftware umgesetzt wird. Es trennt nur die fachliche Objektidentitaet von der technischen Ausfuehrung.

## Objektzustand als Modellgegenstand

Die folgenden Zustandsdimensionen gehoeren fachlich zu `ENT-B-02 CoffeeMachine`. Sie sind keine technischen Variablen, sondern pruefbare Aussagen, die in Conditions, Events und StateAssertions genutzt werden duerfen.

| Zustandsdimension | Beispielausdruecke | Modellierungsstelle |
| --- | --- | --- |
| Verfuegbarkeit | `CoffeeMachine.availabilityState = available` | Scenario-Precondition, Guard, ValidationCase |
| Energie-/Aktivzustand | `CoffeeMachine.powerState = on` | Scenario-Precondition |
| Lebenszyklus | `CoffeeMachine.lifecycleState = idle`, `ready`, `notReady`, `brewing`, `finished`, `error` | Condition und StateAssertion |
| Bereitschaftsmerkmale | `CoffeeMachine.waterLevel = sufficient`, `CoffeeMachine.cupPresent = true`, `CoffeeMachine.selectedProgram = coffee` | Guard und StateAssertion |
| Startfreigabe | `CoffeeMachine.startPermission = allowed` oder `blocked` | Guard und StateAssertion |
| Bedienfeedback | `CoffeeMachine.readyFeedback = visible`, `progressIndicator = visible`, `completionFeedback = visible` | Event, StateAssertion und ValidationCase |
| Sicherer Zustand | `CoffeeMachine.safeState = true`, `CoffeeMachine.lifecycleState != brewing` | Exception-Postcondition und StateAssertion |

Diese Zustandsdimensionen sind orthogonal. Insbesondere ist `lifecycleState = brewing` nicht dasselbe wie `progressIndicator = visible`, und `cupPresent = true` ist nicht dasselbe wie `Cup.state = placed`.

## Direkte Verwendung als subjectRef

| Artefaktart | Beispiele fuer Referenzen auf `ENT-B-02 CoffeeMachine` | Bedeutung |
| --- | --- | --- |
| `Condition` | `B-MAIN-PRE-02`, `B-MAIN-PRE-03`, `B-MAIN-PRE-04`, `B-MAIN-G03`, `B-MAIN-G04`, `B-MAIN-G06`, `B-MAIN-G08`, `B-MAIN-G09`, `B-MAIN-G10`, `B-MAIN-G11` | Bedingungen ueber Verfuegbarkeit, Betriebszustand, Bereitschaft, Startfreigabe und Abschluss. |
| `Event` | `B-E04`, `B-E06`, `B-E09`, `B-E13`, `B-E14`, `B-E15`, `B-E16` | Beobachtbare Objektzustandswechsel oder Objektfeedback. |
| `StateAssertion` | `SA-B-CM-CUP-PRESENT`, `SA-B-CM-PROGRAM-COFFEE`, `SA-B-CM-READY`, `SA-B-CM-START-PERMISSION`, `SA-B-CM-BREWING`, `SA-B-CM-FINISHED` | Erwartete oder beobachtete Kaffeemaschinenzustaende. |
| Exception-StateAssertions | `SA-B-CM-WATER-LOW`, `SA-B-CM-NOT-READY`, `SA-B-CM-START-BLOCKED`, `SA-B-CM-SAFE`, `SA-B-CM-NOT-BREWING` | Sicherer und erklaerbarer Nicht-Start bei fehlender Bereitschaft. |

## Kontextentitaeten, aber nicht Teil von Task 8.4

| Kandidat | Status | Grund |
| --- | --- | --- |
| `ENT-B-03 Cup` | Kandidat, noch nicht als vollstaendige Entity-Instanz in diesem Task angelegt | Die Tasse ist ein relevantes Kontextobjekt, aber Task 8.4 fokussiert die Kaffeemaschine. |
| `ENT-B-04 BrewingRequest` | Kandidat, noch nicht als vollstaendige Entity-Instanz in diesem Task angelegt | Der Startwunsch ist fuer Request-Zustaende wichtig, wird aber spaeter mit ScenarioSteps, Conditions und CapabilityUses konsolidiert. |
| `ENT-B-05 VisitorEmbodiment` | nicht instanziiert | Die Benutzerrolle reicht fuer den aktuellen Use Case; ein Avatarzustand ist nicht noetig. |

Diese Kandidaten bleiben konsistent referenzierbar, werden aber nicht mit der Kaffeemaschine vermischt.

## Keine Verwechslung mit RuntimeAction

| Fachliche Aussage | Zulaessige Modellierung | Nicht zulaessig in Task 8.4 |
| --- | --- | --- |
| Die Kaffeemaschine ist bereit. | `StateAssertion.subjectRef = ENT-B-02`, `expectedState = CoffeeMachine.lifecycleState = ready` | `CoffeeMachineController.checkReady()` als Entity-Eigenschaft |
| Die Tasse ist erkannt. | `Condition.expression = CoffeeMachine.cupPresent = true` oder `SA-B-CM-CUP-PRESENT` | Sensor-API, Raycast-Hitbox oder Event-Topic in der Entity |
| Das Kaffeeprogramm ist gewaehlt. | `CoffeeMachine.selectedProgram = coffee` | UI-Widget-ID, Button-Component oder Controller-Methode |
| Der Bruehvorgang laeuft. | `CoffeeMachine.lifecycleState = brewing` | Direkter Verweis auf `RA-B-COFFEE-START` aus einem ScenarioStep |
| Fortschritt ist sichtbar. | `CoffeeMachine.progressIndicator = visible` | AnimationClip, Shader, Timeline oder konkreter Renderingaufruf |

Der technische Startaufruf darf spaeter existieren, aber nur in der erlaubten Kette:

`ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

Nicht erlaubt ist:

`ScenarioStep -> RuntimeAction`

und ebenfalls nicht:

`Entity(CoffeeMachine) = RuntimeAction`

## Vorbereitete Capability-Kandidaten ohne Instanziierung

Die Entity kann spaeter fachliche Capabilities bereitstellen oder an ihnen beteiligt sein. In Task 8.4 werden diese Capabilities noch nicht instanziiert.

| Kandidat | Voraussichtliche Modellierungsstelle | Warum noch nicht hier? |
| --- | --- | --- |
| `CAP-B-CHECK-MACHINE-READY` | Task 8.9 | Capabilities muessen Intent, Preconditions und Effects erhalten. |
| `CAP-B-START-BREWING` | Task 8.9 | Der Bruehstart braucht eigene Effects und spaeter RuntimeBinding. |
| `CAP-B-SHOW-BREWING-PROGRESS` | Task 8.9 | Fortschrittsfeedback ist fachlich, aber noch keine RuntimeAction. |
| `CAP-B-BLOCK-START` | Task 8.9 | Exception-Verhalten muss als sichere fachliche Faehigkeit beschrieben werden. |

## Anschluss an Scenario- und Validation-Ebene

| Ebene | Anschluss von `ENT-B-02 CoffeeMachine` |
| --- | --- |
| UseCase | Zentrales Interaktionsobjekt von `UC-B-01`. |
| Scenario | Main, Alternative und Exception duerfen `ENT-B-02` als fachliches Objekt referenzieren. |
| ScenarioStep | Maschinenreaktionen sind `environmentObservation`; der Maschinenzustand wird nicht ueber `performedBy` gesetzt. |
| Event | Maschinenzustandswechsel sind `Event.kind = environment`. |
| Condition | Bereitschaft und Startfreigabe werden als Conditions ueber `CoffeeMachine` formuliert. |
| StateAssertion | Beobachtete Maschinenzustaende werden mit `subjectRef = ENT-B-02` beschrieben. |
| Capability | Objektbezogene Faehigkeiten werden spaeter fachlich, nicht technisch, beschrieben. |
| RuntimeBinding | Technische Bindung folgt nur ueber Capabilities. |
| ValidationCase | Erwartete Outcomes duerfen `ENT-B-02`-StateAssertions pruefen. |

## Abnahmekontrolle

| Kriterium aus Task 8.4 | Erfuellung |
| --- | --- |
| Entity-Kandidat vorhanden | `ENT-B-02 CoffeeMachine` ist als `Entity` angelegt. |
| Art asset/system entschieden | `Entity.kind = asset`; systemische Logik wird nicht in die Entity verschoben, sondern spaeter als Capability modelliert. |
| Objektzustand modellierbar | Verfuegbarkeit, Lebenszyklus, Bereitschaft, Startfreigabe, Feedback und sicherer Zustand sind als fachliche Zustandsdimensionen beschrieben. |
| Objektzustand nicht mit RuntimeAction verwechselt | Controller, API, Topic, Tool, GameObject, Prefab und RuntimeAction sind explizit ausgeschlossen. |
| Nicht als Actor modelliert | Die Kaffeemaschine ist keine externe Rolle und hat keine Actor-UseCase-Beziehung. |
| Nicht als Agent modelliert | Assistenz- und Dialogverhalten bleibt bei `ENT-B-01 VivianAssistant` oder systemischen Capabilities. |
| Folge-Tasks nicht vorweggenommen | Scenario-, ScenarioStep-, Capability-, Runtime- und Validation-Instanzen bleiben fuer Task 8.5 bis 8.12 offen. |

## Konsequenz fuer Task 8.5

Task 8.5 kann nun die Scenario-Instanzen fuer B anlegen. Dabei kann `UC-B-01` genau ein Main Scenario besitzen und die vorbereiteten Alternativ- und Exception-Szenarien koennen auf `ENT-B-02 CoffeeMachine` als zentrales Interaktionsobjekt Bezug nehmen.
