# Anwendungsfall B: Objektzustaende der Kaffeemaschine

Stand: 2026-07-07

Task: 6.6 `Objektzustaende der Kaffeemaschine sammeln`

## Zweck

Diese Datei sammelt pruefbare Zustaende der virtuellen Kaffeemaschine fuer Anwendungsfall B. Jeder Zustand ist so formuliert, dass er spaeter als `StateAssertion` abgebildet werden kann.

Baseline-Subjekt fuer alle Maschinenzustaende ist:

`subjectRef = ENT-B-02 CoffeeMachine`

## Abgrenzung

Die Zustandsliste beschreibt beobachtbare oder pruefbare fachliche Zustaende der Kaffeemaschine. Sie beschreibt noch keine vollstaendige Zustandsmaschine und keine erlaubten Transitionen. Erlaubte Uebergaenge, falls spaeter noetig, gehoeren in die Modellierbarkeitspruefung beziehungsweise in ein moegliches State-/Transition-Ergaenzungsmodell.

Nicht zur Kaffeemaschine selbst gezaehlt werden:

- `VivianAssistant.mode` oder `VivianAssistant.feedbackState`, weil Vivian ein eigener `Agent` ist,
- `Cup.state`, weil die Tasse eine eigene `Entity` sein kann,
- `BrewingRequest.state`, falls der Startwunsch spaeter als eigenes fachliches Objekt modelliert wird,
- technische Controller-, API- oder Runtime-Zustaende.

## Zustandsdimensionen

Die Kaffeemaschine besitzt fuer B mehrere orthogonale Zustandsdimensionen. Nicht alle Werte gehoeren in dasselbe eindimensionale `state`-Attribut:

| Dimension | Bedeutung |
| --- | --- |
| Betriebszustand | Grober Lebenszyklus der Maschine im Bedienablauf, z. B. `idle`, `ready`, `brewing`, `finished`, `error`. |
| Bereitschaftsmerkmale | Pruefbare Merkmale, die Startbereitschaft begruenden, z. B. Wasserstand, Tasse, Programmauswahl. |
| Bedienfeedback | Sichtbare oder hoerbare Rueckmeldungen der Maschine, z. B. Startfreigabe, Fortschritt, Fehlerhinweis. |
| Sicherer Zustand | Zustand, in dem kein unerlaubter oder unkontrollierter Bruehvorgang laeuft. |

## Zustandsliste als StateAssertion-Kandidaten

