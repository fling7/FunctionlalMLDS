using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;

namespace FunctionalMlds.V2
{
    [Serializable]
    public sealed class FunctionalMldsV2RuntimeContext
    {
        [JsonProperty("documentId")]
        public string DocumentId { get; set; }

        [JsonProperty("metamodelVersion")]
        public string MetamodelVersion { get; set; }

        [JsonProperty("modelSha256")]
        public string ModelSha256 { get; set; }

        [JsonProperty("profile")]
        public string Profile { get; set; }

        [JsonProperty("scenarioId")]
        public string ScenarioId { get; set; }

        [JsonProperty("sessionId")]
        public string SessionId { get; set; }

        [JsonProperty("activeAgentId")]
        public string ActiveAgentId { get; set; }

        [JsonProperty("activeStepIds")]
        public List<string> ActiveStepIds { get; set; } = new List<string>();

        public static FunctionalMldsV2RuntimeContext Create(
            FunctionalMldsV2LoadResult loaded,
            string scenarioId,
            string sessionId = null)
        {
            if (loaded == null)
                throw new ArgumentNullException(nameof(loaded));
            loaded.Index.Require(scenarioId, "Scenario");
            return new FunctionalMldsV2RuntimeContext
            {
                DocumentId = loaded.Document.Id,
                MetamodelVersion = loaded.Document.MetamodelVersion,
                ModelSha256 = loaded.Sha256,
                Profile = loaded.Document.Profile,
                ScenarioId = scenarioId,
                SessionId = sessionId
            };
        }

        public void SetActiveSteps(IEnumerable<string> stepIds, FunctionalMldsV2ModelIndex index)
        {
            if (index == null)
                throw new ArgumentNullException(nameof(index));
            var unique = new List<string>();
            foreach (var id in stepIds ?? Enumerable.Empty<string>())
            {
                index.Require(id, "ScenarioStep");
                if (!unique.Contains(id))
                    unique.Add(id);
            }
            ActiveStepIds = unique;
        }
    }

    [Serializable]
    public sealed class FunctionalMldsV2ExecutionReference
    {
        [JsonProperty("scenarioStepId")]
        public string ScenarioStepId { get; set; }

        [JsonProperty("capabilityUseId")]
        public string CapabilityUseId { get; set; }

        [JsonProperty("capabilityId")]
        public string CapabilityId { get; set; }

        [JsonProperty("providerId")]
        public string ProviderId { get; set; }

        [JsonProperty("targetIds")]
        public List<string> TargetIds { get; set; } = new List<string>();

        [JsonProperty("runtimeBindingId")]
        public string RuntimeBindingId { get; set; }

        [JsonProperty("runtimeActionId")]
        public string RuntimeActionId { get; set; }
    }
}
