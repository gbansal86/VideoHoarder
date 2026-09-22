"""Immutable per-job download options.

The desktop queue captures these values when a job is enqueued.  They are then
owned by that job and must not be implemented by temporarily mutating the
process-wide CFG/RUNTIME dictionaries.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence


def _bounded_int(value: Any, default: int, low: int, high: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(low, min(high, parsed))


@dataclass(frozen=True, slots=True)
class DownloadOptions:
    action: str = "full_download"
    resolve_embedded: bool = False
    quality: str = "1080"
    use_ollama: bool = False
    save_srt: bool = False
    prefix_upload_date: bool = False
    download_comments: bool = False
    category: str = "Entertainment"
    vtt: bool = True
    category_mode: str = "source"
    smart_resume: bool = True
    parallel_videos: int = 2
    concurrent_fragments: int = 4

    @classmethod
    def from_values(
        cls,
        *,
        action: str = "full_download",
        resolve_embedded: bool = False,
        quality: str = "1080",
        use_ollama: bool = False,
        save_srt: bool = False,
        prefix_upload_date: bool = False,
        download_comments: bool = False,
        category: str = "Entertainment",
        vtt: bool = True,
        category_mode: str = "source",
        smart_resume: bool = True,
        parallel_videos: int = 2,
        concurrent_fragments: int = 4,
    ) -> "DownloadOptions":
        return cls(
            action=str(action or "full_download"),
            resolve_embedded=bool(resolve_embedded),
            quality=str(quality or "1080"),
            use_ollama=bool(use_ollama),
            save_srt=bool(save_srt),
            prefix_upload_date=bool(prefix_upload_date),
            download_comments=bool(download_comments),
            category=str(category or "Entertainment"),
            vtt=bool(vtt),
            category_mode=str(category_mode or "source"),
            smart_resume=bool(smart_resume),
            parallel_videos=_bounded_int(parallel_videos, 2, 1, 5),
            concurrent_fragments=_bounded_int(concurrent_fragments, 4, 1, 16),
        )

    @classmethod
    def from_settings(cls, values: Mapping[str, Any] | None, *, action: str = "full_download") -> "DownloadOptions":
        values = values or {}
        return cls.from_values(
            action=action,
            quality=str(values.get("download_quality") or "1080"),
            save_srt=bool(values.get("save_srt_default")),
            prefix_upload_date=bool(values.get("prefix_upload_date_default")),
            use_ollama=bool(values.get("ai_enabled", False)) and not bool(values.get("fast_no_llm_mode", False)),
            vtt=bool(values.get("download_subtitles", True)),
            smart_resume=bool(values.get("smart_resume", True)),
            parallel_videos=values.get("parallel_videos", 2),
            concurrent_fragments=values.get("concurrent_fragments", 4),
        )

    @classmethod
    def from_workflow_call(cls, args: Sequence[Any], kwargs: Mapping[str, Any] | None = None) -> "DownloadOptions | None":
        """Capture ``web_download_workflow`` options from an enqueue call.

        ``args`` includes the URL list at index 0.  A non-workflow task may not
        have these positions; in that case ``None`` is returned.
        """

        kwargs = dict(kwargs or {})
        try:
            action = kwargs.get("action", args[1] if len(args) > 1 else "full_download")
            if str(action) not in {"full_download", "media_only"}:
                return None
            return cls.from_values(
                action=str(action),
                resolve_embedded=kwargs.get("resolve_embedded", args[2] if len(args) > 2 else False),
                quality=kwargs.get("quality", args[3] if len(args) > 3 else "1080"),
                use_ollama=kwargs.get("use_ollama", args[4] if len(args) > 4 else False),
                save_srt=kwargs.get("save_srt", args[5] if len(args) > 5 else False),
                prefix_upload_date=kwargs.get("prefix_upload_date", args[6] if len(args) > 6 else False),
                download_comments=kwargs.get("download_comments", args[7] if len(args) > 7 else False),
                category=kwargs.get("category", args[8] if len(args) > 8 else "Entertainment"),
                vtt=kwargs.get("vtt", args[9] if len(args) > 9 else True),
                category_mode=kwargs.get("category_mode", args[10] if len(args) > 10 else "source"),
                smart_resume=kwargs.get("smart_resume", args[11] if len(args) > 11 else True),
                parallel_videos=kwargs.get("parallel_videos", 2),
                concurrent_fragments=kwargs.get("concurrent_fragments", 4),
            )
        except Exception:
            return None

    @property
    def download_video(self) -> bool:
        return self.action in {"full_download", "media_only"} and self.quality != "audio"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
