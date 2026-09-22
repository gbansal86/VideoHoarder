"""Presentation metadata helpers for VideoHoarder's managed download queue."""

from __future__ import annotations

import re
import urllib.parse
from pathlib import Path
from typing import Any

from .youtube_url import youtube_video_id



def initial_job_metadata(
    url: str,
    job_type: str,
    batch_id: str = "",
    batch_index: int = 1,
    batch_total: int = 1,
) -> dict[str, Any]:
    text = str(url or "").strip()
    video_id = youtube_video_id(text)
    parsed = urllib.parse.urlparse(text)
    fallback_name = video_id or Path(parsed.path.rstrip("/")).name or parsed.netloc or "Video"
    thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg" if video_id else ""
    return {
        "source_url": text,
        "display_name": fallback_name,
        "job_type": str(job_type or "Download"),
        "video_id": video_id,
        "thumbnail_url": thumbnail_url,
        "batch_id": str(batch_id or ""),
        "batch_index": int(batch_index or 1),
        "batch_total": max(1, int(batch_total or 1)),
    }


def metadata_job_fields(
    title: str = "",
    thumbnail_url: str = "",
    thumbnail_path: str = "",
    video_id: str = "",
    source_url: str = "",
) -> dict[str, str]:
    return {
        "display_name": str(title or video_id or "Video").strip(),
        "thumbnail_url": str(thumbnail_url or "").strip(),
        "thumbnail_path": str(thumbnail_path or "").strip(),
        "video_id": str(video_id or "").strip(),
        "source_url": str(source_url or "").strip(),
    }


def display_name(job: dict[str, Any]) -> str:
    value = str(job.get("display_name") or "").strip()
    if value:
        return Path(value).name or value
    current = str(job.get("current_file") or job.get("current") or "").strip()
    # Use transient stage/current-file text only until metadata supplies a stable title/file.
    if current and not current.startswith(("http://", "https://")):
        return Path(current).name or current
    url = str(job.get("source_url") or "").strip()
    if url:
        parsed = urllib.parse.urlparse(url)
        return Path(parsed.path.rstrip("/")).name or parsed.netloc or url
    return str(job.get("label") or "Background job")


def job_type(job: dict[str, Any]) -> str:
    explicit = str(job.get("job_type") or "").strip()
    if explicit:
        return explicit
    label = str(job.get("label") or "Download")
    label = re.sub(r"\s+\d+/\d+$", "", label).strip()
    return label


def latest_batch_summary(jobs: list[dict[str, Any]]) -> dict[str, int | str]:
    batched = [job for job in jobs if str(job.get("batch_id") or "")]
    if not batched:
        return {"batch_id": "", "total": 0, "done": 0, "left": 0, "running": 0, "queued": 0, "failed": 0}
    latest = max(batched, key=lambda job: float(job.get("created_at") or 0))
    batch_id = str(latest.get("batch_id") or "")
    rows = [job for job in batched if str(job.get("batch_id") or "") == batch_id]
    statuses = [str(job.get("status") or "").upper() for job in rows]
    done = sum(status in {"SUCCESS", "WARN", "FAILED", "CANCELLED"} for status in statuses)
    return {
        "batch_id": batch_id,
        "total": len(rows),
        "done": done,
        "left": max(0, len(rows) - done),
        "running": statuses.count("RUNNING"),
        "queued": statuses.count("QUEUED"),
        "failed": statuses.count("FAILED"),
    }


def queue_wait_message(
    job: dict[str, Any],
    jobs: list[dict[str, Any]],
    queue_state: dict[str, Any] | None = None,
) -> str:
    """Explain why a queued job is waiting using actual queue position/state."""
    state = dict(queue_state or {})
    if state.get("paused"):
        return "Waiting because the queue is paused. Click Resume queue below."
    if str(job.get("status") or "").upper() != "QUEUED":
        return str(job.get("message") or "")
    queued = sorted(
        [row for row in (jobs or []) if str(row.get("status") or "").upper() == "QUEUED"],
        key=lambda row: float(row.get("created_at") or 0),
    )
    job_id = str(job.get("job_id") or "")
    position = next((i for i, row in enumerate(queued) if str(row.get("job_id") or "") == job_id), 0)
    running = int(state.get("running") or 0)
    if running:
        if position:
            return f"Waiting behind the active job and {position} earlier queued job(s)."
        return "Waiting behind the active running job."
    if position:
        return f"Waiting behind {position} earlier queued job(s)."
    return "Waiting for the queue worker to start."


def _int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return default


def _percent_value(value: Any) -> int:
    if isinstance(value, (int, float)):
        return max(0, min(100, int(float(value))))
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", str(value or ""))
    return max(0, min(100, int(float(match.group(1))))) if match else 0


def overall_progress_percent(job: dict[str, Any], live: dict[str, Any] | None = None) -> int:
    """Return truthful overall progress from separate batch/transfer fields."""
    live = live or {}
    status = str(job.get("status") or "").upper()
    total = _int_value(job.get("batch_total") if job.get("batch_total") not in (None, "") else job.get("total"))
    processed = _int_value(job.get("batch_processed") if job.get("batch_processed") not in (None, "") else job.get("processed"))
    transfer_raw = job.get("transfer_percent")
    transfer = _percent_value(transfer_raw if transfer_raw not in (None, "") else (live.get("current_percent") if status == "RUNNING" else 0))
    if total:
        completed = float(max(0, min(processed, total)))
        if status in {"RUNNING", "CANCELLING"} and completed < total and transfer > 0:
            completed += transfer / 100.0
        return max(0, min(100, round(completed * 100 / total)))
    if status in {"RUNNING", "CANCELLING"}:
        return transfer
    if status in {"SUCCESS", "WARN"}:
        return 100
    return 0
