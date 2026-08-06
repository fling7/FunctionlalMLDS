# Arbeitsbaum- und Änderungsaudit

Stand: 14. Juli 2026

## Ausgangszustand und Schutz der Nutzeränderungen

Der Zustand unmittelbar vor der V2-Runtime-Anpassung ist im unveränderlichen
Archiv `archive/functionalmlds_implementation_v05_20260714_pre_v2_runtime/`
festgehalten. Die damaligen Git-Zustände stehen in
`git-state/unity-status.txt` und `git-state/backend-status.txt`; die tatsächlich
benötigten Quellen liegen im `source-overlay/` und sind über
`manifest.sha256.csv` abgesichert.

Bereits vor diesem Auftrag vorhandene Änderungen wurden nicht zurückgesetzt.
Das betrifft insbesondere die fünf Character-Hair-Materialien,
`Assets/Scripting/ArrowProjectWizard.cs`, die damals bereits geänderten
`QuickAgentManager.cs`, `backend/app.py`, `backend/kb.py`, `backend/server.py`,
`backend/state.py`, die bestehenden Projektverzeichnisse und Runtime-Logs. Wo
dieser Auftrag dieselben Integrationsdateien weiterentwickeln musste, bleibt der
vollständige vorherige Inhalt über das v0.5-Archiv wiederherstellbar.

Es wurden weder `git reset --hard` noch `git checkout --`, Repository-Cleanups
oder Löschungen fremder Arbeitsdateien ausgeführt. Entfernt wurde ausschließlich
ein während der Diagnose dieses Auftrags erzeugtes temporäres Debug-Verzeichnis,
nach expliziter Pfadprüfung innerhalb von `output/unity_v2_alignment`.

## Produktionsänderungen dieses Auftrags

- Native Unity-V2-Laufzeit unter
  `InteractivAgents/InteractiveAgents2/Assets/Scripting/FunctionalMldsV2/`
  sowie `FunctionalMldsV2QuickAgentBridge.cs`.
- V2-Integration im vorhandenen `QuickAgentManager.cs`, Editor-Smokes und
  V2-Fixture unter `Assets/InteractiveAgents/Editor/`.
- Explizite Newtonsoft-Abhängigkeit in `Packages/manifest.json`; der Lockfile
  löst dieselbe Version `3.2.2` auf.
- Bytegleiche Verteilkopien unter
  `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/unity_scripts/`.
- Versionierter Backend-Vertrag, gepinnte Sessions, transaktionale Runtime-
  Evidenz und exakter Modellendpunkt in `backend/`.
- Native V2-Assembly, duale Materialisierung, gemeinsame Validatoren, Schemata,
  Handoff-Modell-Scope und Pipeline-Reihenfolge unter
  `tools/case_study_pipeline/`.
- V2-Artefakte und Assembly-Reports neben allen sieben archivierten
  Golden-v0.5-Fällen; die v0.5-Dateien selbst sind bytegleich zum Archiv.
- Regressions-, Mutations-, Provenienz-, Session-, Agent-Mapping- und
  Abnahmetests unter `tools/tests/` und den Backend-Tests.

## Erzeugte Nachweise

Die auftragsbezogenen Berichte und Testlogs liegen ausschließlich unter
`output/unity_v2_alignment/`. Die maßgeblichen Dateien sind:

- `implementation_inventory.md`
- `implementation_matrix.md`
- `migration_and_operations_guide.md`
- `unity_v2_alignment_acceptance.json` und `.md`
- `pytest_tools_full_final.log`
- `pytest_backend_full_final.log`
- `unity_final_v2_compile.log`
- `unity_final_v2_smoke.log`
- `unity_final_native_v2_smoke.log`
- `unity_final_real_instance_validation.log`
- `unity_final_real_instance_smoke.log`
- `native_smoke_artifacts/runtime_event.v2.jsonl`
- `native_smoke_artifacts/runtime_validation.v2.json`

## Kontrollstand

- Tools-Gesamtsuite: 85 Tests und 58 Subtests bestanden.
- Backend-Gesamtsuite: 5 Tests und 23 Subtests bestanden.
- Unity: finaler Compile, QuickAgent-Bridge-Smoke, nativer V2-Smoke, reale
  292-Objekt-Validierung und realer HTTP-/Setup-Smoke bestanden.
- Archiv: 373 Manifest-Einträge, sieben Fixtures, keine Secret-Funde; ZIP-SHA-256
  `657626434B3DD7D3D80E070137CA795745B05D6079101738BB277C67320D7CDC`.
