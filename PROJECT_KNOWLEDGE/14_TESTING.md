# Testing

Recorded: 2026-08-15

## Current reconciliation run

- Command: `py -3 -m py_compile app/app.py app/gui.py app/native_ui.py run_gui.pyw` - PASSED.
- Command: `py -3 -m unittest discover -s tests -p 'test_*.py' -v`.
- Discovered: 14; passed: 11; failed: 0; skipped: 3.
- Skip reason: PySide6 is not installed in current system Python.

## Independent validation rerun

- Baseline: `f74650adbfc04b26386835cab05fd71109611e2b`, clean and synchronized with `origin/main` before documentation edits.
- Compilation command rerun: PASSED.
- Unittest discovery rerun: 14 discovered, 11 passed, 0 failed, 3 skipped for the same PySide6 environment limitation.
- Dashboard smoke again started the loopback server and passed.
- This rerun confirms the existing test record; it does not expand the behaviors covered by those tests.

## Actual coverage

- Backend: library-root override, config presence, dashboard startup/progress endpoint, canonical health-file migration.
- ChatGPT: timestamp parser/walker, package tamper detection, evidence provenance availability, planner integrity/group limits, duplicate review safety, clip-plan validation/manual handoff.
- Native UI declarations: sidebar, eight workflows, and download presets, but only when PySide6 is available.

## Historical evidence

`specs/` records 14/14 passing in the separate PySide6 build environment and installed runtime HTTP/UI checks on 2026-08-13. This is preserved as historical evidence, not reported as the current run.

## Material gaps

No automated coverage for populated DB migrations, artifact-manifest reconciliation, downloads/providers, report rendering, package generation/multiple-import/combined-CSV, review decision persistence, tag cleanup, taxonomy apply/undo, jobs/concurrency/cancellation, local HTTP security, collections/Ollama, recovery/interruption, destructive-operation fixtures, installed GUI, clean build, or large-library performance.
