# Dynamic Functional MLDS - V2-Umsetzung und abgeschlossene Taskliste

Stand: 2026-07-14  
Status: **Abgeschlossen** – Modellrelease `2.0.0-model`; 64/64 Tasks nachgewiesen. Das Metamodell v0.5 und die bestehende Implementierung blieben unverändert.

## 1. Auftrag und Abgrenzung

Diese Arbeitsliste dokumentiert die umgesetzte zweite Modellfassung, die sich formal enger an EAST-ADL V2.1.12 hält. Gegenstand waren ausschließlich das neue Metamodell V2, seine verlustfreie v0.5-Kompatibilitätssicht sowie Modell-, Diagramm- und Abnahmenachweise.

Im Auftrag ausdrücklich nicht enthalten und deshalb unverändert geblieben:

- Änderungen an Unity, Backend, Pipeline, JSON-Schemas oder bestehenden Instanzen,
- eine Migration vorhandener Projekte oder eine Umstellung des v0.5-Runtime-Vertrags,
- eine Umdeutung oder Entfernung bereits nutzbarer Modellfähigkeiten.

## 2. Gesicherter Ausgangsstand

| Gegenstand | Ergebnis |
| --- | --- |
| Aktuelle Modellfassung | Dynamic Functional MLDS v0.5 |
| Kanonische Quelle | `tools/generate_dynamic_functional_mlds.py` |
| Generierte Hauptartefakte | `output/metamodel/dynamic_functional_mlds_metamodel.{png,svg,mmd}` und `dynamic_functional_mlds_specification.md` |
| Pre-V2-Snapshot | `archive/metamodel_snapshot_20260714_084522_pre_v2/` |
| ZIP | `archive/metamodel_snapshot_20260714_084522_pre_v2.zip` |
| Prüfsumme/Manifest | `archive/metamodel_snapshot_20260714_084522_pre_v2/manifest.sha256.csv` |
| Sicherungsumfang | 132 Dateien: vollständiges `output/metamodel/**` plus Generator |
| Verifikation | Alle 132 Quelldateien und Kopien per SHA-256 abgeglichen; ZIP enthält 133 Einträge einschließlich Manifest |
| Git-Ausgangslage | Branch `master`, noch kein Commit; alle Projektordner unversioniert. Deshalb wurde bewusst das vorhandene Snapshot-Muster statt eines breiten Erst-Commits verwendet. |

Geprüfte Quellen:

- EAST-ADL-Spezifikation V2.1.12, SHA-256 `6B1645C4FA668DBFA8AF24C37B83BC0B7343B9B6284E1DD29E1085B10BC59C3D`
- Prüfergebnis/Kritik, SHA-256 `9E33878E44C4C2B89555C222E976F91E11132A68CE1FD3FF7DF83340D3F9FAFA`

## 3. Nichtregressionsvertrag für die Modellfassung V2

V2 darf die Semantik anders und EAST-ADL-konformer ordnen, muss aber jede heute abbildbare Information verlustfrei weiter ausdrücken können. Insbesondere bleiben erhalten:

1. Requirements und Use Cases mit `Satisfy`, `Include`, `Extend` und `ExtensionPoint`.
2. Main-, Alternativ- und Exception-Szenarien mit Schritten, Triggern, Guards, Zustandsaussagen, lokalen Verzweigungen und Parallelgruppen.
3. Die Trennung zwischen Actor-Rolle, konkreter Entity und Agent.
4. Die fachlich-technische Kette `ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`.
5. Mindestens ein beobachtbarer `Effect` je Capability und dessen Evidenz durch `StateAssertion`.
6. Mehrere RuntimeBindings je Capability und mindestens eine RuntimeAction je Binding.
7. ValidationCases mit Stimuli, erwarteten Ergebnissen, Requirement-Trace und prüfbaren RuntimeBindings.
8. Die Invariante, dass ScenarioSteps keine direkte RuntimeAction-Referenz besitzen.
9. Agenten-Grounding, Raumwissen, Antwort-Capability und Agent-Handoff, wie sie die bestehende Pipeline erzeugt.
10. Bestehende v0.5-Instanzen müssen durch eine dokumentierte V2-Kompatibilitätssicht verlustfrei repräsentierbar bleiben.

### Derzeit von der Unity-/Backend-Kette erwartete v0.5-Sicht

Diese Namen werden in V2 nicht vorschnell als fachliche Klassennamen festgeschrieben. Sie bilden aber einen verbindlichen Serialisierungs-/Kompatibilitätsvertrag:

- Top-Level: `metamodelVersion`, `requirementsModel`, `actors`, `entities`, `agents`, `events`, `conditions`, `stateAssertions`, `capabilityUses`, `capabilities`, `runtimeBindings`, `validationCases`, `satisfyRelationships`.
- Use Case/Scenario: `useCases`, `scenarios`, `steps`, `stepRelations`, `parallelGroups`.
- ScenarioStep: `stepNumber`, `performedBy`, `triggeredBy`, `guard`, `resultingState`, `capabilityUseIds`.
- CapabilityUse/Capability: `capability_id`, `parameters`, `effects`, `evidencedBy`.
- RuntimeBinding/RuntimeAction: `runtimeActions`, `endpoint`, `tool`, `topic`, `inputSchema`, `outputSchema`.
- Validation: `level`, `stimulus_ids`, `runtime_binding_ids`, `expectedOutcome`, `verifies_requirement_ids`, `validates_use_case_ids`.
- Runtime-Trace: `scenario_step_id`, `capability_use_ids`, `capability_id`, `runtime_binding_id`, `runtime_action_id`.

