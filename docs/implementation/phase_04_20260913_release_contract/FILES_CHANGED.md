# Files Changed

| File / Area | Change Type | Reason |
|---|---|---|
| `BUILD_WINDOWS.ps1` | Modified/Added | BUILD_WINDOWS.ps1 builds VideoHoarder.spec, not the launcher spec. |
| `BUILD_DEV_LAUNCHER.ps1` | Modified/Added | Development launcher moved to its own build script. |
| `BUILD_DEV_LAUNCHER.bat` | Modified/Added | Release gate runs full pytest, requires unskipped native subset on Windows, and performs EXE-only clean-room self-test. |
| `VideoHoarder.spec` | Modified/Added | Bundled config is sanitized and frozen Program Files installs use per-user writable state. |
| `VideoHoarder_launcher.spec` | Modified/Added | Bundled config is sanitized and frozen Program Files installs use per-user writable state. |
| `run_gui.pyw` | Modified/Added | Bundled config is sanitized and frozen Program Files installs use per-user writable state. |
| `app/app.py` | Modified/Added | Bundled config is sanitized and frozen Program Files installs use per-user writable state. |
| `app/gui.py` | Modified/Added | Bundled config is sanitized and frozen Program Files installs use per-user writable state. |
| `app/config.default.json` | Modified/Added | Bundled config is sanitized and frozen Program Files installs use per-user writable state. |
| `tests/test_phase4_release_contract.py` | Modified/Added | Bundled config is sanitized and frozen Program Files installs use per-user writable state. |
