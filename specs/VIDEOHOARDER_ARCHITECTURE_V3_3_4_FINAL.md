# VideoHoarder — Token-Efficient High-Quality Processing Architecture V3.3.4 FINAL

## Version note

This V3.3.4 document contains the complete V3.3.3 Final Architecture plus the
V3.3.4 Transcript Health Analyzer, health-aware routing, Group Similar Videos
integration, and deterministic package-balancing architecture.

All V3.3.3 requirements remain authoritative unless an explicit V3.3.4 rule
below supersedes them.

## Goal

Build a permanent, high-quality video intelligence library while minimizing model-token usage.

The design is:

**One main AI pass per video → deterministic validation → optional targeted AI audit only when useful → save result or flag video for later package recreation → continue processing.**

Do **not** implement the five phases as five separate LLM calls.

---

## 1. Main processing flow

For every VIDEO_ID in a package:

1. Load authoritative metadata and allowed transcript evidence.
2. Make **one main LLM call** using `VIDEO_LIBRARY_MASTER_PROMPT_5_PHASE_OPTIMIZED.md`.
3. The model performs five internal phases in that one call:
   - Phase 1: Understand, clean and segment.
   - Phase 2: Detailed content intelligence.
   - Phase 3: Specialized extraction.
   - Phase 4: Library/search intelligence.
   - Phase 5: Semantic self-review.
4. Parse the returned structured JSON.
5. Run deterministic/code validation.
6. Decide whether a targeted Pass 2 is useful.
7. If no targeted review is needed, save the result.
8. If targeted review is useful, send only the affected result fields plus the smallest relevant transcript excerpts to Pass 2.
9. Apply Pass-2 patches to the Pass-1 JSON.
10. Run deterministic validation again.
11. Save the best available result and processing status.
12. Continue to the next VIDEO_ID regardless of whether this video passed.
13. At package end, write a reprocessing manifest containing only videos that should be packaged again.

---

## 2. Pass 1: one LLM call, five internal phases

### Important token rule

Do not call the model separately for each phase.

Wrong:

`transcript → phase1 call → phase2 call → phase3 call → phase4 call → phase5 call`

Correct:

`transcript → ONE model call containing the five-phase master prompt → final structured JSON`

The transcript is supplied once to the main call.

### Expected output

Keep the existing video-intelligence fields and add these internal quality fields:

```json
{
  "processing_status": "PASS",
  "processing_warnings": [],
  "reprocess_recommended": false,
  "reprocess_reasons": [],
  "uncertain_items": [],
  "targeted_review_hints": []
}
```

Allowed `processing_status` values:

- `PASS`
- `PASS_WITH_WARNINGS`
- `REPROCESS_RECOMMENDED`
- `SOURCE_INSUFFICIENT`

These fields are for the pipeline and must not become visible report sections.

---

## 3. Deterministic validation after Pass 1

Use normal code, not another model call, for checks that do not require semantic judgment.

Recommended checks:

### JSON/schema
- valid JSON
- expected VIDEO_ID
- required keys/types
- valid status enum
- arrays/objects have correct shapes

### Title
- original title matches authoritative metadata exactly
- New Title is nonempty
- Windows-invalid filename characters are absent from New Title
- no accidental VIDEO_ID insertion unless application rules require it
- length within configured filename limit

### Timestamps/chapters
- timestamps parse correctly
- timestamps are monotonic where required
- chapter start < chapter end
- no unintended chapter overlap
- timestamps do not exceed known transcript duration
- recipe/reference/Q&A timestamps are valid
- promotional ranges can be checked against any promo ranges identified by the model

### Formatting/data hygiene
- Named Items exists where required by schema
- Named Items is rendered last in HTML
- duplicate tags removed/detected
- duplicate named items detected
- duplicate recipes with same normalized name/range detected
- empty optional sections omitted from HTML
- no prohibited visible sections
- no `Source framing` text
- no individual recipe-step timestamps
- no obvious promotional URLs/coupon codes in report fields
- HTML rendering succeeds

### Important principle

Code validation should identify suspicious conditions but must not pretend to perform semantic verification that requires understanding the transcript.

---

## 4. Pass 2: targeted AI quality audit

Pass 2 is **not mandatory for every video**.

Its purpose is to cheaply inspect specific questionable parts rather than reprocess the full video.

### Trigger Pass 2 when useful

Examples:

- Pass 1 returns `PASS_WITH_WARNINGS` and the warning is resolvable from a small transcript range.
- `targeted_review_hints` contains specific timestamp ranges.
- a recipe has a suspicious/missing quantity, ratio, duration or frequency.
- a chapter boundary appears inconsistent.
- an important ASR term is uncertain and nearby context may resolve it.
- deterministic checks detect duplicate/conflicting structured information that requires semantic judgment.
- title/tags look weak enough that a small semantic correction can fix them.
- a meaningful reference may have been incorrectly extracted or omitted.
- promotional leakage is suspected in a specific range.

### Do not trigger Pass 2 merely because

- an optional section is empty.
- a video is simple.
- deterministic validation already proves the issue and code can fix it safely.
- the source itself is clearly insufficient and another model call cannot recover missing evidence.
- the video already has a clean `PASS`.

### Pass-2 input

Send:

1. VIDEO_ID.
2. Only the relevant Pass-1 JSON fields.
3. The exact warning/validation issue.
4. The smallest transcript excerpt(s) needed to resolve it.
5. The applicable master-prompt rules.

Avoid sending:

- the full transcript by default.
- unrelated report sections.
- descriptions/comments.
- the complete package.
- all other videos.

### Pass-2 output

Return **patches only**, not a full regenerated report.

Example:

```json
{
  "video_id": "Mu3vP4GfRE0",
  "patches": [
    {
      "path": "recipes[2].frequency",
      "action": "replace",
      "value": "Twice weekly; maximum three times weekly",
      "reason": "Transcript 09:33–09:50"
    }
  ],
  "remaining_warnings": [],
  "recommended_status": "PASS"
}
```

Your code applies validated patches to the Pass-1 result.

---

## 5. Never fail the package because of one video

This is a hard pipeline requirement.

Wrap processing at **VIDEO_ID level**, not package level.

Pseudo-flow:

```text
for video in package:
    try:
        result = run_pass_1(video)
        validation = validate(result)

        if should_run_targeted_pass_2(result, validation):
            patch = run_targeted_pass_2(...)
            result = apply_patch(result, patch)
            validation = validate(result)

        status = finalize_status(result, validation)
        save_video_result(result, status)

        if status requires reprocessing:
            add_to_reprocess_manifest(video, status, reasons)

    except video_specific_error:
        record SOURCE_INSUFFICIENT or REPROCESS_RECOMMENDED
        add_to_reprocess_manifest(...)
        continue

finalize_package()
```

A failure on video 7 of 12 must not prevent videos 8–12 from processing.

---

## 6. Reprocessing manifest

At the end of every package create both:

- `REPROCESS_MANIFEST.json`
- `REPROCESS_MANIFEST.txt`

Suggested JSON:

```json
{
  "source_package_id": "PACKAGE_ID",
  "total_videos": 12,
  "pass": 9,
  "pass_with_warnings": 1,
  "reprocess_recommended": 1,
  "source_insufficient": 1,
  "videos_to_repackage": [
    {
      "video_id": "VIDEO_ID",
      "status": "REPROCESS_RECOMMENDED",
      "reasons": [
        "Recipe timestamps could not be resolved reliably from supplied transcript."
      ],
      "recommended_source_improvement": [
        "Recreate transcript/SRT evidence for the affected range."
      ]
    }
  ]
}
```

Suggested text:

```text
PACKAGE PROCESSING SUMMARY
Package: PACKAGE_ID
Videos supplied: 12
PASS: 9
PASS_WITH_WARNINGS: 1
REPROCESS_RECOMMENDED: 1
SOURCE_INSUFFICIENT: 1

VIDEOS TO REPACKAGE

VIDEO_ID
Status: REPROCESS_RECOMMENDED
Reason: Recipe timestamps could not be resolved reliably.
Recommended action: Recreate transcript/SRT evidence for affected range.
```

Only `REPROCESS_RECOMMENDED` and `SOURCE_INSUFFICIENT` must automatically enter `videos_to_repackage`.

`PASS_WITH_WARNINGS` remains in the permanent result unless your own policy later decides a particular warning type requires recreation.

---

## 7. Preserve usable output for flagged videos

Do not throw away a partially useful intelligence record merely because it is flagged.

Recommended output structure:

```text
incoming/
  PACKAGE_ID/
    results/
      VIDEO_ID.json
      VIDEO_ID.html
    quality/
      VIDEO_ID.validation.json
    REPROCESS_MANIFEST.json
    REPROCESS_MANIFEST.txt
```

For `REPROCESS_RECOMMENDED`, keep the generated JSON/HTML clearly associated with its status so it can be replaced later.

For `SOURCE_INSUFFICIENT`, generate HTML only if enough reliable intelligence exists to make it useful. Otherwise keep the machine status/reason and move on.

---

## 8. Token-saving rules

1. One main LLM call per video.
2. Five phases happen inside that one call.
3. Never resend the transcript separately for each phase.
4. Do deterministic validation in code.
5. Do HTML generation in code.
6. Do schema validation in code.
7. Do filename validation in code.
8. Do duplicate detection in code where possible.
9. Run Pass 2 only when semantic correction is likely to help.
10. Pass 2 receives excerpts, not the full transcript by default.
11. Pass 2 returns patches only.
12. Never regenerate an entire good report just to fix one field.
13. Cache Pass-1 results so retries do not consume the main-call tokens again.
14. Store the exact prompt version/hash with every result.
15. Store transcript/source fingerprint/hash so unchanged evidence is not reprocessed unnecessarily.
16. If only HTML formatting changes, rerender from JSON without any LLM call.
17. If only deterministic rules change, migrate/revalidate JSON without an LLM call when safe.
18. Recreate packages only for VIDEO_IDs in the reprocessing manifest.

---

## 9. Recommended quality metadata stored with each result

Keep operational metadata separate from visible intelligence:

```json
{
  "processor": {
    "prompt_version": "5-phase-optimized-v1",
    "prompt_hash": "...",
    "source_fingerprint": "...",
    "pass_1_completed": true,
    "pass_2_used": false,
    "pass_2_ranges": [],
    "processing_status": "PASS",
    "processing_warnings": [],
    "reprocess_recommended": false,
    "reprocess_reasons": []
  }
}
```

This is important for a permanent library because you can later identify exactly which videos were processed with an older prompt and selectively regenerate them.

---

## 10. Package acceptance behavior

Package completion should mean:

> Every VIDEO_ID was attempted and received a recorded outcome.

It should **not** mean:

> Every VIDEO_ID must be perfect or the package fails.

Recommended package statuses:

- `COMPLETE` — every video attempted; no reprocessing required.
- `COMPLETE_WITH_REPROCESS_LIST` — every video attempted; one or more videos should be repackaged.
- `PACKAGE_INPUT_ERROR` — package itself cannot be read/parsed or required package-level structure is missing.

Only a genuine package-level input error should stop the package.

---

## 11. Important separation of responsibilities

### LLM / ChatGPT
Use for:
- semantic transcript understanding
- real chapter/topic boundaries
- detailed summarization
- recipe/reference/Q&A interpretation
- promotion recognition
- ASR uncertainty judgment
- search intelligence
- meaningful Named Items
- targeted semantic corrections

### Code / Codex
Use for:
- package parsing
- transcript extraction
- calling the model
- JSON parsing/schema checks
- timestamp arithmetic
- filename checks
- duplicate detection
- patch application
- status aggregation
- manifest creation
- JSON persistence
- HTML rendering
- retry/error handling
- caching/fingerprinting
- package recreation from flagged VIDEO_IDs

This separation minimizes Codex/model usage while preserving semantic quality.

