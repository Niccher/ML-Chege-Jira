# 3. Header-Based API Key Authentication

Date: 2026-09-15  
Status: Accepted

## Context and Problem Statement
Inter-service calls between CodeIgniter 4 and FastAPI need a fast, stateless, and secure authentication protocol that prevents unauthorized execution of compute-heavy LLM endpoints.

## Decision Drivers
- Lightweight, low latency, no database lookup required per token.
- Secure against timing attacks.
- Simple configuration via shared environment variable (`API_KEY`).

## Decision Outcome
Implemented `X-API-Key` header authentication enforced via `app/api/deps.py` and `app/core/security.py` using `secrets.compare_digest()`.
