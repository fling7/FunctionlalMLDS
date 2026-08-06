#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

public static class ArrowProjectWizardSmokeTest
{
    [MenuItem("Tools/Interactive Agents/Tests/Run MLDSI Wizard 1.0 Smoke Test")]
    public static void RunFromMenu()
    {
        var report = ArrowProjectWizard.RunEditorSmokeTest();
        Debug.Log(report);
        EditorUtility.DisplayDialog("MLDSI Wizard Smoke Test", report, "OK");
    }

    // Batch mode:
    // Unity.exe -batchmode -quit -projectPath <project> \
    //   -executeMethod ArrowProjectWizardSmokeTest.RunFromCommandLine -logFile -
    public static void RunFromCommandLine()
    {
        Debug.Log(ArrowProjectWizard.RunEditorSmokeTest());
    }
}
#endif
