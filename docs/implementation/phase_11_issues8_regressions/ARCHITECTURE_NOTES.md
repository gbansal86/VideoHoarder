# Architecture Notes

- Refresh/reconciliation is now managed queue work, so user-visible background operations share one job-control model.
- Physical library state is authoritative only for previously downloaded paths under the managed library root. Metadata-only or external paths are not destructively purged.
- Job progress remains split into batch progress and transfer progress; downloader output updates the managed job directly.
- Small-EXE is a packaging alternative only. The application architecture and feature set are unchanged; QtWebEngine/Chromium move to sidecar files rather than being embedded in one EXE.
