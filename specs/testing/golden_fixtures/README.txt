VIDEOHOARDER GRADE GOLDEN FIXTURES V1

Purpose:
Permanent BEFORE fixtures for cumulative Phase 0-9 regression testing.

Primary grade:
transcript_health_grade (A/B/C/D/F)

Contents:
- FIXTURE_MANIFEST.json / .csv
- grade_A .. grade_F folders
- CURRENT_VIDEO_OBJECT.json = exact current package video object
- FIXTURE_CONTEXT.json = grade/reason/package context and selection rationale

Rules:
1. Do not edit CURRENT_VIDEO_OBJECT.json.
2. Future phase outputs should be written separately and compared against these baselines.
3. Do not require byte-for-byte equality for fields intentionally changed by the new architecture.
4. Transcript evidence/health should remain invariant when only description, clean_title, source tags, source chapter names, or comments are changed.
5. Future normal transcript-intelligence packages must exclude D/F videos after grade normalization/routing is implemented.
