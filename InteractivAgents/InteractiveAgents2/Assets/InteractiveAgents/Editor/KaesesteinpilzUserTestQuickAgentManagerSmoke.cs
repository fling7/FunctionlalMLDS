using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>Deterministic contract smoke for the participant-facing KAESESTEINPILZ runtime.</summary>
public static class KaesesteinpilzUserTestQuickAgentManagerSmoke
{
    private sealed class HandoffProbeEnumerator : IEnumerator
    {
        private readonly QuickAgentManager core;
        private readonly FieldInfo fpvField;

        public HandoffProbeEnumerator(QuickAgentManager core, FieldInfo fpvField)
        {
            this.core = core;
            this.fpvField = fpvField;
        }

        public bool SawArmedFpv { get; private set; }
        public object Current => null;
        public bool MoveNext()
        {
            SawArmedFpv = (bool)fpvField.GetValue(core);
            return false;
        }
        public void Reset() { }
    }

    private const string LegacyManagerSha256 =
        "979D30117532422E05BE37032C63B205BE0E11E7C8C84B1EE37798C49E48F067";
    private const string MenuPath = "Tools/Interactive Agents/Run KAESESTEINPILZ User-Test Smoke";

    [MenuItem(MenuPath)]
    public static void Run()
    {
        RequireLegacyManagerUnchanged();
        RequireBuildAndSceneContract();
        RequireBackendResolutionContract();
        RequireMobileSelectionContract();
        RequireParticipantTranscriptContract();
        RequireHandoffNavigationContract();
        RequireAnimationAssets();
        RequireWebXrTemplate();
        Debug.Log("[KaesesteinpilzUserTestQuickAgentManagerSmoke] OK");
    }

    public static void RunFromCommandLine()
    {
        try
        {
            Run();
            EditorApplication.Exit(0);
        }
        catch (Exception exception)
        {
            Debug.LogException(exception);
            EditorApplication.Exit(1);
        }
    }

    private static void RequireLegacyManagerUnchanged()
    {
        const string path = "Assets/Scripting/QuickAgentManager.cs";
        Require(File.Exists(path), "QuickAgentManager.cs is missing.");
        using (var stream = File.OpenRead(path))
        using (var sha = SHA256.Create())
        {
            var actual = BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "");
            Require(string.Equals(actual, LegacyManagerSha256, StringComparison.Ordinal),
                "The legacy QuickAgentManager changed; the user-test component must remain separate. " + actual);
        }

