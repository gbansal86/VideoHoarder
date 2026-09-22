from __future__ import annotations

import dataclasses
import threading
import time
import importlib
from pathlib import Path
from unittest.mock import patch

from app.download_options import DownloadOptions
from app.download_queue_service import overall_progress_percent
from app.download_workflows import aggregate_input_outcomes, ensure_input_outcomes
from app.yt_dlp_arguments import add_download_performance_args


def _backend():
    return importlib.import_module("app.app")


def test_download_options_are_immutable_and_capture_workflow_call() -> None:
    opts = DownloadOptions.from_workflow_call(
        (["https://example/video"], "full_download", True, "720", True, True, False, True, "Education", True, "source"),
        {},
    )
    assert opts is not None
    assert opts.quality == "720"
    assert opts.save_srt is True
    assert opts.resolve_embedded is True
    try:
        opts.quality = "1080"  # type: ignore[misc]
    except dataclasses.FrozenInstanceError:
        pass
    else:
        raise AssertionError("DownloadOptions must be frozen")


def test_download_performance_options_are_bounded_and_use_argument_lists() -> None:
    opts = DownloadOptions.from_settings({"parallel_videos": "99", "concurrent_fragments": "bad"})
    assert opts.parallel_videos == 5
    assert opts.concurrent_fragments == 4
    assert add_download_performance_args(["yt-dlp"], concurrent_fragments=20) == [
        "yt-dlp", "--concurrent-fragments", "16",
    ]


def test_full_download_runs_video_rows_concurrently_and_preserves_result_order() -> None:
    backend = _backend()
    urls = [f"https://example.invalid/{index}" for index in range(3)]
    rows = [(f"video{index}", url, f"Title {index}", f"Title {index}", "Channel", "20260101") for index, url in enumerate(urls)]
    lock = threading.Lock()
    release = threading.Event()
    active = 0
    peak = 0

    def fake_process(row, _quality, options=None):
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
            if active == 2:
                release.set()
        assert release.wait(2)
        with lock:
            active -= 1
        return True

    def no_database():
        raise RuntimeError("database intentionally unavailable in scheduler unit test")

    with patch.dict(backend.CFG, {"parallel_videos": 2, "concurrent_fragments": 4}, clear=False), patch.multiple(
        backend,
        web_write_urls=lambda values: list(values),
        metadata_scan=lambda: None,
        rows_for_current_urls=lambda: rows,
        web_current_job_context=lambda: None,
        web_stop_requested=lambda: False,
        db_connect=no_database,
        web_update_current_job_media=lambda **kwargs: None,
        web_job_log=lambda *args, **kwargs: None,
        web_job_progress=lambda *args, **kwargs: None,
        set_state=lambda **kwargs: None,
        smart_resume_artifact_status=lambda _vid: {"action": "DOWNLOAD", "reason": ""},
        process_download=fake_process,
        export_artifact_registry=lambda: "",
        print_all_downloads_done_banner=lambda: None,
    ):
        result = backend.web_full_download(urls, smart_resume=False, vtt=False)

    assert result["ok"] is True
    assert peak == 2
    assert [item["video_id"] for item in result["results"]] == ["video0", "video1", "video2"]


def test_media_only_and_external_batches_share_bounded_parallelism() -> None:
    backend = _backend()
    lock = threading.Lock()

    def exercise(wrapper_name: str, serial_name: str, item_key: str) -> None:
        active = 0
        peak = 0
        release = threading.Event()

        def fake_serial(urls, *args, **kwargs):
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
                if active == 2:
                    release.set()
            assert release.wait(2)
            with lock:
                active -= 1
            url = urls[0]
            if item_key == "details":
                return {"ok": True, "success": 1, "failed": 0, "warnings": 0, "details": [{"url": url, "status": "SUCCESS"}]}
            return {"ok": True, "items": [{"url": url, "status": "SUCCESS"}], "folder": "test"}

        patches = {
            serial_name: fake_serial,
            "web_current_job_context": lambda: None,
        }
        if wrapper_name == "web_media_only_download":
            patches.update({
                "web_write_urls": lambda values: list(values),
                "web_job_log": lambda *args, **kwargs: None,
                "web_reset_video_progress": lambda: None,
                "export_csv": lambda: None,
                "export_artifact_registry": lambda: "",
                "print_all_downloads_done_banner": lambda: None,
            })
        else:
            patches["external_media_root"] = lambda category="Streams": Path("test")

        with patch.dict(backend.CFG, {"parallel_videos": 2}, clear=False), patch.multiple(backend, **patches):
            result = getattr(backend, wrapper_name)(["one", "two", "three"])
        assert result["ok"] is True
        assert peak == 2

    exercise("web_media_only_download", "_web_media_only_download_serial", "details")
    exercise("web_external_media_download", "_web_external_media_download_serial", "items")


