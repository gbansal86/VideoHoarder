# Git Handoff Recommendation

Recorded: 2026-08-15

The initial `main` baseline and remote are established. Continue with these controls:

1. Keep credentials, media, runtime databases, logs, browser profiles, caches, builds, and temporary output excluded.
2. Review `git status` and the intended diff before every commit.
3. Run relevant tests and credential scanning before push.
4. Use descriptive commits and update `GIT_STATE.md`, `SOURCE_VERSION.md`, implementation truth, and the session log.
5. Protect `main` on GitHub when collaboration begins; prefer pull requests for risky changes.
6. Store release binaries in GitHub Releases or another artifact store rather than normal Git history.
7. Never force-push, rewrite history, or commit secrets without explicit owner direction and a documented recovery plan.
