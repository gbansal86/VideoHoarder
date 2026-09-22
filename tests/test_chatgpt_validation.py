import hashlib
import base64
import io
import json
import os
import shutil
import sqlite3
import unittest
import uuid
import zipfile
from pathlib import Path
from unittest.mock import patch

class ChatGPTValidationTests(unittest.TestCase):
    def runtime_root(self):
        root=Path.cwd()/"tests"/"runtime_data"/f"chatgpt_{uuid.uuid4().hex}"
        root.mkdir(parents=True,exist_ok=True)
        self.addCleanup(lambda:shutil.rmtree(root,ignore_errors=True))
        return root

    def test_timestamp_parser(self):
        from app import app
        self.assertEqual(app._chatgpt_timestamp_seconds("01:02"), 62)
        self.assertEqual(app._chatgpt_timestamp_seconds("01:02:03"), 3723)
        self.assertIsNone(app._chatgpt_timestamp_seconds("not-a-time"))

    def test_old_database_is_migrated_with_duration_seconds(self):
        from app import app
        base=self.runtime_root();db=base/"old.db";con=sqlite3.connect(db)
        con.execute("CREATE TABLE videos(video_id TEXT PRIMARY KEY, url TEXT, upload_date TEXT)");con.commit();con.close()
        with patch.object(app,"BASE",base),patch.object(app,"DB",db):
            migrated=app.db_connect()
            columns={row[1] for row in migrated.execute("PRAGMA table_info(videos)").fetchall()}
            migrated.close()
        self.assertIn("duration_seconds",columns)

    def test_timestamp_walker(self):
        from app import app
        rows = app._chatgpt_walk_timestamps({"timeline": [{"start_timestamp": "00:10"}]})
        self.assertIn(("$.timeline[0].start_timestamp", "00:10"), rows)

    def test_canonical_evidence_grades_and_segments(self):
        from app import app
        transcript="\n".join(f"[00:{n:02d}] useful transcript line {n}" for n in range(60))
        result=app.chatgpt_canonical_evidence("abc",{"original_title":"Useful transcript","description":"Useful transcript details"},{"timestamped_transcript":"x"},transcript,"en","")
        self.assertTrue(result["transcript_available"])
        self.assertEqual(result["transcript_source"],"existing_transcript")
        self.assertTrue(result["timestamps_monotonic"])
        self.assertEqual(result["canonical_transcript"]["segments"][0]["segment_id"],"s00001")
        self.assertIn("end_timestamp",result["canonical_transcript"]["segments"][0])
        self.assertGreater(result["canonical_segment_count"],0)
        self.assertIn(result["evidence_grade"],{"A","B"})

    def test_caption_fragments_merge_and_comments_are_structured(self):
        from app import app
        srt="""1\n00:00:00,000 --> 00:00:02,000\nThis is a short\n\n2\n00:00:02,000 --> 00:00:05,000\ncaption fragment that becomes complete.\n\n3\n00:00:05,000 --> 00:00:08,000\nA second sentence ends here.\n"""
        result=app.chatgpt_canonical_evidence("abc",{"original_title":"Example","duration_seconds":10},{"srt":"x"},srt,"en","Great explanation\nPlease cover risks")
        segments=result["canonical_transcript"]["segments"]
        self.assertEqual(segments[0]["text"],"This is a short caption fragment that becomes complete.")
        self.assertEqual(segments[0]["start_seconds"],0)
        self.assertEqual(segments[0]["end_seconds"],5)
        self.assertEqual(result["video_duration_seconds"],10)
        self.assertEqual(result["comments"]["total_comments"],2)
        self.assertEqual(result["comments"]["sampling_method"],"all_supplied_comments")

    def test_music_only_caption_is_not_usable_transcript(self):
        from app import app
        self.assertFalse(app.transcript_has_useful_speech("[00:00:01] [Music]\n[00:00:05] (applause)\n[00:00:08] ♪"))
        self.assertTrue(app.transcript_has_useful_speech("[00:00:01] This video explains five dinner foods to avoid and why they matter."))

    def test_v334_transcript_health_routes_and_missing_duration(self):
        from app import app
        missing=app.chatgpt_transcript_health("",0,{})
        self.assertEqual(missing["grade"],"F")
        self.assertEqual(missing["routing_class"],"REPAIR_REQUIRED")
        self.assertIn("TRANSCRIPT_MISSING",missing["reason_codes"])
        healthy=app.chatgpt_transcript_health("\n".join(f"00:{i:02d} useful spoken transcript line with enough words for health analysis." for i in range(0,55,5)),0,{})
        self.assertIn(healthy["grade"],{"A","B","C"})
        self.assertNotEqual(healthy["routing_class"],"REPAIR_REQUIRED")
        self.assertIsNone(healthy["signals"]["duration_coverage"])

    def test_chatgpt_page_exposes_single_file_and_batch_controls(self):
        from app import app
        page=app.chatgpt_processing_page_html()
        self.assertIn("Group Similar Videos",page)
        self.assertIn("CHATGPT_PACKAGE.json",page)
        self.assertIn("BATCH_PACKAGE_SUMMARY.csv",page)
        self.assertIn('id="githubPublish"',page)
        self.assertIn('id="githubPublishPlanner"',page)
        self.assertIn('id="githubPublishBatches"',page)
        self.assertIn('id="githubArchiveProcessed"',page)
        self.assertIn("Upload latest planner to GitHub",page)
        self.assertIn("Upload latest grouped packages to GitHub",page)
        self.assertIn("publishLatestGithub",page)
        self.assertIn("/api/chatgpt-processing/import-github",page)
        self.assertIn("Phase: ",page)
        self.assertIn("Progress: ",page)
        self.assertIn("public gbansal86/VideoHoarder repository",page)
        self.assertIn("BATCH_VALIDATION_REPORT.csv",page)
        self.assertIn("automaticBatchSize",page)
        self.assertIn("compactChatgptPackage",page)
        self.assertIn("Use master modular sequential ChatGPT prompt",page)
        self.assertIn("exclude videos without usable transcript/SRT/VTT or music-only captions",page)
        self.assertIn("allowRecreateProcessed",page)
        self.assertIn("resetProcessedLocksBatches",page)
        self.assertIn("reset_processed_locks_before_grouping",page)
        self.assertIn("refreshLibraryBeforeGrouping",page)
        self.assertIn("refresh_library_before_grouping",page)
        self.assertIn("Rebuild database counts",page)
        self.assertIn("library_rebuild_exports",page)
        self.assertIn("named_items.v1",page)
        self.assertIn("resultZip",page)
        self.assertIn("/api/chatgpt-processing/import-zip",page)
        self.assertIn("Apply all validated results",page)
        self.assertIn("applyAllValidatedResults",page)
        self.assertIn("/api/chatgpt-processing/apply-all-validated",page)

    @unittest.skipUnless(os.name == "nt", "Windows-specific git.exe path semantics")
    def test_github_upload_git_lookup_uses_executable_discovery(self):
        from app import app
        discovered = r"C:\Tools\Git\cmd\git.exe"
        with patch.object(app.shutil,"which",return_value=discovered):
            found=Path(app.chatgpt_git_executable())
            self.assertEqual(found,Path(discovered))

    def test_github_publisher_is_repo_scoped_and_curates_files(self):
        from app import app
        base=self.runtime_root();source=base/"data"/"chatgpt"/"exchange"/"outgoing"/"pkg";source.mkdir(parents=True)
        (source/"CHATGPT_PACKAGE.json").write_text("{}",encoding="utf-8")
        (source/"evidence.json").write_text("private duplicate",encoding="utf-8")
        mirror=base/"tmp_github_clone"/"VideoHoarder"
        mirror.mkdir(parents=True)
        captured_stage=[]
        def fake_git(args,cwd=None,timeout=180):
            if args[:3]==["remote","get-url","origin"]: return app.CHATGPT_GITHUB_REPO_URL
            if args[:3]==["diff","--cached","--name-only"]:
                published=mirror/"exchange"/"outgoing"/"single_packages"/"master"/"pkg"
                captured_stage.append((published/"CHATGPT_PACKAGE.json").is_file())
                captured_stage.append((published/"evidence.json").exists())
                return "exchange/outgoing/single_packages/master/pkg/CHATGPT_PACKAGE.json"
            if args[:2]==["rev-parse","HEAD"]: return "a"*40
            return ""
        with patch.object(app,"BASE",base),patch.object(app,"_chatgpt_git",side_effect=fake_git):
            with patch.object(app,"ensure_chatgpt_github_mirror",return_value=mirror):
                result=app.publish_chatgpt_exchange_to_github(source,"exchange/outgoing/single_packages/master/pkg","pkg")
            self.assertTrue(result["public_repository"])
            self.assertTrue(result["local_clone_removed"])
            self.assertFalse(mirror.parent.exists())
            self.assertEqual(captured_stage,[True,False])
            with self.assertRaises(ValueError):
                app.publish_chatgpt_exchange_to_github(source,"another-repository/pkg","pkg")

    def test_github_result_import_copies_locally_and_archives_processed(self):
        from app import app
        base=self.runtime_root()
        mirror=base/"tmp_github_clone"/"VideoHoarder"
        result_file=mirror/"exchange"/"incoming"/"chatgpt_results"/"pkg_result.json"
        result_file.parent.mkdir(parents=True)
        result_file.write_text(json.dumps({"package_id":"pkg","schema_version":"3.0","video_updates":[]}),encoding="utf-8")
        git_calls=[]
        def fake_git(args,cwd=None,timeout=180):
            git_calls.append(args)
            if args[:2]==["diff","--cached"]: return "exchange/incoming/chatgpt_results/pkg_result.json"
            if args[:2]==["rev-parse","HEAD"]: return "b"*40
            return ""
        def fake_import(payload):
            self.assertEqual(payload["filename"],"pkg_result.json")
            self.assertIn('"package_id": "pkg"',payload["result_json"])
            return {"ok":True,"package_id":"pkg","status":"VALIDATED","result_file":"local"}
        with patch.object(app,"BASE",base),patch.object(app,"ensure_chatgpt_github_mirror",return_value=mirror),patch.object(app,"_chatgpt_git",side_effect=fake_git),patch.object(app,"import_validate_manual_chatgpt_processing_result",side_effect=fake_import):
            result=app.import_validate_chatgpt_results_from_github({"archive_processed":True})
        self.assertTrue(result["ok"])
        self.assertTrue(result["local_clone_removed"])
        self.assertTrue(result["local_copies"])
        self.assertTrue(Path(result["local_copies"][0]).is_file())
        self.assertIn(str(Path("exchange")/"incoming"/"full_intelligence"),str(Path(result["local_copies"][0])))
        self.assertNotIn("exchange\\incoming\\from_remote",str(Path(result["local_copies"][0])))
        self.assertNotIn("exchange\\incoming\\github",str(Path(result["local_copies"][0])))
        self.assertFalse(mirror.parent.exists())
        self.assertTrue(result["archived"][0]["to"].startswith("exchange/archive/processed/chatgpt_results/"))
        self.assertTrue(any(call and call[0]=="commit" for call in git_calls))

    def test_chatgpt_runtime_paths_are_inside_exchange(self):
        from app import app
        base=self.runtime_root()
        with patch.object(app,"BASE",base):
            mirror=app.chatgpt_github_mirror_path()
            self.assertEqual(app.chatgpt_exchange_dir().resolve(),(base/"data"/"chatgpt"/"exchange").resolve())
            packages,results,retry,archive,history=app.phase2_chatgpt_dirs()
        exchange=(base/"data"/"chatgpt"/"exchange").resolve()
        for path in [mirror,packages,results,retry,archive,history]:
            self.assertIn(exchange, Path(path).resolve().parents)
        shutil.rmtree(mirror.parent,ignore_errors=True)
    def test_processing_package_creates_one_upload_json_with_actual_title(self):
        from app import app
        base=self.runtime_root();db=base/"test.db";con=sqlite3.connect(db)
        con.executescript("""
        CREATE TABLE videos(video_id TEXT,url TEXT,original_title TEXT,clean_title TEXT,channel TEXT,upload_date TEXT,description TEXT,source_category TEXT,youtube_category_name TEXT,comments_file TEXT,comments_transcript_file TEXT,local_folder TEXT,archived INTEGER,duration_seconds REAL);
        CREATE TABLE chatgpt_requests(request_id TEXT PRIMARY KEY,package_id TEXT UNIQUE,mode TEXT,schema_version TEXT,prompt_version TEXT,requested_features_json TEXT,package_hash TEXT,manifest_json TEXT,created_at TEXT,status TEXT,result_path TEXT,result_hash TEXT,validation_status TEXT,applied_status TEXT,notes TEXT);
        CREATE TABLE chatgpt_request_videos(request_id TEXT,video_id TEXT,source_snapshot_hash TEXT,evidence_manifest_json TEXT,requested_features_json TEXT,PRIMARY KEY(request_id,video_id));
        CREATE TABLE video_feature_coverage(video_id TEXT,feature_id TEXT,feature_version TEXT,status TEXT,source_snapshot_hash TEXT,package_id TEXT,result_hash TEXT,evidence_coverage TEXT,completed_at TEXT,stale_reason TEXT,last_error TEXT,PRIMARY KEY(video_id,feature_id,feature_version));
        """)
        (base/"folder").mkdir(parents=True,exist_ok=True);(base/"folder_def").mkdir(parents=True,exist_ok=True)
        con.execute("INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",("abc","https://youtu.be/abc","The Actual Title","Clean Title","Channel","2026-01-01","Useful details","Education","Education","","",str(base/"folder"),0,120))
        con.execute("INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",("def","https://youtu.be/def","No Transcript Title","No Transcript Clean Title","Channel","2026-01-02","Metadata only","Education","Education","","",str(base/"folder_def"),0,120));con.commit();con.close()
        transcript="\n".join(f"[00:{n:02d}] useful transcript line {n}" for n in range(60))
        with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)),patch.object(app,"artifact_manifest_for_video",return_value={"timestamped_transcript":"transcript.txt"}),patch.object(app,"best_transcript_for_video",return_value=(transcript,"en")):
            result=app.create_manual_chatgpt_processing_package({"mode":"FULL_INTELLIGENCE","video_ids":"abc","features":["title_en.v1","detailed_summary.v3","named_items.v1"]})
            with patch.object(app,"chatgpt_package_transcript_preflight",return_value={"total":1,"available":1,"unavailable":0,"available_ids":["abc"],"unavailable_ids":[],"checked":False}):
                batch=app.create_manual_chatgpt_processing_batch_set({"video_ids":"abc","features":["title_en.v1","detailed_summary.v3","named_items.v1"],"automatic_batch_size":True})
                planner=app.create_manual_chatgpt_batch_planner({"video_ids":"abc"})
            with patch.object(app,"chatgpt_package_transcript_preflight",return_value={"total":2,"available":1,"unavailable":1,"available_ids":["abc"],"unavailable_ids":["def"],"checked":False}):
                compact_batch=app.create_manual_chatgpt_processing_batch_set({"video_ids":"abc\ndef","features":list(app.CHATGPT_FEATURES),"automatic_batch_size":True,"compact_chatgpt_package":True})
        upload=Path(result["upload_file"]);self.assertTrue(upload.is_file())
        payload=json.loads(upload.read_text(encoding="utf-8"))
        self.assertEqual(payload["videos"][0]["metadata"]["original_title"],"The Actual Title")
        self.assertEqual(payload["videos"][0]["evidence"]["canonical_transcript"]["segments"][0]["segment_id"],"s00001")
        contracts=payload["response_schema"]["feature_contracts"]
        self.assertNotIn("editorial_assessment.v1",contracts)
        self.assertIn("named_items.v1",contracts)
        title_rules=" ".join(payload["response_schema"]["feature_contracts"]["title_en.v1"]["rules"])
        self.assertIn("include the key named items",title_rules)
        self.assertEqual(payload["instructions"]["response_template"]["video_updates"][0]["features"]["title_en.v1"]["title"],"")
        self.assertNotIn("Example named item",json.dumps(payload["instructions"]["response_template"]))
        self.assertIn("detailed_summary.v3",contracts)
        self.assertIn("quality_rubric",payload["instructions"])
        self.assertEqual(payload["manifest"]["feature_contract_version"],"3.3.4")
        self.assertEqual(payload["manifest"]["validation_pipeline"],"v3.3.4-health-aware")
        self.assertEqual(payload["manifest"]["prompt_version"],"3.3.4-final")
        self.assertIn("package_quality",payload)
        self.assertIn(payload["package_quality"]["grade"],{"A","B","C","D","F"})
        self.assertIn("workload",payload)
        self.assertIn("package_quality_context",payload["instructions"])
        self.assertTrue((upload.parent/"VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md").is_file())
        self.assertIn("transcript_health",payload["videos"][0]["evidence"]["assessment"])
        formal=payload["response_schema"]["formal_json_schema"]
        self.assertEqual(formal["$schema"],"https://json-schema.org/draft/2020-12/schema")
        self.assertIn("video_updates",formal["properties"])
        self.assertIn("controlled_taxonomy",payload["response_schema"])
        video_payload=payload["videos"][0]
        evidence=video_payload["evidence"]
        self.assertNotIn("comments",evidence)
        self.assertNotIn("description",video_payload["metadata"])
        self.assertIn("auxiliary_metadata",video_payload)
        self.assertIn("transcript_provenance",video_payload)
        self.assertNotIn("transcript",evidence)
        csv_text=Path(batch["batch_summary_csv"]).read_text(encoding="utf-8-sig")
        self.assertIn("actual_title",csv_text)
        self.assertIn("The Actual Title",csv_text)
        self.assertEqual(batch["local_batch_validation_status"],"PASS")
        self.assertTrue((Path(batch["folder"])/"BATCH_SET_INDEX.json").is_file())
        planner_payload=json.loads(Path(planner["upload_file"]).read_text(encoding="utf-8"))
        rubric=planner_payload["response_schema"]["grouping_quality_rubric"]
        self.assertIn("actual topic and research purpose",rubric["priority_order"])
        self.assertTrue(any("keyword" in rule.lower() for rule in rubric["quality_rules"]))
        self.assertIn("topic_first_size_split",rubric["allowed_grouping_basis"])
        self.assertTrue(any("Group 1" in rule for rule in rubric["quality_rules"]))
        self.assertEqual(len(rubric["final_validation_checklist"]),9)
        self.assertTrue(any("PCOS" in bucket for bucket in rubric["illustrative_buckets"]))
        self.assertEqual(planner_payload["manifest"]["planner_quality_version"],"1")
        parent_template=planner_payload["response_schema"]["response_template"]["parent_groups"]["transcript_parent_groups"][0]
        no_transcript_parent_template=planner_payload["response_schema"]["response_template"]["parent_groups"]["no_transcript_parent_groups"][0]
        self.assertNotIn("small_group_exception",parent_template)
        self.assertNotIn("small_group_exception",no_transcript_parent_template)
        planner_instructions=planner_payload["instructions"]["instructions"]
        self.assertIn("compatibility guidance only",planner_instructions)
        self.assertIn("hard maximum 30",planner_instructions)
        planner_csv_header=Path(planner["catalog_csv"]).read_text(encoding="utf-8-sig").splitlines()[0].split(",")
        self.assertIn("actual_title",planner_csv_header)
        self.assertIn("transcript_characters",planner_csv_header)
        self.assertIn("video_duration_seconds",planner_csv_header)
        self.assertIn("video_type",planner_csv_header)
        self.assertNotIn("description",planner_csv_header)
        self.assertTrue(compact_batch["compact_chatgpt_package"])
        self.assertEqual(compact_batch["requested_features"],app.CHATGPT_COMPACT_GROUPED_FEATURES)
        self.assertEqual(compact_batch["skipped_no_transcript_videos"],1)
        self.assertTrue(Path(compact_batch["skipped_no_transcript_csv"]).is_file())
        compact_index=json.loads((Path(compact_batch["folder"])/"BATCH_SET_INDEX.json").read_text(encoding="utf-8"))
        self.assertEqual(compact_index["packaged_video_count"],1)
        self.assertEqual(compact_index["skipped_no_transcript_videos"],1)
        self.assertNotIn("NO_TRANSCRIPT_METADATA",json.dumps(compact_index))
        compact_upload=json.loads(Path(compact_batch["packages"][0]["upload_file"]).read_text(encoding="utf-8"))
        self.assertEqual(compact_upload["response_schema"]["allowed_feature_ids"],app.CHATGPT_COMPACT_GROUPED_FEATURES)
        compact_prompt=json.dumps(compact_upload["instructions"],ensure_ascii=False)
        self.assertIn("master_modular_sequential_exact_v1",compact_prompt)
        self.assertIn("Process videos strictly in package order",compact_prompt)
        self.assertIn("Do not use video description or viewer comments for transcript analysis",compact_prompt)
        self.assertIn("Completely exclude sponsor/ad/affiliate/coupon/promotional content",compact_prompt)
        self.assertIn("hard maximum is 30",compact_prompt); self.assertIn("no minimum package size",compact_prompt)
        compact_features=compact_upload["instructions"]["response_template"]["video_updates"][0]["features"]
        self.assertIn("detailed_summary.v3",compact_features)
        self.assertIn("recipes.v1",compact_features)
        self.assertIn("references.v1",compact_features)
        self.assertIn("qa.v1",compact_features)
        self.assertIn("playlist_series.v1",compact_features)
        self.assertIn("technical_intelligence.v1",compact_features)
        self.assertIn("named_items.v1",compact_features)
        self.assertNotIn("executive_summary.v2",compact_features)
        self.assertNotIn("entities.v2",compact_features)
        self.assertNotIn("claims_warnings.v2",compact_features)
        self.assertNotIn("editorial_assessment.v1",compact_features)
        key=app.chatgpt_feature_set_key(["title_en.v1"])
        con=sqlite3.connect(db)
        con.execute("""CREATE TABLE IF NOT EXISTS chatgpt_processed_video_locks(
            video_id TEXT NOT NULL, feature_set_key TEXT NOT NULL, package_id TEXT,
            result_hash TEXT, completed_at TEXT NOT NULL, requested_features_json TEXT,
            PRIMARY KEY(video_id,feature_set_key)
        )""")
        con.execute("INSERT OR REPLACE INTO chatgpt_processed_video_locks VALUES(?,?,?,?,?,?)",("abc",key,"old_pkg","hash","2026-01-01 00:00:00",json.dumps(["title_en.v1"])))
        con.commit();con.close()
        marker_dir=base/"folder"/"_data";marker_dir.mkdir(parents=True,exist_ok=True)
        (marker_dir/f"chatgpt_package_complete_{key}.json").write_text(json.dumps({"video_id":"abc","feature_set_key":key}),encoding="utf-8")
        with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)),patch.object(app,"artifact_manifest_for_video",return_value={"timestamped_transcript":"transcript.txt"}),patch.object(app,"best_transcript_for_video",return_value=(transcript,"en")):
            filtered=app.create_manual_chatgpt_processing_package({"mode":"FULL_INTELLIGENCE","video_ids":"abc\ndef","features":["title_en.v1"]})
            recreated=app.create_manual_chatgpt_processing_package({"mode":"FULL_INTELLIGENCE","video_ids":"abc\ndef","features":["title_en.v1"],"allow_recreate_processed":True})
        self.assertEqual(filtered["videos"],1)
        self.assertEqual(filtered["skipped_already_processed"],1)
        self.assertEqual(recreated["videos"],2)
        (marker_dir/f"chatgpt_package_complete_{key}.json").unlink()
        with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)),patch.object(app,"artifact_manifest_for_video",return_value={"timestamped_transcript":"transcript.txt"}),patch.object(app,"best_transcript_for_video",return_value=(transcript,"en")):
            missing_marker=app.create_manual_chatgpt_processing_package({"mode":"FULL_INTELLIGENCE","video_ids":"abc","features":["title_en.v1"]})
        self.assertEqual(missing_marker["videos"],1)
        self.assertEqual(missing_marker["skipped_already_processed"],0)

    def test_returned_zip_reads_only_unique_result_json_without_extracting(self):
        from app import app
        base=self.runtime_root();buffer=io.BytesIO()
        with zipfile.ZipFile(buffer,"w",zipfile.ZIP_DEFLATED) as z:
            z.writestr("packages/pkg_a/result.json",json.dumps({"package_id":"pkg_a","video_updates":[]}))
            z.writestr("packages/pkg_b/result.json",json.dumps({"package_id":"pkg_b","video_updates":[]}))
            z.writestr("packages/pkg_a/copy/result.json",json.dumps({"package_id":"pkg_a","video_updates":[]}))
            z.writestr("packages/pkg_a/evidence.json",json.dumps({"do_not_import":True}))
        captured={}
        def fake_many(payload):
            captured.update(payload)
            return {"ok":True,"files":len(payload["results"]),"validated":2,"partial":0,"failed":0,"outcomes":[],"manual_review_required":True,"applied":False}
        with patch.object(app,"BASE",base),patch.object(app,"import_validate_many_manual_chatgpt_processing_results",side_effect=fake_many):
            result=app.import_validate_manual_chatgpt_processing_zip({"filename":"returned.zip","zip_base64":base64.b64encode(buffer.getvalue()).decode("ascii")})
        self.assertEqual(result["result_files_found"],2)
        self.assertEqual(len(captured["results"]),2)
        self.assertFalse(result["source_zip_was_extracted"])
        self.assertTrue(Path(result["bulk_validation_report"]).is_file())

    def test_apply_all_validated_results_adapts_v3_features(self):
        from app import app
        base=self.runtime_root();db=base/"test.db";con=sqlite3.connect(db)
        con.executescript("""
        CREATE TABLE videos(video_id TEXT PRIMARY KEY, clean_title TEXT, category TEXT, subcategory TEXT, main_topic TEXT, tags TEXT, taxonomy_updated_at TEXT);
        """)
        con.execute("INSERT INTO videos(video_id,clean_title,category,subcategory,main_topic,tags,taxonomy_updated_at) VALUES(?,?,?,?,?,?,?)",("vid1","Old title","","","","",""))
        con.commit();con.close()
        review=base/"data"/"chatgpt"/"exchange"/"review";review.mkdir(parents=True)
        preview={
            "package_id":"pkg1",
            "status":"VALIDATED",
            "proposed_updates":[{
                "video_id":"vid1",
                "features":{
                    "title_en.v1":{"title":"Better Dinner Foods Title","short_title":"Dinner Foods","reason":"ok"},
                    "taxonomy.v3":{"category":"Health","subcategory":"Nutrition","primary_topic":"Dinner foods","keywords":["dinner"],"canonical_tags":["dinner foods","nutrition"],"search_queries":[]}
                }
            }]
        }
        (review/"pkg1_review.json").write_text(json.dumps(preview),encoding="utf-8")
        with patch.object(app,"BASE",base),patch.object(app,"DB",db),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)),patch.object(app,"phase6_preview_category_moves",return_value={"ok":True}),patch.object(app,"rebuild_database_and_library_exports",return_value={"ok":True}):
            result=app.apply_all_validated_chatgpt_results()
        self.assertEqual(result["applied"],1)
        con=sqlite3.connect(db);row=con.execute("SELECT clean_title,category,subcategory,main_topic,tags FROM videos WHERE video_id='vid1'").fetchone();con.close()
        self.assertEqual(row[0],"Better Dinner Foods Title")
        self.assertEqual(row[1],"Health")
        self.assertEqual(row[2],"Nutrition")
        self.assertEqual(row[3],"Dinner foods")
        self.assertIn("dinner foods",row[4])

    def test_long_result_filename_is_saved_with_short_import_name(self):
        from app import app
        base=self.runtime_root();db=base/"test.db";con=sqlite3.connect(db)
        con.executescript("""
        CREATE TABLE chatgpt_requests(request_id TEXT PRIMARY KEY,package_id TEXT UNIQUE,mode TEXT,schema_version TEXT,prompt_version TEXT,requested_features_json TEXT,package_hash TEXT,manifest_json TEXT,created_at TEXT,status TEXT,result_path TEXT,result_hash TEXT,validation_status TEXT,applied_status TEXT,notes TEXT);
        CREATE TABLE chatgpt_request_videos(request_id TEXT,video_id TEXT,source_snapshot_hash TEXT,evidence_manifest_json TEXT,requested_features_json TEXT,PRIMARY KEY(request_id,video_id));
        CREATE TABLE video_feature_coverage(video_id TEXT,feature_id TEXT,feature_version TEXT,status TEXT,source_snapshot_hash TEXT,package_id TEXT,result_hash TEXT,evidence_coverage TEXT,completed_at TEXT,stale_reason TEXT,last_error TEXT,PRIMARY KEY(video_id,feature_id,feature_version));
        CREATE TABLE videos(video_id TEXT PRIMARY KEY,duration_seconds REAL,local_folder TEXT);
        CREATE TABLE chatgpt_import_field_history(id TEXT,video_id TEXT,feature_id TEXT,field_path TEXT,old_value TEXT,new_value_hash TEXT,action TEXT,review_status TEXT,created_at TEXT);
        """)
        con.execute("INSERT INTO chatgpt_requests VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",("req","vh_full_intelligence_20260905_162917_f2cfb8","FULL_INTELLIGENCE","3.0","p",json.dumps([]),"",json.dumps({}),"2026-09-06","AWAITING_RESULT","","","","",""))
        con.commit();con.close()
        raw=json.dumps({"package_id":"vh_full_intelligence_20260905_162917_f2cfb8","schema_version":"3.0","video_updates":[]})
        long_name="vh_full_intelligence_20260905_162917_f2cfb8_20260906_022755_RESULT_vh_full_intelligence_20260905_162917_f2cfb8_"+"x"*170+".json"
        with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)),patch.object(app,"_validate_chatgpt_package_integrity",return_value=([],[])),patch.object(app,"_chatgpt_package_evidence_index",return_value={}),patch.object(app,"refresh_chatgpt_final_batch_validation",return_value={}):
            result=app.import_validate_manual_chatgpt_processing_result({"filename":long_name,"result_json":raw})
        saved=Path(result["result_file"])
        self.assertTrue(saved.is_file())
        self.assertLess(len(saved.name),130)
        self.assertEqual(saved.name,"RESULT_vh_full_intelligence_20260905_162917_f2cfb8.json")
        changed=json.dumps({"package_id":"vh_full_intelligence_20260905_162917_f2cfb8","schema_version":"3.0","video_updates":[],"batch_validation_status":"PASS"})
        with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)),patch.object(app,"_validate_chatgpt_package_integrity",return_value=([],[])),patch.object(app,"_chatgpt_package_evidence_index",return_value={}),patch.object(app,"refresh_chatgpt_final_batch_validation",return_value={}):
            again=app.import_validate_manual_chatgpt_processing_result({"filename":long_name,"result_json":changed,"session_folder":str(saved.parent)})
        self.assertEqual(Path(again["result_file"]).name,"RESULT_vh_full_intelligence_20260905_162917_f2cfb8.json")
        archived=list((base/"data"/"chatgpt"/"exchange"/"incoming"/"full_intelligence"/"duplicate_imports").glob("RESULT_vh_full_intelligence_20260905_162917_f2cfb8_*.json"))
        self.assertEqual(len(archived),1)

    def test_partial_result_writes_modular_reprocess_manifest(self):
        from app import app
        base=self.runtime_root();db=base/"test.db";con=sqlite3.connect(db)
        con.executescript("""
        CREATE TABLE chatgpt_requests(request_id TEXT PRIMARY KEY,package_id TEXT UNIQUE,mode TEXT,schema_version TEXT,prompt_version TEXT,requested_features_json TEXT,package_hash TEXT,manifest_json TEXT,created_at TEXT,status TEXT,result_path TEXT,result_hash TEXT,validation_status TEXT,applied_status TEXT,notes TEXT);
        CREATE TABLE chatgpt_request_videos(request_id TEXT,video_id TEXT,source_snapshot_hash TEXT,evidence_manifest_json TEXT,requested_features_json TEXT,PRIMARY KEY(request_id,video_id));
        CREATE TABLE video_feature_coverage(video_id TEXT,feature_id TEXT,feature_version TEXT,status TEXT,source_snapshot_hash TEXT,package_id TEXT,result_hash TEXT,evidence_coverage TEXT,completed_at TEXT,stale_reason TEXT,last_error TEXT,PRIMARY KEY(video_id,feature_id,feature_version));
        CREATE TABLE videos(video_id TEXT PRIMARY KEY,duration_seconds REAL,local_folder TEXT);
        CREATE TABLE chatgpt_import_field_history(id TEXT,video_id TEXT,feature_id TEXT,field_path TEXT,old_value TEXT,new_value_hash TEXT,action TEXT,review_status TEXT,created_at TEXT);
        """)
        manifest={"prompt_version":"test-prompt","hashes":{"CHATGPT_PACKAGE.json":"abc123"}}
        con.execute("INSERT INTO chatgpt_requests VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",("req","pkg_partial","FULL_INTELLIGENCE","3.0","p",json.dumps(["title_en.v1"]),"",json.dumps(manifest),"2026-09-06","AWAITING_RESULT","","","","",""))
        for vid in ["v1","v2"]:
            con.execute("INSERT INTO chatgpt_request_videos VALUES(?,?,?,?,?)",("req",vid,"","{}",json.dumps(["title_en.v1"])))
            con.execute("INSERT INTO video_feature_coverage VALUES(?,?,?,?,?,?,?,?,?,?,?)",(vid,"title_en","v1","REQUESTED","","pkg_partial","","","", "", ""))
            con.execute("INSERT INTO videos VALUES(?,?,?)",(vid,10,""))
        con.commit();con.close()
        raw=json.dumps({"package_id":"pkg_partial","schema_version":"3.0","batch_validation_status":"PASS_WITH_WARNINGS","video_updates":[{"video_id":"v1","processing_status":"REPROCESS_RECOMMENDED","evidence_grade":"A","confidence":"medium","evidence_references":[{"source":"canonical_transcript","segment_ids":["s00001"]}],"source_conflicts":[],"validation":{"status":"PASS_WITH_WARNINGS","warnings":["weak title"],"repair_attempts":0},"features":{"title_en.v1":{"new_title":"Better Title","short_title":"Better","reason":"test"}},"targeted_review_hints":[{"field":"title_en.v1","reason":"weak"}]}]})
        evidence={"v1":{"sources":{"metadata","canonical_transcript","transcript"},"segment_ids":{"s00001"},"canonical_segment_count":1,"segment_texts":["hello world"],"transcript_max_seconds":10}}
        with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)),patch.object(app,"_validate_chatgpt_package_integrity",return_value=([],[])),patch.object(app,"_chatgpt_package_evidence_index",return_value=evidence),patch.object(app,"refresh_chatgpt_final_batch_validation",return_value={}):
            result=app.import_validate_manual_chatgpt_processing_result({"filename":"RESULT_pkg_partial.json","result_json":raw})
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"],"PARTIAL")
        self.assertEqual(result["package_completion_status"],"INTERRUPTED")
        artifacts=result["modular_artifacts"]
        self.assertTrue(Path(artifacts["reprocess_manifest_json"]).is_file())
        manifest=json.loads(Path(artifacts["reprocess_manifest_json"]).read_text(encoding="utf-8"))
        self.assertEqual(manifest["total_videos"],2)
        self.assertEqual(len(manifest["videos_to_repackage"]),1)
        self.assertEqual(manifest["unfinished_videos"],["v2"])
        checkpoint=json.loads(Path(artifacts["checkpoint"]).read_text(encoding="utf-8"))
        self.assertEqual(checkpoint["artifact_status_by_video"]["v1"],"COMPLETE")
        self.assertEqual(checkpoint["artifact_status_by_video"]["v2"],"JSON_COMPLETE_HTML_PENDING")
        self.assertTrue(Path(artifacts["targeted_pass2_request_file"]).is_file())

    def test_v334_non_english_generated_prose_creates_targeted_repair(self):
        from app import app
        base=self.runtime_root();db=base/"test.db";con=sqlite3.connect(db)
        con.executescript("""
        CREATE TABLE chatgpt_requests(request_id TEXT PRIMARY KEY,package_id TEXT UNIQUE,mode TEXT,schema_version TEXT,prompt_version TEXT,requested_features_json TEXT,package_hash TEXT,manifest_json TEXT,created_at TEXT,status TEXT,result_path TEXT,result_hash TEXT,validation_status TEXT,applied_status TEXT,notes TEXT);
        CREATE TABLE chatgpt_request_videos(request_id TEXT,video_id TEXT,source_snapshot_hash TEXT,evidence_manifest_json TEXT,requested_features_json TEXT,PRIMARY KEY(request_id,video_id));
        CREATE TABLE video_feature_coverage(video_id TEXT,feature_id TEXT,feature_version TEXT,status TEXT,source_snapshot_hash TEXT,package_id TEXT,result_hash TEXT,evidence_coverage TEXT,completed_at TEXT,stale_reason TEXT,last_error TEXT,PRIMARY KEY(video_id,feature_id,feature_version));
        CREATE TABLE videos(video_id TEXT PRIMARY KEY,duration_seconds REAL,local_folder TEXT);
        CREATE TABLE chatgpt_import_field_history(id TEXT,video_id TEXT,feature_id TEXT,field_path TEXT,old_value TEXT,new_value_hash TEXT,action TEXT,review_status TEXT,created_at TEXT);
        """)
        manifest={"prompt_version":"3.3.4-final","prompt_hash":"prompt-hash","hashes":{"CHATGPT_PACKAGE.json":"abc123"}}
        con.execute("INSERT INTO chatgpt_requests VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",("req","pkg_hindi","FULL_INTELLIGENCE","3.3","3.3.4-final",json.dumps(["detailed_summary.v3"]),"",json.dumps(manifest),"2026-09-06","AWAITING_RESULT","","","","",""))
        con.execute("INSERT INTO chatgpt_request_videos VALUES(?,?,?,?,?)",("req","v1","","{}",json.dumps(["detailed_summary.v3"])))
        con.execute("INSERT INTO video_feature_coverage VALUES(?,?,?,?,?,?,?,?,?,?,?)",("v1","detailed_summary","v3","REQUESTED","","pkg_hindi","","","", "", ""))
        con.execute("INSERT INTO videos VALUES(?,?,?)",("v1",10,""));con.commit();con.close()
        hindi="यह वीडियो भोजन और स्वास्थ्य के बारे में बहुत लंबा विवरण देता है और पूरी रिपोर्ट हिंदी में लिखी गई है।"
        raw=json.dumps({"package_id":"pkg_hindi","schema_version":"3.3","video_updates":[{"video_id":"v1","processing_status":"PASS","evidence_grade":"A","confidence":"medium","evidence_references":[],"source_conflicts":[],"validation":{"status":"PASS","warnings":[],"repair_attempts":0},"features":{"detailed_summary.v3":{"overview":hindi,"sections":[],"practical_details":[],"limitations":[],"source_basis":["canonical_transcript"]}}}]})
        with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)),patch.object(app,"_validate_chatgpt_package_integrity",return_value=([],[])),patch.object(app,"_chatgpt_package_evidence_index",return_value={}),patch.object(app,"refresh_chatgpt_final_batch_validation",return_value={}):
            result=app.import_validate_manual_chatgpt_processing_result({"filename":"RESULT_pkg_hindi.json","result_json":raw})
        pass2=json.loads(Path(result["modular_artifacts"]["targeted_pass2_request_file"]).read_text(encoding="utf-8"))
        self.assertEqual(pass2["requests"][0]["validation_code"],"NON_ENGLISH_GENERATED_PROSE")

    def test_v334_resume_checkpoint_first_unfinished_and_render_only(self):
        from app import app
        expected=[f"v{i:02d}" for i in range(1,26)]
        updates=[{"video_id":vid,"processing_status":"PASS","features":{"title_en.v1":{"title":"Title","short_title":"Title","reason":"ok"}}} for vid in expected[:12]]
        artifacts=app._write_chatgpt_modular_package_artifacts("pkg_resume",self.runtime_root(),expected,updates,[],["title_en.v1"],{"prompt_hash":"h","prompt_version":"3.3.4-final"}, "rh")
        checkpoint=json.loads(Path(artifacts["checkpoint"]).read_text(encoding="utf-8"))
        self.assertEqual(checkpoint["next_video_id"],"v13")
        self.assertTrue(all(checkpoint["video_processing_state_by_video"][vid]=="SEMANTIC_COMPLETE" for vid in expected[:12]))
        self.assertEqual(checkpoint["video_processing_state_by_video"]["v13"],"INTERRUPTED")
        self.assertEqual(checkpoint["artifact_status_by_video"]["v13"],"JSON_COMPLETE_HTML_PENDING")

    def test_v334_renderer_error_records_artifact_status_separately(self):
        from app import app
        expected=["v13"]
        updates=[{"video_id":"v13","processing_status":"PASS","features":{"title_en.v1":{"new_title":"Title","short_title":"Title","reason":"ok"}}}]
        with patch.object(app,"_chatgpt_v334_render_html",return_value=("<html>processing_status leaked</html>",["processing_status"])):
            artifacts=app._write_chatgpt_modular_package_artifacts("pkg_render_error",self.runtime_root(),expected,updates,[],["title_en.v1"],{"prompt_hash":"h","prompt_version":"3.3.4-final"}, "rh")
        checkpoint=json.loads(Path(artifacts["checkpoint"]).read_text(encoding="utf-8"))
        manifest=json.loads(Path(artifacts["reprocess_manifest_json"]).read_text(encoding="utf-8"))
        result_record=json.loads((Path(artifacts["results_folder"])/"v13.json").read_text(encoding="utf-8"))
        self.assertEqual(checkpoint["semantic_status_by_video"]["v13"],"PASS")
        self.assertEqual(checkpoint["artifact_status_by_video"]["v13"],"RENDER_ERROR")
        self.assertEqual(result_record["artifact_status"],"RENDER_ERROR")
        self.assertEqual(manifest["semantic_package_status"],"COMPLETE")
        self.assertEqual(manifest["artifact_package_status"],"COMPLETE_WITH_ERRORS")

    def test_adaptive_chatgpt_package_chunks_target_twenty_five_and_size_limits(self):
        from app import app
        ids=[f"v{i:02d}" for i in range(25)]
        lengths={vid:5000 for vid in ids}
        chunks=app.chatgpt_adaptive_package_chunks("Topic",ids,lengths,False)
        self.assertEqual([len(c[1]) for c in chunks],[25])
        self.assertTrue(all(len(c[1])<=25 for c in chunks))
        heavy={vid:30000 for vid in ids[:10]}
        heavy_chunks=app.chatgpt_adaptive_package_chunks("Heavy",ids[:10],heavy,False)
        self.assertTrue(all(c[2]<=app.CHATGPT_HARD_TRANSCRIPT_CHARS for c in heavy_chunks))
        self.assertTrue(any(len(c[1])<10 for c in heavy_chunks))

    def test_library_rebuild_creates_per_channel_thumbnail_pages_and_hides_deleted_folders(self):
        from app import app
        base=self.runtime_root();db=base/"test.db";con=sqlite3.connect(db)
        available=base/"videos"/"Fit Channel"/"video_a";data=available/"_data";data.mkdir(parents=True)
        thumb=data/"vid_a.jpg";thumb.write_bytes(b"fake-jpg")
        missing=base/"videos"/"Fit Channel"/"video_b"
        con.executescript("""
        CREATE TABLE videos(video_id TEXT,url TEXT,original_title TEXT,clean_title TEXT,channel TEXT,upload_date TEXT,category TEXT,subcategory TEXT,downloaded INTEGER,archived INTEGER,local_folder TEXT,local_video TEXT,report_html TEXT,thumbnail_url TEXT);
        CREATE TABLE youtube_subscriptions(channel_key TEXT,channel_id TEXT,handle TEXT,title TEXT,url TEXT,description TEXT,subscriber_text TEXT,video_count_text TEXT,dominant_category TEXT,selected_for_scan INTEGER,source TEXT,collected_at TEXT);
        """)
        con.execute("INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",("vid_a","https://www.youtube.com/watch?v=vid_a","Workout Title","Workout Clean","Fit Channel","2026-01-01","Fitness","Workout",1,0,str(available),"","", ""))
        con.execute("INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",("vid_b","https://www.youtube.com/watch?v=vid_b","Deleted Folder Title","Deleted Clean","Fit Channel","2026-01-02","Fitness","Workout",1,0,str(missing),"","", ""))
        con.commit();con.close()
        fake_csv=base/"export.csv";fake_csv.write_text("ok",encoding="utf-8")
        with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)),patch.object(app,"export_csv",return_value=str(fake_csv)),patch.object(app,"export_csv_with_chatgpt_titles",return_value=""),patch.object(app,"phase5_build_all",return_value=None):
            result=app.rebuild_database_and_library_exports()
        self.assertTrue(result["ok"])
        self.assertEqual(result["counts"]["available_downloaded_videos"],1)
        self.assertEqual(result["counts"]["missing_local_folders"],1)
        self.assertTrue(Path(result["missing_videos_csv"]).is_file())
        self.assertTrue(Path(result["missing_videos_html"]).is_file())
        missing_csv=Path(result["missing_videos_csv"]).read_text(encoding="utf-8-sig")
        missing_html=Path(result["missing_videos_html"]).read_text(encoding="utf-8")
        self.assertIn("Deleted Folder Title",missing_csv)
        self.assertIn("missing_local_folder",missing_csv)
        self.assertIn("Deleted Folder Title",missing_html)
        self.assertFalse((Path(result["csv_folder"])/"deleted_or_missing_videos.csv").exists())
        self.assertFalse((Path(result["html_folder"])/"deleted_or_missing_videos.html").exists())
        current_html=Path(result["current_videos_html"]).read_text(encoding="utf-8")
        self.assertIn("Edit notes/comments",current_html)
        self.assertIn("/api/video-user-comments",current_html)
        index=Path(result["channels_index_html"])
        self.assertTrue(index.is_file())
        channel_pages=list(Path(result["channel_html_folder"]).glob("*.html"))
        self.assertEqual(len(channel_pages),1)
        html_text=channel_pages[0].read_text(encoding="utf-8")
        self.assertIn("Workout Title",html_text)
        self.assertIn("https://www.youtube.com/watch?v=vid_a",html_text)
        self.assertIn("vid_a.jpg",html_text)
        self.assertIn("Edit notes/comments",html_text)
        self.assertNotIn("Deleted Folder Title",html_text)
        with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)):
            saved=app.save_user_video_comments("vid_a",[{"text":"Useful protein point"},{"text":"Rewatch later"}])
            loaded=app.load_user_video_comments("vid_a")
            removed=app.save_user_video_comments("vid_a",[])
        self.assertTrue(saved["ok"])
        self.assertEqual(loaded["count"],2)
        self.assertTrue(removed["ok"])
        self.assertFalse(Path(saved["path"]).exists())

    def test_package_integrity_detects_tamper(self):
        from app import app
        base = Path.cwd()/"tests"/"fixtures"/"chatgpt_integrity"
        root = base / "data" / "chatgpt" / "exchange" / "outgoing" / "pkg"
        evidence = root / "evidence.json"
        manifest_path = root / "manifest.json"
        manifest = {"package_id":"pkg","hashes": {"evidence.json": hashlib.sha256(evidence.read_bytes()).hexdigest()}}
        manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        with patch.object(app, "BASE", base):
            errors, verified = app._validate_chatgpt_package_integrity("pkg", manifest, manifest_hash)
            self.assertEqual(errors, [])
            self.assertEqual(verified, ["evidence.json"])
            bad_manifest={"package_id":"pkg","hashes":{"evidence.json":"0"*64}}
            errors, _ = app._validate_chatgpt_package_integrity("pkg", bad_manifest, manifest_hash)
            self.assertTrue(any("checksum mismatch" in value.lower() for value in errors))

    def test_provenance_index_reports_only_present_evidence(self):
        from app import app
        base=self.runtime_root()
        folder=base/"data"/"chatgpt"/"exchange"/"outgoing"/"pkg";folder.mkdir(parents=True)
        try:
            (folder/"evidence.json").write_text(json.dumps({"videos":[{"video_id":"abc","metadata":{"description":"available"},"evidence":{"transcript":"[00:05] text [00:42] end","comments":"","manifest":{"subtitle":True}}}]}),encoding="utf-8")
            with patch.object(app,"BASE",base):row=app._chatgpt_package_evidence_index("pkg")["abc"]
            self.assertIn("transcript",row["sources"])
            self.assertIn("subtitle",row["sources"])
            self.assertNotIn("comments",row["sources"])
            self.assertEqual(row["transcript_max_seconds"],42)
        finally:pass

    def test_clip_plan_validates_order_duration_and_handoff(self):
        from app import app
        base=self.runtime_root();db=base/"test.db";con=sqlite3.connect(db)
        try:
            con.execute("CREATE TABLE videos(video_id TEXT, local_video TEXT, duration_seconds REAL)")
            con.execute("INSERT INTO videos VALUES('abc','C:/videos/abc.mp4',60)");con.commit();con.close()
            with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)):
                result=app.validate_chatgpt_clip_plan({"plan":{"clips":[{"video_id":"abc","start_timestamp":"00:10","end_timestamp":"00:20","included":True}]}},True)
                self.assertTrue(result["valid"])
                self.assertEqual(result["clips"][0]["order"],1)
                self.assertEqual(result["clips"][0]["duration"],10)
                self.assertFalse(result["executed"])
                self.assertTrue(Path(result["saved"]).is_file())
        finally:pass

    def test_duplicate_review_requires_canonical_and_never_deletes(self):
        from app import app
        with patch.object(app,"BASE",self.runtime_root()):
            result=app.record_chatgpt_duplicate_review({"group":{"group_name":"same","video_ids":["a","b"]},"canonical_video_id":"a","choices":[{"video_id":"a","decision":"keep"},{"video_id":"b","decision":"mark_delete"}]})
            self.assertTrue(result["ok"])
            self.assertFalse(result["review"]["physical_changes_applied"])
            self.assertTrue(result["review"]["manual_delete_only"])

    def test_planner_import_validates_integrity_and_group_limits(self):
        from app import app
        base=self.runtime_root();package="planner";folder=base/"data"/"chatgpt"/"exchange"/"outgoing"/package;folder.mkdir(parents=True)
        try:
            (folder/"catalog.json").write_text("{}",encoding="utf-8")
            manifest={"package_id":package,"video_ids":["a","b"],"transcript_preflight":{"available_ids":["a"]},"hashes":{"catalog.json":hashlib.sha256((folder/"catalog.json").read_bytes()).hexdigest()}}
            (folder/"manifest.json").write_text(json.dumps(manifest),encoding="utf-8");package_hash=hashlib.sha256((folder/"manifest.json").read_bytes()).hexdigest()
            db=base/"test.db";con=sqlite3.connect(db);con.execute("CREATE TABLE chatgpt_requests(request_id TEXT,package_id TEXT,schema_version TEXT,mode TEXT,manifest_json TEXT,package_hash TEXT,status TEXT,result_path TEXT,result_hash TEXT,validation_status TEXT)")
            con.execute("INSERT INTO chatgpt_requests VALUES(?,?,?,?,?,?,?,?,?,?)",("r",package,"3.0","BATCH_PLANNING",json.dumps(manifest),package_hash,"AWAITING_PLAN","","",""));con.commit();con.close()
            plan={"package_id":package,"schema_version":"3.0","transcript_groups":[{"group_name":"with","video_ids":["a"]}],"no_transcript_groups":[{"group_name":"without","video_ids":["b"]}],"parent_groups":{"transcript_parent_groups":[{"parent_group_name":"with parent","topic_subgroups":[{"group_name":"with","video_ids":["a"]}],"video_ids":["a"]}],"no_transcript_parent_groups":[{"parent_group_name":"without parent","topic_subgroups":[{"group_name":"without","video_ids":["b"]}],"video_ids":["b"]}]}}
            with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)):
                result=app.import_validate_chatgpt_batch_plan({"result_json":json.dumps(plan)})
            self.assertTrue(result["valid"])
            self.assertEqual(result["transcript_parent_groups"],1)
            self.assertIn("catalog.json",result["verified_package_files"])
        finally:pass


    def test_planner_small_parent_group_no_longer_requires_exception(self):
        from app import app
        base=self.runtime_root();package="planner_small";folder=base/"data"/"chatgpt"/"exchange"/"outgoing"/package;folder.mkdir(parents=True)
        try:
            (folder/"catalog.json").write_text("{}",encoding="utf-8")
            ids=[f"v{i:02d}" for i in range(20)]
            manifest={"package_id":package,"video_ids":ids,"transcript_preflight":{"available_ids":[]},"hashes":{"catalog.json":hashlib.sha256((folder/"catalog.json").read_bytes()).hexdigest()},"planner_quality_version":"1"}
            (folder/"manifest.json").write_text(json.dumps(manifest),encoding="utf-8");package_hash=hashlib.sha256((folder/"manifest.json").read_bytes()).hexdigest()
            db=base/"test.db";con=sqlite3.connect(db);con.execute("CREATE TABLE chatgpt_requests(request_id TEXT,package_id TEXT,schema_version TEXT,mode TEXT,manifest_json TEXT,package_hash TEXT,status TEXT,result_path TEXT,result_hash TEXT,validation_status TEXT)")
            con.execute("INSERT INTO chatgpt_requests VALUES(?,?,?,?,?,?,?,?,?,?)",("r",package,"3.3","BATCH_PLANNING",json.dumps(manifest),package_hash,"AWAITING_PLAN","","",""));con.commit();con.close()
            subgroup1={"group_name":"Entertainment niche","group_reason":"Distinct specialized entertainment subject","grouping_basis":"topic_first","recommended_profile":"NO_TRANSCRIPT_METADATA","video_ids":ids[:7]}
            subgroup2={"group_name":"Health metadata","group_reason":"Separate health-related metadata topic","grouping_basis":"topic_first","recommended_profile":"NO_TRANSCRIPT_METADATA","video_ids":ids[7:]}
            parent1={"parent_group_name":"Entertainment & Specialized Topics","parent_group_reason":"Distinct entertainment affinity group.","recommended_profile":"NO_TRANSCRIPT_METADATA","topic_subgroups":[{"group_name":subgroup1["group_name"],"video_ids":ids[:7]}],"video_ids":ids[:7]}
            parent2={"parent_group_name":"Health Metadata Topics","parent_group_reason":"Related health metadata affinity group.","recommended_profile":"NO_TRANSCRIPT_METADATA","topic_subgroups":[{"group_name":subgroup2["group_name"],"video_ids":ids[7:]}],"video_ids":ids[7:]}
            plan={"package_id":package,"schema_version":"3.3","transcript_groups":[],"no_transcript_groups":[subgroup1,subgroup2],"parent_groups":{"transcript_parent_groups":[],"no_transcript_parent_groups":[parent1,parent2]}}
            with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)):
                accepted=app.import_validate_chatgpt_batch_plan({"result_json":json.dumps(plan)})
            self.assertTrue(accepted["valid"],accepted["errors"])
        finally:pass


    def test_local_batch_processor_status_only_does_not_generate_fake_semantics(self):
        import sys
        sys.path.insert(0,str(Path.cwd()/"scripts"))
        import process_batch_packages as processor
        package={"package_id":"pkg1","schema_version":"3.0","videos":[{"video_id":"abc","metadata":{"original_title":"Actual Title","clean_title":"Clean Title","channel":"Channel","source_category":"Health"},"requested_features":["title_en.v1","taxonomy.v3","executive_summary.v2","quality_validation.v1"],"evidence":{"canonical_transcript":{"segments":[{"segment_id":"s00001","start_timestamp":"00:00:00","end_timestamp":"00:00:45","start_seconds":0,"end_seconds":45,"text":"Useful source text for testing."}]},"comments":{"total_comments":0,"included_comments":0,"sampling_method":"none","records":[]},"assessment":{"transcript_available":True,"evidence_grade":"A","canonical_segment_count":1,"transcript_completeness":"usable","source_consistency":"consistent","source_conflicts":[]}}}]}
        with self.assertRaises(RuntimeError):
            processor.build_result(package,"minimal")


    def test_v334_flattened_inline_timestamps_are_normalized_before_health(self):
        from app import app
        transcript=(
            "[00:00:00] Opening explanation with enough useful spoken words. "
            "[00:00:10] Second topic continues with useful details and examples. "
            "[00:00:25] Final point explains the recommendation clearly."
        )
        fragments=app._chatgpt_caption_fragments(transcript,30)
        self.assertEqual(len(fragments),3)
        self.assertEqual(fragments[0][0],0)
        self.assertEqual(fragments[0][1],10)
        self.assertEqual(fragments[1][0],10)
        self.assertEqual(fragments[1][1],25)
        self.assertEqual(fragments[2][0],25)
        # Final marker has no explicit end; video duration must not be used to
        # imply that speech continues to media end.
        self.assertEqual(fragments[2][1],25)
        health=app.chatgpt_transcript_health(transcript,30,{})
        self.assertGreaterEqual(health["signals"]["timestamp_parse_rate"],0.99)
        self.assertNotIn("TIMESTAMP_PARSE_WEAK",health["reason_codes"])

    def test_v334_transcript_source_identity_never_says_no_transcript_when_timestamped_text_exists(self):
        from app import app
        transcript=(
            "[00:00:00] This is useful spoken transcript content for testing. "
            "[00:00:12] It continues with enough information to remain usable. "
            "[00:00:24] The final segment contains a clear concluding explanation."
        )
        result=app.chatgpt_canonical_evidence(
            "abc",
            {"original_title":"Example","duration_seconds":30},
            {},transcript,"en",""
        )
        self.assertTrue(result["transcript_available"])
        self.assertEqual(result["transcript_source"],"timestamped_transcript")
        self.assertEqual(result["canonical_transcript"]["source"],"timestamped_transcript")
        self.assertEqual(result["normalization_status"],"NORMALIZED_TIMESTAMPED")
        self.assertGreaterEqual(result["canonical_segment_count"],2)
        self.assertFalse(all(x["start_seconds"]==0 and x["end_seconds"]==0 for x in result["canonical_transcript"]["segments"]))


    def test_v334_exact_eight_marker_flattened_transcript_uses_shared_detector(self):
        from app import app
        transcript=(
            "00:00:00 Opening explanation with useful spoken words. "
            "00:00:08 Second point has enough detail for a canonical segment. "
            "00:00:17 Third point continues the topic clearly. "
            "00:00:29 Fourth point adds a concrete example. "
            "00:00:41 Fifth point explains another recommendation. "
            "00:00:53 Sixth point adds supporting detail. "
            "00:01:05 Seventh point gives a practical conclusion. "
            "00:01:18 Final point closes the discussion clearly."
        )
        markers=app._chatgpt_timestamp_matches(transcript)
        self.assertEqual(len(markers),8)
        fragments=app._chatgpt_caption_fragments(transcript,90)
        self.assertEqual(len(fragments),8)
        self.assertEqual([x[0] for x in fragments[:3]],[0,8,17])
        health=app.chatgpt_transcript_health(transcript,90,{})
        self.assertEqual(health["signals"]["timestamp_parse_rate"],1.0)
        self.assertNotIn("TIMESTAMP_PARSE_WEAK",health["reason_codes"])
        evidence=app.chatgpt_canonical_evidence(
            "_d1VU6A5Cd4",
            {"original_title":"Eight-marker regression","duration_seconds":90},
            {},transcript,"en",""
        )
        self.assertTrue(evidence["transcript_available"])
        self.assertEqual(evidence["canonical_transcript"]["source"],"timestamped_transcript")
        self.assertGreater(evidence["canonical_segment_count"],1)
        self.assertFalse(all(x["start_seconds"]==0 and x["end_seconds"]==0 for x in evidence["canonical_transcript"]["segments"]))

    def test_v334_shared_timestamp_detector_accepts_common_variants(self):
        from app import app
        transcript=(
            "[0:00] first segment text. "
            "[00:12.500] second segment text. "
            "[01:02,250] third segment text. "
            "1:15:03 final long-form segment text."
        )
        markers=app._chatgpt_timestamp_matches(transcript)
        self.assertEqual(len(markers),4)
        self.assertEqual([x[2] for x in markers],["0:00","00:12.500","01:02.250","1:15:03"])

    def test_v334_usable_transcript_falls_back_when_timestamp_normalization_fails(self):
        from app import app
        transcript=(
            "[00:00:00] Opening explanation contains useful spoken information. "
            "[00:00:12] Another useful point continues with enough semantic detail. "
            "[00:00:25] Final recommendation is clear and useful."
        )
        with patch.object(app,"_chatgpt_caption_fragments",return_value=[]):
            evidence=app.chatgpt_canonical_evidence(
                "fallback1",{"original_title":"Fallback test","duration_seconds":30},{},transcript,"en",""
            )
        self.assertTrue(evidence["transcript_available"])
        self.assertFalse(evidence["timestamps_available"])
        self.assertEqual(evidence["transcript_source"],"untimestamped_transcript")
        self.assertEqual(evidence["normalization_status"],"UNTIMESTAMPED_FALLBACK")
        canonical=evidence["canonical_transcript"]
        self.assertEqual(canonical["segments"],[])
        self.assertTrue(canonical["untimestamped_text"])
        self.assertNotIn("[00:00:12]",canonical["untimestamped_text"])
        self.assertTrue(canonical["timestamp_hints_available"])
        self.assertFalse(canonical["timestamp_hints_reliable"])
        self.assertEqual(canonical["timestamp_hint_count"],3)
        self.assertEqual([h["source_timestamp"] for h in canonical["timestamp_hints"]],["00:00:00","00:00:12","00:00:25"])
        self.assertIn("approximate navigation clues",canonical["timestamp_instruction"].lower())
        self.assertIn("another useful point",canonical["timestamp_hints"][1]["text_excerpt"].lower())

    def test_v334_timestamp_only_health_problem_remains_packageable_caution(self):
        from app import app
        transcript=(
            "[00:00:30] This transcript has useful spoken content and explanations. "
            "[00:00:10] The timestamp order is wrong but the semantic text is still usable. "
            "[00:00:20] More useful speech remains available for semantic processing."
        )
        health=app.chatgpt_transcript_health(transcript,40,{})
        self.assertNotIn(health["routing_class"],{"REPAIR_REQUIRED","REPAIR_RECOMMENDED"})
        self.assertIn(health["routing_class"],{"CAUTION","NORMAL"})

    def test_v334_timestamp_hints_preserve_source_markers_compactly(self):
        from app import app
        transcript=(
            "Intro before marker [00:00] first topic text about breakfast choices. "
            "[00:12.500] second topic text about ingredients and labels. "
            "[01:02,250] third topic text with a recommendation."
        )
        data=app._chatgpt_timestamp_hints(transcript)
        self.assertTrue(data["available"])
        self.assertFalse(data["reliable"])
        self.assertEqual(data["total_detected"],3)
        self.assertEqual([h["source_timestamp"] for h in data["hints"]],["00:00","00:12.500","01:02.250"])
        self.assertEqual(data["hints"][1]["source_seconds"],12.5)
        self.assertIn("second topic",data["hints"][1]["text_excerpt"].lower())

    def test_v334_master_prompt_preserves_approximate_hints_without_timestamp_repair(self):
        from app import app
        prompt=app.chatgpt_master_modular_sequential_prompt().lower()
        self.assertIn("timestamps_available = false",prompt)
        self.assertIn("timestamp_hints_available = true",prompt)
        self.assertIn("approximate source-provided navigation clues",prompt)
        self.assertIn("do not spend significant reasoning time",prompt)
        self.assertIn("do not present them as exact timestamps",prompt)
        self.assertIn("chapters.v1.chapters",prompt)


    def test_v334_active_library_migration_columns_exist(self):
        from app import app
        base=self.runtime_root();db=base/"active.db";con=sqlite3.connect(db)
        con.execute("CREATE TABLE videos(video_id TEXT PRIMARY KEY, url TEXT, upload_date TEXT)");con.commit();con.close()
        with patch.object(app,"BASE",base),patch.object(app,"DB",db):
            migrated=app.db_connect()
            columns={row[1] for row in migrated.execute("PRAGMA table_info(videos)").fetchall()}
            migrated.close()
        for name in ("current_present","deleted_from_library","deleted_at","last_transcript_recheck_at","last_transcript_recheck_status"):
            self.assertIn(name,columns)

    def test_v334_global_optimizer_minimizes_package_count_and_max_30(self):
        from app import app
        ids=[f"v{i:03d}" for i in range(61)]
        lengths={v:1000 for v in ids}
        chunks=app.chatgpt_optimize_full_intelligence_packages(ids,lengths,{},max_videos=30,hard_chars=1000000)
        self.assertEqual(len(chunks),3)
        sizes=sorted(len(c[1]) for c in chunks)
        self.assertEqual(sum(sizes),61)
        self.assertLessEqual(max(sizes),30)
        self.assertGreaterEqual(min(sizes),20)

    def test_v334_global_optimizer_has_no_minimum_package_size(self):
        from app import app
        ids=["a","b","c","d"]
        chunks=app.chatgpt_optimize_full_intelligence_packages(ids,{x:100 for x in ids},{},max_videos=30,hard_chars=1000000)
        self.assertEqual(len(chunks),1)
        self.assertEqual(len(chunks[0][1]),4)

    def test_v334_no_timestamp_based_restricted_intelligence_groups(self):
        import inspect
        from app import app
        source=inspect.getsource(app.create_manual_chatgpt_processing_batch_set)
        self.assertNotIn('("RESTRICTED_INTELLIGENCE",partial_chunks',source)
        self.assertIn("FULL_INTELLIGENCE",source)
        self.assertIn("chatgpt_optimize_full_intelligence_packages",source)

    def test_v334_prompt_full_intelligence_despite_timing_quality(self):
        from app import app
        prompt=app.chatgpt_master_modular_sequential_prompt().lower()
        self.assertIn("full semantic intelligence",prompt)
        self.assertIn("regardless of timestamp quality",prompt)
        self.assertIn("never invent missing timestamps",prompt)
        self.assertIn("hard maximum is 30",prompt)
        self.assertIn("there is no minimum package size",prompt)

    def test_v334_architecture_active_library_and_global_optimizer_rules(self):
        from app import app
        p=Path(app.__file__).resolve().parent.parent/"specs"/"VIDEOHOARDER_ARCHITECTURE_V3_3_4_FINAL.md"
        text=p.read_text(encoding="utf-8").lower()
        self.assertIn("physical active library is authoritative",text)
        self.assertIn("recheck missing / bad transcripts",text)
        self.assertIn("minimize total package count",text)
        self.assertIn("maximum 30 videos",text)
        self.assertIn("there is no minimum package size",text)
        self.assertIn("do not create timestamp-based restricted_intelligence",text)

    def test_v334_redownload_history_uses_guard_not_library_row(self):
        from app import app
        base=self.runtime_root();db=base/"history.db"
        with patch.object(app,"BASE",base),patch.object(app,"DB",db):
            con=app.db_connect();con.close()
            app.remember_deleted_video_for_redownload_guard("abc123XYZ00","Old title","Channel","2026-09-07 10:00:00")
            result=app.redownload_history_check(["https://www.youtube.com/watch?v=abc123XYZ00"])
            con=app.db_connect();row=con.execute("SELECT 1 FROM videos WHERE video_id=?",("abc123XYZ00",)).fetchone();con.close()
        self.assertIsNone(row)
        self.assertTrue(result["requires_confirmation"])
        self.assertEqual(result["items"][0]["status"],"PREVIOUSLY_DELETED")
        self.assertEqual(result["items"][0]["title"],"Old title")

    def test_v334_legacy_deleted_tombstone_migrates_to_guard_and_is_purged(self):
        from app import app
        base=self.runtime_root();db=base/"legacy_deleted.db"
        with patch.object(app,"BASE",base),patch.object(app,"DB",db),patch.object(app,"remove_video_from_cached_indexes",return_value={}):
            con=app.db_connect()
            con.execute("INSERT OR REPLACE INTO videos(video_id,url,original_title,channel,current_present,deleted_from_library,deleted_at) VALUES(?,?,?,?,?,?,?)",
                        ("abc123XYZ00","https://www.youtube.com/watch?v=abc123XYZ00","Old title","Channel",0,1,"2026-09-07 10:00:00"))
            con.commit();con.close()
            app.migrate_legacy_deleted_history_to_guard()
            con=app.db_connect();row=con.execute("SELECT 1 FROM videos WHERE video_id=?",("abc123XYZ00",)).fetchone();con.close()
            result=app.redownload_history_check(["https://www.youtube.com/watch?v=abc123XYZ00"])
        self.assertIsNone(row)
        self.assertTrue(result["requires_confirmation"])
        self.assertEqual(result["items"][0]["status"],"PREVIOUSLY_DELETED")



    def test_v334_package_quality_is_distribution_based_and_workload_independent(self):
        from app import app
        def row(grade,timestamps=True,reasons=None):
            return {"evidence":{"assessment":{"transcript_available":True,"timestamps_available":timestamps,"transcript_health":{"grade":grade,"reason_codes":reasons or [],"hard_failure":False}}}}
        rows=[row("A") for _ in range(24)]+[row("B") for _ in range(4)]+[row("D",False,["SEVERE_TIMESTAMP_CORRUPTION"])]
        metrics=app.chatgpt_package_quality(rows,240000)
        self.assertEqual(metrics["package_quality"]["grade"],"A")
        self.assertGreaterEqual(metrics["package_quality"]["score"],90)
        self.assertEqual(metrics["workload"]["class"],"HIGH")
        self.assertIsNone(metrics["package_quality"]["processing_priority"])

    def test_v334_package_priority_uses_quality_then_timing_then_severe_then_id(self):
        from app import app
        entries=[
            {"package_id":"b","video_count":10,"package_quality":{"score":90,"timestamp_reliable":9,"severe_signal_count":0}},
            {"package_id":"a","video_count":10,"package_quality":{"score":95,"timestamp_reliable":5,"severe_signal_count":2}},
            {"package_id":"c","video_count":10,"package_quality":{"score":90,"timestamp_reliable":8,"severe_signal_count":0}},
        ]
        app.chatgpt_assign_package_priorities(entries)
        by_id={e["package_id"]:e["package_quality"]["processing_priority"] for e in entries}
        self.assertEqual(by_id,{"a":1,"b":2,"c":3})

    def test_v334_reviewed_prompt_contains_source_fidelity_self_audit_and_package_grade_contract(self):
        from app import app
        text=app.chatgpt_master_modular_sequential_prompt()
        self.assertIn("SOURCE-FIDELITY RULE",text)
        self.assertIn("External factual truth is outside this workflow",text)
        self.assertIn("SOURCE_INSUFFICIENT",text)
        self.assertIn("self-review",text.lower())

