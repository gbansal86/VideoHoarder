# AI System

Recorded: 2026-08-15

## Local AI

Ollama support includes server/model checks, generation, configurable model/timeouts/retries, evidence prompts, answer cache, fast/deep modes, and Knowledge AI integration. Source is IMPLEMENTED; current runtime behavior is UNKNOWN because Ollama was not invoked.

## Manual ChatGPT processing v3

Package generation writes `evidence.json`, `prompt.json`, `schema.json`, `manifest.json`, and `PACKAGE_README.txt`; SHA-256 values and request/video/feature state are persisted. The application validates manifest/package identity, safe paths, file hashes, exact VIDEO_IDs, schema, evidence provenance, and timestamps before producing review-only records.

Core validators are VERIFIED by automated tests. Full real-user lifecycle is PARTIAL because no current populated package was created, returned, imported, reviewed, or applied.

## Smart planning

The planner uses metadata, title, channel, description, library/YouTube category, and transcript availability. Optional local category/keyword exclusions are rule-based; AI grouping occurs only after manual upload to ChatGPT. Imported plans enforce every ID exactly once, correct transcript group type, max 25 transcript-backed, and max 50 no-transcript.

KEEP/SKIP/REVIEW classification and manual group editing are NOT IMPLEMENTED as first-class workflow states. YouTube category is an explicit optional exclusion, not an automatic rule.

## Tag cleanup and legacy package systems

Phase 5 tag cleanup has a separate JSONL prompt/export/import and taxonomy backup. Phase 2 legacy packages/results/history and Phase 6 taxonomy/intelligence packages coexist with v3 ChatGPT Processing. This is functional breadth but also lifecycle fragmentation requiring reconciliation—not replacement without proof.
