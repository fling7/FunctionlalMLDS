using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;

namespace FunctionalMlds.V2
{
    /// <summary>
    /// Facts observed by QuickAgentManager during one interaction. Empty values mean that the
    /// corresponding observation has not happened yet; they never count as successful evidence.
    /// Agent identifiers may be native Entity ids or exact Entity.sourceId values.
    /// </summary>
    [Serializable]
    public sealed class FunctionalMldsV2InteractionObservation
    {
        [JsonProperty("interaction_mode")]
        public string InteractionMode { get; set; }

        [JsonProperty("model_sha256")]
        public string ModelSha256 { get; set; }

        [JsonProperty("binding_registry_valid")]
        public bool? BindingRegistryValid { get; set; }

        [JsonProperty("selection_observed")]
        public bool SelectionObserved { get; set; }

        [JsonProperty("selection_state")]
        public string SelectionState { get; set; }

        [JsonProperty("selected_entity_id")]
        public string SelectedEntityId { get; set; }

        [JsonProperty("selected_source_object_id")]
        public string SelectedSourceObjectId { get; set; }

        [JsonProperty("selected_object_group_ids")]
        public List<string> SelectedObjectGroupIds { get; set; } = new List<string>();

        [JsonProperty("selected_zone_ids")]
        public List<string> SelectedZoneIds { get; set; } = new List<string>();

        [JsonProperty("requested_agent_id")]
        public string RequestedAgentId { get; set; }

        [JsonProperty("routed_agent_id")]
        public string RoutedAgentId { get; set; }

        [JsonProperty("response_observed")]
        public bool ResponseObserved { get; set; }

        [JsonProperty("response_selected_entity_id")]
        public string ResponseSelectedEntityId { get; set; }

        [JsonProperty("response_grounded_entity_ids")]
        public List<string> ResponseGroundedEntityIds { get; set; } = new List<string>();

        [JsonProperty("handoff_observed")]
        public bool HandoffObserved { get; set; }

        [JsonProperty("handoff_from_agent_id")]
        public string HandoffFromAgentId { get; set; }

        [JsonProperty("handoff_to_agent_id")]
        public string HandoffToAgentId { get; set; }

        [JsonProperty("modeled_handoff")]
        public bool? ModeledHandoff { get; set; }

        [JsonProperty("capability_use_id")]
        public string CapabilityUseId { get; set; }

        [JsonProperty("capability_id")]
        public string CapabilityId { get; set; }

        [JsonProperty("runtime_binding_id")]
        public string RuntimeBindingId { get; set; }

        [JsonProperty("runtime_action_id")]
        public string RuntimeActionId { get; set; }
    }

    [Serializable]
    public sealed class FunctionalMldsV2InteractionProbeResult
    {
        [JsonProperty("probe")]
        public string Probe { get; set; }

        [JsonProperty("required")]
        public bool Required { get; set; }

        [JsonProperty("verdict")]
        public string Verdict { get; set; }

        [JsonProperty("message")]
        public string Message { get; set; }

        [JsonIgnore]
        public bool Passed =>
            string.Equals(Verdict, FunctionalMldsV2Lexemes.Verdict(FunctionalMldsV2AssertionVerdict.Pass),
                StringComparison.Ordinal);
    }

    [Serializable]
    public sealed class FunctionalMldsV2InteractionAssessment
    {
        [JsonProperty("verdict")]
        public string Verdict { get; set; }

        [JsonProperty("target_resolved")]
        public bool TargetResolved { get; set; }

        [JsonProperty("route_resolved")]
        public bool RouteResolved { get; set; }

        [JsonProperty("completion_satisfied")]
        public bool CompletionSatisfied { get; set; }

        [JsonProperty("scenario_step_completed")]
        public bool ScenarioStepCompleted { get; internal set; }

        [JsonProperty("runtime_event_id")]
        public string RuntimeEventId { get; internal set; }

        [JsonProperty("probes")]
        public List<FunctionalMldsV2InteractionProbeResult> Probes { get; set; } =
            new List<FunctionalMldsV2InteractionProbeResult>();

        public FunctionalMldsV2InteractionProbeResult Probe(string id)
        {
            return Probes.Single(item => string.Equals(item.Probe, id, StringComparison.Ordinal));
        }
    }

