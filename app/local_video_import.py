"""Import user-owned local video files without treating them as YouTube downloads.

The scan is read-only. Import is opt-in; reference mode never changes source files.
No network requests or AI/transcription calls occur in this module.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Callable

VIDEO_EXTENSIONS = frozenset({'.mp4', '.mkv', '.webm', '.mov', '.m4v', '.avi', '.wmv', '.flv', '.mpg', '.mpeg', '.ts', '.mts', '.m2ts', '.3gp', '.ogv'})
MAX_IMPORT_FILES = 10000


def source_paths(raw: str) -> list[Path]:
    """One full file/folder path per line; spaces and drive letters are preserved."""
    paths = [Path(x.strip().strip('"')) for x in str(raw or '').splitlines() if x.strip()]
    if not paths:
        raise ValueError('Enter at least one existing video file or folder, one path per line.')
    for path in paths:
        if not path.exists():
            raise ValueError(f'Source path not found: {path}')
    return paths


def discover(raw: str, *, limit: int = MAX_IMPORT_FILES) -> list[Path]:
    """Deterministic enumeration; never follow directory/file symlinks."""
    found: dict[str, Path] = {}
    for source in source_paths(raw):
        if source.is_symlink():
            continue
        candidates = [source] if source.is_file() else source.rglob('*')
        for p in candidates:
            if p.is_symlink() or not p.is_file() or p.suffix.lower() not in VIDEO_EXTENSIONS:
                continue
            if p.stat().st_size <= 0:
                continue
            normalized = str(p.resolve()).casefold() if os.name == 'nt' else str(p.resolve())
            found[normalized] = p.resolve()
            if len(found) > limit:
                raise ValueError(f'Scan exceeds {limit:,} videos. Select smaller folders.')
    return [found[key] for key in sorted(found)]


def local_video_id(path: Path) -> str:
    """Stable ID for the same original file path, independent of mtime and metadata."""
    identity = str(path.resolve())
    if os.name == 'nt':
        identity = identity.casefold()
    return 'local_' + hashlib.sha256(identity.encode('utf-8')).hexdigest()[:24]


def matching_sidecars(path: Path) -> dict[str, Path]:
    """Associate exact-stem subtitle/transcript files; do not adopt neighbor videos' data."""
    result: dict[str, Path] = {}
    for extension in ('.srt', '.vtt'):
        for candidate in (path.with_suffix(extension), path.with_name(path.stem + '.en' + extension)):
            if candidate.is_file() and not candidate.is_symlink() and candidate.stat().st_size:
                result.setdefault('subtitle', candidate)
                break
    for suffix in ('.transcript.txt', '.transcript_timestamped.txt', '.timestamped.txt'):
        candidate = path.with_name(path.stem + suffix)
        if candidate.is_file() and not candidate.is_symlink() and candidate.stat().st_size:
            result['transcript'] = candidate
            break
    return result


def probe(path: Path, ffprobe: str | None = None) -> dict[str, object]:
    """Metadata only; no transcoding/download. FFprobe is optional."""
    exe = ffprobe or shutil.which('ffprobe')
    if not exe:
        return {}
    try:
        done = subprocess.run([str(exe), '-v', 'error', '-show_entries',
            'format=duration:stream=codec_type,width,height', '-of', 'json', str(path)],
            capture_output=True, text=True, timeout=15, check=False)
        if done.returncode:
            return {}
        data = json.loads(done.stdout)
        stream = next((x for x in data.get('streams', []) if x.get('codec_type') == 'video'), {})
        duration = float((data.get('format') or {}).get('duration') or 0)
        return {'duration_seconds': max(0.0, duration), 'width': int(stream.get('width') or 0),
                'height': int(stream.get('height') or 0)}
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return {}


def _timestamped_subtitle(sidecar: Path, vtt_converter: Callable[[str], str]) -> str:
    raw = sidecar.read_text(encoding='utf-8-sig', errors='replace')
    if sidecar.suffix.lower() == '.vtt':
        return str(vtt_converter(raw) or '')
    output = []
    # SRT -> same bracketed timeline representation accepted by the existing
    # timestamp-aware transcript preflight; no timestamps are fabricated.
    blocks = re.split(r'\n\s*\n', raw.replace('\r\n', '\n').replace('\r', '\n'))
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        match = next((matched for line in lines if (matched := re.match(r'^((?:\d{2}:)?\d{2}:\d{2}[.,]\d{3})\s*-->', line))), None)
        if match:
            stamp = match.group(1).replace(',', '.').split('.')[0]
            if stamp.count(':') == 1:
                stamp = '00:' + stamp
            index = next(i for i, line in enumerate(lines) if '-->' in line)
            speech = ' '.join(lines[index + 1:])
            if speech:
                output.append(f'[{stamp}] {speech}')
    return '\n'.join(output)


def _sidecar_to_cache(video_id: str, sidecars: dict[str, Path], transcript_root: Path,
                      vtt_converter: Callable[[str], str]) -> Path | None:
    """Use the existing temp-path convention; never edit external sidecar files."""
    transcript = sidecars.get('transcript')
    if transcript:
        content = transcript.read_text(encoding='utf-8-sig', errors='replace')
    elif sidecars.get('subtitle'):
        content = _timestamped_subtitle(sidecars['subtitle'], vtt_converter)
    else:
        return None
    if not content.strip():
        return None
    path = transcript_root / video_id / f'{video_id}.timestamped.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    # Repeated imports should not rewrite unchanged derived evidence.
    if not path.exists() or path.read_text(encoding='utf-8', errors='replace') != content:
        tmp = path.with_suffix('.tmp')
        tmp.write_text(content, encoding='utf-8')
        os.replace(tmp, path)
    return path


