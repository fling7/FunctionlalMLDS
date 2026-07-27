# DFMLDS V2 - EAST-ADL-Konformitaetsmatrix

Stand: 2026-07-14

Referenz: EAST-ADL Domain Model Specification V2.1.12. Die PDF-Datei ist durch den in der Modellmetadatenquelle hinterlegten SHA-256-Wert gebunden.

## Umfang und Statussprache

Die Matrix enumeriert jede EAST-ADL-Klasse, jedes lokal uebernommene Attribut, jede uebernommene Enumeration und jede EAST-ADL-eigene Assoziation, die in der kanonischen V2-Modellquelle vorhanden ist. Nicht in den gewaehlten Ausschnitt uebernommene EAST-ADL-Eigenschaften werden nicht stillschweigend als vorhanden behauptet.

- `model-evidence`: Die Deklaration ist in der kanonischen Modellquelle vorhanden und mit einer PDF-Seite verbunden.
- `optional-preliminary`: Zusaetzlich optionaler, vorlaeufiger Annex-C-Ausschnitt.
- `optional-profile`: Zusaetzlich nur in einem optionalen Profil.
- `open-difference`: Direkter Seitenabgleich zeigt noch eine Differenz; fuer dieses Element wird keine Konformitaet behauptet.

Die Begriffe sind keine Test-PASS-Aussage. Ausfuehrungs- und Gesamtstatus kommen ausschliesslich aus den separaten Akzeptanzberichten.

## Vollstaendigkeitszaehlung

| Gegenstand | Kanonische Quelle | Matrix | Enumerationsstatus |
|---|---:|---:|---|
| EAST-ADL-Klassen | 71 | 71 | complete-enumeration |
| lokale Attribute | 28 | 28 | complete-enumeration |
| EAST-ADL-Assoziationen | 68 | 68 | complete-enumeration |
| EAST-ADL-Enumerationen | 3 | 3 | complete-enumeration |

Kanonische Quelle: `tools/dynamic_functional_mlds_v2_model.py`, SHA-256 `C585ED1DC9BFB7080A976D2491149B5D07DB87D1EE25C8CF0AE8E87C15A2A442`.

## Offene Differenzen

Im direkt verglichenen, uebernommenen Deklarationsumfang ist keine offene Differenz eingetragen. Dies ist ein Modellbeleg, kein Laufzeittest.

## Klassen und exakte Generalisierungen

