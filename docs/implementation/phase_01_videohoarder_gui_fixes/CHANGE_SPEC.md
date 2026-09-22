# Phase 01 Change Specification

## Objective
Repair the Codex-added GUI/download/failure features without adding more feature logic to the monolithic `app.py`.

## Requirements
- REQ-002 resolve embedded URLs before, not instead of, normal download.
- REQ-003 plugin-based resolver design.
- REQ-004 enable browser-cookie access and robust YouTube 403 cookie retry.
- REQ-005 queue presentation: video/file name only in Name, thumbnail, separate Type, per-URL jobs, done/left summary.
- REQ-006 Library newest/oldest sorting uses current downloaded state.
- REQ-007 selective cleanup removes the current failure and its count.
- REQ-008 current Failure/Cleanup view retrieves current failures without an arbitrary default 500-row cap.
- REQ-009 Needs attention opens Failure/Cleanup.
- REQ-010 Open downloader visibly focuses the download composer.

## Risks and controls
- Existing download behavior: compatibility wrappers retain previous backend call signatures.
- Resolver loops/host churn: bounded depth/page count and deduplication.
- Cookie regressions: existing cookie args are never duplicated; fallback only adds browser cookies when missing.
- Stale index vs DB: search index retained, mutable fields overlaid from SQLite.
- Historical diagnostics: archives/run logs are retained; only current failure sources are cleaned.
