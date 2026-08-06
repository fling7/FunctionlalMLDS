# Analyse: Interactive Agents Unity-Projekt mit Python-Backend

Stand: 2026-07-08

## 1. Untersuchte Bestandteile

Im Projektordner liegen zwei zusammengehörige Teile:

- `InteractivAgents/InteractiveAgents2`: das eigentliche Unity-Projekt.
- `InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents`: Python-Backend, Beispielprojekte, Wissensbasis und kopierbare Unity-Skripte.

Das Unity-Projekt nutzt Unity `6000.4.5f1`. Die Hauptszene laut README ist `Assets/Scenes/MolkereiChampignion.unity`. Relevante Unity-Pakete sind unter anderem WebXR, XR Interaction Toolkit, Input System, URP, Unity AI Assistant/Inference und Unity Test Framework.

## 2. Architekturüberblick

Das System besteht aus vier Ebenen:

1. Unity-Runtime: `QuickAgentManager.cs`
   - ruft `/setup`, `/chat`, `/tts`, `/stt` und `/projects` auf,
   - spawnt Agenten als Character-Prefabs oder Würfel-Fallback,
   - verwaltet aktive Agenten, Chat-Logs, FPV-Modus, Handoff-Visualisierung, TTS und Voice Input.

2. Unity-Editor-Werkzeuge:
   - `ProjectManagerUI.cs`: Projekte, Agenten, Stimmen, Positionen und Wissen bearbeiten.
   - `ArrowProjectWizard.cs`: MLDSI/JSON analysieren, mit dem Entwurf chatten und als Projekt committen.
   - `InteractiveAgentsPackageUtility.cs`: Manager anlegen, Installation prüfen, Unity-Package exportieren.

3. Python-Backend:
   - `server.py`: eigener HTTP-Server auf Basis von `ThreadingHTTPServer`.
   - `state.py`: Session-State, Agentenspezifikation, Chat-Orchestrierung, Handoff, MLDSI-Projekterzeugung.
   - `placement.py`: Agentenplatzierung über explizite Positionen, Spawnpoints, Zonen, Tags und MLDS-Objektschnitte.
   - `kb.py`: lokale Keyword-Wissenssuche.
   - `openai_client.py`: OpenAI Responses API, TTS und STT über Standardbibliothek.
   - `projects.py`: persistente Projektordner mit `project.json`, `room_plan.json`, `agents.json`, `kb/`.

4. Persistente Daten:
   - globale Wissensbasis unter `kb/<tag>/...`,
   - projektspezifische Daten unter `projects/<project_id>/...`,
   - Beispiel-MLDS-Dateien im Unity-Projekt (`BestfitMLDS.json`, `KlassenraumMLDS.json`, `MLDSSteinpilz.json`).

## 3. Laufzeitablauf

### Setup

Unity ruft `POST /setup` auf. Das Backend akzeptiert drei Varianten:

- direkte Daten im Request,
- Pfade innerhalb des Backend-Projekts,
- `project_id`.

Bei `project_id` lädt das Backend:

- `projects/<project_id>/room_plan.json`,
- `projects/<project_id>/agents.json`,
- `projects/<project_id>/kb/`.

Danach erzeugt `SessionStore.create_session` eine `SessionState` mit Agenten, Placement-Daten, KnowledgeBase und Memory-Modus. Unity erhält nur die für die Szene nötigen Daten: Agent-ID, Anzeigename, Voice-Settings, Position, Blickrichtung, Spawnpoint, Zone und Tags. Persona, Expertise und `knowledge_tags` bleiben Backend-Kontext.

### Agentenplatzierung

Die Platzierung ist mehrstufig:

1. Explizite Agentenpositionen werden bevorzugt.
2. Explizite `spawn_point_id` wird verwendet, wenn gültig und frei.
3. Ansonsten matcht `assign_spawn_points` Agentenpräferenzen auf `preferred_zone_ids` und `preferred_spawn_tags`.
4. Falls keine Spawnpoints vorhanden oder frei sind, werden Defaultpositionen kreisförmig erzeugt.
5. Für MLDS-Szenen werden Hindernisse aus `scene.objects` als 2D-Footprints geschnitten; strukturelle Elemente wie floor, ceiling, wall werden ignoriert.

