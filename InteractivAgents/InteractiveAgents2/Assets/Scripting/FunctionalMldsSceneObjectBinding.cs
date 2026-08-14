using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Stable, inspectable link between one rendered Unity object and one scene-object Entity
/// in a FunctionalMLDS V2 model. The IDs are data, not values derived from a display name
/// during interaction.
/// </summary>
[DisallowMultipleComponent]
[AddComponentMenu("FunctionalMLDS/Scene Object Binding")]
public sealed class FunctionalMldsSceneObjectBinding : MonoBehaviour
{
    [Header("FunctionalMLDS identity")]
    [SerializeField] private string entityId;
    [SerializeField] private string sourceObjectId;
    [SerializeField] private string objectGroupId;
    [SerializeField] private string zoneId;

    [Header("Human-readable reference")]
    [SerializeField] private string displayName;
    [SerializeField] private string[] synonyms = Array.Empty<string>();

    [Header("Unity selection")]
    [SerializeField] private Collider selectionCollider;
    [SerializeField] private Renderer[] highlightRenderers = Array.Empty<Renderer>();

    [SerializeField, HideInInspector] private bool generatedFromModel;

    private readonly List<HighlightMaterialState> highlightMaterialStates =
        new List<HighlightMaterialState>();
    private bool isHighlighted;

    public string EntityId => entityId;
    public string SourceObjectId => sourceObjectId;
    public string ObjectGroupId => objectGroupId;
    public string ZoneId => zoneId;
    public string DisplayName => displayName;
    public string[] Synonyms => synonyms ?? Array.Empty<string>();
    public Collider SelectionCollider => selectionCollider;
    public bool GeneratedFromModel => generatedFromModel;

    /// <summary>
    /// Used by the deterministic V2 bootstrapper and by editor smoke tests. Runtime selection
    /// never infers or rewrites these values.
    /// </summary>
    public void Configure(
        string modelEntityId,
        string modelSourceObjectId,
        string modelObjectGroupId,
        string modelZoneId,
        string humanReadableName,
        Collider collider,
        string[] aliases,
        bool isGeneratedFromModel = false)
    {
        entityId = Clean(modelEntityId);
        sourceObjectId = Clean(modelSourceObjectId);
        objectGroupId = Clean(modelObjectGroupId);
        zoneId = Clean(modelZoneId);
        displayName = Clean(humanReadableName);
        selectionCollider = collider;
        synonyms = NormalizeAliases(aliases);
        generatedFromModel = isGeneratedFromModel;
    }

    public bool TryResolveSelectionCollider(out Collider collider, out string reason)
    {
        if (selectionCollider != null)
        {
            if (selectionCollider.isTrigger)
            {
                collider = null;
                reason = "The configured selection collider is a trigger.";
                return false;
            }

            var colliderTransform = selectionCollider.transform;
            if (colliderTransform != transform && !colliderTransform.IsChildOf(transform))
            {
                collider = null;
                reason = "The configured selection collider is outside the bound object hierarchy.";
                return false;
            }

            collider = selectionCollider;
            reason = null;
            return true;
        }

        var candidates = GetComponentsInChildren<Collider>(true);
        Collider unique = null;
        var count = 0;
        for (var i = 0; i < candidates.Length; i++)
        {
            var candidate = candidates[i];
            if (candidate == null || candidate.isTrigger)
                continue;
            unique = candidate;
            count++;
        }

        if (count == 1)
        {
            collider = unique;
            reason = null;
            return true;
        }

        collider = null;
        reason = count == 0
            ? "No non-trigger selection collider exists."
            : $"Selection collider is ambiguous ({count} non-trigger colliders).";
        return false;
    }

    /// <summary>
    /// Generated GLB instances are intentionally stored outside the disabled design
    /// placeholder hierarchy. The persistent DevDescription link is the authoritative
    /// relationship between both objects, so its visible non-trigger colliders may select
    /// this same semantic entity without relying on mesh names such as "geometry_0".
    /// </summary>
    public Collider[] ResolveLinkedGeneratedColliders()
    {
        var description = GetComponent<DevDescription>();
        var generated = description == null ? null : description.GeneratedInstance;
        if (generated == null || generated == gameObject)
            return Array.Empty<Collider>();

        var candidates = generated.GetComponentsInChildren<Collider>(true);
        var result = new List<Collider>();
        for (var i = 0; i < candidates.Length; i++)
        {
            var candidate = candidates[i];
            if (candidate != null && !candidate.isTrigger && candidate != selectionCollider)
                result.Add(candidate);
        }
        return result.ToArray();
    }

