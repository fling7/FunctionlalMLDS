# Sichtpruefung 13.6

Datum: 2026-07-08
Task: 13.6 `Diagramm visuell pruefen`

## Gepruefte Artefakte

| Artefakt | Zweck |
| --- | --- |
| `output/metamodel/dynamic_functional_mlds_metamodel.png` | visuelle Pruefung in voller Aufloesung. |
| `output/metamodel/dynamic_functional_mlds_metamodel.svg` | vektorbasiertes Zielartefakt. |
| `tools/generate_dynamic_functional_mlds.py` | Generatorquelle fuer die visuelle Korrektur. |

## Vorgehen

Das PNG wurde in voller Aufloesung geoeffnet und visuell auf folgende Punkte geprueft:

- abgeschnittene Klassentitel,
- abgeschnittene Attributzeilen,
- abgeschnittene oder aus der Canvas laufende Edge-Labels,
- unklar zugeordnete Edge-Labels,
- visuell stoerende Kantenkreuzungen,
- visuell stoerende Label-Ueberdeckungen,
- Lesbarkeit der neuen `EntityKind`-Typisierung,
- Lesbarkeit der neuen `Effect -> StateAssertion`-Evidence-Kante.

Zusaetzlich wurden nach der visuellen Korrektur die automatischen Checks aus 13.4 und 13.5 noch einmal kompakt ausgefuehrt.

## Befund und Korrektur

| Befund | Bewertung | Korrektur |
| --- | --- | --- |
| `Condition`-Klasse hatte zu wenig vertikalen Innenabstand fuer die letzte Attributzeile. | visuell nicht sauber genug | `Condition`-Box im Generator von `116` auf `136` px Hoehe erhoeht. |
| Edge-Labels waren nach 13.5 nicht ueberlappend. | akzeptiert | keine weitere Labelkorrektur erforderlich. |
| Evidence-Kante `Effect -> StateAssertion` ist lang, aber kreuzungsfrei und beschriftet. | akzeptiert | Route bleibt an der rechten Aussenseite, weil sie Kreuzungen vermeidet. |
| `EntityKind` in `Entity` wird ueber zwei Attributzeilen dargestellt. | akzeptiert | kein Abschneiden, keine Ueberdeckung. |

Nach der Korrektur wurden Generator, SVG, PNG, Mermaid und Spezifikation neu erzeugt.

## Regression nach Korrektur

| Pruefung | Ergebnis |
| --- | ---: |
| sichtbare Kantenkreuzungen | 0 |
| Label-Label-Overlaps | 0 |
| Label-Klassen-Overlaps | 0 |
| Labels ausserhalb der Canvas | 0 |
| Edge-Labels gesamt | 28 |
| Klassenboxen gesamt | 24 |

## Finale Sichtbewertung

| Kriterium | Ergebnis |
| --- | --- |
| Keine abgeschnittenen Klassentitel | erfuellt |
| Keine abgeschnittenen Attributzeilen | erfuellt |
| Keine abgeschnittenen Edge-Labels | erfuellt |
| Keine unklar ueberdeckten Labels | erfuellt |
| Neue Kernanpassungen sichtbar | `EntityKind` und `Effect.evidencedBy` sind sichtbar. |
| Diagramm bleibt in drei Bereiche gegliedert | EAST-ADL-Kern, Scenario Layer und Functional/Runtime Bridge bleiben erkennbar. |

## Abnahme

| Kriterium aus Task 13.6 | Erfuellung |
| --- | --- |
| Sichtpruefung vorhanden | Diese Datei dokumentiert Befund, Korrektur und finale Sichtbewertung. |
| Keine abgeschnittenen Labels | erfuellt. |
| Keine unklar zugeordneten Labels | erfuellt. |
| Visuelle Korrekturen konsistent erzeugt | Generatorlauf nach Korrektur erfolgreich; SVG und PNG wurden neu geschrieben. |