    /// <summary>
    /// Evaluates runtime observations against exact V2 identities and relations. The evaluator
    /// does not infer entities from labels and does not use utterance heuristics.
    /// </summary>
    public sealed class FunctionalMldsV2InteractionEvidenceEvaluator
    {
        public const string DeicticMode = "deictic";
        public const string NonDeicticMode = "non_deictic";
        public const string ResolvedSelectionState = "resolved";

        private readonly FunctionalMldsV2ModelIndex _index;
        private readonly string _modelSha256;

        public FunctionalMldsV2InteractionEvidenceEvaluator(
            FunctionalMldsV2ModelIndex index,
            string modelSha256)
        {
            _index = index ?? throw new ArgumentNullException(nameof(index));
            _modelSha256 = RequireText(modelSha256, nameof(modelSha256));
        }

        public FunctionalMldsV2InteractionAssessment Evaluate(
            FunctionalMldsV2ExecutionReference execution,
            FunctionalMldsV2InteractionObservation observation)
        {
            if (execution == null)
                throw new ArgumentNullException(nameof(execution));
            if (observation == null)
                throw new ArgumentNullException(nameof(observation));

            var result = new FunctionalMldsV2InteractionAssessment();
            var mode = Clean(observation.InteractionMode);
            var deictic = string.Equals(mode, DeicticMode, StringComparison.Ordinal);
            var nonDeictic = string.Equals(mode, NonDeicticMode, StringComparison.Ordinal);

            result.Probes.Add(InteractionModeProbe(observation, deictic, nonDeictic));
            result.Probes.Add(BindingProbe(observation, deictic, nonDeictic));
            result.Probes.Add(TargetProbe(observation, deictic));

            FunctionalMldsV2Object routedAgent;
            var routedAgentResolution = ResolveAgent(observation.RoutedAgentId, out routedAgent);
            result.Probes.Add(CapabilityProbe(execution, observation, routedAgent, routedAgentResolution));
            result.Probes.Add(ResponsibilityProbe(observation, deictic, routedAgent, routedAgentResolution));
            result.Probes.Add(ResponseObservedProbe(observation));
            result.Probes.Add(ResponseEntityProbe(observation, deictic));
            result.Probes.Add(HandoffPermissionProbe(observation));

            result.TargetResolved = !deictic
                || (result.Probe("model_binding").Passed
                    && result.Probe("target_resolution").Passed);
            result.RouteResolved = result.Probe("entity_capability_agreement").Passed
                && (!deictic || result.Probe("agent_responsibility").Passed);

            var required = result.Probes.Where(item => item.Required).ToList();
            if (required.Any(item => string.Equals(
                    item.Verdict,
                    FunctionalMldsV2Lexemes.Verdict(FunctionalMldsV2AssertionVerdict.Error),
                    StringComparison.Ordinal)))
            {
                result.Verdict = FunctionalMldsV2Lexemes.Verdict(FunctionalMldsV2AssertionVerdict.Error);
            }
            else if (required.Any(item => string.Equals(
                         item.Verdict,
                         FunctionalMldsV2Lexemes.Verdict(FunctionalMldsV2AssertionVerdict.Fail),
                         StringComparison.Ordinal)))
            {
                result.Verdict = FunctionalMldsV2Lexemes.Verdict(FunctionalMldsV2AssertionVerdict.Fail);
            }
            else if (required.All(item => item.Passed))
            {
                result.Verdict = FunctionalMldsV2Lexemes.Verdict(FunctionalMldsV2AssertionVerdict.Pass);
            }
            else
            {
                result.Verdict = FunctionalMldsV2Lexemes.Verdict(FunctionalMldsV2AssertionVerdict.Inconclusive);
            }

            result.CompletionSatisfied = result.TargetResolved
                && result.RouteResolved
                && result.Probe("response_observed").Passed
                && string.Equals(
                    result.Verdict,
                    FunctionalMldsV2Lexemes.Verdict(FunctionalMldsV2AssertionVerdict.Pass),
                    StringComparison.Ordinal);
            return result;
        }

