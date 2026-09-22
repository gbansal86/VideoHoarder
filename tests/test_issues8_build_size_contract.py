from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_small_exe_onedir_build_is_available_without_replacing_full_release() -> None:
    spec = (ROOT / "VideoHoarder_onedir.spec").read_text(encoding="utf-8")
    build = (ROOT / "BUILD_SMALL_EXE.ps1").read_text(encoding="utf-8")
    assert "exclude_binaries=True" in spec
    assert "COLLECT(" in spec
    assert 'name="VideoHoarder"' in spec
    assert "VideoHoarder_onedir.spec" in build
    assert "Small-EXE release" in build
    assert "BUILD_WINDOWS.ps1" in (ROOT / "DESKTOP_README.md").read_text(encoding="utf-8")


def test_code_parent_includes_small_exe_build_files() -> None:
    packager = (ROOT / "scripts" / "create_code_parent_package.py").read_text(encoding="utf-8")
    for name in ("BUILD_SMALL_EXE.bat", "BUILD_SMALL_EXE.ps1", "VideoHoarder_onedir.spec"):
        assert f'"{name}"' in packager
