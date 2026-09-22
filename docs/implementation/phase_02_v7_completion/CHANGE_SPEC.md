# Change Specification — Phase 02 v7 completion

## Change size
MEDIUM. This closes cross-cutting queue, duplicate-download, dashboard-stat, retry, and governance gaps discovered by the v6 re-audit.

## Requirements
- **FIX-701** Refresh All Figures must execute even when the managed download queue is paused/busy.
- **REQ-702** One duplicate/re-download guard must protect native downloads, legacy Downloads, server job-start, and successful Retry.
- **FIX-703** Terminal-job stats refresh must not lose an update when a prior stats read is still running.
- **FIX-704** Completed Today must count physically present videos downloaded today, not arbitrary successful maintenance jobs.
- **FIX-705** Full Library processing must persist `downloaded_at` so the metric and downloaded-date sorting have canonical data.
- **FIX-706** Queued-job explanation must distinguish paused, active-running-job, earlier-queued-job, and worker-start states.
- **FIX-707** Dedicated Queue page must be able to show all in-memory session jobs rather than the former 60-item snapshot cap.
- **DOC-708** Governance feature inventory/evidence must reflect actual code state and stop overclaiming incomplete duplicate protection.

## Current behavior / root cause
v6 had good component-level fixes but several consumers still diverged: figure refresh was incorrectly submitted to the queue it needed to diagnose; legacy Downloads used only library/deletion history and not queue state; the stats-refresh timestamp could be advanced before a pending fresh read completed; Completed Today was derived from generic successful jobs; and Queue page data came from a snapshot capped to 60 rows.

## Required behavior
All download surfaces use the canonical duplicate guard; successful re-download requires explicit confirmation; dashboard metrics come from physical/canonical video state; figure refresh is independent of queue pause; pending stats refreshes are never dropped; queue wait messages describe actual state/position; Queue page requests the unlimited in-memory snapshot; documentation matches evidence.
