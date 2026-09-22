"""Server/database-side Library pagination.

The native Library previously materialized as many as 10,000 merged rows and
then paged them in Qt.  This module keeps count/filter/sort/page selection in
SQLite and returns only the requested page.  Phase-5 search scores can be
provided as a temporary relation so semantic/index search and live SQLite state
remain compatible without an IN-clause size limit.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 500


def _safe_page(value: Any) -> int:
    try:
        return max(1, int(value))
    except Exception:
        return 1


def _safe_page_size(value: Any) -> int:
    try:
        return max(1, min(MAX_PAGE_SIZE, int(value)))
    except Exception:
        return DEFAULT_PAGE_SIZE


def _column_expr(columns: set[str], name: str, fallback: str = "''") -> str:
    return f'v."{name}"' if name in columns else fallback


def paginate_library(
    connection,
    columns: Iterable[str],
    *,
    query: str = "",
    filter_name: str = "all",
    sort_by: str = "downloaded_desc",
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    search_scores: Mapping[str, float] | None = None,
    category: str = "",
    channel: str = "",
    path_exists: Callable[[str], bool] | None = None,
) -> dict[str, Any]:
    """Return one authoritative Library page and its real total count.

    ``search_scores`` is normally produced by the Phase-5 search index.  Scores
    are loaded into a SQLite TEMP table, avoiding SQLite variable limits and
    allowing pagination/counting to remain database-side even for >10k hits.
    Live title/channel/category matching is ORed with that relation so videos
    missing from a stale index are still discoverable.
    """

    cols = {str(c) for c in columns}
    page = _safe_page(page)
    page_size = _safe_page_size(page_size)
    q = str(query or "").strip().lower()
    filter_key = str(filter_name or "all").strip().lower()
    sort_key = str(sort_by or "downloaded_desc").strip().lower()
    category = str(category or "").strip()
    channel = str(channel or "").strip()

    if path_exists is None:
        path_exists = lambda value: Path(str(value or "")).exists()
    connection.create_function("vh_path_exists", 1, lambda value: 1 if value and path_exists(str(value)) else 0)

    connection.execute("DROP TABLE IF EXISTS temp.vh_library_search")
    connection.execute("CREATE TEMP TABLE vh_library_search(video_id TEXT PRIMARY KEY, score REAL NOT NULL)")
    if search_scores:
        connection.executemany(
            "INSERT OR REPLACE INTO vh_library_search(video_id, score) VALUES(?, ?)",
            [(str(video_id), float(score or 0.0)) for video_id, score in search_scores.items() if str(video_id or "").strip()],
        )

    video_id = _column_expr(cols, "video_id")
    original_title = _column_expr(cols, "original_title")
    clean_title = _column_expr(cols, "clean_title")
    title_expr = f"COALESCE(NULLIF({clean_title},''), NULLIF({original_title},''), {video_id})"
    channel_expr = _column_expr(cols, "channel")
    category_expr = _column_expr(cols, "category", "'Other'")
    subcategory_expr = _column_expr(cols, "subcategory", "'General'")
    source_category_expr = _column_expr(cols, "source_category", _column_expr(cols, "youtube_category_name"))
    downloaded_expr = _column_expr(cols, "downloaded_at")
    favorite_expr = _column_expr(cols, "favorite", "0")
    watched_expr = _column_expr(cols, "watched", "0")
    archived_expr = _column_expr(cols, "archived", "0")
    status_expr = _column_expr(cols, "final_status")
    local_video_expr = _column_expr(cols, "local_video")
    thumbnail_expr = _column_expr(cols, "thumbnail_url")
    url_expr = _column_expr(cols, "url")

    where = [f"COALESCE({archived_expr},0)=0"]
    params: list[Any] = []

    if q:
        like = f"%{q}%"
        live_haystack = (
            "LOWER(COALESCE(" + video_id + ",'') || ' ' || COALESCE(" + title_expr + ",'') || ' ' || "
            "COALESCE(" + channel_expr + ",'') || ' ' || COALESCE(" + category_expr + ",'') || ' ' || "
            "COALESCE(" + subcategory_expr + ",''))"
        )
        where.append(f"(s.video_id IS NOT NULL OR {live_haystack} LIKE ?)")
        params.append(like)

    if category:
        where.append(f"COALESCE({category_expr},'')=?")
        params.append(category)
    if channel:
        where.append(f"COALESCE({channel_expr},'')=?")
        params.append(channel)

    if filter_key == "downloaded":
        where.append(f"vh_path_exists({local_video_expr})=1")
    elif filter_key == "failed":
        where.append(f"UPPER(COALESCE({status_expr},''))='FAIL'")
    elif filter_key == "favorites":
        where.append(f"COALESCE({favorite_expr},0)<>0")
    elif filter_key == "unwatched":
        where.append(f"COALESCE({watched_expr},0)=0")
    elif filter_key == "latest":
        cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        where.append(f"COALESCE({downloaded_expr},'')>=?")
        params.append(cutoff)

    where_sql = " AND ".join(where)
    join_sql = f"FROM videos v LEFT JOIN vh_library_search s ON s.video_id={video_id}"

    total = int(connection.execute(f"SELECT COUNT(*) {join_sql} WHERE {where_sql}", params).fetchone()[0] or 0)
    max_page = max(1, (total + page_size - 1) // page_size)
    page = min(page, max_page)
    offset = (page - 1) * page_size

    if q:
        prefix = "COALESCE(s.score,0) DESC, "
    else:
        prefix = ""
    if sort_key in {"downloaded_asc", "oldest"}:
        order_sql = prefix + f"COALESCE({downloaded_expr},'9999') ASC, v.rowid DESC"
    elif sort_key == "title":
        order_sql = prefix + f"LOWER(COALESCE({title_expr},'')) ASC, v.rowid DESC"
    elif sort_key == "channel":
        order_sql = prefix + f"LOWER(COALESCE({channel_expr},'')) ASC, LOWER(COALESCE({title_expr},'')) ASC"
    elif sort_key == "category":
        order_sql = prefix + f"LOWER(COALESCE({category_expr},'')) ASC, LOWER(COALESCE({subcategory_expr},'')) ASC, LOWER(COALESCE({title_expr},'')) ASC"
    else:
        order_sql = prefix + f"COALESCE({downloaded_expr},'') DESC, v.rowid DESC"

    select_sql = f"""
        SELECT
            {video_id} AS video_id,
            {title_expr} AS title,
            {channel_expr} AS channel,
            {category_expr} AS category,
            {subcategory_expr} AS subcategory,
            {source_category_expr} AS source_category,
            {downloaded_expr} AS downloaded_at,
            COALESCE({favorite_expr},0) AS favorite,
            COALESCE({watched_expr},0) AS watched,
            {status_expr} AS status,
            {local_video_expr} AS local_video,
            {thumbnail_expr} AS thumbnail_url,
            {url_expr} AS url,
            COALESCE(s.score,0) AS search_score
        {join_sql}
        WHERE {where_sql}
        ORDER BY {order_sql}
        LIMIT ? OFFSET ?
    """
    rows = connection.execute(select_sql, [*params, page_size, offset]).fetchall()
    names = [d[0] for d in connection.execute(select_sql, [*params, 0, 0]).description] if rows else [
        "video_id","title","channel","category","subcategory","source_category","downloaded_at",
        "favorite","watched","status","local_video","thumbnail_url","url","search_score"
    ]

    items: list[dict[str, Any]] = []
    for row in rows:
        item = dict(zip(names, row))
        local_video = str(item.get("local_video") or "")
        item["has_media"] = bool(local_video and path_exists(local_video))
        item["favorite"] = int(item.get("favorite") or 0)
        item["watched"] = int(item.get("watched") or 0)
        items.append(item)

    return {
        "ok": True,
        "page": page,
        "page_size": page_size,
        "total": total,
        "max_page": max_page,
        "items": items,
    }
