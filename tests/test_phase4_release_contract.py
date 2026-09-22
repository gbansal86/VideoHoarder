from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_release_and_development_launcher_are_separate_build_products() -> None:
    release = (ROOT / "BUILD_WINDOWS.ps1").read_text(encoding="utf-8")
    dev = (ROOT / "BUILD_DEV_LAUNCHER.ps1").read_text(encoding="utf-8")
    assert "VideoHoarder.spec" in release
    assert "VideoHoarder_launcher.spec" not in release
    assert "VideoHoarder_launcher.spec" in dev
    assert "videohoarder.paths.json" in dev


def test_windows_release_gate_runs_full_pytest_native_subset_and_clean_room_smoke() -> None:
    build = (ROOT / "BUILD_WINDOWS.ps1").read_text(encoding="utf-8")
    assert "-m pytest -q tests" in build
    assert "tests\\test_native_ui.py tests\\test_phase3_native_ui_contract.py" in build
    assert 'if (($nativeOutput -join "`n") -match "\\bskipped\\b")' in build
    assert "VideoHoarder-clean-smoke-" in build
    assert "--release-self-test" in build
    assert "VLM_LIBRARY_ROOT" in build
    assert "release_self_test.json" in build


def test_release_spec_bundles_real_gui_and_sanitized_default_not_live_config() -> None:
    spec = (ROOT / "VideoHoarder.spec").read_text(encoding="utf-8")
    assert 'run_gui.pyw' in spec
    assert 'config.default.json' in spec
    assert 'VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md' in spec
    assert '"app/prompts"' in spec
    assert 'config.json"' not in spec
    assert 'excludes=["tkinter", "pytest"]' in spec
    assert 'PySide6' not in spec.split("excludes=", 1)[1].split("]", 1)[0]
    cfg = json.loads((ROOT / "app" / "config.default.json").read_text(encoding="utf-8"))
    assert cfg.get("youtube_data_api_key", "") == ""
    assert cfg.get("cookies_file", "") == ""
    assert cfg.get("cookies_mode") == "none"


def test_frozen_release_has_per_user_program_files_fallback() -> None:
    app_source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")
    gui_source = (ROOT / "app" / "gui.py").read_text(encoding="utf-8")
    assert "_windows_user_data_root" in app_source
    assert "_is_program_files_path(code_root)" in app_source
    assert '"source":"per-user app data"' in app_source
    assert 'os.environ.get("LOCALAPPDATA")' in gui_source


def test_release_self_test_explicitly_rejects_source_and_build_venv_neighbors() -> None:
    launcher = (ROOT / "run_gui.pyw").read_text(encoding="utf-8")
    assert '"--release-self-test" in sys.argv' in launcher
    assert 'source_neighbor = backend.CODE_ROOT / "Source"' in launcher
    assert 'backend.PATH_CONFIGURATION.get("build_environment")' in launcher
    assert 'result["frozen"] and not result["source_neighbor_exists"] and not result["build_venv_neighbor_exists"]' in launcher


def test_release_spec_required_runtime_data_files_exist() -> None:
    required = [
        ROOT / "app" / "config.default.json",
        ROOT / "app" / "VERSION.txt",
        ROOT / "app" / "prompts" / "VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md",
        ROOT / "assets" / "app_icon.svg",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    assert not missing, f"Required frozen runtime data files are missing: {missing}"
