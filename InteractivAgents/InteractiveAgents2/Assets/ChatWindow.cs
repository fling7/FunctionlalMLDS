using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Debug = UnityEngine.Debug;

namespace Assets
{
    public class ChatWindow : EditorWindow
    {
        private Vector2 _scrollPos;
        private string _currentText;
        private List<ChatMessage> _messages = new List<ChatMessage>();
        private Process _pipeLineProcess;
        private Texture2D _droppedImage;
        private bool _isStoppingPython;
        private bool _isPipelineBusy;
        private bool _isWaitingForPythonResponse;
        private bool _isAwaitingConceptChoice;
        private float _pipelineProgress = -1f;
        private string _pipelineProgressText = string.Empty;
        private const string ConceptImagePrefix = "Concept image saved:";
        private const string ConceptChoicePrefix = "[Choice]";
        private const string ProgressPrefix = "[Progress]";
        private const string TracePrefix = "[Trace]";
        private const string ExcerptPrefix = "[Excerpt]";

        private bool InputLocked => (_isPipelineBusy || _isWaitingForPythonResponse) && !_isAwaitingConceptChoice;

        public static ChatWindow OpenWindow()
        {
            ChatWindow window = GetWindow<ChatWindow>("Company Room Pipeline");
            window.minSize = new Vector2(420, 320);
            window.Show();
            window.StartPythonProcess();
            window.AddSystemMessage("Describe the company room you want to create (type 'exit' to quit).");
            return window;
        }

        public void ShowWindow()
        {
            OpenWindow();
        }

        private void OnGUI()
        {
            EditorGUILayout.BeginVertical();

            // Drag & Drop Bereich
            Rect dropArea = GUILayoutUtility.GetRect(0, 50, GUILayout.ExpandWidth(true));
            EditorGUI.BeginDisabledGroup(InputLocked);
            GUI.Box(dropArea, InputLocked ? "Pipeline is running..." : "Drop visual reference image here");
            if (!InputLocked)
            {
                HandleDragAndDrop(dropArea);
            }
            EditorGUI.EndDisabledGroup();

            // Anzeige des Bildes
            if (_droppedImage != null)
            {
                GUILayout.Label(_droppedImage, GUILayout.Height(100), GUILayout.Width(100));
            }

            // Chat-Verlauf
            GUILayout.Label("Room Briefing:", EditorStyles.boldLabel);
            _scrollPos = EditorGUILayout.BeginScrollView(_scrollPos, GUILayout.ExpandHeight(true));
            foreach (var message in _messages)
            {
                DrawCopyableMessage(message);
            }
            EditorGUILayout.EndScrollView();

            // Texteingabe und Senden
            GUILayout.BeginHorizontal();
            EditorGUI.BeginDisabledGroup(InputLocked);
            GUI.SetNextControlName("PipelineInput");
            _currentText = EditorGUILayout.TextField(_currentText);
            bool enterPressed = Event.current.type == EventType.KeyDown
                                && (Event.current.keyCode == KeyCode.Return
                                    || Event.current.keyCode == KeyCode.KeypadEnter)
                                && GUI.GetNameOfFocusedControl() == "PipelineInput";
            bool sendClicked = GUILayout.Button("Send", GUILayout.Width(80));
            EditorGUI.EndDisabledGroup();
            if (sendClicked || enterPressed)
            {
                SendCurrentMessage();
                if (enterPressed)
                {
                    Event.current.Use();
                }
            }
            GUILayout.EndHorizontal();

            if (InputLocked)
            {
                EditorGUILayout.HelpBox(
                    _isPipelineBusy
                        ? "Pipeline laeuft. Eingaben sind bis zum Abschluss gesperrt."
                        : "Warte auf Antwort vom Python-Backend.",
                    MessageType.Info);
            }
            else if (_isAwaitingConceptChoice)
            {
                EditorGUILayout.HelpBox(
                    "Concept-Bild ist fertig. Waehle im Chat 'klassisch', 'bild' oder 'relational'.",
                    MessageType.Info);
            }

            DrawPipelineProgressBar();

            // Steuer-Buttons
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Clear", GUILayout.Width(80)))
            {
                _messages.Clear();
                Repaint();
            }
            if (GUILayout.Button("Copy All", GUILayout.Width(80)))
            {
                CopyAllMessagesToClipboard();
            }
            if (GUILayout.Button("Restart", GUILayout.Width(80)))
            {
                OnApplicationQuit();
                StartPythonProcess();
            }
            if (GUILayout.Button("Exit", GUILayout.Width(80)))
            {
                Exit();
            }
            GUILayout.EndHorizontal();

            EditorGUILayout.EndVertical();
        }

