# Anwendungsfall B: Zweck

Stand: 2026-07-07

Task: 6.1 `Zweck des Anwendungsfalls B in einem Satz formulieren`

## Zwecksatz

Anwendungsfall B beschreibt, wie eine Benutzerrolle in einer virtuellen Szene mit Vivian als fachlich beteiligter Assistenz ein Interaktionsobjekt, exemplarisch eine Kaffeemaschine, bedient, sodass eine konkrete Bedienhandlung pruefbar in einen erwarteten Objektzustand und eine passende Systemrueckmeldung ueberfuehrt wird.

## Praezisierung des Satzes

Der Satz ist bewusst noch rollen-neutral formuliert: Vivian wird hier noch nicht als `Actor`, `Agent`, `Entity` oder Kombination festgelegt. Diese Entscheidung folgt erst in Task 6.3.

Der Zweck umfasst drei fachliche Kerne:

| Kern | Bedeutung fuer B |
| --- | --- |
| Benutzerrolle | Eine externe Rolle will die Kaffeemaschine in der virtuellen Szene bedienen oder dabei angeleitet werden. |
| Objektinteraktion | Die Kaffeemaschine ist nicht nur Kulisse, sondern ein fachlich relevantes Interaktionsobjekt mit bedienbaren Elementen und Zustaenden. |
| Erwarteter Systemeffekt | Nach der Bedienhandlung muss ein pruefbarer Zustand eintreten, z. B. `coffeeMachine.state = brewing`, und eine Rueckmeldung sichtbar oder wahrnehmbar sein. |

## Abnahmekontrolle

| Kriterium aus Task 6.1 | Erfuellung |
| --- | --- |
| Satz enthaelt Benutzerrolle | Ja: `Benutzerrolle in einer virtuellen Szene`. |
| Satz enthaelt Objektinteraktion | Ja: `Interaktionsobjekt, exemplarisch eine Kaffeemaschine, bedient`. |
| Satz enthaelt erwarteten Systemeffekt | Ja: `erwarteten Objektzustand und eine passende Systemrueckmeldung`. |
| Keine vorzeitige Vivian-Einordnung | Ja: Vivian bleibt bis Task 6.3 rollen-neutral. |

## Konsequenz fuer Task 6.2

Task 6.2 muss nun die Systemgrenze fuer B festlegen: Im Scope liegen Vivian, Benutzerinteraktion, Kaffeemaschinenzustand, Bedienhandlungen, fachliche Capabilities, Runtime-Bindung und Validierung. Out of Scope sind konkrete Engine-Implementierung, physische Hardwaredetails, Rendering und nicht relevante Szenenobjekte.
