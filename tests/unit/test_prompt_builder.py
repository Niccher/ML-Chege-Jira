"""Tests for Jinja2 prompt template rendering."""

from app.core.prompt_builder import render_prompt


def test_render_enhance_task_prompt() -> None:
    """Check that enhance_task prompt renders variables correctly."""
    prompt = render_prompt(
        "enhance_task.j2",
        project_name="Portal V2",
        project_tech_stack="PHP 8.2, CI4, Vue.js",
        title="Fix OAuth redirect",
        description="Redirect loop happens on safari",
        status="todo",
    )
    assert "Portal V2" in prompt
    assert "Fix OAuth redirect" in prompt
    assert "Redirect loop happens on safari" in prompt
    assert "acceptance_criteria" in prompt


def test_render_suggest_priority_prompt() -> None:
    """Check suggest_priority template."""
    prompt = render_prompt(
        "suggest_priority.j2",
        project_name="Mobile API",
        title="Payment gateway crash",
        description="500 error on stripe webhook",
    )
    assert "Mobile API" in prompt
    assert "Payment gateway crash" in prompt
    assert "priority" in prompt


def test_render_summarise_sprint_prompt() -> None:
    """Check summarise_sprint template."""
    prompt = render_prompt(
        "summarise_sprint.j2",
        project_name="E-Commerce",
        name="Sprint 14",
        goal="Complete checkout integration",
        status="active",
        total_points=45,
        completed_points=30,
        tasks=[
            {"title": "Implement Stripe checkout", "status": "done", "priority": "high", "story_points": 5, "assignee": "alice"},
            {"title": "Bug in tax calculator", "status": "in_progress", "priority": "critical", "story_points": 3, "assignee": "bob"},
        ],
    )
    assert "Sprint 14" in prompt
    assert "Complete checkout integration" in prompt
    assert "Implement Stripe checkout" in prompt
    assert "Bug in tax calculator" in prompt
