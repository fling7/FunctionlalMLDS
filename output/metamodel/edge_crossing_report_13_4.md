# Kantenkreuzungsreport 13.4

Datum: 2026-07-08
Task: 13.4 `Kantenkreuzungen automatisch pruefen`

## Gepruefte Artefakte

| Artefakt | Zweck |
| --- | --- |
| `tools/generate_dynamic_functional_mlds.py` | Quelle fuer `NODES` und `EDGES`. |
| `output/metamodel/dynamic_functional_mlds_metamodel.svg` | neu gerendertes SVG nach Routenanpassung. |
| `output/metamodel/dynamic_functional_mlds_metamodel.png` | neu gerendertes PNG nach Routenanpassung. |

## Pruefmethode

Der automatische Check importiert die Generatorquelle und prueft alle gezeichneten Kanten als Polylines.

Gezaehlt werden nur sichtbare Kantenkreuzungen:

- Segmente derselben Kante werden nicht gegeneinander gezaehlt.
- Gemeinsame Endpunkte werden nicht als Kreuzung bewertet.
- Schnittpunkte innerhalb einer Klassenbox werden ignoriert, weil Knoten im SVG und PNG ueber den Kanten gezeichnet werden.
- Kollineare Ueberlagerungen wurden im aktuellen Diagramm nicht gefunden.

## Zwischenbefund und Korrektur

Nach dem Einbau von `Effect.evidencedBy -> StateAssertion [0..*]` schnitt die neue Evidence-Kante zunaechst bestehende Routen:

| Iteration | Sichtbare Kreuzungen | Ursache | Korrektur |
| --- | ---: | --- | --- |
| 1 | 2 | Evidence-Kante schnitt `Capability -> RuntimeBinding` und `Capability -> FunctionBehavior`. | Evidence-Kante rechts herum verlegt. |
| 2 | 1 | Evidence-Kante schnitt den rechten Steg von `Capability -> RuntimeBinding`. | Route nicht ueber diesen Steg gefuehrt. |
| 3 | 2 | Untere linke Route schnitt `Entity -> Capability` und `ScenarioStep -> CapabilityUse`. | Evidence-Kante an der freien rechten Aussenseite entlanggefuehrt. |
| 4 | 0 | keine sichtbare Kreuzung mehr | finale Route beibehalten. |

Finale Evidence-Route:

`Effect -> StateAssertion`: `(1260,1424) -> (1260,1455) -> (2500,1455) -> (2500,965) -> (1250,965) -> (1250,876)`

## Finales Ergebnis

| Kennzahl | Ergebnis |
| --- | ---: |
| Kanten gesamt | 29 |
| Liniensegmente gesamt | 66 |
| sichtbare Kantenkreuzungen | 0 |
| ignorierte Endpunkt-/Knoten-Schnittpunkte | 0 |

## Abnahme

| Kriterium | Erfuellung |
| --- | --- |
| Kreuzungsreport vorhanden | Diese Datei dokumentiert Methode, Zwischenbefund, Korrektur und finales Ergebnis. |
| Automatische Pruefung ausgefuehrt | Der Checker wurde auf Basis der Generator-Polylines ausgefuehrt. |
| `0` sichtbare Kantenkreuzungen oder begruendete Ausnahme | `0` sichtbare Kantenkreuzungen; keine Ausnahme erforderlich. |
| Artefakte konsistent neu erzeugt | Generatorlauf nach finaler Routenanpassung erfolgreich; SVG und PNG wurden neu geschrieben. |
