using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace FunctionalMlds.V2
{
    /// <summary>
    /// References which are not part of the executable ScenarioStep -> CapabilityUse ->
    /// Capability -> RuntimeBinding -> RuntimeAction chain. Callers must supply these exact
    /// identifiers; the logger deliberately never guesses them from names or naming patterns.
    /// </summary>
    [Serializable]
    public sealed class FunctionalMldsV2TraceReferences
    {
        public string CaseId { get; set; }
        public List<string> AssertionIds { get; set; } = new List<string>();
        public List<string> ValidationCaseIds { get; set; } = new List<string>();
        public List<string> RuntimeValidationTargetIds { get; set; } = new List<string>();
    }

    [Serializable]
    public sealed class FunctionalMldsV2RuntimeEvent
    {
        [JsonProperty("schema")]
        public string Schema { get; set; } = FunctionalMldsV2Lexemes.RuntimeEventSchema;

        [JsonProperty("schema_version")]
        public string SchemaVersion { get; set; } = FunctionalMldsV2Lexemes.RuntimeSchemaVersion;

        [JsonProperty("event_id")]
        public string EventId { get; set; }

        [JsonProperty("timestamp")]
        public string Timestamp { get; set; }

        [JsonProperty("case_id")]
        public string CaseId { get; set; }

        [JsonProperty("session_id")]
        public string SessionId { get; set; }

        [JsonProperty("event_type")]
        public string EventType { get; set; }

        [JsonProperty("agent_id")]
        public string AgentId { get; set; }

        [JsonProperty("model_version")]
        public string ModelVersion { get; set; }

        [JsonProperty("model_sha256")]
        public string ModelSha256 { get; set; }

        [JsonProperty("scenario_step_id")]
        public string ScenarioStepId { get; set; }

        [JsonProperty("capability_use_id")]
        public string CapabilityUseId { get; set; }

        [JsonProperty("capability_id")]
        public string CapabilityId { get; set; }

        [JsonProperty("provider_entity_id")]
        public string ProviderEntityId { get; set; }

        [JsonProperty("target_ids")]
        public List<string> TargetIds { get; set; } = new List<string>();

        [JsonProperty("runtime_binding_id")]
        public string RuntimeBindingId { get; set; }

        [JsonProperty("runtime_action_id")]
        public string RuntimeActionId { get; set; }

        [JsonProperty("assertion_ids")]
        public List<string> AssertionIds { get; set; } = new List<string>();

        [JsonProperty("validation_case_ids")]
        public List<string> ValidationCaseIds { get; set; } = new List<string>();

        [JsonProperty("runtime_validation_target_ids")]
        public List<string> RuntimeValidationTargetIds { get; set; } = new List<string>();

        [JsonProperty("input_summary")]
        public string InputSummary { get; set; }

        [JsonProperty("output_summary")]
        public string OutputSummary { get; set; }

        [JsonProperty("duration_ms")]
        public double? DurationMs { get; set; }

        [JsonProperty("status")]
        public string Status { get; set; }

        [JsonProperty("error_summary")]
        public string ErrorSummary { get; set; }

        [JsonProperty("metadata")]
        public JObject Metadata { get; set; } = new JObject();
    }

    /// <summary>
    /// JSONL logger for runtime_event_v2.schema.json. Every model reference is supplied by the
    /// caller and checked against the loaded native V2 instance before a line is written.
    /// </summary>
    public sealed class FunctionalMldsV2RuntimeLogger
    {
        private static readonly Regex SecretToken = new Regex(@"sk-[A-Za-z0-9_-]{12,}", RegexOptions.Compiled);
        private static readonly Regex SecretHeader = new Regex(
            @"(?i)(api[_-]?key|authorization|bearer)\s*[:=]\s*[^,\s}]+",
            RegexOptions.Compiled);
        private static readonly Regex UpperSha256 = new Regex("^[A-F0-9]{64}$", RegexOptions.Compiled);
        private static readonly HashSet<string> Statuses = new HashSet<string>(StringComparer.Ordinal)
        {
            "success", "failed", "error", "inconclusive"
        };

        private readonly object _gate = new object();
        private readonly string _path;
        private readonly FunctionalMldsV2ModelIndex _index;
        private readonly FunctionalMldsV2RuntimeContext _context;

        public FunctionalMldsV2RuntimeLogger(
            string path,
            FunctionalMldsV2ModelIndex index,
            FunctionalMldsV2RuntimeContext context)
        {
            if (string.IsNullOrWhiteSpace(path))
                throw new ArgumentException("A V2 runtime log path is required.", nameof(path));
            _path = Path.GetFullPath(path);
            _index = index ?? throw new ArgumentNullException(nameof(index));
            _context = context ?? throw new ArgumentNullException(nameof(context));
            _index.Require(_context.ScenarioId, "Scenario");
            if (!string.Equals(_context.MetamodelVersion, FunctionalMldsV2Lexemes.ModelVersion, StringComparison.Ordinal))
                throw new FunctionalMldsV2FormatException("RuntimeContext.model version is not the accepted V2 model release.");
            if (!UpperSha256.IsMatch(_context.ModelSha256 ?? string.Empty))
                throw new FunctionalMldsV2FormatException("RuntimeContext.model SHA-256 must contain 64 uppercase hexadecimal characters.");
        }

        public FunctionalMldsV2RuntimeEvent Append(
            string eventType,
            FunctionalMldsV2ExecutionReference execution,
            FunctionalMldsV2TraceReferences traceReferences,
            string status,
            object inputSummary,
            object outputSummary,
            double? durationMs = null,
            string errorSummary = null,
            JObject metadata = null)
        {
            if (string.IsNullOrWhiteSpace(eventType))
                throw new ArgumentException("eventType is required.", nameof(eventType));
            if (!Statuses.Contains(status ?? string.Empty))
                throw new ArgumentException("Unsupported V2 runtime status.", nameof(status));
            if (durationMs.HasValue && durationMs.Value < 0)
                throw new ArgumentOutOfRangeException(nameof(durationMs), "durationMs cannot be negative.");

            ValidateExecution(execution);
            ValidateTraceReferences(traceReferences, execution);

            var runtimeEvent = new FunctionalMldsV2RuntimeEvent
            {
                EventId = "EVT-" + Guid.NewGuid().ToString("N"),
                Timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ", CultureInfo.InvariantCulture),
                CaseId = traceReferences.CaseId.Trim(),
                SessionId = _context.SessionId,
                EventType = eventType.Trim(),
                AgentId = _context.ActiveAgentId,
                ModelVersion = _context.MetamodelVersion,
                ModelSha256 = _context.ModelSha256,
                ScenarioStepId = execution.ScenarioStepId,
                CapabilityUseId = execution.CapabilityUseId,
                CapabilityId = execution.CapabilityId,
                ProviderEntityId = execution.ProviderId,
                TargetIds = Copy(trace: execution.TargetIds),
                RuntimeBindingId = execution.RuntimeBindingId,
                RuntimeActionId = execution.RuntimeActionId,
                AssertionIds = Copy(traceReferences.AssertionIds),
                ValidationCaseIds = Copy(traceReferences.ValidationCaseIds),
                RuntimeValidationTargetIds = Copy(traceReferences.RuntimeValidationTargetIds),
                InputSummary = Summary(inputSummary),
                OutputSummary = Summary(outputSummary),
                DurationMs = durationMs,
                Status = status,
                ErrorSummary = string.IsNullOrWhiteSpace(errorSummary) ? null : Summary(errorSummary),
                Metadata = CleanMetadata(metadata)
            };

            var directory = Path.GetDirectoryName(_path);
            if (!string.IsNullOrEmpty(directory))
                Directory.CreateDirectory(directory);
            var line = JsonConvert.SerializeObject(runtimeEvent, Formatting.None);
            lock (_gate)
            {
                File.AppendAllText(_path, line + Environment.NewLine);
            }
            return runtimeEvent;
        }

        private void ValidateExecution(FunctionalMldsV2ExecutionReference execution)
        {
            if (execution == null)
                throw new ArgumentNullException(nameof(execution));
            RequireText(execution.ScenarioStepId, "scenario_step_id");
            RequireText(execution.CapabilityUseId, "capability_use_id");
            RequireText(execution.CapabilityId, "capability_id");
            RequireText(execution.ProviderId, "provider_entity_id");
            RequireText(execution.RuntimeBindingId, "runtime_binding_id");
            RequireText(execution.RuntimeActionId, "runtime_action_id");

            var step = _index.Require(execution.ScenarioStepId, "ScenarioStep");
            var use = _index.Require(execution.CapabilityUseId, "CapabilityUse");
            var capability = _index.Require(execution.CapabilityId, "Capability");
            var provider = _index.Require(execution.ProviderId, "Entity");
            var binding = _index.Require(execution.RuntimeBindingId, "RuntimeBinding");
            var action = _index.Require(execution.RuntimeActionId, "RuntimeAction");

            if (_index.ScenarioOfStep(step.Id) != _context.ScenarioId)
                throw new FunctionalMldsV2FormatException("Execution step is outside RuntimeContext.scenarioId.");
            if (_index.StepOfCapabilityUse(use.Id) != step.Id)
                throw new FunctionalMldsV2FormatException("Execution CapabilityUse is not owned by the supplied ScenarioStep.");
            if (use.References("typeRef").Single() != capability.Id)
                throw new FunctionalMldsV2FormatException("Execution Capability does not match CapabilityUse.typeRef.");
            if (use.References("provider").Single() != provider.Id)
                throw new FunctionalMldsV2FormatException("Execution provider does not match CapabilityUse.provider.");
            if (!step.References("performedBy").Contains(provider.Id))
                throw new FunctionalMldsV2FormatException("Execution provider is not declared by ScenarioStep.performedBy.");
            if (!provider.References("providedCapability").Contains(capability.Id))
                throw new FunctionalMldsV2FormatException("Execution provider does not provide the supplied Capability.");

            var declaredTargets = new HashSet<string>(use.References("target"), StringComparer.Ordinal);
            var suppliedTargets = UniqueIds(execution.TargetIds, "target_ids", allowEmpty: true);
            foreach (var target in suppliedTargets)
                _index.Require(target);
            if (!declaredTargets.SetEquals(suppliedTargets))
                throw new FunctionalMldsV2FormatException("Execution target_ids must exactly match CapabilityUse.target.");
            if (binding.References("capability").Single() != capability.Id)
                throw new FunctionalMldsV2FormatException("Execution RuntimeBinding does not realize the supplied Capability.");
            if (!binding.References("runtimeAction").Contains(action.Id))
                throw new FunctionalMldsV2FormatException("Execution RuntimeAction is not owned by the supplied RuntimeBinding.");
        }

        private void ValidateTraceReferences(
            FunctionalMldsV2TraceReferences traceReferences,
            FunctionalMldsV2ExecutionReference execution)
        {
            if (traceReferences == null)
                throw new ArgumentNullException(nameof(traceReferences));
            RequireText(traceReferences.CaseId, "case_id");
            if (!string.IsNullOrWhiteSpace(_index.Document.CaseId) &&
                !string.Equals(traceReferences.CaseId, _index.Document.CaseId, StringComparison.Ordinal))
                throw new FunctionalMldsV2FormatException(
                    "case_id must exactly match the loaded V2 document.caseId.");

            var assertions = UniqueIds(traceReferences.AssertionIds, "assertion_ids", allowEmpty: false);
            foreach (var id in assertions)
                _index.Require(id, "Assertion");

            var validationCases = UniqueIds(traceReferences.ValidationCaseIds, "validation_case_ids", allowEmpty: true);
            foreach (var id in validationCases)
                _index.Require(id, "ValidationCase");

            var targets = UniqueIds(
                traceReferences.RuntimeValidationTargetIds,
                "runtime_validation_target_ids",
                allowEmpty: true);
            foreach (var id in targets)
            {
                var target = _index.Require(id, "RuntimeValidationTarget");
                if (!target.References("runtimeBinding").Contains(execution.RuntimeBindingId))
                    throw new FunctionalMldsV2FormatException(
                        $"RuntimeValidationTarget {id} does not contain RuntimeBinding {execution.RuntimeBindingId}.");
            }
        }

        private static HashSet<string> UniqueIds(IEnumerable<string> ids, string field, bool allowEmpty)
        {
            var values = ids == null ? new List<string>() : ids.ToList();
            if (!allowEmpty && values.Count == 0)
                throw new FunctionalMldsV2FormatException($"{field} requires at least one id.");
            var unique = new HashSet<string>(StringComparer.Ordinal);
            foreach (var id in values)
            {
                RequireText(id, field);
                if (!unique.Add(id))
                    throw new FunctionalMldsV2FormatException($"{field} contains duplicate id {id}.");
            }
            return unique;
        }

        private static List<string> Copy(IEnumerable<string> trace)
        {
            return (trace ?? Enumerable.Empty<string>()).ToList();
        }

        private static void RequireText(string value, string field)
        {
            if (string.IsNullOrWhiteSpace(value))
                throw new FunctionalMldsV2FormatException($"{field} is required.");
        }

        private static string Summary(object value)
        {
            var text = value == null
                ? string.Empty
                : value is string ? (string)value : JsonConvert.SerializeObject(value, Formatting.None);
            text = SecretToken.Replace(text, "[REDACTED]");
            text = SecretHeader.Replace(text, "[REDACTED]");
            text = Regex.Replace(text, @"\s+", " ").Trim();
            return text.Length <= 2000 ? text : text.Substring(0, 1985).TrimEnd() + " [TRUNCATED]";
        }

        private static JObject CleanMetadata(JObject metadata)
        {
            var output = new JObject();
            if (metadata == null)
                return output;
            foreach (var property in metadata.Properties())
            {
                var value = property.Value;
                if (value.Type != JTokenType.Null && value.Type != JTokenType.String &&
                    value.Type != JTokenType.Integer && value.Type != JTokenType.Float && value.Type != JTokenType.Boolean)
                    throw new FunctionalMldsV2FormatException($"Runtime metadata {property.Name} must be scalar or null.");
                output[property.Name] = value.Type == JTokenType.String
                    ? new JValue(Summary(value.Value<string>()))
                    : value.DeepClone();
            }
            return output;
        }
    }
}
