# Entscheidung 10.6: Werden raeumliche Beziehungen explizit benoetigt?

Stand: 2026-07-07

Task: 10.6 `Pruefen, ob raeumliche Beziehungen explizit benoetigt werden`

Verglichene Use Cases:

- `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`
- `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Bezugsdateien:

- `differences_A_B.md`
- `entity_agent_scene_object_decision.md`
- `state_assertion_object_state_decision.md`
- `capability_runtime_vivian_action_decision.md`
- `use_case_A_indirect_modelability.md`
- `use_case_A_gap_decision_matrix.md`
- `use_case_B_indirect_modelability.md`
- `use_case_B_gap_decision_matrix.md`

## Entscheidung

Raeumliche Beziehungen werden fuer die aktuellen Baseline-Beispiele nicht als explizite Kernklassen benoetigt.

Sie werden aber als optionales `SpatialSemanticsModule` benoetigt, sobald Position, Naehe, Sichtbarkeit, Erreichbarkeit, Distanz, Flaeche, Volumen, Kollisionszonen oder Referenzrahmen maschinenlesbar geprueft, generiert oder in einer Runtime konsistent berechnet werden sollen.

Damit lautet die Entscheidung:

| Frage | Entscheidung |
| --- | --- |
| Reichen `Condition.expression`, `Event.expression` und `StateAssertion.expectedState` fuer die Baseline? | ja |
| Braucht der Kern neue Klassen wie `SpatialRelation`, `SpatialRegion` oder `SpatialFrame`? | nein |
| Braucht Anwendungsfall A bei automatischer Raumpruefung ein Spatial-Modul? | ja |
| Braucht Anwendungsfall B bei Bedienzonen oder Affordance-Geometrie ein Spatial-Modul? | ja, aber meist als Teil von Interaktionsobjekt-/Affordance-Semantik |
| Soll Spatial Semantics in `Capability`, `RuntimeBinding` oder Vivian-Dialog modelliert werden? | nein |
| Empfohlene Behandlung | optionales `SpatialSemanticsModule`, an `Entity`, `Event`, `Condition` und `StateAssertion` angebunden |

Die Kernlinie bleibt: Raum kann im kompakten Kern qualitativ beschrieben werden. Raum wird erst dann explizit modelliert, wenn er nicht nur beschrieben, sondern maschinenlesbar verarbeitet werden muss.

## Aktuelle Kernabbildung

| Raeumlicher Sachverhalt | Aktuelle Abbildung | Beispiel | Bewertung |
| --- | --- | --- | --- |
| Position | `StateAssertion.expectedState` oder `Condition.expression` | `at(AgentBody, TargetZone)` | fuer Baseline ausreichend |
| Einschluss | `Condition.expression` | `inside(AgentBody, SceneBoundary)` | fuer Baseline ausreichend |
| Naehe | `Condition.expression` | `near(Visitor, CoffeeMachine.startButton)` | fuer Baseline ausreichend, aber nicht geometrisch pruefbar |
| Erreichbarkeit | `Condition.expression` oder `StateAssertion.expectedState` | `reachable(AgentBody, TargetZone)` | fachlich ausreichend, aber ohne Begruendung |
| Bewegung | `StateAssertion.expectedState` und RuntimeAction-Trace | `movingTo(AgentBody, TargetZone)` | fachlich ausreichend, aber ohne Pfad/Trajektorie |
| Sichtbarkeit | `StateAssertion.expectedState` oder `Effect.observableBy` | `visibleTo(FeedbackSignal, SceneObserver)` | ausreichend fuer beobachtbare Wirkung |
| Bedienzone | `Event.expression` oder RuntimeAction-Schema | `placed(Cup, CoffeeMachine.cupArea)` | ausreichend fuer B-Baseline, aber keine Geometrie |

Diese Abbildung ist bewusst qualitativ. Sie sagt, was fachlich gelten soll, aber nicht, wie eine Engine Position, Entfernung, Sichtfeld, Kollisionsfreiheit oder Pfadkosten berechnet.

## Beispiele fuer explizit werdende Raumbeziehungen

Die folgenden Beispiele zeigen, wann die aktuell textuelle Abbildung nicht mehr genuegt.

| Kategorie | Baseline-Ausdruck | Wann explizit noetig? | Moegliche Modulstruktur |
| --- | --- | --- | --- |
| Position | `at(AgentBody, TargetZone)` | Wenn Koordinaten, Toleranz oder Zielvolumen pruefbar sein muessen. | `SpatialPosition`, `SpatialRegion`, `SpatialFrame` |
| Naehe | `near(Visitor, CoffeeMachine.startButton)` | Wenn ein Schwellwert, z. B. 0.5 m, fuer Bedienbarkeit gilt. | `SpatialRelation(kind=near, threshold=0.5m)` |
| Sichtbarkeit | `visibleTo(CoffeeMachine.display, Visitor)` | Wenn Sichtlinie, Occlusion, Blickrichtung oder Sichtbarkeitsdauer relevant sind. | `VisibilityRelation`, `Observer`, `Occluder` |
| Erreichbarkeit | `reachable(AgentBody, TargetZone)` | Wenn Pfad, Hindernisse, Navigation Mesh oder Bewegungsmodus beruecksichtigt werden. | `ReachabilityRelation`, `PathConstraint`, `ObstacleRegion` |
| Einschluss | `inside(AgentBody, SceneBoundary)` | Wenn Grenzen als Flaeche, Volumen oder Referenzrahmen ausgewertet werden. | `SpatialRegion`, `Boundary`, `ContainmentRelation` |
| Bedienbereich | `placed(Cup, CoffeeMachine.cupArea)` | Wenn Toleranz, Ausrichtung, Sensorbereich oder Cup-Pose relevant ist. | `InteractionZone` plus Spatial-Anbindung |

Damit ist die Abnahmebedingung erfuellt: Position, Naehe, Sichtbarkeit und Erreichbarkeit sind mit konkreten Beispielen benannt.

## Bewertung fuer Anwendungsfall A

A erzeugt den staerksten Spatial-Bedarf. Der dynamische Agent bewegt sich in einer Szene, reagiert auf Triggerzonen, Szenengrenzen, Zielbereiche und Hindernisse.

| A-Aspekt | Aktuelle Abbildung | Reicht fuer Baseline? | Wann Modul noetig wird |
| --- | --- | --- | --- |
| `TriggerZone` | `Entity`; `entered(SceneParticipant, TriggerZone)` in `Event.expression` | ja | Wenn Eintritt geometrisch oder sensorisch berechnet werden soll. |
| `SceneBoundary` | `Entity`; `inside(AgentBody, SceneBoundary)` | ja | Wenn Grenzen als Flaeche/Volumen pruefbar sein muessen. |
| `TargetZone` | `Entity`; `at(AgentBody, TargetZone)` und `movingTo(TargetZone)` | ja | Wenn Zielposition, Toleranz oder Navigationspfad relevant sind. |
| `ObstacleRegion` | `Entity`; Blockade in `Condition` und `StateAssertion` | ja | Wenn Kollision, Umgehung oder Pfadkosten geprueft werden. |
| Erreichbarkeit | `Condition.expression = reachable(TargetZone)` | ja, als fachliche Aussage | Wenn Reachability aus Raumdaten abgeleitet werden soll. |
| Beobachtungspunkt | `ObservationPoint` als `Entity` | ja | Wenn Messposition, Sichtlinie oder Sensorabdeckung relevant ist. |

Fuer A ist ein Spatial-Modul also fachlich plausibel, aber es sollte optional bleiben. Sonst wuerde der Kern Richtung Geometrie-, Navigations- oder Simulationsmodell kippen.

## Bewertung fuer Anwendungsfall B

B benoetigt Raum weniger als eigenstaendige Navigationssemantik, aber Raum tritt lokal bei Interaktionsobjekten auf.

| B-Aspekt | Aktuelle Abbildung | Reicht fuer Baseline? | Wann Modul noetig wird |
| --- | --- | --- | --- |
| Starttaste | `pressed(Visitor, CoffeeMachine.startButton)` | ja | Wenn Position, Reichweite, Sichtbarkeit oder Bedienzone der Taste geprueft werden soll. |
| Tassenbereich | `CoffeeMachine.cupArea`; `placed(Cup, CoffeeMachine.cupArea)` | ja | Wenn Cup-Pose, Toleranz, Sensorbereich oder Kollision relevant ist. |
| Programmauswahl | `selectedProgram(CoffeeMachine, coffee)` | ja | Wenn UI-Elemente raeumlich lokalisiert oder als Control Surfaces generiert werden sollen. |
| Fortschrittsanzeige | `shown(CoffeeMachine.progressIndicator)` | ja | Wenn Anzeigeort, Sichtbarkeit fuer Visitor oder Dauer relevant ist. |
| Vivian-Hinweise | RuntimeAction praesentiert Guidance | ja | Wenn Hinweise auf konkrete Stellen zeigen oder Highlights geometrisch verankert werden. |

Fuer B sollte Spatial Semantics nicht allein entworfen werden. Sie gehoert meist unter oder neben ein `InteractionObjectModule`, weil die raeumlichen Aspekte Bedienzonen, Control Surfaces, Affordances und Feedbackanzeigen betreffen.

## Abgrenzung zu anderen Modulen

| Modul | Grenze zu Spatial Semantics |
| --- | --- |
| `InteractionObjectModule` | Beschreibt Bedienpunkte, Affordances und erlaubte Manipulationen. Spatial Semantics beschreibt deren Position, Zone, Sichtbarkeit oder Reichweite. |
| `AssistantInteractionModule` | Beschreibt Vivians Dialogakte und GuidanceContent. Spatial Semantics beschreibt nur, worauf ein Hinweis raeumlich zeigt. |
| `StateTransitionModule` | Beschreibt erlaubte Zustandsuebergaenge. Spatial Semantics kann Guards wie `reachable` oder `inside` begruenden. |
| `RuntimeExecutionModule` | Beschreibt technische Reihenfolge, Retry, Profile und Schemas. Spatial Semantics bleibt fachlich/strukturell und darf nicht nur Runtime-Schema sein. |
| `EventDetailModule` | Beschreibt Quelle, Ziel, Payload und Kanal von Events. Spatial Semantics kann das raeumliche Ziel oder die Region eines Events formalisieren. |

Diese Abgrenzung verhindert, dass raeumliche Semantik in Capability-, Runtime- oder Dialogklassen versteckt wird.

## Vorgeschlagener Andockpunkt fuer ein optionales Modul

Ein optionales `SpatialSemanticsModule` sollte nicht den Kern ersetzen, sondern vorhandene Kernklassen referenzieren.

| Modulkonzept | Andockpunkt | Zweck |
| --- | --- | --- |
| `SpatialFrame` | Modellkontext oder Scene-Entity | Definiert Referenzrahmen wie Raum, Welt, Objektkoordinaten. |
| `SpatialRegion` | `Entity` | Beschreibt Flaeche, Volumen, Zone, Grenze oder Bedienbereich. |
| `SpatialPosition` | `Entity` | Beschreibt Punkt, Pose oder Bereich eines Subjekts. |
| `SpatialRelation` | `Entity`, `Condition`, `StateAssertion` | Beschreibt `inside`, `at`, `near`, `visibleTo`, `reachable`, `overlaps`. |
| `SpatialConstraint` | `Condition` | Macht Toleranz, Distanz, Sichtlinie oder Bewegungsregel pruefbar. |
| `ReachabilityRelation` | `Entity`, `ObstacleRegion`, `TargetZone` | Formalisiert erreichbare oder blockierte Ziele. |
| `VisibilityRelation` | `Entity`, `Actor` oder Observer-Entity | Formalisiert Sichtbarkeit, Sichtlinie, Occlusion oder Dauer. |
| `InteractionZone` | `InteractionObjectModule` und `SpatialRegion` | Verbindet Affordance-Bedienbereiche mit Raumstruktur. |

Wichtig: `SpatialRelation` sollte nicht direkt zu `RuntimeAction` fuehren. Auch bei raeumlicher Semantik bleibt der technische Pfad ueber `Capability -> RuntimeBinding -> RuntimeAction`.

## Kern- und Modulentscheidung

| Modellierungsbedarf | Entscheidung |
| --- | --- |
| Qualitative Raumangabe im Szenario | im Kern ueber `Condition.expression`, `Event.expression`, `StateAssertion.expectedState` |
| Position als erwarteter Zustand | im Kern als StateAssertion moeglich |
| Naehe als Guard | im Kern als Condition moeglich |
| Sichtbarkeit als erwarteter beobachtbarer Zustand | im Kern als StateAssertion oder Effect-Beobachtbarkeit moeglich |
| Erreichbarkeit als fachliche Bedingung | im Kern als Condition moeglich |
| Koordinaten, Referenzrahmen, Volumen, Toleranz | optionales `SpatialSemanticsModule` |
| Pfade, Hindernisse, Kollisionszonen, Navigation | optionales `SpatialSemanticsModule` |
| Bedienzonen und Control-Surface-Positionen | optionales `InteractionObjectModule` mit Spatial-Anbindung |
| Runtime-nahe Geometrieausfuehrung | optionales Runtime-/Spatial-Profil, nicht Kern |

## Invariantencheck

| Regel | Auswirkung |
| --- | --- |
| `ScenarioStep` darf keine direkte RuntimeAction referenzieren | Auch raeumliche Aktionen duerfen nicht direkt technisch kurzgeschlossen werden. |
| `Capability` enthaelt keine technischen Daten | Raumbezogene Faehigkeiten duerfen keine Engine-Koordinaten oder Controllerdetails enthalten. |
| `StateAssertion.subject [1]` | Raeumliche Zustandsaussagen brauchen ein identifizierbares Subjekt. |
| `ScenarioStep -> Condition [0..1]` | Ein Schritt kann einen raeumlichen Guard besitzen; komplexe Raumlogik sollte ausgelagert werden. |
| `ScenarioStep -> StateAssertion [0..*]` | Ein Schritt kann mehrere resultierende raeumliche Zustandsaussagen besitzen. |

Keine Invariante erzwingt ein Spatial-Modul im Kern.

## Abnahmekontrolle

| Kriterium aus Task 10.6 | Erfuellung |
| --- | --- |
| Entscheidung vorhanden | Raeumliche Beziehungen bleiben fuer die Baseline im Kern qualitativ; explizite Spatial Semantics wird optional. |
| Beispiele fuer Position genannt | `at(AgentBody, TargetZone)` und `SpatialPosition`. |
| Beispiele fuer Naehe genannt | `near(Visitor, CoffeeMachine.startButton)` und Distanzschwellwert. |
| Beispiele fuer Sichtbarkeit genannt | `visibleTo(CoffeeMachine.display, Visitor)` und `visibleTo(FeedbackSignal, SceneObserver)`. |
| Beispiele fuer Erreichbarkeit genannt | `reachable(AgentBody, TargetZone)` und Hindernis-/Pfadbezug. |
| A und B getrennt bewertet | A als raumgetriebener Agentenfall; B als lokal raeumliche Interaktionsobjektlogik. |
| Kein Kernumbau abgeleitet | Spatial Semantics wird als optionales Modul empfohlen. |

## Konsequenz fuer Task 10.7

Task 10.7 soll nun pruefen, ob Interaktionsobjekte eigene Affordances brauchen. Die Entscheidung aus 10.6 bereitet das vor: Raeumliche Bedienbereiche wie Starttaste, Tassenbereich oder Displayposition koennen nicht allein durch Spatial Semantics beschrieben werden. Sie brauchen bei hoeherer Praezision eine Affordance-Semantik, an die SpatialRegion oder InteractionZone andocken kann.
