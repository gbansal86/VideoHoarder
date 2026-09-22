"""Persistence helpers for canonical VideoHoarder metadata.

Phase 3 wires the pure Phase 2 normalization layer into future metadata scans
and downloads.  This module owns the SQLite update contract for canonical
metadata so app.py only orchestrates extraction/download workflows.

The functions are intentionally additive and backward-compatible: existing
legacy metadata columns continue to be populated by the existing save path,
while the new canonical/local-only fields are updated from normalized data.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from collections.abc import Mapping
from typing import Any

try:
    from .metadata_normalization import flattened_persistence_view, normalize_extractor_metadata
except ImportError:  # pragma: no cover - direct script compatibility
    from metadata_normalization import flattened_persistence_view, normalize_extractor_metadata


def canonicalize_metadata_record(
    record: Mapping[str, Any] | None,
    *,
    raw: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize a metadata record, optionally overlaying enriched fields.

    ``raw`` should be the richest extractor object available (for example the
    full yt-dlp JSON). ``record`` may contain VideoHoarder/API-enriched values.
    Record values win when non-empty so API category/statistics enrichment is
    preserved while yt-dlp-only chapters/heatmap/live/playlist data survives.
    """

    record = dict(record or {})
    raw_map = dict(raw or {})
    combined = dict(raw_map)
    for key, value in record.items():
        if value not in (None, "", [], {}):
            combined[key] = value
        elif key not in combined:
            combined[key] = value
    return normalize_extractor_metadata(combined, fallback=record)