| ID | Zustandsdimension | Erwarteter Zustand | StateAssertion-Formulierung | Herkunft aus 6.5 | Bemerkung |
| --- | --- | --- | --- | --- | --- |
| B-CM-ST-001 | Betriebszustand | Maschine ist verfuegbar | `CoffeeMachine.availabilityState = available` | Vorbedingung fuer B-ACT-011/B-ACT-014 | Wird in 6.7 wahrscheinlich Condition. |
| B-CM-ST-002 | Betriebszustand | Maschine ist nicht verfuegbar | `CoffeeMachine.availabilityState = unavailable` | Fehlerkandidat aus B-ACT-012 | Kann Exception ausloesen. |
| B-CM-ST-003 | Betriebszustand | Maschine ist eingeschaltet | `CoffeeMachine.powerState = on` | Vorbedingung fuer Bedienung | Kein Hardwaredetail, nur fachlich pruefbarer Zustand. |
| B-CM-ST-004 | Betriebszustand | Maschine ist aus oder nicht aktivierbar | `CoffeeMachine.powerState = off` | Fehlerkandidat | Kann zu `notReady` fuehren. |
| B-CM-ST-005 | Betriebszustand | Maschine wartet auf Bedienung | `CoffeeMachine.lifecycleState = idle` | Startzustand vor Bedienung | Ausgangszustand fuer Main Scenario. |
| B-CM-ST-006 | Betriebszustand | Maschine ist bereit | `CoffeeMachine.lifecycleState = ready` | B-ACT-011/B-ACT-013 | Ergebnis positiver Bereitschaftspruefung. |
| B-CM-ST-007 | Betriebszustand | Maschine ist nicht bereit | `CoffeeMachine.lifecycleState = notReady` | B-ACT-012/B-ACT-007 | Sammelzustand fuer fehlende Preconditions. |
| B-CM-ST-008 | Betriebszustand | Maschine brueht | `CoffeeMachine.lifecycleState = brewing` | B-ACT-014 | Zentraler Erfolgseffekt des Startvorgangs. |
| B-CM-ST-009 | Betriebszustand | Bruehvorgang ist abgeschlossen | `CoffeeMachine.lifecycleState = finished` | B-ACT-016/B-ACT-008 | Zielzustand des Main Scenario. |
| B-CM-ST-010 | Betriebszustand | Maschine ist im Fehlerzustand | `CoffeeMachine.lifecycleState = error` | B-ACT-012 | Exception-Kandidat. |
| B-CM-ST-011 | Betriebszustand | Bedienvorgang wurde abgebrochen | `CoffeeMachine.lifecycleState = cancelled` | B-ACT-006 | Kontrollierter Alternativabschluss. |
| B-CM-ST-012 | Sicherer Zustand | Maschine ist sicher angehalten | `CoffeeMachine.safeState = true` | B-ACT-006 oder Fehlerabschluss | Wichtig fuer Abbruch- und Ausnahmefaelle. |
| B-CM-ST-013 | Bereitschaftsmerkmal | Wasserstand reicht aus | `CoffeeMachine.waterLevel = sufficient` | B-ACT-007/B-ACT-011 | Wird in 6.7 als Precondition relevant. |
| B-CM-ST-014 | Bereitschaftsmerkmal | Wasserstand ist zu niedrig | `CoffeeMachine.waterLevel = low` | B-ACT-012 | Fehler-/Korrekturanlass. |
| B-CM-ST-015 | Bereitschaftsmerkmal | Keine Tasse erkannt | `CoffeeMachine.cupPresent = false` | B-ACT-012 | Fehler-/Korrekturanlass. |
| B-CM-ST-016 | Bereitschaftsmerkmal | Tasse ist vorhanden | `CoffeeMachine.cupPresent = true` | B-ACT-002/B-ACT-007 | Kann aus separater `Cup`-Entity abgeleitet sein. |
| B-CM-ST-017 | Bereitschaftsmerkmal | Kein Programm gewaehlt | `CoffeeMachine.selectedProgram = none` | Vor B-ACT-003 | Start noch nicht vollstaendig vorbereitet. |
| B-CM-ST-018 | Bereitschaftsmerkmal | Kaffeeprogramm gewaehlt | `CoffeeMachine.selectedProgram = coffee` | B-ACT-003 | Beispielhafte Auswahl fuer den Main Path. |
| B-CM-ST-019 | Bereitschaftsmerkmal | Start ist erlaubt | `CoffeeMachine.startPermission = allowed` | B-ACT-013 | Ergebnis aus Preconditions und Bestaetigung. |
| B-CM-ST-020 | Bereitschaftsmerkmal | Start ist blockiert | `CoffeeMachine.startPermission = blocked` | B-ACT-012 | Exception- oder Alternativpfad. |
| B-CM-ST-021 | Bedienfeedback | Bereitschaftsrueckmeldung ist sichtbar | `CoffeeMachine.readyFeedback = visible` | B-ACT-013 | Rueckmeldung fuer Benutzer und ValidationCase. |
| B-CM-ST-022 | Bedienfeedback | Auswahlbestaetigung ist sichtbar | `CoffeeMachine.selectionFeedback = visible` | B-ACT-003 | Zeigt, dass Programmauswahl angenommen wurde. |
| B-CM-ST-023 | Bedienfeedback | Bruehfortschritt ist sichtbar | `CoffeeMachine.progressIndicator = visible` | B-ACT-014/B-ACT-015 | Beobachtbarer Effekt des Bruehstarts. |
| B-CM-ST-024 | Bedienfeedback | Fehlerrueckmeldung ist sichtbar | `CoffeeMachine.errorFeedback = visible` | B-ACT-012 | Ergaenzt Vivians Fehlererklaerung. |
| B-CM-ST-025 | Bedienfeedback | Abschlussrueckmeldung ist sichtbar | `CoffeeMachine.completionFeedback = visible` | B-ACT-016 | Beobachtbares Ende des Main Scenario. |

## Primaerer Betriebszustand versus orthogonale Merkmale

Fuer die spaetere Szenariomodellierung ist folgende Trennung wichtig:

