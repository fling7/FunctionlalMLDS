# Wissensmanagement der Interactive Agents

Dieses Dokument beschreibt, wie Wissen im Projekt gespeichert, geladen, gesucht und zwischen Agenten im Gespraech weitergegeben wird. Es bezieht sich auf die aktuelle Implementierung in `backend/` und die Unity-Beispielclients in `unity_scripts/`.

## Kurzfassung

Das System trennt Wissen in drei Ebenen:

1. **Persistente Wissensbasis**: Textdateien unter `kb/<tag>/...` oder projektspezifisch unter `projects/<project_id>/kb/<tag>/...`.
2. **Agentenspezifisches Wissen**: Jeder Agent besitzt `knowledge_tags`. Diese Tags bestimmen, aus welchen Wissensordnern der Agent bei einer Nutzerfrage Snippets abrufen darf.
3. **Session-Gedaechtnis**: Eine laufende Chat-Session speichert Chat-Kontext je nach Modus entweder gemeinsam oder pro Agent getrennt.

Das Session-Gedaechtnis ist jetzt umschaltbar:

- `shared_history`: bisheriges Verhalten. Alle Agenten einer Session teilen dieselbe sichtbare Chat-History.
- `agent_private_history`: neues Testverhalten. Jeder Agent hat eine eigene Chat-History; andere Agenten sehen nur, was ihnen per Handoff-Brief uebergeben wurde.

Es gibt weiterhin keine echte interne Wissenssynchronisation zwischen Agenten. Agenten teilen sich dieselbe Wissensbasis-Dateisammlung, greifen aber je nach Tags auf unterschiedliche Ausschnitte zu.

## Zentrale Dateien

- `backend/kb.py`: Laedt lokale Wissensdateien, zerlegt sie in Chunks und fuehrt Keyword-Suche aus.
- `backend/state.py`: Verwaltet Sessions, Agentenprofile, Chat-History, Retrieval und Handoff-Orchestrierung.
- `backend/projects.py`: Verwaltet Projektordner, Agenten, Room-Plans und projektspezifische Wissenseintraege.
- `backend/server.py`: Stellt die HTTP-Endpunkte bereit, unter anderem `/setup`, `/chat` und die Projekt-Wissens-API.
- `unity_scripts/BackendClient.cs`: Minimaler Unity-Client fuer `/setup` und `/chat`.
- `unity_scripts/QuickAgentManager.cs`: Ausfuehrlicher Unity-Client mit Chat-Bubbles, Handoff-Linie, FPV-Handoff und TTS.

## Persistente Wissensbasis

Wissen liegt als einfache Textdatei-Struktur vor:

```text
kb/
  common/
    beispiel.md
  pricing/
    preise.md
  tech/
    integration.md
```

In Projekten ist die Struktur identisch, aber unterhalb des jeweiligen Projektordners:

```text
projects/<project_id>/
  project.json
  agents.json
  room_plan.json
  kb/
    <tag>/
      <datei>.txt
```

Die Tags sind die Ordnernamen direkt unterhalb von `kb`. Ein Agent verweist mit `knowledge_tags` auf diese Tags.

Unterstuetzte Dateitypen sind aktuell `.txt` und `.md`. Andere Dateien werden von `KnowledgeBase` ignoriert.

## Laden der Wissensbasis

Beim Backend-Start wird eine globale `KnowledgeBase` aus dem in `config.json` gesetzten `kb_root` geladen. Standard ist:

```json
"kb_root": "kb"
```

Die globale Wissensbasis wird beim Start erzeugt und in `SessionStore.kb` gehalten. Sie gilt fuer Setups, die nicht ueber `project_id` laufen.

Wenn `/setup` mit `project_id` aufgerufen wird, wird stattdessen eine projektspezifische `KnowledgeBase` aus folgendem Pfad geladen:

```text
projects/<project_id>/kb/
```

