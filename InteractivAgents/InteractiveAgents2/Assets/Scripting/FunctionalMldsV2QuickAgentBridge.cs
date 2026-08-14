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
    private readonly FunctionalMldsV2ValidationRecorder recorder;
    private readonly FunctionalMldsV2InteractionEvidenceEvaluator interactionEvaluator;
    private readonly Dictionary<string, List<RuntimeMapping>> mappings;
    private readonly Dictionary<string, ScenarioRuntime> scenarioRuntimes;
    private readonly string validationLogPath;

    public string CaseId { get; }
    public string ModelSha256 => loaded.Sha256;

    private FunctionalMldsV2QuickAgentBridge(
        string caseId,
        FunctionalMldsV2LoadResult loaded,
        FunctionalMldsV2ValidationRecorder recorder,
        FunctionalMldsV2InteractionEvidenceEvaluator interactionEvaluator,
        Dictionary<string, List<RuntimeMapping>> mappings,
        Dictionary<string, ScenarioRuntime> scenarioRuntimes,
        string validationLogPath)
    {
        CaseId = caseId;
        this.loaded = loaded;
        this.recorder = recorder;
        this.interactionEvaluator = interactionEvaluator;
        this.mappings = mappings;
        this.scenarioRuntimes = scenarioRuntimes;
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
        loaded.Index.Require(scenarioId, "Scenario");

        var mappings = ParseMappings(runtime["runtime_actions"], loaded.Index, scenarioId, caseId);
        foreach (var requiredKind in new[] { "setup", "chat", "handoff" })
        {
            if (!mappings.ContainsKey(requiredKind) || mappings[requiredKind].Count == 0)
                throw new FunctionalMldsV2FormatException($"V2 runtime context has no exact '{requiredKind}' mapping.");
        }
        if (mappings["setup"].Count != 1)
            throw new FunctionalMldsV2FormatException("V2 runtime context must have exactly one setup mapping.");

        var directory = Path.GetFullPath(logDirectory ?? string.Empty);
        Directory.CreateDirectory(directory);
        var eventPath = Path.Combine(directory, "events.v2.jsonl");
        var validationPath = Path.Combine(directory, "runtime_validation.v2.jsonl");
        var scenarioRuntimes = mappings.Values
            .SelectMany(items => items)
            .Select(item => item.ScenarioId)
            .Distinct(StringComparer.Ordinal)
            .ToDictionary(
                id => id,
                id =>
                {
                    var scenarioContext = FunctionalMldsV2RuntimeContext.Create(loaded, id, sessionId);
                    return new ScenarioRuntime(
                        scenarioContext,
                        new FunctionalMldsV2RuntimeLogger(eventPath, loaded.Index, scenarioContext),
                        new FunctionalMldsV2ScenarioRunner(loaded.Index, scenarioContext));
                },
                StringComparer.Ordinal);
        return new FunctionalMldsV2QuickAgentBridge(
            caseId,
            loaded,
            new FunctionalMldsV2ValidationRecorder(loaded),
            new FunctionalMldsV2InteractionEvidenceEvaluator(loaded.Index, loaded.Sha256),
            mappings,
            scenarioRuntimes,
            validationPath);
    }

    public void RequireAction(
        string actionKind,
        string activeAgentId,
        FunctionalMldsV2InteractionObservation observation = null)
    {
        RequireMapping(Mapping(actionKind, observation, activeAgentId), activeAgentId);
    }

    public FunctionalMldsV2RuntimeEvent Record(
        string actionKind,
        string eventType,
        string activeAgentId,
        string status,
        object inputSummary,
        object outputSummary,
        double? durationMs = null,
        string errorSummary = null,
        FunctionalMldsV2InteractionObservation observation = null)
    {
        var mapping = Mapping(actionKind, observation, activeAgentId);
        var runtime = RequireMapping(mapping, activeAgentId);
        var runtimeEvent = runtime.Logger.Append(
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
            runtime.Context.SessionId);
        File.AppendAllText(
            validationLogPath,
            JsonConvert.SerializeObject(validation, Formatting.None) + Environment.NewLine);
        return runtimeEvent;
    }

    /// <summary>
    /// Records evidence produced by the real QuickAgent interaction path. Unlike Record, this
    /// method may emit pass/fail assertion outcomes. A successful HTTP transport alone must use
    /// Record and therefore remains inconclusive.
    /// </summary>
    public FunctionalMldsV2InteractionAssessment RecordInteraction(
        string actionKind,
        string eventType,
        string activeAgentId,
        FunctionalMldsV2InteractionObservation observation,
        object inputSummary,
        object outputSummary,
        double? durationMs = null)
    {
        var mapping = Mapping(actionKind, observation, activeAgentId);
        var runtime = RequireMapping(mapping, activeAgentId);
        var assessment = interactionEvaluator.Evaluate(mapping.Execution, observation);
        var eventStatus = string.Equals(assessment.Verdict, "pass", StringComparison.Ordinal)
            ? "success"
            : string.Equals(assessment.Verdict, "fail", StringComparison.Ordinal)
                ? "failed"
                : string.Equals(assessment.Verdict, "error", StringComparison.Ordinal)
                    ? "error"
                    : "inconclusive";
        var runtimeEvent = runtime.Logger.Append(
            eventType,
            mapping.Execution,
            mapping.TraceReferences,
            eventStatus,
            inputSummary,
            outputSummary,
            durationMs,
            eventStatus == "failed" || eventStatus == "error"
                ? ProbeSummary(assessment)
                : null,
            new JObject
            {
                ["application_action_kind"] = mapping.ActionKind,
                ["interaction_mode"] = observation?.InteractionMode,
                ["evidence_verdict"] = assessment.Verdict,
                ["target_resolved"] = assessment.TargetResolved,
                ["route_resolved"] = assessment.RouteResolved,
                ["completion_satisfied"] = assessment.CompletionSatisfied
            });

        assessment.RuntimeEventId = runtimeEvent.EventId;
        FunctionalMldsV2Transition transition;
        assessment.ScenarioStepCompleted = assessment.CompletionSatisfied
            && runtime.Runner.TryCompleteEvidenceBoundStep(
                mapping.Execution.ScenarioStepId,
                assessment.TargetResolved,
                assessment.RouteResolved,
                out transition);

        var observed = JToken.FromObject(
            new
            {
                assessment.Verdict,
                assessment.TargetResolved,
                assessment.RouteResolved,
                assessment.CompletionSatisfied,
                assessment.ScenarioStepCompleted,
                assessment.Probes
            });
        var evaluations = mapping.TraceReferences.AssertionIds.Select(
            assertionId => new FunctionalMldsV2AssertionEvaluation
            {
                Id = "assertion-result-" + Guid.NewGuid().ToString("N"),
                AssertionId = assertionId,
                Verdict = assessment.Verdict,
                ObservedValue = observed.DeepClone(),
                EvidenceRef = "runtime-event://" + runtimeEvent.EventId,
                Timestamp = runtimeEvent.Timestamp,
                Message = ProbeSummary(assessment)
            }).ToList();
        var validation = recorder.Record(
            CaseId,
            mapping.TraceReferences.ValidationCaseIds,
            mapping.TraceReferences.RuntimeValidationTargetIds,
            evaluations,
            runtime.Context.SessionId);
        File.AppendAllText(
            validationLogPath,
            JsonConvert.SerializeObject(validation, Formatting.None) + Environment.NewLine);
        return assessment;
    }

    private static string ProbeSummary(FunctionalMldsV2InteractionAssessment assessment)
    {
        if (assessment == null)
            return "Interaction assessment is missing.";
        return string.Join(
            "; ",
            assessment.Probes.Select(
                item => $"{item.Probe}={item.Verdict}: {item.Message}"));
    }

    private ScenarioRuntime RequireMapping(RuntimeMapping mapping, string activeAgentId)
    {
        ScenarioRuntime runtime;
        if (mapping == null || !scenarioRuntimes.TryGetValue(mapping.ScenarioId, out runtime))
            throw new FunctionalMldsV2FormatException("The selected V2 mapping has no scenario runtime.");
        runtime.Context.ActiveAgentId =
            string.IsNullOrWhiteSpace(activeAgentId) ? null : activeAgentId.Trim();
        runtime.Runner.SynchronizeExternallyObservedStep(mapping.Execution.ScenarioStepId);
        return runtime;
    }

    private RuntimeMapping Mapping(
        string actionKind,
        FunctionalMldsV2InteractionObservation observation = null,
        string activeAgentId = null)
    {
        var normalized = (actionKind ?? string.Empty).Trim().ToLowerInvariant();
        List<RuntimeMapping> candidates;
        if (!mappings.TryGetValue(normalized, out candidates) || candidates.Count == 0)
            throw new FunctionalMldsV2FormatException($"No exact V2 trace mapping for '{actionKind}'.");
        if (candidates.Count == 1)
            return candidates[0];

        var narrowed = candidates.AsEnumerable();
        var selectedTarget = TextOf(
            observation?.SelectedEntityId,
            observation?.ResponseSelectedEntityId);
        if (!string.IsNullOrWhiteSpace(selectedTarget))
            narrowed = narrowed.Where(item => item.Execution.TargetIds.Contains(selectedTarget));

        if (observation != null)
        {
            var nonDeictic = string.Equals(
                observation.InteractionMode,
                FunctionalMldsV2InteractionEvidenceEvaluator.NonDeicticMode,
                StringComparison.Ordinal);
            narrowed = FilterExact(narrowed, observation.CapabilityUseId, item => item.Execution.CapabilityUseId);
            narrowed = FilterExact(narrowed, observation.CapabilityId, item => item.Execution.CapabilityId);
            narrowed = FilterExact(narrowed, observation.RuntimeBindingId, item => item.Execution.RuntimeBindingId);
            if (string.Equals(normalized, "chat", StringComparison.Ordinal))
                narrowed = FilterExact(narrowed, observation.RuntimeActionId, item => item.Execution.RuntimeActionId);

            // Non-deictic communication uses provider-specific targetless
            // chains. Remove object-bound mappings first, then resolve the
            // exact source provider below.
            if (nonDeictic)
            {
                narrowed = narrowed.Where(item => item.Execution.TargetIds.Count == 0);
            }

            string provider;
            if (nonDeictic)
            {
                // In non-deictic mode the response's active/routed agent may
                // already be the destination of a handoff. Bind the generic
                // action to the source that initiated the request instead.
                // Exact model-binding fields above remain authoritative: when
                // they already selected a different single chain, a missing
                // provider match must not override that trusted binding.
                provider = string.Equals(normalized, "handoff", StringComparison.Ordinal)
                    ? TextOf(
                        observation.HandoffFromAgentId,
                        activeAgentId,
                        observation.RequestedAgentId,
                        observation.RoutedAgentId)
                    : TextOf(
                        activeAgentId,
                        observation.RequestedAgentId,
                        observation.RoutedAgentId);
            }
            else
            {
                // Deictic communication remains bound to the routed agent that
                // is responsible for the selected model target.
                provider = TextOf(observation.RoutedAgentId, observation.RequestedAgentId);
            }
            if (!string.IsNullOrWhiteSpace(provider))
            {
                var providerMatches = narrowed.Where(item => ProviderMatches(item.Execution.ProviderId, provider)).ToList();
                // A source-bound non-deictic action must never inherit a chain
                // selected for another provider. Deictic preflight keeps its
                // target/owner fallback because the active source may differ.
                if (nonDeictic || providerMatches.Count > 0)
                    narrowed = providerMatches;
            }

        }

        var exact = narrowed.ToList();
        if (exact.Count != 1)
        {
            var qualifier = string.IsNullOrWhiteSpace(selectedTarget)
                ? "without one trusted target/model binding"
                : $"for target '{selectedTarget}'";
            throw new FunctionalMldsV2FormatException(
                $"V2 '{normalized}' runtime mapping is {(exact.Count == 0 ? "missing" : "ambiguous")} {qualifier}.");
        }
        return exact[0];
    }

    private bool ProviderMatches(string providerId, string observedAgentId)
    {
        if (string.Equals(providerId, observedAgentId, StringComparison.Ordinal))
            return true;
        var provider = loaded.Index.Require(providerId, "Entity");
        return string.Equals(provider.OptionalString("sourceAgentId"), observedAgentId, StringComparison.Ordinal)
            || string.Equals(provider.OptionalString("sourceId"), observedAgentId, StringComparison.Ordinal);
    }

    private static IEnumerable<RuntimeMapping> FilterExact(
        IEnumerable<RuntimeMapping> candidates,
        string expected,
        Func<RuntimeMapping, string> selector)
    {
        if (string.IsNullOrWhiteSpace(expected))
            return candidates;
        var normalized = expected.Trim();
        return candidates.Where(item => string.Equals(selector(item), normalized, StringComparison.Ordinal));
    }

    private static string TextOf(params string[] values)
    {
        return (values ?? Array.Empty<string>())
            .Select(value => value?.Trim())
            .FirstOrDefault(value => !string.IsNullOrWhiteSpace(value));
    }

    private static Dictionary<string, List<RuntimeMapping>> ParseMappings(
        JToken token,
        FunctionalMldsV2ModelIndex index,
        string mainScenarioId,
        string caseId)
    {
        var array = token as JArray;
        if (array == null || array.Count == 0)
            throw new FunctionalMldsV2FormatException("V2 runtime context contains no runtime_actions.");
        var result = new Dictionary<string, List<RuntimeMapping>>(StringComparer.Ordinal);
        var actualChains = new HashSet<string>(StringComparer.Ordinal);
        foreach (var raw in array.OfType<JObject>())
        {
            var kind = RequiredText(raw, "action_kind").ToLowerInvariant();
            if (kind != "setup" && kind != "chat" && kind != "handoff" && kind != "runtime")
                throw new FunctionalMldsV2FormatException($"Unsupported application action kind '{kind}'.");
            var scenarioId = RequiredText(raw, "scenario_id");
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
            {
                List<RuntimeMapping> byKind;
                if (!result.TryGetValue(kind, out byKind))
                {
                    byKind = new List<RuntimeMapping>();
                    result.Add(kind, byKind);
                }
                byKind.Add(new RuntimeMapping(kind, scenarioId, execution, references));
            }
        }
        if (!result.ContainsKey("setup")
            || result["setup"].Count != 1
            || !string.Equals(result["setup"][0].ScenarioId, mainScenarioId, StringComparison.Ordinal))
            throw new FunctionalMldsV2FormatException(
                "V2 runtime context requires one setup mapping in main_scenario_id.");
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
        public string ScenarioId { get; }
        public FunctionalMldsV2ExecutionReference Execution { get; }
        public FunctionalMldsV2TraceReferences TraceReferences { get; }

        public RuntimeMapping(
            string actionKind,
            string scenarioId,
            FunctionalMldsV2ExecutionReference execution,
            FunctionalMldsV2TraceReferences traceReferences)
        {
            ActionKind = actionKind;
            ScenarioId = scenarioId;
            Execution = execution;
            TraceReferences = traceReferences;
        }
    }

    private sealed class ScenarioRuntime
    {
        public FunctionalMldsV2RuntimeContext Context { get; }
        public FunctionalMldsV2RuntimeLogger Logger { get; }
        public FunctionalMldsV2ScenarioRunner Runner { get; }

        public ScenarioRuntime(
            FunctionalMldsV2RuntimeContext context,
            FunctionalMldsV2RuntimeLogger logger,
            FunctionalMldsV2ScenarioRunner runner)
        {
            Context = context;
            Logger = logger;
            Runner = runner;
        }
    }
}
