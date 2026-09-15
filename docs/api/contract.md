# API Contract Reference

The **ML Chege Jira** REST API provides endpoints for model management, telemetry monitoring, AI task enhancements, sprint retrospectives, and background report jobs.

All requests (except `/api/v1/health`) require the authentication header:
```http
X-API-Key: chege_jira_ml_super_secret_key_2026
```

---

## 1. Health & Status

### `GET /api/v1/health`
Performs an end-to-end liveness probe checking model loading and database reachability.

- **Response `200 OK`:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "app_env": "production",
  "default_model": "phi3-mini",
  "model_loaded": true,
  "database_connected": true
}
```

---

## 2. Telemetry & Hardware

### `GET /api/v1/admin/telemetry`
Returns real-time container CPU, RAM, Disk, MySQL connection, and Redis statistics.

- **Response `200 OK`:**
```json
{
  "status": "online",
  "timestamp": "2026-09-15T19:30:00Z",
  "cpu_percent": 12.5,
  "cpu_cores": 4,
  "ram_used_bytes": 1073741824,
  "ram_total_bytes": 8589934592,
  "ram_used_human": "1.00 GB",
  "ram_percent": 12.5,
  "disk_percent": 24.0,
  "db_connected": true,
  "db_threads": 2
}
```

---

## 3. Model Management

### `GET /api/v1/models`
Lists all available models in the registry, their disk presence, file sizes, and download status.

### `POST /api/v1/models/switch`
Dynamically switches the active in-memory model.
- **Payload:**
```json
{
  "model_key": "mistral-7b"
}
```

---

## 4. AI Enhancement Endpoints

### `POST /api/v1/tasks/enhance`
Refines task descriptions and generates Gherkin acceptance criteria.
- **Payload:**
```json
{
  "task_id": 42,
  "title": "Build user notification bell",
  "description": "Need a dropdown showing unread alerts",
  "tech_stack": "PHP, CodeIgniter 4, Bootstrap"
}
```

- **Response `200 OK`:**
```json
{
  "success": true,
  "task_id": 42,
  "enhanced_description": "Comprehensive specification...",
  "acceptance_criteria": [
    "Given an authenticated user, when notifications exist, badge count is visible",
    "When clicked, popup shows 8 most recent alerts"
  ]
}
```

### `POST /api/v1/sprints/retrospective`
Analyzes velocity, completed vs pending story points, and produces actionable retrospective summaries.

### `POST /api/v1/time-reports/summarize`
Detects timesheet anomalies, unbilled activity patterns, and generates executive summaries.

---

## 5. Asynchronous Background Jobs

### `POST /api/v1/async-tasks/generate`
Dispatches a long-running generation task without blocking the HTTP request.
- **Payload:**
```json
{
  "task_type": "sprint_summary",
  "entity_id": 12,
  "parameters": {}
}
```
- **Response `202 Accepted`:**
```json
{
  "job_id": "job_8dfa91b2",
  "status": "queued",
  "created_at": "2026-09-15T19:30:00Z"
}
```

### `GET /api/v1/async-tasks/status/{job_id}`
Checks the execution progress and retrieves final output.
