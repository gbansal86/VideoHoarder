"""Existing-library canonical metadata migration for VideoHoarder.

Phase 7 backfills the canonical metadata fields introduced in Phases 1-4 for
videos that pre-date the new persistence path.  The migration is deliberately
safe:

* dry-run is read-only;
* an actual run can create a transaction-consistent SQLite backup first;
* source priority is SQLite -> retained .info.json -> local metadata artifacts
  -> optional metadata-only fetch callback;
* no function in this module downloads video/audio media;
* completed/current rows are skipped on repeated runs unless ``force=True``;
* interrupted ``IN_PROGRESS`` rows are safe to process again;
* existing ChatGPT/result columns are never changed.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from .metadata_normalization import CANONICAL_METADATA_SCHEMA_VERSION
    from .metadata_persistence import canonicalize_metadata_record, persist_canonical_metadata
except ImportError:  # pragma: no cover - direct script compatibility
    from metadata_normalization import CANONICAL_METADATA_SCHEMA_VERSION
    from metadata_persistence import canonicalize_metadata_record, persist_canonical_metadata

MetadataFetcher = Callable[[str, str], Mapping[str, Any] | None]

_COMPLETED = {"COMPLETE", "COMPLETE_WITH_WARNINGS"}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _json_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if not value:
        return []
    if isinstance(value, str):
        try:
            obj = json.loads(value)
            return obj if isinstance(obj, list) else []
        except Exception:
            return [x.strip() for x in value.split(",") if x.strip()]
    return []


def _json_value(value: Any, default: Any) -> Any:
    if isinstance(value, type(default)):
        return value
    if not value:
        return default
    if isinstance(value, str):
        try:
            obj = json.loads(value)
            return obj if isinstance(obj, type(default)) else default
        except Exception:
            return default
    return default


def _table_columns(con: sqlite3.Connection, table: str = "videos") -> list[str]:
    return [str(row[1]) for row in con.execute(f"PRAGMA table_info({table})").fetchall()]


def _row_mapping(columns: list[str], row: tuple[Any, ...]) -> dict[str, Any]:
    return dict(zip(columns, row))


def sqlite_row_metadata(row: Mapping[str, Any]) -> dict[str, Any]:
    """Translate one existing DB row into normalizer-friendly fallback data."""

    raw_tags = _json_list(row.get("youtube_tags"))
    source_chapters = _json_list(row.get("source_chapters_json"))
    heatmap = _json_list(row.get("heatmap_json"))
    return {
        "id": _text(row.get("video_id")),
        "url": _text(row.get("url")),
        "webpage_url": _text(row.get("url")),
        "title": _text(row.get("original_title")),
        "channel": _text(row.get("channel")),
        "upload_date": _text(row.get("upload_date")),
        "description": _text(row.get("description")),
        "duration_seconds": row.get("duration_seconds"),
        "availability": _text(row.get("availability")),
        "youtube_category_name": _text(row.get("youtube_category_name") or row.get("source_category")),
        "youtube_category_id": _text(row.get("youtube_category_id") or row.get("source_category_id")),
        "youtube_tags": raw_tags,
        "chapters": source_chapters,
        "channel_id": _text(row.get("channel_id")),
        "channel_url": _text(row.get("channel_url")),
        "uploader_id": _text(row.get("uploader_id")),
        "channel_follower_count": row.get("channel_follower_count"),
        "channel_is_verified": row.get("channel_is_verified"),
        "heatmap": heatmap,
        "thumbnail_url": _text(row.get("thumbnail_url")),
        "playlist": _text(row.get("playlist")),
        "playlist_id": _text(row.get("playlist_id")),
        "playlist_title": _text(row.get("playlist_title")),
        "playlist_index": row.get("playlist_index"),
        "playlist_count": row.get("playlist_count"),
        "playlist_channel": _text(row.get("playlist_channel")),
        "playlist_channel_id": _text(row.get("playlist_channel_id")),
        "playlist_uploader": _text(row.get("playlist_uploader")),
        "playlist_uploader_id": _text(row.get("playlist_uploader_id")),
        "playlist_webpage_url": _text(row.get("playlist_webpage_url")),
        "language": _text(row.get("language")),
        "is_live": row.get("is_live"),
        "was_live": row.get("was_live"),
        "live_status": _text(row.get("live_status")),
        "filesize_approx": row.get("filesize_approx"),
        "view_count": row.get("view_count"),
        "like_count": row.get("like_count"),
        "comment_count": row.get("comment_count"),
    }


def _candidate_folders(row: Mapping[str, Any]) -> list[Path]:
    result: list[Path] = []
    folder = _text(row.get("local_folder"))
    if folder:
        p = Path(folder)
        if p.exists() and p.is_dir():
            result.append(p)
    return result


def find_retained_info_json(row: Mapping[str, Any]) -> Path | None:
    """Find the best retained yt-dlp info JSON for an existing DB row."""

    video_id = _text(row.get("video_id"))
    candidates: list[Path] = []
    for folder in _candidate_folders(row):
        data = folder / "_data"
        for root in (data, folder):
            if not root.exists():
                continue
            if video_id:
                candidates.extend(root.glob(f"{video_id}*.info.json"))
            candidates.extend(root.glob("*.info.json"))
    unique = {
        str(p.resolve()): p
        for p in candidates
        if p.is_file() and not p.name.lower().endswith(".comments_source.info.json")
    }
    if not unique:
        return None

    def priority(path: Path) -> tuple[int, int, float, str]:
        low = path.name.lower()
        # Canonical retained yt-dlp metadata first, then exact/video-ID metadata,
        # then other normal info JSON. Comment-workflow metadata is excluded above.
        if low == "metadata.info.json":
            tier = 0
        elif video_id and low == f"{video_id.lower()}.info.json":
            tier = 1
        elif video_id and low.startswith(video_id.lower()) and low.endswith(".info.json"):
            tier = 2
        else:
            tier = 3
        in_data = 0 if path.parent.name.lower() == "_data" else 1
        return (tier, in_data, -path.stat().st_mtime, low)

    return sorted(unique.values(), key=priority)[0]


def local_artifact_metadata(row: Mapping[str, Any]) -> dict[str, Any]:
    """Best-effort metadata from small local sidecar artifacts only.

    These files are used only to fill blank identity/display metadata before an
    optional metadata-only online refresh.  Transcript content is intentionally
    not used as metadata evidence.
    """

    video_id = _text(row.get("video_id"))
    out: dict[str, Any] = {}
    for folder in _candidate_folders(row):
        roots = [folder / "_data", folder]
        for root in roots:
            if not root.exists():
                continue
            title_files = list(root.glob(f"{video_id}*.original-title*")) if video_id else []
            desc_files = list(root.glob(f"{video_id}*.description*")) if video_id else []
            if not title_files:
                title_files = list(root.glob("*.original-title*"))
            if not desc_files:
                desc_files = list(root.glob("*.description*"))
            if title_files and not out.get("title"):
                try:
                    out["title"] = title_files[0].read_text(encoding="utf-8", errors="replace").strip()
                except Exception:
                    pass
            if desc_files and not out.get("description"):
                try:
                    out["description"] = desc_files[0].read_text(encoding="utf-8", errors="replace").strip()
                except Exception:
                    pass
    return out


def load_info_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(obj, Mapping):
        raise ValueError(f"info JSON is not an object: {path}")
    return dict(obj)


def backup_database(con: sqlite3.Connection, destination: str | Path) -> Path:
    """Create a transaction-consistent SQLite backup using the backup API."""

    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    target = sqlite3.connect(path)
    try:
        con.backup(target)
        target.commit()
    finally:
        target.close()
    return path


def _needs_online_refresh(normalized: Mapping[str, Any]) -> bool:
    core = normalized.get("llm_core") or {}
    aux = normalized.get("llm_auxiliary") or {}
    local = normalized.get("local_only") or {}
    # A row can be migrated without network access; online metadata is only a
    # useful final source when the compact canonical record is materially sparse.
    return not any([
        core.get("category"),
        aux.get("source_chapters"),
        aux.get("source_tags_raw"),
        local.get("channel_id"),
        local.get("filesize_approx"),
    ])


def plan_video_migration(
    row: Mapping[str, Any],
    *,
    metadata_fetcher: MetadataFetcher | None = None,
) -> dict[str, Any]:
    """Build one migration plan without mutating the DB."""

    video_id = _text(row.get("video_id"))
    fallback = sqlite_row_metadata(row)
    local = local_artifact_metadata(row)
    for key, value in local.items():
        if value not in (None, "", [], {}) and fallback.get(key) in (None, "", [], {}):
            fallback[key] = value

    source_chain = ["sqlite"]
    warnings: list[str] = []
    raw: Mapping[str, Any] | None = None
    info_path = find_retained_info_json(row)
    if info_path:
        try:
            raw = load_info_json(info_path)
            source_chain.append("info_json")
        except Exception as exc:
            warnings.append(f"info_json_read_failed: {type(exc).__name__}: {exc}")

    normalized = canonicalize_metadata_record(fallback, raw=raw)

    if metadata_fetcher is not None and _needs_online_refresh(normalized):
        try:
            fetched = metadata_fetcher(video_id, _text(row.get("url")))
            if fetched:
                raw_combined = dict(raw or {})
                raw_combined.update(dict(fetched))
                normalized = canonicalize_metadata_record(fallback, raw=raw_combined)
                source_chain.append("metadata_only_fetch")
            else:
                warnings.append("metadata_only_fetch_returned_no_data")
        except Exception as exc:
            warnings.append(f"metadata_only_fetch_failed: {type(exc).__name__}: {exc}")

    if local:
        source_chain.insert(1, "local_artifacts")

    core = normalized.get("llm_core") or {}
    aux = normalized.get("llm_auxiliary") or {}
    local_only = normalized.get("local_only") or {}
    sparse = _needs_online_refresh(normalized)
    if sparse:
        warnings.append("canonical_metadata_remains_sparse")

    return {
        "video_id": video_id,
        "source_chain": source_chain,
        "info_json": str(info_path) if info_path else "",
        "warnings": warnings,
        "normalized": normalized,
        "preview": {
            "category": core.get("category") or "",
            "chapters": len(aux.get("source_chapters") or []),
            "raw_tags": len(aux.get("source_tags_raw") or []),
            "cleaned_tags": len(aux.get("source_tags_cleaned") or []),
            "availability": core.get("availability") or "",
            "channel_id": local_only.get("channel_id") or "",
            "filesize_approx": local_only.get("filesize_approx"),
        },
    }


def run_existing_library_metadata_migration(
    con: sqlite3.Connection,
    *,
    dry_run: bool = True,
    force: bool = False,
    metadata_fetcher: MetadataFetcher | None = None,
    backup_path: str | Path | None = None,
    now: datetime | None = None,
    limit: int = 0,
    video_ids: list[str] | tuple[str, ...] | set[str] | None = None,
) -> dict[str, Any]:
    """Dry-run or execute canonical metadata backfill for existing DB rows."""

    columns = _table_columns(con)
    if "video_id" not in columns:
        raise RuntimeError("videos table is missing video_id")
    order = "rowid"
    rows = con.execute(f"SELECT {','.join(chr(34)+c+chr(34) for c in columns)} FROM videos ORDER BY {order}").fetchall()
    stamp = (now or datetime.now()).isoformat(timespec="seconds")
    report: dict[str, Any] = {
        "mode": "DRY_RUN" if dry_run else "APPLY",
        "created_at": stamp,
        "canonical_schema_version": CANONICAL_METADATA_SCHEMA_VERSION,
        "total_rows": len(rows),
        "processed": 0,
        "migrated": 0,
        "skipped_current": 0,
        "complete_with_warnings": 0,
        "failed": 0,
        "backup_path": "",
        "videos": [],
    }

    selected_ids = {str(value).strip() for value in (video_ids or []) if str(value).strip()}
    candidates: list[dict[str, Any]] = []
    for raw_row in rows:
        row = _row_mapping(columns, raw_row)
        if selected_ids and _text(row.get("video_id")) not in selected_ids:
            continue
        version = int(row.get("metadata_schema_version") or 0)
        status = _text(row.get("metadata_migration_status")).upper()
        if not force and version >= CANONICAL_METADATA_SCHEMA_VERSION and status in _COMPLETED:
            report["skipped_current"] += 1
            report["videos"].append({"video_id": _text(row.get("video_id")), "action": "SKIP_CURRENT", "status": status})
            continue
        candidates.append(row)
        if limit and len(candidates) >= int(limit):
            break

    if not dry_run and backup_path and candidates:
        report["backup_path"] = str(backup_database(con, backup_path))

    for row in candidates:
        video_id = _text(row.get("video_id"))
        item: dict[str, Any] = {"video_id": video_id}
        report["processed"] += 1
        try:
            plan = plan_video_migration(row, metadata_fetcher=metadata_fetcher)
            item.update({
                "action": "WOULD_MIGRATE" if dry_run else "MIGRATED",
                "source_chain": plan["source_chain"],
                "info_json": plan["info_json"],
                "preview": plan["preview"],
                "warnings": plan["warnings"],
            })
            if not dry_run:
                # One video's canonical update is an atomic unit.  A SAVEPOINT
                # preserves earlier successful videos while allowing every write
                # for this video to be rolled back before FAILED is recorded.
                savepoint = f"vh_metadata_{report['processed']}"
                con.execute(f"SAVEPOINT {savepoint}")
                try:
                    con.execute(
                        "UPDATE videos SET metadata_migration_status=? WHERE video_id=?",
                        ("IN_PROGRESS", video_id),
                    )
                    persist_canonical_metadata(con, video_id, plan["normalized"])
                    final_status = "COMPLETE_WITH_WARNINGS" if plan["warnings"] else "COMPLETE"
                    con.execute(
                        "UPDATE videos SET metadata_migration_status=?, metadata_migrated_at=? WHERE video_id=?",
                        (final_status, stamp, video_id),
                    )
                    con.execute(f"RELEASE SAVEPOINT {savepoint}")
                    con.commit()
                except Exception:
                    con.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                    con.execute(f"RELEASE SAVEPOINT {savepoint}")
                    raise
                item["status"] = final_status
                report["migrated"] += 1
                if final_status == "COMPLETE_WITH_WARNINGS":
                    report["complete_with_warnings"] += 1
            else:
                item["status"] = "WOULD_COMPLETE_WITH_WARNINGS" if plan["warnings"] else "WOULD_COMPLETE"
        except Exception as exc:
            item.update({"action": "FAILED", "status": "FAILED", "error": f"{type(exc).__name__}: {exc}"})
            report["failed"] += 1
            if not dry_run:
                try:
                    con.execute(
                        "UPDATE videos SET metadata_migration_status=?, metadata_migrated_at=? WHERE video_id=?",
                        ("FAILED", stamp, video_id),
                    )
                    con.commit()
                except Exception:
                    con.rollback()
        report["videos"].append(item)

    report["ready"] = report["failed"] == 0
    return report
