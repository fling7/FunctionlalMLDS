# Entscheidung 10.5: Reichen `Capability` und `RuntimeBinding` fuer Vivian-Aktionen aus?

Stand: 2026-07-07

Task: 10.5 `Pruefen, ob Capability/RuntimeBinding fuer Vivian-Aktionen ausreicht`

Use Case:

- `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Bezugsdateien:

- `dynamic_functional_mlds_specification.md`
- `invariants.md`
- `differences_A_B.md`
- `state_assertion_object_state_decision.md`
- `use_case_B_vivian_classification.md`
- `use_case_B_capability_use_instances.md`
- `use_case_B_capability_instances.md`
- `use_case_B_runtime_binding_instances.md`
- `use_case_B_runtime_action_instances.md`
- `use_case_B_validation_case_instances.md`
- `use_case_B_gap_decision_matrix.md`

## Entscheidung

`Capability` und `RuntimeBinding` reichen fuer Vivians Baseline-Aktionen aus, wenn Vivian-Aktionen als fachliche Systemreaktionen mit technischen Bindungen modelliert werden.

Sie reichen nicht aus, wenn Vivians Dialogverhalten selbst als eigenstaendige, maschinenlesbare Dialogstruktur mit Dialogakten, Inhalt, Modalitaet, Sprache, Wiederholung, Turn-Taking, Antwortoptionen, Personalisierung oder Erklaerstrategie modelliert werden soll.

Damit lautet die Entscheidung:

| Frage | Entscheidung |
| --- | --- |
| Reicht `Capability` fuer Vivians fachliche Faehigkeit? | ja |
| Reicht `RuntimeBinding` fuer die Bindung an Vivian-/VR-/Trace-Runtimes? | ja |
| Reicht `RuntimeAction` fuer konkrete technische Ausgaben, Endpoints, Topics und Schemas? | ja |
| Reicht `Capability` fuer strukturiertes Dialogverhalten? | nein |
| Reicht `RuntimeBinding` fuer Dialogstrategie oder GuidanceContent? | nein |
| Muss der Kern deshalb erweitert werden? | nein |
| Empfohlene Behandlung fuer Dialogdetails | optionales `AssistantInteractionModule` |

Die Kernregel bleibt:

`ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

Vivian darf in dieser Kette nicht als technische Abkuerzung benutzt werden. Benutzerhandlungen bleiben `actorIntent` des `Visitor`; Vivian-Reaktionen bleiben `systemResponse` mit `CapabilityUse`.

## Trennung der drei Ebenen

| Ebene | Modellklasse | Aufgabe | Vivian-Beispiel | Was nicht hineingehoert |
| --- | --- | --- | --- | --- |
| Fachliche Faehigkeit | `Capability` mit `Effect` | Beschreibt, was Vivian fachlich leisten kann. | `CAP-B-VIVIAN-GUIDE-CUP` leitet zur Tassenplatzierung an. | Endpoint, Topic, Tool, TTS, Avatar, LLM-Prompt, konkreter UI-Text. |
| Dialogverhalten | aktuell nur indirekt; optionales Modul | Beschreibt, wie Vivian kommuniziert, welche Dialogakte, Inhalte, Modalitaeten und Antwortregeln gelten. | Rueckfrage, Hinweis, Fehlererklaerung, Abschlussmeldung. | Nicht vollstaendig im Kern; nicht in `Capability` hineinmodellieren. |
| Technische Aktion | `RuntimeBinding -> RuntimeAction` | Bindet eine fachliche Faehigkeit an technische Laufzeitaktionen. | `B-RA-VIVIAN-COMPOSE-CUP-GUIDANCE`; `B-RA-VR-PRESENT-CUP-GUIDANCE`. | Fachliche UseCase-Semantik oder Dialogpolitik. |

Diese Trennung ist fuer Vivian besonders wichtig, weil Vivian leicht mit drei unterschiedlichen Dingen verwechselt wird:

- Vivian als modellierte Assistenzinstanz: `Agent`/`Entity`.
- Vivian als fachliche Faehigkeitsanbieterin: `Entity -> Capability`.
- Vivian als technische Ausgabeschicht: `RuntimeBinding -> RuntimeAction`.

