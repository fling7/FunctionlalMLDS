# Spezifikation 11.5: Ergaenzungsmodelle

Stand: 2026-07-07

Task: 11.5 `Ergaenzungsmodell spezifizieren, falls erforderlich`

Zweck: Diese Spezifikation beschreibt optionale Ergaenzungsmodule fuer Bedarfe, die nicht in den Kern gehoeren, aber fuer Praezision, Generierung, Runtime-Anbindung oder Validierung maschinenlesbar werden sollen. Der Kern bleibt ohne jedes Modul gueltig.

Bezugsdateien:

- `extension_model_criteria.md`
- `gap_criteria_evaluation.md`
- `minimal_core_adaptations.md`
- `interaction_object_affordance_decision.md`
- `agent_goal_role_runtime_profile_decision.md`

## Entscheidung

Es werden neun optionale Ergaenzungsmodule spezifiziert:

| Prioritaet | Modul | Primaerer Zweck |
| --- | --- | --- |
| hoch | `InteractionObjectModule` | Bedienbare Objekte, Bedienpunkte und Affordances |
| hoch | `AssistantInteractionModule` | Vivian-Dialog, Guidance und Antwortoptionen |
| hoch | `DecisionRuleModule` | Readiness-, Diagnose- und Auswahlregeln |
| hoch | `StateTransitionModule` | Formale, optionale Zustandsuebergaenge |
| mittel | `SpatialSemanticsModule` | Raeumliche Beziehungen, Regionen und Constraints |
| mittel | `EventDetailModule` | Quelle, Ziel, Kanal, Payload und Korrelation von Events |
| mittel | `RuntimeExecutionModule` | Reihenfolge, Abhaengigkeiten und Fehlerbehandlung innerhalb einer RuntimeBinding |
| mittel | `ValidationAssertionModule` | Formale Testorakel und zusammengesetzte erwartete Outcomes |
| mittel | `RuntimeProfileModule` | Plattform-, Adapter-, Schema- und Profilinformationen |

Nicht spezifiziert werden `ScenarioVariationModule`, `SafetyArgumentModule` und `RecoveryPolicyModule`. Fuer die aktuelle Baseline reichen `Scenario.kind`, `StepRelation.kind`, `Condition`, `StateAssertion` und `ValidationCase`. Diese drei Module koennen spaeter bei erweitertem Varianten-, Safety- oder Robustheitsscope neu geprueft werden.

## Globale Modulregeln

| ID | Regel |
| --- | --- |
| MOD-01 | Jedes Modul ist optional. Ein Kernmodell ohne Modulinstanzen bleibt gueltig. |
| MOD-02 | Eine Modulklasse ersetzt keine Kernklasse. Sie verfeinert oder referenziert bestehende Kerninstanzen. |
| MOD-03 | Jede Anschlussstelle an den Kern ist eine gerichtete Referenz oder Assoziation mit Kardinalitaet. |
| MOD-04 | Modulklassen duerfen fachliche Semantik nicht direkt an technische Endpunkte binden. |
| MOD-05 | Technische Ausfuehrung wird nur ueber `RuntimeBinding` und `RuntimeAction` konkret. |
| MOD-06 | Es gibt keine direkte Pflichtkante `ScenarioStep -> RuntimeAction`. |
| MOD-07 | Es gibt keine direkte Kante `Affordance -> RuntimeAction`. Bedienung erzeugt fachliche Events oder StateAssertions; Runtime liegt hinter Capability und RuntimeBinding. |
| MOD-08 | `Actor` beschreibt externe Use-Case-Rollen. `Agent` und `Entity` beschreiben modellierte System- oder Szeneninstanzen. |
| MOD-09 | Modulinterne Kompositionen besitzen ihre Teile. Anschlussstellen an den Kern sind nicht-kompositiv. |
| MOD-10 | Alle Modulregeln muessen durch einen Validator oder Review-Check pruefbar sein. |

## Anschlussstellenuebersicht

Alle Kernanschlussstellen in dieser Spezifikation referenzieren bestehende Kernklassen:

`Actor`, `Agent`, `Entity`, `Event`, `Condition`, `StateAssertion`, `Capability`, `Effect`, `RuntimeBinding`, `RuntimeAction`, `ValidationCase`, `ScenarioStep`.

| Modul | Anschlussstellen an bestehende Kernklassen |
| --- | --- |
| `InteractionObjectModule` | `Entity`, `Actor`, `Event`, `Condition`, `StateAssertion`, `Capability` |
| `AssistantInteractionModule` | `Agent`, `Actor`, `Capability`, `ScenarioStep`, `Event`, `StateAssertion`, `RuntimeBinding` |
| `DecisionRuleModule` | `Capability`, `Condition`, `StateAssertion`, `Effect`, `ValidationCase`, `Entity` |
| `StateTransitionModule` | `Entity`, `Agent`, `Event`, `Condition`, `StateAssertion`, `Effect`, `ScenarioStep` |
| `SpatialSemanticsModule` | `Entity`, `Condition`, `StateAssertion`, `Event` |
| `EventDetailModule` | `Event`, `Actor`, `Entity`, `ScenarioStep`, `RuntimeAction` |
| `RuntimeExecutionModule` | `RuntimeBinding`, `RuntimeAction`, `ValidationCase` |
| `ValidationAssertionModule` | `ValidationCase`, `StateAssertion`, `Event`, `Effect`, `Condition` |
| `RuntimeProfileModule` | `RuntimeBinding`, `RuntimeAction`, `Condition`, `ValidationCase` |

## InteractionObjectModule

### Scope

Das Modul beschreibt, welche `Entity` als Interaktionsobjekt genutzt wird, welche Teile oder Zonen bedienbar sind und welche fachlichen Events oder Zustandsaussagen durch eine Bedienhandlung entstehen.

