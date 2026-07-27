# Migrations- und Betriebsleitfaden: FunctionalMLDS V2

Stand: 14. Juli 2026. Dieser Leitfaden beschreibt den aktuell implementierten
V2-Standardbetrieb, den bewusst separaten v0.5-Legacy-Modus und die
Wiederherstellung des archivierten Vorstands. Alle relativen Pfade beziehen
sich auf `C:\Users\burklo\Documents\FunctionalMLDS`.

## 1. Betriebsmodi

### V2-Standard: Dualprojekt

Ein neu materialisiertes FunctionalMLDS-Projekt ist ein V2-Dualprojekt. Der
aktive Runtime-Vertrag ist V2, waehrend das genaue v0.5-Artefakt fuer
Altanwendung, Vergleich und Rueckverfolgbarkeit daneben erhalten bleibt.

Der V2-Vertrag verwendet:

- Modellversion `2.0.0-model`
- Serialisierungsversion `1.0`
- Instanzschema `dynamic_functional_mlds_v2_instance`
- Profil `executable`
- Trace-Schema `functionalmlds_trace_map_v2`, Version `2.0`
- Runtime-Ereignisschema `functionalmlds_runtime_event`, Version `2.0`
- Runtime-Validierungsschema
  `dynamic_functional_mlds_v2_runtime_validation`, Version `2.0`

### Expliziter v0.5-Legacy-Modus

Ein Legacy-Projekt bleibt moeglich und wird nicht automatisch migriert. Es
deklariert `metamodelVersion` beziehungsweise
`functionalmlds_model_version` als `v0.5` (oder besitzt bei einem alten
Projekt noch keine Versionsangabe), verwendet als aktiven
`trace_map.json` das Schema `functionalmlds_trace_map` und kann die native
Legacy-Datei `functionalmlds.v05.instance.json` enthalten.

Ein Verzeichnis mit V2-Modell, V2-Trace oder V2-Metadaten darf nicht durch das
blosse Zuruecksetzen der Versionsnummer als Legacy betrieben werden. Der
Backend-Loader erkennt diese Mischung als Downgrade und bricht ab. Fuer einen
echten Legacy-Betrieb ist ein in sich geschlossenes v0.5-Projektverzeichnis
oder der archivierte Stand zu verwenden.

## 2. Erzeugungs- und Materialisierungsreihenfolge

Die verbindliche Reihenfolge ist:

1. `functionalmlds_assembly` erzeugt die bestehende v0.5-Instanz
   `functionalmlds/functionalmlds.instance.generated.json`.
2. `handoff_derivation` vervollstaendigt und validiert die Handoff-Semantik.
3. `functionalmlds_v2_assembly` projiziert danach die native V2-Instanz und
   schreibt den Assemblybericht.
4. `project_materialization` schreibt das Dualprojekt in das Backend.
5. `schema_validation` prueft beide Modelle, beide Traces, Projektmetadaten,
   Hash, kanonische V2-Regeln und vorhandene Runtime-Logs.

Diese Reihenfolge steht sowohl in
`tools/case_study_pipeline/run_batch_case_study.py` als auch in
`InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/functionalmlds_adapter.py`.
`tools/case_study_pipeline/stage_completion.py` fordert Handoff-Ableitung vor
V2-Assembly sowie den gueltigen V2-Assemblybericht explizit an.

Fuer eine einzelne bereits vorhandene v0.5-Datei kann die native Projektion
direkt erzeugt werden:

```powershell
python tools\case_study_pipeline\functionalmlds_v2_assembler.py `
  output\case_studies\classroom_dinosaur\functionalmlds\functionalmlds.instance.generated.json `
  output\case_studies\classroom_dinosaur\functionalmlds\functionalmlds.v2.instance.json
```

Dieser direkte Aufruf schreibt nur die angegebene Instanz. Fuer einen
vollstaendigen Betriebsstand sind die Pipeline-Stufen einschliesslich
Handoff-Ableitung, Assemblybericht, Materialisierung und Schema-Pruefung zu
verwenden.

Eine oder mehrere Fallstudien koennen nach der Materialisierung so geprueft
werden:

```powershell
python -m tools.case_study_pipeline.validators.schema_validator `
  --case-dir output\case_studies\classroom_dinosaur `
  --backend-root InteractivAgents\openai_unity_expert_npcs_pycharm\InteractiveAgents
```

## 3. Erwartete Dateien eines Dualprojekts

Im Fallstudienverzeichnis:

