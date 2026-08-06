# Anwendungsfall B: Actor- und Agent-Zuordnung

Stand: 2026-07-07

Task: 8.3 `Actor- und Agent-Zuordnung fuer Vivian und Benutzer anlegen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Modellierungsregel

Ein `Actor` ist eine externe Rolle, die mit dem Use Case interagiert. Ein `Agent` ist eine ausfuehrende oder beobachtete `Entity` innerhalb des betrachteten Systems. Diese Trennung ist fuer Anwendungsfall B zentral:

- Der `Visitor` ist die externe Benutzerrolle und wird als `Actor` modelliert.
- `VivianAssistant` ist im aktuellen Systemzuschnitt Teil der assistierten VR-Interaktion und wird als `Agent` modelliert. Als `Agent` ist Vivian zugleich eine spezialisierte `Entity`.
- Vivian wird in der Baseline nicht als `Actor` modelliert.
- `ScenarioStep.performedBy` wird nur fuer Schritte mit `ScenarioStep.kind = actorIntent` gesetzt.
- Vivian-Schritte bleiben `systemResponse` und werden spaeter ueber `CapabilityUse -> Capability` angebunden, nicht ueber `performedBy`.

Diese Regel erfuellt die Invariante: Wenn `ScenarioStep.kind = actorIntent`, dann sollte `performedBy` auf einen `Actor` zeigen. Systemantworten werden dagegen ueber fachliche Capabilities modelliert.

## Angelegte Actor-Instanz

| Instanz-ID | Metamodellklasse | `uuid` | `shortName` | Rolle im Use Case | `interactsWith` | Interaktionsart | Abgrenzung |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ACT-B-01` | `Actor` | `ACT-B-01` | `Visitor` | Externe Benutzerrolle, die die assistierte Bedienung anfordert, Bedienhandlungen ausfuehrt und den assistierten Start bestaetigt. | `UC-B-01` | Primaere UseCase-Rolle; liefert Hilfewunsch, Tassenplatzierung, Programmauswahl, Startwunsch und Startbestaetigung. | Keine konkrete Person, kein Avatar, keine Entity und kein Agent. Eine koerperliche Repraesentation waere bei Bedarf eine separate `Entity`. |

## Explizite Actor-UseCase-Beziehung

| Beziehung-ID | Quelle | Ziel | Beziehung | Kardinalitaetsbewertung |
| --- | --- | --- | --- | --- |
| `B-AU-01` | `ACT-B-01 Visitor` | `UC-B-01 Assistierte Kaffeemaschinenbedienung mit Vivian` | `interactsWith` | Zulaessig, weil `Actor -- UseCase` beidseitig `0..*` erlaubt und `Visitor` die primaere externe Rolle des Use Case ist. |

## Angelegte Agent-/Entity-Instanz fuer Vivian

