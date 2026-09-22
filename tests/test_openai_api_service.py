import json
import os
import sys
import types
from pathlib import Path

import pytest

from app import openai_api_service as svc
from app.settings_service import validate_settings_update


class FakeUsage:
    input_tokens = 101
    output_tokens = 55
    total_tokens = 156


class FakeResponse:
    def __init__(self, response_id, payload):
        self.id = response_id
        self.output_text = json.dumps(payload)
        self.usage = FakeUsage()


class FakeResponses:
    def __init__(self, calls, fail_video_id=None, structured_error=False):
        self.calls = calls
        self.fail_video_id = fail_video_id
        self.structured_error = structured_error
        self.structured_failed_once = False

    def create(self, **kwargs):
        self.calls.append(kwargs)
        user = json.loads(kwargs["input"])
        vid = user["execution"]["video_id"]
        if self.fail_video_id == vid:
            raise RuntimeError("simulated transport failure")
        if self.structured_error and kwargs.get("text", {}).get("format", {}).get("type") == "json_schema" and not self.structured_failed_once:
            self.structured_failed_once = True
            raise RuntimeError("simulated unsupported structured schema")
        return FakeResponse(
            "resp_" + vid,
            {
                "package_id": user["package_id"],
                "schema_version": user["schema_version"],
                "batch_validation_status": "PASS",
                "package_outcome_status": "COMPLETE",
                "video_updates": [
                    {
                        "video_id": vid,
                        "processing_status": "PASS",
                        "evidence_grade": "A",
                        "confidence": "high",
                        "evidence_references": [{"source": "canonical_transcript", "segment_ids": ["s00001"]}],
                        "source_conflicts": [],
                        "validation": {"status": "PASS", "warnings": [], "repair_attempts": 0},
                        "features": {"test.v1": {"summary": "ok"}},
                    }
                ],
            },
        )


class FakeClient:
    calls = []
    fail_video_id = None
    structured_error = False
    init_kwargs = None

    def __init__(self, **kwargs):
        type(self).init_kwargs = kwargs
        self.responses = FakeResponses(type(self).calls, type(self).fail_video_id, type(self).structured_error)


def install_fake_openai(monkeypatch, *, fail_video_id=None, structured_error=False):
    FakeClient.calls = []
    FakeClient.fail_video_id = fail_video_id
    FakeClient.structured_error = structured_error
    FakeClient.init_kwargs = None
    module = types.ModuleType("openai")
    module.OpenAI = FakeClient
    module.__version__ = "test"
    monkeypatch.setitem(sys.modules, "openai", module)
    return FakeClient


def package_payload():
    schema = {
        "type": "object",
        "required": ["package_id", "schema_version", "batch_validation_status", "video_updates"],
        "properties": {
            "package_id": {"const": "pkg_123"},
            "schema_version": {"const": "3.3"},
            "batch_validation_status": {"type": "string"},
            "package_outcome_status": {"type": "string"},
            "video_updates": {"type": "array"},
        },
        "additionalProperties": False,
    }
    return {
        "package_id": "pkg_123",
        "schema_version": "3.3",
        "prompt_version": "test-prompt",
        "prompt_hash": "abc",
        "package_type": "VIDEO_INTELLIGENCE",
        "authoritative_prompt": "Use only current-video evidence.",
        "instructions": {"instructions": "Return JSON only."},
        "response_schema": {"formal_json_schema": schema},
        "videos": [
            {"video_id": "VIDEO_A", "evidence": {"transcript": "TRANSCRIPT_ALPHA_ONLY", "segments": [{"id": "s00001", "text": "alpha"}]}},
            {"video_id": "VIDEO_B", "evidence": {"transcript": "TRANSCRIPT_BETA_ONLY", "segments": [{"id": "s00001", "text": "beta"}]}},
        ],
    }


def write_package(tmp_path: Path) -> Path:
    folder = tmp_path / "pkg_123"
    folder.mkdir()
    (folder / "CHATGPT_PACKAGE.json").write_text(json.dumps(package_payload()), encoding="utf-8")
    return folder


def settings():
    return {
        "openai_api_enabled": True,
        "openai_model": "gpt-5.6",
        "openai_reasoning_effort": "high",
        "openai_timeout_seconds": 30,
        "openai_max_retries": 1,
        "openai_max_output_tokens": 8000,
        "openai_api_key_env": "OPENAI_API_KEY",
        "openai_store_responses": False,
        "openai_structured_outputs": True,
        "openai_allow_restricted_videos": False,
    }


def test_provider_status_never_exposes_key(monkeypatch):
    install_fake_openai(monkeypatch)
    secret = "TEST_SECRET_SUPER_UNIQUE_NEVER_WRITE"
    monkeypatch.setenv("OPENAI_API_KEY", secret)
    status = svc.provider_status(settings())
    assert status["ready"] is True
    assert status["api_key_configured"] is True
    assert secret not in json.dumps(status)


