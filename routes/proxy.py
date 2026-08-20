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


def _content_disposition(filename: str) -> str:
    ascii_fallback = filename.encode("ascii", "ignore").decode("ascii").strip() or "video.mp4"
    from urllib.parse import quote
    encoded = quote(filename)
    return f'attachment; filename="{ascii_fallback}"; filename*=UTF-8\'\'{encoded}'


def _stream_local_file(file_path: str, token: str, filename: str = None):
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

    response_headers = {
        "Content-Disposition": _content_disposition(filename or os.path.basename(file_path)),
    }
    try:
        response_headers["Content-Length"] = str(os.path.getsize(file_path))
    except OSError:
        pass

    return StreamingResponse(
        iterator(),
        media_type="video/mp4",
        headers=response_headers,
    )


def _stream_remote_url(video_url: str, platform: str, filename: str = None):
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

    response_headers = {
        "Content-Disposition": _content_disposition(filename or "video.mp4"),
    }
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
    filename: str = Query("", description="Desired output filename (e.g. video title). Optional — falls back to the resolved title or a generic name."),
    api_key: str = Depends(verify_api_key),
):
    if proxy_token:
        file_path = resolve_cache.get_file(proxy_token)
        if not file_path:
            raise HTTPException(
                status_code=410,
                detail="This download link has expired or was already used. Please send the link again.",
            )
        resolved_name = filename or resolve_cache.get_filename(proxy_token)
        return _stream_local_file(file_path, proxy_token, resolved_name)

    if video_url:
        return _stream_remote_url(video_url, platform, filename)

    raise HTTPException(status_code=400, detail="No proxy_token or video_url provided")
