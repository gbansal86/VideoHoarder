"""Embedded-player URL resolution orchestration for VideoHoarder.

Host/player parsing is plugin based under :mod:`app.resolvers`; this module owns
bounded traversal, HTTP fetching and evidence-report persistence.
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable, Iterable

try:
    from .resolvers import (
        VideoCandidate,
        default_final_resolvers,
        default_player_resolvers,
    )
except ImportError:  # pragma: no cover - direct script compatibility
    from resolvers import (
        VideoCandidate,
        default_final_resolvers,
        default_player_resolvers,
    )


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0 Safari/537.36"
)


def fetch_text(url: str, referer: str = "", timeout: int = 30, max_bytes: int = 2_500_000) -> str:
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    if referer:
        headers["Referer"] = referer
        parsed = urllib.parse.urlparse(referer)
        if parsed.scheme and parsed.netloc:
            headers["Origin"] = f"{parsed.scheme}://{parsed.netloc}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(max_bytes)
        content_type = str(response.headers.get("content-type") or "")
    encoding = "utf-8"
    match = re.search(r"charset=([\w.-]+)", content_type, re.I)
    if match:
        encoding = match.group(1)
    return raw.decode(encoding, errors="replace")


class EmbeddedVideoResolver:
    """Breadth-first resolver that follows plugin-discovered player pages."""

    def __init__(
        self,
        fetcher: Callable[[str, str], str] | None = None,
        max_depth: int = 3,
        max_pages: int = 16,
        final_resolvers: Iterable | None = None,
        player_resolvers: Iterable | None = None,
    ) -> None:
        self.fetcher = fetcher or (lambda url, referer="": fetch_text(url, referer))
        self.max_depth = max(0, int(max_depth))
        self.max_pages = max(1, int(max_pages))
        self.final_resolvers = list(final_resolvers or default_final_resolvers())
        self.player_resolvers = list(player_resolvers or default_player_resolvers())

    def _final_candidates(self, text: str) -> list[VideoCandidate]:
        found: list[VideoCandidate] = []
        seen: set[tuple[str, str]] = set()
        for resolver in self.final_resolvers:
            for candidate in resolver.find(text):
                key = (candidate.host, candidate.video_id)
                if key not in seen:
                    seen.add(key)
                    found.append(candidate)
        return found

    def _player_urls(self, base_url: str, body: str) -> list[str]:
        found: list[str] = []
        for resolver in self.player_resolvers:
            if not resolver.applies(base_url):
                continue
            for url in resolver.find(base_url, body):
                if url not in found:
                    found.append(url)
        return found

    def resolve(self, url: str) -> dict:
        original = str(url or "").strip()
        result: dict = {
            "original_url": original,
            "status": "UNRESOLVED",
            "resolver_chain": [original] if original else [],
            "candidate_urls": [],
            "embedded_players": [],
            "player_errors": [],
            "error": "",
        }
        if not original:
            result["error"] = "Empty URL"
            return result

        direct = self._final_candidates(original)
        if direct:
            candidate = direct[0]
            result.update(candidate.as_dict())
            result["status"] = "RESOLVED"
            result["candidate_urls"] = [item.as_dict() for item in direct]
            return result

        queue: list[tuple[str, str, list[str], int]] = [(original, "", [original], 0)]
        visited: set[str] = set()
        players_seen: list[str] = []

        while queue and len(visited) < self.max_pages:
            current, referer, chain, depth = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            try:
                body = self.fetcher(current, referer)
            except Exception as exc:
                result["player_errors"].append({"url": current, "error": f"{type(exc).__name__}: {exc}"[:500]})
                if current == original:
                    result["error"] = f"{type(exc).__name__}: {exc}"
                continue

            candidates = self._final_candidates(body)
            if candidates:
                candidate = candidates[0]
                result.update(candidate.as_dict())
                result["status"] = "RESOLVED"
                resolved_chain = list(chain)
                if candidate.embed_url and candidate.embed_url not in resolved_chain:
                    resolved_chain.append(candidate.embed_url)
                result["resolver_chain"] = resolved_chain
                result["candidate_urls"] = [item.as_dict() for item in candidates]
                result["embedded_players"] = players_seen[:50]
                return result

            if depth >= self.max_depth:
                continue

            for player_url in self._player_urls(current, body):
                if player_url in visited or player_url in players_seen:
                    continue
                players_seen.append(player_url)
                direct_player = self._final_candidates(player_url)
                if direct_player:
                    candidate = direct_player[0]
                    result.update(candidate.as_dict())
                    result["status"] = "RESOLVED"
                    result["resolver_chain"] = chain + [player_url]
                    result["candidate_urls"] = [item.as_dict() for item in direct_player]
                    result["embedded_players"] = players_seen[:50]
                    return result
                queue.append((player_url, current, chain + [player_url], depth + 1))

        result["embedded_players"] = players_seen[:50]
        return result


def write_resolution_report(results: list[dict], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"resolved_video_urls_{stamp}.json"
    csv_path = output_dir / f"resolved_video_urls_{stamp}.csv"
    json_path.write_text(
        json.dumps({"ok": True, "count": len(results), "results": results}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    fields = ["status", "host", "video_id", "watch_url", "embed_url", "original_url", "resolver_chain", "error"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow({
                key: "; ".join(result.get(key) or []) if key == "resolver_chain" else result.get(key, "")
                for key in fields
            })
    return json_path, csv_path


def resolve_many(
    urls: Iterable[str],
    output_dir: Path,
    progress: Callable[[int, int, str, dict], None] | None = None,
    resolver: EmbeddedVideoResolver | None = None,
) -> dict:
    url_list = [str(url or "").strip() for url in urls if str(url or "").strip()]
    engine = resolver or EmbeddedVideoResolver()
    results: list[dict] = []
    total = len(url_list)
    for index, url in enumerate(url_list, 1):
        result = engine.resolve(url)
        results.append(result)
        if progress:
            progress(index, total, url, result)
    json_path, csv_path = write_resolution_report(results, output_dir)
    return {
        "ok": True,
        "count": len(results),
        "resolved": sum(1 for result in results if result.get("status") == "RESOLVED"),
        "json": str(json_path),
        "csv": str(csv_path),
        "results": results,
    }
