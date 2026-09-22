# Phase 09 — Fresh 10-Pass Audit Fixes

## Scope
This phase implements the confirmed defects and hardening actions from the fresh ten-pass audit of `VideoHoarder_Code_Parent_FINAL_RECHECK_FIXED_2026-09-13.zip`.

## Requirement IDs
- FIX-091: content-safe duplicate detection for destructive filesystem merges.
- FIX-092: installed/frozen mode keeps mutable state under the writable data root.
- FIX-093: frozen release bundles Selenium and youtube-transcript-api and never invokes the frozen EXE as pip.
- FIX-094: visible Settings defaults map to immutable per-job download options.
- FIX-095: one canonical YouTube URL parser supports watch/youtu.be/shorts/embed/live/playlist/channel/handle/user forms.
- FIX-096: Windows reserved device names are sanitized.
- FIX-097: corrupt config is quarantined, surfaced, and reset from privacy-safe authoritative defaults.
- SEC-098: downloaded executable/tool payloads require configured SHA-256 unless the user explicitly opts into unverified downloads; automatic yt-dlp self-update is disabled by default.
- FIX-099: retry descriptors reject values that cannot round-trip through JSON without type coercion.
- FIX-100: managed per-job URL inputs do not overwrite the canonical pasted URL batch.
- FIX-101: generated report API fallback scans the configured local-server port range instead of hardcoding 8765.
- GOV-102: Code Parent ZIP is byte-reproducible for unchanged source content and handoff wrappers are path-portable.
- GOV-103: remove duplicate prompt copy and reconcile Feature Inventory IDs/classifications.
- ARCH-104: reduce configuration/dependency source-of-truth drift through authoritative `config.default.json` and centralized dependency discovery.

## Known limitations intentionally not converted into defects
- Queue terminal history remains capped at 100 entries after restart; all unfinished/recoverable jobs remain uncapped and durable.
- `app.py` remains a large legacy monolith. This phase extracts/hardens filesystem and URL domains and centralizes configuration/dependency discovery, but does not perform a risky wholesale rewrite.
- Windows-native/PySide/PyInstaller/live-network acceptance remains environment-specific and is not executed on this Linux host.
