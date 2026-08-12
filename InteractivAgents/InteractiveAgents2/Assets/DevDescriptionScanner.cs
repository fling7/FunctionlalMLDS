#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Assets;
public class DevDescriptionImporter : EditorWindow
{
    /*────────── API & Settings ─────────────────────────────*/
    private const string ApiImage     = "http://127.0.0.1:5000/generate_image";
    private const string ApiModel     = "http://127.0.0.1:5000/generate_model";
    private const string ApiBase      = "http://127.0.0.1:5000";
    private const string ImageBackend = "gpt-image-2";//"local";   // oder "dalle3"
    private const string NegativeLocal =
        "blurry areas, complex background, strange reflections, odd geometry, distortion, harsh shadows";
    private const string TargetFolder = "Assets/GeneratedModels";
    private const string CacheRoot = TargetFolder + "/ResumeCache";
    private const string ImageCacheFolder = CacheRoot + "/Images";
    private const string CacheManifestPath = CacheRoot + "/manifest.json";
    private const string CacheSchemaVersion = "dev-description-cache-v2";
    private const string ImagePromptVersion = "isolated-product-preview-v1";
    private const string ModelGeneratorVersion = "trellis-model-v1";
    private const string LegacySavedImagesFolder = "../textto3d/saved_images";

    /*────────── Skalierungs-Grenzen ─────────────────────────*/
    private const float EPS   = 1e-4f;   // alles darunter gilt als „0“ (Division vermeiden)
    private const float MIN_F = 0.01f;   // kleinster erlaubter Skalierungsfaktor
    private const float MAX_F = 100f;    // größter  „                   “

    /*────────── interne Typen ─────────────────────────────*/
    private class Group
    {
        public string  key;
        public string  description;
        public Vector3 size;
        public readonly List<DevDescription> items = new();
        public bool    generate = true;   // Checkbox „Aktiv“
        public bool    reuse    = true;   // Checkbox „Reuse“
    }

    private class ImageInfo
    {
        public byte[]    data;
        public Texture2D preview;
        public bool      approved;
        public string    editPrompt = "";
        public float     denoise    = 0.8f;   // 0 = Original, 1 = völlig neu
        public string    cacheId = "";
        public string    contentHash = "";
    }

    private readonly struct ImageJob
    {
        public readonly Group Group;
        public readonly DevDescription Item;

        public ImageJob(Group group, DevDescription item)
        {
            Group = group;
            Item = item;
        }
    }

    private readonly struct ModelJob
    {
        public readonly Group Group;
        public readonly List<DevDescription> Targets;
        public readonly DevDescription CacheKey;

        public ModelJob(Group group, List<DevDescription> targets, DevDescription cacheKey)
        {
            Group = group;
            Targets = targets;
            CacheKey = cacheKey;
        }
    }

    private readonly struct ModelPlacement
    {
        public readonly DevDescription Target;
        public readonly GameObject Prefab;
        public readonly string JobId;
        public readonly string Fingerprint;
        public readonly string ContentSignature;
        public readonly string AssetPath;

        public ModelPlacement(DevDescription target, GameObject prefab, string jobId,
                              string fingerprint, string contentSignature, string assetPath)
        {
            Target = target;
            Prefab = prefab;
            JobId = jobId;
            Fingerprint = fingerprint;
            ContentSignature = contentSignature;
            AssetPath = assetPath;
        }
    }

    private sealed class ResolvedModel
    {
        public GameObject Prefab;
        public string JobId;
        public string Fingerprint;
        public string ContentSignature;
        public string AssetPath;
        public bool Legacy;
    }

    [Serializable] private class ImageCacheRecord
    {
        public string id;
        public string filePath;
        public string sha256;
        public bool approved;
    }

    [Serializable] private class ModelCacheRecord
    {
        public string jobId;
        public string fingerprint;
        public string contentSignature;
        public string assetPath;
        public string imageSha256;
    }

    [Serializable] private class CacheManifest
    {
        public int version = 2;
        public List<ImageCacheRecord> images = new();
        public List<ModelCacheRecord> models = new();
    }

    [Serializable] private class ImagePayload
    {
        public string job_id;
        public string image_backend;
        public string positive_prompt;
        public string negative_prompt;
        public string base_image_base64;
        public float  denoise;
    }

    [Serializable] private class ModelPayload
    {
        public string job_id;
        public string image_base64;
    }

    private enum Phase { Config, Images, Models }

    /*────────── Felder ───────────────────────────────────*/
    private readonly List<Group> _groups = new();
    private readonly Dictionary<object, ImageInfo> _img = new();   // Key = Group oder DevDescription
    private readonly HashSet<object> _modelsDone = new();          // zum Einfärben
    private readonly Dictionary<string, ResolvedModel> _preflightModels = new();
    private CacheManifest _cacheManifest;
    private Phase   _phase = Phase.Config;

    private Vector2 _scroll;
    private bool    _busy;
    private bool    _cancel;
    private int     _todo, _done;
    private string  _current = "";
    private string  _apiImage = ApiImage;
    private string  _apiModel = ApiModel;

    private static GUIStyle _green;
    private static GUIStyle _hierarchyStyle;

    [InitializeOnLoadMethod]
    private static void RefreshOpenImportersAfterScriptReload()
    {
        EditorApplication.delayCall += () =>
        {
            DevDescription[] descriptions = FindObjectsByType<DevDescription>(
                FindObjectsInactive.Include, FindObjectsSortMode.None);
            int markedInstances = descriptions.Count(description =>
                description != null && description.GeneratedInstance != null);
            if (descriptions.Length > 0)
            {
                Debug.Log($"[GLB] Offene Szene erkannt: {descriptions.Length} Platzhalter, " +
                          $"{markedInstances} mit persistenter Instanz-Referenz.");
            }

            foreach (DevDescriptionImporter importer in
                     Resources.FindObjectsOfTypeAll<DevDescriptionImporter>())
            {
                if (importer == null) continue;
                importer.CollectGroups();
                importer.Repaint();
            }
        };
    }

    private void OnEnable()
    {
        minSize = new Vector2(820, 620);
        ConfigureApi(null);
        EditorApplication.delayCall -= RefreshAfterDomainReload;
        EditorApplication.delayCall += RefreshAfterDomainReload;
    }

    private void OnDisable()
    {
        EditorApplication.delayCall -= RefreshAfterDomainReload;
    }

    private void RefreshAfterDomainReload()
    {
        if (this == null) return;
        CollectGroups();
        Repaint();
    }

    /*────────── MENU ─────────────────────────────────────*/
    [MenuItem("GameObject/Dev Tools/Generate Images & GLB...", false, 50)]
    private static void Open()
    {
        var w = GetWindow<DevDescriptionImporter>("GLB Import");
        w.minSize = new Vector2(820, 620);
        w.ConfigureApi(null);
        w.CollectGroups();
    }

    [MenuItem("GameObject/Dev Tools/Place Existing Generated GLBs", false, 51)]
    private static void PlaceExistingGeneratedGlbs()
    {
        var w = GetWindow<DevDescriptionImporter>("GLB Import");
        w.minSize = new Vector2(820, 620);
        w.ConfigureApi(null);
        w.CollectGroups();
        w._phase = Phase.Models;
        w.PlaceExistingGeneratedModelsForScene();
    }

    public static void GenerateForCurrentScene(string apiUrl = null, bool showWindow = false)
    {
        var w = GetWindow<DevDescriptionImporter>("GLB Import");
        w.minSize = new Vector2(820, 620);
        w.ConfigureApi(apiUrl);
        w.CollectGroups();

        if (w._groups.Count == 0)
        {
            Debug.LogWarning("[Text2-3D] Keine DevDescription-Objekte in der Szene gefunden.");
            return;
        }

        w._phase = Phase.Images;
        w.Repaint();
        _ = w.RunAutomaticGeneration();
    }

    private void ConfigureApi(string apiUrl)
    {
        string baseUrl = string.IsNullOrWhiteSpace(apiUrl) ? ApiBase : apiUrl.Trim().TrimEnd('/');

        if (baseUrl.EndsWith("/generate", StringComparison.OrdinalIgnoreCase))
        {
            baseUrl = baseUrl.Substring(0, baseUrl.Length - "/generate".Length);
        }
        else if (baseUrl.EndsWith("/generate_image", StringComparison.OrdinalIgnoreCase))
        {
            baseUrl = baseUrl.Substring(0, baseUrl.Length - "/generate_image".Length);
        }
        else if (baseUrl.EndsWith("/generate_model", StringComparison.OrdinalIgnoreCase))
        {
            baseUrl = baseUrl.Substring(0, baseUrl.Length - "/generate_model".Length);
        }

        _apiImage = baseUrl + "/generate_image";
        _apiModel = baseUrl + "/generate_model";
    }

    /*────────── GROUP SCAN ───────────────────────────────*/
    private void CollectGroups()
    {
        _groups.Clear();
        _preflightModels.Clear();
        _cacheManifest = null;
        AddDevDescriptionsFromConverter();

        foreach (var dd in FindObjectsByType<DevDescription>(
                     FindObjectsInactive.Include, FindObjectsSortMode.None))
        {
            if (dd == null || dd.gameObject == null)
            {
                continue;
            }

            string d = string.IsNullOrWhiteSpace(dd.Description) ? "Unnamed object" : dd.Description.Trim();
            Vector3 s = Round2(dd.transform.lossyScale);
            string k = $"{d}__{s.x}_{s.y}_{s.z}";

            var g = _groups.FirstOrDefault(x => x.key == k) ?? new Group
            {
                key = k, description = d, size = s
            };
            if (!_groups.Contains(g)) _groups.Add(g);
            g.items.Add(dd);
        }

        RefreshCachedModelStatus();
    }

    private void AddDevDescriptionsFromConverter()
    {
        if (Visualizer.Instance == null || Visualizer.Instance.Converter == null ||
            Visualizer.Instance.Converter.GameObjects == null)
        {
            return;
        }

        List<JulangGameObject> descriptionObjects = Visualizer.Instance.Converter.GameObjects;

        for (int i = descriptionObjects.Count - 1; i >= 0; i--)
        {
            JulangGameObject descriptionObject = descriptionObjects[i];
            GameObject target = null;

            try
            {
                if (descriptionObject != null)
                {
                    target = descriptionObject.GameObject;
                }
            }
            catch (MissingReferenceException)
            {
                target = null;
            }

            if (target == null)
            {
                descriptionObjects.RemoveAt(i);
                continue;
            }

            DevDescription devDescription = target.GetComponent<DevDescription>();
            if (devDescription == null)
            {
                devDescription = target.AddComponent<DevDescription>();
            }

            devDescription.SetDescription(descriptionObject.Specification);
        }
    }

    /*────────── GUI STEUERUNG ────────────────────────────*/
    private void OnGUI()
    {
        _green ??= new GUIStyle(EditorStyles.label) { normal = { textColor = Color.green } };
        _hierarchyStyle ??= new GUIStyle(EditorStyles.miniLabel) { normal = { textColor = new Color(0.35f, 0.65f, 1f) } };

        switch (_phase)
        {
            case Phase.Config:  DrawConfig();  break;
            case Phase.Images:  DrawImages();  break;
            case Phase.Models:  DrawModels();  break;
        }
    }

