# Change Index

| Change ID | Requirement ID | Phase | Feature/Fix | Files Changed | Status | Test Report | Git Checkpoint |
|---|---|---|---|---|---|---|---|
| ISSUE6-001 | FIX-601 | 01 | Job Details layout | app/native_ui.py | Implemented; Windows UI verification required | phase_01_issue6_completion/TEST_RESULTS.html | N/A (no .git) |
| ISSUE6-002 | REQ-602 | 01 | Duplicate download confirmation | app/download_guard_service.py, app/app.py, app/native_ui.py | Implemented | phase_01_issue6_completion/TEST_RESULTS.html | N/A |
| ISSUE6-003 | FIX-603 | 01 | Library count refresh after completion | app/native_ui.py, app/library_stats_service.py, app/app.py | Implemented | phase_01_issue6_completion/TEST_RESULTS.html | N/A |
| ISSUE6-004 | REQ-604 | 01 | Queue scrollbars + refresh | app/native_ui.py, app/native_queue_page.py | Implemented; Windows UI verification required | phase_01_issue6_completion/TEST_RESULTS.html | N/A |
| ISSUE6-005 | ARCH-605 | 01 | Dedicated Queue page | app/native_queue_page.py, app/gui.py | Implemented; Windows UI verification required | phase_01_issue6_completion/TEST_RESULTS.html | N/A |
| ISSUE6-006 | FIX-606 | 01 | Explain why jobs are queued | app/native_ui.py, app/native_queue_page.py | Implemented | phase_01_issue6_completion/TEST_RESULTS.html | N/A |
| ISSUE6-007 | FIX-607 | 01 | Refresh figures after physical deletion | app/library_stats_service.py, app/app.py, app/native_ui.py | Implemented | phase_01_issue6_completion/TEST_RESULTS.html | N/A |
| ISSUE6-008 | FIX-609 | 01 | Restore build integrity fixture | tests/fixtures/chatgpt_integrity/... | Implemented | final_validation/FINAL_TEST_RESULTS.html | N/A |
| ISSUE6-009 | DOC-608 | 01 | Restore governance evidence | docs/implementation/* | Implemented | final_validation/FINAL_TEST_RESULTS.html | N/A |

| V7-001 | FIX-701 | 02 | Refresh figures independent of download queue | app/native_ui.py | Implemented; Windows verify | phase_02_v7_completion/TEST_RESULTS.html | N/A |
| V7-002 | REQ-702 | 02 | Canonical duplicate/re-download guard across native/legacy/backend/retry | app/download_guard_service.py, app/app.py, app/native_ui.py, app/native_queue_page.py | Implemented | phase_02_v7_completion/TEST_RESULTS.html | N/A |
| V7-003 | FIX-703 | 02 | Lossless pending stats refresh | app/native_ui.py | Implemented; Windows verify | phase_02_v7_completion/TEST_RESULTS.html | N/A |
| V7-004 | FIX-704 | 02 | Physical Completed Today metric | app/library_stats_service.py, app/app.py, app/native_ui.py | Implemented | phase_02_v7_completion/TEST_RESULTS.html | N/A |
| V7-005 | FIX-705 | 02 | Persist Full Library downloaded_at | app/app.py | Implemented | phase_02_v7_completion/TEST_RESULTS.html | N/A |
| V7-006 | FIX-706 | 02 | Precise queue wait reason | app/download_queue_service.py, app/native_ui.py | Implemented | phase_02_v7_completion/TEST_RESULTS.html | N/A |
| V7-007 | FIX-707 | 02 | Unlimited dedicated Queue snapshot | app/app.py, app/native_queue_page.py | Implemented | phase_02_v7_completion/TEST_RESULTS.html | N/A |
| V7-008 | DOC-708 | 02 | Correct/expand governance evidence | docs/implementation/* | Implemented | final_validation/FINAL_TEST_RESULTS.html | N/A |

| FIX-REFRESH-001 | REQ-REFRESH-001 | Phase 03 | Refresh all figures runtime constructor fix | `app/native_ui.py`, `tests/test_v7_completion.py` | VALIDATED (native Windows click-through pending) | `phase_03_refresh_figures_runtime_fix/TEST_RESULTS.html` | not created in this environment |

| ISSUES3-018 | REQ-018 | Historical Phase 03 | Larger Library thumbnail | app/native_library_page.py | Implemented historically | phase_03_issues3_failure_downloads_library/TEST_RESULTS.html | N/A |
| ISSUES3-019 | REQ-019 | Historical Phase 03 | Library Video/Channel/Category sorts | app/native_library_page.py, app/library_browser_service.py | Implemented historically | phase_03_issues3_failure_downloads_library/TEST_RESULTS.html | N/A |
| ISSUES3-020 | REQ-020 | Historical Phase 03 | Unified current-failure register | app/current_failure_registry.py, app/app.py | Implemented historically | phase_03_issues3_failure_downloads_library/TEST_RESULTS.html | N/A |
| ISSUES3-021 | REQ-021 | Historical Phase 03 | Delete/dismiss every current failure | app/failure_service.py, app/current_failure_registry.py | Implemented historically | phase_03_issues3_failure_downloads_library/TEST_RESULTS.html | N/A |
| ISSUES3-022 | REQ-022 | Historical Phase 03 | Visible Delete next to failures | app/native_failure_page.py | Implemented historically | phase_03_issues3_failure_downloads_library/TEST_RESULTS.html | N/A |
| ISSUES3-023 | REQ-023 | Historical Phase 03 | Downloads navigation tab | app/native_ui.py, app/gui.py | Implemented historically | phase_03_issues3_failure_downloads_library/TEST_RESULTS.html | N/A |
| ISSUES3-ARCH | ARCH-003 | Historical Phase 03 | Keep failure logic outside app.py | app/current_failure_registry.py | Implemented historically | phase_03_issues3_failure_downloads_library/TEST_RESULTS.html | N/A |
| CLEANUP-041 | FIX-041 | Historical Phase 04 | Failure count/list consistency | failure registry/UI | Implemented historically | phase_04_failure_cleanup_consistency/TEST_RESULTS.html | N/A |
| CLEANUP-042 | FIX-042 | Historical Phase 04 | Complete unresolved failure list | failure registry/UI | Implemented historically | phase_04_failure_cleanup_consistency/TEST_RESULTS.html | N/A |
| CLEANUP-043 | FIX-043 | Historical Phase 04 | Delete action on each failure | native failure UI | Implemented historically | phase_04_failure_cleanup_consistency/TEST_RESULTS.html | N/A |
| CLEANUP-044 | FIX-044 | Historical Phase 04 | Stable-key delete for non-video/job failures | failure service | Implemented historically | phase_04_failure_cleanup_consistency/TEST_RESULTS.html | N/A |
| CLEANUP-ARCH | ARCH-045 | Historical Phase 04 | Feature logic outside app.py | failure service modules | Implemented historically | phase_04_failure_cleanup_consistency/TEST_RESULTS.html | N/A |
| VH0-G01 | GOV-001 | Phase 0 (2026-09-13) | Reconcile governance truth | docs/implementation/* | Implemented in Phase 0 | phase_00_20260913_reconciliation/TEST_RESULTS.html | N/A (no .git) |
| VH0-G02 | GOV-002 | Phase 0 (2026-09-13) | Reproducible/sanitized Code Parent | scripts/create_code_parent_package.py, tests/test_code_parent_package.py | Implemented in Phase 0 | phase_00_20260913_reconciliation/TEST_RESULTS.html | N/A |
| VH0-F05 | TEST-005 | Phase 0 (2026-09-13) | pytest becomes canonical Windows build gate | BUILD_WINDOWS.ps1 | Implemented in Phase 0 | phase_00_20260913_reconciliation/TEST_RESULTS.html | N/A |

| VH1-F01 | FIX-101 | Phase 01 (2026-09-13) | Scoped job cancellation | job execution service + app wrappers | Implemented | phase_01_20260913_job_contract/TEST_RESULTS.html | N/A |
| VH1-F02 | FIX-102 | Phase 01 (2026-09-13) | Truthful zero-result Full Download | app workflow accounting | Implemented | phase_01_20260913_job_contract/TEST_RESULTS.html | N/A |
| VH1-F06 | FIX-103 | Phase 01 (2026-09-13) | Current transfer progress | job progress contract | Implemented | phase_01_20260913_job_contract/TEST_RESULTS.html | N/A |
| VH1-F12 | ARCH-104 | Phase 01 (2026-09-13) | Immutable per-job options | `download_options.py`, job context | Implemented | phase_01_20260913_job_contract/TEST_RESULTS.html | N/A |
| VH2-F13 | FIX-201 | Phase 02 (2026-09-13) | Settings validation/atomic persistence | `settings_service.py` | Implemented | phase_02_20260913_safety_integrity/TEST_RESULTS.html | N/A |
| VH2-F14 | SEC-202 | Phase 02 (2026-09-13) | Local mutation authorization | `local_api_security.py` | Implemented | phase_02_20260913_safety_integrity/TEST_RESULTS.html | N/A |
| VH2-F15 | SEC-203 | Phase 02 (2026-09-13) | Strict JSON mutation parsing | HTTP mutation handler | Implemented | phase_02_20260913_safety_integrity/TEST_RESULTS.html | N/A |
| VH2-F16 | FIX-204 | Phase 02 (2026-09-13) | Correct byte-range parsing | `http_range.py` | Implemented | phase_02_20260913_safety_integrity/TEST_RESULTS.html | N/A |
| VH2-F17 | FIX-205 | Phase 02 (2026-09-13) | Atomic metadata migration | `metadata_migration.py` | Implemented | phase_02_20260913_safety_integrity/TEST_RESULTS.html | N/A |
| VH3-F04 | FIX-301 | Phase 03 (2026-09-13) | Saved download defaults | native UI | Implemented; Windows verify | phase_03_20260913_native_ui_contract/TEST_RESULTS.html | N/A |
| VH3-F07 | FIX-302 | Phase 03 (2026-09-13) | Cancel one vs Stop All | native UI | Implemented; Windows verify | phase_03_20260913_native_ui_contract/TEST_RESULTS.html | N/A |
| VH3-F09 | FIX-303 | Phase 03 (2026-09-13) | Global notification surface | native shell | Implemented; Windows verify | phase_03_20260913_native_ui_contract/TEST_RESULTS.html | N/A |
| VH4-F03 | BUILD-401 | Phase 04 (2026-09-13) | Standalone release contract | build scripts/spec/self-test | Implemented in source; Windows execute pending | phase_04_20260913_release_contract/TEST_RESULTS.html | N/A |
| VH4-F05 | TEST-402 | Phase 04 (2026-09-13) | Complete pytest/native release gate | `BUILD_WINDOWS.ps1` | Implemented in source | phase_04_20260913_release_contract/TEST_RESULTS.html | N/A |
| VH5-F08 | SCALE-501 | Phase 05 (2026-09-13) | Server/SQLite Library pagination | `library_pagination.py`, native Library, API | Implemented | phase_05_20260913_scale_ai_correctness/TEST_RESULTS.html | N/A |
| VH5-F10 | AI-502 | Phase 05 (2026-09-13) | Embedding identity fingerprint | `ai_cache_identity.py`, Phase-6 embeddings | Implemented | phase_05_20260913_scale_ai_correctness/TEST_RESULTS.html | N/A |
| VH5-F11 | AI-503 | Phase 05 (2026-09-13) | Evidence-aware Local AI answer cache | `ai_cache_identity.py`, answer cache | Implemented | phase_05_20260913_scale_ai_correctness/TEST_RESULTS.html | N/A |

| VH-P7 | FIX-071..078 | Phase 07 | Current review completion | `app.py`, media/job services, native UI/library, GUI, launcher/build, tests | COMPLETE (Windows packaged execution pending) | `phase_07_20260913_current_review_completion/TEST_RESULTS.html` | N/A (no .git) |

| VH08-081 | FIX-081/FIX-082/PERF-083 | Phase 08 | Durable/complete/compact queue recovery | `job_persistence_service.py` | COMPLETE (source) | `phase_08_20260913_final_recheck_hardening/TEST_RESULTS.html` | Git N/A |
| VH08-084 | BUILD-084 | Phase 08 | Frozen bundled Qt identity | runtime hook | COMPLETE SOURCE / WINDOWS PENDING | same | Git N/A |
| VH08-085 | PERF-085 | Phase 08 | Bounded native thumbnail caches | native Library/Queue | COMPLETE (source) | same | Git N/A |
| VH08-086 | FIX-086 | Phase 08 | Legacy Media Save-SRT parity | legacy Downloads | COMPLETE (source) | same | Git N/A |
| VH08-087 | DOC-087 | Phase 08 | Current README/final validation | docs | COMPLETE | same | Git N/A |
| P09-091 | FIX-091 | Phase 09 | Content-safe filesystem dedupe | app/file_safety.py, app/app.py | PASS | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-092 | FIX-092 | Phase 09 | Installed writable-state boundary | app/app.py | PASS | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-093 | FIX-093 | Phase 09 | Frozen dependency packaging/no frozen pip | requirements.txt, VideoHoarder.spec, app/app.py | PASS source contract / Windows build pending | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-094 | FIX-094 | Phase 09 | Visible Settings → immutable job options | app/download_options.py, app/download_workflows.py, app/native_ui.py, app/app.py | PASS | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-095 | FIX-095 | Phase 09 | Canonical YouTube URL parser | app/youtube_url.py, download guard/queue/app | PASS | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-096 | FIX-096 | Phase 09 | Windows reserved filename safety | app/file_safety.py, app/app.py | PASS | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-097 | FIX-097 | Phase 09 | Corrupt config quarantine/privacy-safe restore | app/app.py, app/config.default.json | PASS | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-098 | SEC-098 | Phase 09 | Integrity-gated executable downloads | app/app.py, app/config.default.json | PASS | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-099 | FIX-099 | Phase 09 | Strict retry descriptor types | app/job_persistence_service.py | PASS | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-100 | FIX-100 | Phase 09 | Per-job URL input isolation | app/app.py, app/native_ui.py | PASS | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-101 | FIX-101 | Phase 09 | Dynamic report local-server fallback | app/app.py | PASS | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-102 | GOV-102 | Phase 09 | Deterministic portable Code Parent | scripts/create_code_parent_package.py, wrappers/scripts | PASS | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-103 | GOV-103 | Phase 09 | Feature inventory/prompt cleanup | docs/implementation/FEATURE_INVENTORY.md, app/prompts | PASS | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |
| P09-104 | ARCH-104 | Phase 09 | Reduce config/dependency source drift | app/app.py, app/dependency_service.py, app/config.default.json | IMPLEMENTED; monolith debt remains incremental | phase_09_20260914_fresh_audit_fixes/TEST_RESULTS.html | N/A |

| P10-105 | FIX-105 | Phase 10 | Content-safe residual transcript/legacy merges | app/app.py | Implemented | phase_10_repeat_ten_pass_hardening/TEST_RESULTS.html | N/A |
| P10-106 | SEC-106 | Phase 10 | Exact YouTube host/cookie-fallback classification | app/youtube_url.py, app/download_access.py, app/app.py | Implemented | phase_10_repeat_ten_pass_hardening/TEST_RESULTS.html | N/A |
| P10-107 | FIX-107 | Phase 10 | Windows reserved-name spacing variants | app/file_safety.py | Implemented | phase_10_repeat_ten_pass_hardening/TEST_RESULTS.html | N/A |
| P10-108 | FIX-108 | Phase 10 | Native Settings quality/privacy contract | app/native_ui.py | Implemented | phase_10_repeat_ten_pass_hardening/TEST_RESULTS.html | N/A |
| P10-109 | FIX-109 | Phase 10 | Portable OAuth/dependency guidance | app/app.py | Implemented | phase_10_repeat_ten_pass_hardening/TEST_RESULTS.html | N/A |
| P10-110 | GOV-110 | Phase 10 | Pristine full-schema Code Parent config example | scripts/create_code_parent_package.py | Implemented | phase_10_repeat_ten_pass_hardening/TEST_RESULTS.html | N/A |

| PH11-111 | FIX-111 | 11 | Small-EXE onedir build | VideoHoarder_onedir.spec; BUILD_SMALL_EXE.* | COMPLETE | phase_11_issues8_regressions/TEST_RESULTS.html | pending Windows tag |
| PH11-112 | FIX-112 | 11 | Queue Refresh all figures | app/native_ui.py | COMPLETE | phase_11_issues8_regressions/TEST_RESULTS.html | pending Windows tag |
| PH11-113 | FIX-113 | 11 | Purge physically deleted library videos | app/app.py | COMPLETE | phase_11_issues8_regressions/TEST_RESULTS.html | pending Windows tag |
| PH11-114 | FIX-114 | 11 | Job-scoped Media/Audio progress | app/app.py | COMPLETE | phase_11_issues8_regressions/TEST_RESULTS.html | pending Windows tag |
| PH11-115 | FIX-115 | 11 | Explicit Job Details dialog | app/native_queue_page.py | COMPLETE | phase_11_issues8_regressions/TEST_RESULTS.html | pending Windows tag |
| PH11-116 | FIX-116 | 11 | Portable Code Parent wrapper | CREATE_CODE_PARENT_PACKAGE.bat | COMPLETE | phase_11_issues8_regressions/TEST_RESULTS.html | pending Windows tag |