def attach_canonical_metadata(
    record: Mapping[str, Any] | None,
    *,
    raw: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a shallow record copy with an in-memory canonical snapshot."""

    result = dict(record or {})
    result["_canonical_metadata"] = canonicalize_metadata_record(result, raw=raw)
    return result


def persist_canonical_metadata(
    con: sqlite3.Connection,
    video_id: str,
    normalized: Mapping[str, Any],
) -> None:
    """Persist canonical/local metadata without erasing richer existing data.

    Metadata scans may be sparse (especially YouTube Data API rows), while a
    later retained ``.info.json`` can contain chapters, heatmap, playlist/live
    state and filesize data.  Empty/unknown incoming values therefore preserve
    the current DB value; meaningful incoming values replace it.
    """

    view = flattened_persistence_view(normalized)
    source_chapters = view.get("source_chapters") or []
    raw_tags = view.get("youtube_tags") or []
    cleaned_tags = view.get("youtube_tags_cleaned") or []
    heatmap = view.get("heatmap") or []

    def bint(value: Any) -> int | None:
        if value is None:
            return None
        return 1 if bool(value) else 0

    chapters_json = json.dumps(source_chapters, ensure_ascii=False) if source_chapters else ""
    tags_json = json.dumps(raw_tags, ensure_ascii=False) if raw_tags else ""
    cleaned_tags_json = json.dumps(cleaned_tags, ensure_ascii=False) if cleaned_tags else ""
    heatmap_json = json.dumps(heatmap, ensure_ascii=False) if heatmap else ""

    con.execute(
        """UPDATE videos SET
             availability=CASE WHEN ?<>'' THEN ? ELSE availability END,
             duration_seconds=CASE WHEN ? IS NOT NULL AND ?>=0 THEN ? ELSE duration_seconds END,
             source_chapters_json=CASE WHEN ?<>'' THEN ? ELSE source_chapters_json END,
             youtube_tags=CASE WHEN ?<>'' THEN ? ELSE youtube_tags END,
             youtube_tags_cleaned=CASE WHEN ?<>'' THEN ? ELSE youtube_tags_cleaned END,
             youtube_category_name=CASE WHEN ?<>'' THEN ? ELSE youtube_category_name END,
             channel_id=CASE WHEN ?<>'' THEN ? ELSE channel_id END,
             channel_url=CASE WHEN ?<>'' THEN ? ELSE channel_url END,
             uploader_id=CASE WHEN ?<>'' THEN ? ELSE uploader_id END,
             channel_follower_count=COALESCE(?,channel_follower_count),
             channel_is_verified=COALESCE(?,channel_is_verified),
             heatmap_json=CASE WHEN ?<>'' THEN ? ELSE heatmap_json END,
             playlist=CASE WHEN ?<>'' THEN ? ELSE playlist END,
             playlist_id=CASE WHEN ?<>'' THEN ? ELSE playlist_id END,
             playlist_title=CASE WHEN ?<>'' THEN ? ELSE playlist_title END,
             playlist_index=COALESCE(?,playlist_index),
             playlist_count=COALESCE(?,playlist_count),
             playlist_channel=CASE WHEN ?<>'' THEN ? ELSE playlist_channel END,
             playlist_channel_id=CASE WHEN ?<>'' THEN ? ELSE playlist_channel_id END,
             playlist_uploader=CASE WHEN ?<>'' THEN ? ELSE playlist_uploader END,
             playlist_uploader_id=CASE WHEN ?<>'' THEN ? ELSE playlist_uploader_id END,
             playlist_webpage_url=CASE WHEN ?<>'' THEN ? ELSE playlist_webpage_url END,
             language=CASE WHEN ?<>'' THEN ? ELSE language END,
             is_live=COALESCE(?,is_live),
             was_live=COALESCE(?,was_live),
             live_status=CASE WHEN ?<>'' THEN ? ELSE live_status END,
             filesize_approx=COALESCE(?,filesize_approx),
             thumbnail_url=CASE WHEN ?<>'' THEN ? ELSE thumbnail_url END,
             view_count=COALESCE(?,view_count),
             like_count=COALESCE(?,like_count),
             comment_count=COALESCE(?,comment_count),
             metadata_schema_version=CASE WHEN ?>metadata_schema_version THEN ? ELSE metadata_schema_version END
           WHERE video_id=?""",
        (
            view.get("availability") or "", view.get("availability") or "",
            view.get("duration_seconds"), view.get("duration_seconds"), view.get("duration_seconds"),
            chapters_json, chapters_json,
            tags_json, tags_json,
            cleaned_tags_json, cleaned_tags_json,
            view.get("youtube_category_name") or "", view.get("youtube_category_name") or "",
            view.get("channel_id") or "", view.get("channel_id") or "",
            view.get("channel_url") or "", view.get("channel_url") or "",
            view.get("uploader_id") or "", view.get("uploader_id") or "",
            view.get("channel_follower_count"),
            bint(view.get("channel_is_verified")),
            heatmap_json, heatmap_json,
            view.get("playlist") or "", view.get("playlist") or "",
            view.get("playlist_id") or "", view.get("playlist_id") or "",
            view.get("playlist_title") or "", view.get("playlist_title") or "",
            view.get("playlist_index"),
            view.get("playlist_count"),
            view.get("playlist_channel") or "", view.get("playlist_channel") or "",
            view.get("playlist_channel_id") or "", view.get("playlist_channel_id") or "",
            view.get("playlist_uploader") or "", view.get("playlist_uploader") or "",
            view.get("playlist_uploader_id") or "", view.get("playlist_uploader_id") or "",
            view.get("playlist_webpage_url") or "", view.get("playlist_webpage_url") or "",
            view.get("language") or "", view.get("language") or "",
            bint(view.get("is_live")),
            bint(view.get("was_live")),
            view.get("live_status") or "", view.get("live_status") or "",
            view.get("filesize_approx"),
            view.get("thumbnail_url") or "", view.get("thumbnail_url") or "",
            view.get("view_count"), view.get("like_count"), view.get("comment_count"),
            int(view.get("metadata_schema_version") or 0), int(view.get("metadata_schema_version") or 0),
            str(video_id),
        ),
    )


def canonical_metadata_from_info_json(
    path: str | Path,
    *,
    fallback: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Load one retained yt-dlp info JSON and normalize it canonically."""

    info_path = Path(path)
    raw = json.loads(info_path.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(raw, Mapping):
        raise ValueError(f"info JSON is not an object: {info_path}")
    return canonicalize_metadata_record(fallback or {}, raw=raw)


def persist_info_json_canonical_metadata(
    con: sqlite3.Connection,
    video_id: str,
    path: str | Path,
    *,
    fallback: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize and persist one retained yt-dlp info JSON artifact."""

    normalized = canonical_metadata_from_info_json(path, fallback=fallback)
    persist_canonical_metadata(con, video_id, normalized)
    return normalized


def persist_record_canonical_metadata(
    con: sqlite3.Connection,
    record: Mapping[str, Any],
) -> dict[str, Any]:
    """Persist a record's attached snapshot or normalize it on demand."""

    video_id = str(record.get("id") or record.get("video_id") or "").strip()
    if not video_id:
        raise ValueError("metadata record is missing video id")
    normalized = record.get("_canonical_metadata")
    if not isinstance(normalized, Mapping):
        normalized = canonicalize_metadata_record(record)
    persist_canonical_metadata(con, video_id, normalized)
    return dict(normalized)
