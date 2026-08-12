using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Assets.Json_Files;
using Newtonsoft.Json;
using UnityEditor;
using UnityEngine;

namespace Assets
{
    public class Writer
    {
        public void WriteScene(ReverseConverter converter)
        {
            Scene2 scene2 = new Scene2
            {
                SceneName = converter.SceneName,
                Environment = new Environment2
                {
                    Type = converter.Environment.Type,
                    Dimensions = new Dimensions3D2
                    {
                        Width = converter.Environment.Dimensions.Width,
                        Height = converter.Environment.Dimensions.Height,
                        Depth = converter.Environment.Dimensions.Depth
                    },
                    Lighting = converter.Environment.Lighting
                        .Select(l => new LightSource2
                        {
                            LightType = l.LightType,
                            Intensity = l.Intensity,
                            Color = l.Color,
                            Range = l.Range,
                            SpotAngle = l.SpotAngle
                        }).ToList(),
                    Background = converter.Environment.Background
                },
                ObjectGroups = converter.ObjectGroups
                    .ToDictionary(
                        kv => kv.Key,
                        kv => new ObjectGroup2 { Color = kv.Value }
                    )
            };

            List<JulangGameObject> exportObjects = converter.GameObjects
                .Where(IsExportable)
                .GroupBy(julang => julang.GameObject)
                .Select(group => group.First())
                .ToList();
            Dictionary<GameObject, JulangGameObject> byGameObject = exportObjects
                .ToDictionary(julang => julang.GameObject, julang => julang);
            Dictionary<JulangGameObject, List<JulangGameObject>> childrenByParent = new Dictionary<JulangGameObject, List<JulangGameObject>>();
            var roots = new List<JulangGameObject>();

            foreach (JulangGameObject julangGameObject in exportObjects)
            {
                JulangGameObject parent = FindKnownParent(julangGameObject, byGameObject);
                if (parent == null)
                {
                    roots.Add(julangGameObject);
                    continue;
                }

                if (!childrenByParent.TryGetValue(parent, out List<JulangGameObject> children))
                {
                    children = new List<JulangGameObject>();
                    childrenByParent[parent] = children;
                }

                children.Add(julangGameObject);
            }

            foreach (JulangGameObject root in roots)
            {
                scene2.Objects.Add(BuildTopLevelObject(root, childrenByParent, byGameObject));
            }

            int childCount = childrenByParent.Values.Sum(children => children.Count);
            if (childCount > 0)
            {
                Debug.Log($"Reverse export preserved {childCount} child object(s) in parent/child hierarchy.");
            }

            SceneData2 sceneData2 = new SceneData2 {Scene = scene2};

            string json = JsonConvert.SerializeObject(sceneData2, Formatting.Indented);

            string folderPath = Path.Combine(Application.dataPath, "Json_Tests", "GPT_Tests");
            string fileName = $"output_reverse_{DateTime.Now:yyyy-MM-dd-HH-mm-ss}.json";
            string filePath = Path.Combine(folderPath, fileName + ".json");

            File.WriteAllText(filePath, json);

            Debug.Log($"JSON gespeichert unter: {filePath}");

            #if UNITY_EDITOR
            AssetDatabase.Refresh();
            #endif
        }

        private static bool IsExportable(JulangGameObject julangGameObject)
        {
            if (julangGameObject == null)
            {
                return false;
            }

            try
            {
                return julangGameObject.GameObject != null;
            }
            catch (MissingReferenceException)
            {
                return false;
            }
        }

        private static JulangGameObject FindKnownParent(
            JulangGameObject julangGameObject,
            Dictionary<GameObject, JulangGameObject> byGameObject)
        {
            Transform parent = julangGameObject.GameObject.transform.parent;
            while (parent != null)
            {
                if (byGameObject.TryGetValue(parent.gameObject, out JulangGameObject parentJulangObject))
                {
                    return parentJulangObject;
                }

                parent = parent.parent;
            }

            return null;
        }

