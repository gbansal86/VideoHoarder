import hashlib
import json
import shutil
import sqlite3
import unittest
import uuid
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

    def test_timestamp_walker(self):
        from app import app
        rows = app._chatgpt_walk_timestamps({"timeline": [{"start_timestamp": "00:10"}]})
        self.assertIn(("$.timeline[0].start_timestamp", "00:10"), rows)

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
            plan={"package_id":package,"schema_version":"3.0","transcript_groups":[{"group_name":"with","video_ids":["a"]}],"no_transcript_groups":[{"group_name":"without","video_ids":["b"]}]}
            with patch.object(app,"BASE",base),patch.object(app,"db_connect",side_effect=lambda:sqlite3.connect(db)):
                result=app.import_validate_chatgpt_batch_plan({"result_json":json.dumps(plan)})
            self.assertTrue(result["valid"])
            self.assertIn("catalog.json",result["verified_package_files"])
        finally:pass


if __name__ == "__main__":
    unittest.main()
