# Anwendungsfall B: UseCase-Instanz

Stand: 2026-07-07

Task: 8.2 `UseCase-Instanz fuer B anlegen`

## UseCase-Instanz

| Attribut / Beziehung | Wert |
| --- | --- |
| Instanz-ID | `UC-B-01` |
| Metamodellklasse | `UseCase` |
| `uuid` | `UC-B-01` |
| `shortName` | `AssistierteKaffeemaschinenbedienungMitVivian` |
| Anzeigename | `Assistierte Kaffeemaschinenbedienung mit Vivian` |
| `text` | Der Use Case beschreibt die fachliche Bedienung einer virtuellen Kaffeemaschine durch eine Benutzerrolle mit Vivian als Assistenzagent. Der Visitor fordert Hilfe an, Vivian fuehrt durch die Bedienung, das Interaktionsobjekt meldet beobachtbare Zustaende, das System prueft die Startbereitschaft, der Visitor bestaetigt den assistierten Start, und der Ablauf endet entweder mit einem pruefbaren Brueh- und Abschlusszustand oder mit einem sicheren und erklaerten Abbruch. |
| `formalism` | `FunctionalMLDS` |
| `goal` | Eine virtuelle Kaffeemaschine so assistiert bedienen, dass Benutzerabsicht, Vivian-Fuehrung, Objektzustand, Startfreigabe, Bruehstart und Abschluss fachlich nachvollziehbar, pruefbar und ohne direkte Runtime-Kopplung modelliert sind. |
| Primaerer Actor-Kandidat | `ACT-B-01 Visitor` |
| Fachlich beteiligter Agent-Kandidat | `ENT-B-01 VivianAssistant` |
| Zentrales Interaktionsobjekt | `ENT-B-02 CoffeeMachine` |
| Weitere fachliche Entitaeten im Kontext | `ENT-B-03 Cup`, `ENT-B-04 BrewingRequest` |
| Requirements im Kontext | `B-REQ-001` bis `B-REQ-018` |
| Scenarios im Kontext | `SC-B-01-MAIN`, `SC-B-01-ALT01`, `SC-B-01-EX01` |
| ExtensionPoints | keine formale Instanz in der aktuellen Baseline |
| Include-Beziehungen | keine formale Instanz in der aktuellen Baseline |
| Extend-Beziehungen | keine formale Instanz in der aktuellen Baseline |

## Fachlicher UseCase-Text

`UC-B-01` beschreibt nicht das technische Starten einer Kaffeemaschine, sondern die fachliche, assistierte Bedienung eines Interaktionsobjekts in einer virtuellen Szene. Der Visitor verfolgt das Ziel, mit Vivians Unterstuetzung einen Kaffeevorgang auszufuehren. Vivian ist dabei kein externer Actor, sondern ein im System modellierter Assistenzagent, der Hinweise gibt, Rueckfragen stellt, erklaert und den Ablauf fachlich begleitet.

Der erfolgreiche Hauptpfad beginnt mit dem Hilfewunsch des Visitors. Vivian wechselt in den Fuehrungsmodus, fuehrt den Visitor zur Tassenplatzierung und Programmauswahl, bestaetigt die erkannte Bruehanforderung und fordert vor dem Start eine explizite Bestaetigung an. Das System prueft vorher die Bedienbereitschaft der Kaffeemaschine. Erst wenn Tasse, Programm, Bereitschaft und Benutzerbestaetigung fachlich vorliegen, wird der Bruehvorgang als fachliche Systemreaktion gestartet. Danach werden Bruehzustand, Fortschritt, Abschlusszustand und Vivian-Rueckmeldung getrennt beobachtbar.

Der Use Case umfasst ausserdem einen korrigierbaren alternativen Ablauf bei fehlender Tasse und einen Exception-Ablauf bei fehlgeschlagener Bereitschaftspruefung. Die Alternative fuehrt nach erfolgreicher Korrektur zurueck in den Hauptpfad. Die Exception startet keinen Bruehvorgang, sondern endet in einem sicheren und fuer den Visitor erklaerten Zustand.

