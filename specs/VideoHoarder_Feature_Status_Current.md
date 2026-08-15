# VideoHoarder Feature Status

Last updated: 2026-08-13 (ChatGPT Processing verification pass)

This is the working implementation record for the installed VideoHoarder build. Update this file whenever a feature is implemented, changed, or verified.

## Dashboard

- Implemented: local desktop shell, dashboard navigation, single-instance startup, local server health.
- Implemented in source: compact Design 1 current-work dashboard, status badge, live command/phase/current/progress display, and native styling overrides.
- Installed build verified: the EXE serves ChatGPT Processing over HTTP 200.

## Downloads / Queue

- Implemented: download workflows, queue visibility, job status APIs, stop/cancel paths.
- Pending: ensure every command has the same live progress presentation in the native shell.

## Library

- Implemented: search/library routes, metadata, reports, collections, transcript/comment tools.
- Pending: final tab-specific status cards and complete repair/import visual workflow.

## Old Library Import & Repair

- Implemented: selectable source folders, legacy scan/repair jobs, transcript/SRT/VTT reuse, metadata/category repair options, progress state and resumable job infrastructure.
- Pending: finish performance hardening and complete per-file progress presentation for every repair action.

## ChatGPT Processing

- Implemented: manual-only exchange, local packages, request history storage, feature coverage storage, import/validation, review preview, audit trail, package modes, multiple JSON import, unprocessed-package deletion, planner placement after Overview, category/keyword skip controls, one small similarity-planner package, 25-video transcript and 50-video no-transcript planning rules.
- Implemented in source: Design 1 visual pass, grouped Advanced navigation label, current-work panel, and structured Request History/Feature Coverage tables.
- Implemented in source: unprocessed-package filter by package ID/batch text, filtered deletion selection, and dashboard/history refresh after deletion.
- Implemented in source: dynamic selector API for local folders, categories, topics and channels; Create Package sends selected folder/topic/category values and filters eligible videos.
- Implemented in source: collection selector data from Phase 6 collections and collection-scoped package creation.
- Installed build verified at 2026-08-13 20:06 with collection selector UI and backend.
- Implemented and tested in source: strict manifest/package and evidence-file SHA-256 validation, safe manifest paths, manifest/package identity checks, timestamp validation against video duration with transcript-duration fallback, and provenance checks against evidence actually present for each VIDEO_ID.
- Implemented and tested in source: field-level Review & Apply cards, individual approval checkboxes, and reviewed staging actions for metadata, taxonomy, rename preview, folder-move preview, duplicates, clip plans and report refresh. Decisions are audited; physical file changes remain manual.
- Installed build verified at 2026-08-13 20:38: final EXE contains the strict validation, field-review, duplicate, clip and complete planner workflows.

## Group Similar Videos

- Implemented: appears immediately after Overview and before Create Package; creates one small planner package; app remains authority for transcript availability; optional Entertainment and keyword exclusions.
- Implemented and tested: returned-plan file selector, strict package-integrity validation, transcript/no-transcript group validation, visible result summary, and explicit creation of grouped 25-video transcript / 50-video no-transcript packages.

## Intelligence / Knowledge Center

- Implemented: existing reports, search, transcript/comment intelligence and local AI integration remain available.
- Pending: complete projection of normalized ChatGPT intelligence into every report/search/Knowledge Center view.

## Duplicates / Clip Studio / Organization

- Implemented and tested: duplicate-group JSON preview, canonical selection, per-video Keep/Archive/Mark Delete choices, immutable review records and manual Duplicate Audit route. No deletion is automatic.
- Implemented and tested: clip VIDEO_ID, start/end, order and duration validation; inclusion/order preview; saved reviewed handoff to the existing Clip Studio route. No cutting or merging is automatic.

## Maintenance / Backups

- Implemented: backup directory exists and is limited to the four newest backups as of this update.
- Pending: automated four-backup retention check in the maintenance workflow.

## Safety guarantees

- No automatic ChatGPT upload.
- No automatic rename, move, delete, cut, merge, or media download from ChatGPT suggestions.
- Imported results require validation/review before application.

## Latest test result

- Automated suite in the PySide6 build environment: 14/14 passed with no skips.
- Coverage includes backend startup, configuration, native navigation, integrity tamper detection, provenance availability, timestamp parsing, planner import/group rules, duplicate canonical review and clip-plan validation/manual handoff.
- Destructive moves/deletes/cuts were intentionally not executed; those operations remain reviewed and manual by design.
- Installed runtime: ChatGPT Processing and selectors returned HTTP 200; all required final UI markers were present. A duplicate-launch probe exited and left the original one-file parent/child instance pair intact.

## Update rule

Every future implementation turn must update this file and append a dated entry to `VideoHoarder_Implementation_Changelog.md` before reporting completion.

## Pending-updates record

The authoritative backlog and date-prefixed specifications are maintained under `future_requests/`. See `future_requests/README.md` for the index.
