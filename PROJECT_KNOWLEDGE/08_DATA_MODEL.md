# Data Model

SQLite tables: `videos`, `video_artifact_manifest`, `transcript_availability`, `chatgpt_requests`, `chatgpt_request_videos`, `video_feature_coverage`, `chatgpt_import_field_history`, `external_media`, `youtube_subscriptions`, and `clip_projects`.

The checked database has zero rows in every table. The `videos` table carries identity, taxonomy, paths, transcript/report references, comments, processing state, and ChatGPT package fields. The artifact manifest currently stores one JSON blob plus `scanned_at` per VIDEO_ID, which is insufficient for the full proposed lifecycle without schema/API evolution.

No formal migration framework was found; schema expansion is performed in `db_connect()` with `CREATE TABLE IF NOT EXISTS` and `ALTER TABLE` logic.
