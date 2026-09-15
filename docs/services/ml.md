# Machine Learning & LLM Engine Guide

This document describes model loading, quantization, prompt engineering, context window management, and inference optimization using `llama-cpp-python`.

## LLM Engine Architecture (`app/core/llm_engine.py`)

The `LLMEngine` class encapsulates the underlying `Llama` instance as a managed thread-safe singleton.

### Model Loading & Lifecycle
1. Models are loaded on demand upon service startup or when an administrative switch is requested (`POST /api/v1/models/switch`).
2. When switching models, the previous instance is explicitly unallocated before initializing the new model weights to prevent memory leaks.
3. If a requested model is missing from `/app/models`, the service falls back gracefully without crashing the web process.

## Supported Model Catalog

| Model Identifier | Base Architecture | Parameters | Quantization | Disk Size | Ideal Use Case |
|------------------|-------------------|------------|--------------|-----------|----------------|
| `phi3-mini` | Microsoft Phi-3 Mini | 3.8 Billion | `Q4_K_M` | ~2.2 GB | Real-time task enhancement, fast QA |
| `mistral-7b` | Mistral Instruct v0.2 | 7.3 Billion | `Q4_K_M` | ~4.1 GB | Complex sprint analysis & retrospectives |
| `llama3-8b` | Meta Llama 3 Instruct | 8.0 Billion | `Q4_K_M` | ~4.7 GB | High-accuracy timesheet auditing & analytics |
| `deepseek-7b` | DeepSeek Coder Instruct | 7.0 Billion | `Q4_K_M` | ~4.2 GB | Technical bug triage & code snippet suggestions |

## CPU & Hardware Acceleration Tuning

In `app/config.py`:
- `N_THREADS`: Set to match physical CPU cores (typically `4` to `8`).
- `N_GPU_LAYERS`: Set to `0` for CPU inference (utilizing OpenBLAS). When running on an NVIDIA GPU host, set to `33`+ to offload all model layers to VRAM.
- `N_CTX`: Context window length in tokens (default `4096`).
