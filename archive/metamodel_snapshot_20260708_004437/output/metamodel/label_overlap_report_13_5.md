# Label-Overlap-Report 13.5

Datum: 2026-07-08
Task: 13.5 `Label-Overlaps automatisch pruefen`

## Gepruefte Artefakte

| Artefakt | Zweck |
| --- | --- |
| `tools/generate_dynamic_functional_mlds.py` | Quelle fuer Knoten, Kanten und Labelpositionen. |
| `output/metamodel/dynamic_functional_mlds_metamodel.svg` | neu gerendertes SVG nach Labelkorrektur. |
| `output/metamodel/dynamic_functional_mlds_metamodel.png` | neu gerendertes PNG nach Labelkorrektur. |

## Pruefmethode

Der automatische Check importiert die Generatorquelle und rekonstruiert die im SVG gezeichneten Label-Boxen.

Geprueft wurden:

- Label-Label-Ueberdeckungen zwischen allen sichtbaren Edge-Labels.
- Label-Klassen-Ueberdeckungen zwischen allen sichtbaren Edge-Labels und allen Klassenboxen.
- Labels ausserhalb der Canvas.

Die Berechnung nutzt dieselbe Boxlogik wie der SVG-Renderer:

- Labelbreite: `max(64, maxLineLength * 7.6 + 26)`
- Labelhoehe: `18 * lineCount + 12`
- Labelursprung: `label_pos`, mit `y - 15` als oberer Boxkante
- Sicherheitsmarge: `2 px`

## Zwischenbefund und Korrektur

Der erste automatische Check fand folgende Overlaps:

| Kategorie | Anzahl | Ursache | Korrektur |
| --- | ---: | --- | --- |
| Label-Label | 1 | `ScenarioStep -> StateAssertion` lag sehr knapp an `StepRelation -> ScenarioStep target`. | Label `target step [1]` auf `y=700` verschoben. |
| Label-Klasse | 2 | `UseCase -> ExtensionPoint` beruehrte die benachbarten Klassenboxen. | Label unter die Kante auf `y=405` verschoben. |
| Label-Klasse | 1 | `Entity -> Capability` lag zu nah an der vergroesserten `Entity`-Box. | Label auf `y=1330` verschoben. |
| Label-Klasse | 1 | `ValidationCase -> RuntimeBinding` beruehrte die `ValidationCase`-Box. | Label auf `y=1270` verschoben. |

Nach diesen Korrekturen wurden Generator, SVG und PNG neu erzeugt.

## Finales Ergebnis

| Kennzahl | Ergebnis |
| --- | ---: |
| Edge-Labels gesamt | 28 |
| Klassenboxen gesamt | 24 |
| Label-Label-Overlaps | 0 |
| Label-Klassen-Overlaps | 0 |
| Labels ausserhalb der Canvas | 0 |

## Abnahme

| Kriterium | Erfuellung |
| --- | --- |
| Overlap-Report vorhanden | Diese Datei dokumentiert Methode, Befund, Korrektur und finales Ergebnis. |
| Label-Label-Overlaps automatisch geprueft | `0` Overlaps. |
| Label-Klassen-Overlaps automatisch geprueft | `0` Overlaps. |
| Artefakte konsistent neu erzeugt | Generatorlauf nach finaler Labelkorrektur erfolgreich; SVG und PNG wurden neu geschrieben. |
