
using System.IO;
using UnityEngine;

namespace Assets
{
    public static class GlobalPaths
    {
        private const string FixedPythonPath = @"C:\Users\burklo\AppData\Local\Programs\Python\Python312\python.exe";
        private const string FixedPipeLinePath = @"C:\Users\burklo\Documents\VR Projekt Dive\RoomGenerationPipeline\pipeline_test_v1";

        public static string PythonPath
        {
            get
            {
                if (File.Exists(FixedPythonPath))
                {
                    return FixedPythonPath;
                }

                Debug.LogWarning($"GlobalPaths: Python Path nicht gefunden: {FixedPythonPath}");
                return string.Empty;
            }
        }

        public static string PipeLinePath
        {
            get
            {
                if (Directory.Exists(FixedPipeLinePath))
                {
                    return FixedPipeLinePath;
                }

                Debug.LogWarning($"GlobalPaths: PipeLine Path nicht gefunden: {FixedPipeLinePath}");
                return string.Empty;
            }
        }

        public static string UnityProjectPath
        {
            get
            {
                DirectoryInfo assetsDirectory = Directory.GetParent(Application.dataPath);
                return assetsDirectory?.FullName ?? string.Empty;
            }
        }
    }
}
