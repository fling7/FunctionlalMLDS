# Anwendungsfall A: Main-Use-Case

Stand: 2026-07-07

Task: 3.1 `Einen Main-Use-Case fuer A benennen`

Zweckbezug: Der Anwendungsfall beschreibt, wie ein Agent innerhalb einer virtuellen Szene zur Laufzeit auf Ereignisse und Bedingungen reagiert, seine Rolle, Position oder Handlung dynamisch aendert und dadurch einen explizit pruefbaren Zielzustand der Szene erreicht.

## Festlegung

| Feld | Wert |
| --- | --- |
| Stabiler Identifier | `UC-A-01` |
| Use-Case-Name | `Dynamisches Agentenverhalten in virtueller Szene modellieren` |
| Kurzname | `Dynamische Agentenreaktion` |
| Primaerer Actor | `ScenarioDesigner` |
| Weitere beteiligte Rollen | `SceneParticipant`, `SceneObserver`, optional `ExternalEventSource`, optional `TrainingSupervisor` |
| Main-Scenario-Name fuer Folge-Tasks | `Agent reagiert auf gueltiges Ereignis und erreicht Zielzone` |
| UseCase.goal | `Dynamisches Agentenverhalten in einer virtuellen Szene so fachlich modellieren, dass ein Agent auf gueltige Ereignisse und Bedingungen reagieren, seine Rolle oder Handlung anpassen und einen pruefbaren Zielzustand der Szene erreichen kann.` |

## Begruendung

Der Name beschreibt die fachliche Nutzung: Ein dynamisches Agentenverhalten wird in einer virtuellen Szene modelliert. Er vermeidet technische Begriffe wie Engine, Controller, API, Pathfinding, RuntimeAction oder Simulation-Backend. Gleichzeitig bleiben die fachlichen Kernbestandteile sichtbar:

- `Agentenverhalten`: Der Use Case bezieht sich auf einen Agenten als ausfuehrende oder beobachtete Entitaet.
- `virtuelle Szene`: Der Use Case ist nicht allgemein-agentisch, sondern szenenbezogen.
- `modellieren`: Der Use Case beschreibt die Spezifikation und Strukturierung des Verhaltens, nicht dessen technische Ausfuehrung.
- `dynamisch`: Der Use Case deckt Reaktionen auf Ereignisse, Bedingungen, Rollenwechsel, Zustandswechsel und Zielerreichung ab.

## Namenskandidaten

| Kandidat | Bewertung | Entscheidung |
| --- | --- | --- |
| `Dynamisches Agentenverhalten in virtueller Szene modellieren` | Fachlich, kompakt, ohne technische Implementierungsannahmen; passt zu Scope, Ziel und Metamodell. | gewaehlt |
| `Agent reagiert in virtueller Szene auf Ereignisse` | Gut verstaendlich, aber zu eng, weil Zielzustand und Modellierungsaspekt fehlen. | verworfen |
| `Agent erreicht Zielzone nach Szenenereignis` | Gut als Szenarioname, aber zu konkret fuer den Use Case. | nur als Grundlage fuer Main-Scenario-Name |
| `Dynamische Agentensteuerung in VR` | Zu technisch und zu nah an Steuerung/Runtime; `VR` verengt den Kontext unnoetig. | verworfen |
| `Agent Pathfinding und Szenenreaktion ausfuehren` | Enthaelt technische und algorithmische Begriffe; Pathfinding ist out of scope. | verworfen |
| `Runtime Agent Controller konfigurieren` | Beschreibt technische Umsetzung statt fachlicher Nutzung. | verworfen |

## Einordnung im Metamodell

| Metamodell-Element | Vorgesehene Belegung |
| --- | --- |
| `UseCase.uuid` | `UC-A-01` |
| `UseCase.text` | Fachliche Beschreibung des dynamischen Agentenverhaltens in der virtuellen Szene. |
| `UseCase.goal` | Siehe Festlegung oben. |
| `Scenario.kind` | `main` fuer das Hauptszenario aus Task 3.2. |
| `Scenario.goal` | `Nach einem gueltigen Ausloeseereignis befindet sich der dynamische Agent innerhalb des gueltigen Szenenbereichs in der passenden Rolle, erreicht die fachlich erreichbare Zielzone und erzeugt eine bestaetigte beobachtbare Rueckmeldung.` |
| `Actor` | Primaer `ScenarioDesigner`; weitere Rollen werden in den ScenarioSteps verwendet, wenn sie fachlich ausloesen oder beobachten. |

## Abnahmekontrolle

| Kriterium aus Task 3.1 | Erfuellung |
| --- | --- |
| Stabiler Use-Case-Identifier vorhanden | `UC-A-01` |
| Sprechender Name vorhanden | `Dynamisches Agentenverhalten in virtueller Szene modellieren` |
| Name beschreibt fachliche Nutzung | Der Name nennt Agentenverhalten, virtuelle Szene und Modellierung. |
| Name beschreibt nicht technische Umsetzung | Keine Engine, keine API, kein Pathfinding, kein Controller, keine RuntimeAction. |
| Anschluss an Folge-Tasks vorhanden | Main-Scenario-Name ist festgelegt, aber die ScenarioSteps bleiben Task 3.2 vorbehalten. |

## Konsequenz fuer Task 3.2

Task 3.2 kann das Main Scenario `Agent reagiert auf gueltiges Ereignis und erreicht Zielzone` in nummerierte `ScenarioStep`-Kandidaten zerlegen. Dabei sollte der Hauptpfad zuerst ohne Alternative und Exception modelliert werden.
