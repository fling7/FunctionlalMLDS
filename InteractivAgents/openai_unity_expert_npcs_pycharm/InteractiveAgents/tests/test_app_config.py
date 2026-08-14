from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from backend import app


class AppConfigEnvironmentTests(unittest.TestCase):
    def write_config(self, root: Path, **overrides: object) -> Path:
        payload = {
            "openai_api_key": "config-key",
            "server_host": "127.0.0.1",
            "server_port": 8787,
        }
        payload.update(overrides)
        path = root / "config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_file_secret_and_server_overrides_do_not_rewrite_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = self.write_config(root, openai_api_key="old-config-key")
            before = config_path.read_bytes()
            secret_path = root / "openai-key"
            secret_path.write_text("file-key\n", encoding="utf-8")
            env = {
                "OPENAI_API_KEY_FILE": str(secret_path),
                "SERVER_HOST": "0.0.0.0",
                "SERVER_PORT": "9876",
            }
            with mock.patch.object(app, "_project_root", return_value=root), mock.patch.dict(
                os.environ, env, clear=True
            ):
                config = app.load_config()

            self.assertEqual(config.openai_api_key, "file-key")
            self.assertEqual(config.server_host, "0.0.0.0")
            self.assertEqual(config.server_port, 9876)
            self.assertEqual(config_path.read_bytes(), before)

    def test_direct_secret_wins_without_rewriting_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = self.write_config(root)
            before = config_path.read_bytes()
            with mock.patch.object(app, "_project_root", return_value=root), mock.patch.dict(
                os.environ, {"OPENAI_API_KEY": "environment-key"}, clear=True
            ):
                config = app.load_config()
            self.assertEqual(config.openai_api_key, "environment-key")
            self.assertEqual(config_path.read_bytes(), before)

    def test_conflicting_secret_sources_and_invalid_ports_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_config(root)
            with mock.patch.object(app, "_project_root", return_value=root), mock.patch.dict(
                os.environ,
                {"OPENAI_API_KEY": "one", "OPENAI_API_KEY_FILE": "two"},
                clear=True,
            ):
                with self.assertRaises(ValueError):
                    app.load_config()

            for value in ("nope", "0", "65536"):
                with self.subTest(value=value), mock.patch.object(
                    app, "_project_root", return_value=root
                ), mock.patch.dict(os.environ, {"SERVER_PORT": value}, clear=True):
                    with self.assertRaises(ValueError):
                        app.load_config()


if __name__ == "__main__":
    unittest.main()
