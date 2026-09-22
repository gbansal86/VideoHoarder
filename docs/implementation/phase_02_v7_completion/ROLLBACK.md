# Rollback — Phase 02

No database schema migration was added. To roll back, restore the v6 source files listed in `FILES_CHANGED.md` and remove `tests/test_v7_completion.py` plus this phase folder. Existing `downloaded_at` values written by v7 are valid pre-existing schema data and do not require destructive rollback. Preserve user library/database/media and configuration. Re-run the v6 test suite after rollback.
