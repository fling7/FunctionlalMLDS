from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_dynamic_functional_mlds_v2 import (  # noqa: E402
    main as validator_main,
    validate_instance,
    validate_model,
    write_reports,
)


EAST = "EAST-ADL::Core"
DFMLDS = "DFMLDS::V2"
ANNEX = "EAST-ADL::AnnexC"


def attr(name: str, type_name: str, multiplicity: str = "1", **extra):
    return {"name": name, "type": type_name, "multiplicity": multiplicity, **extra}


def cls(name: str, package: str = EAST, bases=(), attributes=(), abstract: bool = False):
    return {
        "name": name,
        "package": package,
        "abstract": abstract,
        "bases": list(bases),
        "attributes": list(attributes),
    }


def assoc(
    assoc_id: str,
    source: str,
    target: str,
    target_role: str,
    target_multiplicity: str = "0..*",
    *,
    package: str = DFMLDS,
    source_role: str = "owner",
    source_multiplicity: str = "1",
    composition: bool = False,
    ordered: bool = False,
    stereotype: str = "",
):
    return {
        "id": assoc_id,
        "package": package,
        "source": source,
        "target": target,
        "source_role": source_role,
        "target_role": target_role,
        "source_multiplicity": source_multiplicity,
        "target_multiplicity": target_multiplicity,
        "composition": composition,
        "owner": "source" if composition else None,
        "ordered": ordered,
        "stereotype": stereotype,
    }


