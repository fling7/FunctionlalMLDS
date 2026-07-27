# Anwendungsfall B: Main-Use-Case

Stand: 2026-07-07

Task: 7.1 `Main-Use-Case fuer B benennen`

## Entscheidung

| Feld | Wert |
| --- | --- |
| Stabiler Identifier | `UC-B-01` |
| Sprechender Name | `Assistierte Kaffeemaschinenbedienung mit Vivian` |
| Kurzform | `Kaffeemaschine mit Vivian bedienen` |
| Primaerer Actor | `ACT-B-01 Visitor` |
| Fachlich beteiligter Agent | `ENT-B-01 VivianAssistant` |
| Zentrales Interaktionsobjekt | `ENT-B-02 CoffeeMachine` |

## Use-Case-Satz

`UC-B-01 Assistierte Kaffeemaschinenbedienung mit Vivian` beschreibt, wie eine Benutzerrolle in einer virtuellen Szene mit Vivian als fachlicher Assistenz eine Kaffeemaschine bedient, die Bedienbereitschaft pruefen laesst, den Bruehvorgang freigibt oder korrigiert und am Ende einen pruefbaren Maschinenzustand mit nachvollziehbarer Rueckmeldung erreicht.

## Begruendung des Namens

| Namensbestandteil | Begruendung |
| --- | --- |
| `Assistierte` | Macht deutlich, dass Vivian fachlich beteiligt ist, ohne Vivian faelschlich als primaeren Actor zu setzen. |
| `Kaffeemaschinenbedienung` | Beschreibt die fachliche Nutzung des Interaktionsobjekts, nicht eine technische Aktion. |
| `mit Vivian` | Verankert den konkreten Beispielkontext und grenzt B vom allgemeinen Kaffeemaschinen-Use-Case ab. |

## Abgrenzung zu unpassenden Namen

| Verworfener Name | Grund |
| --- | --- |
| `StartBrewing` | Zu technisch und zu eng; beschreibt nur eine Capability oder RuntimeAction-nahe Funktion. |
| `CoffeeMachineController.startBrewing` | Verletzt die Trennung von UseCase und RuntimeAction. |
| `Vivian startet Kaffeemaschine` | Verschiebt die externe Benutzerrolle aus dem Fokus und klingt wie eine einzelne Systemreaktion. |
| `Kaffee bruehen` | Zu allgemein; Vivian-Assistenz und Bedieninteraktion fehlen. |

## Fachlicher Umfang des Main-Use-Case

Der Use Case umfasst:

- Benutzer fordert assistierte Bedienung an oder interagiert mit der Kaffeemaschine.
- Vivian fuehrt, bestaetigt, erklaert oder fragt fachlich nach.
- Kaffeemaschine wird auf Bereitschaft geprueft.
- Benutzer setzt notwendige Voraussetzungen wie Tasse und Programmauswahl.
- Vivian/System gibt den Start frei oder erklaert fehlende Voraussetzungen.
- Bruehvorgang wird fachlich gestartet, falls alle Bedingungen erfuellt sind.
- Abschluss oder sicherer/erklaerbarer Abbruch wird rueckgemeldet.

Der Use Case umfasst nicht:

- konkrete Controller-, API-, Tool- oder Topic-Aufrufe,
- interne LLM-, TTS-, Avatar- oder Dialogmodell-Implementierung von Vivian,
- physische Kaffeemaschinenhardware,
- Rendering-, Asset- oder Collider-Details.

## Erwarteter Erfolgszustand

Ein erfolgreicher Hauptpfad von `UC-B-01` endet mindestens mit:

- `CoffeeMachine.lifecycleState = brewing` nach dem assistierten Start,
- spaeter `CoffeeMachine.lifecycleState = finished` nach Abschluss,
- sichtbarer oder hoerbarer Rueckmeldung durch Vivian oder Kaffeemaschine,
- keiner direkten Abkuerzung von `ScenarioStep` zu `RuntimeAction`.

## Anschluss an bestehende B-Artefakte

| Artefakt | Anschluss |
| --- | --- |
| `use_case_B_purpose.md` | Liefert den Zweck: Benutzerrolle, Interaktionsobjekt, Vivian und erwarteter Systemeffekt. |
| `use_case_B_scope.md` | Definiert die Systemgrenze fuer Vivian, Kaffeemaschine, Benutzerinteraktion und Runtime-Trace. |
| `use_case_B_vivian_classification.md` | Legt Vivian als `Agent`/`Entity` fest, nicht als primaeren Actor. |
| `use_case_B_coffee_machine_classification.md` | Legt die Kaffeemaschine als `Entity` und Interaktionsobjekt fest. |
| `use_case_B_interaction_actions.md` | Liefert den Handlungskatalog fuer spaetere ScenarioSteps. |
| `use_case_B_preconditions.md` | Liefert Preconditions und Guards fuer den Use Case. |
| `use_case_B_error_exception_cases.md` | Liefert Alternative- und Exception-Kandidaten. |

## Abnahmekontrolle

| Kriterium aus Task 7.1 | Erfuellung |
| --- | --- |
| Stabiler Use-Case-Identifier vorhanden | Ja: `UC-B-01`. |
| Sprechender Name vorhanden | Ja: `Assistierte Kaffeemaschinenbedienung mit Vivian`. |
| Name beschreibt fachliche Nutzung | Ja: Der Name beschreibt Bedienung des Interaktionsobjekts mit Vivian, nicht eine technische Umsetzung. |
| Keine technische Runtime-Vermischung | Ja: Controller-, API- und RuntimeAction-Namen sind explizit ausgeschlossen. |
| Anschluss an spaetere Szenarios vorbereitet | Ja: Umfang und Erfolgszustand bereiten Task 7.2 vor. |

## Konsequenz fuer Task 7.2

Task 7.2 kann nun das Hauptszenario von `UC-B-01` in nummerierte ScenarioStep-Kandidaten zerlegen. Grundlage ist die minimale Hauptpfad-Sequenz aus `use_case_B_interaction_actions.md`, verfeinert durch Preconditions und Fehlerkandidaten.
