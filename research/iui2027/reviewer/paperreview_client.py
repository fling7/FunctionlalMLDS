#!/usr/bin/env python3
"""Minimal, secret-safe client for https://paperreview.ai/.

The upload command refuses drafts that fail the strict local submission check.
Tokens and raw reviews are written only to paths ignored by Git.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import secrets
import stat
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent / "paper"
DEFAULT_PDF = PAPER_DIR / "build" / "main.pdf"
DEFAULT_TOKEN = HERE / "paperreview.token"
DEFAULT_REVIEW = HERE / "private" / "review-latest.json"
BASE_URL = "https://paperreview.ai"


def api_json(
    method: str,
    path: str,
    *,
    body: bytes | None = None,
    content_type: str | None = None,
) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    if content_type:
        headers["Content-Type"] = content_type
    request = urllib.request.Request(
        BASE_URL + path,
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Reviewer API returned HTTP {exc.code}: {detail}") from exc
    return json.loads(payload.decode("utf-8"))


def multipart(fields: dict[str, str], file_field: str, path: Path) -> tuple[bytes, str]:
    boundary = "----FunctionalMLDS" + secrets.token_hex(16)
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )
    content_type = mimetypes.guess_type(path.name)[0] or "application/pdf"
    chunks.extend(
        [
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="{file_field}"; '
                f'filename="{path.name}"\r\n'
            ).encode(),
            f"Content-Type: {content_type}\r\n\r\n".encode(),
            path.read_bytes(),
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def strict_submission_check() -> None:
    command = [sys.executable, str(PAPER_DIR / "check_submission.py")]
    result = subprocess.run(command, cwd=PAPER_DIR, check=False)
    if result.returncode:
        raise RuntimeError("Strict submission checks failed; upload refused.")


def write_private(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    try:
        path.chmod(stat.S_IREAD | stat.S_IWRITE)
    except OSError:
        pass


def read_token(path: Path) -> str:
    token = path.read_text(encoding="utf-8").strip()
    if not token:
        raise RuntimeError(f"Token file is empty: {path}")
    return token


def upload(args: argparse.Namespace) -> int:
    email = os.environ.get("PAPERREVIEW_EMAIL", "").strip()
    if not email:
        raise RuntimeError("Set PAPERREVIEW_EMAIL for the authorized upload address.")
    pdf = args.pdf.resolve()
    if not pdf.is_file():
        raise RuntimeError(f"PDF not found: {pdf}")
    strict_submission_check()
    body, content_type = multipart(
        {"venue": args.venue, "email": email},
        "pdf",
        pdf,
    )
    response = api_json("POST", "/api/upload", body=body, content_type=content_type)
    token = str(response.get("token") or response.get("access_token") or "").strip()
    if not token:
        raise RuntimeError("Upload succeeded without a recognizable access token.")
    write_private(args.token_file.resolve(), token + "\n")
    print(f"Upload confirmed; token saved privately at {args.token_file.resolve()}.")
    return 0


def status(args: argparse.Namespace) -> int:
    token = read_token(args.token_file.resolve())
    response = api_json("GET", f"/api/status/{token}")
    safe = {
        key: value
        for key, value in response.items()
        if "token" not in key.lower() and "email" not in key.lower()
    }
    print(json.dumps(safe, indent=2, ensure_ascii=False))
    return 0


def fetch(args: argparse.Namespace) -> int:
    token = read_token(args.token_file.resolve())
    response = api_json("GET", f"/api/review/{token}")
    write_private(
        args.output.resolve(),
        json.dumps(response, indent=2, ensure_ascii=False) + "\n",
    )
    print(f"Raw review saved privately at {args.output.resolve()}.")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    upload_parser = commands.add_parser("upload")
    upload_parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    upload_parser.add_argument("--venue", default="ACM IUI 2027")
    upload_parser.add_argument("--token-file", type=Path, default=DEFAULT_TOKEN)
    upload_parser.set_defaults(handler=upload)

    status_parser = commands.add_parser("status")
    status_parser.add_argument("--token-file", type=Path, default=DEFAULT_TOKEN)
    status_parser.set_defaults(handler=status)

    fetch_parser = commands.add_parser("fetch")
    fetch_parser.add_argument("--token-file", type=Path, default=DEFAULT_TOKEN)
    fetch_parser.add_argument("--output", type=Path, default=DEFAULT_REVIEW)
    fetch_parser.set_defaults(handler=fetch)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
