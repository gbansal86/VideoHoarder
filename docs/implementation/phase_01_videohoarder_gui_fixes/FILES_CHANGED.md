# Files Changed

| File | Change type | Reason |
|---|---|---|
| `app/app.py` | Refactored/Modified | Thin wiring/wrappers, queue metadata hooks, live Library source, config/use of modular services |
| `app/config.json` | Modified | Browser cookies default + cookie fallback flag |
| `app/native_ui.py` | Modified | Queue UI, per-URL batch, navigation and attention behavior |
| `app/gui.py` | Modified | Refresh/focus navigation |
| `app/embedded_video_resolver.py` | Added | Resolver traversal/report orchestration |
| `app/resolvers/base.py` | Added | Plugin contracts/data |
| `app/resolvers/known_hosts.py` | Added | Dailymotion/YouTube/Vimeo plugins |
| `app/resolvers/players.py` | Added | FastVid/DramaVideo/generic iframe plugins |
| `app/resolvers/__init__.py` | Added | Resolver registry exports |
| `app/download_workflows.py` | Added | Resolve-before-download orchestration |
| `app/download_queue_service.py` | Added | Queue names/type/thumbnail/batch metadata |
| `app/library_browser_service.py` | Added | Live state overlay/filter/sort |
| `app/download_access.py` | Added | Cookie and YouTube fallback policy |
| `app/failure_service.py` | Added | Current failure aggregation/cleanup |
| `tests/test_gui_issue_fixes.py` | Added | New regression tests |
| `tests/test_backend_smoke.py` | Modified | Failure retrieval/cleanup regression tests |
| `tests/test_native_ui.py` | Modified | Native queue/resolver wiring coverage (skipped here without PySide6) |
