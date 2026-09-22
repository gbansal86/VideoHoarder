# VideoHoarder Metadata Architecture — Implemented Specification V1

**Status:** Implemented and cumulatively tested through Phase 9  
**Scope:** Metadata normalization, persistence, source chapters/tags, transcript evidence grading, ChatGPT package contract, existing-library migration, and legacy-reader migration.  
**Authority:** This document describes the behavior actually implemented in the delivered Phase 9 code snapshot. Where older planning documents differ, this implemented specification is authoritative for the delivered code.

## 1. Objectives

The implementation establishes a maintainable metadata architecture that:

1. Keeps useful source metadata without sending unnecessary raw yt-dlp structures to ChatGPT.
2. Preserves `.info.json` for compatibility and recovery while reducing direct reader dependency on it.
3. Reuses existing VideoHoarder database/transcript fields instead of creating a competing transcript system.
4. Keeps source chapters and source tags auxiliary and non-semantic.
5. Makes transcript health/evidence grading independent of description, clean title, source tags, source chapters, and comments.
6. Uses a canonical A/B/C/D/F grading system for normal-package eligibility and repair routing.
7. Builds ChatGPT transcript-intelligence payloads through an explicit allow-list.
8. Migrates existing library metadata safely through dry-run, backup, resumable/idempotent processing.
9. Makes legacy readers canonical-metadata-first while keeping `.info.json` fallback.
10. Moves the new business logic out of `app.py` into responsibility-focused modules.

## 2. Implemented Module Ownership

| Module | Responsibility |
|---|---|
| `app/metadata_schema.py` | Additive metadata schema migrations |
| `app/metadata_normalization.py` | Raw extractor metadata → canonical metadata classifications |
| `app/metadata_persistence.py` | Canonical SQLite persistence and retained `.info.json` refresh |
| `app/source_tags.py` | Source-tag normalization, conservative junk filtering, audit output |
| `app/source_chapters.py` | Immutable source chapters, display-title overlay, subchapter validation/navigation |
| `app/transcript_evidence.py` | Canonical A/B/C/D/F evidence grade normalization and routing |
| `app/chatgpt_package_builder.py` | Strict allow-listed ChatGPT video payload construction and validation |
| `app/metadata_migration.py` | Existing-library dry-run/apply/backup/idempotent migration |
| `app/legacy_metadata.py` | Canonical-first legacy metadata resolution with `.info.json` fallback |

`app.py` remains the high-level application/orchestration layer. The above modules own the new metadata business rules.

## 3. Canonical Metadata Classification

### 3.1 LLM Core

The canonical metadata normalizer exposes these semantic-package identity/context fields:

- `id`
- `original_title`
- `channel`
- `upload_date`
- `duration_seconds`
- `webpage_url`
- `availability`
- `category`

`category` is populated from the application's existing `youtube_category_name` storage concept. The implementation does not create a parallel `categories_json` canonical category field.

### 3.2 LLM Auxiliary

Auxiliary metadata is explicitly separate from transcript evidence:

- `source_chapters`
- `source_tags_raw`
- `source_tags_cleaned` where appropriate downstream

Rules:

- Source chapters are for navigation/seeking.
- Source tags are for search/indexing.
- Neither source chapters nor source tags may influence transcript health, evidence grade, transcript interpretation, or transcript-derived claims.

### 3.3 Local Only

Examples of locally retained metadata include:

- `description`
- channel identifiers/URLs and follower/verification metadata
- view/like/comment counts
- heatmap
- thumbnail
- playlist metadata
- media language/live state
- `filesize_approx`

`description` is retained locally for presentation/report uses and is not part of transcript-intelligence semantic evidence.

### 3.4 Temporary Technical

Large technical extractor structures are not copied into canonical metadata:

- `formats`
- codec/bitrate/resolution/protocol fields
- temporary media URLs
- raw automatic-caption URL maps
- extractor implementation details

yt-dlp may use these values during its own execution. The rule is not that yt-dlp must never obtain them; the rule is that VideoHoarder does not persist or send those large technical structures as canonical semantic metadata.

### 3.5 Derived / Redundant

Redundant presentation/technical values are derived when needed rather than treated as independent semantic facts.

## 4. Database / Schema Behavior

Schema changes are additive and idempotent.

