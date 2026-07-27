# FunctionalMLDS v0.5 Runtime-Archiv

Dieses Archiv bewahrt den unmittelbar vor der V2-Runtime-Anpassung verwendeten
v0.5-Implementierungsstand. Es ist ein Source-Overlay; grosse unveraenderte
Unity-Assets werden aus dem festgehaltenen Git/LFS-Commit rekonstruiert.

## Integritaet pruefen

```powershell
python verification/archive_functionalmlds_v05.py verify --output .
```

Neben dem Archiv liegt eine `.zip.sha256`-Datei fuer die Pruefung des ZIPs.

## Wiederherstellung

1. Unity-Basis auschecken und LFS-Inhalte laden:

```powershell
git clone https://git.informatik.fh-nuernberg.de/jobboerse/forschung/doktoranden/interactiveworlds/interactiveagentsfrontendunity.git InteractivAgents/InteractiveAgents2
git -C InteractivAgents/InteractiveAgents2 checkout c5bc0804de3ad834f7d4f033a172b2efa3d408b8
git -C InteractivAgents/InteractiveAgents2 lfs pull
```

2. Backend-Basis auschecken:

```powershell
git clone https://git.informatik.fh-nuernberg.de/jobboerse/forschung/doktoranden/interactiveworlds/interactiveagentsbackend.git InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents
git -C InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents checkout ec9bd4f15a6fd49ba1bce9c517f36f1a5adda7db
```

3. Den Inhalt von `source-overlay/` ueber den Workspace kopieren. Relative
   Pfade und Unity-`.meta`-Dateien muessen erhalten bleiben.
4. Das Modell-ZIP aus `model/` entpacken.
5. Eine lokale `config.json` neu anlegen. Zugangsdaten sind bewusst nicht im
   Archiv enthalten.
6. Das Laufzeitprofil explizit auf `v0.5` setzen.

Nicht wiederherzustellen sind `Library`, `Temp`, Logs, IDE-Caches,
`UserSettings`, Runtime-Logs oder das alte exportierte Unity-Paket. Unity baut
die Cache-Verzeichnisse neu auf; das Exportpaket ist kein Runtime-Eingang.

## Nichtregression

```powershell
python tools/dynamic_functional_mlds_v2_compat.py
python -m pytest -q tools/tests/test_dynamic_functional_mlds_v2_compat.py tools/tests/test_dynamic_functional_mlds_v2_validation.py
python -m pytest -q InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_functionalmlds_adapter_smoke.py InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests/test_backend_endpoints_smoke.py
```

Erwartet werden sieben verlustfreie v0.5-Roundtrips, 173 abgedeckte Pfade und
gueltige Schema-/Invariantenpruefungen aller sieben Golden-Fixtures.

Unity-Version: 6000.4.5f1. Der bekannte Editor-Smoke wird ueber
`QuickAgentManagerFunctionalMldsSmoke.Run` gestartet.
