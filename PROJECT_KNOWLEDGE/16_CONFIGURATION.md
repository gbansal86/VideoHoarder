# Configuration

Recorded: 2026-08-15

`app/config.json` covers roots/folders, download quality/content, concurrency/timeouts/retries, transcripts/languages, YouTube API/tool behavior, title/report rules, Ollama, Phase 0-6 controls, ChatGPT package folders/schema/batching/import/cleanup, repair/recovery, and dashboard behavior.

`VLM_LIBRARY_ROOT` overrides runtime root and is test-verified. `youtube_data_api_key` is empty in the tracked config; `youtube_api_key_file` points to external storage. Values are never recorded in project knowledge.

Status: configuration loading and root override VERIFIED; broad setting behavior PARTIAL/UNKNOWN. `web_config_update()` requires a dedicated allow-list/sensitive-field review. There is no environment-specific schema validation or generated config reference.
