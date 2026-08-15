# Feature Catalog

Recorded: 2026-08-15
Status basis: code presence plus explicitly recorded test/runtime evidence

Independent review on 2026-08-15 confirmed these classifications against baseline `f74650adbfc04b26386835cab05fd71109611e2b`. Fixture- and runtime-dependent rows remain `NEEDS REVIEW`; see `INDEPENDENT_VALIDATION_REPORT.md`.

| Area | Status | Primary evidence | Verification and limitations |
|---|---|---|---|
| Windows application entry | IMPLEMENTED | `run_gui.pyw`, `app/gui.py:main()` | Compilation passed; installed interaction not rerun in current audit |
| Single-instance desktop shell | IMPLEMENTED / NEEDS REVIEW | `app/gui.py:acquire_single_instance()`, `MainWindow` | Prior checkpoint reports installed guard verification |
| Native dashboard/navigation | IMPLEMENTED / PARTIAL | `app/native_ui.py`, `Sidebar`, `CommandCenter`, `WorkflowsPage`, `SettingsPage` | Three UI tests exist but skipped in system Python without PySide6 |
| Embedded web workspace | IMPLEMENTED | HTTP handler and HTML/JS in `app/app.py` | Dashboard startup and `/api/progress` smoke test passed |
| Dependency/tool discovery | IMPLEMENTED / NEEDS REVIEW | `refresh_tool_paths()`, `dependency_status()`, setup functions | External installation paths not exercised |
| YouTube source metadata | IMPLEMENTED / NEEDS REVIEW | source descriptor, playlist/channel enumeration, API metadata functions | Network/API calls not run |
| Download pipeline | IMPLEMENTED / NEEDS REVIEW | `process_download()`, fallback/quality selectors, progress jobs | Real media download not run |
| Queue, progress, cancellation | IMPLEMENTED / NEEDS REVIEW | state/progress/job APIs and UI | Concurrency/cancellation edge cases not tested |
| Caption/transcript retrieval | IMPLEMENTED / NEEDS REVIEW | transcript API, caption download, VTT/SRT conversion functions | Provider/network/language cases not run |
| Transcript cleanup/analysis | IMPLEMENTED / NEEDS REVIEW | parsing, chunking, deterministic and Ollama-assisted analysis | Fixture-level output quality not audited |
| Library organization | IMPLEMENTED / NEEDS REVIEW | folder naming, staging, commit, migration, indexing functions | Real rename/move operations not run |
| Library browsing/detail/state | IMPLEMENTED / NEEDS REVIEW | `/api/library-browser`, `/api/video-detail`, video state handlers | Checked source DB has zero videos |
| HTML reports/navigation | IMPLEMENTED / NEEDS REVIEW | `write_html_report()`, report navigation and rebuild functions | Generated reports not visually inspected this session |
| Taxonomy and categorization | IMPLEMENTED / NEEDS REVIEW | taxonomy hashes, exports/imports, move preview/apply/undo | Apply/undo not run |
| Comments intelligence | IMPLEMENTED / NEEDS REVIEW | comments files/counts/intelligence fields and functions | Live YouTube comments not tested |
| Failure tracking/retry | IMPLEMENTED / NEEDS REVIEW | failure CSV/TXT/history and retry functions | Interruption/retry matrix not exercised |
| Delete marker/purge | IMPLEMENTED / NEEDS REVIEW | delete marker, collection, purge, DB/index cleanup functions | Destructive path intentionally not executed |
| Old-library import/repair | IMPLEMENTED / NEEDS REVIEW | preflight, merge, path repair, folder reconstruction functions | Requires controlled populated fixtures |
| Maintenance/recovery/backups | IMPLEMENTED / NEEDS REVIEW | audit, recovery roots, DB merge, cleanup, backup functions | Full disaster recovery not tested |
| ChatGPT package creation | IMPLEMENTED / PARTIAL | request tables, package builders, manifests/evidence/prompt/schema | Real package lifecycle not executed in this audit |
| Package integrity/provenance | IMPLEMENTED / VERIFIED | validation functions and `test_chatgpt_validation.py` | Tamper/provenance/timestamp tests passed |
| Similar-video planner | IMPLEMENTED / VERIFIED CORE | planner package/import/group validation | Integrity and 25/50 group rules tested; UI not exercised |
| Result import/review | IMPLEMENTED / PARTIAL | import-many, review, CSV, field history, coverage tables | Real multi-result apply workflow not run |
| Duplicate review | IMPLEMENTED / VERIFIED SAFETY | duplicate review function/test | Test confirms review records and no physical deletion |
| Clip planning/handoff | IMPLEMENTED / VERIFIED SAFETY | clip validation/handoff function/test | Validation and non-execution tested; cutting/merge not run |
| Collections | IMPLEMENTED / NEEDS REVIEW | Phase 6 collection APIs/storage | Populated-library behavior not run |
| Knowledge Center/search | IMPLEMENTED / NEEDS REVIEW | Phase 6 search/Ask Library, indexes, Ollama APIs | Empty DB; Ollama not invoked |
| External media | IMPLEMENTED / NEEDS REVIEW | `external_media` table, commands and API | External protocols not exercised |
| YouTube subscriptions | IMPLEMENTED / NEEDS REVIEW | `youtube_subscriptions` table, collection/UI functions | Browser/network collection not run |
| Central artifact manifest | PARTIAL | table plus `artifact_inventory()`, `artifact_manifest_for_video()`, `build_video_artifact_manifest()` | Full proposed lifecycle/reconciliation/export/UI integration not implemented |
| Windows build/package | IMPLEMENTED / VERIFIED HISTORICALLY | `BUILD_WINDOWS.ps1`, `VideoHoarder.spec`, build logs | Existing EXE and installed EXE hashes match; no new build run |
| Git/source handoff | IMPLEMENTED | `.gitignore`, GitHub `main`, `PROJECT_KNOWLEDGE` | Pre-baseline history unavailable |

Status changes require code/test evidence and corresponding updates to `IMPLEMENTATION_TRUTH.md`.
