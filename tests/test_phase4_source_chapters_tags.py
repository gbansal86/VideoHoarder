import json
import sqlite3
from copy import deepcopy

import pytest

from app.metadata_normalization import normalize_extractor_metadata
from app.metadata_persistence import persist_canonical_metadata
from app.metadata_schema import apply_video_schema_migrations
from app.source_chapters import (
    apply_navigation_enhancements,
    build_navigation_structure,
    effective_chapter_title,
    normalize_source_chapters,
)
from app.source_tags import clean_source_tags, junk_reason


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


def test_phase4_tag_cleaner_is_conservative_and_auditable():
    result = clean_source_tags([
        "#Moringa", "moringa", "Dabur Chyawanprash", "Best natural mascara",
        "Subscribe to my channel", "USE CODE FIT20", "link in description",
        "https://example.com/deal", "Fit Tuber Makeup",
    ])
    assert result["raw"][0] == "Moringa"
    assert result["cleaned"] == [
        "Moringa", "Dabur Chyawanprash", "Best natural mascara", "Fit Tuber Makeup"
    ]
    reasons = {x["tag"]: x["reason"] for x in result["removed"]}
    assert reasons["Subscribe to my channel"] == "subscribe_prompt"
    assert reasons["USE CODE FIT20"] == "coupon"
    assert reasons["link in description"] == "purchase_bait"
    assert reasons["https://example.com/deal"] == "url"
    # Do not over-clean legitimate potentially-clickbaity vocabulary.
    assert junk_reason("best natural mascara") == ""
    assert junk_reason("free ai tools") == ""


def test_phase4_normalizer_keeps_raw_and_cleaned_source_tags_separate():
    normalized = normalize_extractor_metadata({
        "id": "v1", "title": "Title",
        "tags": ["Ayurveda", "subscribe now", "Dabur Honey"],
    })
    aux = normalized["llm_auxiliary"]
    assert aux["source_tags_raw"] == ["Ayurveda", "subscribe now", "Dabur Honey"]
    assert aux["source_tags_cleaned"] == ["Ayurveda", "Dabur Honey"]
    assert normalized["local_only"]["source_tags_removed"] == [
        {"tag": "subscribe now", "reason": "subscribe_prompt"}
    ]


def test_phase4_source_chapter_enhancement_never_overwrites_source_title_or_timestamps():
    source = normalize_source_chapters([
        {"start_time": 0, "end_time": 60, "title": "Benefits"},
        {"start_time": 60, "end_time": 120, "title": "Products"},
    ])
    before = deepcopy(source)
    enhanced = apply_navigation_enhancements(
        source,
        display_titles={0: "Key Health Benefits"},
        subchapters={0: [
            {"start_seconds": 10, "end_seconds": 25, "title": "Digestive Benefits"},
            {"start_seconds": 30, "end_seconds": 45, "title": "Who Should Avoid It"},
        ]},
    )
    assert source == before  # caller/source object is not mutated
    assert enhanced[0]["source_title"] == "Benefits"
    assert enhanced[0]["display_title"] == "Key Health Benefits"
    assert enhanced[0]["start_seconds"] == 0.0
    assert enhanced[0]["end_seconds"] == 60.0
    assert len(enhanced[0]["subchapters"]) == 2
    assert effective_chapter_title(enhanced[0]) == "Key Health Benefits"
    assert effective_chapter_title(enhanced[1]) == "Products"


def test_phase4_subchapters_must_stay_inside_parent_boundary():
    source = [{"start_time": 10, "end_time": 20, "title": "Parent"}]
    with pytest.raises(ValueError):
        apply_navigation_enhancements(
            source,
            subchapters={0: [{"start_seconds": 9, "title": "Too early"}]},
        )
    with pytest.raises(ValueError):
        apply_navigation_enhancements(
            source,
            subchapters={0: [{"start_seconds": 15, "end_seconds": 21, "title": "Too late"}]},
        )


def test_phase4_navigation_prefers_source_chapters_and_uses_semantic_only_when_missing():
    with_source = build_navigation_structure(
        [{"start_time": 0, "end_time": 10, "title": "Source"}],
        semantic_chapters_if_missing=[{"start_seconds": 1, "title": "Semantic"}],
    )
    assert with_source["basis"] == "source_chapters"
    assert with_source["chapters"][0]["source_title"] == "Source"

    without_source = build_navigation_structure(
        [], semantic_chapters_if_missing=[{"start_seconds": 1, "end_seconds": 9, "title": "Semantic"}]
    )
    assert without_source == {
        "basis": "semantic_transcript_fallback",
        "chapters": [{"start_seconds": 1.0, "end_seconds": 9.0, "title": "Semantic"}],
    }


def test_phase4_cleaned_tags_persist_separately_and_sparse_refresh_preserves_them():
    con = _db()
    first = normalize_extractor_metadata({
        "id": "v1", "title": "Title",
        "tags": ["Moringa", "subscribe now", "Dabur Honey"],
    })
    persist_canonical_metadata(con, "v1", first)
    raw_json, cleaned_json = con.execute(
        "SELECT youtube_tags,youtube_tags_cleaned FROM videos WHERE video_id='v1'"
    ).fetchone()
    assert json.loads(raw_json) == ["Moringa", "subscribe now", "Dabur Honey"]
    assert json.loads(cleaned_json) == ["Moringa", "Dabur Honey"]

    sparse = normalize_extractor_metadata({"id": "v1", "title": "Sparse", "tags": []})
    persist_canonical_metadata(con, "v1", sparse)
    raw_json2, cleaned_json2 = con.execute(
        "SELECT youtube_tags,youtube_tags_cleaned FROM videos WHERE video_id='v1'"
    ).fetchone()
    assert raw_json2 == raw_json
    assert cleaned_json2 == cleaned_json
    con.close()


def test_phase4_realistic_source_chapter_sponsor_title_is_preserved_not_deleted():
    chapters = normalize_source_chapters([
        {"start_time": 537, "end_time": 603, "title": "Segment Partner - Mamaearth Vitamin C Face wash and Face mask"}
    ])
    assert chapters[0]["source_title"].startswith("Segment Partner")
    assert chapters[0]["display_title"] == ""
