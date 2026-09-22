# External Services

Recorded: 2026-08-15

| Service/tool | Use | Status |
|---|---|---|
| YouTube pages/Data API | source/playlist/channel metadata and categories | IMPLEMENTED / network untested |
| yt-dlp or compatible executable | metadata, captions, media download | IMPLEMENTED / runtime untested |
| FFmpeg/FFprobe | media validation/processing/clips | IMPLEMENTED / runtime untested |
| `youtube-transcript-api` | transcript fallback/retrieval | IMPLEMENTED / runtime untested |
| Ollama loopback API | local generation and library Q&A | IMPLEMENTED / runtime untested |
| ChatGPT website | manual package upload and result return | MANUAL EXTERNAL STEP; retained |
| OpenAI Responses API | optional one-video-at-a-time transcript intelligence using the same package/validation contract | IMPLEMENTED; disabled by default; live network call not performed in source QA |
| Selenium + browser drivers | selected subscriptions/browser workflows | IMPLEMENTED / runtime untested |
| Windows Explorer/default apps | open local artifacts/folders | IMPLEMENTED / not exercised |

Network/service behavior, quotas, authentication failures, provider changes, and offline recovery were not tested in this reconciliation.

## Runtime availability check - 2026-08-24

- Ollama executable/process: not available in the checked environment.
- YouTube credential file: present outside the repository; its contents were not read and it remains excluded from Git.
- YouTube, yt-dlp, transcript-provider, FFmpeg, Selenium and ChatGPT exchange behavior: not invoked during this input check.
- Manual ChatGPT package exchange remains usable in principle without granting the application direct ChatGPT credentials, but no representative package/result fixture was available for an end-to-end run.


### OpenAI provider boundary - 2026-09-22

- API key value comes only from an environment variable; configuration stores the variable name, not the secret.
- Normal transcript packages are allow-list driven and exclude descriptions/comments/raw format inventories/local paths.
- One VIDEO_ID is submitted per model call.
- `store=false` is the default provider setting.
- Private/unlisted/restricted video submission is blocked by default and requires explicit opt-in.
- Returned API JSON is still imported through VideoHoarder's existing deterministic validator and manual review gate.