Das ist für dynamisches Modellieren von Agenten in einer Szene bereits stark: Agenten sind räumlich verankert, haben Position, Blickrichtung, Zone, Spawnpoint und semantische Tags.

### Chat

Unity sendet an `POST /chat`:

- `session_id`,
- `active_agent_id`,
- `user_text`.

Das Backend:

1. sucht die Session,
2. bestimmt den aktiven Agenten,
3. sucht lokale KB-Snippets über `knowledge_tags`,
4. baut einen Developer-Prompt aus Persona, Expertise, Kommunikationsregeln, Handoff-Regeln, anderen Agenten und KB-Snippets,
5. ruft die OpenAI Responses API mit Structured Output auf,
6. normalisiert `say`, `handoff_to`, `handoff_reason`, `handoff_brief`, `confidence`,
7. gibt Events an Unity zurück.

Die Antwort hat eine klare Ereignisstruktur:

```json
{
  "session_id": "...",
  "active_agent_id": "agent_b",
  "memory_mode": "shared_history",
  "handoff": {
    "from": "agent_a",
    "to": "agent_b",
    "reason": "...",
    "brief": "..."
  },
  "events": [
    {"type": "say", "agent_id": "agent_a", "text": "..."},
    {"type": "say", "agent_id": "agent_b", "text": "..."}
  ]
}
```

### Handoff

Handoff ist modellgestützt, aber technisch begrenzt:

- Das Structured-Output-Schema erlaubt als `handoff_to` nur IDs anderer Agenten oder `null`.
- Das Backend prüft zusätzlich, ob die ID existiert und nicht der eigene Agent ist.
- `max_handoffs` begrenzt Kettenweiterleitungen.
- Im Zielagenten-Aufruf ist Handoff deaktiviert.

Es gibt zwei Memory-Modi:

- `shared_history`: alle Agenten teilen dieselbe History.
- `agent_private_history`: jeder Agent hat eigene History; beim Handoff wird nur ein kompakter `handoff_brief` übergeben.

Unity visualisiert Handoff im normalen Modus über Bubbles und im FPV-/Proximity-Modus als ausstehende Weiterleitung: Der Nutzer muss zum Zielagenten laufen, bevor dessen Antwort angezeigt wird. Die echte Unity-Version enthält eine weiterentwickelte Handoff-Routenanzeige mit Hindernis-/Colliderbezug.

### Voice und Audio

Desktop/Editor:

- Unity nimmt Audio mit `Microphone` auf,
- kodiert WAV,
- sendet Multipart an `/stt`,
- sendet das Transkript optional automatisch an `/chat`.

WebGL/WebXR:

- `WebGLVoiceBridge.jslib` nutzt `getUserMedia` und `MediaRecorder`,
- sendet WebM/Opus direkt an `/stt`,
- gibt JSON über `SendMessage` zurück an Unity.

TTS:

- Unity sendet Text und Voice-Settings an `/tts`.
- Backend ruft OpenAI Audio Speech auf.
- Unity cached AudioClips pro `agentId::text`.

## 4. Datenmodell des Projekts

### Project

Ein Projekt ist ein Ordner:

```text
projects/<project_id>/
  project.json
  room_plan.json
  agents.json
  kb/
    <tag>/
      <entry>.txt
```

### AgentSpec

Relevante Felder:

- `id`
- `display_name`
- `persona`
- `expertise`
- `knowledge_tags`
- `preferred_zone_ids`
- `preferred_spawn_tags`
- `position`
- `forward`
- `spawn_point_id`
- `zone_id`
- `tags`
- `voice`, `voice_style`, `tts_model`

### RoomPlan

Zwei Formen werden unterstützt:

1. Einfaches RoomPlan-Format:
   - `zones`
   - `spawn_points`
   - optional `objects`, `furniture`, `props`, `fixtures`, `obstacles`

2. MLDS-Szenenformat:
   - `scene.environment.dimensions`
   - `scene.objects`
   - `objectType`, `group`, `position`, `dimensions`

### KnowledgeBase

