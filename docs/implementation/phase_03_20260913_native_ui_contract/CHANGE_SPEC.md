# Phase 03 — Native UI contract

Findings: F04, F07, F09.

Saved download-quality/SRT defaults are applied to untouched New Download controls, while explicit user overrides remain deliberate. Running jobs expose scoped `Cancel this job`; `Stop all jobs` is a distinct destructive control. The main native shell now carries a persistent application message strip that is independent of Dashboard queue polling.
