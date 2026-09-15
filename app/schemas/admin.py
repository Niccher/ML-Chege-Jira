"""Admin telemetry and runtime configuration schemas."""

from typing import Any

from pydantic import BaseModel, Field


class ContainerTelemetry(BaseModel):
    hostname: str
    uptime_seconds: int
    python_version: str
    platform: str
    cpu_count: int
    cpu_percent: float
    ram_total_mb: float
    ram_used_mb: float
    ram_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_percent: float


class LlmRuntimeTelemetry(BaseModel):
    llama_cpp_version: str
    fastapi_version: str
    default_model: str
    n_gpu_layers: int
    n_threads: int
    n_ctx: int
    compute_mode: str


class DatabaseTelemetry(BaseModel):
    connected: bool
    host: str
    database: str
    ai_tables_present: bool


class TelemetryData(BaseModel):
    container: ContainerTelemetry
    llm_runtime: LlmRuntimeTelemetry
    models: dict[str, Any]
    database: DatabaseTelemetry


class ConfigResponse(BaseModel):
    default_model: str
    n_gpu_layers: int
    n_threads: int
    n_ctx: int
    updated_at: str | None = None


class ConfigUpdate(BaseModel):
    default_model: str | None = Field(default=None, description="New default model key")
    n_gpu_layers: int | None = Field(default=None, ge=-1, le=100, description="0=CPU, -1=Full GPU")
    n_threads: int | None = Field(default=None, ge=1, le=64, description="CPU thread count")
    n_ctx: int | None = Field(default=None, ge=512, le=32768, description="Context window size")
