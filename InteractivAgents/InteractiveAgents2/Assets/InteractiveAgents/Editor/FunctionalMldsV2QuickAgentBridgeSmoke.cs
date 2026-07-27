#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using FunctionalMlds.V2;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;

public static class FunctionalMldsV2QuickAgentBridgeSmoke
{
    [MenuItem("Tools/Interactive Agents/FunctionalMLDS V2/Run QuickAgent Bridge Smoke", false, 221)]
    public static void RunMenu()
    {
        Run();
        Debug.Log("[FunctionalMldsV2QuickAgentBridgeSmoke] OK");
    }

    public static void RunFromCommandLine()
    {
        try
        {
            Run();
            Debug.Log("[FunctionalMldsV2QuickAgentBridgeSmoke] OK");
            EditorApplication.Exit(0);
        }
        catch (Exception exception)
        {
            Debug.LogException(exception);
            EditorApplication.Exit(1);
        }
    }

    private static void Run()
    {
        var fixturePath = Path.Combine(
            Application.dataPath,
            "InteractiveAgents",
            "Editor",
            "FunctionalMldsV2SmokeInstance.json");
        var modelJson = File.ReadAllText(fixturePath);
        var loaded = FunctionalMldsV2Loader.LoadJson(modelJson, fixturePath, validate: true);
        var setup = BuildSetup(loaded);
        var root = Path.Combine(Application.temporaryCachePath, "functionalmlds-v2-qam-bridge-smoke");
        if (Directory.Exists(root))
            Directory.Delete(root, true);

        var endpoint = FunctionalMldsV2QuickAgentBridge.ModelEndpointFor(setup.ToString(Formatting.None));
        Require(endpoint == "/projects/unity_v2_native_smoke/functionalmlds-v2", "Model endpoint mismatch.");
        var bridge = FunctionalMldsV2QuickAgentBridge.Create(
            setup.ToString(Formatting.None),
            modelJson,
            root);
        foreach (var kind in new[] { "setup", "chat", "handoff" })
        {
            bridge.RequireAction(kind, "runtime-agent");
            bridge.Record(
                kind,
                "unity_" + kind + "_smoke",
                "runtime-agent",
                "success",
                new { kind },
                new { ok = true });
        }

        var events = File.ReadAllLines(Path.Combine(root, "events.v2.jsonl"));
        var validations = File.ReadAllLines(Path.Combine(root, "runtime_validation.v2.jsonl"));
        Require(events.Length == 3, "Bridge must write three runtime events.");
        Require(validations.Length == 3, "Bridge must write three validation records.");
        foreach (var line in events)
        {
            var payload = JObject.Parse(line);
            Require((string)payload["schema"] == "functionalmlds_runtime_event", "Runtime schema mismatch.");
            Require((string)payload["model_sha256"] == loaded.Sha256, "Runtime hash mismatch.");
            Require((payload["assertion_ids"] as JArray)?.Count == 5, "Runtime assertion trace is incomplete.");
        }
        foreach (var line in validations)
        {
            var payload = JObject.Parse(line);
            Require(
                (string)payload["schema"] == "dynamic_functional_mlds_v2_runtime_validation",
                "Validation schema mismatch.");
            Require(
                (string)payload["runtimeActualOutcome"]?["result"]?[0]?["verdict"] == "inconclusive",
                "Transport success must remain semantically inconclusive without a domain probe.");
        }

        var badSetup = (JObject)setup.DeepClone();
        badSetup["model_sha256"] = new string('0', 64);
        ExpectFailure(
            () => FunctionalMldsV2QuickAgentBridge.Create(
                badSetup.ToString(Formatting.None),
                modelJson,
                root),
            "Hash mutation must fail closed.");

        ExpectTraceFailure(
            setup,
            modelJson,
            root,
            action => action["target_ids"] = new JArray("provider-agent"),
            "Target mutation must fail closed.");
        ExpectTraceFailure(
            setup,
            modelJson,
            root,
            action => action["assertion_ids"] = new JArray("assert-state"),
            "Assertion mutation must fail closed.");
        ExpectTraceFailure(
            setup,
            modelJson,
            root,
            action => action["validation_case_ids"] = new JArray(),
            "ValidationCase mutation must fail closed.");
        ExpectTraceFailure(
            setup,
            modelJson,
            root,
            action => action["runtime_validation_target_ids"] = new JArray(),
            "RuntimeValidationTarget mutation must fail closed.");
        ExpectTraceFailure(
            setup,
            modelJson,
            root,
            action => action["locator"]["value"] = "POST /wrong",
            "Locator mutation must fail closed.");
        ExpectTraceFailure(
            setup,
            modelJson,
            root,
            action => action["action_kind"] = "handoff",
            "Action-kind mutation must fail closed.");

        var incompleteSetup = (JObject)setup.DeepClone();
        var incompleteActions = (JArray)incompleteSetup["functionalmlds"]?["runtime_actions"];
        incompleteActions?.RemoveAt(incompleteActions.Count - 1);
        ExpectFailure(
            () => FunctionalMldsV2QuickAgentBridge.Create(
                incompleteSetup.ToString(Formatting.None),
                modelJson,
                root),
            "Missing runtime chain must fail closed.");
    }

