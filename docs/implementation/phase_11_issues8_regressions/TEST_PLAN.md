# Test Plan

1. Targeted Issues 8 regression tests.
2. Full cumulative pytest suite.
3. `compileall`.
4. Generate Code Parent twice and compare file sets/content hashes.
5. Extract retained package and rerun full pytest suite.
6. Windows-only: run native no-skip tests and both one-file and Small-EXE clean-room builds.
