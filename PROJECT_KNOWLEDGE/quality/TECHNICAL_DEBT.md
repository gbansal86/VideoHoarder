# Technical Debt

- Approximately 22k-line `app/app.py` mixes many architectural layers.
- Broad `except Exception: pass` patterns reduce error visibility.
- No Git repository or `.gitignore` baseline.
- Runtime/build/cache/browser artifacts coexist with source.
- Schema evolution is embedded rather than managed by a migration framework.
- Prompt definitions and UI markup are embedded in the main backend.
- Test coverage is small relative to feature count.
- ChatGPT Processing v3, legacy Phase 2, Phase 5 tag cleanup and Phase 6 taxonomy/intelligence use parallel lifecycle representations.
- Smart planning has validation and package creation but no manual group editor or KEEP/SKIP/REVIEW state model.