The implementation reuses existing fields wherever possible, including:

- `video_id`
- `original_title`
- `clean_title`
- `url`
- `channel`
- `upload_date`
- `duration_seconds`
- `youtube_category_name`
- `youtube_tags`
- `tags`
- existing subtitle/transcript source/language fields
- existing transcript health / canonical transcript infrastructure

New canonical metadata/migration fields are added only where the prior schema lacks the required concept.

Migration ownership lives in `metadata_schema.py`. `app.py` delegates schema migration to this module.

No destructive database-column removal is performed as part of the delivered Phase 1–9 implementation.

## 5. Raw yt-dlp Metadata Normalization

Entry point: `normalize_extractor_metadata(raw, fallback=None)`

Behavior:

1. Accepts the rich raw extractor dictionary.
2. Produces structured canonical output grouped into `llm_core`, `llm_auxiliary`, `local_only`, `derived`, and temporary-technical field inventory.
3. Normalizes source chapters without overwriting source titles.
4. Normalizes source tags without treating them as transcript evidence.
5. Excludes raw formats and caption/download URL maps from canonical output.
6. Keeps useful local metadata such as heatmap and filesize estimate in local-only storage.
7. Supports fallback values from existing VideoHoarder records when the extractor payload is sparse.

`flattened_persistence_view()` converts the normalized structure to the database-oriented persistence view.

## 6. Future Download Persistence

Future metadata flow:

`yt-dlp / YouTube API → canonical normalization → legacy save path + canonical SQLite persistence`

The implementation keeps current `.info.json` creation/retention behavior.

After download metadata assets are available, the retained `.info.json` can be normalized and used to enrich canonical SQLite fields.

Persistence is **richness-preserving**:

- meaningful incoming values may update canonical fields;
- sparse/empty incoming values do not erase richer data already stored.

This prevents a sparse API refresh from destroying richer chapters, heatmap, playlist/live state, tags, channel information, or filesize previously learned from `.info.json`.

## 7. Source Tags

Module: `source_tags.py`  
Main API: `clean_source_tags(values)`

The output preserves normalized raw source tags, cleaned source tags, and removed tags with reasons.

Filtering is deliberately conservative. It may remove obvious junk such as URL-like/promotional/subscribe-style tags according to deterministic rules, while preserving legitimate entities, products, topics, and source tags.

Source tags remain separate from AI/transcript-derived tags. AI-generated semantic tags are derived from the transcript independently; source tags do not become evidence for transcript meaning.

## 8. Source Chapters

Module: `source_chapters.py`

Implemented behavior:

1. Normalize YouTube/source chapters into stable records.
2. Preserve source timestamp and `source_title`.
3. Allow a separate `display_title`.
4. Allow validated transcript-supported subchapters/navigation enhancements.
5. Never overwrite the original source title.
6. If source chapters do not exist, navigation may fall back to transcript-derived chapter structure.

Source chapters remain navigation/seeking context only and cannot alter transcript grading or transcript interpretation.

## 9. Transcript Evidence and Grade Model

Module: `transcript_evidence.py`

Canonical grades: `A`, `B`, `C`, `D`, `F`.

Legacy compatibility: legacy evidence grade `E` is normalized to `F`.

Normal transcript-intelligence package eligibility:

- A: eligible
- B: eligible
- C: eligible according to normal package/profile rules
- D: excluded from normal package; repair routing
- F: excluded from normal package; repair routing

Transcript evidence grading is based on transcript/timestamp/coverage/integrity signals.

The following must not influence transcript health/evidence grade:

- `description`
- `clean_title`
- source tags
- source chapter names
- comments

`original_title` may remain identity context but may not downgrade a valid transcript merely because wording differs.

## 10. ChatGPT Transcript-Intelligence Package Contract

Module: `chatgpt_package_builder.py`

The builder uses an explicit allow-list.

Conceptual payload:

```json
{
  "video_id": "<video id>",
  "package_grade": "A",
  "metadata": {
    "id": "<video id>",
    "original_title": "<source title>",
    "clean_title": "<VideoHoarder clean title>",
    "channel": "<channel>",
    "upload_date": "<date>",
    "duration_seconds": 0,
    "webpage_url": "<url>",
    "availability": "<status>",
    "category": "<category>"
  },
  "auxiliary_metadata": {
    "source_chapters": [],
    "source_tags": []
  },
  "transcript_provenance": {
    "...": "existing transcript provenance/health"
  },
  "evidence": {
    "canonical_transcript": {}
  }
}
```

