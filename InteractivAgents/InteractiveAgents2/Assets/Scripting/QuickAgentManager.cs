using System;
using System.Collections;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.RegularExpressions;
using System.IO;
using FunctionalMlds.V2;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif
using UnityEngine.Networking;

public class QuickAgentManager : MonoBehaviour
{
#if UNITY_WEBGL && !UNITY_EDITOR
    [DllImport("__Internal")]
    private static extern int IAVoice_IsSupported();

    [DllImport("__Internal")]
    private static extern void IAVoice_StartRecording(
        string gameObjectName,
        string successMethodName,
        string errorMethodName,
        string backendBaseUrl,
        string sttModel,
        string sttLanguage,
        float maxSeconds);

    [DllImport("__Internal")]
    private static extern void IAVoice_StopRecording();
#endif

    [Header("Backend")]
    public string backendBaseUrl = "http://127.0.0.1:8787";
    public string roomPlanPath = "examples/room_plan.example.json";
    public string agentsPath = "examples/agents.example.json";
    [Tooltip("shared_history = gemeinsames Chatgedaechtnis; agent_private_history = privates Agentengedaechtnis mit Handoff-Brief.")]
    public string memoryMode = "shared_history";

    [Header("Spawn")]
    public Vector3 spawnArea = new Vector3(12f, 0f, 12f);
    public float spawnHeight = 0.5f;
    public Vector2 boxScaleRange = new Vector2(0.8f, 1.2f);

    [Header("UI")]
    public bool showUi = true;
    public Rect uiRect = new Rect(10, 10, 420, 520);

    [Header("Agent Visuals")]
    public Color activeAgentColor = new Color(1f, 0.85f, 0.2f);
    public float activeAgentEmission = 0.6f;
    public bool showAgentBubbles = true;
    public float bubbleHeight = 1.7f;
    public float bubbleDuration = 15f;
    public float bubbleStagger = 5f;
    public float handoffDelay = 5f;
    public float handoffIndicatorDuration = 5f;
    public float handoffLineWidth = 0.06f;
    public Color handoffRouteColor = new Color(1f, 0.84f, 0.08f, 0.95f);
    public float handoffRouteGroundOffset = 0.035f;
    public float handoffRouteDashLength = 0.42f;
    public float handoffRouteGapLength = 0.24f;
    public float handoffRouteDashSpeed = 0.9f;
    public float handoffRouteObstaclePadding = 0.7f;
    public float handoffRouteGridSize = 0.35f;
    public float handoffRouteSearchMargin = 5f;
    public float handoffRouteCornerRadius = 0.35f;
    public float handoffRouteRepathDistance = 1.35f;

    [Header("Animation")]
    public string animationResourceFolder = "Characters";

    [Header("TTS")]
    public bool enableTts = true;
    public float ttsCooldownSeconds = 0.5f;

    [Header("Voice Input")]
    public bool enableVoiceInput = true;
    public KeyCode voiceRecordKey = KeyCode.V;
    public float voiceMaxRecordSeconds = 10f;
    public int voiceSampleRate = 16000;
    public string sttModel = "whisper-1";
    public string sttLanguage = "de";
    public bool sendVoiceTranscriptAutomatically = true;

    [Header("Camera Movement")]
    public bool enableFreeMovement = true;
    public float cameraMoveSpeed = 4f;
    public float cameraBoostMultiplier = 2f;
    public float cameraLookSpeed = 2f;
    public float cameraLookClamp = 80f;

    [Header("XR/WebXR")]
    public bool moveXrOriginInsteadOfCamera = true;
    public bool ensureFallbackGroundCollider = true;
    public bool ensureSceneObjectColliders = true;
    public Vector2 fallbackGroundSize = new Vector2(40f, 40f);
    public float fallbackGroundY = 0f;
    public float fallbackGroundThickness = 0.08f;

    [Header("FPV-Modus")]
    public KeyCode fpvToggleKey = KeyCode.F1;
    public float fpvEyeHeight = 1.7f;
    public float fpvCollisionRadius = 0.28f;
    public float fpvCollisionHeight = 1.65f;
    public float fpvCollisionSkin = 0.04f;
    public LayerMask fpvCollisionMask = ~0;
    [Range(0.2f, 6f)]
    public float fpvMouseSensitivity = 2f;

    [Header("FPV-Interaktion")]
    public float fpvInteractionRadius = 3f;
    public KeyCode fpvChatKey = KeyCode.T;
    public bool fpvProximityHandoff = true;

    [Header("Spatial Grounding")]
    public bool enableSpatialTargetSelection = true;
    public LayerMask spatialSelectionMask = ~0;
    public float spatialSelectionMaxDistance = 100f;
    [Min(0f)]
    public float spatialAmbiguityDistanceTolerance = 0.025f;
    public Color selectedSpatialTargetColor = new Color(0.15f, 0.9f, 1f, 1f);
    public float selectedSpatialTargetEmission = 1.1f;

    [Header("FPV-Richtungspfeil")]
    public float fpvDirectionArrowRadius = 130f;
    public float fpvDirectionArrowSize = 58f;
    public Color fpvDirectionArrowTint = new Color(1f, 0.84f, 0.08f);

    [Serializable]
    public class Vector3Data { public float x; public float y; public float z; }

    [Serializable]
    public class SetupRequestPaths
    {
        public string room_plan_path;
        public string agents_path;
        public string session_id;
        public string project_id;
        public string memory_mode;
    }

    [Serializable]
    public class ProjectSummary
    {
        public string id;
        public string display_name;
        public string description;
    }

    [Serializable]
    public class ProjectListResponse
    {
        public ProjectSummary[] projects;
    }

    [Serializable]
    public class AgentPlacement
    {
        public string id;
        public string display_name;
        public string voice;
        public string voice_style;
        public string tts_model;
        public Vector3Data position;
        public Vector3Data forward;
        public string spawn_point_id;
        public string zone_id;
        public string[] tags;
        public string voice_gender;
        public string functionalmlds_agent_id;
        public string functionalmlds_entity_id;
        public string[] provided_capability_ids;
        public string[] plays_actor_ids;
        public string[] responsible_zone_ids;
        public string[] grounded_asset_ids;
        public string[] grounded_object_group_ids;
    }

    [Serializable]
    public class SetupResponse
    {
        public string session_id;
        public string memory_mode;
        public AgentPlacement[] agents;
        public string metamodel_version;
        public string trace_schema_version;
        public string model_sha256;
        public string functionalmlds_profile;
        public string functionalmlds_model_endpoint;
        public string runtime_validation_target_id;
    }

    [Serializable]
    public class ChatRequest
    {
        public string session_id;
        public string active_agent_id;
        public string user_text;
        public string interaction_mode;
        public SpatialContext spatial_context;
    }

    /// <summary>
    /// JsonUtility materializes null nested serializable classes as empty objects in some
    /// Unity versions. Use this serializer for /chat so a legacy request really omits the
    /// optional spatial_context field.
    /// </summary>
    public static string SerializeChatRequest(ChatRequest request)
    {
        if (request == null)
            throw new ArgumentNullException(nameof(request));
        if (string.Equals(
                request.interaction_mode,
                FunctionalMldsV2InteractionEvidenceEvaluator.DeicticMode,
                StringComparison.Ordinal)
            && request.spatial_context == null)
        {
            throw new ArgumentException(
                "A deictic chat request requires spatial_context.",
                nameof(request));
        }
        return JsonConvert.SerializeObject(
            request,
            Formatting.None,
            new JsonSerializerSettings
            {
                NullValueHandling = NullValueHandling.Ignore
            });
    }

    /// <summary>
    /// Selects the explicit V2 interaction contract from runtime state only. User text is never
    /// inspected. Ambiguous or internally inconsistent selection state fails closed.
    /// </summary>
    public static string ResolveV2InteractionMode(
        bool isV2,
        string selectionState,
        SpatialContext spatialContext)
    {
        if (!isV2)
            return null;
        if (string.Equals(
                selectionState,
                FunctionalMldsSpatialTargetStates.Ambiguous,
                StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                "An ambiguous spatial selection cannot fall back to non_deictic mode.");
        }
        if (spatialContext != null)
        {
            if (!string.Equals(
                    selectionState,
                    FunctionalMldsSpatialTargetStates.Resolved,
                    StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    "A spatial_context requires resolved selection state.");
            }
            return FunctionalMldsV2InteractionEvidenceEvaluator.DeicticMode;
        }
        if (string.Equals(
                selectionState,
                FunctionalMldsSpatialTargetStates.Resolved,
                StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                "Resolved V2 selection state requires spatial_context.");
        }
        return FunctionalMldsV2InteractionEvidenceEvaluator.NonDeicticMode;
    }

    /// <summary>
    /// Optional request extension. A null value preserves the legacy /chat contract.
    /// The backend validates IDs and derives trusted group/zone membership from model_sha256.
    /// </summary>
    [Serializable]
    public class SpatialContext
    {
        public string model_sha256;
        public string state;
        public string entity_id;
        public string source_object_id;
        public string object_group_id;
        public string zone_id;
        public string display_name;
        public string[] synonyms;
        public Vector3Data hit_position;
        public float distance_m;
        public string selection_modality;
        public string ambiguity_reason;
        public string[] candidate_entity_ids;
    }

    [Serializable]
    public class SpatialSelectionEvent
    {
        public string event_type;
        public string state;
        public string entity_id;
        public string source_object_id;
        public string selection_modality;
        public string reason;
        public string[] candidate_entity_ids;
        public float time_since_start_s;
    }

    [Serializable]
    public class ChatEvent
    {
        public string type;
        public string agent_id;
        public string text;
    }

    [Serializable]
    public class Handoff
    {
        public string from;
        public string to;
        public string reason;
        public string brief;
    }

    [Serializable]
    public class GroundingEvidenceItem
    {
        public string relation;
        public string subject_id;
        public string object_id;
        public string source_object_id;
        public string source;
    }

    [Serializable]
    public class GroundingInfo
    {
        public string status;
        public string model_sha256;
        public string selected_entity_id;
        public string selected_source_object_id;
        public string selected_name;
        public string[] object_group_ids;
        public string[] zone_ids;
        public string[] grounded_entity_ids;
        public Vector3Data hit_position;
        public float distance_m;
        public string selection_modality;
        public GroundingEvidenceItem[] evidence;
    }

    [Serializable]
    public class RoutingInfo
    {
        public string requested_agent_id;
        public string selected_agent_id;
        public string priority;
        public string[] candidate_agent_ids;
        public bool? modeled_handoff;
        public string reason;
    }

    [Serializable]
    public class ModelBindingInfo
    {
        public string runtime_binding_id;
        public string runtime_action_id;
        public string capability_id;
        public string capability_use_id;
    }

    [Serializable]
    public class ChatResponse
    {
        public string session_id;
        public string active_agent_id;
        public string memory_mode;
        public string interaction_mode;
        public ModelBindingInfo model_binding;
        public Handoff handoff;
        public ChatEvent[] events;
        public string[] grounded_entity_ids;
        public GroundingEvidenceItem[] grounding_evidence;
        public string routing_reason;
        public GroundingInfo grounding;
        public RoutingInfo routing;
    }

    [Serializable]
    public class TtsRequest
    {
        public string text;
        public string voice;
        public string voice_style;
        public string tts_model;
    }

    [Serializable]
    public class SttResponse
    {
        public string text;
        public string model;
        public string language;
    }

    [Header("Runtime")]
    public string sessionId;
    public string activeAgentId;

    public string SpatialSelectionState => spatialSelectionState;
    public string SelectedSpatialEntityId =>
        selectedSpatialTarget == null ? string.Empty : selectedSpatialTarget.EntityId;
    public string SelectedSpatialSourceObjectId =>
        selectedSpatialTarget == null ? string.Empty : selectedSpatialTarget.SourceObjectId;
    public string CurrentModelSha256 => currentModelSha256;
    public string InteractionEvidenceStatus => interactionEvidenceStatus;
    public FunctionalMldsSceneObjectBindingRegistry SpatialBindingRegistry => spatialBindingRegistry;
    public event Action<SpatialSelectionEvent> SpatialEventLogged;
    public event Action<FunctionalMldsV2InteractionAssessment> InteractionEvidenceLogged;

    private class AgentVisual
    {
        public GameObject obj;
        public Renderer renderer;
        public Color baseColor;
        public float scale;
        public AudioSource audioSource;
        public PlayableGraph animGraph;
    }

    private class BubbleInfo
    {
        public string text;
        public float expiresAt;
    }

    private class AgentVoiceSettings
    {
        public string voice;
        public string voiceStyle;
        public string ttsModel;
    }

    private struct HandoffRouteObstacle
    {
        public Rect rect;

        public HandoffRouteObstacle(Rect rect)
        {
            this.rect = rect;
        }
    }

    private readonly Dictionary<string, AgentVisual> agentObjects = new Dictionary<string, AgentVisual>();
    private readonly Dictionary<string, BubbleInfo> agentBubbles = new Dictionary<string, BubbleInfo>();
    private readonly Dictionary<string, AgentVoiceSettings> agentVoices = new Dictionary<string, AgentVoiceSettings>();
    private readonly Dictionary<string, AudioClip> ttsCache = new Dictionary<string, AudioClip>();
    private readonly HashSet<string> ttsInFlight = new HashSet<string>();
    private readonly Dictionary<string, float> ttsLastRequest = new Dictionary<string, float>();
    private readonly List<string> chatLog = new List<string>();
    private readonly Dictionary<string, List<string>> agentChatLogs = new Dictionary<string, List<string>>();
    private AudioClip voiceRecordingClip;
    private string voiceRecordingDevice;
    private bool isVoiceRecording;
    private bool sttInFlight;
    private float voiceRecordingStartedAt;
    private AgentPlacement[] lastAgents;
    private FunctionalMldsV2QuickAgentBridge functionalMldsV2Bridge;
    private readonly FunctionalMldsSceneObjectBindingRegistry spatialBindingRegistry =
        new FunctionalMldsSceneObjectBindingRegistry();
    private FunctionalMldsSceneBindingBootstrapper.Report lastSpatialBootstrapReport;
    private FunctionalMldsSceneObjectBinding selectedSpatialTarget;
    private string spatialSelectionState = FunctionalMldsSpatialTargetStates.None;
    private string spatialSelectionReason = "No target selected.";
    private string spatialSelectionModality = "";
    private string[] spatialSelectionCandidates = Array.Empty<string>();
    private Vector3 spatialSelectionHitPosition;
    private float spatialSelectionDistance;
    private string currentModelSha256 = "";
    private string interactionEvidenceStatus = "Noch keine modellgebundene Interaktionsbewertung.";
    private string statusMessage = "";
    private string chatInput = "";
    private const string ChatInputControlName = "chatInputField";
    private bool isChatInputFocused = false;
    private Vector2 agentScroll;
    private Vector2 chatScroll;
    private Vector2 uiScroll;
    private Vector2 projectScroll;
    private bool useProjectSelection = true;
    private ProjectSummary[] projects = Array.Empty<ProjectSummary>();
    private int selectedProjectIndex = -1;
    private string selectedProjectId = "";
    private Texture2D fpvDirectionArrowTexture;
    private GUIStyle bubbleStyle;
    private GUIStyle bubblePointerStyle;
    private GameObject handoffRouteRoot;
    private Material handoffRouteMaterial;
    private readonly List<LineRenderer> handoffRouteDashes = new List<LineRenderer>();
    private readonly List<Vector3> handoffRouteCachedPoints = new List<Vector3>();
    private readonly List<Vector3> handoffRouteRenderPoints = new List<Vector3>();
    private float handoffLineExpiresAt;
    private string handoffFromId;
    private string handoffToId;
    private bool handoffRoutePersistUntilArrival;
    private Vector3 handoffRouteLastFrom;
    private Vector3 handoffRouteLastTo;
    private const float HandoffRouteRebuildDistance = 0.08f;
    private float cameraYaw;
    private float cameraPitch;
    private bool cameraInitialized;
    private bool _fpvActive;
    private Transform _fpvSavedTransform;
    private Vector3 _fpvSavedPos;
    private Quaternion _fpvSavedRot;
    private bool _fpvChatOpen;
    private bool _fpvChatJustOpened;
    private string _fpvChatInput = "";
    private string _fpvNearestAgentId = "";
    private string _pendingHandoffAgentId = "";
    private ChatEvent[] _pendingHandoffEvents;
    private const string FpvChatControlName = "fpvChatField";
    private const float InputSystemMouseDeltaScale = 0.05f;
    private const string BrowserVoiceTranscriptMethod = "OnBrowserVoiceTranscript";
    private const string BrowserVoiceErrorMethod = "OnBrowserVoiceError";
    private const string FallbackGroundName = "InteractiveAgents_FallbackGround";

    private void Start()
    {
        EnsureSceneBasics();
        EnsureSceneObjectColliders();
        RefreshSpatialBindingRegistry();
        StartCoroutine(SetupFromServer());
    }

    private void Update()
    {
        CheckFpvToggle();
        HandleVoiceInput();
        if (_fpvActive) UpdateFpvProximity();
        UpdatePendingAgentPulse();
        UpdateFreeMovement();

        if (enableSpatialTargetSelection && TryGetSelectPosition(out var screenPosition))
        {
            if (_fpvActive)
            {
                if (!_fpvChatOpen && Camera.main != null)
                {
                    var cameraTransform = Camera.main.transform;
                    TrySelectSpatialTargetFromRay(
                        new Ray(cameraTransform.position, cameraTransform.forward),
                        "desktop_ray");
                }
            }
            else
            {
                TrySelectFromScreenPosition(screenPosition);
            }
        }

        CleanupExpiredBubbles();
        UpdateHandoffLine();
    }

    private void CheckFpvToggle()
    {
        var pressed = false;
#if ENABLE_INPUT_SYSTEM
        var kb = Keyboard.current;
        if (kb != null && kb.f1Key.wasPressedThisFrame) pressed = true;
#elif ENABLE_LEGACY_INPUT_MANAGER
        if (Input.GetKeyDown(fpvToggleKey)) pressed = true;
#endif
        if (pressed) ToggleFpv();
    }

    private void ToggleFpv()
    {
        var cam = Camera.main;
        if (cam == null) return;
        var viewerTransform = GetViewerMovementTransform(cam);

        if (!_fpvActive)
        {
            EnsureSceneObjectColliders();
            _fpvSavedTransform = viewerTransform;
            _fpvSavedPos = viewerTransform.position;
            _fpvSavedRot = viewerTransform.rotation;

            MoveViewerToCameraWorldPosition(cam, viewerTransform, ComputeRoomCenter());
            if (viewerTransform == cam.transform)
            {
                cam.transform.rotation = Quaternion.identity;
            }
            cameraYaw   = 0f;
            cameraPitch = 0f;
            cameraInitialized = true;

            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible   = false;
            _fpvActive = true;
        }
        else
        {
            var restoreTransform = _fpvSavedTransform != null ? _fpvSavedTransform : viewerTransform;
            restoreTransform.position = _fpvSavedPos;
            restoreTransform.rotation = _fpvSavedRot;
            _fpvSavedTransform = null;

            Cursor.lockState = CursorLockMode.None;
            Cursor.visible   = true;
            _fpvActive        = false;
            cameraInitialized = false;
            _fpvChatOpen      = false;
            _fpvChatJustOpened = false;
            _fpvChatInput     = "";
            _fpvNearestAgentId = "";
            ClearPendingHandoff();
        }
    }

    private Vector3 ComputeRoomCenter()
    {
        var sum   = Vector3.zero;
        var count = 0;
        foreach (var v in agentObjects.Values)
        {
            if (v?.obj == null) continue;
            sum += v.obj.transform.position;
            count++;
        }
        var xz = count > 0 ? sum / count : Vector3.zero;
        return new Vector3(xz.x, fpvEyeHeight, xz.z);
    }

    private void EnsureSceneBasics()
    {
        if (Camera.main == null)
        {
            var cameraObject = new GameObject("Main Camera") { tag = "MainCamera" };
            var camera = cameraObject.AddComponent<Camera>();
            camera.transform.position = new Vector3(0f, 12f, -12f);
            camera.transform.rotation = Quaternion.Euler(35f, 0f, 0f);
        }

#if UNITY_2023_1_OR_NEWER
        if (FindAnyObjectByType<Light>() == null)
#else
        if (FindObjectOfType<Light>() == null)
#endif
        {
            var lightObject = new GameObject("Directional Light");
            var light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
        }

        EnsureFallbackGroundCollider();
    }

    private void EnsureFallbackGroundCollider()
    {
        if (!ensureFallbackGroundCollider)
        {
            return;
        }

        var groundObject = GameObject.Find(FallbackGroundName);
        if (groundObject == null)
        {
            groundObject = new GameObject(FallbackGroundName);
            groundObject.hideFlags = HideFlags.DontSave;
        }

        var collider = groundObject.GetComponent<BoxCollider>();
        if (collider == null)
        {
            collider = groundObject.AddComponent<BoxCollider>();
        }

        var sizeX = Mathf.Max(4f, fallbackGroundSize.x);
        var sizeZ = Mathf.Max(4f, fallbackGroundSize.y);
        var thickness = Mathf.Max(0.01f, fallbackGroundThickness);
        groundObject.transform.position = Vector3.zero;
        collider.center = new Vector3(0f, fallbackGroundY - thickness * 0.5f, 0f);
        collider.size = new Vector3(sizeX, thickness, sizeZ);
    }

