# Code Changes

- A downloader exit code of zero is no longer enough for Media Only success; a non-empty output file is mandatory.
- Media/Audio Only receives `save_srt`; subtitle fetch is performed when VTT or SRT is requested, and SRT is generated locally from VTT.
- Queue snapshots are atomically persisted to `data/database/job_queue_state.json`; active prior jobs restore as `INTERRUPTED` and can be explicitly retried when a safe task descriptor exists.
- Dashboard bottom progress delegates to `overall_progress_percent` just like Queue rows.
- Native Library query work leaves the GUI thread.
- Queue attaches before other pages; one page failure no longer prevents Queue attachment.
- Release self-test now proves local HTTP readiness, a visible/cancellable Queue job, and restart recovery in the packaged EXE.