---

## 12. Recommended implementation order

1. Replace the current master prompt with the new five-phase optimized prompt.
2. Extend output schema with processing-quality fields.
3. Make the per-video loop non-blocking.
4. Add deterministic validator.
5. Add status finalization.
6. Add reprocessing manifest generation.
7. Add targeted Pass-2 patch workflow.
8. Add caching and source/prompt fingerprints.
9. Make HTML renderer consume final JSON only.
10. Add package recreation command that accepts `videos_to_repackage`.
11. Test first on `Mu3vP4GfRE0`.
12. Test a simple video, a technical video, a poor-ASR video and a video with no recipes.
13. Compare token use, quality and reprocessing rate before running the full backlog.

---

## 13. Final architecture

```text
PACKAGE
  |
  +-- VIDEO 1
  |     |
  |     +-- Pass 1: ONE LLM call / five internal phases
  |     |
  |     +-- deterministic validation
  |     |
  |     +-- clean --------------------------> save
  |     |
  |     +-- targeted semantic issue
  |             |
  |             +-- Pass 2: excerpt + patch only
  |             +-- validate
  |             +-- save
  |
  +-- VIDEO 2 ... continue regardless of VIDEO 1 status
  |
  +-- VIDEO N
  |
  +-- package summary
  +-- reprocessing manifest
        |
        +-- only flagged VIDEO_IDs are packaged again later
```

This is the recommended balance for **minimum tokens + high semantic quality + a maintainable permanent video intelligence library**.


---

## 14. Sequential package execution — REQUIRED

Change the worker design from parallel processing to strict sequential processing.

```text
for video in package_order:
    finish video completely
    persist all section files
    persist assembled JSON/HTML
    record status
    then start next video
```

Do not use a worker pool for videos within the same package. Do not process
two package videos concurrently. Do not combine transcripts.

A bad video is recorded and the loop continues; it never aborts the package.

---

## 15. Persist Pass-1 output as modular section files

Pass 1 is still one model call. Code splits its result afterward.

```text
VIDEO_ID/
  source/source_manifest.json

  intelligence/
    01_title_search.json
    02_category.json
    03_tags.json
    04_chapters.json
    05_detailed_summary.json
    06_recipes.json
    07_references.json
    08_qa.json
    09_playlist_series.json
    10_technical_intelligence.json
    11_named_items.json

  quality/
    processing_quality.json
    validation.json
    section_status.json

  assembled/
    VIDEO_ID.json
    VIDEO_ID.html
```

### Why this is recommended

This gives the permanent library a stable, repairable source layer.

If only `06_recipes.json` is wrong:

1. leave all other section files untouched;
2. manually edit it, change it with deterministic code, or regenerate only
   that section from the relevant transcript excerpt;
3. validate recipe timestamps and dependencies;
4. rebuild `VIDEO_ID.json`;
5. rerender `VIDEO_ID.html`.

Manual/code-only repair uses **zero LLM tokens**.

### Section replacement modes

Store `generated_by` for each section:

- `pass_1`
- `pass_2`
- `manual`
- `code_migration`

Also store section status:

- `PASS`
- `PASS_WITH_WARNINGS`
- `REPLACE_RECOMMENDED`
- `EMPTY_BY_DESIGN`

### Dependency validation

A section can be replaced independently, but code must validate important
dependencies after replacement.

Examples:

- replacing Chapters -> validate Detailed Summary boundaries and all
  timestamped child sections;
- replacing Detailed Summary -> validate chapter coherence;
- replacing Recipes -> validate recipe timestamps and duplicate recipes;
- replacing Title/Category/Tags -> validate that search fields remain
  grounded in the assembled content;
- replacing Named Items -> validate final visible ordering and useful
  consistency with the report.

Do not automatically regenerate dependent sections. Flag them only when
there is a real dependency conflict.

---

## 16. Section-only semantic repair

When a section genuinely needs AI repair, do not rerun full Pass 1 by default.

Input to a section-repair call should contain only:

- VIDEO_ID;
- section name;
- current section JSON;
- exact problem/warning;
- minimum relevant transcript excerpts;
- required dependency context, such as chapter boundaries;
- only the master-prompt rules relevant to that section.

Output should be a replacement section or patch for that section only.

Then code validates, versions, replaces, reassembles and rerenders.

If the source evidence itself is inadequate, do not keep retrying the
section. Mark the VIDEO_ID for package/source recreation.

---

## 17. Updated final flow

```text
PACKAGE
  |
  +-- VIDEO 1
  |     Pass 1: one LLM call / five internal phases
  |       |
  |       +-- code splits output into section JSON files
  |       +-- deterministic validation
  |       +-- optional targeted Pass 2 / section repair
  |       +-- save section files
  |       +-- assemble final JSON
  |       +-- render HTML
  |       +-- record video/section statuses
  |
  +-- ONLY AFTER VIDEO 1 IS COMPLETE -> VIDEO 2
  |
  +-- repeat sequentially through VIDEO N
  |
  +-- package summary
  +-- reprocessing manifest
```

This intentionally favors deterministic recovery, section-level repair,
traceability and predictable token usage over parallel throughput.


---

## 18. Standard package size: 25 videos

Use a global minimum-package-count optimizer with a hard maximum of **30 videos per package**. There is no minimum package size; 25 is only an advisory target when equally efficient.

This does not mean 25 transcripts are sent to the model together.

The application must treat the package as an orchestration container only:

```text
PACKAGE (25 VIDEO_IDs)
    |
    +-- load VIDEO 1 only -> process -> persist -> checkpoint
    +-- load VIDEO 2 only -> process -> persist -> checkpoint
    +-- ...
    +-- load VIDEO 25 only -> process -> persist -> checkpoint
```

### Hard context-isolation rule

For every Pass-1 call, construct model input from only:

- current VIDEO_ID;
- current video's authoritative metadata;
- current video's allowed transcript/SRT evidence;
- the required master-prompt instructions.

Do not send:

- other videos' transcripts;
- already completed transcripts;
- future package transcripts;
- viewer comments/descriptions when prohibited by the master prompt;
- the complete 25-video package merely because it is available.

**Package size must never equal model context size.**

This keeps per-video semantic quality and token usage essentially
independent of whether the orchestration package contains 5, 12 or 25
videos.

### Exceptionally large videos

25 is an advisory target only, not a requirement that overrides practical
input limits. The package builder may create a smaller package when one
or more transcripts are exceptionally large or another operational
constraint makes that safer.

---

## 19. Checkpoint after every video

After every VIDEO_ID, atomically persist:

1. modular intelligence section files;
2. section metadata/status;
3. deterministic validation output;
4. processing-quality metadata;
5. assembled final JSON;
6. rendered HTML when applicable;
7. package progress/checkpoint state;
8. any reprocessing-manifest entry for that VIDEO_ID.

Only after persistence succeeds should the package advance to the next
VIDEO_ID.

Suggested checkpoint:

```json
{
  "package_id": "PACKAGE_ID",
  "package_size": 25,
  "last_completed_index": 17,
  "last_completed_video_id": "VIDEO_ID",
  "next_video_index": 18,
  "completed_video_ids": ["..."],
  "updated_at": "..."
}
```

Prefer a per-video state map in the real implementation so recovery does
not depend only on one index.

---

## 20. Resume without wasting AI tokens

On package restart:

1. read package checkpoint;
2. inspect persisted per-video status;
3. verify source fingerprint;
4. verify prompt/version compatibility;
5. verify required section files are present;
6. skip completed reusable VIDEO_IDs;
7. continue with the first unfinished or explicitly invalidated VIDEO_ID.

Example:

```text
25-video package interrupted after VIDEO 17

VIDEO 1-17 -> already persisted -> SKIP
VIDEO 18   -> resume processing here
VIDEO 19-25 -> continue sequentially
```

Do **not** rerun Pass 1 for videos 1–17 simply because the process
restarted.

If HTML rendering failed but the final section JSON is valid, rerender
HTML with code and consume zero LLM tokens.

If one modular section is invalid, follow the section-repair workflow
rather than rerunning the whole video by default.

---

## 21. Recommended package policy

```text
DEFAULT_PACKAGE_SIZE = 25
PROCESSING_MODE = sequential
CHECKPOINT_FREQUENCY = after_each_video
RESUME_MODE = first_unfinished_video
MODEL_CONTEXT_SCOPE = current_video_only
```

This is the recommended default for the permanent VideoHoarder library:
larger manageable packages, strict per-video isolation, deterministic
recovery, and no unnecessary token-consuming reprocessing.


======================================================================
V3 RENDERING + QUALITY IMPLEMENTATION REQUIREMENTS
======================================================================

The following requirements are now part of the approved architecture.

1. The semantic architecture remains unchanged:
   - one semantic model call per video
   - current-video-only context
   - code splits the result into authoritative modular section JSONs
   - deterministic JSON assembly and HTML rendering
   - optional targeted Pass 2 only for flagged sections/videos

2. The renderer MUST preserve these visible report elements:
   - Video Intelligence Report
   - Original Title
   - New Title
   - Category
   - Tags
   - Chapters

3. Chapters are no longer rendered as a table.
   Render `04_chapters.json` as compact responsive chapter cards:
   - numbered circle
   - chapter title
   - timestamp/range pill
   - chronological order
   No additional LLM call is allowed for this presentation change.

4. Detailed Timestamped Summary is rendered as responsive topic cards:
   - numbered circle
   - topic heading
   - timestamp pill
   - concise lead paragraph
   - optional structured gray detail box
   The renderer may select a visual pattern from semantic metadata already
   present in the section result. It must not invent semantic content.

5. Recipes / Preparations use the SAME visual design system as the
   Detailed Summary.
   Supported renderer variants:
   - full recipe/preparation
   - compact preparation
   - simple-use card
   - uncertain-source card
   Empty fields are never rendered. No N/A placeholders.

6. Recipe structured data should support, when present:
   - name
   - timestamp/start/end
   - ingredients
   - quantities/ratios
   - preparation_steps
   - usage
   - frequency
   - duration
   - storage
   - important_tip
   - caution
   - uncertainty_notes
   The semantic pass should populate only source-supported values.

7. Meaningful References and Named Items:
   - JSON may retain timestamp as its own field
   - HTML renderer must append timestamp to the visible item/reference
     name
   - renderer must NOT show a separate Timestamp column
   Example: `Charaka Samhita (06:30)`
   Example: `Shatavari (06:30)`

8. Named Items remains the LAST visible report section.

9. Phase-5 semantic validation adds:
   - adaptive information-density coverage
   - internal coverage ledger
   - localized ASR uncertainty
   - chapter navigation-value test
   - title compression check
   - recipe field completeness check
   - Q&A retrieval-value test
   - Named Items precision check
   - final cross-section consistency check

10. The internal coverage ledger is never persisted as visible report
    content. Existing quality files may record only actionable status,
    warnings, uncertainty and repair/reprocess reasons as already defined.

11. Rendering changes are deterministic and token-free.
    Changing CSS/layout or re-rendering Chapters/Summary/Recipes must not
    require another LLM call when semantic JSON has not changed.

12. Manual edits remain section-scoped:
    edit authoritative section JSON -> validate dependencies -> assemble
    VIDEO_ID.json -> render VIDEO_ID.html.

13. V3 acceptance criteria:
    - no regression in semantic accuracy
    - no new unsupported information
    - no promotional leakage
    - better scanability for Chapters, Detailed Summary and Recipes
    - exact quantities/timestamps preserved
    - ASR uncertainty localized
    - optional sections omitted when empty
    - all required visible identity/navigation fields preserved


======================================================================
V3.1 IMPLEMENTATION — ENGLISH OUTPUT + VIDEO URL
======================================================================

14. LANGUAGE NORMALIZATION IS A SEMANTIC REQUIREMENT

The canonical transcript remains stored in its original language.

