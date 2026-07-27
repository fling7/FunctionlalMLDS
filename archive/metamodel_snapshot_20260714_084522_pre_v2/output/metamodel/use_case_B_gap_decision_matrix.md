# Anwendungsfall B: Entscheidungsmatrix zu harten Luecken

Stand: 2026-07-07

Task: 9.4 `Entscheidung Kernanpassung oder Ergaenzungsmodell fuer B vorbereiten`

Use Case: `UC-B-01` - `Assistierte Kaffeemaschinenbedienung mit Vivian`

Bezugsdateien:

- `use_case_B_non_modelable_gaps.md`
- `use_case_B_indirect_modelability.md`
- `use_case_B_cardinality_invariant_check.md`
- `use_case_A_gap_decision_matrix.md`
- `dynamic_functional_mlds_specification.md`
- `invariants.md`

## Ziel der Entscheidung

Diese Matrix bereitet fuer jede in Task 9.3 identifizierte B-Luecke eine Modellentscheidung vor. Sie aendert das Metamodell noch nicht. Sie legt aber fest, ob eine Luecke eher in den kompakten Kern gehoert, als optionales Ergaenzungsmodell angebunden werden sollte oder fuer die aktuelle B-Baseline keinen unmittelbaren Modellbedarf erzeugt.

Die Entscheidung ist B-spezifisch. Eine endgueltige gemeinsame Entscheidung fuer A und B folgt erst nach der gemeinsamen Analyse in den spaeteren Tasks.

## Entscheidungskriterien

| Entscheidung | Kriterium | Bevorzugt, wenn |
| --- | --- | --- |
| `Kernanpassung` | Allgemeingueltig, kompakt, traceability-relevant, rueckwaertskompatibel | die Aenderung fuer fast alle Dynamic-Functional-MLDS-Modelle nuetzlich ist, nur wenige optionale Attribute oder Kanten braucht und die EAST-ADL-nahe UseCase-Semantik nicht verfaelscht |
| `Ergaenzungsmodell` | Domaenen- oder Ausfuehrungsspezifik, optional, groesserer Strukturbedarf | die Luecke nur fuer bestimmte Runtimes, Dialoge, Interaktionsobjekte, Safety, formale Tests oder ausfuehrbare Orchestrierung gebraucht wird |
| `Kein unmittelbarer Modellbedarf fuer B` | Out of Scope oder fuer B ausreichend textuell abbildbar | die Luecke nur Implementierungsdetails betrifft oder die aktuelle B-Baseline mit vorhandenen Klassen und dokumentierten Konventionen belastbar bleibt |

## Entscheidungsmatrix

