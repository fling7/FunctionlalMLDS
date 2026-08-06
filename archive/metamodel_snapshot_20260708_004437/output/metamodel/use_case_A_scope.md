# Anwendungsfall A: Systemgrenze

Stand: 2026-07-07

Task: 2.2 `Systemgrenze fuer Anwendungsfall A festlegen`

Zweckbezug: Der Anwendungsfall beschreibt, wie ein Agent innerhalb einer virtuellen Szene zur Laufzeit auf Ereignisse und Bedingungen reagiert, seine Rolle, Position oder Handlung dynamisch aendert und dadurch einen explizit pruefbaren Zielzustand der Szene erreicht.

## Kurzdefinition der Systemgrenze

Im Scope liegt die fachliche Modellierung dynamischen Agentenverhaltens innerhalb einer virtuellen Szene, einschliesslich ausloesender Ereignisse, relevanter Bedingungen, beobachtbarer Szenenzustaende, benoetigter fachlicher Faehigkeiten und ihrer nachvollziehbaren technischen Bindung.

Out of Scope liegen die konkrete 3D-Asset-Erzeugung, Engine- oder Framework-Implementierung, Low-Level-Pathfinding, Physiksimulation, Renderingdetails und die tatsaechliche Ausfuehrung von Code in Unity, WebXR oder einer sonstigen Runtime.

## Im Scope

| Bereich | Im Scope | Modellnahe Begruendung |
| --- | --- | --- |
| Agentenverhalten | Fachliche Beschreibung, wie ein Agent auf Events und Conditions reagiert, eine Rolle einnimmt, eine Handlung ausfuehrt, sich in der Szene verortet oder seinen Zustand aendert. | Wird spaeter ueber `Agent`, `ScenarioStep`, `Event`, `Condition`, `CapabilityUse`, `Capability` und `StateAssertion` abbildbar. |
| Szenenzustand | Beobachtbare Zustaende der Szene, die fuer den Ablauf oder Zielzustand relevant sind, z. B. Agentposition, Zielzone, Objektstatus, Sichtbarkeit, Aktivierung oder Erreichbarkeit. | Wird spaeter ueber `StateAssertion`, `Condition`, `Effect` und ggf. `Entity` beschrieben. |
| Runtime-Ausfuehrung | Nachvollziehbare Zuordnung fachlicher Capabilities zu technischen Bindungen, soweit sie fuer Traceability und Validierung benoetigt wird. | Wird spaeter ueber `RuntimeBinding`, `RuntimeAction` und `ValidationCase` angebunden, ohne ScenarioSteps technisch kurzzuschliessen. |
| Ereignisse | User-, Signal-, Raum-, Zeit- oder Umgebungsereignisse, die Agentenverhalten ausloesen oder verzweigen. | Passt zu `Event.kind` und `StepRelation`. |
| Bedingungen | Guards, Vorbedingungen, Nachbedingungen, raeumliche oder zeitliche Bedingungen, die Verhalten erlauben, verhindern oder verzweigen. | Passt zu `Condition.kind` und Capability-Preconditions. |
| Zielzustand | Pruefbare Zielaussage, dass Agent und Szene nach dem Ablauf einen erwarteten Zustand erreicht haben. | Passt zu `StateAssertion`, `Effect` und `ValidationCase.expectedOutcome`. |
| Traceability | Nachvollziehbarkeit von Requirement/UseCase ueber ScenarioStep und Capability bis zur RuntimeBinding und Validierung. | Entspricht der Kernidee des Metamodells. |

## Out of Scope

