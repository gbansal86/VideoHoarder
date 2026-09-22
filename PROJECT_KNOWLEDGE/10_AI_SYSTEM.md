# AI System

Recorded: 2026-08-15

## Local AI

Ollama support includes server/model checks, generation, configurable model/timeouts/retries, evidence prompts, answer cache, fast/deep modes, and Knowledge AI integration. Source is IMPLEMENTED; current runtime behavior is UNKNOWN because Ollama was not invoked.

## Manual ChatGPT processing v3

Package generation writes `evidence.json`, `prompt.json`, `schema.json`, `manifest.json`, and `PACKAGE_README.txt`; SHA-256 values and request/video/feature state are persisted. The application validates manifest/package identity, safe paths, file hashes, exact VIDEO_IDs, schema, evidence provenance, and timestamps before producing review-only records.

Core validators are VERIFIED by automated tests. Full real-user lifecycle is PARTIAL because no current populated package was created, returned, imported, reviewed, or applied.


## Optional OpenAI Responses API processing - 2026-09-22

VideoHoarder v33.1 adds an optional `app/openai_api_service.py` provider beside the existing manual ChatGPT exchange. The provider consumes the same self-contained VIDEO_INTELLIGENCE package, submits exactly one VIDEO_ID per model call, uses the package formal JSON Schema as Structured Outputs when supported, merges per-video results, and passes the result through `import_validate_manual_chatgpt_processing_result()`. API results remain review-only and are never automatically applied.

The API key value is not stored in VideoHoarder. `openai_api_key_env` stores only the environment-variable name (default `OPENAI_API_KEY`). Provider audit JSON records model/response/timing/token metadata without the secret. Responses use `store=false` by default. Private/unlisted/restricted videos are blocked unless `openai_allow_restricted_videos` is explicitly enabled.

The manual file-exchange workflow remains supported and is not replaced by the API path.

## Smart planning

The planner uses metadata, title, channel, description, library/YouTube category, and transcript availability. Optional local category/keyword exclusions are rule-based; AI grouping occurs only after manual upload to ChatGPT. Imported plans enforce every ID exactly once, correct transcript group type, max 25 transcript-backed, and max 50 no-transcript.

KEEP/SKIP/REVIEW classification and manual group editing are NOT IMPLEMENTED as first-class workflow states. YouTube category is an explicit optional exclusion, not an automatic rule.

## Tag cleanup and legacy package systems

Phase 5 tag cleanup has a separate JSONL prompt/export/import and taxonomy backup. Phase 2 legacy packages/results/history and Phase 6 taxonomy/intelligence packages coexist with v3 ChatGPT Processing. This is functional breadth but also lifecycle fragmentation requiring reconciliation—not replacement without proof.
