# Architecture Decisions

## AD-001: Preserve existing systems

Decision: extend the existing SQLite manifest and package/history systems rather than adding competing stores.

## AD-002: Evidence before status

Decision: code presence is IMPLEMENTED IN SOURCE; only successful relevant tests or observed behavior is VERIFIED.

## AD-003: No Git mutation during audit

Decision: Git initialization/commit/push requires explicit owner approval.

## AD-004: Characterization before decomposition

Recommendation: add behavior-preserving tests before splitting the monolithic backend.
