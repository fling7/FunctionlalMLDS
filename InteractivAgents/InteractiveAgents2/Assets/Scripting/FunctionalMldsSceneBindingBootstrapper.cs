using System;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;
using UnityEngine;

/// <summary>
/// Creates runtime scene bindings from explicit V2 Entity IDs. A generated room object is
/// matched only by the pipeline's stable "sourceId" or "sourceId_objectType" name. Fuzzy
/// matching is deliberately excluded because a plausible but wrong spatial target is worse
/// than an unavailable one.
/// </summary>
public static class FunctionalMldsSceneBindingBootstrapper
{
    public sealed class Report
    {
        public int ExpectedBindingCount;
        public int BoundCount;
        public int GeneratedCount;
        public int ManualCount;
        public readonly List<FunctionalMldsSceneObjectBinding> Bindings =
            new List<FunctionalMldsSceneObjectBinding>();
        public readonly List<string> Errors = new List<string>();

        public bool IsValid =>
            Errors.Count == 0 && BoundCount == ExpectedBindingCount;

        public string Summary()
        {
            if (IsValid)
            {
                return $"valid (expected={ExpectedBindingCount}, bound={BoundCount}, "
                    + $"generated={GeneratedCount}, manual={ManualCount})";
            }
            return $"invalid (expected={ExpectedBindingCount}, bound={BoundCount}): "
                + string.Join(" | ", Errors);
        }
    }

    public static Report ApplyV2Model(string modelJson)
    {
        var report = new Report();
        var sceneBindings = FindSceneObjects<FunctionalMldsSceneObjectBinding>();
        for (var i = 0; i < sceneBindings.Count; i++)
        {
            var existing = sceneBindings[i];
            if (existing != null && existing.GeneratedFromModel)
            {
                existing.SetHighlighted(false, Color.clear, 0f);
                existing.enabled = false;
            }
        }

        JObject root;
        try
        {
            root = JObject.Parse(modelJson ?? string.Empty);
        }
        catch (Exception exception)
        {
            report.Errors.Add("V2 model JSON cannot be parsed: " + exception.Message);
            return report;
        }

        var objectArray = root["objects"] as JArray;
        if (objectArray == null)
        {
            report.Errors.Add("V2 model has no objects array.");
            return report;
        }

        var specs = ParseSpecs(objectArray, report.Errors);
        report.ExpectedBindingCount = specs.Count;
        var sceneObjects = FindSceneObjects<Transform>();

        for (var specIndex = 0; specIndex < specs.Count; specIndex++)
        {
            var spec = specs[specIndex];
            var matchingBindings = FindExistingBindings(sceneBindings, spec);
            if (matchingBindings.Count > 1)
            {
                report.Errors.Add(
                    $"{spec.EntityId}: {matchingBindings.Count} existing bindings match "
                    + $"entity/source identity.");
                continue;
            }

            if (matchingBindings.Count == 1)
            {
                var existing = matchingBindings[0];
                if (!ApplyExistingBinding(existing, spec, report))
                    continue;
                AddBinding(report, existing, existing.GeneratedFromModel);
                continue;
            }

            var objectMatches = FindNamedSceneObjects(
                sceneObjects,
                spec.SourceObjectId,
                spec.ObjectType);
            if (objectMatches.Count == 0)
            {
                report.Errors.Add(
                    $"{spec.EntityId}: no scene GameObject matches sourceObjectId "
                    + $"'{spec.SourceObjectId}'.");
                continue;
            }
            if (objectMatches.Count > 1)
            {
                report.Errors.Add(
                    $"{spec.EntityId}: sourceObjectId '{spec.SourceObjectId}' matches "
                    + $"{objectMatches.Count} scene GameObjects.");
                continue;
            }

            var target = objectMatches[0];
            var conflictingBinding = target.GetComponent<FunctionalMldsSceneObjectBinding>();
            if (conflictingBinding != null)
            {
                report.Errors.Add(
                    $"{spec.EntityId}: scene object '{target.name}' already has a binding "
                    + $"for '{conflictingBinding.EntityId}'.");
                continue;
            }

            Collider collider;
            string colliderError;
            if (!TryResolveUniqueCollider(target, out collider, out colliderError))
            {
                report.Errors.Add($"{spec.EntityId} on '{target.name}': {colliderError}");
                continue;
            }

            var generated = target.gameObject.AddComponent<FunctionalMldsSceneObjectBinding>();
            generated.Configure(
                spec.EntityId,
                spec.SourceObjectId,
                spec.ObjectGroupId,
                spec.ZoneId,
                spec.DisplayName,
                collider,
                spec.Synonyms,
                true);
            generated.enabled = true;
            sceneBindings.Add(generated);
            AddBinding(report, generated, true);
        }

        report.Errors.Sort(StringComparer.Ordinal);
        return report;
    }

