# Phase 0 Test Plan

1. Compile source/tests/scripts.
2. Run package-specific tests for inclusion/exclusion/sanitization/manifest hashes.
3. Generate an actual Code Parent and validate its embedded manifest.
4. Run the complete pytest suite cumulatively.
5. Inspect BUILD_WINDOWS.ps1 contract to prove pytest is the build gate while launcher build behavior remains unchanged in Phase 0.
6. Re-audit governance files for Phase 03/04 and current baseline references.