if __name__ == "__main__":
    unittest.main()



def test_v334_global_optimizer_has_no_minimum_and_max_30():
    import app.app as app
    ids=[f"v{i:03d}" for i in range(61)]
    lengths={v:1000 for v in ids}
    chunks=app.chatgpt_optimize_full_intelligence_packages(ids,lengths,{},max_videos=30,hard_chars=250000)
    assert len(chunks)==3
    sizes=sorted(len(x[1]) for x in chunks)
    assert sum(sizes)==61
    assert max(sizes)<=30
    assert max(sizes)-min(sizes)<=1

def test_v334_global_optimizer_28_stays_one_package():
    import app.app as app
    ids=[f"v{i:03d}" for i in range(28)]
    chunks=app.chatgpt_optimize_full_intelligence_packages(ids,{v:1000 for v in ids},{},max_videos=30,hard_chars=250000)
    assert len(chunks)==1
    assert len(chunks[0][1])==28

def test_v334_prompt_and_architecture_include_full_intelligence_timing_fallback():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    prompt=(root/"app"/"prompts"/"VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md").read_text(encoding="utf-8")
    arch=(root/"specs"/"VIDEOHOARDER_ARCHITECTURE_V3_3_4_FINAL.md").read_text(encoding="utf-8")
    assert "Usable transcript text always receives FULL_INTELLIGENCE" in prompt
    assert "Do not waste reasoning on timestamp recovery" in prompt
    assert "There is **no minimum package size**" in arch
    assert "maximum 30 videos" in arch
    assert "Recheck Missing / Bad Transcripts" in arch

