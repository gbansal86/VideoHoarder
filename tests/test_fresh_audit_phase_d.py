import hashlib
from pathlib import Path
from app.job_persistence_service import task_descriptor


def test_retry_descriptor_rejects_arbitrary_objects_and_paths():
    def work(*args, **kwargs):
        pass
    class Weird:
        def __str__(self):
            return "<WEIRD OBJ>"
    assert task_descriptor(work, (Weird(),), {}) is None
    assert task_descriptor(work, (Path("x"),), {}) is None
    assert task_descriptor(work, ({1: "bad-key"},), {}) is None
    assert task_descriptor(work, (["ok", 1, True, {"x": None}],), {}) is not None


def test_tool_downloads_require_integrity_by_default():
    import json
    cfg=json.loads(Path("app/config.default.json").read_text(encoding="utf-8"))
    assert cfg["allow_unverified_tool_downloads"] is False
    assert cfg["allow_unverified_tool_updates"] is False
    assert cfg["auto_update_ytdlp_on_403"] is False
    assert isinstance(cfg["tool_download_sha256"], dict)


def test_download_file_verifies_sha256_source_contract():
    text=Path("app/app.py").read_text(encoding="utf-8")
    assert 'SHA-256 mismatch for {label}' in text
    assert 'Blocked unverified {name} download' in text
    assert 'yt-dlp self-update blocked by integrity policy' in text
