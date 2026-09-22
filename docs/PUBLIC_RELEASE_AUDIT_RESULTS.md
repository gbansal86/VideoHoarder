# Public source audit and regression results — 2026-09-22

This document describes the **new sanitized source distribution only**, not the history/content already visible in the existing public GitHub repository.

- OpenAI provider preserved, `openai_api_enabled=false` by default; no personal API key or paid API request is required.
- Manual processing and local Ollama continue to work independently of OpenAI API credentials.
- Live configuration, `library_root.txt`, runtime SQLite, local logs, browser/session/cookie files, builds, downloads, media, archives, and ChatGPT exchange folders are excluded.
- Historic machine-specific documentation paths have been replaced with `<VIDEOHOARDER_HOME>` placeholders.
- `specs/evidence/` with actual video/transcript captures is excluded; synthetic integrity fixtures remain.
- Staged public release privacy/secret scan: PASS (0 findings).
- Focused public package / API tests: PASS.
- Complete source regression: **345 passed, 22 skipped, 0 failed** on the available Linux test host.
- Archive content SHA-256 validation: performed by `scripts/create_code_parent_package.py` on each generated clean handoff.
- Paid live OpenAI request: **not performed**; provider transport tested with fake SDK/client.
- Windows executable build and Windows smoke tests: **not performed** in this environment; required before a binary release.
- Historical public Git commits and currently published exchange packages: **not audited or changed** by this source package. Review them separately prior to announcing the public repository as sanitized.

For step-by-step maintainer instructions see `docs/PUBLIC_RELEASE_CHECKLIST.md`.
