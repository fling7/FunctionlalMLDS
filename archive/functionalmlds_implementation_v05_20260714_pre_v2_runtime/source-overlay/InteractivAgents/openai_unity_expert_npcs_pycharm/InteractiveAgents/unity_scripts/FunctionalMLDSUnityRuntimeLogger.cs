using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using UnityEngine;

public class FunctionalMLDSUnityRuntimeLogger : MonoBehaviour
{
    public bool enableLogging = false;
    public string overrideLogFilePath = "";
    public bool mirrorToUnityDebug = false;

    private static readonly Regex SecretTokenRegex = new Regex(@"sk-[A-Za-z0-9_-]{12,}", RegexOptions.Compiled);
    private static readonly Regex SecretHeaderRegex = new Regex(@"(?i)(api[_-]?key|authorization|bearer)\s*[:=]\s*[^,\s}]+", RegexOptions.Compiled);

    public void LogSetupCompleted(string caseId, string sessionId, string memoryMode, int agentCount)
    {
        var trace = BuildTraceRef(caseId, "SETUP-INTERACTIVE-SESSION", "BACKEND-SETUP", "S09");
        AppendEvent(
            caseId,
            "unity_setup_completed",
            sessionId,
            null,
            trace,
            $"memory_mode={memoryMode}",
            $"setup ok; agents={agentCount}",
            new Dictionary<string, string> { { "agent_count", agentCount.ToString() } });
    }

    public void LogAgentSelected(string caseId, string sessionId, string agentId, string source)
    {
        AppendEvent(
            caseId,
            "unity_agent_selected",
            sessionId,
            agentId,
            TraceRef.Empty,
            $"source={source}",
            $"active_agent_id={agentId}",
            new Dictionary<string, string> { { "source", source ?? "" } });
    }

    public void LogChatSent(string caseId, string sessionId, string agentId, int userTextLength)
    {
        var trace = BuildTraceRef(caseId, "ANSWER-ROOM-GROUNDED-QUESTION", "BACKEND-CHAT", "S11");
        AppendEvent(
            caseId,
            "unity_chat_sent",
            sessionId,
            agentId,
            trace,
            $"active_agent_id={agentId}; user_text_length={userTextLength}",
            "chat request sent",
            new Dictionary<string, string> { { "user_text_length", userTextLength.ToString() } });
    }

    public void LogChatReceived(string caseId, string sessionId, string agentId, int eventCount, bool handoff)
    {
        var trace = BuildTraceRef(caseId, "ANSWER-ROOM-GROUNDED-QUESTION", "BACKEND-CHAT", "S11");
        AppendEvent(
            caseId,
            "unity_chat_received",
            sessionId,
            agentId,
            trace,
            $"active_agent_id={agentId}",
            $"chat response received; events={eventCount}; handoff={handoff}",
            new Dictionary<string, string>
            {
                { "event_count", eventCount.ToString() },
                { "handoff", handoff ? "true" : "false" }
            });
    }

    public void LogHandoffArrived(string caseId, string sessionId, string fromAgentId, string toAgentId, int eventCount)
    {
        var trace = BuildTraceRef(caseId, "HANDOFF-TO-RESPONSIBLE-AGENT", "BACKEND-CHAT-HANDOFF", "S12");
        AppendEvent(
            caseId,
            "unity_handoff_arrived",
            sessionId,
            toAgentId,
            trace,
            $"from={fromAgentId}; to={toAgentId}",
            $"handoff target reached; deferred_events={eventCount}",
            new Dictionary<string, string>
            {
                { "from", fromAgentId ?? "" },
                { "to", toAgentId ?? "" },
                { "event_count", eventCount.ToString() }
            });
    }

    private void AppendEvent(
        string caseId,
        string eventType,
        string sessionId,
        string agentId,
        TraceRef trace,
        string inputSummary,
        string outputSummary,
        Dictionary<string, string> metadata)
    {
        if (!enableLogging)
            return;

        caseId = string.IsNullOrWhiteSpace(caseId) ? "unity_manual_room" : caseId.Trim();
        var json = BuildEventJson(caseId, eventType, sessionId, agentId, trace, inputSummary, outputSummary, metadata);
        var path = ResolveLogPath(caseId);
        var dir = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(dir))
            Directory.CreateDirectory(dir);
        File.AppendAllText(path, json + Environment.NewLine, Encoding.UTF8);

