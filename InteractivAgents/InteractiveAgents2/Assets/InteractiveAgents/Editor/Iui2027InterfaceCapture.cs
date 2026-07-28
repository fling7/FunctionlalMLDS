using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>
/// Deterministic, review-anonymous capture of the implemented visitor surface.
/// The command opens the real Steinpilz scene, selects its frozen backend
/// project, waits for the V2 bindings, enters one resolved selection through
/// the same state transition used by ray selection, and captures the Game view.
/// </summary>
public static class Iui2027InterfaceCapture
{
    private const string ScenePath = "Assets/Scenes/MolkereiChampignion.unity";
    private const string ProjectId = "steinpilz_brand_room";
    private const string SuccessMarker = "[Iui2027InterfaceCapture] OK";
    private const double CaptureDelaySeconds = 8.0;
    private const double TimeoutSeconds = 240.0;
    private const double ProgressIntervalSeconds = 15.0;
    private const string RunningSessionKey = "Iui2027InterfaceCapture.Running";
    private const string OutputSessionKey = "Iui2027InterfaceCapture.Output";

    private static string outputPath;
    private static bool setupStarted;
    private static bool captureRequested;
    private static bool screenshotIssued;
    private static bool finishing;
    private static double startedAt;
    private static double selectionAt;
    private static double nextProgressAt;

    [InitializeOnLoadMethod]
    private static void ResumeAfterDomainReload()
    {
        if (!SessionState.GetBool(RunningSessionKey, false))
        {
            return;
        }

        outputPath = SessionState.GetString(OutputSessionKey, string.Empty);
        ResetRuntimeState();
        AttachCallbacks();
        EditorApplication.delayCall += AttachUpdateIfAlreadyPlaying;
    }

    public static void RunFromCommandLine()
    {
        outputPath = Environment.GetEnvironmentVariable(
            "IUI2027_INTERFACE_CAPTURE_OUTPUT");
        if (string.IsNullOrWhiteSpace(outputPath))
        {
            throw new InvalidOperationException(
                "IUI2027_INTERFACE_CAPTURE_OUTPUT must name the PNG output.");
        }

        outputPath = Path.GetFullPath(outputPath);
        var directory = Path.GetDirectoryName(outputPath);
        if (string.IsNullOrWhiteSpace(directory))
        {
            throw new InvalidOperationException("Capture output has no parent directory.");
        }
        Directory.CreateDirectory(directory);
        if (File.Exists(outputPath))
        {
            File.Delete(outputPath);
        }

        SessionState.SetString(OutputSessionKey, outputPath);
        SessionState.SetBool(RunningSessionKey, true);
        EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
        Screen.SetResolution(1440, 900, false);
        ResetRuntimeState();
        AttachCallbacks();
        EditorApplication.isPlaying = true;
    }

    private static void ResetRuntimeState()
    {
        setupStarted = false;
        captureRequested = false;
        screenshotIssued = false;
        finishing = false;
        startedAt = EditorApplication.timeSinceStartup;
        selectionAt = 0.0;
        nextProgressAt = startedAt + ProgressIntervalSeconds;
    }

    private static void AttachCallbacks()
    {
        EditorApplication.playModeStateChanged -= OnPlayModeStateChanged;
        EditorApplication.playModeStateChanged += OnPlayModeStateChanged;
    }

    private static void AttachUpdateIfAlreadyPlaying()
    {
        if (!SessionState.GetBool(RunningSessionKey, false)
            || !EditorApplication.isPlaying)
        {
            return;
        }

        EditorApplication.update -= Tick;
        EditorApplication.update += Tick;
    }

    private static void OnPlayModeStateChanged(PlayModeStateChange state)
    {
        if (state != PlayModeStateChange.EnteredPlayMode)
        {
            return;
        }

        ResetRuntimeState();
        EditorApplication.update -= Tick;
        EditorApplication.update += Tick;
    }

    private static void Tick()
    {
        try
        {
            TickCore();
        }
        catch (Exception exception)
        {
            var cause = exception is TargetInvocationException invocation
                && invocation.InnerException != null
                ? invocation.InnerException
                : exception;
            Fail(cause.GetType().Name + ": " + cause.Message);
        }
    }

