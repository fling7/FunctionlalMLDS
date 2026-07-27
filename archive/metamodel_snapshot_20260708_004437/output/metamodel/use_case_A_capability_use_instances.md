# Anwendungsfall A: CapabilityUse-Instanzen

Stand: 2026-07-07

Task: 4.10 `CapabilityUse-Instanzen fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

`ScenarioStep -> CapabilityUse [0..*]` ist eine Komposition: Ein fachlicher Schritt kann keine, eine oder mehrere Faehigkeitsnutzungen besitzen. Eine `CapabilityUse` referenziert genau eine fachliche `Capability`.

Task 4.10 legt nur die Nutzung fachlicher Faehigkeiten an. Die referenzierten Capability-IDs werden als geplante Ziel-IDs vorbereitet und in Task 4.11 formal als `Capability`-Instanzen angelegt. Eine `CapabilityUse` darf keine RuntimeAction, API, Topic, Tool- oder Controllerdaten enthalten.

Fuer Anwendungsfall A gilt:

- `environmentObservation`-Steps beobachten oder stellen fachliche Zustaende fest und benoetigen keine CapabilityUse.
- `systemResponse`-Steps modellieren fachliche System- oder Agentenreaktionen und benoetigen CapabilityUses.
- Die technische Ausfuehrung bleibt fuer `RuntimeBinding -> RuntimeAction` in spaeteren Tasks reserviert.

## Angelegte CapabilityUse-Instanzen

| CapabilityUse-ID | Owner-Scenario | Owner-Step | Step-Art | Referenzierte geplante Capability | Parameter | Fachlicher Zweck |
| --- | --- | --- | --- | --- | --- | --- |
| `A-CU-001` | `A-MAIN-SC01` | `A-MAIN-S05` | `systemResponse` | `A-CAP-ADOPT-EXECUTOR-ROLE` | `agent=AgentBody`; `targetRole=executor`; `targetZone=TargetZone` | Der Agent nimmt die Ausfuehrungsrolle an. |
| `A-CU-002` | `A-MAIN-SC01` | `A-MAIN-S06` | `systemResponse` | `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | `agent=AgentBody`; `target=TargetZone`; `obstacle=ObstacleRegion` | Der Agent fuehrt die zielgerichtete Szenenhandlung in Richtung Zielzone aus. |
| `A-CU-003` | `A-EX-SC01` | `A-EX-S02` | `systemResponse` | `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | `agent=AgentBody`; `blockedRegion=ObstacleRegion`; `target=TargetZone` | Der Agent wird bei dauerhafter Blockade sicher am Fortsetzen des Zielpfads gehindert. |

## Step-Abdeckung

| ScenarioStep | Step-Art | CapabilityUse | Entscheidung |
| --- | --- | --- | --- |
| `A-MAIN-S01` | `environmentObservation` | keine | Ereignisfeststellung; keine fachliche Systemreaktion. |
| `A-MAIN-S02` | `environmentObservation` | keine | Bereichszustand wird beobachtet. |
| `A-MAIN-S03` | `environmentObservation` | keine | Handlungsbereitschaft wird beobachtet. |
| `A-MAIN-S04` | `environmentObservation` | keine | Zielerreichbarkeit wird geprueft; Verzweigung erfolgt ueber Guards. |
| `A-MAIN-S05` | `systemResponse` | `A-CU-001` | Rollenwechsel ist eine fachliche Agentenreaktion. |
| `A-MAIN-S06` | `systemResponse` | `A-CU-002` | Zielgerichtete Handlung ist eine fachliche Agentenreaktion. |
| `A-MAIN-S07` | `environmentObservation` | keine | Zielerreichung wird beobachtet. |
| `A-MAIN-S08` | `environmentObservation` | keine | Verifikation wird als beobachtbarer Zustand modelliert; kein aktiver Systemschritt in A. |
| `A-MAIN-S09` | `environmentObservation` | keine | Rueckmeldung wird bestaetigt, aber nicht als aktiver Systemschritt modelliert. |
| `A-ALT-S01` | `environmentObservation` | keine | Temporaere Blockade wird festgestellt. |
| `A-ALT-S02` | `environmentObservation` | keine | Blockadeaufhebung wird beobachtet. |
| `A-EX-S01` | `environmentObservation` | keine | Dauerhafte Blockade wird festgestellt. |
| `A-EX-S02` | `systemResponse` | `A-CU-003` | Sicheres Hindern am Fortsetzen ist eine fachliche Agentenreaktion. |
| `A-EX-S03` | `environmentObservation` | keine | Fehlerabschluss wird beobachtet und rueckgemeldet. |

## Warum keine CapabilityUse fuer Beobachtungsschritte?

Beobachtungsschritte in Anwendungsfall A beschreiben, dass ein fachlicher Zustand festgestellt, verifiziert oder als Ergebnis sichtbar wird. Sie sind deshalb bereits durch `Event`, `Condition` und `StateAssertion` operationalisiert.

Eine aktive Mess-, Pruef- oder Feedbackfunktion koennte spaeter als zusaetzliche Capability modelliert werden. Fuer den aktuellen kompakten A-Durchlauf waere das aber eine Modellaufblaehung, weil keine technische oder fachliche Aktion ueber die Beobachtung hinaus gefordert ist.

## Keine direkte technische Kurzschaltung

| Pruefpunkt | Bewertung |
| --- | --- |
| Verweist ein ScenarioStep direkt auf eine technische Aktion? | nein |
| Enthaelt eine CapabilityUse einen Endpoint, ein Topic, ein Tool oder eine Controlleraktion? | nein |
| Referenziert jede CapabilityUse genau eine geplante Capability? | ja |
| Bleibt die technische Ausfuehrung fuer spaetere RuntimeBinding-/RuntimeAction-Tasks reserviert? | ja |

## Offene Formalisierung fuer Folgetasks

| Elementgruppe | Status nach Task 4.10 | Folgetask |
| --- | --- | --- |
| `A-CAP-ADOPT-EXECUTOR-ROLE` | geplante Capability-ID | 4.11 |
| `A-CAP-PERFORM-TARGETED-SCENE-ACTION` | geplante Capability-ID | 4.11 |
| `A-CAP-PREVENT-BLOCKED-TARGET-PROGRESS` | geplante Capability-ID | 4.11 |
| Promised Effects der Capabilities | nicht angelegt | 4.12 |
| RuntimeBindings | nicht angelegt | 4.13 |
| RuntimeActions | nicht angelegt | 4.14 |

## Abnahmekontrolle

| Kriterium aus Task 4.10 | Erfuellung |
| --- | --- |
| Benoetigte fachliche Faehigkeiten je Schritt bestimmt | Alle 14 Steps sind in der Step-Abdeckung bewertet. |
| CapabilityUse-Instanzen angelegt | `A-CU-001`, `A-CU-002`, `A-CU-003` sind angelegt. |
| Jede CapabilityUse referenziert genau eine Capability | Jede Zeile besitzt genau eine geplante Capability-ID. |
| Beobachtungsschritte begruendet ohne CapabilityUse | Alle `environmentObservation`-Steps sind explizit mit `keine` bewertet. |
| Kein ScenarioStep zeigt direkt auf RuntimeAction | ScenarioSteps verweisen nur auf CapabilityUse oder bleiben ohne CapabilityUse. |
| Keine technischen Details in CapabilityUse | Keine CapabilityUse enthaelt Endpoint, Topic, Tool, API oder Controlleraktion. |

## Konsequenz fuer Task 4.11

Task 4.11 kann nun die drei geplanten Capability-Instanzen formal anlegen. Jede Capability muss einen fachlichen Intent, fachliche Preconditions und spaeter mindestens einen promised Effect erhalten, ohne technische Endpoint-, Tool- oder Topic-Daten zu enthalten.
