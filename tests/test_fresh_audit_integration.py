from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import patch


def test_legacy_migration_preserves_equal_size_different_content(tmp_path: Path):
    from app import app as backend
    old_base = backend.BASE
    try:
        backend.BASE = tmp_path
        legacy = tmp_path / "video_library.db"
        canonical = tmp_path / "data" / "database" / "video_library.db"
        canonical.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_bytes(b"AAAA")
        canonical.write_bytes(b"BBBB")
        backend.migrate_legacy_root_files()
        assert canonical.read_bytes() == b"BBBB"
        conflicts = list(canonical.parent.glob("video_library_legacy*.db"))
        assert len(conflicts) == 1
        assert conflicts[0].read_bytes() == b"AAAA"
        assert not legacy.exists()
    finally:
        backend.BASE = old_base


def test_staging_commit_preserves_equal_size_different_media(tmp_path: Path):
    from app import app as backend
    staging = tmp_path / "staging"
    final = tmp_path / "final"
    (staging / "_data").mkdir(parents=True)
    (final / "_data").mkdir(parents=True)
    staged_media = staging / "video.mp4"
    final_media = final / "video.mp4"
    staged_media.write_bytes(b"AAAA")
    final_media.write_bytes(b"BBBB")
    with patch.multiple(
        backend,
        staging_dir=lambda vid, create=True: staging,
        video_folder_path=lambda title, upload_date, channel, vid: final,
        refresh_db_artifact_paths=lambda *args, **kwargs: None,
        find_any_media=lambda folder: next(Path(folder).glob("*.mp4"), None),
    ):
        backend.commit_staging_to_library("vid123", "2026-09-14", "Title", "Channel")
    assert final_media.read_bytes() == b"BBBB"
    conflicts = [p for p in final.glob("*.mp4") if p.name != "video.mp4"]
    assert len(conflicts) == 1
    assert conflicts[0].read_bytes() == b"AAAA"


def test_corrupt_config_is_quarantined_and_safe_defaults_restored(tmp_path: Path):
    from app import app as backend
    old_config = backend.CONFIG
    old_warning = backend.CONFIG_LOAD_WARNING
    try:
        backend.CONFIG = tmp_path / "app" / "config.json"
        backend.CONFIG.parent.mkdir(parents=True)
        backend.CONFIG.write_text("{broken", encoding="utf-8")
        cfg = backend.load_config()
        assert cfg["cookies_mode"] == "none"
        assert backend.CONFIG.exists()
        assert any(backend.CONFIG.parent.glob("config.corrupt_*.json"))
        assert "Invalid config.json" in backend.CONFIG_LOAD_WARNING
    finally:
        backend.CONFIG = old_config
        backend.CONFIG_LOAD_WARNING = old_warning


def test_frozen_dependency_installers_do_not_invoke_exe_as_pip():
    from app import app as backend
    with patch.object(backend, "transcript_api_import", return_value=None), patch.object(backend.sys, "frozen", True, create=True), patch.object(backend.subprocess, "run") as run:
        ok, message = backend.install_youtube_transcript_api()
        assert ok is False
        assert "cannot be used as a pip interpreter" in message
        run.assert_not_called()
    with patch.object(backend, "selenium_status", return_value={"ok": True, "installed": False, "version": "", "message": "missing"}), patch.object(backend.sys, "frozen", True, create=True), patch.object(backend.subprocess, "Popen") as popen:
        result = backend.ensure_selenium_installed(True)
        assert result["installed"] is False
        assert "cannot run pip" in result["message"]
        popen.assert_not_called()


def test_verified_portable_download_accepts_hash_and_rejects_wrong_hash(tmp_path: Path):
    from app import app as backend
    source = tmp_path / "source.bin"
    source.write_bytes(b"verified payload")
    expected = hashlib.sha256(source.read_bytes()).hexdigest()
    old_tools = backend.TOOLS
    try:
        backend.TOOLS = tmp_path / "tools"
        good = tmp_path / "good.bin"
        ok, message = backend.download_file(source.as_uri(), good, "fixture", expected)
        assert ok is True
        assert good.read_bytes() == source.read_bytes()
        bad = tmp_path / "bad.bin"
        ok, message = backend.download_file(source.as_uri(), bad, "fixture", "0" * 64)
        assert ok is False
        assert "SHA-256 mismatch" in message
        assert not bad.exists()
    finally:
        backend.TOOLS = old_tools


def test_managed_job_uses_its_own_urls_file_and_keeps_canonical_batch(tmp_path: Path):
    from app import app as backend
    from app.job_execution_service import JobContext
    old_base, old_urls = backend.BASE, backend.URLS
    old_job_id = getattr(backend.WEB_JOB_CONTEXT, "job_id", None)
    old_ctx = getattr(backend.WEB_JOB_CONTEXT, "context", None)
    try:
        backend.BASE = tmp_path
        backend.URLS = tmp_path / "urls.txt"
        backend.WEB_JOB_CONTEXT.job_id = None
        backend.WEB_JOB_CONTEXT.context = None
        backend.web_write_urls(["https://example.test/a", "https://example.test/b"])
        assert backend.URLS.read_text(encoding="utf-8").splitlines() == ["https://example.test/a", "https://example.test/b"]
        ctx = JobContext("job-1")
        backend.WEB_JOB_CONTEXT.job_id = "job-1"
        backend.WEB_JOB_CONTEXT.context = ctx
        backend.web_write_urls(["https://example.test/a"])
        assert backend.load_urls() == ["https://example.test/a"]
        assert backend.URLS.read_text(encoding="utf-8").splitlines() == ["https://example.test/a", "https://example.test/b"]
    finally:
        backend.BASE, backend.URLS = old_base, old_urls
        backend.WEB_JOB_CONTEXT.job_id = old_job_id
        backend.WEB_JOB_CONTEXT.context = old_ctx
