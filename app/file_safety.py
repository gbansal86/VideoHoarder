"""Filesystem safety helpers shared by migration, staging and Windows naming paths."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

_WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def file_sha256(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    target = Path(path)
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_equal(left: str | Path, right: str | Path) -> bool:
    """Return True only when two ordinary files have identical content."""
    a, b = Path(left), Path(right)
    try:
        if not a.is_file() or not b.is_file():
            return False
        if a.resolve() == b.resolve():
            return True
        if a.stat().st_size != b.stat().st_size:
            return False
        # Hash only after the cheap size check.  SHA-256 avoids destructive
        # false-positive dedupe when equal-sized files contain different bytes.
        return file_sha256(a) == file_sha256(b)
    except OSError:
        return False


def unique_conflict_path(target: str | Path, *, marker: str = "conflict") -> Path:
    """Return an unused sibling path without overwriting existing content."""
    path = Path(target)
    index = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{marker}{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def windows_safe_component(value: str, fallback: str = "video", *, max_chars: int = 140) -> str:
    """Sanitize one Windows filename component, including device names."""
    text = str(value or "").strip().strip(" .")
    text = re.sub(r'[<>:"/\\|?*]', " ", text)
    text = re.sub(r"\s+", " ", text).strip(" .-_–—")
    text = text[:max_chars].rstrip(" .")
    if not text:
        text = str(fallback or "video").strip() or "video"
    # Device names are reserved even with an extension (CON.txt, AUX.json...).
    stem = text.split(".", 1)[0].rstrip(" .").upper()
    if stem in _WINDOWS_RESERVED:
        text = "_" + text
    # Windows also rejects components ending in a dot/space after truncation.
    text = text.rstrip(" .")
    return text or str(fallback or "video")
