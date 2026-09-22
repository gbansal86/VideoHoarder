"""Compatibility wrapper for older imports.

New code should import from ``current_status_service``.
"""

from __future__ import annotations

try:  # pragma: no cover - package import
    from .current_status_service import download_status_payload, failure_reason_bucket, failure_summary
except ImportError:  # pragma: no cover - direct script compatibility
    from current_status_service import download_status_payload, failure_reason_bucket, failure_summary

__all__ = ["download_status_payload", "failure_reason_bucket", "failure_summary"]
