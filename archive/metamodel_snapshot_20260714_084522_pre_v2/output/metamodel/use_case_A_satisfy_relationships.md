# Anwendungsfall A: Satisfy-Beziehungen

Stand: 2026-07-07

Task: 4.4 `Satisfy-Beziehungen fuer A pruefen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

`Satisfy` verbindet entweder Requirements oder UseCases mit erfuellenden Modellelementen. Eine einzelne `Satisfy`-Instanz darf nicht gleichzeitig `satisfiedRequirement` und `satisfiedUseCase` belegen.

Fuer Anwendungsfall A wird deshalb jede Requirement-Zuordnung als eigene `Satisfy`-Instanz mit belegtem `satisfiedRequirement` angelegt. Der UseCase-Bezug wird separat als eigene `Satisfy`-Instanz mit belegtem `satisfiedUseCase` modelliert.

`satisfiedBy` zeigt nur auf identifizierbare Modellteile. Conditions, Events und StateAssertions werden hier als Nachweisstellen angegeben, aber nicht als primaere `satisfiedBy`-Ziele verwendet, weil die aktuelle kompakte Metamodellfassung diese Elemente nicht als `TraceableSpecification` ausweist. Die formal zu instanziierenden Scenarios und ScenarioSteps werden ueber ihre stabilen IDs referenziert und in den folgenden Tasks 4.5 bis 4.9 detailliert angelegt.

## Requirement-Satisfy-Instanzen

| Satisfy-ID | `satisfiedRequirement` | `satisfiedUseCase` | `satisfiedBy` | Nachweisstellen | XOR-Bewertung |
| --- | --- | --- | --- | --- | --- |
| `SAT-A-REQ-001` | `A-REQ-001` | leer | `UC-A-01`; `A-MAIN-SC01`; `A-ALT-SC01`; `A-EX-SC01` | UseCase-Text, Ziel und vorbereitete Scenarios | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-002` | `A-REQ-002` | leer | `A-MAIN-S01` | `A-E1`; `A-GUARD-S01` | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-003` | `A-REQ-003` | leer | `A-MAIN-S02` | `A-GUARD-S02`; `A-SA-S02-01`; `A-SA-S02-02` | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-004` | `A-REQ-004` | leer | `A-MAIN-S03` | `A-GUARD-S03`; `A-SA-S03-01`; `A-SA-S03-02` | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-005` | `A-REQ-005` | leer | `A-MAIN-S04`; `A-ALT-SC01`; `A-EX-SC01` | `A-GUARD-S04`; `A-SA-S04-01`; `A-SA-S04-02`; `A-ALT-R01`; `A-EX-R01` | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-006` | `A-REQ-006` | leer | `A-MAIN-S05` | `A-GUARD-S05`; `A-SA-S05-01`; `A-SA-S05-02` | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-007` | `A-REQ-007` | leer | `A-MAIN-S06` | `A-GUARD-S06`; `A-SA-S06-01`; `A-SA-S06-02` | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-008` | `A-REQ-008` | leer | `A-MAIN-S07` | `A-SA-S07-01`; `A-SA-S07-02` | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-009` | `A-REQ-009` | leer | `A-MAIN-S08` | `A-E7`; `A-GUARD-S08`; `A-SA-S08-01`; `A-SA-S08-02` | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-010` | `A-REQ-010` | leer | `A-MAIN-S09` | `A-E8`; `A-GUARD-S09`; `A-SA-S09-01`; `A-SA-S09-02` | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-011` | `A-REQ-011` | leer | `A-ALT-SC01` | `A-ALT-S01`; `A-ALT-S02`; `A-ALT-R01`; `A-ALT-R02`; `A-ALT-R03` | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-012` | `A-REQ-012` | leer | `A-EX-SC01` | `A-EX-S01`; `A-EX-S02`; `A-EX-S03`; `A-EX-R01`; `A-EX-R02`; `A-EX-R03` | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-013` | `A-REQ-013` | leer | `A-MAIN-SC01`; `A-ALT-SC01`; `A-EX-SC01` | keine ScenarioStep-zu-RuntimeAction-Direktkante in den A-Artefakten; technische Bindung bleibt fuer 4.10 bis 4.14 reserviert | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-014` | `A-REQ-014` | leer | `A-MAIN-SC01`; `A-ALT-SC01`; `A-EX-SC01` | Parallelitaetsentscheidung: keine `ParallelGroup` fuer A | gueltig: nur Requirement-Zweig belegt |
| `SAT-A-REQ-015` | `A-REQ-015` | leer | `UC-A-01`; `ACT-A-01`; `ACT-A-02`; `ACT-A-03`; `A-MAIN-SC01`; `A-ALT-SC01`; `A-EX-SC01` | Requirements-, UseCase-, Actor-, Scenario- und Satisfy-Artefakte bilden die Trace-Basis; Validation folgt in 4.15 | gueltig: nur Requirement-Zweig belegt |

