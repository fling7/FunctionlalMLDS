# Anwendungsfall B: Systemgrenze

Stand: 2026-07-07

Task: 6.2 `Systemgrenze fuer B festlegen`

Zweckbezug: Anwendungsfall B beschreibt, wie eine Benutzerrolle in einer virtuellen Szene mit Vivian als fachlich beteiligter Assistenz ein Interaktionsobjekt, exemplarisch eine Kaffeemaschine, bedient, sodass eine konkrete Bedienhandlung pruefbar in einen erwarteten Objektzustand und eine passende Systemrueckmeldung ueberfuehrt wird.

## Kurzdefinition der Systemgrenze

Im Scope liegt die fachliche Modellierung einer assistierten Objektinteraktion in einer virtuellen Szene: Benutzerhandlung, Vivian-Beteiligung, bedienbares Kaffeemaschinenobjekt, relevante Objektzustaende, Bedingungen, fachliche Capabilities, nachvollziehbare Runtime-Bindung und Validierung.

Out of Scope liegen die konkrete Engine-Implementierung, physische Kaffeemaschinen-Hardware, Renderingdetails, 3D-Asset-Erzeugung, Low-Level-Controllercode, interne LLM- oder Dialogmodell-Mechanik und reale Getraenkezubereitung.

## Im Scope

| Bereich | Im Scope | Modellnahe Begruendung |
| --- | --- | --- |
| Benutzerinteraktion | Fachliche Beschreibung, welche externe Benutzerrolle eine Bedienhandlung ausloest, bestaetigt, abbricht oder beobachtet. | Wird spaeter ueber `Actor`, `ScenarioStep.kind = actorIntent`, `Event`, `Condition` und `ValidationCase` abbildbar. |
| Vivian-Beteiligung | Vivian wird als fachlich relevantes Assistenzkonzept betrachtet, z. B. fuer Anleitung, Rueckfrage, Bestaetigung, Fehlerhinweis oder assistierte Ausfuehrung. | Die genaue Einordnung als `Actor`, `Agent`, `Entity` oder Kombination folgt in Task 6.3; die Beteiligung selbst liegt im Scope. |
| Kaffeemaschine als Interaktionsobjekt | Die Kaffeemaschine ist ein bedienbares Objekt mit relevanten Zustaenden, Bedienpunkten und beobachtbaren Reaktionen. | Die genaue Einordnung als `Entity`, Asset, Runtime-Ziel oder Interaktionsobjekt-Erweiterung folgt in Task 6.4. |
| Bedienhandlungen | Fachliche Handlungen wie Starttaste druecken, Auswahl treffen, Vorgang starten, Vorgang abbrechen oder Vivian um Hilfe bitten. | Wird spaeter in Task 6.5 gesammelt und ueber `Event`, `ScenarioStep`, `CapabilityUse` und `Effect` strukturiert. |
| Objektzustaende | Pruefbare Zustaende der Kaffeemaschine, z. B. bereit, nicht bereit, brueht, fertig, Fehlerzustand oder wartet auf Eingabe. | Wird spaeter ueber `StateAssertion`, `Condition`, `Effect` und ggf. ein Interaktionsobjekt-Ergaenzungsmodell abbildbar. |
| Vorbedingungen und Guards | Pruefbare Bedingungen fuer Bedienung, z. B. Maschine verfuegbar, Wasser vorhanden, Tasse platziert, Start erlaubt, Vivian-Hilfe aktiv. | Passt zu `Condition.kind` und zu Capability-Preconditions. |
| Fachliche Capabilities | Fachliche Faehigkeiten wie Bereitschaft pruefen, Bruehvorgang starten, Rueckmeldung geben oder Bedienfehler behandeln. | Wird ueber `CapabilityUse`, `Capability` und `Effect` modelliert; technische Details bleiben draussen. |
| Runtime-Bindung | Nachvollziehbare Zuordnung fachlicher Capabilities zu technischen Bindungen und Aktionen, soweit fuer Traceability und Validierung relevant. | Wird ueber `RuntimeBinding`, `RuntimeAction` und `ValidationCase` angebunden, ohne `ScenarioStep` technisch kurzzuschliessen. |
| Validierung | Pruefung, ob Stimulus, Bedingungen und erwartete Outcomes zusammenpassen, z. B. Startsignal fuehrt zu `coffeeMachine.state = brewing`. | Wird ueber `ValidationCase.expectedOutcome`, `StateAssertion` und ggf. RuntimeBinding-Pruefung beschrieben. |
| Traceability | Nachvollziehbarkeit von Requirement/UseCase ueber Szenario, Bedienhandlung, Capability, RuntimeBinding und ValidationCase. | Entspricht dem Kernziel des kompakten Dynamic-Functional-MLDS-Metamodells. |