        private void DrawCopyableMessage(ChatMessage message)
        {
            string text = $"{message.User} {message.Text}";
            GUIStyle messageStyle = new GUIStyle(EditorStyles.wordWrappedLabel)
            {
                wordWrap = true,
                richText = false
            };

            float width = Mathf.Max(200f, EditorGUIUtility.currentViewWidth - 42f);
            float height = messageStyle.CalcHeight(new GUIContent(text), width) + 8f;
            EditorGUILayout.SelectableLabel(text, messageStyle, GUILayout.Height(height));

            if (message.Image != null)
            {
                float previewWidth = Mathf.Min(width, 420f);
                float aspect = message.Image.height > 0
                    ? (float)message.Image.width / message.Image.height
                    : 1f;
                float previewHeight = previewWidth / Mathf.Max(0.1f, aspect);

                GUILayout.Label(message.Image, GUILayout.Width(previewWidth), GUILayout.Height(previewHeight));
                GUILayout.BeginHorizontal();
                if (GUILayout.Button("Copy Path", GUILayout.Width(85)))
                {
                    GUIUtility.systemCopyBuffer = message.ImagePath ?? string.Empty;
                }
                if (!string.IsNullOrEmpty(message.ImagePath) && GUILayout.Button("Show File", GUILayout.Width(85)))
                {
                    EditorUtility.RevealInFinder(message.ImagePath);
                }
                GUILayout.EndHorizontal();
            }
        }

        private void CopyAllMessagesToClipboard()
        {
            GUIUtility.systemCopyBuffer = string.Join(
                "\n\n",
                _messages.Select(message => $"{message.User} {message.Text}"));
            AddSystemMessage("Chat copied to clipboard.");
        }

        private void DrawPipelineProgressBar()
        {
            bool shouldShowProgress = _pipelineProgress >= 0f
                                      && (_isPipelineBusy || _isWaitingForPythonResponse || _isAwaitingConceptChoice);
            if (!shouldShowProgress)
            {
                return;
            }

            float progress = Mathf.Clamp01(_pipelineProgress);
            string label = string.IsNullOrWhiteSpace(_pipelineProgressText)
                ? "Pipeline laeuft..."
                : _pipelineProgressText;
            Rect progressRect = GUILayoutUtility.GetRect(18f, 18f, GUILayout.ExpandWidth(true));
            EditorGUI.ProgressBar(progressRect, progress, label);
            GUILayout.Space(4f);
        }

        private void SendCurrentMessage()
        {
            if (InputLocked)
            {
                return;
            }

            string toSentToPipeline = _currentText;
            if (string.IsNullOrWhiteSpace(toSentToPipeline))
            {
                return;
            }

            bool wasAwaitingConceptChoice = _isAwaitingConceptChoice;
            _currentText = string.Empty;
            GUIUtility.keyboardControl = 0;
            Repaint();
            SenMessageToPipeLine(toSentToPipeline);
            if (wasAwaitingConceptChoice)
            {
                _isAwaitingConceptChoice = false;
                _isPipelineBusy = true;
            }
        }

        private void SenMessageToPipeLine(string toSentToPipeline)
        {
            if (string.IsNullOrWhiteSpace(toSentToPipeline))
            {
                return;
            }
            
            _messages.Add(new ChatMessage(text: toSentToPipeline, user: "User: "));
            
            Repaint();

            _isWaitingForPythonResponse = GetPipelineAnswer(toSentToPipeline);
            
            _scrollPos.y = float.MaxValue;
            Repaint();
        }

        private bool GetPipelineAnswer(string question)
        {
            if ((_pipeLineProcess == null || _pipeLineProcess.HasExited) && !StartPythonProcess())
            {
                Debug.LogWarning("[ChatWindow] Python-Prozess nicht verfügbar.");
                AddSystemMessage("Python-Prozess nicht verfügbar. Bitte Unity Console auf Python-Fehler prüfen.");
                return false;
            }

            _pipeLineProcess.StandardInput.WriteLine(question);
            _pipeLineProcess.StandardInput.Flush();
            return true;
        }

