using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

#if UNITY_EDITOR
using UnityEditor;
#endif

#if UNITY_EDITOR
public class ArrowProjectWizard : EditorWindow
{
    private enum GenerationMode
    {
        Legacy = 0,
        FunctionalMLDS = 1,
    }

    private static readonly string[] GenerationModeLabels =
    {
        "Legacy Interactive Agents",
        "FunctionalMLDS",
    };

    [Serializable]
    public class AnalyzeRequest
    {
        public string arrow_json;
        public string generation_mode;
        public string project_id_hint;
        public bool run_validation;
        public int max_repair_attempts;
    }

    [Serializable]
    public class ChatRequest
    {
        public string session_id;
        public string user_text;
        public string generation_mode;
    }

    [Serializable]
    public class CommitRequest
    {
        public string session_id;
        public string generation_mode;
        public string display_name;
        public string project_id;
        public string description;
    }

    [Serializable]
    public class HealthResponse
    {
        public string status;
        public string backend_version;
        public string api_version;
        public string version;
        public string application_version;
    }

    [Serializable]
    public class PlacementUpdateItem
    {
        public string id;
        public Vector3Data position;
        public Vector3Data forward;
    }

    [Serializable]
    public class PlacementUpdateRequest
    {
        public string session_id;
        public string generation_mode;
        public PlacementUpdateItem[] agent_placements;
    }

    [Serializable]
    public class PlacementValidation
    {
        public string status;
        public string[] errors;
        public string[] warnings;
    }

    [Serializable]
    public class PlacementUpdateResponse
    {
        public string status;
        public string generation_mode;
        public PlacementPreview placement_preview;
        public PlacementValidation validation;
    }

    [Serializable]
    public class DraftProject
    {
        public string display_name;
        public string description;
    }

    [Serializable]
    public class Vector3Data
    {
        public float x;
        public float y;
        public float z;
    }

    [Serializable]
    public class PlacementSummary
    {
        public string id;
        public string display_name;
        public Vector3Data position;
        public Vector3Data forward;
        public string spawn_point_id;
        public string zone_id;
        public string[] tags;
    }

    [Serializable]
    public class PlacementPreview
    {
        public RoomObjectSummary[] room_objects;
        public PlacementSummary[] agent_placements;
        public RoomBounds room_bounds;  // populated for MLDS scenes
    }

    [Serializable]
    public class RoomObjectSummary
    {
        public string id;
        public string name;
        public Vector3Data position;
        public float radius;
        public float width;   // MLDS: actual footprint width (X)
        public float depth;   // MLDS: actual footprint depth (Z)
    }

    [Serializable]
    public class RoomBounds
    {
        public float min_x;
        public float max_x;
        public float min_z;
        public float max_z;
    }

    [Serializable]
    public class AgentSpec
    {
        public string id;
        public string display_name;
        public string persona;
        public string[] expertise;
        public string[] knowledge_tags;
        public string voice;
        public string voice_style;
        public string voice_gender;
        public string tts_model;
    }

    [Serializable]
    public class KnowledgeEntry
    {
        public string tag;
        public string name;
        public string text;
    }

    [Serializable]
    public class FunctionalMldsSummary
    {
        public string case_id;
        public string schema;
        public string metamodel_version;
        public string use_case_id;
        public string main_scenario_id;
        public int actor_count;
        public int entity_count;
        public int agent_count;
        public int capability_count;
        public int runtime_binding_count;
        public int validation_case_count;
        public int satisfy_relationship_count;
    }

    [Serializable]
    public class ValidationSummary
    {
        public string status;
        public string schema_status;
        public string invariant_status;
        public string materialization_status;
        public string traceability_status;
        public string handoff_status;
        public int error_count;
        public int warning_count;
        public float traceability_average_coverage;
        public float handoff_decision_accuracy;
        public string[] errors;
        public string[] warnings;
    }

    [Serializable]
    public class ScenarioSummary
    {
        public string use_case_id;
        public string main_scenario_id;
        public string goal;
        public int step_count;
        public int validation_case_count;
    }

    [Serializable]
    public class CapabilitySummaryItem
    {
        public string id;
        public int runtime_binding_count;
    }

    [Serializable]
    public class CapabilitySummary
    {
        public int capability_count;
        public int runtime_binding_count;
        public int runtime_action_count;
        public CapabilitySummaryItem[] capabilities;
    }

    [Serializable]
    public class HandoffSummary
    {
        public int agent_count;
        public int declared_handoff_pair_count;
        public float valid_handoff_target_ratio;
        public float handoff_decision_accuracy;
        public int self_handoff_count;
    }

    [Serializable]
    public class RoomKnowledgeSummary
    {
        public int room_object_count;
        public int semantic_zone_count;
        public int knowledge_file_count;
        public float agent_to_knowledge_tag_coverage;
        public float object_group_to_agent_role_grounding;
        public string[] important_object_groups;
        public string[] semantic_zones;
    }

    [Serializable]
    public class RefinementRequest
    {
        public string id;
        public string role;
        public string content;
        public string status;
        public long created_ms;
    }

    [Serializable]
    public class DraftResponse
    {
        public string generation_mode;
        public bool validation_stale;
        public string refinement_status;
        public string analysis;
        public string assistant_message;
        public DraftProject project;
        public AgentSpec[] agents;
        public KnowledgeEntry[] knowledge;
        public PlacementPreview placement_preview;
        public FunctionalMldsSummary functionalmlds_summary;
        public string functionalmlds_path;
        public string trace_map_path;
        public ValidationSummary validation_summary;
        public ScenarioSummary scenario_summary;
        public CapabilitySummary capability_summary;
        public HandoffSummary handoff_summary;
        public RoomKnowledgeSummary room_knowledge_summary;
        public RefinementRequest[] refinement_requests;
    }

    [Serializable]
    public class AnalyzeResponse
    {
        public string session_id;
        public DraftResponse draft;
    }

    [Serializable]
    public class ChatResponse
    {
        public DraftResponse draft;
    }

    [Serializable]
    public class ProjectMetadata
    {
        public string id;
        public string display_name;
        public string description;
    }

    [Serializable]
    public class CommitResponse
    {
        public string status;
        public string generation_mode;
        public ProjectMetadata project;
        public PlacementSummary[] placements;
        public RoomObjectSummary[] room_objects;
        public RoomBounds room_bounds;
        public string functionalmlds_path;
        public string trace_map_path;
        public ValidationSummary validation_summary;
        public FunctionalMldsSummary functionalmlds_summary;
    }

    private class EditorCoroutine
    {
        private readonly Stack<IEnumerator> routineStack = new Stack<IEnumerator>();

        public EditorCoroutine(IEnumerator routine)
        {
            if (routine != null)
            {
                routineStack.Push(routine);
            }
        }

        public bool MoveNext()
        {
            while (routineStack.Count > 0)
            {
                var current = routineStack.Peek();
                if (!current.MoveNext())
                {
                    routineStack.Pop();
                    continue;
                }

                if (current.Current is IEnumerator nested)
                {
                    routineStack.Push(nested);
                    return true;
                }

                if (current.Current is AsyncOperation asyncOp)
                {
                    routineStack.Push(WaitForAsync(asyncOp));
                    return true;
                }

                return true;
            }
            return false;
        }

        private IEnumerator WaitForAsync(AsyncOperation op)
        {
            while (!op.isDone)
            {
                yield return null;
            }
        }
    }

    private static readonly List<EditorCoroutine> ActiveCoroutines = new List<EditorCoroutine>();

    private const string DefaultBackendUrl = "http://127.0.0.1:8787";
    private const float PlacementWallMargin = 0.45f;
    private const float PlacementMapPadding = 0.8f;
    private const float PlacementMarkerRadius = 7f;
    private const float PlacementHitRadius = 11f;
    private const float ForwardHandleRadius = 7f;

    private enum PlacementDragMode
    {
        None,
        Position,
        Forward,
    }

    [SerializeField]
    private string backendBaseUrl = DefaultBackendUrl;

    [SerializeField]
    private GenerationMode generationMode = GenerationMode.Legacy;

    private string arrowFilePath = "";
    private string arrowJson = "";
    private string statusMessage = "";
    private string sessionId = "";
    private DraftResponse draft;

    private string chatInput = "";
    private readonly List<string> chatLog = new List<string>();
    private Vector2 scroll;
    private Vector2 chatScroll;

    private string projectDisplayName = "";
    private string projectId = "";
    private string projectDescription = "";
    private bool isAnalyzing;
    private bool isChatting;
    private bool isCommitting;
    private bool isCheckingHealth;
    private bool isApplyingPlacement;
    private string committedProjectId = "";
    private CommitResponse lastCommitResponse;
    private Texture2D _previewTex;
    private string backendHealthStatus = "Noch nicht geprueft";
    private string backendVersion = "-";
    private string backendApiVersion = "-";
    private PlacementPreview canonicalPlacementPreview;
    private bool placementDirty;
    private string placementStatus = "";
    private MessageType placementStatusType = MessageType.Info;
    private string selectedPlacementId = "";
    private string draggingPlacementId = "";
    private PlacementDragMode placementDragMode = PlacementDragMode.None;

    private static readonly Dictionary<char, string[]> ExportGlyphs = new Dictionary<char, string[]>
    {
        { ' ', new[] { "00000", "00000", "00000", "00000", "00000", "00000", "00000" } },
        { 'A', new[] { "01110", "10001", "10001", "11111", "10001", "10001", "10001" } },
        { 'B', new[] { "11110", "10001", "10001", "11110", "10001", "10001", "11110" } },
        { 'C', new[] { "01111", "10000", "10000", "10000", "10000", "10000", "01111" } },
        { 'D', new[] { "11110", "10001", "10001", "10001", "10001", "10001", "11110" } },
        { 'E', new[] { "11111", "10000", "10000", "11110", "10000", "10000", "11111" } },
        { 'F', new[] { "11111", "10000", "10000", "11110", "10000", "10000", "10000" } },
        { 'G', new[] { "01111", "10000", "10000", "10111", "10001", "10001", "01111" } },
        { 'H', new[] { "10001", "10001", "10001", "11111", "10001", "10001", "10001" } },
        { 'I', new[] { "11111", "00100", "00100", "00100", "00100", "00100", "11111" } },
        { 'J', new[] { "00111", "00010", "00010", "00010", "10010", "10010", "01100" } },
        { 'K', new[] { "10001", "10010", "10100", "11000", "10100", "10010", "10001" } },
        { 'L', new[] { "10000", "10000", "10000", "10000", "10000", "10000", "11111" } },
        { 'M', new[] { "10001", "11011", "10101", "10101", "10001", "10001", "10001" } },
        { 'N', new[] { "10001", "11001", "10101", "10011", "10001", "10001", "10001" } },
        { 'O', new[] { "01110", "10001", "10001", "10001", "10001", "10001", "01110" } },
        { 'P', new[] { "11110", "10001", "10001", "11110", "10000", "10000", "10000" } },
        { 'Q', new[] { "01110", "10001", "10001", "10001", "10101", "10010", "01101" } },
        { 'R', new[] { "11110", "10001", "10001", "11110", "10100", "10010", "10001" } },
        { 'S', new[] { "01111", "10000", "10000", "01110", "00001", "00001", "11110" } },
        { 'T', new[] { "11111", "00100", "00100", "00100", "00100", "00100", "00100" } },
        { 'U', new[] { "10001", "10001", "10001", "10001", "10001", "10001", "01110" } },
        { 'V', new[] { "10001", "10001", "10001", "10001", "10001", "01010", "00100" } },
        { 'W', new[] { "10001", "10001", "10001", "10101", "10101", "10101", "01010" } },
        { 'X', new[] { "10001", "10001", "01010", "00100", "01010", "10001", "10001" } },
        { 'Y', new[] { "10001", "10001", "01010", "00100", "00100", "00100", "00100" } },
        { 'Z', new[] { "11111", "00001", "00010", "00100", "01000", "10000", "11111" } },
        { '0', new[] { "01110", "10001", "10011", "10101", "11001", "10001", "01110" } },
        { '1', new[] { "00100", "01100", "00100", "00100", "00100", "00100", "01110" } },
        { '2', new[] { "01110", "10001", "00001", "00010", "00100", "01000", "11111" } },
        { '3', new[] { "11110", "00001", "00001", "01110", "00001", "00001", "11110" } },
        { '4', new[] { "00010", "00110", "01010", "10010", "11111", "00010", "00010" } },
        { '5', new[] { "11111", "10000", "10000", "11110", "00001", "00001", "11110" } },
        { '6', new[] { "01110", "10000", "10000", "11110", "10001", "10001", "01110" } },
        { '7', new[] { "11111", "00001", "00010", "00100", "01000", "01000", "01000" } },
        { '8', new[] { "01110", "10001", "10001", "01110", "10001", "10001", "01110" } },
        { '9', new[] { "01110", "10001", "10001", "01111", "00001", "00001", "01110" } },
        { '[', new[] { "01110", "01000", "01000", "01000", "01000", "01000", "01110" } },
        { ']', new[] { "01110", "00010", "00010", "00010", "00010", "00010", "01110" } },
        { '(', new[] { "00010", "00100", "01000", "01000", "01000", "00100", "00010" } },
        { ')', new[] { "01000", "00100", "00010", "00010", "00010", "00100", "01000" } },
        { '_', new[] { "00000", "00000", "00000", "00000", "00000", "00000", "11111" } },
        { '-', new[] { "00000", "00000", "00000", "11111", "00000", "00000", "00000" } },
        { '.', new[] { "00000", "00000", "00000", "00000", "00000", "00110", "00110" } },
        { ':', new[] { "00000", "00110", "00110", "00000", "00110", "00110", "00000" } },
        { '/', new[] { "00001", "00010", "00010", "00100", "01000", "01000", "10000" } },
        { '?', new[] { "01110", "10001", "00001", "00010", "00100", "00000", "00100" } },
    };

