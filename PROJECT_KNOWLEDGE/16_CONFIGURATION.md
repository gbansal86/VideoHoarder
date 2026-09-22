# Configuration

Recorded: 2026-08-15

`app/config.json` covers roots/folders, download quality/content, concurrency/timeouts/retries, transcripts/languages, YouTube API/tool behavior, title/report rules, Ollama, Phase 0-6 controls, ChatGPT package folders/schema/batching/import/cleanup, repair/recovery, and dashboard behavior.

`VLM_LIBRARY_ROOT` overrides runtime root and is test-verified. `youtube_data_api_key` is empty in the tracked config; `youtube_api_key_file` points to external storage. Values are never recorded in project knowledge.

Status: configuration loading and root override VERIFIED; broad setting behavior PARTIAL/UNKNOWN. `web_config_update()` requires a dedicated allow-list/sensitive-field review. There is no environment-specific schema validation or generated config reference.

## Download concurrency (2026-09-19)

- `parallel_videos` (1-5, default 2) is the user-facing **Simultaneous downloads** value and controls full-download video-row concurrency.
- `concurrent_fragments` (1-16, default 4) is passed to yt-dlp as `--concurrent-fragments`; it accelerates fragment-based formats and does not split every possible media source.
- `workflow_workers` (1-5, default 4) controls generic queued workflow jobs independently from video concurrency.
- Legacy `workers` remains accepted for compatibility and other historical configuration consumers; it no longer controls the desktop workflow worker pool.
- `VLM_VIDEO_LIBRARY` now takes precedence over saved `video_library_dir`; this makes explicit portable/test/runtime overrides deterministic.
