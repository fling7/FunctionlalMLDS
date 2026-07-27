# Kriterien 11.1: Wann darf der Kern angepasst werden?

Stand: 2026-07-07

Task: 11.1 `Kriterien fuer Kernanpassung festlegen`

Zweck: Diese Kriterien entscheiden noch keine konkrete Anpassung. Sie legen fest, wann eine erkannte Modellierungsluecke in den Kern des Metamodells gehoert und wann sie als Ergaenzungsmodell, Konvention oder kein Modellbedarf behandelt werden muss.

Bezugsdateien:

- `common_concepts_A_B.md`
- `differences_A_B.md`
- `entity_agent_scene_object_decision.md`
- `state_assertion_object_state_decision.md`
- `capability_runtime_vivian_action_decision.md`
- `spatial_relationship_decision.md`
- `interaction_object_affordance_decision.md`
- `agent_goal_role_runtime_profile_decision.md`

## Kernregel

Eine Kernanpassung ist nur gerechtfertigt, wenn ein Bedarf allgemein, kompakt, EAST-ADL-nah und wiederverwendbar ist und nicht sauber durch bestehende Kernklassen oder ein optionales Modul geloest werden kann.

Der Kern ist fuer die stabile fachliche Trace-Kette verantwortlich:

`Requirement -> UseCase -> Scenario -> ScenarioStep -> Event/Condition/StateAssertion -> CapabilityUse -> Capability -> Effect -> RuntimeBinding -> RuntimeAction -> ValidationCase`

Alles, was nur eine bestimmte Domaene, Runtime, Dialogstrategie, Geometrie, Bedienoberflaeche oder Plattform betrifft, darf den Kern nicht vergroessern.

## Harte Ausschlusskriterien

Wenn eines der folgenden Kriterien zutrifft, darf der Bedarf nicht als Kernanpassung umgesetzt werden.

| Ausschluss | Bedeutung | Beispiel |
| --- | --- | --- |
| Domaenenspezifisch | Der Bedarf ist nur fuer A oder nur fuer B zentral. | Kaffeemaschinen-Affordances, Vivian-Dialog, konkrete Spatial-Geometrie |
| Technisch statt fachlich | Der Bedarf beschreibt Endpoints, Topics, Controller, Adapter, Schemas, Modellversionen oder Ausfuehrungsparameter. | Vivian-LLM-Profil, CoffeeMachineAdapter-Version |
| Bereits modellierbar | Der Bedarf ist mit bestehenden Klassen ohne harte Inkonsistenz abbildbar. | Rollenzustand als `StateAssertion`, Starttaste als `Event.expression` in der Baseline |
| Besser modular | Der Bedarf kann optional an Kernklassen andocken, ohne die Kernkette zu veraendern. | `InteractionObjectModule`, `SpatialSemanticsModule`, `AssistantInteractionModule` |
| Verletzung einer Kerninvariante | Die Anpassung wuerde eine bestehende Trennlinie aufheben. | direkte Kante `ScenarioStep -> RuntimeAction` |
| Nur bessere Dokumentation | Die Anpassung erhoeht Lesbarkeit, aber nicht formale Modellierbarkeit oder Pruefbarkeit. | rein sprechendere Namen ohne neue Semantik |

## Pflichtkriterien fuer eine Kernanpassung

Alle Pflichtkriterien muessen erfuellt sein. Wenn auch nur eines fehlt, ist der Bedarf kein Kernkandidat.

