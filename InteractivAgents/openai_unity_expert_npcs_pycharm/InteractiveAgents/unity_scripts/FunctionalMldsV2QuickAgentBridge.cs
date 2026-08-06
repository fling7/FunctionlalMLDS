using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using FunctionalMlds.V2;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

/// <summary>
/// Binds QuickAgentManager to the native V2 model and the exact backend trace map.
/// No model identifier is derived from a display name, endpoint, or ID suffix.
/// </summary>
public sealed class FunctionalMldsV2QuickAgentBridge
{
    private const string ModelVersion = "2.0.0-model";
    private const string LegacyVersion = "v0.5";
    private const string RuntimeContextSchema = "functionalmlds_runtime_context_v2";

    private readonly FunctionalMldsV2LoadResult loaded;
    private readonly FunctionalMldsV2RuntimeContext context;
    private readonly FunctionalMldsV2RuntimeLogger logger;
    private readonly FunctionalMldsV2ValidationRecorder recorder;
    private readonly Dictionary<string, RuntimeMapping> mappings;
    private readonly string validationLogPath;

    public string CaseId { get; }
    public string ModelSha256 => loaded.Sha256;

    private FunctionalMldsV2QuickAgentBridge(
        string caseId,
        FunctionalMldsV2LoadResult loaded,
        FunctionalMldsV2RuntimeContext context,
        FunctionalMldsV2RuntimeLogger logger,
        FunctionalMldsV2ValidationRecorder recorder,
        Dictionary<string, RuntimeMapping> mappings,
        string validationLogPath)
    {
        CaseId = caseId;
        this.loaded = loaded;
        this.context = context;
        this.logger = logger;
        this.recorder = recorder;
        this.mappings = mappings;
        this.validationLogPath = validationLogPath;
    }

    /// <summary>
    /// Returns null for unversioned/direct or explicit v0.5 setup responses. Unknown versions
    /// and incomplete V2 responses fail closed.
    /// </summary>
    public static string ModelEndpointFor(string setupJson)
    {
        var root = ParseObject(setupJson, "setup response");
        var version = Text(root["metamodel_version"]);
        if (string.IsNullOrEmpty(version) || string.Equals(version, LegacyVersion, StringComparison.Ordinal))
            return null;
        if (!string.Equals(version, ModelVersion, StringComparison.Ordinal))
            throw new FunctionalMldsV2FormatException($"Unsupported FunctionalMLDS model version '{version}'.");
        var endpoint = Text(root["functionalmlds_model_endpoint"]);
        if (string.IsNullOrEmpty(endpoint))
            throw new FunctionalMldsV2FormatException("V2 setup response has no functionalmlds_model_endpoint.");
        return endpoint;
    }

