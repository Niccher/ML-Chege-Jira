# Engineering Security Guide

This document details security practices, secret handling, and code auditing rules for **ML Chege Jira**.

## Key Security Principles

1. **Header Authentication**:
   - Every protected API route enforces `verify_api_key` via FastAPI `Security(verify_api_key)`.
   - Comparison uses `secrets.compare_digest()` to prevent timing attacks.
2. **Sanitized Logging**:
   - Prompts and LLM generation outputs are never logged with plaintext secrets or user credentials.
3. **Restricted CORS**:
   - `CORSMiddleware` in production is locked to configured WebApp domains.
4. **Read-Only Scope Enforcement**:
   - Database operations against core entity tables (`projects`, `tasks`, `users`) use read-only SELECT queries; write operations are restricted to `ai_*` tables.
