# Anwendungsfall A: Zweckformulierung

Stand: 2026-07-07

Task: 2.1 `Zweck des Anwendungsfalls A in einem Satz formulieren`

## Zwecksatz

Der Anwendungsfall beschreibt, wie ein Agent innerhalb einer virtuellen Szene zur Laufzeit auf Ereignisse und Bedingungen reagiert, seine Rolle, Position oder Handlung dynamisch aendert und dadurch einen explizit pruefbaren Zielzustand der Szene erreicht.

## Abnahmekontrolle

| Kriterium aus Task 2.1 | Erfuellt durch | Status |
| --- | --- | --- |
| enthaelt Szene | `innerhalb einer virtuellen Szene`, `Zielzustand der Szene` | OK |
| enthaelt Agent | `ein Agent` | OK |
| enthaelt dynamische Aenderung | `zur Laufzeit ... reagiert`, `dynamisch aendert` | OK |
| enthaelt Zielzustand | `explizit pruefbaren Zielzustand` | OK |

## Begruendung der Formulierung

- `Agent` bleibt bewusst fachlich und wird noch nicht mit einer technischen Implementierung verwechselt.
- `virtuelle Szene` legt den Kontext fest, ohne bereits konkrete Objekte oder Layouts festzuschreiben.
- `Ereignisse und Bedingungen` passt zu `Event` und `Condition` des Metamodells.
- `Rolle, Position oder Handlung` laesst genug Raum fuer Agentendynamik, ohne bereits ein eigenes Agenten-Ergaenzungsmodell vorauszusetzen.
- `explizit pruefbarer Zielzustand` verweist auf `StateAssertion`, `Effect` und spaetere `ValidationCase`-Instanzen.

## Nicht vorweggenommen

Dieser Task legt noch nicht fest:

- welche konkrete Szene verwendet wird,
- welche Actor- oder Agent-Instanzen existieren,
- welche Szenenobjekte im Scope liegen,
- welche Capabilities benoetigt werden,
- ob das bestehende Metamodell ausreicht oder ein Ergaenzungsmodell benoetigt wird.

Diese Punkte folgen erst in den naechsten Tasks ab 2.2.
