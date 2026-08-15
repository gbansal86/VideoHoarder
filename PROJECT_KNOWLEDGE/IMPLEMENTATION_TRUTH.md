# Implementation Truth

Recorded: 2026-08-15

The source contains substantial implementations, but only the explicitly tested subset is VERIFIED. All other code-present capabilities remain IMPLEMENTED IN SOURCE / NEEDS REVIEW until exercised with controlled data.

## Verified

- Source compilation.
- Dashboard server startup and progress endpoint.
- Root override and canonical health-file migration behavior.
- ChatGPT checksum/provenance/timestamp/planner validation.
- Duplicate review records do not delete files.
- Clip plan creates a manual handoff and does not execute media changes.
- Installed EXE equals local distribution EXE by SHA-256.

## Partial

- Central artifact manifest: table and helper functions exist; proposed authoritative lifecycle, reconciliation, history, UI, atomic exports, and command-wide integration are not complete.
- Automated test coverage: focused tests pass but do not represent the complete feature surface.
- Git handoff: initial repository baseline is implemented; pre-baseline history is unavailable and remote push verification is recorded separately.

## Needs review

Downloads, transcripts, reports, populated-library workflows, taxonomy apply/undo, imports, collection AI, recovery, external media, subscriptions, installed GUI behavior, and destructive operations.

## Discussed but not implemented

Full Central Artifact Manifest proposal: Discussed YES; Implemented NO (PARTIAL foundation only).
