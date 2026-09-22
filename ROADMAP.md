# Roadmap

Roadmap items are directional rather than promises or deadlines.

## P0 — OSS/reliability

- Continue extracting feature logic from the oversized `app.py` into focused services with compatibility wrappers.
- Keep Windows full-suite CI green and expand deterministic fixtures for transcript/provider workflows.
- Publish signed/versioned releases with release notes and reproducible build evidence.
- Improve first-run diagnostics for dependencies and API/provider readiness.

## P1 — Transcript intelligence

- Strengthen canonical transcript candidate selection/provenance across legacy libraries.
- Expand deterministic transcript-health golden fixtures and idempotent repair tests.
- Persist provider/model/prompt/input-hash provenance for every accepted semantic feature.
- Add API cost/token estimates before submission and per-video budget controls.
- Add explicit cancel/resume checkpoints for long API package runs.

## P1 — Architecture

- Move remaining ChatGPT package/import/review logic from `app.py` into dedicated package, validation, and orchestration modules.
- Isolate HTTP route registration from core business logic.
- Reduce shared globals through focused configuration/state interfaces.

## P2 — Community

- Publish newcomer-friendly architecture diagrams and sample fixture library.
- Label good-first-issue/documentation/test contributions.
- Add contributor-facing plugin/provider interface documentation after the core API provider stabilizes.

## Local video roadmap

- Add optional offline speech-to-text for `platform=local` videos lacking subtitles.
- Strengthen preview of imported collections: file-size estimates, duplicate-content detection and per-file selection.
- Extend optional local metadata enrichment while keeping YouTube-only retrieval limited to YouTube records.
