# Anwendungsfall A: Ausfuehrende oder beobachtete Entitaeten

Stand: 2026-07-07

Task: 2.4 `Ausfuehrende oder beobachtete Entitaeten bestimmen`

Zweckbezug: Der Anwendungsfall beschreibt dynamisches Agentenverhalten in einer virtuellen Szene. Dieser Task bestimmt Kandidaten fuer `Entity` und `Agent`, ohne bereits konkrete Szenenobjekte, Ereignisse oder Capabilities vollstaendig auszuarbeiten.

## Grundentscheidung

Ein `Agent` ist eine spezialisierte `Entity`. Deshalb werden Agent-Kandidaten ebenfalls mit `Entity.kind` typisiert. Die Typisierung verwendet ausschliesslich die in der v0.5-Spezifikation vorgesehenen Werte:

- `agent`
- `asset`
- `zone`
- `signal`
- `stateObject`

Fruehere Unterscheidungen wie Benutzer-, System- oder Umgebungskontext bleiben fachlich in der Beschreibung erhalten. Sie sind aber keine `EntityKind`-Werte des finalen Kernmodells.

Die folgende Liste beschreibt Kandidaten, keine finalen Instanzen. Ob alle Kandidaten im spaeteren Beispielszenario tatsaechlich verwendet werden, wird erst in den Folge-Tasks entschieden.

## Agent-Kandidaten

| Kandidat | Metamodellklasse | Entity.kind | Ausfuehrend oder beobachtet? | Beschreibung | Abgrenzung zu Actor |
| --- | --- | --- | --- | --- | --- |
| `DynamicSceneAgent` | `Agent` | `agent` | ausfuehrend und beobachtet | Systemgesteuerter Agent innerhalb der virtuellen Szene, der auf Events und Conditions reagiert und dadurch Position, Rolle, Handlung oder Zustand aendert. | Kein Actor, weil dies die ausfuehrende Entitaet ist; Actor-Rollen wie `SceneParticipant` koennen spaeter optional gespielt werden. |
| `UserEmbodiedAgent` | `Agent` | `agent` | ausfuehrend und beobachtet | Benutzerrepraesentation in der Szene, z. B. Avatar oder verkoerperte Praesenz, deren Handlungen Agentenreaktionen ausloesen oder selbst als Agentenverhalten beobachtet werden. | Der Actor waere die Rolle `SceneParticipant`; die Entitaet ist die konkrete benutzerbezogene Praesenz im Modell. |
| `SupervisorAgent` | `Agent` | `agent` | ausfuehrend | Systemischer Ueberwachungs- oder Tutor-Agent, der Korrektur, Wiederholung oder Erklaerung fachlich ausloesen kann. | Der Actor waere `TrainingSupervisor`; der Agent ist die ausfuehrende Entitaet, falls diese Rolle durch das System realisiert wird. |
| `EnvironmentReactiveAgent` | `Agent` | `agent` | beobachtet und ggf. ausfuehrend | Umgebungsgesteuerte Agentenentitaet, die auf Raeume, Zonen, Signale oder zeitliche Veraenderungen reagiert, ohne als Benutzer oder technisches Runtime-System verstanden zu werden. | Kein Actor, weil es eine modellierte Entitaet innerhalb der Szene ist; externe Ereignisquellen bleiben Rollen oder Events. |

## Entity-Kandidaten, die nicht zwingend Agenten sind

