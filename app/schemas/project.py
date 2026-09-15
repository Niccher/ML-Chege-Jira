"""Project and Wiki schemas."""

from pydantic import BaseModel, Field


class WikiGenerateRequest(BaseModel):
    """Request payload for auto-generating a project wiki page."""

    page_title: str = Field(min_length=3, max_length=255, description="Title of the wiki page")
    parent_id: int | None = Field(default=None, description="Optional parent page ID in wiki tree")
    created_by: int | None = Field(default=None, description="User ID requesting page generation")
    model: str | None = Field(default=None, description="Optional model key override")
    custom_instructions: str | None = Field(default=None, description="Extra instructions for LLM")


class WikiGenerateData(BaseModel):
    id: int
    project_id: int
    parent_id: int | None
    title: str
    slug: str
    content: str
    version: int
