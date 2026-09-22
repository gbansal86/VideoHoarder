"""Small dashboard-server helpers."""

from __future__ import annotations

import time
import urllib.request
from typing import Tuple


def wait_for_http_ready(url: str, timeout_seconds: float = 3.0, interval_seconds: float = 0.05) -> Tuple[bool, str]:
    deadline = time.time() + max(0.1, float(timeout_seconds))
    last_error = ""
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=min(1.0, max(0.1, deadline - time.time()))) as response:
                if response.status < 500:
                    return True, ""
                last_error = f"HTTP {response.status}"
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(max(0.01, float(interval_seconds)))
    return False, last_error
