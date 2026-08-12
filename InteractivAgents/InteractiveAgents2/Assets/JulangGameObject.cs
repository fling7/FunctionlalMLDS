
using Assets.Json_Controller;
using Assets.Json_Files;
using UnityEngine;

namespace Assets
{
    public class JulangGameObject : ScriptableObject
    {
        public string Specification;
        public string ObjectId;
        public string ObjectType;
        public string AssetName;
        public string Group;
        public GameObject GameObject;
        public RelativePositioning2 RelativePositioning;
        public XyzCoordinates2 Offset;

        public void Instantiate(ISceneObject sceneObject)
        {
            this.Specification = sceneObject.Specification;
            this.ObjectId = sceneObject.ObjectId;
            this.ObjectType = sceneObject.ObjectType;
            this.AssetName = sceneObject.AssetName;
            this.Group = sceneObject.Group;
            this.RelativePositioning = null;
            this.Offset = null;

            if (sceneObject is TopLevelSceneObject2 topLevelSceneObject)
            {
                this.RelativePositioning = CloneRelativePositioning(topLevelSceneObject.RelativePositioning);
                this.Offset = CloneCoordinates(topLevelSceneObject.Offset);
            }
            else if (sceneObject is ChildSceneObject2 childSceneObject)
            {
                this.RelativePositioning = CloneRelativePositioning(childSceneObject.RelativePositioning);
                this.Offset = CloneCoordinates(childSceneObject.Offset);
            }
        }

        public void Instantiate(string specification, string objectId, string objectType, string assetName, string group)
        {
            this.Specification = specification;
            this.ObjectId = objectId;
            this.ObjectType = objectType;
            this.AssetName = assetName;
            this.Group = group;
            this.RelativePositioning = null;
            this.Offset = null;
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
