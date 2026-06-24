"""Models for the /studies search response."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .study import Study


class StudySearchResult(BaseModel):
    """The parsed response from a GET /studies search request."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    studies: list[Study] = Field(default_factory=list)
    next_page_token: str | None = Field(default=None, alias="nextPageToken")
    total_count: int | None = Field(default=None, alias="totalCount")