    private void EnsureSceneObjectColliders()
    {
        if (!ensureSceneObjectColliders)
        {
            return;
        }

#if UNITY_2023_1_OR_NEWER
        var renderers = FindObjectsByType<Renderer>(FindObjectsInactive.Exclude);
#else
        var renderers = FindObjectsOfType<Renderer>();
#endif
        for (var i = 0; i < renderers.Length; i++)
        {
            var renderer = renderers[i];
            if (!IsSceneColliderRendererCandidate(renderer))
            {
                continue;
            }

            var bounds = renderer.bounds;
            if (!ShouldTreatAsSceneColliderObject(bounds))
            {
                continue;
            }

            var existing = renderer.GetComponent<Collider>();
            if (existing != null)
            {
                existing.isTrigger = false;
                continue;
            }

            var box = renderer.gameObject.AddComponent<BoxCollider>();
            box.isTrigger = false;
            box.center = renderer.transform.InverseTransformPoint(bounds.center);
            box.size = GetLocalColliderSize(renderer.transform, bounds.size);
        }
    }

    private bool IsSceneColliderRendererCandidate(Renderer renderer)
    {
        if (renderer == null || !renderer.enabled || !renderer.gameObject.activeInHierarchy)
        {
            return false;
        }

        if (renderer is LineRenderer || renderer is ParticleSystemRenderer)
        {
            return false;
        }

        var obj = renderer.gameObject;
        if (obj.name == FallbackGroundName
            || string.Equals(obj.name, "SelectionIndicator", StringComparison.OrdinalIgnoreCase))
        {
            return false;
        }

        var transform = renderer.transform;
        if (handoffRouteRoot != null && transform.IsChildOf(handoffRouteRoot.transform))
        {
            return false;
        }

        return !IsTransformPartOfAnyAgent(transform);
    }

    private bool ShouldTreatAsSceneColliderObject(Bounds bounds)
    {
        if (bounds.size.x < 0.05f && bounds.size.z < 0.05f)
        {
            return false;
        }

        if (bounds.max.y < fallbackGroundY + 0.08f)
        {
            return false;
        }

        if (bounds.size.y < 0.08f && (bounds.size.x > 1.25f || bounds.size.z > 1.25f))
        {
            return false;
        }

        return bounds.size.x < 80f && bounds.size.y < 30f && bounds.size.z < 80f;
    }

    private static Vector3 GetLocalColliderSize(Transform transform, Vector3 worldSize)
    {
        var scale = transform.lossyScale;
        return new Vector3(
            worldSize.x / Mathf.Max(0.001f, Mathf.Abs(scale.x)),
            worldSize.y / Mathf.Max(0.001f, Mathf.Abs(scale.y)),
            worldSize.z / Mathf.Max(0.001f, Mathf.Abs(scale.z)));
    }

    private IEnumerator SetupFromServer()
    {
        if (useProjectSelection && string.IsNullOrWhiteSpace(selectedProjectId))
        {
            statusMessage = "Kein Projekt ausgewählt.";
            yield break;
        }

        statusMessage = "Setup läuft...";
        ClearSpatialTarget("A new setup is being loaded.", "setup", false);
        currentModelSha256 = "";
        interactionEvidenceStatus = "Noch keine modellgebundene Interaktionsbewertung.";
        var setupStartedAt = Time.realtimeSinceStartupAsDouble;
        var url = $"{backendBaseUrl}/setup";
        var payload = new SetupRequestPaths
        {
            room_plan_path = useProjectSelection ? null : roomPlanPath,
            agents_path = useProjectSelection ? null : agentsPath,
            project_id = useProjectSelection ? selectedProjectId : null,
            memory_mode = memoryMode
        };
        var json = JsonUtility.ToJson(payload);

        using (var req = new UnityWebRequest(url, "POST"))
        {
            var body = Encoding.UTF8.GetBytes(json);
            req.uploadHandler = new UploadHandlerRaw(body);
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
            {
                statusMessage = "Setup fehlgeschlagen: " + req.error;
                chatLog.Add(statusMessage + " | " + req.downloadHandler.text);
                yield break;
            }

            var setupJson = req.downloadHandler.text;
            var resp = JsonUtility.FromJson<SetupResponse>(setupJson);
            if (resp == null)
            {
                statusMessage = "Setup fehlgeschlagen: ungültige JSON-Antwort.";
                chatLog.Add(statusMessage);
                yield break;
            }
            sessionId = resp.session_id;
            if (!string.IsNullOrEmpty(resp.memory_mode))
                memoryMode = resp.memory_mode;

            functionalMldsV2Bridge = null;
            string spatialBindingModelJson = null;
            string modelEndpoint;
            try
            {
                modelEndpoint = FunctionalMldsV2QuickAgentBridge.ModelEndpointFor(setupJson);
            }
            catch (Exception exception)
            {
                sessionId = "";
                statusMessage = "Setup verworfen: FunctionalMLDS-Vertrag ist ungültig: " + exception.Message;
                chatLog.Add(statusMessage);
                yield break;
            }

            if (!string.IsNullOrWhiteSpace(modelEndpoint))
            {
                var modelUrl = modelEndpoint.StartsWith("http://", StringComparison.OrdinalIgnoreCase)
                    || modelEndpoint.StartsWith("https://", StringComparison.OrdinalIgnoreCase)
                    ? modelEndpoint
                    : backendBaseUrl.TrimEnd('/') + "/" + modelEndpoint.TrimStart('/');
                using (var modelRequest = UnityWebRequest.Get(modelUrl))
                {
                    yield return modelRequest.SendWebRequest();
                    if (modelRequest.result != UnityWebRequest.Result.Success)
                    {
                        sessionId = "";
                        statusMessage = "Setup verworfen: V2-Modell konnte nicht geladen werden: " + modelRequest.error;
                        chatLog.Add(statusMessage + " | " + modelRequest.downloadHandler.text);
                        yield break;
                    }

                    try
                    {
                        spatialBindingModelJson = modelRequest.downloadHandler.text;
                        var logDirectory = Path.Combine(
                            Application.persistentDataPath,
                            "FunctionalMLDS",
                            string.IsNullOrWhiteSpace(selectedProjectId) ? "direct" : selectedProjectId);
                        functionalMldsV2Bridge = FunctionalMldsV2QuickAgentBridge.Create(
                            setupJson,
                            spatialBindingModelJson,
                            logDirectory);
                    }
                    catch (Exception exception)
                    {
                        sessionId = "";
                        statusMessage = "Setup verworfen: V2-Modell/Trace ist inkonsistent: " + exception.Message;
                        chatLog.Add(statusMessage);
                        yield break;
                    }
                }
            }

            lastAgents = resp.agents ?? Array.Empty<AgentPlacement>();
            if (functionalMldsV2Bridge != null
                && !ValidateExecutableAgentPlacements(lastAgents, out var placementError))
            {
                sessionId = "";
                statusMessage = "Setup verworfen: V2-Agentenplatzierung ist ungültig: " + placementError;
                chatLog.Add(statusMessage);
                yield break;
            }
            currentModelSha256 = string.IsNullOrWhiteSpace(resp.model_sha256)
                ? string.Empty
                : resp.model_sha256.Trim();
            statusMessage = $"Setup OK. Memory: {memoryMode} | Agents: {lastAgents.Length}";
            UpdateAgentVoices(lastAgents);
            SpawnAgents(lastAgents);
            InitializeSpatialBindings(spatialBindingModelJson);
            if (lastAgents.Length > 0)
            {
                SetActiveAgentId(lastAgents[0].id);
            }

            if (functionalMldsV2Bridge != null
                && !TryRecordFunctionalMldsV2(
                    "setup",
                    "unity_setup_completed",
                    "success",
                    json,
                    setupJson,
                    (Time.realtimeSinceStartupAsDouble - setupStartedAt) * 1000.0,
                    null))
            {
                sessionId = "";
                yield break;
            }

            if (useProjectSelection)
            {
                statusMessage = $"Setup OK. Projekt: {selectedProjectId} | Memory: {memoryMode} | Agents: {lastAgents.Length}";
            }
            if (!spatialBindingRegistry.IsValid)
            {
                statusMessage += " | Spatial Grounding blockiert";
                chatLog.Add(
                    "Spatial Grounding blockiert: "
                    + spatialBindingRegistry.ValidationSummary());
            }
        }
    }

    private IEnumerator RefreshProjects()
    {
        statusMessage = "Projekte laden...";
        var url = $"{backendBaseUrl}/projects";
        using (var req = UnityWebRequest.Get(url))
        {
            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
            {
                statusMessage = "Projektliste fehlgeschlagen: " + req.error;
                yield break;
            }

            var resp = JsonUtility.FromJson<ProjectListResponse>(req.downloadHandler.text);
            projects = resp?.projects ?? Array.Empty<ProjectSummary>();
            UpdateProjectSelection();
            statusMessage = $"Projekte geladen: {projects.Length}";
        }
    }

    private void UpdateProjectSelection()
    {
        if (projects.Length == 0)
        {
            selectedProjectIndex = -1;
            selectedProjectId = "";
            return;
        }

        if (!string.IsNullOrWhiteSpace(selectedProjectId))
        {
            for (var i = 0; i < projects.Length; i++)
            {
                if (projects[i].id == selectedProjectId)
                {
                    selectedProjectIndex = i;
                    return;
                }
            }
        }

        selectedProjectIndex = 0;
        selectedProjectId = projects[0].id;
    }

    private void UpdateAgentVoices(AgentPlacement[] agents)
    {
        agentVoices.Clear();
        if (agents == null)
        {
            return;
        }

        foreach (var agent in agents)
        {
            if (string.IsNullOrWhiteSpace(agent.id))
            {
                continue;
            }

            agentVoices[agent.id] = new AgentVoiceSettings
            {
                voice = agent.voice,
                voiceStyle = agent.voice_style,
                ttsModel = agent.tts_model
            };
        }
    }

    private void SpawnAgents(AgentPlacement[] agents)
    {
        foreach (var entry in agentObjects)
        {
            if (entry.Value != null)
            {
                if (entry.Value.animGraph.IsValid())
                    entry.Value.animGraph.Destroy();
                if (entry.Value.obj != null)
                    Destroy(entry.Value.obj);
            }
        }
        agentObjects.Clear();

        var idleClips = LoadAllClipsFromFolder(animationResourceFolder);
        if (idleClips.Length == 0)
            Debug.LogWarning($"[QuickAgentManager] Keine AnimationClips in Resources/{animationResourceFolder} gefunden.");

        var characterPrefabs = LoadCharacterPrefabs();
        var useCharacters = characterPrefabs.Length > 0;
        if (!useCharacters)
        {
            Debug.LogWarning("[QuickAgentManager] Keine Prefabs in Resources/Characters – nutze Würfel als Fallback.");
        }

        for (var i = 0; i < agents.Length; i++)
        {
            var agent = agents[i];
            var id = string.IsNullOrEmpty(agent.id) ? $"agent_{i + 1}" : agent.id;
            var displayName = string.IsNullOrEmpty(agent.display_name) ? id : agent.display_name;

            var pos = GetAgentSpawnPosition(agent);

            GameObject agentGo;
            Renderer mainRenderer;
            float visualScale;

            if (useCharacters)
            {
                var prefab = characterPrefabs[UnityEngine.Random.Range(0, characterPrefabs.Length)];
                agentGo = Instantiate(prefab, pos, Quaternion.identity);
                agentGo.name = $"Agent_{displayName}";
                ApplyAgentForward(agent, agentGo.transform);

                // Capsule collider on root for click selection
                if (agentGo.GetComponent<Collider>() == null)
                {
                    var cap = agentGo.AddComponent<CapsuleCollider>();
                    cap.height = 1.8f;
                    cap.radius = 0.3f;
                    cap.center = new Vector3(0f, 0.9f, 0f);
                }

                // Small disc indicator below feet for active-agent highlighting
                var indicator = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                indicator.name = "SelectionIndicator";
                indicator.transform.SetParent(agentGo.transform, false);
                indicator.transform.localPosition = new Vector3(0f, 0.02f, 0f);
                indicator.transform.localScale = new Vector3(0.5f, 0.01f, 0.5f);
                if (indicator.TryGetComponent<Collider>(out var indicatorCol))
                    Destroy(indicatorCol);
                mainRenderer = indicator.GetComponent<Renderer>();
                visualScale = 1.8f;
            }
            else
            {
                agentGo = GameObject.CreatePrimitive(PrimitiveType.Cube);
                agentGo.name = $"Agent_{displayName}";
                agentGo.transform.position = pos;
                ApplyAgentForward(agent, agentGo.transform);
                var scale = UnityEngine.Random.Range(boxScaleRange.x, boxScaleRange.y);
                agentGo.transform.localScale = Vector3.one * scale;
                mainRenderer = agentGo.GetComponent<Renderer>();
                visualScale = scale;
            }

            var baseColor = Color.Lerp(new Color(0.3f, 0.6f, 1f), Color.white, 0.2f * i);
            if (mainRenderer != null)
            {
                mainRenderer.material.color = baseColor;
            }

            var audioSource = agentGo.AddComponent<AudioSource>();
            audioSource.playOnAwake = false;

            var idleClip = idleClips.Length > 0
                ? idleClips[UnityEngine.Random.Range(0, idleClips.Length)]
                : null;

            var animGraph = new PlayableGraph();
            if (useCharacters && idleClip != null)
            {
                var animator = agentGo.GetComponent<Animator>();
                if (animator == null)
                    animator = agentGo.AddComponent<Animator>();
                animGraph = PlayableGraph.Create($"Idle_{id}");
                var clipPlayable = AnimationClipPlayable.Create(animGraph, idleClip);
                var output = AnimationPlayableOutput.Create(animGraph, "Idle", animator);
                output.SetSourcePlayable(clipPlayable);
                animGraph.SetTimeUpdateMode(DirectorUpdateMode.GameTime);
                animGraph.Play();
            }

            agentObjects[id] = new AgentVisual
            {
                obj = agentGo,
                renderer = mainRenderer,
                baseColor = baseColor,
                scale = visualScale,
                audioSource = audioSource,
                animGraph = animGraph,
            };
        }

        UpdateAgentHighlights();
        EnsureSceneObjectColliders();
    }

    private AnimationClip[] LoadAllClipsFromFolder(string folder)
    {
        var assets = Resources.LoadAll<AnimationClip>(folder);
        var result = new List<AnimationClip>();
        foreach (var clip in assets)
        {
            if (!clip.name.StartsWith("__preview__"))
                result.Add(clip);
        }
        return result.ToArray();
    }

    private GameObject[] LoadCharacterPrefabs()
    {
        var assets = Resources.LoadAll<GameObject>("Characters");
        if (assets == null || assets.Length == 0)
        {
            return Array.Empty<GameObject>();
        }

        var result = new List<GameObject>();
        var skipped = 0;

        foreach (var asset in assets)
        {
            if (asset == null)
            {
                skipped++;
                continue;
            }

            // Animation FBX assets include '@' (for example 'Ch23_nonPBR@Idle')
            // and should not be spawned as character prefabs.
            if (asset.name.Contains("@"))
            {
                skipped++;
                continue;
            }

            if (!HasRenderableCharacterMesh(asset))
            {
                skipped++;
                continue;
            }

            result.Add(asset);
        }

        if (result.Count == 0)
        {
            Debug.LogWarning("[QuickAgentManager] Gefilterte Character-Liste ist leer - fallback auf ungefilterte Resources/Characters Assets.");
            return assets;
        }

        Debug.Log($"[QuickAgentManager] Character-Prefabs geladen: {result.Count} (gefiltert: {skipped}).");
        return result.ToArray();
    }

    private static bool HasRenderableCharacterMesh(GameObject candidate)
    {
        if (candidate == null)
        {
            return false;
        }

        var renderers = candidate.GetComponentsInChildren<SkinnedMeshRenderer>(true);
        if (renderers == null || renderers.Length == 0)
        {
            return false;
        }

        for (var i = 0; i < renderers.Length; i++)
        {
            var renderer = renderers[i];
            if (renderer == null)
            {
                continue;
            }

            var materials = renderer.sharedMaterials;
            if (materials == null || materials.Length == 0)
            {
                continue;
            }

            for (var m = 0; m < materials.Length; m++)
            {
                var material = materials[m];
                if (material == null)
                {
                    continue;
                }

                if (material.mainTexture != null)
                {
                    return true;
                }

                if (material.HasProperty("_BaseMap") && material.GetTexture("_BaseMap") != null)
                {
                    return true;
                }

                if (material.HasProperty("_MainTex") && material.GetTexture("_MainTex") != null)
                {
                    return true;
                }
            }
        }

        return false;
    }

    private void OnDestroy()
    {
        if (selectedSpatialTarget != null)
            selectedSpatialTarget.SetHighlighted(false, selectedSpatialTargetColor, 0f);

        foreach (var entry in agentObjects)
        {
            if (entry.Value != null && entry.Value.animGraph.IsValid())
                entry.Value.animGraph.Destroy();
        }

        if (fpvDirectionArrowTexture != null)
            Destroy(fpvDirectionArrowTexture);
    }

    private Vector3 GetAgentSpawnPosition(AgentPlacement agent)
    {
        if (agent != null && agent.position != null)
        {
            return new Vector3(agent.position.x, agent.position.y, agent.position.z);
        }

        return new Vector3(
            UnityEngine.Random.Range(-spawnArea.x * 0.5f, spawnArea.x * 0.5f),
            spawnHeight,
            UnityEngine.Random.Range(-spawnArea.z * 0.5f, spawnArea.z * 0.5f)
        );
    }

    private static bool ValidateExecutableAgentPlacements(AgentPlacement[] agents, out string error)
    {
        error = "";
        var ids = new HashSet<string>(StringComparer.Ordinal);
        for (var index = 0; index < (agents?.Length ?? 0); index++)
        {
            var agent = agents[index];
            var id = agent == null ? "" : (agent.id ?? "").Trim();
            if (string.IsNullOrEmpty(id) || !ids.Add(id))
            {
                error = $"Agent {index} hat keine eindeutige ID.";
                return false;
            }
            if (agent.position == null || agent.forward == null)
            {
                error = $"Agent '{id}' benötigt Position und Blickrichtung.";
                return false;
            }
            if (!IsFinite(agent.position.x) || !IsFinite(agent.position.y) || !IsFinite(agent.position.z)
                || !IsFinite(agent.forward.x) || !IsFinite(agent.forward.y) || !IsFinite(agent.forward.z))
            {
                error = $"Agent '{id}' enthält nicht-endliche Koordinaten.";
                return false;
            }
            if (Mathf.Abs(agent.position.y) > 0.001f || Mathf.Abs(agent.forward.y) > 0.001f)
            {
                error = $"Agent '{id}' muss planar auf X/Z platziert sein.";
                return false;
            }
            var forwardLength = new Vector2(agent.forward.x, agent.forward.z).magnitude;
            if (Mathf.Abs(forwardLength - 1f) > 0.002f)
            {
                error = $"Blickrichtung von Agent '{id}' ist nicht normalisiert.";
                return false;
            }
        }
        return true;
    }

    private static bool IsFinite(float value)
    {
        return !float.IsNaN(value) && !float.IsInfinity(value);
    }

    private void ApplyAgentForward(AgentPlacement agent, Transform target)
    {
        if (agent == null || target == null || agent.forward == null)
        {
            return;
        }

        var forward = new Vector3(agent.forward.x, agent.forward.y, agent.forward.z);
        if (forward.sqrMagnitude <= 0.0001f)
        {
            return;
        }

        target.rotation = Quaternion.LookRotation(forward, Vector3.up);
    }

    private bool TryGetSelectPosition(out Vector2 screenPosition)
    {
#if ENABLE_INPUT_SYSTEM
        if (Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame)
        {
            screenPosition = Mouse.current.position.ReadValue();
            return true;
        }
#elif ENABLE_LEGACY_INPUT_MANAGER
        if (Input.GetMouseButtonDown(0))
        {
            screenPosition = Input.mousePosition;
            return true;
        }
#endif

        screenPosition = default;
        return false;
    }

    private void TrySelectFromScreenPosition(Vector2 screenPosition)
    {
        var cam = Camera.main;
        if (cam == null)
        {
            SetSpatialTargetAmbiguous(
                "No main camera is available for target selection.",
                "mouse_ray",
                Array.Empty<string>());
            return;
        }

        TrySelectSpatialTargetFromRay(
            cam.ScreenPointToRay(screenPosition),
            "mouse_ray");
    }

