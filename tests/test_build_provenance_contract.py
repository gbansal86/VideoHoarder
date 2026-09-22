from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_windows_builds_package_provenance_files() -> None:
    workflow = _text(".github/workflows/windows-build.yml")
    private_build = _text("BUILD_WINDOWS.ps1")

    for text in (workflow, private_build):
        assert "BUILD_INFO.txt" in text
        assert "DEPENDENCIES.txt" in text
        assert "release_self_test.json" in text
        assert "SHA256" in text

    assert "python -m pip list --format=freeze" in workflow
    assert "-m pip list --format=freeze" in private_build
    assert "pip freeze" not in workflow
    assert "pip freeze" not in private_build
    assert "Could not record dependency snapshot." in workflow
    assert "Could not record dependency snapshot." in private_build
    assert "Dependency snapshot is empty." in workflow
    assert "Dependency snapshot is empty." in private_build
    assert '"app\\VERSION.txt"' in private_build
    assert '"app\\\\VERSION.txt"' not in private_build
    assert "COMPUTERNAME" not in private_build


def test_release_docs_explain_provenance_files() -> None:
    releasing = _text("RELEASING.md")
    assert "## Build provenance files" in releasing
    assert "BUILD_INFO.txt" in releasing
    assert "DEPENDENCIES.txt" in releasing
    assert "release_self_test.json" in releasing
