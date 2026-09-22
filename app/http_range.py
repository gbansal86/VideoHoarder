"""Single-range HTTP byte parser used by local media streaming."""
from __future__ import annotations

class RangeNotSatisfiable(ValueError):
    pass


def parse_single_byte_range(header: str, size: int) -> tuple[int, int] | None:
    """Return inclusive (start,end), None for no Range, or raise for 416.

    Supports ``N-M``, ``N-``, and suffix ``-N``. Multiple ranges are rejected
    because the local server does not emit multipart/byteranges.
    """
    if not header:
        return None
    if size < 0 or not header.startswith("bytes="):
        raise RangeNotSatisfiable("Unsupported range unit")
    spec = header[6:].strip()
    if not spec or "," in spec or "-" not in spec:
        raise RangeNotSatisfiable("Only one byte range is supported")
    left, right = (part.strip() for part in spec.split("-", 1))
    if size == 0:
        raise RangeNotSatisfiable("Empty resource")
    try:
        if left:
            start = int(left)
            if start < 0 or start >= size:
                raise RangeNotSatisfiable("Range start outside resource")
            if right:
                end = int(right)
                if end < start:
                    raise RangeNotSatisfiable("Range end precedes start")
                end = min(end, size - 1)
            else:
                end = size - 1
            return start, end
        # suffix-byte-range-spec: bytes=-N means last N bytes.
        suffix = int(right)
        if suffix <= 0:
            raise RangeNotSatisfiable("Suffix length must be positive")
        length = min(suffix, size)
        return size - length, size - 1
    except ValueError as exc:
        if isinstance(exc, RangeNotSatisfiable):
            raise
        raise RangeNotSatisfiable("Invalid byte range") from exc
