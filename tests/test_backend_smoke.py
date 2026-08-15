from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import unittest
from unittest import mock
import urllib.request


class BackendSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_root = (Path(__file__).parent / "runtime_data").resolve()
        cls.test_root.mkdir(parents=True, exist_ok=True)
        os.environ["VLM_LIBRARY_ROOT"] = str(cls.test_root)
        cls.backend = importlib.import_module("app.app")

    @classmethod
    def tearDownClass(cls) -> None:
        os.environ.pop("VLM_LIBRARY_ROOT", None)

    def test_library_root_override_is_used(self) -> None:
        self.assertEqual(Path(self.backend.BASE), self.test_root)

    def test_config_is_loaded_and_writable(self) -> None:
        self.assertIsInstance(self.backend.CFG, dict)
        self.assertIn("download_quality", self.backend.CFG)
        self.assertEqual(Path(self.backend.CONFIG).parent.name, "app")

    def test_dashboard_starts_without_opening_external_browser(self) -> None:
        with mock.patch.object(self.backend.webbrowser, "open") as browser_open:
            server = self.backend.start_dashboard(open_browser=False)
        try:
            port = int(server.server_address[1])
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/api/progress", timeout=5
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertEqual(response.status, 200)
            self.assertIn("phase", payload)
            browser_open.assert_not_called()
        finally:
            server.shutdown()
            server.server_close()

    def test_legacy_migration_preserves_canonical_health_files(self) -> None:
        audit_dir = self.test_root / "maintenance" / "audits"
        audit_dir.mkdir(parents=True, exist_ok=True)
        health_csv = audit_dir / "library_health.csv"
        health_json = audit_dir / "library_health_summary.json"
        health_csv.write_text("status,detail\nPASS,canonical\n", encoding="utf-8")
        health_json.write_text('{"status":"PASS"}', encoding="utf-8")

        self.backend.migrate_legacy_root_files()

        self.assertEqual(
            health_csv.read_text(encoding="utf-8"),
            "status,detail\nPASS,canonical\n",
        )
        self.assertEqual(
            health_json.read_text(encoding="utf-8"),
            '{"status":"PASS"}',
        )


if __name__ == "__main__":
    unittest.main()
