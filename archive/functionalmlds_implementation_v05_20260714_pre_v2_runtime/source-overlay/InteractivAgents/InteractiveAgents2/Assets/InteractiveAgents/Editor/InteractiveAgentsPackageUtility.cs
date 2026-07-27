using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class InteractiveAgentsPackageUtility
{
    private const string PackageRoot = "Assets/InteractiveAgents";
    private const string DocumentationPath = PackageRoot + "/Documentation/InteractiveAgentsImportGuide.md";
    private const string QuickAgentManagerPath = "Assets/Scripting/QuickAgentManager.cs";
    private const string ProjectManagerPath = "Assets/Scripting/ProjectManagerUI.cs";
    private const string ProjectWizardPath = "Assets/Scripting/ArrowProjectWizard.cs";
    private const string BestfitMldsPath = "Assets/Scripting/BestfitMLDS.json";
    private const string KlassenraumMldsPath = "Assets/Scripting/KlassenraumMLDS.json";
    private const string SteinpilzMldsPath = "Assets/Scripting/MLDSSteinpilz.json";
    private const string WebGlVoiceBridgePath = "Assets/Plugins/WebGL/WebGLVoiceBridge.jslib";
    private const string CharacterResourcesPath = "Assets/Resources/Characters";

    private static readonly string[] CorePackagePaths =
    {
        PackageRoot,
        QuickAgentManagerPath,
        ProjectManagerPath,
        ProjectWizardPath,
        BestfitMldsPath,
        KlassenraumMldsPath,
        SteinpilzMldsPath,
        WebGlVoiceBridgePath
    };

    private static readonly string[] OptionalCharacterPackagePaths =
    {
        CharacterResourcesPath
    };

    private static readonly RecommendedPackage[] RecommendedPackages =
    {
        new RecommendedPackage("com.unity.inputsystem", "Input System", "Optional keyboard/gamepad input path."),
        new RecommendedPackage("com.unity.xr.interaction.toolkit", "XR Interaction Toolkit", "Recommended for XR scenes."),
        new RecommendedPackage("com.de-panther.webxr", "WebXR Export", "Required for browser-based WebXR builds."),
        new RecommendedPackage("com.de-panther.webxr-interactions", "WebXR Interactions", "Recommended with WebXR.")
    };

    [MenuItem("Tools/Interactive Agents/Create Manager In Scene", false, 10)]
    private static void CreateManagerInScene()
    {
        var existing = FindExistingManager();
        if (existing != null)
        {
            Selection.activeGameObject = existing.gameObject;
            EditorGUIUtility.PingObject(existing.gameObject);
            EditorUtility.DisplayDialog("Interactive Agents", "A QuickAgentManager already exists in this scene.", "OK");
            return;
        }

        var managerObject = new GameObject("Interactive Agents Manager");
        Undo.RegisterCreatedObjectUndo(managerObject, "Create Interactive Agents Manager");
        var manager = managerObject.AddComponent<QuickAgentManager>();
        manager.backendBaseUrl = "http://127.0.0.1:8787";
        Selection.activeGameObject = managerObject;
        EditorGUIUtility.PingObject(managerObject);
        EditorUtility.SetDirty(managerObject);
        EditorSceneManager.MarkSceneDirty(managerObject.scene);
    }

    [MenuItem("Tools/Interactive Agents/Validate Installation", false, 20)]
    private static void ValidateInstallation()
    {
        var report = new StringBuilder();
        var missingRequired = new List<string>();

        foreach (var path in CorePackagePaths)
        {
            if (!AssetPathExists(path))
            {
                missingRequired.Add(path);
            }
        }

        report.AppendLine("Interactive Agents installation check");
        report.AppendLine();

        if (missingRequired.Count == 0)
        {
            report.AppendLine("Required package files: OK");
        }
        else
        {
            report.AppendLine("Missing required package files:");
            foreach (var path in missingRequired)
            {
                report.AppendLine("- " + path);
            }
        }

        report.AppendLine();
        report.AppendLine("Recommended Unity packages:");
        var manifestText = ReadManifestText();
        foreach (var package in RecommendedPackages)
        {
            var installed = manifestText.Contains("\"" + package.Id + "\"");
            report.AppendLine("- " + package.DisplayName + " (" + package.Id + "): " + (installed ? "installed" : "missing") + " - " + package.Note);
        }

        if (!manifestText.Contains("package.openupm.com"))
        {
            report.AppendLine();
            report.AppendLine("OpenUPM scoped registry is not configured. Add it before installing the WebXR packages.");
        }

        report.AppendLine();
        report.AppendLine(AssetPathExists(CharacterResourcesPath)
            ? "Character assets: included"
            : "Character assets: missing, runtime will use cube fallback avatars.");

        Debug.Log(report.ToString());
        EditorUtility.DisplayDialog("Interactive Agents", report.ToString(), "OK");
    }

    [MenuItem("Tools/Interactive Agents/Export/Core Unity Package", false, 100)]
    private static void ExportCorePackage()
    {
        ExportPackage("InteractiveAgents-Core", includeCharacters: false);
    }

    [MenuItem("Tools/Interactive Agents/Export/Core + Character Assets Unity Package", false, 101)]
    private static void ExportFullPackage()
    {
        ExportPackage("InteractiveAgents-WithCharacters", includeCharacters: true);
    }

    [MenuItem("Tools/Interactive Agents/Open Import Guide", false, 200)]
    private static void OpenImportGuide()
    {
        var guide = AssetDatabase.LoadAssetAtPath<TextAsset>(DocumentationPath);
        if (guide == null)
        {
            EditorUtility.DisplayDialog("Interactive Agents", "Import guide not found at " + DocumentationPath, "OK");
            return;
        }

        Selection.activeObject = guide;
        EditorGUIUtility.PingObject(guide);
        AssetDatabase.OpenAsset(guide);
    }

    private static void ExportPackage(string baseName, bool includeCharacters)
    {
        var exportPaths = new List<string>(CorePackagePaths);
        if (includeCharacters)
        {
            exportPaths.AddRange(OptionalCharacterPackagePaths);
        }

        var existingPaths = new List<string>();
        var missingPaths = new List<string>();
        foreach (var path in exportPaths)
        {
            if (AssetPathExists(path))
            {
                existingPaths.Add(path);
            }
            else
            {
                missingPaths.Add(path);
            }
        }

        if (missingPaths.Count > 0)
        {
            var message = "Some package paths are missing and will not be exported:\n\n" + string.Join("\n", missingPaths);
            if (!EditorUtility.DisplayDialog("Interactive Agents Export", message, "Export anyway", "Cancel"))
            {
                return;
            }
        }

        if (existingPaths.Count == 0)
        {
            EditorUtility.DisplayDialog("Interactive Agents Export", "No package paths found.", "OK");
            return;
        }

        var defaultDirectory = GetDefaultExportDirectory();
        var defaultFileName = baseName + "-" + System.DateTime.Now.ToString("yyyyMMdd-HHmm") + ".unitypackage";
        var targetPath = EditorUtility.SaveFilePanel("Export Interactive Agents package", defaultDirectory, defaultFileName, "unitypackage");
        if (string.IsNullOrEmpty(targetPath))
        {
            return;
        }

        AssetDatabase.ExportPackage(existingPaths.ToArray(), targetPath, ExportPackageOptions.Recurse);
        EditorUtility.DisplayDialog("Interactive Agents Export", "Package exported:\n" + targetPath, "OK");
    }

    private static string GetDefaultExportDirectory()
    {
        var projectRoot = Directory.GetParent(Application.dataPath).FullName;
        var exportDirectory = Path.Combine(projectRoot, "ExportedPackages");
        Directory.CreateDirectory(exportDirectory);
        return exportDirectory;
    }

    private static bool AssetPathExists(string assetPath)
    {
        if (AssetDatabase.IsValidFolder(assetPath)
            || AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(assetPath) != null)
        {
            return true;
        }

        var projectRoot = Directory.GetParent(Application.dataPath).FullName;
        var absolutePath = Path.Combine(projectRoot, assetPath.Replace('/', Path.DirectorySeparatorChar));
        return File.Exists(absolutePath) || Directory.Exists(absolutePath);
    }

    private static string ReadManifestText()
    {
        var projectRoot = Directory.GetParent(Application.dataPath).FullName;
        var manifestPath = Path.Combine(projectRoot, "Packages", "manifest.json");
        return File.Exists(manifestPath) ? File.ReadAllText(manifestPath) : string.Empty;
    }

    private static QuickAgentManager FindExistingManager()
    {
#if UNITY_2023_1_OR_NEWER
        return Object.FindAnyObjectByType<QuickAgentManager>();
#else
        return Object.FindObjectOfType<QuickAgentManager>();
#endif
    }

    private readonly struct RecommendedPackage
    {
        public readonly string Id;
        public readonly string DisplayName;
        public readonly string Note;

        public RecommendedPackage(string id, string displayName, string note)
        {
            Id = id;
            DisplayName = displayName;
            Note = note;
        }
    }
}