    public void SetHighlighted(bool highlighted, Color color, float emissionStrength)
    {
        if (highlighted == isHighlighted)
            return;

        if (highlighted)
        {
            CaptureAndApplyHighlight(color, emissionStrength);
            isHighlighted = true;
            return;
        }

        RestoreHighlight();
        isHighlighted = false;
    }

    private void OnDisable()
    {
        if (isHighlighted)
        {
            RestoreHighlight();
            isHighlighted = false;
        }
    }

    private void OnDestroy()
    {
        if (isHighlighted)
            RestoreHighlight();
    }

    private void CaptureAndApplyHighlight(Color color, float emissionStrength)
    {
        highlightMaterialStates.Clear();
        var renderers = ResolveHighlightRenderers();
        var capturedMaterials = new HashSet<Material>();
        for (var rendererIndex = 0; rendererIndex < renderers.Length; rendererIndex++)
        {
            var targetRenderer = renderers[rendererIndex];
            if (targetRenderer == null)
                continue;

            var materials = targetRenderer.materials;
            for (var materialIndex = 0; materialIndex < materials.Length; materialIndex++)
            {
                var material = materials[materialIndex];
                if (material == null || !capturedMaterials.Add(material))
                    continue;

                // Unity's standard/URP shaders and glTFast's shader graphs use
                // different reference names for the same PBR inputs.
                var colorProperty = FirstMaterialProperty(
                    material,
                    "_BaseColor",
                    "_Color",
                    "baseColorFactor",
                    "_BaseColorFactor");
                var emissionProperty = FirstMaterialProperty(
                    material,
                    "_EmissionColor",
                    "emissiveFactor",
                    "_EmissiveFactor");
                var hasEmission = emissionProperty != null;
                var state = new HighlightMaterialState
                {
                    Material = material,
                    ColorProperty = colorProperty,
                    OriginalColor = colorProperty == null ? Color.white : material.GetColor(colorProperty),
                    HasEmission = hasEmission,
                    EmissionProperty = emissionProperty,
                    OriginalEmission = hasEmission ? material.GetColor(emissionProperty) : Color.black,
                    UsesEmissionKeyword = emissionProperty == "_EmissionColor",
                    EmissionKeywordEnabled = emissionProperty == "_EmissionColor"
                        && material.IsKeywordEnabled("_EMISSION")
                };
                highlightMaterialStates.Add(state);

                if (colorProperty != null)
                    material.SetColor(colorProperty, color);
                if (hasEmission)
                {
                    if (state.UsesEmissionKeyword)
                        material.EnableKeyword("_EMISSION");
                    material.SetColor(
                        emissionProperty,
                        color * Mathf.Max(0f, emissionStrength));
                }
            }
        }
    }

    private void RestoreHighlight()
    {
        for (var i = 0; i < highlightMaterialStates.Count; i++)
        {
            var state = highlightMaterialStates[i];
            if (state.Material == null)
                continue;

            if (state.ColorProperty != null && state.Material.HasProperty(state.ColorProperty))
                state.Material.SetColor(state.ColorProperty, state.OriginalColor);
            if (state.HasEmission
                && !string.IsNullOrEmpty(state.EmissionProperty)
                && state.Material.HasProperty(state.EmissionProperty))
            {
                state.Material.SetColor(state.EmissionProperty, state.OriginalEmission);
                if (state.UsesEmissionKeyword && !state.EmissionKeywordEnabled)
                    state.Material.DisableKeyword("_EMISSION");
            }
        }
        highlightMaterialStates.Clear();
    }

    private Renderer[] ResolveHighlightRenderers()
    {
        if (highlightRenderers != null && highlightRenderers.Length > 0)
            return highlightRenderers;

        var description = GetComponent<DevDescription>();
        var generated = description == null ? null : description.GeneratedInstance;
        var candidates = generated != null && generated != gameObject
            ? generated.GetComponentsInChildren<Renderer>(true)
            : GetComponentsInChildren<Renderer>(true);
        var result = new List<Renderer>();
        for (var i = 0; i < candidates.Length; i++)
        {
            var candidate = candidates[i];
            if (candidate == null || candidate is LineRenderer || candidate is ParticleSystemRenderer)
                continue;
            result.Add(candidate);
        }
        return result.ToArray();
    }

