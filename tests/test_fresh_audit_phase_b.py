from pathlib import Path
from app.download_options import DownloadOptions


def test_settings_map_to_job_options():
    opts = DownloadOptions.from_settings({
        "download_quality":"720",
        "save_srt_default":True,
        "download_subtitles":False,
        "smart_resume":False,
        "ai_enabled":True,
        "fast_no_llm_mode":True,
    })
    assert opts.quality == "720"
    assert opts.save_srt is True
    assert opts.vtt is False
    assert opts.smart_resume is False
    assert opts.use_ollama is False


def test_frozen_pip_is_not_used_source_contract():
    text = Path("app/app.py").read_text(encoding="utf-8")
    assert 'if getattr(sys,"frozen",False):' in text
    assert 'frozen EXE cannot run pip' in text
    assert 'frozen EXE cannot be used as a pip interpreter' in text


def test_release_bundles_python_dependencies():
    req = Path("requirements.txt").read_text(encoding="utf-8").lower()
    spec = Path("VideoHoarder.spec").read_text(encoding="utf-8")
    assert "selenium" in req
    assert "youtube-transcript-api" in req
    assert 'collect_submodules("selenium")' in spec
    assert 'collect_submodules("youtube_transcript_api")' in spec


def test_shipped_default_is_privacy_safe():
    import json
    cfg = json.loads(Path("app/config.default.json").read_text(encoding="utf-8"))
    assert cfg["cookies_mode"] == "none"
    assert cfg["cookies_file"] == ""


def test_composer_wires_visible_settings_to_download_payload_source_contract():
    text = Path("app/native_ui.py").read_text(encoding="utf-8")
    assert '"vtt": self.download_subtitles.isChecked()' in text
    assert '"smart_resume": self.smart_resume.isChecked()' in text
    assert 'self.use_ollama.setChecked(defaults.use_ollama)' in text
