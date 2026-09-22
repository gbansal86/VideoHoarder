# VideoHoarder V3.3.4 — VTT / Speech-Coverage Corrections

## Updated authoritative files

- `app/prompts/VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md`
- `specs/VIDEOHOARDER_ARCHITECTURE_V3_3_4_FINAL.md`
- `app/app.py`
- `tests/test_chatgpt_validation.py`

The corresponding files under `changed/` were synchronized byte-for-byte with the deployed copies.

## Main changes

1. Kept the one-VTT policy: English preferred; fallback language only when English is unavailable.
2. Strengthened deterministic WebVTT normalization for progressive/rolling YouTube captions.
3. Separated transcript usability, spoken-content completeness, and timestamp reliability.
4. Removed duration-only `CLEAR_MAJOR_TRUNCATION` behavior.
5. Added `LARGE_UNSUBTITLED_TAIL` / `END_COVERAGE_UNCERTAIN` for large media tails when later speech is unknown.
6. Added `CONFIRMED_MISSING_SPOKEN_CONTENT` only when independent evidence establishes that speech is actually missing.
7. Changed completeness states to `COMPLETE`, `LIKELY_COMPLETE`, `PARTIAL`, `UNKNOWN`, `NONE`; character count no longer proves completeness.
8. Stopped extending a final timestamp-only caption to full video duration when no source end timestamp exists.
9. Preserved FULL_INTELLIGENCE for usable speech even when exact timing is unavailable.
10. Confirmed missing spoken content remains semantically usable when appropriate but is also added to source repair/retranscription routing.
11. Added Master Prompt rules for source-coverage boundaries, caption-display artifacts, non-speech cues, and source-certainty preservation.
12. Added regression tests for rolling captions, large silent/unsubtitled tails, confirmed missing speech, long-but-unproven-complete transcripts, and near-edge timing.

## Validation

- `tests/test_chatgpt_validation.py`: 63/63 passed.
- Full repository suite: 130 passed, 3 skipped, 0 failed.
- Actual uploaded VTT corpus: 367/367 files normalized without exceptions.
