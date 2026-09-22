# Code Changes — Phase 02

- `physical_downloaded_today_count()` added to the existing modular `library_stats_service.py`; generic job success is no longer a Dashboard completion metric.
- `queue_wait_message()` added to `download_queue_service.py` to make queue reason deterministic/testable outside Qt.
- `web_job_snapshot(job_id=None, limit=60)` retains the legacy default while allowing `limit=None` for the dedicated Queue page and duplicate guard.
- `redownload_history_check()` now merges physical-library/deletion history with all current session queued/running/recent-success job identities.
- `/api/job-start` enforces duplicate confirmation server-side for Full Library and Media Only, so UI preflight cannot be bypassed by a race or direct request.
- Legacy Downloads JavaScript now relies on the backend confirmation response and resubmits only after user confirmation.
- Successful Retry is protected in backend and both native Queue/Dashboard UIs; legacy queue manager also prompts before confirming the retry.
- Full Library `process_download()` writes canonical `downloaded_at` when media exists.
- Dashboard `Refresh all figures` now runs as an independent background `FunctionTask`, not a managed download job.
- Stats refresh uses pending + in-flight target tracking so a completion event arriving during an existing stats read schedules a second fresh read instead of being lost.