def full_surface_model():
    classes = {
        "EAST-ADL::Core::Referrable": cls("Referrable", attributes=[attr("shortName", "Identifier")], abstract=True),
        "EAST-ADL::Core::Identifiable": cls(
            "Identifiable", bases=["Referrable"],
            attributes=[attr("category", "Identifier", "0..1"), attr("uuid", "String", "0..1")], abstract=True,
        ),
        "EAST-ADL::Core::EAElement": cls("EAElement", bases=["Identifiable"], attributes=[attr("name", "String", "0..1")], abstract=True),
        "EAST-ADL::Core::EAPackageableElement": cls("EAPackageableElement", bases=["EAElement"], abstract=True),
        "EAST-ADL::Core::Context": cls("Context", bases=["EAPackageableElement"], abstract=True),
        "EAST-ADL::Core::Relationship": cls("Relationship", bases=["EAElement"], abstract=True),
        "EAST-ADL::Core::RequirementsRelationship": cls("RequirementsRelationship", bases=["Relationship"], abstract=True),
        "EAST-ADL::Core::RedefinableElement": cls("RedefinableElement", bases=["EAElement"], abstract=True),
        "EAST-ADL::Core::TraceableSpecification": cls(
            "TraceableSpecification", bases=["EAPackageableElement"], attributes=[attr("text", "String", "0..1")], abstract=True,
        ),
        "EAST-ADL::Core::EAType": cls("EAType", abstract=True),
        "EAST-ADL::Core::EAPrototype": cls("EAPrototype", abstract=True),
        "EAST-ADL::Core::EAPort": cls("EAPort", abstract=True),
        "EAST-ADL::Core::EAConnector": cls("EAConnector", abstract=True),
        "EAST-ADL::Core::AllocateableElement": cls("AllocateableElement", bases=["EAElement"], abstract=True),
        "EAST-ADL::Core::Mode": cls("Mode", bases=["EAElement"], attributes=[attr("condition", "String")]),
        "EAST-ADL::Core::RequirementsModel": cls("RequirementsModel", bases=["Context"]),
        "EAST-ADL::Core::Requirement": cls(
            "Requirement", bases=["TraceableSpecification"],
            attributes=[attr("formalism", "String", "0..1"), attr("url", "String", "0..1"), attr("mode", "Mode", "0..*")],
        ),
        "EAST-ADL::Core::RequirementContainer": cls("RequirementContainer", bases=["TraceableSpecification"]),
        "EAST-ADL::Core::Actor": cls("Actor", bases=["TraceableSpecification"]),
        "EAST-ADL::Core::UseCase": cls("UseCase", bases=["TraceableSpecification"]),
        "EAST-ADL::Core::ExtensionPoint": cls("ExtensionPoint", bases=["RedefinableElement"]),
        "EAST-ADL::Core::Include": cls("Include", bases=["Relationship"]),
        "EAST-ADL::Core::Extend": cls("Extend", bases=["Relationship"]),
        "EAST-ADL::Core::Satisfy": cls("Satisfy", bases=["RequirementsRelationship"]),
        "EAST-ADL::Core::EADatatype": cls("EADatatype", bases=["TraceableSpecification"], abstract=True),
        "EAST-ADL::Core::EABoolean": cls("EABoolean", bases=["EADatatype"]),
        "EAST-ADL::Core::EAValue": cls("EAValue", attributes=[attr("type", "EADatatype")], abstract=True),
        "EAST-ADL::Core::EAExpression": cls("EAExpression", bases=["EAValue"], abstract=True),
        "EAST-ADL::Core::EANumericalValue": cls("EANumericalValue", bases=["EAValue"], attributes=[attr("value", "Numerical")]),
        "EAST-ADL::Core::EANumerical": cls(
            "EANumerical", bases=["EADatatype"],
            attributes=[attr("min", "Numerical", "0..1"), attr("max", "Numerical", "0..1")],
        ),
        "EAST-ADL::Core::FunctionType": cls("FunctionType", bases=["EAType", "Context"], attributes=[attr("isElementary", "Boolean")], abstract=True),
        "EAST-ADL::Core::FunctionPrototype": cls("FunctionPrototype", bases=["EAElement", "EAPrototype"], abstract=True),
        "EAST-ADL::Core::FunctionPort": cls("FunctionPort", bases=["EAPort", "EAElement"]),
        "EAST-ADL::Core::FunctionConnector": cls("FunctionConnector", bases=["AllocateableElement", "EAConnector", "EAElement"]),
        "EAST-ADL::Core::AnalysisFunctionType": cls("AnalysisFunctionType", bases=["FunctionType"]),
        "EAST-ADL::Core::AnalysisFunctionPrototype": cls("AnalysisFunctionPrototype", bases=["FunctionPrototype"], attributes=[attr("type", "AnalysisFunctionType")]),
        "EAST-ADL::Core::DesignFunctionType": cls("DesignFunctionType", bases=["FunctionType"]),
        "EAST-ADL::Core::DesignFunctionPrototype": cls("DesignFunctionPrototype", bases=["FunctionPrototype", "AllocateableElement"], attributes=[attr("type", "DesignFunctionType")]),
        "EAST-ADL::Core::AnalysisLevel": cls("AnalysisLevel", bases=["Context"], attributes=[attr("functionalAnalysisArchitecture", "AnalysisFunctionPrototype", "0..1")]),
        "EAST-ADL::Core::DesignLevel": cls("DesignLevel", bases=["Context"], attributes=[attr("functionalDesignArchitecture", "DesignFunctionPrototype", "0..1")]),
        "EAST-ADL::Core::FunctionBehavior": cls(
            "FunctionBehavior", bases=["Context"],
            attributes=[
                attr("path", "String"), attr("representation", "FunctionBehaviorKind"),
                attr("function", "FunctionType", "0..1"), attr("mode", "Mode", "0..*"),
            ],
        ),
        "EAST-ADL::Core::TimingDescription": cls("TimingDescription", bases=["EAElement"], abstract=True),
        "EAST-ADL::Core::Event": cls("Event", bases=["TimingDescription"], abstract=True),
        "EAST-ADL::Core::ExternalEvent": cls("ExternalEvent", bases=["Event"]),
        "EAST-ADL::Core::VerificationValidation": cls("VerificationValidation", bases=["Context"]),
        "EAST-ADL::Core::VVCase": cls("VVCase", bases=["TraceableSpecification"], abstract=True),
        "EAST-ADL::Core::VVProcedure": cls("VVProcedure", bases=["TraceableSpecification"], abstract=True),
        "EAST-ADL::Core::VVStimuli": cls("VVStimuli", bases=["TraceableSpecification"], abstract=True),
        "EAST-ADL::Core::VVIntendedOutcome": cls("VVIntendedOutcome", bases=["TraceableSpecification"], abstract=True),
        "EAST-ADL::Core::VVActualOutcome": cls("VVActualOutcome", bases=["TraceableSpecification"], abstract=True),
        "EAST-ADL::Core::VVTarget": cls("VVTarget", bases=["TraceableSpecification"], abstract=True),
        "EAST-ADL::Core::VVLog": cls("VVLog", bases=["TraceableSpecification"], abstract=True),
        "EAST-ADL::Core::Verify": cls("Verify", bases=["RequirementsRelationship"]),
        "EAST-ADL::Core::FeatureTreeNode": cls("FeatureTreeNode", bases=["Context"]),
        "DFMLDS::V2::DynamicFunctionalModel": cls("DynamicFunctionalModel", DFMLDS, ["Context"]),
        "DFMLDS::V2::Scenario": cls("Scenario", DFMLDS, ["TraceableSpecification"], [attr("kind", "ScenarioKind")]),
        "DFMLDS::V2::ScenarioStep": cls(
            "ScenarioStep", DFMLDS, ["TraceableSpecification"],
            [attr("stepNumber", "Integer", derived=True), attr("occurrenceProbability", "Probability", "0..1")],
        ),
        "DFMLDS::V2::StepRelation": cls("StepRelation", DFMLDS, ["Relationship"], [attr("kind", "StepRelationKind"), attr("probability", "Probability", "0..1")]),
        "DFMLDS::V2::ParallelGroup": cls("ParallelGroup", DFMLDS, ["EAElement"]),
        "DFMLDS::V2::UseCaseScenarioSpecification": cls("UseCaseScenarioSpecification", DFMLDS, ["Relationship"]),
        "DFMLDS::V2::ActorParticipation": cls("ActorParticipation", DFMLDS, ["Relationship"]),
        "DFMLDS::V2::ConditionalExtend": cls("ConditionalExtend", DFMLDS, ["Extend"]),
        "DFMLDS::V2::ScenarioEvent": cls("ScenarioEvent", DFMLDS, ["Event", "EAExpression"]),
        "DFMLDS::V2::ScenarioExternalEvent": cls("ScenarioExternalEvent", DFMLDS, ["ScenarioEvent", "ExternalEvent"]),
        "DFMLDS::V2::ScenarioCondition": cls("ScenarioCondition", DFMLDS, ["EAExpression", "EAElement"], [attr("kind", "ConditionKind")]),
        "DFMLDS::V2::Assertion": cls("Assertion", DFMLDS, ["TraceableSpecification"], [attr("severity", "AssertionSeverity", "0..1")], abstract=True),
        "DFMLDS::V2::StateAssertion": cls("StateAssertion", DFMLDS, ["Assertion"]),
        "DFMLDS::V2::EventAssertion": cls("EventAssertion", DFMLDS, ["Assertion"]),
        "DFMLDS::V2::OutputAssertion": cls("OutputAssertion", DFMLDS, ["Assertion"]),
        "DFMLDS::V2::GroundingAssertion": cls("GroundingAssertion", DFMLDS, ["Assertion"]),
        "DFMLDS::V2::RelationAssertion": cls("RelationAssertion", DFMLDS, ["Assertion"]),
        "DFMLDS::V2::Entity": cls("Entity", DFMLDS, ["TraceableSpecification"], [attr("kind", "EntityKind")]),
        "DFMLDS::V2::Agent": cls("Agent", DFMLDS, ["Entity"]),
        "DFMLDS::V2::Capability": cls("Capability", DFMLDS, ["EAType", "TraceableSpecification"]),
        "DFMLDS::V2::CapabilityUse": cls("CapabilityUse", DFMLDS, ["EAPrototype", "EAElement"]),
        "DFMLDS::V2::Effect": cls("Effect", DFMLDS, ["TraceableSpecification"]),
        "DFMLDS::V2::RuntimeBinding": cls("RuntimeBinding", DFMLDS, ["Relationship"]),
        "DFMLDS::V2::RuntimeAction": cls("RuntimeAction", DFMLDS, ["EAElement"]),
        "DFMLDS::V2::RuntimeActionLocator": cls("RuntimeActionLocator", DFMLDS, ["EAElement"], [attr("kind", "RuntimeLocatorKind"), attr("value", "String")]),
        "DFMLDS::V2::SchemaReference": cls("SchemaReference", DFMLDS, ["TraceableSpecification"]),
        "DFMLDS::V2::KeyValueParameter": cls("KeyValueParameter", DFMLDS, ["EAElement"], [attr("key", "String")]),
        "DFMLDS::V2::ParameterBinding": cls("ParameterBinding", DFMLDS, ["Relationship"]),
        "DFMLDS::V2::ValidationCase": cls("ValidationCase", DFMLDS, ["VVCase"]),
        "DFMLDS::V2::RuntimeValidationProcedure": cls("RuntimeValidationProcedure", DFMLDS, ["VVProcedure"]),
        "DFMLDS::V2::RuntimeStimulus": cls("RuntimeStimulus", DFMLDS, ["VVStimuli"]),
        "DFMLDS::V2::AssertionOutcome": cls("AssertionOutcome", DFMLDS, ["VVIntendedOutcome"], abstract=True),
        "DFMLDS::V2::StateAssertionOutcome": cls("StateAssertionOutcome", DFMLDS, ["AssertionOutcome"]),
        "DFMLDS::V2::AssertionResult": cls(
            "AssertionResult", DFMLDS, ["EAElement"],
            [attr("verdict", "AssertionVerdict"), attr("evidenceRef", "String", "0..1"), attr("timestamp", "String", "0..1")],
        ),
        "DFMLDS::V2::RuntimeActualOutcome": cls("RuntimeActualOutcome", DFMLDS, ["VVActualOutcome"]),
        "DFMLDS::V2::RuntimeValidationTarget": cls(
            "RuntimeValidationTarget", DFMLDS, ["VVTarget"],
            [attr("platform", "String"), attr("environmentRef", "String", "0..1")],
        ),
        "DFMLDS::V2::RuntimeValidationLog": cls("RuntimeValidationLog", DFMLDS, ["VVLog"]),
        "DFMLDS::V2::ValidationCaseUseCaseBinding": cls("ValidationCaseUseCaseBinding", DFMLDS, ["Relationship"]),
        "EAST-ADL::AnnexC::BehaviorConstraintParameter": cls("BehaviorConstraintParameter", ANNEX, ["EAElement"], abstract=True),
        "EAST-ADL::AnnexC::TransitionEvent": cls("TransitionEvent", ANNEX, ["EAElement", "BehaviorConstraintParameter"]),
    }

    enums = {
        "FunctionBehaviorKind": {"name": "FunctionBehaviorKind", "package": EAST, "literals": ["behavior", "implementation"]},
        "ScenarioKind": {"name": "ScenarioKind", "package": DFMLDS, "literals": ["main", "alternative", "exception"]},
        "StepRelationKind": {"name": "StepRelationKind", "package": DFMLDS, "literals": ["sequence", "alternative", "exception", "fork", "join", "loop"]},
        "ConditionKind": {"name": "ConditionKind", "package": DFMLDS, "literals": ["guard", "precondition", "postcondition", "spatial", "timing"]},
        "EntityKind": {"name": "EntityKind", "package": DFMLDS, "literals": ["agent", "asset", "zone", "signal", "stateObject"]},
        "RuntimeLocatorKind": {"name": "RuntimeLocatorKind", "package": DFMLDS, "literals": ["endpoint", "tool", "topic"]},
        "AssertionSeverity": {"name": "AssertionSeverity", "package": DFMLDS, "literals": ["info", "warning", "error", "critical"]},
        "AssertionVerdict": {"name": "AssertionVerdict", "package": DFMLDS, "literals": ["pass", "fail", "inconclusive", "error"]},
    }

    associations = [
        assoc("functionConnector-port", "FunctionConnector", "FunctionPort", "port", "2", package=EAST, stereotype="instanceRef"),
        assoc("root-requirementsModel", "DynamicFunctionalModel", "RequirementsModel", "requirementsModel", "1", composition=True),
        assoc("root-verificationValidation", "DynamicFunctionalModel", "VerificationValidation", "verificationValidation", "1", composition=True),
        assoc("root-assertion", "DynamicFunctionalModel", "Assertion", "assertion", "0..*", composition=True),
        assoc("vv-validationCase", "VerificationValidation", "ValidationCase", "validationCase", "0..*", composition=True),
        assoc("case-runtimeLog", "ValidationCase", "RuntimeValidationLog", "vvLog", "0..*", composition=True),
        assoc("log-actualOutcome", "RuntimeValidationLog", "RuntimeActualOutcome", "actualOutcome", "0..*", composition=True),
        assoc("root-useCaseScenario", "DynamicFunctionalModel", "UseCaseScenarioSpecification", "scenarioSpecification", "0..*", composition=True),
        assoc("root-actorParticipation", "DynamicFunctionalModel", "ActorParticipation", "actorParticipation", "0..*", composition=True),
        assoc("root-conditionalExtend", "DynamicFunctionalModel", "ConditionalExtend", "conditionalExtend", "0..*", composition=True),
        assoc("root-runtimeBinding", "DynamicFunctionalModel", "RuntimeBinding", "runtimeBinding", "0..*", composition=True),
        assoc("root-validationBinding", "DynamicFunctionalModel", "ValidationCaseUseCaseBinding", "validationBinding", "0..*", composition=True),
        assoc("root-parameterBinding", "DynamicFunctionalModel", "ParameterBinding", "parameterBinding", "0..*", composition=True),
        assoc("root-satisfy", "DynamicFunctionalModel", "Satisfy", "satisfy", "0..*", composition=True),
        assoc("root-verify", "DynamicFunctionalModel", "Verify", "verify", "0..*", composition=True),
        assoc("usecase-extensionPoint", "UseCase", "ExtensionPoint", "extensionPoint", "0..*", package=EAST, composition=True),
        assoc("usecase-include", "UseCase", "Include", "include", "0..*", package=EAST, composition=True),
        assoc("usecase-extend", "UseCase", "Extend", "extend", "0..*", package=EAST, composition=True),
        assoc("include-addition", "Include", "UseCase", "addition", "1", package=EAST),
        assoc("extend-case", "Extend", "UseCase", "extendedCase", "1", package=EAST),
        assoc("extend-location", "Extend", "ExtensionPoint", "extensionLocation", "1..*", package=EAST),
        assoc("scenario-step", "Scenario", "ScenarioStep", "step", "1..*", composition=True, ordered=True),
        assoc("scenario-relation", "Scenario", "StepRelation", "stepRelation", "0..*", composition=True),
        assoc("scenario-parallel", "Scenario", "ParallelGroup", "parallelGroup", "0..*", composition=True),
        assoc("scenario-variant", "Scenario", "Scenario", "variantOf", "0..1"),
        assoc("relation-source", "StepRelation", "ScenarioStep", "source", "1"),
        assoc("relation-target", "StepRelation", "ScenarioStep", "target", "1"),
        assoc("group-member", "ParallelGroup", "ScenarioStep", "memberStep", "2..*"),
        assoc("spec-useCase", "UseCaseScenarioSpecification", "UseCase", "useCase", "1"),
        assoc("spec-scenario", "UseCaseScenarioSpecification", "Scenario", "scenario", "1"),
        assoc("step-capabilityUse", "ScenarioStep", "CapabilityUse", "capabilityUse", "0..*", composition=True),
        assoc("step-performedBy", "ScenarioStep", "Entity", "performedBy", "0..*"),
        assoc("capabilityUse-type", "CapabilityUse", "Capability", "type", "1", stereotype="isOfType"),
        assoc("capabilityUse-provider", "CapabilityUse", "Entity", "provider", "0..1"),
        assoc("capabilityUse-target", "CapabilityUse", "Identifiable", "target", "0..*", stereotype="instanceRef"),
        assoc("capabilityUse-parameter", "CapabilityUse", "KeyValueParameter", "parameter", "0..*", composition=True),
        assoc("entity-capability", "Entity", "Capability", "providedCapability", "0..*"),
        assoc("capability-effect", "Capability", "Effect", "effect", "1..*", composition=True),
        assoc("effect-specifiedBy", "Effect", "Assertion", "specifiedBy", "1..*"),
        assoc("assertion-subject", "Assertion", "Identifiable", "subject", "1"),
        assoc("assertion-expression", "Assertion", "EAExpression", "expression", "1", composition=True),
        assoc("runtime-action", "RuntimeBinding", "RuntimeAction", "runtimeAction", "1..*", composition=True, ordered=True),
        assoc("action-locator", "RuntimeAction", "RuntimeActionLocator", "locator", "1", composition=True),
        assoc("action-parameter", "RuntimeAction", "KeyValueParameter", "runtimeParameter", "0..*", composition=True),
        assoc("action-inputSchema", "RuntimeAction", "SchemaReference", "inputSchema", "0..1", composition=True),
        assoc("action-outputSchema", "RuntimeAction", "SchemaReference", "outputSchema", "0..1", composition=True),
        assoc("parameter-capability", "ParameterBinding", "KeyValueParameter", "capabilityParameter", "1"),
        assoc("parameter-runtime", "ParameterBinding", "KeyValueParameter", "runtimeParameter", "1"),
        assoc("case-subject", "ValidationCase", "RuntimeBinding", "vvSubject", "1..*"),
        assoc("case-target", "ValidationCase", "RuntimeValidationTarget", "vvTarget", "1..*"),
        assoc("case-procedure", "ValidationCase", "RuntimeValidationProcedure", "vvProcedure", "0..*", composition=True, ordered=True),
        assoc("case-abstract", "ValidationCase", "ValidationCase", "abstractVVCase", "0..1"),
        assoc("procedure-stimulus", "RuntimeValidationProcedure", "RuntimeStimulus", "vvStimuli", "0..*", composition=True),
        assoc("procedure-intended", "RuntimeValidationProcedure", "StateAssertionOutcome", "vvIntendedOutcome", "0..*", composition=True),
        assoc("procedure-abstract", "RuntimeValidationProcedure", "RuntimeValidationProcedure", "abstractVVProcedure", "0..1"),
        assoc("intended-assertion", "AssertionOutcome", "Assertion", "assertion", "1..*"),
        assoc("result-assertion", "AssertionResult", "Assertion", "assertion", "1"),
        assoc("result-observedValue", "AssertionResult", "EAValue", "observedValue", "0..1", composition=True),
        assoc("actual-result", "RuntimeActualOutcome", "AssertionResult", "result", "1..*", composition=True),
        assoc("target-element", "RuntimeValidationTarget", "Identifiable", "element", "0..*"),
        assoc("target-runtimeBinding", "RuntimeValidationTarget", "RuntimeBinding", "runtimeBinding", "0..*"),
        assoc("validation-usecase-case", "ValidationCaseUseCaseBinding", "ValidationCase", "validationCase", "1"),
        assoc("validation-usecase-usecase", "ValidationCaseUseCaseBinding", "UseCase", "useCase", "1..*"),
        assoc("verify-requirement", "Verify", "Requirement", "requirement", "1", package=EAST),
        assoc("verify-case", "Verify", "VVCase", "vvCase", "1..*", package=EAST),
        assoc("verify-procedure", "Verify", "VVProcedure", "vvProcedure", "0..*", package=EAST),
    ]

    invariants = [
        {"id": "INV-COND-BOOLEAN", "scope": "ScenarioCondition", "severity": "error", "expression": "self.type.oclIsKindOf(EABoolean)", "text": "Boolean typed"},
        {"id": "INV-SCENARIO-VARIANT", "scope": "Scenario", "severity": "error", "expression": "self.kind <> main implies self.variantOf.kind = main", "text": "Variants refer to main"},
        {"id": "INV-SCENARIO-MAIN", "scope": "Scenario", "severity": "error", "expression": "UseCase executable implies Scenario.main->size() = 1", "text": "one main"},
        {"id": "INV-PARALLEL-FORK-JOIN", "scope": "ParallelGroup", "severity": "error", "expression": "members are reachable between fork and join", "text": "fork/join"},
        {"id": "INV-ENTITY-AGENT-IFF", "scope": "Entity", "severity": "error", "expression": "(self.kind = agent) = self.oclIsKindOf(Agent)", "text": "agent iff"},
        {"id": "INV-SATISFY-XOR", "scope": "Satisfy", "severity": "error", "expression": "satisfiedRequirement xor satisfiedUseCase", "text": "xor"},
        {"id": "INV-SATISFY-EXCLUDE", "scope": "Satisfy", "severity": "error", "expression": "satisfiedBy excludes Requirement and RequirementContainer", "text": "exclusions"},
        {"id": "INV-ROOT-REQ", "scope": "DynamicFunctionalModel", "severity": "error", "expression": "requirementsModel->size()=1", "text": "one requirements model"},
        {"id": "INV-ROOT-VV", "scope": "DynamicFunctionalModel", "severity": "error", "expression": "verificationValidation->size()=1", "text": "one V&V model"},
        {"id": "INV-CAP-PROVIDER", "scope": "CapabilityUse", "severity": "error", "expression": "provider->notEmpty() implies scenarioStep.performedBy->includes(provider) and provider.providedCapability->includes(type)", "text": "provider consistency"},
        {"id": "INV-CAP-PROVIDER-EXEC", "scope": "CapabilityUse", "severity": "error", "expression": "provider->size()=1", "text": "one executable provider", "profile": "executable"},
        {"id": "INV-TARGET-SUBSET", "scope": "RuntimeValidationTarget", "severity": "error", "expression": "runtimeBinding->forAll(rb | element->includes(rb))", "text": "binding subset"},
        {"id": "INV-VV-SUBJECT", "scope": "ValidationCase", "severity": "error", "expression": "vvSubject->forAll(s | s.oclIsKindOf(ScenarioStep) or s.oclIsKindOf(Capability) or s.oclIsKindOf(RuntimeBinding) or s.oclIsKindOf(Entity))", "text": "allowed subjects"},
        {"id": "INV-STEP-PROB-KIND", "scope": "StepRelation", "severity": "error", "expression": "probability->notEmpty() implies (kind=alternative or kind=exception)", "text": "branch probability kinds"},
        {"id": "INV-STEP-PROB-SUM", "scope": "Scenario", "severity": "error", "expression": "complete branches probability->sum() = 1.0", "text": "complete branch sum"},
    ]

    return {
        "metadata": {
            "id": "DFMLDS-V2-positive-full-surface",
            "version": "2.0.0-draft",
            "invariant_ids": [item["id"] for item in invariants],
        },
        "packages": {
            EAST: {"name": EAST, "imports": []},
            DFMLDS: {"name": DFMLDS, "imports": [EAST]},
            ANNEX: {"name": ANNEX, "imports": [EAST], "optional": True, "status": "preliminary"},
        },
        "primitives": ["String", "Boolean", "Integer", "Numerical", "Identifier"],
        "enums": enums,
        "datatypes": {
            "Probability": {"name": "Probability", "package": DFMLDS, "bases": ["EANumerical"], "min": 0, "max": 1},
        },
        "classes": classes,
        "associations": associations,
        "invariants": invariants,
        "views": {"core": {"invariant_ids": [item["id"] for item in invariants]}},
        "compatibility_contract": {"invariant_ids": ["INV-ENTITY-AGENT-IFF"]},
        "annex_mappings": {
            "optional": True,
            "status": "preliminary / not validated for the base core",
            "entries": [
                {"source": "ScenarioStep", "target": "LogicalTransformation/TransformationOccurrence"},
                {"source": "ScenarioEvent", "target": "TransitionEvent via occurredExecutionEvent: Timing::Event"},
            ],
        },
    }


