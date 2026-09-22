# Phase 06 Test Plan

1. `python -m compileall -q app tests`.
2. Run focused Phase 0–5 contract suites together.
3. Run the complete `python -m pytest -q tests` suite.
4. Run pytest with skip reasons and verify all skips are native PySide6 runtime tests unavailable on this Linux host.
5. Generate two clean Code Parent archives from unchanged source and verify identical approved file sets/content SHA256 maps.
6. Audit implementation markers, phase evidence, feature inventory, change index, traceability and progress records.
7. Run the complete pytest suite again after all implementation/governance reconciliation.
8. Do not mark Windows PyInstaller/native GUI acceptance passed; record it as NOT EXECUTED with exact reason.
