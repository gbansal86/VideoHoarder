# Rollback — Phase 08

Rollback is code-only; no database migration is introduced. Revert the Phase 08 files listed in `FILES_CHANGED.md`. Existing `job_queue_state.json` schema-1 files remain loadable because restore logic consumes the same `jobs`/`tasks` structure. If rollback is needed, stop VideoHoarder first so no queue-state writer is active, restore files, and rerun the Phase 07 cumulative suite.
