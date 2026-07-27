# Anwendungsfall A: Requirement-Instanzen

Stand: 2026-07-07

Task: 4.1 `Requirements fuer A anlegen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Modellierungsregel

Dieser Task legt nur Requirement-Instanzen fuer Anwendungsfall A an. Jede Requirement-Instanz besitzt:

- eine eindeutige ID,
- einen pruefbaren Requirement-Text,
- eine fachliche Begruendung,
- eine vorlaeufige Verifikationsidee.

`Satisfy`-Beziehungen werden hier noch nicht angelegt. Sie folgen in Task 4.4, damit die XOR-Regel fuer `Satisfy` sauber separat geprueft werden kann.

## Requirement-Liste

| Requirement-ID | Name | Requirement-Text | Prioritaet | Begruendung | Vorlaeufige Verifikation |
| --- | --- | --- | --- | --- | --- |
| `A-REQ-001` | Fachlicher Use Case | Das System muss dynamisches Agentenverhalten in einer virtuellen Szene als fachlichen Use Case mit Ziel und Szenarien beschreiben koennen. | muss | Der Anwendungsfall darf nicht nur technische Ausfuehrung beschreiben. | Pruefen, ob `UC-A-01` mit Text, Ziel und Scenarios existiert. |
| `A-REQ-002` | Ereignisbasierter Start | Das Hauptszenario muss durch ein gueltiges fachliches Ereignis ausgeloest werden koennen. | muss | Agentenverhalten soll auf Ereignisse reagieren, nicht beliebig starten. | Pruefen, ob `A-MAIN-S01` ein Event mit Art und Ausdruck referenziert. |
| `A-REQ-003` | Raeumliche Gueltigkeit | Das Szenario muss pruefen koennen, ob der Agent innerhalb des gueltigen Szenenbereichs ist. | muss | Agentenhandlungen ausserhalb der fachlichen Szenengrenze duerfen nicht als Erfolg gelten. | Pruefen, ob eine Condition und StateAssertion fuer `inside(AgentBody, SceneBoundary)` existieren. |
| `A-REQ-004` | Handlungsbereitschaft | Das Szenario muss pruefen koennen, ob der Agent handlungsbereit und nicht blockiert ist. | muss | Rollenwechsel und Zielhandlung setzen einen handlungsfaehigen Agenten voraus. | Pruefen, ob `AgentBody.state in {idle, waiting}` und `AgentBody.roleState != blocked` modelliert sind. |
| `A-REQ-005` | Zielerreichbarkeit | Das Szenario muss pruefen koennen, ob die Zielzone fachlich erreichbar und nicht blockiert ist. | muss | Die Zielhandlung ist nur sinnvoll, wenn das Ziel erreichbar ist. | Pruefen, ob `TargetZone.state = reachable` und `ObstacleRegion.state != blocked` als Guard modelliert sind. |
| `A-REQ-006` | Rollenwechsel | Das Szenario muss modellieren koennen, dass der Agent eine passende Ausfuehrungsrolle annimmt. | muss | Dynamisches Agentenverhalten umfasst Rollen- und Handlungswechsel. | Pruefen, ob eine StateAssertion `AgentBody.roleState = executor` existiert. |
| `A-REQ-007` | Zielgerichtete Handlung | Das Szenario muss modellieren koennen, dass der Agent eine zielgerichtete fachliche Handlung in Richtung Zielzone ausfuehrt. | muss | Ohne Handlung waere der Zielzustand nicht aus dem Ablauf erklaerbar. | Pruefen, ob `A-MAIN-S06` als systemische Agentenreaktion modelliert ist. |
| `A-REQ-008` | Beobachtbare Zielerreichung | Das Szenario muss den erreichten Zielzustand als beobachtbare Zustandsaussage modellieren koennen. | muss | Der Erfolg muss pruefbar und nicht nur behauptet sein. | Pruefen, ob `AgentBody = at(TargetZone)` und `TargetZone = reached` existieren. |
| `A-REQ-009` | Zielverifikation | Das Szenario muss den erreichten Zielzustand verifizieren koennen. | muss | Wissenschaftlich belastbare Modellierung benoetigt einen pruefbaren Abschluss. | Pruefen, ob `ObservationPoint = verified` modelliert ist. |
| `A-REQ-010` | Ergebnisrueckmeldung | Das Szenario muss eine beobachtbare Ergebnisrueckmeldung modellieren koennen. | muss | Der Abschluss soll fuer Beobachter oder System nachvollziehbar sein. | Pruefen, ob `FeedbackSignal = confirmed` modelliert ist. |
| `A-REQ-011` | Alternative bei temporaerer Blockade | Das Modell muss eine temporaere Blockade der Zielzone als Alternative mit Rueckfuehrung in den Hauptpfad beschreiben koennen. | soll | Dynamische Szenen enthalten zulaessige Abweichungen, ohne das Ziel aufzugeben. | Pruefen, ob `A-ALT-SC01` mit Einstieg, Guard und Rueckfuehrung existiert. |
| `A-REQ-012` | Exception bei dauerhafter Blockade | Das Modell muss eine dauerhafte Blockade der Zielzone als Exception mit sicherem Fehlerabschluss beschreiben koennen. | muss | Nicht erreichbare Ziele duerfen nicht als Erfolg modelliert werden. | Pruefen, ob `A-EX-SC01` ohne Rueckfuehrung und mit Fehlerzustand existiert. |
| `A-REQ-013` | Keine technische Kurzschaltung | Ein `ScenarioStep` darf keine direkte technische RuntimeAction, API, Topic oder Controlleraktion referenzieren. | muss | Fachliche Ablaufmodellierung und technische Ausfuehrung muessen getrennt bleiben. | Pruefen, ob technische Aktionen nur spaeter ueber `Capability -> RuntimeBinding -> RuntimeAction` vorkommen. |
| `A-REQ-014` | Parallelitaet nur bei Bedarf | Das Modell darf fuer Anwendungsfall A keine `ParallelGroup` anlegen, solange keine mindestens zwei nebenlaeufigen Schritte fachlich benoetigt werden. | muss | Eine kuenstliche ParallelGroup wuerde die Kardinalitaet und Semantik verzerren. | Pruefen, ob `Scenario -> ParallelGroup [0..*]` fuer A mit `0` belegt ist. |
| `A-REQ-015` | Traceability | Alle zentralen Elemente des Anwendungsfalls muessen spaeter auf Requirements, UseCase, Scenario, ScenarioSteps, Conditions, StateAssertions und Validierung zurueckfuehrbar sein. | soll | Die Dissertation braucht nachvollziehbare Modellketten. | In Task 4.4 und spaeteren Mapping-Tasks Satisfy- und Validierungsbezug pruefen. |

## Minimaler Requirement-Satz fuer den ersten Mapping-Durchlauf

Die folgenden Requirements sind fuer das erste vollstaendige Mapping zwingend:

- `A-REQ-001`
- `A-REQ-002`
- `A-REQ-003`
- `A-REQ-004`
- `A-REQ-005`
- `A-REQ-006`
- `A-REQ-007`
- `A-REQ-008`
- `A-REQ-009`
- `A-REQ-010`
- `A-REQ-012`
- `A-REQ-013`
- `A-REQ-014`

`A-REQ-011` und `A-REQ-015` sind ebenfalls fachlich wichtig, koennen aber in der Priorisierung als `soll` behandelt werden.

## Noch nicht angelegte Beziehungen

| Beziehung | Status | Begruendung |
| --- | --- | --- |
| `Satisfy` von Requirements zu erfuellenden Elementen | offen bis Task 4.4 | Die XOR-Regel soll separat geprueft werden. |
| `ValidationCase` zu Requirements | offen bis Task 4.15 | ValidationCases werden spaeter als eigene Instanzen angelegt. |
| `RuntimeBinding` oder `RuntimeAction` | offen bis Task 4.13 und 4.14 | Requirements bleiben fachlich und enthalten keine technischen Bindungen. |

## Abnahmekontrolle

| Kriterium aus Task 4.1 | Erfuellung |
| --- | --- |
| Liste von Requirement-Instanzen vorhanden | `A-REQ-001` bis `A-REQ-015` sind angelegt. |
| Jedes Requirement hat eine eindeutige ID | Jede Tabellenzeile besitzt genau eine stabile Requirement-ID. |
| Jedes Requirement hat Text | Jede Tabellenzeile enthaelt einen Requirement-Text. |
| Requirements sind fachlich | Die Texte beschreiben Anforderungen an das Modell und den Anwendungsfall, keine Implementierungsbefehle. |
| Satisfy nicht vorweggenommen | Satisfy-Beziehungen werden explizit fuer Task 4.4 offengelassen. |
| Keine technische Kurzschaltung | Requirements nennen technische Begriffe nur zur Abgrenzung, nicht als direkte ScenarioStep-Ziele. |

## Konsequenz fuer Task 4.2

Task 4.2 kann nun die UseCase-Instanz `UC-A-01` anlegen und auf diese Requirements beziehen, ohne bereits `Satisfy`-Beziehungen zu modellieren.