| Bereich | Out of Scope | Begruendung |
| --- | --- | --- |
| 3D-Asset-Erzeugung | Generierung konkreter Meshes, Texturen, Materialien, Animationsclips oder Prefabs. | Das Metamodell beschreibt dynamisches Verhalten und Traceability, nicht die Asset-Pipeline. |
| Rendering | Licht, Kamera, Shader, Level-of-Detail, Framerate und visuelle Post-Processing-Effekte. | Diese Details sind technische Darstellungsfragen und keine fachlichen Agentenregeln. |
| Low-Level-Pathfinding | Algorithmische Pfadsuche, Kollisionsvermeidung, Steering-Details oder NavMesh-Implementierung. | Fachlich relevant ist der Zielzustand, nicht die konkrete Bewegungsberechnung. |
| Physiksimulation | Starre Koerper, Kollisionen, Kraefte, Constraints oder Solver-Parameter. | Nur beobachtbare Effekte oder Bedingungen gehoeren in den Scope. |
| Runtime-Code | Implementierung konkreter Controller, APIs, Tools, Topics, Skripte oder Engine-Komponenten. | Technische Details werden nur als RuntimeAction referenzierbar, aber nicht implementiert. |
| KI-Planungsalgorithmus | Interne Entscheidungslogik eines autonomen Agenten, z. B. Planner, Behavior Tree oder Policy-Training. | Modelliert wird das fachlich relevante Verhalten im Szenario, nicht der interne Algorithmus. |
| Vollstaendige Szenenmodellierung | Vollstaendige Raumgeometrie, Inventarlisten oder nicht interaktionsrelevante Umgebungsobjekte. | Nur fuer Verhalten relevante Entities, Conditions und StateAssertions werden betrachtet. |
| Nutzerstudie | Empirische Evaluation von Wahrnehmung, Usability oder Immersion. | Kann spaeter validierend anschliessen, ist aber nicht Teil dieser Systemgrenze. |

## Eindeutige Einsortierung der Abnahmekriterien

| Abnahmekriterium | Einsortierung | Konsequenz fuer die naechsten Tasks |
| --- | --- | --- |
| Agentenverhalten | Im Scope als fachliches Verhalten, Rollenbezug, Reaktion, Handlung und Zustandsaenderung; out of scope als konkrete KI- oder Bewegungsimplementierung. | In 2.3 und 2.4 werden Rollen, Agents und Entities getrennt bestimmt. |
| Szenenzustand | Im Scope als beobachtbarer, pruefbarer Zustand; out of scope als vollstaendige grafische oder physikalische Szenenbeschreibung. | In 2.5, 2.6, 2.8 und 2.9 werden relevante Objekte, Ereignisse, Vor- und Nachbedingungen gesammelt. |
| Runtime-Ausfuehrung | Im Scope als Trace von Capability zu RuntimeBinding/RuntimeAction und ValidationCase; out of scope als konkrete Code-Implementierung und Engine-Ausfuehrung. | In spaeteren Mapping-Tasks wird technische Ausfuehrung erst nach Capability modelliert. |

## Grenzentscheidungen

| Frage | Entscheidung |
| --- | --- |
| Darf ein ScenarioStep direkt eine API, ein Tool oder einen Topic nennen? | Nein. Das bleibt out of scope fuer ScenarioStep und gehoert spaeter unter `RuntimeBinding -> RuntimeAction`. |
| Darf Agentenbewegung modelliert werden? | Ja, aber fachlich als Ziel, Bedingung, Schritt, Capability und erwarteter Zustand, nicht als Pathfinding-Algorithmus. |
| Darf die Szene selbst modelliert werden? | Ja, aber nur soweit Szenelemente fuer Agentenverhalten, Bedingungen oder Zielzustaende relevant sind. |
| Darf technische Ausfuehrung ueberhaupt vorkommen? | Ja, aber nur als nachvollziehbare Bindung fachlicher Capabilities an RuntimeActions, nicht als Implementierung. |
| Wird jetzt schon entschieden, ob ein Ergaenzungsmodell noetig ist? | Nein. Diese Entscheidung folgt erst nach den Modellierbarkeitspruefungen. |

## Nicht vorweggenommen

Dieser Task legt noch nicht fest:

- konkrete externe Rollen,
- konkrete Agent- oder Entity-Instanzen,
- konkrete Szenenobjekte,
- konkrete Ereignisse, Conditions oder Zielzustaende,
- konkrete Capabilities,
- konkrete RuntimeBindings,
- ob das Kernmetamodell angepasst oder ein Ergaenzungsmodell eingehangen wird.

Diese Punkte werden in den naechsten Tasks schrittweise ausgearbeitet.
