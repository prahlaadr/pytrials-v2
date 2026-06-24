"""Exception types raised by the SDK."""

from __future__ import annotations


class CTGError(Exception):
    """Base error for all ClinicalTrials.gov API failures.

    Carries the HTTP status code (when available) and a human readable message.
    """

    def __init__(self, status_code: int | None, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        if self.status_code is None:
            return self.message
        return f"[{self.status_code}] {self.message}"


class NotFoundError(CTGError):
    """Raised on HTTP 404, for example when an NCT ID does not exist."""


class RateLimitError(CTGError):
    """Raised on HTTP 429 when the API rate limit (around 50 req/min) is hit."""
