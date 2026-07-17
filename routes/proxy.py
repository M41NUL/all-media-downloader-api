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

from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import StreamingResponse
import requests

from core.auth import verify_api_key

router = APIRouter()

# Per-platform headers a real browser/app would send. TikTok in particular
# checks Referer/Origin against tiktok.com and rejects mismatches.
_PLATFORM_HEADERS = {
    "tiktok": {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
        ),
        "Referer": "https://www.tiktok.com/",
        "Origin": "https://www.tiktok.com",
        "Accept": "*/*",
    },
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


@router.get("/api/proxy-video")
def proxy_video(
    video_url: str = Query(..., description="Direct CDN url returned by a resolve endpoint"),
    platform: str = Query("", description="Platform the video_url belongs to (tiktok/facebook/instagram)"),
    api_key: str = Depends(verify_api_key),
):
    headers = _PLATFORM_HEADERS.get((platform or "").lower(), _DEFAULT_HEADERS)

    try:
        upstream = requests.get(
            video_url,
            headers=headers,
            stream=True,
            timeout=45,
        )
        upstream.raise_for_status()
    except requests.exceptions.HTTPError as error:
        status = error.response.status_code if error.response is not None else 502
        raise HTTPException(
            status_code=502,
            detail=f"Source CDN rejected the request (HTTP {status}). Please send the link again.",
        )
    except requests.exceptions.RequestException as error:
        raise HTTPException(status_code=502, detail=f"Failed to reach source CDN: {error}")

    def stream():
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
        stream(),
        media_type=upstream.headers.get("Content-Type", "video/mp4"),
        headers=response_headers,
    )
