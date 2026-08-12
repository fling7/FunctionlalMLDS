
using Assets.Json_Files;
using System.Collections.Generic;
using System.Text;
using UnityEngine;

namespace Assets.Json_Controller
{
    public class JsonController2 : IJsonController
    {
        public SceneData2 SceneData;
        public Dictionary<string, GameObject> spawnedObjects = new Dictionary<string, GameObject>();
        private readonly Dictionary<GameObject, Bounds> spawnedObjectBounds = new Dictionary<GameObject, Bounds>();
        private static readonly HashSet<string> DevDescriptionExcludedTypes = new HashSet<string>
        {
            "floor",
            "floor_surface_detail",
            "floor_inlay",
            "wall",
            "room_wall",
            "architectural_wall",
            "wall_fragment",
            "wallboard",
            "wallpaper",
            "ceiling",
            "ceiling_detail",
            "ceiling_lighting",
            "lighting",
            "light",
            "spot_light",
            "point_light",
            "opening"
        };
        //private UnityConnectionSpawner _spawner = new UnityConnectionSpawner();

        public Dictionary<string, GameObject> LoadScene(object json)
        {
            spawnedObjects = new Dictionary<string, GameObject>();
            spawnedObjectBounds.Clear();

            if (json == null)
            {
                return spawnedObjects;
            }

            SceneData = (SceneData2)json;

            if (SceneData.Scene == null)
            {
                return spawnedObjects;
            }

            Visualizer.Instance.Converter.InitializeJulang(SceneData.Scene);
            SpawnObjects();

            return spawnedObjects;
        }

        public void WriteScene(SceneData2 sceneData)
        {

        }

        private void SpawnObjects()
        {
            if (SceneData == null || SceneData.Scene == null)
            {
                return;
            }

            foreach (TopLevelSceneObject2 topLevelSceneObject in SceneData.Scene.Objects)
            {
                SpawnObject(topLevelSceneObject);
            }
        }

        private GameObject SpawnObject(TopLevelSceneObject2 objData)
        {
            GameObject obj;
            GameObject prefab = Resources.Load<GameObject>(objData.AssetName);
            bool isGeneratedPlaceholder = prefab == null;
            if (prefab != null)
            {
                obj = Visualizer.Instance.Converter.InstantiateObj(prefab, objData);
            }
            else
            {
                //Debug.LogWarning("Prefab " + objData.AssetName + " nicht gefunden. Erstelle leeres GameObject.");
                obj = Visualizer.Instance.Converter.InstantiateObj(Resources.Load<GameObject>("Cube"), objData);
            }
            
            obj.name = objData.ObjectId + "_" + objData.ObjectType;

            // Berechne die Position: Falls relativePositioning definiert ist,
            // versuchen wir, das referenzierte Objekt zu finden.
            Vector3 position;
            if (objData.RelativePositioning != null && !string.IsNullOrEmpty(objData.RelativePositioning.ReferenceObject))
            {
                GameObject refObj = ResolveReferenceObject(objData.RelativePositioning.ReferenceObject, null);
                if (refObj != null)
                {
                    position = CalculateRelativePosition(refObj, objData);
                }
                else
                {
                    //Debug.LogWarning("Referenzobjekt " + objData.RelativePositioning.ReferenceObject + " nicht gefunden für Objekt " + objData.ObjectId);
                    position = ConvertToVector3(objData.Position);
                }
            }
            else
            {
                position = ConvertToVector3(objData.Position);
            }
            obj.transform.position = position;

            // Setze Rotation (Euler-Winkel)
            obj.transform.eulerAngles = ConvertToVector3(objData.Rotation);

            // Setze die Skalierung anhand der Dimensionen
            obj.transform.localScale = new Vector3(objData.Dimensions.Width, objData.Dimensions.Height, objData.Dimensions.Depth);

            if (isGeneratedPlaceholder)
            {
                AttachDevDescription(obj, objData);
            }

            if (!string.IsNullOrEmpty(objData.Group))
            {
                ApplyGroupColor(obj, objData.Group);
            }

            RegisterSpawnedObject(objData.ObjectId, obj);

            // Falls Kind-Objekte definiert sind, spawne diese rekursiv
            if (objData.Children != null)
            {
                foreach (var child in objData.Children)
                {
                    SpawnChildObject(child, obj);
                }
            }

            return obj;
        }

