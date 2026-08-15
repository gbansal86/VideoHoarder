# Checkpoint — 2026-08-13

## Current state

- Source: Python + PySide6 VideoHoarder desktop application.
- Main source files: `app/app.py`, `app/gui.py`.
- Installed EXE: `D:\YT GUi\VideoHoarder.exe`.
- Local service: `http://127.0.0.1:8765`.

## Last verified

- Python compilation passed.
- Automated suite: 7 passed, 3 GUI tests skipped in system Python.
- Live HTTP checks passed for overview, history, coverage, selectors, ChatGPT Processing, and planner preview.

## Current implementation boundary

- ChatGPT exchange remains manual-only.
- Current Work, planner, selectors, package history, coverage, and package deletion filtering are present.
- Advanced review/apply, rich duplicate review, Clip Studio handoff, and strict provenance validation remain incomplete.

## Recovery rule

If a future build fails, use this checkpoint plus the two status documents to identify the last verified state before changing or rebuilding anything.

## Latest source pass

- Collection selector data now comes from the existing Phase 6 collection store.
- Selecting a collection scopes package creation to its stored VIDEO_IDs.
- Source compilation, automated tests, and live selector/page smoke tests passed.
- EXE rebuild/install for this newest pass remains pending.

## Installed release verification

- PyInstaller completed using a background monitored process.
- `D:\YT GUi\VideoHoarder.exe` replaced and launched.
- `/chatgpt-processing` returned HTTP 200 and included the collection selector UI.