    public static void DisableGeneratedBindings()
    {
        var bindings = FindSceneObjects<FunctionalMldsSceneObjectBinding>();
        for (var i = 0; i < bindings.Count; i++)
        {
            var binding = bindings[i];
            if (binding == null || !binding.GeneratedFromModel)
                continue;
            binding.SetHighlighted(false, Color.clear, 0f);
            binding.enabled = false;
        }
    }

    private static List<ModelBindingSpec> ParseSpecs(
        JArray objects,
        ICollection<string> errors)
    {
        var zonesBySource = new Dictionary<string, List<string>>(StringComparer.Ordinal);
        var sceneEntities = new List<JObject>();

        for (var i = 0; i < objects.Count; i++)
        {
            var item = objects[i] as JObject;
            if (item == null || Text(item["type"]) != "Entity")
                continue;
            var role = Text(item["entityRole"]);
            if (role == "semanticZone")
            {
                var zoneId = Text(item["id"]);
                var sourceIds = TextArray(item["sourceObjectId"]);
                for (var sourceIndex = 0; sourceIndex < sourceIds.Length; sourceIndex++)
                {
                    List<string> zones;
                    if (!zonesBySource.TryGetValue(sourceIds[sourceIndex], out zones))
                    {
                        zones = new List<string>();
                        zonesBySource.Add(sourceIds[sourceIndex], zones);
                    }
                    if (!zones.Contains(zoneId))
                        zones.Add(zoneId);
                }
            }
            else if (role == "sceneObject")
            {
                sceneEntities.Add(item);
            }
        }

        sceneEntities.Sort((left, right) =>
            string.Compare(Text(left["id"]), Text(right["id"]), StringComparison.Ordinal));

        var result = new List<ModelBindingSpec>();
        var entityIds = new HashSet<string>(StringComparer.Ordinal);
        var sourceIdsSeen = new HashSet<string>(StringComparer.Ordinal);
        for (var i = 0; i < sceneEntities.Count; i++)
        {
            var item = sceneEntities[i];
            var entityId = Text(item["id"]);
            var sourceObjectId = Text(item["sourceId"]);
            var displayName = Text(item["name"]);
            var objectType = Text(item["objectType"]);
            var groups = TextArray(item["objectGroup"]);
            List<string> zones;
            zonesBySource.TryGetValue(sourceObjectId, out zones);

            if (entityId.Length == 0)
                errors.Add($"Scene-object Entity at objects[{i}] has no id.");
            else if (!entityIds.Add(entityId))
                errors.Add($"Duplicate scene-object Entity id '{entityId}'.");
            if (sourceObjectId.Length == 0)
                errors.Add($"{entityId}: sourceId is missing.");
            else if (!sourceIdsSeen.Add(sourceObjectId))
                errors.Add($"Duplicate scene-object sourceId '{sourceObjectId}'.");
            if (groups.Length != 1)
                errors.Add($"{entityId}: expected exactly one objectGroup, got {groups.Length}.");
            if (zones == null || zones.Count != 1)
                errors.Add(
                    $"{entityId}: sourceId '{sourceObjectId}' must belong to exactly one "
                    + $"semantic zone, got {(zones == null ? 0 : zones.Count)}.");

            var aliases = UniqueNonEmpty(sourceObjectId, displayName, objectType);
            result.Add(new ModelBindingSpec
            {
                EntityId = entityId,
                SourceObjectId = sourceObjectId,
                ObjectGroupId = groups.Length == 1 ? groups[0] : string.Empty,
                ZoneId = zones != null && zones.Count == 1 ? zones[0] : string.Empty,
                DisplayName = displayName.Length == 0 ? sourceObjectId : displayName,
                ObjectType = objectType,
                Synonyms = aliases
            });
        }
        return result;
    }

