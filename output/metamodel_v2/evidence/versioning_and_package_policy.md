# DFMLDS V2 - Versionierungs- und Paketregel

Stand: 2026-07-14

## Geltungsbereich

Diese Regel trennt die Version des fachlichen Metamodells von der bereits
produktiven v0.5-Serialisierung. Sie gilt fuer die Modellartefakte unter
`output/metamodel_v2/` und die V2-Werkzeuge unter `tools/`. Sie aendert weder
den v0.5-Vertrag noch Unity, Backend oder Case-Study-Pipeline.

## Versionen

| Gegenstand | Kennung | Regel |
|---|---|---|
| Arbeitsnamensraum | `DFMLDS::V2` | Stabiler Namensraum waehrend der Modellbearbeitung. |
| Abgenommener Modellrelease | `2.0.0-model` | Freigegebener Modellstand nach erfolgreicher Abschlussabnahme. Das Suffix kennzeichnet, dass es sich um die Modellversion und nicht um das Runtime-JSON-Format handelt. |
| Bestehende Runtime-Serialisierung | `metamodelVersion: "v0.5"` | Bleibt fuer bestehende Instanzen, Unity, Backend und Pipeline unveraendert. |
| V2-Kompatibilitaetsprojektion | `dynamic_functional_mlds_v2_projection` / `v2.0` | Internes Projektionsformat; kein Ersatz fuer den v0.5-Runtime-Vertrag. |
| Projektionsledger | `V05ProjectionLedger` / `1.0` | Bewahrt nicht sicher ableitbare Serialisierungsdetails fuer die exakte Rueckprojektion. |

`2.0.0-model` wurde erst vergeben, nachdem das kanonische Modell, alle daraus
generierten Sichten, die EAST-ADL-Konformitaetsmatrix, die Invarianten und die
v0.5-Rueckprojektionsnachweise denselben Stand in der Abschlussabnahme belegt
haben. Der kanonische Status lautet `accepted-model-release`; der verbindliche
Gesamtstatus dieses Release-Stands steht in
`output/metamodel_v2/evidence/acceptance_report.json`.

## Paket- und Abhaengigkeitsregel

Die Abhaengigkeit ist strikt einseitig:

```text
DFMLDS::V2  ----uses/imports---->  EAST-ADL::2.1.12
EAST-ADL::2.1.12  - - -X- - ->    DFMLDS::V2
```

- `DFMLDS::V2` darf EAST-ADL-Metaklassen spezialisieren, referenzieren und
  deren unveraenderte Semantik wiederverwenden.
- Keine EAST-ADL-Metaklasse erhaelt durch DFMLDS ein neues Pflichtattribut,
  eine neue Pflichtassoziation, eine strengere Kardinalitaet oder eine
  zusaetzliche Invariante.
- DFMLDS-eigene Beziehungen liegen im Paket `DFMLDS::V2` und generalisieren
  bei Bedarf `EAST-ADL::Infrastructure::Relationship` oder eine passendere
  EAST-ADL-Beziehung.
- Das optionale Annex-C-Mapping und optionale Automotive-Feature-Mappings
  duerfen keinen Import vom EAST-ADL-Paket zurueck in `DFMLDS::V2` erzeugen.
- Ein EAST-ADL-Modell ohne DFMLDS-Inhalte bleibt unveraendert gueltig. Die
  strengeren Ausfuehrungsregeln gelten nur fuer ein explizit aktiviertes
  DFMLDS-Ausfuehrungsprofil.

Der kanonische Paketgraph konkretisiert dies wie folgt:

- `DFMLDS::V2::Core` importiert nur die benoetigten normativen EAST-ADL-Pakete;
- `DFMLDS::V2::AnnexCBridge` importiert den Core und die vorlaeufigen
  Annex-C-Pakete, der Core importiert die Bridge nicht;
- `DFMLDS::V2::FeatureBridge` importiert den Core und die optionalen Feature-
  Pakete, der Core importiert die Bridge nicht;
- `DFMLDS::V2::AgentKnowledge` importiert den Core, der Core verpflichtet keine
  AgentKnowledge-Instanz.

## Kompatibilitaetsgrenze

Das V2-Modell und die v0.5-Serialisierung sind zwei getrennte Vertrage:

1. Der Import liest eine gueltige v0.5-Instanz in eine V2-Projektionshuelle.
2. Die semantisch eindeutigen Inhalte werden auf V2-Elemente abgebildet.
3. Nicht eindeutig rekonstruierbare Details bleiben im separaten
   `V05ProjectionLedger`: Feldpraesenz, explizites `null`, leere Container,
   Objekt- und Arrayreihenfolge, Original-IDs, Enum-Lexeme, rohe
   `stepNumber`-Werte, `level`, alle drei Locator-Slots sowie Agent-/Entity-
   Aliasse.
4. Der Export ist fail-closed. V2-Inhalte ausserhalb der v0.5-ausdrueckbaren
   Teilmenge duerfen nicht stillschweigend verworfen werden.

Verbindliches Gesetz fuer jede gueltige v0.5-Instanz `x`:

```text
exportV05(importV05(x)) == x
```

Die Umkehrung gilt nur fuer die v0.5-repraesentierbare V2-Teilmenge oder unter
Mitfuehrung des Ledgers. Insbesondere werden `ValidationCase.level`, Locator-
Slots und AG-/ENT-/Source-Agent-Identitaeten nicht aus fachlichen V2-Strukturen
erraten.

## Aenderungsregeln

| Aenderungsart | Erforderliche Folge |
|---|---|
| Rein redaktionelle Modellbeschreibung | Patch der Modellversion; keine Runtime-Aenderung. |
| Additive, optionale DFMLDS-Klasse oder -Beziehung | Minor der Modellversion; Rueckprojektion muss weiterhin fail-closed sein. |
| Inkompatible Modellsemantik | Major der Modellversion und erneute Abnahme aller Invarianten. |
| Aenderung der v0.5-JSON-Felder oder -Semantik | Eigene Runtime-Vertragsentscheidung; nicht durch einen Modellrelease impliziert. |
| Aenderung einer EAST-ADL-Uebernahme | Erneuter Seitenabgleich gegen die festgelegte EAST-ADL-Version. |

## Kanonische Nachweise

- Modellquelle: `tools/dynamic_functional_mlds_v2_model.py`
- Kompatibilitaetsimplementierung:
  `tools/dynamic_functional_mlds_v2_compat.py`
- Vollstaendige Feldabbildung:
  `output/metamodel_v2/evidence/v05_compatibility_mapping.md`
- Maschinenlesbare Feldabdeckung:
  `output/metamodel_v2/evidence/v05_field_coverage.json`
- Runde-Reise-Nachweis:
  `output/metamodel_v2/evidence/v05_roundtrip_report.md`
- EAST-ADL-Abgleich:
  `output/metamodel_v2/evidence/east_adl_conformance_matrix.md`
- Annex-C-Regeln:
  `output/metamodel_v2/evidence/annex_c_mapping.md`

Die Existenz dieser Verweise allein ist keine Abnahme. Der Release-Status wird
erst gesetzt, wenn die verlinkten Artefakte vorhanden, konsistent und durch die
Akzeptanzpruefung belegt sind.
