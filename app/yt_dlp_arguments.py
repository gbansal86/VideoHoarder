"""Safe, centralized yt-dlp argument helpers used by download jobs."""

from __future__ import annotations

from typing import Iterable


def bounded_int(value: object, default: int, low: int, high: int) -> int:
    try:
        number = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        number = int(default)
    return max(int(low), min(int(high), number))


def add_download_performance_args(
    args: Iterable[str],
    *,
    concurrent_fragments: object = 4,
) -> list[str]:
    """Return a new argv list with bounded media-transfer performance flags.

    This helper intentionally accepts and returns argument arrays.  It never
    constructs a shell command string.
    """

    result = [str(value) for value in args]
    fragments = bounded_int(concurrent_fragments, 4, 1, 16)
    result.extend(["--concurrent-fragments", str(fragments)])
    return result
