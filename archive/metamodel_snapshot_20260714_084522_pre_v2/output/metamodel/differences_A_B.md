# Gemeinsame Analyse A/B: Unterschiede

Stand: 2026-07-07

Task: 10.2 `Unterschiede von A und B extrahieren`

Verglichene Use Cases:

- `UC-A-01` - `Dynamisches Agentenverhalten in virtueller Szene modellieren`
- `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Bezugsdateien:

- `common_concepts_A_B.md`
- `use_case_A_indirect_modelability.md`
- `use_case_A_non_modelable_gaps.md`
- `use_case_A_gap_decision_matrix.md`
- `use_case_B_indirect_modelability.md`
- `use_case_B_non_modelable_gaps.md`
- `use_case_B_gap_decision_matrix.md`

## Abgrenzung

Diese Datei beschreibt unterschiedliche Modellierungsbedarfe, nicht unterschiedliche Modellqualitaet. Beide Beispiele sind mit dem aktuellen kompakten Metamodell grundsaetzlich abbildbar. Der Unterschied liegt darin, welche fachlichen Semantiken bei automatischer Pruefung, Generierung oder Runtime-Ausfuehrung genauer strukturiert werden muessten.

Die gemeinsame Basis aus Task 10.1 bleibt unveraendert: Requirements, UseCase, Scenario, ScenarioStep, Event, Condition, StateAssertion, Capability, RuntimeBinding, RuntimeAction und ValidationCase bilden den gemeinsamen Kern. Task 10.2 trennt nur die Spezialisierungsrichtungen.

## Ergebnis

A und B unterscheiden sich primaer in der fachlichen Schwerpunktsetzung:

- A ist ein Szenario fuer Agentendynamik in einer virtuellen Szene. Der Modellierungsdruck entsteht durch raeumliche Relationen, Agentenrollen, Aktivitaetszustaende, Bewegung, Blockaden und beobachtbare Szenenzustaende.
- B ist ein Szenario fuer assistierte Interaktionsobjektlogik. Der Modellierungsdruck entsteht durch Bedienpunkte, Objektzustaende, Vivian-Assistenz, Readiness-Entscheidungen, Benutzerbestaetigung und technische Adapter zur Kaffeemaschine.

Daraus folgt: A treibt vor allem Spatial-, Agent-State- und Beobachtbarkeitsfragen. B treibt vor allem InteractionObject-, AssistantInteraction-, DecisionRule- und ObjectLifecycle-Fragen.

## Uebersicht der unterschiedlichen Modellierungsbedarfe

| Unterscheidungsachse | A: Agentendynamik | B: Interaktionsobjektlogik | Modellierungsfolge |
| --- | --- | --- | --- |
| Primaerer Fokus | Ein dynamischer Agent veraendert sein Verhalten in einer virtuellen Szene. | Ein Benutzer bedient mit Vivian ein technisches Interaktionsobjekt. | A prueft Agentenverhalten; B prueft objektbezogene Interaktion und Assistenz. |
| Zentrales modelliertes Subjekt | `AgentBody` plus raeumliche Entities wie `TriggerZone`, `TargetZone`, `ObstacleRegion`. | `VivianAssistant`, `CoffeeMachine`, `Cup`, `BrewingRequest`. | A benoetigt Agent-/Raumtypen; B benoetigt Objekt-, Assistenz- und Requesttypen. |
| Externe Rollen | Mehrere Rollen: Designer, Teilnehmer, Beobachter. | Eine Hauptrolle: Visitor. | `Actor` reicht in beiden Faellen; Unterschied ist Umfang, nicht neue Kernklasse. |
| Hauptausloeser | Raeumlicher Eintritt, Blockadeaenderung, externe Signale. | Benutzerhandlungen, Vivian-Signale, Maschinenzustaende. | A benoetigt raeumliche Eventsemantik staerker; B benoetigt Eventquelle, Zielobjekt und Payload staerker. |
| Zustandslogik | Agentenrolle, Aktivitaet, Position, Blockade, Zielerreichung. | Maschinen-Lifecycle, orthogonale Maschinenmerkmale, Request-Lifecycle, Vivian-Modus. | Beide nutzen `StateAssertion`; B braucht staerker Objektzustandsautomaten und State-Dimensions. |
| Raumbezug | Zentral: `inside`, `at`, `near`, `reachable`, `movingTo`. | Sekundaer: Tassenbereich, Bedienzone, Anzeigeort. | Spatial Semantics ist A-getrieben; fuer B eher Teil von Affordance-/InteractionZone-Semantik. |
| Interaktionsobjekt | Nur vorbereitet ueber generische `Entity` oder `InteractionAsset`. | Zentral: CoffeeMachine mit Starttaste, Tassenbereich, Programmauswahl, Feedback. | InteractionObject/Affordance ist B-getrieben und sollte optional bleiben. |
| Assistenz- und Dialoglogik | Rueckmeldung und InstructionMarker sind Neben-/Feedbackelemente. | Vivian fuehrt, erklaert, fragt nach und bestaetigt. | AssistantInteraction ist B-getrieben, kein allgemeiner Kernbedarf. |
| Entscheidungslogik | Erreichbarkeit, Blockade und Rollen-/Aktivitaetswechsel. | Readiness-Pruefung, Benutzerbestaetigung, Fehlerdiagnose, Startfreigabe. | B benoetigt eher DecisionRule/Authorization; A eher Spatial-/State-Guards. |
| Runtime-Landschaft | Vor allem VR-Szenenruntime fuer Agentenrolle, Zielhandlung und Blockadesicherung. | VivianRuntime, VRInteractionRuntime, CoffeeMachineAdapterRuntime und TraceRuntime. | B erzeugt mehr Runtime-Heterogenitaet; RuntimeExecution bleibt trotzdem unter `RuntimeBinding`. |
| Validierungsfokus | Rollenbindung, Zielhandlung, Blockade, Hauptpfadabschluss. | Guidance-Start, Tassen-/Programmpfad, Readiness, Bestaetigung, Bruehstart. | Validation bleibt gleich strukturiert, aber Testorakel und Stimulusarten unterscheiden sich. |
| Variantenbedarf | Alternative und Exception wegen Blockade. | Alternative fehlende Tasse, Exception nicht bereit, weitere denkbare Abbruch-/Timeout-Pfade. | B hat staerkeren Variation-/Recovery-Druck, aber nicht zwingend Kernbedarf. |
| Safety-Nahe | Nicht zentral; Blockade ist fachlich, nicht als SafetyCase modelliert. | Sicherer Nicht-Start ist fachlich relevant, SafetyCase aber noch optional. | Safety/Hazard darf nicht implizit in den Kern gezogen werden. |

## Klassifikation der Unterschiede

| Modellierungsbedarf | Klassifikation | Begruendung |
| --- | --- | --- |
| Agentenrolle, Agentenaktivitaet, Bewegung und Blockade | A-spezifisch stark | Diese Semantik beschreibt den dynamischen Agenten in der Szene und darf nicht als allgemeine Objektlogik formuliert werden. |
| Raumrelationen `inside`, `at`, `near`, `reachable`, `movingTo` | A-spezifisch stark; optionales Modul | Fuer A zentral, fuer B nur indirekt ueber Bedien- oder Tassenbereiche relevant. |
| Bedienpunkte, Affordances und Control Surfaces | B-spezifisch stark; optionales Modul | Starttaste, Tassenbereich und Programmauswahl sind Kern der Kaffeemaschinenbedienung, aber nicht Kern jeder `Entity`. |
| Vivian-Dialog, GuidanceContent und Modalitaet | B-spezifisch stark; optionales Modul | Vivian ist in B fachlich zentral; A hat nur allgemeines Feedback und InstructionMarker. |
| Readiness-Regeln, Diagnose und Korrekturvorschlag | B-spezifisch stark; optionales Modul | Die Readiness-Pruefung ist objekt- und domaenenspezifisch, kein allgemeiner Kernmechanismus. |
| State/Transition-Semantik | gemeinsam optional | A hat Agentenrollen und Aktivitaeten; B hat Maschinen-, Request- und Vivian-Zustaende. Beide bleiben aber aktuell mit `Condition`, `Event`, `ScenarioStep` und `StateAssertion` abbildbar. |
| Eventquelle, Eventziel, Payload und Kanal | gemeinsam optional | Beide Beispiele verwenden Eventausdruecke mit Quelle und Ziel, aber die Baseline braucht noch kein eigenes Event-Detailmodell. |
| RuntimeAction-Reihenfolge, Adapterprofil und Schemas | gemeinsam optional | Beide Beispiele haben technische Orchestrierungsfragen; diese gehoeren unter `RuntimeBinding`, nicht direkt in den fachlichen Kern. |
| Optionale `Entity.kind`-Typisierung | minimaler Kernkandidat | Grobe Typisierung ist allgemein, kompakt und rueckwaertskompatibel, solange sie optional bleibt. |
| Optionale Trace-Kante `Effect -> StateAssertion` | minimaler Kernkandidat | Die Kante verbessert Nachweisbarkeit in A und B, ohne die fachliche/technische Trennung aufzubrechen. |
| Mehr Schritte in B und mehr Actors in A | kein aktueller Modellbedarf | Das sind Instanzauspraegungen, die vorhandene Kardinalitaeten bereits abdecken. |
| Safety/Hazard-Argumentation | kein aktueller Modellbedarf; optional bei erweitertem Scope | Fuer den aktuellen B-Fall fachlich ansprechbar, aber ein SafetyCase waere ein eigenes EAST-ADL-nahes Ergaenzungsmodell. |

## Getrennte Bewertung: Agentendynamik

Agentendynamik ist der eigentliche Differenzkern von A. Der Agent ist nicht nur ein referenziertes Objekt, sondern ein aktives modelliertes Subjekt, dessen Rolle, Aktivitaet, Position und Blockadezustand sich im Szenario aendern.

| Aspekt der Agentendynamik | Aktuelle Abbildung | Unterschied zu B | Bewertung |
| --- | --- | --- | --- |
| Agent als aktives Subjekt | `Agent --|> Entity`, `Entity -> Capability`, `StateAssertion.subjectRef` | B hat Vivian ebenfalls als Agent, aber Vivians Hauptproblem ist Assistenz-/Dialogverhalten, nicht raeumliche Dynamik. | Kernkonzept vorhanden; keine neue Kernklasse noetig. |
| Rollenwechsel des Agenten | `StateAssertion.expectedState`, `Condition.expression`, `Capability` | B hat Moduswechsel bei Vivian, aber nicht denselben rollen- und bewegungsnahen Agentenzustand. | Fuer einfache Abbildung ausreichend; bei formaler Pruefung optionales `StateTransitionModule`. |
| Raeumliche Position und Bewegung | `Condition.expression`, `StateAssertion.expectedState`, RuntimeAction-Trace | B benoetigt Raum nur lokal fuer Bedienbereiche; A benoetigt Raum als Szenenlogik. | A-getriebenes optionales `SpatialSemanticsModule`, kein Kernumbau. |
| Blockade und Erreichbarkeit | Guards, Events, StateAssertions, Alternative/Exception | B hat Readiness/Fehlerdiagnose statt Navigationsblockade. | In A ueber Conditions abbildbar; fuer automatische Konsistenzpruefung Spatial-/State-Ergaenzung. |
| Beobachtbarkeit des Agentenverhaltens | `Effect.observableBy`, `StateAssertion`, `ValidationCase` | B validiert eher Bedien- und Assistenzwirkungen. | Gemeinsamer Validation-Kern reicht; optionale Trace-Kante `Effect -> StateAssertion` hilft beiden. |

Konsequenz: Agentendynamik bestaetigt nicht, dass das Kernmetamodell gross erweitert werden muss. Sie bestaetigt vor allem `Agent` als Spezialisierung von `Entity`, optionale `Entity.kind`-Typisierung und bei erweiterter Praezision ein optionales Spatial-/State-Ergaenzungsmodell.

## Getrennte Bewertung: Interaktionsobjektlogik

Interaktionsobjektlogik ist der eigentliche Differenzkern von B. Die Kaffeemaschine ist nicht nur ein Zustandstraeger, sondern ein bedienbares Objekt mit Affordances, Bedienpunkten, Rueckmeldungen, internen Zustandsmerkmalen und technischen Adapteraktionen. Vivian vermittelt diese Bedienung.

| Aspekt der Interaktionsobjektlogik | Aktuelle Abbildung | Unterschied zu A | Bewertung |
| --- | --- | --- | --- |
| Bedienbares Objekt | `CoffeeMachine` als `Entity.kind = asset` | A hat nur vorbereitete Interaktionsobjekte; B macht Bedienbarkeit zentral. | Fuer Baseline ausreichend; bei Generierung/Pruefung optionales `InteractionObjectModule`. |
| Affordances und Bedienpunkte | Starttaste, Tassenbereich und Programmauswahl in `Event.expression`, `Condition.expression`, Runtime-Schemas | A hat keine gleichwertige konkrete Affordance-Kette. | B-getriebener Modulbedarf, nicht Kernbedarf fuer alle Entities. |
| Objektzustandsautomat | Maschinen-Lifecycle und Request-Lifecycle als `StateAssertion` und Guards | A hat Agentenzustaende, aber keine technische Objektmaschine mit Readiness und Startfreigabe. | Gemeinsamer State/Transition-Bedarf, fuer B staerker objektgetrieben. |
| Readiness-Entscheidung | Conditions, Capability, Effect und RuntimeAction-Schemas | A hat Erreichbarkeit/Blockade, aber keine regelartige Objektbereitschaft. | B-getriebenes optionales `DecisionRuleModule`. |
| Vivian-Assistenz | Vivian als `Agent`, Guidance als Capability/Effect/RuntimeAction | A hat Feedback/InstructionMarker, aber keinen assistierenden Dialogagenten. | Optionales `AssistantInteractionModule`; nicht in `Capability` hineinziehen. |
| Benutzerbestaetigung und Autorisierung | Guards, StateAssertions, Request-Capability, RuntimeActions | A braucht keine vergleichbare Consent-/Authorization-Semantik. | Optionales Authorization-/Recovery-Modul bei erweitertem Scope. |

Konsequenz: Interaktionsobjektlogik darf nicht durch eine allgemeine Verkomplizierung von `Entity` geloest werden. Der Kern sollte nur identifizierbare Entities, optionale grobe Entity-Typisierung und die vorhandene Capability-/Runtime-Kette bereitstellen. Bedienpunkte, Affordances, DecisionRules und Dialoginhalte gehoeren in optionale Module.

## Unterschiedliche Modulimpulse

| Potenzielles Modul | A-Relevanz | B-Relevanz | Schlussfolgerung |
| --- | --- | --- | --- |
| `SpatialSemanticsModule` | hoch: Szene, Grenze, Zone, Bewegung, Erreichbarkeit | niedrig bis mittel: Bedienzone/Tassenbereich | A-getrieben, optional. B kann bei InteractionZones andocken. |
| `StateTransitionModule` | mittel bis hoch: Rollen- und Aktivitaetswechsel | hoch: Maschinen-, Request- und Vivian-Zustaende | Gemeinsamer optionaler Bedarf, aber nicht zwingend Kern. |
| `InteractionObjectModule` | niedrig bis mittel: vorbereitete InteractionAssets | hoch: Kaffeemaschine, Bedienpunkte, Affordances | B-getrieben, optional, an `Entity` andocken. |
| `AssistantInteractionModule` | niedrig: Feedback und InstructionMarker | hoch: Vivian-Dialog, GuidanceContent, Modalitaet | B-getrieben, optional, an `Agent`, `Capability` und `RuntimeBinding` andocken. |
| `DecisionRuleModule` | mittel: Erreichbarkeit und Blockade koennen regelartig werden | hoch: Readiness, Diagnose, Korrekturvorschlag | B-getrieben; A kann einfache Conditions behalten. |
| `EventDetailModule` | mittel: Quelle, Ziel und Payload fuer Raum-/Signalereignisse | mittel bis hoch: Benutzer-, Vivian- und Maschinenereignisse | Gemeinsames optionales Modul, falls automatische Event-Korrelation gefordert ist. |
| `RuntimeExecutionModule` | mittel: Reihenfolge innerhalb VR-Bindings | hoch: mehrere Runtimes und Adapter | Gemeinsames technisches Modul, strikt unter `RuntimeBinding`. |
| `SafetyArgumentModule` | niedrig im aktuellen A-Scope | niedrig bis mittel im aktuellen B-Scope, hoeher bei Automotive Safety | Nur bei explizitem Safety-Scope, nicht als aktueller Kernbedarf. |

## Nicht als modellrelevanter Unterschied werten

| Beobachtung | Warum kein eigener Modellierungsbedarf |
| --- | --- |
| B hat mehr Schritte als A | Schrittanzahl ist eine Instanzauspraegung; `ScenarioStep [1..*]` deckt beide ab. |
| A hat mehrere Actor-Rollen, B nur eine | `Actor` und `interactsWith` decken beide Faelle ab; kein neuer Metamodellbedarf. |
| B nutzt formale `Satisfy`-Instanzen noch nicht im gleichen Umfang wie A | Das ist ein Ausarbeitungsstand der Instanzen, nicht ein Unterschied im Metamodellbedarf. |
| Vivian koennte je nach Systemgrenze auch externer Dienst sein | Das ist eine Systemgrenzenfrage; fuer die aktuelle Baseline bleibt Vivian als `Agent`/`Entity` korrekt. |
| Beide nutzen Alternative und Exception | Die Pfadarten sind Gemeinsamkeit; unterschiedlich sind nur die fachlichen Ursachen. |
| Beide nutzen RuntimeActions | Die technische Kette ist Gemeinsamkeit; unterschiedlich sind nur Runtime-Kontexte und Adaptervielfalt. |

## Konsequenzen fuer die naechsten Tasks

| Folgetask | Relevanz der Unterschiede |
| --- | --- |
| 10.3 `Entity`/`Agent` fuer Szenenobjekte | Muss pruefen, ob grobe `Entity.kind`-Typisierung reicht oder ob Interaktionsobjekte eigene Klassen brauchen. |
| 10.4 `StateAssertion` fuer Objektzustaende | Muss Agenten-/Objektzustaende von formalen Zustandsautomaten und Transitionen trennen. |
| 10.5 `Capability`/`RuntimeBinding` fuer Vivian-Aktionen | Muss fachliche Faehigkeit, Dialoginhalt und technische Ausgabe getrennt halten. |
| 10.6 Spatial/Interaction-Ergaenzungen | Muss A-getriebene Spatial Semantics von B-getriebenen InteractionZones/Affordances unterscheiden. |
| 10.7 Kern versus Ergaenzungsmodell | Muss verhindern, dass B-spezifische Bedienlogik oder A-spezifische Raumlogik den Kern vergroessert. |

## Abnahmekontrolle

| Kriterium aus Task 10.2 | Erfuellung |
| --- | --- |
| Liste unterschiedlicher Modellierungsbedarfe vorhanden | Die Tabelle `Uebersicht der unterschiedlichen Modellierungsbedarfe` nennt die wesentlichen Differenzachsen. |
| Unterschiede explizit klassifiziert | Die Tabelle `Klassifikation der Unterschiede` ordnet Bedarfe als A-spezifisch, B-spezifisch, gemeinsam optional, minimaler Kernkandidat oder kein aktueller Modellbedarf ein. |
| Agentendynamik getrennt bewertet | Eigener Abschnitt `Getrennte Bewertung: Agentendynamik` bewertet A-spezifische Bedarfe. |
| Interaktionsobjektlogik getrennt bewertet | Eigener Abschnitt `Getrennte Bewertung: Interaktionsobjektlogik` bewertet B-spezifische Bedarfe. |
| Kern und Ergaenzungsmodell nicht vermischt | Unterschiedliche Modulimpulse werden als optionale Module eingeordnet, nicht direkt als Kernumbau. |
| Keine gemeinsamen Konzepte doppelt als Unterschiede gewertet | Eigener Abschnitt grenzt nicht modellrelevante Unterschiede ab. |

## Kritischer Review-Abgleich

Ein paralleler kritischer Abgleich bestaetigte die Trennung zwischen A-getriebener Agentendynamik und B-getriebener Interaktionsobjektlogik. Der Review betonte zusaetzlich, dass Task 10.2 die Unterschiede nicht nur beschreiben, sondern klassifizieren muss. Diese Klassifikation wurde im Abschnitt `Klassifikation der Unterschiede` ergaenzt.

Der Review bestaetigte ausserdem die vorsichtige Kernlinie: `Entity.kind [0..1]` und `Effect -> StateAssertion [0..*]` bleiben die einzigen minimalen Kernkandidaten. `InteractionObject`, `AssistantInteraction`, `DecisionRule`, `SpatialSemantics`, `StateTransition` und `RuntimeExecution` bleiben als optionale Module eingeordnet.

## Konsequenz

Task 10.3 kann nun gezielt entscheiden, ob `Entity` und `Agent` fuer die benoetigten Szenenobjekte ausreichen. Dabei muss die Entscheidung zweigleisig erfolgen: Fuer A geht es um Agent, Raum-Entities und beobachtbare Szenenzustaende; fuer B geht es um CoffeeMachine, Cup, BrewingRequest und Vivian als Agent/Entity.