| Gruppe | Beispiele | Modellierungsfolge |
| --- | --- | --- |
| Primaerer Betriebszustand | `idle`, `ready`, `notReady`, `brewing`, `finished`, `error`, `cancelled` | Diese Werte sollten sich fuer dieselbe Maschine gegenseitig ausschliessen. |
| Orthogonale Bereitschaftsmerkmale | `waterLevel`, `cupPresent`, `selectedProgram`, `startPermission` | Diese Merkmale koennen parallel zum Betriebszustand gelten und spaeter Preconditions/Guards bilden. |
| Orthogonales Feedback | `readyFeedback`, `progressIndicator`, `errorFeedback`, `completionFeedback` | Diese Merkmale machen Systemeffekte fuer Benutzer und ValidationCase beobachtbar. |

## Direkt verwendbare StateAssertion-Muster

| Muster | Beispiel |
| --- | --- |
| Main-Startzustand | `StateAssertion(id = SA-B-CM-IDLE, subjectRef = ENT-B-02 CoffeeMachine, expectedState = "lifecycleState = idle")` |
| Bereitschaft | `StateAssertion(id = SA-B-CM-READY, subjectRef = ENT-B-02 CoffeeMachine, expectedState = "lifecycleState = ready")` |
| Bruehstart | `StateAssertion(id = SA-B-CM-BREWING, subjectRef = ENT-B-02 CoffeeMachine, expectedState = "lifecycleState = brewing")` |
| Abschluss | `StateAssertion(id = SA-B-CM-FINISHED, subjectRef = ENT-B-02 CoffeeMachine, expectedState = "lifecycleState = finished")` |
| Fehler | `StateAssertion(id = SA-B-CM-ERROR, subjectRef = ENT-B-02 CoffeeMachine, expectedState = "lifecycleState = error")` |
| Tasse vorhanden | `StateAssertion(id = SA-B-CM-CUP-PRESENT, subjectRef = ENT-B-02 CoffeeMachine, expectedState = "cupPresent = true")` |
| Fortschritt sichtbar | `StateAssertion(id = SA-B-CM-PROGRESS-VISIBLE, subjectRef = ENT-B-02 CoffeeMachine, expectedState = "progressIndicator = visible")` |

## Zusammenhang mit Task 6.7

Einige der hier gesammelten Zustaende werden in Task 6.7 als Vorbedingungen oder Guards wiederverwendet:

| Zustand | Voraussichtliche Verwendung in 6.7 |
| --- | --- |
| `CoffeeMachine.availabilityState = available` | Precondition fuer jede Bedienung. |
| `CoffeeMachine.powerState = on` | Precondition fuer Bereitschaftspruefung. |
| `CoffeeMachine.waterLevel = sufficient` | Precondition fuer Bruehstart. |
| `CoffeeMachine.cupPresent = true` | Precondition fuer Bruehstart. |
| `CoffeeMachine.selectedProgram != none` | Precondition fuer Bruehstart. |
| `CoffeeMachine.startPermission = allowed` | Guard fuer assistierten Start. |
| `CoffeeMachine.lifecycleState != brewing` | Guard gegen doppelten Start. |

## Abnahmekontrolle

| Kriterium aus Task 6.6 | Erfuellung |
| --- | --- |
| Zustandsliste vorhanden | Die Tabelle enthaelt 25 Zustandskandidaten fuer die Kaffeemaschine. |
| Jeder Zustand kann als StateAssertion formuliert werden | Jede Zeile enthaelt eine konkrete `StateAssertion`-Formulierung fuer `CoffeeMachine`. |
| Objektzustand bleibt von technischer Ansteuerung getrennt | Keine Zeile verwendet Controller, API, Topic, Tool oder RuntimeAction als Zustand. |
| Bereitschaftsmerkmale sind nicht mit Betriebszustand vermischt | Primaerer Betriebszustand, Bereitschaftsmerkmale und Feedback sind getrennt. |
| Anschluss an Task 6.7 vorbereitet | Relevante Zustaende fuer Preconditions und Guards sind explizit markiert. |

## Konsequenz fuer Task 6.7

Task 6.7 kann nun aus den Zustandskandidaten pruefbare Vorbedingungen ableiten, insbesondere Verfuegbarkeit, Wasserstand, Tasse, Programmauswahl, Startfreigabe und Nicht-Doppelstart.
