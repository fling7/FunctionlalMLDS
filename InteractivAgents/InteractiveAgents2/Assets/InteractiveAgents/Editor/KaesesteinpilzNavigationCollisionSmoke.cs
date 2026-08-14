using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>
/// Batch-safe regression smoke for the participant collision profile.
///
/// It intentionally exercises the private runtime setup used by the study instead of
/// duplicating its collider-generation rules here.  The checks cover the two user-visible
/// contracts that regressed: chairs are real barriers, while both circulation lanes next
/// to the central touch table remain traversable by the configured player capsule.
/// </summary>
public static class KaesesteinpilzNavigationCollisionSmoke
{
    private const string MenuPath =
        "Tools/Interactive Agents/Tests/Run KAESESTEINPILZ Navigation Collision Smoke";
    private const string NavigationProxyPrefix = "Navigation Footprint - ";
    private const float GridSpacing = 0.18f;

    private static readonly BindingFlags InstancePrivate =
        BindingFlags.Instance | BindingFlags.NonPublic;

    [MenuItem(MenuPath)]
    public static void RunFromMenu()
    {
        Run();
        EditorUtility.DisplayDialog(
            "KAESESTEINPILZ Navigation",
            "Chair barriers and both central circulation lanes passed.",
            "OK");
    }

    // Unity.exe -batchmode -projectPath <project> -executeMethod
    // KaesesteinpilzNavigationCollisionSmoke.RunFromCommandLine -quit -logFile -
    public static void RunFromCommandLine()
    {
        try
        {
            Run();
            Debug.Log("[KaesesteinpilzNavigationCollisionSmoke] OK");
            EditorApplication.Exit(0);
        }
        catch (Exception exception)
        {
            Debug.LogException(exception);
            EditorApplication.Exit(1);
        }
    }

    private static void Run()
    {
        var scene = EditorSceneManager.OpenScene(
            KaesesteinpilzUserTestQuickAgentManager.StudyScenePath,
            OpenSceneMode.Single);
        Require(scene.IsValid(), "The KAESESTEINPILZ scene could not be opened.");

        var study = UnityEngine.Object.FindAnyObjectByType<
            KaesesteinpilzUserTestQuickAgentManager>(FindObjectsInactive.Include);
        Require(study != null, "The study manager is missing from SampleScene.");

        var core = study.GetComponent<QuickAgentManager>();
        Require(core != null, "The composed QuickAgentManager is missing.");
        core.ensureFallbackGroundCollider = true;
        core.ensureSceneObjectColliders = true;
        InvokeRuntimeSetup(core, "EnsureFallbackGroundCollider");
        InvokeRuntimeSetup(core, "EnsureSceneObjectColliders");
        InvokeRuntimeSetup(study, "EnsurePlayerRig");
        InvokeRuntimeSetup(study, "ConfigurePreciseGeneratedNavigationColliders");
        Physics.SyncTransforms();

        var controller = GetPrivateField<CharacterController>(study, "characterController");
        Require(controller != null && controller.enabled,
            "Runtime setup did not create an enabled CharacterController.");

        RequireCollisionFilterSurvivesControllerReenable(study, controller);
        RequireChairBarriers(controller);
        RequireCentralCirculationLanes(controller);
    }

    private static void RequireCollisionFilterSurvivesControllerReenable(
        KaesesteinpilzUserTestQuickAgentManager study,
        CharacterController controller)
    {
        // The real start-positioning path disables and re-enables the controller.
        // Unity drops pairwise IgnoreCollision state at that point, so the idempotent
        // configuration method must restore the complete allow-list.
        controller.enabled = false;
        controller.enabled = true;
        InvokeRuntimeSetup(study, "ConfigurePreciseGeneratedNavigationColliders");
        Physics.SyncTransforms();

        var proxySet = new HashSet<Collider>(FindNavigationProxies());
        Require(proxySet.Count > 0, "No navigation footprints were generated.");

        var colliders = UnityEngine.Object.FindObjectsByType<Collider>(
            FindObjectsInactive.Exclude,
            FindObjectsSortMode.None);
        var broadColliderCount = 0;
        foreach (var collider in colliders)
        {
            if (collider == null || collider == controller || !collider.enabled
                || collider.isTrigger)
                continue;

            var shouldCollide = proxySet.Contains(collider)
                || string.Equals(collider.gameObject.name,
                    "InteractiveAgents_FallbackGround",
                    StringComparison.OrdinalIgnoreCase);
            var ignored = Physics.GetIgnoreCollision(controller, collider);
            Require(ignored != shouldCollide,
                "Collision allow-list was not restored for '"
                + collider.gameObject.name + "' (shouldCollide="
                + shouldCollide + ").");
            if (!shouldCollide)
                broadColliderCount++;
        }

        Require(broadColliderCount > 0,
            "The lifecycle regression did not exercise any broad scene collider.");
    }

