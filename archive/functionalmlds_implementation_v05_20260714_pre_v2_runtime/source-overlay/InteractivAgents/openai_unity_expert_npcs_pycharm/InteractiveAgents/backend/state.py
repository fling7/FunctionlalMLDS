from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .kb import KnowledgeBase
from .functionalmlds_adapter import ANALYZE_STAGE_IDS, COMMIT_STAGE_IDS, FunctionalMldsAdapter, derive_case_id
from .openai_client import OpenAIHTTPError, OpenAIResponsesClient, create_transcription, create_tts_audio
from .placement import assign_spawn_points, normalize_placement_preview, summarize_room_objects, mlds_slice_obstacles, _is_mlds
from .projects import ProjectManager
from .schemas import arrow_project_schema, npc_action_schema


def _now_ms() -> int:
    return int(time.time() * 1000)


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9äöüß_-]+", "_", s, flags=re.IGNORECASE)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "agent"


MEMORY_MODE_SHARED = "shared_history"
MEMORY_MODE_AGENT_PRIVATE = "agent_private_history"
VALID_MEMORY_MODES = {MEMORY_MODE_SHARED, MEMORY_MODE_AGENT_PRIVATE}
_MEMORY_MODE_ALIASES = {
    "shared": MEMORY_MODE_SHARED,
    "global": MEMORY_MODE_SHARED,
    "global_history": MEMORY_MODE_SHARED,
    "agent_private": MEMORY_MODE_AGENT_PRIVATE,
    "private": MEMORY_MODE_AGENT_PRIVATE,
    "private_history": MEMORY_MODE_AGENT_PRIVATE,
    "per_agent": MEMORY_MODE_AGENT_PRIVATE,
    "per_agent_history": MEMORY_MODE_AGENT_PRIVATE,
}

GENERATION_MODE_LEGACY = "legacy"
GENERATION_MODE_FUNCTIONALMLDS = "functionalmlds"
VALID_GENERATION_MODES = {GENERATION_MODE_LEGACY, GENERATION_MODE_FUNCTIONALMLDS}
_GENERATION_MODE_ALIASES = {
    "": GENERATION_MODE_LEGACY,
    "arrow": GENERATION_MODE_LEGACY,
    "legacy_interactive_agents": GENERATION_MODE_LEGACY,
    "functional": GENERATION_MODE_FUNCTIONALMLDS,
    "functional_mlds": GENERATION_MODE_FUNCTIONALMLDS,
    "functional-mlds": GENERATION_MODE_FUNCTIONALMLDS,
}


def normalize_memory_mode(value: Any, default: str = MEMORY_MODE_SHARED) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        raw = default
    raw = _MEMORY_MODE_ALIASES.get(raw, raw)
    if raw not in VALID_MEMORY_MODES:
        valid = ", ".join(sorted(VALID_MEMORY_MODES))
        raise ValueError(f"Unbekannter memory_mode: {raw}. Erlaubt: {valid}.")
    return raw


def normalize_generation_mode(value: Any, default: str = GENERATION_MODE_LEGACY) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        raw = default
    raw = _GENERATION_MODE_ALIASES.get(raw, raw)
    if raw not in VALID_GENERATION_MODES:
        valid = ", ".join(sorted(VALID_GENERATION_MODES))
        raise ValueError(f"Unbekannter generation_mode: {raw}. Erlaubt: {valid}.")
    return raw


