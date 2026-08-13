using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using Newtonsoft.Json.Linq;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.EventSystems;
using UnityEngine.Playables;
using UnityEngine.Scripting;
using UnityEngine.UI;
using UnityEngine.XR;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;
using UnityEngine.InputSystem.UI;
using UnityEngine.InputSystem.XR;
using NewInputDevice = UnityEngine.InputSystem.InputDevice;
#endif

/// <summary>
/// Participant-facing runtime for the fixed KAESESTEINPILZ IUI study.
///
/// This is deliberately a separate component. QuickAgentManager remains the single
/// communication/FunctionalMLDS implementation while this component supplies the
/// study configuration, responsive UI, FPV locomotion and cross-device input.
/// Keeping the protocol implementation central also means future communication fixes
/// automatically remain available to the study surface.
/// </summary>
[Preserve]
[DisallowMultipleComponent]
[RequireComponent(typeof(QuickAgentManager))]
[DefaultExecutionOrder(-10000)]
public sealed class KaesesteinpilzUserTestQuickAgentManager : MonoBehaviour
{
    public enum FlatControlMode
    {
        Computer,
        Smartphone
    }

    public const string StudyProjectId =
        "kaesestand_steinpilz_haptisch_chill_milcherlebnisraum_welcome_gruen_029e9a89";
    public const string StudyMemoryMode = "shared_history";
    public const string StudyScenePath = "Assets/Scenes/SampleScene.unity";
    public const string SafeAnimationFolder = "Characters/Animations";

    private const BindingFlags CoreFlags =
        BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
    private const string PlayerRootName = "XR Origin (KAESESTEINPILZ User Test)";
    private const float AgentScanInterval = 0.2f;

    [Header("Core integration")]
    [SerializeField] private QuickAgentManager coreManager;
    [SerializeField] private string desktopBackendBaseUrl = "http://127.0.0.1:8787";
    [Tooltip("WebGL defaults to same-origin /api when this is empty. Use an HTTPS URL only.")]
    [SerializeField] private string webBackendBaseUrl = "";

    [Header("User test")]
    [SerializeField] private bool autoEnterFlatFpv = true;
    [SerializeField] private bool showIntroduction = true;
    [SerializeField] private bool recordAnonymousStudyEvents = true;
    [SerializeField] private FlatControlMode flatControlMode = FlatControlMode.Computer;

    [Header("FPV")]
    [SerializeField, Min(0.5f)] private float moveSpeed = 2.6f;
    [SerializeField, Min(1f)] private float sprintMultiplier = 1.65f;
    [SerializeField, Range(0.02f, 1f)] private float mouseLookSensitivity = 0.12f;
    [SerializeField, Range(0.02f, 1f)] private float touchLookSensitivity = 0.16f;
    [SerializeField, Range(20f, 89f)] private float pitchLimit = 78f;
    [SerializeField, Min(0.5f)] private float eyeHeight = 1.68f;
    [SerializeField, Min(0.05f)] private float gravity = 18f;

    [Header("Study task")]
    [TextArea(2, 5)]
    [SerializeField] private string taskText =
        "Erkunde den KÄSESTEINPILZ-Raum. Sprich mit mindestens zwei Agent:innen " +
        "und untersuche mindestens ein Objekt.";

    public QuickAgentManager CoreManager => coreManager;
    public bool IsReady { get; private set; }
    public bool IsImmersiveXr => xrActive;
    public bool UsesTouchLayout => touchLayout;
    public FlatControlMode SelectedFlatControlMode => flatControlMode;
    public string ParticipantCode => participantCode;
    public string ResolvedBackendBaseUrl { get; private set; }

    private Camera playerCamera;
    private GameObject playerRoot;
    private CharacterController characterController;
    private float yaw;
    private float pitch;
    private float verticalVelocity;
    private bool participantStarted;
    private bool studyFinished;
    private bool touchLayout;
    private bool xrActive;
    private bool pointerLocked;
    private bool lastXrTrigger;
    private bool lastXrPrimaryButton;
    private bool awaitingVoiceTranscript;
    private float nextXrSnapTurnAt;
    private float nextAgentScanAt;
    private float nextPoseScanAt;
    private int lastWebXrState = -1;
    private int lastScreenWidth;
    private int lastScreenHeight;
    private Rect lastSafeArea;
    private Vector2 touchMove;
    private Vector2 queuedLookDelta;
    private string participantCode;
    private string studyLogPath;
    private string lastTranscript = "";
    private string lastStatus = "";
    private string lastProximityAgentId = "";
    private string lastPendingHandoffAgentId = "";
    private int successfulInteractions;
    private bool inspectedObject;
    private readonly HashSet<string> contactedAgents = new HashSet<string>();
    private readonly HashSet<GameObject> knownAgentRoots = new HashSet<GameObject>();
    private readonly Dictionary<string, MethodInfo> methodCache = new Dictionary<string, MethodInfo>();

    private Canvas canvas;
    private RectTransform canvasRect;
    private RectTransform safeAreaRoot;
    private RectTransform headerPanel;
    private RectTransform taskPanel;
    private RectTransform chatPanel;
    private RectTransform moveControlRoot;
    private RectTransform lookControlRoot;
    private RectTransform introductionCard;
    private RectTransform completionCard;
    private GameObject introductionOverlay;
    private GameObject completionOverlay;
    private GameObject crosshair;
    private RectTransform handoffIndicator;
    private RectTransform handoffArrowGlyph;
    private Text handoffTargetLabel;
    private Text statusLabel;
    private Text agentLabel;
    private Text taskLabel;
    private Text transcriptLabel;
    private Text micButtonLabel;
    private Text completionLabel;
    private Text toastLabel;
    private Text controlModeButtonLabel;
    private InputField chatInput;
    private ScrollRect transcriptScroll;
    private Button micButton;
    private Button retryButton;
    private Button controlModeButton;
    private Font uiFont;
    private IuiStudyVirtualStick moveStick;
    private IuiStudyLookSurface lookSurface;
    private Coroutine toastCoroutine;
    private Camera xrUiRayCamera;
    private GameObject xrUiHover;

#if ENABLE_INPUT_SYSTEM
    private TrackedPoseDriver trackedPoseDriver;
    private InputAction xrHeadPositionAction;
    private InputAction xrHeadRotationAction;
#endif

    private sealed class PoseWatch
    {
        public GameObject root;
        public SkinnedMeshRenderer[] renderers;
        public Animator animator;
        public PlayableGraph graph;
        public AnimationClipPlayable playable;
        public AnimationClip clip;
        public double clipTime;
    }

    private readonly Dictionary<GameObject, PoseWatch> poseWatches =
        new Dictionary<GameObject, PoseWatch>();
    private AnimationClip[] safeIdleClips;

    [Serializable]
    private sealed class StudyLogEntry
    {
        public string utc;
        public string participant;
        public string event_name;
        public string modality;
        public string agent_id;
        public string target_id;
        public int value;
        public float seconds;
    }

    private void Awake()
    {
        coreManager = coreManager != null ? coreManager : GetComponent<QuickAgentManager>();
        if (coreManager == null)
        {
            enabled = false;
            return;
        }

        ConfigureCoreForStudy();
        touchLayout = flatControlMode == FlatControlMode.Smartphone;
        participantCode = "IUI-" + Guid.NewGuid().ToString("N").Substring(0, 8).ToUpperInvariant();
        studyLogPath = Path.Combine(
            Application.persistentDataPath,
            "kaesesteinpilz-user-test-" + participantCode + ".jsonl");

        // QAM picks character/idle combinations during Start. A stable seed keeps study
        // sessions visually reproducible while the dedicated folder excludes bind clips.
        UnityEngine.Random.InitState(StableHash(StudyProjectId));
    }

    private void Start()
    {
        EnsurePlayerRig();
        BuildInterface();
        SubscribeCoreEvents();
        LogStudyEvent("runtime_started", CurrentModality(), "", "", 0);

        if (!showIntroduction)
        {
            BeginParticipantSession();
        }
        else
        {
            SetPointerLock(false);
        }
    }

    private void OnEnable()
    {
    }

    private void OnDisable()
    {
        UnsubscribeCoreEvents();
        SetPointerLock(false);
    }

    private void OnDestroy()
    {
        foreach (var watch in poseWatches.Values)
        {
            if (watch != null && watch.graph.IsValid())
                watch.graph.Destroy();
        }
        poseWatches.Clear();

#if ENABLE_INPUT_SYSTEM
        if (xrHeadPositionAction != null)
        {
            xrHeadPositionAction.Dispose();
            xrHeadPositionAction = null;
        }
        if (xrHeadRotationAction != null)
        {
            xrHeadRotationAction.Dispose();
            xrHeadRotationAction = null;
        }
#endif
        if (xrUiRayCamera != null)
            Destroy(xrUiRayCamera.gameObject);
    }

    /// <summary>Applies the immutable study contract before QuickAgentManager.Start runs.</summary>
    public void ConfigureCoreForStudy()
    {
        if (coreManager == null)
            return;

        ResolvedBackendBaseUrl = ResolveBackendBaseUrl(
            desktopBackendBaseUrl,
            webBackendBaseUrl,
            Application.absoluteURL,
            IsWebRuntime());

        coreManager.backendBaseUrl = ResolvedBackendBaseUrl;
        coreManager.memoryMode = StudyMemoryMode;
        coreManager.animationResourceFolder = SafeAnimationFolder;
        coreManager.showUi = false;
        coreManager.showAgentBubbles = false;
        coreManager.enableFreeMovement = false;
        coreManager.enableVoiceInput = false; // The new mic button owns recording state.
        // Voice transcription is still provided by QAM, but this component sends the
        // resulting text through its navigation-aware chat coroutine.
        coreManager.sendVoiceTranscriptAutomatically = false;
        // The participant surface owns pointer routing so UI taps cannot leak through to
        // QAM's legacy global mouse selector. SelectRay enables the resolver atomically.
        coreManager.enableSpatialTargetSelection = false;
        coreManager.fpvToggleKey = KeyCode.None;
        coreManager.moveXrOriginInsteadOfCamera = true;

        SetCoreField("useProjectSelection", true);
        SetCoreField("selectedProjectId", StudyProjectId);
        SetCoreField("selectedProjectIndex", -1);
        SetCoreField("_fpvActive", false);
        SetCoreField("_fpvChatOpen", false);
    }

    public static string ResolveBackendBaseUrl(
        string desktopBaseUrl,
        string configuredWebBaseUrl,
        string absoluteUrl,
        bool webRuntime)
    {
        if (!webRuntime)
            return TrimTrailingSlash(string.IsNullOrWhiteSpace(desktopBaseUrl)
                ? "http://127.0.0.1:8787"
                : desktopBaseUrl.Trim());

        var queryOverride = ReadQueryValue(absoluteUrl, "backend");
        if (!string.IsNullOrWhiteSpace(queryOverride))
            return TrimTrailingSlash(queryOverride.Trim());

        if (!string.IsNullOrWhiteSpace(configuredWebBaseUrl))
            return TrimTrailingSlash(configuredWebBaseUrl.Trim());

        if (Uri.TryCreate(absoluteUrl, UriKind.Absolute, out var pageUri))
        {
            // Local WebGL preview servers normally do not proxy /api. Keep the
            // backend on its configured localhost port while developing.
            if (pageUri.IsLoopback && !string.IsNullOrWhiteSpace(desktopBaseUrl))
                return TrimTrailingSlash(desktopBaseUrl.Trim());

            return TrimTrailingSlash(pageUri.GetLeftPart(UriPartial.Authority)) + "/api";
        }

        return "/api";
    }

    private static string ReadQueryValue(string absoluteUrl, string key)
    {
        if (!Uri.TryCreate(absoluteUrl, UriKind.Absolute, out var uri)
            || string.IsNullOrEmpty(uri.Query))
            return "";

        var pairs = uri.Query.TrimStart('?').Split('&');
        foreach (var pair in pairs)
        {
            var parts = pair.Split(new[] { '=' }, 2);
            if (parts.Length == 2
                && string.Equals(Uri.UnescapeDataString(parts[0]), key, StringComparison.OrdinalIgnoreCase))
                return Uri.UnescapeDataString(parts[1].Replace('+', ' '));
        }
        return "";
    }

    private static string TrimTrailingSlash(string value)
    {
        return (value ?? "").TrimEnd('/');
    }

    private static bool IsWebRuntime()
    {
#if UNITY_WEBGL && !UNITY_EDITOR
        return true;
#else
        return false;
#endif
    }

