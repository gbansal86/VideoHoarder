# VideoHoarder Implementation Changelog

## 2026-08-15

- Created `specs/future_requests/` as the authoritative location for proposed work.
- Moved the prior general pending-updates backlog into the dated `2026-08-14_Pending_Updates_Backlog.md` file.
- Added the dated Central Artifact Manifest specification, including automatic command updates, artifact and ChatGPT-package lifecycle tracking, staleness detection, exports, change history and the complete manual checkbox behavior.
- Added a future-request index and updated status/checkpoint references. No application code or EXE was changed.
- Added a standalone colorful HTML Future Request Editor with document navigation, content editing, browser-local autosave, accent themes, reset, print, HTML export and text export. No application code or EXE was changed.
- Added five persistent background themes to the Future Request Editor: midnight navy, charcoal, forest, deep plum and warm brown. Accent and background colors can be selected independently.

## 2026-08-14

- Added the original pending-updates backlog (later moved into `specs/future_requests/` with its original date preserved).
- Recorded the six remaining improvement areas and added copy-paste prompts for implementing all items, selected items, recording a new idea without coding, and refining an idea before implementation.
- Linked the pending-updates record from the current feature-status document.

## 2026-08-13

- Added the current feature-status record by application tab.
- Recorded implemented versus pending ChatGPT Processing and Group Similar Videos behavior.
- Recorded requested package batch-number deletion filtering and dashboard refresh as pending.
- Established the rule to update the status record and this changelog after every implementation turn.
- Backup retention target: keep the four newest app backups.
- Added Design 1 source UI pass: grouped Advanced navigation, current-work status card, status badges, structured history/coverage table rendering, and native styling overrides.
- Source compilation passed; Windows EXE rebuild/install remains pending for this pass.
- Added package deletion filtering by batch/package text and refresh of overview/history after deletion; source compilation passed.
- Built and installed `D:\YT GUi\VideoHoarder.exe`; startup and `/chatgpt-processing` HTTP verification passed. Added visible scope selectors and coverage-status filter controls. Selector data population and advanced review actions remain pending.
- Added selector backend source pass: `/api/chatgpt-processing/selectors` returns local folders, categories, topics and channels; package creation applies selected folder/topic/category filters. Source compilation passed; EXE rebuild remains pending.
- Added collection selector data from the existing Phase 6 collection store; selecting a collection scopes package creation to its VIDEO_IDs. Testing passed: 7 automated tests and live selectors/overview/page HTTP checks.
- Fixed packaging timeout by running PyInstaller as a background monitored process; build completed, installed EXE launched, and ChatGPT Processing returned HTTP 200 with collection selector UI.
- Testing pass: automated suite 7 tests passed (3 GUI tests skipped in system Python); live HTTP checks passed for overview, history, coverage, selectors, ChatGPT Processing page, and planner preview. No destructive package/import test was run.
- Completed strict ChatGPT package validation: stored manifest checksum, per-file SHA-256 checks, safe evidence paths, package identity, timestamp/duration checks and evidence-presence provenance validation.
- Added field-level review cards with individual approval checkboxes and audited staging for metadata, taxonomy, rename, folder move, duplicate, clip-plan and report-refresh actions.
- Added duplicate-group preview, canonical selection and Keep/Archive/Mark Delete review records. These controls never delete files automatically.
- Added clip-plan VIDEO_ID/timestamp/duration validation, structured inclusion/order preview and reviewed manual Clip Studio handoff. No automatic cut or merge.
- Completed the Group Similar Videos import/validate/create-grouped-packages UI and applied package-integrity validation to planner imports.
- Added end-to-end workflow tests. Result in the PySide6 build environment: 14/14 tests passed with no skips.
- Built release v33, installed `D:\YT GUi\VideoHoarder.exe` (218,124,389 bytes), launched it, and verified ChatGPT Processing plus selector endpoints returned HTTP 200 with every requested UI marker present. Duplicate-launch probe exited after the single-instance guard check.