    private static void TickCore()
    {
        var now = EditorApplication.timeSinceStartup;
        var manager = UnityEngine.Object.FindAnyObjectByType<QuickAgentManager>();
        if (manager == null)
        {
            if (now - startedAt > TimeoutSeconds)
            {
                Fail("QuickAgentManager was not found.");
            }
            return;
        }

        if (!setupStarted)
        {
            SetPrivateField(manager, "selectedProjectId", ProjectId);
            var setup = InvokePrivate(manager, "SetupFromServer") as IEnumerator;
            if (setup == null)
            {
                Fail("SetupFromServer did not return a coroutine.");
                return;
            }
            manager.StartCoroutine(setup);
            setupStarted = true;
            return;
        }

        var registry = manager.SpatialBindingRegistry;
        if (now >= nextProgressAt)
        {
            var managerStatus = GetPrivateField(manager, "statusMessage") as string;
            Debug.Log(
                "[Iui2027InterfaceCapture] waiting; model_hash="
                + (!string.IsNullOrWhiteSpace(manager.CurrentModelSha256))
                + "; registry="
                + (registry == null ? "missing" : registry.ValidationSummary())
                + "; manager_status="
                + (string.IsNullOrWhiteSpace(managerStatus)
                    ? "empty"
                    : managerStatus));
            nextProgressAt = now + ProgressIntervalSeconds;
        }
        if (!captureRequested
            && !string.IsNullOrWhiteSpace(manager.CurrentModelSha256)
            && registry != null
            && registry.IsValid
            && registry.Count > 0)
        {
            var binding = SelectVisibleBinding(registry);
            var collider = binding.SelectionCollider;
            if (collider == null)
            {
                Fail("No stable scene binding has a selection collider.");
                return;
            }

            InvokePrivate(
                manager,
                "SetSpatialTargetResolved",
                binding,
                collider.bounds.center,
                2.4f,
                "desktop_ray");
            selectionAt = now;
            captureRequested = true;
            return;
        }

        if (captureRequested
            && !screenshotIssued
            && now - selectionAt >= CaptureDelaySeconds)
        {
            if (Application.isBatchMode)
            {
                CaptureRenderedFrame(outputPath);
            }
            else
            {
                ScreenCapture.CaptureScreenshot(outputPath, 1);
            }
            screenshotIssued = true;
        }

        if (screenshotIssued
            && File.Exists(outputPath)
            && new FileInfo(outputPath).Length > 0)
        {
            Debug.Log(SuccessMarker + " " + Path.GetFileName(outputPath));
            Complete(0);
            return;
        }

        if (now - startedAt > TimeoutSeconds)
        {
            var managerStatus = GetPrivateField(manager, "statusMessage") as string;
            Fail(
                "Timed out before a valid V2 binding and screenshot were available; "
                + "manager status: "
                + (string.IsNullOrWhiteSpace(managerStatus)
                    ? "empty"
                    : managerStatus));
        }
    }

    private static FunctionalMldsSceneObjectBinding SelectVisibleBinding(
        FunctionalMldsSceneObjectBindingRegistry registry)
    {
        var camera = Camera.main ?? UnityEngine.Object.FindAnyObjectByType<Camera>();
        FunctionalMldsSceneObjectBinding fallback = null;
        FunctionalMldsSceneObjectBinding best = null;
        var bestScore = float.PositiveInfinity;

        foreach (var candidate in registry.Bindings)
        {
            if (candidate == null || candidate.SelectionCollider == null)
            {
                continue;
            }
            fallback ??= candidate;
            if (camera == null)
            {
                continue;
            }

            var viewport = camera.WorldToViewportPoint(
                candidate.SelectionCollider.bounds.center);
            if (viewport.z <= 0f
                || viewport.x < 0.05f
                || viewport.x > 0.95f
                || viewport.y < 0.05f
                || viewport.y > 0.95f)
            {
                continue;
            }

            var score = Mathf.Abs(viewport.x - 0.5f)
                + Mathf.Abs(viewport.y - 0.5f)
                + viewport.z * 0.0001f;
            if (score < bestScore)
            {
                best = candidate;
                bestScore = score;
            }
        }

        var selected = best ?? fallback;
        if (selected == null)
        {
            throw new InvalidOperationException(
                "The registry contains no binding with a selection collider.");
        }

        if (best == null && camera != null)
        {
            camera.transform.LookAt(selected.SelectionCollider.bounds.center);
        }
        return selected;
    }

