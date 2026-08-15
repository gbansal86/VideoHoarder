# Codebase Map

- `app/app.py`: main backend, database setup, downloads, transcripts, reports, AI, packages, API, HTML workspace, maintenance, and commands.
- `app/gui.py`: PySide6 desktop host, logging, embedded web view, single-instance behavior.
- `app/native_ui.py`: native dashboard/workflow/settings components.
- `run_gui.pyw`: Windows entry point.
- `tests/`: three focused unittest modules plus fixtures/runtime data.
- `build_support/`: library audit/normalization/rebuild/relocation and build helpers.
- `specs/`: status, changelog, checkpoints, future requests.
- `data/`: SQLite database and runtime/browser data.
- `build/`, `dist/`: PyInstaller artifacts and release outputs.
- `tools/`: document/mockup tooling plus large browser profiles/caches.
