"""Jinja2 prompt template loader and renderer."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Locate prompts directory
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

_env = Environment(
    loader=FileSystemLoader(str(PROMPTS_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_prompt(template_name: str, **kwargs: Any) -> str:
    """Render a named Jinja2 template with context kwargs.

    Args:
        template_name: Name of template (e.g. 'enhance_task.j2')
        **kwargs: Variables passed to the template

    Returns:
        Rendered string prompt ready for LLM inference
    """
    template = _env.get_template(template_name)
    return template.render(**kwargs)
