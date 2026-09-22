"""Dependency discovery helpers kept outside the main VideoHoarder app module."""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
import urllib.request
import json
from pathlib import Path
from typing import Any, Callable


def python_site_package_fallbacks(cfg: dict[str, Any] | None = None) -> list[Path]:
    """Return only explicitly configured package folders.

    User-profile and system Python locations are intentionally not searched:
    portable dependencies belong under the configured VideoHoarder parent.
    """
    roots: list[Path] = []
    try:
        configured = (cfg or {}).get("python_site_package_fallbacks", [])
        if isinstance(configured, str):
            configured = [configured]
        roots.extend(Path(str(p)) for p in configured or [])
    except Exception:
        pass
    seen: set[str] = set()
    out: list[Path] = []
    for p in roots:
        try:
            rp = str(Path(p).resolve())
        except Exception:
            rp = str(p)
        if rp in seen:
            continue
        seen.add(rp)
        if Path(p).exists():
            out.append(Path(p))
    return out


def ensure_transcript_api_paths(py_packages: Path, cfg: dict[str, Any] | None = None, fallback_paths: list[Path] | None = None) -> None:
    paths = [py_packages]
    paths.extend(list(fallback_paths) if fallback_paths is not None else python_site_package_fallbacks(cfg))
    for p in paths:
        s = str(p)
        if p.exists() and s not in sys.path:
            sys.path.insert(0, s)
    importlib.invalidate_caches()


def transcript_api_location(py_packages: Path, cfg: dict[str, Any] | None = None, fallback_paths: list[Path] | None = None) -> str:
    ensure_transcript_api_paths(py_packages, cfg, fallback_paths)
    try:
        spec = importlib.util.find_spec("youtube_transcript_api")
        if spec and spec.origin:
            return str(spec.origin)
    except Exception:
        pass
    return ""


def transcript_api_import(py_packages: Path, cfg: dict[str, Any] | None = None, fallback_paths: list[Path] | None = None):
    ensure_transcript_api_paths(py_packages, cfg, fallback_paths)
    try:
        return importlib.import_module("youtube_transcript_api")
    except Exception:
        return None


def ollama_model_manifest_path(model: str, ollama_exe: Path | None, base: Path | None) -> Path | None:
    name = str(model or "").strip()
    if not name:
        return None
    family, tag = name.split(":", 1) if ":" in name else (name, "latest")
    roots: list[Path] = []
    if ollama_exe:
        roots.append(Path(ollama_exe).parent / "models")
    if base:
        roots.append(Path(base) / "tools" / "ollama" / "models")
    env_root = os.environ.get("OLLAMA_MODELS") or ""
    if env_root:
        roots.append(Path(env_root))
    for root in roots:
        if not root:
            continue
        manifest = root / "manifests" / "registry.ollama.ai" / "library" / family / tag
        if manifest.exists():
            return manifest
    return None


def ollama_server_ok() -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def ollama_model_ok(model: str) -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as r:
            data = json.loads(r.read().decode("utf-8"))
        names: list[str] = []
        for m in data.get("models", []):
            names.append(m.get("name", ""))
            names.append(m.get("model", ""))
        return model in names or any(x.startswith(model.split(":")[0] + ":") for x in names)
    except Exception:
        return False


def dependency_status_report(
    *,
    cfg: dict[str, Any],
    py_packages: Path,
    ytdlp: Path,
    ffmpeg: Path,
    ffprobe: Path,
    deno: Path,
    ollama: Path,
    base: Path,
    tool_version: Callable[..., str],
    refresh_tool_paths: Callable[[], None],
) -> list[dict[str, str]]:
    refresh_tool_paths()
    statuses = [
        {"tool": "Python", "required": "Yes", "status": "OK", "path": sys.executable, "version": sys.version.split()[0]},
        {"tool": "yt-dlp", "required": "Yes", "status": "OK" if ytdlp.exists() else "Missing", "path": str(ytdlp) if ytdlp.exists() else "", "version": tool_version(ytdlp)},
        {"tool": "FFmpeg", "required": "For video merging", "status": "OK" if ffmpeg.exists() else "Missing", "path": str(ffmpeg) if ffmpeg.exists() else "", "version": tool_version(ffmpeg, ["-version"])},
        {"tool": "ffprobe", "required": "Recommended", "status": "OK" if ffprobe.exists() else "Missing", "path": str(ffprobe) if ffprobe.exists() else "", "version": tool_version(ffprobe, ["-version"])},
        {"tool": "Deno", "required": "Recommended for YouTube", "status": "OK" if deno.exists() else "Missing", "path": str(deno) if deno.exists() else "", "version": tool_version(deno)},
        {"tool": "Ollama CLI", "required": "For AI", "status": "OK" if ollama.exists() else "Missing", "path": str(ollama) if ollama.exists() else "", "version": tool_version(ollama)},
    ]
    yta_path = transcript_api_location(py_packages, cfg)
    yta_ok = bool(yta_path) and transcript_api_import(py_packages, cfg) is not None
    statuses.append({"tool": "youtube-transcript-api", "required": "Preferred transcript source", "status": "OK" if yta_ok else "Missing", "path": yta_path or str(py_packages), "version": ""})
    server = ollama_server_ok()
    model = cfg.get("ollama_model", "qwen2.5:7b")
    local_model = ollama_model_manifest_path(model, ollama, base)
    statuses.append({"tool": "Ollama server", "required": "For AI", "status": "OK" if server else "Not Running", "path": "127.0.0.1:11434", "version": ""})
    if server and ollama_model_ok(model):
        model_status = "OK"
    elif local_model:
        model_status = "Installed locally; server not running"
    else:
        model_status = "Missing/Unknown"
    statuses.append({"tool": f"Model {model}", "required": "For AI", "status": model_status, "path": str(local_model or ""), "version": ""})
    return statuses
