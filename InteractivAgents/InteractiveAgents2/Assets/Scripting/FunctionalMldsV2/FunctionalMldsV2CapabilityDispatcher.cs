using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;

namespace FunctionalMlds.V2
{
    public interface IFunctionalMldsV2RuntimeActionExecutor
    {
        FunctionalMldsV2RuntimeActionResult Execute(
            FunctionalMldsV2Object action,
            FunctionalMldsV2Object locator,
            FunctionalMldsV2ExecutionReference execution,
            JObject parameters,
            FunctionalMldsV2RuntimeContext runtimeContext);
    }

    public sealed class FunctionalMldsV2DispatchRequest
    {
        public string CapabilityUseId { get; set; }
        public string RuntimeBindingId { get; set; }
        public JObject Parameters { get; set; } = new JObject();
    }

    public sealed class FunctionalMldsV2RuntimeActionResult
    {
        public string RuntimeActionId { get; set; }
        public bool Success { get; set; }
        public string OutputSummary { get; set; }
        public string EvidenceRef { get; set; }
        public JToken ObservedValue { get; set; }
    }

    public sealed class FunctionalMldsV2DispatchResult
    {
        public FunctionalMldsV2ExecutionReference Execution { get; internal set; }
        public IReadOnlyList<FunctionalMldsV2RuntimeActionResult> ActionResults { get; internal set; }
        public bool Success => ActionResults != null && ActionResults.All(item => item.Success);
    }

    /// <summary>
    /// Resolves and dispatches only the normative chain
    /// ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> ordered RuntimeAction.
    /// </summary>
    public sealed class FunctionalMldsV2CapabilityDispatcher
    {
        private readonly FunctionalMldsV2ModelIndex _index;
        private readonly FunctionalMldsV2RuntimeContext _context;
        private readonly IFunctionalMldsV2RuntimeActionExecutor _executor;

        public FunctionalMldsV2CapabilityDispatcher(
            FunctionalMldsV2ModelIndex index,
            FunctionalMldsV2RuntimeContext context,
            IFunctionalMldsV2RuntimeActionExecutor executor)
        {
            _index = index ?? throw new ArgumentNullException(nameof(index));
            _context = context ?? throw new ArgumentNullException(nameof(context));
            _executor = executor ?? throw new ArgumentNullException(nameof(executor));
        }

        public FunctionalMldsV2DispatchResult Dispatch(FunctionalMldsV2DispatchRequest request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.CapabilityUseId))
                throw new ArgumentException("CapabilityUseId is required.", nameof(request));

            var use = _index.Require(request.CapabilityUseId, "CapabilityUse");
            var stepId = _index.StepOfCapabilityUse(use.Id);
            if (stepId == null)
                throw new FunctionalMldsV2FormatException($"CapabilityUse {use.Id} has no owning ScenarioStep.");
            if (!_context.ActiveStepIds.Contains(stepId))
                throw new InvalidOperationException($"CapabilityUse {use.Id} belongs to inactive ScenarioStep {stepId}.");

            var capabilityId = use.References("typeRef").Single();
            var providerId = use.References("provider").Single();
            var targetIds = use.References("target").ToList();
            var capability = _index.Require(capabilityId, "Capability");
            var provider = _index.Require(providerId, "Entity");
            var step = _index.Require(stepId, "ScenarioStep");

            if (!step.References("performedBy").Contains(providerId))
                throw new FunctionalMldsV2FormatException($"Provider {providerId} is not a performer of {stepId}.");
            if (!provider.References("providedCapability").Contains(capability.Id))
                throw new FunctionalMldsV2FormatException($"Provider {providerId} does not provide {capability.Id}.");
            foreach (var targetId in targetIds)
                _index.Require(targetId);

            var bindings = _index.OfType("RuntimeBinding")
                .Where(binding => binding.References("capability").SingleOrDefault() == capability.Id)
                .ToList();
            FunctionalMldsV2Object selected;
            if (!string.IsNullOrWhiteSpace(request.RuntimeBindingId))
            {
                selected = _index.Require(request.RuntimeBindingId, "RuntimeBinding");
                if (!bindings.Contains(selected))
                    throw new FunctionalMldsV2FormatException(
                        $"RuntimeBinding {selected.Id} does not realize Capability {capability.Id}.");
            }
            else
            {
                if (bindings.Count != 1)
                    throw new FunctionalMldsV2FormatException(
                        $"Capability {capability.Id} has {bindings.Count} RuntimeBindings; an exact binding selection is required.");
                selected = bindings[0];
            }

            var baseExecution = new FunctionalMldsV2ExecutionReference
            {
                ScenarioStepId = stepId,
                CapabilityUseId = use.Id,
                CapabilityId = capability.Id,
                ProviderId = provider.Id,
                TargetIds = targetIds,
                RuntimeBindingId = selected.Id
            };

            var actionResults = new List<FunctionalMldsV2RuntimeActionResult>();
            foreach (var actionId in selected.References("runtimeAction"))
            {
                var action = _index.Require(actionId, "RuntimeAction");
                var locator = _index.Require(action.References("locator").Single(), "RuntimeActionLocator");
                var execution = CloneExecution(baseExecution, action.Id);
                var result = _executor.Execute(
                    action,
                    locator,
                    execution,
                    request.Parameters == null ? new JObject() : (JObject)request.Parameters.DeepClone(),
                    _context);
                if (result == null)
                    throw new InvalidOperationException($"Runtime executor returned null for {action.Id}.");
                result.RuntimeActionId = action.Id;
                actionResults.Add(result);
                if (!result.Success)
                    break;
            }

            var finalExecution = CloneExecution(baseExecution, actionResults.LastOrDefault()?.RuntimeActionId);
            return new FunctionalMldsV2DispatchResult
            {
                Execution = finalExecution,
                ActionResults = actionResults.AsReadOnly()
            };
        }

        private static FunctionalMldsV2ExecutionReference CloneExecution(
            FunctionalMldsV2ExecutionReference source,
            string runtimeActionId)
        {
            return new FunctionalMldsV2ExecutionReference
            {
                ScenarioStepId = source.ScenarioStepId,
                CapabilityUseId = source.CapabilityUseId,
                CapabilityId = source.CapabilityId,
                ProviderId = source.ProviderId,
                TargetIds = new List<string>(source.TargetIds ?? new List<string>()),
                RuntimeBindingId = source.RuntimeBindingId,
                RuntimeActionId = runtimeActionId
            };
        }
    }
}
