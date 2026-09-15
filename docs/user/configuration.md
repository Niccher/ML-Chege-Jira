# User Configuration Reference

This document lists all environment variables that operators may configure in `.env` or inject via container orchestration platforms (such as Railway or Kubernetes).

## Core Configuration Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `APP_ENV` | String | No | `production` | Environment mode (`development`, `production`, `testing`). In development, `/docs` Swagger is enabled. |
| `APP_HOST` | String | No | `0.0.0.0` | Network binding interface. |
| `APP_PORT` | Integer | No | `8000` | Port listened to by the Uvicorn ASGI server. |
| `API_KEY` | String | **Yes** | `chege_jira_ml_super_secret_key_2026` | Shared secret key required on all API requests in the `X-API-Key` header. |
| `DB_HOST` | String | **Yes** | `mysql` | Hostname or IP of the MySQL server. |
| `DB_PORT` | Integer | No | `3306` | Port of the MySQL database. |
| `DB_USER` | String | **Yes** | `root` | Database username. |
| `DB_PASSWORD` | String | **Yes** | `root_password` | Database user password. |
| `DB_NAME` | String | **Yes** | `db_chege_jira` | Database schema name. |
| `REDIS_URL` | String | No | `redis://redis:6379/0` | Connection string for Redis instance. |

## LLM & Inference Parameters

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MODELS_DIR` | Path | `/app/models` | Filesystem path storing `.gguf` model binaries. |
| `DEFAULT_MODEL` | String | `phi3-mini` | Active model key (`phi3-mini`, `mistral-7b`, `llama3-8b`, `deepseek-7b`). |
| `N_GPU_LAYERS` | Integer | `0` | Number of layers to offload to GPU VRAM (set `0` for CPU-only inference). |
| `N_THREADS` | Integer | `4` | Number of CPU threads dedicated to LLM token generation. |
| `N_CTX` | Integer | `4096` | Context window length in tokens. |

## Cloud / Railway Automated Variables

When deployed on Railway alongside a MySQL plugin, the service automatically recognizes and maps:
- `MYSQLHOST` → `DB_HOST`
- `MYSQLPORT` → `DB_PORT`
- `MYSQLUSER` → `DB_USER`
- `MYSQLPASSWORD` → `DB_PASSWORD`
- `MYSQLDATABASE` → `DB_NAME`
- `MYSQL_URL` / `DATABASE_URL` → Parsed automatically