Diese projektspezifische KB wird in `SessionStore.kb_cache` zwischengespeichert. Wenn Wissen ueber die Projekt-API geaendert oder geloescht wird, ruft das Backend `refresh_project_kb(project_id)` auf und laedt die Projekt-KB neu.

Wichtig: Eine bereits laufende `SessionState` haelt eine Referenz auf die KB, die beim `/setup` aktiv war. Wenn Wissen waehrend einer laufenden Session geaendert wird, sollte `/setup` erneut ausgefuehrt werden, damit die Session sicher mit der frisch geladenen KB arbeitet.

## Chunking und Suche

`KnowledgeBase` liest alle `.txt`- und `.md`-Dateien ein und zerlegt sie in Chunks. Die Chunk-Groesse wird ueber `kb_chunk_chars` in `config.json` gesteuert. Standard laut Beispielkonfiguration:

```json
"kb_chunk_chars": 900
```

Die Zerlegung funktioniert so:

- Der Text wird an Leerzeilen in Absaetze geteilt.
- Absaetze werden zu Chunks zusammengepackt, bis die Zielgroesse erreicht ist.
- Wenn keine Absaetze erkannt werden, wird der Text als Fallback in feste Zeichenbloecke geteilt.
- Jeder Chunk bekommt Tokens aus Buchstaben, Zahlen und `_`.

Bei jeder Nutzerfrage sucht das Backend relevante Chunks mit einfacher Keyword-Ueberschneidung:

- Die aktuelle Nutzerfrage wird tokenisiert.
- Es werden nur Chunks aus den Tags betrachtet, die der aktive Agent in `knowledge_tags` hat.
- Haben die `knowledge_tags` keine Eintraege, betrachtet die Suche alle Tags der Session-KB.
- Treffer brauchen mindestens ein uebereinstimmendes Token.
- Sortiert wird nach Anzahl der Ueberschneidungen plus einem kleinen Coverage-Bonus.
- Die maximale Anzahl an Snippets wird ueber `kb_max_snippets` gesteuert. Standard laut Beispielkonfiguration:

```json
"kb_max_snippets": 4
```

Es gibt aktuell keine Embeddings, keine semantische Vektorsuche und keine Datenbank. Die Suche ist bewusst lokal, klein und nachvollziehbar.

## Memory-Modi

Der Modus wird beim Backend-Start aus `config.json` gelesen:

```json
"memory_mode": "shared_history"
```

Er kann pro `/setup`-Request ueberschrieben werden:

```json
{
  "project_id": "museonova_xr",
  "memory_mode": "agent_private_history"
}
```

Die `/setup`-Antwort und `/chat`-Antwort enthalten den aktiven Modus als `memory_mode`.

Unterstuetzte Werte:

- `shared_history`
- `agent_private_history`

Der Unity-`QuickAgentManager` bietet dafuer im UI einen Umschalter `Gemeinsam` / `Privat`.

## Was alle Agenten im Modus `shared_history` gemeinsam wissen

Alle Agenten einer Session teilen:

- dieselbe Session-ID,
- dieselbe Session-History,
- dieselbe geladene KB-Instanz der Session,
- dieselbe Agentenliste,
- die sichtbaren Antworten anderer Agenten, sofern sie bereits in der History stehen.

Die Session-History liegt in `SessionState.history` und enthaelt Eintraege mit:

```json
{"role": "user", "content": "..."}
{"role": "assistant", "content": "..."}
```

Diese History wird bei jedem Agentenaufruf als Gespraechskontext an das Modell gegeben. Sie ist also das gemeinsame Gespraechsgedaechtnis der Agenten.

Wichtig: Die History speichert nur Rolle und Text. Sie speichert nicht explizit, welcher Agent eine fruehere Assistant-Antwort erzeugt hat. In der HTTP-Antwort gibt es zwar `events` mit `agent_id`, aber in der gespeicherten Modell-History landen nur die sichtbaren Antworttexte.

## Was nicht gemeinsam geteilt wird