Besonders migrationssensitiv sind `Event`/`Condition`, `performedBy`, die Schrittfolge, Capability-Type/Use, RuntimeAction-Locator und die V&V-Struktur. Für diese Elemente ist im Modell eine explizite v0.5-Projektion Pflicht, bevor eine neue Serialisierung erwogen wird.

## 4. Konsolidierte Kritikliste

### A. Übernommener EAST-ADL-Ausschnitt

| ID | Kritik am aktuellen Stand | EAST-ADL-Bezug | Priorität |
| --- | --- | --- | --- |
| K-01 | Die Überschrift "unverfälschter Kern" ist falsch. Gezeigt wird ein legitimer, aber verkürzter Ausschnitt. | RequirementsModel, §11.2.9, S. 97 | P0 |
| K-02 | Generalisierungen werden im Hauptdiagramm überwiegend nur durch Stereotype angedeutet oder fehlen. Ein Stereotyp ersetzt keine UML-Generalisation. | `Context`, `EAElement`, `Relationship`, `TraceableSpecification`, §§25.2.2-25.2.16, S. 189-195 | P0 |
| K-03 | `Requirement.text` und `UseCase.text` erscheinen lokal und verpflichtend, obwohl `text: String [0..1]` von `TraceableSpecification` geerbt wird. | Requirement §11.2.6, S. 94-95; UseCase §12.2.6, S. 103; TraceableSpecification §25.2.16, S. 195 | P0 |
| K-04 | Bei Requirement fehlen im verwendeten Ausschnitt die relevanten Eigenschaften `formalism [0..1]`, `url [0..1]` und `mode [*]`, oder es fehlt eine klare Notiz, dass sie ausgelassen wurden. | §11.2.6, S. 95 | P0 |
| K-05 | Die Texte "usage of a system" und "captures required functionality" werden wie UseCase-Attribute dargestellt, sind aber Beschreibung/Note. | §12.2.6, S. 103 | P0 |
| K-06 | `ExtensionPoint.name` ist geerbt und optional; "belongs to extended UseCase" folgt aus der Komposition und ist kein Attribut. | §12.2.3, S. 102; EAElement S. 190 | P0 |
| K-07 | `Extend.condition` gehört nicht zur EAST-ADL-Metaklasse Extend. Die bedingte Ausdrucksfähigkeit darf dennoch nicht verloren gehen. | Extend §12.2.2, S. 101-102 | P0 |
| K-08 | Die direkte Actor-UseCase-Kante ist eine DFMLDS-Erweiterung, wird aber optisch dem EAST-ADL-Kern zugerechnet. | Actor §12.2.1, S. 101; UseCase-Diagramm S. 100 | P0 |
| K-09 | Bei `Satisfy` fehlt die EAST-ADL-Invariante, dass `satisfiedBy` kein Requirement/RequirementContainer sein darf. Enden und Requirement/UseCase-XOR sind dagegen richtig und bleiben erhalten. | Satisfy §11.2.12, S. 98 | P0 |

### B. Konservative Erweiterungsstruktur

| ID | Kritik am aktuellen Stand | EAST-ADL-Bezug | Priorität |
| --- | --- | --- | --- |
| K-10 | `UseCase -> Scenario [1..*]` verändert die Gültigkeit jedes EAST-ADL-UseCases. Der Kern muss `[0..*]` erlauben; die strengere Regel gehört in ein DFMLDS-Ausführungsprofil. | UseCase §12.2.6, S. 103; Konservativitätsforderung der Kritik | P0 |
| K-11 | Ein Root-Container für die neuen Elemente fehlt. Dadurch sind Besitz von Scenario, Entity, Capability, RuntimeBinding und ValidationCase sowie Relationship-Kontext unklar. | Context §25.2.2, S. 189 | P0 |
| K-12 | Neue DFMLDS-Klassen besitzen nicht durchgängig formale EAST-ADL-Infrastruktur-Generalisationen. Dadurch sind Traceability, UUID/shortName und Relationship-Ziele teilweise nur behauptet. | §§25.2.2-25.2.16, S. 189-195 | P0 |
| K-13 | Die Paketabhängigkeit muss einseitig bleiben: DFMLDS darf EAST-ADL verwenden; EAST-ADL-Klassen dürfen nicht durch neue Pflichtmerkmale verändert werden. | EAST-ADL-Paketstruktur und konservative Erweiterungsregel | P0 |

### C. Szenario- und Ablaufmodell

