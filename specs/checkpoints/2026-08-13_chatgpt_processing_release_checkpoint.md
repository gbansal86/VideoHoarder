# VideoHoarder ChatGPT Processing Recovery Checkpoint — 2026-08-13

## Verified source state

- Manual ChatGPT exchange only; no automatic upload.
- Strict manifest/package and evidence-file checksum validation.
- Timestamp validation against video duration, with transcript-time fallback when video duration is unavailable.
- Provenance references must name evidence actually present for that VIDEO_ID in the outgoing package.
- Field-level review cards and individual approval decisions are stored in the review audit directory.
- Rename, folder move, metadata and taxonomy outcomes are staged for reviewed existing workflows; physical file changes are not automatic.
- Duplicate groups support canonical selection and Keep/Archive/Mark Delete review records. Delete remains manual.
- Clip plans support VIDEO_ID/timestamp/duration validation, inclusion/order preview and a saved manual handoff to existing Clip Studio.
- Similarity planner supports one small planner package, manual result import, strict 25/50 group rules and grouped intelligence-package creation.

## Test evidence

- `python -m py_compile app/app.py`: passed.
- PySide6 build-environment suite: 14 tests run, 14 passed, 0 skipped.
- Tests cover backend startup, native UI navigation, package tampering, provenance, timestamps, planner import/grouping, duplicate review and clip handoff.
- Destructive media operations were not executed because this release intentionally keeps them manual.

## Recovery files

- Main implementation: `app/app.py`
- Native shell: `app/gui.py`
- Workflow tests: `tests/test_chatgpt_validation.py`
- Current status: `specs/VideoHoarder_Feature_Status_Current.md`
- Changelog: `specs/VideoHoarder_Implementation_Changelog.md`

## Build/install state

- PyInstaller release build completed successfully.
- Installed EXE: `D:\YT GUi\VideoHoarder.exe`
- Installed size: 218,124,389 bytes.
- Installed app launched successfully.
- `/chatgpt-processing` returned HTTP 200 and contained every required workflow control.
- `/api/chatgpt-processing/selectors` returned HTTP 200.
- Duplicate-launch probe exited; the original PyInstaller parent/child pair remained as the only application instance.

## Backlog handoff — 2026-08-14

- Future work is recorded as date-prefixed specifications under `specs/future_requests/`.
- The backlog includes copy-paste prompts for implementing all or selected items and for recording/refining new ideas without authorizing code changes.
- This documentation-only update did not change the verified EXE.

## Future-request organization — 2026-08-15

- The prior pending backlog was moved to `specs/future_requests/2026-08-14_Pending_Updates_Backlog.md`.
- The Central Artifact Manifest proposal is stored at `specs/future_requests/2026-08-15_Central_Artifact_Manifest_System.md`.
- The requested checkbox behavior is included in that proposal. This remained a documentation-only change.
- A standalone browser-editable HTML view was added at `specs/future_requests/VideoHoarder_Future_Requests_Editor.html`; it does not alter the verified application build.
- The editor now includes independent persistent accent and background color palettes; this remains documentation-only.
