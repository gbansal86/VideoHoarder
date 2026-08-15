# Prompt Library

Recorded: 2026-08-15

| Prompt family | Location | Version/state |
|---|---|---|
| ChatGPT Processing feature package | `create_manual_chatgpt_processing_package()` | schema/prompt `3.0`; generated JSON |
| Similarity batch planner | `create_manual_chatgpt_batch_planner()` | schema `3.0`; generated JSON |
| Phase 5 tag cleanup | `phase5_tag_cleanup_prompt()` | embedded multiline text; no explicit version |
| Phase 6 taxonomy/intelligence | Phase 6 export functions in `app/app.py` | embedded/generated; separate lifecycle |
| Ollama evidence answering | `phase6_evidence_prompt()` and related functions | embedded; model/settings external |
| Transcript/title/chapter/report AI | earlier `app/app.py` AI functions | embedded strings and configuration |

Status: PARTIAL governance. Version fields exist for the v3 package system, but prompts are dispersed through one large module and several legacy/current workflows. There is no centralized registry documenting prompt ID, version, input contract, output schema, compatibility, safety rules, or regression tests.

Do not consolidate prompts until callers, formats, and backward compatibility are characterized.
