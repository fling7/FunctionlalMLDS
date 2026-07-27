# Anwendungsfall A: Parallelitaetspruefung

Stand: 2026-07-07

Task: 3.10 `Parallele oder nebenlaeufige Agentenablaeufe pruefen`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

## Entscheidung

Fuer den aktuell ausgearbeiteten Anwendungsfall A wird keine `ParallelGroup` benoetigt.

Der Hauptpfad, das Alternativszenario und das Exception-Szenario sind fachlich sequenziell modellierbar. Es gibt derzeit keine zwei `ScenarioStep`-Elemente desselben `Scenario`, die gleichzeitig oder nebenlaeufig ausgefuehrt oder beobachtet werden muessen.

## Begruendung anhand der bestehenden Szenarien

| Szenario | Gepruefter Ablauf | Parallelitaet fachlich erforderlich? | Begruendung |
| --- | --- | --- | --- |
| `A-MAIN` | `A-MAIN-S01` bis `A-MAIN-S09` | nein | Jeder Schritt baut fachlich auf dem vorherigen auf: Ausloeser, Bereich, Bereitschaft, Zielerreichbarkeit, Rolle, Handlung, Zielerreichung, Verifikation, Rueckmeldung. |
| `A-ALT-SC01` | temporaere Blockade aufloesen | nein | Die Alternative verzweigt nach `A-MAIN-S04`, beobachtet die Blockadeaufloesung und fuehrt danach zu `A-MAIN-S05` zurueck. |
| `A-EX-SC01` | dauerhafte Blockade verhindert Zielerreichung | nein | Die Exception beendet den Erfolgspfad sicher; ihre Schritte sind Feststellung, systemische Reaktion und Fehlerabschluss. |

## Abgleich mit Metamodellregeln

| Regel | Bewertung fuer Anwendungsfall A |
| --- | --- |
| `ParallelGroup.memberSteps [2..*]` | Nicht erfuellt, weil aktuell keine mindestens zwei parallel laufenden Schritte benoetigt werden. |
| Alle Mitgliedsschritte muessen zum selben `Scenario` gehoeren. | Wuerde gelten, falls spaeter eine ParallelGroup eingefuehrt wird. Aktuell gibt es keine Gruppe. |
| `ParallelGroup` besitzt Schritte nicht, sondern referenziert sie. | Relevant fuer spaetere Erweiterung; aktuell nicht anzuwenden. |
| Keine Parallelitaet mit nur einem Schritt. | Wird eingehalten, indem keine kuenstliche ParallelGroup angelegt wird. |

## Warum keine kuenstliche ParallelGroup?

Eine `ParallelGroup` waere nur korrekt, wenn mindestens zwei fachliche Schritte gleichzeitig oder nebenlaeufig betrachtet werden muessen. Das ist im aktuellen Szenario nicht der Fall:

- Die Verifikation (`A-MAIN-S08`) folgt auf die Zielerreichung (`A-MAIN-S07`), statt parallel dazu zu laufen.
- Die Rueckmeldung (`A-MAIN-S09`) folgt auf die Verifikation, statt parallel dazu zu laufen.
- Die temporaere Blockade-Alternative fuehrt in den Hauptpfad zurueck, statt parallel zum Hauptpfad zu laufen.
- Die Exception beendet den Hauptpfad, statt parallel zu ihm weiterzulaufen.

## Bedingungen fuer eine spaetere ParallelGroup

Falls der Anwendungsfall spaeter erweitert wird, waere eine `ParallelGroup` nur dann gerechtfertigt, wenn mindestens zwei konkrete Schritte desselben Scenarios parallel laufen. Beispiele:

| Moegliche Erweiterung | Denkbare Mitgliedsschritte | Waere `ParallelGroup` zulaessig? | Bemerkung |
| --- | --- | --- | --- |
| Mehrere Agenten bewegen sich gleichzeitig zu unterschiedlichen Zielzonen. | `AgentA bewegt sich zu TargetZoneA`; `AgentB bewegt sich zu TargetZoneB` | ja, falls beide Schritte im selben Scenario liegen | Mindestens zwei Mitgliedsschritte waeren vorhanden. |
| Agent handelt, waehrend ein Beobachtungskanal kontinuierlich validiert. | `Agent fuehrt Zielhandlung aus`; `ObservationChannel prueft Zielnaehe` | ja, falls fachlich echte Nebenlaeufigkeit gefordert ist | Muss von einer sequenziellen Pruefung unterschieden werden. |
| Rueckmeldung wird parallel zur Zielverifikation angezeigt. | `ObservationPoint wird verifiziert`; `FeedbackSignal wird angezeigt` | moeglich, aber derzeit nicht modelliert | Aktuell ist die Rueckmeldung bewusst nachgelagert. |
| Temporaere Blockade wird beobachtet, waehrend Agent wartet. | `Agent wartet`; `ObstacleRegion wird erneut geprueft` | moeglich, aber aktuell als Sequenz modelliert | Nur noetig, wenn gleichzeitiges Warten und Monitoring fachlich relevant wird. |

## Entscheidung fuer die aktuelle Modellversion

| Entscheidungsfrage | Antwort |
| --- | --- |
| Wird `ParallelGroup` fuer den aktuellen Hauptpfad benoetigt? | nein |
| Wird `ParallelGroup` fuer die aktuelle Alternative benoetigt? | nein |
| Wird `ParallelGroup` fuer die aktuelle Exception benoetigt? | nein |
| Muessen mindestens zwei Mitgliedsschritte angegeben werden? | nein, weil keine ParallelGroup angelegt wird |
| Soll das Metamodell dafuer angepasst werden? | nein |
| Soll ein Ergaenzungsmodell dafuer eingehangen werden? | nein |

## Abnahmekontrolle

| Kriterium aus Task 3.10 | Erfuellung |
| --- | --- |
| Entscheidung vorhanden | Keine `ParallelGroup` fuer den aktuellen Anwendungsfall A. |
| Entscheidung begruendet | Haupt-, Alternativ- und Exception-Szenario wurden sequenziell geprueft. |
| Falls ja, mindestens zwei Mitgliedsschritte | Nicht anwendbar, weil keine ParallelGroup angelegt wird. |
| Keine kuenstliche Parallelitaet | Die Mindestkardinalitaet `2..*` wird nicht durch eine Scheingruppe unterlaufen. |
| Erweiterungsfall dokumentiert | Bedingungen fuer spaetere ParallelGroup-Nutzung sind mit moeglichen Mitgliedsschritten beschrieben. |

## Konsequenz fuer Abschnitt 4

Abschnitt 4 kann Anwendungsfall A nun auf das bestehende Metamodell abbilden, ohne eine `ParallelGroup`-Instanz fuer A anzulegen. Die Abbildung muss dennoch dokumentieren, dass `Scenario -> ParallelGroup [0..*]` fuer A mit `0` belegt wird.
