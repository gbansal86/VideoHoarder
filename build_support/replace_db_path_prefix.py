"""Replace an exact path prefix in every text column of the videos table."""

from __future__ import annotations

import argparse
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--old-prefix", required=True)
    parser.add_argument("--new-prefix", required=True)
    args = parser.parse_args()
    database = args.database.resolve()
    backup = database.with_name(f"{database.stem}.pre_video_folder_move_{datetime.now():%Y%m%d_%H%M%S}.db")
    shutil.copy2(database, backup)
    con = sqlite3.connect(database)
    try:
        columns = [row[1] for row in con.execute("PRAGMA table_info(videos)")]
        con.execute("BEGIN IMMEDIATE")
        changed = 0
        for column in columns:
            result = con.execute(
                f'UPDATE videos SET "{column}"=REPLACE("{column}", ?, ?) '
                f'WHERE typeof("{column}")="text" AND "{column}" LIKE ?',
                (args.old_prefix, args.new_prefix, args.old_prefix + "%"),
            )
            changed += max(0, result.rowcount)
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("Database integrity check failed")
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()
    print(f"BACKUP={backup}")
    print(f"UPDATED_ROWS={changed}")


if __name__ == "__main__":
    main()
