"""Terminal-host resolver plugins (Dailymotion, YouTube and Vimeo)."""

from __future__ import annotations

import re

from .base import VideoCandidate


class DailymotionResolver:
    name = "dailymotion"
    patterns = (
        re.compile(r"https?://(?:www\.)?dailymotion\.com/embed/video/([A-Za-z0-9]+)", re.I),
        re.compile(r"https?://(?:www\.)?dailymotion\.com/video/([A-Za-z0-9]+)", re.I),
        re.compile(r"https?://dai\.ly/([A-Za-z0-9]+)", re.I),
    )

    def find(self, text: str) -> list[VideoCandidate]:
        return self._find(text)

    def _find(self, text: str) -> list[VideoCandidate]:
        found: list[VideoCandidate] = []
        seen: set[str] = set()
        for pattern in self.patterns:
            for match in pattern.finditer(str(text or "")):
                video_id = match.group(1)
                if video_id in seen:
                    continue
                seen.add(video_id)
                found.append(VideoCandidate(
                    host=self.name,
                    video_id=video_id,
                    embed_url=f"https://www.dailymotion.com/embed/video/{video_id}",
                    watch_url=f"https://www.dailymotion.com/video/{video_id}",
                ))
        return found


class YouTubeResolver:
    name = "youtube"
    patterns = (
        re.compile(r"https?://(?:www\.)?youtube\.com/embed/([A-Za-z0-9_-]{6,})", re.I),
        re.compile(r"https?://(?:www\.)?youtube\.com/watch\?[^\s\"'<>]*?v=([A-Za-z0-9_-]{6,})", re.I),
        re.compile(r"https?://youtu\.be/([A-Za-z0-9_-]{6,})", re.I),
    )

    def find(self, text: str) -> list[VideoCandidate]:
        found: list[VideoCandidate] = []
        seen: set[str] = set()
        for pattern in self.patterns:
            for match in pattern.finditer(str(text or "")):
                video_id = match.group(1)
                if video_id in seen:
                    continue
                seen.add(video_id)
                found.append(VideoCandidate(
                    host=self.name,
                    video_id=video_id,
                    embed_url=f"https://www.youtube.com/embed/{video_id}",
                    watch_url=f"https://www.youtube.com/watch?v={video_id}",
                ))
        return found


class VimeoResolver:
    name = "vimeo"
    patterns = (
        re.compile(r"https?://player\.vimeo\.com/video/(\d+)", re.I),
        re.compile(r"https?://(?:www\.)?vimeo\.com/(\d+)", re.I),
    )

    def find(self, text: str) -> list[VideoCandidate]:
        found: list[VideoCandidate] = []
        seen: set[str] = set()
        for pattern in self.patterns:
            for match in pattern.finditer(str(text or "")):
                video_id = match.group(1)
                if video_id in seen:
                    continue
                seen.add(video_id)
                found.append(VideoCandidate(
                    host=self.name,
                    video_id=video_id,
                    embed_url=f"https://player.vimeo.com/video/{video_id}",
                    watch_url=f"https://vimeo.com/{video_id}",
                ))
        return found


def default_final_resolvers() -> list:
    return [DailymotionResolver(), YouTubeResolver(), VimeoResolver()]
