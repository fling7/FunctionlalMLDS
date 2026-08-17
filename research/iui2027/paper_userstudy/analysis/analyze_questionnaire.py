#!/usr/bin/env python3
"""Reproduce the descriptive questionnaire results for Study U.

Usage:
    python analyze_questionnaire.py path/to/questionnaire-export.json

The handoff subset is intentionally strict: only sessions with
q5_handoff_observed == "yes" contribute to q6/q7 summaries. Numeric q6/q7
values attached to "no" or "unsure" responses are excluded.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


def numeric_values(responses: list[dict[str, Any]], key: str) -> list[float]:
    values: list[float] = []
    for response in responses:
        value = response.get("answers", {}).get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            values.append(float(value))
    return values


def quartiles(values: Iterable[float]) -> tuple[float, float, float]:
    data = sorted(values)
    if not data:
        raise ValueError("Cannot summarize an empty sequence.")
    median = statistics.median(data)
    if len(data) == 1:
        return data[0], median, data[0]
    q1, _, q3 = statistics.quantiles(data, n=4, method="inclusive")
    return q1, median, q3


def summarize_scale(values: list[float]) -> dict[str, float | int]:
    q1, median, q3 = quartiles(values)
    return {
        "n": len(values),
        "mean": sum(values) / len(values),
        "median": median,
        "q1": q1,
        "q3": q3,
        "positive_4_or_5": sum(value >= 4 for value in values),
    }


def wilson_interval(
    successes: int,
    n: int,
    z: float = 1.959963984540054,
) -> tuple[float, float]:
    if n <= 0:
        raise ValueError("n must be positive.")
    p = successes / n
    denominator = 1 + (z * z) / n
    center = (p + (z * z) / (2 * n)) / denominator
    margin = (
        z
        * math.sqrt((p * (1 - p) / n) + (z * z) / (4 * n * n))
        / denominator
    )
    return center - margin, center + margin


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("export", type=Path, help="Questionnaire JSON export")
    args = parser.parse_args()

    payload = json.loads(args.export.read_text(encoding="utf-8"))
    completed = [
        response
        for response in payload.get("responses", [])
        if response.get("status") == "completed"
    ]

    # Keep the latest record if an export ever contains a duplicate session ID.
    by_session: dict[str, dict[str, Any]] = {}
    for response in completed:
        session_id = response.get("sessionId")
        if not session_id:
            continue
        current = by_session.get(session_id)
        if current is None or response.get("updatedAt", "") >= current.get(
            "updatedAt", ""
        ):
            by_session[session_id] = response
    responses = list(by_session.values())

    handoff_yes = [
        response
        for response in responses
        if response.get("answers", {}).get("q5_handoff_observed") == "yes"
    ]
    error_exposed = [
        response
        for response in responses
        if isinstance(
            response.get("answers", {}).get("q9_error_explanation"),
            (int, float),
        )
        and not isinstance(
            response.get("answers", {}).get("q9_error_explanation"), bool
        )
    ]

    intended = sum(
        response.get("answers", {}).get("q10_agent_selection_model")
        == "object_and_topic"
        for response in responses
    )
    lower, upper = wilson_interval(intended, len(responses))

    result = {
        "exported_at": payload.get("exportedAt"),
        "completed_unique_sessions": len(responses),
        "devices": Counter(
            response.get("answers", {}).get("q1_device") for response in responses
        ),
        "handoff_observed": Counter(
            response.get("answers", {}).get("q5_handoff_observed")
            for response in responses
        ),
        "handoff_filter": 'q5_handoff_observed == "yes"',
        "q6_handoff_understandability": summarize_scale(
            numeric_values(handoff_yes, "q6_handoff_understandability")
        ),
        "q7_final_agent_clarity": summarize_scale(
            numeric_values(handoff_yes, "q7_final_agent_clarity")
        ),
        "q9_error_explanation": summarize_scale(
            numeric_values(error_exposed, "q9_error_explanation")
        ),
        "q10_intended_model": {
            "successes": intended,
            "n": len(responses),
            "proportion": intended / len(responses),
            "wilson_95": [lower, upper],
        },
    }

    print(json.dumps(result, indent=2, ensure_ascii=False, default=dict))


if __name__ == "__main__":
    main()