Nicht-Ziel: Das Modul beschreibt keine technische Unity-, API- oder Controller-Aktion. Technische Ausfuehrung bleibt hinter `Capability -> RuntimeBinding -> RuntimeAction`.

### Klassen

| Klasse | Attribute | Bedeutung |
| --- | --- | --- |
| `InteractionObject` | `label: String` | Interaktionssicht auf genau eine bestehende `Entity`. |
| `InteractionTarget` | `kind: InteractionTargetKind`, `localName: String [0..1]` | Bedienpunkt, Bedienzone oder sichtbares Anzeigeelement eines Interaktionsobjekts. |
| `Affordance` | `label: String`, `manipulationKind: ManipulationKind`, `isMandatory: boolean [0..1]` | Fachliche Handlung, die an einem Interaktionsobjekt angeboten wird. |
| `InputObjectConstraint` | `role: String [0..1]`, `quantity: String [0..1]` | Optionaler Bedarf an einem Eingabeobjekt, etwa Tasse oder Bohnenbehaelter. |
| `AffordanceFeedback` | `feedbackKind: FeedbackKind`, `message: String [0..1]` | Beobachtbare Rueckmeldung nach einer Affordance. |

### Enumerationen

| Enumeration | Werte |
| --- | --- |
| `InteractionTargetKind` | `controlSurface`, `interactionZone`, `display`, `handle`, `slot`, `region` |
| `ManipulationKind` | `press`, `place`, `select`, `confirm`, `observe`, `adjust`, `remove` |
| `FeedbackKind` | `visual`, `auditory`, `haptic`, `stateChange`, `dialogue` |

### Beziehungen

| Quelle | Ziel | Rollenname | Kardinalitaet | Besitz |
| --- | --- | --- | --- | --- |
| `InteractionObject` | `Entity` | `representedEntity` | `1` | Referenz |
| `InteractionObject` | `InteractionTarget` | `target` | `0..*` | Komposition |
| `InteractionObject` | `Affordance` | `affordance` | `1..*` | Komposition |
| `Affordance` | `InteractionTarget` | `actsOn` | `0..1` | Referenz |
| `Affordance` | `Actor` | `offeredTo` | `0..*` | Referenz |
| `Affordance` | `Condition` | `activationCondition` | `0..*` | Referenz |
| `Affordance` | `Event` | `producesEvent` | `1..*` | Referenz |
| `Affordance` | `StateAssertion` | `resultingState` | `0..*` | Referenz |
| `Affordance` | `Capability` | `enablesCapability` | `0..*` | Referenz |
| `Affordance` | `InputObjectConstraint` | `inputConstraint` | `0..*` | Komposition |
| `InputObjectConstraint` | `Entity` | `requiredEntity` | `0..*` | Referenz |
| `Affordance` | `AffordanceFeedback` | `feedback` | `0..*` | Komposition |
| `AffordanceFeedback` | `StateAssertion` | `evidencedBy` | `0..*` | Referenz |

### Invarianten

| ID | Invariante |
| --- | --- |
| IOM-01 | Jedes `InteractionObject` referenziert genau eine bestehende `Entity`. |
| IOM-02 | Jedes `InteractionObject` besitzt mindestens eine `Affordance`. |
| IOM-03 | Jede `Affordance` erzeugt mindestens ein fachliches `Event`. |
| IOM-04 | Eine `Affordance` darf keine `RuntimeAction` referenzieren. |
| IOM-05 | `offeredTo` referenziert `Actor`, nicht `Agent`. Die Rolle im Use Case bleibt von der Szeneninstanz getrennt. |

### Beispiel B

Die Kaffeemaschine ist eine `Entity` mit `kind = asset`. Das Modul ergaenzt:

| Instanz | Abbildung |
| --- | --- |
| `InteractionObject: CoffeeMachineInteraction` | `representedEntity -> Entity: CoffeeMachine` |
| `InteractionTarget: StartButton` | `kind = controlSurface`, `localName = start button` |
| `Affordance: PressStart` | `manipulationKind = press`, `actsOn -> StartButton`, `offeredTo -> Actor: Visitor` |
| `PressStart.producesEvent` | `Event: VisitorPressedStart` |
| `PressStart.resultingState` | `StateAssertion: StartRequestSubmitted` |
| `PressStart.enablesCapability` | `Capability: CheckMachineReadiness` |

Damit ist die Bedienung fachlich praezise, ohne eine technische Aktion direkt an die Taste zu haengen.

## AssistantInteractionModule

### Scope

Das Modul beschreibt Dialogakte, Guidance-Inhalte und Antwortoptionen fuer eine assistierende `Agent`-Instanz wie Vivian.

Nicht-Ziel: Das Modul ist kein Ersatz fuer `Capability` und kein UI-Implementierungsmodell. Es beschreibt, was Vivian fachlich mitteilt oder abfragt, nicht welche konkrete Render- oder Speech-API genutzt wird.

### Klassen

| Klasse | Attribute | Bedeutung |
| --- | --- | --- |
| `AssistantInteraction` | `label: String` | Dialogischer Kontext einer assistierenden Agent-Instanz. |
| `DialogueAct` | `kind: DialogueActKind`, `text: String [0..1]` | Einzelner fachlicher Dialogakt. |
| `GuidanceContent` | `topic: String`, `contentRef: String [0..1]`, `language: String [0..1]` | Strukturierter Inhalt fuer Anleitung oder Erklaerung. |
| `ResponseOption` | `label: String`, `isAffirmative: boolean [0..1]` | Moegliche Antwort oder Auswahl des Nutzers. |
| `InteractionPolicy` | `maxRepetitions: int [0..1]`, `timeoutExpression: String [0..1]` | Optionale Dialogpolitik fuer Wiederholung, Timeout oder Nachfrage. |
| `PresentationMode` | `modality: PresentationModality`, `channelHint: String [0..1]` | Fachlicher Hinweis auf Modalitaet, etwa Sprache oder visueller Hinweis. |

