from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from app.download_access import add_browser_cookie_retry, build_youtube_download_attempts, has_cookie_args, run_with_browser_cookie_fallback
from app.download_queue_service import initial_job_metadata, latest_batch_summary
from app.download_workflows import execute_download_workflow, resolved_download_urls
from app.embedded_video_resolver import EmbeddedVideoResolver
from app.resolvers import DailymotionResolver, DramaVideoResolver, FastVidResolver, GenericIframeResolver, VimeoResolver, YouTubeResolver
from app.library_browser_service import browser_rows, merge_index_with_live_rows
from app.current_failure_registry import merge_current_failures, clear_terminal_job_failure
from app.failure_service import csv_failure_key, remove_failure_key_from_current_csvs
from app.current_status_service import download_status_payload, failure_summary
import csv
import threading


class EmbeddedResolverTests(unittest.TestCase):
    def test_resolver_plugins_are_separate_extensible_components(self) -> None:
        self.assertEqual(DailymotionResolver().name, "dailymotion")
        self.assertEqual(YouTubeResolver().name, "youtube")
        self.assertEqual(VimeoResolver().name, "vimeo")
        self.assertEqual(FastVidResolver().name, "fastvid")
        self.assertEqual(DramaVideoResolver().name, "dramavideo")
        self.assertEqual(GenericIframeResolver().name, "generic-iframe")

    def test_recursive_iframe_chain_resolves_known_host(self) -> None:
        pages = {
            "https://source.example/play": '<iframe src="https://fastvid.example/watch/1"></iframe>',
            "https://fastvid.example/watch/1": '<iframe src="/player/2"></iframe>',
            "https://fastvid.example/player/2": '<iframe src="https://www.dailymotion.com/embed/video/k66abc123"></iframe>',
        }

        def fetcher(url: str, referer: str = "") -> str:
            return pages[url]

        result = EmbeddedVideoResolver(fetcher=fetcher, max_depth=3).resolve("https://source.example/play")
        self.assertEqual(result["status"], "RESOLVED")
        self.assertEqual(result["host"], "dailymotion")
        self.assertEqual(result["watch_url"], "https://www.dailymotion.com/video/k66abc123")
        self.assertEqual(
            result["resolver_chain"],
            [
                "https://source.example/play",
                "https://fastvid.example/watch/1",
                "https://fastvid.example/player/2",
                "https://www.dailymotion.com/embed/video/k66abc123",
            ],
        )

    def test_direct_youtube_url_is_canonicalized_without_fetch(self) -> None:
        result = EmbeddedVideoResolver(fetcher=lambda *_args: (_ for _ in ()).throw(RuntimeError("should not fetch"))).resolve(
            "https://www.youtube.com/embed/abcDEF12345"
        )
        self.assertEqual(result["status"], "RESOLVED")
        self.assertEqual(result["watch_url"], "https://www.youtube.com/watch?v=abcDEF12345")


class DownloadWorkflowTests(unittest.TestCase):
    def test_resolver_result_is_downloaded_automatically(self) -> None:
        captured: list[list[str]] = []

        def resolver(urls: list[str]) -> dict:
            return {
                "ok": True,
                "results": [
                    {
                        "original_url": urls[0],
                        "status": "RESOLVED",
                        "watch_url": "https://www.dailymotion.com/video/xyz123",
                        "host": "dailymotion",
                        "video_id": "xyz123",
                    }
                ],
            }

        def full_download(urls: list[str], *_args) -> dict:
            captured.append(list(urls))
            return {"ok": True, "results": [{"status": "SUCCESS"}]}

        result = execute_download_workflow(
            ["https://source.example/play"],
            "full_download",
            True,
            resolver,
            full_download,
            lambda *_args: {"ok": False},
        )
        self.assertEqual(captured, [["https://www.dailymotion.com/video/xyz123"]])
        self.assertTrue(result["ok"])
        self.assertTrue(result["resolution_decisions"][0]["resolved"])

    def test_unresolved_url_falls_back_to_original_download_url(self) -> None:
        resolution = {"results": [{"original_url": "https://x", "status": "UNRESOLVED"}]}
        effective, decisions = resolved_download_urls(resolution, ["https://x"])
        self.assertEqual(effective, ["https://x"])
        self.assertFalse(decisions[0]["resolved"])


