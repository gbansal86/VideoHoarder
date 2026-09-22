# Files Changed

| File | Change | Requirement |
|---|---|---|
| `app/app.py` | Media correctness, SRT forwarding target, durable queue integration | FIX-071/072, ARCH-073 |
| `app/media_only_service.py` | New output/SRT helpers | FIX-071/072 |
| `app/job_persistence_service.py` | New durable queue-state helpers | ARCH-073 |
| `app/download_workflows.py` | Forward `save_srt` to media workflow | FIX-072 |
| `app/native_ui.py` | Canonical bottom progress; interrupted resume control | FIX-075, ARCH-073 |
| `app/native_library_page.py` | Background Library fetch | PERF-076 |
| `app/gui.py` | Queue-first isolated backend attachment | FIX-077 |
| `run_gui.pyw` | Packaged backend/Queue/recovery acceptance | TEST-074 |
| `BUILD_WINDOWS.ps1` | Require strengthened clean-room evidence | TEST-074 |
| `CREATE_CODE_PARENT_PACKAGE.bat` | Correct remaining artifact message | FIX-078 |
| `tests/test_current_review_completion.py` | Regression coverage | all |
