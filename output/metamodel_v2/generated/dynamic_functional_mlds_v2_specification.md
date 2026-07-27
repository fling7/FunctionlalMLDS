# Dynamic Functional MLDS V2 – Metamodell-Spezifikation

Modellversion: `2.0.0-model`  
Namespace: `DFMLDS::V2`  
Status: `accepted-model-release`  
EAST-ADL-Bezug: V2.1.12  
Kanonische Quelle: `tools/dynamic_functional_mlds_v2_model.py`

## 1. Abgrenzung und Konformitätsregel

Die blau dargestellten EAST-ADL-Metaklassen sind ein ausgewählter, unverändert übernommener Ausschnitt der EAST-ADL-Spezifikation V2.1.12. Auslassungen sind Auslassungen des Ausschnitts, keine Änderungen an EAST-ADL. Sämtliche projektspezifischen Klassen und Beziehungen liegen im Namespace `DFMLDS::V2`.

Die Abhängigkeit ist strikt einseitig: DFMLDS importiert EAST-ADL. Keine EAST-ADL-Metaklasse erhält durch V2 eine neue Eigenschaft, Pflichtassoziation oder Rückabhängigkeit. Annex C, Feature-Mapping und AgentKnowledge sind optionale Module; Annex C ist in V2.1.12 vorläufig.

V2 ist eine reine Modellfassung. Unity, Backend, Pipeline und die v0.5-Serialisierung werden nicht verändert.

## 2. Pakete

| Paket | Art | normativ | Imports | Zweck |
| --- | --- | --- | --- | --- |
| `EAST-ADL::Elements` | imported-east-adl | ja | — | Selected exact EAST-ADL V2.1.12 infrastructure slice (section 25). |
| `EAST-ADL::Datatypes` | imported-east-adl | ja | `EAST-ADL::Elements` | Selected exact EAST-ADL datatype slice (section 23). |
| `EAST-ADL::Values` | imported-east-adl | ja | `EAST-ADL::Datatypes` | Selected exact EAST-ADL value slice (section 24). |
| `EAST-ADL::Requirements` | imported-east-adl | ja | `EAST-ADL::Elements`, `EAST-ADL::UseCases`, `EAST-ADL::Behavior` | Selected exact EAST-ADL requirements slice (section 11). |
| `EAST-ADL::UseCases` | imported-east-adl | ja | `EAST-ADL::Elements` | Exact EAST-ADL Actor, UseCase, Extend, Include and ExtensionPoint slice (section 12). |
| `EAST-ADL::SystemModeling` | imported-east-adl | ja | `EAST-ADL::Elements`, `EAST-ADL::FunctionModeling` | Selected exact EAST-ADL abstraction-level slice (section 3). |
| `EAST-ADL::FunctionModeling` | imported-east-adl | ja | `EAST-ADL::Elements`, `EAST-ADL::Datatypes`, `EAST-ADL::Values` | Selected exact EAST-ADL function type/prototype slice (section 6). |
| `EAST-ADL::Behavior` | imported-east-adl | ja | `EAST-ADL::Elements`, `EAST-ADL::FunctionModeling`, `EAST-ADL::Values` | Selected exact EAST-ADL FunctionBehavior slice (section 9). |
| `EAST-ADL::Timing` | imported-east-adl | ja | `EAST-ADL::Elements` | Selected exact EAST-ADL timing event slice (section 14). |
| `EAST-ADL::Events` | imported-east-adl | ja | `EAST-ADL::Timing` | Selected exact EAST-ADL ExternalEvent slice (section 16). |
| `EAST-ADL::VerificationValidation` | imported-east-adl | ja | `EAST-ADL::Elements`, `EAST-ADL::Requirements` | Exact EAST-ADL V&V container and element slice (section 13). |
| `DFMLDS::V2::Core` | dfmlds-extension | ja | `EAST-ADL::Elements`, `EAST-ADL::Datatypes`, `EAST-ADL::Values`, `EAST-ADL::Requirements`, `EAST-ADL::UseCases`, `EAST-ADL::SystemModeling`, `EAST-ADL::FunctionModeling`, `EAST-ADL::Behavior`, `EAST-ADL::Timing`, `EAST-ADL::Events`, `EAST-ADL::VerificationValidation` | Conservative DFMLDS V2 extension; imported EAST-ADL packages never import it. |
| `EAST-ADL::AnnexC::BehaviorDescription` | imported-east-adl-annex-c | nein; vorläufig | `EAST-ADL::Elements`, `EAST-ADL::FunctionModeling`, `EAST-ADL::Behavior`, `EAST-ADL::VehicleFeatureModeling` | Preliminary Annex C behavior-description slice. |
| `EAST-ADL::AnnexC::AttributeQuantificationConstraint` | imported-east-adl-annex-c | nein; vorläufig | `EAST-ADL::Elements`, `EAST-ADL::Values` | Preliminary Annex C quantification slice. |
| `EAST-ADL::AnnexC::ComputationConstraint` | imported-east-adl-annex-c | nein; vorläufig | `EAST-ADL::Elements`, `EAST-ADL::AnnexC::AttributeQuantificationConstraint` | Preliminary Annex C logical-computation slice. |
| `EAST-ADL::AnnexC::TemporalConstraint` | imported-east-adl-annex-c | nein; vorläufig | `EAST-ADL::Elements`, `EAST-ADL::Values`, `EAST-ADL::Timing`, `EAST-ADL::AnnexC::BehaviorDescription`, `EAST-ADL::AnnexC::AttributeQuantificationConstraint` | Preliminary Annex C temporal-constraint slice; TransitionEvent is not Timing::Event. |
| `DFMLDS::V2::AnnexCBridge` | optional-dfmlds-extension | nein; vorläufig | `EAST-ADL::Elements`, `DFMLDS::V2::Core`, `EAST-ADL::AnnexC::ComputationConstraint`, `EAST-ADL::AnnexC::TemporalConstraint`, `EAST-ADL::AnnexC::AttributeQuantificationConstraint`, `EAST-ADL::AnnexC::BehaviorDescription` | Optional semantic mapping onto preliminary Annex C; Core has no dependency on it. |
| `EAST-ADL::FeatureModeling` | imported-east-adl-optional | ja | `EAST-ADL::Elements` | Minimal target slice for optional generic feature mapping. |
| `EAST-ADL::VehicleFeatureModeling` | imported-east-adl-optional | ja | `EAST-ADL::FeatureModeling` | Automotive-only VehicleFeature target slice. |
| `DFMLDS::V2::FeatureBridge` | optional-dfmlds-extension | nein | `EAST-ADL::Elements`, `DFMLDS::V2::Core`, `EAST-ADL::FeatureModeling`, `EAST-ADL::VehicleFeatureModeling` | Optional feature mapping; no VehicleFeature dependency in Core. |
| `DFMLDS::V2::AgentKnowledge` | optional-dfmlds-extension | nein | `EAST-ADL::Elements`, `DFMLDS::V2::Core` | Optional perception, provenance, knowledge and modification-rights module. |

## 3. Enumerationen

| Enumeration | Literale | Quelle |
| --- | --- | --- |
| `EAST-ADL::Behavior::FunctionBehaviorKind` | `ASCET`, `MARTE`, `OTHER`, `SCADE`, `SCILAB`, `SDL`, `SIMULINK`, `STATEMATE`, `UML` | 9.2.3, pp. 70-71 |
| `EAST-ADL::Behavior::TriggerPolicyKind` | `EVENT`, `TIME` | 9.2.7, p. 73 |
| `EAST-ADL::FunctionModeling::EADirectionKind` | `in`, `inout`, `out` | 6.2.9, p. 45 |
| `DFMLDS::V2::Core::ScenarioKind` | `main`, `alternative`, `exception` | DFMLDS V2 |
| `DFMLDS::V2::Core::ScenarioStepKind` | `actorIntent`, `systemResponse`, `environmentObservation` | DFMLDS V2 |
| `DFMLDS::V2::Core::StepRelationKind` | `sequence`, `alternative`, `exception`, `fork`, `join`, `loop` | DFMLDS V2 |
| `DFMLDS::V2::Core::ConditionKind` | `guard`, `precondition`, `postcondition`, `spatial`, `timing` | DFMLDS V2 |
| `DFMLDS::V2::Core::ScenarioEventKind` | `temporal`, `spatial`, `signal`, `user`, `environment` | DFMLDS V2 |
| `DFMLDS::V2::Core::AssertionSeverity` | `info`, `warning`, `error`, `critical` | DFMLDS V2 |
| `DFMLDS::V2::Core::AssertionVerdict` | `pass`, `fail`, `inconclusive`, `error` | DFMLDS V2 |
| `DFMLDS::V2::Core::EntityKind` | `agent`, `asset`, `zone`, `signal`, `stateObject` | DFMLDS V2 |
| `DFMLDS::V2::Core::RuntimeLocatorKind` | `endpoint`, `tool`, `topic` | DFMLDS V2 |
| `DFMLDS::V2::Core::RuntimeParameterDirection` | `input`, `output`, `inout` | DFMLDS V2 |
| `DFMLDS::V2::Core::DistributionKind` | `constant`, `uniform`, `normal`, `bernoulli`, `custom` | DFMLDS V2 |
| `DFMLDS::V2::AgentKnowledge::KnowledgePermission` | `perceive`, `know`, `explain`, `modify` | DFMLDS V2 |
| `DFMLDS::V2::AgentKnowledge::KnowledgeProvenanceKind` | `authored`, `observed`, `imported`, `inferred` | DFMLDS V2 |

## 4. Klassen und Datentypen

### EAST-ADL::Elements

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `Comment` | — | `body: String [1]` | Textual annotation. | 25.2.1, pp. 188-189 |
| `Context` (abstract) | `EAST-ADL::Elements::EAPackageableElement` | — | Owns relationships and identifies traceable specifications in a model context. | 25.2.2, p. 189 |
| `EAConnector` (abstract) | — | — | Abstract connector marker; it has no generalization. | 25.2.3, p. 189 |
| `EAElement` (abstract) | `EAST-ADL::Elements::Identifiable` | `name: String [0..1]` | Arbitrary named EAST-ADL domain-model entity. | 25.2.4, pp. 189-190 |
| `EAPackageableElement` (abstract) | `EAST-ADL::Elements::EAElement` | — | Element that may be directly contained in an EAPackage. | 25.2.6, pp. 190-191 |
| `EAPort` (abstract) | — | — | Abstract port marker; it has no generalization. | 25.2.7, p. 191 |
| `EAPrototype` (abstract) | — | — | Abstract prototype-pattern marker; it has no generalization. | 25.2.8, p. 191 |
| `EAType` (abstract) | — | — | Abstract type-pattern marker; it has no generalization. | 25.2.9, p. 191 |
| `Identifiable` (abstract) | `EAST-ADL::Elements::Referrable` | `category: Identifier [0..1]`<br>`uuid: String [0..1]` | Referrable element with optional category and UUID. | 25.2.11, pp. 192-193 |
| `Referrable` (abstract) | — | `shortName: Identifier [1]` | Element referable by a context-unique shortName. | 25.2.14, p. 194 |
| `Relationship` (abstract) | `EAST-ADL::Elements::EAElement` | — | Relationship between arbitrary elements. | 25.2.15, pp. 194-195 |
| `TraceableSpecification` (abstract) | `EAST-ADL::Elements::EAPackageableElement` | `text: String [0..1]` | Specification allocatable to a Context; text is its only local attribute. | 25.2.16, p. 195 |