| ID | Kritik am aktuellen Stand | EAST-ADL-Bezug | Priorität |
| --- | --- | --- | --- |
| K-14 | `performedBy: Actor` vermischt externe Rolle und konkrete ausführende Entity. Systemantworten können so nicht sauber zugeordnet werden. | Actor §12.2.1, S. 101 | P0 |
| K-15 | Listenreihenfolge, `stepNumber` und `StepRelation.sequence` sind drei konkurrierende Quellen der Ablaufsemantik. | DFMLDS-interne Konsistenz; Annex C `LogicalPath.segment`, S. 226-227 | P0 |
| K-16 | `ParallelGroup` und `fork/join` überschneiden sich ohne klare Rollen oder Konsistenzinvariante. | Annex C `LogicalPath.strand`, S. 226-227 | P0 |
| K-17 | `Scenario.kind` und `StepRelation.kind` verwenden beide alternative/exception, ohne vollständige Variante und lokale Verzweigung eindeutig zu unterscheiden. | DFMLDS-interne Konsistenz | P0 |
| K-18 | Alternative/Exception-Szenarien besitzen keine formale Referenz auf ihr Main-Szenario. | DFMLDS-Erweiterung; aus der Kritik abgeleitete Invariante | P1 |
| K-19 | Der Name `Event` kollidiert mit dem abstrakten EAST-ADL `Timing::Event`; die DFMLDS-Bedeutung ist nicht formal angebunden. | Timing::Event §14.2.1, S. 113; ExternalEvent §16.2.8, S. 139 | P0 |
| K-20 | `Condition.expression: String` bleibt untypisiert, obwohl EAST-ADL `EAExpression` Modellreferenzen und Typisierung unterstützt. | EAExpression §24.2.5, S. 185 | P0 |
| K-21 | `[0..1]` hinter Float wird als UML-Kardinalität gelesen, nicht als Zahlenintervall 0 bis 1. | EANumerical §23.2.6, S. 178-179 | P0 |

### D. Entity, Capability und Runtime

| ID | Kritik am aktuellen Stand | EAST-ADL-Bezug | Priorität |
| --- | --- | --- | --- |
| K-22 | `Agent` als Subklasse und `EntityKind.agent` sind redundant. Da Unity `kind=agent` derzeit nutzt, darf der Wert nicht einfach entfallen; erforderlich ist eine Äquivalenzinvariante. | DFMLDS-interne Konsistenz und Unity-Vertrag | P0 |
| K-23 | `playsActor` ist nur an Agent gebunden, obwohl EAST-ADL-Actor-Rollen auch von Menschen, Hardware oder anderen Systemen gespielt werden können. | Actor §12.2.1, S. 101 | P1 |
| K-24 | `Capability`/`CapabilityUse` nutzen das EAST-ADL-Type-Prototype-Muster nicht formal. | EAType/EAPrototype, S. 191; FunctionType/FunctionPrototype §§6.2.18-6.2.19, S. 50-51 | P1 |
| K-25 | `FunctionBehavior` ist falsch verkürzt: `path` und `representation` sind verpflichtend; `function` und `mode` fehlen. | FunctionBehavior §9.2.2, S. 69-70 | P0 |
| K-26 | `Capability refines FunctionBehavior` ist keine gültige EAST-ADL-Refine-Semantik, weil `Refine` einen Requirement-Supplier verlangt. | Refine §11.2.5, S. 94 | P0 |
| K-27 | `RuntimeAction` verwendet die informelle Notation `endpoint | tool | topic`; XOR/Locator-Semantik und Reihenfolge mehrerer Aktionen sind unklar. | DFMLDS-Erweiterung | P0 |
| K-28 | Das Parameter-Mapping zwischen CapabilityUse und RuntimeAction-Eingaben/-Ausgaben fehlt. | EAST-ADL-Datatype-/Prototype-Muster; DFMLDS-Erweiterung | P1 |
| K-29 | Verwendete Typen `RandomVariable`, `KeyValue`, `Schema` und teilweise `EntityKind` sind im Hauptdiagramm nicht vollständig definiert. | EADatatype/EADatatypePrototype, S. 178; DFMLDS-Erweiterung | P0 |
| K-30 | Wahrnehmung, Wissen, Quelle und Änderungsrecht eines Agenten sind trotz vorhandener Agentenhandlungen nicht modellierbar. | Optionale DFMLDS-Erweiterung | P2 |

### E. Behavior, Functional Architecture und V&V

| ID | Kritik am aktuellen Stand | EAST-ADL-Bezug | Priorität |
| --- | --- | --- | --- |
| K-31 | Die Scenario-Schicht wird nicht explizit auf Annex C abgebildet und kann dadurch wie eine unbeabsichtigte Duplizierung wirken. Annex C ist allerdings vorläufig und noch nicht Teil des validierten Basiskerns. | Annex C, S. 212-236 | P1 |
| K-32 | `ValidationCase` bildet die EAST-ADL-Struktur aus VVCase, VVProcedure, VVStimuli, VVIntendedOutcome, VVActualOutcome, VVTarget und Verify nicht ab. | VerificationValidation §§13.2.1-13.2.9, S. 106-111 | P0 |
| K-33 | `level: abstract|concrete` dupliziert die EAST-ADL-Verknüpfung `abstractVVCase [0..1]`; `checks RuntimeBinding` sollte über `vvSubject`/VVTarget modelliert werden. | VVCase §13.2.4, S. 107-108 | P0 |
| K-34 | Die aktuelle Bridge nennt FunctionBehavior, verortet Capabilities aber nicht sauber gegenüber Analysis-/Design-Funktionsarchitektur. | SystemModeling §§3.2.1-3.2.2, S. 20-22; FunctionModeling S. 40-51 | P1 |

## 5. EAST-ADL-Präzisierungen, die bei der Umsetzung bindend sind

