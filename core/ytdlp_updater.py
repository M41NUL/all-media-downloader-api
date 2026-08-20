import subprocess
import sys
import threading

import requests
import yt_dlp

from config import YTDLP_AUTO_UPDATE, YTDLP_UPDATE_CHECK_INTERVAL_SECONDS

PYPI_URL = "https://pypi.org/pypi/yt-dlp/json"

_last_checked_version = None
_last_update_status = "not_checked"


def get_installed_version() -> str:
    return yt_dlp.version.__version__


def get_latest_version() -> str:
    response = requests.get(PYPI_URL, timeout=15)
    response.raise_for_status()
    return response.json()["info"]["version"]


def update_ytdlp() -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "--no-cache-dir", "yt-dlp"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def check_and_update() -> dict:
    global _last_checked_version, _last_update_status

    installed = get_installed_version()

    try:
        latest = get_latest_version()
    except Exception as error:
        _last_update_status = f"check_failed: {error}"
        return {"installed": installed, "latest": None, "updated": False, "status": _last_update_status}

    _last_checked_version = latest

    if latest == installed:
        _last_update_status = "up_to_date"
        return {"installed": installed, "latest": latest, "updated": False, "status": _last_update_status}

    print(f"[yt-dlp-updater] New version available: {installed} -> {latest}. Updating...")
    success = update_ytdlp()

    if success:
        _last_update_status = f"updated_to_{latest}_pending_restart"
        print(f"[yt-dlp-updater] yt-dlp updated to {latest}. Restart process to load new version.")
    else:
        _last_update_status = "update_failed"
        print("[yt-dlp-updater] yt-dlp update failed, will retry on next check.")

    return {"installed": installed, "latest": latest, "updated": success, "status": _last_update_status}


def get_status() -> dict:
    return {
        "installedVersion": get_installed_version(),
        "latestKnownVersion": _last_checked_version,
        "autoUpdateEnabled": YTDLP_AUTO_UPDATE,
        "lastStatus": _last_update_status,
    }


def start_background_updater():
    if not YTDLP_AUTO_UPDATE:
        print("[yt-dlp-updater] Auto-update disabled via config.")
        return

    def _loop():
        check_and_update()
        timer = threading.Timer(YTDLP_UPDATE_CHECK_INTERVAL_SECONDS, _loop)
        timer.daemon = True
        timer.start()

    initial_delay = threading.Timer(5, _loop)
    initial_delay.daemon = True
    initial_delay.start()