def full_surface_instance():
    objects = [
        {
            "id": "root", "type": "DynamicFunctionalModel",
            "requirementsModel": ["requirements"],
            "verificationValidation": ["vv"],
            "assertion": ["state", "event-assertion", "output-assertion", "grounding-assertion", "relation-assertion"],
            "scenarioSpecification": ["spec-main", "spec-alt", "spec-exception"],
            "actorParticipation": ["participation"],
            "conditionalExtend": ["conditional-extend"],
            "runtimeBinding": ["rb"],
            "validationBinding": ["case-usecase"],
            "parameterBinding": ["parameter-binding"],
            "satisfy": ["satisfy-requirement", "satisfy-usecase"],
            "verify": ["verify"],
        },
        {"id": "requirements", "type": "RequirementsModel"},
        {"id": "req", "type": "Requirement", "formalism": "text"},
        {
            "id": "uc", "type": "UseCase", "extensionPoint": ["ep"],
            "include": ["include"], "extend": ["extend"],
        },
        {"id": "uc-included", "type": "UseCase"},
        {"id": "ep", "type": "ExtensionPoint"},
        {"id": "include", "type": "Include", "addition": ["uc-included"]},
        {"id": "extend", "type": "Extend", "extendedCase": ["uc"], "extensionLocation": ["ep"]},
        {"id": "actor", "type": "Actor"},
        {"id": "participation", "type": "ActorParticipation", "actor": ["actor"], "useCase": ["uc"]},
        {
            "id": "conditional-extend", "type": "ConditionalExtend", "condition": ["condition"],
            "extendedCase": ["uc"], "extensionLocation": ["ep"],
        },
        {"id": "spec-main", "type": "UseCaseScenarioSpecification", "useCase": ["uc"], "scenario": ["main"]},
        {"id": "spec-alt", "type": "UseCaseScenarioSpecification", "useCase": ["uc"], "scenario": ["alt"]},
        {"id": "spec-exception", "type": "UseCaseScenarioSpecification", "useCase": ["uc"], "scenario": ["exception"]},
        {
            "id": "main", "type": "Scenario", "kind": "main",
            "step": ["s0", "s1", "s2", "s3", "s4", "s5", "s6"],
            "stepRelation": ["r01", "r02", "r13", "r23", "r34", "r45-alt", "r46-exc", "r64-loop"],
            "parallelGroup": ["pg"],
        },
        {"id": "alt", "type": "Scenario", "kind": "alternative", "variantOf": ["main"], "step": ["sa"], "stepRelation": [], "parallelGroup": []},
        {"id": "exception", "type": "Scenario", "kind": "exception", "variantOf": ["main"], "step": ["se"], "stepRelation": [], "parallelGroup": []},
        {"id": "s0", "type": "ScenarioStep", "occurrenceProbability": 1.0},
        {"id": "s1", "type": "ScenarioStep", "occurrenceProbability": 0.5},
        {"id": "s2", "type": "ScenarioStep", "occurrenceProbability": 0.5},
        {"id": "s3", "type": "ScenarioStep", "occurrenceProbability": 1.0},
        {"id": "s4", "type": "ScenarioStep", "occurrenceProbability": 1.0, "capabilityUse": ["cap-use"], "performedBy": ["agent"]},
        {"id": "s5", "type": "ScenarioStep", "occurrenceProbability": 0.4},
        {"id": "s6", "type": "ScenarioStep", "occurrenceProbability": 0.1},
        {"id": "sa", "type": "ScenarioStep", "occurrenceProbability": 0.2},
        {"id": "se", "type": "ScenarioStep", "occurrenceProbability": 0.1},
        {"id": "r01", "type": "StepRelation", "kind": "fork", "source": ["s0"], "target": ["s1"]},
        {"id": "r02", "type": "StepRelation", "kind": "fork", "source": ["s0"], "target": ["s2"]},
        {"id": "r13", "type": "StepRelation", "kind": "join", "source": ["s1"], "target": ["s3"]},
        {"id": "r23", "type": "StepRelation", "kind": "join", "source": ["s2"], "target": ["s3"]},
        {"id": "r34", "type": "StepRelation", "kind": "sequence", "source": ["s3"], "target": ["s4"]},
        {"id": "r45-alt", "type": "StepRelation", "kind": "alternative", "source": ["s4"], "target": ["s5"], "probability": 0.8},
        {"id": "r46-exc", "type": "StepRelation", "kind": "exception", "source": ["s4"], "target": ["s6"], "probability": 0.2},
        {"id": "r64-loop", "type": "StepRelation", "kind": "loop", "source": ["s6"], "target": ["s4"]},
        {"id": "pg", "type": "ParallelGroup", "memberStep": ["s1", "s2"]},
        {"id": "event", "type": "ScenarioExternalEvent"},
        {"id": "condition", "type": "ScenarioCondition", "datatype": "EABoolean", "kind": "guard"},
        {"id": "state", "type": "StateAssertion", "subject": ["s4"], "expression": ["expr-state"], "severity": "error"},
        {"id": "event-assertion", "type": "EventAssertion", "subject": ["event"], "expression": ["expr-event"], "severity": "warning"},
        {"id": "output-assertion", "type": "OutputAssertion", "subject": ["rb"], "expression": ["expr-output"]},
        {"id": "grounding-assertion", "type": "GroundingAssertion", "subject": ["ent-human"], "expression": ["expr-grounding"]},
        {"id": "relation-assertion", "type": "RelationAssertion", "subject": ["cap-use"], "expression": ["expr-relation"]},
        {"id": "expr-state", "type": "ScenarioCondition", "datatype": "EABoolean", "kind": "postcondition"},
        {"id": "expr-event", "type": "ScenarioCondition", "datatype": "EABoolean", "kind": "postcondition"},
        {"id": "expr-output", "type": "ScenarioCondition", "datatype": "EABoolean", "kind": "postcondition"},
        {"id": "expr-grounding", "type": "ScenarioCondition", "datatype": "EABoolean", "kind": "postcondition"},
        {"id": "expr-relation", "type": "ScenarioCondition", "datatype": "EABoolean", "kind": "postcondition"},
        {"id": "ent-human", "type": "Entity", "kind": "asset"},
        {"id": "ent-signal", "type": "Entity", "kind": "signal"},
        {"id": "agent", "type": "Agent", "kind": "agent", "providedCapability": ["cap"]},
        {"id": "cap", "type": "Capability", "effect": ["effect"]},
        {"id": "cap-use", "type": "CapabilityUse", "typeRef": ["cap"], "provider": ["agent"], "target": ["ent-signal"], "parameter": ["cap-param"]},
        {"id": "cap-param", "type": "KeyValueParameter", "key": "message", "valueType": "String"},
        {"id": "runtime-param", "type": "KeyValueParameter", "key": "payload", "valueType": "String"},
        {"id": "effect", "type": "Effect", "specifiedBy": ["state"]},
        {"id": "rb", "type": "RuntimeBinding", "runtimeAction": ["ra-endpoint", "ra-tool", "ra-topic"]},
        {"id": "ra-endpoint", "type": "RuntimeAction", "locator": ["locator-endpoint"], "runtimeParameter": ["runtime-param"], "inputSchema": ["schema-in"], "outputSchema": ["schema-out"]},
        {"id": "ra-tool", "type": "RuntimeAction", "locator": ["locator-tool"]},
        {"id": "ra-topic", "type": "RuntimeAction", "locator": ["locator-topic"]},
        {"id": "locator-endpoint", "type": "RuntimeActionLocator", "kind": "endpoint", "value": "/chat"},
        {"id": "locator-tool", "type": "RuntimeActionLocator", "kind": "tool", "value": "HANDOFF"},
        {"id": "locator-topic", "type": "RuntimeActionLocator", "kind": "topic", "value": "agent.events"},
        {"id": "schema-in", "type": "SchemaReference"},
        {"id": "schema-out", "type": "SchemaReference"},
        {"id": "parameter-binding", "type": "ParameterBinding", "capabilityParameter": ["cap-param"], "runtimeParameter": ["runtime-param"]},
        {"id": "vv", "type": "VerificationValidation", "validationCase": ["vc", "vc-abstract"]},
        {"id": "vc", "type": "ValidationCase", "isConcrete": True, "vvSubject": ["rb"], "vvTarget": ["vt"], "vvProcedure": ["procedure"], "vvLog": ["log"], "abstractVVCase": ["vc-abstract"]},
        {"id": "vc-abstract", "type": "ValidationCase", "abstract": True},
        {"id": "procedure", "type": "RuntimeValidationProcedure", "isConcrete": True, "vvStimuli": ["stimulus"], "vvIntendedOutcome": ["intended"], "abstractVVProcedure": ["procedure-abstract"]},
        {"id": "procedure-abstract", "type": "RuntimeValidationProcedure", "abstract": True},
        {"id": "stimulus", "type": "RuntimeStimulus"},
        {"id": "intended", "type": "StateAssertionOutcome", "assertion": ["state"]},
        {"id": "vt", "type": "RuntimeValidationTarget", "platform": "Unity", "environmentRef": "play-mode", "element": ["rb"], "runtimeBinding": ["rb"]},
        {"id": "log", "type": "RuntimeValidationLog", "actualOutcome": ["actual"]},
        {"id": "actual", "type": "RuntimeActualOutcome", "result": ["assertion-result"]},
        {"id": "assertion-result", "type": "AssertionResult", "assertion": ["state"], "verdict": "pass", "observedValue": ["observed-value"], "evidenceRef": "log://state", "timestamp": "2026-07-14T12:00:00Z"},
        {"id": "observed-value", "type": "EANumericalValue", "value": 1},
        {"id": "case-usecase", "type": "ValidationCaseUseCaseBinding", "validationCase": ["vc"], "useCase": ["uc"]},
        {"id": "verify", "type": "Verify", "requirement": ["req"], "vvCase": ["vc"]},
        {"id": "satisfy-requirement", "type": "Satisfy", "satisfiedRequirement": ["req"], "satisfiedUseCase": [], "satisfiedBy": ["cap"]},
        {"id": "satisfy-usecase", "type": "Satisfy", "satisfiedRequirement": [], "satisfiedUseCase": ["uc"], "satisfiedBy": ["cap"]},
        {"id": "behavior", "type": "FunctionBehavior", "path": "model/behavior", "representation": "behavior"},
    ]
    return {"id": "positive-full-surface", "fixture_profile": "full-surface", "objects": objects}


