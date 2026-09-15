"""Schema guard ensuring that required ai_* tables exist in MySQL."""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)

DDL_STATEMENTS: list[tuple[str, str]] = [
    (
        "ai_config",
        """
        CREATE TABLE IF NOT EXISTS ai_config (
            id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            default_model   VARCHAR(64)  NOT NULL DEFAULT 'mistral-7b',
            n_gpu_layers    INT          NOT NULL DEFAULT 0,
            n_threads       INT          NOT NULL DEFAULT 4,
            n_ctx           INT          NOT NULL DEFAULT 4096,
            updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """,
    ),
    (
        "ai_config_seed",
        """
        INSERT INTO ai_config (id, default_model, n_gpu_layers, n_threads, n_ctx)
        VALUES (1, 'mistral-7b', 0, 4, 4096)
        ON DUPLICATE KEY UPDATE id=id;
        """,
    ),
    (
        "ai_task_enhancements",
        """
        CREATE TABLE IF NOT EXISTS ai_task_enhancements (
            id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            task_id             INT NOT NULL,
            summary             TEXT,
            acceptance_criteria JSON,
            story_points        TINYINT UNSIGNED,
            priority            ENUM('low','medium','high','critical'),
            model_used          VARCHAR(64),
            tokens_used         INT UNSIGNED,
            created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_task_id (task_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """,
    ),
    (
        "ai_sprint_summaries",
        """
        CREATE TABLE IF NOT EXISTS ai_sprint_summaries (
            id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            sprint_id       INT NOT NULL,
            summary_text    LONGTEXT,
            health_score    TINYINT UNSIGNED COMMENT '0-100',
            risk_flags      JSON,
            model_used      VARCHAR(64),
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_sprint_id (sprint_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """,
    ),
    (
        "ai_time_reports",
        """
        CREATE TABLE IF NOT EXISTS ai_time_reports (
            id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            user_id         INT NOT NULL,
            project_id      INT,
            period_from     DATE,
            period_to       DATE,
            report_text     LONGTEXT,
            model_used      VARCHAR(64),
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_project (user_id, project_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """,
    ),
    (
        "ai_qa_log",
        """
        CREATE TABLE IF NOT EXISTS ai_qa_log (
            id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            question        TEXT NOT NULL,
            context_json    JSON,
            answer          LONGTEXT,
            model_used      VARCHAR(64),
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """,
    ),
]


async def ensure_ai_tables_exist(async_engine: AsyncEngine) -> None:
    """Check and ensure that required ai_* tables exist in MySQL."""
    try:
        async with async_engine.begin() as conn:
            for name, statement in DDL_STATEMENTS:
                await conn.execute(text(statement.strip()))
        logger.info("Database schema check completed successfully.")
    except Exception as e:
        logger.warning(
            "Schema guard database initialization notice (will rely on PHP migrations): %s", e
        )
