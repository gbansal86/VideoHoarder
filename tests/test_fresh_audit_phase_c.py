from pathlib import Path
from app.youtube_url import parse_youtube_reference, youtube_video_id, youtube_source_descriptor


def test_youtube_parser_supports_modern_video_forms():
    vid = "AbCdEf12345"
    for url in [
        f"https://www.youtube.com/watch?v={vid}",
        f"https://youtu.be/{vid}",
        f"https://www.youtube.com/shorts/{vid}",
        f"https://www.youtube.com/embed/{vid}",
        f"https://www.youtube.com/live/{vid}",
    ]:
        assert youtube_video_id(url) == vid
        assert youtube_source_descriptor(url) == ("video", vid)


def test_watch_with_list_is_explicitly_single_video_policy():
    ref = parse_youtube_reference("https://www.youtube.com/watch?v=AbCdEf12345&list=PL123")
    assert ref.video_id == "AbCdEf12345"
    assert ref.playlist_id == "PL123"
    assert ref.kind == "video"


def test_playlist_channel_and_handle_forms():
    assert youtube_source_descriptor("https://www.youtube.com/playlist?list=PL123") == ("playlist", "PL123")
    assert youtube_source_descriptor("https://www.youtube.com/channel/UC123") == ("channel_id", "UC123")
    assert youtube_source_descriptor("https://www.youtube.com/@demo") == ("handle", "@demo")


def test_report_does_not_hardcode_only_8765():
    text = Path("app/app.py").read_text(encoding="utf-8")
    assert "for(let p=preferred;p<=preferred+20;p++)" in text
    assert "'http://127.0.0.1:8765'+path" not in text


def test_native_batch_preserves_canonical_urls_before_per_job_queueing():
    text = Path("app/native_ui.py").read_text(encoding="utf-8")
    assert 'writer=getattr(self.backend,"web_write_urls",None)' in text
    backend = Path("app/app.py").read_text(encoding="utf-8")
    assert "def current_urls_path():" in backend
    assert 'BASE/"data"/"job_inputs"' in backend
