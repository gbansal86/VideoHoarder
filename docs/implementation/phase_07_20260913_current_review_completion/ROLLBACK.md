# Rollback

Revert the Phase 07 files listed in `FILES_CHANGED.md`. Delete `job_queue_state.json` only if explicitly discarding restart-recovery history; it contains no required library content. Re-run the pre-Phase-07 full suite and package tests after rollback.
