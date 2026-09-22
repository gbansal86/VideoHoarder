# VideoHoarder 33.1-GUI — OSS/API implementation summary

Date: 2026-09-22

## Scope completed

This source milestone prepares VideoHoarder for public OSS maintenance and adds an optional OpenAI API path without removing the existing manual ChatGPT package workflow.

### OpenAI transcript-intelligence provider

- New focused provider module: `app/openai_api_service.py`.
- Uses the OpenAI Responses API through the official Python SDK.
- Reuses VideoHoarder's existing self-contained `VIDEO_INTELLIGENCE` package, authoritative master prompt, formal JSON contract, and deterministic importer/validator.
- Processes exactly one `VIDEO_ID` per model request, sequentially.
- Uses Structured Outputs when the package schema is accepted; falls back to JSON-object mode if the historical schema is not accepted, while keeping VideoHoarder's importer as the final authority.
- Reads the API key only from an environment variable (`OPENAI_API_KEY` by default). The key value is not stored in VideoHoarder config, reports, manifests, or provider audit files.
- Sets API response storage off by default.
- Blocks private/unlisted/restricted videos by default; external submission requires explicit opt-in.
- Writes a sanitized provider audit and merged API result into the existing package folder.
- Imports the result into the existing review workflow; API processing never auto-applies title/file/database changes.

### UI/config integration

- Added native Settings controls for enable/disable, model, reasoning effort, key environment-variable name, and restricted-video opt-in.
- Added OpenAI status and submit actions to the ChatGPT Processing page for both an existing package and a newly created current selection.
- Added safe provider settings to `settings_service.py`, `config.default.json`, and the sanitized package template.
- Manual package exchange remains available and unchanged as a fallback.

### OSS/public-repository hardening

Added or expanded:

- `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `GOVERNANCE.md`, `MAINTAINERS.md`, `SUPPORT.md`, `TESTING.md`, `RELEASING.md`, `ROADMAP.md` and `OSS_PROJECT_OVERVIEW.md`;
- GitHub issue and pull-request templates;
- Windows + Linux CI contracts;
- CodeQL workflow;
- Dependabot configuration;
- public OpenAI API, architecture and maintainer-automation documentation;
- Code Parent packaging allow-list so the public OSS/governance/CI files are included in clean handoffs.

Runtime SQLite data and live `app/config.json` are deliberately excluded from the clean Code Parent package.

## Current codebase dimensions

- Python files considered in the source/test/build tree: **101**
- Python LOC: **48,675**
- `app/app.py`: **29,928 lines**
- Test files: **37**
- Test functions discovered: **355**

The application still has a large legacy orchestration module. New provider transport was intentionally placed in a focused module instead of increasing the provider/business-logic footprint in `app.py`. Further modularization should follow the strangler-style roadmap rather than a big-bang rewrite.

## Final source validation

- Full pytest suite: **341 passed, 22 skipped, 0 failed**.
- Focused OpenAI/provider/package tests: PASS.
- Python compile validation: PASS.
- OpenAI provider tests use a fake SDK/client; **no live paid API call was made** during this review.
- Windows PyInstaller/EXE build: **not executed on this Linux review host**. It remains a required Windows release gate.

## Key source SHA-256 fingerprints

- `app/app.py`: `C7C9CDBD1C675338EDB9363AF36E4B29D3BEFB22D2858AB3041FDA0464A9B2EE`
- `app/native_ui.py`: `9D607CAC3E9B629FC6F88624CC2AD921E4E65F4C94EC1D2BCBABDCF039D22915`
- `app/openai_api_service.py`: `8EEEE358631ED33611DBC0AFFFACAF9E592D0363710B5D8B7A52EF1E0EB823A5`
- `app/settings_service.py`: `992A057FBE6414A5EABE606C30E326EC5098121329CFBDEFFA4A6EC3C3468AD7`
- `scripts/create_code_parent_package.py`: `0589FA21D9D559E74B7F19F27F453C8E74346594D6C1D4C22018B9A748181D8D`
- `requirements.txt`: `3361D7A03D436A537A759CEE0E2E27EF215CDE3582099483E3D1A67A3A6AF63D`

## Release safety notes

1. Set the OpenAI API key in the environment, never in repository/config files.
2. Keep `openai_store_responses=false` unless the maintainer deliberately changes the privacy policy.
3. Keep restricted-video submission off unless the user explicitly opts in and is authorized to send that material externally.
4. Treat all API results as proposals until the existing VideoHoarder validator/review workflow accepts them.
5. Build and smoke-test the Windows executable before publishing a binary release.
