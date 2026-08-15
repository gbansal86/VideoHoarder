# Data Model

Recorded: 2026-08-15

The audited `data/database/video_library.db` is SQLite, 102,400 bytes, and contains zero rows in every application table. Schema evidence is therefore VERIFIED; production data behavior is UNKNOWN.

| Table | Purpose | Status |
|---|---|---|
| `videos` | VIDEO_ID identity, source metadata, taxonomy, artifact paths, transcript/report/comments, user state, failure and ChatGPT fields | IMPLEMENTED; broad denormalized table |
| `video_artifact_manifest` | per-VIDEO_ID JSON snapshot plus `scanned_at` | PARTIAL foundation for proposed central manifest |
| `transcript_availability` | availability/source/check time/detail/preflight association | IMPLEMENTED for package routing |
| `chatgpt_requests` | request/package identity, versions, hashes, manifest, lifecycle/result/application state, notes | IMPLEMENTED |
| `chatgpt_request_videos` | request-to-video evidence snapshot and requested features | IMPLEMENTED |
| `video_feature_coverage` | per-video feature/version/package/result status | IMPLEMENTED |
| `chatgpt_import_field_history` | proposed field/action audit rows | IMPLEMENTED / PARTIAL lifecycle |
| `external_media` | non-library media download records | IMPLEMENTED |
| `youtube_subscriptions` | collected channel/subscription metadata | IMPLEMENTED |
| `clip_projects` | clip project definition/output/status | IMPLEMENTED |

Schema creation/evolution occurs inside `db_connect()` with `CREATE TABLE IF NOT EXISTS`, column inspection, and `ALTER TABLE`; no ordered migration framework or schema-version table was found.

The proposed central manifest is NOT IMPLEMENTED as authoritative normalized lifecycle storage: it lacks dedicated artifact/change-history schema, schema version, command-wide incremental updates, atomic master exports, completeness profiles, and reconciliation metadata.
