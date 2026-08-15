# VideoHoarder Master Codex Instructions

Recorded: 2026-08-15
Status: Master operating instruction
Scope: audit, development, Git, packaging, validation, and continuous project memory

Canonical human-readable source: `D:\YT GUi\specs\currentversion\VideoHoarder_Master_Codex_Git_Project_Instructions.docx`. This Markdown record is the repository-operational version.

## Operating responsibility

The coding agent is responsible for both requested implementation work and trustworthy long-term handoff. The next developer or AI must be able to determine what exists, what changed, what remains, what is broken, where code lives, which Git revision represents it, and what should happen next without relying on old chats.

## Non-negotiable rules

- Current code is implementation truth. Documentation is context until verified.
- Inspect and reuse existing implementations; do not create competing systems because a request uses different wording.
- Classify every relevant capability as IMPLEMENTED, PARTIAL, MISSING, NEEDS REVIEW, DEPRECATED, or BLOCKED and cite code/test evidence.
- A discussed feature or written plan is not implemented.
- Preserve user data. Do not silently download, delete, move, rename, overwrite, reprocess, or expose it.
- Never record secrets, credentials, API keys, tokens, private certificates, or recovery codes.
- Do not silently change unrelated behavior.
- Record exactly what remains whenever work is incomplete.
- Update affected project knowledge, tests, source version, Git state, and the session handoff after meaningful work.

## Audit scope

Before major implementation, inspect UI/screens, backend/services, jobs/queues, SQLite/schema/recovery, APIs, external integrations, video/media storage, transcripts/SRT/VTT, metadata/comments, YouTube integration, taxonomy, collections, ChatGPT packages, tag cleanup, Knowledge AI/indexing/embeddings, imports/exports, configuration, security, logs, errors, tests, deployment, manifests, checkpoints, and overlapping systems.

Evidence should name exact files, functions/classes, routes, tables, APIs, tests, and observed behavior. Never infer runtime success solely from code presence.

## Living knowledge system

Maintain the canonical files indexed by `README.md`. Extend existing records instead of adding competing documents. Each record should answer its relevant subset of:

- What the application is and who it serves.
- What is implemented and verified today.
- What is partial, blocked, deprecated, missing, or untested.
- Where the code and data live.
- How workflows and data flow operate.
- What changed recently and at which Git revision.
- What is broken or risky.
- What should be improved next.
- Which decisions were made and why.

## Implementation truth

For meaningful features record purpose, status, exact code evidence, UI/backend/database/test/documentation status, limitations, and opportunities. If only discussed, state `Discussed: YES; Implemented: NO`.

## Independent improvement discovery

Inspect for missing functionality, duplication, fragile architecture, data consistency risks, security/privacy issues, performance bottlenecks, confusing UX, weak validation, missing tests/monitoring/recovery, prompt/version weaknesses, avoidable API cost, manual work, and package traceability gaps.

Do not automatically implement discretionary discoveries. Record them in `quality/IMPROVEMENT_OPPORTUNITIES.md` as REQUIRED FOR CURRENT TASK, RECOMMENDED IMPROVEMENT, FUTURE IDEA, or POTENTIAL RISK.

## Video and ChatGPT package lifecycle

Reuse existing package, request, coverage, audit, and artifact systems. Track exact VIDEO_ID, evidence availability, package/request identifiers, grouping/batch identity, checksums, creation/sent/returned/imported/reviewed/applied state, feature coverage, and regeneration reason. Do not repackage completed features unless evidence or processing version changed or the user explicitly requests it.

Treat YouTube category as evidence rather than an automatic skip rule. Keep transcript-backed and no-transcript workflows distinct. Validate imports before application and retain per-video/package processing history. Physical rename, move, delete, cut, or merge must remain explicitly reviewed and authorized.

## Central Artifact Manifest constraint

Extend the existing `video_artifact_manifest` SQLite table and `artifact_inventory()`, `artifact_manifest_for_video()`, and `build_video_artifact_manifest()` systems. Do not create a competing inventory.

The proposed feature remains PARTIAL until it provides schema/version and refresh metadata, per-artifact states and identity, ChatGPT lifecycle, incremental command updates, change history, staleness/reconciliation, completeness/next actions, atomic JSON/CSV exports, UI/verification actions, interruption recovery, broad tests, and installed-runtime verification.

Manifest maintenance must never silently download, rename, move, or delete files.

## Git discipline

Git is source-history truth; `PROJECT_KNOWLEDGE` is project-understanding truth. Before commits, review intended files, check secrets/large artifacts, run relevant tests, update documentation, and use a descriptive message. Record the resulting SHA.

Never add, commit, push, merge, delete branches, reset, rewrite history, or force-push without authorization. Preserve `.gitignore` exclusions for credentials, user inputs, media, runtime databases, logs, builds, releases, browser profiles, caches, and temporary output.

## End-of-session handoff

Update `sessions/YYYY-MM-DD.md` with objective, areas inspected, files changed, completed/partial/missing work, tests and results, database/configuration changes, branch/commit/working tree, bugs/limitations, discoveries, and recommended next action.

## Five-pass self-check

1. Scope and completeness: reconcile the request with actual implementation and status.
2. Code and architecture: check duplication, dependencies, assumptions, state/races, and regression risk.
3. Data/package integrity: check VIDEO_ID mapping, schemas, fingerprints, manifests, imports/exports, duplicate prevention, and history.
4. UI/workflow: exercise relevant screens, actions, validation/error states, filters, edit/notes, and handoff visibility.
5. Tests/documentation: run relevant tests and reconcile all affected knowledge and Git/source records.

## Definition of done

Done means implemented in code, verified by relevant testing, and reflected in project knowledge. Documentation-only completion is not implementation. One happy-path test is insufficient for imports, batching, AI packages, duplicate prevention, or persistent state. Known limitations remain visible.

## Final response format

Report COMPLETED, IN PROGRESS, NOT IMPLEMENTED, BUGS FOUND, TESTS, DOCUMENTATION UPDATED, GIT STATE, NEW IDEAS DISCOVERED, and RECOMMENDED NEXT ACTION.
