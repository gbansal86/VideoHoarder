# Files Changed

| File / Area | Change Type | Reason |
|---|---|---|
| `scripts/create_code_parent_package.py` | Modified/Added | Code Parent generator explicitly includes docs/implementation and excludes runtime/live configuration. |
| `BUILD_WINDOWS.ps1` | Modified/Added | Archive manifest records content SHA256 hashes and validates its own archive. |
| `tests/test_code_parent_package.py` | Modified/Added | Windows release gate invokes the full pytest test directory. |
| `docs/implementation/*` | Modified/Added | Windows release gate invokes the full pytest test directory. |
