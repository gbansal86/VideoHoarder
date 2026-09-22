from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

CORE_DOCS = [
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "SECURITY.md",
    ROOT / "SUPPORT.md",
    ROOT / "GOVERNANCE.md",
    ROOT / "RELEASING.md",
    ROOT / "ROADMAP.md",
    ROOT / "TESTING.md",
    ROOT / "docs" / "QUICK_START.md",
    ROOT / "docs" / "LOCAL_VIDEO_IMPORT.md",
    ROOT / "docs" / "OPENAI_API_INTEGRATION.md",
    ROOT / "docs" / "THREAT_MODEL.md",
]

LINK_RE = re.compile(r"!?[[^]]*](([^)]+))")


def _local_target(raw: str) -> str | None:
    target = raw.strip().strip("<>")
    if not target or target.startswith("#"):
        return None
    lowered = target.lower()
    if lowered.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
        return None
    # Drop an optional Markdown title after the path.
    if ' "' in target:
        target = target.split(' "', 1)[0]
    target = target.split("#", 1)[0]
    target = target.split("?", 1)[0]
    return unquote(target) or None


def test_core_documentation_local_links_exist() -> None:
    missing: list[str] = []

    for doc in CORE_DOCS:
        assert doc.is_file(), f"Core OSS document is missing: {doc.relative_to(ROOT)}"
        text = doc.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = _local_target(match.group(1))
            if target is None:
                continue

            candidate = (doc.parent / target).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                missing.append(
                    f"{doc.relative_to(ROOT)} -> {target} escapes repository root"
                )
                continue

            if not candidate.exists():
                missing.append(f"{doc.relative_to(ROOT)} -> {target}")

    assert not missing, "Broken local documentation links:\n" + "\n".join(missing)


def test_readme_keeps_annotated_beginner_guides() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for image in (
        "docs/images/01_getting_started.svg",
        "docs/images/02_import_local_videos.svg",
        "docs/images/03_ai_processing.svg",
        "docs/images/04_public_repo_safety.svg",
    ):
        assert image in readme
        assert (ROOT / image).is_file()