### Enumerationen

| Enumeration | Werte |
| --- | --- |
| `DialogueActKind` | `instruction`, `confirmationRequest`, `confirmation`, `errorExplanation`, `completionReport`, `correctionHint`, `question` |
| `PresentationModality` | `speech`, `text`, `highlight`, `avatarGesture`, `sound` |

### Beziehungen

| Quelle | Ziel | Rollenname | Kardinalitaet | Besitz |
| --- | --- | --- | --- | --- |
| `AssistantInteraction` | `Agent` | `assistant` | `1` | Referenz |
| `AssistantInteraction` | `Capability` | `supportsCapability` | `0..*` | Referenz |
| `AssistantInteraction` | `DialogueAct` | `dialogueAct` | `1..*` | Komposition |
| `DialogueAct` | `ScenarioStep` | `ownerStep` | `0..1` | Referenz |
| `DialogueAct` | `Capability` | `realizedBy` | `0..1` | Referenz |
| `DialogueAct` | `GuidanceContent` | `content` | `0..1` | Komposition |
| `DialogueAct` | `ResponseOption` | `responseOption` | `0..*` | Komposition |
| `DialogueAct` | `PresentationMode` | `presentationMode` | `0..*` | Komposition |
| `DialogueAct` | `StateAssertion` | `expectedState` | `0..*` | Referenz |
| `DialogueAct` | `RuntimeBinding` | `runtimeBinding` | `0..*` | Referenz |
| `ResponseOption` | `Actor` | `selectedBy` | `0..*` | Referenz |
| `ResponseOption` | `Event` | `producesEvent` | `0..*` | Referenz |
| `AssistantInteraction` | `InteractionPolicy` | `policy` | `0..1` | Komposition |

### Invarianten

| ID | Invariante |
| --- | --- |
| AIM-01 | `assistant` muss eine bestehende `Agent`-Instanz sein. |
| AIM-02 | Ein `DialogueAct` darf eine `Capability` referenzieren, aber keine `Capability` ersetzen. |
| AIM-03 | `ResponseOption.producesEvent` beschreibt fachliche Nutzerauswahl, keine technische UI-Callback-Implementierung. |
| AIM-04 | `runtimeBinding` ist optional und bleibt unterhalb der Capability-/Agent-Ausfuehrung; es entsteht keine direkte `ScenarioStep -> RuntimeAction`-Kante. |

### Beispiel B

Vivian prueft die Kaffeemaschine und fragt den Besucher nach Bestaetigung:

| Instanz | Abbildung |
| --- | --- |
| `AssistantInteraction: VivianCoffeeGuidance` | `assistant -> Agent: Vivian` |
| `DialogueAct: AskStartConfirmation` | `kind = confirmationRequest`, `ownerStep -> ScenarioStep: ConfirmStart` |
| `AskStartConfirmation.content` | `GuidanceContent: "Soll der Kaffee jetzt gestartet werden?"` |
| `ResponseOption: ConfirmStart` | `selectedBy -> Actor: Visitor`, `producesEvent -> Event: VisitorConfirmedStart` |
| `DialogueAct.expectedState` | `StateAssertion: UserConsentAvailable` |

## DecisionRuleModule

### Scope

Das Modul beschreibt fachliche Entscheidungsregeln, etwa ob eine Kaffeemaschine bereit ist oder welcher Agent eine Aufgabe uebernimmt.

Nicht-Ziel: Das Modul ist keine Programmiersprache und kein Runtime-Orchestrator. Es bestimmt fachliche Outcomes, nicht technische Aufrufreihenfolgen.

### Klassen

| Klasse | Attribute | Bedeutung |
| --- | --- | --- |
| `DecisionRuleSet` | `name: String`, `purpose: String [0..1]` | Zusammenhaengende Menge fachlicher Regeln. |
| `DecisionRule` | `name: String`, `priority: int [0..1]` | Einzelne Regel mit Bedingungen und Outcome. |
| `DecisionInput` | `name: String`, `inputKind: String [0..1]` | Benannte Eingabe fuer eine Entscheidung. |
| `DecisionOutcome` | `name: String`, `outcomeKind: DecisionOutcomeKind` | Ergebnis einer Regel. |
| `DiagnosticFinding` | `severity: FindingSeverity`, `message: String` | Begruendete Diagnose bei Nicht-Erfuellung. |
| `CorrectionProposal` | `text: String`, `isBlocking: boolean [0..1]` | Fachlicher Vorschlag zur Korrektur. |

### Enumerationen

| Enumeration | Werte |
| --- | --- |
| `DecisionOutcomeKind` | `accepted`, `rejected`, `requiresCorrection`, `deferred`, `unknown` |
| `FindingSeverity` | `info`, `warning`, `error`, `blocking` |

### Beziehungen

| Quelle | Ziel | Rollenname | Kardinalitaet | Besitz |
| --- | --- | --- | --- | --- |
| `DecisionRuleSet` | `Capability` | `evaluatesCapability` | `0..*` | Referenz |
| `DecisionRuleSet` | `DecisionRule` | `rule` | `1..*` | Komposition |
| `DecisionRule` | `Condition` | `condition` | `1..*` | Referenz |
| `DecisionRule` | `DecisionInput` | `input` | `0..*` | Komposition |
| `DecisionInput` | `Entity` | `subject` | `0..*` | Referenz |
| `DecisionRule` | `DecisionOutcome` | `outcome` | `1` | Komposition |
| `DecisionOutcome` | `StateAssertion` | `resultingState` | `0..*` | Referenz |
| `DecisionOutcome` | `Effect` | `promisedEffect` | `0..*` | Referenz |
| `DecisionOutcome` | `DiagnosticFinding` | `finding` | `0..*` | Komposition |
| `DiagnosticFinding` | `CorrectionProposal` | `proposal` | `0..*` | Komposition |
| `DecisionOutcome` | `ValidationCase` | `validatedBy` | `0..*` | Referenz |

