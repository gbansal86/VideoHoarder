# Code Changes

- Added frozen DownloadOptions captured at submission.
- Added JobContext with per-job cancel/process ownership.
- Changed Full Download result accounting so unresolved/empty inputs fail truthfully.
- Separated current-transfer progress from batch completion progress.