Rules:

- `clean_title` may be present as operational/title context but is not transcript evidence.
- `description` is excluded from the transcript-intelligence package.
- raw comments are excluded from this package boundary.
- technical yt-dlp metadata is excluded.
- D/F videos are not admitted to normal transcript-intelligence packages.
- auxiliary source chapters/tags remain explicitly non-semantic.
- package validation rejects forbidden keys/structures.

Comments may be handled by a separate future/comment-specific package path; the delivered implementation does not use comments as transcript evidence.

## 11. Existing-Library Migration

Module: `metadata_migration.py`

Source priority:

1. Existing canonical/legacy SQLite values
2. Retained `.info.json`
3. Local metadata sidecars/artifacts
4. Optional metadata-only yt-dlp refresh when still materially sparse

The migration supports dry-run, reports per-video source chain/warnings, creates a transaction-consistent SQLite backup before apply when requested, records migration lifecycle/status, is resumable, is idempotent, skips already-current rows unless forced, does not redownload video/audio merely to repair metadata, and preserves existing ChatGPT semantic/result fields.

The optional app fallback uses metadata extraction with `--skip-download`.

## 12. Legacy Reader Resolution

Module: `legacy_metadata.py`

Resolution priority:

1. Canonical SQLite metadata
2. Local hints / canonical local values
3. Retained `.info.json` fallback

The implementation updates key legacy workflows so `.info.json` is no longer necessarily the first or mandatory metadata source when canonical SQLite metadata exists.

`.info.json` remains retained for compatibility and recovery. Sparse canonical metadata can still fall back to retained `.info.json`.

## 13. `.info.json` Policy

Final delivered policy:

- Do not disable `.info.json` retention.
- Keep it for compatibility/recovery.
- Prefer canonical SQLite metadata for migrated readers.
- Use `.info.json` as fallback/enrichment source.
- Never send the full raw `.info.json` to the transcript-intelligence LLM package.
- Never require media redownload merely because canonical metadata is missing.

## 14. Comments Policy

- Comments are not transcript evidence.
- Comments do not affect transcript health or evidence grade.
- Comments are not included in the normal transcript-intelligence strict package.
- Existing comment acquisition/analysis can remain separate.
- Future comment-specific package/analysis behavior is outside this delivered metadata implementation.

## 15. `clean_title` Policy

- Keep existing `clean_title` because VideoHoarder uses it operationally and AI may later produce improved naming.
- It may appear in the strict package as title/operational context.
- It must not influence transcript evidence grade, transcript health, transcript consistency, or semantic interpretation.

## 16. `description` Policy

- Keep `description` locally.
- Do not use it for transcript evidence/grade.
- Do not include it in the normal transcript-intelligence package.
- It may later be used in final HTML/report presentation.

## 17. `filesize_approx`

- Retain locally.
- Intended for future operational use such as download prioritization.
- The delivered Phase 1–9 implementation does not implement smaller-first download ordering.

## 18. Backward Compatibility

The implementation is intentionally additive.

Key compatibility measures:

- existing DB columns are reused;
- destructive schema cleanup is deferred;
- `.info.json` remains available;
- legacy evidence grade `E` is normalized to `F`;
- strict package builder tolerates legacy DB rows where newer optional canonical columns are absent;
- migration does not invalidate existing ChatGPT semantic results merely because metadata was backfilled;
- compatibility fallbacks remain available while canonical metadata becomes primary.

## 19. Testing / Acceptance Contract

Final Phase 9 automated results:

- Phase 9 acceptance tests: 6 passed
- Phase 1–9 focused cumulative tests: 61 passed
- Full VideoHoarder suite: 140 passed, 3 skipped
- Python compile/import check: PASS

Golden fixture routing:

- A/B/C: normal package eligible
- D/F: excluded and repair-routed
- tested across 13 frozen fixtures

Performance measurements in the delivered environment showed sub-millisecond average overhead for real metadata normalization and strict package build/validation.

## 20. Known Limitations

The following are not known code defects, but were not executable in the offline implementation environment:

