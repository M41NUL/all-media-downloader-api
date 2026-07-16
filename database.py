# ============================================
# DATABASE FILE
# Firebase connection and stats logging
# ============================================

import json
import time
import firebase_admin
from firebase_admin import credentials, db

from config import FIREBASE_CREDENTIALS_JSON, FIREBASE_DATABASE_URL

_firebase_app = None


def init_firebase():
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    if not FIREBASE_CREDENTIALS_JSON or not FIREBASE_DATABASE_URL:
        return None

    credentials_dict = json.loads(FIREBASE_CREDENTIALS_JSON)
    cred = credentials.Certificate(credentials_dict)

    _firebase_app = firebase_admin.initialize_app(cred, {
        "databaseURL": FIREBASE_DATABASE_URL,
    })

    return _firebase_app


def _get_stats_ref():
    if init_firebase() is None:
        return None
    return db.reference("stats")


def _get_users_ref():
    if init_firebase() is None:
        return None
    return db.reference("users")


def increment_restart_count() -> int:
    stats_ref = _get_stats_ref()

    if stats_ref is None:
        return 0

    try:
        counter_ref = stats_ref.child("counters").child("restarts")
        current = counter_ref.get() or 0
        new_value = current + 1
        counter_ref.set(new_value)
        return new_value
    except Exception:
        return 0


def get_restart_count() -> int:
    stats_ref = _get_stats_ref()

    if stats_ref is None:
        return 0

    try:
        return stats_ref.child("counters").child("restarts").get() or 0
    except Exception:
        return 0


def log_download(platform: str, success: bool, duration_taken: float):
    stats_ref = _get_stats_ref()

    if stats_ref is None:
        return

    timestamp = int(time.time())

    entry = {
        "platform": platform,
        "success": success,
        "duration_taken": duration_taken,
        "timestamp": timestamp,
    }

    stats_ref.child("downloads").push(entry)

    counter_ref = stats_ref.child("counters").child(platform)
    current = counter_ref.get() or 0
    counter_ref.set(current + 1)

    total_ref = stats_ref.child("counters").child("total")
    total_current = total_ref.get() or 0
    total_ref.set(total_current + 1)


def register_user(user_id: str):
    users_ref = _get_users_ref()

    if users_ref is None or not user_id:
        return

    safe_id = str(user_id).replace(".", "_").replace("#", "_").replace("$", "_").replace("[", "_").replace("]", "_").replace("/", "_")

    try:
        users_ref.child(safe_id).set({
            "last_seen": int(time.time()),
        })
    except Exception:
        pass


def get_stats_summary() -> dict:
    stats_ref = _get_stats_ref()
    users_ref = _get_users_ref()

    if stats_ref is None:
        return {
            "downloads": 0,
            "byPlatform": {"tiktok": 0, "instagram": 0, "facebook": 0},
            "users": 0,
            "successRate": None,
        }

    counters = stats_ref.child("counters").get() or {}
    users = users_ref.get() or {} if users_ref is not None else {}

    recent_downloads = stats_ref.child("downloads").order_by_key().limit_to_last(200).get() or {}
    success_count = sum(1 for entry in recent_downloads.values() if entry.get("success"))
    total_recent = len(recent_downloads)
    success_rate = round((success_count / total_recent) * 100) if total_recent > 0 else None

    durations = [
        entry.get("duration_taken")
        for entry in recent_downloads.values()
        if isinstance(entry.get("duration_taken"), (int, float))
    ]
    avg_time_sec = round(sum(durations) / len(durations), 2) if durations else None

    return {
        "downloads": counters.get("total", 0),
        "byPlatform": {
            "tiktok": counters.get("tiktok", 0),
            "instagram": counters.get("instagram", 0),
            "facebook": counters.get("facebook", 0),
        },
        "users": len(users),
        "successRate": success_rate,
        "avgTimeSec": avg_time_sec,
    }


def get_last_7_days() -> list:
    stats_ref = _get_stats_ref()

    if stats_ref is None:
        return []

    from datetime import datetime, timezone

    seven_days_ago = int(time.time()) - (7 * 24 * 60 * 60)

    try:
        all_downloads = stats_ref.child("downloads").order_by_child("timestamp").start_at(seven_days_ago).get() or {}
    except Exception:
        all_downloads = stats_ref.child("downloads").order_by_key().limit_to_last(500).get() or {}

    day_counts = {}
    for i in range(7):
        day_key = datetime.fromtimestamp(
            int(time.time()) - (6 - i) * 86400, tz=timezone.utc
        ).strftime("%Y-%m-%d")
        day_counts[day_key] = 0

    for entry in all_downloads.values():
        ts = entry.get("timestamp")
        if not ts:
            continue
        day_key = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        if day_key in day_counts:
            day_counts[day_key] += 1

    return [{"date": day, "downloads": count} for day, count in day_counts.items()]


def get_recent_activity(limit: int = 5) -> list:
    stats_ref = _get_stats_ref()

    if stats_ref is None:
        return []

    recent = stats_ref.child("downloads").order_by_key().limit_to_last(limit).get() or {}

    entries = list(recent.values())
    entries.sort(key=lambda entry: entry.get("timestamp", 0), reverse=True)

    activity = []
    for entry in entries:
        activity.append({
            "platform": entry.get("platform"),
            "time": entry.get("timestamp"),
        })

    return activity