    /*===== 1) KONFIGURATION ===================================================*/
    private void DrawConfig()
    {
        EditorGUILayout.LabelField("1 | Gruppen wählen & Reuse einstellen", EditorStyles.boldLabel);
        EditorGUILayout.BeginHorizontal();
        GUILayout.FlexibleSpace();
        if (GUILayout.Button("Alle abwaehlen", GUILayout.Width(130)))
        {
            SetAllGroupsActive(false);
        }
        EditorGUILayout.EndHorizontal();

        _scroll = EditorGUILayout.BeginScrollView(_scroll);

        Dictionary<DevDescription, Group> groupByItem = BuildGroupLookup();
        HashSet<DevDescription> allItems = new(groupByItem.Keys);
        HashSet<DevDescription> drawnItems = new();

        List<DevDescription> hierarchyRoots = allItems
            .Where(item =>
            {
                DevDescription parent = GetParentDevDescription(item);
                return HasDevDescriptionHierarchy(item) && (parent == null || !allItems.Contains(parent));
            })
            .OrderBy(item => GetTransformPath(item.transform))
            .ToList();

        if (hierarchyRoots.Count > 0)
        {
            EditorGUILayout.LabelField("Hierarchie", EditorStyles.boldLabel);
            foreach (DevDescription root in hierarchyRoots)
            {
                EditorGUILayout.BeginVertical("box");
                DrawHierarchyConfigNode(root, groupByItem, allItems, drawnItems, 0);
                EditorGUILayout.EndVertical();
            }
        }

        List<Group> flatGroups = _groups
            .Where(group => group.items.Any(item => !drawnItems.Contains(item)))
            .ToList();
        if (flatGroups.Count > 0)
        {
            EditorGUILayout.LabelField("Ohne Hierarchie", EditorStyles.boldLabel);
            foreach (Group group in flatGroups)
            {
                DrawFlatConfigGroup(group, drawnItems);
            }
        }

        foreach (var g in Enumerable.Empty<Group>())
        {
            EditorGUILayout.BeginVertical("box");
            EditorGUILayout.BeginHorizontal();
            g.generate = EditorGUILayout.ToggleLeft("Aktiv", g.generate, GUILayout.Width(70));

            if (g.items.Count > 1)
                g.reuse = EditorGUILayout.ToggleLeft("Reuse", g.reuse, GUILayout.Width(70));
            else GUILayout.Space(70);

            GUILayout.Label(g.description, GUILayout.Width(260));
            GUILayout.Label(BuildHierarchySummary(g), _hierarchyStyle, GUILayout.Width(190));
            GUILayout.Label($"{g.size.x:F2}×{g.size.z:F2}×{g.size.y:F2} m", GUILayout.Width(120));
            GUILayout.Label($"{g.items.Count}×", GUILayout.Width(40));
            EditorGUILayout.EndHorizontal();

            List<string> hierarchyDetails = BuildHierarchyDetails(g);
            foreach (string detail in hierarchyDetails)
            {
                EditorGUILayout.BeginHorizontal();
                GUILayout.Space(150);
                GUILayout.Label(detail, _hierarchyStyle, GUILayout.ExpandWidth(true));
                EditorGUILayout.EndHorizontal();
            }

            EditorGUILayout.EndVertical();
        }

        EditorGUILayout.EndScrollView();
        GUILayout.FlexibleSpace();

        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Weiter zu Bild-Schritt", GUILayout.Height(32)))
        {
            _phase  = Phase.Images;
            _scroll = Vector2.zero;
            _ = RunGenerateImages(autoStart:true);
        }
        if (GUILayout.Button("Schließen", GUILayout.Height(32))) Close();
        EditorGUILayout.EndHorizontal();
    }

    private static string BuildHierarchySummary(Group group)
    {
        int hierarchyCount = group.items.Count(HasDevDescriptionHierarchy);
        if (hierarchyCount == 0)
        {
            return "Hierarchie: keine";
        }

        int parentCount = group.items.Count(IsDevDescriptionParent);
        int childCount = group.items.Count(IsDevDescriptionChild);
        if (group.items.Count == 1)
        {
            return $"Hierarchie: {GetHierarchyRole(group.items[0])}";
        }

        return $"Hierarchie: {hierarchyCount}/{group.items.Count} | P:{parentCount} C:{childCount}";
    }

    private Dictionary<DevDescription, Group> BuildGroupLookup()
    {
        Dictionary<DevDescription, Group> lookup = new();
        foreach (Group group in _groups)
        {
            foreach (DevDescription item in group.items)
            {
                if (item != null && !lookup.ContainsKey(item))
                {
                    lookup.Add(item, group);
                }
            }
        }

        return lookup;
    }

    private void DrawHierarchyConfigNode(DevDescription item,
                                         Dictionary<DevDescription, Group> groupByItem,
                                         HashSet<DevDescription> allItems,
                                         HashSet<DevDescription> drawnItems,
                                         int depth)
    {
        if (item == null || drawnItems.Contains(item) || !groupByItem.TryGetValue(item, out Group group))
        {
            return;
        }

        drawnItems.Add(item);
        DrawConfigTreeRow(item, group, depth);

        List<DevDescription> children = allItems
            .Where(child => GetParentDevDescription(child) == item)
            .OrderBy(child => child.transform.GetSiblingIndex())
            .ThenBy(child => child.name)
            .ToList();

        foreach (DevDescription child in children)
        {
            DrawHierarchyConfigNode(child, groupByItem, allItems, drawnItems, depth + 1);
        }
    }

    private void DrawConfigTreeRow(DevDescription item, Group group, int depth)
    {
        EditorGUILayout.BeginHorizontal();
        GUILayout.Space(depth * 28);
        group.generate = EditorGUILayout.ToggleLeft("Aktiv", group.generate, GUILayout.Width(70));

        if (group.items.Count > 1)
            group.reuse = EditorGUILayout.ToggleLeft("Reuse", group.reuse, GUILayout.Width(70));
        else GUILayout.Space(70);

        GUILayout.Label(GetHierarchyRole(item), _hierarchyStyle, GUILayout.Width(92));
        GUILayout.Label(item.name, GUILayout.Width(210));
        GUILayout.Label(group.description, GUILayout.Width(260));
        GUILayout.Label($"{group.size.x:F2} x {group.size.z:F2} x {group.size.y:F2} m", GUILayout.Width(120));
        GUILayout.Label($"{group.items.Count}x", GUILayout.Width(40));
        EditorGUILayout.EndHorizontal();
    }

    private void DrawFlatConfigGroup(Group group, HashSet<DevDescription> drawnItems)
    {
        List<DevDescription> flatItems = group.items
            .Where(item => item != null && !drawnItems.Contains(item))
            .OrderBy(item => item.name)
            .ToList();
        if (flatItems.Count == 0)
        {
            return;
        }

        EditorGUILayout.BeginVertical("box");
        EditorGUILayout.BeginHorizontal();
        group.generate = EditorGUILayout.ToggleLeft("Aktiv", group.generate, GUILayout.Width(70));

        if (group.items.Count > 1)
            group.reuse = EditorGUILayout.ToggleLeft("Reuse", group.reuse, GUILayout.Width(70));
        else GUILayout.Space(70);

        GUILayout.Label("Root", _hierarchyStyle, GUILayout.Width(92));
        GUILayout.Label(flatItems.Count == 1 ? flatItems[0].name : $"{flatItems.Count} Objekte", GUILayout.Width(210));
        GUILayout.Label(group.description, GUILayout.Width(260));
        GUILayout.Label($"{group.size.x:F2} x {group.size.z:F2} x {group.size.y:F2} m", GUILayout.Width(120));
        GUILayout.Label($"{group.items.Count}x", GUILayout.Width(40));
        EditorGUILayout.EndHorizontal();

        if (flatItems.Count > 1)
        {
            foreach (DevDescription item in flatItems)
            {
                EditorGUILayout.BeginHorizontal();
                GUILayout.Space(150);
                GUILayout.Label(item.name, _hierarchyStyle, GUILayout.ExpandWidth(true));
                EditorGUILayout.EndHorizontal();
            }
        }

        foreach (DevDescription item in flatItems)
        {
            drawnItems.Add(item);
        }

        EditorGUILayout.EndVertical();
    }

    private static List<string> BuildHierarchyDetails(Group group)
    {
        List<string> details = new();
        foreach (DevDescription item in group.items.OrderBy(GetHierarchyDepth).ThenBy(dd => dd.name))
        {
            if (!HasDevDescriptionHierarchy(item))
            {
                continue;
            }

            DevDescription parent = GetParentDevDescription(item);
            int childCount = CountChildDevDescriptions(item);
            string parentInfo = parent == null ? "" : $" | parent: {parent.name}";
            string childInfo = childCount == 0 ? "" : $" | children: {childCount}";
            details.Add($"{GetHierarchyRole(item)} | {GetTransformPath(item.transform)}{parentInfo}{childInfo}");
        }

        return details;
    }

    private static bool HasDevDescriptionHierarchy(DevDescription item)
    {
        return IsDevDescriptionParent(item) || IsDevDescriptionChild(item);
    }

    private static bool IsDevDescriptionParent(DevDescription item)
    {
        return CountChildDevDescriptions(item) > 0;
    }

    private static bool IsDevDescriptionChild(DevDescription item)
    {
        return GetParentDevDescription(item) != null;
    }

    private static string GetHierarchyRole(DevDescription item)
    {
        bool isParent = IsDevDescriptionParent(item);
        bool isChild = IsDevDescriptionChild(item);
        if (isParent && isChild) return "Parent+Child";
        if (isParent) return "Parent";
        if (isChild) return "Child";
        return "Root";
    }

    private static DevDescription GetParentDevDescription(DevDescription item)
    {
        if (item == null || item.transform == null)
        {
            return null;
        }

        Transform current = item.transform.parent;
        while (current != null)
        {
            DevDescription parent = current.GetComponent<DevDescription>();
            if (parent != null)
            {
                return parent;
            }

            current = current.parent;
        }

        return null;
    }

    private static int CountChildDevDescriptions(DevDescription item)
    {
        if (item == null)
        {
            return 0;
        }

        return item.GetComponentsInChildren<DevDescription>(true)
            .Count(child => child != null && child != item);
    }

    private static string GetTransformPath(Transform transform)
    {
        if (transform == null)
        {
            return "";
        }

        Stack<string> names = new();
        Transform current = transform;
        while (current != null)
        {
            names.Push(current.name);
            current = current.parent;
        }

        return string.Join("/", names);
    }

    /*===== 2) BILDER ==========================================================*/
    private void SetAllGroupsActive(bool active)
    {
        foreach (var g in _groups)
        {
            g.generate = active;
        }

        Repaint();
    }

    private void DrawImages()
    {
        EditorGUILayout.LabelField("2 | Bilder prüfen", EditorStyles.boldLabel);
        DrawProgress();

        _scroll = EditorGUILayout.BeginScrollView(_scroll);
        foreach (var g in _groups.Where(x => x.generate))
        {
            DrawImageRow(g, g.reuse ? (object)g : null);

            if (!g.reuse)
                foreach (var dd in g.items) DrawImageRow(g, dd, 40);
        }
        EditorGUILayout.EndScrollView();

        GUILayout.FlexibleSpace();
        EditorGUILayout.BeginHorizontal();
        using (new EditorGUI.DisabledScope(_busy))
        {
            if (GUILayout.Button("Alle Bilder generieren", GUILayout.Height(32)))
                _ = RunGenerateImages(autoStart:false);
        }
        bool ready = _groups.Where(g => g.generate).All(AllApproved);
        using (new EditorGUI.DisabledScope(!ready || _busy))
        {
            if (GUILayout.Button("Weiter zu 3D-Schritt", GUILayout.Height(32)))
            {
                _phase = Phase.Models;
                _scroll = Vector2.zero;
            }
        }
        if (!_busy)
            if (GUILayout.Button("Zurück", GUILayout.Height(32)))
            {
                _phase = Phase.Config;
                _scroll = Vector2.zero;
            }
        if (_busy && GUILayout.Button("Abbrechen", GUILayout.Height(32))) _cancel = true;
        EditorGUILayout.EndHorizontal();
    }

    private void DrawImageRow(Group g, object key, int indent = 0)
    {
        _img.TryGetValue(key ?? g, out var info);
        bool ok = info?.approved ?? false;
        Texture prev = info?.preview ?? Texture2D.grayTexture;

        using (new EditorGUI.DisabledScope(_busy))
        {
            EditorGUILayout.BeginHorizontal();
            GUILayout.Space(indent);
            GUILayout.Box(prev, GUILayout.Width(64), GUILayout.Height(64));

            /*— Aktionen —*/
            GUILayout.BeginVertical();
            if (GUILayout.Button("⟳ Bild neu", GUILayout.Width(92)))
                _ = (key is Group ? GenerateImageForItem((Group)key, ((Group)key).items[0], true)
                                  : GenerateImageForItem(g, (DevDescription)key, true));
            if (info != null)
            {
                bool approved = GUILayout.Toggle(ok, "✓ OK", GUILayout.Width(60));
                if (approved != info.approved)
                {
                    info.approved = approved;
                    PersistImageApproval(info);
                }
            }
            else
                GUILayout.Toggle(false, "✓ OK", GUILayout.Width(60));
            GUILayout.EndVertical();

            /*— Prompt & Denoise —*/
            GUILayout.BeginVertical(GUILayout.Width(260));
            string promptOld = info?.editPrompt ?? "";
            string promptNew = EditorGUILayout.TextField(promptOld, GUILayout.Width(250));
            if (info != null) info.editPrompt = promptNew;

            float denoiseOld = info?.denoise ?? 0.8f;
            float denoiseNew = EditorGUILayout.Slider(denoiseOld, 0f, 1f, GUILayout.Width(250));
            if (info != null) info.denoise = denoiseNew;

            using (new EditorGUI.DisabledScope(info == null || string.IsNullOrWhiteSpace(promptNew)))
            {
                if (GUILayout.Button("✎ Ändern", GUILayout.Width(92)))
                    _ = (key is Group
                            ? TransformImageForItem((Group)key, ((Group)key).items[0])
                            : TransformImageForItem(g, (DevDescription)key));
            }
            GUILayout.EndVertical();

            GUILayout.FlexibleSpace();
            GUILayout.Label(key is DevDescription d ? d.name : g.description,
                            ok ? _green : EditorStyles.label, GUILayout.Width(340));
            EditorGUILayout.EndHorizontal();
        }
    }

