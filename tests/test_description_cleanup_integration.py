from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pytest

from app import description_cleanup as dc
from app.metadata_migration import find_retained_info_json


SAMPLE = """Demo Video Title
This is a sufficiently long introduction paragraph explaining the video topic and what the viewer will learn from the content in detail.
00:00 - Introduction
01:10 - Main Topic
PRODUCTS RELATED TO THIS VIDEO
Buy Example Product - https://example.com/item
Buy Example Product Again - https://example.com/item
RECOMMENDED VIDEOS
Useful Related Video - https://youtu.be/abc123
DISCLAIMER: Educational information only.
"""


def make_db(path: Path, video_id="vid1", description=""):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE videos(video_id TEXT PRIMARY KEY, description TEXT)")
    con.execute("INSERT INTO videos(video_id,description) VALUES(?,?)", (video_id, description))
    con.commit()
    return con


def test_description_cleanup_first_run_and_db_persistence(tmp_path):
    folder = tmp_path / "Channel" / "Video"
    data = folder / "_data"
    data.mkdir(parents=True)
    source = data / "vid1.description"
    source.write_text(SAMPLE, encoding="utf-8")
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    con = make_db(tmp_path / "db.sqlite")
    try:
        result = dc.cleanup_video_description(folder, "vid1", con=con)
        assert result["ok"] is True
        assert result["status"] == "COMPLETE"
        assert result["url_count"] == 3
        assert result["duplicate_url_group_count"] == 1
        assert (data / "description.txt_raw").read_text(encoding="utf-8") == SAMPLE
        cleaned = (data / "description.txt").read_text(encoding="utf-8")
        assert cleaned.count("https://example.com/item") >= 2
        assert "https://youtu.be/abc123" in cleaned
        assert cleaned.count("Educational information only.") == 1
        assert (data / "description.html").is_file()
        stored = con.execute("SELECT description FROM videos WHERE video_id='vid1'").fetchone()[0]
        assert stored == cleaned
        assert hashlib.sha256(source.read_bytes()).hexdigest() == original_hash
    finally:
        con.close()


def test_description_cleanup_idempotent_and_raw_immutable(tmp_path):
    folder = tmp_path / "Video"
    data = folder / "_data"; data.mkdir(parents=True)
    (data / "vid1.description").write_text(SAMPLE, encoding="utf-8")
    con = make_db(tmp_path / "db.sqlite")
    try:
        first = dc.cleanup_video_description(folder, "vid1", con=con)
        raw = data / "description.txt_raw"
        raw_hash = hashlib.sha256(raw.read_bytes()).hexdigest()
        clean_hash = hashlib.sha256((data / "description.txt").read_bytes()).hexdigest()
        # Mutate the retained yt-dlp sidecar; immutable canonical raw remains authority on rerun.
        (data / "vid1.description").write_text("CHANGED SOURCE SHOULD NOT REPLACE RAW", encoding="utf-8")
        second = dc.cleanup_video_description(folder, "vid1", con=con)
        assert first["description"] == second["description"]
        assert hashlib.sha256(raw.read_bytes()).hexdigest() == raw_hash
        assert hashlib.sha256((data / "description.txt").read_bytes()).hexdigest() == clean_hash
    finally:
        con.close()


def test_description_cleanup_missing_is_safe_skip(tmp_path):
    folder = tmp_path / "Video"; folder.mkdir()
    result = dc.cleanup_video_description(folder, "vid1")
    assert result == {"ok": True, "status": "SKIPPED", "reason": "description missing", "video_id": "vid1"}


def test_description_cleanup_safety_failure_does_not_overwrite_existing_clean(tmp_path, monkeypatch):
    folder = tmp_path / "Video"; data = folder / "_data"; data.mkdir(parents=True)
    (data / "vid1.description").write_text(SAMPLE, encoding="utf-8")
    existing = data / "description.txt"; existing.write_text("SAFE OLD VALUE\n", encoding="utf-8")
    monkeypatch.setattr(dc, "_url_occurrence_check", lambda parsed, rendered: ["forced failure"])
    result = dc.cleanup_video_description(folder, "vid1")
    assert result["ok"] is False
    assert existing.read_text(encoding="utf-8") == "SAFE OLD VALUE\n"


