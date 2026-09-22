# Change Log

## 2026-09-20 — Independent child-video controls
- Every concurrently scheduled full-download video now owns a separate cancellation/process context beneath its parent queue job.
- Job Details adds Pause video, Cancel video, and Resume/retry controls without changing the page structure.
- Cancelling one video terminates only that child's subprocesses; sibling downloads continue.
- Child source URLs, status, progress, and log paths persist, and unfinished children restore as `INTERRUPTED` after restart.
- Per-video events are mirrored into dedicated JSONL files while the parent run log remains complete.
- HTTP job control gained equivalent child actions for the legacy surface.
- Validation: **331 passed, 21 skipped, 0 failed**.

## 2026-09-20 — Five-video acceptance and remaining scheduler parity
- Legacy full-library rows now receive pre-seeded child state and their own child contexts.
- External-media downloads now own child contexts, progress rows, source/log identity, and cancellation-aware fallback behavior.
- Live acceptance used five short public-domain YouTube videos at 360p with five simultaneous videos and four concurrent fragments.
- Result: 5/5 `SUCCESS`, peak five running children, all five database rows `PASS`, all media non-empty and ffprobe-valid with audio/video streams, and five independent JSONL child logs.
- Final source suite: **332 passed, 21 skipped, 0 failed**.
- The live run exposed two transcript-dependent report checks displayed as `FAIL` when transcripts were disabled; they now correctly display `NOT REQUESTED` and are regression-tested.

## ISSUE6-20260911 — VideoHoarder Issue 6 completion
- Change size: MEDIUM.
- Baseline: supplied `VideoHoarder_Code_Parent(3).zip`.
- Fixed duplicate re-download confirmation across active library, deleted history, current queue, and repeated pasted URLs.
- Added dedicated native Queue page, explicit horizontal/vertical scrollbars, Refresh queue, and queued-wait explanations.
- Fixed Job Details narrow-layout clipping by stacking controls vertically.
- Dashboard library counts now refresh when terminal jobs complete and verify physical media presence for the visible Library count.
- Restored missing ChatGPT integrity test fixture.
- Restored implementation-governance evidence under `docs/implementation/`.
- Git checkpoint: NOT AVAILABLE — supplied ZIP contains no `.git` metadata.


## V7-20260911 — Re-audit completion
- Corrected v6 overclaim: legacy Downloads previously did not inspect current queue state; v7 canonical duplicate check now does.
- Refresh All Figures no longer enters the managed queue and therefore works when that queue is paused.
- Successful Retry now requires explicit re-download confirmation.
- Fixed terminal-stats refresh race with pending/in-flight targets.
- Completed Today now counts physical videos with canonical `downloaded_at` today rather than generic successful jobs.
- Full Library processing persists `downloaded_at` on successful media materialization.
- Queue wait reason is position/state-aware.
- Dedicated Queue page can retrieve all in-memory session jobs rather than the legacy 60-row snapshot cap.
- Expanded `FEATURE_INVENTORY.md` to the current major subsystem set and generated `FEATURE_GAP_REPORT.html`.
- Automated evidence: 127 tests OK, 19 skipped; compileall PASS.
- Git checkpoint: N/A — no `.git` metadata supplied.

## FIX-REFRESH-001 — Refresh all figures FunctionTask constructor mismatch
- Fixed native Dashboard `Refresh all figures` runtime TypeError caused by passing an unsupported third argument to `FunctionTask`.
- The full-rebuild flag is now passed through a zero-argument lambda compatible with the existing worker contract.
- Added AST regression coverage for all `FunctionTask(...)` constructor calls.
- Evidence: `phase_03_refresh_figures_runtime_fix/TEST_RESULTS.html`.

## 2026-09-13 — VH-AUDIT-20260913
- Phase 0: reconciled governance truth, sanitized/reproducible Code Parent creation, full pytest release gate.
- Phase 1: isolated job options/cancellation, truthful empty Full Download outcomes, corrected progress semantics.
- Phase 2: atomic settings, localhost mutation authorization, strict JSON, correct byte ranges, atomic metadata migration.
- Phase 3: Settings defaults propagation, Cancel One vs Stop All, shell-level status notices.
- Phase 4: true release build contract separated from development launcher; clean-room self-test contract added.
- Phase 5: >10k Library pagination and AI embedding/answer cache identity correctness.
- Phase 6: cumulative/failure/reproducibility validation and final governance reconciliation.
- Git checkpoint: N/A because the supplied source package contains no `.git` metadata.

