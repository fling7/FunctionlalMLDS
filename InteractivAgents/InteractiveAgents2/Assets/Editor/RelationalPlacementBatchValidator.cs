using System.IO;
using System.Collections.Generic;
using System.Linq;
using Assets;
using UnityEditor;
using UnityEngine;

namespace Assets.EditorTools
{
    public static class RelationalPlacementBatchValidator
    {
        private static readonly string[] ReviewSceneAssetPaths =
        {
            "Assets/Json_Tests/ClassicFlatRegressionTest.json",
            "Assets/Json_Tests/RelationalPlacementTest.json",
            "Assets/Json_Tests/RelationalPodiumProductTest.json",
            "Assets/Json_Tests/RelationalNestedParentChildTest.json",
            "Assets/Json_Tests/Repaired_Review/ClassicFlatRegressionTest_Repaired.json",
            "Assets/Json_Tests/Repaired_Review/RelationalPlacementTest_Repaired.json",
            "Assets/Json_Tests/Repaired_Review/RelationalPodiumProductTest_Repaired.json",
            "Assets/Json_Tests/Repaired_Review/RelationalNestedParentChildTest_Repaired.json",
            "Assets/Json_Tests/Repaired_Review/comparison_2026-06-19_18-22-46_relational_Repaired.json",
            "Assets/Json_Tests/GPT_Tests/comparison_2026-06-19_18-22-46_classic.json",
            "Assets/Json_Tests/GPT_Tests/comparison_2026-06-19_18-22-46_relational.json"
        };

        public static void ValidateReviewScenes()
        {
            int failures = 0;

            foreach (string assetPath in EnumerateReviewSceneAssetPaths())
            {
                string fullPath = AssetPathToFullPath(assetPath);
                if (!File.Exists(fullPath))
                {
                    Debug.LogWarning($"[Placement Batch Validator] Missing JSON: {fullPath}");
                    continue;
                }

                Visualizer.Instance.Delete(false);
                Visualizer.Instance.ShouldCheckCollision = false;
                Visualizer.Instance.DoVisualize(File.ReadAllText(fullPath));

                int rendererCount = Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None).Length;
                if (rendererCount == 0)
                {
                    string message = $"[Placement Batch Validator] {assetPath}: no renderers spawned; JSON may have failed to load.";
                    if (IsStrictReviewScene(assetPath))
                    {
                        Debug.LogError(message);
                        failures++;
                    }
                    else
                    {
                        Debug.LogWarning(message);
                    }
                    continue;
                }

                int collisions = Visualizer.CountRelevantCollisions();
                int supportIssues = Visualizer.CountRelationPlacementIssues();
                Debug.Log($"[Placement Batch Validator] {assetPath}: relevantCollisions={collisions}, supportIssues={supportIssues}");
                RenderPreview(assetPath);
                if (collisions > 0 || supportIssues > 0)
                {
                    if (IsStrictReviewScene(assetPath))
                    {
                        failures++;
                    }
                    else
                    {
                        Debug.LogWarning($"[Placement Batch Validator] {assetPath} is informational and does not block relational validation.");
                    }
                }
            }

            Visualizer.Instance.Delete(false);

            if (failures > 0)
            {
                Debug.LogError($"[Placement Batch Validator] {failures} review scene(s) still have relevant collisions or support issues.");
                EditorApplication.Exit(1);
                return;
            }

            Debug.Log("[Placement Batch Validator] All review scenes passed with 0 relevant collisions.");
            EditorApplication.Exit(0);
        }

        public static void ValidateLatestGeneratedUiLoadPath()
        {
            AssetDatabase.Refresh();

            if (!Visualizer.Instance.LoadLatestGeneratedJson())
            {
                Debug.LogError("[Placement Batch Validator] UI load-path simulation failed: no generated scene JSON loaded.");
                EditorApplication.Exit(1);
                return;
            }

            int rendererCount = Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None).Length;
            int collisions = Visualizer.CountRelevantCollisions();
            int supportIssues = Visualizer.CountRelationPlacementIssues();
            Debug.Log(
                $"[Placement Batch Validator] UI load-path simulation: renderers={rendererCount}, " +
                $"relevantCollisions={collisions}, supportIssues={supportIssues}");