### Invarianten

| ID | Invariante |
| --- | --- |
| DRM-01 | Jede `DecisionRule` besitzt mindestens eine `Condition` und genau ein `DecisionOutcome`. |
| DRM-02 | Ein `DecisionRuleSet` darf eine `Capability` bewerten, aber keine RuntimeAction direkt ausloesen. |
| DRM-03 | `DiagnosticFinding` muss aus einer nicht erfuellten oder auffaelligen fachlichen Bedingung begruendbar sein. |
| DRM-04 | Ein `DecisionOutcome` mit `outcomeKind = rejected` sollte mindestens eine `StateAssertion` oder einen `DiagnosticFinding` besitzen. |

### Beispiel B

Die Bereitschaftspruefung der Kaffeemaschine wird als Regelmenge modelliert:

| Instanz | Abbildung |
| --- | --- |
| `DecisionRuleSet: CoffeeMachineReadinessRules` | `evaluatesCapability -> Capability: CheckMachineReadiness` |
| `DecisionRule: CupPresentRule` | `condition -> Condition: CupIsPlaced` |
| `DecisionRule: WaterAvailableRule` | `condition -> Condition: WaterTankNotEmpty` |
| `DecisionOutcome: ReadyAccepted` | `resultingState -> StateAssertion: CoffeeMachineReady` |
| `DecisionOutcome: MissingCupRejected` | `finding -> DiagnosticFinding: CupMissing`, `proposal -> CorrectionProposal: PlaceCup` |

## StateTransitionModule

### Scope

Das Modul beschreibt optionale formale Zustandsdimensionen und erlaubte Zustandsuebergaenge fuer Entities oder Agents. Es ist sinnvoll, wenn lifecycleartige Semantik maschinenpruefbar werden soll.

Nicht-Ziel: Das Modul ersetzt keine `ScenarioStep`-Sequenz und keine `StateAssertion`. Es macht nur wiederkehrende Zustandslogik explizit.

### Klassen

| Klasse | Attribute | Bedeutung |
| --- | --- | --- |
| `StateDimension` | `name: String`, `isExclusive: boolean [0..1]` | Zustandsraum eines Subjekts, etwa RequestStatus oder AgentActivity. |
| `StateValue` | `name: String`, `isInitial: boolean [0..1]`, `isTerminal: boolean [0..1]` | Ein erlaubter Wert innerhalb einer Dimension. |
| `StateTransition` | `name: String`, `priority: int [0..1]` | Erlaubter Uebergang zwischen StateValues. |
| `TransitionPolicy` | `timeoutExpression: String [0..1]`, `retryLimit: int [0..1]` | Optionale fachliche Uebergangspolitik. |

### Beziehungen

| Quelle | Ziel | Rollenname | Kardinalitaet | Besitz |
| --- | --- | --- | --- | --- |
| `StateDimension` | `Entity` | `subject` | `1` | Referenz |
| `StateDimension` | `StateValue` | `value` | `1..*` | Komposition |
| `StateTransition` | `StateDimension` | `dimension` | `1` | Referenz |
| `StateTransition` | `StateValue` | `source` | `0..*` | Referenz |
| `StateTransition` | `StateValue` | `target` | `1` | Referenz |
| `StateTransition` | `Event` | `trigger` | `0..*` | Referenz |
| `StateTransition` | `Condition` | `guard` | `0..*` | Referenz |
| `StateTransition` | `Effect` | `effect` | `0..*` | Referenz |
| `StateTransition` | `StateAssertion` | `evidencedBy` | `0..*` | Referenz |
| `StateTransition` | `ScenarioStep` | `observedInStep` | `0..*` | Referenz |
| `StateTransition` | `TransitionPolicy` | `policy` | `0..1` | Komposition |

`Agent` wird ueber die bestehende Spezialisierung von `Entity` angebunden. Falls ein Agentenzustand modelliert wird, referenziert `StateDimension.subject` die entsprechende `Agent`-Instanz als `Entity`.

### Invarianten

| ID | Invariante |
| --- | --- |
| STM-01 | `source` und `target` eines `StateTransition` muessen zu derselben `StateDimension` gehoeren. |
| STM-02 | `source [0..*]` erlaubt Initial- oder Any-State-Uebergaenge; `target [1]` ist immer Pflicht. |
| STM-03 | `StateTransition` darf `ScenarioStep` nicht ersetzen; `observedInStep` ist nur eine Trace-Referenz. |
| STM-04 | Wenn `StateDimension.isExclusive = true`, darf zu einem Zeitpunkt nur ein aktiver `StateValue` fuer das Subjekt gelten. |

### Beispiel A und B

| Beispiel | Abbildung |
| --- | --- |
| Agent in Szene | `StateDimension: AgentActivity` fuer `Agent: MuseumGuide`, Werte `idle`, `navigating`, `explaining`; Transition `navigatingToExplaining` wird durch `Event: AgentArrivedAtTarget` getriggert. |
| Kaffeemaschine | `StateDimension: BrewingRequestStatus` fuer `Entity: BrewingRequest`, Werte `requested`, `checked`, `accepted`, `brewing`, `completed`, `rejected`; Transition `checkedToRejected` wird durch `Condition: ReadinessFailed` bewacht. |

## SpatialSemanticsModule

### Scope

Das Modul beschreibt strukturierte Raumsemantik wie `inside`, `at`, `near`, `reachable` oder `visibleTo`.

Nicht-Ziel: Das Modul erzwingt keine konkrete 3D-Engine, keine Koordinatenquelle und kein Geometriemodell im Kern.

