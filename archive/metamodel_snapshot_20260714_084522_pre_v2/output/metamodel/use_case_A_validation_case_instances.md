# Anwendungsfall A: ValidationCase-Instanzen

Stand: 2026-07-07

Task: 4.15 `ValidationCase-Instanzen fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

Ein `ValidationCase` beschreibt einen pruefbaren Fall mit Stimulus und mindestens einem erwarteten Outcome. Er kann Requirements verifizieren, einen Use Case validieren und RuntimeBindings ausfuehren oder pruefen. Er besitzt diese RuntimeBindings aber nicht.

Fuer Anwendungsfall A gilt:

- Jeder ValidationCase besitzt mindestens einen Stimulus.
- Jeder ValidationCase besitzt mindestens ein erwartetes Outcome.
- `ValidationCase -> RuntimeBinding [0..*]` ist eine pruefende Dependency, keine Komposition.
- RuntimeActions duerfen im Stimulus als technische Ausfuehrungsdetails genannt werden, bleiben aber unter ihrer RuntimeBinding eingeordnet.
- Structural ValidationCases duerfen ohne RuntimeBinding arbeiten, wenn sie Modellregeln pruefen.
- Kein ValidationCase erzeugt eine direkte `ScenarioStep -> RuntimeAction`-Kante.

## Angelegte ValidationCase-Instanzen

| ValidationCase-ID | Art | `verifies` | `validates` | `executes/checks` RuntimeBinding | Stimulus | ExpectedOutcome |
| --- | --- | --- | --- | --- | --- | --- |
| `A-VC-001-MAIN-PRECONDITION-CHAIN` | abstrakt, strukturell | `A-REQ-002`; `A-REQ-003`; `A-REQ-004`; `A-REQ-005` | `UC-A-01` | keine | Modellinspektion des Hauptpfads `A-MAIN-S01` bis `A-MAIN-S04` mit Start-Event `entered(SceneParticipant, TriggerZone)`. | `A-SA-S01-01`; `A-SA-S01-02`; `A-SA-S02-01`; `A-SA-S02-02`; `A-SA-S03-01`; `A-SA-S03-02`; `A-SA-S04-01`; `A-SA-S04-02` sind erreichbar und pruefbar. |
| `A-VC-002-ROLE-BINDING` | konkret, runtime-nah | `A-REQ-006`; `A-REQ-013`; `A-REQ-015` | `UC-A-01` | `A-RB-ROLE-EXECUTOR-VR` | Ausfuehren der Binding-Sequenz `A-RA-ROLE-SET` vor `A-RA-ROLE-SYNC` fuer `AgentBody` mit `targetRole=executor`. | `A-SA-S05-01` und `A-SA-S05-02` treten ein; keine direkte Referenz von `A-MAIN-S05` auf eine RuntimeAction entsteht. |
| `A-VC-003-TARGET-ACTION-BINDING` | konkret, runtime-nah | `A-REQ-007`; `A-REQ-008`; `A-REQ-013`; `A-REQ-015` | `UC-A-01` | `A-RB-TARGET-ACTION-VR` | Ausfuehren der Binding-Sequenz `A-RA-TARGET-ACTION-REQUEST` vor `A-RA-TARGET-OCCUPANCY-SYNC` fuer `AgentBody` und `TargetZone`. | `A-SA-S06-01` und `A-SA-S06-02` treten ein; die Zielhandlung bleibt ueber `CapabilityUse -> Capability -> RuntimeBinding` vermittelt. |
| `A-VC-004-MAIN-COMPLETION` | abstrakt, end-to-end | `A-REQ-001`; `A-REQ-008`; `A-REQ-009`; `A-REQ-010`; `A-REQ-015` | `UC-A-01` | `A-RB-ROLE-EXECUTOR-VR`; `A-RB-TARGET-ACTION-VR` | Durchlauf des gueltigen Hauptpfads von `A-MAIN-S01` bis `A-MAIN-S09` mit erreichbarer Zielzone und nicht blockiertem Agenten. | `A-SA-S07-01`; `A-SA-S07-02`; `A-SA-S08-01`; `A-SA-S08-02`; `A-SA-S09-01`; `A-SA-S09-02` sind beobachtbar. |
| `A-VC-005-ALTERNATIVE-TEMPORARY-BLOCK` | abstrakt, strukturell | `A-REQ-011`; `A-REQ-015` | `UC-A-01` | keine | Modellinspektion des Alternativpfads `A-ALT-SC01` bei temporaerer Blockade der `ObstacleRegion`. | `A-ALT-SA01`; `A-ALT-SA02`; `A-ALT-SA03`; `A-ALT-SA04` sind vorhanden; der Pfad fuehrt fachlich zum Hauptpfad zurueck. |
| `A-VC-006-EXCEPTION-BLOCKED-PROGRESS` | konkret, runtime-nah | `A-REQ-012`; `A-REQ-013`; `A-REQ-015` | `UC-A-01` | `A-RB-BLOCKED-PROGRESS-VR` | Ausfuehren der Binding-Sequenz `A-RA-BLOCK-PROGRESS-HOLD` vor `A-RA-BLOCK-STATE-SYNC` bei dauerhaft blockierter `ObstacleRegion`. | `A-EX-SA03` und `A-EX-SA04` treten ein; danach sind `A-EX-SA05` und `A-EX-SA06` als sicherer Fehlerabschluss erwartbar. |
| `A-VC-007-NO-DIRECT-RUNTIME-SHORTCUT` | abstrakt, strukturell | `A-REQ-013`; `A-REQ-015` | `UC-A-01` | alle A-RuntimeBindings als gepruefte Referenzmenge | Modellinspektion aller A-Artefakte von `ScenarioStep` ueber `CapabilityUse`, `Capability`, `RuntimeBinding` bis `RuntimeAction`. | Kein `ScenarioStep` und keine `CapabilityUse` referenziert eine RuntimeAction direkt; technische Endpoints stehen nur in RuntimeActions. |
| `A-VC-008-NO-ARTIFICIAL-PARALLELGROUP` | abstrakt, strukturell | `A-REQ-014` | `UC-A-01` | keine | Modellinspektion von `A-MAIN-SC01`, `A-ALT-SC01` und `A-EX-SC01` auf ParallelGroup-Instanzen. | Fuer Anwendungsfall A existiert keine `ParallelGroup`; damit wird keine nebenlaeufige Struktur ohne fachlichen Bedarf erzeugt. |

## RuntimeBinding-Abdeckung

| RuntimeBinding-ID | Geprueft durch ValidationCases | Ergebnis |
| --- | --- | --- |
| `A-RB-ROLE-EXECUTOR-VR` | `A-VC-002-ROLE-BINDING`; `A-VC-004-MAIN-COMPLETION`; `A-VC-007-NO-DIRECT-RUNTIME-SHORTCUT` | abgedeckt |
| `A-RB-TARGET-ACTION-VR` | `A-VC-003-TARGET-ACTION-BINDING`; `A-VC-004-MAIN-COMPLETION`; `A-VC-007-NO-DIRECT-RUNTIME-SHORTCUT` | abgedeckt |
| `A-RB-BLOCKED-PROGRESS-VR` | `A-VC-006-EXCEPTION-BLOCKED-PROGRESS`; `A-VC-007-NO-DIRECT-RUNTIME-SHORTCUT` | abgedeckt |

## Requirement-Abdeckung

| Requirement-ID | Geprueft durch ValidationCases | Bewertung |
| --- | --- | --- |
| `A-REQ-001` | `A-VC-004-MAIN-COMPLETION` | UseCase und Hauptablauf werden end-to-end validiert. |
| `A-REQ-002` | `A-VC-001-MAIN-PRECONDITION-CHAIN` | Start-Event ist pruefbar. |
| `A-REQ-003` | `A-VC-001-MAIN-PRECONDITION-CHAIN` | Raeumliche Gueltigkeit ist pruefbar. |
| `A-REQ-004` | `A-VC-001-MAIN-PRECONDITION-CHAIN` | Handlungsbereitschaft ist pruefbar. |
| `A-REQ-005` | `A-VC-001-MAIN-PRECONDITION-CHAIN` | Zielerreichbarkeit ist pruefbar. |
| `A-REQ-006` | `A-VC-002-ROLE-BINDING` | Rollenwechsel ist runtime-nah validierbar. |
| `A-REQ-007` | `A-VC-003-TARGET-ACTION-BINDING` | Zielgerichtete Handlung ist runtime-nah validierbar. |
| `A-REQ-008` | `A-VC-003-TARGET-ACTION-BINDING`; `A-VC-004-MAIN-COMPLETION` | Zielzustand ist als Zwischen- und Endzustand pruefbar. |
| `A-REQ-009` | `A-VC-004-MAIN-COMPLETION` | Zielverifikation ist im Hauptabschluss pruefbar. |
| `A-REQ-010` | `A-VC-004-MAIN-COMPLETION` | Ergebnisrueckmeldung ist pruefbar. |
| `A-REQ-011` | `A-VC-005-ALTERNATIVE-TEMPORARY-BLOCK` | Alternative ist pruefbar. |
| `A-REQ-012` | `A-VC-006-EXCEPTION-BLOCKED-PROGRESS` | Exception ist pruefbar. |
| `A-REQ-013` | `A-VC-002-ROLE-BINDING`; `A-VC-003-TARGET-ACTION-BINDING`; `A-VC-006-EXCEPTION-BLOCKED-PROGRESS`; `A-VC-007-NO-DIRECT-RUNTIME-SHORTCUT` | Trennung von fachlichem Ablauf und Runtime ist pruefbar. |
| `A-REQ-014` | `A-VC-008-NO-ARTIFICIAL-PARALLELGROUP` | Keine kuenstliche ParallelGroup ist pruefbar. |
| `A-REQ-015` | `A-VC-002-ROLE-BINDING`; `A-VC-003-TARGET-ACTION-BINDING`; `A-VC-004-MAIN-COMPLETION`; `A-VC-005-ALTERNATIVE-TEMPORARY-BLOCK`; `A-VC-006-EXCEPTION-BLOCKED-PROGRESS`; `A-VC-007-NO-DIRECT-RUNTIME-SHORTCUT` | Traceability ist ueber mehrere Pfade pruefbar. |

## ExpectedOutcome-Rueckbindung

| ValidationCase-ID | Erwartete Outcomes | Outcome-Typ |
| --- | --- | --- |
| `A-VC-001-MAIN-PRECONDITION-CHAIN` | `A-SA-S01-01`; `A-SA-S01-02`; `A-SA-S02-01`; `A-SA-S02-02`; `A-SA-S03-01`; `A-SA-S03-02`; `A-SA-S04-01`; `A-SA-S04-02` | StateAssertions |
| `A-VC-002-ROLE-BINDING` | `A-SA-S05-01`; `A-SA-S05-02`; keine direkte Step-zu-RuntimeAction-Referenz | StateAssertions und Strukturregel |
| `A-VC-003-TARGET-ACTION-BINDING` | `A-SA-S06-01`; `A-SA-S06-02`; indirekter Runtime-Pfad bleibt erhalten | StateAssertions und Strukturregel |
| `A-VC-004-MAIN-COMPLETION` | `A-SA-S07-01`; `A-SA-S07-02`; `A-SA-S08-01`; `A-SA-S08-02`; `A-SA-S09-01`; `A-SA-S09-02` | StateAssertions |
| `A-VC-005-ALTERNATIVE-TEMPORARY-BLOCK` | `A-ALT-SA01`; `A-ALT-SA02`; `A-ALT-SA03`; `A-ALT-SA04`; Rueckfuehrung zum Hauptpfad | StateAssertions und Ablaufstruktur |
| `A-VC-006-EXCEPTION-BLOCKED-PROGRESS` | `A-EX-SA03`; `A-EX-SA04`; `A-EX-SA05`; `A-EX-SA06` | StateAssertions |
| `A-VC-007-NO-DIRECT-RUNTIME-SHORTCUT` | Keine direkte RuntimeAction-Referenz von `ScenarioStep` oder `CapabilityUse` | Strukturregel |
| `A-VC-008-NO-ARTIFICIAL-PARALLELGROUP` | Keine `ParallelGroup` fuer A | Strukturregel |

## Warum strukturelle ValidationCases notwendig sind

Nicht jede Anforderung wird durch eine technische Runtimeausfuehrung geprueft. Einige Anforderungen pruefen die Korrektheit des Modells selbst, etwa:

- keine direkte technische Kurzschaltung,
- keine kuenstliche ParallelGroup,
- korrekte Rueckfuehrung der Alternative,
- vollstaendige Traceability.

Diese Faelle sind dennoch echte ValidationCases, weil sie einen Stimulus besitzen, naemlich die Modellinspektion, und ein erwartetes Outcome, naemlich eine konkrete Modellstruktur oder das Fehlen einer verbotenen Struktur.

## Keine Besitzsemantik bei RuntimeBinding-Pruefung

| Beziehung | Interpretation in diesem Artefakt |
| --- | --- |
| `ValidationCase -> RuntimeBinding` | Der ValidationCase fuehrt oder prueft die RuntimeBinding. |
| `RuntimeBinding -> RuntimeAction` | Die RuntimeBinding besitzt ihre RuntimeActions. |
| `ValidationCase -> RuntimeAction` | Nicht als Metamodellkante verwendet; RuntimeActions erscheinen nur im Stimulus-Text. |

## Abnahmekontrolle

| Kriterium aus Task 4.15 | Erfuellung |
| --- | --- |
| ValidationCase-Instanzen angelegt | Acht ValidationCases sind angelegt. |
| Jeder ValidationCase hat Stimulus | Jede Tabellenzeile besitzt einen konkreten Stimulus. |
| Jeder ValidationCase hat expected Outcome | Jede Tabellenzeile besitzt mindestens ein erwartetes Outcome. |
| RuntimeBindings sind pruefbar angebunden | Alle drei RuntimeBindings werden durch mindestens einen ValidationCase geprueft. |
| Main, Alternative und Exception sind abgedeckt | Hauptpfad, Alternativpfad und Exception-Pfad besitzen ValidationCases. |
| Strukturregeln sind abgedeckt | Keine direkte RuntimeAction-Referenz und keine kuenstliche ParallelGroup werden geprueft. |

## Konsequenz fuer Task 4.16

Task 4.16 kann nun die Kardinalitaeten fuer Anwendungsfall A pruefen. Besonders wichtig sind die Beziehungen `ValidationCase -> RuntimeBinding [0..*]`, `RuntimeBinding -> RuntimeAction [1..*]`, `Capability -> Effect [1..*]` und `CapabilityUse -> Capability [1]`.
