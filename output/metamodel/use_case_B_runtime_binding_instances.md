# Anwendungsfall B: RuntimeBinding-Instanzen

Stand: 2026-07-07

Task: 8.10 `RuntimeBindings fuer Vivian-/VR-/Toolchain-Ausfuehrung anlegen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Modellierungsregel

Eine `RuntimeBinding` ordnet genau eine fachliche `Capability` einem technischen Laufzeitkontext zu. Sie ist die erste technische Ebene im Trace, aber noch nicht die konkrete Einzelaktion.

Fuer Anwendungsfall B gilt:

- Jede RuntimeBinding referenziert genau eine `Capability`.
- Eine `Capability` darf keine, eine oder mehrere RuntimeBindings besitzen.
- Fuer den kompakten B-Durchlauf wird je Capability genau eine RuntimeBinding angelegt.
- Konkrete Endpunkte, Topics, Tools, Controlleraufrufe und Ein-/Ausgabeschemas gehoeren nicht in Task 8.10, sondern in Task 8.11 zu `RuntimeAction`.
- Die hier angegebenen `planned RuntimeAction IDs` sind reservierte Anschlussstellen fuer Task 8.11 und noch keine formal ausgearbeiteten RuntimeAction-Instanzen.
- Kein `ScenarioStep` und keine `CapabilityUse` wird direkt an eine RuntimeAction gebunden.

Der fachliche bis technische Pfad bleibt:

`ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

## Runtime-Kontexte fuer Anwendungsfall B

| Runtime-Kontext | Rolle im B-Beispiel | Abgrenzung |
| --- | --- | --- |
| `VivianAssistantRuntime` | Technischer Kontext fuer Vivians Moduswechsel, Anleitung, Rueckfrage, Fehlererklaerung und Abschlussmeldung. | Beschreibt keinen konkreten Sprach-, Avatar-, LLM- oder UI-Aufruf. |
| `VRInteractionRuntime` | Technischer Kontext fuer die Praesentation von Hinweisen, Prompts und Objektfeedback in der virtuellen Szene. | Beschreibt keine konkrete Engine-Komponente, kein Prefab und keinen Controller. |
| `CoffeeMachineAdapterRuntime` | Technischer Kontext fuer Bereitschaftspruefung und fachlichen Bruehstart am Interaktionsobjekt. | Beschreibt keinen konkreten Maschinen-API-, Sensor- oder Controlleraufruf. |
| `FunctionalMLDSTraceRuntime` | Technischer Kontext fuer Trace- und Outcome-Synchronisation der modellierten Ausfuehrung. | Beschreibt kein Validierungs- oder Testartefakt; ValidationCases folgen in Task 8.12. |

## Angelegte RuntimeBinding-Instanzen