        private static TopLevelSceneObject2 BuildTopLevelObject(
            JulangGameObject julangGameObject,
            Dictionary<JulangGameObject, List<JulangGameObject>> childrenByParent,
            Dictionary<GameObject, JulangGameObject> byGameObject)
        {
            var sceneObject = new TopLevelSceneObject2
            {
                ObjectId = julangGameObject.ObjectId,
                ObjectType = julangGameObject.ObjectType,
                AssetName = julangGameObject.AssetName,
                Position = ToCoordinates(julangGameObject.GameObject.transform.position),
                Rotation = ToCoordinates(julangGameObject.GameObject.transform.eulerAngles),
                Dimensions = ToDimensions(julangGameObject.GameObject.transform.lossyScale),
                Group = julangGameObject.Group,
                Specification = julangGameObject.Specification,
                RelativePositioning = CloneRelativePositioning(julangGameObject.RelativePositioning),
                Offset = CloneCoordinates(julangGameObject.Offset)
            };

            if (childrenByParent.TryGetValue(julangGameObject, out List<JulangGameObject> children))
            {
                sceneObject.Children = children
                    .Select(child => BuildChildObject(child, julangGameObject, childrenByParent, byGameObject))
                    .ToList();
            }

            return sceneObject;
        }

        private static ChildSceneObject2 BuildChildObject(
            JulangGameObject julangGameObject,
            JulangGameObject parent,
            Dictionary<JulangGameObject, List<JulangGameObject>> childrenByParent,
            Dictionary<GameObject, JulangGameObject> byGameObject)
        {
            RelativePositioning2 relativePositioning = CloneRelativePositioning(julangGameObject.RelativePositioning)
                                                       ?? CreateFallbackRelativePositioning(julangGameObject, parent);
            EnsureReferenceObject(relativePositioning, parent);

            XyzCoordinates2 offset = CalculateCurrentOffset(julangGameObject, parent, relativePositioning, byGameObject);
            relativePositioning.Offset = CloneCoordinates(offset);

            var childObject = new ChildSceneObject2
            {
                ObjectId = julangGameObject.ObjectId,
                ObjectType = julangGameObject.ObjectType,
                AssetName = julangGameObject.AssetName,
                RelativePositioning = relativePositioning,
                Rotation = ToCoordinates(julangGameObject.GameObject.transform.eulerAngles),
                Dimensions = ToDimensions(julangGameObject.GameObject.transform.lossyScale),
                Offset = offset,
                Group = julangGameObject.Group,
                Specification = julangGameObject.Specification
            };

            if (childrenByParent.TryGetValue(julangGameObject, out List<JulangGameObject> children))
            {
                childObject.Children = children
                    .Select(child => BuildChildObject(child, julangGameObject, childrenByParent, byGameObject))
                    .ToList();
            }

            return childObject;
        }

        private static RelativePositioning2 CreateFallbackRelativePositioning(JulangGameObject child, JulangGameObject parent)
        {
            Debug.LogWarning(
                $"Reverse export created a generic next_to relation for child '{child.ObjectId}' under parent '{parent.ObjectId}' because no original relation metadata was available.");
            return new RelativePositioning2
            {
                ReferenceObject = parent.ObjectId,
                Relation = "next_to"
            };
        }

        private static void EnsureReferenceObject(RelativePositioning2 relativePositioning, JulangGameObject parent)
        {
            if (relativePositioning == null)
            {
                return;
            }

            if (string.IsNullOrWhiteSpace(relativePositioning.ReferenceObject))
            {
                relativePositioning.ReferenceObject = parent.ObjectId;
            }
        }

        private static XyzCoordinates2 CalculateCurrentOffset(
            JulangGameObject child,
            JulangGameObject parent,
            RelativePositioning2 relativePositioning,
            Dictionary<GameObject, JulangGameObject> byGameObject)
        {
            JulangGameObject reference = ResolveReference(child, parent, relativePositioning, byGameObject);
            Vector3 basePosition = CalculateBasePosition(reference, child, relativePositioning);
            Vector3 worldOffset = child.GameObject.transform.position - basePosition;
            Vector3 localOffset = reference.GameObject.transform.InverseTransformDirection(worldOffset);
            return ToCoordinates(localOffset);
        }

