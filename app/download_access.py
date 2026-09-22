"""Source-access helpers for download retries.

Keeps cookie fallback policy out of the main application module.  Normal
configured cookie arguments remain authoritative; this module only adds a
browser-cookie retry for YouTube when the initial arguments did not already
include cookies.
"""

from __future__ import annotations

from typing import Any, Callable

from .youtube_url import is_youtube_url


def has_cookie_args(args: list[str]) -> bool:
    values = [str(value) for value in args]
    return "--cookies" in values or "--cookies-from-browser" in values


def browser_cookie_args(config: dict[str, Any]) -> list[str]:
    browser = str(config.get("browser_for_cookies") or "firefox").strip() or "firefox"
    return ["--cookies-from-browser", browser]


def add_browser_cookie_retry(base_args: list[str], config: dict[str, Any]) -> list[str]:
    args = list(base_args)
    if has_cookie_args(args):
        return args
    return args + browser_cookie_args(config)


def should_retry_with_browser_cookies(
    url: str,
    error_text: str,
    base_args: list[str],
    config: dict[str, Any],
) -> bool:
    if not bool(config.get("youtube_cookie_fallback", True)):
        return False
    if not is_youtube_url(url) or has_cookie_args(base_args):
        return False
    error = str(error_text or "").lower()
    return "403" in error or "forbidden" in error or "sign in" in error or "login" in error


def run_with_browser_cookie_fallback(
    base_args: list[str],
    url: str,
    config: dict[str, Any],
    runner: Callable[[list[str]], tuple[int, str, str]],
) -> tuple[int, str, str, bool]:
    """Run one yt-dlp command and retry once with browser cookies when warranted.

    Returns ``(rc, stdout, stderr, retried)``.  The caller owns timeouts and
    process execution; this helper owns only the retry policy.
    """
    args = list(base_args)
    rc, out, err = runner(args)
    if rc == 0 or not should_retry_with_browser_cookies(url, err or out, args, config):
        return rc, out, err, False
    retry_args = add_browser_cookie_retry(args, config)
    rc2, out2, err2 = runner(retry_args)
    return rc2, out2, err2, True


def build_youtube_download_attempts(
    base_args: list[str],
    url: str,
    quality: str,
    config: dict[str, Any],
    format_selector: Callable[[str], str],
) -> list[tuple[str, list[str]]]:
    """Build the normal + YouTube 403/cookie fallback download ladder."""
    args0 = list(base_args)
    fmt = format_selector(quality)
    attempts: list[tuple[str, list[str]]] = [("default", args0 + ["-f", fmt, url])]
    if not bool(config.get("youtube_403_fallback", True)) or not is_youtube_url(url):
        return attempts

    height = str(quality).lower()
    if height in ("best", "audio"):
        hls_fmt = "bestaudio/best" if height == "audio" else "best[protocol*=m3u8]/best"
    else:
        try:
            maximum = int(height)
            hls_fmt = (
                f"bestvideo[protocol*=m3u8][height<={maximum}]+bestaudio[protocol*=m3u8]/"
                f"best[protocol*=m3u8][height<={maximum}]/"
                f"bestvideo[height<={maximum}]+bestaudio/best[height<={maximum}]/best"
            )
        except Exception:
            hls_fmt = (
                "bestvideo[protocol*=m3u8][height<=1080]+bestaudio[protocol*=m3u8]/"
                "best[protocol*=m3u8][height<=1080]/"
                "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
            )

    clients = list(config.get("youtube_fallback_clients", ["web_safari", "web_embedded"]))
    for client in clients:
        client_args = list(args0)
        client_args += ["--extractor-args", f"youtube:player_client={client}", "-f", hls_fmt, url]
        attempts.append((str(client), client_args))

    if bool(config.get("youtube_cookie_fallback", True)) and not has_cookie_args(args0):
        cookie_base = add_browser_cookie_retry(args0, config)
        attempts.append(("browser-cookies", cookie_base + ["-f", fmt, url]))
        for client in clients:
            client_args = list(cookie_base)
            client_args += ["--extractor-args", f"youtube:player_client={client}", "-f", hls_fmt, url]
            attempts.append((f"browser-cookies-{client}", client_args))
    return attempts
