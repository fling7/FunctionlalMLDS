# Anwendungsfall A: Actor-Instanzen

Stand: 2026-07-07

Task: 4.3 `Actor-Instanzen fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

Ein `Actor` ist in diesem Metamodell eine externe Rolle, die mit einer Systemnutzung interagiert. Ein Actor ist keine konkrete Person, kein Avatar, kein Sensor, kein Szenenobjekt und kein Agent.

Die Beziehung `Actor -- UseCase` ist eine Assoziation mit `0..*` auf beiden Seiten. Ein Actor besitzt den Use Case also nicht, und ein Use Case besitzt den Actor nicht. Fuer `UC-A-01` werden nur solche Actor-Instanzen angelegt, die im fachlichen Anwendungsfall tatsaechlich mit der Systemnutzung interagieren. Weitere Kandidaten werden bewusst ausgeschlossen oder zurueckgestellt.

`ScenarioStep.performedBy` wird hier noch nicht belegt. Diese Referenz ist spaeter nur fuer konkrete Schritte mit `ScenarioStep.kind = actorIntent` relevant und hat die Kardinalitaet `0..1`.

## Angelegte Actor-Instanzen

| Instanz-ID | Metamodellklasse | `uuid` | `shortName` | Rolle im Use Case | `interactsWith` | Interaktionsart | Abgrenzung |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ACT-A-01` | `Actor` | `ACT-A-01` | `ScenarioDesigner` | Externe Rolle, die Ziel, Bedingungen und erwartetes dynamisches Agentenverhalten fachlich spezifiziert. | `UC-A-01` | Primaere UseCase-Rolle; liefert Modellierungsabsicht, Zieltext und fachlichen Kontext. | Keine Person und kein Autorentool; konkrete Ausfuehrung bleibt offen. |
| `ACT-A-02` | `Actor` | `ACT-A-02` | `SceneParticipant` | Externe Rolle, deren raeumliche oder interaktive Handlung ein gueltiges Szenenereignis ausloesen kann. | `UC-A-01` | Unterstuetzende Rolle; steht im Hauptpfad hinter dem Event `A-E1 = entered(SceneParticipant, TriggerZone)`. | Kein Avatar und kein Agent; die konkrete Praesenz waere spaeter `Entity` oder `Agent`. |
| `ACT-A-03` | `Actor` | `ACT-A-03` | `SceneObserver` | Externe Rolle, die Zielzustand, Rueckmeldung und beobachtbare Wirkung des Agentenverhaltens beurteilen kann. | `UC-A-01` | Unterstuetzende Beobachterrolle; relevant fuer beobachtbare Effekte, StateAssertions und spaetere ValidationCases. | Kein ValidationCase und kein Monitoring-Objekt; diese werden separat modelliert. |

## Explizite Actor-UseCase-Beziehungen

| Beziehung-ID | Quelle | Ziel | Beziehung | Kardinalitaetsbewertung |
| --- | --- | --- | --- | --- |
| `A-AU-01` | `ACT-A-01` | `UC-A-01` | `interactsWith` | Zulaessig, weil `Actor -- UseCase` beidseitig `0..*` erlaubt. |
| `A-AU-02` | `ACT-A-02` | `UC-A-01` | `interactsWith` | Zulaessig, weil der Actor ein fachliches Start-Event im UseCase-Kontext ausloesen kann. |
| `A-AU-03` | `ACT-A-03` | `UC-A-01` | `interactsWith` | Zulaessig, weil der Actor die beobachtbare Zielerreichung des UseCase-Kontexts bewertet. |

## Nicht instanziierte Kandidaten

| Kandidat | Entscheidung | Begruendung | Spaetere Modellierungsstelle |
| --- | --- | --- | --- |
| `TrainingSupervisor` | Fuer `UC-A-01` nicht als Actor-Instanz angelegt. | Der aktuelle Basis-UseCase beschreibt dynamisches Agentenverhalten in einer Szene, aber keinen expliziten Trainings-, Korrektur- oder Tutorablauf. Ohne konkreten Trainingsmodus waere die Rolle zu breit. | Kann in einem separaten Trainings-UseCase, einem `Extend`-UseCase oder spaeter in Beispiel B wieder aufgenommen werden. |
| `ExternalEventSource` | Nicht als Actor-Instanz angelegt. | Eine passive Signalquelle interagiert hier nicht als externe UseCase-Rolle, sondern liefert ein Ereignis. Das ist praeziser als `Event` mit optionaler `Entity` modellierbar. | `A-E2 = signalEmitted(ExternalSignalSource)` sowie `ExternalSignalSource` als `Entity`, falls der alternative Startpfad formalisiert wird. |

## Warum genau diese drei Actoren?

`ScenarioDesigner` ist notwendig, weil der Use Case eine fachliche Modellierungsleistung beschreibt. Ohne diese externe Rolle waere nicht klar, wer Ziel, Bedingungen und erwartetes Verhalten als Systemnutzung einbringt.

`SceneParticipant` ist notwendig, weil das Hauptszenario mit einem raeumlichen Ereignis startet, das fachlich durch eine externe Teilnahme an der Szene ausgeloest werden kann.

`SceneObserver` ist notwendig, weil die Zielerreichung im Use Case nicht nur intern ausgefuehrt, sondern beobachtbar und spaeter validierbar sein muss.

`TrainingSupervisor` und `ExternalEventSource` werden nicht geloescht, sondern bewusst nicht instanziiert: Der erste Kandidat gehoert zu einem optionalen Trainingskontext, der zweite zu Ereignis- und Entity-Modellierung.

## Abnahmekontrolle

| Kriterium aus Task 4.3 | Erfuellung |
| --- | --- |
| Actorliste vorhanden | `ACT-A-01`, `ACT-A-02` und `ACT-A-03` sind angelegt. |
| Jeder angelegte Actor interagiert mit dem UseCase | Alle drei Actor-Instanzen besitzen eine explizite `interactsWith`-Beziehung zu `UC-A-01`. |
| Ausgeschlossene Kandidaten begruendet | `TrainingSupervisor` und `ExternalEventSource` sind mit Entscheidung und spaeterer Modellierungsstelle dokumentiert. |
| Actor/Agent/Entity-Trennung gewahrt | Kein Actor wird als Avatar, Agent, Szenenobjekt, Sensor oder Runtime-System modelliert. |
| Kardinalitaet eingehalten | Drei Actoren koennen denselben Use Case referenzieren; die `0..*`-Assoziation erlaubt das. |
| Keine Folge-Tasks vorweggenommen | `performedBy`, `Satisfy`, `Scenario`, `CapabilityUse`, `RuntimeBinding` und `ValidationCase` bleiben fuer spaetere Tasks offen. |

## Konsequenz fuer Task 4.4

Task 4.4 kann nun die `Satisfy`-Beziehungen fuer Anwendungsfall A pruefen. Dabei ist zu beachten, dass `Satisfy` entweder Requirements oder UseCases referenziert, aber nicht beides in derselben Instanz.
