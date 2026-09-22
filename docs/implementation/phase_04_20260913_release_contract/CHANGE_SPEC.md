# Phase 04 — Windows release contract

Findings: F03 and the Windows portion of F05.

`BUILD_WINDOWS.ps1` now builds the actual GUI application from `VideoHoarder.spec`; the Source/.videohoarder-build launcher is a separate `BUILD_DEV_LAUNCHER.ps1` product. Release builds execute the full pytest gate, a native-PySide subset with no skips permitted, then an EXE-only clean-room `--release-self-test`. The bundled default config is sanitized, and frozen Program Files installations use per-user application data rather than writing beside the EXE.
