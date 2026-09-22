# Architecture

Recorded: 2026-08-15

## Runtime topology

`run_gui.pyw` starts the PySide6 shell in `app/gui.py`. The shell hosts native pages and an embedded web view pointed at a loopback `ThreadingHTTPServer` implemented in `app/app.py`. The backend uses SQLite plus filesystem artifacts and invokes local executables, YouTube/transcript services, Selenium/browser workflows, and local Ollama. ChatGPT exchange is file-based and manual.

## State and persistence

- SQLite: videos, ChatGPT requests/video membership/feature coverage/field history, transcript availability, artifact manifest JSON, external media, subscriptions, and clip projects.
- Filesystem: video folders, transcripts, reports, maintenance records, indexes/embeddings, exchange packages/results/reviews/exports, collections, and recovery artifacts.
- In-memory process state: jobs, queue, progress, stop/pause controls, processes, drivers, and dashboard state.

## Safety boundaries

- ChatGPT never uploads automatically.
- Imports are validated and stored as review proposals.
- Duplicate and clip-plan actions remain non-physical at review time.
- Destructive purge and organization tools exist separately and require explicit operation.

## Architectural findings

`app/app.py` combines persistence, filesystem mutation, external calls, HTTP routing, HTML/JavaScript, jobs, AI, reports, recovery, and CLI menus. This centralization creates regression, observability, test-isolation, and ownership risk. Decomposition should follow characterization tests and preserve current interfaces.

The repository has no formal migration package, API framework, dependency injection, or separated prompt registry. These are maintainability findings, not authorization to rewrite the application.
