using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FunctionalMlds.V2;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;

public static class FunctionalMldsV2NativeSmoke
{
    private const string EnvironmentPath = "FUNCTIONALMLDS_V2_INSTANCE";
    private const string OutputEnvironmentPath = "FUNCTIONALMLDS_V2_SMOKE_OUTPUT_DIR";

    [MenuItem("Tools/Interactive Agents/FunctionalMLDS V2/Validate Configured V2 Instance", false, 219)]
    public static void ValidateConfiguredInstance()
    {
        var path = ResolvePath();
        var loaded = FunctionalMldsV2Loader.LoadFile(path);
        Require(loaded.Validation.IsValid, loaded.Validation.ToDisplayString());
        Debug.Log(
            "[FunctionalMLDSV2Validation] OK"
            + "; source=" + path
            + "; model_version=" + loaded.Document.MetamodelVersion
            + "; sha256=" + loaded.Sha256
            + "; objects=" + loaded.Document.Objects.Count);
    }

    [MenuItem("Tools/Interactive Agents/FunctionalMLDS V2/Run Native V2 Smoke", false, 220)]
    public static void Run()
    {
        var path = ResolvePath();
        var outputDirectory = ResolveOutputDirectory();
        var loaded = FunctionalMldsV2Loader.LoadFile(path);
        Require(loaded.Validation.IsValid, loaded.Validation.ToDisplayString());
        Require(loaded.Index.OfType("DynamicFunctionalModel").Count() == 1, "Expected one DynamicFunctionalModel.");
        Require(FunctionalMldsV2InvariantValidator.AssertionTypes.All(
            type => loaded.Index.Objects.Any(item => item.Type == type)), "Not all five Assertion specializations are present.");

        var context = FunctionalMldsV2RuntimeContext.Create(loaded, "main", "unity-v2-smoke-session");
        var runner = new FunctionalMldsV2ScenarioRunner(loaded.Index, context, random: () => 0.1);
        RequireSequence(runner.Start(), "step-start");
        RequireSet(runner.CompleteAndAdvance("step-start").ActivatedStepIds, "step-left", "step-right");
        Require(runner.CompleteAndAdvance("step-left").ActivatedStepIds.Count == 0, "Join activated before all fork branches completed.");
        RequireSequence(runner.CompleteAndAdvance("step-right").ActivatedStepIds, "step-joined");
        RequireSequence(runner.CompleteAndAdvance("step-joined").ActivatedStepIds, "step-dispatch");

        var executor = new RecordingExecutor();
        var dispatcher = new FunctionalMldsV2CapabilityDispatcher(loaded.Index, context, executor);
        var dispatch = dispatcher.Dispatch(new FunctionalMldsV2DispatchRequest
        {
            CapabilityUseId = "capability-use-chat",
            Parameters = new JObject { ["message"] = "hello" }
        });
        Require(dispatch.Success, "Capability dispatch failed.");
        RequireSequence(executor.ActionIds, "action-endpoint", "action-tool", "action-topic");
        RequireSequence(executor.LocatorKinds, "endpoint", "tool", "topic");
        Require(dispatch.Execution.ProviderId == "provider-agent", "Dispatcher lost CapabilityUse.provider.");
        RequireSequence(dispatch.Execution.TargetIds, "target-asset");

        RequireSequence(runner.CompleteAndAdvance("step-dispatch").ActivatedStepIds, "step-success");
        Require(runner.CompleteAndAdvance("step-success").IsTerminal, "Success step must be terminal.");
        ExerciseExceptionAndLoop(loaded);

        var probe = new FunctionalMldsV2DictionaryAssertionProbe();
        probe.Set("step-dispatch", new JValue("ready"), "smoke://state");
        probe.Set("runtime-event", new JValue("different-event"), "smoke://event");
        probe.Set("target-asset", new JValue(5), "smoke://grounding");
        probe.Set("capability-use-chat", new JValue("relation"), "smoke://relation");
        var evaluator = new FunctionalMldsV2AssertionEvaluator(loaded.Index, probe);
        var evaluations = new[]
        {
            evaluator.Evaluate("assert-state"),
            evaluator.Evaluate("assert-event"),
            evaluator.Evaluate("assert-output"),
            evaluator.Evaluate("assert-grounding"),
            evaluator.Evaluate("assert-relation")
        };
        Require(evaluations.Count(item => item.VerdictValue == FunctionalMldsV2AssertionVerdict.Pass) == 2, "Expected two passing assertions.");
        Require(evaluations.Count(item => item.VerdictValue == FunctionalMldsV2AssertionVerdict.Fail) == 1, "Expected one failing assertion.");
        Require(evaluations.Count(item => item.VerdictValue == FunctionalMldsV2AssertionVerdict.Inconclusive) == 1, "Expected one inconclusive assertion.");
        Require(evaluations.Count(item => item.VerdictValue == FunctionalMldsV2AssertionVerdict.Error) == 1, "Expected one assertion error.");

        var artifact = new FunctionalMldsV2ValidationRecorder(loaded).Record(
            "unity_v2_native_smoke",
            new[] { "validation-case" },
            new[] { "validation-target" },
            evaluations,
            context.SessionId);
        Require(artifact.RuntimeValidationLog != null, "Validation artifact has no RuntimeValidationLog.");
        Require(artifact.RuntimeActualOutcome != null, "Validation artifact has no RuntimeActualOutcome.");
        Require(artifact.RuntimeActualOutcome.Result.Count == 5, "Validation artifact did not record all results.");
        ValidateValidationEnvelope(artifact);
        if (outputDirectory != null)
        {
            File.WriteAllText(
                Path.Combine(outputDirectory, "runtime_validation.v2.json"),
                JsonConvert.SerializeObject(artifact, Formatting.Indented));
        }

        ExerciseLogger(loaded, context, dispatch.Execution, outputDirectory);
        ExerciseFailClosedMutation(loaded.Document);

        Debug.Log(
            "[FunctionalMLDSV2NativeSmoke] OK"
            + "; source=" + path
            + "; sha256=" + loaded.Sha256
            + "; objects=" + loaded.Document.Objects.Count
            + "; actions=" + dispatch.ActionResults.Count
            + "; assertion_results=" + evaluations.Length);
    }

