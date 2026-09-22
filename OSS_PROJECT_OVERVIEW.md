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


## Current maintenance evidence

As of 2026-09-22, the public repository demonstrates an active maintainer workflow rather than a source dump:

- changes are developed and reviewed through pull requests before merging to `main`;
- Windows and Linux CI validate privacy, compilation, provider/package contracts, and the full regression suite;
- CodeQL runs on repository changes;
- Dependency Security runs `pip-audit` and publishes a CycloneDX SBOM as CI evidence;
- the Windows build pipeline produces a frozen executable from clean public source, runs a clean-room self-test, records SHA-256/build metadata, and uploads a temporary CI artifact;
- release-version consistency and build-provenance contracts are regression-tested;
- public documentation links and annotated newcomer images are regression-tested;
- Dependabot is configured for dependency maintenance;
- the repository has security, contribution, governance, support, release, roadmap, CODEOWNERS, issue-template, and PR-template policies;
- roadmap issues track Windows release acceptance, incremental modularization, offline local speech-to-text, repository-admin hardening, and historical Git cleanup.

Representative merged maintenance PRs include the sanitized OSS publication, Windows build automation, CODEOWNERS, release/security hardening, threat-model/community onboarding, build provenance, and documentation-integrity checks.

## Security and release posture

The current public `main` tree excludes runtime databases, live configuration, cookies/tokens, generated exchange packages/results, downloaded media, real transcripts, and private browser/session state. A public-source audit is part of CI.

AI/provider functionality is optional. OpenAI submission is disabled by default, credentials are supplied by each user outside the repository, and provider results remain behind deterministic validation and human review.

## Adoption status

VideoHoarder is newly published as a conventional OSS source repository. External stars, forks, download counts, outside issues, and third-party contributions are therefore still limited and should not be overstated.

The project's current case for maintainer tooling is based on technical depth, active maintenance responsibilities, security/release complexity, and the demonstrated review/test/release workflow. Broader ecosystem adoption remains an area to grow through real users rather than manufactured repository activity.
