# Phase 02 Test Plan

- Invalid workers/type values leave in-memory and disk configuration unchanged.
- Simulated disk failure leaves in-memory settings unchanged.
- Valid settings persist atomically.
- Local mutation token, Host, Origin, and loopback boundary checks.
- Foreign origin is rejected before mutation dispatch.
- Malformed/non-object JSON is rejected without action dispatch.
- N-M, N-, -N, oversized end and invalid/multiple ranges.
- Fault injection after migration writes rolls back every video field, then stores FAILED outside the savepoint.
- Retrying a failed migration succeeds from clean pre-failure data.
- Full cumulative pytest suite.
