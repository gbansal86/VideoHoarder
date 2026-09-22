# Feature Inventory — Current VideoHoarder subsystem state (2026-09-13 reconciliation)

This inventory is maintained at the **major subsystem / user-visible feature** level so it remains usable project memory. It is based on the current code paths in this package; Windows-only native rendering remains explicitly marked where it was not executable in this Linux validation environment.

| ID | Feature | Classification | UI / Entry Point | Backend / Evidence | Current gap / note |
|---|---|---|---|---|---|
| F-001 | Native Dashboard command center | FULLY IMPLEMENTED IN CODE | Sidebar → Dashboard | `app/native_ui.py`, `app/gui.py` | Windows visual/runtime verification still required |
| F-002 | Native New Download composer | FULLY IMPLEMENTED IN CODE | Dashboard | `DownloadComposer`, `CommandCenter._start_download` | Windows UI runtime verification required |
| F-003 | Full Library download workflow | FULLY IMPLEMENTED | Dashboard + legacy Downloads | `web_download_workflow`, `web_full_download`, `process_download` | External network/YouTube behavior not exercised here |
| F-004 | Media Only workflow | FULLY IMPLEMENTED | Dashboard + legacy Downloads | `web_download_workflow`, `web_media_only_download` | External network behavior not exercised here |
| F-005 | Audio Only workflow | FULLY IMPLEMENTED IN CODE | Dashboard workflow selector | Media-only path with audio quality | External network behavior not exercised here |
| F-006 | Embedded-video resolver | FULLY IMPLEMENTED IN CODE | Download advanced option / legacy Downloads | `embedded_video_resolver.py`, `resolvers/*` | Live rotating-host behavior depends on source sites |
| F-007 | YouTube 403/cookie fallback | FULLY IMPLEMENTED IN CODE | Download engine | `download_access.py`, canonical parsed-host predicate, configured browser cookies | Lookalike-domain regressions pass; live YouTube response not exercised here |
| F-008 | Duplicate/re-download protection | FULLY IMPLEMENTED IN CODE | Native + legacy Downloads + successful Retry | `download_guard_service.py`, `redownload_history_check`, server-side `/api/job-start` gate | Windows dialogs/runtime verification required |
| F-009 | Managed job queue | FULLY IMPLEMENTED IN CODE | Dashboard compact view + Queue page | `WEB_JOBS`, `job_execution_service.py`, `download_options.py`, worker queue | Per-job cancellation/options/progress isolation validated in Phase 01; Windows UI runtime still required |
| F-010 | Dedicated native Queue page | FULLY IMPLEMENTED IN CODE | Sidebar → Queue | `native_queue_page.py` | Windows visual/runtime verification required |
| F-011 | Queue pause/resume/cancel/retry | FULLY IMPLEMENTED IN CODE | Queue + Job Details | scoped `JobContext` cancel plus explicit queue-wide Stop All | Phase 01/03 regressions validate cancel-one vs Stop All; Windows UI runtime still required |
| F-012 | Queue wait explanation | FULLY IMPLEMENTED IN CODE | Job Details / Queue status | `queue_wait_message()` | Windows runtime verification required |
| F-013 | Queue thumbnails/name/type/progress columns | FULLY IMPLEMENTED IN CODE | Dashboard / Queue | `QueueTable`, `download_queue_service.py` | Windows rendering verification required |
| F-014 | Library browser | FULLY IMPLEMENTED IN CODE | Sidebar → Library | `native_library_page.py`, `library_browser_service.py` | Windows runtime verification required |
| F-015 | Library sort/filter/pagination | FULLY IMPLEMENTED IN CODE | Library | `library_pagination.py`, `web_library_page`, native server-side pager | 12,050-row regression proves pagination beyond historical 10,000 cap; Windows UI runtime still required |
| F-016 | Library thumbnail + click-to-play | FULLY IMPLEMENTED IN CODE | Library row | native library page + local media path | Windows media-open verification required |
| F-017 | Physical Library count | FULLY IMPLEMENTED IN CODE | Dashboard metric | `physical_media_available`, `web_library_stats` | Filesystem scan cost depends on library size |
| F-018 | Completed Today video metric | FULLY IMPLEMENTED IN CODE | Dashboard metric | physical media + canonical `downloaded_at` via `physical_downloaded_today_count` | Existing legacy rows without `downloaded_at` are not backdated automatically |
| F-019 | Refresh all figures | FULLY IMPLEMENTED IN CODE | Dashboard | direct background `FunctionTask`, `refresh_dashboard_figures` | Windows runtime verification required; no longer blocked by paused download queue |
| F-020 | Current failure registry | FULLY IMPLEMENTED | Dashboard + Failure/Cleanup + API | `current_failure_registry.py`, `current_status_service.py` | Historical logs remain separate intentionally |
| F-021 | Delete/dismiss current failure | FULLY IMPLEMENTED IN CODE | Failure/Cleanup + Job Details | `failure_service.py`, current-failure clear APIs | Windows runtime verification required |
| F-022 | Clear all current failures | FULLY IMPLEMENTED IN CODE | Dashboard / Failure UI | `web_clear_all_current_failures` | Guarded action; Windows verification required |
| F-023 | Failure diagnostics/log archive | FULLY IMPLEMENTED | Job Details / logs | `logs/runs`, archive-on-clear | Diagnostic history intentionally retained |
| F-024 | Smart Resume | FULLY IMPLEMENTED IN CODE | More/workflows + backend | `web_smart_resume_download`, audit/reconcile functions | Large real-library scenario not executed here |
| F-025 | Transcript acquisition/health/canonicalization | FULLY IMPLEMENTED IN CODE | download/repair workflows | transcript API + yt-dlp fallback + V3.3.4 tests | External availability/rate limits remain environmental |
| F-026 | Canonical subtitle/VTT/SRT cleanup | FULLY IMPLEMENTED IN CODE | download completion | `canonicalize_video_subtitle_artifacts` | Real Windows path edge cases require runtime validation |
| F-027 | Metadata persistence/normalization | FULLY IMPLEMENTED IN CODE | download/import | `metadata_schema.py`, `metadata_persistence.py`, `metadata_normalization.py`, `metadata_migration.py` | Phase 02 adds per-video SAVEPOINT atomicity and fault/retry regression coverage |
| F-028 | Description cleanup/HTML | FULLY IMPLEMENTED IN CODE | download/report workflows | `description_cleanup.py`, description files | Content quality depends on source description |
| F-029 | HTML video intelligence reports | FULLY IMPLEMENTED IN CODE | Library/report flows | report generation and repair functions | Browser/runtime rendering not tested here |
| F-030 | Comments capture/intelligence | FULLY IMPLEMENTED IN CODE | Full download option / maintenance | YouTube API + yt-dlp fallback | API availability/quota environmental |
| F-031 | ChatGPT processing package workflow | FULLY IMPLEMENTED IN CODE | ChatGPT Processing | `chatgpt_package_builder.py`, exchange/import/validation APIs | Manual ChatGPT exchange remains intentionally user-driven |
| F-032 | ChatGPT package integrity validation | FULLY IMPLEMENTED | tests/build | strict package contract + restored fixture | Full suite passes in current environment |
| F-033 | Knowledge & AI | FULLY IMPLEMENTED IN CODE | Sidebar → Knowledge & AI | phase 5/6 knowledge plus `ai_cache_identity.py` | Embedding/answer-cache correctness validated in Phase 05; Ollama/model availability remains environmental |
| F-034 | YouTube subscriptions collection | PARTIALLY IMPLEMENTED END-TO-END | Sidebar → Subscriptions | OAuth/Selenium/yt-dlp subscription collectors | Subscription → automatic selected-channel video scan remains a separate incomplete workflow from earlier audit |
| F-035 | Collections | FULLY IMPLEMENTED IN CODE | Sidebar → Collections | collection CRUD/export APIs | Windows/web workflow verification not executed here |
| F-036 | Import & Repair | FULLY IMPLEMENTED IN CODE | Sidebar → Import & Repair | old-library preflight/import/repair functions | Destructive/repair actions require controlled user validation |
| F-037 | Recovery center / DB rebuild | FULLY IMPLEMENTED IN CODE | More → Recovery | recovery/rebuild functions | Real recovery should be validated on backup copy |
| F-038 | Dependency/setup assistant | IMPLEMENTED / VERIFIED-IN-SOURCE | More → Setup | `dependency_service.py`, bundled Selenium/YTA plus integrity-gated portable-tool setup | Frozen release does not invoke itself as pip; unverified executable downloads are blocked by default |
| F-039 | Desktop local server readiness | FULLY IMPLEMENTED IN CODE | application startup | `dashboard_server_service.py` | Windows startup timing verification required |
| F-040 | Windows development launcher build + auto-deploy | FULLY IMPLEMENTED IN CODE | `BUILD_DEV_LAUNCHER.ps1` / launcher flow | launcher build → backup/deploy/hash verify | Explicitly separated from the standalone release in Phase 04; Windows execution required |
| F-042 | Self-contained Windows release | FULLY IMPLEMENTED IN CODE / WINDOWS ACCEPTANCE PENDING | `BUILD_WINDOWS.ps1` | `VideoHoarder.spec` + full pytest/native gate + EXE-only release self-test | Source contract is corrected; actual PyInstaller/clean-Windows execution remains NOT EXECUTED here |
| F-043 | Settings validation / persistence boundary | FULLY IMPLEMENTED IN CODE | Settings + `/api/config-save` | `settings_service.py`, atomic persistence wrapper | Invalid type/range/fault-injection regressions pass in Phase 02 |
| F-044 | Local mutating API request boundary | FULLY IMPLEMENTED IN CODE | localhost HTTP mutation endpoints | `local_api_security.py`, strict bounded JSON parser, per-run token | Foreign-origin/host and malformed-JSON regressions pass in Phase 02 |
| F-041 | Implementation-governance evidence | FULLY IMPLEMENTED | repository docs | `docs/implementation/*` | Git checkpoint unavailable because supplied ZIP has no `.git` |

