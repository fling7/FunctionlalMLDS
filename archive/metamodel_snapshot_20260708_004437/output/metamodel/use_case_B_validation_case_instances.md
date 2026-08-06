# Anwendungsfall B: ValidationCase-Instanzen

Stand: 2026-07-07

Task: 8.12 `ValidationCases fuer B anlegen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Modellierungsregel

Ein `ValidationCase` beschreibt einen pruefbaren Fall mit Stimulus und mindestens einem erwarteten Outcome. Er kann Requirements verifizieren, einen Use Case validieren und RuntimeBindings ausfuehren oder pruefen. Er besitzt diese RuntimeBindings aber nicht.

Fuer Anwendungsfall B gilt:

- Jeder ValidationCase besitzt mindestens einen Stimulus.
- Jeder ValidationCase besitzt mindestens ein erwartetes Outcome.
- `ValidationCase -> RuntimeBinding [0..*]` ist eine pruefende Dependency, keine Komposition.
- RuntimeActions duerfen im Stimulus als technische Ausfuehrungsdetails genannt werden, bleiben aber unter ihrer RuntimeBinding eingeordnet.
- Structural ValidationCases duerfen ohne RuntimeBinding arbeiten, wenn sie Modellregeln pruefen.
- Kein ValidationCase erzeugt eine direkte `ScenarioStep -> RuntimeAction`-Kante.

Der erlaubte Trace bleibt:

`ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

## Angelegte ValidationCase-Instanzen

