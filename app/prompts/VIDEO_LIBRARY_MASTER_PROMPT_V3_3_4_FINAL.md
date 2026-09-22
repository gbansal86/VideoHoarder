======================================================================
VIDEO LIBRARY — CHATGPT TRANSCRIPT INTELLIGENCE PROCESSOR — V3.3.4 FINAL
======================================================================

VERSION NOTE
======================================================================

This V3.3.4 file contains the complete V3.3.3 Final Master Prompt plus the
V3.3.4 Transcript Health integration contract.

All V3.3.3 requirements remain authoritative unless an explicit V3.3.4 rule
below supersedes them.

V3.3.4 does NOT change the semantic-authoring architecture. It adds
deterministic transcript-health metadata as a mechanical diagnostic/routing
signal. ChatGPT remains independently responsible for complete current-video
semantic understanding, semantic ASR/uncertainty judgment, semantic
self-review, and final semantic status.


PURPOSE
======================================================================

Analyze each supplied video transcript and create a detailed,
well-structured intelligence report for the video library.

The report should make it possible to understand what is actually
discussed in the video without reading the complete transcript.

The output must also provide structured information that the
application can use for:

- video renaming
- chapters
- search
- tags
- categorization
- transcript navigation
- recipes/preparations
- references
- related-video retrieval
- technical information extraction
- future clip extraction

Process EACH video independently.

Never mix information from different VIDEO_IDs.


======================================================================
INPUT
======================================================================

Input may contain:

- VIDEO_ID
- authoritative video metadata
- timestamped transcript
- untimestamped transcript, if supplied
- existing chapters/sections, if supplied

DO NOT use the video description for transcript analysis.

DO NOT use viewer comments for transcript analysis.

The original video description and viewer comments are handled
separately by the application and may be attached unchanged to the
final report.


======================================================================
SOURCE PRIORITY
======================================================================

Use information in this priority:

1. Timestamped transcript
2. Untimestamped transcript, if supplied
3. Authoritative video metadata
4. Existing chapter/section information, if supplied

Metadata determines video identity.

The transcript determines what is actually discussed in the video.

Never allow metadata/title wording to override clear transcript
evidence about the actual content.


======================================================================
PROMOTIONAL / SPONSOR CONTENT — EXCLUDE COMPLETELY
======================================================================

Do NOT retain promotional information in the intelligence report.

Completely exclude:
- sponsor segments
- advertisements
- affiliate promotions
- coupon/discount codes
- promotional URLs
- calls to purchase unrelated products
- sponsor product demonstrations
- promotional brand claims
- promotional outro material

Promotional material must NOT influence:
- New Title
- Category
- Tags
- Chapters
- Detailed Timestamped Summary
- Recipes / Preparations
- References
- Q&A
- Named Items Discussed
- search intelligence

If a promotional segment interrupts useful content, skip that time range
and continue with the actual video content.

A product should only remain when it is genuinely part of the video's
primary non-promotional subject.


======================================================================
PROCESSING ARCHITECTURE — ONE MAIN PASS, FIVE INTERNAL PHASES
======================================================================

IMPORTANT: Each video MUST be semantically processed independently as
one complete unit. The semantic processor must have access to the complete
allowed evidence for the CURRENT video and must perform the five internal
phases below before the result is accepted.

No other video's transcript or semantic content may influence the current
video.

The normal/default path is ONE complete semantic read of the current
video, with all five phases performed sequentially so later phases use the
decisions made by earlier phases. Do NOT resend the complete transcript
separately for Chapters, Summary, Recipes, Q&A, Tags, Named Items, or
other sections.

The implementation MAY use an additional targeted semantic operation when
validation identifies a specific weak section or recoverable issue. Such a
repair must use only the minimum relevant evidence and dependencies needed
for that issue; it must not trigger unnecessary regeneration of good
sections or another full transcript read unless genuinely required.

Quality and semantic correctness take priority over enforcing a literal
model-call count, while semantic isolation and token efficiency remain
mandatory.

----------------------------------------------------------------------
PHASE 1 — UNDERSTAND, CLEAN AND SEGMENT
----------------------------------------------------------------------

Before drafting output:

- understand the complete transcript as one video
- identify the true primary topic and supporting topics
- identify real topic changes and canonical chapter boundaries
- identify and exclude promotional/sponsor/affiliate material
- recognize obvious transcript fragmentation
- identify uncertain ASR words, names, quantities or technical terms
- do not guess uncertain important values
- distinguish useful content from repetition, recap and filler
- establish the canonical content timeline that later phases must use

Do not generate final search/index fields before this understanding is
established.

----------------------------------------------------------------------
PHASE 2 — BUILD THE DETAILED CONTENT INTELLIGENCE
----------------------------------------------------------------------

Using Phase 1 understanding:

- write the Detailed Timestamped Summary from the actual substantive content of
  each topic, not from a reusable/template paragraph shell
- preserve the canonical chapter/topic structure
- capture important explanations, reasoning, claims, quantities, examples, methods,
  recommendations, cautions, comparisons and conclusions WHEN THEY ARE ACTUALLY
  PRESENT; never manufacture a category merely because this list mentions it
- cover the complete available semantic evidence, not only opening segments, titles,
  headings or a few convenient excerpts
- keep related information together
- preserve meaningful detail without turning the report into a transcript dump
- avoid unnecessary duplication and generic filler that could fit unrelated videos

----------------------------------------------------------------------
PHASE 3 — SPECIALIZED EXTRACTION
----------------------------------------------------------------------

Using the established understanding and summary, extract only when
meaningful and supported:

- Recipes / Preparations
- Meaningful References
- useful Questions & Answers
- IT / Technical Intelligence when applicable
- playlist/series relationships when clearly supported
- exact quantities, ratios, durations, frequencies, commands or other
  structured details that belong in those sections

Do not create optional sections merely because a field exists.

----------------------------------------------------------------------
PHASE 4 — LIBRARY AND SEARCH INTELLIGENCE
----------------------------------------------------------------------

Only after the video's content is understood, generate:

- New Title
- Category
- Subcategory
- Primary Topic
- Content Type
- Tags
- internal title/search intelligence
- Named Items Discussed
- internal concepts, aliases, search phrases and questions answered

These fields must reflect the actual non-promotional content rather
than isolated transcript words.


======================================================================
REFERENCE-RUN REFINEMENTS — V2
======================================================================

These rules refine quality based on the 17-video reference benchmark.
They do NOT add another transcript pass and do NOT change the architecture.

----------------------------------------------------------------------
A. ADAPTIVE SUMMARY COMPLETENESS
----------------------------------------------------------------------

Summary length is determined by information density, not video duration
alone.

For every canonical chapter, preserve each DISTINCT useful information
unit that materially helps understanding, retrieval, navigation or
practical use. An information unit may be:

- an explanation or reason
- a meaningful claim or conclusion
- a named item with substantive discussion
- a quantity, ratio, dosage, frequency or duration
- a preparation or method
- a caution or limitation stated in the source
- a comparison or alternative
- a study/reference actually identified
- an important example
- a practical recommendation

Do not compress several distinct useful units into a vague sentence such
as "the video discusses diet and lifestyle."

At the same time, do not inflate simple material. Repetition, filler,
recaps and promotional content do not count as information units.

For a dense chapter, multiple explanatory paragraphs or focused
subsections are allowed. For a simple chapter, one concise paragraph is
enough.

----------------------------------------------------------------------
B. COVERAGE LEDGER DURING PHASE 5
----------------------------------------------------------------------

During INTERNAL self-review, mentally classify each major useful
information unit from the transcript as exactly one of:

- REPRESENTED
- INTENTIONALLY OMITTED AS DUPLICATE/FILLER
- PROMOTIONAL
- UNCERTAIN / NOT RELIABLY RECOVERABLE

Do not output this ledger.

If a useful, non-promotional, reliably recoverable information unit is
neither represented nor intentionally omitted as duplicate/filler,
repair the appropriate section before returning the result.

This is a coverage check, NOT a second transcript pass.

----------------------------------------------------------------------
C. LOCALIZE ASR UNCERTAINTY
----------------------------------------------------------------------

Attach uncertainty to the smallest affected element possible.

If one name, number, ingredient or sentence is uncertain but the rest of
the chapter is understandable:
- preserve the reliable surrounding information normally
- mark or omit only the uncertain element internally
- do NOT make the whole chapter vague

Escalate a whole chapter/video to warning status only when corruption
materially prevents reliable recovery of important content.

Never reconstruct a damaged proper noun, quantity, medicine, ingredient,
technical term or URL from outside knowledge.

----------------------------------------------------------------------
D. CHAPTER NAVIGATION-VALUE TEST
----------------------------------------------------------------------

Create a new chapter only when BOTH are true:

1. there is a meaningful subject/method/stage change, AND
2. a viewer could reasonably want to jump directly to the new part.

Do not split merely because a new example, ingredient or brief tip is
mentioned.

Do split when a new preparation, major item, major myth/question,
procedure stage, comparison target or clearly independent subject begins.

After drafting chapters, check whether any adjacent chapters would be
more useful merged and whether any overloaded chapter contains two
independently navigable subjects.

----------------------------------------------------------------------
E. TITLE COMPRESSION CHECK
----------------------------------------------------------------------

After generating the accurate New Title, perform one compression check.

Prefer the shortest title that preserves the video's distinguishing
search value.

When listing many items makes the title crowded:
- keep the 2–5 most distinguishing named items, OR
- use an accurate umbrella phrase for the remaining items

Do not remove a term if doing so makes the title materially less
searchable or changes the subject.

Accuracy always outranks brevity.

----------------------------------------------------------------------
F. RECIPE FIELD COMPLETENESS AUDIT
----------------------------------------------------------------------

For every genuine preparation, Phase 5 must explicitly check the source
for each of these fields:

Ingredients; Ratio/Quantity; Preparation; Usage; Frequency; Duration;
Storage; Important Tip; Caution.

Include a field only when stated, but do not miss a stated field.

If a preparation is repeated in a recap, merge the recap only when it
adds a new supported actionable detail; never create a duplicate recipe.

----------------------------------------------------------------------
G. Q&A RETRIEVAL-VALUE TEST
----------------------------------------------------------------------

Generate Q&A when the transcript clearly answers a question that a user
would plausibly search or ask independently and the answer can be given
concisely without duplicating a large summary passage.

High-value triggers include:
- explicit question-and-answer wording
- myth -> correction
- "can/should/how often/how much/when/why/which" guidance
- comparisons with a clear decision answer
- troubleshooting or eligibility questions

Do not create Q&A merely by turning every chapter heading into a
question.

For a video with several clearly answered practical questions, prefer a
small set of the highest-value questions rather than omitting Q&A
entirely.

----------------------------------------------------------------------
H. NAMED ITEMS PRECISION
----------------------------------------------------------------------

"Named Items Discussed" is primarily an entity/item index, not a concept
index.

Prefer concrete identifiable:
- foods and ingredients
- herbs, medicines and supplements
- products and tools
- exercises, techniques and treatments
- books, studies and named resources
- people, companies and organizations
- software, technologies and services
- identifiable locations

Include a disease/condition only when it functions as a specific named
subject that materially improves retrieval.

Normally EXCLUDE broad abstract concepts, physiological variables and
systems when they merely describe the topic, for example:
- health
- wellness
- digestion
- hormones
- testosterone as a general topic
- Ayurveda as a general system
- Shukra Dhatu or Ojas when used only as explanatory concepts

An abstract concept may still appear in Category, Tags, Chapters or the
Detailed Summary.

Do not duplicate an item in Named Items merely because it already exists
as a generic tag; include it because it is an important identifiable
entity/item in the source.

----------------------------------------------------------------------
I. FINAL CROSS-SECTION CONSISTENCY
----------------------------------------------------------------------

Before returning:
- every chapter must have a matching detailed-summary topic
- every recipe timestamp must fall within the relevant chapter/source
- important named ingredients/items used in recipes should not be lost
  from the explanatory summary when central
- Q&A answers must agree with the detailed summary
- Named Items must remain the LAST visible content section
- optional empty sections must remain omitted
- no internal quality/status fields may leak into the visible report


----------------------------------------------------------------------
PHASE 5 — INTERNAL SEMANTIC SELF-REVIEW
----------------------------------------------------------------------

Before returning the result, review the complete record against the
allowed source material.

Check for:

- missing important content
- invented or unsupported information
- incorrect or inconsistent timestamps
- incorrect chapter boundaries
- chapter/summary mismatch
- promotional leakage
- duplicate information
- weak/generic tags
- poor or copied New Title
- unsupported numerical counts
- recipe/preparation errors
- recap mistakenly extracted as a second recipe
- uncertain ASR terms presented as certain
- meaningful references incorrectly omitted or fabricated
- low-value/mechanical Q&A
- Named Items that are missing, trivial or promotional
- Named Items not being the final visible content section
- violation of any visibility or formatting rule

Correct issues that can be corrected confidently from the supplied
source before returning the final record.

Do NOT output these five internal phases as visible report sections.
Return only the final structured intelligence result and the internal
processing-quality fields defined below.



======================================================================
SEQUENTIAL PACKAGE PROCESSING
======================================================================

When a package contains multiple videos, process the videos STRICTLY
SEQUENTIALLY in the order supplied by the package.

Required behavior:

1. Fully finish VIDEO 1 before starting VIDEO 2.
2. For the current video, complete Pass 1, deterministic validation,
   any optional targeted Pass 2, final status assignment and persistence.
3. Only then begin the next VIDEO_ID.
4. Do NOT process multiple videos from the same package concurrently.
5. Do NOT batch multiple transcripts into one semantic model call.
6. Keep every VIDEO_ID semantically isolated from every other VIDEO_ID.
7. A weak or failed video must not stop the sequence; record its status,
   add it to the reprocessing manifest when required, and continue to
   the next video.

Package order is therefore:

VIDEO 1 -> complete -> VIDEO 2 -> complete -> VIDEO 3 -> complete -> ...

This sequential rule is intentional. It prioritizes isolation,
traceability, predictable token usage and easy recovery over maximum
throughput.




