# Entscheidung 10.4: Reicht `StateAssertion` fuer Objektzustaende aus?

Stand: 2026-07-07

Task: 10.4 `Pruefen, ob StateAssertion fuer Objektzustaende ausreicht`

Verglichene Use Cases:

- `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`
- `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Bezugsdateien:

- `dynamic_functional_mlds_specification.md`
- `metamodel_element_notes.md`
- `cardinality_table.md`
- `invariants.md`
- `entity_agent_scene_object_decision.md`
- `differences_A_B.md`
- `use_case_A_indirect_modelability.md`
- `use_case_B_indirect_modelability.md`
- `use_case_A_gap_decision_matrix.md`
- `use_case_B_gap_decision_matrix.md`

## Entscheidung

`StateAssertion` reicht fuer Objektzustaende im kompakten Kern aus, solange ein Zustand als erwartete oder beobachtete Aussage ueber ein identifizierbares Subjekt modelliert wird.

`StateAssertion` reicht nicht aus, wenn ein vollstaendiger Zustandsautomat mit formalen States, State-Dimensions, erlaubten Uebergaengen, Triggern, Guards, Effekten und Transition-Regeln maschinenlesbar modelliert werden soll.

Damit lautet die Entscheidung:

| Frage | Entscheidung |
| --- | --- |
| Reicht `StateAssertion` fuer statische Objektzustaende? | ja |
| Reicht `StateAssertion` fuer erwartete Ergebniszustaende von Schritten? | ja |
| Reicht `StateAssertion` fuer Validation-Expected-Outcomes? | ja |
| Reicht `StateAssertion` fuer formale Zustandsautomaten? | nein |
| Reicht `StateAssertion` fuer formal eigenstaendige Uebergaenge? | nein |
| Muss deshalb der Kern sofort erweitert werden? | nein |
| Empfohlene Behandlung fuer Automaten/Transitionen | optionales `StateTransitionModule` |

Die Kernlinie bleibt also kompakt: `StateAssertion` bleibt eine Zustandsaussage, kein StateMachine-Modell.

## Begriffliche Abgrenzung

| Begriff | Bedeutung im kompakten Kern | Nicht damit gemeint |
| --- | --- | --- |
| `StateAssertion` | Aussage, dass ein identifizierbares Subjekt einen erwarteten oder beobachteten Zustand besitzt. | Kein eigener State-Katalog und kein Zustandsautomat. |
| `Condition` | Vorbedingung, Guard, Timing-, Raum- oder logischer Ausdruck. | Kein formaler Transition-Quellzustand mit eigener Semantik. |
| `Event` | Ausloeser eines Schritts oder beobachtbares Signal. | Kein vollstaendiges Event-Payload-/Korrelationmodell. |
| `ScenarioStep` | Fachlicher Schritt, der Ereignisse, Guards, Faehigkeitsnutzungen und resultierende Zustaende zusammenfuehrt. | Keine technische Aktion und keine StateMachine-Transition. |
| `Effect` | Versprochene beobachtbare Wirkung einer Capability. | Kein Ersatz fuer `StateAssertion`, sondern fachliche Wirkung, die durch StateAssertions belegt werden kann. |

## Statische Zustaende

Fuer statische, beobachtete oder erwartete Objektzustaende ist `StateAssertion` geeignet.

| Zustandsart | A-Beispiel | B-Beispiel | Bewertung |
| --- | --- | --- | --- |
| Rollen- oder Moduszustand | `AgentBody.roleState = executor` | `VivianAssistant.mode = guiding` | direkt als `StateAssertion.expectedState` modellierbar |
| Aktivitaetszustand | `AgentBody.activityState = moving` | `CoffeeMachine.lifecycleState = brewing` | direkt modellierbar, solange keine erlaubten Transitionen ausgewertet werden |
| Objektmerkmal | `TargetZone.state = occupied` | `CoffeeMachine.cupPresent = true` | direkt modellierbar |
| Sicherheits- oder Freigabezustand | `AgentBody.roleState = blocked` | `CoffeeMachine.safeState = true`; `startPermission = blocked` | direkt modellierbar |
| Feedback- oder Sichtbarkeitszustand | `FeedbackSignal.visible = true` | `CoffeeMachine.progressIndicator.visible = true` | direkt modellierbar |
| Request- oder Prozessstatus | nicht zentral in A | `BrewingRequest.state = confirmed` | direkt modellierbar |

Die Staerke von `StateAssertion` ist hier genau richtig: Ein Zustand ist an ein eindeutig identifizierbares Subjekt gebunden. Das Subjekt kann `AgentBody`, `CoffeeMachine`, `Cup`, `BrewingRequest`, `TargetZone`, `FeedbackSignal` oder eine andere `Entity` sein.

## Zusammengesetzte und orthogonale Zustaende

Mehrere parallele Objektmerkmale sollten im Kern nicht als ein monolithischer Zustand erzwungen werden. Besser ist eine disziplinierte Zerlegung in mehrere StateAssertions oder klar strukturierte Ausdruecke.

| Objekt | Zusammengesetzter Zustand | Empfohlene Kernabbildung |
| --- | --- | --- |
| `AgentBody` | Rolle, Aktivitaet, Position, Blockade | mehrere StateAssertions, z. B. `roleState = executor`, `activityState = moving`, `positionRelation = at(TargetZone)` |
| `CoffeeMachine` | Lifecycle, Wasserstand, Tasse, Programm, Startfreigabe, Feedback | mehrere StateAssertions, z. B. `lifecycleState = ready`, `waterLevel = sufficient`, `cupPresent = true`, `selectedProgram = coffee` |
| `VivianAssistant` | Modus, Feedback, erwartete Antwort, GuidanceTopic | mehrere StateAssertions, z. B. `mode = awaitingConfirmation`, `guidanceTopic = confirmStart` |
| `BrewingRequest` | angefordert, bestaetigt, gestartet, abgeschlossen | mehrere StateAssertions oder ein einzelner Request-State, solange keine formale Transition gefordert ist |

Diese Zerlegung ist wichtig, weil B sonst einen kuenstlichen Mega-Zustand wie `machineReadyAndCupPlacedAndCoffeeSelectedAndConfirmed` erzeugen wuerde. Das waere schwer zu pruefen und schlecht wiederverwendbar.

## Zustandsautomaten

Fuer Zustandsautomaten reicht `StateAssertion` allein nicht aus.

Ein Zustandsautomat braucht mindestens:

- identifizierte State-Elemente,
- State-Dimensions oder Regionen,
- Source-State und Target-State,
- Trigger-Event,
- Guard oder Constraint,
- Transition-Effect,
- erlaubte und verbotene Uebergaenge,
- optional Prioritaet, History, Parallelitaet, Timeout oder Recovery-Regeln.

Diese Semantik ist im kompakten Kern bewusst nicht vorhanden. Sie laesst sich fuer die aktuellen Beispiele durch `Condition`, `Event`, `ScenarioStep`, `StateAssertion`, `Capability` und `ValidationCase` nachvollziehbar verteilen, aber nicht als eigenstaendiger Automat pruefen.

| Automatbedarf | A-Befund | B-Befund | Entscheidung |
| --- | --- | --- | --- |
| Agentenrollen und Aktivitaeten | `notBlocked`, `executor`, `moving`, `waiting`, `blocked`, `completed` | Vivian-Modi wie `guiding`, `awaitingConfirmation`, `errorExplained` | fuer Baseline mit StateAssertions ausreichend; formal als optionales Modul |
| Objekt-Lifecycle | A hat eher Szenen- und Agentenzustaende | `idle`, `ready`, `notReady`, `brewing`, `finished` | B bestaetigt Bedarf, aber als optionales `StateTransitionModule` |
| Request-Lifecycle | in A nicht zentral | `requested`, `confirmed`, `startIssued`, `completed` | optionales Modul bei automatischer Pruefung |
| Recovery/Timeout | A: Blockadepfade | B: fehlende Tasse, fehlende Bereitschaft, moeglicher Abbruch/Timeout | aktuell ueber Scenarios abbildbar; Policy-Modell nur bei erweitertem Scope |

Damit bestaetigt 10.4 die bisherige Linie: State/Transition-Semantik ist ein gemeinsamer optionaler Modulbedarf, kein Kernumbau.

## Uebergaenge

Ein Uebergang kann im aktuellen Kern nachvollziehbar dargestellt werden, aber nicht als eigenstaendiges Transition-Objekt.

Das heutige Muster lautet:

`Vorzustand als Condition -> Event/Guard -> ScenarioStep -> CapabilityUse/Capability -> Effect -> resultierende StateAssertion`

### Beispiel A: Agent wird ausfuehrender Szenenagent

| Transition-Aspekt | Kernabbildung |
| --- | --- |
| Subjekt | `AgentBody` als `Agent`/`Entity` |
| Vorzustand | `Condition.expression = AgentBody.roleState = notBlocked` |
| Ausloeser | Schritt oder Event im Hauptpfad, z. B. Eintritt/Instruktion im Szenario |
| Fachlicher Schritt | `A-MAIN-S05` |
| Faehigkeit | `A-CU-001 -> A-CAP-ADOPT-EXECUTOR-ROLE` |
| Wirkung | `A-EFF-ROLE-EXECUTOR` |
| Zielzustand | `StateAssertion.expectedState = AgentBody.roleState = executor` |
| Technische Bindung | `A-RB-ROLE-EXECUTOR-VR -> A-RA-ROLE-SET` |
| Bewertung | nachvollziehbar modellierbar; kein formales Transition-Objekt |

### Beispiel B: Kaffeemaschine startet Bruehvorgang

| Transition-Aspekt | Kernabbildung |
| --- | --- |
| Subjekt | `CoffeeMachine` als `Entity` |
| Vorzustand | `Condition.expression = CoffeeMachine.lifecycleState = ready` und `ReadinessCheck.result = passed` |
| Ausloeser | Benutzerbestaetigung und Systemschritt im Hauptpfad |
| Fachlicher Schritt | `B-MAIN-S15` |
| Faehigkeit | `B-CU-007 -> CAP-B-START-BREWING` |
| Wirkung | `B-EFF-BREWING-START-ISSUED` |
| Zielzustand | `StateAssertion.expectedState = CoffeeMachine.lifecycleState = brewing` |
| Technische Bindung | `B-RB-COFFEE-START-BREWING -> B-RA-CM-REQUEST-BREWING-START` |
| Bewertung | nachvollziehbar modellierbar; formale Erlaubnis `ready -> brewing` bleibt optionales StateTransition-Thema |

Diese Darstellung reicht fuer Traceability, Requirements-Nachweis und Baseline-Validierung. Sie reicht nicht, wenn ein Werkzeug automatisch alle erlaubten und verbotenen Uebergaenge einer Kaffeemaschine oder eines Agenten pruefen soll.

## Wann ein optionales `StateTransitionModule` noetig wird

| Bedingung | Modul noetig? | Begruendung |
| --- | --- | --- |
| Es sollen nur erwartete Zustandsfolgen im Szenario dokumentiert werden. | nein | `StateAssertion` plus `Condition` reicht. |
| Ein ValidationCase prueft konkrete erwartete Endzustaende. | nein | `ValidationCase.expectedOutcome` kann StateAssertions enthalten. |
| Ein Generator soll aus Zustandswerten eine einfache Szene erzeugen. | eher nein | Solange keine erlaubten Transitionen berechnet werden, reichen StateAssertions. |
| Ein Pruefer soll erkennen, ob `ready -> brewing` erlaubt und `notReady -> brewing` verboten ist. | ja | Dafuer braucht es formale Transitionsregeln. |
| Mehrere orthogonale State-Dimensions sollen unabhaengig analysiert werden. | ja | Dafuer braucht es `StateDimension` oder gleichwertige Struktur. |
| Timeout, Recovery, History oder parallele Regionen sollen formal gelten. | ja | Das ist StateMachine-/Policy-Semantik. |
| Safety-Argumentation soll verbotene Zustaende und Mitigations beweisen. | ja, aber als optionales State/Safety-Modul | `StateAssertion` allein ist kein SafetyCase. |

## Vorgeschlagener Andockpunkt fuer ein Modul

Falls ein `StateTransitionModule` spaeter modelliert wird, sollte es an vorhandene Kernklassen andocken, ohne sie zu ersetzen.

| Modulkonzept | Andockpunkt | Zweck |
| --- | --- | --- |
| `StateModel` | `Entity` oder `Agent` | Fasst Zustandsdimensionen eines Subjekts zusammen. |
| `StateDimension` | `StateModel` | Trennt z. B. Lifecycle, Position, Rolle, Feedback und Freigabe. |
| `State` | `StateDimension` | Benennt erlaubte Werte wie `ready`, `brewing`, `blocked`. |
| `StateTransition` | `State`, `Event`, `Condition`, `Effect`, `StateAssertion` | Bindet Source-State, Target-State, Trigger, Guard und erwarteten Effekt zusammen. |
| `TransitionPolicy` | `StateTransition` oder `Scenario` | Beschreibt Timeout, Recovery, Prioritaet oder Verbot. |

Wichtig: Ein solches Modul darf `StateAssertion` nicht ersetzen. `StateAssertion` bleibt der Ort, an dem ein Szenarioschritt oder ValidationCase einen konkreten erwarteten Zustand behauptet.

## Kern- und Modulentscheidung

| Modellierungsbedarf | Entscheidung |
| --- | --- |
| Statische Zustaende | im Kern mit `StateAssertion` |
| Erwartete Schrittresultate | im Kern mit `ScenarioStep -> StateAssertion [0..*]` |
| Validation-Expected-Outcomes | im Kern mit `ValidationCase.expectedOutcome [1..*]` |
| Zusammengesetzte Objektzustaende | im Kern durch mehrere StateAssertions oder klare Expressions |
| Effekt-zu-Zustandsnachweis | minimaler Kernkandidat: optionale Kante `Effect -> StateAssertion [0..*]` |
| Formale StateMachines | optionales `StateTransitionModule` |
| Erlaubte/verbotene Uebergaenge | optionales `StateTransitionModule` |
| Safety- oder Recovery-Policies | optionales Safety-/Recovery-Modul, ggf. an StateTransition angebunden |

## Abnahmekontrolle

| Kriterium aus Task 10.4 | Erfuellung |
| --- | --- |
| Entscheidung vorhanden | `StateAssertion` reicht fuer statische und erwartete Objektzustaende, aber nicht fuer formale Zustandsautomaten. |
| Statische Zustaende genannt | Abschnitt `Statische Zustaende` nennt Agent-, Vivian-, Kaffeemaschinen-, Tassen-, Request- und Feedbackzustaende. |
| Zustandsautomaten genannt | Abschnitt `Zustandsautomaten` erklaert, welche StateMachine-Semantik fehlt. |
| Uebergaenge genannt | Abschnitt `Uebergaenge` zeigt A- und B-Beispiele fuer verteilte Uebergangsmodellierung. |
| Kern versus Modul entschieden | StateAssertions bleiben Kern; StateTransition wird als optionales Modul eingeordnet. |
| A und B beruecksichtigt | Beispiele fuer AgentBody und CoffeeMachine/BrewingRequest sind enthalten. |

## Konsequenz fuer Task 10.5

Task 10.5 soll nun pruefen, ob `Capability` und `RuntimeBinding` fuer Vivian-Aktionen ausreichen. Die Entscheidung aus 10.4 ist dafuer relevant: Vivian-Zustaende koennen als `StateAssertion` beschrieben werden, aber Dialogverhalten, GuidanceContent und technische Ausgabe duerfen nicht in StateAssertions hineingezogen werden.