    /// <summary>
    /// Package-independent ray hook for desktop and XR controllers. A WebXR/XRI adapter can
    /// pass its controller ray and the modality "xr_controller_ray" without this
    /// component claiming or depending on a particular XR input implementation.
    /// </summary>
    public bool TrySelectSpatialTargetFromRay(Ray ray, string selectionModality)
    {
        if (!enableSpatialTargetSelection)
            return false;

        var modality = NormalizeSpatialSelectionModality(selectionModality);
        if (modality == null)
        {
            SetSpatialTargetAmbiguous(
                $"Unsupported selection modality '{selectionModality}'.",
                "programmatic",
                Array.Empty<string>());
            return false;
        }
        LogSpatialEvent(
            "target_selection_started",
            spatialSelectionState,
            modality,
            string.Empty,
            spatialSelectionCandidates);

        var maximumDistance = Mathf.Max(0.01f, spatialSelectionMaxDistance);
        var hits = Physics.RaycastAll(
            ray,
            maximumDistance,
            spatialSelectionMask,
            QueryTriggerInteraction.Ignore);
        if (hits == null || hits.Length == 0)
        {
            ClearSpatialTarget("Raycast hit no selectable object.", modality, true);
            return false;
        }
        Array.Sort(hits, (left, right) => left.distance.CompareTo(right.distance));

        var frontDistance = hits[0].distance;
        var tolerance = Mathf.Max(0f, spatialAmbiguityDistanceTolerance);
        var relevantHitCount = 0;
        while (relevantHitCount < hits.Length
               && hits[relevantHitCount].distance <= frontDistance + tolerance)
        {
            relevantHitCount++;
        }

        // Preserve the original agent-selection behavior. Agent colliders at the first
        // surface take precedence and do not clear an already selected semantic target.
        for (var hitIndex = 0; hitIndex < relevantHitCount; hitIndex++)
        {
            string agentId;
            if (TryGetAgentIdForCollider(hits[hitIndex].collider, out agentId))
            {
                SetActiveAgentId(agentId, true);
                LogSpatialEvent(
                    "agent_selected_by_ray",
                    spatialSelectionState,
                    modality,
                    "Ray hit an agent; semantic target selection is unchanged.",
                    spatialSelectionCandidates);
                return true;
            }
        }

        if (!spatialBindingRegistry.IsValid)
        {
            var invalidCandidates = RegisteredSpatialEntityIds();
            SetSpatialTargetAmbiguous(
                "Scene bindings are invalid: " + spatialBindingRegistry.ValidationSummary(),
                modality,
                invalidCandidates);
            return false;
        }

        var candidateBindings = new List<FunctionalMldsSceneObjectBinding>();
        var candidateHits = new List<RaycastHit>();
        for (var hitIndex = 0; hitIndex < relevantHitCount; hitIndex++)
        {
            var resolution = spatialBindingRegistry.ResolveCollider(hits[hitIndex].collider);
            if (resolution.State == FunctionalMldsSpatialTargetStates.Ambiguous)
            {
                SetSpatialTargetAmbiguous(
                    resolution.Reason,
                    modality,
                    resolution.CandidateEntityIds);
                return false;
            }
            if (!resolution.IsResolved || candidateBindings.Contains(resolution.Binding))
                continue;
            candidateBindings.Add(resolution.Binding);
            candidateHits.Add(hits[hitIndex]);
        }

        if (candidateBindings.Count == 0)
        {
            ClearSpatialTarget(
                $"Front collider '{hits[0].collider.name}' has no semantic binding.",
                modality,
                true);
            return false;
        }
        if (candidateBindings.Count > 1)
        {
            var candidateIds = new List<string>();
            for (var i = 0; i < candidateBindings.Count; i++)
                candidateIds.Add(candidateBindings[i].EntityId);
            SetSpatialTargetAmbiguous(
                $"{candidateBindings.Count} semantic objects overlap at the selected surface.",
                modality,
                candidateIds);
            return false;
        }

        if (string.IsNullOrWhiteSpace(currentModelSha256))
        {
            SetSpatialTargetAmbiguous(
                "The selected object is not anchored to a loaded V2 model hash.",
                modality,
                new[] { candidateBindings[0].EntityId });
            return false;
        }

        SetSpatialTargetResolved(
            candidateBindings[0],
            candidateHits[0].point,
            candidateHits[0].distance,
            modality);
        return true;
    }

    public void ClearSelectedSpatialTarget()
    {
        ClearSpatialTarget("Selection cleared by the user.", "ui", true);
    }

    public void RefreshSpatialBindingRegistry()
    {
        var all = Resources.FindObjectsOfTypeAll<FunctionalMldsSceneObjectBinding>();
        var sceneBindings = new List<FunctionalMldsSceneObjectBinding>();
        for (var i = 0; i < all.Length; i++)
        {
            var binding = all[i];
            if (binding == null
                || !binding.gameObject.scene.IsValid()
                || !binding.gameObject.scene.isLoaded)
            {
                continue;
            }
            sceneBindings.Add(binding);
        }

        spatialBindingRegistry.Rebuild(
            sceneBindings,
            lastSpatialBootstrapReport == null
                ? null
                : lastSpatialBootstrapReport.Errors);
    }

    private void InitializeSpatialBindings(string modelJson)
    {
        if (string.IsNullOrWhiteSpace(modelJson))
        {
            FunctionalMldsSceneBindingBootstrapper.DisableGeneratedBindings();
            lastSpatialBootstrapReport = null;
        }
        else
        {
            lastSpatialBootstrapReport =
                FunctionalMldsSceneBindingBootstrapper.ApplyV2Model(modelJson);
        }

        RefreshSpatialBindingRegistry();
        Debug.Log(
            "[SpatialGrounding] binding_registry="
            + spatialBindingRegistry.ValidationSummary()
            + (lastSpatialBootstrapReport == null
                ? "; bootstrap=manual_only"
                : "; bootstrap=" + lastSpatialBootstrapReport.Summary()));
    }

    private bool TryGetAgentIdForCollider(Collider collider, out string agentId)
    {
        agentId = string.Empty;
        if (collider == null)
            return false;

        var hitTransform = collider.transform;
        while (hitTransform != null)
        {
            foreach (var pair in agentObjects)
            {
                if (pair.Value != null
                    && pair.Value.obj != null
                    && pair.Value.obj.transform == hitTransform)
                {
                    agentId = pair.Key;
                    return true;
                }
            }
            hitTransform = hitTransform.parent;
        }
        return false;
    }

    private void SetSpatialTargetResolved(
        FunctionalMldsSceneObjectBinding binding,
        Vector3 hitPosition,
        float distance,
        string modality)
    {
        if (selectedSpatialTarget != null && selectedSpatialTarget != binding)
        {
            selectedSpatialTarget.SetHighlighted(
                false,
                selectedSpatialTargetColor,
                selectedSpatialTargetEmission);
        }

        selectedSpatialTarget = binding;
        spatialSelectionState = FunctionalMldsSpatialTargetStates.Resolved;
        spatialSelectionReason = string.Empty;
        spatialSelectionModality = modality;
        spatialSelectionCandidates = new[] { binding.EntityId };
        spatialSelectionHitPosition = hitPosition;
        spatialSelectionDistance = Mathf.Max(0f, distance);
        binding.SetHighlighted(
            true,
            selectedSpatialTargetColor,
            selectedSpatialTargetEmission);
        statusMessage = $"Raumziel: {binding.DisplayName} ({binding.SourceObjectId})";
        LogSpatialEvent(
            "target_selection_resolved",
            spatialSelectionState,
            modality,
            string.Empty,
            spatialSelectionCandidates);
        if (functionalMldsV2Bridge != null)
        {
            FunctionalMldsV2InteractionAssessment ignoredAssessment;
            TryRecordFunctionalMldsV2Interaction(
                "chat",
                "unity_target_selection_resolved",
                CreateInteractionObservation(
                    FunctionalMldsV2InteractionEvidenceEvaluator.DeicticMode,
                    null,
                    responseObserved: false),
                new
                {
                    binding.EntityId,
                    binding.SourceObjectId,
                    selection_modality = modality
                },
                new { selection_state = spatialSelectionState },
                null,
                requireCompletion: false,
                out ignoredAssessment);
        }
    }

    private void SetSpatialTargetAmbiguous(
        string reason,
        string modality,
        IEnumerable<string> candidateEntityIds)
    {
        if (selectedSpatialTarget != null)
        {
            selectedSpatialTarget.SetHighlighted(
                false,
                selectedSpatialTargetColor,
                selectedSpatialTargetEmission);
        }

        selectedSpatialTarget = null;
        spatialSelectionState = FunctionalMldsSpatialTargetStates.Ambiguous;
        spatialSelectionReason = string.IsNullOrWhiteSpace(reason)
            ? "Spatial target is ambiguous."
            : reason.Trim();
        spatialSelectionModality = modality ?? string.Empty;
        spatialSelectionCandidates = UniqueSorted(candidateEntityIds);
        spatialSelectionHitPosition = Vector3.zero;
        spatialSelectionDistance = 0f;
        statusMessage = "Raumziel mehrdeutig: " + spatialSelectionReason;
        LogSpatialEvent(
            "target_selection_ambiguous",
            spatialSelectionState,
            spatialSelectionModality,
            spatialSelectionReason,
            spatialSelectionCandidates);
    }

    private void ClearSpatialTarget(
        string reason,
        string modality,
        bool logEvent)
    {
        if (selectedSpatialTarget != null)
        {
            selectedSpatialTarget.SetHighlighted(
                false,
                selectedSpatialTargetColor,
                selectedSpatialTargetEmission);
        }

        selectedSpatialTarget = null;
        spatialSelectionState = FunctionalMldsSpatialTargetStates.None;
        spatialSelectionReason = string.IsNullOrWhiteSpace(reason)
            ? "No target selected."
            : reason.Trim();
        spatialSelectionModality = modality ?? string.Empty;
        spatialSelectionCandidates = Array.Empty<string>();
        spatialSelectionHitPosition = Vector3.zero;
        spatialSelectionDistance = 0f;
        if (logEvent)
        {
            statusMessage = "Kein Raumziel: " + spatialSelectionReason;
            LogSpatialEvent(
                "target_selection_no_target",
                spatialSelectionState,
                spatialSelectionModality,
                spatialSelectionReason,
                spatialSelectionCandidates);
        }
    }

    private SpatialContext CreateResolvedSpatialContext()
    {
        if (spatialSelectionState != FunctionalMldsSpatialTargetStates.Resolved
            || selectedSpatialTarget == null
            || string.IsNullOrWhiteSpace(currentModelSha256))
        {
            return null;
        }

        return new SpatialContext
        {
            model_sha256 = currentModelSha256,
            state = FunctionalMldsSpatialTargetStates.Resolved,
            entity_id = selectedSpatialTarget.EntityId,
            source_object_id = selectedSpatialTarget.SourceObjectId,
            object_group_id = selectedSpatialTarget.ObjectGroupId,
            zone_id = selectedSpatialTarget.ZoneId,
            display_name = selectedSpatialTarget.DisplayName,
            synonyms = (string[])selectedSpatialTarget.Synonyms.Clone(),
            hit_position = new Vector3Data
            {
                x = spatialSelectionHitPosition.x,
                y = spatialSelectionHitPosition.y,
                z = spatialSelectionHitPosition.z
            },
            distance_m = spatialSelectionDistance,
            selection_modality = spatialSelectionModality,
            ambiguity_reason = string.Empty,
            candidate_entity_ids = new[] { selectedSpatialTarget.EntityId }
        };
    }

    private static bool ValidateGroundedResponse(
        ChatResponse response,
        SpatialContext requestContext,
        out string error)
    {
        error = string.Empty;
        if (response == null || requestContext == null)
        {
            error = "Grounding response or request context is missing.";
            return false;
        }
        if (response.grounding == null
            || response.grounding.status != FunctionalMldsSpatialTargetStates.Resolved)
        {
            error = "Backend response has no resolved grounding object.";
            return false;
        }
        if (!string.Equals(
                response.grounding.model_sha256,
                requestContext.model_sha256,
                StringComparison.OrdinalIgnoreCase))
        {
            error = "Backend response references a different model hash.";
            return false;
        }
        if (!string.Equals(
                response.grounding.selected_entity_id,
                requestContext.entity_id,
                StringComparison.Ordinal)
            || !string.Equals(
                response.grounding.selected_source_object_id,
                requestContext.source_object_id,
                StringComparison.Ordinal))
        {
            error = "Backend response resolved a different scene object.";
            return false;
        }
        if (!ContainsOrdinal(response.grounded_entity_ids, requestContext.entity_id)
            || !ContainsEvidenceForTarget(
                response.grounding_evidence,
                requestContext.entity_id,
                requestContext.source_object_id))
        {
            error = "Backend response has no model-grounding evidence for the selected entity.";
            return false;
        }
        if (response.routing == null
            || string.IsNullOrWhiteSpace(response.routing.selected_agent_id)
            || string.IsNullOrWhiteSpace(response.routing.reason)
            || !string.Equals(
                response.routing.selected_agent_id,
                response.active_agent_id,
                StringComparison.Ordinal))
        {
            error = "Backend response has no consistent model-grounded routing decision.";
            return false;
        }
        return true;
    }

    private static bool ContainsEvidenceForTarget(
        IEnumerable<GroundingEvidenceItem> evidence,
        string entityId,
        string sourceObjectId)
    {
        if (evidence == null)
            return false;
        foreach (var item in evidence)
        {
            if (item == null)
                continue;
            if (string.Equals(item.subject_id, entityId, StringComparison.Ordinal)
                || string.Equals(item.object_id, entityId, StringComparison.Ordinal)
                || string.Equals(item.source_object_id, sourceObjectId, StringComparison.Ordinal))
            {
                return true;
            }
        }
        return false;
    }

    private static bool ContainsOrdinal(IEnumerable<string> values, string expected)
    {
        if (values == null)
            return false;
        foreach (var value in values)
        {
            if (string.Equals(value, expected, StringComparison.Ordinal))
                return true;
        }
        return false;
    }

    private string[] RegisteredSpatialEntityIds()
    {
        var result = new List<string>();
        var registered = spatialBindingRegistry.Bindings;
        for (var i = 0; i < registered.Count; i++)
        {
            if (registered[i] != null)
                result.Add(registered[i].EntityId);
        }
        return UniqueSorted(result);
    }

    private static string[] UniqueSorted(IEnumerable<string> values)
    {
        var seen = new HashSet<string>(StringComparer.Ordinal);
        var result = new List<string>();
        if (values != null)
        {
            foreach (var value in values)
            {
                if (string.IsNullOrWhiteSpace(value))
                    continue;
                var clean = value.Trim();
                if (seen.Add(clean))
                    result.Add(clean);
            }
        }
        result.Sort(StringComparer.Ordinal);
        return result.ToArray();
    }

    private static string NormalizeSpatialSelectionModality(string value)
    {
        var modality = string.IsNullOrWhiteSpace(value)
            ? "programmatic"
            : value.Trim().ToLowerInvariant();
        switch (modality)
        {
            case "desktop_ray":
            case "mouse_ray":
            case "keyboard_mouse":
            case "xr_controller_ray":
            case "controller_ray":
            case "gaze":
            case "touch":
            case "direct":
            case "programmatic":
                return modality;
            default:
                return null;
        }
    }

    private void LogSpatialEvent(
        string eventType,
        string state,
        string modality,
        string reason,
        string[] candidates)
    {
        var item = new SpatialSelectionEvent
        {
            event_type = eventType ?? string.Empty,
            state = state ?? FunctionalMldsSpatialTargetStates.None,
            entity_id = selectedSpatialTarget == null
                ? string.Empty
                : selectedSpatialTarget.EntityId,
            source_object_id = selectedSpatialTarget == null
                ? string.Empty
                : selectedSpatialTarget.SourceObjectId,
            selection_modality = modality ?? string.Empty,
            reason = reason ?? string.Empty,
            candidate_entity_ids = candidates ?? Array.Empty<string>(),
            time_since_start_s = Time.realtimeSinceStartup
        };
        Debug.Log("[SpatialGrounding] " + JsonUtility.ToJson(item));
        var handler = SpatialEventLogged;
        if (handler != null)
            handler(item);
    }

    private IEnumerator SendChat(string message)
    {
        if (string.IsNullOrEmpty(sessionId))
        {
            statusMessage = "Kein sessionId. Setup zuerst ausführen.";
            yield break;
        }

        if (string.IsNullOrEmpty(activeAgentId))
        {
            statusMessage = "Kein aktiver Agent ausgewählt.";
            yield break;
        }

        // Once the user has attempted a spatial selection, an ambiguous result must never
        // silently fall back to an ungrounded answer. "none" remains backwards compatible
        // for ordinary, non-deictic chat.
        if (spatialSelectionState == FunctionalMldsSpatialTargetStates.Ambiguous)
        {
            statusMessage = "Chat blockiert: Raumziel ist mehrdeutig. "
                + spatialSelectionReason;
            chatLog.Add(statusMessage);
            yield break;
        }

        var url = $"{backendBaseUrl}/chat";
        var chatStartedAt = Time.realtimeSinceStartupAsDouble;
        var spatialContext = CreateResolvedSpatialContext();
        var interactionMode = ResolveV2InteractionMode(
            functionalMldsV2Bridge != null,
            spatialSelectionState,
            spatialContext);
        var preflightObservation = functionalMldsV2Bridge == null
            ? null
            : CreateInteractionObservation(interactionMode, null, responseObserved: false);
        if (functionalMldsV2Bridge != null
            && !TryRequireFunctionalMldsV2Action("chat", preflightObservation))
        {
            yield break;
        }
        var payload = new ChatRequest
        {
            session_id = sessionId,
            active_agent_id = activeAgentId,
            user_text = message,
            interaction_mode = interactionMode,
            spatial_context = spatialContext
        };
        var json = SerializeChatRequest(payload);
        if (spatialContext != null)
        {
            LogSpatialEvent(
                "grounded_chat_sent",
                spatialSelectionState,
                spatialSelectionModality,
                string.Empty,
                spatialSelectionCandidates);
        }

        using (var req = new UnityWebRequest(url, "POST"))
        {
            var body = Encoding.UTF8.GetBytes(json);
            req.uploadHandler = new UploadHandlerRaw(body);
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
            {
                if (spatialContext != null)
                {
                    LogSpatialEvent(
                        "grounded_response_failed",
                        spatialSelectionState,
                        spatialSelectionModality,
                        req.error,
                        spatialSelectionCandidates);
                }
                statusMessage = "Chat fehlgeschlagen: " + req.error;
                chatLog.Add(statusMessage + " | " + req.downloadHandler.text);
                if (functionalMldsV2Bridge != null)
                {
                    TryRecordFunctionalMldsV2(
                        "chat",
                        "unity_chat_received",
                        "error",
                        json,
                        req.downloadHandler.text,
                        (Time.realtimeSinceStartupAsDouble - chatStartedAt) * 1000.0,
                        req.error,
                        preflightObservation);
                }
                yield break;
            }

            // Chat responses contain nullable evidence fields (for example
            // routing.modeled_handoff). Unity's JsonUtility does not reliably
            // deserialize Nullable<T>; use the same Newtonsoft contract as the
            // request path so absence and false remain distinguishable.
            ChatResponse resp = null;
            try
            {
                resp = JsonConvert.DeserializeObject<ChatResponse>(req.downloadHandler.text);
            }
            catch (JsonException exception)
            {
                statusMessage = "Chat fehlgeschlagen: ungültige JSON-Antwort.";
                chatLog.Add(statusMessage);
                if (functionalMldsV2Bridge != null)
                {
                    TryRecordFunctionalMldsV2(
                        "chat",
                        "unity_chat_received",
                        "error",
                        json,
                        req.downloadHandler.text,
                        (Time.realtimeSinceStartupAsDouble - chatStartedAt) * 1000.0,
                        exception.Message,
                        preflightObservation);
                }
                yield break;
            }
            if (resp == null)
            {
                statusMessage = "Chat fehlgeschlagen: ungültige JSON-Antwort.";
                chatLog.Add(statusMessage);
                if (functionalMldsV2Bridge != null)
                {
                    TryRecordFunctionalMldsV2(
                        "chat",
                        "unity_chat_received",
                        "error",
                        json,
                        req.downloadHandler.text,
                        (Time.realtimeSinceStartupAsDouble - chatStartedAt) * 1000.0,
                        "Invalid JSON response",
                        preflightObservation);
                }
                yield break;
            }
            if (spatialContext != null
                && !ValidateGroundedResponse(resp, spatialContext, out var groundingError))
            {
                statusMessage = "Chat-Antwort verworfen: " + groundingError;
                chatLog.Add(statusMessage);
                LogSpatialEvent(
                    "grounded_response_failed",
                    spatialSelectionState,
                    spatialSelectionModality,
                    groundingError,
                    spatialSelectionCandidates);
                yield break;
            }
            var isHandoff = resp.handoff != null && !string.IsNullOrEmpty(resp.handoff.to);
            if (functionalMldsV2Bridge != null)
            {
                var observation = CreateInteractionObservation(
                    payload.interaction_mode,
                    resp,
                    responseObserved: true);
                FunctionalMldsV2InteractionAssessment chatAssessment;
                if (!TryRecordFunctionalMldsV2Interaction(
                    "chat",
                    "unity_grounded_chat_observed",
                    observation,
                    payload,
                    resp,
                    (Time.realtimeSinceStartupAsDouble - chatStartedAt) * 1000.0,
                    requireCompletion: true,
                    out chatAssessment))
                {
                    yield break;
                }
                if (isHandoff)
                {
                    FunctionalMldsV2InteractionAssessment handoffAssessment;
                    if (!TryRequireFunctionalMldsV2Action("handoff", observation)
                        || !TryRecordFunctionalMldsV2Interaction(
                            "handoff",
                            "unity_handoff_observed",
                            observation,
                            payload,
                            resp,
                            (Time.realtimeSinceStartupAsDouble - chatStartedAt) * 1000.0,
                            requireCompletion: true,
                            out handoffAssessment))
                    {
                        yield break;
                    }
                }
            }
            sessionId = resp.session_id;
            if (!string.IsNullOrEmpty(resp.memory_mode))
                memoryMode = resp.memory_mode;
            if (spatialContext != null)
            {
                LogSpatialEvent(
                    "grounded_response_received",
                    spatialSelectionState,
                    spatialSelectionModality,
                    resp.routing_reason ?? string.Empty,
                    spatialSelectionCandidates);
            }

            if (isHandoff && _fpvActive && fpvProximityHandoff)
            {
                // From-agent events go to log now; to-agent events are deferred until arrival
                var fromEvents = FilterEvents(resp.events, resp.handoff.from, include: true);
                var toEvents   = FilterEvents(resp.events, resp.handoff.from, include: false);
                AppendChatEvents(fromEvents);
                SetPendingHandoff(resp, toEvents);
                ShowPendingHandoffRoute(resp);
                StartCoroutine(ShowHandoffOnly(resp, fromEvents));
            }
            else
            {
                SetActiveAgentId(resp.active_agent_id);
                AppendChatEvents(resp.events);
                StartCoroutine(ShowChatBubbles(resp));
            }
        }
    }