| Instanz-ID | Metamodellklasse | `uuid` | `shortName` | `Entity.kind` | Rolle im Use Case | `playsActor` | Abgrenzung |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ENT-B-01` | `Agent` und damit `Entity` | `ENT-B-01` | `VivianAssistant` | `agent` | Modellierte Assistenzinstanz in der virtuellen Szene; fuehrt, bestaetigt, fragt nach, erklaert Fehler und meldet Abschluss fachlich zurueck. | leer in der Baseline | Kein primaerer Actor, keine externe Rolle und keine RuntimeAction. Technische KI-, Sprach-, Avatar- oder Controllerdetails liegen spaeter nur unter `RuntimeBinding -> RuntimeAction`. |

`ENT-B-01 VivianAssistant` darf in `StateAssertion.subjectRef`, `Event.expression`, `Condition.expression` und spaeter in Capability-Kontexten referenziert werden. Vivian wird aber nicht direkt in `ScenarioStep.performedBy` eingetragen, solange der jeweilige Schritt `systemResponse` ist.

## Zuordnung zu bestehenden und vorbereiteten Schritten

| Schrittkategorie | Betroffene Schritte | `performedBy` | Begruendung |
| --- | --- | --- | --- |
| Benutzerabsicht im Hauptpfad | `B-MAIN-S01`, `B-MAIN-S04`, `B-MAIN-S07`, `B-MAIN-S09`, `B-MAIN-S14` | `ACT-B-01 Visitor` | Diese Schritte sind `actorIntent` und beschreiben eine externe Benutzerabsicht oder Bedienhandlung. |
| Benutzerkorrektur in Alternative | `B-ALT-S03` | `ACT-B-01 Visitor` | Die Tassenkorrektur ist eine externe Benutzerhandlung im korrigierbaren Alternativpfad. |
| Vivian-Fuehrung und Vivian-Rueckmeldung | `B-MAIN-S02`, `B-MAIN-S03`, `B-MAIN-S06`, `B-MAIN-S10`, `B-MAIN-S13`, `B-MAIN-S20`, `B-ALT-S02`, `B-EX-S02`, `B-EX-S04` | leer | Vivian ist Agent/Entity im System; diese Schritte bleiben `systemResponse` und werden spaeter ueber Capabilities beschrieben. |
| Systemische Pruefung und Startausloesung | `B-MAIN-S11`, `B-MAIN-S15` | leer | Diese Schritte sind fachliche Systemreaktionen. Die verantwortlichen Capabilities und technischen Bindungen werden erst in Task 8.8 bis 8.11 angelegt. |
| Objektbeobachtungen | `B-MAIN-S05`, `B-MAIN-S08`, `B-MAIN-S12`, `B-MAIN-S16`, `B-MAIN-S17`, `B-MAIN-S18`, `B-MAIN-S19`, `B-ALT-S01`, `B-ALT-S04`, `B-EX-S01`, `B-EX-S03` | leer | Objektzustaende sind `environmentObservation`; sie werden ueber `Event`, `Condition` und `StateAssertion` modelliert, nicht ueber Actor- oder Agent-`performedBy`. |

## Rollen- und Instanztrennung

| Frage | Entscheidung | Begruendung |
| --- | --- | --- |
| Ist der Visitor ein Actor? | Ja. | Der Visitor liegt ausserhalb des betrachteten Systems und bringt Hilfewunsch, Bedienhandlung und Startbestaetigung ein. |
| Ist der Visitor ein Agent? | Nein in der Baseline. | Der Use Case benoetigt keine eigene ausfuehrende Benutzer-Entity. Falls ein Avatarzustand relevant wird, kann spaeter eine separate `Entity` wie `VisitorEmbodiment` ergaenzt werden. |
| Ist Vivian ein Actor? | Nein in der Baseline. | Vivian liegt innerhalb der assistierten VR-Interaktion und ist kein externer Nutzer des Systems. |
| Ist Vivian ein Agent? | Ja. | Vivian kann fachlich fuehren, rueckfragen, bestaetigen, erklaeren und Abschluss rueckmelden. |
| Kann Vivian jemals Actor sein? | Nur bei anderer Systemgrenze. | Wenn das betrachtete System ausschliesslich die Kaffeemaschinensteuerung waere und Vivian als externer Assistenzdienst auftraete, koennte eine Actor-Rolle `VivianAssistantRole` eingefuehrt werden. Das ist nicht die aktuelle Baseline. |

## Nicht instanziierte Kandidaten

| Kandidat | Entscheidung | Begruendung | Spaetere Modellierungsstelle |
| --- | --- | --- | --- |
| `ACT-B-02 VivianAssistantRole` | Nicht instanziiert. | Vivian ist in der aktuellen Systemgrenze kein externer Actor, sondern `ENT-B-01 VivianAssistant` als Agent/Entity. | Nur bei geaenderter Systemgrenze oder separatem Use Case fuer eine externe Assistenzschnittstelle. |
| `ENT-B-05 VisitorEmbodiment` | Nicht instanziiert. | Der aktuelle Ablauf braucht die Benutzerrolle als Actor, aber keinen modellierten Avatarzustand des Benutzers. | Moeglich, falls spaeter Hand-, Blick-, Position- oder Avatarzustaende validiert werden muessen. |
| `ACT-B-03 TrainingSupervisor` | Nicht instanziiert. | Trainings- oder Supervisionsverhalten ist kein Teil der aktuellen Baseline von `UC-B-01`. | Moeglicher Extend-UseCase oder separater Trainings-UseCase. |
| `ACT-B-04 CoffeeMachine` | Nicht instanziiert. | Die Kaffeemaschine ist keine externe Rolle. Sie wird in Task 8.4 als fachliche Entity behandelt. | Task 8.4 `Kaffeemaschine als fachliche Entitaet modellieren`. |

## Konsequenz fuer Task 8.6

Wenn die ScenarioStep-Instanzen fuer B angelegt werden, gilt folgende Setzregel:

| `ScenarioStep.kind` | `performedBy`-Regel |
| --- | --- |
| `actorIntent` | Setze `performedBy = ACT-B-01 Visitor`, falls der Schritt eine Visitor-Handlung ist. |
| `systemResponse` | Lasse `performedBy` leer; nutze spaeter `CapabilityUse -> Capability`. |
| `environmentObservation` | Lasse `performedBy` leer; nutze Events, Conditions und StateAssertions. |

Damit bleibt `performedBy` eine Referenz auf externe Rollen und wird nicht als allgemeines Feld fuer ausfuehrende Instanzen missbraucht.

## Abnahmekontrolle

| Kriterium aus Task 8.3 | Erfuellung |
| --- | --- |
| Actor-/Agent-Mapping vorhanden | `ACT-B-01 Visitor` und `ENT-B-01 VivianAssistant` sind angelegt und voneinander getrennt. |
| Benutzerrolle als Actor modelliert | `ACT-B-01 Visitor` ist Actor und interagiert mit `UC-B-01`. |
| Vivian als Agent/Entity modelliert | `ENT-B-01 VivianAssistant` ist Agent und damit Entity mit `Entity.kind = agent`. |
| Rollen und ausfuehrende Instanzen getrennt | Visitor ist externe Rolle; Vivian ist modellierte Assistenzinstanz. |
| Vivian nicht faelschlich als Actor instanziiert | `ACT-B-02 VivianAssistantRole` wird in der Baseline explizit nicht instanziiert. |
| `performedBy`-Regel vorbereitet | Nur `actorIntent`-Schritte erhalten `ACT-B-01 Visitor`; Vivian- und Systemschritte bleiben ohne `performedBy`. |
| Keine technische Direktkopplung | Vivian enthaelt keine API-, Tool-, Topic-, Controller- oder RuntimeAction-Daten. |
| Folge-Tasks nicht vorweggenommen | Kaffeemaschine, Scenarios, Steps, Capabilities, Runtime und Validation bleiben fuer Task 8.4 bis 8.12 offen. |

## Konsequenz fuer Task 8.4

Task 8.4 kann nun die Kaffeemaschine als fachliche Entitaet modellieren. Dabei muss analog zu Vivian und Visitor strikt getrennt werden zwischen Objektzustand, Interaktionsobjektrolle und technischer Runtime-Ansteuerung.