        private bool StartPythonProcess()
        {
            if (_pipeLineProcess != null && !_pipeLineProcess.HasExited)
            {
                return true;
            }

            int maxValidatorIterations = Visualizer.Instance.ValidatorIterations;
            string pythonPath = GlobalPaths.PythonPath;
            string pipeLinePath = GlobalPaths.PipeLinePath;
            string mainPath = Path.Combine(pipeLinePath, "main.py");

            if (string.IsNullOrEmpty(pythonPath) || !File.Exists(pythonPath))
            {
                AddSystemMessage("Python.exe wurde nicht gefunden.");
                return false;
            }

            if (string.IsNullOrEmpty(pipeLinePath) || !Directory.Exists(pipeLinePath))
            {
                AddSystemMessage("Pipeline-Ordner wurde nicht gefunden.");
                return false;
            }

            if (!File.Exists(mainPath))
            {
                Debug.LogWarning($"[ChatWindow] main.py nicht gefunden: {mainPath}");
                AddSystemMessage("main.py wurde im Pipeline-Ordner nicht gefunden.");
                return false;
            }

            ProcessStartInfo startInfo = new ProcessStartInfo();
            startInfo.FileName = pythonPath;
            startInfo.WorkingDirectory = pipeLinePath;
            startInfo.Arguments = $"{QuoteArgument(mainPath)} {maxValidatorIterations}";
            startInfo.UseShellExecute = false;
            startInfo.RedirectStandardInput = true;
            startInfo.RedirectStandardOutput = true;
            startInfo.RedirectStandardError = true;
            startInfo.CreateNoWindow = false;
            startInfo.StandardOutputEncoding = System.Text.Encoding.UTF8;
            startInfo.StandardErrorEncoding = System.Text.Encoding.UTF8;
            startInfo.EnvironmentVariables["UNITY_PATH"] = GlobalPaths.UnityProjectPath;
            startInfo.EnvironmentVariables["PYTHONUNBUFFERED"] = "1";
            startInfo.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";

            _pipeLineProcess = new Process();
            _pipeLineProcess.StartInfo = startInfo;
            _pipeLineProcess.EnableRaisingEvents = true;
            _isStoppingPython = false;
            _isPipelineBusy = false;
            _isWaitingForPythonResponse = false;
            _isAwaitingConceptChoice = false;
            _pipelineProgress = -1f;
            _pipelineProgressText = string.Empty;

            _pipeLineProcess.Exited += (sender, e) =>
            {
                int exitCode = -1;
                try
                {
                    exitCode = ((Process)sender).ExitCode;
                }
                catch (System.Exception)
                {
                    // Process may already be disposed while Unity is closing.
                }

                Debug.LogWarning($"[ChatWindow] Python-Prozess beendet. ExitCode: {exitCode}");
                if (!_isStoppingPython)
                {
                    EditorApplication.delayCall += () =>
                    {
                        if (this)
                        {
                            _isPipelineBusy = false;
                            _isWaitingForPythonResponse = false;
                            _isAwaitingConceptChoice = false;
                            AddSystemMessage($"Python-Prozess wurde beendet. ExitCode: {exitCode}");
                        }
                    };
                }
            };

            _pipeLineProcess.OutputDataReceived += (sender, e) =>
            {
                if (!string.IsNullOrEmpty(e.Data))
                {
                    string pythonOutput = e.Data;
                    Debug.LogWarning("Python: " + pythonOutput);
                    // Aktualisierung im Hauptthread über EditorApplication.delayCall
                    EditorApplication.delayCall += () =>
                    {
                        ApplyPipelineStateFromOutput(pythonOutput);
                        _messages.Add(CreatePipelineMessage(pythonOutput));
                        _scrollPos.y = float.MaxValue;
                        _currentText = "";

                        if (pythonOutput.Contains("Json saved"))
                        {
                            try
                            {
                                AssetDatabase.Refresh();
                                Visualizer.Instance.LoadLatestGeneratedJson();
                            }
                            catch (System.Exception ex)
                            {
                                Debug.LogException(ex);
                                AddSystemMessage("Visualizer konnte die JSON-Datei nicht laden: " + ex.Message);
                            }
                        }

                        Repaint();
                    };
                }
            };

            _pipeLineProcess.ErrorDataReceived += (sender, e) =>
            {
                if (!string.IsNullOrEmpty(e.Data))
                {
                    Debug.LogWarning("Python Error: " + e.Data);
                    EditorApplication.delayCall += () =>
                    {
                        _isPipelineBusy = false;
                        _isWaitingForPythonResponse = false;
                        _isAwaitingConceptChoice = false;
                        AddSystemMessage("Python Error: " + e.Data);
                    };
                }
            };

            try
            {
                Debug.Log($"[ChatWindow] Starte Python: {pythonPath} {startInfo.Arguments}");
                Debug.Log($"[ChatWindow] Python WorkingDirectory: {pipeLinePath}");
                _pipeLineProcess.Start();
                _pipeLineProcess.BeginOutputReadLine();
                _pipeLineProcess.BeginErrorReadLine();

                string droppedImagePath = GetDroppedImageFullPath();
                if (!string.IsNullOrEmpty(droppedImagePath))
                {
                    _pipeLineProcess.StandardInput.WriteLine($"Image_flush:{droppedImagePath}");
                    _pipeLineProcess.StandardInput.Flush();
                }

                return true;
            }
            catch (System.Exception ex)
            {
                Debug.LogException(ex);
                AddSystemMessage("Python-Prozess konnte nicht gestartet werden.");
                return false;
            }
        }