| Paket | Klasse | Abstrakt | Generalisierung(en) | Stereotyp(en) | PDF-Beleg | Status |
|---|---|:---:|---|---|---|---|
| `EAST-ADL::Elements` | `EAST-ADL::Elements::Comment` | nein | keine | keine | 25.2.1, pp. 188-189 | model-evidence |
| `EAST-ADL::Elements` | `EAST-ADL::Elements::Referrable` | ja | keine | keine | 25.2.14, p. 194 | model-evidence |
| `EAST-ADL::Elements` | `EAST-ADL::Elements::Identifiable` | ja | `EAST-ADL::Elements::Referrable` | keine | 25.2.11, pp. 192-193 | model-evidence |
| `EAST-ADL::Elements` | `EAST-ADL::Elements::EAElement` | ja | `EAST-ADL::Elements::Identifiable` | keine | 25.2.4, pp. 189-190 | model-evidence |
| `EAST-ADL::Elements` | `EAST-ADL::Elements::EAPackageableElement` | ja | `EAST-ADL::Elements::EAElement` | keine | 25.2.6, pp. 190-191 | model-evidence |
| `EAST-ADL::Elements` | `EAST-ADL::Elements::Context` | ja | `EAST-ADL::Elements::EAPackageableElement` | keine | 25.2.2, p. 189 | model-evidence |
| `EAST-ADL::Elements` | `EAST-ADL::Elements::Relationship` | ja | `EAST-ADL::Elements::EAElement` | keine | 25.2.15, pp. 194-195 | model-evidence |
| `EAST-ADL::Elements` | `EAST-ADL::Elements::TraceableSpecification` | ja | `EAST-ADL::Elements::EAPackageableElement` | keine | 25.2.16, p. 195 | model-evidence |
| `EAST-ADL::Elements` | `EAST-ADL::Elements::EAType` | ja | keine | keine | 25.2.9, p. 191 | model-evidence |
| `EAST-ADL::Elements` | `EAST-ADL::Elements::EAPrototype` | ja | keine | keine | 25.2.8, p. 191 | model-evidence |
| `EAST-ADL::Elements` | `EAST-ADL::Elements::EAPort` | ja | keine | keine | 25.2.7, p. 191 | model-evidence |
| `EAST-ADL::Elements` | `EAST-ADL::Elements::EAConnector` | ja | keine | keine | 25.2.3, p. 189 | model-evidence |
| `EAST-ADL::Datatypes` | `EAST-ADL::Datatypes::EADatatype` | ja | `EAST-ADL::Elements::TraceableSpecification` | `atpType` | 23.2.4, p. 178 | model-evidence |
| `EAST-ADL::Datatypes` | `EAST-ADL::Datatypes::EADatatypePrototype` | nein | `EAST-ADL::Elements::EAElement` | `atpPrototype` | 23.2.5, p. 178 | model-evidence |
| `EAST-ADL::Datatypes` | `EAST-ADL::Datatypes::EABoolean` | nein | `EAST-ADL::Datatypes::EADatatype` | keine | 23.2.3, p. 177 | model-evidence |
| `EAST-ADL::Datatypes` | `EAST-ADL::Datatypes::EANumerical` | nein | `EAST-ADL::Datatypes::EADatatype` | keine | 23.2.6, pp. 178-179 | model-evidence |
| `EAST-ADL::Values` | `EAST-ADL::Values::EAValue` | ja | keine | `atpPrototype` | 24.2.8, p. 186 | model-evidence |
| `EAST-ADL::Values` | `EAST-ADL::Values::EAExpression` | nein | `EAST-ADL::Values::EAValue` | `atpMixedString` | 24.2.5, p. 185 | model-evidence |
| `EAST-ADL::Values` | `EAST-ADL::Values::EANumericalValue` | nein | `EAST-ADL::Values::EAValue` | keine | 24.2.6, p. 185 | model-evidence |
| `EAST-ADL::Requirements` | `EAST-ADL::Requirements::RequirementsRelationship` | ja | `EAST-ADL::Elements::Relationship` | keine | 11.2.10, p. 97 | model-evidence |
| `EAST-ADL::Requirements` | `EAST-ADL::Requirements::Requirement` | nein | `EAST-ADL::Elements::TraceableSpecification` | keine | 11.2.6, pp. 94-95 | model-evidence |
| `EAST-ADL::Requirements` | `EAST-ADL::Requirements::RequirementsModel` | nein | `EAST-ADL::Elements::Context` | keine | 11.2.9, p. 97 | model-evidence |
| `EAST-ADL::Requirements` | `EAST-ADL::Requirements::Satisfy` | nein | `EAST-ADL::Requirements::RequirementsRelationship` | keine | 11.2.12, pp. 98-99 | model-evidence |
| `EAST-ADL::Requirements` | `EAST-ADL::Requirements::Refine` | nein | `EAST-ADL::Requirements::RequirementsRelationship` | keine | 11.2.5, p. 94 | model-evidence |
| `EAST-ADL::UseCases` | `EAST-ADL::UseCases::Actor` | nein | `EAST-ADL::Elements::TraceableSpecification` | keine | 12.2.1, p. 101 | model-evidence |
| `EAST-ADL::UseCases` | `EAST-ADL::UseCases::RedefinableElement` | ja | `EAST-ADL::Elements::EAElement` | keine | 12.2.5, pp. 102-103 | model-evidence |
| `EAST-ADL::UseCases` | `EAST-ADL::UseCases::ExtensionPoint` | nein | `EAST-ADL::UseCases::RedefinableElement` | keine | 12.2.3, p. 102 | model-evidence |
| `EAST-ADL::UseCases` | `EAST-ADL::UseCases::Include` | nein | `EAST-ADL::Elements::Relationship` | keine | 12.2.4, p. 102 | model-evidence |
| `EAST-ADL::UseCases` | `EAST-ADL::UseCases::Extend` | nein | `EAST-ADL::Elements::Relationship` | keine | 12.2.2, pp. 101-102 | model-evidence |
| `EAST-ADL::UseCases` | `EAST-ADL::UseCases::UseCase` | nein | `EAST-ADL::Elements::TraceableSpecification` | keine | 12.2.6, p. 103 | model-evidence |
| `EAST-ADL::FunctionModeling` | `EAST-ADL::FunctionModeling::AllocateableElement` | ja | keine | keine | 6.2.1, p. 41 | model-evidence |
| `EAST-ADL::FunctionModeling` | `EAST-ADL::FunctionModeling::FunctionPort` | ja | `EAST-ADL::Elements::EAPort`<br>`EAST-ADL::Elements::EAElement` | `atpPrototype` | 6.2.16, pp. 49-50 | model-evidence |
| `EAST-ADL::FunctionModeling` | `EAST-ADL::FunctionModeling::FunctionFlowPort` | nein | `EAST-ADL::FunctionModeling::FunctionPort` | keine | 6.2.15, pp. 48-49 | model-evidence |
| `EAST-ADL::FunctionModeling` | `EAST-ADL::FunctionModeling::FunctionConnector` | nein | `EAST-ADL::FunctionModeling::AllocateableElement`<br>`EAST-ADL::Elements::EAConnector`<br>`EAST-ADL::Elements::EAElement` | `atpStructureElement` | 6.2.14, pp. 47-48 | model-evidence |
| `EAST-ADL::FunctionModeling` | `EAST-ADL::FunctionModeling::PortGroup` | nein | `EAST-ADL::Elements::EAElement` | keine | 6.2.23, p. 54 | model-evidence |
| `EAST-ADL::FunctionModeling` | `EAST-ADL::FunctionModeling::FunctionPrototype` | ja | `EAST-ADL::Elements::EAElement`<br>`EAST-ADL::Elements::EAPrototype` | `atpPrototype` | 6.2.18, pp. 50-51 | model-evidence |
| `EAST-ADL::FunctionModeling` | `EAST-ADL::FunctionModeling::FunctionType` | ja | `EAST-ADL::Elements::EAType`<br>`EAST-ADL::Elements::Context` | `atpType` | 6.2.19, p. 51 | model-evidence |
| `EAST-ADL::FunctionModeling` | `EAST-ADL::FunctionModeling::AnalysisFunctionPrototype` | nein | `EAST-ADL::FunctionModeling::FunctionPrototype` | keine | 6.2.3, p. 42 | model-evidence |
| `EAST-ADL::FunctionModeling` | `EAST-ADL::FunctionModeling::AnalysisFunctionType` | nein | `EAST-ADL::FunctionModeling::FunctionType` | keine | 6.2.4, pp. 42-43 | model-evidence |
| `EAST-ADL::FunctionModeling` | `EAST-ADL::FunctionModeling::DesignFunctionPrototype` | nein | `EAST-ADL::FunctionModeling::AllocateableElement`<br>`EAST-ADL::FunctionModeling::FunctionPrototype` | keine | 6.2.7, p. 44 | model-evidence |
| `EAST-ADL::FunctionModeling` | `EAST-ADL::FunctionModeling::DesignFunctionType` | nein | `EAST-ADL::FunctionModeling::FunctionType` | keine | 6.2.8, pp. 44-45 | model-evidence |
| `EAST-ADL::SystemModeling` | `EAST-ADL::SystemModeling::AnalysisLevel` | nein | `EAST-ADL::Elements::Context` | `atpStructureElement` | 3.2.1, pp. 20-21 | model-evidence |
| `EAST-ADL::SystemModeling` | `EAST-ADL::SystemModeling::DesignLevel` | nein | `EAST-ADL::Elements::Context` | `atpStructureElement` | 3.2.2, pp. 21-22 | model-evidence |
| `EAST-ADL::Behavior` | `EAST-ADL::Behavior::Mode` | nein | `EAST-ADL::Elements::EAElement` | keine | 9.2.5, p. 72 | model-evidence |
| `EAST-ADL::Behavior` | `EAST-ADL::Behavior::FunctionBehavior` | nein | `EAST-ADL::Elements::Context` | keine | 9.2.2, pp. 69-70 | model-evidence |
| `EAST-ADL::Behavior` | `EAST-ADL::Behavior::FunctionTrigger` | nein | `EAST-ADL::Values::EAExpression`<br>`EAST-ADL::Elements::EAElement` | keine | 9.2.4, pp. 71-72 | model-evidence |
| `EAST-ADL::Timing` | `EAST-ADL::Timing::TimingDescription` | ja | `EAST-ADL::Elements::EAElement` | keine | 14.2.6, p. 116 | model-evidence |
| `EAST-ADL::Timing` | `EAST-ADL::Timing::Event` | ja | `EAST-ADL::Timing::TimingDescription` | keine | 14.2.1, pp. 113-114 | model-evidence |
| `EAST-ADL::Events` | `EAST-ADL::Events::ExternalEvent` | nein | `EAST-ADL::Timing::Event` | keine | 16.2.8, p. 139 | model-evidence |
| `EAST-ADL::VerificationValidation` | `EAST-ADL::VerificationValidation::VerificationValidation` | nein | `EAST-ADL::Elements::Context` | keine | 13.2.1, p. 106 | model-evidence |
| `EAST-ADL::VerificationValidation` | `EAST-ADL::VerificationValidation::Verify` | nein | `EAST-ADL::Requirements::RequirementsRelationship` | keine | 13.2.2, pp. 106-107 | model-evidence |
| `EAST-ADL::VerificationValidation` | `EAST-ADL::VerificationValidation::VVActualOutcome` | nein | `EAST-ADL::Elements::TraceableSpecification` | keine | 13.2.3, p. 107 | model-evidence |
| `EAST-ADL::VerificationValidation` | `EAST-ADL::VerificationValidation::VVCase` | nein | `EAST-ADL::Elements::TraceableSpecification` | keine | 13.2.4, pp. 107-108 | model-evidence |
| `EAST-ADL::VerificationValidation` | `EAST-ADL::VerificationValidation::VVIntendedOutcome` | nein | `EAST-ADL::Elements::TraceableSpecification` | keine | 13.2.5, p. 108 | model-evidence |
| `EAST-ADL::VerificationValidation` | `EAST-ADL::VerificationValidation::VVLog` | nein | `EAST-ADL::Elements::TraceableSpecification` | keine | 13.2.6, pp. 108-109 | model-evidence |
| `EAST-ADL::VerificationValidation` | `EAST-ADL::VerificationValidation::VVProcedure` | nein | `EAST-ADL::Elements::TraceableSpecification` | keine | 13.2.7, pp. 109-110 | model-evidence |
| `EAST-ADL::VerificationValidation` | `EAST-ADL::VerificationValidation::VVStimuli` | nein | `EAST-ADL::Elements::TraceableSpecification` | keine | 13.2.8, p. 110 | model-evidence |
| `EAST-ADL::VerificationValidation` | `EAST-ADL::VerificationValidation::VVTarget` | nein | `EAST-ADL::Elements::TraceableSpecification` | keine | 13.2.9, pp. 110-111 | model-evidence |
| `EAST-ADL::AnnexC::BehaviorDescription` | `EAST-ADL::AnnexC::BehaviorDescription::BehaviorConstraintParameter` | ja | keine | keine | Annex C 30.2.4, p. 217 | model-evidence; optional-preliminary |
| `EAST-ADL::AnnexC::BehaviorDescription` | `EAST-ADL::AnnexC::BehaviorDescription::BehaviorConstraintType` | nein | `EAST-ADL::Elements::Context` | `atpType` | Annex C 30.2.7, pp. 219-220 | model-evidence; optional-preliminary |
| `EAST-ADL::AnnexC::BehaviorDescription` | `EAST-ADL::AnnexC::BehaviorDescription::BehaviorConstraintTargetBinding` | nein | `EAST-ADL::Elements::Relationship` | keine | Annex C 30.2.6, pp. 218-219 | model-evidence; optional-preliminary |
| `EAST-ADL::AnnexC::AttributeQuantificationConstraint` | `EAST-ADL::AnnexC::AttributeQuantificationConstraint::Quantification` | nein | `EAST-ADL::Elements::EAElement`<br>`EAST-ADL::Values::EAExpression` | keine | Annex C 31.2.5, pp. 223-224 | model-evidence; optional-preliminary |
| `EAST-ADL::AnnexC::ComputationConstraint` | `EAST-ADL::AnnexC::ComputationConstraint::LogicalPath` | nein | `EAST-ADL::Elements::EAElement` | keine | Annex C 32.2.2, pp. 226-227 | model-evidence; optional-preliminary |
| `EAST-ADL::AnnexC::ComputationConstraint` | `EAST-ADL::AnnexC::ComputationConstraint::LogicalTransformation` | nein | `EAST-ADL::Elements::EAElement` | keine | Annex C 32.2.3, pp. 227-228 | model-evidence; optional-preliminary |
| `EAST-ADL::AnnexC::ComputationConstraint` | `EAST-ADL::AnnexC::ComputationConstraint::TransformationOccurrence` | nein | `EAST-ADL::Elements::EAElement` | keine | Annex C 32.2.4, pp. 228-229 | model-evidence; optional-preliminary |
| `EAST-ADL::AnnexC::TemporalConstraint` | `EAST-ADL::AnnexC::TemporalConstraint::LogicalTimeCondition` | nein | `EAST-ADL::Elements::EAElement` | keine | Annex C 33.2.1, p. 232 | model-evidence; optional-preliminary |
| `EAST-ADL::AnnexC::TemporalConstraint` | `EAST-ADL::AnnexC::TemporalConstraint::State` | nein | `EAST-ADL::Elements::EAElement` | keine | Annex C 33.2.2, pp. 232-233 | model-evidence; optional-preliminary |
| `EAST-ADL::AnnexC::TemporalConstraint` | `EAST-ADL::AnnexC::TemporalConstraint::TransitionEvent` | nein | `EAST-ADL::Elements::EAElement`<br>`EAST-ADL::AnnexC::BehaviorDescription::BehaviorConstraintParameter` | keine | Annex C 33.2.7, p. 236 | model-evidence; optional-preliminary |
| `EAST-ADL::FeatureModeling` | `EAST-ADL::FeatureModeling::FeatureTreeNode` | ja | `EAST-ADL::Elements::Context` | keine | 4.2.8, p. 32 | model-evidence; optional-profile |
| `EAST-ADL::FeatureModeling` | `EAST-ADL::FeatureModeling::Feature` | nein | `EAST-ADL::FeatureModeling::FeatureTreeNode` | `atpStructureElement` | 4.2.3, pp. 28-29 | model-evidence; optional-profile |
| `EAST-ADL::VehicleFeatureModeling` | `EAST-ADL::VehicleFeatureModeling::VehicleFeature` | nein | `EAST-ADL::FeatureModeling::Feature` | keine | 5.2.3, pp. 38-39 | model-evidence; optional-profile |