    private static void ExerciseExceptionAndLoop(FunctionalMldsV2LoadResult loaded)
    {
        var context = FunctionalMldsV2RuntimeContext.Create(loaded, "main", "unity-v2-exception-smoke");
        var runner = new FunctionalMldsV2ScenarioRunner(loaded.Index, context, random: () => 0.1);
        runner.Start();
        runner.CompleteAndAdvance("step-start");
        runner.CompleteAndAdvance("step-left");
        runner.CompleteAndAdvance("step-right");
        runner.CompleteAndAdvance("step-joined");
        RequireSequence(
            runner.CompleteAndAdvance("step-dispatch", new FunctionalMldsV2AdvanceRequest { ExceptionRaised = true }).ActivatedStepIds,
            "step-exception");
        RequireSequence(
            runner.CompleteAndAdvance("step-exception", new FunctionalMldsV2AdvanceRequest { AllowLoop = true }).ActivatedStepIds,
            "step-dispatch");
    }

    private static void ExerciseLogger(
        FunctionalMldsV2LoadResult loaded,
        FunctionalMldsV2RuntimeContext context,
        FunctionalMldsV2ExecutionReference execution,
        string outputDirectory)
    {
        var persistent = !string.IsNullOrWhiteSpace(outputDirectory);
        var path = persistent
            ? Path.Combine(outputDirectory, "runtime_event.v2.jsonl")
            : Path.Combine(Path.GetTempPath(), "functionalmlds-v2-smoke-" + Guid.NewGuid().ToString("N") + ".jsonl");
        try
        {
            var logger = new FunctionalMldsV2RuntimeLogger(path, loaded.Index, context);
            var traceReferences = new FunctionalMldsV2TraceReferences
            {
                CaseId = "unity_v2_native_smoke",
                AssertionIds = new List<string>
                {
                    "assert-state", "assert-event", "assert-output", "assert-grounding", "assert-relation"
                },
                ValidationCaseIds = new List<string> { "validation-case" },
                RuntimeValidationTargetIds = new List<string> { "validation-target" }
            };
            logger.Append(
                "capability_dispatch_completed",
                execution,
                traceReferences,
                "success",
                new { parameter_count = 1 },
                new { action_count = 3 },
                durationMs: 1.25,
                metadata: new JObject { ["smoke"] = true });
            var line = File.ReadAllLines(path).Single();
            var evt = JObject.Parse(line);
            ValidateRuntimeEventEnvelope(evt, loaded.Sha256);
        }
        finally
        {
            if (!persistent && File.Exists(path))
                File.Delete(path);
        }
    }

