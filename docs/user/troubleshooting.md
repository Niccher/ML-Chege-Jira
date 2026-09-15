# Operational Troubleshooting Guide

This guide covers common symptoms and resolution steps for operators starting or managing **ML Chege Jira**.

## Common Symptoms & Solutions

### 1. Port 8000 Already In Use
- **Symptom**: `ERROR: [Errno 98] Address already in use` during container startup.
- **Cause**: Another service is occupying port 8000 on the host.
- **Resolution**:
  1. Open `.env` and adjust `APP_PORT=8005`.
  2. In `docker-compose.yml`, change ports to `"8005:8000"`.
  3. Restart the container: `docker compose up -d`.

### 2. Database Connection Timeout or Refused
- **Symptom**: `OperationalError: (2003, "Can't connect to MySQL server")`.
- **Cause**: MySQL is not running or the container is not connected to the shared Docker network.
- **Resolution**:
  1. Verify MySQL container status: `docker ps | grep mysql`.
  2. Verify network attachment:
     ```bash
     docker network inspect hosts-shared-network
     ```
  3. Ensure `DB_HOST` in `.env` matches the container name or hostname.

### 3. Model Weights Missing on Startup
- **Symptom**: `FileNotFoundError: No model found for 'phi3-mini' at /app/models/...`
- **Cause**: The `.gguf` file has not been downloaded into the `models/` directory.
- **Resolution**:
  1. Run the model download script:
     ```bash
     bash scripts/download_model.sh phi3-mini
     ```
  2. Verify file presence: `ls -lh models/*.gguf`.
  3. Restart the container: `docker compose restart ml-chege-jira`.

### 4. High Memory Consumption or OOM Kill
- **Symptom**: Container restarts unexpectedly with exit code 137.
- **Cause**: The active LLM exceeds the container memory limit.
- **Resolution**:
  1. Use `phi3-mini` (2.2 GB) instead of 7B/8B models.
  2. Reduce context window in `.env`: `N_CTX=2048`.
  3. Set `N_THREADS=2` to reduce concurrency memory pressure.

### 5. 401 Unauthorized Error on API Calls
- **Symptom**: HTTP response `{"detail": "Invalid or missing X-API-Key header"}`.
- **Cause**: The request is missing the secret key or has a mismatched key.
- **Resolution**:
  Pass the header `X-API-Key: your_key` in all HTTP requests matching `API_KEY` in `.env`.
