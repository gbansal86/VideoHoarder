# Contributing to VideoHoarder

Thanks for helping improve VideoHoarder. The project favors focused, reviewable changes that preserve existing libraries and user control.

## Before changing code

1. Read `README.md`, `SECURITY.md`, `PROJECT_KNOWLEDGE/README.md`, and the relevant current spec under `specs/current/`.
2. Search for an existing service/module before adding a parallel implementation.
3. Trace the complete path: UI/route → orchestration → service → persistence/files → output/recovery.
4. For migrations or filesystem changes, define rollback/idempotency behavior before implementation.

## Architecture rules

- Prefer **reuse → expose → complete → repair → refactor → new implementation**.
- Do not add new feature logic to `app.py` when a focused service module is practical.
- Keep acquisition and deterministic transcript processing independent of external AI providers.
- Keep one authoritative transcript/evidence model.
- External model output is a proposal until it passes deterministic validation and user review.
- Never add a second source of truth for metadata, package state, or completion state without an explicit migration plan.

## Development setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-build.txt
```

## Required checks

```powershell
python -m compileall -q app tests build_support
python -m pytest -q
```

For an OpenAI-provider change, also run:

```powershell
python -m pytest -q tests/test_openai_api_service.py tests/test_openai_app_integration.py
```

Provider tests must not require a real API key or network request.

## Pull requests

Include:

- problem/current behavior;
- proposed behavior;
- affected files/data/schema;
- regression/security/privacy risks;
- tests run and results;
- migration/rollback notes when applicable.

Keep generated runtime data, downloads, database files, secrets, ZIPs, test output, and local browser profiles out of commits.