def _ensure_schema(con: sqlite3.Connection) -> None:
    con.execute('''CREATE TABLE IF NOT EXISTS local_video_imports (
      video_id TEXT PRIMARY KEY, source_path TEXT NOT NULL UNIQUE,
      storage_mode TEXT NOT NULL, stored_path TEXT NOT NULL, file_size INTEGER NOT NULL,
      imported_at TEXT NOT NULL)''')


def scan_local_videos(options: dict) -> dict:
    files = discover(options.get('paths') or '')
    preview_limit = 100
    return {'ok': True, 'found': len(files), 'preview': [
        {'path': str(p), 'size': p.stat().st_size, 'id': local_video_id(p),
         'sidecars': sorted(matching_sidecars(p))} for p in files[:preview_limit]],
        'preview_truncated': len(files) > preview_limit,
        'message': 'Read-only preview; nothing has been moved, copied, uploaded, or transcribed.'}


def import_local_videos(options: dict, *, connect: Callable[[], sqlite3.Connection],
                        managed_root: Path, transcript_root: Path,
                        vtt_converter: Callable[[str], str],
                        progress: Callable[[int, int, str], None] | None = None) -> dict:
    """Add independent `platform=local` records. Never upload or call any AI API."""
    mode = str(options.get('mode') or 'reference').lower()
    if mode not in {'reference', 'copy', 'move'}:
        raise ValueError('Mode must be reference, copy, or move.')
    if mode == 'move' and options.get('confirm_move') is not True:
        raise ValueError('Moving original video files requires explicit confirmation.')
    sources = discover(options.get('paths') or '')
    managed_root = managed_root.resolve()
    transcript_root = transcript_root.resolve()
    con = connect()
    _ensure_schema(con)
    added = skipped = errors = 0
    rows = []
    try:
        for index, source in enumerate(sources, 1):
            if progress:
                progress(index - 1, len(sources), str(source))
            vid = local_video_id(source)
            dest = None
            dest_created = False
            try:
                # Avoid recursively importing a managed copy; we keep the
                # existing database identity instead.
                if source.is_relative_to(managed_root):
                    skipped += 1; rows.append({'id': vid, 'status': 'SKIPPED_MANAGED_SOURCE'}); continue
                if con.execute('SELECT 1 FROM videos WHERE video_id=?', (vid,)).fetchone():
                    skipped += 1; rows.append({'id': vid, 'status': 'ALREADY_IMPORTED'}); continue
                sidecars = matching_sidecars(source)
                info = probe(source, options.get('ffprobe') or None)
                target = source
                if mode in {'copy', 'move'}:
                    managed_root.mkdir(parents=True, exist_ok=True)
                    dest = managed_root / vid
                    if dest.exists():
                        raise FileExistsError('Managed destination already exists; refusing to overwrite.')
                    dest.mkdir(parents=True, exist_ok=False)
                    dest_created = True
                    target = dest / source.name
                    if mode == 'copy':
                        shutil.copy2(source, target)
                    else:
                        shutil.move(str(source), str(target))
                now = time.strftime('%Y-%m-%d %H:%M:%S')
                title = source.stem
                record = {
                    'video_id': vid, 'platform': 'local', 'url': '', 'original_title': title,
                    'clean_title': title, 'channel': 'Local Files', 'category': 'Local Videos',
                    'downloaded': 1, 'status': 'active', 'current_present': 1,
                    'local_folder': str(target.parent), 'local_video': str(target),
                    'subtitle_file': str(sidecars.get('subtitle') or ''),
                    'transcript_original': str(sidecars.get('transcript') or ''),
                    'transcript_source': 'local_sidecar' if sidecars else '',
                    'duration_seconds': info.get('duration_seconds') or 0,
                    'metadata_source': 'local_ffprobe' if info else 'local_filesystem',
                    'filesize_approx': source.stat().st_size if source.exists() else target.stat().st_size,
                    'first_seen': now, 'last_seen': now, 'final_status': 'PASS',
                    'availability': 'local',
                }
                canonical = _sidecar_to_cache(vid, sidecars, transcript_root, vtt_converter)
                if canonical:
                    record['transcript_original'] = str(canonical)
                    record['transcript_clean'] = str(canonical)
                keys = list(record)
                con.execute('INSERT INTO videos (' + ','.join('"'+k+'"' for k in keys) +
                            ') VALUES (' + ','.join('?' for _ in keys) + ')', [record[k] for k in keys])
                con.execute('INSERT INTO local_video_imports VALUES (?,?,?,?,?,?)',
                            (vid, str(source), mode, str(target), target.stat().st_size, now))
                con.commit()
                added += 1
                rows.append({'id': vid, 'status': 'IMPORTED', 'title': title, 'mode': mode,
                             'transcript_ready': bool(canonical), 'stored_path': str(target)})
            except Exception as exc:
                con.rollback()
                if dest_created and dest and dest.exists():
                    # Only clean up folders created by this run. Never touch
                    # a pre-existing destination, and never delete a moved
                    # original if rollback to its source path fails.
                    moved_file = dest / source.name
                    if mode == 'move' and moved_file.is_file() and not source.exists():
                        try: shutil.move(str(moved_file), str(source))
                        except OSError: pass
                    if mode == 'copy' and moved_file.is_file():
                        moved_file.unlink()
                    if not any(dest.iterdir()):
                        dest.rmdir()
                errors += 1
                rows.append({'id': vid, 'status': 'ERROR', 'error_type': type(exc).__name__})
        if progress:
            progress(len(sources), len(sources), 'Completed')
    finally:
        con.close()
    return {'ok': errors == 0, 'found': len(sources), 'imported': added,
            'skipped': skipped, 'errors': errors, 'items': rows,
            'message': 'No network, speech recognition, or OpenAI API request was made.'}
