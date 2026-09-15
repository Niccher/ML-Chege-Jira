#!/usr/bin/env bash
set -euo pipefail

# Helper script to download supported GGUF models from HuggingFace
# Usage: ./scripts/download_model.sh [mistral-7b|llama3-8b|phi3-mini|deepseek-7b]

MODELS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../models" && pwd)"
mkdir -p "$MODELS_DIR"

MODEL_KEY="${1:-mistral-7b}"

echo "=========================================="
echo " Chege Jira ML Model Downloader"
echo " Target Directory: $MODELS_DIR"
echo " Model Requested:  $MODEL_KEY"
echo "=========================================="

case "$MODEL_KEY" in
  mistral-7b)
    URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    DEST="$MODELS_DIR/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    ;;
  llama3-8b)
    URL="https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
    DEST="$MODELS_DIR/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
    ;;
  phi3-mini)
    URL="https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
    DEST="$MODELS_DIR/Phi-3-mini-4k-instruct.Q4_K_M.gguf"
    ;;
  deepseek-7b)
    URL="https://huggingface.co/TheBloke/deepseek-coder-7b-instruct-v1.5-GGUF/resolve/main/deepseek-coder-7b-instruct-v1.5.Q4_K_M.gguf"
    DEST="$MODELS_DIR/deepseek-coder-7b-instruct.Q4_K_M.gguf"
    ;;
  *)
    echo "Unknown model key: $MODEL_KEY"
    echo "Supported keys: mistral-7b, llama3-8b, phi3-mini, deepseek-7b"
    exit 1
    ;;
esac

if [ -f "$DEST" ]; then
    echo "Model file already exists at $DEST. Skipping download."
    exit 0
fi

echo "Downloading from: $URL"
echo "Saving to:        $DEST"

if command -v curl >/dev/null 2>&1; then
    curl -L --progress-bar -o "$DEST" "$URL"
elif command -v wget >/dev/null 2>&1; then
    wget -O "$DEST" "$URL"
else
    echo "Error: Neither curl nor wget found on system."
    exit 1
fi

echo "Download complete! Verified file: $(ls -lh "$DEST")"