| Gap-ID | Vorbereitete Entscheidung | Entscheidendes Kriterium | Risiko der Entscheidung | Auswirkung auf bestehendes Modell | Empfehlung fuer naechste Schritte |
| --- | --- | --- | --- | --- | --- |
| `B-GAP-01` | `Ergaenzungsmodell`: Interaction Object/Affordance | Bedienpunkte, Manipulationsarten, Aktivierungsbedingungen und Objektreaktionen sind zentral fuer Interaktionsobjekte, aber nicht jede `Entity` ist ein bedienbares Objekt. | Ohne Ergaenzung bleiben Starttaste, Tassenbereich und Programmauswahl nur in Expressions. Als Kernbestandteil wuerde jedes Entity-Modell mit Affordance-Semantik belastet. | Bestehende `Entity`, `Event`, `Condition`, `StateAssertion` und `Capability` bleiben gueltig. Ein optionales Modul kann an `Entity` andocken. | Fuer B hoch priorisieren: optionales Modul mit `InteractionObject`, `Affordance`, `InteractionZone`, `ControlSurface` und `ManipulationKind` vorbereiten. |
| `B-GAP-02` | `Ergaenzungsmodell`: State/Transition Semantics | Explizite StateMachines sind fuer Kaffeemaschine und `BrewingRequest` nuetzlich, aber nicht jeder UseCase braucht formale Transitionen. | Ohne Ergaenzung bleiben Zustandswechsel verteilt auf Event, Guard, Step und StateAssertion. Als Kernklasse koennte `StateTransition` einfache Szenarien stark aufblaehen. | Bestehende StateAssertions bleiben gueltig. Ein optionales Modul kann `Entity` oder `Agent` mit States, StateDimensions und Transitions verbinden. | Gemeinsam mit A-GAP-02 in Task 10/11 erneut bewerten; fuer B als wichtiges optionales State/Transition-Modul vormerken. |
| `B-GAP-03` | `Ergaenzungsmodell`: Assistant Interaction/Guidance Content | Vivian-Dialog, Guidance-Inhalt, Modalitaet und Erklaerstrategie sind assistenzspezifisch und wuerden den fachlichen Kern ueberfrachten. | Ohne Ergaenzung bleiben Vivian-Hinweise als Topics und Texte dokumentiert. Mit Kernintegration wuerde `Capability` in Richtung Dialogmodell kippen. | `Capability` bleibt fachlich. Ein Modul kann `Capability` oder `RuntimeBinding` mit GuidanceContent, DialogueAct und PresentationMode verbinden. | Optionales Vivian-/Assistant-Modul vorbereiten, aber nicht in den Kern aufnehmen. |
| `B-GAP-04` | `Ergaenzungsmodell`: Authorization/Consent, spaeter Safety-Abgleich | Benutzerbestaetigung, Ablehnung, Timeout und Gueltigkeitsdauer sind fuer assistierte Ausfuehrung wichtig, aber nicht fuer jeden SystemResponse-Schritt notwendig. | Ohne Ergaenzung bleibt Autorisierung ueber Guards und StateAssertions abgebildet. Bei Kernintegration droht Vermischung von UseCase-Ablauf, Safety und Interaktionspolitik. | Bestehende Guards `B-MAIN-G07` und `B-MAIN-G08` bleiben gueltig. Optionales Modul kann `AuthorizationState`, `Consent`, `TimeoutPolicy` und `Revocation` ergaenzen. | Fuer aktuelle B-Baseline nicht sofort umsetzen; bei Abbruch-/Timeout-Scope oder Safety-Nachweis als Ergaenzungsmodell nutzen. |
| `B-GAP-05` | `Ergaenzungsmodell`: Readiness Decision/RuleSet | Readiness ist eine zentrale fachliche Entscheidung, aber die Regeln sind objekt- und domaenenspezifisch. | Ohne Ergaenzung bleibt `ReadinessCheck` in Conditions und RuntimeActions. Als Kernbestandteil koennte eine allgemeine Entscheidungslogik den Kern mit Rule-Engine-Semantik belasten. | `Condition.expression`, `Capability.precondition` und `Effect` bleiben gueltig. Ein Modul kann geordnete Regeln, Diagnosen und Korrekturvorschlaege referenzieren. | Fuer B hoch priorisieren: optionales `DecisionRuleSet`/`ReadinessRule`-Modul an `Capability` und `Condition` anbinden. |
| `B-GAP-06` | `Ergaenzungsmodell`: Event Participation and Payload | Quelle, Ziel, Payload, Kanal und Korrelation sind fuer Eventverarbeitung wichtig, aber nicht fuer jeden fachlichen Ablauf notwendig. | Ohne Ergaenzung bleiben Eventdetails in `Event.expression`. Bei Kernintegration droht Vermischung von Actor-Rolle und Ereignisquelle als Instanz. | `Event` bleibt kompakt. Optionales Modul kann `Event.source`, `Event.target`, `payload`, `channel`, `timestamp` und `correlationId` strukturieren. | Fuer automatische Runtime-/Testkorrelation spaeter spezifizieren; fuer aktuelle B-Baseline nicht als Kernanpassung. |
| `B-GAP-07` | `Ergaenzungsmodell`: Runtime Orchestration | Reihenfolge, Dependencies, Retry, Timeout und Rollback gehoeren zur technischen Orchestrierung unterhalb von `RuntimeBinding`. | Ohne Ergaenzung bleibt Action-Reihenfolge dokumentarisch. Als Kernanpassung wuerde `RuntimeBinding` in Richtung Workflow-Engine kippen. | Bestehende RuntimeBindings und RuntimeActions bleiben gueltig. Ein optionales Modul kann ActionDependency, Order, Transaction und Recovery unter RuntimeBinding beschreiben. | Nicht in den Kern aufnehmen; bei ausfuehrbarer Toolchain als Runtime-Orchestration-Modul spezifizieren. |
| `B-GAP-08` | `Ergaenzungsmodell`: Runtime Profile and Schema Model | Plattformprofile, Adapterversionen, Schemafelder und Kompatibilitaet sind runtime- und codegenerierungsspezifisch. | Ohne Ergaenzung bleiben Runtime-Kontexte und Schemas als Tabellenwerte. Als Kernbestandteil wuerde das Metamodell stark in Richtung Implementierungs-/IDL-Modell wachsen. | `RuntimeAction.inputSchema` und `outputSchema` bleiben als optionale Attributwerte gueltig. Ein Modul kann Schemaelemente bei Bedarf formalisieren. | Bei Codegenerierung oder Toolchain-Integration als RuntimeProfile-/Schema-Ergaenzung entwerfen. |
| `B-GAP-09` | `Kernanpassung minimal` fuer `Effect -> StateAssertion`; `Ergaenzungsmodell` fuer formale ValidationOutcome-Struktur | Die Rueckbindung von Effect auf beobachtbare StateAssertions ist allgemein traceability-relevant und kompakt als optionale nicht-kompositive Kante. Formale ValidationOutcome-Logik ist groesser und testmodellspezifisch. | Ohne Kernkante bleibt der Effect-Nachweis dokumentarisch. Eine zu starke Pflichtkante koennte wiederverwendbare Capabilities zu eng an einzelne Scenarios binden. | Rueckwaertskompatibel, wenn die Kante optional bleibt. Bestehende Effects und StateAssertions bleiben gueltig. | Minimalen Kernkandidaten vormerken: `Effect.evidencedBy StateAssertion [0..*]`. ValidationOutcome-Logik nur als optionales Validation-Modul. |
| `B-GAP-10` | `Kein unmittelbarer Modellbedarf fuer B-Baseline`; spaeter `Ergaenzungsmodell`: Scenario Variation | BranchPoint, EntryPoint, ReturnPoint und RecoveryPolicy sind fuer komplexe Varianten wichtig, aber die aktuelle Alternative und Exception funktionieren bereits mit `StepRelation`. | Ohne Ergaenzung bleiben Branch-Anker textuell. Als Kernbestandteil koennte das Scenario-Modell in Richtung vollstaendiger Workflow-/Variantenmodellierung wachsen. | Bestehende `Scenario.kind` und `StepRelation.kind` bleiben gueltig. Optionales Modul kann VariationPoints und ReturnPolicies an Scenarios haengen, falls Varianten automatisch analysiert werden sollen. | Fuer aktuelle B-Baseline nicht umsetzen; bei vielen Alternativen/Exceptions als ScenarioVariation-Modul spezifizieren. |
| `B-GAP-11` | `Kein unmittelbarer Modellbedarf fuer B-Baseline`; spaeter `Ergaenzungsmodell`: Safety/Hazard Argumentation | Hazard, SafetyGoal, Risiko und ASIL/Sicherheitsklassifikation sind eigene Safety-Semantik und sollten nicht implizit in `StateAssertion` oder `Condition` versteckt werden. | Ohne Ergaenzung bleibt sicherer Nicht-Start nur fachlich validiert. Als Kernintegration wuerde das Modell Safety-Semantik aufnehmen, die nicht jeder UseCase braucht. | Bestehende Exception-StateAssertions bleiben gueltig. Safety kann optional an Requirement, Condition, StateAssertion und ValidationCase andocken. | Wenn automotive Safety explizit gefordert wird, EAST-ADL-nahe Safety-Ergaenzung entwerfen; fuer aktuelle B-Demo kein Kernumbau. |
| `B-GAP-12` | `Kein unmittelbarer Modellbedarf fuer B-Baseline`; spaeter `Ergaenzungsmodell`: Recovery/Temporal Policy | Abbruch-, Timeout- und Recovery-Pfade koennen als weitere Scenarios modelliert werden. Ein eigenes Policy-Modell ist erst bei Vollspezifikation oder Automatisierung notwendig. | Ohne Ergaenzung bleiben Policies textuell oder als zusaetzliche Scenarios. Als Kernbestandteil wuerde jeder UseCase mit Timeout-/Recovery-Semantik belastet. | Bestehende Scenario- und StepRelation-Struktur bleibt ausreichend. Weitere Pfade koennen instanziiert werden, ohne das Metamodell zu aendern. | Fuer aktuellen Scope nur dokumentieren. Bei vollstaendiger Interaktionsrobustheit optionales RecoveryPolicy-/Temporal-Modul vorbereiten. |

