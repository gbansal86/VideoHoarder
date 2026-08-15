"""Double-click launcher for the VideoHoarder desktop application."""

from __future__ import annotations

import ctypes
from pathlib import Path
import sys
import traceback


def message_box(title: str, message: str, error: bool = False) -> None:
    flags = 0x10 if error else 0x40
    try:
        ctypes.windll.user32.MessageBoxW(None, message, title, flags)
    except Exception:
        pass


try:
    from app.gui import main
except ModuleNotFoundError as exc:
    if (exc.name or "").startswith("PySide6"):
        root = Path(__file__).resolve().parent
        message_box(
            "VideoHoarder needs PySide6",
            "The desktop GUI dependencies are not installed yet.\n\n"
            "Run INSTALL_GUI.ps1 once, then double-click run_gui.pyw again.\n\n"
            f"Installer location:\n{root / 'INSTALL_GUI.ps1'}",
            error=True,
        )
        raise SystemExit(2)
    raise
except Exception as exc:
    message_box(
        "VideoHoarder could not start",
        f"{type(exc).__name__}: {exc}\n\n{traceback.format_exc()[-1800:]}",
        error=True,
    )
    raise SystemExit(1)


raise SystemExit(main())
