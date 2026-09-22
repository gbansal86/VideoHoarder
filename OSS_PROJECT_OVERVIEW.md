# VideoHoarder OSS project overview

VideoHoarder is an actively developed local-first video-library and transcript-intelligence application. Its maintenance surface spans a native desktop UI, local HTTP endpoints, SQLite migrations, filesystem operations, download/subtitle tooling, deterministic transcript quality/repair, AI package contracts, external-provider adapters, result validation, and Windows release packaging.

## Why ongoing maintenance is non-trivial

A change can cross UI, queued jobs, persistent state, source files, transcript evidence, report generation, and recovery behavior. The test suite therefore includes architecture contracts and regression tests in addition to ordinary feature tests.

## AI/provider philosophy

External AI is downstream of deterministic evidence. Provider availability must never determine whether the local library can be opened, downloaded, repaired, or inspected. Provider results are untrusted structured proposals until validated against the exact package contract and reviewed.

## Maintainer automation opportunities

The repository is well suited to automated support for:

- issue classification and reproduction-plan drafting;
- identifying affected modules/tests for a proposed change;
- PR diff summaries and regression-risk review;
- generation of focused regression tests;
- security review of local HTTP/filesystem/provider boundaries;
- release checklist/evidence verification;
- documentation/traceability checks during incremental modularization.

Human maintainers remain responsible for merge/release decisions and user-impacting actions.
