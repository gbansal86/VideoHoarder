# Phase 01 Change Spec — Issue 6 Completion

## Requirements
- FIX-601: readable Job Details layout.
- REQ-602: explicit confirmation before duplicate/re-download.
- FIX-603: immediate library-count refresh after successful download.
- REQ-604: queue horizontal + vertical scrolling and Refresh queue.
- ARCH-605: Queue page distinct from Dashboard.
- FIX-606: queued rows explain why they wait.
- FIX-607: Refresh all figures reflects physical deletion.
- FIX-609: restore missing integrity fixture.
- DOC-608: restore governance evidence.

## Design
New feature logic is modular: `download_guard_service.py`, `library_stats_service.py`, and `native_queue_page.py`. `app.py` remains compatibility/backend wiring and is smaller than baseline.

## Risks
- Native PySide6 behavior cannot be executed in this Linux environment.
- Duplicate confirmation for non-YouTube hosts relies on current queue URL matching; library-history ID matching is strongest for YouTube IDs.
- Full physical-library scans can be expensive; terminal-triggered stats refresh is bounded by one refresh per newer terminal timestamp.

## Acceptance criteria
See TEST_PLAN.md and TRACEABILITY_MATRIX.md.
