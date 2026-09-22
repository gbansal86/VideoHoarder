# Architecture Notes

Decision: normal Library browsing and current Failure/Cleanup are native desktop pages rather than adding more HTML/JavaScript to `app.py`.

Rationale:
- user explicitly requested separate feature modules and a smaller/easier-to-understand architecture;
- the backend functions already exist and are reusable;
- routing native pages avoids duplicating backend logic while preventing further growth of the monolithic `app.py`;
- legacy web pages remain reachable for compatibility but are no longer the normal desktop route for Library or Failure/Cleanup.

`app.py` remains 28,850 lines after this phase; Phase 02 adds no new feature implementation to it.