| RuntimeBinding-ID | Referenzierte Capability | Laufzeitkontext | Bindungszweck | Planned RuntimeAction IDs fuer Task 8.11 | Kardinalitaetsbewertung |
| --- | --- | --- | --- | --- | --- |
| `B-RB-VIVIAN-GUIDANCE-MODE` | `CAP-B-VIVIAN-ENTER-GUIDANCE` | `VivianAssistantRuntime`; `VRInteractionRuntime` | Bindet den fachlichen Wechsel in Vivians Fuehrungsmodus an eine Laufzeit, die Assistenzzustand und Szenenwahrnehmung synchron fuehren kann. | `B-RA-VIVIAN-SET-GUIDANCE-MODE`; `B-RA-VR-SYNC-ASSISTANT-STATE` | gueltig fuer 8.10: genau eine Capability referenziert. |
| `B-RB-VIVIAN-CUP-GUIDANCE` | `CAP-B-VIVIAN-GUIDE-CUP` | `VivianAssistantRuntime`; `VRInteractionRuntime` | Bindet die fachliche Tassenplatzierungsanleitung an eine Laufzeit, die Vivian-Hinweise in der Szene praesentieren kann. | `B-RA-VIVIAN-COMPOSE-CUP-GUIDANCE`; `B-RA-VR-PRESENT-CUP-GUIDANCE` | gueltig fuer 8.10: genau eine Capability referenziert. |
| `B-RB-VIVIAN-PROGRAM-GUIDANCE` | `CAP-B-VIVIAN-GUIDE-PROGRAM` | `VivianAssistantRuntime`; `VRInteractionRuntime` | Bindet die fachliche Programmauswahlanleitung an eine Laufzeit, die den naechsten Bedienhinweis passend zum Objektzustand darstellen kann. | `B-RA-VIVIAN-COMPOSE-PROGRAM-GUIDANCE`; `B-RA-VR-PRESENT-PROGRAM-GUIDANCE` | gueltig fuer 8.10: genau eine Capability referenziert. |
| `B-RB-VIVIAN-REQUEST-CONFIRMED` | `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST` | `VivianAssistantRuntime`; `FunctionalMLDSTraceRuntime` | Bindet die fachliche Bestaetigung der Bruehanforderung an eine Laufzeit, die Vivians Rueckmeldung und den Request-Zustand konsistent haelt. | `B-RA-VIVIAN-CONFIRM-BREWING-REQUEST`; `B-RA-TRACE-SYNC-REQUEST-FEEDBACK` | gueltig fuer 8.10: genau eine Capability referenziert. |
| `B-RB-COFFEE-READINESS-CHECK` | `CAP-B-CHECK-MACHINE-READY` | `CoffeeMachineAdapterRuntime`; `VRInteractionRuntime`; `FunctionalMLDSTraceRuntime` | Bindet die fachliche Bereitschaftspruefung an eine Laufzeit, die Maschinenzustand, Startfreigabe und Entscheidungsoutcome synchronisieren kann. | `B-RA-CM-EVALUATE-READINESS`; `B-RA-CM-SYNC-READINESS-RESULT`; `B-RA-TRACE-SYNC-READINESS-OUTCOME` | gueltig fuer 8.10: genau eine Capability referenziert. |
| `B-RB-VIVIAN-CONFIRMATION-PROMPT` | `CAP-B-VIVIAN-REQUEST-CONFIRMATION` | `VivianAssistantRuntime`; `VRInteractionRuntime` | Bindet Vivians fachliche Startbestaetigungsanfrage an eine Laufzeit, die eine wahrnehmbare Rueckfrage und ein bestaetigbares Szenenangebot bereitstellt. | `B-RA-VIVIAN-COMPOSE-CONFIRMATION-PROMPT`; `B-RA-VR-SHOW-CONFIRMATION-AFFORDANCE` | gueltig fuer 8.10: genau eine Capability referenziert. |
| `B-RB-COFFEE-START-BREWING` | `CAP-B-START-BREWING` | `CoffeeMachineAdapterRuntime`; `VRInteractionRuntime`; `FunctionalMLDSTraceRuntime` | Bindet den fachlichen Bruehstart an eine Laufzeit, die Startausloesung und beobachtbaren Bruehzustand synchronisieren kann. | `B-RA-CM-REQUEST-BREWING-START`; `B-RA-CM-SYNC-BREWING-STATE`; `B-RA-TRACE-SYNC-START-OUTCOME` | gueltig fuer 8.10: genau eine Capability referenziert. |
| `B-RB-VIVIAN-COMPLETION-REPORT` | `CAP-B-VIVIAN-REPORT-COMPLETION` | `VivianAssistantRuntime`; `VRInteractionRuntime` | Bindet die fachliche Abschlussmeldung an eine Laufzeit, die Vivians Abschlussfeedback sichtbar oder hoerbar machen kann. | `B-RA-VIVIAN-COMPOSE-COMPLETION-REPORT`; `B-RA-VR-PRESENT-COMPLETION-REPORT` | gueltig fuer 8.10: genau eine Capability referenziert. |
| `B-RB-VIVIAN-CUP-CORRECTION` | `CAP-B-VIVIAN-GUIDE-CUP-CORRECTION` | `VivianAssistantRuntime`; `VRInteractionRuntime` | Bindet die Korrekturanleitung im Alternativpfad an eine Laufzeit, die fehlende Tassenplatzierung erklaerbar zurueckmeldet. | `B-RA-VIVIAN-COMPOSE-CUP-CORRECTION`; `B-RA-VR-PRESENT-CUP-CORRECTION` | gueltig fuer 8.10: genau eine Capability referenziert. |
| `B-RB-VIVIAN-ERROR-EXPLANATION` | `CAP-B-VIVIAN-EXPLAIN-ERROR` | `VivianAssistantRuntime`; `VRInteractionRuntime`; `FunctionalMLDSTraceRuntime` | Bindet die fachliche Fehlererklaerung an eine Laufzeit, die Ursache, blockierten Start und Vivian-Rueckmeldung konsistent praesentieren kann. | `B-RA-VIVIAN-COMPOSE-ERROR-EXPLANATION`; `B-RA-VR-PRESENT-ERROR-EXPLANATION`; `B-RA-TRACE-SYNC-ERROR-OUTCOME` | gueltig fuer 8.10: genau eine Capability referenziert. |
| `B-RB-VIVIAN-EXCEPTION-CLOSE` | `CAP-B-VIVIAN-CLOSE-EXCEPTION` | `VivianAssistantRuntime`; `FunctionalMLDSTraceRuntime` | Bindet den fachlichen Exception-Abschluss an eine Laufzeit, die Nichtfortsetzung des Hauptpfads und sicheres Outcome nachvollziehbar synchronisiert. | `B-RA-VIVIAN-CLOSE-EXCEPTION-FEEDBACK`; `B-RA-TRACE-SYNC-EXCEPTION-CLOSED` | gueltig fuer 8.10: genau eine Capability referenziert. |

