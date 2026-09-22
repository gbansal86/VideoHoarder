"""Database schema ownership for canonical VideoHoarder video metadata.

Phase 1 centralizes additive ``videos`` table migrations here so ``app.py`` can
remain focused on application orchestration.  The migration is intentionally
idempotent and non-destructive: existing columns are reused and no legacy
column is dropped or renamed in this phase.
"""

from __future__ import annotations

import sqlite3
from typing import Mapping

# Existing schema extensions are preserved here exactly as additive columns.
# Newly approved canonical metadata fields are grouped at the bottom.
VIDEO_COLUMN_MIGRATIONS: Mapping[str, str] = {
    "subtitle_source": "TEXT",
    "subtitle_lang": "TEXT",
    "transcript_temp": "TEXT",
    "identity_json": "TEXT",
    "chapters_temp": "TEXT",
    "subtitle_base_lang": "TEXT",
    "youtube_tags": "TEXT",
    "youtube_category_id": "TEXT",
    "duration_iso": "TEXT",
    "duration_seconds": "REAL DEFAULT 0",
    "view_count": "INTEGER",
    "like_count": "INTEGER",
    "comment_count": "INTEGER",
    "metadata_source": "TEXT",
    "transcript_source": "TEXT",
    "final_status": "TEXT",
    "failure_reason": "TEXT",
    "chatgpt_summary_file": "TEXT",
    "chatgpt_imported": "INTEGER DEFAULT 0",
    "chatgpt_result_hash": "TEXT",
    "chatgpt_report_hash": "TEXT",
    "title_finalized": "INTEGER DEFAULT 0",
    "primary_category": "TEXT",
    "primary_topic": "TEXT",
    "topics_json": "TEXT",
    "entities_json": "TEXT",
    "ingredients_json": "TEXT",
    "herbs_json": "TEXT",
    "products_json": "TEXT",
    "people_json": "TEXT",
    "locations_json": "TEXT",
    "summary_language": "TEXT",
    "downloaded_at": "TEXT",
    "favorite": "INTEGER DEFAULT 0",
    "watched": "INTEGER DEFAULT 0",
    "user_rating": "INTEGER DEFAULT 0",
    "archived": "INTEGER DEFAULT 0",
    "phase5_hash": "TEXT",
    "phase5_indexed_at": "TEXT",
    "taxonomy_hash": "TEXT",
    "taxonomy_updated_at": "TEXT",
    "html_report_updated_at": "TEXT",
    "html_report_taxonomy_hash": "TEXT",
    "source_category_id": "TEXT",
    "source_category": "TEXT",
    "source_categories_json": "TEXT",
    "youtube_category_name": "TEXT",
    "comments_file": "TEXT",
    "comments_count_saved": "INTEGER DEFAULT 0",
    "comments_transcript_file": "TEXT",
    "comments_meaningful_file": "TEXT",
    "comments_meaningful_json": "TEXT",
    "comments_meaningful_count": "INTEGER DEFAULT 0",
    "comments_intelligence_updated_at": "TEXT",
    "video_identity_file": "TEXT",
    "thumbnail_url": "TEXT",
    "current_present": "INTEGER DEFAULT 1",
    "deleted_from_library": "INTEGER DEFAULT 0",
    "deleted_at": "TEXT",
    "last_transcript_recheck_at": "TEXT",
    "last_transcript_recheck_status": "TEXT",
    "last_transcript_recheck_detail": "TEXT",
    "chatgpt_package_status": "TEXT",
    "chatgpt_package_id": "TEXT",
    "chatgpt_packaged_at": "TEXT",

    # Phase 1 canonical metadata foundation.  These fields are storage only in
    # this phase; population/normalization begins in later phases.
    "availability": "TEXT",
    "source_chapters_json": "TEXT",
    "youtube_tags_cleaned": "TEXT",
    "channel_id": "TEXT",
    "channel_url": "TEXT",
    "uploader_id": "TEXT",
    "channel_follower_count": "INTEGER",
    "channel_is_verified": "INTEGER",
    "heatmap_json": "TEXT",
    "playlist": "TEXT",
    "playlist_id": "TEXT",
    "playlist_title": "TEXT",
    "playlist_index": "INTEGER",
    "playlist_count": "INTEGER",
    "playlist_channel": "TEXT",
    "playlist_channel_id": "TEXT",
    "playlist_uploader": "TEXT",
    "playlist_uploader_id": "TEXT",
    "playlist_webpage_url": "TEXT",
    "language": "TEXT",
    "is_live": "INTEGER",
    "was_live": "INTEGER",
    "live_status": "TEXT",
    "filesize_approx": "INTEGER",
    "metadata_schema_version": "INTEGER DEFAULT 0",
    "metadata_migrated_at": "TEXT",
    "metadata_migration_status": "TEXT",
}


def apply_video_schema_migrations(con: sqlite3.Connection) -> list[str]:
    """Add all missing ``videos`` columns and return the names added.

    The function is safe to call on every connection.  It never drops,
    renames, or rewrites an existing column, which keeps old libraries and
    older readers backward compatible during the phased rollout.
    """

    existing = {row[1] for row in con.execute("PRAGMA table_info(videos)").fetchall()}
    added: list[str] = []
    for column, declaration in VIDEO_COLUMN_MIGRATIONS.items():
        if column in existing:
            continue
        con.execute(f'ALTER TABLE videos ADD COLUMN "{column}" {declaration}')
        existing.add(column)
        added.append(column)
    return added
