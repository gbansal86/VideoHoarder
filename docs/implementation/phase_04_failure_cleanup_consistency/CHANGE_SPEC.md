# Phase 04 Change Spec — Failure Cleanup Consistency

## Classification

MEDIUM. The change affects user-facing failure counts, failure listing, selective cleanup, native dashboard status, and the web Failure page.

## Requirements

- FIX-041: Failure count must match the current Failure / Cleanup list.
- FIX-042: All current unresolved failures must be shown, including video failures, CSV failures without VIDEO_ID, and failed queue jobs.
- FIX-043: A Delete action must be available next to each failure.
- FIX-044: Failures without VIDEO_ID and failed queue jobs must be deletable by stable failure key.
- ARCH-045: New feature logic should live outside app.py where practical.

## Root Cause

VideoHoarder had both `web_download_failure_rows()` and `web_current_failure_rows()`. Some UI paths used the older video/CSV-only function while the native Failure page used the newer unified register. The web status endpoint also overwrote the correct library stat count with the older video-only count.

## Design

- Keep durable video/CSV failure collection in `app/failure_service.py`.
- Keep queue-job merge/delete logic in `app/current_failure_registry.py`.
- Add `app/failure_status_service.py` for user-facing summary/status formatting.
- Keep `app.py` as a thin wrapper/API layer.

## Acceptance Criteria

- `/api/download-status` returns unified current failures.
- Failure Summary count equals returned failure rows length.
- Native dashboard count uses unified current failure rows.
- Web status table shows Delete next to each row.
- Delete can use `failure_key`, not only `video_id`.
