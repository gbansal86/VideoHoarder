# Phase 02 Rollback

Revert settings_service.py, local_api_security.py, http_range.py and coordinated changes in app.py/metadata_migration.py/tests. Restore all pieces together; otherwise the HTTP handler or settings path may reference missing validation helpers. Re-run full cumulative tests.