        const BindingFlags flags = BindingFlags.Instance | BindingFlags.NonPublic;
        Require(typeof(QuickAgentManager).GetField("selectedProjectId", flags) != null,
            "The expected project-selection field is missing.");
        Require(typeof(QuickAgentManager).GetMethod("SetupFromServer", flags) != null,
            "The expected setup coroutine is missing.");
        Require(typeof(QuickAgentManager).GetMethod(
                "SendChat", flags, null, new[] { typeof(string) }, null) != null,
            "The expected chat coroutine is missing.");
    }

    private static void RequireBuildAndSceneContract()
    {
        var enabledScenes = EditorBuildSettings.scenes.Where(scene => scene.enabled).ToArray();
        Require(enabledScenes.Length == 1,
            "The study build must contain exactly one enabled scene.");
        Require(string.Equals(
                enabledScenes[0].path,
                KaesesteinpilzUserTestQuickAgentManager.StudyScenePath,
                StringComparison.Ordinal),
            "The enabled build scene is not KAESESTEINPILZ SampleScene.");

        var scene = EditorSceneManager.OpenScene(
            KaesesteinpilzUserTestQuickAgentManager.StudyScenePath,
            OpenSceneMode.Single);
        Require(scene.IsValid(), "KAESESTEINPILZ scene could not be opened.");

        var managers = UnityEngine.Object.FindObjectsByType<KaesesteinpilzUserTestQuickAgentManager>(
            FindObjectsInactive.Include, FindObjectsSortMode.None);
        Require(managers.Length == 1,
            "The scene must contain exactly one KAESESTEINPILZ user-test manager.");
        var study = managers[0];
        var core = study.GetComponent<QuickAgentManager>();
        Require(core != null && study.CoreManager == core,
            "The new component must compose the existing manager on AGENTSPAWNER.");
        Require(core.enabled && study.enabled,
            "Both the communication core and the study component must be enabled.");
        var serializedStudy = new SerializedObject(study);
        Require(serializedStudy.FindProperty("autoEnterFlatFpv")?.boolValue == true,
            "Flat-screen participants must enter FPV automatically.");
        Require(study.SelectedFlatControlMode
                == KaesesteinpilzUserTestQuickAgentManager.FlatControlMode.Computer,
            "The flat control mode must start in an explicit, stable computer mode.");

        study.ConfigureCoreForStudy();
        Require(string.Equals(core.memoryMode, KaesesteinpilzUserTestQuickAgentManager.StudyMemoryMode,
                StringComparison.Ordinal),
            "Shared knowledge is not enforced.");
        Require(string.Equals(core.animationResourceFolder,
                KaesesteinpilzUserTestQuickAgentManager.SafeAnimationFolder,
                StringComparison.Ordinal),
            "The safe dedicated animation folder is not enforced.");
        Require(!core.showUi && !core.showAgentBubbles && !core.enableFreeMovement
                && !core.enableVoiceInput && !core.sendVoiceTranscriptAutomatically,
            "The legacy participant UI/input must be disabled by the new component.");
        Require(!core.enableSpatialTargetSelection && core.fpvToggleKey == KeyCode.None,
            "Legacy global pointer/FPV input must be owned by the new component.");

        var selectedProject = typeof(QuickAgentManager)
            .GetField("selectedProjectId", BindingFlags.Instance | BindingFlags.NonPublic)
            ?.GetValue(core) as string;
        Require(string.Equals(selectedProject,
                KaesesteinpilzUserTestQuickAgentManager.StudyProjectId,
                StringComparison.Ordinal),
            "The KAESESTEINPILZ project is not pinned.");
    }

    private static void RequireBackendResolutionContract()
    {
        var desktop = KaesesteinpilzUserTestQuickAgentManager.ResolveBackendBaseUrl(
            "http://127.0.0.1:8787/", "", "", false);
        Require(desktop == "http://127.0.0.1:8787", "Desktop backend normalization failed.");

        var sameOrigin = KaesesteinpilzUserTestQuickAgentManager.ResolveBackendBaseUrl(
            "", "", "https://study.example/iui/index.html", true);
        Require(sameOrigin == "https://study.example/api",
            "WebGL must default to a secure same-origin /api endpoint.");

        var localWebGl = KaesesteinpilzUserTestQuickAgentManager.ResolveBackendBaseUrl(
            "http://127.0.0.1:8787", "", "http://localhost:8000/index.html", true);
        Require(localWebGl == "http://127.0.0.1:8787",
            "Local WebGL must connect to the configured local backend instead of an absent /api proxy.");

        var queryOverride = KaesesteinpilzUserTestQuickAgentManager.ResolveBackendBaseUrl(
            "", "", "https://study.example/?backend=https%3A%2F%2Fapi.example%2Fv1", true);
        Require(queryOverride == "https://api.example/v1",
            "The explicit WebGL backend query override failed.");
    }

    private static void RequireMobileSelectionContract()
    {
        var manager = UnityEngine.Object.FindFirstObjectByType<
            KaesesteinpilzUserTestQuickAgentManager>();
        Require(manager != null, "The study manager is unavailable for mobile selection smoke.");

        const BindingFlags flags = BindingFlags.Instance | BindingFlags.NonPublic;
        var modeField = typeof(KaesesteinpilzUserTestQuickAgentManager).GetField(
            "flatControlMode", flags);
        var modalityMethod = typeof(KaesesteinpilzUserTestQuickAgentManager).GetMethod(
            "CurrentRayModality", flags);
        Require(modeField != null && modalityMethod != null,
            "The explicit mobile modality contract is missing.");

        var previous = modeField.GetValue(manager);
        try
        {
            modeField.SetValue(
                manager,
                KaesesteinpilzUserTestQuickAgentManager.FlatControlMode.Smartphone);
            var modality = modalityMethod.Invoke(manager, null) as string;
            Require(string.Equals(modality, "touch", StringComparison.Ordinal),
                "Smartphone selection must emit the normative V2 'touch' modality.");
        }
        finally
        {
            modeField.SetValue(manager, previous);
        }
    }

    private static void RequireParticipantTranscriptContract()
    {
        var extractor = typeof(KaesesteinpilzUserTestQuickAgentManager).GetMethod(
            "ExtractParticipantReply",
            BindingFlags.Static | BindingFlags.NonPublic);
        Require(extractor != null, "The participant transcript extractor is missing.");

        var screenshotCase = extractor.Invoke(null, new object[]
        {
            "{\"response\":\"Herzlich willkommen! Du bist jetzt am Empfang.\"}"
        }) as string;
        Require(screenshotCase == "Herzlich willkommen! Du bist jetzt am Empfang.",
            "The backend response field is displayed as raw JSON.");

        var nestedCase = extractor.Invoke(null, new object[]
        {
            "```json\n{\"result\":{\"message\":\"Vollständige Antwort\"}}\n```"
        }) as string;
        Require(nestedCase == "Vollständige Antwort",
            "Nested/fenced response JSON is not normalized.");
    }

    private static void RequireHandoffNavigationContract()
    {
        const BindingFlags flags = BindingFlags.Instance | BindingFlags.NonPublic;
        var managerType = typeof(KaesesteinpilzUserTestQuickAgentManager);
        Require(managerType.GetMethod("RunCoreChatWithHandoffNavigation", flags) != null,
            "Study chat does not arm the original proximity-handoff branch.");
        Require(managerType.GetMethod("UpdatePendingHandoffNavigation", flags) != null,
            "Study runtime has no pending-handoff arrival/navigation driver.");
        Require(managerType.GetField("handoffIndicator", flags) != null,
            "Study runtime has no participant-facing handoff arrow.");

        var coreType = typeof(QuickAgentManager);
        var fpvField = coreType.GetField("_fpvActive", flags);
        Require(coreType.GetField("_pendingHandoffAgentId", flags) != null
                && coreType.GetMethod("TriggerPendingHandoffArrival", flags) != null,
            "The composed communication core no longer exposes the expected handoff state.");

        var manager = UnityEngine.Object.FindAnyObjectByType<
            KaesesteinpilzUserTestQuickAgentManager>();
        Require(manager != null && fpvField != null,
            "Handoff coroutine probe cannot access the study manager/core.");
        var core = manager.CoreManager;
        fpvField.SetValue(core, false);
        var probe = new HandoffProbeEnumerator(core, fpvField);
        var wrapper = (IEnumerator)managerType.GetMethod(
            "RunCoreChatWithHandoffNavigation", flags).Invoke(manager, new object[] { probe });
        Require(!wrapper.MoveNext() && probe.SawArmedFpv && !(bool)fpvField.GetValue(core),
            "The legacy proximity branch is not armed atomically around chat processing.");
    }

    private static void RequireAnimationAssets()
    {
        var clipPaths = AssetDatabase.FindAssets(
                "t:AnimationClip",
                new[] { "Assets/Resources/Characters/Animations" })
            .Select(AssetDatabase.GUIDToAssetPath)
            .Distinct()
            .ToArray();
        var clips = new List<AnimationClip>();
        foreach (var path in clipPaths)
        {
            clips.AddRange(AssetDatabase.LoadAllAssetsAtPath(path)
                .OfType<AnimationClip>()
                .Where(clip => !clip.name.StartsWith("__preview__", StringComparison.Ordinal)));
        }
        Require(clips.Count >= 6, "Fewer than six dedicated idle clips are available.");
        foreach (var clip in clips)
        {
            Require(!clip.legacy && clip.isHumanMotion && clip.length > 0.1f,
                "Unsafe animation clip: " + clip.name);
            Require(clip.isLooping, "Study idle clip is not looping: " + clip.name);
        }

        var characterPaths = AssetDatabase.FindAssets(
                "t:GameObject",
                new[] { "Assets/Resources/Characters" })
            .Select(AssetDatabase.GUIDToAssetPath)
            .Where(path => !path.Contains("/Animations/"))
            .Where(path => !Path.GetFileNameWithoutExtension(path).Contains("@"))
            .Distinct()
            .ToArray();
        Require(characterPaths.Length >= 5, "Expected humanoid character assets are missing.");
        foreach (var path in characterPaths)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null || prefab.GetComponentInChildren<SkinnedMeshRenderer>(true) == null)
                continue;
            var animator = prefab.GetComponentInChildren<Animator>(true);
            Require(animator != null && animator.avatar != null
                    && animator.avatar.isHuman && animator.avatar.isValid,
                "Character has no valid Humanoid avatar: " + path);
        }
    }

    private static void RequireWebXrTemplate()
    {
        Require(PlayerSettings.WebGL.template == "PROJECT:WebXRFullView2020",
            "The WebXR Full View template is not selected.");
        Require(File.Exists("Assets/WebGLTemplates/WebXRFullView2020/index.html"),
            "The WebXR template entry point is missing.");
        Require(File.Exists("Assets/WebGLTemplates/WebXRFullView2020/TemplateData/style.css"),
            "The responsive WebXR template styling is missing.");
        var template = File.ReadAllText("Assets/WebGLTemplates/WebXRFullView2020/index.html");
        Require(template.Contains("id=\"entervr\"")
                && template.Contains("Module.WebXR.toggleVR()")
                && template.Contains("Module.WebXR.toggleAR()"),
            "The browser user-gesture controls for WebXR are incomplete.");
        var link = File.ReadAllText("Assets/link.xml");
        Require(link.Contains("QuickAgentManager")
                && link.Contains("WebXR.WebXRManager")
                && link.Contains("WebXR.InputSystem.WebXRInputSystem")
                && link.Contains("WebXR.InputSystem.WebXRController"),
            "IL2CPP reflection preservation is incomplete.");
    }

    private static void Require(bool condition, string message)
    {
        if (!condition)
            throw new InvalidOperationException(message);
    }
}
