import json
import sqlite3
from pathlib import Path


def test_phase9_all_new_architecture_modules_import_cleanly():
    from app import metadata_schema  # noqa: F401
    from app import metadata_normalization  # noqa: F401
    from app import metadata_persistence  # noqa: F401
    from app import source_tags  # noqa: F401
    from app import source_chapters  # noqa: F401
    from app import transcript_evidence  # noqa: F401
    from app import chatgpt_package_builder  # noqa: F401
    from app import metadata_migration  # noqa: F401
    from app import legacy_metadata  # noqa: F401


def test_phase9_package_contract_rejects_nested_forbidden_material():
    from app.chatgpt_package_builder import assert_strict_package_contract

    payload = {
        "video_id": "v1",
        "package_grade": "A",
        "metadata": {
            "id": "v1",
            "original_title": "Original",
            "clean_title": "Clean",
            "channel": "Channel",
            "upload_date": "2026-01-01",
            "duration_seconds": 10.0,
            "webpage_url": "https://youtu.be/v1",
            "availability": "public",
            "category": "Education",
        },
        "auxiliary_metadata": {"source_chapters": [], "source_tags": []},
        "transcript_provenance": {"health": {"grade": "A"}},
        "requested_features": [],
        "evidence": {
            "canonical_transcript": {},
            "manifest": {},
            "assessment": {"nested": {"description": "must not leak"}},
        },
    }
    try:
        assert_strict_package_contract(payload)
    except ValueError as exc:
        assert "Forbidden package key leaked" in str(exc)
    else:
        raise AssertionError("nested forbidden material was not rejected")


def test_phase9_grade_contract_is_consistent_end_to_end():
    from app.transcript_evidence import (
        EVIDENCE_GRADES,
        normal_transcript_package_eligible,
        normalize_evidence_grade,
        repair_routing_for_grade,
    )

    assert EVIDENCE_GRADES == ("A", "B", "C", "D", "F")
    assert {g: normal_transcript_package_eligible(g) for g in EVIDENCE_GRADES} == {
        "A": True, "B": True, "C": True, "D": False, "F": False
    }
    assert normalize_evidence_grade("E") == "F"
    assert repair_routing_for_grade("D") == "REPAIR_RECOMMENDED"
    assert repair_routing_for_grade("F") == "REPAIR_REQUIRED"


def test_phase9_canonical_db_reader_works_without_info_json(tmp_path):
    from app.metadata_schema import apply_video_schema_migrations
    from app.legacy_metadata import resolve_legacy_metadata

    con = sqlite3.connect(tmp_path / "library.db")
    con.execute("""
        CREATE TABLE videos(
          video_id TEXT PRIMARY KEY,url TEXT,original_title TEXT,clean_title TEXT,
          channel TEXT,upload_date TEXT,description TEXT,youtube_category_name TEXT,
          duration_seconds REAL
        )
    """)
    apply_video_schema_migrations(con)
    folder = tmp_path / "video"
    folder.mkdir()
    con.execute(
        "INSERT INTO videos(video_id,url,original_title,clean_title,channel,upload_date,description,youtube_category_name,duration_seconds,availability,metadata_schema_version,metadata_migration_status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        ("v1", "https://youtu.be/v1", "Original", "Clean", "Channel", "2026-01-01", "Local only", "Education", 120.0, "public", 1, "COMPLETE"),
    )
    con.commit()
    resolved = resolve_legacy_metadata(con, "v1", folder)
    assert resolved["_sources"] == ["sqlite"]
    assert resolved["original_title"] == "Original"
    assert resolved["youtube_category_name"] == "Education"
    assert not list(folder.rglob("*.info.json"))
    con.close()


def test_phase9_source_chapter_and_tag_contracts_remain_separate():
    from app.source_chapters import normalize_source_chapters, apply_navigation_enhancements
    from app.source_tags import clean_source_tags

    chapters = normalize_source_chapters([
        {"start_time": 0, "end_time": 30, "title": "Intro"},
        {"start_time": 30, "end_time": 60, "title": "Sponsor"},
    ])
    enhanced = apply_navigation_enhancements(chapters, display_titles={0: "Introduction"})
    assert enhanced[0]["source_title"] == "Intro"
    assert enhanced[0]["display_title"] == "Introduction"
    assert enhanced[1]["source_title"] == "Sponsor"

    cleaned = clean_source_tags(["health", "BUY NOW", "health", "nutrition"])
    assert cleaned["raw"] == ["health", "BUY NOW", "nutrition"]
    assert "health" in cleaned["cleaned"] and "nutrition" in cleaned["cleaned"]
    assert "BUY NOW" not in cleaned["cleaned"]


def test_phase9_no_duplicate_authoritative_implementation_in_app_py():
    app_text = (Path(__file__).parents[1] / "app" / "app.py").read_text(encoding="utf-8")
    # These responsibilities must remain module-owned rather than being copied back into app.py.
    forbidden_defs = [
        "def normalize_extractor_metadata(",
        "def persist_canonical_metadata(",
        "def clean_source_tags(",
        "def normalize_source_chapters(",
        "def normalize_evidence_grade(",
        "def build_video_payload(",
        "def run_existing_library_metadata_migration(",
        "def resolve_legacy_metadata(",
    ]
    for signature in forbidden_defs:
        assert signature not in app_text, signature
