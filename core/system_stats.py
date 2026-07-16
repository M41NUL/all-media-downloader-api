# ============================================
# CORE MODULE - SYSTEM STATS
# CPU, memory and process uptime monitoring
# ============================================

import time
from datetime import datetime, timezone
import psutil

_process_start_time = time.time()


def get_uptime_seconds() -> float:
    return time.time() - _process_start_time


def get_process_start_iso() -> str:
    return datetime.fromtimestamp(_process_start_time, tz=timezone.utc).isoformat()


def get_cpu_percent() -> float:
    return psutil.cpu_percent(interval=None)


def get_memory_usage_mb() -> float:
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)


def get_system_memory_percent() -> float:
    return psutil.virtual_memory().percent


def get_system_snapshot() -> dict:
    return {
        "uptime": get_uptime_seconds(),
        "cpuPercent": get_cpu_percent(),
        "memoryMB": get_memory_usage_mb(),
        "systemMemoryPercent": get_system_memory_percent(),
    }
