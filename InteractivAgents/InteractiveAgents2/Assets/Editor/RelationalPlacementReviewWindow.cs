using System;
using System.IO;
using System.Linq;
using Assets;
using UnityEditor;
using UnityEngine;

namespace Assets.EditorTools
{
    public class RelationalPlacementReviewWindow : EditorWindow
    {
        private const string TestFolderAssetPath = "Assets/Json_Tests";
        private const string GeneratedFolderAssetPath = "Assets/Json_Tests/GPT_Tests";
        private const string RepairedReviewFolderAssetPath = "Assets/Json_Tests/Repaired_Review";

        private static readonly ReviewScene[] ReviewScenes =
        {
            new ReviewScene(
                "Classic flat regression",
                "Assets/Json_Tests/ClassicFlatRegressionTest.json",
                "Classic path: all objects stay top-level; no children or relativePositioning should be needed."),
            new ReviewScene(
                "Relational table, wall, ceiling",
                "Assets/Json_Tests/RelationalPlacementTest.json",
                "Mixed relations: table items on top, wall display attached to wall, ceiling spots below ceiling."),
            new ReviewScene(
                "Relational podium products",
                "Assets/Json_Tests/RelationalPodiumProductTest.json",
                "Multiple product models should sit on one podium and spread out through X/Z offsets."),
            new ReviewScene(
                "Relational nested hierarchy",
                "Assets/Json_Tests/RelationalNestedParentChildTest.json",
                "Nested parent/child/child placement should preserve tray, artifact, and label hierarchy.")
        };

        private static readonly ReviewScene[] RepairedReviewScenes =
        {
            new ReviewScene(
                "Repaired classic flat regression",
                "Assets/Json_Tests/Repaired_Review/ClassicFlatRegressionTest_Repaired.json",
                "Same classic regression scene after deterministic geometry repair; expected to load without object overlaps."),
            new ReviewScene(
                "Repaired relational table, wall, ceiling",
                "Assets/Json_Tests/Repaired_Review/RelationalPlacementTest_Repaired.json",
                "Same relational table/wall/ceiling scene after repair; children should still stay attached to their parents."),
            new ReviewScene(
                "Repaired relational podium products",
                "Assets/Json_Tests/Repaired_Review/RelationalPodiumProductTest_Repaired.json",
                "Same podium product relation test after repair; product children should remain distributed on the podium."),
            new ReviewScene(
                "Repaired relational nested hierarchy",
                "Assets/Json_Tests/Repaired_Review/RelationalNestedParentChildTest_Repaired.json",
                "Same nested hierarchy after repair; tray, artifact, and label hierarchy should remain intact."),
            new ReviewScene(
                "Repaired generated relational comparison",
                "Assets/Json_Tests/Repaired_Review/comparison_2026-06-19_18-22-46_relational_Repaired.json",
                "Latest saved relational comparison rerun through the current geometry repair logic.")
        };

        private bool clearPreviousSpawn = true;
        private bool checkCollisionAfterLoad;
        private Vector2 scrollPosition;
        private string lastLoaded = "None";

        [MenuItem("Tools/Relational Placement/Review Tests")]
        public static void Open()
        {
            RelationalPlacementReviewWindow window = GetWindow<RelationalPlacementReviewWindow>("Placement Review");
            window.minSize = new Vector2(520, 360);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("Relational Placement Review", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Last loaded", lastLoaded);

            clearPreviousSpawn = EditorGUILayout.ToggleLeft("Clear previous spawned objects before loading", clearPreviousSpawn);
            checkCollisionAfterLoad = EditorGUILayout.ToggleLeft("Highlight collisions after loading", checkCollisionAfterLoad);

            EditorGUILayout.Space(8);
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);

            foreach (ReviewScene scene in ReviewScenes)
            {
                DrawReviewScene(scene);
            }

            EditorGUILayout.Space(8);
            EditorGUILayout.LabelField("Repaired review scenes", EditorStyles.boldLabel);
            foreach (ReviewScene scene in RepairedReviewScenes)
            {
                DrawReviewScene(scene);
            }

            EditorGUILayout.Space(8);
            DrawGeneratedSceneControls();

            EditorGUILayout.Space(8);
            DrawUtilityButtons();

            EditorGUILayout.EndScrollView();
        }

        private void DrawReviewScene(ReviewScene scene)
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField(scene.Label, EditorStyles.boldLabel);
            EditorGUILayout.LabelField(scene.AssetPath, EditorStyles.miniLabel);
            EditorGUILayout.HelpBox(scene.ExpectedResult, MessageType.None);

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Load"))
            {
                LoadScene(scene);
            }
            if (GUILayout.Button("Ping JSON", GUILayout.Width(90)))
            {
                PingAsset(scene.AssetPath);
            }
            if (GUILayout.Button("Copy Feedback", GUILayout.Width(110)))
            {
                CopyFeedbackTemplate(scene);
            }
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.EndVertical();
        }