def _parse_bool(value: Any, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    raw = str(value).strip().lower()
    if raw in {"1", "true", "yes", "y", "on"}:
        return True
    if raw in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Ungueltiger Boolean-Wert: {value}.")


def _as_str_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return [str(x).strip() for x in value if str(x).strip()]


def _semantic_tokens(value: Any) -> set[str]:
    text = str(value or "").lower()
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        "_": " ",
        "-": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return {m.group(0) for m in re.finditer(r"[a-z0-9]+", text)}


@dataclass
class AgentSpec:
    id: str
    display_name: str
    persona: str
    expertise: List[str] = field(default_factory=list)
    knowledge_tags: List[str] = field(default_factory=list)
    responsible_zone_ids: List[str] = field(default_factory=list)
    grounded_object_ids: List[str] = field(default_factory=list)
    handoff_targets: List[str] = field(default_factory=list)
    preferred_zone_ids: List[str] = field(default_factory=list)
    preferred_spawn_tags: List[str] = field(default_factory=list)
    voice: Optional[str] = None
    voice_style: Optional[str] = None
    tts_model: Optional[str] = None
    functionalmlds_agent_ref: Optional[str] = None

    @staticmethod
    def from_dict(d: Dict[str, Any], idx: int) -> "AgentSpec":
        display = str(d.get("display_name") or d.get("name") or f"Agent {idx+1}")
        agent_id = str(d.get("id") or _slugify(display) or f"agent_{idx+1}")
        persona = str(d.get("persona") or "").strip()

        voice = str(d.get("voice") or "").strip() or None
        voice_style = str(d.get("voice_style") or "").strip() or None
        tts_model = str(d.get("tts_model") or "").strip() or None
        functionalmlds_agent_ref = str(d.get("functionalmlds_agent_ref") or "").strip() or None

        return AgentSpec(
            id=agent_id,
            display_name=display,
            persona=persona,
            expertise=_as_str_list(d.get("expertise")),
            knowledge_tags=_as_str_list(d.get("knowledge_tags")),
            responsible_zone_ids=_as_str_list(d.get("responsible_zone_ids")),
            grounded_object_ids=_as_str_list(d.get("grounded_object_ids")),
            handoff_targets=_as_str_list(d.get("handoff_targets")),
            preferred_zone_ids=_as_str_list(d.get("preferred_zone_ids")),
            preferred_spawn_tags=_as_str_list(d.get("preferred_spawn_tags")),
            voice=voice,
            voice_style=voice_style,
            tts_model=tts_model,
            functionalmlds_agent_ref=functionalmlds_agent_ref,
        )

    def short_profile(self) -> str:
        exp = ", ".join(self.expertise) if self.expertise else "—"
        return f"{self.id} ({self.display_name}): Expertise: {exp}"


@dataclass
class SessionState:
    session_id: str
    agents: Dict[str, AgentSpec]
    placements: Dict[str, Dict[str, Any]]
    kb: KnowledgeBase
    memory_mode: str = MEMORY_MODE_SHARED
    history: List[Dict[str, str]] = field(default_factory=list)  # shared mode: role=user|assistant, content=str
    agent_histories: Dict[str, List[Dict[str, str]]] = field(default_factory=dict)
    created_ms: int = field(default_factory=_now_ms)
    updated_ms: int = field(default_factory=_now_ms)
    project_id: Optional[str] = None

    def touch(self) -> None:
        self.updated_ms = _now_ms()


@dataclass
class ArrowProjectDraft:
    session_id: str
    arrow_payload: Dict[str, Any]
    analysis: str
    assistant_message: str
    project: Dict[str, str]
    agents: List[Dict[str, Any]]
    knowledge: List[Dict[str, Any]]
    placement_preview: Dict[str, Any]
    generation_mode: str = GENERATION_MODE_LEGACY
    project_id_hint: str = ""
    run_validation: bool = False
    max_repair_attempts: Optional[int] = None
    case_id: Optional[str] = None
    case_dir: Optional[str] = None
    agent_roles: Dict[str, Any] = field(default_factory=dict)
    functionalmlds_path: Optional[str] = None
    trace_map_path: Optional[str] = None
    validation_summary: Dict[str, Any] = field(default_factory=dict)
    functionalmlds_summary: Dict[str, Any] = field(default_factory=dict)
    scenario_summary: Dict[str, Any] = field(default_factory=dict)
    capability_summary: Dict[str, Any] = field(default_factory=dict)
    handoff_summary: Dict[str, Any] = field(default_factory=dict)
    room_knowledge_summary: Dict[str, Any] = field(default_factory=dict)
    refinement_requests: List[Dict[str, Any]] = field(default_factory=list)
    validation_stale: bool = False
    history: List[Dict[str, str]] = field(default_factory=list)
    created_ms: int = field(default_factory=_now_ms)
    updated_ms: int = field(default_factory=_now_ms)

    def touch(self) -> None:
        self.updated_ms = _now_ms()

    def request_options(self) -> Dict[str, Any]:
        return {
            "project_id_hint": self.project_id_hint,
            "run_validation": self.run_validation,
            "max_repair_attempts": self.max_repair_attempts,
            "refinement_request_count": len(self.refinement_requests),
        }

    def decorate_draft_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(payload)
        out["generation_mode"] = self.generation_mode
        out["request_options"] = self.request_options()
        out["validation_stale"] = self.validation_stale
        out["refinement_status"] = "stale" if self.validation_stale else "validated"
        if self.refinement_requests:
            out["refinement_requests"] = list(self.refinement_requests)
        if self.case_id:
            out["case_id"] = self.case_id
        if self.case_dir:
            out["case_dir"] = self.case_dir
        if self.functionalmlds_path:
            out["functionalmlds_path"] = self.functionalmlds_path
        if self.trace_map_path:
            out["trace_map_path"] = self.trace_map_path
        if self.validation_summary:
            out["validation_summary"] = self.validation_summary
        if self.functionalmlds_summary:
            out["functionalmlds_summary"] = self.functionalmlds_summary
        if self.scenario_summary:
            out["scenario_summary"] = self.scenario_summary
        if self.capability_summary:
            out["capability_summary"] = self.capability_summary
        if self.handoff_summary:
            out["handoff_summary"] = self.handoff_summary
        if self.room_knowledge_summary:
            out["room_knowledge_summary"] = self.room_knowledge_summary
        return out


@dataclass
class SessionStore:
    max_history_turns: int
    max_handoffs: int
    kb: KnowledgeBase
    kb_max_snippets: int
    model: str
    temperature: float
    stt_model: str
    stt_language: str
    stt_max_audio_bytes: int
    openai: OpenAIResponsesClient
    project_manager: ProjectManager
    default_room_plan_path: str = "examples/room_plan.example.json"
    default_agents_path: str = "examples/agents.example.json"
    default_memory_mode: str = MEMORY_MODE_SHARED
    sessions: Dict[str, SessionState] = field(default_factory=dict)
    kb_cache: Dict[str, KnowledgeBase] = field(default_factory=dict)
    arrow_sessions: Dict[str, ArrowProjectDraft] = field(default_factory=dict)

    def _project_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def _load_json_file(self, rel_path: str) -> Dict[str, Any]:
        path = (self._project_root() / rel_path).resolve()
        # Safety: ensure file is inside project
        if self._project_root() not in path.parents and path != self._project_root():
            raise ValueError("Ungültiger Pfad (außerhalb Projekt).")
        return json.loads(path.read_text(encoding="utf-8"))

    def create_session(
        self,
        room_plan: Dict[str, Any],
        agent_dicts: List[Dict[str, Any]],
        session_id: Optional[str] = None,
        kb: Optional[KnowledgeBase] = None,
        project_id: Optional[str] = None,
        memory_mode: Optional[str] = None,
    ) -> SessionState:
        if not session_id:
            session_id = str(uuid.uuid4())
        mode = normalize_memory_mode(memory_mode, default=normalize_memory_mode(self.default_memory_mode))

        agents_list: List[AgentSpec] = [AgentSpec.from_dict(d, i) for i, d in enumerate(agent_dicts)]
        agents_map = {a.id: a for a in agents_list}

        agent_inputs = []
        for idx, agent in enumerate(agents_list):
            source = agent_dicts[idx] if idx < len(agent_dicts) else {}
            agent_inputs.append(
                {
                    "id": agent.id,
                    "preferred_zone_ids": agent.preferred_zone_ids,
                    "preferred_spawn_tags": agent.preferred_spawn_tags,
                    "position": source.get("position") if isinstance(source, dict) else None,
                    "forward": source.get("forward") if isinstance(source, dict) else None,
                    "spawn_point_id": source.get("spawn_point_id") if isinstance(source, dict) else None,
                }
            )

        placements = assign_spawn_points(
            room_plan=room_plan,
            agents=agent_inputs,
        )

        st = SessionState(
            session_id=session_id,
            agents=agents_map,
            placements=placements,
            kb=kb or self.kb,
            memory_mode=mode,
            history=[],
            agent_histories={a.id: [] for a in agents_list},
            project_id=project_id,
        )
        self.sessions[session_id] = st
        return st

    def setup_from_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Supports:
        - direct: {"room_plan": {...}, "agents": [{"..."}]}
        - via paths: {"room_plan_path": "examples/room_plan.example.json", "agents_path": "examples/agents.example.json"}
        - via project: {"project_id": "demo_project"}
        """
        project_id = str(payload.get("project_id") or "").strip() or None
        project_room_plan = None
        project_agents = None
        project_kb = None
        if project_id:
            project_room_plan = self.project_manager.load_room_plan(project_id)
            project_agents = self.project_manager.load_agents(project_id).get("agents", [])
            project_kb = self._get_project_kb(project_id)
        memory_mode = normalize_memory_mode(payload.get("memory_mode"), default=self.default_memory_mode)

        room_plan_path = payload.get("room_plan_path")
        if room_plan_path:
            room_plan = self._load_json_file(str(room_plan_path))
        elif project_room_plan is not None:
            room_plan = project_room_plan
        else:
            room_plan = payload.get("room_plan") or {}
            if not room_plan:
                room_plan = self._load_json_file(self.default_room_plan_path)

        agents_path = payload.get("agents_path")
        if agents_path:
            agents_doc = self._load_json_file(str(agents_path))
            agent_dicts = agents_doc.get("agents") or []
        elif project_agents is not None:
            agent_dicts = project_agents
        else:
            agent_dicts = payload.get("agents") or payload.get("agent_specs") or []
            if not agent_dicts:
                agents_doc = self._load_json_file(self.default_agents_path)
                agent_dicts = agents_doc.get("agents") or []

        session_id = payload.get("session_id")
        st = self.create_session(
            room_plan=room_plan,
            agent_dicts=agent_dicts,
            session_id=session_id,
            kb=project_kb,
            project_id=project_id,
            memory_mode=memory_mode,
        )

        agents_out = []
        for aid, agent in st.agents.items():
            pl = st.placements.get(aid, {})
            agents_out.append(
                {
                    "id": agent.id,
                    "display_name": agent.display_name,
                    "voice": agent.voice,
                    "voice_style": agent.voice_style,
                    "tts_model": agent.tts_model,
                    "position": pl.get("position", {"x": 0, "y": 0, "z": 0}),
                    "forward": pl.get("forward", {"x": 0, "y": 0, "z": 1}),
                    "spawn_point_id": pl.get("spawn_point_id"),
                    "zone_id": pl.get("zone_id"),
                    "tags": pl.get("tags", []),
                }
            )

        return {"session_id": st.session_id, "memory_mode": st.memory_mode, "agents": agents_out}

    def tts(self, payload: Dict[str, Any]) -> Tuple[bytes, str]:
        text = str(payload.get("text") or "").strip()
        if not text:
            raise ValueError("text fehlt.")
        voice = str(payload.get("voice") or "").strip() or "alloy"
        tts_model = str(payload.get("tts_model") or "").strip() or "gpt-4o-mini-tts"
        response_format = str(payload.get("response_format") or "mp3").strip() or "mp3"
        print(
            "[TTS] Anfrage vorbereiten: "
            f"text_len={len(text)}, voice={voice}, model={tts_model}, format={response_format}",
            flush=True,
        )
        audio, content_type = create_tts_audio(
            api_key=self.openai.api_key,
            text=text,
            voice=voice,
            model=tts_model,
            response_format=response_format,
            timeout_seconds=self.openai.timeout_seconds,
        )
        print(
            "[TTS] Antwort erhalten: "
            f"bytes={len(audio)}, content_type={content_type}",
            flush=True,
        )
        return audio, content_type

    def stt(self, payload: Dict[str, Any], files: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        file_info = files.get("audio") or files.get("file")
        if not file_info:
            raise ValueError("audio fehlt.")

        audio = file_info.get("content") or b""
        if not isinstance(audio, (bytes, bytearray)) or not audio:
            raise ValueError("audio ist leer.")
        if len(audio) > self.stt_max_audio_bytes:
            raise ValueError(f"audio ist zu groß ({len(audio)} Bytes, Limit {self.stt_max_audio_bytes}).")

        model = str(payload.get("model") or self.stt_model or "whisper-1").strip()
        language = str(payload.get("language") or self.stt_language or "").strip() or None
        prompt = str(payload.get("prompt") or "").strip() or None
        filename = str(file_info.get("filename") or "speech.wav").strip() or "speech.wav"
        content_type = str(file_info.get("content_type") or "audio/wav").strip() or "audio/wav"

        print(
            "[STT] Anfrage vorbereiten: "
            f"bytes={len(audio)}, filename={filename}, content_type={content_type}, model={model}, language={language or ''}",
            flush=True,
        )
        result = create_transcription(
            api_key=self.openai.api_key,
            audio=bytes(audio),
            filename=filename,
            content_type=content_type,
            model=model,
            language=language,
            prompt=prompt,
            timeout_seconds=self.openai.timeout_seconds,
        )

        text = str(result.get("text") or "").strip()
        print(f"[STT] Transkript erhalten: text_len={len(text)}", flush=True)
        return {
            "text": text,
            "model": model,
            "language": language,
        }

    def _get_project_kb(self, project_id: str) -> KnowledgeBase:
        if project_id in self.kb_cache:
            return self.kb_cache[project_id]
        kb_root = self.project_manager.project_kb_root(project_id)
        kb = KnowledgeBase(kb_root, chunk_chars=self.kb.chunk_chars)
        self.kb_cache[project_id] = kb
        return kb

    def refresh_project_kb(self, project_id: str) -> KnowledgeBase:
        if project_id in self.kb_cache:
            del self.kb_cache[project_id]
        return self._get_project_kb(project_id)

    # -------------------- Chat orchestration --------------------

    def _trim_history(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        # keep last N turns (user+assistant pairs). A turn is a user message.
        max_user_msgs = max(1, int(self.max_history_turns))
        # find last max_user_msgs user messages and keep everything after the earliest of those.
        user_indices = [i for i, m in enumerate(history) if m.get("role") == "user"]
        if len(user_indices) <= max_user_msgs:
            return history
        cutoff_user_idx = user_indices[-max_user_msgs]
        return history[cutoff_user_idx:]

    def _agent_history(self, st: SessionState, agent_id: str) -> List[Dict[str, str]]:
        return st.agent_histories.setdefault(agent_id, [])

    def _commit_agent_history(self, st: SessionState, agent_id: str, history: List[Dict[str, str]]) -> None:
        st.agent_histories[agent_id] = self._trim_history(history)

    def _handoff_brief(self, res: Dict[str, Any], user_text: str) -> str:
        brief = str(res.get("handoff_brief") or "").strip()
        if brief:
            return brief
        reason = str(res.get("handoff_reason") or "").strip()
        if reason:
            return f"Nutzerfrage: {user_text}\nWeiterleitungsgrund: {reason}"
        return f"Nutzerfrage: {user_text}"

    def _handoff_user_context(
        self,
        from_agent: AgentSpec,
        user_text: str,
        handoff_brief: str,
        handoff_reason: Optional[str],
    ) -> str:
        lines = [f"Uebergabekontext von {from_agent.display_name}: {handoff_brief}"]
        if handoff_reason:
            lines.append(f"Weiterleitungsgrund: {handoff_reason}")
        lines.append(f"Aktuelle Nutzerfrage: {user_text}")
        return "\n".join(lines)

    def _build_developer_prompt(self, agent: AgentSpec, others: List[AgentSpec], kb_snippets: List[Dict[str, Any]], allow_handoff: bool) -> str:
        lines: List[str] = []
        lines.append(f"Du bist ein virtueller Gesprächspartner (NPC) in Unity.")
        lines.append(f"Name: {agent.display_name} (id: {agent.id})")
        if agent.persona:
            lines.append(f"Persona:\n{agent.persona}")
        if agent.expertise:
            lines.append("Expertise (Schwerpunkte): " + ", ".join(agent.expertise))
        lines.append("")
        lines.append("Kommunikationsstil:")
        lines.append("- Antworte auf Deutsch.")
        lines.append("- Kurz, natürlich, hilfreich (Messestand/Showroom-Stil).")
        lines.append("- Wenn Informationen fehlen, stelle 1 kurze Rückfrage (statt zu raten), sofern es in deinem Bereich liegt.")
        lines.append("")
        if allow_handoff and others:
            lines.append("Handoff-Regel:")
            lines.append("- Wenn du weiterleitest, setze 'handoff_brief' auf 1-2 kurze Saetze fuer den Zielagenten: Thema, wichtige Nutzerangaben und offene Frage.")
            lines.append("- Wenn du nicht weiterleitest, setze 'handoff_to', 'handoff_reason' und 'handoff_brief' auf null.")
            lines.append("- Wenn die Nutzerfrage deutlich außerhalb deiner Expertise liegt oder du unsicher bist (confidence < 0.55), leite an den am besten passenden anderen Agenten weiter.")
            lines.append("- Setze dann 'handoff_to' auf dessen id, und 'say' ist nur eine kurze Weiterleitungsformulierung (ohne ausführliche Antwort).")
            lines.append("")
            lines.append("Verfügbare andere Agenten:")
            for o in others:
                lines.append(f"- {o.id}: {o.display_name} | Expertise: {', '.join(o.expertise) if o.expertise else '—'}")
        else:
            lines.append("Handoff: deaktiviert. Antworte selbst so gut wie möglich oder bitte um Klärung.")
        lines.append("")
        if kb_snippets:
            lines.append("Lokale Wissensauszüge (nur nutzen, wenn relevant; nicht erfinden):")
            for s in kb_snippets:
                meta = f"[{s.get('tag')}/{s.get('file')}#{s.get('chunk_index')}]"
                lines.append(f"- {meta} {s.get('text')}")
            lines.append("")
        lines.append("WICHTIG: Du MUSST deine Antwort als JSON ausgeben und genau das Schema erfüllen (Structured Output).")
        return "\n".join(lines).strip()

    def _agent_match_score(self, agent: AgentSpec, query_tokens: set[str]) -> float:
        if not query_tokens:
            return 0.0
        parts: List[str] = [
            agent.id,
            agent.display_name,
            agent.persona,
            " ".join(agent.expertise),
            " ".join(agent.knowledge_tags),
            " ".join(agent.responsible_zone_ids),
            " ".join(agent.grounded_object_ids),
        ]
        agent_tokens = _semantic_tokens(" ".join(parts))
        matched = set()
        for query_token in query_tokens:
            for agent_token in agent_tokens:
                if query_token == agent_token:
                    matched.add(agent_token)
                elif len(agent_token) >= 4 and agent_token in query_token:
                    matched.add(agent_token)
                elif len(query_token) >= 4 and query_token in agent_token:
                    matched.add(agent_token)
        direct = len(matched)
        return float(direct) + (direct / max(1, len(query_tokens)))

    def _select_fallback_handoff_target(
        self,
        st: SessionState,
        agent: AgentSpec,
        user_text: str,
        allow_handoff: bool,
    ) -> Optional[AgentSpec]:
        if not allow_handoff or self.max_handoffs <= 0:
            return None

        query_tokens = _semantic_tokens(user_text)
        current_score = self._agent_match_score(agent, query_tokens)
        allowed_ids = set(agent.handoff_targets or [])

        candidates: List[Tuple[float, AgentSpec]] = []
        for other in st.agents.values():
            if other.id == agent.id:
                continue
            if allowed_ids and other.id not in allowed_ids:
                continue
            score = self._agent_match_score(other, query_tokens)
            if score > 0:
                candidates.append((score, other))

        if not candidates:
            return None
        candidates.sort(key=lambda item: item[0], reverse=True)
        best_score, best_agent = candidates[0]
        if best_score <= current_score:
            return None
        return best_agent

    def _fallback_snippets(self, st: SessionState, agent: AgentSpec, user_text: str) -> List[Dict[str, Any]]:
        snippets = st.kb.search(query=user_text, tags=agent.knowledge_tags, k=self.kb_max_snippets)
        if snippets:
            return snippets
        snippets = st.kb.search(query=user_text, tags=[], k=self.kb_max_snippets)
        if snippets:
            return snippets
        return st.kb.snippets(tags=agent.knowledge_tags, k=self.kb_max_snippets)

    def _fallback_room_answer(self, st: SessionState, agent: AgentSpec, user_text: str) -> str:
        snippets = self._fallback_snippets(st, agent, user_text)
        if not snippets:
            return (
                "Offline-Fallback aus FunctionalMLDS: Fuer diesen Agenten liegt kein "
                "passender Wissensausschnitt im Projekt-KB vor."
            )

        facts: List[str] = []
        seen = set()
        for snippet in snippets:
            text = re.sub(r"\s+", " ", str(snippet.get("text") or "")).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            facts.append(text)
            if len(facts) >= 3:
                break

        if not facts:
            return (
                "Offline-Fallback aus FunctionalMLDS: Die KB-Treffer waren leer, "
                "daher kann ich die Raumfrage nicht belastbar beantworten."
            )
        return "Offline-Fallback aus FunctionalMLDS-Raumwissen: " + " ".join(facts)

    def _fallback_agent_response(
        self,
        st: SessionState,
        agent: AgentSpec,
        user_text: str,
        allow_handoff: bool,
        error: OpenAIHTTPError,
        forwarded_from: Optional[AgentSpec] = None,
    ) -> Dict[str, Any]:
        target = self._select_fallback_handoff_target(st, agent, user_text, allow_handoff)
        if target is not None:
            reason = (
                f"FunctionalMLDS-Fallback: {target.display_name} ist anhand von "
                "Expertise, Knowledge-Tags und verantwortlichen Raumobjekten passender."
            )
            return {
                "say": f"Ich leite die Frage an {target.display_name} weiter.",
                "handoff_to": target.id,
                "handoff_reason": reason,
                "handoff_brief": f"Nutzerfrage: {user_text}",
                "confidence": 0.7,
                "_runtime_fallback": True,
                "_openai_error": str(error),
            }

        answer = self._fallback_room_answer(st, agent, user_text)
        if forwarded_from is not None:
            answer = f"Uebernommen von {forwarded_from.display_name}. {answer}"
        return {
            "say": answer,
            "handoff_to": None,
            "handoff_reason": None,
            "handoff_brief": None,
            "confidence": 0.55,
            "_runtime_fallback": True,
            "_openai_error": str(error),
        }

    def _call_agent(
        self,
        st: SessionState,
        agent: AgentSpec,
        history_with_user: List[Dict[str, str]],
        allow_handoff: bool,
        forwarded_from: Optional[AgentSpec] = None,
        forwarded_reason: Optional[str] = None,
        forwarded_brief: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Determine allowed handoff ids (excluding self)
        allowed = [a.id for a in st.agents.values() if a.id != agent.id] if allow_handoff else []
        schema = npc_action_schema(allowed_handoff_ids=allowed)

        others = []
        for aid, a in st.agents.items():
            if aid != agent.id:
                others.append(a)

        # KB retrieval
        kb_snips = st.kb.search(query=history_with_user[-1]["content"], tags=agent.knowledge_tags, k=self.kb_max_snippets)

        dev_prompt = self._build_developer_prompt(agent, others, kb_snips, allow_handoff=allow_handoff)

        input_msgs: List[Dict[str, Any]] = [{"role": "developer", "content": dev_prompt}]

        if forwarded_from is not None:
            context = f"Du wurdest gerade von {forwarded_from.display_name} (id: {forwarded_from.id}) an den Nutzer weitergeleitet."
            if forwarded_reason:
                context += f" Grund: {forwarded_reason}"
            if forwarded_brief:
                context += f" Uebergabekontext: {forwarded_brief}"
            context += " Antworte direkt auf die Nutzerfrage."
            input_msgs.append(
                {
                    "role": "developer",
                    "content": context,
                }
            )

        # Add trimmed history
        trimmed = self._trim_history(history_with_user)
        for m in trimmed:
            input_msgs.append({"role": m["role"], "content": m["content"]})

        try:
            parsed, resp, out_text = self.openai.create_structured_json(
                model=self.model,
                input_messages=input_msgs,
                schema=schema,
                schema_name="npc_action",
                temperature=self.temperature,
            )
        except OpenAIHTTPError as e:
            # Fallback: older JSON mode (valid JSON, but not schema-validated)
            # This helps if the chosen model does not support json_schema.
            if e.status != 400:
                raise
            parsed, resp, out_text = self.openai.create_json_object(
                model=self.model,
                input_messages=input_msgs,
                temperature=self.temperature,
            )

        # Normalise
        result = {
            "say": str(parsed.get("say", "")).strip(),
            "handoff_to": parsed.get("handoff_to", None),
            "handoff_reason": parsed.get("handoff_reason", None),
            "handoff_brief": parsed.get("handoff_brief", None),
            "confidence": parsed.get("confidence", 0.5),
            "_raw_text": out_text,
            "_response_id": resp.get("id"),
        }

        if not result["say"]:
            # fallback: use raw text
            result["say"] = out_text.strip() or "…"

        if result["handoff_reason"] is not None:
            result["handoff_reason"] = str(result["handoff_reason"]).strip() or None
        if result["handoff_brief"] is not None:
            result["handoff_brief"] = str(result["handoff_brief"]).strip() or None

        return result

    def chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        session_id = str(payload.get("session_id") or "").strip()
        if not session_id:
            raise ValueError("session_id fehlt. Bitte zuerst /setup aufrufen.")
        st = self.sessions.get(session_id)
        if not st:
            raise ValueError("Unbekannte session_id. Bitte /setup erneut aufrufen.")

        active_agent_id = str(payload.get("active_agent_id") or "").strip()
        if not active_agent_id or active_agent_id not in st.agents:
            # fallback to first agent
            active_agent_id = next(iter(st.agents.keys()))

        user_text = str(payload.get("user_text") or "").strip()
        if not user_text:
            raise ValueError("user_text ist leer.")

        agent_a = st.agents[active_agent_id]
        if st.memory_mode == MEMORY_MODE_AGENT_PRIVATE:
            return self._chat_agent_private(st, session_id, agent_a, user_text)
        return self._chat_shared(st, session_id, agent_a, user_text)

    def _openai_error_chat_response(self, session_id: str, active_agent_id: str, error: OpenAIHTTPError) -> Dict[str, Any]:
        return {
            "session_id": session_id,
            "active_agent_id": active_agent_id,
            "memory_mode": MEMORY_MODE_SHARED,
            "events": [
                {"type": "say", "agent_id": active_agent_id, "text": f"[Backend] OpenAI Fehler: {error}"},
            ],
            "error": {"status": error.status, "details": error.details},
        }

    def _chat_shared(self, st: SessionState, session_id: str, agent_a: AgentSpec, user_text: str) -> Dict[str, Any]:
        history_with_user = st.history + [{"role": "user", "content": user_text}]

        try:
            res_a = self._call_agent(st, agent_a, history_with_user, allow_handoff=True)
        except OpenAIHTTPError as e:
            res_a = self._fallback_agent_response(
                st,
                agent_a,
                user_text,
                allow_handoff=True,
                error=e,
            )

        events = [{"type": "say", "agent_id": agent_a.id, "text": res_a["say"]}]
        new_active = agent_a.id
        handoff = None

        handoff_to = res_a.get("handoff_to", None)
        if handoff_to in st.agents and handoff_to != agent_a.id:
            if self.max_handoffs > 0:
                agent_b = st.agents[handoff_to]
                try:
                    res_b = self._call_agent(
                        st,
                        agent_b,
                        history_with_user,
                        allow_handoff=False,
                        forwarded_from=agent_a,
                        forwarded_reason=str(res_a.get("handoff_reason") or ""),
                    )
                except OpenAIHTTPError as e:
                    res_b = self._fallback_agent_response(
                        st,
                        agent_b,
                        user_text,
                        allow_handoff=False,
                        error=e,
                        forwarded_from=agent_a,
                    )
                events.append({"type": "say", "agent_id": agent_b.id, "text": res_b["say"]})
                new_active = agent_b.id
                handoff = {
                    "from": agent_a.id,
                    "to": agent_b.id,
                    "reason": res_a.get("handoff_reason"),
                    "brief": res_a.get("handoff_brief"),
                }
                st.history = history_with_user + [
                    {"role": "assistant", "content": res_a["say"]},
                    {"role": "assistant", "content": res_b["say"]},
                ]
            else:
                st.history = history_with_user + [{"role": "assistant", "content": res_a["say"]}]
        else:
            st.history = history_with_user + [{"role": "assistant", "content": res_a["say"]}]

        st.history = self._trim_history(st.history)
        st.touch()

        return {
            "session_id": session_id,
            "active_agent_id": new_active,
            "memory_mode": st.memory_mode,
            "handoff": handoff,
            "events": events,
        }

    def _chat_agent_private(self, st: SessionState, session_id: str, agent_a: AgentSpec, user_text: str) -> Dict[str, Any]:
        history_a_with_user = list(self._agent_history(st, agent_a.id)) + [{"role": "user", "content": user_text}]

        try:
            res_a = self._call_agent(st, agent_a, history_a_with_user, allow_handoff=True)
        except OpenAIHTTPError as e:
            res_a = self._fallback_agent_response(
                st,
                agent_a,
                user_text,
                allow_handoff=True,
                error=e,
            )

        events = [{"type": "say", "agent_id": agent_a.id, "text": res_a["say"]}]
        new_active = agent_a.id
        handoff = None

        handoff_to = res_a.get("handoff_to", None)
        if handoff_to in st.agents and handoff_to != agent_a.id and self.max_handoffs > 0:
            agent_b = st.agents[handoff_to]
            handoff_brief = self._handoff_brief(res_a, user_text)
            handoff_reason = res_a.get("handoff_reason")
            target_user_context = self._handoff_user_context(agent_a, user_text, handoff_brief, handoff_reason)
            history_b_with_user = list(self._agent_history(st, agent_b.id)) + [
                {"role": "user", "content": target_user_context}
            ]
            try:
                res_b = self._call_agent(
                    st,
                    agent_b,
                    history_b_with_user,
                    allow_handoff=False,
                    forwarded_from=agent_a,
                    forwarded_reason=str(handoff_reason or ""),
                    forwarded_brief=handoff_brief,
                )
            except OpenAIHTTPError as e:
                res_b = self._fallback_agent_response(
                    st,
                    agent_b,
                    user_text,
                    allow_handoff=False,
                    error=e,
                    forwarded_from=agent_a,
                )

            events.append({"type": "say", "agent_id": agent_b.id, "text": res_b["say"]})
            new_active = agent_b.id
            handoff = {
                "from": agent_a.id,
                "to": agent_b.id,
                "reason": handoff_reason,
                "brief": handoff_brief,
            }
            self._commit_agent_history(
                st,
                agent_a.id,
                history_a_with_user + [{"role": "assistant", "content": res_a["say"]}],
            )
            self._commit_agent_history(
                st,
                agent_b.id,
                history_b_with_user + [{"role": "assistant", "content": res_b["say"]}],
            )
        else:
            self._commit_agent_history(
                st,
                agent_a.id,
                history_a_with_user + [{"role": "assistant", "content": res_a["say"]}],
            )

        st.touch()

        return {
            "session_id": session_id,
            "active_agent_id": new_active,
            "memory_mode": st.memory_mode,
            "handoff": handoff,
            "events": events,
        }

    def analyze_arrow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        generation_mode = normalize_generation_mode(payload.get("generation_mode"))
        project_id_hint = str(payload.get("project_id_hint") or "").strip()
        run_validation = _parse_bool(payload.get("run_validation"), default=False)
        max_repair_attempts_raw = payload.get("max_repair_attempts")
        max_repair_attempts: Optional[int] = None
        if max_repair_attempts_raw not in (None, ""):
            try:
                max_repair_attempts = int(max_repair_attempts_raw)
            except (TypeError, ValueError) as exc:
                raise ValueError("max_repair_attempts muss eine ganze Zahl sein.") from exc
            if max_repair_attempts < 0:
                raise ValueError("max_repair_attempts darf nicht negativ sein.")

        arrow_payload = payload.get("arrow_json")
        if isinstance(arrow_payload, str):
            try:
                arrow_payload = json.loads(arrow_payload)
            except json.JSONDecodeError as exc:
                raise ValueError(f"arrow_json ungültig: {exc}") from exc
        if not isinstance(arrow_payload, dict):
            raise ValueError("arrow_json muss ein Objekt sein.")
        case_id = derive_case_id(arrow_payload, project_id_hint=project_id_hint)

        draft_meta: Dict[str, Any] = {}
        if generation_mode == GENERATION_MODE_FUNCTIONALMLDS:
            draft_payload, draft_meta = self._generate_functionalmlds_analyze_draft(
                arrow_payload,
                case_id=case_id,
                max_repair_attempts=max_repair_attempts,
            )
        else:
            draft_payload = self._generate_arrow_draft(arrow_payload, history=[])
        session_id = str(uuid.uuid4())
        draft = ArrowProjectDraft(
            session_id=session_id,
            arrow_payload=arrow_payload,
            analysis=draft_payload["analysis"],
            assistant_message=draft_payload["assistant_message"],
            project=draft_payload["project"],
            agents=draft_payload["agents"],
            knowledge=draft_payload["knowledge"],
            placement_preview=draft_payload["placement_preview"],
            generation_mode=generation_mode,
            project_id_hint=project_id_hint,
            run_validation=run_validation,
            max_repair_attempts=max_repair_attempts,
            case_id=case_id,
            case_dir=draft_meta.get("case_dir"),
            agent_roles=draft_meta.get("agent_roles") or {},
            functionalmlds_path=draft_meta.get("functionalmlds_path"),
            trace_map_path=draft_meta.get("trace_map_path"),
            validation_summary=draft_meta.get("validation_summary") or {},
            functionalmlds_summary=draft_meta.get("functionalmlds_summary") or {},
            scenario_summary=draft_meta.get("scenario_summary") or {},
            capability_summary=draft_meta.get("capability_summary") or {},
            handoff_summary=draft_meta.get("handoff_summary") or {},
            room_knowledge_summary=draft_meta.get("room_knowledge_summary") or {},
            history=[{"role": "assistant", "content": draft_payload["assistant_message"]}] if draft_payload["assistant_message"] else [],
        )
        self.arrow_sessions[session_id] = draft
        return {"session_id": session_id, "draft": draft.decorate_draft_payload(draft_payload)}

    def arrow_chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        session_id = str(payload.get("session_id") or "").strip()
        if not session_id:
            raise ValueError("session_id fehlt.")
        session = self.arrow_sessions.get(session_id)
        if not session:
            raise ValueError("Unbekannte session_id.")

        user_text = str(payload.get("user_text") or "").strip()
        if not user_text:
            raise ValueError("user_text ist leer.")
        if session.generation_mode == GENERATION_MODE_FUNCTIONALMLDS:
            request = {
                "id": f"REF-{len(session.refinement_requests) + 1:03d}",
                "role": "user",
                "content": user_text,
                "created_ms": _now_ms(),
                "status": "pending_full_regeneration",
            }
            session.refinement_requests.append(request)
            session.validation_stale = True
            session.assistant_message = (
                "Ich habe den Änderungswunsch für den FunctionalMLDS-Modus vorgemerkt. "
                "Der aktuelle FunctionalMLDS-Stand bleibt unverändert und gilt jetzt als nicht final validiert; "
                "beim Commit muss die Pipeline vollständig neu laufen, damit die Änderung im Metamodell sichtbar "
                "und erneut validiert wird."
            )
            session.history = self._trim_history(
                session.history
                + [{"role": "user", "content": user_text}]
                + [{"role": "assistant", "content": session.assistant_message}]
            )
            session.touch()
            draft_payload = {
                "analysis": session.analysis,
                "assistant_message": session.assistant_message,
                "project": session.project,
                "agents": session.agents,
                "knowledge": session.knowledge,
                "placement_preview": session.placement_preview,
            }
            return {"draft": session.decorate_draft_payload(draft_payload)}

        history = session.history + [{"role": "user", "content": user_text}]
        draft_payload = self._generate_arrow_draft(session.arrow_payload, history=history, current=session)

        session.analysis = draft_payload["analysis"]
        session.assistant_message = draft_payload["assistant_message"]
        session.project = draft_payload["project"]
        session.agents = draft_payload["agents"]
        session.knowledge = draft_payload["knowledge"]
        session.placement_preview = draft_payload["placement_preview"]
        session.history = history + (
            [{"role": "assistant", "content": draft_payload["assistant_message"]}]
            if draft_payload["assistant_message"]
            else []
        )
        session.history = self._trim_history(session.history)
        session.touch()

        return {"draft": session.decorate_draft_payload(draft_payload)}

    def commit_arrow_project(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        session_id = str(payload.get("session_id") or "").strip()
        if not session_id:
            raise ValueError("session_id fehlt.")
        session = self.arrow_sessions.get(session_id)
        if not session:
            raise ValueError("Unbekannte session_id.")

        requested_generation_mode_raw = payload.get("generation_mode")
        if requested_generation_mode_raw not in (None, ""):
            requested_generation_mode = normalize_generation_mode(requested_generation_mode_raw)
            if requested_generation_mode != session.generation_mode:
                raise ValueError(
                    f"generation_mode passt nicht zur Session: "
                    f"{requested_generation_mode} != {session.generation_mode}."
                )
        display_name = str(payload.get("display_name") or session.project.get("display_name") or "").strip()
        if not display_name:
            raise ValueError("display_name fehlt.")
        project_id = str(payload.get("project_id") or "").strip() or None
        description = str(payload.get("description") or session.project.get("description") or "").strip()

        if session.generation_mode == GENERATION_MODE_FUNCTIONALMLDS:
            return self._commit_functionalmlds_project(
                session,
                display_name=display_name,
                project_id=project_id,
                description=description,
            )

        meta = self.project_manager.create_project(display_name=display_name, project_id=project_id, description=description)
        project_id = meta["id"]

        placement_preview = normalize_placement_preview(session.arrow_payload, session.agents, session.placement_preview)
        placement_lookup = {}
        for placement in placement_preview.get("agent_placements") or []:
            if isinstance(placement, dict) and placement.get("id"):
                placement_lookup[placement["id"]] = placement

        agents_with_positions = []
        for agent in session.agents:
            agent_copy = dict(agent)
            placement = placement_lookup.get(agent_copy.get("id"), {})
            position = placement.get("position")
            if position:
                agent_copy["position"] = position
            agent_copy["forward"] = placement.get("forward") or {"x": 0, "y": 0, "z": 1}
            agent_copy["spawn_point_id"] = placement.get("spawn_point_id")
            agent_copy["zone_id"] = placement.get("zone_id")
            agent_copy["tags"] = placement.get("tags", [])
            agents_with_positions.append(agent_copy)

        self.project_manager.save_agents(project_id, agents_with_positions)
        self.project_manager.save_room_plan(project_id, session.arrow_payload)
        for entry in session.knowledge:
            tag = str(entry.get("tag") or "").strip()
            name = str(entry.get("name") or "").strip()
            if not tag or not name:
                continue
            text = str(entry.get("text") or "")
            self.project_manager.upsert_knowledge(project_id, tag=tag, name=name, text=text, overwrite=True)

        self.refresh_project_kb(project_id)
        placement_list = []
        for agent in agents_with_positions:
            placement = placement_lookup.get(agent.get("id"), {})
            placement_list.append(
                {
                    "id": agent.get("id"),
                    "display_name": agent.get("display_name"),
                    "position": placement.get("position"),
                    "forward": placement.get("forward"),
                    "spawn_point_id": placement.get("spawn_point_id"),
                    "zone_id": placement.get("zone_id"),
                    "tags": placement.get("tags", []),
                }
            )
        fallback_room_objects = (
            mlds_slice_obstacles(session.arrow_payload)
            if _is_mlds(session.arrow_payload)
            else summarize_room_objects(session.arrow_payload, floor_only=True)
        )
        return {
            "status": "ok",
            "generation_mode": session.generation_mode,
            "project": meta,
            "placements": placement_list,
            "room_objects": placement_preview.get("room_objects") or fallback_room_objects,
            "room_bounds": placement_preview.get("room_bounds"),
        }

    def _commit_functionalmlds_project(
        self,
        session: ArrowProjectDraft,
        *,
        display_name: str,
        project_id: Optional[str],
        description: str,
    ) -> Dict[str, Any]:
        if project_id and session.case_id and project_id != session.case_id:
            return self._functionalmlds_commit_response(
                session,
                status="needs_repair",
                validation_summary=self._commit_error_summary(
                    "FunctionalMLDS-Projekt-ID muss vor Analyze feststehen. "
                    f"Commit-ID '{project_id}' passt nicht zur Case-ID '{session.case_id}'."
                ),
            )
        if session.validation_stale:
            return self._functionalmlds_commit_response(
                session,
                status="needs_regeneration",
                validation_summary=self._commit_error_summary(
                    "Der FunctionalMLDS-Draft enthaelt vorgemerkte Chat-Aenderungen und ist nicht final validiert. "
                    "Bitte Analyze/Regeneration erneut ausfuehren, bevor ein Runtime-Projekt final committet wird."
                ),
            )
        if not session.case_dir:
            return self._functionalmlds_commit_response(
                session,
                status="needs_repair",
                validation_summary=self._commit_error_summary("FunctionalMLDS-Case-Verzeichnis fehlt in der Session."),
            )

        adapter = FunctionalMldsAdapter.discover(backend_root=self._project_root())
        case_dir = Path(session.case_dir)
        analyze_report = adapter.validate_analyze_case(case_dir)
        if analyze_report.get("status") != "valid":
            validation_summary = adapter.summarize_analyze_validation(analyze_report)
            session.validation_summary = validation_summary
            session.touch()
            return self._functionalmlds_commit_response(
                session,
                status="needs_repair",
                validation_summary=validation_summary,
            )

        stage_errors: List[str] = []
        deterministic_commit_stages = [
            "functionalmlds_invariants",
            *[stage_id for stage_id in COMMIT_STAGE_IDS if stage_id not in ANALYZE_STAGE_IDS],
        ]
        for stage_id in deterministic_commit_stages:
            try:
                result = adapter.run_stage_deterministic_first(case_dir, stage_id)
            except Exception as exc:
                stage_errors.append(f"{stage_id}: {exc}")
                break
            if str(result.get("status") or "").lower() not in {"success", "valid"}:
                for error in result.get("errors") or []:
                    stage_errors.append(f"{stage_id}: {error}")
                if not stage_errors:
                    stage_errors.append(f"{stage_id}: status={result.get('status')}")
                break

        commit_report = adapter.validate_commit_case(case_dir)
        if stage_errors:
            commit_report = dict(commit_report)
            commit_report["status"] = "invalid"
            commit_report["errors"] = stage_errors + list(commit_report.get("errors") or [])
        validation_summary = adapter.summarize_commit_validation(commit_report)
        session.validation_summary = validation_summary
        session.trace_map_path = str(adapter.paths.backend_root / "projects" / case_dir.name / "trace_map.json")
        session.touch()

        if validation_summary.get("status") != "valid":
            return self._functionalmlds_commit_response(
                session,
                status="needs_repair",
                validation_summary=validation_summary,
            )

        meta = self.project_manager.update_metadata(case_dir.name, display_name=display_name, description=description)
        self.refresh_project_kb(case_dir.name)
        return self._functionalmlds_commit_response(
            session,
            status="ok",
            project=meta,
            validation_summary=validation_summary,
        )

    @staticmethod
    def _commit_error_summary(message: str) -> Dict[str, Any]:
        return {
            "status": "invalid",
            "schema_status": "not_run",
            "invariant_status": "not_run",
            "materialization_status": "not_run",
            "traceability_status": "not_run",
            "handoff_status": "not_run",
            "error_count": 1,
            "warning_count": 0,
            "traceability_average_coverage": 0.0,
            "handoff_decision_accuracy": 0.0,
            "errors": [message],
            "warnings": [],
        }

    def _functionalmlds_commit_response(
        self,
        session: ArrowProjectDraft,
        *,
        status: str,
        validation_summary: Dict[str, Any],
        project: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        case_id = session.case_id or ""
        project_dir = self._project_root() / "projects" / case_id if case_id else None
        agents_doc = self._read_json_if_exists(project_dir / "agents.json") if project_dir else {}
        placements = []
        for agent in agents_doc.get("agents") or []:
            if not isinstance(agent, dict):
                continue
            placements.append(
                {
                    "id": agent.get("id"),
                    "display_name": agent.get("display_name"),
                    "position": agent.get("position"),
                    "forward": agent.get("forward"),
                    "spawn_point_id": agent.get("spawn_point_id"),
                    "zone_id": agent.get("zone_id"),
                    "tags": agent.get("tags", []),
                }
            )
        placement_preview = session.placement_preview or {}
        room_objects = placement_preview.get("room_objects") or (
            mlds_slice_obstacles(session.arrow_payload)
            if _is_mlds(session.arrow_payload)
            else summarize_room_objects(session.arrow_payload, floor_only=True)
        )
        return {
            "status": status,
            "generation_mode": session.generation_mode,
            "project": project,
            "placements": placements or placement_preview.get("agent_placements") or [],
            "room_objects": room_objects,
            "room_bounds": placement_preview.get("room_bounds"),
            "functionalmlds_path": session.functionalmlds_path,
            "trace_map_path": str(project_dir / "trace_map.json") if project_dir else session.trace_map_path,
            "validation_summary": validation_summary,
            "functionalmlds_summary": session.functionalmlds_summary,
        }

    def _generate_functionalmlds_analyze_draft(
        self,
        arrow_payload: Dict[str, Any],
        *,
        case_id: str,
        max_repair_attempts: Optional[int],
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        adapter = FunctionalMldsAdapter.discover(backend_root=self._project_root())
        initialized = adapter.initialize_case_from_payload(arrow_payload, case_id=case_id)
        case_dir = Path(initialized["case_dir"])
        stage_errors: List[str] = []
        stage_results: List[Dict[str, Any]] = []

        for stage_id in ANALYZE_STAGE_IDS:
            kwargs: Dict[str, Any] = {}
            if stage_id in {"scene_semantics", "agent_roles", "knowledge_synthesis"}:
                kwargs["max_repair_attempts"] = 3 if max_repair_attempts is None else max_repair_attempts
            try:
                result = adapter.run_stage_deterministic_first(case_dir, stage_id, **kwargs)
            except Exception as exc:
                stage_errors.append(f"{stage_id}: {exc}")
                break

            stage_results.append({"stage_id": stage_id, **result})
            if str(result.get("status") or "").lower() not in {"success", "valid"}:
                for error in result.get("errors") or []:
                    stage_errors.append(f"{stage_id}: {error}")
                if not stage_errors:
                    stage_errors.append(f"{stage_id}: status={result.get('status')}")
                break

        analyze_report = adapter.validate_analyze_case(case_dir)
        if stage_errors:
            analyze_report = dict(analyze_report)
            analyze_report["status"] = "invalid"
            analyze_report["errors"] = stage_errors + list(analyze_report.get("errors") or [])
        validation_summary = adapter.summarize_analyze_validation(analyze_report)

        agent_roles = self._read_json_if_exists(case_dir / "intermediate" / "agent_roles.generated.json")
        knowledge_doc = self._read_json_if_exists(case_dir / "intermediate" / "knowledge.generated.json")
        placements_doc = self._read_json_if_exists(case_dir / "intermediate" / "agent_placements.json")
        functionalmlds_instance = self._read_json_if_exists(case_dir / "functionalmlds" / "functionalmlds.instance.generated.json")
        normalized_scene = self._read_json_if_exists(case_dir / "intermediate" / "scene_graph.normalized.json")
        scene_semantics = self._read_json_if_exists(case_dir / "intermediate" / "scene_semantics.json")
        group_summary = self._read_json_if_exists(case_dir / "intermediate" / "object_group_summary.json")
        if not functionalmlds_instance:
            validation_summary = self._mark_functionalmlds_analyze_invalid(
                validation_summary,
                "FunctionalMLDS-Instanz wurde nicht erzeugt. Die Analyse darf nicht als Legacy-Draft interpretiert werden.",
            )

        agents = [dict(agent) for agent in agent_roles.get("agents") or [] if isinstance(agent, dict)]
        knowledge = [
            {
                "tag": str(entry.get("tag") or ""),
                "name": str(entry.get("name") or ""),
                "text": str(entry.get("text") or ""),
            }
            for entry in knowledge_doc.get("knowledge_entries") or []
            if isinstance(entry, dict)
        ]
        room_objects = (
            mlds_slice_obstacles(arrow_payload)
            if _is_mlds(arrow_payload)
            else summarize_room_objects(arrow_payload, floor_only=True)
        )
        placement_preview = {
            "room_objects": room_objects,
            "agent_placements": placements_doc.get("agent_placements") or [],
            "room_bounds": placements_doc.get("room_bounds") or normalized_scene.get("room_bounds"),
        }

        functionalmlds_path = case_dir / "functionalmlds" / "functionalmlds.instance.generated.json"
        draft_payload = {
            "assistant_message": self._functionalmlds_analyze_message(validation_summary),
            "analysis": self._functionalmlds_analysis_text(case_id, validation_summary, stage_results),
            "project": {
                "display_name": case_id.replace("_", " ").title(),
                "description": "Generated FunctionalMLDS preview project for Interactive Agents.",
            },
            "agents": agents,
            "knowledge": knowledge,
            "placement_preview": placement_preview,
        }
        draft_meta = {
            "case_dir": str(case_dir),
            "agent_roles": agent_roles,
            "functionalmlds_path": str(functionalmlds_path) if functionalmlds_path.exists() else None,
            "trace_map_path": None,
            "validation_summary": validation_summary,
            "functionalmlds_summary": self._build_functionalmlds_summary(functionalmlds_instance)
            or self._minimal_functionalmlds_summary(case_id, validation_summary),
            "scenario_summary": self._build_scenario_summary(functionalmlds_instance),
            "capability_summary": self._build_capability_summary(functionalmlds_instance),
            "handoff_summary": self._build_handoff_summary(agent_roles, analyze_report),
            "room_knowledge_summary": self._build_room_knowledge_summary(
                normalized_scene,
                scene_semantics,
                group_summary,
                knowledge,
                functionalmlds_instance,
            ),
        }
        return draft_payload, draft_meta

    @staticmethod
    def _minimal_functionalmlds_summary(case_id: str, validation_summary: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "case_id": case_id,
            "schema": "functionalmlds_case_study",
            "metamodel_version": "",
            "use_case_id": "",
            "main_scenario_id": "",
            "actor_count": 0,
            "entity_count": 0,
            "agent_count": 0,
            "capability_count": 0,
            "runtime_binding_count": 0,
            "validation_case_count": 0,
            "satisfy_relationship_count": 0,
            "status": validation_summary.get("status") or "invalid",
        }

    @staticmethod
    def _mark_functionalmlds_analyze_invalid(
        validation_summary: Dict[str, Any],
        message: str,
    ) -> Dict[str, Any]:
        summary = dict(validation_summary or {})
        errors = list(summary.get("errors") or [])
        if message not in errors:
            errors.insert(0, message)
        summary.update(
            {
                "status": "invalid",
                "invariant_status": summary.get("invariant_status") or "invalid",
                "error_count": max(int(summary.get("error_count") or 0), len(errors)),
                "errors": errors,
            }
        )
        return summary

    @staticmethod
    def _read_json_if_exists(path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return {}

    @staticmethod
    def _functionalmlds_analyze_message(validation_summary: Dict[str, Any]) -> str:
        if validation_summary.get("status") == "valid":
            return (
                "FunctionalMLDS-Analyze abgeschlossen. Der Draft ist validiert und als Preview sichtbar; "
                "es wurden noch keine Runtime-Projektdateien committet."
            )
        return (
            "FunctionalMLDS-Analyze abgeschlossen, aber die Validierung ist nicht gueltig. "
            "Bitte die angezeigten Fehler beheben; es werden keine Projektdateien committet."
        )

    @staticmethod
    def _functionalmlds_analysis_text(
        case_id: str,
        validation_summary: Dict[str, Any],
        stage_results: List[Dict[str, Any]],
    ) -> str:
        lines = [
            f"FunctionalMLDS-Case: {case_id}",
            f"Analyze-Status: {validation_summary.get('status')}",
            f"Schema/Semantik/Rollen/Wissen/Placement: {validation_summary.get('schema_status')}",
            f"FunctionalMLDS-Invarianten: {validation_summary.get('invariant_status')}",
            f"Handoff-Ableitung: {validation_summary.get('handoff_status')}",
            f"Fehler: {validation_summary.get('error_count', 0)}",
            f"Warnungen: {validation_summary.get('warning_count', 0)}",
        ]
        if stage_results:
            lines.append("Ausgefuehrte Stages: " + ", ".join(str(item.get("stage_id")) for item in stage_results))
        return "\n".join(lines)

    @staticmethod
    def _build_functionalmlds_summary(instance: Dict[str, Any]) -> Dict[str, Any]:
        if not instance:
            return {}
        use_case, scenario = SessionStore._main_use_case_and_scenario(instance)
        return {
            "case_id": instance.get("caseId"),
            "schema": instance.get("schema"),
            "metamodel_version": instance.get("metamodelVersion"),
            "use_case_id": use_case.get("id"),
            "main_scenario_id": scenario.get("id"),
            "actor_count": len(instance.get("actors") or []),
            "entity_count": len(instance.get("entities") or []),
            "agent_count": len(instance.get("agents") or []),
            "capability_count": len(instance.get("capabilities") or []),
            "runtime_binding_count": len(instance.get("runtimeBindings") or []),
            "validation_case_count": len(instance.get("validationCases") or []),
            "satisfy_relationship_count": len(instance.get("satisfyRelationships") or []),
        }

    @staticmethod
    def _build_scenario_summary(instance: Dict[str, Any]) -> Dict[str, Any]:
        if not instance:
            return {}
        use_case, scenario = SessionStore._main_use_case_and_scenario(instance)
        return {
            "use_case_id": use_case.get("id"),
            "main_scenario_id": scenario.get("id"),
            "goal": scenario.get("goal") or use_case.get("goal"),
            "step_count": len(scenario.get("steps") or []),
            "validation_case_count": len(instance.get("validationCases") or []),
        }

    @staticmethod
    def _build_capability_summary(instance: Dict[str, Any]) -> Dict[str, Any]:
        if not instance:
            return {}
        runtime_bindings = instance.get("runtimeBindings") or []
        binding_counts: Dict[str, int] = {}
        runtime_action_count = 0
        for binding in runtime_bindings:
            if not isinstance(binding, dict):
                continue
            capability_id = str(binding.get("capability_id") or "")
            binding_counts[capability_id] = binding_counts.get(capability_id, 0) + 1
            runtime_action_count += len(binding.get("runtimeActions") or [])
        return {
            "capability_count": len(instance.get("capabilities") or []),
            "runtime_binding_count": len(runtime_bindings),
            "runtime_action_count": runtime_action_count,
            "capabilities": [
                {
                    "id": capability.get("id"),
                    "runtime_binding_count": binding_counts.get(str(capability.get("id") or ""), 0),
                }
                for capability in instance.get("capabilities") or []
                if isinstance(capability, dict)
            ],
        }

    @staticmethod
    def _build_handoff_summary(agent_roles: Dict[str, Any], analyze_report: Dict[str, Any]) -> Dict[str, Any]:
        agents = [agent for agent in agent_roles.get("agents") or [] if isinstance(agent, dict)]
        agent_ids = {str(agent.get("id") or "") for agent in agents}
        declared_pairs = []
        self_handoff_count = 0
        valid_target_count = 0
        for agent in agents:
            source = str(agent.get("id") or "")
            for target in agent.get("handoff_targets") or []:
                target_id = str(target)
                declared_pairs.append((source, target_id))
                if target_id == source:
                    self_handoff_count += 1
                if target_id in agent_ids and target_id != source:
                    valid_target_count += 1
        pair_count = len(declared_pairs)
        validations = analyze_report.get("validations") or {}
        handoff_metrics = (validations.get("handoff_derivation") or {}).get("metrics") or {}
        return {
            "agent_count": len(agents),
            "declared_handoff_pair_count": pair_count,
            "valid_handoff_target_ratio": (valid_target_count / pair_count) if pair_count else 1.0,
            "handoff_decision_accuracy": float(handoff_metrics.get("handoff_decision_accuracy") or 0.0),
            "self_handoff_count": self_handoff_count,
        }

    @staticmethod
    def _build_room_knowledge_summary(
        normalized_scene: Dict[str, Any],
        scene_semantics: Dict[str, Any],
        group_summary: Dict[str, Any],
        knowledge: List[Dict[str, Any]],
        functionalmlds_instance: Dict[str, Any],
    ) -> Dict[str, Any]:
        semantic_zones = scene_semantics.get("semantic_zones") or []
        knowledge_tags = {str(entry.get("tag") or "") for entry in knowledge if isinstance(entry, dict)}
        agent_tags = {
            str(tag)
            for agent in functionalmlds_instance.get("agents") or []
            if isinstance(agent, dict)
            for tag in agent.get("knowledge_tags") or []
        }
        object_groups = [
            str(group.get("group") or "")
            for group in group_summary.get("groups") or []
            if isinstance(group, dict) and not group.get("is_structural")
        ]
        grounded_groups = {
            str(group)
            for agent in functionalmlds_instance.get("agents") or []
            if isinstance(agent, dict)
            for group in agent.get("grounded_object_groups") or []
        }
        return {
            "room_object_count": len(normalized_scene.get("objects") or []),
            "semantic_zone_count": len(semantic_zones),
            "knowledge_file_count": len(knowledge),
            "agent_to_knowledge_tag_coverage": (
                len(agent_tags & knowledge_tags) / len(agent_tags)
                if agent_tags
                else 1.0
            ),
            "object_group_to_agent_role_grounding": (
                len(set(object_groups) & grounded_groups) / len(set(object_groups))
                if object_groups
                else 1.0
            ),
            "important_object_groups": object_groups,
            "semantic_zones": [
                str(zone.get("zone_id") or zone.get("name") or "")
                for zone in semantic_zones
                if isinstance(zone, dict)
            ],
        }

    @staticmethod
    def _main_use_case_and_scenario(instance: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        use_cases = (instance.get("requirementsModel") or {}).get("useCases") or []
        use_case = use_cases[0] if use_cases and isinstance(use_cases[0], dict) else {}
        scenarios = use_case.get("scenarios") or []
        scenario = scenarios[0] if scenarios and isinstance(scenarios[0], dict) else {}
        return use_case, scenario

    def _generate_arrow_draft(
        self,
        arrow_payload: Dict[str, Any],
        *,
        history: List[Dict[str, str]],
        current: Optional[ArrowProjectDraft] = None,
    ) -> Dict[str, Any]:
        schema = arrow_project_schema()
        arrow_text = json.dumps(arrow_payload, ensure_ascii=False, indent=2)
        current_summary = ""
        if current is not None:
            current_summary = json.dumps(
                {
                    "analysis": current.analysis,
                    "project": current.project,
                    "agents": current.agents,
                    "knowledge": current.knowledge,
                    "placement_preview": current.placement_preview,
                },
                ensure_ascii=False,
                indent=2,
            )

        dev_prompt = (
            "Du bist ein Projekt-Assistent für Unity. Analysiere die folgende MLDSI-Datei (JSON) "
            "und leite daraus eine Projektbeschreibung, passende Agenten (mit Personas), und benötigte "
            "Wissenseinträge ab. Antworte präzise, strukturiert und auf Deutsch. "
            "Die Agentenauswahl soll sich am Raumtyp orientieren (z. B. Klassenraum -> Lehrer, Schüler, Rektor; "
            "Firmenpräsentation -> PR, Marketing, Vertrieb, Technik). Nutze die Raum-Beschreibung/Metadaten "
            "aus der MLDSI-Datei als primäre Leitlinie für Rollen, Ton und Expertise. "
            "Gib außerdem für jeden Agenten passende Voice-Settings an: "
            "voice_gender (\"weiblich\" oder \"männlich\"), voice (Stimm-ID passend zum Geschlecht), "
            "voice_style (z. B. klar, kreativ, präzise, warm, neutral) und tts_model (gpt-4o-mini-tts). "
            "Verwende nach Möglichkeit folgende Stimm-IDs: weiblich = coral, nova, shimmer; "
            "männlich = alloy, verse, onyx, fable, echo. "
            "Gib eine kurze assistant_message, die dem Nutzer die Analyse und evtl. Rückfragen zusammenfasst. "
            "Erstelle zusätzlich eine placement_preview mit:\n"
            "- room_objects: nur Objekte am Boden (y nahe 0) mit id, name, position (x,y,z) und radius.\n"
            "- agent_placements: sinnvolle, kontextbezogene Agentenpositionen (x,y,z; y=0).\n"
            "Achte darauf, dass Agenten nicht mit room_objects überlappen und untereinander "
            "einen Mindestabstand halten. Verwende nur die MLDSI-Informationen für Objektlage."
            "\n\nMLDSI JSON:\n"
            f"{arrow_text}"
        )

        input_msgs: List[Dict[str, Any]] = [{"role": "developer", "content": dev_prompt}]
        if current_summary:
            input_msgs.append(
                {
                    "role": "developer",
                    "content": "Aktueller Entwurf (bei Aktualisierung berücksichtigen):\n" + current_summary,
                }
            )
        for m in history:
            input_msgs.append({"role": m["role"], "content": m["content"]})

        try:
            parsed, resp, out_text = self.openai.create_structured_json(
                model=self.model,
                input_messages=input_msgs,
                schema=schema,
                schema_name="arrow_project",
                temperature=self.temperature,
            )
        except OpenAIHTTPError as e:
            if e.status != 400:
                raise
            parsed, resp, out_text = self.openai.create_json_object(
                model=self.model,
                input_messages=input_msgs,
                temperature=self.temperature,
            )

        return self._normalize_arrow_draft(parsed, room_plan=arrow_payload, fallback=current)

    def _normalize_arrow_draft(
        self,
        parsed: Dict[str, Any],
        *,
        room_plan: Dict[str, Any],
        fallback: Optional[ArrowProjectDraft] = None,
    ) -> Dict[str, Any]:
        fallback_project = fallback.project if fallback else {}
        fallback_agents = fallback.agents if fallback else []
        fallback_knowledge = fallback.knowledge if fallback else []

        assistant_message = str(parsed.get("assistant_message") or fallback.assistant_message if fallback else "").strip()
        analysis = str(parsed.get("analysis") or fallback.analysis if fallback else "").strip()

        project_data = parsed.get("project") or {}
        display_name = str(project_data.get("display_name") or fallback_project.get("display_name") or "Neues Projekt").strip()
        description = str(project_data.get("description") or fallback_project.get("description") or "").strip()

        agents_raw = parsed.get("agents")
        if not isinstance(agents_raw, list):
            agents_raw = fallback_agents
        agents: List[Dict[str, Any]] = []
        for idx, agent in enumerate(agents_raw or []):
            if not isinstance(agent, dict):
                continue
            display = str(agent.get("display_name") or f"Agent {idx+1}").strip()
            agent_id = str(agent.get("id") or _slugify(display) or f"agent_{idx+1}").strip()
            persona = str(agent.get("persona") or "").strip()
            voice = str(agent.get("voice") or "").strip()
            voice_gender = str(agent.get("voice_gender") or "").strip()
            voice_style = str(agent.get("voice_style") or "").strip()
            tts_model = str(agent.get("tts_model") or "").strip()
            expertise = agent.get("expertise") or []
            if isinstance(expertise, str):
                expertise = [expertise]
            knowledge_tags = agent.get("knowledge_tags") or []
            if isinstance(knowledge_tags, str):
                knowledge_tags = [knowledge_tags]
            if not voice_gender and voice:
                if voice in {"coral", "nova", "shimmer"}:
                    voice_gender = "weiblich"
                elif voice in {"alloy", "verse", "onyx", "fable", "echo"}:
                    voice_gender = "männlich"
            if not voice and voice_gender:
                voice = "coral" if voice_gender == "weiblich" else "alloy"
            if not voice:
                voice = "alloy"
            if not voice_gender:
                voice_gender = "weiblich" if voice in {"coral", "nova", "shimmer"} else "männlich"
            if not voice_style:
                voice_style = "neutral"
            if tts_model.lower() == "standard":
                tts_model = ""
            if not tts_model:
                tts_model = "gpt-4o-mini-tts"
            agents.append(
                {
                    "id": agent_id,
                    "display_name": display,
                    "persona": persona,
                    "voice": voice,
                    "voice_gender": voice_gender,
                    "voice_style": voice_style,
                    "tts_model": tts_model,
                    "expertise": [str(x) for x in expertise],
                    "knowledge_tags": [str(x) for x in knowledge_tags],
                }
            )

        knowledge_raw = parsed.get("knowledge")
        if not isinstance(knowledge_raw, list):
            knowledge_raw = fallback_knowledge
        knowledge: List[Dict[str, Any]] = []
        for entry in knowledge_raw or []:
            if not isinstance(entry, dict):
                continue
            tag = str(entry.get("tag") or "").strip()
            name = str(entry.get("name") or "").strip()
            text = str(entry.get("text") or "").strip()
            knowledge.append({"tag": tag, "name": name, "text": text})

        placement_preview_raw = parsed.get("placement_preview")
        placement_preview_fallback = fallback.placement_preview if fallback else {}
        placement_preview = normalize_placement_preview(
            room_plan,
            agents,
            placement_preview_raw if isinstance(placement_preview_raw, dict) else placement_preview_fallback,
        )

        return {
            "assistant_message": assistant_message,
            "analysis": analysis,
            "project": {
                "display_name": display_name,
                "description": description,
            },
            "agents": agents,
            "knowledge": knowledge,
            "placement_preview": placement_preview,
        }