## Kompakte B-Empfehlung

| Kategorie | Gaps | Begruendung |
| --- | --- | --- |
| Minimaler Kernkandidat | `B-GAP-09` anteilig | `Effect -> StateAssertion` ist klein, rueckwaertskompatibel und fuer Traceability in A und B nuetzlich. |
| Optionales Ergaenzungsmodell mit hoher Prioritaet | `B-GAP-01`, `B-GAP-02`, `B-GAP-03`, `B-GAP-05` | Diese Luecken betreffen die eigentliche B-Domaene: Interaktionsobjekt, Objektzustand, Vivian-Assistenz und Readiness-Entscheidung. |
| Optionales Ergaenzungsmodell mit mittlerer Prioritaet | `B-GAP-04`, `B-GAP-06`, `B-GAP-07`, `B-GAP-08` | Relevant fuer Autorisierung, Eventverarbeitung und Runtime, aber nicht blockierend fuer die aktuelle Baseline. |
| Kein unmittelbarer Modellbedarf fuer B-Baseline | `B-GAP-10`, `B-GAP-11`, `B-GAP-12` | Variantenanalyse, SafetyCase und vollstaendige Recovery-Policy sind wichtig bei erweitertem Scope, aber die aktuelle B-Baseline bleibt mit `Scenario`, `StepRelation`, `Condition` und `StateAssertion` belastbar. |