    private bool AllApproved(Group g)
    {
        if (g.reuse) return _img.TryGetValue(g, out var i) && i.approved;
        return g.items.All(dd => _img.TryGetValue(dd, out var i) && i.approved);
    }

    /*===== 3) MODELLE =========================================================*/
    private void DrawModels()
    {
        EditorGUILayout.LabelField("3 | 3D-Generierung", EditorStyles.boldLabel);
        DrawProgress();

        _scroll = EditorGUILayout.BeginScrollView(_scroll);
        foreach (var g in _groups.Where(x => x.generate))
        {
            DrawModelRow(g, g.reuse ? (object)g : null);

            if (!g.reuse)
                foreach (var dd in g.items) DrawModelRow(g, dd, 40);
        }
        EditorGUILayout.EndScrollView();

        GUILayout.FlexibleSpace();
        EditorGUILayout.BeginHorizontal();
        using (new EditorGUI.DisabledScope(_busy))
        {
            if (GUILayout.Button("Start 3D-Generierung", GUILayout.Height(32)))
                _ = RunGenerateModels();
            if (GUILayout.Button("Vorhandene GLBs platzieren", GUILayout.Height(32)))
                PlaceExistingGeneratedModelsForScene();
        }
        if (!_busy)
            if (GUILayout.Button("Zurück", GUILayout.Height(32)))
            {
                _phase = Phase.Images;
                _scroll = Vector2.zero;
            }
        if (_busy && GUILayout.Button("Abbrechen", GUILayout.Height(32))) _cancel = true;
        EditorGUILayout.EndHorizontal();
    }

    private void DrawModelRow(Group g, object key, int indent = 0)
    {
        _img.TryGetValue(key ?? g, out var info);
        Texture prev = info?.preview ?? Texture2D.grayTexture;

        bool done = _modelsDone.Contains(key ?? g);
        GUIStyle st = done ? _green : EditorStyles.label;

        EditorGUILayout.BeginHorizontal();
        GUILayout.Space(indent);
        GUILayout.Box(prev, GUILayout.Width(64), GUILayout.Height(64));
        GUILayout.Space(6);
        GUILayout.Label(key is DevDescription d ? d.name : g.description, st, GUILayout.Width(340));
        EditorGUILayout.EndHorizontal();
    }

    private void DrawProgress()
    {
        if (!_busy) return;
        float p = _todo == 0 ? 0f : _done / (float)_todo;
        Rect r  = GUILayoutUtility.GetRect(18, 22, GUILayout.ExpandWidth(true));
        EditorGUI.ProgressBar(r, p, $"{_done}/{_todo}  –  {_current}");
        GUILayout.Space(4);
    }

    /*===== NETZWERK / LOGIK ===================================================*/
    private async Task RunAutomaticGeneration()
    {
        _cancel = false;
        List<ModelJob> modelJobs = BuildModelJobs(_groups.Where(g => g.generate).ToList());
        HashSet<string> imageCacheIdsWithModels = PreflightAvailableModels(modelJobs);

        // Der GLB-Preflight läuft bewusst vor der Bildphase. Bereits fertige
        // Modelle benötigen nach einem Domain-Reload kein erneut bezahltes Bild.
        await RunGenerateImages(autoStart:true, imageCacheIdsWithModels);
        if (_cancel)
        {
            return;
        }

        _phase = Phase.Models;
        Repaint();
        await RunGenerateModels(generateMissingImages:true);
    }

    private async Task RunGenerateImages(bool autoStart,
                                         HashSet<string> skippedImageCacheIds = null)
    {
        var todoGroups = _groups.Where(g => g.generate).ToList();
        if (todoGroups.Count == 0)
        {
            Debug.LogWarning("[IMG] Keine Gruppen aktiv.");
            return;
        }

        bool refresh = !autoStart;
        List<ImageJob> imageJobs = BuildImageJobs(todoGroups, refresh, skippedImageCacheIds);
        if (imageJobs.Count == 0)
        {
            Debug.Log("[IMG] Keine neuen Bilder zu generieren.");
            return;
        }

        _busy = true; _cancel = false;
        _todo = imageJobs.Count; _done = 0;

        using HttpClient cli = new() { Timeout = TimeSpan.FromMinutes(15) };
        try
        {
            if (UsesExternalImageBackend())
            {
                Debug.Log($"[IMG] Starte {imageJobs.Count} externe Bildgenerierungen parallel ({ImageBackend}).");
                await Task.WhenAll(imageJobs.Select(job => GenerateImageJob(job, refresh, cli)));
            }
            else
            {
                foreach (ImageJob job in imageJobs)
                {
                    if (_cancel) break;
                    await GenerateImageJob(job, refresh, cli);
                }
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"[IMG] Bildgenerierung abgebrochen: {ex}");
        }
        finally
        {
            _busy = false;
            Repaint();
        }
    }

    private List<ImageJob> BuildImageJobs(List<Group> groups, bool refresh,
                                          HashSet<string> skippedImageCacheIds = null)
    {
        List<ImageJob> jobs = new();
        foreach (Group group in groups)
        {
            if (group.reuse)
            {
                DevDescription item = group.items[0];
                string imageCacheId = BuildImageCacheId(group, item);
                if (skippedImageCacheIds != null && skippedImageCacheIds.Contains(imageCacheId))
                {
                    continue;
                }

                bool available = !refresh && TryLoadCachedImage(group, item, out _);
                if (refresh || !available)
                {
                    jobs.Add(new ImageJob(group, item));
                }

                continue;
            }

            foreach (DevDescription item in group.items)
            {
                string imageCacheId = BuildImageCacheId(group, item);
                if (skippedImageCacheIds != null && skippedImageCacheIds.Contains(imageCacheId))
                {
                    continue;
                }

                bool available = !refresh && TryLoadCachedImage(group, item, out _);
                if (refresh || !available)
                {
                    jobs.Add(new ImageJob(group, item));
                }
            }
        }

        return jobs;
    }

    private static bool UsesExternalImageBackend()
    {
        return !string.Equals(ImageBackend?.Trim(), "local", StringComparison.OrdinalIgnoreCase);
    }

    private async Task GenerateImageJob(ImageJob job, bool refresh, HttpClient cli)
    {
        try
        {
            ImageInfo result = await GenerateImageForItem(job.Group, job.Item, refresh, cli);
            if (result == null)
            {
                Progress($"{job.Item.name} (failed)");
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"[IMG] Fehler bei {job.Item.name}: {ex}");
            Progress($"{job.Item.name} (failed)");
        }
    }

    private async Task<ImageInfo> GenerateImageForItem(Group g, DevDescription dd,
                                                       bool refresh, HttpClient cli = null,
                                                       bool reportProgress = true)
    {
        cli ??= new HttpClient { Timeout = TimeSpan.FromMinutes(15) };
        object key = g.reuse ? (object)g : dd;
        if (!refresh && TryLoadCachedImage(g, dd, out ImageInfo cached)) return cached;

        string imageCacheId = BuildImageCacheId(g, dd);
        string prompt = BuildImagePrompt(g, dd);

        float denoise = _img.TryGetValue(key, out var existing) ? existing.denoise : 0.8f;
        var payload = new ImagePayload
        {
            // Manuelles "Bild neu" soll eine neue Variante erzeugen. Der
            // automatische Pfad verwendet dagegen eine deterministische UUID,
            // damit auch das Backend denselben Job wiederaufnehmen kann.
            job_id         = refresh ? Guid.NewGuid().ToString("D") : imageCacheId,
            image_backend   = ImageBackend,
            positive_prompt = prompt,
            negative_prompt = ImageBackend == "local" ? NegativeLocal : "",
            denoise         = denoise
        };
        string json = JsonUtility.ToJson(payload);

        var resp = await cli.PostAsync(_apiImage,
            new StringContent(json, Encoding.UTF8, "application/json"));
        if (!resp.IsSuccessStatusCode)
        {
            Debug.LogError($"[IMG] Fehler: {resp.StatusCode} – {await resp.Content.ReadAsStringAsync()}");
            return null;
        }
        byte[] data = await resp.Content.ReadAsByteArrayAsync();
        var tex = new Texture2D(2, 2);
        if (!tex.LoadImage(data))
        {
            DestroyImmediate(tex);
            Debug.LogError($"[IMG] Ungültige Bildantwort für {dd.name}.");
            return null;
        }

        string contentHash = ComputeSha256Hex(data);

        _img[key] = new ImageInfo
        {
            data     = data,
            preview  = tex,
            approved = !refresh,
            denoise  = denoise,
            cacheId  = imageCacheId,
            contentHash = contentHash
        };
        PersistImageCache(imageCacheId, data, contentHash, approved:!refresh);
        if (reportProgress) Progress(dd.name);
        return _img[key];
    }

    private async Task TransformImageForItem(Group g, DevDescription dd, HttpClient cli = null)
    {
        object key = g.reuse ? (object)g : dd;
        if (!_img.TryGetValue(key, out var info) || string.IsNullOrWhiteSpace(info.editPrompt))
        {
            Debug.LogWarning("[IMG-Edit] Kein Ursprungsbild oder Prompt leer.");
            return;
        }

        cli ??= new HttpClient { Timeout = TimeSpan.FromMinutes(15) };
        var payload = new ImagePayload
        {
            job_id            = BuildDeterministicUuid(
                $"{info.cacheId}|edit|{info.contentHash}|{info.editPrompt}|" +
                info.denoise.ToString("R", CultureInfo.InvariantCulture)),
            image_backend      = ImageBackend,
            positive_prompt    = info.editPrompt,
            negative_prompt    = ImageBackend == "local" ? NegativeLocal : "",
            base_image_base64  = Convert.ToBase64String(info.data),
            denoise            = info.denoise
        };
        string json = JsonUtility.ToJson(payload);

        _busy = true; _todo = 1; _done = 0; _current = dd.name;
        var resp = await cli.PostAsync(_apiImage,
            new StringContent(json, Encoding.UTF8, "application/json"));
        _busy = false;

        if (!resp.IsSuccessStatusCode)
        {
            Debug.LogError($"[IMG-Edit] Fehler: {resp.StatusCode} – {await resp.Content.ReadAsStringAsync()}");
            return;
        }
        byte[] data = await resp.Content.ReadAsByteArrayAsync();
        var tex = new Texture2D(2, 2);
        if (!tex.LoadImage(data))
        {
            DestroyImmediate(tex);
            Debug.LogError($"[IMG-Edit] Ungültige Bildantwort für {dd.name}.");
            return;
        }

        info.data      = data;
        info.preview   = tex;
        info.approved  = false;
        info.cacheId   = BuildImageCacheId(g, dd);
        info.contentHash = ComputeSha256Hex(data);
        PersistImageCache(info.cacheId, data, info.contentHash, approved:false);
        Repaint();
    }