The Pass-1 semantic model must understand that original-language source
but return all generated intelligence in English, except:
- `original_title`, which remains exact
- proper nouns / classical terms / product names / medicine names /
  technical identifiers where preserving the source term is necessary

This is NOT a deterministic post-processing translation step.

Do not solve this by:
- copying Hindi/Hinglish transcript sentences into HTML
- regex replacement
- transliteration
- translating only metadata while leaving summary text unchanged

The semantic model output itself must be English.

Add deterministic validation after Pass 1:
- inspect generated human-readable semantic fields for unexpected
  non-English script/prose
- exempt `original_title`
- exempt approved proper/source terms where appropriate
- if ordinary non-English prose is detected in a generated section,
  flag that section for targeted semantic repair before final assembly
- do not reprocess already-good sections unnecessarily

Suggested validation flag:
`NON_ENGLISH_GENERATED_PROSE`

A targeted repair receives only:
- affected section JSON
- relevant transcript excerpts
- language rule
- existing dependencies
and rewrites that section in English without changing supported meaning,
numbers, timestamps, or uncertainty.

15. VIDEO URL DATA + RENDERING

Add/retain source identity field:
`video_url`

Source priority:
1. canonical URL from package/video metadata
2. deterministic YouTube watch URL built from canonical VIDEO_ID when URL
   is absent

The LLM does not generate this field.

HTML header order is mandatory:
- Original Title
- New Title
- Video URL
- Category

Render Video URL as a clickable `<a>` element using the authoritative
URL. Escape HTML attributes safely.

16. V3.1 VALIDATION ACCEPTANCE CRITERIA

Before a video is marked PASS:
- Original Title exactly matches source metadata
- New Title is English and semantically generated
- Video URL exists and is rendered immediately after New Title
- Chapters are English semantic headings
- Detailed Summary prose is English
- Recipes / Preparations are English when present
- References/Q&A/Technical/Playlist/Named Items generated prose is English
- legitimate proper nouns/source terms may remain in original form
- no promotional material leaks into semantic sections
- no transcript-language prose is copied merely because the transcript is
  Hindi/Hinglish/non-English

If source evidence is insufficient, keep the existing
SOURCE_INSUFFICIENT / REPROCESS_RECOMMENDED behavior rather than
inventing an English report.


======================================================================
V3.2 SEMANTIC ISOLATION — QUALITY OVER LITERAL MODEL-CALL COUNT
======================================================================

This section supersedes earlier architecture wording that could be read as
requiring exactly one literal model/API call per video.

The mandatory requirement is SEMANTIC ISOLATION, not a fixed call count.

For each VIDEO_ID:

1. Treat the video as one complete semantic unit.
2. Give the semantic processor the complete allowed evidence for the
   CURRENT video when performing the main semantic pass.
3. Do not include, retain, or use another video's transcript or semantic
   content to interpret the current video.
4. Perform the required internal sequence:
   Understand/Clean/Segment -> Detailed Intelligence -> Specialized
   Extraction -> Library/Search Intelligence -> Semantic Self-review.
5. The normal/default path should use one complete semantic read and return
   the full structured intelligence result.
6. Do not perform separate full-transcript reads merely to generate
   Chapters, Summary, Recipes, References, Q&A, Tags, Named Items, etc.
7. If deterministic validation identifies a specific recoverable weakness,
   an additional TARGETED semantic repair is allowed.
8. A targeted repair must receive only the affected section, concrete
   validation issue, minimum relevant transcript excerpts, dependencies and
   applicable rules. Replace only the affected section where safe.
9. A second complete transcript read is allowed only when genuinely
   necessary for correctness and cannot be solved reliably with targeted
   evidence. It must not become the default workflow.
10. Quality and correctness take priority over artificially minimizing the
    literal number of model operations. Token efficiency remains an
    optimization constraint, not a reason to accept inferior intelligence.

Required video lifecycle:

CURRENT VIDEO
  -> complete semantic processing
  -> deterministic validation
  -> optional targeted semantic repair
  -> final validation/status
  -> persist modular section files
  -> assemble JSON
  -> render HTML
  -> checkpoint
  -> NEXT VIDEO

The current video must be fully validated, persisted, assembled, rendered
and checkpointed before advancing to the next VIDEO_ID.

PROHIBITED SHORTCUTS include:
- mechanically dividing a transcript into equal-duration/equal-size chunks
  and treating those chunks as semantic chapters
- using the first sentences of transcript chunks as a substitute for a
  semantic Detailed Summary
- deriving Tags or Named Items merely from title words or word frequency
- using metadata/title wording to override clear transcript evidence
- processing multiple videos together in a way that permits semantic
  contamination
- skipping whole-transcript understanding to reduce model usage
- calling deterministic/extractive output a completed semantic V3 report

Acceptance is based on semantic quality, source grounding, section
consistency, language rules, promotion exclusion, ASR handling and
validation—not on proving an exact API/model-call count.


======================================================================
V3.3 IMPLEMENTATION — CHANNEL NAME + DURATION
======================================================================

Extend the per-video source identity model with:

- `channel_name`
- authoritative duration field(s), e.g. `duration_seconds` and/or
  `duration_display`

Source priority:
- Channel Name: authoritative package/video metadata only.
- Duration: authoritative package/video metadata first; deterministic
  derivation from authoritative source timing only when safe.

Do not ask the semantic model to generate either field.

HTML HEADER ORDER IS MANDATORY:

Original Title
New Title
Video URL
Channel Name
Duration
Category

Rendering rules:
- Video URL remains clickable.
- Channel Name is rendered as exact source metadata text.
- Duration is rendered in a human-readable deterministic format.
- Escape all rendered metadata safely.
- Missing authoritative channel/duration must not be guessed.
- Do not substitute transcript represented-duration for actual video
  duration unless the source contract explicitly establishes they are the
  same authoritative duration.

Validation additions:
- verify Channel Name exactly matches authoritative metadata when present
- verify Duration matches authoritative metadata/deterministic source value
- verify both appear after Video URL and before Category
- verify neither field was semantically invented


======================================================================
V3.3 CHATGPT PACKAGE EXECUTION MODE — ARCHITECTURE
======================================================================

Interactive ChatGPT runs may use DEFERRED DETERMINISTIC PERSISTENCE.

Semantic lifecycle remains strictly sequential:

CURRENT VIDEO
  -> complete-video semantic understanding
  -> five internal phases
  -> semantic self-review
  -> per-video validation/status
  -> mark semantic result complete in the current session
  -> NEXT VIDEO

After one or more videos have completed semantic processing:

COMPLETED SEMANTIC RESULTS
  -> deterministic modular persistence
  -> section validation
  -> assembled JSON
  -> HTML rendering
  -> package index/status/reprocess list

This exception changes only the timing of deterministic persistence. It does
NOT change the semantic contract.

Mandatory safeguards:
1. Never use another VIDEO_ID's transcript/content as evidence for the
   current video.
2. Never replace semantic processing with equal-time/equal-size chunking,
   first-sentence extraction, word-frequency tags, title-derived Named
   Items, or similar heuristics.
3. Complete and validate each video's semantic result before interpreting
   the next video.
4. Preserve a distinct result object keyed by exact VIDEO_ID.
5. Renderer/persistence code may format and validate but may not invent
   semantic intelligence.
6. A weak video is recorded as PASS_WITH_WARNINGS,
   REPROCESS_RECOMMENDED or SOURCE_INSUFFICIENT and does not block later
   videos.
7. If the interactive run is interrupted before deterministic persistence,
   only results actually persisted are resumable across sessions; therefore
   production use should continue to checkpoint after every video.
8. Acceptance criteria and semantic quality are identical to normal V3.3.

The production/default runtime remains immediate per-video persistence and
checkpointing. Deferred persistence is permitted specifically for
interactive ChatGPT package execution where it enables faithful semantic
processing without imposing an artificial model-call boundary.


======================================================================
V3.3 SEMANTIC-AUTHORING / DETERMINISTIC-CODE EXECUTION CONTRACT
======================================================================

Required execution pipeline for each CURRENT VIDEO:

1. CODE: load only permitted source identity + complete allowed transcript/
   SRT evidence for the CURRENT VIDEO.
2. SEMANTIC PROCESSOR/MODEL: perform complete V3.3 understanding and author
   the semantic intelligence.
3. SEMANTIC PROCESSOR/MODEL: perform V3.3 self-review and assign semantic
   status/reprocess recommendation.
4. CODE: accept the completed semantic result object; code may validate
   deterministic invariants but may not replace semantic fields with
   heuristic/extractive substitutes.
5. CODE: persist modular section files, quality/status files, assembled JSON
   and HTML (immediately in production mode, or under the permitted deferred
   persistence rule in interactive ChatGPT mode).
6. CODE: checkpoint/index/reprocess-list update.
7. Proceed to NEXT VIDEO.

AUTHORITATIVE RESULT BOUNDARY
The model-authored semantic result is the source for semantic section
content. Modular section JSON becomes the authoritative editable persisted
representation after it is written. HTML is always a deterministic view,
never a semantic source.

PROHIBITED CODE PATHS
Any code path that creates purported V3.3 semantic content through transcript
chunking, sentence extraction, keyword/frequency ranking, title-word reuse,
generic topic numbering, mechanical translation, or guessed ASR recovery is
a non-compliant fallback and MUST NOT be labeled V3.3 semantic processing.

If semantic processing is unavailable for a video, the system must record
that state rather than silently switching to such a fallback.

VALIDATION OWNERSHIP
- Semantic quality checks belong to semantic self-review.
- Deterministic checks belong to code.
- Code may FLAG a semantic section for targeted repair but may not repair
  semantic meaning by heuristic generation.
- Targeted semantic repair must return to the semantic processor/model with
  the minimum necessary evidence and dependencies.

PACKAGE ACCEPTANCE
A package is COMPLETE or COMPLETE_WITH_REPROCESS_LIST only after every
claimed processed VIDEO_ID has:
- an independently authored semantic result,
- a recorded V3.3 semantic validation/status,
- persisted modular output,
- assembled JSON,
- rendered HTML,
- and checkpoint/package bookkeeping.

A count of rendered HTML files alone is never a package-completion metric.

# V3.3.1 Architecture Hardening

V3.3.1 hardens the existing V3.3 architecture. It does **not** change the
fundamental design: strict sequential processing, current-video-only semantic
context, normally one complete semantic read, five internal phases, optional
targeted repair, modular authoritative JSON, deterministic assembly/rendering,
checkpoint after every video, and non-blocking weak-video handling.

## A. Deterministic Source Preflight

Before spending semantic-model tokens on the current VIDEO_ID, code performs a
cheap deterministic source preflight.

Check only mechanical/source-integrity facts:
- selected VTT/transcript exists;
- transcript contains usable text;
- transcript contains enough usable semantic speech evidence for processing;
- timestamp records are parseable and reasonably ordered when timing is used;
- mechanically proven missing-spoken-content / empty evidence is detected;
- a large unsubtitled beginning/end tail is recorded as a coverage uncertainty signal, not automatically as truncation;
- selected evidence follows the one-VTT source policy.

Preflight MUST NOT author semantic chapters, summaries, tags, categories,
Named Items, recipes or other intelligence.

### Transcript Completeness Gate

If evidence is empty, has no usable speech, or independent mechanical evidence proves that meaningful spoken content is materially missing:

`SOURCE_INSUFFICIENT -> videos_to_repackage -> checkpoint -> NEXT VIDEO`

Do not spend a normal semantic pass attempting to reconstruct missing spoken
content from obviously insufficient evidence.

A transcript ending substantially before `video_duration` is NOT by itself proof
of truncation. The remaining media may legitimately contain silence, music,
visual demonstrations, credits or an end screen. Record a large unsubtitled
tail as `END_COVERAGE_UNCERTAIN` / `LARGE_UNSUBTITLED_TAIL` unless independent
evidence establishes that speech is actually missing.