    public static FunctionalMldsV2QuickAgentBridge Create(
        string setupJson,
        string modelJson,
        string logDirectory)
    {
        var root = ParseObject(setupJson, "setup response");
        var version = RequiredText(root, "metamodel_version");
        if (!string.Equals(version, ModelVersion, StringComparison.Ordinal))
            throw new FunctionalMldsV2FormatException("QuickAgent V2 bridge requires model version 2.0.0-model.");

        var runtime = root["functionalmlds"] as JObject;
        if (runtime == null || !string.Equals(Text(runtime["schema"]), RuntimeContextSchema, StringComparison.Ordinal))
            throw new FunctionalMldsV2FormatException("Setup response has no valid V2 runtime context.");
        if (!string.Equals(RequiredText(runtime, "model_version"), ModelVersion, StringComparison.Ordinal))
            throw new FunctionalMldsV2FormatException("Runtime context model version does not match setup metadata.");
        if (!string.Equals(RequiredText(runtime, "profile"), "executable", StringComparison.Ordinal))
            throw new FunctionalMldsV2FormatException("QuickAgent requires the executable V2 profile.");

        var expectedHash = RequiredText(root, "model_sha256").ToUpperInvariant();
        if (!string.Equals(expectedHash, RequiredText(runtime, "model_sha256").ToUpperInvariant(), StringComparison.Ordinal))
            throw new FunctionalMldsV2FormatException("Setup and runtime-context model hashes differ.");

        var loaded = FunctionalMldsV2Loader.LoadJson(modelJson, "backend:functionalmlds-v2", validate: true);
        if (!string.Equals(loaded.Sha256, expectedHash, StringComparison.Ordinal))
            throw new FunctionalMldsV2FormatException(
                $"Downloaded V2 model hash mismatch: expected {expectedHash}, got {loaded.Sha256}.");

        var caseId = RequiredText(runtime, "case_id");
        if (!string.IsNullOrWhiteSpace(loaded.Document.CaseId)
            && !string.Equals(loaded.Document.CaseId, caseId, StringComparison.Ordinal))
            throw new FunctionalMldsV2FormatException("Runtime context case_id does not match the downloaded model.");
        var scenarioId = RequiredText(runtime, "main_scenario_id");
        var sessionId = RequiredText(root, "session_id");
        var context = FunctionalMldsV2RuntimeContext.Create(loaded, scenarioId, sessionId);

        var mappings = ParseMappings(runtime["runtime_actions"], loaded.Index, scenarioId, caseId);
        foreach (var requiredKind in new[] { "setup", "chat", "handoff" })
        {
            if (!mappings.ContainsKey(requiredKind))
                throw new FunctionalMldsV2FormatException($"V2 runtime context has no exact '{requiredKind}' mapping.");
        }

        var directory = Path.GetFullPath(logDirectory ?? string.Empty);
        Directory.CreateDirectory(directory);
        var eventPath = Path.Combine(directory, "events.v2.jsonl");
        var validationPath = Path.Combine(directory, "runtime_validation.v2.jsonl");
        return new FunctionalMldsV2QuickAgentBridge(
            caseId,
            loaded,
            context,
            new FunctionalMldsV2RuntimeLogger(eventPath, loaded.Index, context),
            new FunctionalMldsV2ValidationRecorder(loaded),
            mappings,
            validationPath);
    }

    public void RequireAction(string actionKind, string activeAgentId)
    {
        var mapping = Mapping(actionKind);
        context.ActiveAgentId = string.IsNullOrWhiteSpace(activeAgentId) ? null : activeAgentId.Trim();
        context.SetActiveSteps(new[] { mapping.Execution.ScenarioStepId }, loaded.Index);
    }

    public FunctionalMldsV2RuntimeEvent Record(
        string actionKind,
        string eventType,
        string activeAgentId,
        string status,
        object inputSummary,
        object outputSummary,
        double? durationMs = null,
        string errorSummary = null)
    {
        var mapping = Mapping(actionKind);
        RequireAction(actionKind, activeAgentId);
        var runtimeEvent = logger.Append(
            eventType,
            mapping.Execution,
            mapping.TraceReferences,
            status,
            inputSummary,
            outputSummary,
            durationMs,
            errorSummary,
            new JObject { ["application_action_kind"] = mapping.ActionKind });

        var verdict = status == "error"
            ? "error"
            : status == "failed"
                ? "fail"
                : "inconclusive";
        var observed = outputSummary == null ? JValue.CreateNull() : JToken.FromObject(outputSummary);
        var evaluations = mapping.TraceReferences.AssertionIds.Select(
            assertionId => new FunctionalMldsV2AssertionEvaluation
            {
                Id = "assertion-result-" + Guid.NewGuid().ToString("N"),
                AssertionId = assertionId,
                Verdict = verdict,
                ObservedValue = observed.DeepClone(),
                EvidenceRef = "runtime-event://" + runtimeEvent.EventId,
                Timestamp = runtimeEvent.Timestamp,
                Message = "Transport observation recorded; domain probe evaluation is not available."
            }).ToList();
        var validation = recorder.Record(
            CaseId,
            mapping.TraceReferences.ValidationCaseIds,
            mapping.TraceReferences.RuntimeValidationTargetIds,
            evaluations,
            context.SessionId);
        File.AppendAllText(
            validationLogPath,
            JsonConvert.SerializeObject(validation, Formatting.None) + Environment.NewLine);
        return runtimeEvent;
    }

