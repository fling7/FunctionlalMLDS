using System;
using System.Collections.Generic;
using System.Linq;

namespace FunctionalMlds.V2
{
    public interface IFunctionalMldsV2GuardEvaluator
    {
        bool Evaluate(FunctionalMldsV2Object condition, FunctionalMldsV2RuntimeContext context);
    }

    public sealed class FunctionalMldsV2BooleanGuardEvaluator : IFunctionalMldsV2GuardEvaluator
    {
        public bool Evaluate(FunctionalMldsV2Object condition, FunctionalMldsV2RuntimeContext context)
        {
            if (condition == null)
                throw new ArgumentNullException(nameof(condition));
            var value = condition.OptionalBoolean("value");
            if (!value.HasValue)
                throw new FunctionalMldsV2FormatException(
                    $"Guard {condition.Id} has no runtime Boolean value; execution is fail-closed.");
            return value.Value;
        }
    }

    public sealed class FunctionalMldsV2AdvanceRequest
    {
        public bool ExceptionRaised { get; set; }
        public bool AllowLoop { get; set; }
    }

    public sealed class FunctionalMldsV2Transition
    {
        public string CompletedStepId { get; internal set; }
        public IReadOnlyList<string> RelationIds { get; internal set; } = Array.Empty<string>();
        public IReadOnlyList<string> ActivatedStepIds { get; internal set; } = Array.Empty<string>();
        public bool IsTerminal => ActivatedStepIds.Count == 0;
    }

    /// <summary>
    /// Executes a single Scenario using StepRelation only. Scenario.step order and stepNumber are
    /// never inspected for transition decisions.
    /// </summary>
    public sealed class FunctionalMldsV2ScenarioRunner
    {
        private readonly FunctionalMldsV2ModelIndex _index;
        private readonly FunctionalMldsV2Object _scenario;
        private readonly FunctionalMldsV2RuntimeContext _context;
        private readonly IFunctionalMldsV2GuardEvaluator _guards;
        private readonly Func<double> _random;
        private readonly List<FunctionalMldsV2Object> _relations;
        private readonly HashSet<string> _scenarioSteps;
        private readonly HashSet<string> _active = new HashSet<string>(StringComparer.Ordinal);
        private readonly HashSet<string> _completed = new HashSet<string>(StringComparer.Ordinal);

        public IReadOnlyCollection<string> ActiveStepIds => _active;
        public IReadOnlyCollection<string> CompletedStepIds => _completed;

        public FunctionalMldsV2ScenarioRunner(
            FunctionalMldsV2ModelIndex index,
            FunctionalMldsV2RuntimeContext context,
            IFunctionalMldsV2GuardEvaluator guards = null,
            Func<double> random = null)
        {
            _index = index ?? throw new ArgumentNullException(nameof(index));
            _context = context ?? throw new ArgumentNullException(nameof(context));
            _scenario = index.Require(context.ScenarioId, "Scenario");
            _guards = guards ?? new FunctionalMldsV2BooleanGuardEvaluator();
            _random = random ?? (() => UnityEngine.Random.value);
            _scenarioSteps = new HashSet<string>(_scenario.References("step"), StringComparer.Ordinal);
            _relations = _scenario.References("stepRelation").Select(id => index.Require(id, "StepRelation")).ToList();
        }

        public IReadOnlyList<string> Start()
        {
            if (_active.Count != 0 || _completed.Count != 0)
                throw new InvalidOperationException("ScenarioRunner has already started.");

            var targets = new HashSet<string>(
                _relations
                    .Where(relation => relation.OptionalString("kind") != "loop")
                    .SelectMany(relation => relation.References("targetStep")),
                StringComparer.Ordinal);
            var entries = _scenarioSteps.Where(step => !targets.Contains(step)).OrderBy(id => id, StringComparer.Ordinal).ToList();
            if (entries.Count != 1)
                throw new FunctionalMldsV2FormatException(
                    $"Scenario {_scenario.Id} needs exactly one entry step derived from StepRelations, got {entries.Count}.");
            Activate(entries);
            return entries;
        }

        /// <summary>
        /// Synchronizes the runner with an externally observed runtime step without claiming
        /// that skipped build-time predecessors were executed by this Unity session. This is
        /// used when Unity joins a scenario after the offline materialization steps.
        /// </summary>
        public void SynchronizeExternallyObservedStep(string stepId)
        {
            if (string.IsNullOrWhiteSpace(stepId) || !_scenarioSteps.Contains(stepId))
                throw new FunctionalMldsV2FormatException(
                    $"Cannot observe ScenarioStep {stepId ?? "<null>"} outside Scenario {_scenario.Id}.");
            _active.Clear();
            _active.Add(stepId);
            _completed.Remove(stepId);
            _context.SetActiveSteps(_active, _index);
        }

        /// <summary>
        /// Completes a runtime step only after both target resolution and route resolution have
        /// been established by real observations. A false evidence flag leaves runner state
        /// unchanged and therefore fails closed.
        /// </summary>
        public bool TryCompleteEvidenceBoundStep(
            string stepId,
            bool targetResolved,
            bool routeResolved,
            out FunctionalMldsV2Transition transition,
            FunctionalMldsV2AdvanceRequest request = null)
        {
            transition = null;
            if (!targetResolved || !routeResolved)
                return false;
            transition = CompleteAndAdvance(stepId, request);
            return true;
        }

