# Architecture Decisions

## ADR-ISSUE6-01 — Separate Queue page
**Decision:** `Queue` now resolves to `NativeQueuePage`; Dashboard retains only its compact queue overview.
**Reason:** the supplied implementation mapped both navigation items to the same `CommandCenter` widget and only changed focus, which is why the user saw the same page.

## ADR-ISSUE6-02 — Duplicate guard outside app.py
**Decision:** duplicate-download rules live in `app/download_guard_service.py`; `app.py` keeps a compatibility wrapper.
**Reason:** avoid expanding the 28k-line monolith and ensure native/web surfaces can use one rule.

## ADR-ISSUE6-03 — Physical media is authoritative for Dashboard library count
**Decision:** `available_downloaded_videos` requires real media, not only `downloaded=1`.
**Reason:** stale database flags otherwise survive manual file deletion and leave Dashboard counts unchanged. Existing library-export compatibility semantics are preserved separately.

## ADR-ISSUE6-04 — Terminal jobs trigger stats refresh
**Decision:** the native Dashboard refreshes library stats when a job reaches a newer terminal timestamp.
**Reason:** the previous 45-second timer made successful downloads/rebuilds appear not to change counts.


## ADR-V7-01 — Server-side duplicate guard is authoritative
**Decision:** `/api/job-start` enforces duplicate confirmation for download actions; UI checks are convenience only.
**Reason:** prevents legacy/native parity drift and closes preflight race/direct-request bypass.

## ADR-V7-02 — Dashboard figures refresh bypasses download queue
**Decision:** native Refresh All Figures runs a background function task directly.
**Reason:** a diagnostic/refresh control must work precisely when the managed download queue is paused or blocked.

## ADR-V7-03 — Completed Today is a physical video metric
**Decision:** compute it from canonical `downloaded_at` plus physical media verification.
**Reason:** maintenance/rebuild job success must not inflate a user-facing video count.

## ADR-V7-04 — Lossless refresh coalescing
**Decision:** track requested target, in-flight target and pending refresh separately.
**Reason:** terminal state arriving during a stats read must trigger a second read rather than being marked refreshed before evidence exists.


## ADR-VH0-01 — Code Parent is a sanitized deterministic handoff
**Decision:** `scripts/create_code_parent_package.py` deliberately includes `docs`, excludes runtime/build/cache/browser/user data, replaces live configuration with templates, writes SHA-256 content hashes, and validates the ZIP against its embedded manifest before reporting success.
**Reason:** the reviewed Code Parent contents must be reproducible from the included generator and must not depend on accidental post-copy files or live machine state.

## ADR-VH0-02 — pytest is the canonical build gate
**Decision:** `BUILD_WINDOWS.ps1` runs `python -m pytest -q tests` after compile validation instead of unittest discovery.
**Reason:** the current repository contains pytest-style tests that unittest discovery does not collect; the release gate must cover the complete project test inventory.

## VH-AUDIT-20260913 decisions

### ADR-VH-01 — Job-owned execution state
Use immutable per-job DownloadOptions and JobContext cancellation/process ownership. Queue-wide Stop All remains explicit and separate. This prevents one job from mutating shared settings or cancelling unrelated queued work.

### ADR-VH-02 — Validate before mutation
Settings and localhost mutation APIs validate type/range/caller/body before changing memory, disk, database, or application state. Metadata migration uses per-video savepoints so a failed item is retryable without partial content commits.

### ADR-VH-03 — Separate development launcher from release
The Source/.videohoarder-build launcher is a development product. The normal Windows release builds the real GUI from VideoHoarder.spec and must pass an EXE-only clean-room self-test.

### ADR-VH-04 — Database-side Library pagination
The native Library consumes a page contract with authoritative total/count/filter/sort in SQLite rather than a 10,000-row client snapshot. Phase-5 search scores are joined through a temporary relation so ranked searches can exceed SQLite parameter limits.

### ADR-VH-05 — Derived AI caches are identity-bound
Embedding reuse requires matching backend/model/dimension/implementation identity and source hash. Local-AI answer reuse requires matching question, exact evidence content, prompt contract and generation settings. Derived caches are disposable and rebuildable.

### ADR-VH-06 — Platform evidence remains explicit
Linux validation may establish source/unit/integration/package evidence, but Windows-native PySide rendering and PyInstaller artifact execution remain NOT EXECUTED until run on Windows. No platform-blocked gate is inferred as PASS.


## ADR-VH-07 — Restart recovery is explicit, not automatic
Persist queue state, transform unfinished work to `INTERRUPTED` on startup, and require an explicit user retry. Do not silently resume external downloads after a process restart. Safe retry descriptors are omitted when sensitive mapping keys are detected.

## ADR-VH-08 — Queue must remain available when secondary pages fail
Attach the native Queue before other pages and isolate each `set_backend()` call. A Library/Settings/Failures initialization error must not hide a successfully submitted backend job.

## ADR-VH-09 — Full release retains QtWebEngine
The current full build keeps QtWebEngine because specialist/legacy pages still use embedded web content. EXE-size reduction must not remove those features silently; a future native-only/lite distribution should be a separate product contract.

## ADR-VH-10 — Recovery state is complete for unfinished work and bounded for history
**Decision:** Persist every recoverable job independent of terminal-history limits, store only restart-critical fields, and serialize unique-temp atomic writes.
**Reason:** A history cap must never discard unfinished work, result payloads do not belong in the recovery index, and concurrent status writers must not share one temp filename.

## ADR-VH-11 — Frozen release uses only bundled Qt
**Decision:** The PyInstaller runtime hook resolves Qt/Shiboken exclusively from `sys._MEIPASS`.
**Reason:** A self-contained release must execute the exact Qt runtime it ships. `.videohoarder-build` remains a build/development environment, not a runtime dependency.

## ADR-VH-12 — Native thumbnail caches are bounded
**Decision:** Native Library and Queue use a 256-entry LRU cache.
**Reason:** browsing a large library must not grow QPixmap memory without bound.

## Phase 09 fresh-audit decisions

### ADR-P09-01 — Hash before destructive dedupe
Equal size is never sufficient evidence to delete a colliding file. SHA-256 content equality is required.

### ADR-P09-02 — Installed executable directory is read-only
Frozen/installed user state is written under resolved writable `BASE`; CODE_ROOT is treated as resource/deployment location only.

### ADR-P09-03 — Canonical YouTube URL parser
Queue, duplicate guard and metadata-source logic consume `app/youtube_url.py` rather than independent regex sets.

### ADR-P09-04 — Frozen Python dependencies are bundled
The release must contain Selenium and youtube-transcript-api. Runtime pip through the frozen executable is forbidden.

### ADR-P09-05 — Executable tool downloads require integrity evidence
SHA-256 verification is required by default; unverified tool downloads/updates are explicit opt-in behavior.

### ADR-P09-06 — Canonical batch URL state is not worker scratch state
Managed jobs use per-job URL files; the user's batch `urls.txt` remains the submitted batch.

## Phase 10 repeat-audit decisions

### ADR-P10-01 — Duplicate evidence is content-based in every merge path
All destructive/skip decisions for colliding files use content equality, never byte length alone.

### ADR-P10-02 — YouTube host identity is centralized
YouTube-specific behavior, including browser-cookie fallback, consumes the canonical parsed-host predicate; substring matching and `str.lstrip("www.")` are prohibited.

### ADR-P10-03 — Handoff templates derive from authoritative defaults
`config.default.json` is the source for sanitized handoff examples. A live `config.json` is neither required nor consulted for schema generation.
