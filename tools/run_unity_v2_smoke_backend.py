from __future__ import annotations

"""Start a network-free backend for the real Unity V2 HTTP smoke.

The harness exposes the production HTTP handlers and real materialized projects,
but deliberately has no LLM implementation.  The Unity acceptance smoke uses only
GET /projects, POST /setup and GET /projects/<id>/functionalmlds-v2, so any attempt
to expand the smoke into a network-backed chat fails explicitly.
"""

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = (
    ROOT
    / "InteractivAgents"
    / "openai_unity_expert_npcs_pycharm"
    / "InteractiveAgents"
)
for import_root in (ROOT, BACKEND_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from backend.kb import KnowledgeBase  # noqa: E402
from backend.projects import ProjectManager  # noqa: E402
from backend.server import start_http_server  # noqa: E402
from backend.state import SessionStore  # noqa: E402


class _NoNetworkOpenAI:
    def __getattr__(self, name: str):
        raise RuntimeError(
            f"Unity V2 smoke backend does not permit OpenAI operation {name!r}."
        )


def build_store() -> SessionStore:
    project_manager = ProjectManager(
        root=BACKEND_ROOT / "projects",
        template_room_plan=BACKEND_ROOT / "examples" / "room_plan.example.json",
        template_agents=BACKEND_ROOT / "examples" / "agents.example.json",
    )
    return SessionStore(
        max_history_turns=4,
        max_handoffs=1,
        kb=KnowledgeBase(BACKEND_ROOT / "kb"),
        kb_max_snippets=2,
        model="unity-v2-offline-smoke",
        temperature=0.0,
        stt_model="disabled",
        stt_language="de",
        stt_max_audio_bytes=1024,
        openai=_NoNetworkOpenAI(),
        project_manager=project_manager,
        default_room_plan_path="examples/room_plan.example.json",
        default_agents_path="examples/agents.example.json",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline production backend for the Unity V2 smoke.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18787)
    args = parser.parse_args()
    print(f"UNITY_V2_SMOKE_BACKEND_READY http://{args.host}:{args.port}", flush=True)
    start_http_server(host=args.host, port=args.port, store=build_store())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
