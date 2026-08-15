# Technical Debt

- Approximately 22k-line `app/app.py` mixes many architectural layers.
- Broad `except Exception: pass` patterns reduce error visibility.
- No Git repository or `.gitignore` baseline.
- Runtime/build/cache/browser artifacts coexist with source.
- Schema evolution is embedded rather than managed by a migration framework.
- Prompt definitions and UI markup are embedded in the main backend.
- Test coverage is small relative to feature count.