Do not use a universal character-count threshold as proof of completeness.
Mechanical size/timestamp checks are signals; when evidence is ambiguous,
set completeness to UNKNOWN/LIKELY_COMPLETE as warranted and allow semantic
processing to use the available speech evidence without inventing unseen content.

## B. Timestamp Sanity Check

Code may detect:
- malformed timestamps;
- impossible ordering;
- severe timestamp discontinuity;
- missing timestamp fields where the contract requires them.

Code must not invent or semantically reposition chapters to repair timestamp
problems.

## C. Critical-ASR Risk Signaling

Deterministic checks may flag suspicious source patterns for model attention,
but only the semantic processor decides whether an entity, dosage, medicine,
ingredient, instruction or claim is recoverable.

## D. Semantic Processing and Acceptance

For usable source evidence:

`Preflight -> V3.3.1 semantic authoring -> semantic acceptance gate -> optional targeted repair`

The semantic acceptance gate includes all V3.3 checks plus:
- information-preservation check;
- number/entity integrity;
- strict recipe qualification;
- source-claim attribution;
- critical-ASR protection;
- chapter navigation quality;
- Q&A retrieval quality;
- Named Items precision;
- category specificity.

## E. Deterministic Postflight

After semantic authoring is accepted, code checks mechanical invariants only:
- JSON/schema validity;
- required/optional section contract;
- timestamp format/order;
- filenames and VIDEO_ID identity;
- authoritative URL/channel/duration handling;
- generated-output language signals where mechanically testable;
- duplicate/empty structural artifacts;
- HTML-visible-field contract;
- safe link/HTML escaping;
- section/assembled consistency.

Postflight MUST flag semantic-looking anomalies for targeted review rather than
rewriting semantic content heuristically.

### Number/Entity Structural Signal

Where mechanically detectable, code may flag suspicious orphan quantities,
times, dosages or measurements. It MUST NOT invent the missing entity/action.
A semantic repair is required if the issue matters.

## F. Visible HTML Contract Test

After rendering, deterministically verify that internal/forbidden fields are
not exposed in the human report, including:
- processing status;
- processing warnings;
- validation diagnostics;
- confidence/internal provenance fields;
- source diagnostics;
- internal section-status metadata.

The visible report contract remains the authoritative V3/V3.3 layout rules.

## G. Renderer Failure Isolation

Semantic completion and rendering completion are separate states.

If semantic processing succeeds and authoritative JSON/section files are
persisted, an HTML renderer failure MUST NOT trigger another semantic pass.

Flow:

`semantic JSON persisted -> renderer -> failure -> deterministic retry`

If retry still fails:
- retain all semantic JSON/section files;
- record artifact status `RENDER_ERROR` or
  `JSON_COMPLETE_HTML_PENDING`;
- checkpoint;
- continue to the next VIDEO_ID.

A later deterministic rerender consumes zero semantic-model tokens.

## H. Separate Semantic and Artifact Status

Track at least:

```text
semantic_status:
  PASS
  PASS_WITH_WARNINGS
  REPROCESS_RECOMMENDED
  SOURCE_INSUFFICIENT

artifact_status:
  COMPLETE
  JSON_COMPLETE_HTML_PENDING
  RENDER_ERROR
```

Package completion accounting must distinguish semantic completion from
artifact/render completion.

## I. Structured Repackage Reason Codes

Where practical, record a stable reason code plus human-readable detail:

```text
TRANSCRIPT_MISSING
TRANSCRIPT_TRUNCATED
ASR_SEVERE
CRITICAL_ENTITY_UNCERTAIN
CRITICAL_NUMBER_UNCERTAIN
TIMESTAMP_CORRUPTION
SOURCE_INSUFFICIENT_OTHER
```

Do not force one code when the actual reason is unknown.

## J. Package-Level Completion Summary

At package completion, code should produce counts/lists for:
- PASS;
- PASS_WITH_WARNINGS;
- REPROCESS_RECOMMENDED;
- SOURCE_INSUFFICIENT;
- artifact/render failures;
- videos_to_repackage.

The package must continue after any individual weak/error video unless the
package input itself is structurally unusable.

## K. Resume Safety

Resume from the first genuinely unfinished semantic video.

Do NOT rerun completed semantic processing merely because:
- HTML rendering failed;
- index generation failed;
- ZIP creation failed;
- package summary generation failed;
- another later video failed.

Reuse completed semantic results when source fingerprint and prompt/version
compatibility allow it.

## L. V3.3.1 Reference Pipeline

```text
PACKAGE
  -> CURRENT VIDEO ONLY
  -> deterministic source preflight
       -> clearly insufficient:
            SOURCE_INSUFFICIENT
            -> repackage list
            -> checkpoint
            -> NEXT VIDEO
       -> usable:
            V3.3.1 semantic authoring
            -> semantic acceptance gate
            -> optional targeted repair
            -> final semantic status
            -> persist modular authoritative JSON
            -> deterministic postflight
            -> assemble JSON
            -> render HTML
            -> visible HTML contract test
            -> checkpoint
            -> NEXT VIDEO
```

No deterministic preflight/postflight/renderer component may replace semantic
authoring with extractive or heuristic intelligence generation.

# End V3.3.1 Architecture Hardening


# V3.3.3 Direct-ChatGPT Continuous Execution / Resume Architecture

When VideoHoarder packages are processed directly in ChatGPT, orchestration
must assume that a chat execution can eventually be interrupted by an actual
environment/tool/context limit. Correctness therefore depends on durable
per-video checkpoints and idempotent resume behavior.

## Continuous execution policy

After the user requests complete-package processing:

`CURRENT VIDEO -> semantic final status -> persist -> checkpoint -> NEXT VIDEO`

Repeat without asking for permission or stopping at arbitrary milestones while
the current execution can continue.

A progress milestone is not a completion condition.

## Per-video commit boundary

A video becomes a durable completed semantic unit only after its semantic
result has reached a final semantic status and has been persisted when
persistence is available.

The checkpoint is committed before the next video begins.

Recommended checkpoint state:

```text
package_id
expected_video_count
completed_video_ids
last_completed_video_id
next_video_id
semantic_status_by_video
artifact_status_by_video
videos_to_repackage
prompt_version
checkpoint_timestamp
```

## Interruption semantics

If interruption occurs before semantic persistence:
- current video = unfinished;
- resume current video.

If interruption occurs after semantic persistence but before HTML:
- semantic video = completed;
- artifact = pending;
- resume deterministic rendering only.

If interruption occurs after checkpoint:
- resume at `next_video_id`.

## Resume entry point

For a later "continue"/"resume"/"process rest" instruction:

`load checkpoint -> validate package/source identity -> locate next_video_id
 -> resume`

Do not restart from Video 1 and do not ask for instructions already present in
the package/current authoritative specification.

## No false watchdog assumption

The architecture does not assume that a scheduled ChatGPT task can inspect and
restart the exact currently executing chat turn at five-minute intervals.
Native automation is optional and is not part of the correctness guarantee.

The correctness guarantee is:

`per-video semantic isolation + durable persistence + checkpoint-before-next
 + idempotent resume`

## Completion condition

Semantic package completion requires:

`expected_video_count == final_semantic_status_count`

Artifact completion is checked separately.

If execution ends before that equality is reached, the state is
`INTERRUPTED / IN_PROGRESS`, not `COMPLETE`.

# End V3.3.3 Direct-ChatGPT Continuous Execution / Resume Architecture

# V3.3.4 Transcript Health Analyzer + Health-Aware Similarity Grouping

## A. Goal

V3.3.4 adds a deterministic transcript-health and package-routing layer before
normal ChatGPT semantic processing.

The design is:

```text
VIDEO LIBRARY
  -> source/transcript selection
  -> Transcript Health Analyzer
  -> health routing
       -> NORMAL
       -> CAUTION
       -> REPAIR_RECOMMENDED
       -> REPAIR_REQUIRED
  -> eligible NORMAL/CAUTION videos
  -> Group Similar Videos planner
  -> validated similarity groups
  -> deterministic Package Balancer
       similarity + health + transcript size + workload
  -> final processing packages
  -> V3.3.4 semantic processing
       CURRENT VIDEO ONLY
       -> semantic result
       -> persistence
       -> validation/rendering
       -> checkpoint
       -> NEXT VIDEO
```

D/F repair-path videos should normally be repaired/retranscribed before entering
the normal semantic-processing package flow.

This new layer MUST NOT weaken:

- current-video semantic isolation;
- V3.3.3 sequential processing;
- semantic self-review;
- modular authoritative persistence;
- targeted Pass-2 repair;
- renderer isolation;
- artifact/semantic status separation;
- checkpoint/resume;
- no-heuristic-semantic-fallback rules.

---

## B. Transcript Health Analyzer position

Run the Transcript Health Analyzer after VideoHoarder has selected the
authoritative transcript/SRT/VTT source and before Group Similar Videos package
planning/final package creation.

Conceptually:

```text
source selection
  -> transcript fingerprint
  -> Transcript Health Analyzer
  -> persisted transcript_health record
  -> routing eligibility
  -> similarity planner
  -> package balancer
```

Do not upload a transcript to ChatGPT merely to obtain a health grade.

Health analysis is local deterministic code.

---

## C. Deterministic health signals

The analyzer may calculate mechanical signals including:

- transcript/SRT/VTT existence;
- non-empty usable text;
- timestamp parse success rate;
- monotonic timestamp quality;
- invalid timestamp ranges;
- timestamp overlaps;
- represented start coverage;
- represented end position;
- transcript/video represented-duration ratio when authoritative duration exists;
- large unsubtitled head/tail duration as an uncertainty signal (not proof of missing speech);
- unusually large timestamp gaps;
- caption/text density;
- sparse transcript regions;
- duplicated/repeated caption ratio;
- repeated caption blocks;
- fragmentation ratio;
- very short caption-fragment ratio;
- obvious noise/non-speech marker ratio;
- suspicious beginning coverage;
- suspicious ending coverage;
- independently confirmed missing spoken-content regions;
- word count;
- character count;
- words/characters per represented minute;
- source-language/source-selection policy compliance when deterministically
  knowable.

Unknown/unavailable signals MUST remain null/unknown rather than being invented.

Authoritative video duration is useful but NOT required for transcript
acceptance.

If duration is unavailable:

- do not guess it;
- skip duration-based health signals;
- record the unavailable signal;
- do not fail the transcript solely for missing duration.

---

## D. Mechanical-health boundary

The analyzer MUST NOT:

- author chapters;
- summarize content;
- generate category/tags;
- extract Named Items semantically;
- determine factual accuracy;
- repair ASR meaning;
- infer missing recipes;
- reconstruct missing proper nouns/numbers;
- determine semantic claim validity;
- replace ChatGPT semantic assessment.

The analyzer may flag suspicious mechanical patterns for later attention.

ChatGPT remains responsible for semantic recoverability.

---

## E. Health record

Persist a structured record similar to:

```json
{
  "analyzer_version": "1.0",
  "transcript_fingerprint": "...",
  "source_fingerprint": "...",
  "score": 84,
  "grade": "B",
  "routing_class": "NORMAL",
  "hard_failure": false,
  "signals": {
    "timestamp_parse_rate": 1.0,
    "timestamp_monotonicity": 1.0,
    "start_coverage": 0.99,
    "end_coverage": 0.97,
    "duration_coverage": 0.96,
    "text_density": 0.82,
    "large_gap_ratio": 0.02,
    "duplicate_ratio": 0.03,
    "fragmentation_ratio": 0.08,
    "noise_ratio": 0.01
  },
  "reason_codes": [],
  "warnings": [],
  "analyzed_at": "..."
}
```

