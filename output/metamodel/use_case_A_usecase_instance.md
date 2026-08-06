# Anwendungsfall A: UseCase-Instanz

Stand: 2026-07-07

Task: 4.2 `UseCase-Instanz fuer A anlegen`

## UseCase-Instanz

| Attribut / Beziehung | Wert |
| --- | --- |
| Instanz-ID | `UC-A-01` |
| Metamodellklasse | `UseCase` |
| `uuid` | `UC-A-01` |
| `shortName` | `DynamischeAgentenreaktion` |
| Anzeigename | `Dynamisches Agentenverhalten in virtueller Szene modellieren` |
| `text` | Der Use Case beschreibt die fachliche Modellierung eines dynamischen Agentenverhaltens in einer virtuellen Szene. Ein Agent reagiert auf gueltige Ereignisse und Bedingungen, nimmt eine passende Rolle oder Handlung ein, erreicht einen pruefbaren Zielzustand und erzeugt eine beobachtbare Rueckmeldung. |
| `formalism` | `FunctionalMLDS` |
| `goal` | Dynamisches Agentenverhalten in einer virtuellen Szene so fachlich modellieren, dass ein Agent auf gueltige Ereignisse und Bedingungen reagieren, seine Rolle oder Handlung anpassen und einen pruefbaren Zielzustand der Szene erreichen kann. |
| Primaerer Actor-Kandidat | `ScenarioDesigner` |
| Weitere Actor-Kandidaten | `SceneParticipant`, `SceneObserver`, optional `ExternalEventSource`, optional `TrainingSupervisor` |
| Requirements im Kontext | `A-REQ-001` bis `A-REQ-015` |
| Scenarios im Kontext | `A-MAIN-SC01`, `A-ALT-SC01`, `A-EX-SC01` |
| ExtensionPoints | vorerst keine |
| Include-Beziehungen | vorerst keine |
| Extend-Beziehungen | vorerst keine |

## Fachlicher UseCase-Text

`UC-A-01` beschreibt, wie dynamisches Agentenverhalten in einer virtuellen Szene fachlich spezifiziert wird. Der Use Case beginnt mit einem gueltigen Ausloeseereignis, prueft relevante Bedingungen des Agenten und der Szene, modelliert Rollenwechsel und zielgerichtete Agentenhandlung, macht den erreichten Zielzustand beobachtbar und ermoeglicht eine nachvollziehbare Rueckmeldung.

Der Use Case umfasst zusaetzlich eine erlaubte Alternative bei temporaerer Blockade und eine Exception bei dauerhafter Blockade. Beide Pfade bleiben fachlich modelliert und enthalten keine technische Ausfuehrung.

## Warum das eine Nutzung des Systems ist

| Kriterium | Bewertung |
| --- | --- |
| Externe Rolle vorhanden | `ScenarioDesigner` liefert die Modellierungsabsicht; `SceneParticipant`, `SceneObserver` und `ExternalEventSource` koennen spaeter fachlich ausloesen oder beobachten. |
| Fachliches Ziel vorhanden | Der Use Case beschreibt ein modellierbares dynamisches Agentenverhalten mit pruefbarem Zielzustand. |
| Systemleistung beschrieben | Das System strukturiert Agentenverhalten, Ereignisse, Bedingungen, Szenarien und beobachtbare Zustandsaussagen. |
| Nicht nur technische Aktion | Der Use Case nennt keine konkrete Engine-Methode, API, Topic, Controlleraktion oder RuntimeAction als Ziel. |
| Szenarien anschliessbar | Haupt-, Alternativ- und Exception-Szenario sind bereits fachlich vorbereitet. |

## Vorgesehene Scenarios

| Scenario-ID | `Scenario.kind` | Name | Status |
| --- | --- | --- | --- |
| `A-MAIN-SC01` | `main` | `Agent reagiert auf gueltiges Ereignis und erreicht Zielzone` | in Abschnitt 3 ausgearbeitet |
| `A-ALT-SC01` | `alternative` | `Temporaere Blockade der Zielzone aufloesen` | in Task 3.8 ausgearbeitet |
| `A-EX-SC01` | `exception` | `Dauerhafte Blockade verhindert Zielerreichung` | in Task 3.9 ausgearbeitet |

Die formalen Scenario-Instanzen werden in Task 4.5 angelegt. Diese UseCase-Instanz dokumentiert nur, welche Scenarios fachlich zugeordnet werden sollen.

## Nicht vorweggenommen

| Element | Status | Begruendung |
| --- | --- | --- |
| `Actor`-Instanzen | offen bis Task 4.3 | Actor-Instanzen werden separat angelegt und begruendet. |
| `Satisfy`-Beziehungen | offen bis Task 4.4 | Die XOR-Regel wird dort separat geprueft. |
| `Scenario`-Instanzen | offen bis Task 4.5 | Die Szenarien werden als eigene Instanzen angelegt. |
| `CapabilityUse`, `Capability`, `RuntimeBinding`, `RuntimeAction` | offen bis Task 4.10 bis 4.14 | Der Use Case bleibt fachlich und verweist nicht direkt auf technische Ausfuehrung. |
| `ValidationCase` | offen bis Task 4.15 | Validierung wird spaeter als eigene Instanzebene erfasst. |

## Abnahmekontrolle

| Kriterium aus Task 4.2 | Erfuellung |
| --- | --- |
| UseCase mit Text vorhanden | `UC-A-01` besitzt einen fachlichen UseCase-Text. |
| UseCase mit Ziel vorhanden | `UC-A-01` besitzt ein explizites `goal`. |
| Nutzung des Systems beschrieben | Der Text beschreibt Modellierung dynamischen Agentenverhaltens mit Ereignissen, Bedingungen, Szenarien und Zielzustand. |
| Nicht nur technische Aktion | Der Use Case vermeidet konkrete Engine-, API-, Topic-, Controller- oder RuntimeAction-Ziele. |
| Keine Folge-Tasks vorweggenommen | Actor, Satisfy, Scenarios, Capabilities, Runtime und Validation bleiben fuer die vorgesehenen Tasks offen. |

## Konsequenz fuer Task 4.3

Task 4.3 kann nun die Actor-Instanzen fuer `UC-A-01` anlegen und entscheiden, welche Rollen direkt mit dem Use Case interagieren und welche nur optional oder begruendet ausgeschlossen sind.