def full_surface_bundle():
    """CLI fixture provider: model plus positive full-surface instance."""

    return {"model": full_surface_model(), "instance": full_surface_instance()}


def class_record(model, name):
    return next(item for key, item in model["classes"].items() if item["name"] == name)


def association_record(model, assoc_id):
    return next(item for item in model["associations"] if item["id"] == assoc_id)


def object_record(instance, object_id):
    return next(item for item in instance["objects"] if item["id"] == object_id)


class CanonicalModelValidationTests(unittest.TestCase):
    def setUp(self):
        self.model = full_surface_model()
        self.instance = full_surface_instance()

    def assert_model_mutation(self, mutator, expected_code):
        candidate = copy.deepcopy(self.model)
        mutator(candidate)
        report = validate_model(candidate)
        self.assertIn(expected_code, report.codes(), report.to_dict())

    def assert_instance_mutation(self, mutator, expected_code):
        candidate = copy.deepcopy(self.instance)
        mutator(candidate)
        report = validate_instance(self.model, candidate, "negative mutation")
        self.assertIn(expected_code, report.codes(), report.to_dict())

    def test_positive_full_surface_model_and_instance(self):
        model_report = validate_model(self.model)
        instance_report = validate_instance(self.model, self.instance, "positive full-surface")
        self.assertTrue(model_report.ok, model_report.to_dict())
        self.assertTrue(instance_report.ok, instance_report.to_dict())
        coverage = instance_report.evidence["fixture_coverage"]
        self.assertEqual(coverage["covered_count"], coverage["requirement_count"])
        self.assertGreaterEqual(coverage["requirement_count"], 10)

    def test_additional_exact_east_definitions_are_mutation_checked(self):
        mutations = [
            (lambda model: class_record(model, "Relationship").update(bases=[]), "EAST001"),
            (lambda model: class_record(model, "EADatatype").update(bases=["EAElement"]), "EAST001"),
            (lambda model: class_record(model, "VVCase").update(bases=["EAElement"]), "EAST001"),
            (lambda model: class_record(model, "FunctionPort").update(bases=["EAPort"]), "EAST001"),
            (lambda model: class_record(model, "FeatureTreeNode").update(bases=["EAElement"]), "EAST001"),
            (
                lambda model: next(item for item in class_record(model, "Mode")["attributes"] if item["name"] == "condition").update(multiplicity="0..1"),
                "EAST004",
            ),
            (lambda model: association_record(model, "functionConnector-port").update(target_multiplicity="1"), "EAST005"),
        ]
        for mutator, code in mutations:
            with self.subTest(code=code, mutator=mutator):
                self.assert_model_mutation(mutator, code)

    def test_reference_and_enum_closure_mutations(self):
        self.assert_model_mutation(
            lambda model: class_record(model, "Scenario")["attributes"].append(attr("broken", "MissingType")),
            "REF004",
        )
        self.assert_model_mutation(
            lambda model: model["enums"]["EntityKind"].update(literals=["agent", "agent"]),
            "ENUM001",
        )

    def test_east_exact_base_and_shadow_mutations(self):
        self.assert_model_mutation(
            lambda model: class_record(model, "FunctionBehavior").update(bases=["EAElement"]),
            "EAST001",
        )
        self.assert_model_mutation(
            lambda model: class_record(model, "UseCase")["attributes"].append(attr("text", "String")),
            "EAST002",
        )

    def test_reverse_import_and_duplicate_owner_mutations(self):
        self.assert_model_mutation(
            lambda model: model["packages"][EAST]["imports"].append(DFMLDS),
            "PKG002",
        )
        self.assert_model_mutation(
            lambda model: model["associations"].append(
                assoc("second-runtime-owner", "RuntimeBinding", "RuntimeAction", "runtimeAction", "1..*", composition=True)
            ),
            "OWN002",
        )

    def test_invariant_sync_mutation(self):
        self.assert_model_mutation(
            lambda model: model["metadata"]["invariant_ids"].pop(),
            "INV006",
        )

    def test_capability_type_and_condition_mutations(self):
        self.assert_model_mutation(
            lambda model: class_record(model, "Capability").update(bases=["TraceableSpecification"]),
            "CAP001",
        )
        self.assert_model_mutation(
            lambda model: next(item for item in model["invariants"] if item["id"] == "INV-COND-BOOLEAN").update(expression="self.type = EADatatype"),
            "VAL002",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "condition").update(datatype="String"),
            "IVAL001",
        )

    def test_root_and_capability_use_contract_mutations(self):
        self.assert_model_mutation(
            lambda model: association_record(model, "root-requirementsModel").update(target_multiplicity="0..1"),
            "ROOT001",
        )
        self.assert_model_mutation(
            lambda model: association_record(model, "capabilityUse-provider").update(target_multiplicity="0..*"),
            "CAP005",
        )
        self.assert_model_mutation(
            lambda model: association_record(model, "capabilityUse-target").update(target="Entity"),
            "CAP006",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "root").update(requirementsModel=[]),
            "IROOT001",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "root").update(requirementsModel=["uc"]),
            "IROOT003",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "cap-use").update(provider=[]),
            "ICAP002",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "agent").update(providedCapability=[]),
            "ICAP004",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "s4").update(performedBy=[]),
            "ICAP005",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "cap-use").update(target=["observed-value"]),
            "ICAP006",
        )

        compatibility = copy.deepcopy(self.instance)
        compatibility["fixture_profile"] = "compatibility"
        object_record(compatibility, "cap-use")["provider"] = []
        report = validate_instance(self.model, compatibility, "compatibility core")
        self.assertTrue(report.ok, report.to_dict())

    def test_assertion_structure_and_instance_mutations(self):
        self.assert_model_mutation(
            lambda model: class_record(model, "StateAssertion").update(bases=["TraceableSpecification"]),
            "AST002",
        )
        self.assert_model_mutation(
            lambda model: association_record(model, "assertion-expression").update(composition=False),
            "AST006",
        )
        self.assert_model_mutation(
            lambda model: association_record(model, "effect-specifiedBy").update(target="StateAssertion"),
            "AST007",
        )
        self.assert_model_mutation(
            lambda model: association_record(model, "actual-result").update(target_multiplicity="0..*"),
            "AST017",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "state").update(expression=[]),
            "IAST004",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "state").update(subject=["observed-value"]),
            "IAST003",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "effect").update(specifiedBy=[]),
            "IAST007",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "intended").update(assertion=["uc"]),
            "IAST019",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "assertion-result").update(verdict="unknown"),
            "IAST013",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "actual").update(result=[]),
            "IAST017",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "actual").update(result=["state"]),
            "IAST018",
        )

    def test_probability_descriptor_and_value_mutations(self):
        self.assert_model_mutation(
            lambda model: model["datatypes"]["Probability"].update(max=2),
            "VAL004",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "s1").update(occurrenceProbability=1.01),
            "IVAL002",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "r34").update(probability=0.1),
            "ISCN010",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "r45-alt").update(probability=0.7),
            "ISCN011",
        )
        self.assert_model_mutation(
            lambda model: next(item for item in model["invariants"] if item["id"] == "INV-STEP-PROB-KIND").update(expression="probability->notEmpty()"),
            "SCN010",
        )

    def test_runtime_structure_and_runtime_instance_mutations(self):
        self.assert_model_mutation(
            lambda model: association_record(model, "runtime-action").update(ordered=False),
            "RUN004",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "rb").update(runtimeAction=[]),
            "IRUN001",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "ra-endpoint").update(locator=["locator-endpoint", "locator-tool"]),
            "IRUN002",
        )

    def test_scenario_variant_and_parallel_mutations(self):
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "alt").update(variantOf=[]),
            "ISCN003",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "main").update(stepRelation=["r01", "r02"]),
            "ISCN008",
        )

    def test_entity_agent_equivalence_mutation(self):
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "ent-human").update(kind="agent"),
            "IENT001",
        )

    def test_satisfy_xor_and_exclusion_mutations(self):
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "satisfy-requirement").update(satisfiedUseCase=["uc"]),
            "IREQ001",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "satisfy-requirement").update(satisfiedBy=["req"]),
            "IREQ003",
        )

    def test_vv_log_and_subject_target_mutations(self):
        self.assert_model_mutation(
            lambda model: association_record(model, "log-actualOutcome").update(source="ValidationCase"),
            "VV005",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "log").update(actualOutcome=[]),
            "IVV001",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "vc").update(vvTarget=[]),
            "IVV003",
        )
        self.assert_model_mutation(
            lambda model: model["associations"].remove(association_record(model, "target-element")),
            "VV009",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "vc-abstract").update(vvTarget=["vt"]),
            "IVV007",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "procedure-abstract").update(vvStimuli=["stimulus"]),
            "IVV008",
        )
        self.assert_model_mutation(
            lambda model: next(item for item in class_record(model, "RuntimeValidationTarget")["attributes"] if item["name"] == "platform").update(multiplicity="0..1"),
            "VV012",
        )
        self.assert_model_mutation(
            lambda model: association_record(model, "target-runtimeBinding").update(target="Capability"),
            "VV014",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "vc").update(vvSubject=["uc"]),
            "IVV009",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "vt").update(platform=""),
            "IVV010",
        )
        self.assert_instance_mutation(
            lambda instance: object_record(instance, "vt").update(element=[]),
            "IVV013",
        )

    def test_verify_requires_case_not_procedure_alone(self):
        def procedure_only(instance):
            verify = object_record(instance, "verify")
            verify["vvCase"] = []
            verify["vvProcedure"] = ["procedure"]

        self.assert_instance_mutation(procedure_only, "IVV006")

    def test_vv_roles_may_coincidentally_reference_same_identifiable(self):
        report = validate_instance(self.model, self.instance, "coincident V&V roles")
        self.assertTrue(report.ok, report.to_dict())
        coverage = report.evidence["fixture_coverage"]
        role_item = next(item for item in coverage["requirements"] if item["id"] == "COV-VV-ROLE-SEPARATION")
        self.assertTrue(role_item["covered"])
        self.assertEqual(role_item["evidence"], ["rb"])

        def force_value_inequality(model):
            invariant = {
                "id": "INV-BROKEN-VV-DISJOINT",
                "scope": "VVCase",
                "severity": "error",
                "expression": "vvSubject <> vvTarget.element",
                "text": "incorrect value disjointness",
            }
            model["invariants"].append(invariant)
            model["metadata"]["invariant_ids"].append(invariant["id"])

        self.assert_model_mutation(force_value_inequality, "VV011")

    def test_function_behavior_and_architecture_mutations(self):
        self.assert_model_mutation(
            lambda model: class_record(model, "FunctionBehavior").update(
                attributes=[item for item in class_record(model, "FunctionBehavior")["attributes"] if item["name"] != "path"]
            ),
            "FUN001",
        )
        self.assert_model_mutation(
            lambda model: model["classes"].update({"DFMLDS::V2::FAA": cls("FAA", DFMLDS, ["EAElement"])}),
            "ARCH001",
        )

    def test_annex_status_and_dependency_mutations(self):
        self.assert_model_mutation(
            lambda model: model["annex_mappings"].update(optional=False, status="normative"),
            "ANNEX002",
        )
        self.assert_model_mutation(
            lambda model: model["packages"][DFMLDS]["imports"].append(ANNEX),
            "PKG004",
        )

    def test_cli_report_serialization(self):
        reports = [validate_model(self.model), validate_instance(self.model, self.instance)]
        with tempfile.TemporaryDirectory() as directory:
            json_path, markdown_path = write_reports(reports, Path(directory), "evidence")
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertTrue(payload["ok"])
            self.assertIn("Overall result: **PASS**", markdown_path.read_text(encoding="utf-8"))

    def test_cli_fixture_provider_writes_structured_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            model_path = directory_path / "model.json"
            model_path.write_text(json.dumps(self.model), encoding="utf-8")
            result = validator_main(
                [
                    "--model-json", str(model_path),
                    "--fixture-provider", "tools.tests.test_dynamic_functional_mlds_v2_validation:full_surface_bundle",
                    "--output-dir", str(directory_path),
                    "--prefix", "fixture-coverage",
                ]
            )
            self.assertEqual(result, 0)
            payload = json.loads((directory_path / "fixture-coverage.json").read_text(encoding="utf-8"))
            coverage_reports = [item for item in payload["reports"] if "fixture_coverage" in item["evidence"]]
            self.assertEqual(len(coverage_reports), 1)
            self.assertTrue(coverage_reports[0]["evidence"]["fixture_coverage"]["ok"])


class RepositoryCanonicalModelTests(unittest.TestCase):
    def test_repository_model_when_available(self):
        try:
            from tools.dynamic_functional_mlds_v2_model import MODEL
        except ModuleNotFoundError:
            self.skipTest("canonical V2 model is being generated in parallel")
        report = validate_model(MODEL)
        self.assertTrue(report.ok, report.to_dict())


if __name__ == "__main__":
    unittest.main(verbosity=2)
