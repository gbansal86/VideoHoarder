"""Stable cache identities for Phase-6 embeddings and local-AI answers."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

EMBEDDING_SCHEMA_VERSION = 2
ANSWER_CACHE_SCHEMA_VERSION = 2
ANSWER_PROMPT_VERSION = "phase6-evidence-prompt-v2"
HASHING_EMBEDDING_VERSION = "sha1-token-bigram-v1"
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"


def _fingerprint(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(dict(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def embedding_identity(backend: str, dimension: int, model: str = "", implementation: str = "") -> dict[str, Any]:
    backend = str(backend or "hashing")
    if not model:
        model = SENTENCE_TRANSFORMER_MODEL if backend == "sentence_transformers" else HASHING_EMBEDDING_VERSION
    if not implementation:
        implementation = "sentence-transformers" if backend == "sentence_transformers" else HASHING_EMBEDDING_VERSION
    identity = {
        "schema_version": EMBEDDING_SCHEMA_VERSION,
        "backend": backend,
        "model": model,
        "dimension": int(dimension or 0),
        "implementation": implementation,
    }
    identity["fingerprint"] = _fingerprint(identity)
    return identity


def embedding_manifest_compatible(manifest: Any, expected_identity: Mapping[str, Any]) -> bool:
    return bool(
        isinstance(manifest, dict)
        and manifest.get("schema_version") == EMBEDDING_SCHEMA_VERSION
        and isinstance(manifest.get("identity"), dict)
        and manifest["identity"].get("fingerprint") == expected_identity.get("fingerprint")
        and isinstance(manifest.get("chunks"), dict)
    )


def evidence_content_hash(evidence: Iterable[Mapping[str, Any]]) -> str:
    normalized = []
    for item in evidence or []:
        normalized.append({
            "chunk_id": str(item.get("chunk_id") or ""),
            "video_id": str(item.get("video_id") or ""),
            "section_title": str(item.get("section_title") or ""),
            "start": str(item.get("start") or ""),
            "end": str(item.get("end") or ""),
            "text": str(item.get("text") or ""),
        })
    return _fingerprint({"evidence": normalized})


def answer_generation_identity(settings: Mapping[str, Any], *, model: str, mode: str) -> dict[str, Any]:
    mode = str(mode or "fast")
    num_ctx_key = "num_ctx_fast" if mode == "fast" else "num_ctx_deep"
    chunks_key = "fast_chunks" if mode == "fast" else "deep_chunks"
    identity = {
        "schema_version": ANSWER_CACHE_SCHEMA_VERSION,
        "prompt_version": ANSWER_PROMPT_VERSION,
        "model": str(model or ""),
        "mode": mode,
        "temperature": float(settings.get("temperature", 0.2)),
        "num_ctx": int(settings.get(num_ctx_key, 8192 if mode == "fast" else 16384)),
        "evidence_limit": int(settings.get(chunks_key, 10 if mode == "fast" else 24)),
    }
    identity["fingerprint"] = _fingerprint(identity)
    return identity


def answer_cache_identity(
    *,
    question: str,
    mode: str,
    model: str,
    evidence: Iterable[Mapping[str, Any]],
    settings: Mapping[str, Any],
) -> dict[str, Any]:
    evidence_hash = evidence_content_hash(evidence)
    generation = answer_generation_identity(settings, model=model, mode=mode)
    identity = {
        "schema_version": ANSWER_CACHE_SCHEMA_VERSION,
        "question": str(question or "").strip().lower(),
        "evidence_hash": evidence_hash,
        "generation": generation,
    }
    identity["cache_key"] = _fingerprint(identity)
    return identity
