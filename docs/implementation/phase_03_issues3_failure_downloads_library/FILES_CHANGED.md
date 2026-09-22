# Files Changed

| File | Change Type | Requirement | Reason |
|---|---|---|---|
| app/current_failure_registry.py | Added | REQ-020/021, ARCH-003 | Unified video/job failure register and safe failed-job dismissal/archive |
| app/failure_service.py | Modified | REQ-021 | Stable CSV failure keys and exact deletion for no-VIDEO_ID failures |
| app/native_failure_page.py | Modified | REQ-020/021/022 | Complete failure list and visible per-row Delete action |
| app/native_library_page.py | Modified | REQ-018/019 | Larger thumbnails and new sort choices |
| app/library_browser_service.py | Modified | REQ-019 | Category sorting |
| app/native_ui.py | Modified | REQ-023 | Downloads sidebar item and workflow navigation |
| app/gui.py | Modified | REQ-023 | Route Downloads to existing `/app?tab=downloads` page |
| app/app.py | Modified | REQ-020/021 | Thin wrappers for unified failure rows/count/delete |
| tests/test_gui_issue_fixes.py | Modified | All | Regression tests for issue 3 services/navigation |
| tests/test_native_ui.py | Modified | REQ-018/019/022/023 | Native widget contract tests |
