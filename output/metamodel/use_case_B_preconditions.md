# Anwendungsfall B: Vorbedingungen und Guards fuer die Bedienung

Stand: 2026-07-07

Task: 6.7 `Vorbedingungen fuer Bedienung sammeln`

## Zweck

Diese Datei sammelt pruefbare Conditions fuer die assistierte Bedienung der virtuellen Kaffeemaschine. Die Conditions entstehen aus den Bedienhandlungen aus Task 6.5 und den Objektzustaenden aus Task 6.6.

Die Liste beschreibt noch keine endgueltigen ScenarioSteps. Sie bereitet aber vor, welche Bedingungen spaeter auf `Scenario.precondition`, `ScenarioStep.guard`, `StepRelation.guard` oder `Capability.precondition` liegen koennen.

## Modellierungsprinzip

| Ebene | Verwendung | Beispiel |
| --- | --- | --- |
| Scenario-Precondition | Muss vor dem betrachteten Bedienablauf gelten. | Maschine ist verfuegbar. |
| Step-Guard | Entscheidet, ob ein konkreter Schritt oder eine Verzweigung ausgefuehrt werden darf. | Start ist erlaubt. |
| Capability-Precondition | Muss gelten, damit eine fachliche Capability sinnvoll nutzbar ist. | Bruehvorgang starten erfordert Wasser, Tasse und Programmauswahl. |

Jede Bedingung ist als pruefbarer Ausdruck formuliert. Pruefbar heisst: Der Ausdruck kann spaeter entweder als `Condition.expression` gelesen, gegen `StateAssertion`-Kandidaten abgeglichen oder in einem `ValidationCase` erwartet werden.

## Condition-Katalog

