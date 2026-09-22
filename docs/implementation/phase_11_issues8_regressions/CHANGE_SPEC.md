# Phase 11 — Issues 8 Regression Repair

## Scope
Repair the five user-reported regressions in `Issues 8.docx` plus the Code Parent wrapper inconsistency found in the supplied Code Parent (7).

## Requirements
- FIX-111: provide a smaller-EXE build option without changing the normal one-file release.
- FIX-112: `Refresh all figures` must be a visible managed Queue job.
- FIX-113: physical deletion of a previously downloaded managed-library video must remove its normal DB/cache/index references and leave only the minimal redownload guard.
- FIX-114: managed Media/Audio download progress must update the selected job rather than remain at 0% while the file is downloading/completed.
- FIX-115: Job Details must be explicitly discoverable from the Queue page even on narrow layouts.
- FIX-116: Code Parent wrapper must be portable and report the actual ZIP artifact.

## Design
- Preserve the existing one-file build; add a separate onedir Small-EXE build.
- Queue dashboard refresh through `web_start_job` instead of a private `FunctionTask`.
- Extend physical-library reconciliation to purge missing previously downloaded managed-library rows with `purge_video_everywhere`, preserving only `deleted_video_guard_history.json`.
- Propagate downloader transfer percentages into the current managed job and add batch progress calls to Media Only.
- Add a dedicated Job Details dialog/button while retaining the right-side details panel.
- Remove hard-coded D-drive values from the Code Parent wrapper.