======================================================================
PACKAGE SIZE, CURRENT-VIDEO CONTEXT AND CHECKPOINT / RESUME
======================================================================

The normal package target is approximately 25 videos, there is NO minimum package size, and the hard maximum is 30 videos. The application should minimize the total number of packages subject to hard workload and processing-path constraints.

Package size must NEVER determine semantic model context size.

For a package containing 25 videos:

- Process VIDEO_IDs strictly sequentially in package order.
- Load/send to Pass 1 only the CURRENT video's authoritative metadata,
  allowed transcript evidence and required processing instructions.
- Do NOT place the other 24 transcripts into the current video's model
  context.
- Do NOT keep previously processed video transcripts in the semantic
  context for later videos.
- Fully persist the current video's modular section files, assembled
  JSON/HTML, validation result and processing status before advancing.
- Checkpoint package progress after EVERY video.
- If processing stops or crashes after VIDEO N, a resumed run must keep
  all already completed valid results and continue from the first
  unfinished video rather than restarting the package.
- Completed videos must not consume model tokens again merely because
  the package is resumed.
- Use stored source fingerprints and prompt/version metadata to decide
  whether an already completed result is still reusable.
- A video already marked for later source/package recreation must not
  block checkpointing or continuation of the current package.
- Smaller packages may be used for exceptionally large transcripts or
  operational constraints, but 25 videos is the normal target size.

Conceptually:

25-video package
  -> VIDEO 1 only in semantic context -> finish/save/checkpoint
  -> VIDEO 2 only in semantic context -> finish/save/checkpoint
  -> ...
  -> VIDEO 25 only in semantic context -> finish/save/checkpoint
  -> package summary + reprocessing manifest

The total token requirement should therefore depend primarily on the
individual videos being processed, not on how many videos are grouped
inside the package.


======================================================================
MODULAR PHASE-1 SECTION FILES
======================================================================

Pass 1 remains one complete semantic processing pass with five internal
phases. Its normal/default implementation is one complete semantic read of
the current video; the architecture does not require a literal fixed model-
call count when a targeted repair is genuinely needed.
However, after that call the application MUST persist the resulting
intelligence as separate modular section files in addition to keeping
an assembled final record.

The purpose is repairability: if one section is later found to be weak,
that section can be manually edited, regenerated, or deterministically
changed without regenerating the other good sections.

Recommended per-video structure:

VIDEO_ID/
  source/
    source_manifest.json
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

Rules:

- The LLM should NOT be called once per section during normal Pass 1.
- Pass 1 returns one structured result; CODE splits that result into
  the modular section files.
- Each section file is the authoritative editable source for that
  section after persistence.
- The assembled JSON and HTML are generated FROM the section files.
- Never treat HTML as the authoritative intelligence source.
- A manual edit to one section file must require only deterministic
  reassembly and HTML rerendering; it must consume zero LLM tokens.
- A code-rule change affecting only one section should, when safe, update
  or migrate only that section and then reassemble.
- If semantic regeneration is required for one bad section, send only
  the minimum transcript evidence and dependencies needed for that
  section and replace only that section file.
- Do not regenerate unaffected sections merely because one section is
  replaced.
- Preserve backups/version history when replacing a section.
- Record which sections were manually edited, code-modified or
  AI-regenerated.

Dependencies must be respected. In particular:

- Detailed Summary should remain coherent with Chapters.
- Recipes/References/Q&A timestamps must remain valid against the source
  timeline.
- Title/Category/Tags/Search Intelligence should remain grounded in the
  video's actual content.
- Named Items should remain consistent with the final intelligence.
- If changing one section creates a dependency conflict, flag the
  dependent section(s) for validation rather than silently rewriting
  them.

For each section maintain internal metadata such as:

- section_name
- section_status
- source_fingerprint
- prompt_version
- generated_by: pass_1 | pass_2 | manual | code_migration
- generated_at
- last_modified_at
- validation_warnings
- dependency_warnings

Suggested section statuses:

- PASS
- PASS_WITH_WARNINGS
- REPLACE_RECOMMENDED
- EMPTY_BY_DESIGN

Optional sections that are legitimately absent should use
EMPTY_BY_DESIGN internally; they must still be omitted from the visible
HTML report.

The package-level reprocessing manifest remains video-oriented for
source/package recreation, while `section_status.json` identifies
individual sections that can be repaired without recreating the whole
video package.


======================================================================
PROCESSING QUALITY, NON-BLOCKING FAILURE AND REPROCESSING
======================================================================

A difficult or low-quality video must NEVER cause the rest of a package
to fail.

Each VIDEO_ID must finish independently with one of these internal
processing statuses:

- PASS
  The result is suitable for the permanent intelligence library.

- PASS_WITH_WARNINGS
  The result is usable, but one or more minor uncertainties should be
  recorded.

- REPROCESS_RECOMMENDED
  The result is not trustworthy enough for permanent-library acceptance
  without another package/source attempt. Preserve any usable result,
  record why reprocessing is recommended, and continue with the next
  VIDEO_ID.

- SOURCE_INSUFFICIENT
  The supplied semantic transcript/evidence is too incomplete, corrupt or
  contradictory to determine reliably WHAT THE VIDEO SAYS. This status is about
  source recoverability, not external truth or independent verification. A claim
  must never become SOURCE_INSUFFICIENT merely because it is controversial,
  medically/scientifically questionable, unusual, disputed, or not externally
  verified. Poor or unreliable timestamps ALONE do not qualify when usable speech
  text remains; in that case continue FULL_INTELLIGENCE with untimestamped semantic
  evidence and approximate source timing hints only. Record the reason and continue
  with the next VIDEO_ID.

Never abort the package merely because one VIDEO_ID receives
PASS_WITH_WARNINGS, REPROCESS_RECOMMENDED or SOURCE_INSUFFICIENT.

Do not repeatedly retry the same video inside the main processing pass.

For every video, return these INTERNAL machine-readable quality fields:

- processing_status
- processing_warnings
- reprocess_recommended
- reprocess_reasons
- uncertain_items
- targeted_review_hints

Rules:

- `processing_warnings` should contain only concrete useful warnings.
- `reprocess_recommended` is true only for REPROCESS_RECOMMENDED or
  SOURCE_INSUFFICIENT.
- `reprocess_reasons` must be concise and actionable.
- `uncertain_items` should identify important ASR/source uncertainties
  without guessing their correct value.
- `targeted_review_hints` should identify the smallest useful timestamp
  ranges or sections for an optional targeted second-pass review.
- These processing-quality fields are INTERNAL and must NOT be printed
  as ordinary sections in the human-readable video report.
- A video with REPROCESS_RECOMMENDED or SOURCE_INSUFFICIENT must still
  allow package processing to continue.

At package level, the application should collect all VIDEO_IDs with
`reprocess_recommended = true` into a reprocessing manifest so a new
package can later be created only for those videos.


======================================================================
1. TITLE & SEARCH INTELLIGENCE
======================================================================

Create accurate title and search intelligence for the video.

----------------------------------------------------------------------
VISIBLE TITLE INFORMATION
----------------------------------------------------------------------

The human-readable report should show:

Original Title:
<exact original metadata title>

New Title:
<generated title>

The New Title is EXTREMELY IMPORTANT.

`new_title` is the final generated title that the application may use
to rename:

- the video file
- associated media files
- transcript files
- report files
- related video folder, where applicable

There should be ONE definitive generated rename-title field:

new_title

Do not create several competing generated titles.

----------------------------------------------------------------------
ORIGINAL TITLE
----------------------------------------------------------------------

`original_title` must remain EXACTLY as supplied in authoritative
metadata.

Do NOT:

- translate it
- rewrite it
- clean it
- shorten it
- change capitalization
- remove emojis
- replace regional/common names
- correct grammar

It represents the original source identity.

----------------------------------------------------------------------
NEW TITLE
----------------------------------------------------------------------

Generate `new_title` primarily from what is actually discussed in the
transcript.

The New Title should be:

- accurate
- descriptive
- searchable
- natural English
- suitable for a filename
- reasonably concise
- specific
- based on actual recoverable content

Prefer identifiable names and subjects over vague wording.

----------------------------------------------------------------------
ACTUAL NAMES ARE IMPORTANT
----------------------------------------------------------------------

If the original title says:

"7 Foods for Grey Hair"

and the transcript identifies:

- Amla
- Walnuts
- Sesame Seeds
- Spinach
- Eggs
- Lentils
- Moringa

do not simply generate:

"7 Foods for Grey Hair"

Use actual identifiable subjects when this improves the title.

For example:

"Amla, Walnuts, Sesame & Other Foods for Grey Hair"

----------------------------------------------------------------------
DO NOT TRUST UNSUPPORTED COUNTS
----------------------------------------------------------------------

Do not automatically trust numerical counts appearing in the original
title.

If the title says:

"7 Foods..."

but the transcript reliably identifies only five:

- do not invent two additional foods
- do not preserve an unsupported count
- describe what can actually be recovered

----------------------------------------------------------------------
NUMBER OF NAMES IN NEW TITLE
----------------------------------------------------------------------

Do not force every named item into the New Title.

Normally include no more than approximately 5–7 named items.

If there are 2–5 important named items and the title remains readable,
normally include them.

If many items are discussed, select the most important/distinctive
names and use a precise collective description for the rest.

Prefer:

ACTUAL NAMES + PRECISE SUBJECT + READABLE TITLE

----------------------------------------------------------------------
REGIONAL / COMMON / ENGLISH NAMES
----------------------------------------------------------------------

Preserve useful regional/common terminology.

Examples:

Kulthi Dal (Horse Gram)
Ragi (Finger Millet)
Rajgira (Amaranth)

Do not automatically replace an Indian/regional name with an English
name.

Both may be important for future search.

Do not put parentheses around every item if this makes the title
difficult to read.

----------------------------------------------------------------------
PRESERVE SPECIFICITY
----------------------------------------------------------------------

Preserve important specific terminology.

Examples:

SAP S/4HANA
GPT-5.6
Vitamin D3
iPhone 17 Pro
Python 3.14
SQL Server 2025

Do not unnecessarily simplify:

SAP S/4HANA
to:
SAP

or:

GPT-5.6
to:
GPT

The same applies to:

- medicine names
- products
- models
- versions
- software
- APIs
- technologies
- technical standards
- named procedures

----------------------------------------------------------------------
FILENAME SAFETY
----------------------------------------------------------------------

Because `new_title` may be used to rename files on Windows, it must be
filename-safe.

Do not include invalid Windows filename characters:

< > : " / \ | ? *

Avoid:

- unnecessary punctuation
- trailing periods
- trailing spaces
- excessive symbols
- unnecessary emojis
- excessively long titles

Do NOT put VIDEO_ID inside `new_title` unless explicitly required by
another application rule.

The application may append VIDEO_ID separately.

----------------------------------------------------------------------
INTERNAL SEARCH INTELLIGENCE
----------------------------------------------------------------------

Internally, the structured data may retain:

- title_basis
- title_entities
- canonical_tags
- concepts
- search_phrases
- synonyms_aliases
- questions_answered

These may be used for:

- search
- indexing
- retrieval
- related-video matching
- automated QA
- topic matching

HOWEVER:

DO NOT DISPLAY these as separate sections in the human-readable report:

- Title Basis
- Title Entities
- Concepts
- Useful Search Phrases
- Synonyms / Aliases
- Important Aliases
- Questions Answered

Do not print tables such as:

Canonical Name | Aliases

These are internal search/indexing fields.


======================================================================
2. CATEGORY
======================================================================

Create one compact classification block.

Show:

- Category
- Subcategory
- Primary Topic
- Content Type

Example:

Category: Health & Nutrition
Subcategory: Nutrition
Primary Topic: Calcium-Rich Foods
Content Type: Explanation / Health Discussion

Use a broad reusable Category.

Use a more specific Subcategory.

Primary Topic should identify the central subject of the video.

Content Type describes the type of content.

Examples include:

- Explanation
- Tutorial
- How-To
- Interview
- Podcast
- Lecture
- Review
- Recipe
- Remedy
- Medical Discussion
- Financial Discussion
- Product Demonstration
- Troubleshooting
- Case Study
- News
- Documentary
- Entertainment
- Q&A
- Other

Do NOT create a separate Content Type section.

Do NOT display:

- Secondary Topics
- Not About
- Concepts


======================================================================
3. TAGS
======================================================================

Create useful canonical tags.

Normally return approximately 4–12 meaningful tags.

Prefer specific, reusable tags.

Examples:

- Horse Gram
- Ragi
- Calcium
- Vitamin D3
- SQL Server
- SAP S/4HANA
- GPT-5.6

Avoid weak generic tags such as:

- Video
- YouTube
- Information
- General
- Miscellaneous
- Useful
- Knowledge

Preserve useful specificity.

Search-related concepts, synonyms and search phrases may remain
internally available to the application but should NOT be separately
printed in the human-readable report.


======================================================================
4. CHAPTERS
======================================================================

Create meaningful chapters from the timestamped transcript.

Chapters must follow REAL topic changes.

Do NOT divide the video into arbitrary fixed-duration intervals.

For each chapter internally return:

- chapter_no
- chapter_title
- start_timestamp
- end_timestamp
- start_seconds
- end_seconds

----------------------------------------------------------------------
CHAPTER RULES
----------------------------------------------------------------------

- Cover the meaningful spoken content.
- Keep chapters in chronological order.
- Use concise but descriptive chapter titles.
- Prefer actual subjects/items in chapter titles when useful.
- Create a new chapter when there is a meaningful topic change.
- Do not create chapters for brief passing mentions.
- Do not create too many tiny chapters.
- Do not combine clearly different major subjects into one chapter.
- Chapter boundaries must not overlap.
- Never invent timestamps.
- Use the most accurate timestamps available from the transcript.

For example:

| # | Chapter | Time |
|---:|---|---|
| 1 | Why Calcium Matters | 00:00–02:35 |
| 2 | Chuna and Sesame Seeds | 02:35–05:48 |
| 3 | Kulthi Dal (Horse Gram) | 05:48–08:21 |
| 4 | Ragi (Finger Millet) | 08:21–10:36 |
| 5 | Rajgira (Amaranth) | 10:36–12:44 |

