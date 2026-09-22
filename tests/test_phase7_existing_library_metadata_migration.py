import json
import sqlite3
from pathlib import Path

from app.metadata_migration import (
    backup_database,
    run_existing_library_metadata_migration,
)
from app.metadata_schema import apply_video_schema_migrations


def make_db(tmp_path: Path):
    db = tmp_path / "library.db"
    con = sqlite3.connect(db)
    con.execute("""CREATE TABLE videos(
        video_id TEXT PRIMARY KEY, url TEXT, original_title TEXT, clean_title TEXT,
        channel TEXT, upload_date TEXT, description TEXT, local_folder TEXT,
        chatgpt_imported INTEGER DEFAULT 0, chatgpt_result_hash TEXT,
        duration_seconds REAL DEFAULT 0, youtube_tags TEXT, youtube_category_name TEXT,
        thumbnail_url TEXT, view_count INTEGER, like_count INTEGER, comment_count INTEGER,
        source_category TEXT, source_category_id TEXT, youtube_category_id TEXT
    )""")
    apply_video_schema_migrations(con)
    con.commit()
    return db, con


def add_video(con, tmp_path, video_id="abcdefghijk", with_info=True):
    folder = tmp_path / video_id
    data = folder / "_data"
    data.mkdir(parents=True)
    (data / ".video_id").write_text(video_id, encoding="utf-8")
    con.execute("""INSERT INTO videos(
        video_id,url,original_title,clean_title,channel,upload_date,description,local_folder,
        chatgpt_imported,chatgpt_result_hash,youtube_tags,youtube_category_name
    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",(
        video_id, f"https://www.youtube.com/watch?v={video_id}", "Old title", "Old title",
        "Old channel", "2020-01-02", "DB description", str(folder), 1, "keep-me",
        json.dumps(["old-tag"]), "Education"
    ))
    if with_info:
        info = {
            "id": video_id,
            "title": "Info title",
            "webpage_url": f"https://www.youtube.com/watch?v={video_id}",
            "channel": "Info channel",
            "channel_id": "UC123",
            "upload_date": "20200102",
            "duration": 321,
            "availability": "public",
            "categories": ["Howto & Style"],
            "tags": ["Useful", "BUY NOW"],
            "chapters": [{"start_time": 0, "end_time": 100, "title": "Intro"}],
            "filesize_approx": 123456,
            "heatmap": [{"start_time": 0, "end_time": 1, "value": .5}],
        }
        (data / f"{video_id}.info.json").write_text(json.dumps(info), encoding="utf-8")
    con.commit()
    return folder


def test_phase7_dry_run_is_read_only_and_reports_source_priority(tmp_path):
    _, con = make_db(tmp_path)
    add_video(con, tmp_path)
    before = con.execute("SELECT metadata_schema_version,metadata_migration_status FROM videos").fetchone()
    report = run_existing_library_metadata_migration(con, dry_run=True)
    after = con.execute("SELECT metadata_schema_version,metadata_migration_status FROM videos").fetchone()
    assert before == after
    assert report["mode"] == "DRY_RUN"
    assert report["processed"] == 1
    item = report["videos"][0]
    assert item["source_chain"] == ["sqlite", "info_json"]
    assert item["preview"]["chapters"] == 1
    assert item["preview"]["raw_tags"] == 2
    assert item["preview"]["cleaned_tags"] == 1
    con.close()


def test_phase7_apply_backs_up_and_preserves_chatgpt_results(tmp_path):
    db, con = make_db(tmp_path)
    add_video(con, tmp_path)
    backup = tmp_path / "backups" / "before_phase7.db"
    report = run_existing_library_metadata_migration(con, dry_run=False, backup_path=backup)
    assert backup.exists() and report["backup_path"] == str(backup)
    row = con.execute("""SELECT availability,source_chapters_json,youtube_tags,youtube_tags_cleaned,
        youtube_category_name,channel_id,filesize_approx,metadata_schema_version,metadata_migration_status,
        metadata_migrated_at,chatgpt_imported,chatgpt_result_hash FROM videos""").fetchone()
    assert row[0] == "public"
    assert len(json.loads(row[1])) == 1
    assert json.loads(row[2]) == ["Useful", "BUY NOW"]
    assert json.loads(row[3]) == ["Useful"]
    assert row[4] == "Education"  # non-empty existing SQLite category wins
    assert row[5] == "UC123"
    assert row[6] == 123456
    assert row[7] == 1 and row[8] == "COMPLETE" and row[9]
    assert row[10] == 1 and row[11] == "keep-me"
    # Backup is a real pre-migration SQLite DB.
    bcon = sqlite3.connect(backup)
    brow = bcon.execute("SELECT metadata_schema_version,metadata_migration_status FROM videos").fetchone()
    bcon.close()
    assert brow == (0, None)
    con.close()


def test_phase7_repeat_run_is_idempotent(tmp_path):
    _, con = make_db(tmp_path)
    add_video(con, tmp_path)
    first = run_existing_library_metadata_migration(con, dry_run=False)
    second = run_existing_library_metadata_migration(con, dry_run=False)
    assert first["migrated"] == 1
    assert second["migrated"] == 0
    assert second["skipped_current"] == 1
    con.close()


def test_phase7_interrupted_in_progress_is_resumable(tmp_path):
    _, con = make_db(tmp_path)
    add_video(con, tmp_path)
    con.execute("UPDATE videos SET metadata_migration_status='IN_PROGRESS', metadata_schema_version=0")
    con.commit()
    report = run_existing_library_metadata_migration(con, dry_run=False)
    status = con.execute("SELECT metadata_migration_status FROM videos").fetchone()[0]
    assert report["migrated"] == 1
    assert status == "COMPLETE"
    con.close()


def test_phase7_missing_info_uses_metadata_only_callback_without_media_download(tmp_path):
    _, con = make_db(tmp_path)
    vid = "zyxwvutsrqp"
    add_video(con, tmp_path, video_id=vid, with_info=False)
    # Make existing fallback sparse so metadata-only refresh is genuinely required.
    con.execute("UPDATE videos SET youtube_category_name='',youtube_tags='[]'")
    con.commit()
    calls = []
    def metadata_only_fetcher(video_id, url):
        calls.append((video_id, url))
        return {
            "id": video_id,
            "webpage_url": url,
            "categories": ["Science & Technology"],
            "tags": ["AI", "tutorial"],
            "channel_id": "UC-FETCH",
            "availability": "public",
            "filesize_approx": 98765,
        }
    report = run_existing_library_metadata_migration(con, dry_run=False, metadata_fetcher=metadata_only_fetcher)
    assert calls == [(vid, f"https://www.youtube.com/watch?v={vid}")]
    item = report["videos"][0]
    assert item["source_chain"] == ["sqlite", "metadata_only_fetch"]
    row = con.execute("SELECT youtube_category_name,channel_id,filesize_approx,metadata_migration_status FROM videos").fetchone()
    assert row == ("Science & Technology", "UC-FETCH", 98765, "COMPLETE")
    con.close()


def test_phase7_fetch_failure_finishes_with_warning_not_data_loss(tmp_path):
    _, con = make_db(tmp_path)
    vid = "mnopqrstuvw"
    add_video(con, tmp_path, video_id=vid, with_info=False)
    # Make fallback sparse enough to request metadata-only fetch.
    con.execute("UPDATE videos SET youtube_category_name='',youtube_tags='[]'")
    con.commit()
    def failing_fetcher(video_id, url):
        raise RuntimeError("offline")
    report = run_existing_library_metadata_migration(con, dry_run=False, metadata_fetcher=failing_fetcher)
    assert report["failed"] == 0
    assert report["complete_with_warnings"] == 1
    row = con.execute("SELECT metadata_migration_status,chatgpt_result_hash FROM videos").fetchone()
    assert row == ("COMPLETE_WITH_WARNINGS", "keep-me")
    assert any("metadata_only_fetch_failed" in w for w in report["videos"][0]["warnings"])
    con.close()


def test_phase7_force_reprocesses_current_row(tmp_path):
    _, con = make_db(tmp_path)
    add_video(con, tmp_path)
    run_existing_library_metadata_migration(con, dry_run=False)
    forced = run_existing_library_metadata_migration(con, dry_run=False, force=True)
    assert forced["migrated"] == 1
    assert forced["skipped_current"] == 0
    con.close()


def test_phase7_app_wrapper_dry_run_uses_existing_db_without_network(tmp_path, monkeypatch):
    from app import app
    db, con = make_db(tmp_path)
    add_video(con, tmp_path)
    con.close()
    monkeypatch.setattr(app, "DB", db)
    monkeypatch.setattr(app, "BASE", tmp_path)
    report = app.phase7_migrate_existing_library_metadata(dry_run=True, fetch_missing=False)
    assert report["mode"] == "DRY_RUN"
    assert report["processed"] == 1
    assert Path(report["report_path"]).exists()
    check = sqlite3.connect(db)
    assert check.execute("SELECT metadata_migration_status FROM videos").fetchone()[0] is None
    check.close()


def test_phase7_selected_video_ids_limit_local_repair_scope(tmp_path):
    _, con = make_db(tmp_path)
    first = "selectvid001"
    second = "selectvid002"
    add_video(con, tmp_path, video_id=first)
    add_video(con, tmp_path, video_id=second)
    report = run_existing_library_metadata_migration(
        con,
        dry_run=False,
        force=True,
        metadata_fetcher=None,
        video_ids=[first],
    )
    assert report["processed"] == 1
    assert report["migrated"] == 1
    rows = dict(con.execute("SELECT video_id,metadata_migration_status FROM videos").fetchall())
    assert rows[first] == "COMPLETE"
    assert rows[second] is None
    con.close()


def test_missing_data_cleanup_checkbox_wires_local_metadata_repair_without_refresh_flag():
    app_source = (Path(__file__).parents[1] / "app" / "app.py").read_text(encoding="utf-8")
    assert "canonical_metadata_repair:$('subtitleCleanup').checked" in app_source
    assert 'if options.get("canonical_metadata_repair")' in app_source
    assert "metadata_fetcher=None" in app_source
    assert 'video_ids=selected_ids' in app_source
