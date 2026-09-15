# Local Development Guide

This guide describes how to configure a native Python development environment for building, debugging, and testing **ML Chege Jira**.

## Prerequisites

- **Python 3.11** or **Python 3.12**
- **uv** (recommended for ultra-fast packaging) or standard `pip` / `venv`
- C/C++ compiler toolchain (`build-essential`, `cmake`, `libopenblas-dev`)
- Docker (for local MySQL and Redis backing services)

## Native Environment Setup

1. **Clone the repository and enter directory:**
   ```bash
   git clone https://github.com/Niccher/ML-Chege-Jira.git
   cd ML-Chege-Jira
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies in editable mode:**
   ```bash
   # Using uv (fastest)
   uv pip install -e ".[dev]"

   # Or standard pip
   pip install -e ".[dev]"
   ```

4. **Start local backing services (MySQL & Redis):**
   ```bash
   docker compose up -d mysql redis
   ```

5. **Run the FastAPI development server with hot-reload:**
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

6. **Access Interactive Swagger Docs:**
   Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.