    private static void ExerciseFailClosedMutation(FunctionalMldsV2Document source)
    {
        var root = JObject.Parse(JsonConvert.SerializeObject(source));
        var use = ((JArray)root["objects"])
            .OfType<JObject>()
            .Single(item => item.Value<string>("id") == "capability-use-chat");
        use["provider"] = new JArray();
        try
        {
            FunctionalMldsV2Loader.LoadJson(root.ToString(Formatting.None), "<invalid-smoke-mutation>");
            throw new Exception("Fail-closed validation accepted CapabilityUse without provider.");
        }
        catch (FunctionalMldsV2ValidationException)
        {
            // Expected.
        }

        ExpectFormatFailure(source, "schema", "not-the-v2-instance-schema");
        ExpectFormatFailure(source, "metamodelVersion", "2.0.0-runtime");
        ExpectFormatFailure(source, "profile", "review-only");
        ExpectFormatFailure(source, "unexpectedRootMember", true);
    }

    private static void ExpectFormatFailure(FunctionalMldsV2Document source, string property, JToken value)
    {
        var root = JObject.Parse(JsonConvert.SerializeObject(source));
        root[property] = value;
        try
        {
            FunctionalMldsV2Loader.LoadJson(root.ToString(Formatting.None), "<invalid-root-smoke-mutation>");
            throw new Exception("Fail-closed loader accepted invalid root property " + property + ".");
        }
        catch (FunctionalMldsV2FormatException)
        {
            // Expected.
        }
    }

    private static void ValidateRuntimeEventEnvelope(JObject evt, string expectedSha256)
    {
        RequireSet(
            evt.Properties().Select(property => property.Name),
            "schema", "schema_version", "event_id", "timestamp", "case_id", "session_id",
            "event_type", "agent_id", "model_version", "model_sha256", "scenario_step_id",
            "capability_use_id", "capability_id", "provider_entity_id", "target_ids",
            "runtime_binding_id", "runtime_action_id", "assertion_ids", "validation_case_ids",
            "runtime_validation_target_ids", "input_summary", "output_summary", "duration_ms",
            "status", "error_summary", "metadata");
        Require(evt.Value<string>("schema") == "functionalmlds_runtime_event", "Logger emitted wrong schema.");
        Require(evt.Value<string>("schema_version") == "2.0", "Logger emitted wrong schema_version.");
        Require(evt.Value<string>("model_version") == "2.0.0-model", "Logger emitted wrong model_version.");
        Require(evt.Value<string>("model_sha256") == expectedSha256, "Logger lost model identity.");
        Require(evt.Value<string>("case_id") == "unity_v2_native_smoke", "Logger lost exact case_id.");
        Require(evt.Value<string>("scenario_step_id") == "step-dispatch", "Logger lost exact ScenarioStep id.");
        Require(evt.Value<string>("capability_use_id") == "capability-use-chat", "Logger lost exact CapabilityUse id.");
        Require(evt.Value<string>("capability_id") == "capability-chat", "Logger lost exact Capability id.");
        Require(evt.Value<string>("provider_entity_id") == "provider-agent", "Logger lost exact provider id.");
        RequireSequence(evt["target_ids"].Values<string>(), "target-asset");
        Require(evt.Value<string>("runtime_binding_id") == "binding-chat", "Logger lost exact RuntimeBinding id.");
        Require(evt.Value<string>("runtime_action_id") == "action-topic", "Logger lost exact RuntimeAction id.");
        Require(evt["assertion_ids"].Count() == 5, "Logger lost Assertion ids.");
        RequireSequence(evt["validation_case_ids"].Values<string>(), "validation-case");
        RequireSequence(evt["runtime_validation_target_ids"].Values<string>(), "validation-target");
        Require(evt.Value<string>("status") == "success", "Logger emitted an unsupported status.");
    }

