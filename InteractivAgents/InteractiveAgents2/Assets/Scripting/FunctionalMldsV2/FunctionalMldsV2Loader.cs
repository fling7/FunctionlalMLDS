using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace FunctionalMlds.V2
{
    public sealed class FunctionalMldsV2LoadResult
    {
        public FunctionalMldsV2Document Document { get; }
        public FunctionalMldsV2ModelIndex Index { get; }
        public FunctionalMldsV2ValidationReport Validation { get; }
        public string Sha256 { get; }
        public string SourcePath { get; }

        internal FunctionalMldsV2LoadResult(
            FunctionalMldsV2Document document,
            FunctionalMldsV2ModelIndex index,
            FunctionalMldsV2ValidationReport validation,
            string sha256,
            string sourcePath)
        {
            Document = document;
            Index = index;
            Validation = validation;
            Sha256 = sha256;
            SourcePath = sourcePath;
        }
    }

    public static class FunctionalMldsV2Loader
    {
        private static readonly HashSet<string> RootMembers = new HashSet<string>(StringComparer.Ordinal)
        {
            "schema", "id", "metamodelVersion", "serializationVersion", "caseId", "profile",
            "fixture_profile", "sourceContract", "objects"
        };

        public static FunctionalMldsV2LoadResult LoadFile(string path, bool validate = true)
        {
            if (string.IsNullOrWhiteSpace(path))
                throw new ArgumentException("A V2 instance path is required.", nameof(path));
            var absolute = Path.GetFullPath(path);
            if (!File.Exists(absolute))
                throw new FileNotFoundException("FunctionalMLDS V2 instance not found.", absolute);
            var bytes = File.ReadAllBytes(absolute);
            return LoadBytes(bytes, absolute, validate);
        }

        public static FunctionalMldsV2LoadResult LoadJson(string json, string sourceName = "<memory>", bool validate = true)
        {
            if (string.IsNullOrWhiteSpace(json))
                throw new FunctionalMldsV2FormatException("FunctionalMLDS V2 JSON is empty.");
            return LoadBytes(Encoding.UTF8.GetBytes(json), sourceName, validate);
        }

        private static FunctionalMldsV2LoadResult LoadBytes(byte[] bytes, string sourceName, bool validate)
        {
            FunctionalMldsV2Document document;
            try
            {
                using (var stringReader = new StringReader(Encoding.UTF8.GetString(bytes)))
                using (var jsonReader = new JsonTextReader(stringReader))
                {
                    jsonReader.DateParseHandling = DateParseHandling.None;
                    jsonReader.FloatParseHandling = FloatParseHandling.Decimal;
                    jsonReader.MaxDepth = 128;
                    var root = JToken.ReadFrom(jsonReader, new JsonLoadSettings
                    {
                        CommentHandling = CommentHandling.Ignore,
                        DuplicatePropertyNameHandling = DuplicatePropertyNameHandling.Error,
                        LineInfoHandling = LineInfoHandling.Load
                    });
                    if (root.Type != JTokenType.Object)
                        throw new FunctionalMldsV2FormatException("The V2 document root must be an object.");
                    ValidateRootMembers((JObject)root);

                    var serializer = JsonSerializer.Create(new JsonSerializerSettings
                    {
                        DateParseHandling = DateParseHandling.None,
                        FloatParseHandling = FloatParseHandling.Decimal,
                        MetadataPropertyHandling = MetadataPropertyHandling.Ignore,
                        MissingMemberHandling = MissingMemberHandling.Ignore,
                        NullValueHandling = NullValueHandling.Include,
                        TypeNameHandling = TypeNameHandling.None,
                        MaxDepth = 128
                    });
                    document = root.ToObject<FunctionalMldsV2Document>(serializer);
                }
            }
            catch (FunctionalMldsV2FormatException)
            {
                throw;
            }
            catch (Exception exception)
            {
                throw new FunctionalMldsV2FormatException(
                    $"Cannot parse native FunctionalMLDS V2 document '{sourceName}': {exception.Message}",
                    exception);
            }

            if (document == null)
                throw new FunctionalMldsV2FormatException("Deserializer returned no V2 document.");
            if (!string.Equals(document.Schema, FunctionalMldsV2Lexemes.InstanceSchema, StringComparison.Ordinal))
                throw new FunctionalMldsV2FormatException(
                    $"Document.schema must be '{FunctionalMldsV2Lexemes.InstanceSchema}'.");
            if (string.IsNullOrWhiteSpace(document.Id))
                throw new FunctionalMldsV2FormatException("Document.id is required.");
            if (!string.Equals(document.MetamodelVersion, FunctionalMldsV2Lexemes.ModelVersion, StringComparison.Ordinal))
                throw new FunctionalMldsV2FormatException(
                    $"Document.metamodelVersion must be '{FunctionalMldsV2Lexemes.ModelVersion}'.");
            if (!string.IsNullOrWhiteSpace(document.SerializationVersion) &&
                !string.Equals(document.SerializationVersion, "1.0", StringComparison.Ordinal))
                throw new FunctionalMldsV2FormatException("Document.serializationVersion must be '1.0' when supplied.");
            if (document.CaseId != null && string.IsNullOrWhiteSpace(document.CaseId))
                throw new FunctionalMldsV2FormatException("Document.caseId cannot be empty when supplied.");
            if (!string.Equals(document.Profile, FunctionalMldsV2Lexemes.ExecutableProfile, StringComparison.Ordinal))
                throw new FunctionalMldsV2FormatException("Unity accepts only profile='executable'.");
            if (document.FixtureProfile != null &&
                !string.Equals(document.FixtureProfile, FunctionalMldsV2Lexemes.ExecutableProfile, StringComparison.Ordinal))
                throw new FunctionalMldsV2FormatException("Document.fixture_profile must be 'executable' when supplied.");
            if (document.Objects == null || document.Objects.Count == 0)
                throw new FunctionalMldsV2FormatException("Document.objects must be a non-empty array.");

            var index = new FunctionalMldsV2ModelIndex(document);
            var report = FunctionalMldsV2InvariantValidator.Validate(document, index);
            if (validate && !report.IsValid)
                throw new FunctionalMldsV2ValidationException(report);

            return new FunctionalMldsV2LoadResult(
                document,
                index,
                report,
                Sha256(bytes),
                sourceName);
        }

        private static string Sha256(byte[] bytes)
        {
            using (var algorithm = SHA256.Create())
            {
                return string.Concat(algorithm.ComputeHash(bytes).Select(value => value.ToString("X2")));
            }
        }

        private static void ValidateRootMembers(JObject root)
        {
            foreach (var property in root.Properties())
            {
                if (!RootMembers.Contains(property.Name))
                    throw new FunctionalMldsV2FormatException(
                        $"Unsupported V2 document root member '{property.Name}'.");
            }
        }
    }

    public sealed class FunctionalMldsV2ModelIndex
    {
        private readonly Dictionary<string, FunctionalMldsV2Object> _byId;
        private readonly Dictionary<string, string> _stepScenario = new Dictionary<string, string>(StringComparer.Ordinal);
        private readonly Dictionary<string, string> _relationScenario = new Dictionary<string, string>(StringComparer.Ordinal);
        private readonly Dictionary<string, string> _capabilityUseStep = new Dictionary<string, string>(StringComparer.Ordinal);
        private readonly Dictionary<string, string> _actualOutcomeLog = new Dictionary<string, string>(StringComparer.Ordinal);

        public FunctionalMldsV2Document Document { get; }
        public IEnumerable<FunctionalMldsV2Object> Objects => _byId.Values;

        public FunctionalMldsV2ModelIndex(FunctionalMldsV2Document document)
        {
            Document = document ?? throw new ArgumentNullException(nameof(document));
            _byId = new Dictionary<string, FunctionalMldsV2Object>(StringComparer.Ordinal);
            foreach (var item in document.Objects ?? new List<FunctionalMldsV2Object>())
            {
                if (item == null)
                    throw new FunctionalMldsV2FormatException("Document.objects contains null.");
                if (string.IsNullOrWhiteSpace(item.Id) || string.IsNullOrWhiteSpace(item.Type))
                    throw new FunctionalMldsV2FormatException("Every V2 object requires non-empty id and type.");
                item.Id = item.Id.Trim();
                item.Type = item.Type.Trim();
                if (item.Type.StartsWith("@", StringComparison.Ordinal))
                    throw new FunctionalMldsV2FormatException($"{item.Id}.type is not a native V2 metaclass name.");
                if (!_byId.TryAdd(item.Id, item))
                    throw new FunctionalMldsV2FormatException($"Duplicate V2 object id: {item.Id}.");
            }
            BuildOwnershipIndexes();
        }

        public bool TryGet(string id, out FunctionalMldsV2Object item)
        {
            return _byId.TryGetValue(id ?? string.Empty, out item);
        }

        public FunctionalMldsV2Object Get(string id)
        {
            FunctionalMldsV2Object item;
            return TryGet(id, out item) ? item : null;
        }

        public FunctionalMldsV2Object Require(string id, string expectedType = null)
        {
            var item = Get(id);
            if (item == null)
                throw new FunctionalMldsV2FormatException($"Unresolved V2 reference: {id}.");
            if (!string.IsNullOrWhiteSpace(expectedType) && !IsInstanceOf(item, expectedType))
                throw new FunctionalMldsV2FormatException($"{id} must be {expectedType}, got {item.Type}.");
            return item;
        }

        public IEnumerable<FunctionalMldsV2Object> OfType(string type)
        {
            return _byId.Values.Where(item => IsInstanceOf(item, type));
        }

        public bool IsInstanceOf(FunctionalMldsV2Object item, string type)
        {
            if (item == null || string.IsNullOrWhiteSpace(type))
                return false;
            if (string.Equals(item.Type, type, StringComparison.Ordinal))
                return true;
            if (type == "Assertion")
                return FunctionalMldsV2InvariantValidator.AssertionTypes.Contains(item.Type);
            if (type == "Entity")
                return item.Type == "Agent";
            if (type == "AssertionOutcome")
                return item.Type == "StateAssertionOutcome";
            if (type == "EAExpression")
                return item.Type == "ScenarioCondition" || item.Type == "ScenarioEvent";
            if (type == "EAValue")
                return item.Type == "EAExpression" || item.Type == "EANumericalValue" || item.Type == "ScenarioCondition" || item.Type == "ScenarioEvent";
            return false;
        }

        public string ScenarioOfStep(string stepId)
        {
            string value;
            return _stepScenario.TryGetValue(stepId, out value) ? value : null;
        }

        public string ScenarioOfRelation(string relationId)
        {
            string value;
            return _relationScenario.TryGetValue(relationId, out value) ? value : null;
        }

        public string StepOfCapabilityUse(string capabilityUseId)
        {
            string value;
            return _capabilityUseStep.TryGetValue(capabilityUseId, out value) ? value : null;
        }

        public string LogOfActualOutcome(string actualOutcomeId)
        {
            string value;
            return _actualOutcomeLog.TryGetValue(actualOutcomeId, out value) ? value : null;
        }

        private void BuildOwnershipIndexes()
        {
            foreach (var scenario in OfType("Scenario"))
            {
                foreach (var id in SafeReferences(scenario, "step"))
                    AddOwned(_stepScenario, id, scenario.Id, "ScenarioStep");
                foreach (var id in SafeReferences(scenario, "stepRelation"))
                    AddOwned(_relationScenario, id, scenario.Id, "StepRelation");
            }
            foreach (var step in OfType("ScenarioStep"))
            {
                foreach (var id in SafeReferences(step, "capabilityUse"))
                    AddOwned(_capabilityUseStep, id, step.Id, "CapabilityUse");
            }
            foreach (var log in OfType("RuntimeValidationLog"))
            {
                foreach (var id in SafeReferences(log, "vvActualOutcome")
                    .Concat(SafeReferences(log, "actualOutcome"))
                    .Distinct(StringComparer.Ordinal))
                    AddOwned(_actualOutcomeLog, id, log.Id, "RuntimeActualOutcome");
            }
        }

        private static IEnumerable<string> SafeReferences(FunctionalMldsV2Object item, string property)
        {
            try { return item.References(property); }
            catch { return Array.Empty<string>(); }
        }

        private static void AddOwned(Dictionary<string, string> map, string child, string owner, string label)
        {
            string previous;
            if (map.TryGetValue(child, out previous) && previous != owner)
                throw new FunctionalMldsV2FormatException($"{label} {child} has multiple composite owners: {previous}, {owner}.");
            map[child] = owner;
        }
    }

    public sealed class FunctionalMldsV2ValidationIssue
    {
        public string Code { get; }
        public string ObjectId { get; }
        public string Message { get; }

        public FunctionalMldsV2ValidationIssue(string code, string objectId, string message)
        {
            Code = code;
            ObjectId = objectId;
            Message = message;
        }

        public override string ToString()
        {
            return $"{Code} [{ObjectId}]: {Message}";
        }
    }

    public sealed class FunctionalMldsV2ValidationReport
    {
        public IReadOnlyList<FunctionalMldsV2ValidationIssue> Issues { get; }
        public bool IsValid => Issues.Count == 0;

        internal FunctionalMldsV2ValidationReport(IEnumerable<FunctionalMldsV2ValidationIssue> issues)
        {
            Issues = issues.ToList().AsReadOnly();
        }

        public string ToDisplayString()
        {
            return IsValid
                ? "FunctionalMLDS V2 validation passed."
                : "FunctionalMLDS V2 validation failed:\n" + string.Join("\n", Issues.Select(issue => "- " + issue));
        }
    }

    public static class FunctionalMldsV2InvariantValidator
    {
        public static readonly HashSet<string> AssertionTypes = new HashSet<string>(StringComparer.Ordinal)
        {
            "StateAssertion", "EventAssertion", "OutputAssertion", "GroundingAssertion", "RelationAssertion"
        };

        private static readonly HashSet<string> RelationKinds = new HashSet<string>(StringComparer.Ordinal)
        {
            "sequence", "alternative", "exception", "fork", "join", "loop"
        };

        private static readonly Dictionary<string, string[]> ReferenceFields = new Dictionary<string, string[]>(StringComparer.Ordinal)
        {
            ["DynamicFunctionalModel"] = new[] { "requirementsModel", "verificationValidation", "actor", "scenario", "scenarioEvent", "scenarioCondition", "assertion", "scenarioSpecification", "runtimeBinding", "entity", "capability", "ownedRelationship", "verify", "satisfy" },
            ["RequirementsModel"] = new[] { "requirement", "useCase" },
            ["UseCase"] = new[] { "include", "extend", "extensionPoint" },
            ["ActorParticipation"] = new[] { "actor", "useCase" },
            ["UseCaseScenarioSpecification"] = new[] { "useCase", "scenario" },
            ["Scenario"] = new[] { "variantOf", "precondition", "postcondition", "step", "stepRelation", "parallelGroup" },
            ["ScenarioStep"] = new[] { "performedBy", "actorRole", "triggeredBy", "guard", "resultingAssertion", "capabilityUse", "occurrenceProbability" },
            ["StepRelation"] = new[] { "sourceStep", "targetStep", "source", "target", "guard", "probability" },
            ["ParallelGroup"] = new[] { "memberStep" },
            ["StateAssertion"] = new[] { "subject", "expression" },
            ["EventAssertion"] = new[] { "subject", "expression" },
            ["OutputAssertion"] = new[] { "subject", "expression" },
            ["GroundingAssertion"] = new[] { "subject", "expression" },
            ["RelationAssertion"] = new[] { "subject", "expression" },
            ["Agent"] = new[] { "providedCapability", "playsActor", "handoffTarget", "responsibleZone", "groundedAsset", "groundedObjectGroup" },
            ["Entity"] = new[] { "providedCapability", "objectGroup" },
            ["CapabilityUse"] = new[] { "typeRef", "provider", "target", "parameter" },
            ["Capability"] = new[] { "precondition", "effect" },
            ["Effect"] = new[] { "specifiedBy", "observableBy" },
            ["RuntimeBinding"] = new[] { "capability", "runtimeAction" },
            ["RuntimeAction"] = new[] { "locator", "inputSchema", "outputSchema", "runtimeParameter" },
            ["ParameterBinding"] = new[] { "capabilityParameter", "runtimeParameter", "transformation" },
            ["VerificationValidation"] = new[] { "vvCase", "validationCase", "vvTarget", "verify" },
            ["ValidationCase"] = new[] { "vvSubject", "vvTarget", "vvProcedure", "vvLog", "abstractVVCase" },
            ["RuntimeValidationProcedure"] = new[] { "vvStimuli", "vvIntendedOutcome", "abstractVVProcedure" },
            ["RuntimeStimulus"] = new[] { "scenarioEvent", "runtimeAction" },
            ["StateAssertionOutcome"] = new[] { "assertion" },
            ["RuntimeValidationTarget"] = new[] { "element", "runtimeBinding" },
            ["RuntimeValidationLog"] = new[] { "performedVVProcedure", "vvActualOutcome", "actualOutcome" },
            ["RuntimeActualOutcome"] = new[] { "intendedOutcome", "result" },
            ["AssertionResult"] = new[] { "assertion", "observedValue" },
            ["ValidationCaseUseCaseBinding"] = new[] { "validationCase", "useCase" },
            ["Satisfy"] = new[] { "satisfiedRequirement", "satisfiedBy", "satisfiedUseCase" },
            ["Verify"] = new[] { "requirement", "verifiedRequirement", "vvCase", "verifiedByCase", "vvProcedure", "verifiedByProcedure" }
        };

        public static FunctionalMldsV2ValidationReport Validate(FunctionalMldsV2Document document, FunctionalMldsV2ModelIndex index)
        {
            var issues = new List<FunctionalMldsV2ValidationIssue>();
            ValidateReferences(index, issues);
            ValidateRoot(index, issues);
            ValidateScenarios(index, issues);
            ValidateAssertions(index, issues);
            ValidateCapabilities(index, issues);
            ValidateRuntime(index, issues);
            ValidateVerification(index, issues);
            return new FunctionalMldsV2ValidationReport(issues);
        }

        private static void ValidateReferences(FunctionalMldsV2ModelIndex index, List<FunctionalMldsV2ValidationIssue> issues)
        {
            foreach (var item in index.Objects)
            {
                string[] fields;
                if (!ReferenceFields.TryGetValue(item.Type, out fields))
                    continue;
                foreach (var field in fields)
                {
                    try
                    {
                        foreach (var id in item.References(field))
                        {
                            if (index.Get(id) == null)
                                Add(issues, "REF-001", item, $"{field} references missing object {id}.");
                        }
                    }
                    catch (Exception exception)
                    {
                        Add(issues, "REF-002", item, exception.Message);
                    }
                }
            }
        }

        private static void ValidateRoot(FunctionalMldsV2ModelIndex index, List<FunctionalMldsV2ValidationIssue> issues)
        {
            var roots = index.OfType("DynamicFunctionalModel").ToList();
            if (roots.Count != 1)
            {
                issues.Add(new FunctionalMldsV2ValidationIssue("INV-ROOT", "<document>", $"Exactly one DynamicFunctionalModel is required, got {roots.Count}."));
                return;
            }
            if (!string.Equals(roots[0].Id, index.Document.Id, StringComparison.Ordinal))
                Add(issues, "INV-ROOT-ID", roots[0], "Document.id must equal the DynamicFunctionalModel root id.");
            Exact(roots[0], "requirementsModel", 1, "INV-063", issues);
            Exact(roots[0], "verificationValidation", 1, "INV-034", issues);
            RequireReferencedType(roots[0], "requirementsModel", "RequirementsModel", index, issues);
            RequireReferencedType(roots[0], "verificationValidation", "VerificationValidation", index, issues);
        }

        private static void ValidateScenarios(FunctionalMldsV2ModelIndex index, List<FunctionalMldsV2ValidationIssue> issues)
        {
            foreach (var probabilityValue in index.OfType("ProbabilityValue"))
            {
                var value = probabilityValue.OptionalNumber("value");
                if (!value.HasValue)
                    Add(issues, "INV-018", probabilityValue, "ProbabilityValue.value is required.");
                else if (value.Value < 0 || value.Value > 1)
                    Add(issues, "INV-018", probabilityValue, "ProbabilityValue.value must be in [0,1].");
            }

            foreach (var condition in index.OfType("ScenarioCondition"))
            {
                if (condition.OptionalString("datatype") != "EABoolean")
                    Add(issues, "INV-015", condition, "ScenarioCondition.datatype must be EABoolean.");
            }

            foreach (var scenario in index.OfType("Scenario"))
            {
                var kind = scenario.OptionalString("kind");
                if (kind == "main" && scenario.References("variantOf").Count != 0)
                    Add(issues, "INV-009", scenario, "A main Scenario must not have variantOf.");
                if (kind != "main")
                {
                    Exact(scenario, "variantOf", 1, "INV-010", issues);
                    var main = FirstReference(scenario, "variantOf", index);
                    if (main != null && main.OptionalString("kind") != "main")
                        Add(issues, "INV-010", scenario, "A variant must reference a main Scenario.");
                }

                var steps = scenario.References("step");
                var relations = scenario.References("stepRelation");
                if (steps.Count == 0)
                    Add(issues, "SCN-STEP", scenario, "A Scenario requires at least one ScenarioStep.");
                if (steps.Count > 1 && relations.Count == 0)
                    Add(issues, "INV-011", scenario, "A multi-step Scenario requires explicit StepRelations.");

                var stepSet = new HashSet<string>(steps, StringComparer.Ordinal);
                var branchGroups = new Dictionary<string, List<double>>(StringComparer.Ordinal);
                var branchCounts = new Dictionary<string, int>(StringComparer.Ordinal);
                foreach (var relationId in relations)
                {
                    var relation = index.Get(relationId);
                    if (relation == null)
                        continue;
                    Exact(relation, "sourceStep", 1, "INV-071", issues);
                    Exact(relation, "targetStep", 1, "INV-071", issues);
                    RequireReferencedType(relation, "sourceStep", "ScenarioStep", index, issues);
                    RequireReferencedType(relation, "targetStep", "ScenarioStep", index, issues);
                    var source = relation.References("sourceStep").FirstOrDefault();
                    var target = relation.References("targetStep").FirstOrDefault();
                    ValidateAlias(relation, "sourceStep", "source", issues);
                    ValidateAlias(relation, "targetStep", "target", issues);
                    if (!stepSet.Contains(source) || !stepSet.Contains(target))
                        Add(issues, "INV-071", relation, "Both StepRelation endpoints must belong to the owning Scenario.");
                    var relationKind = relation.OptionalString("kind");
                    if (!RelationKinds.Contains(relationKind ?? string.Empty))
                        Add(issues, "INV-011", relation, $"Unsupported StepRelation kind: {relationKind ?? "<null>"}.");
                    var probability = ReferencedProbability(relation, "probability", index, issues);
                    if (probability.HasValue)
                    {
                        if (relationKind != "alternative" && relationKind != "exception")
                            Add(issues, "INV-073", relation, "Only alternative/exception relations may carry probability.");
                        if (probability.Value < 0 || probability.Value > 1)
                            Add(issues, "INV-018", relation, "Probability must be in [0,1].");
                    }
                    if (relationKind == "alternative" || relationKind == "exception")
                    {
                        if (!branchGroups.ContainsKey(source))
                        {
                            branchGroups[source] = new List<double>();
                            branchCounts[source] = 0;
                        }
                        branchCounts[source]++;
                        if (probability.HasValue)
                            branchGroups[source].Add(probability.Value);
                    }
                }
                foreach (var pair in branchGroups)
                {
                    if (pair.Value.Count == branchCounts[pair.Key] && Math.Abs(pair.Value.Sum() - 1.0) > 0.000001)
                        Add(issues, "INV-074", scenario, $"Complete probabilistic branch at {pair.Key} must sum to 1.0.");
                }

                foreach (var groupId in scenario.References("parallelGroup"))
                {
                    var group = index.Get(groupId);
                    if (group == null)
                        continue;
                    var members = group.References("memberStep");
                    if (members.Count < 2 || members.Any(member => !stepSet.Contains(member)))
                        Add(issues, "INV-072", group, "ParallelGroup requires at least two members in the same Scenario.");
                    if (!HasForkJoinBounds(members, relations, index))
                        Add(issues, "INV-072", group, "ParallelGroup members must be bounded by a common fork and join.");
                }
            }

            foreach (var step in index.OfType("ScenarioStep"))
            {
                ReferencedProbability(step, "occurrenceProbability", index, issues);
                if (step.Has("runtimeAction") || step.Has("runtimeActions") || step.Has("runtimeActionIds"))
                    Add(issues, "INV-014", step, "ScenarioStep must not directly reference RuntimeAction.");
            }
        }

        private static void ValidateAssertions(FunctionalMldsV2ModelIndex index, List<FunctionalMldsV2ValidationIssue> issues)
        {
            foreach (var item in index.Objects.Where(candidate => AssertionTypes.Contains(candidate.Type)))
            {
                Exact(item, "subject", 1, "INV-066", issues);
                Exact(item, "expression", 1, "INV-066", issues);
                RequireReferencedType(item, "expression", "EAExpression", index, issues);
                var severity = item.OptionalString("severity");
                if (severity != null && !new[] { "info", "warning", "error", "critical" }.Contains(severity))
                    Add(issues, "AST-SEVERITY", item, "Invalid assertion severity.");
            }

            foreach (var result in index.OfType("AssertionResult"))
            {
                Exact(result, "assertion", 1, "INV-067", issues);
                RequireReferencedType(result, "assertion", "Assertion", index, issues);
                FunctionalMldsV2AssertionVerdict verdict;
                if (!FunctionalMldsV2Lexemes.TryVerdict(result.OptionalString("verdict") ?? string.Empty, out verdict))
                    Add(issues, "INV-067", result, "AssertionResult.verdict must be pass/fail/inconclusive/error.");
                if (result.References("observedValue").Count > 1)
                    Add(issues, "INV-067", result, "AssertionResult.observedValue multiplicity is [0..1].");
            }
        }

        private static void ValidateCapabilities(FunctionalMldsV2ModelIndex index, List<FunctionalMldsV2ValidationIssue> issues)
        {
            foreach (var capability in index.OfType("Capability"))
            {
                if (capability.References("effect").Count == 0)
                    Add(issues, "INV-022", capability, "Capability requires at least one Effect.");
                RequireReferencedType(capability, "effect", "Effect", index, issues);
            }
            foreach (var effect in index.OfType("Effect"))
            {
                if (effect.References("specifiedBy").Count == 0)
                    Add(issues, "INV-023", effect, "Effect requires at least one specifiedBy Assertion.");
                RequireReferencedType(effect, "specifiedBy", "Assertion", index, issues);
                if (effect.Has("evidencedBy"))
                    Add(issues, "INV-023", effect, "evidencedBy is a v0.5 projection field and is forbidden in native V2.");
            }
            foreach (var use in index.OfType("CapabilityUse"))
            {
                Exact(use, "typeRef", 1, "INV-021", issues);
                RequireReferencedType(use, "typeRef", "Capability", index, issues);
                Exact(use, "provider", 1, "INV-065", issues);
                RequireReferencedType(use, "provider", "Entity", index, issues);
                var stepId = index.StepOfCapabilityUse(use.Id);
                if (stepId == null)
                {
                    Add(issues, "CAP-OWNER", use, "CapabilityUse must be composed by exactly one ScenarioStep.");
                    continue;
                }
                var step = index.Get(stepId);
                var provider = use.References("provider").FirstOrDefault();
                var capability = use.References("typeRef").FirstOrDefault();
                if (provider != null && !step.References("performedBy").Contains(provider))
                    Add(issues, "INV-064", use, "Provider must be a performer of the owning ScenarioStep.");
                var providerObject = index.Get(provider);
                if (providerObject != null && capability != null && !providerObject.References("providedCapability").Contains(capability))
                    Add(issues, "INV-064", use, "Provider must provide the Capability type.");
            }
        }

        private static void ValidateRuntime(FunctionalMldsV2ModelIndex index, List<FunctionalMldsV2ValidationIssue> issues)
        {
            foreach (var binding in index.OfType("RuntimeBinding"))
            {
                Exact(binding, "capability", 1, "RUN-CAP", issues);
                RequireReferencedType(binding, "capability", "Capability", index, issues);
                if (binding.References("runtimeAction").Count == 0)
                    Add(issues, "INV-030", binding, "RuntimeBinding requires at least one ordered RuntimeAction.");
                RequireReferencedType(binding, "runtimeAction", "RuntimeAction", index, issues);
                if (string.IsNullOrWhiteSpace(binding.OptionalString("targetPlatform")))
                    Add(issues, "RUN-PLATFORM", binding, "RuntimeBinding.targetPlatform is required.");
            }
            foreach (var action in index.OfType("RuntimeAction"))
            {
                Exact(action, "locator", 1, "INV-031", issues);
                var locator = FirstReference(action, "locator", index);
                if (locator == null || locator.Type != "RuntimeActionLocator")
                {
                    Add(issues, "INV-031", action, "RuntimeAction.locator must reference RuntimeActionLocator.");
                    continue;
                }
                var kind = locator.OptionalString("kind");
                if (kind != "endpoint" && kind != "tool" && kind != "topic")
                    Add(issues, "INV-032", locator, "Locator kind must be endpoint, tool or topic.");
                if (string.IsNullOrWhiteSpace(locator.OptionalString("value")))
                    Add(issues, "INV-032", locator, "Locator value is required.");
                if (action.Has("endpoint") || action.Has("tool") || action.Has("topic"))
                    Add(issues, "INV-032", action, "Legacy locator slots are forbidden in native V2.");
            }
        }

        private static void ValidateVerification(FunctionalMldsV2ModelIndex index, List<FunctionalMldsV2ValidationIssue> issues)
        {
            foreach (var target in index.OfType("RuntimeValidationTarget"))
            {
                if (string.IsNullOrWhiteSpace(target.OptionalString("platform")))
                    Add(issues, "INV-069", target, "RuntimeValidationTarget.platform is required.");
                var elements = new HashSet<string>(target.References("element"), StringComparer.Ordinal);
                foreach (var binding in target.References("runtimeBinding"))
                {
                    var item = index.Get(binding);
                    if (item != null && item.Type != "RuntimeBinding")
                        Add(issues, "INV-069", target, $"{binding} is not a RuntimeBinding.");
                    if (!elements.Contains(binding))
                        Add(issues, "INV-069", target, "runtimeBinding must be a subset of inherited element.");
                }
            }
            foreach (var validationCase in index.OfType("ValidationCase"))
            {
                foreach (var subjectId in validationCase.References("vvSubject"))
                {
                    var subject = index.Get(subjectId);
                    if (subject != null && !new[] { "ScenarioStep", "Capability", "RuntimeBinding", "Entity", "Agent" }.Contains(subject.Type))
                        Add(issues, "INV-070", validationCase, $"Invalid vvSubject type {subject.Type}.");
                }
            }
            foreach (var stimulus in index.OfType("RuntimeStimulus"))
            {
                if (stimulus.References("scenarioEvent").Count == 0 && stimulus.References("runtimeAction").Count == 0)
                    Add(issues, "INV-056", stimulus, "RuntimeStimulus needs a ScenarioEvent or RuntimeAction.");
            }
            foreach (var outcome in index.OfType("RuntimeActualOutcome"))
            {
                if (outcome.References("result").Count == 0)
                    Add(issues, "INV-068", outcome, "RuntimeActualOutcome requires at least one AssertionResult.");
                RequireReferencedType(outcome, "result", "AssertionResult", index, issues);
                if (index.LogOfActualOutcome(outcome.Id) == null)
                    Add(issues, "INV-040", outcome, "RuntimeActualOutcome must be owned by RuntimeValidationLog.");
            }
        }

        private static bool HasForkJoinBounds(IReadOnlyList<string> members, IReadOnlyList<string> relationIds, FunctionalMldsV2ModelIndex index)
        {
            if (members.Count < 2)
                return false;
            var forkSources = new HashSet<string>();
            var joinTargets = new HashSet<string>();
            foreach (var member in members)
            {
                var incomingForkSources = relationIds
                    .Select(index.Get)
                    .Where(relation => relation != null && relation.OptionalString("kind") == "fork" && relation.References("targetStep").Contains(member))
                    .SelectMany(relation => relation.References("sourceStep"))
                    .ToHashSet(StringComparer.Ordinal);
                var outgoingJoinTargets = relationIds
                    .Select(index.Get)
                    .Where(relation => relation != null && relation.OptionalString("kind") == "join" && relation.References("sourceStep").Contains(member))
                    .SelectMany(relation => relation.References("targetStep"))
                    .ToHashSet(StringComparer.Ordinal);
                if (forkSources.Count == 0)
                    forkSources.UnionWith(incomingForkSources);
                else
                    forkSources.IntersectWith(incomingForkSources);
                if (joinTargets.Count == 0)
                    joinTargets.UnionWith(outgoingJoinTargets);
                else
                    joinTargets.IntersectWith(outgoingJoinTargets);
            }
            return forkSources.Count > 0 && joinTargets.Count > 0;
        }

        private static double? ReferencedProbability(
            FunctionalMldsV2Object owner,
            string field,
            FunctionalMldsV2ModelIndex index,
            List<FunctionalMldsV2ValidationIssue> issues)
        {
            IReadOnlyList<string> references;
            try
            {
                references = owner.References(field);
            }
            catch (Exception exception)
            {
                Add(issues, "INV-018", owner, exception.Message);
                return null;
            }
            if (references.Count == 0)
                return null;
            if (references.Count != 1)
            {
                Add(issues, "INV-018", owner, $"{field} requires at most one ProbabilityValue.");
                return null;
            }
            var probability = index.Get(references[0]);
            if (probability == null)
                return null;
            if (probability.Type != "ProbabilityValue")
            {
                Add(issues, "INV-018", owner, $"{field} must reference ProbabilityValue, got {probability.Type}.");
                return null;
            }
            var value = probability.OptionalNumber("value");
            if (!value.HasValue)
                Add(issues, "INV-018", probability, "ProbabilityValue.value is required.");
            return value;
        }

        private static void ValidateAlias(
            FunctionalMldsV2Object owner,
            string canonicalField,
            string aliasField,
            List<FunctionalMldsV2ValidationIssue> issues)
        {
            if (!owner.Has(aliasField))
                return;
            try
            {
                if (!owner.References(canonicalField).SequenceEqual(owner.References(aliasField)))
                    Add(issues, "SERIALIZATION-ALIAS", owner, $"{aliasField} must equal canonical {canonicalField}.");
            }
            catch (Exception exception)
            {
                Add(issues, "SERIALIZATION-ALIAS", owner, exception.Message);
            }
        }

        private static FunctionalMldsV2Object FirstReference(FunctionalMldsV2Object item, string field, FunctionalMldsV2ModelIndex index)
        {
            var id = item.References(field).FirstOrDefault();
            return id == null ? null : index.Get(id);
        }

        private static void RequireReferencedType(
            FunctionalMldsV2Object owner,
            string field,
            string expectedType,
            FunctionalMldsV2ModelIndex index,
            List<FunctionalMldsV2ValidationIssue> issues)
        {
            foreach (var id in owner.References(field))
            {
                var target = index.Get(id);
                if (target != null && !index.IsInstanceOf(target, expectedType))
                    Add(issues, "TYPE-REF", owner, $"{field} expects {expectedType}, got {target.Type} ({id}).");
            }
        }

        private static void Exact(FunctionalMldsV2Object item, string field, int count, string code, List<FunctionalMldsV2ValidationIssue> issues)
        {
            try
            {
                var actual = item.References(field).Count;
                if (actual != count)
                    Add(issues, code, item, $"{field} requires exactly {count} reference(s), got {actual}.");
            }
            catch (Exception exception)
            {
                Add(issues, code, item, exception.Message);
            }
        }

        private static void Add(List<FunctionalMldsV2ValidationIssue> issues, string code, FunctionalMldsV2Object item, string message)
        {
            issues.Add(new FunctionalMldsV2ValidationIssue(code, item == null ? "<null>" : item.Id, message));
        }
    }
}
