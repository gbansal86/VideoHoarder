# VideoHoarder Pending Updates

Originally recorded: 2026-08-14

This is the general backlog for future VideoHoarder work. Adding an idea here does not authorize implementation.

## Current pending updates

1. Standardize detailed live progress for every command.
   - Show command, phase, current VIDEO_ID/file, processed/total, skipped, failed, speed, elapsed time, ETA and latest error.
   - Use the same progress model in Queue, Current Work and task pages.

2. Improve Library and Old Library Import & Repair screens.
   - Add clearer status cards, preflight summaries and per-file repair progress.
   - Keep multiple source-folder selection and resumable checkpoints.

3. Optimize large legacy-library repairs.
   - Reduce repeated folder scans by using the central artifact manifest.
   - Preserve the five-second maximum for unavailable transcript/subtitle checks.
   - Resume from the last completed VIDEO_ID after interruption.

4. Project normalized ChatGPT intelligence throughout the app.
   - Show approved summaries, taxonomy, entities, topics and feature coverage in Library, reports, search and Knowledge Center.
   - Preserve package/request provenance for every displayed field.

5. Automate backup retention.
   - Keep only the four newest verified VideoHoarder EXE backups.
   - Never remove data/library backups through this EXE-retention rule.

6. Run real-user acceptance testing with actual ChatGPT return packages.
   - Test valid, partial, invalid, tampered and multi-file returns.
   - Test reviewed rename/move/taxonomy staging, duplicate decisions and Clip Studio handoff without automatic destructive actions.

## Prompt to implement the entire backlog

> Implement every item currently listed in `D:\YT GUi\specs\future_requests\2026-08-14_Pending_Updates_Backlog.md`. Inspect the existing implementation first and reuse existing systems. Complete the code, automated tests, installed-runtime testing, documentation updates, recovery checkpoint, EXE build and installation in one release. Keep ChatGPT exchange manual and do not automatically rename, move, delete, cut, merge or download media. Do not mark an item complete unless it is implemented and verified.

## Prompt to implement selected items

> Implement pending-update items 1, 2 and 3 from `D:\YT GUi\specs\future_requests\2026-08-14_Pending_Updates_Backlog.md`. Complete their code and tests, update the status/changelog, create a recovery checkpoint, rebuild and install the EXE, and report anything genuinely still pending.

## Prompt to record a new future idea only

> Create a date-prefixed specification under `D:\YT GUi\specs\future_requests`. Clarify the idea's purpose, UI location, behavior, safety rules, dependencies and acceptance tests. Update `README.md` and the changelog. Do not implement or rebuild anything yet: [describe the idea].

## Completion rules

- Reuse existing VideoHoarder systems instead of creating duplicate workflows.
- Keep one application/backend instance.
- Show live progress for long-running work.
- Keep ChatGPT exchange manual-only.
- Require review before physical rename, movement, deletion, cutting or merging.
- Update current status, changelog, future-request status and recovery checkpoint after every release.
- Create a dated checkpoint and keep no more than four verified EXE backups.
- Build and install the EXE only after tests pass.