    private bool TryRequireFunctionalMldsV2Action(
        string actionKind,
        FunctionalMldsV2InteractionObservation observation = null)
    {
        if (functionalMldsV2Bridge == null)
            return true;
        try
        {
            functionalMldsV2Bridge.RequireAction(actionKind, activeAgentId, observation);
            return true;
        }
        catch (Exception exception)
        {
            statusMessage = $"FunctionalMLDS V2 blockiert {actionKind}: {exception.Message}";
            chatLog.Add(statusMessage);
            return false;
        }
    }

    private bool TryRecordFunctionalMldsV2(
        string actionKind,
        string eventType,
        string status,
        object inputSummary,
        object outputSummary,
        double? durationMs,
        string errorSummary,
        FunctionalMldsV2InteractionObservation observation = null)
    {
        if (functionalMldsV2Bridge == null)
            return true;
        try
        {
            functionalMldsV2Bridge.Record(
                actionKind,
                eventType,
                activeAgentId,
                status,
                inputSummary,
                outputSummary,
                durationMs,
                errorSummary,
                observation);
            return true;
        }
        catch (Exception exception)
        {
            statusMessage = $"FunctionalMLDS V2 Logging blockiert {actionKind}: {exception.Message}";
            chatLog.Add(statusMessage);
            return false;
        }
    }

    private FunctionalMldsV2InteractionObservation CreateInteractionObservation(
        string interactionMode,
        ChatResponse response,
        bool responseObserved)
    {
        var deictic = string.Equals(
            interactionMode,
            FunctionalMldsV2InteractionEvidenceEvaluator.DeicticMode,
            StringComparison.Ordinal);
        var groundedIds = new List<string>();
        if (response != null)
        {
            if (response.grounded_entity_ids != null)
                groundedIds.AddRange(response.grounded_entity_ids);
            if (response.grounding != null && response.grounding.grounded_entity_ids != null)
                groundedIds.AddRange(response.grounding.grounded_entity_ids);
        }
        var hasHandoff = response != null
            && response.handoff != null
            && !string.IsNullOrWhiteSpace(response.handoff.to);
        return new FunctionalMldsV2InteractionObservation
        {
            InteractionMode = interactionMode,
            ModelSha256 = currentModelSha256,
            BindingRegistryValid = deictic ? (bool?)spatialBindingRegistry.IsValid : null,
            SelectionObserved = deictic && selectedSpatialTarget != null,
            SelectionState = deictic ? spatialSelectionState : FunctionalMldsSpatialTargetStates.None,
            SelectedEntityId = deictic && selectedSpatialTarget != null
                ? selectedSpatialTarget.EntityId
                : null,
            SelectedSourceObjectId = deictic && selectedSpatialTarget != null
                ? selectedSpatialTarget.SourceObjectId
                : null,
            SelectedObjectGroupIds = deictic
                && selectedSpatialTarget != null
                && !string.IsNullOrWhiteSpace(selectedSpatialTarget.ObjectGroupId)
                    ? new List<string> { selectedSpatialTarget.ObjectGroupId }
                    : new List<string>(),
            SelectedZoneIds = deictic
                && selectedSpatialTarget != null
                && !string.IsNullOrWhiteSpace(selectedSpatialTarget.ZoneId)
                    ? new List<string> { selectedSpatialTarget.ZoneId }
                    : new List<string>(),
            RequestedAgentId = activeAgentId,
            RoutedAgentId = response?.routing?.selected_agent_id ?? response?.active_agent_id,
            ResponseObserved = responseObserved,
            ResponseSelectedEntityId = response?.grounding?.selected_entity_id,
            ResponseGroundedEntityIds = new List<string>(UniqueSorted(groundedIds)),
            HandoffObserved = hasHandoff,
            HandoffFromAgentId = hasHandoff ? response.handoff.from : null,
            HandoffToAgentId = hasHandoff ? response.handoff.to : null,
            ModeledHandoff = hasHandoff ? response.routing?.modeled_handoff : null,
            CapabilityUseId = response?.model_binding?.capability_use_id,
            CapabilityId = response?.model_binding?.capability_id,
            RuntimeBindingId = response?.model_binding?.runtime_binding_id,
            RuntimeActionId = response?.model_binding?.runtime_action_id
        };
    }

    private bool TryRecordFunctionalMldsV2Interaction(
        string actionKind,
        string eventType,
        FunctionalMldsV2InteractionObservation observation,
        object inputSummary,
        object outputSummary,
        double? durationMs,
        bool requireCompletion,
        out FunctionalMldsV2InteractionAssessment assessment)
    {
        assessment = null;
        if (functionalMldsV2Bridge == null)
            return true;
        try
        {
            assessment = functionalMldsV2Bridge.RecordInteraction(
                actionKind,
                eventType,
                activeAgentId,
                observation,
                inputSummary,
                outputSummary,
                durationMs);
            interactionEvidenceStatus =
                $"FunctionalMLDS-Evidenz: {assessment.Verdict} "
                + $"| Ziel: {(assessment.TargetResolved ? "ok" : "offen")} "
                + $"| Route: {(assessment.RouteResolved ? "ok" : "offen")} "
                + $"| Abschluss: {(assessment.CompletionSatisfied ? "ja" : "nein")}";
            var handler = InteractionEvidenceLogged;
            if (handler != null)
                handler(assessment);

            if (string.Equals(assessment.Verdict, "fail", StringComparison.Ordinal)
                || string.Equals(assessment.Verdict, "error", StringComparison.Ordinal)
                || (requireCompletion && !assessment.CompletionSatisfied))
            {
                statusMessage = $"FunctionalMLDS V2 blockiert {actionKind}: "
                    + interactionEvidenceStatus;
                chatLog.Add(statusMessage);
                return false;
            }
            return true;
        }
        catch (Exception exception)
        {
            interactionEvidenceStatus = $"FunctionalMLDS-Evidenzfehler: {exception.Message}";
            statusMessage = $"FunctionalMLDS V2 Logging blockiert {actionKind}: {exception.Message}";
            chatLog.Add(statusMessage);
            return false;
        }
    }

    private void AppendChatEvents(ChatEvent[] events)
    {
        if (events == null)
        {
            return;
        }

        foreach (var ev in events)
        {
            var agentLabel = string.IsNullOrWhiteSpace(ev.agent_id) ? "System" : ev.agent_id;
            if (!string.IsNullOrWhiteSpace(ev.type))
            {
                agentLabel = $"{agentLabel}/{ev.type}";
            }

            var text = NormalizeChatText(ev.text);
            AddChatLine($"[{agentLabel}] {text}", ev.agent_id);
        }
    }

    private bool IsPrivateMemoryMode()
    {
        return string.Equals(memoryMode, "agent_private_history", StringComparison.Ordinal);
    }

    private void AddChatLine(string line, string agentId = null)
    {
        if (string.IsNullOrWhiteSpace(line))
            return;

        chatLog.Add(line);
        if (string.IsNullOrWhiteSpace(agentId))
            return;

        if (!agentChatLogs.TryGetValue(agentId, out var agentLog))
        {
            agentLog = new List<string>();
            agentChatLogs[agentId] = agentLog;
        }
        agentLog.Add(line);
    }

    private void AddUserChatLine(string text, bool voice = false)
    {
        var clean = NormalizeChatText(text);
        if (string.IsNullOrWhiteSpace(clean))
            return;

        AddChatLine(voice ? $"[Du/Voice] {clean}" : $"[Du] {clean}", activeAgentId);
    }

    private void ClearChatLogs()
    {
        chatLog.Clear();
        agentChatLogs.Clear();
    }

    private List<string> GetRecentFpvChatLines(int maxLines)
    {
        var source = chatLog;
        if (IsPrivateMemoryMode())
        {
            var agentId = !string.IsNullOrEmpty(_fpvNearestAgentId) ? _fpvNearestAgentId : activeAgentId;
            if (string.IsNullOrEmpty(agentId) || !agentChatLogs.TryGetValue(agentId, out source))
            {
                return new List<string>();
            }
        }

        var recent = new List<string>();
        for (var i = source.Count - 1; i >= 0 && recent.Count < maxLines; i--)
            recent.Insert(0, source[i]);
        return recent;
    }

    private string NormalizeChatText(string text)
    {
        if (string.IsNullOrEmpty(text))
        {
            return "";
        }

        var normalized = text.Replace("\\n", "\n").Trim();
        if (normalized.StartsWith("{") && normalized.EndsWith("}"))
        {
            var extracted = TryExtractSayFromJson(normalized);
            if (!string.IsNullOrWhiteSpace(extracted))
            {
                return extracted.Trim();
            }

            extracted = TryExtractSayFromLooseJson(normalized);
            if (!string.IsNullOrWhiteSpace(extracted))
            {
                return extracted.Trim();
            }
        }

        var jsonStart = normalized.IndexOf('{');
        var jsonEnd = normalized.LastIndexOf('}');
        if (jsonStart >= 0 && jsonEnd > jsonStart)
        {
            var jsonCandidate = normalized.Substring(jsonStart, jsonEnd - jsonStart + 1);
            var extracted = TryExtractSayFromJson(jsonCandidate);
            if (!string.IsNullOrWhiteSpace(extracted))
            {
                return extracted.Trim();
            }

            extracted = TryExtractSayFromLooseJson(jsonCandidate);
            if (!string.IsNullOrWhiteSpace(extracted))
            {
                return extracted.Trim();
            }
        }

        return normalized;
    }

    private string TryExtractSayFromJson(string json)
    {
        try
        {
            var parsed = JsonUtility.FromJson<StructuredNpcReply>(json);
            if (parsed != null && !string.IsNullOrWhiteSpace(parsed.say))
            {
                return parsed.say;
            }
            if (parsed != null)
            {
                var parts = new List<string>();
                if (!string.IsNullOrWhiteSpace(parsed.antwort))
                {
                    parts.Add(parsed.antwort.Trim());
                }
                if (!string.IsNullOrWhiteSpace(parsed.rueckfrage))
                {
                    var followUp = parsed.rueckfrage.Trim();
                    if (!string.IsNullOrWhiteSpace(followUp))
                    {
                        parts.Add($"Rückfrage: {followUp}");
                    }
                }
                if (parts.Count > 0)
                {
                    return string.Join("\n\n", parts);
                }
            }
        }
        catch
        {
            // Ignore JSON parse failures and fall back to raw text.
        }

        return null;
    }

    private string TryExtractSayFromLooseJson(string jsonLike)
    {
        if (string.IsNullOrWhiteSpace(jsonLike))
        {
            return null;
        }

        var antwort = ExtractLooseField(jsonLike, "antwort");
        var rueckfrage = ExtractLooseField(jsonLike, "rueckfrage");
        if (string.IsNullOrWhiteSpace(antwort) && string.IsNullOrWhiteSpace(rueckfrage))
        {
            return null;
        }

        var parts = new List<string>();
        if (!string.IsNullOrWhiteSpace(antwort))
        {
            parts.Add(antwort.Trim());
        }

        if (!string.IsNullOrWhiteSpace(rueckfrage))
        {
            parts.Add($"Rückfrage: {rueckfrage.Trim()}");
        }

        return string.Join("\n\n", parts);
    }

    private string ExtractLooseField(string jsonLike, string field)
    {
        var pattern = $"\\\"{Regex.Escape(field)}\\\"\\s*:\\s*\\\"(?<value>[\\s\\S]*?)\\\"";
        var match = Regex.Match(jsonLike, pattern, RegexOptions.Singleline);
        if (!match.Success)
        {
            return null;
        }

        var value = match.Groups["value"].Value;
        return value.Replace("\\n", "\n").Replace("\\r", "\r").Replace("\\t", "\t").Replace("\\\"", "\"");
    }

    private void OnGUI()
    {
        DrawAgentBubbles();

        if (_fpvActive)
        {
            DrawFpvHud();
            isChatInputFocused = _fpvChatOpen;
            return;
        }

        if (!showUi)
        {
            isChatInputFocused = false;
            return;
        }

        var maxWidth = Mathf.Min(uiRect.width, Screen.width - uiRect.x - 10f);
        var maxHeight = Mathf.Min(uiRect.height, Screen.height - uiRect.y - 10f);
        var clampedRect = new Rect(uiRect.x, uiRect.y, maxWidth, maxHeight);

        if (Event.current.type == EventType.MouseDown && !clampedRect.Contains(Event.current.mousePosition))
        {
            GUI.FocusControl(string.Empty);
            isChatInputFocused = false;
        }

        GUILayout.BeginArea(clampedRect, GUI.skin.box);
        uiScroll = GUILayout.BeginScrollView(uiScroll);
        GUILayout.Label("Quick Agent Manager");
        GUILayout.Space(4);

        GUILayout.Label($"Status: {statusMessage}");
        GUILayout.Label($"Session: {sessionId}");
        GUILayout.Label($"Aktiv: {activeAgentId}");
        GUILayout.Label("Raumziel: " + GetSpatialTargetLabel());
        if (functionalMldsV2Bridge != null)
            GUILayout.Label(interactionEvidenceStatus);
        if (spatialSelectionState != FunctionalMldsSpatialTargetStates.None
            && GUILayout.Button("Raumziel aufheben"))
        {
            ClearSelectedSpatialTarget();
        }

        GUILayout.Space(6);
        GUILayout.Label("Gedaechtnis:");
        var memoryIndex = memoryMode == "agent_private_history" ? 1 : 0;
        memoryIndex = GUILayout.Toolbar(memoryIndex, new[] { "Gemeinsam", "Privat" });
        memoryMode = memoryIndex == 0 ? "shared_history" : "agent_private_history";

        GUILayout.Space(6);
        GUILayout.Label("Projekt auswählen:");
        var sourceIndex = useProjectSelection ? 0 : 1;
        sourceIndex = GUILayout.Toolbar(sourceIndex, new[] { "Projekt", "Pfade" });
        useProjectSelection = sourceIndex == 0;

        if (useProjectSelection)
        {
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Projektliste laden"))
            {
                StartCoroutine(RefreshProjects());
            }
            GUILayout.EndHorizontal();

            if (projects.Length == 0)
            {
                GUILayout.Label("Keine Projekte geladen.");
            }
            else
            {
                projectScroll = GUILayout.BeginScrollView(projectScroll, GUILayout.Height(140f));
                for (var i = 0; i < projects.Length; i++)
                {
                    var project = projects[i];
                    var label = $"{project.display_name} ({project.id})";
                    var isSelected = i == selectedProjectIndex;
                    var previousColor = GUI.backgroundColor;
                    if (isSelected)
                    {
                        GUI.backgroundColor = new Color(0.35f, 0.7f, 1f, 1f);
                    }

                    if (GUILayout.Button(label))
                    {
                        selectedProjectIndex = i;
                        selectedProjectId = project.id;
                    }

                    GUI.backgroundColor = previousColor;
                }
                GUILayout.EndScrollView();

                if (selectedProjectIndex >= 0)
                {
                    var selected = projects[selectedProjectIndex];
                    GUILayout.Label($"Aktuelles Projekt: {selected.display_name} ({selected.id})");
                }
            }
        }
        else
        {
            GUILayout.Label("Room-Plan Pfad:");
            roomPlanPath = GUILayout.TextField(roomPlanPath);
            GUILayout.Label("Agenten Pfad:");
            agentsPath = GUILayout.TextField(agentsPath);
        }

        if (GUILayout.Button("Setup erneut vom Server"))
        {
            StartCoroutine(SetupFromServer());
        }

        GUILayout.Space(6);
        GUILayout.Label("Agenten wählen:");
        agentScroll = GUILayout.BeginScrollView(agentScroll, GUILayout.Height(120));
        if (lastAgents != null)
        {
            foreach (var agent in lastAgents)
            {
                var id = string.IsNullOrEmpty(agent.id) ? "(unbekannt)" : agent.id;
                var label = string.IsNullOrEmpty(agent.display_name) ? id : $"{agent.display_name} ({id})";
                if (GUILayout.Button(label))
                {
                    SetActiveAgentId(id, true);
                }
            }
        }
        GUILayout.EndScrollView();

        GUILayout.Space(6);
        GUILayout.Label("Chat:");
        GUI.SetNextControlName(ChatInputControlName);
        chatInput = GUILayout.TextField(chatInput);
        isChatInputFocused = GUI.GetNameOfFocusedControl() == ChatInputControlName;
        if (Event.current.type == EventType.KeyDown
            && (Event.current.keyCode == KeyCode.Return
                || Event.current.keyCode == KeyCode.KeypadEnter
                || Event.current.character == '\n'
                || Event.current.character == '\r')
            && GUI.GetNameOfFocusedControl() == ChatInputControlName)
        {
            TrySendChatFromInput();
            Event.current.Use();
        }
        if (GUILayout.Button("Senden"))
        {
            TrySendChatFromInput();
        }
        if (enableVoiceInput)
        {
            GUILayout.BeginHorizontal();
            if (isVoiceRecording)
            {
                if (GUILayout.Button("Aufnahme stoppen + senden"))
                {
                    StopVoiceRecordingAndSend();
                }
                GUILayout.Label("Aufnahme laeuft...");
            }
            else
            {
                if (GUILayout.Button("Voice aufnehmen"))
                {
                    StartVoiceRecording();
                }
                GUILayout.Label(sttInFlight ? "Transkription laeuft..." : $"{voiceRecordKey} halten = sprechen");
            }
            GUILayout.EndHorizontal();
        }
        if (GUILayout.Button("Chat leeren"))
        {
            ClearChatLogs();
        }

        chatScroll = GUILayout.BeginScrollView(chatScroll, GUILayout.Height(160));
        var chatText = string.Join("\n", chatLog);
        GUILayout.TextArea(chatText, GUILayout.ExpandHeight(true));
        GUILayout.EndScrollView();

        GUILayout.Space(6);
        GUILayout.Label("Interaktion: Linksklick wählt Agent oder semantisches Raumobjekt.");
        GUILayout.Label("Freie Kamera: WASD + QE, rechte Maustaste zum Umschauen.");
        GUILayout.Space(6);
        GUILayout.Label($"FPV Maussensitivitaet: {fpvMouseSensitivity:0.00}");
        fpvMouseSensitivity = GUILayout.HorizontalSlider(fpvMouseSensitivity, 0.2f, 6f);
        GUILayout.EndScrollView();
        GUILayout.EndArea();
    }

    private void SetActiveAgentId(string id, bool updateStatus = false)
    {
        if (string.IsNullOrEmpty(id))
        {
            return;
        }

        activeAgentId = id;
        if (updateStatus)
        {
            statusMessage = $"Aktiver Agent: {activeAgentId}";
        }
        UpdateAgentHighlights();
    }

    private void UpdateAgentHighlights()
    {
        foreach (var pair in agentObjects)
        {
            var visual = pair.Value;
            if (visual == null || visual.renderer == null)
            {
                continue;
            }

            var isActive = pair.Key == activeAgentId;
            var color = isActive ? activeAgentColor : visual.baseColor;
            visual.renderer.material.color = color;
            if (visual.renderer.material.HasProperty("_EmissionColor"))
            {
                if (isActive)
                {
                    visual.renderer.material.EnableKeyword("_EMISSION");
                    visual.renderer.material.SetColor("_EmissionColor", color * activeAgentEmission);
                }
                else
                {
                    visual.renderer.material.SetColor("_EmissionColor", Color.black);
                }
            }
        }
    }

    private IEnumerator ShowChatBubbles(ChatResponse resp)
    {
        if (resp == null)
        {
            yield break;
        }

        if (resp.handoff != null
            && !string.IsNullOrWhiteSpace(resp.handoff.from)
            && !string.IsNullOrWhiteSpace(resp.handoff.to))
        {
            var handoffText = $"Leitet weiter an {resp.handoff.to}";
            if (!string.IsNullOrWhiteSpace(resp.handoff.reason))
            {
                handoffText = $"{handoffText}\n{resp.handoff.reason}";
            }

            SetBubble(resp.handoff.from, handoffText, handoffIndicatorDuration);
            ShowHandoffLine(ResolveAgentId(resp.handoff.from), ResolveAgentId(resp.handoff.to),
                handoffIndicatorDuration + handoffDelay);
            yield return new WaitForSeconds(handoffIndicatorDuration + handoffDelay);
            ClearBubble(resp.handoff.from);
        }

        if (resp.events == null)
        {
            yield break;
        }

        foreach (var ev in resp.events)
        {
            if (string.IsNullOrWhiteSpace(ev.agent_id))
            {
                continue;
            }

            var text = NormalizeChatText(ev.text);
            if (string.IsNullOrWhiteSpace(text))
            {
                continue;
            }

            SetBubble(ev.agent_id, text, bubbleDuration);
            StartCoroutine(PlayAgentSpeech(ev.agent_id, text));
            yield return new WaitForSeconds(bubbleStagger);
        }
    }

    private IEnumerator ShowHandoffOnly(ChatResponse resp, ChatEvent[] fromEvents)
    {
        if (resp.handoff == null) yield break;

        // Show forwarding agent's own speech immediately
        foreach (var ev in fromEvents)
        {
            var text = NormalizeChatText(ev.text);
            if (string.IsNullOrWhiteSpace(text)) continue;
            SetBubble(ev.agent_id, text, bubbleDuration);
            StartCoroutine(PlayAgentSpeech(ev.agent_id, text));
            yield return new WaitForSeconds(bubbleStagger);
        }

        // Then show the forwarding indicator
        var handoffText = $"Leitet weiter an {resp.handoff.to}";
        if (!string.IsNullOrWhiteSpace(resp.handoff.reason))
            handoffText = $"{handoffText}\n{resp.handoff.reason}";
        SetBubble(resp.handoff.from, handoffText, handoffIndicatorDuration);
        yield return new WaitForSeconds(handoffIndicatorDuration + handoffDelay);
        ClearBubble(resp.handoff.from);
    }

