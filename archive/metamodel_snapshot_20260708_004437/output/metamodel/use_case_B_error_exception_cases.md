# Anwendungsfall B: Fehler- und Ausnahmefaelle

Stand: 2026-07-07

Task: 6.8 `Fehler- und Ausnahmefaelle sammeln`

## Zweck

Diese Datei sammelt Fehler-, Abbruch- und Ausnahmefaelle fuer die assistierte Bedienung der virtuellen Kaffeemaschine mit Vivian. Die Faelle leiten sich aus den Bedienhandlungen aus Task 6.5, den Objektzustaenden aus Task 6.6 und den Conditions aus Task 6.7 ab.

Die Liste erzeugt noch keine finalen `Scenario`-Instanzen. Sie bereitet aber vor, welche Faelle spaeter als `Scenario.kind = alternative` oder `Scenario.kind = exception` modelliert werden koennen.

## Einordnung der Fallarten

| Fallart | Bedeutung | Spaetere Modellierung |
| --- | --- | --- |
| `alternative` | Korrigierbarer oder optionaler Pfad, der zum Hauptablauf zurueckkehren kann. | `Scenario.kind = alternative` oder `StepRelation.kind = alternative`. |
| `controlledAbort` | Benutzer oder System beendet den Ablauf kontrolliert in einem sicheren Zustand. | Alternative oder Exception, je nach Eintrittspunkt. |
| `exception` | Fehlerfall, der den Hauptablauf verhindert oder in einen sicheren/erklaerbaren Endzustand fuehrt. | `Scenario.kind = exception` oder `StepRelation.kind = exception`. |
| `nonErrorBranch` | Fachlich gueltige Abweichung, aber kein Fehler. | Alternative oder spaeter eventuell `Extend`. |

## Fehler- und Ausnahmefallkatalog