### EAST-ADL::Datatypes

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `EABoolean` | `EAST-ADL::Datatypes::EADatatype` | — | Boolean datatype with true and false values. | 23.2.3, p. 177 |
| `EADatatype` (abstract) | `EAST-ADL::Elements::TraceableSpecification` | — | Type whose instances are identified only by value. | 23.2.4, p. 178 |
| `EADatatypePrototype` | `EAST-ADL::Elements::EAElement` | — | Typed variable acting as an appearance of an EADatatype. | 23.2.5, p. 178 |
| `EANumerical` | `EAST-ADL::Datatypes::EADatatype` | `max: Numerical [0..1]`<br>`min: Numerical [0..1]` | Numerical datatype with optional range bounds. | 23.2.6, pp. 178-179 |

### EAST-ADL::Values

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `EAExpression` | `EAST-ADL::Values::EAValue` | — | Mixed-string expression capable of model references. | 24.2.5, p. 185 |
| `EANumericalValue` | `EAST-ADL::Values::EAValue` | `value: Numerical [1]` | Numerical value typed by EANumerical or RangeableValueType. | 24.2.6, p. 185 |
| `EAValue` (abstract) | — | — | Abstract non-identifiable typed value. | 24.2.8, p. 186 |

### EAST-ADL::Requirements

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `Refine` | `EAST-ADL::Requirements::RequirementsRelationship` | — | Exact requirement-to-EAElement refinement relationship. | 11.2.5, p. 94 |
| `Requirement` | `EAST-ADL::Elements::TraceableSpecification` | `formalism: String [0..1]`<br>`url: String [0..1]` | Capability or condition to be satisfied; text is inherited and optional. | 11.2.6, pp. 94-95 |
| `RequirementsModel` | `EAST-ADL::Elements::Context` | — | Container for requirements, their relationships and use cases. | 11.2.9, p. 97 |
| `RequirementsRelationship` (abstract) | `EAST-ADL::Elements::Relationship` | — | Abstract base for requirement relationships. | 11.2.10, p. 97 |
| `Satisfy` | `EAST-ADL::Requirements::RequirementsRelationship` | — | Relates Requirement or UseCase suppliers to satisfying Identifiables. | 11.2.12, pp. 98-99 |

### EAST-ADL::UseCases

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `Actor` | `EAST-ADL::Elements::TraceableSpecification` | — | External role interacting with a UseCase, not a concrete physical entity. | 12.2.1, p. 101 |
| `Extend` | `EAST-ADL::Elements::Relationship` | — | Extends a UseCase at one or more ExtensionPoints; EAST-ADL defines no condition property. | 12.2.2, pp. 101-102 |
| `ExtensionPoint` | `EAST-ADL::UseCases::RedefinableElement` | — | Point where a UseCase can be augmented; name is inherited and optional. | 12.2.3, p. 102 |
| `Include` | `EAST-ADL::Elements::Relationship` | — | Mandatory insertion of an addition UseCase. | 12.2.4, p. 102 |
| `RedefinableElement` (abstract) | `EAST-ADL::Elements::EAElement` | — | Named element that can be redefined in a specializing context. | 12.2.5, pp. 102-103 |
| `UseCase` | `EAST-ADL::Elements::TraceableSpecification` | — | Usage of a system; text is inherited and optional. | 12.2.6, p. 103 |

### EAST-ADL::SystemModeling

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `AnalysisLevel` | `EAST-ADL::Elements::Context` | — | Analysis abstraction level containing an optional FAA root prototype. | 3.2.1, pp. 20-21 |
| `DesignLevel` | `EAST-ADL::Elements::Context` | — | Design abstraction level containing an optional FDA root prototype. | 3.2.2, pp. 21-22 |

### EAST-ADL::FunctionModeling

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `AllocateableElement` (abstract) | — | — | Abstract marker for allocateable elements. | 6.2.1, p. 41 |
| `AnalysisFunctionPrototype` | `EAST-ADL::FunctionModeling::FunctionPrototype` | — | Prototype typed by AnalysisFunctionType. | 6.2.3, p. 42 |
| `AnalysisFunctionType` | `EAST-ADL::FunctionModeling::FunctionType` | — | Function type used at AnalysisLevel; owns analysis parts. | 6.2.4, pp. 42-43 |
| `DesignFunctionPrototype` | `EAST-ADL::FunctionModeling::AllocateableElement`, `EAST-ADL::FunctionModeling::FunctionPrototype` | — | Allocateable prototype typed by DesignFunctionType. | 6.2.7, p. 44 |
| `DesignFunctionType` | `EAST-ADL::FunctionModeling::FunctionType` | — | Function type used at DesignLevel; owns design parts. | 6.2.8, pp. 44-45 |
| `FunctionConnector` | `EAST-ADL::FunctionModeling::AllocateableElement`, `EAST-ADL::Elements::EAConnector`, `EAST-ADL::Elements::EAElement` | — | Connector between exactly two FunctionPorts through an instance reference. | 6.2.14, pp. 47-48 |
| `FunctionFlowPort` | `EAST-ADL::FunctionModeling::FunctionPort` | `direction: EADirectionKind [1]` | Single-buffer flow port typed by an EADatatype. | 6.2.15, pp. 48-49 |
| `FunctionPort` (abstract) | `EAST-ADL::Elements::EAPort`, `EAST-ADL::Elements::EAElement` | — | Abstract function interaction port. | 6.2.16, pp. 49-50 |
| `FunctionPrototype` (abstract) | `EAST-ADL::Elements::EAElement`, `EAST-ADL::Elements::EAPrototype` | — | Occurrence of a FunctionType when acting as a part. | 6.2.18, pp. 50-51 |
| `FunctionType` (abstract) | `EAST-ADL::Elements::EAType`, `EAST-ADL::Elements::Context` | `isElementary: Boolean [1]` | Abstract function component type owning ports, connectors and port groups. | 6.2.19, p. 51 |
| `PortGroup` | `EAST-ADL::Elements::EAElement` | — | Graphical grouping of FunctionPorts without added behavior semantics. | 6.2.23, p. 54 |

### EAST-ADL::Behavior

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `FunctionBehavior` | `EAST-ADL::Elements::Context` | `path: String [1]`<br>`representation: FunctionBehaviorKind [1]` | Synchronous run-to-completion behavior assigned to at most one FunctionType. | 9.2.2, pp. 69-70 |
| `FunctionTrigger` | `EAST-ADL::Values::EAExpression`, `EAST-ADL::Elements::EAElement` | `triggerPolicy: TriggerPolicyKind [1]` | Event- or time-driven trigger for a FunctionType or FunctionPrototype. | 9.2.4, pp. 71-72 |
| `Mode` | `EAST-ADL::Elements::EAElement` | `condition: String [1]` | Execution mode with its mandatory activation condition. | 9.2.5, p. 72 |

### EAST-ADL::Timing

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `Event` (abstract) | `EAST-ADL::Timing::TimingDescription` | — | Identifiable form of state change with semantic occurrences. | 14.2.1, pp. 113-114 |
| `TimingDescription` (abstract) | `EAST-ADL::Elements::EAElement` | — | Abstract timing description. | 14.2.6, p. 116 |

### EAST-ADL::Events

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `ExternalEvent` | `EAST-ADL::Timing::Event` | — | Particular externally described form of state change. | 16.2.8, p. 139 |

### EAST-ADL::VerificationValidation

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `VVActualOutcome` | `EAST-ADL::Elements::TraceableSpecification` | — | Actual output captured by a VVLog. | 13.2.3, p. 107 |
| `VVCase` | `EAST-ADL::Elements::TraceableSpecification` | — | Groups VVProcedures and identifies subjects and concrete test targets. | 13.2.4, pp. 107-108 |
| `VVIntendedOutcome` | `EAST-ADL::Elements::TraceableSpecification` | — | Expected output of a concrete VVProcedure. | 13.2.5, p. 108 |
| `VVLog` | `EAST-ADL::Elements::TraceableSpecification` | `date: String [1]` | Execution log of a concrete VVCase; owns the actual outcomes. | 13.2.6, pp. 108-109 |
| `VVProcedure` | `EAST-ADL::Elements::TraceableSpecification` | — | Individual abstract or concrete task in a V&V effort. | 13.2.7, pp. 109-110 |
| `VVStimuli` | `EAST-ADL::Elements::TraceableSpecification` | — | Concrete input values used by a VVProcedure. | 13.2.8, p. 110 |
| `VVTarget` | `EAST-ADL::Elements::TraceableSpecification` | — | Concrete testing environment, distinct from VVCase.vvSubject. | 13.2.9, pp. 110-111 |
| `VerificationValidation` | `EAST-ADL::Elements::Context` | — | Container for related VVTargets, VVCases and Verify relationships. | 13.2.1, p. 106 |
| `Verify` | `EAST-ADL::Requirements::RequirementsRelationship` | — | Relates Requirements to verifying VVCases and optional VVProcedures. | 13.2.2, pp. 106-107 |

