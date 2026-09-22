"""Correct known missing/partial media states and refresh generated indexes."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import sys
import traceback
from datetime import datetime
from pathlib import Path


PATH_COLUMNS = (
    "local_folder", "local_video", "subtitle_file", "transcript_original",
    "transcript_clean", "transcript_detailed", "report_html", "transcript_temp",
    "identity_json", "chapters_temp", "chatgpt_summary_file", "comments_file",
    "comments_transcript_file", "comments_meaningful_file", "video_identity_file",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    database = root / "data" / "database" / "video_library.db"
    if not database.is_file():
        raise RuntimeError(f"Database not found: {database}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = root / "maintenance" / "backups" / f"pre_final_state_repair_{stamp}.db"
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(database, backup)

    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    changes = []
    try:
        connection.execute("BEGIN IMMEDIATE")

        missing_id = "IzrVhjZiy2M"
        missing = connection.execute("SELECT * FROM videos WHERE video_id=?", (missing_id,)).fetchone()
        if missing:
            values = {
                "downloaded": 0,
                "final_status": "FAIL",
                "failure_reason": "Media file is missing; redownload required",
                "last_error": "Media file is missing; redownload required",
            }
            cleared = []
            for column in PATH_COLUMNS:
                value = str(missing[column] or "").strip()
                if value and not Path(value).exists():
                    values[column] = ""
                    cleared.append(column)
            assignments = ", ".join(f'"{key}"=?' for key in values)
            connection.execute(
                f"UPDATE videos SET {assignments} WHERE video_id=?",
                [*values.values(), missing_id],
            )
            changes.append({"video_id": missing_id, "state": "missing", "cleared_invalid_paths": cleared})

        partial_id = "KJ-SpnhUURc"
        partial = connection.execute("SELECT * FROM videos WHERE video_id=?", (partial_id,)).fetchone()
        if partial:
            folder = Path(str(partial["local_folder"] or ""))
            partial_files = list(folder.glob("*.part")) if folder.is_dir() else []
            if not partial_files:
                raise RuntimeError(f"Expected partial file was not found for {partial_id}")
            connection.execute(
                """UPDATE videos
                   SET downloaded=0, local_video='', final_status='WARN',
                       failure_reason='Partial download found; resume required', last_error=''
                   WHERE video_id=?""",
                (partial_id,),
            )
            changes.append({
                "video_id": partial_id,
                "state": "partial",
                "partial_files": [str(path) for path in partial_files],
            })

        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"Database integrity check failed: {integrity}")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    os.environ["VLM_LIBRARY_ROOT"] = str(root)
    project = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project))
    from app import app as backend

    outputs = {}
    try:
        outputs["resume_queue"] = str(backend.reconcile_existing_smart_resume_state())
        outputs["video_export"] = str(backend.export_csv())
        outputs["logical_indexes"] = backend.build_library_indexes()
        outputs["phase5"] = backend.phase5_build_all()
        outputs["phase6"] = backend.phase6_build_all()
        outputs["library_health"] = backend.phase1_scan_library()
        outputs["core_audit"] = backend.phase0_core_audit()
        payload = {
            "ok": True,
            "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "database_backup": str(backup),
            "changes": changes,
            "outputs": outputs,
        }
    except Exception as exc:
        payload = {
            "ok": False,
            "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "database_backup": str(backup),
            "changes": changes,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
