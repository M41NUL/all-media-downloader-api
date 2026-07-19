# ============================================
# CORE MODULE - RESOLVE CACHE
# Short-lived in-memory cache mapping a token -> a locally downloaded file
#
# Why this exists: TikTok's CDN rejects fetches for its signed video urls
# when they come from a different process/server than the one that
# resolved them via yt-dlp (confirmed even when passing yt-dlp's own
# resolved headers along). So instead of handing out a CDN url, the API
# actually downloads the file to local disk at resolve time and hands back
# an opaque token; the proxy-video endpoint looks the token up to find the
# local file and streams it directly — no second CDN fetch happens at all.
#
# In-memory and single-process only — fine for a single Render free-tier
# instance. Entries (and their temp files/dirs) are cleaned up once
# consumed, or after TTL expiry as a safety net for abandoned downloads.
# ============================================

import os
import shutil
import time
import uuid
import threading

_TTL_SECONDS = 10 * 60  # safety net for files that are never claimed
_lock = threading.Lock()
_store = {}


def put_file(file_path: str) -> str:
    token = uuid.uuid4().hex
    with _lock:
        _store[token] = {
            "file_path": file_path,
            "expires_at": time.time() + _TTL_SECONDS,
        }
        _prune_locked()
    return token


def get_file(token: str):
    """
    Returns the file path for this token, or None if missing/expired.
    Does NOT delete the entry — call cleanup(token) once you're done
    streaming it, so a failed send can still be retried.
    """
    with _lock:
        entry = _store.get(token)
        if not entry:
            return None
        if entry["expires_at"] < time.time():
            _remove_locked(token)
            return None
        if not os.path.exists(entry["file_path"]):
            _remove_locked(token)
            return None
        return entry["file_path"]


def cleanup(token: str) -> None:
    with _lock:
        _remove_locked(token)


def _remove_locked(token: str) -> None:
    entry = _store.pop(token, None)
    if not entry:
        return
    file_path = entry["file_path"]
    try:
        parent_dir = os.path.dirname(file_path)
        if parent_dir and os.path.isdir(parent_dir):
            shutil.rmtree(parent_dir, ignore_errors=True)
        elif os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass


def _prune_locked():
    now = time.time()
    expired = [key for key, value in _store.items() if value["expires_at"] < now]
    for key in expired:
        _remove_locked(key)
