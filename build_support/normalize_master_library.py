"""Normalize loose yt-dlp downloads into VideoHoarder's per-video layout.

The command is a dry-run unless --apply is supplied.  It is intentionally
stdlib-only so it can be run by either the build Python or a system Python.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ID_RE = re.compile(r"\[([A-Za-z0-9_-]{11})\]")
DATE_RE = re.compile(r"^(\d{8})\s*-\s*(.*)$")
MEDIA_EXTENSIONS = {
    ".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v", ".mpg", ".mpeg",
}
MAX_DESTINATION_LENGTH = 235


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def is_completed_media(path: Path) -> bool:
    return path.suffix.lower() in MEDIA_EXTENSIONS and not path.name.lower().endswith(".part")


def title_from_name(name: str, video_id: str) -> tuple[str, str]:
    before_id = name.split(f"[{video_id}]", 1)[0].rstrip(" .-_")
    match = DATE_RE.match(before_id)
    if match:
        return match.group(2).strip() or video_id, match.group(1)
    return before_id.strip() or video_id, ""


def safe_folder_name(sample: Path, video_id: str) -> str:
    title, upload_date = title_from_name(sample.name, video_id)
    title = re.sub(r'[<>:"/\\|?*]', " ", title)
    title = re.sub(r"\s+", " ", title).strip(" .")[:34].rstrip(" .")
    prefix = f"{upload_date} - " if upload_date else ""
    return f"{prefix}{title or 'Video'} [{video_id}]"


def shortened_name(path: Path, video_id: str) -> str:
    marker = f"[{video_id}]"
    suffix = path.name.split(marker, 1)[1] if marker in path.name else path.suffix
    if not suffix:
        suffix = path.suffix
    return f"{video_id}{suffix}"


def find_loose_groups(downloads: Path) -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = defaultdict(list)
    if not downloads.is_dir():
        return groups
    for path in downloads.rglob("*"):
        if not path.is_file() or path.parent.name == "_data":
            continue
        # A marker beside a media file means it is already in the normalized layout.
        if (path.parent / "_data" / ".video_id").is_file():
            continue
        match = ID_RE.search(path.name)
        if match:
            groups[match.group(1)].append(path)
    return dict(groups)


def plan_moves(root: Path) -> list[dict]:
    downloads = root / "downloads"
    groups = find_loose_groups(downloads)
    plan: list[dict] = []
    claimed: set[str] = set()

    for video_id, files in sorted(groups.items()):
        parents = {p.parent.resolve() for p in files}
        if len(parents) != 1:
            raise RuntimeError(f"{video_id}: loose files occur in multiple folders: {sorted(map(str, parents))}")
        media = [p for p in files if is_completed_media(p)]
        if len(media) > 1:
            raise RuntimeError(f"{video_id}: expected at most one completed media file, found {len(media)}")

        source_parent = files[0].parent
        sample = media[0] if media else sorted(files, key=lambda p: p.name.lower())[0]
        folder = source_parent / safe_folder_name(sample, video_id)
        moves = []
        for source in sorted(files, key=lambda p: p.name.lower()):
            destination_dir = folder if is_completed_media(source) or source.name.lower().endswith(".part") else folder / "_data"
            destination = destination_dir / source.name
            if len(str(destination)) > MAX_DESTINATION_LENGTH:
                destination = destination_dir / shortened_name(source, video_id)
            key = str(destination).lower()
            if key in claimed:
                raise RuntimeError(f"Destination collision in plan: {destination}")
            claimed.add(key)
            if destination.exists() and source.resolve() != destination.resolve():
                raise RuntimeError(f"Destination already exists: {destination}")
            moves.append({
                "source": str(source),
                "destination": str(destination),
                "bytes": source.stat().st_size,
                "media": is_completed_media(source),
                "partial": source.name.lower().endswith(".part"),
            })

        title, upload_date = title_from_name(sample.name, video_id)
        subtitle_paths = [
            Path(m["destination"]) for m in moves
            if Path(m["destination"]).suffix.lower() in {".vtt", ".srt", ".ass", ".ssa"}
        ]
        plan.append({
            "video_id": video_id,
            "title": title,
            "upload_date": upload_date,
            "channel": source_parent.name,
            "folder": str(folder),
            "media": str(Path(media and next(m["destination"] for m in moves if m["media"]) or "")),
            "subtitle": str(subtitle_paths[0]) if subtitle_paths else "",
            "partial_only": not bool(media),
            "moves": moves,
        })
    return plan


def db_columns(connection: sqlite3.Connection) -> set[str]:
    return {row[1] for row in connection.execute("PRAGMA table_info(videos)")}


def update_database(connection: sqlite3.Connection, item: dict) -> str:
    columns = db_columns(connection)
    video_id = item["video_id"]
    existing = connection.execute(
        "SELECT * FROM videos WHERE video_id=?", (video_id,)
    ).fetchone()
    timestamp = now_iso()
    media = item["media"]

    authoritative = {
        "local_folder": item["folder"],
        "local_video": media,
        "subtitle_file": item["subtitle"],
        "downloaded": 1 if media else 0,
        "final_status": "PASS" if media else "WARN",
        "failure_reason": "" if media else "Partial download found; resume required",
        "last_error": "",
        "last_seen": timestamp,
    }
    fill_if_blank = {
        "platform": "youtube",
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "original_title": item["title"],
        "clean_title": item["title"],
        "channel": item["channel"],
        "upload_date": item["upload_date"],
        "category": "Entertainment",
        "subcategory": "General",
        "status": "active",
        "first_seen": timestamp,
        "downloaded_at": timestamp if media else "",
        "subtitle_source": "youtube" if item["subtitle"] else "",
    }
    authoritative = {k: v for k, v in authoritative.items() if k in columns}
    fill_if_blank = {k: v for k, v in fill_if_blank.items() if k in columns and v != ""}

    if existing:
        names = [description[0] for description in connection.execute(
            "SELECT * FROM videos LIMIT 0"
        ).description]
        current = dict(zip(names, existing))
        values = dict(authoritative)
        for key, value in fill_if_blank.items():
            if current.get(key) in (None, ""):
                values[key] = value
        assignments = ", ".join(f'"{key}"=?' for key in values)
        connection.execute(
            f"UPDATE videos SET {assignments} WHERE video_id=?",
            [*values.values(), video_id],
        )
        return "updated"

    values = {"video_id": video_id, **fill_if_blank, **authoritative}
    names = list(values)
    placeholders = ", ".join("?" for _ in names)
    quoted = ", ".join(f'"{name}"' for name in names)
    connection.execute(
        f"INSERT INTO videos ({quoted}) VALUES ({placeholders})",
        [values[name] for name in names],
    )
    return "inserted"


def apply_plan(root: Path, plan: list[dict]) -> dict:
    database = root / "data" / "database" / "video_library.db"
    if not database.is_file():
        raise FileNotFoundError(f"Database not found: {database}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = root / "maintenance" / "backups" / f"pre_v33_master_rebuild_{stamp}"
    report_dir = root / "maintenance" / "recovery"
    backup_dir.mkdir(parents=True, exist_ok=False)
    report_dir.mkdir(parents=True, exist_ok=True)
    database_backup = backup_dir / database.name
    shutil.copy2(database, database_backup)

    moved: list[tuple[Path, Path]] = []
    created: list[Path] = []
    db_actions: dict[str, str] = {}
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("BEGIN IMMEDIATE")
        for item in plan:
            folder = Path(item["folder"])
            data_dir = folder / "_data"
            for directory in (folder, data_dir):
                if not directory.exists():
                    directory.mkdir(parents=True)
                    created.append(directory)

            for movement in item["moves"]:
                source = Path(movement["source"])
                destination = Path(movement["destination"])
                destination.parent.mkdir(parents=True, exist_ok=True)
                expected_size = movement["bytes"]
                shutil.move(str(source), str(destination))
                moved.append((source, destination))
                if not destination.is_file() or destination.stat().st_size != expected_size:
                    raise RuntimeError(f"Move verification failed: {source} -> {destination}")

            marker = data_dir / ".video_id"
            url_file = data_dir / f"{item['video_id']}.url"
            title_file = data_dir / f"{item['video_id']}.original-title"
            for path, content in (
                (marker, item["video_id"] + "\n"),
                (url_file, f"https://www.youtube.com/watch?v={item['video_id']}\n"),
                (title_file, item["title"] + "\n"),
            ):
                if not path.exists():
                    path.write_text(content, encoding="utf-8")
                    created.append(path)

            db_actions[item["video_id"]] = update_database(connection, item)

        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"Database integrity check failed: {integrity}")
        connection.commit()
    except Exception:
        connection.rollback()
        for source, destination in reversed(moved):
            if destination.exists() and not source.exists():
                source.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(destination), str(source))
        for path in reversed(created):
            try:
                if path.is_file():
                    path.unlink()
                elif path.is_dir() and not any(path.iterdir()):
                    path.rmdir()
            except OSError:
                pass
        raise
    finally:
        connection.close()

    report = {
        "completed_at": now_iso(),
        "root": str(root),
        "database_backup": str(database_backup),
        "groups": len(plan),
        "completed_media": sum(not item["partial_only"] for item in plan),
        "partial_only": sum(item["partial_only"] for item in plan),
        "moved_files": len(moved),
        "moved_bytes": sum(m["bytes"] for item in plan for m in item["moves"]),
        "database_actions": db_actions,
        "items": plan,
    }
    report_path = report_dir / f"normalization_{stamp}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report["report"] = str(report_path)
    return report


def summarize(plan: list[dict]) -> dict:
    lengths = [len(m["destination"]) for item in plan for m in item["moves"]]
    return {
        "groups": len(plan),
        "completed_media": sum(not item["partial_only"] for item in plan),
        "partial_only": sum(item["partial_only"] for item in plan),
        "files": sum(len(item["moves"]) for item in plan),
        "bytes": sum(m["bytes"] for item in plan for m in item["moves"]),
        "max_destination_length": max(lengths, default=0),
        "video_ids": [item["video_id"] for item in plan],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if root == Path(root.anchor):
        raise RuntimeError("Refusing to operate on a drive root")
    if not (root / "data" / "database" / "video_library.db").is_file():
        raise RuntimeError(f"Not a VideoHoarder library: {root}")

    plan = plan_moves(root)
    if args.apply:
        result = apply_plan(root, plan)
        result["mode"] = "applied"
    else:
        result = {"mode": "dry-run", **summarize(plan)}
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
