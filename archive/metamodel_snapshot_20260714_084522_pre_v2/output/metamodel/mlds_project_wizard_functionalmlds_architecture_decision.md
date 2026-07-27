# Architekturentscheidung: FunctionalMLDS-Modus im MLDS Project Wizard

Stand: 2026-07-09

## Entscheidung

Der FunctionalMLDS-Modus erweitert die bestehenden Wizard-Endpunkte mit einem optionalen Feld `generation_mode`.

Verwendete Endpunkte bleiben:

- `POST /projects/arrow/analyze`
- `POST /projects/arrow/chat`
- `POST /projects/arrow/commit`

Neues Request-Feld:

`generation_mode: "legacy" | "functionalmlds"`

Wenn `generation_mode` fehlt oder leer ist, gilt immer `legacy`. Dadurch bleiben alle bestehenden Unity- und Backend-Aufrufe abwaertskompatibel.

## Begruendung

Der Unity-Wizard nutzt aktuell einen einzigen Dialogfluss:

1. MLDSI/MLDS laden.
2. Analyse starten.
3. optional per Chat verfeinern.
4. Projekt committen.

Dieser Ablauf passt fachlich fuer beide Zielartefakte. Der Unterschied liegt nicht im Bedienkonzept, sondern in der Backend-Erzeugung:

- Legacy erzeugt nur das bisherige Interactive-Agents-Projekt.
- FunctionalMLDS erzeugt zusaetzlich eine metamodel-konforme FunctionalMLDS-Instanz, Traceability und Validierungsreports.

Separate HTTP-Endpunkte wuerden den Unity-Code und die Bedienlogik doppeln, ohne fachlichen Mehrwert. Die klare Trennung soll stattdessen im Backend ueber getrennte Servicefunktionen erfolgen.

## Konsequenzen fuer das Backend

`/projects/arrow/analyze` entscheidet anhand von `generation_mode`:

- `legacy`: bestehende `analyze_arrow`-Logik unveraendert.
- `functionalmlds`: neuer Adapter fuer FunctionalMLDS-Analyse und Draft-Aufbau.

`/projects/arrow/chat` nutzt den Modus aus der gespeicherten Wizard-Session. Chat-Refinement muss spaeter entweder:

- im Legacy-Modus unveraendert bleiben, oder
- im FunctionalMLDS-Modus Aenderungen am FunctionalMLDS-Draft markieren und vor Commit erneut validieren.

`/projects/arrow/commit` nutzt ebenfalls den gespeicherten Session-Modus:

- `legacy`: bisheriger Commit unveraendert.
- `functionalmlds`: Pipeline-Materialisierung, Validierung und anschliessendes Schreiben des Unity-nutzbaren Projekts.

## Konsequenzen fuer Unity

Der Wizard erhaelt eine sichtbare Modusauswahl:

- Legacy Interactive Agents
- FunctionalMLDS

Unity sendet bei Analyze und Commit das Feld `generation_mode`. Fuer maximale Rueckwaertskompatibilitaet muss ein Backend ohne dieses Feld weiterhin wie bisher funktionieren.

## Validierungsgrenze

Im FunctionalMLDS-Modus ist ein Commit nur erfolgreich, wenn mindestens diese Pruefungen erfolgreich sind:

- Schema-Validierung
- FunctionalMLDS-Invariant-Validierung
- Projekt-Materialisierungsvalidierung
- Traceability-Metriken vorhanden

Die Antwort an Unity muss diese Evidenz enthalten, damit der Wizard nicht nur meldet, dass ein Projekt geschrieben wurde, sondern auch, dass es sich am Metamodell orientiert.

## Abwaertskompatibilitaet

Bestehende Requests ohne `generation_mode` muessen exakt weiterlaufen:

- keine geaenderte Pflichtstruktur in Legacy-Requests
- keine geaenderten Pflichtfelder in Legacy-Responses
- keine FunctionalMLDS-Dateien im Legacy-Modus
- keine `trace_map.json` im Legacy-Modus, solange nicht explizit FunctionalMLDS gewaehlt wurde

## Spaetere Erweiterbarkeit

Falls externe Clients spaeter explizit getrennte FunctionalMLDS-Endpunkte benoetigen, koennen diese als duenne Wrapper ueber dieselben internen Servicefunktionen ergaenzt werden. Fuer den Wizard-Umbau ist das nicht erforderlich.