1. Live YouTube/network download workflows.
2. Live metadata-only fallback against YouTube.
3. Migration of the user's entire real production database/library.
4. Final production Git checkpoint/tag in the user's actual repository.

Before production rollout:

1. Commit/tag the real repository.
2. Run Phase 7 dry-run against a copy of the real database.
3. Review migration counts/warnings.
4. Take a fresh SQLite backup.
5. Apply migration on the controlled copy.
6. Validate representative real downloads and live metadata refresh.
7. Roll out to the production library only after those checks.

## 21. Future Technical Debt

`app.py` remains large because the Phase 0–9 project intentionally extracted only responsibilities touched by this metadata initiative.

Future development should continue the approved incremental rule:

**Touch a functional area → assess responsibility → extract related business logic into a focused module when appropriate → keep orchestration in `app.py`.**

Do not perform a risky unrelated wholesale rewrite merely to reduce line count.

## 22. Source of Truth

For the delivered Phase 9 code:

1. This implemented specification describes the intended behavior.
2. The Phase 9 automated tests enforce the executable contract.
3. `PHASE_0_TO_9_IMPLEMENTATION_PROGRESS.docx` contains the full engineering/test history.
4. Phase HTML evidence contains actual input/output examples from each phase.

If a future change intentionally modifies this behavior, update this specification and the relevant executable tests in the same change.

## 23. Local Repair of Already-Downloaded Metadata

The **Missing Data & AI** cleanup checkbox now runs canonical metadata repair for the selected already-downloaded videos in addition to subtitle/transcript artifact cleanup.

Local metadata repair uses the implemented canonical migration pipeline with this source priority:

1. Existing SQLite metadata.
2. Existing local metadata sidecars/artifacts.
3. Retained `.info.json`.
4. Canonical normalization, source chapter/tag normalization, richness-preserving SQLite persistence, migration status/version update, and audit report.

This branch is deliberately offline: it passes no metadata fetcher and does not call YouTube Data API, yt-dlp metadata refresh, or media download. Missing fields that cannot be recovered locally remain sparse/warned. The separate **Refresh YouTube metadata** checkbox remains the only refresh action on this page.

A transaction-consistent SQLite backup and JSON migration report are created for each local repair run. The repair can be scoped to the selected video IDs; leaving the selection blank applies it to the active library videos selected by the existing page behavior.

Description repair is implemented in the governed post-Phase-9 description-cleanup change documented below.

## 23. Description Cleanup Integration (Post-Phase-9 Governed Change)

Implemented behavior:

- The existing **Clean up duplicate transcripts, metadata, and descriptions per video** checkbox now submits `subtitle_cleanup`, `canonical_metadata_repair`, and `description_cleanup` together.
- Description cleanup is local-only and does not invoke YouTube API, yt-dlp refresh, or media download.
- The retained yt-dlp `*.description` file remains untouched.
- `description.txt_raw` is created once as the immutable canonical raw cleanup source under `_data` when `_data` exists.
- `description.txt` and `description.html` are deterministic derived outputs under `_data`.
- After all three `_data` canonical description artifacts are validated, obsolete root-level `description.txt_raw`, `description.txt`, and `description.html` are deleted. This cleanup is idempotent.
- Root-level `metadata.info.json` and retained yt-dlp `*.description` source artifacts are explicitly preserved.
- URL occurrences are validated before replacing canonical outputs; DB update occurs only after safety validation.
- Cleaned canonical text is persisted to `videos.description`.
- Planner/grouping and taxonomy paths that intentionally allow description call `canonical_clean_description()` before adding description to outgoing content, so manual cleanup is not a prerequisite.
- The strict transcript-intelligence package continues to forbid description.
- Canonical metadata repair excludes `*.comments_source.info.json`; normal metadata priority is `metadata.info.json` -> exact `<video_id>.info.json` -> other normal video-ID-matching info JSON -> other verified normal info JSON.
- Description parsing is owned by `app/description_parser.py`; VideoHoarder file/DB orchestration is owned by `app/description_cleanup.py`.

Validation for this governed change: 10 new description integration tests passed; 73 Phase 1-9 + description focused tests passed; full repository suite 152 passed with 3 skipped; compile/import validation passed. Git checkpoint remains pending in the user's real repository because the uploaded code package contains no `.git` history.

