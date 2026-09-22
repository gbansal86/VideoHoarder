# Architecture Notes — Phase 08

- Queue recovery separates **recoverable work** from bounded **terminal history**. Limits never discard QUEUED/RUNNING/CANCELLING/INTERRUPTED rows.
- Queue-state persistence is a compact recovery index, not a second job-result database. Full run results stay in existing run logs.
- Atomic replacement uses a unique temporary file plus a process-local write lock; the shared `<name>.tmp` race is removed.
- Frozen release runtime is self-contained: Qt/Shiboken resolution comes from `sys._MEIPASS` only. Source/development launchers remain separate products.
- Native thumbnail surfaces use bounded LRU caches (256 entries).
- Legacy Media Only now has Save-SRT parity with the native workflow.