### DFMLDS::V2::Core

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `ActorParticipation` | `EAST-ADL::Elements::Relationship` | — | DFMLDS relationship assigning external Actor roles to UseCases. | DFMLDS V2 |
| `Agent` | `DFMLDS::V2::Core::Entity` | `sourceAgentId: String [0..1]`<br>`displayName: String [0..1]`<br>`persona: String [0..1]`<br>`expertise: String [*] {ordered}`<br>`knowledgeTag: String [*] {ordered}`<br>`voice: String [0..1]`<br>`voiceGender: String [0..1]`<br>`voiceStyle: String [0..1]`<br>`ttsModel: String [0..1]` | Entity capable of providing capabilities, grounded runtime interaction and handoffs. | DFMLDS V2 |
| `Assertion` (abstract) | `EAST-ADL::Elements::TraceableSpecification` | `/expressionText: String [1]`<br>`severity: AssertionSeverity [0..1]` | Abstract reusable, evaluable assertion about an identifiable subject. | DFMLDS V2 |
| `AssertionOutcome` (abstract) | `EAST-ADL::VerificationValidation::VVIntendedOutcome` | — | Intended outcome specified by one or more reusable Assertions. | DFMLDS V2 |
| `AssertionResult` | `EAST-ADL::Elements::EAElement` | `verdict: AssertionVerdict [1]`<br>`evidenceRef: String [0..1]`<br>`timestamp: String [0..1]` | Structured runtime evaluation result for exactly one Assertion. | DFMLDS V2 |
| `Capability` | `EAST-ADL::Elements::EAType`, `EAST-ADL::Elements::TraceableSpecification` | — | Domain-independent capability type retaining traceable intent and effects. | DFMLDS V2 |
| `CapabilityBehaviorBinding` | `EAST-ADL::Elements::Relationship` | `requiresRunToCompletion: Boolean [1]` = `true` | Optional relationship to a synchronous EAST-ADL FunctionBehavior; it is not Refine. | DFMLDS V2 |
| `CapabilityFunctionMapping` | `EAST-ADL::Elements::Relationship` | — | Optional mapping, not identity, to an exact analysis/design function type or prototype. | DFMLDS V2 |
| `CapabilityUse` | `EAST-ADL::Elements::EAPrototype`, `EAST-ADL::Elements::EAElement` | — | Typed occurrence of a Capability in a ScenarioStep. | DFMLDS V2 |
| `ConditionalExtend` | `EAST-ADL::UseCases::Extend` | — | Condition-bearing specialization of EAST-ADL Extend; remains admissible in UseCase.extend. | DFMLDS V2 |
| `DynamicFunctionalModel` | `EAST-ADL::Elements::Context` | — | Single root Context for a DFMLDS V2 model. | DFMLDS V2 |
| `Effect` | `EAST-ADL::Elements::TraceableSpecification` | — | Observable promised effect of a Capability. | DFMLDS V2 |
| `Entity` | `EAST-ADL::Elements::TraceableSpecification` | `kind: EntityKind [0..1]`<br>`sourceId: String [0..1]`<br>`entityRole: String [0..1]`<br>`sourceObjectId: String [*] {ordered}`<br>`purpose: String [0..1]`<br>`sourceGroup: String [0..1]`<br>`objectType: String [0..1]` | Concrete participant, asset, zone, signal or state object with optional source/provenance metadata. | DFMLDS V2 |
| `EventAssertion` | `DFMLDS::V2::Core::Assertion` | — | Assertion that an event occurred or did not occur. | DFMLDS V2 |
| `GroundingAssertion` | `DFMLDS::V2::Core::Assertion` | — | Assertion that information or interaction is grounded in an identifiable model element or source. | DFMLDS V2 |
| `KeyValueParameter` | `EAST-ADL::Datatypes::EADatatypePrototype` | — | Typed capability-use parameter; shortName is the key. | DFMLDS V2 |
| `OutputAssertion` | `DFMLDS::V2::Core::Assertion` | — | Assertion about an emitted visual, audio, textual or technical output. | DFMLDS V2 |
| `ParallelGroup` | `EAST-ADL::Elements::EAElement` | — | Structural grouping of parallel steps bounded by matching fork and join flow. | DFMLDS V2 |
| `ParameterBinding` | `EAST-ADL::Elements::Relationship` | — | Maps capability-use parameters to runtime parameters with an optional typed transformation. | DFMLDS V2 |
| `Probability` (datatype) | `EAST-ADL::Datatypes::EANumerical` | range `[0, 1]` | EANumerical specialization with closed value range [0, 1]. | DFMLDS V2 |
| `ProbabilityValue` | `EAST-ADL::Values::EANumericalValue` | — | Numerical value whose type is the bounded DFMLDS Probability datatype. | DFMLDS V2 |
| `RandomVariable` (datatype) | `EAST-ADL::Datatypes::EANumerical` | `distribution: DistributionKind [1]` | Typed stochastic quantity used by optional probabilistic expressions. | DFMLDS V2 |
| `RelationAssertion` | `DFMLDS::V2::Core::Assertion` | — | Assertion about a relation between identifiable model elements. | DFMLDS V2 |
| `RuntimeAction` | `EAST-ADL::Elements::EAElement` | — | Atomic technical action with exactly one structured locator. | DFMLDS V2 |
| `RuntimeActionLocator` | `EAST-ADL::Elements::EAElement` | `kind: RuntimeLocatorKind [1]`<br>`value: String [1]` | Exclusive endpoint, tool or topic locator. | DFMLDS V2 |
| `RuntimeActualOutcome` | `EAST-ADL::VerificationValidation::VVActualOutcome` | — | Actual runtime outcome; owned only by RuntimeValidationLog. | DFMLDS V2 |
| `RuntimeBinding` | `EAST-ADL::Elements::Relationship` | `targetPlatform: String [1]` | Ordered technical realization choices for a Capability. | DFMLDS V2 |
| `RuntimeParameter` | `EAST-ADL::Datatypes::EADatatypePrototype` | `direction: RuntimeParameterDirection [1]` | Typed runtime input/output parameter. | DFMLDS V2 |
| `RuntimeStimulus` | `EAST-ADL::VerificationValidation::VVStimuli` | — | Runtime stimulus specialization. | DFMLDS V2 |
| `RuntimeValidationLog` | `EAST-ADL::VerificationValidation::VVLog` | — | Runtime execution log containing actual outcomes. | DFMLDS V2 |
| `RuntimeValidationProcedure` | `EAST-ADL::VerificationValidation::VVProcedure` | — | Runtime-validation specialization of VVProcedure. | DFMLDS V2 |
| `RuntimeValidationTarget` | `EAST-ADL::VerificationValidation::VVTarget` | `platform: String [1]`<br>`environmentRef: String [0..1]` | Runtime test environment with an explicit platform; its elements need not equal the case's vvSubjects. | DFMLDS V2 |
| `Scenario` | `EAST-ADL::Elements::TraceableSpecification` | `kind: ScenarioKind [1]` | Complete main, alternative or exception execution flow. | DFMLDS V2 |
| `ScenarioCondition` | `EAST-ADL::Elements::EAElement`, `EAST-ADL::Values::EAExpression` | `kind: ConditionKind [1]`<br>`expressionText: String [1]` | Identifiable Boolean-typed EAExpression used as guard, pre/post, spatial or timing condition. | DFMLDS V2 |
| `ScenarioEvent` | `EAST-ADL::Timing::Event`, `EAST-ADL::Values::EAExpression` | `kind: ScenarioEventKind [1]`<br>`expressionText: String [1]` | Identifiable timing event with an EAExpression lexical representation. | DFMLDS V2 |
| `ScenarioExternalEvent` | `DFMLDS::V2::Core::ScenarioEvent`, `EAST-ADL::Events::ExternalEvent` | — | Scenario event representing a user, environment, spatial or other external state change. | DFMLDS V2 |
| `ScenarioStep` | `EAST-ADL::Elements::TraceableSpecification` | `/stepNumber: Integer [1]`<br>`kind: ScenarioStepKind [1]` | Traceable step in a scenario; it never references a RuntimeAction directly. | DFMLDS V2 |
| `SchemaReference` | `EAST-ADL::Elements::TraceableSpecification` | `uri: String [0..1]`<br>`dialect: String [0..1]` | Reference to, or textual form of, a runtime data schema. | DFMLDS V2 |
| `StateAssertion` | `DFMLDS::V2::Core::Assertion` | — | Assertion about a state or state transition; retained as the v0.5-compatible specialization. | DFMLDS V2 |
| `StateAssertionOutcome` | `DFMLDS::V2::Core::AssertionOutcome` | — | v0.5-compatible intended-outcome specialization for StateAssertions. | DFMLDS V2 |
| `StepRelation` | `EAST-ADL::Elements::Relationship` | `kind: StepRelationKind [1]` | Canonical local control-flow edge between scenario steps. | DFMLDS V2 |
| `UseCaseScenarioSpecification` | `EAST-ADL::Elements::Relationship` | — | Conservative DFMLDS relationship from an unchanged EAST-ADL UseCase to scenarios. | DFMLDS V2 |
| `ValidationCase` | `EAST-ADL::VerificationValidation::VVCase` | — | DFMLDS runtime-validation specialization of VVCase; legacy level is preserved by projection, not inferred. | DFMLDS V2 |
| `ValidationCaseUseCaseBinding` | `EAST-ADL::Elements::Relationship` | — | DFMLDS relationship for legacy validates_use_case_ids; Verify remains requirement-only. | DFMLDS V2 |

### EAST-ADL::AnnexC::BehaviorDescription

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `BehaviorConstraintParameter` (abstract, optional) | — | — | Abstract Annex C behavior-constraint parameter with no generalization. | Annex C 30.2.4, p. 217 |
| `BehaviorConstraintTargetBinding` (optional) | `EAST-ADL::Elements::Relationship` | — | Preliminary Annex C relationship assigning a BehaviorConstraintType to behavior targets. | Annex C 30.2.6, pp. 218-219 |
| `BehaviorConstraintType` (optional) | `EAST-ADL::Elements::Context` | — | Preliminary Annex C behavior-constraint type. | Annex C 30.2.7, pp. 219-220 |

### EAST-ADL::AnnexC::AttributeQuantificationConstraint

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `Quantification` (optional) | `EAST-ADL::Elements::EAElement`, `EAST-ADL::Values::EAExpression` | — | Preliminary Annex C value-condition expression. | Annex C 31.2.5, pp. 223-224 |

### EAST-ADL::AnnexC::ComputationConstraint

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `LogicalPath` (optional) | `EAST-ADL::Elements::EAElement` | — | Preliminary Annex C ordered/parallel logical cause-effect path. | Annex C 32.2.2, pp. 226-227 |
| `LogicalTransformation` (optional) | `EAST-ADL::Elements::EAElement` | `isClientServerInterface: Boolean [1]` = `false` | Preliminary Annex C logical computation restriction. | Annex C 32.2.3, pp. 227-228 |
| `TransformationOccurrence` (optional) | `EAST-ADL::Elements::EAElement` | — | Activation of a logical transformation. | Annex C 32.2.4, pp. 228-229 |

### EAST-ADL::AnnexC::TemporalConstraint

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `LogicalTimeCondition` (optional) | `EAST-ADL::Elements::EAElement` | `isLogicalTimeSuspended: Boolean [1]` = `false` | Preliminary Annex C logical time interval condition. | Annex C 33.2.1, p. 232 |
| `State` (optional) | `EAST-ADL::Elements::EAElement` | `isErrorState: Boolean [1]` = `false`<br>`isHazard: Boolean [1]` = `false`<br>`isInitState: Boolean [1]` = `false`<br>`isMode: Boolean [1]` = `false` | Preliminary Annex C discrete state. | Annex C 33.2.2, pp. 232-233 |
| `TransitionEvent` (optional) | `EAST-ADL::Elements::EAElement`, `EAST-ADL::AnnexC::BehaviorDescription::BehaviorConstraintParameter` | — | Occurrence parameter firing a transition; deliberately not a Timing::Event subtype. | Annex C 33.2.7, p. 236 |

### DFMLDS::V2::AnnexCBridge

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `ScenarioAnnexMapping` (optional) | `EAST-ADL::Elements::Relationship` | — | Optional bridge to preliminary Annex C constructs; never a Core prerequisite. | DFMLDS V2 |

### EAST-ADL::FeatureModeling

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `Feature` (optional) | `EAST-ADL::FeatureModeling::FeatureTreeNode` | `cardinality: String [1]` | Generic EAST-ADL feature. | 4.2.3, pp. 28-29 |
| `FeatureTreeNode` (abstract, optional) | `EAST-ADL::Elements::Context` | — | Abstract base for elements in a feature tree. | 4.2.8, p. 32 |

### EAST-ADL::VehicleFeatureModeling

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `VehicleFeature` (optional) | `EAST-ADL::FeatureModeling::Feature` | `isCustomerVisible: Boolean [1]`<br>`isDesignVariabilityRationale: Boolean [1]`<br>`isRemoved: Boolean [1]` | Automotive VehicleLevel feature; never required by the domain-independent Core. | 5.2.3, pp. 38-39 |

