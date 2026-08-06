# Visuelle Abnahme der V2-Diagramme

Stand: 2026-07-14  
Modellrelease: `2.0.0-model`  
Ergebnis: **PASS**

Die zentrale A/B/C-Gesamtansicht und die sieben ergänzenden Fachsichten wurden
als PNG in Originalauflösung geprüft. Die acht SVG-Dateien wurden zusätzlich als
XML geparst. Geprüft wurden insbesondere der A/B/C-Lesefluss, Klassen- und
Paketkennzeichnung, Generalisierungen, Kompositionen, optionale Beziehungen,
Stereotype, Kardinalitäten, Pfeilspitzen, Farbcodierung, Panelgliederung und die
vollständigen Beziehungsnachweise.

| Sicht | PNG-Auflösung | SVG | Visuell | Geometrie |
|---|---:|---:|---|---|
| `dynamic_functional_mlds_v2_metamodel` | 3200 × 2520 | 58.810 Bytes | PASS | PASS |
| `01_east_adl_infrastructure` | 2186 × 1742 | 24.398 Bytes | PASS | PASS |
| `02_east_adl_requirements_usecases` | 2186 × 1576 | 22.524 Bytes | PASS | PASS |
| `03_east_adl_function_system_behavior` | 2506 × 1576 | 27.500 Bytes | PASS | PASS |
| `04_dfmlds_scenario_flow` | 2506 × 2622 | 41.716 Bytes | PASS | PASS |
| `05_dfmlds_capability_runtime` | 2700 × 2223 | 39.414 Bytes | PASS | PASS |
| `06_east_adl_dfmlds_verification_validation` | 2826 × 2009 | 40.291 Bytes | PASS | PASS |
| `07_optional_annex_feature_knowledge` | 3000 × 1788 | 40.553 Bytes | PASS | PASS |

Die zentrale Grafik ist der primäre Einstieg und zeigt Requirements/UseCases,
Scenario Layer sowie Capability/Runtime/V&V in einer durchgehenden Leserichtung.
Die sieben Fachsichten liefern die vollständigen Details. Damit die Grafiken
vorzeigbar bleiben, wird nur eine kuratierte Teilmenge der lokalen Beziehungen
als Kante geroutet; jede nicht gezeichnete lokale Beziehung bleibt im darunter
stehenden Beziehungsnachweis mit Quellrolle, Zielrolle, Zieltyp, Multiplizität,
Ordnung und Optionalität erhalten.

Die Prä-v1.0-Erweiterungen wurden gezielt in den bestehenden Sichten geprüft:

- Gesamtansicht: geerbte EAST-ADL-Felder, Satisfy-Ausschluss, Kontrollflussnote,
  abstrakte Assertion, Providerprofil, RuntimeValidationTarget und AssertionResult;
- Sicht 04: ExternalEvent/ScenarioExternalEvent und alle fünf Assertion-Arten;
- Sicht 05: getrennte, kreuzungsfreie Korridore für CapabilityUse.provider,
  CapabilityUse.target und Effect.specifiedBy;
- Sicht 06: getrennte Subject-/Target-Semantik sowie spaltenreine Result-Kette.

Der automatisierte Geometriecheck ergibt über alle acht Sichten:

| Prüfkriterium | Gesamtwert | Grenzwert |
|---|---:|---:|
| Diagonale Kantensegmente | 0 | 0 |
| Kanten durch fremde Klassenkarten | 0 | 0 |
| Echte Kantenkreuzungen | 0 | 0 |
| Kollineare Linienüberlagerungen | 0 | 0 |
| Kantenlabel/Karten-Überdeckungen | 0 | 0 |

Maschinenlesbare Nachweise stehen in `diagram_geometry_qa.json`,
`format_consistency.json`, `generation_reproducibility.json` und
`../generated/generation_manifest.sha256.json`.