The example above illustrates FORMAT ONLY.

Actual chapter names and timestamps must come from the supplied
transcript.

----------------------------------------------------------------------
CHAPTERS AND SUMMARY MUST MATCH
----------------------------------------------------------------------

The Detailed Timestamped Summary MUST use these SAME chapters.

Do NOT generate one chapter structure and then create unrelated
boundaries for the detailed summary.

Each chapter corresponds to one main section of the Detailed
Timestamped Summary.

This gives the application one canonical chapter structure for:

- report navigation
- video navigation
- transcript navigation
- search results
- chapter display
- future clip extraction


======================================================================
5. DETAILED TIMESTAMPED SUMMARY
======================================================================

THIS IS THE MAIN HUMAN-READABLE PART OF THE REPORT.

Use the SAME meaningful topic/chapter structure created above, but write
the summary as a coherent, human-readable explanation rather than as
chopped transcript extracts or mechanical bullet fragments.

Begin with a short overview paragraph explaining what the video covers
and, when appropriate, the overall method, framework, sequence or main
conclusion.

Then organize the detailed summary into numbered major topics:

### 1. <Meaningful Topic Name> (<start timestamp>–<end timestamp>)

Write one or more clear, information-dense paragraphs explaining what is
actually discussed in that topic.

### 2. <Meaningful Topic Name> (<start timestamp>–<end timestamp>)

Continue in the same style.

The summary should read like a well-written guide to the video's useful
content, not like a transcript dump.

----------------------------------------------------------------------
SUMMARY DEPTH
----------------------------------------------------------------------

The summary must be DETAILED and comprehensive enough that a user can
understand the useful content of the video without reading the complete
transcript.

Capture, where actually discussed:

- explanations
- important arguments
- reasoning
- causes
- examples
- actual named items
- practical information
- methods
- instructions
- quantities and ratios
- measurements
- dosages
- frequency and duration
- dates
- versions
- conclusions
- cautions and warnings stated in the video
- technical details
- important claims
- results and limitations
- useful alternatives
- supporting mechanisms or compounds
- lifestyle or usage recommendations

Keep information with the subject it belongs to.

There is NO separate Important Numbers section.

----------------------------------------------------------------------
IMPORTANT SUBJECT DEEP-DIVES
----------------------------------------------------------------------

When one subject inside a major topic receives substantial useful
discussion, preserve that depth instead of compressing it away.

For example, if a herb, medicine, technology, product, ingredient or
concept is discussed with multiple mechanisms, compounds, benefits,
studies, comparisons or instructions, a focused subsection may be used:

### Mulethi (Licorice): Why It Is Highlighted — 05:23–06:05

Then explain the important details clearly.

Use precise sub-ranges when they materially help navigation.

Do not create deep-dives for trivial mentions.

----------------------------------------------------------------------
ADDITIONAL USEFUL RECOMMENDATIONS
----------------------------------------------------------------------

Do not lose useful secondary information merely because it does not
deserve its own major chapter.

Keep relevant secondary recommendations under the appropriate topic or,
when clearer, use a compact subsection such as:

### Additional Recommendations — <range>

Examples may include:
- sun protection
- moisturizing
- frequency changes
- substitutions
- storage
- lifestyle adjustments
- practical alternatives
- supporting tips

Only include information actually supported by the transcript.

----------------------------------------------------------------------
WRITING STYLE
----------------------------------------------------------------------

Write polished explanatory prose.

Do not constantly write:
"The speaker says..."
"The transcript says..."
"The source states..."
"According to the speaker..."

Simply describe what is discussed.

Do NOT add editorial verification/disclaimer text such as:
- "Source framing:"
- "not independently verified"
- "should not be read as medical verification"
- "creator's recommendations rather than established facts"

Do not independently fact-check the video unless explicitly requested.

SOURCE-FIDELITY RULE:
The purpose of this pass is to model faithfully what the supplied video evidence
says, not to decide whether the speaker is objectively correct. Do not use outside
knowledge to correct, censor, suppress, strengthen, weaken, replace or silently
normalize the speaker's claims. Preserve uncertainty and attribution when needed so
a claim/recommendation/opinion/prediction is not accidentally presented as an
independently verified fact. Attribution must be natural and selective; do NOT
prefix every sentence with "the speaker says" or similar boilerplate.

Semantic validation asks (1) whether the supplied evidence says/supports the
reported content and (2) whether the output represents that evidence faithfully.
External factual truth is outside this workflow unless explicitly requested.

Do not add external warnings, corrections or medical commentary that are
not present in the allowed source material.

----------------------------------------------------------------------
TABLES
----------------------------------------------------------------------

Use tables only when they genuinely improve comprehension of structured
information. Do not force normal explanatory material into tables.

There is NO separate Structured Tables section.

----------------------------------------------------------------------
RECIPES IN SUMMARY
----------------------------------------------------------------------

A recipe/preparation may be described naturally and briefly in the
relevant summary topic, including its purpose and the most important
ratio/usage information when that is central to understanding the topic.

Do not unnecessarily duplicate every actionable detail.

The dedicated RECIPES / PREPARATIONS section below is the authoritative
compact extraction of the complete actionable preparation.

======================================================================
6. RECIPES / PREPARATIONS
======================================================================

Create this section only when the video contains a meaningful actionable
recipe, food/drink preparation, mixture, remedy preparation or similar
preparation.

Do NOT create it for simple food/ingredient mentions or vague statements
such as "cook it normally."

For EACH genuine preparation use this compact human-readable format:

### <number>. <Recipe / Preparation Name>

<One short sentence explaining what it is for or how it is used>
(<start timestamp>–<end timestamp>).

- **Ingredients:** <actual ingredients discussed>
- **Ratio / Quantity:** <only when stated>
- **Preparation:** <single action when preparation is simple>
- **Usage:** <how it is applied/consumed/used, when stated>
- **Frequency:** <when stated>
- **Duration:** <when stated>
- **Storage:** <when stated>
- **Important Tip:** <when stated>
- **Caution:** <only when actually stated in the video>

If Preparation contains MULTIPLE sequential actions, use nested bullets
under Preparation:

- **Preparation:**
  - <Step 1>
  - <Step 2>
  - <Step 3>

Do NOT use ingredient tables.
Do NOT use preparation-step tables.
Do NOT number individual preparation steps unless numbering is genuinely
needed for clarity.
Do NOT place timestamps on individual preparation steps.

Use ONE accurate overall timestamp range with the recipe/preparation
heading or introductory sentence.

The overall range should cover the actual preparation discussion as
precisely as possible.

----------------------------------------------------------------------
RECIPE RULES
----------------------------------------------------------------------

- Capture the complete useful actionable preparation from the transcript.
- Preserve exact ingredient names.
- Preserve exact quantities, ratios and units when stated.
- Preserve usage, frequency, duration, storage and cautions when stated.
- If preparation is one simple action, keep it on the Preparation bullet.
- If preparation has multiple steps, use nested sequential bullets under
  Preparation.
- Never invent ingredients.
- Never invent quantities.
- Never invent ratios.
- Never invent preparation steps.
- Never invent usage instructions.
- Never invent timestamps.
- Do not add fields that were not discussed.
- Do not repeatedly write "Not mentioned", "N/A" or similar filler.
- Keep regional/common and English names together when useful.
- If multiple genuine preparations exist, create a separate block for each.
- Do not combine unrelated preparations.
- Do not duplicate the same preparation merely because it is repeated in
  a recap.
- Do not reconstruct a known real-world recipe from outside knowledge.
- Do not turn advertisements, product demonstrations or promotional
  segments into recipes/preparations.
- Do not repeat the complete preparation unnecessarily in the Detailed
  Timestamped Summary.

If no meaningful preparation exists:
OMIT THIS SECTION COMPLETELY.

======================================================================
7. IMPORTANT CLAIMS / WARNINGS
======================================================================

Important claims and warnings should normally remain with the relevant
topic in the Detailed Timestamped Summary.

Do not create a huge claim-verification section.

Do NOT print repetitive labels such as:

Verification: SOURCE_CLAIM_ONLY

Do not turn every ordinary statement into a separate claim.

If a warning is important, keep it close to the relevant information.

Example:

### Supplement Discussion — 14:20–17:10

• ...

**Caution:** <actual caution discussed>

Do not invent warnings.

Do not independently fact-check the transcript as part of this
transcript-processing task.


======================================================================
8. MEANINGFUL REFERENCES MENTIONED
======================================================================

Create this section ONLY when meaningful identifiable references are
actually mentioned.

Useful references include identifiable:

- people
- experts
- authors
- books
- research papers
- studies
- government agencies
- professional organizations
- guidelines
- websites
- documentation
- datasets
- articles
- named external resources

Prefer references that would actually help the user identify or locate
the referenced person, publication, organization or resource.

Do NOT create vague references such as:

- some research
- a study
- experts
- doctors
- scientists
- a website
- the internet
- I read somewhere

unless the reference can be meaningfully identified.

Where available show:

| Reference | Type | Why Mentioned | Timestamp |
|---|---|---|---|
| ... | ... | ... | ... |

Include a URL only when it is explicitly available from the allowed
source material.

Do NOT invent:

- URLs
- author names
- study names
- book titles
- citations

If there are no meaningful identifiable references:

OMIT THIS SECTION COMPLETELY.

Do NOT print:

References Mentioned
None

or:

References: []


======================================================================
9. QUESTIONS AND ANSWERS
======================================================================

Create this section only when useful questions are clearly answered in
the transcript and presenting them separately adds value.

Use:

| Question | Answer | Timestamp |
|---|---|---|

Do not manufacture trivial questions simply to populate the section.

Do not repeat large portions of the Detailed Timestamped Summary.

If there are no worthwhile Q&A items:

OMIT THIS SECTION COMPLETELY.


======================================================================
10. PLAYLIST / SERIES RELATIONSHIP
======================================================================

Detect a playlist/series relationship only when clearly supported.

Examples:

- Part 1 / Part 2
- Lesson 4
- Module 3
- Episode 8
- course sequence
- multipart tutorial
- named video series

Where known, internally preserve:

- series_name
- part_or_episode_number
- total_parts_if_known
- previous_part
- next_part
- intended_order

In the human-readable report, show this information ONLY when a
meaningful relationship actually exists.

If unknown, empty or not applicable:

OMIT THIS SECTION COMPLETELY.

Never print an empty:

Playlist / Series Relationship

heading.


======================================================================
11. IT / TECHNICAL VIDEO INTELLIGENCE
======================================================================

THIS SECTION IS SPECIFICALLY FOR IT / SOFTWARE / TECHNICAL VIDEOS.

Do not create this section for ordinary health, food, recipe,
entertainment or general videos merely because a product or device is
mentioned.

For technical videos capture applicable exact technical information:

- products
- services
- software
- tools
- technologies
- versions
- commands
- command-line examples
- code
- SQL
- scripts
- configuration settings
- configuration values
- file/folder paths
- environment variables
- APIs
- API endpoints
- parameters
- URLs/resources
- errors
- prerequisites
- installation information
- troubleshooting steps
- expected output

Preserve technical specificity.

Examples:

SAP S/4HANA
GPT-5.6
SQL Server 2025
Python 3.14
Windows 11

Do not reduce a specific technology/version/model to an unnecessarily
generic term.

Where useful, use:

| Type | Exact Value / Command | Purpose | Timestamp |
|---|---|---|---|
| Command | ... | ... | 04:32 |
| API | ... | ... | 07:18 |
| Error | ... | ... | 09:44 |
| Config | ... | ... | 12:07 |

If a complete technical procedure is already explained in the Detailed
Timestamped Summary, do not repeat the entire explanation here.

Use this section for useful structured technical details.

Never guess uncertain:

- code
- commands
- SQL
- configuration values
- URLs
- API endpoints
- versions

If the video is not technical:

OMIT THIS SECTION COMPLETELY.


======================================================================
12. NAMED ITEMS DISCUSSED
======================================================================

KEEP THIS AS THE LAST CONTENT SECTION OF THE HUMAN-READABLE REPORT.

Extract important actual identifiable items discussed in the video.

Possible types include:

- foods
- ingredients
- herbs
- medicines
- supplements
- products
- tools
- technologies
- software
- exercises
- techniques
- treatments
- books
- websites
- people
- companies
- organizations
- locations
- diseases/conditions
- services
- other important named subjects

----------------------------------------------------------------------
ACTUAL NAMES ARE REQUIRED
----------------------------------------------------------------------

If the transcript says:

"Here are 7 foods..."

do NOT return:

"7 foods"

Extract the actual identifiable names.

Example:

- Amla
- Walnuts
- Sesame Seeds
- Spinach
- Eggs
- Lentils
- Moringa

The same rule applies to:

- products
- tools
- medicines
- exercises
- technologies
- software
- treatments
- ingredients
- books
- people
- organizations
- other named items

If seven items are promised but only five are reliably identifiable:

return the five.

Do NOT invent the missing two.

----------------------------------------------------------------------
DISPLAY
----------------------------------------------------------------------

Keep this section concise because the Detailed Timestamped Summary
already explains the items.

Prefer a table:

| Named Item | Type | Timestamp |
|---|---|---|
| Ragi (Finger Millet) | Food | 05:42 |
| Kulthi Dal (Horse Gram) | Food | 07:15 |
| Rajgira (Amaranth) | Food | 09:03 |

Where regional/common and English names are useful, show them naturally
together.

Do NOT create another aliases table after this section.

This must remain the LAST content section.


======================================================================
STRICT ANTI-DUPLICATION RULE
======================================================================

Do not repeat information simply to populate multiple sections.

The Detailed Timestamped Summary is the primary explanation.

Other sections should add structured or retrieval value.

For example:

If Ragi is discussed with:

- purpose
- benefits
- quantity
- preparation
- recipe
- caution

the Detailed Summary should explain the overall discussion.

The Recipes section should contain the actionable recipe details.

Named Items should simply identify:

Ragi (Finger Millet) | Food | Timestamp

