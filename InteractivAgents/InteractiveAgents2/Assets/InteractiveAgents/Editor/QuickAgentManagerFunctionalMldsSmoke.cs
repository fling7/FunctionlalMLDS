using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Text;
using System.Threading;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

public static class QuickAgentManagerFunctionalMldsSmoke
{
    private const string DefaultBackendBaseUrl = "http://127.0.0.1:8787";
    private const string DefaultProjectId = "classroom_dinosaur";

    [Serializable]
    private class SetupRequest
    {
        public string project_id;
        public string memory_mode;
    }

    public static void Run()
    {
        var backendBaseUrl = Environment.GetEnvironmentVariable("FUNCTIONALMLDS_BACKEND_URL");
        if (string.IsNullOrWhiteSpace(backendBaseUrl))
            backendBaseUrl = DefaultBackendBaseUrl;

        var projectId = Environment.GetEnvironmentVariable("FUNCTIONALMLDS_PROJECT_ID");
        if (string.IsNullOrWhiteSpace(projectId))
            projectId = DefaultProjectId;

        var runChatSmoke = IsEnabled(Environment.GetEnvironmentVariable("FUNCTIONALMLDS_CHAT_SMOKE"));
        RunSmoke(backendBaseUrl.TrimEnd('/'), projectId.Trim(), runChatSmoke);
        Debug.Log("[FunctionalMLDSUnitySmoke] OK");
    }

    private static void RunSmoke(string backendBaseUrl, string projectId, bool runChatSmoke)
    {
        var listUrl = backendBaseUrl + "/projects";
        using (var req = UnityWebRequest.Get(listUrl))
        {
            SendBlocking(req);
            RequireSuccess(req, "GET /projects");
            var body = req.downloadHandler.text ?? "";
            if (!body.Contains("\"id\":\"" + projectId + "\"") && !body.Contains("\"id\": \"" + projectId + "\""))
                throw new Exception("Project list does not contain project_id=" + projectId + ". Body: " + body);
        }

        var setupPayload = JsonUtility.ToJson(new SetupRequest
        {
            project_id = projectId,
            memory_mode = "shared_history"
        });
        QuickAgentManager.SetupResponse setupResponse;
        string setupJson;
        using (var req = new UnityWebRequest(backendBaseUrl + "/setup", "POST"))
        {
            req.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(setupPayload));
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            SendBlocking(req);
            RequireSuccess(req, "POST /setup");
            setupJson = req.downloadHandler.text;
            setupResponse = JsonUtility.FromJson<QuickAgentManager.SetupResponse>(setupJson);
        }

        if (setupResponse == null || string.IsNullOrWhiteSpace(setupResponse.session_id))
            throw new Exception("Setup response has no session_id.");
        var agents = setupResponse.agents ?? Array.Empty<QuickAgentManager.AgentPlacement>();
        if (agents.Length == 0)
            throw new Exception("Setup response has no agents.");
        ValidatePlacementPreflight(agents);
        ValidateNativeV2Contract(backendBaseUrl, setupJson, setupResponse, agents[0].id);

        var go = new GameObject("FunctionalMLDS_QuickAgentManager_Smoke");
        var manager = go.AddComponent<QuickAgentManager>();
        manager.backendBaseUrl = backendBaseUrl;
        manager.memoryMode = "shared_history";
        manager.showUi = false;
        manager.enableTts = false;
        manager.enableVoiceInput = false;
        manager.sessionId = setupResponse.session_id;

        SetPrivate(manager, "useProjectSelection", true);
        SetPrivate(manager, "selectedProjectId", projectId);
        SetPrivate(manager, "selectedProjectIndex", 0);
        SetPrivate(manager, "lastAgents", agents);
        manager.activeAgentId = agents[0].id;

        InvokePrivate(manager, "EnsureSceneBasics");
        InvokePrivate(manager, "UpdateAgentVoices", (object)agents);
        InvokePrivate(manager, "SpawnAgents", (object)agents);

        var agentObjects = GetPrivate<IDictionary>(manager, "agentObjects");
        if (agentObjects == null)
            throw new Exception("QuickAgentManager.agentObjects could not be inspected.");
        if (agentObjects.Count != agents.Length)
            throw new Exception($"Spawn count mismatch: got {agentObjects.Count}, expected {agents.Length}.");