### Klassen

| Klasse | Attribute | Bedeutung |
| --- | --- | --- |
| `SpatialFrame` | `name: String`, `unit: String [0..1]` | Bezugsrahmen fuer raeumliche Angaben. |
| `SpatialRegion` | `name: String`, `regionKind: SpatialRegionKind` | Semantischer Bereich, etwa Bedienzone oder Zielzone. |
| `SpatialPosition` | `expression: String`, `confidence: float [0..1]` | Optionale Positionsangabe einer Entity. |
| `SpatialRelation` | `kind: SpatialRelationKind`, `expression: String [0..1]` | Qualitative Relation zwischen zwei Entities. |
| `SpatialConstraint` | `expression: String`, `isHard: boolean [0..1]` | Raeumliche Bedingung oder Einschraenkung. |

### Enumerationen

| Enumeration | Werte |
| --- | --- |
| `SpatialRegionKind` | `room`, `zone`, `interactionArea`, `path`, `viewCone`, `safetyArea` |
| `SpatialRelationKind` | `inside`, `at`, `near`, `reachable`, `visibleTo`, `overlaps`, `movingTo` |

### Beziehungen

| Quelle | Ziel | Rollenname | Kardinalitaet | Besitz |
| --- | --- | --- | --- | --- |
| `SpatialFrame` | `Entity` | `contextEntity` | `0..1` | Referenz |
| `SpatialRegion` | `Entity` | `representedEntity` | `1` | Referenz |
| `SpatialPosition` | `Entity` | `subject` | `1` | Referenz |
| `SpatialPosition` | `SpatialFrame` | `frame` | `0..1` | Referenz |
| `SpatialRelation` | `Entity` | `subject` | `1` | Referenz |
| `SpatialRelation` | `Entity` | `object` | `1` | Referenz |
| `SpatialRelation` | `Condition` | `condition` | `0..*` | Referenz |
| `SpatialRelation` | `StateAssertion` | `assertion` | `0..*` | Referenz |
| `SpatialRelation` | `Event` | `triggerEvent` | `0..*` | Referenz |
| `SpatialConstraint` | `Condition` | `refinedCondition` | `0..*` | Referenz |

### Invarianten

| ID | Invariante |
| --- | --- |
| SSM-01 | Jede `SpatialRegion` muss durch genau eine `Entity` repraesentiert sein, meistens `Entity.kind = zone`. |
| SSM-02 | `SpatialRelation.subject` und `SpatialRelation.object` duerfen nicht dieselbe Instanz sein, ausser die Relation wird explizit als Selbstbezug begruendet. |
| SSM-03 | Raumsemantik darf `Condition.expression` oder `StateAssertion.expectedState` verfeinern, aber nicht deren Gueltigkeit aufheben. |

### Beispiel A

Ein dynamisch modellierter Agent bewegt sich zu einer Zielzone:

| Instanz | Abbildung |
| --- | --- |
| `SpatialRegion: CoffeeCounterZone` | `representedEntity -> Entity: CoffeeCounterZoneEntity` |
| `SpatialRelation: AgentNearCounter` | `kind = near`, `subject -> Entity/Agent: Vivian`, `object -> Entity: CoffeeCounterZoneEntity` |
| `SpatialRelation.assertion` | `StateAssertion: VivianIsNearCoffeeCounter` |

## EventDetailModule

### Scope

Das Modul strukturiert Details eines bestehenden `Event`, insbesondere Quelle, Ziel, Kanal, Payload und Korrelation.

Nicht-Ziel: Das Modul ersetzt `Event.expression` nicht. Es ergaenzt sie dort, wo Generatoren oder Validatoren strukturierte Eventdetails brauchen.

### Klassen

| Klasse | Attribute | Bedeutung |
| --- | --- | --- |
| `EventDetail` | `name: String [0..1]` | Strukturierte Zusatzsicht auf genau ein `Event`. |
| `EventPayload` | `schemaRef: String [0..1]`, `contentExpression: String [0..1]` | Fachliche Nutzlast eines Events. |
| `EventChannel` | `channelKind: EventChannelKind`, `name: String [0..1]` | Kommunikations- oder Wahrnehmungskanal. |
| `EventCorrelation` | `correlationKey: String`, `relationKind: String [0..1]` | Zusammenhang zwischen mehreren Events. |

### Enumerationen

| Enumeration | Werte |
| --- | --- |
| `EventChannelKind` | `userInput`, `sensor`, `dialogue`, `systemSignal`, `environmentObservation`, `runtimeLog` |

### Beziehungen

| Quelle | Ziel | Rollenname | Kardinalitaet | Besitz |
| --- | --- | --- | --- | --- |
| `EventDetail` | `Event` | `event` | `1` | Referenz |
| `EventDetail` | `Actor` | `sourceActor` | `0..*` | Referenz |
| `EventDetail` | `Entity` | `sourceEntity` | `0..*` | Referenz |
| `EventDetail` | `Entity` | `targetEntity` | `0..*` | Referenz |
| `EventDetail` | `ScenarioStep` | `consumedByStep` | `0..*` | Referenz |
| `EventDetail` | `RuntimeAction` | `observedByAction` | `0..*` | Referenz |
| `EventDetail` | `EventPayload` | `payload` | `0..1` | Komposition |
| `EventDetail` | `EventChannel` | `channel` | `0..1` | Komposition |
| `EventDetail` | `EventCorrelation` | `correlation` | `0..*` | Komposition |
| `EventCorrelation` | `Event` | `relatedEvent` | `1..*` | Referenz |

### Invarianten

