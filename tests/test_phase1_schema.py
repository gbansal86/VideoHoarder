import sqlite3

from app.metadata_schema import VIDEO_COLUMN_MIGRATIONS, apply_video_schema_migrations


def _columns(con):
    return {row[1] for row in con.execute("PRAGMA table_info(videos)")}


def test_phase1_schema_migration_is_additive_and_idempotent():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE videos(video_id TEXT PRIMARY KEY, original_title TEXT)")

    first_added = apply_video_schema_migrations(con)
    first_columns = _columns(con)
    second_added = apply_video_schema_migrations(con)
    second_columns = _columns(con)

    assert first_added
    assert second_added == []
    assert first_columns == second_columns
    assert {"video_id", "original_title"}.issubset(first_columns)
    assert set(VIDEO_COLUMN_MIGRATIONS).issubset(first_columns)


def test_phase1_preserves_existing_values_and_legacy_columns():
    con = sqlite3.connect(":memory:")
    con.execute(
        "CREATE TABLE videos(video_id TEXT PRIMARY KEY, youtube_category_name TEXT, clean_title TEXT)"
    )
    con.execute(
        "INSERT INTO videos(video_id, youtube_category_name, clean_title) VALUES(?,?,?)",
        ("abc123", "Howto & Style", "Existing Clean Title"),
    )

    apply_video_schema_migrations(con)
    row = con.execute(
        "SELECT video_id, youtube_category_name, clean_title FROM videos WHERE video_id='abc123'"
    ).fetchone()

    assert row == ("abc123", "Howto & Style", "Existing Clean Title")
    assert "youtube_category_name" in _columns(con)


def test_phase1_canonical_metadata_columns_are_present():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE videos(video_id TEXT PRIMARY KEY)")
    apply_video_schema_migrations(con)

    expected = {
        "availability",
        "source_chapters_json",
        "youtube_tags_cleaned",
        "channel_id",
        "channel_url",
        "uploader_id",
        "channel_follower_count",
        "channel_is_verified",
        "heatmap_json",
        "playlist",
        "playlist_id",
        "playlist_title",
        "playlist_index",
        "playlist_count",
        "playlist_channel",
        "playlist_channel_id",
        "playlist_uploader",
        "playlist_uploader_id",
        "playlist_webpage_url",
        "language",
        "is_live",
        "was_live",
        "live_status",
        "filesize_approx",
        "metadata_schema_version",
        "metadata_migrated_at",
        "metadata_migration_status",
    }
    assert expected.issubset(_columns(con))


def test_phase1_db_connect_applies_canonical_schema(tmp_path, monkeypatch):
    from app import app

    test_db = tmp_path / "video_library.db"
    monkeypatch.setattr(app, "DB", test_db)

    con = app.db_connect()
    try:
        columns = _columns(con)
        assert set(VIDEO_COLUMN_MIGRATIONS).issubset(columns)
        assert "youtube_category_name" in columns
        assert "source_chapters_json" in columns
        assert "metadata_schema_version" in columns
    finally:
        con.close()