    private void Update()
    {
        PollWebXrState();
        UpdateResponsiveLayoutIfNeeded();
        UpdateRuntimeState();
        ForwardCompletedVoiceTranscript();
        EnforceVoiceRecordingLimit();
        UpdateInterfaceText();
        UpdateMicButton();
        UpdatePendingHandoffNavigation();

        // Keep the immersive UI ray alive during onboarding and connection errors;
        // otherwise a participant who enters VR from the browser would have no way to
        // press the start/retry buttons. World interaction, voice and locomotion stay gated.
        var participantCanInteract = participantStarted && IsReady && !studyFinished;
        if (xrActive)
            UpdateXrInput(participantCanInteract);

        if (studyFinished || !participantStarted || !IsReady)
            return;

        if (!xrActive)
            UpdateFlatInput();

        UpdateMovement();
        UpdateNearestAgent();
    }

    private void LateUpdate()
    {
        AdvanceStudyIdleAnimations();
        DiscoverAndGuardAgentPoses();
    }

    private void UpdateRuntimeState()
    {
        if (coreManager == null)
            return;

        if (!IsReady
            && !string.IsNullOrWhiteSpace(coreManager.sessionId)
            && GetAgentRoots().Count > 0)
        {
            IsReady = true;
            retryButton.gameObject.SetActive(false);
            if (autoEnterFlatFpv && !xrActive)
                PositionAtStudyStart();
            ShowToast("Bereit – nähere dich einer Person oder untersuche ein Objekt.", 4f);
            LogStudyEvent("setup_ready", CurrentModality(), coreManager.activeAgentId, "", 0);
        }

        var coreStatus = GetCoreField<string>("statusMessage") ?? "";
        var failed = coreStatus.IndexOf("fehlgeschlagen", StringComparison.OrdinalIgnoreCase) >= 0
            || coreStatus.IndexOf("blockiert", StringComparison.OrdinalIgnoreCase) >= 0;
        if (retryButton != null)
            retryButton.gameObject.SetActive(!IsReady && failed);
    }

    private void EnsurePlayerRig()
    {
        playerCamera = Camera.main;
        if (playerCamera == null)
        {
            var cameraObject = new GameObject("Main Camera", typeof(Camera), typeof(AudioListener));
            cameraObject.tag = "MainCamera";
            playerCamera = cameraObject.GetComponent<Camera>();
        }

        playerRoot = GameObject.Find(PlayerRootName);
        if (playerRoot == null)
            playerRoot = new GameObject(PlayerRootName);

        var initialPosition = playerCamera.transform.position;
        playerRoot.transform.position = new Vector3(initialPosition.x, 0f, initialPosition.z);
        playerRoot.transform.rotation = Quaternion.identity;
        playerCamera.transform.SetParent(playerRoot.transform, false);
        playerCamera.transform.localPosition = new Vector3(0f, eyeHeight, 0f);
        playerCamera.transform.localRotation = Quaternion.identity;

        characterController = playerRoot.GetComponent<CharacterController>();
        if (characterController == null)
            characterController = playerRoot.AddComponent<CharacterController>();
        characterController.height = Mathf.Max(1.2f, eyeHeight);
        characterController.radius = 0.28f;
        characterController.center = new Vector3(0f, characterController.height * 0.5f, 0f);
        characterController.stepOffset = 0.28f;
        characterController.slopeLimit = 50f;

#if ENABLE_INPUT_SYSTEM
        trackedPoseDriver = playerCamera.GetComponent<TrackedPoseDriver>();
        if (trackedPoseDriver == null)
            trackedPoseDriver = playerCamera.gameObject.AddComponent<TrackedPoseDriver>();
        trackedPoseDriver.enabled = false;
        trackedPoseDriver.trackingType = TrackedPoseDriver.TrackingType.RotationAndPosition;
        trackedPoseDriver.ignoreTrackingState = true;

        xrHeadPositionAction = new InputAction(
            "WebXR HMD Position",
            InputActionType.Value,
            "<XRHMD>/centerEyePosition",
            expectedControlType: "Vector3");
        xrHeadRotationAction = new InputAction(
            "WebXR HMD Rotation",
            InputActionType.Value,
            "<XRHMD>/centerEyeRotation",
            expectedControlType: "Quaternion");
        trackedPoseDriver.positionInput = new InputActionProperty(xrHeadPositionAction);
        trackedPoseDriver.rotationInput = new InputActionProperty(xrHeadRotationAction);
#endif

        TryAddWebXrCameraSettings(playerCamera);
        TryEnsureWebXrInputSystem();
    }

    private void PositionAtStudyStart()
    {
        var roots = GetAgentRoots();
        if (roots.Count == 0 || playerRoot == null)
            return;

        GameObject welcome = null;
        foreach (var pair in roots)
        {
            if (string.Equals(pair.Key, "welcome_host", StringComparison.OrdinalIgnoreCase))
            {
                welcome = pair.Value;
                break;
            }
        }
        welcome = welcome != null ? welcome : FirstAgentRoot(roots);
        if (welcome == null)
            return;

        var facing = welcome.transform.forward;
        facing.y = 0f;
        if (facing.sqrMagnitude < 0.01f)
            facing = Vector3.forward;
        facing.Normalize();

        if (characterController != null)
            characterController.enabled = false;
        playerRoot.transform.position = welcome.transform.position + facing * 2.25f;
        var look = welcome.transform.position + Vector3.up * 1.45f - playerCamera.transform.position;
        yaw = Quaternion.LookRotation(new Vector3(look.x, 0f, look.z).normalized).eulerAngles.y;
        pitch = Mathf.Clamp(-Mathf.Atan2(look.y, Mathf.Max(0.01f, new Vector2(look.x, look.z).magnitude))
            * Mathf.Rad2Deg, -pitchLimit, pitchLimit);
        playerRoot.transform.rotation = Quaternion.Euler(0f, yaw, 0f);
        playerCamera.transform.localRotation = Quaternion.Euler(pitch, 0f, 0f);
        if (characterController != null)
            characterController.enabled = true;
    }

    private static GameObject FirstAgentRoot(Dictionary<string, GameObject> roots)
    {
        foreach (var pair in roots)
            return pair.Value;
        return null;
    }

    private void BuildInterface()
    {
        uiFont = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        EnsureEventSystem();

        var canvasObject = NewUiObject("KAESESTEINPILZ Study UI", transform);
        canvas = canvasObject.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 100;
        var scaler = canvasObject.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1280f, 720f);
        scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
        scaler.matchWidthOrHeight = 0.5f;
        canvasObject.AddComponent<GraphicRaycaster>();
        canvasRect = canvasObject.GetComponent<RectTransform>();

        safeAreaRoot = NewUiObject("Safe Area", canvas.transform).GetComponent<RectTransform>();
        Stretch(safeAreaRoot);

        headerPanel = CreatePanel("Header", safeAreaRoot, new Color(0.08f, 0.16f, 0.12f, 0.96f));
        var brand = CreateText("Brand", headerPanel, "KÄSESTEINPILZ  ·  IUI USER STUDY", 20,
            FontStyle.Bold, TextAnchor.MiddleLeft, new Color(1f, 0.94f, 0.76f));
        SetRect(brand.rectTransform, new Vector2(0.03f, 0f), new Vector2(0.48f, 1f));
        statusLabel = CreateText("Status", headerPanel, "Verbindung wird aufgebaut …", 15,
            FontStyle.Normal, TextAnchor.MiddleRight, Color.white);
        SetRect(statusLabel.rectTransform, new Vector2(0.47f, 0f), new Vector2(0.78f, 1f));
        controlModeButton = CreateButton("Control mode", headerPanel, "PC", new Color(0.24f, 0.38f, 0.30f));
        controlModeButtonLabel = controlModeButton.GetComponentInChildren<Text>();
        SetRect(controlModeButton.GetComponent<RectTransform>(), new Vector2(0.80f, 0.14f), new Vector2(0.97f, 0.86f));
        controlModeButton.onClick.AddListener(ToggleFlatControlMode);

        taskPanel = CreatePanel("Task", safeAreaRoot, new Color(0.97f, 0.93f, 0.80f, 0.96f));
        var taskHeading = CreateText("Task heading", taskPanel, "DEINE AUFGABE", 15,
            FontStyle.Bold, TextAnchor.UpperLeft, new Color(0.23f, 0.19f, 0.11f));
        SetRect(taskHeading.rectTransform, new Vector2(0.06f, 0.72f), new Vector2(0.94f, 0.94f));
        taskLabel = CreateText("Task text", taskPanel, taskText, 15,
            FontStyle.Normal, TextAnchor.UpperLeft, new Color(0.17f, 0.14f, 0.09f));
        SetRect(taskLabel.rectTransform, new Vector2(0.06f, 0.12f), new Vector2(0.94f, 0.73f));
        taskLabel.resizeTextForBestFit = true;
        taskLabel.resizeTextMinSize = 11;
        taskLabel.resizeTextMaxSize = 15;

        chatPanel = CreatePanel("Conversation", safeAreaRoot, new Color(0.055f, 0.075f, 0.065f, 0.94f));
        agentLabel = CreateText("Agent", chatPanel, "Agent: wird geladen …", 18,
            FontStyle.Bold, TextAnchor.MiddleLeft, new Color(0.97f, 0.81f, 0.31f));
        SetRect(agentLabel.rectTransform, new Vector2(0.05f, 0.89f), new Vector2(0.95f, 0.98f));

        transcriptScroll = CreateTranscript(chatPanel);
        SetRect(transcriptScroll.GetComponent<RectTransform>(), new Vector2(0.04f, 0.31f), new Vector2(0.96f, 0.88f));

        chatInput = CreateInputField(chatPanel);
        SetRect(chatInput.GetComponent<RectTransform>(), new Vector2(0.04f, 0.18f), new Vector2(0.75f, 0.29f));
        chatInput.onEndEdit.AddListener(HandleInputEndEdit);
        var send = CreateButton("Send", chatPanel, "SENDEN", new Color(0.91f, 0.62f, 0.16f));
        SetRect(send.GetComponent<RectTransform>(), new Vector2(0.77f, 0.18f), new Vector2(0.96f, 0.29f));
        send.onClick.AddListener(SendCurrentMessage);

        micButton = CreateButton("Microphone", chatPanel, "MIKRO", new Color(0.16f, 0.45f, 0.31f));
        micButtonLabel = micButton.GetComponentInChildren<Text>();
        SetRect(micButton.GetComponent<RectTransform>(), new Vector2(0.04f, 0.04f), new Vector2(0.27f, 0.15f));
        micButton.onClick.AddListener(ToggleVoiceRecording);

        var interact = CreateButton("Interact", chatPanel, "ANSEHEN", new Color(0.15f, 0.48f, 0.54f));
        SetRect(interact.GetComponent<RectTransform>(), new Vector2(0.29f, 0.04f), new Vector2(0.53f, 0.15f));
        interact.onClick.AddListener(SelectAtViewCenter);

        var help = CreateButton("Help", chatPanel, "HILFE", new Color(0.28f, 0.30f, 0.27f));
        SetRect(help.GetComponent<RectTransform>(), new Vector2(0.55f, 0.04f), new Vector2(0.73f, 0.15f));
        help.onClick.AddListener(ShowHelp);

        var finish = CreateButton("Finish", chatPanel, "FERTIG", new Color(0.52f, 0.23f, 0.16f));
        SetRect(finish.GetComponent<RectTransform>(), new Vector2(0.75f, 0.04f), new Vector2(0.96f, 0.15f));
        finish.onClick.AddListener(FinishStudy);

        retryButton = CreateButton("Retry", safeAreaRoot, "ERNEUT VERBINDEN", new Color(0.66f, 0.24f, 0.18f));
        SetRect(retryButton.GetComponent<RectTransform>(), new Vector2(0.38f, 0.46f), new Vector2(0.62f, 0.54f));
        retryButton.onClick.AddListener(RetrySetup);
        retryButton.gameObject.SetActive(false);

        crosshair = NewUiObject("Crosshair", safeAreaRoot);
        var crosshairImage = crosshair.AddComponent<Image>();
        crosshairImage.color = new Color(1f, 0.91f, 0.55f, 0.85f);
        var crosshairRect = crosshair.GetComponent<RectTransform>();
        crosshairRect.anchorMin = crosshairRect.anchorMax = new Vector2(0.5f, 0.5f);
        crosshairRect.sizeDelta = new Vector2(7f, 7f);

        BuildHandoffIndicator();

        moveControlRoot = CreatePanel("Move touch control", safeAreaRoot, new Color(1f, 1f, 1f, 0.08f));
        moveStick = moveControlRoot.gameObject.AddComponent<IuiStudyVirtualStick>();
        moveStick.ValueChanged += value => touchMove = value;
        CreateText("Move label", moveControlRoot, "BEWEGEN", 13, FontStyle.Bold,
            TextAnchor.MiddleCenter, new Color(1f, 1f, 1f, 0.55f));

