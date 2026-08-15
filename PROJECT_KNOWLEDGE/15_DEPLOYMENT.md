# Deployment

`BUILD_WINDOWS.ps1` creates/uses an isolated environment, installs build dependencies, compiles source, runs tests, generates the icon, builds a PyInstaller windowed executable, and creates `VideoHoarder-v33.0-Windows.zip`.

Build log reports PySide6 6.11.1, PyInstaller 6.22.0, Pillow 12.3.0, and Python 3.12 paths. A missing QML plugin warning occurred, but packaging completed. Installed and local EXE hashes match.

No rebuild or installation was performed during this audit.
