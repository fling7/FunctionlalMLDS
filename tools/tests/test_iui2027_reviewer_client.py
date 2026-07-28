from __future__ import annotations

import argparse
import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from research.iui2027.reviewer import paperreview_client


class PaperReviewClientTests(unittest.TestCase):
    def test_multipart_places_presigned_fields_before_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pdf = Path(temporary) / "paper.pdf"
            pdf.write_bytes(b"%PDF-1.7\n")
            body, content_type = paperreview_client.multipart(
                {"key": "object-key", "policy": "policy-value"},
                file_field="file",
                path=pdf,
            )

        self.assertTrue(content_type.startswith("multipart/form-data; boundary="))
        self.assertLess(body.index(b'name="key"'), body.index(b'name="file"'))
        self.assertLess(body.index(b'name="policy"'), body.index(b'name="file"'))
        boundary = content_type.split("boundary=", 1)[1].encode("ascii")
        self.assertTrue(body.endswith(b"--" + boundary + b"--\r\n"))

    def test_upload_uses_presigned_three_step_flow_and_saves_token(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pdf = root / "paper.pdf"
            pdf.write_bytes(b"%PDF-1.7\n")
            token_file = root / "review.token"
            args = argparse.Namespace(
                pdf=pdf,
                venue="ACM IUI 2027",
                token_file=token_file,
                dry_run=False,
            )
            calls: list[tuple[str, str]] = []

            def fake_json(
                method: str,
                url_or_path: str,
                **_: object,
            ) -> tuple[int, dict[str, object]]:
                calls.append((method, url_or_path))
                if url_or_path == "/api/get-upload-url":
                    return (
                        200,
                        {
                            "success": True,
                            "presigned_url": "https://objects.example/upload",
                            "s3_key": "private/object",
                            "presigned_fields": {
                                "key": "private/object",
                                "policy": "signed-policy",
                            },
                        },
                    )
                self.assertEqual(url_or_path, "/api/confirm-upload")
                return 200, {"success": True, "token": "private-review-token"}

            def fake_bytes(
                method: str,
                url_or_path: str,
                **_: object,
            ) -> tuple[int, bytes]:
                calls.append((method, url_or_path))
                return 204, b""

            with (
                mock.patch.dict(
                    os.environ,
                    {"PAPERREVIEW_EMAIL": "authorized@example.invalid"},
                    clear=False,
                ),
                mock.patch.object(
                    paperreview_client,
                    "strict_submission_check",
                ),
                mock.patch.object(
                    paperreview_client,
                    "request_json",
                    side_effect=fake_json,
                ),
                mock.patch.object(
                    paperreview_client,
                    "request_bytes",
                    side_effect=fake_bytes,
                ),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                result = paperreview_client.upload(args)

            self.assertEqual(result, 0)
            self.assertEqual(token_file.read_text(encoding="utf-8").strip(), "private-review-token")
            self.assertEqual(
                calls,
                [
                    ("POST", "/api/get-upload-url"),
                    ("POST", "https://objects.example/upload"),
                    ("POST", "/api/confirm-upload"),
                ],
            )

    def test_status_does_not_print_review_content_or_token(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            token_file = Path(temporary) / "review.token"
            token_file.write_text("private-review-token\n", encoding="utf-8")
            args = argparse.Namespace(token_file=token_file)
            output = io.StringIO()
            with (
                mock.patch.object(
                    paperreview_client,
                    "request_json",
                    return_value=(
                        200,
                        {
                            "title": "Anonymous paper",
                            "venue": "ACM IUI 2027",
                            "content": "private full review",
                            "token": "private-review-token",
                        },
                    ),
                ),
                contextlib.redirect_stdout(output),
            ):
                result = paperreview_client.status(args)

        rendered = output.getvalue()
        self.assertEqual(result, 0)
        self.assertIn('"status": "complete"', rendered)
        self.assertNotIn("private full review", rendered)
        self.assertNotIn("private-review-token", rendered)


if __name__ == "__main__":
    unittest.main()
