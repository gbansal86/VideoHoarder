# Files Changed

| File / Area | Change Type | Reason |
|---|---|---|
| `app/library_pagination.py` | Modified/Added | Canonical SQLite paged Library service with real totals and TEMP-table search ranking. |
| `app/ai_cache_identity.py` | Modified/Added | Native Library fetches only the requested page. |
| `app/native_library_page.py` | Modified/Added | Embedding manifest/rows include backend/model/dimension identity fingerprint and reject legacy/mismatched reuse. |
| `app/app.py` | Modified/Added | Answer cache key includes evidence content plus prompt/model/mode/temperature/context/evidence-limit identity. |
| `tests/test_phase5_scale_ai_contract.py` | Modified/Added | Answer cache key includes evidence content plus prompt/model/mode/temperature/context/evidence-limit identity. |