1. FAA und FDA sind keine Metaklassen. `AnalysisLevel.functionalAnalysisArchitecture` zeigt auf einen `AnalysisFunctionPrototype [0..1]`, der durch `AnalysisFunctionType` typisiert ist. Analog gilt dies für `DesignFunctionPrototype`/`DesignFunctionType` auf dem DesignLevel (§§3.2.1-3.2.2, S. 20-22).
2. Eine breite DFMLDS-Capability darf daher nicht ungeprüft in eine Analysis- oder DesignFunction umbenannt werden. Sie bleibt domänenübergreifend und erhält bei Bedarf eine optionale Mapping-Beziehung zu den exakten EAST-ADL-Typen/Prototypen.
3. FunctionType besitzt Ports und Connectoren; konkrete Analysis-/DesignFunctionTypes besitzen Parts. `FunctionConnector` verbindet genau zwei FunctionPorts über `port: FunctionPort [2]` und benötigt den konkreten Prototype-/Instanzpfad (§§6.2.14-6.2.19, S. 47-51). `StepRelation` und `RuntimeBinding` dürfen nicht als FunctionConnector umgedeutet werden.
4. FunctionBehavior hat synchrone Run-to-completion-Semantik (S. 70). Dauerhafte Dialoge, Animationen und offene VR-Prozesse werden deshalb nur optional angebunden.
5. VehicleFeature ist fahrzeugspezifisch und darf den domänenübergreifenden Kern nicht verpflichtend machen (§5, S. 35-39). Eine Feature-Abbildung bleibt optional.

## 6. Priorisierte Taskliste für die Modelländerung

### Phase 0 - Basis und Entscheidungen

- [x] **V2-00 - v0.5 sichern.** Vollständigen, hash-geprüften Pre-V2-Snapshot mit Generator und Modellartefakten erstellen.
- [x] **V2-01 - Bestand und Kritik inventarisieren.** Diagramm, Spezifikation, Generator, Kritikdatei, EAST-ADL-PDF und Unity-/Backend-Vertrag abgleichen.
- [x] **V2-02 - V2-Namensraum und Versionsregel festlegen.** Arbeitsbezeichnung `DFMLDS::V2`; endgültige semantische Versionsnummer erst nach Modellabnahme. Keine Änderung der v0.5-Instanzkennung in dieser Phase.
- [x] **V2-03 - Kompatibilitätssicht spezifizieren.** Tabelle `v0.5-Feld -> V2-Element/Rolle` für alle in Abschnitt 3 genannten Felder definieren. Abnahme: jede bestehende v0.5-Information besitzt genau eine verlustfreie V2-Abbildung.

### Phase 1 - EAST-ADL-Ausschnitt unverändert und formal korrekt darstellen

- [x] **V2-10 - Ausschnitt korrekt benennen.** Titel in "EAST-ADL Requirements/UseCases - verwendeter Ausschnitt" ändern.
- [x] **V2-11 - Infrastruktur-Generalisationen einzeichnen.** Mindestens `RequirementsModel -> Context`, `Requirement/Actor/UseCase -> TraceableSpecification`, `ExtensionPoint -> RedefinableElement`, `Include/Extend -> Relationship`, `Satisfy -> RequirementsRelationship` in allen Diagrammformaten darstellen.
- [x] **V2-12 - Geerbte Eigenschaften bereinigen.** Lokale Pflichtattribute `Requirement.text`, `UseCase.text` und `ExtensionPoint.name` entfernen oder eindeutig als geerbt `[0..1]` kennzeichnen; Beschreibungen als Notes darstellen.
- [x] **V2-13 - Requirement-Ausschnitt vervollständigen.** `formalism`, `url`, `mode` darstellen oder einen sichtbaren, präzisen Auslassungshinweis ergänzen.
- [x] **V2-14 - Extend korrigieren.** EAST-ADL-`Extend` selbst ohne `condition` darstellen. Zur Fähigkeitserhaltung `DFMLDS::ConditionalExtend -> EAST-ADL::Extend` mit `condition: ScenarioCondition [1]` modellieren. Dadurch bleibt die Spezialisierung in `UseCase.extend: Extend [*]` zulässig, ohne lokale Scenario-Guards mit einer UseCase-Erweiterungsbedingung zu vermischen.
- [x] **V2-15 - ActorParticipation auslagern.** Die direkte Actor-UseCase-Kante durch eine sichtbar DFMLDS-eigene `ActorParticipation -> Relationship` ersetzen.
- [x] **V2-16 - Satisfy vervollständigen.** Bestehende Enden und XOR erhalten; zusätzlich den Ausschluss von Requirement/RequirementContainer bei `satisfiedBy` notieren.

### Phase 2 - Konservativer DFMLDS-Container und Infrastruktur