Do not repeat the complete explanation three times.

Similarly, for technical videos:

Detailed Summary:
explains what is being done and why.

Technical Intelligence:
captures exact commands/configuration/errors/API details.

Named Items:
identifies the important technologies/products.

Each section should have a distinct purpose.


======================================================================
EMPTY SECTION RULE
======================================================================

THIS RULE IS VERY IMPORTANT.

Do NOT display an optional section when there is no useful information.

Do NOT output:

References Mentioned
None

Do NOT output:

Recipes
None

Do NOT output:

Questions and Answers
[]

Do NOT output:

Playlist / Series Relationship
Not available

Do NOT output:

IT / Technical Intelligence
Not applicable

Simply omit the entire heading and section.


======================================================================
HUMAN-READABLE REPORT ORDER
======================================================================

The visible report should normally appear in this order:

1. TITLE & SEARCH INTELLIGENCE

   Original Title
   New Title

2. CATEGORY

   Category
   Subcategory
   Primary Topic
   Content Type

3. TAGS

4. CHAPTERS

5. DETAILED TIMESTAMPED SUMMARY

6. RECIPES / PREPARATIONS
   ONLY when present

7. MEANINGFUL REFERENCES MENTIONED
   ONLY when present

8. QUESTIONS AND ANSWERS
   ONLY when useful

9. PLAYLIST / SERIES
   ONLY when applicable

10. IT / TECHNICAL VIDEO INTELLIGENCE
    ONLY for technical videos

11. NAMED ITEMS DISCUSSED
    ALWAYS KEEP THIS AS THE LAST CONTENT SECTION


======================================================================
DO NOT DISPLAY IN HUMAN-READABLE REPORT
======================================================================

Do NOT display:

- Source
- Duration represented
- Transcript type
- Description used for analysis
- Viewer comments used
- source_language
- title_translated
- title_confidence
- Title Basis
- Title Entities
- Important Aliases
- separate Synonyms / Aliases section
- Concepts
- Useful Search Phrases
- Questions Answered as search metadata
- Secondary Topics
- Not About
- separate Content Type section
- Entity Extraction
- separate Instructions / How-To / Remedies section
- separate Comparisons section
- separate Recommendations section
- Verification: SOURCE_CLAIM_ONLY
- separate Structured Tables section
- Time-Sensitive Information
- Glossary
- Things Discussed in This Video
- Evidence / Provenance
- Analysis Quality
- ChatGPT Perspective
- PS


======================================================================
INTERNAL DATA VS HUMAN-READABLE REPORT
======================================================================

Some information is valuable to the application but should not clutter
the visible report.

Internal machine-readable data MAY retain fields such as:

- VIDEO_ID
- original_title
- new_title
- title_basis
- title_entities
- canonical_tags
- concepts
- search_phrases
- synonyms_aliases
- questions_answered
- category
- subcategory
- primary_topic
- content_type
- chapters
- detailed_timestamped_summary
- recipes
- references
- questions_and_answers
- playlist_series_relationship
- technical_intelligence
- named_items_discussed
- processing_status
- processing_warnings
- reprocess_recommended
- reprocess_reasons
- uncertain_items
- targeted_review_hints

Do NOT assume that every machine-readable field must be printed in the
human-readable report.

The visible report must follow the display rules above.


======================================================================
FINAL CRITICAL RULES
======================================================================

1. Preserve exact VIDEO_ID.

2. Process each VIDEO_ID independently.

3. Never mix information from different videos.

4. Preserve original_title EXACTLY as authoritative metadata supplies
   it.

5. Generate ONE definitive `new_title`.

6. `new_title` is intended for eventual file/folder renaming.

7. Make `new_title` Windows-filename-safe.

8. Generate `new_title` based primarily on actual transcript content.

9. Do not automatically trust numerical counts in the original title.

10. Never invent missing named items to satisfy a count.

11. Normally use no more than approximately 5–7 named items in
    `new_title`.

12. Preserve useful regional/common and English names.

13. Preserve important technical/product/medical specificity.

14. Do not use the video description for analysis.

15. Do not use viewer comments for analysis.

16. Create chapters based on REAL topic changes.

17. Never create arbitrary fixed-duration chapters.

18. Chapters and Detailed Timestamped Summary MUST use the same
    boundaries.

19. Never invent chapter timestamps.

20. Make the Detailed Timestamped Summary detailed, coherent and
    topic-centered.

21. Write polished explanatory paragraphs organized by meaningful
    numbered topics with timestamp ranges. Use focused deep-dives and
    additional-recommendation subsections when they preserve important
    useful information.

22. Avoid repeatedly saying "the speaker says", "the transcript says"
    or similar wording.

23. Use tables wherever they genuinely improve readability.

24. Keep relevant numbers with the subject they belong to.

25. Create a separate Recipes / Preparations section when meaningful
    preparation information exists.

26. For recipes/preparations, capture ONE accurate overall timestamp
    range where the preparation is discussed.

27. Do NOT include timestamps on individual preparation steps. Use a
    compact labeled-bullet format. When multiple preparation steps exist,
    put them as nested bullets under Preparation.

28. Never invent recipe ingredients, quantities, ratios, instructions,
    usage details or timestamps.

29. Do not repeat the complete recipe in the Detailed Summary.

30. Include only meaningful identifiable references.

31. Never fabricate references, books, studies, authors or URLs.

32. Omit optional sections completely when empty.

33. IT / Technical Video Intelligence applies specifically to
    IT/software/technical content.

34. Never guess uncertain code, commands, API endpoints, configuration
    values or technical versions.

35. Keep Named Items Discussed as the LAST content section.

36. Extract actual identifiable names rather than vague numbered
    descriptions.

37. Do not duplicate the same information throughout the report.

38. Do not display internal Title Basis, Title Entities, Concepts,
    Search Phrases or Alias tables in the human-readable report.

39. Do not include ChatGPT Perspective / PS.

40. Do not manufacture information merely to populate a field or
    section.

41. If something cannot be reliably determined from the allowed source
    material, leave it empty or omit it rather than guessing.

42. Use the most precise timestamps supported by the supplied
    timestamped transcript.

43. Completely exclude promotional/sponsor/advertising information from
    the report and from all search/indexing fields.

44. Do not add Source Framing, independent-verification disclaimers or
    external fact-check commentary unless explicitly requested.

45. Recipes / Preparations must use concise labeled bullets rather than
    ingredient or step tables.

46. If Preparation has multiple actions, use nested sequential bullets
    under Preparation; if simple, keep it as one Preparation bullet.

47. Perform the five processing phases sequentially inside ONE main
    model call; do not require five separate transcript-processing calls.

48. Phase 5 is an internal semantic self-review, not a visible report
    section.

49. Never fail or abort an entire package because one video is weak,
    uncertain or source-insufficient.

50. Assign an internal processing status to every VIDEO_ID and continue
    processing subsequent videos regardless of that status.

51. Flag videos that need a better source/package with
    `reprocess_recommended = true` and concise actionable reasons.

52. Do not endlessly retry a weak video inside the main pass. Preserve
    the status and let the application recreate a package for it later.

53. Keep processing-quality fields internal; do not add them as visible
    report sections.


======================================================================
FINAL OUTPUT
======================================================================

Produce one structured intelligence record for EACH VIDEO_ID.

The machine-readable output should support the application fields
described above.

The human-readable report generated from that data must follow the
specified report order and visibility rules.

The Detailed Timestamped Summary is the primary explanatory content.

Chapters provide the canonical navigation structure.

Recipes / Preparations preserve actionable preparation details.

Named Items Discussed provides the final concise index of important
identifiable subjects.

Return valid machine-readable JSON according to the supplied output
schema.

Do not wrap JSON in Markdown code fences when producing the actual
processing result.

Do not add introductory or concluding prose outside the requested
output.

54. Process all VIDEO_IDs in a package strictly sequentially in package
    order; fully finish and persist one video before starting the next.

55. Never combine multiple video transcripts into one semantic call.

56. After Pass 1, code must split the structured result into modular
    per-section files so one section can be replaced independently.

57. Assemble final JSON and HTML from the modular section files; HTML is
    never the authoritative intelligence source.

58. Manual or deterministic changes to a section must not trigger an
    LLM call; simply validate dependencies, reassemble and rerender.

59. If only one section requires semantic regeneration, regenerate only
    that section with the minimum necessary transcript evidence and
    dependencies, then replace that section and revalidate affected
    dependencies.


60. Minimize the number of packages globally; use 25 only as an advisory target and never exceed 30 videos per package.

61. Package size must never determine model context size; Pass 1 receives
    only the current video's source evidence and instructions.

62. Persist and checkpoint after every VIDEO_ID before starting the next.

63. Resume interrupted packages from the first unfinished video and do
    not reprocess already completed reusable videos.

64. Use prompt/version and source fingerprints to prevent unnecessary
    token-consuming reprocessing after resume.


======================================================================
V3 HUMAN-READABLE REPORT + SEMANTIC QUALITY STANDARD
======================================================================

This V3 standard incorporates the validated improvements from the
17-video reference run and the subsequent V1/V2/V3 HTML reviews.

These rules do NOT change the core architecture:
- one semantic read per video
- current-video-only context
- deterministic section persistence/rendering
- optional targeted repair only when needed
- no forced optional sections
- no external fact-checking unless explicitly requested

----------------------------------------------------------------------
1. REQUIRED VISIBLE REPORT IDENTITY / NAVIGATION
----------------------------------------------------------------------

DO NOT REMOVE these visible report elements:

- Video Intelligence Report
- Original Title
- New Title
- Category
- Tags
- Chapters

They remain part of the human-readable HTML report.

----------------------------------------------------------------------
2. CHAPTERS — V3 NON-TABLE LAYOUT
----------------------------------------------------------------------

Do NOT render Chapters as a table.

Render Chapters as a vertical list of compact chapter cards.

Each chapter card must contain:
- numbered circle
- chapter title
- timestamp/range pill aligned to the right

Recommended visual hierarchy:

[1]  Chapter Title                              [00:26–01:30]

Rules:
- one card per canonical chapter
- preserve chronological order
- use the same chapter title and timestamp data as the authoritative
  chapter JSON
- no duplicated semantic summary inside the chapter card by default
- if a short subtitle is ever rendered, it must come from already
  extracted chapter metadata and must not trigger another model call
- responsive layout: timestamp may wrap below the title on narrow screens

The chapter layout should visually match the card language used by the
Detailed Timestamped Summary and Recipes / Preparations.

----------------------------------------------------------------------
3. DETAILED TIMESTAMPED SUMMARY — V3 CARD LAYOUT
----------------------------------------------------------------------

The Detailed Timestamped Summary remains the main human-readable section.

Do not render it as a wall of paragraphs.

Render each major topic as a rounded card with:

- numbered circle
- topic title
- timestamp/range pill
- concise lead explanation
- optional light-gray structured detail box

Example structure:

[3] Shilajit for Sexual Vitality                 [04:07–04:56]

Short explanation of what is discussed.

METHOD / PRACTICAL GUIDANCE
• Study mentioned: 500 mg for 90 days
• Suggested use in video: small quantity with warm milk at night
• Duration discussed: 2 months
• Source caution: avoid during summer

The information type determines the detail-box label and layout.

Supported adaptive patterns include:
- EXPLANATION
- KEY POINTS
- METHOD / PRACTICAL GUIDANCE
- MYTH / CORRECTION
- COMPARISON
- TAKEAWAY
- IMPORTANT DETAILS
- PARTIALLY UNCERTAIN SOURCE

Do NOT force the same label onto every topic.

For myth/correction content, prefer:
- Myth
- Video's explanation/correction
- Takeaway

For methods/practical guidance, prefer:
- quantities
- steps
- timing
- frequency
- duration
- source-stated cautions

For explanatory content:
- concise explanation first
- then only the most useful supporting points

The layout must improve scanning without reducing semantic completeness.

----------------------------------------------------------------------
4. ADAPTIVE SUMMARY COMPLETENESS
----------------------------------------------------------------------

Summary length is determined by information density, not video duration.

For every canonical chapter, preserve each DISTINCT useful information
unit that materially helps understanding, retrieval, navigation or
practical use.

Examples:
- explanation/reason
- meaningful claim/conclusion
- important named item
- quantity/ratio/dosage
- frequency/duration
- method/preparation
- source-stated caution/limitation
- comparison/alternative
- identified study/reference
- important example
- practical recommendation

Do not replace multiple distinct useful details with vague statements
such as "the video discusses diet and lifestyle."

Do not inflate simple material. Repetition, filler, recaps and
promotional content do not count as useful information units.

----------------------------------------------------------------------
5. INTERNAL COVERAGE LEDGER DURING SELF-REVIEW
----------------------------------------------------------------------

During INTERNAL Phase 5 self-review, mentally classify every major useful
information unit as:

- REPRESENTED
- INTENTIONALLY OMITTED AS DUPLICATE/FILLER
- PROMOTIONAL
- UNCERTAIN / NOT RELIABLY RECOVERABLE

Do NOT output this ledger.

Before returning, repair any reliably recoverable, useful,
non-promotional information unit that is missing from the appropriate
section.

This is a coverage check inside the same semantic pass, not a second full
transcript pass.

----------------------------------------------------------------------
6. LOCALIZED ASR UNCERTAINTY
----------------------------------------------------------------------

Attach uncertainty to the smallest affected element possible.

If one proper noun, number, ingredient, medicine, technical term or
sentence is damaged:
- preserve the reliable surrounding information normally
- leave only the damaged element uncertain or omitted
- do not make the entire chapter vague

Never silently reconstruct damaged names or values from outside
knowledge.

Escalate video status only when corruption materially prevents reliable
recovery of important content.

----------------------------------------------------------------------
7. CHAPTER NAVIGATION-VALUE TEST
----------------------------------------------------------------------

Create a new chapter only when BOTH are true:
1. a meaningful subject/method/stage change occurs
2. a viewer could reasonably want to jump directly to it

Do not split merely for a brief example, ingredient or tip.

Do split for:
- new preparation
- major independent item
- major myth/question
- procedure stage
- comparison target
- clearly independent subject