        lookControlRoot = CreatePanel("Look touch control", safeAreaRoot, new Color(1f, 1f, 1f, 0.06f));
        lookSurface = lookControlRoot.gameObject.AddComponent<IuiStudyLookSurface>();
        lookSurface.Dragged += delta => queuedLookDelta += delta;
        lookSurface.Tapped += SelectAtScreenPoint;
        CreateText("Look label", lookControlRoot, "BLICK  ·  TIPPEN = AUSWÄHLEN", 12, FontStyle.Bold,
            TextAnchor.MiddleCenter, new Color(1f, 1f, 1f, 0.48f));

        toastLabel = CreateText("Toast", safeAreaRoot, "", 16, FontStyle.Bold,
            TextAnchor.MiddleCenter, Color.white);
        toastLabel.color = Color.white;
        var toastImage = toastLabel.gameObject.AddComponent<Outline>();
        toastImage.effectColor = new Color(0f, 0f, 0f, 0.8f);
        SetRect(toastLabel.rectTransform, new Vector2(0.25f, 0.52f), new Vector2(0.75f, 0.60f));
        toastLabel.gameObject.SetActive(false);

        BuildIntroduction();
        BuildCompletion();
        UpdateControlModeButton();
        UpdateResponsiveLayout(true);
    }

    private void BuildHandoffIndicator()
    {
        handoffIndicator = NewUiObject("Handoff direction", safeAreaRoot).GetComponent<RectTransform>();
        handoffIndicator.anchorMin = handoffIndicator.anchorMax = new Vector2(0.5f, 0.5f);
        handoffIndicator.pivot = new Vector2(0.5f, 0.5f);
        handoffIndicator.sizeDelta = new Vector2(190f, 112f);

        var arrow = CreateText("Arrow", handoffIndicator, "▲", 54, FontStyle.Bold,
            TextAnchor.MiddleCenter, new Color(1f, 0.78f, 0.15f));
        handoffArrowGlyph = arrow.rectTransform;
        SetRect(handoffArrowGlyph, new Vector2(0.30f, 0.38f), new Vector2(0.70f, 1f));
        var arrowOutline = arrow.gameObject.AddComponent<Outline>();
        arrowOutline.effectColor = new Color(0f, 0f, 0f, 0.85f);
        arrowOutline.effectDistance = new Vector2(2f, -2f);

        handoffTargetLabel = CreateText("Target", handoffIndicator, "", 14,
            FontStyle.Bold, TextAnchor.MiddleCenter, Color.white);
        SetRect(handoffTargetLabel.rectTransform, new Vector2(0f, 0f), new Vector2(1f, 0.40f));
        var labelOutline = handoffTargetLabel.gameObject.AddComponent<Outline>();
        labelOutline.effectColor = new Color(0f, 0f, 0f, 0.95f);
        labelOutline.effectDistance = new Vector2(1.5f, -1.5f);
        handoffIndicator.gameObject.SetActive(false);
    }

    private void BuildIntroduction()
    {
        introductionOverlay = NewUiObject("Introduction overlay", canvas.transform);
        Stretch(introductionOverlay.GetComponent<RectTransform>());
        var dim = introductionOverlay.AddComponent<Image>();
        dim.color = new Color(0.025f, 0.045f, 0.035f, 0.76f);

        introductionCard = CreatePanel("Introduction card", introductionOverlay.transform,
            new Color(0.97f, 0.93f, 0.80f, 1f));
        var title = CreateText("Introduction title", introductionCard,
            "Willkommen im KÄSESTEINPILZ", 30, FontStyle.Bold, TextAnchor.MiddleCenter,
            new Color(0.16f, 0.25f, 0.18f));
        SetRect(title.rectTransform, new Vector2(0.06f, 0.76f), new Vector2(0.94f, 0.94f));

        var body = CreateText("Introduction body", introductionCard,
            "Wähle die Steuerung selbst und erkunde dann den Raum.\n\n" +
            "Computer: WASD + Maus · T öffnet den Chat · V startet Sprache\n" +
            "Smartphone: linker Bereich bewegt · rechter Bereich dreht und wählt\n" +
            "WebXR: Controller bewegen, Trigger wählt; Voice bleibt verfügbar.\n\n" +
            "Für die Studie speichern wir nur anonyme Ereignisse und Zeiten – " +
            "keine Chattexte und keine Audiodateien.",
            17, FontStyle.Normal, TextAnchor.UpperLeft, new Color(0.14f, 0.13f, 0.10f));
        SetRect(body.rectTransform, new Vector2(0.08f, 0.34f), new Vector2(0.92f, 0.74f));

        var computer = CreateButton("Choose computer", introductionCard, "COMPUTER",
            new Color(0.19f, 0.36f, 0.27f));
        SetRect(computer.GetComponent<RectTransform>(), new Vector2(0.16f, 0.19f), new Vector2(0.48f, 0.30f));
        computer.onClick.AddListener(() => SetFlatControlMode(FlatControlMode.Computer));

        var smartphone = CreateButton("Choose smartphone", introductionCard, "SMARTPHONE",
            new Color(0.15f, 0.48f, 0.54f));
        SetRect(smartphone.GetComponent<RectTransform>(), new Vector2(0.52f, 0.19f), new Vector2(0.84f, 0.30f));
        smartphone.onClick.AddListener(() => SetFlatControlMode(FlatControlMode.Smartphone));

        var start = CreateButton("Start study", introductionCard, "TEILNAHME STARTEN",
            new Color(0.16f, 0.45f, 0.31f));
        SetRect(start.GetComponent<RectTransform>(), new Vector2(0.22f, 0.05f), new Vector2(0.78f, 0.15f));
        start.onClick.AddListener(BeginParticipantSession);
        introductionOverlay.SetActive(showIntroduction);
    }

    private void BuildCompletion()
    {
        completionOverlay = NewUiObject("Completion overlay", canvas.transform);
        Stretch(completionOverlay.GetComponent<RectTransform>());
        completionOverlay.AddComponent<Image>().color = new Color(0.025f, 0.045f, 0.035f, 0.95f);

        completionCard = CreatePanel("Completion card", completionOverlay.transform,
            new Color(0.97f, 0.93f, 0.80f, 1f));
        var title = CreateText("Completion title", completionCard, "Vielen Dank!", 34,
            FontStyle.Bold, TextAnchor.MiddleCenter, new Color(0.16f, 0.25f, 0.18f));
        SetRect(title.rectTransform, new Vector2(0.08f, 0.72f), new Vector2(0.92f, 0.92f));
        completionLabel = CreateText("Completion summary", completionCard, "", 19,
            FontStyle.Normal, TextAnchor.UpperCenter, new Color(0.14f, 0.13f, 0.10f));
        SetRect(completionLabel.rectTransform, new Vector2(0.08f, 0.22f), new Vector2(0.92f, 0.70f));
        completionOverlay.SetActive(false);
    }

    private void EnsureEventSystem()
    {
        var eventSystem = EventSystem.current;
        if (eventSystem == null)
        {
            var eventObject = new GameObject("EventSystem", typeof(EventSystem));
            eventSystem = eventObject.GetComponent<EventSystem>();
        }

#if ENABLE_INPUT_SYSTEM
        var module = eventSystem.GetComponent<InputSystemUIInputModule>();
        if (module == null)
            module = eventSystem.gameObject.AddComponent<InputSystemUIInputModule>();
        if (module.actionsAsset == null)
            module.AssignDefaultActions();
#else
        if (eventSystem.GetComponent<StandaloneInputModule>() == null)
            eventSystem.gameObject.AddComponent<StandaloneInputModule>();
#endif
    }

    private ScrollRect CreateTranscript(Transform parent)
    {
        var root = NewUiObject("Transcript scroll", parent);
        var scroll = root.AddComponent<ScrollRect>();
        scroll.horizontal = false;
        scroll.vertical = true;
        scroll.scrollSensitivity = 28f;

        var viewport = NewUiObject("Viewport", root.transform);
        Stretch(viewport.GetComponent<RectTransform>());
        viewport.AddComponent<Image>().color = new Color(1f, 1f, 1f, 0.035f);
        viewport.AddComponent<RectMask2D>();

        transcriptLabel = CreateText("Transcript", viewport.transform,
            "Die Unterhaltung erscheint hier.", 16, FontStyle.Normal,
            TextAnchor.UpperLeft, new Color(0.93f, 0.95f, 0.90f));
        var contentRect = transcriptLabel.rectTransform;
        contentRect.anchorMin = new Vector2(0f, 1f);
        contentRect.anchorMax = new Vector2(1f, 1f);
        contentRect.pivot = new Vector2(0.5f, 1f);
        contentRect.offsetMin = new Vector2(12f, 0f);
        contentRect.offsetMax = new Vector2(-12f, 0f);
        var fitter = transcriptLabel.gameObject.AddComponent<ContentSizeFitter>();
        fitter.verticalFit = ContentSizeFitter.FitMode.PreferredSize;
        scroll.viewport = viewport.GetComponent<RectTransform>();
        scroll.content = contentRect;
        return scroll;
    }

    private InputField CreateInputField(Transform parent)
    {
        var root = NewUiObject("Chat input", parent);
        var image = root.AddComponent<Image>();
        image.color = new Color(0.98f, 0.97f, 0.91f, 1f);
        var input = root.AddComponent<InputField>();
        input.lineType = InputField.LineType.SingleLine;
        input.characterLimit = 500;

        var text = CreateText("Text", root.transform, "", 16, FontStyle.Normal,
            TextAnchor.MiddleLeft, new Color(0.10f, 0.12f, 0.10f));
        SetRect(text.rectTransform, Vector2.zero, Vector2.one, new Vector2(14f, 3f), new Vector2(-10f, -3f));
        text.supportRichText = false;

        var placeholder = CreateText("Placeholder", root.transform, "Nachricht eingeben …", 16,
            FontStyle.Italic, TextAnchor.MiddleLeft, new Color(0.28f, 0.30f, 0.27f, 0.68f));
        SetRect(placeholder.rectTransform, Vector2.zero, Vector2.one, new Vector2(14f, 3f), new Vector2(-10f, -3f));

        input.textComponent = text;
        input.placeholder = placeholder;
        return input;
    }

    private void UpdateResponsiveLayoutIfNeeded()
    {
        if (Screen.width == lastScreenWidth
            && Screen.height == lastScreenHeight
            && Screen.safeArea == lastSafeArea)
            return;
        UpdateResponsiveLayout(false);
    }

    private void UpdateResponsiveLayout(bool force)
    {
        if (safeAreaRoot == null)
            return;

        lastScreenWidth = Mathf.Max(1, Screen.width);
        lastScreenHeight = Mathf.Max(1, Screen.height);
        lastSafeArea = Screen.safeArea;

        if (!xrActive)
        {
            var safe = Screen.safeArea;
            safeAreaRoot.anchorMin = new Vector2(safe.xMin / lastScreenWidth, safe.yMin / lastScreenHeight);
            safeAreaRoot.anchorMax = new Vector2(safe.xMax / lastScreenWidth, safe.yMax / lastScreenHeight);
            safeAreaRoot.offsetMin = safeAreaRoot.offsetMax = Vector2.zero;
        }
        else
        {
            safeAreaRoot.anchorMin = Vector2.zero;
            safeAreaRoot.anchorMax = Vector2.one;
            safeAreaRoot.offsetMin = safeAreaRoot.offsetMax = Vector2.zero;
        }

        touchLayout = flatControlMode == FlatControlMode.Smartphone;
        var portrait = lastScreenHeight > lastScreenWidth;

        if (xrActive)
        {
            SetRect(headerPanel, new Vector2(0.08f, 0.90f), new Vector2(0.92f, 0.975f));
            SetRect(taskPanel, new Vector2(0.05f, 0.68f), new Vector2(0.36f, 0.88f));
            SetRect(chatPanel, new Vector2(0.64f, 0.24f), new Vector2(0.95f, 0.88f));
        }
        else if (!touchLayout)
        {
            SetRect(headerPanel, new Vector2(0.02f, 0.925f), new Vector2(0.62f, 0.985f));
            SetRect(taskPanel, new Vector2(0.02f, 0.72f), new Vector2(0.27f, 0.91f));
            SetRect(chatPanel, new Vector2(0.74f, 0.30f), new Vector2(0.985f, 0.91f));
        }
        else if (portrait)
        {
            SetRect(headerPanel, new Vector2(0.03f, 0.91f), new Vector2(0.97f, 0.985f));
            SetRect(taskPanel, new Vector2(0.03f, 0.78f), new Vector2(0.97f, 0.895f));
            SetRect(chatPanel, new Vector2(0.03f, 0.48f), new Vector2(0.97f, 0.765f));
            SetRect(moveControlRoot, new Vector2(0.03f, 0.04f), new Vector2(0.42f, 0.30f));
            SetRect(lookControlRoot, new Vector2(0.58f, 0.04f), new Vector2(0.97f, 0.30f));
        }
        else
        {
            SetRect(headerPanel, new Vector2(0.02f, 0.91f), new Vector2(0.58f, 0.985f));
            SetRect(taskPanel, new Vector2(0.02f, 0.69f), new Vector2(0.28f, 0.89f));
            SetRect(chatPanel, new Vector2(0.72f, 0.36f), new Vector2(0.98f, 0.89f));
            SetRect(moveControlRoot, new Vector2(0.03f, 0.05f), new Vector2(0.20f, 0.31f));
            SetRect(lookControlRoot, new Vector2(0.23f, 0.05f), new Vector2(0.42f, 0.31f));
        }

        var showTouch = touchLayout && !xrActive && participantStarted && !studyFinished;
        moveControlRoot.gameObject.SetActive(showTouch);
        lookControlRoot.gameObject.SetActive(showTouch);
        crosshair.SetActive(!touchLayout && !xrActive && participantStarted && !studyFinished);
        controlModeButton.gameObject.SetActive(!xrActive);

        var cardWidth = portrait ? 0.92f : 0.58f;
        var cardHeight = portrait ? 0.66f : 0.62f;
        SetRect(introductionCard,
            new Vector2((1f - cardWidth) * 0.5f, (1f - cardHeight) * 0.5f),
            new Vector2((1f + cardWidth) * 0.5f, (1f + cardHeight) * 0.5f));
        SetRect(completionCard,
            new Vector2((1f - cardWidth) * 0.5f, 0.22f),
            new Vector2((1f + cardWidth) * 0.5f, 0.78f));

        if (force)
            LogStudyEvent("layout_changed", CurrentModality(), "", "", portrait ? 1 : 0);
    }

    public void SetFlatControlMode(FlatControlMode mode)
    {
        if (flatControlMode == mode && touchLayout == (mode == FlatControlMode.Smartphone))
        {
            UpdateControlModeButton();
            return;
        }

        flatControlMode = mode;
        touchLayout = mode == FlatControlMode.Smartphone;
        touchMove = Vector2.zero;
        queuedLookDelta = Vector2.zero;
        SetPointerLock(false);
        UpdateControlModeButton();
        UpdateResponsiveLayout(true);
        ShowToast(touchLayout ? "Smartphone-Steuerung aktiv." : "Computer-Steuerung aktiv.", 2f);
        LogStudyEvent("control_mode_changed", CurrentModality(), coreManager.activeAgentId, "", (int)mode);
    }

    public void ToggleFlatControlMode()
    {
        SetFlatControlMode(flatControlMode == FlatControlMode.Computer
            ? FlatControlMode.Smartphone
            : FlatControlMode.Computer);
    }

    private void UpdateControlModeButton()
    {
        if (controlModeButtonLabel != null)
            controlModeButtonLabel.text = flatControlMode == FlatControlMode.Computer ? "PC" : "MOBIL";
    }

    private void UpdateInterfaceText()
    {
        if (statusLabel == null || coreManager == null)
            return;

        var status = GetCoreField<string>("statusMessage") ?? "";
        var visibleStatus = IsReady
            ? (xrActive ? "WEBXR · VERBUNDEN" : touchLayout ? "MOBIL · VERBUNDEN" : "FPV · VERBUNDEN")
            : string.IsNullOrWhiteSpace(status) ? "VERBINDUNG WIRD AUFGEBAUT …" : status.ToUpperInvariant();
        if (!string.Equals(lastStatus, visibleStatus, StringComparison.Ordinal))
        {
            statusLabel.text = visibleStatus;
            lastStatus = visibleStatus;
        }

        var activeId = coreManager.activeAgentId ?? "";
        agentLabel.text = string.IsNullOrWhiteSpace(activeId)
            ? "Agent: noch niemand in der Nähe"
            : "Im Gespräch: " + GetAgentDisplayName(activeId);

        // The full task stays in the introduction. The small in-world HUD must never
        // clip a requirement, so it shows the three requirements as compact status rows.
        taskLabel.text = ProgressMark(contactedAgents.Count >= 2)
            + "  2 Gespräche  (" + Mathf.Min(contactedAgents.Count, 2) + "/2)\n"
            + ProgressMark(inspectedObject) + "  1 Objekt untersucht\n"
            + ProgressMark(successfulInteractions > 0) + "  1 Antwort erhalten";

        var lines = GetCoreField<IList>("chatLog");
        var transcript = BuildTranscript(lines);
        if (!string.Equals(transcript, lastTranscript, StringComparison.Ordinal))
        {
            transcriptLabel.text = string.IsNullOrWhiteSpace(transcript)
                ? "Beginne ein Gespräch – per Text oder Mikrofon."
                : transcript;
            lastTranscript = transcript;
            Canvas.ForceUpdateCanvases();
            transcriptScroll.verticalNormalizedPosition = 0f;
        }
    }

    private static string BuildTranscript(IList lines)
    {
        if (lines == null || lines.Count == 0)
            return "";
        var start = Mathf.Max(0, lines.Count - 24);
        var result = new System.Text.StringBuilder();
        for (var i = start; i < lines.Count; i++)
        {
            var line = lines[i] as string;
            if (string.IsNullOrWhiteSpace(line))
                continue;
            if (result.Length > 0)
                result.Append("\n\n");
            result.Append(CleanParticipantTranscriptLine(line));
        }
        return result.ToString();
    }

    private static string CleanParticipantTranscriptLine(string line)
    {
        if (line.StartsWith("[Du/Voice] ", StringComparison.Ordinal))
            return "Du (Sprache)\n" + ExtractParticipantReply(line.Substring(11));
        if (line.StartsWith("[Du] ", StringComparison.Ordinal))
            return "Du\n" + ExtractParticipantReply(line.Substring(5));

        var separator = line.IndexOf("] ", StringComparison.Ordinal);
        if (line.StartsWith("[", StringComparison.Ordinal) && separator > 1)
        {
            var label = line.Substring(1, separator - 1);
            if (label.EndsWith("/say", StringComparison.OrdinalIgnoreCase))
                label = label.Substring(0, label.Length - 4);
            return label + "\n" + ExtractParticipantReply(line.Substring(separator + 2));
        }

        return ExtractParticipantReply(line);
    }

    private static string ExtractParticipantReply(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            return "";

        var normalized = value.Replace("\\n", "\n").Trim();
        if (normalized.StartsWith("```", StringComparison.Ordinal))
        {
            var firstLine = normalized.IndexOf('\n');
            var closingFence = normalized.LastIndexOf("```", StringComparison.Ordinal);
            if (firstLine >= 0 && closingFence > firstLine)
                normalized = normalized.Substring(firstLine + 1, closingFence - firstLine - 1).Trim();
        }

        var jsonStart = normalized.IndexOf('{');
        var jsonEnd = normalized.LastIndexOf('}');
        if (jsonStart < 0 || jsonEnd <= jsonStart)
            return normalized;

        try
        {
            var root = JToken.Parse(normalized.Substring(jsonStart, jsonEnd - jsonStart + 1));
            var extracted = FindParticipantReply(root);
            return string.IsNullOrWhiteSpace(extracted) ? normalized : extracted.Trim();
        }
        catch
        {
            // Preserve ordinary text when a model really returned incomplete JSON.
            return normalized;
        }
    }

    private static string FindParticipantReply(JToken token)
    {
        if (token == null)
            return null;

        if (token.Type == JTokenType.Object)
        {
            var preferredFields = new[]
            {
                "response", "say", "antwort", "answer", "text", "message", "content"
            };
            foreach (var field in preferredFields)
            {
                var property = ((JObject)token).Property(field, StringComparison.OrdinalIgnoreCase);
                if (property == null)
                    continue;
                var text = property.Value.Type == JTokenType.String
                    ? property.Value.Value<string>()
                    : FindParticipantReply(property.Value);
                if (!string.IsNullOrWhiteSpace(text))
                    return text;
            }

            foreach (var child in token.Children<JProperty>())
            {
                if (child.Value.Type != JTokenType.Object
                    && child.Value.Type != JTokenType.Array)
                    continue;
                var text = FindParticipantReply(child.Value);
                if (!string.IsNullOrWhiteSpace(text))
                    return text;
            }
        }
        else if (token.Type == JTokenType.Array)
        {
            foreach (var child in token.Children())
            {
                var text = FindParticipantReply(child);
                if (!string.IsNullOrWhiteSpace(text))
                    return text;
            }
        }
        else if (token.Type == JTokenType.String)
        {
            return token.Value<string>();
        }

        return null;
    }

    private static string ProgressMark(bool completed)
    {
        return completed ? "✓" : "○";
    }

    private void BeginParticipantSession()
    {
        participantStarted = true;
        studyFinished = false;
        introductionOverlay.SetActive(false);
        UpdateResponsiveLayout(true);
        if (!touchLayout && !xrActive)
            SetPointerLock(true);
        LogStudyEvent("participant_started", CurrentModality(), coreManager.activeAgentId, "", 0);
    }

    /// <summary>Starts the participant surface for deterministic editor capture/smoke tooling.</summary>
    public void BeginParticipantSessionForAutomation()
    {
        BeginParticipantSession();
    }

    private void ShowHelp()
    {
        introductionOverlay.SetActive(true);
        SetPointerLock(false);
    }

    private void FinishStudy()
    {
        studyFinished = true;
        SetPointerLock(false);
        moveControlRoot.gameObject.SetActive(false);
        lookControlRoot.gameObject.SetActive(false);
        crosshair.SetActive(false);
        completionLabel.text =
            "Teilnahmecode: " + participantCode + "\n\n" +
            "Gespräche mit Agent:innen: " + contactedAgents.Count + "\n" +
            "Objekt untersucht: " + (inspectedObject ? "ja" : "noch nicht") + "\n" +
            "Erfolgreiche Interaktionen: " + successfulInteractions + "\n\n" +
            "Du kannst diesen Code der Studienleitung nennen.";
        completionOverlay.SetActive(true);
        LogStudyEvent("participant_finished", CurrentModality(), coreManager.activeAgentId,
            coreManager.SelectedSpatialEntityId, successfulInteractions);
    }

    private void HandleInputEndEdit(string value)
    {
#if ENABLE_INPUT_SYSTEM
        var keyboard = Keyboard.current;
        if (keyboard != null && keyboard.enterKey.wasPressedThisFrame)
            SendCurrentMessage();
#endif
    }

    public void SendCurrentMessage()
    {
        if (chatInput == null || string.IsNullOrWhiteSpace(chatInput.text))
            return;
        if (!IsReady)
        {
            ShowToast("Bitte warte, bis die Verbindung bereit ist.", 3f);
            return;
        }

        var message = chatInput.text.Trim();
        chatInput.text = "";
        SendMessageThroughCore(message, false);
    }

    private void SendMessageThroughCore(string message, bool voice)
    {
        if (coreManager == null || string.IsNullOrWhiteSpace(message))
            return;

        message = message.Trim();
        var activeId = coreManager.activeAgentId ?? "";
        if (!string.IsNullOrWhiteSpace(activeId))
            contactedAgents.Add(activeId);

        InvokeCore("AddUserChatLine", new[] { typeof(string), typeof(bool) }, message, voice);
        var routine = InvokeCore("SendChat", new[] { typeof(string) }, message) as IEnumerator;
        if (routine != null)
            StartCoroutine(RunCoreChatWithHandoffNavigation(routine));
        LogStudyEvent(voice ? "voice_chat_sent" : "chat_sent", CurrentModality(), activeId,
            coreManager.SelectedSpatialEntityId, message.Length);
    }

    private IEnumerator RunCoreChatWithHandoffNavigation(IEnumerator routine)
    {
        if (routine == null)
            yield break;

        while (true)
        {
            bool hasNext;
            object yielded = null;
            // QAM's original proximity handoff branch is gated by its private FPV flag.
            // Arm it only while advancing the chat coroutine; its legacy input and HUD
            // therefore remain disabled, while pending events and the dashed route are kept.
            SetCoreField("_fpvActive", true);
            SetCoreField("_fpvChatOpen", false);
            try
            {
                hasNext = routine.MoveNext();
                if (hasNext)
                    yielded = routine.Current;
            }
            finally
            {
                SetCoreField("_fpvActive", false);
                SetCoreField("_fpvChatOpen", false);
            }

            if (!hasNext)
                yield break;
            yield return yielded;
        }
    }

    private void ForwardCompletedVoiceTranscript()
    {
        if (!awaitingVoiceTranscript || coreManager == null)
            return;
        if (GetCoreField<bool>("isVoiceRecording") || GetCoreField<bool>("sttInFlight"))
            return;

        var transcript = GetCoreField<string>("chatInput");
        if (string.IsNullOrWhiteSpace(transcript))
            return;

        SetCoreField("chatInput", "");
        awaitingVoiceTranscript = false;
        SendMessageThroughCore(transcript, true);
    }

    public void ToggleVoiceRecording()
    {
        if (!IsReady)
        {
            ShowToast("Mikrofon ist verfügbar, sobald die Verbindung steht.", 3f);
            return;
        }

        var recording = GetCoreField<bool>("isVoiceRecording");
        if (recording)
        {
            awaitingVoiceTranscript = true;
            InvokeCore("StopVoiceRecordingAndSend", Type.EmptyTypes);
            LogStudyEvent("voice_stopped", CurrentModality(), coreManager.activeAgentId, "", 0);
        }
        else
        {
            awaitingVoiceTranscript = false;
            if (!string.IsNullOrWhiteSpace(coreManager.activeAgentId))
                contactedAgents.Add(coreManager.activeAgentId);
            InvokeCore("StartVoiceRecording", Type.EmptyTypes);
            LogStudyEvent("voice_started", CurrentModality(), coreManager.activeAgentId, "", 0);
        }
    }

    private void UpdateMicButton()
    {
        if (micButtonLabel == null)
            return;
        var recording = GetCoreField<bool>("isVoiceRecording");
        var transcribing = GetCoreField<bool>("sttInFlight");
        micButtonLabel.text = recording ? "STOPP" : transcribing ? "VERARBEITET …" : "MIKRO";
        micButton.interactable = !transcribing;
    }

    private void EnforceVoiceRecordingLimit()
    {
        if (coreManager == null || !GetCoreField<bool>("isVoiceRecording"))
            return;
        var startedAt = GetCoreField<float>("voiceRecordingStartedAt");
        var maximum = Mathf.Max(1f, coreManager.voiceMaxRecordSeconds);
        if (startedAt <= 0f || Time.time - startedAt < maximum)
            return;
        awaitingVoiceTranscript = true;
        InvokeCore("StopVoiceRecordingAndSend", Type.EmptyTypes);
        LogStudyEvent("voice_auto_stopped", CurrentModality(), coreManager.activeAgentId, "", 0);
    }

    public void SelectAtViewCenter()
    {
        if (playerCamera == null)
            return;
        SelectRay(new Ray(playerCamera.transform.position, playerCamera.transform.forward), CurrentRayModality());
    }

    private void SelectAtScreenPoint(Vector2 screenPoint)
    {
        if (playerCamera == null)
            return;
        // "touch" is the normative V2 modality. "touch_ray" was a local UI
        // label and is intentionally rejected by QuickAgentManager/backend.
        SelectRay(playerCamera.ScreenPointToRay(screenPoint), "touch");
    }

    private void SelectRay(Ray ray, string modality)
    {
        if (!IsReady)
            return;
        var previous = coreManager.enableSpatialTargetSelection;
        coreManager.enableSpatialTargetSelection = true;
        bool selected;
        try
        {
            selected = coreManager.TrySelectSpatialTargetFromRay(ray, modality);
        }
        finally
        {
            coreManager.enableSpatialTargetSelection = previous;
        }
        if (selected && !string.IsNullOrWhiteSpace(coreManager.SelectedSpatialEntityId))
        {
            ShowToast("Objekt ausgewählt: " + SelectedObjectDisplayName()
                + ". Stelle jetzt deine Frage.", 3.5f);
        }
        else if (selected)
        {
            ShowToast("Agent ausgewählt. Richte die Mitte für ein Objekt auf ein Exponat.", 3f);
        }
        else
        {
            var reason = GetCoreField<string>("spatialSelectionReason") ?? "Kein Objekt getroffen.";
            ShowToast("Kein Exponat ausgewählt. Ziele direkt auf Kuh, Milchlaster oder Ausstellung.\n"
                + reason, 4f);
        }
        LogStudyEvent("selection_attempted", modality, coreManager.activeAgentId,
            coreManager.SelectedSpatialEntityId, selected ? 1 : 0);
    }

    private string SelectedObjectDisplayName()
    {
        var entityId = coreManager == null ? "" : coreManager.SelectedSpatialEntityId;
        var registry = coreManager == null ? null : coreManager.SpatialBindingRegistry;
        if (registry != null)
        {
            var bindings = registry.Bindings;
            for (var i = 0; i < bindings.Count; i++)
            {
                var binding = bindings[i];
                if (binding != null && string.Equals(binding.EntityId, entityId, StringComparison.Ordinal))
                    return string.IsNullOrWhiteSpace(binding.DisplayName)
                        ? binding.SourceObjectId
                        : binding.DisplayName;
            }
        }
        return string.IsNullOrWhiteSpace(entityId) ? "Exponat" : entityId;
    }

    private string CurrentRayModality()
    {
        if (xrActive)
            return "xr_controller_ray";
        return touchLayout ? "touch" : "desktop_ray";
    }

    private void UpdateFlatInput()
    {
#if ENABLE_INPUT_SYSTEM
        var keyboard = Keyboard.current;
        var mouse = Mouse.current;
        if (keyboard != null)
        {
            var typing = chatInput != null && chatInput.isFocused;
            if (keyboard.escapeKey.wasPressedThisFrame)
                SetPointerLock(false);
            if (!typing
                && (keyboard.tKey.wasPressedThisFrame || keyboard.tabKey.wasPressedThisFrame)
                && chatInput != null)
            {
                SetPointerLock(false);
                chatInput.Select();
                chatInput.ActivateInputField();
            }
            if (!typing && keyboard.vKey.wasPressedThisFrame)
                ToggleVoiceRecording();
            if (!typing && keyboard.eKey.wasPressedThisFrame)
                SelectAtViewCenter();
            if (!typing && keyboard.mKey.wasPressedThisFrame)
                ToggleFlatControlMode();
        }

        if (!touchLayout && mouse != null)
        {
            if (!pointerLocked
                && mouse.leftButton.wasPressedThisFrame
                && (EventSystem.current == null || !EventSystem.current.IsPointerOverGameObject()))
                SetPointerLock(true);
            if (pointerLocked)
                queuedLookDelta += mouse.delta.ReadValue() * mouseLookSensitivity;
        }
#endif

        if (!touchLayout && queuedLookDelta.sqrMagnitude > 0f)
        {
            yaw += queuedLookDelta.x;
            pitch = Mathf.Clamp(pitch - queuedLookDelta.y, -pitchLimit, pitchLimit);
            queuedLookDelta = Vector2.zero;
            playerRoot.transform.rotation = Quaternion.Euler(0f, yaw, 0f);
            playerCamera.transform.localRotation = Quaternion.Euler(pitch, 0f, 0f);
        }
        else if (touchLayout && queuedLookDelta.sqrMagnitude > 0f)
        {
            yaw += queuedLookDelta.x * touchLookSensitivity;
            pitch = Mathf.Clamp(pitch - queuedLookDelta.y * touchLookSensitivity, -pitchLimit, pitchLimit);
            queuedLookDelta = Vector2.zero;
            playerRoot.transform.rotation = Quaternion.Euler(0f, yaw, 0f);
            playerCamera.transform.localRotation = Quaternion.Euler(pitch, 0f, 0f);
        }
    }

    private void UpdateMovement()
    {
        if (characterController == null || chatInput == null || chatInput.isFocused)
            return;

        var move = touchLayout && !xrActive ? touchMove : Vector2.zero;
        var sprint = false;

#if ENABLE_INPUT_SYSTEM
        if (!touchLayout && !xrActive)
        {
            var keyboard = Keyboard.current;
            if (keyboard != null)
            {
                move.x += (keyboard.dKey.isPressed ? 1f : 0f) - (keyboard.aKey.isPressed ? 1f : 0f);
                move.y += (keyboard.wKey.isPressed ? 1f : 0f) - (keyboard.sKey.isPressed ? 1f : 0f);
                sprint = keyboard.leftShiftKey.isPressed || keyboard.rightShiftKey.isPressed;
            }
        }
#endif

        if (xrActive)
        {
            if (!TryReadWebXrStick(false, out move))
            {
                var left = InputDevices.GetDeviceAtXRNode(XRNode.LeftHand);
                if (left.isValid
                    && left.TryGetFeatureValue(UnityEngine.XR.CommonUsages.primary2DAxis, out var axis))
                    move = axis;
            }
        }

        move = Vector2.ClampMagnitude(move, 1f);
        var cameraForward = playerCamera.transform.forward;
        cameraForward.y = 0f;
        cameraForward = cameraForward.sqrMagnitude > 0.001f ? cameraForward.normalized : playerRoot.transform.forward;
        var cameraRight = playerCamera.transform.right;
        cameraRight.y = 0f;
        cameraRight = cameraRight.sqrMagnitude > 0.001f ? cameraRight.normalized : playerRoot.transform.right;

        var velocity = cameraRight * move.x + cameraForward * move.y;
        if (velocity.sqrMagnitude > 1f)
            velocity.Normalize();
        velocity *= moveSpeed * (sprint ? sprintMultiplier : 1f);

        if (characterController.isGrounded && verticalVelocity < 0f)
            verticalVelocity = -1.5f;
        else
            verticalVelocity -= gravity * Time.deltaTime;
        velocity.y = verticalVelocity;
        characterController.Move(velocity * Time.deltaTime);
    }

    private void UpdateXrInput(bool allowParticipantInteraction)
    {
        var trigger = false;
        var primaryButton = false;
        var turn = Vector2.zero;
        var hasRay = TryReadWebXrController(
            out var ray,
            out trigger,
            out primaryButton,
            out turn);

        if (!hasRay)
        {
            var right = InputDevices.GetDeviceAtXRNode(XRNode.RightHand);
            if (right.isValid)
            {
                right.TryGetFeatureValue(UnityEngine.XR.CommonUsages.triggerButton, out trigger);
                right.TryGetFeatureValue(UnityEngine.XR.CommonUsages.primaryButton, out primaryButton);
                right.TryGetFeatureValue(UnityEngine.XR.CommonUsages.primary2DAxis, out turn);
                hasRay = TryBuildControllerRay(right, out ray);
            }
        }

        if (hasRay)
        {
            var uiClaimed = ProcessXrUiRay(ray, trigger, lastXrTrigger);
            if (allowParticipantInteraction && !uiClaimed && trigger && !lastXrTrigger)
                SelectRay(ray, "xr_controller_ray");
        }

        if (allowParticipantInteraction)
        {
            if (primaryButton && !lastXrPrimaryButton)
                ToggleVoiceRecording();

            if (Mathf.Abs(turn.x) > 0.75f
                && Time.unscaledTime >= nextXrSnapTurnAt)
            {
                playerRoot.transform.Rotate(0f, Mathf.Sign(turn.x) * 30f, 0f, Space.World);
                nextXrSnapTurnAt = Time.unscaledTime + 0.35f;
            }
        }
        lastXrTrigger = trigger;
        lastXrPrimaryButton = primaryButton;
    }

