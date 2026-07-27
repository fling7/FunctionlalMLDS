# Anwendungsfall B: Hauptszenario als nummerierte Schritte

Stand: 2026-07-07

Task: 7.2 `Hauptszenario B in nummerierte Schritte zerlegen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Zweck

Diese Datei zerlegt den erfolgreichen Hauptablauf von `UC-B-01` in nummerierte `ScenarioStep`-Kandidaten. Jeder Schritt beschreibt genau eine fachliche Aussage: eine Benutzerhandlung, eine Vivian-Reaktion, eine Systemreaktion oder eine beobachtbare Objektreaktion.

Die Schrittarten `actorIntent`, `systemResponse` und `environmentObservation` werden noch nicht final zugeordnet. Diese Zuordnung folgt in Task 7.3.

## Annahmen fuer den Hauptpfad

Der Hauptpfad beschreibt den erfolgreichen Ablauf. Er setzt voraus, dass die in Task 6.7 beschriebenen Mindestbedingungen erfuellbar sind:

- die Kaffeemaschine ist verfuegbar und eingeschaltet,
- Vivian kann in den Assistenzmodus wechseln,
- eine Tasse kann platziert oder bestaetigt werden,
- ein Kaffeeprogramm kann gewaehlt werden,
- die Bereitschaftspruefung faellt positiv aus,
- der Benutzer bestaetigt den assistierten Start,
- kein Abbruch und kein Maschinenfehler tritt ein.

Fehlende Tasse, fehlendes Wasser, fehlende Auswahl, Benutzerabbruch, doppelter Start, Maschinenfehler und fehlende RuntimeBinding bleiben fuer Alternative- oder Exception-Szenarien reserviert.

## Nummerierte ScenarioStep-Kandidaten

| Nr. | Step-ID | Schritttext | Fachlicher Fokus | Herkunft / Bezug |
| ---: | --- | --- | --- | --- |
| 1 | B-MAIN-S01 | Der Visitor fordert die assistierte Kaffeemaschinenbedienung an. | Benutzerhandlung | B-ACT-001 |
| 2 | B-MAIN-S02 | Vivian wechselt in den Fuehrungsmodus fuer die Kaffeemaschinenbedienung. | Vivian-Reaktion | B-ACT-010, Vivian-Zustand |
| 3 | B-MAIN-S03 | Vivian weist den Visitor auf die notwendige Tassenplatzierung hin. | Vivian-Reaktion | B-ACT-010 |
| 4 | B-MAIN-S04 | Der Visitor platziert die Tasse an der Kaffeemaschine. | Benutzerhandlung | B-ACT-002 |
| 5 | B-MAIN-S05 | Die Kaffeemaschine meldet, dass eine Tasse vorhanden ist. | Objektreaktion | B-CM-ST-016 |
| 6 | B-MAIN-S06 | Vivian weist den Visitor auf die Programmauswahl hin. | Vivian-Reaktion | B-ACT-010 |
| 7 | B-MAIN-S07 | Der Visitor waehlt das Kaffeeprogramm. | Benutzerhandlung | B-ACT-003 |
| 8 | B-MAIN-S08 | Die Kaffeemaschine bestaetigt die Programmauswahl. | Objektreaktion | B-CM-ST-018, B-CM-ST-022 |
| 9 | B-MAIN-S09 | Der Visitor betaetigt die Starttaste. | Benutzerhandlung | B-ACT-004 |
| 10 | B-MAIN-S10 | Vivian bestaetigt die erkannte Bruehanforderung. | Vivian-Reaktion | B-ACT-009 |
| 11 | B-MAIN-S11 | Das System prueft die Bedienbereitschaft der Kaffeemaschine. | Systemreaktion | B-ACT-011, CAP-B-CHECK-MACHINE-READY |
| 12 | B-MAIN-S12 | Die Kaffeemaschine meldet ihre Startbereitschaft. | Objektreaktion | B-CM-ST-006, B-CM-ST-021 |
| 13 | B-MAIN-S13 | Vivian fordert die explizite Startbestaetigung an. | Vivian-Reaktion | B-ACT-013 |
| 14 | B-MAIN-S14 | Der Visitor bestaetigt den assistierten Start. | Benutzerhandlung | B-ACT-005 |
| 15 | B-MAIN-S15 | Das System startet den Bruehvorgang fachlich. | Systemreaktion | B-ACT-014, CAP-B-START-BREWING |
| 16 | B-MAIN-S16 | Die Kaffeemaschine wechselt in den Zustand `brewing`. | Objektreaktion | B-CM-ST-008 |
| 17 | B-MAIN-S17 | Die Kaffeemaschine zeigt den Bruehfortschritt an. | Objektreaktion | B-CM-ST-023 |
| 18 | B-MAIN-S18 | Die Kaffeemaschine wechselt in den Zustand `finished`. | Objektreaktion | B-CM-ST-009 |
| 19 | B-MAIN-S19 | Die Kaffeemaschine zeigt die Abschlussrueckmeldung an. | Objektreaktion | B-CM-ST-025 |
| 20 | B-MAIN-S20 | Vivian meldet dem Visitor den erfolgreichen Abschluss. | Vivian-Reaktion | B-ACT-016 |

## Schrittqualitaet

| Prueffrage | Ergebnis |
| --- | --- |
| Beschreibt jeder Schritt genau eine fachliche Aussage? | Ja. Kombinierte Aussagen wie "pruefen und starten" wurden getrennt. |
| Sind Benutzerhandlungen von Vivian-Reaktionen getrennt? | Ja. Visitor-Schritte und Vivian-Schritte sind jeweils eigene Kandidaten. |
| Sind Systemreaktionen von Objektreaktionen getrennt? | Ja. Bereitschaftspruefung und Bruehstart liegen getrennt von Maschinenzustaenden. |
| Gibt es technische Controller-Aufrufe? | Nein. `RuntimeAction`-Details bleiben spaeteren Mapping-Tasks vorbehalten. |
| Ist der Erfolgszustand beobachtbar? | Ja. `brewing`, `finished`, Fortschritt und Abschlussrueckmeldung sind eigene Objektreaktionen. |

## Minimaler Trace des Hauptpfads

Der Hauptpfad bleibt fachlich und runtimefrei:

`UC-B-01 -> B-MAIN-S01 -> ... -> B-MAIN-S20`

Die technische Ausfuehrung des Bruehstarts wird nicht in der Schrittfolge beschrieben. Sie wird spaeter nur ueber:

`B-MAIN-S15 -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`

angebunden.

## Noch nicht entschieden in 7.2

Folgende Punkte werden bewusst erst in den naechsten Tasks entschieden:

- Task 7.3 ordnet jedem Schritt `actorIntent`, `systemResponse` oder `environmentObservation` zu.
- Task 7.4 bestimmt die konkreten Events.
- Task 7.5 bestimmt Guards, Pre- und Postconditions.
- Task 7.6 bestimmt konkrete StateAssertions.
- Task 7.7 definiert StepRelations.
- Task 7.9 und 7.10 formulieren Alternative- und Exception-Szenarien.

## Abnahmekontrolle

| Kriterium aus Task 7.2 | Erfuellung |
| --- | --- |
| Sequenz von ScenarioStep-Kandidaten vorhanden | Die Tabelle enthaelt `B-MAIN-S01` bis `B-MAIN-S20`. |
| Jeder Schritt beschreibt genau eine fachliche Aussage | Die Schritttexte trennen Benutzerhandlung, Vivian-Reaktion, Systemreaktion und Objektreaktion. |
| Benutzer-, Vivian-, System- und Objektreaktionen sind enthalten | Alle vier Fokusarten kommen im Hauptpfad vor. |
| Keine Runtime-Direktkopplung | Kein Schritt nennt Controller, API, Tool, Topic oder RuntimeAction. |
| Grundlage fuer 7.3 vorhanden | Die Spalte `Fachlicher Fokus` bereitet die Schrittart-Zuordnung vor, ohne sie vorwegzunehmen. |

## Konsequenz fuer Task 7.3

Task 7.3 kann nun fuer jeden Schritt bestimmen, ob er als `actorIntent`, `systemResponse` oder `environmentObservation` modelliert wird. Dabei ist besonders zu pruefen, ob Vivian-Schritte konsistent als Reaktionen eines `Agent`/`Entity` im System behandelt werden.
