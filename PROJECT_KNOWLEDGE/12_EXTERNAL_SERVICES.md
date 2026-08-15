# External Services

Recorded: 2026-08-15

| Service/tool | Use | Status |
|---|---|---|
| YouTube pages/Data API | source/playlist/channel metadata and categories | IMPLEMENTED / network untested |
| yt-dlp or compatible executable | metadata, captions, media download | IMPLEMENTED / runtime untested |
| FFmpeg/FFprobe | media validation/processing/clips | IMPLEMENTED / runtime untested |
| `youtube-transcript-api` | transcript fallback/retrieval | IMPLEMENTED / runtime untested |
| Ollama loopback API | local generation and library Q&A | IMPLEMENTED / runtime untested |
| ChatGPT website | manual package upload and result return | MANUAL EXTERNAL STEP; no automatic upload |
| Selenium + browser drivers | selected subscriptions/browser workflows | IMPLEMENTED / runtime untested |
| Windows Explorer/default apps | open local artifacts/folders | IMPLEMENTED / not exercised |

Network/service behavior, quotas, authentication failures, provider changes, and offline recovery were not tested in this reconciliation.
