from __future__ import annotations

from datetime import datetime
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from app.download_queue_service import queue_wait_message
from app.library_stats_service import physical_downloaded_today_count


class V7DashboardMetricTests(unittest.TestCase):
    def test_completed_today_counts_physical_videos_not_generic_jobs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            media = root / "video.mp4"
            media.write_bytes(b"media")
            today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            empty = root / "empty"
            empty.mkdir()
            rows = [(root, media, 1, today), (empty, "", 1, today)]
            self.assertEqual(physical_downloaded_today_count(rows), 1)

    def test_queue_wait_reason_distinguishes_worker_start_from_earlier_jobs(self) -> None:
        first = {"job_id": "a", "status": "QUEUED", "created_at": 1}
        second = {"job_id": "b", "status": "QUEUED", "created_at": 2}
        state = {"paused": False, "running": 0, "queued": 2}
        self.assertIn("worker to start", queue_wait_message(first, [first, second], state))
        self.assertIn("1 earlier queued job", queue_wait_message(second, [first, second], state))
        self.assertIn("queue is paused", queue_wait_message(first, [first], {"paused": True}),)


class V7BackendGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        from app import app
        self.app = app
        with app.WEB_JOB_LOCK:
            self.old_jobs = dict(app.WEB_JOBS)
            self.old_tasks = dict(app.WEB_JOB_TASKS)
            app.WEB_JOBS.clear()
            app.WEB_JOB_TASKS.clear()

    def tearDown(self) -> None:
        app = self.app
        with app.WEB_JOB_LOCK:
            app.WEB_JOBS.clear(); app.WEB_JOBS.update(self.old_jobs)
            app.WEB_JOB_TASKS.clear(); app.WEB_JOB_TASKS.update(self.old_tasks)

    def test_unlimited_snapshot_returns_more_than_60(self) -> None:
        app = self.app
        with app.WEB_JOB_LOCK:
            for i in range(75):
                app.WEB_JOBS[f"j{i}"] = {"job_id": f"j{i}", "created_at": i, "status": "SUCCESS"}
        self.assertEqual(len(app.web_job_snapshot()), 60)
        self.assertEqual(len(app.web_job_snapshot(limit=None)), 75)

    def test_legacy_duplicate_report_includes_current_queue(self) -> None:
        app = self.app
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "library.db"
            with patch.object(app, "BASE", root), patch.object(app, "DB", db):
                # ensure schema exists but no media row exists
                con = app.db_connect(); con.close()
                with app.WEB_JOB_LOCK:
                    app.WEB_JOBS["queued"] = {
                        "job_id": "queued",
                        "status": "QUEUED",
                        "created_at": time.time(),
                        "source_url": "https://youtu.be/abcDEF12345",
                        "video_id": "abcDEF12345",
                        "display_name": "Queued example",
                    }
                report = app.redownload_history_check(["https://www.youtube.com/watch?v=abcDEF12345"])
        self.assertTrue(report["requires_confirmation"])
        self.assertTrue(any(row.get("status") == "ALREADY_IN_QUEUE" for row in report["items"]))

    def test_successful_retry_requires_explicit_confirmation(self) -> None:
        app = self.app
        def dummy(urls):
            return {"ok": True}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "library.db"
            with patch.object(app, "BASE", root), patch.object(app, "DB", db):
                con = app.db_connect(); con.close()
                with app.WEB_JOB_LOCK:
                    app.WEB_JOBS["done"] = {
                        "job_id": "done",
                        "label": "Full Library Download",
                        "status": "SUCCESS",
                        "created_at": time.time()-1,
                        "finished_at": time.time(),
                        "source_url": "https://youtu.be/abcDEF12345",
                        "video_id": "abcDEF12345",
                    }
                    app.WEB_JOB_TASKS["done"] = (dummy, (["https://youtu.be/abcDEF12345"],), {})
                ok, msg, new_id = app.web_retry_job("done", False)
        self.assertFalse(ok)
        self.assertEqual(msg, "CONFIRM_REDOWNLOAD_REQUIRED")
        self.assertIsNone(new_id)


class V7SourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.native = (cls.root / "app" / "native_ui.py").read_text(encoding="utf-8")
        cls.app_source = (cls.root / "app" / "app.py").read_text(encoding="utf-8")
        cls.queue_source = (cls.root / "app" / "native_queue_page.py").read_text(encoding="utf-8")

    def test_refresh_all_figures_is_visible_in_managed_queue(self) -> None:
        block = self.native[self.native.index("def _refresh_all_figures"):self.native.index("@Slot(str, str)", self.native.index("def _refresh_all_figures"))]
        self.assertIn('starter = getattr(self.backend, "web_start_job", None)', block)
        self.assertIn('starter("Refresh all figures", function, True)', block)
        self.assertNotIn('FunctionTask("dashboard_figures"', block)

    def test_all_function_task_calls_match_two_argument_constructor(self) -> None:
        import ast
        tree = ast.parse(self.native)
        calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "FunctionTask"
        ]
        self.assertGreaterEqual(len(calls), 1)
        for call in calls:
            self.assertEqual(len(call.args), 2, f"FunctionTask call at line {call.lineno} has {len(call.args)} positional args")
            self.assertEqual(call.keywords, [], f"FunctionTask call at line {call.lineno} unexpectedly uses keyword args")

    def test_stats_refresh_has_pending_and_inflight_targets(self) -> None:
        self.assertIn("self._stats_pending = True", self.native)
        self.assertIn("self._stats_inflight_target = self._stats_refresh_target", self.native)
        self.assertIn("self._stats_refreshed_through = max(self._stats_refreshed_through, self._stats_inflight_target)", self.native)

    def test_completed_today_comes_from_library_stats(self) -> None:
        self.assertIn('self.library_stats.get("downloaded_today")', self.native)
        self.assertIn('"downloaded_today":int(downloaded_today or 0)', self.app_source)

    def test_full_download_records_downloaded_at(self) -> None:
        self.assertIn('UPDATE videos SET downloaded=1,downloaded_at=? WHERE video_id=?', self.app_source)

    def test_legacy_job_start_has_server_side_duplicate_gate(self) -> None:
        self.assertIn('if action in {"media_only","full_download"}:', self.app_source)
        self.assertIn('"requires_confirmation":True', self.app_source)
        self.assertIn('confirmed_redownload:true', self.app_source)

    def test_queue_page_requests_unlimited_snapshot(self) -> None:
        self.assertIn("snapshot(limit=None)", self.queue_source)

    def test_legacy_retry_prompts_before_successful_redownload(self) -> None:
        self.assertIn("x.message==='CONFIRM_REDOWNLOAD_REQUIRED'", self.app_source)
        self.assertIn("confirm_redownload:true", self.app_source)


if __name__ == "__main__":
    unittest.main()
