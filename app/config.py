"""Application configuration loaded via pydantic-settings."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration class for the ML backend."""

    # Environment
    APP_ENV: Literal["development", "production", "testing"] = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    API_KEY: str = Field(
        default="chege_jira_ml_super_secret_key_2026",
        description="Shared secret API key required on all protected endpoints",
    )

    # Database
    DB_HOST: str = "mysql"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "root_password"
    DB_NAME: str = "db_chege_jira"

    # LLM Settings
    MODELS_DIR: Path = Path("/app/models")
    DEFAULT_MODEL: str = "mistral-7b"
    N_GPU_LAYERS: int = 0
    N_THREADS: int = 4
    N_CTX: int = 4096

    # Model Mapping (key -> filename)
    MODEL_FILES: dict[str, str] = {
        "mistral-7b": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "llama3-8b": "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf",
        "phi3-mini": "Phi-3-mini-4k-instruct.Q4_K_M.gguf",
        "deepseek-7b": "deepseek-coder-7b-instruct.Q4_K_M.gguf",
    }

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:9001",
        "http://127.0.0.1:9001",
        "http://chege-jira-webapp:80",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def async_database_url(self) -> str:
        """Generate SQLAlchemy async MySQL connection URL."""
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )


settings = Settings()
