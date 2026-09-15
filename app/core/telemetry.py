"""Telemetry provider for system and hardware metrics."""

import os
import platform
import sys
import time
from typing import Any

import psutil

# Capture start time of process
_PROCESS_START_TIME = time.time()


def get_system_telemetry() -> dict[str, Any]:
    """Collect host/container hardware metrics."""
    # Memory
    mem = psutil.virtual_memory()
    ram_total_mb = round(mem.total / (1024**2), 2)
    ram_used_mb = round(mem.used / (1024**2), 2)
    ram_percent = mem.percent

    # CPU
    cpu_count = psutil.cpu_count(logical=True) or 1
    cpu_percent = psutil.cpu_percent(interval=None)

    # Disk
    disk = psutil.disk_usage("/")
    disk_total_gb = round(disk.total / (1024**3), 2)
    disk_used_gb = round(disk.used / (1024**3), 2)
    disk_percent = disk.percent

    # Uptime
    uptime_seconds = int(time.time() - _PROCESS_START_TIME)

    return {
        "hostname": os.uname().nodename if hasattr(os, "uname") else "ml-chege-jira",
        "uptime_seconds": uptime_seconds,
        "python_version": sys.version.split()[0],
        "platform": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "cpu_count": cpu_count,
        "cpu_percent": cpu_percent,
        "ram_total_mb": ram_total_mb,
        "ram_used_mb": ram_used_mb,
        "ram_percent": ram_percent,
        "disk_total_gb": disk_total_gb,
        "disk_used_gb": disk_used_gb,
        "disk_percent": disk_percent,
    }
