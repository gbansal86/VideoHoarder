"""Small orchestration helpers for VideoHoarder download jobs.

The backend download implementations remain callable as before.  This module
owns the optional resolve-before-download workflow and the per-input outcome
ledger so queue success is based on every submitted input rather than on an
empty/partial result list.
"""

from __future__ import annotations

from typing import Any, Callable


TERMINAL_INPUT_STATUSES = {"SUCCESS", "SKIPPED_INTENTIONAL", "FAILED", "CANCELLED"}


def resolved_download_urls(resolution: dict, original_urls: list[str]) -> tuple[list[str], list[dict]]:
    results = list((resolution or {}).get("results") or [])
    by_original = {str(item.get("original_url") or ""): item for item in results}
    effective: list[str] = []
    decisions: list[dict] = []
    for original in original_urls:
        item = by_original.get(str(original), {})
        resolved = str(item.get("watch_url") or "").strip() if item.get("status") == "RESOLVED" else ""
        chosen = resolved or str(original)
        effective.append(chosen)
        decisions.append(
            {
                "original_url": str(original),
                "effective_url": chosen,
                "resolved": bool(resolved),
                "resolution_status": str(item.get("status") or ("RESOLVED" if resolved else "NOT_REQUESTED")),
                "host": item.get("host") or "",
                "video_id": item.get("video_id") or "",
            }
        )
    return effective, decisions


def _status_from_download_item(item: dict[str, Any]) -> str:
    status = str(item.get("status") or "").upper()
    if status in {"SUCCESS", "PASS", "COMPLETE", "COMPLETED"}:
        return "SUCCESS"
    if status in {"SKIPPED", "ALREADY_COMPLETE", "DUPLICATE", "EXISTS"}:
        return "SKIPPED_INTENTIONAL"
    if status in {"CANCELLED", "CANCELED", "STOPPED"}:
        return "CANCELLED"
    return "FAILED"


def ensure_input_outcomes(
    original_urls: list[str],
    effective_urls: list[str],
    download_result: dict[str, Any] | None,
    decisions: list[dict] | None = None,
) -> list[dict[str, Any]]:
    """Return exactly one terminal ledger entry for every submitted URL.

    Backends may return their own ``input_outcomes``.  Otherwise this helper
    derives conservative outcomes from detailed result rows.  If the backend
    claims success but returns no processable evidence, inputs are marked
    failed rather than allowing ``all([])`` style false success.
    """

    original_urls = [str(x) for x in original_urls]
    effective_urls = [str(x) for x in effective_urls]
    result = dict(download_result or {})
    existing = list(result.get("input_outcomes") or [])
    if existing:
        by_input = {str(x.get("input_url") or ""): dict(x) for x in existing if isinstance(x, dict)}
        ledger: list[dict[str, Any]] = []
        for idx, original in enumerate(original_urls):
            row = dict(by_input.get(original) or {})
            if not row:
                row = {
                    "input_url": original,
                    "effective_url": effective_urls[idx] if idx < len(effective_urls) else original,
                    "status": "FAILED",
                    "stage": "result_accounting",
                    "message": "Backend returned no terminal outcome for this input.",
                }
            status = str(row.get("status") or "FAILED").upper()
            row["status"] = status if status in TERMINAL_INPUT_STATUSES else "FAILED"
            ledger.append(row)
        return ledger

    details = [x for x in (result.get("details") or result.get("results") or []) if isinstance(x, dict)]
    ledger = []
    for idx, original in enumerate(original_urls):
        effective = effective_urls[idx] if idx < len(effective_urls) else original
        match = next(
            (
                item
                for item in details
                if str(item.get("source_url") or item.get("url") or "") in {original, effective}
            ),
            None,
        )
        if match is None and len(original_urls) == 1 and len(details) == 1:
            match = details[0]
        if match is not None:
            ledger.append(
                {
                    "input_url": original,
                    "effective_url": effective,
                    "status": _status_from_download_item(match),
                    "stage": "download",
                    "message": str(match.get("reason") or match.get("message") or match.get("status") or ""),
                }
            )
        else:
            ledger.append(
                {
                    "input_url": original,
                    "effective_url": effective,
                    "status": "FAILED",
                    "stage": "result_accounting",
                    "message": "No processable result was returned for this input.",
                }
            )
    return ledger


def aggregate_input_outcomes(outcomes: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {status: 0 for status in TERMINAL_INPUT_STATUSES}
    for row in outcomes:
        status = str(row.get("status") or "FAILED").upper()
        counts[status if status in counts else "FAILED"] += 1
    ok = bool(outcomes) and counts["FAILED"] == 0 and counts["CANCELLED"] == 0
    return {"ok": ok, "submitted": len(outcomes), "outcome_counts": counts}


def execute_download_workflow(
    urls: list[str],
    action: str,
    resolve_embedded: bool,
    resolver_func: Callable[[list[str]], dict],
    full_download_func: Callable[..., dict],
    media_download_func: Callable[..., dict],
    quality: str = "1080",
    use_ollama: bool = False,
    save_srt: bool = False,
    prefix_upload_date: bool = False,
    download_comments: bool = False,
    category: str = "Entertainment",
    vtt: bool = True,
    category_mode: str = "source",
    smart_resume: bool = True,
) -> dict[str, Any]:
    original_urls = [str(url or "").strip() for url in urls if str(url or "").strip()]
    if not original_urls:
        return {"ok": False, "message": "No URLs supplied", "input_outcomes": [], "submitted": 0}

    resolution: dict[str, Any] | None = None
    effective_urls = list(original_urls)
    decisions: list[dict] = []
    if resolve_embedded:
        resolution = resolver_func(original_urls)
        effective_urls, decisions = resolved_download_urls(resolution, original_urls)

    if str(action) == "full_download":
        download_result = full_download_func(
            effective_urls,
            quality,
            bool(use_ollama),
            bool(save_srt),
            bool(prefix_upload_date),
            bool(download_comments),
            bool(smart_resume),
            bool(vtt),
        )
    elif str(action) == "media_only":
        download_result = media_download_func(
            effective_urls,
            quality,
            category,
            bool(vtt),
            category_mode,
            bool(save_srt),
        )
    else:
        raise ValueError(f"Unsupported download workflow action: {action}")

    download_result = dict(download_result or {})
    outcomes = ensure_input_outcomes(original_urls, effective_urls, download_result, decisions)
    aggregate = aggregate_input_outcomes(outcomes)
    download_result["input_outcomes"] = outcomes
    download_result["submitted"] = aggregate["submitted"]
    download_result["outcome_counts"] = aggregate["outcome_counts"]
    # A backend failure remains a failure; otherwise the ledger is authoritative.
    download_result["ok"] = bool(download_result.get("ok") is not False and aggregate["ok"])

    if not resolve_embedded:
        return download_result

    return {
        "ok": bool(download_result.get("ok")),
        "resolution": resolution,
        "resolution_decisions": decisions,
        "effective_urls": effective_urls,
        "input_outcomes": outcomes,
        "submitted": aggregate["submitted"],
        "outcome_counts": aggregate["outcome_counts"],
        "download": download_result,
    }