    private static JObject BuildSetup(FunctionalMldsV2LoadResult loaded)
    {
        var actionIds = new[] { "action-endpoint", "action-tool", "action-topic" };
        var kinds = new[] { "setup", "chat", "handoff" };
        var assertionIds = new[]
        {
            "assert-state",
            "assert-event",
            "assert-output",
            "assert-grounding",
            "assert-relation"
        };
        var actions = new JArray();
        for (var index = 0; index < actionIds.Length; index++)
        {
            var action = loaded.Index.Require(actionIds[index], "RuntimeAction");
            var locator = loaded.Index.Require(action.References("locator").Single(), "RuntimeActionLocator");
            actions.Add(
                new JObject
                {
                    ["action_kind"] = kinds[index],
                    ["scenario_step_id"] = "step-dispatch",
                    ["capability_use_id"] = "capability-use-chat",
                    ["capability_id"] = "capability-chat",
                    ["provider_entity_id"] = "provider-agent",
                    ["target_ids"] = new JArray("target-asset"),
                    ["runtime_binding_id"] = "binding-chat",
                    ["runtime_action_id"] = action.Id,
                    ["locator"] = new JObject
                    {
                        ["kind"] = locator.RequiredString("kind"),
                        ["value"] = locator.RequiredString("value")
                    },
                    ["assertion_ids"] = new JArray(assertionIds),
                    ["validation_case_ids"] = new JArray("validation-case"),
                    ["runtime_validation_target_ids"] = new JArray("validation-target")
                });
        }

        return new JObject
        {
            ["session_id"] = "unity-bridge-smoke-session",
            ["metamodel_version"] = "2.0.0-model",
            ["model_sha256"] = loaded.Sha256,
            ["functionalmlds_model_endpoint"] = "/projects/unity_v2_native_smoke/functionalmlds-v2",
            ["functionalmlds"] = new JObject
            {
                ["schema"] = "functionalmlds_runtime_context_v2",
                ["case_id"] = "unity_v2_native_smoke",
                ["model_version"] = "2.0.0-model",
                ["model_sha256"] = loaded.Sha256,
                ["profile"] = "executable",
                ["main_scenario_id"] = "main",
                ["runtime_actions"] = actions
            }
        };
    }

    private static void ExpectFailure(Action action, string message)
    {
        try
        {
            action();
        }
        catch
        {
            return;
        }
        throw new Exception(message);
    }

    private static void ExpectTraceFailure(
        JObject setup,
        string modelJson,
        string root,
        Action<JObject> mutate,
        string message)
    {
        var changed = (JObject)setup.DeepClone();
        var actions = changed["functionalmlds"]?["runtime_actions"] as JArray;
        var setupAction = actions?
            .OfType<JObject>()
            .Single(item => (string)item["action_kind"] == "setup");
        if (setupAction == null)
            throw new Exception("Smoke fixture has no setup mapping.");
        mutate(setupAction);
        ExpectFailure(
            () => FunctionalMldsV2QuickAgentBridge.Create(
                changed.ToString(Formatting.None),
                modelJson,
                root),
            message);
    }

    private static void Require(bool condition, string message)
    {
        if (!condition)
            throw new Exception(message);
    }
}
#endif