    private static ChatEvent[] FilterEvents(ChatEvent[] events, string agentId, bool include)
    {
        if (events == null) return Array.Empty<ChatEvent>();
        var result = new List<ChatEvent>();
        foreach (var e in events)
            if (include ? e.agent_id == agentId : e.agent_id != agentId)
                result.Add(e);
        return result.ToArray();
    }

    private void TriggerPendingHandoffArrival()
    {
        var agentId = _pendingHandoffAgentId;
        var events  = _pendingHandoffEvents;

        ClearPendingHandoff();
        SetActiveAgentId(agentId);
        if (events != null && events.Length > 0)
        {
            AppendChatEvents(events);
            StartCoroutine(ShowChatBubbles(new ChatResponse
            {
                session_id      = sessionId,
                active_agent_id = agentId,
                events          = events
            }));
        }
    }

    private void ShowPendingHandoffRoute(ChatResponse resp)
    {
        if (resp == null || resp.handoff == null || string.IsNullOrEmpty(_pendingHandoffAgentId))
        {
            return;
        }

        var fromId = ResolveAgentId(resp.handoff.from);
        if (string.IsNullOrEmpty(fromId) || !agentObjects.ContainsKey(fromId))
        {
            fromId = activeAgentId;
        }

        ShowHandoffLine(fromId, _pendingHandoffAgentId, 0f, persistUntilArrival: true);
    }

    private void SetPendingHandoff(ChatResponse resp, ChatEvent[] targetEvents)
    {
        var targetAgentId = ResolvePendingHandoffTargetId(resp);
        if (string.IsNullOrEmpty(targetAgentId) || !agentObjects.ContainsKey(targetAgentId))
        {
            ClearPendingHandoff();
            statusMessage = "Weiterleitungsziel nicht gefunden.";
            return;
        }

        if (!string.Equals(_pendingHandoffAgentId, targetAgentId, StringComparison.Ordinal))
            ClearPendingHandoff();

        _pendingHandoffAgentId = targetAgentId;
        _pendingHandoffEvents = targetEvents;
        statusMessage = $"Weiterleitung zu: {GetAgentDisplayName(targetAgentId)}";
    }

    private string ResolvePendingHandoffTargetId(ChatResponse resp)
    {
        if (resp == null)
            return "";

        var fromId = ResolveAgentId(resp.handoff?.from);
        var handoffTarget = ResolveAgentId(resp.handoff?.to);
        if (!string.IsNullOrEmpty(handoffTarget) && agentObjects.ContainsKey(handoffTarget))
            return handoffTarget;

        var activeTarget = ResolveAgentId(resp.active_agent_id);
        if (!string.IsNullOrEmpty(activeTarget)
            && agentObjects.ContainsKey(activeTarget)
            && !string.Equals(activeTarget, fromId, StringComparison.Ordinal))
        {
            return activeTarget;
        }

        return "";
    }

    private string ResolveAgentId(string agentRef)
    {
        if (string.IsNullOrWhiteSpace(agentRef))
            return "";

        var trimmed = agentRef.Trim();
        if (agentObjects.ContainsKey(trimmed))
            return trimmed;

        if (lastAgents != null)
        {
            foreach (var agent in lastAgents)
            {
                if (agent == null)
                    continue;

                if (string.Equals(agent.id, trimmed, StringComparison.Ordinal)
                    || string.Equals(agent.display_name, trimmed, StringComparison.OrdinalIgnoreCase))
                {
                    return agent.id;
                }
            }
        }

        return trimmed;
    }

    private string GetAgentDisplayName(string agentId)
    {
        if (lastAgents != null)
        {
            foreach (var agent in lastAgents)
            {
                if (agent != null && string.Equals(agent.id, agentId, StringComparison.Ordinal))
                    return string.IsNullOrEmpty(agent.display_name) ? agent.id : agent.display_name;
            }
        }

        return agentId;
    }

    private void ClearPendingHandoff()
    {
        if (string.IsNullOrEmpty(_pendingHandoffAgentId) && _pendingHandoffEvents == null)
            return;

        _pendingHandoffAgentId = "";
        _pendingHandoffEvents = null;
        SetHandoffRouteVisible(false);
        UpdateAgentHighlights();
    }

    private void SetBubble(string agentId, string text, float duration)
    {
        if (string.IsNullOrWhiteSpace(agentId))
        {
            return;
        }

        showAgentBubbles = true;
        agentBubbles[agentId] = new BubbleInfo
        {
            text = text,
            expiresAt = Time.time + duration
        };
    }

    private void ClearBubble(string agentId)
    {
        if (string.IsNullOrWhiteSpace(agentId))
        {
            return;
        }

        agentBubbles.Remove(agentId);
    }

    private void CleanupExpiredBubbles()
    {
        if (agentBubbles.Count == 0)
        {
            return;
        }

        var now = Time.time;
        var toRemove = new List<string>();
        foreach (var pair in agentBubbles)
        {
            if (pair.Value == null || pair.Value.expiresAt <= now)
            {
                toRemove.Add(pair.Key);
            }
        }

        for (var i = 0; i < toRemove.Count; i++)
        {
            agentBubbles.Remove(toRemove[i]);
        }
    }

    private void DrawAgentBubbles()
    {
        if (!showAgentBubbles)
        {
            return;
        }

        if (agentBubbles.Count == 0)
        {
            return;
        }

        var cam = Camera.main;
        if (cam == null)
        {
            return;
        }

        EnsureBubbleStyles();

        foreach (var pair in agentBubbles)
        {
            if (!agentObjects.TryGetValue(pair.Key, out var visual) || visual == null || visual.obj == null)
            {
                continue;
            }

            var content = pair.Value != null ? pair.Value.text : "";
            if (string.IsNullOrWhiteSpace(content))
            {
                continue;
            }

            var worldPos = visual.obj.transform.position + Vector3.up * (bubbleHeight + visual.scale * 0.5f);
            var screenPos = cam.WorldToScreenPoint(worldPos);
            if (screenPos.z <= 0f)
            {
                continue;
            }

            var maxWidth = 220f;
            var height = bubbleStyle.CalcHeight(new GUIContent(content), maxWidth);
            var rect = new Rect(
                screenPos.x - maxWidth * 0.5f,
                Screen.height - screenPos.y - height - 16f,
                maxWidth,
                height
            );

            GUI.Box(rect, content, bubbleStyle);
            var pointerRect = new Rect(rect.x, rect.yMax - 4f, rect.width, 16f);
            GUI.Label(pointerRect, "▼", bubblePointerStyle);
        }
    }

    private void EnsureBubbleStyles()
    {
        if (bubbleStyle != null)
        {
            return;
        }

        bubbleStyle = new GUIStyle(GUI.skin.box)
        {
            alignment = TextAnchor.MiddleCenter,
            wordWrap = true,
            fontSize = 12
        };
        bubbleStyle.padding = new RectOffset(8, 8, 6, 6);

        bubblePointerStyle = new GUIStyle(GUI.skin.label)
        {
            alignment = TextAnchor.UpperCenter,
            fontSize = 14,
            fontStyle = FontStyle.Bold
        };
    }

    private void ShowHandoffLine(string fromId, string toId, float duration, bool persistUntilArrival = false)
    {
        if (string.IsNullOrWhiteSpace(fromId) || string.IsNullOrWhiteSpace(toId))
        {
            return;
        }

        EnsureHandoffRouteRoot();
        handoffFromId = fromId;
        handoffToId = toId;
        handoffRouteRoot.SetActive(true);
        handoffRouteCachedPoints.Clear();
        handoffRoutePersistUntilArrival = persistUntilArrival;
        handoffLineExpiresAt = Time.time + duration;
        UpdateHandoffLinePositions(true);
    }

    private void UpdateHandoffLine()
    {
        if (handoffRouteRoot == null || !handoffRouteRoot.activeSelf)
        {
            return;
        }

        if (!handoffRoutePersistUntilArrival && Time.time > handoffLineExpiresAt)
        {
            SetHandoffRouteVisible(false);
            return;
        }

        UpdateHandoffLinePositions();
    }

    private void UpdateHandoffLinePositions(bool forceRebuild = false)
    {
        if (handoffRouteRoot == null)
        {
            return;
        }

        if (!agentObjects.TryGetValue(handoffFromId, out var fromVisual)
            || !agentObjects.TryGetValue(handoffToId, out var toVisual)
            || fromVisual == null
            || toVisual == null
            || fromVisual.obj == null
            || toVisual.obj == null)
        {
            SetHandoffRouteVisible(false);
            return;
        }

        var routeStartsAtViewer = ShouldHandoffRouteStartAtViewer();
        var fromPos = routeStartsAtViewer ? GetHandoffRouteViewerGroundPoint(fromVisual) : GetHandoffRouteGroundPoint(fromVisual);
        var toPos = GetHandoffRouteGroundPoint(toVisual);
        var flatDirection = new Vector3(toPos.x - fromPos.x, 0f, toPos.z - fromPos.z);
        if (flatDirection.sqrMagnitude > 0.001f)
        {
            var direction = flatDirection.normalized;
            if (!routeStartsAtViewer)
            {
                fromPos += direction * Mathf.Max(0.25f, fromVisual.scale * 0.18f);
            }
            toPos -= direction * Mathf.Max(0.25f, toVisual.scale * 0.18f);
        }

        if (!forceRebuild && routeStartsAtViewer && TryRenderStableViewerHandoffRoute(fromPos, toPos))
        {
            return;
        }

        if (!forceRebuild
            && handoffRouteCachedPoints.Count > 1
            && (handoffRouteLastFrom - fromPos).sqrMagnitude < HandoffRouteRebuildDistance * HandoffRouteRebuildDistance
            && (handoffRouteLastTo - toPos).sqrMagnitude < HandoffRouteRebuildDistance * HandoffRouteRebuildDistance)
        {
            RenderHandoffRoute(handoffRouteCachedPoints);
            return;
        }

        var route = BuildHandoffRoute(fromPos, toPos);
        handoffRouteCachedPoints.Clear();
        handoffRouteCachedPoints.AddRange(route);
        handoffRouteLastFrom = fromPos;
        handoffRouteLastTo = toPos;
        RenderHandoffRoute(handoffRouteCachedPoints);
    }

    private Vector3 GetHandoffRouteGroundPoint(AgentVisual visual)
    {
        var pos = visual.obj.transform.position;
        var y = fallbackGroundY + Mathf.Max(0.005f, handoffRouteGroundOffset);
        return new Vector3(pos.x, y, pos.z);
    }

    private bool ShouldHandoffRouteStartAtViewer()
    {
        return _fpvActive
               && handoffRoutePersistUntilArrival
               && !string.IsNullOrEmpty(_pendingHandoffAgentId)
               && string.Equals(handoffToId, _pendingHandoffAgentId, StringComparison.Ordinal);
    }

    private Vector3 GetHandoffRouteViewerGroundPoint(AgentVisual fallbackVisual)
    {
        var cam = Camera.main;
        if (cam == null)
        {
            return GetHandoffRouteGroundPoint(fallbackVisual);
        }

        var pos = cam.transform.position;
        var y = fallbackGroundY + Mathf.Max(0.005f, handoffRouteGroundOffset);
        return new Vector3(pos.x, y, pos.z);
    }

    private bool TryRenderStableViewerHandoffRoute(Vector3 viewerPos, Vector3 targetPos)
    {
        if (handoffRouteCachedPoints.Count < 2)
        {
            return false;
        }

        var targetTolerance = Mathf.Max(0.25f, HandoffRouteRebuildDistance * 2f);
        if ((handoffRouteLastTo - targetPos).sqrMagnitude > targetTolerance * targetTolerance)
        {
            return false;
        }

        var cumulative = BuildHandoffRouteCumulativeDistances(handoffRouteCachedPoints);
        var totalLength = cumulative[cumulative.Length - 1];
        if (totalLength < 0.05f)
        {
            return false;
        }

        float routeDistance;
        float distanceToRouteSqr;
        if (!TryFindClosestDistanceOnHandoffRoute(
                handoffRouteCachedPoints,
                cumulative,
                viewerPos,
                out routeDistance,
                out distanceToRouteSqr))
        {
            return false;
        }

        var repathDistance = Mathf.Max(0.4f, handoffRouteRepathDistance);
        if (distanceToRouteSqr > repathDistance * repathDistance)
        {
            return false;
        }

        if (routeDistance >= totalLength - 0.1f)
        {
            return false;
        }

        handoffRouteRenderPoints.Clear();
        AddRoutePointIfDistinct(handoffRouteRenderPoints, viewerPos);
        AddRoutePointIfDistinct(
            handoffRouteRenderPoints,
            GetHandoffRoutePointAtDistance(handoffRouteCachedPoints, cumulative, routeDistance));

        for (var i = 1; i < handoffRouteCachedPoints.Count - 1; i++)
        {
            if (cumulative[i] > routeDistance)
            {
                AddRoutePointIfDistinct(handoffRouteRenderPoints, handoffRouteCachedPoints[i]);
            }
        }

        AddRoutePointIfDistinct(handoffRouteRenderPoints, handoffRouteCachedPoints[handoffRouteCachedPoints.Count - 1]);
        RenderHandoffRoute(handoffRouteRenderPoints);
        return true;
    }

    private static float[] BuildHandoffRouteCumulativeDistances(List<Vector3> route)
    {
        var cumulative = new float[route.Count];
        for (var i = 1; i < route.Count; i++)
        {
            cumulative[i] = cumulative[i - 1] + Vector3.Distance(route[i - 1], route[i]);
        }

        return cumulative;
    }

    private static bool TryFindClosestDistanceOnHandoffRoute(
        List<Vector3> route,
        float[] cumulative,
        Vector3 point,
        out float routeDistance,
        out float distanceToRouteSqr)
    {
        routeDistance = 0f;
        distanceToRouteSqr = float.PositiveInfinity;
        if (route == null || route.Count < 2)
        {
            return false;
        }

        var point2D = new Vector2(point.x, point.z);
        for (var i = 1; i < route.Count; i++)
        {
            var a = new Vector2(route[i - 1].x, route[i - 1].z);
            var b = new Vector2(route[i].x, route[i].z);
            var segment = b - a;
            var segmentLengthSqr = segment.sqrMagnitude;
            if (segmentLengthSqr < 0.0001f)
            {
                continue;
            }

            var t = Mathf.Clamp01(Vector2.Dot(point2D - a, segment) / segmentLengthSqr);
            var closest = a + segment * t;
            var sqr = (point2D - closest).sqrMagnitude;
            if (sqr < distanceToRouteSqr)
            {
                distanceToRouteSqr = sqr;
                routeDistance = cumulative[i - 1] + Mathf.Sqrt(segmentLengthSqr) * t;
            }
        }

        return !float.IsInfinity(distanceToRouteSqr);
    }

    private void EnsureHandoffRouteRoot()
    {
        if (handoffRouteRoot != null)
        {
            return;
        }

        handoffRouteRoot = new GameObject("HandoffGroundRoute");
        handoffRouteRoot.hideFlags = HideFlags.DontSave;
        handoffRouteMaterial = CreateHandoffRouteMaterial();
    }

    private Material CreateHandoffRouteMaterial()
    {
        var shader = Shader.Find("Sprites/Default");
        if (shader == null)
            shader = Shader.Find("Universal Render Pipeline/Unlit");
        if (shader == null)
            shader = Shader.Find("Unlit/Color");

        var material = shader != null ? new Material(shader) : new Material(Shader.Find("Standard"));
        material.name = "HandoffRoute_DashedGround";
        material.hideFlags = HideFlags.DontSave;
        material.renderQueue = 3000;
        return material;
    }

    private void SetHandoffRouteVisible(bool visible)
    {
        if (handoffRouteRoot != null)
        {
            handoffRouteRoot.SetActive(visible);
        }

        if (!visible)
        {
            handoffRouteCachedPoints.Clear();
            handoffRoutePersistUntilArrival = false;
            DisableHandoffRouteDashes(0);
        }
    }

    private List<Vector3> BuildHandoffRoute(Vector3 fromPos, Vector3 toPos)
    {
        var obstacles = CollectHandoffRouteObstacles(fromPos, toPos);
        List<Vector2> route2D = null;
        for (var attempt = 0; attempt < 3 && route2D == null; attempt++)
        {
            route2D = FindHandoffRoute2D(
                fromPos,
                toPos,
                obstacles,
                Mathf.Max(1f, handoffRouteSearchMargin) + attempt * 3f);
        }

        if (route2D == null)
        {
            route2D = FindHandoffVisibilityRoute2D(fromPos, toPos, obstacles);
        }

        var route = new List<Vector3>();

        if (route2D == null || route2D.Count < 2)
        {
            route.Add(fromPos);
            route.Add(toPos);
            return route;
        }

        for (var i = 0; i < route2D.Count; i++)
        {
            route.Add(new Vector3(route2D[i].x, fromPos.y, route2D[i].y));
        }

        return RoundHandoffRouteCorners(route);
    }

    private List<HandoffRouteObstacle> CollectHandoffRouteObstacles(Vector3 fromPos, Vector3 toPos)
    {
        var obstacles = new List<HandoffRouteObstacle>();
        var margin = Mathf.Max(1f, handoffRouteSearchMargin);
        var searchRect = CreateRouteRect(
            Mathf.Min(fromPos.x, toPos.x) - margin,
            Mathf.Min(fromPos.z, toPos.z) - margin,
            Mathf.Max(fromPos.x, toPos.x) + margin,
            Mathf.Max(fromPos.z, toPos.z) + margin);
        var padding = Mathf.Max(0.05f, handoffRouteObstaclePadding);

#if UNITY_2023_1_OR_NEWER
        var colliders = FindObjectsByType<Collider>(FindObjectsInactive.Exclude);
#else
        var colliders = FindObjectsOfType<Collider>();
#endif
        for (var i = 0; i < colliders.Length; i++)
        {
            var collider = colliders[i];
            if (!IsHandoffRouteColliderCandidate(collider))
            {
                continue;
            }

            AddHandoffRouteObstacleFromBounds(obstacles, collider.bounds, fromPos.y, padding, searchRect);
        }

#if UNITY_2023_1_OR_NEWER
        var renderers = FindObjectsByType<Renderer>(FindObjectsInactive.Exclude);
#else
        var renderers = FindObjectsOfType<Renderer>();
#endif
        for (var i = 0; i < renderers.Length; i++)
        {
            var renderer = renderers[i];
            if (!IsHandoffRouteRendererCandidate(renderer))
            {
                continue;
            }

            AddHandoffRouteObstacleFromBounds(obstacles, renderer.bounds, fromPos.y, padding, searchRect);
        }

        return obstacles;
    }

    private static void AddHandoffRouteObstacleFromBounds(
        List<HandoffRouteObstacle> obstacles,
        Bounds bounds,
        float groundY,
        float padding,
        Rect searchRect)
    {
        if (!ShouldTreatAsHandoffRouteObstacle(bounds, groundY))
        {
            return;
        }

        var obstacleRect = CreateRouteRect(
            bounds.min.x - padding,
            bounds.min.z - padding,
            bounds.max.x + padding,
            bounds.max.z + padding);

        if (obstacleRect.Overlaps(searchRect))
        {
            obstacles.Add(new HandoffRouteObstacle(obstacleRect));
        }
    }

    private bool IsHandoffRouteColliderCandidate(Collider collider)
    {
        if (collider == null || !collider.enabled || collider.isTrigger || !collider.gameObject.activeInHierarchy)
        {
            return false;
        }

        var transform = collider.transform;
        if (handoffRouteRoot != null && transform.IsChildOf(handoffRouteRoot.transform))
        {
            return false;
        }

        if (IsTransformPartOfAnyAgent(transform))
        {
            return false;
        }

        return !string.Equals(collider.gameObject.name, FallbackGroundName, StringComparison.OrdinalIgnoreCase);
    }

    private bool IsHandoffRouteRendererCandidate(Renderer renderer)
    {
        if (renderer == null || !renderer.enabled || !renderer.gameObject.activeInHierarchy)
        {
            return false;
        }

        if (renderer is LineRenderer)
        {
            return false;
        }

        var transform = renderer.transform;
        if (handoffRouteRoot != null && transform.IsChildOf(handoffRouteRoot.transform))
        {
            return false;
        }

        if (IsTransformPartOfAnyAgent(transform))
        {
            return false;
        }

        return !string.Equals(renderer.gameObject.name, "SelectionIndicator", StringComparison.OrdinalIgnoreCase);
    }

    private bool IsTransformPartOfAnyAgent(Transform candidate)
    {
        if (candidate == null)
        {
            return false;
        }

        foreach (var visual in agentObjects.Values)
        {
            if (visual?.obj != null && candidate.IsChildOf(visual.obj.transform))
            {
                return true;
            }
        }

        return false;
    }

    private static bool ShouldTreatAsHandoffRouteObstacle(Bounds bounds, float groundY)
    {
        if (bounds.size.x < 0.08f && bounds.size.z < 0.08f)
        {
            return false;
        }

        if (bounds.max.y < groundY + 0.12f)
        {
            return false;
        }

        if (bounds.min.y > groundY + 2.2f)
        {
            return false;
        }

        if (bounds.size.y < 0.08f && (bounds.size.x > 1.5f || bounds.size.z > 1.5f))
        {
            return false;
        }

        return bounds.size.x < 80f && bounds.size.z < 80f;
    }

