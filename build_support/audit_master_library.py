"""Produce a strict, machine-readable post-rebuild audit."""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from pathlib import Path


MEDIA_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v", ".mpg", ".mpeg"}


def canonical(path: str | Path) -> str:
    return str(Path(path).resolve()).casefold()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--app-root", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    downloads = root / "downloads"
    database = root / "data" / "database" / "video_library.db"
    connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        "SELECT video_id, downloaded, final_status, local_folder, local_video FROM videos"
    ).fetchall()
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    connection.close()

    physical_media = [
        path for path in downloads.rglob("*")
        if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS
        and not path.name.lower().endswith(".part")
    ]
    partials = [path for path in downloads.rglob("*.part") if path.is_file()]
    markers = list(downloads.rglob(".video_id"))
    marker_ids = {}
    for path in markers:
        value = path.read_text(encoding="utf-8", errors="ignore").strip()
        marker_ids[value] = marker_ids.get(value, 0) + 1

    physical_by_path = {canonical(path): path for path in physical_media}
    db_media_values = [str(row["local_video"] or "") for row in rows if str(row["local_video"] or "").strip()]
    db_valid_paths = [path for path in db_media_values if Path(path).is_file()]
    db_valid_canonical = [canonical(path) for path in db_valid_paths]
    db_path_counts = Counter(db_valid_canonical)
    referenced = set(db_valid_canonical)
    orphan_media = [str(path) for key, path in physical_by_path.items() if key not in referenced]
    external_media = [path for path in db_valid_paths if not canonical(path).startswith(canonical(downloads) + "\\")]
    missing_db_paths = [
        {"video_id": row["video_id"], "path": row["local_video"]}
        for row in rows if str(row["local_video"] or "").strip() and not Path(row["local_video"]).is_file()
    ]
    missing_downloaded = [
        row["video_id"] for row in rows
        if row["downloaded"] and not (row["local_video"] and Path(row["local_video"]).is_file())
    ]
    valid_media_not_pass = [
        {"video_id": row["video_id"], "status": row["final_status"], "downloaded": row["downloaded"]}
        for row in rows
        if row["local_video"] and Path(row["local_video"]).is_file()
        and (row["final_status"] != "PASS" or not row["downloaded"])
    ]
    invalid_folders = [
        {"video_id": row["video_id"], "path": row["local_folder"]}
        for row in rows if str(row["local_folder"] or "").strip() and not Path(row["local_folder"]).is_dir()
    ]
    db_ids = {row["video_id"] for row in rows}
    unresolved_markers = sorted(value for value in marker_ids if value not in db_ids)
    duplicate_markers = {key: count for key, count in marker_ids.items() if count > 1}
    duplicate_db_paths = {key: count for key, count in db_path_counts.items() if count > 1}

    required = {
        "knowledge_center": root / "VIDEO_LIBRARY_KNOWLEDGE_CENTER.html",
        "logical_index": root / "indexes" / "index.html",
        "video_export": root / "data" / "exports" / "video_list.csv",
        "search_index": root / "data" / "knowledge" / "search" / "library_search_index.jsonl",
        "chunk_index": root / "data" / "knowledge" / "phase6" / "chunks" / "chunk_index.jsonl",
        "embeddings": root / "data" / "knowledge" / "phase6" / "embeddings" / "chunk_embeddings.jsonl",
        "library_health": root / "maintenance" / "audits" / "library_health.csv",
        "resume_queue": root / "logs" / "smart_resume_queue.txt",
    }
    pointer = args.app_root / "library_root.txt"
    pointer_value = pointer.read_text(encoding="utf-8", errors="strict").strip() if pointer.is_file() else ""
    required_state = {
        name: {"exists": path.is_file(), "bytes": path.stat().st_size if path.is_file() else 0, "path": str(path)}
        for name, path in required.items()
    }

    checks = {
        "database_integrity": integrity == "ok",
        "every_physical_media_referenced_once": not orphan_media and len(referenced & set(physical_by_path)) == len(physical_media),
        "no_duplicate_database_media_paths": not duplicate_db_paths,
        "no_external_media_references": not external_media,
        "no_unresolved_markers": not unresolved_markers,
        "no_duplicate_markers": not duplicate_markers,
        "no_invalid_database_folders": not invalid_folders,
        "required_rebuild_outputs_exist": all(item["exists"] and item["bytes"] > 0 for item in required_state.values()),
        "gui_points_to_master_root": canonical(pointer_value) == canonical(root),
    }
    result = {
        "ok": all(checks.values()),
        "checks": checks,
        "database": {
            "integrity": integrity,
            "rows": len(rows),
            "status": dict(Counter(str(row["final_status"] or "blank") for row in rows)),
            "nonempty_media_paths": len(db_media_values),
            "valid_media_paths": len(db_valid_paths),
            "missing_media_paths": missing_db_paths,
            "downloaded_without_media": missing_downloaded,
            "valid_media_not_pass": valid_media_not_pass,
            "invalid_folders": invalid_folders,
            "duplicate_valid_media_paths": duplicate_db_paths,
        },
        "physical": {
            "completed_media": len(physical_media),
            "completed_media_bytes": sum(path.stat().st_size for path in physical_media),
            "partial_files": len(partials),
            "partial_bytes": sum(path.stat().st_size for path in partials),
            "markers": len(markers),
            "unique_marker_ids": len(marker_ids),
            "orphan_media": orphan_media,
            "unresolved_markers": unresolved_markers,
            "duplicate_markers": duplicate_markers,
        },
        "app": {"root": str(args.app_root.resolve()), "library_pointer": pointer_value},
        "outputs": required_state,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
