# Security Findings

1. HIGH: plaintext installed API-key file exists; do not include it in Git or handoffs.
2. HIGH: browser profile/cache trees may contain session-sensitive state and should not be retained with source.
3. MEDIUM: powerful local HTTP endpoints need explicit loopback, CSRF, input/path, and command-dispatch review.
4. MEDIUM: absent Git history weakens supply-chain traceability and change auditability.
5. MEDIUM: silent exception handling can suppress validation/security failures.

No secret values are reproduced in this package.
