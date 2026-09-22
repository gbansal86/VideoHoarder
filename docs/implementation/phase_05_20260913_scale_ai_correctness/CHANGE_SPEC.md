# Phase 05 — Library scale and AI cache correctness

Findings: F08, F10, F11.

Implemented one canonical SQLite/server-side Library pagination service with real totals and no 10,000-row client snapshot; the native Library and `/api/library-page` now use the same paged contract. Phase-6 embedding caches now persist and validate a backend/model/dimension/implementation fingerprint, and legacy/mismatched vectors are rebuilt rather than reused. Ask Local AI answer-cache identity now includes normalized evidence content plus prompt/model/mode/temperature/context/evidence-limit generation identity, so transcript/evidence corrections cannot reuse stale answers under unchanged chunk IDs.
