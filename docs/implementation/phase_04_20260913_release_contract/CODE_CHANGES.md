# Code Changes

- BUILD_WINDOWS.ps1 builds VideoHoarder.spec, not the launcher spec.
- Development launcher moved to its own build script.
- Release gate runs full pytest, requires unskipped native subset on Windows, and performs EXE-only clean-room self-test.
- Bundled config is sanitized and frozen Program Files installs use per-user writable state.
