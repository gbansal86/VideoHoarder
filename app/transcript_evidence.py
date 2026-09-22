"""Transcript-evidence grading and normal-package routing.

Phase 5 establishes one canonical A/B/C/D/F vocabulary.  The grading is
mechanical and transcript-derived: metadata, comments, source tags, source
chapters, and clean/display titles must not affect transcript evidence grade.
"""

from __future__ import annotations

from typing import Any, Mapping

EVIDENCE_GRADES = ("A", "B", "C", "D", "F")
NORMAL_PACKAGE_ELIGIBLE_GRADES = frozenset({"A", "B", "C"})
REPAIR_GRADES = frozenset({"D", "F"})
LEGACY_EVIDENCE_GRADE_MAP = {"E": "F"}


def normalize_evidence_grade(value: Any, *, allow_legacy: bool = True) -> str:
    """Return canonical A/B/C/D/F evidence grade.

    Old persisted/results payloads may contain legacy ``E``.  Accepting and
    normalizing it to ``F`` preserves backward compatibility while preventing
    new contracts from emitting E.
    """
    grade = str(value or "F").strip().upper()
    if allow_legacy:
        grade = LEGACY_EVIDENCE_GRADE_MAP.get(grade, grade)
    return grade if grade in EVIDENCE_GRADES else "F"


def evidence_grade_from_transcript_health(
    health: Mapping[str, Any] | None,
    *,
    transcript_available: bool,
) -> str:
    """Derive evidence grade only from canonical transcript health/availability."""
    if not transcript_available:
        return "F"
    return normalize_evidence_grade((health or {}).get("grade"), allow_legacy=True)


def normal_transcript_package_eligible(grade: Any) -> bool:
    """Whether a canonical evidence grade can enter normal transcript intelligence."""
    return normalize_evidence_grade(grade, allow_legacy=True) in NORMAL_PACKAGE_ELIGIBLE_GRADES


def repair_routing_for_grade(grade: Any) -> str:
    """Stable routing label for diagnostics/repair queues."""
    canonical = normalize_evidence_grade(grade, allow_legacy=True)
    if canonical == "D":
        return "REPAIR_RECOMMENDED"
    if canonical == "F":
        return "REPAIR_REQUIRED"
    if canonical == "C":
        return "CAUTION"
    return "NORMAL"