        void SpawnChildObject(ChildSceneObject2 childData, GameObject parent)
        {
            GameObject childObj;
            GameObject prefab = Resources.Load<GameObject>(childData.AssetName);
            bool isGeneratedPlaceholder = prefab == null;
            if (prefab != null)
            {
                childObj = Visualizer.Instance.Converter.InstantiateObj(prefab, childData);
            }
            else
            {
                //Debug.LogWarning("Prefab " + childData.AssetName + " nicht gefunden. Erstelle leeres GameObject.");
                childObj = Visualizer.Instance.Converter.InstantiateObj(Resources.Load<GameObject>("Cube"), childData);
            }
            

            if (!string.IsNullOrEmpty(childData.Group))
            {
                ApplyGroupColor(childObj, childData.Group);
            }

            childObj.name = childData.ObjectId + "_" + childData.ObjectType;

            // Für Child-Objekte erfolgt die Positionierung über relativePositioning.
            // Hier nehmen wir an, dass das referenzierte Objekt in der Regel der Parent ist.
            Vector3 position = parent.transform.position;
            if (childData.RelativePositioning != null && !string.IsNullOrEmpty(childData.RelativePositioning.ReferenceObject))
            {
                GameObject referenceObj = ResolveReferenceObject(childData.RelativePositioning.ReferenceObject, parent);
                position = CalculateRelativePosition(referenceObj, childData);
            }
            childObj.transform.position = position;

            // Setze Rotation
            childObj.transform.eulerAngles = ConvertToVector3(childData.Rotation);

            // Setze Skalierung
            childObj.transform.localScale = new Vector3(childData.Dimensions.Width, childData.Dimensions.Height, childData.Dimensions.Depth);

            if (isGeneratedPlaceholder)
            {
                AttachDevDescription(childObj, childData);
            }

            RegisterSpawnedObject(childData.ObjectId, childObj);
            childObj.transform.SetParent(parent.transform, true);

            // Spawne ggf. weitere verschachtelte Kind-Objekte
            if (childData.Children != null)
            {
                foreach (var nested in childData.Children)
                {
                    SpawnChildObject(nested, childObj);
                }
            }
        }

        private static void AttachDevDescription(GameObject obj, ISceneObject sceneObject)
        {
            if (!ShouldAttachDevDescription(sceneObject))
            {
                return;
            }

            global::DevDescription description = obj.GetComponent<global::DevDescription>();
            if (description == null)
            {
                description = obj.AddComponent<global::DevDescription>();
            }

            description.SetDescription(BuildDevDescriptionText(sceneObject));
        }

        private static bool ShouldAttachDevDescription(ISceneObject sceneObject)
        {
            if (sceneObject == null || !Visualizer.Instance.AddDevDescriptionsToGeneratedPlaceholders)
            {
                return false;
            }

            if (string.IsNullOrWhiteSpace(sceneObject.Specification))
            {
                return false;
            }

            string objectType = sceneObject.ObjectType?.Trim().ToLowerInvariant() ?? string.Empty;
            if (DevDescriptionExcludedTypes.Contains(objectType))
            {
                return false;
            }

            bool isRenderableLightFixture = objectType == "decorative_pendant_light_cluster" ||
                                            objectType == "pendant_light" ||
                                            objectType == "linear_light_fixture";
            return !objectType.EndsWith("_floor") &&
                   !objectType.EndsWith("_wall") &&
                   !objectType.EndsWith("_ceiling") &&
                   (!objectType.Contains("light") || isRenderableLightFixture) &&
                   !objectType.Contains("opening");
        }

