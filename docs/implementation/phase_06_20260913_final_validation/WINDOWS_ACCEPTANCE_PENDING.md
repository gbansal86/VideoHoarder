# Windows acceptance still required

The Linux validation host does not have the PySide6 GUI runtime and cannot truthfully execute the PowerShell/PyInstaller release build. The final suite has 21 skips: 19 in `tests/test_native_ui.py` and 2 in `tests/test_phase3_native_ui_contract.py`, all explicitly skipped for missing PySide6/native runtime.

Before calling the release fully complete on Windows, execute `BUILD_WINDOWS.ps1`. Its contract now requires the complete pytest suite, an unskipped native-PySide subset, the real `VideoHoarder.spec` build, and an EXE-only clean-room `--release-self-test` without adjacent `Source` or `.videohoarder-build`. Also perform the documented visual/click-through checks for New Download defaults, per-job Cancel vs Stop all, shell notifications, Library paging, Queue/Job Details layout, duplicate confirmation, and refresh figures.