| ID | Pflichtkriterium | Prueffrage | Nachweis |
| --- | --- | --- | --- |
| K1 | Allgemeingueltigkeit | Gilt der Bedarf unabhaengig von VR, Vivian, Kaffeemaschine, Agentendynamik oder einer einzelnen Beispieldomaene? | Mindestens A und B oder eine klare allgemeine Modellregel zeigen denselben Bedarf. |
| K2 | Kompaktheit | Laesst sich die Anpassung mit minimaler Klasse, Beziehung oder optionalem Attribut ausdruecken? | Keine neue umfangreiche Teilontologie im Kern; keine Verdopplung bestehender Konzepte. |
| K3 | EAST-ADL-Nahe | Passt die Anpassung zur Use-Case-, Requirements-, Satisfy-, Trace- und Verhaltenslogik von EAST-ADL-naher Modellierung? | Begriff und Beziehung bleiben fachlich, tracebar und nicht runtime-spezifisch. |
| K4 | Wiederverwendbarkeit | Kann die Anpassung in mehreren industriellen Toolchains, Use Cases und Domaenen wiederverwendet werden? | Der Begriff ist nicht beispiel- oder toolgebunden. |
| K5 | Notwendigkeit | Ist der Bedarf mit `Entity`, `Agent`, `Event`, `Condition`, `StateAssertion`, `Capability`, `RuntimeBinding` und `ValidationCase` nicht sauber genug abbildbar? | Ohne Anpassung entsteht eine echte semantische Luecke, nicht nur ein Komfortverlust. |
| K6 | Invariantenvertraeglichkeit | Bleiben Actor/Agent-Trennung, fachlich/technisch-Trennung und Scenario/Runtime-Trennung erhalten? | Keine neue direkte technische Kurzschlusskante. |
| K7 | Kardinalitaet und Eindeutigkeit | Lassen sich Rollen, Kardinalitaeten, Besitzsemantik und Richtung der Beziehung eindeutig angeben? | Jede neue Beziehung hat klare Multiplizitaet und Kompositions-/Assoziationsentscheidung. |

## Unterstuetzende Kriterien

Diese Kriterien muessen nicht alle gleichzeitig erfuellt sein, staerken aber die Begruendung einer Kernanpassung.

| ID | Unterstuetzendes Kriterium | Warum wichtig? |
| --- | --- | --- |
| U1 | Traceability-Gewinn | Eine Kernanpassung sollte Anforderungen, Szenarios, Effekte oder Validierung nachweisbar besser verbinden. |
| U2 | Maschinenlesbarkeit | Die Anpassung sollte nicht nur Text ersetzen, sondern automatische Pruefung, Generierung oder Konsistenzanalyse ermoeglichen. |
| U3 | Rueckwaertskompatibilitaet | Bestehende A- und B-Instanzen sollten ohne Bruch migrierbar sein. |
| U4 | Semantische Nicht-Ueberlappung | Die Anpassung darf kein vorhandenes Konzept unter anderem Namen wiederholen. |
| U5 | Stabilitaet | Der Begriff sollte nicht von kurzfristigen Tool-, Runtime- oder Projektentscheidungen abhaengen. |
| U6 | Gute Modularisierbarkeit | Auch wenn die Anpassung Kern wird, sollte sie optionale Details an Module abgeben koennen. |
| U7 | Validierbarkeit | Es muss klar sein, wie ein Modellpruefer die neue Struktur auf Gueltigkeit kontrolliert. |

## Entscheidungsregel

| Ergebnis | Regel |
| --- | --- |
| `Kern` | Alle Pflichtkriterien K1 bis K7 sind erfuellt und kein hartes Ausschlusskriterium trifft zu. |
| `Kernkandidat mit Vorsicht` | K1 bis K7 sind erfuellt, aber der konkrete Zuschnitt muss noch verkleinert oder kardinalitaetssicher gemacht werden. |
| `Ergaenzungsmodell` | Der Bedarf ist maschinenlesbar wichtig, aber domaenenspezifisch, optional, detailreich oder besser andockbar. |
| `kein Modellbedarf` | Der Bedarf ist in der Baseline ausreichend durch Expressions, StateAssertions, Tabellenkonvention oder Dokumentation abgedeckt. |
| `zurueckstellen` | Der Bedarf ist plausibel, aber es fehlen Beispiele, Kardinalitaeten, Invarianten oder ein klarer Nutzen. |

Eine Kernanpassung muss also positiv begruendet werden. Es reicht nicht, dass eine neue Klasse "nuetzlich" waere.

## Anwendung auf bekannte Kandidaten als Plausibilitaetscheck

Diese Tabelle ist noch nicht die vollstaendige Bewertung aus Task 11.3. Sie prueft nur, ob die Kriterien erwartbar wirken.

