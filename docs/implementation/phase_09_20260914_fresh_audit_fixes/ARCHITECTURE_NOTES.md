# Architecture Notes

## ADR-P09-01 — Content equality is required before destructive dedupe
File length is only a pre-check. Destructive duplicate handling requires SHA-256 equality. Different content is retained.

## ADR-P09-02 — Installed CODE_ROOT is read-only
All mutable runtime/user state belongs under the resolved writable `BASE` or explicit user override. The frozen executable directory may contain read-only resources only.

## ADR-P09-03 — One YouTube parser
URL syntax knowledge lives in `app/youtube_url.py`; feature modules consume the parser rather than maintain regex variants.

## ADR-P09-04 — Release dependencies are build-time dependencies
A frozen GUI executable is not a Python interpreter. Python packages needed at runtime are bundled by the release build; source-mode local pip installation remains a development fallback only.

## ADR-P09-05 — Integrity-gated executable downloads
Remote executable/ZIP tool payloads are executable code and require a configured SHA-256 unless the user explicitly opts into an unverified workflow.

## ADR-P09-06 — Job inputs are immutable
The user's canonical `urls.txt` batch is not process-wide scratch state. Queue workers receive separate per-job URL input files.