Store the health-analyzer version/configuration identity so an algorithm upgrade
can rescore existing transcripts without requiring retranscription or automatic
semantic regeneration.

---

## F. Grade model

Provide human-readable grades:

- A — excellent mechanical transcript health
- B — good mechanical transcript health
- C — usable but caution warranted
- D — poor; source repair recommended
- F — unusable or hard source failure

The Architecture implementation MUST document deterministic score thresholds
and weighting.

However routing MUST NOT depend only on numeric score/grade.

Routing uses:

```text
grade
+ hard_failure
+ reason_codes
+ severity
```

This prevents a single averaged score from hiding a critical failure.

---

## G. Hard-failure overrides

Examples of hard-failure reason codes:

```text
TRANSCRIPT_MISSING
EMPTY_TRANSCRIPT
NO_USABLE_TEXT
SEVERE_TIMESTAMP_CORRUPTION
CONFIRMED_MISSING_SPOKEN_CONTENT
SOURCE_POLICY_FAILURE
```

A hard failure may force:

```text
grade = F
routing_class = REPAIR_REQUIRED
```

Use hard failures only when the mechanical evidence clearly supports them.

Do not turn moderate uncertainty into a hard failure.

---

## H. Routing classes

Use explicit routing classes:

```text
NORMAL
CAUTION
REPAIR_RECOMMENDED
REPAIR_REQUIRED
```

Default routing guidance:

```text
A -> NORMAL
B -> NORMAL
C -> CAUTION
D -> REPAIR_RECOMMENDED
F -> REPAIR_REQUIRED
```

The code may allow a C-grade transcript to continue under a
NORMAL_WITH_CAUTION-equivalent internal policy when its specific reason codes
are minor and the configured routing policy permits it.

Do not automatically convert C into SOURCE_INSUFFICIENT.

Do not convert transcript-health grade directly into semantic status.

---

## I. D/F source-repair flow

Normal flow:

```text
D/F
  -> source-repair/retranscription queue
  -> obtain improved transcript/SRT/VTT
  -> recompute transcript/source fingerprint
  -> rerun Transcript Health Analyzer
  -> reroute
  -> if eligible -> Group Similar Videos planner
```

Do not permanently exclude repaired videos.

A D/F video with a clear hard source failure should normally not consume normal
semantic-processing capacity until repaired.

---

## J. C-grade handling

C-grade videos remain potentially semantically usable.

They should remain distinguishable as CAUTION.

Possible handling:

- create CAUTION packages;
- mix a small number into balanced packages if configured and safe;
- preserve health reason codes/warnings in package metadata.

ChatGPT still performs complete semantic review and may return any legitimate
final semantic status independently.

---

## K. Keep Group Similar Videos

Do NOT remove Group Similar Videos.

Its V3.3.4 role becomes:

> Create semantically coherent, health-compatible, workload-balanced processing
> groups.

The grouping planner provides semantic/topic grouping.

Deterministic VideoHoarder code provides health calculation and final package
capacity balancing.

---

## L. Group Similar Videos planner input

The grouping package should remain compact.

Do NOT send complete transcripts merely for grouping unless an existing
authoritative grouping contract genuinely requires them.

Preferred input per eligible video may include:

```json
{
  "video_id": "...",
  "original_title": "...",
  "description_or_compact_grouping_signal": "...",
  "existing_category_if_available": "...",
  "duration_seconds": 900,
  "transcript_words": 4200,
  "transcript_characters": 24100,
  "transcript_health": {
    "grade": "B",
    "routing_class": "NORMAL",
    "hard_failure": false,
    "reason_codes": []
  }
}
```

Preserve existing useful grouping metadata/signals unless they conflict with
V3.3.4.

Full detailed health signal arrays need not be sent to the grouping model unless
useful.

---

## M. Grouping responsibility boundary

ChatGPT grouping may decide:

- subject/topic similarity;
- likely series/playlist coherence when supported;
- broad content relationships;
- meaningful thematic group labels.

VideoHoarder deterministic code decides:

- transcript-health grade/score;
- routing class;
- transcript word/character counts;
- duration;
- workload estimate;
- final package capacity;
- package count/cap enforcement.

The grouping model MUST NOT invent operational measurements.

---

## N. Similarity group is orchestration only

If a similarity group contains:

```text
VIDEO_1
VIDEO_2
VIDEO_3
VIDEO_4
```

that means only that the videos are appropriate to place in the same
orchestration/processing family.

It does NOT authorize sending all four transcripts together for semantic
intelligence.

Final processing remains:

```text
VIDEO_1 evidence only -> finish -> persist -> checkpoint
VIDEO_2 evidence only -> finish -> persist -> checkpoint
VIDEO_3 evidence only -> finish -> persist -> checkpoint
VIDEO_4 evidence only -> finish -> persist -> checkpoint
```

This rule is absolute.

---

## O. Similarity planner output

Recommended output:

```json
{
  "groups": [
    {
      "group_id": "G001",
      "theme": "Hair Loss and Scalp Care",
      "video_ids": ["VIDEO_1", "VIDEO_8", "VIDEO_14"]
    }
  ]
}
```

VideoHoarder MUST validate:

- every eligible input video appears exactly once unless the explicit planner
  contract supports a documented exception;
- no unknown VIDEO_IDs;
- no duplicates across groups;
- no repair-only video is introduced into a normal eligible group;
- output schema is valid.

Only after this validation does deterministic package balancing occur.

---

## P. Deterministic Package Balancer

Keep:

```text
target_package_size = 25  # advisory only
max_package_size = 30
```

But 25 is an advisory target only, not a cap and not a requirement to fill every package. The hard maximum remains 30.

Final package balancing should consider:

- similarity group;
- routing class;
- transcript health;
- transcript word/character size;
- represented/authoritative duration when available;
- workload estimate;
- max video count.

Valid packages may contain fewer than 25 videos.

Examples:

```text
16 videos -> valid
21 videos -> valid
25 videos -> valid
```

Do not create pathological packages merely to reach 25.

---

## Q. Workload estimate

Create a deterministic workload estimate.

Recommended inputs include:

- transcript word count;
- transcript character count;
- represented duration;
- authoritative duration when available;
- routing class;
- selected mechanical health-complexity signals.

The exact formula/thresholds must be deterministic, versioned and documented.

Workload is an operational capacity estimate, NOT semantic quality.

Use it to avoid packages such as:

```text
25 very long C-grade transcripts
```

when smaller or better-balanced packages are safer.

---

## R. Health-compatible grouping/balancing

Prefer:

```text
NORMAL with NORMAL
CAUTION with CAUTION
```

where practical.

Topic similarity remains important.

However routing safety and workload may justify splitting one semantic group
into multiple processing packages.

Do not mix D/F repair videos into normal packages merely to fill capacity.

---

## S. Package metadata

Each final processing package should include actual and target package sizes:

```text
video_count = actual videos in package
batch_size = actual videos in package
target_package_size = 25  # advisory only
max_package_size = 30
```

A package containing 16 videos must say:

```text
video_count = 16
batch_size = 16
target_package_size = 25  # advisory only
max_package_size = 30
```

Do not misleadingly report `batch_size = 25` for smaller packages.

---

## T. Health metadata in final ChatGPT package

Every eligible video in the processing package should carry compact health
metadata, at minimum:

```json
{
  "transcript_health": {
    "analyzer_version": "1.0",
    "grade": "B",
    "routing_class": "NORMAL",
    "hard_failure": false,
    "reason_codes": [],
    "warnings": []
  }
}
```

The same selected transcript is included for semantic processing.

There is NO second transcript upload for health analysis.

---

## U. Transcript-health persistence

Store the full health record internally.

Recommended locations:

```text
VIDEO_ID/
  source/
    source_manifest.json
  quality/
    transcript_health.json
```

`source_manifest.json` should reference the transcript-health record and include
the source/transcript fingerprints used to create it.

Transcript health must not become a normal visible report section.

---

## V. Health cache/fingerprint behavior

If:

```text
transcript fingerprint unchanged
+ analyzer version/config compatible
```

reuse the health result.

If the transcript changes:

```text
recompute transcript health
```

If only the analyzer algorithm/version changes:

```text
recompute health
without automatically rerunning semantic intelligence
```

However, if the new health result discovers a hard source failure that
materially invalidates the evidence used by a prior semantic result:

```text
flag prior semantic result for compatibility review/reprocessing
```

Do not silently accept a permanent semantic result against newly established
major source incompleteness.

---

## W. Integrate existing V3.3.3 source preflight

Do NOT maintain two contradictory transcript-quality systems.

The Transcript Health Analyzer is the persistent mechanical analysis layer.

Immediately before semantic processing, source preflight should:

1. confirm current source/transcript fingerprint;
2. consume compatible stored health facts;
3. cheaply revalidate critical mechanical prerequisites if needed;
4. determine whether the source can proceed to semantic processing.

Flow:

```text
Transcript Health Analyzer
  -> persistent health result
  -> routing/grouping/package creation

later:

source preflight
  -> fingerprint/critical checks
  -> usable -> semantic processing
  -> clearly unusable -> SOURCE_INSUFFICIENT
                         -> repackage list
                         -> checkpoint
                         -> next video
```

Avoid duplicate heavy computation.

---

## X. Semantic status remains independent

Transcript-health grades and V3 semantic statuses are separate dimensions.

Possible examples:

```text
health grade C + semantic PASS
health grade C + semantic PASS_WITH_WARNINGS
health grade A + semantic REPROCESS_RECOMMENDED
health grade B + semantic SOURCE_INSUFFICIENT
```

The semantic model has independent authority over semantic recoverability after
complete current-video review.

---

## Y. No second transcript upload

Hard requirement:

```text
VideoHoarder transcript
  -> local deterministic health analysis
  -> same transcript packaged
  -> ChatGPT semantic processing
```

Do NOT implement:

```text
upload transcript to ChatGPT for health
  -> upload transcript again for semantic processing
```

---

## Z. V3.3.4 direct-ChatGPT package snapshot

Every direct-ChatGPT processing package should remain self-contained and carry:

```text
CHATGPT_PACKAGE.json
VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md
PACKAGE_README.txt
manifest.json
schema.json
prompt.json
evidence.json
```

The package prompt hash must be calculated from the exact V3.3.4 prompt snapshot
copied into that package.

Old package prompt snapshots remain immutable historical contracts.

---

## AA. Checkpoint/resume compatibility

V3.3.4 health/grouping changes MUST NOT regress V3.3.3 resume behavior.

Completed semantic results are reusable only when prompt/source compatibility
rules permit.

Health rescore alone does not automatically force semantic reprocessing.

A changed transcript/source fingerprint does.

A newly detected hard source failure may invalidate an otherwise completed
semantic result and must be surfaced for reprocessing review.

---

## AB. Testing requirements

Add deterministic tests for at least:

### Transcript Health Analyzer
- missing transcript -> hard failure;
- empty transcript -> hard failure;
- healthy transcript -> A/B range under configured fixtures;
- large missing ending -> truncation reason;
- timestamp corruption detected;
- large timestamp gaps detected;
- duplicated captions detected;
- noise markers detected;
- missing authoritative duration does not fail transcript;
- unavailable signals remain null/unknown;
- result tied to transcript fingerprint;
- changed transcript invalidates cached health;
- changed analyzer version permits rescore;
- health rescore alone does not automatically force semantic reprocessing;
- newly discovered hard source failure flags incompatible prior semantic result.

### Routing
- A/B -> NORMAL;
- C -> CAUTION according to policy;
- D -> REPAIR_RECOMMENDED;
- F/hard failure -> REPAIR_REQUIRED;
- D/F excluded from normal similarity-planner input;
- repaired video can re-enter eligibility after reassessment.

### Group Similar Videos
- eligible input appears exactly once;
- unknown VIDEO_ID rejected;
- duplicate group membership rejected;
- repair-only VIDEO_ID rejected from normal groups;
- compact grouping input does not require full transcripts;
- similarity group never changes current-video semantic isolation.