- [x] **V2-20 - Root-Container einführen.** Genau einen `DynamicFunctionalModel -> Context` modellieren. Er besitzt Szenarien, Entities, Capabilities, RuntimeBindings und die DFMLDS-Relationships sowie genau einen `VerificationValidation`-Container. ValidationCases werden ausschließlich von diesem Container komposit besessen; keine doppelte Kompositionsownership und kein paralleler zweiter `ScenarioModel`.
- [x] **V2-21 - Erweiterungsklassen formalisieren.** Für jede DFMLDS-Klasse eine begründete Infrastruktur-Generalisation festlegen. Weil `EAType`, `EAPrototype`, `EAPort` und `EAConnector` selbst nicht Identifiable sind, generalisiert `Capability` zusätzlich `TraceableSpecification` und `CapabilityUse` zusätzlich `EAElement`. Abnahme: jedes referenzierbare Ziel ist tatsächlich Identifiable, ohne die EAST-ADL-Infrastruktur umzudeuten.
- [x] **V2-22 - Paketabhängigkeit dokumentieren.** Ausschließlich `DFMLDS -> EAST-ADL`; keine neue Pflichtassoziation oder Eigenschaft auf einer EAST-ADL-Metaklasse.
- [x] **V2-23 - UseCase-Szenario konservativ anbinden.** EAST-ADL-UseCase unverändert lassen und eine DFMLDS-eigene `UseCaseScenarioSpecification -> Relationship` modellieren. Kernmultiplikität `0..*`; das ausführbare DFMLDS-Profil fordert genau ein Main-Szenario. Die bestehende verschachtelte v0.5-JSON-Sicht bleibt eine Projektion.

### Phase 3 - Eindeutige Szenariosemantik

- [x] **V2-30 - Actor-Rolle und Ausführer trennen.** `performedBy: Entity [0..*]` und `actorRole: Actor [0..*]` modellieren. v0.5-`performedBy` wird als Actor-Rollen-Projektion dokumentiert, bis eine neue Serialisierung existiert.
- [x] **V2-31 - Entity-Rollenspiel verallgemeinern.** `Entity.playsActor [0..*]`; Agent erbt diese Fähigkeit.
- [x] **V2-32 - Schrittfolge kanonisieren.** `StepRelation` ist in V2 die einzige semantische Kontrollflussquelle; `/stepNumber` ist lediglich Anzeige. Beim v0.5-Import werden vorhandene StepRelations nicht aus der Listenposition überschrieben. Ursprüngliche Arrayreihenfolge und rohe `stepNumber`-Werte bleiben im `V05ProjectionLedger` erhalten, damit auch nicht rekonstruierbare Altwerte exakt zurückprojiziert werden. Keine Unity-Änderung.
- [x] **V2-33 - Parallelität konsistent machen.** `fork/join` beschreibt Kontrollfluss; `ParallelGroup` bleibt wegen bestehender Modellierbarkeit als strukturelle Gruppierung erhalten und muss vollständig zwischen passendem Fork und Join erreichbar sein. Alternativ darf es als abgeleitete Sicht gekennzeichnet werden, aber nicht ersatzlos entfallen.
- [x] **V2-34 - Variantenbezug ergänzen.** `variantOf: Scenario [0..1]`; höchstens ein Main-Szenario je ausführbarem UseCase, jede Alternative/Exception verweist genau auf Main, Main besitzt kein `variantOf`.
- [x] **V2-35 - Variantenebenen definieren.** `Scenario.kind` = vollständiger Ablauf; `StepRelation.kind` = lokale Verzweigung.
- [x] **V2-36 - Event formal anbinden.** In `DFMLDS::ScenarioEvent` umbenennen und auf `Timing::Event` aufbauen. Externe User-/Umwelt-/Raumereignisse erhalten eine präzise `ExternalEvent`-Spezialisierung oder -Abbildung. Der v0.5-Containername `events` bleibt in der Kompatibilitätssicht.
- [x] **V2-37 - Condition typisieren.** `ScenarioCondition -> EAElement + EAExpression`; `ConditionKind = guard|precondition|postcondition|spatial|timing`; `EAValue.type` muss ein `EABoolean` sein. Der Legacy-String wird auf den Mixed-String-Inhalt von `EAExpression` abgebildet. Wert- und Zeitbedingungen dürfen nur unter den Annex-C-Vorbedingungen optional auf `Quantification` bzw. `LogicalTimeCondition` abgebildet werden.
- [x] **V2-38 - Probability definieren.** Den Datentyp `Probability -> EANumerical` mit `min=0`, `max=1` vom konkreten `EANumericalValue` trennen. `ScenarioStep.occurrenceProbability` und `StepRelation.probability` sind optionale Werte, deren `type` auf `Probability` zeigt; Property-Multiplizität und Wertebereich bleiben getrennt.

### Phase 4 - Entity-, Capability- und Runtime-Bridge

