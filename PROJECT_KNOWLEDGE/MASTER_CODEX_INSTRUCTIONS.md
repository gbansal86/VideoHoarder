# VideoHoarder Master Codex Instructions

Recorded: 2026-08-15
Status: Operating instruction

Canonical human-readable source: `VideoHoarder_Master_Codex_Git_Project_Instructions.docx`, retained beside this audit package.

## Core rules

- Treat current code as implementation truth and documentation as context until verified.
- Audit before implementation; reuse existing systems and do not create competing implementations.
- Classify capabilities as IMPLEMENTED, PARTIAL, MISSING, NEEDS REVIEW, DEPRECATED, or BLOCKED with exact evidence.
- Never claim completion from a plan or document alone.
- Preserve user data and do not silently rename, move, delete, overwrite, reprocess, or expose secrets.
- Keep project knowledge, tests, Git state, source version, and session handoff current after every meaningful change.
- Record improvements separately as REQUIRED FOR CURRENT TASK, RECOMMENDED IMPROVEMENT, FUTURE IDEA, or POTENTIAL RISK.
- Git operations require explicit authorization. Never automatically add, commit, push, merge, reset, rewrite history, or force-push.

## Required audit scope

Inspect UI, backend, jobs, database, APIs, integrations, storage, video/transcript artifacts, YouTube, ChatGPT packages, taxonomy, Knowledge AI, imports/exports, authentication/security, logging, testing, deployment, manifests, checkpoints, and documentation.

## Definition of done

Done means implemented in code, verified by relevant testing, reflected in project knowledge, and tied to an exact source/build state. Known limitations remain visible.

## Five-pass completion check

1. Scope and completeness.
2. Code and architecture.
3. Data and package integrity.
4. UI and workflow behavior.
5. Tests, documentation, session log, and Git/source state.

## Central artifact manifest constraint

Extend the existing `video_artifact_manifest` SQLite system and related functions rather than creating a competing inventory. Manifest maintenance must not download, rename, move, or delete files. The proposed full manifest remains not implemented until all relevant commands update it, required lifecycle/history/export behavior exists, tests pass, and the installed build is verified.
