# VideoHoarder Project Knowledge Index

Recorded: 2026-08-15
Status: Active handoff index

This directory is the repository source of truth for project understanding, implementation status, decisions, quality findings, planning, and session continuity. Source code and tests remain the source of truth for actual implementation.

## Start here

1. `00_MASTER_CONTEXT.md` - product purpose, scope, and safety boundaries.
2. `01_PROJECT_STATUS.md` - current verified state and priorities.
3. `IMPLEMENTATION_TRUTH.md` - what is verified, partial, missing, or untested.
4. `SOURCE_VERSION.md` - source/build identity and hashes.
5. `GIT_STATE.md` - repository, branch, remote, and commit state.
6. `INITIAL_AUDIT_REPORT.md` - evidence and initial findings.
7. `sessions/2026-08-15.md` - latest session handoff.

## Canonical name mapping

The master instructions use numbered canonical records. Shorthand requests map as follows:

| Shorthand | Canonical record |
|---|---|
| `FEATURE_CATALOG.md` | `03_FEATURE_CATALOG.md` |
| `CODEBASE_MAP.md` | `06_CODEBASE_MAP.md` |
| `IMPROVEMENT_OPPORTUNITIES.md` | `quality/IMPROVEMENT_OPPORTUNITIES.md` |
| Session handoff | latest dated file under `sessions/` |

Do not create unnumbered duplicates. Extend the canonical record.

## Catalogs and system records

- `03_FEATURE_CATALOG.md`: feature-by-feature status and evidence.
- `04_SCREEN_CATALOG.md`: native and embedded workspace surfaces.
- `05_WORKFLOW_CATALOG.md`: end-to-end workflows and verification state.
- `06_CODEBASE_MAP.md`: source ownership and architectural hotspots.
- `07_ARCHITECTURE.md`: runtime architecture and boundaries.
- `08_DATA_MODEL.md`: SQLite tables and persistence observations.
- `09_API_CATALOG.md`: local HTTP surface.
- `10_AI_SYSTEM.md`: Ollama and manual ChatGPT package systems.
- `11_PROMPT_LIBRARY.md`: prompt/version ownership.
- `12_EXTERNAL_SERVICES.md`: YouTube, transcript, browser, and local tool integrations.
- `13_SECURITY.md`: trust boundaries and credential handling.
- `14_TESTING.md`: executed tests and gaps.
- `15_DEPLOYMENT.md`: Windows build and packaging.
- `16_CONFIGURATION.md`: configuration ownership and sensitive-capable settings.
- `17_FILE_INVENTORY.md`: repository/runtime file classes.

## Git and handoff

- `GIT_STATE.md`, `GIT_HISTORY.md`, `GIT_REPOSITORY_COMPLETENESS.md`, `GIT_HANDOFF_RECOMMENDATION.md`, and `SOURCE_VERSION.md`.
- `status/`: status-specific rollups.
- `quality/`: bugs, debt, security, performance, UX, and improvements.
- `planning/`: roadmap, ideas, future work, and open questions.
- `decisions/`: architectural decisions.
- `features/`: dated feature/audit records.
- `packages/`: ChatGPT package inventory and processing history.
- `sessions/`: dated handoffs.

## Update rule

After meaningful work, update affected catalogs, implementation truth, source/Git state, quality or planning records, and the dated session handoff in the same change. Never promote a feature from discussion to implemented without code and test evidence.