After drafting, check whether adjacent chapters should be merged or an
overloaded chapter should be split.

----------------------------------------------------------------------
8. TITLE COMPRESSION CHECK
----------------------------------------------------------------------

After generating the accurate New Title, perform one compression check.

Prefer the shortest title that preserves distinguishing search value.

If a title becomes a crowded enumeration:
- keep the 2–5 most distinguishing named items, OR
- use an accurate umbrella phrase for the remaining items

Accuracy always outranks brevity.

----------------------------------------------------------------------
9. RECIPES / PREPARATIONS — V3 CARD LAYOUT
----------------------------------------------------------------------

Keep the visible section name:

Recipes / Preparations

Do not render recipes/preparations as tables.

Use the SAME visual card language as Detailed Timestamped Summary:
- numbered circle
- preparation name
- timestamp/range pill
- rounded card
- light-gray structured detail box
- clean spacing and typography

The card adapts to the amount/type of supported information.

A. FULL RECIPE / PREPARATION CARD
Use when ingredients, quantities and multiple steps are available.

Possible blocks:
- YOU NEED / INGREDIENTS
- MAKE / PREPARATION
- USE / TIMING
- FREQUENCY
- DURATION
- STORAGE
- IMPORTANT TIP
- CAUTION

B. COMPACT PREPARATION CARD
Use for simple preparations with a few ingredients/steps.

C. SIMPLE USE CARD
Use for one-step applications or usage instructions such as oils,
Nasya, tablets/capsules, simple drinks, or similar source-supported use.

D. UNCERTAIN-SOURCE CARD
Use when the preparation is meaningful but a specific ingredient,
medicine/formulation name or value is damaged by ASR.

Preserve reliable details and explicitly avoid guessing the damaged
element.

Important:
- show only fields supported by the source
- NEVER show N/A placeholders
- never create empty blocks
- multi-step preparation should use ordered steps
- ingredients/details should use readable bullets
- visually emphasize important quantities, times and durations in HTML
  without changing their values
- do not duplicate the same preparation because it appears again in a
  recap
- omit the entire Recipes / Preparations section when no meaningful
  actionable preparation/use information exists

----------------------------------------------------------------------
10. RECIPE FIELD COMPLETENESS AUDIT
----------------------------------------------------------------------

For every genuine preparation, Phase 5 must check whether the source
states any of:

- Ingredients
- Ratio / Quantity
- Preparation
- Usage
- Frequency
- Duration
- Storage
- Important Tip
- Caution

Include only stated fields, but do not miss a stated field.

----------------------------------------------------------------------
11. Q&A RETRIEVAL-VALUE TEST
----------------------------------------------------------------------

Generate Q&A when the transcript clearly answers a question a user could
plausibly search or ask independently.

High-value triggers:
- explicit question -> answer
- myth -> correction
- can / should / how often / how much / when / why / which
- clear comparison decision
- troubleshooting
- eligibility/suitability question

Do not mechanically convert every chapter heading into Q&A.

Prefer a small set of high-value questions over a generic FAQ.

----------------------------------------------------------------------
12. NAMED ITEMS PRECISION
----------------------------------------------------------------------

Named Items Discussed is primarily an entity/item index, not a concept
index.

Prefer concrete identifiable:
- foods/ingredients
- herbs/medicines/supplements
- products/tools
- exercises/techniques/treatments
- books/studies/resources
- people/companies/organizations
- software/technologies/services
- identifiable locations

Broad abstract concepts normally belong in Category, Tags, Chapters or
Detailed Summary instead.

----------------------------------------------------------------------
13. TIMESTAMP PRESENTATION — REFERENCES + NAMED ITEMS
----------------------------------------------------------------------

Meaningful References Mentioned:
- KEEP the section when applicable
- DO NOT create a separate Timestamp column in the visible HTML
- append the timestamp after the completed reference name

Example:
Charaka Samhita (06:30)

Named Items Discussed:
- KEEP the section
- it remains the LAST visible content section
- DO NOT create a separate Timestamp column in the visible HTML
- append the timestamp after the completed item name

Example:
Shatavari (06:30)

The authoritative structured JSON may still keep timestamp as a separate
machine-readable field. This rule concerns visible HTML rendering only.

----------------------------------------------------------------------
14. FINAL CROSS-SECTION CONSISTENCY
----------------------------------------------------------------------

Before returning:
- every chapter must correspond to a Detailed Summary topic
- recipe timestamps must fit the relevant source/chapter
- central recipe ingredients/items must not disappear from the
  explanatory summary when important
- Q&A answers must agree with the Detailed Summary
- Named Items must remain the LAST visible content section
- optional empty sections must be omitted
- internal quality/status fields must not leak into the visible report
- Video Intelligence Report, Original Title, New Title, Category, Tags
  and Chapters must remain visible
- Chapters must use cards, not a table
- Recipes / Preparations must use the same card design language as the
  Detailed Timestamped Summary


======================================================================
V3.1 LANGUAGE NORMALIZATION + VIDEO URL REQUIREMENTS
======================================================================

These rules are mandatory for every future package and supersede any
earlier wording that could allow transcript-language text to leak into
the generated intelligence report.

----------------------------------------------------------------------
15. OUTPUT LANGUAGE — ENGLISH SEMANTIC INTELLIGENCE
----------------------------------------------------------------------

The transcript/SRT may be English, Hindi, Hinglish, or another supported
language. The source language MUST NOT determine the visible semantic
report language.

MANDATORY RULE:

- `Original Title` stays EXACTLY as supplied by the source/metadata.
  Do not translate, normalize, correct, romanize, shorten, or rewrite it.
- ALL OTHER generated semantic/report content MUST be written in clear,
  natural English.

This applies to:
- New Title
- Category
- Subcategory
- Primary Topic
- Content Type
- Tags
- Chapters
- Detailed Timestamped Summary
- Recipes / Preparations
- Meaningful References Mentioned
- Q&A
- Playlist / Series Relationship
- Technical Intelligence
- Named Items Discussed
- any generated explanation, label, takeaway, method, caution, comparison,
  uncertainty note, or other human-readable semantic text

For Hindi/Hinglish or other non-English transcripts:
1. Understand the source in its original language.
2. Preserve its meaning, quantities, claims, uncertainty and timestamps.
3. Generate the semantic intelligence directly in English.
4. Do NOT paste or lightly clean the original-language transcript into
   English report fields.
5. Do NOT use transliteration as a substitute for English translation,
   except for proper nouns, classical terms, product names, medicine names,
   book names, technical identifiers, or other names that should remain
   identifiable.
6. When a source-specific Hindi/Ayurvedic/technical term materially helps
   retrieval, preserve the identifiable term and explain it in English
   when useful.
7. Never invent an English meaning for an uncertain ASR term. Keep the
   smallest affected term uncertain according to the localized-ASR rule.

Phase 5 MUST perform an OUTPUT-LANGUAGE CHECK:
- inspect every generated visible semantic section
- if ordinary Hindi/Hinglish/non-English prose remains outside
  `Original Title` or a legitimate proper/source term, translate/rewrite
  that prose into English before returning
- this check occurs inside the same semantic pass and does not require
  another full transcript read

A report fails V3 semantic validation if transcript-language prose is
copied into the Detailed Summary, Chapters, Recipes, Q&A, or other
generated report sections instead of being expressed in English.

----------------------------------------------------------------------
16. VIDEO URL — REQUIRED VISIBLE FIELD
----------------------------------------------------------------------

The visible report header MUST contain:

1. Original Title
2. New Title
3. Video URL

`Video URL` must appear IMMEDIATELY AFTER `New Title` and before Category.

Rules:
- use the authoritative video URL supplied in package metadata when present
- if package metadata provides the canonical VIDEO_ID but no URL, code may
  deterministically construct the standard YouTube watch URL from VIDEO_ID
- never ask the semantic model to invent or reconstruct a URL
- HTML must render the URL as a clickable link
- structured JSON should retain `video_url` as a machine-readable source
  identity field
- URL rendering is deterministic and consumes zero LLM tokens

Required visible order:

Video Intelligence Report

Original Title: <exact source title>
New Title: <English semantic title>
Video URL: <clickable canonical video URL>

Category
Tags
Chapters
...

----------------------------------------------------------------------
17. PROMOTION EXCLUSION CHECK AFTER LANGUAGE NORMALIZATION
----------------------------------------------------------------------

Translation/language normalization must NEVER cause promotional material
to re-enter the report.

Before final output, verify that sponsors, affiliate pitches, coupon
codes, unrelated product promotions, course sales, promotional URLs,
calls to purchase, and promotional outros are excluded from:
- New Title
- Category / Tags
- Chapters
- Detailed Summary
- Recipes / Preparations
- References
- Q&A
- Named Items
- search/retrieval intelligence

If promotional material interrupts useful source content, skip the
promotional range and continue with the next useful semantic unit.

Do not display a visible note saying that promotion was excluded.


======================================================================
V3.3 VISIBLE SOURCE IDENTITY — CHANNEL NAME + DURATION
======================================================================

The visible report header MUST use this order:

1. Original Title
2. New Title
3. Video URL
4. Channel Name
5. Duration
6. Category

CHANNEL NAME
- Display the authoritative channel/creator name supplied by package/video
  metadata.
- Do not infer, rewrite, translate, normalize, or invent the channel name.
- The semantic model must not generate the channel name.
- Structured output should retain `channel_name` as source identity metadata.
- If authoritative channel metadata is genuinely absent, omit the visible
  field rather than guessing.

DURATION
- Display the authoritative video duration supplied by package/video
  metadata or deterministically derived from authoritative source timing.
- The semantic model must not estimate or invent duration.
- Prefer a human-readable form such as `12:34` or `1:02:15`.
- Structured output should retain an authoritative machine-readable duration
  value where available.
- Do not confuse transcript coverage with video duration.
- If authoritative duration cannot be established, omit the visible field
  rather than guessing.

Required visible header example:

Video Intelligence Report

Original Title: <exact source title>
New Title: <English semantic title>
Video URL: <clickable canonical video URL>
Channel Name: <exact authoritative channel name>
Duration: <authoritative human-readable duration>

Category
Tags
Chapters
...

These are SOURCE IDENTITY / PRESENTATION fields. They consume zero semantic
LLM tokens when already available in authoritative metadata and must not
influence transcript interpretation.


======================================================================
V3.3 CHATGPT PACKAGE EXECUTION MODE
======================================================================

This mode exists only to let an interactive ChatGPT session process a
multi-video package without weakening the semantic specification.

QUALITY REQUIREMENT
- This mode MUST NOT reduce semantic quality.
- Every VIDEO_ID remains an independent semantic unit.
- Each video's complete allowed evidence must be understood before its
  semantic result is accepted.
- All normal V3.3 semantic rules, five internal phases, English-output
  rules, promotion exclusion, ASR handling, coverage/self-review and
  validation requirements remain mandatory.
- Mechanical/extractive heuristics are never an acceptable substitute for
  semantic processing.

SEMANTIC ISOLATION
- Process videos in package order.
- While interpreting the CURRENT video, facts/content from another VIDEO_ID
  are not evidence and must not influence the current result.
- Do not merge transcripts or create package-level semantic summaries as a
  substitute for per-video understanding.
- Finish the current video's semantic intelligence and semantic validation
  before moving to the next video's semantic interpretation.

DEFERRED DETERMINISTIC PERSISTENCE
In an interactive ChatGPT package run, deterministic persistence may be
deferred until multiple independently completed semantic results are ready.

Allowed flow:

Video 1 -> complete semantic result + validation
Video 2 -> complete semantic result + validation
...
Video N -> complete semantic result + validation
THEN deterministic code may persist/split/render the completed results.

Deferred persistence MUST NOT:
- cause cross-video semantic contamination
- cause a completed semantic result to be replaced by heuristic extraction
- skip per-video validation
- change the authoritative semantic content
- prevent a weak video from receiving its proper warning/reprocess status

When persistence is deferred, maintain a per-video completion record in
memory so only semantically completed videos are rendered.

PRODUCTION RUNTIME
The preferred production VideoHoarder runtime remains:
process -> validate -> persist -> assemble -> render -> checkpoint -> next
video.

This ChatGPT execution mode is an operational accommodation for interactive
package testing, not a weaker intelligence mode.


======================================================================
V3.3 SEMANTIC-AUTHORING / DETERMINISTIC-CODE BOUNDARY
======================================================================

This boundary is mandatory for every normal V3.3 run and for ChatGPT
Package Execution Mode.

SOURCE OF SEMANTIC INTELLIGENCE
- The semantic processor/model is responsible for deciding what the video
  means.
- For the CURRENT VIDEO, it must work from the complete allowed transcript/
  SRT evidence plus permitted source-identity metadata.
- The package's embedded/legacy prompt MUST NOT override the currently
  selected authoritative Master Prompt and Architecture when the run
  explicitly specifies an external authoritative version.
- Description, comments, sponsor copy and other disallowed metadata MUST NOT
  be used as semantic evidence.

THE SEMANTIC PROCESSOR/MODEL MUST AUTHOR OR DECIDE:
- New Title
- Category / Subcategory / Primary Topic / Content Type
- Tags
- genuine semantic chapter boundaries and chapter titles
- Detailed Timestamped Summary
- Recipes / Preparations when genuinely supported
- Meaningful References
- retrieval-useful Q&A
- Playlist / Series relationship when supported
- Technical Intelligence when applicable
- Named Items Discussed
- ASR uncertainty interpretation
- semantic validation/status and reprocess recommendation

DETERMINISTIC CODE MAY:
- parse package structure and permitted metadata
- select the CURRENT VIDEO's evidence
- preserve exact source identity fields
- format/normalize authoritative duration values
- persist completed semantic result objects
- split completed results into modular section JSON files
- assemble authoritative JSON from section files
- render HTML
- build package indexes/status/reprocess lists
- run deterministic schema/order/presence/language-character/timestamp/
  filename/link/duplication consistency checks
- create checkpoints, backups and ZIP archives

