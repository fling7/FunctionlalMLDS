# Interactive Agents mit FunctionalMLDS

Dieses Repository verbindet ein Python-Backend für interaktive Expert:innen-Agenten
mit einem Unity-Frontend und einer FunctionalMLDS-Modellierungs- und
Validierungspipeline. Es enthält den vollständigen Forschungsprototyp, Fallstudien,
Metamodell-Artefakte und automatisierte Akzeptanztests.

## Funktionsumfang

- dynamische Expert:innen-Agenten mit Persona, Expertise und lokaler Wissensbasis
- Chat, Agent-Handoffs, Speech-to-Text und Text-to-Speech
- Unity-Integration inklusive MLDSI Project Wizard und FunctionalMLDS-v2-Runtime
- Ableitung und Validierung von FunctionalMLDS-Fallstudien
- Kompatibilitätsabbildung zwischen FunctionalMLDS v0.5 und v2
- Runtime-Tracing, V&V-Artefakte und reproduzierbare Auswertungen

## Repository-Struktur

| Pfad | Inhalt |
| --- | --- |
| `InteractivAgents/InteractiveAgents2/` | vollständiges Unity-Projekt |
| `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/` | Python-Backend und wiederverwendbare Unity-Skripte |
| `tools/` | Generatoren, Validatoren, Pipeline und Tests |
| `output/` | erzeugte Modell-, Fallstudien- und Validierungsartefakte |
| `archive/` | versionierte Snapshots früherer Entwicklungsstände |

Unity-Caches (`Library`, `Temp`, `Logs`, `obj`), Python-Caches, lokale
Konfigurationen und generierte Smoke-Test-Projektkopien werden nicht versioniert.
Große Binärdateien werden über Git LFS verwaltet.

## Voraussetzungen

- Git mit Git LFS
- Python 3.11 oder neuer
- Unity `6000.4.5f1` für das vollständige Frontend
- optional ein OpenAI API-Key für modellgestützte Antworten, STT und TTS

Nach dem Klonen müssen die LFS-Dateien geladen sein:

```bash
git lfs install
git lfs pull
```

## Backend starten

```bash
cd InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents
python main.py
```

Das Backend verwendet standardmäßig `http://127.0.0.1:8787`. Eine lokale
`config.json` kann aus `config.example.json` abgeleitet werden; sie darf wegen
des API-Keys nicht committet werden.

Wichtige Endpunkte:

- `GET /health` und `GET /version`
- `POST /setup`
- `POST /chat`
- `POST /stt`
- `POST /tts`
- Projektverwaltung unter `/projects/...`

Weitere Backend-, API- und Konfigurationsdetails stehen in
[`InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/README.md`](InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/README.md).

## Unity-Projekt starten

1. Das Backend starten.
2. `InteractivAgents/InteractiveAgents2` mit Unity Hub und Unity `6000.4.5f1` öffnen.
3. Package- und Asset-Import abwarten.
4. `Assets/Scenes/MolkereiChampignion.unity` öffnen.
5. Play Mode starten.

Die Editor-Werkzeuge sind über `Tools > Project Manager` und
`Tools > MLDSI Project Wizard` erreichbar. Hinweise zum Unity-Projekt und zu den
Runtime Controls stehen in
[`InteractivAgents/InteractiveAgents2/README.md`](InteractivAgents/InteractiveAgents2/README.md).

## FunctionalMLDS erzeugen und validieren

Die zentralen Werkzeuge können direkt aus dem Repository-Root ausgeführt werden:

```bash
python tools/generate_dynamic_functional_mlds_v2.py
python tools/validate_dynamic_functional_mlds_v2.py
python tools/validate_dynamic_functional_mlds_v2_diagrams.py
```

Für die v0.5/v2-Kompatibilitätsabbildung:

```bash
python tools/dynamic_functional_mlds_v2_compat.py --help
```

Die Fallstudienpipeline befindet sich unter `tools/case_study_pipeline/`.
Standard-Eingaben, Schemas, Prompts und deterministische Reparaturregeln liegen
in den jeweiligen Unterverzeichnissen.

## Tests

Die Python-Testpakete können vom Repository-Root ausgeführt werden:

```bash
python -m pytest tools/tests
python -m pytest InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents/tests
```

Zusätzliche End-to-End- und Unity-Akzeptanzläufe:

```bash
python tools/run_dynamic_functional_mlds_v2_acceptance.py
python tools/run_unity_v2_alignment_acceptance.py
```

Einige Integrations- und Unity-Tests benötigen eine lokale Unity-Installation
beziehungsweise ein laufendes Backend.

## Sicherheit

Keine API-Keys oder Zugangsdaten committen. Insbesondere sind `config.json`,
`.env`-Dateien und private Schlüssel durch die Root-`.gitignore` ausgeschlossen.