| ValidationCase-ID | Art | `verifies` | `validates` | `executes/checks` RuntimeBinding | Stimulus | ExpectedOutcome |
| --- | --- | --- | --- | --- | --- | --- |
| `B-VC-001-USECASE-STRUCTURE` | abstrakt, strukturell | `B-REQ-001`; `B-REQ-002`; `B-REQ-016`; `B-REQ-018` | `UC-B-01` | keine | Modellinspektion von `UC-B-01`, `ACT-B-01`, `ENT-B-01`, `ENT-B-02`, `SC-B-01-MAIN`, `SC-B-01-ALT01` und `SC-B-01-EX01`. | Genau ein `main` Scenario existiert; `Visitor` ist Actor; `VivianAssistant` ist Agent/Entity; `CoffeeMachine` ist Entity; Alternative und Exception sind nicht als Include/Extend missbraucht. |
| `B-VC-002-MAIN-GUIDANCE-START` | konkret, runtime-nah | `B-REQ-003`; `B-REQ-004`; `B-REQ-017` | `SC-B-01-MAIN` | `B-RB-VIVIAN-GUIDANCE-MODE`; `B-RB-VIVIAN-CUP-GUIDANCE` | Hilfewunsch des Visitors mit `B-E01` und `B-MAIN-G01`; Ausfuehren von `B-RA-VIVIAN-SET-GUIDANCE-MODE`, `B-RA-VR-SYNC-ASSISTANT-STATE`, `B-RA-VIVIAN-COMPOSE-CUP-GUIDANCE`, `B-RA-VR-PRESENT-CUP-GUIDANCE` in der dokumentierten Reihenfolge. | `SA-B-VIVIAN-GUIDING` und `SA-B-VIVIAN-GUIDANCE-CUP` treten ein; `B-MAIN-S02` und `B-MAIN-S03` bleiben ueber `CapabilityUse -> Capability -> RuntimeBinding` vermittelt. |
| `B-VC-003-CUP-AND-PROGRAM-GUIDANCE` | konkret, runtime-nah | `B-REQ-005`; `B-REQ-007`; `B-REQ-017` | `SC-B-01-MAIN` | `B-RB-VIVIAN-PROGRAM-GUIDANCE` | Tasse wird im Hauptpfad platziert und erkannt (`B-E03`, `B-E04`, `B-MAIN-G03`); danach wird die Programmauswahlanleitung mit `B-RA-VIVIAN-COMPOSE-PROGRAM-GUIDANCE` vor `B-RA-VR-PRESENT-PROGRAM-GUIDANCE` ausgefuehrt. | `SA-B-CUP-PLACED`, `SA-B-CM-CUP-PRESENT` und `SA-B-VIVIAN-GUIDANCE-PROGRAM` sind beobachtbar; der anschliessende Schritt `B-MAIN-S08` kann `SA-B-CM-PROGRAM-COFFEE` erreichen. |
| `B-VC-004-REQUEST-READINESS-PASSED` | konkret, runtime-nah | `B-REQ-008`; `B-REQ-009`; `B-REQ-017` | `SC-B-01-MAIN` | `B-RB-VIVIAN-REQUEST-CONFIRMED`; `B-RB-COFFEE-READINESS-CHECK` | Visitor drueckt die Starttaste (`B-E07`) nach gesetzter Programmauswahl; Ausfuehren von `B-RA-VIVIAN-CONFIRM-BREWING-REQUEST`, `B-RA-TRACE-SYNC-REQUEST-FEEDBACK`, `B-RA-CM-EVALUATE-READINESS`, `B-RA-CM-SYNC-READINESS-RESULT`, `B-RA-TRACE-SYNC-READINESS-OUTCOME` mit `ReadinessResult=passed`. | `SA-B-BREWING-REQUESTED`, `SA-B-VIVIAN-INTENT-CONFIRMED`, `SA-B-CM-READY`, `SA-B-CM-READY-FEEDBACK` und `SA-B-CM-START-PERMISSION` treten ein. |
| `B-VC-005-CONFIRMATION-AND-START` | konkret, runtime-nah | `B-REQ-010`; `B-REQ-011`; `B-REQ-012`; `B-REQ-017` | `SC-B-01-MAIN` | `B-RB-VIVIAN-CONFIRMATION-PROMPT`; `B-RB-COFFEE-START-BREWING` | Bei `B-MAIN-G08` wahr: Vivian fordert mit `B-RA-VIVIAN-COMPOSE-CONFIRMATION-PROMPT` und `B-RA-VR-SHOW-CONFIRMATION-AFFORDANCE` die Startbestaetigung an; nach `B-E11` werden `B-RA-CM-REQUEST-BREWING-START`, `B-RA-CM-SYNC-BREWING-STATE` und `B-RA-TRACE-SYNC-START-OUTCOME` ausgefuehrt. | `SA-B-VIVIAN-AWAITING-CONFIRMATION`, `SA-B-BREWING-CONFIRMED`, `SA-B-BREWING-START-ISSUED` und `SA-B-CM-BREWING` treten ein; ein Start ohne `B-MAIN-G08` ist nicht erlaubt. |
| `B-VC-006-MAIN-COMPLETION` | abstrakt und runtime-nah | `B-REQ-012`; `B-REQ-013`; `B-REQ-018` | `SC-B-01-MAIN` | `B-RB-VIVIAN-COMPLETION-REPORT` | Durchlauf des erfolgreichen Hauptpfads bis `B-MAIN-S20`; nach `B-E15` und `B-E16` werden `B-RA-VIVIAN-COMPOSE-COMPLETION-REPORT` und `B-RA-VR-PRESENT-COMPLETION-REPORT` ausgefuehrt. | `SA-B-CM-BREWING`, `SA-B-CM-PROGRESS-VISIBLE`, `SA-B-CM-FINISHED`, `SA-B-CM-COMPLETION-FEEDBACK` und `SA-B-VIVIAN-COMPLETION-REPORTED` sind beobachtbar. |
| `B-VC-007-ALTERNATIVE-MISSING-CUP` | abstrakt und runtime-nah | `B-REQ-005`; `B-REQ-006`; `B-REQ-007`; `B-REQ-017` | `SC-B-01-ALT01` | `B-RB-VIVIAN-CUP-CORRECTION`; `B-RB-VIVIAN-PROGRAM-GUIDANCE` | Nach `B-MAIN-S05` gilt `B-ALT-G01` mit `CoffeeMachine.cupPresent=false`; Ausfuehren von `B-RA-VIVIAN-COMPOSE-CUP-CORRECTION` vor `B-RA-VR-PRESENT-CUP-CORRECTION`; danach korrigiert der Visitor die Tasse und `B-ALT-G02` wird wahr. | `SA-B-CM-CUP-MISSING`, `SA-B-VIVIAN-CUP-CORRECTION-GUIDANCE`, `SA-B-CUP-PLACED` und `SA-B-CM-CUP-PRESENT` treten ein; der Ablauf kehrt vor `B-MAIN-S06` in den Hauptpfad zurueck. |
| `B-VC-008-EXCEPTION-READINESS-FAILED` | konkret, runtime-nah | `B-REQ-009`; `B-REQ-014`; `B-REQ-015`; `B-REQ-017` | `SC-B-01-EX01` | `B-RB-COFFEE-READINESS-CHECK`; `B-RB-VIVIAN-ERROR-EXPLANATION`; `B-RB-VIVIAN-EXCEPTION-CLOSE` | Bereitschaftspruefung nach `B-MAIN-S11` liefert mit `B-RA-CM-EVALUATE-READINESS` das Ergebnis `failed` und `reasonCode=waterLevelLow`; danach werden Fehlererklaerung und Exception-Abschluss ueber `B-RA-VIVIAN-COMPOSE-ERROR-EXPLANATION`, `B-RA-VR-PRESENT-ERROR-EXPLANATION`, `B-RA-TRACE-SYNC-ERROR-OUTCOME`, `B-RA-VIVIAN-CLOSE-EXCEPTION-FEEDBACK` und `B-RA-TRACE-SYNC-EXCEPTION-CLOSED` ausgefuehrt. | `SA-B-READINESS-FAILED`, `SA-B-CM-WATER-LOW`, `SA-B-CM-NOT-READY`, `SA-B-VIVIAN-ERROR-EXPLAINED`, `SA-B-CM-START-BLOCKED`, `SA-B-CM-SAFE`, `SA-B-CM-NOT-BREWING` und `SA-B-VIVIAN-EXCEPTION-CLOSED` treten ein; es gibt keine Rueckkehr zu `B-MAIN-S12`. |
| `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT` | abstrakt, strukturell | `B-REQ-017`; `B-REQ-018` | `UC-B-01` | alle B-RuntimeBindings als gepruefte Referenzmenge | Modellinspektion aller B-Artefakte von `ScenarioStep` ueber `CapabilityUse`, `Capability`, `RuntimeBinding` bis `RuntimeAction`. | Kein `ScenarioStep`, keine `CapabilityUse`, keine `Capability` und kein `Effect` referenziert eine RuntimeAction direkt; technische Endpoints, Topics und Schemas stehen nur in RuntimeActions. |
| `B-VC-010-RUNTIME-COVERAGE` | abstrakt, strukturell | `B-REQ-017`; `B-REQ-018` | `UC-B-01` | alle B-RuntimeBindings | Modellinspektion der RuntimeBinding- und RuntimeAction-Artefakte aus Task 8.10 und 8.11. | Alle elf RuntimeBindings referenzieren genau eine Capability; alle elf RuntimeBindings besitzen mindestens eine RuntimeAction; alle 25 RuntimeActions besitzen genau einen Owner. |

