# Files Changed

| File | Change Type | Requirement | Reason |
|---|---|---|---|
| app/download_guard_service.py | Added | REQ-602 | Central duplicate/re-download logic outside app.py |
| app/library_stats_service.py | Added | FIX-607 | Physical-media availability rules |
| app/native_queue_page.py | Added | REQ-604, ARCH-605, FIX-606 | Dedicated full Queue screen |
| app/native_ui.py | Modified | FIX-601, REQ-602, FIX-603, REQ-604, FIX-606 | Layout, duplicate confirmation, scrolling, refresh behavior |
| app/gui.py | Modified | ARCH-605 | Route Queue to dedicated page |
| app/app.py | Modified/refactored | REQ-602, FIX-607 | Thin service imports/wrappers; physical count |
| tests/test_issue6_completion.py | Added | all | Deterministic Issue-6 tests |
| tests/test_native_ui.py | Modified | UI requirements | Windows/PySide runtime checks |
| tests/fixtures/chatgpt_integrity/... | Restored | FIX-609 | Fix packaged build-test fixture |
| docs/implementation/* | Added | DOC-608 | Persistent governance evidence |
