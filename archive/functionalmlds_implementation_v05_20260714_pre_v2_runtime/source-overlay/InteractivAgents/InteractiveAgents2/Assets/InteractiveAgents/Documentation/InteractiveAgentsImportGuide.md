# Interactive Agents Import Guide

This folder turns the reusable agent functionality into a Unity package workflow.

## Export from this project

Use the Unity menu:

- `Tools/Interactive Agents/Export/Core Unity Package`
- `Tools/Interactive Agents/Export/Core + Character Assets Unity Package`

The core package contains:

- `QuickAgentManager` runtime behaviour
- `Tools/Project Manager`
- `Tools/MLDSI Project Wizard`
- MLDS sample JSON files
- WebGL voice bridge
- this import/export utility and documentation

The character package also includes `Assets/Resources/Characters`. That folder is large, so only use it when the target project should keep the included avatar FBX, textures, materials, and animation clips. Without it, `QuickAgentManager` still works and falls back to generated cube avatars.

## Import into another Unity project

1. In the target project, open `Assets > Import Package > Custom Package...`.
2. Select the exported `.unitypackage`.
3. Import all files, or at least keep the `Assets/Scripting`, `Assets/Plugins/WebGL`, and `Assets/InteractiveAgents` entries selected.
4. Run `Tools/Interactive Agents/Validate Installation`.
5. Run `Tools/Interactive Agents/Create Manager In Scene` or add `QuickAgentManager` manually to a GameObject.
6. Set `Backend Base Url` on `QuickAgentManager` if the backend does not run on `http://127.0.0.1:8787`.

## Backend contract

The target project still needs a running backend. The runtime and editor tools expect endpoints equivalent to:

- `/setup`
- `/chat`
- `/tts`
- `/stt`
- `/projects/...`

The package moves the Unity-side functionality. It does not embed the backend service itself.

## Recommended Unity packages

The core scripts compile without hard dependencies on WebXR or XR packages. For feature parity with this project, install the packages listed in `required-packages.json`, especially WebXR and XR Interaction Toolkit for browser/XR builds.

If WebXR packages are installed from OpenUPM, add this scoped registry to the target project's `Packages/manifest.json`:

```json
{
  "name": "package.openupm.com",
  "url": "https://package.openupm.com",
  "scopes": [
    "com.de-panther.webxr",
    "com.de-panther.webxr-interactions"
  ]
}
```

## Re-export from an imported project

After importing, the same `Tools/Interactive Agents/Export/...` menu is available in the target project. That lets you make local adjustments and export the adapted agent package again.
