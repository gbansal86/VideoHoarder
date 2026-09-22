# Architecture Notes

The main design rule for this phase is separation of concerns. `app.py` keeps compatibility entry points, while pure or focused logic lives in new modules that can be tested without the full GUI/runtime.

Flow after change:

`Native/Web URL input -> per-URL managed job -> optional resolver plugins -> effective final URL -> existing Full/Media downloader -> metadata updates current job -> queue renders thumbnail/name/type -> SQLite persists result -> Library overlays live SQLite state over search index.`

Failure flow:

`SQLite current failure + current failure CSVs -> failure_service -> Failure/Cleanup + dashboard count -> selective cleanup clears DB state and current CSV entries -> next refresh shows reduced count.`