        private void DrawGeneratedSceneControls()
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("Generated pipeline output", EditorStyles.boldLabel);
            EditorGUILayout.LabelField(GeneratedFolderAssetPath, EditorStyles.miniLabel);

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Load latest generated JSON"))
            {
                LoadLatestGeneratedScene("*.json", "Latest generated JSON");
            }
            if (GUILayout.Button("Open Folder", GUILayout.Width(100)))
            {
                RevealFolder(GeneratedFolderAssetPath);
            }
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Load latest classic comparison"))
            {
                LoadLatestGeneratedScene("comparison_*_classic.json", "Latest classic comparison");
            }
            if (GUILayout.Button("Load latest relational comparison"))
            {
                LoadLatestGeneratedScene("comparison_*_relational.json", "Latest relational comparison");
            }
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.EndVertical();
        }

        private static void DrawUtilityButtons()
        {
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Open Test Folder"))
            {
                RevealFolder(TestFolderAssetPath);
            }
            if (GUILayout.Button("Open Repaired"))
            {
                RevealFolder(RepairedReviewFolderAssetPath);
            }
            if (GUILayout.Button("Clear Last Spawned"))
            {
                Visualizer.Instance.Delete(false);
            }
            if (GUILayout.Button("Open Chat"))
            {
                ChatWindow.OpenWindow();
            }
            EditorGUILayout.EndHorizontal();
        }

        private void LoadScene(ReviewScene scene)
        {
            string fullPath = AssetPathToFullPath(scene.AssetPath);
            if (!File.Exists(fullPath))
            {
                EditorUtility.DisplayDialog("Placement Review", $"JSON file not found:\n{fullPath}", "OK");
                return;
            }

            LoadJson(fullPath, scene.Label);
        }

        private void LoadLatestGeneratedScene(string searchPattern, string label)
        {
            string folderPath = AssetPathToFullPath(GeneratedFolderAssetPath);
            if (!Directory.Exists(folderPath))
            {
                EditorUtility.DisplayDialog("Placement Review", $"Folder not found:\n{folderPath}", "OK");
                return;
            }

            string newestFile = Directory.GetFiles(folderPath, searchPattern)
                .Where(IsSceneJsonCandidate)
                .OrderByDescending(File.GetLastWriteTimeUtc)
                .FirstOrDefault();

            if (string.IsNullOrEmpty(newestFile))
            {
                EditorUtility.DisplayDialog("Placement Review", $"No generated JSON files found for {searchPattern}.", "OK");
                return;
            }

            LoadJson(newestFile, $"{label}: {Path.GetFileName(newestFile)}");
        }

        private void LoadJson(string fullPath, string label)
        {
            if (clearPreviousSpawn)
            {
                Visualizer.Instance.Delete(false);
            }

            bool previousCollisionSetting = Visualizer.Instance.ShouldCheckCollision;
            Visualizer.Instance.ShouldCheckCollision = checkCollisionAfterLoad;

            try
            {
                Visualizer.Instance.DoVisualize(File.ReadAllText(fullPath));
                lastLoaded = label;
                Selection.activeGameObject = Visualizer.Instance.gameObject;
                SceneView.RepaintAll();
                EditorApplication.QueuePlayerLoopUpdate();
                Debug.Log($"[Placement Review] Loaded {label}: {fullPath}");
            }
            catch (Exception ex)
            {
                Debug.LogException(ex);
                EditorUtility.DisplayDialog("Placement Review", $"Could not load scene:\n{ex.Message}", "OK");
            }
            finally
            {
                Visualizer.Instance.ShouldCheckCollision = previousCollisionSetting;
            }
        }

        private static void PingAsset(string assetPath)
        {
            UnityEngine.Object asset = AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(assetPath);
            if (asset == null)
            {
                EditorUtility.DisplayDialog("Placement Review", $"Asset not found:\n{assetPath}", "OK");
                return;
            }

            EditorGUIUtility.PingObject(asset);
            Selection.activeObject = asset;
        }

        private static void CopyFeedbackTemplate(ReviewScene scene)
        {
            GUIUtility.systemCopyBuffer =
                $"Scene: {scene.Label}\n" +
                "Objects touch the expected surfaces: yes/no\n" +
                "Offsets distribute repeated objects clearly: yes/no\n" +
                "Unexpected floating/sinking: yes/no, where?\n" +
                "Unexpected collisions/overlaps: yes/no, where?\n" +
                "Notes:\n";
        }

        private static void RevealFolder(string assetFolderPath)
        {
            string fullPath = AssetPathToFullPath(assetFolderPath);
            Directory.CreateDirectory(fullPath);
            EditorUtility.RevealInFinder(fullPath);
        }

        private static bool IsSceneJsonCandidate(string fullPath)
        {
            string fileName = Path.GetFileName(fullPath);
            return !fileName.EndsWith("_summary.json", StringComparison.OrdinalIgnoreCase);
        }

        private static string AssetPathToFullPath(string assetPath)
        {
            string normalized = assetPath.Replace('\\', '/');
            if (normalized == "Assets")
            {
                return Application.dataPath;
            }

            if (normalized.StartsWith("Assets/"))
            {
                string relativeToAssets = normalized.Substring("Assets/".Length)
                    .Replace('/', Path.DirectorySeparatorChar);
                return Path.Combine(Application.dataPath, relativeToAssets);
            }

            return Path.GetFullPath(assetPath);
        }

        private readonly struct ReviewScene
        {
            public ReviewScene(string label, string assetPath, string expectedResult)
            {
                Label = label;
                AssetPath = assetPath;
                ExpectedResult = expectedResult;
            }

            public string Label { get; }
            public string AssetPath { get; }
            public string ExpectedResult { get; }
        }
    }
}
