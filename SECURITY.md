# Security policy

VideoHoarder handles local media, filesystem mutations, SQLite state, subprocesses, browser/source authentication, and optional external AI processing. Security reports are taken seriously.

## Supported version

Security fixes target the current `main` branch and latest release unless a maintainer explicitly states otherwise.

## Reporting a vulnerability

Prefer GitHub's private vulnerability reporting / Security Advisory mechanism when available. Do not post API keys, cookies, OAuth tokens, private video information, private paths, exploit payloads, or personal library data in a public issue.

## Security boundaries

For the project-level assets, trust boundaries, attacker assumptions, and review checklist, see [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

### Local server

The desktop helper/server is expected to bind to loopback (`127.0.0.1`). Mutation endpoints use local request authorization. Changes that expose it to non-loopback interfaces require a separate threat review.

### Filesystem

Discovery/reporting should be read-only where possible. Destructive changes must use explicit user actions and safe-path checks. Code handling paths/ZIPs/packages must defend against traversal and unintended writes outside the configured library/exchange areas.

### Credentials

- Never commit keys, tokens, cookies, `.env` files, browser profiles, or credential exports.
- The OpenAI API key is read from an environment variable and is not stored by VideoHoarder.
- Logs/audit/report files must contain only sanitized provider metadata, never credential values.

### External AI

The OpenAI API path is disabled by default and sends data only after an explicit user action. Normal packages are allow-list driven and one-video isolated. Restricted/private/unlisted videos are blocked by default. API output never bypasses the local importer/review gate.

### Public GitHub exchange

Publishing ChatGPT exchange packages to a public repository is a separate explicit feature. Do not conflate it with API submission. Review the package evidence before publishing it publicly.

## Dependency and release hygiene

Dependabot and CI should remain enabled. Release changes should pass compile/tests, document known security/privacy changes, and avoid bundling secrets or runtime library data.

## Automated dependency auditing

The repository runs a scheduled and requirements-change dependency audit with PyPA `pip-audit`. The job emits both a machine-readable vulnerability report and a CycloneDX JSON SBOM as temporary GitHub Actions artifacts. A known vulnerability or dependency-resolution failure makes the audit job fail rather than silently publishing a clean-looking report.

The SBOM is evidence for a specific CI run; it does not replace reviewing dependency changes, Dependabot alerts, or release notes.
