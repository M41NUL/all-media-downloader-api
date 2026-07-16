# ============================================
# ROUTE FILE - AUTO
# Single endpoint that auto detects the platform from the url
# ============================================

import time
from fastapi import APIRouter, Query, Request, HTTPException, Depends

from core.service import resolve_media, ExtractionFailedError
from core.detector import detect_platform
from core.auth import verify_api_key
import database

router = APIRouter()


@router.get("/api/download")
def auto_download(
    request: Request,
    url: str = Query(..., description="Any supported video url"),
    api_key: str = Depends(verify_api_key),
):
    detected = detect_platform(url)

    if detected == "unknown":
        raise HTTPException(status_code=400, detail="Url platform is not supported")

    client_id = request.client.host if request.client else "unknown"
    database.register_user(client_id)

    start_time = time.time()

    try:
        result = resolve_media(url, detected)
    except ExtractionFailedError as error:
        database.log_download(detected, False, time.time() - start_time)
        raise HTTPException(status_code=422, detail=str(error))

    database.log_download(detected, True, time.time() - start_time)

    return {
        "success": True,
        "caption": result["caption"],
        "platform": result["platform"],
        "format": result["format"],
        "size": result["size"],
        "duration": result["duration"],
        "video_url": result["video_url"],
        "thumbnail_url": result.get("thumbnail_url"),
        "quality": result.get("quality"),
    }
