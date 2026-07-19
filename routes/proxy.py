# ============================================
# ROUTE FILE - PROXY
# Streams a resolved CDN video through this server.
#
# Why this exists: TikTok's signed CDN urls are short-lived and are
# commonly bound (via IP / session heuristics on TikTok's side) to the
# client that resolved them. When the raw video_url from /api/download or
# /api/tiktok is handed to a *different* client (e.g. the Telegram bot
# running on another server) and fetched from there, TikTok's CDN often
# responds with 403 Forbidden.
#
# Fetching the CDN url from here instead — the same server/process that
# just resolved it via yt-dlp — avoids that mismatch entirely.
# ============================================

# ============================================
# ROUTE FILE - PROXY
# Streams video to the bot.
#
# TikTok: the file was already downloaded to local disk at resolve time
# (see core/service.py + core/downloader.py:download_with_ytdlp) because
# handing out TikTok's signed CDN url — even re-fetched from this same
# server with yt-dlp's own resolved headers — still gets rejected by
# TikTok's CDN. So for TikTok, proxy_token always points to a local file;
# this endpoint just streams it and cleans it up afterward.
#
# Facebook/Instagram: these still work fine being fetched directly from
# their CDN urls, so video_url + generic headers continues to be used.
# ============================================

import os

from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import StreamingResponse
import requests

from core.auth import verify_api_key
from core import resolve_cache

router = APIRouter()

_PLATFORM_HEADERS = {
    "facebook": {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
        ),
        "Referer": "https://www.facebook.com/",
        "Origin": "https://www.facebook.com",
        "Accept": "*/*",
    },
    "instagram": {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
        ),
        "Referer": "https://www.instagram.com/",
        "Origin": "https://www.instagram.com",
        "Accept": "*/*",
    },
}

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": "*/*",
}


def _stream_local_file(file_path: str, token: str):
    def iterator():
        try:
            with open(file_path, "rb") as fh:
                while True:
                    chunk = fh.read(64 * 1024)
                    if not chunk:
                        break
                    yield chunk
        finally:
            resolve_cache.cleanup(token)

    response_headers = {}
    try:
        response_headers["Content-Length"] = str(os.path.getsize(file_path))
    except OSError:
        pass

    return StreamingResponse(
        iterator(),
        media_type="video/mp4",
        headers=response_headers,
    )


def _stream_remote_url(video_url: str, platform: str):
    headers = _PLATFORM_HEADERS.get((platform or "").lower(), _DEFAULT_HEADERS)

    try:
        upstream = requests.get(video_url, headers=headers, stream=True, timeout=45)
        upstream.raise_for_status()
    except requests.exceptions.HTTPError as error:
        status = error.response.status_code if error.response is not None else 502
        raise HTTPException(
            status_code=502,
            detail=f"Source CDN rejected the request (HTTP {status}). Please send the link again.",
        )
    except requests.exceptions.RequestException as error:
        raise HTTPException(status_code=502, detail=f"Failed to reach source CDN: {error}")

    def iterator():
        try:
            for chunk in upstream.iter_content(chunk_size=64 * 1024):
                if chunk:
                    yield chunk
        finally:
            upstream.close()

    response_headers = {}
    content_length = upstream.headers.get("Content-Length")
    if content_length:
        response_headers["Content-Length"] = content_length

    return StreamingResponse(
        iterator(),
        media_type=upstream.headers.get("Content-Type", "video/mp4"),
        headers=response_headers,
    )


@router.get("/api/proxy-video")
def proxy_video(
    video_url: str = Query("", description="Direct CDN url (facebook/instagram only)"),
    platform: str = Query("", description="Platform the video belongs to"),
    proxy_token: str = Query("", description="Token from /api/download's proxy_token field (tiktok — points to a locally downloaded file)"),
    api_key: str = Depends(verify_api_key),
):
    if proxy_token:
        file_path = resolve_cache.get_file(proxy_token)
        if not file_path:
            raise HTTPException(
                status_code=410,
                detail="This download link has expired or was already used. Please send the link again.",
            )
        return _stream_local_file(file_path, proxy_token)

    if video_url:
        return _stream_remote_url(video_url, platform)

    raise HTTPException(status_code=400, detail="No proxy_token or video_url provided")
