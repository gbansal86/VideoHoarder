# Codex Miss Analysis — Issue 6

## Scope
Compared the supplied `VideoHoarder_Code_Parent(3).zip` against the user-reported Issue 6 acceptance scenarios. This is code-path analysis plus executed automated evidence; native Windows GUI runtime remains separately required.

## Why the earlier Codex revision still missed behavior

| Issue | What existed | Why it still failed the user scenario | Corrective design |
|---|---|---|---|
| Job Details layout | Buttons/actions existed | Pause + Retry/Cancel were packed into a narrow side panel, so labels/actions could clip | Stack primary controls full-width and verify in Windows native GUI |
| Duplicate video downloaded twice | `redownload_history_check()` existed | Native downloader did not call it; `ALREADY_ACTIVE` did not require confirmation; current queue duplicates were not checked | Shared duplicate guard used by native + web; confirm active-library, deleted-history, queued/running and recent successful matches |
| Library count did not rise immediately | Stats service existed | Dashboard stats used a long timer and job completion did not trigger a stats refresh | Trigger library/stat refresh when a newer terminal job appears |
| Queue columns hidden | Columns existed | Fixed widths exceeded viewport, scrollbars were not explicitly guaranteed, Dashboard showed only a capped compact queue | Explicit H/V scrollbars plus dedicated Queue page with all session rows and Refresh queue |
| Dashboard and Queue same page | Sidebar entries existed | Router mapped both routes to the same `CommandCenter`, only changing focus | Separate `NativeQueuePage`; Dashboard remains compact overview |
| Queued jobs gave no reason | Queue status existed | Row/job details did not explain paused queue vs waiting behind another job | Expose queue-state reason in row tooltip/status and Job Details |
| Refresh figures stayed stale after manual file deletion | DB had `downloaded=1` and folder metadata | Availability count trusted stale DB state/folder existence rather than physical media; asynchronous rebuild could also complete after the immediate refresh | Dashboard availability uses physical media truth; terminal rebuild/download completion triggers another stats refresh |
| Build governance disappeared | Functional code changes existed | `docs/implementation` and the integrity test fixture were omitted from the delivered package, so traceability/completion gates could not catch missing acceptance paths | Restore baseline, feature inventory, traceability, phase evidence, actual test logs, final validation and required fixture |

## Process cause
The common cause was **component-level implementation without an end-to-end consumer matrix**. A helper or button existing was treated as sufficient, while the user scenario crossed multiple surfaces: native Dashboard, Queue, legacy Downloads, SQLite state, filesystem state and persistent jobs. Native PySide6 execution was also not available in the Linux validation environment, which makes screenshot-derived acceptance tests and a Windows validation gate mandatory.

## Prevention rule added for this phase
For cross-cutting UI/state changes, validate the matrix:

`User action -> native/web entry point -> shared service -> persistent state/filesystem -> every count/list consumer -> rendered UI state`

A feature is not release-complete if a mandatory native Windows UI result is skipped or unverified.


## v6 re-audit findings closed in Phase 02 (v7)
A second consumer-matrix audit found additional gaps that v6 itself still missed:

- **Refresh All Figures was queued behind the paused download queue.** It now runs as an independent background task.
- **Legacy Downloads and backend job-start did not share the full queue-aware duplicate guard.** The canonical backend check now merges physical library/deletion history with current/recent queue identity, and `/api/job-start` enforces confirmation.
- **Successful Retry could silently download again.** Backend plus native and legacy Retry paths now require explicit confirmation.
- **Stats refresh could lose a terminal update while another read was running.** Pending and in-flight targets now prevent premature acknowledgement.
- **Completed Today counted generic successful jobs.** It now counts physically present videos with canonical `downloaded_at` today.
- **Full Library did not consistently persist `downloaded_at`.** Successful media materialization now writes it.
- **Queued reason was generic and Queue page data was capped to 60 jobs.** Reason is position/state aware and dedicated Queue requests the unlimited session snapshot.

These misses reinforce the prevention rule above: tests must assert equality/behavior at every consumer, not only the helper/service that was added.
