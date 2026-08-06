# Implementierungsinventar: Dynamic Functional MLDS V2 und Unity

Stand: 14. Juli 2026. Alle Pfade sind relativ zum Workspace
`C:\Users\burklo\Documents\FunctionalMLDS` angegeben und wurden im Workspace
geprueft.

## Zweck und Autoritaetsreihenfolge

Die Implementierung besteht aus vier bewusst getrennten Ebenen. Bei einem
Widerspruch gilt folgende Reihenfolge:

1. Die ausgewaehlten EAST-ADL-V2.1.12-Metaklassen und das kanonische
   DFMLDS-V2-Autoritaetsmodell definieren die Semantik.
2. Der kanonische Python-Validator und das ausfuehrbare V2-JSON-Schema
   begrenzen gueltige Modelle beziehungsweise Runtime-Instanzen.
3. Pipeline und Backend erzeugen, materialisieren, pruefen und transportieren
   die Instanz, ohne neue Modellbeziehungen zu erfinden.
4. Unity konsumiert den gepinnten Vertrag und fuehrt nur exakt aufgeloeste
   Modellketten aus.

Unity, Backend-Trace und Dateinamen sind damit keine zweite Quelle fuer die
Metamodellsemantik.

## Aenderungsgrenze

### EAST-ADL-Schicht

`tools/dynamic_functional_mlds_v2_model.py` enthaelt einen ausgewaehlten,
unveraenderten Ausschnitt aus EAST-ADL V2.1.12. Der Validator
`tools/validate_dynamic_functional_mlds_v2.py` prueft unter anderem exakte
Basen und Eigenschaften sowie die einseitige Abhaengigkeit: DFMLDS darf
EAST-ADL importieren; EAST-ADL importiert DFMLDS nicht.

Projektbezogene Semantik wird deshalb in DFMLDS-Metaklassen und konservativen
Spezialisierungen modelliert. Beispiele sind `ConditionalExtend`,
`UseCaseScenarioSpecification`, `CapabilityUse`, `RuntimeBinding` und die
Assertion-Spezialisierungen. Bestehende EAST-ADL-Klassen werden dafuer nicht
umdefiniert oder mit lokalen Schattenattributen versehen.

### Authoring- und Kompatibilitaetsschicht

Das kanonische V2-Autoritaetsmodell bleibt in
`tools/dynamic_functional_mlds_v2_model.py`. Die vollstaendige Modell- und
Instanzpruefung liegt in `tools/validate_dynamic_functional_mlds_v2.py`.
`tools/dynamic_functional_mlds_v2_compat.py` bildet die explizite
v0.5-Kompatibilitaetsgrenze und den verlustfreien Roundtrip fuer darstellbare
v0.5-Daten ab.

Diese Ebene ist umfangreicher als das Unity-Laufzeitformat. Sie umfasst auch
Modellierungs-, Kompatibilitaets- und optionale Brueckenaspekte, die Unity
nicht zum Ausfuehren einer Session benoetigt.

### V2-Runtime-Schicht

`tools/case_study_pipeline/functionalmlds_v2_assembler.py` erzeugt aus der
semantischen v0.5-Projektion eine native, ausfuehrbare V2-Instanz. Das
Ergebnis besitzt den Diskriminator
`dynamic_functional_mlds_v2_instance`, die Modellversion `2.0.0-model`, die
Serialisierungsversion `1.0`, das Profil `executable` und ein universelles
`objects`-Array. Projektions-Ledger und v0.5-Hilfsfelder werden nicht in den
Runtime-Vertrag uebernommen; die Herkunft wird in `sourceContract`
festgehalten.

Die Runtime-Schicht ersetzt die v0.5-Datei nicht. Sie wird daneben erzeugt,
nach der Handoff-Ableitung materialisiert und mit einem versionierten V2-Trace
verbunden.

### Unity-Schicht

Unity ist ein strikt pruefender Verbraucher des ausfuehrbaren Profils.
`FunctionalMldsV2Loader` akzeptiert nur die native V2-Huelle und
`profile='executable'`. `FunctionalMldsV2QuickAgentBridge` vergleicht
Setup-Metadaten, Modellbytes, SHA-256 und jede abgeleitete Trace-Tatsache mit
den nativen Objekten. `QuickAgentManager` bricht Setup, Chat oder Handoff ab,
wenn der Vertrag nicht exakt aufloesbar ist.