    private static string Clean(string value)
    {
        return string.IsNullOrWhiteSpace(value) ? string.Empty : value.Trim();
    }

    private static string FirstMaterialProperty(Material material, params string[] names)
    {
        if (material == null || names == null)
            return null;
        for (var i = 0; i < names.Length; i++)
        {
            if (!string.IsNullOrEmpty(names[i]) && material.HasProperty(names[i]))
                return names[i];
        }
        return null;
    }

    private static string[] NormalizeAliases(IEnumerable<string> values)
    {
        if (values == null)
            return Array.Empty<string>();

        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var result = new List<string>();
        foreach (var value in values)
        {
            var clean = Clean(value);
            if (clean.Length == 0 || !seen.Add(clean))
                continue;
            result.Add(clean);
        }
        return result.ToArray();
    }

    private sealed class HighlightMaterialState
    {
        public Material Material;
        public string ColorProperty;
        public Color OriginalColor;
        public bool HasEmission;
        public string EmissionProperty;
        public Color OriginalEmission;
        public bool UsesEmissionKeyword;
        public bool EmissionKeywordEnabled;
    }
}

public static class FunctionalMldsSpatialTargetStates
{
    public const string None = "none";
    public const string Resolved = "resolved";
    public const string Ambiguous = "ambiguous";
}

/// <summary>
/// Result of resolving either a collider hit or a textual alias. No partial result is
/// returned when the registry itself is invalid.
/// </summary>
public sealed class FunctionalMldsSceneBindingResolution
{
    public string State { get; private set; }
    public FunctionalMldsSceneObjectBinding Binding { get; private set; }
    public string Reason { get; private set; }
    public string[] CandidateEntityIds { get; private set; }

    public bool IsResolved =>
        State == FunctionalMldsSpatialTargetStates.Resolved && Binding != null;

    private FunctionalMldsSceneBindingResolution(
        string state,
        FunctionalMldsSceneObjectBinding binding,
        string reason,
        string[] candidateEntityIds)
    {
        State = state;
        Binding = binding;
        Reason = reason ?? string.Empty;
        CandidateEntityIds = candidateEntityIds ?? Array.Empty<string>();
    }

    public static FunctionalMldsSceneBindingResolution None(string reason)
    {
        return new FunctionalMldsSceneBindingResolution(
            FunctionalMldsSpatialTargetStates.None,
            null,
            reason,
            Array.Empty<string>());
    }

    public static FunctionalMldsSceneBindingResolution Resolved(
        FunctionalMldsSceneObjectBinding binding)
    {
        return new FunctionalMldsSceneBindingResolution(
            FunctionalMldsSpatialTargetStates.Resolved,
            binding,
            string.Empty,
            binding == null ? Array.Empty<string>() : new[] { binding.EntityId });
    }

    public static FunctionalMldsSceneBindingResolution Ambiguous(
        string reason,
        IEnumerable<string> candidateEntityIds)
    {
        var candidates = new List<string>();
        if (candidateEntityIds != null)
        {
            var seen = new HashSet<string>(StringComparer.Ordinal);
            foreach (var candidate in candidateEntityIds)
            {
                if (!string.IsNullOrWhiteSpace(candidate) && seen.Add(candidate.Trim()))
                    candidates.Add(candidate.Trim());
            }
        }
        candidates.Sort(StringComparer.Ordinal);
        return new FunctionalMldsSceneBindingResolution(
            FunctionalMldsSpatialTargetStates.Ambiguous,
            null,
            reason,
            candidates.ToArray());
    }
}

/// <summary>
/// Deterministic index over scene bindings. Duplicate identities, duplicate colliders,
/// incomplete records, and bootstrap errors invalidate the complete index (fail closed).
/// Shared display names or synonyms remain indexable but resolve as ambiguous.
/// </summary>
public sealed class FunctionalMldsSceneObjectBindingRegistry
{
    private readonly Dictionary<Collider, FunctionalMldsSceneObjectBinding> byCollider =
        new Dictionary<Collider, FunctionalMldsSceneObjectBinding>();
    private readonly Dictionary<string, List<FunctionalMldsSceneObjectBinding>> byReference =
        new Dictionary<string, List<FunctionalMldsSceneObjectBinding>>(StringComparer.OrdinalIgnoreCase);
    private readonly List<FunctionalMldsSceneObjectBinding> bindings =
        new List<FunctionalMldsSceneObjectBinding>();
    private readonly List<string> validationErrors = new List<string>();

