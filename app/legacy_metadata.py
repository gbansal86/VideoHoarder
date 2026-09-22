"""Canonical-first metadata resolution for legacy VideoHoarder readers.

Phase 8 keeps retained yt-dlp .info.json as a compatibility/recovery fallback while
moving old readers toward the canonical SQLite metadata introduced in Phases 1-7.
This module is deliberately GUI-free and side-effect-free except for database reads.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

CORE_FIELDS = (
    "video_id", "url", "original_title", "clean_title", "channel", "upload_date",
    "description", "availability", "youtube_category_name", "channel_id",
    "channel_url", "uploader_id", "filesize_approx", "metadata_schema_version",
    "metadata_migration_status",
)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_date(value: Any) -> str:
    text = _text(value)
    if re.fullmatch(r"\d{8}", text):
        return f"{text[:4]}-{text[4:6]}-{text[6:8]}"
    return text


def _table_columns(con, table: str = "videos") -> set[str]:
    try:
        return {str(row[1]) for row in con.execute(f"PRAGMA table_info({table})").fetchall()}
    except Exception:
        return set()


def canonical_db_metadata(con, video_id: str) -> dict[str, Any]:
    """Return canonical/local identity metadata from SQLite when a row exists."""
    vid = _text(video_id)
    if not vid:
        return {}
    cols = _table_columns(con)
    selected = [name for name in CORE_FIELDS if name in cols]
    if not selected:
        return {}
    row = con.execute(
        "SELECT " + ",".join(f'\"{name}\"' for name in selected) + " FROM videos WHERE video_id=?",
        (vid,),
    ).fetchone()
    if not row:
        return {}
    out = dict(zip(selected, row))
    if "upload_date" in out:
        out["upload_date"] = _normalize_date(out.get("upload_date"))
    out["video_id"] = vid
    return out


def canonical_metadata_available(con, video_id: str) -> bool:
    """Whether SQLite contains enough canonical identity metadata to replace info.json as a requirement."""
    data = canonical_db_metadata(con, video_id)
    if not data:
        return False
    # A migrated/current row is always sufficient. Future-download rows may be
    # canonical even before explicit old-library migration, so useful identity is
    # also accepted.
    try:
        if int(data.get("metadata_schema_version") or 0) >= 1:
            return True
    except Exception:
        pass
    useful = [data.get("url"), data.get("original_title"), data.get("channel"), data.get("upload_date")]
    return sum(bool(_text(v)) for v in useful) >= 2


def read_info_json_metadata(folder: str | Path) -> dict[str, Any]:
    """Read retained yt-dlp metadata only as a fallback."""
    folder = Path(folder)
    roots = [folder / "_data", folder]
    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.glob("*.info.json"):
            try:
                path = path.resolve()
            except Exception:
                pass
            if path in seen:
                continue
            seen.add(path)
            try:
                obj = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            return {
                "video_id": _text(obj.get("id")),
                "url": _text(obj.get("webpage_url") or obj.get("original_url")),
                "original_title": _text(obj.get("title")),
                "clean_title": _text(obj.get("title")),
                "channel": _text(obj.get("channel") or obj.get("uploader") or obj.get("creator")),
                "upload_date": _normalize_date(obj.get("upload_date")),
                "description": _text(obj.get("description")),
                "availability": _text(obj.get("availability")),
                "youtube_category_name": _text((obj.get("categories") or [""])[0] if isinstance(obj.get("categories"), list) else obj.get("categories")),
                "channel_id": _text(obj.get("channel_id")),
                "channel_url": _text(obj.get("channel_url")),
                "uploader_id": _text(obj.get("uploader_id")),
                "filesize_approx": obj.get("filesize_approx"),
                "_source_info_json": str(path),
            }
    return {}


def merge_prefer_primary(primary: Mapping[str, Any] | None, fallback: Mapping[str, Any] | None) -> dict[str, Any]:
    """Fill only blank primary values from fallback; never overwrite richer canonical values."""
    out = dict(primary or {})
    for key, value in dict(fallback or {}).items():
        if key.startswith("_"):
            continue
        current = out.get(key)
        blank = current is None or current == "" or current == [] or current == {}
        if blank and value not in (None, "", [], {}):
            out[key] = value
    return out


def resolve_legacy_metadata(con, video_id: str, folder: str | Path | None = None, local_hint: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Resolve metadata using canonical DB -> local hint -> retained .info.json."""
    db = canonical_db_metadata(con, video_id)
    out = merge_prefer_primary(db, local_hint)
    info = read_info_json_metadata(folder) if folder else {}
    out = merge_prefer_primary(out, info)
    sources = []
    if db:
        sources.append("sqlite")
    if local_hint:
        sources.append("local_hint")
    if info:
        sources.append("info_json_fallback")
    out["_sources"] = sources
    if info.get("_source_info_json"):
        out["_source_info_json"] = info["_source_info_json"]
    return out