Die eigenstaendigen Klassen fuer Szenarioablauf, Capability-Dispatch und
Assertion-Auswertung sind als native V2-Laufzeitbibliothek vorhanden. Der
aktuelle `QuickAgentManager` bindet davon den Anwendungsfluss
`setup`/`chat`/`handoff` ueber den Bridge-Vertrag ein; Unity wird dadurch
nicht zum Authoring-Werkzeug und veraendert das Modell nicht.

## Oberflaecheninventar

### Kanonisches Modell und Pruefung

| Oberflaeche | Reale Datei | Verantwortung |
|---|---|---|
| V2-Autoritaetsmodell | `tools/dynamic_functional_mlds_v2_model.py` | EAST-ADL-Ausschnitt, DFMLDS-Klassen, Assoziationen, Multiplizitaeten und Invarianten |
| Kanonischer Validator | `tools/validate_dynamic_functional_mlds_v2.py` | Modell- und Instanzregeln, EAST-ADL-Exaktheit, Referenz- und Profilpruefung |
| v0.5-Kompatibilitaet | `tools/dynamic_functional_mlds_v2_compat.py` | Import, Export, Projektions-Ledger und verlustfreier Roundtrip |
| Diagrammerzeugung | `tools/generate_dynamic_functional_mlds_v2.py`, `tools/dynamic_functional_mlds_v2_diagrams.py` | Ableitung der grafischen Fachsichten aus demselben Modell |
| Diagrammpruefung | `tools/validate_dynamic_functional_mlds_v2_diagrams.py` | Konsistenz- und Layoutpruefung der erzeugten Diagramme |

### Pipeline und JSON-Schemas

| Oberflaeche | Reale Datei | Verantwortung |
|---|---|---|
| Bestehende v0.5-Assembly | `tools/case_study_pipeline/functionalmlds_assembler.py` | Erzeugt weiterhin `functionalmlds.instance.generated.json` im v0.5-Vertrag |
| Handoff-Ableitung | `tools/case_study_pipeline/handoff_derivation.py` | Vervollstaendigt die v0.5-Semantik vor der V2-Projektion |
| Native V2-Assembly | `tools/case_study_pipeline/functionalmlds_v2_assembler.py` | Deterministische V2-Instanz und `functionalmlds.v2.assembly_report.json` |
| Projektmaterialisierung | `tools/case_study_pipeline/project_materializer.py` | Dualdateien, V2- und v0.5-Trace, Modellhash, Agentabbildung und Projektmetadaten |
| Batch-Reihenfolge | `tools/case_study_pipeline/run_batch_case_study.py` | `functionalmlds_assembly` -> `handoff_derivation` -> `functionalmlds_v2_assembly` -> `project_materialization` |
| Stage-Vollstaendigkeit | `tools/case_study_pipeline/stage_completion.py` | Fordert die drei Modellstufen, V2-Artefakt und V2-Assemblybericht explizit an |
| Runtime-Logpruefung | `tools/case_study_pipeline/runtime_logging.py` | Prueft gemischte Ereignisversionen und Trace-Referenzen |
| Gemeinsame Schema-Pruefung | `tools/case_study_pipeline/validators/schema_validator.py` | Erkennt `v0.5` oder `v2-dual`, prueft Dateien, Hash, kanonische Regeln und Runtime-Logs |
| Native Instanz | `tools/case_study_pipeline/schemas/dynamic_functional_mlds_v2_instance.schema.json` | Geschlossene V2-Runtime-Huelle und erlaubte native Objekte |
| Projektdateien | `tools/case_study_pipeline/schemas/interactive_agents_project.schema.json` | Projekt-, Agent-, Raum- und aktiver Trace-Vertrag fuer v0.5 oder V2 |
| V2-Ereignis | `tools/case_study_pipeline/schemas/runtime_event_v2.schema.json` | Runtime-Ereignis 2.0 mit vollstaendiger Modellkette |
| V2-Validierung | `tools/case_study_pipeline/schemas/runtime_validation_v2.schema.json` | `RuntimeValidationLog`, `RuntimeActualOutcome` und strukturierte `AssertionResult`-Eintraege |
| Legacy-Ereignis | `tools/case_study_pipeline/schemas/runtime_event.schema.json` | Bestehender Ereignisvertrag 1.0 fuer v0.5 |

