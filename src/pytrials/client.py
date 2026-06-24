"""Low level HTTP client wrapping httpx for the ClinicalTrials.gov API v2."""

from __future__ import annotations

from typing import Any, NoReturn

import httpx

from .errors import CTGError, NotFoundError, RateLimitError

DEFAULT_BASE_URL = "https://clinicaltrials.gov/api/v2"
DEFAULT_TIMEOUT = 30.0
DEFAULT_PAGE_SIZE = 100


class CTGClient:
    """Synchronous HTTP client for the ClinicalTrials.gov API v2.

    This is an internal building block. Most users should go through the
    :class:`pytrials.ClinicalTrials` facade and its module namespaces.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        default_page_size: int = DEFAULT_PAGE_SIZE,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_page_size = default_page_size
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Accept": "application/json"},
        )

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Issue a GET request and return the parsed JSON body.

        Raises :class:`NotFoundError` on 404, :class:`RateLimitError` on 429,
        and :class:`CTGError` on any other 4xx or 5xx response.
        """
        cleaned = _clean_params(params or {})
        response = self._client.get(path, params=cleaned)
        if response.is_success:
            data: dict[str, Any] = response.json()
            return data
        self._raise_for_status(response)

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> NoReturn:
        status = response.status_code
        message = _extract_message(response)
        if status == 404:
            raise NotFoundError(status, message)
        if status == 429:
            raise RateLimitError(status, message)
        raise CTGError(status, message)

    def close(self) -> None:
        """Close the underlying httpx client and its connection pool."""
        self._client.close()

    def __enter__(self) -> CTGClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def _clean_params(params: dict[str, Any]) -> dict[str, Any]:
    """Drop None values so they are not serialized into the query string."""
    return {key: value for key, value in params.items() if value is not None}


def _extract_message(response: httpx.Response) -> str:
    """Pull a useful error message out of an error response body."""
    try:
        body = response.json()
    except ValueError:
        return response.text or response.reason_phrase
    if isinstance(body, dict):
        for key in ("message", "detail", "error"):
            value = body.get(key)
            if isinstance(value, str):
                return value
    return response.reason_phrase