        foreach (var agent in agents)
        {
            if (agent == null || string.IsNullOrWhiteSpace(agent.id))
                throw new Exception("Spawned agent response contains empty id.");
            if (!agentObjects.Contains(agent.id))
                throw new Exception("Spawned agent dictionary misses id=" + agent.id);
            if (agent.position == null)
                throw new Exception("Agent has no position: " + agent.id);
            if (agent.forward == null)
                throw new Exception("Agent has no forward vector: " + agent.id);

            var visual = agentObjects[agent.id];
            var obj = visual.GetType().GetField("obj", BindingFlags.Instance | BindingFlags.Public)?.GetValue(visual) as GameObject;
            if (obj == null)
                throw new Exception("Spawned GameObject missing for agent=" + agent.id);
        }

        Debug.Log(
            "[FunctionalMLDSUnitySmoke] project_id=" + projectId
            + "; session_id_present=True"
            + "; spawned_agents=" + agentObjects.Count
            + "; expected_agents=" + agents.Length);

        if (runChatSmoke)
            RunChatAndHandoffSmoke(backendBaseUrl, manager, setupResponse.session_id, agents[0].id);

        UnityEngine.Object.DestroyImmediate(go);
    }

    private static void ValidateNativeV2Contract(
        string backendBaseUrl,
        string setupJson,
        QuickAgentManager.SetupResponse setupResponse,
        string activeAgentId)
    {
        if (setupResponse.metamodel_version != "2.0.0-model"
            || setupResponse.trace_schema_version != "2.0"
            || setupResponse.functionalmlds_profile != "executable"
            || string.IsNullOrWhiteSpace(setupResponse.model_sha256))
            throw new Exception("Setup response does not expose the complete executable V2 contract.");
        var endpoint = FunctionalMldsV2QuickAgentBridge.ModelEndpointFor(setupJson);
        if (string.IsNullOrWhiteSpace(endpoint)
            || endpoint != setupResponse.functionalmlds_model_endpoint)
            throw new Exception("Setup response has no consistent V2 model endpoint.");

        var modelUrl = endpoint.StartsWith("http://", StringComparison.OrdinalIgnoreCase)
            || endpoint.StartsWith("https://", StringComparison.OrdinalIgnoreCase)
            ? endpoint
            : backendBaseUrl.TrimEnd('/') + "/" + endpoint.TrimStart('/');
        string modelJson;
        using (var req = UnityWebRequest.Get(modelUrl))
        {
            SendBlocking(req);
            RequireSuccess(req, "GET FunctionalMLDS V2 model");
            modelJson = req.downloadHandler.text;
        }

        var logDirectory = Path.Combine(
            Application.temporaryCachePath,
            "functionalmlds-v2-real-http-smoke-" + Guid.NewGuid().ToString("N"));
        try
        {
            var bridge = FunctionalMldsV2QuickAgentBridge.Create(setupJson, modelJson, logDirectory);
            if (bridge.ModelSha256 != setupResponse.model_sha256)
                throw new Exception("Unity bridge model hash differs from the setup contract.");
            bridge.RequireAction("setup", activeAgentId);
            bridge.Record(
                "setup",
                "unity_real_http_setup_smoke",
                activeAgentId,
                "success",
                new { project = DefaultProjectId },
                new { accepted = true });
            if (File.ReadAllLines(Path.Combine(logDirectory, "events.v2.jsonl")).Length != 1
                || File.ReadAllLines(Path.Combine(logDirectory, "runtime_validation.v2.jsonl")).Length != 1)
                throw new Exception("Unity bridge did not write one complete V2 evidence pair.");
            Debug.Log(
                "[FunctionalMLDSUnitySmoke] native_v2=True"
                + "; model_sha256=" + bridge.ModelSha256
                + "; model_endpoint=" + endpoint);
        }
        finally
        {
            if (Directory.Exists(logDirectory))
                Directory.Delete(logDirectory, true);
        }
    }

    private static void ValidatePlacementPreflight(QuickAgentManager.AgentPlacement[] agents)
    {
        var method = typeof(QuickAgentManager).GetMethod(
            "ValidateExecutableAgentPlacements",
            BindingFlags.Static | BindingFlags.NonPublic);
        if (method == null)
            throw new MissingMethodException(nameof(QuickAgentManager), "ValidateExecutableAgentPlacements");

        var validArgs = new object[] { agents, null };
        if (!(bool)method.Invoke(null, validArgs))
            throw new Exception("Real V2 placements failed Unity preflight: " + validArgs[1]);

        var invalid = new[]
        {
            new QuickAgentManager.AgentPlacement
            {
                id = "invalid-placement",
                position = new QuickAgentManager.Vector3Data { x = 0f, y = 0f, z = 0f },
                forward = new QuickAgentManager.Vector3Data { x = 0f, y = 0f, z = 0f },
            }
        };
        var invalidArgs = new object[] { invalid, null };
        if ((bool)method.Invoke(null, invalidArgs))
            throw new Exception("Unity V2 placement preflight accepted a zero forward vector.");
    }

    private static void RunChatSmoke(string backendBaseUrl, QuickAgentManager manager, string sessionId, string activeAgentId)
    {
        var message = "Welche Ausstattung gibt es im Unterrichtsbereich? Antworte kurz und nenne nur Dinge aus dem Raumwissen.";
        var payload = QuickAgentManager.SerializeChatRequest(new QuickAgentManager.ChatRequest
        {
            session_id = sessionId,
            active_agent_id = activeAgentId,
            user_text = message,
            interaction_mode = FunctionalMlds.V2.FunctionalMldsV2InteractionEvidenceEvaluator.NonDeicticMode
        });

        QuickAgentManager.ChatResponse chatResponse;
        using (var req = new UnityWebRequest(backendBaseUrl + "/chat", "POST"))
        {
            req.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(payload));
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            SendBlocking(req);
            RequireSuccess(req, "POST /chat");
            chatResponse = JsonUtility.FromJson<QuickAgentManager.ChatResponse>(req.downloadHandler.text);
        }

        if (chatResponse == null || chatResponse.events == null || chatResponse.events.Length == 0)
            throw new Exception("Chat response has no events.");

        manager.sessionId = chatResponse.session_id;
        if (!string.IsNullOrEmpty(chatResponse.memory_mode))
            manager.memoryMode = chatResponse.memory_mode;
        InvokePrivate(manager, "AppendChatEvents", (object)chatResponse.events);

        var chatLog = GetPrivate<List<string>>(manager, "chatLog");
        if (chatLog == null || chatLog.Count == 0)
            throw new Exception("QuickAgentManager chatLog was not updated.");

        var combinedText = string.Join("\n", chatLog).ToLowerInvariant();
        if (!combinedText.Contains("tafel")
            && !combinedText.Contains("chalkboard")
            && !combinedText.Contains("schuel")
            && !combinedText.Contains("schül")
            && !combinedText.Contains("desk")
            && !combinedText.Contains("pult"))
        {
            throw new Exception("Chat response was not visibly grounded in classroom equipment. Text: " + combinedText);
        }

        Debug.Log(
            "[FunctionalMLDSUnitySmoke] chat_events=" + chatResponse.events.Length
            + "; chat_log_entries=" + chatLog.Count
            + "; active_agent=" + activeAgentId);
    }

    private static void SendBlocking(UnityWebRequest request)
    {
        var operation = request.SendWebRequest();
        while (!operation.isDone)
            Thread.Sleep(25);
    }

    private static void RunChatAndHandoffSmoke(string backendBaseUrl, QuickAgentManager manager, string sessionId, string activeAgentId)
    {
        var roomResponse = SendChat(
            backendBaseUrl,
            sessionId,
            activeAgentId,
            "Welche Ausstattung gibt es im Unterrichtsbereich? Antworte kurz und nenne nur Dinge aus dem Raumwissen.");
        AppendResponse(manager, roomResponse);

        var chatLog = GetPrivate<List<string>>(manager, "chatLog");
        if (chatLog == null || chatLog.Count == 0)
            throw new Exception("QuickAgentManager chatLog was not updated.");

        var combinedText = string.Join("\n", chatLog).ToLowerInvariant();
        if (!combinedText.Contains("tafel")
            && !combinedText.Contains("chalkboard")
            && !combinedText.Contains("schuel")
            && !combinedText.Contains("student")
            && !combinedText.Contains("desk")
            && !combinedText.Contains("pult"))
        {
            throw new Exception("Chat response was not visibly grounded in classroom equipment. Text: " + combinedText);
        }

        var handoffResponse = SendChat(
            backendBaseUrl,
            roomResponse.session_id,
            activeAgentId,
            "Was kannst du mir ueber das Dinosaurierskelett sagen?");
        AppendResponse(manager, handoffResponse);

        if (handoffResponse.handoff == null || string.IsNullOrWhiteSpace(handoffResponse.handoff.to))
            throw new Exception("Expected handoff response, but backend returned no handoff.");
        if (handoffResponse.handoff.to != "exhibit_interpreter")
            throw new Exception("Expected handoff to exhibit_interpreter, got: " + handoffResponse.handoff.to);

        combinedText = string.Join("\n", chatLog).ToLowerInvariant();
        if (!combinedText.Contains("dinosaur") && !combinedText.Contains("skeleton") && !combinedText.Contains("paleontology"))
            throw new Exception("Handoff answer was not visibly grounded in dinosaur exhibit knowledge. Text: " + combinedText);

        Debug.Log(
            "[FunctionalMLDSUnitySmoke] chat_events=" + (roomResponse.events.Length + handoffResponse.events.Length)
            + "; chat_log_entries=" + chatLog.Count
            + "; active_agent=" + activeAgentId
            + "; handoff_to=" + handoffResponse.handoff.to);
    }

    private static QuickAgentManager.ChatResponse SendChat(string backendBaseUrl, string sessionId, string activeAgentId, string message)
    {
        var payload = QuickAgentManager.SerializeChatRequest(new QuickAgentManager.ChatRequest
        {
            session_id = sessionId,
            active_agent_id = activeAgentId,
            user_text = message,
            interaction_mode = FunctionalMlds.V2.FunctionalMldsV2InteractionEvidenceEvaluator.NonDeicticMode
        });

        using (var req = new UnityWebRequest(backendBaseUrl + "/chat", "POST"))
        {
            req.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(payload));
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            SendBlocking(req);
            RequireSuccess(req, "POST /chat");
            var chatResponse = JsonUtility.FromJson<QuickAgentManager.ChatResponse>(req.downloadHandler.text);
            if (chatResponse == null || chatResponse.events == null || chatResponse.events.Length == 0)
                throw new Exception("Chat response has no events.");
            return chatResponse;
        }
    }

    private static void AppendResponse(QuickAgentManager manager, QuickAgentManager.ChatResponse chatResponse)
    {
        manager.sessionId = chatResponse.session_id;
        if (!string.IsNullOrEmpty(chatResponse.memory_mode))
            manager.memoryMode = chatResponse.memory_mode;
        InvokePrivate(manager, "AppendChatEvents", (object)chatResponse.events);
    }

    private static void RequireSuccess(UnityWebRequest request, string label)
    {
        if (request.result == UnityWebRequest.Result.Success)
            return;
        throw new Exception(label + " failed: " + request.error + " | " + request.downloadHandler?.text);
    }

    private static bool IsEnabled(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            return false;
        value = value.Trim().ToLowerInvariant();
        return value == "1" || value == "true" || value == "yes" || value == "on";
    }

    private static void SetPrivate(object target, string fieldName, object value)
    {
        var field = target.GetType().GetField(fieldName, BindingFlags.Instance | BindingFlags.NonPublic);
        if (field == null)
            throw new MissingFieldException(target.GetType().Name, fieldName);
        field.SetValue(target, value);
    }

    private static T GetPrivate<T>(object target, string fieldName) where T : class
    {
        var field = target.GetType().GetField(fieldName, BindingFlags.Instance | BindingFlags.NonPublic);
        if (field == null)
            throw new MissingFieldException(target.GetType().Name, fieldName);
        return field.GetValue(target) as T;
    }

    private static void InvokePrivate(object target, string methodName, params object[] args)
    {
        var method = target.GetType().GetMethod(methodName, BindingFlags.Instance | BindingFlags.NonPublic);
        if (method == null)
            throw new MissingMethodException(target.GetType().Name, methodName);
        method.Invoke(target, args);
    }
}