### Backend

| Oberflaeche | Reale Datei | Verantwortung |
|---|---|---|
| Vertragsloader | `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/functionalmlds_v2_runtime.py` | Explizite Versionswahl, V2-/Legacy-Loader, Hash- und Trace-Pruefung, Runtime-Kontext und Aktionsauswahl |
| Sessionzustand | `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/state.py` | Vertrag beim Setup laden und pinnen, Drift vor Chat/Handoff pruefen, Modellbytes bereitstellen |
| HTTP-Oberflaeche | `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/server.py` | `/setup`, `/chat` und `GET /projects/{id}/functionalmlds-v2`; letzterer liefert exakt die gehashten Bytes |
| Backend-Logging | `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/runtime_trace.py` | Versioniertes Ereignis- und Validierungs-JSONL, V2-Tracebezug und transaktionales Schreiben beider Dateien |
| Wizard-/Pipeline-Adapter | `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/backend/functionalmlds_adapter.py` | V2-Assembly als explizite Stufe zwischen Handoff-Ableitung und Materialisierung |
| Materialisierte Projekte | `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/projects/<case-id>/` | `project.json`, Dualmodelle, Dualtraces, Agenten, Raumplan und KB |
| Verteilkopie fuer Unity | `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/unity_scripts/` | Synchronisierte C#-Quellen fuer Import/Weitergabe, einschliesslich `FunctionalMldsV2/` und Bridge |

### Unity

| Oberflaeche | Reale Datei | Verantwortung |
|---|---|---|
| Datenmodell | `InteractivAgents/InteractiveAgents2/Assets/Scripting/FunctionalMldsV2/FunctionalMldsV2Model.cs` | Native Dokument-/Objektform, Ausnahmen, Verdict-Lexeme |
| Loader und Index | `InteractivAgents/InteractiveAgents2/Assets/Scripting/FunctionalMldsV2/FunctionalMldsV2Loader.cs` | Sichere JSON-Deserialisierung, Byte-SHA-256, Objekt-/Besitzindex und Runtime-Invarianten |
| Runtime-Kontext | `InteractivAgents/InteractiveAgents2/Assets/Scripting/FunctionalMldsV2/FunctionalMldsV2RuntimeContext.cs` | Gepinnte Modellidentitaet, Session, Szenario und aktive Schritte |
| Szenarioausfuehrung | `InteractivAgents/InteractiveAgents2/Assets/Scripting/FunctionalMldsV2/FunctionalMldsV2ScenarioRunner.cs` | Ablauf nur ueber `StepRelation`, Guards, Wahrscheinlichkeiten, Fork/Join und Loop |
| Capability-Ausfuehrung | `InteractivAgents/InteractiveAgents2/Assets/Scripting/FunctionalMldsV2/FunctionalMldsV2CapabilityDispatcher.cs` | Exakte Kette von `CapabilityUse` zu `RuntimeBinding` und geordneten Aktionen |
| Assertion-Auswertung | `InteractivAgents/InteractiveAgents2/Assets/Scripting/FunctionalMldsV2/FunctionalMldsV2Assertions.cs` | Fuenf Assertion-Typen und vier Verdicts ueber einen expliziten Observation-Probe |
| Ereignislogger | `InteractivAgents/InteractiveAgents2/Assets/Scripting/FunctionalMldsV2/FunctionalMldsV2RuntimeLogger.cs` | Schema-2.0-JSONL mit exakt validierten Modellreferenzen |
| V&V-Recorder | `InteractivAgents/InteractiveAgents2/Assets/Scripting/FunctionalMldsV2/FunctionalMldsV2ValidationRecorder.cs` | Schema-kompatible Runtime-Validierungsartefakte |
| QuickAgent-Bridge | `InteractivAgents/InteractiveAgents2/Assets/Scripting/FunctionalMldsV2QuickAgentBridge.cs` | Setup-/Hash-/Trace-Pruefung und Logging fuer `setup`, `chat`, `handoff`, `runtime` |
| Anwendungsintegration | `InteractivAgents/InteractiveAgents2/Assets/Scripting/QuickAgentManager.cs` | Download des V2-Modells, fail-closed Initialisierung und Aktions-/Log-Aufrufe |
| Native Smoke | `InteractivAgents/InteractiveAgents2/Assets/InteractiveAgents/Editor/FunctionalMldsV2NativeSmoke.cs` | Loader, Runner, Dispatcher, Assertions, Logging, V&V und Negativmutationen |
| Bridge Smoke | `InteractivAgents/InteractiveAgents2/Assets/InteractiveAgents/Editor/FunctionalMldsV2QuickAgentBridgeSmoke.cs` | Setup-/Chat-/Handoff-Abbildung sowie Hash-, Ketten- und Trace-Mutationen |
| Smoke-Instanz | `InteractivAgents/InteractiveAgents2/Assets/InteractiveAgents/Editor/FunctionalMldsV2SmokeInstance.json` | Kleine ausfuehrbare native V2-Testinstanz |
| Abhaengigkeit | `InteractivAgents/InteractiveAgents2/Packages/manifest.json` | Direkte Newtonsoft-JSON-Abhaengigkeit `com.unity.nuget.newtonsoft-json` 3.2.2 |

