import json
import sqlite3
from pathlib import Path

from app.metadata_normalization import normalize_extractor_metadata
from app.metadata_persistence import (
    attach_canonical_metadata,
    canonical_metadata_from_info_json,
    persist_canonical_metadata,
)
from app.metadata_schema import apply_video_schema_migrations


def _db():
    con = sqlite3.connect(":memory:")
    con.execute(
        """CREATE TABLE videos(
             video_id TEXT PRIMARY KEY,
             youtube_tags TEXT,
             youtube_category_name TEXT,
             thumbnail_url TEXT,
             duration_seconds REAL DEFAULT 0,
             view_count INTEGER,
             like_count INTEGER,
             comment_count INTEGER
           )"""
    )
    apply_video_schema_migrations(con)
    con.execute("INSERT INTO videos(video_id) VALUES('v1')")
    return con


def test_phase3_persists_rich_canonical_metadata():
    con = _db()
    normalized = normalize_extractor_metadata({
        "id": "v1",
        "title": "Example",
        "webpage_url": "https://www.youtube.com/watch?v=v1",
        "channel": "Channel",
        "duration": 123.5,
        "availability": "public",
        "categories": ["Education"],
        "tags": ["alpha", "beta"],
        "chapters": [{"start_time": 0, "end_time": 50, "title": "Intro"}],
        "channel_id": "UC123",
        "channel_url": "https://www.youtube.com/channel/UC123",
        "channel_follower_count": 42,
        "channel_is_verified": True,
        "heatmap": [{"start_time": 0, "end_time": 10, "value": 0.9}],
        "playlist_id": "PL1",
        "playlist_title": "Playlist",
        "language": "en-US",
        "is_live": False,
        "was_live": True,
        "live_status": "was_live",
        "filesize_approx": 9999,
        "thumbnail": "https://i.ytimg.com/example.jpg",
        "view_count": 100,
        "like_count": 10,
        "comment_count": 2,
    })
    persist_canonical_metadata(con, "v1", normalized)
    row = con.execute(
        """SELECT availability,duration_seconds,source_chapters_json,youtube_tags,youtube_category_name,
                  channel_id,channel_url,channel_follower_count,channel_is_verified,heatmap_json,
                  playlist_id,playlist_title,language,is_live,was_live,live_status,filesize_approx,
                  thumbnail_url,view_count,like_count,comment_count,metadata_schema_version
             FROM videos WHERE video_id='v1'"""
    ).fetchone()
    assert row[0] == "public"
    assert row[1] == 123.5
    assert json.loads(row[2])[0]["source_title"] == "Intro"
    assert json.loads(row[3]) == ["alpha", "beta"]
    assert row[4] == "Education"
    assert row[5:9] == ("UC123", "https://www.youtube.com/channel/UC123", 42, 1)
    assert len(json.loads(row[9])) == 1
    assert row[10:13] == ("PL1", "Playlist", "en-US")
    assert row[13:17] == (0, 1, "was_live", 9999)
    assert row[17:21] == ("https://i.ytimg.com/example.jpg", 100, 10, 2)
    assert row[21] == 1
    con.close()


def test_phase3_sparse_refresh_preserves_richer_existing_metadata():
    con = _db()
    rich = normalize_extractor_metadata({
        "id": "v1", "title": "Rich", "availability": "public",
        "categories": ["Education"], "tags": ["alpha"],
        "chapters": [{"start_time": 0, "title": "Source chapter"}],
        "heatmap": [{"value": 1}], "playlist_id": "PL1", "filesize_approx": 500,
        "channel_id": "UC1", "was_live": True,
    })
    persist_canonical_metadata(con, "v1", rich)

    sparse = normalize_extractor_metadata({
        "id": "v1", "title": "Sparse", "categories": ["Education"], "tags": []
    })
    persist_canonical_metadata(con, "v1", sparse)

    row = con.execute(
        "SELECT availability,source_chapters_json,youtube_tags,heatmap_json,playlist_id,filesize_approx,channel_id,was_live FROM videos WHERE video_id='v1'"
    ).fetchone()
    assert row[0] == "public"
    assert json.loads(row[1])[0]["source_title"] == "Source chapter"
    assert json.loads(row[2]) == ["alpha"]
    assert json.loads(row[3]) == [{"value": 1}]
    assert row[4:] == ("PL1", 500, "UC1", 1)
    con.close()


def test_phase3_info_json_helper_uses_raw_rich_fields(tmp_path):
    info = tmp_path / "v1.info.json"
    info.write_text(json.dumps({
        "id": "v1", "title": "Raw title", "duration": 77,
        "webpage_url": "https://youtu.be/v1", "categories": ["Howto & Style"],
        "chapters": [{"start_time": 5, "end_time": 20, "title": "Part"}],
        "tags": ["tag1"], "filesize_approx": 1234,
        "formats": [{"url": "https://googlevideo.com/temp"}],
    }), encoding="utf-8")
    normalized = canonical_metadata_from_info_json(info, fallback={"channel": "Fallback"})
    assert normalized["llm_core"]["duration_seconds"] == 77.0
    assert normalized["llm_core"]["channel"] == "Fallback"
    assert normalized["llm_auxiliary"]["source_chapters"][0]["source_title"] == "Part"
    assert normalized["local_only"]["filesize_approx"] == 1234
    assert "googlevideo.com" not in json.dumps(normalized)


