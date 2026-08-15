# API Catalog

Recorded: 2026-08-15

The application uses a custom local `BaseHTTPRequestHandler`/`ThreadingHTTPServer`, not a public web API framework.

## Read/navigation endpoints

- Progress/jobs/config/tool catalog/diagnostics/dependencies/system health.
- Library browser/page/detail/suggestions, media/report/thumbnail serving.
- Failures, clips, external media, subscriptions, collections, Knowledge AI status/search.
- ChatGPT overview, selectors, history, coverage, review, and unprocessed packages.
- Pages: `/app`, `/chatgpt-processing`, `/oldimport`, `/repairdata`, `/knowledge`, video/report/media routes.

## Mutating endpoints

- Configuration save, stop/close sessions, Selenium setup, log cleanup.
- Job start/control, safe repair, taxonomy export/import/reapply/move/undo.
- Exchange upload/import, collection create/rename/delete/export, video state/delete marker.
- ChatGPT package creation, planner import/preview, one/many result import, CSV export, review decisions, duplicate review, clip validation/handoff, and unprocessed-package deletion.

## Findings

- Request bodies above 145 MB are rejected; UI notes a 100 MB per-file exchange limit.
- Many endpoint errors are converted to JSON with HTTP 400/409/500/503.
- Powerful endpoints assume a trusted local desktop boundary. A dedicated review is still needed for loopback binding, CSRF/local-browser threats, authorization, path traversal, file serving, and command dispatch.
- No API schema/OpenAPI document or endpoint-level automated coverage matrix exists.
