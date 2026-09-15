"""Tests for LLM Engine JSON extraction and cache control."""

import pytest
from fastapi import HTTPException

from app.core.llm_engine import engine_manager


def test_extract_json_clean_json() -> None:
    """Standard JSON string is parsed correctly."""
    raw = '{"summary": "Test summary", "priority": "high", "story_points": 5}'
    result = engine_manager.extract_json(raw)
    assert result["summary"] == "Test summary"
    assert result["priority"] == "high"
    assert result["story_points"] == 5


def test_extract_json_with_markdown_blocks() -> None:
    """JSON embedded in markdown ```json ... ``` blocks is extracted."""
    raw = """
    Here is the requested Jira ticket:
    ```json
    {
      "summary": "Fix login bug",
      "acceptance_criteria": ["Criteria 1", "Criteria 2"],
      "story_points": 3
    }
    ```
    Hope this helps!
    """
    result = engine_manager.extract_json(raw)
    assert result["summary"] == "Fix login bug"
    assert len(result["acceptance_criteria"]) == 2


def test_extract_json_invalid_fails() -> None:
    """Unparseable string raises 422 HTTP exception."""
    raw = "This is plain text with no json"
    with pytest.raises(HTTPException) as exc_info:
        engine_manager.extract_json(raw)
    assert exc_info.value.status_code == 422


def test_model_locks_created_dynamically() -> None:
    """Asyncio lock is lazily initialized per model key."""
    lock1 = engine_manager.get_lock("mistral-7b")
    lock2 = engine_manager.get_lock("mistral-7b")
    lock3 = engine_manager.get_lock("phi3-mini")

    assert lock1 is lock2
    assert lock1 is not lock3
