using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace FunctionalMlds.V2
{
    [Serializable]
    public sealed class FunctionalMldsV2ObservedValueRecord
    {
        [JsonProperty("type")]
        public string Type { get; set; }

        [JsonProperty("mixedStringContent", NullValueHandling = NullValueHandling.Ignore)]
        public string MixedStringContent { get; set; }

        [JsonProperty("value", NullValueHandling = NullValueHandling.Ignore)]
        public double? Value { get; set; }
    }

    [Serializable]
    public sealed class FunctionalMldsV2AssertionResultRecord
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("type")]
        public string Type { get; set; } = "AssertionResult";

        [JsonProperty("assertion")]
        public List<string> Assertion { get; set; } = new List<string>();

        [JsonProperty("verdict")]
        public string Verdict { get; set; }

        [JsonProperty("observedValue")]
        public FunctionalMldsV2ObservedValueRecord ObservedValue { get; set; }

        [JsonProperty("evidenceRef")]
        public string EvidenceRef { get; set; }

        [JsonProperty("timestamp")]
        public string Timestamp { get; set; }
    }

    [Serializable]
    public sealed class FunctionalMldsV2RuntimeActualOutcomeRecord
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("type")]
        public string Type { get; set; } = "RuntimeActualOutcome";

        [JsonProperty("result")]
        public List<FunctionalMldsV2AssertionResultRecord> Result { get; set; } =
            new List<FunctionalMldsV2AssertionResultRecord>();
    }

    [Serializable]
    public sealed class FunctionalMldsV2RuntimeValidationLogRecord
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("type")]
        public string Type { get; set; } = "RuntimeValidationLog";

        [JsonProperty("actualOutcome")]
        public List<string> ActualOutcome { get; set; } = new List<string>();
    }

    [Serializable]
    public sealed class FunctionalMldsV2ValidationArtifact
    {
        [JsonProperty("schema")]
        public string Schema { get; set; } = FunctionalMldsV2Lexemes.RuntimeValidationSchema;

        [JsonProperty("schema_version")]
        public string SchemaVersion { get; set; } = FunctionalMldsV2Lexemes.RuntimeSchemaVersion;

        [JsonProperty("model_version")]
        public string ModelVersion { get; set; }

        [JsonProperty("model_sha256")]
        public string ModelSha256 { get; set; }

        [JsonProperty("case_id")]
        public string CaseId { get; set; }

        [JsonProperty("session_id")]
        public string SessionId { get; set; }

        [JsonProperty("validation_case_ids")]
        public List<string> ValidationCaseIds { get; set; } = new List<string>();

        [JsonProperty("runtime_validation_target_ids")]
        public List<string> RuntimeValidationTargetIds { get; set; } = new List<string>();

        [JsonProperty("runtimeValidationLog")]
        public FunctionalMldsV2RuntimeValidationLogRecord RuntimeValidationLog { get; set; }

        [JsonProperty("runtimeActualOutcome")]
        public FunctionalMldsV2RuntimeActualOutcomeRecord RuntimeActualOutcome { get; set; }
    }

    /// <summary>
    /// Produces the exact runtime_validation_v2.schema.json envelope. Case, ValidationCase and
    /// RuntimeValidationTarget identifiers are caller-supplied and resolved without inference.
    /// </summary>
    public sealed class FunctionalMldsV2ValidationRecorder
    {
        private readonly FunctionalMldsV2LoadResult _loaded;

        public FunctionalMldsV2ValidationRecorder(FunctionalMldsV2LoadResult loaded)
        {
            _loaded = loaded ?? throw new ArgumentNullException(nameof(loaded));
        }

        public FunctionalMldsV2ValidationArtifact Record(
            string caseId,
            IEnumerable<string> validationCaseIds,
            IEnumerable<string> runtimeValidationTargetIds,
            IEnumerable<FunctionalMldsV2AssertionEvaluation> evaluations,
            string sessionId = null,
            string logId = null)
        {
            RequireText(caseId, "case_id");
            if (!string.IsNullOrWhiteSpace(_loaded.Document.CaseId) &&
                !string.Equals(caseId, _loaded.Document.CaseId, StringComparison.Ordinal))
                throw new FunctionalMldsV2FormatException(
                    "case_id must exactly match the loaded V2 document.caseId.");
            var caseIds = ValidateIds(validationCaseIds, "validation_case_ids", "ValidationCase");
            var targetIds = ValidateIds(
                runtimeValidationTargetIds,
                "runtime_validation_target_ids",
                "RuntimeValidationTarget");
            var results = (evaluations ?? Enumerable.Empty<FunctionalMldsV2AssertionEvaluation>()).ToList();
            if (results.Count == 0)
                throw new ArgumentException("At least one AssertionResult is required.", nameof(evaluations));

            var resultRecords = new List<FunctionalMldsV2AssertionResultRecord>();
            var seenResultIds = new HashSet<string>(StringComparer.Ordinal);
            foreach (var evaluation in results)
            {
                if (evaluation == null)
                    throw new FunctionalMldsV2FormatException("AssertionResult list contains null.");
                _loaded.Index.Require(evaluation.AssertionId, "Assertion");
                FunctionalMldsV2AssertionVerdict verdict;
                if (!FunctionalMldsV2Lexemes.TryVerdict(evaluation.Verdict, out verdict))
                    throw new FunctionalMldsV2FormatException($"Invalid AssertionResult verdict: {evaluation.Verdict}.");
                RequireText(evaluation.EvidenceRef, "AssertionResult.evidenceRef");

                var resultId = string.IsNullOrWhiteSpace(evaluation.Id)
                    ? "assertion-result-" + Guid.NewGuid().ToString("N")
                    : evaluation.Id.Trim();
                if (!seenResultIds.Add(resultId))
                    throw new FunctionalMldsV2FormatException($"Duplicate AssertionResult id: {resultId}.");
                var timestamp = string.IsNullOrWhiteSpace(evaluation.Timestamp)
                    ? DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ", CultureInfo.InvariantCulture)
                    : evaluation.Timestamp.Trim();
                DateTimeOffset parsedTimestamp;
                if (!DateTimeOffset.TryParse(
                    timestamp,
                    CultureInfo.InvariantCulture,
                    DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal,
                    out parsedTimestamp))
                    throw new FunctionalMldsV2FormatException($"AssertionResult {resultId} has an invalid timestamp.");

                var observed = evaluation.ObservedValue == null
                    ? JValue.CreateNull()
                    : evaluation.ObservedValue.DeepClone();
                resultRecords.Add(new FunctionalMldsV2AssertionResultRecord
                {
                    Id = resultId,
                    Assertion = new List<string> { evaluation.AssertionId },
                    Verdict = evaluation.Verdict,
                    ObservedValue = ObservedValue(observed),
                    EvidenceRef = evaluation.EvidenceRef.Trim(),
                    Timestamp = timestamp
                });
            }

            var actualLogId = string.IsNullOrWhiteSpace(logId)
                ? "runtime-validation-log-" + Guid.NewGuid().ToString("N")
                : logId.Trim();
            var actualOutcomeId = "runtime-actual-outcome-" + Guid.NewGuid().ToString("N");
            return new FunctionalMldsV2ValidationArtifact
            {
                ModelVersion = _loaded.Document.MetamodelVersion,
                ModelSha256 = _loaded.Sha256,
                CaseId = caseId.Trim(),
                SessionId = sessionId,
                ValidationCaseIds = caseIds,
                RuntimeValidationTargetIds = targetIds,
                RuntimeValidationLog = new FunctionalMldsV2RuntimeValidationLogRecord
                {
                    Id = actualLogId,
                    ActualOutcome = new List<string> { actualOutcomeId }
                },
                RuntimeActualOutcome = new FunctionalMldsV2RuntimeActualOutcomeRecord
                {
                    Id = actualOutcomeId,
                    Result = resultRecords
                }
            };
        }

        public void Write(string path, FunctionalMldsV2ValidationArtifact artifact)
        {
            if (artifact == null)
                throw new ArgumentNullException(nameof(artifact));
            var absolute = Path.GetFullPath(path);
            var directory = Path.GetDirectoryName(absolute);
            if (!string.IsNullOrEmpty(directory))
                Directory.CreateDirectory(directory);
            File.WriteAllText(absolute, JsonConvert.SerializeObject(artifact, Formatting.Indented));
        }

        private List<string> ValidateIds(IEnumerable<string> ids, string field, string expectedType)
        {
            var result = new List<string>();
            var seen = new HashSet<string>(StringComparer.Ordinal);
            foreach (var raw in ids ?? Enumerable.Empty<string>())
            {
                RequireText(raw, field);
                var id = raw.Trim();
                if (!seen.Add(id))
                    throw new FunctionalMldsV2FormatException($"{field} contains duplicate id {id}.");
                _loaded.Index.Require(id, expectedType);
                result.Add(id);
            }
            return result;
        }

        private static FunctionalMldsV2ObservedValueRecord ObservedValue(JToken value)
        {
            if (value != null && (value.Type == JTokenType.Integer || value.Type == JTokenType.Float))
            {
                return new FunctionalMldsV2ObservedValueRecord
                {
                    Type = "EANumericalValue",
                    Value = value.Value<double>()
                };
            }
            return new FunctionalMldsV2ObservedValueRecord
            {
                Type = "EAExpression",
                MixedStringContent = value == null || value.Type == JTokenType.Null
                    ? string.Empty
                    : value.Type == JTokenType.String
                        ? value.Value<string>()
                        : value.ToString(Formatting.None)
            };
        }

        private static void RequireText(string value, string field)
        {
            if (string.IsNullOrWhiteSpace(value))
                throw new FunctionalMldsV2FormatException($"{field} is required.");
        }
    }
}