def test_one_video_per_call_and_sanitized_audit(monkeypatch, tmp_path):
    client = install_fake_openai(monkeypatch)
    secret = "TEST_API_KEY_UNIQUE"
    monkeypatch.setenv("OPENAI_API_KEY", secret)
    folder = write_package(tmp_path)
    progress = []

    result = svc.process_video_intelligence_package(
        folder,
        settings(),
        progress=lambda done, total, vid, msg: progress.append((done, total, vid, msg)),
    )

    assert result["ok"] is True
    assert result["successful_videos"] == 2
    assert result["failed_videos"] == 0
    assert len(client.calls) == 2
    first_user = client.calls[0]["input"]
    second_user = client.calls[1]["input"]
    assert "VIDEO_A" in first_user and "TRANSCRIPT_ALPHA_ONLY" in first_user
    assert "VIDEO_B" not in first_user and "TRANSCRIPT_BETA_ONLY" not in first_user
    assert "VIDEO_B" in second_user and "TRANSCRIPT_BETA_ONLY" in second_user
    assert "VIDEO_A" not in second_user and "TRANSCRIPT_ALPHA_ONLY" not in second_user
    assert client.calls[0]["store"] is False
    assert client.calls[0]["text"]["format"]["type"] == "json_schema"
    assert FakeClient.init_kwargs["api_key"] == secret

    merged = json.loads(Path(result["result_file"]).read_text(encoding="utf-8"))
    assert [x["video_id"] for x in merged["video_updates"]] == ["VIDEO_A", "VIDEO_B"]
    audit_text = Path(result["audit_file"]).read_text(encoding="utf-8")
    assert secret not in audit_text
    assert "resp_VIDEO_A" in audit_text
    assert progress[-1][0] == 2


def test_failure_is_recorded_and_remaining_video_continues(monkeypatch, tmp_path):
    client = install_fake_openai(monkeypatch, fail_video_id="VIDEO_A")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    result = svc.process_video_intelligence_package(write_package(tmp_path), settings())
    assert result["ok"] is False
    assert result["partial"] is True
    assert result["successful_videos"] == 1
    assert result["failed_videos"] == 1
    assert result["failures"][0]["video_id"] == "VIDEO_A"
    # A structured request may retry in JSON mode, but processing must continue to VIDEO_B.
    called_ids = [json.loads(x["input"])["execution"]["video_id"] for x in client.calls]
    assert "VIDEO_B" in called_ids


def test_structured_output_failure_falls_back_to_json_object(monkeypatch, tmp_path):
    client = install_fake_openai(monkeypatch, structured_error=True)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    package = package_payload()
    video = package["videos"][0]
    fake_client = client(api_key="test", timeout=10, max_retries=0)
    value, meta = svc._call_one_video(fake_client, package=package, video=video, settings=settings())
    assert value["video_updates"][0]["video_id"] == "VIDEO_A"
    assert meta["structured_outputs"] is False
    assert client.calls[0]["text"]["format"]["type"] == "json_schema"
    assert client.calls[1]["text"]["format"]["type"] == "json_object"


def test_openai_settings_validate_without_accepting_secret_field():
    current = {
        "openai_api_enabled": False,
        "openai_model": "gpt-5.6",
        "openai_api_key_env": "OPENAI_API_KEY",
        "openai_reasoning_effort": "high",
    }
    candidate, errors = validate_settings_update(
        {
            "openai_api_enabled": True,
            "openai_model": "gpt-5.6",
            "openai_reasoning_effort": "xhigh",
            "openai_api_key_env": "VH_OPENAI_KEY",
            "openai_max_output_tokens": 32000,
        },
        current,
    )
    assert not errors
    assert candidate["openai_api_enabled"] is True
    assert candidate["openai_api_key_env"] == "VH_OPENAI_KEY"

    _, errors = validate_settings_update({"openai_api_key": "do-not-store-secrets"}, current)
    assert errors and "unknown setting" in errors[0]


def test_restricted_video_is_not_sent_without_explicit_opt_in(monkeypatch, tmp_path):
    client = install_fake_openai(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    package = package_payload()
    package["videos"][0]["metadata"] = {"availability": "private"}
    folder = tmp_path / "pkg_123"
    folder.mkdir()
    (folder / "CHATGPT_PACKAGE.json").write_text(json.dumps(package), encoding="utf-8")
    result = svc.process_video_intelligence_package(folder, settings())
    assert result["failed_videos"] == 1
    assert result["failures"][0]["video_id"] == "VIDEO_A"
    called_ids = [json.loads(x["input"])["execution"]["video_id"] for x in client.calls]
    assert "VIDEO_A" not in called_ids
    assert "VIDEO_B" in called_ids


def test_restricted_video_can_be_sent_only_after_explicit_opt_in(monkeypatch, tmp_path):
    client = install_fake_openai(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    package = package_payload()
    package["videos"][0]["metadata"] = {"availability": "unlisted"}
    folder = tmp_path / "pkg_123"
    folder.mkdir()
    (folder / "CHATGPT_PACKAGE.json").write_text(json.dumps(package), encoding="utf-8")
    cfg = settings(); cfg["openai_allow_restricted_videos"] = True
    result = svc.process_video_intelligence_package(folder, cfg)
    assert result["ok"] is True
    called_ids = [json.loads(x["input"])["execution"]["video_id"] for x in client.calls]
    assert called_ids == ["VIDEO_A", "VIDEO_B"]


def test_raw_provider_exception_never_leaks_key_to_audit(monkeypatch, tmp_path):
    install_fake_openai(monkeypatch)
    secret = "TEST_ENV_SECRET_NOT_FOR_AUDIT"
    monkeypatch.setenv("OPENAI_API_KEY", secret)

    def failing_call(*args, **kwargs):
        raise RuntimeError("provider error contained " + secret)

    monkeypatch.setattr(svc, "_call_one_video", failing_call)
    result = svc.process_video_intelligence_package(write_package(tmp_path), settings())
    assert result["failed_videos"] == 2
    assert secret not in json.dumps(result)
    assert secret not in Path(result["audit_file"]).read_text(encoding="utf-8")