    private static Rect CreateRouteRect(float minX, float minZ, float maxX, float maxZ)
    {
        return new Rect(
            minX,
            minZ,
            Mathf.Max(0.01f, maxX - minX),
            Mathf.Max(0.01f, maxZ - minZ));
    }

    private List<Vector2> FindHandoffRoute2D(
        Vector3 fromPos,
        Vector3 toPos,
        List<HandoffRouteObstacle> obstacles,
        float searchMargin)
    {
        var margin = Mathf.Max(1f, searchMargin);
        var minX = Mathf.Min(fromPos.x, toPos.x) - margin;
        var maxX = Mathf.Max(fromPos.x, toPos.x) + margin;
        var minZ = Mathf.Min(fromPos.z, toPos.z) - margin;
        var maxZ = Mathf.Max(fromPos.z, toPos.z) + margin;
        var cellSize = Mathf.Clamp(handoffRouteGridSize, 0.2f, 1.2f);
        var width = 0;
        var depth = 0;

        for (var i = 0; i < 8; i++)
        {
            width = Mathf.CeilToInt((maxX - minX) / cellSize) + 1;
            depth = Mathf.CeilToInt((maxZ - minZ) / cellSize) + 1;
            if (width * depth <= 14000)
            {
                break;
            }
            cellSize *= 1.25f;
        }

        if (width < 2 || depth < 2)
        {
            return null;
        }

        var total = width * depth;
        var blocked = new bool[total];
        for (var z = 0; z < depth; z++)
        {
            for (var x = 0; x < width; x++)
            {
                var point = GetHandoffRouteCellCenter(x, z, minX, minZ, cellSize);
                blocked[GetHandoffRouteIndex(x, z, width)] = IsHandoffRouteBlocked(point, obstacles);
            }
        }

        var start = new Vector2(fromPos.x, fromPos.z);
        var end = new Vector2(toPos.x, toPos.z);
        var startX = GetHandoffRouteCell(fromPos.x, minX, cellSize, width);
        var startZ = GetHandoffRouteCell(fromPos.z, minZ, cellSize, depth);
        var endX = GetHandoffRouteCell(toPos.x, minX, cellSize, width);
        var endZ = GetHandoffRouteCell(toPos.z, minZ, cellSize, depth);
        var startIndex = GetHandoffRouteIndex(startX, startZ, width);
        var endIndex = GetHandoffRouteIndex(endX, endZ, width);
        startIndex = FindNearestOpenHandoffRouteIndex(blocked, startX, startZ, width, depth);
        endIndex = FindNearestOpenHandoffRouteIndex(blocked, endX, endZ, width, depth);
        startX = startIndex % width;
        startZ = startIndex / width;
        endX = endIndex % width;
        endZ = endIndex / width;

        var cameFrom = new int[total];
        var gScore = new float[total];
        var fScore = new float[total];
        var closed = new bool[total];
        for (var i = 0; i < total; i++)
        {
            cameFrom[i] = -1;
            gScore[i] = float.PositiveInfinity;
            fScore[i] = float.PositiveInfinity;
        }

        var open = new List<int> { startIndex };
        gScore[startIndex] = 0f;
        fScore[startIndex] = GetHandoffRouteHeuristic(startX, startZ, endX, endZ, cellSize);

        while (open.Count > 0)
        {
            var current = PopBestHandoffRouteNode(open, fScore);
            if (current == endIndex)
            {
                var route = ReconstructHandoffRoute2D(cameFrom, current, startIndex, width, minX, minZ, cellSize);
                route[0] = start;
                route[route.Count - 1] = end;
                return SmoothHandoffRoute2D(route, obstacles);
            }

            closed[current] = true;
            var currentX = current % width;
            var currentZ = current / width;

            for (var dz = -1; dz <= 1; dz++)
            {
                for (var dx = -1; dx <= 1; dx++)
                {
                    if (dx == 0 && dz == 0)
                    {
                        continue;
                    }

                    var nx = currentX + dx;
                    var nz = currentZ + dz;
                    if (nx < 0 || nx >= width || nz < 0 || nz >= depth)
                    {
                        continue;
                    }

                    var neighbor = GetHandoffRouteIndex(nx, nz, width);
                    if (closed[neighbor] || blocked[neighbor])
                    {
                        continue;
                    }

                    if (dx != 0 && dz != 0)
                    {
                        var sideA = GetHandoffRouteIndex(currentX + dx, currentZ, width);
                        var sideB = GetHandoffRouteIndex(currentX, currentZ + dz, width);
                        if (blocked[sideA] || blocked[sideB])
                        {
                            continue;
                        }
                    }

                    var stepCost = (dx == 0 || dz == 0) ? cellSize : cellSize * 1.41421356f;
                    var tentative = gScore[current] + stepCost;
                    if (tentative >= gScore[neighbor])
                    {
                        continue;
                    }

                    cameFrom[neighbor] = current;
                    gScore[neighbor] = tentative;
                    fScore[neighbor] = tentative + GetHandoffRouteHeuristic(nx, nz, endX, endZ, cellSize);
                    if (!open.Contains(neighbor))
                    {
                        open.Add(neighbor);
                    }
                }
            }
        }

        return null;
    }

    private static int GetHandoffRouteCell(float value, float min, float cellSize, int count)
    {
        return Mathf.Clamp(Mathf.RoundToInt((value - min) / cellSize), 0, count - 1);
    }

    private static int GetHandoffRouteIndex(int x, int z, int width)
    {
        return z * width + x;
    }

    private static int FindNearestOpenHandoffRouteIndex(bool[] blocked, int startX, int startZ, int width, int depth)
    {
        var clampedX = Mathf.Clamp(startX, 0, width - 1);
        var clampedZ = Mathf.Clamp(startZ, 0, depth - 1);
        var startIndex = GetHandoffRouteIndex(clampedX, clampedZ, width);
        if (!blocked[startIndex])
        {
            return startIndex;
        }

        var maxRadius = Mathf.Max(width, depth);
        for (var radius = 1; radius < maxRadius; radius++)
        {
            for (var dz = -radius; dz <= radius; dz++)
            {
                for (var dx = -radius; dx <= radius; dx++)
                {
                    if (Mathf.Abs(dx) != radius && Mathf.Abs(dz) != radius)
                    {
                        continue;
                    }

                    var x = clampedX + dx;
                    var z = clampedZ + dz;
                    if (x < 0 || x >= width || z < 0 || z >= depth)
                    {
                        continue;
                    }

                    var index = GetHandoffRouteIndex(x, z, width);
                    if (!blocked[index])
                    {
                        return index;
                    }
                }
            }
        }

        blocked[startIndex] = false;
        return startIndex;
    }

    private static Vector2 GetHandoffRouteCellCenter(int x, int z, float minX, float minZ, float cellSize)
    {
        return new Vector2(minX + x * cellSize, minZ + z * cellSize);
    }

    private static float GetHandoffRouteHeuristic(int x, int z, int endX, int endZ, float cellSize)
    {
        var dx = (x - endX) * cellSize;
        var dz = (z - endZ) * cellSize;
        return Mathf.Sqrt(dx * dx + dz * dz);
    }

    private static int PopBestHandoffRouteNode(List<int> open, float[] fScore)
    {
        var bestOpenIndex = 0;
        var bestScore = fScore[open[0]];
        for (var i = 1; i < open.Count; i++)
        {
            var score = fScore[open[i]];
            if (score < bestScore)
            {
                bestScore = score;
                bestOpenIndex = i;
            }
        }

        var node = open[bestOpenIndex];
        open.RemoveAt(bestOpenIndex);
        return node;
    }

    private static List<Vector2> ReconstructHandoffRoute2D(
        int[] cameFrom,
        int current,
        int startIndex,
        int width,
        float minX,
        float minZ,
        float cellSize)
    {
        var route = new List<Vector2>();
        while (current >= 0)
        {
            var x = current % width;
            var z = current / width;
            route.Add(GetHandoffRouteCellCenter(x, z, minX, minZ, cellSize));
            if (current == startIndex)
            {
                break;
            }
            current = cameFrom[current];
        }

        route.Reverse();
        return route;
    }

    private static bool IsHandoffRouteBlocked(Vector2 point, List<HandoffRouteObstacle> obstacles)
    {
        for (var i = 0; i < obstacles.Count; i++)
        {
            if (obstacles[i].rect.Contains(point))
            {
                return true;
            }
        }

        return false;
    }

    private static List<Vector2> SmoothHandoffRoute2D(List<Vector2> route, List<HandoffRouteObstacle> obstacles)
    {
        if (route == null || route.Count < 3)
        {
            return route;
        }

        var smoothed = new List<Vector2> { route[0] };
        var current = 0;
        while (current < route.Count - 1)
        {
            var next = route.Count - 1;
            while (next > current + 1 && IsHandoffRouteSegmentBlocked(route[current], route[next], obstacles))
            {
                next--;
            }

            smoothed.Add(route[next]);
            current = next;
        }

        return smoothed;
    }

    private List<Vector2> FindHandoffVisibilityRoute2D(
        Vector3 fromPos,
        Vector3 toPos,
        List<HandoffRouteObstacle> obstacles)
    {
        var start = new Vector2(fromPos.x, fromPos.z);
        var end = new Vector2(toPos.x, toPos.z);
        if (!IsHandoffRouteSegmentBlocked(start, end, obstacles))
        {
            return new List<Vector2> { start, end };
        }

        var candidates = new List<Vector2> { start, end };
        var clearance = Mathf.Max(0.15f, handoffRouteGridSize * 0.75f);
        for (var i = 0; i < obstacles.Count; i++)
        {
            var rect = obstacles[i].rect;
            AddHandoffRouteCandidate(candidates, new Vector2(rect.xMin - clearance, rect.yMin - clearance), obstacles);
            AddHandoffRouteCandidate(candidates, new Vector2(rect.xMin - clearance, rect.yMax + clearance), obstacles);
            AddHandoffRouteCandidate(candidates, new Vector2(rect.xMax + clearance, rect.yMin - clearance), obstacles);
            AddHandoffRouteCandidate(candidates, new Vector2(rect.xMax + clearance, rect.yMax + clearance), obstacles);
        }

        var count = candidates.Count;
        var distances = new float[count];
        var previous = new int[count];
        var visited = new bool[count];
        for (var i = 0; i < count; i++)
        {
            distances[i] = float.PositiveInfinity;
            previous[i] = -1;
        }

        distances[0] = 0f;
        for (var step = 0; step < count; step++)
        {
            var current = -1;
            var bestDistance = float.PositiveInfinity;
            for (var i = 0; i < count; i++)
            {
                if (!visited[i] && distances[i] < bestDistance)
                {
                    current = i;
                    bestDistance = distances[i];
                }
            }

            if (current < 0 || current == 1)
            {
                break;
            }

            visited[current] = true;
            for (var neighbor = 0; neighbor < count; neighbor++)
            {
                if (neighbor == current || visited[neighbor])
                {
                    continue;
                }

                if (IsHandoffRouteSegmentBlocked(candidates[current], candidates[neighbor], obstacles))
                {
                    continue;
                }

                var tentative = distances[current] + Vector2.Distance(candidates[current], candidates[neighbor]);
                if (tentative < distances[neighbor])
                {
                    distances[neighbor] = tentative;
                    previous[neighbor] = current;
                }
            }
        }

        if (previous[1] < 0)
        {
            return null;
        }

        var route = new List<Vector2>();
        var node = 1;
        while (node >= 0)
        {
            route.Add(candidates[node]);
            node = previous[node];
        }
        route.Reverse();
        return SmoothHandoffRoute2D(route, obstacles);
    }

    private static void AddHandoffRouteCandidate(
        List<Vector2> candidates,
        Vector2 candidate,
        List<HandoffRouteObstacle> obstacles)
    {
        if (IsHandoffRouteBlocked(candidate, obstacles))
        {
            return;
        }

        for (var i = 0; i < candidates.Count; i++)
        {
            if ((candidates[i] - candidate).sqrMagnitude < 0.01f)
            {
                return;
            }
        }

        candidates.Add(candidate);
    }

    private static bool IsHandoffRouteSegmentBlocked(Vector2 a, Vector2 b, List<HandoffRouteObstacle> obstacles)
    {
        for (var i = 0; i < obstacles.Count; i++)
        {
            if (SegmentIntersectsRouteRect(a, b, obstacles[i].rect))
            {
                return true;
            }
        }

        return false;
    }

    private static bool SegmentIntersectsRouteRect(Vector2 a, Vector2 b, Rect rect)
    {
        if (rect.Contains(a) || rect.Contains(b))
        {
            return true;
        }

        var t0 = 0f;
        var t1 = 1f;
        var dx = b.x - a.x;
        var dz = b.y - a.y;

        if (!ClipRouteSegment(-dx, a.x - rect.xMin, ref t0, ref t1)) return false;
        if (!ClipRouteSegment(dx, rect.xMax - a.x, ref t0, ref t1)) return false;
        if (!ClipRouteSegment(-dz, a.y - rect.yMin, ref t0, ref t1)) return false;
        if (!ClipRouteSegment(dz, rect.yMax - a.y, ref t0, ref t1)) return false;

        return t1 >= t0;
    }

    private static bool ClipRouteSegment(float p, float q, ref float t0, ref float t1)
    {
        if (Mathf.Abs(p) < 0.00001f)
        {
            return q >= 0f;
        }

        var r = q / p;
        if (p < 0f)
        {
            if (r > t1) return false;
            if (r > t0) t0 = r;
        }
        else
        {
            if (r < t0) return false;
            if (r < t1) t1 = r;
        }

        return true;
    }

    private List<Vector3> RoundHandoffRouteCorners(List<Vector3> route)
    {
        if (route == null || route.Count < 3)
        {
            return route;
        }

        var radius = Mathf.Max(0f, handoffRouteCornerRadius);
        if (radius < 0.02f)
        {
            return route;
        }

        var rounded = new List<Vector3> { route[0] };
        for (var i = 1; i < route.Count - 1; i++)
        {
            var previous = route[i - 1];
            var corner = route[i];
            var next = route[i + 1];
            var into = corner - previous;
            var outOf = next - corner;
            var intoLength = into.magnitude;
            var outLength = outOf.magnitude;

            if (intoLength < 0.05f || outLength < 0.05f)
            {
                AddRoutePointIfDistinct(rounded, corner);
                continue;
            }

            var cornerRadius = Mathf.Min(radius, intoLength * 0.45f, outLength * 0.45f);
            var entry = corner - into.normalized * cornerRadius;
            var exit = corner + outOf.normalized * cornerRadius;
            AddRoutePointIfDistinct(rounded, entry);

            for (var step = 1; step <= 4; step++)
            {
                var t = step / 4f;
                var a = Vector3.Lerp(entry, corner, t);
                var b = Vector3.Lerp(corner, exit, t);
                AddRoutePointIfDistinct(rounded, Vector3.Lerp(a, b, t));
            }
        }

        AddRoutePointIfDistinct(rounded, route[route.Count - 1]);
        return rounded;
    }

    private void RenderHandoffRoute(List<Vector3> route)
    {
        if (route == null || route.Count < 2)
        {
            DisableHandoffRouteDashes(0);
            return;
        }

        var cumulative = new float[route.Count];
        for (var i = 1; i < route.Count; i++)
        {
            cumulative[i] = cumulative[i - 1] + Vector3.Distance(route[i - 1], route[i]);
        }

        var totalLength = cumulative[cumulative.Length - 1];
        if (totalLength < 0.05f)
        {
            DisableHandoffRouteDashes(0);
            return;
        }

        var dashLength = Mathf.Clamp(handoffRouteDashLength, 0.08f, 2f);
        var gapLength = Mathf.Clamp(handoffRouteGapLength, 0.04f, 2f);
        var patternLength = dashLength + gapLength;
        var phase = handoffRouteDashSpeed > 0f
            ? Mathf.Repeat(Time.time * handoffRouteDashSpeed, patternLength)
            : 0f;

        var cursor = phase - patternLength;
        var dashIndex = 0;
        while (cursor < totalLength && dashIndex < 192)
        {
            var dashStart = Mathf.Max(0f, cursor);
            var dashEnd = Mathf.Min(totalLength, cursor + dashLength);
            if (dashEnd - dashStart > 0.03f)
            {
                var points = GetHandoffRouteSubsection(route, cumulative, dashStart, dashEnd);
                SetHandoffRouteDash(dashIndex, points);
                dashIndex++;
            }

            cursor += patternLength;
        }

        DisableHandoffRouteDashes(dashIndex);
    }

    private List<Vector3> GetHandoffRouteSubsection(List<Vector3> route, float[] cumulative, float startDistance, float endDistance)
    {
        var points = new List<Vector3>();
        AddRoutePointIfDistinct(points, GetHandoffRoutePointAtDistance(route, cumulative, startDistance));
        for (var i = 1; i < route.Count - 1; i++)
        {
            if (cumulative[i] > startDistance && cumulative[i] < endDistance)
            {
                AddRoutePointIfDistinct(points, route[i]);
            }
        }
        AddRoutePointIfDistinct(points, GetHandoffRoutePointAtDistance(route, cumulative, endDistance));
        return points;
    }

    private static Vector3 GetHandoffRoutePointAtDistance(List<Vector3> route, float[] cumulative, float distance)
    {
        if (distance <= 0f)
        {
            return route[0];
        }

        var total = cumulative[cumulative.Length - 1];
        if (distance >= total)
        {
            return route[route.Count - 1];
        }

        for (var i = 1; i < cumulative.Length; i++)
        {
            if (cumulative[i] < distance)
            {
                continue;
            }

            var segmentLength = cumulative[i] - cumulative[i - 1];
            if (segmentLength < 0.0001f)
            {
                return route[i];
            }

            var t = (distance - cumulative[i - 1]) / segmentLength;
            return Vector3.Lerp(route[i - 1], route[i], t);
        }

        return route[route.Count - 1];
    }

    private void SetHandoffRouteDash(int index, List<Vector3> points)
    {
        if (points == null || points.Count < 2)
        {
            return;
        }

        var dash = GetHandoffRouteDash(index);
        dash.gameObject.SetActive(true);
        dash.positionCount = points.Count;
        for (var i = 0; i < points.Count; i++)
        {
            dash.SetPosition(i, points[i]);
        }
        ApplyHandoffRouteDashStyle(dash);
    }

    private LineRenderer GetHandoffRouteDash(int index)
    {
        EnsureHandoffRouteRoot();
        while (handoffRouteDashes.Count <= index)
        {
            var dashObject = new GameObject($"HandoffRouteDash_{handoffRouteDashes.Count:00}");
            dashObject.hideFlags = HideFlags.DontSave;
            dashObject.transform.SetParent(handoffRouteRoot.transform, false);
            var dash = dashObject.AddComponent<LineRenderer>();
            dash.useWorldSpace = true;
            dash.sharedMaterial = handoffRouteMaterial;
            dash.numCapVertices = 5;
            dash.numCornerVertices = 5;
            dash.textureMode = LineTextureMode.Stretch;
            dash.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            dash.receiveShadows = false;
            handoffRouteDashes.Add(dash);
        }

        return handoffRouteDashes[index];
    }

    private void DisableHandoffRouteDashes(int firstInactiveIndex)
    {
        for (var i = firstInactiveIndex; i < handoffRouteDashes.Count; i++)
        {
            if (handoffRouteDashes[i] != null)
            {
                handoffRouteDashes[i].gameObject.SetActive(false);
            }
        }
    }

    private void ApplyHandoffRouteDashStyle(LineRenderer dash)
    {
        if (dash == null)
        {
            return;
        }

        var pulse = Mathf.Sin(Time.time * 2.6f) * 0.12f + 0.88f;
        var color = new Color(
            handoffRouteColor.r,
            handoffRouteColor.g,
            handoffRouteColor.b,
            Mathf.Clamp01(handoffRouteColor.a * pulse));
        var width = Mathf.Max(0.01f, handoffLineWidth) * (0.92f + pulse * 0.08f);
        dash.startWidth = width;
        dash.endWidth = width;
        dash.startColor = color;
        dash.endColor = color;
        dash.sharedMaterial = handoffRouteMaterial;
    }

    private static void AddRoutePointIfDistinct(List<Vector3> points, Vector3 point)
    {
        if (points.Count == 0 || (points[points.Count - 1] - point).sqrMagnitude > 0.0004f)
        {
            points.Add(point);
        }
    }

    private AgentVoiceSettings GetAgentVoiceSettings(string agentId)
    {
        if (!string.IsNullOrWhiteSpace(agentId) && agentVoices.TryGetValue(agentId, out var settings))
        {
            return settings;
        }

        return new AgentVoiceSettings
        {
            voice = null,
            voiceStyle = null,
            ttsModel = null
        };
    }

    private bool IsTtsRateLimited(string agentId)
    {
        if (ttsCooldownSeconds <= 0f || string.IsNullOrWhiteSpace(agentId))
        {
            return false;
        }

        if (ttsLastRequest.TryGetValue(agentId, out var lastTime))
        {
            return Time.time - lastTime < ttsCooldownSeconds;
        }

        return false;
    }

    private void RecordTtsRequest(string agentId)
    {
        if (string.IsNullOrWhiteSpace(agentId))
        {
            return;
        }

        ttsLastRequest[agentId] = Time.time;
    }

    private void PlayAgentClip(string agentId, AudioClip clip)
    {
        if (clip == null || string.IsNullOrWhiteSpace(agentId))
        {
            return;
        }

        if (agentObjects.TryGetValue(agentId, out var visual) && visual != null && visual.audioSource != null)
        {
            visual.audioSource.PlayOneShot(clip);
        }
    }

