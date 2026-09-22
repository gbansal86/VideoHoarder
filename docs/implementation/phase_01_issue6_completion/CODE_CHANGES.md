# Code Changes

## REQ-602 Duplicate guard
Before: active videos could be reported by `redownload_history_check`, but `requires_confirmation` was true only for PREVIOUSLY_DELETED, the native UI did not call the guard, and current queue duplicates were not checked.
After: one modular guard covers physical active-library duplicates, deleted history, current queue/recent jobs, and repeated pasted URLs; native and legacy web surfaces prompt before queueing again.

## ARCH-605 Queue page
Before: `show_page()` routed both `dashboard` and `queue` to the same CommandCenter.
After: `queue` routes to `NativeQueuePage`, while Dashboard keeps its compact overview.

## FIX-603/FIX-607 Counts
Before: Dashboard cached library stats for up to 45 seconds and `downloaded=1` could count even without physical media.
After: a newer terminal job triggers a stats refresh, and the Dashboard's available-download count verifies actual media presence.

## REQ-604/FIX-606 Queue usability
Before: no explicit Refresh queue, no guaranteed horizontal scrollbar, 12-row presentation cap, and paused queued jobs showed no explanatory reason.
After: full Queue page has all session rows, explicit both-axis scrolling, Refresh queue, and pause/wait explanations in rows/details.