    private async Task RunGenerateModels(bool generateMissingImages = false)
    {
        var todoGroups = _groups.Where(g => g.generate).ToList();
        if (todoGroups.Count == 0)
        {
            Debug.LogWarning("[GLB] Keine Gruppen aktiv.");
            return;
        }

        List<ModelJob> modelJobs = BuildModelJobs(todoGroups);
        if (modelJobs.Count == 0)
        {
            Debug.Log("[GLB] Keine Modelle zu generieren.");
            return;
        }

        _busy = true; _cancel = false; _modelsDone.Clear();
        _todo = modelJobs.Count; _done = 0;

        try
        {
            string absoluteTargetFolder = ToAbsoluteProjectPath(TargetFolder);
            if (!Directory.Exists(absoluteTargetFolder)) Directory.CreateDirectory(absoluteTargetFolder);
            using HttpClient cli = new() { Timeout = TimeSpan.FromMinutes(150) };

            Dictionary<Transform, Transform> placedByPlaceholder = new();
            HashSet<Transform> expectedGeneratedPlaceholders = BuildExpectedGeneratedPlaceholders(modelJobs);
            List<ModelPlacement> pendingPlacements = new();

            foreach (ModelJob job in modelJobs)
            {
                if (_cancel) break;

                string jobId = BuildModelJobId(job);
                object doneKey = GetModelKey(job.Group, job.CacheKey);
                try
                {
                    if (TryRegisterCompleteExistingJob(job, jobId, placedByPlaceholder))
                    {
                        _modelsDone.Add(doneKey);
                        Progress($"{job.CacheKey.name} (already placed)");
                        continue;
                    }

                    ResolvedModel resolved = null;
                    if (_preflightModels.TryGetValue(jobId, out ResolvedModel prefetched) &&
                        prefetched?.Prefab != null)
                    {
                        resolved = prefetched;
                    }
                    else
                    {
                        TryResolveCachedModel(job, out resolved, allowLegacy:true);
                    }

                    if (resolved == null)
                    {
                        ImageInfo image = await EnsureApprovedImage(job, cli, generateMissingImages);
                        if (image == null)
                        {
                            Progress($"{job.CacheKey.name} (missing image)");
                            continue;
                        }

                        string fingerprint = BuildModelFingerprint(jobId, image.contentHash);
                        if (!TryLoadExactGeneratedPrefab(job, jobId, fingerprint,
                                image.contentHash, out resolved))
                        {
                            resolved = await GenerateModelPrefab(
                                job, jobId, fingerprint, image, cli);
                        }
                    }

                    if (resolved == null)
                    {
                        Progress($"{job.CacheKey.name} (failed)");
                        continue;
                    }

                    List<DevDescription> missingTargets = RegisterExistingPlacements(
                        job.Targets, resolved.JobId, resolved.Fingerprint, placedByPlaceholder);
                    QueueOrPlaceModelTargets(missingTargets, resolved.Prefab, resolved.JobId,
                        resolved.Fingerprint, resolved.ContentSignature, resolved.AssetPath,
                        placedByPlaceholder,
                        expectedGeneratedPlaceholders, pendingPlacements);
                    FlushPendingPlacements(pendingPlacements, placedByPlaceholder,
                        expectedGeneratedPlaceholders, force:false);
                    _modelsDone.Add(doneKey);
                    _preflightModels[jobId] = resolved;
                    Progress($"{job.CacheKey.name} ({(resolved.Legacy ? "legacy cache" : "cached/generated")})");
                    Repaint();
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[GLB] Fehler bei Job {job.CacheKey.name} ({jobId}): {ex}");
                    Progress($"{job.CacheKey.name} (failed)");
                }
            }

            if (!_cancel)
            {
                FlushPendingPlacements(pendingPlacements, placedByPlaceholder,
                    expectedGeneratedPlaceholders, force:true);
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"[GLB] Initialisierung der 3D-Generierung fehlgeschlagen: {ex}");
        }
        finally
        {
            _busy = false;
            Repaint();
        }
    }

    private void PlaceExistingGeneratedModelsForScene()
    {
        List<ModelJob> modelJobs = BuildModelJobs(_groups.Where(g => g.generate).ToList());
        if (modelJobs.Count == 0)
        {
            Debug.LogWarning("[GLB] Keine Gruppen fuer vorhandene GLBs gefunden.");
            return;
        }

        _modelsDone.Clear();
        Dictionary<Transform, Transform> placedByPlaceholder = new();
        HashSet<Transform> expectedGeneratedPlaceholders = BuildExpectedGeneratedPlaceholders(modelJobs);
        List<ModelPlacement> pendingPlacements = new();
        int loadedCount = 0;
        int missingCount = 0;

        foreach (ModelJob job in modelJobs)
        {
            string jobId = BuildModelJobId(job);
            object doneKey = GetModelKey(job.Group, job.CacheKey);

            if (TryRegisterCompleteExistingJob(job, jobId, placedByPlaceholder))
            {
                _modelsDone.Add(doneKey);
                loadedCount++;
                continue;
            }

            if (!TryResolveCachedModel(job, out ResolvedModel resolved, allowLegacy:true))
            {
                missingCount++;
                continue;
            }

            List<DevDescription> missingTargets = RegisterExistingPlacements(
                job.Targets, resolved.JobId, resolved.Fingerprint, placedByPlaceholder);
            QueueOrPlaceModelTargets(missingTargets, resolved.Prefab, resolved.JobId,
                resolved.Fingerprint, resolved.ContentSignature, resolved.AssetPath,
                placedByPlaceholder,
                expectedGeneratedPlaceholders, pendingPlacements);
            FlushPendingPlacements(pendingPlacements, placedByPlaceholder,
                expectedGeneratedPlaceholders, force:false);
            _modelsDone.Add(doneKey);
            loadedCount++;
        }

        FlushPendingPlacements(pendingPlacements, placedByPlaceholder,
            expectedGeneratedPlaceholders, force:true);
        Debug.Log($"[GLB] Vorhandene GLBs platziert: {loadedCount}, fehlend: {missingCount}.");
        Repaint();
    }

    private static List<ModelJob> BuildModelJobs(List<Group> groups)
    {
        List<ModelJob> jobs = new();
        foreach (Group group in groups)
        {
            if (group.reuse)
            {
                List<DevDescription> targets = OrderTargetsForPlacement(group.items).ToList();
                if (targets.Count > 0)
                {
                    jobs.Add(new ModelJob(group, targets, targets[0]));
                }

                continue;
            }

            foreach (DevDescription item in OrderTargetsForPlacement(group.items))
            {
                jobs.Add(new ModelJob(group, new List<DevDescription> { item }, item));
            }
        }

        return jobs
            .OrderBy(job => job.Targets.Min(GetHierarchyDepth))
            .ThenBy(job => job.Targets.Max(GetHierarchyDepth))
            .ToList();
    }

    private static IEnumerable<DevDescription> OrderTargetsForPlacement(IEnumerable<DevDescription> targets)
    {
        return targets
            .Where(target => target != null && target.transform != null)
            .OrderBy(GetHierarchyDepth);
    }

    private static int GetHierarchyDepth(DevDescription dd)
    {
        if (dd == null || dd.transform == null)
        {
            return int.MaxValue;
        }

        int depth = 0;
        Transform current = dd.transform.parent;
        while (current != null)
        {
            depth++;
            current = current.parent;
        }

        return depth;
    }

    private static object GetModelKey(Group group, DevDescription cacheKey)
    {
        return group.reuse ? (object)group : cacheKey;
    }

    private async Task<ImageInfo> EnsureApprovedImage(ModelJob job, HttpClient cli,
                                                      bool allowGeneration)
    {
        object key = GetModelKey(job.Group, job.CacheKey);
        if (_img.TryGetValue(key, out ImageInfo existing) && existing.approved)
        {
            return existing;
        }

        if (TryLoadCachedImage(job.Group, job.CacheKey, out ImageInfo cached))
        {
            return cached.approved ? cached : null;
        }

        if (!allowGeneration)
        {
            Debug.LogWarning($"[GLB] Kein freigegebenes Bild für {job.CacheKey.name} vorhanden.");
            return null;
        }

        return await GenerateImageForItem(job.Group, job.CacheKey, refresh:false, cli,
            reportProgress:false);
    }

    private async Task<ResolvedModel> GenerateModelPrefab(ModelJob job, string jobId,
                                                           string fingerprint, ImageInfo info,
                                                           HttpClient cli)
    {
        var payload = new ModelPayload
        {
            job_id = fingerprint,
            image_base64 = Convert.ToBase64String(info.data)
        };
        var resp = await cli.PostAsync(_apiModel,
            new StringContent(JsonUtility.ToJson(payload), Encoding.UTF8, "application/json"));
        if (!resp.IsSuccessStatusCode)
        {
            Debug.LogError($"[GLB] Fehler: {resp.StatusCode} – {await resp.Content.ReadAsStringAsync()}");
            return null;
        }

        byte[] glb = await resp.Content.ReadAsByteArrayAsync();
        if (!IsValidGlbBytes(glb))
        {
            Debug.LogError($"[GLB] Ungültige GLB-Antwort für {job.CacheKey.name}.");
            return null;
        }

        string rel = BuildDeterministicModelAssetPath(job, fingerprint);
        string absolutePath = ToAbsoluteProjectPath(rel);
        AtomicWriteBytes(absolutePath, glb);

        if (!TryLoadModelAsset(rel, out GameObject prefab))
        {
            Debug.LogError($"[GLB] Importiertes GLB konnte nicht geladen werden: {rel}");
            return null;
        }

        string contentSignature = BuildModelContentSignature(job);
        RegisterModelCache(jobId, fingerprint, rel, info.contentHash, contentSignature);
        return new ResolvedModel
        {
            Prefab = prefab,
            JobId = jobId,
            Fingerprint = fingerprint,
            ContentSignature = contentSignature,
            AssetPath = rel,
            Legacy = false
        };
    }

    private bool TryResolveCachedModel(ModelJob job, out ResolvedModel resolved,
                                       bool allowLegacy)
    {
        resolved = null;
        string jobId = BuildModelJobId(job);
        string contentSignature = BuildModelContentSignature(job);
        string imageCacheId = BuildImageCacheId(job.Group, job.CacheKey);
        ImageCacheRecord imageRecord = FindImageCacheRecord(imageCacheId);
        if (imageRecord == null)
        {
            TryMigrateImageCacheForMarkedModel(job, imageCacheId, contentSignature);
            imageRecord = FindImageCacheRecord(imageCacheId);
        }
        ModelCacheRecord modelRecord = FindModelCacheRecord(jobId);
        string currentImageHash = imageRecord?.sha256 ?? "";

        if (modelRecord != null && !string.IsNullOrWhiteSpace(modelRecord.contentSignature) &&
            !string.Equals(modelRecord.contentSignature, contentSignature, StringComparison.Ordinal))
        {
            return false;
        }

        // Ein bewusst erneuertes/editiertes PNG invalidiert ausschließlich das
        // dazugehörige Modell. In diesem Fall darf auch kein Legacy-GLB gewinnen.
        // Alte, bereits platzierte GLBs besitzen noch keinen gespeicherten
        // imageSha256. Ein leerer Hash bedeutet "Provenienz unbekannt", nicht
        // "das Preview wurde geaendert". Erst zwei bekannte, unterschiedliche
        // Hashes sind eine echte Invalidierung. Beim erfolgreichen Laden unten
        // wird der aktuelle Hash einmalig in den Altbestand uebernommen.
        if (modelRecord != null && !string.IsNullOrWhiteSpace(currentImageHash) &&
            !string.IsNullOrWhiteSpace(modelRecord.imageSha256) &&
            !string.Equals(modelRecord.imageSha256, currentImageHash, StringComparison.OrdinalIgnoreCase))
        {
            return false;
        }

        string fingerprint = modelRecord?.fingerprint;
        if (string.IsNullOrWhiteSpace(fingerprint) && !string.IsNullOrWhiteSpace(currentImageHash))
        {
            fingerprint = BuildModelFingerprint(jobId, currentImageHash);
        }

        List<string> candidatePaths = new();
        if (!string.IsNullOrWhiteSpace(modelRecord?.assetPath))
        {
            candidatePaths.Add(modelRecord.assetPath);
        }

        if (!string.IsNullOrWhiteSpace(fingerprint))
        {
            candidatePaths.Add(BuildDeterministicModelAssetPath(job, fingerprint));
        }

        foreach (DevDescription target in job.Targets)
        {
            if (target != null && target.GeneratedInstance != null &&
                !string.IsNullOrWhiteSpace(target.GeneratedAssetPath) &&
                (string.IsNullOrWhiteSpace(target.GeneratedContentSignature) ||
                 string.Equals(target.GeneratedContentSignature, contentSignature,
                     StringComparison.Ordinal)))
            {
                candidatePaths.Add(target.GeneratedAssetPath);
            }
        }

        foreach (string candidatePath in candidatePaths.Where(path => !string.IsNullOrWhiteSpace(path))
                     .Distinct(StringComparer.OrdinalIgnoreCase))
        {
            if (!TryLoadModelAsset(candidatePath, out GameObject prefab)) continue;

            DevDescription marker = job.Targets.FirstOrDefault(target => target != null &&
                target.GeneratedInstance != null &&
                string.Equals(target.GeneratedAssetPath, candidatePath,
                    StringComparison.OrdinalIgnoreCase));
            if (marker != null && !string.IsNullOrWhiteSpace(marker.GeneratedContentSignature) &&
                !string.Equals(marker.GeneratedContentSignature, contentSignature,
                    StringComparison.Ordinal))
            {
                continue;
            }

            string resolvedFingerprint = fingerprint;
            if (string.IsNullOrWhiteSpace(resolvedFingerprint))
            {
                resolvedFingerprint = marker?.GeneratedFingerprint;
            }

            if (string.IsNullOrWhiteSpace(resolvedFingerprint))
            {
                resolvedFingerprint = BuildLegacyModelFingerprint(jobId, candidatePath);
            }

            if (marker != null &&
                (!string.Equals(marker.GeneratedJobId, jobId, StringComparison.Ordinal) ||
                 !string.Equals(marker.GeneratedContentSignature, contentSignature,
                     StringComparison.Ordinal)))
            {
                if (!string.Equals(marker.GeneratedJobId, jobId, StringComparison.Ordinal))
                {
                    RemoveSupersededModelCacheRecord(marker.GeneratedJobId, candidatePath);
                }
                AdoptMarkedSceneModel(job, jobId, resolvedFingerprint, contentSignature,
                    candidatePath);
            }

            RegisterModelCache(jobId, resolvedFingerprint, NormalizeProjectPath(candidatePath),
                currentImageHash, contentSignature);
            resolved = new ResolvedModel
            {
                Prefab = prefab,
                JobId = jobId,
                Fingerprint = resolvedFingerprint,
                ContentSignature = contentSignature,
                AssetPath = NormalizeProjectPath(candidatePath),
                Legacy = !candidatePath.Contains("_cache_", StringComparison.OrdinalIgnoreCase)
            };
            return true;
        }

        return allowLegacy && TryLoadLegacyGeneratedPrefab(job, jobId, currentImageHash,
            contentSignature, out resolved);
    }