## Fachliche Faehigkeit

Fuer fachliche Vivian-Aktionen ist `Capability` geeignet.

| Capability | Fachliche Bedeutung | Warum `Capability` passt |
| --- | --- | --- |
| `CAP-B-VIVIAN-ENTER-GUIDANCE` | Vivian wechselt in den Fuehrungsmodus. | Beschreibt einen fachlichen Assistenzzustand und einen beobachtbaren Effect. |
| `CAP-B-VIVIAN-GUIDE-CUP` | Vivian leitet zur Tassenplatzierung an. | Beschreibt die intendierte Hilfestellung, nicht den konkreten Ausgabekanal. |
| `CAP-B-VIVIAN-GUIDE-PROGRAM` | Vivian unterstuetzt die Programmauswahl. | Trennt fachlichen Hinweis von technischer Darstellung. |
| `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST` | Vivian bestaetigt die erkannte Bruehanforderung. | Beschreibt die fachliche Rueckmeldung. |
| `CAP-B-VIVIAN-REQUEST-CONFIRMATION` | Vivian fordert eine explizite Startbestaetigung an. | Beschreibt die notwendige Benutzerfreigabe als fachliche Interaktion. |
| `CAP-B-VIVIAN-REPORT-COMPLETION` | Vivian meldet den erfolgreichen Abschluss. | Beschreibt den Abschluss als fachliche Wirkung. |
| `CAP-B-VIVIAN-GUIDE-CUP-CORRECTION` | Vivian gibt eine Korrekturanleitung. | Beschreibt eine Alternative, ohne technische UI-Regeln einzufuehren. |
| `CAP-B-VIVIAN-EXPLAIN-ERROR` | Vivian erklaert die Fehlerursache. | Beschreibt die fachliche Erklaerleistung, nicht eine konkrete Textgenerierung. |
| `CAP-B-VIVIAN-CLOSE-EXCEPTION` | Vivian schliesst den Ausnahmefall fachlich ab. | Beschreibt den fachlichen Abschluss ohne Runtime-Abbruchbefehl. |

Diese Capabilities sind im aktuellen B-Stand sauber, weil sie keine technischen Endpoint-, Topic-, Tool- oder Schema-Daten enthalten. Sie besitzen fachliche Preconditions und mindestens einen promised Effect.

## Dialogverhalten

Vivians Dialogverhalten ist nur teilweise durch `Capability`, `Effect` und `StateAssertion` abbildbar.

| Dialogaspekt | Baseline-Abbildung | Reicht? | Begruendung |
| --- | --- | --- | --- |
| Dass Vivian einen Hinweis gibt | `Capability` + `Effect` + `StateAssertion` | ja | Fuer die Baseline reicht eine fachliche Wirkung wie `Guidance issued`. |
| Dass Vivian auf Bestaetigung wartet | `CAP-B-VIVIAN-REQUEST-CONFIRMATION`; `SA-B-VIVIAN-AWAITING-CONFIRMATION` | ja | Der erwartete Zustand und die fachliche Rueckfrage sind pruefbar. |
| Dass Vivian einen Fehler erklaert | `CAP-B-VIVIAN-EXPLAIN-ERROR`; `B-EFF-ERROR-EXPLAINED` | ja | Fachlicher Grund und beobachtbarer Effekt sind ausreichend. |
| Exakter Dialogakt | indirekt ueber Capability-Name und RuntimeAction-Name | nein | Es gibt keine Klasse `DialogueAct`. |
| Inhalt und Textstruktur | RuntimeAction-Schema oder ContentRef | nein, nur technisch | Das beschreibt technische Uebergabe, nicht fachliche Inhaltssemantik. |
| Modalitaet | Runtime-Kontext oder Schemafeld `presentationMode` | nein, nur grob | Sprache, Avatar, Text, Geste und Kombinationen sind nicht fachlich typisiert. |
| Antwortoptionen und Turn-Taking | Guards, Events, StateAssertions | nein, nur verteilt | Antwortstatus, Timeout, Ablehnung, Wiederholung und Abbruchpolitik sind nicht als Dialogmodell vorhanden. |
| Personalisierung oder Didaktik | nicht formal | nein | Lernstand, Hilfestufe, Erklaerstrategie oder Adaptivitaet fehlen. |

