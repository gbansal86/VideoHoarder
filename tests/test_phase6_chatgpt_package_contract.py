import json
import sqlite3
from pathlib import Path
from unittest.mock import patch


def _db(path: Path):
    con=sqlite3.connect(path)
    con.executescript("""
    CREATE TABLE videos(
      video_id TEXT,url TEXT,original_title TEXT,clean_title TEXT,channel TEXT,upload_date TEXT,
      description TEXT,source_category TEXT,youtube_category_name TEXT,comments_file TEXT,
      comments_transcript_file TEXT,local_folder TEXT,archived INTEGER,duration_seconds REAL,
      current_present INTEGER DEFAULT 1,availability TEXT,source_chapters_json TEXT,youtube_tags_cleaned TEXT,
      subtitle_source TEXT,subtitle_lang TEXT,subtitle_base_lang TEXT,transcript_source TEXT);
    CREATE TABLE chatgpt_requests(request_id TEXT PRIMARY KEY,package_id TEXT UNIQUE,mode TEXT,schema_version TEXT,prompt_version TEXT,requested_features_json TEXT,package_hash TEXT,manifest_json TEXT,created_at TEXT,status TEXT,result_path TEXT,result_hash TEXT,validation_status TEXT,applied_status TEXT,notes TEXT);
    CREATE TABLE chatgpt_request_videos(request_id TEXT,video_id TEXT,source_snapshot_hash TEXT,evidence_manifest_json TEXT,requested_features_json TEXT,PRIMARY KEY(request_id,video_id));
    CREATE TABLE video_feature_coverage(video_id TEXT,feature_id TEXT,feature_version TEXT,status TEXT,source_snapshot_hash TEXT,package_id TEXT,result_hash TEXT,evidence_coverage TEXT,completed_at TEXT,stale_reason TEXT,last_error TEXT,PRIMARY KEY(video_id,feature_id,feature_version));
    """)
    return con


def _assessment(grade="A"):
    return {
      "video_id":"v1","transcript_available":True,"transcript_source":"timestamped_transcript",
      "canonical_segment_count":1,"timestamps_available":True,"timestamp_status":"reliable",
      "timestamp_hints_available":False,"timestamp_hints_reliable":False,"normalization_status":"NORMALIZED",
      "transcript_characters":1000,"transcript_words":150,
      "transcript_health":{"grade":grade,"score":95,"routing_class":"NORMAL","reason_codes":[],"hard_failure":False},
      "evidence_grade":grade,"source_conflicts":[],"source_consistency":"not_used_for_grading",
      "canonical_transcript":{"source":"timestamped_transcript","language":"en","segments":[{"segment_id":"s00001","start_seconds":0,"end_seconds":10,"text":"hello"}],"untimestamped_text":""},
      "comments":{"included_comments":2,"records":[{"text":"SHOULD NEVER LEAK"}]},
    }


def test_phase6_builder_exact_allowlist_and_forbidden_fields_absent():
    from app.chatgpt_package_builder import build_video_payload, assert_strict_package_contract
    row={
      "video_id":"v1","url":"https://youtu.be/v1","original_title":"Original","clean_title":"Clean",
      "channel":"Channel","upload_date":"2026-01-01","duration_seconds":120,"availability":"public",
      "youtube_category_name":"Education","source_chapters_json":json.dumps([{"start_seconds":0,"source_title":"Intro","display_title":"Introduction"}]),
      "youtube_tags_cleaned":json.dumps(["nutrition","health"]),"subtitle_source":"youtube_auto","subtitle_lang":"en",
      "subtitle_base_lang":"hi","transcript_source":"canonical_vtt","description":"DO NOT SEND",
      "view_count":999,"heatmap_json":"[]",
    }
    payload=build_video_payload(row,assessment=_assessment(),artifact_manifest={"timestamped_transcript":"x","description":"secret.description","comments":"comments.json","info_json":"raw.info.json"},transcript_language="en",requested_features=["title_en.v1"])
    assert_strict_package_contract(payload)
    assert set(payload["metadata"]) == {"id","original_title","clean_title","channel","upload_date","duration_seconds","webpage_url","availability","category"}
    assert payload["metadata"]["clean_title"] == "Clean"
    assert payload["metadata"]["category"] == "Education"
    assert payload["auxiliary_metadata"]["source_tags"] == ["nutrition","health"]
    assert payload["auxiliary_metadata"]["source_chapters"][0]["source_title"] == "Intro"
    assert payload["transcript_provenance"]["base_language"] == "hi"
    serialized=json.dumps(payload)
    for forbidden in ["description","comments","view_count","heatmap_json","youtube_category_name","youtube_tags_cleaned"]:
        assert f'"{forbidden}"' not in serialized
    assert "SHOULD NEVER LEAK" not in serialized
    assert "secret.description" not in serialized
    assert "comments.json" not in serialized
    assert "raw.info.json" not in serialized
    assert "comments_available" not in serialized
    assert "description_available" not in serialized


