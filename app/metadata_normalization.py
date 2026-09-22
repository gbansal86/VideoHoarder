"""Canonical metadata normalization for VideoHoarder.

Phase 2 introduces a pure, side-effect-free normalization boundary between raw
extractor metadata (primarily yt-dlp) and VideoHoarder's canonical metadata
model.  It deliberately does *not* persist data or change download behavior;
Phase 3 will wire this layer into future-download persistence.

The normalizer keeps five concerns distinct:
- llm_core: source identity/context allowed in transcript-intelligence packages
- llm_auxiliary: source chapters/tags for navigation/search only
- local_only: useful library metadata that must not become transcript evidence
- derived: values that can be recreated from canonical values
- temporary_technical: names of raw technical fields that must not be copied
  into canonical metadata/LLM payloads

No source chapters, source tags, description, comments, popularity metrics, or
technical download fields are semantic transcript evidence.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urlparse

try:
    from .source_chapters import normalize_source_chapters
    from .source_tags import clean_source_tags
except ImportError:  # pragma: no cover - direct script compatibility
    from source_chapters import normalize_source_chapters
    from source_tags import clean_source_tags

CANONICAL_METADATA_SCHEMA_VERSION = 1

# Technical/extractor fields may be used transiently by yt-dlp, but should not
# be copied into canonical metadata or transcript-intelligence packages.
TEMPORARY_TECHNICAL_FIELDS = frozenset({
    "_format_sort_fields", "_version", "_type", "acodec", "age_limit", "asr",
    "audio_channels", "dynamic_range", "epoch", "formats", "playable_in_embed",
    "protocol", "uploader_url", "vcodec", "width", "height", "n_entries", "abr",
    "extractor_key", "media_type", "aspect_ratio", "ext", "extractor", "format",
    "format_id", "format_note", "fps", "tbr", "vbr",
})

LOCAL_ONLY_RAW_FIELDS = (
    "description", "channel_id", "channel_url", "uploader_id",
    "channel_follower_count", "channel_is_verified", "heatmap", "thumbnail",
    "playlist", "playlist_id", "playlist_title", "playlist_index", "playlist_count",
    "playlist_channel", "playlist_channel_id", "playlist_uploader",
    "playlist_uploader_id", "playlist_webpage_url", "language", "is_live",
    "was_live", "live_status", "filesize_approx", "view_count", "like_count",
    "comment_count",
)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _first_nonempty(*values: Any) -> str:
    for value in values:
        text = _text(value)
        if text:
            return text
    return ""


def _int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _bool_or_none(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    return None


def _list_of_text(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        values: Sequence[Any] = [value]
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        values = value
    else:
        return []
    result: list[str] = []
    seen: set[str] = set()
    for item in values:
        text = _text(item)
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(text)
    return result


def _canonical_category(raw: Mapping[str, Any]) -> str:
    # Approved storage decision: youtube_category_name is the canonical DB field.
    explicit = _first_nonempty(raw.get("youtube_category_name"), raw.get("source_category"))
    if explicit:
        return explicit
    categories = raw.get("categories") or raw.get("source_categories") or []
    if isinstance(categories, str):
        return categories.strip()
    if isinstance(categories, Sequence):
        for item in categories:
            text = _text(item)
            if text:
                return text
    return ""


def _canonical_url(raw: Mapping[str, Any], fallback: Mapping[str, Any]) -> str:
    return _first_nonempty(raw.get("webpage_url"), raw.get("url"), fallback.get("webpage_url"), fallback.get("url"))


def normalize_extractor_metadata(
    raw: Mapping[str, Any] | None,
    *,
    fallback: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return canonical metadata categories from one raw extractor record.

    This function is pure: it performs no I/O, persistence, network access, or
    transcript analysis.  Unknown raw fields are ignored rather than copied.
    """

    raw = raw or {}
    fallback = fallback or {}
    if not isinstance(raw, Mapping):
        raise TypeError("raw metadata must be a mapping")
    if not isinstance(fallback, Mapping):
        raise TypeError("fallback metadata must be a mapping")

    categories = _list_of_text(raw.get("categories") or raw.get("source_categories"))
    category = _canonical_category(raw)
    if category and not categories:
        categories = [category]

    url = _canonical_url(raw, fallback)
    video_id = _first_nonempty(raw.get("id"), fallback.get("id"))
    title = _first_nonempty(raw.get("title"), fallback.get("title"), video_id)
    channel = _first_nonempty(raw.get("channel"), raw.get("uploader"), fallback.get("channel"), fallback.get("uploader"))
    upload_date = _first_nonempty(raw.get("upload_date"), fallback.get("upload_date"))
    duration = _float_or_none(raw.get("duration", raw.get("duration_seconds")))
    availability = _text(raw.get("availability"))

    source_tag_result = clean_source_tags(raw.get("tags") if raw.get("tags") is not None else raw.get("youtube_tags"))
    source_tags = source_tag_result["raw"]
    source_tags_cleaned = source_tag_result["cleaned"]
    source_chapters = normalize_source_chapters(raw.get("chapters") or raw.get("source_chapters"))

    llm_core = {
        "id": video_id,
        "original_title": title,
        "channel": channel,
        "upload_date": upload_date,
        "duration_seconds": duration,
        "webpage_url": url,
        "availability": availability,
        "category": category,
    }
    llm_auxiliary = {
        "source_chapters": source_chapters,
        "source_tags_raw": source_tags,
        "source_tags_cleaned": source_tags_cleaned,
    }

    local_only: dict[str, Any] = {
        "description": _text(raw.get("description")),
        "channel_id": _text(raw.get("channel_id")),
        "channel_url": _text(raw.get("channel_url")),
        "uploader_id": _text(raw.get("uploader_id")),
        "channel_follower_count": _int_or_none(raw.get("channel_follower_count")),
        "channel_is_verified": _bool_or_none(raw.get("channel_is_verified")),
        "heatmap": raw.get("heatmap") if isinstance(raw.get("heatmap"), list) else [],
        "thumbnail": _text(raw.get("thumbnail") or raw.get("thumbnail_url")),
        "playlist": _text(raw.get("playlist")),
        "playlist_id": _text(raw.get("playlist_id")),
        "playlist_title": _text(raw.get("playlist_title")),
        "playlist_index": _int_or_none(raw.get("playlist_index")),
        "playlist_count": _int_or_none(raw.get("playlist_count")),
        "playlist_channel": _text(raw.get("playlist_channel")),
        "playlist_channel_id": _text(raw.get("playlist_channel_id")),
        "playlist_uploader": _text(raw.get("playlist_uploader")),
        "playlist_uploader_id": _text(raw.get("playlist_uploader_id")),
        "playlist_webpage_url": _text(raw.get("playlist_webpage_url")),
        "language": _text(raw.get("language")),
        "is_live": _bool_or_none(raw.get("is_live")),
        "was_live": _bool_or_none(raw.get("was_live")),
        "live_status": _text(raw.get("live_status")),
        "filesize_approx": _int_or_none(raw.get("filesize_approx")),
        "view_count": _int_or_none(raw.get("view_count")),
        "like_count": _int_or_none(raw.get("like_count")),
        "comment_count": _int_or_none(raw.get("comment_count")),
        "categories": categories,
        "youtube_category_id": _text(raw.get("youtube_category_id") or raw.get("source_category_id")),
        "source_tags_removed": source_tag_result["removed"],
    }

    parsed = urlparse(url) if url else None
    derived = {
        "duration_string": "",  # presentation layer can derive from duration_seconds
        "webpage_url_domain": parsed.netloc.lower() if parsed else "",
        "webpage_url_basename": parsed.path.rsplit("/", 1)[-1] if parsed and parsed.path else "",
    }

    present_technical = sorted(field for field in TEMPORARY_TECHNICAL_FIELDS if field in raw)

    return {
        "metadata_schema_version": CANONICAL_METADATA_SCHEMA_VERSION,
        "llm_core": llm_core,
        "llm_auxiliary": llm_auxiliary,
        "local_only": local_only,
        "derived": derived,
        "temporary_technical_fields_present": present_technical,
    }


