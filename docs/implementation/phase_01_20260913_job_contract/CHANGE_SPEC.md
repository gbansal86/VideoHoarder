# Phase 01 — Job execution contract

Findings: F01, F02, F06, F12.

Implemented immutable per-job `DownloadOptions`, per-job `JobContext` cancellation/process ownership, scoped running-job cancel, explicit queue-wide Stop All, truthful per-input download outcome accounting, and progress that separates batch position from current-transfer progress. Full Download no longer temporarily mutates process-global CFG/RUNTIME to express job options.
