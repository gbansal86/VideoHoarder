from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app.download_guard_service import confirmation_message, queue_duplicate_matches
from app.library_stats_service import physical_media_available


class DuplicateDownloadGuardTests(unittest.TestCase):
    def test_queue_duplicate_match_finds_same_youtube_id(self) -> None:
        rows = queue_duplicate_matches(
            ["https://www.youtube.com/watch?v=abcDEF12345"],
            [{
                "job_id": "j1",
                "status": "RUNNING",
                "source_url": "https://youtu.be/abcDEF12345",
                "video_id": "abcDEF12345",
                "display_name": "Example",
            }],
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "ALREADY_IN_QUEUE")
        self.assertIn("Already queued/running", confirmation_message(rows))

    def test_active_library_video_requires_confirmation_only_when_media_exists(self) -> None:
        from app import app

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "library.db"
            folder = root / "video"
            folder.mkdir()
            media = folder / "video.mp4"
            media.write_bytes(b"media")
            with patch.object(app, "BASE", root), patch.object(app, "DB", db):
                con = app.db_connect()
                con.execute(
                    "INSERT OR REPLACE INTO videos(video_id,url,original_title,channel,downloaded,current_present,local_folder,local_video) VALUES(?,?,?,?,?,?,?,?)",
                    ("abcDEF12345", "https://www.youtube.com/watch?v=abcDEF12345", "Example", "Channel", 1, 1, str(folder), str(media)),
                )
                con.commit(); con.close()
                result = app.redownload_history_check(["https://www.youtube.com/watch?v=abcDEF12345"])
            self.assertTrue(result["requires_confirmation"])
            self.assertEqual(result["items"][0]["status"], "ALREADY_ACTIVE")

    def test_metadata_only_row_does_not_block_first_real_download(self) -> None:
        from app import app

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "library.db"
            with patch.object(app, "BASE", root), patch.object(app, "DB", db):
                con = app.db_connect()
                con.execute(
                    "INSERT OR REPLACE INTO videos(video_id,url,original_title,channel,downloaded,current_present,local_folder,local_video) VALUES(?,?,?,?,?,?,?,?)",
                    ("abcDEF12345", "https://www.youtube.com/watch?v=abcDEF12345", "Example", "Channel", 0, 1, "", ""),
                )
                con.commit(); con.close()
                result = app.redownload_history_check(["https://www.youtube.com/watch?v=abcDEF12345"])
            self.assertFalse(result["requires_confirmation"])
            self.assertEqual(result["items"], [])


class PhysicalLibraryCountTests(unittest.TestCase):
    def test_downloaded_flag_without_media_is_not_counted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "video"
            folder.mkdir()
            self.assertFalse(physical_media_available(folder, "", 1))

    def test_real_media_is_counted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "video"
            folder.mkdir()
            media = folder / "real.mp4"
            media.write_bytes(b"x")
            self.assertTrue(physical_media_available(folder, media, 1))


class Issue6SourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.native = (cls.root / "app" / "native_ui.py").read_text(encoding="utf-8")
        cls.gui = (cls.root / "app" / "gui.py").read_text(encoding="utf-8")
        cls.queue_page = (cls.root / "app" / "native_queue_page.py").read_text(encoding="utf-8")

    def test_queue_is_a_distinct_native_page(self) -> None:
        self.assertIn("self.queue_page = NativeQueuePage()", self.gui)
        self.assertIn('if key == "queue":', self.gui)
        self.assertIn("self.content_stack.setCurrentWidget(self.queue_page)", self.gui)

    def test_queue_has_explicit_refresh_and_both_scrollbars(self) -> None:
        self.assertIn('QPushButton("Refresh queue")', self.native)
        self.assertIn("ScrollBarAlwaysOn", self.native)
        self.assertIn('QPushButton("Refresh queue")', self.queue_page)

    def test_queued_reason_mentions_paused_queue(self) -> None:
        self.assertIn("Waiting because the queue is paused", self.native)
        self.assertIn("Queue is PAUSED", self.queue_page)

    def test_job_details_controls_are_stacked_not_two_column(self) -> None:
        self.assertIn("root.addWidget(self.pause)", self.native)
        self.assertIn("root.addWidget(self.secondary)", self.native)

    def test_terminal_job_triggers_library_stats_refresh(self) -> None:
        self.assertIn("terminal_finished > self._stats_refreshed_through", self.native)

    def test_integrity_fixture_is_packaged(self) -> None:
        fixture = self.root / "tests" / "fixtures" / "chatgpt_integrity" / "data" / "chatgpt" / "exchange" / "outgoing" / "pkg" / "evidence.json"
        self.assertTrue(fixture.is_file())


if __name__ == "__main__":
    unittest.main()