Wissen ist dateibasiert. Retrieval ist keine Vektorsuche, sondern einfache Keyword-Überlappung:

- Tokenisierung der Nutzerfrage,
- Filterung nach Agent-`knowledge_tags`,
- Sortierung nach Overlap-Score,
- Übergabe der Top-Snippets in den Prompt.

## 5. Bezug zum Metamodell

Für dein dynamisches Metamodell ist das Projekt sehr relevant, weil es mehrere konkrete Laufzeitkonzepte liefert:

- `Agent`: direkt durch `AgentSpec` abbildbar.
- `Scene`/`RoomPlan`: durch `room_plan.json` beziehungsweise MLDS-Szene abbildbar.
- `SpatialPlacement`: Position, Forward, Zone, Spawnpoint und Tags sind vorhanden.
- `ScenarioStep`: Setup, Chat, Handoff, Voice-Transkription, TTS-Ausgabe und Proximity-Arrival sind als Laufzeitereignisse modellierbar.
- `Event`: User-Chat, Voice-Transcript, Agent-Say, Handoff, Arrival beim Zielagenten.
- `Capability`: Antworten, Weiterleiten, Sprechen, Transkribieren, Agentenplatzierung, Projektgenerierung.
- `RuntimeBinding`: Unity-WebRequest zu Backend-Endpunkten, Backend-Aufruf zu OpenAI APIs.
- `MemoryPolicy`: `shared_history` und `agent_private_history`.
- `KnowledgeScope`: `knowledge_tags` je Agent.

Für den Anwendungsfall "dynamisches Modellieren von Agenten in einer Szene" ist das bestehende System gut abbildbar.

Für den Anwendungsfall "Interaktionsobjekte mit Vivian, z. B. Bedienung einer Kaffeemaschine" reicht die aktuelle Implementierung nur teilweise:

- Geometrische Objekte sind über MLDS/RoomPlan vorhanden.
- Semantisches Wissen über Objekte kann in `kb/` liegen.
- Es fehlt aber ein explizites Laufzeitmodell für Objektzustände, Affordances, Bedienhandlungen, Preconditions, Effects und Tool-/Unity-Actions.

Dafür sollte das Metamodell entweder erweitert oder ein ergänzendes Object-Interaction-Modell eingehängt werden. Sinnvolle Zusatzklassen wären:

- `InteractiveObject`
- `Affordance`
- `ObjectState`
- `InteractionAction`
- `Precondition`
- `Effect`
- `RuntimeCommand`
- `Observation`

Damit wäre z. B. eine Kaffeemaschine nicht nur ein `objectType: coffee_machine`, sondern ein interaktives System mit Zuständen wie `idle`, `water_missing`, `beans_missing`, `brewing`, `coffee_ready` und Aktionen wie `pressPower`, `insertCup`, `selectProgram`, `startBrewing`.

## 6. Stärken

- Klare Trennung zwischen Unity-Frontend, Backend-Orchestrierung und persistenten Projektdateien.
- Agentenrollen sind nicht fest verdrahtet, sondern datengetrieben.
- Handoff ist durch Structured Output kontrolliert und nicht nur freier Text.
- Memory-Modi erlauben Vergleich zwischen globalem und agentenspezifischem Gesprächsgedächtnis.
- Unity-Editor-Werkzeuge machen das System für nicht rein technische Workflows benutzbar.
- MLDSI-Wizard schlägt Agenten, Wissen und Positionen aus einer Szenenbeschreibung vor.
- WebGL-Voice-Bridge berücksichtigt Browserrestriktionen.
- Backend-Dateizugriffe für Setup-Pfade sind auf das Projektverzeichnis begrenzt.

## 7. Risiken und konkrete Befunde

1. `QuickAgentManager.cs` ist sehr groß und bündelt viele Verantwortlichkeiten.
   - Netzwerk, UI, FPV, Spawning, Collider, Handoff-Routing, TTS und STT liegen in einer Klasse.
   - Für Forschung/Dissertation verständlich als Prototyp, aber schwer wartbar.

