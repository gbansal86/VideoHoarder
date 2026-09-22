# Security

Recorded: 2026-08-15
Overall status: NEEDS REVIEW

| Severity | Finding | Evidence/status |
|---|---|---|
| HIGH | Plaintext installed API-key file | `<VIDEOHOARDER_HOME>\api_key.txt` exists; value was not read; excluded by Git |
| HIGH | Browser profile/session material beside source | ignored `tools/edge-*` trees contain browser databases/state; not tracked |
| HIGH | Powerful local HTTP mutation surface | custom handler exposes configuration, files, jobs, moves, deletion markers, imports and tools; trust-boundary review missing |
| MEDIUM | Broad exception suppression | numerous `except Exception: pass` paths can conceal validation/cleanup failures |
| MEDIUM | Path/file serving complexity | media/report/thumb/open-folder/exchange paths require dedicated traversal and authorization tests |
| MEDIUM | Dependency/tool acquisition | application can locate/install/update tools; integrity and supply-chain controls need review |
| LOW | No common token/private-key patterns detected | repository and knowledge scans found zero scoped matches; this is not proof of absence |

Positive controls include loopback-oriented design, manual ChatGPT exchange, manifest checksums, safe evidence paths, review-only imports, `.gitignore`, and non-physical duplicate/clip review. No secrets are reproduced here.


## 2026-09-22 OSS/API hardening update

- The OSS source package no longer contains the runtime `data/database/video_library.db`.
- OpenAI API credentials are environment-variable-only; no `openai_api_key` config field is accepted.
- External AI results do not bypass the deterministic package importer or manual-review state.
- API processing is one-video isolated and `store=false` by default.
- Restricted/private/unlisted videos are blocked from API submission unless explicitly enabled.
- Public repository security guidance, CodeQL, Dependabot, CI, and issue/PR templates were added.
- The older `api_key.txt` finding remains relevant to historical/runtime installations using YouTube credentials; credential values must stay outside source control.
