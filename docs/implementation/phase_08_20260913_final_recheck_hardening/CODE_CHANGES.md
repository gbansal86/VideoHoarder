# Code Changes — Phase 08

## FIX-081
Replaced the shared `job_queue_state.json.tmp` writer with `tempfile.mkstemp()` + `os.replace()` under a dedicated re-entrant lock.

## FIX-082 / PERF-083
`queue_payload()` now always persists recoverable rows and applies `limit` only to completed history. A restart-specific field whitelist excludes full `result` payloads and unrelated internal fields.

## BUILD-084
The frozen runtime hook no longer scans parent folders for `.videohoarder-build`; it resolves PySide6/Shiboken from the bundled `_MEIPASS` runtime only.

## PERF-085
Added `LRUCache(max_items=256)` and applied it to native Library and Queue thumbnail caches.

## FIX-086
Added legacy `mediaSrt` control and forwarded `save_srt` in the `/api/job-start` payload.

## DOC-087
Corrected the desktop README to the actual one-file release and optional `-Deploy` behavior; regenerated final validation for the current revision.