    private RuntimeMapping Mapping(string actionKind)
    {
        var normalized = (actionKind ?? string.Empty).Trim().ToLowerInvariant();
        RuntimeMapping mapping;
        if (!mappings.TryGetValue(normalized, out mapping))
            throw new FunctionalMldsV2FormatException($"No exact V2 trace mapping for '{actionKind}'.");
        return mapping;
    }

    private static Dictionary<string, RuntimeMapping> ParseMappings(
        JToken token,
        FunctionalMldsV2ModelIndex index,
        string scenarioId,
        string caseId)
    {
        var array = token as JArray;
        if (array == null || array.Count == 0)
            throw new FunctionalMldsV2FormatException("V2 runtime context contains no runtime_actions.");
        var result = new Dictionary<string, RuntimeMapping>(StringComparer.Ordinal);
        var actualChains = new HashSet<string>(StringComparer.Ordinal);
        foreach (var raw in array.OfType<JObject>())
        {
            var kind = RequiredText(raw, "action_kind").ToLowerInvariant();
            if (kind != "setup" && kind != "chat" && kind != "handoff" && kind != "runtime")
                throw new FunctionalMldsV2FormatException($"Unsupported application action kind '{kind}'.");
            if (kind != "runtime" && result.ContainsKey(kind))
                throw new FunctionalMldsV2FormatException($"Ambiguous V2 '{kind}' runtime mapping.");

            var execution = new FunctionalMldsV2ExecutionReference
            {
                ScenarioStepId = RequiredText(raw, "scenario_step_id"),
                CapabilityUseId = RequiredText(raw, "capability_use_id"),
                CapabilityId = RequiredText(raw, "capability_id"),
                ProviderId = RequiredText(raw, "provider_entity_id"),
                TargetIds = Strings(raw["target_ids"]),
                RuntimeBindingId = RequiredText(raw, "runtime_binding_id"),
                RuntimeActionId = RequiredText(raw, "runtime_action_id")
            };
            var references = new FunctionalMldsV2TraceReferences
            {
                CaseId = caseId,
                AssertionIds = Strings(raw["assertion_ids"]),
                ValidationCaseIds = Strings(raw["validation_case_ids"]),
                RuntimeValidationTargetIds = Strings(raw["runtime_validation_target_ids"])
            };
            ValidateMapping(raw, kind, execution, references, index, scenarioId);
            if (!actualChains.Add(ChainKey(execution)))
                throw new FunctionalMldsV2FormatException("V2 runtime context contains a duplicate runtime chain.");
            if (kind != "runtime")
                result.Add(kind, new RuntimeMapping(kind, execution, references));
        }
        var expectedChains = ExpectedChainKeys(index);
        if (!actualChains.SetEquals(expectedChains))
            throw new FunctionalMldsV2FormatException(
                "V2 runtime context is not a complete, exact projection of the native runtime chains.");
        return result;
    }

