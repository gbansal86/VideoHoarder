"""Source chapter navigation handling for VideoHoarder.

YouTube/source chapters are navigation/seeking structure only.  Their original
source title and timestamps remain recoverable and are never overwritten by AI
or semantic chapter generation.  A separate display title and validated
transcript-supported subchapters may be layered on top later.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any


def _text(value: Any) -> str:
    return str(value or "").strip()


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_source_chapters(value: Any) -> list[dict[str, Any]]:
    """Normalize source chapters without interpreting or rewriting their meaning."""

    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    result: list[dict[str, Any]] = []
    for chapter in value:
        if not isinstance(chapter, Mapping):
            continue
        start = _float_or_none(chapter.get("start_time", chapter.get("start_seconds")))
        end = _float_or_none(chapter.get("end_time", chapter.get("end_seconds")))
        source_title = _text(chapter.get("source_title", chapter.get("title")))
        display_title = _text(chapter.get("display_title"))
        if start is None and end is None and not source_title:
            continue
        row = {
            "start_seconds": start,
            "end_seconds": end,
            "source_title": source_title,
            "display_title": display_title,
        }
        normalized_subchapters = _normalize_subchapters(chapter.get("subchapters"))
        if normalized_subchapters:
            row["subchapters"] = normalized_subchapters
        result.append(row)
    return result


def _normalize_subchapters(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    rows: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            continue
        start = _float_or_none(item.get("start_seconds", item.get("start_time")))
        end = _float_or_none(item.get("end_seconds", item.get("end_time")))
        title = _text(item.get("title", item.get("display_title")))
        if start is None or not title:
            continue
        rows.append({"start_seconds": start, "end_seconds": end, "title": title})
    return rows


def effective_chapter_title(chapter: Mapping[str, Any]) -> str:
    """Return display title when supplied, otherwise the immutable source title."""

    return _text(chapter.get("display_title")) or _text(chapter.get("source_title"))


def apply_navigation_enhancements(
    source_chapters: Any,
    *,
    display_titles: Mapping[int, str] | None = None,
    subchapters: Mapping[int, Sequence[Mapping[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    """Layer display titles/subchapters without changing source titles/timestamps.

    Enhancements are keyed by zero-based source chapter index.  Subchapters
    must fit within the parent chapter interval when that boundary is known.
    Invalid subchapters raise ``ValueError`` instead of silently corrupting the
    navigation hierarchy.
    """

    chapters = normalize_source_chapters(source_chapters)
    display_titles = display_titles or {}
    subchapters = subchapters or {}
    out = deepcopy(chapters)

    for idx, chapter in enumerate(out):
        if idx in display_titles:
            improved = _text(display_titles[idx])
            if improved:
                chapter["display_title"] = improved
        if idx in subchapters:
            normalized = _normalize_subchapters(subchapters[idx])
            parent_start = chapter.get("start_seconds")
            parent_end = chapter.get("end_seconds")
            previous_start: float | None = None
            for sub in normalized:
                start = sub["start_seconds"]
                end = sub.get("end_seconds")
                if parent_start is not None and start < parent_start:
                    raise ValueError(f"subchapter {idx} starts before parent")
                if parent_end is not None and start >= parent_end:
                    raise ValueError(f"subchapter {idx} starts outside parent")
                if end is not None:
                    if end < start:
                        raise ValueError(f"subchapter {idx} ends before it starts")
                    if parent_end is not None and end > parent_end:
                        raise ValueError(f"subchapter {idx} ends outside parent")
                if previous_start is not None and start < previous_start:
                    raise ValueError(f"subchapters for parent {idx} are not chronological")
                previous_start = start
            chapter["subchapters"] = normalized
    return out


def build_navigation_structure(
    source_chapters: Any,
    *,
    semantic_chapters_if_missing: Any = None,
) -> dict[str, Any]:
    """Choose source navigation when available, otherwise semantic fallback.

    This function does not generate semantic chapters.  It only provides the
    routing contract for a later AI stage: source chapters win when supplied;
    transcript-derived semantic chapters may be used only when source chapters
    are absent.
    """

    source = normalize_source_chapters(source_chapters)
    if source:
        return {"basis": "source_chapters", "chapters": source}
    semantic = _normalize_subchapters(semantic_chapters_if_missing)
    return {"basis": "semantic_transcript_fallback", "chapters": semantic}
