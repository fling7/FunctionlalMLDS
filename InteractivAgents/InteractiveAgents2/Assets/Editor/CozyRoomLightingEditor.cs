using Assets;
using Newtonsoft.Json;
using SceneData2 = Assets.Json_Files.SceneData2;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

[InitializeOnLoad]
public static class CozyRoomLightingEditor
{
    static CozyRoomLightingEditor()
    {
        EditorApplication.delayCall += ApplyAfterReload;
    }

    [MenuItem("GameObject/Dev Tools/Apply Cozy Room Lighting", false, 52)]
    public static void ApplyToOpenScene()
    {
        Scene scene = SceneManager.GetActiveScene();
        if (!scene.IsValid() || !scene.isLoaded) return;

        Visualizer visualizer = Object.FindFirstObjectByType<Visualizer>();
        JulangEnvironment environment = visualizer != null && visualizer.gameObject.scene == scene
            ? ResolveEnvironment(visualizer)
            : null;
        if (!CozyRoomLighting.ApplyToScene(scene, environment)) return;
        EditorSceneManager.MarkSceneDirty(scene);
        SceneView.RepaintAll();
        Debug.Log("[LIGHTING] Warme Grundbeleuchtung, Lightstripes und Pendelleuchten aktualisiert.");
    }

    private static void ApplyAfterReload()
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode) return;
        Scene scene = SceneManager.GetActiveScene();
        if (!scene.IsValid() || !scene.isLoaded) return;
        Visualizer visualizer = Object.FindFirstObjectByType<Visualizer>();
        if (visualizer == null || visualizer.gameObject.scene != scene) return;
        if (HasCompleteLighting(scene)) return;
        ApplyToOpenScene();
    }

    private static bool HasCompleteLighting(Scene scene)
    {
        Transform[] transforms = Object.FindObjectsByType<Transform>(
            FindObjectsInactive.Include, FindObjectsSortMode.None);
        int stripCount = 0;
        int pendantCount = 0;
        int expectedShadeCount = 0;
        GameObject lightingRoot = null;
        foreach (Transform item in transforms)
        {
            if (item == null || item.gameObject.scene != scene) continue;
            if (item.parent == null && item.name == CozyRoomLighting.LightingRootName)
            {
                lightingRoot = item.gameObject;
            }
            if (IsOwnedLightingTransform(item)) continue;
            string key = item.name.ToLowerInvariant();
            if (key.Contains("_cache_") || HasHexAssetSuffix(key)) continue;
            if (key.Contains("longitudinal_light_strip") || key.Contains("linear_light_fixture"))
            {
                stripCount++;
            }
            else if (key.Contains("pendant_lamp") || key.Contains("pendant_light"))
            {
                pendantCount++;
                if (key.Contains("counter_pendant")) expectedShadeCount += 4;
                else if (key.Contains("lounge_pendant")) expectedShadeCount += 3;
                else if (key.Contains("cluster")) expectedShadeCount += 3;
                else expectedShadeCount++;
            }
        }

        CozyRoomLightingProfileState state = lightingRoot != null
            ? lightingRoot.GetComponent<CozyRoomLightingProfileState>()
            : null;
        if (state == null || state.ProfileVersion != CozyRoomLighting.ProfileVersion)
        {
            return false;
        }

        int expectedEnabledLights = 1 + stripCount * 2 + pendantCount;
        int actualEnabledLights = 0;
        int actualStripDiffusers = 0;
        int actualShadeGlows = 0;
        foreach (MeshRenderer renderer in Object.FindObjectsByType<MeshRenderer>(
                     FindObjectsInactive.Include, FindObjectsSortMode.None))
        {
            if (renderer == null || !renderer.enabled || !renderer.gameObject.activeInHierarchy ||
                renderer.gameObject.scene != scene ||
                !IsOwnedLightingTransform(renderer.transform))
            {
                continue;
            }
            if (!IsVisiblyEmissive(renderer)) continue;
            if (renderer.name == "Full_Length_Emissive_Diffuser") actualStripDiffusers++;
            else if (renderer.name.StartsWith("Shade_Glow_")) actualShadeGlows++;
        }

        foreach (Light light in Object.FindObjectsByType<Light>(
                     FindObjectsInactive.Include, FindObjectsSortMode.None))
        {
            if (light == null || !light.enabled || !light.gameObject.activeInHierarchy ||
                light.gameObject.scene != scene) continue;
            Transform current = light.transform;
            while (current != null)
            {
                if (current.name == CozyRoomLighting.LightingRootName ||
                    current.name == CozyRoomLighting.FixtureRigName)
                {
                    actualEnabledLights++;
                    break;
                }
                current = current.parent;
            }
        }

        return stripCount + pendantCount > 0 &&
               actualEnabledLights == expectedEnabledLights &&
               actualStripDiffusers == stripCount &&
               actualShadeGlows == expectedShadeCount;
    }

    private static JulangEnvironment ResolveEnvironment(Visualizer visualizer)
    {
        if (visualizer == null) return null;
        JulangEnvironment environment = visualizer.Converter.Environment;
        if (environment != null) return environment;
        if (visualizer.JsonFile == null || string.IsNullOrWhiteSpace(visualizer.JsonFile.text))
        {
            return null;
        }

        try
        {
            string json = visualizer.JsonFile.text.Trim('\uFEFF', ' ', '\r', '\n', '\t');
            if (json.StartsWith("\"") && json.EndsWith("\""))
            {
                json = JsonConvert.DeserializeObject<string>(json)
                    ?.Trim('\uFEFF', ' ', '\r', '\n', '\t') ?? string.Empty;
            }
            SceneData2 data = JsonConvert.DeserializeObject<SceneData2>(json);
            return data?.Scene?.Environment != null
                ? new JulangEnvironment(data.Scene.Environment)
                : null;
        }
        catch (System.Exception exception)
        {
            Debug.LogWarning($"[LIGHTING] MLDS-Lichtprofil konnte nicht gelesen werden: {exception.Message}");
            return null;
        }
    }

    private static bool IsOwnedLightingTransform(Transform item)
    {
        return CozyRoomLighting.IsOwnedLightingTransform(item);
    }

    private static bool IsVisiblyEmissive(Renderer renderer)
    {
        foreach (Material material in renderer.sharedMaterials)
        {
            if (material == null || !material.HasProperty("_EmissionColor") ||
                !material.IsKeywordEnabled("_EMISSION"))
            {
                continue;
            }
            if (material.GetColor("_EmissionColor").maxColorComponent > 1f)
            {
                return true;
            }
        }
        return false;
    }

    private static bool HasHexAssetSuffix(string objectName)
    {
        int separator = objectName.LastIndexOf('_');
        if (separator < 0 || objectName.Length - separator - 1 != 32) return false;
        for (int index = separator + 1; index < objectName.Length; index++)
        {
            char value = objectName[index];
            if (!((value >= '0' && value <= '9') || (value >= 'a' && value <= 'f')))
            {
                return false;
            }
        }
        return true;
    }
}
