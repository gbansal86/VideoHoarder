# Test Plan

1. Re-run exact equal-size/different-content legacy migration and staging collisions.
2. Verify Windows reserved basenames are escaped.
3. Verify invalid configuration is quarantined and privacy-safe defaults are restored.
4. Verify frozen dependency setup never calls pip through the frozen executable.
5. Verify correct/wrong SHA-256 tool payload behavior.
6. Verify Settings map to immutable per-job options.
7. Verify modern YouTube URL forms, including `/live/` and explicit watch+list policy.
8. Verify canonical batch URLs remain intact while managed workers receive isolated URL files.
9. Verify Code Parent creation is byte-reproducible and validates its embedded manifest.
10. Run compileall and the complete pytest suite.
11. Generate the final Code Parent twice, extract the retained archive, and rerun the complete suite from the extracted source.
