# Test Plan

1. Compile `app`, scripts, and launcher.
2. Reproduce F21 with downloader rc=0 and no output; expect failure.
3. Compare Media Only invocation with SRT off/on; expect distinct final argument.
4. Persist a RUNNING job, reload state, and verify `INTERRUPTED` + retry task.
5. Static/native contract checks for canonical progress, background Library reads, Queue-first attachment, frozen Queue acceptance, and Code Parent wrapper output.
6. Run full pytest suite.
7. Generate a fresh Code Parent, extract it, and run package/integrity/current-review regression tests from the extracted package.
8. Windows build must execute strengthened clean-room self-test before release is marked complete.
