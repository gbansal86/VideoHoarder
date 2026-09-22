"""Canonical YouTube URL parsing used by queue, duplicate guard and metadata paths."""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse


@dataclass(frozen=True, slots=True)
class YouTubeReference:
    raw: str
    video_id: str = ""
    playlist_id: str = ""
    channel_id: str = ""
    handle: str = ""
    username: str = ""
    kind: str = "other"


def _host_is_youtube(host: str) -> bool:
    host = host.lower().split(":", 1)[0].strip().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    return host in {"youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"} or host.endswith(".youtube.com")


def is_youtube_url(url: str) -> bool:
    """Return True only for actual YouTube/youtu.be hosts."""
    raw = str(url or "").strip()
    if not raw:
        return False
    parsed = urlparse(raw if "://" in raw else "https://" + raw)
    return _host_is_youtube(parsed.netloc)


def parse_youtube_reference(url: str) -> YouTubeReference:
    raw = str(url or "").strip()
    if not raw:
        return YouTubeReference(raw=raw)
    parsed = urlparse(raw if "://" in raw else "https://" + raw)
    host = parsed.netloc.lower().split(":", 1)[0]
    if not _host_is_youtube(host):
        return YouTubeReference(raw=raw)
    parts = [part for part in parsed.path.split("/") if part]
    qs = parse_qs(parsed.query)
    video_id = ""
    playlist_id = str((qs.get("list") or [""])[0] or "").strip()
    channel_id = ""
    handle = ""
    username = ""

    if host.endswith("youtu.be") and parts:
        video_id = parts[0]
    elif parts[:1] == ["watch"] or parsed.path.rstrip("/") == "/watch":
        video_id = str((qs.get("v") or [""])[0] or "").strip()
    elif parts and parts[0] in {"shorts", "embed", "live"} and len(parts) >= 2:
        video_id = parts[1]
    elif parts and parts[0] == "channel" and len(parts) >= 2:
        channel_id = parts[1]
    elif parts and parts[0].startswith("@"):
        handle = parts[0]
    elif parts and parts[0] == "user" and len(parts) >= 2:
        username = parts[1]

    # Explicit policy: a watch URL with both v= and list= means the selected
    # video, not an implicit whole-playlist download.  /playlist?list= is the
    # playlist form.  The playlist_id is still retained as metadata.
    if video_id:
        kind = "video"
    elif parsed.path.rstrip("/") == "/playlist" and playlist_id:
        kind = "playlist"
    elif channel_id:
        kind = "channel_id"
    elif handle:
        kind = "handle"
    elif username:
        kind = "username"
    elif playlist_id:
        kind = "playlist"
    else:
        kind = "other"
    return YouTubeReference(
        raw=raw,
        video_id=video_id,
        playlist_id=playlist_id,
        channel_id=channel_id,
        handle=handle,
        username=username,
        kind=kind,
    )


def youtube_video_id(url: str) -> str:
    return parse_youtube_reference(url).video_id


def youtube_source_descriptor(url: str) -> tuple[str, str]:
    ref = parse_youtube_reference(url)
    if ref.kind == "video":
        return "video", ref.video_id
    if ref.kind == "playlist":
        return "playlist", ref.playlist_id
    if ref.kind == "channel_id":
        return "channel_id", ref.channel_id
    if ref.kind == "handle":
        return "handle", ref.handle
    if ref.kind == "username":
        return "username", ref.username
    return "other", ref.raw