    [MenuItem("Tools/MLDSI Project Wizard")]
    public static void ShowWindow()
    {
        var window = GetWindow<ArrowProjectWizard>("MLDSI Project Wizard");
        window.minSize = new Vector2(620, 620);
    }

    private void OnEnable()
    {
        EditorApplication.update += TickCoroutines;
        RefreshBackendHealth();
    }

    private void OnDisable()
    {
        EditorApplication.update -= TickCoroutines;
        ActiveCoroutines.Clear();
        isCheckingHealth = false;
        isApplyingPlacement = false;
        placementDragMode = PlacementDragMode.None;
        draggingPlacementId = "";
        if (_previewTex != null) { DestroyImmediate(_previewTex); _previewTex = null; }
    }

    private static void TickCoroutines()
    {
        for (int i = ActiveCoroutines.Count - 1; i >= 0; i--)
        {
            if (!ActiveCoroutines[i].MoveNext())
            {
                ActiveCoroutines.RemoveAt(i);
            }
        }
    }

    private void OnGUI()
    {
        scroll = EditorGUILayout.BeginScrollView(scroll);

        EditorGUILayout.LabelField("Backend", EditorStyles.boldLabel);
        backendBaseUrl = EditorGUILayout.TextField("Backend Base Url", backendBaseUrl);
        DrawVersionAndBackendStatus();

        DrawGenerationModeSection();

        EditorGUILayout.Space();
        EditorGUILayout.LabelField("MLDSI-Datei", EditorStyles.boldLabel);
        DrawDropZone();

        if (!string.IsNullOrEmpty(arrowFilePath))
        {
            EditorGUILayout.LabelField("Datei", arrowFilePath);
        }

        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("MLDSI analysieren", GUILayout.Height(28)))
        {
            StartAnalyze();
        }
        if (GUILayout.Button("Zurücksetzen", GUILayout.Height(28)))
        {
            ResetState();
        }
        EditorGUILayout.EndHorizontal();

        if (!string.IsNullOrEmpty(statusMessage))
        {
            EditorGUILayout.HelpBox(statusMessage, MessageType.Info);
        }
        DrawLoadingIndicator();

        DrawDraft();
        DrawChat();
        DrawCommitSection();