### DFMLDS::V2::FeatureBridge

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `CapabilityFeatureMapping` (optional) | `EAST-ADL::Elements::Relationship` | — | Optional mapping from Capability to generic Feature or automotive VehicleFeature. | DFMLDS V2 |

### DFMLDS::V2::AgentKnowledge

| Element | Basis/Basen | lokal definierte Attribute | Beschreibung | EAST-ADL-Quelle |
| --- | --- | --- | --- | --- |
| `AgentKnowledgeBinding` (optional) | `EAST-ADL::Elements::Relationship` | `permissions: KnowledgePermission [1..*]`<br>`provenanceKind: KnowledgeProvenanceKind [1]` | Optional permissions and provenance relationship for agent knowledge. | DFMLDS V2 |
| `KnowledgeItem` (optional) | `EAST-ADL::Elements::TraceableSpecification` | — | Optional traceable knowledge item. | DFMLDS V2 |
| `KnowledgeSource` (optional) | `EAST-ADL::Elements::TraceableSpecification` | `uri: String [0..1]` | Optional source/provenance record. | DFMLDS V2 |

## 5. Assoziationen

Die Multiplizität steht jeweils am referenzierten Ende. `{ordered}` kennzeichnet eine semantisch geordnete Sammlung; `{composite}` genau einen Kompositionsbesitzer.

