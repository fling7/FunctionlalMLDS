#!/usr/bin/env python3
"""Fail-fast checks for the anonymous ACM IUI 2027 review manuscript."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.tex"
BUILD = ROOT / "build"
PDF = BUILD / "main.pdf"
LOG = BUILD / "main.log"

REVIEW_CLASS = r"\documentclass[manuscript,review,anonymous]{acmart}"
PDF_UA_STANDARD = "pdfstandard=UA-2"
MAX_RECOMMENDED_WORDS = 8_000
LENGTH_JUSTIFICATION_THRESHOLD = 10_000
MAX_REVIEWER_BYTES = 10 * 1024 * 1024
MAX_REVIEWER_ANALYZED_PAGES = 15


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def tex_without_commands(text: str) -> str:
    text = re.sub(r"(?m)%.*$", " ", text)
    text = re.sub(r"\\(?:cite|ref|label|url|doi)\w*\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}$^_~&#]", " ", text)
    return text


def source_paths() -> list[Path]:
    """Return every textual source that can contribute review-visible content."""

    files = [MAIN, ROOT / "references.bib"]
    files.extend(sorted((ROOT / "sections").glob("*.tex")))
    files.extend(sorted((ROOT / "figures").glob("*.tex")))
    return files


def review_source_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8") for path in source_paths()
    )


def manuscript_text() -> str:
    """Return the approximate IUI word-count scope.

    IUI excludes references, captions, the GenAI disclosure, and appendices.
    Figure sources are therefore deliberately absent here.
    """

    files = [MAIN]
    files.extend(
        ROOT / "sections" / name
        for name in (
            "01_introduction.tex",
            "02_related_work.tex",
            "03_system.tex",
            "04_method.tex",
            "05_results.tex",
            "06_discussion.tex",
            "07_limitations.tex",
            "08_conclusion.tex",
        )
    )
    return "\n".join(path.read_text(encoding="utf-8") for path in files)


def pending_marker_count(source: str) -> int:
    """Count uses, not the ``\\newcommand`` definition with its ``[1]`` arity."""

    return len(re.findall(r"\\resultpending\{", source))


def inspect_pdf(
    pdf_path: Path,
) -> tuple[int, dict[str, str], bool, str] | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    reader = PdfReader(str(pdf_path))
    metadata = {
        str(key): str(value)
        for key, value in (reader.metadata or {}).items()
        if value is not None
    }
    mark_info = reader.trailer["/Root"].get("/MarkInfo")
    tagged = bool(mark_info and mark_info.get("/Marked"))
    analyzed_text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages[:MAX_REVIEWER_ANALYZED_PAGES]
    )
    return len(reader.pages), metadata, tagged, analyzed_text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help="Permit visible RESULT PENDING markers while developing.",
    )
    args = parser.parse_args()

    failures: list[str] = []
    warnings: list[str] = []
    source = review_source_text()
    word_count_source = manuscript_text()
    main_source = MAIN.read_text(encoding="utf-8")

    if REVIEW_CLASS not in main_source:
        fail(f"main.tex must contain exactly {REVIEW_CLASS}", failures)
    compact_main_source = re.sub(r"\s+", "", main_source)
    if PDF_UA_STANDARD not in compact_main_source:
        fail("main.tex must request PDF/UA-2 in DocumentMetadata.", failures)
    if r"\setcopyright{none}" in main_source:
        fail("Do not suppress ACM review top matter with setcopyright{none}.", failures)
    if "printacmref=false" in main_source:
        fail("Do not suppress ACM reference-format top matter.", failures)

    pending_uses = pending_marker_count(source)
    if pending_uses and not args.allow_pending:
        fail(f"{pending_uses} RESULT PENDING marker(s) remain.", failures)
    elif pending_uses:
        warnings.append(f"{pending_uses} RESULT PENDING marker(s) remain.")

    identity_patterns = {
        "email address": r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "Windows user path": r"(?i)\b[A-Z]:\\Users\\[^\\\s]+",
        "non-anonymous affiliation": r"(?i)\\institution\{(?!Anonymous\b)[^}]+\}",
    }
    for label, pattern in identity_patterns.items():
        if re.search(pattern, source):
            fail(f"Potential {label} in manuscript source.", failures)

    words = re.findall(
        r"\b[\w'-]+\b",
        tex_without_commands(word_count_source),
        re.UNICODE,
    )
    word_count = len(words)
    if word_count > LENGTH_JUSTIFICATION_THRESHOLD:
        fail(
            f"Approximate main-text word count {word_count} exceeds 10,000; "
            "IUI requires a length justification.",
            failures,
        )
    elif word_count > MAX_RECOMMENDED_WORDS:
        warnings.append(
            f"Approximate main-text word count {word_count} exceeds the "
            "recommended 8,000 words."
        )

    citations = set(
        key.strip()
        for group in re.findall(r"\\cite\w*\{([^}]+)\}", source)
        for key in group.split(",")
    )
    bib_text = (ROOT / "references.bib").read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"@\w+\{\s*([^,\s]+)", bib_text))
    missing = sorted(citations - bib_keys)
    if missing:
        fail(f"Undefined bibliography keys: {', '.join(missing)}", failures)

    if not PDF.exists():
        fail("build/main.pdf is missing; run build.ps1 first.", failures)
    else:
        if PDF.stat().st_size > MAX_REVIEWER_BYTES:
            fail("PDF exceeds the reviewer's 10 MB upload limit.", failures)
        pdf_details = inspect_pdf(PDF)
        if pdf_details is None:
            warnings.append("pypdf unavailable; PDF metadata checks skipped.")
        else:
            pages, metadata, tagged, analyzed_text = pdf_details
            if pages > MAX_REVIEWER_ANALYZED_PAGES:
                if "Conclusion" not in analyzed_text:
                    fail(
                        "The Conclusion falls outside the 15 pages analyzed by "
                        "paperreview.ai.",
                        failures,
                    )
                else:
                    warnings.append(
                        f"PDF has {pages} pages; paperreview.ai analyzes only the "
                        "first 15. The complete main argument and Conclusion are "
                        "within that window; later bibliography/appendix pages are "
                        "not reviewer inputs."
                    )
            metadata_text = "\n".join(f"{key}: {value}" for key, value in metadata.items())
            for label, pattern in identity_patterns.items():
                if re.search(pattern, metadata_text):
                    fail(f"Potential {label} in PDF metadata.", failures)
            author = metadata.get("/Author", "").strip()
            if author and "anonymous" not in author.lower():
                fail("PDF /Author metadata is not anonymous.", failures)
            if not tagged:
                fail(
                    "PDF is not tagged; use the pinned LuaLaTeX accessibility build.",
                    failures,
                )

    if LOG.exists():
        log_text = LOG.read_text(encoding="utf-8", errors="replace")
        forbidden_log_patterns = (
            "undefined citations",
            "There were undefined references",
            "Overfull \\hbox",
            "Overfull \\vbox",
            "! LaTeX Error:",
        )
        for pattern in forbidden_log_patterns:
            if pattern.lower() in log_text.lower():
                fail(f"LaTeX log contains: {pattern}", failures)
    else:
        fail("build/main.log is missing; run build.ps1 first.", failures)

    print(f"Approximate main-text words: {word_count}")
    if PDF.exists():
        details = inspect_pdf(PDF)
        pages = details[0] if details is not None else "?"
        print(f"PDF: {pages} pages, {PDF.stat().st_size} bytes")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for failure in failures:
        print(f"ERROR: {failure}")
    if failures:
        return 1
    print("Submission checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
