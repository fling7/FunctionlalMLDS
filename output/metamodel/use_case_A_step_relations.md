# Anwendungsfall A: StepRelations des Hauptszenarios

Stand: 2026-07-07

Task: 3.7 `StepRelations fuer das Hauptszenario A definieren`

Use Case: `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`

Main Scenario: `Agent reagiert auf gueltiges Ereignis und erreicht Zielzone`

## Modellierungsregel

Eine `StepRelation` verbindet genau einen Quellschritt mit genau einem Zielschritt:

- `StepRelation.source -> ScenarioStep [1]`
- `StepRelation.target -> ScenarioStep [1]`
- `StepRelation.kind = sequence|alternative|exception|fork|join|loop`

Fuer den erfolgreichen Hauptpfad werden ausschliesslich `sequence`-Beziehungen verwendet. Alternativen und Exceptions werden erst in den Tasks 3.8 und 3.9 formuliert. Die schrittbezogenen Guards aus Task 3.5 werden nicht nochmals als `StepRelation.guard` dupliziert.

## StepRelations im Hauptpfad

| Relation-ID | Source-Step | Target-Step | `StepRelation.kind` | `StepRelation.guard` | Begruendung |
| --- | --- | --- | --- | --- | --- |
| `A-MAIN-R01` | `A-MAIN-S01` | `A-MAIN-S02` | `sequence` | keine | Nach Feststellung des gueltigen Ausloeseereignisses wird der gueltige Szenenbereich geprueft. |
| `A-MAIN-R02` | `A-MAIN-S02` | `A-MAIN-S03` | `sequence` | keine | Nach der Bereichspruefung wird die Handlungsbereitschaft des Agenten festgestellt. |
| `A-MAIN-R03` | `A-MAIN-S03` | `A-MAIN-S04` | `sequence` | keine | Nach Feststellung der Handlungsbereitschaft wird die Zielzone auf Erreichbarkeit geprueft. |
| `A-MAIN-R04` | `A-MAIN-S04` | `A-MAIN-S05` | `sequence` | keine | Nach positiver Zielerreichbarkeit kann der Agent die Ausfuehrungsrolle annehmen. |
| `A-MAIN-R05` | `A-MAIN-S05` | `A-MAIN-S06` | `sequence` | keine | Nach Rollenannahme folgt die zielgerichtete Szenenhandlung. |
| `A-MAIN-R06` | `A-MAIN-S06` | `A-MAIN-S07` | `sequence` | keine | Nach der zielgerichteten Handlung wird die Zielerreichung beobachtet. |
| `A-MAIN-R07` | `A-MAIN-S07` | `A-MAIN-S08` | `sequence` | keine | Nach Zielerreichung wird der Zielzustand verifiziert. |
| `A-MAIN-R08` | `A-MAIN-S08` | `A-MAIN-S09` | `sequence` | keine | Nach Verifikation wird die Ergebnisrueckmeldung bestaetigt. |

## Ausgehende Beziehungen je Schritt

| Step-ID | Ausgehende Relation im Hauptpfad | Bewertung |
| --- | --- | --- |
| `A-MAIN-S01` | `A-MAIN-R01` | Erfuellt: ausgehende Sequenzrelation vorhanden. |
| `A-MAIN-S02` | `A-MAIN-R02` | Erfuellt: ausgehende Sequenzrelation vorhanden. |
| `A-MAIN-S03` | `A-MAIN-R03` | Erfuellt: ausgehende Sequenzrelation vorhanden. |
| `A-MAIN-S04` | `A-MAIN-R04` | Erfuellt: ausgehende Sequenzrelation vorhanden. |
| `A-MAIN-S05` | `A-MAIN-R05` | Erfuellt: ausgehende Sequenzrelation vorhanden. |
| `A-MAIN-S06` | `A-MAIN-R06` | Erfuellt: ausgehende Sequenzrelation vorhanden. |
| `A-MAIN-S07` | `A-MAIN-R07` | Erfuellt: ausgehende Sequenzrelation vorhanden. |
| `A-MAIN-S08` | `A-MAIN-R08` | Erfuellt: ausgehende Sequenzrelation vorhanden. |
| `A-MAIN-S09` | keine | Erfuellt: letzter Schritt des erfolgreichen Hauptpfads. |

## Warum keine Guards auf den Sequence-Relations?

Die Guards fuer die fachliche Zulaessigkeit der einzelnen Schritte wurden in Task 3.5 auf `ScenarioStep.guard` gesetzt. Fuer den linearen Hauptpfad wuerden identische `StepRelation.guard`-Bedingungen dieselben Regeln doppelt modellieren.

`StepRelation.guard` bleibt fuer spaetere alternative oder exception-artige Verzweigungen reserviert, wo eine Ablaufkante selbst die Entscheidung zwischen mehreren Zielschritten ausdrueckt.

## Abnahmekontrolle

| Kriterium aus Task 3.7 | Erfuellung |
| --- | --- |
| Source Step definiert | Jede Relation `A-MAIN-R01` bis `A-MAIN-R08` hat genau einen Source-Step. |
| Target Step definiert | Jede Relation `A-MAIN-R01` bis `A-MAIN-R08` hat genau einen Target-Step. |
| Relation Kind definiert | Jede Hauptpfad-Relation ist als `sequence` typisiert. |
| Jeder Schritt ausser dem letzten hat ausgehende Sequenzrelation | `A-MAIN-S01` bis `A-MAIN-S08` haben je genau eine ausgehende Sequenzrelation. |
| Letzter Schritt begruendet ohne ausgehende Relation | `A-MAIN-S09` ist der Abschluss des erfolgreichen Hauptpfads. |
| Keine Alternative oder Exception vorweggenommen | `alternative` und `exception` werden nicht im Hauptpfad verwendet; sie folgen in 3.8 und 3.9. |
| Kardinalitaeten eingehalten | Jede `StepRelation` referenziert genau einen Source- und genau einen Target-Step. |

## Konsequenz fuer Task 3.8

Task 3.8 kann nun ein alternatives Szenario formulieren. Geeignet ist `A-ALT2`, weil eine temporaere Blockade nach `A-MAIN-S04` abzweigen und nach Freigabe vor `A-MAIN-S05` wieder in den Hauptpfad zurueckkehren kann.