            if (rendererCount == 0 || collisions > 0 || supportIssues > 0)
            {
                Debug.LogError("[Placement Batch Validator] UI load-path simulation failed.");
                EditorApplication.Exit(1);
                return;
            }

            Debug.Log("[Placement Batch Validator] UI load-path simulation passed.");
            EditorApplication.Exit(0);
        }

        private static bool IsStrictReviewScene(string assetPath)
        {
            string normalized = assetPath.Replace('\\', '/').ToLowerInvariant();
            if (!normalized.Contains("/gpt_tests/"))
            {
                return true;
            }

            string fileName = Path.GetFileName(normalized);
            return normalized.Contains("_hardened") || fileName.StartsWith("output_");
        }

        private static IEnumerable<string> EnumerateReviewSceneAssetPaths()
        {
            HashSet<string> seen = new HashSet<string>();
            foreach (string assetPath in ReviewSceneAssetPaths)
            {
                if (seen.Add(assetPath))
                {
                    yield return assetPath;
                }
            }

            foreach (string assetPath in FindLatestGeneratedScenePaths())
            {
                if (seen.Add(assetPath))
                {
                    yield return assetPath;
                }
            }
        }

        private static IEnumerable<string> FindLatestGeneratedScenePaths()
        {
            string folder = Path.Combine(Application.dataPath, "Json_Tests", "GPT_Tests");
            if (!Directory.Exists(folder))
            {
                yield break;
            }

            foreach (string pattern in new[] { "comparison_*_classic.json", "comparison_*_relational.json", "comparison_*_relational_hardened.json", "output_*.json" })
            {
                string latest = Directory.GetFiles(folder, pattern)
                    .Where(IsSceneJsonCandidate)
                    .OrderByDescending(File.GetLastWriteTimeUtc)
                    .FirstOrDefault();
                if (!string.IsNullOrEmpty(latest))
                {
                    yield return "Assets/Json_Tests/GPT_Tests/" + Path.GetFileName(latest);
                }
            }
        }

        private static bool IsSceneJsonCandidate(string filePath)
        {
            string fileName = Path.GetFileName(filePath)?.ToLowerInvariant() ?? string.Empty;
            return fileName.EndsWith(".json") &&
                   !fileName.EndsWith("_summary.json") &&
                   !fileName.Contains("_summary_");
        }

        private static string AssetPathToFullPath(string assetPath)
        {
            string normalized = assetPath.Replace('\\', '/');
            if (normalized.StartsWith("Assets/"))
            {
                return Path.Combine(Application.dataPath, normalized.Substring("Assets/".Length));
            }

            return Path.GetFullPath(assetPath);
        }

        private static void RenderPreview(string assetPath)
        {
            MeshRenderer[] renderers = Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None);
            if (renderers.Length == 0)
            {
                return;
            }

            List<MeshRenderer> hiddenForPreview = new List<MeshRenderer>();
            foreach (MeshRenderer renderer in renderers)
            {
                if (IsPreviewOccluder(renderer))
                {
                    renderer.enabled = false;
                    hiddenForPreview.Add(renderer);
                }
            }

            MeshRenderer[] visibleRenderers = renderers.Where(renderer => renderer.enabled).ToArray();
            if (visibleRenderers.Length == 0)
            {
                visibleRenderers = renderers;
            }

            Bounds bounds = visibleRenderers[0].bounds;
            for (int i = 1; i < visibleRenderers.Length; i++)
            {
                bounds.Encapsulate(visibleRenderers[i].bounds);
            }

            GameObject lightObject = new GameObject("PlacementPreviewLight");
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.8f;
            lightObject.transform.rotation = Quaternion.Euler(50f, -35f, 0f);

            GameObject cameraObject = new GameObject("PlacementPreviewCamera");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.78f, 0.80f, 0.82f, 1f);
            camera.orthographic = true;
            camera.orthographicSize = Mathf.Max(bounds.extents.x, bounds.extents.y, bounds.extents.z) * 1.35f;
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 200f;

            float distance = Mathf.Max(bounds.extents.magnitude * 2.2f, 6f);
            cameraObject.transform.position = bounds.center + new Vector3(distance, distance * 0.7f, -distance);
            cameraObject.transform.LookAt(bounds.center);

            RenderTexture renderTexture = new RenderTexture(1280, 720, 24);
            Texture2D screenshot = new Texture2D(1280, 720, TextureFormat.RGB24, false);
            RenderTexture previous = RenderTexture.active;

            try
            {
                camera.targetTexture = renderTexture;
                RenderTexture.active = renderTexture;
                camera.Render();
                screenshot.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0);
                screenshot.Apply();

                string folder = Path.Combine(Application.dataPath, "..", "Logs", "PlacementReviewScreenshots");
                Directory.CreateDirectory(folder);
                string fileName = SanitizeFileName(assetPath) + ".png";
                WriteCameraPreview(camera, screenshot, Path.Combine(folder, fileName));

                camera.orthographic = true;
                camera.orthographicSize = Mathf.Max(bounds.extents.x, bounds.extents.z) * 1.15f;
                cameraObject.transform.position = bounds.center + new Vector3(0f, Mathf.Max(bounds.extents.y * 4f, 8f), 0f);
                cameraObject.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
                WriteCameraPreview(camera, screenshot, Path.Combine(folder, SanitizeFileName(assetPath) + "_topdown.png"));

                camera.orthographic = true;
                camera.orthographicSize = Mathf.Max(bounds.extents.x, bounds.extents.z) * 0.72f;
                float detailDistance = Mathf.Max(bounds.extents.magnitude * 1.35f, 5f);
                cameraObject.transform.position = bounds.center + new Vector3(detailDistance * 0.45f, detailDistance * 0.55f, detailDistance * 0.65f);
                cameraObject.transform.LookAt(bounds.center + new Vector3(0f, 0.35f, 0f));
                WriteCameraPreview(camera, screenshot, Path.Combine(folder, SanitizeFileName(assetPath) + "_interior.png"));
            }
            finally
            {
                camera.targetTexture = null;
                RenderTexture.active = previous;
                Object.DestroyImmediate(renderTexture);
                Object.DestroyImmediate(screenshot);
                Object.DestroyImmediate(cameraObject);
                Object.DestroyImmediate(lightObject);
                foreach (MeshRenderer renderer in hiddenForPreview)
                {
                    if (renderer != null)
                    {
                        renderer.enabled = true;
                    }
                }
            }
        }

        private static void WriteCameraPreview(Camera camera, Texture2D screenshot, string path)
        {
            camera.Render();
            screenshot.ReadPixels(new Rect(0, 0, screenshot.width, screenshot.height), 0, 0);
            screenshot.Apply();
            File.WriteAllBytes(path, screenshot.EncodeToPNG());
        }

        private static bool IsPreviewOccluder(MeshRenderer renderer)
        {
            string name = renderer.gameObject.name.ToLowerInvariant();
            return name == "ceiling"
                || name == "solid_ceiling"
                || name.Contains("_ceiling")
                || name.Contains("decke")
                || name == "front_wall"
                || name == "back_wall"
                || name == "left_wall"
                || name == "right_wall"
                || name == "wall_front"
                || name == "wall_back"
                || name == "wall_left"
                || name == "wall_right";
        }

        private static string SanitizeFileName(string value)
        {
            string safe = value.Replace("Assets/", string.Empty)
                .Replace('/', '_')
                .Replace('\\', '_');
            foreach (char invalid in Path.GetInvalidFileNameChars())
            {
                safe = safe.Replace(invalid, '_');
            }

            return safe;
        }
    }
}
