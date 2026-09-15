# Database & Schema Guard Guide

This document describes how **ML Chege Jira** interacts with the shared MySQL database and enforces safety boundaries.

## Architecture & Responsibilities

- **Source of Truth**: The MySQL database is shared with the CodeIgniter 4 WebApp.
- **Migration Ownership**: Core entity migrations (`users`, `projects`, `tasks`, `sprints`, `time_logs`, `project_wiki_pages`) are owned by the CodeIgniter WebApp.
- **Schema Guard (`app/db/schema_guard.py`)**: On startup, the ML backend validates that required `ai_*` tables exist. If missing, it creates them idempotently without altering core WebApp tables.

## Async SQLAlchemy & Session Lifecycle

- Database connections utilize `aiomysql` via `SQLAlchemy 2.0` async engine.
- Connection pooling is configured in `app/db/session.py`.
- Sessions are injected into FastAPI route handlers via `Depends(get_db_session)` and automatically closed upon completion.
