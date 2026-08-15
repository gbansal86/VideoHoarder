# Security

Recorded: 2026-08-15
Overall status: NEEDS REVIEW

| Severity | Finding | Evidence/status |
|---|---|---|
| HIGH | Plaintext installed API-key file | `D:\YT GUi\api_key.txt` exists; value was not read; excluded by Git |
| HIGH | Browser profile/session material beside source | ignored `tools/edge-*` trees contain browser databases/state; not tracked |
| HIGH | Powerful local HTTP mutation surface | custom handler exposes configuration, files, jobs, moves, deletion markers, imports and tools; trust-boundary review missing |
| MEDIUM | Broad exception suppression | numerous `except Exception: pass` paths can conceal validation/cleanup failures |
| MEDIUM | Path/file serving complexity | media/report/thumb/open-folder/exchange paths require dedicated traversal and authorization tests |
| MEDIUM | Dependency/tool acquisition | application can locate/install/update tools; integrity and supply-chain controls need review |
| LOW | No common token/private-key patterns detected | repository and knowledge scans found zero scoped matches; this is not proof of absence |

Positive controls include loopback-oriented design, manual ChatGPT exchange, manifest checksums, safe evidence paths, review-only imports, `.gitignore`, and non-physical duplicate/clip review. No secrets are reproduced here.
