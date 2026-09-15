# ML Chege Jira

High-performance local LLM inference microservice and AI copilot backend for Chege Jira WebApp. Powered by Python 3.11+, FastAPI, and `llama-cpp-python` for quantized on-premise GGUF model execution.

Stack: Python 3.11+, FastAPI, llama.cpp, SQLAlchemy (Async MySQL), Redis.

**If you only need to run the system, this page is enough.**  
Software engineers: [docs/README.md](docs/README.md).

## What “running” looks like

| Service / Endpoint | URL / Command | Expected Response |
|--------------------|---------------|-------------------|
| API Health Check | `GET http://localhost:8000/api/v1/health` | `{"status":"ok","version":"0.1.0"}` |
| System Telemetry | `GET http://localhost:8000/api/v1/admin/telemetry` | CPU, RAM, Disk, MySQL, Redis JSON |
| Active Model Vitals | `GET http://localhost:8000/api/v1/models/active` | Model details & loaded status |
| Interactive Swagger | `http://localhost:8000/docs` | Available when `APP_ENV=development` |

## Prerequisites

### Option A — Docker Compose (Recommended)
- Git
- Docker Engine 24+ and Docker Compose v2 (or Docker Desktop)

### Option B — Without Docker (Native Linux / macOS)
- Python 3.11 or 3.12 with `uv` or `pip`
- C/C++ compiler toolchain (`build-essential`, `cmake`, `libopenblas-dev`)
- Running MySQL 8.0+ and Redis 7.0+ instances

## Setup and Run

From a fresh machine:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Niccher/ML-Chege-Jira.git
   cd ML-Chege-Jira
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

3. **Download a lightweight GGUF model:**
   ```bash
   bash scripts/download_model.sh phi3-mini
   ```

4. **Start the container stack:**
   ```bash
   docker compose up --build -d
   ```

5. **Verify service health:**
   ```bash
   curl -f http://localhost:8000/api/v1/health
   ```

6. **Stop the stack:**
   ```bash
   docker compose down
   ```

## Configuration Users May Change

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_PORT` | `8000` | HTTP port exposed by the microservice |
| `API_KEY` | `chege_jira_ml_super_secret_key_2026` | Shared secret header (`X-API-Key`) |
| `DB_HOST` | `mysql` | MySQL hostname or Railway service name |
| `DB_PORT` | `3306` | MySQL port |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL for caching & jobs |
| `DEFAULT_MODEL` | `phi3-mini` | Active GGUF model identifier |
| `N_THREADS` | `4` | CPU inference threads |
| `N_CTX` | `4096` | Context window size in tokens |

Full settings reference: [docs/user/configuration.md](docs/user/configuration.md).

## Something Went Wrong?

- **Port 8000 already in use:** Change `APP_PORT=8005` in `.env` and `docker-compose.yml`.
- **Database connection error:** Ensure MySQL container is healthy on the shared Docker network.
- **Model weights not found:** Run `bash scripts/download_model.sh phi3-mini` to populate `models/`.
- **High RAM usage:** Switch to a smaller model quantization (`Q4_K_M`) or reduce `N_CTX=2048`.

Detailed recovery steps: [docs/user/troubleshooting.md](docs/user/troubleshooting.md).

## Software Engineers

- System Architecture: [docs/architecture/overview.md](docs/architecture/overview.md)
- Inter-Service Communication: [docs/architecture/communication.md](docs/architecture/communication.md)
- OpenAPI Specification: [docs/api/openapi.yaml](docs/api/openapi.yaml)
- Local Development & Testing: [docs/engineering/local-development.md](docs/engineering/local-development.md)
- Making Safe Changes: [docs/engineering/making-changes.md](docs/engineering/making-changes.md)