Konsequenz: Das aktuelle Modell reicht fuer die Aussage "Vivian fuehrt, fragt, bestaetigt oder erklaert". Es reicht nicht fuer die Aussage "Vivian fuehrt einen formal spezifizierten Dialog nach einer Dialogstrategie aus".

## Technische Aktion

Fuer technische Vivian-Aktionen sind `RuntimeBinding` und `RuntimeAction` geeignet.

| RuntimeBinding | RuntimeActions | Bewertung |
| --- | --- | --- |
| `B-RB-VIVIAN-GUIDANCE-MODE` | `B-RA-VIVIAN-SET-GUIDANCE-MODE`; `B-RA-VR-SYNC-ASSISTANT-STATE` | Geeignet fuer technischen Moduswechsel und Szenensynchronisation. |
| `B-RB-VIVIAN-CUP-GUIDANCE` | `B-RA-VIVIAN-COMPOSE-CUP-GUIDANCE`; `B-RA-VR-PRESENT-CUP-GUIDANCE` | Geeignet fuer technische Erzeugung und Praesentation des Tassenhinweises. |
| `B-RB-VIVIAN-PROGRAM-GUIDANCE` | `B-RA-VIVIAN-COMPOSE-PROGRAM-GUIDANCE`; `B-RA-VR-PRESENT-PROGRAM-GUIDANCE` | Geeignet fuer technische Programmanleitung. |
| `B-RB-VIVIAN-REQUEST-CONFIRMED` | `B-RA-VIVIAN-CONFIRM-BREWING-REQUEST`; `B-RA-TRACE-SYNC-REQUEST-FEEDBACK` | Geeignet fuer Rueckmeldung und Trace-Synchronisation. |
| `B-RB-VIVIAN-CONFIRMATION-PROMPT` | `B-RA-VIVIAN-COMPOSE-CONFIRMATION-PROMPT`; `B-RA-VR-SHOW-CONFIRMATION-AFFORDANCE` | Geeignet fuer technische Rueckfrage und sichtbare Bestaetigungsmoeglichkeit. |
| `B-RB-VIVIAN-COMPLETION-REPORT` | `B-RA-VIVIAN-COMPOSE-COMPLETION-REPORT`; `B-RA-VR-PRESENT-COMPLETION-REPORT` | Geeignet fuer Abschlussmeldung. |
| `B-RB-VIVIAN-CUP-CORRECTION` | `B-RA-VIVIAN-COMPOSE-CUP-CORRECTION`; `B-RA-VR-PRESENT-CUP-CORRECTION` | Geeignet fuer Korrekturanleitung. |
| `B-RB-VIVIAN-ERROR-EXPLANATION` | `B-RA-VIVIAN-COMPOSE-ERROR-EXPLANATION`; `B-RA-VR-PRESENT-ERROR-EXPLANATION`; `B-RA-TRACE-SYNC-ERROR-OUTCOME` | Geeignet fuer Fehlererklaerung und Trace. |
| `B-RB-VIVIAN-EXCEPTION-CLOSE` | `B-RA-VIVIAN-CLOSE-EXCEPTION-FEEDBACK`; `B-RA-TRACE-SYNC-EXCEPTION-CLOSED` | Geeignet fuer technischen Exception-Abschluss. |

Die RuntimeAction-Ebene ist der richtige Ort fuer Endpoints, Topics, InputSchemas und OutputSchemas. Das schuetzt `ScenarioStep` und `Capability` vor technischer Vermischung.

## Beispieltrace

### Vivian leitet Tassenplatzierung an

| Ebene | Instanz |
| --- | --- |
| ScenarioStep | `B-MAIN-S03` |
| CapabilityUse | `B-CU-002` |
| Capability | `CAP-B-VIVIAN-GUIDE-CUP` |
| Effect | `B-EFF-CUP-GUIDANCE-ISSUED` |
| StateAssertion | `SA-B-VIVIAN-GUIDANCE-CUP` |
| RuntimeBinding | `B-RB-VIVIAN-CUP-GUIDANCE` |
| RuntimeAction | `B-RA-VIVIAN-COMPOSE-CUP-GUIDANCE`; `B-RA-VR-PRESENT-CUP-GUIDANCE` |
| ValidationCase | `B-VC-002-MAIN-GUIDANCE-START` |

