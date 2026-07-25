# ============================================
# ROUTE FILE - HOME
# Serves the status page and provides live stats api
# ============================================

import time

from fastapi import APIRouter
from fastapi.responses import FileResponse

from core.system_stats import get_system_snapshot, get_process_start_iso
import database
from version import VERSION

router = APIRouter()

_stats_cache = {"data": None, "ts": 0}
_STATS_CACHE_TTL_SECONDS = 4


@router.api_route("/", methods=["GET", "HEAD"])
def serve_home_page():
    return FileResponse("public/index.html")


@router.get("/docs")
def serve_docs_page():
    return FileResponse("public/docs.html")


@router.get("/api/stats")
def get_stats():
    now = time.time()

    # Serve from cache if fresh. This avoids hitting Firebase with several
    # blocking calls on every single poll (dashboard polls every 2s), which
    # was causing requests to queue up / time out and the dashboard to flap
    # between Online and Offline.
    if _stats_cache["data"] is not None and (now - _stats_cache["ts"]) < _STATS_CACHE_TTL_SECONDS:
        cached = dict(_stats_cache["data"])
        cached["uptime"] = get_system_snapshot().get("uptime", cached.get("uptime", 0))
        return cached

    try:
        system_snapshot = get_system_snapshot()
    except Exception:
        system_snapshot = {"uptime": 0, "cpuPercent": 0, "memoryMB": 0, "systemMemoryPercent": 0}

    try:
        stats_summary = database.get_stats_summary()
    except Exception:
        stats_summary = {"users": 0, "downloads": 0, "byPlatform": {}, "successRate": None, "avgTimeSec": None}

    try:
        recent_activity = database.get_recent_activity(limit=5)
    except Exception:
        recent_activity = []

    try:
        last_7_days = database.get_last_7_days()
    except Exception:
        last_7_days = []

    try:
        restart_count = database.get_restart_count()
    except Exception:
        restart_count = 0

    result = {
        "status": "operational",
        "uptime": system_snapshot["uptime"],
        "users": stats_summary["users"],
        "downloads": stats_summary["downloads"],
        "byPlatform": stats_summary["byPlatform"],
        "successRate": stats_summary["successRate"],
        "memoryMB": system_snapshot["memoryMB"],
        "cpuPercent": system_snapshot["cpuPercent"],
        "systemMemoryPercent": system_snapshot["systemMemoryPercent"],
        "avgTimeSec": stats_summary["avgTimeSec"],
        "version": VERSION,
        "last7Days": last_7_days,
        "recentActivity": recent_activity,
        "dailyLimit": None,
        "restarts": restart_count,
        "lastDeploy": get_process_start_iso(),
    }

    _stats_cache["data"] = result
    _stats_cache["ts"] = now

    return result