def test_disabled_optional_outputs_are_not_reported_as_validation_failures(tmp_path: Path) -> None:
    backend = _backend()
    folder = tmp_path / "video"
    data = folder / "_data"
    data.mkdir(parents=True)
    video = folder / "video.mp4"
    video.write_bytes(b"media")
    (folder / "title.original-title").write_text("title", encoding="utf-8")
    (data / ".video_id").write_text("abcdefghijk", encoding="utf-8")
    (data / "x.description").write_text("description", encoding="utf-8")
    (data / "x.info.json").write_text("{}", encoding="utf-8")
    (data / "x.jpg").write_bytes(b"image")

    report = folder / "report.html"
    report.write_text('<select id="speedSelect"></select><script>seekTo(1)</script>VideoLibraryManager v'+backend.APP_VERSION, encoding="utf-8")
    with patch.object(backend, "canonical_metadata_available", lambda *_args: True):
        ok, checks = backend.validate_video_outputs(
            folder, "x", "abcdefghijk", video, report,
            require_transcript=False, require_report=True,
        )

    assert ok is True
    values = {name: (passed, path) for name, passed, path in checks}
    assert values["Timestamped transcript"] == (True, "NOT REQUESTED")
    assert values["Detailed summaries"] == (True, "NOT REQUESTED")
    assert values["Timestamp-bound source blocks"] == (True, "NOT REQUESTED")


def test_cancelled_video_does_not_continue_through_fallback_strategies() -> None:
    backend = _backend()
    calls: list[list[str]] = []

    def stopped(args, *_args, **_kwargs):
        calls.append(list(args))
        return 130, "", "STOPPED BY USER"

    with patch.multiple(
        backend,
        youtube_download_attempts=lambda *_args: [("first", ["first"]), ("second", ["second"])],
        run_download_with_progress=stopped,
        web_stop_requested=lambda: True,
        set_state=lambda **kwargs: None,
        console_newline=lambda: None,
    ):
        rc, _output, error = backend.run_video_with_fallback([], "url", "360", "title")

    assert rc == 130
    assert error == "STOPPED BY USER"
    assert calls == []


def test_per_video_log_reader_filters_child_events(tmp_path: Path) -> None:
    backend = _backend()
    with patch.object(backend, "BASE", tmp_path):
        backend.web_job_log("job", "video_started", video_id="one", title="One")
        backend.web_job_log("job", "video_progress", video_id="two", percent=50, speed="1MiB/s")
        backend.web_job_log("job", "video_finished", video_id="one", status="SUCCESS")
        filtered = backend.web_job_video_log("job", "one")
        complete = backend.web_job_video_log("job")

    assert len(filtered) == 2
    assert all("[one]" in line for line in filtered)
    assert any("[two]" in line and "50%" in line for line in complete)


def test_progress_uses_current_transfer_when_batch_processed_is_zero() -> None:
    job = {
        "status": "RUNNING",
        "batch_processed": 0,
        "batch_total": 1,
        "transfer_percent": 47,
    }
    assert overall_progress_percent(job, {}) == 47
    job = {
        "status": "RUNNING",
        "batch_processed": 1,
        "batch_total": 2,
        "transfer_percent": 50,
    }
    assert overall_progress_percent(job, {}) == 75


