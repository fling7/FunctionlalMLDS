# Anwendungsfall B: Schrittarten des Hauptszenarios

Stand: 2026-07-07

Task: 7.3 `Fuer jeden Schritt B die Schrittart bestimmen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Quelle: `use_case_B_main_scenario_steps.md`

## Zuordnungsregel

| Schrittart | Verwendung in B | Begruendung |
| --- | --- | --- |
| `actorIntent` | Externe Benutzerrolle aeussert eine Absicht oder fuehrt eine fachliche Bedienhandlung aus. | `Actor` ist eine externe Rolle; im Basismodell ist das `ACT-B-01 Visitor`. |
| `systemResponse` | Vivian oder das System reagiert fachlich, fuehrt, fragt, prueft oder startet eine Capability. | Vivian ist als `Agent`/`Entity` im System modelliert, nicht als primaerer Actor. |
| `environmentObservation` | Ein beobachtbarer Objekt- oder Szenenzustand tritt ein oder wird gemeldet. | Die Kaffeemaschine ist eine `Entity`; ihre Zustandsaussagen werden nicht als Actor-Intent modelliert. |

Diese Regel folgt den bestehenden Invarianten:

- Wenn `ScenarioStep.kind = actorIntent`, sollte `performedBy` auf einen `Actor` zeigen.
- Systemantworten werden ueber `CapabilityUse -> Capability` modelliert.
- Vivian ist im Basismodell `Agent`/`Entity`, nicht primaerer `Actor`.
- Die Kaffeemaschine ist `Entity`, nicht `Actor` und nicht `Agent`.

## Schrittart-Tabelle

| Nr. | Step-ID | Schritttext | ScenarioStep.kind | performedBy | Begruendung |
| ---: | --- | --- | --- | --- | --- |
| 1 | B-MAIN-S01 | Der Visitor fordert die assistierte Kaffeemaschinenbedienung an. | `actorIntent` | `ACT-B-01 Visitor` | Externe Benutzerrolle aeussert eine Bedienabsicht. |
| 2 | B-MAIN-S02 | Vivian wechselt in den Fuehrungsmodus fuer die Kaffeemaschinenbedienung. | `systemResponse` | - | Vivian ist Agent im System; der Moduswechsel ist System-/Assistenzreaktion. |
| 3 | B-MAIN-S03 | Vivian weist den Visitor auf die notwendige Tassenplatzierung hin. | `systemResponse` | - | Vivian fuehrt den Benutzer ueber eine fachliche Assistenz-Capability. |
| 4 | B-MAIN-S04 | Der Visitor platziert die Tasse an der Kaffeemaschine. | `actorIntent` | `ACT-B-01 Visitor` | Externe Benutzerrolle fuehrt eine Bedienhandlung aus. |
| 5 | B-MAIN-S05 | Die Kaffeemaschine meldet, dass eine Tasse vorhanden ist. | `environmentObservation` | - | Beobachtbarer Zustand einer `Entity`, keine Benutzerabsicht. |
| 6 | B-MAIN-S06 | Vivian weist den Visitor auf die Programmauswahl hin. | `systemResponse` | - | Vivian reagiert assistierend und bleibt Agent/Entity im System. |
| 7 | B-MAIN-S07 | Der Visitor waehlt das Kaffeeprogramm. | `actorIntent` | `ACT-B-01 Visitor` | Externe Benutzerrolle trifft eine Programmauswahl. |
| 8 | B-MAIN-S08 | Die Kaffeemaschine bestaetigt die Programmauswahl. | `environmentObservation` | - | Beobachtbare Rueckmeldung des Interaktionsobjekts. |
| 9 | B-MAIN-S09 | Der Visitor betaetigt die Starttaste. | `actorIntent` | `ACT-B-01 Visitor` | Externe Benutzerrolle fordert den Bruehstart fachlich an. |
| 10 | B-MAIN-S10 | Vivian bestaetigt die erkannte Bruehanforderung. | `systemResponse` | - | Vivian bestaetigt als Assistenzreaktion, nicht als externe Rolle. |
| 11 | B-MAIN-S11 | Das System prueft die Bedienbereitschaft der Kaffeemaschine. | `systemResponse` | - | Fachliche Systempruefung, spaeter ueber CapabilityUse modellierbar. |
| 12 | B-MAIN-S12 | Die Kaffeemaschine meldet ihre Startbereitschaft. | `environmentObservation` | - | Beobachtbarer Objektzustand und Feedback. |
| 13 | B-MAIN-S13 | Vivian fordert die explizite Startbestaetigung an. | `systemResponse` | - | Vivian stellt eine fachliche Rueckfrage als Assistenzreaktion. |
| 14 | B-MAIN-S14 | Der Visitor bestaetigt den assistierten Start. | `actorIntent` | `ACT-B-01 Visitor` | Externe Benutzerrolle autorisiert den Start. |
| 15 | B-MAIN-S15 | Das System startet den Bruehvorgang fachlich. | `systemResponse` | - | Fachlicher Systemstart, spaeter ueber CapabilityUse und RuntimeBinding angebunden. |
| 16 | B-MAIN-S16 | Die Kaffeemaschine wechselt in den Zustand `brewing`. | `environmentObservation` | - | Beobachtbare Zustandsaussage der Kaffeemaschine. |
| 17 | B-MAIN-S17 | Die Kaffeemaschine zeigt den Bruehfortschritt an. | `environmentObservation` | - | Beobachtbares Feedback des Interaktionsobjekts. |
| 18 | B-MAIN-S18 | Die Kaffeemaschine wechselt in den Zustand `finished`. | `environmentObservation` | - | Beobachtbare Zustandsaussage der Kaffeemaschine. |
| 19 | B-MAIN-S19 | Die Kaffeemaschine zeigt die Abschlussrueckmeldung an. | `environmentObservation` | - | Beobachtbares Abschlussfeedback des Interaktionsobjekts. |
| 20 | B-MAIN-S20 | Vivian meldet dem Visitor den erfolgreichen Abschluss. | `systemResponse` | - | Vivian gibt fachliche Rueckmeldung als Agent im System. |

## Verteilung der Schrittarten

| ScenarioStep.kind | Anzahl | Step-IDs |
| --- | ---: | --- |
| `actorIntent` | 5 | `B-MAIN-S01`, `B-MAIN-S04`, `B-MAIN-S07`, `B-MAIN-S09`, `B-MAIN-S14` |
| `systemResponse` | 8 | `B-MAIN-S02`, `B-MAIN-S03`, `B-MAIN-S06`, `B-MAIN-S10`, `B-MAIN-S11`, `B-MAIN-S13`, `B-MAIN-S15`, `B-MAIN-S20` |
| `environmentObservation` | 7 | `B-MAIN-S05`, `B-MAIN-S08`, `B-MAIN-S12`, `B-MAIN-S16`, `B-MAIN-S17`, `B-MAIN-S18`, `B-MAIN-S19` |

## Konsistenzpruefung

| Prueffrage | Ergebnis |
| --- | --- |
| Haben alle `actorIntent`-Schritte einen Actor? | Ja. Alle fuenf `actorIntent`-Schritte werden von `ACT-B-01 Visitor` ausgefuehrt. |
| Werden Vivian-Schritte als Actor behandelt? | Nein. Alle Vivian-Schritte sind `systemResponse`, weil Vivian als `Agent`/`Entity` im System modelliert ist. |
| Werden Kaffeemaschinenreaktionen als Actor behandelt? | Nein. Sie sind `environmentObservation`, weil die Kaffeemaschine eine `Entity` ist. |
| Gibt es technische Direktkopplung? | Nein. `B-MAIN-S15` bleibt fachlich und verweist noch nicht auf RuntimeAction. |
| Bleibt Actor/Agent-Trennung erhalten? | Ja. Visitor ist Actor; Vivian ist Agent/Entity; Kaffeemaschine ist Entity. |

## Konsequenz fuer spaetere Mapping-Tasks

| Schrittart | Spaetere Modellierungsfolge |
| --- | --- |
| `actorIntent` | `performedBy = ACT-B-01 Visitor`; Events aus Benutzerhandlungen in Task 7.4. |
| `systemResponse` | Falls fachliche Faehigkeit noetig ist, spaeter `CapabilityUse -> Capability`; technische Umsetzung erst in RuntimeBinding/RuntimeAction. |
| `environmentObservation` | Spaeter vor allem `StateAssertion` und ggf. Event aus Objektzustandswechsel, aber keine CapabilityUse erzwingen. |

## Abnahmekontrolle

| Kriterium aus Task 7.3 | Erfuellung |
| --- | --- |
| Fuer jeden Schritt eine Schrittart bestimmt | Alle 20 Hauptszenario-Schritte haben `ScenarioStep.kind`. |
| Ergebnis enthaelt `actorIntent`, `systemResponse`, `environmentObservation` | Alle drei Schrittarten werden verwendet. |
| Vivian-Schritte konsistent als Agent behandelt | Vivian-Schritte sind `systemResponse`, nicht `actorIntent`. |
| Actor/Agent-Trennung eingehalten | Nur Visitor-Schritte besitzen `performedBy = ACT-B-01 Visitor`. |
| Keine Runtime-Direktkopplung | Kein Schritt zeigt direkt auf eine technische RuntimeAction. |

## Konsequenz fuer Task 7.4

Task 7.4 kann nun die ausloesenden Events bestimmen. Dabei muessen Benutzereingaben, Vivian-/Systemsignale und Objektzustandswechsel getrennt werden.
