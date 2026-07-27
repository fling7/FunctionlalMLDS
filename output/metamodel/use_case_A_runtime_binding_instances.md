# Anwendungsfall A: RuntimeBinding-Instanzen

Stand: 2026-07-07

Task: 4.13 `RuntimeBinding-Instanzen fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

Eine `RuntimeBinding` ordnet genau eine fachliche `Capability` einer technischen Laufzeitbindung zu. Sie ist damit die erste technische Ebene im Trace, aber noch nicht die konkrete Einzelaktion.

Fuer Anwendungsfall A gilt:

- Jede RuntimeBinding referenziert genau eine `Capability`.
- Eine `Capability` darf keine, eine oder mehrere RuntimeBindings besitzen. In diesem Beispiel bekommt jede der drei A-Capabilities genau eine generische VR-Szenenbindung.
- Konkrete Endpunkte, Topics, Tools, Controlleraufrufe und Ein-/Ausgabeschemas gehoeren nicht in Task 4.13, sondern in Task 4.14 zu `RuntimeAction`.
- Die hier angegebenen `planned RuntimeAction IDs` sind reservierte Anschlussstellen fuer Task 4.14 und noch keine formal ausgearbeiteten RuntimeAction-Instanzen.
- Kein `ScenarioStep` und keine `CapabilityUse` wird direkt an eine RuntimeAction gebunden.

Der fachliche bis technische Pfad bleibt damit:

`ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

## Angelegte RuntimeBinding-Instanzen

| RuntimeBinding-ID | Referenzierte Capability | Laufzeitkontext | Bindungszweck | Planned RuntimeAction IDs fuer Task 4.14 | Kardinalitaetsbewertung |
| --- | --- | --- | --- | --- | --- |
| `A-RB-ROLE-EXECUTOR-VR` | `A-CAP-ADOPT-EXECUTOR-ROLE` | `GenericVRSceneRuntime` | Bindet den fachlichen Rollenwechsel des Agenten an eine VR-Szenenlaufzeit, die Agentenzustand und Rollenzustand synchron fuehrt. | `A-RA-ROLE-SET`; `A-RA-ROLE-SYNC` | gueltig fuer 4.13: genau eine Capability referenziert. |
| `A-RB-TARGET-ACTION-VR` | `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `GenericVRSceneRuntime` | Bindet die zielgerichtete Agentenhandlung an eine VR-Szenenlaufzeit, die Agentenbewegung und Zielzonenbelegung technisch ausfuehrbar macht. | `A-RA-TARGET-ACTION-REQUEST`; `A-RA-TARGET-OCCUPANCY-SYNC` | gueltig fuer 4.13: genau eine Capability referenziert. |
| `A-RB-BLOCKED-PROGRESS-VR` | `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `GenericVRSceneRuntime` | Bindet das sichere Stoppen eines blockierten Zielpfads an eine VR-Szenenlaufzeit, die Agentenfortschritt und Blockadezustand konsistent haelt. | `A-RA-BLOCK-PROGRESS-HOLD`; `A-RA-BLOCK-STATE-SYNC` | gueltig fuer 4.13: genau eine Capability referenziert. |

## Rueckbindung an fachliche Capabilities

| Capability-ID | RuntimeBinding-ID | Fachlicher Ausloeser im Szenario | Versprochene Effects |
| --- | --- | --- | --- |
| `A-CAP-ADOPT-EXECUTOR-ROLE` | `A-RB-ROLE-EXECUTOR-VR` | `A-CU-001` in `A-MAIN-S05` | `A-EFF-ROLE-EXECUTOR`; `A-EFF-AGENT-ACTING` |
| `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `A-RB-TARGET-ACTION-VR` | `A-CU-002` in `A-MAIN-S06` | `A-EFF-AGENT-MOVING-TO-TARGET`; `A-EFF-TARGET-OCCUPIED` |
| `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `A-RB-BLOCKED-PROGRESS-VR` | `A-CU-003` in `A-EX-S02` | `A-EFF-AGENT-WAITING`; `A-EFF-ROLE-BLOCKED` |

## Warum genau eine RuntimeBinding pro Capability?

Das Metamodell erlaubt `Capability -> RuntimeBinding [0..*]`, weil eine fachliche Faehigkeit auf keiner, einer oder mehreren technischen Plattformen gebunden werden kann. Fuer den kompakten A-Durchlauf wird je Capability genau eine generische VR-Szenenbindung angelegt.

Das ist ausreichend, weil Anwendungsfall A noch keine konkrete Plattformvariante vergleicht. Mehrere RuntimeBindings waeren erst noetig, wenn dieselbe Capability parallel z. B. fuer verschiedene Engines, Simulationen oder Ausfuehrungsprofile modelliert werden soll.

## Abgrenzung zu RuntimeAction