## B-Abgleich mit A-Kernkandidaten

| A-Kandidat | B-Befund | Entscheidungstendenz |
| --- | --- | --- |
| `A-GAP-06`: optionale `Entity.kind`-Typisierung | B nutzt `Entity.kind = asset` fuer CoffeeMachine und Cup, `Entity.kind = agent` fuer Vivian sowie `Entity.kind = stateObject` fuer BrewingRequest bereits als wichtige Konvention. | B bestaetigt eine minimale Kernanpassung `Entity.kind [0..1]`, obwohl sie in B nicht als blockierende harte Luecke gefuehrt wurde. |
| `A-GAP-08`: optionale Trace-Kante `Effect -> StateAssertion` | B nutzt Effect-StateAssertion-Traces in Capability-, RuntimeAction- und ValidationCase-Artefakten intensiv. | B bestaetigt `B-GAP-09` als minimalen Kernkandidaten. |
| `A-GAP-07`: Interaction Object/Affordance | B macht diesen Bedarf deutlich staerker als A. | Nicht Kern, aber fuer B hoch priorisiertes Ergaenzungsmodell. |
| `A-GAP-02`: State/Transition Semantics | B bestaetigt den Bedarf fuer Kaffeemaschine und BrewingRequest. | Optionales gemeinsames State/Transition-Ergaenzungsmodell statt Kernumbau. |

## Vorgeschlagene Ergaenzungsmodule

