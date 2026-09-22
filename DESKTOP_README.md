# VideoHoarder Desktop v33.2

VideoHoarder now opens in a native PySide6 command centre with a focused
download composer, live queue, job inspector, seven-item navigation, eight
guided workflows, and simplified settings. Specialist library and knowledge
views remain embedded inside the application, so normal use does not open a
command prompt or a separate browser window.

## Run from source

1. Right-click `INSTALL_GUI.ps1` and choose **Run with PowerShell** once.
2. Afterwards, double-click `START_GUI.vbs` or `run_gui.pyw`.

The private `.videohoarder-gui` environment (created beside the release folder)
keeps PySide6 separate from other Python apps and avoids Windows path limits.

## Build the self-contained Windows app

Run `BUILD_WINDOWS.ps1`. The finished application is:

`dist\VideoHoarder.exe`

The release uses PyInstaller's windowed **one-file** mode. Python, PySide6, Qt,
and QtWebEngine/Chromium required by the full desktop build are bundled into
the executable; users do not need Python installed.

The build also creates `dist\VideoHoarder-v33.2-Windows.zip` for distribution.

By default `BUILD_WINDOWS.ps1` builds and validates the release but does **not** replace the live installed EXE. Run it with `-Deploy` (or use `BUILD_AND_DEPLOY.bat`) to back up the executable under the configured install root as `VideoHoarder_previous.exe`, deploy the new executable, and verify its SHA-256 hash. If the installed EXE is locked/running, deployment stops with a clear error instead of silently leaving an old executable in place.

## Data and privacy

- The UI server binds only to `127.0.0.1` (this computer).
- Config, logs, downloads, tools, and the SQLite library remain persistent in
  the portable application/library folder.
- Public web links open in the user's normal browser.
- `api_key.txt` is intentionally excluded from the packaged application. Add
  it beside the executable or use the existing library-root override.
- GUI/console output is written to `logs\gui.log` with rotation.

## Legacy diagnostic mode

The original `START.bat` and command-line menus are retained for troubleshooting.
They are not needed for normal desktop use.


## Why the standalone EXE is large

The full standalone build intentionally includes PySide6 and QtWebEngine/Chromium because VideoHoarder still exposes specialist/legacy pages inside the desktop shell. In one-file PyInstaller mode those runtime binaries are compressed into `VideoHoarder.exe`, so a roughly 200–250 MiB executable is expected. `upx=True` is already enabled, but Qt/Chromium binaries do not always compress much further.

Safe choices:
- Keep the current **full one-file build** for all features.
- Use an **onedir** build if the goal is only a smaller `.exe` file; total installed size stays similar because the DLL/resources sit beside it.
- A much smaller **native-only/lite build** would require removing QtWebEngine and therefore must be a separate product because specialist embedded web pages would no longer be available.

Do not manually exclude QtWebEngine/Chromium from the current full spec: that would reduce size by breaking features.

## Optional smaller EXE build

`BUILD_SMALL_EXE.bat` creates a PyInstaller **one-folder** release at:

`dist\VideoHoarder\VideoHoarder.exe`

The EXE itself is much smaller because Qt/PySide6/QtWebEngine binaries live beside it in the `VideoHoarder` runtime folder. The total folder/ZIP size remains broadly similar to the one-file release because Chromium/QtWebEngine is still required for specialist embedded web pages.

Use the normal `BUILD_WINDOWS.ps1` when you specifically want one portable EXE. Use `BUILD_SMALL_EXE.bat` when the size of the EXE file itself matters more than having a single-file distribution.
