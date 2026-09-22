# Phase 08 — Final Recheck Hardening

## Classification
MEDIUM follow-up hardening on the governed LARGE change set.

## Requirements
- FIX-081: make durable queue-state writes thread-safe and atomic.
- FIX-082: persist every unfinished/recoverable job regardless of completed-history cap.
- PERF-083: keep queue recovery state compact by excluding full result payloads.
- BUILD-084: frozen release must use only the Qt/Shiboken runtime bundled in that exact PyInstaller build.
- PERF-085: bound native thumbnail caches.
- FIX-086: legacy Media Only UI must expose/forward Save SRT.
- DOC-087: synchronize desktop build documentation and final validation with the exact current revision.

## Acceptance criteria
Concurrent queue writes produce no temp-file collisions; 150 unfinished jobs survive a 100-item terminal-history cap; recovery state excludes full result blobs; frozen runtime hook contains no `.videohoarder-build` discovery; thumbnail cache evicts past 256 items; legacy media payload includes Save SRT; full cumulative and extracted-Code-Parent suites pass.
