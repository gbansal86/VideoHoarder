import json
from pathlib import Path


def test_config_default_file_is_authoritative_source():
    text=Path("app/app.py").read_text(encoding="utf-8")
    assert "app/config.default.json is authoritative" in text
    assert '"cookies_mode": "browser"' not in text
    assert 'DEFAULT = {' in text
    default=json.loads(Path("app/config.default.json").read_text(encoding="utf-8"))
    assert len(default) > 100


def test_dependency_discovery_delegates_to_service():
    text=Path("app/app.py").read_text(encoding="utf-8")
    assert "return dependency_transcript_api_import(PY_PACKAGES,CFG,_python_site_package_fallbacks())" in text
    assert "return dependency_ollama_server_ok()" in text
    assert "return dependency_ollama_model_ok(model)" in text


def test_program_files_release_uses_writable_base_for_visible_library_source_contract():
    text=Path("app/app.py").read_text(encoding="utf-8")
    assert 'if getattr(sys,"frozen",False) and _is_program_files_path(CODE_ROOT):' in text
    assert 'BASE / "downloads"' in text


def test_organize_existing_library_setting_removed_but_safe_explicit_action_remains():
    cfg=json.loads(Path("app/config.default.json").read_text(encoding="utf-8"))
    assert "organize_existing_library" not in cfg
    text=Path("app/app.py").read_text(encoding="utf-8")
    assert "def organize_existing_library():" in text
    assert "files_equal(fp, target)" in text
