# Code Changes

- `app.py` baseline: 28,939 lines; final: 28,850 lines. New feature logic was extracted rather than accumulated in the monolith.
- Resolver checkbox now calls one workflow that optionally resolves each URL and then invokes the selected Full Library or Media Only downloader.
- Resolver is decomposed into host/player plugins and a bounded traversal engine.
- YouTube access ladder and metadata extraction can retry with browser cookies when a persisted config lacks cookie arguments and YouTube returns access/403/login errors.
- Native queue now separates Name and Type, attaches thumbnail metadata, and maintains batch metadata for “done / left / running”.
- Library browser overlays live SQLite state over Phase-5 indexed documents before sorting/filtering.
- Failure aggregation/CSV cleanup moved to a focused service; current-failure API has no default artificial cap.
- Dashboard failure metric reflects current unresolved video failures, not historical failed-job logs.
