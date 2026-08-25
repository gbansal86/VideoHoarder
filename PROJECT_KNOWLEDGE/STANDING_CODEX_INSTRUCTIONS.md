# VideoHoarder — Standing Instructions for Every Future Codex Coding Session

> **THIS FILE IS MANDATORY.**
>
> Before every coding task:
> 1. Read this file.
> 2. Read `PROJECT_KNOWLEDGE/README.md`.
> 3. Read `PROJECT_KNOWLEDGE/IMPLEMENTATION_TRUTH.md`.
> 4. Read the latest session handoff.
>
> If these steps are skipped, the task is considered non-compliant.

## Purpose

VideoHoarder is a long-lived project. Git is the source of truth for code history and exact source state. `PROJECT_KNOWLEDGE` is the source of truth for project understanding, status, decisions, handoff, and discovered improvements.

Every meaningful coding session must leave the project in a state that another developer or AI can continue without relying on old chat history.

## 1. Before coding

Before changing anything:

1. Read:
   - `PROJECT_KNOWLEDGE/README.md`
   - `PROJECT_KNOWLEDGE/00_MASTER_CONTEXT.md`
   - `PROJECT_KNOWLEDGE/01_PROJECT_STATUS.md`
   - `PROJECT_KNOWLEDGE/IMPLEMENTATION_TRUTH.md`
   - `PROJECT_KNOWLEDGE/SOURCE_VERSION.md`
   - `PROJECT_KNOWLEDGE/GIT_STATE.md`
   - the latest `PROJECT_KNOWLEDGE/sessions/*.md`
   - the relevant feature/package/architecture documents
2. Inspect the actual source code.
3. Determine whether the requested feature already exists.
4. Reuse existing implementations where possible.
5. Do not create duplicate systems because the request uses different wording.

## 2. Implement the requested change

- Make the smallest safe change that satisfies the request.
- Preserve existing functionality.
- Do not silently change unrelated behavior.
- Follow the existing architecture and naming conventions.
- Add or update tests for changed behavior.
- Handle errors, edge cases, cancellation, retries, and duplicate processing where relevant.
- Protect secrets and private data.
- Do not add unnecessary dependencies.

## 3. Check for broader impacts

Before declaring completion, inspect whether the change affects UI, backend, database, APIs, AI workflows, package generation/import, VIDEO_ID processing history, configuration, tests, deployment/build, security, performance, or documentation. Update all affected areas.

## 4. Discover improvements, but don't silently expand scope

During every task, independently look for bugs, missing validation, duplicated code, performance problems, UX problems, security issues, reliability problems, missing tests, automation opportunities, scalability issues, and recovery weaknesses.

Record useful findings in the existing canonical `PROJECT_KNOWLEDGE/quality/IMPROVEMENT_OPPORTUNITIES.md`.

Do NOT implement unrelated discretionary improvements unless required for correctness, security, compatibility, or the requested feature.

## 5. Test before completion

Run relevant tests. Record the commands, passed, failed, skipped, and environment limitations. Never say “tested” unless the test was actually run. If runtime testing is unavailable, explicitly say so.

## 6. Update project knowledge in the same session

After implementing a meaningful change, update the existing canonical documentation, including affected status, feature, screen/workflow, code map, architecture, data model, API, AI, testing, implementation-truth, quality, and package records as applicable.

Do not create duplicate documentation files when a canonical file already exists.

## 7. Implementation truth

Update `PROJECT_KNOWLEDGE/IMPLEMENTATION_TRUTH.md` using:

- `IMPLEMENTED`
- `PARTIAL`
- `NOT IMPLEMENTED`
- `BROKEN`
- `UNKNOWN`
- `DEPRECATED`

Base status on actual code/tests/runtime evidence, not old chats or plans.

## 8. Session handoff

At the end of every meaningful coding session, create/update `PROJECT_KNOWLEDGE/sessions/YYYY-MM-DD.md` with objective, changes, files, completed/partial work, tests/results, bugs, limitations, new improvements, database/config changes, next action, and Git commit SHA.

## 9. Git workflow

After coding and testing:

1. Review `git status`.
2. Review `git diff`.
3. Include all necessary source, tests, project-knowledge, migrations, configuration, and build changes.
4. Ensure no secrets, credentials, private sessions, large media libraries, caches, or generated junk are committed.

Unless explicitly authorized, do NOT reset, force-push, rewrite history, delete branches, or merge unrelated branches.

## 10. Commit

When commit is authorized, use a descriptive commit message and update `PROJECT_KNOWLEDGE/GIT_STATE.md`, `PROJECT_KNOWLEDGE/SOURCE_VERSION.md`, and the session handoff with the new commit SHA.

## 11. Push to GitHub

When push is authorized, push to the correct branch, verify success, and report the branch, commit SHA, GitHub state, and working-tree state. Do not claim a successful push without verification.

## 12. What must be kept in Git

Git should contain the reproducible project state, including source code, tests, database migrations/schema, configuration templates, build/deployment scripts, `PROJECT_KNOWLEDGE`, specifications, and safe fixtures as appropriate.

Do NOT commit API keys, passwords, tokens, private certificates, browser sessions/cookies, `.env` files containing real secrets, large personal media libraries, temporary caches, dependency directories, build junk, or private databases.

## 13. Build and EXE

If a change affects the Windows application, update build configuration if needed, run the build when practical, and record build/version information. Do not claim EXE verification unless it was actually run.

## 14. Package and AI workflow changes

If a change affects ChatGPT/video packages, review/update package manifest, prompt/schema, evidence, checksum/integrity, batch state, processing history, result import, duplicate prevention, and reprocessing logic.

Track processing per `VIDEO_ID`.

Do not process an already-completed feature again unless source evidence changed or the user explicitly requested reprocessing.

## 15. Final response after every coding session

Always finish with:

```text
COMPLETED
IN PROGRESS
NOT IMPLEMENTED
FILES CHANGED
TESTS RUN
TEST RESULTS
PROJECT KNOWLEDGE UPDATED
GIT COMMIT
GIT PUSH
KNOWN LIMITATIONS
NEW IMPROVEMENTS DISCOVERED
RECOMMENDED NEXT ACTION
```

Be factual. Never claim completion when work is partial.

## 16. Most important rule

The project must remain self-documenting.

Every meaningful code change must leave behind:

```text
actual code
+
tests/evidence
+
updated PROJECT_KNOWLEDGE
+
session handoff
+
Git history
```

A future developer or ChatGPT session must be able to open the repository and understand what exists, what changed, what works, what does not work, what remains, and what should be done next.

## 17. Do not repeatedly ask for information already in the repository

Before asking the user for anything:

1. Search the repository.
2. Search `PROJECT_KNOWLEDGE`.
3. Inspect Git.
4. Inspect existing configuration/tests.
5. Inspect existing fixtures/examples.

Only ask the user when the information truly cannot be obtained from the project.

Do not repeatedly request documentation, audits, or inventories that already exist.

## 18. Future handoff rule

When another developer/ChatGPT takes over, they should be able to start from:

```text
GitHub repository
+
PROJECT_KNOWLEDGE
+
latest commit
+
latest session handoff
```

without needing the previous developer's chat history.