| ID | Fallart | Ausloeser oder fehlgeschlagene Bedingung | Erkennbare Ursache | Erwartete Reaktion | Erwarteter Zustand / Outcome | Spaetere Modellierung |
| --- | --- | --- | --- | --- | --- | --- |
| B-EXC-001 | exception | `not B-COND-001` | Kaffeemaschine ist nicht verfuegbar. | Vivian erklaert, dass die Bedienung nicht gestartet werden kann; kein Bruehstart wird angefordert. | `CoffeeMachine.availabilityState = unavailable`; `CoffeeMachine.safeState = true` | Exception-Szenario mit sicherem Ende. |
| B-EXC-002 | exception | `not B-COND-002` | Kaffeemaschine ist ausgeschaltet oder nicht aktivierbar. | Vivian meldet die Ursache und verhindert Startfreigabe. | `CoffeeMachine.powerState = off`; `CoffeeMachine.startPermission = blocked` | Exception oder Korrekturpfad, falls Einschalten im Scope liegt. |
| B-ALT-001 | alternative | `not B-COND-004` | Vivian-Assistenzmodus ist nicht verfuegbar. | System bietet unassistierte Bedienung an oder beendet den assistierten Use Case erklaerbar. | `VivianAssistant.mode != guiding`; kein Vivian-CapabilityUse fuer Anleitung | Alternative, kein Maschinenfehler. |
| B-ALT-002 | nonErrorBranch | `not B-COND-005` | Benutzer hat keine Hilfe angefordert. | Assistenzpfad wird nicht betreten; normaler Bedienpfad kann ohne Vivian-Hilfe weiterlaufen. | Kein Fehlerzustand; `helpRequested = false` | Alternative oder ausgelassener Extend. |
| B-ALT-003 | alternative | `not B-COND-006` oder `not B-COND-016` | Tasse fehlt oder wurde nicht bestaetigt. | Vivian fordert Benutzer auf, eine Tasse zu platzieren; nach Korrektur Rueckkehr zur Bereitschaftspruefung. | `CoffeeMachine.cupPresent = false` bis Korrektur, danach `CoffeeMachine.cupPresent = true` | Korrigierbarer Alternativpfad. |
| B-ALT-004 | alternative | `not B-COND-008` | Kein Kaffeeprogramm wurde gewaehlt. | Vivian fuehrt zur Programmauswahl; Start bleibt blockiert, bis Auswahl gesetzt ist. | `CoffeeMachine.selectedProgram = none`; spaeter `CoffeeMachine.selectedProgram = coffee` | Korrigierbarer Alternativpfad. |
| B-ALT-005 | alternative | `not B-COND-007`, aber Korrektur moeglich | Wasserstand ist zu niedrig, kann aber im Modell korrigiert werden. | Vivian erklaert fehlendes Wasser; Benutzer korrigiert Voraussetzung. | `CoffeeMachine.waterLevel = low`, danach `CoffeeMachine.waterLevel = sufficient` | Alternative mit Rueckkehr zur Bereitschaftspruefung. |
| B-EXC-003 | exception | `not B-COND-007` und Korrektur nicht moeglich | Wasserstand ist zu niedrig und kann im aktuellen Ablauf nicht behoben werden. | Vivian erklaert Abbruchgrund; Bruehstart wird nicht ausgefuehrt. | `CoffeeMachine.waterLevel = low`; `CoffeeMachine.startPermission = blocked`; `CoffeeMachine.safeState = true` | Exception-Szenario mit erklaerbarem Ende. |
| B-EXC-004 | exception | `B-COND-018` oder `not B-COND-017` | Bereitschaftspruefung schlaegt fehl. | Vivian nennt die fehlgeschlagene Voraussetzung und startet nicht. | `ReadinessCheck.result = failed`; `CoffeeMachine.lifecycleState = notReady` | Exception, falls Ursache nicht innerhalb des Ablaufs korrigiert wird. |
| B-EXC-005 | exception | `not B-COND-009` | Startfreigabe ist blockiert. | Vivian verhindert assistierten Start und meldet Grund. | `CoffeeMachine.startPermission = blocked`; kein `CoffeeMachine.lifecycleState = brewing` | Exception oder Alternative je nach konkretem Grund. |
| B-ALT-006 | controlledAbort | `not B-COND-011` | Benutzer bestaetigt Vivians Rueckfrage nicht. | Vivian wartet, fragt erneut oder bietet Abbruch an. | `BrewingRequest.confirmed != true`; Maschine bleibt `idle` oder `ready` | Alternative mit Warten oder kontrolliertem Abbruch. |
| B-ALT-007 | controlledAbort | `not B-COND-012` | Benutzer bricht vor dem Bruehstart ab. | Ablauf wird beendet; Vivian bestaetigt Abbruch. | `BrewingRequest.state = cancelled`; `CoffeeMachine.safeState = true` | Kontrollierter Alternativabschluss. |
| B-EXC-006 | exception | `not B-COND-013` | Bruehvorgang laeuft bereits, doppelter Start waere unzulaessig. | Vivian meldet, dass bereits ein Vorgang laeuft; kein zweiter Start wird erzeugt. | `CoffeeMachine.lifecycleState = brewing`; bestehender Vorgang bleibt kontrolliert | Exception oder Guarded no-op. |
| B-EXC-007 | exception | `not B-COND-014` | Kaffeemaschine ist im Fehlerzustand. | Vivian erklaert Fehler und fuehrt nicht in den Hauptpfad zurueck, bevor ein sicherer Zustand hergestellt ist. | `CoffeeMachine.lifecycleState = error`; `CoffeeMachine.errorFeedback = visible` | Exception-Szenario. |
| B-EXC-008 | exception | `not B-COND-015` | Sicherer Zustand ist nicht bestaetigt. | System/Vivian blockiert Start und fordert sicheren Zustand. | `CoffeeMachine.safeState != true`; Start bleibt blockiert | Exception bis sicherer Zustand erreicht ist. |
| B-ALT-008 | controlledAbort | B-ACT-006 waehrend laufendem Vorgang | Benutzer bricht waehrend oder nach Start ab. | Vivian/System beendet oder stoppt den Ablauf kontrolliert, soweit fachlich erlaubt. | `CoffeeMachine.lifecycleState = cancelled` oder `CoffeeMachine.safeState = true` | Alternative oder Exception, abhaengig vom Eintrittspunkt. |
| B-EXC-009 | exception | Laufzeitbindung fuer Start-Capability fehlt spaeter | Fachliche Capability waere vorhanden, aber keine geeignete RuntimeBinding ist verfuegbar. | Validierung meldet fehlende technische Bindung; ScenarioStep bleibt fachlich korrekt, aber Ausfuehrung ist nicht moeglich. | Kein direkter `RuntimeAction`-Aufruf; `ValidationCase` schlaegt fehl | Mapping-/Runtime-Exception fuer spaetere Tasks, nicht als ScenarioStep-Technikdetail. |

## Korrigierbar versus fatal