        private FunctionalMldsV2InteractionProbeResult InteractionModeProbe(
            FunctionalMldsV2InteractionObservation observation,
            bool deictic,
            bool nonDeictic)
        {
            if (!deictic && !nonDeictic)
                return Fail("interaction_mode_contract", true, "interaction_mode must be deictic or non_deictic.");
            if (deictic && !observation.SelectionObserved)
                return Inconclusive(
                    "interaction_mode_contract",
                    true,
                    "A deictic request has no target-selection observation.");
            if (nonDeictic && (observation.SelectionObserved
                               || HasText(observation.SelectedEntityId)
                               || HasText(observation.SelectedSourceObjectId)
                               || HasText(observation.ResponseSelectedEntityId)
                               || ExactIds(observation.ResponseGroundedEntityIds).Count > 0))
            {
                return Fail(
                    "interaction_mode_contract",
                    true,
                    "A non_deictic interaction contains spatial grounding evidence.");
            }
            return Pass("interaction_mode_contract", true, "The explicit interaction mode matches the observation.");
        }

        private FunctionalMldsV2InteractionProbeResult BindingProbe(
            FunctionalMldsV2InteractionObservation observation,
            bool deictic,
            bool nonDeictic)
        {
            if (!HasText(observation.ModelSha256))
                return Inconclusive("model_binding", true, "No observed model hash is available.");
            if (!string.Equals(observation.ModelSha256.Trim(), _modelSha256, StringComparison.OrdinalIgnoreCase))
                return Fail("model_binding", true, "The observation references a different V2 model hash.");
            if (!deictic)
            {
                return nonDeictic
                    ? Pass("model_binding", true, "The request is bound to the loaded V2 model hash.")
                    : Inconclusive("model_binding", true, "The interaction mode is unavailable.");
            }
            if (!observation.BindingRegistryValid.HasValue)
                return Inconclusive("model_binding", true, "The scene-binding registry was not observed.");
            if (!observation.BindingRegistryValid.Value)
                return Fail("model_binding", true, "The scene-binding registry is invalid.");
            if (!HasText(observation.SelectedEntityId) || !HasText(observation.SelectedSourceObjectId))
                return Inconclusive("model_binding", true, "The selected entity/source binding is incomplete.");

            FunctionalMldsV2Object entity;
            try
            {
                entity = _index.Require(observation.SelectedEntityId.Trim(), "Entity");
            }
            catch (Exception exception)
            {
                return Fail("model_binding", true, "The selected entity is not in the loaded model: " + exception.Message);
            }
            var sourceId = entity.OptionalString("sourceId");
            if (!string.Equals(sourceId, observation.SelectedSourceObjectId.Trim(), StringComparison.Ordinal))
            {
                return Fail(
                    "model_binding",
                    true,
                    "The observed scene-object id differs from Entity.sourceId.");
            }
            return Pass("model_binding", true, "The selected Unity object resolves to one exact V2 Entity.");
        }

        private static FunctionalMldsV2InteractionProbeResult TargetProbe(
            FunctionalMldsV2InteractionObservation observation,
            bool deictic)
        {
            if (!deictic)
                return Inconclusive("target_resolution", false, "No spatial target is required for non_deictic mode.");
            if (!observation.SelectionObserved)
                return Inconclusive("target_resolution", true, "No target-selection observation is available.");
            if (!string.Equals(
                    Clean(observation.SelectionState),
                    ResolvedSelectionState,
                    StringComparison.Ordinal))
            {
                return Fail("target_resolution", true, "The observed target-selection state is not resolved.");
            }
            if (!HasText(observation.SelectedEntityId) || !HasText(observation.SelectedSourceObjectId))
                return Fail("target_resolution", true, "A resolved target lacks its entity or source-object id.");
            return Pass("target_resolution", true, "The deictic target is explicitly resolved.");
        }