| F-045 | Media/Audio Only output validation + optional SRT | FULLY IMPLEMENTED IN CODE | Native Downloads | `media_only_service.py`, `download_workflows.py`, `app.py` | Windows/live source download acceptance still recommended |
| F-046 | Durable Queue restart recovery | FULLY IMPLEMENTED IN CODE | Queue | `job_persistence_service.py`, `app.py`, `native_ui.py` | all unfinished/interrupted jobs persist independent of terminal-history cap; writes are unique-temp atomic; recovery rows are compact |
| F-047 | Packaged Queue acceptance gate | IMPLEMENTED IN CODE / WINDOWS ACCEPTANCE PENDING | `BUILD_WINDOWS.ps1` | `run_gui.pyw --release-self-test` | must execute on Windows frozen artifact |
| F-049 | Bounded native thumbnail cache | FULLY IMPLEMENTED IN CODE | Library + Queue | `lru_cache.py`, native pages | 256-entry LRU prevents unbounded QPixmap retention |
| F-050 | Legacy Media Save-SRT parity | FULLY IMPLEMENTED IN CODE | Legacy Downloads | `app.py` legacy Media UI/JS | live network acceptance remains environmental |
| F-051 | Content-safe filesystem migration/staging merge | FULLY IMPLEMENTED IN CODE | Startup migration + download commit | `file_safety.py`, startup/staging/transcript-archive/legacy-storage merge paths | Equal-size different-content regressions pass across all known merge paths |
| F-052 | Canonical YouTube URL parser | FULLY IMPLEMENTED IN CODE | Download/queue/duplicate/API source paths | `youtube_url.py` | Live URL/network acceptance remains environmental |
| F-053 | Config corruption recovery/privacy-safe defaults | FULLY IMPLEMENTED IN CODE | Application bootstrap | `config.default.json`, `load_config()` | Corrupt config is quarantined; user should review backup if needed |
| F-054 | Integrity-gated portable tool installer | FULLY IMPLEMENTED IN CODE | More → Setup | SHA-256 verification in dependency download path | Requires configured vendor hash or explicit unverified opt-in |
| F-055 | Byte-reproducible Code Parent | FULLY IMPLEMENTED IN CODE | `CREATE_CODE_PARENT_PACKAGE.bat` | deterministic archive root/timestamps + manifest hashes + full-schema sanitized config example | pristine-regeneration regression passes; `SOURCE_DATE_EPOCH` can override deterministic epoch |
