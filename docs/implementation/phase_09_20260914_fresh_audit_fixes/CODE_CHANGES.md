# Code Changes

- Destructive file collision handling now hashes equal-sized files before deduplication. Different-content files are preserved under deterministic conflict names.
- `safe_name()` now protects Windows reserved basenames such as `CON`, `AUX`, `NUL`, `COM1`, and `LPT9`, including names with extensions.
- Frozen/installed mutable files (`urls.txt`, OAuth token, Program Files visible library fallback) now use the writable resolved data root.
- `config.default.json` is the authoritative default schema. Invalid `config.json` is quarantined and replaced with safe defaults; cookie fallback cannot silently switch to browser mode.
- Selenium and youtube-transcript-api are release dependencies. Frozen builds return an actionable missing-bundle error rather than executing `VideoHoarder.exe -m pip`.
- Native Settings now drive subtitle acquisition, Smart Resume and AI/fast-mode defaults through immutable `DownloadOptions`.
- One canonical YouTube parser is reused by queue/duplicate/API/direct-ID paths and supports `/live/`.
- Per-job URL files isolate queue workers; native batch submission writes the full canonical batch once before queue split.
- Portable executable downloads verify configured SHA-256 hashes; unverified downloads/updates are opt-in only.
- Retry descriptors reject non-JSON-native argument types instead of silently converting them to strings.
- Static report note-edit API fallback tries the actual configured server port plus the same +20 bind range used by the application.
- Code Parent generation normalizes archive root/timestamps and is byte-reproducible for unchanged content.
- Machine-specific D-drive defaults were removed from Code Parent/exchange helper scripts.
- Duplicate master-prompt copy removed.
- Dependency discovery delegates to `dependency_service.py`; the large in-code config duplicate was reduced to a small emergency bootstrap.