Die RuntimeBinding benennt den technischen Bindungskontext und die Zuordnung zur fachlichen Capability. Sie fuehrt noch keine Einzelaktion aus.

| Element | Darf in 4.13 vorkommen? | Grund |
| --- | --- | --- |
| Laufzeitkontext | ja | Die Binding-Ebene muss wissen, fuer welche technische Umgebung die Capability gebunden wird. |
| Capability-Referenz | ja | Jede RuntimeBinding muss genau eine fachliche Capability referenzieren. |
| Planned RuntimeAction ID | ja | Reservierte IDs sichern die Anschlussfaehigkeit fuer Task 4.14. |
| Konkreter Aufrufname | nein | Gehoert zu `RuntimeAction`. |
| Input- oder Output-Schema | nein | Gehoert zu `RuntimeAction`. |
| Direkte Referenz vom ScenarioStep | nein | Wuerde die fachliche Ablaufebene technisch kurzschliessen. |

## Vorbereitete RuntimeAction-Anschlussstellen fuer 4.14

| RuntimeBinding-ID | Reservierte RuntimeAction-ID | Erwarteter Zweck in Task 4.14 |
| --- | --- | --- |
| `A-RB-ROLE-EXECUTOR-VR` | `A-RA-ROLE-SET` | Technische Einzelaktion zum Setzen des Agentenrollenzustands. |
| `A-RB-ROLE-EXECUTOR-VR` | `A-RA-ROLE-SYNC` | Technische Einzelaktion zur Rueckmeldung des synchronisierten Agentenzustands. |
| `A-RB-TARGET-ACTION-VR` | `A-RA-TARGET-ACTION-REQUEST` | Technische Einzelaktion zum Anfordern der zielgerichteten Agentenhandlung. |
| `A-RB-TARGET-ACTION-VR` | `A-RA-TARGET-OCCUPANCY-SYNC` | Technische Einzelaktion zur Synchronisierung der Zielzonenbelegung. |
| `A-RB-BLOCKED-PROGRESS-VR` | `A-RA-BLOCK-PROGRESS-HOLD` | Technische Einzelaktion zum Halten des Agenten in einem sicheren Wartezustand. |
| `A-RB-BLOCKED-PROGRESS-VR` | `A-RA-BLOCK-STATE-SYNC` | Technische Einzelaktion zur Synchronisierung des blockierten Rollenzustands. |

## Kardinalitaetspruefung fuer 4.13

| Pruefpunkt | Ergebnis |
| --- | --- |
| Anzahl RuntimeBindings | 3 |
| Jede RuntimeBinding referenziert genau eine Capability | ja |
| Jede referenzierte Capability existiert aus Task 4.11 | ja |
| Jede referenzierte Capability hat Effects aus Task 4.12 | ja |
| Jede A-Capability besitzt in diesem Beispiel genau eine RuntimeBinding | ja |
| RuntimeAction-Details bleiben in Task 4.14 | ja |

## Keine technische Kurzschaltung

| Verbotene Kurzschaltung | Bewertung |
| --- | --- |
| `ScenarioStep -> RuntimeBinding` | nicht vorhanden. |
| `ScenarioStep -> RuntimeAction` | nicht vorhanden. |
| `CapabilityUse -> RuntimeBinding` | nicht vorhanden; CapabilityUse referenziert nur `Capability`. |
| `Capability` mit konkreten Einzelaktionsdaten | nicht vorhanden; Einzelaktionsdetails bleiben fuer `RuntimeAction`. |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 4.13 | Folgetask |
| --- | --- | --- |
| `RuntimeAction`-Instanzen | IDs reserviert, Details nicht angelegt | 4.14 |
| `ValidationCase` | nicht angelegt | 4.15 |
| Finale Kardinalitaetspruefung inklusive RuntimeAction-Komposition | vorbereitet | 4.16 |

## Abnahmekontrolle

| Kriterium aus Task 4.13 | Erfuellung |
| --- | --- |
| Technische Bindungen je Capability vorhanden | Drei RuntimeBindings sind angelegt. |
| Jede RuntimeBinding referenziert genau eine Capability | Jede Binding-Zeile besitzt genau eine Capability-Referenz. |
| Keine RuntimeAction-Details vorweggenommen | Es gibt nur reservierte Anschluss-IDs fuer Task 4.14. |
| Trace vom ScenarioStep bleibt indirekt | Der Pfad laeuft weiterhin ueber CapabilityUse und Capability. |

## Konsequenz fuer Task 4.14

Task 4.14 kann nun die reservierten RuntimeAction-IDs formal als technische Aktionen ausarbeiten. Dann muss jede der drei RuntimeBindings mindestens eine konkrete RuntimeAction besitzen; in diesem Entwurf sind jeweils zwei RuntimeAction-Anschlussstellen vorbereitet.
