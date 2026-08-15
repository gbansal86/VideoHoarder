# VideoHoarder Desktop v33

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

`dist\VideoHoarder\VideoHoarder.exe`

The build uses PyInstaller's windowed one-folder mode. Users do not need Python
installed. Keep the complete `VideoHoarder` output folder together; its
`_internal` directory contains the embedded Python and Qt runtimes.

The build also creates `dist\VideoHoarder-v33.0-Windows.zip` for distribution.

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