## Out of Scope

| Bereich | Out of Scope | Begruendung |
| --- | --- | --- |
| Engine-Implementierung | Unity-, Unreal-, WebXR- oder sonstige konkrete Controller-, Script- oder Komponentenimplementierung. | Das Metamodell beschreibt fachliche Ablaeufe und Bindungen, nicht den Code selbst. |
| Physische Hardware | Elektrische Kaffeemaschinensteuerung, Pumpen, Heizelemente, reale Wasserzirkulation oder Maschinenfirmware. | Betrachtet wird das virtuelle Interaktionsobjekt, nicht ein reales Geraet. |
| Reale Getraenkezubereitung | Temperaturkurven, Mahlgrad, Extraktionsdruck, Hygiene oder Lebensmittelqualitaet. | Fuer die VR-Interaktion relevant ist der beobachtbare Objektzustand, nicht reale Kaffeequalitaet. |
| 3D-Asset-Erzeugung | Meshes, Texturen, Materialien, Animation Clips oder Prefab-Erzeugung der Kaffeemaschine. | Diese Assets koennen existieren, sind aber nicht Gegenstand der fachlichen Verhaltensmodellierung. |
| Rendering und UI-Designdetails | Shader, Beleuchtung, Kamera, Schriftgroessen, Partikeleffekte oder visuelle Gestaltung der Rueckmeldung. | Im Scope ist nur, dass Rueckmeldung existiert und pruefbar ist. |
| Low-Level-Interaktionsmechanik | Collider, Raycast-Details, Handtracking-Offsets, Button-Hitboxen oder Input-Device-Treiber. | Diese Details gehoeren zu Runtime/Engine, nicht zum fachlichen Scenario. |
| Interne Vivian-Implementierung | LLM-Prompting, NLU-Pipeline, Dialogpolicy, Speech-to-Text, Text-to-Speech oder Avatar-Rendering. | Vivian wird fachlich als Assistenzbeteiligung modelliert, nicht als interne KI-Architektur. |
| Vollstaendige Raum- oder Inventarmodellierung | Nicht relevante Moebel, Dekorationen, nicht bediente Objekte oder allgemeine Szenenausstattung. | Nur fuer Bedienung, Bedingungen, Zustand oder Validierung relevante Entities gehoeren in den Scope. |
| Nutzerstudie | Empirische Usability-, Lernwirksamkeits- oder Praesenzmessung. | Kann spaeter eine externe Evaluation sein, ist aber nicht Teil der Modellinstanziierung. |

## Eindeutige Einsortierung der Abnahmekriterien

| Abnahmekriterium | Einsortierung | Konsequenz fuer die naechsten Tasks |
| --- | --- | --- |
| Vivian | Im Scope als fachlich beteiligte Assistenz; out of scope als konkrete LLM-, Avatar-, Sprach- oder Dialogimplementierung. | Task 6.3 entscheidet, ob Vivian als `Actor`, `Agent`, `Entity` oder Kombination modelliert wird. |
| Kaffeemaschine | Im Scope als bedienbares Interaktionsobjekt mit Zustaenden und Effekten; out of scope als reale Hardware oder reines 3D-Asset. | Task 6.4 entscheidet die fachliche Einordnung und trennt Objektzustand von technischer Ansteuerung. |
| Benutzerinteraktion | Im Scope als fachliche Bedienhandlung, Ereignis, Absicht, Rueckfrage oder Abbruch; out of scope als Low-Level-Inputmechanik. | Task 6.5 sammelt konkrete Bedienhandlungen mit Ausloeser, Ziel und Effekt. |
| Runtime-Ausfuehrung | Im Scope als Trace von Capability zu RuntimeBinding/RuntimeAction und ValidationCase; out of scope als konkrete Codeausfuehrung oder Engine-Skript. | Die spaeteren Mapping-Tasks duerfen technische Aktionen erst unter `RuntimeBinding -> RuntimeAction` anlegen. |

