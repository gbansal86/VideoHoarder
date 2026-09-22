from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_release_version_contract_is_consistent() -> None:
    public_version = _text("app/VERSION.txt").strip()
    base_version = public_version.removesuffix("-GUI")
    major, minor = (int(part) for part in base_version.split(".", 1))

    gui_match = re.search(r'^GUI_VERSION\s*=\s*"([^"]+)"', _text("app/gui.py"), re.MULTILINE)
    assert gui_match, "app/gui.py must define GUI_VERSION"
    assert gui_match.group(1) == base_version

    version_info = _text("build_support/version_info.txt")
    assert f"filevers=({major}, {minor}, 0, 0)" in version_info
    assert f"prodvers=({major}, {minor}, 0, 0)" in version_info
    assert f"StringStruct('FileVersion', '{base_version}.0')" in version_info
    assert f"StringStruct('ProductVersion', '{base_version}.0')" in version_info

    build_script = _text("BUILD_WINDOWS.ps1")
    assert f'VideoHoarder-v{base_version}-Windows.zip' in build_script

    changelog = _text("CHANGELOG.md")
    assert f"## {public_version}" in changelog

    release_workflow = ROOT / ".github" / "workflows" / "release.yml"
    if release_workflow.exists():
        release_text = release_workflow.read_text(encoding="utf-8")
        assert "app/VERSION.txt" in release_text
        assert "GITHUB_REF_NAME" in release_text