def test_v334_source_has_active_library_and_redownload_contract():
    from pathlib import Path
    src=(Path(__file__).resolve().parents[1]/"app"/"app.py").read_text(encoding="utf-8")
    assert "def reconcile_active_library_state" in src
    assert "def redownload_history_check" in src
    assert "PREVIOUSLY_DELETED" in src
    assert "def recheck_missing_bad_transcripts" in src
    assert 'CHATGPT_MAX_PACKAGE_VIDEOS=30' in src
    # New grouped runs must not instantiate restricted-intelligence chunks.
    assert '("RESTRICTED_INTELLIGENCE",partial_chunks' not in src

def test_v334_chapter_schema_allows_unavailable_timing():
    import app.app as app
    schema=app.chatgpt_formal_result_schema('pkg',['chapters.v1','detailed_summary.v3'],True)
    chapter=schema['properties']['video_updates']['items']['properties']['features']['properties']['chapters.v1']['properties']['chapters']['items']
    assert chapter['properties']['start_timestamp']['type']==['string','null']
    assert chapter['properties']['start_seconds']['type']==['number','null']
    assert 'timestamp_precision' in chapter['properties']

def test_v334_smart_resume_uses_current_active_library_only():
    import inspect, app.app as app
    src=inspect.getsource(app.smart_resume_queue_items)
    assert 'current_present' in src