## Warum das eine Nutzung des Systems ist

| Kriterium | Bewertung |
| --- | --- |
| Externe Rolle vorhanden | `ACT-B-01 Visitor` liefert die Bedienabsicht, nimmt Vivians Hinweise auf und bestaetigt den assistierten Start. |
| Fachliches Ziel vorhanden | Der Use Case beschreibt eine vollstaendige assistierte Bedienhandlung mit beobachtbarem Maschinen- und Rueckmeldezustand. |
| Systemleistung beschrieben | Das System strukturiert Benutzerhandlung, Vivian-Fuehrung, Objektzustand, Bereitschaftspruefung, Startfreigabe und Ergebnisbeobachtung. |
| Agent und Actor getrennt | Vivian wird als fachlich beteiligter `Agent`/`Entity` vorbereitet; der Visitor bleibt primaerer Actor. |
| Interaktionsobjekt getrennt | Die Kaffeemaschine wird als fachliche Entitaet mit Zustandsaussagen vorbereitet, nicht als technische Aktion. |
| Nicht nur technische Aktion | Der Use Case nennt keinen Controller, keine API, kein Topic, kein Tool und keine RuntimeAction als Ziel. |
| Szenarien anschliessbar | Haupt-, Alternativ- und Exception-Szenario sind bereits fachlich vorbereitet und koennen spaeter als `Scenario`-Instanzen angelegt werden. |

## Vorgesehene Scenarios

| Scenario-ID | `Scenario.kind` | Name | Anschluss |
| --- | --- | --- | --- |
| `SC-B-01-MAIN` | `main` | `Assistierte Kaffeemaschinenbedienung erfolgreich ausfuehren` | Erfolgreicher Ablauf von `B-MAIN-S01` bis `B-MAIN-S20`. |
| `SC-B-01-ALT01` | `alternative` | `Fehlende Tasse korrigieren` | Einstieg nach `B-MAIN-S05`, Rueckkehr vor `B-MAIN-S06`. |
| `SC-B-01-EX01` | `exception` | `Bereitschaftspruefung schlaegt fehl` | Einstieg nach `B-MAIN-S11`, kein Ruecksprung in den Hauptpfad. |

Die formalen Scenario-Instanzen werden in Task 8.5 angelegt. Diese UseCase-Instanz dokumentiert nur, welche Szenarien fachlich zu `UC-B-01` gehoeren sollen.

## Requirement-Abdeckung auf UseCase-Ebene

| Requirement | Beitrag dieser UseCase-Instanz |
| --- | --- |
| `B-REQ-001` | `UC-B-01` beschreibt Ziel, primaeren Actor-Kandidaten, Vivian als Agent-Kandidaten, Kaffeemaschine als Interaktionsobjekt und die zugehoerigen Szenarien. |
| `B-REQ-002` | Die UseCase-Instanz trennt `ACT-B-01 Visitor` von `ENT-B-01 VivianAssistant`. |
| `B-REQ-003` bis `B-REQ-013` | Der fachliche Text fasst den erfolgreichen assistierten Hauptpfad inklusive Fuehrung, Preconditions, Startbestaetigung, Bruehzustand und Abschluss zusammen. |
| `B-REQ-014` bis `B-REQ-015` | Der Exception-Ablauf bei fehlgeschlagener Bereitschaft wird als sicherer und erklaerter Nicht-Start eingeordnet. |
| `B-REQ-016` | Include und Extend werden nicht voreilig instanziiert; Kandidaten bleiben in der Include/Extend-Entscheidung dokumentiert. |
| `B-REQ-017` | Die UseCase-Instanz vermeidet technische Direktkopplung. Technische Ausfuehrung bleibt spaeteren RuntimeBinding- und RuntimeAction-Tasks vorbehalten. |
| `B-REQ-018` | Die Referenzen auf Requirements, Scenarios, Actor-, Agent- und Entity-Kandidaten bereiten die spaetere Trace-Kette vor. |