| Modul | Primaere Gaps | Andockpunkte im bestehenden Modell | Zweck |
| --- | --- | --- | --- |
| `InteractionObjectModule` | `B-GAP-01` | `Entity`, `Event`, `Condition`, `Capability` | Affordances, Bedienpunkte, Interaktionszonen und erlaubte Manipulationen modellieren. |
| `StateTransitionModule` | `B-GAP-02` | `Entity`, `Agent`, `Event`, `Condition`, `StateAssertion` | Zustaende, StateDimensions und erlaubte Transitionen strukturiert erfassen. |
| `AssistantInteractionModule` | `B-GAP-03`, teilweise `B-GAP-04` | `Agent`, `Capability`, `RuntimeBinding`, `ValidationCase` | Vivian-Dialogakte, GuidanceContent, Modalitaet und Erklaerstrategien modellieren. |
| `DecisionRuleModule` | `B-GAP-05` | `Capability`, `Condition`, `Effect`, `ValidationCase` | Readiness-Regeln, Diagnosen und Korrekturvorschlaege formal abbilden. |
| `EventDetailModule` | `B-GAP-06` | `Event`, `Actor`, `Entity`, `RuntimeAction` | Eventquelle, Ziel, Payload, Kanal, Zeit und Korrelation strukturieren. |
| `RuntimeExecutionModule` | `B-GAP-07`, `B-GAP-08` | `RuntimeBinding`, `RuntimeAction` | Action-Reihenfolge, Dependencies, RuntimeProfile, Schemas und technische Fehlerregeln beschreiben. |
| `ScenarioVariationModule` | `B-GAP-10`, teilweise `B-GAP-12` | `Scenario`, `ScenarioStep`, `StepRelation` | Nur bei erweitertem Scope: BranchPoints, EntryPoints, ReturnPoints, RecoveryPolicies und VariationPoints strukturieren. |
| `SafetyArgumentModule` | `B-GAP-11` | `Requirement`, `Condition`, `StateAssertion`, `ValidationCase` | Nur bei Safety-Scope: Hazard, SafetyGoal, Mitigation und SafetyCase-Bezug optional modellieren. |
| `ValidationAssertionModule` | Anteil aus `B-GAP-09` | `ValidationCase`, `StateAssertion`, `Effect` | Komplexe ExpectedOutcomes, Negation, Temporalitaet und Testorakel formalisieren. |

## Risikoanalyse nach Modellqualitaet

| Qualitaetskriterium | Risiko | Gegenmassnahme |
| --- | --- | --- |
| Kompaktheit | Zu viele B-spezifische Klassen im Kern machen das Diagramm wieder gross und schwer lesbar. | Nur minimale Trace- und Entity-Typisierungs-Kandidaten fuer den Kern vormerken; B-Domaenenlogik modular halten. |
| EAST-ADL-Nahe | Vivian-Dialog, Affordances oder Runtime-Orchestrierung koennten die UseCase-Semantik ueberdecken. | UseCase-, Scenario-, Actor- und Satisfy-Semantik unveraendert lassen; Module nur andocken. |
| Rueckwaertskompatibilitaet | Neue Pflichtfelder koennten bestehende A- und B-Instanzen ungueltig machen. | Alle Kernkandidaten optional und nicht-kompositiv halten. |
| Fachliche/technische Trennung | Runtime-Orchestrierung koennte wieder direkte Step-zu-RuntimeAction-Kanten nahelegen. | Runtime-Module ausschliesslich unter `RuntimeBinding -> RuntimeAction` platzieren. |
| Automatisierbarkeit | Ohne Module bleiben Dialog, Affordances, Readiness und Runtime-Reihenfolge teilweise textuell. | Automatisierung gezielt ueber optionale Module statt Kernaufblaehung ermoeglichen. |
| Wissenschaftliche Nachvollziehbarkeit | Zu viele Workarounds koennten unpraezise wirken. | Jede Unschaerfe ist dokumentiert, priorisiert und mit Entscheidung versehen; keine stille Modellluecke bleibt offen. |

## Auswirkungen auf bestehende Invarianten

| Invariante | Auswirkung der B-Entscheidung |
| --- | --- |
| Genau ein Main-Scenario pro UseCase | Keine Entscheidung veraendert diese Regel. |
| Include verpflichtend, Extend optional | Keine Entscheidung veraendert die EAST-ADL-nahe UseCase-Semantik. |
| Satisfy-XOR-Regel | Keine Entscheidung veraendert die XOR-Regel. |
| Keine direkte `ScenarioStep -> RuntimeAction`-Kante | RuntimeExecutionModule bleibt unter `RuntimeBinding`; keine direkte Kante wird eingefuehrt. |
| Capability ohne technische Daten | Assistant-, Decision- und Interaction-Module duerfen fachliche Inhalte verfeinern; technische Details bleiben in RuntimeBinding/RuntimeAction. |
| Actor/Agent-Trennung | AssistantInteractionModule darf Vivian als Agent/Entity verfeinern, aber nicht automatisch zum Actor machen. |
| ParallelGroup-Mitgliedschaft | ScenarioVariationModule darf Varianten strukturieren, aber keine ParallelGroup-Regeln verletzen. |

