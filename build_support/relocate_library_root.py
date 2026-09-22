"""Safely relocate VideoHoarder database paths to a new library root."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-root", required=True, type=Path)
    parser.add_argument("--new-root", required=True, type=Path)
    args = parser.parse_args()

    old_root = args.old_root
    new_root = args.new_root.resolve()
    if new_root == Path(new_root.anchor):
        raise RuntimeError("Refusing to use a drive root")
    database = new_root / "data" / "database" / "video_library.db"
    if not database.is_file():
        raise FileNotFoundError(database)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = new_root / "maintenance" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / f"pre_root_relocation_{stamp}.db"
    shutil.copy2(database, backup)

    old_text = str(old_root).rstrip("\\/")
    new_text = str(new_root).rstrip("\\/")
    connection = sqlite3.connect(database)
    changed: dict[str, int] = {}
    try:
        columns = [row[1] for row in connection.execute("PRAGMA table_info(videos)")]
        connection.execute("BEGIN IMMEDIATE")
        for column in columns:
            # SQLite's typeof keeps numeric/status fields out of the path rewrite.
            sql = (
                f'UPDATE videos SET "{column}"=REPLACE("{column}", ?, ?) '
                f'WHERE typeof("{column}")="text" AND "{column}" LIKE ?'
            )
            result = connection.execute(sql, (old_text, new_text, old_text + "%"))
            if result.rowcount:
                changed[column] = result.rowcount
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {integrity}")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    # utf-8 without a BOM keeps both packaged and source Python launchers happy.
    (new_root / "library_root.txt").write_text(new_text, encoding="utf-8")
    report = {
        "old_root": old_text,
        "new_root": new_text,
        "database": str(database),
        "backup": str(backup),
        "changed_columns": changed,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
