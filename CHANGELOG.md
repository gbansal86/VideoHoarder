# Changelog

## 33.2-GUI — 2026-09-22

- Added independent **Import Local Videos** desktop/web page, read-only preview, file/folder scan, stable local IDs, SQLite registration and local playback support.
- Default leave-in-place mode; optional copy or explicitly confirmed move without overwriting existing managed destinations.
- Adjacent subtitle/transcript association and local timestamped-evidence cache; no automatic network, ASR or OpenAI request on import.
- Local records excluded from YouTube-only caption fetching and destructive YouTube-deletion reconciliation; retained original manual and optional OpenAI processing paths.
- Added importer regression tests and [local import instructions](docs/LOCAL_VIDEO_IMPORT.md).


## 33.1-GUI — 2026-09-22

### Added

- Optional OpenAI Responses API provider for Video Intelligence packages.
- One-VIDEO_ID-per-model-call semantic isolation.
- Structured Outputs using the existing VideoHoarder formal result schema, with JSON-object compatibility fallback.
- Environment-variable-only API key handling; key values are never persisted by VideoHoarder.
- Provider status/readiness in native Settings and the ChatGPT Processing command center.
- Sanitized `OPENAI_API_RUN.json` audit with response IDs/timing/token usage but no secrets.
- `OPENAI_API_RESULT_<package>.json` merged result artifact.
- Privacy gate blocking private/unlisted/restricted videos unless explicitly enabled.
- Provider unit/integration tests using fake clients (no real API calls).
- Public OSS README, license, security, contribution, governance, support, roadmap, issue/PR templates, CI and Dependabot configuration.

### Changed

- API results now reuse the same existing manual-result importer/validator and remain subject to manual review before apply.
- Normal manual ChatGPT package exchange remains fully supported.
- OpenAI provider code lives in its own service module instead of adding provider transport logic to `app.py`.

## 33.0-GUI

- Existing native desktop UI, managed queue, transcript intelligence packaging, library/report workflows, and Windows packaging baseline.

## Public distribution hardening (2026-09-22)

- Kept OpenAI Responses API transcript submission optional and disabled by default; no key is bundled.
- Added staged source privacy/secret audit and regression tests, public-release checklist, and stricter packaging/ignore rules.
- Replaced historical machine-specific documentation paths with `<VIDEOHOARDER_HOME>` placeholders and omitted historical real-video evidence from public release packaging.
- The existing public GitHub history and Windows binary are not changed by this source-only release.
