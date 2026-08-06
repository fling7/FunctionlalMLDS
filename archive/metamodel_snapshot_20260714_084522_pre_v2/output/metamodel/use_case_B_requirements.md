# Anwendungsfall B: Requirement-Instanzen

Stand: 2026-07-07

Task: 8.1 `Requirements fuer B anlegen`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

## Modellierungsregel

Dieser Task legt nur Requirement-Instanzen fuer Anwendungsfall B an. Jede Requirement-Instanz besitzt:

- eine eindeutige ID,
- einen pruefbaren Requirement-Text,
- eine Prioritaet,
- eine fachliche Begruendung,
- eine vorlaeufige Verifikationsidee.

`Satisfy`-Beziehungen werden hier noch nicht angelegt. Sie werden spaeter aus den Mapping-Artefakten abgeleitet, damit die XOR-Regel fuer `Satisfy` sauber pruefbar bleibt.

Requirements bleiben fachlich. Sie duerfen technische Begriffe nur zur Abgrenzung nennen, aber keine direkte RuntimeAction, API, Topic, Tool- oder Controller-Aktion als ScenarioStep-Ziel fordern.

## Requirement-Liste

| Requirement-ID | Name | Requirement-Text | Prioritaet | Begruendung | Vorlaeufige Verifikation |
| --- | --- | --- | --- | --- | --- |
| `B-REQ-001` | Fachlicher Use Case | Das System muss die assistierte Kaffeemaschinenbedienung mit Vivian als fachlichen Use Case mit Ziel, primaerem Actor, beteiligtem Agent, Interaktionsobjekt und Szenarien beschreiben koennen. | muss | Der Anwendungsfall darf nicht auf einen technischen Startaufruf reduziert werden. | Pruefen, ob `UC-B-01` mit `ACT-B-01 Visitor`, `ENT-B-01 VivianAssistant`, `ENT-B-02 CoffeeMachine` und Szenarien existiert. |
| `B-REQ-002` | Rollen- und Instanztrennung | Das Modell muss die externe Benutzerrolle vom ausfuehrenden Assistenzagenten trennen: `Visitor` ist Actor, Vivian ist Agent/Entity. | muss | Actor und Agent duerfen nicht vermischt werden, sonst wird die Use-Case-Semantik unklar. | Pruefen, ob nur Visitor-Schritte `actorIntent` mit `performedBy = ACT-B-01 Visitor` nutzen und Vivian-Schritte `systemResponse` bleiben. |
| `B-REQ-003` | Assistenzstart | Das Hauptszenario muss durch einen fachlichen Hilfewunsch des Visitors gestartet werden koennen. | muss | Der assistierte Pfad beginnt nicht beliebig, sondern durch eine Benutzerabsicht. | Pruefen, ob `B-MAIN-S01` durch `B-E01` und `B-MAIN-G01 helpRequested = true` abgedeckt ist. |
| `B-REQ-004` | Vivian-Fuehrungsmodus | Nach dem Hilfewunsch muss Vivian in einen Fuehrungsmodus wechseln und fuer die Bedienung wahrnehmbare Hinweise geben koennen. | muss | Ohne Vivian-Fuehrung waere der Use Case nicht die assistierte Bedienung mit Vivian. | Pruefen, ob `SA-B-VIVIAN-GUIDING`, `SA-B-VIVIAN-GUIDANCE-CUP` und `SA-B-VIVIAN-GUIDANCE-PROGRAM` existieren. |
| `B-REQ-005` | Tassenbedingung | Das Modell muss vor dem Bruehstart pruefbar machen, ob eine Tasse vorhanden ist. | muss | Ein sicherer Bruehstart setzt die Tasse als fachliche Voraussetzung voraus. | Pruefen, ob `CoffeeMachine.cupPresent = true` als Condition und `SA-B-CM-CUP-PRESENT` als StateAssertion modelliert sind. |
| `B-REQ-006` | Korrigierbare fehlende Tasse | Das Modell muss eine fehlende Tasse als korrigierbare Alternative mit Rueckkehr in den Hauptpfad beschreiben koennen. | muss | Eine fehlende Tasse ist im Beispiel kein fataler Fehler, sondern durch Benutzerhandlung behebbar. | Pruefen, ob `SC-B-01-ALT01` mit `Scenario.kind = alternative`, Einstieg bei `B-MAIN-S05` und Rueckkehr zu `B-MAIN-S06` existiert. |
| `B-REQ-007` | Programmauswahl | Das Modell muss vor der Startanforderung eine fachlich gesetzte Programmauswahl nachweisen koennen. | muss | Der Bruehstart ist nur sinnvoll, wenn das Getraenk beziehungsweise Programm festgelegt ist. | Pruefen, ob `CoffeeMachine.selectedProgram = coffee`, `SA-B-CM-PROGRAM-COFFEE` und `B-MAIN-G04` existieren. |
| `B-REQ-008` | Bruehanforderung | Das Modell muss den Startwunsch des Visitors als fachlichen Request abbilden koennen. | muss | Der Bruehstart muss auf eine nachvollziehbare Benutzerabsicht zurueckgehen. | Pruefen, ob `B-MAIN-S09`, `B-E07`, `SA-B-BREWING-REQUESTED` und `B-MAIN-G05` existieren. |
| `B-REQ-009` | Bereitschaftspruefung | Vor dem assistierten Bruehstart muss eine Bereitschaftspruefung die relevanten Startbedingungen fachlich pruefen. | muss | Die Maschine darf nicht starten, wenn Wasser, Tasse, Programm oder sicherer Zustand fehlen. | Pruefen, ob `B-MAIN-S11`, `B-MAIN-G06`, `SA-B-CM-READY`, `SA-B-CM-START-PERMISSION` und die zugehoerigen Conditions existieren. |
| `B-REQ-010` | Explizite Startbestaetigung | Das Modell muss vor dem assistierten Start eine explizite Bestaetigung des Visitors nach Vivians Rueckfrage verlangen. | muss | Assistiertes Ausloesen einer Objektfunktion braucht eine klare Benutzerfreigabe. | Pruefen, ob `B-MAIN-S13`, `B-MAIN-S14`, `B-E10`, `B-E11`, `B-MAIN-G07` und `SA-B-BREWING-CONFIRMED` existieren. |
| `B-REQ-011` | Start nur bei Freigabe | Das System darf den Bruehstart fachlich nur ausloesen, wenn die Bereitschaftspruefung bestanden ist, Startpermission erlaubt ist und die Benutzerbestaetigung vorliegt. | muss | Der assistierte Start darf nicht an Conditions vorbeigehen. | Pruefen, ob `B-MAIN-G08`, `SA-B-BREWING-START-ISSUED` und `SA-B-CM-BREWING` nur nach den Freigabebedingungen erreichbar sind. |
| `B-REQ-012` | Beobachtbarer Bruehzustand | Nach dem fachlichen Start muss der Bruehvorgang als beobachtbarer Zustand der Kaffeemaschine modelliert werden. | muss | Erfolg darf nicht nur behauptet werden; die Maschine muss einen pruefbaren Zustand besitzen. | Pruefen, ob `B-MAIN-S16` und `SA-B-CM-BREWING` existieren. |
| `B-REQ-013` | Fortschritt und Abschluss | Das Modell muss Bruehfortschritt, abgeschlossenen Maschinenzustand und Abschlussfeedback als getrennte beobachtbare Aussagen abbilden koennen. | muss | Fortschritt, Abschlusszustand und Benutzerfeedback sind unterschiedliche Nachweise. | Pruefen, ob `SA-B-CM-PROGRESS-VISIBLE`, `SA-B-CM-FINISHED`, `SA-B-CM-COMPLETION-FEEDBACK` und `SA-B-VIVIAN-COMPLETION-REPORTED` existieren. |
| `B-REQ-014` | Exception bei fehlender Bereitschaft | Das Modell muss eine fehlgeschlagene Bereitschaftspruefung als Exception ohne Rueckkehr in den Hauptpfad beschreiben koennen. | muss | Ein nicht korrigierbarer Bereitschaftsfehler darf nicht als erfolgreicher Bruehstart modelliert werden. | Pruefen, ob `SC-B-01-EX01` mit `Scenario.kind = exception`, Einstieg nach `B-MAIN-S11` und ohne Rueckkehr zu `B-MAIN-S12` existiert. |
| `B-REQ-015` | Sicherer Exception-Abschluss | Eine Exception muss in einem sicheren und erklaerbaren Zustand enden. | muss | Bei fehlender Startbereitschaft muss das System blockieren und Vivian muss die Ursache erklaeren. | Pruefen, ob `SA-B-CM-SAFE`, `SA-B-CM-START-BLOCKED`, `SA-B-CM-NOT-BREWING` und `SA-B-VIVIAN-ERROR-EXPLAINED` existieren. |
| `B-REQ-016` | Include/Extend-Semantik | Das Modell muss Pflichtverhalten, optionale Zusatzablaeufe, Alternativen und Exceptions semantisch unterscheiden. | soll | Include und Extend duerfen nicht als allgemeine Verzweigungsmechanik missbraucht werden. | Pruefen, ob `use_case_B_include_extend_decision.md` kein unvollstaendiges Include/Extend anlegt und Kandidaten sauber begruendet. |
| `B-REQ-017` | Keine technische Kurzschaltung | Ein `ScenarioStep` darf keine direkte technische RuntimeAction, API, Topic, Tool- oder Controlleraktion referenzieren. | muss | Fachlicher Ablauf und technische Ausfuehrung muessen getrennt bleiben. | Pruefen, ob technische Aktionen erst spaeter ueber `CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction` vorkommen. |
| `B-REQ-018` | Traceability und Validierung | Alle zentralen Elemente des B-Anwendungsfalls muessen spaeter auf Requirements, UseCase, Scenarios, ScenarioSteps, Events, Conditions, StateAssertions, Capabilities und ValidationCases zurueckfuehrbar sein. | soll | Die Modellierung muss fuer wissenschaftliche Nachvollziehbarkeit und spaetere Validierung belastbar sein. | In den folgenden Tasks pruefen, ob Requirements in UseCase-, Scenario-, Capability- und ValidationCase-Artefakten referenzierbar bleiben. |