        private FunctionalMldsV2InteractionProbeResult CapabilityProbe(
            FunctionalMldsV2ExecutionReference execution,
            FunctionalMldsV2InteractionObservation observation,
            FunctionalMldsV2Object routedAgent,
            string routedAgentResolution)
        {
            if (!HasText(observation.RoutedAgentId))
            {
                return observation.ResponseObserved
                    ? Fail("entity_capability_agreement", true, "The observed response omitted its routing decision.")
                    : Inconclusive("entity_capability_agreement", true, "No routing observation is available.");
            }
            if (routedAgent == null)
                return Fail("entity_capability_agreement", true, routedAgentResolution);
            if (!routedAgent.References("providedCapability").Contains(execution.CapabilityId))
            {
                return Fail(
                    "entity_capability_agreement",
                    true,
                    $"Routed agent {routedAgent.Id} does not provide capability {execution.CapabilityId}.");
            }
            return Pass(
                "entity_capability_agreement",
                true,
                "The routed agent provides the exact modeled capability used by this runtime action.");
        }

        private FunctionalMldsV2InteractionProbeResult ResponsibilityProbe(
            FunctionalMldsV2InteractionObservation observation,
            bool deictic,
            FunctionalMldsV2Object routedAgent,
            string routedAgentResolution)
        {
            if (!deictic)
                return Inconclusive("agent_responsibility", false, "No spatial responsibility is required.");
            if (!HasText(observation.RoutedAgentId))
            {
                return observation.ResponseObserved
                    ? Fail("agent_responsibility", true, "The observed response omitted its routing decision.")
                    : Inconclusive("agent_responsibility", true, "No routing observation is available.");
            }
            if (!HasText(observation.SelectedEntityId))
                return Inconclusive("agent_responsibility", true, "No target entity observation is available.");
            if (routedAgent == null)
                return Fail("agent_responsibility", true, routedAgentResolution);

            var selectedEntity = _index.Require(observation.SelectedEntityId.Trim(), "Entity");
            if (routedAgent.References("groundedAsset").Contains(selectedEntity.Id))
            {
                return Pass("agent_responsibility", true, "The routed agent is directly responsible for the target asset.");
            }

            var observedGroups = ExactIds(observation.SelectedObjectGroupIds);
            foreach (var id in selectedEntity.References("objectGroup"))
                observedGroups.Add(id);
            if (routedAgent.References("groundedObjectGroup").Any(observedGroups.Contains))
            {
                return Pass(
                    "agent_responsibility",
                    true,
                    "The routed agent is responsible for the target's modeled object group.");
            }

            var observedZones = ExactIds(observation.SelectedZoneIds);
            foreach (var id in selectedEntity.References("zone"))
                observedZones.Add(id);
            if (routedAgent.References("responsibleZone").Any(observedZones.Contains))
            {
                return Pass(
                    "agent_responsibility",
                    true,
                    "The routed agent is responsible for the target's modeled zone.");
            }
            return Fail(
                "agent_responsibility",
                true,
                $"Routed agent {routedAgent.Id} has no modeled responsibility for {selectedEntity.Id}.");
        }

        private static FunctionalMldsV2InteractionProbeResult ResponseObservedProbe(
            FunctionalMldsV2InteractionObservation observation)
        {
            return observation.ResponseObserved
                ? Pass("response_observed", true, "A backend response was parsed and observed.")
                : Inconclusive("response_observed", true, "No backend response observation is available.");
        }

        private static FunctionalMldsV2InteractionProbeResult ResponseEntityProbe(
            FunctionalMldsV2InteractionObservation observation,
            bool deictic)
        {
            if (!deictic)
                return Inconclusive("response_entity", false, "No grounded response entity is required.");
            if (!observation.ResponseObserved)
                return Inconclusive("response_entity", true, "No backend response observation is available.");
            if (!HasText(observation.ResponseSelectedEntityId))
                return Fail("response_entity", true, "The observed response omitted its selected entity.");
            if (!string.Equals(
                    observation.ResponseSelectedEntityId.Trim(),
                    Clean(observation.SelectedEntityId),
                    StringComparison.Ordinal))
            {
                return Fail("response_entity", true, "The response selected a different entity.");
            }
            var grounded = ExactIds(observation.ResponseGroundedEntityIds);
            if (!grounded.Contains(Clean(observation.SelectedEntityId)))
                return Fail("response_entity", true, "The response grounding set omits the selected entity.");
            return Pass("response_entity", true, "The response preserves the exact selected entity.");
        }