## Lokal uebernommene Attribute

| Owner | Attribut | Typ | Multiplizitaet | Zusatz | PDF-Beleg | Status |
|---|---|---|---:|---|---|---|
| `EAST-ADL::Elements::Comment` | `body` | `String` | `1` | - | 25.2.1, pp. 188-189 | model-evidence |
| `EAST-ADL::Elements::Referrable` | `shortName` | `Identifier` | `1` | - | 25.2.14, p. 194 | model-evidence |
| `EAST-ADL::Elements::Identifiable` | `category` | `Identifier` | `0..1` | - | 25.2.11, pp. 192-193 | model-evidence |
| `EAST-ADL::Elements::Identifiable` | `uuid` | `String` | `0..1` | - | 25.2.11, pp. 192-193 | model-evidence |
| `EAST-ADL::Elements::EAElement` | `name` | `String` | `0..1` | - | 25.2.4, pp. 189-190 | model-evidence |
| `EAST-ADL::Elements::TraceableSpecification` | `text` | `String` | `0..1` | - | 25.2.16, p. 195 | model-evidence |
| `EAST-ADL::Datatypes::EANumerical` | `max` | `Numerical` | `0..1` | - | 23.2.6, pp. 178-179 | model-evidence |
| `EAST-ADL::Datatypes::EANumerical` | `min` | `Numerical` | `0..1` | - | 23.2.6, pp. 178-179 | model-evidence |
| `EAST-ADL::Values::EANumericalValue` | `value` | `Numerical` | `1` | - | 24.2.6, p. 185 | model-evidence |
| `EAST-ADL::Requirements::Requirement` | `formalism` | `String` | `0..1` | - | 11.2.6, pp. 94-95 | model-evidence |
| `EAST-ADL::Requirements::Requirement` | `url` | `String` | `0..1` | - | 11.2.6, pp. 94-95 | model-evidence |
| `EAST-ADL::FunctionModeling::FunctionType` | `isElementary` | `Boolean` | `1` | - | 6.2.19, p. 51 | model-evidence |
| `EAST-ADL::FunctionModeling::FunctionFlowPort` | `direction` | `EAST-ADL::FunctionModeling::EADirectionKind` | `1` | - | 6.2.15, pp. 48-49 | model-evidence |
| `EAST-ADL::Behavior::Mode` | `condition` | `String` | `1` | - | 9.2.5, p. 72 | model-evidence |
| `EAST-ADL::Behavior::FunctionBehavior` | `path` | `String` | `1` | - | 9.2.2, pp. 69-70 | model-evidence |
| `EAST-ADL::Behavior::FunctionBehavior` | `representation` | `EAST-ADL::Behavior::FunctionBehaviorKind` | `1` | - | 9.2.2, pp. 69-70 | model-evidence |
| `EAST-ADL::Behavior::FunctionTrigger` | `triggerPolicy` | `EAST-ADL::Behavior::TriggerPolicyKind` | `1` | - | 9.2.4, pp. 71-72 | model-evidence |
| `EAST-ADL::VerificationValidation::VVLog` | `date` | `String` | `1` | - | 13.2.6, pp. 108-109 | model-evidence |
| `EAST-ADL::AnnexC::ComputationConstraint::LogicalTransformation` | `isClientServerInterface` | `Boolean` | `1` | default=false | Annex C 32.2.3, pp. 227-228 | model-evidence |
| `EAST-ADL::AnnexC::TemporalConstraint::LogicalTimeCondition` | `isLogicalTimeSuspended` | `Boolean` | `1` | default=false | Annex C 33.2.1, p. 232 | model-evidence |
| `EAST-ADL::AnnexC::TemporalConstraint::State` | `isErrorState` | `Boolean` | `1` | default=false | Annex C 33.2.2, pp. 232-233 | model-evidence |
| `EAST-ADL::AnnexC::TemporalConstraint::State` | `isHazard` | `Boolean` | `1` | default=false | Annex C 33.2.2, pp. 232-233 | model-evidence |
| `EAST-ADL::AnnexC::TemporalConstraint::State` | `isInitState` | `Boolean` | `1` | default=false | Annex C 33.2.2, pp. 232-233 | model-evidence |
| `EAST-ADL::AnnexC::TemporalConstraint::State` | `isMode` | `Boolean` | `1` | default=false | Annex C 33.2.2, pp. 232-233 | model-evidence |
| `EAST-ADL::FeatureModeling::Feature` | `cardinality` | `String` | `1` | - | 4.2.3, pp. 28-29 | model-evidence |
| `EAST-ADL::VehicleFeatureModeling::VehicleFeature` | `isCustomerVisible` | `Boolean` | `1` | - | 5.2.3, pp. 38-39 | model-evidence |
| `EAST-ADL::VehicleFeatureModeling::VehicleFeature` | `isDesignVariabilityRationale` | `Boolean` | `1` | - | 5.2.3, pp. 38-39 | model-evidence |
| `EAST-ADL::VehicleFeatureModeling::VehicleFeature` | `isRemoved` | `Boolean` | `1` | - | 5.2.3, pp. 38-39 | model-evidence |

