# Grenzen: MLDS Project Wizard und FunctionalMLDS-Integration

Stand: 2026-07-09

## Zweck

Dieses Dokument grenzt ab, was der umgebaute `MLDSI Project Wizard` im FunctionalMLDS-Modus leistet und was bewusst ausserhalb des aktuellen Umfangs liegt. Die Grenzen sind wichtig fuer Nutzer, Tests und wissenschaftliche Interpretation.

## Keine Automatische 3D-Geometrie-Generierung Aus FunctionalMLDS

FunctionalMLDS erzeugt aktuell keine neue Unity-Geometrie und importiert auch keine vollstaendigen 3D-Assets in die Szene.

Der Materialisierungsschritt schreibt:

- `project.json`
- `room_plan.json`
- `agents.json`
- `kb/...`
- `trace_map.json`

Dabei wird die urspruengliche MLDS/MLDSI-Quelle als `room_plan.json` in das Backend-Projekt uebernommen. Unity nutzt diese Daten fuer Agenten-Setup, Platzierung, Raumwissen und Hindernis-/Objektbezug. Der Wizard baut aber nicht automatisch Waende, Moebel, Meshes oder Interaktionsobjekte als sichtbare Unity-GameObjects nach.

## Raumgeometrie Bleibt MLDS/room_plan

Die Geometriequelle bleibt die MLDS/MLDSI-Datei bzw. das daraus materialisierte `room_plan.json`.

FunctionalMLDS referenziert und strukturiert diese Raumdaten semantisch:

- Objekte und Objektgruppen werden geerdet.
- Agentenrollen werden auf Zonen, Objekte und Wissensbereiche bezogen.
- Agentenplatzierungen werden gegen Raumgrenzen und Hindernis-Footprints validiert.
- Raumwissen wird in der Projekt-KB materialisiert.

FunctionalMLDS ersetzt aber nicht das Raumformat. Es ist in diesem Umbau die Modell-, Trace- und Validierungsschicht ueber der bestehenden MLDS-/room_plan-Raumrepraesentation.

## FunctionalMLDS Steuert Struktur, Nicht Rendering

FunctionalMLDS steuert im aktuellen Projekt:

- Requirements, UseCases, Scenarios und ScenarioSteps.
- Agenten, Rollen, Spezialwissen und Handoff-Beziehungen.
- Capabilities, RuntimeBindings und RuntimeActions.
- ValidationCases und Traceability.
- Generierte Knowledge-Artefakte.
- Runtime-Trace-Bezug ueber `trace_map.json`.

FunctionalMLDS steuert aktuell nicht:

- visuelles Level-Design in Unity,
- automatische Mesh-Erzeugung,
- Material-, Shader- oder Lichtsetzung,
- Animationen jenseits der bestehenden Agentenruntime,
- physikalisch genaue Simulation von Objektzustaenden,
- vollstaendige Interaktionslogik fuer beliebige Maschinen oder Werkzeuge.

## Agentenruntime Bleibt Interactive Agents

Das Zielartefakt bleibt ein Interactive-Agents-Projekt. FunctionalMLDS ist die strukturierende und pruefende Schicht, nicht ein eigener Unity-Agentenruntime-Ersatz.

Die Runtime laeuft weiterhin ueber:

- Python-Backend-Endpunkte wie `/setup` und `/chat`.
- Projektdateien unter `InteractiveAgents/projects/<project_id>/`.
- `QuickAgentManager` in Unity.
- Projekt-KB und Agentenspezifikationen.

FunctionalMLDS macht diese Runtime-Aktionen tracebar und validierbar. Es ersetzt aber nicht die Chat-, Handoff-, TTS-, STT- oder Spawn-Implementierung.

## Wizard-Chat Im FunctionalMLDS-Modus Ist Kein Sofortiger Modell-Patch

Im Legacy-Modus kann Wizard-Chat den Draft direkt fortschreiben.

Im FunctionalMLDS-Modus werden Chat-Aenderungswuensche als Refinement Requests vorgemerkt. Das ist absichtlich konservativ: Eine Aenderung soll nicht nur den sichtbaren Draft veraendern, sondern erneut durch Pipeline, Modellinstanz und Validierungen laufen. Bis zur erneuten Regeneration ist der Draft nicht final.

## LLM-Stufen Sind Begrenzte Semantische Stufen

Die Pipeline nutzt LLM-Aufrufe fuer semantische Zwischenergebnisse, etwa Szene-Semantik, Rollen oder Wissen. Deterministische Wiederverwendung und deterministische Reparaturen werden zuerst genutzt.

Die aktuelle Implementierung beweist daher nicht, dass jede moegliche MLDS ohne LLM-Varianz gleich ausfaellt. Sie belegt, dass die erzeugten Artefakte nach der Generierung validiert, reparierbar eingegrenzt und ueber Stages nachvollzogen werden koennen.

## Aktueller Scope Der Case Study

Der aktuelle Fokus liegt auf raumkundigen Agenten:

- Agenten kennen Raum, Objekte, Zonen und Wissensbereiche.
- Agenten besitzen Spezialwissen.
- Agenten koennen Handoffs an fachlich geeignetere Agenten ausloesen.
- Runtime-Verhalten wird ueber Setup, Chat, Handoff und Answer Grounding geprueft.

Nicht vollstaendig abgedeckt sind:

- stateful object manipulation,
- physische Bediensequenzen komplexer Maschinen,
- Safety-/Timing-Analysen wie in produktionsnahen Automotive-Toolchains,
- breite statistische Generalisierung,
- Expertenvalidierung jeder semantischen Modellentscheidung.

Diese Punkte koennen spaeter als ergaenzende Modelle oder weitere Case Studies angebunden werden.

## Wissenschaftliche Interpretation

Die aktuelle Implementierung stuetzt eine begrenzte, aber belastbare Aussage:

FunctionalMLDS macht die evaluierte MLDS-zu-Interactive-Agents-Pipeline tracebar, validierbar und runtime-pruefbar, ohne den Legacy-Modus zu brechen.

Sie stuetzt nicht die Aussage:

FunctionalMLDS sei damit fuer alle Domaenen, alle industriellen Toolchains oder alle moeglichen Interaktionsobjekte vollstaendig validiert.

Diese Grenze sollte in Paper, Demo und Verteidigung explizit benannt werden.