| ID | Condition.kind | Ausdruck | Pruefbasis | Verwendung | Bei Nichterfuellung |
| --- | --- | --- | --- | --- | --- |
| B-COND-001 | pre | `CoffeeMachine.availabilityState = available` | `B-CM-ST-001` | Allgemeine Scenario-Precondition fuer assistierte Bedienung | Bedienung nicht starten; Fehlerfall Maschine nicht verfuegbar |
| B-COND-002 | pre | `CoffeeMachine.powerState = on` | `B-CM-ST-003` | Scenario-Precondition oder Capability-Precondition fuer Bereitschaftspruefung | Vivian erklaert, dass Maschine nicht eingeschaltet oder nicht aktivierbar ist |
| B-COND-003 | pre | `CoffeeMachine.lifecycleState in {idle, ready, notReady}` | `B-CM-ST-005`, `B-CM-ST-006`, `B-CM-ST-007` | Bedienung darf nur beginnen, wenn kein laufender oder abgeschlossener Bruehvorgang aktiv ist | Guard gegen Start waehrend `brewing`, `finished`, `error` oder `cancelled` |
| B-COND-004 | pre | `VivianAssistant.mode can become guiding` | `ENT-B-01 VivianAssistant` | Voraussetzung fuer assistierte Bedienung | Ohne Assistenzmodus kann nur unassistierte Objektbedienung modelliert werden |
| B-COND-005 | guard | `helpRequested = true` | Event aus `B-ACT-001` | Einstieg in assistierte Bedienung mit Vivian | Ohne Hilfewunsch kann normaler Bedienpfad ohne Vivian-Hilfe laufen |
| B-COND-006 | guard | `CoffeeMachine.cupPresent = true` | `B-CM-ST-016` | Guard fuer Bruehstart und positive Bereitschaftspruefung | Alternative: Benutzer platziert Tasse; Exception bei Abbruch |
| B-COND-007 | guard | `CoffeeMachine.waterLevel = sufficient` | `B-CM-ST-013` | Guard fuer Bruehstart und positive Bereitschaftspruefung | Vivian erklaert fehlendes Wasser; Korrekturpfad |
| B-COND-008 | guard | `CoffeeMachine.selectedProgram != none` | `B-CM-ST-018` oder nicht `B-CM-ST-017` | Guard fuer Startfreigabe | Benutzer muss Programm auswaehlen |
| B-COND-009 | guard | `CoffeeMachine.startPermission = allowed` | `B-CM-ST-019` | Guard fuer assistierten Start durch Vivian/System | Start bleibt blockiert; Fehler-/Korrekturhinweis |
| B-COND-010 | guard | `BrewingRequest.state = requested` | Effekt aus `B-ACT-004` | Voraussetzung, dass Bereitschaftspruefung fachlich ausgeloest wird | Kein Startpfad; Benutzer hat noch keine Startabsicht geaeussert |
| B-COND-011 | guard | `BrewingRequest.confirmed = true` | Effekt aus `B-ACT-005` | Guard fuer assistiertes Starten nach Vivians Rueckfrage | Alternative: warten oder abbrechen |
| B-COND-012 | guard | `BrewingRequest.state != cancelled` | Effekt aus `B-ACT-006` | Guard fuer Fortsetzung des Hauptpfads | Kontrollierter Abbruchpfad |
| B-COND-013 | guard | `CoffeeMachine.lifecycleState != brewing` | nicht `B-CM-ST-008` | Guard gegen doppelten Bruehstart | Vivian meldet, dass bereits ein Vorgang laeuft |
| B-COND-014 | guard | `CoffeeMachine.lifecycleState != error` | nicht `B-CM-ST-010` | Guard fuer normale Bedienung | Exception: Fehler erklaeren und sicheren Zustand herstellen |
| B-COND-015 | guard | `CoffeeMachine.safeState = true or CoffeeMachine.lifecycleState in {idle, ready, notReady}` | `B-CM-ST-012`, `B-CM-ST-005`, `B-CM-ST-006`, `B-CM-ST-007` | Guard fuer kontrollierten Start oder kontrollierten Abbruch | Kein Start, bis sicherer Zustand bestaetigt ist |
| B-COND-016 | pre | `Cup.state = placed or CoffeeMachine.cupPresent = true` | `B-ACT-002`, `B-CM-ST-016` | Alternative Form der Tassenbedingung, falls `Cup` als eigene Entity modelliert wird | Benutzer muss Tasse platzieren |
| B-COND-017 | guard | `ReadinessCheck.result = passed` | Ergebnis aus `B-ACT-011` | Guard fuer B-ACT-013 Startfreigabe | Vivian erklaert fehlende Voraussetzung |
| B-COND-018 | guard | `ReadinessCheck.result = failed` | Ergebnis aus `B-ACT-011` | Guard fuer B-ACT-012 Fehlererklaerung | Kein Fehlerpfad; Rueckkehr zur Startfreigabe moeglich |
| B-COND-019 | pre | `Visitor is present and able to interact` | Actor-Kontext `ACT-B-01 Visitor` | Scenario-Precondition fuer Bedienablauf | Bedienung kann nicht sinnvoll gestartet werden |
| B-COND-020 | guard | `UserAcknowledgement.state != received` | nicht Effekt aus `B-ACT-008` | Guard, damit Abschlussquittierung nicht doppelt erfolgt | Kein weiterer Quittierungsschritt noetig |

## Mindestbedingungen fuer den Main Path

Fuer einen erfolgreichen Hauptpfad sind mindestens folgende Bedingungen notwendig:

| Zweck | Conditions |
| --- | --- |
| Bedienung kann beginnen | `B-COND-001`, `B-COND-002`, `B-COND-003`, `B-COND-019` |
| Assistierte Bedienung mit Vivian kann beginnen | `B-COND-004`, `B-COND-005` |
| Bruehstart kann fachlich freigegeben werden | `B-COND-006`, `B-COND-007`, `B-COND-008`, `B-COND-010`, `B-COND-013`, `B-COND-014` |
| Vivian/System darf assistiert starten | `B-COND-009`, `B-COND-011`, `B-COND-012`, `B-COND-017` |
| Abschluss kann quittiert werden | `CoffeeMachine.lifecycleState = finished` und `B-COND-020` |

