# ============================================
# CORE MODULE - MODELS
# Shared response data structures
# ============================================

from typing import Optional
from pydantic import BaseModel


class MediaResult(BaseModel):
    platform: str
    caption: str
    format: str
    size: str
    duration: str
    video_url: str
    thumbnail_url: Optional[str] = None
    quality: Optional[str] = None


class ErrorResult(BaseModel):
    success: bool = False
    message: str
