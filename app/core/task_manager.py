import json
import uuid
import time
from typing import Any
import redis
from app.config import settings

class TaskManager:
    def __init__(self) -> None:
        self.fallback_store = {}
        self.use_redis = False
        try:
            self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=0.5)
            self.redis_client.ping()
            self.use_redis = True
        except (redis.ConnectionError, redis.TimeoutError):
            pass # Use fallback_store
        
    def create_task(self, model_key: str | None = None) -> str:
        task_id = str(uuid.uuid4())
        task_data = {
            "status": "pending",
            "model": model_key or settings.DEFAULT_MODEL,
            "created_at": time.time(),
            "updated_at": time.time(),
            "result": None,
            "error": None
        }
        
        if self.use_redis:
            try:
                self.redis_client.set(f"task:{task_id}", json.dumps(task_data), ex=86400) # Expire in 24h
            except redis.RedisError:
                self.fallback_store[task_id] = task_data
        else:
            self.fallback_store[task_id] = task_data
            
        return task_id
        
    def update_task(self, task_id: str, status: str, result: Any = None, error: str | None = None) -> None:
        task_data = None
        
        if self.use_redis:
            try:
                task_data_str = self.redis_client.get(f"task:{task_id}")
                if task_data_str:
                    task_data = json.loads(task_data_str)
            except redis.RedisError:
                task_data = self.fallback_store.get(task_id)
        else:
            task_data = self.fallback_store.get(task_id)
            
        if not task_data:
            return
        
        task_data["status"] = status
        task_data["updated_at"] = time.time()
        if result is not None:
            task_data["result"] = result
        if error is not None:
            task_data["error"] = error
            
        if self.use_redis:
            try:
                self.redis_client.set(f"task:{task_id}", json.dumps(task_data), ex=86400)
            except redis.RedisError:
                self.fallback_store[task_id] = task_data
        else:
            self.fallback_store[task_id] = task_data
        
    def get_task(self, task_id: str) -> dict[str, Any] | None:
        if self.use_redis:
            try:
                task_data_str = self.redis_client.get(f"task:{task_id}")
                if task_data_str:
                    return json.loads(task_data_str)
            except redis.RedisError:
                return self.fallback_store.get(task_id)
                
        return self.fallback_store.get(task_id)

task_manager = TaskManager()
