# Test Plan — Phase 02

## Automated
1. Unit-test physical Completed Today metric.
2. Unit-test precise queue wait reasons.
3. Verify unlimited queue snapshot returns >60 jobs.
4. Verify canonical duplicate report detects a video that is only queued, not yet in the library.
5. Verify successful Retry is blocked without explicit re-download confirmation.
6. Source-contract test that Refresh All Figures does not call `web_start_job`.
7. Source-contract test pending/in-flight stats-refresh coordination.
8. Source-contract test canonical `downloaded_at` persistence and server-side duplicate gate.
9. Run complete unittest discovery.
10. Run compileall for app and tests.

## Windows/native acceptance still required
- Pause queue → click Refresh all figures → counts update without Resume.
- Download a new video → Library and Completed Today update promptly.
- Delete physical media → Refresh all figures decreases Library count.
- Use legacy Downloads on a queued/existing URL → one confirmation, no silent duplicate.
- Select a successful job → Download again asks confirmation.
- Queue with no running worker shows "waiting for worker to start" for first queued item and position-aware reason for later items.
- Queue page with >60 session jobs scrolls through all rows.
