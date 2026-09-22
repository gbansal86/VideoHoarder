# Test Plan — Phase 08

1. Concurrent atomic queue writers (300 writes / 16 workers).
2. 150 recoverable jobs plus 150 completed jobs with terminal-history cap 100.
3. Backend persist/restore integration with 150 unfinished jobs.
4. Compact payload excludes a 1 MiB synthetic result blob.
5. Frozen runtime-hook source contract rejects external build-runtime discovery.
6. Legacy web Media Only SRT UI/payload contract.
7. Bounded LRU eviction.
8. README release-layout/deploy contract.
9. Full cumulative pytest and compileall.
10. Generate Code Parent, validate manifest, extract it, rerun complete pytest from extracted handoff.
