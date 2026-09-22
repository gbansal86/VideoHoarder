"""Source/YouTube tag handling for VideoHoarder.

Source tags are search/indexing hints only.  They are never transcript evidence.
Phase 4 performs deliberately conservative deterministic cleanup: obvious
promotional/clickbait/spam tags are removed, while legitimate topic, product,
entity and creator terms are preserved.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

# High-confidence promotional/junk phrases only.  Avoid broad words such as
# "best", "free", "health", "review" or product names because those can be
# legitimate search tags.
_PROMOTIONAL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("subscribe_prompt", re.compile(r"\b(?:please\s+)?subscribe(?:\s+(?:now|today|to\s+(?:my|our)\s+channel))?\b", re.I)),
    ("engagement_bait", re.compile(r"\b(?:like\s*(?:and|&)\s*share|like\s+share\s+subscribe|smash\s+the\s+like|hit\s+the\s+bell)\b", re.I)),
    ("affiliate", re.compile(r"\b(?:affiliate\s+link|affiliate\s+links|amazon\s+affiliate)\b", re.I)),
    ("coupon", re.compile(r"\b(?:coupon\s+code|promo\s+code|use\s+code|discount\s+code)\b", re.I)),
    ("purchase_bait", re.compile(r"\b(?:buy\s+now|shop\s+now|click\s+(?:the\s+)?link|link\s+in\s+(?:bio|description))\b", re.I)),
    ("sponsorship", re.compile(r"\b(?:sponsored\s+video|paid\s+promotion)\b", re.I)),
)

_WHITESPACE = re.compile(r"\s+")


def normalize_source_tag(value: Any) -> str:
    """Normalize presentation whitespace without semantically rewriting a tag."""

    text = str(value or "").strip()
    if not text:
        return ""
    # A leading hashtag is presentation syntax, not part of the searchable term.
    text = text.lstrip("#").strip()
    return _WHITESPACE.sub(" ", text)


def junk_reason(tag: str) -> str:
    """Return a high-confidence junk reason, or an empty string when preserved."""

    normalized = normalize_source_tag(tag)
    if not normalized:
        return "empty"
    # URLs are not useful source tags and commonly encode promotional links.
    lowered = normalized.casefold()
    if lowered.startswith(("http://", "https://", "www.")):
        return "url"
    for reason, pattern in _PROMOTIONAL_PATTERNS:
        if pattern.search(normalized):
            return reason
    return ""


def clean_source_tags(values: Any) -> dict[str, list[Any]]:
    """Conservatively clean source tags while preserving an audit trail.

    Returns ``raw``, ``cleaned`` and ``removed``.  ``removed`` contains the
    original normalized tag plus the deterministic reason.  Duplicate tags are
    deduplicated case-insensitively but are not classified as promotional junk.
    """

    if values is None:
        items: Sequence[Any] = []
    elif isinstance(values, str):
        items = [values]
    elif isinstance(values, Sequence) and not isinstance(values, (bytes, bytearray)):
        items = values
    else:
        items = []

    raw: list[str] = []
    cleaned: list[str] = []
    removed: list[dict[str, str]] = []
    seen_raw: set[str] = set()
    seen_clean: set[str] = set()

    for value in items:
        tag = normalize_source_tag(value)
        if not tag:
            continue
        key = tag.casefold()
        if key not in seen_raw:
            raw.append(tag)
            seen_raw.add(key)
        reason = junk_reason(tag)
        if reason:
            removed.append({"tag": tag, "reason": reason})
            continue
        if key in seen_clean:
            continue
        cleaned.append(tag)
        seen_clean.add(key)

    return {"raw": raw, "cleaned": cleaned, "removed": removed}