Bewertung: Vollstaendig abbildbar. Was fachlich passiert, steht in Capability und Effect. Wie es technisch erzeugt und praesentiert wird, steht in RuntimeActions. Was nicht formal abgebildet ist: der genaue Dialogakt, Textinhalt, Stil oder didaktische Erklaerstrategie.

### Vivian fordert Startbestaetigung an

| Ebene | Instanz |
| --- | --- |
| ScenarioStep | `B-MAIN-S13` |
| CapabilityUse | `B-CU-006` |
| Capability | `CAP-B-VIVIAN-REQUEST-CONFIRMATION` |
| Effect | `B-EFF-CONFIRMATION-REQUESTED` |
| StateAssertion | `SA-B-VIVIAN-AWAITING-CONFIRMATION` |
| RuntimeBinding | `B-RB-VIVIAN-CONFIRMATION-PROMPT` |
| RuntimeAction | `B-RA-VIVIAN-COMPOSE-CONFIRMATION-PROMPT`; `B-RA-VR-SHOW-CONFIRMATION-AFFORDANCE` |
| ValidationCase | `B-VC-005-CONFIRMATION-AND-START` |

Bewertung: Fuer die Baseline ausreichend. Nicht formal modelliert sind Ablehnung, Timeout, Widerruf, Wiederholung und Autorisierungsdauer. Diese gehoeren bei erweitertem Scope in ein optionales Authorization-/AssistantInteraction-Modul.

## Wann ein `AssistantInteractionModule` noetig wird

| Bedingung | Modul noetig? | Begruendung |
| --- | --- | --- |
| Es soll nur nachvollziehbar sein, dass Vivian anleitet, bestaetigt oder erklaert. | nein | `Capability`, `Effect`, `StateAssertion`, `RuntimeBinding` und `RuntimeAction` reichen. |
| Es soll nur technisch ausgefuehrt werden, welcher Vivian-Endpunkt Inhalte erzeugt. | nein | `RuntimeAction` mit Schema reicht fuer die technische Bindung. |
| Dialogakte sollen fachlich unterscheidbar sein, z. B. `instruction`, `confirmationRequest`, `errorExplanation`. | ja | Der Kern besitzt keine `DialogueAct`-Klasse. |
| GuidanceContent soll versioniert, lokalisiert oder didaktisch bewertet werden. | ja | Das ist Inhalts- und Erklaersemantik, keine reine Capability. |
| Modalitaeten wie Sprache, Text, Avatar, Geste oder Highlight sollen fachlich geplant werden. | ja | RuntimeSchemas koennen sie transportieren, aber nicht als fachliche Semantik pruefen. |
| Antwortoptionen, Timeout, Ablehnung, Wiederholung oder Abbruch sollen formal gelten. | ja | Das ist Dialog-/Authorization-/Recovery-Policy. |
| Ein LLM soll aus dem Modell konkrete Vivian-Utterances kontrolliert generieren. | ja | Dafuer braucht es strukturierten GuidanceContent, Zielgruppe, Ton, Constraint und Validierung. |

## Vorgeschlagener Andockpunkt fuer ein optionales Modul

Falls das Dialogverhalten maschinenlesbar werden soll, sollte ein optionales `AssistantInteractionModule` an die vorhandenen Kernklassen andocken.

| Modulkonzept | Andockpunkt | Zweck |
| --- | --- | --- |
| `AssistantInteraction` | `Agent` oder `Capability` | Gruppiert assistierende Interaktion einer Agent-Entity. |
| `DialogueAct` | `Capability` oder `ScenarioStep` | Typisiert fachliche Dialogakte wie Hinweis, Rueckfrage, Bestaetigung, Fehlererklaerung. |
| `GuidanceContent` | `DialogueAct` oder `RuntimeBinding` | Beschreibt Inhalt, Zielgruppe, Thema, Sprache, Ton und Erklaerstrategie. |
| `PresentationMode` | `GuidanceContent` oder `RuntimeBinding` | Modelliert Sprache, Text, Avatar, Highlight, Geste oder Kombinationen. |
| `ResponseOption` | `DialogueAct` | Beschreibt erlaubte Benutzerantworten wie bestaetigen, ablehnen, spaeter, abbrechen. |
| `InteractionPolicy` | `AssistantInteraction` | Beschreibt Wiederholung, Timeout, Eskalation, Recovery und Personalisierung. |