| ID | Paket | Quelle | Ziel/Rolle | Multiplizitäten | Eigenschaften |
| --- | --- | --- | --- | --- | --- |
| `EAElement_ownedComment` | `EAST-ADL::Elements` | `EAElement.commentOwner` | `Comment.ownedComment` | `1 → *` | composite; owner=source |
| `Context_ownedRelationship` | `EAST-ADL::Elements` | `Context.owningContext` | `Relationship.ownedRelationship` | `1 → *` | composite; owner=source |
| `Context_traceableSpecification` | `EAST-ADL::Elements` | `Context.context` | `TraceableSpecification.traceableSpecification` | `* → *` | — |
| `EADatatypePrototype_type` | `EAST-ADL::Datatypes` | `EADatatypePrototype.typedPrototype` | `EADatatype.type` | `* → 1` | «isOfType» |
| `EAValue_type` | `EAST-ADL::Values` | `EAValue.typedValue` | `EADatatype.type` | `* → 1` | «isOfType» |
| `Requirement_mode` | `EAST-ADL::Requirements` | `Requirement.validRequirement` | `Mode.mode` | `* → *` | — |
| `RequirementsModel_requirement` | `EAST-ADL::Requirements` | `RequirementsModel.requirementsModel` | `Requirement.requirement` | `1 → *` | composite; owner=source |
| `RequirementsModel_useCase` | `EAST-ADL::Requirements` | `RequirementsModel.requirementsModel` | `UseCase.useCase` | `1 → *` | composite; owner=source |
| `Refine_refinedRequirement` | `EAST-ADL::Requirements` | `Refine.refine` | `Requirement.refinedRequirement` | `* → 1..*` | — |
| `Refine_refinedBy` | `EAST-ADL::Requirements` | `Refine.refine` | `EAElement.refinedBy` | `* → 1..*` | «instanceRef» |
| `Satisfy_satisfiedRequirement` | `EAST-ADL::Requirements` | `Satisfy.satisfy` | `Requirement.satisfiedRequirement` | `* → *` | — |
| `Satisfy_satisfiedUseCase` | `EAST-ADL::Requirements` | `Satisfy.satisfy` | `UseCase.satisfiedUseCase` | `* → *` | — |
| `Satisfy_satisfiedBy` | `EAST-ADL::Requirements` | `Satisfy.satisfy` | `Identifiable.satisfiedBy` | `* → 1..*` | «instanceRef» |
| `UseCase_extensionPoint` | `EAST-ADL::UseCases` | `UseCase.useCase` | `ExtensionPoint.extensionPoint` | `1 → *` | composite; owner=source |
| `UseCase_include` | `EAST-ADL::UseCases` | `UseCase.includingUseCase` | `Include.include` | `1 → *` | composite; owner=source |
| `UseCase_extend` | `EAST-ADL::UseCases` | `UseCase.extendingUseCase` | `Extend.extend` | `1 → *` | composite; owner=source |
| `Include_addition` | `EAST-ADL::UseCases` | `Include.include` | `UseCase.addition` | `* → 1` | — |
| `Extend_extendedCase` | `EAST-ADL::UseCases` | `Extend.extend` | `UseCase.extendedCase` | `* → 1` | — |
| `Extend_extensionLocation` | `EAST-ADL::UseCases` | `Extend.extend` | `ExtensionPoint.extensionLocation` | `* → 1..*` | — |
| `FunctionConnector_port` | `EAST-ADL::FunctionModeling` | `FunctionConnector.functionConnector` | `FunctionPort.port` | `* → 2` | «instanceRef» |
| `FunctionFlowPort_type` | `EAST-ADL::FunctionModeling` | `FunctionFlowPort.typedPort` | `EADatatype.type` | `* → 1` | «isOfType» |
| `FunctionFlowPort_defaultValue` | `EAST-ADL::FunctionModeling` | `FunctionFlowPort.functionFlowPort` | `EAValue.defaultValue` | `1 → 0..1` | composite; owner=source |
| `FunctionType_port` | `EAST-ADL::FunctionModeling` | `FunctionType.functionType` | `FunctionPort.port` | `1 → *` | composite; owner=source |
| `FunctionType_connector` | `EAST-ADL::FunctionModeling` | `FunctionType.functionType` | `FunctionConnector.connector` | `1 → *` | composite; owner=source |
| `FunctionType_portGroup` | `EAST-ADL::FunctionModeling` | `FunctionType.functionType` | `PortGroup.portGroup` | `1 → *` | composite; owner=source |
| `PortGroup_port` | `EAST-ADL::FunctionModeling` | `PortGroup.portGroup` | `FunctionPort.port` | `* → *` | — |
| `PortGroup_portGroup` | `EAST-ADL::FunctionModeling` | `PortGroup.parentPortGroup` | `PortGroup.portGroup` | `0..1 → *` | composite; owner=source |
| `AnalysisFunctionPrototype_type` | `EAST-ADL::FunctionModeling` | `AnalysisFunctionPrototype.typedPrototype` | `AnalysisFunctionType.type` | `* → 1` | «isOfType» |
| `AnalysisFunctionType_part` | `EAST-ADL::FunctionModeling` | `AnalysisFunctionType.analysisFunctionType` | `AnalysisFunctionPrototype.part` | `1 → *` | composite; owner=source |
| `DesignFunctionPrototype_type` | `EAST-ADL::FunctionModeling` | `DesignFunctionPrototype.typedPrototype` | `DesignFunctionType.type` | `* → 1` | «isOfType» |
| `DesignFunctionType_part` | `EAST-ADL::FunctionModeling` | `DesignFunctionType.designFunctionType` | `DesignFunctionPrototype.part` | `1 → *` | composite; owner=source |
| `AnalysisLevel_functionalAnalysisArchitecture` | `EAST-ADL::SystemModeling` | `AnalysisLevel.analysisLevel` | `AnalysisFunctionPrototype.functionalAnalysisArchitecture` | `1 → 0..1` | composite; owner=source |
| `DesignLevel_functionalDesignArchitecture` | `EAST-ADL::SystemModeling` | `DesignLevel.designLevel` | `DesignFunctionPrototype.functionalDesignArchitecture` | `1 → 0..1` | composite; owner=source |
| `FunctionBehavior_function` | `EAST-ADL::Behavior` | `FunctionBehavior.functionBehavior` | `FunctionType.function` | `* → 0..1` | — |
| `FunctionBehavior_mode` | `EAST-ADL::Behavior` | `FunctionBehavior.functionBehavior` | `Mode.mode` | `* → *` | — |
| `FunctionTrigger_port` | `EAST-ADL::Behavior` | `FunctionTrigger.functionTrigger` | `FunctionPort.port` | `* → *` | — |
| `FunctionTrigger_function` | `EAST-ADL::Behavior` | `FunctionTrigger.functionTrigger` | `FunctionType.function` | `* → 0..1` | — |
| `FunctionTrigger_functionPrototype` | `EAST-ADL::Behavior` | `FunctionTrigger.functionTrigger` | `FunctionPrototype.functionPrototype` | `* → 0..1` | — |
| `FunctionTrigger_mode` | `EAST-ADL::Behavior` | `FunctionTrigger.functionTrigger` | `Mode.mode` | `* → *` | — |
| `VerificationValidation_vvTarget` | `EAST-ADL::VerificationValidation` | `VerificationValidation.verificationValidation` | `VVTarget.vvTarget` | `1 → *` | composite; owner=source |
| `VerificationValidation_vvCase` | `EAST-ADL::VerificationValidation` | `VerificationValidation.verificationValidation` | `VVCase.vvCase` | `1 → *` | composite; owner=source |
| `VerificationValidation_verify` | `EAST-ADL::VerificationValidation` | `VerificationValidation.verificationValidation` | `Verify.verify` | `1 → *` | composite; owner=source |
| `Verify_verifiedRequirement` | `EAST-ADL::VerificationValidation` | `Verify.verify` | `Requirement.verifiedRequirement` | `* → 1..*` | — |
| `Verify_verifiedByProcedure` | `EAST-ADL::VerificationValidation` | `Verify.verify` | `VVProcedure.verifiedByProcedure` | `* → *` | — |
| `Verify_verifiedByCase` | `EAST-ADL::VerificationValidation` | `Verify.verify` | `VVCase.verifiedByCase` | `* → 1..*` | — |
| `VVActualOutcome_intendedOutcome` | `EAST-ADL::VerificationValidation` | `VVActualOutcome.actualOutcome` | `VVIntendedOutcome.intendedOutcome` | `* → 0..1` | — |
| `VVCase_vvProcedure` | `EAST-ADL::VerificationValidation` | `VVCase.vvCase` | `VVProcedure.vvProcedure` | `1 → *` | composite; owner=source, ordered |
| `VVCase_vvTarget` | `EAST-ADL::VerificationValidation` | `VVCase.vvCase` | `VVTarget.vvTarget` | `* → *` | — |
| `VVCase_vvLog` | `EAST-ADL::VerificationValidation` | `VVCase.vvCase` | `VVLog.vvLog` | `1 → *` | composite; owner=source |
| `VVCase_abstractVVCase` | `EAST-ADL::VerificationValidation` | `VVCase.concreteVVCase` | `VVCase.abstractVVCase` | `* → 0..1` | — |
| `VVCase_vvSubject` | `EAST-ADL::VerificationValidation` | `VVCase.vvCase` | `Identifiable.vvSubject` | `* → *` | «instanceRef» |
| `VVLog_performedVVProcedure` | `EAST-ADL::VerificationValidation` | `VVLog.vvLog` | `VVProcedure.performedVVProcedure` | `* → 1` | — |
| `VVLog_vvActualOutcome` | `EAST-ADL::VerificationValidation` | `VVLog.vvLog` | `VVActualOutcome.vvActualOutcome` | `1 → *` | composite; owner=source |
| `VVProcedure_abstractVVProcedure` | `EAST-ADL::VerificationValidation` | `VVProcedure.concreteVVProcedure` | `VVProcedure.abstractVVProcedure` | `* → 0..1` | — |
| `VVProcedure_vvStimuli` | `EAST-ADL::VerificationValidation` | `VVProcedure.vvProcedure` | `VVStimuli.vvStimuli` | `1 → *` | composite; owner=source |
| `VVProcedure_vvIntendedOutcome` | `EAST-ADL::VerificationValidation` | `VVProcedure.vvProcedure` | `VVIntendedOutcome.vvIntendedOutcome` | `1 → *` | composite; owner=source |
| `VVTarget_element` | `EAST-ADL::VerificationValidation` | `VVTarget.vvTarget` | `Identifiable.element` | `* → *` | «instanceRef» |
| `DynamicFunctionalModel_requirementsModel` | `DFMLDS::V2::Core` | `DynamicFunctionalModel.dynamicFunctionalModel` | `RequirementsModel.requirementsModel` | `1 → 1` | composite; owner=source |
| `DynamicFunctionalModel_actor` | `DFMLDS::V2::Core` | `DynamicFunctionalModel.dynamicFunctionalModel` | `Actor.actor` | `1 → *` | composite; owner=source |
| `DynamicFunctionalModel_scenario` | `DFMLDS::V2::Core` | `DynamicFunctionalModel.dynamicFunctionalModel` | `Scenario.scenario` | `1 → *` | composite; owner=source |
| `DynamicFunctionalModel_scenarioEvent` | `DFMLDS::V2::Core` | `DynamicFunctionalModel.dynamicFunctionalModel` | `ScenarioEvent.scenarioEvent` | `1 → *` | composite; owner=source |
| `DynamicFunctionalModel_scenarioCondition` | `DFMLDS::V2::Core` | `DynamicFunctionalModel.dynamicFunctionalModel` | `ScenarioCondition.scenarioCondition` | `1 → *` | composite; owner=source |
| `DynamicFunctionalModel_assertion` | `DFMLDS::V2::Core` | `DynamicFunctionalModel.dynamicFunctionalModel` | `Assertion.assertion` | `1 → *` | composite; owner=source |
| `DynamicFunctionalModel_entity` | `DFMLDS::V2::Core` | `DynamicFunctionalModel.dynamicFunctionalModel` | `Entity.entity` | `1 → *` | composite; owner=source |
| `DynamicFunctionalModel_capability` | `DFMLDS::V2::Core` | `DynamicFunctionalModel.dynamicFunctionalModel` | `Capability.capability` | `1 → *` | composite; owner=source |
| `DynamicFunctionalModel_runtimeBinding` | `DFMLDS::V2::Core` | `DynamicFunctionalModel.dynamicFunctionalModel` | `RuntimeBinding.runtimeBinding` | `1 → *` | composite; owner=source |
| `DynamicFunctionalModel_verificationValidation` | `DFMLDS::V2::Core` | `DynamicFunctionalModel.dynamicFunctionalModel` | `VerificationValidation.verificationValidation` | `1 → 1` | composite; owner=source |
| `UseCaseScenarioSpecification_useCase` | `DFMLDS::V2::Core` | `UseCaseScenarioSpecification.specification` | `UseCase.useCase` | `* → 1` | — |
| `UseCaseScenarioSpecification_scenario` | `DFMLDS::V2::Core` | `UseCaseScenarioSpecification.specification` | `Scenario.scenario` | `* → 1` | — |
| `ActorParticipation_actor` | `DFMLDS::V2::Core` | `ActorParticipation.participation` | `Actor.actor` | `* → 1` | — |
| `ActorParticipation_useCase` | `DFMLDS::V2::Core` | `ActorParticipation.participation` | `UseCase.useCase` | `* → 1` | — |
| `ConditionalExtend_condition` | `DFMLDS::V2::Core` | `ConditionalExtend.conditionalExtend` | `ScenarioCondition.condition` | `* → 1` | — |
| `Scenario_variantOf` | `DFMLDS::V2::Core` | `Scenario.variant` | `Scenario.variantOf` | `* → 0..1` | — |
| `Scenario_precondition` | `DFMLDS::V2::Core` | `Scenario.scenario` | `ScenarioCondition.precondition` | `* → *` | — |
| `Scenario_postcondition` | `DFMLDS::V2::Core` | `Scenario.scenario` | `ScenarioCondition.postcondition` | `* → *` | — |
| `Scenario_step` | `DFMLDS::V2::Core` | `Scenario.scenario` | `ScenarioStep.step` | `1 → 1..*` | composite; owner=source |
| `Scenario_stepRelation` | `DFMLDS::V2::Core` | `Scenario.scenario` | `StepRelation.stepRelation` | `1 → *` | composite; owner=source |
| `Scenario_parallelGroup` | `DFMLDS::V2::Core` | `Scenario.scenario` | `ParallelGroup.parallelGroup` | `1 → *` | composite; owner=source |
| `ScenarioStep_performedBy` | `DFMLDS::V2::Core` | `ScenarioStep.scenarioStep` | `Entity.performedBy` | `* → *` | — |
| `ScenarioStep_actorRole` | `DFMLDS::V2::Core` | `ScenarioStep.scenarioStep` | `Actor.actorRole` | `* → *` | — |
| `ScenarioStep_triggeredBy` | `DFMLDS::V2::Core` | `ScenarioStep.scenarioStep` | `ScenarioEvent.triggeredBy` | `* → *` | — |
| `ScenarioStep_guard` | `DFMLDS::V2::Core` | `ScenarioStep.scenarioStep` | `ScenarioCondition.guard` | `* → 0..1` | — |
| `ScenarioStep_resultingAssertion` | `DFMLDS::V2::Core` | `ScenarioStep.scenarioStep` | `Assertion.resultingAssertion` | `* → *` | — |
| `ScenarioStep_occurrenceProbability` | `DFMLDS::V2::Core` | `ScenarioStep.scenarioStep` | `ProbabilityValue.occurrenceProbability` | `1 → 0..1` | composite; owner=source |
| `ScenarioStep_capabilityUse` | `DFMLDS::V2::Core` | `ScenarioStep.scenarioStep` | `CapabilityUse.capabilityUse` | `1 → *` | composite; owner=source, ordered |
| `StepRelation_sourceStep` | `DFMLDS::V2::Core` | `StepRelation.outgoingRelation` | `ScenarioStep.sourceStep` | `* → 1` | — |
| `StepRelation_targetStep` | `DFMLDS::V2::Core` | `StepRelation.incomingRelation` | `ScenarioStep.targetStep` | `* → 1` | — |
| `StepRelation_guard` | `DFMLDS::V2::Core` | `StepRelation.stepRelation` | `ScenarioCondition.guard` | `* → 0..1` | — |
| `StepRelation_probability` | `DFMLDS::V2::Core` | `StepRelation.stepRelation` | `ProbabilityValue.probability` | `1 → 0..1` | composite; owner=source |
| `ParallelGroup_memberStep` | `DFMLDS::V2::Core` | `ParallelGroup.parallelGroup` | `ScenarioStep.memberStep` | `* → 2..*` | ordered |
| `Assertion_subject` | `DFMLDS::V2::Core` | `Assertion.assertion` | `Identifiable.subject` | `* → 1` | «instanceRef» |
| `Assertion_expression` | `DFMLDS::V2::Core` | `Assertion.assertion` | `EAExpression.expression` | `1 → 1` | composite; owner=source |
| `Entity_playsActor` | `DFMLDS::V2::Core` | `Entity.entity` | `Actor.playsActor` | `* → *` | — |
| `Entity_providedCapability` | `DFMLDS::V2::Core` | `Entity.provider` | `Capability.providedCapability` | `* → *` | — |
| `Entity_objectGroup` | `DFMLDS::V2::Core` | `Entity.groupMember` | `Entity.objectGroup` | `* → 0..1` | — |
| `Agent_handoffTarget` | `DFMLDS::V2::Core` | `Agent.handoffSource` | `Agent.handoffTarget` | `* → *` | — |
| `Agent_responsibleZone` | `DFMLDS::V2::Core` | `Agent.responsibleAgent` | `Entity.responsibleZone` | `* → *` | — |
| `Agent_groundedAsset` | `DFMLDS::V2::Core` | `Agent.groundedAgent` | `Entity.groundedAsset` | `* → *` | — |
| `Agent_groundedObjectGroup` | `DFMLDS::V2::Core` | `Agent.groundedAgent` | `Entity.groundedObjectGroup` | `* → *` | — |
| `CapabilityUse_type` | `DFMLDS::V2::Core` | `CapabilityUse.typedCapabilityUse` | `Capability.type` | `* → 1` | «isOfType» |
| `CapabilityUse_provider` | `DFMLDS::V2::Core` | `CapabilityUse.providedCapabilityUse` | `Entity.provider` | `* → 0..1` | — |
| `CapabilityUse_target` | `DFMLDS::V2::Core` | `CapabilityUse.targetedCapabilityUse` | `Identifiable.target` | `* → *` | «instanceRef» |
| `CapabilityUse_parameter` | `DFMLDS::V2::Core` | `CapabilityUse.capabilityUse` | `KeyValueParameter.parameter` | `1 → *` | composite; owner=source, ordered |
| `KeyValueParameter_value` | `DFMLDS::V2::Core` | `KeyValueParameter.keyValueParameter` | `EAValue.value` | `1 → 0..1` | composite; owner=source |
| `Capability_precondition` | `DFMLDS::V2::Core` | `Capability.capability` | `ScenarioCondition.precondition` | `* → *` | — |
| `Capability_effect` | `DFMLDS::V2::Core` | `Capability.capability` | `Effect.effect` | `1 → 1..*` | composite; owner=source |
| `Effect_specifiedBy` | `DFMLDS::V2::Core` | `Effect.effect` | `Assertion.specifiedBy` | `* → 1..*` | — |
| `Effect_observableBy` | `DFMLDS::V2::Core` | `Effect.effect` | `Actor.observableBy` | `* → *` | — |
| `CapabilityFunctionMapping_capability` | `DFMLDS::V2::Core` | `CapabilityFunctionMapping.functionMapping` | `Capability.capability` | `* → 1` | — |
| `CapabilityFunctionMapping_capabilityUse` | `DFMLDS::V2::Core` | `CapabilityFunctionMapping.functionMapping` | `CapabilityUse.capabilityUse` | `* → 0..1` | — |
| `CapabilityFunctionMapping_analysisType` | `DFMLDS::V2::Core` | `CapabilityFunctionMapping.functionMapping` | `AnalysisFunctionType.analysisFunctionType` | `* → 0..1` | — |
| `CapabilityFunctionMapping_analysisPrototype` | `DFMLDS::V2::Core` | `CapabilityFunctionMapping.functionMapping` | `AnalysisFunctionPrototype.analysisFunctionPrototype` | `* → 0..1` | — |
| `CapabilityFunctionMapping_designType` | `DFMLDS::V2::Core` | `CapabilityFunctionMapping.functionMapping` | `DesignFunctionType.designFunctionType` | `* → 0..1` | — |
| `CapabilityFunctionMapping_designPrototype` | `DFMLDS::V2::Core` | `CapabilityFunctionMapping.functionMapping` | `DesignFunctionPrototype.designFunctionPrototype` | `* → 0..1` | — |
| `CapabilityBehaviorBinding_capability` | `DFMLDS::V2::Core` | `CapabilityBehaviorBinding.behaviorBinding` | `Capability.capability` | `* → 1` | — |
| `CapabilityBehaviorBinding_functionBehavior` | `DFMLDS::V2::Core` | `CapabilityBehaviorBinding.behaviorBinding` | `FunctionBehavior.functionBehavior` | `* → 1` | — |
| `RuntimeBinding_capability` | `DFMLDS::V2::Core` | `RuntimeBinding.runtimeBinding` | `Capability.capability` | `* → 1` | — |
| `RuntimeBinding_runtimeAction` | `DFMLDS::V2::Core` | `RuntimeBinding.runtimeBinding` | `RuntimeAction.runtimeAction` | `1 → 1..*` | composite; owner=source, ordered |
| `RuntimeAction_locator` | `DFMLDS::V2::Core` | `RuntimeAction.runtimeAction` | `RuntimeActionLocator.locator` | `1 → 1` | composite; owner=source |
| `RuntimeAction_inputSchema` | `DFMLDS::V2::Core` | `RuntimeAction.runtimeAction` | `SchemaReference.inputSchema` | `1 → 0..1` | composite; owner=source |
| `RuntimeAction_outputSchema` | `DFMLDS::V2::Core` | `RuntimeAction.runtimeAction` | `SchemaReference.outputSchema` | `1 → 0..1` | composite; owner=source |
| `RuntimeAction_runtimeParameter` | `DFMLDS::V2::Core` | `RuntimeAction.runtimeAction` | `RuntimeParameter.runtimeParameter` | `1 → *` | composite; owner=source, ordered |
| `ParameterBinding_capabilityParameter` | `DFMLDS::V2::Core` | `ParameterBinding.parameterBinding` | `KeyValueParameter.capabilityParameter` | `* → 1` | — |
| `ParameterBinding_runtimeParameter` | `DFMLDS::V2::Core` | `ParameterBinding.parameterBinding` | `RuntimeParameter.runtimeParameter` | `* → 1` | — |
| `ParameterBinding_transformation` | `DFMLDS::V2::Core` | `ParameterBinding.parameterBinding` | `EAExpression.transformation` | `1 → 0..1` | composite; owner=source |
| `AssertionOutcome_assertion` | `DFMLDS::V2::Core` | `AssertionOutcome.assertionOutcome` | `Assertion.assertion` | `* → 1..*` | — |
| `AssertionResult_assertion` | `DFMLDS::V2::Core` | `AssertionResult.assertionResult` | `Assertion.assertion` | `* → 1` | — |
| `AssertionResult_observedValue` | `DFMLDS::V2::Core` | `AssertionResult.assertionResult` | `EAValue.observedValue` | `1 → 0..1` | composite; owner=source |
| `RuntimeActualOutcome_result` | `DFMLDS::V2::Core` | `RuntimeActualOutcome.runtimeActualOutcome` | `AssertionResult.result` | `1 → 1..*` | composite; owner=source |
| `RuntimeValidationTarget_runtimeBinding` | `DFMLDS::V2::Core` | `RuntimeValidationTarget.runtimeValidationTarget` | `RuntimeBinding.runtimeBinding` | `* → *` | «instanceRef» |
| `RuntimeStimulus_scenarioEvent` | `DFMLDS::V2::Core` | `RuntimeStimulus.runtimeStimulus` | `ScenarioEvent.scenarioEvent` | `* → 0..1` | — |
| `RuntimeStimulus_runtimeAction` | `DFMLDS::V2::Core` | `RuntimeStimulus.runtimeStimulus` | `RuntimeAction.runtimeAction` | `* → 0..1` | — |
| `ValidationCaseUseCaseBinding_validationCase` | `DFMLDS::V2::Core` | `ValidationCaseUseCaseBinding.useCaseBinding` | `ValidationCase.validationCase` | `* → 1` | — |
| `ValidationCaseUseCaseBinding_useCase` | `DFMLDS::V2::Core` | `ValidationCaseUseCaseBinding.useCaseBinding` | `UseCase.useCase` | `* → 1` | — |
| `BehaviorConstraintTargetBinding_behaviorConstraintType` | `EAST-ADL::AnnexC::BehaviorDescription` | `BehaviorConstraintTargetBinding.targetBinding` | `BehaviorConstraintType.behaviorConstraintType` | `* → 1` | optional module |
| `BehaviorConstraintTargetBinding_targetedFunctionType` | `EAST-ADL::AnnexC::BehaviorDescription` | `BehaviorConstraintTargetBinding.targetBinding` | `FunctionType.targetedFunctionType` | `* → *` | optional module |
| `BehaviorConstraintTargetBinding_targetedVehicleFeature` | `EAST-ADL::AnnexC::BehaviorDescription` | `BehaviorConstraintTargetBinding.targetBinding` | `VehicleFeature.targetedVehicleFeature` | `* → *` | optional module |
| `BehaviorConstraintTargetBinding_constrainedModeBehavior` | `EAST-ADL::AnnexC::BehaviorDescription` | `BehaviorConstraintTargetBinding.targetBinding` | `Mode.constrainedModeBehavior` | `* → *` | optional module |
| `BehaviorConstraintTargetBinding_constrainedFunctionBehavior` | `EAST-ADL::AnnexC::BehaviorDescription` | `BehaviorConstraintTargetBinding.targetBinding` | `FunctionBehavior.constrainedFunctionBehavior` | `* → *` | optional module |
| `BehaviorConstraintTargetBinding_constrainedFunctionTriggering` | `EAST-ADL::AnnexC::BehaviorDescription` | `BehaviorConstraintTargetBinding.targetBinding` | `FunctionTrigger.constrainedFunctionTriggering` | `* → *` | optional module |
| `LogicalPath_segment` | `EAST-ADL::AnnexC::ComputationConstraint` | `LogicalPath.logicalPath` | `LogicalPath.segment` | `* → *` | ordered, optional module |
| `LogicalPath_strand` | `EAST-ADL::AnnexC::ComputationConstraint` | `LogicalPath.logicalPath` | `LogicalPath.strand` | `* → *` | optional module |
| `LogicalPath_transformationOccurrence` | `EAST-ADL::AnnexC::ComputationConstraint` | `LogicalPath.logicalPath` | `TransformationOccurrence.transformationOccurrence` | `1 → 0..1` | composite; owner=source, optional module |
| `TransformationOccurrence_invokedLogicalTransformation` | `EAST-ADL::AnnexC::ComputationConstraint` | `TransformationOccurrence.transformationOccurrence` | `LogicalTransformation.invokedLogicalTransformation` | `* → 1` | optional module |
| `TransitionEvent_occurredExecutionEvent` | `EAST-ADL::AnnexC::TemporalConstraint` | `TransitionEvent.transitionEvent` | `Event.occurredExecutionEvent` | `* → *` | optional module |
| `ScenarioAnnexMapping_scenarioStep` | `DFMLDS::V2::AnnexCBridge` | `ScenarioAnnexMapping.annexMapping` | `ScenarioStep.scenarioStep` | `* → 0..1` | optional module |
| `ScenarioAnnexMapping_stepRelation` | `DFMLDS::V2::AnnexCBridge` | `ScenarioAnnexMapping.annexMapping` | `StepRelation.stepRelation` | `* → 0..1` | optional module |
| `ScenarioAnnexMapping_scenarioEvent` | `DFMLDS::V2::AnnexCBridge` | `ScenarioAnnexMapping.annexMapping` | `ScenarioEvent.scenarioEvent` | `* → 0..1` | optional module |
| `ScenarioAnnexMapping_stateAssertion` | `DFMLDS::V2::AnnexCBridge` | `ScenarioAnnexMapping.annexMapping` | `StateAssertion.stateAssertion` | `* → 0..1` | optional module |
| `ScenarioAnnexMapping_capability` | `DFMLDS::V2::AnnexCBridge` | `ScenarioAnnexMapping.annexMapping` | `Capability.capability` | `* → 0..1` | optional module |
| `ScenarioAnnexMapping_annexElement` | `DFMLDS::V2::AnnexCBridge` | `ScenarioAnnexMapping.annexMapping` | `EAElement.annexElement` | `* → 1..*` | optional module |
| `CapabilityFeatureMapping_capability` | `DFMLDS::V2::FeatureBridge` | `CapabilityFeatureMapping.featureMapping` | `Capability.capability` | `* → 1` | optional module |
| `CapabilityFeatureMapping_feature` | `DFMLDS::V2::FeatureBridge` | `CapabilityFeatureMapping.featureMapping` | `Feature.feature` | `* → 1` | optional module |
| `AgentKnowledgeBinding_agent` | `DFMLDS::V2::AgentKnowledge` | `AgentKnowledgeBinding.knowledgeBinding` | `Agent.agent` | `* → 1` | optional module |
| `AgentKnowledgeBinding_knowledgeItem` | `DFMLDS::V2::AgentKnowledge` | `AgentKnowledgeBinding.knowledgeBinding` | `KnowledgeItem.knowledgeItem` | `* → 1` | optional module |
| `AgentKnowledgeBinding_source` | `DFMLDS::V2::AgentKnowledge` | `AgentKnowledgeBinding.knowledgeBinding` | `KnowledgeSource.source` | `* → 0..1` | optional module |
| `AgentKnowledgeBinding_groundedEntity` | `DFMLDS::V2::AgentKnowledge` | `AgentKnowledgeBinding.knowledgeBinding` | `Entity.groundedEntity` | `* → *` | optional module |