    private static void ValidateMapping(
        JObject raw,
        string actionKind,
        FunctionalMldsV2ExecutionReference execution,
        FunctionalMldsV2TraceReferences references,
        FunctionalMldsV2ModelIndex index,
        string scenarioId)
    {
        var step = index.Require(execution.ScenarioStepId, "ScenarioStep");
        var use = index.Require(execution.CapabilityUseId, "CapabilityUse");
        var capability = index.Require(execution.CapabilityId, "Capability");
        var provider = index.Require(execution.ProviderId, "Entity");
        var binding = index.Require(execution.RuntimeBindingId, "RuntimeBinding");
        var action = index.Require(execution.RuntimeActionId, "RuntimeAction");
        if (index.ScenarioOfStep(step.Id) != scenarioId
            || index.StepOfCapabilityUse(use.Id) != step.Id
            || use.References("typeRef").Single() != capability.Id
            || use.References("provider").Single() != provider.Id
            || !step.References("performedBy").Contains(provider.Id)
            || !provider.References("providedCapability").Contains(capability.Id)
            || binding.References("capability").Single() != capability.Id
            || !binding.References("runtimeAction").Contains(action.Id))
            throw new FunctionalMldsV2FormatException("V2 runtime mapping does not resolve through the normative chain.");
        if (!new HashSet<string>(use.References("target"), StringComparer.Ordinal)
            .SetEquals(execution.TargetIds ?? new List<string>()))
            throw new FunctionalMldsV2FormatException("V2 runtime mapping target_ids differ from CapabilityUse.target.");

        var modeledActionKind = ModeledActionKind(action, index);
        if (!string.Equals(actionKind, modeledActionKind, StringComparison.Ordinal))
            throw new FunctionalMldsV2FormatException(
                "V2 runtime mapping action_kind differs from RuntimeAction.inputSchema applicationActionKind.");

        var locatorTrace = raw["locator"] as JObject;
        var locator = index.Require(action.References("locator").Single(), "RuntimeActionLocator");
        if (locatorTrace == null
            || !string.Equals(RequiredText(locatorTrace, "kind"), locator.RequiredString("kind"), StringComparison.Ordinal)
            || !string.Equals(RequiredText(locatorTrace, "value"), locator.RequiredString("value"), StringComparison.Ordinal))
            throw new FunctionalMldsV2FormatException("V2 trace locator differs from the native RuntimeAction locator.");

        var expectedAssertions = capability.References("effect")
            .Select(effectId => index.Require(effectId, "Effect"))
            .SelectMany(effect => effect.References("specifiedBy"))
            .Distinct(StringComparer.Ordinal)
            .ToList();
        foreach (var id in expectedAssertions)
            index.Require(id, "Assertion");
        if (!references.AssertionIds.SequenceEqual(expectedAssertions))
            throw new FunctionalMldsV2FormatException(
                "V2 runtime mapping assertion_ids differ from Capability.effect.specifiedBy.");

        var expectedCases = index.OfType("ValidationCase")
            .Where(item => item.References("vvSubject").Contains(binding.Id))
            .Select(item => item.Id)
            .Distinct(StringComparer.Ordinal)
            .ToList();
        if (!SetEquals(references.ValidationCaseIds, expectedCases))
            throw new FunctionalMldsV2FormatException(
                "V2 runtime mapping validation_case_ids differ from ValidationCase.vvSubject.");

        var expectedTargets = expectedCases
            .Select(caseId => index.Require(caseId, "ValidationCase"))
            .SelectMany(validationCase => validationCase.References("vvTarget"))
            .Select(targetId => index.Require(targetId, "RuntimeValidationTarget"))
            .Where(target => target.References("runtimeBinding").Contains(binding.Id))
            .Select(target => target.Id)
            .Distinct(StringComparer.Ordinal)
            .ToList();
        if (!SetEquals(references.RuntimeValidationTargetIds, expectedTargets))
            throw new FunctionalMldsV2FormatException(
                "V2 runtime mapping runtime_validation_target_ids differ from the modeled V&V binding.");
    }

    private static string ModeledActionKind(
        FunctionalMldsV2Object action,
        FunctionalMldsV2ModelIndex index)
    {
        var markers = new List<string>();
        foreach (var schemaId in action.References("inputSchema"))
        {
            var schema = index.Require(schemaId, "SchemaReference");
            var text = schema.OptionalString("text");
            if (string.IsNullOrWhiteSpace(text))
                continue;
            JObject payload;
            try { payload = JObject.Parse(text); }
            catch (JsonException) { continue; }
            var marker = Text(payload["applicationActionKind"])?.ToLowerInvariant();
            if (!string.IsNullOrWhiteSpace(marker))
                markers.Add(marker);
        }
        var allowed = new HashSet<string>(new[] { "setup", "chat", "handoff", "runtime" }, StringComparer.Ordinal);
        if (markers.Count != 1 || !allowed.Contains(markers[0]))
            throw new FunctionalMldsV2FormatException(
                $"RuntimeAction {action.Id} requires exactly one modeled applicationActionKind.");
        return markers[0];
    }