## Rueckbindung an fachliche Capabilities

| Capability-ID | RuntimeBinding-ID | Fachlicher Ausloeser im Szenario | Versprochener Effect |
| --- | --- | --- | --- |
| `CAP-B-VIVIAN-ENTER-GUIDANCE` | `B-RB-VIVIAN-GUIDANCE-MODE` | `B-CU-001` in `B-MAIN-S02` | `B-EFF-VIVIAN-GUIDING` |
| `CAP-B-VIVIAN-GUIDE-CUP` | `B-RB-VIVIAN-CUP-GUIDANCE` | `B-CU-002` in `B-MAIN-S03` | `B-EFF-CUP-GUIDANCE-ISSUED` |
| `CAP-B-VIVIAN-GUIDE-PROGRAM` | `B-RB-VIVIAN-PROGRAM-GUIDANCE` | `B-CU-003` in `B-MAIN-S06` | `B-EFF-PROGRAM-GUIDANCE-ISSUED` |
| `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST` | `B-RB-VIVIAN-REQUEST-CONFIRMED` | `B-CU-004` in `B-MAIN-S10` | `B-EFF-BREWING-REQUEST-CONFIRMED` |
| `CAP-B-CHECK-MACHINE-READY` | `B-RB-COFFEE-READINESS-CHECK` | `B-CU-005` in `B-MAIN-S11` | `B-EFF-READINESS-RESULT-PRODUCED` |
| `CAP-B-VIVIAN-REQUEST-CONFIRMATION` | `B-RB-VIVIAN-CONFIRMATION-PROMPT` | `B-CU-006` in `B-MAIN-S13` | `B-EFF-CONFIRMATION-REQUESTED` |
| `CAP-B-START-BREWING` | `B-RB-COFFEE-START-BREWING` | `B-CU-007` in `B-MAIN-S15` | `B-EFF-BREWING-START-ISSUED` |
| `CAP-B-VIVIAN-REPORT-COMPLETION` | `B-RB-VIVIAN-COMPLETION-REPORT` | `B-CU-008` in `B-MAIN-S20` | `B-EFF-COMPLETION-REPORTED` |
| `CAP-B-VIVIAN-GUIDE-CUP-CORRECTION` | `B-RB-VIVIAN-CUP-CORRECTION` | `B-CU-009` in `B-ALT-S02` | `B-EFF-CUP-CORRECTION-GUIDANCE-ISSUED` |
| `CAP-B-VIVIAN-EXPLAIN-ERROR` | `B-RB-VIVIAN-ERROR-EXPLANATION` | `B-CU-010` in `B-EX-S02` | `B-EFF-ERROR-EXPLAINED` |
| `CAP-B-VIVIAN-CLOSE-EXCEPTION` | `B-RB-VIVIAN-EXCEPTION-CLOSE` | `B-CU-011` in `B-EX-S04` | `B-EFF-EXCEPTION-CLOSED` |

## Warum genau eine RuntimeBinding pro Capability?

Das Metamodell erlaubt `Capability -> RuntimeBinding [0..*]`, weil dieselbe fachliche Faehigkeit auf keiner, einer oder mehreren technischen Plattformen gebunden werden kann. Fuer den kompakten B-Durchlauf wird pro Capability genau eine Binding-Instanz angelegt.

Diese Entscheidung ist ausreichend, weil das Beispiel nicht mehrere konkrete Vivian-, VR- oder Kaffeemaschinenplattformen vergleicht. Mehrere Bindings waeren erst noetig, wenn dieselbe Capability parallel fuer verschiedene Engines, Simulationsprofile, Assistenzdienste oder Maschinenadapter modelliert werden soll.

## Abgrenzung zu RuntimeAction

Die RuntimeBinding benennt den technischen Bindungskontext und die Zuordnung zur fachlichen Capability. Sie fuehrt noch keine Einzelaktion aus.