Diese Tabelle ist noch keine formale `Satisfy`-Instanziierung. Sie beschreibt nur, welche Requirements durch die UseCase-Instanz inhaltlich vorbereitet werden. Formale `Satisfy`-Beziehungen werden spaeter separat angelegt und gegen die XOR-Regel geprueft.

## Abgrenzung zu unzulaessigen UseCase-Deutungen

| Unzulaessige Deutung | Warum unpassend |
| --- | --- |
| `StartBrewing` | Beschreibt nur einen spaeten Schritt oder eine Capability, aber nicht die gesamte assistierte Bedienung. |
| `CoffeeMachineController.startBrewing` | Vermischt UseCase-Ebene mit technischer Ausfuehrung und waere eine RuntimeAction-nahe Formulierung. |
| `Vivian startet die Kaffeemaschine` | Verschiebt den Actor-Fokus falsch auf Vivian und unterschlaegt die explizite Benutzerbestaetigung. |
| `Kaffeemaschine brueht Kaffee` | Reduziert den Ablauf auf Objektverhalten und verliert Benutzerabsicht, Assistenz und Startfreigabe. |

## Nicht vorweggenommen

| Element | Status | Begruendung |
| --- | --- | --- |
| `Actor`-Instanzen | offen bis Task 8.3 | Die genaue Actor-/Agent-Zuordnung wird separat angelegt und begruendet. |
| `Entity`-Instanzen fuer Vivian, Kaffeemaschine, Tasse und Bruehanforderung | offen bis Task 8.3 und 8.4 | Dieser Task referenziert nur Kandidaten und legt keine vollstaendigen Entity-Instanzen an. |
| `Satisfy`-Beziehungen | offen | Die XOR-Regel wird erst spaeter mit konkreten Instanzen geprueft. |
| `Scenario`-Instanzen | offen bis Task 8.5 | Main, Alternative und Exception werden als eigene Instanzebene angelegt. |
| `ScenarioStep`-Instanzen | offen bis Task 8.6 | Die 20 Hauptpfadschritte und die Zweigschritte werden separat instanziiert. |
| `Event`, `Condition`, `StateAssertion` | offen bis Task 8.7 | Ablaufereignisse, Guards und erwartete Zustaende werden separat zusammengefuehrt. |
| `CapabilityUse`, `Capability`, `RuntimeBinding`, `RuntimeAction` | offen bis Task 8.8 bis 8.11 | Der Use Case bleibt fachlich; technische Ausfuehrung wird nur ueber die erlaubte Kette angebunden. |
| `ValidationCase` | offen bis Task 8.12 | Validierung wird spaeter als eigene Instanzebene beschrieben. |

## Abnahmekontrolle

| Kriterium aus Task 8.2 | Erfuellung |
| --- | --- |
| UseCase mit Text vorhanden | `UC-B-01` besitzt einen fachlichen UseCase-Text. |
| UseCase mit Ziel vorhanden | `UC-B-01` besitzt ein explizites `goal`. |
| UseCase beschreibt Bedienung | Der Text beschreibt assistierte Kaffeemaschinenbedienung mit Visitor, Vivian, Objektzustand und Startfreigabe. |
| Nicht bloss API-Aufruf | Der Use Case vermeidet konkrete Controller-, API-, Topic-, Tool- oder RuntimeAction-Ziele. |
| Actor/Agent-Trennung vorbereitet | Visitor und Vivian sind getrennt referenziert, aber noch nicht als Folgeinstanzen vorweggenommen. |
| Scenarios anschliessbar | Main, Alternative und Exception sind als Kontext referenziert und fuer Task 8.5 vorbereitet. |
| Keine Folge-Tasks vorweggenommen | Actor, Entity, Satisfy, Scenarios, Steps, Capabilities, Runtime und Validation bleiben fuer die vorgesehenen Tasks offen. |

## Konsequenz fuer Task 8.3

Task 8.3 kann nun die Actor- und Agent-Zuordnung fuer `UC-B-01` anlegen. Dabei ist besonders zu pruefen, dass nur die externe Benutzerrolle als `Actor` modelliert wird, waehrend Vivian als fachlich beteiligter `Agent`/`Entity` im System bleibt.