    private static void ValidateValidationEnvelope(FunctionalMldsV2ValidationArtifact artifact)
    {
        var root = JObject.Parse(JsonConvert.SerializeObject(artifact, Formatting.None));
        RequireSet(
            root.Properties().Select(property => property.Name),
            "schema", "schema_version", "model_version", "model_sha256", "case_id", "session_id",
            "validation_case_ids", "runtime_validation_target_ids", "runtimeValidationLog",
            "runtimeActualOutcome");
        Require(root.Value<string>("schema") == "dynamic_functional_mlds_v2_runtime_validation", "Recorder emitted wrong schema.");
        Require(root.Value<string>("schema_version") == "2.0", "Recorder emitted wrong schema_version.");
        Require(root.Value<string>("model_version") == "2.0.0-model", "Recorder emitted wrong model_version.");
        RequireSequence(root["validation_case_ids"].Values<string>(), "validation-case");
        RequireSequence(root["runtime_validation_target_ids"].Values<string>(), "validation-target");

        var log = (JObject)root["runtimeValidationLog"];
        var actual = (JObject)root["runtimeActualOutcome"];
        RequireSet(log.Properties().Select(property => property.Name), "id", "type", "actualOutcome");
        RequireSet(actual.Properties().Select(property => property.Name), "id", "type", "result");
        RequireSequence(log["actualOutcome"].Values<string>(), actual.Value<string>("id"));
        foreach (var result in actual["result"].OfType<JObject>())
        {
            RequireSet(
                result.Properties().Select(property => property.Name),
                "id", "type", "assertion", "verdict", "observedValue", "evidenceRef", "timestamp");
            var observed = (JObject)result["observedValue"];
            if (observed.Value<string>("type") == "EANumericalValue")
                RequireSet(observed.Properties().Select(property => property.Name), "type", "value");
            else
            {
                Require(observed.Value<string>("type") == "EAExpression", "Recorder emitted a non-EAST-ADL observed value type.");
                RequireSet(observed.Properties().Select(property => property.Name), "type", "mixedStringContent");
            }
            Require(!string.IsNullOrWhiteSpace(result.Value<string>("evidenceRef")), "Recorder emitted an empty evidenceRef.");
        }
    }

    private static string ResolvePath()
    {
        var configured = Environment.GetEnvironmentVariable(EnvironmentPath);
        var path = string.IsNullOrWhiteSpace(configured)
            ? Path.Combine(Application.dataPath, "InteractiveAgents", "Editor", "FunctionalMldsV2SmokeInstance.json")
            : configured.Trim();
        return Path.GetFullPath(path);
    }

    private static string ResolveOutputDirectory()
    {
        var configured = Environment.GetEnvironmentVariable(OutputEnvironmentPath);
        if (string.IsNullOrWhiteSpace(configured))
            return null;
        var path = Path.GetFullPath(configured.Trim());
        Directory.CreateDirectory(path);
        return path;
    }

    private static void Require(bool condition, string message)
    {
        if (!condition)
            throw new Exception(message);
    }

    private static void RequireSequence(IEnumerable<string> actual, params string[] expected)
    {
        var values = (actual ?? Enumerable.Empty<string>()).ToArray();
        if (!values.SequenceEqual(expected))
            throw new Exception("Sequence mismatch. Expected [" + string.Join(",", expected) + "], got [" + string.Join(",", values) + "].");
    }

    private static void RequireSet(IEnumerable<string> actual, params string[] expected)
    {
        var values = new HashSet<string>(actual ?? Enumerable.Empty<string>(), StringComparer.Ordinal);
        if (!values.SetEquals(expected))
            throw new Exception("Set mismatch. Expected [" + string.Join(",", expected) + "], got [" + string.Join(",", values) + "].");
    }

    private sealed class RecordingExecutor : IFunctionalMldsV2RuntimeActionExecutor
    {
        public List<string> ActionIds { get; } = new List<string>();
        public List<string> LocatorKinds { get; } = new List<string>();

        public FunctionalMldsV2RuntimeActionResult Execute(
            FunctionalMldsV2Object action,
            FunctionalMldsV2Object locator,
            FunctionalMldsV2ExecutionReference execution,
            JObject parameters,
            FunctionalMldsV2RuntimeContext runtimeContext)
        {
            ActionIds.Add(action.Id);
            LocatorKinds.Add(locator.RequiredString("kind"));
            return new FunctionalMldsV2RuntimeActionResult
            {
                Success = true,
                OutputSummary = locator.RequiredString("value"),
                EvidenceRef = "smoke://" + action.Id,
                ObservedValue = new JValue(action.Id)
            };
        }
    }
}
