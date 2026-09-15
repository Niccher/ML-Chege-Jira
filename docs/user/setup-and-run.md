# Setup and Run Guide

This guide walks operators through starting and verifying the **ML Chege Jira** service on a target server or local machine.

## Prerequisites

- **Docker & Docker Compose** (version 24.0+ / Compose v2 recommended)
- **Minimum System Specifications**:
  - **RAM**: 8 GB (16 GB recommended for 7B/8B models)
  - **CPU**: 4+ cores with AVX2 instruction support
  - **Disk**: 10 GB free space for GGUF model binaries and Docker base layers

## Step-by-Step Installation

### 1. Clone the Codebase
```bash
git clone https://github.com/Niccher/ML-Chege-Jira.git
cd ML-Chege-Jira
```

### 2. Configure Environment Variables
Copy the template configuration file:
```bash
cp .env.example .env
```

Ensure your `API_KEY` matches the `ml.apiKey` setting configured in the CodeIgniter WebApp.

### 3. Obtain LLM Model Weights
Download the default quantized model binary (`phi3-mini` ~2.2 GB or `mistral-7b` ~4.1 GB):
```bash
bash scripts/download_model.sh phi3-mini
```
The model binary will be placed inside the `models/` folder.

### 4. Launch Containerized Service
```bash
docker compose up --build -d
```

### 5. Validate Health & Readiness
Inspect container logs and query the health endpoint:
```bash
docker compose logs -f ml-chege-jira
```

Once initialized, test via `curl`:
```bash
curl -i http://localhost:8000/api/v1/health
```

Expected output:
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

### 6. Stopping and Restarting
To stop the service cleanly:
```bash
docker compose down
```

To restart the service after modifying environment variables:
```bash
docker compose restart ml-chege-jira
```
