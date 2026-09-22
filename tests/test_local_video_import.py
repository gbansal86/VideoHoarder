"""Local-video import contracts: no YouTube ID, network, AI, or implicit file writes."""
import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from app import local_video_import as local


@pytest.fixture
def store(tmp_path, monkeypatch):
    db = tmp_path / 'library.sqlite'
    con = sqlite3.connect(db)
    con.execute('''CREATE TABLE videos (
        video_id TEXT PRIMARY KEY, platform TEXT, url TEXT, original_title TEXT,
        clean_title TEXT, channel TEXT, category TEXT, downloaded INTEGER,
        status TEXT, current_present INTEGER, local_folder TEXT, local_video TEXT,
        subtitle_file TEXT, transcript_original TEXT, transcript_clean TEXT,
        transcript_source TEXT, subtitle_base_lang TEXT, duration_seconds REAL, metadata_source TEXT,
        filesize_approx INTEGER, first_seen TEXT, last_seen TEXT, final_status TEXT,
        availability TEXT)''')
    con.close()
    monkeypatch.setattr(local, 'probe', lambda *a, **kw: {'duration_seconds': 45.3})
    return (lambda: sqlite3.connect(db)), db, tmp_path / 'managed', tmp_path / 'transcripts'


def _sample(folder: Path, filename: str = 'My Lesson.mp4', content: bytes = b'local fake video' * 100):
    folder.mkdir(parents=True, exist_ok=True)
    media = folder / filename
    media.write_bytes(content)
    return media


def _import(path, store, *, mode='reference', **extra):
    connect, db, managed, transcripts = store
    return local.import_local_videos(
        {'paths': str(path), 'mode': mode, **extra},
        connect=connect, managed_root=managed, transcript_root=transcripts,
        vtt_converter=lambda body: '[00:00:01] ' + body,
    )


def test_preview_is_read_only_and_accepts_individual_file_and_nested_folders(tmp_path):
    root = tmp_path / 'source'
    first = _sample(root, 'A Movie.MP4')
    second = _sample(root / 'Course', 'Lesson.mkv')
    (root / 'notes.txt').write_text('ignore')
    result = local.scan_local_videos({'paths': f'{first}\n{root}'})
    assert result['found'] == 2
    assert {x['path'] for x in result['preview']} == {str(first), str(second)}
    assert all(x['id'].startswith('local_') for x in result['preview'])
    assert not (root / '_data').exists()


def test_reference_never_changes_source_and_reimport_is_idempotent(tmp_path, store):
    video = _sample(tmp_path / 'source')
    before = video.read_bytes()
    first = _import(video, store)
    again = _import(video, store)
    assert first['imported'] == 1 and again['skipped'] == 1
    assert video.read_bytes() == before
    connect, db, managed, transcripts = store
    assert not managed.exists()
    with connect() as con:
        row = con.execute('SELECT platform, url, local_video, video_id FROM videos').fetchone()
        assert row == ('local', '', str(video), local.local_video_id(video))
        assert con.execute('SELECT COUNT(*) FROM videos').fetchone()[0] == 1


def test_copy_preserves_source_and_uses_unique_managed_folder(tmp_path, store):
    video = _sample(tmp_path / 'source')
    outcome = _import(video, store, mode='copy')
    assert outcome['imported'] == 1 and video.is_file()
    copied = Path(outcome['items'][0]['stored_path'])
    assert copied.is_file() and copied.read_bytes() == video.read_bytes()
    assert copied.parent.name == local.local_video_id(video)
    assert _import(video, store, mode='copy')['skipped'] == 1


def test_move_needs_explicit_permission_and_preserves_other_files(tmp_path, store):
    video = _sample(tmp_path / 'source')
    sibling = _sample(video.parent, 'Keep Me.mp4')
    with pytest.raises(ValueError, match='explicit confirmation'):
        _import(video, store, mode='move')
    assert video.is_file() and sibling.is_file()
    outcome = _import(video, store, mode='move', confirm_move=True)
    assert outcome['imported'] == 1 and not video.exists() and sibling.exists()
    assert Path(outcome['items'][0]['stored_path']).read_bytes() == b'local fake video' * 100


