"""Optional OpenAI Responses API provider for VideoHoarder transcript intelligence.

The provider deliberately sits outside ``app.py``.  It consumes the same self-contained
ChatGPT package that the manual exchange workflow creates, processes ONE VIDEO_ID per
model call, merges the validated shapes back into one package result, and never applies
filesystem/database changes itself.

Security/privacy design:
- API keys are read from an environment variable (OPENAI_API_KEY by default).
- Keys are never written to config, logs, manifests, reports, or audit JSON.
- Responses are requested with ``store=False`` by default.
- Only the current video's evidence is sent in each call.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Callable, Mapping


class OpenAIProviderError(RuntimeError):
    """Raised for provider configuration, transport, or response-contract failures."""


def _get(settings: Mapping[str, Any], key: str, default: Any) -> Any:
    value = settings.get(key, default)
    return default if value is None else value


def provider_status(settings: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return a secret-free readiness report for the OpenAI provider."""
    cfg = dict(settings or {})
    key_env = str(_get(cfg, "openai_api_key_env", "OPENAI_API_KEY") or "OPENAI_API_KEY").strip()
    model = str(_get(cfg, "openai_model", "gpt-5.6") or "gpt-5.6").strip()
    enabled = bool(_get(cfg, "openai_api_enabled", False))
    key_present = bool(os.environ.get(key_env, "").strip())
    try:
        import openai  # noqa: F401
        sdk_available = True
        sdk_error = ""
    except Exception as exc:  # pragma: no cover - environment dependent
        sdk_available = False
        sdk_error = f"{type(exc).__name__}: {exc}"
    ready = enabled and key_present and sdk_available
    message = "Ready"
    if not enabled:
        message = "OpenAI API processing is disabled in VideoHoarder settings."
    elif not key_present:
        message = f"Environment variable {key_env} is not set."
    elif not sdk_available:
        message = "The openai Python package is not installed."
    return {
        "ok": True,
        "provider": "openai_responses_api",
        "enabled": enabled,
        "ready": ready,
        "model": model,
        "reasoning_effort": str(_get(cfg, "openai_reasoning_effort", "high")),
        "api_key_env": key_env,
        "api_key_configured": key_present,
        "sdk_available": sdk_available,
        "sdk_error": sdk_error,
        "store_responses": bool(_get(cfg, "openai_store_responses", False)),
        "structured_outputs": bool(_get(cfg, "openai_structured_outputs", True)),
        "allow_restricted_videos": bool(_get(cfg, "openai_allow_restricted_videos", False)),
        "message": message,
    }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OpenAIProviderError(f"Required package file is missing: {path.name}") from exc
    except json.JSONDecodeError as exc:
        raise OpenAIProviderError(f"Invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise OpenAIProviderError(f"{path.name} must contain one JSON object.")
    return data


def _usage_dict(response: Any) -> dict[str, int]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}
    out: dict[str, int] = {}
    for source, target in (
        ("input_tokens", "input_tokens"),
        ("output_tokens", "output_tokens"),
        ("total_tokens", "total_tokens"),
    ):
        value = getattr(usage, source, None)
        if value is not None:
            try:
                out[target] = int(value)
            except Exception:
                pass
    return out


def _safe_schema_name(package_id: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_-]+", "_", str(package_id or "videohoarder"))
    text = text.strip("_") or "videohoarder"
    return ("vh_" + text)[-60:]


def _compact_contract(package: Mapping[str, Any]) -> dict[str, Any]:
    response_schema = dict(package.get("response_schema") or {})
    # The JSON Schema itself is supplied to Responses API text.format; avoid also
    # repeating that potentially large object inside the textual prompt.
    response_schema.pop("formal_json_schema", None)
    instructions = dict(package.get("instructions") or {})
    # Current self-contained packages may carry the full master prompt and a full
    # response template inside prompt.json as well as at package top level.  The
    # API developer message already supplies the authoritative prompt and the
    # Structured Outputs contract carries the schema, so do not pay for the same
    # large strings twice.
    for redundant in ("master_prompt_exact", "response_template", "manual_exchange_notice"):
        instructions.pop(redundant, None)
    return {
        "package_id": package.get("package_id"),
        "schema_version": package.get("schema_version"),
        "prompt_version": package.get("prompt_version"),
        "prompt_hash": package.get("prompt_hash"),
        "package_type": package.get("package_type"),
        "instructions": instructions,
        "response_contract": response_schema,
    }


def _developer_prompt(package: Mapping[str, Any]) -> str:
    master = str(package.get("authoritative_prompt") or "").strip()
    return (
        "VIDEOHOARDER API EXECUTION CONTRACT\n"
        "Process exactly ONE supplied VIDEO_ID and no other video. "
        "Use only the supplied package evidence. Never invent missing timestamps, entities, "
        "quantities, or transcript content. Return only the required structured result. "
        "Do not perform web search or use outside facts. Preserve source fidelity.\n\n"
        "AUTHORITATIVE VIDEOHOARDER MASTER PROMPT\n"
        + master
    )