Nicht gemeinsam geteilt werden:

- die interne Persona eines anderen Agenten,
- die intern gefundenen KB-Snippets eines anderen Agenten,
- Confidence-Werte,
- Raw-Responses des Modells,
- Handoff-Schema-Details,
- nicht sichtbare Developer-Prompts.

Wenn Agent A beim Antworten KB-Snippets benutzt, bekommt Agent B diese Snippets nicht automatisch. Im Modus `shared_history` sieht Agent B spaeter aber den sichtbaren Antworttext von Agent A in der gemeinsamen History. Im Modus `agent_private_history` sieht Agent B diesen Text nur, wenn B selbst beteiligt war oder per Handoff einen Brief bekommen hat.

## Privates Agentengedaechtnis

Im Modus `agent_private_history` fuehrt die Session getrennte Histories pro Agent:

```text
agent_histories["agent_a"]
agent_histories["agent_b"]
agent_histories["agent_c"]
```

Wenn der Nutzer Agent B direkt anspricht, bekommt B nur:

- seine eigene bisherige History,
- die aktuelle Nutzerfrage,
- seine Persona und Expertise,
- seine eigenen KB-Snippets aus `knowledge_tags`.

Gesprache mit Agent A oder C werden B nicht automatisch gegeben.

Bei einem Handoff wird Agent B nicht die komplette History von Agent A uebergeben. Agent A liefert stattdessen ein Feld `handoff_brief`. Daraus baut das Backend einen kompakten Uebergabekontext fuer B. Dieser Kontext wird in B's private History aufgenommen, damit B darauf in spaeteren eigenen Gespraechen aufbauen kann.

## Gemeinsames Wissen ueber Tags

Ein Tag ist nur dann fuer mehrere Agenten gemeinsam nutzbar, wenn mehrere Agenten denselben Tag in `knowledge_tags` haben.

Beispiel:

```json
{
  "id": "agent_sales",
  "knowledge_tags": ["common", "pricing"]
}
```

Wenn alle Agenten den Tag `common` enthalten, koennen alle Agenten passende Snippets aus `kb/common/...` abrufen. Wenn nur ein Agent `pricing` besitzt, kann nur dieser Agent aus `kb/pricing/...` abrufen.

Das System kennt keine Sonderbehandlung fuer den Namen `common`. `common` ist nur eine Konvention. Technisch ist es ein normaler Tag wie `pricing`, `tech` oder `legal`.

## Was ein einzelner Agent weiss

Ein Agent wird in `agents.json` beschrieben. Relevant fuer Wissen und Verhalten sind vor allem:

```json
{
  "id": "agent_tech",
  "display_name": "Tina",
  "persona": "Du bist Tina, technische Expertin ...",
  "expertise": ["Integration", "API", "Unity"],
  "knowledge_tags": ["common", "tech"]
}
```

Ein Agent besitzt individuell:

- `id`: technische eindeutige Kennung,
- `display_name`: Anzeigename,
- `persona`: Rollen- und Verhaltensanweisung,
- `expertise`: Kompetenzbeschreibung fuer Prompt und Handoff-Auswahl,
- `knowledge_tags`: erlaubte Wissensbereiche fuer Retrieval,
- optional Voice- und TTS-Einstellungen,
- optional bevorzugte Zonen oder Spawn-Tags.

Bei einem Modellaufruf wird fuer genau diesen Agenten ein Developer-Prompt gebaut. Dieser enthaelt:

- Name und ID des Agenten,
- Persona,
- Expertise,
- Kommunikationsregeln,
- Handoff-Regeln, falls Handoff erlaubt ist,
- Liste anderer verfuegbarer Agenten mit deren Expertise,
- relevante lokale Wissensauszuege fuer die aktuelle Nutzerfrage.

Dadurch hat jeder Agent eine eigene Perspektive, auch wenn alle auf derselben technischen Infrastruktur laufen.