def test_comments_source_info_json_is_excluded_and_metadata_priority_is_deterministic(tmp_path):
    folder = tmp_path / "Video"; data = folder / "_data"; data.mkdir(parents=True)
    (data / "vid1.comments_source.info.json").write_text('{"title":"COMMENTS"}', encoding="utf-8")
    normal = data / "vid1.info.json"; normal.write_text('{"title":"NORMAL"}', encoding="utf-8")
    canonical = folder / "metadata.info.json"; canonical.write_text('{"title":"CANONICAL"}', encoding="utf-8")
    row = {"video_id":"vid1", "local_folder":str(folder)}
    selected = find_retained_info_json(row)
    assert selected == canonical
    canonical.unlink()
    selected = find_retained_info_json(row)
    assert selected == normal
    normal.unlink()
    assert find_retained_info_json(row) is None


def test_gui_checkbox_wires_all_three_local_cleanup_branches():
    src = (Path(__file__).parents[1] / "app" / "app.py").read_text(encoding="utf-8")
    assert "Clean up duplicate transcripts, metadata, and descriptions per video" in src
    assert "subtitle_cleanup:$('subtitleCleanup').checked" in src
    assert "canonical_metadata_repair:$('subtitleCleanup').checked" in src
    assert "description_cleanup:$('subtitleCleanup').checked" in src


def test_description_cleanup_module_has_no_network_refresh_dependency():
    src = (Path(__file__).parents[1] / "app" / "description_cleanup.py").read_text(encoding="utf-8")
    assert "import yt_dlp" not in src
    assert "from yt_dlp" not in src
    assert "import urllib" not in src
    assert "import requests" not in src
    assert "import subprocess" not in src


def test_package_consumers_use_canonical_description_gate_and_strict_package_stays_isolated():
    app_src = (Path(__file__).parents[1] / "app" / "app.py").read_text(encoding="utf-8")
    builder_src = (Path(__file__).parents[1] / "app" / "chatgpt_package_builder.py").read_text(encoding="utf-8")
    assert "desc=canonical_clean_description(str(vid),desc or \"\")" in app_src
    assert "DESCRIPTION: {canonical_clean_description(vid,d.get('description') or '')[:8000]}" in app_src
    assert '"description":canonical_clean_description(vid,doc.get("description") or "")[:8000]' in app_src
    assert '"description",' in builder_src


def test_canonical_description_gate_runs_cleanup_on_demand(tmp_path, monkeypatch):
    from app import app as application

    folder = tmp_path / "Video"; data = folder / "_data"; data.mkdir(parents=True)
    (data / "vid1.description").write_text(SAMPLE, encoding="utf-8")
    db_path = tmp_path / "db.sqlite"
    seed = make_db(db_path, description="STALE DB")
    seed.close()

    monkeypatch.setattr(application, "library_has_video", lambda vid: (True, str(folder)))
    monkeypatch.setattr(application, "db_connect", lambda: sqlite3.connect(db_path))
    cleaned = application.canonical_clean_description("vid1", "fallback")
    assert "https://example.com/item" in cleaned
    con = sqlite3.connect(db_path)
    try:
        assert con.execute("SELECT description FROM videos WHERE video_id='vid1'").fetchone()[0] == cleaned
    finally:
        con.close()


def test_repair_job_combines_three_local_cleanup_branches_without_online_refresh(tmp_path, monkeypatch):
    from app import app as application

    folder = tmp_path / "Video"; data = folder / "_data"; data.mkdir(parents=True)
    (data / "vid1.description").write_text(SAMPLE, encoding="utf-8")
    db_path = tmp_path / "db.sqlite"
    con = sqlite3.connect(db_path)
    con.execute("""CREATE TABLE videos(
        video_id TEXT PRIMARY KEY,url TEXT,original_title TEXT,upload_date TEXT,
        subtitle_source TEXT,subtitle_lang TEXT,subtitle_base_lang TEXT,
        archived INTEGER DEFAULT 0,current_present INTEGER DEFAULT 1,description TEXT
    )""")
    con.execute("INSERT INTO videos(video_id,url,original_title,upload_date,description) VALUES(?,?,?,?,?)",
                ("vid1","https://www.youtube.com/watch?v=vid1","Title","20260908","OLD"))
    con.commit(); con.close()

    monkeypatch.setattr(application, "BASE", tmp_path)
    monkeypatch.setattr(application, "db_connect", lambda: sqlite3.connect(db_path))
    monkeypatch.setattr(application, "library_has_video", lambda vid: (True, str(folder)))
    monkeypatch.setattr(application, "canonicalize_video_subtitle_artifacts", lambda *a, **k: {"ok":True,"changed":True,"winner":"x.vtt"})
    monkeypatch.setattr(application, "metadata_via_youtube_api", lambda *a, **k: (_ for _ in ()).throw(AssertionError("online refresh must not run")))
    monkeypatch.setattr(application, "run_existing_library_metadata_migration", lambda con, **kwargs: {
        "processed":1,"migrated":1,"skipped_current":0,"complete_with_warnings":0,"failed":0,
        "backup_path":str(kwargs.get("backup_path") or ""),"videos":[{"video_id":"vid1","status":"COMPLETE"}]
    })
    monkeypatch.setattr(application, "export_csv", lambda: None)
    monkeypatch.setattr(application, "build_library_indexes", lambda: None)
    result = application.repair_selected_video_data({
        "video_ids":"vid1","metadata":False,"transcripts":False,
        "subtitle_cleanup":True,"canonical_metadata_repair":True,"description_cleanup":True,
        "comments":False,"reports":False,"chatgpt_packages":False,"knowledge_ai":False
    })
    assert result["metadata"] == 0
    assert result["canonical_metadata_repair"]["migrated"] == 1
    assert result["subtitle_cleanup"]["cleaned"] == 1
    assert result["description_cleanup"]["cleaned"] == 1
    assert result["description_cleanup"]["failed"] == 0