## RuntimeBinding-Abdeckung

| RuntimeBinding-ID | Geprueft durch ValidationCases | Ergebnis |
| --- | --- | --- |
| `B-RB-VIVIAN-GUIDANCE-MODE` | `B-VC-002-MAIN-GUIDANCE-START`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | abgedeckt |
| `B-RB-VIVIAN-CUP-GUIDANCE` | `B-VC-002-MAIN-GUIDANCE-START`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | abgedeckt |
| `B-RB-VIVIAN-PROGRAM-GUIDANCE` | `B-VC-003-CUP-AND-PROGRAM-GUIDANCE`; `B-VC-007-ALTERNATIVE-MISSING-CUP`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | abgedeckt |
| `B-RB-VIVIAN-REQUEST-CONFIRMED` | `B-VC-004-REQUEST-READINESS-PASSED`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | abgedeckt |
| `B-RB-COFFEE-READINESS-CHECK` | `B-VC-004-REQUEST-READINESS-PASSED`; `B-VC-008-EXCEPTION-READINESS-FAILED`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | abgedeckt |
| `B-RB-VIVIAN-CONFIRMATION-PROMPT` | `B-VC-005-CONFIRMATION-AND-START`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | abgedeckt |
| `B-RB-COFFEE-START-BREWING` | `B-VC-005-CONFIRMATION-AND-START`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | abgedeckt |
| `B-RB-VIVIAN-COMPLETION-REPORT` | `B-VC-006-MAIN-COMPLETION`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | abgedeckt |
| `B-RB-VIVIAN-CUP-CORRECTION` | `B-VC-007-ALTERNATIVE-MISSING-CUP`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | abgedeckt |
| `B-RB-VIVIAN-ERROR-EXPLANATION` | `B-VC-008-EXCEPTION-READINESS-FAILED`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | abgedeckt |
| `B-RB-VIVIAN-EXCEPTION-CLOSE` | `B-VC-008-EXCEPTION-READINESS-FAILED`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | abgedeckt |