| Kandidat | Erwartete Einordnung nach Kriterien | Kurze Begruendung |
| --- | --- | --- |
| optionale `Entity.kind [0..1]` | `Kernkandidat mit Vorsicht` | Allgemein, kompakt, wiederverwendbar; muss mit kleinen, stabilen Kategorien definiert werden. |
| optionale Kante `Effect -> StateAssertion [0..*]` | `Kernkandidat mit Vorsicht` | Staerkt Traceability in A und B, bleibt fachlich und kompakt; Besitzsemantik muss klar sein. |
| `SpatialSemanticsModule` | `Ergaenzungsmodell` | Maschinenlesbar wichtig, aber detailreich und A-getrieben; Geometrie gehoert nicht in den Kern. |
| `InteractionObjectModule` | `Ergaenzungsmodell` | Fuer B stark, fuer A optional; Affordances sollen an `Entity` andocken. |
| `AssistantInteractionModule` | `Ergaenzungsmodell` | Vivian-Dialog ist wichtig, aber B-spezifisch und darf `Capability` nicht ueberladen. |
| `AgentBehaviorModule` | `Ergaenzungsmodell` | Interne Ziele und Policies sind relevant bei Autonomie, aber nicht Baseline-Kern. |
| `RuntimeProfileModule` | `Ergaenzungsmodell` | Technische Plattform- und Adapterprofile gehoeren unter RuntimeBinding, nicht in den fachlichen Kern. |
| direkte `ScenarioStep -> RuntimeAction` | ausgeschlossen | Verletzt die zentrale fachlich/technische Trennung. |

## Mindestdokumentation je Kernanpassung

Falls spaeter eine Kernanpassung beschlossen wird, muss sie mindestens folgende Informationen enthalten:

| Pflichtangabe | Inhalt |
| --- | --- |
| Neuer oder geaenderter Begriff | Name, Definition und Abgrenzung zu bestehenden Klassen. |
| Zweck | Welche echte Luecke geschlossen wird. |
| Beziehungen | Quelle, Ziel, Richtung, Kardinalitaet und Kompositions-/Assoziationsart. |
| Invariante | Mindestens eine Regel, die Fehlmodellierung verhindert. |
| A/B-Nachweis | Zeigt, wie die Anpassung in A und B oder allgemein in der Kernkette genutzt wird. |
| Nicht-Ziele | Was explizit in Ergaenzungsmodelle ausgelagert bleibt. |
| Migrationshinweis | Wie bestehende Instanzen ohne Bruch weiter gelten. |

## Abnahmekontrolle

| Kriterium aus Task 11.1 | Erfuellung |
| --- | --- |
| Kriterienliste vorhanden | Pflicht-, Ausschluss- und unterstuetzende Kriterien sind definiert. |
| Allgemeingueltigkeit enthalten | K1 fordert domaenenunabhaengige Gueltigkeit. |
| Kompaktheit enthalten | K2 fordert minimale, nicht aufblaehende Anpassung. |
| EAST-ADL-Nahe enthalten | K3 fordert Requirements-, Use-Case-, Satisfy-, Trace- und Verhaltensnaehe. |
| Wiederverwendbarkeit enthalten | K4 fordert Nutzung ueber Beispiele und Toolchains hinweg. |
| Entscheidungsregel vorhanden | Abschnitt `Entscheidungsregel` ordnet `Kern`, `Ergaenzungsmodell`, `kein Modellbedarf` und `zurueckstellen` zu. |
| Vorbereitung fuer 11.2/11.3 vorhanden | Harte Ausschluesse und Plausibilitaetscheck trennen Kernkandidaten von optionalen Modulen. |

## Konsequenz fuer Task 11.2

Task 11.2 soll nun spiegelbildlich Kriterien fuer Ergaenzungsmodelle festlegen. Dort muss nicht mehr gefragt werden, ob ein Bedarf in den Kern darf, sondern wann ein optionales Modul gerechtfertigt ist, wie es andockt und wie es den Kern entlastet.
