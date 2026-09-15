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

# Copy project metadata and source code required by build backend (hatchling)
COPY pyproject.toml README.md ./
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY docs/ ./docs/

# Install dependencies and package
RUN uv pip install --system -e "."

# Make scripts executable
RUN chmod +x /app/scripts/*.sh 2>/dev/null || true

EXPOSE 8000

# Railway passes $PORT dynamically; fallback to 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