## Minimaler Requirement-Satz fuer den ersten B-Mapping-Durchlauf

Die folgenden Requirements sind fuer das erste vollstaendige Mapping zwingend:

- `B-REQ-001`
- `B-REQ-002`
- `B-REQ-003`
- `B-REQ-004`
- `B-REQ-005`
- `B-REQ-007`
- `B-REQ-008`
- `B-REQ-009`
- `B-REQ-010`
- `B-REQ-011`
- `B-REQ-012`
- `B-REQ-013`
- `B-REQ-014`
- `B-REQ-015`
- `B-REQ-017`

`B-REQ-006`, `B-REQ-016` und `B-REQ-018` sind ebenfalls fachlich wichtig, koennen aber in der Priorisierung als `soll` beziehungsweise als zweite Validierungsstufe behandelt werden, falls ein kleinerer Demonstrationsumfang benoetigt wird.

## Noch nicht angelegte Beziehungen

| Beziehung | Status | Begruendung |
| --- | --- | --- |
| `Satisfy` von Requirements zu erfuellenden Elementen | offen | Die XOR-Regel soll erst mit konkreten UseCase-, Capability- und ValidationCase-Instanzen geprueft werden. |
| `ValidationCase` zu Requirements | offen bis Task 8.12 | ValidationCases werden spaeter als eigene Instanzen angelegt. |
| `RuntimeBinding` oder `RuntimeAction` | offen bis Task 8.10 und 8.11 | Requirements bleiben fachlich und enthalten keine technischen Bindungen. |
| Vollstaendige Kardinalitaetspruefung | offen bis Task 8.13 | Erst nach den B-Mapping-Instanzen kann die Gesamtpruefung belastbar erfolgen. |