| Datei | Rolle |
|---|---|
| `functionalmlds/functionalmlds.instance.generated.json` | unveraenderte v0.5-Quelle fuer die V2-Projektion |
| `functionalmlds/functionalmlds.v2.instance.json` | native ausfuehrbare V2-Instanz |
| `functionalmlds/functionalmlds.v2.assembly_report.json` | kanonischer V2-Pruefbericht der Assembly |
| `validation/handoff_derivation_validation.json` | Nachweis der vorgelagerten Handoff-Ableitung |
| `validation/project_materialization_validation.json` | Pruefung der Backend-Projektdateien |
| `validation/schema_validation.json` | gemeinsamer v0.5-/V2-/Runtime-Schemanachweis |

Im Backend-Projektverzeichnis
`InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/<case-id>/`:

| Datei | Rolle |
|---|---|
| `functionalmlds.v2.instance.json` | aktives, gehashtes V2-Modell |
| `functionalmlds.v05.instance.json` | explizit erhaltenes Legacy-Modell |
| `trace_map.v2.json` | V2-Trace mit exakten nativen IDs und abgeleiteten Fakten |
| `trace_map.v05.json` | explizit erhaltener Legacy-Trace |
| `trace_map.json` | aktive Sicht; im V2-Dualprojekt JSON-inhaltlich identisch mit `trace_map.v2.json` |
| `project.json` | Versions-, Profil-, Pfad- und SHA-256-Pinning |
| `agents.json`, `room_plan.json`, `kb/` | bestehende Interactive-Agents-Projektdateien mit nativen Agentreferenzen |

Fuer V2 muessen in `project.json` mindestens folgende Werte konsistent sein:

```json
{
  "generation_mode": "functionalmlds",
  "metamodelVersion": "2.0.0-model",
  "functionalmlds_model_version": "2.0.0-model",
  "functionalmlds_model_schema": "dynamic_functional_mlds_v2_instance",
  "functionalmlds_profile": "executable",
  "functionalmlds_model_path": "functionalmlds.v2.instance.json",
  "functionalmlds_legacy_path": "functionalmlds.v05.instance.json",
  "functionalmlds_trace_map_path": "trace_map.v2.json",
  "functionalmlds_legacy_trace_map_path": "trace_map.v05.json",
  "functionalmlds_trace_schema_version": "2.0"
}
```

`functionalmlds_model_sha256` muss dem SHA-256 der tatsaechlichen Bytes von
`functionalmlds.v2.instance.json` entsprechen. Schon reines Neuformatieren
der JSON-Datei aendert den Hash; Modell, Traces und Projektmetadaten muessen
dann gemeinsam neu erzeugt werden.

## 4. Setup- und Runtime-Vertrag

### Backend-Setup

Ein Projektsetup beginnt mit `POST /setup` und einem `project_id`. Der
Backend-Loader in `backend/functionalmlds_v2_runtime.py`:

1. entscheidet anhand expliziter Version und vorhandener Artefakte zwischen
   `v2` und `v05`,
2. prueft Modellhuelle, Profil, Wurzel und runtime-relevante Invarianten,
3. prueft Modellhash und V2-Trace,
4. prueft jede vollstaendige Kette
   `ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`,
5. vergleicht Ziele, Assertions, ValidationCases, RuntimeValidationTargets,
   Locator und `applicationActionKind` exakt mit dem Modell und
6. erzeugt den kompakten Runtime-Kontext.

Die Setup-Antwort enthaelt fuer V2 insbesondere:

- `metamodel_version`
- `trace_schema_version`
- `model_sha256`
- `functionalmlds_profile`
- `functionalmlds_model_endpoint`
- `functionalmlds` als Runtime-Kontext
- native Agent-/Entity-Referenzen in den Agentdaten

`GET /projects/{project-id}/functionalmlds-v2` liefert die exakten Bytes der
gehashten Modellinstanz und keine neu serialisierte Variante.

### Unity-Setup

`QuickAgentManager.cs` wertet die Setup-Antwort mit
`FunctionalMldsV2QuickAgentBridge` aus. Im V2-Modus wird das Modell vom
angegebenen Endpunkt geladen. Die Bridge prueft Version, Profil, Case,
SHA-256, Hauptszenario und alle Trace-Abbildungen erneut gegen die nativen
Objekte. Ein fehlender oder mehrdeutiger Setup-/Chat-/Handoff-Pfad verwirft
das Setup.

Bei einem expliziten v0.5- oder unversionierten direkten Setup liefert
`ModelEndpointFor` keinen V2-Endpunkt. Dann bleibt der bisherige
QuickAgent-Ablauf aktiv; es findet keine verdeckte V2-Konvertierung statt.
Unbekannte Versionen und unvollstaendige V2-Antworten werden fail-closed
abgelehnt.

### Session-Pinning und Drift

