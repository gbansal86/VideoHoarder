import copy
import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

from app.transcript_evidence import (
    EVIDENCE_GRADES,
    evidence_grade_from_transcript_health,
    normal_transcript_package_eligible,
    normalize_evidence_grade,
    repair_routing_for_grade,
)


def _healthy_transcript():
    return "\n".join(
        f"[00:{n:02d}] useful spoken transcript line {n} with enough words for stable grading"
        for n in range(60)
    )


def test_phase5_canonical_grade_vocabulary_and_legacy_e_mapping():
    assert EVIDENCE_GRADES == ("A", "B", "C", "D", "F")
    assert normalize_evidence_grade("E") == "F"
    assert normalize_evidence_grade("z") == "F"
    assert normal_transcript_package_eligible("A")
    assert normal_transcript_package_eligible("B")
    assert normal_transcript_package_eligible("C")
    assert not normal_transcript_package_eligible("D")
    assert not normal_transcript_package_eligible("F")
    assert repair_routing_for_grade("D") == "REPAIR_RECOMMENDED"
    assert repair_routing_for_grade("F") == "REPAIR_REQUIRED"


def test_phase5_evidence_grade_comes_only_from_transcript_health():
    assert evidence_grade_from_transcript_health({"grade": "A"}, transcript_available=True) == "A"
    assert evidence_grade_from_transcript_health({"grade": "C"}, transcript_available=True) == "C"
    assert evidence_grade_from_transcript_health({"grade": "D"}, transcript_available=True) == "D"
    assert evidence_grade_from_transcript_health({"grade": "A"}, transcript_available=False) == "F"


def test_phase5_metadata_comments_titles_do_not_change_transcript_grade_or_consistency():
    from app import app

    transcript = _healthy_transcript()
    manifest = {"timestamped_transcript": "x"}
    baseline = app.chatgpt_canonical_evidence(
        "v1",
        {
            "original_title": "Completely unrelated title alpha",
            "clean_title": "Unrelated clean title beta",
            "description": "Unrelated description gamma",
            "duration_seconds": 60,
            "source_tags": ["unrelated tag"],
            "source_chapters": [{"title": "Unrelated chapter"}],
        },
        manifest,
        transcript,
        "en",
        "viewer comment unrelated delta",
    )
    variant = app.chatgpt_canonical_evidence(
        "v1",
        {
            "original_title": "Different identity title",
            "clean_title": "Totally different clean title",
            "description": "Totally different description",
            "duration_seconds": 60,
            "source_tags": ["different tag"],
            "source_chapters": [{"title": "Different chapter"}],
        },
        manifest,
        transcript,
        "en",
        "completely different viewer comment",
    )

    assert baseline["transcript_health"]["grade"] == variant["transcript_health"]["grade"]
    assert baseline["evidence_grade"] == variant["evidence_grade"]
    assert baseline["source_consistency"] == variant["source_consistency"] == "consistent"
    assert not any("title/description" in x.lower() for x in baseline["source_conflicts"])
    assert not any("title/description" in x.lower() for x in variant["source_conflicts"])


def test_phase5_no_transcript_is_f_even_when_description_or_comments_exist():
    from app import app

    result = app.chatgpt_canonical_evidence(
        "v1",
        {"original_title": "Title", "clean_title": "Clean", "description": "Rich description", "duration_seconds": 100},
        {},
        "",
        "en",
        "Very useful viewer comment",
    )
    assert result["transcript_health"]["grade"] == "F"
    assert result["evidence_grade"] == "F"
    assert not result["transcript_available"]


def test_phase5_new_result_schema_uses_f_not_e():
    from app import app

    schema = app.chatgpt_formal_result_schema("pkg", ["title_en.v1"], False)
    grades = schema["properties"]["video_updates"]["items"]["properties"]["evidence_grade"]["enum"]
    assert grades == ["A", "B", "C", "D", "F"]
    assert "E" not in grades


