# Testing

VideoHoarder uses regression tests as part of the architecture contract because changes can cross UI, queued jobs, SQLite state, filesystem operations, transcript evidence, semantic packages, and recovery paths.

## Full source validation

```powershell
python -m compileall -q app tests build_support
python -m pytest -q
```

## OpenAI provider validation

```powershell
python -m pytest -q tests/test_openai_api_service.py tests/test_openai_app_integration.py
```

These tests use a fake `openai` module/client. They verify isolation, privacy, fallback, audit, settings, and review behavior without network/API charges.

## Platform notes

The primary release target is Windows. The full suite should run on Windows CI. A smaller Linux contract job catches import, provider, package and safety regressions. Tests that assert Windows-only path semantics should be explicitly marked Windows-only rather than weakening production behavior.

## Release evidence

Before a release, record:

- source version/commit;
- compile result;
- test counts;
- Windows build result;
- archive/executable hashes;
- startup smoke check;
- known warnings/skips;
- any provider/security/privacy changes.

## Local-video import (v33.2)

Run `python -m pytest -q tests/test_local_video_import.py` to verify path discovery, read-only scan, reference/copy/confirmed move, idempotency, subtitle parsing and the no-YouTube/no-AI boundary. For Windows manual QA, use a temporary folder of synthetic videos and subtitles; never use irreplaceable originals for the move test.