## Abnahmekontrolle

| Kriterium aus Task 8.1 | Erfuellung |
| --- | --- |
| Requirementliste vorhanden | `B-REQ-001` bis `B-REQ-018` sind angelegt. |
| Jedes Requirement hat eine eindeutige ID | Jede Tabellenzeile besitzt genau eine stabile Requirement-ID. |
| Jedes Requirement hat pruefbaren Text | Jeder Requirement-Text enthaelt ein pruefbares Muss- oder Soll-Ziel. |
| Jede Anforderung hat vorlaeufige Verifikation | Jede Zeile nennt ein konkretes Artefakt oder einen konkreten Modellzustand zur Pruefung. |
| Requirements sind fachlich formuliert | Die Anforderungen beschreiben Modell- und Ablaufverhalten, keine Implementierungsbefehle. |
| Satisfy nicht vorweggenommen | Satisfy-Beziehungen werden explizit offengelassen. |
| Keine technische Kurzschaltung | Technische Begriffe erscheinen nur zur Abgrenzung, nicht als direkte ScenarioStep-Ziele. |

## Konsequenz fuer Task 8.2

Task 8.2 kann nun die UseCase-Instanz `UC-B-01` mit Ziel und Text anlegen und dabei auf diese Requirements Bezug nehmen, ohne bereits `Satisfy`-Beziehungen zu erzeugen.