## Capability-Preconditions

| Capability-Kandidat | Preconditions | Begruendung |
| --- | --- | --- |
| `CAP-B-VIVIAN-GUIDE-USER` | `B-COND-004`, optional `B-COND-005` | Vivian kann nur fuehren, wenn Assistenzmodus fachlich verfuegbar ist und Hilfe gewuenscht oder vorgesehen ist. |
| `CAP-B-CHECK-MACHINE-READY` | `B-COND-001`, `B-COND-002`, `B-COND-010` | Bereitschaftspruefung setzt verfuegbare, eingeschaltete Maschine und Startabsicht voraus. |
| `CAP-B-VIVIAN-CONFIRM-ACTION` | `B-COND-010` | Vivian bestaetigt eine erkannte oder angeforderte Bedienabsicht. |
| `CAP-B-START-BREWING` | `B-COND-006`, `B-COND-007`, `B-COND-008`, `B-COND-009`, `B-COND-011`, `B-COND-012`, `B-COND-013`, `B-COND-014` | Der Bruehstart darf nur erfolgen, wenn alle fachlichen Startbedingungen erfuellt sind. |
| `CAP-B-VIVIAN-EXPLAIN-ERROR` | `B-COND-018` oder Negation einer Startbedingung | Fehlererklaerung wird benoetigt, wenn die Bereitschaftspruefung fehlschlaegt. |

## Entscheidungslogik fuer spaetere Verzweigungen

| Situation | Bedingung | Voraussichtlicher Pfad |
| --- | --- | --- |
| Alle Startbedingungen erfuellt | `B-COND-006 and B-COND-007 and B-COND-008 and B-COND-017` | Hauptpfad: Startfreigabe und Bruehstart |
| Tasse fehlt | `CoffeeMachine.cupPresent = false` | Alternative: Tasse platzieren, dann Rueckkehr zur Bereitschaftspruefung |
| Wasser reicht nicht | `CoffeeMachine.waterLevel = low` | Exception oder Korrekturpfad: Wasserbedingung erfuellen oder Abbruch |
| Kein Programm gewaehlt | `CoffeeMachine.selectedProgram = none` | Alternative: Programm auswaehlen |
| Benutzer bricht ab | `BrewingRequest.state = cancelled` | Kontrollierter Alternativabschluss |
| Maschine ist im Fehlerzustand | `CoffeeMachine.lifecycleState = error` | Exception: Fehler erklaeren und sicheren Zustand herstellen |

## Abnahmekontrolle

| Kriterium aus Task 6.7 | Erfuellung |
| --- | --- |
| Conditions vorhanden | Der Condition-Katalog enthaelt 20 Bedingungen. |
| Beispiele Verfuegbarkeit, Wasserstand, Tasse vorhanden | `B-COND-001`, `B-COND-007` und `B-COND-006` decken diese Beispiele ab. |
| Jede Bedingung ist pruefbar | Jede Zeile enthaelt einen konkreten Ausdruck und eine Pruefbasis. |
| Vorbedingungen und Guards getrennt | `Condition.kind` unterscheidet `pre` und `guard`. |
| Anschluss an Capabilities vorbereitet | Abschnitt `Capability-Preconditions` ordnet Conditions fachlichen Capabilities zu. |
| Keine technische Direktkopplung | Keine Condition verwendet Controller-, API-, Tool- oder Topic-Aufrufe. |

## Konsequenz fuer Task 6.8

Task 6.8 kann nun Fehler- und Ausnahmefaelle aus negierten oder fehlgeschlagenen Conditions ableiten, insbesondere Maschine nicht verfuegbar, Wasserstand niedrig, Tasse fehlt, keine Programmauswahl, doppelter Start, Benutzerabbruch und Maschinenfehler.