    private bool TryLoadExactGeneratedPrefab(ModelJob job, string jobId, string fingerprint,
                                              string imageHash, out ResolvedModel resolved)
    {
        resolved = null;
        string assetPath = BuildDeterministicModelAssetPath(job, fingerprint);
        if (!TryLoadModelAsset(assetPath, out GameObject prefab)) return false;

        string contentSignature = BuildModelContentSignature(job);
        RegisterModelCache(jobId, fingerprint, assetPath, imageHash, contentSignature);
        resolved = new ResolvedModel
        {
            Prefab = prefab,
            JobId = jobId,
            Fingerprint = fingerprint,
            ContentSignature = contentSignature,
            AssetPath = assetPath,
            Legacy = false
        };
        return true;
    }

    private bool TryLoadLegacyGeneratedPrefab(ModelJob job, string jobId, string imageHash,
                                               string contentSignature,
                                               out ResolvedModel resolved)
    {
        resolved = null;
        string absoluteFolder = ToAbsoluteProjectPath(TargetFolder);
        if (!Directory.Exists(absoluteFolder)) return false;

        HashSet<string> legacyAssetsClaimedByOtherJobs = GetCacheManifest().models
            .Where(record => !string.Equals(record.jobId, jobId, StringComparison.Ordinal) &&
                             !string.IsNullOrWhiteSpace(record.assetPath))
            .Select(record => NormalizeProjectPath(record.assetPath))
            .ToHashSet(StringComparer.OrdinalIgnoreCase);

        HashSet<string> candidateNames = new(StringComparer.OrdinalIgnoreCase);
        if (job.CacheKey != null) candidateNames.Add(job.CacheKey.name);
        foreach (DevDescription target in OrderTargetsForPlacement(job.Targets))
        {
            candidateNames.Add(target.name);
        }

        List<FileInfo> candidates = new();
        foreach (string candidateName in candidateNames)
        {
            string sanitizedName = Sanitize(candidateName);
            string pattern = $"{sanitizedName}_*.glb";
            foreach (string path in Directory.GetFiles(absoluteFolder, pattern))
            {
                // Neue fingerprintbasierte Dateien dürfen niemals als Legacy-
                // Treffer eines anderen Jobs interpretiert werden. Freie Suffixe
                // wie "recovered_after_timeout" bleiben dagegen ausdrücklich gültig.
                if (Path.GetFileName(path).Contains("_cache_", StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }

                if (!IsAcceptedLegacyModelFileName(Path.GetFileName(path), sanitizedName))
                {
                    continue;
                }

                candidates.Add(new FileInfo(path));
            }
        }

        foreach (FileInfo candidate in candidates
                     .GroupBy(file => file.FullName, StringComparer.OrdinalIgnoreCase)
                     .Select(group => group.First())
                     .OrderByDescending(file => file.LastWriteTimeUtc))
        {
            string relativePath = $"{TargetFolder}/{candidate.Name}";
            if (legacyAssetsClaimedByOtherJobs.Contains(NormalizeProjectPath(relativePath)))
            {
                continue;
            }

            if (!TryLoadModelAsset(relativePath, out GameObject prefab)) continue;

            string fingerprint = BuildLegacyModelFingerprint(jobId, relativePath);
            RegisterModelCache(jobId, fingerprint, relativePath, imageHash, contentSignature);
            Debug.Log($"[GLB] Legacy-Cache übernommen: {relativePath} -> {jobId}");
            resolved = new ResolvedModel
            {
                Prefab = prefab,
                JobId = jobId,
                Fingerprint = fingerprint,
                ContentSignature = contentSignature,
                AssetPath = relativePath,
                Legacy = true
            };
            return true;
        }

        return false;
    }

    private void RefreshCachedModelStatus()
    {
        _modelsDone.Clear();
        if (_groups.Count == 0) return;

        List<ModelJob> jobs = BuildModelJobs(_groups.Where(group => group.generate).ToList());
        PreflightAvailableModels(jobs);
        Debug.Log($"[GLB] Cache-Status der offenen Szene: {_modelsDone.Count}/{jobs.Count} " +
                  "Modell-Jobs bereits vorhanden; nur der Rest wird generiert.");
    }

    private HashSet<string> PreflightAvailableModels(List<ModelJob> modelJobs)
    {
        HashSet<string> coveredImageCacheIds = new(StringComparer.Ordinal);
        _preflightModels.Clear();

        foreach (ModelJob job in modelJobs)
        {
            string jobId = BuildModelJobId(job);
            bool available = TryResolveCachedModel(job, out ResolvedModel resolved, allowLegacy:true);
            if (available)
            {
                _preflightModels[jobId] = resolved;
            }
            else
            {
                available = HasCompleteExistingJob(job, jobId);
            }

            if (!available) continue;

            coveredImageCacheIds.Add(BuildImageCacheId(job.Group, job.CacheKey));
            _modelsDone.Add(GetModelKey(job.Group, job.CacheKey));
        }

        return coveredImageCacheIds;
    }

    private bool HasCompleteExistingJob(ModelJob job, string jobId)
    {
        if (job.Targets.Count == 0) return false;

        string imageCacheId = BuildImageCacheId(job.Group, job.CacheKey);
        string currentImageHash = FindImageCacheRecord(imageCacheId)?.sha256 ?? "";
        ModelCacheRecord modelRecord = FindModelCacheRecord(jobId);
        string expectedFingerprint = "";

        if (!string.IsNullOrWhiteSpace(currentImageHash))
        {
            if (modelRecord == null ||
                (!string.IsNullOrWhiteSpace(modelRecord.imageSha256) &&
                 !string.Equals(modelRecord.imageSha256, currentImageHash,
                    StringComparison.OrdinalIgnoreCase)))
            {
                return false;
            }

            expectedFingerprint = modelRecord.fingerprint;
        }

        string sharedFingerprint = null;
        foreach (DevDescription target in job.Targets)
        {
            if (target == null || target.GeneratedInstance == null ||
                !string.Equals(target.GeneratedJobId, jobId, StringComparison.Ordinal))
            {
                return false;
            }

            if (!string.IsNullOrWhiteSpace(expectedFingerprint) &&
                !string.Equals(target.GeneratedFingerprint, expectedFingerprint,
                    StringComparison.Ordinal))
            {
                return false;
            }

            sharedFingerprint ??= target.GeneratedFingerprint;
            if (!string.Equals(sharedFingerprint, target.GeneratedFingerprint,
                    StringComparison.Ordinal))
            {
                return false;
            }
        }

        return !string.IsNullOrWhiteSpace(sharedFingerprint);
    }

    private bool TryRegisterCompleteExistingJob(ModelJob job, string jobId,
                                                 Dictionary<Transform, Transform> placedByPlaceholder)
    {
        if (!HasCompleteExistingJob(job, jobId)) return false;

        foreach (DevDescription target in OrderTargetsForPlacement(job.Targets))
        {
            ResyncExistingPlacement(target, placedByPlaceholder);
            placedByPlaceholder[target.transform] = target.GeneratedInstance.transform;
        }

        return true;
    }

    private static List<DevDescription> RegisterExistingPlacements(
        IEnumerable<DevDescription> targets, string jobId, string fingerprint,
        Dictionary<Transform, Transform> placedByPlaceholder)
    {
        List<DevDescription> missing = new();
        foreach (DevDescription target in OrderTargetsForPlacement(targets))
        {
            if (target.HasGeneratedInstance(jobId, fingerprint))
            {
                ResyncExistingPlacement(target, placedByPlaceholder);
                placedByPlaceholder[target.transform] = target.GeneratedInstance.transform;
            }
            else
            {
                missing.Add(target);
            }
        }

        return missing;
    }

    private static void ResyncExistingPlacement(
        DevDescription target,
        IReadOnlyDictionary<Transform, Transform> placedByPlaceholder)
    {
        if (target == null || target.GeneratedInstance == null) return;

        Transform generatedParent = ResolveGeneratedParent(
            target.transform.parent, placedByPlaceholder);
        ApplyPlacementTransform(target.GeneratedInstance, target.transform, generatedParent);
        target.GeneratedInstance.SetActive(true);
        target.gameObject.SetActive(false);
        CozyRoomLighting.ConfigureFixture(target);
        EditorUtility.SetDirty(target.GeneratedInstance);
        EditorUtility.SetDirty(target);
        if (target.gameObject.scene.IsValid())
        {
            EditorSceneManager.MarkSceneDirty(target.gameObject.scene);
        }
    }

    private static HashSet<Transform> BuildExpectedGeneratedPlaceholders(List<ModelJob> modelJobs)
    {
        HashSet<Transform> expected = new();
        foreach (ModelJob job in modelJobs)
        {
            foreach (DevDescription target in OrderTargetsForPlacement(job.Targets))
            {
                expected.Add(target.transform);
            }
        }

        return expected;
    }

    private static void QueueOrPlaceModelTargets(IEnumerable<DevDescription> targets,
                                                 GameObject prefab, string jobId,
                                                 string fingerprint, string contentSignature,
                                                 string assetPath,
                                                 Dictionary<Transform, Transform> placedByPlaceholder,
                                                 HashSet<Transform> expectedGeneratedPlaceholders,
                                                 List<ModelPlacement> pendingPlacements)
    {
        foreach (DevDescription target in OrderTargetsForPlacement(targets))
        {
            ModelPlacement placement = new(target, prefab, jobId, fingerprint,
                contentSignature, assetPath);
            if (!CanPlaceNow(target, placedByPlaceholder, expectedGeneratedPlaceholders) ||
                !TryPlaceModelPlacement(placement, placedByPlaceholder))
            {
                pendingPlacements.Add(placement);
            }
        }
    }

    private static void FlushPendingPlacements(List<ModelPlacement> pendingPlacements,
                                               Dictionary<Transform, Transform> placedByPlaceholder,
                                               HashSet<Transform> expectedGeneratedPlaceholders,
                                               bool force)
    {
        bool placedAny;
        do
        {
            placedAny = false;
            List<ModelPlacement> orderedPending = pendingPlacements
                .OrderBy(placement => GetHierarchyDepth(placement.Target))
                .ToList();
            pendingPlacements.Clear();

            foreach (ModelPlacement placement in orderedPending)
            {
                if (!force && !CanPlaceNow(placement.Target, placedByPlaceholder, expectedGeneratedPlaceholders))
                {
                    pendingPlacements.Add(placement);
                    continue;
                }

                if (TryPlaceModelPlacement(placement, placedByPlaceholder))
                {
                    placedAny = true;
                }
            }
        }
        while (!force && placedAny && pendingPlacements.Count > 0);
    }

    private static bool TryPlaceModelPlacement(ModelPlacement placement,
                                               Dictionary<Transform, Transform> placedByPlaceholder)
    {
        GameObject instance = PlacePrefab(placement.Prefab, placement.Target, placedByPlaceholder,
            placement.JobId, placement.Fingerprint, placement.ContentSignature,
            placement.AssetPath);
        if (instance == null)
        {
            return false;
        }

        placedByPlaceholder[placement.Target.transform] = instance.transform;
        return true;
    }

    private static bool CanPlaceNow(DevDescription target,
                                    Dictionary<Transform, Transform> placedByPlaceholder,
                                    HashSet<Transform> expectedGeneratedPlaceholders)
    {
        Transform requiredParent = FindNearestExpectedGeneratedAncestor(
            target.transform.parent, expectedGeneratedPlaceholders);
        return requiredParent == null || placedByPlaceholder.ContainsKey(requiredParent);
    }

    private static Transform FindNearestExpectedGeneratedAncestor(
        Transform current, HashSet<Transform> expectedGeneratedPlaceholders)
    {
        while (current != null)
        {
            if (expectedGeneratedPlaceholders.Contains(current))
            {
                return current;
            }

            current = current.parent;
        }

        return null;
    }

    /*────────── UTILS ────────────────────────────────────*/

    /// <summary>
    /// Skaliert das Instanz-Objekt so, dass es exakt den Platzhalter-Cube belegt,
    /// ermittelt über lokale Mesh-Bounds statt Welt-Bounds.
    /// </summary>
    private static Vector3 CalcScale(GameObject inst, Vector3 targetSize)
    {
        MeshFilter[] mfs = inst.GetComponentsInChildren<MeshFilter>(true)
            .Where(mf => mf != null && mf.sharedMesh != null &&
                         !IsUnderGeneratedLightingRig(mf.transform, inst.transform))
            .ToArray();
        if (mfs.Length == 0)
            return Vector3.one;

        Bounds meshBounds = TransformBoundsToRoot(mfs[0], inst.transform);
        foreach (var mf in mfs.Skip(1))
            meshBounds.Encapsulate(TransformBoundsToRoot(mf, inst.transform));
        Vector3 meshSize = meshBounds.size;

        float sx = meshSize.x < EPS ? 1f : targetSize.x / meshSize.x;
        float sy = meshSize.y < EPS ? 1f : targetSize.y / meshSize.y;
        float sz = meshSize.z < EPS ? 1f : targetSize.z / meshSize.z;

        sx = Mathf.Clamp(sx, MIN_F, MAX_F);
        sy = Mathf.Clamp(sy, MIN_F, MAX_F);
        sz = Mathf.Clamp(sz, MIN_F, MAX_F);

        return new Vector3(sx, sy, sz);
    }

    private static bool IsUnderGeneratedLightingRig(Transform candidate, Transform instanceRoot)
    {
        Transform current = candidate;
        while (current != null)
        {
            if (current.name == CozyRoomLighting.FixtureRigName)
            {
                return true;
            }
            if (current == instanceRoot)
            {
                break;
            }
            current = current.parent;
        }
        return false;
    }

    private static Bounds TransformBoundsToRoot(MeshFilter meshFilter, Transform instanceRoot)
    {
        Bounds source = meshFilter.sharedMesh.bounds;
        Matrix4x4 toRoot = instanceRoot.worldToLocalMatrix * meshFilter.transform.localToWorldMatrix;
        Vector3 center = toRoot.MultiplyPoint3x4(source.center);
        Vector3 extents = source.extents;
        Vector3 axisX = toRoot.MultiplyVector(new Vector3(extents.x, 0f, 0f));
        Vector3 axisY = toRoot.MultiplyVector(new Vector3(0f, extents.y, 0f));
        Vector3 axisZ = toRoot.MultiplyVector(new Vector3(0f, 0f, extents.z));
        Vector3 transformedExtents = new Vector3(
            Mathf.Abs(axisX.x) + Mathf.Abs(axisY.x) + Mathf.Abs(axisZ.x),
            Mathf.Abs(axisX.y) + Mathf.Abs(axisY.y) + Mathf.Abs(axisZ.y),
            Mathf.Abs(axisX.z) + Mathf.Abs(axisY.z) + Mathf.Abs(axisZ.z));
        return new Bounds(center, transformedExtents * 2f);
    }

    /// <summary>
    /// Platziert das generierte Prefab an der Transform des DevDescription,
    /// skaliert es korrekt und blendet den Platzhalter aus.
    /// </summary>
    private static GameObject PlacePrefab(GameObject prefab, DevDescription dd,
                                          IReadOnlyDictionary<Transform, Transform> placedByPlaceholder,
                                          string jobId, string fingerprint,
                                          string contentSignature, string assetPath)
    {
        Transform ph = dd.transform;
        Transform targetParent = ResolveGeneratedParent(ph.parent, placedByPlaceholder);

        if (dd.HasGeneratedInstance(jobId, fingerprint))
        {
            GameObject exactInstance = dd.GeneratedInstance;
            ApplyPlacementTransform(exactInstance, ph, targetParent);
            ph.gameObject.SetActive(false);
            return exactInstance;
        }

        GameObject staleInstance = dd.GeneratedInstance;
        GameObject inst = null;

        // Wurde lediglich dieselbe deterministische Asset-Datei atomar ersetzt,
        // kann die bestehende Prefab-Instanz weiterverwendet und neu markiert werden.
        if (staleInstance != null &&
            string.Equals(NormalizeProjectPath(dd.GeneratedAssetPath),
                NormalizeProjectPath(assetPath), StringComparison.OrdinalIgnoreCase))
        {
            inst = staleInstance;
        }

        // Übernimmt einmalig Instanzen, die von der alten Pipeline bereits an
        // genau diesem Platz erzeugt, aber noch nicht am Platzhalter markiert wurden.
        inst ??= FindUntrackedExistingInstance(prefab, dd, assetPath);
        inst ??= (GameObject)PrefabUtility.InstantiatePrefab(prefab);
        if (inst == null)
        {
            Debug.LogWarning($"[GLB] Prefab konnte nicht instanziiert werden: {prefab?.name ?? "null"}");
            return null;
        }

        ApplyPlacementTransform(inst, ph, targetParent);
        ph.gameObject.SetActive(false);
        dd.SetGeneratedResult(jobId, fingerprint, contentSignature,
            NormalizeProjectPath(assetPath), inst);
        EditorUtility.SetDirty(dd);
        if (dd.gameObject.scene.IsValid())
        {
            EditorSceneManager.MarkSceneDirty(dd.gameObject.scene);
        }

        if (staleInstance != null && staleInstance != inst && staleInstance.scene.IsValid())
        {
            DestroyImmediate(staleInstance);
        }

        foreach (Renderer r in inst.GetComponentsInChildren<Renderer>(true)
                     .Where(renderer => renderer != null &&
                                        !IsUnderGeneratedLightingRig(renderer.transform,
                                            inst.transform)))
            foreach (var mat in r.sharedMaterials)
            {
                if (mat == null) continue;
                Color c = mat.color; c.a = 1f;
                mat.color = c;
                mat.EnableKeyword("_EMISSION");
                mat.SetColor("_EmissionColor", c * 0.15f);
            }

        CozyRoomLighting.ConfigureFixture(dd);
        return inst;
    }

    private static void ApplyPlacementTransform(GameObject instance, Transform placeholder,
                                                Transform targetParent)
    {
        // Die Skalierung wird in Weltkoordinaten aus den Mesh-Bounds abgeleitet.
        // Eine bereits unter einem skalierten generierten Parent liegende Instanz
        // muss deshalb zuerst gelöst werden; sonst würde dessen Skalierung bei
        // jedem Resume erneut auf das Child aufgeschlagen.
        instance.transform.SetParent(null, true);
        instance.transform.localScale = Vector3.one;
        instance.transform.rotation = Quaternion.identity;
        instance.transform.localScale = CalcScale(instance, placeholder.lossyScale);
        instance.transform.SetPositionAndRotation(placeholder.position, placeholder.rotation);
        instance.transform.SetParent(targetParent, true);
    }

    private static GameObject FindUntrackedExistingInstance(GameObject prefab, DevDescription target,
                                                             string assetPath)
    {
        if (prefab == null || target == null || string.IsNullOrWhiteSpace(assetPath)) return null;

        List<GameObject> matches = new();
        foreach (GameObject candidate in FindObjectsByType<GameObject>(
                     FindObjectsInactive.Include, FindObjectsSortMode.None))
        {
            if (candidate == null || candidate == target.gameObject || !candidate.scene.IsValid() ||
                candidate.scene != target.gameObject.scene) continue;

            // Ein importiertes GLB besteht typischerweise aus Root -> world ->
            // geometry_0. Root und Kinder koennen dieselbe Welt-Pose und denselben
            // Assetpfad besitzen. Nur der wirkliche Prefab-Instanz-Root darf als
            // vorhandenes Modell uebernommen werden; sonst entstehen mehrere
            // Scheintreffer oder ein Mesh-Child wird aus seinem GLB herausgerissen.
            GameObject instanceRoot = PrefabUtility.GetNearestPrefabInstanceRoot(candidate);
            if (instanceRoot == null || instanceRoot != candidate) continue;
            if ((candidate.transform.position - target.transform.position).sqrMagnitude > 0.000001f) continue;
            if (Quaternion.Angle(candidate.transform.rotation, target.transform.rotation) > 0.25f) continue;

            GameObject source = PrefabUtility.GetCorrespondingObjectFromSource(candidate);
            if (source != prefab) continue;
            string sourcePath = source == null ? "" : AssetDatabase.GetAssetPath(source);
            if (!string.Equals(NormalizeProjectPath(sourcePath), NormalizeProjectPath(assetPath),
                    StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }

            bool claimedElsewhere = FindObjectsByType<DevDescription>(
                    FindObjectsInactive.Include, FindObjectsSortMode.None)
                .Any(other => other != target && other.GeneratedInstance == candidate);
            if (!claimedElsewhere) matches.Add(candidate);
        }

        return matches.Count == 1 ? matches[0] : null;
    }

    private static Transform ResolveGeneratedParent(Transform originalParent,
                                                    IReadOnlyDictionary<Transform, Transform> placedByPlaceholder)
    {
        Transform current = originalParent;
        while (current != null)
        {
            if (placedByPlaceholder.TryGetValue(current, out Transform generatedParent) &&
                generatedParent != null)
            {
                return generatedParent;
            }

            current = current.parent;
        }

        current = originalParent;
        while (current != null)
        {
            if (current.gameObject.activeInHierarchy)
            {
                return current;
            }

            current = current.parent;
        }

        return null;
    }

    private string BuildModelJobId(ModelJob job)
    {
        string targetIdentity = job.Group.reuse
            ? "shared"
            : BuildStableTargetIdentity(job.CacheKey);
        string material = string.Join("|", new[]
        {
            CacheSchemaVersion,
            "model-job",
            ModelGeneratorVersion,
            ImagePromptVersion,
            ImageBackend ?? "",
            _apiModel?.Trim().ToLowerInvariant() ?? "",
            job.Group.description?.Trim() ?? "",
            FormatVector(job.Group.size),
            job.Group.reuse ? "reuse" : "unique",
            targetIdentity
        });
        return BuildDeterministicUuid(material);
    }

    private string BuildModelContentSignature(ModelJob job)
    {
        string material = string.Join("|", new[]
        {
            CacheSchemaVersion,
            "model-content",
            ModelGeneratorVersion,
            ImagePromptVersion,
            ImageBackend ?? "",
            _apiModel?.Trim().ToLowerInvariant() ?? "",
            job.Group.description?.Trim() ?? "",
            FormatVector(job.Group.size),
            job.Group.reuse ? "reuse" : "unique"
        });
        return BuildDeterministicUuid(material);
    }

    private static string BuildImageCacheId(Group group, DevDescription item)
    {
        string targetIdentity = group.reuse ? "shared" : BuildStableTargetIdentity(item);
        string material = string.Join("|", new[]
        {
            CacheSchemaVersion,
            "image-job",
            ImagePromptVersion,
            ImageBackend ?? "",
            BuildImagePrompt(group, item),
            group.reuse ? "reuse" : "unique",
            targetIdentity
        });
        return BuildDeterministicUuid(material);
    }

    private static string BuildModelFingerprint(string jobId, string imageHash)
    {
        return BuildDeterministicUuid(
            $"{CacheSchemaVersion}|model-output|{jobId}|{imageHash?.ToLowerInvariant() ?? ""}");
    }

    private static string BuildLegacyModelFingerprint(string jobId, string assetPath)
    {
        string absolutePath = ToAbsoluteProjectPath(assetPath);
        string fileHash = "missing";
        try
        {
            using FileStream stream = File.OpenRead(absolutePath);
            using SHA256 sha = SHA256.Create();
            fileHash = BytesToHex(sha.ComputeHash(stream));
        }
        catch (Exception)
        {
            // Der Loader validiert die Datei separat. Der Pfad hält die
            // Legacy-Zuordnung auch bei einem kurzfristigen Lesefehler stabil.
        }

        return BuildDeterministicUuid(
            $"{CacheSchemaVersion}|legacy-model|{jobId}|{NormalizeProjectPath(assetPath)}|{fileHash}");
    }

    private static string BuildDeterministicModelAssetPath(ModelJob job, string fingerprint)
    {
        string compactFingerprint = (fingerprint ?? "").Replace("-", "");
        return $"{TargetFolder}/{Sanitize(job.CacheKey.name)}_cache_{compactFingerprint}.glb";
    }

    private static string BuildImagePrompt(Group group, DevDescription item)
    {
        Vector3 size = item.transform.lossyScale;
        return string.Format(CultureInfo.InvariantCulture,
            "{0}. Dimensions {1:F2} x {2:F2} x {3:F2} meters. " +
            "Positioned at a slight angle to reveal multiple sides, centered and isolated on a plain white background, " +
            "soft even lighting, no shadows, no reflections, no additional objects, " +
            "suitable for product display and 3D modeling",
            group.description, size.x, size.z, size.y);
    }

    private static string BuildStableTargetIdentity(DevDescription item)
    {
        if (item == null || item.transform == null) return "missing-target";

        Stack<string> segments = new();
        Transform current = item.transform;
        while (current != null)
        {
            // Ein normaler SiblingIndex verschiebt sich, sobald ein generiertes
            // Prefab in die Hierarchie eingefuegt wird. Nur gleichnamige Geschwister
            // unterscheiden; fremde/generated Siblings beeinflussen die ID nicht.
            segments.Push($"{current.name}[{GetSameNameSiblingOrdinal(current)}]");
            current = current.parent;
        }

        // Der Szenenpfad ist absichtlich kein Teil der Identitaet. Ein Speichern
        // oder Umbenennen der aktuell geladenen Szene darf keinen Cache invalidieren.
        return $"target-path-v2/{string.Join("/", segments)}";
    }

    private static int GetSameNameSiblingOrdinal(Transform target)
    {
        if (target == null) return 0;

        int ordinal = 0;
        Transform parent = target.parent;
        if (parent != null)
        {
            for (int index = 0; index < parent.childCount; index++)
            {
                Transform sibling = parent.GetChild(index);
                if (sibling == target) break;
                if (string.Equals(sibling.name, target.name, StringComparison.Ordinal) &&
                    sibling.GetComponent<DevDescription>() != null)
                {
                    ordinal++;
                }
            }
            return ordinal;
        }

        if (!target.gameObject.scene.IsValid()) return 0;
        foreach (GameObject root in target.gameObject.scene.GetRootGameObjects())
        {
            if (root.transform == target) break;
            if (string.Equals(root.name, target.name, StringComparison.Ordinal) &&
                root.GetComponent<DevDescription>() != null)
            {
                ordinal++;
            }
        }
        return ordinal;
    }

    private static string FormatVector(Vector3 value)
    {
        Vector3 rounded = Round2(value);
        return string.Format(CultureInfo.InvariantCulture,
            "{0:F2},{1:F2},{2:F2}", rounded.x, rounded.y, rounded.z);
    }

    private static string BuildDeterministicUuid(string material)
    {
        byte[] bytes;
        using (SHA256 sha = SHA256.Create())
        {
            bytes = sha.ComputeHash(Encoding.UTF8.GetBytes(material ?? ""));
        }

        // RFC 4122 variant + Version 5-Kennung. Die Hashfunktion bleibt SHA-256;
        // formatiert wird explizit in Network-Byte-Order, nicht über Guid(byte[]).
        bytes[6] = (byte)((bytes[6] & 0x0f) | 0x50);
        bytes[8] = (byte)((bytes[8] & 0x3f) | 0x80);
        string hex = BytesToHex(bytes.Take(16).ToArray());
        return $"{hex.Substring(0, 8)}-{hex.Substring(8, 4)}-{hex.Substring(12, 4)}-" +
               $"{hex.Substring(16, 4)}-{hex.Substring(20, 12)}";
    }

    private static string ComputeSha256Hex(byte[] data)
    {
        using SHA256 sha = SHA256.Create();
        return BytesToHex(sha.ComputeHash(data ?? Array.Empty<byte>()));
    }

    private static string BytesToHex(byte[] bytes)
    {
        StringBuilder builder = new(bytes.Length * 2);
        foreach (byte value in bytes) builder.Append(value.ToString("x2", CultureInfo.InvariantCulture));
        return builder.ToString();
    }

    private bool TryLoadCachedImage(Group group, DevDescription item, out ImageInfo info)
    {
        object key = group.reuse ? (object)group : item;
        if (_img.TryGetValue(key, out info) && info?.data != null && info.data.Length > 0)
        {
            return true;
        }

        string imageCacheId = BuildImageCacheId(group, item);
        ImageCacheRecord record = FindImageCacheRecord(imageCacheId);
        if (record != null && TryReadPersistentImage(record, imageCacheId, out info))
        {
            _img[key] = info;
            return true;
        }

        if (TryRecoverDeterministicImageCache(imageCacheId, out info))
        {
            _img[key] = info;
            return true;
        }

        if (TryImportLegacySavedImage(group, item, imageCacheId, out info))
        {
            _img[key] = info;
            return true;
        }

        info = null;
        return false;
    }

    private bool TryRecoverDeterministicImageCache(string imageCacheId, out ImageInfo info)
    {
        info = null;
        string relativePath = $"{ImageCacheFolder}/{imageCacheId}.png";
        if (!TryResolveCachePath(relativePath, out string absolutePath) ||
            !File.Exists(absolutePath))
        {
            return false;
        }

        try
        {
            byte[] data = File.ReadAllBytes(absolutePath);
            if (!TryCreateTexture(data, out Texture2D texture)) return false;

            string hash = ComputeSha256Hex(data);
            // Ohne Manifest lässt sich nicht beweisen, dass ein manuell erzeugtes
            // Bild bereits freigegeben war. Es bleibt erhalten, wird aber sicher
            // als ungeprüft wiederhergestellt.
            RegisterImageCacheRecord(imageCacheId, relativePath, hash, approved:false);
            info = new ImageInfo
            {
                data = data,
                preview = texture,
                approved = false,
                denoise = 0.8f,
                cacheId = imageCacheId,
                contentHash = hash
            };
            Debug.Log($"[IMG] Deterministischen PNG-Cache ohne Manifest wiederhergestellt: {relativePath}");
            return true;
        }
        catch (Exception ex)
        {
            Debug.LogWarning($"[IMG] Deterministischer Cache unlesbar ({relativePath}): {ex.Message}");
            return false;
        }
    }

    private bool TryReadPersistentImage(ImageCacheRecord record, string expectedId,
                                        out ImageInfo info)
    {
        info = null;
        if (record == null || !string.Equals(record.id, expectedId, StringComparison.Ordinal) ||
            !TryResolveCachePath(record.filePath, out string absolutePath) ||
            !File.Exists(absolutePath))
        {
            return false;
        }

        try
        {
            byte[] data = File.ReadAllBytes(absolutePath);
            string hash = ComputeSha256Hex(data);
            if (!string.Equals(hash, record.sha256, StringComparison.OrdinalIgnoreCase))
            {
                Debug.LogWarning($"[IMG] Cache-Hash stimmt nicht: {record.filePath}");
                return false;
            }

            if (!TryCreateTexture(data, out Texture2D texture)) return false;
            info = new ImageInfo
            {
                data = data,
                preview = texture,
                approved = record.approved,
                denoise = 0.8f,
                cacheId = expectedId,
                contentHash = hash
            };
            return true;
        }
        catch (Exception ex)
        {
            Debug.LogWarning($"[IMG] Cache konnte nicht gelesen werden ({record.filePath}): {ex.Message}");
            return false;
        }
    }

    private bool TryImportLegacySavedImage(Group group, DevDescription item, string imageCacheId,
                                           out ImageInfo info)
    {
        info = null;
        string absoluteLegacyFolder = ToAbsoluteProjectPath(LegacySavedImagesFolder);
        if (!Directory.Exists(absoluteLegacyFolder)) return false;

        string snippet = BuildLegacyPromptSnippet(BuildImagePrompt(group, item));
        if (string.IsNullOrWhiteSpace(snippet) ||
            !IsLegacyImageSnippetUnique(group, item, snippet, imageCacheId))
        {
            return false;
        }

        string shortJobId = imageCacheId.Substring(0, 8);
        List<FileInfo> candidates = Directory.GetFiles(absoluteLegacyFolder, "*.png")
            .Select(path => new FileInfo(path))
            .Where(file => LegacyImageFilenameMatches(file.Name, snippet))
            .OrderByDescending(file =>
                Path.GetFileNameWithoutExtension(file.Name)
                    .EndsWith("_" + shortJobId, StringComparison.OrdinalIgnoreCase))
            .ThenByDescending(file => file.LastWriteTimeUtc)
            .ToList();

        foreach (FileInfo candidate in candidates)
        {
            try
            {
                byte[] data = File.ReadAllBytes(candidate.FullName);
                if (!TryCreateTexture(data, out Texture2D texture)) continue;

                string hash = ComputeSha256Hex(data);
                PersistImageCache(imageCacheId, data, hash, approved:true);
                info = new ImageInfo
                {
                    data = data,
                    preview = texture,
                    approved = true,
                    denoise = 0.8f,
                    cacheId = imageCacheId,
                    contentHash = hash
                };
                Debug.Log($"[IMG] Legacy-PNG übernommen: {candidate.Name} -> {imageCacheId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[IMG] Legacy-PNG unlesbar ({candidate.Name}): {ex.Message}");
            }
        }

        return false;
    }

    private bool IsLegacyImageSnippetUnique(Group requestedGroup, DevDescription requestedItem,
                                            string snippet, string requestedImageCacheId)
    {
        HashSet<string> matchingIds = new(StringComparer.Ordinal);
        foreach (Group group in _groups.Where(candidate => candidate.generate))
        {
            IEnumerable<DevDescription> items = group.reuse
                ? group.items.Take(1)
                : group.items;
            foreach (DevDescription item in items)
            {
                if (!string.Equals(BuildLegacyPromptSnippet(BuildImagePrompt(group, item)), snippet,
                        StringComparison.Ordinal))
                {
                    continue;
                }

                matchingIds.Add(BuildImageCacheId(group, item));
            }
        }

        if (matchingIds.Count == 1 && matchingIds.Contains(requestedImageCacheId)) return true;

        Debug.LogWarning($"[IMG] Legacy-PNG-Präfix '{snippet}' ist nicht eindeutig; kein Auto-Import.");
        return false;
    }

    private static string BuildLegacyPromptSnippet(string prompt)
    {
        StringBuilder builder = new();
        bool separator = false;
        foreach (char character in prompt ?? "")
        {
            bool asciiAlphaNumeric = character >= 'A' && character <= 'Z' ||
                                      character >= 'a' && character <= 'z' ||
                                      character >= '0' && character <= '9';
            if (asciiAlphaNumeric)
            {
                builder.Append(character);
                separator = false;
            }
            else if (!separator)
            {
                builder.Append('_');
                separator = true;
            }

            if (builder.Length >= 30) break;
        }

        return builder.ToString(0, Math.Min(30, builder.Length));
    }

    private static bool LegacyImageFilenameMatches(string fileName, string snippet)
    {
        string stem = Path.GetFileNameWithoutExtension(fileName);
        if (stem.Length < 16 + snippet.Length || stem[8] != '_' || stem[15] != '_') return false;
        for (int index = 0; index < 8; index++) if (!char.IsDigit(stem[index])) return false;
        for (int index = 9; index < 15; index++) if (!char.IsDigit(stem[index])) return false;

        string tail = stem.Substring(16);
        return string.Equals(tail, snippet, StringComparison.Ordinal) ||
               tail.StartsWith(snippet + "_", StringComparison.Ordinal);
    }

    private static bool IsAcceptedLegacyModelFileName(string fileName, string sanitizedObjectName)
    {
        string stem = Path.GetFileNameWithoutExtension(fileName);
        string prefix = sanitizedObjectName + "_";
        if (!stem.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)) return false;

        string suffix = stem.Substring(prefix.Length);
        bool guidSuffix = suffix.Length == 32 && suffix.All(character =>
            character >= '0' && character <= '9' ||
            character >= 'a' && character <= 'f' ||
            character >= 'A' && character <= 'F');
        bool recoveredSuffix = string.Equals(
            suffix, "recovered_after_timeout", StringComparison.OrdinalIgnoreCase);
        return guidSuffix || recoveredSuffix;
    }

    private static bool TryCreateTexture(byte[] data, out Texture2D texture)
    {
        texture = new Texture2D(2, 2);
        if (data != null && data.Length > 0 && texture.LoadImage(data)) return true;
        DestroyImmediate(texture);
        texture = null;
        return false;
    }

    private void PersistImageCache(string imageCacheId, byte[] data, string hash, bool approved)
    {
        string relativePath = $"{ImageCacheFolder}/{imageCacheId}.png";
        AtomicWriteBytes(ToAbsoluteProjectPath(relativePath), data);

        RegisterImageCacheRecord(imageCacheId, relativePath, hash, approved);
    }

    private void PersistImageApproval(ImageInfo info)
    {
        if (info == null || string.IsNullOrWhiteSpace(info.cacheId)) return;

        string relativePath = $"{ImageCacheFolder}/{info.cacheId}.png";
        if (!File.Exists(ToAbsoluteProjectPath(relativePath)) && info.data != null)
        {
            AtomicWriteBytes(ToAbsoluteProjectPath(relativePath), info.data);
        }

        RegisterImageCacheRecord(info.cacheId, relativePath, info.contentHash, info.approved);
    }

    private void RegisterImageCacheRecord(string imageCacheId, string relativePath, string hash,
                                          bool approved)
    {
        CacheManifest manifest = GetCacheManifest();
        ImageCacheRecord record = manifest.images.FirstOrDefault(entry =>
            string.Equals(entry.id, imageCacheId, StringComparison.Ordinal));
        bool changed = false;
        if (record == null)
        {
            record = new ImageCacheRecord { id = imageCacheId };
            manifest.images.Add(record);
            changed = true;
        }

        if (!string.Equals(record.filePath, relativePath, StringComparison.Ordinal))
        {
            record.filePath = relativePath;
            changed = true;
        }

        if (!string.Equals(record.sha256, hash, StringComparison.OrdinalIgnoreCase))
        {
            record.sha256 = hash;
            changed = true;
        }

        if (record.approved != approved)
        {
            record.approved = approved;
            changed = true;
        }

        if (changed) SaveCacheManifest();
    }

    private void TryMigrateImageCacheForMarkedModel(ModelJob job, string newImageCacheId,
                                                     string contentSignature)
    {
        CacheManifest manifest = GetCacheManifest();
        foreach (DevDescription target in job.Targets)
        {
            if (target == null || string.IsNullOrWhiteSpace(target.GeneratedJobId) ||
                (!string.IsNullOrWhiteSpace(target.GeneratedContentSignature) &&
                 !string.Equals(target.GeneratedContentSignature, contentSignature,
                     StringComparison.Ordinal)))
            {
                continue;
            }

            ModelCacheRecord oldModel = manifest.models.FirstOrDefault(record =>
                string.Equals(record.jobId, target.GeneratedJobId, StringComparison.Ordinal));
            if (oldModel == null || string.IsNullOrWhiteSpace(oldModel.imageSha256)) continue;

            ImageCacheRecord oldImage = manifest.images.FirstOrDefault(record =>
                string.Equals(record.sha256, oldModel.imageSha256,
                    StringComparison.OrdinalIgnoreCase) &&
                !string.IsNullOrWhiteSpace(record.filePath) &&
                File.Exists(ToAbsoluteProjectPath(record.filePath)));
            if (oldImage == null) continue;

            RegisterImageCacheRecord(newImageCacheId, oldImage.filePath, oldImage.sha256,
                oldImage.approved);
            return;
        }
    }

    private void AdoptMarkedSceneModel(ModelJob job, string jobId, string fingerprint,
                                       string contentSignature, string assetPath)
    {
        string normalizedAssetPath = NormalizeProjectPath(assetPath);
        foreach (DevDescription target in job.Targets)
        {
            if (target == null || target.GeneratedInstance == null ||
                !string.Equals(NormalizeProjectPath(target.GeneratedAssetPath),
                    normalizedAssetPath, StringComparison.OrdinalIgnoreCase) ||
                (!string.IsNullOrWhiteSpace(target.GeneratedContentSignature) &&
                 !string.Equals(target.GeneratedContentSignature, contentSignature,
                     StringComparison.Ordinal)))
            {
                continue;
            }

            target.SetGeneratedResult(jobId, fingerprint, contentSignature,
                normalizedAssetPath, target.GeneratedInstance);
            EditorUtility.SetDirty(target);
            if (target.gameObject.scene.IsValid())
            {
                EditorSceneManager.MarkSceneDirty(target.gameObject.scene);
            }
        }
    }

    private void RemoveSupersededModelCacheRecord(string oldJobId, string assetPath)
    {
        if (string.IsNullOrWhiteSpace(oldJobId)) return;

        string normalizedAssetPath = NormalizeProjectPath(assetPath);
        CacheManifest manifest = GetCacheManifest();
        int removed = manifest.models.RemoveAll(record =>
            string.Equals(record.jobId, oldJobId, StringComparison.Ordinal) &&
            string.Equals(NormalizeProjectPath(record.assetPath), normalizedAssetPath,
                StringComparison.OrdinalIgnoreCase));
        if (removed > 0) SaveCacheManifest();
    }

    private CacheManifest GetCacheManifest()
    {
        if (_cacheManifest != null) return _cacheManifest;

        string absolutePath = ToAbsoluteProjectPath(CacheManifestPath);
        try
        {
            if (File.Exists(absolutePath))
            {
                _cacheManifest = JsonUtility.FromJson<CacheManifest>(File.ReadAllText(absolutePath));
            }
        }
        catch (Exception ex)
        {
            Debug.LogWarning($"[CACHE] Manifest konnte nicht gelesen werden: {ex.Message}");
        }

        _cacheManifest ??= new CacheManifest();
        _cacheManifest.images ??= new List<ImageCacheRecord>();
        _cacheManifest.models ??= new List<ModelCacheRecord>();
        return _cacheManifest;
    }

    private ImageCacheRecord FindImageCacheRecord(string imageCacheId)
    {
        return GetCacheManifest().images.FirstOrDefault(record =>
            string.Equals(record.id, imageCacheId, StringComparison.Ordinal));
    }

    private ModelCacheRecord FindModelCacheRecord(string jobId)
    {
        return GetCacheManifest().models.FirstOrDefault(record =>
            string.Equals(record.jobId, jobId, StringComparison.Ordinal));
    }

    private void RegisterModelCache(string jobId, string fingerprint, string assetPath,
                                    string imageHash, string contentSignature)
    {
        CacheManifest manifest = GetCacheManifest();
        ModelCacheRecord record = manifest.models.FirstOrDefault(entry =>
            string.Equals(entry.jobId, jobId, StringComparison.Ordinal));
        bool changed = false;
        if (record == null)
        {
            record = new ModelCacheRecord { jobId = jobId };
            manifest.models.Add(record);
            changed = true;
        }

        string normalizedAssetPath = NormalizeProjectPath(assetPath);
        string normalizedImageHash = imageHash ?? "";
        if (!string.Equals(record.fingerprint, fingerprint, StringComparison.Ordinal))
        {
            record.fingerprint = fingerprint;
            changed = true;
        }

        if (!string.Equals(record.contentSignature, contentSignature, StringComparison.Ordinal))
        {
            record.contentSignature = contentSignature ?? "";
            changed = true;
        }

        if (!string.Equals(record.assetPath, normalizedAssetPath, StringComparison.OrdinalIgnoreCase))
        {
            record.assetPath = normalizedAssetPath;
            changed = true;
        }

        if (!string.Equals(record.imageSha256, normalizedImageHash,
                StringComparison.OrdinalIgnoreCase))
        {
            record.imageSha256 = normalizedImageHash;
            changed = true;
        }

        if (changed) SaveCacheManifest();
    }

    private void SaveCacheManifest()
    {
        string json = JsonUtility.ToJson(GetCacheManifest(), prettyPrint:true);
        AtomicWriteBytes(ToAbsoluteProjectPath(CacheManifestPath), Encoding.UTF8.GetBytes(json));
    }

    private static void AtomicWriteBytes(string absolutePath, byte[] data)
    {
        string folder = Path.GetDirectoryName(absolutePath);
        if (!string.IsNullOrWhiteSpace(folder)) Directory.CreateDirectory(folder);

        string temporaryPath = absolutePath + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try
        {
            File.WriteAllBytes(temporaryPath, data ?? Array.Empty<byte>());
            if (File.Exists(absolutePath))
            {
                try
                {
                    File.Replace(temporaryPath, absolutePath, null);
                }
                catch (PlatformNotSupportedException)
                {
                    File.Delete(absolutePath);
                    File.Move(temporaryPath, absolutePath);
                }
            }
            else
            {
                File.Move(temporaryPath, absolutePath);
            }
        }
        finally
        {
            if (File.Exists(temporaryPath)) File.Delete(temporaryPath);
        }
    }

    private static bool TryLoadModelAsset(string assetPath, out GameObject prefab)
    {
        prefab = null;
        string normalized = NormalizeProjectPath(assetPath);
        if (string.IsNullOrWhiteSpace(normalized) || Path.IsPathRooted(normalized) ||
            !normalized.StartsWith(TargetFolder + "/", StringComparison.OrdinalIgnoreCase) ||
            !normalized.EndsWith(".glb", StringComparison.OrdinalIgnoreCase))
        {
            return false;
        }

        string absolutePath = ToAbsoluteProjectPath(normalized);
        if (!IsValidGlbFile(absolutePath)) return false;

        AssetDatabase.ImportAsset(normalized, ImportAssetOptions.ForceSynchronousImport);
        prefab = AssetDatabase.LoadAssetAtPath<GameObject>(normalized);
        return prefab != null;
    }

    private static bool IsValidGlbFile(string absolutePath)
    {
        try
        {
            using FileStream stream = File.OpenRead(absolutePath);
            if (stream.Length < 12 || stream.Length > uint.MaxValue) return false;
            byte[] header = new byte[12];
            if (stream.Read(header, 0, header.Length) != header.Length) return false;
            return IsValidGlbHeader(header, (uint)stream.Length);
        }
        catch (Exception)
        {
            return false;
        }
    }

    private static bool IsValidGlbBytes(byte[] data)
    {
        return data != null && data.Length >= 12 && data.LongLength <= uint.MaxValue &&
               IsValidGlbHeader(data, (uint)data.Length);
    }

    private static bool IsValidGlbHeader(byte[] data, uint actualLength)
    {
        if (data[0] != (byte)'g' || data[1] != (byte)'l' ||
            data[2] != (byte)'T' || data[3] != (byte)'F')
        {
            return false;
        }

        uint version = ReadUInt32LittleEndian(data, 4);
        uint declaredLength = ReadUInt32LittleEndian(data, 8);
        return version == 2 && declaredLength == actualLength;
    }

    private static uint ReadUInt32LittleEndian(byte[] data, int offset)
    {
        return (uint)(data[offset] |
                      data[offset + 1] << 8 |
                      data[offset + 2] << 16 |
                      data[offset + 3] << 24);
    }

    private static bool TryResolveCachePath(string relativePath, out string absolutePath)
    {
        absolutePath = "";
        string normalized = NormalizeProjectPath(relativePath);
        if (string.IsNullOrWhiteSpace(normalized) || Path.IsPathRooted(normalized) ||
            !normalized.StartsWith(CacheRoot + "/", StringComparison.OrdinalIgnoreCase))
        {
            return false;
        }

        string candidate = ToAbsoluteProjectPath(normalized);
        string cacheRoot = ToAbsoluteProjectPath(CacheRoot)
            .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) +
            Path.DirectorySeparatorChar;
        if (!candidate.StartsWith(cacheRoot, StringComparison.OrdinalIgnoreCase)) return false;
        absolutePath = candidate;
        return true;
    }

    private static string ToAbsoluteProjectPath(string relativePath)
    {
        string platformPath = (relativePath ?? "")
            .Replace('/', Path.DirectorySeparatorChar)
            .Replace('\\', Path.DirectorySeparatorChar);
        DirectoryInfo projectRoot = Directory.GetParent(Application.dataPath);
        string basePath = projectRoot?.FullName ?? Environment.CurrentDirectory;
        return Path.GetFullPath(Path.Combine(basePath, platformPath));
    }

    private static string NormalizeProjectPath(string path)
    {
        return (path ?? "").Replace('\\', '/').Trim();
    }

    private void Progress(string n) { _done++; _current = n; Repaint(); }

    private static Vector3 Round2(Vector3 v) => new(Mathf.Round(v.x * 100) / 100,
                                                    Mathf.Round(v.y * 100) / 100,
                                                    Mathf.Round(v.z * 100) / 100);

    private static string Sanitize(string n)
    {
        foreach (char c in Path.GetInvalidFileNameChars()) n = n.Replace(c, '_');
        return n;
    }
}
#endif