def test_srt_is_associated_and_derived_cache_never_changes_sidecar(tmp_path, store):
    video = _sample(tmp_path / 'source')
    sidecar = video.with_suffix('.srt')
    text = '1\n00:00:01,000 --> 00:00:04,000\nHello from the lecture.\n'
    sidecar.write_text(text)
    result = _import(video, store)
    assert result['items'][0]['transcript_ready'] is True
    assert sidecar.read_text() == text
    connect, _, _, _ = store
    with connect() as con:
        subtitle, transcript = con.execute('SELECT subtitle_file,transcript_original FROM videos').fetchone()
    assert subtitle == str(sidecar)
    assert '[00:00:01] Hello from the lecture.' in Path(transcript).read_text()


def test_missing_transcript_does_not_trigger_ai_or_youtube(tmp_path, store):
    video = _sample(tmp_path / 'source')
    result = _import(video, store)
    assert result['items'][0]['transcript_ready'] is False
    assert result['message'] == 'No network, speech recognition, or OpenAI API request was made.'


def test_local_record_is_not_sent_to_youtube_caption_preflight(monkeypatch):
    from app import app as backend
    fake = sqlite3.connect(':memory:')
    fake.execute("CREATE TABLE videos(video_id TEXT,url TEXT,original_title TEXT,upload_date TEXT,subtitle_source TEXT,subtitle_lang TEXT,subtitle_base_lang TEXT,duration_seconds REAL,platform TEXT)")
    fake.execute("CREATE TABLE transcript_availability(video_id TEXT,status TEXT,source TEXT,checked_at TEXT,detail TEXT,package_preflight_id TEXT)")
    fake.execute("INSERT INTO videos VALUES('local_123','','Example','','','','',30,'local')")
    fake.commit()
    class LiveConnection:
        def execute(self, *args): return fake.execute(*args)
        def commit(self): return fake.commit()
        def close(self): pass
    def forbidden(_): raise AssertionError('YouTube caption fetch must not be called for local records')
    monkeypatch.setattr(backend, 'db_connect', lambda: LiveConnection())
    monkeypatch.setattr(backend, 'has_usable_transcript', forbidden)
    monkeypatch.setattr(backend, 'prepare_transcripts_rows', lambda _: (_ for _ in ()).throw(AssertionError('network fetch')))
    monkeypatch.setattr(backend, 'build_video_artifact_manifest', lambda _: {})
    monkeypatch.setattr(backend, 'artifact_manifest_for_video', lambda _: {})
    monkeypatch.setattr(backend, 'best_transcript_for_video', lambda _: ('',''))
    monkeypatch.setattr(backend, 'chatgpt_canonical_evidence', lambda *args: {'transcript_available': False, 'transcript_source': 'no_transcript'})
    report = backend.chatgpt_package_transcript_preflight(['local_123'], fetch_missing=True)
    assert report['unavailable'] == 1
    fake.close()



def test_local_short_video_transcript_uses_same_cache_as_ai_package(tmp_path, store, monkeypatch):
    from app import app as backend
    video = _sample(tmp_path / 'source')
    sidecar = video.with_suffix('.vtt')
    sidecar.write_text('WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nA sample transcript line')
    outcome = _import(video, store)
    assert outcome['imported'] == 1
    connect, _, _, transcripts = store
    monkeypatch.setattr(backend, 'db_connect', connect)
    monkeypatch.setattr(backend, 'temp_transcript_root', lambda: transcripts)
    monkeypatch.setattr(backend, 'temp_short_video_root', lambda: tmp_path / 'short_transcripts')
    video_id = local.local_video_id(video)
    # Even with an FFprobe duration under 60 seconds, a local source does not
    # switch into the YouTube Shorts transcript cache folder.
    canonical = backend.temp_paths(video_id)['timestamped']
    assert canonical.is_file()
    transcript, language = backend.best_transcript_for_video(video_id)
    assert 'sample transcript line' in transcript.lower()


def test_native_navigation_and_manual_api_separation():
    from app import app as backend
    native_source = (Path(__file__).parents[1] / 'app' / 'native_ui.py').read_text(encoding='utf-8')
    assert '("localimport", "▣", "Import Local Videos")' in native_source
    html = backend.import_local_page_html()
    assert '/api/import-local/start' in html and '/api/import-local/scan' in html
    assert 'No automatic transcription' in html
    assert '/api/chatgpt-processing/openai-submit' not in html