        private static string BuildDevDescriptionText(ISceneObject sceneObject)
        {
            StringBuilder builder = new StringBuilder();

            if (!string.IsNullOrWhiteSpace(sceneObject.ObjectType))
            {
                builder.Append(sceneObject.ObjectType.Trim());
            }

            if (builder.Length > 0)
            {
                builder.Append(": ");
            }

            builder.Append(sceneObject.Specification.Trim());
            return builder.ToString();
        }

        Vector3 ConvertToVector3(XyzCoordinates2 coords)
        {
            return coords == null ? Vector3.zero : new Vector3(coords.X, coords.Y, coords.Z);
        }

        private GameObject ResolveReferenceObject(string referenceObject, GameObject fallback)
        {
            if (!string.IsNullOrEmpty(referenceObject) &&
                spawnedObjects.TryGetValue(referenceObject, out GameObject referenceObj))
            {
                return referenceObj;
            }

            if (fallback != null)
            {
                Debug.LogWarning($"Reference object '{referenceObject}' not found. Falling back to parent '{fallback.name}'.");
                return fallback;
            }

            return null;
        }

        private void RegisterSpawnedObject(string objectId, GameObject obj)
        {
            if (obj == null)
            {
                return;
            }

            if (!string.IsNullOrEmpty(objectId))
            {
                spawnedObjects[objectId] = obj;
            }

            spawnedObjectBounds[obj] = CalculateObjectBounds(obj);
        }

        private Bounds GetReferenceBounds(GameObject referenceObj)
        {
            if (referenceObj != null && spawnedObjectBounds.TryGetValue(referenceObj, out Bounds cachedBounds))
            {
                return cachedBounds;
            }

            Bounds bounds = CalculateObjectBounds(referenceObj);
            if (referenceObj != null)
            {
                spawnedObjectBounds[referenceObj] = bounds;
            }

            return bounds;
        }

        private static Bounds CalculateObjectBounds(GameObject obj)
        {
            if (obj == null)
            {
                return new Bounds(Vector3.zero, Vector3.one);
            }

            Renderer[] renderers = obj.GetComponentsInChildren<Renderer>();
            if (renderers.Length > 0)
            {
                Bounds bounds = renderers[0].bounds;
                for (int i = 1; i < renderers.Length; i++)
                {
                    bounds.Encapsulate(renderers[i].bounds);
                }

                return bounds;
            }

            Vector3 size = obj.transform.lossyScale;
            size = new Vector3(Mathf.Abs(size.x), Mathf.Abs(size.y), Mathf.Abs(size.z));
            if (size == Vector3.zero)
            {
                size = Vector3.one;
            }

            return new Bounds(obj.transform.position, size);
        }

        Vector3 CalculateRelativePosition(GameObject referenceObj, TopLevelSceneObject2 objData)
        {
            return CalculatePosition(referenceObj, objData.RelativePositioning, objData.Dimensions, objData.Offset);
        }

        Vector3 CalculateRelativePosition(GameObject referenceObj, ChildSceneObject2 childData)
        {
            return CalculatePosition(referenceObj, childData.RelativePositioning, childData.Dimensions, childData.Offset);
        }