    public bool IsValid => validationErrors.Count == 0;
    public int Count => bindings.Count;
    public IReadOnlyList<FunctionalMldsSceneObjectBinding> Bindings => bindings;
    public IReadOnlyList<string> ValidationErrors => validationErrors;

    public void Rebuild(
        IEnumerable<FunctionalMldsSceneObjectBinding> candidates,
        IEnumerable<string> bootstrapErrors = null)
    {
        byCollider.Clear();
        byReference.Clear();
        bindings.Clear();
        validationErrors.Clear();

        if (bootstrapErrors != null)
        {
            foreach (var error in bootstrapErrors)
            {
                if (!string.IsNullOrWhiteSpace(error))
                    validationErrors.Add("Bootstrap: " + error.Trim());
            }
        }

        if (candidates != null)
        {
            foreach (var candidate in candidates)
            {
                if (candidate != null && candidate.enabled)
                    bindings.Add(candidate);
            }
        }

        bindings.Sort(CompareBindings);
        var byEntityId = new Dictionary<string, FunctionalMldsSceneObjectBinding>(
            StringComparer.Ordinal);
        var bySourceObjectId = new Dictionary<string, FunctionalMldsSceneObjectBinding>(
            StringComparer.Ordinal);

        for (var i = 0; i < bindings.Count; i++)
        {
            var binding = bindings[i];
            ValidateRequired(binding, "entityId", binding.EntityId);
            ValidateRequired(binding, "sourceObjectId", binding.SourceObjectId);
            ValidateRequired(binding, "objectGroupId", binding.ObjectGroupId);
            ValidateRequired(binding, "zoneId", binding.ZoneId);
            ValidateRequired(binding, "displayName", binding.DisplayName);

            Collider collider;
            string colliderReason;
            if (!binding.TryResolveSelectionCollider(out collider, out colliderReason))
            {
                validationErrors.Add(Describe(binding) + ": " + colliderReason);
            }
            else
            {
                FunctionalMldsSceneObjectBinding existingColliderBinding;
                if (byCollider.TryGetValue(collider, out existingColliderBinding))
                {
                    validationErrors.Add(
                        $"Collider '{collider.name}' is shared by "
                        + $"{Describe(existingColliderBinding)} and {Describe(binding)}.");
                }
                else
                {
                    byCollider.Add(collider, binding);
                }
            }

            var linkedColliders = binding.ResolveLinkedGeneratedColliders();
            for (var linkedIndex = 0; linkedIndex < linkedColliders.Length; linkedIndex++)
            {
                var linkedCollider = linkedColliders[linkedIndex];
                if (linkedCollider == null || linkedCollider == collider)
                    continue;

                FunctionalMldsSceneObjectBinding existingLinkedBinding;
                if (byCollider.TryGetValue(linkedCollider, out existingLinkedBinding))
                {
                    if (existingLinkedBinding != binding)
                    {
                        validationErrors.Add(
                            $"Linked collider '{linkedCollider.name}' is shared by "
                            + $"{Describe(existingLinkedBinding)} and {Describe(binding)}.");
                    }
                    continue;
                }
                byCollider.Add(linkedCollider, binding);
            }

            AddUniqueIdentity(byEntityId, binding.EntityId, binding, "entityId");
            AddUniqueIdentity(bySourceObjectId, binding.SourceObjectId, binding, "sourceObjectId");

            AddReference(binding.EntityId, binding);
            AddReference(binding.SourceObjectId, binding);
            AddReference(binding.DisplayName, binding);
            var aliases = binding.Synonyms;
            for (var aliasIndex = 0; aliasIndex < aliases.Length; aliasIndex++)
                AddReference(aliases[aliasIndex], binding);
        }

        validationErrors.Sort(StringComparer.Ordinal);
    }

