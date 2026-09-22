# Files Changed — Phase 08

| File | Change | Requirement |
|---|---|---|
| `app/job_persistence_service.py` | Unique-temp atomic writes; all recoverable jobs; compact row whitelist | FIX-081/FIX-082/PERF-083 |
| `build_support/pyi_rth_videohoarder_qt.py` | Bundled frozen Qt only | BUILD-084 |
| `app/lru_cache.py` | New bounded LRU helper | PERF-085 |
| `app/native_library_page.py` | Bounded thumbnail cache | PERF-085 |
| `app/native_ui.py` | Bounded Queue thumbnail cache | PERF-085 |
| `app/app.py` | Legacy Media Only Save-SRT control/payload | FIX-086 |
| `DESKTOP_README.md` | Correct one-file/optional-deploy documentation | DOC-087 |
| `tests/test_final_recheck_fixes.py` | New regressions/integration coverage | ALL |
| `docs/implementation/*` | Current traceability/final evidence | DOC-087 |