## 6. Nummerierte Invarianten

Die nachfolgende Liste ist kanonisch. Diagramme, Tests und Kompatibilitätsnachweise referenzieren diese IDs.

| ID | Profil | Scope | Prüfausdruck | Bedeutung |
| --- | --- | --- | --- | --- |
| **INV-001** | `core` | `PackageDependency` | `EAST_ADL.packages.imports->excludes(DFMLDS_V2)` | Dependencies are one-way: DFMLDS may import EAST-ADL; no EAST-ADL package imports DFMLDS. |
| **INV-002** | `core` | `TraceableSpecification` | `localAttributes = {'text: String [0..1]'}` | The imported TraceableSpecification has exactly one local optional text attribute. |
| **INV-003** | `core` | `EAType|EAPrototype|EAPort|EAConnector` | `bases->isEmpty()` | The four imported infrastructure marker metaclasses have no generalizations. |
| **INV-004** | `core` | `Satisfy` | `satisfiedRequirement->notEmpty() xor satisfiedUseCase->notEmpty()` | Satisfy targets Requirements or UseCases, never both in one relationship. |
| **INV-005** | `core` | `Satisfy` | `satisfiedBy->forAll(not oclIsKindOf(Requirement) and not oclIsKindOf(RequirementContainer))` | satisfiedBy excludes Requirement and RequirementContainer. |
| **INV-006** | `core` | `Extend` | `localAttributes->isEmpty() and localAssociations->excludes(condition)` | Imported EAST-ADL Extend has no condition; ConditionalExtend adds it conservatively. |
| **INV-007** | `core` | `UseCaseScenarioSpecification` | `scenario->size() >= 0` | An unchanged EAST-ADL UseCase may have zero DFMLDS scenarios in the core profile. |
| **INV-008** | `executable` | `UseCaseScenarioSpecification` | `scenario->select(kind=main)->size() = 1` | The executable DFMLDS profile requires exactly one main scenario per specified UseCase. |
| **INV-009** | `core` | `Scenario` | `kind=main implies variantOf->isEmpty()` | A main scenario has no variantOf reference. |
| **INV-010** | `core` | `Scenario` | `kind<>main implies variantOf->size()=1 and variantOf.kind=main` | Every alternative or exception scenario references exactly one main scenario. |
| **INV-011** | `core` | `Scenario` | `stepRelation->select(kind=sequence or kind=fork or kind=join or kind=alternative or kind=exception or kind=loop)` | StepRelation is the single semantic source of control flow; collection order and stepNumber are display/projection data. |
| **INV-012** | `core` | `ScenarioStep` | `stepNumber = deriveTopologicalDisplayOrder(self)` | stepNumber is derived for display and is not a third control-flow authority. |
| **INV-013** | `core` | `ParallelGroup` | `memberStep->size()>=2 and boundedByReachableForkJoin(self)` | A ParallelGroup is structural and all members are reachable between matching fork and join relations. |
| **INV-014** | `core` | `ScenarioStep` | `not hasDirectReference(RuntimeAction)` | ScenarioStep never directly references RuntimeAction; the capability chain remains mandatory. |
| **INV-015** | `core` | `ScenarioCondition` | `type.oclIsKindOf(EABoolean)` | Every ScenarioCondition EAExpression is Boolean-typed. |
| **INV-016** | `core` | `ScenarioEvent` | `oclIsKindOf(Timing::Event) and oclIsKindOf(EAExpression)` | ScenarioEvent combines identifiable timing-event semantics with expression semantics. |
| **INV-017** | `core` | `Probability` | `min=0 and max=1` | Probability is an EANumerical type with the closed range [0,1]; this is not a UML multiplicity. |
| **INV-018** | `core` | `ProbabilityValue` | `type.oclIsTypeOf(Probability) and value>=0 and value<=1` | Every ProbabilityValue is typed by Probability and lies in its range. |
| **INV-019** | `core` | `Agent|Entity` | `oclIsKindOf(Agent) iff kind=EntityKind::agent` | Unity-compatible EntityKind.agent is retained and exactly equivalent to Agent specialization. |
| **INV-020** | `core` | `ScenarioStep` | `performedBy->forAll(oclIsKindOf(Entity)) and actorRole->forAll(oclIsKindOf(Actor))` | Concrete performers and external Actor roles remain separate. |
| **INV-021** | `core` | `CapabilityUse` | `type->size()=1 and type.oclIsKindOf(Capability)` | CapabilityUse follows the formal EAPrototype-to-EAType pattern. |
| **INV-022** | `core` | `Capability` | `effect->size()>=1` | Every Capability promises at least one observable Effect. |
| **INV-023** | `core` | `Effect` | `specifiedBy->size()>=1` | Every Effect is specified by at least one reusable, testable Assertion; an expectation is not mislabeled as evidence. |
| **INV-024** | `core` | `CapabilityFunctionMapping` | `targetCount(analysisFunctionType,analysisFunctionPrototype,designFunctionType,designFunctionPrototype)=1` | A function mapping selects exactly one real EAST-ADL type/prototype target; FAA/FDA are not invented metaclasses. |
| **INV-025** | `core` | `FunctionType` | `isElementary implies parts()->isEmpty()` | Elementary FunctionTypes have no analysis/design parts (exact EAST-ADL constraint). |
| **INV-026** | `core` | `FunctionConnector` | `port->size()=2` | FunctionConnector links exactly two FunctionPorts through instance references. |
| **INV-027** | `core` | `FunctionBehavior` | `path->size()=1 and representation->size()=1` | FunctionBehavior keeps both mandatory EAST-ADL attributes. |
| **INV-028** | `core` | `FunctionBehavior` | `executionSemantics=readInputs_executeToCompletion_publishOutputs` | FunctionBehavior has synchronous run-to-completion execution semantics. |
| **INV-029** | `core` | `CapabilityBehaviorBinding` | `requiresRunToCompletion=true` | A behavior binding is admissible only where the bound behavior's run-to-completion semantics fit; it is never a Refine relation. |
| **INV-030** | `core` | `RuntimeBinding` | `runtimeAction->size()>=1 and runtimeAction.isOrdered=true` | Every RuntimeBinding owns at least one ordered RuntimeAction. |
| **INV-031** | `core` | `RuntimeAction` | `locator->size()=1` | Every V2 RuntimeAction has exactly one structured locator. |
| **INV-032** | `core` | `RuntimeActionLocator` | `kind=endpoint xor kind=tool xor kind=topic` | Locator kind is exclusive; legacy endpoint/tool/topic slots are projection fields. |
| **INV-033** | `core` | `ParameterBinding` | `capabilityParameter->size()=1 and runtimeParameter->size()=1` | ParameterBinding maps one typed use parameter to one typed runtime parameter. |
| **INV-034** | `core` | `DynamicFunctionalModel` | `verificationValidation->size()=1` | The root owns exactly one exact VerificationValidation container. |
| **INV-035** | `core` | `ValidationCase` | `compositeOwner(self).oclIsKindOf(VerificationValidation)` | ValidationCase is composed only through VerificationValidation.vvCase, never directly by the root. |
| **INV-036** | `core` | `VVCase` | `vvLog->notEmpty() implies isConcrete(self)` | Only a concrete VVCase may own VVLogs. |
| **INV-037** | `core` | `VVCase` | `vvTarget->notEmpty() implies isConcrete(self)` | Only a concrete VVCase may have VVTargets. |
| **INV-038** | `core` | `VVCase` | `abstractVVCase->notEmpty() implies isConcrete(self)` | Only a concrete VVCase may identify an abstractVVCase. |
| **INV-039** | `core` | `VVProcedure` | `(vvStimuli->notEmpty() or vvIntendedOutcome->notEmpty() or abstractVVProcedure->notEmpty()) implies isConcrete(self)` | Stimuli, intended outcomes and abstractVVProcedure are concrete-procedure features. |
| **INV-040** | `core` | `RuntimeActualOutcome` | `compositeOwner(self).oclIsKindOf(RuntimeValidationLog)` | Actual runtime outcomes exist only under RuntimeValidationLog/VVLog. |
| **INV-041** | `core` | `VVCase` | `distinctRoles(vvSubject,VVTarget.element) and not requiredEqual(vvSubject,VVTarget.element)` | vvSubject and VVTarget.element have distinct roles but may coincidentally reference some of the same elements. |
| **INV-042** | `core` | `Verify` | `verifiedRequirement->size()>=1 and verifiedByCase->size()>=1` | Verify remains a RequirementsRelationship between Requirements and VVCases/optional procedures. |
| **INV-043** | `core` | `ValidationCaseUseCaseBinding` | `validationCase->size()=1 and useCase->size()=1` | Each UseCase-validation relationship has exactly one case and one UseCase and does not overload Verify. |
| **INV-044** | `core` | `ValidationCase` | `legacyLevel is suppliedBy(V05ProjectionLedger)` | Legacy abstract/concrete level is not uniquely derivable from abstractVVCase and must be preserved by the projection ledger. |
| **INV-045** | `compatibility` | `V05Projection` | `exportV05(importV05(x,ledger),ledger)=x` | Every valid v0.5 instance round-trips byte-semantically, including IDs, array order, null/missing distinctions and enum lexemes. |
| **INV-046** | `compatibility` | `V05Projection` | `reverseRoundTripRequires(isV05Representable(v2) or completeLedger(v2))` | V2-to-v0.5 reverse projection is total only for the representable subset or with a complete sidecar ledger. |
| **INV-047** | `compatibility` | `V05Projection` | `mainScenario is serialized before variants` | The v0.5 compatibility view keeps the main scenario first for existing backend selection behavior. |
| **INV-048** | `compatibility` | `V05Projection` | `preserveAgentEntityAlias(AG_id,ENT_AGENT_id)` | The two existing Agent identities and their provenance are preserved exactly. |
| **INV-049** | `annex-c` | `TransitionEvent` | `not oclIsKindOf(Timing::Event)` | Annex C TransitionEvent is EAElement plus BehaviorConstraintParameter, not a Timing::Event subtype. |
| **INV-050** | `annex-c` | `TransitionEvent` | `occurredExecutionEvent->forAll(oclIsKindOf(Timing::Event))` | The Annex C connection to Timing::Event is an association only. |
| **INV-051** | `annex-c` | `AnnexCBridge` | `optional=true and preliminary=true and not Core.imports(AnnexCBridge)` | Annex C mapping is optional and preliminary and creates no Core back-dependency. |
| **INV-052** | `feature` | `FeatureBridge` | `optional=true and not Core.imports(FeatureBridge)` | Generic/VehicleFeature mapping is optional; the domain-independent Core has no automotive dependency. |
| **INV-053** | `agent-knowledge` | `AgentKnowledge` | `optional=true and not Core.imports(AgentKnowledge)` | Knowledge/perception/provenance support is optional and does not invalidate existing Agent instances. |
| **INV-054** | `core` | `CapabilityFunctionMapping` | `capabilityUse->notEmpty() and prototypeTarget->notEmpty() implies prototypeTarget.type = mappedTypeFor(capabilityUse.type)` | A CapabilityUse-to-function-prototype mapping must use a prototype whose type matches the function type mapped for the same Capability. |
| **INV-055** | `annex-c` | `BehaviorConstraintType` | `targetBindings(self).targets()->notEmpty() or refinedRequirements(self)->notEmpty()` | An Annex C BehaviorConstraintType references at least one requirement, vehicle feature, mode, function type, function behavior, function trigger or error behavior definition. |
| **INV-056** | `core` | `RuntimeStimulus` | `scenarioEvent->notEmpty() or runtimeAction->notEmpty()` | A concrete RuntimeStimulus identifies at least one ScenarioEvent or RuntimeAction. |
| **INV-057** | `core` | `Agent` | `responsibleZone.kind=zone and groundedAsset.kind=asset` | Agent responsibility and grounding references retain the Unity-visible zone/asset meaning. |
| **INV-058** | `core` | `Refine` | `refinedBy->forAll(not oclIsKindOf(Requirement) and not oclIsKindOf(RequirementContainer))` | The exact Refine.refinedBy role excludes Requirement and RequirementContainer. |
| **INV-059** | `core` | `FunctionTrigger` | `triggerPolicy=EVENT implies port->notEmpty()` | An event-driven FunctionTrigger references at least one triggering port. |
| **INV-060** | `core` | `FunctionTrigger` | `triggerPolicy=TIME implies port->isEmpty()` | A time-driven FunctionTrigger has no triggering port. |
| **INV-061** | `core` | `FunctionTrigger` | `function->notEmpty() xor functionPrototype->notEmpty()` | A FunctionTrigger identifies either one FunctionType or one FunctionPrototype, never both. |
| **INV-062** | `core` | `FunctionTrigger` | `port->forAll(oclIsKindOf(FunctionFlowPort) and direction=in)` | Every triggering port is an input FunctionFlowPort. |
| **INV-063** | `core` | `DynamicFunctionalModel` | `requirementsModel->size()=1` | The DFMLDS application profile requires exactly one RequirementsModel in addition to exactly one VerificationValidation container. |
| **INV-064** | `core` | `CapabilityUse` | `provider->notEmpty() implies scenarioStep.performedBy->includes(provider) and provider.providedCapability->includes(type)` | An explicit CapabilityUse provider must perform the owning step and provide the referenced Capability type. |
| **INV-065** | `executable` | `CapabilityUse` | `provider->size()=1` | Every CapabilityUse in the executable authoring profile has exactly one explicit provider; the compatibility core remains [0..1] because legacy data cannot identify one unambiguously. |
| **INV-066** | `core` | `Assertion` | `not self.oclIsTypeOf(Assertion) and subject->size()=1 and expression->size()=1` | Only concrete Assertion specializations may be instantiated, each with exactly one identifiable subject and one EAExpression. |
| **INV-067** | `core` | `AssertionResult` | `assertion->size()=1 and verdict->size()=1` | Each structured result evaluates exactly one Assertion and records exactly one verdict. |
| **INV-068** | `core` | `RuntimeActualOutcome` | `result->size()>=1` | Every runtime actual outcome contains at least one structured AssertionResult. |
| **INV-069** | `core` | `RuntimeValidationTarget` | `platform->size()=1 and runtimeBinding->forAll(rb \| element->includes(rb))` | Every runtime target names one platform and exposes every configured RuntimeBinding through the inherited VVTarget.element role. |
| **INV-070** | `core` | `ValidationCase` | `vvSubject->forAll(s \| s.oclIsKindOf(ScenarioStep) or s.oclIsKindOf(Capability) or s.oclIsKindOf(RuntimeBinding) or s.oclIsKindOf(Entity))` | DFMLDS ValidationCase subjects are ScenarioSteps, Capabilities, RuntimeBindings or Entities while EAST-ADL VVCase.vvSubject remains unchanged. |
| **INV-071** | `core` | `StepRelation` | `sourceStep.scenario = targetStep.scenario` | Both endpoints of a StepRelation belong to the same owning Scenario. |
| **INV-072** | `core` | `ParallelGroup` | `memberStep->forAll(s \| s.scenario = self.scenario) and memberStep->size()>=2 and boundedByReachableForkJoin(self)` | A ParallelGroup is owned with at least two members in one Scenario, structurally between matching fork and join relations. |
| **INV-073** | `core` | `StepRelation` | `probability->notEmpty() implies (kind=alternative or kind=exception)` | A control-flow probability is permitted only on alternative or exception edges. |
| **INV-074** | `core` | `Scenario` | `completeProbabilisticBranches()->forAll(b \| abs(b.outgoing.probability.value->sum()-1.0)<0.000001)` | If every alternative/exception edge of a branch carries a probability, the complete branch probabilities sum to one. |

