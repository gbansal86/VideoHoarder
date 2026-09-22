# File Inventory

Recorded: 2026-08-15

Git currently tracks 125 files at reconciliation start; untracked count was zero. The working directory also contains approximately 7,162 ignored files, including runtime/build/browser/QA data. Some ignored temporary LibreOffice/test directories deny enumeration; they are not tracked.

Tracked classes: runtime source, tests/intentional fixtures, build/install scripts, requirements, icons, specifications/checkpoints/future requests, selected design artifacts/tools, `.gitignore`, and `PROJECT_KNOWLEDGE`.

Ignored classes: secrets/user URL input, media/downloads/transcripts, `data/` and databases, logs/maintenance, build/dist/ZIP/environment, document QA, browser profiles/session state, Python caches, and test runtime output.

Repository completeness is suitable for source continuation, not production-data reproduction. Release executables belong in release/artifact storage rather than ordinary Git history.
