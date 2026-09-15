# ML Chege Jira

High-performance, pure REST API micro-service hosting open-source Large Language Models (LLMs) via `llama-cpp-python` for the **Chege Jira WebApp**.

---

## 🌟 What This Service Does

- **Task Ticket Enhancement**: Expands short titles or bullet points into comprehensive Jira tickets with acceptance criteria, story point estimates, and priority suggestions.
- **Sprint Health Summaries**: Automatically analyzes sprint completion rate, remaining velocity, open blockers, and time log distributions.
- **Wiki Documentation Generation**: Generates comprehensive project architecture and onboarding documentation directly into `project_wiki_pages`.
- **Productivity & Time Analysis**: Produces natural language developer time-log analysis reports.
- **Real-Time Admin Telemetry & Control**: Exposes container CPU, RAM, disk, model cache stats, and runtime configuration controls directly to the PHP Admin panel.

---

## 🚀 Getting Started

### 1. Prerequisites
- Docker Engine & Docker Compose
- Shared network `hosts-shared-network` running with MySQL (started from `Chege Jira WebApp`)

### 2. Download at least one GGUF model
```bash
chmod +x scripts/download_model.sh
./scripts/download_model.sh phi3-mini
# or: ./scripts/download_model.sh mistral-7b
```

### 3. Start the Container
```bash
docker compose up --build -d
```

### 4. Verify Health & Telemetry
```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/admin/telemetry -H "X-API-Key: chege_jira_ml_super_secret_key_2026"
```

---

## 📚 API Endpoints Summary

All requests require the `X-API-Key` header and return standard JSON envelopes.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health & liveness status |
| `GET` | `/api/v1/models` | List available models on disk |
| `POST` | `/api/v1/tasks/{id}/enhancements` | Expand task into full Jira ticket |
| `POST` | `/api/v1/tasks/{id}/priority-suggestions` | Suggest priority & story points |
| `POST` | `/api/v1/sprints/{id}/summaries` | Generate sprint health summary |
| `POST` | `/api/v1/projects/{id}/wiki-pages` | Auto-generate and publish wiki page |
| `POST` | `/api/v1/time-reports` | Produce developer time log report |
| `POST` | `/api/v1/qa` | Project-grounded Q&A |
| `GET` | `/api/v1/admin/telemetry` | Container vitals & LLM cache metrics |
| `GET` | `/api/v1/admin/config` | Read current runtime configuration |
| `PATCH` | `/api/v1/admin/config` | Update default model, threads, GPU layers |
| `POST` | `/api/v1/admin/models/{key}/cache` | Pre-load model into RAM |
| `DELETE` | `/api/v1/admin/models/{key}/cache` | Evict model from RAM |

---

## 🛠️ Software Engineers

For architecture details, database schemas, and testing instructions, please read [docs/README.md](docs/README.md).
