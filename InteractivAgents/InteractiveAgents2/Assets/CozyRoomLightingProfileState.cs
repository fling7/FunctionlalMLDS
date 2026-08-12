using UnityEngine;

namespace Assets
{
    [AddComponentMenu("")]
    [DisallowMultipleComponent]
    public sealed class CozyRoomLightingProfileState : MonoBehaviour
    {
        [HideInInspector] public int ProfileVersion;
        [HideInInspector] public Color AmbientSky;
        [HideInInspector] public Color AmbientEquator;
        [HideInInspector] public Color AmbientGround;
        [HideInInspector] public float AmbientIntensity;
        [HideInInspector] public Color DirectionalColor;
        [HideInInspector] public float DirectionalIntensity;
        [HideInInspector] public Color FixtureColor;
        [HideInInspector] public float FixtureIntensity;
        [HideInInspector] public float FixtureRange;
        [HideInInspector] public float FixtureSpotAngle;
        [HideInInspector] public Vector3 RoomSize;
    }
}
