"""Unified current-failure registry for the native VideoHoarder UI.

The old UI exposed video failures and queue-job failures through different data
sources, so dashboard counts and the Failure / Cleanup page disagreed.  This
module normalizes both sources into one list and provides safe dismissal of
terminal job failures while archiving their diagnostic run log.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import time
from typing import Any, Iterable, MutableMapping


TERMINAL_FAILURE_STATUSES = {"FAILED", "WARN"}


def merge_current_failures(video_rows: Iterable[dict[str, Any]], job_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for row in video_rows or []:
        item = dict(row)
        video_id = str(item.get("video_id") or "").strip()
        item.setdefault("failure_key", f"video:{video_id}" if video_id else "")
        item.setdefault("failure_kind", "Video")
        item["display_name"] = (
            item.get("clean_title") or item.get("original_title") or video_id or "Unknown video"
        )
        item["reason"] = item.get("failure_reason") or item.get("last_error") or "No reason captured"
        item["sort_time"] = str(item.get("downloaded_at") or "")
        merged.append(item)

    seen_jobs: set[str] = set()
    for row in job_rows or []:
        item = dict(row)
        status = str(item.get("status") or "").upper()
        if status == "CANCELLED":
            continue
        if status not in TERMINAL_FAILURE_STATUSES and not item.get("has_error"):
            continue
        job_id = str(item.get("job_id") or "").strip()
        if not job_id or job_id in seen_jobs:
            continue
        seen_jobs.add(job_id)
        merged.append({
            **item,
            "failure_key": f"job:{job_id}",
            "failure_kind": "Queue job",
            "display_name": item.get("display_title") or item.get("current_file") or item.get("label") or job_id,
            "channel": item.get("channel") or "",
            "reason": item.get("error_summary") or item.get("message") or f"Queue job {status.lower()}",
            "sort_time": str(item.get("finished_at") or item.get("created_at") or ""),
        })

    merged.sort(key=lambda row: str(row.get("sort_time") or ""), reverse=True)
    return merged


def clear_terminal_job_failure(
    job_id: str,
    jobs: MutableMapping[str, dict[str, Any]],
    tasks: MutableMapping[str, Any],
    lock: Any,
    log_path: Path,
    archive_dir: Path,
) -> dict[str, Any]:
    job_id = str(job_id or "").strip()
    if not job_id:
        return {"ok": False, "message": "Missing job ID."}

    with lock:
        existing = jobs.get(job_id)
        status = str((existing or {}).get("status") or "").upper()
        if existing and status in {"RUNNING", "QUEUED"}:
            return {"ok": False, "message": f"Job {job_id} is still {status.lower()} and cannot be deleted."}
        jobs.pop(job_id, None)
        tasks.pop(job_id, None)

    archived = ""
    path = Path(log_path)
    if path.exists():
        archive_dir = Path(archive_dir)
        archive_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        target = archive_dir / f"cleared_{stamp}_{path.name}"
        try:
            shutil.move(str(path), str(target))
            archived = str(target)
        except Exception as exc:
            return {
                "ok": False,
                "message": f"Removed job from current queue state but could not archive its run log: {type(exc).__name__}: {exc}",
            }

    return {
        "ok": True,
        "message": f"Deleted current failure entry for queue job {job_id}.",
        "archived_log": archived,
    }