## Requirement-Abdeckung

| Requirement-ID | Geprueft durch ValidationCases | Bewertung |
| --- | --- | --- |
| `B-REQ-001` | `B-VC-001-USECASE-STRUCTURE` | UseCase, Actor, Agent, Interaktionsobjekt und Scenarios sind pruefbar. |
| `B-REQ-002` | `B-VC-001-USECASE-STRUCTURE` | Actor/Agent-Trennung ist pruefbar. |
| `B-REQ-003` | `B-VC-002-MAIN-GUIDANCE-START` | Assistenzstart ist pruefbar. |
| `B-REQ-004` | `B-VC-002-MAIN-GUIDANCE-START` | Vivian-Fuehrungsmodus und erster Hinweis sind pruefbar. |
| `B-REQ-005` | `B-VC-003-CUP-AND-PROGRAM-GUIDANCE`; `B-VC-007-ALTERNATIVE-MISSING-CUP` | Tassenbedingung ist im Haupt- und Alternativpfad pruefbar. |
| `B-REQ-006` | `B-VC-007-ALTERNATIVE-MISSING-CUP` | Korrigierbare fehlende Tasse ist pruefbar. |
| `B-REQ-007` | `B-VC-003-CUP-AND-PROGRAM-GUIDANCE`; `B-VC-007-ALTERNATIVE-MISSING-CUP` | Programmauswahl nach erkannter Tasse ist pruefbar. |
| `B-REQ-008` | `B-VC-004-REQUEST-READINESS-PASSED` | Bruehanforderung ist pruefbar. |
| `B-REQ-009` | `B-VC-004-REQUEST-READINESS-PASSED`; `B-VC-008-EXCEPTION-READINESS-FAILED` | Bereitschaftspruefung ist fuer positive und negative Ergebnisse pruefbar. |
| `B-REQ-010` | `B-VC-005-CONFIRMATION-AND-START` | Explizite Startbestaetigung ist pruefbar. |
| `B-REQ-011` | `B-VC-005-CONFIRMATION-AND-START`; `B-VC-008-EXCEPTION-READINESS-FAILED` | Start nur bei Freigabe ist pruefbar. |
| `B-REQ-012` | `B-VC-005-CONFIRMATION-AND-START`; `B-VC-006-MAIN-COMPLETION` | Beobachtbarer Bruehzustand ist pruefbar. |
| `B-REQ-013` | `B-VC-006-MAIN-COMPLETION` | Fortschritt, Abschluss und Abschlussfeedback sind pruefbar. |
| `B-REQ-014` | `B-VC-008-EXCEPTION-READINESS-FAILED` | Exception bei fehlender Bereitschaft ist pruefbar. |
| `B-REQ-015` | `B-VC-008-EXCEPTION-READINESS-FAILED` | Sicherer Exception-Abschluss ist pruefbar. |
| `B-REQ-016` | `B-VC-001-USECASE-STRUCTURE` | Include/Extend-Abgrenzung ist pruefbar. |
| `B-REQ-017` | `B-VC-002-MAIN-GUIDANCE-START`; `B-VC-003-CUP-AND-PROGRAM-GUIDANCE`; `B-VC-004-REQUEST-READINESS-PASSED`; `B-VC-005-CONFIRMATION-AND-START`; `B-VC-007-ALTERNATIVE-MISSING-CUP`; `B-VC-008-EXCEPTION-READINESS-FAILED`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | Keine technische Kurzschaltung ist in Ablauf- und Strukturfaellen pruefbar. |
| `B-REQ-018` | `B-VC-001-USECASE-STRUCTURE`; `B-VC-006-MAIN-COMPLETION`; `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT`; `B-VC-010-RUNTIME-COVERAGE` | Traceability ist ueber Struktur, Hauptpfad und Runtime-Schichten pruefbar. |