        private void OnApplicationQuit()
        {
            StopPythonProcess();
            _isPipelineBusy = false;
            _isWaitingForPythonResponse = false;
            _isAwaitingConceptChoice = false;
            _pipelineProgress = -1f;
            _pipelineProgressText = string.Empty;
            _messages.Clear();
            Repaint();
        }

        private void StopPythonProcess()
        {
            if (_pipeLineProcess != null && !_pipeLineProcess.HasExited)
            {
                try
                {
                    _isStoppingPython = true;
                    _pipeLineProcess.StandardInput.WriteLine("exit");
                    _pipeLineProcess.StandardInput.Flush();
                    _pipeLineProcess.WaitForExit(1000);
                    if (!_pipeLineProcess.HasExited)
                    {
                        _pipeLineProcess.Kill();
                    }
                }
                catch (System.Exception ex)
                {
                    Debug.LogWarning($"[ChatWindow] Python-Prozess konnte nicht sauber beendet werden: {ex.Message}");
                }
            }

            _pipeLineProcess = null;
            _isPipelineBusy = false;
            _isWaitingForPythonResponse = false;
            _isAwaitingConceptChoice = false;
            _pipelineProgress = -1f;
            _pipelineProgressText = string.Empty;
        }

        private void Exit()
        {
            OnApplicationQuit();
            this.Close();
        }

        private void OnDestroy()
        {
            StopPythonProcess();
        }

        private void AddSystemMessage(string text)
        {
            _messages.Add(new ChatMessage(text, "System: "));
            Repaint();
        }

        private ChatMessage CreatePipelineMessage(string pythonOutput)
        {
            if (!pythonOutput.StartsWith(ConceptImagePrefix))
            {
                return new ChatMessage(pythonOutput, "Assistant:");
            }

            string imagePath = pythonOutput.Substring(ConceptImagePrefix.Length).Trim();
            Texture2D image = LoadTextureFromFile(imagePath);
            if (image == null)
            {
                AddSystemMessage("Concept image konnte nicht geladen werden: " + imagePath);
                return new ChatMessage(pythonOutput, "Assistant:");
            }

            return new ChatMessage(pythonOutput, "Assistant:", image, imagePath);
        }

        private static Texture2D LoadTextureFromFile(string imagePath)
        {
            if (string.IsNullOrWhiteSpace(imagePath) || !File.Exists(imagePath))
            {
                return null;
            }

            try
            {
                byte[] bytes = File.ReadAllBytes(imagePath);
                Texture2D texture = new Texture2D(2, 2);
                if (!texture.LoadImage(bytes))
                {
                    return null;
                }

                texture.name = Path.GetFileName(imagePath);
                return texture;
            }
            catch (System.Exception ex)
            {
                Debug.LogWarning($"[ChatWindow] Concept image konnte nicht geladen werden: {ex.Message}");
                return null;
            }
        }

