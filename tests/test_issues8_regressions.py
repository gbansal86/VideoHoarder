from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]


def test_refresh_all_figures_is_a_managed_queue_job() -> None:
    source = (ROOT / "app" / "native_ui.py").read_text(encoding="utf-8")
    block = source[source.index("def _refresh_all_figures"):source.index("@Slot(str, str)", source.index("def _refresh_all_figures"))]
    assert 'starter = getattr(self.backend, "web_start_job", None)' in block
    assert 'starter("Refresh all figures", function, True)' in block
    assert 'FunctionTask("dashboard_figures"' not in block


def test_manually_deleted_download_is_purged_from_database_and_kept_only_in_redownload_guard(tmp_path: Path) -> None:
    from app import app as backend

    root = tmp_path / "library"
    videos = root / "VideoHoarder Videos"
    folder = videos / "Channel" / "Deleted Video [abc123DEF45]"
    data = folder / "_data"
    data.mkdir(parents=True)
    (data / ".video_id").write_text("abc123DEF45", encoding="utf-8")
    db = root / "library.db"

    with patch.object(backend, "BASE", root), \
         patch.object(backend, "DB", db), \
         patch.object(backend, "DOWNLOADS", videos), \
         patch.object(backend, "VISIBLE_VIDEO_LIBRARY", videos):
        con = backend.db_connect()
        con.execute(
            "INSERT OR REPLACE INTO videos(video_id,url,original_title,channel,downloaded,current_present,local_folder,local_video) VALUES(?,?,?,?,?,?,?,?)",
            ("abc123DEF45", "https://youtu.be/abc123DEF45", "Deleted Video", "Channel", 1, 1, str(folder), str(folder / "missing.mp4")),
        )
        con.commit(); con.close()

        result = backend.reconcile_active_library_state()
        stats = backend.web_library_stats()
        con = backend.db_connect()
        row = con.execute("SELECT video_id FROM videos WHERE video_id=?", ("abc123DEF45",)).fetchone()
        con.close()
        guard = backend._load_deleted_video_guard_history()

    assert result["purged_missing_count"] == 1
    assert row is None
    assert stats["database_rows"] == 0
    assert stats["available_downloaded_videos"] == 0
    assert "abc123DEF45" in guard


def test_media_only_updates_managed_job_progress_to_completion(tmp_path: Path) -> None:
    from app import app as backend

    fake_db = MagicMock()
    folder = tmp_path / "Entertainment" / "Channel" / "Video [progress123]"
    media = folder / "Video [progress123].mp4"
    progress_calls: list[tuple] = []

    def fake_run(*_args, **_kwargs):
        folder.mkdir(parents=True, exist_ok=True)
        media.write_bytes(b"media")
        return 0, "", ""

    with patch.multiple(
        backend,
        DOWNLOADS=tmp_path,
        web_write_urls=lambda urls: list(urls),
        extract_single_source_metadata=lambda url: ({"id": "progress123", "title": "Video", "channel": "Channel", "url": url}, ""),
        save_metadata=lambda rows: None,
        db_connect=lambda: fake_db,
        run_video_with_fallback=fake_run,
        find_any_media=lambda _folder: media,
        usable_media_file=lambda value: value,
        strict_common_args=lambda: [],
        export_csv=lambda: None,
        export_artifact_registry=lambda: "",
        phase5_thumbnail_path=lambda *args: "",
        forget_deleted_video_redownload_guard=lambda *args: None,
        web_job_progress=lambda *args, **kwargs: progress_calls.append((args, kwargs)),
    ):
        result = backend.web_media_only_download(["https://example.invalid/video"], vtt=False)

    assert result["ok"] is True
    assert any(call[0][1:3] == (0, 1) for call in progress_calls)
    assert any(call[0][1:3] == (1, 1) and call[0][-1] == 100 for call in progress_calls)


def test_queue_has_explicit_job_details_window() -> None:
    source = (ROOT / "app" / "native_queue_page.py").read_text(encoding="utf-8")
    assert 'QPushButton("Job details")' in source
    assert "def _show_job_details" in source
    assert "QDialog(self)" in source
    assert "self.table.cellDoubleClicked.connect" in source
    assert "refresh_dialog_details" in source
    native = (ROOT / "app" / "native_ui.py").read_text(encoding="utf-8")
    assert 'setHorizontalHeaderLabels(["Video","Status","Progress","Speed","ETA"])' in native
    assert 'chooser.setObjectName("childLogFilter")' in native
    assert 'reader=getattr(backend,"web_job_video_log",None)' in native


def test_code_parent_wrapper_is_portable_and_reports_zip() -> None:
    wrapper = (ROOT / "CREATE_CODE_PARENT_PACKAGE.bat").read_text(encoding="utf-8")
    assert "D:\\YT GUi" not in wrapper
    assert "VideoHoarder_Code_Parent.zip" in wrapper


def test_retry_reuses_the_same_logical_job_row(tmp_path: Path) -> None:
    from app import app as backend

    old_base = backend.BASE
    old_jobs = dict(backend.WEB_JOBS)
    old_tasks = dict(backend.WEB_JOB_TASKS)
    old_contexts = dict(backend.WEB_JOB_CONTEXTS)
    old_queue = backend.WEB_JOB_QUEUE
    try:
        backend.BASE = tmp_path
        backend.WEB_JOBS.clear(); backend.WEB_JOB_TASKS.clear(); backend.WEB_JOB_CONTEXTS.clear()
        backend.WEB_JOB_QUEUE = __import__("queue").Queue()
        backend.WEB_JOBS["same-job"] = {
            "job_id": "same-job", "label": "Retry: Full Library Download",
            "status": "FAILED", "created_at": 1.0, "message": "failed",
        }
        backend.WEB_JOB_TASKS["same-job"] = (backend.web_library_stats, (), {})

        ok, message, retried_id = backend.web_retry_job("same-job")

        assert ok is True
        assert message == "Retry queued"
        assert retried_id == "same-job"
        assert list(backend.WEB_JOBS) == ["same-job"]
        assert backend.WEB_JOBS["same-job"]["label"] == "Full Library Download"
        assert backend.WEB_JOBS["same-job"]["status"] == "QUEUED"
        assert backend.WEB_JOB_QUEUE.get_nowait() == "same-job"
    finally:
        backend.BASE = old_base
        backend.WEB_JOBS.clear(); backend.WEB_JOBS.update(old_jobs)
        backend.WEB_JOB_TASKS.clear(); backend.WEB_JOB_TASKS.update(old_tasks)
        backend.WEB_JOB_CONTEXTS.clear(); backend.WEB_JOB_CONTEXTS.update(old_contexts)
        backend.WEB_JOB_QUEUE = old_queue


def test_library_reconciliation_is_serialized() -> None:
    source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")
    assert "LIBRARY_RECONCILE_LOCK=threading.RLock()" in source
    assert "with LIBRARY_RECONCILE_LOCK:" in source


def test_queue_uses_separate_bounded_workflow_workers() -> None:
    source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")
    assert 'worker_count=max(1,min(5,int(CFG.get("workflow_workers",4) or 4)))' in source
    assert 'name=f"VLM-Web-Job-Worker-{index+1}"' in source