    private static void RequireChairBarriers(CharacterController controller)
    {
        var chairs = UnityEngine.Object.FindObjectsByType<DevDescription>(
                FindObjectsInactive.Include,
                FindObjectsSortMode.None)
            .Where(description => description != null
                && description.GeneratedInstance != null
                && description.GeneratedInstance.activeInHierarchy
                && IsChairName(description.gameObject.name))
            .ToArray();
        Require(chairs.Length >= 1,
            "No generated lounge chair is available for the navigation regression check.");

        var allProxies = FindNavigationProxies();
        foreach (var chair in chairs)
        {
            var matching = allProxies
                .Where(collider => collider.gameObject.name.IndexOf(
                    chair.gameObject.name,
                    StringComparison.OrdinalIgnoreCase) >= 0)
                .ToArray();
            Require(matching.Length >= 1,
                "No navigation barrier was generated for chair '"
                + chair.gameObject.name + "'.");

            var dimensions = Abs(chair.transform.lossyScale);
            var intendedBottom = chair.transform.position.y - dimensions.y * 0.5f;
            var barrierTop = matching.Max(collider => collider.bounds.max.y);
            var barrierHeight = barrierTop - Mathf.Max(0f, intendedBottom);

            // A barrier ending at or below stepOffset is treated as a stair by Unity's
            // CharacterController.  Skin width plus a small tolerance keeps the contract
            // stable across PhysX/platform rounding without forcing full visual bounds.
            var minimumBarrierHeight = controller.stepOffset
                + controller.skinWidth
                + 0.08f;
            Require(barrierHeight >= minimumBarrierHeight,
                "Chair '" + chair.gameObject.name + "' can be stepped over: barrier height "
                + barrierHeight.ToString("F3") + " m, required at least "
                + minimumBarrierHeight.ToString("F3") + " m (stepOffset "
                + controller.stepOffset.ToString("F3") + " m).");
        }
    }

    private static void RequireCentralCirculationLanes(CharacterController controller)
    {
        var centralTable = UnityEngine.Object.FindObjectsByType<DevDescription>(
                FindObjectsInactive.Include,
                FindObjectsSortMode.None)
            .FirstOrDefault(description => description != null
                && description.gameObject.name.IndexOf(
                    "central_touch_table",
                    StringComparison.OrdinalIgnoreCase) >= 0);
        Require(centralTable != null, "The central touch-table placeholder is missing.");

        var tableSize = Abs(centralTable.transform.lossyScale);
        var halfWidth = tableSize.x * 0.5f;
        var halfDepth = tableSize.z * 0.5f;

        // The source description promises wide circulation on both sides.  Search a
        // 2.4 m strip outside each long table edge and require a capsule-sized route
        // from the visitor-facing side to the service-counter side.
        var lateralNear = halfWidth + controller.radius + 0.12f;
        var lateralFar = halfWidth + 2.4f;
        var longitudinalExtent = halfDepth + 1.35f;
        var navigationObstacles = ActiveNavigationObstacles(controller).ToArray();

        using (var probe = new CapsuleProbe(controller))
        {
            Require(HasConnectedLane(
                    centralTable.transform,
                    probe,
                    navigationObstacles,
                    -lateralFar,
                    -lateralNear,
                    -longitudinalExtent,
                    longitudinalExtent),
                "The left circulation lane beside the central touch table is blocked.");
            Require(HasConnectedLane(
                    centralTable.transform,
                    probe,
                    navigationObstacles,
                    lateralNear,
                    lateralFar,
                    -longitudinalExtent,
                    longitudinalExtent),
                "The right circulation lane beside the central touch table is blocked.");
        }
    }

