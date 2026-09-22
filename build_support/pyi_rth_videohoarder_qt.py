"""Ensure bundled Qt DLLs win Windows DLL resolution in frozen builds."""

from __future__ import annotations

import os
from pathlib import Path
import sys


if sys.platform.startswith("win") and getattr(sys, "frozen", False):
    # A self-contained release must always use the Qt/Shiboken runtime bundled
    # into this exact PyInstaller build. Development/source launchers are a
    # separate product and do not execute this frozen-only runtime hook.
    runtime_root = Path(sys._MEIPASS)
    dll_directories = [runtime_root / "PySide6", runtime_root / "shiboken6"]
    dll_directories = [path for path in dll_directories if path.is_dir()]
    if dll_directories:
        prefix = os.pathsep.join(str(path) for path in dll_directories)
        os.environ["PATH"] = prefix + os.pathsep + os.environ.get("PATH", "")
        _videohoarder_dll_directories = []
        for path in dll_directories:
            try:
                _videohoarder_dll_directories.append(os.add_dll_directory(str(path)))
            except (AttributeError, OSError):
                pass
        # PyInstaller's PySide6 runtime hook loads Qt after these search paths
        # are registered. Forcing WinDLL loads here can deadlock before Python
        # reaches the application entry point on some Windows installations.
