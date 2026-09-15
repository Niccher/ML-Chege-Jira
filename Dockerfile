FROM python:3.12-slim

# System dependencies for building llama-cpp-python and native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Optimize llama.cpp for CPU with OpenBLAS
ENV CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv for fast Python package management
RUN pip install --no-cache-dir uv

# Copy project definition and install dependencies
COPY pyproject.toml .
RUN uv pip install --system -e ".[dev]"

# Copy source code and prompt templates
COPY app/ /app/app/
COPY scripts/ /app/scripts/
COPY docs/ /app/docs/
COPY README.md /app/README.md

# Make script executable
RUN chmod +x /app/scripts/*.sh 2>/dev/null || true

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
