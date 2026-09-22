# Phase 04 Test Plan

- Static build-product separation and application-spec contract.
- Full pytest gate and native PySide no-skip gate present in release script.
- Sanitized bundled config contract.
- Frozen Program Files writable-root fallback.
- Clean-room EXE-only self-test contract.
- Existing deployment backup/hash contract preserved.
- Full cumulative source suite.
- On Windows: execute BUILD_WINDOWS.ps1, native UI tests, PyInstaller build, clean-room self-test, and optional deployment/hash verification.