| Element | Darf in 8.10 vorkommen? | Grund |
| --- | --- | --- |
| Laufzeitkontext | ja | Die Binding-Ebene muss wissen, fuer welche technische Umgebung die Capability gebunden wird. |
| Capability-Referenz | ja | Jede RuntimeBinding muss genau eine fachliche Capability referenzieren. |
| Planned RuntimeAction ID | ja | Reservierte IDs sichern die Anschlussfaehigkeit fuer Task 8.11. |
| Konkreter Aufrufname | nein | Gehoert zu `RuntimeAction`. |
| Input- oder Output-Schema | nein | Gehoert zu `RuntimeAction`. |
| Direkte Referenz vom ScenarioStep | nein | Wuerde die fachliche Ablaufebene technisch kurzschliessen. |
| Direkte Referenz von CapabilityUse auf RuntimeBinding | nein | `CapabilityUse` bleibt fachlich und referenziert nur `Capability`. |

## Vorbereitete RuntimeAction-Anschlussstellen fuer 8.11

| RuntimeBinding-ID | Reservierte RuntimeAction-ID | Erwarteter Zweck in Task 8.11 |
| --- | --- | --- |
| `B-RB-VIVIAN-GUIDANCE-MODE` | `B-RA-VIVIAN-SET-GUIDANCE-MODE` | Technische Einzelaktion zum Setzen von Vivians Assistenzmodus. |
| `B-RB-VIVIAN-GUIDANCE-MODE` | `B-RA-VR-SYNC-ASSISTANT-STATE` | Technische Einzelaktion zur Szenensynchronisation des Assistenzzustands. |
| `B-RB-VIVIAN-CUP-GUIDANCE` | `B-RA-VIVIAN-COMPOSE-CUP-GUIDANCE` | Technische Einzelaktion zum Erzeugen des Tassenhinweises. |
| `B-RB-VIVIAN-CUP-GUIDANCE` | `B-RA-VR-PRESENT-CUP-GUIDANCE` | Technische Einzelaktion zur Praesentation des Tassenhinweises in der Szene. |
| `B-RB-VIVIAN-PROGRAM-GUIDANCE` | `B-RA-VIVIAN-COMPOSE-PROGRAM-GUIDANCE` | Technische Einzelaktion zum Erzeugen des Programmauswahlhinweises. |
| `B-RB-VIVIAN-PROGRAM-GUIDANCE` | `B-RA-VR-PRESENT-PROGRAM-GUIDANCE` | Technische Einzelaktion zur Praesentation des Programmauswahlhinweises. |
| `B-RB-VIVIAN-REQUEST-CONFIRMED` | `B-RA-VIVIAN-CONFIRM-BREWING-REQUEST` | Technische Einzelaktion zum Ausgeben der fachlichen Request-Bestaetigung. |
| `B-RB-VIVIAN-REQUEST-CONFIRMED` | `B-RA-TRACE-SYNC-REQUEST-FEEDBACK` | Technische Einzelaktion zur Trace-Synchronisation der Request-Bestaetigung. |
| `B-RB-COFFEE-READINESS-CHECK` | `B-RA-CM-EVALUATE-READINESS` | Technische Einzelaktion zur Ermittlung des Bereitschaftsergebnisses. |
| `B-RB-COFFEE-READINESS-CHECK` | `B-RA-CM-SYNC-READINESS-RESULT` | Technische Einzelaktion zur Synchronisation des Maschinen-Readiness-Zustands. |
| `B-RB-COFFEE-READINESS-CHECK` | `B-RA-TRACE-SYNC-READINESS-OUTCOME` | Technische Einzelaktion zur Trace-Synchronisation des positiven oder negativen Readiness-Outcomes. |
| `B-RB-VIVIAN-CONFIRMATION-PROMPT` | `B-RA-VIVIAN-COMPOSE-CONFIRMATION-PROMPT` | Technische Einzelaktion zum Erzeugen der Startbestaetigungsfrage. |
| `B-RB-VIVIAN-CONFIRMATION-PROMPT` | `B-RA-VR-SHOW-CONFIRMATION-AFFORDANCE` | Technische Einzelaktion zur Anzeige des bestaetigbaren Szenenangebots. |
| `B-RB-COFFEE-START-BREWING` | `B-RA-CM-REQUEST-BREWING-START` | Technische Einzelaktion zum Anfordern des Bruehstarts. |
| `B-RB-COFFEE-START-BREWING` | `B-RA-CM-SYNC-BREWING-STATE` | Technische Einzelaktion zur Synchronisation des Bruehzustands. |
| `B-RB-COFFEE-START-BREWING` | `B-RA-TRACE-SYNC-START-OUTCOME` | Technische Einzelaktion zur Trace-Synchronisation des Start-Outcomes. |
| `B-RB-VIVIAN-COMPLETION-REPORT` | `B-RA-VIVIAN-COMPOSE-COMPLETION-REPORT` | Technische Einzelaktion zum Erzeugen der Abschlussmeldung. |
| `B-RB-VIVIAN-COMPLETION-REPORT` | `B-RA-VR-PRESENT-COMPLETION-REPORT` | Technische Einzelaktion zur Praesentation der Abschlussmeldung. |
| `B-RB-VIVIAN-CUP-CORRECTION` | `B-RA-VIVIAN-COMPOSE-CUP-CORRECTION` | Technische Einzelaktion zum Erzeugen der Korrekturanleitung. |
| `B-RB-VIVIAN-CUP-CORRECTION` | `B-RA-VR-PRESENT-CUP-CORRECTION` | Technische Einzelaktion zur Praesentation der Korrekturanleitung. |
| `B-RB-VIVIAN-ERROR-EXPLANATION` | `B-RA-VIVIAN-COMPOSE-ERROR-EXPLANATION` | Technische Einzelaktion zum Erzeugen der Fehlererklaerung. |
| `B-RB-VIVIAN-ERROR-EXPLANATION` | `B-RA-VR-PRESENT-ERROR-EXPLANATION` | Technische Einzelaktion zur Praesentation der Fehlererklaerung. |
| `B-RB-VIVIAN-ERROR-EXPLANATION` | `B-RA-TRACE-SYNC-ERROR-OUTCOME` | Technische Einzelaktion zur Trace-Synchronisation des Fehler-Outcomes. |
| `B-RB-VIVIAN-EXCEPTION-CLOSE` | `B-RA-VIVIAN-CLOSE-EXCEPTION-FEEDBACK` | Technische Einzelaktion zum Ausgeben des Exception-Abschlussfeedbacks. |
| `B-RB-VIVIAN-EXCEPTION-CLOSE` | `B-RA-TRACE-SYNC-EXCEPTION-CLOSED` | Technische Einzelaktion zur Trace-Synchronisation des abgeschlossenen Exception-Pfads. |