def test_empty_backend_result_never_becomes_successful_input_ledger() -> None:
    outcomes = ensure_input_outcomes(["https://x"], ["https://x"], {"ok": True, "results": []})
    assert outcomes == [
        {
            "input_url": "https://x",
            "effective_url": "https://x",
            "status": "FAILED",
            "stage": "result_accounting",
            "message": "No processable result was returned for this input.",
        }
    ]
    aggregate = aggregate_input_outcomes(outcomes)
    assert aggregate["ok"] is False
    assert aggregate["outcome_counts"]["FAILED"] == 1


def test_full_download_empty_metadata_fails_and_does_not_mutate_global_options() -> None:
    backend = _backend()
    originals = {
        name: getattr(backend, name)
        for name in (
            "web_write_urls",
            "metadata_scan",
            "rows_for_current_urls",
            "export_artifact_registry",
            "print_all_downloads_done_banner",
        )
    }
    cfg_before = dict(backend.CFG)
    runtime_before = dict(backend.RUNTIME)
    try:
        backend.web_write_urls = lambda urls: list(urls)
        backend.metadata_scan = lambda: None
        backend.rows_for_current_urls = lambda: []
        backend.export_artifact_registry = lambda: ""
        backend.print_all_downloads_done_banner = lambda: None
        result = backend.web_full_download(
            ["https://www.youtube.com/watch?v=unavailable1"],
            quality="720",
            use_ollama=True,
            save_srt=True,
        )
    finally:
        for name, value in originals.items():
            setattr(backend, name, value)
    assert result["ok"] is False
    assert result["status"] == "FAILED"
    assert result["resolved"] == 0
    assert result["input_outcomes"][0]["status"] == "FAILED"
    assert backend.CFG == cfg_before
    assert backend.RUNTIME == runtime_before


def test_cancel_running_job_is_scoped_and_later_jobs_run() -> None:
    backend = _backend()
    # Use the actual managed worker and queue.  No other test starts it.
    with backend.WEB_JOB_LOCK:
        backend.WEB_JOBS.clear()
        backend.WEB_JOB_TASKS.clear()
        backend.WEB_JOB_CONTEXTS.clear()
        backend.WEB_QUEUE_PAUSED = False
    backend.WEB_STOP_EVENT.clear()
    backend.STOP = False

    started = threading.Event()
    release = threading.Event()
    ran: list[str] = []

    def first() -> dict:
        started.set()
        release.wait(3)
        return {"ok": True}

    def later(name: str) -> dict:
        ran.append(name)
        return {"ok": True}

    a = backend.web_start_job("A", first)
    backend.web_job_update(a, active_videos=[
        {"video_id": "one", "title": "One", "status": "RUNNING", "stage": "Downloading", "percent": 42},
        {"video_id": "two", "title": "Two", "status": "QUEUED", "stage": "Queued", "percent": 0},
    ])
    b = backend.web_start_job("B", later, "B")
    c = backend.web_start_job("C", later, "C")
    assert started.wait(2)
    ok, _ = backend.web_cancel_job(a)
    assert ok is True
    d = backend.web_start_job("D", later, "D")
    assert backend.WEB_JOB_CONTEXTS[a].cancelled() is True
    assert {row["status"] for row in backend.WEB_JOBS[a]["active_videos"]} == {"CANCELLING"}
    release.set()
    deadline = time.time() + 5
    while time.time() < deadline:
        states = [backend.WEB_JOBS[j]["status"] for j in (a, b, c, d)]
        if all(x in {"SUCCESS", "WARN", "FAILED", "CANCELLED"} for x in states):
            break
        time.sleep(0.05)
    assert backend.WEB_JOBS[a]["status"] == "CANCELLED"
    assert backend.WEB_JOBS[b]["status"] == "SUCCESS"
    assert backend.WEB_JOBS[c]["status"] == "SUCCESS"
    assert backend.WEB_JOBS[d]["status"] == "SUCCESS"
    assert ran == ["B", "C", "D"]
    assert backend.WEB_STOP_EVENT.is_set() is False


