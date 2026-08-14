from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.case_study_pipeline.llm_client import LlmStageError, load_llm_settings


class LlmClientSettingsTests(unittest.TestCase):
    def config(self, root: Path, key: str = "config-key") -> Path:
        path = root / "config.json"
        path.write_text(json.dumps({"openai_api_key": key}), encoding="utf-8")
        return path

    def test_file_secret_overrides_config_and_trims_newline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = self.config(root)
            secret = root / "key"
            secret.write_text("file-key\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {"OPENAI_API_KEY_FILE": str(secret)}, clear=True):
                settings = load_llm_settings(config_path=config)
            self.assertEqual(settings.api_key, "file-key")

    def test_direct_secret_overrides_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = self.config(Path(temp_dir))
            with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}, clear=True):
                settings = load_llm_settings(config_path=config)
            self.assertEqual(settings.api_key, "env-key")

    def test_conflicting_or_broken_file_secret_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = self.config(root)
            with mock.patch.dict(
                os.environ,
                {"OPENAI_API_KEY": "one", "OPENAI_API_KEY_FILE": str(root / "key")},
                clear=True,
            ):
                with self.assertRaises(LlmStageError):
                    load_llm_settings(config_path=config)
            with mock.patch.dict(
                os.environ, {"OPENAI_API_KEY_FILE": str(root / "missing")}, clear=True
            ):
                with self.assertRaises(LlmStageError):
                    load_llm_settings(config_path=config)


if __name__ == "__main__":
    unittest.main()
