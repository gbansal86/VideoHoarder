# Files Changed

| File / Area | Change Type | Reason |
|---|---|---|
| `app/settings_service.py` | Modified/Added | Atomic settings validation/persistence. |
| `app/local_api_security.py` | Modified/Added | Per-run localhost mutation token plus loopback Host/Origin/client validation. |
| `app/http_range.py` | Modified/Added | Strict bounded JSON object parsing. |
| `app/metadata_migration.py` | Modified/Added | Correct single/suffix byte-range parsing. |
| `app/app.py` | Modified/Added | Per-video SQLite SAVEPOINT migration atomicity. |
| `tests/test_phase2_safety_contract.py` | Modified/Added | Per-video SQLite SAVEPOINT migration atomicity. |
