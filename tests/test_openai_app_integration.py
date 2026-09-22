from __future__ import annotations

import importlib
import os
from pathlib import Path


def backend(tmp_path, monkeypatch):
    monkeypatch.setenv("VLM_LIBRARY_ROOT", str(tmp_path / "library"))
    module = importlib.import_module("app.app")
    return module


def test_chatgpt_page_exposes_optional_openai_api_controls(tmp_path, monkeypatch):
    app = backend(tmp_path, monkeypatch)
    page = app.chatgpt_processing_page_html()
    assert "Optional OpenAI API transcript processing" in page
    assert "/api/chatgpt-processing/openai-status" in page
    assert "/api/chatgpt-processing/openai-submit" in page
    assert "/api/chatgpt-processing/openai-create-submit" in page
    assert "never applied automatically" in page


def test_web_config_exposes_provider_controls_but_not_api_key(tmp_path, monkeypatch):
    app = backend(tmp_path, monkeypatch)
    values = app.web_config_view()
    assert "openai_api_enabled" in values
    assert "openai_model" in values
    assert "openai_api_key_env" in values
    assert "openai_allow_restricted_videos" in values
    assert "openai_api_key" not in values


def test_existing_package_api_wrapper_imports_for_review_without_auto_apply(tmp_path, monkeypatch):
    app = backend(tmp_path, monkeypatch)
    package_id = "pkg_api_review"
    folder = tmp_path / package_id
    folder.mkdir()
    monkeypatch.setattr(app, "chatgpt_outgoing_package_folder", lambda _pid: folder)
    monkeypatch.setattr(app, "chatgpt_openai_api_status", lambda: {"ready": True, "message": "Ready"})
    monkeypatch.setattr(
        app,
        "openai_process_video_intelligence_package",
        lambda *args, **kwargs: {
            "ok": True,
            "package_id": package_id,
            "result_file": str(folder / "OPENAI_API_RESULT.json"),
            "result_json": '{"package_id":"pkg_api_review","schema_version":"3.3","batch_validation_status":"PASS","video_updates":[]}',
            "audit_file": str(folder / "OPENAI_API_RUN.json"),
            "successful_videos": 1,
            "failed_videos": 0,
            "failures": [],
        },
    )
    imported_payload = {}

    def fake_import(payload):
        imported_payload.update(payload)
        return {"ok": True, "status": "VALIDATED", "manual_review_required": True, "applied": False}

    monkeypatch.setattr(app, "import_validate_manual_chatgpt_processing_result", fake_import)
    result = app.process_existing_chatgpt_package_via_openai({"package_id": package_id})
    assert result["ok"] is True
    assert result["review_required"] is True
    assert result["automatic_apply"] is False
    assert result["applied"] is False
    assert imported_payload["result_json"].startswith("{")
