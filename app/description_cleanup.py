from __future__ import annotations

import html as _html
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

try:
    from .description_parser import parse_description
except ImportError:  # pragma: no cover
    from description_parser import parse_description


CANONICAL_RAW = "description.txt_raw"
CANONICAL_TEXT = "description.txt"
CANONICAL_HTML = "description.html"


def _text(value: Any) -> str:
    return str(value or "").strip()


def _roots(folder: str | Path) -> list[Path]:
    folder = Path(folder)
    data = folder / "_data"
    roots = []
    if data.exists() and data.is_dir():
        roots.append(data)
    roots.append(folder)
    return roots


def _normal_description_candidates(folder: str | Path, video_id: str) -> list[Path]:
    """Return retained yt-dlp description artifacts in deterministic priority order."""
    video_id = _text(video_id)
    candidates: list[tuple[int, float, Path]] = []
    seen: set[str] = set()
    for root_index, root in enumerate(_roots(folder)):
        if not root.exists():
            continue
        patterns = [f"{video_id}.description", f"{video_id}*.description"] if video_id else []
        patterns.append("*.description")
        for pattern_index, pattern in enumerate(patterns):
            for path in root.glob(pattern):
                if not path.is_file():
                    continue
                low = path.name.lower()
                if low in {CANONICAL_RAW.lower(), CANONICAL_TEXT.lower()}:
                    continue
                key = str(path.resolve())
                if key in seen:
                    continue
                seen.add(key)
                exact = 0 if video_id and path.name == f"{video_id}.description" else 1
                id_match = 0 if video_id and path.name.startswith(video_id) else 1
                score = root_index * 100 + exact * 10 + id_match * 3 + pattern_index
                candidates.append((score, -path.stat().st_mtime, path))
    return [x[2] for x in sorted(candidates, key=lambda x: (x[0], x[1], x[2].name.lower()))]


def select_description_source(folder: str | Path, video_id: str, db_description: str = "") -> dict[str, Any]:
    """Select local description source without any network access."""
    roots = _roots(folder)
    primary = roots[0]
    raw_path = primary / CANONICAL_RAW
    if raw_path.is_file() and raw_path.stat().st_size > 0:
        return {"kind": "canonical_raw", "path": raw_path, "text": raw_path.read_text(encoding="utf-8", errors="replace")}

    # Backward compatibility: older cleanup builds wrote canonical description
    # artifacts in the video root. If _data exists, treat the old root raw file
    # as source evidence before falling back to yt-dlp *.description artifacts.
    # It will be copied to _data and removed only after the new canonical files
    # have been validated successfully.
    folder_path = Path(folder)
    legacy_root_raw = folder_path / CANONICAL_RAW
    if primary != folder_path and legacy_root_raw.is_file() and legacy_root_raw.stat().st_size > 0:
        return {"kind": "legacy_root_raw", "path": legacy_root_raw, "text": legacy_root_raw.read_text(encoding="utf-8", errors="replace")}

    candidates = _normal_description_candidates(folder, video_id)
    if candidates:
        path = candidates[0]
        return {"kind": "yt_dlp_description", "path": path, "text": path.read_text(encoding="utf-8", errors="replace")}
    if _text(db_description):
        return {"kind": "database", "path": None, "text": str(db_description)}
    return {"kind": "missing", "path": None, "text": ""}