## Grenzentscheidungen

| Frage | Entscheidung |
| --- | --- |
| Darf ein ScenarioStep direkt `CoffeeMachineController.startBrewing()` nennen? | Nein. Der Schritt beschreibt fachlich den Bruehstart; der Controller-Aufruf gehoert spaeter unter `RuntimeAction`. |
| Darf Vivian eine Handlung im Szenario ausfuehren? | Ja, fachlich im Scope. Ob das als Actor-Absicht, Agent-Aktion oder Entity-Capability modelliert wird, entscheidet Task 6.3. |
| Darf die Kaffeemaschine Zustaende besitzen? | Ja. Zustaende wie `ready`, `brewing`, `finished` oder `error` sind fachlich relevant und als `StateAssertion` pruefbar. |
| Darf die Kaffeemaschine technische Endpoints besitzen? | Nicht als fachliches Objekt. Technische Endpoints liegen ausschliesslich in `RuntimeAction` unter einer `RuntimeBinding`. |
| Darf eine Bedienhandlung fehlschlagen? | Ja. Fehler- und Ausnahmefaelle sind im Scope, werden aber erst in Task 6.8 gesammelt. |
| Wird jetzt schon ein Interaktionsobjekt-Ergaenzungsmodell eingefuehrt? | Nein. Der Bedarf wird in B gesammelt und spaeter in den Modellierbarkeits- und Entscheidungsaufgaben bewertet. |

## Nicht vorweggenommen

Dieser Task legt noch nicht fest:

- ob Vivian `Actor`, `Agent`, `Entity` oder eine Kombination ist,
- ob die Kaffeemaschine nur `Entity`, ein Asset, ein Runtime-Ziel oder Teil eines Interaktionsobjekt-Ergaenzungsmodells ist,
- welche konkreten Bedienhandlungen verwendet werden,
- welche Objektzustaende vollstaendig benoetigt werden,
- welche Preconditions und Fehlerfaelle gelten,
- welche Capabilities, RuntimeBindings oder RuntimeActions angelegt werden,
- ob das Kernmetamodell wegen B angepasst oder ein Ergaenzungsmodell eingehangen wird.

## Abnahmekontrolle

| Kriterium aus Task 6.2 | Erfuellung |
| --- | --- |
| Liste `im Scope` vorhanden | Abschnitt `Im Scope` grenzt die relevanten Bereiche ab. |
| Liste `out of Scope` vorhanden | Abschnitt `Out of Scope` grenzt Implementierungs- und Nicht-Zielbereiche ab. |
| Vivian eindeutig einsortiert | Vivian ist fachlich im Scope, technische KI-/Avatar-/Dialogimplementierung out of scope. |
| Kaffeemaschine eindeutig einsortiert | Virtuelles Interaktionsobjekt im Scope, reale Hardware und Asset-Erzeugung out of scope. |
| Benutzerinteraktion eindeutig einsortiert | Fachliche Bedienhandlung im Scope, Low-Level-Inputmechanik out of scope. |
| Runtime-Ausfuehrung eindeutig einsortiert | Runtime-Trace im Scope, Codeausfuehrung und Engine-Skript out of scope. |
| Keine spaeteren Entscheidungen vorweggenommen | 6.3, 6.4, 6.5, 6.6, 6.7 und 6.8 bleiben fachlich offen. |

## Konsequenz fuer Task 6.3

Task 6.3 muss Vivian fachlich einordnen. Dabei ist strikt zu trennen zwischen Vivian als externer Rolle im Use Case, Vivian als ausfuehrender oder beobachteter Agent/Entity in der Szene und Vivian als moeglicher Traeger fachlicher Capabilities.