#if ENABLE_INPUT_SYSTEM
    private static NewInputDevice FindWebXrController(bool rightHand)
    {
        foreach (var device in UnityEngine.InputSystem.InputSystem.devices)
        {
            if (device == null)
                continue;
            var product = device.description.product ?? "";
            if (!string.Equals(product, "WebXR Controller", StringComparison.OrdinalIgnoreCase)
                && (device.layout ?? "").IndexOf("WebXRController", StringComparison.OrdinalIgnoreCase) < 0)
                continue;

            foreach (var usage in device.usages)
            {
                var usageName = usage.ToString();
                if (rightHand && string.Equals(usageName, "RightHand", StringComparison.OrdinalIgnoreCase))
                    return device;
                if (!rightHand && string.Equals(usageName, "LeftHand", StringComparison.OrdinalIgnoreCase))
                    return device;
            }
        }
        return null;
    }

    private static bool TryReadWebXrStick(bool rightHand, out Vector2 value)
    {
        value = Vector2.zero;
        var device = FindWebXrController(rightHand);
        var control = device?.TryGetChildControl<Vector2Control>("thumbstick");
        if (control == null)
            return false;
        value = control.ReadValue();
        return true;
    }

    private bool TryReadWebXrController(
        out Ray ray,
        out bool trigger,
        out bool primaryButton,
        out Vector2 turn)
    {
        ray = default;
        trigger = false;
        primaryButton = false;
        turn = Vector2.zero;
        var device = FindWebXrController(true);
        if (device == null)
            return false;

        var pointerPosition = device.TryGetChildControl<Vector3Control>("pointerPosition");
        var pointerRotation = device.TryGetChildControl<QuaternionControl>("pointerRotation");
        if (pointerPosition == null || pointerRotation == null)
            return false;

        trigger = device.TryGetChildControl<ButtonControl>("triggerPressed")?.isPressed == true;
        primaryButton = device.TryGetChildControl<ButtonControl>("buttonA")?.isPressed == true;
        turn = device.TryGetChildControl<Vector2Control>("thumbstick")?.ReadValue() ?? Vector2.zero;
        var localPosition = pointerPosition.ReadValue();
        var localRotation = pointerRotation.ReadValue();
        ray = new Ray(
            playerRoot.transform.TransformPoint(localPosition),
            playerRoot.transform.rotation * localRotation * Vector3.forward);
        return true;
    }
