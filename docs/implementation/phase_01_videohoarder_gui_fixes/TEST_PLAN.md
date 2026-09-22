# Test Plan

1. Compile all changed Python modules.
2. Resolver recursive iframe chain and direct-host canonicalization.
3. Resolver plugin component registration.
4. Resolve-then-download and unresolved fallback-to-original URL.
5. Browser cookie retry and YouTube attempt ladder.
6. Queue metadata/thumbnail/batch summary helpers.
7. Library stale-index/live-SQLite overlay and downloaded-date sorting.
8. Failure retrieval beyond old default cap and selective cleanup/count behavior.
9. Existing backend smoke/regression suite.
10. Full repository test suite.
11. Native PySide tests when PySide6 is available; otherwise record SKIPPED/NOT EXECUTED rather than claiming GUI runtime validation.