## 7. Verlustfreie v0.5-Kompatibilitätssicht

Die technische Sicht heißt `V05ProjectionLedger`. The v0.5 JSON schema and runtime implementation remain unchanged.

Projektionsgesetze:

- `exportV05(importV05(x, ledger), ledger) == x for every valid v0.5 instance`
- `importV05(exportV05(y, ledger), ledger) == y only for the v0.5-representable V2 subset or a complete ledger`

Der Ledger bewahrt:

- complete envelope and unknown extension data
- array order and main-scenario-first ordering
- presence versus explicit null versus empty values
- all opaque identifiers and enum lexemes
- raw stepNumber and storage order
- AG-* to ENT-AGENT-* alias/provenance pairs
- legacy ValidationCase.level without deriving it from abstractVVCase
- legacy endpoint/tool/topic slots while V2 uses one RuntimeActionLocator

Verbindliche fachlich-technische Kette:

```text
ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction
```

Verbotene Abkürzung: `ScenarioStep -> RuntimeAction`.

`CapabilityUse.provider` ist im rückwärtskompatiblen Core `[0..1]`, weil die vorhandenen v0.5-Daten keinen eindeutigen Anbieter enthalten. Das ausführbare Authoring-Profil fordert über `INV-065` genau einen Provider; dieser muss den owning `ScenarioStep` ausführen und den Capability-Typ bereitstellen. `CapabilityUse.target [*]` benennt die betroffenen identifizierbaren Objekte, ohne Parameter zu missbrauchen.