def test_phase3_attach_prefers_enriched_record_but_keeps_raw_only_fields():
    raw = {
        "id": "v1", "title": "yt-dlp title", "categories": ["People & Blogs"],
        "chapters": [{"start_time": 0, "title": "Raw chapter"}], "channel_id": "UCraw",
    }
    enriched = {
        "id": "v1", "title": "API title", "youtube_category_name": "Education",
        "view_count": 9,
    }
    out = attach_canonical_metadata(enriched, raw=raw)
    norm = out["_canonical_metadata"]
    assert norm["llm_core"]["original_title"] == "API title"
    assert norm["llm_core"]["category"] == "Education"
    assert norm["llm_auxiliary"]["source_chapters"][0]["source_title"] == "Raw chapter"
    assert norm["local_only"]["channel_id"] == "UCraw"
    assert norm["local_only"]["view_count"] == 9


def test_phase3_save_metadata_integration_persists_canonical_fields(tmp_path, monkeypatch):
    from app import app

    db = tmp_path / "video_library.db"
    monkeypatch.setattr(app, "DB", db)
    record = attach_canonical_metadata({
        "id": "v1", "url": "https://youtu.be/v1", "title": "Title", "channel": "Channel",
        "upload_date": "20260908", "description": "desc", "platform": "YouTube",
        "metadata_source": "yt-dlp", "source_category": "Education",
        "source_categories": ["Education"], "youtube_tags": ["one"],
        "subtitle_source": "auto", "subtitle_lang": "en", "subtitle_base_lang": "en",
    }, raw={
        "id": "v1", "title": "Title", "webpage_url": "https://youtu.be/v1",
        "channel": "Channel", "categories": ["Education"], "tags": ["one"],
        "chapters": [{"start_time": 0, "title": "Intro"}], "availability": "public",
        "filesize_approx": 321,
    })
    app.save_metadata([record])
    con = app.db_connect()
    try:
        row = con.execute(
            "SELECT availability,source_chapters_json,filesize_approx,metadata_schema_version FROM videos WHERE video_id='v1'"
        ).fetchone()
        assert row[0] == "public"
        assert json.loads(row[1])[0]["source_title"] == "Intro"
        assert row[2:] == (321, 1)
    finally:
        con.close()


def test_phase3_info_json_persist_helper_updates_database(tmp_path):
    from app.metadata_persistence import persist_info_json_canonical_metadata

    con = _db()
    info = tmp_path / "v1.info.json"
    info.write_text(json.dumps({
        "id": "v1", "title": "Title", "duration": 88,
        "categories": ["Education"], "availability": "public",
        "chapters": [{"start_time": 1, "title": "Chapter"}], "filesize_approx": 654,
    }), encoding="utf-8")
    persist_info_json_canonical_metadata(con, "v1", info)
    row = con.execute(
        "SELECT availability,duration_seconds,source_chapters_json,filesize_approx FROM videos WHERE video_id='v1'"
    ).fetchone()
    assert row[0:2] == ("public", 88.0)
    assert json.loads(row[2])[0]["source_title"] == "Chapter"
    assert row[3] == 654
    con.close()


def test_phase3_youtube_api_rows_attach_canonical_channel_and_availability(monkeypatch):
    from app import app

    def fake_get(resource, params):
        assert resource == "videos"
        return {"items": [{
            "id": "v1",
            "snippet": {
                "title": "API Title", "channelTitle": "Channel", "channelId": "UC123",
                "publishedAt": "2026-09-08T00:00:00Z", "description": "Desc",
                "categoryId": "27", "tags": ["one"], "thumbnails": {},
            },
            "contentDetails": {"duration": "PT1M"},
            "statistics": {"viewCount": "10", "likeCount": "2", "commentCount": "1"},
            "status": {"privacyStatus": "public"},
        }]}

    monkeypatch.setattr(app, "youtube_api_get", fake_get)
    monkeypatch.setattr(app, "youtube_category_titles", lambda ids: {"27": "Education"})
    monkeypatch.setattr(app, "set_state", lambda **kwargs: None)
    monkeypatch.setattr(app, "console_progress", lambda *args, **kwargs: None)

    rows = app.youtube_api_video_metadata(["v1"])
    assert len(rows) == 1
    row = rows[0]
    assert row["channel_id"] == "UC123"
    assert row["channel_url"].endswith("/UC123")
    assert row["availability"] == "public"
    canonical = row["_canonical_metadata"]
    assert canonical["llm_core"]["category"] == "Education"
    assert canonical["llm_core"]["availability"] == "public"
    assert canonical["local_only"]["channel_id"] == "UC123"
