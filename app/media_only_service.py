"""Validation/materialization helpers for Media Only and Audio Only downloads."""
from __future__ import annotations

from pathlib import Path
from typing import Callable


def usable_media_file(value: object) -> Path | None:
    """Return a non-empty media file path, otherwise ``None``."""
    if not value:
        return None
    try:
        path = Path(str(value))
        if path.is_file() and path.stat().st_size > 0:
            return path
    except (OSError, ValueError, TypeError):
        return None
    return None


def create_srt_from_vtt(vtt_path: object, converter: Callable[[str], str]) -> Path | None:
    """Create an SRT beside a VTT when useful subtitle text is available."""
    if not vtt_path:
        return None
    try:
        source = Path(str(vtt_path))
        if not source.is_file() or source.stat().st_size <= 0:
            return None
        text = converter(source.read_text(encoding="utf-8", errors="replace"))
        if not str(text or "").strip():
            return None
        target = source.with_suffix(".srt")
        target.write_text(str(text), encoding="utf-8")
        return target if target.is_file() and target.stat().st_size > 0 else None
    except (OSError, ValueError, TypeError):
        return None