- [x] **V2-40 - Agent-Discriminator konsistent halten.** Wegen bestehender Unity-Verwendung `EntityKind.agent` zunächst behalten und Invariante `Entity.kind=agent iff Entity is Agent` ergänzen.
- [x] **V2-41 - Capability-Type/Use formal modellieren.** `Capability -> EAType` und bei Bedarf zusätzlich `TraceableSpecification`; `CapabilityUse -> EAElement + EAPrototype` mit `type: Capability [1] <<isOfType>>`. Die fachliche Fähigkeit und alle bestehenden Parameter/Effects bleiben erhalten.
- [x] **V2-42 - EAST-ADL-Funktionsmapping ergänzen.** Optionale Relationship von Capability/CapabilityUse auf die exakten AnalysisFunctionType/-Prototype- oder DesignFunctionType/-Prototype-Elemente. Keine Gleichsetzung und keine erfundene FAA/FDA-Metaklasse.
- [x] **V2-43 - FunctionBehavior exakt darstellen.** `FunctionBehavior -> Context`, `path: String [1]`, `representation: FunctionBehaviorKind [1]`, `function: FunctionType [0..1]`, `mode: Mode [*]`.
- [x] **V2-44 - CapabilityBehaviorBinding einführen.** Ungültige Refine-Kante durch `CapabilityBehaviorBinding -> Relationship` ersetzen. Binding bleibt optional und dokumentiert die Run-to-completion-Voraussetzung.
- [x] **V2-45 - Fehlende Typen definieren.** `RandomVariable`, `SchemaReference`, `EntityKind` und alle Enumerationen formal definieren. Ein Parameter-Key wird als typisiertes `EADatatypePrototype` modelliert; sein konkreter Inhalt bleibt ein separates `EAValue`. Das Type/Prototype-Muster ersetzt daher nicht stillschweigend die Key-Value-Semantik.
- [x] **V2-46 - RuntimeAction formal definieren.** `locatorKind` plus `locator` oder strukturierte `RuntimeActionLocator` verwenden. Bestehende `endpoint/tool/topic`-Felder als verlustfreie, abgeleitete v0.5-Projektion festlegen; genau ein Locator muss gültig sein.
- [x] **V2-47 - RuntimeAction-Reihenfolge festlegen.** Mindestens `runtimeAction [1..*] {ordered}`. Komplexere parallele/alternative/kompensierende Abläufe nur ergänzen, wenn sie nicht mit Scenario-Control-Flow vermischt werden.
- [x] **V2-48 - ParameterBinding ergänzen.** CapabilityUse-Parameter, Runtime-Inputs/-Outputs und optionale Transformation formal verbinden.
- [x] **V2-49 - AgentKnowledgeBinding als optionales Modul entwerfen.** Wahrnehmen, Wissen, Erklären, Ändern und Quellenbezug modellieren, ohne den Core oder bestehende Agenteninstanzen zu verpflichten.

### Phase 5 - EAST-ADL-konforme V&V-Struktur

- [x] **V2-50 - ValidationCase spezialisieren.** `ValidationCase -> VVCase`.
- [x] **V2-51 - Laufzeit-V&V-Elemente ergänzen.** `RuntimeValidationProcedure -> VVProcedure`, `RuntimeStimulus -> VVStimuli`, `StateAssertionOutcome -> VVIntendedOutcome`, `RuntimeValidationLog -> VVLog`, `RuntimeActualOutcome -> VVActualOutcome` und `RuntimeValidationTarget -> VVTarget`. ActualOutcomes werden ausschließlich unter einem VVLog besessen.
- [x] **V2-52 - Abstract/Concrete korrekt abbilden.** Im Core kein eigenes autoritatives `level` führen; `abstractVVCase [0..1]` und die EAST-ADL-Constraints exakt übernehmen. Da daraus der Legacy-Wert nicht in allen Fällen eindeutig ableitbar ist, bleibt v0.5-`level` als expliziter Kompatibilitätsdiscriminator im `V05ProjectionLedger` erhalten; keine künstlichen abstrakten Cases erzeugen.
- [x] **V2-53 - Runtime-Prüfrollen trennen.** `VVCase.vvSubject` bezeichnet das Prüfobjekt; `RuntimeValidationTarget.element` bezeichnet von der Testumgebung realisierte Elemente. Eine RuntimeBinding darf in beiden Rollen vorkommen, aber es gilt keine allgemeine Gleichheitsinvariante. `runtime_binding_ids` werden über den Kompatibilitätsledger exakt erhalten.
- [x] **V2-54 - Requirement-Verifikation verwenden.** EAST-ADL-`Verify` mit `verifiedRequirement [1..*]`, `verifiedByCase [1..*]` und optionalen Procedures einsetzen. Die Legacy-UseCase-Validierung bleibt separat über `ValidationCaseUseCaseBinding -> Relationship` erhalten, weil `Verify` keine UseCases verifiziert.
- [x] **V2-55 - Wiederverwendbare StateAssertion erhalten.** `StateAssertion` bleibt als konkrete, v0.5-kompatible Spezialisierung der abstrakten `Assertion` erhalten. `StateAssertionOutcome -> AssertionOutcome -> VVIntendedOutcome` referenziert allgemeine Assertions, ohne die Assertions selbst in Outcomes umzudeuten.

### Phase 6 - Annex-C- und Feature-Abbildung

- [x] **V2-60 - Präzise optionale Mapping-Tabelle erstellen.** Ein ScenarioStep wird bevorzugt als `TransformationOccurrence` mit genau einer `LogicalTransformation` abgebildet; Sequenz und Parallelität erzeugen Step-Pfade, die in einem Parent-`LogicalPath` als geordnete `segment`- bzw. parallele `strand`-Referenzen erscheinen. `TransitionEvent` ist kein Untertyp von `Timing::Event`, sondern referenziert aufgetretene Events. Quantification erfordert Attribute-Operands; StateAssertion wird kontextabhängig auf State, Quantification oder VVIntendedOutcome abgebildet. `BehaviorConstraintType` muss zusätzlich ein zulässiges EAST-ADL-Zielelement betreffen und darf nicht allein an Capability hängen.
- [x] **V2-61 - Annex-C-Status kennzeichnen.** Das Mapping ist optional/semantisch, weil Annex C in V2.1.12 ausdrücklich vorläufig und noch nicht für den Basiskern validiert ist.
- [x] **V2-62 - Feature-Mapping prüfen.** Optionales Mapping auf `Feature`/`VehicleFeature` nur für passende automotive Profile; keine VehicleFeature-Pflicht im domänenübergreifenden Core.