## Ablauf von `/setup`

`/setup` erzeugt eine neue Chat-Session. Das Backend unterstuetzt drei Datenquellen:

1. Direkte Daten im Request:

```json
{
  "room_plan": {},
  "agents": []
}
```

2. Pfade innerhalb des Repositories:

```json
{
  "room_plan_path": "examples/room_plan.example.json",
  "agents_path": "examples/agents.example.json"
}
```

3. Projekt-ID:

```json
{
  "project_id": "museonova_xr"
}
```

Bei `project_id` werden geladen:

- `projects/<project_id>/room_plan.json`,
- `projects/<project_id>/agents.json`,
- `projects/<project_id>/kb/`.

Danach erstellt `create_session`:

- `AgentSpec`-Objekte aus den Agenten-JSON-Daten,
- Spawn-Platzierungen ueber `assign_spawn_points`,
- eine `SessionState` mit Agenten, Platzierungen, KB und leerer History.

Die Antwort von `/setup` enthaelt die Session-ID und die Agenten mit Position, Blickrichtung, Spawnpoint, Zone und Tags. Die Persona, Expertise und `knowledge_tags` werden nicht an Unity zurueckgegeben; sie bleiben Backend-Kontext.

## Ablauf einer normalen Chat-Nachricht

Unity sendet an `/chat`:

```json
{
  "session_id": "...",
  "active_agent_id": "agent_tech",
  "user_text": "Was kostet die Integration?"
}
```

Das Backend macht dann:

1. Session anhand `session_id` suchen.
2. Aktiven Agenten anhand `active_agent_id` bestimmen. Wenn die ID fehlt oder ungueltig ist, wird der erste Agent der Session verwendet.
3. Nutzertext an die bisherige History anhaengen, zunaechst nur temporaer.
4. Fuer den aktiven Agenten KB-Snippets suchen:
   - Query ist nur die aktuelle Nutzerfrage.
   - Tags kommen aus `agent.knowledge_tags`.
   - Anzahl der Snippets kommt aus `kb_max_snippets`.
5. Developer-Prompt fuer den Agenten bauen.
6. OpenAI Responses API mit Structured Output aufrufen.
7. Ergebnis normalisieren.
8. Antwort in `events` schreiben.
9. History dauerhaft aktualisieren und auf `max_history_turns` kuerzen.

Das erwartete Modellformat ist:

```json
{
  "say": "Antworttext",
  "handoff_to": null,
  "handoff_reason": null,
  "handoff_brief": null,
  "confidence": 0.9
}
```

Wenn kein Handoff passiert, sieht die HTTP-Antwort vereinfacht so aus:

```json
{
  "session_id": "...",
  "active_agent_id": "agent_tech",
  "handoff": null,
  "events": [
    {"type": "say", "agent_id": "agent_tech", "text": "Antworttext"}
  ]
}
```

## Wie Handoff entschieden wird

Der aktive Agent wird beim ersten Aufruf mit `allow_handoff=True` angesprochen. Im Prompt steht die Regel:

- Wenn die Nutzerfrage deutlich ausserhalb der eigenen Expertise liegt oder die Sicherheit niedrig ist, soll der Agent an den passendsten anderen Agenten weiterleiten.
- Dann setzt das Modell `handoff_to` auf die ID des Zielagenten.
- `say` soll nur eine kurze Weiterleitungsformulierung sein, keine ausfuehrliche Antwort.

Das Structured-Output-Schema erlaubt als `handoff_to` nur IDs anderer Agenten oder `null`. Das Backend prueft zusaetzlich, ob die ID existiert und nicht die eigene ID ist.

Die Entscheidung ist also modellgestuetzt, aber durch die erlaubten IDs und das JSON-Schema begrenzt.

## Technischer Handoff-Ablauf im Backend

Wenn Agent A einen gueltigen Zielagenten B zurueckgibt und `max_handoffs > 0` ist:

1. Agent A erzeugt ein erstes Event:

```json
{"type": "say", "agent_id": "agent_a", "text": "Dazu leite ich dich an ... weiter."}
```

2. Agent A liefert zusaetzlich `handoff_brief`, also einen knappen Uebergabetext fuer Agent B.
3. Das Backend ruft Agent B direkt im selben `/chat`-Request auf.
4. Agent B bekommt:
   - dieselbe Nutzerfrage,
   - eine Developer-Nachricht, dass Agent A gerade weitergeleitet hat,
   - optional den `handoff_reason`,
   - optional den `handoff_brief`,
   - eigene KB-Snippets aus den Tags von Agent B.
5. Im Modus `shared_history` bekommt Agent B weiterhin die gemeinsame bisherige History.
6. Im Modus `agent_private_history` bekommt Agent B nur seine eigene History plus den Uebergabekontext.
7. Fuer Agent B ist Handoff deaktiviert (`allow_handoff=False`), damit keine Kettenweiterleitung entsteht.
8. Agent B erzeugt ein zweites Event mit der eigentlichen Antwort.
9. `active_agent_id` der HTTP-Antwort wird auf Agent B gesetzt.

Vereinfachte Antwort:

```json
{
  "session_id": "...",
  "active_agent_id": "agent_b",
  "handoff": {
    "from": "agent_a",
    "to": "agent_b",
    "reason": "Preisfrage gehoert zum Vertrieb.",
    "brief": "Der Nutzer fragt nach Preisen fuer ein Schulpaket und moechte wissen, welche Laufzeit sinnvoll ist."
  },
  "events": [
    {"type": "say", "agent_id": "agent_a", "text": "Ich leite dich an den Vertrieb weiter."},
    {"type": "say", "agent_id": "agent_b", "text": "Unsere Preise beginnen bei ..."}
  ]
}
```

Die Anzahl der automatischen Handoffs wird durch `max_handoffs` in `config.json` begrenzt. In der aktuellen Implementierung wird bei einem gueltigen Handoff maximal ein Zielagent im selben Request aufgerufen, weil Agent B mit deaktiviertem Handoff antwortet.

## Was bei der Uebergabe wirklich uebergeben wird

Im Modus `shared_history` wird uebergeben:

- die aktuelle Nutzerfrage,
- die gemeinsame Session-History,
- der sichtbare Weiterleitungstext von Agent A,
- der Zielagent `handoff_to`,
- der optionale `handoff_reason`,
- der optionale `handoff_brief`,
- ein Hinweis im Developer-Prompt von Agent B, dass Agent A weitergeleitet hat.

Im Modus `agent_private_history` wird uebergeben:

- die aktuelle Nutzerfrage,
- die private bisherige History von Agent B,
- der Zielagent `handoff_to`,
- der optionale `handoff_reason`,
- der `handoff_brief` als kompakter Uebergabekontext,
- ein Hinweis im Developer-Prompt von Agent B, dass Agent A weitergeleitet hat.

Nicht uebergeben wird:

- die interne Prompt-Konstruktion von Agent A,
- die fuer Agent A gefundenen KB-Snippets,
- interne Scores der KB-Suche,
- der Confidence-Wert als gesonderter Kontext fuer Agent B,
- die komplette private History von Agent A im Modus `agent_private_history`,
- nicht sichtbare Gedanken oder Zwischenentscheidungen.

Agent B beantwortet die Frage also mit seinem eigenen Profil und seinem eigenen Wissenszugriff. Die Uebergabe ist eine Gespraechsuebergabe, keine Datenmigration zwischen Agenten.

## Handoff in Unity

Unity wertet die `/chat`-Antwort ueber `ChatResponse` aus:

```csharp
public class ChatResponse
{
    public string session_id;
    public string active_agent_id;
    public Handoff handoff;
    public ChatEvent[] events;
}
```

Im einfachen `AgentManagerExample.cs` wird `activeAgentId` direkt auf `resp.active_agent_id` gesetzt und jedes Event geloggt.

