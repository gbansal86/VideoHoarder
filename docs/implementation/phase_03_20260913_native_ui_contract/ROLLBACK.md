# Phase 03 Rollback

Revert coordinated native_ui.py/gui.py Phase-03 UI changes and `tests/test_phase3_native_ui_contract.py`. Backend Phase-01 scoped cancellation remains valid independently, but the UI should not be reverted to a misleading Stop-All-only running control without documenting that regression.
