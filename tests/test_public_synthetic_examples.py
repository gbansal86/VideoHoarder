from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "synthetic_local_import"

MEDIA_SUFFIXES = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".wmv", ".flv",
    ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg",
}


def test_synthetic_example_contains_no_media_or_remote_urls() -> None:
    assert EXAMPLE.is_dir()

    files = [path for path in EXAMPLE.rglob("*") if path.is_file()]
    assert files

    media = [path.relative_to(ROOT).as_posix() for path in files if path.suffix.lower() in MEDIA_SUFFIXES]
    assert not media, f"Public synthetic examples must not contain media files: {media}"

    for path in files:
        if path.suffix.lower() in {".md", ".json", ".srt", ".vtt", ".txt"}:
            text = path.read_text(encoding="utf-8").lower()
            assert "http://" not in text
            assert "https://" not in text


def test_synthetic_metadata_is_explicitly_marked_synthetic() -> None:
    metadata = json.loads((EXAMPLE / "demo_video.metadata.json").read_text(encoding="utf-8"))
    assert metadata["synthetic"] is True
    assert metadata["platform"] == "local"
    assert "source_url" not in metadata
    assert "video_id" not in metadata


def test_synthetic_subtitle_declares_its_public_fixture_role() -> None:
    subtitle = (EXAMPLE / "demo_video.srt").read_text(encoding="utf-8").lower()
    assert "synthetic" in subtitle
    assert "private media" in subtitle
