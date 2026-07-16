# ============================================
# ROUTE FILE - HOME
# Serves the status page and provides live stats api
# ============================================

from fastapi import APIRouter
from fastapi.responses import FileResponse

from core.system_stats import get_system_snapshot, get_process_start_iso
import database
from version import VERSION

router = APIRouter()


@router.api_route("/", methods=["GET", "HEAD"])
def serve_home_page():
    return FileResponse("public/index.html")


@router.get("/docs")
def serve_docs_page():
    return FileResponse("public/docs.html")


@router.get("/api/stats")
def get_stats():
    system_snapshot = get_system_snapshot()

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

    return {
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