def test_cancel_one_child_does_not_cancel_its_sibling() -> None:
    backend = _backend()
    parent_id = "parent-child-isolation"
    with backend.WEB_JOB_LOCK:
        backend.WEB_JOBS[parent_id] = {
            "job_id": parent_id,
            "status": "RUNNING",
            "active_videos": [
                {"video_id": "one", "status": "RUNNING", "percent": 25},
                {"video_id": "two", "status": "RUNNING", "percent": 40},
            ],
        }
        backend.WEB_CHILD_CONTEXTS.clear()
    first = backend.web_child_context(parent_id, "one")
    second = backend.web_child_context(parent_id, "two")

    with patch.object(backend, "web_persist_job_state", lambda **_kwargs: None):
        ok, message = backend.web_cancel_child_job(parent_id, "one")

    assert ok is True
    assert "sibling" in message.lower()
    assert first.cancelled() is True
    assert second.cancelled() is False
    rows = {row["video_id"]: row for row in backend.WEB_JOBS[parent_id]["active_videos"]}
    assert rows["one"]["status"] == "CANCELLING"
    assert rows["two"]["status"] == "RUNNING"


def test_external_media_uses_its_own_child_context_and_records_retry_identity(tmp_path: Path) -> None:
    backend = _backend()
    parent_id = "external-parent"
    url = "https://example.invalid/live.m3u8"
    external_id = "EXT_" + __import__("hashlib").sha1(url.encode()).hexdigest()[:14]
    seen_contexts: list[str] = []

    class FakeConnection:
        def execute(self, *_args, **_kwargs):
            return self
        def commit(self):
            return None
        def close(self):
            return None

    def fake_run(args, **_kwargs):
        context = backend.web_current_job_context()
        seen_contexts.append(context.job_id if context else "")
        if "--dump-single-json" in args:
            return 0, '{"title":"External test","protocol":"m3u8"}', ""
        output = Path(args[args.index("-o") + 1].replace("%(ext)s", "mp4"))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"media")
        return 0, "", ""

    with backend.WEB_JOB_LOCK:
        backend.WEB_JOBS[parent_id] = {"job_id": parent_id, "status": "RUNNING", "active_videos": []}
        backend.WEB_CHILD_CONTEXTS.clear()
    backend.WEB_JOB_CONTEXT.job_id = parent_id
    backend.WEB_JOB_CONTEXT.context = backend.JobContext(parent_id)
    backend.web_seed_video_progress([{"video_id": external_id, "title": url, "source_url": url}])

    with patch.multiple(
        backend,
        external_media_root=lambda category="Streams": tmp_path,
        run=fake_run,
        db_connect=lambda: FakeConnection(),
        web_persist_job_state=lambda **_kwargs: None,
    ):
        result = backend._web_external_media_download_serial([url])

    assert result["ok"] is True
    assert seen_contexts and set(seen_contexts) == {f"{parent_id}:{external_id}"}
    child = backend.WEB_JOBS[parent_id]["active_videos"][0]
    assert child["source_url"] == url
    assert child["status"] == "SUCCESS"
    assert child["log_path"].endswith(f"{external_id}.jsonl")


def test_stop_everything_remains_queue_wide() -> None:
    backend = _backend()
    started = threading.Event()

    def blocking() -> dict:
        started.set()
        deadline = time.time() + 3
        while time.time() < deadline and not backend.web_stop_requested():
            time.sleep(0.02)
        return {"ok": False, "status": "CANCELLED"}

    a = backend.web_start_job("stop-A", blocking)
    b = backend.web_start_job("stop-B", lambda: {"ok": True})
    assert started.wait(2)
    backend.web_stop_everything()
    deadline = time.time() + 5
    while time.time() < deadline:
        if backend.WEB_JOBS[a]["status"] in {"CANCELLED", "FAILED"} and backend.WEB_JOBS[b]["status"] == "CANCELLED":
            break
        time.sleep(0.05)
    assert backend.WEB_JOBS[a]["status"] == "CANCELLED"
    assert backend.WEB_JOBS[b]["status"] == "CANCELLED"
