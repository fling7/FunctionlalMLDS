using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace Assets
{
    /// <summary>
    /// Baut eine warme, wiederholbar konfigurierbare Echtzeitbeleuchtung fuer
    /// generierte Innenraeume auf. Die sichtbaren Leuchtflaechen werden als
    /// eigene Diffusoren angelegt, weil Text-to-3D-GLBs meist nur ein einziges
    /// Material fuer Kabel, Gehaeuse und Schirm enthalten.
    /// </summary>
    public static class CozyRoomLighting
    {
        private readonly struct ShadeProfile
        {
            public readonly Vector3 NormalizedOffset;
            public readonly Vector2 NormalizedDiameter;

            public ShadeProfile(Vector3 normalizedOffset, Vector2 normalizedDiameter)
            {
                NormalizedOffset = normalizedOffset;
                NormalizedDiameter = normalizedDiameter;
            }
        }

        private readonly struct LightingProfile
        {
            public readonly Color AmbientSky;
            public readonly Color AmbientEquator;
            public readonly Color AmbientGround;
            public readonly float AmbientIntensity;
            public readonly Color DirectionalColor;
            public readonly float DirectionalIntensity;
            public readonly Color FixtureColor;
            public readonly float FixtureIntensity;
            public readonly float FixtureRange;
            public readonly float FixtureSpotAngle;
            public readonly Vector3 RoomSize;

            public LightingProfile(Color ambientSky, Color ambientEquator,
                Color ambientGround, float ambientIntensity,
                Color directionalColor, float directionalIntensity,
                Color fixtureColor, float fixtureIntensity, float fixtureRange,
                float fixtureSpotAngle, Vector3 roomSize)
            {
                AmbientSky = ambientSky;
                AmbientEquator = ambientEquator;
                AmbientGround = ambientGround;
                AmbientIntensity = ambientIntensity;
                DirectionalColor = directionalColor;
                DirectionalIntensity = directionalIntensity;
                FixtureColor = fixtureColor;
                FixtureIntensity = fixtureIntensity;
                FixtureRange = fixtureRange;
                FixtureSpotAngle = fixtureSpotAngle;
                RoomSize = roomSize;
            }
        }

        public const string LightingRootName = "__Steinpilz_CozyLighting";
        public const string FixtureRigName = "__Steinpilz_FixtureLighting";
        public const int ProfileVersion = 3;
        private const string DiffuserMaterialName = "Steinpilz_Warm_Light_Diffuser";

        private static readonly Color AmbientSky = new(0.973f, 0.933f, 0.863f);
        private static readonly Color AmbientEquator = new(0.72f, 0.52f, 0.36f);
        private static readonly Color AmbientGround = new(0.31f, 0.22f, 0.15f);
        private static readonly Color WarmLight = new(1.00f, 0.847f, 0.541f);
        private static readonly Color WarmDiffuser = new(1.00f, 0.65f, 0.30f);
        private static readonly Dictionary<int, LightingProfile> SceneProfiles = new();

        private static readonly LightingProfile DefaultProfile = new(
            AmbientSky, AmbientEquator, AmbientGround, 0.70f,
            WarmLight, 0.62f, WarmLight, 1f, 5.8f, 58f,
            new Vector3(14.2f, 4.1f, 10f));

        public static bool ApplyToScene(Scene scene)
        {
            return ApplyToScene(scene, null);
        }

        public static bool ApplyToScene(Scene scene, JulangEnvironment environment)
        {
            if (!scene.IsValid() || !scene.isLoaded) return false;

            Transform[] sceneTransforms = UnityEngine.Object.FindObjectsByType<Transform>(
                    FindObjectsInactive.Include, FindObjectsSortMode.None)
                .Where(item => item != null && item.gameObject.scene == scene)
                .ToArray();
            Transform ceiling = sceneTransforms.FirstOrDefault(IsCeilingPlaceholder);
            Transform[] fixtures = sceneTransforms.Where(IsFixturePlaceholder).ToArray();

            // Nicht in beliebige Unity-Szenen eingreifen. Erst eine MLDS-Decke
            // oder mindestens ein benanntes Lichtobjekt aktiviert den Aufbau.
            if (ceiling == null && fixtures.Length == 0) return false;

            Transform root = GetOrCreateLightingRoot(scene);
            if (root == null) return false;

            LightingProfile profile;
            if (environment != null)
            {
                profile = BuildLightingProfile(environment);
            }
            else if (!TryReadPersistedProfile(root, out profile))
            {
                profile = DefaultProfile;
            }
            SceneProfiles[scene.handle] = profile;
            PersistProfile(root, profile);
            ConfigureAmbientSettings(profile);

            DisableTemplateDirectionalLight(scene, root);
            ConfigureBaseLights(ceiling, root, profile);

            HashSet<string> expectedRootChildren = new(StringComparer.Ordinal)
            {
                "Cozy_DirectionalFill"
            };

            foreach (Transform fixture in fixtures)
            {
                Transform rigParent = ResolveFixtureRigParent(fixture, root);
                if (rigParent == root)
                {
                    expectedRootChildren.Add(BuildGlobalFixtureRigName(fixture));
                }
                ConfigureFixture(fixture, root, profile);
            }

            PruneChildren(root, expectedRootChildren);

            return true;
        }

        public static void RemoveFromScene(Scene scene)
        {
            if (!scene.IsValid() || !scene.isLoaded) return;

            if (RenderSettings.sun != null &&
                IsOwnedLightingTransform(RenderSettings.sun.transform))
            {
                RenderSettings.sun = null;
            }

            foreach (Transform transform in UnityEngine.Object.FindObjectsByType<Transform>(
                         FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                if (transform == null || transform.gameObject.scene != scene) continue;
                if (transform.name == FixtureRigName ||
                    (transform.parent == null && transform.name == LightingRootName))
                {
                    DestroyOwnedGameObject(transform.gameObject);
                }
            }

            foreach (Light light in UnityEngine.Object.FindObjectsByType<Light>(
                         FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                if (light != null && light.gameObject.scene == scene &&
                    IsTemplateDirectionalLight(light))
                {
                    light.enabled = true;
                }
            }

            SceneProfiles.Remove(scene.handle);
            DynamicGI.UpdateEnvironment();
        }

        public static void ConfigureFixture(DevDescription description)
        {
            if (description == null || !description.gameObject.scene.IsValid()) return;
            string key = description.name.ToLowerInvariant();
            if (!IsStripKey(key) && !IsPendantKey(key)) return;

            Scene scene = description.gameObject.scene;
            Transform lightingRoot = GetOrCreateLightingRoot(scene);
            LightingProfile profile = SceneProfiles.TryGetValue(scene.handle, out LightingProfile cached)
                ? cached
                : TryReadPersistedProfile(lightingRoot, out LightingProfile persisted)
                    ? persisted
                    : DefaultProfile;
            SceneProfiles[scene.handle] = profile;
            ConfigureFixture(description.transform, lightingRoot, profile);
        }

        private static void ConfigureFixture(Transform source, Transform lightingRoot,
                                             LightingProfile profile)
        {
            if (source == null || lightingRoot == null) return;

            string key = source.name.ToLowerInvariant();
            bool isStrip = IsStripKey(key);
            bool isPendant = IsPendantKey(key);
            if (!isStrip && !isPendant) return;

            Transform rigParent = ResolveFixtureRigParent(source, lightingRoot);
            string rigName = rigParent == lightingRoot
                ? BuildGlobalFixtureRigName(source)
                : FixtureRigName;
            if (rigParent != lightingRoot)
            {
                Transform obsoleteGlobalRig = lightingRoot.Find(BuildGlobalFixtureRigName(source));
                if (obsoleteGlobalRig != null)
                {
                    DestroyOwnedGameObject(obsoleteGlobalRig.gameObject);
                }
            }
            Transform fixtureRoot = GetOrCreateChild(rigParent, rigName);
            fixtureRoot.localPosition = Vector3.zero;
            fixtureRoot.localRotation = Quaternion.identity;
            fixtureRoot.localScale = Vector3.one;
            Transform placementAnchor = rigParent == lightingRoot ? source : rigParent;

            if (isStrip)
            {
                ConfigureLightStrip(source, placementAnchor, fixtureRoot, profile);
            }
            else
            {
                ConfigurePendant(source, placementAnchor, fixtureRoot,
                    key.Contains("cluster"), profile);
            }
        }

        private static void ConfigureAmbientSettings(LightingProfile profile)
        {
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = profile.AmbientSky;
            RenderSettings.ambientEquatorColor = profile.AmbientEquator;
            RenderSettings.ambientGroundColor = profile.AmbientGround;
            RenderSettings.ambientIntensity = profile.AmbientIntensity;
            RenderSettings.reflectionIntensity = 0.55f;
            RenderSettings.subtractiveShadowColor = new Color(0.18f, 0.10f, 0.07f, 1f);
            DynamicGI.UpdateEnvironment();
        }

        private static LightingProfile BuildLightingProfile(JulangEnvironment environment)
        {
            if (environment == null) return DefaultProfile;

            LightSource ambient = environment.Lighting?.FirstOrDefault(light =>
                string.Equals(light.LightType, "ambient", StringComparison.OrdinalIgnoreCase));
            LightSource directional = environment.Lighting?.FirstOrDefault(light =>
                string.Equals(light.LightType, "directional", StringComparison.OrdinalIgnoreCase));
            LightSource fixture = environment.Lighting?.FirstOrDefault(light =>
                string.Equals(light.LightType, "spot", StringComparison.OrdinalIgnoreCase));

            Color ambientBase = ParseColor(ambient?.Color, AmbientSky);
            Color ambientSky = Color.Lerp(ambientBase, Color.white, 0.04f);
            Color ambientEquator = MultiplyRgb(ambientBase, new Color(0.74f, 0.56f, 0.42f));
            Color ambientGround = MultiplyRgb(ambientBase, new Color(0.32f, 0.24f, 0.18f));
            float ambientIntensity = Mathf.Clamp((ambient?.Intensity ?? 0.62f) * 1.35f,
                0.55f, 0.90f);

            Color directionalColor = ParseColor(directional?.Color, WarmLight);
            float directionalIntensity = Mathf.Clamp(directional?.Intensity ?? 0.55f,
                0.25f, 1.10f);

            Color fixtureColor = ParseColor(fixture?.Color, WarmLight);
            float fixtureIntensity = Mathf.Clamp(fixture?.Intensity ?? 1f, 0.65f, 1.60f);
            float fixtureRange = Mathf.Clamp(fixture?.Range ?? 5.8f, 4.8f, 6.6f);
            float fixtureSpotAngle = Mathf.Clamp(fixture?.SpotAngle ?? 58f, 35f, 82f);

            Vector3 roomSize = DefaultProfile.RoomSize;
            if (environment.Dimensions != null)
            {
                roomSize = new Vector3(
                    Mathf.Max(1f, environment.Dimensions.Width),
                    Mathf.Max(1f, environment.Dimensions.Height),
                    Mathf.Max(1f, environment.Dimensions.Depth));
            }

            return new LightingProfile(ambientSky, ambientEquator, ambientGround,
                ambientIntensity, directionalColor, directionalIntensity,
                fixtureColor, fixtureIntensity, fixtureRange, fixtureSpotAngle, roomSize);
        }

        private static bool TryReadPersistedProfile(Transform root, out LightingProfile profile)
        {
            CozyRoomLightingProfileState state = root != null
                ? root.GetComponent<CozyRoomLightingProfileState>()
                : null;
            if (state == null || state.ProfileVersion != ProfileVersion ||
                state.AmbientIntensity <= 0f ||
                state.DirectionalIntensity <= 0f || state.FixtureIntensity <= 0f ||
                state.FixtureRange <= 0f)
            {
                profile = DefaultProfile;
                return false;
            }

            profile = new LightingProfile(state.AmbientSky, state.AmbientEquator,
                state.AmbientGround, state.AmbientIntensity, state.DirectionalColor,
                state.DirectionalIntensity, state.FixtureColor, state.FixtureIntensity,
                state.FixtureRange, state.FixtureSpotAngle, state.RoomSize);
            return true;
        }

        private static void PersistProfile(Transform root, LightingProfile profile)
        {
            if (root == null) return;
            CozyRoomLightingProfileState state =
                root.GetComponent<CozyRoomLightingProfileState>() ??
                root.gameObject.AddComponent<CozyRoomLightingProfileState>();
            state.ProfileVersion = ProfileVersion;
            state.AmbientSky = profile.AmbientSky;
            state.AmbientEquator = profile.AmbientEquator;
            state.AmbientGround = profile.AmbientGround;
            state.AmbientIntensity = profile.AmbientIntensity;
            state.DirectionalColor = profile.DirectionalColor;
            state.DirectionalIntensity = profile.DirectionalIntensity;
            state.FixtureColor = profile.FixtureColor;
            state.FixtureIntensity = profile.FixtureIntensity;
            state.FixtureRange = profile.FixtureRange;
            state.FixtureSpotAngle = profile.FixtureSpotAngle;
            state.RoomSize = profile.RoomSize;
        }

        private static Color ParseColor(string htmlColor, Color fallback)
        {
            return !string.IsNullOrWhiteSpace(htmlColor) &&
                   ColorUtility.TryParseHtmlString(htmlColor, out Color parsed)
                ? parsed
                : fallback;
        }

        private static Color MultiplyRgb(Color left, Color right)
        {
            return new Color(left.r * right.r, left.g * right.g, left.b * right.b, 1f);
        }

        private static void ConfigureBaseLights(Transform ceiling, Transform root,
                                                LightingProfile profile)
        {
            Vector3 center = ceiling != null
                ? ceiling.position
                : new Vector3(0f, profile.RoomSize.y, 0f);

            Transform directionalTransform = GetOrCreateChild(root, "Cozy_DirectionalFill");
            directionalTransform.SetPositionAndRotation(center, Quaternion.Euler(48f, -32f, 0f));
            Light directional = GetOrCreateLight(directionalTransform.gameObject);
            ConfigureLight(directional, LightType.Directional, profile.DirectionalColor,
                profile.DirectionalIntensity, 0f, 0f);
            RenderSettings.sun = directional;
        }

        private static void DisableTemplateDirectionalLight(Scene scene, Transform lightingRoot)
        {
            foreach (Light light in UnityEngine.Object.FindObjectsByType<Light>(
                         FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                if (light == null || light.gameObject.scene != scene ||
                    light.transform.IsChildOf(lightingRoot))
                {
                    continue;
                }

                if (IsTemplateDirectionalLight(light))
                {
                    light.enabled = false;
                }
            }
        }

        private static bool IsTemplateDirectionalLight(Light light)
        {
            if (light == null) return false;
            Vector3 euler = light.transform.eulerAngles;
            return string.Equals(light.name, "Directional Light", StringComparison.Ordinal) &&
                   light.type == LightType.Directional &&
                   Mathf.Abs(light.intensity - 2f) < 0.01f &&
                   Mathf.Abs(Mathf.DeltaAngle(euler.x, 50f)) < 0.1f &&
                   Mathf.Abs(Mathf.DeltaAngle(euler.y, 330f)) < 0.1f;
        }

        private static void ConfigureLightStrip(Transform source, Transform placementAnchor,
                                                Transform fixtureRoot, LightingProfile profile)
        {
            Vector3 size = Abs(source.lossyScale);
            Vector3 up = placementAnchor.up.normalized;
            Vector3 axis = placementAnchor.right.normalized;
            Vector3 undersideCenter = placementAnchor.position -
                                      up * Mathf.Max(0.04f, size.y * 0.5f);
            if (TryGetFixtureRendererBounds(placementAnchor, out Bounds rendererBounds))
            {
                float bottomProjection = GetMinimumProjection(rendererBounds, up);
                undersideCenter = rendererBounds.center +
                                  up * (bottomProjection -
                                        Vector3.Dot(rendererBounds.center, up));
            }

            GameObject diffuser = GetOrCreatePrimitiveChild(
                PrimitiveType.Cube, fixtureRoot, "Full_Length_Emissive_Diffuser");
            diffuser.transform.SetPositionAndRotation(
                undersideCenter - up * 0.003f,
                placementAnchor.rotation);
            SetWorldScale(diffuser.transform, new Vector3(
                Mathf.Max(0.2f, size.x * 0.995f), 0.004f,
                Mathf.Max(0.06f, size.z * 0.88f)));
            ConfigureEmissiveRenderer(diffuser.GetComponent<Renderer>(),
                profile.FixtureColor, 3.5f);
            Debug.Log($"[LIGHTING] Lightstrip {source.name} an {placementAnchor.name}: " +
                      $"Unterseite={Vector3.Dot(undersideCenter, up):F3}, " +
                      $"Diffuser={Vector3.Dot(diffuser.transform.position, up):F3}");

            const int lightCount = 2;
            HashSet<string> expectedChildren = new(StringComparer.Ordinal)
            {
                "Full_Length_Emissive_Diffuser"
            };
            for (int i = 0; i < lightCount; i++)
            {
                float normalized = lightCount == 1 ? 0f : Mathf.Lerp(-0.31f, 0.31f, i / (lightCount - 1f));
                string lightName = $"Strip_Downlight_{i + 1:00}";
                expectedChildren.Add(lightName);
                Transform lightTransform = GetOrCreateChild(fixtureRoot, lightName);
                lightTransform.position = undersideCenter +
                                          axis * (size.x * normalized) - up * 0.035f;
                lightTransform.rotation = Quaternion.LookRotation(-up, placementAnchor.forward);
                Light light = GetOrCreateLight(lightTransform.gameObject);
                float stripAngle = Mathf.Max(88f, profile.FixtureSpotAngle + 40f);
                ConfigureLight(light, LightType.Spot, profile.FixtureColor,
                    profile.FixtureIntensity * 2.25f,
                    Mathf.Max(5.4f, profile.FixtureRange), stripAngle);
                light.innerSpotAngle = Mathf.Min(stripAngle - 8f, 68f);
            }

            PruneChildren(fixtureRoot, expectedChildren);
        }

        private static void ConfigurePendant(Transform source, Transform placementAnchor,
                                             Transform fixtureRoot, bool isCluster,
                                             LightingProfile profile)
        {
            Vector3 size = Abs(source.lossyScale);
            Vector3 right = placementAnchor.right.normalized;
            Vector3 forward = placementAnchor.forward.normalized;
            Vector3 up = placementAnchor.up.normalized;
            string key = source.name.ToLowerInvariant();
            ShadeProfile[] profiles = GetShadeProfiles(key, isCluster);
            Vector3 averageShadePosition = Vector3.zero;
            HashSet<string> expectedChildren = new(StringComparer.Ordinal)
            {
                "Pendant_Downlight"
            };

            for (int i = 0; i < profiles.Length; i++)
            {
                ShadeProfile shadeProfile = profiles[i];
                Vector3 shadePosition = placementAnchor.position
                                        + right * (shadeProfile.NormalizedOffset.x * size.x)
                                        + up * (shadeProfile.NormalizedOffset.y * size.y)
                                        + forward * (shadeProfile.NormalizedOffset.z * size.z);
                averageShadePosition += shadePosition;

                string glowName = $"Shade_Glow_{i + 1:00}";
                expectedChildren.Add(glowName);
                GameObject glow = GetOrCreatePrimitiveChild(
                    PrimitiveType.Cylinder, fixtureRoot, glowName);
                glow.transform.SetPositionAndRotation(shadePosition, placementAnchor.rotation);
                float diameterX = Mathf.Clamp(
                    size.x * shadeProfile.NormalizedDiameter.x, 0.16f, 0.68f);
                float diameterZ = Mathf.Clamp(
                    size.z * shadeProfile.NormalizedDiameter.y, 0.16f, 0.68f);
                SetWorldScale(glow.transform, new Vector3(diameterX, 0.012f, diameterZ));
                ConfigureEmissiveRenderer(glow.GetComponent<Renderer>(),
                    profile.FixtureColor, 6.5f);

            }

            averageShadePosition /= Mathf.Max(1, profiles.Length);
            Transform lightTransform = GetOrCreateChild(fixtureRoot, "Pendant_Downlight");
            lightTransform.position = averageShadePosition - up * 0.035f;
            lightTransform.rotation = Quaternion.LookRotation(-up, forward);
            Light light = GetOrCreateLight(lightTransform.gameObject);
            float pendantAngle = Mathf.Max(profile.FixtureSpotAngle,
                isCluster ? 72f : 58f);
            ConfigureLight(light, LightType.Spot, profile.FixtureColor,
                profile.FixtureIntensity * (isCluster ? 3.6f : 2.8f),
                Mathf.Max(5.2f, profile.FixtureRange), pendantAngle);
            light.innerSpotAngle = isCluster ? 46f : 34f;
            PruneChildren(fixtureRoot, expectedChildren);
        }

        private static ShadeProfile[] GetShadeProfiles(string key, bool isCluster)
        {
            // Aus den realen GLB-Meshbounds abgeleitete Schirmpositionen. So
            // bleibt beim Counter auch der vierte tatsaechlich vorhandene Schirm
            // aktiv und beim kontaminierten Touch-GLB leuchtet nicht das Moebel.
            if (key.Contains("counter_pendant"))
            {
                return new[]
                {
                    new ShadeProfile(new Vector3(-0.366f, -0.097f, 0f), new Vector2(0.29f, 0.86f)),
                    new ShadeProfile(new Vector3(-0.366f, -0.441f, 0f), new Vector2(0.29f, 0.86f)),
                    new ShadeProfile(new Vector3( 0.000f, -0.304f, 0f), new Vector2(0.30f, 0.89f)),
                    new ShadeProfile(new Vector3( 0.366f, -0.441f, 0f), new Vector2(0.29f, 0.86f))
                };
            }

            if (key.Contains("lounge_pendant"))
            {
                return new[]
                {
                    new ShadeProfile(new Vector3(-0.336f, -0.130f, 0f), new Vector2(0.35f, 0.46f)),
                    new ShadeProfile(new Vector3( 0.336f, -0.010f, 0f), new Vector2(0.35f, 0.46f)),
                    new ShadeProfile(new Vector3( 0.000f, -0.414f, 0f), new Vector2(0.34f, 0.46f))
                };
            }

            if (key.Contains("touch_table_pendant"))
            {
                return new[]
                {
                    new ShadeProfile(new Vector3(0f, 0.283f, 0f), new Vector2(0.38f, 0.40f))
                };
            }

            return isCluster
                ? new[]
                {
                    new ShadeProfile(new Vector3(-0.28f, -0.38f,  0.08f), new Vector2(0.22f, 0.32f)),
                    new ShadeProfile(new Vector3( 0.00f, -0.43f, -0.08f), new Vector2(0.22f, 0.32f)),
                    new ShadeProfile(new Vector3( 0.28f, -0.40f,  0.08f), new Vector2(0.22f, 0.32f))
                }
                : new[]
                {
                    new ShadeProfile(new Vector3(0f, -0.42f, 0f), new Vector2(0.42f, 0.42f))
                };
        }

        private static void ConfigureLight(Light light, LightType type, Color color,
                                           float intensity, float range, float spotAngle)
        {
            light.type = type;
            light.color = color;
            light.intensity = intensity;
            if (range > 0f) light.range = range;
            if (spotAngle > 0f) light.spotAngle = spotAngle;
            light.bounceIntensity = 1f;
            light.shadows = LightShadows.None;
            light.renderMode = LightRenderMode.Auto;
#if UNITY_EDITOR
            light.lightmapBakeType = LightmapBakeType.Realtime;
#endif
            light.enabled = true;
        }

        private static void ConfigureEmissiveRenderer(Renderer renderer, Color lightColor,
                                                       float emissionStrength)
        {
            if (renderer == null) return;

            Shader shader = GraphicsSettings.currentRenderPipeline != null
                ? Shader.Find("Universal Render Pipeline/Lit")
                : Shader.Find("Standard");
            if (shader == null || !shader.isSupported)
            {
                shader = Shader.Find("Standard") ?? Shader.Find("Unlit/Color");
            }
            if (shader == null) return;

            Material material = renderer.sharedMaterial;
            if (material == null || material.name != DiffuserMaterialName || material.shader != shader)
            {
                DestroyOwnedMaterial(material);
                material = new Material(shader)
                {
                    name = DiffuserMaterialName
                };
                renderer.sharedMaterial = material;
            }
            if (material.HasProperty("_BaseColor"))
            {
                material.SetColor("_BaseColor", lightColor);
            }
            if (material.HasProperty("_Color"))
            {
                material.SetColor("_Color", lightColor);
            }
            if (material.HasProperty("_EmissionColor"))
            {
                material.EnableKeyword("_EMISSION");
                Color diffuserColor = Color.Lerp(WarmDiffuser, lightColor, 0.65f);
                material.SetColor("_EmissionColor", diffuserColor * emissionStrength);
                material.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
            }
            if (material.HasProperty("_Smoothness")) material.SetFloat("_Smoothness", 0.32f);
            if (material.HasProperty("_Metallic")) material.SetFloat("_Metallic", 0f);

            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
        }

        private static Transform ResolveFixtureRigParent(Transform source, Transform lightingRoot)
        {
            DevDescription description = source != null
                ? source.GetComponent<DevDescription>()
                : null;
            GameObject generated = description != null ? description.GeneratedInstance : null;
            if (generated != null && generated.scene == source.gameObject.scene)
            {
                return generated.transform;
            }

            if (source != null)
            {
                string generatedNamePrefix = source.name + "_";
                Transform discovered = UnityEngine.Object.FindObjectsByType<Transform>(
                        FindObjectsInactive.Include, FindObjectsSortMode.None)
                    .Where(candidate => candidate != null && candidate != source &&
                                        candidate.gameObject.scene == source.gameObject.scene &&
                                        candidate.gameObject.activeInHierarchy &&
                                        !IsOwnedLightingTransform(candidate) &&
                                        candidate.name.StartsWith(generatedNamePrefix,
                                            StringComparison.OrdinalIgnoreCase) &&
                                        HasGeneratedAssetSuffix(candidate.name) &&
                                        candidate.GetComponentsInChildren<Renderer>(true)
                                            .Any(renderer => renderer != null &&
                                                             !IsOwnedLightingTransform(
                                                                 renderer.transform)))
                    .OrderBy(candidate =>
                        (candidate.position - source.position).sqrMagnitude)
                    .FirstOrDefault();
                if (discovered != null)
                {
                    return discovered;
                }
            }
            return lightingRoot;
        }

        private static bool TryGetFixtureRendererBounds(Transform fixture,
                                                        out Bounds combinedBounds)
        {
            Renderer[] renderers = fixture != null
                ? fixture.GetComponentsInChildren<Renderer>(true)
                    .Where(renderer => renderer != null && renderer.enabled &&
                                       renderer.gameObject.activeInHierarchy &&
                                       !IsOwnedLightingTransform(renderer.transform))
                    .ToArray()
                : Array.Empty<Renderer>();
            if (renderers.Length == 0)
            {
                combinedBounds = default;
                return false;
            }

            combinedBounds = renderers[0].bounds;
            for (int index = 1; index < renderers.Length; index++)
            {
                combinedBounds.Encapsulate(renderers[index].bounds);
            }
            return true;
        }

        private static float GetMinimumProjection(Bounds bounds, Vector3 axis)
        {
            Vector3 absoluteAxis = new(
                Mathf.Abs(axis.x), Mathf.Abs(axis.y), Mathf.Abs(axis.z));
            return Vector3.Dot(bounds.center, axis) -
                   Vector3.Dot(bounds.extents, absoluteAxis);
        }

        private static string BuildGlobalFixtureRigName(Transform source)
        {
            return $"Fixture__{source.name}";
        }

        private static Transform GetOrCreateLightingRoot(Scene scene)
        {
            GameObject[] existingRoots = scene.GetRootGameObjects()
                .Where(item => item != null && item.name == LightingRootName)
                .ToArray();
            GameObject rootObject = existingRoots.FirstOrDefault(item =>
                                        item.GetComponent<CozyRoomLightingProfileState>() != null) ??
                                    existingRoots.FirstOrDefault();
            if (rootObject == null)
            {
                rootObject = new GameObject(LightingRootName);
                SceneManager.MoveGameObjectToScene(rootObject, scene);
            }

            foreach (GameObject duplicate in existingRoots)
            {
                if (duplicate != rootObject)
                {
                    DestroyOwnedGameObject(duplicate);
                }
            }

            rootObject.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            rootObject.transform.localScale = Vector3.one;
            return rootObject.transform;
        }

        private static Transform GetOrCreateChild(Transform parent, string name)
        {
            Transform child = parent.Find(name);
            if (child != null) return child;

            GameObject childObject = new(name);
            childObject.transform.SetParent(parent, false);
            return childObject.transform;
        }

        private static GameObject GetOrCreatePrimitiveChild(PrimitiveType type, Transform parent,
                                                            string name)
        {
            Transform existing = parent.Find(name);
            if (existing != null && existing.GetComponent<MeshFilter>() != null &&
                existing.GetComponent<MeshRenderer>() != null)
            {
                existing.gameObject.SetActive(true);
                return existing.gameObject;
            }
            if (existing != null)
            {
                DestroyOwnedGameObject(existing.gameObject);
            }

            GameObject primitive = GameObject.CreatePrimitive(type);
            primitive.name = name;
            primitive.transform.SetParent(parent, false);
            Collider collider = primitive.GetComponent<Collider>();
            if (collider != null)
            {
                collider.enabled = false;
                DestroyObject(collider);
            }
            return primitive;
        }

        private static Light GetOrCreateLight(GameObject target)
        {
            Light light = target.GetComponent<Light>();
            return light != null ? light : target.AddComponent<Light>();
        }

        private static void PruneChildren(Transform parent, ISet<string> expectedNames)
        {
            for (int index = parent.childCount - 1; index >= 0; index--)
            {
                Transform child = parent.GetChild(index);
                if (!expectedNames.Contains(child.name))
                {
                    DestroyOwnedGameObject(child.gameObject);
                }
            }
        }

        private static void DestroyOwnedGameObject(GameObject target)
        {
            if (target == null) return;

            foreach (Renderer renderer in target.GetComponentsInChildren<Renderer>(true))
            {
                if (renderer == null) continue;
                foreach (Material material in renderer.sharedMaterials)
                {
                    DestroyOwnedMaterial(material);
                }
            }

            target.SetActive(false);
            if (Application.isPlaying)
            {
                target.transform.SetParent(null, true);
            }
            DestroyObject(target);
        }

        private static void DestroyOwnedMaterial(Material material)
        {
            if (material != null && material.name == DiffuserMaterialName)
            {
                DestroyObject(material);
            }
        }

        private static bool IsCeilingPlaceholder(Transform item)
        {
            if (item == null || IsOwnedLightingTransform(item) || HasGeneratedAssetSuffix(item.name))
            {
                return false;
            }
            return item.name.ToLowerInvariant().Contains("room_ceiling");
        }

        private static bool IsFixturePlaceholder(Transform item)
        {
            if (item == null || IsOwnedLightingTransform(item) || HasGeneratedAssetSuffix(item.name))
            {
                return false;
            }
            string key = item.name.ToLowerInvariant();
            return IsStripKey(key) || IsPendantKey(key);
        }

        private static bool IsStripKey(string key)
        {
            return key.Contains("longitudinal_light_strip") || key.Contains("linear_light_fixture");
        }

        private static bool IsPendantKey(string key)
        {
            return key.Contains("pendant_lamp") || key.Contains("pendant_light");
        }

        public static bool IsOwnedLightingTransform(Transform item)
        {
            Transform current = item;
            while (current != null)
            {
                if (current.name == LightingRootName || current.name == FixtureRigName) return true;
                current = current.parent;
            }
            return false;
        }

        private static bool HasGeneratedAssetSuffix(string objectName)
        {
            string key = objectName?.ToLowerInvariant() ?? string.Empty;
            if (key.Contains("_cache_")) return true;

            int separator = key.LastIndexOf('_');
            if (separator < 0 || key.Length - separator - 1 != 32) return false;
            for (int index = separator + 1; index < key.Length; index++)
            {
                char value = key[index];
                if (!((value >= '0' && value <= '9') || (value >= 'a' && value <= 'f')))
                {
                    return false;
                }
            }
            return true;
        }

        private static void DestroyObject(UnityEngine.Object target)
        {
            if (target == null) return;
            if (Application.isPlaying) UnityEngine.Object.Destroy(target);
            else UnityEngine.Object.DestroyImmediate(target);
        }

        private static Vector3 Abs(Vector3 value)
        {
            return new Vector3(Mathf.Abs(value.x), Mathf.Abs(value.y), Mathf.Abs(value.z));
        }

        private static void SetWorldScale(Transform target, Vector3 worldScale)
        {
            Vector3 parentScale = target.parent != null
                ? Abs(target.parent.lossyScale)
                : Vector3.one;
            target.localScale = new Vector3(
                worldScale.x / Mathf.Max(0.0001f, parentScale.x),
                worldScale.y / Mathf.Max(0.0001f, parentScale.y),
                worldScale.z / Mathf.Max(0.0001f, parentScale.z));
        }
    }
}