        if (mirrorToUnityDebug)
            Debug.Log("[FunctionalMLDSRuntime] " + json);
    }

    private string ResolveLogPath(string caseId)
    {
        if (!string.IsNullOrWhiteSpace(overrideLogFilePath))
            return overrideLogFilePath;
        return Path.Combine(Application.persistentDataPath, "FunctionalMLDS", "runtime_logs", SafePathPart(caseId), "events.jsonl");
    }

    private static string BuildEventJson(
        string caseId,
        string eventType,
        string sessionId,
        string agentId,
        TraceRef trace,
        string inputSummary,
        string outputSummary,
        Dictionary<string, string> metadata)
    {
        var parts = new List<string>
        {
            Pair("schema", "functionalmlds_runtime_event"),
            Pair("schema_version", "1.0"),
            Pair("event_id", "EVT-" + Guid.NewGuid().ToString("N")),
            Pair("timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")),
            Pair("case_id", caseId),
            Pair("session_id", sessionId),
            Pair("event_type", eventType),
            Pair("agent_id", agentId),
            Pair("scenario_step_id", trace.scenarioStepId),
            Pair("capability_id", trace.capabilityId),
            Pair("runtime_binding_id", trace.runtimeBindingId),
            Pair("runtime_action_id", trace.runtimeActionId),
            Pair("input_summary", Redact(inputSummary)),
            Pair("output_summary", Redact(outputSummary)),
            "\"duration_ms\":null",
            Pair("status", "success"),
            "\"error_summary\":null",
            "\"metadata\":" + MetadataJson(metadata)
        };
        return "{" + string.Join(",", parts) + "}";
    }

    private static TraceRef BuildTraceRef(string caseId, string capabilitySuffix, string actionSuffix, string stepSuffix)
    {
        var prefix = (caseId ?? "unity_manual_room").Trim().ToUpperInvariant();
        return new TraceRef
        {
            scenarioStepId = $"STEP-{prefix}-{stepSuffix}",
            capabilityId = $"CAP-{prefix}-{capabilitySuffix}",
            runtimeBindingId = $"RB-{prefix}-{capabilitySuffix}",
            runtimeActionId = $"RA-{prefix}-{actionSuffix}"
        };
    }

    private static string MetadataJson(Dictionary<string, string> metadata)
    {
        if (metadata == null || metadata.Count == 0)
            return "{}";

        var parts = new List<string>();
        foreach (var item in metadata)
            parts.Add(JsonString(item.Key) + ":" + JsonString(Redact(item.Value)));
        return "{" + string.Join(",", parts) + "}";
    }

    private static string Pair(string key, string value)
    {
        return JsonString(key) + ":" + JsonString(string.IsNullOrWhiteSpace(value) ? null : value);
    }

    private static string JsonString(string value)
    {
        if (value == null)
            return "null";
        return "\"" + value
            .Replace("\\", "\\\\")
            .Replace("\"", "\\\"")
            .Replace("\r", "\\r")
            .Replace("\n", "\\n")
            .Replace("\t", "\\t") + "\"";
    }

    private static string Redact(string value)
    {
        if (string.IsNullOrEmpty(value))
            return "";
        value = SecretTokenRegex.Replace(value, "[REDACTED]");
        value = SecretHeaderRegex.Replace(value, "[REDACTED]");
        value = Regex.Replace(value, @"\s+", " ").Trim();
        return value.Length <= 2000 ? value : value.Substring(0, 1985).TrimEnd() + " [TRUNCATED]";
    }

    private static string SafePathPart(string value)
    {
        value = string.IsNullOrWhiteSpace(value) ? "unity_manual_room" : value.Trim();
        foreach (var invalid in Path.GetInvalidFileNameChars())
            value = value.Replace(invalid, '_');
        return value;
    }

    private struct TraceRef
    {
        public static readonly TraceRef Empty = new TraceRef();
        public string scenarioStepId;
        public string capabilityId;
        public string runtimeBindingId;
        public string runtimeActionId;
    }
}
