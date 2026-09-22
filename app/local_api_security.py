"""Local dashboard request parsing and mutation authorization."""
from __future__ import annotations

import json
import secrets
import urllib.parse
from dataclasses import dataclass
from http.cookies import SimpleCookie
from typing import Any, Mapping

MAX_JSON_BYTES = 145 * 1024 * 1024
MUTATION_COOKIE_NAME = "vh_mutation_token"

class RequestValidationError(ValueError):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def new_mutation_token() -> str:
    return secrets.token_urlsafe(32)


def mutation_cookie(token: str) -> str:
    return f"{MUTATION_COOKIE_NAME}={token}; Path=/; SameSite=Strict; HttpOnly"


def read_json_body(handler: Any, *, max_bytes: int = MAX_JSON_BYTES) -> dict[str, Any]:
    raw_len = handler.headers.get("Content-Length", "0")
    try:
        length = int(raw_len or 0)
    except (TypeError, ValueError):
        raise RequestValidationError("Invalid Content-Length.", 400)
    if length < 0:
        raise RequestValidationError("Invalid Content-Length.", 400)
    if length > max_bytes:
        raise RequestValidationError("Request too large.", 413)
    if length == 0:
        return {}
    try:
        raw = handler.rfile.read(length)
        text = raw.decode("utf-8", "strict")
        obj = json.loads(text)
    except UnicodeDecodeError:
        raise RequestValidationError("Request body must be UTF-8 JSON.", 400)
    except json.JSONDecodeError:
        raise RequestValidationError("Malformed JSON request body.", 400)
    if not isinstance(obj, dict):
        raise RequestValidationError("JSON request body must be an object.", 400)
    return obj


def _header(headers: Mapping[str, Any], key: str) -> str:
    try:
        return str(headers.get(key, "") or "").strip()
    except Exception:
        return ""


def _split_host_port(value: str, default_port: int) -> tuple[str, int] | None:
    if not value:
        return None
    # urlsplit handles IPv6 literals when supplied with // prefix.
    try:
        parsed = urllib.parse.urlsplit("//" + value)
        host = (parsed.hostname or "").lower()
        port = int(parsed.port or default_port)
        return host, port
    except Exception:
        return None


def _origin_host_port(value: str) -> tuple[str, int] | None:
    if not value:
        return None
    try:
        parsed = urllib.parse.urlsplit(value)
        if parsed.scheme not in {"http", "https"}:
            return None
        host = (parsed.hostname or "").lower()
        port = int(parsed.port or (443 if parsed.scheme == "https" else 80))
        return host, port
    except Exception:
        return None


def _cookie_token(headers: Mapping[str, Any]) -> str:
    raw = _header(headers, "Cookie")
    if not raw:
        return ""
    try:
        jar = SimpleCookie(); jar.load(raw)
        morsel = jar.get(MUTATION_COOKIE_NAME)
        return morsel.value if morsel else ""
    except Exception:
        return ""

@dataclass(frozen=True)
class MutationAuthorizer:
    token: str

    def validate(self, handler: Any, server_port: int) -> tuple[bool, str]:
        client = ""
        try:
            client = str(handler.client_address[0]).lower()
        except Exception:
            pass
        if client not in {"127.0.0.1", "::1", "localhost"}:
            return False, "Mutation requests are accepted only from the local machine."

        host = _split_host_port(_header(handler.headers, "Host"), server_port)
        if host is None or host[0] not in {"127.0.0.1", "localhost", "::1"} or host[1] != int(server_port):
            return False, "Invalid local Host boundary."

        origin = _header(handler.headers, "Origin")
        if origin:
            parsed_origin = _origin_host_port(origin)
            if parsed_origin is None or parsed_origin[0] not in {"127.0.0.1", "localhost", "::1"} or parsed_origin[1] != int(server_port):
                return False, "Invalid request Origin."

        supplied = _header(handler.headers, "X-VideoHoarder-Token") or _cookie_token(handler.headers)
        if not supplied or not secrets.compare_digest(supplied, self.token):
            return False, "Missing or invalid local mutation token."
        return True, ""
