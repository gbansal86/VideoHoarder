# Rollback

Restore the Phase 02 / v4 versions of the modified files listed in FILES_CHANGED.md and remove `app/current_failure_registry.py`. Dismissed queue-job logs are moved to `logs/runs/archive/`; rollback does not need to delete them.
