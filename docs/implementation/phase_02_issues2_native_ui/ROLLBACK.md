# Rollback

Restore the previous v3 AutoDeploy versions of:
- `app/gui.py`
- `app/native_ui.py`
- `app/library_browser_service.py`
- `tests/test_gui_issue_fixes.py`
- `tests/test_native_ui.py`

Remove:
- `app/native_library_page.py`
- `app/native_failure_page.py`

No database migration or persistent data transformation is introduced by Phase 02. Failure deletion remains an explicit user action using the existing cleanup function.
