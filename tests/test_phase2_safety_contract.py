from __future__ import annotations

import io
import http.client
import importlib
import threading
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.http_range import RangeNotSatisfiable, parse_single_byte_range
from app.local_api_security import MutationAuthorizer, RequestValidationError, read_json_body
from app.settings_service import apply_settings_update
from app.metadata_schema import apply_video_schema_migrations
import app.metadata_migration as migration


def test_invalid_settings_are_all_or_nothing_in_memory_and_on_disk(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    current = {"workers": 4, "download_subtitles": True, "download_quality": "1080", "ollama_model": "qwen"}
    path.write_text(json.dumps(current), encoding="utf-8")
    before_memory = dict(current)
    before_disk = path.read_bytes()
    result = apply_settings_update({"workers": 0, "download_subtitles": "false"}, current, path)
    assert result["ok"] is False
    assert current == before_memory
    assert path.read_bytes() == before_disk


def test_valid_settings_are_written_atomically(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    current = {"workers": 4, "download_subtitles": True, "download_quality": "1080", "ollama_model": "qwen"}
    path.write_text(json.dumps(current), encoding="utf-8")
    result = apply_settings_update({"workers": 8, "download_subtitles": False, "download_quality": "720"}, current, path)
    assert result["ok"] is True
    persisted = json.loads(path.read_text(encoding="utf-8"))
    assert persisted["workers"] == 8
    assert persisted["download_subtitles"] is False
    assert current == persisted
    assert not list(tmp_path.glob("config.json.*.tmp"))


class _Headers(dict):
    def get(self, key, default=None):
        for k, value in self.items():
            if str(k).lower() == str(key).lower():
                return value
        return default


def _fake_handler(*, token="secret", host="127.0.0.1:8765", origin="http://127.0.0.1:8765", client="127.0.0.1"):
    return SimpleNamespace(
        headers=_Headers({"Host": host, "Origin": origin, "X-VideoHoarder-Token": token}),
        client_address=(client, 1234),
    )


def test_mutation_authorizer_requires_loopback_boundary_and_token() -> None:
    auth = MutationAuthorizer("secret")
    assert auth.validate(_fake_handler(), 8765) == (True, "")
    ok, _ = auth.validate(_fake_handler(token="wrong"), 8765); assert ok is False
    ok, _ = auth.validate(_fake_handler(host="evil.example:8765"), 8765); assert ok is False
    ok, _ = auth.validate(_fake_handler(origin="https://evil.example"), 8765); assert ok is False
    ok, _ = auth.validate(_fake_handler(client="10.0.0.8"), 8765); assert ok is False


def test_strict_json_parser_rejects_malformed_and_non_object_without_dispatch() -> None:
    bad = SimpleNamespace(headers=_Headers({"Content-Length": "7"}), rfile=io.BytesIO(b"{broken"))
    with pytest.raises(RequestValidationError):
        read_json_body(bad)
    arr = b"[1,2]"
    wrong_shape = SimpleNamespace(headers=_Headers({"Content-Length": str(len(arr))}), rfile=io.BytesIO(arr))
    with pytest.raises(RequestValidationError):
        read_json_body(wrong_shape)
    good = b'{"full_rebuild":false}'
    valid = SimpleNamespace(headers=_Headers({"Content-Length": str(len(good))}), rfile=io.BytesIO(good))
    assert read_json_body(valid) == {"full_rebuild": False}


@pytest.mark.parametrize(
    "header,size,expected",
    [
        ("bytes=0-3", 10, (0, 3)),
        ("bytes=4-", 10, (4, 9)),
        ("bytes=-4", 10, (6, 9)),
        ("bytes=-40", 10, (0, 9)),
        ("bytes=8-99", 10, (8, 9)),
    ],
)
def test_http_byte_ranges(header: str, size: int, expected: tuple[int, int]) -> None:
    assert parse_single_byte_range(header, size) == expected


@pytest.mark.parametrize("header", ["bytes=10-", "bytes=5-2", "bytes=-0", "items=0-1", "bytes=0-1,4-5"])
def test_invalid_http_byte_ranges_are_416_candidates(header: str) -> None:
    with pytest.raises(RangeNotSatisfiable):
        parse_single_byte_range(header, 10)


def _make_migration_db(tmp_path: Path):
    db = tmp_path / "library.db"
    con = sqlite3.connect(db)
    con.execute("""CREATE TABLE videos(
        video_id TEXT PRIMARY KEY, url TEXT, original_title TEXT, clean_title TEXT,
        channel TEXT, upload_date TEXT, description TEXT, local_folder TEXT,
        chatgpt_imported INTEGER DEFAULT 0, chatgpt_result_hash TEXT,
        duration_seconds REAL DEFAULT 0, youtube_tags TEXT, youtube_category_name TEXT,
        thumbnail_url TEXT, view_count INTEGER, like_count INTEGER, comment_count INTEGER,
        source_category TEXT, source_category_id TEXT, youtube_category_id TEXT
    )""")
    apply_video_schema_migrations(con)
    folder = tmp_path / "atomicvid01" / "_data"
    folder.mkdir(parents=True)
    (folder / ".video_id").write_text("atomicvid01", encoding="utf-8")
    info = {
        "id": "atomicvid01", "title": "Info title", "webpage_url": "https://youtu.be/atomicvid01",
        "channel": "Info channel", "channel_id": "UC123", "upload_date": "20200102",
        "duration": 321, "availability": "public", "categories": ["Science & Technology"],
        "tags": ["new-tag"],
    }
    (folder / "atomicvid01.info.json").write_text(json.dumps(info), encoding="utf-8")
    con.execute("""INSERT INTO videos(video_id,url,original_title,clean_title,channel,upload_date,description,local_folder,
        chatgpt_imported,chatgpt_result_hash,youtube_tags,youtube_category_name)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", (
        "atomicvid01", "https://youtu.be/atomicvid01", "Old", "Old", "Old channel", "20200102",
        "old desc", str(folder.parent), 1, "keep-me", json.dumps(["old-tag"]), "Education"
    ))
    con.commit()
    return con


def test_metadata_migration_failure_rolls_back_video_writes_before_failed_status(tmp_path: Path, monkeypatch) -> None:
    con = _make_migration_db(tmp_path)
    original = migration.persist_canonical_metadata
    def partial_then_fail(connection, video_id, normalized):
        connection.execute("UPDATE videos SET clean_title='PARTIAL-WRITE' WHERE video_id=?", (video_id,))
        original(connection, video_id, normalized)
        raise RuntimeError("fault injection after writes")
    monkeypatch.setattr(migration, "persist_canonical_metadata", partial_then_fail)
    report = migration.run_existing_library_metadata_migration(con, dry_run=False, force=True)
    row = con.execute("SELECT clean_title,metadata_migration_status,youtube_tags,chatgpt_result_hash FROM videos WHERE video_id='atomicvid01'").fetchone()
    assert report["failed"] == 1
    assert row[0] == "Old"                  # partial write rolled back
    assert row[1] == "FAILED"               # failure marker committed after rollback
    assert json.loads(row[2]) == ["old-tag"] # canonical update also rolled back
    assert row[3] == "keep-me"
    con.close()


def test_settings_disk_write_failure_does_not_change_memory(tmp_path: Path, monkeypatch) -> None:
    import app.settings_service as service
    path = tmp_path / "config.json"
    current = {"workers": 4, "download_subtitles": True, "download_quality": "1080", "ollama_model": "qwen"}
    path.write_text(json.dumps(current), encoding="utf-8")
    before = dict(current)
    monkeypatch.setattr(service.os, "replace", lambda *_args, **_kw: (_ for _ in ()).throw(OSError("disk fault")))
    with pytest.raises(OSError):
        service.apply_settings_update({"workers": 8}, current, path)
    assert current == before
    assert json.loads(path.read_text(encoding="utf-8"))["workers"] == 4


def test_handler_rejects_foreign_origin_and_malformed_json_before_dispatch(monkeypatch) -> None:
    backend = importlib.import_module("app.app")
    calls = []
    monkeypatch.setattr(backend, "web_config_update", lambda values: calls.append(("config", values)) or {"ok": True})
    monkeypatch.setattr(backend, "refresh_dashboard_figures", lambda full: calls.append(("refresh", full)) or {"ok": True})
    server = backend.ThreadingHTTPServer(("127.0.0.1", 0), backend.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    port = server.server_address[1]
    token = backend.WEB_MUTATION_AUTHORIZER.token
    try:
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
        body = b'{"settings":{"workers":8}}'
        conn.request("POST", "/api/config-save", body=body, headers={
            "Content-Type": "application/json", "Content-Length": str(len(body)),
            "X-VideoHoarder-Token": token, "Origin": "https://untrusted.example",
        })
        response = conn.getresponse(); response.read()
        assert response.status == 403
        assert calls == []
        conn.close()

        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
        bad = b"{broken"
        conn.request("POST", "/api/dashboard-figures/refresh", body=bad, headers={
            "Content-Type": "application/json", "Content-Length": str(len(bad)),
            "X-VideoHoarder-Token": token, "Origin": f"http://127.0.0.1:{port}",
        })
        response = conn.getresponse(); payload = json.loads(response.read())
        assert response.status == 400
        assert "Malformed JSON" in payload["message"]
        assert calls == []
        conn.close()
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_metadata_migration_failure_is_retryable_from_clean_pre_failure_data(tmp_path: Path, monkeypatch) -> None:
    con = _make_migration_db(tmp_path)
    original = migration.persist_canonical_metadata
    def fail_after_write(connection, video_id, normalized):
        connection.execute("UPDATE videos SET clean_title='PARTIAL-WRITE' WHERE video_id=?", (video_id,))
        raise RuntimeError("injected")
    monkeypatch.setattr(migration, "persist_canonical_metadata", fail_after_write)
    failed = migration.run_existing_library_metadata_migration(con, dry_run=False, force=True)
    assert failed["failed"] == 1
    assert con.execute("SELECT clean_title FROM videos").fetchone()[0] == "Old"
    monkeypatch.setattr(migration, "persist_canonical_metadata", original)
    retried = migration.run_existing_library_metadata_migration(con, dry_run=False, force=True)
    row = con.execute("SELECT clean_title,metadata_migration_status,channel_id FROM videos").fetchone()
    assert retried["migrated"] == 1 and retried["failed"] == 0
    assert row[0] == "Old" and row[1] == "COMPLETE" and row[2] == "UC123"
    con.close()
