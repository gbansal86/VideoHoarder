# Processing History

Recorded: 2026-08-15

Live history is unavailable in the audited empty DB. Implemented history surfaces include `chatgpt_requests`, `chatgpt_request_videos`, `video_feature_coverage`, `chatgpt_import_field_history`, Phase 2 history files, validated review JSON, decision/duplicate/clip records, package indexes, taxonomy processed-ID state, and combined CSV exports.

Lifecycle truth: v3 records created -> awaiting result/plan -> validated/partial/invalid -> review-only/not applied. Unprocessed package deletion is allowed only for `AWAITING_RESULT` with no result path and removes requested coverage rows while retaining a deletion note. Tag cleanup has backup/import behavior but no unified request/result state machine.

Audit activity created no real package, result, tag-cleanup import, reprocessing job, or physical application. Automated tests created synthetic temporary records only.
