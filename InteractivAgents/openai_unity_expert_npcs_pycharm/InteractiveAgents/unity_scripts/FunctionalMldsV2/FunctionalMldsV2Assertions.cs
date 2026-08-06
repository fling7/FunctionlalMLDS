using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.RegularExpressions;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace FunctionalMlds.V2
{
    public interface IFunctionalMldsV2AssertionProbe
    {
        bool TryObserve(
            FunctionalMldsV2Object assertion,
            FunctionalMldsV2Object subject,
            out JToken observedValue,
            out string evidenceRef);
    }

    public sealed class FunctionalMldsV2DictionaryAssertionProbe : IFunctionalMldsV2AssertionProbe
    {
        private readonly Dictionary<string, JToken> _values = new Dictionary<string, JToken>(StringComparer.Ordinal);
        private readonly Dictionary<string, string> _evidence = new Dictionary<string, string>(StringComparer.Ordinal);

        public void Set(string subjectId, JToken value, string evidenceRef = null)
        {
            if (string.IsNullOrWhiteSpace(subjectId))
                throw new ArgumentException("subjectId is required.", nameof(subjectId));
            _values[subjectId] = value == null ? JValue.CreateNull() : value.DeepClone();
            if (!string.IsNullOrWhiteSpace(evidenceRef))
                _evidence[subjectId] = evidenceRef;
        }

        public bool TryObserve(
            FunctionalMldsV2Object assertion,
            FunctionalMldsV2Object subject,
            out JToken observedValue,
            out string evidenceRef)
        {
            evidenceRef = null;
            if (subject == null || !_values.TryGetValue(subject.Id, out observedValue))
            {
                observedValue = null;
                return false;
            }
            observedValue = observedValue.DeepClone();
            _evidence.TryGetValue(subject.Id, out evidenceRef);
            return true;
        }
    }

    [Serializable]
    public sealed class FunctionalMldsV2AssertionEvaluation
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("assertionId")]
        public string AssertionId { get; set; }

        [JsonProperty("verdict")]
        public string Verdict { get; set; }

        [JsonProperty("observedValue")]
        public JToken ObservedValue { get; set; }

        [JsonProperty("evidenceRef")]
        public string EvidenceRef { get; set; }

        [JsonProperty("timestamp")]
        public string Timestamp { get; set; }

        [JsonProperty("message")]
        public string Message { get; set; }

        [JsonIgnore]
        public FunctionalMldsV2AssertionVerdict VerdictValue
        {
            get
            {
                FunctionalMldsV2AssertionVerdict value;
                return FunctionalMldsV2Lexemes.TryVerdict(Verdict, out value)
                    ? value
                    : FunctionalMldsV2AssertionVerdict.Error;
            }
        }
    }

    /// <summary>
    /// Shared evaluator for State-, Event-, Output-, Grounding- and RelationAssertion.
    /// Expressions are EAExpression objects with operator and optional expectedValue.
    /// </summary>
    public sealed class FunctionalMldsV2AssertionEvaluator
    {
        private readonly FunctionalMldsV2ModelIndex _index;
        private readonly IFunctionalMldsV2AssertionProbe _probe;

        public FunctionalMldsV2AssertionEvaluator(
            FunctionalMldsV2ModelIndex index,
            IFunctionalMldsV2AssertionProbe probe)
        {
            _index = index ?? throw new ArgumentNullException(nameof(index));
            _probe = probe ?? throw new ArgumentNullException(nameof(probe));
        }

        public FunctionalMldsV2AssertionEvaluation Evaluate(string assertionId)
        {
            var now = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ", CultureInfo.InvariantCulture);
            var evaluation = new FunctionalMldsV2AssertionEvaluation
            {
                Id = "assertion-result-" + Guid.NewGuid().ToString("N"),
                AssertionId = assertionId,
                Timestamp = now,
                EvidenceRef = "unity-assertion-evaluator://" + (assertionId ?? "missing-assertion-id")
            };
            try
            {
                var assertion = _index.Require(assertionId, "Assertion");
                var subject = _index.Require(assertion.References("subject").Single());
                var expression = _index.Require(assertion.References("expression").Single(), "EAExpression");
                JToken observed;
                string evidence;
                if (!_probe.TryObserve(assertion, subject, out observed, out evidence))
                {
                    evaluation.Verdict = FunctionalMldsV2Lexemes.Verdict(FunctionalMldsV2AssertionVerdict.Inconclusive);
                    evaluation.Message = $"No observation is available for subject {subject.Id}.";
                    return evaluation;
                }

                evaluation.ObservedValue = observed == null ? JValue.CreateNull() : observed.DeepClone();
                if (!string.IsNullOrWhiteSpace(evidence))
                    evaluation.EvidenceRef = evidence;
                var passed = EvaluateExpression(expression, observed);
                evaluation.Verdict = FunctionalMldsV2Lexemes.Verdict(
                    passed ? FunctionalMldsV2AssertionVerdict.Pass : FunctionalMldsV2AssertionVerdict.Fail);
                evaluation.Message = passed ? "Assertion satisfied." : "Assertion not satisfied.";
                return evaluation;
            }
            catch (Exception exception)
            {
                evaluation.Verdict = FunctionalMldsV2Lexemes.Verdict(FunctionalMldsV2AssertionVerdict.Error);
                evaluation.Message = exception.Message;
                return evaluation;
            }
        }

        private static bool EvaluateExpression(FunctionalMldsV2Object expression, JToken observed)
        {
            var operation = expression.RequiredString("operator");
            var expected = expression.ValueToken("expectedValue");
            switch (operation)
            {
                case "equals":
                    RequireExpected(expression, expected);
                    return JToken.DeepEquals(Normalize(observed), Normalize(expected));
                case "notEquals":
                    RequireExpected(expression, expected);
                    return !JToken.DeepEquals(Normalize(observed), Normalize(expected));
                case "contains":
                    RequireExpected(expression, expected);
                    return Contains(observed, expected);
                case "exists":
                    return observed != null && observed.Type != JTokenType.Null;
                case "truthy":
                    return Truthy(observed);
                case "greaterThan":
                    RequireExpected(expression, expected);
                    return Number(observed) > Number(expected);
                case "greaterThanOrEqual":
                    RequireExpected(expression, expected);
                    return Number(observed) >= Number(expected);
                case "lessThan":
                    RequireExpected(expression, expected);
                    return Number(observed) < Number(expected);
                case "lessThanOrEqual":
                    RequireExpected(expression, expected);
                    return Number(observed) <= Number(expected);
                case "matches":
                    RequireExpected(expression, expected);
                    return Regex.IsMatch(Text(observed), Text(expected), RegexOptions.CultureInvariant);
                default:
                    throw new FunctionalMldsV2FormatException(
                        $"Expression {expression.Id} uses unsupported operator '{operation}'.");
            }
        }

        private static void RequireExpected(FunctionalMldsV2Object expression, JToken expected)
        {
            if (expected == null)
                throw new FunctionalMldsV2FormatException($"Expression {expression.Id} requires expectedValue.");
        }

        private static JToken Normalize(JToken token)
        {
            return token == null ? JValue.CreateNull() : token;
        }

        private static bool Contains(JToken observed, JToken expected)
        {
            var array = observed as JArray;
            if (array != null)
                return array.Any(item => JToken.DeepEquals(Normalize(item), Normalize(expected)));
            return Text(observed).IndexOf(Text(expected), StringComparison.Ordinal) >= 0;
        }

        private static bool Truthy(JToken value)
        {
            if (value == null || value.Type == JTokenType.Null)
                return false;
            if (value.Type == JTokenType.Boolean)
                return value.Value<bool>();
            if (value.Type == JTokenType.Integer || value.Type == JTokenType.Float)
                return Math.Abs(value.Value<double>()) > double.Epsilon;
            if (value.Type == JTokenType.String)
                return !string.IsNullOrWhiteSpace(value.Value<string>());
            var array = value as JArray;
            if (array != null)
                return array.Count > 0;
            var obj = value as JObject;
            return obj != null && obj.Count > 0;
        }

        private static double Number(JToken value)
        {
            if (value != null && (value.Type == JTokenType.Integer || value.Type == JTokenType.Float))
                return value.Value<double>();
            throw new FunctionalMldsV2FormatException("Numeric assertion operator received a non-numeric value.");
        }

        private static string Text(JToken value)
        {
            if (value == null || value.Type == JTokenType.Null)
                return string.Empty;
            return value.Type == JTokenType.String ? value.Value<string>() : value.ToString(Formatting.None);
        }
    }
}
