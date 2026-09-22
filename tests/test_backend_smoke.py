from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import urllib.request


class BackendSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_root = (Path(__file__).parent / "runtime_data").resolve()
        cls.test_root.mkdir(parents=True, exist_ok=True)
        os.environ["VLM_LIBRARY_ROOT"] = str(cls.test_root)
        cls.backend = importlib.import_module("app.app")

    @classmethod
    def tearDownClass(cls) -> None:
        os.environ.pop("VLM_LIBRARY_ROOT", None)

    def test_library_root_override_is_used(self) -> None:
        self.assertEqual(Path(self.backend.BASE), self.test_root)

    def test_config_is_loaded_and_writable(self) -> None:
        self.assertIsInstance(self.backend.CFG, dict)
        self.assertIn("download_quality", self.backend.CFG)
        self.assertEqual(Path(self.backend.CONFIG).parent.name, "app")

    def test_dashboard_starts_without_opening_external_browser(self) -> None:
        with mock.patch.object(self.backend.webbrowser, "open") as browser_open:
            server = self.backend.start_dashboard(open_browser=False)
        try:
            port = int(server.server_address[1])
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/api/progress", timeout=5
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertEqual(response.status, 200)
            self.assertIn("phase", payload)
            browser_open.assert_not_called()
        finally:
            server.shutdown()
            server.server_close()

    def test_legacy_migration_preserves_canonical_health_files(self) -> None:
        audit_dir = self.test_root / "maintenance" / "audits"
        audit_dir.mkdir(parents=True, exist_ok=True)
        health_csv = audit_dir / "library_health.csv"
        health_json = audit_dir / "library_health_summary.json"
        health_csv.write_text("status,detail\nPASS,canonical\n", encoding="utf-8")
        health_json.write_text('{"status":"PASS"}', encoding="utf-8")

        self.backend.migrate_legacy_root_files()

        self.assertEqual(
            health_csv.read_text(encoding="utf-8"),
            "status,detail\nPASS,canonical\n",
        )
        self.assertEqual(
            health_json.read_text(encoding="utf-8"),
            '{"status":"PASS"}',
        )

    def test_failure_rows_are_not_limited_to_latest_database_rows(self) -> None:
        con = self.backend.db_connect()
        try:
            con.execute("DELETE FROM videos")
            con.execute(
                "INSERT INTO videos(video_id,url,original_title,final_status,failure_reason) VALUES(?,?,?,?,?)",
                ("old_failed_video", "https://example.com/old", "Old failure", "FAIL", "old failure reason"),
            )
            for index in range(525):
                con.execute(
                    "INSERT INTO videos(video_id,url,original_title,final_status,failure_reason,last_error) VALUES(?,?,?,?,?,?)",
                    (f"ok_{index}", f"https://example.com/{index}", f"OK {index}", "DONE", "", ""),
                )
            con.commit()
        finally:
            con.close()

        rows = self.backend.web_download_failure_rows(limit=20)

        self.assertIn("old_failed_video", {row.get("video_id") for row in rows})

    def test_default_failure_rows_returns_all_current_failures(self) -> None:
        con = self.backend.db_connect()
        try:
            con.execute("DELETE FROM videos")
            for index in range(525):
                con.execute(
                    "INSERT INTO videos(video_id,url,original_title,final_status,failure_reason,last_error) VALUES(?,?,?,?,?,?)",
                    (f"failure_{index}", f"https://example.com/f/{index}", f"Failure {index}", "FAIL", "reason", "reason"),
                )
            con.commit()
        finally:
            con.close()
        try:
            rows = self.backend.web_download_failure_rows()
            ids = {row.get("video_id") for row in rows}
            self.assertTrue({f"failure_{index}" for index in range(525)}.issubset(ids))
        finally:
            con = self.backend.db_connect()
            try:
                con.execute("DELETE FROM videos WHERE video_id LIKE 'failure_%'")
                con.commit()
            finally:
                con.close()

    def test_selective_failure_cleanup_removes_failure_from_current_count(self) -> None:
        vid = "cleanup_failure_video"
        con = self.backend.db_connect()
        try:
            con.execute("DELETE FROM videos WHERE video_id=?", (vid,))
            con.execute(
                "INSERT INTO videos(video_id,url,original_title,final_status,failure_reason,last_error) VALUES(?,?,?,?,?,?)",
                (vid, "https://example.com/cleanup", "Cleanup failure", "FAIL", "test failure", "test failure"),
            )
            con.commit()
        finally:
            con.close()
        self.backend.log_failed_video(
            video_id=vid, url="https://example.com/cleanup", title="Cleanup failure",
            stage="Download", error_type="Test", error_message="test failure"
        )
        self.assertIn(vid, {row.get("video_id") for row in self.backend.web_download_failure_rows()})

        result = self.backend.clear_selected_failure_entries([vid])

        self.assertTrue(result.get("ok"))
        self.assertNotIn(vid, {row.get("video_id") for row in self.backend.web_download_failure_rows()})
        con = self.backend.db_connect()
        try:
            row = con.execute("SELECT final_status,failure_reason,last_error FROM videos WHERE video_id=?", (vid,)).fetchone()
        finally:
            con.close()
        self.assertEqual(tuple(row or ()), ("", "", ""))

    def test_dependency_status_finds_transcript_api_from_python_site_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            site_dir = Path(td) / "site-packages"
            package_dir = site_dir / "youtube_transcript_api"
            package_dir.mkdir(parents=True)
            (package_dir / "__init__.py").write_text("VALUE = 'fallback'\n", encoding="utf-8")
            with mock.patch.object(self.backend, "_python_site_package_fallbacks", return_value=[site_dir]):
                location = self.backend.transcript_api_location()

        self.assertTrue(location.endswith("youtube_transcript_api\\__init__.py") or location.endswith("youtube_transcript_api/__init__.py"))

    def test_dependency_status_points_to_local_ollama_model_manifest_when_server_off(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ollama_exe = root / "ollama.exe"
            ollama_exe.write_text("", encoding="utf-8")
            manifest = root / "models" / "manifests" / "registry.ollama.ai" / "library" / "qwen2.5" / "7b"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("{}", encoding="utf-8")
            with mock.patch.object(self.backend, "OLLAMA", ollama_exe):
                found = self.backend.ollama_model_manifest_path("qwen2.5:7b")

        self.assertEqual(found, manifest)


if __name__ == "__main__":
    unittest.main()
