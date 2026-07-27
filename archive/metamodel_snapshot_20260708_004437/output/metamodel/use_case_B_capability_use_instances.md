# Anwendungsfall B: CapabilityUse-Instanzen

Arbeitsstand fuer Task 8.8 der schrittweisen Beispielszenarien-Ausarbeitung.

## Modellierungsregel

`CapabilityUse` beschreibt die fachliche Faehigkeit, die ein systemischer `ScenarioStep` benoetigt. Die Instanz liegt zwischen Szenarioebene und technischer Ausfuehrung:

```text
ScenarioStep 1 -- 0..* CapabilityUse
CapabilityUse * -- 1 Capability
Capability 1 -- 0..* RuntimeBinding
RuntimeBinding 1 -- 1..* RuntimeAction
```

Damit gilt fuer diesen Task:

- Jeder systemische Schritt vom Typ `systemResponse` erhaelt mindestens eine `CapabilityUse`-Instanz.
- Ein `CapabilityUse` referenziert genau eine geplante fachliche `Capability`.
- Die referenzierte `Capability` wird in Task 8.9 formal mit Intent, Preconditions und Effect beschrieben.
- RuntimeBindings und RuntimeActions werden erst in Task 8.10 und 8.11 angelegt.
- Actor-Intents und Environment-Observations erhalten keine `CapabilityUse`, weil sie externe Handlungen beziehungsweise beobachtete Zustaende modellieren.

## Angelegte CapabilityUse-Instanzen

| CapabilityUse-ID | Owner-Scenario | Owner-Step | Step-Art | Referenzierte geplante Capability | Fachliche Parameter | Zweck im Szenario |
|---|---|---|---|---|---|---|
| `B-CU-001` | `SC-B-01-MAIN` | `B-MAIN-S02` | `systemResponse` | `CAP-B-VIVIAN-ENTER-GUIDANCE` | `agent=ENT-B-01 VivianAssistant`; `mode=guiding`; `targetObject=ENT-B-02 CoffeeMachine` | Vivian wechselt fachlich in den Fuehrungsmodus fuer die Kaffeemaschinenbedienung. |
| `B-CU-002` | `SC-B-01-MAIN` | `B-MAIN-S03` | `systemResponse` | `CAP-B-VIVIAN-GUIDE-CUP` | `agent=ENT-B-01 VivianAssistant`; `visitor=ACT-B-01 Visitor`; `targetObject=ENT-B-02 CoffeeMachine`; `contextObject=ENT-B-03 Cup` | Vivian leitet den Visitor zur korrekten Platzierung der Tasse an. |
| `B-CU-003` | `SC-B-01-MAIN` | `B-MAIN-S06` | `systemResponse` | `CAP-B-VIVIAN-GUIDE-PROGRAM` | `agent=ENT-B-01 VivianAssistant`; `visitor=ACT-B-01 Visitor`; `targetObject=ENT-B-02 CoffeeMachine`; `program=coffee` | Vivian unterstuetzt die Auswahl des Kaffeeprogramms. |
| `B-CU-004` | `SC-B-01-MAIN` | `B-MAIN-S10` | `systemResponse` | `CAP-B-VIVIAN-CONFIRM-BREWING-REQUEST` | `agent=ENT-B-01 VivianAssistant`; `request=ENT-B-04 BrewingRequest` | Vivian bestaetigt die fachlich erkannte Bruehanforderung. |
| `B-CU-005` | `SC-B-01-MAIN` | `B-MAIN-S11` | `systemResponse` | `CAP-B-CHECK-MACHINE-READY` | `targetObject=ENT-B-02 CoffeeMachine`; `request=ENT-B-04 BrewingRequest`; `requiredCup=ENT-B-03 Cup` | Das System prueft, ob die Kaffeemaschine fuer den gewuenschten Bruehstart bereit ist. |
| `B-CU-006` | `SC-B-01-MAIN` | `B-MAIN-S13` | `systemResponse` | `CAP-B-VIVIAN-REQUEST-CONFIRMATION` | `agent=ENT-B-01 VivianAssistant`; `visitor=ACT-B-01 Visitor`; `request=ENT-B-04 BrewingRequest` | Vivian fordert vor dem Start eine explizite Bestaetigung durch den Visitor an. |
| `B-CU-007` | `SC-B-01-MAIN` | `B-MAIN-S15` | `systemResponse` | `CAP-B-START-BREWING` | `targetObject=ENT-B-02 CoffeeMachine`; `request=ENT-B-04 BrewingRequest`; `program=coffee` | Das System loest den Bruehstart auf fachlicher Ebene aus. |
| `B-CU-008` | `SC-B-01-MAIN` | `B-MAIN-S20` | `systemResponse` | `CAP-B-VIVIAN-REPORT-COMPLETION` | `agent=ENT-B-01 VivianAssistant`; `targetObject=ENT-B-02 CoffeeMachine`; `result=finished` | Vivian meldet dem Visitor den erfolgreichen Abschluss der Bedienung. |
| `B-CU-009` | `SC-B-01-ALT01` | `B-ALT-S02` | `systemResponse` | `CAP-B-VIVIAN-GUIDE-CUP-CORRECTION` | `agent=ENT-B-01 VivianAssistant`; `visitor=ACT-B-01 Visitor`; `targetObject=ENT-B-02 CoffeeMachine`; `contextObject=ENT-B-03 Cup` | Vivian leitet die Korrektur einer falsch oder unvollstaendig platzierten Tasse an. |
| `B-CU-010` | `SC-B-01-EX01` | `B-EX-S02` | `systemResponse` | `CAP-B-VIVIAN-EXPLAIN-ERROR` | `agent=ENT-B-01 VivianAssistant`; `targetObject=ENT-B-02 CoffeeMachine`; `reason=waterLevelLow` | Vivian erklaert den Grund, weshalb der Bruehstart nicht ausgefuehrt wird. |
| `B-CU-011` | `SC-B-01-EX01` | `B-EX-S04` | `systemResponse` | `CAP-B-VIVIAN-CLOSE-EXCEPTION` | `agent=ENT-B-01 VivianAssistant`; `request=ENT-B-04 BrewingRequest`; `outcome=brewingNotStarted` | Vivian schliesst den Ausnahmefall fachlich ab, ohne den Hauptpfad fortzusetzen. |

