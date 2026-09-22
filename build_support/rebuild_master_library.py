"""Run VideoHoarder's complete recovery/rebuild against a selected library."""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    if root == Path(root.anchor):
        raise RuntimeError("Refusing to use a drive root as the library")
    database = root / "data" / "database" / "video_library.db"
    if not database.is_file():
        raise RuntimeError(f"Database not found: {database}")

    os.environ["VLM_LIBRARY_ROOT"] = str(root)
    project = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project))
    from app import app as backend  # Import only after setting the library root.

    started = datetime.now().astimezone().isoformat(timespec="seconds")
    try:
        result = backend.one_click_recover_rebuild_everything()
        payload = {"ok": True, "started_at": started, "result": result}
    except Exception as exc:
        payload = {
            "ok": False,
            "started_at": started,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }
    payload["finished_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