| Kandidat | Metamodellklasse | Entity.kind | Ausfuehrend oder beobachtet? | Beschreibung | Spaetere Verwendung |
| --- | --- | --- | --- | --- | --- |
| `VirtualSceneContext` | `Entity` | `stateObject` | beobachtet | Fachlicher Kontext der virtuellen Szene, soweit er Bedingungen, Ereignisse oder Zielzustaende fuer Agentenverhalten bestimmt. | Bezugspunkt fuer raeumliche oder umgebungsbezogene Conditions und StateAssertions. |
| `SceneStateController` | `Entity` | nicht gesetzt | ausfuehrend | Fachliche Systementitaet, die Szenenzustand, Ablaufsteuerung oder Agentenreaktionen orchestriert, ohne selbst konkrete Runtime-Implementierung zu sein. | Kann spaeter Capabilities bereitstellen, bleibt aber von RuntimeAction getrennt; `Entity.kind` ist optional. |
| `TargetZone` | `Entity` | `zone` | beobachtet | Markierbarer Zielbereich oder Zielpunkt in der Szene, gegen den Agentenposition oder Erreichbarkeit geprueft werden kann. | Wahrscheinliches Subjekt von `Condition` oder `StateAssertion`, z. B. Agent befindet sich in Zielzone. |
| `TriggerZone` | `Entity` | `zone` | beobachtet | Raeumlicher oder logischer Bereich, dessen Betreten, Verlassen oder Aktivierung ein Event ausloesen kann. | Quelle fuer raeumliche Events oder Guards. |
| `InteractionAsset` | `Entity` | `asset` | beobachtet und ggf. ausfuehrungsrelevant | Generischer interaktionsrelevanter Gegenstand der Szene, dessen Zustand Agentenverhalten ausloesen oder beeinflussen kann. | Detaillierung folgt in Task 2.5, wenn relevante Szenenobjekte gesammelt werden. |
| `ObservationChannel` | `Entity` | `signal` | beobachtet | Fachliche Beobachtungs- oder Monitoring-Entitaet, die fuer Validierung oder Zustandspruefung relevant ist. | Kann spaeter ValidationCases oder StateAssertions stuetzen, ohne selbst Actor zu sein. |
| `ExternalSignalSource` | `Entity` | `signal` | beobachtet | Umgebungssignal oder externer Ausloeser, der als fachliche Entitaet modelliert werden kann, wenn eine blosse Actor-Rolle `ExternalEventSource` nicht praezise genug ist. | Kann spaeter Event-Subjekt oder Event-Kontext werden. |

## Bewusst nicht als Entity/Agent aufgenommen

| Nicht-Kandidat | Grund | Spaetere Behandlung |
| --- | --- | --- |
| `ScenarioDesigner` als Person | In Task 2.3 als Actor-Rolle bestimmt; konkrete Person oder Toolinstanz ist fuer Anwendungsfall A nicht erforderlich. | Bleibt Actor, solange keine beobachtete oder ausfuehrende Entitaet im Szenario benoetigt wird. |
| Unity-, WebXR- oder Engine-Instanz | Technische Plattform, nicht fachliche Entity des dynamischen Agentenmodells. | Spaeter nur ueber `RuntimeBinding` und `RuntimeAction`. |
| Pathfinding-Komponente | Algorithmisches Implementierungsdetail. | Out of Scope; fachlich nur Ziel, Bedingung und Effekt modellieren. |
| Vollstaendige 3D-Szene als Asset-Liste | Zu breit fuer Task 2.4 und teilweise out of scope. | Task 2.5 sammelt nur relevante Szenenobjekte mit Zustand oder Interaktion. |

## Abnahmekontrolle

| Kriterium aus Task 2.4 | Erfuellung |
| --- | --- |
| Kandidaten fuer `Entity` bestimmt | `VirtualSceneContext`, `SceneStateController`, `TargetZone`, `TriggerZone`, `InteractionAsset`, `ObservationChannel`, `ExternalSignalSource` |
| Kandidaten fuer `Agent` bestimmt | `DynamicSceneAgent`, `UserEmbodiedAgent`, `SupervisorAgent`, `EnvironmentReactiveAgent` |
| Alle gesetzten `Entity.kind`-Werte gehoeren zur v0.5-Enumeration | Gesetzte Werte sind `agent`, `asset`, `zone`, `signal` oder `stateObject`; `SceneStateController` bleibt bewusst untypisiert, weil `Entity.kind` optional ist. |
| Trennung zu Actor gewahrt | Jede Agent-Zeile grenzt sich gegen Actor-Rollen ab; Actor-Kandidaten aus Task 2.3 bleiben Rollen. |
| Runtime-Ausfuehrung nicht vorweggenommen | Runtime-Plattformen und konkrete Engine-Instanzen sind explizit ausgeschlossen. |

## Konsequenz fuer Task 2.5

Task 2.5 kann auf diesen Kandidaten aufbauen und die wirklich relevanten Szenenobjekte als fachliche Gegenstaende erfassen. Besonders wahrscheinlich sind:

- `TargetZone`,
- `TriggerZone`,
- `InteractionAsset`,
- beobachtbare Zustaende von `DynamicSceneAgent`,
- beobachtbare Zustaende von `VirtualSceneContext`.
