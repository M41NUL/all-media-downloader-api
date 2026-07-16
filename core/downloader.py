# ============================================
# CORE MODULE - DOWNLOADER
# Primary media extraction engine using yt-dlp
# yt-dlp only - no third-party scraper fallback
# ============================================

import yt_dlp
import requests
import re
import json
import base64
from urllib.parse import urlparse, parse_qs, unquote

from core.utils import format_size, format_duration, clean_caption
from config import PREFERRED_QUALITY


class DownloaderError(Exception):
    pass


def _get_size_via_head(video_url: str):
    try:
        resp = requests.head(video_url, timeout=8, allow_redirects=True)
        content_length = resp.headers.get("Content-Length")
        if content_length:
            return int(content_length)
    except Exception:
        pass
    return None


def _get_duration_from_url(video_url: str):
    try:
        parsed = urlparse(video_url)
        params = parse_qs(parsed.query)
        efg_values = params.get("efg")
        if not efg_values:
            return None

        efg_raw = unquote(efg_values[0])
        padded = efg_raw + "=" * (-len(efg_raw) % 4)
        decoded = base64.b64decode(padded)
        efg_data = json.loads(decoded)

        duration = efg_data.get("duration_s")
        if duration:
            return float(duration)
    except Exception:
        pass
    return None


def _format_string_for(platform: str) -> str:
    if platform == "tiktok":
        return "best[ext=mp4][vcodec!=none][acodec!=none]/best[ext=mp4]/best"
    if platform == "facebook":
        return (
            "best[ext=mp4][vcodec!=none][acodec!=none][height>=720]/"
            "best[ext=mp4][vcodec!=none][acodec!=none][height>=480]/"
            "best[ext=mp4][vcodec!=none][acodec!=none]/"
            "best[ext=mp4]/best"
        )
    if platform == "instagram":
        return "best[ext=mp4][vcodec!=none][acodec!=none]/best[ext=mp4]/best"
    return "best[ext=mp4][vcodec!=none][acodec!=none]/best[ext=mp4]/best"


def extract_with_ytdlp(url: str, platform: str) -> dict:
    ydl_options = {
        "quiet": True,
        "no_warnings": True,
        "format": _format_string_for(platform),
        "noplaylist": True,
        "playlist_items": "1",
        "extract_flat": False,
        "skip_download": True,
        "socket_timeout": 30,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as error:
        raise DownloaderError(str(error))

    if not info:
        raise DownloaderError("No data returned from extractor")

    video_url = info.get("url")

    if not video_url and info.get("formats"):
        formats = info.get("formats")
        best_format = formats[-1]
        video_url = best_format.get("url")
    else:
        best_format = None

    if not video_url:
        raise DownloaderError("Could not resolve direct video url")

    caption_source = info.get("description") or info.get("title") or ""

    size_bytes = info.get("filesize") or info.get("filesize_approx")
    if not size_bytes and best_format:
        size_bytes = best_format.get("filesize") or best_format.get("filesize_approx")
    if not size_bytes and info.get("formats"):
        for fmt in reversed(info.get("formats")):
            candidate = fmt.get("filesize") or fmt.get("filesize_approx")
            if candidate:
                size_bytes = candidate
                break

    if not size_bytes:
        size_bytes = _get_size_via_head(video_url)

    duration_seconds = info.get("duration")
    if not duration_seconds and best_format:
        duration_seconds = best_format.get("duration")
    if not duration_seconds:
        requested = info.get("requested_downloads")
        if requested and isinstance(requested, list):
            duration_seconds = requested[0].get("duration")
    if not duration_seconds:
        duration_seconds = _get_duration_from_url(video_url)

    ext = info.get("ext", "mp4")

    result = {
        "platform": platform,
        "caption": clean_caption(caption_source),
        "format": ext,
        "size": format_size(size_bytes),
        "duration": format_duration(duration_seconds),
        "video_url": video_url,
        "thumbnail_url": info.get("thumbnail"),
        "quality": info.get("format_note") or PREFERRED_QUALITY,
    }

    return result