## UseCase-Satisfy-Instanz

| Satisfy-ID | `satisfiedRequirement` | `satisfiedUseCase` | `satisfiedBy` | Nachweisstellen | XOR-Bewertung |
| --- | --- | --- | --- | --- | --- |
| `SAT-A-UC-001` | leer | `UC-A-01` | `A-MAIN-SC01`; `A-ALT-SC01`; `A-EX-SC01` | Der UseCase wird durch genau einen Main-Scenario-Pfad plus Alternative und Exception operationalisiert. | gueltig: nur UseCase-Zweig belegt |

## Kompakte Pruefung der XOR-Regel

| Prueffrage | Ergebnis |
| --- | --- |
| Gibt es eine `Satisfy`-Instanz mit gleichzeitig belegtem `satisfiedRequirement` und `satisfiedUseCase`? | nein |
| Hat jede Requirement-Zuordnung ein leeres `satisfiedUseCase`? | ja |
| Hat die UseCase-Zuordnung ein leeres `satisfiedRequirement`? | ja |
| Hat jede `Satisfy`-Instanz mindestens ein `satisfiedBy`-Element? | ja |
| Werden technische RuntimeActions direkt als `satisfiedBy` genutzt? | nein |

## Warum keine Sammelinstanz fuer alle Requirements?

Die Kardinalitaet erlaubt zwar grundsaetzlich `satisfiedRequirement [0..*]`, solange `satisfiedUseCase` leer bleibt. Fuer die Dissertation ist jedoch eine einzelne `Satisfy`-Instanz pro Requirement praeziser:

- Jede Anforderung bleibt separat pruefbar.
- Eine fehlende oder schwache Erfuellung laesst sich isolieren.
- Die XOR-Regel ist pro Zeile unmittelbar lesbar.
- Spaetere ValidationCases koennen einfacher an einzelne Requirements rueckgebunden werden.

## Offene Formalisierung fuer Folgetasks

| Elementgruppe | Status nach Task 4.4 | Folgetask |
| --- | --- | --- |
| `Scenario`-Instanzen | IDs referenziert, formale Instanzen folgen | 4.5 |
| `ScenarioStep`-Instanzen | IDs referenziert, formale Instanzen folgen | 4.6 |
| `Condition`- und `Event`-Instanzen | als Nachweisstellen referenziert, formale Einordnung folgt mit Steps | 4.7 und 4.8 |
| `StateAssertion`-Instanzen | als Nachweisstellen referenziert, formale Instanzen folgen | 4.9 |
| `CapabilityUse`, `Capability`, `Effect`, `RuntimeBinding`, `RuntimeAction` | nicht vorweggenommen | 4.10 bis 4.14 |
| `ValidationCase` | nicht vorweggenommen | 4.15 |

## Abnahmekontrolle

| Kriterium aus Task 4.4 | Erfuellung |
| --- | --- |
| Zuordnung Requirement zu erfuellenden Elementen vorhanden | `SAT-A-REQ-001` bis `SAT-A-REQ-015` decken alle A-Requirements ab. |
| Zuordnung UseCase zu erfuellenden Elementen vorhanden | `SAT-A-UC-001` ordnet `UC-A-01` den vorbereiteten Scenarios zu. |
| XOR-Regel eingehalten | Keine Zeile belegt gleichzeitig `satisfiedRequirement` und `satisfiedUseCase`. |
| `satisfiedBy [1..*]` eingehalten | Jede Satisfy-Instanz besitzt mindestens ein erfuellendes Element. |
| Keine technische Kurzschaltung | Keine Satisfy-Instanz referenziert RuntimeAction, API, Topic oder Controlleraktion direkt. |
| Folgetasks nicht unzulaessig vorweggenommen | Scenarios, Steps, Conditions, StateAssertions, Capabilities, Runtime und Validation bleiben formal in ihren eigenen Tasks. |

## Konsequenz fuer Task 4.5

Task 4.5 kann nun die Scenario-Instanzen `A-MAIN-SC01`, `A-ALT-SC01` und `A-EX-SC01` formal anlegen. Dabei sollte geprueft werden, ob die in `SAT-A-REQ-*` und `SAT-A-UC-001` referenzierten Scenario-IDs exakt uebernommen werden.
