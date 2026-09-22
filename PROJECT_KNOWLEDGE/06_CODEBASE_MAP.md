# Codebase Map

Recorded: 2026-08-15

## Runtime source

- `run_gui.pyw` - Windows GUI entry point.
- `app/gui.py` - PySide6 application host, file logging, safe web navigation, loading/error surfaces, main windows, exception hook, single-instance guard, and startup.
- `app/native_ui.py` - native sidebar, metric cards, download composer, queue table, job details, command center, workflow cards/page, settings page, and stylesheet.
- `app/app.py` - approximately 25,000 physical lines and the primary architectural hotspot. It owns configuration, SQLite schema, downloads, transcripts, reports, taxonomy, artifacts, failures, repair/recovery, ChatGPT packages, collections/Knowledge AI, jobs, local HTTP APIs, embedded HTML/JavaScript, external media, subscriptions, clips, menus, and command dispatch.

## Build and installation

- `BUILD_WINDOWS.ps1` - isolated environment, dependencies, compile/test gate, icon generation, PyInstaller, and ZIP packaging.
- `VideoHoarder.spec` - PyInstaller specification.
- `INSTALL_GUI.ps1` - installation helper.
- `requirements.txt` - runtime dependency declaration.
- `requirements-build.txt` - build dependencies.
- `assets/` - application icons.
- `build_support/` - library audit/finalization/normalization/rebuild, refresh, relocation, DB path replacement, rendering, icon, and version helpers.

## Tests

- `tests/test_backend_smoke.py` - root override, config, dashboard startup, and canonical health-file preservation.
- `tests/test_chatgpt_validation.py` - timestamps, integrity tamper detection, provenance, planner rules, duplicate safety, and clip handoff.
- `tests/test_native_ui.py` - sidebar/workflow/download preset declarations; requires PySide6.
- `tests/fixtures/` - intentional package fixtures. `tests/runtime_data/` is ignored.

## Specifications and project memory

- `specs/VideoHoarder_Feature_Status_Current.md` - pre-knowledge feature status.
- `specs/VideoHoarder_Implementation_Changelog.md` - historical change narrative.
- `specs/checkpoints/` - recovery/release checkpoints.
- `specs/future_requests/` - proposed work, including Central Artifact Manifest.
- `PROJECT_KNOWLEDGE/` - canonical current handoff and implementation truth.

## Design/source-support tools

- `tools/*.py` - document/spec/mockup generation and inspection helpers.
- `tools/*.html`, selected PNGs and DOCX files - design and specification artifacts intentionally included.
- Browser profiles, render QA, caches, and temporary outputs are ignored.

## Runtime data excluded from Git

`data/`, `downloads/`, `all_transcripts/`, `logs/`, `maintenance/`, builds/releases, databases, user URL/key files, browser profiles, caches, and test runtime output.

## Ownership recommendation

Before decomposition, add characterization tests around stable public functions and HTTP behavior. Extract bounded modules in this order: configuration/path safety, database/schema, jobs/progress, artifact manifest, ChatGPT packages, transcript/report services, downloads/external integrations, then HTTP/UI rendering.