    private static bool ApplyExistingBinding(
        FunctionalMldsSceneObjectBinding existing,
        ModelBindingSpec spec,
        Report report)
    {
        if (existing == null)
            return false;

        Collider collider;
        string colliderError;
        if (!existing.TryResolveSelectionCollider(out collider, out colliderError))
        {
            report.Errors.Add($"{spec.EntityId} on '{existing.gameObject.name}': {colliderError}");
            return false;
        }

        if (existing.GeneratedFromModel)
        {
            existing.Configure(
                spec.EntityId,
                spec.SourceObjectId,
                spec.ObjectGroupId,
                spec.ZoneId,
                spec.DisplayName,
                collider,
                spec.Synonyms,
                true);
            existing.enabled = true;
            return true;
        }

        if (!existing.enabled)
        {
            report.Errors.Add($"{spec.EntityId}: matching manual binding is disabled.");
            return false;
        }

        var mismatches = new List<string>();
        CompareField(mismatches, "entityId", existing.EntityId, spec.EntityId);
        CompareField(mismatches, "sourceObjectId", existing.SourceObjectId, spec.SourceObjectId);
        CompareField(mismatches, "objectGroupId", existing.ObjectGroupId, spec.ObjectGroupId);
        CompareField(mismatches, "zoneId", existing.ZoneId, spec.ZoneId);
        if (mismatches.Count > 0)
        {
            report.Errors.Add(
                $"{spec.EntityId}: manual binding conflicts with the V2 model: "
                + string.Join(", ", mismatches));
            return false;
        }
        return true;
    }

    private static List<FunctionalMldsSceneObjectBinding> FindExistingBindings(
        IList<FunctionalMldsSceneObjectBinding> bindings,
        ModelBindingSpec spec)
    {
        var result = new List<FunctionalMldsSceneObjectBinding>();
        for (var i = 0; i < bindings.Count; i++)
        {
            var binding = bindings[i];
            if (binding == null)
                continue;
            if (string.Equals(binding.EntityId, spec.EntityId, StringComparison.Ordinal)
                || string.Equals(
                    binding.SourceObjectId,
                    spec.SourceObjectId,
                    StringComparison.Ordinal))
            {
                result.Add(binding);
            }
        }
        return result;
    }

    private static List<GameObject> FindNamedSceneObjects(
        IList<Transform> sceneTransforms,
        string sourceObjectId,
        string objectType)
    {
        var result = new List<GameObject>();
        if (string.IsNullOrWhiteSpace(sourceObjectId))
            return result;

        var exactGeneratedName = string.IsNullOrWhiteSpace(objectType)
            ? string.Empty
            : sourceObjectId + "_" + objectType.Trim();
        for (var i = 0; i < sceneTransforms.Count; i++)
        {
            var transform = sceneTransforms[i];
            if (transform == null)
                continue;
            var objectName = transform.gameObject.name;
            if (string.Equals(objectName, sourceObjectId, StringComparison.OrdinalIgnoreCase)
                || (!string.IsNullOrEmpty(exactGeneratedName)
                    && string.Equals(
                        objectName,
                        exactGeneratedName,
                        StringComparison.OrdinalIgnoreCase)))
            {
                result.Add(transform.gameObject);
            }
        }
        result.Sort((left, right) =>
            string.Compare(ScenePath(left), ScenePath(right), StringComparison.Ordinal));
        return result;
    }

