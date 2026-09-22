"""Render the native command centre off-screen for visual regression checks."""

from __future__ import annotations

import os
from pathlib import Path
import sys


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")

output = Path(sys.argv[1] if len(sys.argv) > 1 else "gui-preview.png").resolve()
if len(sys.argv) > 2:
    os.environ["VLM_LIBRARY_ROOT"] = str(Path(sys.argv[2]).resolve())
requested_page = sys.argv[3] if len(sys.argv) > 3 else "dashboard"
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QLabel

from app.gui import MainWindow


app = QApplication.instance() or QApplication([])
window = MainWindow(output.with_suffix(".log"))
window.resize(1500, 900)
if os.environ.get("VLM_RENDER_HIDDEN") == "1":
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
window.show()


def select_page() -> None:
    if window.backend is None:
        QTimer.singleShot(250, select_page)
        return
    window.show_page(requested_page)


QTimer.singleShot(100, select_page)


def capture() -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    brand = window.findChild(QLabel, "brandName")
    if brand is not None:
        print(
            "BRAND_GEOMETRY",
            brand.geometry().getRect(),
            "TEXT_WIDTH",
            brand.fontMetrics().horizontalAdvance(brand.text()),
        )
    if not window.grab().save(str(output), "PNG"):
        raise RuntimeError(f"Could not save GUI preview to {output}")
    window._closing = True
    window.close()
    app.quit()


QTimer.singleShot(8_000, capture)
raise SystemExit(app.exec())