### Package Balancing
- package never exceeds `max_package_size`;
- package may contain fewer than `target_package_size`;
- actual `batch_size` equals actual video count;
- workload balancing avoids configured pathological heavy-package fixtures;
- NORMAL/CAUTION compatibility policy is respected.

### Final Processing Package
- `transcript_health` included per video;
- full transcript not duplicated solely for health;
- V3.3.4 prompt snapshot included;
- prompt hash matches exact package snapshot;
- transcript health not rendered in visible HTML;
- source preflight consumes compatible health state;
- changed transcript fingerprint forces health/source-preflight refresh.

### Regression
Run all existing V3.3.3 semantic, renderer, checkpoint/resume and import
compatibility tests.

---

## AC. V3.3.4 reference preprocessing pipeline

```text
VIDEO SOURCE
  -> authoritative transcript/source selection
  -> transcript/source fingerprints
  -> Transcript Health Analyzer
       -> health record
       -> grade
       -> routing class
       -> hard-failure decision
  -> route
       -> D/F repair queue
       -> A/B/C eligible pool
  -> Group Similar Videos semantic planner
       -> topic-coherent groups
  -> deterministic group validation
  -> deterministic Package Balancer
       -> health compatibility
       -> transcript size
       -> workload
       -> target/max package size
  -> self-contained V3.3.4 processing package
       -> exact V3.3.4 Master Prompt snapshot
       -> compact health metadata per video
       -> CURRENT VIDEO transcript evidence
  -> sequential semantic processing
       -> current video only
       -> semantic final status
       -> modular persistence
       -> deterministic postflight
       -> assembled JSON
       -> HTML
       -> checkpoint
       -> next video
```

---

## AD. Final V3.3.4 responsibility boundary

### VideoHoarder deterministic code
Responsible for:

- transcript/source selection;
- transcript/source fingerprints;
- transcript-health analysis;
- health grade/score;
- routing class;
- hard-failure detection;
- repair queue;
- grouping-package construction;
- planner-result validation;
- workload calculation;
- final package balancing;
- package size/cap enforcement;
- source preflight;
- persistence;
- schema/timestamp/filename validation;
- checkpoint/resume bookkeeping;
- reprocess manifests;
- deterministic rendering.

### Group Similar Videos semantic planner
Responsible for:

- semantic/topic similarity;
- coherent group themes;
- series/topic relationships supported by compact grouping evidence.

It is NOT responsible for final semantic video intelligence.

### ChatGPT V3.3.4 semantic processor
Responsible for:

- complete current-video semantic understanding;
- semantic chapters;
- detailed summary;
- recipes/preparations;
- references;
- Q&A;
- playlist/series interpretation inside the current video;
- technical intelligence;
- title/search/category/tag intelligence;
- Named Items;
- semantic ASR uncertainty;
- semantic self-review;
- final semantic status.

No deterministic component may substitute heuristic/extractive output for these
semantic responsibilities.

# AE. Final V3.3.4 hardening requirements

These requirements are mandatory implementation constraints. They clarify the
architecture and must be reflected in package creation, validation, persistence,
resume behavior, and tests.

## AE.1 Parent-group hierarchy

Health-aware grouping must preserve a two-level grouping hierarchy:

```text
parent_group
  -> topic_subgroups
    -> video_ids
```

Topic subgroups preserve precise research/classification meaning.

Parent groups control actual ChatGPT package creation.

Do not create one ChatGPT processing package per small topic subgroup when the
subgroup can be sensibly combined with a reasonably related subgroup inside a
parent group.

The final package builder creates one processing package per parent group or
per deterministic split of a parent group when workload or max-size limits
require it.

## AE.2 Measurable tiny-package rule

Use these measurable package-size rules:

```yaml
preferred_package_size: globally optimized; no minimum

### Parent-group size contract

Parent groups are semantic compatibility guidance only and may contain any number of videos. Actual package boundaries are chosen deterministically by the global optimizer. There is no minimum package size, no `small_group_exception` requirement, and the hard maximum is 30 videos.

The optimizer minimizes total package count first, while respecting transcript/no-transcript separation, semantic compatibility, transcript-health/workload safety, and the 30-video hard maximum. A small final package is valid without an exception flag when it is the safest remainder after global optimization.

```yaml
preferred_package_size: globally optimized; no minimum
target_package_size: 25  # advisory/convenience metadata only
max_package_size: 30
```

## AE.3 No-transcript separation

Videos without usable transcript/SRT/VTT evidence must never be mixed into
normal transcript-processing packages.

They must be routed to an explicit separate path, such as:

- source repair;
- retranscription;
- no-transcript handling;
- metadata-only holding;
- or another explicit non-normal route.

They should not consume normal V3.3.4 transcript-semantic package capacity.

## AE.4 Package completion validation

Package completion accounting must distinguish final semantic completion from
unfinished execution state.

```text
COMPLETE:
  every expected VIDEO_ID has a final semantic status.

IN_PROGRESS / INTERRUPTED:
  unfinished VIDEO_IDs are allowed,
  but each unfinished ID must have execution state:
  PENDING, IN_PROGRESS, or INTERRUPTED.
```

A missing ChatGPT result must never automatically become SOURCE_INSUFFICIENT.

SOURCE_INSUFFICIENT is valid only when source/evidence insufficiency is proven
by deterministic preflight or by semantic processing of the current video.

## AE.5 Self-contained processing packages

Every processing package must be fully self-contained. Preserve existing files
where already present and create them where missing:

```text
CHATGPT_PACKAGE.json
VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md
PACKAGE_README.txt
manifest.json
schema.json
prompt.json
evidence.json
```

The prompt snapshot inside the package is authoritative.

The package prompt hash must be calculated from that exact copied prompt
snapshot, not from a mutable source prompt path.

## AE.6 Strong resume regression tests

Add explicit resume tests for the two interruption cases that protect the
whole architecture.

Semantic interruption test:

```text
25 videos
-> process 1-12
-> interrupt during 13
-> restart
-> verify 1-12 are NOT semantically rerun
-> resume at 13
-> finish 13-25
```

Render-only interruption test:

```text
Video 13 semantic JSON saved
-> HTML fails
-> restart
-> render Video 13 only
-> semantic processing continues at Video 14
```

These tests must verify that completed compatible semantic results are reused,
unfinished videos are not misclassified as SOURCE_INSUFFICIENT, and renderer
failures do not trigger another semantic pass.

# End V3.3.4 Transcript Health + Similarity Grouping Architecture

## V3.3.4 Implementation Correction — Canonical Transcript Normalization Order

Before Transcript Health, source preflight, Group Similar routing, or final
ChatGPT package creation, VideoHoarder MUST normalize the selected transcript
into its canonical mechanical representation.

Required order:

```text
selected transcript/source
  -> format detection
  -> deterministic timestamp parsing
  -> canonical segment construction
  -> canonical transcript source identity
  -> transcript/source fingerprint
  -> Transcript Health Analyzer
  -> source preflight
  -> grouping/package creation
```

Rules:

- Transcript Health MUST operate on normalized canonical transcript segments,
  not on an unparsed flattened transcript blob when parseable timestamps are
  present.
- A flattened transcript such as `[00:00:00] text [00:00:17] text ...` MUST be
  split deterministically into ordered canonical segments.
- `canonical_transcript.source = "no_transcript"` is valid only when no usable
  transcript source exists. If transcript text exists, source identity must
  describe the actual selected/normalized source.
- A transcript containing multiple parseable timestamps MUST NOT be persisted
  or exported as one `0 -> 0` canonical segment. Package creation must fail fast
  if that contradiction is detected.
- For timestamp-only text without explicit end times, the next timestamp is the
  deterministic end of the current segment. For the final segment, do NOT extend
  its end to authoritative video duration merely because the video continues;
  without an explicit source end, keep the final represented boundary at its
  source timestamp. Video duration is not proof that speech continues.
- Missing authoritative video duration remains non-fatal.
- Package validation must reject a final ChatGPT package when transcript text is
  present but the canonical source is `no_transcript`, or when multiple inline
  timestamps collapse into <=1 canonical segment.

This is an implementation clarification of V3.3.4 and does not create a new
schema or prompt version.

## V3.3.4 Implementation Correction — Usable Transcript / Unreliable Timestamp Fallback

This section supersedes any earlier V3.3.4 wording that required a video with
usable speech text to be excluded from a processing package solely because
timestamps could not be normalized.

Required behavior:

```text
usable transcript text + reliable normalized timestamps
  -> timestamped canonical segments
  -> normal timestamp-aware semantic processing

usable transcript text + missing/unreliable/unparseable timestamps
  -> preserve transcript text
  -> canonical source = untimestamped_transcript
  -> timestamps_available = false
  -> timestamp_status = unavailable_or_unreliable
  -> untimestamped_text = normalized speech text
  -> package video normally (normally CAUTION / PASS_WITH_WARNINGS)
  -> disable timestamp-dependent outputs

no usable speech text
  -> source repair / retranscription / SOURCE_INSUFFICIENT path