    private static bool TryResolveUniqueCollider(
        GameObject target,
        out Collider collider,
        out string error)
    {
        var direct = target.GetComponents<Collider>();
        var directNonTriggers = NonTriggerColliders(direct);
        if (directNonTriggers.Count == 1)
        {
            collider = directNonTriggers[0];
            error = null;
            return true;
        }
        if (directNonTriggers.Count > 1)
        {
            collider = null;
            error = $"{directNonTriggers.Count} direct non-trigger colliders are ambiguous.";
            return false;
        }

        var descendants = NonTriggerColliders(target.GetComponentsInChildren<Collider>(true));
        if (descendants.Count == 1)
        {
            collider = descendants[0];
            error = null;
            return true;
        }

        collider = null;
        error = descendants.Count == 0
            ? "no non-trigger collider exists"
            : $"{descendants.Count} descendant non-trigger colliders are ambiguous";
        return false;
    }

    private static List<Collider> NonTriggerColliders(IEnumerable<Collider> colliders)
    {
        var result = new List<Collider>();
        if (colliders == null)
            return result;
        foreach (var collider in colliders)
        {
            if (collider != null && !collider.isTrigger)
                result.Add(collider);
        }
        return result;
    }

    private static List<T> FindSceneObjects<T>() where T : UnityEngine.Object
    {
        var all = Resources.FindObjectsOfTypeAll<T>();
        var result = new List<T>();
        for (var i = 0; i < all.Length; i++)
        {
            var item = all[i];
            var component = item as Component;
            var gameObject = item as GameObject;
            var scene = component != null
                ? component.gameObject.scene
                : gameObject != null ? gameObject.scene : default;
            if (!scene.IsValid() || !scene.isLoaded)
                continue;
            result.Add(item);
        }
        return result;
    }

    private static void AddBinding(
        Report report,
        FunctionalMldsSceneObjectBinding binding,
        bool generated)
    {
        report.Bindings.Add(binding);
        report.BoundCount++;
        if (generated)
            report.GeneratedCount++;
        else
            report.ManualCount++;
    }

    private static void CompareField(
        ICollection<string> mismatches,
        string field,
        string actual,
        string expected)
    {
        if (!string.Equals(actual ?? string.Empty, expected ?? string.Empty, StringComparison.Ordinal))
            mismatches.Add($"{field}='{actual}' (model: '{expected}')");
    }

    private static string[] TextArray(JToken token)
    {
        var array = token as JArray;
        if (array == null)
            return Array.Empty<string>();
        var result = new List<string>();
        for (var i = 0; i < array.Count; i++)
        {
            var value = Text(array[i]);
            if (value.Length > 0)
                result.Add(value);
        }
        return result.ToArray();
    }

    private static string Text(JToken token)
    {
        return token == null || token.Type == JTokenType.Null
            ? string.Empty
            : (token.Type == JTokenType.String ? token.Value<string>() : token.ToString()).Trim();
    }

    private static string[] UniqueNonEmpty(params string[] values)
    {
        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var result = new List<string>();
        for (var i = 0; i < values.Length; i++)
        {
            var value = string.IsNullOrWhiteSpace(values[i]) ? string.Empty : values[i].Trim();
            if (value.Length > 0 && seen.Add(value))
                result.Add(value);
        }
        return result.ToArray();
    }

    private static string ScenePath(GameObject gameObject)
    {
        if (gameObject == null)
            return string.Empty;
        var parts = new List<string>();
        var current = gameObject.transform;
        while (current != null)
        {
            parts.Add(current.name);
            current = current.parent;
        }
        parts.Reverse();
        return gameObject.scene.path + ":" + string.Join("/", parts);
    }

    private sealed class ModelBindingSpec
    {
        public string EntityId;
        public string SourceObjectId;
        public string ObjectGroupId;
        public string ZoneId;
        public string DisplayName;
        public string ObjectType;
        public string[] Synonyms;
    }
}
