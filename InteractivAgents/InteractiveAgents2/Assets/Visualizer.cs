using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Assets
{
    public class Visualizer : MonoBehaviour
    {
        #region Singelton Pattern

        private static Visualizer _instance;

        public static Visualizer Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindFirstObjectByType<Visualizer>();

                    if (_instance == null)
                    {
                        GameObject instance = new GameObject("Visualizer");
                        _instance = instance.AddComponent<Visualizer>();

                        return Instance;
                    }
                }
                return _instance;
            }
        }

        public void Awake()
        {
            EnsureDefaultSettings();

            if (_instance == null)
            {
                _instance = this;
                if (Application.isPlaying)
                {
                    DontDestroyOnLoad(gameObject);
                }
            }
            else if (_instance != this)
            {
                Destroy(gameObject);
            }
        }

        private void OnValidate()
        {
            EnsureDefaultSettings();
        }

        private void EnsureDefaultSettings()
        {
            if (JsonVersion <= 0)
            {
                JsonVersion = 2;
            }
        }

        #endregion

        [Tooltip("JSON Datei mit der Szenenbeschreibung")]
        public TextAsset JsonFile;

        [Tooltip("JSON Version")]
        public int JsonVersion = 2;

        [Tooltip("Collision Color")]
        public Color CollisionColor = Color.magenta;

        [Tooltip("Should Check Collision?")]
        public bool ShouldCheckCollision;

        [Tooltip("Instand Load Json")]
        public bool InstantLoadJson;

        [Tooltip("Delete All")]
        public bool DeleteAll;

        [Tooltip("Validator Iterations")]
        public int ValidatorIterations = 1;

        [Tooltip("Scene Name")] 
        public string SceneName;

        [Tooltip("Input Image")] 
        public Texture2D Image;

        [Tooltip("Add DevDescription components to generated JSON placeholders")]
        public bool AddDevDescriptionsToGeneratedPlaceholders = true;

        [Tooltip("Automatically send DevDescription placeholders to the Text2-3D Flask backend after loading JSON")]
        public bool GenerateTextTo3DModelsAfterLoad;

        [Tooltip("Text2-3D Flask base URL or /generate endpoint")]
        public string TextTo3DApiUrl = "http://127.0.0.1:5000";

        private Reader _reader = new Reader();
        private Writer _writer = new Writer();
        private Spawner _spawner = new Spawner();
        private ChatWindow _chatWindow;
        private object _json;
        private List<string> _jsons = new List<string>();
        private ReverseConverter _converter;
        private bool _textTo3DGenerationQueued;
        private int EffectiveJsonVersion => JsonVersion > 0 ? JsonVersion : 2;

        public ReverseConverter Converter => _converter ??= ScriptableObject.CreateInstance<ReverseConverter>();

        public void Start()
        {
        }

        public void Update()
        {
            if (!InstantLoadJson)
            {
                return;
            }

            string folderPath = GetGeneratedJsonFolderPath();

            if (!Directory.Exists(folderPath))
            {
                return;
            }

            List<string> currentJsons = Directory.GetFiles(folderPath, "*.json")
                .Where(IsSceneJsonCandidate)
                .ToList();
            List<string> newFiles = currentJsons
                .Where(current => _jsons.All(existing => existing != current))
                .ToList();

            if (!newFiles.Any())
            {
                return;
            }

            _jsons = currentJsons;

            string newestFile = newFiles
                .OrderByDescending(file => file)
                .First();

            DoVisualize(File.ReadAllText(newestFile));
        }

        [MenuItem("GameObject/Visualize %g")]
        public static void Visualize()
        {
            EditorUtility.DisplayDialog("Visualizer", "Loading latest company room scene...", "OK", "");

            Visualizer.Instance.DoVisualize();
        }

        [MenuItem("GameObject/Save Scene %r")]
        public static void SaveScene()
        {
            Visualizer.Instance.Converter.ScanForNewObjects();
            Visualizer.Instance._writer.WriteScene(Visualizer.Instance.Converter);
        }

        [MenuItem("GameObject/Delete Last Items %e")]
        public static void DeleteLastItems()
        {
            bool delete = EditorUtility.DisplayDialog("Visualizer", "Are u sure u want to delete the last spawned items?", "OK", "NO");

            if (delete)
            {
                Visualizer.Instance.Delete();
            }
        }

        [MenuItem("GameObject/Check Collision")]
        public static void CheckCollision()
        {
            int collisionPairs = CheckCollisionInternal(highlight: true);
            Debug.Log($"Visualizer: Relevant collision pairs found: {collisionPairs}");
        }

        public static int CountRelevantCollisions()
        {
            return CheckCollisionInternal(highlight: false);
        }

        public static int CountRelationPlacementIssues()
        {
            int issues = 0;

            foreach (JulangGameObject item in Visualizer.Instance.Converter.GameObjects)
            {
                if (item == null || item.GameObject == null || item.RelativePositioning == null)
                {
                    continue;
                }

                string relation = NormalizeToken(item.RelativePositioning.Relation);
                if (relation != "on_top_of" && relation != "over" && relation != "below")
                {
                    continue;
                }

                JulangGameObject reference = FindJulangByObjectId(item.RelativePositioning.ReferenceObject);
                if (reference == null || reference.GameObject == null)
                {
                    Debug.LogWarning($"Visualizer: Missing relation reference '{item.RelativePositioning.ReferenceObject}' for {item.ObjectId}.");
                    issues++;
                    continue;
                }

                Bounds itemBounds = CalculateOwnObjectBounds(item);
                Bounds referenceBounds = CalculateOwnObjectBounds(reference);
                float distance = Mathf.Max(0f, item.RelativePositioning.Distance);
                float tolerance = 0.04f;

                if (relation == "below")
                {
                    float expectedTop = referenceBounds.min.y - distance;
                    float gap = expectedTop - itemBounds.max.y;
                    float maxAllowedGap = Mathf.Max(0.20f, distance + tolerance);
                    bool penetratesReference = itemBounds.max.y > expectedTop + tolerance;
                    bool hangsTooFarAway = gap > maxAllowedGap;
                    if (penetratesReference || hangsTooFarAway)
                    {
                        Debug.LogWarning(
                            $"Visualizer: Relation support issue {item.ObjectId} below {reference.ObjectId}: " +
                            $"top={itemBounds.max.y:F3}, expected<={expectedTop:F3}, gap={gap:F3}");
                        issues++;
                    }
                }
                else
                {
                    float expectedBottom = referenceBounds.max.y + distance;
                    if (Mathf.Abs(itemBounds.min.y - expectedBottom) > tolerance)
                    {
                        Debug.LogWarning(
                            $"Visualizer: Relation support issue {item.ObjectId} {relation} {reference.ObjectId}: " +
                            $"bottom={itemBounds.min.y:F3}, expected={expectedBottom:F3}");
                        issues++;
                    }
                }
            }

            return issues;
        }

        private static int CheckCollisionInternal(bool highlight)
        {
            List<MeshRenderer> allSceneElements = FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None)
                .Where(renderer => renderer != null &&
                                   !CozyRoomLighting.IsOwnedLightingTransform(renderer.transform))
                .ToList();

            var penetrated = new HashSet<MeshRenderer>();
            int collisionPairs = 0;

            for (int i = 0; i < allSceneElements.Count; i++)
            {
                var ra = allSceneElements[i];
                if (!ra) continue;

                for (int j = i + 1; j < allSceneElements.Count; j++)
                {
                    var rb = allSceneElements[j];
                    if (!rb) continue;

                    if (ShouldIgnoreCollisionPair(ra, rb))
                    {
                        continue;
                    }

                    if (BoundsPenetrate(ra.bounds, rb.bounds))
                    {
                        collisionPairs++;
                        penetrated.Add(ra);
                        penetrated.Add(rb);
                        Debug.LogWarning(
                            $"Visualizer: Relevant collision pair {DescribeRendererCollisionTarget(ra)} <-> {DescribeRendererCollisionTarget(rb)}");
                    }
                }
            }

            if (highlight)
            {
                foreach (MeshRenderer renderer in penetrated)
                {
                    ApplyRendererColor(renderer, Visualizer.Instance.CollisionColor);
                }
            }

            return collisionPairs;
        }

        private static string DescribeRendererCollisionTarget(Renderer renderer)
        {
            JulangGameObject julangObject = FindJulangObject(renderer);
            if (julangObject != null)
            {
                return $"{julangObject.ObjectId} [{julangObject.ObjectType}]";
            }

            return renderer != null ? renderer.name : "<missing renderer>";
        }

        [MenuItem("GameObject/Show UI")]
        public static void ShowWindow()
        {
            Instance._chatWindow = ChatWindow.OpenWindow();
        }

        public void DoVisualize()
        {
            if (JsonFile != null)
            {
                DoVisualize(JsonFile.text);
                return;
            }

            LoadLatestGeneratedJson();
        }

        public void DoVisualize(string fileName)
        {
            ReadJsonFile(fileName);
            SpawnObjects();
            QueueTextTo3DGenerationAfterLoad();

            if (ShouldCheckCollision)
            {
                CheckCollision();
            }
        }

        private void QueueTextTo3DGenerationAfterLoad()
        {
            if (!GenerateTextTo3DModelsAfterLoad || _textTo3DGenerationQueued)
            {
                return;
            }

            _textTo3DGenerationQueued = true;
            EditorApplication.delayCall += () =>
            {
                _textTo3DGenerationQueued = false;
                global::DevDescriptionImporter.GenerateForCurrentScene(TextTo3DApiUrl, false);
            };
        }

        public bool LoadLatestGeneratedJson()
        {
            string folderPath = GetGeneratedJsonFolderPath();

            if (!Directory.Exists(folderPath))
            {
                Debug.LogWarning($"Visualizer: JSON-Ordner nicht gefunden: {folderPath}");
                return false;
            }

            string newestFile = Directory.GetFiles(folderPath, "*.json")
                .Where(IsSceneJsonCandidate)
                .OrderByDescending(File.GetLastWriteTimeUtc)
                .FirstOrDefault();

            if (string.IsNullOrEmpty(newestFile))
            {
                Debug.LogWarning($"Visualizer: Keine JSON-Datei in {folderPath} gefunden.");
                return false;
            }

            Debug.Log($"Visualizer: Lade neueste JSON-Datei: {newestFile}");
            DoVisualize(File.ReadAllText(newestFile));
            return true;
        }

        public void Delete()
        {
            Delete(DeleteAll);
        }

        public void Delete(bool deleteAll)
        {
            CozyRoomLighting.RemoveFromScene(gameObject.scene);
            Visualizer.Instance.Converter.GameObjects.Clear();
            if (deleteAll)
            {
                MeshRenderer[] meshRenderers = FindObjectsByType<MeshRenderer>(FindObjectsInactive.Include, FindObjectsSortMode.None);

                EditorApplication.delayCall += () =>
                {
                    foreach (MeshRenderer mr in meshRenderers)
                    {
                        if (mr) DestroyImmediate(mr.gameObject);
                    }
                };

                _spawner.LastSpawnedObjects.Clear();
                return;
            }

            foreach (KeyValuePair<string, GameObject> spawnedObject in _spawner.LastSpawnedObjects)
            {
                DestroyImmediate(spawnedObject.Value);
            }
            _spawner.LastSpawnedObjects.Clear();
            CozyRoomLighting.ApplyToScene(gameObject.scene, Converter.Environment);
        }

        private void ReadJsonFile(string json)
        {
            _json = null;

            if (string.IsNullOrEmpty(json))
            {
                Debug.LogWarning("Visualizer: JSON-Inhalt ist leer.");
                return;
            }

            try
            {
                string cleanJson = NormalizeJsonInput(json);

                object readJson = _reader.ReadJson(cleanJson, EffectiveJsonVersion);

                if (readJson != null)
                {
                    _json = readJson;
                    return;
                }

                Debug.LogWarning($"Visualizer: JSON konnte nicht gelesen werden. JsonVersion={EffectiveJsonVersion}");
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Visualizer: Loading JSON was not successful: {ex.Message}");
            }
        }

        private static string NormalizeJsonInput(string json)
        {
            string cleanJson = json.Trim('\uFEFF', ' ', '\r', '\n', '\t');

            if (!cleanJson.StartsWith("\"") || !cleanJson.EndsWith("\""))
            {
                return cleanJson;
            }

            try
            {
                string decodedJson = JsonConvert.DeserializeObject<string>(cleanJson);
                return string.IsNullOrWhiteSpace(decodedJson)
                    ? cleanJson
                    : decodedJson.Trim('\uFEFF', ' ', '\r', '\n', '\t');
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Visualizer: JSON string wrapper could not be decoded: {ex.Message}");
                return cleanJson;
            }
        }

        private void SpawnObjects()
        {
            if (_json == null)
            {
                Debug.LogWarning("Visualizer: Keine gelesenen JSON-Daten zum Spawnen vorhanden.");
                return;
            }

            try
            {
                _spawner.SpawnObjects(_json, EffectiveJsonVersion);
                CozyRoomLighting.ApplyToScene(gameObject.scene, Converter.Environment);
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Visualizer: Spawn failed: {ex.Message}");
                return;
            }

            Debug.Log($"Visualizer: Spawned {_spawner.LastSpawnedObjects.Count} objects.");
            if (_spawner.LastSpawnedObjects.Count == 0)
            {
                Debug.LogWarning($"Visualizer: Keine Objekte erzeugt. Prüfe JsonVersion={EffectiveJsonVersion} und JSON-Struktur.");
            }

            if (!Application.isPlaying && gameObject.scene.IsValid())
            {
                EditorSceneManager.MarkSceneDirty(gameObject.scene);
            }
        }

        private static string GetGeneratedJsonFolderPath()
        {
            return Path.Combine(Application.dataPath, "Json_Tests", "GPT_Tests");
        }

        private static bool IsSceneJsonCandidate(string filePath)
        {
            string fileName = Path.GetFileName(filePath)?.ToLowerInvariant() ?? string.Empty;
            return fileName.EndsWith(".json") &&
                   !fileName.EndsWith("_summary.json") &&
                   !fileName.Contains("_summary_");
        }

        public static void ApplyRendererColor(Renderer renderer, Color color)
        {
            if (renderer == null)
            {
                return;
            }

            Material[] sourceMaterials = renderer.sharedMaterials;
            if (sourceMaterials == null || sourceMaterials.Length == 0)
            {
                renderer.sharedMaterial = CreateSafeMaterial(color);
                return;
            }

            Material[] coloredMaterials = new Material[sourceMaterials.Length];
            for (int i = 0; i < sourceMaterials.Length; i++)
            {
                coloredMaterials[i] = CreateSafeMaterial(color, sourceMaterials[i]);
            }

            renderer.sharedMaterials = coloredMaterials;
        }

        private static Material CreateSafeMaterial(Color color, Material sourceMaterial = null)
        {
            Shader shader = sourceMaterial != null && sourceMaterial.shader != null && sourceMaterial.shader.isSupported
                ? sourceMaterial.shader
                : FindSupportedLitShader();

            Material material = sourceMaterial != null && sourceMaterial.shader != null && sourceMaterial.shader.isSupported
                ? new Material(sourceMaterial)
                : new Material(shader);

            material.name = $"{material.name}_RuntimeColor";
            SetMaterialColor(material, color);
            return material;
        }

        private static Shader FindSupportedLitShader()
        {
            string[] shaderNames =
            {
                "Universal Render Pipeline/Lit",
                "Universal Render Pipeline/Simple Lit",
                "Universal Render Pipeline/Unlit",
                "Standard",
                "Sprites/Default"
            };

            foreach (string shaderName in shaderNames)
            {
                Shader shader = Shader.Find(shaderName);
                if (shader != null && shader.isSupported)
                {
                    return shader;
                }
            }

            return Shader.Find("Sprites/Default");
        }

        private static void SetMaterialColor(Material material, Color color)
        {
            if (material == null)
            {
                return;
            }

            if (material.HasProperty("_BaseColor"))
            {
                material.SetColor("_BaseColor", color);
            }

            if (material.HasProperty("_Color"))
            {
                material.SetColor("_Color", color);
            }
        }

        private static bool ShouldIgnoreCollisionPair(MeshRenderer first, MeshRenderer second)
        {
            if (CozyRoomLighting.IsOwnedLightingTransform(first?.transform) ||
                CozyRoomLighting.IsOwnedLightingTransform(second?.transform))
            {
                return true;
            }

            JulangGameObject firstObject = FindJulangObject(first);
            JulangGameObject secondObject = FindJulangObject(second);

            if (firstObject != null && secondObject != null)
            {
                if (firstObject == secondObject)
                {
                    return true;
                }

                if (IsExpectedRelationalPair(firstObject, secondObject))
                {
                    return true;
                }

                if (IsRoomShellPair(firstObject, secondObject))
                {
                    return true;
                }

                if (IsIntentionalFloorOverlayPair(firstObject, secondObject, first.bounds, second.bounds))
                {
                    return true;
                }
            }

            return false;
        }

        private static JulangGameObject FindJulangObject(Renderer renderer)
        {
            if (renderer == null)
            {
                return null;
            }

            Transform rendererTransform = renderer.transform;
            return Visualizer.Instance.Converter.GameObjects.FirstOrDefault(item =>
                item != null &&
                item.GameObject != null &&
                (rendererTransform == item.GameObject.transform ||
                 rendererTransform.IsChildOf(item.GameObject.transform)));
        }

        private static JulangGameObject FindJulangByObjectId(string objectId)
        {
            if (string.IsNullOrEmpty(objectId))
            {
                return null;
            }

            return Visualizer.Instance.Converter.GameObjects.FirstOrDefault(item =>
                item != null &&
                string.Equals(item.ObjectId, objectId, StringComparison.Ordinal));
        }

        private static Bounds CalculateOwnObjectBounds(JulangGameObject item)
        {
            if (item?.GameObject == null)
            {
                return new Bounds(Vector3.zero, Vector3.zero);
            }

            List<Transform> nestedJulangRoots = Visualizer.Instance.Converter.GameObjects
                .Where(other =>
                    other != null &&
                    other != item &&
                    other.GameObject != null &&
                    other.GameObject.transform.IsChildOf(item.GameObject.transform))
                .Select(other => other.GameObject.transform)
                .ToList();

            Renderer[] renderers = item.GameObject.GetComponentsInChildren<Renderer>()
                .Where(renderer => renderer != null &&
                                   !CozyRoomLighting.IsOwnedLightingTransform(renderer.transform))
                .ToArray();
            bool hasBounds = false;
            Bounds bounds = new Bounds(item.GameObject.transform.position, Vector3.zero);

            foreach (Renderer renderer in renderers)
            {
                if (renderer == null || nestedJulangRoots.Any(root =>
                        renderer.transform == root || renderer.transform.IsChildOf(root)))
                {
                    continue;
                }

                if (!hasBounds)
                {
                    bounds = renderer.bounds;
                    hasBounds = true;
                }
                else
                {
                    bounds.Encapsulate(renderer.bounds);
                }
            }

            return hasBounds ? bounds : CalculateTransformBounds(item.GameObject);
        }

        private static Bounds CalculateObjectBounds(GameObject obj)
        {
            if (obj == null)
            {
                return new Bounds(Vector3.zero, Vector3.zero);
            }

            Renderer[] renderers = obj.GetComponentsInChildren<Renderer>()
                .Where(renderer => renderer != null &&
                                   !CozyRoomLighting.IsOwnedLightingTransform(renderer.transform))
                .ToArray();
            if (renderers.Length > 0)
            {
                Bounds bounds = renderers[0].bounds;
                for (int i = 1; i < renderers.Length; i++)
                {
                    bounds.Encapsulate(renderers[i].bounds);
                }

                return bounds;
            }

            return CalculateTransformBounds(obj);
        }

        private static Bounds CalculateTransformBounds(GameObject obj)
        {
            Vector3 size = obj.transform.lossyScale;
            return new Bounds(obj.transform.position, new Vector3(Mathf.Abs(size.x), Mathf.Abs(size.y), Mathf.Abs(size.z)));
        }

        private static bool IsExpectedRelationalPair(JulangGameObject first, JulangGameObject second)
        {
            if (first?.GameObject == null || second?.GameObject == null)
            {
                return false;
            }

            bool hierarchyPair =
                first.GameObject.transform.IsChildOf(second.GameObject.transform) ||
                second.GameObject.transform.IsChildOf(first.GameObject.transform);
            if (hierarchyPair && (first.RelativePositioning != null || second.RelativePositioning != null))
            {
                return true;
            }

            return ReferencesObject(first, second) || ReferencesObject(second, first);
        }

        private static bool ReferencesObject(JulangGameObject source, JulangGameObject target)
        {
            return source?.RelativePositioning != null &&
                   target != null &&
                   !string.IsNullOrEmpty(target.ObjectId) &&
                   string.Equals(source.RelativePositioning.ReferenceObject, target.ObjectId, StringComparison.Ordinal);
        }

        private static bool IsRoomShellPair(JulangGameObject first, JulangGameObject second)
        {
            return IsRoomShellObject(first) && IsRoomShellObject(second);
        }

        private static bool IsRoomShellObject(JulangGameObject obj)
        {
            string type = NormalizeToken(obj?.ObjectType);
            string id = NormalizeToken(obj?.ObjectId);

            if (type == "floor" || type == "ceiling" || type == "roof" ||
                type == "room_ceiling" || type == "wall" ||
                type == "room_wall" || type == "architectural_wall")
            {
                return true;
            }

            if (id == "floor" || id == "ceiling" ||
                id == "front_wall" || id == "back_wall" ||
                id == "left_wall" || id == "right_wall")
            {
                return true;
            }

            return false;
        }

        private static bool IsIntentionalFloorOverlayPair(
            JulangGameObject first,
            JulangGameObject second,
            Bounds firstBounds,
            Bounds secondBounds)
        {
            return (IsFloorObject(first) && IsFloorOverlayObject(second, secondBounds, firstBounds)) ||
                   (IsFloorObject(second) && IsFloorOverlayObject(first, firstBounds, secondBounds));
        }

        private static bool IsFloorObject(JulangGameObject obj)
        {
            string type = NormalizeToken(obj?.ObjectType);
            string id = NormalizeToken(obj?.ObjectId);
            return type == "floor" || id == "floor";
        }

        private static bool IsFloorOverlayObject(JulangGameObject obj, Bounds overlayBounds, Bounds floorBounds)
        {
            string type = NormalizeToken(obj?.ObjectType);
            string id = NormalizeToken(obj?.ObjectId);
            bool looksLikeOverlay =
                type.Contains("rug") ||
                type.Contains("carpet") ||
                type.Contains("mat") ||
                type.Contains("floor_path") ||
                type.Contains("path_marker") ||
                type.Contains("floor_decal") ||
                type.Contains("footprint") ||
                id.Contains("rug") ||
                id.Contains("carpet") ||
                id.Contains("mat") ||
                id.Contains("floor_path") ||
                id.Contains("path_marker") ||
                id.Contains("floor_decal") ||
                id.Contains("footprint");

            if (!looksLikeOverlay)
            {
                return false;
            }

            float overlayHeight = overlayBounds.size.y;
            float floorTop = floorBounds.max.y;
            return overlayHeight <= 0.12f && overlayBounds.min.y >= floorTop - 0.08f;
        }

        private static string NormalizeToken(string value)
        {
            return string.IsNullOrWhiteSpace(value)
                ? string.Empty
                : value.Trim().ToLowerInvariant();
        }

        private static bool BoundsPenetrate(in Bounds a, in Bounds b, float eps = 1e-5f)
        {
            return (a.min.x + eps < b.max.x && a.max.x - eps > b.min.x) &&
                   (a.min.y + eps < b.max.y && a.max.y - eps > b.min.y) &&
                   (a.min.z + eps < b.max.z && a.max.z - eps > b.min.z);
        }
    }
}
