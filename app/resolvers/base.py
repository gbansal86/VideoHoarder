"""Shared interfaces/data for embedded video URL resolver plugins."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class VideoCandidate:
    host: str
    video_id: str
    embed_url: str
    watch_url: str

    def as_dict(self) -> dict[str, str]:
        return {
            "host": self.host,
            "video_id": self.video_id,
            "embed_url": self.embed_url,
            "watch_url": self.watch_url,
        }


class FinalHostResolver(Protocol):
    name: str

    def find(self, text: str) -> list[VideoCandidate]: ...


class PlayerPageResolver(Protocol):
    name: str

    def applies(self, base_url: str) -> bool: ...

    def find(self, base_url: str, text: str) -> list[str]: ...