def test_description_cleanup_removes_obsolete_root_copies_after_validated_data_outputs(tmp_path):
    folder = tmp_path / "Video"
    data = folder / "_data"; data.mkdir(parents=True)
    # Normal retained source and metadata must survive cleanup.
    (data / "vid1.description").write_text(SAMPLE, encoding="utf-8")
    metadata = folder / "metadata.info.json"
    metadata.write_text('{"id":"vid1"}', encoding="utf-8")

    # Legacy copies from the older location.
    legacy_raw = folder / "description.txt_raw"
    legacy_text = folder / "description.txt"
    legacy_html = folder / "description.html"
    legacy_raw.write_text(SAMPLE, encoding="utf-8")
    legacy_text.write_text("OLD CLEANED\n", encoding="utf-8")
    legacy_html.write_text("<html>OLD</html>", encoding="utf-8")

    result = dc.cleanup_video_description(folder, "vid1")
    assert result["ok"] is True
    assert result["legacy_root_cleanup"]["found"] == 3
    assert result["legacy_root_cleanup"]["deleted"] == 3
    assert result["legacy_root_cleanup"]["preserved"] == 0

    assert (data / "description.txt_raw").is_file()
    assert (data / "description.txt").is_file()
    assert (data / "description.html").is_file()
    assert not legacy_raw.exists()
    assert not legacy_text.exists()
    assert not legacy_html.exists()
    assert metadata.is_file(), "metadata.info.json in video root must be preserved"
    assert (data / "vid1.description").is_file(), "retained yt-dlp description source must be preserved"


def test_description_cleanup_root_cleanup_is_idempotent(tmp_path):
    folder = tmp_path / "Video"
    data = folder / "_data"; data.mkdir(parents=True)
    (data / "vid1.description").write_text(SAMPLE, encoding="utf-8")
    (folder / "description.txt_raw").write_text(SAMPLE, encoding="utf-8")
    (folder / "description.txt").write_text("OLD\n", encoding="utf-8")
    (folder / "description.html").write_text("OLD", encoding="utf-8")

    first = dc.cleanup_video_description(folder, "vid1")
    second = dc.cleanup_video_description(folder, "vid1")
    assert first["legacy_root_cleanup"]["deleted"] == 3
    assert second["legacy_root_cleanup"] == {"found": 0, "deleted": 0, "preserved": 0, "files": []}


def test_description_cleanup_safety_failure_preserves_legacy_root_files(tmp_path, monkeypatch):
    folder = tmp_path / "Video"
    data = folder / "_data"; data.mkdir(parents=True)
    (data / "vid1.description").write_text(SAMPLE, encoding="utf-8")
    for name in ("description.txt_raw", "description.txt", "description.html"):
        (folder / name).write_text("LEGACY", encoding="utf-8")
    monkeypatch.setattr(dc, "_url_occurrence_check", lambda parsed, rendered: ["forced failure"])
    result = dc.cleanup_video_description(folder, "vid1")
    assert result["ok"] is False
    for name in ("description.txt_raw", "description.txt", "description.html"):
        assert (folder / name).exists(), f"{name} must remain when canonical validation fails"
