# Test Plan

1. Compile all changed Python modules.
2. Unit-test category sorting.
3. Unit-test unified failure aggregation: video + failed job, excluding cancelled job.
4. Unit-test exact deletion of CSV failure without VIDEO_ID.
5. Unit-test failed-job dismissal removes current job and archives run log.
6. Static/navigation test confirms Downloads sidebar route points to `/app?tab=downloads`.
7. Run complete unittest discovery.
8. Windows/PySide manual acceptance remains required for visual layout and actual clicks.
