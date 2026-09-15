# Inter-Service Communication

This document specifies the protocols, authentication mechanisms, sequence flows, and error contracts between the **CodeIgniter 4 WebApp** and the **FastAPI ML Service**.

## Communication Protocols

| Source | Destination | Protocol | Authentication | Base URL (Dev / Prod) | Purpose |
|--------|-------------|----------|----------------|------------------------|---------|
| Browser | WebApp | HTTP / HTTPS | Session Cookie + CSRF | `http://localhost:9001` | User interface and interaction |
| WebApp | ML Backend | HTTP / JSON | `X-API-Key` Header | `http://ml-chege-jira:8000/api/v1` | AI copilot inference and telemetry |
| ML Backend | MySQL | Async TCP (`aiomysql`) | DB Username & Password | `mysql:3306` | Schema query & AI result storage |
| ML Backend | Redis | TCP (`redis-py`) | Redis Auth / Default | `redis:6379/0` | Async task state & job tracking |

## Core Sequence: Synchronous Task AI Enhancement

When a user requests AI refinement or acceptance criteria generation for a task:

```mermaid
sequenceDiagram
    autonumber
    actor User as Engineer (Browser)
    participant WebApp as CodeIgniter 4 WebApp
    participant ML as FastAPI ML Service
    participant LLM as llama-cpp-python Engine
    participant DB as MySQL Database

    User->>WebApp: Click "Enhance Task with AI"
    WebApp->>DB: Fetch Task & Project Context
    DB-->>WebApp: Title, Description, Tech Stack
    WebApp->>ML: POST /api/v1/tasks/enhance (X-API-Key, JSON payload)
    ML->>LLM: Generate Prompt & Execute Inference
    LLM-->>ML: Generated Markdown & Acceptance Criteria
    ML->>DB: INSERT INTO ai_task_enhancements
    ML-->>WebApp: 200 OK (JSON with enhanced description & suggestions)
    WebApp-->>User: Render Refined Task in Modal / UI
```

## Core Sequence: Asynchronous Sprint Retrospective Report

For heavy workloads that exceed synchronous HTTP timeouts:

```mermaid
sequenceDiagram
    autonumber
    actor Lead as Scrum Master
    participant WebApp as WebApp
    participant ML as FastAPI Service
    participant TaskManager as Background Worker
    participant DB as MySQL

    Lead->>WebApp: Request Sprint Retrospective Report
    WebApp->>ML: POST /api/v1/async-tasks/generate (X-API-Key, task_type="sprint_summary")
    ML->>TaskManager: Dispatch background asyncio Task
    ML-->>WebApp: 202 Accepted ({"task_id": "job_12345", "status": "queued"})
    WebApp-->>Lead: "Report is generating in the background..."

    TaskManager->>DB: Read Sprint Burndown & Velocity Logs
    TaskManager->>ML: Run LLM Inference (llama.cpp)
    TaskManager->>DB: Save Report to ai_sprint_summaries
    TaskManager->>ML: Update job status = "completed"

    loop Poll Status Every 3s
        WebApp->>ML: GET /api/v1/async-tasks/status/job_12345
        ML-->>WebApp: {"status": "completed", "result": {...}}
    end
    WebApp-->>Lead: Display Formatted Retrospective Report
```

## Standard Error Response Format

All API errors return RFC 7807 compliant JSON envelopes:

```json
{
  "success": false,
  "error": {
    "code": "model_not_found",
    "message": "The requested model 'llama3-8b' is not present in /app/models",
    "details": null
  }
}
```