### Phase 7 - Konsistenz, Darstellung und Modellabnahme

- [x] **V2-70 - Eine kanonische Modellquelle herstellen.** PNG, SVG, Mermaid und Spezifikation müssen aus derselben Modellbeschreibung entstehen; keine Generalisation darf nur in einem Ausgabeformat vorkommen.
- [x] **V2-71 - Kardinalitäten und Invarianten synchronisieren.** Diagramm, Spezifikation, Tabellen und Beispiele gegen eine einzige Invariantenliste prüfen.
- [x] **V2-72 - v0.5-V2-Abbildung an realen Instanzen prüfen.** Vorhandene Case-Study-/Wizard-Instanzen modellseitig auf V2 abbilden und zurückprojizieren; keine Information darf verloren gehen. Dabei bleiben Implementierungsdateien unverändert.
- [x] **V2-73 - Nichtregressionsmatrix abnehmen.** Alle zehn Punkte aus Abschnitt 3 sowie Answer-/Handoff-Capabilities, `POST /chat`, Trace-Map und ValidationCase-Ausdrucksfähigkeit als erhalten markieren.
- [x] **V2-74 - Visuelle Prüfung.** Gerenderte Diagramme auf Lesbarkeit, fehlende Pfeile, falsche Stereotype, Kantenüberlagerungen und Legende prüfen.
- [x] **V2-75 - Modellreview gegen EAST-ADL-Seitenbezüge.** Jeden übernommenen EAST-ADL-Namen, jede Generalisation, Multiplizität und Semantik mit den oben genannten Abschnitten abgleichen.

### Phase 8 - Präsentationsfähige Gesamt- und Detailsichten

- [x] **V2-76 - Eine zentrale A/B/C-Gesamtansicht bereitstellen.** Das kompakte Metamodell wird wieder als ein zusammenhängendes Diagramm mit Requirements/UseCases, Scenario Layer und Capability/Runtime/V&V gezeigt.
- [x] **V2-77 - Pfeilführung geometrisch abnehmen.** Alle acht Sichten müssen 0 diagonale Segmente, 0 Kartendurchläufe, 0 echte Kreuzungen, 0 Linienüberlagerungen und 0 Kantenlabel/Karten-Überdeckungen erreichen.
- [x] **V2-78 - Detailsichten als Ergänzung kennzeichnen.** Die sieben Fachsichten ergänzen die zentrale Darstellung; nicht eingezeichnete lokale Beziehungen bleiben vollständig und exakt im Beziehungsnachweis jeder Sicht erhalten.
- [x] **V2-79 - Dichte Fachsichten neu gliedern.** Scenario Flow, Capability/Runtime, V&V und optionale Module erhalten getrennte Panels und orthogonale Beziehungskorridore.
- [x] **V2-80 - PNG, SVG und Mermaid konsistent finalisieren.** Acht Sichten in allen drei Formaten erzeugen, visuell prüfen und reproduzierbar abnehmen.

### Phase 9 - Prä-v1.0-Review und Assertion-/Runtime-Präzisierung

- [x] **V2-81 - Review gegen EAST-ADL verifizieren.** Geerbte Eigenschaften von Requirement, UseCase und ExtensionPoint, beide Satisfy-Regeln, echte Generalisierungen, ExternalEvent sowie die exakten Root-Container gegen EAST-ADL V2.1.12 prüfen und sichtbar dokumentieren.
- [x] **V2-82 - CapabilityUse-Anbieter und Ziele ergänzen.** `provider: Entity [0..1]` im kompatiblen Core, genau ein Provider im ausführbaren Profil und `target: Identifiable [*]` modellieren. Kein Provider wird aus mehrdeutigen Legacy-Daten erfunden.
- [x] **V2-83 - Allgemeines Assertion-Modell einführen.** Abstrakte `Assertion` mit genau einem Subject und einer `EAExpression`, optionaler Severity sowie State-, Event-, Output-, Grounding- und Relation-Spezialisierungen modellieren.
- [x] **V2-84 - Effekt- und Intended-Outcome-Semantik bereinigen.** `Effect.specifiedBy: Assertion [1..*]` und abstraktes `AssertionOutcome -> VVIntendedOutcome` einführen; Legacy-`evidencedBy` ausschließlich als v0.5-Projektionsname bewahren.
- [x] **V2-85 - Strukturierte Runtime-Ergebnisse ergänzen.** `AssertionResult` mit Assertion, Verdict, optionalem EAValue, Evidence-Referenz und Zeitstempel sowie `RuntimeActualOutcome.result [1..*]` modellieren und validieren.
- [x] **V2-86 - V&V-Target und Subject präzisieren.** `RuntimeValidationTarget -> VVTarget` mit Platform, RuntimeBindings und Environment-Referenz ergänzen; DFMLDS-Subjects auf ScenarioStep, Capability, RuntimeBinding oder Entity beschränken, ohne EAST-ADL zu verändern.
- [x] **V2-87 - Kontrollflussregeln vervollständigen.** Same-Scenario-Endpunkte, fork/join-begrenzte ParallelGroups, Probability nur auf alternative/exception und Summenregel für vollständig annotierte Alternativverzweigungen als Invarianten und Instanzchecks ergänzen.
- [x] **V2-88 - Kompakte Gesamt- und Fachsichten aktualisieren.** Assertion, Provider/Target, RuntimeValidationTarget und AssertionResult in die vorhandenen acht Sichten integrieren; keine zusätzlichen Diagramme erzeugen.
- [x] **V2-89 - Kompatibilität und Validatoren erweitern.** 70 Legacy-CapabilityUses ohne erfundene Provider, sieben reale Roundtrips, neue Full-Surface-Fixture und positive/negative Mutationen vollständig prüfen.
- [x] **V2-90 - Prä-v1.0-Abnahme abschließen.** Alle Artefakte reproduzierbar generieren, 37 Modelltests und Backend-Smoke ausführen, alle acht PNGs visuell sowie geometrisch abnehmen und die Review-Entscheidungen dokumentieren.