#else
    private static bool TryReadWebXrStick(bool rightHand, out Vector2 value)
    {
        value = Vector2.zero;
        return false;
    }

    private bool TryReadWebXrController(
        out Ray ray,
        out bool trigger,
        out bool primaryButton,
        out Vector2 turn)
    {
        ray = default;
        trigger = false;
        primaryButton = false;
        turn = Vector2.zero;
        return false;
    }
#endif

    private bool ProcessXrUiRay(Ray ray, bool trigger, bool previousTrigger)
    {
        if (!xrActive || canvas == null || EventSystem.current == null)
            return false;
        EnsureXrUiRayCamera();
        if (xrUiRayCamera == null)
            return false;

        xrUiRayCamera.transform.SetPositionAndRotation(ray.origin, Quaternion.LookRotation(ray.direction));
        canvas.worldCamera = xrUiRayCamera;
        var pointer = new PointerEventData(EventSystem.current)
        {
            position = new Vector2(50f, 50f),
            button = PointerEventData.InputButton.Left
        };
        var results = new List<RaycastResult>();
        var graphicRaycaster = canvas.GetComponent<GraphicRaycaster>();
        graphicRaycaster?.Raycast(pointer, results);

        GameObject handler = null;
        foreach (var result in results)
        {
            handler = ExecuteEvents.GetEventHandler<IPointerClickHandler>(result.gameObject);
            if (handler != null)
                break;
        }

        if (handler != xrUiHover)
        {
            if (xrUiHover != null)
                ExecuteEvents.Execute(xrUiHover, pointer, ExecuteEvents.pointerExitHandler);
            xrUiHover = handler;
            if (xrUiHover != null)
                ExecuteEvents.Execute(xrUiHover, pointer, ExecuteEvents.pointerEnterHandler);
        }

        if (handler != null && trigger && !previousTrigger)
        {
            pointer.pointerPress = handler;
            ExecuteEvents.Execute(handler, pointer, ExecuteEvents.pointerDownHandler);
            ExecuteEvents.Execute(handler, pointer, ExecuteEvents.pointerUpHandler);
            ExecuteEvents.Execute(handler, pointer, ExecuteEvents.pointerClickHandler);
        }
        return handler != null;
    }

    private void EnsureXrUiRayCamera()
    {
        if (xrUiRayCamera != null)
            return;
        var rayCamera = new GameObject("WebXR UI Ray Camera", typeof(Camera));
        rayCamera.hideFlags = HideFlags.DontSave;
        xrUiRayCamera = rayCamera.GetComponent<Camera>();
        xrUiRayCamera.enabled = false;
        xrUiRayCamera.cullingMask = 0;
        xrUiRayCamera.nearClipPlane = 0.01f;
        xrUiRayCamera.farClipPlane = 20f;
        xrUiRayCamera.fieldOfView = 1f;
        xrUiRayCamera.aspect = 1f;
        xrUiRayCamera.pixelRect = new Rect(0f, 0f, 100f, 100f);
    }

    private bool TryBuildControllerRay(UnityEngine.XR.InputDevice device, out Ray ray)
    {
        ray = default;
        if (!device.TryGetFeatureValue(UnityEngine.XR.CommonUsages.devicePosition, out var localPosition)
            || !device.TryGetFeatureValue(UnityEngine.XR.CommonUsages.deviceRotation, out var localRotation))
            return false;
        ray = new Ray(
            playerRoot.transform.TransformPoint(localPosition),
            playerRoot.transform.rotation * localRotation * Vector3.forward);
        return true;
    }

    private void PollWebXrState()
    {
        var state = ReadWebXrState();
        if (state == lastWebXrState)
            return;
        lastWebXrState = state;
        SetWebXrMode(state != 0, state);
    }

    private static int ReadWebXrState()
    {
        // WebXR deliberately sets autoReferenced=false on its assembly. Reflection keeps
        // this component package-optional while still reading the authoritative runtime
        // state (VR=1, AR=2, NORMAL=0 by name below).
        var managerType = Type.GetType("WebXR.WebXRManager, WebXR");
        if (managerType != null)
        {
            var instance = managerType.GetProperty("Instance", BindingFlags.Public | BindingFlags.Static)
                ?.GetValue(null, null);
            var state = instance == null
                ? null
                : managerType.GetProperty("XRState", BindingFlags.Public | BindingFlags.Instance)
                    ?.GetValue(instance, null);
            var name = state == null ? "" : state.ToString();
            if (string.Equals(name, "VR", StringComparison.OrdinalIgnoreCase))
                return 1;
            if (string.Equals(name, "AR", StringComparison.OrdinalIgnoreCase))
                return 2;
        }

        return XRSettings.isDeviceActive ? 1 : 0;
    }

    private void SetWebXrMode(bool immersive, int state)
    {
        if (xrActive == immersive)
            return;
        xrActive = immersive;
        SetPointerLock(false);

#if ENABLE_INPUT_SYSTEM
        if (trackedPoseDriver != null)
            trackedPoseDriver.enabled = xrActive;
#endif

        if (xrActive)
        {
            canvas.renderMode = RenderMode.WorldSpace;
            canvas.worldCamera = playerCamera;
            canvasRect.SetParent(playerCamera.transform, false);
            canvasRect.localPosition = new Vector3(0f, -0.05f, 1.35f);
            canvasRect.localRotation = Quaternion.identity;
            canvasRect.sizeDelta = new Vector2(1080f, 720f);
            canvasRect.localScale = Vector3.one * 0.00105f;
            TryAddTrackedDeviceRaycaster(canvas.gameObject);
        }
        else
        {
            if (xrUiHover != null && EventSystem.current != null)
            {
                var pointer = new PointerEventData(EventSystem.current);
                ExecuteEvents.Execute(xrUiHover, pointer, ExecuteEvents.pointerExitHandler);
                xrUiHover = null;
            }
            canvasRect.SetParent(transform, false);
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.worldCamera = null;
            canvasRect.anchorMin = Vector2.zero;
            canvasRect.anchorMax = Vector2.one;
            canvasRect.offsetMin = Vector2.zero;
            canvasRect.offsetMax = Vector2.zero;
            canvasRect.localPosition = Vector3.zero;
            canvasRect.localRotation = Quaternion.identity;
            canvasRect.sizeDelta = Vector2.zero;
            canvasRect.localScale = Vector3.one;
            playerCamera.transform.localPosition = new Vector3(0f, eyeHeight, 0f);
            playerCamera.transform.localRotation = Quaternion.Euler(pitch, 0f, 0f);
        }

        UpdateResponsiveLayout(true);
        LogStudyEvent("webxr_state_changed", CurrentModality(), coreManager.activeAgentId, "", state);
    }

    private static void TryAddWebXrCameraSettings(Camera camera)
    {
        if (camera == null)
            return;
        var type = Type.GetType("WebXR.WebXRCameraSettings, WebXR");
        if (type == null)
            return;
        var component = camera.GetComponent(type) ?? camera.gameObject.AddComponent(type);
        var behaviour = component as Behaviour;
        if (behaviour != null)
            behaviour.enabled = false;

        // A settings component added at runtime has already passed Awake before its
        // camera reference can be assigned. Disable its pose restore (which would
        // otherwise dereference an uninitialised transform) and explicitly preserve
        // the live camera's render settings for normal, VR and AR modes.
        var mask = (LayerMask)camera.cullingMask;
        SetWebXrProperty(type, component, "Camera", camera);
        SetWebXrProperty(type, component, "UpdateNormalFieldOfView", false);
        SetWebXrProperty(type, component, "UpdateNormalLocalPose", false);
        SetWebXrProperty(type, component, "NormalClearFlags", camera.clearFlags);
        SetWebXrProperty(type, component, "NormalBackgroundColor", camera.backgroundColor);
        SetWebXrProperty(type, component, "NormalCullingMask", mask);
        SetWebXrProperty(type, component, "VRClearFlags", camera.clearFlags);
        SetWebXrProperty(type, component, "VRBackgroundColor", camera.backgroundColor);
        SetWebXrProperty(type, component, "VRCullingMask", mask);
        SetWebXrProperty(type, component, "ARClearFlags", CameraClearFlags.SolidColor);
        SetWebXrProperty(type, component, "ARBackgroundColor", new Color(0f, 0f, 0f, 0f));
        SetWebXrProperty(type, component, "ARCullingMask", mask);

        if (behaviour != null)
            behaviour.enabled = true;
    }

    private static void SetWebXrProperty(Type type, Component component, string name, object value)
    {
        type.GetProperty(name, BindingFlags.Public | BindingFlags.Instance)
            ?.SetValue(component, value, null);
    }

    private static void TryEnsureWebXrInputSystem()
    {
        var type = Type.GetType("WebXR.InputSystem.WebXRInputSystem, WebXR.InputSystem");
        if (type == null || Resources.FindObjectsOfTypeAll(type).Length > 0)
            return;
        var inputObject = new GameObject("WebXRInputSystem");
        inputObject.AddComponent(type);
        DontDestroyOnLoad(inputObject);
    }

    private static void TryAddTrackedDeviceRaycaster(GameObject canvasObject)
    {
        var type = Type.GetType(
            "UnityEngine.XR.Interaction.Toolkit.UI.TrackedDeviceGraphicRaycaster, " +
            "Unity.XR.Interaction.Toolkit");
        if (type != null && canvasObject.GetComponent(type) == null)
            canvasObject.AddComponent(type);
    }

    private void UpdatePendingHandoffNavigation()
    {
        if (handoffIndicator == null || coreManager == null || playerCamera == null)
            return;

        var targetId = GetCoreField<string>("_pendingHandoffAgentId") ?? "";
        if (string.IsNullOrWhiteSpace(targetId))
        {
            lastPendingHandoffAgentId = "";
            handoffIndicator.gameObject.SetActive(false);
            return;
        }

        var roots = GetAgentRoots();
        if (!roots.TryGetValue(targetId, out var targetRoot) || targetRoot == null)
        {
            handoffIndicator.gameObject.SetActive(false);
            return;
        }

        var toTarget = targetRoot.transform.position - playerCamera.transform.position;
        var distance = toTarget.magnitude;
        if (distance <= Mathf.Max(1f, coreManager.fpvInteractionRadius))
        {
            InvokeCore("TriggerPendingHandoffArrival", Type.EmptyTypes);
            handoffIndicator.gameObject.SetActive(false);
            lastPendingHandoffAgentId = "";
            lastProximityAgentId = targetId;
            contactedAgents.Add(targetId);
            ShowToast("Angekommen bei " + GetAgentDisplayName(targetId) + ".", 2.5f);
            LogStudyEvent("handoff_arrived", CurrentModality(), targetId,
                coreManager.SelectedSpatialEntityId, 1);
            return;
        }

        if (!string.Equals(lastPendingHandoffAgentId, targetId, StringComparison.Ordinal))
        {
            lastPendingHandoffAgentId = targetId;
            ShowToast(GetAgentDisplayName(targetId) + " ist zuständig – folge Linie und Pfeil.", 4f);
            LogStudyEvent("handoff_route_started", CurrentModality(), coreManager.activeAgentId,
                targetId, 1);
        }

        var flatTarget = Vector3.ProjectOnPlane(toTarget, Vector3.up);
        var flatForward = Vector3.ProjectOnPlane(playerCamera.transform.forward, Vector3.up);
        var flatRight = Vector3.ProjectOnPlane(playerCamera.transform.right, Vector3.up);
        if (flatTarget.sqrMagnitude < 0.001f || flatForward.sqrMagnitude < 0.001f)
        {
            handoffIndicator.gameObject.SetActive(false);
            return;
        }

        flatTarget.Normalize();
        flatForward.Normalize();
        flatRight = flatRight.sqrMagnitude > 0.001f ? flatRight.normalized : Vector3.right;
        var direction = new Vector2(
            Vector3.Dot(flatTarget, flatRight),
            Vector3.Dot(flatTarget, flatForward)).normalized;
        var radiusPixels = Mathf.Clamp(Mathf.Min(Screen.width, Screen.height) * 0.22f, 72f, 190f);
        var scale = canvas == null ? 1f : Mathf.Max(0.01f, canvas.scaleFactor);
        handoffIndicator.anchoredPosition = direction * (radiusPixels / scale);
        var angle = Mathf.Atan2(direction.x, direction.y) * Mathf.Rad2Deg;
        handoffArrowGlyph.localRotation = Quaternion.Euler(0f, 0f, -angle);
        handoffTargetLabel.text = "ZU " + GetAgentDisplayName(targetId).ToUpperInvariant()
            + "  ·  " + Mathf.CeilToInt(distance) + " m";
        handoffIndicator.gameObject.SetActive(true);
        handoffIndicator.SetAsLastSibling();
    }

    private void UpdateNearestAgent()
    {
        if (!string.IsNullOrWhiteSpace(GetCoreField<string>("_pendingHandoffAgentId")))
            return;
        if (Time.unscaledTime < nextAgentScanAt || playerCamera == null)
            return;
        nextAgentScanAt = Time.unscaledTime + AgentScanInterval;

        var roots = GetAgentRoots();
        var nearestId = "";
        var nearestDistance = float.PositiveInfinity;
        foreach (var pair in roots)
        {
            if (pair.Value == null)
                continue;
            var distance = Vector3.Distance(playerCamera.transform.position, pair.Value.transform.position);
            if (distance < nearestDistance)
            {
                nearestDistance = distance;
                nearestId = pair.Key;
            }
        }

        if (nearestDistance > Mathf.Max(1f, coreManager.fpvInteractionRadius))
            nearestId = "";

        // Change the conversational focus only when the participant enters another
        // proximity zone. A modeled handoff may change activeAgentId while the user is
        // still standing near the previous agent; do not immediately undo that route.
        if (string.Equals(nearestId, lastProximityAgentId, StringComparison.Ordinal))
            return;
        lastProximityAgentId = nearestId;

        if (!string.IsNullOrWhiteSpace(nearestId)
            && !string.Equals(nearestId, coreManager.activeAgentId, StringComparison.Ordinal))
        {
            InvokeCore("SetActiveAgentId", new[] { typeof(string), typeof(bool) }, nearestId, false);
            ShowToast("Du sprichst jetzt mit " + GetAgentDisplayName(nearestId) + ".", 2f);
            LogStudyEvent("agent_entered_range", CurrentModality(), nearestId, "", 0);
        }

    }

    private void DiscoverAndGuardAgentPoses()
    {
        if (Time.unscaledTime < nextPoseScanAt)
            return;
        nextPoseScanAt = Time.unscaledTime + 0.1f;

        foreach (var pair in GetAgentRoots())
        {
            var root = pair.Value;
            if (root == null || knownAgentRoots.Contains(root))
                continue;
            knownAgentRoots.Add(root);

            var watch = new PoseWatch
            {
                root = root,
                renderers = root.GetComponentsInChildren<SkinnedMeshRenderer>(true),
                animator = SelectValidAnimator(root)
            };
            if (watch.renderers.Length == 0)
            {
                // QuickAgentManager's non-humanoid primitive fallback cannot T-pose.
                LogStudyEvent("agent_pose_primitive", "animation", pair.Key, "", 1);
                continue;
            }
            poseWatches[root] = watch;
            foreach (var renderer in watch.renderers)
            {
                if (renderer != null)
                    renderer.enabled = false;
            }
            StartCoroutine(ValidateAndRevealPose(watch));
        }
    }

    private static Animator SelectValidAnimator(GameObject root)
    {
        var animators = root.GetComponentsInChildren<Animator>(true);
        foreach (var animator in animators)
        {
            if (animator != null
                && animator.avatar != null
                && animator.avatar.isValid
                && animator.avatar.isHuman)
                return animator;
        }
        return null;
    }

    private IEnumerator ValidateAndRevealPose(PoseWatch watch)
    {
        if (watch == null || watch.root == null)
            yield break;

        if (watch.animator != null
            && watch.animator.avatar != null
            && watch.animator.avatar.isValid
            && watch.animator.avatar.isHuman
            && HasCoreHumanoidBones(watch.animator))
        {
            DisableCoreAnimationGraph(watch.root);
            var clips = GetSafeIdleClips();
            var agentId = AgentIdForRoot(watch.root);
            // Start with the visibly animated Happy Idle clip. If a particular avatar
            // cannot retarget it, the remaining validated idles are tried in order.
            var startIndex = 0;

            for (var attempt = 0; attempt < clips.Length; attempt++)
            {
                var clip = clips[(startIndex + attempt) % clips.Length];
                if (!BindStudyIdle(watch, clip))
                    continue;

                // Renderers stay hidden through graph binding and the first evaluated
                // frames, so neither a bind pose nor a one-frame T-pose can flash.
                yield return null;
                yield return null;
                yield return new WaitForSecondsRealtime(0.06f);
                if (watch.root == null)
                    yield break;
                if (watch.animator.hasBoundPlayables && !LooksLikeTPose(watch.animator))
                {
                    RevealAgentRenderers(watch);
                    LogStudyEvent("agent_pose_ready", "animation", agentId, clip.name, 1);
                    yield break;
                }
            }
        }

        CreatePoseSafeFallback(watch.root);
        LogStudyEvent("agent_pose_fallback", "animation", AgentIdForRoot(watch.root), "", 0);
        Debug.LogWarning("[KAESESTEINPILZ Study] Invalid/T-pose animation hidden for " + watch.root.name);
    }

    private AnimationClip[] GetSafeIdleClips()
    {
        if (safeIdleClips != null)
            return safeIdleClips;
        var loaded = Resources.LoadAll<AnimationClip>(SafeAnimationFolder);
        var safe = new List<AnimationClip>();
        foreach (var clip in loaded)
        {
            if (clip != null && !clip.legacy && clip.isHumanMotion && clip.length > 0.1f)
                safe.Add(clip);
        }
        safe.Sort((left, right) =>
        {
            var priority = IdleClipPriority(left).CompareTo(IdleClipPriority(right));
            return priority != 0 ? priority : string.CompareOrdinal(left.name, right.name);
        });
        safeIdleClips = safe.ToArray();
        return safeIdleClips;
    }

    private static int IdleClipPriority(AnimationClip clip)
    {
        if (clip == null)
            return int.MaxValue;
        if (string.Equals(clip.name, "Happy Idle 1", StringComparison.OrdinalIgnoreCase))
            return 0;
        if (clip.name.IndexOf("Happy Idle", StringComparison.OrdinalIgnoreCase) >= 0)
            return 1;
        if (clip.name.IndexOf("Standing Idle", StringComparison.OrdinalIgnoreCase) >= 0)
            return 2;
        if (clip.name.IndexOf("Neutral Idle", StringComparison.OrdinalIgnoreCase) >= 0)
            return 3;
        return 4;
    }

    private static bool BindStudyIdle(PoseWatch watch, AnimationClip clip)
    {
        if (watch == null || watch.animator == null || clip == null)
            return false;
        if (watch.graph.IsValid())
            watch.graph.Destroy();

        try
        {
            var animator = watch.animator;
            animator.enabled = true;
            animator.applyRootMotion = false;
            animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
            animator.runtimeAnimatorController = null;
            animator.Rebind();
            animator.Update(0f);

            watch.graph = PlayableGraph.Create("IUIStudyIdle_" + watch.root.name);
            watch.graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);
            watch.playable = AnimationClipPlayable.Create(watch.graph, clip);
            watch.playable.SetApplyFootIK(true);
            watch.playable.SetDuration(double.PositiveInfinity);
            watch.playable.SetSpeed(0d);
            watch.clip = clip;
            watch.clipTime = Mathf.Min(0.18f, clip.length * 0.25f);
            watch.playable.SetTime(watch.clipTime);
            var output = AnimationPlayableOutput.Create(watch.graph, "Study Idle", animator);
            output.SetSourcePlayable(watch.playable);
            output.SetWeight(1f);
            watch.graph.Play();
            watch.graph.Evaluate(0f);
            return true;
        }
        catch (Exception exception)
        {
            if (watch.graph.IsValid())
                watch.graph.Destroy();
            Debug.LogWarning("[KAESESTEINPILZ Study] Idle binding failed: " + exception.Message);
            return false;
        }
    }

    private void AdvanceStudyIdleAnimations()
    {
        var delta = Math.Min(Math.Max(Time.unscaledDeltaTime, 0f), 0.1f);
        foreach (var watch in poseWatches.Values)
        {
            if (watch == null
                || watch.root == null
                || watch.clip == null
                || !watch.graph.IsValid()
                || !watch.playable.IsValid())
                continue;

            // Drive time explicitly. This keeps the idles moving in the editor, in a
            // paused/time-scaled study and in WebGL, independent of PlayableGraph clocks.
            watch.clipTime += delta;
            if (watch.clip.length > 0.01f)
                watch.clipTime %= watch.clip.length;
            watch.playable.SetTime(watch.clipTime);
            watch.graph.Evaluate(0f);
        }
    }

    private static void RevealAgentRenderers(PoseWatch watch)
    {
        foreach (var renderer in watch.renderers)
        {
            if (renderer != null)
                renderer.enabled = true;
        }
    }

    private void DisableCoreAnimationGraph(GameObject root)
    {
        var dictionary = GetCoreField<IDictionary>("agentObjects");
        if (dictionary == null)
            return;
        foreach (DictionaryEntry entry in dictionary)
        {
            var visual = entry.Value;
            if (visual == null)
                continue;
            var type = visual.GetType();
            var objectField = type.GetField("obj", CoreFlags);
            if (objectField?.GetValue(visual) as GameObject != root)
                continue;
            var graphField = type.GetField("animGraph", CoreFlags);
            if (graphField?.GetValue(visual) is PlayableGraph graph && graph.IsValid())
            {
                graph.Destroy();
                graphField.SetValue(visual, default(PlayableGraph));
            }
            return;
        }
    }

    private static bool HasCoreHumanoidBones(Animator animator)
    {
        return animator.GetBoneTransform(HumanBodyBones.Hips) != null
            && animator.GetBoneTransform(HumanBodyBones.Head) != null
            && animator.GetBoneTransform(HumanBodyBones.LeftUpperArm) != null
            && animator.GetBoneTransform(HumanBodyBones.RightUpperArm) != null
            && animator.GetBoneTransform(HumanBodyBones.LeftHand) != null
            && animator.GetBoneTransform(HumanBodyBones.RightHand) != null;
    }

    private static bool LooksLikeTPose(Animator animator)
    {
        var leftShoulder = animator.GetBoneTransform(HumanBodyBones.LeftUpperArm);
        var rightShoulder = animator.GetBoneTransform(HumanBodyBones.RightUpperArm);
        var leftHand = animator.GetBoneTransform(HumanBodyBones.LeftHand);
        var rightHand = animator.GetBoneTransform(HumanBodyBones.RightHand);
        if (leftShoulder == null || rightShoulder == null || leftHand == null || rightHand == null)
            return true;

        var shoulderWidth = Vector3.Distance(leftShoulder.position, rightShoulder.position);
        if (shoulderWidth < 0.05f)
            return true;
        var handSpan = Vector3.Distance(leftHand.position, rightHand.position);
        var handsAtShoulderHeight = Mathf.Abs(leftHand.position.y - leftShoulder.position.y) < shoulderWidth * 0.35f
            && Mathf.Abs(rightHand.position.y - rightShoulder.position.y) < shoulderWidth * 0.35f;
        return handsAtShoulderHeight && handSpan > shoulderWidth * 2.4f;
    }

    private static void CreatePoseSafeFallback(GameObject root)
    {
        if (root.transform.Find("PoseSafeFallback") != null)
            return;

        var fallback = new GameObject("PoseSafeFallback");
        fallback.transform.SetParent(root.transform, false);
        var cream = new Color(0.88f, 0.76f, 0.50f);
        var brown = new Color(0.30f, 0.18f, 0.10f);
        var skin = new Color(0.82f, 0.62f, 0.45f);
        var orange = new Color(0.78f, 0.34f, 0.12f);
        CreateFallbackPart("Body", PrimitiveType.Capsule, fallback.transform,
            new Vector3(0f, 0.92f, 0f), new Vector3(0.42f, 0.55f, 0.30f), Quaternion.identity, cream);
        CreateFallbackPart("Head", PrimitiveType.Sphere, fallback.transform,
            new Vector3(0f, 1.58f, 0f), Vector3.one * 0.34f, Quaternion.identity, skin);
        CreateFallbackPart("Mushroom cap", PrimitiveType.Sphere, fallback.transform,
            new Vector3(0f, 1.82f, 0f), new Vector3(0.58f, 0.18f, 0.50f), Quaternion.identity, orange);
        CreateFallbackPart("Left arm", PrimitiveType.Capsule, fallback.transform,
            new Vector3(-0.34f, 0.92f, 0f), new Vector3(0.11f, 0.36f, 0.11f),
            Quaternion.Euler(0f, 0f, -7f), cream);
        CreateFallbackPart("Right arm", PrimitiveType.Capsule, fallback.transform,
            new Vector3(0.34f, 0.92f, 0f), new Vector3(0.11f, 0.36f, 0.11f),
            Quaternion.Euler(0f, 0f, 7f), cream);
        CreateFallbackPart("Left leg", PrimitiveType.Capsule, fallback.transform,
            new Vector3(-0.16f, 0.30f, 0f), new Vector3(0.14f, 0.34f, 0.14f), Quaternion.identity, brown);
        CreateFallbackPart("Right leg", PrimitiveType.Capsule, fallback.transform,
            new Vector3(0.16f, 0.30f, 0f), new Vector3(0.14f, 0.34f, 0.14f), Quaternion.identity, brown);
    }

    private static void CreateFallbackPart(
        string name,
        PrimitiveType primitive,
        Transform parent,
        Vector3 position,
        Vector3 scale,
        Quaternion rotation,
        Color color)
    {
        var part = GameObject.CreatePrimitive(primitive);
        part.name = name;
        part.transform.SetParent(parent, false);
        part.transform.localPosition = position;
        part.transform.localRotation = rotation;
        part.transform.localScale = scale;
        var collider = part.GetComponent<Collider>();
        if (collider != null)
            Destroy(collider);
        var renderer = part.GetComponent<Renderer>();
        var shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
        if (renderer != null && shader != null)
        {
            renderer.material = new Material(shader);
            renderer.material.color = color;
        }
    }

    private string AgentIdForRoot(GameObject root)
    {
        foreach (var pair in GetAgentRoots())
        {
            if (pair.Value == root)
                return pair.Key;
        }
        return "";
    }

    private void SubscribeCoreEvents()
    {
        if (coreManager == null)
            return;
        coreManager.SpatialEventLogged -= HandleSpatialEvent;
        coreManager.SpatialEventLogged += HandleSpatialEvent;
        coreManager.InteractionEvidenceLogged -= HandleInteractionEvidence;
        coreManager.InteractionEvidenceLogged += HandleInteractionEvidence;
    }

    private void UnsubscribeCoreEvents()
    {
        if (coreManager == null)
            return;
        coreManager.SpatialEventLogged -= HandleSpatialEvent;
        coreManager.InteractionEvidenceLogged -= HandleInteractionEvidence;
    }

    private void HandleSpatialEvent(QuickAgentManager.SpatialSelectionEvent item)
    {
        if (item == null)
            return;
        if (string.Equals(item.state, FunctionalMldsSpatialTargetStates.Resolved,
                StringComparison.OrdinalIgnoreCase))
            inspectedObject = true;
        LogStudyEvent(item.event_type ?? "spatial_event", item.selection_modality,
            coreManager.activeAgentId, item.entity_id, 0);
    }

    private void HandleInteractionEvidence(FunctionalMlds.V2.FunctionalMldsV2InteractionAssessment assessment)
    {
        if (assessment == null)
            return;
        if (assessment.CompletionSatisfied
            && string.Equals(assessment.Verdict, "pass", StringComparison.OrdinalIgnoreCase))
            successfulInteractions++;
        LogStudyEvent("interaction_evidence", CurrentModality(), coreManager.activeAgentId,
            coreManager.SelectedSpatialEntityId, assessment.CompletionSatisfied ? 1 : 0);
    }

    private void RetrySetup()
    {
        if (coreManager == null)
            return;
        ConfigureCoreForStudy();
        var routine = InvokeCore("SetupFromServer", Type.EmptyTypes) as IEnumerator;
        if (routine != null)
            coreManager.StartCoroutine(routine);
        LogStudyEvent("setup_retried", CurrentModality(), "", "", 0);
    }

    private Dictionary<string, GameObject> GetAgentRoots()
    {
        var result = new Dictionary<string, GameObject>();
        var dictionary = GetCoreField<IDictionary>("agentObjects");
        if (dictionary == null)
            return result;

        foreach (DictionaryEntry entry in dictionary)
        {
            var id = entry.Key as string;
            var visual = entry.Value;
            if (string.IsNullOrWhiteSpace(id) || visual == null)
                continue;
            var field = visual.GetType().GetField("obj", CoreFlags);
            var root = field == null ? null : field.GetValue(visual) as GameObject;
            if (root != null)
                result[id] = root;
        }
        return result;
    }

    private string GetAgentDisplayName(string id)
    {
        var agents = GetCoreField<QuickAgentManager.AgentPlacement[]>("lastAgents");
        if (agents != null)
        {
            foreach (var agent in agents)
            {
                if (agent != null && string.Equals(agent.id, id, StringComparison.Ordinal))
                    return string.IsNullOrWhiteSpace(agent.display_name) ? id : agent.display_name;
            }
        }
        return id.Replace('_', ' ');
    }

    private void SetCoreField(string name, object value)
    {
        var field = typeof(QuickAgentManager).GetField(name, CoreFlags);
        if (field == null)
            throw new MissingFieldException(typeof(QuickAgentManager).FullName, name);
        field.SetValue(coreManager, value);
    }

    private T GetCoreField<T>(string name)
    {
        if (coreManager == null)
            return default;
        var field = typeof(QuickAgentManager).GetField(name, CoreFlags);
        if (field == null)
            return default;
        var value = field.GetValue(coreManager);
        return value is T typed ? typed : default;
    }

    private object InvokeCore(string name, Type[] signature, params object[] arguments)
    {
        if (coreManager == null)
            return null;
        var key = name + "(" + string.Join(",", Array.ConvertAll(signature, t => t.FullName)) + ")";
        if (!methodCache.TryGetValue(key, out var method))
        {
            method = typeof(QuickAgentManager).GetMethod(name, CoreFlags, null, signature, null);
            methodCache[key] = method;
        }
        if (method == null)
            throw new MissingMethodException(typeof(QuickAgentManager).FullName, key);
        return method.Invoke(coreManager, arguments);
    }

    private void ShowToast(string message, float seconds)
    {
        if (toastLabel == null)
            return;
        if (toastCoroutine != null)
            StopCoroutine(toastCoroutine);
        toastCoroutine = StartCoroutine(ShowToastRoutine(message, seconds));
    }

    private IEnumerator ShowToastRoutine(string message, float seconds)
    {
        toastLabel.text = message;
        toastLabel.gameObject.SetActive(true);
        yield return new WaitForSecondsRealtime(Mathf.Max(0.5f, seconds));
        toastLabel.gameObject.SetActive(false);
        toastCoroutine = null;
    }

    private void SetPointerLock(bool locked)
    {
        pointerLocked = locked && !touchLayout && !xrActive;
        Cursor.lockState = pointerLocked ? CursorLockMode.Locked : CursorLockMode.None;
        Cursor.visible = !pointerLocked;
    }

    private string CurrentModality()
    {
        if (xrActive)
            return "webxr";
        return touchLayout ? "touch" : "desktop";
    }

    private void LogStudyEvent(
        string eventName,
        string modality,
        string agentId,
        string targetId,
        int value)
    {
        if (!recordAnonymousStudyEvents || string.IsNullOrWhiteSpace(studyLogPath))
            return;
        var entry = new StudyLogEntry
        {
            utc = DateTime.UtcNow.ToString("o"),
            participant = participantCode,
            event_name = eventName ?? "event",
            modality = modality ?? "",
            agent_id = agentId ?? "",
            target_id = targetId ?? "",
            value = value,
            seconds = Time.realtimeSinceStartup
        };
        try
        {
            File.AppendAllText(studyLogPath, JsonUtility.ToJson(entry) + Environment.NewLine);
        }
        catch (Exception exception)
        {
            Debug.LogWarning("[KAESESTEINPILZ Study] Event log unavailable: " + exception.Message);
            recordAnonymousStudyEvents = false;
        }
    }

    private static int StableHash(string value)
    {
        unchecked
        {
            var hash = 23;
            foreach (var character in value ?? "")
                hash = hash * 31 + character;
            return hash;
        }
    }

    private GameObject NewUiObject(string name, Transform parent)
    {
        var result = new GameObject(name, typeof(RectTransform));
        result.layer = LayerMask.NameToLayer("UI");
        result.transform.SetParent(parent, false);
        return result;
    }

    private RectTransform CreatePanel(string name, Transform parent, Color color)
    {
        var result = NewUiObject(name, parent);
        result.AddComponent<Image>().color = color;
        var shadow = result.AddComponent<Shadow>();
        shadow.effectColor = new Color(0f, 0f, 0f, 0.22f);
        shadow.effectDistance = new Vector2(0f, -3f);
        return result.GetComponent<RectTransform>();
    }

    private Text CreateText(
        string name,
        Transform parent,
        string value,
        int size,
        FontStyle style,
        TextAnchor alignment,
        Color color)
    {
        var result = NewUiObject(name, parent).AddComponent<Text>();
        result.font = uiFont;
        result.text = value;
        result.fontSize = size;
        result.fontStyle = style;
        result.alignment = alignment;
        result.color = color;
        result.horizontalOverflow = HorizontalWrapMode.Wrap;
        result.verticalOverflow = VerticalWrapMode.Truncate;
        result.raycastTarget = false;
        Stretch(result.rectTransform);
        return result;
    }

    private Button CreateButton(string name, Transform parent, string label, Color color)
    {
        var result = NewUiObject(name, parent);
        var image = result.AddComponent<Image>();
        image.color = color;
        var button = result.AddComponent<Button>();
        var colors = button.colors;
        colors.normalColor = color;
        colors.highlightedColor = Color.Lerp(color, Color.white, 0.16f);
        colors.pressedColor = Color.Lerp(color, Color.black, 0.18f);
        colors.disabledColor = new Color(color.r, color.g, color.b, 0.35f);
        button.colors = colors;
        var text = CreateText("Label", result.transform, label, 14, FontStyle.Bold,
            TextAnchor.MiddleCenter, Color.white);
        Stretch(text.rectTransform, new Vector2(5f, 2f), new Vector2(-5f, -2f));
        return button;
    }

    private static void Stretch(RectTransform rect, Vector2? offsetMin = null, Vector2? offsetMax = null)
    {
        rect.anchorMin = Vector2.zero;
        rect.anchorMax = Vector2.one;
        rect.offsetMin = offsetMin ?? Vector2.zero;
        rect.offsetMax = offsetMax ?? Vector2.zero;
    }

    private static void SetRect(
        RectTransform rect,
        Vector2 anchorMin,
        Vector2 anchorMax,
        Vector2? offsetMin = null,
        Vector2? offsetMax = null)
    {
        rect.anchorMin = anchorMin;
        rect.anchorMax = anchorMax;
        rect.offsetMin = offsetMin ?? Vector2.zero;
        rect.offsetMax = offsetMax ?? Vector2.zero;
    }
}

