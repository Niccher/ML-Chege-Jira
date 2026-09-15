# ML Chege Jira — Engineering Documentation

This document provides deep technical details on architecture, database interactions, multi-model cache lifecycle, and PHP integration.

---

## 1. System Architecture

The ML Chege Jira backend operates as a decoupled microservice within Docker network `hosts-shared-network`.

```
PHP WebApp (9001) <---> MySQL 8.4 (3306) <---> FastAPI (8000)
                              ^                     |
                              |                     v
                              +---- reads & writes GGUF models on disk
```

### Key Principles:
1. **Stateless HTTP API**: All persistent state is in MySQL or on the mounted `/models` disk volume.
2. **Lazy Multi-Model Caching**: Models are loaded into RAM only upon their first request or explicit pre-load command.
3. **Asyncio Lock Isolation**: Concurrency is safely controlled with an `asyncio.Lock` per model key to prevent memory thrashing and race conditions inside the C++ runtime.
4. **Database Safety**: The service reads from core domain tables (`tasks`, `projects`, `sprints`, `time_logs`) and writes exclusively to dedicated `ai_*` tables, preserving transactional integrity of the main webapp.

---

## 2. Database Schema (ai_* tables)

```sql
-- Runtime configuration table
CREATE TABLE IF NOT EXISTS ai_config (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    default_model   VARCHAR(64)  NOT NULL DEFAULT 'mistral-7b',
    n_gpu_layers    INT          NOT NULL DEFAULT 0,
    n_threads       INT          NOT NULL DEFAULT 4,
    n_ctx           INT          NOT NULL DEFAULT 4096,
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Task enhancements table
CREATE TABLE IF NOT EXISTS ai_task_enhancements (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    task_id             INT UNSIGNED NOT NULL,
    summary             TEXT,
    acceptance_criteria JSON,
    story_points        TINYINT UNSIGNED,
    priority            ENUM('low','medium','high','critical'),
    model_used          VARCHAR(64),
    tokens_used         INT UNSIGNED,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Sprint summaries table
CREATE TABLE IF NOT EXISTS ai_sprint_summaries (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    sprint_id       INT UNSIGNED NOT NULL,
    summary_text    LONGTEXT,
    health_score    TINYINT UNSIGNED COMMENT '0-100',
    risk_flags      JSON,
    model_used      VARCHAR(64),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE CASCADE
);

-- Time reports table
CREATE TABLE IF NOT EXISTS ai_time_reports (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         INT UNSIGNED NOT NULL,
    project_id      INT UNSIGNED,
    period_from     DATE,
    period_to       DATE,
    report_text     LONGTEXT,
    model_used      VARCHAR(64),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- AI Q&A Log
CREATE TABLE IF NOT EXISTS ai_qa_log (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    question        TEXT NOT NULL,
    context_json    JSON,
    answer          LONGTEXT,
    model_used      VARCHAR(64),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Supported Model Keys and Files

| Model Key | Filename in `models/` | Parameter Size | Default Quant |
|---|---|---|---|
| `mistral-7b` | `mistral-7b-instruct-v0.2.Q4_K_M.gguf` | 7.3B | Q4_K_M (~4.1GB) |
| `llama3-8b` | `Meta-Llama-3-8B-Instruct.Q4_K_M.gguf` | 8.0B | Q4_K_M (~4.9GB) |
| `phi3-mini` | `Phi-3-mini-4k-instruct.Q4_K_M.gguf` | 3.8B | Q4_K_M (~2.2GB) |
| `deepseek-7b` | `deepseek-coder-7b-instruct.Q4_K_M.gguf` | 7.0B | Q4_K_M (~4.1GB) |