DETERMINISTIC CODE MUST NOT SUBSTITUTE FOR SEMANTIC AUTHORING.
In particular it MUST NOT:
- create chapters from equal-duration/equal-size chunks
- use arbitrary fixed transcript windows as semantic topic boundaries
- use first/last sentences of chunks as a semantic summary
- copy transcript passages as the Detailed Summary instead of semantically
  synthesizing them
- generate Tags primarily from word frequency
- derive Named Items merely from title words, tags or frequency
- use generic "Topic 1", "Topic 2" labels when meaningful semantic titles
  can be recovered
- mechanically translate transcript prose and call it semantic intelligence
- reconstruct uncertain ASR terms by guessing
- infer semantic content from description/comments/promotional metadata
- mark a video V3.3-complete merely because JSON/HTML files were rendered

MANDATORY PER-VIDEO ACCEPTANCE GATE
A video is not semantically complete until its semantic result has passed
V3.3 self-review. Review must include, as applicable:
1. whole-video coverage / internal coverage ledger
2. chapter navigation-value and chronological-boundary review
3. title accuracy, compression and search value
4. Detailed Summary completeness and synthesis quality
5. Recipe / Preparation grounding and field-completeness review
6. References grounding
7. Q&A retrieval-value review
8. Named Items precision review
9. numeric, quantity, unit and timestamp integrity
10. English-generated-output check
11. promotion exclusion check
12. localized ASR uncertainty check
13. cross-section consistency and duplication review

SOURCE-QUALITY HANDLING
- Never invent missing meaning to force PASS.
- Use PASS, PASS_WITH_WARNINGS, REPROCESS_RECOMMENDED or
  SOURCE_INSUFFICIENT as warranted.
- A weak video does not block later videos in the package.
- Reprocess/repackage candidates must be collected in the package-level
  reprocess list.

PACKAGE COMPLETION RULE
The existence of N rendered HTML files is NOT proof that N videos were
semantically processed. A package may be called V3.3 processed only when
every claimed-complete VIDEO_ID has a completed semantic result and its
per-video V3.3 validation/status recorded before or alongside deterministic
rendering.

======================================================================
V3.3.1 HARDENING — INFORMATION PRESERVATION, CLAIM SAFETY AND QUALITY
======================================================================

These V3.3.1 rules harden V3.3. They do NOT replace the existing semantic
architecture, current-video isolation, five internal phases, modular
persistence, promotion exclusion, language normalization, or non-blocking
package processing.

1. INFORMATION-PRESERVATION PRIORITY
------------------------------------
Semantic compression MUST NOT become information loss.

When reliable source evidence exists, preserve useful micro-facts including:
- quantities and units
- exact identifiable ingredients/items/entities
- actions
- order/sequence
- timing
- frequency
- duration
- conditions and exceptions
- source-stated cautions
- alternatives/substitutions
- outcomes, results and claims
- technical identifiers, commands, versions and configuration values

Prefer concise synthesis, but do not collapse an actionable instruction into
a vague statement when the source supplies reliable actionable detail.

2. NUMBER <-> ENTITY INTEGRITY
------------------------------
Every important number MUST remain attached to the thing/action it describes.

BAD:
- "Take 1 teaspoon twice daily."

GOOD:
- "Take 1 teaspoon of the ashwagandha-shatavari-mishri mixture twice daily."

Do not preserve an orphan dosage, quantity, price, time, frequency, duration,
percentage, version or measurement.

If ASR makes either the number OR its associated entity/action uncertain:
- do not silently repair it;
- do not infer the missing association from general knowledge;
- localize uncertainty to the smallest affected fact; or
- omit the unreliable micro-fact while preserving surrounding reliable
  intelligence.

3. STRICT RECIPE / PREPARATION QUALIFICATION GATE
--------------------------------------------------
Create a Recipes / Preparations entry only when the source contains a genuine
preparation operation such as meaningful:
- mixing
- soaking
- cooking
- boiling
- blending
- infusing
- fermenting
- grinding/combining
- or another actual preparation sequence.

Simple consumption/usage instructions do NOT by themselves qualify:
- "eat 8 curry leaves"
- "take Triphala"
- "drink coconut water"
- "eat one fruit"
- "take one tablet"

Keep such instructions in Detailed Timestamped Summary and, when useful,
Named Items Discussed.

4. SOURCE-CLAIM ATTRIBUTION
---------------------------
For medical, disease-treatment, physiological, scientific, longevity,
hormonal, detoxification, fertility, mental-health or other high-consequence
claims, preserve the source's level of certainty and attribution.

Use formulations such as:
- "The video claims..."
- "The speaker attributes..."
- "The source presents..."

when needed to avoid silently converting a source claim into an established
fact.

Do NOT:
- strengthen the source's certainty;
- independently fact-check unless explicitly requested;
- add unrelated external medical/scientific warnings or corrections;
- turn VideoHoarder into a fact-checking workflow.

5. ASR CRITICAL-FACT PROTECTION
-------------------------------
Apply extra caution to:
- medicine/formulation names
- herb/ingredient names
- product names
- people/organization names
- quantities/dosages
- frequency/duration
- prices
- URLs
- technical commands/identifiers/versions
- dates and important numeric values

Never confidently reconstruct a critical fact from damaged ASR merely because
a plausible term exists.

6. CHAPTER NAVIGATION QUALITY
-----------------------------
A chapter must represent a meaningful viewer navigation point.
Chapter titles should communicate what the viewer will find or learn there.
Avoid generic titles such as "Topic 1", "More Information", "Discussion" or
"Next Point" when a semantic title is recoverable.

7. Q&A RETRIEVAL QUALITY
------------------------
Q&A exists for future retrieval, not to duplicate the overview.
Each retained question should correspond to a plausible future search intent
and its answer should expose useful video-specific information.
Omit low-value/repetitive Q&A.

8. NAMED ITEMS PRECISION
------------------------
Named Items Discussed remains an entity/item index, not a keyword/concept
dump. Prefer concrete identifiable items. If a candidate name is materially
damaged by ASR, omit it or localize uncertainty rather than normalizing it by
guessing.

9. CATEGORY SPECIFICITY
-----------------------
Choose the most specific Category/Subcategory/Primary Topic/Content Type that
the source supports. Avoid unnecessarily generic classification when a stable,
useful narrower classification is obvious from the complete video.

10. V3.3.1 SEMANTIC ACCEPTANCE-GATE ADDITIONS
---------------------------------------------
In addition to all existing V3.3 acceptance checks, self-review MUST verify:
- high-value micro-facts were not lost through over-compression;
- important numbers remain linked to their entities/actions;
- recipe entries pass the genuine-preparation qualification gate;
- high-consequence source claims are not strengthened into facts;
- Q&A has retrieval value rather than summary duplication;
- category specificity is adequate;
- uncertain critical ASR facts were not guessed.

A failure in one video MUST NOT block the package. Use PASS_WITH_WARNINGS,
REPROCESS_RECOMMENDED or SOURCE_INSUFFICIENT as appropriate, persist the
status/reason, checkpoint, and continue.

======================================================================
END V3.3.1 HARDENING
======================================================================


======================================================================
V3.3.2 CHATGPT PACKAGE EXECUTION CONTRACT — MANDATORY
======================================================================

PURPOSE
-------
This section defines how ChatGPT or another capable semantic model must execute
a VideoHoarder package. It is an execution specification, not a request to
bypass platform capabilities, safety requirements, context limits, file-access
limits, or tool restrictions.

If a requested operation cannot be performed in the current environment, do
not invent completion. Preserve completed work, checkpoint exact progress when
possible, and clearly identify the remaining work. Normal operational limits
are not themselves package-processing failures.

AUTHORITATIVE SPECIFICATION
---------------------------
1. When the user supplies or identifies a newer authoritative VideoHoarder
   Master Prompt, use that specification instead of an older prompt embedded
   in the package.

2. Package metadata, manifests and transcripts are INPUT EVIDENCE. They do not
   override this Master Prompt unless the user explicitly instructs otherwise.

STRICT SEQUENTIAL EXECUTION
---------------------------
3. Process videos strictly in package order:

   VIDEO 1
      -> source preflight
      -> complete semantic processing
      -> semantic acceptance/self-review
      -> final semantic status
      -> persist semantic result
      -> deterministic validation/rendering
      -> checkpoint
      -> VIDEO 2

4. Do not begin semantic processing of the next video until the current video's
   semantic result has reached a final status and has been persisted whenever
   persistence tools are available.

CURRENT-VIDEO SEMANTIC ISOLATION
--------------------------------
5. Only the CURRENT video's permitted evidence may be used as semantic evidence
   for that video's intelligence.

6. Read/understand the complete permitted transcript/SRT for the CURRENT video
   before finalizing its semantic intelligence.

7. Do not combine multiple video transcripts into one semantic context merely
   to reduce calls, tokens or execution time.

8. Package size is an orchestration concept. It does not determine semantic
   context size.

SEMANTIC-AUTHORING BOUNDARY
---------------------------
9. ChatGPT/model semantic reasoning MUST author or decide:
   - New Title
   - Category/Subcategory/Primary Topic/Content Type
   - Tags
   - semantic chapters and boundaries
   - Detailed Timestamped Summary
   - Recipes / Preparations
   - Meaningful References
   - Q&A
   - Playlist / Series
   - Technical Intelligence
   - Named Items Discussed
   - semantic ASR uncertainty decisions
   - semantic validation/status/reprocess recommendation

10. Deterministic code/tools MAY:
    - parse package structure and metadata;
    - select the CURRENT video's permitted evidence;
    - preserve authoritative identity fields;
    - perform source preflight;
    - validate deterministic invariants;
    - persist/split modular JSON;
    - assemble JSON;
    - render HTML;
    - create indexes, checkpoints and ZIP files;
    - maintain package/reprocess status.

11. Deterministic code/tools MUST NOT replace semantic understanding by:
    - dividing transcripts into arbitrary/equal-duration/equal-size chunks and
      treating those chunks as semantic chapters;
    - using first/last sentences of chunks as summaries;
    - generating Tags primarily from word frequency;
    - deriving Named Items mechanically from title words/frequency;
    - generating generic chapter titles from timestamp intervals;
    - copying transcript passages and calling them semantic synthesis;
    - mechanically translating fragments and calling that completed semantic
      intelligence;
    - inferring missing semantic content from filenames, titles or unrelated
      metadata.

SEMANTIC COMPLETION DEFINITION
------------------------------
12. The existence of HTML, JSON or section files does NOT by itself mean that a
    video has been semantically processed.

13. A video counts as semantically processed only after:
    a. complete permitted evidence has been semantically understood;
    b. required semantic intelligence has been authored;
    c. semantic self-review/acceptance checks have run;
    d. a final semantic status has been assigned; and
    e. the semantic result has been persisted when persistence capability is
       available.

14. Never label placeholder, extractive, heuristic or mechanically generated
    intelligence as completed V3.3.2 semantic processing.

SOURCE FAILURE BEHAVIOR
-----------------------
15. If source evidence is clearly missing/incomplete:
       SOURCE_INSUFFICIENT
       -> record reason
       -> add to repackage list
       -> checkpoint
       -> continue.

16. If substantial evidence exists but ASR corruption prevents reliable
    recovery of important semantic information:
       REPROCESS_RECOMMENDED
       -> preserve only reliable intelligence
       -> never fabricate missing facts
       -> record reason
       -> checkpoint
       -> continue.

17. A weak or failed individual video MUST NOT block processing of later videos
    unless the package itself is structurally unusable.

NO QUALITY-DEGRADING FALLBACK
-----------------------------
18. Do not silently switch from semantic processing to heuristic/extractive
    generation because:
    - the package is large;
    - many videos remain;
    - execution is taking time;
    - token usage is high;
    - rendering/persistence is inconvenient.

19. If the full requested package cannot be completed in the current execution
    window, preserve all valid completed results and exact progress rather than
    replacing remaining semantic work with lower-quality output.

INTERRUPTION / RESUME CONTRACT
------------------------------
20. If execution must stop because of an actual environment/tool/context limit:
    - finish and persist the CURRENT video first when reasonably possible;
    - checkpoint the exact completed-video list;
    - identify the first unfinished VIDEO_ID;
    - retain completed semantic results;
    - resume later from the first unfinished video.

21. Do NOT rerun completed semantic processing merely because:
    - HTML rendering failed;
    - index creation failed;
    - ZIP creation failed;
    - package-summary generation failed;
    - execution was interrupted after persistence;
    - a later video failed.

RENDERING IS NOT SEMANTIC PROCESSING
------------------------------------
22. Rendering occurs only after semantic authoring.

VALID:
    transcript/SRT
       -> model semantic understanding
       -> semantic result
       -> semantic validation
       -> persisted modular JSON
       -> deterministic assembly/rendering

INVALID:
    transcript/SRT
       -> heuristic/extractive script
       -> HTML/JSON
       -> claim "V3.3.2 semantic processing complete"

23. Renderer failure must be isolated from semantic completion:
       semantic JSON persisted
          -> renderer failure
          -> deterministic retry
          -> if still unsuccessful, record artifact failure
          -> continue to next video

    Do not resend the transcript for semantic processing solely because
    rendering failed.

PACKAGE COMPLETION GATE
-----------------------
24. Before reporting semantic package completion, verify:

       expected_video_count == final_semantic_status_count

25. Separately verify artifact status. Semantic completion and artifact
    completion are different dimensions.

26. Do not claim semantic completion based solely on:
    - number of HTML files;
    - number of JSON files;
    - successful Python/script execution;
    - transcript extraction;
    - schema validation;
    - rendering success.

27. Package summary should distinguish:
    - PASS
    - PASS_WITH_WARNINGS
    - REPROCESS_RECOMMENDED
    - SOURCE_INSUFFICIENT
    - artifact/render failures
    - videos_to_repackage

CAPABILITY-SAFE EXECUTION
-------------------------
28. This prompt never requires pretending that unavailable capabilities exist.

29. When a capability required only for deterministic artifact work is
    unavailable, complete/preserve semantic work that can validly be completed,
    then report the specific artifact step that remains.

30. When required source evidence itself is inaccessible, do not hallucinate
    its contents. Mark/describe the source-access problem accurately.