| ID | Invariante |
| --- | --- |
| EDM-01 | Jedes `EventDetail` gehoert zu genau einem bestehenden `Event`. |
| EDM-02 | `sourceActor` und `sourceEntity` duerfen gemeinsam genutzt werden, muessen aber semantisch getrennt bleiben: Rolle versus modellierte Instanz. |
| EDM-03 | `observedByAction` darf nur beschreiben, dass eine RuntimeAction ein Event beobachtet oder emittiert; daraus folgt keine direkte `ScenarioStep -> RuntimeAction`-Pflichtkante. |

### Beispiel A und B

| Beispiel | Abbildung |
| --- | --- |
| Agentenmodellierung | `EventDetail: AgentArrivedDetail` mit `event -> Event: AgentArrivedAtTarget`, `sourceEntity -> Agent: Vivian`, `targetEntity -> Entity: TargetZone`. |
| Kaffeemaschine | `EventDetail: ButtonPressDetail` mit `event -> Event: VisitorPressedStart`, `sourceActor -> Actor: Visitor`, `targetEntity -> Entity: CoffeeMachine`, `channel = userInput`. |

## RuntimeExecutionModule

### Scope

Das Modul beschreibt technische Ausfuehrungsstruktur innerhalb einer bestehenden `RuntimeBinding`, etwa Aktionsreihenfolge, Abhaengigkeiten, Retry und Transaktion.

Nicht-Ziel: Das Modul erzeugt keine fachlichen Schritte. Es bleibt unterhalb von `RuntimeBinding`.

### Klassen

| Klasse | Attribute | Bedeutung |
| --- | --- | --- |
| `RuntimePlan` | `name: String`, `isTransactional: boolean [0..1]` | Ausfuehrungsplan fuer genau eine RuntimeBinding. |
| `RuntimeActionNode` | `orderIndex: int [0..1]`, `isOptional: boolean [0..1]` | Knoten fuer eine bestehende RuntimeAction. |
| `RuntimeActionDependency` | `kind: RuntimeDependencyKind` | Abhaengigkeit zwischen Action-Knoten. |
| `RetryPolicy` | `maxRetries: int`, `backoffExpression: String [0..1]` | Retry-Regel fuer einen Knoten oder Plan. |
| `FailureHandlingPolicy` | `failureKind: String [0..1]`, `handlingKind: FailureHandlingKind` | Technische Fehlerbehandlung. |

### Enumerationen

| Enumeration | Werte |
| --- | --- |
| `RuntimeDependencyKind` | `sequence`, `requiresSuccess`, `mayRunInParallel`, `compensates`, `observes` |
| `FailureHandlingKind` | `abort`, `retry`, `compensate`, `ignore`, `escalate` |

### Beziehungen

| Quelle | Ziel | Rollenname | Kardinalitaet | Besitz |
| --- | --- | --- | --- | --- |
| `RuntimePlan` | `RuntimeBinding` | `binding` | `1` | Referenz |
| `RuntimePlan` | `RuntimeActionNode` | `node` | `1..*` | Komposition |
| `RuntimePlan` | `ValidationCase` | `validatedBy` | `0..*` | Referenz |
| `RuntimeActionNode` | `RuntimeAction` | `action` | `1` | Referenz |
| `RuntimeActionNode` | `RetryPolicy` | `retryPolicy` | `0..1` | Komposition |
| `RuntimeActionNode` | `FailureHandlingPolicy` | `failurePolicy` | `0..1` | Komposition |
| `RuntimeActionDependency` | `RuntimeActionNode` | `source` | `1` | Referenz |
| `RuntimeActionDependency` | `RuntimeActionNode` | `target` | `1` | Referenz |
| `RuntimePlan` | `RuntimeActionDependency` | `dependency` | `0..*` | Komposition |

### Invarianten

| ID | Invariante |
| --- | --- |
| REM-01 | Jeder `RuntimePlan` referenziert genau eine `RuntimeBinding`. |
| REM-02 | Jeder `RuntimeActionNode` referenziert genau eine bestehende `RuntimeAction`. |
| REM-03 | Alle `RuntimeActionNode.action`-Instanzen eines Plans muessen zur fachlich referenzierten RuntimeBinding passen. |
| REM-04 | `RuntimePlan` darf keine `ScenarioStep`-Sequenz definieren oder ersetzen. |

### Beispiel B

Vivians technische Kaffeemaschinenanbindung benoetigt mehrere technische Actions:

| Instanz | Abbildung |
| --- | --- |
| `RuntimePlan: CoffeeMachineStartPlan` | `binding -> RuntimeBinding: StartCoffeeMachineBinding` |
| `RuntimeActionNode: CheckSensorNode` | `action -> RuntimeAction: readMachineSensors` |
| `RuntimeActionNode: SendStartNode` | `action -> RuntimeAction: sendStartCommand` |
| `RuntimeActionDependency` | `source -> CheckSensorNode`, `target -> SendStartNode`, `kind = requiresSuccess` |

## ValidationAssertionModule

### Scope

Das Modul beschreibt formale Testorakel fuer zusammengesetzte erwartete Outcomes. Es ist relevant, wenn `ValidationCase` mehr braucht als eine Menge einfacher StateAssertions.

Nicht-Ziel: Das Modul ersetzt nicht `Effect.evidencedBy`. Die Kernkante bleibt Traceability; dieses Modul ist formale Testlogik.

### Klassen

| Klasse | Attribute | Bedeutung |
| --- | --- | --- |
| `ValidationAssertion` | `name: String`, `operator: AssertionOperator` | Formale Aussage innerhalb eines ValidationCase. |
| `AssertionGroup` | `operator: AssertionOperator` | Gruppierung mehrerer Assertions. |
| `TemporalConstraint` | `expression: String`, `kind: TemporalConstraintKind` | Zeitliche Einschraenkung einer Assertion. |
| `Tolerance` | `expression: String`, `unit: String [0..1]` | Toleranz fuer quantitative Pruefungen. |
| `ValidationOutcome` | `kind: ValidationOutcomeKind`, `message: String [0..1]` | Strukturierter Ausgang einer Validierung. |

