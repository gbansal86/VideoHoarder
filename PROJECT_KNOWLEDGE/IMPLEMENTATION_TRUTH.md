# Implementation Truth

Recorded: 2026-08-15
Classification: IMPLEMENTED, PARTIAL, NOT IMPLEMENTED, UNKNOWN, or DEPRECATED

| Capability | Status | Evidence and truth |
|---|---|---|
| Desktop/local dashboard | IMPLEMENTED | `app/gui.py`, `app/native_ui.py`, local HTTP handler; current dashboard smoke test passes |
| Downloads/transcripts/reports | UNKNOWN runtime | extensive source in `app/app.py`; not executed with network/media |
| Library/search/Knowledge | PARTIAL | source implemented; audited DB empty and Ollama not run |
| Jobs/progress/stop/retry | PARTIAL | queue/job functions and APIs exist; concurrency/interruptions not tested |
| Repair/recovery/destructive tools | UNKNOWN runtime | source exists; controlled end-to-end safety tests absent |
| ChatGPT v3 package files/state | IMPLEMENTED | evidence/prompt/schema/manifest/checksum generation and SQLite request/video/coverage state |
| Package integrity/provenance/timestamps | IMPLEMENTED | source plus passing automated tests |
| One/many JSON result import | IMPLEMENTED | endpoints/functions exist; validation core tested, many-file path not directly tested |
| Combined review CSV | IMPLEMENTED | `export_chatgpt_processing_review_csv()`; not directly tested |
| Physical automatic ChatGPT apply | NOT IMPLEMENTED | imports/reviews explicitly set `automatic_apply=False`; physical tools remain separate |
| Similarity planner metadata/category/preflight | IMPLEMENTED | planner catalog/exclusions/transcript availability functions |
| AI KEEP/SKIP/REVIEW classification | NOT IMPLEMENTED | no planner result/state contract for these labels; local exclusions only |
| AI similar grouping | IMPLEMENTED | planner prompt/result contract and validation |
| Manual group rename/merge/split/move/add/remove UI | NOT IMPLEMENTED | planner page only create/import/create-from-plan; no editor controls/functions found |
| Max-25 transcript batches | IMPLEMENTED | enforced in plan validation and batch creation |
| Small group single package | IMPLEMENTED | each validated group becomes one package if under limit |
| No-transcript workflow | IMPLEMENTED | separate metadata profile; up to 50 in current code |
| Folder result import | NOT IMPLEMENTED | browser accepts selected files/payloads, not a filesystem folder operation |
| Per-video edit page/user notes in planner | NOT IMPLEMENTED | no planner edit/notes persistence found |
| Tag-cleanup export/result/import | IMPLEMENTED / PARTIAL | separate Phase 5 JSONL system; not unified with v3 lifecycle tables |
| Duplicate review safety | IMPLEMENTED | passing test confirms no physical changes |
| Clip-plan handoff safety | IMPLEMENTED | passing test confirms validation/save without execution |
| Central Artifact Manifest | PARTIAL | JSON snapshot table/helpers exist; authoritative proposal remains NOT IMPLEMENTED |
| Git/project handoff | IMPLEMENTED | private GitHub main and canonical `PROJECT_KNOWLEDGE` |

No feature becomes verified merely because a historical spec or UI string says “implemented.” Current test/runtime evidence is stated separately.