`Assertion` verallgemeinert prüfbare Zustands-, Ereignis-, Ausgabe-, Grounding- und Relationsaussagen. `StateAssertion` bleibt als verlustfrei projizierbare Spezialisierung erhalten. Effekte werden normativ durch `specifiedBy: Assertion [1..*]` beschrieben; das alte Feld `evidencedBy` bleibt ausschließlich der Name in der v0.5-Kompatibilitätssicht.

`StepRelation` ist die einzige Quelle der Kontrollflusssemantik. `Scenario.step` ist Containment, `stepNumber` nur Anzeige. Wahrscheinlichkeiten sind normativ nur auf `alternative`-/`exception`-Kanten zulässig; vollständig annotierte, wechselseitig ausschließende Verzweigungen summieren sich auf 1. Nicht passende Legacy-Werte bleiben unverändert im Projektionsledger.

## 8. Verification & Validation

`DynamicFunctionalModel` besitzt genau einen unveränderten `VerificationValidation`-Container. Dieser besitzt `VVCase`- und `VVTarget`-Instanzen sowie `Verify`-Beziehungen. `ValidationCase` wird ausschließlich über `VerificationValidation.vvCase` komponiert. `RuntimeActualOutcome` liegt ausschließlich in einem `RuntimeValidationLog`/`VVLog`.

`VVCase.vvSubject` bezeichnet das primäre Prüfobjekt. `VVTarget.element` bezeichnet Elemente, die die konkrete Testumgebung realisiert. Die Rollen sind semantisch getrennt, dürfen aber zufällig dieselben Elemente referenzieren.

`RuntimeValidationTarget` konkretisiert die Testumgebung durch `platform [1]`, optionale `environmentRef` und die konfigurierten `runtimeBinding [*]`; diese Bindings sind zugleich Elemente des geerbten `VVTarget.element`. Zulässige DFMLDS-Subjects sind `ScenarioStep`, `Capability`, `RuntimeBinding` und `Entity`, ohne die EAST-ADL-Assoziation zu verändern.

`RuntimeActualOutcome` enthält mindestens ein strukturiertes `AssertionResult`. Jedes Resultat referenziert genau eine Assertion und erfasst Verdict, optionalen typisierten Beobachtungswert, Evidence-Referenz und Zeitstempel.

Der v0.5-Wert `ValidationCase.level` wird nicht aus `abstractVVCase` geraten. Er bleibt explizit im Kompatibilitäts-Ledger erhalten.

## 9. Optionales Annex-C-Mapping

Annex C ist in EAST-ADL V2.1.12 vorläufig. Die folgenden Abbildungen sind deshalb semantische Optionen und keine Core-Gültigkeitsbedingungen:

| DFMLDS-Quelle | Annex-C-Ziel | Abbildungsart | Status |
| --- | --- | --- | --- |
| `ScenarioStep` | `LogicalTransformation / TransformationOccurrence` | optional-semantic | preliminary |
| `StepRelation.sequence` | `LogicalPath.segment` | optional-semantic | preliminary |
| `ParallelGroup and fork/join` | `LogicalPath.strand` | optional-semantic | preliminary |
| `ScenarioEvent` | `TransitionEvent.occurredExecutionEvent -> Timing::Event` | association-bridge | preliminary |
| `ScenarioCondition value condition` | `Quantification` | optional-semantic | preliminary |
| `ScenarioCondition timing condition` | `LogicalTimeCondition` | optional-semantic | preliminary |
| `StateAssertion` | `State / Quantification / VVIntendedOutcome` | context-dependent | preliminary |
| `Capability behavior` | `BehaviorConstraintType` | optional-semantic | preliminary |

Wesentlich: Annex-C-`TransitionEvent` generalisiert `EAElement` und `BehaviorConstraintParameter`, **nicht** `Timing::Event`. Die Verbindung erfolgt ausschließlich über `TransitionEvent.occurredExecutionEvent: Timing::Event [*]`.

## 10. Generierte Sichten

Jede Sicht wird aus derselben Modellbeschreibung als Mermaid, SVG und PNG erzeugt. Eine zentrale A/B/C-Gesamtansicht zeigt das kompakte Metamodell; sieben ergänzende Fachsichten liefern die vollständigen Details und Beziehungsnachweise.

| Präfix | Titel | Zweck |
| --- | --- | --- |
| `dynamic_functional_mlds_v2_metamodel` | Kompaktes Metamodell für Dynamic Functional MLDS (V2.0) | Zentrale EAST-ADL-konforme A/B/C-Gesamtansicht; die sieben Fachsichten liefern die vollständigen Details. |
| `01_east_adl_infrastructure` | EAST-ADL V2.1.12 – verwendeter Infrastruktur-Ausschnitt | Exact selected infrastructure, datatype and value inheritance. |
| `02_east_adl_requirements_usecases` | EAST-ADL Requirements/UseCases – verwendeter Ausschnitt | Unmodified Requirements and UseCases metaclasses plus their exact infrastructure bases. |
| `03_east_adl_function_system_behavior` | EAST-ADL Function/System/Behavior – verwendeter Ausschnitt | Exact type/prototype, FAA/FDA root, connector and behavior semantics. |
| `04_dfmlds_scenario_flow` | DFMLDS V2 – konservativer Szenario- und Ablaufkern | UseCase binding, actor/entity separation, typed events/conditions and canonical control flow. |
| `05_dfmlds_capability_runtime` | DFMLDS V2 – Capability-, Function- und Runtime-Bridge | EAType/EAPrototype capability pattern, optional exact function mapping and ordered runtime realization. |
| `06_east_adl_dfmlds_verification_validation` | EAST-ADL / DFMLDS V2 – Verification & Validation | Exact V&V container ownership with DFMLDS specializations, logs and distinct subject/target semantics. |
| `07_optional_annex_feature_knowledge` | DFMLDS V2 – optionale Annex-C-, Feature- und Wissensmodule | Optional one-way bridges; Annex C is preliminary and TransitionEvent is not Timing::Event. |

## 11. Reproduzierbarkeit

Der Generator validiert Referenzen, Paketabhängigkeiten, eindeutige Association-/Invariant-IDs, die lückenlose Invariantenfolge und alle View-Mitglieder vor dem Schreiben. JSON wird schlüsselsortiert ausgegeben; alle Artefakte enthalten keine Laufzeitstempel. `generation_manifest.sha256.json` enthält die SHA-256-Werte aller verwalteten Ausgaben.
