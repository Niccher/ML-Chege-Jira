# 2. Asynchronous Schema Guard for Shared MySQL

Date: 2026-09-15  
Status: Accepted

## Context and Problem Statement
The WebApp and ML service share a central MySQL instance. The ML service must ensure that its required `ai_*` tables exist without interfering with CodeIgniter 4's primary database migrations.

## Decision Drivers
- Avoid race conditions during container orchestrations.
- Maintain decoupled migration lifecycles between PHP and Python services.
- Ensure automated recovery if AI tables are missing.

## Decision Outcome
Implemented `app/db/schema_guard.py` executing during FastAPI application startup (`lifespan`), verifying and idempotently creating `ai_config`, `ai_task_enhancements`, `ai_sprint_summaries`, `ai_time_reports`, and `ai_qa_log` tables using `CREATE TABLE IF NOT EXISTS`.
