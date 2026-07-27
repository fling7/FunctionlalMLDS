# Anwendungsfall B: Events des Hauptszenarios

Stand: 2026-07-07

Task: 7.4 `Events fuer B bestimmen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Quelle:

- `use_case_B_main_scenario_steps.md`
- `use_case_B_step_kinds.md`
- `use_case_B_interaction_actions.md`
- `use_case_B_coffee_machine_states.md`
- `use_case_B_preconditions.md`

## Modellierungsregel

`ScenarioStep -> Event` ist im Metamodell eine Assoziation mit `triggeredBy [0..*]`. Ein Schritt kann also kein, ein oder mehrere ausloesende Events referenzieren.

Fuer Anwendungsfall B werden Events nur dann angelegt, wenn sie eine fachlich beobachtbare Ausloesung beschreiben:

- `user`: Eingabe oder Bedienhandlung des externen Actors `ACT-B-01 Visitor`.
- `signal`: fachliches Signal von Vivian oder System, zum Beispiel ein Assistenzmodus, eine Rueckfrage oder ein Startsignal.
- `environment`: beobachtbarer Objektzustandswechsel oder sichtbares Feedback der Kaffeemaschine.

Nicht verwendet werden im Hauptpfad:

- `spatial`, weil die Kaffeemaschinenbedienung hier nicht durch eine Raumzone oder Position ausgeloest wird.
- `temporal`, weil der erfolgreiche Hauptpfad keine zeitgesteuerte Ausloesung benoetigt.

Technische Controller-Aufrufe, APIs, Topics oder Tools werden nicht als Event formuliert. Sie gehoeren spaeter ausschliesslich unter `RuntimeBinding -> RuntimeAction`.

## Event-Katalog

| Event-ID | Metamodellklasse | `uuid` | `shortName` | `Event.kind` | `Event.expression` | Kategorie | Begruendung |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `B-E01` | `Event` | `B-E01` | `AssistenzAngefordert` | `user` | `requestedAssistance(Visitor, CoffeeMachine)` | Benutzereingabe | Startet die assistierte Bedienung fachlich. |
| `B-E02` | `Event` | `B-E02` | `VivianFuehrungsmodusAktiv` | `signal` | `modeChanged(VivianAssistant, guiding)` | System-/Vivian-Signal | Zeigt, dass Vivian in den fachlichen Fuehrungsmodus gewechselt ist. |
| `B-E03` | `Event` | `B-E03` | `TassePlatziert` | `user` | `placed(Visitor, Cup, CoffeeMachine.cupArea)` | Benutzereingabe | Beschreibt die externe Bedienhandlung des Tassenplatzierens. |
| `B-E04` | `Event` | `B-E04` | `TasseErkannt` | `environment` | `stateChanged(CoffeeMachine.cupPresent, true)` | Objektzustandswechsel | Macht die erfolgreiche Tassenerkennung als Objektzustand beobachtbar. |
| `B-E05` | `Event` | `B-E05` | `ProgrammGewaehlt` | `user` | `selectedProgram(Visitor, CoffeeMachine, coffee)` | Benutzereingabe | Beschreibt die Programmauswahl durch den Visitor. |
| `B-E06` | `Event` | `B-E06` | `ProgrammauswahlBestaetigt` | `environment` | `stateChanged(CoffeeMachine.selectedProgram, coffee)` | Objektzustandswechsel | Beschreibt die angenommene Programmauswahl der Kaffeemaschine. |
| `B-E07` | `Event` | `B-E07` | `StarttasteBetaetigt` | `user` | `pressed(Visitor, CoffeeMachine.startButton)` | Benutzereingabe | Beschreibt den fachlichen Startwunsch des Visitors. |
| `B-E08` | `Event` | `B-E08` | `BruehanforderungErkannt` | `signal` | `recognized(BrewingRequest.state, requested)` | System-/Vivian-Signal | Vivian/System hat die Startanforderung fachlich erkannt. |
| `B-E09` | `Event` | `B-E09` | `StartbereitschaftGemeldet` | `environment` | `stateChanged(CoffeeMachine.lifecycleState, ready) and shown(CoffeeMachine.readyFeedback)` | Objektzustandswechsel | Die Maschine meldet pruefbar, dass der Start zulaessig ist. |
| `B-E10` | `Event` | `B-E10` | `StartbestaetigungAngefordert` | `signal` | `confirmationRequested(VivianAssistant, BrewingRequest)` | System-/Vivian-Signal | Vivian fordert die ausdrueckliche Benutzerfreigabe an. |
| `B-E11` | `Event` | `B-E11` | `AssistierterStartBestaetigt` | `user` | `confirmed(Visitor, BrewingRequest)` | Benutzereingabe | Der Visitor autorisiert den assistierten Bruehstart. |
| `B-E12` | `Event` | `B-E12` | `FachlichesStartsignalAusgegeben` | `signal` | `startSignalEmitted(System, CoffeeMachine)` | System-/Vivian-Signal | Das System loest den Bruehstart fachlich aus, ohne technische Runtime zu nennen. |
| `B-E13` | `Event` | `B-E13` | `BruehvorgangLaeuft` | `environment` | `stateChanged(CoffeeMachine.lifecycleState, brewing)` | Objektzustandswechsel | Die Maschine wechselt in den beobachtbaren Bruehzustand. |
| `B-E14` | `Event` | `B-E14` | `BruehfortschrittSichtbar` | `environment` | `shown(CoffeeMachine.progressIndicator)` | Objektfeedback | Der Bruehfortschritt ist fuer Benutzer oder ValidationCase beobachtbar. |
| `B-E15` | `Event` | `B-E15` | `BruehvorgangAbgeschlossen` | `environment` | `stateChanged(CoffeeMachine.lifecycleState, finished)` | Objektzustandswechsel | Die Maschine erreicht den fachlichen Abschlusszustand. |
| `B-E16` | `Event` | `B-E16` | `AbschlussrueckmeldungSichtbar` | `environment` | `shown(CoffeeMachine.completionFeedback)` | Objektfeedback | Die Abschlussrueckmeldung der Maschine ist beobachtbar. |
| `B-E17` | `Event` | `B-E17` | `VivianAbschlussGemeldet` | `signal` | `reported(VivianAssistant, completion)` | System-/Vivian-Signal | Vivian meldet den erfolgreichen Abschluss fachlich an den Visitor. |

## Eventzuordnung pro ScenarioStep

| Nr. | ScenarioStep | ScenarioStep.kind | Direkte Events fuer `triggeredBy` | Event-Art(en) | Begruendung |
| ---: | --- | --- | --- | --- | --- |
| 1 | `B-MAIN-S01` | `actorIntent` | `B-E01` | `user` | Der Use Case startet durch den Hilfewunsch des Visitors. |
| 2 | `B-MAIN-S02` | `systemResponse` | `B-E01` | `user` | Vivian wechselt als direkte Systemreaktion auf den Hilfewunsch in den Fuehrungsmodus. |
| 3 | `B-MAIN-S03` | `systemResponse` | `B-E02` | `signal` | Der aktive Fuehrungsmodus erlaubt den ersten Bedienhinweis zur Tasse. |
| 4 | `B-MAIN-S04` | `actorIntent` | `B-E03` | `user` | Das Platzieren der Tasse ist eine externe Benutzerhandlung. |
| 5 | `B-MAIN-S05` | `environmentObservation` | `B-E04` | `environment` | Die Tassenerkennung wird als beobachtbarer Maschinenzustand modelliert. |
| 6 | `B-MAIN-S06` | `systemResponse` | `B-E04` | `environment` | Nach erkannter Tasse kann Vivian auf die Programmauswahl fuehren. |
| 7 | `B-MAIN-S07` | `actorIntent` | `B-E05` | `user` | Die Programmauswahl ist eine Benutzerentscheidung. |
| 8 | `B-MAIN-S08` | `environmentObservation` | `B-E06` | `environment` | Die Kaffeemaschine bestaetigt die angenommene Auswahl als Objektzustand. |
| 9 | `B-MAIN-S09` | `actorIntent` | `B-E07` | `user` | Der Visitor aeussert den Bruehstart fachlich ueber die Starttaste. |
| 10 | `B-MAIN-S10` | `systemResponse` | `B-E07` | `user` | Vivian bestaetigt die erkannte Bruehanforderung als Reaktion auf den Startwunsch. |
| 11 | `B-MAIN-S11` | `systemResponse` | `B-E08` | `signal` | Die erkannte Bruehanforderung loest die fachliche Bereitschaftspruefung aus. |
| 12 | `B-MAIN-S12` | `environmentObservation` | `B-E09` | `environment` | Die Startbereitschaft ist ein pruefbarer Maschinenzustand mit Feedback. |
| 13 | `B-MAIN-S13` | `systemResponse` | `B-E09` | `environment` | Nach positiver Startbereitschaft fordert Vivian die explizite Freigabe an. |
| 14 | `B-MAIN-S14` | `actorIntent` | `B-E10`, `B-E11` | `signal`, `user` | Die Benutzerbestaetigung ist nur im Kontext von Vivians Rueckfrage fachlich eindeutig. |
| 15 | `B-MAIN-S15` | `systemResponse` | `B-E11`, `B-E12` | `user`, `signal` | Die Freigabe des Visitors und das fachliche Startsignal tragen den assistierten Start. |
| 16 | `B-MAIN-S16` | `environmentObservation` | `B-E13` | `environment` | Der beobachtbare Wechsel nach `brewing` bestaetigt den Start auf Objektebene. |
| 17 | `B-MAIN-S17` | `environmentObservation` | `B-E14` | `environment` | Fortschrittsanzeige ist ein beobachtbares Objektfeedback. |
| 18 | `B-MAIN-S18` | `environmentObservation` | `B-E15` | `environment` | Der Maschinenzustand `finished` zeigt den fachlichen Abschluss des Bruehvorgangs. |
| 19 | `B-MAIN-S19` | `environmentObservation` | `B-E16` | `environment` | Das sichtbare Abschlussfeedback macht den Abschluss fuer Benutzer und Testfall wahrnehmbar. |
| 20 | `B-MAIN-S20` | `systemResponse` | `B-E16`, `B-E17` | `environment`, `signal` | Vivian meldet den Abschluss, nachdem die Kaffeemaschine Abschlussfeedback liefert. |

## Trennung der Event-Kategorien

| Kategorie | Event-IDs | Modellierungsabsicht |
| --- | --- | --- |
| Benutzereingaben | `B-E01`, `B-E03`, `B-E05`, `B-E07`, `B-E11` | Diese Events kommen vom externen Actor `ACT-B-01 Visitor` und passen zu `actorIntent`-Schritten. |
| System-/Vivian-Signale | `B-E02`, `B-E08`, `B-E10`, `B-E12`, `B-E17` | Diese Events beschreiben fachliche Signale des Assistenzsystems, keine technischen Controller- oder Topic-Aufrufe. |
| Objektzustandswechsel und Objektfeedback | `B-E04`, `B-E06`, `B-E09`, `B-E13`, `B-E14`, `B-E15`, `B-E16` | Diese Events beschreiben beobachtbare Zustaende oder Rueckmeldungen der `ENT-B-02 CoffeeMachine`. |

## Beziehung zu Conditions und StateAssertions

| Event | Naheliegende spaetere Condition oder StateAssertion |
| --- | --- |
| `B-E01` | Guard `helpRequested = true` aus `B-COND-005`. |
| `B-E04` | StateAssertion `CoffeeMachine.cupPresent = true` aus `B-CM-ST-016`; Guard `B-COND-006`. |
| `B-E06` | StateAssertion `CoffeeMachine.selectedProgram = coffee` aus `B-CM-ST-018`; Guard `B-COND-008`. |
| `B-E09` | StateAssertion `CoffeeMachine.lifecycleState = ready`; Guard `B-COND-017` fuer positive Bereitschaftspruefung. |
| `B-E11` | Guard `BrewingRequest.confirmed = true` aus `B-COND-011`. |
| `B-E13` | StateAssertion `CoffeeMachine.lifecycleState = brewing` aus `B-CM-ST-008`. |
| `B-E15` | StateAssertion `CoffeeMachine.lifecycleState = finished` aus `B-CM-ST-009`. |
| `B-E16` | StateAssertion `CoffeeMachine.completionFeedback = visible` aus `B-CM-ST-025`. |

## Kardinalitaets- und Konsistenzcheck

| Regel | Bewertung fuer B |
| --- | --- |
| `ScenarioStep.triggeredBy [0..*]` | Erfuellt. Jeder Hauptpfad-Schritt besitzt mindestens ein fachlich begruendetes Event; Schritte 14, 15 und 20 nutzen mehrere Events. |
| Jeder genutzte Event hat genau eine Art | Erfuellt. Jedes Event besitzt genau einen Wert in `Event.kind`. |
| Eingaben, Objektzustandswechsel und Systemsignale getrennt | Erfuellt. Die drei Kategorien sind im Event-Katalog und in der Kategorieuebersicht getrennt. |
| Keine technische Direktkopplung | Erfuellt. Kein Event nennt API, Topic, Tool, Controller oder RuntimeAction. |
| Actor/Agent-Trennung bleibt erhalten | Erfuellt. User-Events stammen vom `Visitor`; Vivian-Events sind `signal`, nicht `actorIntent`. |
| Objektreaktionen bleiben objektbezogen | Erfuellt. Maschinenzustaende sind `environment`-Events und koennen spaeter StateAssertions tragen. |

## Abnahmekontrolle

| Kriterium aus Task 7.4 | Erfuellung |
| --- | --- |
| Eventliste vorhanden | `B-E01` bis `B-E17` sind als Event-Kandidaten angelegt. |
| Events fuer alle Hauptpfad-Schritte bestimmt | `B-MAIN-S01` bis `B-MAIN-S20` haben je eine direkte `triggeredBy`-Zuordnung. |
| Benutzereingaben getrennt | `B-E01`, `B-E03`, `B-E05`, `B-E07`, `B-E11` sind `user`-Events. |
| Objektzustandswechsel getrennt | `B-E04`, `B-E06`, `B-E09`, `B-E13`, `B-E14`, `B-E15`, `B-E16` sind `environment`-Events. |
| Systemsignale getrennt | `B-E02`, `B-E08`, `B-E10`, `B-E12`, `B-E17` sind `signal`-Events. |
| Ausdruck fuer jedes Event vorhanden | Jedes Event besitzt eine konkrete `Event.expression`. |
| Anschluss an Task 7.5 vorbereitet | Die relevante Beziehung zu Guards, Preconditions und StateAssertions ist benannt. |

## Konsequenz fuer Task 7.5

Task 7.5 kann aus dieser Eventliste Guards, Preconditions und Postconditions ableiten. Besonders relevant sind:

- `B-E01` fuer den Einstieg in assistierte Bedienung,
- `B-E04`, `B-E06`, `B-E09` fuer die positive Bereitschaftspruefung,
- `B-E10` und `B-E11` fuer die explizite Startbestaetigung,
- `B-E13`, `B-E15` und `B-E16` fuer beobachtbare Postconditions des Bruehvorgangs.
