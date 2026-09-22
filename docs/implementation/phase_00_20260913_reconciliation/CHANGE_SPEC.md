# Phase 0 Change Specification — 2026-09-13 Reconciliation

Requirements: GOV-001, GOV-002, TEST-005.

## Current behavior / problem
- Governance evidence exists but Phase 03/04 history was not completely reflected in master/index/traceability records.
- The Code Parent archive could contain files not reproducible from the included generator; `docs` was not an explicit source item and live configuration could be copied.
- `BUILD_WINDOWS.ps1` used unittest discovery, collecting only the unittest subset rather than all pytest-style tests.

## Required behavior
- Preserve historical evidence but expose one coherent current baseline and open finding state.
- One generator must deliberately include governance docs, exclude runtime/build/cache/user data, generate sanitized templates and validate a hash manifest against the archive.
- pytest must be the canonical build gate; Phase 0 does not change the launcher/release artifact contract.

## Rollback
Restore the prior packager and build-test command. Application runtime behavior is otherwise unchanged in Phase 0.
