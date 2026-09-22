"""Live Library-browser merge/filter/sort logic.

Phase-5 search documents are useful for rich search text, but mutable state such
as downloaded_at, local paths and failure/personal-state flags must come from
SQLite on every browser request.  This module overlays those authoritative
values before filtering and sorting.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


LIVE_FIELDS = {
    "url",
    "original_title",
    "clean_title",
    "channel",
    "category",
    "subcategory",
    "source_category",
    "youtube_category_name",
    "downloaded_at",
    "local_video",
    "final_status",
    "favorite",
    "watched",
    "archived",
    "thumbnail_url",
}


def merge_index_with_live_rows(index_docs: Iterable[dict[str, Any]], live_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    docs_by_id: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for doc in index_docs or []:
        video_id = str(doc.get("video_id") or "").strip()
        if not video_id:
            continue
        docs_by_id[video_id] = dict(doc)
        order.append(video_id)

    for row in live_rows or []:
        video_id = str(row.get("video_id") or "").strip()
        if not video_id:
            continue
        doc = docs_by_id.get(video_id, {"video_id": video_id})
        for field in LIVE_FIELDS:
            if field in row:
                doc[field] = row.get(field)
        doc["title"] = row.get("clean_title") or row.get("original_title") or doc.get("title") or video_id
        doc["original_title"] = row.get("original_title") or doc.get("original_title") or ""
        doc["channel"] = row.get("channel") or doc.get("channel") or ""
        doc["category"] = row.get("category") or doc.get("category") or "Other"
        doc["subcategory"] = row.get("subcategory") or doc.get("subcategory") or "General"
        doc["source_category"] = row.get("source_category") or row.get("youtube_category_name") or doc.get("source_category") or ""
        docs_by_id[video_id] = doc
        if video_id not in order:
            order.append(video_id)

    return [docs_by_id[video_id] for video_id in order if video_id in docs_by_id]


def browser_rows(
    docs: Iterable[dict[str, Any]],
    query: str = "",
    filter_name: str = "all",
    sort_by: str = "default",
    limit: int = 300,
    path_exists=lambda value: Path(str(value)).exists(),
) -> list[dict[str, Any]]:
    q = str(query or "").strip().lower()
    filter_key = str(filter_name or "all").lower()
    now = datetime.now()
    output: list[dict[str, Any]] = []

    for doc in docs or []:
        if int(doc.get("archived") or 0):
            continue
        haystack = " ".join(
            str(doc.get(key) or "")
            for key in ("video_id", "title", "original_title", "channel", "category", "subcategory", "search_text")
        ).lower()
        if q and q not in haystack:
            continue

        local_video = str(doc.get("local_video") or "")
        media = bool(local_video and path_exists(local_video))
        if filter_key == "downloaded" and not media:
            continue
        if filter_key == "failed" and str(doc.get("final_status") or "").upper() != "FAIL":
            continue
        if filter_key == "favorites" and not int(doc.get("favorite") or 0):
            continue
        if filter_key == "unwatched" and int(doc.get("watched") or 0):
            continue
        if filter_key == "latest":
            try:
                downloaded = datetime.strptime(str(doc.get("downloaded_at") or "")[:19], "%Y-%m-%d %H:%M:%S")
                if (now - downloaded).days > 7:
                    continue
            except Exception:
                continue

        output.append(
            {
                "video_id": str(doc.get("video_id") or ""),
                "title": doc.get("title") or doc.get("original_title") or doc.get("video_id"),
                "channel": doc.get("channel") or "",
                "category": doc.get("category") or "Other",
                "subcategory": doc.get("subcategory") or "General",
                "source_category": doc.get("source_category") or doc.get("youtube_category_name") or "",
                "downloaded_at": doc.get("downloaded_at") or "",
                "favorite": int(doc.get("favorite") or 0),
                "watched": int(doc.get("watched") or 0),
                "status": doc.get("final_status") or "",
                "has_media": media,
                "local_video": local_video,
                "thumbnail_url": doc.get("thumbnail_url") or "",
                "url": doc.get("url") or "",
            }
        )

    sort_key = str(sort_by or ("downloaded_desc" if filter_key == "latest" else "default")).lower()
    if sort_key in {"downloaded_desc", "latest", "newest"}:
        output.sort(key=lambda row: str(row.get("downloaded_at") or ""), reverse=True)
    elif sort_key in {"downloaded_asc", "oldest"}:
        output.sort(key=lambda row: str(row.get("downloaded_at") or "9999"))
    elif sort_key == "title":
        output.sort(key=lambda row: str(row.get("title") or "").lower())
    elif sort_key == "channel":
        output.sort(key=lambda row: (str(row.get("channel") or "").lower(), str(row.get("title") or "").lower()))
    elif sort_key == "category":
        output.sort(key=lambda row: (str(row.get("category") or "").lower(), str(row.get("subcategory") or "").lower(), str(row.get("title") or "").lower()))
    return output[: max(1, min(10000, int(limit)))]