    private IEnumerator PlayAgentSpeech(string agentId, string text)
    {
        if (!enableTts || string.IsNullOrWhiteSpace(text) || string.IsNullOrWhiteSpace(agentId))
        {
            yield break;
        }

        var key = $"{agentId}::{text}";
        if (ttsCache.TryGetValue(key, out var cachedClip))
        {
            Debug.Log($"[TTS] Cache hit für Agent {agentId} (text_len={text.Length}).");
            PlayAgentClip(agentId, cachedClip);
            yield break;
        }

        if (ttsInFlight.Contains(key))
        {
            Debug.Log($"[TTS] Anfrage bereits in-flight für Agent {agentId} (text_len={text.Length}).");
            yield break;
        }

        if (IsTtsRateLimited(agentId))
        {
            Debug.Log($"[TTS] Rate limit aktiv für Agent {agentId} (text_len={text.Length}).");
            yield break;
        }

        ttsInFlight.Add(key);
        RecordTtsRequest(agentId);

        var voiceSettings = GetAgentVoiceSettings(agentId);
        var payload = new TtsRequest
        {
            text = text,
            voice = voiceSettings.voice,
            voice_style = voiceSettings.voiceStyle,
            tts_model = voiceSettings.ttsModel
        };
        var json = JsonUtility.ToJson(payload);
        var url = $"{backendBaseUrl}/tts";
        Debug.Log(
            "[TTS] Sende Anfrage: "
            + $"agent={agentId}, text_len={text.Length}, voice={payload.voice}, model={payload.tts_model}"
        );

        using (var req = new UnityWebRequest(url, "POST"))
        {
            var body = Encoding.UTF8.GetBytes(json);
            req.uploadHandler = new UploadHandlerRaw(body);
            req.downloadHandler = new DownloadHandlerAudioClip(url, AudioType.MPEG);
            req.SetRequestHeader("Content-Type", "application/json");
            yield return req.SendWebRequest();

            ttsInFlight.Remove(key);

            if (req.result != UnityWebRequest.Result.Success)
            {
                statusMessage = "TTS fehlgeschlagen: " + req.error;
                chatLog.Add(statusMessage + " | " + req.downloadHandler.text);
                Debug.LogWarning($"[TTS] Fehler: agent={agentId}, error={req.error}");
                yield break;
            }

            var clip = DownloadHandlerAudioClip.GetContent(req);
            if (clip == null)
            {
                statusMessage = "TTS fehlgeschlagen: Kein AudioClip.";
                chatLog.Add(statusMessage);
                Debug.LogWarning($"[TTS] Kein AudioClip: agent={agentId}");
                yield break;
            }

            ttsCache[key] = clip;
            Debug.Log($"[TTS] AudioClip erhalten: agent={agentId}, length={clip.length:0.00}s");
            PlayAgentClip(agentId, clip);
        }
    }

    private void HandleVoiceInput()
    {
        if (!enableVoiceInput)
        {
            return;
        }

        if (isVoiceRecording)
        {
            if (WasVoiceRecordKeyReleasedThisFrame()
                || Time.time - voiceRecordingStartedAt >= Mathf.Max(1f, voiceMaxRecordSeconds))
            {
                StopVoiceRecordingAndSend();
            }
            return;
        }

        if (sttInFlight || !CanStartVoiceRecordingFromKeyboard())
        {
            return;
        }

        if (WasVoiceRecordKeyPressedThisFrame())
        {
            StartVoiceRecording();
        }
    }

    private bool CanStartVoiceRecordingFromKeyboard()
    {
        if (string.IsNullOrEmpty(sessionId) || string.IsNullOrEmpty(activeAgentId))
        {
            return false;
        }

        if (_fpvChatOpen)
        {
            return false;
        }

        if (!_fpvActive && isChatInputFocused)
        {
            return false;
        }

        if (_fpvActive && string.IsNullOrEmpty(_fpvNearestAgentId))
        {
            return false;
        }

        return true;
    }

    private void StartVoiceRecording()
    {
        if (sttInFlight)
        {
            statusMessage = "Transkription laeuft bereits.";
            return;
        }

#if UNITY_WEBGL && !UNITY_EDITOR
        StartBrowserVoiceRecording();
        return;
#endif

        if (Microphone.devices == null || Microphone.devices.Length == 0)
        {
            statusMessage = "Kein Mikrofon gefunden.";
            chatLog.Add(statusMessage);
            return;
        }

        if (string.IsNullOrEmpty(sessionId) || string.IsNullOrEmpty(activeAgentId))
        {
            statusMessage = "Kein aktiver Agent fuer Voice Chat.";
            return;
        }

        voiceRecordingDevice = Microphone.devices[0];
        var seconds = Mathf.CeilToInt(Mathf.Max(1f, voiceMaxRecordSeconds));
        var sampleRate = Mathf.Clamp(voiceSampleRate, 8000, 48000);
        voiceRecordingClip = Microphone.Start(voiceRecordingDevice, false, seconds, sampleRate);
        if (voiceRecordingClip == null)
        {
            statusMessage = "Mikrofonaufnahme konnte nicht gestartet werden.";
            return;
        }

        isVoiceRecording = true;
        voiceRecordingStartedAt = Time.time;
        statusMessage = $"Aufnahme laeuft... {voiceRecordKey} loslassen zum Senden.";
    }

#if UNITY_WEBGL && !UNITY_EDITOR
    private void StartBrowserVoiceRecording()
    {
        if (IAVoice_IsSupported() == 0)
        {
            statusMessage = "Browser-Mikrofon wird nicht unterstuetzt.";
            chatLog.Add(statusMessage);
            return;
        }

        if (string.IsNullOrEmpty(sessionId) || string.IsNullOrEmpty(activeAgentId))
        {
            statusMessage = "Kein aktiver Agent fuer Voice Chat.";
            return;
        }

        isVoiceRecording = true;
        sttInFlight = false;
        voiceRecordingStartedAt = Time.time;
        statusMessage = $"Browser-Aufnahme laeuft... {voiceRecordKey} loslassen zum Senden.";
        IAVoice_StartRecording(
            gameObject.name,
            BrowserVoiceTranscriptMethod,
            BrowserVoiceErrorMethod,
            backendBaseUrl,
            sttModel,
            sttLanguage,
            Mathf.Max(1f, voiceMaxRecordSeconds));
    }
#endif

    private void StopVoiceRecordingAndSend()
    {
        if (!isVoiceRecording)
        {
            return;
        }

#if UNITY_WEBGL && !UNITY_EDITOR
        isVoiceRecording = false;
        sttInFlight = true;
        statusMessage = "Transkription laeuft...";
        IAVoice_StopRecording();
        return;
#endif

        var clip = voiceRecordingClip;
        var device = voiceRecordingDevice;
        var samplePosition = 0;
        if (!string.IsNullOrEmpty(device))
        {
            samplePosition = Microphone.GetPosition(device);
            if (Microphone.IsRecording(device))
            {
                Microphone.End(device);
            }
        }

        isVoiceRecording = false;
        voiceRecordingClip = null;
        voiceRecordingDevice = "";

        if (clip == null)
        {
            statusMessage = "Aufnahme fehlgeschlagen.";
            return;
        }

        var elapsed = Mathf.Clamp(Time.time - voiceRecordingStartedAt, 0f, Mathf.Max(1f, voiceMaxRecordSeconds));
        var elapsedSamples = Mathf.RoundToInt(elapsed * clip.frequency);
        var sampleFrames = samplePosition > 0 ? samplePosition : elapsedSamples;
        sampleFrames = Mathf.Clamp(sampleFrames, 0, clip.samples);

        if (sampleFrames < Mathf.RoundToInt(clip.frequency * 0.2f))
        {
            statusMessage = "Aufnahme zu kurz.";
            return;
        }

        var samples = new float[sampleFrames * clip.channels];
        clip.GetData(samples, 0);
        var wav = EncodeWav(samples, sampleFrames, clip.channels, clip.frequency);
        StartCoroutine(TranscribeVoiceAndSend(wav));
    }

    private IEnumerator TranscribeVoiceAndSend(byte[] wavBytes)
    {
        if (wavBytes == null || wavBytes.Length == 0)
        {
            statusMessage = "Keine Audiodaten fuer Transkription.";
            yield break;
        }

        sttInFlight = true;
        statusMessage = "Transkription laeuft...";

        var url = $"{backendBaseUrl}/stt";
        var form = new WWWForm();
        form.AddBinaryData("audio", wavBytes, "voice.wav", "audio/wav");
        if (!string.IsNullOrWhiteSpace(sttModel))
        {
            form.AddField("model", sttModel);
        }
        if (!string.IsNullOrWhiteSpace(sttLanguage))
        {
            form.AddField("language", sttLanguage);
        }

        using (var req = UnityWebRequest.Post(url, form))
        {
            yield return req.SendWebRequest();
            sttInFlight = false;

            if (req.result != UnityWebRequest.Result.Success)
            {
                statusMessage = "Transkription fehlgeschlagen: " + req.error;
                chatLog.Add(statusMessage + " | " + req.downloadHandler.text);
                yield break;
            }

            var resp = JsonUtility.FromJson<SttResponse>(req.downloadHandler.text);
            var transcript = resp == null ? "" : (resp.text ?? "").Trim();
            if (string.IsNullOrWhiteSpace(transcript))
            {
                statusMessage = "Keine Sprache erkannt.";
                chatLog.Add(statusMessage);
                yield break;
            }

            HandleVoiceTranscript(transcript);
        }
    }

    public void OnBrowserVoiceTranscript(string json)
    {
        isVoiceRecording = false;
        sttInFlight = false;

        var resp = string.IsNullOrWhiteSpace(json) ? null : JsonUtility.FromJson<SttResponse>(json);
        var transcript = resp == null ? "" : (resp.text ?? "").Trim();
        if (string.IsNullOrWhiteSpace(transcript))
        {
            statusMessage = "Keine Sprache erkannt.";
            chatLog.Add(statusMessage);
            return;
        }

        HandleVoiceTranscript(transcript);
    }

    public void OnBrowserVoiceError(string message)
    {
        isVoiceRecording = false;
        sttInFlight = false;
        var detail = string.IsNullOrWhiteSpace(message) ? "Unbekannter Browser-Mikrofonfehler." : message;
        statusMessage = "Voice fehlgeschlagen: " + detail;
        chatLog.Add(statusMessage);
    }

    private void HandleVoiceTranscript(string transcript)
    {
        statusMessage = "Transkription OK.";
        if (sendVoiceTranscriptAutomatically)
        {
            AddUserChatLine(transcript, voice: true);
            StartCoroutine(SendChat(transcript));
        }
        else
        {
            chatInput = transcript;
            statusMessage = "Transkript ins Chatfeld uebernommen.";
        }
    }

    private static byte[] EncodeWav(float[] samples, int sampleFrames, int channels, int frequency)
    {
        channels = Mathf.Max(1, channels);
        frequency = Mathf.Max(8000, frequency);
        var sampleCount = Mathf.Clamp(sampleFrames * channels, 0, samples == null ? 0 : samples.Length);
        var dataSize = sampleCount * 2;
        var bytes = new byte[44 + dataSize];

        WriteAscii(bytes, 0, "RIFF");
        WriteInt32(bytes, 4, 36 + dataSize);
        WriteAscii(bytes, 8, "WAVE");
        WriteAscii(bytes, 12, "fmt ");
        WriteInt32(bytes, 16, 16);
        WriteInt16(bytes, 20, 1);
        WriteInt16(bytes, 22, (short)channels);
        WriteInt32(bytes, 24, frequency);
        WriteInt32(bytes, 28, frequency * channels * 2);
        WriteInt16(bytes, 32, (short)(channels * 2));
        WriteInt16(bytes, 34, 16);
        WriteAscii(bytes, 36, "data");
        WriteInt32(bytes, 40, dataSize);

        var offset = 44;
        for (var i = 0; i < sampleCount; i++)
        {
            var value = Mathf.Clamp(samples[i], -1f, 1f);
            var pcm = (short)Mathf.RoundToInt(value * short.MaxValue);
            bytes[offset++] = (byte)(pcm & 0xff);
            bytes[offset++] = (byte)((pcm >> 8) & 0xff);
        }

        return bytes;
    }

    private static void WriteAscii(byte[] bytes, int offset, string value)
    {
        for (var i = 0; i < value.Length; i++)
        {
            bytes[offset + i] = (byte)value[i];
        }
    }

    private static void WriteInt16(byte[] bytes, int offset, short value)
    {
        bytes[offset] = (byte)(value & 0xff);
        bytes[offset + 1] = (byte)((value >> 8) & 0xff);
    }

    private static void WriteInt32(byte[] bytes, int offset, int value)
    {
        bytes[offset] = (byte)(value & 0xff);
        bytes[offset + 1] = (byte)((value >> 8) & 0xff);
        bytes[offset + 2] = (byte)((value >> 16) & 0xff);
        bytes[offset + 3] = (byte)((value >> 24) & 0xff);
    }

    private bool WasVoiceRecordKeyPressedThisFrame()
    {
#if ENABLE_INPUT_SYSTEM
        if (TryGetInputSystemKeyControl(voiceRecordKey, out var control))
            return control.wasPressedThisFrame;
        return false;
#elif ENABLE_LEGACY_INPUT_MANAGER
        return Input.GetKeyDown(voiceRecordKey);
#else
        return false;
#endif
    }

    private bool WasVoiceRecordKeyReleasedThisFrame()
    {
#if ENABLE_INPUT_SYSTEM
        if (TryGetInputSystemKeyControl(voiceRecordKey, out var control))
            return control.wasReleasedThisFrame;
        return false;
#elif ENABLE_LEGACY_INPUT_MANAGER
        return Input.GetKeyUp(voiceRecordKey);
#else
        return false;
#endif
    }

#if ENABLE_INPUT_SYSTEM
    private static bool TryGetInputSystemKeyControl(
        KeyCode keyCode,
        out UnityEngine.InputSystem.Controls.KeyControl control)
    {
        control = null;
        var keyboard = Keyboard.current;
        if (keyboard == null)
        {
            return false;
        }

        var name = keyCode.ToString();
        if (keyCode == KeyCode.Return)
            name = "Enter";
        else if (keyCode == KeyCode.BackQuote)
            name = "Backquote";
        else if (keyCode == KeyCode.LeftControl)
            name = "LeftCtrl";
        else if (keyCode == KeyCode.RightControl)
            name = "RightCtrl";

        if (!Enum.TryParse<UnityEngine.InputSystem.Key>(name, true, out var inputKey))
        {
            return false;
        }

        try
        {
            control = keyboard[inputKey];
            return control != null;
        }
        catch
        {
            control = null;
            return false;
        }
    }
#endif

    private void TrySendChatFromInput()
    {
        if (string.IsNullOrWhiteSpace(chatInput))
        {
            return;
        }

        var toSend = chatInput.Trim();
        AddUserChatLine(toSend);
        chatInput = "";
        StartCoroutine(SendChat(toSend));
    }

    private Transform GetViewerMovementTransform(Camera cam)
    {
        if (cam == null || !moveXrOriginInsteadOfCamera)
        {
            return cam != null ? cam.transform : null;
        }

        var current = cam.transform;
        while (current != null)
        {
            if (IsXrOriginLikeTransform(current))
            {
                return current;
            }

            current = current.parent;
        }

        return cam.transform;
    }

    private static bool IsXrOriginLikeTransform(Transform candidate)
    {
        if (candidate == null)
        {
            return false;
        }

        var name = candidate.name;
        if (!string.IsNullOrEmpty(name)
            && (name.IndexOf("XR Origin", StringComparison.OrdinalIgnoreCase) >= 0
                || name.IndexOf("XROrigin", StringComparison.OrdinalIgnoreCase) >= 0
                || name.IndexOf("XR Rig", StringComparison.OrdinalIgnoreCase) >= 0))
        {
            return true;
        }

        var components = candidate.GetComponents<Component>();
        foreach (var component in components)
        {
            if (component == null)
            {
                continue;
            }

            var typeName = component.GetType().Name;
            if (typeName == "XROrigin" || typeName == "XRRig")
            {
                return true;
            }
        }

        return false;
    }

    private static void MoveViewerToCameraWorldPosition(Camera cam, Transform viewerTransform, Vector3 targetCameraWorldPosition)
    {
        if (cam == null || viewerTransform == null)
        {
            return;
        }

        if (viewerTransform == cam.transform)
        {
            viewerTransform.position = targetCameraWorldPosition;
            return;
        }

        var delta = targetCameraWorldPosition - cam.transform.position;
        viewerTransform.position += delta;
    }

    private void UpdateFreeMovement()
    {
        if (!enableFreeMovement)
        {
            return;
        }

        if (isChatInputFocused && !_fpvActive)
        {
            return;
        }

        if (_fpvChatOpen)
        {
            return;
        }

        var cam = Camera.main;
        if (cam == null)
        {
            return;
        }
        var viewerTransform = GetViewerMovementTransform(cam);
        if (viewerTransform == null)
        {
            return;
        }

        if (!cameraInitialized)
        {
            var euler = cam.transform.rotation.eulerAngles;
            cameraYaw = euler.y;
            cameraPitch = euler.x;
            cameraInitialized = true;
        }

        var move = Vector3.zero;
        var lookDelta = Vector2.zero;
        var isLooking = false;
        var isBoost = false;

#if ENABLE_INPUT_SYSTEM
        var keyboard = Keyboard.current;
        if (keyboard != null)
        {
            if (keyboard.wKey.isPressed) move += Vector3.forward;
            if (keyboard.sKey.isPressed) move += Vector3.back;
            if (keyboard.aKey.isPressed) move += Vector3.left;
            if (keyboard.dKey.isPressed) move += Vector3.right;
            if (keyboard.qKey.isPressed) move += Vector3.down;
            if (keyboard.eKey.isPressed) move += Vector3.up;
            isBoost = keyboard.leftShiftKey.isPressed || keyboard.rightShiftKey.isPressed;
        }

        var mouse = Mouse.current;
        if (mouse != null && (_fpvActive || mouse.rightButton.isPressed))
        {
            isLooking = true;
            lookDelta = mouse.delta.ReadValue();
        }
#elif ENABLE_LEGACY_INPUT_MANAGER
        if (Input.GetKey(KeyCode.W)) move += Vector3.forward;
        if (Input.GetKey(KeyCode.S)) move += Vector3.back;
        if (Input.GetKey(KeyCode.A)) move += Vector3.left;
        if (Input.GetKey(KeyCode.D)) move += Vector3.right;
        if (Input.GetKey(KeyCode.Q)) move += Vector3.down;
        if (Input.GetKey(KeyCode.E)) move += Vector3.up;
        isBoost = Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);

        if (_fpvActive || Input.GetMouseButton(1))
        {
            isLooking = true;
            lookDelta = new Vector2(Input.GetAxis("Mouse X"), Input.GetAxis("Mouse Y"));
        }
#endif

        if (isLooking)
        {
            var lookSpeed = _fpvActive ? fpvMouseSensitivity : cameraLookSpeed;
#if ENABLE_INPUT_SYSTEM
            if (_fpvActive)
                lookSpeed *= InputSystemMouseDeltaScale;
#endif
            cameraYaw += lookDelta.x * lookSpeed;
            cameraPitch = Mathf.Clamp(cameraPitch - lookDelta.y * lookSpeed, -cameraLookClamp, cameraLookClamp);
            if (viewerTransform == cam.transform)
            {
                cam.transform.rotation = Quaternion.Euler(cameraPitch, cameraYaw, 0f);
            }
            else
            {
                viewerTransform.rotation = Quaternion.Euler(0f, cameraYaw, 0f);
            }
        }

