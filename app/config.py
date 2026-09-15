"""Application configuration loaded via pydantic-settings."""

import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration class for the ML backend.

    Accepts Railway's auto-injected MySQL variables as fallbacks so you only
    need to set API_KEY manually; all DB credentials are shared from the MySQL
    service reference variables (${{MySQL.MYSQLHOST}} etc.).
    """

    # Environment
    APP_ENV: Literal["development", "production", "testing"] = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    API_KEY: str = Field(
        default="chege_jira_ml_super_secret_key_2026",
        description="Shared secret API key required on all protected endpoints",
    )

    # Database — primary names (DB_*), with Railway MYSQL* as fallbacks resolved below
    DB_HOST: str = "mysql"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "root_password"
    DB_NAME: str = "db_chege_jira"

    # LLM Settings
    MODELS_DIR: Path = Path("/app/models")
    DEFAULT_MODEL: str = "phi3-mini"
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

    @model_validator(mode="after")
    def _resolve_db_from_railway(self) -> "Settings":
        """
        Apply Railway MySQL alias env vars as fallbacks when the primary DB_*
        vars are still at their defaults. Supports both individual vars and the
        MYSQL_URL / DATABASE_URL connection string formats.

        Priority:
          1. DB_HOST / DB_USER / DB_PASSWORD / DB_NAME (explicit, highest)
          2. MYSQL_URL or DATABASE_URL (full DSN string)
          3. MYSQLHOST / MYSQLUSER / MYSQLPASSWORD / MYSQLDATABASE (Railway auto)
        """
        env = os.environ

        # --- DSN parsing (MYSQL_URL or DATABASE_URL) ---
        dsn_raw = env.get("MYSQL_URL") or env.get("DATABASE_URL") or ""
        if dsn_raw:
            try:
                parsed = urlparse(dsn_raw)
                if self.DB_HOST == "mysql":
                    self.DB_HOST = parsed.hostname or self.DB_HOST
                if self.DB_PORT == 3306 and parsed.port:
                    self.DB_PORT = parsed.port
                if self.DB_USER == "root":
                    self.DB_USER = parsed.username or self.DB_USER
                if self.DB_PASSWORD == "root_password":
                    self.DB_PASSWORD = parsed.password or self.DB_PASSWORD
                if self.DB_NAME == "db_chege_jira":
                    self.DB_NAME = (parsed.path or "/").lstrip("/") or self.DB_NAME
            except Exception:
                pass

        # --- Railway short-form aliases (MYSQLHOST / MYSQLUSER / etc.) ---
        if self.DB_HOST == "mysql" and env.get("MYSQLHOST"):
            self.DB_HOST = env["MYSQLHOST"]
        if self.DB_USER == "root" and env.get("MYSQLUSER"):
            self.DB_USER = env["MYSQLUSER"]
        if self.DB_PASSWORD == "root_password" and env.get("MYSQLPASSWORD"):
            self.DB_PASSWORD = env["MYSQLPASSWORD"]
        if self.DB_NAME == "db_chege_jira":
            self.DB_NAME = env.get("MYSQLDATABASE") or env.get("MYSQL_DATABASE") or self.DB_NAME
        if self.DB_PORT == 3306 and env.get("MYSQLPORT"):
            try:
                self.DB_PORT = int(env["MYSQLPORT"])
            except ValueError:
                pass

        return self

    @property
    def async_database_url(self) -> str:
        """Generate SQLAlchemy async MySQL connection URL."""
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )


settings = Settings()