## 2026-09-13 — Release runtime-data and Code Parent completeness correction [F03/G02]
- `VideoHoarder.spec` now bundles `app/prompts/VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md` into the frozen application.
- Code Parent generation now includes the development-launcher scripts and the package-creation BAT helper instead of silently dropping them.
- Added regression tests covering both the frozen runtime-data list and required handoff build scripts.


## 2026-09-13 — Phase 07 current-review completion [FIX-071..078]
- Media Only/Audio Only require a real non-empty output before success.
- Save SRT is forwarded and locally materialized from VTT when available.
- Queue state persists across restart; unfinished jobs restore as INTERRUPTED for explicit resume/retry.
- Dashboard and Queue use one progress algorithm.
- Native Library reads no longer execute on the Qt GUI thread.
- Queue backend attachment is first and failure-isolated.
- Frozen release self-test now covers backend readiness, Queue visibility/cancel, and restart recovery.
- Code Parent BAT reports the ZIP artifact that remains.

Final Phase 07 cumulative evidence: **266 passed, 21 skipped, 0 failed (287 collected)**. Windows packaged/PySide acceptance remains pending.

## 2026-09-13 — Phase 08 final recheck hardening [FIX-081..DOC-087]
- Removed queue-state shared-temp-file race with unique atomic temp files and serialized replacement.
- Recovery limits now apply only to completed history; all unfinished/interrupted jobs are preserved.
- Recovery state is compact and no longer stores full job result payloads.
- Frozen full release now resolves Qt/Shiboken only from its bundled PyInstaller runtime.
- Native Library/Queue thumbnail caches are bounded LRU caches.
- Legacy Media Only exposes/forwards Save SRT.
- Desktop README corrected to current one-file and optional-deploy behavior.
- Final validation regenerated for this exact source state; Windows-native/PyInstaller execution remains pending.

## 2026-09-14 — Phase 09 fresh 10-pass audit fixes [FIX-091..GOV-103 / ARCH-104]
- Replaced equal-size destructive dedupe with SHA-256 content equality and preserved conflicts.
- Moved installed-mode mutable URL/OAuth/library state to writable data roots and escaped Windows reserved names.
- Bundled Selenium/youtube-transcript-api for frozen releases; frozen EXE no longer attempts pip installation.
- Wired visible Settings through immutable per-job options (subtitles, Smart Resume, AI/fast mode).
- Added one canonical YouTube URL parser including `/live/` and explicit watch+list behavior.
- Corrupt config is quarantined and restored from privacy-safe authoritative defaults.
- Added SHA-256 integrity gating for portable executable downloads and disabled unverified auto-update by default.
- Retry descriptors reject type-coercing values.
- Isolated per-job URL inputs from canonical user batch state and removed fixed report-port fallback.
- Made Code Parent output byte-reproducible for unchanged source, portable across install paths, and removed duplicate prompt copy.
- Centralized config/dependency truth further into config.default/dependency_service.
- Source cumulative evidence: **305 passed, 21 skipped, 0 failed (326 collected)** before final package regeneration.

## 2026-09-14 — Phase 10 repeat ten-pass hardening [FIX-105..GOV-110 / DOC-111]
- Replaced the remaining size-only archive/migration duplicate decisions with SHA-256-backed content equality and unique conflict preservation.
- Corrected YouTube host parsing (`www.` prefix handling) and cookie-fallback classification so lookalike domains are rejected.
- Escaped Windows reserved stems with spaces before extensions.
- Aligned Native Settings and privacy text with actual behavior; kept Audio Only as a workflow.
- Removed machine-specific OAuth guidance and clarified verified-tool requirements.
- Made pristine Code Parent `config.example.json` derive from the full authoritative default schema and validate exact key parity.
- Cumulative evidence: 313 passed, 21 skipped, 0 failed before final package regeneration.

## Phase 11 — Issues 8 regression repair
- FIX-111: optional one-folder Small-EXE build added.
- FIX-112: Refresh all figures is now a visible managed Queue job.
- FIX-113: physically deleted downloaded videos are purged from normal DB/index state during reconciliation, retaining only the redownload guard.
- FIX-114: Media/Audio managed-job progress is updated from downloader progress and batch completion.
- FIX-115: Queue now exposes a dedicated Job Details dialog/button.
- FIX-116: Code Parent BAT wrapper is portable and reports the ZIP artifact.
- Full source suite: 320 passed, 21 skipped, 0 failed before final package proof.