def test_phase6_actual_package_uses_contract_and_omits_description_comments(tmp_path):
    from app import app
    db=tmp_path/"test.db";con=_db(db);folder=tmp_path/"folder";folder.mkdir()
    comments=tmp_path/"comments.txt";comments.write_text("valuable but separate comment",encoding="utf-8")
    con.execute("INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
      "v1","https://youtu.be/v1","Original Title","Clean Title","Channel","2026-01-01","SECRET DESCRIPTION","Education","Education",str(comments),str(comments),str(folder),0,120,1,"public",
      json.dumps([{"start_seconds":0,"end_seconds":30,"source_title":"Intro","display_title":"Introduction"}]),
      json.dumps(["clean tag"]),"youtube_auto","en","en","canonical_vtt"))
    con.commit();con.close()
    transcript="\n".join(f"[00:{n:02d}] useful transcript line {n}" for n in range(60))
    with patch.object(app,"BASE",tmp_path),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)),patch.object(app,"artifact_manifest_for_video",return_value={"timestamped_transcript":"x"}),patch.object(app,"best_transcript_for_video",return_value=(transcript,"en")),patch.object(app,"chatgpt_canonical_evidence",return_value=_assessment("A")):
        result=app.create_manual_chatgpt_processing_package({"mode":"FULL_INTELLIGENCE","video_ids":"v1","features":["title_en.v1"]})
    assert result["ok"] is True and result["videos"] == 1
    payload=json.loads(Path(result["upload_file"]).read_text(encoding="utf-8"))
    video=payload["videos"][0]
    assert video["package_grade"] == "A"
    assert video["metadata"]["clean_title"] == "Clean Title"
    assert video["metadata"]["category"] == "Education"
    assert video["auxiliary_metadata"]["source_tags"] == ["clean tag"]
    assert "comments" not in video["evidence"]
    text=json.dumps(video)
    assert "SECRET DESCRIPTION" not in text
    assert "valuable but separate comment" not in text
    assert '"description"' not in text


def test_phase6_legacy_db_without_new_columns_still_packages(tmp_path):
    from app import app
    db=tmp_path/"test.db";con=sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE videos(video_id TEXT,url TEXT,original_title TEXT,clean_title TEXT,channel TEXT,upload_date TEXT,description TEXT,source_category TEXT,youtube_category_name TEXT,comments_file TEXT,comments_transcript_file TEXT,local_folder TEXT,archived INTEGER,duration_seconds REAL,current_present INTEGER DEFAULT 1);
    CREATE TABLE chatgpt_requests(request_id TEXT PRIMARY KEY,package_id TEXT UNIQUE,mode TEXT,schema_version TEXT,prompt_version TEXT,requested_features_json TEXT,package_hash TEXT,manifest_json TEXT,created_at TEXT,status TEXT,result_path TEXT,result_hash TEXT,validation_status TEXT,applied_status TEXT,notes TEXT);
    CREATE TABLE chatgpt_request_videos(request_id TEXT,video_id TEXT,source_snapshot_hash TEXT,evidence_manifest_json TEXT,requested_features_json TEXT,PRIMARY KEY(request_id,video_id));
    CREATE TABLE video_feature_coverage(video_id TEXT,feature_id TEXT,feature_version TEXT,status TEXT,source_snapshot_hash TEXT,package_id TEXT,result_hash TEXT,evidence_coverage TEXT,completed_at TEXT,stale_reason TEXT,last_error TEXT,PRIMARY KEY(video_id,feature_id,feature_version));
    """)
    folder=tmp_path/"folder";folder.mkdir()
    con.execute("INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",("v1","https://youtu.be/v1","Original","Clean","Channel","2026-01-01","Description","Education","Education","","",str(folder),0,120,1));con.commit();con.close()
    with patch.object(app,"BASE",tmp_path),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)),patch.object(app,"artifact_manifest_for_video",return_value={"timestamped_transcript":"x"}),patch.object(app,"best_transcript_for_video",return_value=("usable transcript","en")),patch.object(app,"chatgpt_canonical_evidence",return_value=_assessment("A")):
        result=app.create_manual_chatgpt_processing_package({"mode":"FULL_INTELLIGENCE","video_ids":"v1","features":["title_en.v1"]})
    payload=json.loads(Path(result["upload_file"]).read_text())
    video=payload["videos"][0]
    assert video["metadata"]["availability"] == ""
    assert video["auxiliary_metadata"] == {"source_chapters":[],"source_tags":[]}


def test_phase6_d_f_exclusion_still_happens_before_payload_build(tmp_path):
    from app import app
    db=tmp_path/"test.db";con=_db(db);folder=tmp_path/"folder";folder.mkdir()
    con.execute("INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",("v1","https://youtu.be/v1","Original","Clean","Channel","2026-01-01","Description","Education","Education","","",str(folder),0,120,1,"public","[]","[]","","en","en",""));con.commit();con.close()
    for grade in ("D","F"):
        with patch.object(app,"BASE",tmp_path),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)),patch.object(app,"artifact_manifest_for_video",return_value={"timestamped_transcript":"x"}),patch.object(app,"best_transcript_for_video",return_value=("usable transcript","en")),patch.object(app,"chatgpt_canonical_evidence",return_value=_assessment(grade)):
            result=app.create_manual_chatgpt_processing_package({"mode":"FULL_INTELLIGENCE","video_ids":"v1","features":["title_en.v1"]})
        assert result["ok"] is False
        assert result["videos"] == 0
        assert result["skipped_source_repair"] == 1
