using UnityEngine;

/// <summary>
/// Nur für den Editor: trägt eine Beschreibung, die im Inspector erscheint.
/// </summary>
[DisallowMultipleComponent]          // verhindert doppelte Anbringung
public class DevDescription : MonoBehaviour
{
    [TextArea(2, 5)]                 // mehrzeiliges Eingabefeld
    [SerializeField] private string description = "Erklärtext hier …";

    // Persistente Zuordnung zwischen dem Platzhalter und seiner generierten
    // Szeneninstanz. So kann die Editor-Pipeline nach einem Domain-Reload
    // fortsetzen, ohne dieselbe Instanz erneut anzulegen.
    [SerializeField, HideInInspector] private string generatedJobId = "";
    [SerializeField, HideInInspector] private string generatedFingerprint = "";
    [SerializeField, HideInInspector] private string generatedContentSignature = "";
    [SerializeField, HideInInspector] private string generatedAssetPath = "";
    [SerializeField, HideInInspector] private GameObject generatedInstance;

    // Falls andere Tools zugreifen wollen
    public string Description
    {
        get => description;
        set => description = value;
    }

    public void SetDescription(string value)
    {
        description = string.IsNullOrWhiteSpace(value) ? "Unnamed object" : value.Trim();
    }

    public string GeneratedJobId => generatedJobId;
    public string GeneratedFingerprint => generatedFingerprint;
    public string GeneratedContentSignature => generatedContentSignature;
    public string GeneratedAssetPath => generatedAssetPath;
    public GameObject GeneratedInstance => generatedInstance;

    public bool HasGeneratedInstance(string jobId, string fingerprint)
    {
        return generatedInstance != null &&
               string.Equals(generatedJobId, jobId, System.StringComparison.Ordinal) &&
               string.Equals(generatedFingerprint, fingerprint, System.StringComparison.Ordinal);
    }

    public void SetGeneratedResult(string jobId, string fingerprint,
                                   string contentSignature, string assetPath,
                                   GameObject instance)
    {
        generatedJobId = jobId ?? "";
        generatedFingerprint = fingerprint ?? "";
        generatedContentSignature = contentSignature ?? "";
        generatedAssetPath = assetPath ?? "";
        generatedInstance = instance;
    }
}


