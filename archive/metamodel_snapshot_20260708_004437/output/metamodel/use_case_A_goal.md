# Anwendungsfall A: Hauptziel

Stand: 2026-07-07

Task: 2.7 `Hauptziel des Anwendungsfalls A festlegen`

Zweckbezug: Der Anwendungsfall beschreibt, wie ein Agent innerhalb einer virtuellen Szene zur Laufzeit auf Ereignisse und Bedingungen reagiert, seine Rolle, Position oder Handlung dynamisch aendert und dadurch einen explizit pruefbaren Zielzustand der Szene erreicht.

## Zielentscheidung

Das Hauptziel wird zweistufig formuliert:

1. `UseCase.goal` beschreibt den fachlichen Zweck des Anwendungsfalls.
2. `Scenario.goal` beschreibt den konkret beobachtbaren Erfolg des Hauptszenarios.

Diese Trennung ist wichtig, weil ein UseCase mehrere Szenarien besitzen kann. Der UseCase darf daher nicht nur einen einzelnen Ablaufpfad beschreiben; das Hauptszenario darf dagegen praezise Erfolgsbedingungen festlegen.

## Kandidat fuer `UseCase.goal`

`Dynamisches Agentenverhalten in einer virtuellen Szene so fachlich modellieren, dass ein Agent auf gueltige Ereignisse und Bedingungen reagieren, seine Rolle oder Handlung anpassen und einen pruefbaren Zielzustand der Szene erreichen kann.`

## Kandidat fuer `Scenario.goal`

`Nach einem gueltigen Ausloeseereignis befindet sich der dynamische Agent innerhalb des gueltigen Szenenbereichs in der passenden Rolle, erreicht die fachlich erreichbare Zielzone und erzeugt eine bestaetigte beobachtbare Rueckmeldung.`

## Begruendung der Zielbestandteile

| Zielbestandteil | Warum im Hauptziel? | Bezug zu bisherigen Artefakten | Pruefbarkeit |
| --- | --- | --- | --- |
| gueltiges Ausloeseereignis | Der Agent soll nicht beliebig handeln, sondern auf ein modelliertes Ereignis reagieren. | `A-E1`, `A-E2`; Zweckformulierung aus 2.1 | `Event.kind` und `Event.expression` sind angegeben. |
| gueltiger Szenenbereich | Das Verhalten muss innerhalb der fachlichen Szenengrenze stattfinden. | `A-C2`, `A-S12`, `SceneBoundary` | `inside(AgentBody, SceneBoundary) = true` |
| passende Rolle | Dynamik umfasst nicht nur Bewegung, sondern auch Rollen- oder Handlungswechsel. | `A-S2`, `AgentBody.roleState` | `AgentBody.roleState = executor` oder eine im Szenario erlaubte Rolle |
| fachlich erreichbare Zielzone | Der Kern des Beispiels ist, dass der Agent einen Zielzustand in der Szene erreicht. | `A-C3`, `A-S4`, `A-S5`, `TargetZone` | `TargetZone.state = reached` und `at(AgentBody, TargetZone)` |
| bestaetigte Rueckmeldung | Der Zielzustand soll nicht nur intern angenommen, sondern beobachtbar werden. | `A-C8`, `A-S10`, `FeedbackSignal` | `FeedbackSignal.state = confirmed` |

## Erfolg als beobachtbarer Zielzustand

Der Erfolg des Hauptszenarios ist gegeben, wenn alle folgenden Aussagen wahr sind:

| ID | Beobachtbare Erfolgsaussage | Vorlaeufige Metamodell-Abbildung |
| --- | --- | --- |
| `A-G1` | Ein gueltiges Ereignis hat das Szenario ausgeloest. | `ScenarioStep.triggeredBy -> Event`, z. B. `A-E1` oder `A-E2` |
| `A-G2` | Der Agent ist innerhalb des gueltigen Szenenbereichs. | `Condition.kind = spatial`, Ausdruck `inside(AgentBody, SceneBoundary) = true` |
| `A-G3` | Der Agent ist handlungsbereit oder hat die passende Ausfuehrungsrolle angenommen. | `StateAssertion.subjectRef = AgentBody`, `expectedState = roleState=executor` |
| `A-G4` | Die Zielzone ist fachlich erreichbar oder die relevante Alternative wurde erfolgreich aufgeloest. | `Condition.kind = guard`, z. B. `A-C3` oder `A-C6` |
| `A-G5` | Der Agent hat die Zielzone erreicht. | `StateAssertion.subjectRef = TargetZone`, `expectedState = reached`; optional `StateAssertion` ueber `AgentBody` |
| `A-G6` | Der Beobachtungspunkt oder Zielzustand wurde verifiziert. | `Condition.kind = post`, Ausdruck `ObservationPoint.state = verified` |
| `A-G7` | Die Rueckmeldung zum Ergebnis wurde bestaetigt. | `StateAssertion.subjectRef = FeedbackSignal`, `expectedState = confirmed` |

## Nicht Teil des Hauptziels

| Nicht-Ziel | Warum nicht im Hauptziel? | Spaetere Stelle |
| --- | --- | --- |
| konkrete 3D-Asset-Erzeugung | Out of scope fuer das fachliche Metamodell. | Asset- oder Generierungspipeline ausserhalb dieses Modells |
| konkreter Bewegungsalgorithmus | Das Modell prueft Ziel- und Zustandsaussagen, nicht Pathfinding. | Technische Runtime oder Implementierung |
| API-, Topic- oder Engine-Befehl | `ScenarioStep` darf nicht direkt technisch kurzgeschlossen werden. | `RuntimeBinding -> RuntimeAction` |
| vollstaendige Autonomieentscheidung des Agenten | Interne Planner, Policies oder Behavior Trees sind nicht Kern des UseCase-Ziels. | Optionales Ergaenzungsmodell, falls spaeter noetig |
| alle moeglichen Alternativ- und Fehlerfaelle | Das Hauptziel beschreibt Erfolg; Alternativen und Exceptions folgen separat. | Task 2.10 |

## Abnahmekontrolle

| Kriterium aus Task 2.7 | Erfuellung |
| --- | --- |
| Kandidat fuer `UseCase.goal` vorhanden | Abschnitt `Kandidat fuer UseCase.goal` enthaelt eine fachliche Zielaussage. |
| Kandidat fuer `Scenario.goal` vorhanden | Abschnitt `Kandidat fuer Scenario.goal` enthaelt den beobachtbaren Erfolgspfad. |
| Erfolg als beobachtbarer Zielzustand formulierbar | `A-G1` bis `A-G7` beschreiben pruefbare Ereignis-, Bedingungs- und Zustandsaussagen. |
| Bezug zu bisherigen Tasks hergestellt | Zielbestandteile referenzieren Zweck, Scope, Ereignisse, Bedingungen und Zustandswechsel. |
| Keine technische Kurzschaltung | API, Topic, Engine-Befehl und Pathfinding werden explizit aus dem Hauptziel ausgeschlossen. |

## Konsequenz fuer Task 2.8 und 2.9

Task 2.8 kann aus `A-G1` bis `A-G4` die Startzustaende und Vorbedingungen ableiten.

Task 2.9 kann aus `A-G5` bis `A-G7` die Endzustaende und Nachbedingungen ableiten.