### Enumerationen

| Enumeration | Werte |
| --- | --- |
| `AssertionOperator` | `allOf`, `anyOf`, `not`, `implies`, `equals`, `observed` |
| `TemporalConstraintKind` | `before`, `after`, `within`, `until`, `eventually` |
| `ValidationOutcomeKind` | `passed`, `failed`, `inconclusive`, `notExecuted` |

### Beziehungen

| Quelle | Ziel | Rollenname | Kardinalitaet | Besitz |
| --- | --- | --- | --- | --- |
| `ValidationAssertion` | `ValidationCase` | `validationCase` | `1` | Referenz |
| `ValidationAssertion` | `StateAssertion` | `assertsState` | `0..*` | Referenz |
| `ValidationAssertion` | `Event` | `assertsEvent` | `0..*` | Referenz |
| `ValidationAssertion` | `Effect` | `assertsEffect` | `0..*` | Referenz |
| `ValidationAssertion` | `Condition` | `precondition` | `0..*` | Referenz |
| `ValidationAssertion` | `TemporalConstraint` | `temporalConstraint` | `0..1` | Komposition |
| `ValidationAssertion` | `Tolerance` | `tolerance` | `0..1` | Komposition |
| `AssertionGroup` | `ValidationAssertion` | `member` | `1..*` | Referenz |
| `ValidationAssertion` | `ValidationOutcome` | `observedOutcome` | `0..*` | Komposition |

### Invarianten

| ID | Invariante |
| --- | --- |
| VAM-01 | Jede `ValidationAssertion` gehoert zu genau einem `ValidationCase`. |
| VAM-02 | Eine `ValidationAssertion` muss mindestens eine Zielreferenz besitzen: `StateAssertion`, `Event` oder `Effect`. |
| VAM-03 | `ValidationOutcome` ist Ergebnis einer Pruefung, keine fachliche `StateAssertion`. |
| VAM-04 | Komplexe Assertion-Logik bleibt optional; einfache Kernmodelle brauchen dieses Modul nicht. |

### Beispiel B

Fuer den Kaffeemaschinenstart soll validiert werden, dass erst nach positiver Readiness gestartet wird:

| Instanz | Abbildung |
| --- | --- |
| `ValidationAssertion: StartOnlyAfterReady` | `validationCase -> ValidationCase: CoffeeMachineStartValidation` |
| `StartOnlyAfterReady.assertsState` | `StateAssertion: CoffeeMachineReady` |
| `StartOnlyAfterReady.assertsEvent` | `Event: StartCommandIssued` |
| `TemporalConstraint` | `kind = before`, `expression = ready before start command` |

## RuntimeProfileModule

### Scope

Das Modul beschreibt Plattform-, Adapter-, Schema- und Profilinformationen fuer technische Ausfuehrung.

Nicht-Ziel: Das Modul beschreibt nicht, warum eine Capability fachlich notwendig ist. Es beschreibt nur, unter welchen technischen Rahmenbedingungen eine bestehende RuntimeBinding oder RuntimeAction ausgefuehrt wird.

### Klassen

| Klasse | Attribute | Bedeutung |
| --- | --- | --- |
| `RuntimeProfile` | `name: String`, `version: String [0..1]` | Profil fuer technische Ausfuehrung einer RuntimeBinding. |
| `RuntimeEnvironment` | `name: String`, `environmentKind: String [0..1]` | Zielumgebung, etwa Unity, ROS, Web oder TestHarness. |
| `AdapterProfile` | `adapterName: String`, `adapterVersion: String [0..1]` | Adapter- oder Connector-Profil. |
| `SchemaModel` | `schemaRef: String`, `schemaVersion: String [0..1]` | Strukturmodell fuer Input/Output-Daten. |
| `ExecutionConstraint` | `expression: String`, `constraintKind: String [0..1]` | Technische Einschraenkung, etwa Latenz oder verfuegbare API. |
| `ProfileSelectionRule` | `priority: int [0..1]` | Regel fuer Profilauswahl. |

### Beziehungen

| Quelle | Ziel | Rollenname | Kardinalitaet | Besitz |
| --- | --- | --- | --- | --- |
| `RuntimeProfile` | `RuntimeBinding` | `binding` | `1` | Referenz |
| `RuntimeProfile` | `RuntimeAction` | `action` | `0..*` | Referenz |
| `RuntimeProfile` | `RuntimeEnvironment` | `environment` | `1` | Komposition |
| `RuntimeProfile` | `AdapterProfile` | `adapter` | `0..*` | Komposition |
| `RuntimeProfile` | `SchemaModel` | `schema` | `0..*` | Komposition |
| `RuntimeProfile` | `ExecutionConstraint` | `constraint` | `0..*` | Komposition |
| `RuntimeProfile` | `ProfileSelectionRule` | `selectionRule` | `0..*` | Komposition |
| `ProfileSelectionRule` | `Condition` | `condition` | `0..*` | Referenz |
| `RuntimeProfile` | `ValidationCase` | `validatedBy` | `0..*` | Referenz |

### Invarianten

| ID | Invariante |
| --- | --- |
| RPM-01 | Jedes `RuntimeProfile` referenziert genau eine `RuntimeBinding`. |
| RPM-02 | `RuntimeProfile.action` darf nur RuntimeActions referenzieren, die zur referenzierten RuntimeBinding passen. |
| RPM-03 | Profile duerfen fachliche `Capability`-Semantik nicht veraendern. |
| RPM-04 | `SchemaModel` ist ein technisches Strukturmodell, kein Ersatz fuer fachliche `Event`- oder `StateAssertion`-Semantik. |

### Beispiel B