/// <summary>Pointer-driven virtual stick that works with mouse, touch and WebGL.</summary>
[Preserve]
public sealed class IuiStudyVirtualStick : MonoBehaviour,
    IPointerDownHandler, IDragHandler, IPointerUpHandler
{
    public event Action<Vector2> ValueChanged;
    private RectTransform rect;

    private void Awake()
    {
        rect = transform as RectTransform;
    }

    public void OnPointerDown(PointerEventData eventData)
    {
        UpdateValue(eventData);
    }

    public void OnDrag(PointerEventData eventData)
    {
        UpdateValue(eventData);
    }

    public void OnPointerUp(PointerEventData eventData)
    {
        ValueChanged?.Invoke(Vector2.zero);
    }

    private void UpdateValue(PointerEventData eventData)
    {
        if (rect == null || !RectTransformUtility.ScreenPointToLocalPointInRectangle(
                rect, eventData.position, eventData.pressEventCamera, out var local))
            return;
        var radius = Mathf.Max(1f, Mathf.Min(rect.rect.width, rect.rect.height) * 0.46f);
        ValueChanged?.Invoke(Vector2.ClampMagnitude(local / radius, 1f));
    }
}

/// <summary>Drag-look surface with a short-tap world-selection gesture.</summary>
[Preserve]
public sealed class IuiStudyLookSurface : MonoBehaviour,
    IPointerDownHandler, IDragHandler, IPointerUpHandler
{
    public event Action<Vector2> Dragged;
    public event Action<Vector2> Tapped;
    private Vector2 pressPosition;
    private float pressTime;
    private float travelled;

    public void OnPointerDown(PointerEventData eventData)
    {
        pressPosition = eventData.position;
        pressTime = Time.unscaledTime;
        travelled = 0f;
    }

    public void OnDrag(PointerEventData eventData)
    {
        travelled += eventData.delta.magnitude;
        Dragged?.Invoke(eventData.delta);
    }

    public void OnPointerUp(PointerEventData eventData)
    {
        if (Time.unscaledTime - pressTime <= 0.28f && travelled < 18f)
            Tapped?.Invoke(eventData.position);
    }
}
