# Phase 03 Change Specification — Issues 3

Change size: MEDIUM

## Requirements
- REQ-018: Library thumbnail is larger.
- REQ-019: Library sort options include Video, Channel, and Category.
- REQ-020: Failure/Cleanup and Dashboard use one complete current-failure register covering video/CSV failures and failed queue jobs.
- REQ-021: Every visible current failure can be deleted/dismissed, including CSV failures without VIDEO_ID and failed queue jobs.
- REQ-022: Delete is immediately visible next to the failure entry.
- REQ-023: Restore a real Downloads navigation tab exposing the existing Full Library Download and Media Only / Entertainment screen.
- ARCH-003: New failure aggregation/cleanup logic remains outside app.py except thin compatibility wrappers.

## Baseline
Source baseline: `VideoHoarder_Code_Parent_Fixed_Modular_v4_Issues2.zip`.

## Design
- Extend `library_browser_service.py` for category sorting and enlarge native Library thumbnail presentation.
- Add `current_failure_registry.py` to normalize video/CSV and queue-job failures into one current registry.
- Enhance `failure_service.py` with stable CSV failure keys so unknown/no-VIDEO_ID rows can be deleted safely.
- Move terminal failed-job run logs to `logs/runs/archive/` when dismissed rather than deleting diagnostic evidence.
- Add a first-class native sidebar `Downloads` route to the existing `/app?tab=downloads` implementation. The Workflows `Open downloader` action routes there directly.

## Acceptance criteria
- Library offers Video A-Z, Channel A-Z, Category A-Z plus date sorts.
- Library thumbnail is 120x68 with taller rows.
- Dashboard failure count equals the number of rows returned by the unified current-failure register.
- Failure page shows video/CSV failures and failed queue jobs, excluding ordinary user-cancelled jobs.
- Unknown CSV failures can be deleted without requiring VIDEO_ID.
- Failed queue jobs can be deleted/dismissed and their run log is archived.
- Delete button is the second column next to Failure.
- Downloads is visible in the sidebar and `Open downloader` routes to it.