```

Rules:

- Timestamp failure alone MUST NOT discard, silently skip, or permanently defer
  a video when usable transcript speech text exists.
- `transcript_available` means usable semantic transcript evidence exists; it is
  no longer equivalent to `canonical_segment_count > 0`.
- Source preflight and batch routing must treat `untimestamped_text` as available
  transcript evidence.
- Transcript Health may record timestamp warnings, but timestamp-only problems
  must not force REPAIR_REQUIRED / REPAIR_RECOMMENDED when otherwise usable
  speech text can be processed safely without time navigation. Such videos may
  route as CAUTION.
- The package must explicitly carry `timestamps_available`, `timestamp_status`,
  `normalization_status`, and `untimestamped_text`.
- ChatGPT must be told not to search for, reconstruct, infer, estimate, or invent
  timestamps when `timestamps_available=false`. This saves reasoning/tokens and
  prevents fabricated time navigation.
- `chapters.v1.chapters` must be empty for the untimestamped fallback because
  the V3.3.4 chapter contract is timestamped.
- Non-time-dependent intelligence remains required when semantically supported.
- Timestamp-dependent fields in Recipes, References, Q&A, Technical Intelligence
  or Named Items must be omitted/empty when they cannot be grounded.
- A source-repair queue entry is still appropriate when transcript text itself
  is missing/unusable, or when other independent health failures make the source
  unsafe.

Package preflight must accept either:

```text
canonical_transcript.segments[]
OR
canonical_transcript.untimestamped_text
```

as valid transcript evidence for a transcript-processing package.

### Authoritative Timestamp Reliability Gate

Parseable timestamps are not automatically authoritative. Before setting
`timestamps_available=true`, VideoHoarder MUST run a deterministic timing
reliability gate over Transcript Health plus the normalized segment sequence.

Authoritative timing MUST be rejected when any of these conditions applies:

- `SEVERE_TIMESTAMP_CORRUPTION`;
- `TIMESTAMP_CORRUPTION` (invalid/overlapping ranges beyond tolerance);
- `TIMESTAMP_PARSE_WEAK`;
- `UNTIMESTAMPED_OR_UNPARSEABLE`;
- non-monotonic canonical timestamps;
- a canonical segment has `end < start`;
- canonical segment ordering overlaps beyond the deterministic tolerance.

When the gate fails but usable speech text exists:

```text
timestamps_available = false
timestamp_status = unavailable_or_unreliable
normalization_status = UNTIMESTAMPED_FALLBACK
canonical_transcript.segments = []
canonical_transcript.untimestamped_text = cleaned usable speech
timestamp_hints = compact source-provided markers when available
timestamp_hints_reliable = false
processing profile = FULL_INTELLIGENCE
```

The original timing defects remain visible in `transcript_health`; the downgrade
changes only timing authority, never semantic eligibility. Large gaps or
start/end truncation warnings alone do not automatically invalidate otherwise
monotonic, structurally valid timestamps; they remain separate coverage signals.

======================================================================
V3.3.4 SOURCE TIMESTAMP HINT PRESERVATION
======================================================================

When transcript text is usable but deterministic timestamp normalization fails:

1. The video remains packageable as semantic transcript evidence.
2. Persist cleaned semantic text as `untimestamped_text`.
3. Preserve compact source-provided timing clues separately as
   `timestamp_hints` rather than discarding them or duplicating the complete raw
   transcript. Each hint should retain the source marker, parsed seconds when
   mechanically readable, and a short nearby text excerpt.
4. Set:
   - `timestamps_available = false`
   - `timestamp_hints_available = true|false`
   - `timestamp_hints_reliable = false` for the fallback path
   - `timestamp_status = unavailable_or_unreliable`
5. Transcript Health and package validation must never promote these hints to an
   authoritative normalized timeline.
6. ChatGPT may use supplied hints only as approximate navigation clues. It must
   not spend significant reasoning effort repairing/reconstructing them, must
   not present them as exact timestamps, and must never invent missing timing.
7. Exact timestamp-dependent structured fields remain empty when no normalized
   canonical segments exist.
8. Timestamp-hint failure alone must not discard otherwise usable transcript
   text or route the video to no-transcript handling.

This design preserves potentially useful YouTube/subtitle timing context while
maintaining the separation between authoritative normalized timestamps and
approximate source hints.



======================================================================
V3.3.4 IMPLEMENTATION CORRECTION — ACTIVE LIBRARY, TRANSCRIPT RECHECK,
GLOBAL PACKAGE OPTIMIZATION AND TIMING FALLBACK
======================================================================

This section supersedes earlier V3.3.4 wording where it conflicts.

A. PHYSICAL ACTIVE LIBRARY IS AUTHORITATIVE
-------------------------------------------
- The active library is the set of videos physically present under the configured
  VideoHoarder library root.
- Historical database rows whose local folders are gone must not participate in
  normal library views, Group Similar, search/export counts, package creation,
  transcript recheck or ChatGPT processing.
- Do NOT retain deleted videos as ordinary database/library rows, planner inputs,
  report rows, index entries, counts, or maintenance targets.
- Retain only a minimal hidden deleted-ID guard record (VIDEO_ID plus optional prior
  title/channel/deletion time) used exclusively before a new download is queued.
- When the same VIDEO_ID is requested again, show an explicit confirmation that the
  video was previously downloaded and later deleted. A successful re-download removes
  that guard record because the video is active again.
- Library rebuild and Group Similar must reconcile filesystem state before use.

B. TRANSCRIPT RECHECK / REPAIR BEFORE GROUPING
----------------------------------------------
- Add a separate Recheck Missing / Bad Transcripts action.
- Group Similar may optionally run the same recheck before planner creation.
- Recheck current-library videos only.
- Re-query only missing, empty, semantically unusable, or repair-recommended
  transcript sources.
- Prefer English VTT/SRT/transcript, then configured fallback language.
- Cache unsuccessful recheck state/time to avoid repeatedly querying YouTube.
- Allow an explicit force-recheck override.
- When a better transcript is recovered:
  normalize it -> update canonical source/fingerprint -> recompute Transcript Health
  -> make it immediately eligible for normal FULL_INTELLIGENCE packaging.

C. TRANSCRIPT NORMALIZATION / TIMING CAPABILITY
-----------------------------------------------
Selected source
-> deterministic format/timestamp normalization
-> canonical transcript representation
-> transcript fingerprint
-> Transcript Health
-> package preflight

- Usable transcript speech text is FULL_INTELLIGENCE eligible even when timestamps
  are weak, missing, partial or unparseable.
- Timestamp quality is a navigation-quality signal, not a semantic-routing gate.
- Preserve questionable source timestamp markers as approximate hints when useful.
- Keep cleaned untimestamped text as the semantic evidence fallback.
- Do not create timestamp-based RESTRICTED_INTELLIGENCE packages.
- Only genuinely missing/unusable speech text belongs in source repair/no-transcript
  handling.
- Approximate timestamp hints must never be promoted to exact canonical time ranges.

D. GLOBAL PACKAGE OPTIMIZER
---------------------------
Primary objective:
  MINIMIZE TOTAL PACKAGE COUNT.

Hard constraints:
- maximum 30 videos per normal processing package;
- hard transcript/workload safety limit;
- do not split one VIDEO_ID;
- keep genuinely different processing paths separate where required.

There is NO minimum package size.

Algorithm:
1. Compute the theoretical minimum package count:
   max(ceil(video_count/30), ceil(total_workload/hard_workload_limit)).
2. Attempt to fit all compatible videos into that many packages.
3. Use Group Similar topic/parent groups only as affinity guidance.
4. Prefer same/related topics when several placements are equally feasible.
5. Rebalance globally to avoid greedy leftovers.
6. Increase package count only when a hard constraint makes the theoretical
   minimum impossible.

Examples:
- 28 compatible videos -> 1 package, not 23 + 5.
- 61 compatible videos -> 3 balanced packages rather than 30 + 30 + 1.
- 89 compatible videos -> 3 packages when workload permits.

Parent groups no longer define package boundaries and have no minimum size.
The small-group exception fields may remain for backward compatibility but are
not required to justify actual package creation.

E. FULL_INTELLIGENCE ELIGIBILITY
--------------------------------
- Good text + good timestamps -> FULL_INTELLIGENCE.
- Good text + weak timestamps -> FULL_INTELLIGENCE.
- Good text + no timestamps -> FULL_INTELLIGENCE.
- Good text + timestamp-normalization failure -> FULL_INTELLIGENCE using cleaned
  text plus approximate source hints where available.
- Incomplete but still semantically usable text -> FULL_INTELLIGENCE with warnings.
- Genuinely missing/unusable transcript -> source repair/no-transcript path.

F. ACCEPTANCE TESTS
-------------------
Add deterministic tests for:
- active filesystem count vs historical database count;
- deleted VIDEO_IDs purged from ordinary library/planners/packages/indexes/reports;
- re-download warning from the dedicated deleted-ID guard history;
- transcript recheck success, failure and cache behavior;
- recovered transcript re-normalization and health recalculation;
- no timestamp-based RESTRICTED_INTELLIGENCE package generation;
- usable untimestamped transcript remains FULL_INTELLIGENCE;
- approximate timestamp hints retained but not treated as exact;
- global minimum-package optimizer, no minimum size, max 30;
- balanced distributions without greedy tiny leftovers;
- workload-driven extra packages only when genuinely required.


---

## V3.3.4 ACTIVE-LIBRARY, TRANSCRIPT-RECOVERY, AND GLOBAL PACKAGE OPTIMIZATION ADDENDUM

### Active library is authoritative

`<VIDEOHOARDER_HOME>\VideoHoarder Videos` is the authority for current-library membership.

- A deliberately deleted video MUST be purged from ordinary database/library rows, normal counts, Group Similar planners, searches/exports, transcript rechecks, ChatGPT packages, indexes, cleanup targets and processing queues.
- Missing/unmounted local folders may be marked inactive, but they are not automatically treated as deliberately deleted.
- The only retained deleted-video reference is the minimal hidden deleted-ID guard history used by the pre-download warning.
- If the user confirms and the video is downloaded successfully again, remove its deleted-ID guard record and treat it as a normal active video.
- Library rebuild and Group Similar preflight MUST reconcile database state against the physical library.

### Transcript recheck / recovery

Provide a separate **Recheck Missing / Bad Transcripts** action and run the same targeted preflight automatically before Group Similar unless disabled.

Recheck eligibility is deliberately narrow and deterministic:

- Grade A: never automatically recheck online.
- Grade B: never automatically recheck online.
- Grade C: recheck when due; default cache interval 7 days.
- Grade D: recheck when due; default cache interval 3 days.
- Grade F or missing/unusable transcript: recheck when due; default cache interval 1 day.
- Force Recheck bypasses the time cache but MUST NOT broaden eligibility to A/B. There is no automatic all-transcripts diagnostic mode.

Prefer English source captions/transcripts, then the configured fallback source path. Never delete or overwrite the existing transcript before a candidate replacement has been downloaded, normalized, fingerprinted and health-scored. Stage the candidate first and compare old versus new.

Replacement rules:
- missing/unusable -> accept any usable candidate;
- D -> accept C/B/A; accept D only when materially better;
- C -> accept B/A; accept C only when materially better;
- never replace a usable transcript with a worse/unusable candidate.

For same-grade candidates, require a material health improvement (implementation threshold: at least 5 health-score points or removal of a hard failure). Preserve the previous usable transcript as a backup/version before installing a better candidate. If lookup fails or the candidate is not better, retain the existing transcript unchanged.

When a better VTT/SRT/transcript is recovered:

`staged source -> canonical normalization -> fingerprint -> Transcript Health -> compare -> install only if better -> grouping/package eligibility`

### Usable text is FULL_INTELLIGENCE regardless of timing

Timestamp quality MUST NOT create `RESTRICTED_INTELLIGENCE` packages when usable speech text exists.

- usable text + reliable timestamps -> FULL_INTELLIGENCE
- usable text + weak/partial timestamps -> FULL_INTELLIGENCE
- usable text + no reliable timestamps -> FULL_INTELLIGENCE
- usable text + normalization failure -> FULL_INTELLIGENCE with untimestamped semantic text and retained approximate source hints
- genuinely missing/unusable semantic text -> source repair or no-transcript path

Transcript Health remains mechanical metadata. Poor timing may create warnings, approximate precision, or repair recommendations, but timing alone does not remove semantic eligibility.

### Approximate timestamp hints

If normalization cannot safely produce authoritative segments, retain compact source timestamp hints and nearby transcript excerpts. Mark them approximate/unreliable. Do not discard them, but do not promote them to exact chapter boundaries.

### Global package optimizer

There is **no minimum package size**.

Primary objective: minimize the total number of processing packages.

Hard constraints:

- maximum 30 videos per processing package;
- transcript and true no-transcript processing paths remain separate where required;
- transcript/workload hard limits must not be exceeded;
- one VIDEO_ID belongs to one processing package in a run;
- no cross-video semantic evidence mixing.

Secondary objectives:

- preserve topic affinity where practical;
- balance video count and transcript workload;
- avoid greedy leftovers.

The optimizer starts from the theoretical lower bound:

`max(ceil(video_count / 30), ceil(total_transcript_workload / hard_workload_limit))`

and increases package count only when a hard constraint makes that bound impossible. Parent groups and precise topic subgroups are affinity metadata, not rigid package boundaries.

Examples:

- 28 compatible videos -> one package, not 23 + 5.
- 61 compatible videos -> three balanced packages rather than 30 + 30 + 1 when workload permits.
- 89 compatible videos -> three packages such as 30 + 30 + 29.
- A small final package is allowed; there is no minimum-size validation rule.

Package metadata MUST record actual `video_count`, actual `batch_size`, target size (normally 25 for convenience), maximum size 30, transcript workload, and split reason.

### Deleted-video re-download guard

Deleted videos do not remain in ordinary library/database/index/report state. Keep only a minimal hidden guard-history record used exclusively by the pre-download check. On a new download request:

- active VIDEO_ID -> normal already-downloaded handling;
- VIDEO_ID in deleted guard history -> explicit confirmation to download again;
- unseen VIDEO_ID -> normal download.

The guard history MUST NOT be included in library counts, exports, deleted/missing reports, Group Similar, transcript health/recheck, cleanup, Knowledge/AI indexes, ChatGPT package creation or other normal processing. A successful re-download removes the guard record.


======================================================================
V3.3.4 IMPLEMENTATION CORRECTION — SPEECH COVERAGE, COMPLETENESS, AND VTT NORMALIZATION
======================================================================

This section is authoritative where earlier wording could be read as equating
subtitle time coverage with spoken-content completeness.

A. ONE-VTT SOURCE POLICY
------------------------
For each VIDEO_ID, semantic packaging uses exactly one selected transcript source:

1. prefer the selected English VTT/SRT/transcript when available and usable;
2. otherwise use the configured best available fallback-language source;
3. do not concatenate multiple locale/language subtitle tracks into the normal
   semantic pass.

B. DETERMINISTIC WEBVTT NORMALIZATION
-------------------------------------
Before Transcript Health and semantic packaging, normalize the selected WebVTT
mechanically. Allowed operations include:

- remove WebVTT headers, cue settings and presentation markup;
- remove inline word-timing / `<c>` display markup while preserving words;
- collapse progressive/rolling YouTube caption overlap so display repetition is
  not mistaken for spoken repetition;
- collapse exact duplicated cues;
- retain reliable source timing on the normalized spoken sequence.

Normalization MUST NOT paraphrase, summarize, translate, repair ASR meaning,
reconstruct missing speech, or guess uncertain words/numbers.

C. THREE INDEPENDENT TRANSCRIPT DIMENSIONS
------------------------------------------
Keep these dimensions separate:

- `transcript_usability`: is there useful spoken semantic text?
- `transcript_completeness`: how confidently does the selected transcript cover
  the video's meaningful spoken content?
- `timestamp_reliability`: are exact normalized time ranges safe for navigation?

Recommended completeness values:

```text
COMPLETE
LIKELY_COMPLETE
PARTIAL
UNKNOWN
NONE
```

`USABLE` is not a completeness state. A long transcript is not automatically
complete, and a short transcript is not automatically incomplete. Character or
word count may inform usability but MUST NOT by itself prove completeness.

D. VIDEO DURATION != SPEECH DURATION
------------------------------------
A subtitle track may legitimately end long before the video ends because the
remaining media contains no speech. Therefore:

```text
video_duration = 10:00
last_caption = 05:20
```

does NOT by itself establish truncation.

Duration-tail signals may produce:

```text
LARGE_UNSUBTITLED_TAIL
END_COVERAGE_UNCERTAIN
```

but MUST NOT produce a hard `CLEAR_MAJOR_TRUNCATION`/source-failure conclusion
without independent evidence that meaningful speech is missing.

Independent evidence may include an authoritative alternate source, audio/speech
analysis, a known caption-loss condition, or another deterministic source record
that establishes speech continues outside the selected transcript. When such
evidence exists, use `CONFIRMED_MISSING_SPOKEN_CONTENT` and set completeness to
`PARTIAL`.

E. SEMANTIC ELIGIBILITY
-----------------------
- usable speech + reliable timing -> FULL_INTELLIGENCE;
- usable speech + unreliable timing -> FULL_INTELLIGENCE using untimestamped text;
- usable speech + completeness UNKNOWN -> FULL_INTELLIGENCE with coverage caution;
- usable speech + confirmed PARTIAL coverage -> process supported evidence only and
  route/reprocess according to materiality;
- no usable speech -> source repair/no-transcript path.

F. PERSISTENT SUBTITLE / TRANSCRIPT FILE CONTRACT
-------------------------------------------------
For every successfully normalized video folder, the persistent `_data` subtitle/transcript
set MUST contain exactly these three canonical artifacts, all derived from the SAME
selected winning VTT:

```text
<VIDEO_ID>.<best-language>.vtt
<VIDEO_ID>.srt
<VIDEO_ID>.transcript.txt
```

Rules:

1. Candidate selection MUST NOT use alphabetic filename order as the deciding rule.
2. Score/select candidates using source preference plus language, usability/health,
   timing validity, corruption/repetition signals and useful-content coverage.
3. English remains preferred. A configured fallback language is used only when no
   usable English candidate exists.
4. Generate the canonical SRT and canonical transcript from the SAME normalized spoken sequence produced from the selected winning VTT. The canonical SRT MUST NOT be a raw cue-for-cue copy when the VTT uses progressive/rolling display captions; it must use the deduplicated canonical spoken sequence. Do not generate the SRT from one VTT and the transcript from another.
5. The selected winning VTT itself MUST be retained.
6. Inferior VTT/SRT variants and legacy duplicate transcript TXT artifacts anywhere inside the persistent per-video folder may be physically removed ONLY AFTER all three canonical artifacts have been written, reopened and validated as non-empty/usable. Comment transcripts are a separate artifact and are excluded from this three-file count.
7. Cleanup is transactional. If winning-source selection, SRT creation, transcript creation, verification, moving/removing an inferior artifact, or final exact-count verification fails, the cleanup MUST report failure and restore any inferior artifacts already staged for removal where possible. It MUST NOT report success while extra VTT/SRT/transcript variants remain.
8. Record an audit trail containing the winning source and every removed path.
9. Temporary/cache transcript representations outside the final video's persistent
   `_data` folder may continue to exist for internal processing; this three-file contract
   applies to the permanent per-video library artifacts.
10. Database artifact paths and artifact-manifest scanning MUST resolve the canonical
    three-file set after cleanup and remain backward-compatible when reading older
    folders that have not yet been migrated.
11. The GUI MUST expose an explicit whole-library maintenance control for this contract. With VIDEO_IDs left blank it may run across all active library videos; with VIDEO_IDs supplied it must limit cleanup to those videos. This action is separate from downloading new subtitles and may be run against an existing library.

Never infer content for media portions not represented by transcript evidence.

F. PROVENANCE / PACKAGE FIELDS
------------------------------
The canonical evidence object should carry, where available:

- selected source identity / language;
- `transcript_usability`;
- `transcript_completeness`;
- `timestamp_reliability` / `timestamps_available`;
- Transcript Health reason codes;
- source/canonical transcript fingerprint.

This metadata is internal processing context and must not become a normal visible
report section.

G. ACCEPTANCE TESTS
-------------------
Regression tests MUST cover at least:

- progressive YouTube rolling-caption VTT normalization;
- exact duplicate cue collapse;
- music/non-speech-only captions;
- usable speech with corrupt timestamps -> FULL_INTELLIGENCE fallback;
- 10:00 video + VTT ending 05:20 + no proof of later speech -> NOT hard truncation;
- same timing plus independent proof of later speech -> PARTIAL / confirmed missing
  spoken content;
- long transcript with unknown whole-video speech coverage -> not automatically
  COMPLETE from character count;
- unknown duration -> no invented completeness/timing conclusion.


# V3.3.4 FINAL SOURCE-FIDELITY AND PACKAGE-QUALITY ADDENDUM

This addendum is normative and resolves any ambiguous earlier wording.

## AF. Source fidelity boundary

Semantic processing answers two questions only:

1. Does the supplied allowed video evidence say/support this?
2. Does the generated intelligence represent that evidence faithfully?

It does NOT answer whether the video's statement is objectively true. External
fact-checking, medical/scientific adjudication, censorship/correction, or replacement
of a speaker's position is outside this workflow unless separately requested.

Claims, recommendations, opinions, predictions and disputed assertions should retain
natural attribution where needed to avoid converting source claims into independently
verified facts. Attribution must not become repetitive boilerplate.

`SOURCE_INSUFFICIENT` means the supplied evidence is insufficient to determine
reliably what the video says. It must never mean merely "not externally verified" or
"the model doubts the claim." Timestamp unreliability alone remains insufficient when
usable semantic text exists.

## AG. Semantic-authoring quality contract

- Detailed Summary must cover complete available semantic evidence and contain
  video-specific substance. Generic/repeated section shells are invalid authoring.
- Capture reasoning, steps, examples, quantities, comparisons, recommendations,
  cautions and conclusions only when present; never force absent categories.
- Named Items are semantically identified, meaningful, identifiable things actually
  discussed. Title-token, keyword-frequency and generic-concept extraction is invalid.
- Q&A must provide video-specific retrieval value and be directly answerable from the
  supplied evidence. Mechanical chapter-to-question conversion is invalid.
- Provenance must reference evidence that actually supports the associated output.
  Reusing the first N segment IDs as generic whole-video provenance is invalid.
- Description/comments/sponsor/affiliate material remain prohibited semantic evidence
  except for narrowly permitted identity/orchestration fields explicitly defined by
  the package contract.
- Per-video Phase-5 self-audit checks coverage, fidelity, attribution, invention,
  prohibited-source leakage, section specificity, provenance and timing before save.

Deterministic code may validate structural manifestations of these rules (valid IDs,
valid provenance references, placeholders, extreme repeated templates, timestamp
capability, schema/status rules). It MUST NOT determine external factual truth or
replace model semantic understanding.

## AH. Package input-quality grade and processing priority

Every final semantic-processing package MUST receive a deterministic, versioned input
evidence-quality record. This is package-level orchestration metadata, not semantic
status and not a judgment of content credibility.

Required shape:

```json
{
  "package_quality": {
    "analyzer_version": "1.0",
    "score": 0,
    "grade": "A|B|C|D|F",
    "processing_priority": 1,
    "transcript_grade_distribution": {"A":0,"B":0,"C":0,"D":0,"F":0},
    "usable_transcripts": 0,
    "timestamp_reliable": 0,
    "timestamp_fallback": 0,
    "severe_signal_count": 0,
    "reason_codes": []
  },
  "workload": {
    "class": "LOW|MEDIUM|HIGH",
    "transcript_characters": 0
  }
}
```

### AH.1 Deterministic score

For N videos (N > 0), compute per-video evidence points from the already persisted
Transcript Health grade:

```text
A = 100
B = 85
C = 65
D = 40
F = 15
```

Base score = arithmetic mean of those points. Then apply package-level mechanical
penalties:

```text
- 5 * (timestamp_fallback / N)
- 5 * (severe_signal_video_count / N)
```

Round to nearest integer and clamp to 0..100. A video is counted once in
`severe_signal_video_count` when its health reason codes contain one or more severe
mechanical failure/corruption signals; multiple signals on one video do not stack.
Missing/unknown signals are not invented.

Grade thresholds:

```text
A = 90..100
B = 80..89
C = 65..79
D = 45..64
F = 0..44
```

This distribution-based score intentionally prevents one isolated D/F transcript from
automatically assigning the whole package that grade.

### AH.2 Workload is separate

Workload MUST NOT reduce package quality grade. Continue using the existing deterministic
workload calculation/cap for package balancing. Expose workload class independently.
A high-workload package may still be Grade A. For the current V3.3.4 transcript-character
workload configuration (`target=150000`, `hard=250000`), classify workload deterministically as:

```text
LOW    = 0..75000 transcript characters
MEDIUM = 75001..150000 transcript characters
HIGH   = 150001..250000 transcript characters
```

If those configured target/hard limits change in a future version, update this documented
classification and its tests together rather than silently changing only code.

### AH.3 Processing priority

After final immutable package boundaries/IDs are created, assign processing priority
across that batch set by:

1. higher package-quality score first;
2. higher proportion of reliable timestamps;
3. lower severe-signal-video proportion;
4. stable package ID ascending as the final deterministic tie-break.

Priority is 1-based. Reordering MUST NOT rename package IDs, change package membership,
change hashes, or rebuild package boundaries. Batch summaries/indexes should display
package ID, actual video count, grade, score, workload class and processing priority.

### AH.4 Separation of statuses

Never overwrite `package_quality` after semantic processing. Keep independent:

- INPUT package quality: score/grade/priority;
- workload: operational capacity;
- per-video semantic status: PASS / PASS_WITH_WARNINGS / REPROCESS_RECOMMENDED /
  SOURCE_INSUFFICIENT;
- package semantic/artifact completion statuses.

A D/F package remains processable when its videos contain usable evidence. Package
grade must never automatically set semantic status or create RESTRICTED_INTELLIGENCE.