    private static HashSet<string> ExpectedChainKeys(FunctionalMldsV2ModelIndex index)
    {
        var expected = new HashSet<string>(StringComparer.Ordinal);
        foreach (var binding in index.OfType("RuntimeBinding"))
        {
            var capabilityId = binding.References("capability").Single();
            foreach (var actionId in binding.References("runtimeAction"))
            foreach (var use in index.OfType("CapabilityUse")
                         .Where(item => item.References("typeRef").Single() == capabilityId))
            {
                var stepId = index.StepOfCapabilityUse(use.Id);
                var providerId = use.References("provider").Single();
                if (string.IsNullOrWhiteSpace(stepId))
                    throw new FunctionalMldsV2FormatException(
                        $"CapabilityUse {use.Id} is not owned by exactly one ScenarioStep.");
                expected.Add(string.Join("\u001f", new[]
                {
                    stepId, use.Id, capabilityId, providerId, binding.Id, actionId
                }));
            }
        }
        return expected;
    }

    private static string ChainKey(FunctionalMldsV2ExecutionReference execution)
    {
        return string.Join("\u001f", new[]
        {
            execution.ScenarioStepId,
            execution.CapabilityUseId,
            execution.CapabilityId,
            execution.ProviderId,
            execution.RuntimeBindingId,
            execution.RuntimeActionId
        });
    }

    private static bool SetEquals(IEnumerable<string> left, IEnumerable<string> right)
    {
        var leftList = (left ?? Enumerable.Empty<string>()).ToList();
        var rightList = (right ?? Enumerable.Empty<string>()).ToList();
        return leftList.Count == rightList.Count
            && new HashSet<string>(leftList, StringComparer.Ordinal).SetEquals(rightList);
    }

    private static JObject ParseObject(string json, string label)
    {
        if (string.IsNullOrWhiteSpace(json))
            throw new FunctionalMldsV2FormatException(label + " is empty.");
        try
        {
            return JObject.Parse(json);
        }
        catch (JsonException exception)
        {
            throw new FunctionalMldsV2FormatException(label + " is not valid JSON.", exception);
        }
    }

    private static string RequiredText(JObject obj, string property)
    {
        var value = Text(obj[property]);
        if (string.IsNullOrWhiteSpace(value))
            throw new FunctionalMldsV2FormatException(property + " is required.");
        return value;
    }

    private static string Text(JToken token)
    {
        return token == null || token.Type == JTokenType.Null ? null : token.Value<string>()?.Trim();
    }

    private static List<string> Strings(JToken token)
    {
        var array = token as JArray;
        if (array == null)
            return new List<string>();
        var result = array.Select(Text).Where(value => !string.IsNullOrWhiteSpace(value)).ToList();
        if (result.Count != result.Distinct(StringComparer.Ordinal).Count())
            throw new FunctionalMldsV2FormatException("Trace reference array contains duplicate IDs.");
        return result;
    }

    private sealed class RuntimeMapping
    {
        public string ActionKind { get; }
        public FunctionalMldsV2ExecutionReference Execution { get; }
        public FunctionalMldsV2TraceReferences TraceReferences { get; }

        public RuntimeMapping(
            string actionKind,
            FunctionalMldsV2ExecutionReference execution,
            FunctionalMldsV2TraceReferences traceReferences)
        {
            ActionKind = actionKind;
            Execution = execution;
            TraceReferences = traceReferences;
        }
    }
}
