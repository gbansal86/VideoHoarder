#!/usr/bin/env python3
"""Validate VideoHoarder V3.3.4 incoming RESULT_*.json coverage."""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from pathlib import Path


DEFAULT_EXCHANGE = Path(os.environ.get("VIDEOHOARDER_EXCHANGE") or (Path.cwd() / "data" / "chatgpt" / "exchange"))
VALID_SEMANTIC_STATUS = {"PASS", "PASS_WITH_WARNINGS", "REPROCESS_RECOMMENDED", "SOURCE_INSUFFICIENT"}
REQUIRED_SELF_CONTAINED = {
    "CHATGPT_PACKAGE.json",
    "VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md",
    "PACKAGE_README.txt",
    "manifest.json",
    "schema.json",
    "prompt.json",
    "evidence.json",
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("JSON root is not an object")
    return data


def package_paths(exchange: Path, batch_set: str = "") -> list[Path]:
    root = exchange / "outgoing" / "group_similar" / "batches"
    if batch_set:
        root = root / batch_set
        return sorted(root.glob("packages/*/CHATGPT_PACKAGE.json"))
    return sorted(root.glob("*/packages/*/CHATGPT_PACKAGE.json"))


def validate_pair(package_path: Path, result_path: Path | None) -> dict:
    package = load_json(package_path)
    package_dir = package_path.parent
    package_id = str(package.get("package_id") or package_dir.name)
    expected_ids = [str(v.get("video_id") or "") for v in (package.get("videos") or []) if isinstance(v, dict)]
    requested_by_id = {str(v.get("video_id") or ""): set(v.get("requested_features") or []) for v in (package.get("videos") or []) if isinstance(v, dict)}
    row = {
        "package_id": package_id,
        "package": str(package_path),
        "result": str(result_path or ""),
        "expected_videos": len(expected_ids),
        "final_semantic_status_count": 0,
        "status": "MISSING",
        "warnings": "",
        "errors": "",
    }
    errors: list[str] = []
    warnings: list[str] = []
    missing_files = sorted(name for name in REQUIRED_SELF_CONTAINED if not (package_dir / name).is_file())
    if missing_files:
        errors.append("package missing self-contained file(s): " + ", ".join(missing_files))
    if str(package.get("schema_version") or "") not in {"3.3", "3.0"}:
        warnings.append("package schema_version is not recognized V3.3/V3.0")
    if str(package.get("prompt_version") or "") == "3.3.4-final" and not str(package.get("prompt_hash") or ""):
        errors.append("V3.3.4 package missing prompt_hash")
    if not result_path or not result_path.exists():
        row["status"] = "MISSING"
        row["warnings"] = "; ".join(warnings)
        row["errors"] = "; ".join(errors + ["missing RESULT_<package_id>.json"])
        return row
    try:
        result = load_json(result_path)
    except Exception as exc:
        row["status"] = "INVALID"
        row["warnings"] = "; ".join(warnings)
        row["errors"] = "; ".join(errors + [f"invalid JSON: {type(exc).__name__}: {exc}"])
        return row
    if str(result.get("package_id") or "") != package_id:
        errors.append("package_id mismatch")
    if str(result.get("schema_version") or "") not in {"3.3", "3.0"}:
        errors.append("schema_version is not recognized V3.3/V3.0")
    updates = result.get("video_updates")
    if not isinstance(updates, list):
        errors.append("video_updates is not an array")
        updates = []
    got_ids = [str(u.get("video_id") or "") for u in updates if isinstance(u, dict)]
    if len(got_ids) != len(set(got_ids)):
        errors.append("duplicate video_ids in result")
    missing = sorted(set(expected_ids) - set(got_ids))
    extra = sorted(set(got_ids) - set(expected_ids))
    if missing:
        warnings.append("unfinished video_ids: " + ", ".join(missing[:20]))
    if extra:
        errors.append("invented/extra video_ids: " + ", ".join(extra[:20]))
    final_count = 0
    for update in updates:
        if not isinstance(update, dict):
            errors.append("video_update entry is not object")
            continue
        vid = str(update.get("video_id") or "")
        status = str(update.get("processing_status") or update.get("semantic_status") or "").upper()
        if status not in VALID_SEMANTIC_STATUS:
            errors.append(f"{vid}: invalid/missing semantic status")
        else:
            final_count += 1
        features = update.get("features")
        if not isinstance(features, dict):
            errors.append(f"{vid}: features missing/not object")
            continue
        missing_features = sorted(requested_by_id.get(vid, set()) - set(features))
        if missing_features and status not in {"SOURCE_INSUFFICIENT"}:
            errors.append(f"{vid}: missing required features: {', '.join(missing_features[:10])}")
        if status == "PASS_WITH_WARNINGS":
            warnings.append(f"{vid}: PASS_WITH_WARNINGS")
    row["final_semantic_status_count"] = final_count
    row["warnings"] = "; ".join(warnings[:80])
    row["errors"] = "; ".join(errors)
    row["status"] = "VALID" if not errors and not missing else ("PARTIAL" if not errors and missing else "INVALID")
    return row


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate incoming VideoHoarder RESULT_*.json files against grouped packages.")
    ap.add_argument("--exchange", type=Path, default=DEFAULT_EXCHANGE)
    ap.add_argument("--batch-set", default="")
    args = ap.parse_args(argv)
    exchange = args.exchange.resolve()
    incoming = exchange / "incoming" / "results"
    rows = []
    for package_path in package_paths(exchange, args.batch_set):
        package_id = package_path.parent.name
        rows.append(validate_pair(package_path, incoming / f"RESULT_{package_id}.json"))
    summary = {
        "packages": len(rows),
        "valid": sum(1 for r in rows if r["status"] == "VALID"),
        "partial": sum(1 for r in rows if r["status"] == "PARTIAL"),
        "missing": sum(1 for r in rows if r["status"] == "MISSING"),
        "invalid": sum(1 for r in rows if r["status"] == "INVALID"),
        "warnings": sum(1 for r in rows if r["warnings"]),
    }
    incoming.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    csv_path = incoming / f"INCOMING_RESULT_VALIDATION_{stamp}.csv"
    json_path = incoming / f"INCOMING_RESULT_VALIDATION_{stamp}.json"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        fields = ["package_id", "status", "expected_videos", "final_semantic_status_count", "package", "result", "warnings", "errors"]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps({"summary": summary, "items": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"csv={csv_path}")
    print(f"json={json_path}")
    return 1 if summary["missing"] or summary["invalid"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
