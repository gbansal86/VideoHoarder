# Future Request — Central Artifact Manifest System

Recorded: 2026-08-15
Status: Proposed; not implemented

## Suitable future implementation request

> Implement a central VideoHoarder Artifact Manifest system as the authoritative inventory, completeness record and change history for every `VIDEO_ID`.
>
> Existing commands must consult the manifest first instead of repeatedly scanning every folder. Commands must update only affected manifest records after downloads, imports, repairs, metadata/transcript/comment/thumbnail retrieval, report generation, ChatGPT package activity, Knowledge AI indexing, renames, moves, duplicate review, archive/deletion and Clip Studio handoff.
>
> Preserve and upgrade the existing Missing Data & AI checkbox above Refresh YouTube metadata. Rename it to:
>
> **Verify/rebuild central artifact manifest for selected videos**
>
> Its help text must explain:
>
> **Scans selected video folders, reconciles present, missing, moved, stale and new artifacts, and refreshes the SQLite manifest plus master JSON/CSV exports. Other commands update the manifest automatically.**
>
> When checked, it must perform deliberate filesystem verification for the selected `VIDEO_ID`s: scan current video and `_data` folders; reconcile new, missing, moved, renamed, stale and duplicate artifacts; update SQLite; update optional per-video manifests; regenerate master JSON/CSV; calculate completeness and recommended next actions; record the verification job in change history. When unchecked, the command must use the cached manifest and verify an individual path only when missing or stale.

## Authoritative storage and exports

- Extend the existing `video_artifact_manifest` SQLite system; do not create a competing inventory.
- Store schema version, inventory refresh date, filesystem verification date and last modifying command/job.
- Create atomic readable exports under `D:\YT GUi\downloads\data\artifact_manifest\`:
  - master JSON inventory;
  - master CSV summary;
  - optional per-video `artifact_manifest.json`.
- An interrupted export or job must not corrupt the last valid manifest.

## Per-video identity and location

Track exact VIDEO_ID, URL, channel URL, original/clean title, channel, upload date, duration, YouTube category, VideoHoarder category, current/previous folder paths, media path/filename, archive/deletion/missing-folder state, and duplicate-group/canonical status.

## Artifact coverage

Track video media, `.info.json`, metadata, description, thumbnail, SRT/VTT, clean transcript, timestamped transcript, comments, HTML report, identity file, ChatGPT evidence/package files, returned ChatGPT results, taxonomy/tag cleanup, Knowledge AI indexes/embeddings, clip plans and generated outputs.

For every artifact store:

- present, missing, unavailable, stale, invalid or not-requested status;
- absolute and relative paths;
- filename, size, modified time and SHA-256 where appropriate;
- source and producing command/job ID;
- created/refreshed/verified dates;
- validation status;
- last error, retry eligibility and cooldown.

## ChatGPT package lifecycle

For every video and package track package ID, master-set ID, batch number/total, package mode, requested features, path, checksum, creation date, manually-sent state, returned-result filename/import date, awaiting/valid/partial/invalid/tampered state, review state, applied state, features received, features missing and whether another package is needed.

Do not package an already completed feature again unless its source evidence changed or the user explicitly requests regeneration.

## Command change history

Every modifying command must record command/job ID, name, start/end time, VIDEO_ID, before/after state, files created/modified/moved/renamed/skipped/removed, result status, error and recovery information.

## Staleness and reconciliation

Detect missing indexed files, changed sizes/timestamps/checksums, moved/renamed files, new unindexed files, duplicate paths, wrong VIDEO_ID folders, orphan database/manifest records and reports or AI outputs older than their source evidence.

Normal commands must use quick targeted checks. Full scanning is allowed only for missing/stale records or an explicit manual rebuild.

## Completeness and next actions

Calculate required/optional present counts, missing and permanently unavailable artifacts, retryable failures, completeness percentage and recommended next action. Support profiles such as full library, no-transcript, metadata-only and archived video.

## Interface

Add an Artifact Manifest area showing totals for indexed, complete, incomplete, stale, missing-folder and error videos; last refresh; live job progress; filters; per-video expandable details; and change history.

Provide actions for Verify Selected, Rebuild Selected, Rebuild Entire Manifest, Export Master JSON and Export Master CSV. Always show whether displayed data came from cache or a new filesystem verification.

## Existing systems to reuse

Consolidate `video_artifact_manifest`, `artifact_inventory()`, `artifact_manifest_for_video()`, `build_video_artifact_manifest()`, ChatGPT request/feature-coverage tables, job progress, audit logs and recovery checkpoints.

## Safety and verification

Manifest maintenance must never automatically download, rename, move or delete files. Add tests for initial creation, incremental changes, stale/missing files, rename/move, import/repair/download updates, archive/deletion tracking, ChatGPT lifecycle, checksums, interrupted recovery, exports and large-library performance. Use temporary fixtures rather than real media.

Update the current feature-status document, implementation changelog, future-request index and recovery checkpoint. Do not mark this complete until every relevant command uses or updates the central manifest, all tests pass, the EXE is rebuilt/installed and the installed application passes runtime verification.

