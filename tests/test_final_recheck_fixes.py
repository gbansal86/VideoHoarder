from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.job_persistence_service import atomic_write, interrupted_copy, load, queue_payload
from app.lru_cache import LRUCache

ROOT = Path(__file__).parents[1]


def _noop() -> None:
    return None


def test_queue_payload_never_drops_recoverable_jobs_above_history_limit() -> None:
    jobs = {}
    tasks = {}
    for i in range(150):
        jid = f"active-{i:03d}"
        jobs[jid] = {"job_id": jid, "label": jid, "status": "QUEUED", "created_at": float(i)}
        tasks[jid] = (_noop, (), {})
    for i in range(150):
        jid = f"done-{i:03d}"
        jobs[jid] = {"job_id": jid, "label": jid, "status": "SUCCESS", "created_at": float(1000 + i)}
    payload = queue_payload(jobs, tasks, limit=100)
    persisted_ids = {row["job_id"] for row in payload["jobs"]}
    assert all(f"active-{i:03d}" in persisted_ids for i in range(150))
    assert len([row for row in payload["jobs"] if row["status"] == "SUCCESS"]) == 100
    assert len(payload["jobs"]) == 250


def test_queue_payload_is_compact_and_omits_large_terminal_results() -> None:
    jobs = {
        "j1": {
            "job_id": "j1",
            "label": "Compact",
            "status": "INTERRUPTED",
            "created_at": 1.0,
            "message": "resume me",
            "download_options": {"quality": "1080"},
            "result": {"blob": "x" * (1024 * 1024)},
            "private_internal": "not for restart state",
        }
    }
    payload = queue_payload(jobs, {}, limit=100)
    row = payload["jobs"][0]
    assert row["job_id"] == "j1"
    assert row["download_options"] == {"quality": "1080"}
    assert "result" not in row
    assert "private_internal" not in row
    assert len(json.dumps(payload)) < 10_000


def test_child_download_state_survives_persistence_and_active_rows_become_interrupted() -> None:
    job = {
        "job_id": "parent",
        "status": "RUNNING",
        "active_videos": [
            {"video_id": "running", "source_url": "https://example/r", "status": "RUNNING"},
            {"video_id": "done", "source_url": "https://example/d", "status": "SUCCESS"},
        ],
    }
    persisted = queue_payload({"parent": job}, {}, limit=100)["jobs"][0]
    restored = interrupted_copy(persisted)
    rows = {row["video_id"]: row for row in restored["active_videos"]}
    assert restored["status"] == "INTERRUPTED"
    assert rows["running"]["status"] == "INTERRUPTED"
    assert rows["done"]["status"] == "SUCCESS"
    assert rows["running"]["source_url"] == "https://example/r"


def test_atomic_queue_write_is_safe_under_concurrent_writers(tmp_path: Path) -> None:
    state = tmp_path / "job_queue_state.json"

    def writer(index: int) -> None:
        atomic_write(state, {"schema": 2, "jobs": [{"job_id": str(index)}], "tasks": {}})

    with ThreadPoolExecutor(max_workers=16) as pool:
        list(pool.map(writer, range(300)))
    final = load(state)
    assert final["schema"] == 2
    assert len(final["jobs"]) == 1
    assert list(tmp_path.glob("*.tmp")) == []


def test_frozen_runtime_hook_uses_only_bundled_meipass_runtime() -> None:
    source = (ROOT / "build_support" / "pyi_rth_videohoarder_qt.py").read_text(encoding="utf-8")
    assert "runtime_root = Path(sys._MEIPASS)" in source
    assert ".videohoarder-build" not in source
    assert "external_runtime" not in source


def test_legacy_media_ui_exposes_and_forwards_save_srt() -> None:
    source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")
    assert 'id="mediaSrt"' in source
    assert "save_srt:$('mediaSrt').value==='1'" in source


def test_thumbnail_lru_cache_is_bounded() -> None:
    cache = LRUCache[str, int](max_items=3)
    for i in range(10):
        cache.put(str(i), i)
    assert len(cache) == 3
    assert cache.get("7") == 7
    cache.put("10", 10)
    assert len(cache) == 3
    assert cache.get("8") is None


def test_readme_matches_current_onefile_and_optional_deploy_contract() -> None:
    readme = (ROOT / "DESKTOP_README.md").read_text(encoding="utf-8")
    assert "dist\\VideoHoarder.exe" in readme
    assert "one-file" in readme
    assert "one-folder mode" not in readme
    assert "-Deploy" in readme
    assert "does **not** replace the live installed EXE" in readme


def test_backend_persist_restore_keeps_all_150_unfinished_jobs(tmp_path: Path) -> None:
    from app import app as backend

    old_base = backend.BASE
    old_jobs = dict(backend.WEB_JOBS)
    old_tasks = dict(backend.WEB_JOB_TASKS)
    old_contexts = dict(backend.WEB_JOB_CONTEXTS)
    old_restored = backend.WEB_JOBS_RESTORED
    old_last = backend.WEB_JOB_PERSIST_LAST
    try:
        backend.BASE = tmp_path
        backend.WEB_JOBS.clear(); backend.WEB_JOB_TASKS.clear(); backend.WEB_JOB_CONTEXTS.clear()
        backend.WEB_JOBS_RESTORED = False
        backend.WEB_JOB_PERSIST_LAST = 0.0
        for i in range(150):
            jid = f"bulk-{i:03d}"
            backend.WEB_JOBS[jid] = {
                "job_id": jid, "label": jid, "status": "QUEUED", "created_at": float(i),
                "result": {"blob": "x" * 1000},
            }
            backend.WEB_JOB_TASKS[jid] = (backend.web_library_stats, (), {})
        assert backend.web_persist_job_state(force=True)
        saved = json.loads(backend.web_job_state_path().read_text(encoding="utf-8"))
        assert len(saved["jobs"]) == 150
        assert all("result" not in row for row in saved["jobs"])
        backend.WEB_JOBS.clear(); backend.WEB_JOB_TASKS.clear(); backend.WEB_JOB_CONTEXTS.clear()
        backend.WEB_JOBS_RESTORED = False
        restored = backend.web_restore_persisted_jobs(force=True)
        assert restored["restored"] == 150
        assert restored["interrupted"] == 150
        assert len(backend.WEB_JOBS) == 150
    finally:
        backend.BASE = old_base
        backend.WEB_JOBS.clear(); backend.WEB_JOBS.update(old_jobs)
        backend.WEB_JOB_TASKS.clear(); backend.WEB_JOB_TASKS.update(old_tasks)
        backend.WEB_JOB_CONTEXTS.clear(); backend.WEB_JOB_CONTEXTS.update(old_contexts)
        backend.WEB_JOBS_RESTORED = old_restored
        backend.WEB_JOB_PERSIST_LAST = old_last