        private void ApplyPipelineStateFromOutput(string pythonOutput)
        {
            if (string.IsNullOrEmpty(pythonOutput))
            {
                return;
            }

            if (TryApplyProgress(pythonOutput))
            {
                return;
            }

            if (pythonOutput.StartsWith(ConceptChoicePrefix))
            {
                _isAwaitingConceptChoice = true;
                _isPipelineBusy = false;
                _isWaitingForPythonResponse = false;
                if (_pipelineProgress < 0f)
                {
                    _pipelineProgress = 0.2f;
                }
                _pipelineProgressText = "Warte auf Auswahl: klassisch oder bild";
                return;
            }

            if (pythonOutput.Contains("Okay, lets go")
                || pythonOutput.StartsWith("[Status] Pipeline started")
                || pythonOutput.StartsWith("[Status] Pipeline mode selected")
                || pythonOutput.StartsWith("[Status] Scene generation agent started"))
            {
                _isAwaitingConceptChoice = false;
                _isPipelineBusy = true;
                _isWaitingForPythonResponse = false;
                return;
            }

            if (pythonOutput.Contains("Json saved")
                || pythonOutput.StartsWith("[Status] Pipeline finished")
                || pythonOutput.StartsWith("[Status] Pipeline failed")
                || pythonOutput.StartsWith("Backend error"))
            {
                _isPipelineBusy = false;
                _isWaitingForPythonResponse = false;
                _isAwaitingConceptChoice = false;
                _pipelineProgress = pythonOutput.Contains("Json saved") || pythonOutput.StartsWith("[Status] Pipeline finished")
                    ? 1f
                    : -1f;
                _pipelineProgressText = _pipelineProgress >= 1f ? "Pipeline fertig" : string.Empty;
                return;
            }

            if (pythonOutput.StartsWith(TracePrefix)
                || pythonOutput.StartsWith(ExcerptPrefix))
            {
                return;
            }

            if (!_isPipelineBusy)
            {
                _isWaitingForPythonResponse = false;
            }
        }

        private bool TryApplyProgress(string pythonOutput)
        {
            if (!pythonOutput.StartsWith(ProgressPrefix))
            {
                return false;
            }

            string payload = pythonOutput.Substring(ProgressPrefix.Length).Trim();
            string[] parts = payload.Split(new[] { ' ' }, 2);
            if (parts.Length == 0)
            {
                return true;
            }

            string[] fraction = parts[0].Split('/');
            if (fraction.Length == 2
                && float.TryParse(fraction[0], out float current)
                && float.TryParse(fraction[1], out float total)
                && total > 0f)
            {
                _pipelineProgress = Mathf.Clamp01(current / total);
            }

            _pipelineProgressText = parts.Length > 1 ? parts[1] : "Pipeline laeuft...";
            string lowerText = _pipelineProgressText.ToLowerInvariant();
            if (lowerText.Contains("waiting for mode choice"))
            {
                _isAwaitingConceptChoice = true;
                _isPipelineBusy = false;
                _isWaitingForPythonResponse = false;
            }
            else
            {
                _isAwaitingConceptChoice = false;
                _isPipelineBusy = true;
                _isWaitingForPythonResponse = false;
            }

            return true;
        }

        private string GetDroppedImageFullPath()
        {
            if (_droppedImage == null)
            {
                return string.Empty;
            }

            string relativePath = AssetDatabase.GetAssetPath(_droppedImage);
            return string.IsNullOrEmpty(relativePath)
                ? string.Empty
                : Path.GetFullPath(Path.Combine(GlobalPaths.UnityProjectPath, relativePath));
        }

        private static string QuoteArgument(string argument)
        {
            return $"\"{argument.Replace("\"", "\\\"")}\"";
        }

        private void HandleDragAndDrop(Rect dropArea)
        {
            Event evt = Event.current;
            if (!dropArea.Contains(evt.mousePosition))
                return;

            switch (evt.type)
            {
                case EventType.DragUpdated:
                case EventType.DragPerform:
                    if (DragAndDrop.objectReferences.Any(o => o is Texture2D))
                        DragAndDrop.visualMode = DragAndDropVisualMode.Copy;
                    else
                        DragAndDrop.visualMode = DragAndDropVisualMode.Rejected;

                    if (evt.type == EventType.DragPerform)
                    {
                        DragAndDrop.AcceptDrag();
                        foreach (var obj in DragAndDrop.objectReferences)
                        {
                            if (obj is Texture2D tex)
                            {
                                _droppedImage = tex;
                                Repaint();

                                string fullPath = GetDroppedImageFullPath();
                                Debug.Log($"[ChatWindow] Gedroppter Asset-Pfad: {fullPath}");

                                if (_pipeLineProcess != null && !_pipeLineProcess.HasExited)
                                {
                                    _pipeLineProcess.StandardInput.WriteLine($"Image_flush:{fullPath}");
                                    _pipeLineProcess.StandardInput.Flush();
                                }
                                else
                                {
                                    Debug.LogWarning("[ChatWindow] Python-Prozess nicht verfügbar.");
                                }

                                break;
                            }
                        }
                    }
                    evt.Use();
                    break;
            }
        }

    }
}
