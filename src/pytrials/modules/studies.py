"""The studies module: search and fetch study records."""

from __future__ import annotations

from typing import Any

from ..client import CTGClient
from ..models.enums import OverallStatus, Phase
from ..models.search import StudySearchResult
from ..models.study import Study


def _as_value_list(value: Any) -> list[str]:
    """Coerce a scalar, enum, or sequence into a list of string values."""
    if value is None:
        return []
    if isinstance(value, (str, OverallStatus, Phase)):
        return [_to_str(value)]
    if isinstance(value, (list, tuple, set)):
        return [_to_str(item) for item in value]
    return [_to_str(value)]


def _to_str(value: Any) -> str:
    if isinstance(value, OverallStatus):
        return value.value
    if isinstance(value, Phase):
        return value.value
    return str(value)


class StudiesModule:
    """Operations against the /studies endpoints."""

    def __init__(self, client: CTGClient) -> None:
        self._client = client

    def search(
        self,
        condition: str | None = None,
        status: str | OverallStatus | list[str | OverallStatus] | None = None,
        phase: str | Phase | list[str | Phase] | None = None,
        page_size: int | None = None,
        sort: str | None = None,
        **extra: Any,
    ) -> StudySearchResult:
        """Search studies and return a validated :class:`StudySearchResult`.

        Maps the friendly keyword arguments onto the real API query parameters:
        ``query.cond``, ``filter.overallStatus``, ``aggFilters`` (for phase),
        ``pageSize``, ``sort``, and ``countTotal=true``.
        """
        params: dict[str, Any] = {
            "countTotal": "true",
            "pageSize": page_size if page_size is not None else self._client.default_page_size,
        }

        if condition is not None:
            params["query.cond"] = condition

        statuses = _as_value_list(status)
        if statuses:
            params["filter.overallStatus"] = ",".join(statuses)

        phases = _as_value_list(phase)
        if phases:
            agg = ",".join(f"phase:{value}" for value in phases)
            params["aggFilters"] = agg

        if sort is not None:
            params["sort"] = sort

        params.update(extra)

        data = self._client.get("/studies", params=params)
        return StudySearchResult.model_validate(data)

    def get(self, nct_id: str) -> Study:
        """Fetch a single study by NCT ID via /studies/{nctId}."""
        data = self._client.get(f"/studies/{nct_id}")
        return Study.model_validate(data)