    private static bool HasConnectedLane(
        Transform reference,
        CapsuleProbe probe,
        IReadOnlyList<Collider> obstacles,
        float minX,
        float maxX,
        float minZ,
        float maxZ)
    {
        var width = Mathf.FloorToInt((maxX - minX) / GridSpacing) + 1;
        var depth = Mathf.FloorToInt((maxZ - minZ) / GridSpacing) + 1;
        if (width < 2 || depth < 2)
            return false;

        var free = new bool[width, depth];
        for (var z = 0; z < depth; z++)
        {
            for (var x = 0; x < width; x++)
            {
                var local = new Vector3(
                    minX + x * GridSpacing,
                    0f,
                    minZ + z * GridSpacing);
                // tableSize already contains lossyScale; applying TransformPoint here
                // would scale the lane dimensions a second time.
                var world = reference.position + reference.rotation * local;
                world.y = 0.02f;
                free[x, z] = !probe.Overlaps(world, obstacles);
            }
        }

        var queue = new Queue<Vector2Int>();
        var visited = new bool[width, depth];
        for (var x = 0; x < width; x++)
        {
            if (!free[x, 0])
                continue;
            visited[x, 0] = true;
            queue.Enqueue(new Vector2Int(x, 0));
        }

        var directions = new[]
        {
            new Vector2Int(1, 0),
            new Vector2Int(-1, 0),
            new Vector2Int(0, 1),
            new Vector2Int(0, -1)
        };
        while (queue.Count > 0)
        {
            var current = queue.Dequeue();
            if (current.y == depth - 1)
                return true;
            foreach (var direction in directions)
            {
                var next = current + direction;
                if (next.x < 0 || next.x >= width || next.y < 0 || next.y >= depth
                    || visited[next.x, next.y] || !free[next.x, next.y])
                    continue;
                visited[next.x, next.y] = true;
                queue.Enqueue(next);
            }
        }
        return false;
    }

    private static IEnumerable<Collider> ActiveNavigationObstacles(
        CharacterController controller)
    {
        var colliders = UnityEngine.Object.FindObjectsByType<Collider>(
            FindObjectsInactive.Exclude,
            FindObjectsSortMode.None);
        foreach (var collider in colliders)
        {
            if (collider == null || collider == controller || !collider.enabled
                || collider.isTrigger || IsFloor(collider)
                || Physics.GetIgnoreCollision(controller, collider))
                continue;
            yield return collider;
        }
    }

    private static bool IsFloor(Collider collider)
    {
        var bounds = collider.bounds;
        var size = bounds.size;
        return bounds.max.y < 0.18f && size.y < 0.25f
            && (size.x > 2f || size.z > 2f);
    }

    private static Collider[] FindNavigationProxies()
    {
        return UnityEngine.Object.FindObjectsByType<Collider>(
                FindObjectsInactive.Exclude,
                FindObjectsSortMode.None)
            .Where(collider => collider != null
                && collider.gameObject.layer == 2
                && collider.gameObject.name.StartsWith(
                    NavigationProxyPrefix,
                    StringComparison.Ordinal))
            .ToArray();
    }

    private static bool IsChairName(string value)
    {
        return value.IndexOf("chair", StringComparison.OrdinalIgnoreCase) >= 0
            || value.IndexOf("stuhl", StringComparison.OrdinalIgnoreCase) >= 0;
    }

    private static Vector3 Abs(Vector3 value)
    {
        return new Vector3(Mathf.Abs(value.x), Mathf.Abs(value.y), Mathf.Abs(value.z));
    }

    private static void InvokeRuntimeSetup(object target, string methodName)
    {
        var method = target.GetType().GetMethod(methodName, InstancePrivate);
        Require(method != null, "Runtime setup method is missing: " + methodName);
        method.Invoke(target, null);
    }

    private static T GetPrivateField<T>(object target, string fieldName)
        where T : class
    {
        var field = target.GetType().GetField(fieldName, InstancePrivate);
        Require(field != null, "Runtime field is missing: " + fieldName);
        return field.GetValue(target) as T;
    }

    private static void Require(bool condition, string message)
    {
        if (!condition)
            throw new InvalidOperationException(
                "[KaesesteinpilzNavigationCollisionSmoke] " + message);
    }

    private sealed class CapsuleProbe : IDisposable
    {
        private readonly GameObject root;
        private readonly CapsuleCollider capsule;

        public CapsuleProbe(CharacterController controller)
        {
            root = new GameObject("__KAESESTEINPILZ_NavigationProbe");
            root.hideFlags = HideFlags.HideAndDontSave;
            capsule = root.AddComponent<CapsuleCollider>();
            capsule.direction = 1;
            capsule.radius = controller.radius;
            capsule.height = controller.height;
            capsule.center = controller.center;
        }

        public bool Overlaps(Vector3 position, IReadOnlyList<Collider> obstacles)
        {
            root.transform.position = position;
            root.transform.rotation = Quaternion.identity;
            for (var i = 0; i < obstacles.Count; i++)
            {
                var obstacle = obstacles[i];
                if (obstacle == null || !obstacle.enabled)
                    continue;
                if (Physics.ComputePenetration(
                    capsule,
                    root.transform.position,
                    root.transform.rotation,
                    obstacle,
                    obstacle.transform.position,
                    obstacle.transform.rotation,
                    out _,
                    out _))
                    return true;
            }
            return false;
        }

        public void Dispose()
        {
            if (root != null)
                UnityEngine.Object.DestroyImmediate(root);
        }
    }
}