def _minimal_db(path: Path):
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE videos(video_id TEXT,url TEXT,original_title TEXT,clean_title TEXT,channel TEXT,upload_date TEXT,description TEXT,source_category TEXT,youtube_category_name TEXT,comments_file TEXT,comments_transcript_file TEXT,local_folder TEXT,archived INTEGER,duration_seconds REAL,current_present INTEGER DEFAULT 1);
        CREATE TABLE chatgpt_requests(request_id TEXT PRIMARY KEY,package_id TEXT UNIQUE,mode TEXT,schema_version TEXT,prompt_version TEXT,requested_features_json TEXT,package_hash TEXT,manifest_json TEXT,created_at TEXT,status TEXT,result_path TEXT,result_hash TEXT,validation_status TEXT,applied_status TEXT,notes TEXT);
        CREATE TABLE chatgpt_request_videos(request_id TEXT,video_id TEXT,source_snapshot_hash TEXT,evidence_manifest_json TEXT,requested_features_json TEXT,PRIMARY KEY(request_id,video_id));
        CREATE TABLE video_feature_coverage(video_id TEXT,feature_id TEXT,feature_version TEXT,status TEXT,source_snapshot_hash TEXT,package_id TEXT,result_hash TEXT,evidence_coverage TEXT,completed_at TEXT,stale_reason TEXT,last_error TEXT,PRIMARY KEY(video_id,feature_id,feature_version));
        """
    )
    return con


def _assessment(grade: str):
    available = grade != "F"
    return {
        "video_id": "v1",
        "transcript_available": available,
        "transcript_source": "untimestamped_transcript" if available else "no_transcript",
        "canonical_segment_count": 0,
        "timestamps_available": False,
        "timestamp_status": "unavailable_or_unreliable" if available else "none",
        "timestamp_hints_available": False,
        "timestamp_hints_reliable": False,
        "normalization_status": "UNTIMESTAMPED_FALLBACK" if available else "NO_TRANSCRIPT",
        "transcript_characters": 1000 if available else 0,
        "transcript_words": 150 if available else 0,
        "transcript_health": {
            "grade": grade,
            "score": {"A": 95, "B": 82, "C": 65, "D": 45, "F": 10}[grade],
            "routing_class": repair_routing_for_grade(grade),
            "reason_codes": [] if grade in {"A", "B", "C"} else ["HIGH_NOISE_MARKER_RATIO"],
            "hard_failure": grade == "F",
        },
        "evidence_grade": grade,
        "source_conflicts": [],
        "canonical_transcript": {
            "segments": [],
            "untimestamped_text": "usable transcript text" if available else "",
            "timestamps_available": False,
        },
        "comments": {"included_comments": 0, "total_comments": 0, "sampling_method": "none", "records": []},
    }


def test_phase5_d_grade_is_excluded_from_normal_package_and_queued_for_repair(tmp_path):
    from app import app

    db = tmp_path / "test.db"
    con = _minimal_db(db)
    folder = tmp_path / "folder"
    folder.mkdir()
    con.execute(
        "INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("v1", "https://youtu.be/v1", "Title", "Clean", "Channel", "2026-01-01", "Description", "Education", "Education", "", "", str(folder), 0, 120, 1),
    )
    con.commit(); con.close()

    with patch.object(app, "BASE", tmp_path), \
         patch.object(app, "db_connect", side_effect=lambda: sqlite3.connect(db)), \
         patch.object(app, "artifact_manifest_for_video", return_value={"timestamped_transcript": "x"}), \
         patch.object(app, "best_transcript_for_video", return_value=("usable transcript", "en")), \
         patch.object(app, "chatgpt_canonical_evidence", return_value=_assessment("D")):
        result = app.create_manual_chatgpt_processing_package({"mode": "FULL_INTELLIGENCE", "video_ids": "v1", "features": ["title_en.v1"]})

    assert result["ok"] is False
    assert result["videos"] == 0
    assert result["skipped_source_repair"] == 1
    queue = json.loads(Path(result["skipped_source_repair_file"]).read_text(encoding="utf-8"))
    assert queue["videos"][0]["reason_code"] == "TRANSCRIPT_GRADE_D_EXCLUDED"
    assert queue["videos"][0]["routing_class"] == "REPAIR_RECOMMENDED"


def test_phase5_c_grade_remains_normal_package_eligible(tmp_path):
    from app import app

    db = tmp_path / "test.db"
    con = _minimal_db(db)
    folder = tmp_path / "folder"
    folder.mkdir()
    con.execute(
        "INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("v1", "https://youtu.be/v1", "Title", "Clean", "Channel", "2026-01-01", "Description", "Education", "Education", "", "", str(folder), 0, 120, 1),
    )
    con.commit(); con.close()

    with patch.object(app, "BASE", tmp_path), \
         patch.object(app, "db_connect", side_effect=lambda: sqlite3.connect(db)), \
         patch.object(app, "artifact_manifest_for_video", return_value={"timestamped_transcript": "x"}), \
         patch.object(app, "best_transcript_for_video", return_value=("usable transcript", "en")), \
         patch.object(app, "chatgpt_canonical_evidence", return_value=_assessment("C")):
        result = app.create_manual_chatgpt_processing_package({"mode": "FULL_INTELLIGENCE", "video_ids": "v1", "features": ["title_en.v1"]})

    assert result["ok"] is True
    assert result["videos"] == 1
    assert result["packaged_video_ids"] == ["v1"]
    assert result["evidence_by_video"]["v1"] == "C"


def test_phase5_golden_fixture_routing_matches_approved_a_b_c_vs_d_f_split():
    manifest_path = Path(__file__).parent / "fixtures" / "phase0_grade_golden_manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = data["fixtures"]
    assert len(rows) == 13
    counts = {g: 0 for g in "ABCDF"}
    for row in rows:
        grade = normalize_evidence_grade(row["transcript_health_grade"])
        counts[grade] += 1
        assert normal_transcript_package_eligible(grade) is (grade in {"A", "B", "C"})
    assert counts == {"A": 3, "B": 3, "C": 3, "D": 3, "F": 1}