def render_description(data: Mapping[str, Any]) -> str:
    """Render parsed description into the canonical readable text representation."""
    out: list[str] = []
    title = _text(data.get("title"))
    if title:
        out.append(title)
    intro = [_text(x) for x in data.get("introduction", []) if _text(x)]
    if intro:
        out += ["", "Introduction", ""] + intro
    chapters = data.get("chapters", []) or []
    if chapters:
        out += ["", "Chapters", ""]
        for chapter in chapters:
            ts, text = _text(chapter.get("timestamp")), _text(chapter.get("text"))
            out.append(f"{ts} - {text}" if ts and text else (ts or text))
    outline = data.get("outline_items", []) or []
    if outline:
        out += ["", "Outline", ""]
        out.extend(_text(x.get("text")) for x in outline if _text(x.get("text")))
    for block in (data.get("section_blocks", []) or [])[1:]:
        header = _text(block.get("header_original") or block.get("header"))
        if not header:
            continue
        out += ["", header, ""]
        header_content = _text(block.get("header_content"))
        if header_content and header_content.lower() not in header.lower():
            out.append(header_content)
        emitted: set[str] = set()
        for rec in block.get("content_lines", []) or []:
            text = _text(rec.get("text"))
            inline_duplicate = bool(header_content and text == header_content and text.lower() in header.lower())
            if text and text not in emitted and not inline_duplicate:
                out.append(text); emitted.add(text)
        for item in block.get("items", []) or []:
            label = _text(item.get("label")); urls = [str(x) for x in item.get("urls", []) if x]
            if label and urls:
                if len(urls) == 1:
                    out.append(f"{label} - {urls[0]}")
                else:
                    out.append(label); out.extend(urls)
            elif urls:
                out.extend(urls)
            elif label:
                out.append(label)
    represented: list[str] = []
    for block in (data.get("section_blocks", []) or [])[1:]:
        for item in block.get("items", []) or []:
            represented.extend(str(x) for x in item.get("urls", []) if x)
    represented_counts = Counter(represented)
    remaining = []
    for rec in data.get("urls", []) or []:
        url = str(rec.get("url") or "")
        if represented_counts.get(url, 0):
            represented_counts[url] -= 1
        else:
            remaining.append(rec)
    if remaining:
        out += ["", "Other preserved links", ""]
        for rec in remaining:
            original, url = _text(rec.get("original_text")), _text(rec.get("url"))
            out.append(original if original and original != url else url)
    cleaned: list[str] = []
    blank = False
    for line in out:
        line = str(line).rstrip()
        if not line:
            if cleaned and not blank:
                cleaned.append("")
            blank = True
        else:
            cleaned.append(line); blank = False
    return "\n".join(cleaned).strip() + "\n"