        if (move.sqrMagnitude > 0.001f)
        {
            var speed = cameraMoveSpeed * (isBoost ? cameraBoostMultiplier : 1f);
            Vector3 direction;
            if (viewerTransform != cam.transform)
            {
                var forward = cam.transform.forward;
                forward.y = 0f;
                if (forward.sqrMagnitude < 0.001f)
                {
                    forward = viewerTransform.forward;
                    forward.y = 0f;
                }
                forward = forward.sqrMagnitude > 0.001f ? forward.normalized : Vector3.forward;

                var right = cam.transform.right;
                right.y = 0f;
                if (right.sqrMagnitude < 0.001f)
                {
                    right = viewerTransform.right;
                    right.y = 0f;
                }
                right = right.sqrMagnitude > 0.001f ? right.normalized : Vector3.right;

                direction = (right * move.x + Vector3.up * move.y + forward * move.z).normalized;
            }
            else if (_fpvActive)
            {
                // Horizontal movement (WASD) uses yaw only so height stays locked
                var horizontal = Quaternion.Euler(0f, cameraYaw, 0f) * new Vector3(move.x, 0f, move.z);
                var vertical   = new Vector3(0f, move.y, 0f);
                direction = (horizontal + vertical).normalized;
            }
            else
            {
                direction = cam.transform.TransformDirection(move.normalized);
            }
            var displacement = direction * speed * Time.deltaTime;
            if (_fpvActive)
            {
                MoveViewerWithCollision(cam, viewerTransform, displacement);
            }
            else
            {
                viewerTransform.position += displacement;
            }
        }
    }

    private void MoveViewerWithCollision(Camera cam, Transform viewerTransform, Vector3 displacement)
    {
        if (cam == null || viewerTransform == null || displacement.sqrMagnitude < 0.000001f)
        {
            return;
        }

        var remaining = displacement;
        var applied = Vector3.zero;
        var skin = Mathf.Clamp(fpvCollisionSkin, 0.005f, 0.2f);

        for (var i = 0; i < 3; i++)
        {
            var distance = remaining.magnitude;
            if (distance < 0.0001f)
            {
                break;
            }

            var direction = remaining / distance;
            RaycastHit hit;
            if (Physics.CapsuleCast(
                    GetFpvCollisionCapsuleBottom(cam.transform.position + applied),
                    GetFpvCollisionCapsuleTop(cam.transform.position + applied),
                    Mathf.Max(0.05f, fpvCollisionRadius),
                    direction,
                    out hit,
                    distance + skin,
                    fpvCollisionMask,
                    QueryTriggerInteraction.Ignore))
            {
                var allowed = Mathf.Max(0f, hit.distance - skin);
                applied += direction * allowed;

                var leftover = remaining - direction * allowed;
                var slide = Vector3.ProjectOnPlane(leftover, hit.normal);
                if (slide.sqrMagnitude < 0.0001f)
                {
                    break;
                }

                remaining = slide;
                continue;
            }

            applied += remaining;
            break;
        }

        viewerTransform.position += applied;
    }

    private Vector3 GetFpvCollisionCapsuleBottom(Vector3 cameraPosition)
    {
        var radius = Mathf.Max(0.05f, fpvCollisionRadius);
        var eyeToFeet = Mathf.Max(radius, fpvEyeHeight - radius);
        return cameraPosition + Vector3.down * eyeToFeet;
    }

    private Vector3 GetFpvCollisionCapsuleTop(Vector3 cameraPosition)
    {
        var radius = Mathf.Max(0.05f, fpvCollisionRadius);
        var height = Mathf.Max(radius * 2f + 0.05f, fpvCollisionHeight);
        return GetFpvCollisionCapsuleBottom(cameraPosition) + Vector3.up * Mathf.Max(0.01f, height - radius * 2f);
    }

    private void UpdatePendingAgentPulse()
    {
        if (string.IsNullOrEmpty(_pendingHandoffAgentId)) return;
        if (!agentObjects.TryGetValue(_pendingHandoffAgentId, out var visual) || visual?.renderer == null) return;
        var pulse = Mathf.Sin(Time.time * 4f) * 0.5f + 0.5f;
        var emissive = activeAgentColor * (pulse * 2.5f);
        var mat = visual.renderer.material;
        mat.EnableKeyword("_EMISSION");
        mat.SetColor("_EmissionColor", emissive);
    }

    private void UpdateFpvProximity()
    {
        var cam = Camera.main;
        if (cam == null) return;
        var camPos = cam.transform.position;

        if (!string.IsNullOrEmpty(_pendingHandoffAgentId))
        {
            if (agentObjects.TryGetValue(_pendingHandoffAgentId, out var pendingVisual)
                && pendingVisual?.obj != null
                && Vector3.Distance(camPos, pendingVisual.obj.transform.position) <= fpvInteractionRadius)
            {
                _fpvNearestAgentId = _pendingHandoffAgentId;
                TriggerPendingHandoffArrival();
            }
            else
            {
                _fpvNearestAgentId = "";
                CloseFpvChat();
            }

            HandleFpvChatKey();
            return;
        }

        var nearest = "";
        var nearestDist = fpvInteractionRadius + 1f;

        foreach (var pair in agentObjects)
        {
            if (pair.Value?.obj == null) continue;
            var d = Vector3.Distance(camPos, pair.Value.obj.transform.position);
            if (d < nearestDist) { nearestDist = d; nearest = pair.Key; }
        }

        if (nearestDist <= fpvInteractionRadius)
        {
            _fpvNearestAgentId = nearest;
            if (!string.IsNullOrEmpty(nearest) && nearest != activeAgentId)
            {
                SetActiveAgentId(nearest);
            }
        }
        else
        {
            _fpvNearestAgentId = "";
            CloseFpvChat();
        }

        HandleFpvChatKey();
    }

    private void HandleFpvChatKey()
    {
#if ENABLE_INPUT_SYSTEM
        if (!string.IsNullOrEmpty(_fpvNearestAgentId) && !_fpvChatOpen)
        {
            var kb = Keyboard.current;
            if (kb != null && kb.tKey.wasPressedThisFrame)
                ToggleFpvChat();
        }
#elif ENABLE_LEGACY_INPUT_MANAGER
        if (!string.IsNullOrEmpty(_fpvNearestAgentId) && !_fpvChatOpen && Input.GetKeyDown(fpvChatKey))
            ToggleFpvChat();
#endif
    }

    private void CloseFpvChat()
    {
        if (!_fpvChatOpen)
            return;

        _fpvChatOpen = false;
        _fpvChatInput = "";
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    private void ToggleFpvChat()
    {
        _fpvChatOpen = !_fpvChatOpen;
        if (_fpvChatOpen)
        {
            _fpvChatJustOpened = true;
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }
        else
        {
            _fpvChatInput = "";
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
        }
    }

    private void DrawFpvDirectionArrow()
    {
        if (string.IsNullOrEmpty(_pendingHandoffAgentId)) return;
        if (!agentObjects.TryGetValue(_pendingHandoffAgentId, out var visual) || visual?.obj == null) return;

        var cam = Camera.main;
        if (cam == null) return;

        var sw = Screen.width;
        var sh = Screen.height;
        var center = new Vector2(sw * 0.5f, sh * 0.5f);

        var dir = GetFpvHorizontalGuiDirection(visual.obj.transform.position, cam, out var signedAngle);
        if (dir.sqrMagnitude < 0.001f) return;

        var angle = Mathf.Atan2(dir.x, -dir.y) * Mathf.Rad2Deg;
        var indicatorColor = GetFpvDirectionArrowColor(signedAngle, fpvDirectionArrowTint);

        var arrowSize = Mathf.Clamp(fpvDirectionArrowSize, 36f, 96f);
        var maxRadius = Mathf.Max(40f, Mathf.Min(sw, sh) * 0.42f - arrowSize * 0.5f);
        var radius = Mathf.Clamp(fpvDirectionArrowRadius, 40f, maxRadius);
        var arrowCenter = center + dir * radius;
        var arrowRect = new Rect(
            arrowCenter.x - arrowSize * 0.5f,
            arrowCenter.y - arrowSize * 0.5f,
            arrowSize,
            arrowSize);

        var pulse = Mathf.Sin(Time.time * 3f) * 0.3f + 0.7f;
        var oldColor = GUI.color;
        var savedMatrix = GUI.matrix;

        GUIUtility.RotateAroundPivot(angle, arrowCenter);
        var texture = GetFpvDirectionArrowTexture();

        GUI.color = new Color(0f, 0f, 0f, pulse * 0.45f);
        GUI.DrawTexture(new Rect(arrowRect.x + 2f, arrowRect.y + 2f, arrowRect.width, arrowRect.height),
            texture, ScaleMode.StretchToFill, true);

        GUI.color = new Color(indicatorColor.r, indicatorColor.g, indicatorColor.b, indicatorColor.a * pulse);
        GUI.DrawTexture(arrowRect, texture, ScaleMode.StretchToFill, true);

        GUI.matrix = savedMatrix;
        GUI.color = oldColor;

        DrawFpvDirectionLabel(arrowRect, dir, signedAngle, indicatorColor, pulse);
    }

    private static Vector2 GetFpvHorizontalGuiDirection(Vector3 targetWorldPos, Camera cam, out float signedAngle)
    {
        signedAngle = 0f;
        var toTarget = targetWorldPos - cam.transform.position;
        toTarget.y = 0f;
        if (toTarget.sqrMagnitude < 0.001f)
            return Vector2.zero;

        var forward = cam.transform.forward;
        forward.y = 0f;
        if (forward.sqrMagnitude < 0.001f)
            forward = Vector3.forward;
        forward.Normalize();

        var right = cam.transform.right;
        right.y = 0f;
        if (right.sqrMagnitude < 0.001f)
            right = Vector3.Cross(Vector3.up, forward);
        right.Normalize();

        var flatTarget = toTarget.normalized;
        var x = Vector3.Dot(flatTarget, right);
        var z = Vector3.Dot(flatTarget, forward);
        signedAngle = Mathf.Atan2(x, z) * Mathf.Rad2Deg;
        var dir = new Vector2(x, -z);
        return dir.sqrMagnitude > 0.001f ? dir.normalized : Vector2.zero;
    }

    private void DrawFpvDirectionLabel(Rect arrowRect, Vector2 dir, float signedAngle, Color color, float pulse)
    {
        const float labelW = 118f;
        const float labelH = 24f;
        var labelX = Mathf.Clamp(arrowRect.center.x - labelW * 0.5f, 8f, Screen.width - labelW - 8f);
        var labelY = dir.y > 0.25f ? arrowRect.y - labelH - 6f : arrowRect.yMax + 6f;
        labelY = Mathf.Clamp(labelY, 8f, Screen.height - labelH - 8f);
        var labelRect = new Rect(labelX, labelY, labelW, labelH);

        var oldColor = GUI.color;
        GUI.color = new Color(0f, 0f, 0f, 0.55f * pulse);
        GUI.Box(new Rect(labelRect.x + 2f, labelRect.y + 2f, labelRect.width, labelRect.height), GUIContent.none);

        GUI.color = new Color(1f, 1f, 1f, pulse);
        var style = new GUIStyle(GUI.skin.box)
        {
            fontSize = 13,
            fontStyle = FontStyle.Bold,
            alignment = TextAnchor.MiddleCenter
        };
        style.normal.textColor = color;
        GUI.Box(labelRect, GetFpvDirectionLabelText(signedAngle), style);
        GUI.color = oldColor;
    }

    private static string GetFpvDirectionLabelText(float signedAngle)
    {
        var absAngle = Mathf.Abs(signedAngle);
        if (absAngle <= 28f)
            return "VOR DIR";
        if (absAngle >= 145f)
            return "UMDREHEN";
        return signedAngle > 0f ? "RECHTS" : "LINKS";
    }

    private static Color GetFpvDirectionArrowColor(float signedAngle, Color normalColor)
    {
        var absAngle = Mathf.Abs(signedAngle);
        if (absAngle <= 28f)
            return new Color(0.35f, 1f, 0.45f);
        if (absAngle >= 145f)
            return new Color(1f, 0.42f, 0.05f);
        return normalColor;
    }

    private Texture2D GetFpvDirectionArrowTexture()
    {
        if (fpvDirectionArrowTexture != null)
            return fpvDirectionArrowTexture;

        const int size = 64;
        var texture = new Texture2D(size, size, TextureFormat.RGBA32, false)
        {
            hideFlags = HideFlags.HideAndDontSave,
            filterMode = FilterMode.Bilinear,
            wrapMode = TextureWrapMode.Clamp,
        };

        var pixels = new Color32[size * size];
        var transparent = new Color32(0, 0, 0, 0);
        var outline = new Color32(36, 30, 8, 255);
        var fill = new Color32(255, 255, 255, 255);

        for (var y = 0; y < size; y++)
        {
            for (var x = 0; x < size; x++)
            {
                var px = x + 0.5f;
                var py = y + 0.5f;
                var pixelIndex = y * size + x;

                if (IsFpvArrowInnerPixel(px, py))
                    pixels[pixelIndex] = fill;
                else if (IsFpvArrowOuterPixel(px, py))
                    pixels[pixelIndex] = outline;
                else
                    pixels[pixelIndex] = transparent;
            }
        }

        texture.SetPixels32(pixels);
        texture.Apply(false, true);
        fpvDirectionArrowTexture = texture;
        return fpvDirectionArrowTexture;
    }

    private static bool IsFpvArrowOuterPixel(float x, float y)
    {
        return IsPointInTriangle(x, y, 32f, 62f, 7f, 32f, 57f, 32f)
               || (x >= 22f && x <= 42f && y >= 2f && y <= 37f);
    }

    private static bool IsFpvArrowInnerPixel(float x, float y)
    {
        return IsPointInTriangle(x, y, 32f, 56f, 16f, 35f, 48f, 35f)
               || (x >= 27f && x <= 37f && y >= 8f && y <= 36f);
    }

    private static bool IsPointInTriangle(float px, float py,
        float ax, float ay, float bx, float by, float cx, float cy)
    {
        var d1 = TriangleSign(px, py, ax, ay, bx, by);
        var d2 = TriangleSign(px, py, bx, by, cx, cy);
        var d3 = TriangleSign(px, py, cx, cy, ax, ay);

        var hasNegative = d1 < 0f || d2 < 0f || d3 < 0f;
        var hasPositive = d1 > 0f || d2 > 0f || d3 > 0f;
        return !(hasNegative && hasPositive);
    }

    private static float TriangleSign(float px, float py, float ax, float ay, float bx, float by)
    {
        return (px - bx) * (ay - by) - (ax - bx) * (py - by);
    }

    private string GetSpatialTargetLabel()
    {
        if (spatialSelectionState == FunctionalMldsSpatialTargetStates.Resolved
            && selectedSpatialTarget != null)
        {
            return $"{selectedSpatialTarget.DisplayName} "
                + $"[{selectedSpatialTarget.SourceObjectId}]";
        }
        if (spatialSelectionState == FunctionalMldsSpatialTargetStates.Ambiguous)
        {
            return "mehrdeutig – " + spatialSelectionReason;
        }
        return "keines";
    }

    private void DrawSpatialTargetHud()
    {
        var width = Mathf.Min(680f, Screen.width - 20f);
        var style = new GUIStyle(GUI.skin.box)
        {
            fontSize = 13,
            fontStyle = FontStyle.Bold,
            alignment = TextAnchor.MiddleCenter
        };
        if (spatialSelectionState == FunctionalMldsSpatialTargetStates.Resolved)
            style.normal.textColor = selectedSpatialTargetColor;
        else if (spatialSelectionState == FunctionalMldsSpatialTargetStates.Ambiguous)
            style.normal.textColor = new Color(1f, 0.45f, 0.25f);
        else
            style.normal.textColor = new Color(0.82f, 0.82f, 0.82f);

        GUI.Box(
            new Rect(Screen.width * 0.5f - width * 0.5f, 12f, width, 28f),
            "Raumziel: " + GetSpatialTargetLabel(),
            style);
    }

    private void DrawFpvHud()
    {
        var sw = Screen.width;
        var sh = Screen.height;

        // Crosshair dot
        if (!_fpvChatOpen)
        {
            const int dotSize = 6;
            GUI.DrawTexture(
                new Rect(sw * 0.5f - dotSize * 0.5f, sh * 0.5f - dotSize * 0.5f, dotSize, dotSize),
                Texture2D.whiteTexture, ScaleMode.StretchToFill, false, 0f, Color.white, 0f, 0f);
        }

        DrawSpatialTargetHud();

        // Direction arrow toward pending handoff agent
        DrawFpvDirectionArrow();

        // Nearby agent nameplate
        if (!string.IsNullOrEmpty(_fpvNearestAgentId))
        {
            var agentName = _fpvNearestAgentId;
            if (lastAgents != null)
            {
                foreach (var a in lastAgents)
                {
                    if (a.id == _fpvNearestAgentId)
                    {
                        agentName = string.IsNullOrEmpty(a.display_name) ? a.id : a.display_name;
                        break;
                    }
                }
            }

            var isPendingArrival = _fpvNearestAgentId == _pendingHandoffAgentId
                                   && !string.IsNullOrEmpty(_pendingHandoffAgentId);
            var plateStyle = new GUIStyle(GUI.skin.box) { fontSize = 14, alignment = TextAnchor.MiddleCenter };
            plateStyle.normal.textColor = isPendingArrival ? new Color(1f, 0.85f, 0.2f) : Color.white;
            string plateText;
            if (_fpvChatOpen)
                plateText = agentName;
            else if (isPendingArrival)
                plateText = $"★  {agentName}  —  wartet auf dich";
            else
                plateText = $"{agentName}   [{fpvChatKey} = Chat]  [{voiceRecordKey} halten = Sprechen]";
            var plateWidth = Mathf.Min(620f, sw - 20f);
            var plateY = _fpvChatOpen ? sh - 204f : sh - 68f;
            GUI.Box(new Rect(sw * 0.5f - plateWidth * 0.5f, plateY, plateWidth, 28f), plateText, plateStyle);
        }

        // Chat overlay
        if (_fpvChatOpen)
        {
            const float panelW = 560f;
            const float panelH = 110f;
            var panelX = sw * 0.5f - panelW * 0.5f;
            var panelY = sh - panelH - 60f;

            // Handle Enter / Esc BEFORE the TextField consumes the event
            var ev = Event.current;
            if (ev.type == EventType.KeyDown)
            {
                if (ev.keyCode == KeyCode.Return || ev.keyCode == KeyCode.KeypadEnter)
                {
                    SendFpvChat();
                    ev.Use();
                }
                else if (ev.keyCode == KeyCode.Escape)
                {
                    _fpvChatOpen = false;
                    _fpvChatInput = "";
                    Cursor.lockState = CursorLockMode.Locked;
                    Cursor.visible = false;
                    ev.Use();
                    return; // skip rest of HUD this frame
                }
            }

            GUI.Box(new Rect(panelX - 4f, panelY - 4f, panelW + 8f, panelH + 8f), GUIContent.none);

            var agentName = _fpvNearestAgentId;
            if (lastAgents != null)
            {
                foreach (var a in lastAgents)
                {
                    if (a.id == _fpvNearestAgentId)
                    {
                        agentName = string.IsNullOrEmpty(a.display_name) ? a.id : a.display_name;
                        break;
                    }
                }
            }

            var labelStyle = new GUIStyle(GUI.skin.label) { fontSize = 12 };
            labelStyle.normal.textColor = new Color(0.8f, 0.8f, 0.8f);
            GUI.Label(new Rect(panelX, panelY + 2f, panelW, 20f),
                $"Gespräch mit: {agentName}  |  Enter = Senden  |  Esc = Schließen", labelStyle);

            GUI.SetNextControlName(FpvChatControlName);
            _fpvChatInput = GUI.TextField(
                new Rect(panelX, panelY + 24f, panelW - 90f, 32f), _fpvChatInput, 512);

            // Request focus only on the frame the chat was opened
            if (_fpvChatJustOpened)
            {
                GUI.FocusControl(FpvChatControlName);
                _fpvChatJustOpened = false;
            }

            if (GUI.Button(new Rect(panelX + panelW - 86f, panelY + 24f, 86f, 32f), "Senden"))
                SendFpvChat();

            // Last two chat lines for context. In private-memory mode this is scoped to the current FPV agent.
            var logStyle = new GUIStyle(GUI.skin.label) { fontSize = 11, wordWrap = true };
            logStyle.normal.textColor = new Color(0.9f, 0.9f, 0.9f);
            var recent = GetRecentFpvChatLines(2);
            GUI.Label(new Rect(panelX, panelY + 62f, panelW, 40f),
                string.Join("\n", recent), logStyle);
        }

        // Pending handoff indicator — pulsing banner when target is not yet in range
        if (!string.IsNullOrEmpty(_pendingHandoffAgentId) && _fpvNearestAgentId != _pendingHandoffAgentId)
        {
            var pendingName = _pendingHandoffAgentId;
            if (lastAgents != null)
            {
                foreach (var a in lastAgents)
                {
                    if (a.id == _pendingHandoffAgentId)
                    {
                        pendingName = string.IsNullOrEmpty(a.display_name) ? a.id : a.display_name;
                        break;
                    }
                }
            }

            var pulse = Mathf.Sin(Time.time * 3f) * 0.25f + 0.75f;
            var oldColor = GUI.color;
            GUI.color = new Color(1f, 1f, 1f, pulse);

            var pendingStyle = new GUIStyle(GUI.skin.box)
            {
                fontSize  = 16,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter,
            };
            pendingStyle.normal.textColor = new Color(1f, 0.9f, 0.1f);
            var pendingY = (isVoiceRecording || sttInFlight) ? sh - 144f : sh - 104f;
            GUI.Box(new Rect(sw * 0.5f - 300f, pendingY, 600f, 36f),
                $"★   {pendingName} wartet auf dich  —  lauf hin!   ★", pendingStyle);

            GUI.color = oldColor;
        }

        // Bottom hint bar (hidden while chat is open)
        if (!_fpvChatOpen)
        {
            var hudStyle = new GUIStyle(GUI.skin.box) { fontSize = 13, alignment = TextAnchor.MiddleCenter };
            hudStyle.normal.textColor = Color.white;
            var hint = $"FPV-Modus  |  WASD = bewegen  QE = hoch/runter  Shift = schneller  |  {voiceRecordKey} halten = sprechen  |  {fpvToggleKey} = beenden";
            var hintWidth = Mathf.Min(780f, sw - 20f);
            GUI.Box(new Rect(sw * 0.5f - hintWidth * 0.5f, sh - 34f, hintWidth, 26f), hint, hudStyle);
        }

        if (isVoiceRecording || sttInFlight)
        {
            var voiceStyle = new GUIStyle(GUI.skin.box) { fontSize = 14, fontStyle = FontStyle.Bold, alignment = TextAnchor.MiddleCenter };
            voiceStyle.normal.textColor = isVoiceRecording ? new Color(1f, 0.9f, 0.2f) : new Color(0.55f, 0.85f, 1f);
            var voiceText = isVoiceRecording ? "Aufnahme laeuft... Taste loslassen zum Senden" : "Transkription laeuft...";
            GUI.Box(new Rect(sw * 0.5f - 210f, sh - 104f, 420f, 30f), voiceText, voiceStyle);
        }
    }

    private void SendFpvChat()
    {
        var text = _fpvChatInput.Trim();
        if (string.IsNullOrEmpty(text)) return;
        AddUserChatLine(text);
        _fpvChatInput = "";
        StartCoroutine(SendChat(text));
    }

    [System.Serializable]
    private class StructuredNpcReply
    {
        public string say;
        public string handoff_to;
        public string handoff_reason;
        public float confidence;
        public string antwort;
        public string rueckfrage;
    }
}
