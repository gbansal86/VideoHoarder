"""Durable queue-state helpers for restart recovery.

The application still owns live job execution. This module only stores a compact,
JSON-safe snapshot so unfinished jobs can reappear as INTERRUPTED after restart
and be explicitly retried by the user.
"""
from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

ACTIVE_STATUSES = {"QUEUED", "RUNNING", "CANCELLING"}
TERMINAL_STATUSES = {"SUCCESS", "WARN", "FAILED", "CANCELLED", "INTERRUPTED"}
RECOVERABLE_STATUSES = ACTIVE_STATUSES | {"INTERRUPTED"}
_WRITE_LOCK = threading.RLock()

# Persist only restart/UI-critical state. Full results remain in per-run logs and
# must not make job_queue_state.json grow without bound.
PERSISTED_JOB_FIELDS = {
    "job_id", "label", "action", "status", "created_at", "started_at", "finished_at",
    "message", "stage", "processed", "total", "transfer_percent", "progress",
    "speed", "eta", "source_url", "video_id", "thumbnail_path", "thumbnail_url",
    "download_options", "error",
    "active_videos", "parent_job_id", "retry_of_video_id",
}

SENSITIVE_KEY_PARTS = ("password", "secret", "token", "cookie", "authorization", "api_key", "apikey")

def _contains_sensitive_mapping(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).lower()
            if any(part in lowered for part in SENSITIVE_KEY_PARTS):
                return True
            if _contains_sensitive_mapping(item):
                return True
    elif isinstance(value, (list, tuple, set)):
        return any(_contains_sensitive_mapping(item) for item in value)
    return False


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    return str(value)



def _json_native_copy(value: Any) -> Any:
    """Copy only values whose type survives JSON round-trip without coercion."""
    if value is None or type(value) in {str, int, float, bool}:
        return value
    if isinstance(value, (list, tuple)):
        return [_json_native_copy(item) for item in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("retry descriptor dictionary keys must be strings")
            out[key] = _json_native_copy(item)
        return out
    raise TypeError(f"unsupported retry descriptor value: {type(value).__name__}")

def task_descriptor(func: object, args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any] | None:
    name = str(getattr(func, "__name__", "") or "").strip()
    if not name:
        return None
    if _contains_sensitive_mapping(args) or _contains_sensitive_mapping(kwargs):
        return None
    # Retry descriptors must round-trip without type coercion.  Paths, sets,
    # arbitrary objects and non-string dict keys are rejected instead of being
    # stringified into a different call signature after restart.
    try:
        safe_args = _json_native_copy(list(args))
        safe_kwargs = _json_native_copy(dict(kwargs))
        json.dumps({"name": name, "args": safe_args, "kwargs": safe_kwargs}, allow_nan=False)
    except (TypeError, ValueError):
        return None
    return {"name": name, "args": safe_args, "kwargs": safe_kwargs}


def _compact_job(row: dict[str, Any]) -> dict[str, Any]:
    compact = {key: row.get(key) for key in PERSISTED_JOB_FIELDS if key in row}
    # Keep identity/status even if a caller supplied an unusually sparse row.
    for key in ("job_id", "label", "status", "created_at"):
        if key in row:
            compact[key] = row.get(key)
    return _json_safe(compact)


def queue_payload(jobs: dict[str, dict[str, Any]], tasks: dict[str, tuple], *, limit: int = 100) -> dict[str, Any]:
    """Return a compact durable queue snapshot.

    ``limit`` caps completed history only. Every recoverable job (QUEUED,
    RUNNING, CANCELLING or INTERRUPTED) is always persisted so large batches
    cannot silently lose unfinished work on restart.
    """
    all_rows = sorted(
        jobs.values(), key=lambda row: float(row.get("created_at") or 0), reverse=True
    )
    recoverable = [row for row in all_rows if str(row.get("status") or "").upper() in RECOVERABLE_STATUSES]
    terminal = [row for row in all_rows if str(row.get("status") or "").upper() not in RECOVERABLE_STATUSES]
    history_limit = max(0, int(limit))
    selected = recoverable + terminal[:history_limit]
    selected.sort(key=lambda row: float(row.get("created_at") or 0), reverse=True)

    task_map: dict[str, Any] = {}
    for job in selected:
        jid = str(job.get("job_id") or "")
        task = tasks.get(jid)
        if jid and task and len(task) == 3:
            descriptor = task_descriptor(task[0], tuple(task[1]), dict(task[2]))
            if descriptor:
                task_map[jid] = descriptor
    return {
        "schema": 2,
        "jobs": [_compact_job(dict(row)) for row in selected],
        "tasks": task_map,
    }


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    """Atomically replace queue state without shared-temp-name races."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, ensure_ascii=False, indent=2)
    with _WRITE_LOCK:
        fd, raw_tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
        tmp = Path(raw_tmp)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
                fh.write(data)
                fh.flush()
                try:
                    os.fsync(fh.fileno())
                except OSError:
                    pass
            # Windows Defender/indexers can briefly hold the destination. A
            # bounded retry keeps the atomic write reliable without ever
            # falling back to a non-atomic write.
            last_error: OSError | None = None
            for attempt in range(8):
                try:
                    os.replace(tmp, path)
                    last_error = None
                    break
                except PermissionError as exc:
                    last_error = exc
                    if attempt == 7:
                        raise
                    time.sleep(0.025 * (attempt + 1))
            if last_error is not None:
                raise last_error
        finally:
            try:
                tmp.unlink()
            except FileNotFoundError:
                pass


def load(path: Path) -> dict[str, Any]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {"schema": 1, "jobs": [], "tasks": {}}
    if not isinstance(obj, dict):
        return {"schema": 1, "jobs": [], "tasks": {}}
    return obj


def interrupted_copy(job: dict[str, Any]) -> dict[str, Any]:
    row = dict(job or {})
    status = str(row.get("status") or "").upper()
    if status in ACTIVE_STATUSES:
        row["status"] = "INTERRUPTED"
        row["message"] = "Interrupted by application restart. Select Resume / retry to continue."
        row["stage"] = "Interrupted"
        row.pop("started_at", None)
        row.pop("finished_at", None)
    children = []
    for raw in list(row.get("active_videos") or []):
        child = dict(raw) if isinstance(raw, dict) else {}
        child_status = str(child.get("status") or "").upper()
        if child_status in ACTIVE_STATUSES | {"PAUSING", "CANCELLING"}:
            child["status"] = "INTERRUPTED"
            child["stage"] = "Interrupted"
        children.append(child)
    if children:
        row["active_videos"] = children
    return row