        private static JulangGameObject ResolveReference(
            JulangGameObject child,
            JulangGameObject parent,
            RelativePositioning2 relativePositioning,
            Dictionary<GameObject, JulangGameObject> byGameObject)
        {
            if (relativePositioning != null && !string.IsNullOrWhiteSpace(relativePositioning.ReferenceObject))
            {
                JulangGameObject reference = byGameObject.Values.FirstOrDefault(
                    candidate => candidate.ObjectId == relativePositioning.ReferenceObject);
                if (reference != null)
                {
                    return reference;
                }

                Debug.LogWarning(
                    $"Reverse export could not find reference '{relativePositioning.ReferenceObject}' for child '{child.ObjectId}'. Falling back to parent '{parent.ObjectId}'.");
                relativePositioning.ReferenceObject = parent.ObjectId;
            }

            return parent;
        }

        private static Vector3 CalculateBasePosition(
            JulangGameObject reference,
            JulangGameObject child,
            RelativePositioning2 relativePositioning)
        {
            Bounds referenceBounds = BoundsFromTransform(reference.GameObject.transform);
            Vector3 childHalf = AbsVector(child.GameObject.transform.lossyScale) * 0.5f;
            float distance = Mathf.Max(0f, relativePositioning?.Distance ?? 0f);
            string relation = relativePositioning?.Relation?.Trim() ?? string.Empty;

            switch (relation)
            {
                case "in_front_of_positive_z":
                    return new Vector3(referenceBounds.center.x, referenceBounds.min.y + childHalf.y, referenceBounds.max.z + childHalf.z + distance);
                case "behind_negative_z":
                    return new Vector3(referenceBounds.center.x, referenceBounds.min.y + childHalf.y, referenceBounds.min.z - childHalf.z - distance);
                case "left_of_negative_x":
                    return new Vector3(referenceBounds.min.x - childHalf.x - distance, referenceBounds.min.y + childHalf.y, referenceBounds.center.z);
                case "right_of_positive_x":
                    return new Vector3(referenceBounds.max.x + childHalf.x + distance, referenceBounds.min.y + childHalf.y, referenceBounds.center.z);
                case "on_top_of":
                    return new Vector3(referenceBounds.center.x, referenceBounds.max.y + childHalf.y + distance, referenceBounds.center.z);
                case "below":
                    return new Vector3(referenceBounds.center.x, referenceBounds.min.y - childHalf.y - distance, referenceBounds.center.z);
                case "over":
                    return new Vector3(referenceBounds.center.x, referenceBounds.max.y + childHalf.y + distance, referenceBounds.center.z);
                case "next_to":
                    return referenceBounds.center;
                default:
                    return referenceBounds.center;
            }
        }

        private static Bounds BoundsFromTransform(Transform transform)
        {
            return new Bounds(transform.position, AbsVector(transform.lossyScale));
        }

        private static Vector3 AbsVector(Vector3 value)
        {
            return new Vector3(
                Mathf.Max(Mathf.Abs(value.x), 0.01f),
                Mathf.Max(Mathf.Abs(value.y), 0.01f),
                Mathf.Max(Mathf.Abs(value.z), 0.01f));
        }

        private static Dimensions3D2 ToDimensions(Vector3 scale)
        {
            Vector3 absScale = AbsVector(scale);
            return new Dimensions3D2
            {
                Width = absScale.x,
                Height = absScale.y,
                Depth = absScale.z
            };
        }

        private static XyzCoordinates2 ToCoordinates(Vector3 vector)
        {
            return new XyzCoordinates2
            {
                X = vector.x,
                Y = vector.y,
                Z = vector.z
            };
        }

        private static RelativePositioning2 CloneRelativePositioning(RelativePositioning2 source)
        {
            if (source == null)
            {
                return null;
            }

            return new RelativePositioning2
            {
                ReferenceObject = source.ReferenceObject,
                Relation = source.Relation,
                Distance = source.Distance,
                Offset = CloneCoordinates(source.Offset)
            };
        }

        private static XyzCoordinates2 CloneCoordinates(XyzCoordinates2 source)
        {
            if (source == null)
            {
                return null;
            }

            return new XyzCoordinates2
            {
                X = source.X,
                Y = source.Y,
                Z = source.Z
            };
        }
    }
}
