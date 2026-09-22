# Maintainer automation opportunities

VideoHoarder has a broad maintenance surface: native UI, local HTTP routes, job persistence, SQLite migrations, filesystem operations, source/downloader integrations, transcript evidence, semantic package contracts, security boundaries, and Windows packaging.

Automation should support maintainers rather than merge/release autonomously.

## Useful coding-agent / Codex-assisted workflows

- **Issue triage:** summarize a bug, find likely affected modules, identify existing tests/fixtures, and draft a reproduction plan.
- **PR review:** map the diff to architecture/data boundaries, flag persistence/filesystem/security risks, and identify missing regression tests.
- **Regression generation:** create focused tests for a confirmed bug before or alongside the fix.
- **Modularization:** extract cohesive logic from `app.py` while preserving compatibility wrappers and existing behavior.
- **Release validation:** compare version metadata/changelog/build scripts, review skipped/failing tests, and generate a maintainer checklist.
- **Security review:** inspect local HTTP mutation endpoints, path handling, archive import, subprocess execution, provider credential boundaries, and dependency changes.
- **Documentation traceability:** identify when code behavior changed without corresponding README/spec/project-knowledge updates.

## Human approval boundary

Automated agents should not:

- merge PRs without maintainer review;
- publish releases without maintainer approval;
- run destructive library operations;
- expose or request production API keys/cookies;
- send private user library content to external services merely for code maintenance.

These workflows are intentionally separate from VideoHoarder's runtime transcript-intelligence provider.