Das Backend pinnt beim Setup den vollstaendigen V2-Vertragsfingerprint in der
Session. Vor Chat und Handoff werden Projektvertrag und konkrete Aktion erneut
aufgeloest. Weichen Modell, Trace oder Aktionsabbildung ab, wird die Operation
vor der dauerhaften Sessionmutation abgebrochen. Das schuetzt eine laufende
Session vor nachtraeglich ausgetauschten Projektdateien.

## 5. Runtime-Logging und V&V

### Backend-Logs

Das Backend schreibt Ereignisse nach
`<case-dir>/runtime_logs/events.jsonl`, wenn `functionalmlds_trace_path` auf
die Fallstudie zeigt; andernfalls in
`<backend-project>/runtime_logs/events.jsonl`. Zugehoerige V2-Ergebnisse
liegen daneben in `runtime_validation.v2.jsonl`.

Fuer V2 werden Ereignis und Validierung transaktional geschrieben. Schlaegt
das Schreiben einer der beiden Dateien fehl, werden beide Dateistaende und
bei HTTP-Chat auch der Sessionzustand zurueckgerollt.

### Unity-Logs

Unity schreibt einen getrennten lokalen Strom unter:

```text
<Application.persistentDataPath>/FunctionalMLDS/<project-id>/events.v2.jsonl
<Application.persistentDataPath>/FunctionalMLDS/<project-id>/runtime_validation.v2.jsonl
```

Bei einem direkten Setup ohne Projekt-ID wird `direct` als Verzeichnisname
verwendet.

Jedes V2-Ereignis fuehrt Modellversion, Modellhash und die exakten IDs fuer
Schritt, CapabilityUse, Capability, Provider, Ziele, Binding, RuntimeAction,
Assertions, ValidationCases und RuntimeValidationTargets. Die Logger raten
diese IDs nicht aus Namen oder Endpunkten.

Ein erfolgreicher HTTP-/Unity-Transport ist noch kein fachlicher Nachweis.
Solange kein Domain-Probe die Assertion tatsaechlich auswertet, wird das
Verdict deshalb als `inconclusive` aufgezeichnet. `pass` ist nur fuer eine
fachlich ausgewertete Assertion vorgesehen.

## 6. Unity bauen und Smokes ausfuehren

Vorausgesetzt werden Unity `6000.4.5f1` und die im Projektmanifest deklarierte
Abhaengigkeit `com.unity.nuget.newtonsoft-json` `3.2.2`.

Batchmode-Compile:

```powershell
& "C:\Program Files\Unity\Hub\Editor\6000.4.5f1\Editor\Unity.exe" `
  -batchmode -nographics -quit `
  -projectPath "C:\Users\burklo\Documents\FunctionalMLDS\InteractivAgents\InteractiveAgents2" `
  -logFile "C:\Users\burklo\Documents\FunctionalMLDS\output\unity_v2_alignment\unity_final_v2_compile.log"
```

QuickAgent-Bridge-Smoke:

```powershell
& "C:\Program Files\Unity\Hub\Editor\6000.4.5f1\Editor\Unity.exe" `
  -batchmode -nographics -quit `
  -projectPath "C:\Users\burklo\Documents\FunctionalMLDS\InteractivAgents\InteractiveAgents2" `
  -executeMethod FunctionalMldsV2QuickAgentBridgeSmoke.RunFromCommandLine `
  -logFile "C:\Users\burklo\Documents\FunctionalMLDS\output\unity_v2_alignment\unity_final_v2_smoke.log"
```

Ein gueltiger Smoke endet im Log mit
`[FunctionalMldsV2QuickAgentBridgeSmoke] OK`. Die Menue-/Editor-Smokes liegen
in `Assets/InteractiveAgents/Editor/FunctionalMldsV2NativeSmoke.cs` und
`FunctionalMldsV2QuickAgentBridgeSmoke.cs`.

## 7. v0.5-Archiv verifizieren

Das unveraenderliche Source-Overlay liegt unter
`archive/functionalmlds_implementation_v05_20260714_pre_v2_runtime/`; daneben
liegen ZIP und SHA-Datei.

Normale Archivintegritaet pruefen:

```powershell
python tools\archive_functionalmlds_v05.py verify `
  --output archive\functionalmlds_implementation_v05_20260714_pre_v2_runtime
```

Die am 14. Juli 2026 erneut ausgefuehrte Pruefung ergab:

- Status `pass`
- 373 Manifest-Eintraege
- sieben v0.5-Fixtures
- keine Secret-Funde
- ZIP-SHA-256
  `657626434B3DD7D3D80E070137CA795745B05D6079101738BB277C67320D7CDC`