def _user_payload(package: Mapping[str, Any], video: Mapping[str, Any]) -> str:
    payload = _compact_contract(package)
    payload["execution"] = {
        "provider": "openai_responses_api",
        "isolation": "one_video_per_model_call",
        "video_id": video.get("video_id"),
        "instruction": (
            "Return the same package-level JSON contract but video_updates must contain exactly "
            "one item for this VIDEO_ID. The caller deterministically merges per-video results."
        ),
    }
    payload["video"] = video
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _extract_json(response: Any) -> dict[str, Any]:
    text = str(getattr(response, "output_text", "") or "").strip()
    if not text:
        raise OpenAIProviderError("OpenAI returned no output_text.")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise OpenAIProviderError(f"OpenAI returned invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise OpenAIProviderError("OpenAI result must be one JSON object.")
    return value


def _call_one_video(
    client: Any,
    *,
    package: Mapping[str, Any],
    video: Mapping[str, Any],
    settings: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    model = str(_get(settings, "openai_model", "gpt-5.6") or "gpt-5.6").strip()
    effort = str(_get(settings, "openai_reasoning_effort", "high") or "high").strip().lower()
    max_output = int(_get(settings, "openai_max_output_tokens", 32000))
    store = bool(_get(settings, "openai_store_responses", False))
    structured = bool(_get(settings, "openai_structured_outputs", True))
    formal_schema = ((package.get("response_schema") or {}).get("formal_json_schema") or {})

    kwargs: dict[str, Any] = {
        "model": model,
        "reasoning": {"effort": effort},
        "store": store,
        "max_output_tokens": max_output,
        "instructions": _developer_prompt(package),
        "input": _user_payload(package, video),
    }
    used_structured = False
    if structured and isinstance(formal_schema, dict) and formal_schema:
        kwargs["text"] = {
            "format": {
                "type": "json_schema",
                "name": _safe_schema_name(str(package.get("package_id") or "videohoarder")),
                "strict": True,
                "schema": formal_schema,
            }
        }
        used_structured = True

    started = time.time()
    try:
        response = client.responses.create(**kwargs)
    except Exception as first_exc:
        # Some historical VideoHoarder schemas may contain a JSON-Schema feature
        # unsupported by Structured Outputs.  Retry once in JSON-object mode while
        # retaining downstream VideoHoarder validation as the final authority.
        if not used_structured:
            raise OpenAIProviderError(
                f"OpenAI request failed ({type(first_exc).__name__}). "
                "Check your own API account, model, rate limit, and local network settings."
            ) from first_exc
        kwargs["text"] = {"format": {"type": "json_object"}}
        try:
            response = client.responses.create(**kwargs)
            used_structured = False
        except Exception as second_exc:
            raise OpenAIProviderError(
                "OpenAI request failed with Structured Outputs and JSON fallback: "
                f"{type(second_exc).__name__}. Check your own API account, model, and rate limit."
            ) from second_exc

    value = _extract_json(response)
    updates = value.get("video_updates")
    expected_id = str(video.get("video_id") or "")
    if not isinstance(updates, list) or len(updates) != 1:
        raise OpenAIProviderError("Per-video API result must contain exactly one video_updates item.")
    actual_id = str((updates[0] or {}).get("video_id") or "") if isinstance(updates[0], dict) else ""
    if actual_id != expected_id:
        raise OpenAIProviderError(f"API result VIDEO_ID mismatch: expected {expected_id}, received {actual_id or '<blank>'}.")
    meta = {
        "video_id": expected_id,
        "response_id": str(getattr(response, "id", "") or ""),
        "model": model,
        "reasoning_effort": effort,
        "structured_outputs": used_structured,
        "store": store,
        "seconds": round(time.time() - started, 3),
        "usage": _usage_dict(response),
    }
    return value, meta


def _merge_results(package: Mapping[str, Any], results: list[dict[str, Any]], failures: list[dict[str, str]]) -> dict[str, Any]:
    updates: list[dict[str, Any]] = []
    for result in results:
        for item in result.get("video_updates") or []:
            if isinstance(item, dict):
                updates.append(item)
    status_values = {str((x or {}).get("processing_status") or "") for x in updates}
    warnings = bool(failures or (status_values - {"PASS"}))
    return {
        "package_id": package.get("package_id"),
        "schema_version": package.get("schema_version"),
        "batch_validation_status": "PASS_WITH_WARNINGS" if warnings else "PASS",
        "package_outcome_status": "COMPLETE_WITH_REPROCESS_LIST" if warnings else "COMPLETE",
        "video_updates": updates,
    }


def _restricted_video_reason(video: Mapping[str, Any]) -> str:
    metadata = dict(video.get("metadata") or {})
    availability = str(metadata.get("availability") or "").strip().lower().replace("-", "_").replace(" ", "_")
    restricted = {
        "private", "unlisted", "members_only", "member_only", "subscriber_only",
        "premium_only", "login_required", "needs_auth", "authentication_required",
    }
    if availability in restricted:
        return availability
    return ""


def process_video_intelligence_package(
    package_folder: str | Path,
    settings: Mapping[str, Any],
    progress: Callable[[int, int, str, str], None] | None = None,
) -> dict[str, Any]:
    """Process an existing VideoHoarder CHATGPT_PACKAGE.json through OpenAI.

    The function makes exactly one model call per video, sequentially.  It writes
    provider audit/result sidecars but does not import/apply the result itself.
    """
    folder = Path(package_folder).resolve()
    package_path = folder / "CHATGPT_PACKAGE.json"
    package = _read_json(package_path)
    if str(package.get("package_type") or "") != "VIDEO_INTELLIGENCE":
        raise OpenAIProviderError("OpenAI transcript processing currently supports VIDEO_INTELLIGENCE packages only.")
    videos = package.get("videos") or []
    if not isinstance(videos, list) or not videos:
        raise OpenAIProviderError("Package contains no videos to process.")

    status = provider_status(settings)
    if not status.get("ready"):
        raise OpenAIProviderError(str(status.get("message") or "OpenAI provider is not ready."))
    key_env = str(status["api_key_env"])
    api_key = os.environ.get(key_env, "").strip()

    try:
        from openai import OpenAI
    except Exception as exc:  # pragma: no cover - installation dependent
        raise OpenAIProviderError("Install the 'openai' Python package before API processing.") from exc

    timeout = float(_get(settings, "openai_timeout_seconds", 900))
    retries = int(_get(settings, "openai_max_retries", 2))
    client = OpenAI(api_key=api_key, timeout=timeout, max_retries=retries)

    results: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    total = len(videos)
    allow_restricted = bool(_get(settings, "openai_allow_restricted_videos", False))
    for index, video in enumerate(videos, 1):
        if not isinstance(video, dict):
            failures.append({"video_id": "", "error": "Invalid video payload in package."})
            continue
        video_id = str(video.get("video_id") or "")
        restricted_reason = _restricted_video_reason(video)
        if restricted_reason and not allow_restricted:
            error = f"Restricted video ({restricted_reason}) was not sent. Enable openai_allow_restricted_videos only with explicit authorization."
            failures.append({"video_id": video_id, "error": error})
            calls.append({"video_id": video_id, "skipped": True, "reason": restricted_reason})
            if progress:
                progress(index, total, video_id, "Restricted/private video skipped by API privacy policy")
            continue
        if progress:
            progress(index - 1, total, video_id, "Submitting isolated transcript intelligence request")
        try:
            result, meta = _call_one_video(client, package=package, video=video, settings=settings)
            results.append(result)
            calls.append(meta)
            if progress:
                progress(index, total, video_id, "OpenAI result received; moving to next video")
        except Exception as exc:
            safe_error = (str(exc) if isinstance(exc, OpenAIProviderError) else
                          f"{type(exc).__name__}: provider error; details intentionally omitted from audit")
            failures.append({"video_id": video_id, "error": safe_error})
            calls.append({"video_id": video_id, "error": safe_error})
            if progress:
                progress(index, total, video_id, "API error recorded; continuing with remaining videos")

    merged = _merge_results(package, results, failures)
    package_id = str(package.get("package_id") or "videohoarder")
    result_path = folder / f"OPENAI_API_RESULT_{package_id}.json"
    result_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")

    audit = {
        "provider": "openai_responses_api",
        "package_id": package_id,
        "model": status.get("model"),
        "reasoning_effort": status.get("reasoning_effort"),
        "store_responses": status.get("store_responses"),
        "allow_restricted_videos": allow_restricted,
        "one_video_per_call": True,
        "video_count": total,
        "successful_videos": len(results),
        "failed_videos": len(failures),
        "failures": failures,
        "calls": calls,
        "result_file": result_path.name,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    audit_path = folder / "OPENAI_API_RUN.json"
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "ok": not failures,
        "partial": bool(failures) and bool(results),
        "provider": "openai_responses_api",
        "package_id": package_id,
        "result_file": str(result_path),
        "result_json": json.dumps(merged, ensure_ascii=False),
        "audit_file": str(audit_path),
        "successful_videos": len(results),
        "failed_videos": len(failures),
        "failures": failures,
        "calls": calls,
    }
