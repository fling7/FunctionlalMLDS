using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public static class FunctionalMldsSpatialGroundingSmoke
{
    [MenuItem("Tools/Interactive Agents/Tests/Run Spatial Grounding Smoke Test")]
    public static void RunFromMenu()
    {
        Run();
        EditorUtility.DisplayDialog(
            "Spatial Grounding Smoke Test",
            "Registry, model bootstrap, ray selection, agent-selection compatibility, "
            + "and JSON contract passed.",
            "OK");
    }

    // Command line:
    // Unity.exe -batchmode -quit -projectPath <project> \
    //   -executeMethod FunctionalMldsSpatialGroundingSmoke.RunFromCommandLine -logFile -
    public static void RunFromCommandLine()
    {
        Run();
        Debug.Log("[FunctionalMldsSpatialGroundingSmoke] OK");
    }

    private static void Run()
    {
        var previousScene = SceneManager.GetActiveScene();
        var priorGeneratedStates = CaptureGeneratedBindingStates();
        var reuseBatchModeScene = previousScene.IsValid()
            && string.IsNullOrEmpty(previousScene.path);
        var testScene = reuseBatchModeScene
            ? previousScene
            : EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Additive);
        if (!reuseBatchModeScene)
            SceneManager.SetActiveScene(testScene);

        try
        {
            RunRegistryValidationSmoke();
            RunModelBootstrapSmoke();
            RunChatSerializationSmoke();
            RunGeneratedInstanceColliderSmoke();
            RunRayAndAgentCompatibilitySmoke();
        }
        finally
        {
            if (!reuseBatchModeScene && previousScene.IsValid() && previousScene.isLoaded)
                SceneManager.SetActiveScene(previousScene);
            if (!reuseBatchModeScene)
                EditorSceneManager.CloseScene(testScene, true);
            RestoreGeneratedBindingStates(priorGeneratedStates);
        }
    }

    private static void RunRegistryValidationSmoke()
    {
        var first = CreateBoundCube(
            "registry_first",
            "ENT-SMOKE-FIRST",
            "smoke_first",
            "ENT-GROUP-SMOKE",
            "ENT-ZONE-SMOKE",
            new[] { "shared alias", "first" },
            new Vector3(-20f, 0f, 0f));
        var second = CreateBoundCube(
            "registry_second",
            "ENT-SMOKE-SECOND",
            "smoke_second",
            "ENT-GROUP-SMOKE",
            "ENT-ZONE-SMOKE",
            new[] { "shared alias", "second" },
            new Vector3(-22f, 0f, 0f));

        var registry = new FunctionalMldsSceneObjectBindingRegistry();
        registry.Rebuild(new[] { first, second });
        Require(registry.IsValid, "Two complete unique bindings should be valid.");
        Require(
            registry.ResolveCollider(first.SelectionCollider).IsResolved,
            "Collider lookup did not resolve the exact binding.");

        var aliasResolution = registry.ResolveReference("shared alias");
        Require(
            aliasResolution.State == FunctionalMldsSpatialTargetStates.Ambiguous
            && aliasResolution.CandidateEntityIds.Length == 2,
            "A shared synonym must resolve as ambiguous.");

        var duplicate = CreateBoundCube(
            "registry_duplicate",
            "ENT-SMOKE-FIRST",
            "smoke_duplicate",
            "ENT-GROUP-SMOKE",
            "ENT-ZONE-SMOKE",
            new[] { "duplicate" },
            new Vector3(-24f, 0f, 0f));
        registry.Rebuild(new[] { first, second, duplicate });
        Require(!registry.IsValid, "Duplicate entityId was accepted.");
        Require(
            registry.ResolveCollider(first.SelectionCollider).State
                == FunctionalMldsSpatialTargetStates.Ambiguous,
            "An invalid registry did not fail closed.");

        var missingColliderObject = new GameObject("registry_missing_collider");
        var missingCollider = missingColliderObject.AddComponent<FunctionalMldsSceneObjectBinding>();
        missingCollider.Configure(
            "ENT-SMOKE-MISSING",
            "smoke_missing",
            "ENT-GROUP-SMOKE",
            "ENT-ZONE-SMOKE",
            "Missing collider",
            null,
            new[] { "missing" });
        registry.Rebuild(new[] { missingCollider });
        Require(!registry.IsValid, "Missing collider was accepted.");

        UnityEngine.Object.DestroyImmediate(first.gameObject);
        UnityEngine.Object.DestroyImmediate(second.gameObject);
        UnityEngine.Object.DestroyImmediate(duplicate.gameObject);
        UnityEngine.Object.DestroyImmediate(missingColliderObject);
    }

    private static void RunModelBootstrapSmoke()
    {
        const string sourceId = "iui_spatial_bootstrap_asset";
        const string entityId = "ENT-IUI-SPATIAL-BOOTSTRAP";
        var target = GameObject.CreatePrimitive(PrimitiveType.Cube);
        target.name = sourceId + "_artifact";
        target.transform.position = new Vector3(-30f, 0f, 0f);
        var generatedVariant = GameObject.CreatePrimitive(PrimitiveType.Cube);
        generatedVariant.name = sourceId + "_artifact_0123456789abcdef";
        generatedVariant.transform.position = new Vector3(-31f, 0f, 0f);

        var model = new JObject
        {
            ["schema_version"] = "2.0",
            ["objects"] = new JArray
            {
                new JObject
                {
                    ["id"] = "ENT-ZONE-IUI-SMOKE",
                    ["type"] = "Entity",
                    ["name"] = "Smoke zone",
                    ["kind"] = "zone",
                    ["sourceId"] = "smoke_zone",
                    ["entityRole"] = "semanticZone",
                    ["sourceObjectId"] = new JArray(sourceId)
                },
                new JObject
                {
                    ["id"] = "ENT-GROUP-IUI-SMOKE",
                    ["type"] = "Entity",
                    ["name"] = "Smoke group",
                    ["kind"] = "asset",
                    ["sourceId"] = "group:smoke",
                    ["entityRole"] = "objectGroup",
                    ["sourceObjectId"] = new JArray(sourceId),
                    ["sourceGroup"] = "smoke"
                },
                new JObject
                {
                    ["id"] = entityId,
                    ["type"] = "Entity",
                    ["name"] = "Inspectable artifact",
                    ["kind"] = "asset",
                    ["sourceId"] = sourceId,
                    ["entityRole"] = "sceneObject",
                    ["sourceGroup"] = "smoke",
                    ["objectType"] = "artifact",
                    ["objectGroup"] = new JArray("ENT-GROUP-IUI-SMOKE")
                }
            }
        };

        var report = FunctionalMldsSceneBindingBootstrapper.ApplyV2Model(
            model.ToString(Newtonsoft.Json.Formatting.None));
        Require(report.IsValid, "Valid V2 bootstrap failed: " + report.Summary());
        Require(
            report.ExpectedBindingCount == 1
            && report.BoundCount == 1
            && report.GeneratedCount == 1,
            "Bootstrap counts are inconsistent.");

        var binding = target.GetComponent<FunctionalMldsSceneObjectBinding>();
        Require(binding != null, "Bootstrap did not create a binding component.");
        Require(
            generatedVariant.GetComponent<FunctionalMldsSceneObjectBinding>() == null,
            "A generated UUID-suffix variant was mistaken for the stable scene identity.");
        Require(
            binding.EntityId == entityId
            && binding.SourceObjectId == sourceId
            && binding.ObjectGroupId == "ENT-GROUP-IUI-SMOKE"
            && binding.ZoneId == "ENT-ZONE-IUI-SMOKE",
            "Bootstrap binding does not preserve model IDs.");

        var ambiguousTwin = GameObject.CreatePrimitive(PrimitiveType.Cube);
        ambiguousTwin.name = sourceId + "_artifact";
        ambiguousTwin.transform.position = new Vector3(-32f, 0f, 0f);
        UnityEngine.Object.DestroyImmediate(binding);
        var ambiguousReport = FunctionalMldsSceneBindingBootstrapper.ApplyV2Model(
            model.ToString(Newtonsoft.Json.Formatting.None));
        Require(
            !ambiguousReport.IsValid
            && ContainsText(ambiguousReport.Errors, "matches 2 scene GameObjects"),
            "Ambiguous scene-name bootstrap did not fail closed.");

        UnityEngine.Object.DestroyImmediate(target);
        UnityEngine.Object.DestroyImmediate(generatedVariant);
        UnityEngine.Object.DestroyImmediate(ambiguousTwin);
    }

    private static void RunChatSerializationSmoke()
    {
        var legacyJson = QuickAgentManager.SerializeChatRequest(new QuickAgentManager.ChatRequest
        {
            session_id = "session",
            active_agent_id = "agent",
            user_text = "hello"
        });
        var legacy = JObject.Parse(legacyJson);
        Require(
            legacy["spatial_context"] == null
            || legacy["spatial_context"].Type == JTokenType.Null,
            "Legacy request unexpectedly contains a non-null spatial context.");

        var groundedJson = QuickAgentManager.SerializeChatRequest(new QuickAgentManager.ChatRequest
        {
            session_id = "session",
            active_agent_id = "agent",
            user_text = "What is this?",
            interaction_mode = FunctionalMlds.V2.FunctionalMldsV2InteractionEvidenceEvaluator.DeicticMode,
            spatial_context = new QuickAgentManager.SpatialContext
            {
                model_sha256 = "ABC123",
                state = FunctionalMldsSpatialTargetStates.Resolved,
                entity_id = "ENT-SMOKE",
                source_object_id = "smoke",
                object_group_id = "ENT-GROUP-SMOKE",
                zone_id = "ENT-ZONE-SMOKE",
                display_name = "Smoke",
                synonyms = new[] { "artifact" },
                hit_position = new QuickAgentManager.Vector3Data { x = 1f, y = 2f, z = 3f },
                distance_m = 4f,
                selection_modality = "mouse_ray",
                ambiguity_reason = string.Empty,
                candidate_entity_ids = new[] { "ENT-SMOKE" }
            }
        });
        var grounded = JObject.Parse(groundedJson);
        Require(
            (string)grounded["spatial_context"]?["entity_id"] == "ENT-SMOKE"
            && (string)grounded["interaction_mode"] == "deictic"
            && (string)grounded["spatial_context"]?["selection_modality"] == "mouse_ray"
            && (float?)grounded["spatial_context"]?["hit_position"]?["y"] == 2f,
            "Grounded request JSON does not match the backend contract.");

        var parsedResponse = Newtonsoft.Json.JsonConvert.DeserializeObject<
            QuickAgentManager.ChatResponse>(
            "{\"session_id\":\"session\",\"active_agent_id\":\"agent-b\","
            + "\"routing\":{\"selected_agent_id\":\"agent-b\","
            + "\"modeled_handoff\":false}}");
        Require(
            parsedResponse?.routing?.modeled_handoff.HasValue == true
            && parsedResponse.routing.modeled_handoff.Value == false,
            "Chat response JSON did not preserve a nullable modeled_handoff=false value.");
    }

    private static void RunRayAndAgentCompatibilitySmoke()
    {
        var managerObject = new GameObject("spatial_manager_smoke");
        var manager = managerObject.AddComponent<QuickAgentManager>();
        manager.showUi = false;
        manager.enableTts = false;
        manager.enableVoiceInput = false;
        manager.spatialSelectionMaxDistance = 20f;
        SetPrivate(manager, "currentModelSha256", "SMOKE-HASH");

        var target = CreateBoundCube(
            "spatial_ray_target",
            "ENT-SPATIAL-RAY",
            "spatial_ray",
            "ENT-GROUP-SPATIAL-RAY",
            "ENT-ZONE-SPATIAL-RAY",
            new[] { "ray target" },
            new Vector3(0f, 0.5f, 5f));
        manager.RefreshSpatialBindingRegistry();
        Physics.SyncTransforms();

        var ray = new Ray(new Vector3(0f, 0.5f, 0f), Vector3.forward);
        Require(
            manager.TrySelectSpatialTargetFromRay(ray, "mouse_ray"),
            "Ray did not select the semantic target.");
        Require(
            manager.SpatialSelectionState == FunctionalMldsSpatialTargetStates.Resolved
            && manager.SelectedSpatialEntityId == "ENT-SPATIAL-RAY",
            "Manager did not retain the resolved target state.");

        var agentObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
        agentObject.name = "Agent_spatial_smoke";
        agentObject.transform.position = new Vector3(0f, 0.5f, 2f);
        AddAgentVisual(manager, "agent-spatial-smoke", agentObject);
        manager.activeAgentId = "previous-agent";
        Physics.SyncTransforms();

        Require(
            manager.TrySelectSpatialTargetFromRay(ray, "mouse_ray")
            && manager.activeAgentId == "agent-spatial-smoke",
            "Agent click selection broke after adding semantic selection.");
        Require(
            manager.SpatialSelectionState == FunctionalMldsSpatialTargetStates.Resolved
            && manager.SelectedSpatialEntityId == "ENT-SPATIAL-RAY",
            "Selecting an agent unexpectedly cleared the semantic target.");

        Require(
            !manager.TrySelectSpatialTargetFromRay(ray, "unsupported-modality")
            && manager.SpatialSelectionState == FunctionalMldsSpatialTargetStates.Ambiguous,
            "Unsupported external modality did not fail closed.");

        UnityEngine.Object.DestroyImmediate(agentObject);
        UnityEngine.Object.DestroyImmediate(target.gameObject);
        UnityEngine.Object.DestroyImmediate(managerObject);
    }

    private static void RunGeneratedInstanceColliderSmoke()
    {
        var placeholder = GameObject.CreatePrimitive(PrimitiveType.Cube);
        placeholder.name = "linked_generated_placeholder";
        placeholder.transform.position = new Vector3(-30f, 0f, 0f);
        var placeholderCollider = placeholder.GetComponent<Collider>();
        var description = placeholder.AddComponent<DevDescription>();

        var generated = GameObject.CreatePrimitive(PrimitiveType.Cube);
        generated.name = "linked_generated_visible_instance";
        generated.transform.position = new Vector3(0f, 0.5f, 5f);
        var generatedCollider = generated.GetComponent<Collider>();
        description.SetGeneratedResult("job", "fingerprint", "signature", "asset.glb", generated);

        var binding = placeholder.AddComponent<FunctionalMldsSceneObjectBinding>();
        binding.Configure(
            "ENT-LINKED-GENERATED",
            "linked_generated",
            "ENT-GROUP-LINKED",
            "ENT-ZONE-LINKED",
            "Linked generated exhibit",
            placeholderCollider,
            new[] { "linked exhibit" });

        var registry = new FunctionalMldsSceneObjectBindingRegistry();
        registry.Rebuild(new[] { binding });
        var resolution = registry.ResolveCollider(generatedCollider);
        Require(registry.IsValid && resolution.IsResolved && resolution.Binding == binding,
            "A visible generated-instance collider did not resolve to its placeholder binding.");

        var managerObject = new GameObject("linked_generated_manager");
        var manager = managerObject.AddComponent<QuickAgentManager>();
        manager.showUi = false;
        manager.enableTts = false;
        manager.enableVoiceInput = false;
        manager.spatialSelectionMaxDistance = 20f;
        SetPrivate(manager, "currentModelSha256", "LINKED-SMOKE-HASH");
        manager.RefreshSpatialBindingRegistry();
        Physics.SyncTransforms();
        var ray = new Ray(new Vector3(0f, 0.5f, 0f), Vector3.forward);
        Require(manager.TrySelectSpatialTargetFromRay(ray, "desktop_ray")
                && manager.SelectedSpatialEntityId == "ENT-LINKED-GENERATED",
            "The complete QAM ray path did not select the visible generated instance.");

        // glTFast's shader graphs use these property names rather than Unity's
        // _BaseColor/_EmissionColor convention. Verify both application and restore.
        var generatedRenderer = generated.GetComponent<Renderer>();
        var originalMaterial = generatedRenderer.material;
        var gltfShader = Shader.Find("glTF-pbrMetallicRoughness")
            ?? Shader.Find("Shader Graphs/glTF-pbrMetallicRoughness");
        if (gltfShader != null
            && gltfShader.isSupported
            && gltfShader.FindPropertyIndex("baseColorFactor") >= 0
            && gltfShader.FindPropertyIndex("emissiveFactor") >= 0)
        {
            var gltfMaterial = new Material(gltfShader);
            var originalBase = new Color(0.18f, 0.31f, 0.47f, 1f);
            var originalEmission = new Color(0.02f, 0.03f, 0.04f, 1f);
            gltfMaterial.SetColor("baseColorFactor", originalBase);
            gltfMaterial.SetColor("emissiveFactor", originalEmission);
            generatedRenderer.material = gltfMaterial;

            var highlightColor = new Color(1f, 0.9f, 0.25f, 1f);
            binding.SetHighlighted(false, Color.clear, 0f);
            binding.SetHighlighted(true, highlightColor, 2f);
            Require(gltfMaterial.GetColor("baseColorFactor") == highlightColor,
                "glTFast baseColorFactor did not receive the highlight color.");
            Require(gltfMaterial.GetColor("emissiveFactor") == highlightColor * 2f,
                "glTFast emissiveFactor did not receive the highlight emission.");

            binding.SetHighlighted(false, Color.clear, 0f);
            Require(gltfMaterial.GetColor("baseColorFactor") == originalBase,
                "glTFast baseColorFactor was not restored after highlighting.");
            Require(gltfMaterial.GetColor("emissiveFactor") == originalEmission,
                "glTFast emissiveFactor was not restored after highlighting.");
            UnityEngine.Object.DestroyImmediate(gltfMaterial);
            generatedRenderer.material = originalMaterial;
        }

        UnityEngine.Object.DestroyImmediate(managerObject);
        UnityEngine.Object.DestroyImmediate(generated);
        UnityEngine.Object.DestroyImmediate(placeholder);
    }

    private static FunctionalMldsSceneObjectBinding CreateBoundCube(
        string objectName,
        string entityId,
        string sourceObjectId,
        string groupId,
        string zoneId,
        string[] synonyms,
        Vector3 position)
    {
        var gameObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
        gameObject.name = objectName;
        gameObject.transform.position = position;
        var binding = gameObject.AddComponent<FunctionalMldsSceneObjectBinding>();
        binding.Configure(
            entityId,
            sourceObjectId,
            groupId,
            zoneId,
            objectName,
            gameObject.GetComponent<Collider>(),
            synonyms);
        return binding;
    }

    private static void AddAgentVisual(
        QuickAgentManager manager,
        string agentId,
        GameObject agentObject)
    {
        var managerType = typeof(QuickAgentManager);
        var visualType = managerType.GetNestedType(
            "AgentVisual",
            BindingFlags.NonPublic);
        Require(visualType != null, "QuickAgentManager.AgentVisual type is missing.");
        var visual = Activator.CreateInstance(visualType, true);
        visualType.GetField("obj", BindingFlags.Instance | BindingFlags.Public)
            ?.SetValue(visual, agentObject);
        visualType.GetField("renderer", BindingFlags.Instance | BindingFlags.Public)
            ?.SetValue(visual, agentObject.GetComponent<Renderer>());

        var field = managerType.GetField(
            "agentObjects",
            BindingFlags.Instance | BindingFlags.NonPublic);
        Require(field != null, "QuickAgentManager.agentObjects field is missing.");
        var dictionary = field.GetValue(manager) as IDictionary;
        Require(dictionary != null, "QuickAgentManager.agentObjects is not an IDictionary.");
        dictionary.Add(agentId, visual);
    }

    private static List<GeneratedBindingState> CaptureGeneratedBindingStates()
    {
        var result = new List<GeneratedBindingState>();
        var bindings = Resources.FindObjectsOfTypeAll<FunctionalMldsSceneObjectBinding>();
        for (var i = 0; i < bindings.Length; i++)
        {
            var binding = bindings[i];
            if (binding != null && binding.GeneratedFromModel)
            {
                result.Add(new GeneratedBindingState
                {
                    Binding = binding,
                    Enabled = binding.enabled
                });
            }
        }
        return result;
    }

    private static void RestoreGeneratedBindingStates(
        IEnumerable<GeneratedBindingState> states)
    {
        foreach (var state in states)
        {
            if (state.Binding != null)
                state.Binding.enabled = state.Enabled;
        }
    }

    private static bool ContainsText(IEnumerable<string> values, string text)
    {
        foreach (var value in values)
        {
            if (value != null
                && value.IndexOf(text, StringComparison.OrdinalIgnoreCase) >= 0)
                return true;
        }
        return false;
    }

    private static void SetPrivate(object target, string fieldName, object value)
    {
        var field = target.GetType().GetField(
            fieldName,
            BindingFlags.Instance | BindingFlags.NonPublic);
        if (field == null)
            throw new MissingFieldException(target.GetType().Name, fieldName);
        field.SetValue(target, value);
    }

    private static void Require(bool condition, string message)
    {
        if (!condition)
            throw new Exception("[FunctionalMldsSpatialGroundingSmoke] " + message);
    }

    private sealed class GeneratedBindingState
    {
        public FunctionalMldsSceneObjectBinding Binding;
        public bool Enabled;
    }
}
