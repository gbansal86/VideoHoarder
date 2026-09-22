# Phase 06 Rollback / Failure Rule

If any final validation fails, do not publish a phase-complete status. Reopen the introducing phase, fix the regression, update its evidence, rerun that phase plus all relevant previous phases, then repeat Phase 06. Windows-only failures must be repaired on Windows and followed by the same cumulative gate before release-complete status.