## Abdeckung der ScenarioSteps

| ScenarioStep | Step-Art | CapabilityUse? | Begruendung |
|---|---|---|---|
| `B-MAIN-S01` | `actorIntent` | nein | Der Visitor aeussert eine Absicht; die Systemreaktion beginnt im Folgeschritt. |
| `B-MAIN-S02` | `systemResponse` | ja, `B-CU-001` | Systemischer Fuehrungsmodus wird benoetigt. |
| `B-MAIN-S03` | `systemResponse` | ja, `B-CU-002` | Vivian erzeugt eine fachliche Anleitung. |
| `B-MAIN-S04` | `actorIntent` | nein | Der Visitor handelt extern am Interaktionsobjekt. |
| `B-MAIN-S05` | `environmentObservation` | nein | Die Platzierung der Tasse wird als Event und StateAssertion modelliert. |
| `B-MAIN-S06` | `systemResponse` | ja, `B-CU-003` | Vivian erzeugt die naechste fachliche Anleitung. |
| `B-MAIN-S07` | `actorIntent` | nein | Der Visitor bedient die Auswahl. |
| `B-MAIN-S08` | `environmentObservation` | nein | Die Programmauswahl wird als beobachteter Zustand modelliert. |
| `B-MAIN-S09` | `actorIntent` | nein | Der Visitor aeussert den Startwunsch. |
| `B-MAIN-S10` | `systemResponse` | ja, `B-CU-004` | Vivian bestaetigt die erkannte Anforderung. |
| `B-MAIN-S11` | `systemResponse` | ja, `B-CU-005` | Die Maschine muss fachlich auf Startbereitschaft geprueft werden. |
| `B-MAIN-S12` | `environmentObservation` | nein | Die Startbereitschaft ist ein beobachteter Zustand. |
| `B-MAIN-S13` | `systemResponse` | ja, `B-CU-006` | Eine explizite Freigabe durch den Visitor wird angefordert. |
| `B-MAIN-S14` | `actorIntent` | nein | Der Visitor bestaetigt extern. |
| `B-MAIN-S15` | `systemResponse` | ja, `B-CU-007` | Der Bruehvorgang wird fachlich gestartet. |
| `B-MAIN-S16` | `environmentObservation` | nein | Der laufende Bruehvorgang ist ein beobachteter Zustand. |
| `B-MAIN-S17` | `environmentObservation` | nein | Der Fortschritt wird als Zustand der Maschine modelliert. |
| `B-MAIN-S18` | `environmentObservation` | nein | Die Ausgabe in die Tasse ist ein beobachteter physischer Zustand. |
| `B-MAIN-S19` | `environmentObservation` | nein | Das Ende des Bruehvorgangs ist ein beobachteter Zustand. |
| `B-MAIN-S20` | `systemResponse` | ja, `B-CU-008` | Vivian meldet den Abschluss an den Visitor. |
| `B-ALT-S01` | `environmentObservation` | nein | Die fehlerhafte Tassenlage ist ein beobachteter Zustand. |
| `B-ALT-S02` | `systemResponse` | ja, `B-CU-009` | Vivian erzeugt eine Korrekturanleitung. |
| `B-ALT-S03` | `actorIntent` | nein | Der Visitor korrigiert die Tasse. |
| `B-ALT-S04` | `environmentObservation` | nein | Die korrigierte Tassenlage ist ein beobachteter Zustand. |
| `B-EX-S01` | `environmentObservation` | nein | Die fehlende Bedienbereitschaft ist ein beobachteter Zustand. |
| `B-EX-S02` | `systemResponse` | ja, `B-CU-010` | Vivian erklaert die Fehlerursache. |
| `B-EX-S03` | `environmentObservation` | nein | Der nicht gestartete Bruehvorgang ist ein beobachteter Zustand. |
| `B-EX-S04` | `systemResponse` | ja, `B-CU-011` | Vivian beendet den Ausnahmefall fachlich. |