def flattened_persistence_view(normalized: Mapping[str, Any]) -> dict[str, Any]:
    """Map canonical normalized values to existing Phase-1 database columns.

    This helper is intentionally side-effect free.  Phase 3 may use it when it
    wires persistence into future downloads.
    """

    core = normalized.get("llm_core") or {}
    aux = normalized.get("llm_auxiliary") or {}
    local = normalized.get("local_only") or {}
    return {
        "availability": core.get("availability") or "",
        "duration_seconds": core.get("duration_seconds"),
        "source_chapters": aux.get("source_chapters") or [],
        "youtube_tags": aux.get("source_tags_raw") or [],
        "youtube_tags_cleaned": aux.get("source_tags_cleaned") or [],
        "youtube_category_name": core.get("category") or "",
        "channel_id": local.get("channel_id") or "",
        "channel_url": local.get("channel_url") or "",
        "uploader_id": local.get("uploader_id") or "",
        "channel_follower_count": local.get("channel_follower_count"),
        "channel_is_verified": local.get("channel_is_verified"),
        "heatmap": local.get("heatmap") or [],
        "playlist": local.get("playlist") or "",
        "playlist_id": local.get("playlist_id") or "",
        "playlist_title": local.get("playlist_title") or "",
        "playlist_index": local.get("playlist_index"),
        "playlist_count": local.get("playlist_count"),
        "playlist_channel": local.get("playlist_channel") or "",
        "playlist_channel_id": local.get("playlist_channel_id") or "",
        "playlist_uploader": local.get("playlist_uploader") or "",
        "playlist_uploader_id": local.get("playlist_uploader_id") or "",
        "playlist_webpage_url": local.get("playlist_webpage_url") or "",
        "language": local.get("language") or "",
        "is_live": local.get("is_live"),
        "was_live": local.get("was_live"),
        "live_status": local.get("live_status") or "",
        "filesize_approx": local.get("filesize_approx"),
        "thumbnail_url": local.get("thumbnail") or "",
        "view_count": local.get("view_count"),
        "like_count": local.get("like_count"),
        "comment_count": local.get("comment_count"),
        "metadata_schema_version": normalized.get("metadata_schema_version") or 0,
    }