`QuickAgentManager.cs` macht mehr:

- Ohne FPV-Proximity-Handoff:
  - setzt Unity sofort den aktiven Agenten auf `resp.active_agent_id`,
  - zeigt bei Handoff eine Weiterleitungs-Bubble,
  - zeichnet eine gelbe Linie vom Startagenten zum Zielagenten,
  - zeigt danach die Event-Bubbles nacheinander.

- Mit aktivem FPV-Proximity-Handoff:
  - zeigt Unity zunaechst nur die Events des weiterleitenden Agenten,
  - speichert die Zielagenten-Events als pending,
  - markiert den Zielagenten visuell,
  - zeigt einen Richtungspfeil zum Zielagenten,
  - liefert die Zielantwort erst aus, wenn der Nutzer nahe genug am Zielagenten ist.

Damit kann das Backend den fachlichen Handoff entscheiden, waehrend Unity die raeumliche Uebergabe inszeniert.

## Projekt-Wissen bearbeiten

Projektspezifisches Wissen wird ueber die Projekt-API verwaltet:

- `GET /projects/{id}/knowledge`: Wissenseintraege listen.
- `POST /projects/{id}/knowledge/read`: Eintrag lesen.
- `POST /projects/{id}/knowledge`: Eintrag erstellen, aktualisieren oder loeschen.

Beim Speichern werden `tag` und `name` slugifiziert. Ein Upsert schreibt standardmaessig:

```text
projects/<project_id>/kb/<tag>/<name>.txt
```

Nach Upsert oder Delete wird die Projekt-KB im Cache aktualisiert. Fuer neue Sessions ist das Wissen danach verfuegbar.

## MLDSI-/Arrow-Projektgenerierung

Die Endpunkte:

- `POST /projects/arrow/analyze`
- `POST /projects/arrow/chat`
- `POST /projects/arrow/commit`

koennen aus einem Raum-JSON einen Projektentwurf erzeugen. Dabei werden Agenten, Personas, `knowledge_tags` und Wissenseintraege vom Modell vorgeschlagen. Beim Commit speichert das Backend:

- Projektmetadaten,
- Agenten,
- Room-Plan,
- Wissenseintraege unter `projects/<project_id>/kb/...`.

Danach wird die Projekt-KB aktualisiert und kann ueber `/setup` mit `project_id` verwendet werden.

## Grenzen des aktuellen Systems

- Retrieval ist Keyword-basiert, nicht semantisch.
- Die KB wird pro `KnowledgeBase`-Instanz geladen; Root-KB-Aenderungen nach Serverstart werden nicht automatisch erkannt.
- Laufende Sessions behalten ihre KB-Referenz.
- Agenten teilen nur sichtbare Chat-History, keine internen Snippets.
- Die gespeicherte History enthaelt keine Agenten-ID pro Assistant-Nachricht.
- Handoff ist auf eine direkte Weiterleitung im Request ausgelegt.
- Wissen ist dateibasiert und lokal; es gibt keine externe Datenbank.

## Praktische Empfehlungen

- Gemeinsames Grundwissen in einen Tag wie `common` legen und diesen Tag allen Agenten geben.
- Fachwissen in getrennten Tags halten, zum Beispiel `pricing`, `tech`, `legal`, `product`.
- `expertise` so formulieren, dass andere Agenten daraus ein gutes Handoff-Ziel erkennen koennen.
- Nach Aenderungen an Projektwissen `/setup` erneut ausfuehren, wenn eine laufende Unity-Session das neue Wissen sicher nutzen soll.
- Bei unscharfen Nutzerfragen kurze Rueckfragen erwarten; das ist im Agentenprompt ausdruecklich vorgesehen.
- Fuer bessere Treffer wichtige Begriffe und Synonyme direkt in den Wissensdateien aufnehmen, da die Suche auf Token-Ueberschneidung basiert.