class LibraryBrowserTests(unittest.TestCase):
    def test_live_database_state_overlays_stale_phase5_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            media = Path(tmp) / "video.mp4"
            media.write_bytes(b"x")
            index_docs = [
                {
                    "video_id": "A",
                    "title": "Old title",
                    "downloaded_at": "2026-01-01 00:00:00",
                    "local_video": "",
                    "search_text": "old title",
                },
                {
                    "video_id": "B",
                    "title": "Other",
                    "downloaded_at": "2026-08-01 00:00:00",
                    "local_video": str(media),
                },
            ]
            live_rows = [
                {
                    "video_id": "A",
                    "clean_title": "Current title",
                    "downloaded_at": "2026-09-10 20:00:00",
                    "local_video": str(media),
                    "final_status": "PASS",
                    "archived": 0,
                },
                {
                    "video_id": "B",
                    "clean_title": "Other",
                    "downloaded_at": "2026-08-01 00:00:00",
                    "local_video": str(media),
                    "final_status": "PASS",
                    "archived": 0,
                },
            ]
            merged = merge_index_with_live_rows(index_docs, live_rows)
            rows = browser_rows(merged, sort_by="downloaded_desc", path_exists=lambda value: Path(value).exists())
            self.assertEqual(rows[0]["video_id"], "A")
            self.assertEqual(rows[0]["title"], "Current title")
            self.assertEqual(rows[0]["downloaded_at"], "2026-09-10 20:00:00")
            self.assertTrue(rows[0]["has_media"])

    def test_library_rows_include_thumbnail_and_local_media_for_native_page(self) -> None:
        rows = browser_rows(
            [{
                "video_id": "thumb1",
                "title": "Thumb video",
                "local_video": "/tmp/thumb1.mp4",
                "thumbnail_url": "https://example.com/thumb.jpg",
                "url": "https://example.com/video",
            }],
            path_exists=lambda _value: True,
        )
        self.assertEqual(rows[0]["thumbnail_url"], "https://example.com/thumb.jpg")
        self.assertEqual(rows[0]["local_video"], "/tmp/thumb1.mp4")
        self.assertEqual(rows[0]["url"], "https://example.com/video")

    def test_library_browser_can_return_more_than_legacy_2000_cap(self) -> None:
        docs = [
            {"video_id": f"v{i}", "title": f"Video {i}", "local_video": f"/tmp/v{i}.mp4"}
            for i in range(2505)
        ]
        rows = browser_rows(docs, limit=3000, path_exists=lambda _value: True)
        self.assertEqual(len(rows), 2505)

    def test_library_browser_sorts_by_category_then_video(self) -> None:
        docs = [
            {"video_id": "b", "title": "Zeta", "category": "Sports", "subcategory": "General", "local_video": "/tmp/b.mp4"},
            {"video_id": "a", "title": "Alpha", "category": "Education", "subcategory": "General", "local_video": "/tmp/a.mp4"},
            {"video_id": "c", "title": "Beta", "category": "Education", "subcategory": "General", "local_video": "/tmp/c.mp4"},
        ]
        rows = browser_rows(docs, sort_by="category", path_exists=lambda _value: True)
        self.assertEqual([row["video_id"] for row in rows], ["a", "c", "b"])


class QueueMetadataTests(unittest.TestCase):
    def test_initial_youtube_job_has_thumbnail_and_batch_metadata(self) -> None:
        meta = initial_job_metadata(
            "https://www.youtube.com/watch?v=abcDEF12345",
            "Media Only",
            batch_id="batch-1",
            batch_index=2,
            batch_total=4,
        )
        self.assertEqual(meta["video_id"], "abcDEF12345")
        self.assertIn("abcDEF12345", meta["thumbnail_url"])
        self.assertEqual(meta["job_type"], "Media Only")
        self.assertEqual(meta["batch_total"], 4)

    def test_latest_batch_reports_done_and_left(self) -> None:
        jobs = [
            {"batch_id": "b", "status": "SUCCESS", "created_at": 1},
            {"batch_id": "b", "status": "RUNNING", "created_at": 2},
            {"batch_id": "b", "status": "QUEUED", "created_at": 3},
            {"batch_id": "b", "status": "QUEUED", "created_at": 4},
        ]
        summary = latest_batch_summary(jobs)
        self.assertEqual(summary["done"], 1)
        self.assertEqual(summary["left"], 3)
        self.assertEqual(summary["running"], 1)


