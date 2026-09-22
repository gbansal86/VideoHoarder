# Rollback

Revert the Phase 11 files listed in FILES_CHANGED.md. No database schema migration is introduced. The physical-deletion behavior affects rows only when a user requests a refresh/reconciliation and a previously downloaded managed-library video is physically absent; therefore testing should use a disposable library before Windows release acceptance.