def render_html(description_text: str, title: str) -> str:
    url_re = re.compile(r"(?P<url>https?://[^\s<]+|www\.[^\s<]+)", re.I)
    def linkify(text: str) -> str:
        escaped = _html.escape(text)
        def repl(match):
            shown = match.group("url"); trailing = ""
            while shown and shown[-1] in ".,);]":
                trailing = shown[-1] + trailing; shown = shown[:-1]
            href = shown if shown.lower().startswith(("http://", "https://")) else "https://" + shown
            return f'<a href="{_html.escape(href, quote=True)}" target="_blank" rel="noopener noreferrer">{shown}</a>{trailing}'
        return url_re.sub(repl, escaped)
    body = []
    for line in description_text.splitlines():
        stripped = line.strip()
        if not stripped:
            body.append('<div class="spacer"></div>')
        elif stripped in {"Introduction", "Chapters", "Outline", "Other preserved links"}:
            body.append(f"<h2>{_html.escape(stripped)}</h2>")
        elif re.match(r"^\d{1,2}:\d{2}(?::\d{2})?\s*[-:–—]", stripped):
            body.append(f'<div class="chapter">{linkify(stripped)}</div>')
        else:
            body.append(f"<p>{linkify(stripped)}</p>")
    safe_title = _html.escape(title or "Description")
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{safe_title}</title><style>body{{font-family:Arial,sans-serif;max-width:1000px;margin:32px auto;padding:0 20px;line-height:1.55;color:#20242a}}h1{{font-size:28px;margin-bottom:28px}}h2{{font-size:20px;margin-top:28px;border-bottom:1px solid #ddd;padding-bottom:6px}}p{{margin:7px 0;white-space:pre-wrap}}.chapter{{margin:7px 0;padding:7px 10px;background:#f5f6f7;border-radius:6px}}.spacer{{height:8px}}a{{word-break:break-all}}</style></head><body><h1>{safe_title}</h1>{''.join(body)}</body></html>'''


def _url_occurrence_check(parsed: Mapping[str, Any], rendered: str) -> list[str]:
    source_counts = Counter(str(x.get("url") or "") for x in parsed.get("urls", []) or [] if x.get("url"))
    missing: list[str] = []
    for url, count in source_counts.items():
        if rendered.count(url) < count:
            missing.append(f"{url} (expected {count}, rendered {rendered.count(url)})")
    return missing



def _cleanup_legacy_root_description_artifacts(folder: Path, target_dir: Path) -> dict[str, Any]:
    """Remove obsolete root-level canonical description copies after validation.

    Canonical description artifacts belong under ``_data`` when that directory
    exists. The retained yt-dlp ``*.description`` files and ``metadata.info.json``
    are deliberately outside this cleanup and are never deleted here.
    """
    result = {"found": 0, "deleted": 0, "preserved": 0, "files": []}
    if target_dir == folder:
        return result

    required = [target_dir / CANONICAL_RAW, target_dir / CANONICAL_TEXT, target_dir / CANONICAL_HTML]
    if not all(path.is_file() and path.stat().st_size > 0 for path in required):
        result["preserved"] = sum(1 for name in (CANONICAL_RAW, CANONICAL_TEXT, CANONICAL_HTML) if (folder / name).exists())
        return result

    for name in (CANONICAL_RAW, CANONICAL_TEXT, CANONICAL_HTML):
        legacy = folder / name
        if not legacy.exists():
            continue
        result["found"] += 1
        try:
            legacy.unlink()
            result["deleted"] += 1
            result["files"].append({"path": str(legacy), "action": "DELETED"})
        except Exception as exc:
            result["preserved"] += 1
            result["files"].append({"path": str(legacy), "action": "PRESERVED", "error": f"{type(exc).__name__}: {exc}"})
    return result

def cleanup_video_description(
    folder: str | Path,
    video_id: str,
    *,
    db_description: str = "",
    con: sqlite3.Connection | None = None,
) -> dict[str, Any]:
    """Create/update canonical description artifacts from local data only.

    The retained yt-dlp `*.description` file is never renamed or deleted.
    `description.txt_raw` is immutable once created. Writes are atomic and DB is
    updated only after URL-preservation validation passes.
    """
    folder = Path(folder)
    roots = _roots(folder); target_dir = roots[0]
    target_dir.mkdir(parents=True, exist_ok=True)
    source = select_description_source(folder, video_id, db_description)
    if source["kind"] == "missing":
        return {"ok": True, "status": "SKIPPED", "reason": "description missing", "video_id": str(video_id)}
    raw_path = target_dir / CANONICAL_RAW
    if not raw_path.exists():
        raw_temp = target_dir / (CANONICAL_RAW + ".new")
        raw_temp.write_text(str(source["text"]), encoding="utf-8")
        raw_temp.replace(raw_path)
    raw_text = raw_path.read_text(encoding="utf-8", errors="replace")
    parsed = parse_description(raw_text)
    rendered = render_description(parsed)
    missing = _url_occurrence_check(parsed, rendered)
    if missing:
        return {"ok": False, "status": "ERROR", "video_id": str(video_id), "reason": "URL preservation safety check failed", "missing_urls": missing}
    text_path = target_dir / CANONICAL_TEXT
    html_path = target_dir / CANONICAL_HTML
    text_temp = target_dir / (CANONICAL_TEXT + ".new")
    html_temp = target_dir / (CANONICAL_HTML + ".new")
    text_temp.write_text(rendered, encoding="utf-8")
    html_temp.write_text(render_html(rendered, _text(parsed.get("title")) or folder.name), encoding="utf-8")
    text_temp.replace(text_path); html_temp.replace(html_path)

    # Only after all three canonical _data artifacts exist and are non-empty do
    # we remove obsolete root-level description.txt[_raw]/description.html files.
    # metadata.info.json and retained *.description source files are not touched.
    legacy_cleanup = _cleanup_legacy_root_description_artifacts(folder, target_dir)
    if legacy_cleanup.get("preserved"):
        return {
            "ok": False,
            "status": "ERROR",
            "video_id": str(video_id),
            "reason": "canonical description created but one or more legacy root description artifacts could not be removed",
            "legacy_root_cleanup": legacy_cleanup,
        }

    if con is not None:
        cols = {str(r[1]) for r in con.execute("PRAGMA table_info(videos)").fetchall()}
        if "description" in cols:
            con.execute("UPDATE videos SET description=? WHERE video_id=?", (rendered, str(video_id)))
            con.commit()
    return {
        "ok": True,
        "status": "COMPLETE",
        "video_id": str(video_id),
        "source_kind": source["kind"],
        "source": str(source["path"] or "database"),
        "raw_backup": str(raw_path),
        "cleaned_description": str(text_path),
        "html": str(html_path),
        "url_count": len(parsed.get("urls", []) or []),
        "duplicate_url_group_count": len(parsed.get("duplicate_url_groups", []) or []),
        "chapter_count": len(parsed.get("chapters", []) or []),
        "section_count": len(parsed.get("sections", []) or []),
        "legacy_root_cleanup": legacy_cleanup,
        "description": rendered,
    }