Das Unity-Projekt verwendet laut
`InteractivAgents/InteractiveAgents2/ProjectSettings/ProjectVersion.txt` Unity
`6000.4.5f1`.

## Tests und lokale Nachweise

Die folgenden realen Tests decken die Schichtgrenzen ab:

| Nachweis | Reale Datei |
|---|---|
| Kanonisches V2-Modell und Instanzmutationen | `tools/tests/test_dynamic_functional_mlds_v2_validation.py` |
| Verlustfreie v0.5-Kompatibilitaet ueber sieben Fixtures | `tools/tests/test_dynamic_functional_mlds_v2_compat.py` |
| Native Assembly, alle sieben Fixtures, Assertion-/Runtime-Semantik | `tools/tests/test_functionalmlds_v2_runtime_assembler.py` |
| Dualmaterialisierung, Backendkontext, Logs und fail-closed Trace-Fakten | `tools/tests/test_v2_materializer_backend_contract.py` |
| V2-Agent-/Provider-Bijektion | `tools/tests/test_project_materializer_v2_agent_mapping.py` |
| v0.5-/V2-Dualschema und semantische Faelschungen | `tools/tests/test_schema_validator_dual_contract.py` |
| Reihenfolge Handoff vor V2 und Provenienz-Neuerzeugung | `tools/tests/test_v2_pipeline_provenance.py` |
| Session-Pinning, Drift und transaktionale Logfehler | `tools/tests/test_v2_session_runtime_hardening.py` |

Die zuletzt erzeugten Unity-Nachweise liegen unter
`output/unity_v2_alignment/`. Insbesondere dokumentiert
`unity_final_v2_compile.log` einen erfolgreichen Batchmode-Compile und
`unity_final_v2_smoke.log` den erfolgreichen
`FunctionalMldsV2QuickAgentBridgeSmoke`.

## Archivierter v0.5-Stand

Der unmittelbar vor der V2-Runtime-Anpassung gesicherte Stand liegt in:

- `archive/functionalmlds_implementation_v05_20260714_pre_v2_runtime/`
- `archive/functionalmlds_implementation_v05_20260714_pre_v2_runtime.zip`
- `archive/functionalmlds_implementation_v05_20260714_pre_v2_runtime.zip.sha256`

Die lokale Integritaetspruefung am 14. Juli 2026 ergab `status=pass`, 373
Manifest-Eintraege, sieben Fixtures und keine Secret-Funde. Der ZIP-SHA-256
lautet
`657626434B3DD7D3D80E070137CA795745B05D6079101738BB277C67320D7CDC`.
Die Wiederherstellung ist in
`archive/functionalmlds_implementation_v05_20260714_pre_v2_runtime/README_RESTORE.md`
beschrieben.
