#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using System.Reflection;
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

        var partialTarget = ValidObservation(loaded.Sha256);
        partialTarget.ResponseObserved = false;
        partialTarget.RoutedAgentId = null;
        partialTarget.ResponseSelectedEntityId = null;
        partialTarget.ResponseGroundedEntityIds.Clear();
        var partialAssessment = bridge.RecordInteraction(
            "chat",
            "unity_target_selection_resolved",
            "runtime-agent",
            partialTarget,
            new { target = "target-asset" },
            new { state = "resolved" });
        Require(
            partialAssessment.Verdict == "inconclusive" && !partialAssessment.CompletionSatisfied,
            "Target-only evidence must remain inconclusive until routing and response are observed.");

        var validAssessment = bridge.RecordInteraction(
            "chat",
            "unity_grounded_chat_observed",
            "runtime-agent",
            ValidObservation(loaded.Sha256),
            new { interaction_mode = "deictic", target = "target-asset" },
            new { routed_agent_id = "runtime-agent", grounded_entity_id = "target-asset" });
        Require(validAssessment.Verdict == "pass", "A valid grounded trace must pass.");
        Require(validAssessment.TargetResolved, "A valid grounded trace must resolve its target.");
        Require(validAssessment.RouteResolved, "A valid grounded trace must resolve its route.");
        Require(validAssessment.CompletionSatisfied, "A valid grounded trace must satisfy completion.");
        Require(validAssessment.ScenarioStepCompleted, "Scenario completion must be evidence-gated.");
        Require(
            validAssessment.Probe("model_binding").Passed
            && validAssessment.Probe("target_resolution").Passed
            && validAssessment.Probe("entity_capability_agreement").Passed
            && validAssessment.Probe("agent_responsibility").Passed
            && validAssessment.Probe("response_entity").Passed,
            "The valid trace must pass all required grounding/routing probes.");

        var handoffObservation = ValidObservation(loaded.Sha256);
        handoffObservation.RoutedAgentId = "specialist-agent";
        handoffObservation.HandoffObserved = true;
        handoffObservation.HandoffFromAgentId = "runtime-agent";
        handoffObservation.HandoffToAgentId = "specialist-agent";
        handoffObservation.ModeledHandoff = true;
        var handoffAssessment = bridge.RecordInteraction(
            "handoff",
            "unity_handoff_observed",
            "runtime-agent",
            handoffObservation,
            new { from = "runtime-agent" },
            new { to = "specialist-agent", modeled_handoff = true });
        Require(handoffAssessment.Verdict == "pass", "A modeled handoff trace must pass.");
        Require(
            handoffAssessment.Probe("handoff_permission").Passed,
            "A modeled handoff must pass the handoff-permission probe.");

        var brokenObservation = ValidObservation(loaded.Sha256);
        brokenObservation.ResponseSelectedEntityId = "provider-agent";
        var brokenAssessment = bridge.RecordInteraction(
            "chat",
            "unity_grounded_chat_observed",
            "runtime-agent",
            brokenObservation,
            new { target = "target-asset" },
            new { selected_entity_id = "provider-agent" });
        Require(brokenAssessment.Verdict == "fail", "An injected entity mismatch must fail.");
        Require(!brokenAssessment.CompletionSatisfied, "A broken trace must fail closed.");
        Require(!brokenAssessment.ScenarioStepCompleted, "A broken trace must not complete its scenario step.");

        var nonDeicticWithGrounding = ValidObservation(loaded.Sha256);
        nonDeicticWithGrounding.InteractionMode =
            FunctionalMldsV2InteractionEvidenceEvaluator.NonDeicticMode;
        nonDeicticWithGrounding.SelectionObserved = false;
        nonDeicticWithGrounding.SelectionState = "none";
        nonDeicticWithGrounding.SelectedEntityId = null;
        nonDeicticWithGrounding.SelectedSourceObjectId = null;
        var nonDeicticAssessment = bridge.RecordInteraction(
            "chat",
            "unity_non_deictic_with_grounding_smoke",
            "runtime-agent",
            nonDeicticWithGrounding,
            new { interaction_mode = "non_deictic" },
            new { grounded_entity_id = "target-asset" });
        Require(
            nonDeicticAssessment.Verdict == "fail",
            "A non_deictic response must not receive success from grounding evidence.");

        ExpectFailure(
            () => QuickAgentManager.SerializeChatRequest(new QuickAgentManager.ChatRequest
            {
                session_id = "session",
                active_agent_id = "runtime-agent",
                user_text = "Describe this.",
                interaction_mode = FunctionalMldsV2InteractionEvidenceEvaluator.DeicticMode,
                spatial_context = null
            }),
            "A deictic request without spatial_context must not be serialized.");
        ExpectFailure(
            () => QuickAgentManager.ResolveV2InteractionMode(
                true,
                FunctionalMldsSpatialTargetStates.Ambiguous,
                null),
            "An ambiguous selection must not fall back to non_deictic mode.");
        Require(
            QuickAgentManager.ResolveV2InteractionMode(
                true,
                FunctionalMldsSpatialTargetStates.None,
                null) == FunctionalMldsV2InteractionEvidenceEvaluator.NonDeicticMode,
            "A generic V2 chat without a selection must use explicit non_deictic mode.");

        var events = File.ReadAllLines(Path.Combine(root, "events.v2.jsonl"));
        var validations = File.ReadAllLines(Path.Combine(root, "runtime_validation.v2.jsonl"));
        Require(events.Length == 8, "Bridge must write all transport and interaction events.");
        Require(validations.Length == 8, "Bridge must write one validation record per runtime event.");
        foreach (var line in events)
        {
            var payload = JObject.Parse(line);
            Require((string)payload["schema"] == "functionalmlds_runtime_event", "Runtime schema mismatch.");
            Require((string)payload["model_sha256"] == loaded.Sha256, "Runtime hash mismatch.");
            Require((payload["assertion_ids"] as JArray)?.Count == 5, "Runtime assertion trace is incomplete.");
        }
        foreach (var line in validations.Take(3))
        {
            var payload = JObject.Parse(line);
            Require(
                (string)payload["schema"] == "dynamic_functional_mlds_v2_runtime_validation",
                "Validation schema mismatch.");
            Require(
                (string)payload["runtimeActualOutcome"]?["result"]?[0]?["verdict"] == "inconclusive",
                "Transport success must remain semantically inconclusive without a domain probe.");
        }
        var eventPayloads = events.Select(JObject.Parse).ToList();
        var validationPayloads = validations.Select(JObject.Parse).ToList();
        Require(
            (string)eventPayloads[4]["status"] == "success"
            && (string)validationPayloads[4]["runtimeActualOutcome"]?["result"]?[0]?["verdict"] == "pass",
            "Real valid interaction evidence must produce pass, not transport-only success.");
        Require(
            (string)eventPayloads[6]["status"] == "failed"
            && (string)validationPayloads[6]["runtimeActualOutcome"]?["result"]?[0]?["verdict"] == "fail",
            "The injected broken trace must be persisted as failed evidence.");

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

        RunRealMultiScenarioCorpus();
        RunKaesesteinpilzCommunicationCorpus();
    }

    private static void RunRealMultiScenarioCorpus()
    {
        var projectDirectory = Path.GetFullPath(
            Path.Combine(
                Application.dataPath,
                "..",
                "..",
                "openai_unity_expert_npcs_pycharm",
                "InteractiveAgents",
                "projects",
                "steinpilz_brand_room"));
        var modelPath = Path.Combine(projectDirectory, "functionalmlds.v2.instance.json");
        var tracePath = Path.Combine(projectDirectory, "trace_map.v2.json");
        Require(
            File.Exists(modelPath) && File.Exists(tracePath),
            "The committed multi-scenario Steinpilz corpus is missing.");

        var modelJson = File.ReadAllText(modelPath);
        var trace = JObject.Parse(File.ReadAllText(tracePath));
        var loaded = FunctionalMldsV2Loader.LoadJson(modelJson, modelPath, validate: true);
        Require(
            string.Equals(
                loaded.Sha256,
                (string)trace["model_sha256"],
                StringComparison.Ordinal),
            "The real multi-scenario model and trace hashes differ.");

        var setup = new JObject
        {
            ["session_id"] = "unity-real-multi-scenario-smoke",
            ["metamodel_version"] = "2.0.0-model",
            ["model_sha256"] = loaded.Sha256,
            ["functionalmlds_model_endpoint"] =
                "/projects/steinpilz_brand_room/functionalmlds-v2",
            ["functionalmlds"] = new JObject
            {
                ["schema"] = "functionalmlds_runtime_context_v2",
                ["case_id"] = (string)trace["case_id"],
                ["model_version"] = "2.0.0-model",
                ["model_sha256"] = loaded.Sha256,
                ["profile"] = "executable",
                ["main_scenario_id"] = (string)trace["main_scenario_id"],
                ["runtime_actions"] = trace["runtime_actions"].DeepClone()
            }
        };
        var root = Path.Combine(
            Application.temporaryCachePath,
            "functionalmlds-v2-real-multi-scenario-smoke");
        if (Directory.Exists(root))
            Directory.Delete(root, true);
        var bridge = FunctionalMldsV2QuickAgentBridge.Create(
            setup.ToString(Formatting.None),
            modelJson,
            root);

        var actions = ((JArray)trace["runtime_actions"])
            .OfType<JObject>()
            .Where(item => (string)item["action_kind"] == "chat")
            .GroupBy(item => (string)item["scenario_id"], StringComparer.Ordinal)
            .Select(group => group.First())
            .Take(2)
            .ToList();
        Require(actions.Count == 2, "The real corpus must expose at least two chat scenarios.");
        foreach (var action in actions)
        {
            var targetId = ((JArray)action["target_ids"]).Values<string>().First();
            var target = loaded.Index.Require(targetId, "Entity");
            var provider = loaded.Index.Require((string)action["provider_entity_id"], "Entity");
            var providerSourceId = provider.OptionalString("sourceAgentId")
                ?? provider.OptionalString("sourceId");
            var observation = new FunctionalMldsV2InteractionObservation
            {
                InteractionMode = FunctionalMldsV2InteractionEvidenceEvaluator.DeicticMode,
                ModelSha256 = loaded.Sha256,
                BindingRegistryValid = true,
                SelectionObserved = true,
                SelectionState = FunctionalMldsV2InteractionEvidenceEvaluator.ResolvedSelectionState,
                SelectedEntityId = target.Id,
                SelectedSourceObjectId = target.RequiredString("sourceId"),
                RequestedAgentId = providerSourceId,
                ResponseObserved = false,
                CapabilityUseId = (string)action["capability_use_id"],
                CapabilityId = (string)action["capability_id"],
                RuntimeBindingId = (string)action["runtime_binding_id"],
                RuntimeActionId = (string)action["runtime_action_id"]
            };
            bridge.RequireAction("chat", providerSourceId, observation);
            var assessment = bridge.RecordInteraction(
                "chat",
                "unity_multi_scenario_target_resolved",
                providerSourceId,
                observation,
                new { target_id = target.Id },
                new { state = "resolved" });
            Require(
                assessment.Verdict == "inconclusive" && !assessment.CompletionSatisfied,
                "A target-only multi-scenario observation must remain inconclusive.");
        }

        var events = File.ReadAllLines(Path.Combine(root, "events.v2.jsonl"))
            .Select(JObject.Parse)
            .ToList();
        Require(events.Count == 2, "The multi-scenario smoke must persist both target observations.");
        Require(
            events.Select(item => (string)item["scenario_step_id"])
                .Distinct(StringComparer.Ordinal)
                .Count() == 2,
            "The bridge collapsed two selected scenarios onto one runtime step.");
    }

    private static void RunKaesesteinpilzCommunicationCorpus()
    {
        const string projectId =
            "kaesestand_steinpilz_haptisch_chill_milcherlebnisraum_welcome_gruen_029e9a89";
        var projectDirectory = Path.GetFullPath(
            Path.Combine(
                Application.dataPath,
                "..",
                "..",
                "openai_unity_expert_npcs_pycharm",
                "InteractiveAgents",
                "projects",
                projectId));
        var modelPath = Path.Combine(projectDirectory, "functionalmlds.v2.instance.json");
        var tracePath = Path.Combine(projectDirectory, "trace_map.v2.json");
        Require(
            File.Exists(modelPath) && File.Exists(tracePath),
            "The KAESESTEINPILZ communication corpus is missing.");

        var modelJson = File.ReadAllText(modelPath);
        var trace = JObject.Parse(File.ReadAllText(tracePath));
        var loaded = FunctionalMldsV2Loader.LoadJson(modelJson, modelPath, validate: true);
        Require(
            string.Equals(
                loaded.Sha256,
                (string)trace["model_sha256"],
                StringComparison.Ordinal),
            "The KAESESTEINPILZ model and trace hashes differ.");

        var setup = new JObject
        {
            ["session_id"] = "unity-kaesesteinpilz-communication-smoke",
            ["metamodel_version"] = "2.0.0-model",
            ["model_sha256"] = loaded.Sha256,
            ["functionalmlds_model_endpoint"] =
                "/projects/" + projectId + "/functionalmlds-v2",
            ["functionalmlds"] = new JObject
            {
                ["schema"] = "functionalmlds_runtime_context_v2",
                ["case_id"] = (string)trace["case_id"],
                ["model_version"] = "2.0.0-model",
                ["model_sha256"] = loaded.Sha256,
                ["profile"] = "executable",
                ["main_scenario_id"] = (string)trace["main_scenario_id"],
                ["runtime_actions"] = trace["runtime_actions"].DeepClone()
            }
        };
        var root = Path.Combine(
            Application.temporaryCachePath,
            "functionalmlds-v2-kaesesteinpilz-communication-smoke");
        if (Directory.Exists(root))
            Directory.Delete(root, true);
        var bridge = FunctionalMldsV2QuickAgentBridge.Create(
            setup.ToString(Formatting.None),
            modelJson,
            root);
        var actions = ((JArray)trace["runtime_actions"]).OfType<JObject>().ToList();

        var setupAction = actions.Single(item => (string)item["action_kind"] == "setup");
        bridge.RequireAction(
            "setup",
            ProviderSourceId(loaded, setupAction),
            BoundObservation(loaded, setupAction, false));

        var chatActions = actions.Where(item => (string)item["action_kind"] == "chat").ToList();
        var targetlessChats = chatActions
            .Where(item => !((JArray)item["target_ids"]).Values<string>().Any())
            .ToList();
        Require(
            targetlessChats.Count == 1,
            "KAESESTEINPILZ must expose exactly one trusted targetless chat mapping.");

        var providerSourceIds = chatActions
            .Select(item => ProviderSourceId(loaded, item))
            .Distinct(StringComparer.Ordinal)
            .ToList();
        foreach (var providerSourceId in providerSourceIds)
        {
            var genericText = BoundObservation(loaded, targetlessChats[0], false);
            genericText.InteractionMode =
                FunctionalMldsV2InteractionEvidenceEvaluator.NonDeicticMode;
            genericText.RequestedAgentId = providerSourceId;
            bridge.RequireAction("chat", providerSourceId, genericText);

            var responseObservation = CreateNonDeicticResponseObservationViaManager(
                loaded.Sha256,
                providerSourceId,
                targetlessChats[0]);
            Require(
                responseObservation.RequestedAgentId == null,
                "A non-deictic QuickAgentManager response must not invent a requested agent.");
            Require(
                string.Equals(
                    responseObservation.RoutedAgentId,
                    providerSourceId,
                    StringComparison.Ordinal),
                "QuickAgentManager must fall back to response.active_agent_id when routing is null.");
            Require(
                responseObservation.ResponseObserved,
                "QuickAgentManager must preserve the observed-response flag.");
            bridge.RequireAction("chat", providerSourceId, responseObservation);

            var genericAssessment = bridge.RecordInteraction(
                "chat",
                "unity_qam_non_deictic_null_routing_observed",
                providerSourceId,
                responseObservation,
                new { interaction_mode = "non_deictic" },
                new { active_agent_id = providerSourceId, routing = (object)null });
            Require(
                genericAssessment.Verdict == "pass"
                && genericAssessment.TargetResolved
                && genericAssessment.RouteResolved
                && genericAssessment.CompletionSatisfied,
                "A QuickAgentManager non-deictic response with null routing must complete successfully.");
        }

        foreach (var action in chatActions.Where(item => item != targetlessChats[0]))
        {
            var providerSourceId = ProviderSourceId(loaded, action);
            bridge.RequireAction(
                "chat",
                providerSourceId,
                BoundObservation(loaded, action, true));
        }

        var handoffActions = actions
            .Where(item => (string)item["action_kind"] == "handoff")
            .ToList();
        Require(handoffActions.Count > 0, "KAESESTEINPILZ has no handoff mappings.");
        var targetlessHandoffs = handoffActions
            .Where(item => !((JArray)item["target_ids"]).Values<string>().Any())
            .ToList();
        Require(
            targetlessHandoffs.Count == 1,
            "KAESESTEINPILZ must expose exactly one trusted targetless handoff mapping.");

        var genericProvider = loaded.Index.Require(
            (string)targetlessChats[0]["provider_entity_id"],
            "Entity");
        var genericProviderSourceId = ProviderSourceId(loaded, targetlessChats[0]);
        var modeledHandoffTarget = loaded.Index.Require(
            genericProvider.References("handoffTarget").First(),
            "Entity");
        var modeledHandoffTargetSourceId = modeledHandoffTarget.OptionalString("sourceAgentId")
            ?? modeledHandoffTarget.OptionalString("sourceId")
            ?? modeledHandoffTarget.Id;
        CreateNonDeicticHandoffObservationsViaManager(
            loaded.Sha256,
            genericProviderSourceId,
            modeledHandoffTargetSourceId,
            targetlessChats[0],
            targetlessHandoffs[0],
            out var chatHandoffObservation,
            out var handoffObservation);
        Require(
            string.Equals(
                chatHandoffObservation.CapabilityUseId,
                (string)targetlessChats[0]["capability_use_id"],
                StringComparison.Ordinal),
            "QuickAgentManager must bind the chat observation to the S11 chat chain.");
        Require(
            string.Equals(
                handoffObservation.CapabilityUseId,
                (string)targetlessHandoffs[0]["capability_use_id"],
                StringComparison.Ordinal),
            "QuickAgentManager must bind the handoff observation to the S12 handoff chain.");
        Require(
            chatHandoffObservation.RoutedAgentId == genericProviderSourceId
            && handoffObservation.RoutedAgentId == genericProviderSourceId,
            "Both observations must fall back to active_agent_id when routing is null.");
        Require(
            chatHandoffObservation.ModeledHandoff == true
            && handoffObservation.ModeledHandoff == true,
            "Both observations must preserve handoff.modeled_handoff when routing is null.");

        var chatWithHandoffAssessment = bridge.RecordInteraction(
            "chat",
            "unity_qam_non_deictic_chat_with_handoff_observed",
            genericProviderSourceId,
            chatHandoffObservation,
            new { interaction_mode = "non_deictic" },
            new
            {
                active_agent_id = genericProviderSourceId,
                routing = (object)null,
                handoff_to = modeledHandoffTargetSourceId
            });
        Require(
            chatWithHandoffAssessment.Verdict == "pass"
            && chatWithHandoffAssessment.RouteResolved
            && chatWithHandoffAssessment.CompletionSatisfied,
            "The S11 chat side of a non-deictic handoff response must pass.");

        var handoffAssessment = bridge.RecordInteraction(
            "handoff",
            "unity_qam_non_deictic_handoff_observed",
            genericProviderSourceId,
            handoffObservation,
            new { interaction_mode = "non_deictic" },
            new
            {
                active_agent_id = genericProviderSourceId,
                routing = (object)null,
                handoff_to = modeledHandoffTargetSourceId
            });
        Require(
            handoffAssessment.Verdict == "pass"
            && handoffAssessment.RouteResolved
            && handoffAssessment.CompletionSatisfied,
            "The S12 handoff side of the same non-deictic response must pass.");

        foreach (var providerSourceId in providerSourceIds)
        {
            var genericHandoff = BoundObservation(loaded, targetlessHandoffs[0], false);
            genericHandoff.RequestedAgentId = providerSourceId;
            bridge.RequireAction("handoff", providerSourceId, genericHandoff);
        }
        foreach (var action in handoffActions.Where(item => item != targetlessHandoffs[0]))
        {
            var providerSourceId = ProviderSourceId(loaded, action);
            bridge.RequireAction(
                "handoff",
                providerSourceId,
                BoundObservation(loaded, action, true));
        }
    }

    private static string ProviderSourceId(
        FunctionalMldsV2LoadResult loaded,
        JObject action)
    {
        var provider = loaded.Index.Require((string)action["provider_entity_id"], "Entity");
        return provider.OptionalString("sourceAgentId")
            ?? provider.OptionalString("sourceId")
            ?? provider.Id;
    }

    private static FunctionalMldsV2InteractionObservation
        CreateNonDeicticResponseObservationViaManager(
            string modelSha256,
            string activeAgentId,
            JObject action)
    {
        var managerObject = new GameObject("FunctionalMLDS_QAM_NonDeictic_Response_Smoke");
        try
        {
            var manager = managerObject.AddComponent<QuickAgentManager>();
            manager.activeAgentId = activeAgentId;

            var modelHashField = typeof(QuickAgentManager).GetField(
                "currentModelSha256",
                BindingFlags.Instance | BindingFlags.NonPublic);
            Require(modelHashField != null, "QuickAgentManager.currentModelSha256 is unavailable.");
            modelHashField.SetValue(manager, modelSha256);

            var response = new QuickAgentManager.ChatResponse
            {
                active_agent_id = activeAgentId,
                interaction_mode =
                    FunctionalMldsV2InteractionEvidenceEvaluator.NonDeicticMode,
                routing = null,
                model_binding = new QuickAgentManager.ModelBindingInfo
                {
                    capability_use_id = (string)action["capability_use_id"],
                    capability_id = (string)action["capability_id"],
                    runtime_binding_id = (string)action["runtime_binding_id"],
                    runtime_action_id = (string)action["runtime_action_id"]
                }
            };
            return InvokeManagerObservation(
                manager,
                "CreateInteractionObservation",
                response);
        }
        finally
        {
            UnityEngine.Object.DestroyImmediate(managerObject);
        }
    }

    private static void CreateNonDeicticHandoffObservationsViaManager(
        string modelSha256,
        string activeAgentId,
        string handoffTargetAgentId,
        JObject chatAction,
        JObject handoffAction,
        out FunctionalMldsV2InteractionObservation chatObservation,
        out FunctionalMldsV2InteractionObservation handoffObservation)
    {
        var managerObject = new GameObject("FunctionalMLDS_QAM_NonDeictic_Handoff_Smoke");
        try
        {
            var manager = managerObject.AddComponent<QuickAgentManager>();
            manager.activeAgentId = activeAgentId;

            var modelHashField = typeof(QuickAgentManager).GetField(
                "currentModelSha256",
                BindingFlags.Instance | BindingFlags.NonPublic);
            Require(modelHashField != null, "QuickAgentManager.currentModelSha256 is unavailable.");
            modelHashField.SetValue(manager, modelSha256);

            var response = new QuickAgentManager.ChatResponse
            {
                active_agent_id = activeAgentId,
                interaction_mode =
                    FunctionalMldsV2InteractionEvidenceEvaluator.NonDeicticMode,
                routing = null,
                model_binding = ModelBinding(chatAction),
                handoff_model_binding = ModelBinding(handoffAction),
                handoff = new QuickAgentManager.Handoff
                {
                    from = activeAgentId,
                    to = handoffTargetAgentId,
                    reason = "modeled regression handoff",
                    modeled_handoff = true
                }
            };
            chatObservation = InvokeManagerObservation(
                manager,
                "CreateInteractionObservation",
                response);
            handoffObservation = InvokeManagerObservation(
                manager,
                "CreateHandoffInteractionObservation",
                response);
        }
        finally
        {
            UnityEngine.Object.DestroyImmediate(managerObject);
        }
    }

    private static FunctionalMldsV2InteractionObservation InvokeManagerObservation(
        QuickAgentManager manager,
        string methodName,
        QuickAgentManager.ChatResponse response)
    {
        var method = typeof(QuickAgentManager).GetMethod(
            methodName,
            BindingFlags.Instance | BindingFlags.NonPublic,
            null,
            new[]
            {
                typeof(string),
                typeof(QuickAgentManager.ChatResponse),
                typeof(bool)
            },
            null);
        Require(method != null, "QuickAgentManager." + methodName + " is unavailable.");
        var observation = method.Invoke(
                manager,
                new object[]
                {
                    FunctionalMldsV2InteractionEvidenceEvaluator.NonDeicticMode,
                    response,
                    true
                })
            as FunctionalMldsV2InteractionObservation;
        Require(observation != null, "QuickAgentManager returned no interaction observation.");
        return observation;
    }

    private static QuickAgentManager.ModelBindingInfo ModelBinding(JObject action)
    {
        return new QuickAgentManager.ModelBindingInfo
        {
            capability_use_id = (string)action["capability_use_id"],
            capability_id = (string)action["capability_id"],
            runtime_binding_id = (string)action["runtime_binding_id"],
            runtime_action_id = (string)action["runtime_action_id"]
        };
    }

    private static FunctionalMldsV2InteractionObservation BoundObservation(
        FunctionalMldsV2LoadResult loaded,
        JObject action,
        bool withTarget)
    {
        var providerSourceId = ProviderSourceId(loaded, action);
        var observation = new FunctionalMldsV2InteractionObservation
        {
            InteractionMode = withTarget
                ? FunctionalMldsV2InteractionEvidenceEvaluator.DeicticMode
                : FunctionalMldsV2InteractionEvidenceEvaluator.NonDeicticMode,
            ModelSha256 = loaded.Sha256,
            BindingRegistryValid = true,
            RequestedAgentId = providerSourceId,
            CapabilityUseId = (string)action["capability_use_id"],
            CapabilityId = (string)action["capability_id"],
            RuntimeBindingId = (string)action["runtime_binding_id"],
            RuntimeActionId = (string)action["runtime_action_id"]
        };
        if (!withTarget)
            return observation;

        var targetId = ((JArray)action["target_ids"])
            .Values<string>()
            .First(id => loaded.Index.Require(id).Type == "Entity");
        var target = loaded.Index.Require(targetId, "Entity");
        observation.SelectionObserved = true;
        observation.SelectionState =
            FunctionalMldsV2InteractionEvidenceEvaluator.ResolvedSelectionState;
        observation.SelectedEntityId = target.Id;
        observation.SelectedSourceObjectId = target.OptionalString("sourceId");
        return observation;
    }

    private static FunctionalMldsV2InteractionObservation ValidObservation(string modelSha256)
    {
        return new FunctionalMldsV2InteractionObservation
        {
            InteractionMode = FunctionalMldsV2InteractionEvidenceEvaluator.DeicticMode,
            ModelSha256 = modelSha256,
            BindingRegistryValid = true,
            SelectionObserved = true,
            SelectionState = FunctionalMldsV2InteractionEvidenceEvaluator.ResolvedSelectionState,
            SelectedEntityId = "target-asset",
            SelectedSourceObjectId = "target-asset-source",
            RequestedAgentId = "runtime-agent",
            RoutedAgentId = "runtime-agent",
            ResponseObserved = true,
            ResponseSelectedEntityId = "target-asset",
            ResponseGroundedEntityIds = new System.Collections.Generic.List<string> { "target-asset" },
            HandoffObserved = false
        };
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
                    ["scenario_id"] = "main",
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
