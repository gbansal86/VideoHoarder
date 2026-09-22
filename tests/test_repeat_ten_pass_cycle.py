from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch


def test_transcript_cleanup_preserves_equal_size_different_content(tmp_path: Path):
    from app import app as backend

    trans = tmp_path / "tmp_transcripts"
    shorts = tmp_path / "tmp_shorts"
    archive = tmp_path / "archive"
    trans.mkdir(); shorts.mkdir(); archive.mkdir()
    vid = "vid-cleanup"
    src = trans / vid
    dst = archive / "complete" / vid
    src.mkdir(parents=True); dst.mkdir(parents=True)
    (src / "same.txt").write_bytes(b"AAAA")
    (dst / "same.txt").write_bytes(b"BBBB")

    with patch.multiple(
        backend,
        temp_transcript_root=lambda: trans,
        temp_short_video_root=lambda: shorts,
        transcript_archive_root=lambda: archive,
        transcript_archive_category=lambda _vid: ("complete", {"ok": True}),
    ):
        result = backend.cleanup_temp_after_success(vid)

    assert result[0] == "MOVED"
    assert (dst / "same.txt").read_bytes() == b"BBBB"
    conflicts = [p for p in dst.glob("same_archive*.txt")]
    assert len(conflicts) == 1
    assert conflicts[0].read_bytes() == b"AAAA"


def test_temp_transcript_move_preserves_equal_size_different_content(tmp_path: Path):
    from app import app as backend

    trans = tmp_path / "tmp_transcripts"
    archive = tmp_path / "archive"
    trans.mkdir(); archive.mkdir()
    vid = "vid-move"
    src = trans / vid
    dst = archive / "complete" / vid
    src.mkdir(parents=True); dst.mkdir(parents=True)
    (src / "same.txt").write_bytes(b"CCCC")
    (dst / "same.txt").write_bytes(b"DDDD")

    with patch.multiple(
        backend,
        temp_transcript_root=lambda: trans,
        transcript_archive_root=lambda: archive,
        transcript_archive_category=lambda _vid: ("complete", {"ok": True}),
    ):
        result = backend.move_temp_transcript_out_of_tmp(vid)

    assert result[0] == "MOVED"
    assert (dst / "same.txt").read_bytes() == b"DDDD"
    conflicts = [p for p in dst.glob("same_archive*.txt")]
    assert len(conflicts) == 1
    assert conflicts[0].read_bytes() == b"CCCC"


def test_phase2_legacy_migration_preserves_different_content(tmp_path: Path):
    from app import app as backend

    legacy = tmp_path / "legacy"
    packages = tmp_path / "packages"
    results = tmp_path / "results"
    retry = tmp_path / "retry"
    archive = tmp_path / "archive"
    history = tmp_path / "history"
    for p in (legacy, packages, results, retry, archive, history):
        p.mkdir()
    (legacy / "x.json").write_bytes(b"1111")
    (packages / "x.json").write_bytes(b"2222")

    with patch.multiple(
        backend,
        phase2_legacy_paths=lambda: {"packages": [legacy], "results": [], "retry": [], "archive": []},
        phase2_chatgpt_dirs=lambda: (packages, results, retry, archive, history),
    ):
        copied, moved, skipped, failed = backend.phase2_migrate_legacy_storage(copy_only=True)

    assert (copied, moved, skipped, failed) == (1, 0, 0, 0)
    assert (packages / "x.json").read_bytes() == b"2222"
    conflicts = list(packages.glob("x_legacy*.json"))
    assert len(conflicts) == 1
    assert conflicts[0].read_bytes() == b"1111"


def test_youtube_host_detection_rejects_lookalike_domains():
    from app.youtube_url import is_youtube_url, parse_youtube_reference
    from app.download_access import is_youtube_url as access_is_youtube_url

    good = [
        "https://youtube.com/watch?v=ABC123",
        "https://www.youtube.com/live/ABC123",
        "https://m.youtube.com/shorts/ABC123",
        "https://youtu.be/ABC123",
    ]
    bad = [
        "https://wyoutube.com/watch?v=ABC123",
        "https://wwyoutube.com/watch?v=ABC123",
        "https://youtube.com.evil.example/watch?v=ABC123",
        "https://evil-youtube.com/watch?v=ABC123",
    ]
    for url in good:
        assert is_youtube_url(url) is True
        assert access_is_youtube_url(url) is True
    for url in bad:
        assert is_youtube_url(url) is False
        assert access_is_youtube_url(url) is False
        assert parse_youtube_reference(url).video_id == ""


def test_windows_reserved_names_with_spaces_before_extension_are_escaped():
    from app.file_safety import windows_safe_component

    for name in ["CON .txt", "AUX .json", "NUL .bin", "COM1 .log", "LPT9 .txt"]:
        assert windows_safe_component(name).startswith("_")


def test_native_settings_do_not_offer_audio_as_video_quality_and_privacy_text_matches_default():
    native = Path("app/native_ui.py").read_text(encoding="utf-8")
    assert 'self.quality.addItems(("1080", "720", "480", "360", "best"))' in native
    assert 'self.quality.addItems(("1080", "720", "480", "360", "best", "audio"))' not in native
    assert "Browser-cookie access is off by default" in native
    assert "Browser cookies are enabled by default" not in native


def test_oauth_help_is_portable_not_d_drive_specific():
    source = Path("app/app.py").read_text(encoding="utf-8")
    assert "Desktop OAuth JSON not found. Set VIDEOHOARDER_CLIENT_SECRET" in source
    assert "Google OAuth desktop JSON — uses VIDEOHOARDER_CLIENT_SECRET or client_secret.json" in source
    assert "D:\\YT GUi\\client_secret.json" not in source


def test_pristine_code_parent_preserves_full_config_example_schema(tmp_path: Path):
    import scripts.create_code_parent_package as packager

    pristine = tmp_path / "source"
    app_dir = pristine / "app"
    app_dir.mkdir(parents=True)
    default = {"workers": 12, "download_quality": "1080", "cookies_mode": "none", "youtube_data_api_key": ""}
    (app_dir / "config.default.json").write_text(json.dumps(default), encoding="utf-8")
    packaged = tmp_path / "out" / "Source"
    packaged.mkdir(parents=True)

    with patch.object(packager, "SOURCE_ROOT", pristine):
        packager._write_sanitized_templates(packaged)

    example = json.loads((packaged / "app" / "config.example.json").read_text(encoding="utf-8"))
    assert set(example) == set(default) | set(packager.SANITIZED_CONFIG_OVERRIDES)
    assert example["cookies_mode"] == "none"
    assert example["youtube_data_api_key"] == ""