    public FunctionalMldsSceneBindingResolution ResolveCollider(Collider collider)
    {
        if (!IsValid)
            return InvalidRegistryResolution();
        if (collider == null)
            return FunctionalMldsSceneBindingResolution.None("Raycast returned no collider.");

        FunctionalMldsSceneObjectBinding binding;
        return byCollider.TryGetValue(collider, out binding)
            ? FunctionalMldsSceneBindingResolution.Resolved(binding)
            : FunctionalMldsSceneBindingResolution.None(
                $"Collider '{collider.name}' has no FunctionalMLDS binding.");
    }

    public FunctionalMldsSceneBindingResolution ResolveReference(string reference)
    {
        if (!IsValid)
            return InvalidRegistryResolution();
        if (string.IsNullOrWhiteSpace(reference))
            return FunctionalMldsSceneBindingResolution.None("Reference is empty.");

        List<FunctionalMldsSceneObjectBinding> matches;
        if (!byReference.TryGetValue(reference.Trim(), out matches) || matches.Count == 0)
            return FunctionalMldsSceneBindingResolution.None(
                $"No scene object is registered for '{reference.Trim()}'.");
        if (matches.Count == 1)
            return FunctionalMldsSceneBindingResolution.Resolved(matches[0]);

        var ids = new List<string>();
        for (var i = 0; i < matches.Count; i++)
            ids.Add(matches[i].EntityId);
        return FunctionalMldsSceneBindingResolution.Ambiguous(
            $"Reference '{reference.Trim()}' matches {matches.Count} scene objects.",
            ids);
    }

    public string ValidationSummary()
    {
        if (IsValid)
            return $"valid ({bindings.Count} bindings)";
        return string.Join(" | ", validationErrors);
    }

    private FunctionalMldsSceneBindingResolution InvalidRegistryResolution()
    {
        var ids = new List<string>();
        for (var i = 0; i < bindings.Count; i++)
            ids.Add(bindings[i].EntityId);
        return FunctionalMldsSceneBindingResolution.Ambiguous(
            "Scene binding registry is invalid: " + ValidationSummary(),
            ids);
    }

    private void AddUniqueIdentity(
        IDictionary<string, FunctionalMldsSceneObjectBinding> index,
        string value,
        FunctionalMldsSceneObjectBinding binding,
        string fieldName)
    {
        if (string.IsNullOrWhiteSpace(value))
            return;
        FunctionalMldsSceneObjectBinding existing;
        if (index.TryGetValue(value, out existing))
        {
            validationErrors.Add(
                $"Duplicate {fieldName} '{value}' on {Describe(existing)} and {Describe(binding)}.");
            return;
        }
        index.Add(value, binding);
    }

    private void AddReference(string value, FunctionalMldsSceneObjectBinding binding)
    {
        if (string.IsNullOrWhiteSpace(value))
            return;
        var clean = value.Trim();
        List<FunctionalMldsSceneObjectBinding> items;
        if (!byReference.TryGetValue(clean, out items))
        {
            items = new List<FunctionalMldsSceneObjectBinding>();
            byReference.Add(clean, items);
        }
        if (!items.Contains(binding))
            items.Add(binding);
    }

    private void ValidateRequired(
        FunctionalMldsSceneObjectBinding binding,
        string fieldName,
        string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            validationErrors.Add(Describe(binding) + $": required {fieldName} is missing.");
    }

    private static int CompareBindings(
        FunctionalMldsSceneObjectBinding left,
        FunctionalMldsSceneObjectBinding right)
    {
        var byId = string.Compare(
            left == null ? string.Empty : left.EntityId,
            right == null ? string.Empty : right.EntityId,
            StringComparison.Ordinal);
        if (byId != 0)
            return byId;
        return string.Compare(
            BindingScenePath(left),
            BindingScenePath(right),
            StringComparison.Ordinal);
    }

    private static string BindingScenePath(FunctionalMldsSceneObjectBinding binding)
    {
        if (binding == null)
            return string.Empty;
        var parts = new List<string>();
        var current = binding.transform;
        while (current != null)
        {
            parts.Add(current.name);
            current = current.parent;
        }
        parts.Reverse();
        return binding.gameObject.scene.path + ":" + string.Join("/", parts);
    }

    private static string Describe(FunctionalMldsSceneObjectBinding binding)
    {
        if (binding == null)
            return "<null binding>";
        var id = string.IsNullOrWhiteSpace(binding.EntityId)
            ? "<missing entityId>"
            : binding.EntityId;
        return $"{id} on '{binding.gameObject.name}'";
    }
}
