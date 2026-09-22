"""Validated, atomic settings updates for VideoHoarder."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

BOOL_KEYS = {
    "download_subtitles", "download_description", "download_thumbnail",
    "download_info_json", "html_report", "ai_enabled", "save_srt_default",
    "prefix_upload_date_default", "smart_resume", "fast_no_llm_mode",
    "openai_api_enabled", "openai_store_responses", "openai_structured_outputs", "openai_allow_restricted_videos",
}
INT_RANGES = {
    "workers": (1, 32),
    "workflow_workers": (1, 5),
    "parallel_videos": (1, 5),
    "concurrent_fragments": (1, 16),
    "max_retries": (0, 20),
    "timeout_seconds": (1, 86400),
    "ai_parallel_workers": (1, 32),
    "ollama_timeout_seconds": (1, 86400),
    "openai_timeout_seconds": (10, 3600),
    "openai_max_retries": (0, 10),
    "openai_max_output_tokens": (1000, 128000),
}
ENUMS = {
    "download_quality": {"1080", "720", "480", "360", "best", "audio"},
    "cookies_mode": {"none", "browser", "file"},
    "browser_for_cookies": {"firefox", "chrome", "edge"},
    "openai_reasoning_effort": {"none", "low", "medium", "high", "xhigh", "max"},
}
STRING_KEYS = {"ollama_model", "openai_model", "openai_api_key_env"}
ALLOWED_KEYS = BOOL_KEYS | set(INT_RANGES) | set(ENUMS) | STRING_KEYS


def _validation_error(key: str, message: str) -> str:
    return f"{key}: {message}"


def validate_settings_update(values: Mapping[str, Any] | None, current: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Return a candidate settings object and all validation errors.

    The returned candidate is safe to persist only when errors is empty.  No
    mutation of ``current`` occurs here.
    """
    if values is None:
        values = {}
    if not isinstance(values, Mapping):
        return dict(current), ["settings: expected an object"]
    candidate = dict(current)
    errors: list[str] = []
    for key, value in values.items():
        if key not in ALLOWED_KEYS:
            errors.append(_validation_error(str(key), "unknown setting"))
            continue
        if key in BOOL_KEYS:
            if type(value) is not bool:  # intentionally reject 0/1 and "false"
                errors.append(_validation_error(key, "expected true or false"))
                continue
            candidate[key] = value
            continue
        if key in INT_RANGES:
            if isinstance(value, bool) or not isinstance(value, int):
                errors.append(_validation_error(key, "expected an integer"))
                continue
            low, high = INT_RANGES[key]
            if not low <= value <= high:
                errors.append(_validation_error(key, f"expected {low}..{high}"))
                continue
            candidate[key] = value
            continue
        if key in ENUMS:
            if not isinstance(value, str) or value not in ENUMS[key]:
                errors.append(_validation_error(key, "unsupported value"))
                continue
            candidate[key] = value
            continue
        if key in STRING_KEYS:
            if not isinstance(value, str):
                errors.append(_validation_error(key, "expected text"))
                continue
            text = value.strip()
            if not text or len(text) > 200:
                errors.append(_validation_error(key, "must be 1..200 characters"))
                continue
            if key == "openai_api_key_env" and not text.replace("_", "").isalnum():
                errors.append(_validation_error(key, "must be an environment-variable name"))
                continue
            candidate[key] = text
    return candidate, errors


def atomic_write_json(path: str | Path, value: Mapping[str, Any]) -> None:
    """Write JSON by fsync + os.replace so partial configuration is never visible."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(dict(value), handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, target)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def apply_settings_update(values: Mapping[str, Any] | None, current: dict[str, Any], path: str | Path) -> dict[str, Any]:
    """Validate and persist all-or-nothing, then update the in-memory dict."""
    candidate, errors = validate_settings_update(values, current)
    if errors:
        return {"ok": False, "message": "Settings were not saved.", "errors": errors}
    atomic_write_json(path, candidate)
    current.clear()
    current.update(candidate)
    return {"ok": True, "message": "Settings saved"}
