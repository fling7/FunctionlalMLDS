# Anwendungsfall A: Schrittarten des Hauptszenarios

Stand: 2026-07-07

Task: 3.3 `Fuer jeden Schritt A die Schrittart bestimmen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

Main Scenario: `Agent reagiert auf gueltiges Ereignis und erreicht Zielzone`

## Modellierungsregel

Die Schrittart wird ausschliesslich mit den im Metamodell vorgesehenen Werten belegt:

- `actorIntent`: Eine externe Actor-Rolle bringt eine fachliche Absicht oder Handlung ein.
- `systemResponse`: Das modellierte System oder eine systemische Entitaet reagiert fachlich.
- `environmentObservation`: Ein relevanter Zustand, ein Ereignis oder ein Ergebnis wird fachlich beobachtet oder festgestellt.

Der aktuelle Hauptpfad aus Task 3.2 ist bewusst generisch formuliert. Er enthaelt kein explizites "Benutzer tut X", sondern ein fachlich festgestelltes Ausloeseereignis, mehrere beobachtete Voraussetzungen, Agentenreaktionen und beobachtete Ergebniszustaende. Deshalb wird `actorIntent` im Hauptpfad noch nicht verwendet. Externe Rollen koennen spaeter bei konkreten Alternativen, Triggern oder Verifikationsvarianten ueber Events und `performedBy` praezisiert werden.

## Schrittart je ScenarioStep-Kandidat

| Step-ID | ScenarioStep-Kandidat | Schrittart fuer `ScenarioStep.kind` | Begruendung |
| --- | --- | --- | --- |
| `A-MAIN-S01` | Ein gueltiges Ausloeseereignis wird fachlich festgestellt. | `environmentObservation` | Der Schritt beobachtet, dass ein gueltiger Ausloeser vorliegt; die konkrete Herkunft des Events wird erst in Task 3.4 bestimmt. |
| `A-MAIN-S02` | Der Agent wird im gueltigen Szenenbereich festgestellt. | `environmentObservation` | Der Schritt stellt einen raeumlichen Zustand des Agenten fest. |
| `A-MAIN-S03` | Der Agent wird als handlungsbereit festgestellt. | `environmentObservation` | Der Schritt beobachtet einen Bereitschaftszustand, ohne selbst eine Agentenhandlung auszufuehren. |
| `A-MAIN-S04` | Die Zielzone wird als fachlich erreichbar festgestellt. | `environmentObservation` | Der Schritt prueft einen fachlichen Szenenzustand als Voraussetzung fuer den Hauptpfad. |
| `A-MAIN-S05` | Der Agent nimmt die Ausfuehrungsrolle an. | `systemResponse` | Der Agent ist eine ausfuehrende Entitaet und reagiert auf den festgestellten Ausloeser durch Rollenwechsel. |
| `A-MAIN-S06` | Der Agent fuehrt die zielgerichtete Szenenhandlung aus. | `systemResponse` | Der Schritt beschreibt die fachliche Reaktion beziehungsweise Handlung des Agenten. |
| `A-MAIN-S07` | Der Agent erreicht die Zielzone. | `environmentObservation` | Der Schritt beschreibt den beobachteten Zielzustand nach der Agentenhandlung. |
| `A-MAIN-S08` | Der Zielzustand wird beobachtbar verifiziert. | `environmentObservation` | Der Schritt beschreibt die Beobachtung beziehungsweise Verifikation des erreichten Zustands, nicht die technische Testausfuehrung. |
| `A-MAIN-S09` | Die Ergebnisrueckmeldung wird bestaetigt. | `environmentObservation` | Der Schritt beschreibt den beobachtbaren Abschlusszustand der Rueckmeldung. |

## Umgang mit Actor-Rollen

| Actor-Rolle | Warum nicht automatisch `actorIntent` im Hauptpfad? | Moegliche spaetere Verwendung |
| --- | --- | --- |
| `ScenarioDesigner` | Diese Rolle spezifiziert den Use Case, handelt aber nicht innerhalb des Hauptpfads. | Traceability zu UseCase-Text, Requirements und Modellierungsabsicht. |
| `SceneParticipant` | Der Hauptpfad sagt noch nicht, ob das gueltige Ereignis durch einen Teilnehmer, ein Signal oder die Umgebung ausgeloest wird. | In Task 3.4 kann ein konkretes Event wie `entered(SceneParticipant, TriggerZone)` zugeordnet werden. |
| `SceneObserver` | Die Verifikation ist im Hauptpfad als beobachtbarer Zustand formuliert, nicht als explizite externe Handlung. | Bei einer konkreten Validierungsvariante kann `performedBy = SceneObserver` gesetzt werden. |
| `ExternalEventSource` | Externe Signale sind moegliche Events, aber keine konkrete Hauptpfadhandlung in Task 3.3. | In Task 3.4 kann `A-E2` einem Schritt als ausloesendes Signal zugeordnet werden. |
| `TrainingSupervisor` | Trainings- oder Korrekturhandlungen gehoeren nicht zum erfolgreichen Hauptpfad. | Fuer Alternativen, Wiederholung oder Exception-Behandlung. |

## Plausibilitaetspruefung

| Kategorie | Schritte | Bewertung |
| --- | --- | --- |
| `actorIntent` | keine im generischen Hauptpfad | Korrekt, weil kein Schritt aus 3.2 eine explizite externe Absicht beschreibt. |
| `systemResponse` | `A-MAIN-S05`, `A-MAIN-S06` | Korrekt, weil hier der Agent als systemische Entitaet fachlich reagiert. |
| `environmentObservation` | `A-MAIN-S01`, `A-MAIN-S02`, `A-MAIN-S03`, `A-MAIN-S04`, `A-MAIN-S07`, `A-MAIN-S08`, `A-MAIN-S09` | Korrekt, weil diese Schritte Ereignisse, Voraussetzungen oder Zielzustaende feststellen. |

## Abnahmekontrolle

| Kriterium aus Task 3.3 | Erfuellung |
| --- | --- |
| Fuer jeden Schritt ist eine Schrittart bestimmt | `A-MAIN-S01` bis `A-MAIN-S09` haben genau einen Wert fuer `ScenarioStep.kind`. |
| Nur erlaubte Werte verwendet | Es werden ausschliesslich `actorIntent`, `systemResponse` und `environmentObservation` diskutiert; belegt sind `systemResponse` und `environmentObservation`. |
| Jede Zuordnung ist begruendet | Jede Tabellenzeile enthaelt eine Begruendung. |
| Actor/Agent-Trennung gewahrt | Agentenhandlungen werden als `systemResponse` eingeordnet; externe Actor-Rollen werden nicht mit Agenten verwechselt. |
| Anschluss an Task 3.4 vorhanden | Die konkrete Event-Herkunft wird ausdruecklich fuer Task 3.4 offengelassen. |

## Konsequenz fuer Task 3.4

Task 3.4 kann die ausloesenden Events bestimmen. Besonders wichtig ist `A-MAIN-S01`, weil dort entschieden wird, ob das Hauptszenario durch ein raeumliches Event, ein Signal oder eine andere gueltige Ereignisart gestartet wird.