## Abgrenzung zur Runtime-Ebene

Diese Datei legt keine direkte `RuntimeAction` vom `ScenarioStep` aus an. Auch technische Begriffe wie API-Endpunkt, Message Topic, Controller-Methode oder Toolaufruf gehoeren nicht in die `CapabilityUse`-Instanz. Solche Details werden spaeter unter `RuntimeBinding` und `RuntimeAction` modelliert.

Dadurch bleibt die Szenariobeschreibung stabil, selbst wenn sich die konkrete Vivian-, VR- oder Toolchain-Implementierung aendert.

## Abnahmekontrolle

| Kriterium | Ergebnis |
|---|---|
| Alle systemischen Schritte aus Task 8.6 sind abgedeckt. | Erfuellt: 11 von 11 `systemResponse`-Schritten haben eine `CapabilityUse`. |
| Keine direkte RuntimeAction vom Schritt aus. | Erfuellt: `ScenarioStep` referenziert nur `CapabilityUse`; technische Aktionen folgen erst ab Task 8.10. |
| Jede `CapabilityUse` referenziert genau eine geplante `Capability`. | Erfuellt: jede Zeile der Instanzentabelle enthaelt genau eine Capability-ID. |
| Actor- und Umwelt-Schritte werden nicht kuenstlich als Systemfaehigkeit modelliert. | Erfuellt: Actor-Intents und Environment-Observations bleiben ueber Actor, Event, Condition und StateAssertion abgebildet. |

## Naechster Schritt

Task 8.9 formalisiert die elf referenzierten `Capability`-Instanzen mit Intent, Preconditions und Effect. Erst danach koennen RuntimeBindings konsistent auf diese fachlichen Faehigkeiten verweisen.
