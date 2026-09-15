"""Llama.cpp LLM engine manager with lazy loading, concurrency locks, downloads, and metrics."""

import asyncio
import json
import logging
import re
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.config import settings

logger = logging.getLogger(__name__)

# Try importing Llama from llama_cpp
try:
    from llama_cpp import Llama  # type: ignore
except ImportError:
    Llama = Any  # type: ignore
    logger.warning("llama-cpp-python is not installed or failed to import.")


MODEL_DOWNLOAD_URLS: dict[str, str] = {
    "mistral-7b": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    "llama3-8b": "https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf",
    "phi3-mini": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf",
    "deepseek-7b": "https://huggingface.co/TheBloke/deepseek-coder-7b-instruct-v1.5-GGUF/resolve/main/deepseek-coder-7b-instruct-v1.5.Q4_K_M.gguf",
}


@dataclass
class ModelStats:
    """Telemetry metrics tracked per model."""

    loaded: bool = False
    ram_mb: float = 0.0
    total_requests: int = 0
    total_duration_ms: float = 0.0
    last_used_at: float = field(default_factory=time.time)

    # Download tracking
    download_status: str = "idle"  # idle | downloading | completed | failed
    download_progress_pct: int = 0
    download_bytes_downloaded: int = 0
    download_total_bytes: int = 0
    download_error: str | None = None

    @property
    def avg_duration_ms(self) -> float | None:
        if self.total_requests == 0:
            return None
        return round(self.total_duration_ms / self.total_requests, 2)