## ExpectedOutcome-Rueckbindung

| ValidationCase-ID | Erwartete Outcomes | Outcome-Typ |
| --- | --- | --- |
| `B-VC-001-USECASE-STRUCTURE` | Genau ein Main Scenario; `Visitor` als Actor; `VivianAssistant` als Agent; `CoffeeMachine` als Entity; keine Include/Extend-Fehlverwendung | Strukturregel |
| `B-VC-002-MAIN-GUIDANCE-START` | `SA-B-VIVIAN-GUIDING`; `SA-B-VIVIAN-GUIDANCE-CUP`; indirekter Runtime-Pfad | StateAssertions und Strukturregel |
| `B-VC-003-CUP-AND-PROGRAM-GUIDANCE` | `SA-B-CUP-PLACED`; `SA-B-CM-CUP-PRESENT`; `SA-B-VIVIAN-GUIDANCE-PROGRAM`; spaeter `SA-B-CM-PROGRAM-COFFEE` | StateAssertions |
| `B-VC-004-REQUEST-READINESS-PASSED` | `SA-B-BREWING-REQUESTED`; `SA-B-VIVIAN-INTENT-CONFIRMED`; `SA-B-CM-READY`; `SA-B-CM-READY-FEEDBACK`; `SA-B-CM-START-PERMISSION` | StateAssertions |
| `B-VC-005-CONFIRMATION-AND-START` | `SA-B-VIVIAN-AWAITING-CONFIRMATION`; `SA-B-BREWING-CONFIRMED`; `SA-B-BREWING-START-ISSUED`; `SA-B-CM-BREWING`; kein Start ohne Guard `B-MAIN-G08` | StateAssertions und Guard-Regel |
| `B-VC-006-MAIN-COMPLETION` | `SA-B-CM-BREWING`; `SA-B-CM-PROGRESS-VISIBLE`; `SA-B-CM-FINISHED`; `SA-B-CM-COMPLETION-FEEDBACK`; `SA-B-VIVIAN-COMPLETION-REPORTED` | StateAssertions |
| `B-VC-007-ALTERNATIVE-MISSING-CUP` | `SA-B-CM-CUP-MISSING`; `SA-B-VIVIAN-CUP-CORRECTION-GUIDANCE`; `SA-B-CUP-PLACED`; `SA-B-CM-CUP-PRESENT`; Rueckkehr vor `B-MAIN-S06` | StateAssertions und Ablaufstruktur |
| `B-VC-008-EXCEPTION-READINESS-FAILED` | `SA-B-READINESS-FAILED`; `SA-B-CM-WATER-LOW`; `SA-B-CM-NOT-READY`; `SA-B-VIVIAN-ERROR-EXPLAINED`; `SA-B-CM-START-BLOCKED`; `SA-B-CM-SAFE`; `SA-B-CM-NOT-BREWING`; `SA-B-VIVIAN-EXCEPTION-CLOSED`; keine Rueckkehr zu `B-MAIN-S12` | StateAssertions und Ablaufstruktur |
| `B-VC-009-NO-DIRECT-RUNTIME-SHORTCUT` | Keine direkte RuntimeAction-Referenz von `ScenarioStep`, `CapabilityUse`, `Capability` oder `Effect` | Strukturregel |
| `B-VC-010-RUNTIME-COVERAGE` | Elf RuntimeBindings mit genau einer Capability; 25 RuntimeActions mit genau einem Owner; jede Binding hat mindestens eine Action | Kardinalitaets- und Strukturregel |