| Ursache | Korrigierbar im aktuellen Ablauf? | Folge |
| --- | --- | --- |
| Tasse fehlt | Ja | Alternative: Benutzer platziert Tasse und kehrt zur Bereitschaftspruefung zurueck. |
| Kein Programm gewaehlt | Ja | Alternative: Benutzer waehlt Programm und kehrt zur Bereitschaftspruefung zurueck. |
| Wasserstand niedrig | Bedingt | Alternative bei Korrekturmoeglichkeit, Exception wenn nicht im Scope korrigierbar. |
| Maschine nicht verfuegbar | Nein | Exception mit erklaertem Ende. |
| Maschine ausgeschaltet | Bedingt | Exception, falls Einschalten nicht im Scope liegt; sonst Korrekturpfad. |
| Benutzer bestaetigt nicht | Ja | Warten, erneute Frage oder kontrollierter Abbruch. |
| Benutzer bricht ab | Ja, als gueltiger Abbruch | Kontrollierter Alternativabschluss mit sicherem Zustand. |
| Maschine im Fehlerzustand | Nein im normalen Bedienpfad | Exception; Rueckkehr erst nach Fehlerbehebung. |
| RuntimeBinding fehlt | Nein innerhalb des fachlichen Szenarios | Mapping-/Validierungsfehler, keine direkte technische Abkuerzung. |

## Erwartete sichere Endzustaende

| Fallgruppe | Sicherer oder erklaerbarer Endzustand |
| --- | --- |
| Start blockiert vor Bruehbeginn | `CoffeeMachine.lifecycleState in {idle, notReady}` und `CoffeeMachine.startPermission = blocked` |
| Kontrollierter Abbruch vor Start | `BrewingRequest.state = cancelled` und `CoffeeMachine.safeState = true` |
| Fehler waehrend Bereitschaftspruefung | `ReadinessCheck.result = failed`; relevante Ursache ist als Condition oder StateAssertion sichtbar |
| Maschinenfehler | `CoffeeMachine.lifecycleState = error`; `CoffeeMachine.errorFeedback = visible` |
| Fehlende RuntimeBinding | Fachlicher Trace bleibt bestehen; ValidationCase meldet fehlende technische Ausfuehrbarkeit |

## Kandidaten fuer spaetere Scenarios

| Spaeterer Scenario-Kandidat | Enthaltene Faelle | Ziel |
| --- | --- | --- |
| `B-ALT-SC01 CorrectMissingCupOrProgram` | `B-ALT-003`, `B-ALT-004` | Korrigierbarer Pfad mit Rueckkehr zur Bereitschaftspruefung. |
| `B-ALT-SC02 ControlledUserAbort` | `B-ALT-006`, `B-ALT-007`, `B-ALT-008` | Gueltiger Abbruch ohne Maschinenfehler. |
| `B-EX-SC01 MachineNotReady` | `B-EXC-001`, `B-EXC-002`, `B-EXC-003`, `B-EXC-004`, `B-EXC-005` | Kein Bruehstart; Vivian erklaert Ursache. |
| `B-EX-SC02 UnsafeOrErrorState` | `B-EXC-006`, `B-EXC-007`, `B-EXC-008` | Start verhindern und sicheren/erklaerbaren Zustand herstellen. |
| `B-EX-SC03 RuntimeBindingMissing` | `B-EXC-009` | Spaeterer Mapping-/Validierungsfehler, kein fachlicher ScenarioStep mit Technikdetail. |

## Abnahmekontrolle

| Kriterium aus Task 6.8 | Erfuellung |
| --- | --- |
| Liste von Exceptions vorhanden | Der Katalog enthaelt 17 Fehler-, Abbruch- und Ausnahmefaelle. |
| Jede Ursache erkennbar | Jede Zeile nennt Ausloeser oder fehlgeschlagene Bedingung sowie erkennbare Ursache. |
| Jede erwartete Reaktion benannt | Jede Zeile enthaelt eine erwartete Reaktion von Vivian, System oder Modellvalidierung. |
| Sicherer oder erklaerbarer Zustand beschrieben | Jede Zeile enthaelt erwarteten Zustand oder Outcome. |
| Alternative und Exception getrennt | Fallarten unterscheiden `alternative`, `controlledAbort`, `exception` und `nonErrorBranch`. |
| Keine technische Direktkopplung | Auch der RuntimeBinding-Fall bleibt ein Mapping-/Validierungsfehler, kein direkter ScenarioStep-Endpoint. |

## Konsequenz fuer Task 7.1

Task 7.1 kann nun einen Main-Use-Case fuer B benennen. Der Name sollte die fachliche Nutzung der Kaffeemaschine mit Vivian beschreiben und nicht den technischen Controller-Aufruf.