class CookieFallbackTests(unittest.TestCase):
    def test_browser_cookie_retry_is_added_when_missing(self) -> None:
        args = add_browser_cookie_retry(["yt-dlp", "--no-warnings"], {"browser_for_cookies": "firefox"})
        self.assertTrue(has_cookie_args(args))
        self.assertEqual(args[-2:], ["--cookies-from-browser", "firefox"])

    def test_existing_cookie_args_are_not_duplicated(self) -> None:
        args = ["yt-dlp", "--cookies-from-browser", "firefox"]
        self.assertEqual(add_browser_cookie_retry(args, {"browser_for_cookies": "firefox"}), args)

    def test_youtube_attempt_ladder_includes_cookie_fallbacks(self) -> None:
        attempts = build_youtube_download_attempts(
            ["yt-dlp"],
            "https://www.youtube.com/watch?v=abcDEF12345",
            "1080",
            {
                "youtube_403_fallback": True,
                "youtube_cookie_fallback": True,
                "youtube_fallback_clients": ["web_safari", "web_embedded"],
                "browser_for_cookies": "firefox",
            },
            lambda _quality: "best",
        )
        labels = [label for label, _args in attempts]
        self.assertEqual(
            labels,
            ["default", "web_safari", "web_embedded", "browser-cookies", "browser-cookies-web_safari", "browser-cookies-web_embedded"],
        )
        cookie_attempt = dict(attempts)["browser-cookies"]
        self.assertIn("--cookies-from-browser", cookie_attempt)

    def test_metadata_cookie_fallback_retries_youtube_403_once(self) -> None:
        calls: list[list[str]] = []

        def runner(args: list[str]):
            calls.append(list(args))
            if len(calls) == 1:
                return 1, "", "HTTP Error 403: Forbidden"
            return 0, '{"id":"abcDEF12345"}', ""

        rc, out, err, retried = run_with_browser_cookie_fallback(
            ["yt-dlp", "--dump-single-json", "https://www.youtube.com/watch?v=abcDEF12345"],
            "https://www.youtube.com/watch?v=abcDEF12345",
            {"browser_for_cookies": "firefox", "youtube_cookie_fallback": True},
            runner,
        )
        self.assertEqual(rc, 0)
        self.assertTrue(retried)
        self.assertEqual(len(calls), 2)
        self.assertIn("--cookies-from-browser", calls[1])


