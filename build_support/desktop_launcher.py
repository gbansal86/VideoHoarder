"""Portable launcher for the VideoHoarder desktop application."""

from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import sys


root = Path(sys.executable).resolve().parent
config_file = next(
    (
        candidate
        for parent in (root, *root.parents)
        if (candidate := parent / "videohoarder.paths.json").is_file()
    ),
    root / "videohoarder.paths.json",
)
config = json.loads(config_file.read_text(encoding="utf-8-sig")) if config_file.is_file() else {}
install = Path(str(config.get("install_root") or ".")).expanduser()
if not install.is_absolute():
    install = config_file.parent / install
install = install.resolve()
def configured_path(key: str, fallback: str) -> Path:
    value = Path(str(config.get(key) or fallback)).expanduser()
    return (value if value.is_absolute() else install / value).resolve()
project = configured_path("source_dir", "VideoHoarder_App/Source")
pythonw = configured_path("build_environment", ".videohoarder-tools/build-env") / "Scripts" / "pythonw.exe"
launcher = project / "run_gui.pyw"
media_library = configured_path("video_library_dir", "VideoHoarder Videos")

if not pythonw.is_file() or not launcher.is_file():
    raise SystemExit(
        "VideoHoarder installation is incomplete. Expected "
        "the source and build-environment paths configured in videohoarder.paths.json."
    )

environment = dict(os.environ)
# Source runs use the configured source folder as CODE_ROOT, while the user's media
# collection may live elsewhere. Pass this explicitly so all
# downloads, scans and package preflights use the existing collection.
if media_library.is_dir():
    environment["VLM_VIDEO_LIBRARY"] = str(media_library)

subprocess.Popen(
    [str(pythonw), str(launcher)],
    cwd=str(project),
    env=environment,
    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
)
