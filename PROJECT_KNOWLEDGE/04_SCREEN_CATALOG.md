# Screen Catalog

Recorded: 2026-08-15

| Surface | Status | Evidence | Current verification |
|---|---|---|---|
| Native Dashboard | IMPLEMENTED | `app/native_ui.py:CommandCenter` | Source reviewed; native test skipped without PySide6 |
| Queue | IMPLEMENTED | `QueueTable`, `JobDetails`, `/api/jobs`, job controls | Source reviewed; concurrency UX not exercised |
| Library | IMPLEMENTED | native navigation plus embedded Library tab and library APIs | Empty audit DB prevents data-driven validation |
| Old Import | IMPLEMENTED / UNKNOWN RUNTIME | `/oldimport`, old-library preflight/import functions | Not executed against user data |
| Repair Data | IMPLEMENTED / UNKNOWN RUNTIME | `/repairdata`, `repair_selected_video_data()` | Not executed against user data |
| ChatGPT Processing | IMPLEMENTED / PARTIAL | `/chatgpt-processing`, overview/planner/create/import/review/history/coverage panels | Core HTTP page existed historically; current full UI not interactively tested |
| Group Similar Videos | PARTIAL | planner panel injected before Create Package | Planner create/import/grouped-create exists; no manual group-edit workspace |
| Knowledge | IMPLEMENTED / UNKNOWN RUNTIME | Phase 5/6 search, topic pages, Ask Library, Ollama settings | Empty DB and no Ollama runtime test |
| Collections | IMPLEMENTED / UNKNOWN RUNTIME | collection APIs/menu, create/rename/delete/export | Not tested with populated collections |
| Settings | IMPLEMENTED / NEEDS REVIEW | `SettingsPage`, config GET/save | Sensitive keys must remain masked/external |
| More/Workflows | IMPLEMENTED | eight native workflow cards and embedded tool catalog | Native declarations partly covered by skipped tests |
| Downloads | IMPLEMENTED / UNKNOWN RUNTIME | composer/presets and download jobs | Network/media actions not run |
| Failures | IMPLEMENTED / UNKNOWN RUNTIME | failure summary/list/retry records | No populated failure fixture |
| Health/Diagnostics | IMPLEMENTED / PARTIAL | health, full diagnostics, dependencies, safe repair | Read-only endpoints not comprehensively exercised |
| Clip Studio | IMPLEMENTED / NEEDS REVIEW | clip UI/project table and merge job; ChatGPT handoff route | ChatGPT plan validation tested; actual merge not run |
| Streams/External Media | IMPLEMENTED / UNKNOWN RUNTIME | external media UI/table/download job | External download not run |
| YouTube Subscriptions | IMPLEMENTED / UNKNOWN RUNTIME | subscriptions UI/table/collection job | Browser/network workflow not run |
| Future Request Editor | IMPLEMENTED DOCUMENT TOOL | `specs/future_requests/VideoHoarder_Future_Requests_Editor.html` | Standalone spec editor, not application functionality |

Historical installed-build observations in `specs/` remain evidence for 2026-08-13 only and are not treated as a current interactive test.