## Kardinalitaetspruefung fuer 8.10

| Pruefpunkt | Ergebnis |
| --- | --- |
| Anzahl RuntimeBindings | 11 |
| Jede RuntimeBinding referenziert genau eine Capability | ja |
| Jede referenzierte Capability existiert aus Task 8.9 | ja |
| Jede referenzierte Capability hat einen promised Effect | ja |
| Jede B-Capability besitzt in diesem Beispiel genau eine RuntimeBinding | ja |
| RuntimeAction-Details bleiben in Task 8.11 | ja |

## Keine technische Kurzschaltung

| Verbotene Kurzschaltung | Bewertung |
| --- | --- |
| `ScenarioStep -> RuntimeBinding` | nicht vorhanden. |
| `ScenarioStep -> RuntimeAction` | nicht vorhanden. |
| `CapabilityUse -> RuntimeBinding` | nicht vorhanden; CapabilityUse referenziert nur `Capability`. |
| `Capability` mit konkreten Einzelaktionsdaten | nicht vorhanden; Einzelaktionsdetails bleiben fuer `RuntimeAction`. |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 8.10 | Folgetask |
| --- | --- | --- |
| `RuntimeAction`-Instanzen | IDs reserviert, Details nicht angelegt | 8.11 |
| `ValidationCase` | nicht angelegt | 8.12 |
| Finale Kardinalitaetspruefung inklusive RuntimeAction-Komposition | vorbereitet | 8.13 |

## Abnahmekontrolle

| Kriterium aus Task 8.10 | Erfuellung |
| --- | --- |
| Technische Bindungen vorhanden | Elf RuntimeBindings sind angelegt. |
| Jede Binding referenziert genau eine fachliche Capability | Jede Binding-Zeile besitzt genau eine Capability-Referenz. |
| Vivian-/VR-/Toolchain-Ausfuehrung ist abbildbar | Runtime-Kontexte fuer Vivian, VR-Interaktion, Kaffeemaschinenadapter und Trace-Synchronisation sind beschrieben. |
| Keine RuntimeAction-Details vorweggenommen | Es gibt nur reservierte Anschluss-IDs fuer Task 8.11. |
| Trace vom ScenarioStep bleibt indirekt | Der Pfad laeuft weiterhin ueber CapabilityUse und Capability. |

## Konsequenz fuer Task 8.11

Task 8.11 kann nun die reservierten RuntimeAction-IDs formal als technische Aktionen ausarbeiten. Dann muss jede der elf RuntimeBindings mindestens eine konkrete RuntimeAction besitzen; in diesem Entwurf sind insgesamt 25 RuntimeAction-Anschlussstellen vorbereitet.