        public FunctionalMldsV2Transition CompleteAndAdvance(
            string stepId,
            FunctionalMldsV2AdvanceRequest request = null)
        {
            request = request ?? new FunctionalMldsV2AdvanceRequest();
            if (!_active.Contains(stepId))
                throw new InvalidOperationException($"ScenarioStep {stepId} is not active.");
            _active.Remove(stepId);
            _completed.Add(stepId);

            var eligible = Outgoing(stepId).Where(relation => GuardAllows(relation)).ToList();
            var selected = SelectRelations(eligible, request);
            var activated = new List<string>();
            foreach (var relation in selected)
            {
                var target = relation.References("targetStep").Single();
                if (relation.OptionalString("kind") == "join" && !JoinReady(target))
                    continue;
                if (!activated.Contains(target))
                    activated.Add(target);
            }
            Activate(activated);
            return new FunctionalMldsV2Transition
            {
                CompletedStepId = stepId,
                RelationIds = selected.Select(relation => relation.Id).ToList().AsReadOnly(),
                ActivatedStepIds = activated.AsReadOnly()
            };
        }

        private IEnumerable<FunctionalMldsV2Object> Outgoing(string stepId)
        {
            return _relations.Where(relation => relation.References("sourceStep").Single() == stepId);
        }

        private bool GuardAllows(FunctionalMldsV2Object relation)
        {
            var guardId = relation.References("guard").SingleOrDefault();
            return guardId == null || _guards.Evaluate(_index.Require(guardId, "ScenarioCondition"), _context);
        }

        private List<FunctionalMldsV2Object> SelectRelations(
            List<FunctionalMldsV2Object> eligible,
            FunctionalMldsV2AdvanceRequest request)
        {
            if (eligible.Count == 0)
                return new List<FunctionalMldsV2Object>();

            var exceptions = eligible.Where(item => item.OptionalString("kind") == "exception").ToList();
            if (request.ExceptionRaised)
            {
                if (exceptions.Count == 0)
                    throw new FunctionalMldsV2FormatException("An exception was raised but no eligible exception StepRelation exists.");
                return new List<FunctionalMldsV2Object> { ChooseBranch(exceptions) };
            }
            eligible = eligible.Where(item => item.OptionalString("kind") != "exception").ToList();

            var forks = eligible.Where(item => item.OptionalString("kind") == "fork").ToList();
            if (forks.Count > 0)
                return forks;

            var joins = eligible.Where(item => item.OptionalString("kind") == "join").ToList();
            if (joins.Count > 0)
                return joins;

            var branches = eligible.Where(item => item.OptionalString("kind") == "alternative").ToList();
            if (branches.Count > 0)
                return new List<FunctionalMldsV2Object> { ChooseBranch(branches) };

            var sequences = eligible.Where(item => item.OptionalString("kind") == "sequence").ToList();
            if (sequences.Count > 1)
                throw new FunctionalMldsV2FormatException("Ambiguous sequence: use fork or alternative StepRelations.");
            if (sequences.Count == 1)
                return sequences;

            var loops = eligible.Where(item => item.OptionalString("kind") == "loop").ToList();
            if (!request.AllowLoop)
                return new List<FunctionalMldsV2Object>();
            if (loops.Count > 1)
                throw new FunctionalMldsV2FormatException("Ambiguous loop StepRelations.");
            return loops;
        }

        private FunctionalMldsV2Object ChooseBranch(IReadOnlyList<FunctionalMldsV2Object> branches)
        {
            if (branches.Count == 1)
                return branches[0];
            var probabilities = branches.Select(Probability).ToList();
            if (probabilities.Any(value => !value.HasValue))
                throw new FunctionalMldsV2FormatException("Multiple eligible branches require complete probabilities.");
            var sum = probabilities.Sum(value => value.Value);
            if (sum <= 0)
                throw new FunctionalMldsV2FormatException("Branch probability sum must be positive.");
            var sample = Math.Max(0.0, Math.Min(0.999999999, _random())) * sum;
            var accumulated = 0.0;
            for (var index = 0; index < branches.Count; index++)
            {
                accumulated += probabilities[index].Value;
                if (sample < accumulated)
                    return branches[index];
            }
            return branches[branches.Count - 1];
        }

        private double? Probability(FunctionalMldsV2Object relation)
        {
            var probabilityId = relation.References("probability").SingleOrDefault();
            if (probabilityId == null)
                return null;
            var probability = _index.Require(probabilityId, "ProbabilityValue");
            var value = probability.OptionalNumber("value");
            if (!value.HasValue || value.Value < 0 || value.Value > 1)
                throw new FunctionalMldsV2FormatException(
                    $"ProbabilityValue {probability.Id} must contain a value in [0,1].");
            return value.Value;
        }

        private bool JoinReady(string target)
        {
            var requiredSources = _relations
                .Where(relation => relation.OptionalString("kind") == "join" && relation.References("targetStep").Single() == target)
                .Select(relation => relation.References("sourceStep").Single())
                .Distinct(StringComparer.Ordinal)
                .ToList();
            return requiredSources.Count > 0 && requiredSources.All(source => _completed.Contains(source));
        }

        private void Activate(IEnumerable<string> stepIds)
        {
            foreach (var id in stepIds)
            {
                if (!_scenarioSteps.Contains(id))
                    throw new FunctionalMldsV2FormatException($"Cannot activate step {id} outside Scenario {_scenario.Id}.");
                _active.Add(id);
            }
            _context.SetActiveSteps(_active.OrderBy(value => value, StringComparer.Ordinal), _index);
        }
    }
}
