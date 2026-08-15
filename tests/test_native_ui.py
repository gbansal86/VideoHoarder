from __future__ import annotations

import importlib.util
import os
import unittest


PYSIDE_AVAILABLE = importlib.util.find_spec("PySide6") is not None


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is installed in the GUI/build environment")
class NativeUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication

        cls.app = QApplication.instance() or QApplication([])

    def test_sidebar_has_simplified_navigation(self) -> None:
        from app.native_ui import Sidebar

        sidebar = Sidebar()
        self.assertEqual(
            list(sidebar.buttons),
            ["dashboard", "queue", "library", "oldimport", "repairdata", "chatgpt_processing", "knowledge", "collections", "more", "settings"],
        )

    def test_tool_catalog_is_replaced_by_eight_workflows(self) -> None:
        from app.native_ui import WorkflowsPage

        self.assertEqual(len(WorkflowsPage.WORKFLOWS), 8)
        self.assertEqual(
            [item[0] for item in WorkflowsPage.WORKFLOWS],
            ["new_download", "resume", "health", "knowledge", "chatgpt", "reports", "recovery", "setup"],
        )

    def test_download_presets_have_backend_actions(self) -> None:
        from app.native_ui import DownloadComposer

        actions = {data["action"] for _label, data in DownloadComposer.PRESETS}
        self.assertEqual(actions, {"full_download", "media_only"})


if __name__ == "__main__":
    unittest.main()
