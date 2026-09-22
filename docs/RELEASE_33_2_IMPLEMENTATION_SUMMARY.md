# VideoHoarder 33.2 — local-video import implementation

## Changes

- Dedicated **Import Local Videos** browser page and desktop navigation route; legacy YouTube library import remains unchanged.
- Safe read-only scan of files/folders, selected references/copies/explicitly confirmed moves, local identity, idempotent registration and optional FFprobe metadata.
- Records are added to SQLite with `platform=local`, empty source URL, concrete `local_video`, and `local_video_imports` provenance table. Records may be played through the existing local media endpoint.
- Matching `.srt`, `.vtt` and timestamped-transcript sidecars produce a local cached canonical speech-text candidate; original sidecars remain untouched.
- The existing transcript package's preflight never attempts YouTube retrieval for local video IDs. No API request, transcription, file rename or metadata apply is triggered during import.
- Reconciliation verifies an imported local video against its **exact path** and marks unavailable local media inactive instead of running YouTube deletion/purge logic.
- Release metadata, docs, CI and focused regression tests updated.

## Boundaries

Automatic speech-to-text when no sidecar exists is not included. Browser-to-OS file picker is not used because a browser cannot grant arbitrary hard-drive access; users paste an existing local path. Batch scan is capped at 10,000 videos per run. FFprobe is optional. No real Windows `.exe` was built or physical Windows drive tested in this review; build from source on Windows.

For installation and use see [LOCAL_VIDEO_IMPORT.md](LOCAL_VIDEO_IMPORT.md).