Das Modul darf die Kernkette nicht ersetzen. Es verfeinert nur das Dialogverhalten zwischen `Capability` und `RuntimeBinding` beziehungsweise neben dem ScenarioStep.

## Kern- und Modulentscheidung

| Modellierungsbedarf | Entscheidung |
| --- | --- |
| Vivian als fachlich handelnde Assistenzinstanz | `Agent`/`Entity` im Kern |
| Vivians fachliche Faehigkeiten | `Capability` im Kern |
| Nutzung einer Vivian-Faehigkeit im Schritt | `CapabilityUse` im Kern |
| Beobachtbare Vivian-Wirkung | `Effect` und `StateAssertion` im Kern |
| Technische Bindung an Vivian-/VR-/Trace-Runtime | `RuntimeBinding` im Kern |
| Technische Ausgabe, Endpoint, Topic und Schema | `RuntimeAction` im Kern |
| Dialogakt, GuidanceContent, Modalitaet, Personalisierung | optionales `AssistantInteractionModule` |
| Antwortpolitik, Timeout, Ablehnung, Widerruf | optionales Authorization-/Recovery-Modul oder Teil des AssistantInteractionModule |
| Reihenfolge/Transaktion mehrerer RuntimeActions | optionales `RuntimeExecutionModule` |

## Invariantencheck

| Regel | Ergebnis |
| --- | --- |
| Keine direkte `ScenarioStep -> RuntimeAction`-Kante | eingehalten |
| `CapabilityUse -> Capability [1]` | eingehalten: `B-CU-001` bis `B-CU-011` referenzieren je genau eine Capability |
| `Capability` ohne technische Daten | eingehalten: Endpoints, Topics und Schemas liegen nicht in Capabilities |
| `RuntimeBinding.capability [1]` | eingehalten: jede B-RuntimeBinding referenziert genau eine Capability |
| `RuntimeBinding -> RuntimeAction [1..*]` | eingehalten: alle B-RuntimeBindings besitzen zwei oder drei RuntimeActions |
| Vivian nicht als Actor in der Baseline | eingehalten: Vivian bleibt `Agent`/`Entity`, Visitor bleibt `Actor` |

## Abnahmekontrolle

| Kriterium aus Task 10.5 | Erfuellung |
| --- | --- |
| Entscheidung vorhanden | `Capability`/`RuntimeBinding` reichen fuer Vivians Baseline-Aktionen, aber nicht fuer vollstaendige Dialogsemantik. |
| Fachliche Faehigkeit getrennt | Abschnitt `Fachliche Faehigkeit` beschreibt Vivian-Capabilities ohne technische Daten. |
| Dialogverhalten getrennt | Abschnitt `Dialogverhalten` grenzt GuidanceContent, Dialogakte, Modalitaet und Antwortpolitik als optionales Modul ab. |
| Technische Aktion getrennt | Abschnitt `Technische Aktion` ordnet Endpoints, Topics und Schemas der RuntimeAction-Ebene zu. |
| Konkrete B-Instanzen verwendet | Beispiele verwenden `B-CU-*`, `CAP-B-*`, `B-RB-*`, `B-RA-*` und ValidationCases. |
| Kein Kernumbau abgeleitet | Dialogdetails werden als optionales Modul vorgeschlagen, nicht als Kernklasse. |

## Konsequenz fuer Task 10.6

Task 10.6 soll als naechstes pruefen, ob raeumliche Beziehungen explizit benoetigt werden. Fuer Vivian ist das nur indirekt relevant: Hinweise koennen auf Objekte, Bedienbereiche oder sichtbare Stellen zeigen, aber die eigentliche raeumliche Semantik sollte nicht in `Capability`, `RuntimeBinding` oder ein Dialogmodul hineingezogen werden.