        private FunctionalMldsV2InteractionProbeResult HandoffPermissionProbe(
            FunctionalMldsV2InteractionObservation observation)
        {
            if (!observation.HandoffObserved)
                return Inconclusive("handoff_permission", false, "No handoff was observed in this response.");
            if (!HasText(observation.HandoffFromAgentId) || !HasText(observation.HandoffToAgentId))
                return Fail("handoff_permission", true, "The observed handoff lacks a source or target agent.");

            FunctionalMldsV2Object source;
            FunctionalMldsV2Object target;
            var sourceResolution = ResolveAgent(observation.HandoffFromAgentId, out source);
            var targetResolution = ResolveAgent(observation.HandoffToAgentId, out target);
            if (source == null)
                return Fail("handoff_permission", true, sourceResolution);
            if (target == null)
                return Fail("handoff_permission", true, targetResolution);
            if (!observation.ModeledHandoff.HasValue)
                return Inconclusive("handoff_permission", true, "The response omitted modeled_handoff evidence.");
            if (!observation.ModeledHandoff.Value)
                return Fail("handoff_permission", true, "The backend marked the handoff as unmodeled.");
            if (!source.References("handoffTarget").Contains(target.Id))
            {
                return Fail(
                    "handoff_permission",
                    true,
                    $"Agent {source.Id} has no modeled handoff permission to {target.Id}.");
            }
            return Pass("handoff_permission", true, "The observed handoff follows an exact modeled permission.");
        }

        private string ResolveAgent(string observedId, out FunctionalMldsV2Object agent)
        {
            agent = null;
            var clean = Clean(observedId);
            if (string.IsNullOrEmpty(clean))
                return "Agent observation is missing.";

            var matches = _index.OfType("Entity")
                .Where(item => string.Equals(item.Type, "Agent", StringComparison.Ordinal)
                               || string.Equals(item.OptionalString("kind"), "agent", StringComparison.Ordinal))
                .Where(item => string.Equals(item.Id, clean, StringComparison.Ordinal)
                               || string.Equals(item.OptionalString("sourceId"), clean, StringComparison.Ordinal)
                               || string.Equals(item.OptionalString("sourceAgentId"), clean, StringComparison.Ordinal))
                .ToList();
            if (matches.Count != 1)
                return $"Agent id '{clean}' resolves to {matches.Count} V2 entities.";
            agent = matches[0];
            return null;
        }

        private static HashSet<string> ExactIds(IEnumerable<string> values)
        {
            return new HashSet<string>(
                (values ?? Enumerable.Empty<string>())
                    .Select(Clean)
                    .Where(value => !string.IsNullOrEmpty(value)),
                StringComparer.Ordinal);
        }

        private static FunctionalMldsV2InteractionProbeResult Pass(
            string probe,
            bool required,
            string message)
        {
            return Result(probe, required, FunctionalMldsV2AssertionVerdict.Pass, message);
        }

        private static FunctionalMldsV2InteractionProbeResult Fail(
            string probe,
            bool required,
            string message)
        {
            return Result(probe, required, FunctionalMldsV2AssertionVerdict.Fail, message);
        }

        private static FunctionalMldsV2InteractionProbeResult Inconclusive(
            string probe,
            bool required,
            string message)
        {
            return Result(probe, required, FunctionalMldsV2AssertionVerdict.Inconclusive, message);
        }

        private static FunctionalMldsV2InteractionProbeResult Result(
            string probe,
            bool required,
            FunctionalMldsV2AssertionVerdict verdict,
            string message)
        {
            return new FunctionalMldsV2InteractionProbeResult
            {
                Probe = probe,
                Required = required,
                Verdict = FunctionalMldsV2Lexemes.Verdict(verdict),
                Message = message
            };
        }

        private static string RequireText(string value, string name)
        {
            if (string.IsNullOrWhiteSpace(value))
                throw new ArgumentException(name + " is required.", name);
            return value.Trim();
        }

        private static bool HasText(string value)
        {
            return !string.IsNullOrWhiteSpace(value);
        }

        private static string Clean(string value)
        {
            return string.IsNullOrWhiteSpace(value) ? string.Empty : value.Trim();
        }
    }
}
