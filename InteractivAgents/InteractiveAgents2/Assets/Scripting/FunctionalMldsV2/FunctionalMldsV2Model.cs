using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace FunctionalMlds.V2
{
    [Serializable]
    public sealed class FunctionalMldsV2Document
    {
        [JsonProperty("schema", Required = Required.Always)]
        public string Schema { get; set; }

        [JsonProperty("id", Required = Required.Always)]
        public string Id { get; set; }

        [JsonProperty("metamodelVersion", Required = Required.Always)]
        public string MetamodelVersion { get; set; }

        [JsonProperty("serializationVersion")]
        public string SerializationVersion { get; set; }

        [JsonProperty("caseId")]
        public string CaseId { get; set; }

        [JsonProperty("profile", Required = Required.Always)]
        public string Profile { get; set; }

        [JsonProperty("fixture_profile")]
        public string FixtureProfile { get; set; }

        [JsonProperty("sourceContract")]
        public JObject SourceContract { get; set; }

        [JsonProperty("objects", Required = Required.Always)]
        public List<FunctionalMldsV2Object> Objects { get; set; } = new List<FunctionalMldsV2Object>();
    }

    /// <summary>
    /// Universal native-V2 object. Identity and metaclass are strongly typed; metaclass-specific
    /// properties remain JTokens so one loader can preserve the complete V2 surface without
    /// silently dropping fields it does not understand.
    /// </summary>
    [Serializable]
    public sealed class FunctionalMldsV2Object
    {
        [JsonProperty("id", Required = Required.Always)]
        public string Id { get; set; }

        [JsonProperty("type", Required = Required.Always)]
        public string Type { get; set; }

        [JsonExtensionData(ReadData = true, WriteData = true)]
        public IDictionary<string, JToken> Properties { get; set; } =
            new Dictionary<string, JToken>(StringComparer.Ordinal);

        public bool Has(string name)
        {
            return Properties != null && Properties.ContainsKey(name);
        }

        public JToken Token(string name)
        {
            JToken token;
            return Properties != null && Properties.TryGetValue(name, out token) ? token : null;
        }

        public string OptionalString(string name)
        {
            var token = Token(name);
            if (token == null || token.Type == JTokenType.Null)
                return null;
            if (token.Type != JTokenType.String)
                throw new FunctionalMldsV2FormatException($"{Id}.{name} must be a string.");
            var value = token.Value<string>();
            return string.IsNullOrWhiteSpace(value) ? null : value.Trim();
        }

        public string RequiredString(string name)
        {
            var value = OptionalString(name);
            if (string.IsNullOrWhiteSpace(value))
                throw new FunctionalMldsV2FormatException($"{Id}.{name} is required.");
            return value;
        }

        public bool? OptionalBoolean(string name)
        {
            var token = Token(name);
            if (token == null || token.Type == JTokenType.Null)
                return null;
            if (token.Type != JTokenType.Boolean)
                throw new FunctionalMldsV2FormatException($"{Id}.{name} must be Boolean.");
            return token.Value<bool>();
        }

        public double? OptionalNumber(string name)
        {
            var token = Token(name);
            if (token == null || token.Type == JTokenType.Null)
                return null;
            if (token.Type != JTokenType.Integer && token.Type != JTokenType.Float)
                throw new FunctionalMldsV2FormatException($"{Id}.{name} must be numeric.");
            return token.Value<double>();
        }

        public IReadOnlyList<string> References(string name)
        {
            var token = Token(name);
            if (token == null || token.Type == JTokenType.Null)
                return Array.Empty<string>();

            if (token.Type == JTokenType.String)
            {
                var one = token.Value<string>();
                if (string.IsNullOrWhiteSpace(one))
                    throw new FunctionalMldsV2FormatException($"{Id}.{name} contains an empty reference.");
                return new[] { one.Trim() };
            }

            var array = token as JArray;
            if (array == null)
                throw new FunctionalMldsV2FormatException($"{Id}.{name} must be a reference or reference array.");

            var result = new List<string>(array.Count);
            foreach (var item in array)
            {
                if (item.Type != JTokenType.String || string.IsNullOrWhiteSpace(item.Value<string>()))
                    throw new FunctionalMldsV2FormatException($"{Id}.{name} contains a non-string or empty reference.");
                result.Add(item.Value<string>().Trim());
            }
            return result;
        }

        public JToken ValueToken(string name)
        {
            var token = Token(name);
            return token == null || token.Type == JTokenType.Null ? null : token.DeepClone();
        }

        public override string ToString()
        {
            return $"{Type}({Id})";
        }
    }

    public sealed class FunctionalMldsV2FormatException : Exception
    {
        public FunctionalMldsV2FormatException(string message) : base(message) { }
        public FunctionalMldsV2FormatException(string message, Exception innerException) : base(message, innerException) { }
    }

    public sealed class FunctionalMldsV2ValidationException : Exception
    {
        public FunctionalMldsV2ValidationReport Report { get; }

        public FunctionalMldsV2ValidationException(FunctionalMldsV2ValidationReport report)
            : base(report == null ? "FunctionalMLDS V2 validation failed." : report.ToDisplayString())
        {
            Report = report;
        }
    }

    public enum FunctionalMldsV2AssertionVerdict
    {
        Pass,
        Fail,
        Inconclusive,
        Error
    }

    public static class FunctionalMldsV2Lexemes
    {
        public const string InstanceSchema = "dynamic_functional_mlds_v2_instance";
        public const string ModelVersion = "2.0.0-model";
        public const string ExecutableProfile = "executable";
        public const string RuntimeEventSchema = "functionalmlds_runtime_event";
        public const string RuntimeValidationSchema = "dynamic_functional_mlds_v2_runtime_validation";
        public const string RuntimeSchemaVersion = "2.0";

        public static string Verdict(FunctionalMldsV2AssertionVerdict verdict)
        {
            return verdict.ToString().ToLowerInvariant();
        }

        public static bool TryVerdict(string value, out FunctionalMldsV2AssertionVerdict verdict)
        {
            return Enum.TryParse(value, true, out verdict);
        }

        public static string InvariantNumber(double value)
        {
            return value.ToString("R", CultureInfo.InvariantCulture);
        }
    }
}