def test_v334_planner_contract_has_no_small_group_exception():
    from pathlib import Path
    src=(Path(__file__).resolve().parents[1]/'app'/'app.py').read_text(encoding='utf-8')
    # Obsolete package-size enforcement must not be emitted by the planner template/instructions.
    assert 'below-15 groups require small_group_exception' not in src
    assert 'preferred 20-25, maximum 25' not in src
    assert 'CHATGPT_MAX_PACKAGE_VIDEOS=30' in src

def test_v334_documents_have_no_obsolete_25_cap_or_15_minimum():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    prompt=(root/'app'/'prompts'/'VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md').read_text(encoding='utf-8')
    arch=(root/'specs'/'VIDEOHOARDER_ARCHITECTURE_V3_3_4_FINAL.md').read_text(encoding='utf-8')
    for text in (prompt,arch):
        low=text.lower()
        assert 'maximum package size: 25' not in low
        assert 'parent groups should normally contain 15-25' not in low
        assert 'preferred package size: 20-25' not in low
    assert 'hard maximum is 30' in prompt.lower()
    assert 'there is no minimum package size' in arch.lower()


def test_v334_selective_transcript_recheck_policy_is_narrow_and_safe():
    import inspect
    from app import app as APP
    src=inspect.getsource(APP.recheck_missing_bad_transcripts)
    assert 'old_grade in {"A","B"}' in src
    assert '{"C":7*24,"D":3*24,"F":24}' in src
    assert 'if not force and last_at' in src
    assert 'same-grade health improved' in src
    assert 'candidate grade worse' in src
    assert 'transcript.backup.' in src
    assert 'missing/C/D/F only; A/B never queried' in src