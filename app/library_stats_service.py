"""Physical-library availability helpers used by Dashboard and exports."""
from __future__ import annotations

from pathlib import Path
from datetime import date, datetime
from typing import Any, Callable, Iterable

MEDIA_EXTENSIONS = {".mp4", ".mkv", ".webm", ".m4v", ".mov", ".avi", ".mp3", ".m4a", ".aac", ".opus", ".wav"}


def find_media_in_folder(folder: Path) -> Path | None:
    try:
        for path in folder.rglob("*"):
            if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS and path.stat().st_size > 0:
                return path
    except Exception:
        return None
    return None


def physical_media_available(local_folder: Any, local_video: Any, downloaded_flag: Any = 0, finder: Callable[[Path], Any] | None = None) -> bool:
    """Truthful availability: a DB downloaded flag alone is never enough."""
    try:
        media = Path(str(local_video or "")) if local_video else None
        if media and media.is_file() and media.stat().st_size > 0:
            return True
    except Exception:
        pass
    try:
        folder = Path(str(local_folder or "")) if local_folder else None
        if not folder or not folder.is_dir():
            return False
        if finder is not None:
            found = finder(folder)
            return bool(found and Path(found).is_file() and Path(found).stat().st_size > 0)
        return find_media_in_folder(folder) is not None
    except Exception:
        return False


def available_download_count(rows: Iterable[tuple[Any, Any, Any]]) -> int:
    return sum(1 for folder, video, downloaded in rows if physical_media_available(folder, video, downloaded))


def _download_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except Exception:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except Exception:
            continue
    return None


def physical_downloaded_today_count(
    rows: Iterable[tuple[Any, Any, Any, Any]],
    today: date | None = None,
    finder: Callable[[Path], Any] | None = None,
) -> int:
    """Count physically present media whose canonical ``downloaded_at`` is today.

    Dashboard's *Completed today* metric is a video metric, not a generic job
    metric.  Maintenance/rebuild jobs must never increase it.
    """
    target = today or datetime.now().date()
    count = 0
    for folder, video, downloaded, downloaded_at in rows or []:
        if _download_date(downloaded_at) != target:
            continue
        if physical_media_available(folder, video, downloaded, finder=finder):
            count += 1
    return count
