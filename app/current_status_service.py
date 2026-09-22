"""Authoritative user-facing current-status payloads for VideoHoarder.

The dashboard, web Failure page, and ``/api/download-status`` should all count
the same unified current-failure rows.  This module deliberately has no HTTP,
SQLite, or Qt dependency so ``app.py`` and native UI code can stay as thin
wiring layers.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


def failure_reason_bucket(row: dict[str, Any]) -> str:
    reason = str(
        row.get("reason")
        or row.get("failure_reason")
        or row.get("last_error")
        or row.get("error_summary")
        or row.get("message")
        or "Unknown"
    ).lower()
    if "429" in reason:
        return "YouTube / subtitle 429 rate limit"
    if "403" in reason:
        return "YouTube 403 forbidden"
    if "transcript" in reason and any(word in reason for word in ("missing", "unavailable", "empty")):
        return "Transcript unavailable"
    if "subtitle" in reason or "vtt" in reason or "srt" in reason:
        return "Subtitle/VTT problem"
    if "ffmpeg" in reason:
        return "FFmpeg/media merge"
    if "timeout" in reason or "timed out" in reason:
        return "Timeout"
    if "report" in reason or "html" in reason:
        return "HTML/report problem"
    if "path" in reason or "filename" in reason:
        return "Path/filename problem"
    if not reason.strip() or reason == "unknown":
        return "Unknown / no captured reason"
    return "Other"


def failure_summary(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(failure_reason_bucket(row) for row in rows or [])
    return [{"reason": reason, "count": count} for reason, count in counts.most_common()]


def download_status_payload(stats: dict[str, Any], failures: list[dict[str, Any]]) -> dict[str, Any]:
    fixed_stats = dict(stats or {})
    fixed_stats["failed"] = len(failures or [])
    return {
        "ok": True,
        "stats": fixed_stats,
        "summary": failure_summary(failures or []),
        "failures": failures or [],
    }
