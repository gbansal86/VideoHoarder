from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from app.download_workflows import execute_download_workflow

ROOT = Path(__file__).parents[1]


def test_media_only_requires_real_nonempty_output(tmp_path: Path) -> None:
    from app import app as backend
    fake_db = MagicMock()
    with patch.multiple(
        backend,
        DOWNLOADS=tmp_path,
        web_write_urls=lambda urls: urls,
        extract_single_source_metadata=lambda url: ({"id": "auditmedia1", "title": "Audit", "channel": "Audit", "url": url}, ""),
        save_metadata=lambda rows: None,
        db_connect=lambda: fake_db,
        run_video_with_fallback=lambda *args: (0, "", ""),
        find_any_media=lambda folder: None,
        strict_common_args=lambda: [],
        export_csv=lambda: None,
        export_artifact_registry=lambda: "",
        phase5_thumbnail_path=lambda *args: "",
        forget_deleted_video_redownload_guard=lambda *args: None,
    ):
        result = backend.web_media_only_download(["https://example.invalid/video"], vtt=False)
    assert result["ok"] is False
    assert result["success"] == 0
    assert result["failed"] == 1
    assert result["details"][0]["failure_code"] == "MISSING_MEDIA_OUTPUT"


def test_media_only_srt_option_is_forwarded() -> None:
    calls: list[tuple] = []

    def media_spy(*args):
        calls.append(args)
        return {"details": [{"url": args[0][0], "status": "SUCCESS"}]}

    for save_srt in (False, True):
        execute_download_workflow(
            ["https://example.invalid/video"],
            "media_only",
            False,
            lambda urls: {},
            lambda *args: {},
            media_spy,
            save_srt=save_srt,
        )
    assert calls[0][-1] is False
    assert calls[1][-1] is True
    assert calls[0] != calls[1]


def test_unfinished_job_restores_as_interrupted_with_retry_task(tmp_path: Path) -> None:
    from app import app as backend
    old_base = backend.BASE
    old_jobs = dict(backend.WEB_JOBS)
    old_tasks = dict(backend.WEB_JOB_TASKS)
    old_contexts = dict(backend.WEB_JOB_CONTEXTS)
    old_restored = backend.WEB_JOBS_RESTORED
    try:
        backend.BASE = tmp_path
        backend.WEB_JOBS.clear(); backend.WEB_JOB_TASKS.clear(); backend.WEB_JOB_CONTEXTS.clear()
        backend.WEB_JOBS_RESTORED = False
        jid = "restart-test"
        backend.WEB_JOBS[jid] = {
            "job_id": jid,
            "label": "Restart test",
            "status": "RUNNING",
            "created_at": 1.0,
            "message": "Working",
        }
        backend.WEB_JOB_TASKS[jid] = (backend.web_library_stats, (), {})
        assert backend.web_persist_job_state(force=True)
        backend.WEB_JOBS.clear(); backend.WEB_JOB_TASKS.clear(); backend.WEB_JOB_CONTEXTS.clear()
        result = backend.web_restore_persisted_jobs(force=True)
        restored = backend.web_job_snapshot(jid)
        assert result["interrupted"] == 1
        assert restored["status"] == "INTERRUPTED"
        assert jid in backend.WEB_JOB_TASKS
    finally:
        backend.BASE = old_base
        backend.WEB_JOBS.clear(); backend.WEB_JOBS.update(old_jobs)
        backend.WEB_JOB_TASKS.clear(); backend.WEB_JOB_TASKS.update(old_tasks)
        backend.WEB_JOB_CONTEXTS.clear(); backend.WEB_JOB_CONTEXTS.update(old_contexts)
        backend.WEB_JOBS_RESTORED = old_restored


def test_command_center_uses_canonical_progress_for_bottom_bar() -> None:
    source = (ROOT / "app" / "native_ui.py").read_text(encoding="utf-8")
    assert "global_progress = overall_progress_percent(running_job or {}, self.live) if active else 0" in source


def test_library_refresh_runs_backend_page_query_in_worker() -> None:
    source = (ROOT / "app" / "native_library_page.py").read_text(encoding="utf-8")
    assert "task = FunctionTask(" in source
    assert "backend.web_library_page(query, filter_key, page, page_size, sort_key)" in source
    assert "QThreadPool.globalInstance().start(task)" in source


def test_backend_ready_attaches_queue_first_and_isolates_page_failures() -> None:
    source = (ROOT / "app" / "gui.py").read_text(encoding="utf-8")
    block = source[source.index("# Queue is attached first"):source.index("def backend_failed", source.index("# Queue is attached first"))]
    assert block.index('(\"queue\", self.queue_page)') < block.index('(\"dashboard\", self.command_center)')
    assert "attach_errors" in block
    assert "except Exception" in block


def test_release_self_test_covers_backend_queue_cancel_and_restart_recovery() -> None:
    launcher = (ROOT / "run_gui.pyw").read_text(encoding="utf-8")
    build = (ROOT / "BUILD_WINDOWS.ps1").read_text(encoding="utf-8")
    for marker in ("backend_http_ready", "queue_visible", "queue_cancel_ok", "restart_recovery_ok", "queue_acceptance_ok"):
        assert marker in launcher
        assert marker in build or marker == "queue_visible" or marker == "queue_cancel_ok"


def test_code_parent_wrapper_reports_the_zip_that_remains() -> None:
    wrapper = (ROOT / "CREATE_CODE_PARENT_PACKAGE.bat").read_text(encoding="utf-8")
    assert "VideoHoarder_Code_Parent.zip" in wrapper


def test_media_only_srt_materialization_helper_writes_nonempty_file(tmp_path: Path) -> None:
    from app.media_only_service import create_srt_from_vtt

    vtt = tmp_path / "sample.en.vtt"
    vtt.write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nhello\n", encoding="utf-8")
    srt = create_srt_from_vtt(vtt, lambda _text: "1\n00:00:00,000 --> 00:00:01,000\nhello\n")
    assert srt is not None
    assert srt.is_file()
    assert srt.stat().st_size > 0
