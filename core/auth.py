# ============================================
# CORE MODULE - AUTH
# Shared api key verification dependency
# ============================================

from fastapi import Header, HTTPException, Query
from typing import Optional

from config import API_KEY


def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="x-api-key"),
    api_key: Optional[str] = Query(None, description="Fallback for contexts that can't send a custom header (e.g. a plain browser link/download)"),
):
    provided = x_api_key or api_key
    if provided != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing api key")
    return provided
