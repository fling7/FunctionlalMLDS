#!/usr/bin/env python3
"""Minimal, secret-safe client for https://paperreview.ai/.

The upload command refuses drafts that fail the strict local submission check.
Tokens and raw reviews are written only to paths ignored by Git.

The upload flow mirrors the service's public web client: request a presigned
object-store form, upload the PDF directly, then confirm the submission.
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
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent / "paper"
DEFAULT_PDF = PAPER_DIR / "build" / "main.pdf"
DEFAULT_TOKEN = HERE / "paperreview.token"
DEFAULT_REVIEW = HERE / "private" / "review-latest.json"
BASE_URL = "https://paperreview.ai"
MAX_PDF_BYTES = 10 * 1024 * 1024


def request_bytes(
    method: str,
    url_or_path: str,
    *,
    body: bytes | None = None,
    content_type: str | None = None,
    accept: str = "application/json",
    timeout: int = 180,
) -> tuple[int, bytes]:
    headers = {
        "Accept": accept,
        "User-Agent": "FunctionalMLDS-IUI-review-client/1.0",
    }
    if content_type:
        headers["Content-Type"] = content_type
    url = (
        url_or_path
        if url_or_path.startswith(("https://", "http://"))
        else BASE_URL + url_or_path
    )
    request = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            message = str(parsed.get("detail") or parsed.get("message") or "")
        except (json.JSONDecodeError, AttributeError):
            message = detail
        compact = " ".join(message.split())[:500] or "no diagnostic"
        raise RuntimeError(
            f"Reviewer service returned HTTP {exc.code}: {compact}"
        ) from exc


def request_json(
    method: str,
    url_or_path: str,
    *,
    body: bytes | None = None,
    content_type: str | None = None,
) -> tuple[int, dict[str, Any]]:
    status_code, payload = request_bytes(
        method,
        url_or_path,
        body=body,
        content_type=content_type,
    )
    try:
        decoded = json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Reviewer service returned a non-JSON response."
        ) from exc
    if not isinstance(decoded, dict):
        raise RuntimeError("Reviewer service returned an unexpected JSON value.")
    return status_code, decoded


def multipart(
    fields: Mapping[str, object],
    *,
    file_field: str | None = None,
    path: Path | None = None,
) -> tuple[bytes, str]:
    boundary = "----FunctionalMLDS" + secrets.token_hex(16)
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                str(value).encode("utf-8"),
                b"\r\n",
            ]
        )
    if file_field is not None:
        if path is None:
            raise ValueError("A file path is required for a multipart file field.")
        file_content_type = (
            mimetypes.guess_type(path.name)[0] or "application/pdf"
        )
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                (
                    f'Content-Disposition: form-data; name="{file_field}"; '
                    f'filename="{path.name}"\r\n'
                ).encode(),
                f"Content-Type: {file_content_type}\r\n\r\n".encode(),
                path.read_bytes(),
                b"\r\n",
            ]
        )
    chunks.append(f"--{boundary}--\r\n".encode())
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
    if pdf.stat().st_size > MAX_PDF_BYTES:
        raise RuntimeError("PDF exceeds the reviewer's 10 MB upload limit.")
    if args.dry_run:
        print(
            "Local submission checks passed; no reviewer request was made."
        )
        return 0

    request_payload = json.dumps(
        {"filename": pdf.name, "venue": args.venue},
        separators=(",", ":"),
    ).encode("utf-8")
    _, upload_slot = request_json(
        "POST",
        "/api/get-upload-url",
        body=request_payload,
        content_type="application/json",
    )
    if not upload_slot.get("success"):
        raise RuntimeError("Reviewer service did not approve an upload slot.")
    presigned_url = str(upload_slot.get("presigned_url") or "").strip()
    object_key = str(upload_slot.get("s3_key") or "").strip()
    presigned_fields = upload_slot.get("presigned_fields")
    if (
        not presigned_url.startswith("https://")
        or not object_key
        or not isinstance(presigned_fields, dict)
    ):
        raise RuntimeError("Reviewer service returned an invalid upload slot.")

    upload_body, upload_content_type = multipart(
        presigned_fields,
        file_field="file",
        path=pdf,
    )
    request_bytes(
        "POST",
        presigned_url,
        body=upload_body,
        content_type=upload_content_type,
        accept="*/*",
    )

    confirm_body, confirm_content_type = multipart(
        {"s3_key": object_key, "venue": args.venue, "email": email}
    )
    _, response = request_json(
        "POST",
        "/api/confirm-upload",
        body=confirm_body,
        content_type=confirm_content_type,
    )
    if not response.get("success"):
        raise RuntimeError("Reviewer service did not confirm the submission.")
    token = str(
        response.get("token") or response.get("access_token") or ""
    ).strip()
    if not token:
        raise RuntimeError("Upload succeeded without a recognizable access token.")
    write_private(args.token_file.resolve(), token + "\n")
    print(f"Upload confirmed; token saved privately at {args.token_file.resolve()}.")
    return 0


def status(args: argparse.Namespace) -> int:
    token = read_token(args.token_file.resolve())
    status_code, response = request_json("GET", f"/api/review/{token}")
    if status_code == 202:
        safe = {"status": "processing"}
    else:
        safe = {
            "status": "complete",
            "title": response.get("title"),
            "venue": response.get("venue"),
        }
    print(json.dumps(safe, indent=2, ensure_ascii=False))
    return 0


def fetch(args: argparse.Namespace) -> int:
    token = read_token(args.token_file.resolve())
    status_code, response = request_json("GET", f"/api/review/{token}")
    if status_code == 202:
        raise RuntimeError("Review is still processing.")
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
    upload_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run strict local checks without contacting the reviewer.",
    )
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
