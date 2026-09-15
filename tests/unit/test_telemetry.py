"""Tests for system telemetry collection."""

from app.core.telemetry import get_system_telemetry


def test_system_telemetry_fields() -> None:
    """Check that hardware telemetry returns all required fields and valid metrics."""
    telemetry = get_system_telemetry()

    assert "hostname" in telemetry
    assert "uptime_seconds" in telemetry
    assert "python_version" in telemetry
    assert "platform" in telemetry
    assert "cpu_count" in telemetry
    assert telemetry["cpu_count"] >= 1
    assert "ram_total_mb" in telemetry
    assert telemetry["ram_total_mb"] > 0
    assert "ram_used_mb" in telemetry
    assert "disk_total_gb" in telemetry
