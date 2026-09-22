# Code Changes

- `CommandCenter._refresh_all_figures`: now calls `web_start_job("Refresh all figures", refresh_dashboard_figures, True)`.
- `reconcile_active_library_state`: previously-downloaded missing managed-library videos are fully purged from normal DB/cache/index state while a minimal redownload guard is retained.
- `run_download_with_progress`: yt-dlp transfer percentages update the managed job's `transfer_percent`.
- `web_media_only_download`: emits managed batch progress at start/per-item/completion.
- `NativeQueuePage`: adds an explicit Job Details button and modal, also opened by row double-click.
- Added optional PyInstaller onedir build for a smaller executable file without changing the normal release.