Die Kaffeemaschinensteuerung laeuft in einer bestimmten Laufzeitumgebung:

| Instanz | Abbildung |
| --- | --- |
| `RuntimeProfile: VivianCoffeeRuntimeProfile` | `binding -> RuntimeBinding: StartCoffeeMachineBinding` |
| `RuntimeEnvironment: UnityVRLab` | `environmentKind = Unity` |
| `AdapterProfile: CoffeeMachineAdapter` | `adapterVersion = 1.0` |
| `SchemaModel: CoffeeStartCommandSchema` | `schemaRef = coffee/start-command` |

## Modulinteraktion

| Interaktion | Regel |
| --- | --- |
| `InteractionObjectModule` mit `SpatialSemanticsModule` | Ein `InteractionTarget` darf optional fachlich auf eine `SpatialRegion` bezogen werden. Diese Kante ist modul-intern zwischen Erweiterungen und keine neue Kernanschlussstelle. |
| `InteractionObjectModule` mit `AssistantInteractionModule` | Eine Vivian-Anweisung darf eine Affordance fachlich erklaeren, aber nicht direkt technisch ausfuehren. |
| `DecisionRuleModule` mit `ValidationAssertionModule` | DecisionOutcomes koennen durch ValidationCases und ValidationAssertions pruefbar gemacht werden. |
| `StateTransitionModule` mit `ValidationAssertionModule` | StateTransitions koennen erwartete StateAssertions liefern, die spaeter formal validiert werden. |
| `RuntimeProfileModule` mit `RuntimeExecutionModule` | RuntimeProfile beschreibt Umgebung und Adapter; RuntimeExecution beschreibt Reihenfolge und Fehlerbehandlung. |

## Migrationsregel

Bestehende Kernmodelle muessen nicht migriert werden. Ein Modell kann schrittweise ergaenzt werden:

| Ausgangspunkt im Kern | Optionale Ergaenzung |
| --- | --- |
| `Entity` ist bedienbar | `InteractionObject` mit Affordances anlegen |
| `Agent` fuehrt Assistenzdialog | `AssistantInteraction` mit DialogueActs anlegen |
| `Condition`-Menge wird zur Entscheidungslogik | `DecisionRuleSet` anlegen |
| Wiederkehrende Statuswechsel treten auf | `StateDimension` und `StateTransition` anlegen |
| `Event.expression` reicht nicht fuer Automatisierung | `EventDetail` anlegen |
| `RuntimeBinding` hat mehrere technische Aktionen | `RuntimePlan` anlegen |
| `ValidationCase` braucht formale Orakel | `ValidationAssertion` anlegen |
| Runtime-Adapter/Schemas muessen versioniert werden | `RuntimeProfile` anlegen |

## Validierungsregeln

| ID | Regel |
| --- | --- |
| VAL-11-5-01 | Jede Modulinstanz, die eine Kernanschlussstelle besitzt, muss eine existierende Kerninstanz referenzieren. |
| VAL-11-5-02 | Keine Modulbeziehung darf eine Kernklasse kompositiv besitzen. |
| VAL-11-5-03 | Kein Modul darf eine direkte `ScenarioStep -> RuntimeAction`-Kante einfuehren. |
| VAL-11-5-04 | Kein Modul darf eine direkte `Affordance -> RuntimeAction`-Kante einfuehren. |
| VAL-11-5-05 | Jede Modulklasse muss mindestens mittelbar auf eine Kernklasse tracebar sein. |
| VAL-11-5-06 | Moduluebergreifende Kanten muessen optional sein. |
| VAL-11-5-07 | Technische Profile und Ausfuehrungsplaene duerfen fachliche Capability-, Event- oder StateAssertion-Semantik nicht ueberschreiben. |
| VAL-11-5-08 | Jede neu eingefuehrte Kardinalitaet muss mit den Invarianten des jeweiligen Moduls vereinbar sein. |

## Abnahmekontrolle

| Kriterium aus Task 11.5 | Erfuellung |
| --- | --- |
| Entwurf mit Klassen vorhanden | Fuer alle neun Module sind Klassen und Attribute spezifiziert. |
| Beziehungen vorhanden | Fuer alle neun Module sind Beziehungen mit Quelle, Ziel, Rolle, Kardinalitaet und Besitzsemantik angegeben. |
| Anschlussstellen vorhanden | Die Anschlussstellenuebersicht nennt fuer jedes Modul bestehende Kernklassen. |
| Jede Anschlussstelle referenziert eine bestehende Kernklasse | Erfuellt: verwendet werden nur `Actor`, `Agent`, `Entity`, `Event`, `Condition`, `StateAssertion`, `Capability`, `Effect`, `RuntimeBinding`, `RuntimeAction`, `ValidationCase`, `ScenarioStep`. |
| Kern bleibt kompakt | Erfuellt: alle Module sind optional und fuehren keine neuen Pflichtklassen im Kern ein. |
| Kerninvarianten bleiben erhalten | Erfuellt: keine direkte `ScenarioStep -> RuntimeAction`- oder `Affordance -> RuntimeAction`-Kante. |
| Beispiele abgedeckt | Erfuellt: A-Agentenszene und B-Kaffeemaschine/Vivian sind in den Modulen beispielhaft abbildbar. |

## Konsequenz fuer Task 11.6

Task 11.6 kann aus dieser Spezifikation konkrete Modellanpassungen ableiten. Die Modellgrafik sollte nicht alle neun Module auf einmal in den Kern ziehen. Sinnvoll ist ein kompaktes Kernmetamodell mit zwei sichtbaren optionalen Erweiterungsbereichen:

- fachliche Erweiterungen: Interaction, Assistant, Decision, State, Spatial, EventDetail,
- technische Erweiterungen: RuntimeExecution, RuntimeProfile, ValidationAssertion.
