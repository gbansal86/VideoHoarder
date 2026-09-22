from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

from app.ai_cache_identity import (
    ANSWER_PROMPT_VERSION,
    answer_cache_identity,
    embedding_identity,
)
from app.library_pagination import paginate_library

ROOT = Path(__file__).parents[1]


def _library_db(count: int = 12050) -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.execute(
        """CREATE TABLE videos(
            video_id TEXT PRIMARY KEY,
            url TEXT,
            original_title TEXT,
            clean_title TEXT,
            channel TEXT,
            category TEXT,
            subcategory TEXT,
            source_category TEXT,
            youtube_category_name TEXT,
            downloaded_at TEXT,
            local_video TEXT,
            final_status TEXT,
            favorite INTEGER,
            watched INTEGER,
            archived INTEGER,
            thumbnail_url TEXT
        )"""
    )
    rows = []
    for i in range(count):
        rows.append(
            (
                f"v{i:05d}",
                f"https://youtu.be/v{i:05d}",
                f"Original {i:05d}",
                f"Video {i:05d}",
                f"Channel {i % 7}",
                "Health" if i % 2 == 0 else "Technology",
                "General",
                "Education",
                "Education",
                f"2026-09-{(i % 9) + 1:02d} 12:00:00",
                f"/library/v{i:05d}.mp4",
                "SUCCESS",
                1 if i % 10 == 0 else 0,
                0,
                0,
                "",
            )
        )
    con.executemany("INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    con.commit()
    return con


def test_phase5_library_paginates_beyond_old_10000_cap_with_real_total() -> None:
    con = _library_db(12050)
    try:
        columns = {r[1] for r in con.execute("PRAGMA table_info(videos)")}
        result = paginate_library(
            con,
            columns,
            page=121,
            page_size=100,
            sort_by="title",
            path_exists=lambda _value: True,
        )
    finally:
        con.close()
    assert result["total"] == 12050
    assert result["max_page"] == 121
    assert result["page"] == 121
    assert len(result["items"]) == 50
    assert result["items"][0]["video_id"] == "v12000"


def test_phase5_library_search_scores_use_temp_relation_without_sql_variable_cap() -> None:
    con = _library_db(2500)
    try:
        columns = {r[1] for r in con.execute("PRAGMA table_info(videos)")}
        scores = {f"v{i:05d}": float(i) for i in range(1800)}
        result = paginate_library(
            con,
            columns,
            query="not-present-in-live-columns",
            page=18,
            page_size=100,
            search_scores=scores,
            path_exists=lambda _value: True,
        )
    finally:
        con.close()
    assert result["total"] == 1800
    assert result["max_page"] == 18
    assert len(result["items"]) == 100
    assert result["items"][0]["video_id"] == "v00099"


def test_phase5_native_library_uses_server_page_not_10000_row_snapshot() -> None:
    source = (ROOT / "app" / "native_library_page.py").read_text(encoding="utf-8")
    assert "web_library_page(" in source
    assert "web_library_rows(query, filter_key, 10000" not in source
    assert "self._total" in source
    assert "self.refresh()" in source.split("def _next_page", 1)[1]


def test_phase5_embedding_identity_distinguishes_backend_model_and_dimension() -> None:
    a = embedding_identity("hashing", 384, model="sha1-v1")
    b = embedding_identity("sentence_transformers", 384, model="all-MiniLM-L6-v2")
    c = embedding_identity("sentence_transformers", 768, model="all-MiniLM-L6-v2")
    assert a["fingerprint"] != b["fingerprint"]
    assert b["fingerprint"] != c["fingerprint"]


def test_phase5_wrong_backend_legacy_vector_is_rebuilt_not_reused(tmp_path: Path) -> None:
    from app import app

    chunk = {
        "chunk_id": "c1",
        "video_id": "v1",
        "title": "Title",
        "section_title": "Section",
        "category": "Health",
        "subcategory": "General",
        "topics": ["topic"],
        "text": "correct transcript text",
    }
    cache = tmp_path / "chunk_embeddings.jsonl"
    manifest = tmp_path / "embedding_manifest.json"
    embed_text = app.phase6_chunk_embedding_text(chunk)
    source_hash = hashlib.sha256(embed_text.encode("utf-8")).hexdigest()
    # Legacy manifest/source hash matches, which used to authorize reuse despite
    # the vector being produced by another backend.
    manifest.write_text(json.dumps({"c1": source_hash}), encoding="utf-8")
    cache.write_text(json.dumps({"chunk_id": "c1", "video_id": "v1", "backend": "hashing", "vector": [9.0, 9.0, 9.0]}) + "\n", encoding="utf-8")
    desired = embedding_identity("sentence_transformers", 3, model="all-MiniLM-L6-v2", implementation="sentence-transformers")

    with patch.object(app, "phase6_load_chunks", return_value=[chunk]), \
         patch.object(app, "phase6_embedding_cache_path", return_value=cache), \
         patch.object(app, "phase6_embedding_manifest_path", return_value=manifest), \
         patch.object(app, "phase6_active_embedding_identity", return_value=desired), \
         patch.object(app, "phase6_embed_text", return_value=([0.1, 0.2, 0.3], "sentence_transformers")):
        out = app.phase6_build_embeddings(incremental=True)

    assert out[0]["vector"] == [0.1, 0.2, 0.3]
    assert out[0]["backend"] == "sentence_transformers"
    assert out[0]["identity_fingerprint"] == desired["fingerprint"]
    new_manifest = json.loads(manifest.read_text(encoding="utf-8"))
    assert new_manifest["identity"]["fingerprint"] == desired["fingerprint"]
    assert new_manifest["chunks"]["c1"] == source_hash


def test_phase5_answer_cache_identity_changes_when_same_chunk_text_changes() -> None:
    settings = {"temperature": 0.2, "num_ctx_fast": 8192, "fast_chunks": 10}
    old = [{"chunk_id": "c1", "video_id": "v1", "text": "OLD text"}]
    corrected = [{"chunk_id": "c1", "video_id": "v1", "text": "CORRECTED text"}]
    a = answer_cache_identity(question="What?", mode="fast", model="m", evidence=old, settings=settings)
    b = answer_cache_identity(question="What?", mode="fast", model="m", evidence=corrected, settings=settings)
    assert a["cache_key"] != b["cache_key"]
    assert a["evidence_hash"] != b["evidence_hash"]
    assert a["generation"]["prompt_version"] == ANSWER_PROMPT_VERSION


def test_phase5_answer_cache_identity_changes_with_generation_settings() -> None:
    evidence = [{"chunk_id": "c1", "video_id": "v1", "text": "same"}]
    a = answer_cache_identity(
        question="What?", mode="fast", model="m", evidence=evidence,
        settings={"temperature": 0.2, "num_ctx_fast": 8192, "fast_chunks": 10},
    )
    b = answer_cache_identity(
        question="What?", mode="fast", model="m", evidence=evidence,
        settings={"temperature": 0.7, "num_ctx_fast": 8192, "fast_chunks": 10},
    )
    assert a["cache_key"] != b["cache_key"]


def test_phase5_local_ai_does_not_return_stale_cached_evidence(tmp_path: Path) -> None:
    from app import app

    settings = {
        "fast_model": "qwen-test",
        "deep_model": "qwen-deep",
        "temperature": 0.2,
        "num_ctx_fast": 8192,
        "num_ctx_deep": 16384,
        "fast_chunks": 10,
        "deep_chunks": 24,
        "keep_alive": "30m",
        "ollama_url": "http://127.0.0.1:11434",
        "timeout_seconds": 5,
    }
    old = [{"chunk_id": "c1", "video_id": "v1", "title": "T", "text": "OLD text"}]
    corrected = [{"chunk_id": "c1", "video_id": "v1", "title": "T", "text": "CORRECTED text"}]
    calls = []

    def fake_generate(_url, payload=None, timeout=0):
        calls.append(payload["prompt"])
        return {"response": "answer-old" if "OLD text" in payload["prompt"] else "answer-corrected"}

    with patch.object(app, "phase6_answer_cache_dir", return_value=tmp_path), \
         patch.object(app, "phase6_load_ai_settings", return_value=settings), \
         patch.object(app, "phase6_ollama_status", return_value=(True, ["qwen-test"], "")), \
         patch.object(app, "phase6_http_json", side_effect=fake_generate), \
         patch.object(app, "phase6_build_evidence", side_effect=[old, corrected]):
        first = app.phase6_ollama_generate("question", mode="fast", use_cache=True)
        second = app.phase6_ollama_generate("question", mode="fast", use_cache=True)

    assert first["answer"] == "answer-old"
    assert second["answer"] == "answer-corrected"
    assert second["cached"] is False
    assert len(calls) == 2
    assert len(list(tmp_path.glob("*.json"))) == 2