class Issue3FailureRegistryTests(unittest.TestCase):
    def test_unified_registry_includes_video_and_failed_jobs_but_not_cancelled(self) -> None:
        rows = merge_current_failures(
            [{"video_id": "v1", "clean_title": "Video failure", "failure_reason": "403", "failure_key": "video:v1"}],
            [
                {"job_id": "j1", "label": "Download one", "status": "FAILED", "message": "failed"},
                {"job_id": "j2", "label": "Cancelled", "status": "CANCELLED", "message": "cancelled"},
            ],
        )
        self.assertEqual({row["failure_key"] for row in rows}, {"video:v1", "job:j1"})

    def test_unknown_csv_failure_can_be_deleted_by_stable_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "failed_videos.csv"
            fields = ["Timestamp", "Video ID", "URL", "Title", "Error Message", "Retry Status"]
            row = {"Timestamp": "now", "Video ID": "", "URL": "https://x", "Title": "Unknown", "Error Message": "No ID", "Retry Status": "FAILED"}
            with path.open("w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader(); writer.writerow(row)
            key = csv_failure_key(path, row)
            self.assertEqual(remove_failure_key_from_current_csvs(key, [path]), 1)
            with path.open("r", newline="", encoding="utf-8-sig") as handle:
                self.assertEqual(list(csv.DictReader(handle)), [])

    def test_failed_job_delete_archives_log_and_removes_current_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "j1.jsonl"
            log.write_text('{"event":"status","status":"FAILED"}\n', encoding="utf-8")
            jobs = {"j1": {"job_id": "j1", "status": "FAILED"}}
            tasks = {"j1": object()}
            result = clear_terminal_job_failure("j1", jobs, tasks, threading.RLock(), log, root / "archive")
            self.assertTrue(result["ok"])
            self.assertNotIn("j1", jobs)
            self.assertNotIn("j1", tasks)
            self.assertFalse(log.exists())
            self.assertTrue(Path(result["archived_log"]).exists())

    def test_download_status_payload_uses_unified_failure_count(self) -> None:
        failures = [
            {"failure_key": "video:v1", "failure_reason": "HTTP Error 403: Forbidden"},
            {"failure_key": "job:j1", "reason": "Queue job failed"},
        ]
        payload = download_status_payload({"downloaded": 10, "failed": 999, "latest7": 4}, failures)
        self.assertEqual(payload["stats"]["failed"], 2)
        self.assertEqual(payload["failures"], failures)
        self.assertEqual(payload["summary"][0]["reason"], "YouTube 403 forbidden")

    def test_failure_summary_accepts_queue_job_reason_field(self) -> None:
        summary = failure_summary([{"failure_key": "job:j1", "reason": "ffmpeg merge failed"}])
        self.assertEqual(summary, [{"reason": "FFmpeg/media merge", "count": 1}])

    def test_web_media_only_can_pass_embedded_resolver_flag(self) -> None:
        source_root = Path(__file__).resolve().parents[1]
        app_source = (source_root / "app" / "app.py").read_text(encoding="utf-8")
        self.assertIn('id="mediaResolveEmbedded"', app_source)
        self.assertIn("resolve_embedded:!!($('mediaResolveEmbedded')", app_source)
        compact = app_source.replace(" ", "")
        self.assertIn('"media_only":("MediaOnlyDownload",web_download_workflow', compact)

    def test_download_status_uses_current_status_service(self) -> None:
        source_root = Path(__file__).resolve().parents[1]
        app_source = (source_root / "app" / "app.py").read_text(encoding="utf-8")
        self.assertIn("current_status_service", app_source)
        self.assertIn("download_status_payload(web_library_stats(),failures)", app_source)

    def test_dashboard_startup_waits_for_progress_readiness(self) -> None:
        source_root = Path(__file__).resolve().parents[1]
        app_source = (source_root / "app" / "app.py").read_text(encoding="utf-8")
        self.assertIn("wait_for_http_ready", app_source)
        self.assertIn("/api/progress", app_source)

    def test_clear_all_current_failures_exists_in_web_and_backend(self) -> None:
        source_root = Path(__file__).resolve().parents[1]
        app_source = (source_root / "app" / "app.py").read_text(encoding="utf-8")
        self.assertIn("def web_clear_all_current_failures", app_source)
        self.assertIn("/api/failures/clear-all-current", app_source)
        self.assertIn("clearAllCurrentFailures", app_source)
        self.assertIn('id="clearAllFailuresConfirm"', app_source)

    def test_dashboard_figures_refresh_is_reusable_backend_service(self) -> None:
        source_root = Path(__file__).resolve().parents[1]
        app_source = (source_root / "app" / "app.py").read_text(encoding="utf-8")
        native_source = (source_root / "app" / "native_ui.py").read_text(encoding="utf-8")
        self.assertIn("def refresh_dashboard_figures", app_source)
        self.assertIn("/api/dashboard-figures", app_source)
        self.assertIn("/api/dashboard-figures/refresh", app_source)
        self.assertIn('getattr(self.backend, "refresh_dashboard_figures"', native_source)


class Issue3NavigationTests(unittest.TestCase):
    def test_native_sidebar_exposes_real_downloads_tab_and_workflow_routes_to_it(self) -> None:
        source_root = Path(__file__).resolve().parents[1]
        native = (source_root / "app" / "native_ui.py").read_text(encoding="utf-8")
        gui = (source_root / "app" / "gui.py").read_text(encoding="utf-8")
        self.assertIn('(\"downloads\", \"⇩\", \"Downloads\")', native)
        self.assertIn('self.navigate_requested.emit(\"downloads\")', native)
        self.assertIn('\"downloads\": (\"Downloads\", \"/app?tab=downloads\")', gui)


if __name__ == "__main__":
    unittest.main()
