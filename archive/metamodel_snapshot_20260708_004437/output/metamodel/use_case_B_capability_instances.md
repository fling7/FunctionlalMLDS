# Anwendungsfall B: Capability- und Effect-Instanzen

Stand: 2026-07-07

Task: 8.9 `Capabilities fuer Kaffeemaschinenbedienung anlegen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Modellierungsregel

Eine `Capability` beschreibt eine fachliche Faehigkeit eines modellierten System- oder Objektanteils. Sie sagt, was im fachlichen Szenario geleistet werden kann, aber nicht, wie diese Leistung technisch ausgefuehrt wird.

Fuer Anwendungsfall B gilt deshalb:

- keine technischen Endpunkte,
- keine Tools,
- keine Topics,
- keine Controller- oder Engine-Befehle,
- keine direkte RuntimeAction-Referenz,
- keine direkte Kopplung von `ScenarioStep` zu technischer Ausfuehrung.

Eine `CapabilityUse` referenziert genau eine `Capability`. Die elf geplanten Capability-IDs aus Task 8.8 werden hier formal angelegt. Zu jeder Capability werden Intent, Preconditions und promised Effects beschrieben.

Da Task 8.9 ausdruecklich Effects fordert und fuer B kein separater Effect-Task folgt, werden die benoetigten `Effect`-Instanzen in dieser Datei kompakt mit angelegt. Sie bleiben fachlich und referenzieren vorhandene `StateAssertion`- und `Condition`-IDs aus Task 8.7.

## Angelegte Capability-Instanzen

| Capability-ID | Metamodellklasse | `uuid` | `shortName` | Bereitstellende Entity | Fachlicher Intent | Preconditions | `promisedEffect` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `CAP-B-VIVIAN-ENTER-GUIDANCE` | `Capability` | `CAP-B-VIVIAN-ENTER-GUIDANCE` | `VivianFuehrungsmodusAktivieren` | `ENT-B-01 VivianAssistant` | Vivian kann nach einem Hilfewunsch in einen fachlichen Fuehrungsmodus wechseln, damit die Bedienung der Kaffeemaschine als assistierter Ablauf beginnt. | `B-MAIN-PRE-01`, `B-MAIN-PRE-05`, `B-MAIN-G01` | `B-EFF-VIVIAN-GUIDING` |
| `CAP-B-VIVIAN-GUIDE-CUP` | `Capability` | `CAP-B-VIVIAN-GUIDE-CUP` | `TassenplatzierungAnleiten` | `ENT-B-01 VivianAssistant` | Vivian kann den Visitor zur notwendigen Platzierung der Tasse anleiten, ohne die Tassenplatzierung selbst als Systemhandlung zu modellieren. | `B-MAIN-G02` | `B-EFF-CUP-GUIDANCE-ISSUED` |
| `CAP-B-VIVIAN-GUIDE-PROGRAM` | `Capability` | `CAP-B-VIVIAN-GUIDE-PROGRAM` | `ProgrammauswahlAnleiten` | `ENT-B-01 VivianAssistant` | Vivian kann den Visitor zur Auswahl eines Kaffeeprogramms fuehren, nachdem die Tasse als vorhanden erkannt wurde. | `B-MAIN-G03` | `B-EFF-PROGRAM-GUIDANCE-ISSUED` |
| `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST` | `Capability` | `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST` | `BruehanforderungBestaetigen` | `ENT-B-01 VivianAssistant` | Vivian kann eine erkannte Bruehanforderung fachlich bestaetigen und fuer den weiteren Ablauf sichtbar machen. | `B-MAIN-G04`, `SA-B-BREWING-REQUESTED` | `B-EFF-BREWING-REQUEST-CONFIRMED` |
| `CAP-B-CHECK-MACHINE-READY` | `Capability` | `CAP-B-CHECK-MACHINE-READY` | `BedienbereitschaftPruefen` | `ENT-B-02 CoffeeMachine` | Die Kaffeemaschine kann fachlich pruefbar machen, ob Tasse, Wasser, Programmauswahl und Maschinenzustand einen assistierten Start erlauben. | `B-MAIN-G05` | `B-EFF-READINESS-RESULT-PRODUCED` |
| `CAP-B-VIVIAN-REQUEST-CONFIRMATION` | `Capability` | `CAP-B-VIVIAN-REQUEST-CONFIRMATION` | `StartbestaetigungAnfordern` | `ENT-B-01 VivianAssistant` | Vivian kann vor dem assistierten Start eine ausdrueckliche Bestaetigung des Visitors anfordern. | `B-MAIN-G06`, `SA-B-CM-START-PERMISSION` | `B-EFF-CONFIRMATION-REQUESTED` |
| `CAP-B-START-BREWING` | `Capability` | `CAP-B-START-BREWING` | `BruehvorgangFachlichStarten` | `ENT-B-02 CoffeeMachine` | Die Kaffeemaschine kann den Bruehvorgang fachlich starten, wenn Bereitschaft, Startfreigabe und Benutzerbestaetigung vorliegen. | `B-MAIN-G08` | `B-EFF-BREWING-START-ISSUED` |
| `CAP-B-VIVIAN-REPORT-COMPLETION` | `Capability` | `CAP-B-VIVIAN-REPORT-COMPLETION` | `AbschlussmeldungAusgeben` | `ENT-B-01 VivianAssistant` | Vivian kann dem Visitor den erfolgreichen Abschluss der Bedienung melden, sobald der Maschinenabschluss sichtbar ist. | `B-MAIN-G10`, `B-MAIN-G11` | `B-EFF-COMPLETION-REPORTED` |
| `CAP-B-VIVIAN-GUIDE-CUP-CORRECTION` | `Capability` | `CAP-B-VIVIAN-GUIDE-CUP-CORRECTION` | `TassenkorrekturAnleiten` | `ENT-B-01 VivianAssistant` | Vivian kann eine korrigierende Anleitung ausgeben, wenn die Tasse fehlt oder nicht erkannt wurde. | `B-ALT-G01` | `B-EFF-CUP-CORRECTION-GUIDANCE-ISSUED` |
| `CAP-B-VIVIAN-EXPLAIN-ERROR` | `Capability` | `CAP-B-VIVIAN-EXPLAIN-ERROR` | `FehlerursacheErklaeren` | `ENT-B-01 VivianAssistant` | Vivian kann erklaeren, weshalb der Bruehstart bei fehlender Bereitschaft nicht ausgefuehrt wird. | `B-EX-G01`, `SA-B-READINESS-FAILED`, `SA-B-CM-WATER-LOW` | `B-EFF-ERROR-EXPLAINED` |
| `CAP-B-VIVIAN-CLOSE-EXCEPTION` | `Capability` | `CAP-B-VIVIAN-CLOSE-EXCEPTION` | `AusnahmefallFachlichAbschliessen` | `ENT-B-01 VivianAssistant` | Vivian kann den Ausnahmefall fachlich abschliessen, sodass der Hauptpfad nicht fortgesetzt und kein erfolgreicher Bruehstart behauptet wird. | `B-EX-G02`, `SA-B-VIVIAN-ERROR-EXPLAINED` | `B-EFF-EXCEPTION-CLOSED` |

## Angelegte Effect-Instanzen

| Effect-ID | Metamodellklasse | `uuid` | Fachliche Wirkung | Bezug zu StateAssertions oder Conditions |
| --- | --- | --- | --- | --- |
| `B-EFF-VIVIAN-GUIDING` | `Effect` | `B-EFF-VIVIAN-GUIDING` | Vivian befindet sich im Fuehrungsmodus fuer die Kaffeemaschinenbedienung. | `SA-B-VIVIAN-GUIDING` |
| `B-EFF-CUP-GUIDANCE-ISSUED` | `Effect` | `B-EFF-CUP-GUIDANCE-ISSUED` | Vivian hat eine wahrnehmbare Anleitung zur Tassenplatzierung ausgegeben. | `SA-B-VIVIAN-GUIDANCE-CUP` |
| `B-EFF-PROGRAM-GUIDANCE-ISSUED` | `Effect` | `B-EFF-PROGRAM-GUIDANCE-ISSUED` | Vivian hat eine wahrnehmbare Anleitung zur Programmauswahl ausgegeben. | `SA-B-VIVIAN-GUIDANCE-PROGRAM` |
| `B-EFF-BREWING-REQUEST-CONFIRMED` | `Effect` | `B-EFF-BREWING-REQUEST-CONFIRMED` | Die Bruehanforderung ist durch Vivian fachlich bestaetigt. | `SA-B-VIVIAN-INTENT-CONFIRMED` |
| `B-EFF-READINESS-RESULT-PRODUCED` | `Effect` | `B-EFF-READINESS-RESULT-PRODUCED` | Die Bereitschaftspruefung erzeugt genau ein fachliches Ergebnis: bestanden mit Startfreigabe oder fehlgeschlagen mit blockiertem Start. | positiv: `B-MAIN-G06`, `SA-B-CM-READY`, `SA-B-CM-READY-FEEDBACK`, `SA-B-CM-START-PERMISSION`; negativ: `B-EX-G01`, `SA-B-READINESS-FAILED`, `SA-B-CM-NOT-READY`, `SA-B-CM-START-BLOCKED`, `SA-B-CM-SAFE` |
| `B-EFF-CONFIRMATION-REQUESTED` | `Effect` | `B-EFF-CONFIRMATION-REQUESTED` | Vivian wartet auf eine explizite Startbestaetigung des Visitors. | `SA-B-VIVIAN-AWAITING-CONFIRMATION` |
| `B-EFF-BREWING-START-ISSUED` | `Effect` | `B-EFF-BREWING-START-ISSUED` | Der Bruehstart ist fachlich ausgeloest und fuehrt in den beobachtbaren Bruehvorgang. | `SA-B-BREWING-START-ISSUED`, `SA-B-CM-BREWING` |
| `B-EFF-COMPLETION-REPORTED` | `Effect` | `B-EFF-COMPLETION-REPORTED` | Vivian hat den erfolgreichen Abschluss an den Visitor gemeldet. | `SA-B-VIVIAN-COMPLETION-REPORTED` |
| `B-EFF-CUP-CORRECTION-GUIDANCE-ISSUED` | `Effect` | `B-EFF-CUP-CORRECTION-GUIDANCE-ISSUED` | Vivian hat eine Korrekturanleitung fuer die fehlende oder falsch positionierte Tasse ausgegeben. | `SA-B-VIVIAN-CUP-CORRECTION-GUIDANCE` |
| `B-EFF-ERROR-EXPLAINED` | `Effect` | `B-EFF-ERROR-EXPLAINED` | Vivian hat die Fehlerursache der fehlgeschlagenen Bereitschaftspruefung erklaert. | `SA-B-VIVIAN-ERROR-EXPLAINED`, `B-EX-POST-04` |
| `B-EFF-EXCEPTION-CLOSED` | `Effect` | `B-EFF-EXCEPTION-CLOSED` | Der Ausnahmefall ist fachlich abgeschlossen; der Hauptpfad wird nicht fortgesetzt und der Bruehvorgang wird nicht als gestartet modelliert. | `SA-B-VIVIAN-EXCEPTION-CLOSED`, `B-EX-POST-02`, `B-EX-POST-03`, `B-EX-POST-05` |

## Rueckbindung an CapabilityUse

| CapabilityUse | Owner-Step | Referenzierte Capability | Konsistenzbewertung |
| --- | --- | --- | --- |
| `B-CU-001` | `B-MAIN-S02` | `CAP-B-VIVIAN-ENTER-GUIDANCE` | erfuellt: beschreibt den Wechsel in Vivians Fuehrungsmodus. |
| `B-CU-002` | `B-MAIN-S03` | `CAP-B-VIVIAN-GUIDE-CUP` | erfuellt: beschreibt die fachliche Anleitung zur Tassenplatzierung. |
| `B-CU-003` | `B-MAIN-S06` | `CAP-B-VIVIAN-GUIDE-PROGRAM` | erfuellt: beschreibt die fachliche Anleitung zur Programmauswahl. |
| `B-CU-004` | `B-MAIN-S10` | `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST` | erfuellt: beschreibt Vivians Bestaetigung der Bruehanforderung. |
| `B-CU-005` | `B-MAIN-S11` | `CAP-B-CHECK-MACHINE-READY` | erfuellt: beschreibt die fachliche Bereitschaftspruefung als Entscheidungsfaehigkeit. |
| `B-CU-006` | `B-MAIN-S13` | `CAP-B-VIVIAN-REQUEST-CONFIRMATION` | erfuellt: beschreibt Vivians explizite Startbestaetigungsanfrage. |
| `B-CU-007` | `B-MAIN-S15` | `CAP-B-START-BREWING` | erfuellt: beschreibt den fachlichen Bruehstart. |
| `B-CU-008` | `B-MAIN-S20` | `CAP-B-VIVIAN-REPORT-COMPLETION` | erfuellt: beschreibt die Abschlussmeldung. |
| `B-CU-009` | `B-ALT-S02` | `CAP-B-VIVIAN-GUIDE-CUP-CORRECTION` | erfuellt: beschreibt die Korrekturanleitung im Alternativpfad. |
| `B-CU-010` | `B-EX-S02` | `CAP-B-VIVIAN-EXPLAIN-ERROR` | erfuellt: beschreibt Vivians Fehlererklaerung im Exception-Pfad. |
| `B-CU-011` | `B-EX-S04` | `CAP-B-VIVIAN-CLOSE-EXCEPTION` | erfuellt: beschreibt den fachlichen Abschluss des Exception-Pfads. |

## Fachliche Preconditions je Capability

| Capability-ID | Preconditions | Fachliche Lesart |
| --- | --- | --- |
| `CAP-B-VIVIAN-ENTER-GUIDANCE` | `B-MAIN-PRE-01`, `B-MAIN-PRE-05`, `B-MAIN-G01` | Ein anwesender Visitor hat Hilfe angefordert und Vivian kann in den Fuehrungsmodus wechseln. |
| `CAP-B-VIVIAN-GUIDE-CUP` | `B-MAIN-G02` | Vivian ist bereits im Fuehrungsmodus. |
| `CAP-B-VIVIAN-GUIDE-PROGRAM` | `B-MAIN-G03` | Die Tasse ist vorhanden; die naechste fachliche Bedienhandlung ist die Programmauswahl. |
| `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST` | `B-MAIN-G04`, `SA-B-BREWING-REQUESTED` | Ein Programm ist gewaehlt und der Startwunsch ist als Bruehanforderung modelliert. |
| `CAP-B-CHECK-MACHINE-READY` | `B-MAIN-G05` | Eine nicht abgebrochene Bruehanforderung liegt vor. |
| `CAP-B-VIVIAN-REQUEST-CONFIRMATION` | `B-MAIN-G06`, `SA-B-CM-START-PERMISSION` | Die Bereitschaftspruefung ist bestanden und der Start ist fachlich erlaubt. |
| `CAP-B-START-BREWING` | `B-MAIN-G08` | Startbestaetigung, Startfreigabe und bestandene Bereitschaftspruefung liegen gemeinsam vor. |
| `CAP-B-VIVIAN-REPORT-COMPLETION` | `B-MAIN-G10`, `B-MAIN-G11` | Der Bruehvorgang ist abgeschlossen und das Maschinenfeedback ist sichtbar. |
| `CAP-B-VIVIAN-GUIDE-CUP-CORRECTION` | `B-ALT-G01` | Die Tasse fehlt oder wurde nicht erkannt. |
| `CAP-B-VIVIAN-EXPLAIN-ERROR` | `B-EX-G01`, `SA-B-READINESS-FAILED`, `SA-B-CM-WATER-LOW` | Die Bereitschaftspruefung ist fehlgeschlagen, exemplarisch wegen zu niedrigem Wasserstand. |
| `CAP-B-VIVIAN-CLOSE-EXCEPTION` | `B-EX-G02`, `SA-B-VIVIAN-ERROR-EXPLAINED` | Der Start ist blockiert und Vivian hat die Fehlerursache bereits erklaert. |

## Besonderheit der Bereitschaftspruefung

`CAP-B-CHECK-MACHINE-READY` ist keine technische Sensorabfrage im ScenarioStep. Die Capability beschreibt die fachliche Entscheidungsfaehigkeit, aus den relevanten Bedingungen ein Starturteil abzuleiten.

Deshalb hat `B-EFF-READINESS-RESULT-PRODUCED` zwei fachlich erlaubte Ausgaenge:

- bestanden: Der Hauptpfad darf ueber `B-MAIN-G06` zu Startfreigabe und Rueckfrage weiterlaufen.
- fehlgeschlagen: Der Exception-Pfad darf ueber `B-EX-G01` aktiviert werden und der Start bleibt blockiert.

So bleibt die Modellierung korrekt, obwohl `B-MAIN-S11` selbst noch keinen konkreten `resultingState` besitzt. Der beobachtbare positive Zustand erscheint in `B-MAIN-S12`; der beobachtbare negative Zustand erscheint in `B-EX-S01` und `B-EX-S03`.

## Keine technischen Daten in Capabilities

| Capability-ID | Fachlich sauber? | Begruendung |
| --- | --- | --- |
| `CAP-B-VIVIAN-ENTER-GUIDANCE` | ja | Beschreibt Moduswechsel und Assistenzzustand, keine konkrete Ausgabe-Engine. |
| `CAP-B-VIVIAN-GUIDE-CUP` | ja | Beschreibt Anleitung zur Tassenplatzierung, keine UI-, Voice- oder Avatar-Implementierung. |
| `CAP-B-VIVIAN-GUIDE-PROGRAM` | ja | Beschreibt Programmanleitung, keine Bedienpanel- oder Dialogtechnik. |
| `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST` | ja | Beschreibt fachliche Bestaetigung der Anforderung, keinen Kommunikationskanal. |
| `CAP-B-CHECK-MACHINE-READY` | ja | Beschreibt fachliche Startbereitschaft, keine Sensor- oder Controllerabfrage. |
| `CAP-B-VIVIAN-REQUEST-CONFIRMATION` | ja | Beschreibt die notwendige Benutzerfreigabe, keinen Dialogaufruf. |
| `CAP-B-START-BREWING` | ja | Beschreibt fachlichen Start unter Guards, keine Maschinen-API. |
| `CAP-B-VIVIAN-REPORT-COMPLETION` | ja | Beschreibt Abschlussmeldung, keinen Ausgabekanal. |
| `CAP-B-VIVIAN-GUIDE-CUP-CORRECTION` | ja | Beschreibt Korrekturanleitung, keine konkrete Trackingtechnik. |
| `CAP-B-VIVIAN-EXPLAIN-ERROR` | ja | Beschreibt Fehlererklaerung, keine Runtime-Fehlerbehandlung. |
| `CAP-B-VIVIAN-CLOSE-EXCEPTION` | ja | Beschreibt fachlichen Exception-Abschluss, keinen Abbruchbefehl. |

## Nicht vorweggenommen

| Elementgruppe | Status nach Task 8.9 | Folgetask |
| --- | --- | --- |
| `RuntimeBinding` | nicht angelegt | 8.10 |
| `RuntimeAction` | nicht angelegt | 8.11 |
| `ValidationCase` | nicht angelegt | 8.12 |
| Formale `Satisfy`-Instanzen | nicht angelegt | spaetere Konsolidierung nach B-Mapping |

## Abnahmekontrolle

| Kriterium aus Task 8.9 | Erfuellung |
| --- | --- |
| Capability-Instanzen vorhanden | Elf Capabilities sind angelegt. |
| Jede Capability hat fachlichen Intent | Jede Capability besitzt eine Intent-Beschreibung. |
| Jede Capability hat Preconditions | Jede Capability referenziert fachliche Conditions oder StateAssertions als Voraussetzungen. |
| Jede Capability hat Effect | Jede Capability referenziert genau mindestens einen angelegten promised Effect. |
| Jede CapabilityUse referenziert eine existierende Capability | `B-CU-001` bis `B-CU-011` sind rueckgebunden. |
| Keine Capability enthaelt technische Ausfuehrungsdaten | Keine Capability beschreibt Plattform-, Endpunkt-, Topic-, Tool- oder Controllerdetails. |
| Positive und negative Bereitschaft sind modelliert | `B-EFF-READINESS-RESULT-PRODUCED` deckt Hauptpfadfreigabe und Exception-Einstieg fachlich ab. |

## Konsequenz fuer Task 8.10

Task 8.10 kann nun technische `RuntimeBinding`-Instanzen fuer Vivian-, VR- und Toolchain-Ausfuehrung anlegen. Jede RuntimeBinding muss genau eine der hier definierten fachlichen Capabilities referenzieren und darf die Szenarioschritte nicht direkt umgehen.