class LlmEngineManager:
    """Manages multi-model instances, thread-safety locks, background downloads, and inference."""

    def __init__(self) -> None:
        self._models: dict[str, Any] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._stats: dict[str, ModelStats] = {}

    def get_lock(self, model_key: str) -> asyncio.Lock:
        """Get or create an asyncio.Lock for a specific model key."""
        if model_key not in self._locks:
            self._locks[model_key] = asyncio.Lock()
        return self._locks[model_key]

    def get_stats(self, model_key: str) -> ModelStats:
        """Get or initialize metrics for a specific model key."""
        if model_key not in self._stats:
            self._stats[model_key] = ModelStats()
        return self._stats[model_key]

    def list_models_on_disk(self) -> dict[str, dict[str, Any]]:
        """List all supported models, file existence, download status, and current cache status."""
        result: dict[str, dict[str, Any]] = {}
        models_dir = Path(settings.MODELS_DIR)

        for key, filename in settings.MODEL_FILES.items():
            file_path = models_dir / filename
            exists = file_path.exists()
            size_gb = round(file_path.stat().st_size / (1024**3), 2) if exists else 0.0
            stats = self.get_stats(key)

            result[key] = {
                "key": key,
                "file": filename,
                "path": str(file_path),
                "exists_on_disk": exists,
                "size_gb": size_gb,
                "loaded_in_ram": key in self._models,
                "total_requests": stats.total_requests,
                "avg_duration_ms": stats.avg_duration_ms,
                "download_status": stats.download_status,
                "download_progress_pct": stats.download_progress_pct,
                "download_error": stats.download_error,
                "download_url": MODEL_DOWNLOAD_URLS.get(key),
            }
        return result

    def is_cached(self, model_key: str) -> bool:
        """Check if model is currently held in RAM cache."""
        return model_key in self._models

    def evict_model(self, model_key: str) -> bool:
        """Unload a model from RAM cache to free memory."""
        if model_key in self._models:
            del self._models[model_key]
            stats = self.get_stats(model_key)
            stats.loaded = False
            stats.ram_mb = 0.0
            logger.info("Evicted model '%s' from RAM cache.", model_key)
            return True
        return False

    def reload_model(
        self,
        model_key: str,
        n_gpu_layers: int | None = None,
        n_threads: int | None = None,
        n_ctx: int | None = None,
    ) -> Any:
        """Evict and re-instantiate model in RAM."""
        self.evict_model(model_key)
        return self.load_model(model_key, n_gpu_layers, n_threads, n_ctx)

    def trigger_download(self, model_key: str) -> dict[str, Any]:
        """Start downloading a GGUF model in a background thread."""
        if model_key not in MODEL_DOWNLOAD_URLS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"success": False, "error": {"code": "invalid_model", "message": f"Unsupported model key '{model_key}'"}},
            )

        filename = settings.MODEL_FILES[model_key]
        dest_dir = Path(settings.MODELS_DIR)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / filename

        stats = self.get_stats(model_key)

        if stats.download_status == "downloading":
            return {
                "model_key": model_key,
                "status": "downloading",
                "progress_pct": stats.download_progress_pct,
                "message": "Download is already in progress.",
            }

        if dest_path.exists():
            stats.download_status = "completed"
            stats.download_progress_pct = 100
            return {
                "model_key": model_key,
                "status": "completed",
                "progress_pct": 100,
                "message": f"Model file '{filename}' is already present on disk.",
            }

        url = MODEL_DOWNLOAD_URLS[model_key]
        stats.download_status = "downloading"
        stats.download_progress_pct = 0
        stats.download_error = None

        def _worker() -> None:
            temp_path = dest_dir / f"{filename}.tmp"
            try:
                with httpx.stream("GET", url, follow_redirects=True, timeout=3600.0) as resp:
                    resp.raise_for_status()
                    total_bytes = int(resp.headers.get("content-length", 0))
                    stats.download_total_bytes = total_bytes
                    downloaded = 0

                    with open(temp_path, "wb") as f:
                        for chunk in resp.iter_bytes(chunk_size=1024 * 1024):  # 1MB chunks
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                stats.download_bytes_downloaded = downloaded
                                if total_bytes > 0:
                                    stats.download_progress_pct = int((downloaded / total_bytes) * 100)

                    # Move completed download to destination
                    temp_path.rename(dest_path)
                    stats.download_status = "completed"
                    stats.download_progress_pct = 100
                    logger.info("Finished downloading model '%s' to '%s'", model_key, dest_path)
            except Exception as e:
                logger.exception("Error downloading model '%s': %s", model_key, e)
                stats.download_status = "failed"
                stats.download_error = str(e)
                if temp_path.exists():
                    temp_path.unlink(missing_ok=True)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

        return {
            "model_key": model_key,
            "status": "downloading",
            "progress_pct": 0,
            "message": f"Download initiated for '{model_key}' from {url}",
        }

    def load_model(
        self,
        model_key: str,
        n_gpu_layers: int | None = None,
        n_threads: int | None = None,
        n_ctx: int | None = None,
    ) -> Any:
        """Synchronously load a GGUF model into memory using llama-cpp-python."""
        if model_key not in settings.MODEL_FILES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": "invalid_model_key",
                        "message": f"Model key '{model_key}' is not in supported list: {list(settings.MODEL_FILES.keys())}",
                    },
                },
            )

        filename = settings.MODEL_FILES[model_key]
        file_path = Path(settings.MODELS_DIR) / filename

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "success": False,
                    "error": {
                        "code": "model_not_found_on_disk",
                        "message": f"Model file '{filename}' was not found. You can trigger a download via POST /api/v1/admin/models/{model_key}/download",
                    },
                },
            )

        if Llama is Any or isinstance(Llama, type(Any)):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "success": False,
                    "error": {
                        "code": "llama_cpp_not_available",
                        "message": "llama-cpp-python library is not available in runtime",
                    },
                },
            )

        gpu_layers = n_gpu_layers if n_gpu_layers is not None else settings.N_GPU_LAYERS
        threads = n_threads if n_threads is not None else settings.N_THREADS
        ctx = n_ctx if n_ctx is not None else settings.N_CTX

        logger.info(
            "Loading model '%s' from '%s' (gpu_layers=%s, threads=%s, ctx=%s)...",
            model_key,
            file_path,
            gpu_layers,
            threads,
            ctx,
        )

        try:
            model = Llama(
                model_path=str(file_path),
                n_gpu_layers=gpu_layers,
                n_threads=threads,
                n_ctx=ctx,
                verbose=False,
            )
            self._models[model_key] = model
            stats = self.get_stats(model_key)
            stats.loaded = True
            stats.ram_mb = round(file_path.stat().st_size / (1024**2), 2)
            logger.info("Successfully loaded model '%s' into RAM.", model_key)
            return model
        except Exception as e:
            logger.exception("Failed to load model '%s': %s", model_key, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "success": False,
                    "error": {
                        "code": "model_load_failed",
                        "message": f"Failed to instantiate model '{model_key}': {e!s}",
                    },
                },
            ) from e

    async def generate_response(
        self,
        prompt: str,
        model_key: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.2,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Execute async inference through the locked model instance."""
        target_key = model_key or settings.DEFAULT_MODEL
        lock = self.get_lock(target_key)

        async with lock:
            if target_key not in self._models:
                await asyncio.to_thread(self.load_model, target_key)

            model = self._models[target_key]
            stats = self.get_stats(target_key)

            start_time = time.perf_counter()

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"

            def _run_inference() -> dict[str, Any]:
                return model(
                    full_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=["</s>", "<|im_end|>", "\n\nUser:", "User:"],
                )

            try:
                output = await asyncio.to_thread(_run_inference)
            except Exception as e:
                logger.exception("Inference failed on model '%s': %s", target_key, e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "success": False,
                        "error": {
                            "code": "inference_error",
                            "message": f"Inference execution failed: {e!s}",
                        },
                    },
                ) from e

            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            stats.total_requests += 1
            stats.total_duration_ms += elapsed_ms
            stats.last_used_at = time.time()

            raw_text = output["choices"][0]["text"].strip()
            tokens_used = output.get("usage", {}).get("total_tokens", 0)

            return {
                "raw_text": raw_text,
                "model_used": target_key,
                "tokens_used": tokens_used,
                "duration_ms": elapsed_ms,
            }

    @staticmethod
    def extract_json(raw_text: str) -> dict[str, Any]:
        """Extract structured JSON object from LLM response text."""
        cleaned = re.sub(r"^```json\s*", "", raw_text, flags=re.MULTILINE)
        cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)  # type: ignore[no-any-return]
            except json.JSONDecodeError as err:
                logger.warning("Failed to parse extracted JSON block: %s. Text: %s", err, json_str)

        try:
            return json.loads(cleaned)  # type: ignore[no-any-return]
        except json.JSONDecodeError as err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "success": False,
                    "error": {
                        "code": "invalid_llm_json",
                        "message": f"LLM output could not be parsed as valid JSON: {err!s}",
                        "raw_output": raw_text,
                    },
                },
            ) from err


engine_manager = LlmEngineManager()
