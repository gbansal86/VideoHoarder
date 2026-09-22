from __future__ import annotations

import importlib.util
import os
import unittest


PYSIDE_AVAILABLE = importlib.util.find_spec("PySide6") is not None


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is installed in the GUI/build environment")
class NativeUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication

        cls.app = QApplication.instance() or QApplication([])

    def test_sidebar_has_simplified_navigation(self) -> None:
        from app.native_ui import Sidebar

        sidebar = Sidebar()
        self.assertEqual(
            list(sidebar.buttons),
            ["dashboard", "downloads", "queue", "library", "oldimport", "localimport", "repairdata", "chatgpt_processing", "knowledge", "subscriptions", "collections", "more", "settings"],
        )

    def test_tool_catalog_is_replaced_by_guided_workflows(self) -> None:
        from app.native_ui import WorkflowsPage

        self.assertEqual(len(WorkflowsPage.WORKFLOWS), 10)
        self.assertEqual(
            [item[0] for item in WorkflowsPage.WORKFLOWS],
            ["new_download", "resume", "failures", "health", "knowledge", "subscriptions", "chatgpt", "reports", "recovery", "setup"],
        )

    def test_download_presets_have_backend_actions(self) -> None:
        from app.native_ui import DownloadComposer

        actions = {data["action"] for _label, data in DownloadComposer.PRESETS}
        self.assertEqual(actions, {"full_download", "media_only"})

    def test_download_composer_exposes_embedded_url_resolver(self) -> None:
        from app.native_ui import DownloadComposer

        composer = DownloadComposer()
        self.assertEqual(composer.resolve_embedded.text(), "Resolve embedded video URL")

    def test_multiple_pasted_urls_queue_as_separate_jobs(self) -> None:
        from app.native_ui import CommandCenter

        class FakeBackend:
            def __init__(self) -> None:
                self.calls: list[tuple[str, object, tuple[object, ...]]] = []

            def web_start_job(self, label: str, func: object, *args: object) -> str:
                self.calls.append((label, func, args))
                return f"job-{len(self.calls)}"

            def web_download_workflow(self, *args: object) -> None:
                return None

            def web_job_update(self, job_id: str, **kwargs: object) -> None:
                return None

        center = CommandCenter()
        backend = FakeBackend()
        center.backend = backend

        center._start_download(
            ["https://example.com/1", "https://example.com/2", "https://example.com/3", "https://example.com/4"],
            {"action": "media_only", "quality": "1080"},
        )

        self.assertEqual(len(backend.calls), 4)
        self.assertEqual(backend.calls[0][0], "1080 Media Download 1/4")
        self.assertEqual(backend.calls[-1][0], "1080 Media Download 4/4")
        self.assertEqual(backend.calls[0][2][0], ["https://example.com/1"])
        self.assertEqual(backend.calls[-1][2][0], ["https://example.com/4"])
        self.assertEqual(getattr(backend.calls[0][1], "__name__", ""), "web_download_workflow")


    def test_resolver_checkbox_runs_resolve_then_download_workflow(self) -> None:
        from app.native_ui import CommandCenter

        class FakeBackend:
            def __init__(self) -> None:
                self.calls = []
                self.updates = []

            def web_start_job(self, label: str, func: object, *args: object) -> str:
                self.calls.append((label, func, args))
                return "job-1"

            def web_download_workflow(self, *args: object) -> None:
                return None

            def web_job_update(self, job_id: str, **kwargs: object) -> None:
                self.updates.append((job_id, kwargs))

        center = CommandCenter()
        backend = FakeBackend()
        center.backend = backend
        center._start_download(
            ["https://source.example/play"],
            {"action": "full_download", "quality": "1080", "resolve_embedded": True},
        )
        self.assertEqual(len(backend.calls), 1)
        args = backend.calls[0][2]
        self.assertEqual(args[1], "full_download")
        self.assertTrue(args[2])
        self.assertEqual(backend.updates[0][1]["job_type"], "Full Library + Resolver")

    def test_download_composer_separates_workflow_and_quality(self) -> None:
        from app.native_ui import DownloadComposer

        composer = DownloadComposer()
        self.assertEqual([composer.workflow.itemText(i) for i in range(composer.workflow.count())], ["Full Library", "Media Only", "Audio Only"])
        self.assertEqual(composer.quality.currentData(), "1080")
        composer.workflow.setCurrentIndex(2)
        self.assertFalse(composer.quality.isEnabled())

    def test_queue_table_keeps_name_and_type_as_separate_columns(self) -> None:
        from app.native_ui import QueueTable

        table = QueueTable()
        self.assertEqual(table.horizontalHeaderItem(0).text(), "Name")
        self.assertEqual(table.horizontalHeaderItem(1).text(), "Type")
        self.assertGreaterEqual(table.columnWidth(0), 300)

    def test_native_library_defaults_to_100_videos_per_page(self) -> None:
        from app.native_library_page import NativeLibraryPage

        page = NativeLibraryPage()
        self.assertEqual(page.page_size.currentData(), 100)

    def test_native_failure_page_has_delete_next_to_failure(self) -> None:
        from app.native_failure_page import NativeFailurePage

        page = NativeFailurePage()
        self.assertEqual(page.table.horizontalHeaderItem(0).text(), "Failure")
        self.assertEqual(page.table.horizontalHeaderItem(1).text(), "Delete")
        self.assertEqual(page.clear_all_button.text(), "Clear all failures")

    def test_dashboard_has_clear_all_failure_control_and_attention_routes_to_failures(self) -> None:
        from app.native_ui import CommandCenter

        center = CommandCenter()
        self.assertEqual(center.clear_failures_button.text(), "Clear all failures")
        seen: list[str] = []
        center.navigate_requested.connect(seen.append)
        center._show_attention()
        self.assertEqual(seen, ["failures"])

    def test_dashboard_has_refresh_all_figures_control(self) -> None:
        from app.native_ui import CommandCenter

        center = CommandCenter()
        self.assertEqual(center.refresh_all_button.text(), "Refresh all figures")

    def test_dashboard_does_not_append_old_failed_jobs_to_active_queue(self) -> None:
        from app.native_ui import CommandCenter

        class FakeBackend:
            DOWNLOADS = "D:/Downloads"

            def web_job_snapshot(self) -> list[dict[str, str]]:
                return []

            def web_failed_job_rows(self, limit: int = 25) -> list[dict[str, str]]:
                return [{"job_id": "old-failed", "status": "FAILED", "label": "Old failed job"}]

            def snapshot(self) -> dict[str, object]:
                return {}

            def web_queue_state(self) -> dict[str, int]:
                return {"running": 0, "queued": 0}

        center = CommandCenter()
        center.backend = FakeBackend()
        center.refresh_fast()
        self.assertEqual(center.table.rowCount(), 0)

    def test_job_details_has_delete_failure_and_saved_location_buttons(self) -> None:
        from app.native_ui import JobDetails

        details = JobDetails()
        details.set_job({"job_id": "j1", "status": "FAILED", "label": "Failed job"}, {}, False, None)
        self.assertFalse(details.delete_failure.isHidden())
        self.assertEqual(details.open_saved.text(), "□  Open saved location")

    def test_library_exposes_requested_sort_options_and_larger_thumbnail(self) -> None:
        from app.native_library_page import NativeLibraryPage

        page = NativeLibraryPage()
        labels = [page.sort.itemText(i) for i in range(page.sort.count())]
        self.assertIn("Video A-Z", labels)
        self.assertIn("Channel A-Z", labels)
        self.assertIn("Category A-Z", labels)
        sample = page._video_widget({"video_id": "abc", "title": "Example"})
        thumb = sample.layout().itemAt(0).widget()
        self.assertEqual(thumb.width(), 120)
        self.assertEqual(thumb.height(), 68)

    def test_dashboard_failure_count_uses_unified_current_failures(self) -> None:
        from app.native_ui import CommandCenter

        class FakeBackend:
            def web_current_failure_rows(self) -> list[dict[str, str]]:
                return [{"failure_key": "video:v1"}, {"failure_key": "job:j1"}]

            def web_download_failure_rows(self) -> list[dict[str, str]]:
                return [{"failure_key": "video:v1"}]

        center = CommandCenter()
        center.backend = FakeBackend()
        center.refresh_failure_count()

        self.assertEqual(center.current_failure_count, 2)

    def test_issue6_queue_table_has_both_scrollbars(self) -> None:
        from PySide6.QtCore import Qt
        from app.native_ui import QueueTable

        table = QueueTable(row_limit=None)
        self.assertEqual(table.horizontalScrollBarPolicy(), Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.assertEqual(table.verticalScrollBarPolicy(), Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

    def test_issue6_queue_page_is_dedicated_and_has_refresh(self) -> None:
        from app.native_queue_page import NativeQueuePage

        page = NativeQueuePage()
        self.assertEqual(page.refresh_button.text(), "Refresh queue")
        self.assertIsNone(page.table.row_limit)

    def test_issue6_job_details_queued_reason_is_explicit(self) -> None:
        from app.native_ui import JobDetails

        details = JobDetails()
        details.set_job({"job_id":"q1","status":"QUEUED","label":"Queued job"}, {}, True, None)
        texts=[]
        for i in range(details.detail_layout.count()):
            widget=details.detail_layout.itemAt(i).widget()
            if widget:
                labels=widget.findChildren(type(details.name))
                texts.extend(label.text() for label in labels)
        self.assertTrue(any("queue is paused" in text.lower() for text in texts))



if __name__ == "__main__":
    unittest.main()