        Vector3 CalculatePosition(GameObject referenceObj, RelativePositioning2 rel, Dimensions3D2 childDim, XyzCoordinates2 objectOffset)
        {
            if (referenceObj == null || rel == null)
            {
                return Vector3.zero;
            }

            Bounds refBounds = GetReferenceBounds(referenceObj);
            Vector3 childSize = DimensionsToVector(childDim);
            Vector3 childHalf = childSize * 0.5f;
            float distance = Mathf.Max(0f, rel.Distance);
            string relation = rel.Relation?.Trim() ?? string.Empty;

            Vector3 position = refBounds.center;
            switch (relation)
            {
                case "in_front_of_positive_z":
                    position = new Vector3(
                        refBounds.center.x,
                        refBounds.min.y + childHalf.y,
                        refBounds.max.z + childHalf.z + distance);
                    break;
                case "behind_negative_z":
                    position = new Vector3(
                        refBounds.center.x,
                        refBounds.min.y + childHalf.y,
                        refBounds.min.z - childHalf.z - distance);
                    break;
                case "left_of_negative_x":
                    position = new Vector3(
                        refBounds.min.x - childHalf.x - distance,
                        refBounds.min.y + childHalf.y,
                        refBounds.center.z);
                    break;
                case "right_of_positive_x":
                    position = new Vector3(
                        refBounds.max.x + childHalf.x + distance,
                        refBounds.min.y + childHalf.y,
                        refBounds.center.z);
                    break;
                case "on_top_of":
                    position = new Vector3(
                        refBounds.center.x,
                        refBounds.max.y + childHalf.y + distance,
                        refBounds.center.z);
                    break;
                case "below":
                    position = new Vector3(
                        refBounds.center.x,
                        refBounds.min.y - childHalf.y - distance,
                        refBounds.center.z);
                    break;
                case "over":
                    position = new Vector3(
                        refBounds.center.x,
                        refBounds.max.y + childHalf.y + distance,
                        refBounds.center.z);
                    break;
                case "next_to":
                    if (objectOffset == null && rel.Offset == null)
                    {
                        position = new Vector3(
                            refBounds.max.x + childHalf.x + distance,
                            refBounds.min.y + childHalf.y,
                            refBounds.center.z);
                    }
                    break;
                default:
                    break;
            }

            return position + ResolveRelationOffset(referenceObj.transform, rel, objectOffset, relation);
        }

        private static Vector3 DimensionsToVector(Dimensions3D2 dimensions)
        {
            if (dimensions == null)
            {
                return Vector3.one;
            }

            return new Vector3(
                Mathf.Max(Mathf.Abs(dimensions.Width), 0.01f),
                Mathf.Max(Mathf.Abs(dimensions.Height), 0.01f),
                Mathf.Max(Mathf.Abs(dimensions.Depth), 0.01f));
        }

        private Vector3 ResolveOffset(Transform referenceTransform, RelativePositioning2 rel, XyzCoordinates2 objectOffset)
        {
            XyzCoordinates2 offset = objectOffset ?? rel?.Offset;
            return ResolveOffset(referenceTransform, offset);
        }

        private Vector3 ResolveRelationOffset(
            Transform referenceTransform,
            RelativePositioning2 rel,
            XyzCoordinates2 objectOffset,
            string relation)
        {
            XyzCoordinates2 offset = objectOffset ?? rel?.Offset;
            if (offset == null)
            {
                return Vector3.zero;
            }

            Vector3 localOffset = ConvertToVector3(offset);
            if (IsVerticalContactRelation(relation))
            {
                localOffset.y = 0f;
            }

            return referenceTransform == null
                ? localOffset
                : referenceTransform.TransformDirection(localOffset);
        }

        private Vector3 ResolveOffset(Transform referenceTransform, XyzCoordinates2 offset)
        {
            if (offset == null)
            {
                return Vector3.zero;
            }

            Vector3 localOffset = ConvertToVector3(offset);
            return referenceTransform == null
                ? localOffset
                : referenceTransform.TransformDirection(localOffset);
        }

        private static bool IsVerticalContactRelation(string relation)
        {
            return relation == "on_top_of" || relation == "over" || relation == "below";
        }

        private void ApplyGroupColor(GameObject obj, string groupName)
        {
            if (SceneData?.Scene?.ObjectGroups != null &&
                SceneData.Scene.ObjectGroups.TryGetValue(groupName, out ObjectGroup2 groupData))
            {
                if (!string.IsNullOrEmpty(groupData.Color))
                {
                    if (ColorUtility.TryParseHtmlString(groupData.Color, out Color parsedColor))
                    {
                        Renderer[] renderers = obj.GetComponentsInChildren<Renderer>();
                        if (renderers.Length == 0)
                        {
                            Renderer renderer = obj.AddComponent<MeshRenderer>();
                            if (obj.GetComponent<MeshFilter>() == null)
                            {
                                obj.AddComponent<MeshFilter>();
                            }

                            renderers = new[] { renderer };
                        }

                        foreach (Renderer renderer in renderers)
                        {
                            Visualizer.ApplyRendererColor(renderer, parsedColor);
                        }
                    }
                }
            }
        }



    }
}
