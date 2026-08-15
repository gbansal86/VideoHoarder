# Deployment

Recorded: 2026-08-15

`BUILD_WINDOWS.ps1` uses an isolated `.videohoarder-build` environment, installs `requirements-build.txt`, compiles source, runs unittest discovery, generates the icon, invokes PyInstaller with `VideoHoarder.spec`, and creates `dist/VideoHoarder-v33.0-Windows.zip`. `INSTALL_GUI.ps1` handles installation. Runtime dependency is PySide6; build dependencies include PyInstaller and Pillow.

Historical build logs show Python 3.12, PySide6 6.11.1, PyInstaller 6.22.0, Pillow 12.3.0, a missing QML asset-downloader plugin warning, and successful packaging. The local and installed v33 EXEs match SHA-256 and size.

Status: build process IMPLEMENTED; historical release VERIFIED; current Git HEAD NOT REBUILT. Build/dist, environment, ZIP, logs, and installed binary are intentionally excluded from Git. A reproducible release should build from a recorded clean commit and record tool versions, tests, output hash, installation, and runtime checks.
