# Workflow Catalog

Recorded: 2026-08-15

| Workflow | Status | Flow and evidence | Gap/constraint |
|---|---|---|---|
| Full download | IMPLEMENTED / UNKNOWN RUNTIME | URLs -> metadata/transcript/media -> staging -> validation -> library/report/DB | Network/media not run |
| Media-only download | IMPLEMENTED / UNKNOWN RUNTIME | URL list -> selected quality -> media output | Not run |
| Smart resume/retry | IMPLEMENTED / NEEDS REVIEW | failure/artifact state -> resume/retry functions | Interruption matrix untested |
| Old-library import | IMPLEMENTED / UNKNOWN RUNTIME | source folders -> preflight -> metadata/path merge -> repair | Needs controlled fixtures |
| Repair selected data | IMPLEMENTED / UNKNOWN RUNTIME | selected VIDEO_IDs -> metadata/transcript/comments/report/package/index actions | Central manifest checkbox proposal not implemented |
| Transcript/report pipeline | IMPLEMENTED / NEEDS REVIEW | caption/transcript acquisition -> cleanup/analysis -> report/index | Provider and visual-output coverage missing |
| ChatGPT standard package | IMPLEMENTED / PARTIAL | selected IDs/scopes -> evidence/prompt/schema/manifest/checksums -> manual upload | Real end-to-end return not run this audit |
| Smart quality batch set | IMPLEMENTED / PARTIAL | transcript preflight -> max-25 full-intelligence and max-50 metadata batches -> index | Real populated batch set not run |
| Similarity planner | PARTIAL | metadata catalog -> manual ChatGPT grouping -> strict import validation -> grouped package creation | No KEEP/SKIP/REVIEW model or manual group-edit UI |
| Result import/review | IMPLEMENTED / PARTIAL | one/many JSON files -> integrity/provenance/timestamp validation -> review previews -> decisions | Folder import and automatic application absent by design/current code |
| Combined review export | IMPLEMENTED / NEEDS REVIEW | validated/partial previews -> combined CSV | Function present; no dedicated automated test |
| Tag cleanup | IMPLEMENTED / PARTIAL | Phase 5 index -> JSONL export -> manual ChatGPT -> JSONL import -> taxonomy backup/update | Separate files/history exist, but not unified with v3 request/coverage lifecycle |
| Taxonomy packages | IMPLEMENTED / NEEDS REVIEW | batch export -> result import -> preview/apply/undo -> status | Real apply/undo not run |
| Knowledge indexing | IMPLEMENTED / NEEDS REVIEW | reports/intelligence -> search/chunk/embedding indexes -> search/Ask Library | Empty DB/no model test |
| Collection package | IMPLEMENTED / NEEDS REVIEW | collection -> estimate -> focused/full package export | Not run |
| Duplicate review | IMPLEMENTED / VERIFIED SAFETY | group -> canonical -> keep/archive/mark-delete record | Automated test proves no physical delete |
| Clip-plan handoff | IMPLEMENTED / VERIFIED SAFETY | proposed clips -> ID/time/duration/path validation -> saved manual handoff | Automated test proves no execution |
| Purge/delete marker | IMPLEMENTED / UNKNOWN RUNTIME | marker -> reviewed purge of DB/files/indexes | Destructive; intentionally not run |
| Backup/recovery | IMPLEMENTED / NEEDS REVIEW | locate backups/folders -> merge/rebuild/audit -> checkpoints | Disaster recovery not exercised |
| Build/install | IMPLEMENTED / HISTORICALLY VERIFIED | compile/tests/icon/PyInstaller/ZIP/install | Current source not rebuilt in this audit |
