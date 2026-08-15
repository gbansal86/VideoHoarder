# Configuration

Primary source config: `app/config.json`. It covers downloads, transcripts, AI/Ollama, ChatGPT packages, repair/recovery, folders, concurrency, retries, and UI/server behavior.

Sensitive-capable keys include `youtube_data_api_key` and `youtube_api_key_file`; values are intentionally omitted. Runtime/library root can be overridden through `VLM_LIBRARY_ROOT`, as verified by tests.
