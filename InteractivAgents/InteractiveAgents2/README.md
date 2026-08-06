# InteractiveAgentsUnity

Unity project for interactive multi-agent scenes with WebXR support, in-editor project tooling, and runtime chat/voice interactions.

## Project Status

- Engine: `Unity 6000.4.5f1`
- Main branch: `main`
- Primary scene in Build Settings: `Assets/Scenes/MolkereiChampignion.unity`

## What This Project Includes

- Runtime multi-agent manager (`QuickAgentManager`) with:
  - agent spawning and selection
  - chat flow with agent handoff
  - optional TTS playback and STT voice input
  - FPV interaction mode and proximity-based interactions
- Unity Editor tools:
  - `Tools/Project Manager`
  - `Tools/MLDSI Project Wizard`
- WebXR + XR Interaction Toolkit integration for browser/XR workflows.

## Requirements

- Unity Editor `6000.4.5f1`
- Internet access for package restore (Unity Package Manager)
- A running backend service reachable at:
  - `http://127.0.0.1:8787`

The backend is expected to expose endpoints used by this project (for example `/setup`, `/chat`, `/tts`, `/stt`, and project-management endpoints under `/projects/...`).

## Quick Start

1. Clone this repository.
2. Open the project folder in Unity Hub with Unity `6000.4.5f1`.
3. Let Unity import packages and assets.
4. Start your backend service on `127.0.0.1:8787` (or change the URL in the relevant components/tools).
5. Open `Assets/Scenes/MolkereiChampignion.unity`.
6. Press Play.

## Runtime Controls (Default)

Inside Play Mode (when `QuickAgentManager` is active):

- `F1`: toggle FPV mode
- `WASD`: move
- `Q/E`: move down/up
- `Shift`: movement boost
- `T`: open chat (near an agent in FPV mode)
- `V` (hold): voice recording

## Editor Tools

### 1) Project Manager

Menu: `Tools/Project Manager`

Use it to:

- list/create/load projects from backend
- edit project metadata
- create/edit agents (including voice and placement)
- manage knowledge entries

### 2) MLDSI Project Wizard

Menu: `Tools/MLDSI Project Wizard`

Use it to:

- import an MLDSI/JSON file
- run backend-assisted analysis
- iterate via chat
- commit generated project data
- preview room/object/agent placement

### 3) Interactive Agents Package Export

Menu: `Tools/Interactive Agents`

Use it to:

- export the reusable runtime/editor agent tooling as a `.unitypackage`
- optionally include the large character resources
- validate an imported installation in another Unity project
- create a `QuickAgentManager` object in the current scene

Import details live in `Assets/InteractiveAgents/Documentation/InteractiveAgentsImportGuide.md`.

## Repository Layout

- `Assets/` - scenes, scripts, resources, prefabs, plugin assets
- `Assets/InteractiveAgents/` - export/import utility and package documentation
- `Packages/` - Unity package manifest and lock file
- `ProjectSettings/` - Unity project configuration

Ignored locally (not versioned): `Library/`, `Temp/`, `Logs/`, `UserSettings/`, generated IDE files.

## Notes

- Large binary assets are configured with Git LFS via `.gitattributes`.
- If the backend URL differs, update it in:
  - runtime component settings (`QuickAgentManager`)
  - editor tools (`ProjectManagerUI`, `ArrowProjectWizard`)
