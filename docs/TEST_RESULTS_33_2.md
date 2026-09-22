# VideoHoarder 33.2 regression report

Executed on Linux using the sanitized public-source working tree.

- `python -m py_compile app/app.py app/gui.py app/native_ui.py app/local_video_import.py`: PASS.
- `python -m pytest -q tests/test_local_video_import.py`: 9 passed.
- `python -m pytest -q --disable-warnings`: **354 passed, 22 skipped, 0 failed**, 9.41s.
- Provider calls were not made; existing provider tests use a fake client. Existing Windows-specific tests remain skipped on Linux.
- Public privacy preflight and extracted ZIP verification are separate release checks; see the final packaging audit.
