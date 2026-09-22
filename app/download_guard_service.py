"""Duplicate-download guard helpers.

This module keeps duplicate/re-download decisions out of the large app.py file.
It is intentionally pure so both native and web download surfaces can use the
same rule: an already-present library video, a previously deleted video, or a
matching active/recent queue job requires explicit user confirmation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable

from .youtube_url import youtube_video_id



def media_present(downloaded: Any, local_video: Any, local_folder: Any, media_finder: Callable[[Path], Any] | None = None) -> bool:
    """Return True only when downloaded media is physically present."""
    try:
        path = Path(str(local_video or "")) if local_video else None
        if path and path.is_file() and path.stat().st_size > 0:
            return True
    except Exception:
        pass
    if not bool(int(downloaded or 0)):
        return False
    try:
        folder = Path(str(local_folder or "")) if local_folder else None
        if folder and folder.is_dir() and media_finder is not None:
            found = media_finder(folder)
            return bool(found and Path(found).is_file() and Path(found).stat().st_size > 0)
    except Exception:
        pass
    return False


def queue_duplicate_matches(urls: Iterable[str], jobs: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    """Find URLs/YouTube IDs already represented in the managed queue/history."""
    wanted = []
    for raw in urls or []:
        url = str(raw or "").strip()
        if not url:
            continue
        wanted.append((url, youtube_video_id(url)))
    out: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for job in jobs or []:
        status = str(job.get("status") or "").upper()
        if status not in {"QUEUED", "RUNNING", "SUCCESS", "WARN"}:
            continue
        job_url = str(job.get("source_url") or "").strip()
        job_vid = str(job.get("video_id") or youtube_video_id(job_url)).strip()
        for url, vid in wanted:
            same = bool(vid and job_vid and vid == job_vid) or bool(url and job_url and url == job_url)
            if not same:
                continue
            key = (str(job.get("job_id") or ""), vid or url)
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "video_id": vid or job_vid,
                "url": url,
                "status": "ALREADY_IN_QUEUE" if status in {"QUEUED", "RUNNING"} else "RECENTLY_DOWNLOADED_JOB",
                "title": str(job.get("display_name") or job.get("label") or ""),
                "channel": "",
                "job_id": str(job.get("job_id") or ""),
                "job_status": status,
            })
    return out


def confirmation_message(items: Iterable[dict[str, Any]]) -> str:
    rows = list(items or [])
    if not rows:
        return ""
    lines = ["VideoHoarder found video(s) that may already be downloaded or queued:", ""]
    labels = {
        "ALREADY_ACTIVE": "Already in library",
        "PREVIOUSLY_DELETED": "Previously deleted",
        "ALREADY_IN_QUEUE": "Already queued/running",
        "RECENTLY_DOWNLOADED_JOB": "Recent successful job",
    }
    for item in rows[:20]:
        title = str(item.get("title") or item.get("video_id") or item.get("url") or "Video")
        vid = str(item.get("video_id") or "")
        status = labels.get(str(item.get("status") or ""), str(item.get("status") or "Duplicate"))
        suffix = f" [{vid}]" if vid else ""
        lines.append(f"• {title}{suffix} — {status}")
    if len(rows) > 20:
        lines.append(f"• …and {len(rows) - 20} more")
    lines += ["", "Download/queue these video(s) again?"]
    return "\n".join(lines)


def redownload_history_report(
    urls: Iterable[str],
    db_connect: Callable[[], Any],
    history_loader: Callable[[], dict[str, Any]],
    migration_func: Callable[[], Any] | None = None,
    media_finder: Callable[[Path], Any] | None = None,
) -> dict[str, Any]:
    """Build the library/deleted-history duplicate report for download surfaces."""
    if migration_func is not None:
        try:
            migration_func()
        except Exception:
            pass
    try:
        history = dict(history_loader() or {})
    except Exception:
        history = {}
    items: list[dict[str, Any]] = []
    con = db_connect()
    try:
        for url in urls or []:
            vid = youtube_video_id(str(url or ""))
            if not vid:
                continue
            row = con.execute(
                "SELECT original_title,channel,COALESCE(current_present,1),COALESCE(downloaded,0),COALESCE(local_video,''),COALESCE(local_folder,'') FROM videos WHERE video_id=?",
                (vid,),
            ).fetchone()
            if row and int(row[2] or 0) and media_present(row[3], row[4], row[5], media_finder):
                items.append({
                    "video_id": vid, "url": url, "status": "ALREADY_ACTIVE",
                    "title": row[0] or "", "channel": row[1] or "", "deleted_at": "",
                })
                continue
            old = history.get(vid)
            if old:
                items.append({
                    "video_id": vid, "url": url, "status": "PREVIOUSLY_DELETED",
                    "title": str(old.get("title") or ""), "channel": str(old.get("channel") or ""),
                    "deleted_at": str(old.get("deleted_at") or ""),
                })
    finally:
        con.close()
    return {"ok": True, "items": items, "requires_confirmation": bool(items)}
