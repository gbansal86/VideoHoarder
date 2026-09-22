# Traceability Matrix

| Requirement ID | Requirement | Code Files | Test IDs / Evidence | Status |
|---|---|---|---|---|
| FIX-601 | Job Details controls must fit/read correctly | app/native_ui.py | `Issue6SourceContractTests.test_job_details_controls_are_stacked_not_two_column`; native PySide runtime test remains skipped here | IMPLEMENTED / WINDOWS VERIFY |
| REQ-602 | Ask before same video is downloaded again | app/download_guard_service.py, app/app.py, app/native_ui.py | `DuplicateDownloadGuardTests.*`; existing deleted-video guard tests | PASS |
| FIX-603 | Library count increases promptly after successful download | app/native_ui.py, app/library_stats_service.py | `Issue6SourceContractTests.test_terminal_job_triggers_library_stats_refresh`; physical-media unit tests | PASS (logic) / WINDOWS VERIFY |
| REQ-604 | Queue must expose all columns with horizontal/vertical scrolling and Refresh queue | app/native_ui.py, app/native_queue_page.py | source contract + PySide Issue6 queue-scroll test | IMPLEMENTED / WINDOWS VERIFY |
| ARCH-605 | Queue tab must not be the same page as Dashboard | app/gui.py, app/native_queue_page.py | `test_queue_is_a_distinct_native_page`; PySide dedicated Queue test | IMPLEMENTED / WINDOWS VERIFY |
| FIX-606 | Explain why queued jobs are waiting | app/native_ui.py, app/native_queue_page.py | `test_queued_reason_mentions_paused_queue`; PySide queued-reason test | IMPLEMENTED / WINDOWS VERIFY |
| FIX-607 | Refresh all figures must reflect physical deletion | app/library_stats_service.py, app/app.py, app/native_ui.py | `PhysicalLibraryCountTests.*`; terminal refresh contract | PASS (logic) / WINDOWS VERIFY |
| FIX-609 | Full build test suite must not fail because fixture is missing | tests/fixtures/chatgpt_integrity/... | full suite 115 OK, 19 skipped | PASS |
| DOC-608 | Maintain governance evidence in repo | docs/implementation/* | file inventory | PASS |

| FIX-701 | Refresh All Figures works while queue paused/busy | app/native_ui.py | `V7SourceContractTests.test_refresh_all_figures_bypasses_managed_download_queue` | PASS logic / WINDOWS VERIFY |
| REQ-702 | Duplicate confirmation on native, legacy, server job-start and successful Retry | app/download_guard_service.py, app/app.py, app/native_ui.py, app/native_queue_page.py | `V7BackendGuardTests.test_legacy_duplicate_report_includes_current_queue`; `test_successful_retry_requires_explicit_confirmation`; source contract | PASS |
| FIX-703 | No lost stats refresh when a stats read is already running | app/native_ui.py | `V7SourceContractTests.test_stats_refresh_has_pending_and_inflight_targets` | PASS logic / WINDOWS VERIFY |
| FIX-704 | Completed Today counts physical downloaded videos, not maintenance jobs | app/library_stats_service.py, app/app.py, app/native_ui.py | `V7DashboardMetricTests.test_completed_today_counts_physical_videos_not_generic_jobs` | PASS |
| FIX-705 | Full Library success writes downloaded_at | app/app.py | `V7SourceContractTests.test_full_download_records_downloaded_at` | PASS source contract / LIVE DOWNLOAD VERIFY |
| FIX-706 | Queue reason reflects actual wait state/position | app/download_queue_service.py, app/native_ui.py | `V7DashboardMetricTests.test_queue_wait_reason_distinguishes_worker_start_from_earlier_jobs` | PASS |
| FIX-707 | Dedicated Queue can request all in-memory jobs | app/app.py, app/native_queue_page.py | `V7BackendGuardTests.test_unlimited_snapshot_returns_more_than_60` | PASS |
| DOC-708 | Governance inventory/evidence reflects final code | docs/implementation/* | file review + phase evidence | PASS |

| REQ-REFRESH-001 | Refresh all figures must run without constructor/runtime error and remain independent of managed download queue | Phase 03 | `app/native_ui.py` | `CommandCenter._refresh_all_figures`, `FunctionTask` call contract | `V7SourceContractTests.test_refresh_all_figures_bypasses_managed_download_queue`, `test_all_function_task_calls_match_two_argument_constructor` | `phase_03_refresh_figures_runtime_fix/TEST_RESULTS.html` | VALIDATED IN SOURCE/UNIT TESTS; WINDOWS GUI PENDING |

| REQ-018 | Library thumbnail is larger | app/native_library_page.py | Historical Phase 03 evidence | IMPLEMENTED HISTORICALLY |
| REQ-019 | Library sort includes Video/Channel/Category | app/native_library_page.py, app/library_browser_service.py | Historical Phase 03 evidence | IMPLEMENTED HISTORICALLY |
| REQ-020 | Unified current-failure register | app/current_failure_registry.py, app/app.py | Historical Phase 03/04 evidence | IMPLEMENTED HISTORICALLY |
| REQ-021 | Current failures can be deleted/dismissed | app/failure_service.py, app/current_failure_registry.py | Historical Phase 03/04 evidence | IMPLEMENTED HISTORICALLY |
| REQ-022 | Visible Delete beside failure entry | app/native_failure_page.py | Historical Phase 03 evidence | IMPLEMENTED HISTORICALLY |
| REQ-023 | Downloads navigation exposes existing download screen | app/native_ui.py, app/gui.py | Historical Phase 03 evidence | IMPLEMENTED HISTORICALLY |
| ARCH-003 | Keep new failure logic outside app.py | app/current_failure_registry.py | Historical Phase 03 evidence | IMPLEMENTED HISTORICALLY |
| FIX-041 | Failure count matches current failure list | failure registry/UI | Historical Phase 04 evidence | IMPLEMENTED HISTORICALLY |
| FIX-042 | Complete unresolved failure list | failure registry/UI | Historical Phase 04 evidence | IMPLEMENTED HISTORICALLY |
| FIX-043 | Delete action beside each current failure | native failure UI | Historical Phase 04 evidence | IMPLEMENTED HISTORICALLY |
| FIX-044 | Stable-key deletion for failures without VIDEO_ID / queue jobs | failure service | Historical Phase 04 evidence | IMPLEMENTED HISTORICALLY |
| ARCH-045 | Keep Phase 04 logic outside app.py | failure service modules | Historical Phase 04 evidence | IMPLEMENTED HISTORICALLY |
| GOV-001 | Reconcile master governance records to current package/history | docs/implementation/* | file review + Phase 0 tests | PHASE 0 IMPLEMENTED |
| GOV-002 | One deterministic sanitized Code Parent with self-validated manifest | scripts/create_code_parent_package.py, tests/test_code_parent_package.py | package-integrity tests + generated archive validation | PHASE 0 IMPLEMENTED |
| TEST-005 | Windows build gate executes complete pytest test directory | BUILD_WINDOWS.ps1 | source contract + full pytest run | PHASE 0 IMPLEMENTED; WINDOWS EXECUTION PENDING |

## VH-AUDIT-20260913 implementation traceability

| Requirement ID | Finding | Phase | Code Files / Components | Test Evidence | Status |
|---|---|---|---|---|---|
| FIX-101 | F01 scoped running-job cancellation | 01 | `app/job_execution_service.py`, `app/app.py` | `test_phase1_job_contract.py` + cumulative suite | PASS |
| FIX-102 | F02 zero-result Full Download must not succeed | 01 | `app/app.py` | Phase 01 zero-resolution regression | PASS |
| FIX-103 | F06 current transfer progress semantics | 01 | job progress wrapper/service | Phase 01 one-video progress regression | PASS |
| ARCH-104 | F12 immutable per-job options / no global CFG race | 01 | `app/download_options.py`, job context/wrappers | Phase 01 option-isolation regression | PASS |
| FIX-201 | F13 validated/atomic settings | 02 | `app/settings_service.py` | invalid range/type + fault atomicity | PASS |
| SEC-202 | F14 mutating localhost API authorization boundary | 02 | `app/local_api_security.py`, HTTP handler | foreign Host/Origin rejected before dispatch | PASS |
| SEC-203 | F15 malformed JSON cannot dispatch mutation | 02 | strict JSON reader / HTTP handler | malformed-body regression | PASS |
| FIX-204 | F16 correct suffix/single HTTP byte ranges | 02 | `app/http_range.py`, media handler | suffix/open/closed range tests | PASS |
| FIX-205 | F17 per-video migration atomicity | 02 | `app/metadata_migration.py` | injected failure + clean retry | PASS |
| FIX-301 | F04 Settings defaults reach untouched New Download controls | 03 | native download composer/settings bridge | Phase 03 source/native contracts | PASS LOGIC / WINDOWS UI PENDING |
| FIX-302 | F07 Cancel this job distinct from Stop all | 03 | native queue/job controls | Phase 03 source/native contracts | PASS LOGIC / WINDOWS UI PENDING |
| FIX-303 | F09 app-wide visible status surface | 03 | native shell notification strip | Phase 03 source/native contracts | PASS LOGIC / WINDOWS UI PENDING |
| BUILD-401 | F03 true standalone release separate from dev launcher | 04 | `BUILD_WINDOWS.ps1`, `BUILD_DEV_LAUNCHER.ps1`, `VideoHoarder.spec`, `run_gui.pyw` | `test_phase4_release_contract.py`; Windows artifact execution pending | SOURCE PASS / WINDOWS EXECUTION PENDING |
| TEST-402 | F05 release/build gate covers complete pytest suite | 04 | `BUILD_WINDOWS.ps1` | build-contract tests + cumulative pytest | PASS SOURCE / WINDOWS EXECUTION PENDING |
| SCALE-501 | F08 real Library total/server-side pagination beyond 10k | 05 | `app/library_pagination.py`, native Library, `/api/library-page` | 12,050-row + 1,800-search-score regressions | PASS |
| AI-502 | F10 embedding cache model/backend compatibility | 05 | `app/ai_cache_identity.py`, Phase-6 embedding functions | wrong-backend legacy vector forced rebuild | PASS |
| AI-503 | F11 Local AI cache invalidates when evidence changes | 05 | `app/ai_cache_identity.py`, Phase-6 answer cache | same chunk ID / corrected text yields fresh answer | PASS |

| FIX-071 | Reject Media Only false success without output | Phase 07 | `app/app.py`, `app/media_only_service.py` | `web_media_only_download`, `usable_media_file` | `test_media_only_requires_real_nonempty_output` | full pytest + Phase 07 HTML | PASS |
| FIX-072 | Honor SRT in Media/Audio Only | Phase 07 | `app/download_workflows.py`, `app/app.py`, `app/media_only_service.py` | workflow + SRT helper | `test_media_only_srt_option_is_forwarded` | full pytest + Phase 07 HTML | PASS |
| ARCH-073 | Restore unfinished queue jobs as interrupted | Phase 07 | `app/job_persistence_service.py`, `app/app.py`, `app/native_ui.py` | persist/restore/retry | `test_unfinished_job_restores_as_interrupted_with_retry_task` | full pytest + Phase 07 HTML | PASS |
| TEST-074 | Packaged Queue acceptance | Phase 07 | `run_gui.pyw`, `BUILD_WINDOWS.ps1` | `release_self_test` | source contract; Windows clean-room gate | Windows execution pending | PARTIAL/PENDING WINDOWS |
| FIX-075 | Canonical Dashboard progress | Phase 07 | `app/native_ui.py` | `refresh_fast` | `test_command_center_uses_canonical_progress_for_bottom_bar` | full pytest | PASS |
| PERF-076 | Library query off GUI thread | Phase 07 | `app/native_library_page.py` | `refresh` + callbacks | `test_library_refresh_runs_backend_page_query_in_worker` | full pytest | PASS |
| FIX-077 | Queue-first isolated backend attachment | Phase 07 | `app/gui.py` | `MainWindow.backend_ready` | `test_backend_ready_attaches_queue_first_and_isolates_page_failures` | full pytest | PASS |
| FIX-078 | Correct Code Parent BAT artifact message | Phase 07 | `CREATE_CODE_PARENT_PACKAGE.bat` | wrapper | `test_code_parent_wrapper_reports_the_zip_that_remains` | full pytest | PASS |

| FIX-081 | Queue-state concurrent write safety | Phase 08 | `app/job_persistence_service.py` | `atomic_write` | `test_atomic_queue_write_is_safe_under_concurrent_writers` | Phase 08 HTML + full suite | PASS |
| FIX-082 | Preserve all unfinished jobs beyond history cap | Phase 08 | `app/job_persistence_service.py`, `app/app.py` | `queue_payload`, persist/restore | >100 service + 150-job backend integration regressions | Phase 08 HTML + full suite | PASS |
| PERF-083 | Compact restart state | Phase 08 | `app/job_persistence_service.py` | `_compact_job` | large result omission regression | Phase 08 HTML | PASS |
| BUILD-084 | Frozen release uses bundled Qt only | Phase 08 | `build_support/pyi_rth_videohoarder_qt.py` | runtime hook | source contract + Windows release gate pending | Phase 08 HTML | PASS SOURCE / WINDOWS PENDING |
| PERF-085 | Bound thumbnail memory | Phase 08 | `app/lru_cache.py`, native UI pages | LRU cache | eviction regression | Phase 08 HTML | PASS |
| FIX-086 | Legacy Media Save-SRT parity | Phase 08 | `app/app.py` | legacy Downloads HTML/JS | UI/payload source regression | Phase 08 HTML | PASS |
| DOC-087 | Documentation synchronized | Phase 08 | README + governance/final_validation | N/A | document/source checks | final validation | PASS |
| FIX-091 | Destructive dedupe requires content equality | app/file_safety.py, app/app.py | `test_equal_size_different_content_is_not_duplicate`; `test_legacy_migration_preserves_equal_size_different_content`; `test_staging_commit_preserves_equal_size_different_media` | PASS |
| FIX-092 | Frozen installed state must stay writable outside Program Files | app/app.py | Phase-A/F source contracts | PASS SOURCE CONTRACT / WINDOWS INSTALL VERIFY |
| FIX-093 | Frozen Python dependencies are bundled; no EXE-as-pip | requirements.txt, VideoHoarder.spec, app/app.py | `test_frozen_dependency_installers_do_not_invoke_exe_as_pip`; release source contract | PASS SOURCE / WINDOWS BUILD PENDING |
| FIX-094 | Visible Settings affect new job options | app/download_options.py, app/native_ui.py, app/download_workflows.py | `test_settings_map_to_job_options`; source contract | PASS |
| FIX-095 | One parser supports modern YouTube URL forms | app/youtube_url.py + consumers | `test_youtube_parser_supports_modern_video_forms`; watch+list/channel tests | PASS |
| FIX-096 | Windows reserved basenames are escaped | app/file_safety.py | `test_windows_reserved_names_are_escaped` | PASS |
| FIX-097 | Invalid config is visible, quarantined and privacy-safe | app/app.py, app/config.default.json | `test_corrupt_config_is_quarantined_and_safe_defaults_restored` | PASS |
| SEC-098 | Portable executable downloads are integrity-gated | app/app.py, config | `test_verified_portable_download_accepts_hash_and_rejects_wrong_hash`; policy tests | PASS |
| FIX-099 | Retry descriptors preserve types or are rejected | app/job_persistence_service.py | `test_retry_descriptor_rejects_arbitrary_objects_and_paths` | PASS |
| FIX-100 | Queue worker URL inputs do not overwrite canonical batch | app/app.py, app/native_ui.py | `test_managed_job_uses_its_own_urls_file_and_keeps_canonical_batch` | PASS |
| FIX-101 | File reports do not assume only port 8765 | app/app.py | `test_report_does_not_hardcode_only_8765` | PASS |
| GOV-102 | Code Parent is byte reproducible and portable | scripts/create_code_parent_package.py, wrapper/scripts | `test_code_parent_is_byte_reproducible_for_same_source`; package validation | PASS |
| GOV-103 | Feature IDs unique; one authoritative prompt | FEATURE_INVENTORY.md, app/prompts | `test_feature_inventory_ids_are_unique`; `test_duplicate_prompt_copy_removed` | PASS |
| ARCH-104 | Reduce duplicate config/dependency sources | app/app.py, app/dependency_service.py | Phase-F contracts + full suite | IMPLEMENTED IN TOUCHED DOMAINS |

| FIX-105 | Residual archive/legacy collisions must never discard different content | app/app.py, app/file_safety.py | `test_transcript_cleanup_preserves_equal_size_different_content`, `test_temp_transcript_move_preserves_equal_size_different_content`, `test_phase2_legacy_migration_preserves_different_content` | PASS |
| SEC-106 | YouTube-specific/cookie behavior must reject lookalike hosts | app/youtube_url.py, app/download_access.py | `test_youtube_host_detection_rejects_lookalike_domains` | PASS |
| FIX-107 | Windows reserved device-name variants must be safe | app/file_safety.py | `test_windows_reserved_names_with_spaces_before_extension_are_escaped` | PASS |
| FIX-108 | Native Settings choices/text must match actual default behavior | app/native_ui.py | `test_native_settings_do_not_offer_audio_as_video_quality_and_privacy_text_matches_default` | PASS SOURCE / WINDOWS UI PENDING |
| FIX-109 | OAuth/dependency help must be portable | app/app.py | `test_oauth_help_is_portable_not_d_drive_specific` | PASS |
| GOV-110 | Pristine handoff regeneration must preserve config schema | scripts/create_code_parent_package.py | `test_pristine_code_parent_preserves_full_config_example_schema`; package validator | PASS |

| FIX-111 | Keep EXE file smaller without removing features | 11 | VideoHoarder_onedir.spec; BUILD_SMALL_EXE.ps1 | onedir EXE/COLLECT build | test_issues8_build_size_contract.py | Phase 11 HTML | COMPLETE (Windows execution pending) |
| FIX-112 | Refresh all figures appears in Queue | 11 | app/native_ui.py | CommandCenter._refresh_all_figures | test_issues8_regressions.py | Phase 11 HTML | COMPLETE |
| FIX-113 | Deleted physical video removed from normal DB/library state | 11 | app/app.py | reconcile_active_library_state | test_issues8_regressions.py | Phase 11 HTML | COMPLETE |
| FIX-114 | Completed/running Media job does not remain at 0% | 11 | app/app.py | run_download_with_progress; web_media_only_download | test_issues8_regressions.py | Phase 11 HTML | COMPLETE |
| FIX-115 | Job Details is discoverable | 11 | app/native_queue_page.py | NativeQueuePage._show_job_details | test_issues8_regressions.py | Phase 11 HTML | COMPLETE |
| FIX-116 | Code Parent wrapper portable/accurate | 11 | CREATE_CODE_PARENT_PACKAGE.bat | wrapper | test_issues8_regressions.py | Phase 11 HTML | COMPLETE |