## Warum strukturelle ValidationCases notwendig sind

Nicht jede Anforderung wird durch eine technische Runtimeausfuehrung geprueft. Einige Anforderungen pruefen die Korrektheit des Modells selbst, etwa:

- genau ein Main Scenario,
- korrekte Actor/Agent/Entity-Trennung,
- Alternative mit Rueckfuehrung,
- Exception ohne Rueckfuehrung,
- keine direkte technische Kurzschaltung,
- vollstaendige RuntimeBinding- und RuntimeAction-Abdeckung.

Diese Faelle sind dennoch echte ValidationCases, weil sie einen Stimulus besitzen, naemlich die Modellinspektion, und ein erwartetes Outcome, naemlich eine konkrete Modellstruktur oder das Fehlen einer verbotenen Struktur.

## Keine Besitzsemantik bei RuntimeBinding-Pruefung

| Beziehung | Interpretation in diesem Artefakt |
| --- | --- |
| `ValidationCase -> RuntimeBinding` | Der ValidationCase fuehrt oder prueft die RuntimeBinding. |
| `RuntimeBinding -> RuntimeAction` | Die RuntimeBinding besitzt ihre RuntimeActions. |
| `ValidationCase -> RuntimeAction` | Nicht als Metamodellkante verwendet; RuntimeActions erscheinen nur im Stimulus-Text. |

## Abnahmekontrolle

| Kriterium aus Task 8.12 | Erfuellung |
| --- | --- |
| ValidationCase-Instanzen angelegt | Zehn ValidationCases sind angelegt. |
| Jeder ValidationCase hat Stimulus | Jede Tabellenzeile besitzt einen konkreten Stimulus. |
| Jeder ValidationCase hat expected Outcome | Jede Tabellenzeile besitzt mindestens ein erwartetes Outcome. |
| Hauptpfad ist abgedeckt | `B-VC-002` bis `B-VC-006` decken den erfolgreichen Hauptpfad ab. |
| Alternative ist abgedeckt | `B-VC-007` deckt die fehlende Tasse mit Rueckkehr in den Hauptpfad ab. |
| Exception ist abgedeckt | `B-VC-008` deckt fehlgeschlagene Bereitschaftspruefung, Startblockade und Exception-Abschluss ab. |
| RuntimeBindings sind pruefbar angebunden | Alle elf RuntimeBindings werden durch mindestens einen ValidationCase geprueft. |
| Strukturregeln sind abgedeckt | `B-VC-001`, `B-VC-009` und `B-VC-010` pruefen Struktur, Traceability und Runtime-Kardinalitaeten. |

## Konsequenz fuer Task 8.13

Task 8.13 kann nun die Kardinalitaeten und Invarianten fuer Anwendungsfall B pruefen. Besonders wichtig sind die Beziehungen `ValidationCase -> RuntimeBinding [0..*]`, `RuntimeBinding -> RuntimeAction [1..*]`, `Capability -> Effect [1..*]`, `CapabilityUse -> Capability [1]`, `Scenario -> ScenarioStep [1..*]` und die Main-Scenario-Eindeutigkeit.
