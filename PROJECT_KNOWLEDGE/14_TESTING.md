# Testing

Audit run: `py -3 -m py_compile ...` passed. `py -3 -m unittest discover -s tests -p 'test_*.py' -v` discovered 14 tests: 11 passed and 3 skipped because PySide6 is absent from system Python.

Covered: config/root override, dashboard startup, canonical health-file preservation, ChatGPT integrity/provenance/timestamps/planner rules, duplicate review, clip handoff, and native navigation declarations when PySide6 is available.

Missing: populated DB integration, migrations, real filesystem reconciliation, downloads, transcript providers, report generation, HTTP authorization/path validation, concurrency/cancellation, recovery/interruption, central manifest, installed GUI, package apply, large-library performance, and destructive-operation safety fixtures.
