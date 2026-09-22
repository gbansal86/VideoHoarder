# Package Inventory

Recorded: 2026-08-15

The audited source DB contains zero package rows; the following is an implementation inventory, not a live package listing.

| Package/result family | Identity/files | Tracking status |
|---|---|---|
| ChatGPT Processing v3 package | package/request ID; evidence, prompt, schema, manifest, README; hashes | request, video membership, feature coverage, status/result/review fields implemented |
| Smart quality master set | master-set ID, batch index/README, child packages, profile/group/batch numbers | filesystem index plus child request rows; implemented |
| Similarity planner | planner package ID; catalog, prompt, schema, manifest, validated plan | request status/result/hash/validation implemented |
| ChatGPT result | incoming JSON and review preview keyed by package/result hash | single/many validation implemented; manual review required |
| Review decisions | dated JSON under review/decisions; request notes | implemented; physical changes false |
| Duplicate review | review UUID and JSON | implemented separately; physical changes false |
| Clip plan | dated JSON under review/clip_plans | implemented separately; execution false |
| Tag-cleanup package/result | fixed Phase 5 JSONL paths | implemented separately; not package-ID/feature-coverage integrated |
| Legacy Phase 2 package/result | manifests, result dirs, history/status/retry/archive | implemented legacy/parallel system; requires consolidation assessment |
| Phase 6 taxonomy/intelligence | batch exports, root inbox/results, processed-ID status | implemented parallel lifecycle |

Processing is tracked separately for VIDEO_ID and v3 package/result. Tag cleanup and its result are separate files, not first-class v3 lifecycle entities. Reprocessing controls exist through coverage/source snapshots/config and legacy retry paths, but no single unified reprocessing ledger exists.
