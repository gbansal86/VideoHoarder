"""Current-failure aggregation and selective CSV cleanup for VideoHoarder.

This module owns the durable *video/CSV* failure register.  Queue-job failures
are aggregated separately by :mod:`current_failure_registry` so the native UI
can show one complete failure list without mixing this persistence logic into
``app.py``.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Callable, Iterable


def _csv_value(row: dict, *names: str) -> str:
    for name in names:
        value = str(row.get(name) or "").strip()
        if value:
            return value
    return ""


def csv_failure_key(path: Path, row: dict) -> str:
    """Return a stable key for a CSV failure row, including rows without VIDEO_ID."""
    payload = "\x1f".join(
        [
            str(Path(path).resolve()),
            _csv_value(row, "Video ID", "video_id"),
            _csv_value(row, "URL", "url"),
            _csv_value(row, "Title", "title", "New Title", "clean_title"),
            _csv_value(row, "Reason", "reason", "Failure Reason", "failure_reason", "Error", "error", "Error Message"),
            _csv_value(row, "Stage", "stage"),
        ]
    )
    return "csv:" + hashlib.sha1(payload.encode("utf-8", errors="replace")).hexdigest()


def collect_current_failures(
    connect: Callable[[], object],
    video_columns: Callable[[], set[str] | list[str]],
    csv_paths: Iterable[Path],
    limit: int | None = None,
) -> list[dict]:
    cap = None if limit in (None, 0) else max(1, int(limit))
    cols = set(video_columns() or [])
    wanted = [
        "video_id", "url", "original_title", "clean_title", "channel", "local_video",
        "final_status", "failure_reason", "last_error", "downloaded_at",
    ]
    selected = [column for column in wanted if column in cols]
    rows: list[dict] = []

    con = connect()
    try:
        if selected:
            terms: list[str] = []
            if "final_status" in cols:
                terms.append("UPPER(COALESCE(final_status,''))='FAIL'")
            if "failure_reason" in cols:
                terms.append("COALESCE(failure_reason,'')<>''")
            if "last_error" in cols:
                terms.append("COALESCE(last_error,'')<>''")
            where = " OR ".join(terms) or "0"
            query = "SELECT " + ",".join(f'"{column}"' for column in selected)
            query += f" FROM videos WHERE {where} ORDER BY rowid DESC"
            params: tuple = ()
            if cap is not None:
                query += " LIMIT ?"
                params = (cap,)
            for record in con.execute(query, params).fetchall():
                item = dict(zip(selected, record))
                reason = str(item.get("failure_reason") or item.get("last_error") or "").strip()
                if str(item.get("final_status") or "").upper() == "FAIL" or reason:
                    video_id = str(item.get("video_id") or "").strip()
                    item["failure_reason"] = reason
                    item["failure_key"] = f"video:{video_id}" if video_id else ""
                    item["failure_kind"] = "Video"
                    item["failure_source"] = "SQLite"
                    rows.append(item)
    finally:
        con.close()

    seen = {(str(item.get("video_id") or ""), str(item.get("failure_reason") or "")) for item in rows}
    for raw_path in csv_paths:
        path = Path(raw_path)
        try:
            if not path.exists():
                continue
            with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
                for source in csv.DictReader(handle):
                    retry_status = _csv_value(source, "retry_status", "Retry Status").upper()
                    if retry_status in {"RESOLVED", "SUCCESS"}:
                        continue
                    video_id = _csv_value(source, "video_id", "Video ID")
                    reason = _csv_value(
                        source,
                        "reason", "Reason", "failure_reason", "Failure Reason", "error", "Error", "Error Message",
                    )
                    dedupe_key = (video_id, reason)
                    if dedupe_key in seen:
                        continue
                    rows.append({
                        "video_id": video_id,
                        "url": _csv_value(source, "url", "URL"),
                        "original_title": _csv_value(source, "title", "Title"),
                        "clean_title": _csv_value(source, "clean_title", "New Title"),
                        "channel": _csv_value(source, "channel", "Channel"),
                        "final_status": "FAIL",
                        "failure_reason": reason,
                        "last_error": reason,
                        "failure_key": csv_failure_key(path, source),
                        "failure_kind": "Failure log",
                        "failure_source": str(path),
                    })
                    seen.add(dedupe_key)
                    if cap is not None and len(rows) >= cap:
                        break
        except Exception:
            continue
        if cap is not None and len(rows) >= cap:
            break
    return rows[:cap] if cap is not None else rows


def remove_video_from_current_failure_csvs(video_id: str, csv_paths: Iterable[Path]) -> int:
    video_id = str(video_id or "").strip()
    if not video_id:
        return 0
    removed = 0
    seen_paths: set[Path] = set()
    for raw_path in csv_paths:
        path = Path(raw_path)
        if path in seen_paths:
            continue
        seen_paths.add(path)
        if not path.exists():
            continue
        try:
            with path.open("r", newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                fields = list(reader.fieldnames or [])
                source_rows = list(reader)
            if not fields:
                continue
            kept: list[dict] = []
            for row in source_rows:
                row_video_id = _csv_value(row, "Video ID", "video_id")
                if row_video_id == video_id:
                    removed += 1
                else:
                    kept.append(row)
            with path.open("w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(kept)
        except Exception:
            continue
    return removed


def remove_failure_key_from_current_csvs(failure_key: str, csv_paths: Iterable[Path]) -> int:
    """Remove exactly one keyed CSV failure, including failures without VIDEO_ID."""
    failure_key = str(failure_key or "").strip()
    if not failure_key.startswith("csv:"):
        return 0
    removed = 0
    seen_paths: set[Path] = set()
    for raw_path in csv_paths:
        path = Path(raw_path)
        if path in seen_paths:
            continue
        seen_paths.add(path)
        if not path.exists():
            continue
        try:
            with path.open("r", newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                fields = list(reader.fieldnames or [])
                source_rows = list(reader)
            if not fields:
                continue
            kept: list[dict] = []
            changed = False
            for row in source_rows:
                if csv_failure_key(path, row) == failure_key:
                    removed += 1
                    changed = True
                    continue
                kept.append(row)
            if changed:
                with path.open("w", newline="", encoding="utf-8-sig") as handle:
                    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(kept)
        except Exception:
            continue
    return removed