        EditorGUILayout.EndScrollView();
    }

    private void DrawVersionAndBackendStatus()
    {
        EditorGUILayout.BeginVertical("box");
        EditorGUILayout.LabelField("MLDSI Wizard", $"v{InteractiveAgentsVersion.WizardVersion}");
        EditorGUILayout.LabelField("Backend-Status", backendHealthStatus, EditorStyles.wordWrappedLabel);
        EditorGUILayout.LabelField("Backend-Version", backendVersion);
        EditorGUILayout.LabelField("API-Version", backendApiVersion);
        using (new EditorGUI.DisabledScope(isCheckingHealth))
        {
            if (GUILayout.Button(isCheckingHealth ? "Backend wird geprueft..." : "Backend-Status aktualisieren"))
            {
                RefreshBackendHealth();
            }
        }
        EditorGUILayout.EndVertical();
    }

    private void DrawGenerationModeSection()
    {
        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Projektmodus", EditorStyles.boldLabel);
        var selected = GUILayout.Toolbar((int)generationMode, GenerationModeLabels, GUILayout.Height(24));
        var nextMode = (GenerationMode)Mathf.Clamp(selected, 0, GenerationModeLabels.Length - 1);
        if (nextMode != generationMode)
        {
            SetGenerationMode(nextMode);
        }
    }

    private void SetGenerationMode(GenerationMode nextMode)
    {
        generationMode = nextMode;
        ClearDraftState($"Modus gewechselt zu {GenerationModeDisplayName(generationMode)}. Bitte neu analysieren.");
    }

    private static string GenerationModeDisplayName(GenerationMode mode)
    {
        return mode == GenerationMode.FunctionalMLDS
            ? "FunctionalMLDS"
            : "Legacy Interactive Agents";
    }

    private static string GenerationModeRequestValue(GenerationMode mode)
    {
        return mode == GenerationMode.FunctionalMLDS ? "functionalmlds" : "legacy";
    }

    private void DrawDropZone()
    {
        var dropRect = GUILayoutUtility.GetRect(0f, 60f, GUILayout.ExpandWidth(true));
        GUI.Box(dropRect, "MLDSI-JSON hierhin ziehen");

        var evt = Event.current;
        if (!dropRect.Contains(evt.mousePosition))
        {
            return;
        }

        if (evt.type == EventType.DragUpdated || evt.type == EventType.DragPerform)
        {
            DragAndDrop.visualMode = DragAndDropVisualMode.Copy;
            if (evt.type == EventType.DragPerform)
            {
                DragAndDrop.AcceptDrag();
                foreach (var obj in DragAndDrop.objectReferences)
                {
                    var path = AssetDatabase.GetAssetPath(obj);
                    if (string.IsNullOrEmpty(path))
                    {
                        continue;
                    }
                    if (path.EndsWith(".json", StringComparison.OrdinalIgnoreCase)
                        || path.EndsWith(".mldsi", StringComparison.OrdinalIgnoreCase))
                    {
                        LoadArrowFile(path);
                        break;
                    }
                }
            }
            evt.Use();
        }
    }

    private void DrawDraft()
    {
        if (draft == null)
        {
            return;
        }

        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Analyse", EditorStyles.boldLabel);
        if (!string.IsNullOrEmpty(draft.assistant_message))
        {
            EditorGUILayout.HelpBox(draft.assistant_message, MessageType.None);
        }

        if (!string.IsNullOrEmpty(draft.analysis))
        {
            var wordWrapStyle = new GUIStyle(EditorStyles.textArea) { wordWrap = true };
            EditorGUILayout.TextArea(draft.analysis, wordWrapStyle, GUILayout.MinHeight(80));
        }

        DrawDraftValidationState();
        DrawFunctionalMldsDraftSummary();

        if (draft.agents != null && draft.agents.Length > 0)
        {
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Vorgeschlagene Agenten", EditorStyles.boldLabel);
            foreach (var agent in draft.agents)
            {
                EditorGUILayout.BeginVertical("box");
                EditorGUILayout.LabelField($"{agent.display_name} ({agent.id})", EditorStyles.wordWrappedLabel);
                if (!string.IsNullOrEmpty(agent.persona))
                {
                    EditorGUILayout.LabelField("Persona", agent.persona, EditorStyles.wordWrappedLabel);
                }
                if (agent.expertise != null && agent.expertise.Length > 0)
                {
                    EditorGUILayout.LabelField("Expertise", string.Join(", ", agent.expertise), EditorStyles.wordWrappedLabel);
                }
                if (agent.knowledge_tags != null && agent.knowledge_tags.Length > 0)
                {
                    EditorGUILayout.LabelField("Knowledge Tags", string.Join(", ", agent.knowledge_tags), EditorStyles.wordWrappedLabel);
                }
                if (!string.IsNullOrEmpty(agent.voice_gender))
                {
                    EditorGUILayout.LabelField("Stimmgeschlecht", agent.voice_gender, EditorStyles.wordWrappedLabel);
                }
                if (!string.IsNullOrEmpty(agent.voice_style))
                {
                    EditorGUILayout.LabelField("Stimmtonalität", agent.voice_style, EditorStyles.wordWrappedLabel);
                }
                if (!string.IsNullOrEmpty(agent.tts_model))
                {
                    EditorGUILayout.LabelField("TTS-Modell", agent.tts_model, EditorStyles.wordWrappedLabel);
                }
                EditorGUILayout.EndVertical();
            }
        }

        if (draft.knowledge != null && draft.knowledge.Length > 0)
        {
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Wissenseinträge", EditorStyles.boldLabel);
            foreach (var knowledge in draft.knowledge)
            {
                EditorGUILayout.BeginVertical("box");
                EditorGUILayout.LabelField($"{knowledge.tag}/{knowledge.name}", EditorStyles.wordWrappedLabel);
                if (!string.IsNullOrEmpty(knowledge.text))
                {
                    var wordWrapStyle = new GUIStyle(EditorStyles.textArea) { wordWrap = true };
                    EditorGUILayout.TextArea(knowledge.text, wordWrapStyle, GUILayout.MinHeight(60));
                }
                EditorGUILayout.EndVertical();
            }
        }

        if (draft.placement_preview != null
            && draft.placement_preview.room_objects != null
            && draft.placement_preview.agent_placements != null)
        {
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Platzierungsvorschau", EditorStyles.boldLabel);
            DrawPlacementPreview(
                draft.placement_preview.room_objects,
                draft.placement_preview.agent_placements,
                draft.placement_preview.room_bounds
            );
        }
    }

    private void DrawFunctionalMldsDraftSummary()
    {
        if (!ShouldDrawFunctionalMldsDraft())
        {
            return;
        }

        EditorGUILayout.Space();
        EditorGUILayout.LabelField("FunctionalMLDS", EditorStyles.boldLabel);

        if (!HasFunctionalMldsData(draft))
        {
            EditorGUILayout.HelpBox(
                "FunctionalMLDS-Modus ist ausgewaehlt, aber die Backend-Antwort enthaelt keine FunctionalMLDS-Artefakte oder Validierungsdaten. "
                + "Das ist nicht der erwartete Endzustand. Bitte pruefe, ob das Python-Backend neu gestartet wurde und die aktuelle FunctionalMLDS-Version laeuft.",
                MessageType.Warning
            );
            return;
        }

        DrawFunctionalMldsModelBox();
        DrawFunctionalMldsValidationBox();
        DrawFunctionalMldsScenarioBox();
        DrawFunctionalMldsCapabilityBox();
        DrawFunctionalMldsHandoffBox();
        DrawFunctionalMldsRoomKnowledgeBox();
    }

    private void DrawDraftValidationState()
    {
        if (!ShouldDrawFunctionalMldsDraft())
        {
            return;
        }

        if (draft.validation_stale)
        {
            var count = draft.refinement_requests != null ? draft.refinement_requests.Length : 0;
            var message = count > 0
                ? $"Dieser FunctionalMLDS-Draft ist eine Preview und nicht final validiert. {count} vorgemerkte Chat-Aenderung(en) muessen beim Commit durch eine vollstaendige Regeneration und erneute Validierung laufen."
                : "Dieser FunctionalMLDS-Draft ist eine Preview und nicht final validiert. Beim Commit muss die Pipeline erneut validieren.";
            EditorGUILayout.HelpBox(message, MessageType.Warning);
            DrawRefinementRequests();
            return;
        }

        if (string.Equals(draft.refinement_status, "validated", StringComparison.OrdinalIgnoreCase)
            && HasFunctionalMldsData(draft))
        {
            EditorGUILayout.HelpBox(
                "Dieser FunctionalMLDS-Draft basiert auf dem zuletzt validierten Analyse-Stand.",
                MessageType.Info
            );
        }
    }

    private void DrawRefinementRequests()
    {
        if (draft?.refinement_requests == null || draft.refinement_requests.Length == 0)
        {
            return;
        }

        EditorGUILayout.BeginVertical("box");
        EditorGUILayout.LabelField("Vorgemerkte Chat-Aenderungen", EditorStyles.miniBoldLabel);
        var count = Mathf.Min(draft.refinement_requests.Length, 5);
        for (int i = 0; i < count; i++)
        {
            var request = draft.refinement_requests[i];
            if (request == null)
            {
                continue;
            }

            var title = string.IsNullOrEmpty(request.id) ? $"Aenderung {i + 1}" : request.id;
            var status = string.IsNullOrEmpty(request.status) ? "pending" : request.status;
            EditorGUILayout.LabelField($"{title} ({status})", EditorStyles.wordWrappedLabel);
            if (!string.IsNullOrEmpty(request.content))
            {
                EditorGUILayout.LabelField(request.content, EditorStyles.wordWrappedLabel);
            }
        }
        if (draft.refinement_requests.Length > count)
        {
            EditorGUILayout.LabelField($"... plus {draft.refinement_requests.Length - count} weitere", EditorStyles.wordWrappedLabel);
        }
        EditorGUILayout.EndVertical();
    }

    private bool ShouldDrawFunctionalMldsDraft()
    {
        return generationMode == GenerationMode.FunctionalMLDS
            || string.Equals(draft?.generation_mode, "functionalmlds", StringComparison.OrdinalIgnoreCase)
            || HasFunctionalMldsData(draft);
    }

    private static bool HasFunctionalMldsData(DraftResponse response)
    {
        return response != null
            && (
                response.functionalmlds_summary != null
                || response.validation_summary != null
                || response.scenario_summary != null
                || response.capability_summary != null
                || response.handoff_summary != null
                || response.room_knowledge_summary != null
                || !string.IsNullOrEmpty(response.functionalmlds_path)
                || !string.IsNullOrEmpty(response.trace_map_path)
            );
    }

    private void DrawFunctionalMldsModelBox()
    {
        var summary = draft.functionalmlds_summary;
        if (summary == null && string.IsNullOrEmpty(draft.functionalmlds_path) && string.IsNullOrEmpty(draft.trace_map_path))
        {
            return;
        }

        EditorGUILayout.BeginVertical("box");
        EditorGUILayout.LabelField("Metamodell-Artefakte", EditorStyles.boldLabel);
        if (summary != null)
        {
            DrawValue("Case", summary.case_id);
            DrawValue("Schema", summary.schema);
            DrawValue("Metamodell-Version", summary.metamodel_version);
            DrawValue("Use Case", summary.use_case_id);
            DrawValue("Szenario", summary.main_scenario_id);
            DrawValue("Akteure", summary.actor_count);
            DrawValue("Entitaeten", summary.entity_count);
            DrawValue("Agenten", summary.agent_count);
            DrawValue("Capabilities", summary.capability_count);
            DrawValue("Runtime Bindings", summary.runtime_binding_count);
            DrawValue("Validation Cases", summary.validation_case_count);
            DrawValue("Satisfy-Beziehungen", summary.satisfy_relationship_count);
        }
        DrawPath("FunctionalMLDS", draft.functionalmlds_path);
        DrawPath("Trace Map", draft.trace_map_path);
        EditorGUILayout.EndVertical();
    }

    private void DrawFunctionalMldsValidationBox()
    {
        var validation = draft.validation_summary;
        if (validation == null)
        {
            return;
        }

        EditorGUILayout.BeginVertical("box");
        EditorGUILayout.LabelField("Validierung", EditorStyles.boldLabel);
        if (draft.validation_stale)
        {
            DrawRequiredValue("Draft-Status", "nicht final validiert");
        }
        DrawValue("Gesamtstatus", validation.status);
        DrawValue("Schema", validation.schema_status);
        DrawValue("Invarianten", validation.invariant_status);
        DrawValue("Materialisierung", validation.materialization_status);
        DrawValue("Traceability", validation.traceability_status);
        DrawValue("Handoff", validation.handoff_status);
        DrawValue("Fehler", validation.error_count);
        DrawValue("Warnungen", validation.warning_count);
        DrawPercent("Traceability-Abdeckung", validation.traceability_average_coverage);
        DrawPercent("Handoff-Entscheidungsgenauigkeit", validation.handoff_decision_accuracy);
        DrawValidationMessages("Fehlerdetails", validation.errors, MessageType.Error);
        DrawValidationMessages("Warnungsdetails", validation.warnings, MessageType.Warning);
        EditorGUILayout.EndVertical();
    }

    private void DrawValidationMessages(string label, string[] messages, MessageType type)
    {
        if (messages == null || messages.Length == 0)
        {
            return;
        }

        var limit = Mathf.Min(messages.Length, 5);
        for (int i = 0; i < limit; i++)
        {
            if (!string.IsNullOrWhiteSpace(messages[i]))
            {
                EditorGUILayout.HelpBox($"{label}: {messages[i]}", type);
            }
        }
        if (messages.Length > limit)
        {
            EditorGUILayout.LabelField($"... plus {messages.Length - limit} weitere", EditorStyles.wordWrappedLabel);
        }
    }

    private void DrawFunctionalMldsScenarioBox()
    {
        var scenario = draft.scenario_summary;
        if (scenario == null)
        {
            return;
        }

        EditorGUILayout.BeginVertical("box");
        EditorGUILayout.LabelField("Use Case / Szenario", EditorStyles.boldLabel);
        DrawValue("Use Case", scenario.use_case_id);
        DrawValue("Szenario", scenario.main_scenario_id);
        DrawValue("Ziel", scenario.goal);
        DrawValue("Schritte", scenario.step_count);
        DrawValue("Validation Cases", scenario.validation_case_count);
        EditorGUILayout.EndVertical();
    }

    private void DrawFunctionalMldsCapabilityBox()
    {
        var capabilities = draft.capability_summary;
        if (capabilities == null)
        {
            return;
        }

        EditorGUILayout.BeginVertical("box");
        EditorGUILayout.LabelField("Capabilities / Runtime", EditorStyles.boldLabel);
        DrawValue("Capabilities", capabilities.capability_count);
        DrawValue("Runtime Bindings", capabilities.runtime_binding_count);
        DrawValue("Runtime Actions", capabilities.runtime_action_count);
        if (capabilities.capabilities != null && capabilities.capabilities.Length > 0)
        {
            EditorGUILayout.LabelField("Auszug", EditorStyles.miniBoldLabel);
            var count = Mathf.Min(capabilities.capabilities.Length, 8);
            for (int i = 0; i < count; i++)
            {
                var item = capabilities.capabilities[i];
                if (item == null || string.IsNullOrEmpty(item.id))
                {
                    continue;
                }
                DrawValue(item.id, $"{item.runtime_binding_count} Binding(s)");
            }
            if (capabilities.capabilities.Length > count)
            {
                EditorGUILayout.LabelField($"... plus {capabilities.capabilities.Length - count} weitere", EditorStyles.wordWrappedLabel);
            }
        }
        EditorGUILayout.EndVertical();
    }

    private void DrawFunctionalMldsHandoffBox()
    {
        var handoff = draft.handoff_summary;
        if (handoff == null)
        {
            return;
        }

        EditorGUILayout.BeginVertical("box");
        EditorGUILayout.LabelField("Handoff / Spezialwissen", EditorStyles.boldLabel);
        DrawValue("Agenten", handoff.agent_count);
        DrawValue("Handoff-Paare", handoff.declared_handoff_pair_count);
        DrawPercent("Gueltige Ziele", handoff.valid_handoff_target_ratio);
        DrawPercent("Entscheidungsgenauigkeit", handoff.handoff_decision_accuracy);
        DrawValue("Self-Handoffs", handoff.self_handoff_count);
        EditorGUILayout.EndVertical();
    }

    private void DrawFunctionalMldsRoomKnowledgeBox()
    {
        var room = draft.room_knowledge_summary;
        if (room == null)
        {
            return;
        }

        EditorGUILayout.BeginVertical("box");
        EditorGUILayout.LabelField("Raumwissen / Grounding", EditorStyles.boldLabel);
        DrawValue("Raumobjekte", room.room_object_count);
        DrawValue("Semantische Zonen", room.semantic_zone_count);
        DrawValue("Knowledge-Dateien", room.knowledge_file_count);
        DrawPercent("Agent-Knowledge-Abdeckung", room.agent_to_knowledge_tag_coverage);
        DrawPercent("Objektgruppen-Grounding", room.object_group_to_agent_role_grounding);
        DrawArray("Wichtige Objektgruppen", room.important_object_groups);
        DrawArray("Zonen", room.semantic_zones);
        EditorGUILayout.EndVertical();
    }

    private static void DrawValue(string label, string value)
    {
        if (string.IsNullOrEmpty(value))
        {
            return;
        }
        EditorGUILayout.LabelField(label, value, EditorStyles.wordWrappedLabel);
    }

    private static void DrawValue(string label, int value)
    {
        if (value == 0)
        {
            return;
        }
        EditorGUILayout.LabelField(label, value.ToString(), EditorStyles.wordWrappedLabel);
    }

    private static void DrawRequiredValue(string label, string value)
    {
        EditorGUILayout.LabelField(label, string.IsNullOrEmpty(value) ? "-" : value, EditorStyles.wordWrappedLabel);
    }

    private static void DrawRequiredValue(string label, int value)
    {
        EditorGUILayout.LabelField(label, value.ToString(), EditorStyles.wordWrappedLabel);
    }

    private static void DrawPath(string label, string path)
    {
        if (string.IsNullOrEmpty(path))
        {
            return;
        }
        EditorGUILayout.LabelField(label, path, EditorStyles.wordWrappedLabel);
    }

    private static void DrawPercent(string label, float value)
    {
        if (value <= 0f)
        {
            return;
        }
        EditorGUILayout.LabelField(label, $"{value * 100f:0.0}%", EditorStyles.wordWrappedLabel);
    }

    private static void DrawArray(string label, string[] values)
    {
        if (values == null || values.Length == 0)
        {
            return;
        }
        EditorGUILayout.LabelField(label, string.Join(", ", values), EditorStyles.wordWrappedLabel);
    }

    private void DrawChat()
    {
        if (string.IsNullOrEmpty(sessionId))
        {
            return;
        }

        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Chat", EditorStyles.boldLabel);
        if (ShouldDrawFunctionalMldsDraft() && draft != null)
        {
            EditorGUILayout.HelpBox(
                "FunctionalMLDS-Chat merkt Aenderungswuensche vor. Der angezeigte Draft bleibt Preview, bis Commit/Regeneration die Aenderungen validiert.",
                draft.validation_stale ? MessageType.Warning : MessageType.Info
            );
        }

        chatScroll = EditorGUILayout.BeginScrollView(chatScroll, GUILayout.MinHeight(140), GUILayout.ExpandHeight(true));
        foreach (var line in chatLog)
        {
            EditorGUILayout.LabelField(line, EditorStyles.wordWrappedLabel);
        }
        EditorGUILayout.EndScrollView();

        EditorGUILayout.BeginHorizontal();
        chatInput = EditorGUILayout.TextField(chatInput);
        if (GUILayout.Button("Senden", GUILayout.Width(80)))
        {
            SendChat();
        }
        EditorGUILayout.EndHorizontal();
    }

    private void DrawCommitSection()
    {
        if (draft == null)
        {
            return;
        }

        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Projekt erstellen", EditorStyles.boldLabel);
        projectDisplayName = EditorGUILayout.TextField("Name", projectDisplayName);
        projectId = EditorGUILayout.TextField("Projekt-ID (optional)", projectId);
        var wordWrapStyle = new GUIStyle(EditorStyles.textArea) { wordWrap = true };
        EditorGUILayout.LabelField("Beschreibung");
        projectDescription = EditorGUILayout.TextArea(projectDescription, wordWrapStyle, GUILayout.MinHeight(60));
        if (ShouldDrawFunctionalMldsDraft() && draft.validation_stale)
        {
            EditorGUILayout.HelpBox(
                "Dieser FunctionalMLDS-Draft enthaelt vorgemerkte Chat-Aenderungen und ist nicht final validiert. Abschliessen darf erst eine vollstaendige Regeneration und erneute Validierung ausloesen.",
                MessageType.Warning
            );
        }

        if (placementDirty)
        {
            EditorGUILayout.HelpBox(
                "Die Platzierung wurde lokal geaendert. Vor dem Abschliessen bitte 'Platzierung uebernehmen' oder 'Aenderungen verwerfen' waehlen.",
                MessageType.Warning
            );
        }

        using (new EditorGUI.DisabledScope(placementDirty || isApplyingPlacement || isCommitting))
        {
            if (GUILayout.Button("Abschließen", GUILayout.Height(28)))
            {
                CommitProject();
            }
        }

        DrawFunctionalMldsCommitEvidence();
    }

    private void DrawFunctionalMldsCommitEvidence()
    {
        if (!ShouldDrawFunctionalMldsCommitEvidence() || lastCommitResponse == null)
        {
            return;
        }

        EditorGUILayout.Space();
        EditorGUILayout.LabelField("FunctionalMLDS-Commit-Evidenz", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        DrawRequiredValue("Projekt-ID", string.IsNullOrEmpty(committedProjectId) ? "-" : committedProjectId);

        if (!HasFunctionalMldsCommitData(lastCommitResponse))
        {
            EditorGUILayout.HelpBox(
                "Fuer diesen Commit liegen noch keine FunctionalMLDS-Evidenzdaten in der Backend-Antwort vor.",
                MessageType.Warning
            );
            EditorGUILayout.EndVertical();
            return;
        }

        DrawRequiredValue("Commit-Status", lastCommitResponse.status);
        DrawPath("FunctionalMLDS", lastCommitResponse.functionalmlds_path);
        DrawPath("Trace Map", lastCommitResponse.trace_map_path);

        var summary = lastCommitResponse.functionalmlds_summary;
        if (summary != null)
        {
            EditorGUILayout.LabelField("Metamodell", EditorStyles.miniBoldLabel);
            DrawValue("Case", summary.case_id);
            DrawValue("Schema", summary.schema);
            DrawValue("Metamodell-Version", summary.metamodel_version);
            DrawValue("Use Case", summary.use_case_id);
            DrawValue("Szenario", summary.main_scenario_id);
            DrawValue("Agenten", summary.agent_count);
            DrawValue("Capabilities", summary.capability_count);
            DrawValue("Runtime Bindings", summary.runtime_binding_count);
            DrawValue("Validation Cases", summary.validation_case_count);
        }

        var validation = lastCommitResponse.validation_summary;
        if (validation != null)
        {
            EditorGUILayout.LabelField("Validierung", EditorStyles.miniBoldLabel);
            DrawRequiredValue("Gesamtstatus", validation.status);
            DrawRequiredValue("Schema", validation.schema_status);
            DrawRequiredValue("Invarianten", validation.invariant_status);
            DrawRequiredValue("Materialisierung", validation.materialization_status);
            DrawRequiredValue("Traceability", validation.traceability_status);
            DrawRequiredValue("Handoff", validation.handoff_status);
            DrawRequiredValue("Fehler", validation.error_count);
            DrawRequiredValue("Warnungen", validation.warning_count);
            DrawPercent("Traceability-Abdeckung", validation.traceability_average_coverage);
            DrawPercent("Handoff-Entscheidungsgenauigkeit", validation.handoff_decision_accuracy);
            DrawValidationMessages("Fehlerdetails", validation.errors, MessageType.Error);
            DrawValidationMessages("Warnungsdetails", validation.warnings, MessageType.Warning);
        }

        EditorGUILayout.EndVertical();
    }

    private bool ShouldDrawFunctionalMldsCommitEvidence()
    {
        return generationMode == GenerationMode.FunctionalMLDS
            || string.Equals(lastCommitResponse?.generation_mode, "functionalmlds", StringComparison.OrdinalIgnoreCase)
            || HasFunctionalMldsCommitData(lastCommitResponse);
    }

    private static bool HasFunctionalMldsCommitData(CommitResponse response)
    {
        return response != null
            && (
                response.functionalmlds_summary != null
                || response.validation_summary != null
                || !string.IsNullOrEmpty(response.functionalmlds_path)
                || !string.IsNullOrEmpty(response.trace_map_path)
            );
    }

    private void ResetState()
    {
        arrowFilePath = "";
        arrowJson = "";
        ClearDraftState("");
    }

    private void ClearDraftState(string message)
    {
        sessionId = "";
        draft = null;
        chatLog.Clear();
        chatInput = "";
        projectDisplayName = "";
        projectId = "";
        projectDescription = "";
        statusMessage = "";
        isAnalyzing = false;
        isChatting = false;
        isCommitting = false;
        isApplyingPlacement = false;
        committedProjectId = "";
        lastCommitResponse = null;
        canonicalPlacementPreview = null;
        placementDirty = false;
        placementStatus = "";
        selectedPlacementId = "";
        draggingPlacementId = "";
        placementDragMode = PlacementDragMode.None;
        statusMessage = message ?? "";
    }

    private void LoadArrowFile(string assetPath)
    {
        var fullPath = Path.GetFullPath(assetPath);
        arrowFilePath = fullPath;
        arrowJson = File.ReadAllText(fullPath, Encoding.UTF8);
        statusMessage = "MLDSI geladen.";
    }

    private void RefreshBackendHealth()
    {
        if (isCheckingHealth || string.IsNullOrWhiteSpace(backendBaseUrl))
        {
            return;
        }

        isCheckingHealth = true;
        backendHealthStatus = "Wird geprueft...";
        backendVersion = "-";
        backendApiVersion = "-";
        var url = backendBaseUrl.TrimEnd('/') + "/health";
        ActiveCoroutines.Add(new EditorCoroutine(SendHealthRequest(url)));
    }

    private IEnumerator SendHealthRequest(string url)
    {
        using (var request = UnityWebRequest.Get(url))
        {
            request.downloadHandler = new DownloadHandlerBuffer();
            yield return request.SendWebRequest();

            isCheckingHealth = false;
            if (request.result != UnityWebRequest.Result.Success)
            {
                backendHealthStatus = "Nicht erreichbar: " + request.error;
                Repaint();
                yield break;
            }

            var response = JsonUtility.FromJson<HealthResponse>(request.downloadHandler.text);
            if (response == null)
            {
                backendHealthStatus = "Antwort konnte nicht gelesen werden.";
                Repaint();
                yield break;
            }

            backendHealthStatus = string.Equals(response.status, "ok", StringComparison.OrdinalIgnoreCase)
                ? "Online"
                : string.IsNullOrWhiteSpace(response.status) ? "Antwort ohne Status" : response.status;
            backendVersion = FirstNonEmpty(
                response.backend_version,
                response.version,
                response.application_version,
                "-"
            );
            backendApiVersion = string.IsNullOrWhiteSpace(response.api_version) ? "-" : response.api_version;
            Repaint();
        }
    }

    private static string FirstNonEmpty(params string[] values)
    {
        if (values != null)
        {
            foreach (var value in values)
            {
                if (!string.IsNullOrWhiteSpace(value))
                {
                    return value;
                }
            }
        }
        return "-";
    }

    private void StartAnalyze()
    {
        if (string.IsNullOrEmpty(arrowJson))
        {
            statusMessage = "Bitte zuerst eine MLDSI-JSON laden.";
            return;
        }

        statusMessage = "Analyse läuft...";
        isAnalyzing = true;
        var payload = new AnalyzeRequest
        {
            arrow_json = arrowJson,
            generation_mode = GenerationModeRequestValue(generationMode),
            project_id_hint = projectId,
            run_validation = generationMode == GenerationMode.FunctionalMLDS,
            max_repair_attempts = generationMode == GenerationMode.FunctionalMLDS ? 3 : 0,
        };
        var body = JsonUtility.ToJson(payload);
        var url = backendBaseUrl.TrimEnd('/') + "/projects/arrow/analyze";
        ActiveCoroutines.Add(new EditorCoroutine(SendRequest(url, body, OnAnalyzeResponse, () => isAnalyzing = false)));
    }

    private void SendChat()
    {
        if (string.IsNullOrEmpty(chatInput))
        {
            return;
        }

        var message = chatInput;
        chatInput = "";
        chatLog.Add("Du: " + message);
        statusMessage = "Chat läuft...";
        isChatting = true;
        var payload = new ChatRequest
        {
            session_id = sessionId,
            user_text = message,
            generation_mode = GenerationModeRequestValue(generationMode),
        };
        var body = JsonUtility.ToJson(payload);
        var url = backendBaseUrl.TrimEnd('/') + "/projects/arrow/chat";
        ActiveCoroutines.Add(new EditorCoroutine(SendRequest(url, body, OnChatResponse, () => isChatting = false)));
    }

    private void CommitProject()
    {
        if (string.IsNullOrEmpty(sessionId))
        {
            statusMessage = "Keine aktive Session.";
            return;
        }
        if (placementDirty || isApplyingPlacement)
        {
            statusMessage = "Commit blockiert: Platzierung zuerst uebernehmen oder zuruecksetzen.";
            return;
        }

        statusMessage = "Projekt wird erstellt...";
        isCommitting = true;
        committedProjectId = "";
        lastCommitResponse = null;
        var payload = new CommitRequest
        {
            session_id = sessionId,
            generation_mode = GenerationModeRequestValue(generationMode),
            display_name = projectDisplayName,
            project_id = projectId,
            description = projectDescription,
        };
        var body = JsonUtility.ToJson(payload);
        var url = backendBaseUrl.TrimEnd('/') + "/projects/arrow/commit";
        ActiveCoroutines.Add(new EditorCoroutine(SendRequest(url, body, OnCommitResponse, () => isCommitting = false)));
    }

    private IEnumerator SendRequest(string url, string jsonBody, Action<string> onSuccess, Action onComplete)
    {
        using (var request = new UnityWebRequest(url, "POST"))
        {
            var bodyRaw = Encoding.UTF8.GetBytes(jsonBody);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result != UnityWebRequest.Result.Success)
            {
                statusMessage = "Fehler: " + request.error;
                onComplete?.Invoke();
                yield break;
            }

            onSuccess?.Invoke(request.downloadHandler.text);
            onComplete?.Invoke();
        }
    }

    private void ApplyPlacementChanges()
    {
        var placements = draft?.placement_preview?.agent_placements;
        if (!placementDirty || placements == null || placements.Length == 0)
        {
            return;
        }
        if (string.IsNullOrWhiteSpace(sessionId))
        {
            placementStatus = "Keine aktive Analyse-Session.";
            placementStatusType = MessageType.Error;
            return;
        }

        var requestPlacements = new PlacementUpdateItem[placements.Length];
        for (int i = 0; i < placements.Length; i++)
        {
            var placement = placements[i];
            requestPlacements[i] = new PlacementUpdateItem
            {
                id = placement?.id,
                position = CloneVector(placement?.position),
                forward = NormalizeForward(CloneVector(placement?.forward)),
            };
        }

        var payload = new PlacementUpdateRequest
        {
            session_id = sessionId,
            generation_mode = GenerationModeRequestValue(generationMode),
            agent_placements = requestPlacements,
        };
        isApplyingPlacement = true;
        placementStatus = "Platzierung wird vom Backend validiert...";
        placementStatusType = MessageType.Info;
        var url = backendBaseUrl.TrimEnd('/') + "/projects/arrow/placement";
        ActiveCoroutines.Add(new EditorCoroutine(SendPlacementUpdateRequest(url, JsonUtility.ToJson(payload))));
    }

    private IEnumerator SendPlacementUpdateRequest(string url, string jsonBody)
    {
        using (var request = new UnityWebRequest(url, "POST"))
        {
            request.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(jsonBody));
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            yield return request.SendWebRequest();

            isApplyingPlacement = false;
            if (request.result != UnityWebRequest.Result.Success)
            {
                var responseBody = request.downloadHandler != null ? request.downloadHandler.text : "";
                if (request.responseCode >= 400)
                {
                    RejectPlacementChanges(FirstNonEmpty(responseBody, request.error, "Backend hat die Platzierung abgelehnt."));
                }
                else
                {
                    placementStatus = "Backend nicht erreichbar; lokale Aenderungen bleiben erhalten: " + request.error;
                    placementStatusType = MessageType.Error;
                }
                Repaint();
                yield break;
            }

            OnPlacementUpdateResponse(request.downloadHandler.text);
            Repaint();
        }
    }

    private void OnPlacementUpdateResponse(string json)
    {
        var response = JsonUtility.FromJson<PlacementUpdateResponse>(json);
        if (response == null)
        {
            placementStatus = "Placement-Antwort konnte nicht gelesen werden; lokale Aenderungen bleiben erhalten.";
            placementStatusType = MessageType.Error;
            return;
        }

        var responseOk = IsSuccessStatus(response.status);
        var validationOk = response.validation == null || IsSuccessStatus(response.validation.status);
        if (!responseOk || !validationOk || response.placement_preview == null)
        {
            var validationMessage = response.validation?.errors != null
                ? string.Join(" | ", response.validation.errors)
                : "";
            RejectPlacementChanges(FirstNonEmpty(validationMessage, response.status, "Platzierung ist ungueltig."));
            return;
        }

        InitializePlacementEditing(response.placement_preview);
        placementStatus = "Platzierung validiert und uebernommen.";
        placementStatusType = MessageType.Info;
        statusMessage = "Platzierung gespeichert.";
    }

    private static bool IsSuccessStatus(string value)
    {
        return string.Equals(value, "ok", StringComparison.OrdinalIgnoreCase)
            || string.Equals(value, "valid", StringComparison.OrdinalIgnoreCase)
            || string.Equals(value, "success", StringComparison.OrdinalIgnoreCase);
    }

    private void RejectPlacementChanges(string reason)
    {
        ResetPlacementChanges(false);
        placementStatus = "Platzierung abgelehnt; lokale Aenderungen wurden verworfen. " + reason;
        placementStatusType = MessageType.Error;
        statusMessage = "Platzierung wurde nicht uebernommen.";
    }

    private void OnAnalyzeResponse(string json)
    {
        var response = JsonUtility.FromJson<AnalyzeResponse>(json);
        if (response == null)
        {
            statusMessage = "Antwort konnte nicht gelesen werden.";
            return;
        }

        sessionId = response.session_id;
        draft = response.draft;
        committedProjectId = "";
        lastCommitResponse = null;
        SyncDraftFields();
        InitializePlacementEditing(draft?.placement_preview);
        if (generationMode == GenerationMode.FunctionalMLDS && !HasFunctionalMldsData(draft))
        {
            statusMessage = "Analyse abgeschlossen, aber Backend lieferte keine FunctionalMLDS-Artefakte. Backend bitte neu starten/pruefen.";
            chatLog.Add("Warnung: FunctionalMLDS-Modus aktiv, aber die Backend-Antwort enthaelt keine FunctionalMLDS-Summaries, Pfade oder Validierungsdaten.");
        }
        else
        {
            statusMessage = "Analyse abgeschlossen.";
        }
        if (!string.IsNullOrEmpty(draft?.assistant_message))
        {
            chatLog.Add("Assistent: " + draft.assistant_message);
        }
    }

    private void OnChatResponse(string json)
    {
        var response = JsonUtility.FromJson<ChatResponse>(json);
        if (response == null)
        {
            statusMessage = "Antwort konnte nicht gelesen werden.";
            return;
        }

        draft = response.draft;
        committedProjectId = "";
        lastCommitResponse = null;
        SyncDraftFields();
        InitializePlacementEditing(draft?.placement_preview);
        statusMessage = draft != null && draft.validation_stale
            ? "Chat-Aenderung vorgemerkt; FunctionalMLDS-Draft ist nicht final validiert."
            : "Chat aktualisiert.";
        if (!string.IsNullOrEmpty(draft?.assistant_message))
        {
            chatLog.Add("Assistent: " + draft.assistant_message);
        }
    }

    private void OnCommitResponse(string json)
    {
        var response = JsonUtility.FromJson<CommitResponse>(json);
        if (response == null)
        {
            statusMessage = "Antwort konnte nicht gelesen werden.";
            return;
        }

        lastCommitResponse = response;
        var commitOk = string.Equals(response.status, "ok", StringComparison.OrdinalIgnoreCase);
        statusMessage = commitOk && response.project != null
            ? $"Projekt erstellt: {response.project.display_name} ({response.project.id})"
            : $"Commit nicht final: {response.status}";
        committedProjectId = commitOk && response.project != null ? response.project.id : "";
        if (draft != null && response.placements != null && response.room_objects != null)
        {
            InitializePlacementEditing(new PlacementPreview
            {
                room_objects = response.room_objects,
                agent_placements = response.placements,
                room_bounds = response.room_bounds,
            });
        }
        if (commitOk)
        {
            EditorUtility.DisplayDialog("Projekt gespeichert", "Alles wurde gespeichert.", "OK");
        }
    }

    private void SyncDraftFields()
    {
        NormalizeKnowledgeTags();
        if (draft?.project == null)
        {
            return;
        }

        if (string.IsNullOrEmpty(projectDisplayName))
        {
            projectDisplayName = draft.project.display_name;
        }
        if (string.IsNullOrEmpty(projectDescription))
        {
            projectDescription = draft.project.description;
        }
    }

    private void NormalizeKnowledgeTags()
    {
        if (draft?.agents == null)
        {
            return;
        }

        var knowledgeEntries = new List<KnowledgeEntry>();
        if (draft.knowledge != null)
        {
            knowledgeEntries.AddRange(draft.knowledge);
        }

        var tagLookup = new Dictionary<string, KnowledgeEntry>(StringComparer.OrdinalIgnoreCase);
        foreach (var entry in knowledgeEntries)
        {
            if (!string.IsNullOrEmpty(entry.tag) && !tagLookup.ContainsKey(entry.tag))
            {
                tagLookup.Add(entry.tag, entry);
            }
        }

        foreach (var agent in draft.agents)
        {
            if (!string.IsNullOrEmpty(agent.tts_model)
                && string.Equals(agent.tts_model.Trim(), "standard", StringComparison.OrdinalIgnoreCase))
            {
                agent.tts_model = "";
            }
            if (string.IsNullOrEmpty(agent.tts_model))
            {
                agent.tts_model = "gpt-4o-mini-tts";
            }
            if (agent.knowledge_tags == null)
            {
                continue;
            }

            for (int i = 0; i < agent.knowledge_tags.Length; i++)
            {
                var tag = agent.knowledge_tags[i];
                if (string.IsNullOrEmpty(tag))
                {
                    continue;
                }

                if (tagLookup.TryGetValue(tag, out var existingEntry))
                {
                    agent.knowledge_tags[i] = existingEntry.tag;
                    continue;
                }

                var newEntry = new KnowledgeEntry
                {
                    tag = tag,
                    name = tag,
                    text = ""
                };
                knowledgeEntries.Add(newEntry);
                tagLookup.Add(tag, newEntry);
                agent.knowledge_tags[i] = tag;
            }
        }

        draft.knowledge = knowledgeEntries.ToArray();
    }

    private void DrawLoadingIndicator()
    {
        if (!isAnalyzing && !isChatting && !isCommitting && !isApplyingPlacement && !isCheckingHealth)
        {
            return;
        }

        var spinnerIndex = Mathf.FloorToInt((float)(EditorApplication.timeSinceStartup * 10f) % 12f);
        var spinner = EditorGUIUtility.IconContent($"WaitSpin{spinnerIndex:00}");
        if (spinner != null && spinner.image != null)
        {
            GUILayout.Label(spinner, GUILayout.Width(20), GUILayout.Height(20));
        }

        var loadingMessage = isApplyingPlacement
            ? "Platzierung wird validiert..."
            : isCheckingHealth
                ? "Backend wird geprueft..."
                : isCommitting
                    ? "Speichert..."
                    : "Warte auf Antwort...";
        EditorGUILayout.LabelField(loadingMessage, EditorStyles.wordWrappedLabel);
        Repaint();
    }

    // ── Texture-based floor plan preview ────────────────────────────────────

    private struct WorldMapBounds
    {
        public float minX;
        public float maxX;
        public float minZ;
        public float maxZ;

        public float SpanX => Mathf.Max(0.1f, maxX - minX);
        public float SpanZ => Mathf.Max(0.1f, maxZ - minZ);
    }

    private struct PlacementMapTransform
    {
        public Rect contentRect;
        public float minX;
        public float minZ;
        public float scale;
        public bool valid;

        public Vector2 WorldToGui(float worldX, float worldZ)
        {
            return new Vector2(
                contentRect.x + (worldX - minX) * scale,
                contentRect.yMax - (worldZ - minZ) * scale
            );
        }

        public Vector3Data GuiToWorld(Vector2 guiPosition, float worldY)
        {
            return new Vector3Data
            {
                x = (guiPosition.x - contentRect.x) / scale + minX,
                y = worldY,
                z = (contentRect.yMax - guiPosition.y) / scale + minZ,
            };
        }
    }

    private void InitializePlacementEditing(PlacementPreview preview)
    {
        if (preview == null)
        {
            canonicalPlacementPreview = null;
            placementDirty = false;
            placementStatus = "";
            selectedPlacementId = "";
            if (draft != null)
            {
                draft.placement_preview = null;
            }
            RebuildPreviewTexture(null);
            return;
        }

        canonicalPlacementPreview = ClonePlacementPreview(preview);
        if (draft != null)
        {
            draft.placement_preview = ClonePlacementPreview(preview);
        }
        placementDirty = false;
        placementStatus = "";
        placementDragMode = PlacementDragMode.None;
        draggingPlacementId = "";

        var placements = draft?.placement_preview?.agent_placements;
        if (FindPlacementById(placements, selectedPlacementId) == null)
        {
            selectedPlacementId = placements != null && placements.Length > 0
                ? placements[0]?.id ?? ""
                : "";
        }
        RebuildPreviewTexture(draft?.placement_preview);
    }

    private void ResetPlacementChanges(bool showStatus = true)
    {
        if (draft == null || canonicalPlacementPreview == null)
        {
            return;
        }

        draft.placement_preview = ClonePlacementPreview(canonicalPlacementPreview);
        placementDirty = false;
        placementDragMode = PlacementDragMode.None;
        draggingPlacementId = "";
        if (showStatus)
        {
            placementStatus = "Lokale Platzierungsaenderungen wurden verworfen.";
            placementStatusType = MessageType.Info;
        }
        RebuildPreviewTexture(draft.placement_preview);
        Repaint();
    }

    private static PlacementPreview ClonePlacementPreview(PlacementPreview source)
    {
        if (source == null)
        {
            return null;
        }

        var roomObjects = source.room_objects == null
            ? Array.Empty<RoomObjectSummary>()
            : new RoomObjectSummary[source.room_objects.Length];
        for (int i = 0; i < roomObjects.Length; i++)
        {
            var roomObject = source.room_objects[i];
            roomObjects[i] = roomObject == null ? null : new RoomObjectSummary
            {
                id = roomObject.id,
                name = roomObject.name,
                position = CloneVector(roomObject.position),
                radius = roomObject.radius,
                width = roomObject.width,
                depth = roomObject.depth,
            };
        }

        var placements = source.agent_placements == null
            ? Array.Empty<PlacementSummary>()
            : new PlacementSummary[source.agent_placements.Length];
        for (int i = 0; i < placements.Length; i++)
        {
            var placement = source.agent_placements[i];
            placements[i] = placement == null ? null : new PlacementSummary
            {
                id = placement.id,
                display_name = placement.display_name,
                position = CloneVector(placement.position),
                forward = CloneVector(placement.forward),
                spawn_point_id = placement.spawn_point_id,
                zone_id = placement.zone_id,
                tags = placement.tags == null ? Array.Empty<string>() : (string[])placement.tags.Clone(),
            };
        }

        return new PlacementPreview
        {
            room_objects = roomObjects,
            agent_placements = placements,
            room_bounds = source.room_bounds == null ? null : new RoomBounds
            {
                min_x = source.room_bounds.min_x,
                max_x = source.room_bounds.max_x,
                min_z = source.room_bounds.min_z,
                max_z = source.room_bounds.max_z,
            },
        };
    }

    private static Vector3Data CloneVector(Vector3Data source)
    {
        return source == null ? null : new Vector3Data { x = source.x, y = source.y, z = source.z };
    }

    private static Vector3Data NormalizeForward(Vector3Data source)
    {
        if (source == null)
        {
            return new Vector3Data { x = 0f, y = 0f, z = 1f };
        }
        var length = Mathf.Sqrt(source.x * source.x + source.z * source.z);
        if (length < 0.0001f)
        {
            return new Vector3Data { x = 0f, y = 0f, z = 1f };
        }
        return new Vector3Data { x = source.x / length, y = 0f, z = source.z / length };
    }

    private static PlacementSummary FindPlacementById(PlacementSummary[] placements, string id)
    {
        if (placements == null || string.IsNullOrEmpty(id))
        {
            return null;
        }
        foreach (var placement in placements)
        {
            if (placement != null && string.Equals(placement.id, id, StringComparison.Ordinal))
            {
                return placement;
            }
        }
        return null;
    }

    private static string PlacementLabel(PlacementSummary placement)
    {
        if (placement == null)
        {
            return "-";
        }
        var id = string.IsNullOrWhiteSpace(placement.id) ? "?" : placement.id;
        var name = string.IsNullOrWhiteSpace(placement.display_name) ? id : placement.display_name;
        return $"{name} [{id}]";
    }

    private static Color DeterministicAgentColor(string id)
    {
        unchecked
        {
            uint hash = 2166136261;
            var value = id ?? "";
            for (int i = 0; i < value.Length; i++)
            {
                hash ^= value[i];
                hash *= 16777619;
            }
            var hue = (hash % 360u) / 360f;
            return Color.HSVToRGB(hue, 0.62f, 0.96f);
        }
    }

    private static Vector3Data ClampPositionToRoomBounds(Vector3Data source, RoomBounds bounds)
    {
        if (source == null)
        {
            source = new Vector3Data();
        }
        if (bounds == null)
        {
            return CloneVector(source);
        }

        var minX = bounds.min_x + PlacementWallMargin;
        var maxX = bounds.max_x - PlacementWallMargin;
        var minZ = bounds.min_z + PlacementWallMargin;
        var maxZ = bounds.max_z - PlacementWallMargin;
        if (minX > maxX)
        {
            minX = maxX = (bounds.min_x + bounds.max_x) * 0.5f;
        }
        if (minZ > maxZ)
        {
            minZ = maxZ = (bounds.min_z + bounds.max_z) * 0.5f;
        }
        return new Vector3Data
        {
            x = Mathf.Clamp(source.x, minX, maxX),
            y = source.y,
            z = Mathf.Clamp(source.z, minZ, maxZ),
        };
    }

    private static bool TryGetWorldMapBounds(
        RoomObjectSummary[] roomObjects,
        PlacementSummary[] placements,
        RoomBounds roomBounds,
        out WorldMapBounds bounds)
    {
        float minX = 0f, maxX = 0f, minZ = 0f, maxZ = 0f;
        var any = false;
        if (roomBounds != null && roomBounds.max_x > roomBounds.min_x && roomBounds.max_z > roomBounds.min_z)
        {
            minX = roomBounds.min_x;
            maxX = roomBounds.max_x;
            minZ = roomBounds.min_z;
            maxZ = roomBounds.max_z;
            any = true;
        }
        else
        {
            if (roomObjects != null)
            {
                foreach (var roomObject in roomObjects)
                {
                    if (roomObject?.position != null)
                    {
                        GrowBounds(roomObject.position.x, roomObject.position.z, ref minX, ref maxX, ref minZ, ref maxZ, ref any);
                    }
                }
            }
            if (placements != null)
            {
                foreach (var placement in placements)
                {
                    if (placement?.position != null)
                    {
                        GrowBounds(placement.position.x, placement.position.z, ref minX, ref maxX, ref minZ, ref maxZ, ref any);
                    }
                }
            }
        }

        bounds = new WorldMapBounds();
        if (!any)
        {
            return false;
        }
        bounds.minX = minX - PlacementMapPadding;
        bounds.maxX = maxX + PlacementMapPadding;
        bounds.minZ = minZ - PlacementMapPadding;
        bounds.maxZ = maxZ + PlacementMapPadding;
        return true;
    }

    private static Rect ScaleToFitRect(Rect outerRect, float textureAspect)
    {
        if (outerRect.width <= 0f || outerRect.height <= 0f || textureAspect <= 0f)
        {
            return outerRect;
        }
        var outerAspect = outerRect.width / outerRect.height;
        if (outerAspect > textureAspect)
        {
            var width = outerRect.height * textureAspect;
            return new Rect(outerRect.x + (outerRect.width - width) * 0.5f, outerRect.y, width, outerRect.height);
        }
        var height = outerRect.width / textureAspect;
        return new Rect(outerRect.x, outerRect.y + (outerRect.height - height) * 0.5f, outerRect.width, height);
    }

    private static PlacementMapTransform BuildPlacementMapTransform(Rect outerRect, float textureAspect, WorldMapBounds bounds)
    {
        var imageRect = ScaleToFitRect(outerRect, textureAspect);
        var scale = Mathf.Min(imageRect.width / bounds.SpanX, imageRect.height / bounds.SpanZ);
        var width = bounds.SpanX * scale;
        var height = bounds.SpanZ * scale;
        return new PlacementMapTransform
        {
            contentRect = new Rect(
                imageRect.x + (imageRect.width - width) * 0.5f,
                imageRect.y + (imageRect.height - height) * 0.5f,
                width,
                height
            ),
            minX = bounds.minX,
            minZ = bounds.minZ,
            scale = scale,
            valid = scale > 0.0001f,
        };
    }

    private void RebuildPreviewTexture(PlacementPreview preview)
    {
        if (preview == null)
        {
            if (_previewTex != null)
            {
                DestroyImmediate(_previewTex);
                _previewTex = null;
            }
            Repaint();
            return;
        }

        const int W = 512, H = 512;
        if (_previewTex == null || _previewTex.width != W || _previewTex.height != H)
        {
            if (_previewTex != null) DestroyImmediate(_previewTex);
            _previewTex = new Texture2D(W, H, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Bilinear,
                wrapMode   = TextureWrapMode.Clamp,
            };
        }

        var roomObjects = preview.room_objects;
        var placements  = preview.agent_placements;
        var roomBounds  = preview.room_bounds;

        // ── world bounds ──────────────────────────────────────────────────
        float minX, maxX, minZ, maxZ;
        if (roomBounds != null)
        {
            minX = roomBounds.min_x; maxX = roomBounds.max_x;
            minZ = roomBounds.min_z; maxZ = roomBounds.max_z;
        }
        else
        {
            minX = maxX = minZ = maxZ = 0f;
            bool any = false;
            if (roomObjects != null)
                foreach (var o in roomObjects)
                    if (o?.position != null) { GrowBounds(o.position.x, o.position.z, ref minX, ref maxX, ref minZ, ref maxZ, ref any); }
            if (placements != null)
                foreach (var p in placements)
                    if (p?.position != null) { GrowBounds(p.position.x, p.position.z, ref minX, ref maxX, ref minZ, ref maxZ, ref any); }
            if (!any) { TexClearAndApply(_previewTex, W, H, new Color32(30, 33, 35, 255)); return; }
        }

        const float pad = 0.8f;
        minX -= pad; maxX += pad; minZ -= pad; maxZ += pad;
        float spanX = Mathf.Max(0.1f, maxX - minX);
        float spanZ = Mathf.Max(0.1f, maxZ - minZ);

        // Keep aspect ratio: find the largest drawing area inside W×H
        float scale = Mathf.Min(W / spanX, H / spanZ);
        int dw = Mathf.RoundToInt(spanX * scale);
        int dh = Mathf.RoundToInt(spanZ * scale);
        int ox = (W - dw) / 2;   // left margin in pixels
        int oy = (H - dh) / 2;   // bottom margin in pixels (Tex y=0 is bottom)

        // world → texture pixel  (y=0 at bottom of texture = low-Z in world)
        (int tx, int ty) W2T(float wx, float wz) => (
            ox + Mathf.RoundToInt((wx - minX) * scale),
            oy + Mathf.RoundToInt((wz - minZ) * scale)
        );

        var pixels = new Color32[W * H];

        // Background
        var bg = new Color32(30, 33, 35, 255);
        for (int i = 0; i < pixels.Length; i++) pixels[i] = bg;

        // Room floor fill
        if (roomBounds != null)
        {
            var (x0, y0) = W2T(roomBounds.min_x, roomBounds.min_z);
            var (x1, y1) = W2T(roomBounds.max_x, roomBounds.max_z);
            TexFillRect(pixels, W, H, x0, y0, x1 - x0, y1 - y0, new Color32(46, 51, 56, 255));
            // Wall border (3 px)
            var wall = new Color32(165, 165, 165, 220);
            TexFillRect(pixels, W, H, x0,      y0,      x1 - x0, 3, wall); // south wall
            TexFillRect(pixels, W, H, x0,      y1 - 3,  x1 - x0, 3, wall); // north wall
            TexFillRect(pixels, W, H, x0,      y0,      3, y1 - y0, wall); // west wall
            TexFillRect(pixels, W, H, x1 - 3,  y0,      3, y1 - y0, wall); // east wall
        }

        // Furniture
        if (roomObjects != null)
        {
            var fill    = new Color32(97,  66, 40, 220);
            var outline = new Color32(148, 107, 65, 255);
            foreach (var obj in roomObjects)
            {
                if (obj?.position == null) continue;
                float fw = obj.width > 0 ? obj.width : obj.radius * 2f;
                float fd = obj.depth > 0 ? obj.depth : obj.radius * 2f;
                var (x0, y0) = W2T(obj.position.x - fw * 0.5f, obj.position.z - fd * 0.5f);
                var (x1, y1) = W2T(obj.position.x + fw * 0.5f, obj.position.z + fd * 0.5f);
                if (x1 <= x0) x1 = x0 + 1;
                if (y1 <= y0) y1 = y0 + 1;
                TexFillRect(pixels, W, H, x0, y0, x1 - x0, y1 - y0, fill);
                // 1-px outline
                TexFillRect(pixels, W, H, x0, y0,      x1 - x0, 1, outline);
                TexFillRect(pixels, W, H, x0, y1 - 1,  x1 - x0, 1, outline);
                TexFillRect(pixels, W, H, x0, y0,      1, y1 - y0, outline);
                TexFillRect(pixels, W, H, x1-1, y0,    1, y1 - y0, outline);
            }
        }

        _previewTex.SetPixels32(pixels);
        _previewTex.Apply();
        Repaint();
    }

    private void DrawPlacementPreview(
        RoomObjectSummary[] roomObjects,
        PlacementSummary[] placements,
        RoomBounds roomBounds
    )
    {
        var rect = GUILayoutUtility.GetRect(0f, 360f, GUILayout.ExpandWidth(true));

        if (_previewTex != null)
        {
            GUI.DrawTexture(rect, _previewTex, ScaleMode.ScaleToFit, false);

            var stablePlacements = canonicalPlacementPreview?.agent_placements ?? placements;
            if (TryGetWorldMapBounds(roomObjects, stablePlacements, roomBounds, out var worldBounds))
            {
                var mapTransform = BuildPlacementMapTransform(
                    rect,
                    (float)_previewTex.width / _previewTex.height,
                    worldBounds
                );
                DrawPlacementOverlay(placements, mapTransform);
                HandlePlacementMapInput(placements, roomBounds, mapTransform);
            }
        }
        else
        {
            EditorGUI.DrawRect(rect, new Color(0.12f, 0.13f, 0.14f));
            EditorGUI.LabelField(rect, "Keine Vorschau – Analyse ausführen.", EditorStyles.centeredGreyMiniLabel);
        }

        EditorGUILayout.LabelField(
            "■ Moebel (2D-Schnitt 0,5 m)   ● Agent (ziehen)   ○ Forward-Handle (ziehen)",
            EditorStyles.miniLabel
        );

        DrawSelectedPlacementDetails(placements);

        if (placementDirty)
        {
            EditorGUILayout.HelpBox(
                "Lokale Aenderungen sind noch nicht validiert. Commit bleibt bis Apply oder Reset gesperrt.",
                MessageType.Warning
            );
        }
        if (!string.IsNullOrEmpty(placementStatus))
        {
            EditorGUILayout.HelpBox(placementStatus, placementStatusType);
        }

        EditorGUILayout.BeginHorizontal();
        using (new EditorGUI.DisabledScope(!placementDirty || isApplyingPlacement || string.IsNullOrEmpty(sessionId)))
        {
            if (GUILayout.Button(isApplyingPlacement ? "Wird validiert..." : "Platzierung uebernehmen"))
            {
                ApplyPlacementChanges();
            }
        }
        using (new EditorGUI.DisabledScope(!placementDirty || isApplyingPlacement))
        {
            if (GUILayout.Button("Aenderungen verwerfen"))
            {
                ResetPlacementChanges();
            }
        }
        EditorGUILayout.EndHorizontal();

        if (_previewTex != null && GUILayout.Button("Vorschau mit Agenten-Legende als PNG speichern"))
        {
            var path = EditorUtility.SaveFilePanel("Vorschau speichern", "", "placement_preview", "png");
            if (!string.IsNullOrEmpty(path))
            {
                var exportTexture = BuildPlacementExportTexture(roomObjects, placements, roomBounds);
                if (exportTexture != null)
                {
                    System.IO.File.WriteAllBytes(path, exportTexture.EncodeToPNG());
                    DestroyImmediate(exportTexture);
                    EditorUtility.RevealInFinder(path);
                }
            }
        }
    }

    private void DrawPlacementOverlay(PlacementSummary[] placements, PlacementMapTransform mapTransform)
    {
        if (!mapTransform.valid || placements == null)
        {
            return;
        }

        var sorted = SortedPlacements(placements);
        Handles.BeginGUI();
        foreach (var placement in sorted)
        {
            var marker = mapTransform.WorldToGui(placement.position.x, placement.position.z);
            var color = DeterministicAgentColor(placement.id);
            var selected = string.Equals(placement.id, selectedPlacementId, StringComparison.Ordinal);
            var forwardHandle = ForwardHandlePosition(placement, mapTransform);

            Handles.color = new Color(color.r, color.g, color.b, 0.95f);
            Handles.DrawAAPolyLine(
                selected ? 3.5f : 2.2f,
                new Vector3(marker.x, marker.y, 0f),
                new Vector3(forwardHandle.x, forwardHandle.y, 0f)
            );
            DrawForwardArrowHead(marker, forwardHandle, color, selected ? 7f : 5f);

            if (selected)
            {
                Handles.color = Color.white;
                Handles.DrawWireDisc(new Vector3(marker.x, marker.y, 0f), Vector3.forward, PlacementMarkerRadius + 4f);
            }
            Handles.color = color;
            Handles.DrawSolidDisc(new Vector3(marker.x, marker.y, 0f), Vector3.forward, PlacementMarkerRadius);

            if (selected)
            {
                Handles.color = new Color(1f, 0.86f, 0.25f, 1f);
                Handles.DrawSolidDisc(new Vector3(forwardHandle.x, forwardHandle.y, 0f), Vector3.forward, ForwardHandleRadius);
                Handles.color = Color.white;
                Handles.DrawWireDisc(new Vector3(forwardHandle.x, forwardHandle.y, 0f), Vector3.forward, ForwardHandleRadius + 2f);
            }
        }
        Handles.EndGUI();

        var occupied = new List<Rect>();
        foreach (var placement in sorted)
        {
            var marker = mapTransform.WorldToGui(placement.position.x, placement.position.z);
            var selected = string.Equals(placement.id, selectedPlacementId, StringComparison.Ordinal);
            var style = new GUIStyle(selected ? EditorStyles.miniBoldLabel : EditorStyles.miniLabel)
            {
                alignment = TextAnchor.MiddleLeft,
                padding = new RectOffset(4, 4, 2, 2),
            };
            style.normal.textColor = Color.white;
            var label = PlacementLabel(placement);
            var labelRect = FindLabelRect(marker, label, style, mapTransform.contentRect, occupied);
            occupied.Add(labelRect);

            Handles.BeginGUI();
            Handles.color = new Color(DeterministicAgentColor(placement.id).r, DeterministicAgentColor(placement.id).g, DeterministicAgentColor(placement.id).b, 0.7f);
            Handles.DrawAAPolyLine(
                1.5f,
                new Vector3(marker.x, marker.y, 0f),
                new Vector3(labelRect.center.x, labelRect.center.y, 0f)
            );
            Handles.EndGUI();
            EditorGUI.DrawRect(labelRect, selected ? new Color(0.12f, 0.20f, 0.30f, 0.96f) : new Color(0.08f, 0.09f, 0.10f, 0.90f));
            GUI.Label(labelRect, label, style);

            EditorGUIUtility.AddCursorRect(
                new Rect(marker.x - PlacementHitRadius, marker.y - PlacementHitRadius, PlacementHitRadius * 2f, PlacementHitRadius * 2f),
                MouseCursor.MoveArrow
            );
            if (selected)
            {
                var handle = ForwardHandlePosition(placement, mapTransform);
                EditorGUIUtility.AddCursorRect(
                    new Rect(handle.x - PlacementHitRadius, handle.y - PlacementHitRadius, PlacementHitRadius * 2f, PlacementHitRadius * 2f),
                    MouseCursor.RotateArrow
                );
            }
        }
    }

    private static void DrawForwardArrowHead(Vector2 start, Vector2 end, Color color, float size)
    {
        var direction = end - start;
        if (direction.sqrMagnitude < 0.001f)
        {
            return;
        }
        direction.Normalize();
        var normal = new Vector2(-direction.y, direction.x);
        var basePoint = end - direction * size;
        Handles.color = color;
        Handles.DrawAAPolyLine(
            2f,
            new Vector3(end.x, end.y, 0f),
            new Vector3(basePoint.x + normal.x * size * 0.55f, basePoint.y + normal.y * size * 0.55f, 0f)
        );
        Handles.DrawAAPolyLine(
            2f,
            new Vector3(end.x, end.y, 0f),
            new Vector3(basePoint.x - normal.x * size * 0.55f, basePoint.y - normal.y * size * 0.55f, 0f)
        );
    }

    private static List<PlacementSummary> SortedPlacements(PlacementSummary[] placements)
    {
        var result = new List<PlacementSummary>();
        if (placements != null)
        {
            foreach (var placement in placements)
            {
                if (placement?.position != null)
                {
                    result.Add(placement);
                }
            }
        }
        result.Sort((left, right) => string.Compare(left?.id, right?.id, StringComparison.Ordinal));
        return result;
    }

    private static Vector2 ForwardHandlePosition(PlacementSummary placement, PlacementMapTransform mapTransform)
    {
        var marker = mapTransform.WorldToGui(placement.position.x, placement.position.z);
        var forward = NormalizeForward(placement.forward);
        var guiDirection = new Vector2(forward.x, -forward.z);
        if (guiDirection.sqrMagnitude < 0.001f)
        {
            guiDirection = Vector2.up;
        }
        guiDirection.Normalize();
        var distance = Mathf.Clamp(mapTransform.scale * 0.8f, 30f, 58f);
        var handle = marker + guiDirection * distance;
        handle.x = Mathf.Clamp(
            handle.x,
            mapTransform.contentRect.xMin + ForwardHandleRadius + 2f,
            mapTransform.contentRect.xMax - ForwardHandleRadius - 2f
        );
        handle.y = Mathf.Clamp(
            handle.y,
            mapTransform.contentRect.yMin + ForwardHandleRadius + 2f,
            mapTransform.contentRect.yMax - ForwardHandleRadius - 2f
        );
        return handle;
    }

    private static Rect FindLabelRect(
        Vector2 marker,
        string label,
        GUIStyle style,
        Rect contentRect,
        List<Rect> occupied)
    {
        var measured = style.CalcSize(new GUIContent(label));
        var width = Mathf.Min(Mathf.Max(60f, measured.x + 8f), Mathf.Max(60f, contentRect.width - 8f));
        var height = Mathf.Max(18f, measured.y + 4f);
        var candidates = new[]
        {
            new Vector2(12f, -height * 0.5f),
            new Vector2(-width - 12f, -height * 0.5f),
            new Vector2(-width * 0.5f, 13f),
            new Vector2(-width * 0.5f, -height - 13f),
            new Vector2(12f, 13f),
            new Vector2(-width - 12f, 13f),
            new Vector2(12f, -height - 13f),
            new Vector2(-width - 12f, -height - 13f),
        };

        Rect fallback = new Rect(marker + candidates[0], new Vector2(width, height));
        foreach (var offset in candidates)
        {
            var candidate = ClampRectToBounds(new Rect(marker + offset, new Vector2(width, height)), contentRect);
            fallback = candidate;
            var overlaps = false;
            foreach (var used in occupied)
            {
                if (candidate.Overlaps(used))
                {
                    overlaps = true;
                    break;
                }
            }
            if (!overlaps)
            {
                return candidate;
            }
        }
        return fallback;
    }

    private static Rect ClampRectToBounds(Rect value, Rect bounds)
    {
        value.x = Mathf.Clamp(value.x, bounds.xMin + 2f, Mathf.Max(bounds.xMin + 2f, bounds.xMax - value.width - 2f));
        value.y = Mathf.Clamp(value.y, bounds.yMin + 2f, Mathf.Max(bounds.yMin + 2f, bounds.yMax - value.height - 2f));
        return value;
    }

    private void HandlePlacementMapInput(
        PlacementSummary[] placements,
        RoomBounds roomBounds,
        PlacementMapTransform mapTransform)
    {
        if (!mapTransform.valid || placements == null)
        {
            return;
        }

        var evt = Event.current;
        if (evt == null)
        {
            return;
        }
        var controlId = GUIUtility.GetControlID("MLDSIPlacementMap".GetHashCode(), FocusType.Passive, mapTransform.contentRect);

        if (evt.type == EventType.MouseDown && evt.button == 0 && mapTransform.contentRect.Contains(evt.mousePosition))
        {
            var selected = FindPlacementById(placements, selectedPlacementId);
            if (selected?.position != null)
            {
                var handle = ForwardHandlePosition(selected, mapTransform);
                if (Vector2.Distance(handle, evt.mousePosition) <= PlacementHitRadius)
                {
                    BeginPlacementDrag(controlId, selected.id, PlacementDragMode.Forward);
                    evt.Use();
                    return;
                }
            }

            PlacementSummary hit = null;
            var bestDistance = float.PositiveInfinity;
            foreach (var placement in placements)
            {
                if (placement?.position == null)
                {
                    continue;
                }
                var marker = mapTransform.WorldToGui(placement.position.x, placement.position.z);
                var distance = Vector2.Distance(marker, evt.mousePosition);
                if (distance <= PlacementHitRadius && distance < bestDistance)
                {
                    hit = placement;
                    bestDistance = distance;
                }
            }
            if (hit != null)
            {
                selectedPlacementId = hit.id;
                BeginPlacementDrag(controlId, hit.id, PlacementDragMode.Position);
                evt.Use();
                Repaint();
            }
            return;
        }

        if (GUIUtility.hotControl != controlId || string.IsNullOrEmpty(draggingPlacementId))
        {
            return;
        }

        if (evt.type == EventType.MouseDrag && evt.button == 0)
        {
            var placement = FindPlacementById(placements, draggingPlacementId);
            if (placement?.position != null)
            {
                if (placementDragMode == PlacementDragMode.Position)
                {
                    var updated = mapTransform.GuiToWorld(evt.mousePosition, placement.position.y);
                    updated = ClampPositionToRoomBounds(updated, roomBounds);
                    if (Mathf.Abs(updated.x - placement.position.x) > 0.0001f
                        || Mathf.Abs(updated.z - placement.position.z) > 0.0001f)
                    {
                        placement.position.x = updated.x;
                        placement.position.z = updated.z;
                        MarkPlacementDirty();
                    }
                }
                else if (placementDragMode == PlacementDragMode.Forward)
                {
                    var target = mapTransform.GuiToWorld(evt.mousePosition, placement.position.y);
                    var dx = target.x - placement.position.x;
                    var dz = target.z - placement.position.z;
                    var length = Mathf.Sqrt(dx * dx + dz * dz);
                    if (length > 0.0001f)
                    {
                        placement.forward = new Vector3Data { x = dx / length, y = 0f, z = dz / length };
                        MarkPlacementDirty();
                    }
                }
            }
            evt.Use();
            Repaint();
        }
        else if (evt.type == EventType.MouseUp && evt.button == 0)
        {
            GUIUtility.hotControl = 0;
            placementDragMode = PlacementDragMode.None;
            draggingPlacementId = "";
            evt.Use();
            Repaint();
        }
    }

    private void BeginPlacementDrag(int controlId, string placementId, PlacementDragMode mode)
    {
        GUIUtility.hotControl = controlId;
        selectedPlacementId = placementId;
        draggingPlacementId = placementId;
        placementDragMode = mode;
    }

    private void MarkPlacementDirty()
    {
        placementDirty = true;
        placementStatus = "Lokale Platzierung geaendert; noch nicht vom Backend validiert.";
        placementStatusType = MessageType.Warning;
        committedProjectId = "";
        lastCommitResponse = null;
    }

    private void DrawSelectedPlacementDetails(PlacementSummary[] placements)
    {
        var selected = FindPlacementById(placements, selectedPlacementId);
        if (selected?.position == null)
        {
            return;
        }
        var forward = NormalizeForward(selected.forward);
        EditorGUILayout.BeginVertical("box");
        EditorGUILayout.LabelField("Ausgewaehlt", PlacementLabel(selected), EditorStyles.wordWrappedLabel);
        EditorGUILayout.LabelField("Position (X/Z)", $"{selected.position.x:0.###} / {selected.position.z:0.###}");
        EditorGUILayout.LabelField("Forward (X/Z)", $"{forward.x:0.###} / {forward.z:0.###}");
        EditorGUILayout.LabelField("Marker ziehen = Position; gelben Forward-Handle ziehen = Blickrichtung", EditorStyles.miniLabel);
        EditorGUILayout.EndVertical();
    }

    private Texture2D BuildPlacementExportTexture(
        RoomObjectSummary[] roomObjects,
        PlacementSummary[] placements,
        RoomBounds roomBounds)
    {
        if (_previewTex == null)
        {
            return null;
        }

        const int mapSize = 512;
        const int legendWidth = 460;
        const int textScale = 2;
        const int maxLegendCharacters = 34;
        var sorted = SortedPlacements(placements);
        var wrappedLabels = new List<List<string>>();
        var requiredLegendHeight = 54;
        foreach (var placement in sorted)
        {
            var lines = WrapExportText(NormalizeExportText(PlacementLabel(placement)), maxLegendCharacters);
            wrappedLabels.Add(lines);
            requiredLegendHeight += 12 + lines.Count * 18;
        }
        requiredLegendHeight += 18;

        var exportWidth = mapSize + legendWidth;
        var exportHeight = Mathf.Max(mapSize, requiredLegendHeight);
        var exportTexture = new Texture2D(exportWidth, exportHeight, TextureFormat.RGBA32, false)
        {
            filterMode = FilterMode.Point,
            wrapMode = TextureWrapMode.Clamp,
        };
        var pixels = new Color32[exportWidth * exportHeight];
        var background = new Color32(25, 28, 31, 255);
        for (int i = 0; i < pixels.Length; i++)
        {
            pixels[i] = background;
        }

        var mapPixels = _previewTex.GetPixels32();
        var mapOffsetY = exportHeight - mapSize;
        for (int y = 0; y < mapSize; y++)
        {
            Array.Copy(mapPixels, y * mapSize, pixels, (y + mapOffsetY) * exportWidth, mapSize);
        }
        TexFillRect(pixels, exportWidth, exportHeight, mapSize, 0, legendWidth, exportHeight, new Color32(39, 43, 48, 255));
        TexFillRect(pixels, exportWidth, exportHeight, mapSize, 0, 2, exportHeight, new Color32(118, 127, 138, 255));

        var stablePlacements = canonicalPlacementPreview?.agent_placements ?? placements;
        if (TryGetWorldMapBounds(roomObjects, stablePlacements, roomBounds, out var worldBounds))
        {
            var mapTransform = BuildPlacementMapTransform(new Rect(0f, 0f, mapSize, mapSize), 1f, worldBounds);
            foreach (var placement in sorted)
            {
                var marker = mapTransform.WorldToGui(placement.position.x, placement.position.z);
                var handle = ForwardHandlePosition(placement, mapTransform);
                var markerX = Mathf.RoundToInt(marker.x);
                var markerY = mapOffsetY + mapSize - 1 - Mathf.RoundToInt(marker.y);
                var handleX = Mathf.RoundToInt(handle.x);
                var handleY = mapOffsetY + mapSize - 1 - Mathf.RoundToInt(handle.y);
                var color = (Color32)DeterministicAgentColor(placement.id);
                TexDrawLine(pixels, exportWidth, exportHeight, markerX, markerY, handleX, handleY, 3, color);
                TexFillCircle(pixels, exportWidth, exportHeight, markerX, markerY, 7, color);
                TexFillCircle(pixels, exportWidth, exportHeight, handleX, handleY, 4, new Color32(255, 222, 72, 255));
            }
        }

        TexDrawBitmapTextTop(
            pixels,
            exportWidth,
            exportHeight,
            mapSize + 20,
            20,
            "PLACEMENT LEGEND",
            textScale,
            new Color32(245, 247, 250, 255)
        );
        TexDrawBitmapTextTop(
            pixels,
            exportWidth,
            exportHeight,
            mapSize + 20,
            40,
            "NAME [ID] - COLOR ON MAP",
            1,
            new Color32(184, 193, 204, 255)
        );

        var top = 66;
        for (int i = 0; i < sorted.Count; i++)
        {
            var placement = sorted[i];
            var color = (Color32)DeterministicAgentColor(placement.id);
            var markerTopY = top + 7;
            TexFillCircle(
                pixels,
                exportWidth,
                exportHeight,
                mapSize + 22,
                exportHeight - 1 - markerTopY,
                7,
                color
            );
            var lineTop = top;
            foreach (var line in wrappedLabels[i])
            {
                TexDrawBitmapTextTop(
                    pixels,
                    exportWidth,
                    exportHeight,
                    mapSize + 40,
                    lineTop,
                    line,
                    textScale,
                    new Color32(245, 247, 250, 255)
                );
                lineTop += 18;
            }
            top = lineTop + 12;
        }

        exportTexture.SetPixels32(pixels);
        exportTexture.Apply();
        return exportTexture;
    }

    private static string NormalizeExportText(string value)
    {
        return (value ?? "")
            .Replace("Ä", "AE")
            .Replace("Ö", "OE")
            .Replace("Ü", "UE")
            .Replace("ä", "AE")
            .Replace("ö", "OE")
            .Replace("ü", "UE")
            .Replace("ß", "SS")
            .ToUpperInvariant();
    }

    private static List<string> WrapExportText(string value, int maxCharacters)
    {
        var result = new List<string>();
        var remaining = (value ?? "").Trim();
        if (remaining.Length == 0)
        {
            result.Add("-");
            return result;
        }

        while (remaining.Length > maxCharacters)
        {
            var cut = remaining.LastIndexOf(' ', maxCharacters);
            if (cut < maxCharacters / 2)
            {
                cut = maxCharacters;
            }
            result.Add(remaining.Substring(0, cut).TrimEnd());
            remaining = remaining.Substring(cut).TrimStart();
        }
        if (remaining.Length > 0)
        {
            result.Add(remaining);
        }
        return result;
    }

    private static void TexDrawBitmapTextTop(
        Color32[] pixels,
        int width,
        int height,
        int left,
        int top,
        string text,
        int scale,
        Color32 color)
    {
        var cursorX = left;
        foreach (var rawCharacter in text ?? "")
        {
            var character = char.ToUpperInvariant(rawCharacter);
            if (!ExportGlyphs.TryGetValue(character, out var rows))
            {
                rows = ExportGlyphs['?'];
            }
            for (int row = 0; row < rows.Length; row++)
            {
                for (int column = 0; column < rows[row].Length; column++)
                {
                    if (rows[row][column] != '1')
                    {
                        continue;
                    }
                    var pixelX = cursorX + column * scale;
                    var pixelY = height - top - (row + 1) * scale;
                    TexFillRect(pixels, width, height, pixelX, pixelY, scale, scale, color);
                }
            }
            cursorX += 6 * scale;
        }
    }

    public static string RunEditorSmokeTest()
    {
        SmokeAssert(
            string.Equals(InteractiveAgentsVersion.WizardVersion, "1.0.0", StringComparison.Ordinal),
            "Wizard-Version ist nicht 1.0.0."
        );

        var bounds = new WorldMapBounds { minX = -5f, maxX = 5f, minZ = -4f, maxZ = 4f };
        var map = BuildPlacementMapTransform(new Rect(0f, 0f, 800f, 300f), 1f, bounds);
        SmokeAssert(map.valid, "MapTransform ist ungueltig.");
        SmokeAssert(Mathf.Abs(map.contentRect.x - 250f) < 0.01f, "ScaleToFit-Letterboxing ist falsch.");
        SmokeAssert(Mathf.Abs(map.contentRect.y - 30f) < 0.01f, "World-Aspect-Letterboxing ist falsch.");

        var centerGui = map.WorldToGui(0f, 0f);
        var centerWorld = map.GuiToWorld(centerGui, 0f);
        SmokeAssert(Mathf.Abs(centerWorld.x) < 0.0001f && Mathf.Abs(centerWorld.z) < 0.0001f, "World/GUI-Roundtrip ist falsch.");
        SmokeAssert(map.WorldToGui(0f, 3f).y < map.WorldToGui(0f, -3f).y, "Z-Achse wird in GUI nicht invertiert.");

        var roomBounds = new RoomBounds { min_x = -5f, max_x = 5f, min_z = -4f, max_z = 4f };
        var clamped = ClampPositionToRoomBounds(new Vector3Data { x = 100f, y = 1.25f, z = -100f }, roomBounds);
        SmokeAssert(Mathf.Abs(clamped.x - 4.55f) < 0.001f, "X-Wall-Margin ist falsch.");
        SmokeAssert(Mathf.Abs(clamped.z + 3.55f) < 0.001f, "Z-Wall-Margin ist falsch.");
        SmokeAssert(Mathf.Abs(clamped.y - 1.25f) < 0.001f, "Y darf beim X/Z-Drag nicht geaendert werden.");

        var normalized = NormalizeForward(new Vector3Data { x = 3f, y = 8f, z = 4f });
        SmokeAssert(Mathf.Abs(Mathf.Sqrt(normalized.x * normalized.x + normalized.z * normalized.z) - 1f) < 0.0001f, "Forward ist nicht normalisiert.");
        SmokeAssert(Mathf.Abs(normalized.y) < 0.0001f, "Forward-Y muss 0 sein.");

        var colorA = DeterministicAgentColor("agent-a");
        var colorAAgain = DeterministicAgentColor("agent-a");
        var colorB = DeterministicAgentColor("agent-b");
        SmokeAssert(colorA == colorAAgain, "Agentenfarbe ist nicht deterministisch.");
        SmokeAssert(colorA != colorB, "Unterschiedliche Test-IDs erhalten dieselbe Farbe.");

        var request = new PlacementUpdateRequest
        {
            session_id = "session-smoke",
            generation_mode = "functionalmlds",
            agent_placements = new[]
            {
                new PlacementUpdateItem
                {
                    id = "agent-a",
                    position = new Vector3Data { x = 1f, y = 0f, z = 2f },
                    forward = new Vector3Data { x = 0f, y = 0f, z = 1f },
                },
            },
        };
        var json = JsonUtility.ToJson(request);
        SmokeAssert(json.Contains("\"agent_placements\""), "Placement-Vertragsfeld agent_placements fehlt.");
        SmokeAssert(json.Contains("\"position\"") && json.Contains("\"forward\""), "Position/Forward fehlen im Placement-Vertrag.");
        SmokeAssert(!json.Contains("display_name") && !json.Contains("spawn_point_id") && !json.Contains("zone_id"), "Placement-Patch enthaelt verbotene Semantikfelder.");
        SmokeAssert(
            string.Equals(
                PlacementLabel(new PlacementSummary { id = "agent-a", display_name = "Name" }),
                "Name [agent-a]",
                StringComparison.Ordinal
            ),
            "Sichtbares Label folgt nicht exakt Name [id]."
        );
        SmokeAssert(NormalizeExportText("Name [agent-a]").Contains("[AGENT-A]"), "PNG-Legendentext ist nicht eindeutig.");
        var legendPixels = new Color32[160 * 24];
        TexDrawBitmapTextTop(legendPixels, 160, 24, 0, 0, "NAME [ID]", 2, new Color32(255, 255, 255, 255));
        var legendHasText = false;
        foreach (var pixel in legendPixels)
        {
            if (pixel.a > 0)
            {
                legendHasText = true;
                break;
            }
        }
        SmokeAssert(legendHasText, "PNG-Bitmaplegende rendert keinen Text.");

        return "MLDSI Wizard v1.0.0 smoke test: OK (version, contract, ScaleToFit, X/Z roundtrip, Z inversion, wall margin, forward, labels/colors, PNG legend).";
    }

    private static void SmokeAssert(bool condition, string message)
    {
        if (!condition)
        {
            throw new InvalidOperationException("MLDSI Wizard smoke test failed: " + message);
        }
    }

    // ── Texture pixel helpers ────────────────────────────────────────────

    private static void GrowBounds(float x, float z,
        ref float minX, ref float maxX, ref float minZ, ref float maxZ, ref bool any)
    {
        if (!any) { minX = maxX = x; minZ = maxZ = z; any = true; return; }
        if (x < minX) minX = x; if (x > maxX) maxX = x;
        if (z < minZ) minZ = z; if (z > maxZ) maxZ = z;
    }

    private static void TexClearAndApply(Texture2D tex, int w, int h, Color32 color)
    {
        var pixels = new Color32[w * h];
        for (int i = 0; i < pixels.Length; i++) pixels[i] = color;
        tex.SetPixels32(pixels);
        tex.Apply();
    }

    private static void TexFillRect(Color32[] pixels, int w, int h, int x, int y, int rw, int rh, Color32 color)
    {
        int x1 = Mathf.Clamp(x + rw, 0, w);
        int y1 = Mathf.Clamp(y + rh, 0, h);
        int x0 = Mathf.Clamp(x, 0, w);
        int y0 = Mathf.Clamp(y, 0, h);
        for (int py = y0; py < y1; py++)
            for (int px = x0; px < x1; px++)
                pixels[py * w + px] = color;
    }

    private static void TexFillCircle(Color32[] pixels, int w, int h, int cx, int cy, int r, Color32 color)
    {
        int r2 = r * r;
        for (int dy = -r; dy <= r; dy++)
        for (int dx = -r; dx <= r; dx++)
        {
            if (dx * dx + dy * dy > r2) continue;
            int px = cx + dx, py = cy + dy;
            if (px >= 0 && px < w && py >= 0 && py < h)
                pixels[py * w + px] = color;
        }
    }

    private static void TexDrawLine(Color32[] pixels, int w, int h, int x0, int y0, int x1, int y1, int thick, Color32 color)
    {
        int dx = Mathf.Abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
        int dy = -Mathf.Abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
        int err = dx + dy, half = thick / 2;
        for (;;)
        {
            TexFillRect(pixels, w, h, x0 - half, y0 - half, thick, thick, color);
            if (x0 == x1 && y0 == y1) break;
            int e2 = 2 * err;
            if (e2 >= dy) { if (x0 == x1) break; err += dy; x0 += sx; }
            if (e2 <= dx) { if (y0 == y1) break; err += dx; y0 += sy; }
        }
    }
}
#endif
