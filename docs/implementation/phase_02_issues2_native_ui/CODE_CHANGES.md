# Code Changes

## Native Library

Added `app/native_library_page.py` with:
- default 100-row page size;
- selectable 25/50/100/200/500 rows per page;
- thumbnail + clickable title in the Video column;
- query/filter/sort controls;
- Previous/Next pagination;
- click-to-play through the existing local `/video-view/<VIDEO_ID>` route.

## Native Failure/Cleanup

Added `app/native_failure_page.py` with:
- one authoritative current-failure list from `web_download_failure_rows()`;
- per-row Delete action;
- confirmation that media is not deleted;
- refresh/count signal after cleanup.

## Downloader

Updated `DownloadComposer` so workflow and quality are separate:
- Full Library
- Media Only
- Audio Only

Quality remains separately selectable for video workflows. Opening the downloader from More expands Advanced options.

## Queue

The queue remains six columns: Name, Type, Progress, Status, Speed, ETA. Name is now initialized at 340 px rather than a stretch section that could collapse to zero width when the details panel is present. Name continues to use the existing thumbnail/title widget.

## Failure count

Dashboard failure count refreshes from `web_download_failure_rows()` every 5 seconds and is also updated immediately by the native failure page after deletion. Historical failed job logs are not used for this metric.