## 7. Empfohlene Bearbeitungsreihenfolge

1. Phasen 1 und 2: unveränderter EAST-ADL-Ausschnitt und konservative Infrastruktur.
2. Phase 3: Szenariosemantik und migrationssensitive Namen.
3. Phase 4: Capability/Runtime unter Beibehaltung der Unity-Kette.
4. Phase 5: V&V-Neustrukturierung.
5. Phase 6: optionale Annex-C-/Feature-Mappings.
6. Phase 7: vollständige Konsistenz- und Nichtregressionsabnahme.
7. Phase 8: zentrale Gesamtansicht und kreuzungsfreie Fachsichten.

## 8. Definition of Done für V2 des Metamodells

V2 ist erst modellseitig fertig, wenn:

- keine EAST-ADL-Metaklasse durch DFMLDS-Pflichtmerkmale verändert wird,
- alle verwendeten EAST-ADL-Generalisationen, Attribute, Assoziationen und Multiplizitäten korrekt sind,
- die DFMLDS-Paketabhängigkeit einseitig ist,
- genau eine Ablaufsemantik definiert ist,
- der Capability-/Runtime-Pfad und alle bestehenden Agenten-, Handoff-, Grounding- und Validation-Fähigkeiten erhalten bleiben,
- jede v0.5-Instanz über eine dokumentierte, verlustfreie Kompatibilitätssicht repräsentierbar ist,
- alle Diagramm- und Spezifikationsartefakte dieselbe Modellfassung zeigen,
- die zentrale A/B/C-Ansicht als primärer Einstieg verständlich ist und alle acht Sichten die geometrische Null-Fehler-Prüfung bestehen,
- Unity, Backend und Pipeline in dieser Modellphase nicht geändert wurden.

Alle Punkte der Definition of Done sind im finalen Acceptance-Report mit
`status: pass` belegt.

## 9. Abschlussnachweis

| Nachweis | Finales Ergebnis |
|---|---|
| Task-Evidenz | 64/64 Tasks `PASS`, 0 `PENDING`; alle Quellenlinks auflösbar |
| EAST-ADL-Abgleich | 71 Klassen, 28 lokale Attribute, 68 Assoziationen, 3 Enumerationen, 0 offene Differenzen |
| v0.5-Kompatibilität | 173/173 Pfade zielaufgelöst; 7/7 reale Instanzen tiefengleich und ordnungsgleich zurückprojiziert |
| Modellvalidierung | 18/18 Modellkategorien, 13/13 Instanzkategorien und 17/17 Full-Surface-Anforderungen; 0 Fehler, 0 Warnungen |
| Kanonisches Modell | 118 Klassen, 2 Datentypen, 157 Assoziationen, 74 Invarianten, 8 Sichten |
| Generierung | 27 Artefakte; zwei Läufe byteidentisch; Artifact-Set `AF6B248D133F41583B3EE0644825B96B1BF0F913168F5B3499BD3B3457B7F5F8` |
| Diagrammgeometrie | 8/8 Sichten `PASS`; je 0 diagonale Segmente, Kartendurchläufe, Kreuzungen, Linienüberlagerungen und Kantenlabel/Karten-Überdeckungen |
| Bestandsschutz | 1.715 Implementierungsdateien / 2.449.211.010 Bytes geprüft, 0 Abweichungen |
| Runtime-Trace | 3 Logs, 260 unveränderte Ausgangsevents, 0 unaufgelöste Referenzen; Smoke-Test-Anhänge werden verifiziert und bytegleich zurückgerollt |
| Tests | 37/37 Modell-/Kompatibilitätstests plus Backend-Smoke-Test `PASS` |
| Gesamtstatus | `PASS` für Modellrelease `2.0.0-model` |

Verbindliche Detailnachweise:

- `evidence/task_evidence_matrix.md`
- `evidence/acceptance_report.json` und `evidence/acceptance_report.md`
- `evidence/east_adl_conformance_matrix.json` und `evidence/east_adl_conformance_matrix.md`
- `evidence/v05_compatibility_mapping.json`, `evidence/v05_field_coverage.json` und `evidence/v05_roundtrip_report.json`
- `evidence/nonregression_matrix.md`, `evidence/annex_c_mapping.md` und `evidence/visual_qa.md`
- `evidence/diagram_geometry_qa.json`
- `generated/dynamic_functional_mlds_v2.model.json`, `generated/dynamic_functional_mlds_v2_specification.md` und `generated/generation_manifest.sha256.json`
