import json
from pathlib import Path

import pytest

from app.metadata_normalization import (
    CANONICAL_METADATA_SCHEMA_VERSION,
    TEMPORARY_TECHNICAL_FIELDS,
    flattened_persistence_view,
    normalize_extractor_metadata,
    normalize_source_chapters,
)


def test_normalizer_classifies_core_aux_local_and_does_not_copy_technical_fields():
    raw = {
        "id": "abc123",
        "title": "Example title",
        "webpage_url": "https://www.youtube.com/watch?v=abc123",
        "channel": "Example Channel",
        "uploader": "Redundant Uploader",
        "upload_date": "20260908",
        "duration": 603,
        "availability": "public",
        "categories": ["Howto & Style"],
        "tags": ["Health", "health", " useful tag "],
        "chapters": [{"start_time": 0, "end_time": 60, "title": "Intro"}],
        "description": "local only description",
        "channel_id": "UC123",
        "channel_is_verified": True,
        "view_count": 100,
        "filesize_approx": 123456,
        "formats": [{"format_id": "137", "url": "https://temporary.example"}],
        "acodec": "opus",
        "vcodec": "av01",
        "protocol": "https",
    }

    normalized = normalize_extractor_metadata(raw)

    assert normalized["metadata_schema_version"] == CANONICAL_METADATA_SCHEMA_VERSION
    assert normalized["llm_core"] == {
        "id": "abc123",
        "original_title": "Example title",
        "channel": "Example Channel",
        "upload_date": "20260908",
        "duration_seconds": 603.0,
        "webpage_url": "https://www.youtube.com/watch?v=abc123",
        "availability": "public",
        "category": "Howto & Style",
    }
    assert normalized["llm_auxiliary"]["source_tags_raw"] == ["Health", "useful tag"]
    assert normalized["llm_auxiliary"]["source_chapters"][0]["source_title"] == "Intro"
    assert normalized["llm_auxiliary"]["source_chapters"][0]["display_title"] == ""
    assert normalized["local_only"]["description"] == "local only description"
    assert normalized["local_only"]["filesize_approx"] == 123456
    assert normalized["local_only"]["view_count"] == 100
    assert normalized["temporary_technical_fields_present"] == ["acodec", "formats", "protocol", "vcodec"]

    serialized = json.dumps(normalized, ensure_ascii=False)
    assert "https://temporary.example" not in serialized
    assert '"formats"' not in normalized


def test_category_reuses_youtube_category_name_before_raw_categories():
    raw = {
        "id": "x",
        "title": "x",
        "youtube_category_name": "Education",
        "source_category": "People & Blogs",
        "categories": ["Howto & Style"],
    }
    normalized = normalize_extractor_metadata(raw)
    assert normalized["llm_core"]["category"] == "Education"
    assert normalized["local_only"]["categories"] == ["Howto & Style"]
    persistence = flattened_persistence_view(normalized)
    assert persistence["youtube_category_name"] == "Education"


def test_source_chapters_preserve_source_title_and_timestamps_without_semantic_rewrite():
    chapters = normalize_source_chapters([
        {"start_time": 0, "end_time": 52, "title": "<Untitled Chapter 1>"},
        {"start_time": "52", "end_time": "141", "title": "Benefits"},
        {"junk": "ignored"},
    ])
    assert chapters == [
        {"start_seconds": 0.0, "end_seconds": 52.0, "source_title": "<Untitled Chapter 1>", "display_title": ""},
        {"start_seconds": 52.0, "end_seconds": 141.0, "source_title": "Benefits", "display_title": ""},
    ]


def test_missing_optional_metadata_is_safe_and_fallback_identity_is_used():
    normalized = normalize_extractor_metadata({}, fallback={
        "id": "fallback-id",
        "title": "Fallback title",
        "channel": "Fallback channel",
        "url": "https://youtu.be/fallback-id",
    })
    assert normalized["llm_core"]["id"] == "fallback-id"
    assert normalized["llm_core"]["original_title"] == "Fallback title"
    assert normalized["llm_core"]["channel"] == "Fallback channel"
    assert normalized["llm_core"]["webpage_url"] == "https://youtu.be/fallback-id"
    assert normalized["llm_auxiliary"] == {"source_chapters": [], "source_tags_raw": [], "source_tags_cleaned": []}
    assert normalized["local_only"]["filesize_approx"] is None


def test_normalizer_rejects_non_mapping_inputs():
    with pytest.raises(TypeError):
        normalize_extractor_metadata(["not", "a", "mapping"])
    with pytest.raises(TypeError):
        normalize_extractor_metadata({}, fallback=["not", "a", "mapping"])


def test_technical_field_inventory_contains_expected_high_bloat_fields():
    expected = {"formats", "acodec", "vcodec", "protocol", "fps", "abr", "vbr", "tbr"}
    assert expected.issubset(TEMPORARY_TECHNICAL_FIELDS)


def test_phase1_schema_columns_cover_flattened_phase2_persistence_view(tmp_path):
    # Integration between Phase 1 schema ownership and Phase 2 normalized output.
    import sqlite3
    from app.metadata_schema import apply_video_schema_migrations

    db = tmp_path / "phase2.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE videos (video_id TEXT PRIMARY KEY)")
    apply_video_schema_migrations(con)
    columns = {row[1] for row in con.execute("PRAGMA table_info(videos)")}

    normalized = normalize_extractor_metadata({
        "id": "x", "title": "t", "categories": ["Education"],
        "chapters": [{"start_time": 0, "title": "Intro"}],
        "tags": ["alpha"], "filesize_approx": 42,
    })
    persistence = flattened_persistence_view(normalized)
    required_columns = {
        "availability", "source_chapters_json", "youtube_tags", "youtube_category_name",
        "channel_id", "channel_url", "uploader_id", "channel_follower_count",
        "channel_is_verified", "heatmap_json", "playlist", "playlist_id",
        "playlist_title", "playlist_index", "playlist_count", "playlist_channel",
        "playlist_channel_id", "playlist_uploader", "playlist_uploader_id",
        "playlist_webpage_url", "language", "is_live", "was_live", "live_status",
        "filesize_approx", "metadata_schema_version",
    }
    assert required_columns.issubset(columns)
    assert persistence["youtube_category_name"] == "Education"
    assert persistence["filesize_approx"] == 42
    con.close()