## Kritischer Review-Abgleich

Die bewusst strenge Linie lautet: Nur `B-GAP-09` erzeugt einen echten minimalen Kernkandidaten, und selbst dort nur der Teil `Effect -> StateAssertion`. Fast alle anderen B-Luecken sind wichtig, aber fachlich oder technisch spezialisiert. Sie sollten deshalb als Ergaenzungsmodelle angebunden werden, damit das Kernmetamodell kompakt bleibt.

Eine weichere Auslegung koennte `B-GAP-01` oder `B-GAP-02` in den Kern ziehen, weil Interaktionsobjekte und Zustandsautomaten fuer B zentral sind. Diese Entscheidung wird hier nicht empfohlen: Das wuerde den Kern fuer alle UseCases mit Objekt- und StateMachine-Semantik belasten, obwohl A und einfache B-Instanzen ohne diese Strukturen gueltig bleiben.

Ein kritischer Nebenreview bestaetigte diese Linie und schaerfte drei Punkte:

- Hohe B-Prioritaet bedeutet nicht automatisch Kernreife. `B-GAP-01`, `B-GAP-02`, `B-GAP-03` und `B-GAP-05` bestaetigen vor allem den Modulbedarf.
- `B-GAP-09` muss gesplittet bleiben: Nur `Effect -> StateAssertion` ist Kernkandidat; formale ValidationOutcome-Logik bleibt ein Validation-Ergaenzungsmodell.
- `B-GAP-04` und `B-GAP-12` ueberlappen bei Bestaetigung, Ablehnung, Timeout und Recovery. Einfache Faelle bleiben `Condition`, `Event` und `Scenario`; formale Policies gehoeren spaeter in ein optionales Modul.

## Abnahmekontrolle

| Kriterium aus Task 9.4 | Erfuellung |
| --- | --- |
| Entscheidungsmatrix vorhanden | Die Tabelle `Entscheidungsmatrix` bewertet `B-GAP-01` bis `B-GAP-12`. |
| Jede Luecke hat Entscheidung | Jede Gap-Zeile enthaelt `Kernanpassung`, `Ergaenzungsmodell` oder `Kein unmittelbarer Modellbedarf`. |
| Jede Entscheidung hat fachliche Begruendung | Spalte `Entscheidendes Kriterium` nennt das ausschlaggebende Kriterium. |
| Jede Entscheidung nennt Risiko | Spalte `Risiko der Entscheidung` benennt das Hauptrisiko. |
| Jede Entscheidung nennt Auswirkung auf bestehendes Modell | Spalte `Auswirkung auf bestehendes Modell` beschreibt Rueckwaertskompatibilitaet und Andockpunkte. |
| Auswirkungen auf Modellinvarianten bewertet | Eigener Abschnitt beschreibt, dass zentrale Invarianten erhalten bleiben. |
| Keine sofortige Metamodell-Aenderung | Die Datei bereitet Aenderungen vor, setzt sie aber nicht in Diagramm, Spezifikation oder Generator um. |

## Konsequenz fuer Task 10.1

Task 10.1 kann nun die Gemeinsamkeiten von A und B extrahieren. Besonders relevant sind:

- `Entity.kind` als gemeinsamer minimaler Kernkandidat,
- `Effect -> StateAssertion` als gemeinsamer minimaler Trace-Kandidat,
- State/Transition-Semantik als gemeinsames Ergaenzungsmodell,
- Runtime-Orchestration als gemeinsames technisches Ergaenzungsmodell,
- Interaktionsobjekt-/Affordance- und Assistant-Interaction-Module als B-staerkere, aber anschlussfaehige Erweiterungen.
