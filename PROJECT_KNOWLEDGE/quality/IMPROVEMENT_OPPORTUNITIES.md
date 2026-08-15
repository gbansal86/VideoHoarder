# Improvement Opportunities

Recorded: 2026-08-15

| Priority | Classification | Opportunity | Evidence/rationale | Authorization |
|---|---|---|---|---|
| P0 | POTENTIAL RISK | Replace plaintext API-key storage | `D:\YT GUi\api_key.txt` exists; contents were not read | Not authorized for implementation |
| P0 | RECOMMENDED IMPROVEMENT | Protect GitHub `main` and keep repository private | New baseline is the only Git recovery history | Owner/browser setting |
| P1 | RECOMMENDED IMPROVEMENT | Add path, schema, job, and package characterization tests | Large mutation surface with limited tests | Not authorized |
| P1 | RECOMMENDED IMPROVEMENT | Implement Central Artifact Manifest incrementally | Existing table/helpers are only a partial foundation | Await bounded feature approval |
| P1 | POTENTIAL RISK | Replace broad silent exception suppression with contextual handling | Numerous `except Exception: pass` sites can hide partial failure | Not authorized |
| P1 | RECOMMENDED IMPROVEMENT | Add sanitized populated-library fixtures | Current checked DB is empty | Not authorized |
| P2 | RECOMMENDED IMPROVEMENT | Modularize `app/app.py` behind preserved interfaces | Backend mixes persistence, filesystem, HTTP, UI, AI, and external tools | Characterization tests first |
| P2 | RECOMMENDED IMPROVEMENT | Add installed-runtime UI/end-to-end tests | Native tests skipped in system Python; prior build evidence is historical | Not authorized |
| P2 | RECOMMENDED IMPROVEMENT | Add release provenance manifest | Existing EXE matches installed copy but not independently tied to a Git build | Not authorized |
| P2 | POTENTIAL RISK | Review local HTTP trust boundary and request/path validation | Powerful endpoints are intended for local desktop use | Dedicated security review needed |
| P3 | FUTURE IDEA | Generate feature-to-code-to-test traceability automatically | Catalog maintenance is manual | Backlog only |
| P3 | FUTURE IDEA | Add large-library performance and interruption benchmarks | Manifest/scanning/package behavior needs scale evidence | Backlog only |

No discretionary improvement in this list is approved merely because it is recorded.
