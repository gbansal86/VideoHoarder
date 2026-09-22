# Threat model

VideoHoarder is a local-first desktop application that processes media, transcript evidence, local databases, subprocesses, browser/source authentication state, and optional external AI requests. This document identifies the project's main trust boundaries and the security assumptions contributors should preserve.

## Assets to protect

- local video, subtitle, transcript, and report files;
- SQLite library state and migration integrity;
- API keys, cookies, OAuth tokens, browser profiles, and source credentials;
- user-selected filesystem paths;
- package/result provenance used by transcript intelligence;
- the local desktop application's loopback HTTP control surface;
- release artifacts and the public source repository.

## Trust boundaries

### 1. Local filesystem

User-selected files, imported folders, ZIP/package contents, filenames, symlinks, and metadata are untrusted input.

Expected protections:

- normalize and validate paths before reads/writes;
- reject path traversal outside allowed roots;
- do not overwrite unrelated files implicitly;
- keep discovery/read-only operations separate from destructive actions;
- require explicit confirmation before move/delete/apply operations;
- treat symlinks/reparse points carefully during cleanup and recursive scans.

### 2. Loopback HTTP server

The embedded HTTP service is intended for local desktop use and should remain bound to `127.0.0.1`.

Expected protections:

- never expose mutation routes on a non-loopback interface without a separate threat review;
- preserve local request authorization/anti-CSRF protections;
- validate every path, ID, and command argument received over HTTP;
- do not assume "localhost" means request content is trustworthy.

### 3. Subprocesses and external tools

VideoHoarder can invoke tools such as yt-dlp, FFmpeg/FFprobe, browsers, and build/runtime helpers.

Expected protections:

- use structured argument lists instead of shell-concatenated commands where practical;
- never insert untrusted metadata directly into a shell command;
- verify executable discovery/selection;
- capture and sanitize errors before persisting them;
- preserve timeouts/cancellation for long-running child processes.

### 4. Source/platform services

Remote metadata, subtitles, URLs, and availability information may change or contain malformed/unexpected content.

Expected protections:

- treat remote responses as untrusted data;
- keep source-specific logic isolated from local-video records;
- do not silently convert authentication/session state into public artifacts;
- preserve provenance so imported evidence can be traced to its source.

### 5. External AI providers

AI output is untrusted proposal data, not an authority.

Expected protections:

- external AI remains optional;
- API keys are not stored in project configuration;
- one-video isolation prevents cross-video evidence leakage;
- restricted/private/unlisted content is blocked from external submission by default;
- provider output must pass deterministic schema/provenance/timestamp/ID validation;
- no AI response may silently rename, move, delete, or apply library changes.

Prompt injection inside transcript text is treated as untrusted transcript content. It must not override package rules, safety gates, local validation, or maintainer instructions.

### 6. Public GitHub and exchange artifacts

A public repository is a permanent disclosure boundary.

Expected protections:

- never commit live config, databases, downloads, credentials, cookies, browser profiles, real processing packages/results, or private transcripts;
- run the public-source audit before release/publication;
- keep generated `exchange/` evidence out of source control;
- review Git history separately from the current tree when sensitive historical artifacts existed.

### 7. Dependencies and release pipeline

Third-party packages, GitHub Actions, and build inputs are part of the software supply chain.

Expected protections:

- Dependabot remains enabled;
- CodeQL and CI remain green before merge;
- dependency auditing/SBOM evidence is generated;
- release version fields must remain synchronized;
- Windows release artifacts are built from clean public source and pass the frozen clean-room self-test;
- release asset hashes are recorded.

## Threats explicitly considered

- path traversal and unintended writes;
- malicious archive/package paths;
- command/subprocess argument injection;
- secret leakage through logs, reports, packages, CI, or Git history;
- accidental upload of private/restricted media evidence;
- localhost request abuse;
- prompt injection or malformed AI output;
- corrupted/stale migrations or partial job recovery;
- dependency compromise or known vulnerable packages;
- release/version drift;
- destructive actions triggered without clear user intent.

## Out of scope / non-goals

- protecting a machine already fully compromised by an administrator-level attacker;
- bypassing DRM, access controls, paywalls, private memberships, or source-platform authorization;
- guaranteeing that third-party services retain or process data beyond their published terms;
- treating AI-generated semantic output as ground truth.

## Security review checklist for changes

A change touching files, HTTP routes, subprocesses, authentication, AI providers, migrations, packaging, or release automation should answer:

1. What untrusted input crosses a trust boundary?
2. Which paths/files/state can it read or modify?
3. Can it expose a secret or private transcript?
4. Can malformed input escape an allowed directory or command argument?
5. Can retry/restart duplicate or partially apply the action?
6. Can AI/provider output bypass deterministic validation?
7. Is rollback/idempotency behavior defined?
8. Are regression tests present for the security boundary?

See [SECURITY.md](../SECURITY.md) for vulnerability reporting.
