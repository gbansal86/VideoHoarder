# VideoHoarder Specification Index

## Authoritative current documents

Use these first:

1. `current/VIDEOHOARDER_METADATA_ARCHITECTURE_IMPLEMENTED_SPEC_V1.md`
   - Main source-of-truth for the metadata architecture actually implemented in code.
2. `current/VideoHoarder_Metadata_Architecture_IMPLEMENTED_SPEC_V1.docx`
   - Word version of the implemented specification.
3. `current/PHASE_0_TO_9_IMPLEMENTATION_PROGRESS.docx`
   - Full implementation/testing/failure/retest history.
4. `current/VideoHoarder_Phase9_Final_Acceptance.json`
   - Machine-readable final acceptance.
5. `current/VIDEOHOARDER_ARCHITECTURE_V3_3_4_FINAL.md`
   - Existing broader VideoHoarder architecture specification.
6. `../app/prompts/VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md`
   - Current ChatGPT processing prompt used by the app.

## Decisions

- `decisions/APPROVED_METADATA_DECISIONS_AND_REVIEW_V2.docx`
  - Approved user decisions + reviewer clarifications.
- `decisions/archive/ORIGINAL_METADATA_DECISIONS_WITH_MY_ANSWERS_V1.docx`
  - Earlier decision history retained for traceability.

## Plans

- `plans/SENIOR_ARCHITECT_METADATA_IMPLEMENTATION_PLAN_V1.docx`
- `plans/PHASED_IMPLEMENTATION_AND_GRADE_TEST_PLAN.docx`
- `plans/GRADE_GOLDEN_FIXTURE_SELECTION_V1.docx`

## Process

- `process/SENIOR_DEVELOPER_PHASED_IMPLEMENTATION_PROTOCOL.docx`
- `process/WORD_PROGRESS_AND_MINIMAL_CHAT_PROTOCOL.docx`

## Actual evidence

Open:
- `evidence/phase_0_to_9/index.html`

This contains the real Phase 0–9 input/output evidence pages.

## Reference documents

Reference product/master documents live in `reference/`.

### Rule for future changes

When code intentionally changes the implemented behavior:
1. update the implemented spec;
2. update/add executable tests;
3. update implementation changelog;
4. keep the current prompt/architecture synchronized where applicable.
