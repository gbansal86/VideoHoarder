# File Inventory

Audit inventory: 7,240 files, approximately 1,471,084,668 bytes. This includes source, tests, SQLite/runtime data, build outputs, QA images/PDFs, and many browser-profile/cache artifacts.

Important groups: 25 Python files, 116 JSON files, 82 DB files, 1,360 PNG files, 1,006 QML files, 277 DLLs, and 212 logs. Source control should exclude build/dist outputs, runtime databases, downloads/media, logs, QA intermediates, browser profiles/caches, Python caches, secrets, and temporary test data unless a specific fixture is intentional.