2. Es gibt zwei `QuickAgentManager.cs`-Stände.
   - Das echte Unity-Projekt und die Backend-Kopiervorlage unterscheiden sich stark.
   - Die Unity-Version enthält die neuere Handoff-Routenlogik.
   - Gefahr: Import-Package oder Dokumentation exportiert einen veralteten Stand, wenn nicht synchronisiert.

3. `tts_model: "standard"` ist inkonsistent.
   - Einige Beispielagenten verwenden `standard`.
   - Der `/tts`-Endpunkt normalisiert `standard` nicht, sondern würde es als Modellnamen weitergeben.
   - Andere Teile des Codes normalisieren `standard` bereits zu `gpt-4o-mini-tts`.
   - Empfehlung: zentral im Backend und/oder in Unity normalisieren.

4. Retrieval ist bewusst einfach.
   - Für kleine lokale Demos gut erklärbar.
   - Für fachlich präzises Wissen nicht ausreichend robust gegenüber Synonymen, Paraphrasen und langen Dokumenten.
   - Für eine wissenschaftliche Arbeit sollte klar abgegrenzt werden: lokales Keyword-RAG, kein semantisches RAG.

5. Sessions liegen nur im Speicher.
   - Neustart des Backends löscht Sessions.
   - Keine Persistenz für Chatverlauf.
   - Kein Locking um `sessions`/`arrow_sessions` trotz `ThreadingHTTPServer`; parallele Requests können Race Conditions erzeugen.

6. CORS ist offen.
   - Lokal praktisch.
   - Für Deployment zu offen, insbesondere mit `Access-Control-Allow-Origin: *`.

7. Keine Authentifizierung.
   - Jeder erreichbare Client kann Projekte lesen, ändern, Wissen löschen, STT/TTS/Chat auslösen.
   - Für lokale Forschung okay, für produktive Umgebung nicht.

8. Tests fehlen praktisch.
   - Python-Dateien kompilieren syntaktisch.
   - Unity Test Framework ist installiert, aber ich habe keine projektspezifischen Tests außerhalb Package-Samples gefunden.
   - Besonders testwürdig: Placement, Handoff-Schema, `standard`-TTS-Normalisierung, Projekt-API und Pfadsicherheit.

9. `JsonUtility` ist schemaempfindlich.
   - Unitys `JsonUtility` ist einfach und schnell, aber nicht flexibel bei dynamischen JSON-Strukturen.
   - Das System funktioniert, solange Backend-Antworten exakt zu den C#-DTOs passen.
   - Für stärkere Evolution wäre eine robustere JSON-Schicht sinnvoll.

10. `config.json` enthält sensible Konfiguration.
    - Im Backend ist `config.json` durch `.gitignore` ausgeschlossen.
    - Der lokale API-Key sollte nicht in Berichte, Logs oder Commits gelangen.

## 8. Verifikation

Durchgeführt:

- Projektstruktur und relevante Dateien identifiziert.
- Unity-Projektversion und Package-Manifest geprüft.
- Unity Runtime-/Editor-Skripte analysiert.
- Backend-Module analysiert.
- Beispiel- und Projektdateien stichprobenartig geprüft.
- Python-Backend mit `py_compile` syntaktisch geprüft: keine Compile-Fehler.
- Hashvergleich der doppelten Unity-Skripte durchgeführt.

Nicht durchgeführt:

- Unity-Projekt wurde nicht im Editor kompiliert oder gestartet.
- Backend wurde nicht dauerhaft gestartet.
- Kein OpenAI-Livecall, kein STT/TTS-Livecall.
- Keine visuelle Unity-Szene gerendert.

## 9. Kurzfazit

Das Projekt ist ein brauchbarer und relativ weit entwickelter Prototyp für agentenbasierte, räumlich verankerte Dialoge in Unity/WebXR. Es bildet dynamische Agenten in einer Szene bereits gut ab: Agenten haben Identität, Persona, Wissenstags, räumliche Position, Voice-Settings, Gedächtnismodell und Handoff-Verhalten.

Für echte Interaktionsobjekte wie eine Kaffeemaschine fehlt noch eine explizite semantische und zustandsbasierte Ebene. Diese sollte nicht in `AgentSpec` hineingezwängt werden, sondern als ergänzendes Object-Interaction-Modell an das bestehende Metamodell angehängt werden.