## Uebernommene EAST-ADL-Enumerationen

| Enumeration | Literale | PDF-Beleg | Status |
|---|---|---|---|
| `EAST-ADL::FunctionModeling::EADirectionKind` | `in`, `inout`, `out` | 6.2.9, p. 45 | model-evidence |
| `EAST-ADL::Behavior::FunctionBehaviorKind` | `ASCET`, `MARTE`, `OTHER`, `SCADE`, `SCILAB`, `SDL`, `SIMULINK`, `STATEMATE`, `UML` | 9.2.3, pp. 70-71 | model-evidence |
| `EAST-ADL::Behavior::TriggerPolicyKind` | `EVENT`, `TIME` | 9.2.7, p. 74 | model-evidence |

## Assoziationen und Multiplizitaeten

Die Zielrolle und Zielmultiplizitaet geben die navigierbare EAST-ADL-Deklaration wieder. Wo die Spezifikation keine benannte Gegenrolle angibt, ist die Quellenmultiplizitaet lediglich die inverse Werkzeugdarstellung und fuegt keine EAST-ADL-Semantik hinzu.

| ID | Quelle | Ziel | Quellenende | Zielende | Eigenschaften | PDF-Beleg | Status |
|---|---|---|---|---|---|---|---|
| `EAElement_ownedComment` | `EAST-ADL::Elements::EAElement` | `EAST-ADL::Elements::Comment` | `commentOwner` `[1]` | `ownedComment` `[*]` | composite | 25.2.4, pp. 189-190 | model-evidence |
| `Context_ownedRelationship` | `EAST-ADL::Elements::Context` | `EAST-ADL::Elements::Relationship` | `owningContext` `[1]` | `ownedRelationship` `[*]` | composite | 25.2.2, p. 189 | model-evidence |
| `Context_traceableSpecification` | `EAST-ADL::Elements::Context` | `EAST-ADL::Elements::TraceableSpecification` | `context` `[*]` | `traceableSpecification` `[*]` | - | 25.2.2, p. 189 | model-evidence |
| `EADatatypePrototype_type` | `EAST-ADL::Datatypes::EADatatypePrototype` | `EAST-ADL::Datatypes::EADatatype` | `typedPrototype` `[*]` | `type` `[1]` | <<isOfType>> | 23.2.5, p. 178 | model-evidence |
| `EAValue_type` | `EAST-ADL::Values::EAValue` | `EAST-ADL::Datatypes::EADatatype` | `typedValue` `[*]` | `type` `[1]` | <<isOfType>> | 24.2.8, p. 186 | model-evidence |
| `Requirement_mode` | `EAST-ADL::Requirements::Requirement` | `EAST-ADL::Behavior::Mode` | `validRequirement` `[*]` | `mode` `[*]` | - | 11.2.6, p. 95 | model-evidence |
| `RequirementsModel_requirement` | `EAST-ADL::Requirements::RequirementsModel` | `EAST-ADL::Requirements::Requirement` | `requirementsModel` `[1]` | `requirement` `[*]` | composite | 11.2.9, p. 97 | model-evidence |
| `RequirementsModel_useCase` | `EAST-ADL::Requirements::RequirementsModel` | `EAST-ADL::UseCases::UseCase` | `requirementsModel` `[1]` | `useCase` `[*]` | composite | 11.2.9, p. 97 | model-evidence |
| `Satisfy_satisfiedRequirement` | `EAST-ADL::Requirements::Satisfy` | `EAST-ADL::Requirements::Requirement` | `satisfy` `[*]` | `satisfiedRequirement` `[*]` | - | 11.2.12, pp. 98-99 | model-evidence |
| `Refine_refinedRequirement` | `EAST-ADL::Requirements::Refine` | `EAST-ADL::Requirements::Requirement` | `refine` `[*]` | `refinedRequirement` `[1..*]` | - | 11.2.5, p. 94 | model-evidence |
| `Refine_refinedBy` | `EAST-ADL::Requirements::Refine` | `EAST-ADL::Elements::EAElement` | `refine` `[*]` | `refinedBy` `[1..*]` | <<instanceRef>> | 11.2.5, p. 94 | model-evidence |
| `Satisfy_satisfiedUseCase` | `EAST-ADL::Requirements::Satisfy` | `EAST-ADL::UseCases::UseCase` | `satisfy` `[*]` | `satisfiedUseCase` `[*]` | - | 11.2.12, pp. 98-99 | model-evidence |
| `Satisfy_satisfiedBy` | `EAST-ADL::Requirements::Satisfy` | `EAST-ADL::Elements::Identifiable` | `satisfy` `[*]` | `satisfiedBy` `[1..*]` | <<instanceRef>> | 11.2.12, pp. 98-99 | model-evidence |
| `UseCase_extensionPoint` | `EAST-ADL::UseCases::UseCase` | `EAST-ADL::UseCases::ExtensionPoint` | `useCase` `[1]` | `extensionPoint` `[*]` | composite | 12.2.6, p. 103 | model-evidence |
| `UseCase_include` | `EAST-ADL::UseCases::UseCase` | `EAST-ADL::UseCases::Include` | `includingUseCase` `[1]` | `include` `[*]` | composite | 12.2.6, p. 103 | model-evidence |
| `UseCase_extend` | `EAST-ADL::UseCases::UseCase` | `EAST-ADL::UseCases::Extend` | `extendingUseCase` `[1]` | `extend` `[*]` | composite | 12.2.6, p. 103 | model-evidence |
| `Include_addition` | `EAST-ADL::UseCases::Include` | `EAST-ADL::UseCases::UseCase` | `include` `[*]` | `addition` `[1]` | - | 12.2.4, p. 102 | model-evidence |
| `Extend_extendedCase` | `EAST-ADL::UseCases::Extend` | `EAST-ADL::UseCases::UseCase` | `extend` `[*]` | `extendedCase` `[1]` | - | 12.2.2, pp. 101-102 | model-evidence |
| `Extend_extensionLocation` | `EAST-ADL::UseCases::Extend` | `EAST-ADL::UseCases::ExtensionPoint` | `extend` `[*]` | `extensionLocation` `[1..*]` | - | 12.2.2, pp. 101-102 | model-evidence |
| `FunctionConnector_port` | `EAST-ADL::FunctionModeling::FunctionConnector` | `EAST-ADL::FunctionModeling::FunctionPort` | `functionConnector` `[*]` | `port` `[2]` | <<instanceRef>> | 6.2.14, pp. 47-48 | model-evidence |
| `FunctionType_port` | `EAST-ADL::FunctionModeling::FunctionType` | `EAST-ADL::FunctionModeling::FunctionPort` | `functionType` `[1]` | `port` `[*]` | composite | 6.2.19, p. 51 | model-evidence |
| `FunctionType_connector` | `EAST-ADL::FunctionModeling::FunctionType` | `EAST-ADL::FunctionModeling::FunctionConnector` | `functionType` `[1]` | `connector` `[*]` | composite | 6.2.19, p. 51 | model-evidence |
| `FunctionType_portGroup` | `EAST-ADL::FunctionModeling::FunctionType` | `EAST-ADL::FunctionModeling::PortGroup` | `functionType` `[1]` | `portGroup` `[*]` | composite | 6.2.19, p. 51 | model-evidence |
| `PortGroup_port` | `EAST-ADL::FunctionModeling::PortGroup` | `EAST-ADL::FunctionModeling::FunctionPort` | `portGroup` `[*]` | `port` `[*]` | - | 6.2.23, p. 54 | model-evidence |
| `PortGroup_portGroup` | `EAST-ADL::FunctionModeling::PortGroup` | `EAST-ADL::FunctionModeling::PortGroup` | `parentPortGroup` `[0..1]` | `portGroup` `[*]` | composite | 6.2.23, p. 54 | model-evidence |
| `AnalysisFunctionPrototype_type` | `EAST-ADL::FunctionModeling::AnalysisFunctionPrototype` | `EAST-ADL::FunctionModeling::AnalysisFunctionType` | `typedPrototype` `[*]` | `type` `[1]` | <<isOfType>> | 6.2.3, p. 42 | model-evidence |
| `AnalysisFunctionType_part` | `EAST-ADL::FunctionModeling::AnalysisFunctionType` | `EAST-ADL::FunctionModeling::AnalysisFunctionPrototype` | `analysisFunctionType` `[1]` | `part` `[*]` | composite | 6.2.4, pp. 42-43 | model-evidence |
| `DesignFunctionPrototype_type` | `EAST-ADL::FunctionModeling::DesignFunctionPrototype` | `EAST-ADL::FunctionModeling::DesignFunctionType` | `typedPrototype` `[*]` | `type` `[1]` | <<isOfType>> | 6.2.7, p. 44 | model-evidence |
| `DesignFunctionType_part` | `EAST-ADL::FunctionModeling::DesignFunctionType` | `EAST-ADL::FunctionModeling::DesignFunctionPrototype` | `designFunctionType` `[1]` | `part` `[*]` | composite | 6.2.8, pp. 44-45 | model-evidence |
| `AnalysisLevel_functionalAnalysisArchitecture` | `EAST-ADL::SystemModeling::AnalysisLevel` | `EAST-ADL::FunctionModeling::AnalysisFunctionPrototype` | `analysisLevel` `[1]` | `functionalAnalysisArchitecture` `[0..1]` | composite | 3.2.1, pp. 20-21 | model-evidence |
| `DesignLevel_functionalDesignArchitecture` | `EAST-ADL::SystemModeling::DesignLevel` | `EAST-ADL::FunctionModeling::DesignFunctionPrototype` | `designLevel` `[1]` | `functionalDesignArchitecture` `[0..1]` | composite | 3.2.2, pp. 21-22 | model-evidence |
| `FunctionBehavior_function` | `EAST-ADL::Behavior::FunctionBehavior` | `EAST-ADL::FunctionModeling::FunctionType` | `functionBehavior` `[*]` | `function` `[0..1]` | - | 9.2.2, pp. 69-70 | model-evidence |
| `FunctionBehavior_mode` | `EAST-ADL::Behavior::FunctionBehavior` | `EAST-ADL::Behavior::Mode` | `functionBehavior` `[*]` | `mode` `[*]` | - | 9.2.2, pp. 69-70 | model-evidence |
| `VerificationValidation_vvTarget` | `EAST-ADL::VerificationValidation::VerificationValidation` | `EAST-ADL::VerificationValidation::VVTarget` | `verificationValidation` `[1]` | `vvTarget` `[*]` | composite | 13.2.1, p. 106 | model-evidence |
| `VerificationValidation_vvCase` | `EAST-ADL::VerificationValidation::VerificationValidation` | `EAST-ADL::VerificationValidation::VVCase` | `verificationValidation` `[1]` | `vvCase` `[*]` | composite | 13.2.1, p. 106 | model-evidence |
| `VerificationValidation_verify` | `EAST-ADL::VerificationValidation::VerificationValidation` | `EAST-ADL::VerificationValidation::Verify` | `verificationValidation` `[1]` | `verify` `[*]` | composite | 13.2.1, p. 106 | model-evidence |
| `Verify_verifiedRequirement` | `EAST-ADL::VerificationValidation::Verify` | `EAST-ADL::Requirements::Requirement` | `verify` `[*]` | `verifiedRequirement` `[1..*]` | - | 13.2.2, pp. 106-107 | model-evidence |
| `Verify_verifiedByProcedure` | `EAST-ADL::VerificationValidation::Verify` | `EAST-ADL::VerificationValidation::VVProcedure` | `verify` `[*]` | `verifiedByProcedure` `[*]` | - | 13.2.2, pp. 106-107 | model-evidence |
| `Verify_verifiedByCase` | `EAST-ADL::VerificationValidation::Verify` | `EAST-ADL::VerificationValidation::VVCase` | `verify` `[*]` | `verifiedByCase` `[1..*]` | - | 13.2.2, pp. 106-107 | model-evidence |
| `VVActualOutcome_intendedOutcome` | `EAST-ADL::VerificationValidation::VVActualOutcome` | `EAST-ADL::VerificationValidation::VVIntendedOutcome` | `actualOutcome` `[*]` | `intendedOutcome` `[0..1]` | - | 13.2.3, p. 107 | model-evidence |
| `VVCase_vvProcedure` | `EAST-ADL::VerificationValidation::VVCase` | `EAST-ADL::VerificationValidation::VVProcedure` | `vvCase` `[1]` | `vvProcedure` `[*]` | composite, ordered | 13.2.4, pp. 107-108 | model-evidence |
| `VVCase_vvTarget` | `EAST-ADL::VerificationValidation::VVCase` | `EAST-ADL::VerificationValidation::VVTarget` | `vvCase` `[*]` | `vvTarget` `[*]` | - | 13.2.4, pp. 107-108 | model-evidence |
| `VVCase_vvLog` | `EAST-ADL::VerificationValidation::VVCase` | `EAST-ADL::VerificationValidation::VVLog` | `vvCase` `[1]` | `vvLog` `[*]` | composite | 13.2.4, pp. 107-108 | model-evidence |
| `VVCase_abstractVVCase` | `EAST-ADL::VerificationValidation::VVCase` | `EAST-ADL::VerificationValidation::VVCase` | `concreteVVCase` `[*]` | `abstractVVCase` `[0..1]` | - | 13.2.4, pp. 107-108 | model-evidence |
| `VVCase_vvSubject` | `EAST-ADL::VerificationValidation::VVCase` | `EAST-ADL::Elements::Identifiable` | `vvCase` `[*]` | `vvSubject` `[*]` | <<instanceRef>> | 13.2.4, pp. 107-108 | model-evidence |
| `VVLog_performedVVProcedure` | `EAST-ADL::VerificationValidation::VVLog` | `EAST-ADL::VerificationValidation::VVProcedure` | `vvLog` `[*]` | `performedVVProcedure` `[1]` | - | 13.2.6, pp. 108-109 | model-evidence |
| `VVLog_vvActualOutcome` | `EAST-ADL::VerificationValidation::VVLog` | `EAST-ADL::VerificationValidation::VVActualOutcome` | `vvLog` `[1]` | `vvActualOutcome` `[*]` | composite | 13.2.6, pp. 108-109 | model-evidence |
| `VVProcedure_abstractVVProcedure` | `EAST-ADL::VerificationValidation::VVProcedure` | `EAST-ADL::VerificationValidation::VVProcedure` | `concreteVVProcedure` `[*]` | `abstractVVProcedure` `[0..1]` | - | 13.2.7, pp. 109-110 | model-evidence |
| `VVProcedure_vvStimuli` | `EAST-ADL::VerificationValidation::VVProcedure` | `EAST-ADL::VerificationValidation::VVStimuli` | `vvProcedure` `[1]` | `vvStimuli` `[*]` | composite | 13.2.7, pp. 109-110 | model-evidence |
| `VVProcedure_vvIntendedOutcome` | `EAST-ADL::VerificationValidation::VVProcedure` | `EAST-ADL::VerificationValidation::VVIntendedOutcome` | `vvProcedure` `[1]` | `vvIntendedOutcome` `[*]` | composite | 13.2.7, pp. 109-110 | model-evidence |
| `VVTarget_element` | `EAST-ADL::VerificationValidation::VVTarget` | `EAST-ADL::Elements::Identifiable` | `vvTarget` `[*]` | `element` `[*]` | <<instanceRef>> | 13.2.9, pp. 110-111 | model-evidence |
| `BehaviorConstraintTargetBinding_behaviorConstraintType` | `EAST-ADL::AnnexC::BehaviorDescription::BehaviorConstraintTargetBinding` | `EAST-ADL::AnnexC::BehaviorDescription::BehaviorConstraintType` | `targetBinding` `[*]` | `behaviorConstraintType` `[1]` | optional | Annex C 30.2.6, pp. 218-219 | model-evidence; optional-preliminary |
| `BehaviorConstraintTargetBinding_targetedFunctionType` | `EAST-ADL::AnnexC::BehaviorDescription::BehaviorConstraintTargetBinding` | `EAST-ADL::FunctionModeling::FunctionType` | `targetBinding` `[*]` | `targetedFunctionType` `[*]` | optional | Annex C 30.2.6, pp. 218-219 | model-evidence; optional-preliminary |
| `BehaviorConstraintTargetBinding_targetedVehicleFeature` | `EAST-ADL::AnnexC::BehaviorDescription::BehaviorConstraintTargetBinding` | `EAST-ADL::VehicleFeatureModeling::VehicleFeature` | `targetBinding` `[*]` | `targetedVehicleFeature` `[*]` | optional | Annex C 30.2.6, pp. 218-219 | model-evidence; optional-preliminary |
| `BehaviorConstraintTargetBinding_constrainedModeBehavior` | `EAST-ADL::AnnexC::BehaviorDescription::BehaviorConstraintTargetBinding` | `EAST-ADL::Behavior::Mode` | `targetBinding` `[*]` | `constrainedModeBehavior` `[*]` | optional | Annex C 30.2.6, pp. 218-219 | model-evidence; optional-preliminary |
| `BehaviorConstraintTargetBinding_constrainedFunctionBehavior` | `EAST-ADL::AnnexC::BehaviorDescription::BehaviorConstraintTargetBinding` | `EAST-ADL::Behavior::FunctionBehavior` | `targetBinding` `[*]` | `constrainedFunctionBehavior` `[*]` | optional | Annex C 30.2.6, pp. 218-219 | model-evidence; optional-preliminary |
| `BehaviorConstraintTargetBinding_constrainedFunctionTriggering` | `EAST-ADL::AnnexC::BehaviorDescription::BehaviorConstraintTargetBinding` | `EAST-ADL::Behavior::FunctionTrigger` | `targetBinding` `[*]` | `constrainedFunctionTriggering` `[*]` | optional | Annex C 30.2.6, pp. 218-219 | model-evidence; optional-preliminary |
| `LogicalPath_segment` | `EAST-ADL::AnnexC::ComputationConstraint::LogicalPath` | `EAST-ADL::AnnexC::ComputationConstraint::LogicalPath` | `logicalPath` `[*]` | `segment` `[*]` | ordered, optional | Annex C 32.2.2, pp. 226-227 | model-evidence; optional-preliminary |
| `LogicalPath_strand` | `EAST-ADL::AnnexC::ComputationConstraint::LogicalPath` | `EAST-ADL::AnnexC::ComputationConstraint::LogicalPath` | `logicalPath` `[*]` | `strand` `[*]` | optional | Annex C 32.2.2, pp. 226-227 | model-evidence; optional-preliminary |
| `LogicalPath_transformationOccurrence` | `EAST-ADL::AnnexC::ComputationConstraint::LogicalPath` | `EAST-ADL::AnnexC::ComputationConstraint::TransformationOccurrence` | `logicalPath` `[1]` | `transformationOccurrence` `[0..1]` | composite, optional | Annex C 32.2.2, pp. 226-227 | model-evidence; optional-preliminary |
| `TransformationOccurrence_invokedLogicalTransformation` | `EAST-ADL::AnnexC::ComputationConstraint::TransformationOccurrence` | `EAST-ADL::AnnexC::ComputationConstraint::LogicalTransformation` | `transformationOccurrence` `[*]` | `invokedLogicalTransformation` `[1]` | optional | Annex C 32.2.4, pp. 228-229 | model-evidence; optional-preliminary |
| `TransitionEvent_occurredExecutionEvent` | `EAST-ADL::AnnexC::TemporalConstraint::TransitionEvent` | `EAST-ADL::Timing::Event` | `transitionEvent` `[*]` | `occurredExecutionEvent` `[*]` | optional | Annex C 33.2.7, p. 236 | model-evidence; optional-preliminary |
| `FunctionFlowPort_type` | `EAST-ADL::FunctionModeling::FunctionFlowPort` | `EAST-ADL::Datatypes::EADatatype` | `typedPort` `[*]` | `type` `[1]` | <<isOfType>> | 6.2.15, pp. 48-49 | model-evidence |
| `FunctionFlowPort_defaultValue` | `EAST-ADL::FunctionModeling::FunctionFlowPort` | `EAST-ADL::Values::EAValue` | `functionFlowPort` `[1]` | `defaultValue` `[0..1]` | composite | 6.2.15, pp. 48-49 | model-evidence |
| `FunctionTrigger_port` | `EAST-ADL::Behavior::FunctionTrigger` | `EAST-ADL::FunctionModeling::FunctionPort` | `functionTrigger` `[*]` | `port` `[*]` | - | 9.2.4, pp. 71-72 | model-evidence |
| `FunctionTrigger_function` | `EAST-ADL::Behavior::FunctionTrigger` | `EAST-ADL::FunctionModeling::FunctionType` | `functionTrigger` `[*]` | `function` `[0..1]` | - | 9.2.4, pp. 71-72 | model-evidence |
| `FunctionTrigger_functionPrototype` | `EAST-ADL::Behavior::FunctionTrigger` | `EAST-ADL::FunctionModeling::FunctionPrototype` | `functionTrigger` `[*]` | `functionPrototype` `[0..1]` | - | 9.2.4, pp. 71-72 | model-evidence |
| `FunctionTrigger_mode` | `EAST-ADL::Behavior::FunctionTrigger` | `EAST-ADL::Behavior::Mode` | `functionTrigger` `[*]` | `mode` `[*]` | - | 9.2.4, pp. 71-72 | model-evidence |

