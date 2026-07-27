# Spezifikationsupdate 13.7

Datum: 2026-07-08
Task: 13.7 `Spezifikation aktualisieren`

## Gepruefte und aktualisierte Artefakte

| Artefakt | Rolle |
| --- | --- |
| `tools/generate_dynamic_functional_mlds.py` | Quelle der generierten Spezifikation. |
| `output/metamodel/dynamic_functional_mlds_specification.md` | aktualisierte deutsche Spezifikation. |
| `output/metamodel/dynamic_functional_mlds_metamodel.svg` | durch Generatorlauf konsistent neu geschrieben. |
| `output/metamodel/dynamic_functional_mlds_metamodel.png` | durch Generatorlauf konsistent neu geschrieben. |
| `output/metamodel/dynamic_functional_mlds_metamodel.mmd` | durch Generatorlauf konsistent neu geschrieben. |

## Aktualisierte Spezifikationsinhalte

Die generierte Spezifikation enthaelt jetzt neben der technischen Beschreibung auch die Modellentscheidung aus der A/B-Analyse.

| Inhalt | Status |
| --- | --- |
| `Entity.kind: EntityKind [0..1]` | beschrieben in Reduktionsliste, Kardinalitaeten, Beziehungsabdeckung und Invarianten. |
| `EntityKind = agent, asset, zone, signal, stateObject` | beschrieben als stabile, grobe Enumeration ohne domaenenspezifische Spezialwerte. |
| `Effect.evidencedBy -> StateAssertion [0..*]` | beschrieben in Reduktionsliste, Kardinalitaeten, Beziehungsabdeckung und Invarianten. |
| Modellentscheidung Kern vs. Ergaenzungsmodule | eigener Abschnitt `Kernanpassungen v0.5 und Modellentscheidung`. |
| Nicht in den Kern uebernommene Konzepte | `InteractionObject`, `ControlSurface`, `Affordance`, `GuidanceContent`, StateMachines, Runtime-Reihenfolgen, Retry-Policies und SafetyCases werden als Modulbedarf abgegrenzt. |
| Beispielpfad A | Trace fuer dynamische Agentenmodellierung von `A-REQ-006` bis `A-VC-002-ROLE-BINDING`. |
| Beispielpfad B | Trace fuer Vivian/Kaffeemaschine von `B-REQ-011` bis `B-VC-005-CONFIRMATION-AND-START`. |
| Verbot direkte Runtime-Kopplung | `ScenarioStep -> RuntimeAction` bleibt in Invarianten und Modellentscheidung ausdruecklich ausgeschlossen. |

## Verifikation

| Pruefung | Ergebnis |
| --- | --- |
| Generatorlauf | erfolgreich. |
| `py_compile` fuer Generator | erfolgreich. |
| Spezifikation enthaelt `KERN-01`, `KERN-01a`, `KERN-02` | erfolgreich. |
| Spezifikation enthaelt A- und B-Beispielpfade | erfolgreich. |
| Spezifikation enthaelt neue Kardinalitaeten und Invarianten | erfolgreich. |
| Keine offensichtlichen Encoding-Artefakte wie Mojibake, Replacement-Character oder `??` | erfolgreich. |

## Abnahme

| Kriterium aus Task 13.7 | Erfuellung |
| --- | --- |
| Deutsche Beschreibung vorhanden | `dynamic_functional_mlds_specification.md` ist aktualisiert. |
| Beispiele vorhanden | Beispielpfade A und B sowie das Kaffeemaschinenbeispiel sind enthalten. |
| Modellentscheidung vorhanden | Kernanpassungen und abgegrenzte Ergaenzungsmodule sind beschrieben. |
| Neue/geaenderte Klassen beschrieben | `Entity` mit `Entity.kind` und `EntityKind` sind beschrieben. |
| Neue/geaenderte Beziehungen beschrieben | `Effect -> StateAssertion` ist beschrieben. |
| Kardinalitaeten beschrieben | `Entity.kind [0..1]` und `Effect.evidencedBy [0..*]` sind in der Kardinalitaetentabelle enthalten. |
| Invarianten beschrieben | Optionalitaet, erlaubte Enumeration, nicht-kompositive Evidence-Referenz und keine direkte Runtime-Kopplung sind enthalten. |
