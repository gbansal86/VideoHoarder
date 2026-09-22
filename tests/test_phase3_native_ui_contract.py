from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
NATIVE = (ROOT / "app" / "native_ui.py").read_text(encoding="utf-8")
GUI = (ROOT / "app" / "gui.py").read_text(encoding="utf-8")


def test_phase3_source_wires_saved_defaults_into_composer() -> None:
    assert "def apply_settings_defaults(self, values: dict[str, Any] | None" in NATIVE
    assert "self.apply_settings_defaults(backend.web_config_view(), force=True)" in NATIVE
    assert "self.settings_page.settings_saved.connect(self._settings_saved)" in GUI
    assert "self.command_center.apply_settings_defaults(dict(values or {}), force=False)" in GUI


def test_phase3_running_job_has_scoped_cancel_and_separate_stop_all() -> None:
    assert 'self.secondary.setText("×  Cancel this job")' in NATIVE
    assert 'self.secondary.setProperty("controlAction", "cancel")' in NATIVE
    assert 'self.stop_all = QPushButton("■  Stop all jobs")' in NATIVE
    assert 'self.control_requested.emit("stop", "")' in NATIVE


def test_phase3_shell_has_global_notification_surface_not_overwritten_by_queue_polling() -> None:
    assert 'self.global_notice = QLabel("Ready")' in GUI
    assert "self.global_notice.setText(text[:180])" in GUI
    # Queue polling changes its own bottom strip; it does not write the shell notice.
    refresh_block = NATIVE[NATIVE.index("    def refresh_fast(self)"):NATIVE.index("    def refresh_stats(self)")]
    assert "bottom_status.setText" in refresh_block
    assert "global_notice" not in refresh_block


@pytest.mark.skipif(importlib.util.find_spec("PySide6") is None, reason="PySide6 native runtime not installed")
def test_phase3_native_defaults_respect_explicit_override(monkeypatch) -> None:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from app.native_ui import DownloadComposer
    app = QApplication.instance() or QApplication([])
    composer = DownloadComposer()
    composer.apply_settings_defaults({"download_quality": "720", "save_srt_default": True}, force=True)
    assert composer.quality.currentData() == "720"
    assert composer.save_srt.isChecked() is True
    # Explicitly changed quality remains deliberate when Settings later change.
    idx = next(i for i in range(composer.quality.count()) if composer.quality.itemData(i) == "best")
    composer.quality.setCurrentIndex(idx)
    composer.apply_settings_defaults({"download_quality": "480", "save_srt_default": False}, force=False)
    assert composer.quality.currentData() == "best"
    assert composer.save_srt.isChecked() is False


@pytest.mark.skipif(importlib.util.find_spec("PySide6") is None, reason="PySide6 native runtime not installed")
def test_phase3_native_running_job_controls_are_distinct(monkeypatch) -> None:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from app.native_ui import JobDetails
    app = QApplication.instance() or QApplication([])
    details = JobDetails()
    job = {"job_id": "j1", "status": "RUNNING", "label": "Active"}
    details.set_job(job, {}, False, None, [job, {"job_id":"q","status":"QUEUED"}])
    assert details.secondary.text() == "×  Cancel this job"
    assert details.secondary.property("controlAction") == "cancel"
    assert details.stop_all.isVisible() is False or details.stop_all.isHidden() is False