## Semantische Leitplanken des Ausschnitts

- TraceableSpecification has only local text:String[0..1]; Requirement and UseCase inherit it.
- EAType, EAPrototype, EAPort and EAConnector have no EAST-ADL generalization in this version.
- EAValue is non-identifiable and is typed by EADatatype[1].
- FAA and FDA are architecture roles on AnalysisLevel and DesignLevel, not metaclasses.
- VVCase.vvSubject and VVTarget.element are semantically distinct.
- VVActualOutcome is composed under VVLog, never directly under VVCase or VVProcedure.
- Annex C TransitionEvent is EAElement plus BehaviorConstraintParameter and only associates to Timing::Event.

## Grenzen des Belegs

Die Matrix belegt ausschliesslich die Deklarationen, die aus der kanonischen V2-Modellquelle enumeriert wurden. Sie behauptet keine Volluebernahme aller EAST-ADL-Pakete und keine Ausfuehrung einer Annex-C-Projektion. Annex C ist laut S. 212 vorlaeufig und noch nicht fuer die Basisspezifikation validiert. Die optionale VehicleFeature-Abbildung ist nur fuer passende Automotive-Profile vorgesehen.

Maschinenlesbare Fassung: `output/metamodel_v2/evidence/east_adl_conformance_matrix.json`.