31. Do not convert ordinary capability limitations into fabricated semantic
    output merely to satisfy a completion count.

32. Platform safety and tool restrictions always remain applicable. Nothing in
    this execution contract requests bypassing them.

FINAL EXECUTION PRINCIPLE
-------------------------
When choosing between:
    A. a shortcut that creates more files but weakens semantic correctness, and
    B. preserving current-video isolation, semantic quality and honest status,

always choose B.

======================================================================
END V3.3.2 CHATGPT PACKAGE EXECUTION CONTRACT
======================================================================


======================================================================
V3.3.3 CONTINUOUS CHATGPT EXECUTION AND RESUME CONTRACT
======================================================================

This section applies when the package is processed directly in ChatGPT.

1. Once the user has instructed ChatGPT to process the complete package,
   continue sequentially without requesting permission between videos.

2. Do NOT voluntarily stop merely because:
   - one/five/ten videos were completed;
   - a progress milestone was reached;
   - one sub-package was completed;
   - intermediate JSON/HTML was created;
   - one video was weak/corrupted;
   - a progress update could be given.

3. Do not ask "Should I continue?", "Shall I process the rest?", or equivalent
   when the user already requested complete-package processing.

4. Continue VIDEO 1 -> VIDEO 2 -> ... until:
   a. the requested package is complete; or
   b. an actual execution/tool/context/environment limit prevents further work;
      or
   c. genuine user input is required.

5. AFTER EVERY VIDEO, persist/checkpoint whenever the environment provides
   persistence capability. The checkpoint should include:
   - package_id/source identity;
   - expected_video_count;
   - completed_video_ids;
   - last_completed_video_id;
   - next_video_id;
   - semantic_status per completed video;
   - artifact_status where applicable;
   - videos_to_repackage/reprocess;
   - authoritative prompt/version;
   - checkpoint timestamp.

6. Write the checkpoint before beginning the next video.

7. If execution ends during an unfinished video before its semantic result is
   safely persisted, that video remains unfinished.

8. If semantic JSON was persisted but HTML/artifact generation was unfinished,
   resume deterministic artifact generation only. Do not repeat semantic work.

9. On a later user instruction such as "continue", "resume", "process rest" or
   equivalent:
   - inspect the durable checkpoint first;
   - identify next_video_id;
   - resume immediately from the first unfinished video;
   - do not ask the user to repeat package instructions already available;
   - do not restart completed videos unless their source changed, the stored
     result is invalid, prompt compatibility requires reprocessing, or the user
     explicitly requests it.

10. A weak video never requires permission to proceed. Assign the appropriate
    final status, record/repackage it, checkpoint, and continue.

11. If an actual execution limit forces a response before package completion,
    clearly distinguish interruption from completion and report the durable
    state when known:
       Completed: X / N
       Last completed: VIDEO_ID
       Next: VIDEO_ID
       Reprocess/repackage: [...]
       Prompt version: V3.3.3

12. Never replace remaining semantic work with heuristic/extractive generation
    merely to reach the requested completion count before an execution limit.

13. A prompt cannot override platform execution limits. Therefore interruption
    safety comes from per-video persistence and exact resume state, not from
    pretending one ChatGPT turn can run indefinitely.

14. Native scheduled tasks/automations are not a required part of package
    correctness. Package execution must remain safely resumable without a
    watchdog.

======================================================================
END V3.3.3 CONTINUOUS CHATGPT EXECUTION AND RESUME CONTRACT
======================================================================

======================================================================
V3.3.4 TRANSCRIPT HEALTH METADATA — SEMANTIC INTEGRATION CONTRACT
======================================================================

PURPOSE
----------------------------------------------------------------------

VideoHoarder may supply a machine-readable `transcript_health` object for the
CURRENT video.

`transcript_health` is deterministic preprocessing metadata created by code
before ChatGPT semantic processing. It summarizes mechanical source-quality
signals and package-routing information.

It is NOT semantic truth.

It does NOT replace any V3.3/V3.3.3 semantic requirement.

The CURRENT video's complete permitted transcript/SRT/VTT evidence must still
be understood as one semantic unit before final semantic intelligence is
accepted.

----------------------------------------------------------------------
1. TRANSCRIPT HEALTH IS ADVISORY CONTEXT
----------------------------------------------------------------------

Use supplied `transcript_health` only as context about known mechanical source
conditions.

When normalized structured transcript segments are supplied, treat their
timestamps as the authoritative mechanical timeline. Do not reconstruct or
replace that mechanical timestamp structure from raw inline timestamp markers
unless the structured representation is missing or clearly unusable.

Typical fields may include:

- `analyzer_version`
- `transcript_fingerprint`
- `score`
- `grade`
- `routing_class`
- `hard_failure`
- `signals`
- `reason_codes`
- `warnings`

The health grade may be:

- A
- B
- C
- D
- F

Typical routing classes may include:

- NORMAL
- CAUTION
- REPAIR_RECOMMENDED
- REPAIR_REQUIRED

Do NOT interpret these values as final semantic status.

Examples:

`transcript_health.grade = "A"` does NOT prove that medicine names, quantities,
technical terms, commands, claims or entities were transcribed correctly.

`transcript_health.grade = "C"` does NOT mean the semantic result must be
REPROCESS_RECOMMENDED.

The final semantic status remains independently determined by the semantic
processing rules in this Master Prompt.

----------------------------------------------------------------------
2. DO NOT REDO MECHANICAL HEALTH SCORING
----------------------------------------------------------------------

Do NOT spend semantic effort recreating VideoHoarder's mechanical health score.

Do NOT:

- recalculate the A/B/C/D/F grade;
- recalculate deterministic transcript density;
- recalculate duplicate-caption ratios merely to reproduce the health record;
- recalculate timestamp parse-rate metrics merely to reproduce the health
  record;
- create an alternative mechanical health score;
- rewrite or modify the supplied `transcript_health` object.

Use the supplied health metadata as advisory evidence only.

Normal semantic understanding of the transcript may naturally notice source
problems while performing the required V3.3.4 semantic pass. That is separate
from recreating the deterministic health algorithm.

----------------------------------------------------------------------
3. COMPLETE CURRENT-VIDEO UNDERSTANDING REMAINS MANDATORY
----------------------------------------------------------------------

For every eligible CURRENT video:

1. Read/understand the complete permitted transcript/SRT/VTT evidence for the
   CURRENT VIDEO.
2. Perform the existing five internal semantic phases.
3. Preserve current-video-only semantic isolation.
4. Perform semantic ASR/uncertainty judgment.
5. Perform semantic self-review and acceptance.
6. Assign the final semantic status independently.
7. Persist/checkpoint according to the existing package execution contract.

Do NOT reduce semantic reading because the transcript-health grade is good.

Do NOT skip whole-video understanding merely because code classified the video
as NORMAL.

----------------------------------------------------------------------
4. SEMANTIC JUDGMENT MAY OVERRIDE THE ROUTING EXPECTATION
----------------------------------------------------------------------

If complete semantic review finds an important source/ASR problem that the
mechanical analyzer did not capture, the semantic result takes precedence for:

- semantic warnings;
- uncertainty;
- targeted-review hints;
- REPROCESS_RECOMMENDED;
- SOURCE_INSUFFICIENT.

Examples include:

- an important medicine name that is semantically unrecoverable;
- a critical dosage whose ASR form is ambiguous;
- a technical command that cannot be reconstructed reliably;
- a materially corrupted named entity;
- transcript text that is mechanically dense but semantically incoherent;
- missing semantic continuity that was not deterministically detectable.

Do NOT alter the original `transcript_health` record.

Report semantic concerns through the existing semantic quality fields:

- `processing_status`
- `processing_warnings`
- `reprocess_recommended`
- `reprocess_reasons`
- `uncertain_items`
- `targeted_review_hints`

----------------------------------------------------------------------
5. HEALTH GRADE MUST NOT FORCE SEMANTIC STATUS
----------------------------------------------------------------------

These dimensions are independent.

Example A:

`transcript_health.grade = "C"`
`routing_class = "CAUTION"`

The semantic processor may still return:

`processing_status = "PASS"`

when the complete transcript is semantically reliable.

Example B:

`transcript_health.grade = "A"`
`routing_class = "NORMAL"`

The semantic processor may still return:

`processing_status = "REPROCESS_RECOMMENDED"`

when critical semantic ASR corruption prevents reliable recovery.

Never mechanically copy the health grade into semantic status.

----------------------------------------------------------------------
6. HARD-FAILURE PACKAGES
----------------------------------------------------------------------

Normally VideoHoarder should route deterministic hard failures away from the
normal semantic-processing package before ChatGPT receives them.

If a package nevertheless contains a CURRENT video whose supplied source is
clearly unusable, follow the existing source-failure contract honestly.

Do NOT fabricate semantic intelligence to overcome:

- missing transcript evidence;
- empty transcript evidence;
- independently confirmed material missing spoken content / clearly proven major truncation;
- severe source corruption that leaves no usable semantic speech evidence;
- another source failure that prevents reliable whole-video understanding.

Use SOURCE_INSUFFICIENT when warranted, record the reason, checkpoint, and
continue to the next VIDEO_ID.

----------------------------------------------------------------------
7. NO SECOND TRANSCRIPT-HEALTH PASS / NO SECOND TRANSCRIPT UPLOAD
----------------------------------------------------------------------

The intended V3.3.4 workflow is:

VideoHoarder selected transcript
-> deterministic local Transcript Health Analyzer
-> package creation
-> ChatGPT semantic processing of that same selected transcript

Do NOT request that the user upload the same transcript a second time merely to
perform health scoring.

Do NOT ask ChatGPT to perform a separate transcript-health grading pass before
normal semantic processing.

`transcript_health` travels with the same video package as operational metadata.

----------------------------------------------------------------------
8. TRANSCRIPT HEALTH IS INTERNAL
----------------------------------------------------------------------

Do NOT display transcript-health diagnostics as an ordinary visible Video
Intelligence Report section.

Do NOT add visible sections such as:

- Transcript Health
- Health Grade
- Transcript Score
- Mechanical Quality
- Routing Class
- Analyzer Signals
- Health Reason Codes

The application may retain these fields internally in source/quality metadata
or expose them separately in an administrative/diagnostic interface.

They are not part of the normal human-readable semantic report.

----------------------------------------------------------------------
9. GROUP SIMILAR VIDEOS DOES NOT CHANGE SEMANTIC ISOLATION
----------------------------------------------------------------------

VideoHoarder may place videos into the same processing package because a
separate Group Similar Videos planner determined that they are topically
related and operationally compatible.

That grouping is an orchestration decision only.

If a package contains:

VIDEO_1
VIDEO_2
VIDEO_3

do NOT use VIDEO_1 content as semantic evidence for VIDEO_2.

do NOT combine VIDEO_1 + VIDEO_2 + VIDEO_3 transcripts into one semantic
understanding.

Final semantic processing remains:

VIDEO_1 only
-> complete semantic processing
-> final semantic status
-> persist/checkpoint

then VIDEO_2 only
-> complete semantic processing
-> final semantic status
-> persist/checkpoint

then VIDEO_3 only
-> ...

Topic similarity never authorizes cross-video semantic contamination.

----------------------------------------------------------------------
10. V3.3.4 CONTINUOUS EXECUTION / RESUME REMAINS UNCHANGED
----------------------------------------------------------------------

All V3.3.3 direct-ChatGPT continuous execution and resume requirements remain
mandatory.

In particular:

- process package videos strictly sequentially;
- do not voluntarily stop at arbitrary progress milestones;
- persist/checkpoint each completed semantic unit when persistence is
  available;
- resume from the first genuinely unfinished video;
- do not semantically rerun completed compatible videos merely because the
  package was interrupted;
- if semantic JSON is complete but HTML is pending/failed, resume deterministic
  artifact generation only;
- never replace remaining semantic work with heuristic/extractive generation.

----------------------------------------------------------------------
11. FINAL V3.3.4 HEALTH PRINCIPLE
----------------------------------------------------------------------

When choosing between:

A. trusting a deterministic health grade as proof of semantic quality; and
B. using the grade only as mechanical context while independently performing
   complete current-video semantic understanding,

always choose B.

The authoritative separation is:

VIDEOHOARDER CODE
-> mechanical transcript health
-> routing/package balancing
-> source preflight
-> deterministic persistence/validation/rendering

CHATGPT / SEMANTIC PROCESSOR
-> complete current-video understanding
-> semantic chapters
-> detailed intelligence
-> recipes/references/Q&A/technical intelligence
-> search intelligence
-> semantic ASR uncertainty
-> semantic self-review
-> final semantic status

======================================================================
END V3.3.4 TRANSCRIPT HEALTH INTEGRATION CONTRACT
======================================================================

======================================================================
V3.3.4 HARDENING ADDENDUM — PACKAGE SELF-CONTAINMENT AND COMPLETION
======================================================================

The following rules are mandatory for packages created from this prompt.
They clarify V3.3.4 behavior and do not weaken any earlier V3.3.4 rule.

----------------------------------------------------------------------
1. SELF-CONTAINED PACKAGE REQUIREMENT
----------------------------------------------------------------------

Every ChatGPT processing package must be self-contained.

At minimum, preserve or create:

- CHATGPT_PACKAGE.json
- VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md
- PACKAGE_README.txt
- manifest.json
- schema.json
- prompt.json
- evidence.json

The included prompt snapshot is authoritative for that package.

The package prompt hash must be calculated from the exact prompt snapshot
inside the package, not from a later source file on the user's computer.

----------------------------------------------------------------------
2. COMPLETION AND UNFINISHED VIDEO RULE
----------------------------------------------------------------------

Package completion requires every expected VIDEO_ID to have a final semantic
status.

Allowed final semantic statuses remain only:

- PASS
- PASS_WITH_WARNINGS
- REPROCESS_RECOMMENDED
- SOURCE_INSUFFICIENT

If a VIDEO_ID is missing from the ChatGPT returned result, that does not prove
source insufficiency.

Missing or unfinished returned videos must be represented as execution state,
for example:

- PENDING
- IN_PROGRESS
- INTERRUPTED

Do not automatically convert a missing returned result into SOURCE_INSUFFICIENT.

SOURCE_INSUFFICIENT is reserved for mechanically or semantically proven
insufficient evidence.

----------------------------------------------------------------------
3. NO-TRANSCRIPT PACKAGE SEPARATION
----------------------------------------------------------------------

Videos without usable transcript/SRT/VTT evidence must never be mixed into
normal transcript-processing packages.

They may be routed to:

- source repair;
- retranscription;
- no-transcript handling;
- metadata-only holding;
- or another explicit non-normal path.

They must not consume normal V3.3.4 transcript-semantic package capacity.

----------------------------------------------------------------------
4. GROUPING HIERARCHY FOR PACKAGE CREATION
----------------------------------------------------------------------

When a grouping plan is used for package creation, preserve this hierarchy:

parent_group
  -> topic_subgroups
    -> video_ids

Topic subgroups describe the precise subject/research organization.

Parent groups control actual ChatGPT package creation and may combine closely
related small topic subgroups so package creation remains efficient.

Do not create one processing package per tiny topic subgroup when those videos
can be sensibly combined into a related parent group.

----------------------------------------------------------------------
5. MEASURABLE TINY-PACKAGE RULE
----------------------------------------------------------------------

Preferred package size: globally optimized; there is no minimum package size.

Maximum package size: 30 videos.

There is no minimum package size and no special 1-14 package exception contract.
The deterministic global optimizer should minimize the number of packages subject to the hard maximum of 30 videos, transcript-workload safety, transcript/no-transcript separation, and semantic compatibility. Small final packages are valid when they are the optimizer's safe remainder; they do not require an exception flag.

Topic compatibility and workload safety remain more important than merely approaching the advisory target of 25 videos.

----------------------------------------------------------------------
6. RESUME SAFETY REQUIREMENT
----------------------------------------------------------------------

Completed compatible semantic results must not be rerun merely because a
package was interrupted.

If semantic JSON is already persisted but HTML rendering failed or was
interrupted, resume deterministic artifact rendering only and then continue
semantic processing at the next unfinished VIDEO_ID.

These resume rules protect token usage and preserve per-video semantic
commit boundaries.

======================================================================
V3.3.4 UNTIMESTAMPED FALLBACK — PRESERVE SOURCE TIMESTAMP HINTS
======================================================================

If `canonical_transcript.timestamps_available = false` and
`canonical_transcript.untimestamped_text` contains usable speech text:

- Treat `untimestamped_text` as authoritative transcript evidence for semantic
  understanding.
- Continue semantic processing of the video; timestamp failure alone is NOT a
  reason to discard the video or declare SOURCE_INSUFFICIENT.
- If `timestamp_hints_available = true`, preserve the supplied
  `timestamp_hints` as approximate source-provided navigation clues only.
- A timestamp hint may help identify the rough location of nearby content, but
  it is NOT an authoritative normalized timestamp.
- Do NOT spend significant reasoning time repairing, reconstructing,
  interpolating, or validating timestamp hints.
- Do NOT present them as exact timestamps.
- Do NOT turn approximate hints into exact chapter/recipe/reference ranges.
- Do NOT invent a timestamp that is absent from the supplied evidence.
- Do NOT assume a hint is precise merely because it resembles a YouTube/SRT/VTT
  timestamp.
- Return `chapters.v1.chapters` as an empty array when reliable normalized
  chapter boundaries are unavailable.
- For Detailed Summary, Recipes / Preparations, References, Q&A, Playlist /
  Series, Technical Intelligence, and Named Items, preserve supported semantic
  content. Exact timestamp fields or segment IDs that cannot be grounded in
  normalized segments must remain empty/omitted.
- When a human-readable field can safely mention an approximate location
  without claiming exactness, a directly supplied source hint may be used as an
  approximate clue (for example, "around 00:12") only when helpful.
- Title, Category, Tags, Detailed Summary and other non-time-dependent
  intelligence should still be produced normally from the transcript.
- Record a concise internal warning that exact timestamp-dependent navigation
  was unavailable; do not expose internal diagnostics as a normal visible
  section.

When `timestamps_available = true`, use only the normalized canonical segment
timestamps as authoritative timeline data.

`timestamps_available = true` is an explicit VideoHoarder reliability assertion,
not merely evidence that timestamps were parseable. VideoHoarder must set it to
false whenever its deterministic timing gate detects non-monotonic timing, severe
timestamp corruption, invalid/overlapping ranges, materially weak timestamp
parsing, or otherwise unsafe canonical timing. Such videos remain FULL_INTELLIGENCE
when usable speech text exists; the package must carry cleaned `untimestamped_text`
and any source-provided markers only as approximate `timestamp_hints`.

This fallback preserves useful source timing clues without wasting model effort
on mechanical timestamp recovery and without presenting unreliable timing as
exact.


======================================================================
V3.3.4 IMPLEMENTATION CORRECTION — TIMING CAPABILITY DOES NOT LIMIT SEMANTIC SCOPE
======================================================================

These rules supersede any earlier wording that could imply that weak,
missing or unparseable timestamps require restricted semantic processing.

1. If usable transcript speech text exists, perform FULL semantic intelligence
   regardless of timestamp quality.

2. Reliable normalized timestamps:
   - use them normally for Chapters, Detailed Timestamped Summary, recipes,
     references, Q&A and navigation fields that require time ranges.

3. Approximate source timestamp hints:
   - preserve source-provided markers when available;
   - they may be used as rough navigation clues only;
   - do not spend significant reasoning time repairing, reconstructing,
     interpolating or validating them;
   - do not present them as exact timing;
   - never invent missing timestamps.

4. No usable timing:
   - continue all non-timestamp semantic work normally;
   - do not search for or reconstruct timestamps;
   - do not invent time ranges;
   - semantic chapter/topic structure may still be produced without exact
     start/end times when the response schema permits null/absent timing.

5. Timestamp quality alone must never cause a usable transcript to be
   downgraded to NO_TRANSCRIPT solely because timestamps are weak. New V3.3.4 packages do not create a timestamp-driven RESTRICTED_INTELLIGENCE profile.

6. Only genuinely missing or semantically unusable transcript text may prevent
   normal FULL_INTELLIGENCE processing.

7. Package grouping is operational only. Every VIDEO_ID remains semantically
   isolated and must be processed from that video's evidence alone.


---

## V3.3.4 CURRENT-LIBRARY, TIMING-FALLBACK, AND PACKAGE-OPTIMIZER CONTRACT

These rules are authoritative for V3.3.4 processing packages:

1. **Usable transcript text always receives FULL_INTELLIGENCE.** Timestamp quality alone MUST NOT reduce the semantic processing profile. A transcript with usable speech remains eligible when timestamps are partial, malformed, missing, approximate, or unavailable.
2. **Reliable normalized timestamps are authoritative navigation evidence.** Use them for chapters and timestamped summary boundaries.
3. **Approximate source timestamp hints are retained, not discarded.** When normalized timing is unavailable but source-provided markers exist, use those markers only as approximate navigation clues. Do not claim they are exact.
4. **Do not waste reasoning on timestamp recovery.** Do not repair, reconstruct, interpolate, validate, or invent missing timestamps. Continue directly with the semantic task.
5. **No usable timing does not block semantic output.** Produce all evidence-supported non-time sections normally. Semantic chapter/topic structure may still be returned, but exact start/end timestamps must be null/absent when unsupported.
6. **Per-video isolation remains mandatory.** Package composition does not permit evidence from one video to influence another.
7. **Package size is not a semantic signal.** VideoHoarder may combine compatible videos to minimize the number of packages. Continue to process every VIDEO_ID independently.


---

## V3.3.4 CANONICAL-TRANSCRIPT SELECTION BOUNDARY

VideoHoarder performs local Transcript Health analysis and any applicable source recovery before this semantic package is processed. The transcript supplied here is VideoHoarder's selected canonical evidence. Do not attempt to download, search for, replace, or repair another transcript during semantic processing.

Transcript Health is mechanical context, not semantic truth. A remaining C or D transcript that still contains usable speech text remains valid FULL_INTELLIGENCE evidence. Use reliable normalized timestamps when available; otherwise retain supplied source timestamp hints only as approximate navigation clues and continue semantic processing without reconstructing timing.


======================================================================
V3.3.4 SOURCE-COVERAGE AND CAPTION-ARTIFACT SEMANTIC CLARIFICATION
======================================================================

These rules refine how the CURRENT video's canonical transcript evidence is
interpreted. They do not change the existing five-phase semantic process.

1. COMPLETE EVIDENCE READ != PROVEN COMPLETE VIDEO SPEECH COVERAGE
-----------------------------------------------------------------
Read and understand all permitted canonical transcript evidence supplied for the
CURRENT VIDEO. However, complete understanding of the supplied transcript does
not by itself prove that the transcript contains every meaningful spoken portion
of the original media.

The normal semantic pass receives the canonical transcript generated from exactly
one selected winning subtitle source. Multiple VTT/SRT variants are storage/input
candidates only and MUST NOT be concatenated, counted as corroboration, or treated as
independent evidence.
The canonical transcript and canonical SRT must represent the same deduplicated spoken sequence from that winning source; progressive/rolling caption display repetition is a formatting artifact, not repeated speech.

Use supplied completeness metadata when present:

- `COMPLETE` / `LIKELY_COMPLETE`: normal whole-source semantic processing, subject
  to all existing uncertainty rules.
- `UNKNOWN`: process all supplied evidence normally, but do not assert that absent
  media portions contain no additional spoken information. Do not invent them.
- `PARTIAL`: analyze the supported transcript evidence fully, but do not infer,
  fabricate, summarize or create chapters/intelligence for missing spoken ranges.
  Use REPROCESS_RECOMMENDED or SOURCE_INSUFFICIENT when the missing evidence is
  material to a complete-video result.
- `NONE`: follow the existing no-usable-transcript/source-insufficient path.

A VTT ending substantially before the video duration is not, by itself, evidence
that speech is missing. The remainder may contain silence, music, visual-only
demonstration, credits or an end screen. Treat supplied mechanical tail warnings
as coverage uncertainty unless missing speech is independently established.

2. CAPTION DISPLAY ARTIFACTS ARE NOT SPOKEN EMPHASIS
----------------------------------------------------
The canonical transcript may originate from WebVTT/YouTube captions. Progressive
or rolling caption repetition is a display artifact, not evidence that the
speaker repeated or emphasized the same phrase. Use the normalized spoken
sequence supplied by VideoHoarder. Do not infer semantic emphasis from caption
rendering duplication.

3. NON-SPEECH CUES
------------------
Markers such as `[Music]`, `[Applause]`, `[Laughter]`, silence or sound-effect
annotations are contextual evidence only. Do not turn them into factual claims,
Named Items, Tags, Q&A, References or Chapters unless the non-speech event itself
is materially relevant to understanding the video's content.

4. SOURCE MODALITY / CERTAINTY REMAINS MANDATORY
------------------------------------------------
Continue to preserve the source's level of certainty and attribution under the
existing SOURCE-CLAIM ATTRIBUTION rules. In particular, do not silently change:

- `may` -> `does`;
- `can help` -> `cures`;
- a recommendation/personal experience -> universal fact.

This is source-faithful semantic rewriting, not external fact-checking.

======================================================================
END V3.3.4 SOURCE-COVERAGE AND CAPTION-ARTIFACT CLARIFICATION
======================================================================


======================================================================
V3.3.4 FINAL SEMANTIC FIDELITY + PACKAGE-QUALITY CONTRACT
======================================================================

This section is normative and resolves any ambiguous older wording.

1. SOURCE FIDELITY IS NOT FACT-CHECKING
- Determine what the supplied allowed evidence says and represent it accurately.
- Do not judge processing quality by whether the video's claims are objectively true.
- Do not browse/search externally to verify a claim during this pass.
- Preserve speaker attribution where necessary for claims, recommendations, opinions,
  predictions or disputed assertions; do not make attribution repetitive.

2. DESCRIPTION / COMMENTS
- Description, comments, sponsor/affiliate copy and other prohibited metadata are not
  semantic evidence for Chapters, Detailed Summary, Recipes, References, Q&A, Tags,
  Named Items or other content intelligence.
- Permitted identity/orchestration metadata may still be used only where the package
  contract explicitly allows it.

3. DETAILED SUMMARY QUALITY
- Each topic summary must contain video-specific substance supported by the evidence.
- Generic boilerplate or a repeated paragraph shell is not an acceptable substitute
  for understanding.
- Capture only details actually present. Empty/omitted optional detail is better than
  invented quantities, cautions, examples, steps or conclusions.

4. NAMED ITEMS
- Include only meaningful identifiable items actually discussed in allowed evidence.
- Never create Named Items by tokenizing the title, word frequency, keyword lists or
  generic concepts such as "foods", "avoid", "mistakes", "can" or "become".
- Empty is better than invented.

5. Q&A
- Questions must be useful retrieval questions that this specific video's evidence
  actually answers. Avoid repetitive generic questions such as mechanically asking
  the main point of every video.

6. PROVENANCE
- Evidence references must point to evidence that actually supports the associated
  output. Do not mechanically attach the first few segment IDs to whole-video output.
- Never invent a segment ID or timestamp. Untimestamped fallback remains valid evidence.

7. PER-VIDEO SELF-AUDIT BEFORE FINALIZATION
Check: whole-video coverage; source fidelity; no invention; selective attribution;
no prohibited description/comment leakage; meaningful chapters; video-specific
summary; precise Named Items; retrieval-useful Q&A; real references; supporting
provenance; and no fabricated timing. Correct recoverable issues before moving to
the next VIDEO_ID.

8. PACKAGE INPUT QUALITY
If `package_quality` is supplied, it is deterministic mechanical INPUT-EVIDENCE
context only. It must never change what the video says, trigger fact-checking, or
automatically determine a video's semantic status. Grade/score and workload are
separate concepts. Process higher-priority packages first when orchestrating a batch,
but process every individual video under the same semantic-fidelity standard.
