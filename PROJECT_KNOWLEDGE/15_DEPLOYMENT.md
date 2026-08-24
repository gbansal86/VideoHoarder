# Deployment

Recorded: 2026-08-15

`BUILD_WINDOWS.ps1` uses an isolated `.videohoarder-build` environment, installs `requirements-build.txt`, compiles source, runs unittest discovery, generates the icon, invokes PyInstaller with `VideoHoarder.spec`, and creates `dist/VideoHoarder-v33.0-Windows.zip`. `INSTALL_GUI.ps1` handles installation. Runtime dependency is PySide6; build dependencies include PyInstaller and Pillow.

Historical build logs show Python 3.12, PySide6 6.11.1, PyInstaller 6.22.0, Pillow 12.3.0, a missing QML asset-downloader plugin warning, and successful packaging. The local and installed v33 EXEs match SHA-256 and size.

Status: build process IMPLEMENTED; historical release VERIFIED; current Git HEAD NOT REBUILT. Build/dist, environment, ZIP, logs, and installed binary are intentionally excluded from Git. A reproducible release should build from a recorded clean commit and record tool versions, tests, output hash, installation, and runtime checks.

## Available runtime input - 2026-08-24

- Application version: `33.0-GUI`.
- One-folder executable: `dist/VideoHoarder/VideoHoarder.exe`, modified 2026-08-12.
- Large standalone/local executable: `dist/VideoHoarder.exe`, 218,124,389 bytes, modified 2026-08-13.
- Distribution archive: `dist/VideoHoarder-v33.0-Windows.zip`, 216,762,125 bytes, modified 2026-08-13.
- Runtime check: the one-folder executable started and its `/api/progress` endpoint returned HTTP 200 on 2026-08-24.
- Environment observed: Windows NT 10.0.26200.0, AMD64; source Python 3.12.10.
- Launch from source: install once with `INSTALL_GUI.ps1`, then use `run_gui.pyw` as documented. `DESKTOP_README.md` also mentions `START_GUI.vbs`, but that file is not present in the repository inventory and therefore needs review.
- Logs: source documentation identifies `logs/gui.log`; build logs are `build-output.log` and `build-error.log`.

The available binaries remain historical v33 artifacts. No clean rebuild was performed, so they must not be labeled as produced from the current Git HEAD.
