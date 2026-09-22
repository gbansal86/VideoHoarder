#!/usr/bin/env python3
"""V3.3.4 status-only scanner for VideoHoarder ChatGPT batch packages.

This script intentionally does not generate summaries, tags, chapters, recipes,
named items, or any other semantic intelligence. V3.3.4 requires ChatGPT/manual
semantic processing for that work. The script only reports which packages have
matching RESULT_*.json files and which still need processing.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path


DEFAULT_EXCHANGE = Path(os.environ.get("VIDEOHOARDER_EXCHANGE") or (Path.cwd() / "data" / "chatgpt" / "exchange"))


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def package_paths(exchange: Path, batch_set: str = "") -> list[Path]:
    root = exchange / "outgoing" / "group_similar" / "batches"
    if batch_set:
        root = root / batch_set
        return sorted(root.glob("packages/*/CHATGPT_PACKAGE.json"))
    return sorted(root.glob("*/packages/*/CHATGPT_PACKAGE.json"))


def build_result(*_args, **_kwargs) -> dict:
    raise RuntimeError(
        "V3.3.4 forbids local semantic placeholder generation; use status-only "
        "reporting and ChatGPT for semantic results."
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Report missing VideoHoarder RESULT_*.json files.")
    ap.add_argument("--exchange", type=Path, default=DEFAULT_EXCHANGE)
    ap.add_argument("--batch-set", default="", help="Optional batch set folder under outgoing/group_similar/batches")
    ap.add_argument("--mode", choices=["status-only"], default="status-only")
    ap.add_argument("--force", action="store_true", help="Accepted for old command compatibility; ignored.")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    exchange = args.exchange.resolve()
    incoming = exchange / "incoming" / "results"
    incoming.mkdir(parents=True, exist_ok=True)
    paths = package_paths(exchange, args.batch_set)
    if args.limit:
        paths = paths[: args.limit]

    report = {
        "exchange": str(exchange),
        "mode": "status-only",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "packages_seen": len(paths),
        "completed": 0,
        "missing": 0,
        "failed": 0,
        "warnings": ["V3.3.4 status-only mode: this script does not generate semantic placeholders."],
        "items": [],
    }
    for path in paths:
        try:
            package = load_json(path)
            package_id = str(package.get("package_id") or path.parent.name)
            out = incoming / f"RESULT_{package_id}.json"
            item = {"package_id": package_id, "package": str(path), "expected_result": str(out), "videos": len(package.get("videos") or [])}
            if out.exists():
                report["completed"] += 1
                item.update({"status": "RESULT_EXISTS", "result": str(out)})
            else:
                report["missing"] += 1
                item.update({"status": "MISSING_RESULT"})
            report["items"].append(item)
        except Exception as exc:
            report["failed"] += 1
            report["items"].append({"package": str(path), "status": "FAILED", "message": f"{type(exc).__name__}: {exc}"})

    report_path = incoming / f"LOCAL_BATCH_PROCESS_REPORT_{time.strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("packages_seen", "completed", "missing", "failed")}, indent=2))
    print(f"report={report_path}")
    return 1 if report["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
