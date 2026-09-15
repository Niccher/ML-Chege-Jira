# 1. Local LLM Inference via llama-cpp-python

Date: 2026-09-15  
Status: Accepted

## Context and Problem Statement
The Chege Jira platform requires AI intelligence (task description refinement, acceptance criteria generation, sprint retrospectives, timesheet auditing) while guaranteeing complete data privacy, offline capability, and zero external per-token API fees.

## Decision Drivers
- Zero cloud API dependency (OpenAI / Anthropic data leakage avoidance).
- Ability to run on modest CPU hardware (4-8 cores) or consumer GPUs.
- High token-per-second generation speeds with quantized models.

## Considered Options
1. **llama-cpp-python (llama.cpp with OpenBLAS/CUDA)** — Selected
2. **Ollama local daemon** — Good, but external daemon complicates single-container deployment.
3. **vLLM / HuggingFace Transformers** — Heavy memory footprint, requires dedicated high-end GPUs.

## Decision Outcome
Selected **`llama-cpp-python`** with GGUF 4-bit (`Q4_K_M`) quantization for maximum portability, low RAM usage, and thread-safe embedded Python execution.