Den ZIP-Hash unabhaengig vergleichen:

```powershell
(Get-FileHash `
  archive\functionalmlds_implementation_v05_20260714_pre_v2_runtime.zip `
  -Algorithm SHA256).Hash
```

Die Option `--check-sources` vergleicht das Overlay zusaetzlich mit dem
aktuellen Workspace. Nach der beabsichtigten V2-Weiterentwicklung muessen
diese Quellen abweichen; fuer eine reine Archivintegritaetspruefung ist die
Option deshalb nicht zu setzen. Sie ist fuer einen rekonstruierten alten
Arbeitsbaum oder eine Baseline-Pruefung vor Aenderungen gedacht.

## 8. v0.5-Stand wiederherstellen

Das Archiv ist ein Source-Overlay, kein vollstaendiger Unity-Cache und kein
vollstaendiger Ersatz fuer die Git-/LFS-Basis. Die verbindliche Detailanleitung
steht in
`archive/functionalmlds_implementation_v05_20260714_pre_v2_runtime/README_RESTORE.md`.

Kurzablauf:

1. Unity-Basis aus dem dort genannten Repository auf Commit
   `c5bc0804de3ad834f7d4f033a172b2efa3d408b8` auschecken und `git lfs pull`
   ausfuehren.
2. Backend-Basis auf Commit
   `ec9bd4f15a6fd49ba1bce9c517f36f1a5adda7db` auschecken.
3. `source-overlay/` ueber den rekonstruierten Workspace kopieren. Relative
   Pfade und Unity-`.meta`-Dateien muessen erhalten bleiben.
4. Das Modell-ZIP aus `model/` entpacken.
5. Eine lokale `config.json` mit den benoetigten Zugangsdaten neu anlegen.
   Credentials sind absichtlich nicht archiviert.
6. Das Laufzeitprofil explizit auf `v0.5` setzen und die im Archiv-README
   genannten Nichtregressionstests ausfuehren.

Nicht archiviert sind Unity `Library`, `Temp`, Logs, IDE-Caches,
`UserSettings`, Runtime-Logs, lokale Credentials und das alte exportierte
Unity-Paket. Unity erzeugt die Cache-Verzeichnisse neu; grosse unveraenderte
Assets werden ueber Git LFS wiederhergestellt.

Eine Wiederherstellung sollte in einem separaten Zielverzeichnis erfolgen.
Das Overlay darf nicht ungeprueft ueber den aktiven V2-Arbeitsbaum kopiert
werden.

## 9. Bekannte Betriebsgrenzen

- Die Unity-Runtime akzeptiert nur das Profil `executable`. Das vollstaendige
  Authoring-Modell, optionale Annex-C-/Feature-/Knowledge-Bruecken und
  Kompatibilitaets-Ledger sind keine Unity-Runtime-Eingaenge.
- Der native `FunctionalMldsV2ScenarioRunner`, Capability-Dispatcher und
  Assertion-Evaluator sind implementiert und im Editor-Smoke geprueft. Der
  bestehende `QuickAgentManager` nutzt im Produktpfad derzeit die exakten
  Setup-/Chat-/Handoff-Abbildungen und ersetzt nicht automatisch jede
  bestehende Gameplay-Steuerung durch den allgemeinen ScenarioRunner.
- Unity- und Backend-JSONL sind getrennte Evidenzstroeme. Sie werden nicht
  automatisch zu einer einzigen Datei zusammengefuehrt.
- Die V2-Aktionsart kommt aus dem expliziten
  `SchemaReference.text.applicationActionKind`. IDs, Namen und Locator werden
  im V2-Pfad nicht zur Klassifikation geraten. Solche Heuristiken existieren
  nur im getrennten Legacy-Loader.
- Das V2-Modell wird bytegenau gehasht. Manuelle Bearbeitung von Modell,
  Trace oder `project.json` kann einen Vertrag ungueltig machen und verlangt
  eine gemeinsame Neuerzeugung.
- Ein laufender V2-Sessionvertrag ist gepinnt. Projektupdates erfordern ein
  neues `/setup`; sie werden nicht still in eine bestehende Session uebernommen.
- Ein Transporterfolg bleibt ohne fachliche Beobachtung `inconclusive`.
  Fuer belastbare `pass`-/`fail`-Ergebnisse muss ein Domain-Probe konkrete
  Modellsubjects beobachten und mit der `EAExpression` auswerten.
- Das v0.5-Archiv enthaelt bewusst keine Geheimnisse und keine generierten
  Caches. Eine vollstaendige Altumgebung benoetigt die dokumentierten
  Git-/LFS-Basen und lokal neu konfigurierte Zugangsdaten.
