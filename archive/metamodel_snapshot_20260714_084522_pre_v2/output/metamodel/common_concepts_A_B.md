# Gemeinsame Analyse A/B: Gemeinsame Konzepte

Stand: 2026-07-07

Task: 10.1 `Gemeinsamkeiten von A und B extrahieren`

Verglichene Use Cases:

- `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`
- `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Bezugsdateien:

- `use_case_A_direct_modelability.md`
- `use_case_A_non_modelable_gaps.md`
- `use_case_A_gap_decision_matrix.md`
- `use_case_B_direct_modelability.md`
- `use_case_B_non_modelable_gaps.md`
- `use_case_B_gap_decision_matrix.md`

## Abgrenzung

Diese Datei sammelt nur Konzepte, die in beiden Beispielen relevant sind. Ein Konzept wird deshalb nur aufgenommen, wenn es sowohl in A als auch in B entweder als konkrete Instanz, als direkt genutzter Metamodellanker oder als gleicher, gemeinsamer Modellierungsbedarf auftritt.

Reine A-Spezifika wie raeumliche Navigation des Agenten und reine B-Spezifika wie Vivian-Dialog, Kaffeemaschinen-Affordances oder Readiness-Regeln werden hier nicht als Gemeinsamkeit gewertet. Sie werden in Task 10.2 getrennt betrachtet.

## Ergebnis

Die beiden Beispiele bestaetigen einen gemeinsamen kompakten Kern: Requirements und Use Cases werden ueber Szenarien, Schritte, Ereignisse, Bedingungen, Zustandsaussagen, fachliche Faehigkeiten, technische Bindungen und Validierungsfaelle nachvollziehbar miteinander verbunden.

Der gemeinsame Nenner ist nicht "VR-Agent" oder "Kaffeemaschine", sondern die fachlich-technische Trace-Kette:

`Requirement -> UseCase -> Scenario -> ScenarioStep -> CapabilityUse -> Capability -> Effect -> RuntimeBinding -> RuntimeAction -> ValidationCase`

Entscheidend ist dabei, dass `ScenarioStep` nicht direkt auf `RuntimeAction` zeigt. Der Schritt bleibt fachlich; die technische Ausfuehrung wird erst ueber `Capability`, `Effect` und `RuntimeBinding` erreicht.

## Gemeinsame Konzepte

| Gemeinsames Konzept | A-Auspraegung | B-Auspraegung | Metamodellanker | Warum wirklich gemeinsam? |
| --- | --- | --- | --- | --- |
| Requirements-Kontext | Anforderungen an dynamisches Agentenmodellieren | Anforderungen an assistierte Kaffeemaschinenbedienung | `RequirementsModel`, `Requirement` | Beide Beispiele starten mit Anforderungen, die fachliche Eigenschaften des Use Case absichern. |
| Fachlicher Use Case | `UC-A-01` dynamisches Agentenverhalten | `UC-B-01` assistierte Kaffeemaschinenbedienung | `UseCase` | Beide Beispiele modellieren einen fachlichen Anwendungsfall als oberste Verhaltensklammer. |
| Externe Rolle | `ScenarioDesigner`, `SceneParticipant`, `SceneObserver` | `Visitor` | `Actor`, `Actor -- UseCase : interactsWith` | In beiden Faellen gibt es mindestens eine externe Rolle, die mit dem Use Case interagiert. |
| Genau ein Hauptszenario pro Use Case | `A-MAIN-SC01` | `SC-B-01-MAIN` | `Scenario.kind = main`; Invariante genau ein Main Scenario | Beide Beispiele besitzen genau einen normalen Erfolgsablauf. |
| Optionale Alternativ- und Exception-Szenarien | temporaere Blockade und dauerhafte Blockade | fehlende Tasse und fehlgeschlagene Bereitschaftspruefung | `Scenario.kind = alternative|exception`; `StepRelation.kind` | Beide Beispiele brauchen Abweichungen vom Hauptpfad, aber ohne den Kern um ein Workflow-Modell zu erweitern. |
| Geordnete Schritte | `A-MAIN-S01` bis `A-MAIN-S09` | `B-MAIN-S01` bis `B-MAIN-S20` | `ScenarioStep.stepNumber`, `Scenario -> ScenarioStep [1..*]` | Beide Beispiele beschreiben Verhalten als nachvollziehbare, nummerierte Schrittfolge. |
| Schrittbeziehungen | Hauptpfadsequenz, Alternative, Exception | Hauptpfadsequenz, Alternative, Exception | `StepRelation.source [1]`, `target [1]`, `kind` | Beide Beispiele nutzen explizite Kanten zwischen Schritten statt impliziter Textreihenfolge. |
| Ausloesende Ereignisse | Raeumlicher Eintritt, Blockadeaenderung, Signale | Benutzerereignisse, Vivian-Signale, Maschinenereignisse | `Event.kind`, `Event.expression`, `ScenarioStep.triggeredBy [0..*]` | In beiden Beispielen werden Schritte durch beobachtbare Ereignisse oder Signale angestossen. |
| Bedingungen und Guards | Preconditions, Spatial Guards, Blockadebedingungen | Preconditions, Cup/Program/Readiness Guards | `Condition.kind`, `Condition.expression`, `Scenario.precondition`, `ScenarioStep.guard`, `StepRelation.guard` | Beide Beispiele benoetigen pruefbare Voraussetzungen und Abzweigbedingungen. |
| Erwartete Zustandsaussagen | Agentenrolle, Zielbereich, Blockadezustand, Feedback | Vivian-Zustand, Kaffeemaschinenzustand, Tasse, BrewingRequest | `StateAssertion.subjectRef`, `StateAssertion.expectedState` | Beide Beispiele pruefen Verhalten ueber erwartete Zustaende identifizierbarer Subjekte. |
| Identifizierbare modellierte Subjekte | `AgentBody`, `TriggerZone`, `TargetZone`, `ObstacleRegion` | `VivianAssistant`, `CoffeeMachine`, `Cup`, `BrewingRequest` | `Identifiable`, `Entity`, `Agent` | In beiden Faellen muessen Modellobjekte referenzierbar sein, damit Events, Conditions und StateAssertions auf sie zeigen koennen. |
| Agent als spezialisierte Entity | dynamischer Szenenagent | VivianAssistant | `Agent --|> Entity` | Beide Beispiele enthalten ein aktives, modelliertes Systemsubjekt mit Faehigkeiten. |
| Fachliche Faehigkeitsnutzung im Schritt | Rollenwechsel, Zielhandlung, Blockadesicherung | Vivian-Fuehrung, Maschinenpruefung, Bruehstart | `ScenarioStep -> CapabilityUse [0..*]`; `CapabilityUse -> Capability [1]` | In beiden Beispielen ruft ein fachlicher Schritt eine fachliche Faehigkeit auf. |
| Wiederverwendbare Capability | Agentenfaehigkeiten | Vivian- und Maschinenfaehigkeiten | `Entity -> Capability [0..*]`; `Capability.precondition`; `Capability.promisedEffect [1..*]` | Beide Beispiele trennen den konkreten Schritt von der allgemeineren Faehigkeit einer Entity. |
| Beobachtbare Wirkung | Rollenstatus, Bewegung, Zielbelegung, Blockade | Guidance sichtbar, Readiness-Ergebnis, Bruehstart, Abschluss | `Effect` | Beide Beispiele brauchen eine fachliche Wirkung, die nicht mit technischer Ausfuehrung verwechselt werden darf. |
| Technische Bindung der Capability | VR-Runtime-Bindings des Agenten | Vivian-, VR-, Kaffeemaschinen- und Trace-Bindings | `Capability -> RuntimeBinding [0..*]`; `RuntimeBinding.capability [1]` | Beide Beispiele benoetigen eine technische Anbindung, ohne die fachliche Capability technisch zu verschmutzen. |
| Technische Einzelaktion | Rollen setzen, Zielaktion anfordern, Blockadezustand synchronisieren | Vivian-Ausgabe, VR-Hinweis, CoffeeMachineAdapter, Trace-Aktion | `RuntimeBinding -> RuntimeAction [1..*]` | Beide Beispiele zerlegen technische Ausfuehrung in konkrete RuntimeActions unterhalb der Binding-Ebene. |
| Validierungsfall | Main Preconditions, Rollenbinding, Zielhandlung, Alternative, Exception | UseCase-Struktur, Guidance, Readiness, Bruehstart, Alternative, Exception | `ValidationCase` | Beide Beispiele muessen modellierte Anforderungen und Runtime-Bindungen pruefbar machen. |
| Keine kuenstliche Parallelitaet | keine `ParallelGroup`-Instanz fuer A | keine `ParallelGroup`-Instanz fuer B | `Scenario -> ParallelGroup [0..*]` erlaubt 0 | Beide Beispiele sind sequenziell modellierbar; Parallelitaet ist moeglich, aber nicht erzwungen. |
| Keine direkte technische Kurzschaltung | explizit in A validiert | explizit in B validiert | Invariante: keine direkte `ScenarioStep -> RuntimeAction`-Kante | Beide Beispiele bestaetigen die fachlich-technische Trennung als Kernregel. |

## Gemeinsame Trace-Kette

| Ebene | A-Beispiel | B-Beispiel | Gemeinsames Muster |
| --- | --- | --- | --- |
| Requirement | `A-REQ-006` | `B-REQ-011` | Eine Anforderung begruendet den fachlichen Nachweisbedarf. |
| UseCase | `UC-A-01` | `UC-B-01` | Der Use Case ist die fachliche Klammer. |
| Scenario | `A-MAIN-SC01` | `SC-B-01-MAIN` | Der Hauptablauf liefert den normalen Kontext. |
| ScenarioStep | `A-MAIN-S05` | `B-MAIN-S15` | Ein konkreter Schritt loest fachliches Verhalten aus. |
| CapabilityUse | `A-CU-001` | `B-CU-007` | Der Schritt nutzt eine fachliche Faehigkeit. |
| Capability | `A-CAP-ADOPT-EXECUTOR-ROLE` | `CAP-B-START-BREWING` | Die Faehigkeit beschreibt, was fachlich geleistet wird. |
| Effect | `A-EFF-ROLE-EXECUTOR` | `B-EFF-BREWING-START-ISSUED` | Die Wirkung beschreibt den erwarteten beobachtbaren Effekt. |
| RuntimeBinding | `A-RB-ROLE-EXECUTOR-VR` | `B-RB-COFFEE-START-BREWING` | Die Bindung ordnet die fachliche Faehigkeit einer Runtime-Anbindung zu. |
| RuntimeAction | `A-RA-ROLE-SET` | `B-RA-CM-REQUEST-BREWING-START` | Die technische Aktion ist unterhalb der RuntimeBinding verortet. |
| ValidationCase | `A-VC-002-ROLE-BINDING` | `B-VC-005-CONFIRMATION-AND-START` | Der Nachweis prueft die fachliche und technische Kette. |

Die gemeinsame Kette ist fuer beide Beispiele vollstaendig direkt modellierbar. Unterschiede liegen in der fachlichen Domaene der Entities und Capabilities, nicht in der Grundstruktur der Kette.

## Gemeinsame minimale Kernkandidaten

Die beiden Beispiele bestaetigen zwei kleine Kernpraezisierungen, die fuer A und B gleichermassen nuetzlich sind. Diese Datei entscheidet noch nicht ueber die Umsetzung; sie markiert nur die gemeinsame Basis fuer die spaeteren Tasks.

| Kandidat | A-Befund | B-Befund | Gemeinsame Bewertung fuer spaetere Tasks |
| --- | --- | --- | --- |
| Optionale `Entity.kind`-Typisierung | A braucht unterscheidbare Entity-Arten wie AgentBody, Zone, Boundary, Signal und StateFlag. | B nutzt Vivian, CoffeeMachine, Cup und BrewingRequest als verschiedenartige Entities. | Gemeinsamer kompakter Kernkandidat, wenn optional und mit groben Oberkategorien gehalten. |
| Optionale Trace-Kante `Effect -> StateAssertion` | A dokumentiert Effects auf erwartete Agenten- und Szenenzustaende. | B dokumentiert Effects auf Vivian-, Maschinen-, Tassen- und Request-Zustaende. | Gemeinsamer kompakter Trace-Kandidat, wenn nicht-kompositiv und optional. |

## Gemeinsame Ergaenzungsbedarfe

Mehrere Bedarfe treten in beiden Beispielen auf, sind aber zu gross oder zu spezialisiert fuer den Kern. Sie sind deshalb gemeinsame Kandidaten fuer optionale Ergaenzungsmodelle.

| Gemeinsamer Bedarf | A-Befund | B-Befund | Vorlaeufige Einordnung |
| --- | --- | --- | --- |
| State/Transition-Semantik | Rollen- und Aktivitaetswechsel des Agenten koennten formalisiert werden. | Kaffeemaschine und BrewingRequest koennten formale Zustaende und Transitionen erhalten. | Gemeinsames optionales `StateTransitionModule`. |
| Event-Details | Quelle, Ziel, Payload und Kanal von Raum- und Signalereignissen sind aktuell Expressions. | Quelle, Ziel, Payload und Korrelation von Benutzer-, Vivian- und Maschinenereignissen sind aktuell Expressions. | Gemeinsames optionales `EventDetailModule`. |
| Runtime-Orchestrierung | Reihenfolge und Abhaengigkeit mehrerer RuntimeActions bleiben dokumentarisch. | Reihenfolge, Retry, Timeout und Adapterdetails mehrerer RuntimeActions bleiben dokumentarisch. | Gemeinsames optionales `RuntimeExecutionModule`. |
| Formale Validation-/Assertion-Semantik | Zusammengesetzte erwartete Ergebnisse bleiben halbformal. | Komplexe Outcomes und Trace-Nachweise bleiben halbformal. | Gemeinsames optionales `ValidationAssertionModule`. |

## Nicht als Gemeinsamkeit in 10.1 aufgenommen

| Nicht aufgenommenes Konzept | Grund |
| --- | --- |
| Strukturierte Raumsemantik fuer `inside`, `near`, `reachable`, `movingTo` | Zentral fuer A, aber fuer B nicht gleich stark und nicht als gleicher Kernbedarf belegt. |
| Vivian-Dialog, GuidanceContent und Erklaerstrategie | Zentral fuer B, aber in A nicht als eigenes fachliches Konzept vorhanden. |
| Kaffeemaschinen-Affordances wie Taste, Display, Tassenbereich und Programmauswahl | Zentral fuer B, fuer A nur vorbereitend und nicht als konkretes Beispielkonzept instanziiert. |
| Readiness-Regeln der Kaffeemaschine | B-spezifische Entscheidungslogik, kein A-Gegenstueck. |
| Mehrere externe Rollen mit Szenendesigner und Beobachter | A-spezifisch ausgepraegt; B hat nur die Besucherrolle als externe Rolle. |
| Safety-/Hazard-Argumentation | In B als spaeterer Safety-Scope denkbar, in A nicht als gemeinsames Beispielkonzept belegt. |
| Formale `Satisfy`-Instanzen in beiden Beispielen | A instanziiert `Satisfy` formal, B bewertet es als direkt modellierbar, aber noch nicht formal instanziiert. Gemeinsam ist daher nur die Metamodellfaehigkeit, nicht die Instanzauspraegung. |

## Abnahmekontrolle

| Kriterium aus Task 10.1 | Erfuellung |
| --- | --- |
| Liste gemeinsamer Konzepte vorhanden | Die Tabelle `Gemeinsame Konzepte` extrahiert die gemeinsame Schnittmenge aus A und B. |
| Nur in beiden Beispielen relevante Konzepte aufgenommen | Jede Tabellenzeile nennt eine A-Auspraegung und eine B-Auspraegung. |
| Gemeinsame Trace-Struktur sichtbar | Die Tabelle `Gemeinsame Trace-Kette` zeigt denselben Pfad fuer A und B. |
| A- oder B-Spezifika abgegrenzt | Der Abschnitt `Nicht als Gemeinsamkeit in 10.1 aufgenommen` grenzt einseitige Konzepte aus. |
| Vorbereitung fuer 10.2 vorhanden | Unterschiede werden bewusst nicht entschieden, sondern fuer Task 10.2 vorgemerkt. |

## Konsequenz fuer Task 10.2

Task 10.2 soll nun die Unterschiede systematisch extrahieren. Erwartete Trennlinie ist:

- A betont Agentendynamik, Raumbezug, Szenengrenzen, Hindernisse und Beobachtbarkeit.
- B betont Interaktionsobjekte, Bedienhandlungen, Vivian-Assistenz, Objektzustaende, Readiness und Benutzerbestaetigung.

Diese Unterschiede duerfen nicht vorschnell in den Kern gezogen werden. Sie muessen danach einzeln daraufhin bewertet werden, ob sie mit `Entity`, `Agent`, `StateAssertion`, `Capability` und `RuntimeBinding` genuegend abbildbar sind oder ein optionales Ergaenzungsmodell benoetigen.
