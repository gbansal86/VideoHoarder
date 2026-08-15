"""Run the reusable URL refresh workflow against the portable library."""

from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--library-root", required=True, type=Path)
    parser.add_argument("--video-root", required=True, type=Path)
    parser.add_argument("--urls", required=True, type=Path)
    parser.add_argument("--api-key", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    args = parser.parse_args()
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    os.environ["VLM_LIBRARY_ROOT"] = str(args.library_root.resolve())
    os.environ["VLM_VIDEO_LIBRARY"] = str(args.video_root.resolve())
    os.environ["VLM_URLS_FILE"] = str(args.urls.resolve())
    os.environ["VLM_API_KEY_FILE"] = str(args.api_key.resolve())
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from app import app
    try:
        payload = {"ok": True, "started_at": datetime.now().astimezone().isoformat(timespec="seconds"), "result": app.refresh_library_from_urls()}
    except Exception as exc:
        payload = {"ok": False, "error": str(exc), "traceback": traceback.format_exc()}
    payload["finished_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
