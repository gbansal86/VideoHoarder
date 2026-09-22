"""Intermediate iframe/player-page resolver plugins."""

from __future__ import annotations

import html
import re
import urllib.parse


class GenericIframeResolver:
    name = "generic-iframe"
    ATTR_RE = re.compile(
        r"<(?:iframe|embed|video|source)[^>]+(?:src|data-src|data-url|data-file)=[\"']([^\"']+)[\"']",
        re.I,
    )
    URL_RE = re.compile(r"https?://[^\"'<>\s]+", re.I)
    PLAYER_HINTS = (
        "embed", "player", "watch", "video", "stream", "fastvid",
        "dramavideo", "dailymotion", "youtube", "vimeo",
    )

    def applies(self, base_url: str) -> bool:
        return True

    def find(self, base_url: str, text: str) -> list[str]:
        urls: list[str] = []

        def add(raw: str) -> None:
            value = urllib.parse.urljoin(base_url, html.unescape(str(raw or "")).strip())
            if value.startswith(("http://", "https://")) and value not in urls:
                urls.append(value)

        for match in self.ATTR_RE.finditer(str(text or "")):
            add(match.group(1))
        for match in self.URL_RE.finditer(str(text or "")):
            candidate = html.unescape(match.group(0)).rstrip("),.;")
            if any(hint in candidate.lower() for hint in self.PLAYER_HINTS):
                add(candidate)
        return urls


class FastVidResolver(GenericIframeResolver):
    name = "fastvid"

    def applies(self, base_url: str) -> bool:
        return "fastvid" in urllib.parse.urlparse(str(base_url or "")).netloc.lower()


class DramaVideoResolver(GenericIframeResolver):
    name = "dramavideo"

    def applies(self, base_url: str) -> bool:
        return "dramavideo" in urllib.parse.urlparse(str(base_url or "")).netloc.lower()


def default_player_resolvers() -> list:
    # Host-specific plugins run first so later host quirks can be added without
    # changing the generic fallback or the orchestration engine.
    return [FastVidResolver(), DramaVideoResolver(), GenericIframeResolver()]