    private static void CaptureRenderedFrame(string destination)
    {
        var camera = Camera.main != null
            ? Camera.main
            : UnityEngine.Object.FindAnyObjectByType<Camera>();
        if (camera == null)
        {
            throw new InvalidOperationException(
                "No camera is available for the deterministic interface capture.");
        }

        const int width = 1440;
        const int height = 900;
        var previousTarget = camera.targetTexture;
        var previousActive = RenderTexture.active;
        var canvasStates = new List<CanvasCaptureState>();
        var renderTexture = new RenderTexture(
            width,
            height,
            24,
            RenderTextureFormat.ARGB32);
        var texture = new Texture2D(
            width,
            height,
            TextureFormat.RGB24,
            false);

        try
        {
            foreach (var canvas in UnityEngine.Object.FindObjectsByType<Canvas>(
                         FindObjectsInactive.Exclude))
            {
                if (canvas == null || canvas.renderMode != RenderMode.ScreenSpaceOverlay)
                {
                    continue;
                }

                canvasStates.Add(new CanvasCaptureState(canvas));
                canvas.renderMode = RenderMode.ScreenSpaceCamera;
                canvas.worldCamera = camera;
                canvas.planeDistance = Mathf.Clamp(
                    1.0f,
                    camera.nearClipPlane + 0.01f,
                    camera.farClipPlane - 0.01f);
            }

            Canvas.ForceUpdateCanvases();
            camera.targetTexture = renderTexture;
            camera.Render();
            camera.Render();
            RenderTexture.active = renderTexture;
            texture.ReadPixels(new Rect(0, 0, width, height), 0, 0, false);
            texture.Apply(false, false);
            File.WriteAllBytes(destination, texture.EncodeToPNG());
        }
        finally
        {
            camera.targetTexture = previousTarget;
            RenderTexture.active = previousActive;
            foreach (var state in canvasStates)
            {
                state.Restore();
            }
            UnityEngine.Object.DestroyImmediate(texture);
            renderTexture.Release();
            UnityEngine.Object.DestroyImmediate(renderTexture);
        }
    }

    private sealed class CanvasCaptureState
    {
        private readonly Canvas canvas;
        private readonly RenderMode renderMode;
        private readonly Camera worldCamera;
        private readonly float planeDistance;

        public CanvasCaptureState(Canvas canvas)
        {
            this.canvas = canvas;
            renderMode = canvas.renderMode;
            worldCamera = canvas.worldCamera;
            planeDistance = canvas.planeDistance;
        }

        public void Restore()
        {
            if (canvas == null)
            {
                return;
            }

            canvas.renderMode = renderMode;
            canvas.worldCamera = worldCamera;
            canvas.planeDistance = planeDistance;
        }
    }

    private static object InvokePrivate(object target, string methodName, params object[] arguments)
    {
        var method = target.GetType().GetMethod(
            methodName,
            BindingFlags.Instance | BindingFlags.NonPublic);
        if (method == null)
        {
            throw new MissingMethodException(target.GetType().FullName, methodName);
        }
        return method.Invoke(target, arguments);
    }

    private static void SetPrivateField(object target, string fieldName, object value)
    {
        var field = target.GetType().GetField(
            fieldName,
            BindingFlags.Instance | BindingFlags.NonPublic);
        if (field == null)
        {
            throw new MissingFieldException(target.GetType().FullName, fieldName);
        }
        field.SetValue(target, value);
    }

    private static object GetPrivateField(object target, string fieldName)
    {
        var field = target.GetType().GetField(
            fieldName,
            BindingFlags.Instance | BindingFlags.NonPublic);
        if (field == null)
        {
            throw new MissingFieldException(target.GetType().FullName, fieldName);
        }
        return field.GetValue(target);
    }

    private static void Fail(string message)
    {
        Debug.LogError("[Iui2027InterfaceCapture] " + message);
        Complete(2);
    }

    private static void Complete(int exitCode)
    {
        if (finishing)
        {
            return;
        }
        finishing = true;
        SessionState.SetBool(RunningSessionKey, false);
        SessionState.SetString(OutputSessionKey, string.Empty);
        EditorApplication.update -= Tick;
        EditorApplication.playModeStateChanged -= OnPlayModeStateChanged;
        if (EditorApplication.isPlaying)
        {
            EditorApplication.isPlaying = false;
        }
        EditorApplication.Exit(exitCode);
    }
}
