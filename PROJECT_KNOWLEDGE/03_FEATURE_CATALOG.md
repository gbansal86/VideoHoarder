# Feature Catalog

| Area | Status | Evidence | Limitation |
|---|---|---|---|
| Desktop shell | IMPLEMENTED | `app/gui.py`, `app/native_ui.py` | Live interaction not tested this audit |
| Local dashboard/API | IMPLEMENTED | request handler and `/api/*` paths in `app/app.py`; smoke test passes | No authentication review for non-loopback exposure |
| Downloads/queue/jobs | IMPLEMENTED / NEEDS REVIEW | download, progress, job-control functions and UI | Real download not run |
| Library/search/reports | IMPLEMENTED / NEEDS REVIEW | library, detail, report, indexes and Knowledge Center code | Checked DB empty |
| Transcript/captions | IMPLEMENTED / NEEDS REVIEW | transcript API, VTT/SRT, cleanup and analysis functions | Network/media cases not run |
| ChatGPT exchange | IMPLEMENTED / PARTIAL | request/coverage tables, package create/import/review code; validation tests pass | Complete real lifecycle not run |
| Similar-video planner | IMPLEMENTED | planner import/group validation test passes | UI not exercised |
| Duplicate review | IMPLEMENTED | review test confirms no physical delete | Downstream manual operation not tested |
| Clip planning | IMPLEMENTED | validation/handoff test passes | Cutting/merge not tested |
| Collections/Knowledge AI | IMPLEMENTED / NEEDS REVIEW | Phase 6 functions and API paths | Ollama/live data not tested |
| External media/subscriptions | IMPLEMENTED / NEEDS REVIEW | tables, routes, commands | External integrations not tested |
| Maintenance/recovery | IMPLEMENTED / NEEDS REVIEW | audit/repair/backup/rebuild functions | Destructive/large-data paths not run |
| Central artifact manifest | PARTIAL | table plus `artifact_inventory`, `artifact_manifest_for_video`, `build_video_artifact_manifest` | Proposed lifecycle/history/reconciliation/UI/export completeness missing |
| Git handoff | BLOCKED | no `.git` directory | Must be established with owner approval |
