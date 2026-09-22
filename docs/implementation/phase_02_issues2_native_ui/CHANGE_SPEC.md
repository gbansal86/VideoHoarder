# Phase 02 Change Specification — Issues 2 Native UI

Change size: MEDIUM

## Requirements

- REQ-011: Library rows show thumbnails and can open/play the local video when the user clicks the video title/row.
- REQ-012: Library defaults to 100 videos per page and lets the user choose page size.
- REQ-013: Dashboard Needs attention count and Failure/Cleanup list use the same current unresolved failure source.
- REQ-014: Failure/Cleanup presents a direct per-row Delete action that clears current failure state/log rows without deleting media.
- REQ-015: More → New download → Open downloader visibly opens the complete downloader and shows all normal options.
- REQ-016: Download workflow and video quality are separate controls. Workflow choices: Full Library, Media Only, Audio Only.
- REQ-017: Queue visibly retains separate Name and Type columns, with the filename/title and thumbnail in Name.
- ARCH-002: New Library and Failure/Cleanup UI features live in separate modules rather than app.py.

## Baseline

Latest prior source: `VideoHoarder_Code_Parent_Fixed_Modular_v3_AutoDeploy.zip`.

Baseline test evidence: `Ran 77 tests ... OK (skipped=6)` using `python -m unittest discover -s tests -v`.

`app/app.py` baseline line count: 28,850.

## Design

- Create native `NativeLibraryPage` and `NativeFailurePage` modules.
- Route normal Library and Failure/Cleanup navigation to these native pages; retain legacy web routes for compatibility/direct URLs.
- Reuse `web_library_rows`, `web_download_failure_rows`, `clear_selected_failure_entries`, and `/video-view/<VIDEO_ID>` rather than duplicate backend logic.
- Extend the library browser service output with the live media path/source thumbnail fields required by the native presentation.
- Keep queue/download fixes in native presentation code and reuse existing managed job/download backend.

## Risks

- PySide6 runtime cannot be executed in the current Linux validation environment; Windows native UI behavior is therefore compile/static-tested here and must be executed on the Windows build host.
- Thumbnail URLs may be unavailable for non-YouTube sources; the native page falls back to a placeholder.
- Client-side pagination currently fetches up to 10,000 filtered rows from the existing backend in one request.

## Acceptance criteria

- Library defaults to 100/page and supports 25/50/100/200/500.
- Click/double-click a downloaded Library video opens `/video-view/<VIDEO_ID>` in the embedded player.
- Failure count is refreshed from `web_download_failure_rows()` and the native failure page uses the same rows.
- Each current failure with a VIDEO_ID has a Delete button.
- Workflow and quality are separate controls; Audio Only disables irrelevant video-quality selection.
- Queue Name column is initialized wide enough to remain visible beside Type.
- Existing test suite remains green; new tests cover service/output contracts and native widget contracts where PySide6 is available.
