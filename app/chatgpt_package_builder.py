"""Strict ChatGPT transcript-intelligence package contract.

Phase 6 makes the outgoing per-video payload allow-list driven.  Local metadata
may remain rich in SQLite/.info.json, but only approved identity/context,
auxiliary navigation/search metadata, transcript provenance and canonical
transcript evidence can cross the normal transcript-package boundary.
"""
from __future__ import annotations

import json
from typing import Any, Mapping

VIDEO_METADATA_KEYS = (
    "id",
    "original_title",
    "clean_title",
    "channel",
    "upload_date",
    "duration_seconds",
    "webpage_url",
    "availability",
    "category",
)
AUXILIARY_KEYS = ("source_chapters", "source_tags")
FORBIDDEN_PACKAGE_KEYS = frozenset({
    "description",
    "comments",
    "formats",
    "automatic_captions",
    "subtitles",
    "heatmap",
    "view_count",
    "like_count",
    "comment_count",
    "channel_follower_count",
    "channel_is_verified",
    "filesize_approx",
    "source_category",
    "youtube_category_name",
    "youtube_tags",
    "youtube_tags_cleaned",
})


def _json_value(value: Any, default: Any) -> Any:
    if value in (None, ""):
        return default
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(str(value))
    except Exception:
        return default


def build_metadata(row: Mapping[str, Any]) -> dict[str, Any]:
    """Build approved identity/operational metadata only.

    ``clean_title`` is intentionally retained for operational/title workflows,
    but Phase 5 guarantees it is not transcript evidence.
    """
    return {
        "id": str(row.get("video_id") or ""),
        "original_title": str(row.get("original_title") or ""),
        "clean_title": str(row.get("clean_title") or ""),
        "channel": str(row.get("channel") or ""),
        "upload_date": str(row.get("upload_date") or ""),
        "duration_seconds": float(row.get("duration_seconds") or 0),
        "webpage_url": str(row.get("url") or ""),
        "availability": str(row.get("availability") or ""),
        "category": str(row.get("youtube_category_name") or ""),
    }


def build_auxiliary_metadata(row: Mapping[str, Any]) -> dict[str, Any]:
    chapters = _json_value(row.get("source_chapters_json"), [])
    tags = _json_value(row.get("youtube_tags_cleaned"), [])
    if not isinstance(chapters, list):
        chapters = []
    if not isinstance(tags, list):
        tags = []
    return {
        "source_chapters": chapters,
        "source_tags": [str(x) for x in tags if str(x).strip()],
    }


def build_transcript_provenance(row: Mapping[str, Any], assessment: Mapping[str, Any], language: str) -> dict[str, Any]:
    health = dict(assessment.get("transcript_health") or {})
    return {
        "source": str(assessment.get("transcript_source") or row.get("transcript_source") or row.get("subtitle_source") or ""),
        "language": str(language or row.get("subtitle_lang") or "unknown"),
        "base_language": str(row.get("subtitle_base_lang") or ""),
        "availability": "AVAILABLE" if bool(assessment.get("transcript_available")) else "UNAVAILABLE",
        "timestamps_available": bool(assessment.get("timestamps_available")),
        "timestamp_status": str(assessment.get("timestamp_status") or ""),
        "health": health,
    }


def build_evidence(assessment: Mapping[str, Any], artifact_manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Build transcript evidence without comments/description/local metadata."""
    manifest = {
        "metadata": True,
        "transcript": bool(assessment.get("transcript_available")),
        "canonical_segment_count": int(assessment.get("canonical_segment_count") or 0),
        "evidence_grade": str(assessment.get("evidence_grade") or "F"),
    }
    # Keep the transcript-derived assessment because downstream quality logic and
    # result validation currently consume it.  Phase 5 already removed metadata/
    # comments influence from the grading fields inside this assessment.
    safe_assessment = {
        k: v for k, v in dict(assessment or {}).items()
        if k not in {"comments", "comments_available", "description_available", "metadata_available"}
    }
    return {
        "canonical_transcript": dict(assessment.get("canonical_transcript") or {}),
        "manifest": manifest,
        "assessment": safe_assessment,
    }


def build_video_payload(
    row: Mapping[str, Any],
    *,
    assessment: Mapping[str, Any],
    artifact_manifest: Mapping[str, Any],
    transcript_language: str,
    requested_features: list[str],
) -> dict[str, Any]:
    grade = str(assessment.get("evidence_grade") or "F")
    return {
        "video_id": str(row.get("video_id") or ""),
        "package_grade": grade,
        "metadata": build_metadata(row),
        "auxiliary_metadata": build_auxiliary_metadata(row),
        "transcript_provenance": build_transcript_provenance(row, assessment, transcript_language),
        "requested_features": list(requested_features or []),
        "evidence": build_evidence(assessment, artifact_manifest),
    }


def assert_strict_package_contract(video_payload: Mapping[str, Any]) -> None:
    """Raise ValueError if forbidden/local-only material crosses the boundary."""
    top_allowed = {
        "video_id", "package_grade", "metadata", "auxiliary_metadata",
        "transcript_provenance", "requested_features", "evidence",
    }
    unexpected = set(video_payload) - top_allowed
    if unexpected:
        raise ValueError(f"Unexpected top-level package fields: {sorted(unexpected)}")
    metadata = video_payload.get("metadata") or {}
    if set(metadata) != set(VIDEO_METADATA_KEYS):
        raise ValueError(f"Metadata allow-list mismatch: {sorted(set(metadata))}")
    aux = video_payload.get("auxiliary_metadata") or {}
    if set(aux) != set(AUXILIARY_KEYS):
        raise ValueError(f"Auxiliary allow-list mismatch: {sorted(set(aux))}")
    evidence = video_payload.get("evidence") or {}
    if "comments" in evidence:
        raise ValueError("Comments are forbidden in normal transcript-intelligence evidence")
    def _walk_keys(value: Any):
        if isinstance(value, Mapping):
            for key, child in value.items():
                yield str(key)
                yield from _walk_keys(child)
        elif isinstance(value, list):
            for child in value:
                yield from _walk_keys(child)
    keys={k.lower() for k in _walk_keys(video_payload)}
    leaked=sorted(key for key in FORBIDDEN_PACKAGE_KEYS if key.lower() in keys)
    if leaked:
        raise ValueError(f"Forbidden package key leaked: {leaked}")
